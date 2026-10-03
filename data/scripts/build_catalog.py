#!/usr/bin/env python3
"""Build a unified, organized catalog of all collected QGSS26 material.

Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Generate a searchable catalog of collected QGSS26 resources.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT

Sources:
  - ON24 QGSS26 snapshots      (data/qgss26)
  - IBM Quantum Learning       (data/ibm_learning)
  - Discord export, if present (discord_automation/output/**/messages/*.ndjson)

Outputs (data/catalog):
  - catalog.json   full structured index
  - resources.csv  flat table of every resource
  - INDEX.md       human-readable browsable index
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = ROOT / "data" / "catalog"

SOURCES = {
    "on24_qgss26": ROOT / "data" / "qgss26",
    "ibm_learning": ROOT / "data" / "ibm_learning",
}


@dataclass
class Resource:
    source: str
    kind: str
    title: str
    url: str
    local_path: str = ""
    referenced_by: str = ""


@dataclass
class Catalog:
    pages: list[Resource] = field(default_factory=list)
    assets: list[Resource] = field(default_factory=list)
    discord_links: list[Resource] = field(default_factory=list)


def read_pipe_rows(path: Path, expected_cols: int) -> list[list[str]]:
    """Read the '|'-delimited manifests produced by the collector scripts."""
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) >= expected_cols:
            rows.append(parts)
    return rows


def html_title(path: Path) -> str:
    try:
        soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
    except OSError:
        return ""
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else ""


def classify_page(url: str) -> str:
    u = url.lower()
    if "/category/" in u and "lecture" in u:
        return "lecture"
    if "/docs/tutorials" in u or "/tutorial" in u:
        return "tutorial"
    if "/category/" in u:
        return "section"
    if "/docs/" in u:
        return "documentation"
    if "/lp/" in u or "webcast" in u:
        return "session"
    return "page"


def classify_asset(url: str) -> str:
    u = url.lower().split("?")[0]
    if u.endswith(".ipynb"):
        return "notebook"
    if u.endswith(".pdf"):
        return "pdf"
    if u.endswith((".csv", ".json", ".tsv")):
        return "dataset"
    if u.endswith((".mp4", ".m3u8", ".webm")):
        return "video"
    if u.endswith((".png", ".jpg", ".jpeg", ".svg", ".gif")):
        return "image"
    if "github.com" in u or "githubusercontent.com" in u:
        return "code"
    return "file"


def collect_pages(source: str, base: Path) -> list[Resource]:
    out = []
    for row in read_pipe_rows(base / "manifests" / "html_map.tsv", 3):
        url, local = row[1], row[2]
        local_path = Path(local)
        out.append(
            Resource(
                source=source,
                kind=classify_page(url),
                title=html_title(local_path) or url.rstrip("/").rsplit("/", 1)[-1],
                url=url,
                local_path=str(local_path.relative_to(ROOT)) if local_path.is_relative_to(ROOT) else local,
            )
        )
    return out


def collect_assets(source: str, base: Path) -> list[Resource]:
    out = []
    for name, cols in (("file_assets.tsv", 2), ("direct_media_links.tsv", 2)):
        for row in read_pipe_rows(base / "manifests" / name, cols):
            referenced_by, url = row[0], row[1]
            ref = Path(referenced_by)
            out.append(
                Resource(
                    source=source,
                    kind=classify_asset(url),
                    title=url.split("/")[-1].split("?")[0] or url,
                    url=url,
                    referenced_by=str(ref.relative_to(ROOT)) if ref.is_relative_to(ROOT) else referenced_by,
                )
            )

    downloads = base / "downloads"
    if downloads.is_dir():
        for f in sorted(downloads.rglob("*")):
            if f.is_file():
                out.append(
                    Resource(
                        source=source,
                        kind=classify_asset(f.name),
                        title=f.name,
                        url="",
                        local_path=str(f.relative_to(ROOT)),
                    )
                )
    return out


URL_RE = re.compile(r"https?://[^\s)>\]\"']+")


def collect_discord_links() -> list[Resource]:
    """Absorb links from an authorized Discord export, when one exists."""
    out: list[Resource] = []
    seen: set[str] = set()
    msg_dir = ROOT / "discord_automation" / "output"
    if not msg_dir.is_dir():
        return out

    for nd in sorted(msg_dir.rglob("messages/*.ndjson")):
        channel = nd.stem.split("_", 1)[-1]
        for line in nd.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            urls = list(msg.get("urls") or []) or URL_RE.findall(msg.get("content", ""))
            for a in msg.get("attachments") or []:
                if a.get("url"):
                    urls.append(a["url"])
            for u in urls:
                if u in seen:
                    continue
                seen.add(u)
                out.append(
                    Resource(
                        source="discord",
                        kind=classify_asset(u),
                        title=u.split("/")[-1].split("?")[0] or u,
                        url=u,
                        referenced_by=channel,
                    )
                )
    return out


def dedupe(items: list[Resource]) -> list[Resource]:
    seen: set[tuple[str, str, str]] = set()
    out = []
    for r in items:
        key = (r.source, r.url, r.local_path)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def write_markdown(cat: Catalog, path: Path) -> None:
    lines = [
        "<!--",
        "Author: Mauro Risonho de Paula Assumpção",
        "Date Created: Not recorded",
        "Date Updated: 2026-10-03",
        "Short Description: Browse collected QGSS26 pages, files, and shared links.",
        "Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.",
        "License: MIT",
        "-->",
        "",
        "# QGSS26 - Collected Material Index",
        "",
    ]
    total = len(cat.pages) + len(cat.assets) + len(cat.discord_links)
    lines += [
        f"Total resources: **{total}**",
        "",
        f"- Pages: {len(cat.pages)}",
        f"- Files/assets: {len(cat.assets)}",
        f"- Discord links: {len(cat.discord_links)}",
        "",
    ]

    for source in SOURCES:
        pages = [p for p in cat.pages if p.source == source]
        if not pages:
            continue
        lines += [f"## Pages — {source}", ""]
        by_kind: dict[str, list[Resource]] = {}
        for p in pages:
            by_kind.setdefault(p.kind, []).append(p)
        for kind in sorted(by_kind):
            lines += [f"### {kind} ({len(by_kind[kind])})", ""]
            for p in sorted(by_kind[kind], key=lambda r: r.title.lower()):
                target = p.local_path or p.url
                lines.append(f"- [{p.title}]({target})")
            lines.append("")

    if cat.assets:
        lines += ["## Files and assets", ""]
        by_kind = {}
        for a in cat.assets:
            by_kind.setdefault(a.kind, []).append(a)
        for kind in sorted(by_kind):
            lines += [f"### {kind} ({len(by_kind[kind])})", ""]
            for a in sorted(by_kind[kind], key=lambda r: r.title.lower()):
                target = a.local_path or a.url
                lines.append(f"- [{a.title}]({target})")
            lines.append("")

    if cat.discord_links:
        lines += ["## Links shared on Discord", ""]
        by_channel: dict[str, list[Resource]] = {}
        for d in cat.discord_links:
            by_channel.setdefault(d.referenced_by, []).append(d)
        for ch in sorted(by_channel):
            lines += [f"### #{ch} ({len(by_channel[ch])})", ""]
            for d in by_channel[ch]:
                lines.append(f"- [{d.title}]({d.url})")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_csv(cat: Catalog, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source", "kind", "title", "url", "local_path", "referenced_by"])
        w.writeheader()
        for r in cat.pages + cat.assets + cat.discord_links:
            w.writerow(asdict(r))


def main() -> None:
    cat = Catalog()
    for source, base in SOURCES.items():
        if not base.is_dir():
            continue
        cat.pages.extend(collect_pages(source, base))
        cat.assets.extend(collect_assets(source, base))
    cat.discord_links = collect_discord_links()

    cat.pages = dedupe(cat.pages)
    cat.assets = dedupe(cat.assets)

    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    (CATALOG_DIR / "catalog.json").write_text(
        json.dumps(
            {
                "pages": [asdict(r) for r in cat.pages],
                "assets": [asdict(r) for r in cat.assets],
                "discord_links": [asdict(r) for r in cat.discord_links],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    write_csv(cat, CATALOG_DIR / "resources.csv")
    write_markdown(cat, CATALOG_DIR / "INDEX.md")

    print(f"pages={len(cat.pages)} assets={len(cat.assets)} discord_links={len(cat.discord_links)}")
    print(f"output -> {CATALOG_DIR.relative_to(ROOT)}/ (catalog.json, resources.csv, INDEX.md)")


if __name__ == "__main__":
    main()
