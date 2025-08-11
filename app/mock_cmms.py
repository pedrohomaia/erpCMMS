from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict
from datetime import datetime, timezone
import os

app = FastAPI(title="Mock CMMS API")

security = HTTPBearer(auto_error=False)
CMMS_TOKEN = os.getenv("CMMS_TOKEN", "test-cmms-token")

class WorkOrder(BaseModel):
    work_order_id: str
    asset_code: str | None = None
    title: str
    priority: int = 2
    status: str = "NEW"
    due_date: str | None = None
    source: str = "ERP"
    external_updated_at: str | None = None
    updated_at: str | None = None

def check_auth(creds: HTTPAuthorizationCredentials | None = Depends(security)):
    if not creds or creds.scheme.lower() != "bearer" or creds.credentials != CMMS_TOKEN:
        raise HTTPException(status_code=401, detail="invalid or missing token")

DB: Dict[str, WorkOrder] = {}

@app.put("/workorders/{wo_id}", dependencies=[Depends(check_auth)])
def upsert_work_order(wo_id: str, wo: WorkOrder):
    wo.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    DB[wo_id] = wo
    return wo

@app.get("/workorders", dependencies=[Depends(check_auth)])
def list_workorders():
    return [wo.model_dump() for wo in DB.values()]
