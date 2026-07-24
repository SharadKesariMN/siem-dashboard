import uuid
from sqlalchemy import Column, String, DateTime, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    rule_name = Column(String(100), nullable=False)
    mitre_technique = Column(String(20), nullable=True)
    severity = Column(String(20), nullable=False)

    description = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)

    source_event_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    status = Column(String(20), nullable=False, default="open")
