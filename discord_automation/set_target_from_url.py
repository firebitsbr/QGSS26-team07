#!/usr/bin/env python3
"""Set the Discord guild and channel target from a channel URL.

Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Parse a Discord channel URL and update the collector configuration.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT
"""

import argparse
import re
from pathlib import Path

import yaml


def parse_discord_channel_url(url: str) -> tuple[int, int]:
    m = re.search(r"discord\.com/channels/(\d+)/(\d+)", url)
    if not m:
        raise ValueError("Invalid URL. Expected format: https://discord.com/channels/<guild_id>/<channel_id>")
    return int(m.group(1)), int(m.group(2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Set guild/channel target in Discord collector config from a Discord URL")
    parser.add_argument("url", help="Discord channel URL")
    parser.add_argument("--config", default="discord_automation/config/discord_config.yaml", help="Path to YAML config")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    guild_id, channel_id = parse_discord_channel_url(args.url)

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    data["guild_id"] = guild_id
    data["include_channel_ids"] = [channel_id]

    config_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8")

    print(f"Configured guild_id: {guild_id}")
    print(f"Configured include_channel_ids: [{channel_id}]")
    print(f"Updated file: {config_path}")


if __name__ == "__main__":
    main()
