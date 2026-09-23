#!/usr/bin/env bash
# Hae — transport shim cho env-guard.py. Không parse gì ở đây (bash 3.2 / BSD userland).
# Nếu python không chạy được hoặc script lỗi -> trả "ask" thay vì lặng lẽ allow.
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if out="$(python3 "$DIR/env-guard.py" 2>/tmp/hae-env-guard.err)"; then
  [ -n "$out" ] && printf '%s\n' "$out"
  exit 0
fi
err="$(tr '\n' ' ' </tmp/hae-env-guard.err | cut -c1-300)"
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Hae env-guard không kiểm tra được URL (%s). Chị xem rồi quyết."}}\n' "$(printf '%s' "$err" | sed 's/"/\\"/g')"
exit 0
