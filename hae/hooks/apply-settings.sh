#!/usr/bin/env bash
# Chị chạy tay:  bash "/Users/nngangaa/Downloads/AI Agent/skills-personal/hae/hooks/apply-settings.sh"
# Backup rồi vá ~/.claude/settings.json; in diff để chị xem trước khi restart Claude Code.
set -eu
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HOME/.claude/settings.json"
B="$S.bak-$(date +%Y%m%d-%H%M%S)"
cp "$S" "$B"
jq -f "$DIR/settings-patch.jq" "$B" > "$S.tmp" && mv "$S.tmp" "$S"
echo "Backup: $B"
echo "--- diff (chỉ phần thêm) ---"
diff <(jq -S . "$B") <(jq -S . "$S") || true
echo "--- xong. Khởi động lại Claude Code để hook có hiệu lực. ---"
