#!/usr/bin/env bash
# Cloudflare Pages 배포 — 생년월일이 없는 랜덤 URL.
#   ./tools/deploy_cf.sh [프로젝트슬러그]
set -euo pipefail
SLUG="${1:-ecg-echo-a1311d}"
cd "$(dirname "$0")/.."
set -a; . "$HOME/.config/cloudflare/api_token"; set +a
export CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID
STAGE="/tmp/deploy-$SLUG"
rm -rf "$STAGE"; mkdir -p "$STAGE"
rsync -a --exclude '.git' --exclude 'tools' --exclude '*.md' \
      --exclude 'wrangler.jsonc' --exclude '.assetsignore' ./ "$STAGE/"
cd "$STAGE"
bunx --bun wrangler pages deploy . --project-name "$SLUG" --branch main --commit-dirty=true 2>&1 | tail -4
echo "https://$SLUG.pages.dev/"
