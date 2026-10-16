#!/usr/bin/env bash
# Nối repo này vào Claude Code. Chạy lại bao nhiêu lần cũng được (idempotent).
#
#   bash install.sh
#
# Làm: symlink mọi skills/*/ → ~/.claude/skills/, hae/*.md → ~/.claude/agents/Hae/,
#      luke/*.md (trừ profiles.*) → ~/.claude/agents/Luke/, bật pre-commit hook.
# KHÔNG làm (chị tự chạy, vì sửa settings.json): bash hae/hooks/apply-settings.sh
# Chỉ chạy trên macOS / Linux (dựa trên symlink).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
REPO="$PWD"
EXPECTED="$HOME/Downloads/AI Agent/skills-personal"

need() { command -v "$1" >/dev/null || { echo "THIẾU: $1"; missing=1; }; }
missing=0; need git; need python3; need jq; need curl
[ "$missing" = 0 ] || { echo "Cài các công cụ trên rồi chạy lại."; exit 1; }

# Submodule: thiếu thì references/ chết im lặng
if [ -z "$(ls -A knowledge-work 2>/dev/null)" ]; then
  echo "knowledge-work/ rỗng → git submodule update --init"
  git submodule update --init
fi

link() {  # link <nguồn> <đích>; báo khi đích là file thật (không ghi đè)
  if [ -e "$2" ] && [ ! -L "$2" ]; then echo "BỎ QUA (file thật, không phải symlink): $2"; return; fi
  ln -sfn "$1" "$2"; echo "  $2"
}

mkdir -p ~/.claude/skills ~/.claude/agents/Hae ~/.claude/agents/Luke
echo "Skill:"
for d in skills/*/; do link "$REPO/${d%/}" ~/.claude/skills/"$(basename "$d")"; done
echo "Agent Hae:"
for f in hae/*.md; do link "$REPO/$f" ~/.claude/agents/Hae/"$(basename "$f")"; done
echo "Agent Luke:"
# qa-automation.template.md không phải agent nhưng luke.md đọc nó qua đường dẫn này; profiles.* chỉ là bản lưu
for f in luke/*.md; do
  case "$(basename "$f")" in profiles.*) continue ;; esac
  link "$REPO/$f" ~/.claude/agents/Luke/"$(basename "$f")"
done

# Symlink chết (skill / agent đã xoá khỏi repo)
for l in ~/.claude/skills/* ~/.claude/agents/Hae/* ~/.claude/agents/Luke/*; do
  [ -L "$l" ] && [ ! -e "$l" ] && case "$(readlink "$l")" in "$REPO"/*) rm "$l"; echo "Gỡ symlink chết: $l" ;; esac
done

git config core.hooksPath .githooks && echo "Pre-commit hook: bật"

echo
if [ "$REPO" != "$EXPECTED" ]; then
  echo "CHÚ Ý: repo đang ở $REPO, nhưng hae.md, hae/hooks/settings-patch.jq gọi script theo"
  echo "       $EXPECTED — sửa các đường dẫn đó hoặc chuyển repo về đúng chỗ."
fi
grep -q '"agent"' ~/.claude/settings.json 2>/dev/null || echo 'Chưa đặt Hae mặc định: thêm { "agent": "hae" } vào ~/.claude/settings.json'
grep -q 'env-guard' ~/.claude/settings.json 2>/dev/null || echo "Chưa cài env-guard: bash hae/hooks/apply-settings.sh"
echo "Xong. Mở session Claude Code mới để nạp skill / agent."
