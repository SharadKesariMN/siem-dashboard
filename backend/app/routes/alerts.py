from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.alert import Alert
from app.models.log_event import LogEvent
from app.correlation.mitre_reference import get_technique_info

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()
    return [_serialize_alert(a) for a in alerts]


@router.get("/{alert_id}")
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return {"error": "Alert not found"}

    result = _serialize_alert(alert)
    result["related_events"] = _get_related_events(db, alert)
    return result


def _get_related_events(db: Session, alert: Alert) -> list:
    if not alert.source_event_ids:
        return []
    events = (
        db.query(LogEvent)
        .filter(LogEvent.id.in_(alert.source_event_ids))
        .order_by(LogEvent.timestamp.asc())
        .all()
    )
    return [
        {
            "id": str(e.id),
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "source_type": e.source_type,
            "source_ip": e.source_ip,
            "destination_port": e.destination_port,
            "username": e.username,
            "host": e.host,
            "raw_log": e.raw_log,
            "normalized_message": e.normalized_message,
        }
        for e in events
    ]


def _serialize_alert(a: Alert) -> dict:
    mitre_info = get_technique_info(a.mitre_technique) if a.mitre_technique else None

    return {
        "id": str(a.id),
        "rule_name": a.rule_name,
        "mitre_technique": a.mitre_technique,
        "mitre_info": mitre_info,
        "severity": a.severity,
        "description": a.description,
        "ai_summary": a.ai_summary,
        "status": a.status,
        "created_at": a.created_at.isoformat(),
        "event_count": len(a.source_event_ids) if a.source_event_ids else 0,
    }
