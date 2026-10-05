#!/usr/bin/env bash
# Khoá staging dùng chung giữa Hae (sonder, ash) và Luke (healer) — một app một khoá.
#
#   staging-lock.sh status  <KEY>
#   staging-lock.sh acquire <KEY> <owner> [ghi chú]   # owner vd: hae:sonder:<taskId>, luke:healer:<TICKET>
#   staging-lock.sh release <KEY> <owner>
#   staging-lock.sh release <KEY> --force              # chỉ khi chị bảo
#
# Exit: 0 = được / trống · 1 = đang bận (in người giữ) · 2 = sai cú pháp.
# Khoá quá STALE_HOURS (mặc định 3) coi là bỏ quên: acquire ghi đè và in "STALE-OVERRIDE".
set -euo pipefail

LOCK_DIR="${HAE_LOCK_DIR:-$HOME/.hae/locks}"
STALE_HOURS="${HAE_LOCK_STALE_HOURS:-3}"

cmd="${1:-}"; key="${2:-}"
[[ -z "$cmd" || -z "$key" ]] && { sed -n '2,10p' "$0"; exit 2; }
key="$(printf '%s' "$key" | tr '[:lower:]' '[:upper:]')"
mkdir -p "$LOCK_DIR"
file="$LOCK_DIR/$key.lock"

now=$(date +%s)
read_lock() { # -> owner since note age_min
  [[ -f "$file" ]] || return 1
  owner=$(sed -n 's/^owner=//p' "$file"); since=$(sed -n 's/^since=//p' "$file"); note=$(sed -n 's/^note=//p' "$file")
  age_min=$(( (now - since) / 60 ))
}
is_stale() { (( age_min >= STALE_HOURS * 60 )); }
show() { echo "BUSY $key owner=$owner since=$(date -r "$since" '+%Y-%m-%d %H:%M') (${age_min} phút) note=$note"; }

case "$cmd" in
  status)
    if read_lock; then
      if is_stale; then echo "STALE $key owner=$owner (${age_min} phút) — coi như trống"; exit 0; fi
      show; exit 1
    fi
    echo "FREE $key"; exit 0 ;;
  acquire)
    owner_new="${3:-}"; note_new="${4:-}"
    [[ -z "$owner_new" ]] && { echo "thiếu owner"; exit 2; }
    if read_lock; then
      if [[ "$owner" == "$owner_new" ]]; then :            # gia hạn khoá của chính mình
      elif is_stale; then echo "STALE-OVERRIDE $key (khoá cũ: $owner, ${age_min} phút)"
      else show; exit 1; fi
    fi
    tmp="$file.$$"
    printf 'owner=%s\nsince=%s\nnote=%s\n' "$owner_new" "$now" "$note_new" > "$tmp"
    mv "$tmp" "$file"
    echo "ACQUIRED $key owner=$owner_new"; exit 0 ;;
  release)
    who="${3:-}"
    [[ -z "$who" ]] && { echo "thiếu owner (hoặc --force)"; exit 2; }
    if ! read_lock; then echo "FREE $key (không có khoá)"; exit 0; fi
    if [[ "$who" == "--force" || "$who" == "$owner" ]]; then rm -f "$file"; echo "RELEASED $key"; exit 0; fi
    echo "NOT-OWNER $key: khoá của $owner, không gỡ"; exit 1 ;;
  *) sed -n '2,10p' "$0"; exit 2 ;;
esac
