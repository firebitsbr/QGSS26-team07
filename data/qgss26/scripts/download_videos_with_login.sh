#!/usr/bin/env bash
# Author: Mauro Risonho de Paula Assumpção
# Date Created: Not recorded
# Date Updated: 2026-10-03
# Short Description: Attempt ON24 video downloads using an existing browser login session.
# Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
# License: MIT

set -euo pipefail

# Usage:
#   ./data/qgss26/scripts/download_videos_with_login.sh firefox
#   ./data/qgss26/scripts/download_videos_with_login.sh chrome
#
# Requires a logged-in ON24 session in the chosen browser profile.
# This script does not bypass authentication; it only uses your existing session cookies.

BROWSER="${1:-firefox}"
ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT_DIR="$ROOT_DIR/data/qgss26/downloads/videos"
LOG_DIR="$ROOT_DIR/data/qgss26/logs"
LINKS_FILE="$ROOT_DIR/data/qgss26/manifests/all_content_links.txt"

if [[ -x "$ROOT_DIR/.conda/bin/yt-dlp" ]]; then
  YTDLP_BIN="$ROOT_DIR/.conda/bin/yt-dlp"
elif [[ -x "$ROOT_DIR/.venv/bin/yt-dlp" ]]; then
  YTDLP_BIN="$ROOT_DIR/.venv/bin/yt-dlp"
else
  echo "yt-dlp not found in .conda or .venv" >&2
  exit 1
fi

mkdir -p "$OUT_DIR" "$LOG_DIR"

if [[ ! -f "$LINKS_FILE" ]]; then
  echo "Missing links file: $LINKS_FILE" >&2
  exit 1
fi

# Try each LP URL. yt-dlp will skip pages without downloadable media.
while IFS= read -r url; do
  [[ -z "$url" ]] && continue
  if [[ "$url" != *"/lp/"* ]]; then
    continue
  fi

  echo "[INFO] Processing: $url"
  "$YTDLP_BIN" \
    --cookies-from-browser "$BROWSER" \
    --restrict-filenames \
    --concurrent-fragments 4 \
    --retries 10 \
    --fragment-retries 20 \
    --no-overwrites \
    -o "$OUT_DIR/%(title).180B [%(id)s].%(ext)s" \
    "$url" >> "$LOG_DIR/yt-dlp.log" 2>&1 || true

done < "$LINKS_FILE"

echo "[DONE] Video download attempts finished. Check: $LOG_DIR/yt-dlp.log"
