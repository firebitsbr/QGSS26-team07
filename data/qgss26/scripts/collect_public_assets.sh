#!/usr/bin/env bash
# Author: Mauro Risonho de Paula Assumpção
# Date Created: Not recorded
# Date Updated: 2026-10-03
# Short Description: Collect publicly accessible ON24 QGSS26 assets.
# Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
# License: MIT

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
BASE_URL="https://gateway.on24.com/wcc/eh/5192571/qiskit-global-summer-school-2026"
DATA_DIR="$ROOT_DIR/data/qgss26"
HTML_DIR="$DATA_DIR/html"
MANIFEST_DIR="$DATA_DIR/manifests"
DOWNLOAD_DIR="$DATA_DIR/downloads/public_media"

mkdir -p "$HTML_DIR" "$MANIFEST_DIR" "$DOWNLOAD_DIR"

# Refresh hub shell page.
curl -Ls "$BASE_URL" -o "$HTML_DIR/hub.html"

# Download all known content pages from manifest.
if [[ -f "$MANIFEST_DIR/all_content_links.txt" ]]; then
  i=0
  while IFS= read -r u; do
    [[ -z "$u" ]] && continue
    i=$((i + 1))
    slug=$(echo "$u" | sed -E 's#https?://##; s#[^a-zA-Z0-9._-]+#_#g')
    curl -Ls "$u" -o "$HTML_DIR/${i}_${slug}.html"
    echo "$i|$u|$HTML_DIR/${i}_${slug}.html"
  done < "$MANIFEST_DIR/all_content_links.txt" > "$MANIFEST_DIR/html_map.tsv"
fi

# Extract and download public media URLs found in html source.
rg -No 'https?://[^"'"'"' >]+/media/[^"'"'"' >]+' "$HTML_DIR" \
  | sed 's#^.*:##' \
  | sed 's#^http://#https://#g' \
  | sort -u > "$MANIFEST_DIR/public_media_urls.txt"

while IFS= read -r u; do
  [[ -z "$u" ]] && continue
  full="https:${u}"
  file_name=$(basename "${full%%\?*}")
  [[ -n "$file_name" ]] || continue
  curl -fLs "$full" -o "$DOWNLOAD_DIR/$file_name" || true
done < "$MANIFEST_DIR/public_media_urls.txt"

{
  if [[ -f "$MANIFEST_DIR/all_content_links.txt" ]]; then
    echo "content_links=$(wc -l < "$MANIFEST_DIR/all_content_links.txt")"
  else
    echo "content_links=0"
  fi

  echo "html_pages=$(find "$HTML_DIR" -maxdepth 1 -type f -name '*.html' | wc -l)"

  if [[ -f "$MANIFEST_DIR/public_media_urls.txt" ]]; then
    echo "public_media_urls=$(wc -l < "$MANIFEST_DIR/public_media_urls.txt")"
  else
    echo "public_media_urls=0"
  fi

  echo "public_media_downloaded=$(find "$DOWNLOAD_DIR" -maxdepth 1 -type f | wc -l)"
} > "$MANIFEST_DIR/collection_summary.txt"

echo "Done. Summary in $MANIFEST_DIR/collection_summary.txt"
