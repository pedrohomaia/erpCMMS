PRIORITY_MAP = {"LOW":1,"MEDIUM":2,"HIGH":3,"CRITICAL":4}
STATUS_MAP   = {"OPEN":"NEW","IN_PROGRESS":"IN_PROGRESS","DONE":"COMPLETED","CANCELLED":"CANCELLED"}

def erp_to_cmms(order: dict) -> dict:
    return {
        "work_order_id": str(order["id"]),
        "asset_code": order.get("asset_code"),
        "title": (order.get("description") or "")[:120],
        "priority": PRIORITY_MAP.get(order.get("priority","MEDIUM"),2),
        "status": STATUS_MAP.get(order.get("status","OPEN"),"NEW"),
        "due_date": order.get("due_date"),
        "source": "ERP",
        "external_updated_at": order.get("updated_at"),
    }
