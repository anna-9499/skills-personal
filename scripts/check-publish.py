#!/usr/bin/env python3
"""Kiểm publish.json của các skill port sang Worker: mọi khoá phải khớp đúng 1 lần trong SKILL.md.

  python3 scripts/check-publish.py            # kiểm bản đang staged (dùng trong pre-commit)
  python3 scripts/check-publish.py --worktree # kiểm file trên đĩa

Exit 1 nếu có khoá trỏ trượt (0 lần) hoặc mơ hồ (≥ 2 lần) — bản Worker sẽ âm thầm sai.
"""
import json, subprocess, sys, os

SKILLS = ["qa-requirement-analysis", "gen-testcase", "update-business-rules"]
LIST_KEYS = ["dropSections", "dropParagraphs"]
MAP_KEYS = ["sectionNotes", "replaceSections", "replaceParagraphs"]

root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                      cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip()
worktree = "--worktree" in sys.argv[1:]

def read(path):
    if worktree:
        with open(os.path.join(root, path), encoding="utf-8") as f:
            return f.read()
    r = subprocess.run(["git", "show", f":{path}"], capture_output=True, cwd=root)
    if r.returncode != 0:
        raise FileNotFoundError(path)
    return r.stdout.decode("utf-8")

failed = False
for skill in SKILLS:
    try:
        cfg = json.loads(read(f"skills/{skill}/publish.json"))
        md = read(f"skills/{skill}/SKILL.md")
    except FileNotFoundError as e:
        print(f"FAIL {skill}: không đọc được {e}")
        failed = True
        continue
    except json.JSONDecodeError as e:
        print(f"FAIL {skill}: publish.json không phải JSON hợp lệ ({e})")
        failed = True
        continue
    keys = [(f, k) for f in LIST_KEYS for k in cfg.get(f, [])]
    keys += [(f, k) for f in MAP_KEYS for k in cfg.get(f, {})]
    lines = [l.rstrip() for l in md.splitlines()]

    def hits(k):
        # Khoá là tiêu đề → phải khớp NGUYÊN dòng (thêm chữ vào cuối tiêu đề cũng là trỏ trượt);
        # khoá là đoạn văn → khớp chuỗi con.
        return lines.count(k.rstrip()) if k.lstrip().startswith("#") else md.count(k)

    bad = [f"{f}: [{hits(k)}x] {k[:70]}" for f, k in keys if hits(k) != 1]
    print(("FAIL " if bad else "OK   ") + skill)
    for b in bad:
        print("      ", b)
    failed |= bool(bad)

if failed:
    print("\npublish.json trỏ trượt → sửa khoá cho khớp tiêu đề / đoạn trong SKILL.md "
          "(bỏ qua khẩn cấp: git commit --no-verify).")
sys.exit(1 if failed else 0)
