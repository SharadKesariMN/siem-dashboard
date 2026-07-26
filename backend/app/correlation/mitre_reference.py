"""
Local reference data for MITRE ATT&CK techniques used by our correlation rules.
Source: https://attack.mitre.org/
Extend this dict as new correlation rules are added.
"""

MITRE_TECHNIQUES = {
    "T1110": {
        "name": "Brute Force",
        "tactic": "Credential Access",
        "description": "Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained.",
        "url": "https://attack.mitre.org/techniques/T1110/",
    },
    "T1046": {
        "name": "Network Service Discovery",
        "tactic": "Discovery",
        "description": "Adversaries may attempt to get a listing of services running on remote hosts, including those that may be vulnerable to remote software exploitation.",
        "url": "https://attack.mitre.org/techniques/T1046/",
    },
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "Defense Evasion, Persistence, Privilege Escalation, Initial Access",
        "description": "Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access, Persistence, Privilege Escalation, or Defense Evasion.",
        "url": "https://attack.mitre.org/techniques/T1078/",
    },
}


def get_technique_info(technique_id: str) -> dict:
    """Returns enrichment info for a MITRE technique ID, or a fallback if unknown."""
    return MITRE_TECHNIQUES.get(technique_id, {
        "name": "Unknown Technique",
        "tactic": "Unknown",
        "description": "No local reference data available for this technique.",
        "url": f"https://attack.mitre.org/techniques/{technique_id}/" if technique_id else None,
    })