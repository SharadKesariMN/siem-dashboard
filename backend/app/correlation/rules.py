from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.log_event import LogEvent
from app.models.alert import Alert

BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_MINUTES = 5

PORT_SCAN_THRESHOLD = 10
PORT_SCAN_WINDOW_MINUTES = 2


def _alert_recently_exists(db: Session, rule_name: str, identifier: str, window_minutes: int = 10) -> bool:
    """Prevents duplicate alerts for the same source firing repeatedly every correlation cycle."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    existing = (
        db.query(Alert)
        .filter(Alert.rule_name == rule_name)
        .filter(Alert.description.like(f"%{identifier}%"))
        .filter(Alert.created_at >= cutoff)
        .first()
    )
    return existing is not None


def detect_ssh_brute_force(db: Session):
    """MITRE T1110 - Brute Force. N+ auth failures from the same source IP within a time window."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=BRUTE_FORCE_WINDOW_MINUTES)

    results = (
        db.query(LogEvent.source_ip, func.count(LogEvent.id).label("count"))
        .filter(LogEvent.event_type == "auth_failure")
        .filter(LogEvent.timestamp >= cutoff)
        .filter(LogEvent.source_ip.isnot(None))
        .group_by(LogEvent.source_ip)
        .having(func.count(LogEvent.id) >= BRUTE_FORCE_THRESHOLD)
        .all()
    )

    new_alerts = []
    for source_ip, count in results:
        if _alert_recently_exists(db, "ssh_brute_force", source_ip):
            continue

        event_ids = [
            row.id for row in
            db.query(LogEvent.id)
            .filter(LogEvent.event_type == "auth_failure")
            .filter(LogEvent.source_ip == source_ip)
            .filter(LogEvent.timestamp >= cutoff)
            .all()
        ]

        new_alerts.append(Alert(
            rule_name="ssh_brute_force",
            mitre_technique="T1110",
            severity="high",
            description=f"{count} failed SSH login attempts from {source_ip} within {BRUTE_FORCE_WINDOW_MINUTES} minutes",
            source_event_ids=event_ids,
            status="open",
        ))

    return new_alerts


def detect_port_scan(db: Session):
    """MITRE T1046 - Network Service Discovery. Single source hitting many distinct destination ports."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=PORT_SCAN_WINDOW_MINUTES)

    results = (
        db.query(LogEvent.source_ip, func.count(func.distinct(LogEvent.destination_port)).label("port_count"))
        .filter(LogEvent.timestamp >= cutoff)
        .filter(LogEvent.source_ip.isnot(None))
        .filter(LogEvent.destination_port.isnot(None))
        .group_by(LogEvent.source_ip)
        .having(func.count(func.distinct(LogEvent.destination_port)) >= PORT_SCAN_THRESHOLD)
        .all()
    )

    new_alerts = []
    for source_ip, port_count in results:
        if _alert_recently_exists(db, "port_scan", source_ip):
            continue

        event_ids = [
            row.id for row in
            db.query(LogEvent.id)
            .filter(LogEvent.source_ip == source_ip)
            .filter(LogEvent.timestamp >= cutoff)
            .filter(LogEvent.destination_port.isnot(None))
            .all()
        ]

        new_alerts.append(Alert(
            rule_name="port_scan",
            mitre_technique="T1046",
            severity="medium",
            description=f"{source_ip} probed {port_count} distinct ports within {PORT_SCAN_WINDOW_MINUTES} minutes",
            source_event_ids=event_ids,
            status="open",
        ))

    return new_alerts


def detect_privilege_escalation(db: Session):
    """MITRE T1078 - Valid Accounts. Flags explicit privilege escalation events."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)

    events = (
        db.query(LogEvent)
        .filter(LogEvent.event_type == "privilege_escalation")
        .filter(LogEvent.timestamp >= cutoff)
        .all()
    )

    new_alerts = []
    for event in events:
        identifier = event.username or event.source_ip or str(event.id)
        if _alert_recently_exists(db, "privilege_escalation", identifier):
            continue

        new_alerts.append(Alert(
            rule_name="privilege_escalation",
            mitre_technique="T1078",
            severity="critical",
            description=f"Privilege escalation detected for user '{event.username}' on host '{event.host}' ({identifier})",
            source_event_ids=[event.id],
            status="open",
        ))

    return new_alerts


RULES = [
    detect_ssh_brute_force,
    detect_port_scan,
    detect_privilege_escalation,
]