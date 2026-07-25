import re
from typing import Optional, Dict, Any


def parse_ssh_auth_failure(raw_log: str) -> Optional[Dict[str, Any]]:
    """Matches: 'Failed password for [invalid user] <user> from <ip> port <port> ssh2'"""
    pattern = r"Failed password for (invalid user )?(?P<username>\S+) from (?P<ip>[\d.]+) port (?P<port>\d+)"
    match = re.search(pattern, raw_log)
    if not match:
        return None

    return {
        "event_type": "auth_failure",
        "action": "login",
        "status": "failure",
        "severity": "medium",
        "username": match.group("username"),
        "source_ip": match.group("ip"),
        "source_port": int(match.group("port")),
        "protocol": "ssh",
    }


def parse_ssh_auth_success(raw_log: str) -> Optional[Dict[str, Any]]:
    """Matches: 'Accepted password for <user> from <ip> port <port> ssh2'"""
    pattern = r"Accepted (password|publickey) for (?P<username>\S+) from (?P<ip>[\d.]+) port (?P<port>\d+)"
    match = re.search(pattern, raw_log)
    if not match:
        return None

    return {
        "event_type": "auth_success",
        "action": "login",
        "status": "success",
        "severity": "low",
        "username": match.group("username"),
        "source_ip": match.group("ip"),
        "source_port": int(match.group("port")),
        "protocol": "ssh",
    }


def parse_generic_syslog_header(raw_log: str) -> Optional[Dict[str, Any]]:
    """
    Matches standard syslog priority + timestamp + hostname header:
    '<34>Jul 24 18:00:00 myhost sshd[1234]: ...'
    Extracts host and leaves the rest for other parsers to pick up.
    """
    pattern = r"^<\d+>\w+\s+\d+\s+[\d:]+\s+(?P<host>\S+)\s+(?P<process>\S+?):"
    match = re.search(pattern, raw_log)
    if not match:
        return None

    return {
        "host": match.group("host"),
    }


# Ordered list of parsers to try. Order matters: more specific parsers first.
PARSERS = [
    parse_ssh_auth_failure,
    parse_ssh_auth_success,
]

# Header parsers run separately and merge in regardless of event match
HEADER_PARSERS = [
    parse_generic_syslog_header,
]