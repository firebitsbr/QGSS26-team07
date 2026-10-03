#!/usr/bin/env bash
# Author: Mauro Risonho de Paula Assumpção
# Date Created: Not recorded
# Date Updated: 2026-10-03
# Short Description: List the Discord guilds visible to the configured bot.
# Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
# License: MIT

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "discord_automation/config/discord_config.yaml" ]]; then
  cp discord_automation/config/discord_config.example.yaml discord_automation/config/discord_config.yaml
  echo "Created file: discord_automation/config/discord_config.yaml"
fi

if [[ ! -f "discord_automation/.env" ]]; then
  cp discord_automation/.env.example discord_automation/.env
  echo "Created file: discord_automation/.env"
  echo "Set the bot token and run the script again."
  exit 0
fi

if [[ -x ".conda/bin/python" ]]; then
  PYTHON_BIN=".conda/bin/python"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
else
  echo "Local Python not found (.conda/.venv)." >&2
  exit 1
fi

"$PYTHON_BIN" discord_automation/list_guilds.py \
  --config discord_automation/config/discord_config.yaml \
  --env-file discord_automation/.env
