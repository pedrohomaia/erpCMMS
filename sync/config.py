from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseModel):
    ERP_BASE_URL: str = os.getenv("ERP_BASE_URL","http://127.0.0.1:8001")
    CMMS_BASE_URL: str = os.getenv("CMMS_BASE_URL","http://127.0.0.1:8002")
    ERP_TOKEN: str = os.getenv("ERP_TOKEN","test-erp-token")
    CMMS_TOKEN: str = os.getenv("CMMS_TOKEN","test-cmms-token")
    SYNC_DB_URL: str = os.getenv("SYNC_DB_URL","sqlite:///sync_data.db")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT",10))
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS",3))
    RETRY_BASE_SECONDS: int = int(os.getenv("RETRY_BASE_SECONDS",1))

settings = Settings()
