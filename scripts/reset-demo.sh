#!/bin/bash
# Clears all log events and alerts, so simulate-attack.sh can be re-run
# for a clean demo. Works against local or deployed instances.
#
# Usage:
#   ./scripts/reset-demo.sh
#   SIEM_API_URL=https://your-backend.onrender.com ./scripts/reset-demo.sh
#
# Requires DASHBOARD_USERNAME / DASHBOARD_PASSWORD env vars, or defaults
# to the values below (edit to match your .env).

set -e

API_URL="${SIEM_API_URL:-http://localhost:8000}"
USERNAME="${DASHBOARD_USERNAME:-admin}"
PASSWORD="${DASHBOARD_PASSWORD:-changeme}"

echo "Resetting demo data at $API_URL ..."

RESPONSE=$(curl -s -u "$USERNAME:$PASSWORD" -X POST "$API_URL/api/admin/reset-demo-data")

echo "$RESPONSE"
echo ""
echo "Done. Run ./scripts/simulate-attack.sh for a fresh demo."
