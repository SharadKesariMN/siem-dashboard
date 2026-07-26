from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.log_event import LogEvent
from app.ingestion.schemas import LogEventIn
from app.normalization.engine import normalize_log
from app.splunk.forwarder import forward_event_to_splunk, is_forwarding_enabled


def _event_to_dict(db_event: LogEvent) -> dict:
    return {
        "id": str(db_event.id),
        "timestamp": db_event.timestamp.isoformat() if db_event.timestamp else None,
        "source_type": db_event.source_type,
        "source_name": db_event.source_name,
        "event_type": db_event.event_type,
        "severity": db_event.severity,
        "action": db_event.action,
        "status": db_event.status,
        "source_ip": db_event.source_ip,
        "destination_ip": db_event.destination_ip,
        "source_port": db_event.source_port,
        "destination_port": db_event.destination_port,
        "protocol": db_event.protocol,
        "username": db_event.username,
        "host": db_event.host,
        "raw_log": db_event.raw_log,
        "normalized_message": db_event.normalized_message,
    }


def _maybe_forward(db_event: LogEvent):
    """Forwards to Splunk if enabled. Never raises - forwarding issues must not affect ingestion."""
    if is_forwarding_enabled():
        try:
            forward_event_to_splunk(_event_to_dict(db_event))
        except Exception as e:
            print(f"[ingestion] unexpected forwarding error (ignored): {e}")


def save_log_event(db: Session, event: LogEventIn) -> LogEvent:
    """Persist an incoming log event to the database, filling in any unset fields via normalization."""
    normalized = normalize_log(event.raw_log)

    db_event = LogEvent(
        timestamp=event.timestamp or datetime.now(timezone.utc),
        source_type=event.source_type,
        source_name=event.source_name,
        event_type=event.event_type or normalized.get("event_type"),
        severity=event.severity or normalized.get("severity"),
        action=event.action or normalized.get("action"),
        status=event.status or normalized.get("status"),
        source_ip=event.source_ip or normalized.get("source_ip"),
        destination_ip=event.destination_ip,
        source_port=event.source_port or normalized.get("source_port"),
        destination_port=event.destination_port,
        protocol=event.protocol or normalized.get("protocol"),
        username=event.username or normalized.get("username"),
        host=event.host or normalized.get("host"),
        raw_log=event.raw_log,
        normalized_message=normalized.get("normalized_message"),
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    _maybe_forward(db_event)

    return db_event


def save_raw_syslog_line(db: Session, raw_line: str, source_ip: str) -> LogEvent:
    """Persist a raw syslog line, fully normalized."""
    normalized = normalize_log(raw_line)

    db_event = LogEvent(
        timestamp=datetime.now(timezone.utc),
        source_type="syslog",
        source_ip=normalized.get("source_ip") or source_ip,
        event_type=normalized.get("event_type"),
        severity=normalized.get("severity"),
        action=normalized.get("action"),
        status=normalized.get("status"),
        source_port=normalized.get("source_port"),
        protocol=normalized.get("protocol"),
        username=normalized.get("username"),
        host=normalized.get("host"),
        raw_log=raw_line,
        normalized_message=normalized.get("normalized_message"),
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    _maybe_forward(db_event)

    return db_event
