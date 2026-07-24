from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.log_event import LogEvent
from app.ingestion.schemas import LogEventIn


def save_log_event(db: Session, event: LogEventIn) -> LogEvent:
    """Persist an incoming log event to the database."""
    db_event = LogEvent(
        timestamp=event.timestamp or datetime.now(timezone.utc),
        source_type=event.source_type,
        source_name=event.source_name,
        event_type=event.event_type,
        severity=event.severity,
        action=event.action,
        status=event.status,
        source_ip=event.source_ip,
        destination_ip=event.destination_ip,
        source_port=event.source_port,
        destination_port=event.destination_port,
        protocol=event.protocol,
        username=event.username,
        host=event.host,
        raw_log=event.raw_log,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def save_raw_syslog_line(db: Session, raw_line: str, source_ip: str) -> LogEvent:
    """Persist a raw syslog line with minimal parsing (full parsing comes in Step 5)."""
    db_event = LogEvent(
        timestamp=datetime.now(timezone.utc),
        source_type="syslog",
        source_ip=source_ip,
        raw_log=raw_line,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event