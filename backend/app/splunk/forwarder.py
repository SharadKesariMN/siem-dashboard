import os
import requests
from datetime import datetime

SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL")
SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN")
SPLUNK_FORWARDING_ENABLED = os.getenv("SPLUNK_FORWARDING_ENABLED", "false").lower() == "true"

REQUEST_TIMEOUT_SECONDS = 3


def is_forwarding_enabled() -> bool:
    return SPLUNK_FORWARDING_ENABLED and bool(SPLUNK_HEC_URL) and bool(SPLUNK_HEC_TOKEN)


def forward_event_to_splunk(event_data: dict) -> bool:
    """
    Forwards a single normalized log event to Splunk via HTTP Event Collector.
    Fails silently (logs a warning) if Splunk is unreachable or misconfigured -
    forwarding must never break local ingestion.
    Returns True if the forward succeeded, False otherwise.
    """
    if not is_forwarding_enabled():
        return False

    payload = {
        "time": datetime.now().timestamp(),
        "sourcetype": "_json",
        "source": "siem-dashboard",
        "event": event_data,
    }

    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            SPLUNK_HEC_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
            verify=False,  # many local/dev Splunk HEC setups use self-signed certs
        )
        if response.status_code == 200:
            return True
        else:
            print(f"[splunk_forwarder] non-200 response: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[splunk_forwarder] forwarding failed: {e}")
        return False
