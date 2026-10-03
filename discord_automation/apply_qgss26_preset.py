#!/usr/bin/env python3
"""Apply the QGSS26 essential-channel preset to the Discord collector.

Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Configure Discord collection to target the selected QGSS26 channels.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT
"""

from pathlib import Path
import yaml

CFG = Path("discord_automation/config/discord_config.yaml")
PRESET = Path("discord_automation/config/qgss26_channel_preset.yaml")


def main() -> None:
    if not CFG.exists():
        raise FileNotFoundError(f"Config not found: {CFG}")
    if not PRESET.exists():
        raise FileNotFoundError(f"Preset not found: {PRESET}")

    cfg = yaml.safe_load(CFG.read_text(encoding="utf-8"))
    preset = yaml.safe_load(PRESET.read_text(encoding="utf-8"))

    cfg["include_channel_ids"] = preset.get("include_channel_ids", [])
    cfg["include_channel_names_exact"] = preset.get("include_channel_names_exact", [])

    CFG.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=False), encoding="utf-8")

    print(f"Updated: {CFG}")
    print(f"include_channel_ids={cfg.get('include_channel_ids', [])}")
    print(f"include_channel_names_exact={cfg.get('include_channel_names_exact', [])}")


if __name__ == "__main__":
    main()
