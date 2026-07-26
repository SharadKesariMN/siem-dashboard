from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.alert import Alert
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
    return _serialize_alert(alert)


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
    }