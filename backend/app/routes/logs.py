from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.models.database import get_db
from app.models.log_event import LogEvent

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("")
def list_logs(
    search: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(LogEvent)

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            or_(
                LogEvent.raw_log.ilike(like_pattern),
                LogEvent.normalized_message.ilike(like_pattern),
                LogEvent.source_ip.ilike(like_pattern),
                LogEvent.username.ilike(like_pattern),
                LogEvent.host.ilike(like_pattern),
            )
        )

    if severity:
        query = query.filter(LogEvent.severity == severity)

    if source_type:
        query = query.filter(LogEvent.source_type == source_type)

    logs = query.order_by(LogEvent.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "source_type": log.source_type,
            "event_type": log.event_type,
            "severity": log.severity,
            "status": log.status,
            "source_ip": log.source_ip,
            "destination_port": log.destination_port,
            "username": log.username,
            "host": log.host,
            "normalized_message": log.normalized_message,
            "raw_log": log.raw_log,
        }
        for log in logs
    ]
