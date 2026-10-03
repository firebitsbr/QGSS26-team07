#!/usr/bin/env bash
# Author: Mauro Risonho de Paula Assumpção
# Date Created: Not recorded
# Date Updated: 2026-10-03
# Short Description: Run recurring incremental Discord data collection.
# Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
# License: MIT

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

INTERVAL_SECONDS="${1:-900}"
LOG_DIR="discord_automation/output/daemon_logs"
mkdir -p "$LOG_DIR"

if [[ ! -f "discord_automation/.env" ]]; then
  echo "Missing discord_automation/.env" >&2
  exit 1
fi

if [[ ! -f "discord_automation/config/discord_config.yaml" ]]; then
  echo "Missing discord_automation/config/discord_config.yaml" >&2
  exit 1
fi

if [[ -x ".conda/bin/python" ]]; then
  PYTHON_BIN=".conda/bin/python"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
else
  echo "Local Python not found (.conda/.venv)." >&2
  exit 1
fi

while true; do
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  log_file="$LOG_DIR/run_$ts.log"

  echo "[$(date -u +%FT%TZ)] Starting incremental collection" | tee -a "$log_file"
  "$PYTHON_BIN" discord_automation/discord_collector.py \
    --config discord_automation/config/discord_config.yaml \
    --env-file discord_automation/.env >> "$log_file" 2>&1 || true

  echo "[$(date -u +%FT%TZ)] Collection finished. Sleeping ${INTERVAL_SECONDS}s" | tee -a "$log_file"
  sleep "$INTERVAL_SECONDS"
done
