#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
"""Collect Discord server data using the official bot API.

Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Export accessible Discord messages, attachments, and collection state.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT
"""

from pathlib import Path
from typing import Any

import aiofiles
import aiohttp
import discord
import yaml


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


@dataclass
class Config:
    bot_token_env: str
    guild_id: int | None
    include_channel_ids: list[int]
    include_channel_names_exact: list[str]
    history_limit_per_channel: int
    max_attachments_per_run: int
    include_channel_name_patterns: list[str]
    exclude_channel_name_patterns: list[str]
    output_dir: Path


@dataclass
class RunStats:
    channels_scanned: int = 0
    messages_exported: int = 0
    attachments_discovered: int = 0
    attachments_downloaded: int = 0


def load_config(config_path: Path) -> Config:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return Config(
        bot_token_env=data.get("bot_token_env", "DISCORD_BOT_TOKEN"),
        guild_id=data.get("guild_id"),
        include_channel_ids=[int(x) for x in data.get("include_channel_ids", [])],
        include_channel_names_exact=[str(x).strip().lower() for x in data.get("include_channel_names_exact", []) if str(x).strip()],
        history_limit_per_channel=int(data.get("history_limit_per_channel", 5000)),
        max_attachments_per_run=int(data.get("max_attachments_per_run", 500)),
        include_channel_name_patterns=list(data.get("include_channel_name_patterns", [])),
        exclude_channel_name_patterns=list(data.get("exclude_channel_name_patterns", [])),
        output_dir=Path(data.get("output_dir", "discord_automation/output")),
    )


def channel_allowed(
    channel_id: int,
    name: str,
    include_ids: set[int],
    include_names_exact: set[str],
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> bool:
    lname = name.lower()
    if include_ids and channel_id not in include_ids:
        return False
    if include_names_exact and lname not in include_names_exact:
        return False
    if include_patterns:
        if not any(re.search(p, name) for p in include_patterns):
            return False
    if exclude_patterns:
        if any(re.search(p, name) for p in exclude_patterns):
            return False
    return True


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("_") or "file"


def extract_urls(text: str | None) -> list[str]:
    if not text:
        return []
    return re.findall(r"https?://[^\s)>\]\"]+", text)


def message_to_dict(msg: discord.Message) -> dict[str, Any]:
    return {
        "id": msg.id,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
        "edited_at": msg.edited_at.isoformat() if msg.edited_at else None,
        "author": {
            "id": msg.author.id,
            "name": str(msg.author),
            "bot": msg.author.bot,
        },
        "channel_id": msg.channel.id,
        "channel_name": getattr(msg.channel, "name", "unknown"),
        "content": msg.content,
        "urls": extract_urls(msg.content),
        "attachments": [
            {
                "id": a.id,
                "filename": a.filename,
                "size": a.size,
                "content_type": a.content_type,
                "url": a.url,
                "proxy_url": a.proxy_url,
            }
            for a in msg.attachments
        ],
        "embeds": [e.to_dict() for e in msg.embeds],
        "jump_url": msg.jump_url,
    }


async def download_file(session: aiohttp.ClientSession, url: str, out_path: Path) -> bool:
    try:
        async with session.get(url, timeout=60) as resp:
            if resp.status != 200:
                return False
            out_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(out_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 64):
                    await f.write(chunk)
            return True
    except Exception:
        return False


class CollectorClient(discord.Client):
    def __init__(self, cfg: Config, state_path: Path, run_dir: Path, **kwargs: Any):
        super().__init__(**kwargs)
        self.cfg = cfg
        self.state_path = state_path
        self.run_dir = run_dir
        self.state: dict[str, Any] = {}
        self.stats = RunStats()

    def load_state(self) -> None:
        if self.state_path.exists():
            self.state = json.loads(self.state_path.read_text(encoding="utf-8"))
        else:
            self.state = {"channels": {}, "last_run": None}

    def save_state(self) -> None:
        self.state["last_run"] = utc_now_iso()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def pick_guild(self) -> discord.Guild:
        if self.cfg.guild_id is not None:
            g = self.get_guild(int(self.cfg.guild_id))
            if g is None:
                raise RuntimeError(f"Guild {self.cfg.guild_id} not found for this bot")
            return g
        guilds = list(self.guilds)
        if not guilds:
            raise RuntimeError("Bot is not in any guild")
        return guilds[0]

    async def on_ready(self) -> None:
        self.load_state()
        guild = self.pick_guild()

        run_meta = {
            "run_started_at": utc_now_iso(),
            "bot_user": str(self.user),
            "guild": {"id": guild.id, "name": guild.name},
            "config": {
                "history_limit_per_channel": self.cfg.history_limit_per_channel,
                "max_attachments_per_run": self.cfg.max_attachments_per_run,
            },
            "channels": [],
        }

        messages_dir = self.run_dir / "messages"
        attachments_dir = self.run_dir / "attachments"
        manifests_dir = self.run_dir / "manifests"
        messages_dir.mkdir(parents=True, exist_ok=True)
        attachments_dir.mkdir(parents=True, exist_ok=True)
        manifests_dir.mkdir(parents=True, exist_ok=True)

        attachment_queue: list[tuple[str, Path]] = []

        channels = sorted(guild.text_channels, key=lambda c: c.position)
        include_ids = set(self.cfg.include_channel_ids)
        include_names_exact = set(self.cfg.include_channel_names_exact)

        for ch in channels:
            if not channel_allowed(
                ch.id,
                ch.name,
                include_ids,
                include_names_exact,
                self.cfg.include_channel_name_patterns,
                self.cfg.exclude_channel_name_patterns,
            ):
                continue

            self.stats.channels_scanned += 1
            channel_state = self.state["channels"].get(str(ch.id), {})
            after_id = channel_state.get("last_message_id")
            after_obj = discord.Object(id=int(after_id)) if after_id else None

            out_file = messages_dir / f"{ch.id}_{sanitize_filename(ch.name)}.ndjson"
            written = 0
            newest_id = int(after_id) if after_id else 0

            async with aiofiles.open(out_file, "a", encoding="utf-8") as f:
                async for msg in ch.history(limit=self.cfg.history_limit_per_channel, oldest_first=True, after=after_obj):
                    d = message_to_dict(msg)
                    await f.write(json.dumps(d, ensure_ascii=False) + "\n")
                    written += 1
                    self.stats.messages_exported += 1
                    newest_id = max(newest_id, msg.id)

                    for a in msg.attachments:
                        self.stats.attachments_discovered += 1
                        out_name = f"{msg.id}_{a.id}_{sanitize_filename(a.filename)}"
                        out_path = attachments_dir / str(ch.id) / out_name
                        attachment_queue.append((a.url, out_path))

            if newest_id:
                self.state["channels"][str(ch.id)] = {
                    "channel_name": ch.name,
                    "last_message_id": str(newest_id),
                    "updated_at": utc_now_iso(),
                }

            run_meta["channels"].append(
                {
                    "id": ch.id,
                    "name": ch.name,
                    "messages_written": written,
                    "output": str(out_file),
                }
            )

        attachment_queue = attachment_queue[: self.cfg.max_attachments_per_run]
        connector = aiohttp.TCPConnector(limit=8)
        async with aiohttp.ClientSession(connector=connector) as session:
            for url, out_path in attachment_queue:
                ok = await download_file(session, url, out_path)
                if ok:
                    self.stats.attachments_downloaded += 1

        run_meta["stats"] = {
            "channels_scanned": self.stats.channels_scanned,
            "messages_exported": self.stats.messages_exported,
            "attachments_discovered": self.stats.attachments_discovered,
            "attachments_downloaded": self.stats.attachments_downloaded,
        }
        run_meta["run_finished_at"] = utc_now_iso()

        (manifests_dir / "run_summary.json").write_text(json.dumps(run_meta, indent=2, ensure_ascii=False), encoding="utf-8")
        self.save_state()
        await self.close()


async def run_collection(config_path: Path, env_path: Path) -> None:
    load_env_file(env_path)
    cfg = load_config(config_path)

    token = os.environ.get(cfg.bot_token_env)
    if not token or token == "replace_with_your_bot_token":
        raise RuntimeError(
            f"Missing valid bot token in env var '{cfg.bot_token_env}'. "
            f"Create an official Discord bot, invite it to the server with View Channels and Read Message History, "
            f"then set the token in {env_path}."
        )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = cfg.output_dir / f"run_{ts}"
    state_path = cfg.output_dir / "state" / "collector_state.json"

    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True

    client = CollectorClient(cfg=cfg, state_path=state_path, run_dir=run_dir, intents=intents)
    await client.start(token)


def main() -> None:
    parser = argparse.ArgumentParser(description="Discord organized collector (official bot API)")
    parser.add_argument(
        "--config",
        default="discord_automation/config/discord_config.yaml",
        help="Path to YAML config",
    )
    parser.add_argument(
        "--env-file",
        default="discord_automation/.env",
        help="Path to .env file",
    )
    args = parser.parse_args()

    asyncio.run(run_collection(Path(args.config), Path(args.env_file)))


if __name__ == "__main__":
    main()
