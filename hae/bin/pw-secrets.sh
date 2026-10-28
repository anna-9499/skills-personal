#!/usr/bin/env bash
# Tạo file secrets cho Playwright MCP (--secrets) từ .env của các repo automation.
# Chỉ lấy biến mật khẩu / token / key / OTP — không lấy URL, email (che URL làm hỏng điều hướng).
# Chạy lại mỗi khi .env đổi, rồi mở session Claude mới (server chỉ đọc file lúc khởi động).
# Chỉ in TÊN biến, không in giá trị.
set -euo pipefail

OUT_DIR="$HOME/.hae/secrets"   # để NGOÀI --output-dir của Playwright MCP (~/.hae/playwright) — tool không đọc được
OUT="$OUT_DIR/playwright.env"
SOURCES=(
  "$HOME/Downloads/Auto testing/qikify-QA-mailtro/.env"
  "$HOME/Downloads/Auto testing/shopify-app/.env"
)
PATTERN='^[[:space:]]*(export[[:space:]]+)?[A-Za-z0-9_]*(PASSWORD|PASS|TOKEN|SECRET|API_KEY|PRIVATE_KEY|OTP)[A-Za-z0-9_]*[[:space:]]*='

mkdir -p "$OUT_DIR" "$HOME/.hae/playwright/auth"
chmod 700 "$HOME/.hae" "$OUT_DIR" "$HOME/.hae/playwright" "$HOME/.hae/playwright/auth" 2>/dev/null || true

tmp="$(mktemp "$OUT_DIR/.secrets.XXXXXX")"
chmod 600 "$tmp"
seen_list=""   # bash 3.2 (macOS) không có mảng kết hợp
count=0

for src in "${SOURCES[@]}"; do
  if [[ ! -r "$src" ]]; then
    echo "WARN  không đọc được: $src" >&2
    continue
  fi
  echo "# từ $src" >>"$tmp"
  while IFS= read -r line; do
    name="$(sed -E 's/^[[:space:]]*(export[[:space:]]+)?([A-Za-z0-9_]+).*/\2/' <<<"$line")"
    value="${line#*=}"
    [[ -z "${value//[[:space:]\"\']/}" ]] && { echo "SKIP  $name (rỗng)"; continue; }
    if grep -qx "$name" <<<"$seen_list"; then
      echo "FAIL  trùng tên biến $name giữa hai file .env — đổi tên một bên rồi chạy lại" >&2
      rm -f "$tmp"; exit 1
    fi
    seen_list="$seen_list"$'\n'"$name"; count=$((count+1))
    echo "${line#export }" | sed -E 's/^[[:space:]]+//' >>"$tmp"
    echo "OK    $name"
  done < <(grep -E "$PATTERN" "$src" || true)
done

mv -f "$tmp" "$OUT"
chmod 600 "$OUT"
echo "Đã ghi $OUT ($count biến, quyền 600)."
