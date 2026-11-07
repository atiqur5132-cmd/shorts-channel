#!/usr/bin/env bash
# Render a short on GitHub Actions and download it.
#   bash tools/render_cloud.sh shorts/02-buffett-time ["commit message"]
# -> <short>/renders/final.mp4 (-14 LUFS) and <short>/renders/phone.mp4 (<30 MB preview)
set -euo pipefail
cd "$(dirname "$0")/.."
SHORT="${1:?usage: render_cloud.sh <short-dir>}"
MSG="${2:-Render $SHORT}"
git add -A "$SHORT" tools library .github .gitignore
if ! git diff --cached --quiet; then
  git -c user.name="atiqur5132-cmd" -c user.email="atiqur5132-cmd@users.noreply.github.com" commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
git push -q origin main
before=$(gh run list --workflow render.yml --limit 1 --json databaseId --jq '.[0].databaseId // 0')
gh workflow run render.yml -f project="$SHORT" -f quality=delivery -f run_check=false
run=""
for i in $(seq 1 30); do
  sleep 3
  run=$(gh run list --workflow render.yml --limit 1 --json databaseId --jq '.[0].databaseId')
  [ "$run" != "$before" ] && break
done
echo "run: https://github.com/atiqur5132-cmd/shorts-channel/actions/runs/$run"
gh run watch "$run" --interval 20 --exit-status > /dev/null
mkdir -p "$SHORT/renders"
rm -f "$SHORT/renders/final.mp4"
gh run download "$run" -n "short-$run" -D "$SHORT/renders"
ffmpeg -y -loglevel error -i "$SHORT/renders/final.mp4" -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -c:a copy -movflags +faststart "$SHORT/renders/phone.mp4"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$SHORT/renders/final.mp4"
ffmpeg -hide_banner -i "$SHORT/renders/final.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tail -2
echo "done: $SHORT/renders/final.mp4"
