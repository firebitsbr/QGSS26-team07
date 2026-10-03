<!--
Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Document collection scope, outputs, limitations, and rerun commands.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT
-->

# Collection Status

## Scope
- ON24 QGSS26 hub + search content pages
- IBM Quantum Learning pages and tutorials

## Environment
- Local conda env path: `.conda`
- Python: 3.12.13
- Repro file: `environment-qgss26-conda.yml`
- Locked packages: `requirements-conda-qgss26.txt`

## What was collected

### ON24 QGSS26
- Canonical content links: 39
- HTML snapshots: 42
- Public media URLs found: 35
- Public media files downloaded: 36
- Video login-based attempts script prepared and executed

### IBM Quantum Learning
- Learning/tutorial links: 83
- HTML snapshots: 83
- Direct file asset URLs found (PDF/CSV/IPYNB/etc.): 10
- Direct files downloaded: 9

## Important limitation
- ON24 webcast streams are access-controlled and not directly downloadable from LP URLs using generic extractors.
- Even with browser cookies, `yt-dlp` reports unsupported ON24 LP URL format for these webcast pages.
- No authentication bypass was used.

## Re-run commands

```bash
cd "$(git rev-parse --show-toplevel)"

# All-in-one
./data/run_all_collection.sh

# ON24 public assets only
./data/qgss26/scripts/collect_public_assets.sh

# ON24 video attempts with existing browser login session
./data/qgss26/scripts/download_videos_with_login.sh firefox

# IBM Learning assets
./data/ibm_learning/scripts/collect_ibm_learning_assets.sh
```
