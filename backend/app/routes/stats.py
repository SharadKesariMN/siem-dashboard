from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.models.database import get_db
from app.models.alert import Alert

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/severity-breakdown")
def severity_breakdown(db: Session = Depends(get_db)):
    results = (
        db.query(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
        .all()
    )
    return [{"severity": sev, "count": count} for sev, count in results]


@router.get("/top-sources")
def top_sources(db: Session = Depends(get_db)):
    """Extracts source IPs from alert descriptions - approximate but useful for overview."""
    from app.models.log_event import LogEvent

    results = (
        db.query(LogEvent.source_ip, func.count(LogEvent.id).label("count"))
        .filter(LogEvent.source_ip.isnot(None))
        .filter(LogEvent.severity.in_(["medium", "high", "critical"]))
        .group_by(LogEvent.source_ip)
        .order_by(func.count(LogEvent.id).desc())
        .limit(5)
        .all()
    )
    return [{"source_ip": ip, "count": count} for ip, count in results]


@router.get("/timeline")
def alert_timeline(db: Session = Depends(get_db)):
    """Alert counts bucketed by hour, over the last 24 hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    alerts = db.query(Alert).filter(Alert.created_at >= cutoff).all()

    buckets = {}
    for alert in alerts:
        hour_key = alert.created_at.strftime("%H:00")
        buckets[hour_key] = buckets.get(hour_key, 0) + 1

    sorted_buckets = sorted(buckets.items())
    return [{"hour": hour, "count": count} for hour, count in sorted_buckets]
