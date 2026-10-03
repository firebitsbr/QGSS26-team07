#!/usr/bin/env python3
"""List Discord guilds accessible to the configured bot.

Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Display the guilds and text channels visible to the Discord bot.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT
"""

import argparse
import asyncio
import os
from pathlib import Path

import discord
import yaml


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_token_env_key(config_path: Path) -> str:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return data.get("bot_token_env", "DISCORD_BOT_TOKEN")


class GuildLister(discord.Client):
    async def on_ready(self) -> None:
        print(f"Bot user: {self.user}")
        print("Guilds visiveis para o bot:")
        for g in sorted(self.guilds, key=lambda x: x.name.lower()):
            print(
                f"- name={g.name} | guild_id={g.id} | text_channels={len(g.text_channels)} | members={g.member_count}"
            )
        await self.close()


async def main_async(config_path: Path, env_path: Path) -> None:
    load_env_file(env_path)
    token_env_key = load_token_env_key(config_path)
    token = os.environ.get(token_env_key)
    if not token:
        raise RuntimeError(
            f"Token is missing: set {token_env_key} in {env_path} or in the environment."
        )
    if token.strip() == "replace_with_your_bot_token":
        raise RuntimeError(
            f"Token placeholder detectado em {env_path}. Substitua por um bot token real."
        )

    intents = discord.Intents.default()
    intents.guilds = True

    client = GuildLister(intents=intents)
    try:
        await client.start(token)
    except discord.LoginFailure as exc:
        raise RuntimeError(
            "Falha de autenticacao no Discord (token invalido). "
            "Use an official bot token from the Discord Developer Portal and confirm that the bot was added to the server."
        ) from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="List Discord guild IDs available to the bot")
    parser.add_argument("--config", default="discord_automation/config/discord_config.yaml")
    parser.add_argument("--env-file", default="discord_automation/.env")
    args = parser.parse_args()

    asyncio.run(main_async(Path(args.config), Path(args.env_file)))


if __name__ == "__main__":
    main()
