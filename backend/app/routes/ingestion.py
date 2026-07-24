from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.ingestion.schemas import LogEventIn
from app.ingestion.service import save_log_event

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])


@router.post("/event")
def ingest_event(event: LogEventIn, db: Session = Depends(get_db)):
    saved = save_log_event(db, event)
    return {
        "status": "accepted",
        "event_id": str(saved.id),
        "timestamp": saved.timestamp.isoformat(),
    }