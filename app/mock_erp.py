from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import List
import os

app = FastAPI(title="Mock ERP API")

security = HTTPBearer(auto_error=False)
ERP_TOKEN = os.getenv("ERP_TOKEN", "test-erp-token")

class Order(BaseModel):
    id: int
    asset_code: str
    description: str
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL
    status: str    # OPEN, IN_PROGRESS, DONE, CANCELLED
    due_date: str | None
    updated_at: str  # ISO-8601 Z

def check_auth(creds: HTTPAuthorizationCredentials | None = Depends(security)):
    if not creds or creds.scheme.lower() != "bearer" or creds.credentials != ERP_TOKEN:
        raise HTTPException(status_code=401, detail="invalid or missing token")

def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

now = datetime.now(timezone.utc)
ORDERS: List[Order] = [
    Order(id=1001, asset_code="PMP-01", description="Troca de selo mecânico", priority="HIGH", status="OPEN",        due_date=iso(now + timedelta(days=2)), updated_at=iso(now - timedelta(days=3))),
    Order(id=1002, asset_code="MTR-07", description="Vibração fora da faixa",    priority="MEDIUM", status="IN_PROGRESS", due_date=iso(now + timedelta(days=1)), updated_at=iso(now - timedelta(days=2))),
    Order(id=1003, asset_code="VAL-22", description="Válvula travando",          priority="CRITICAL", status="OPEN",   due_date=iso(now + timedelta(days=5)), updated_at=iso(now - timedelta(hours=12))),
]

@app.get("/orders", dependencies=[Depends(check_auth)])
def list_orders(since: str | None = None, limit: int = 100):
    items = ORDERS
    if since:
        try:
            if since.endswith("Z"):
                since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            else:
                since_dt = datetime.fromisoformat(since)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"invalid since param: {exc}")
        items = [o for o in items if datetime.fromisoformat(o.updated_at.replace("Z", "+00:00")) >= since_dt]
    items = sorted(items, key=lambda o: o.updated_at)[:limit]
    return [o.model_dump() for o in items]
