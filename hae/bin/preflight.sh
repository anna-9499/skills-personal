#!/usr/bin/env bash
# Pre-flight trước khi Hae giao sonder / ash — kiểm thứ script kiểm được, không mở browser.
#
#   preflight.sh <KEY> [URL staging]
#     KEY: MTRO | QCO | QSC | TEPO | DUOS | QIK …
#     URL: bắt buộc với 4 app Shopify nếu muốn kiểm staging; MTRO tự lấy BASE_URL trong .env.
#
# Mỗi dòng: OK | WARN | FAIL  <mục>  <chi tiết>   (FAIL/WARN có thêm dòng "  FIX: …")
# Exit: 0 = không có FAIL · 1 = có FAIL (Hae không giao) · 2 = sai cú pháp.
# Không in giá trị trong .env (chỉ tên biến). Đăng nhập / captcha / store state: sonder tự kiểm ở bước 0.
set -uo pipefail

key="$(printf '%s' "${1:-}" | tr '[:lower:]' '[:upper:]')"; url="${2:-}"
[[ -z "$key" ]] && { sed -n '2,10p' "$0"; exit 2; }

AUTO="$HOME/Downloads/Auto testing"
if [[ "$key" == "MTRO" ]]; then repo="$AUTO/qikify-QA-mailtro"; else repo="$AUTO/shopify-app"; fi
LOCK="$(dirname "$0")/staging-lock.sh"
fails=0
ok()   { echo "OK    $1  $2"; }
warn() { echo "WARN  $1  $2"; [[ -n "${3:-}" ]] && echo "  FIX: $3"; }
fail() { echo "FAIL  $1  $2"; [[ -n "${3:-}" ]] && echo "  FIX: $3"; fails=$((fails+1)); }
envval() { sed -n "s/^$1=//p" "$repo/.env" 2>/dev/null | tail -1 | tr -d '"'"'"; }

# 1. Quyền đọc ~/Downloads (macOS hay thu hồi với Nodeterm / tmux)
if ls "$repo" >/dev/null 2>&1 && [[ -r "$repo/.env" ]] && head -c1 "$repo/.env" >/dev/null 2>&1; then
  ok "downloads" "đọc được $repo + .env"
elif [[ -d "$repo" ]]; then
  fail "downloads" "không đọc được $repo hoặc .env (Operation not permitted?)" \
       "System Settings → Privacy & Security → Full Disk Access: bật cho Nodeterm / Terminal, rồi chạy 'tmux kill-server' và mở lại session"
else
  fail "downloads" "không thấy repo $repo" "kiểm đường dẫn repo automation"
fi

# 2. ENV phải là staging (MTRO)
if [[ "$key" == "MTRO" ]]; then
  e="$(envval ENV)"
  if [[ "$e" == "staging" ]]; then ok "env" "ENV=staging"
  else fail "env" "ENV trong .env không phải staging" "sửa ENV=staging trong .env repo qikify-QA-mailtro"; fi
  [[ -z "$url" ]] && url="$(envval BASE_URL)"
fi

# 3. MCP server
mcp="$(perl -e 'alarm 60; exec @ARGV' claude mcp list 2>&1 || true)"   # macOS không có `timeout`
chk_mcp() { # tên-hiển-thị  pattern  mức-khi-hỏng(fail|warn)  fix
  local line; line="$(printf '%s\n' "$mcp" | grep -E "^$2[: ]" | head -1)"
  if [[ "$line" == *"Connected"* ]]; then ok "mcp:$1" "Connected"
  elif [[ "$3" == fail ]]; then fail "mcp:$1" "${line:-không có trong mcp list}" "$4"
  else warn "mcp:$1" "${line:-không có trong mcp list}" "$4"; fi
}
if [[ -z "$mcp" ]]; then
  warn "mcp" "không chạy được 'claude mcp list'" "chạy /mcp trong session để xem"
else
  chk_mcp testlane   "testlane"          fail "/mcp → testlane: đăng nhập lại (token QA Hub ở /settings/ai)"
  chk_mcp playwright "playwright"        fail "/mcp → playwright: reconnect; hoặc 'npx @playwright/mcp@latest' lỗi mạng"
  chk_mcp chrome     "chrome"            warn "chỉ cần khi dùng Chrome bridge — Hae gọi thêm chrome_status"
  chk_mcp atlassian  "atlassian"         warn "/mcp → atlassian: authenticate lại"
  chk_mcp slack      "plugin:slack:slack" warn "claude.ai → Settings → Connectors → Slack, hoặc /mcp"
fi

# 4. Staging trả lời
if [[ -n "$url" ]]; then
  host="$(printf '%s' "$url" | sed -E 's#^https?://([^/]+).*#\1#')"
  code="$(curl -s -o /dev/null -m 15 -w '%{http_code}' -L --max-redirs 3 "$url" 2>/dev/null || echo 000)"
  case "$code" in
    2*|3*|401|403) ok "staging" "$host → HTTP $code" ;;
    429) warn "staging" "$host → HTTP 429 (rate limit)" "chờ vài phút rồi chạy" ;;
    000) fail "staging" "$host không trả lời (DNS / mạng / VPN)" "kiểm mạng, VPN, URL staging" ;;
    *)   fail "staging" "$host → HTTP $code" "staging đang lỗi — báo Dev / Infra" ;;
  esac
else
  warn "staging" "không có URL để kiểm" "4 app Shopify: truyền URL staging làm tham số thứ 2"
fi

# 5. Khoá staging
if [[ -x "$LOCK" ]]; then
  st="$("$LOCK" status "$key" 2>&1)"; rc=$?
  if (( rc == 0 )); then ok "lock" "$st"; else warn "lock" "$st" "việc của session này → xếp hàng; người khác → câu 11"; fi
fi

# 6. Git repo automation
if git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
  br="$(git -C "$repo" branch --show-current 2>/dev/null)"
  dirty="$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  if [[ "$dirty" == 0 ]]; then ok "git" "$(basename "$repo") sạch · branch $br"
  else warn "git" "$(basename "$repo") có $dirty file chưa commit · branch $br" "log/evidence sonder sẽ lẫn vào thay đổi đang dở — commit hoặc stash nếu cần"; fi
fi

echo "---"
if (( fails > 0 )); then echo "PREFLIGHT: $fails FAIL — không giao"; exit 1; fi
echo "PREFLIGHT: OK"; exit 0
