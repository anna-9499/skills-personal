#!/usr/bin/env bash
# Sinh sonder2.md từ sonder.md: bản sao dùng server Playwright thứ hai (playwright2) để Hae chạy 2 lô song song
# trên 2 store khác nhau. Sửa sonder.md thì chạy lại script này. (16/11/2026)
set -eu
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sed -e 's/^name: sonder$/name: sonder2/' \
    -e 's/mcp__playwright__/mcp__playwright2__/g' \
    "$DIR/sonder.md" > "$DIR/sonder2.md"
# Ghi chú cho sub-agent ngay sau frontmatter
awk 'BEGIN{n=0} {print} /^---$/{n++; if(n==2){print ""; print "> **sonder2** = sonder chạy trên server Playwright thứ hai (`mcp__playwright2__*`, Chromium riêng). Mọi quy tắc của sonder giữ nguyên. Không dùng `mcp__playwright__*` (server đó của sonder chạy song song)."}}' "$DIR/sonder2.md" > "$DIR/sonder2.md.tmp" && mv "$DIR/sonder2.md.tmp" "$DIR/sonder2.md"
