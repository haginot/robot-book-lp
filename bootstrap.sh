#!/usr/bin/env bash
# bootstrap.sh — ワンコマンドでリポジトリ作成〜24時間ループ起動まで
#
# 使い方:
#   1. gh auth login  (未認証なら)
#   2. export ANTHROPIC_API_KEY=sk-ant-...   (Claude API key)
#   3. export GSK_TOKEN=...                  (Genspark API key)
#   4. bash bootstrap.sh
#
set -euo pipefail

REPO_NAME="${REPO_NAME:-robot-book-lp}"
VISIBILITY="${VISIBILITY:-public}"

echo "== 1. Checking prerequisites =="
command -v gh >/dev/null || { echo "ERROR: gh CLI not installed"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "ERROR: run 'gh auth login' first"; exit 1; }
[ -n "${ANTHROPIC_API_KEY:-}" ] || { echo "ERROR: export ANTHROPIC_API_KEY first"; exit 1; }
[ -n "${GSK_TOKEN:-}" ] || { echo "ERROR: export GSK_TOKEN first"; exit 1; }

echo "== 2. Initializing git =="
if [ ! -d .git ]; then
  git init -b main
fi
git add .
git diff --staged --quiet || git commit -m "initial: v3 (score 95/100)"

echo "== 3. Creating GitHub repo =="
if ! gh repo view "$REPO_NAME" >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --push
else
  echo "  repo exists, pushing..."
  git remote get-url origin >/dev/null 2>&1 || \
    gh repo set-default "$REPO_NAME"
  git push -u origin main || true
fi

REPO_FULL=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "  repo: https://github.com/$REPO_FULL"

echo "== 4. Registering secrets =="
gh secret set ANTHROPIC_API_KEY -b "$ANTHROPIC_API_KEY" --repo "$REPO_FULL"
gh secret set GSK_TOKEN         -b "$GSK_TOKEN"         --repo "$REPO_FULL"

echo "== 5. Enabling GitHub Pages =="
gh api -X POST "repos/$REPO_FULL/pages" \
  -f "source[branch]=main" -f "source[path]=/" 2>/dev/null || echo "  pages already enabled"

echo "== 6. Triggering first workflow run =="
gh workflow run 24h-loop.yml --repo "$REPO_FULL"
sleep 3
gh run list --repo "$REPO_FULL" --workflow=24h-loop.yml --limit 1

echo ""
echo "✅ Bootstrap complete!"
echo "   Repo:      https://github.com/$REPO_FULL"
echo "   Actions:   https://github.com/$REPO_FULL/actions"
echo "   Site:      https://${REPO_FULL/\//.github.io/}"
echo ""
echo "24時間ループが 2時間ごとに自動発火します。"
