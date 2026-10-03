#!/usr/bin/env bash
# Author: Mauro Risonho de Paula Assumpção
# Date Created: Not recorded
# Date Updated: 2026-10-03
# Short Description: Run a single Discord data collection.
# Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
# License: MIT

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "discord_automation/config/discord_config.yaml" ]]; then
  cp discord_automation/config/discord_config.example.yaml discord_automation/config/discord_config.yaml
  echo "Created discord_automation/config/discord_config.yaml from example. Customize it before running again."
  exit 0
fi

if [[ ! -f "discord_automation/.env" ]]; then
  cp discord_automation/.env.example discord_automation/.env
  echo "Created discord_automation/.env from example. Set DISCORD_BOT_TOKEN and run again."
  exit 0
fi

if [[ -x ".conda/bin/python" ]]; then
  PYTHON_BIN=".conda/bin/python"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
else
  echo "No local Python found (.conda/.venv)." >&2
  exit 1
fi

"$PYTHON_BIN" discord_automation/discord_collector.py \
  --config discord_automation/config/discord_config.yaml \
  --env-file discord_automation/.env

echo "Done. Check output under discord_automation/output/"
