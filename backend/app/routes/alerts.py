from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.alert import Alert

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()
    return [
        {
            "id": str(a.id),
            "rule_name": a.rule_name,
            "mitre_technique": a.mitre_technique,
            "severity": a.severity,
            "description": a.description,
            "status": a.status,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]