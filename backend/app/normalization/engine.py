from typing import Dict, Any
from app.normalization.parsers import PARSERS, HEADER_PARSERS


def normalize_log(raw_log: str) -> Dict[str, Any]:
    """
    Attempts to extract structured fields from a raw log line.
    Returns a dict of fields to update on the LogEvent (only fields that were found).
    """
    extracted: Dict[str, Any] = {}

    # Header parsers (e.g. hostname) always run and merge in
    for header_parser in HEADER_PARSERS:
        result = header_parser(raw_log)
        if result:
            extracted.update(result)

    # Event parsers - first match wins
    for parser in PARSERS:
        result = parser(raw_log)
        if result:
            extracted.update(result)
            break

    if not extracted:
        extracted["event_type"] = "unclassified"
        extracted["severity"] = "info"

    extracted["normalized_message"] = _build_summary(extracted, raw_log)
    return extracted


def _build_summary(fields: Dict[str, Any], raw_log: str) -> str:
    """Builds a short human-readable summary from extracted fields."""
    event_type = fields.get("event_type", "unclassified")

    if event_type == "auth_failure":
        return f"Failed login attempt for user '{fields.get('username')}' from {fields.get('source_ip')}"
    if event_type == "auth_success":
        return f"Successful login for user '{fields.get('username')}' from {fields.get('source_ip')}"

    return raw_log[:150]