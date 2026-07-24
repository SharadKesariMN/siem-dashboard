import uuid
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.models.database import Base


class LogEvent(Base):
    __tablename__ = "log_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ingested_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Where the log came from
    source_type = Column(String(50), nullable=False)   # "syslog" | "api" | "file"
    source_name = Column(String(100), nullable=True)    # e.g. hostname or integration name

    # Normalized common fields
    event_type = Column(String(100), nullable=True)     # e.g. "auth_failure", "port_scan"
    severity = Column(String(20), nullable=True)         # "low" | "medium" | "high" | "critical"
    action = Column(String(50), nullable=True)           # "allow" | "deny" | "login" | etc.
    status = Column(String(50), nullable=True)           # "success" | "failure"

    source_ip = Column(String(45), nullable=True)        # supports IPv6
    destination_ip = Column(String(45), nullable=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=True)         # "tcp" | "udp" | "icmp"

    username = Column(String(255), nullable=True)
    host = Column(String(255), nullable=True)

    raw_log = Column(Text, nullable=False)                # original untouched log line
    normalized_message = Column(Text, nullable=True)      # human-readable summary

    extra = Column(JSONB, nullable=True)                  # source-specific leftover fields 