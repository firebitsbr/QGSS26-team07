#!/usr/bin/env bash
# Author: Mauro Risonho de Paula Assumpção
# Date Created: Not recorded
# Date Updated: 2026-10-03
# Short Description: Set the Discord collection target using a channel URL.
# Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
# License: MIT

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -lt 1 ]]; then
  echo "Usage: ./discord_automation/set_target_from_url.sh https://discord.com/channels/<guild_id>/<channel_id>"
  exit 1
fi

URL="$1"

if [[ -x ".conda/bin/python" ]]; then
  PYTHON_BIN=".conda/bin/python"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
else
  echo "Local Python not found (.conda/.venv)." >&2
  exit 1
fi

"$PYTHON_BIN" discord_automation/set_target_from_url.py "$URL" --config discord_automation/config/discord_config.yaml
