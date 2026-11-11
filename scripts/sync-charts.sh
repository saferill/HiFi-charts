#!/usr/bin/env bash
set -euo pipefail

mkdir -p api
curl -fsSL "https://chart.simpmusic.org/api/playlists" -o /tmp/raw_playlists.json
jq '.data = (([.data[] | select(.country == "id")] + [.data[] | select(.country == "global")] + [.data[] | select(.country != "id" and .country != "global")]))' /tmp/raw_playlists.json > api/playlists.json

git config user.name "saferill"
git config user.email "saferill@users.noreply.github.com"
if ! git diff --quiet api/playlists.json; then
  git add api/playlists.json
  git commit -m "chore(charts): auto-update trending chart playlists"
  git push origin main
else
  echo "No changes in api/playlists.json"
fi