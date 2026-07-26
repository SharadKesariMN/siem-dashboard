import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a SOC (Security Operations Center) assistant analyzing security alerts.
Given structured alert data, respond with a JSON object containing exactly two fields:
- "summary": a plain-English explanation (2-3 sentences) of what happened, written for a security analyst
- "recommendation": a concise, actionable response recommendation (1-3 sentences)

Respond with ONLY the JSON object, no other text, no markdown formatting."""


def generate_incident_summary(alert_context: dict) -> dict:
    """
    Calls Claude to generate a plain-English summary and response recommendation
    for a given alert. Returns a dict with 'summary' and 'recommendation' keys.
    Falls back gracefully if the API call fails.
    """
    try:
        user_prompt = f"""Analyze this security alert:

Rule: {alert_context.get('rule_name')}
MITRE Technique: {alert_context.get('mitre_technique')} - {alert_context.get('mitre_name')}
Tactic: {alert_context.get('mitre_tactic')}
Severity: {alert_context.get('severity')}
Description: {alert_context.get('description')}
Number of related events: {alert_context.get('event_count')}"""

        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text.strip()
        parsed = json.loads(raw_text)

        return {
            "summary": parsed.get("summary", ""),
            "recommendation": parsed.get("recommendation", ""),
        }

    except Exception as e:
        print(f"[claude_service] AI summary generation failed: {e}")
        return {
            "summary": "AI summary unavailable.",
            "recommendation": "Review the alert details manually.",
        }
