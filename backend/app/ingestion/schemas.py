from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LogEventIn(BaseModel):
    """Shape of a log event coming in via the REST API."""
    source_type: str = "api"
    source_name: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    username: Optional[str] = None
    host: Optional[str] = None
    raw_log: str
    timestamp: Optional[datetime] = None