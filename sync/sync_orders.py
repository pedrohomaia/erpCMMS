from __future__ import annotations
import argparse, time, requests
from sqlalchemy import select, and_
from .config import settings
from .db import SessionLocal, init_db
from .models import SyncLog
from .mapping import erp_to_cmms

def parse_args():
    p=argparse.ArgumentParser(description="ERP→CMMS Sync")
    p.add_argument("--since", type=str)
    p.add_argument("--max-orders", type=int, default=100)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()

def sessions():
    erp=requests.Session(); erp.headers.update({"Authorization":f"Bearer {settings.ERP_TOKEN}","Accept":"application/json"})
    cmms=requests.Session(); cmms.headers.update({"Authorization":f"Bearer {settings.CMMS_TOKEN}","Content-Type":"application/json","Accept":"application/json"})
    return erp, cmms

def already_synced(db, order_id:str, updated:str)->bool:
    q = select(SyncLog).where(and_(SyncLog.order_id==order_id, SyncLog.erp_updated_at==updated, SyncLog.success==True))  # noqa
    return db.execute(q).first() is not None

def list_orders(erp, since, limit:int):
    params={"limit":limit}; 
    if since: params["since"]=since
    r=erp.get(f"{settings.ERP_BASE_URL}/orders", params=params, timeout=settings.REQUEST_TIMEOUT)
    r.raise_for_status(); items=r.json()
    items.sort(key=lambda o:o.get("updated_at") or "")
    return items[:limit]

def upsert_cmms(cmms, payload:dict):
    r = cmms.put(f"{settings.CMMS_BASE_URL}/workorders/{payload['work_order_id']}", json=payload, timeout=settings.REQUEST_TIMEOUT)
    r.raise_for_status(); return r.json()

def backoff(attempt:int): time.sleep(settings.RETRY_BASE_SECONDS * (2**(attempt-1)))

def main():
    a=parse_args()
    if a.verbose: print("[SYNC] start since=", a.since or "<auto>")
    init_db(); db=SessionLocal()
    erp,cmms=sessions()
    try:
        orders=list_orders(erp,a.since,a.max_orders)
        if a.verbose: print(f"[SYNC] {len(orders)} ordens recebidas")
        for o in orders:
            oid=str(o.get("id")); upd=o.get("updated_at") or ""
            if already_synced(db, oid, upd):
                if a.verbose: print(f"- skip #{oid} (já sincronizada {upd})")
                continue
            payload=erp_to_cmms(o)
            attempts=0; ok=False; last_err=None
            while attempts < settings.RETRY_MAX_ATTEMPTS and not ok:
                attempts+=1
                try:
                    if a.dry_run:
                        if a.verbose: print(f"- dry-run upsert {payload['work_order_id']}")
                        ok=True; break
                    upsert_cmms(cmms,payload); ok=True
                except Exception as exc:
                    last_err=str(exc)
                    if a.verbose: print(f"  tentativa {attempts} falhou: {last_err}")
                    if attempts < settings.RETRY_MAX_ATTEMPTS: backoff(attempts)
            if not a.dry_run:
                db.add(SyncLog(order_id=oid, erp_updated_at=upd, success=bool(ok), attempts=attempts, error_message=None if ok else (last_err or "unknown error"))); db.commit()
            if a.verbose: print(f"- #{oid} -> {'OK' if ok else 'ERRO'}")
        if a.verbose: print("[SYNC] fim")
    finally:
        db.close()

if __name__=="__main__": main()
