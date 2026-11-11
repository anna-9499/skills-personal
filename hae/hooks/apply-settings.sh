#!/usr/bin/env bash
# Chị chạy tay:  bash "<repo>/hae/hooks/apply-settings.sh"  (đường dẫn env-guard.sh tự tính theo vị trí script)
# Backup rồi vá ~/.claude/settings.json; in diff để chị xem trước khi restart Claude Code.
set -eu
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HOME/.claude/settings.json"
B="$S.bak-$(date +%Y%m%d-%H%M%S)"
cp "$S" "$B"
[ -f "$DIR/env-guard.sh" ] || { echo "Không thấy $DIR/env-guard.sh — dừng, settings.json chưa đổi." >&2; rm -f "$B"; exit 1; }
jq --arg guard "$DIR/env-guard.sh" -f "$DIR/settings-patch.jq" "$B" && mv "$S.tmp" "$S"
echo "Backup: $B"
echo "--- diff (chỉ phần thêm) ---"
diff <(jq -S . "$B") <(jq -S . "$S") || true
echo "--- xong. Khởi động lại Claude Code để hook có hiệu lực. ---"
