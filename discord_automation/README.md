<!--
Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Set up and use the official-API-based Discord collection tools.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT
-->

# Discord Automation (Official API)

This setup collects Discord server data in an organized way using an official bot token and `discord.py`.
It does not read Firefox cookies or use a personal user token.

## What it exports
- Channel message history (`ndjson` per channel)
- Attachments (downloaded files)
- Run summaries (`run_summary.json`)
- Incremental state (`collector_state.json`)

## Files
- Collector: `discord_automation/discord_collector.py`
- Config template: `discord_automation/config/discord_config.example.yaml`
- Env template: `discord_automation/.env.example`
- Runner: `discord_automation/run_discord_collection.sh`

## Setup
1. Create and configure bot in Discord Developer Portal.
2. Enable intents for the bot:
   - Server Members Intent (optional)
   - Message Content Intent (required for full text)
3. Invite bot to target server with permissions:
   - View Channels
   - Read Message History
   - Attach Files (optional for future actions)
4. Copy templates:
   - `cp discord_automation/config/discord_config.example.yaml discord_automation/config/discord_config.yaml`
   - `cp discord_automation/.env.example discord_automation/.env`
5. Set `DISCORD_BOT_TOKEN` in `.env`.
6. Optionally set `guild_id` in config.

## Run
```bash
cd "$(git rev-parse --show-toplevel)"
chmod +x discord_automation/run_discord_collection.sh
./discord_automation/run_discord_collection.sh
```

## Get guild_id automatically
```bash
cd "$(git rev-parse --show-toplevel)"
chmod +x discord_automation/get_guild_id.sh
./discord_automation/get_guild_id.sh
```

This prints each guild visible to your bot in this format:
- name=<guild_name> | guild_id=<numeric_id> | text_channels=<n> | members=<n>

Copy the target numeric value and set it in:
- discord_automation/config/discord_config.yaml

## Set guild/channel target from a Discord URL
```bash
cd "$(git rev-parse --show-toplevel)"
chmod +x discord_automation/set_target_from_url.sh
./discord_automation/set_target_from_url.sh "https://discord.com/channels/<guild_id>/<channel_id>"
```

This updates:
- `guild_id`
- `include_channel_ids`

Use this when you want focused collection from one channel first.

## Apply QGSS26 essential channel preset
```bash
cd "$(git rev-parse --show-toplevel)"
.conda/bin/python discord_automation/apply_qgss26_preset.py
```

This switches collection from a single channel ID to key QGSS26 channels by exact name.

## Continuous autonomous mode (daemon)
```bash
cd "$(git rev-parse --show-toplevel)"
chmod +x discord_automation/run_discord_daemon.sh
./discord_automation/run_discord_daemon.sh 900
```

- `900` means every 15 minutes (incremental sync).
- Logs: `discord_automation/output/daemon_logs/`

## Output structure
- `discord_automation/output/run_YYYYMMDD_HHMMSS/messages/*.ndjson`
- `discord_automation/output/run_YYYYMMDD_HHMMSS/attachments/...`
- `discord_automation/output/run_YYYYMMDD_HHMMSS/manifests/run_summary.json`
- `discord_automation/output/state/collector_state.json`

## Notes
- Incremental mode resumes by `last_message_id` per channel.
- If no `guild_id` is set, the first guild available to the bot is used.
- For private channels, grant channel-level permissions to the bot.
- You can also get guild_id manually in Discord Desktop: Settings > Advanced > Developer Mode ON, then right-click the server icon > Copy Server ID.
- Session cookie reuse from Discord web login is not required for this setup; use official bot token/API for stable and compliant automation.
