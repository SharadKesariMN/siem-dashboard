import threading
import time

from app.models.database import SessionLocal
from app.correlation.rules import RULES
from app.correlation.mitre_reference import get_technique_info
from app.ai.claude_service import generate_incident_summary

CORRELATION_INTERVAL_SECONDS = 15


def run_correlation_once():
    db = SessionLocal()
    try:
        all_new_alerts = []
        for rule_func in RULES:
            all_new_alerts.extend(rule_func(db))

        for alert in all_new_alerts:
            mitre_info = get_technique_info(alert.mitre_technique) if alert.mitre_technique else {}

            ai_result = generate_incident_summary({
                "rule_name": alert.rule_name,
                "mitre_technique": alert.mitre_technique,
                "mitre_name": mitre_info.get("name"),
                "mitre_tactic": mitre_info.get("tactic"),
                "severity": alert.severity,
                "description": alert.description,
                "event_count": len(alert.source_event_ids) if alert.source_event_ids else 0,
            })

            alert.ai_summary = f"{ai_result['summary']}\n\nRecommended action: {ai_result['recommendation']}"
            db.add(alert)

        if all_new_alerts:
            db.commit()
            print(f"[correlation] created {len(all_new_alerts)} new alert(s) with AI summaries")
    except Exception as e:
        print(f"[correlation] error: {e}")
        db.rollback()
    finally:
        db.close()


def _correlation_loop():
    while True:
        run_correlation_once()
        time.sleep(CORRELATION_INTERVAL_SECONDS)


def start_correlation_thread():
    thread = threading.Thread(target=_correlation_loop, daemon=True)
    thread.start()
