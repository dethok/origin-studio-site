#!/usr/bin/env bash
# Deploy the Origin Social Studio MVP to GitHub Pages (dethok/origin-studio-site, branch main, root).
# Preconditions: scripts/check.py ALL PASS; tree committed. Done = the live index.html hash equals the local one.
set -euo pipefail
cd "$(dirname "$0")"
REPO=dethok/origin-studio-site
URL=https://dethok.com/origin-studio-site/
[ -z "$(git status --porcelain)" ] || { echo "uncommitted changes — commit first"; exit 1; }
git push -u origin main
gh api -X POST "repos/$REPO/pages" -f build_type=legacy -f 'source[branch]=main' -f 'source[path]=/' >/dev/null 2>&1 || true
want=$(shasum -a 256 index.html | cut -c1-16)
for i in $(seq 1 40); do
  got=$(curl -fsSL "$URL" 2>/dev/null | shasum -a 256 | cut -c1-16 || true)
  if [ "$got" = "$want" ]; then echo "LIVE $URL ($want) at $(date '+%H:%M:%S')"; exit 0; fi
  sleep 10
done
echo "NOT LIVE after 400 s (want $want, got ${got:-none})"; exit 1
