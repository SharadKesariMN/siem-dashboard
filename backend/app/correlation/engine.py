import threading
import time

from app.models.database import SessionLocal
from app.correlation.rules import RULES

CORRELATION_INTERVAL_SECONDS = 15


def run_correlation_once():
    db = SessionLocal()
    try:
        all_new_alerts = []
        for rule_func in RULES:
            all_new_alerts.extend(rule_func(db))

        for alert in all_new_alerts:
            db.add(alert)

        if all_new_alerts:
            db.commit()
            print(f"[correlation] created {len(all_new_alerts)} new alert(s)")
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