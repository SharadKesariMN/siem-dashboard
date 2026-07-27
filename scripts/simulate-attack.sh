#!/bin/bash
# Simulates a realistic 3-stage intrusion chain to demonstrate the
# SIEM Dashboard's detection pipeline end-to-end:
#   1. Reconnaissance (Port Scan)      -> MITRE T1046
#   2. Initial Access (SSH Brute Force) -> MITRE T1110
#   3. Privilege Escalation             -> MITRE T1078
#
# Usage: ./scripts/simulate-attack.sh
# Requires: the SIEM Dashboard stack running via `docker compose up`

set -e

API_URL="${SIEM_API_URL:-http://localhost:8000}"
SYSLOG_HOST="${SIEM_SYSLOG_HOST:-localhost}"
SYSLOG_PORT="${SIEM_SYSLOG_PORT:-5514}"
ATTACKER_IP="192.0.2.200"

echo "=================================================="
echo " SIEM Dashboard - Simulated Attack Chain"
echo " Attacker IP: $ATTACKER_IP"
echo "=================================================="

echo ""
echo "[1/3] Simulating reconnaissance (port scan)..."
for port in 21 22 23 25 80 443 445 3306 3389 8080 8443; do
  curl -s -X POST "$API_URL/api/ingest/event" \
    -H "Content-Type: application/json" \
    -d "{\"source_type\": \"api\", \"source_ip\": \"$ATTACKER_IP\", \"destination_port\": $port, \"raw_log\": \"connection probe on port $port from $ATTACKER_IP\"}" > /dev/null
  sleep 0.3
done
echo "      Done - 11 ports probed"

echo ""
echo "[2/3] Simulating SSH brute force..."
for i in {1..7}; do
  echo "<34>$(date '+%b %d %H:%M:%S') target-host sshd[500$i]: Failed password for invalid user admin$i from $ATTACKER_IP port 4000$i ssh2" | nc -u -w1 "$SYSLOG_HOST" "$SYSLOG_PORT"
  sleep 1
done
echo "      Done - 7 failed login attempts"

echo ""
echo "[3/3] Simulating privilege escalation..."
curl -s -X POST "$API_URL/api/ingest/event" \
  -H "Content-Type: application/json" \
  -d "{
    \"source_type\": \"api\",
    \"event_type\": \"privilege_escalation\",
    \"source_ip\": \"$ATTACKER_IP\",
    \"username\": \"admin3\",
    \"host\": \"target-host\",
    \"raw_log\": \"admin3 executed sudo su - unexpectedly after multiple prior failed logins\"
  }" > /dev/null
echo "      Done"

echo ""
echo "=================================================="
echo " Attack simulation complete."
echo " Waiting 20s for the correlation engine to process..."
echo "=================================================="
sleep 20

echo ""
echo "Open http://localhost:5173 to see 3 correlated alerts:"
echo "  - Port Scan (T1046)"
echo "  - SSH Brute Force (T1110)"
echo "  - Privilege Escalation (T1078)"
echo ""
echo "Each includes an AI-generated summary and recommended response."
