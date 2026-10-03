#!/usr/bin/env bash
# Author: Mauro Risonho de Paula Assumpção
# Date Created: Not recorded
# Date Updated: 2026-10-03
# Short Description: Run the QGSS26 and IBM Quantum Learning collection workflows.
# Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
# License: MIT

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/3] Collecting ON24 public assets..."
data/qgss26/scripts/collect_public_assets.sh

echo "[2/3] Attempting ON24 video download with existing browser login (if supported)..."
data/qgss26/scripts/download_videos_with_login.sh firefox || true

echo "[3/3] Collecting IBM Learning public assets..."
data/ibm_learning/scripts/collect_ibm_learning_assets.sh

printf "\n=== Summary ===\n"
echo "QGSS26:"
cat data/qgss26/manifests/collection_summary.txt

printf "\nIBM Learning:\n"
cat data/ibm_learning/manifests/collection_summary.txt

printf "\nNote: ON24 webcast video downloads depend on platform support and authenticated access.\n"
