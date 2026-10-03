#!/usr/bin/env bash
# Author: Mauro Risonho de Paula Assumpção
# Date Created: Not recorded
# Date Updated: 2026-10-03
# Short Description: Collect publicly accessible IBM Quantum Learning assets.
# Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
# License: MIT

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
DATA_DIR="$ROOT_DIR/data/ibm_learning"
MANIFEST_DIR="$DATA_DIR/manifests"
HTML_DIR="$DATA_DIR/html"
DOWNLOAD_DIR="$DATA_DIR/downloads/files"

mkdir -p "$MANIFEST_DIR" "$HTML_DIR" "$DOWNLOAD_DIR"

if [[ ! -f "$MANIFEST_DIR/all_links.txt" ]]; then
  echo "Missing manifest: $MANIFEST_DIR/all_links.txt" >&2
  exit 1
fi

# Download/refresh HTML snapshots.
i=0
while IFS= read -r u; do
  [[ -z "$u" ]] && continue
  i=$((i + 1))
  slug=$(echo "$u" | sed -E 's#https?://##; s#[^a-zA-Z0-9._-]+#_#g')
  curl -Ls "$u" -o "$HTML_DIR/${i}_${slug}.html"
  echo "$i|$u|$HTML_DIR/${i}_${slug}.html"
done < "$MANIFEST_DIR/all_links.txt" > "$MANIFEST_DIR/html_map.tsv"

# Extract direct file assets.
rg -No 'https?://[^"'"'"' >]+\.(pdf|ipynb|csv|json|zip|tar\.gz)(\?[^"'"'"' >]*)?' "$HTML_DIR" \
  | sed 's/:/|/1' \
  | sort -u > "$MANIFEST_DIR/file_assets.tsv"

cut -d'|' -f2 "$MANIFEST_DIR/file_assets.tsv" \
  | sed 's/\\\\\+$//' \
  | sed 's/&quot;.*$//' \
  | sed '/^$/d' \
  | sort -u > "$MANIFEST_DIR/file_asset_urls.txt"

while IFS= read -r u; do
  [[ -z "$u" ]] && continue
  f=$(basename "${u%%\?*}")
  [[ -n "$f" ]] || continue
  curl -fLs "$u" -o "$DOWNLOAD_DIR/$f" || true
done < "$MANIFEST_DIR/file_asset_urls.txt"

{
  echo "learning_links=$(wc -l < "$MANIFEST_DIR/all_links.txt")"
  echo "learning_html_pages=$(find "$HTML_DIR" -maxdepth 1 -type f -name '*.html' | wc -l)"
  echo "learning_file_assets=$(wc -l < "$MANIFEST_DIR/file_asset_urls.txt")"
  echo "learning_files_downloaded=$(find "$DOWNLOAD_DIR" -maxdepth 1 -type f | wc -l)"
} > "$MANIFEST_DIR/collection_summary.txt"

echo "Done. Summary: $MANIFEST_DIR/collection_summary.txt"
