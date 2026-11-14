#!/usr/bin/env bash
set -euo pipefail

mkdir -p api
python3 scripts/sync-charts.py

git config user.name "saferill"
git config user.email "saferill@users.noreply.github.com"
if ! git diff --quiet api/playlists.json; then
  git add api/playlists.json
  git commit -m "chore(charts): auto-update trending chart playlists"
  BRANCH="${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
  git pull --rebase origin "$BRANCH" || true
  git push origin HEAD
else
  echo "No changes in api/playlists.json"
fi
