from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.log_event import LogEvent
from app.models.alert import Alert
from app.auth import verify_credentials

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/reset-demo-data")
def reset_demo_data(db: Session = Depends(get_db), _=Depends(verify_credentials)):
    """
    Deletes all log events and alerts. Intended for resetting demo data
    before a live walkthrough. Protected by the same auth as the dashboard.
    """
    deleted_alerts = db.query(Alert).delete()
    deleted_events = db.query(LogEvent).delete()
    db.commit()
    return {
        "status": "reset complete",
        "deleted_alerts": deleted_alerts,
        "deleted_log_events": deleted_events,
    }
