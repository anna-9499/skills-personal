#!/usr/bin/env python3
"""Công cụ máy cho skill context-change-request (0 token, chỉ stdlib).

  ccr.py lint <CCR.md> [--en <CCR.en.md>] [--final]
      Kiểm file CCR giữ ĐÚNG khung template.md (chỉ chữ trong <<< >>> được thay):
      dòng khung không bị sửa/xoá, không còn placeholder, cột "Độ tin cậy" đúng 1 trong 3 dạng.
      --en: kiểm thêm bản Anh với template.en.md + khớp từng dòng với bản Việt.
      --final: còn "⏳" (câu chờ chị trả lời) cũng tính là lỗi — dùng trước khi đính kèm QA Hub.
      Exit 0 = ✅, 1 = lệch (in đúng dòng lệch).

  ccr.py open --key <KEY> [--rules]
      Liệt kê CCR đang mở (PENDING / ATTACHED) của app trong knowledge-work/apps/<KEY>/ccr/.
      --rules: in JSON {BR-nn: [file CCR…]} — rule đang "tranh chấp".

  ccr.py find --tickets <K1,K2> [--key <KEY>]
      Chống trùng: exit 2 nếu đã có CCR đang mở cho một trong các ticket (in đường dẫn).

  ccr.py hub-copy <CCR.en.md|CCR.md> --out <file>
      Sinh bản gửi QA Hub. QA Hub từ chối Submit khi còn chuỗi '<<<', mà 2 dòng KHUNG của template
      (dòng 9 và dòng checklist cuối) có sẵn chữ `<<< ... >>>`. Chỉ 2 dòng đó được đổi `<<< ... >>>`
      → `‹‹‹ ... ›››`; mọi dòng khác giữ nguyên. Sau đó kiểm không còn '<<<'.

  ccr.py status <CCR.md> [--set PENDING|ATTACHED|SUBMITTED|DROPPED] [--urgency HIGH|MEDIUM|LOW]
                [--note ...] [--task <taskId>] [--reason ...]
      Đọc / sửa file trạng thái CCR-….status.json cạnh file CCR.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
APPS = os.path.realpath(os.path.join(SKILL, "..", "qa-requirement-analysis", "references", "apps"))
if not os.path.isdir(APPS):
    APPS = os.path.expanduser("~/Downloads/AI Agent/skills-personal/knowledge-work/apps")

PH = re.compile(r"`?<<<.*?>>>`?")
GUIDE_PREFIX = ("> Nếu knowledge base đích", "> If the target knowledge base")
LITERAL_PH = "`<<< ... >>>`"  # chữ có sẵn trong 2 dòng khung — không phải placeholder
TRUST = {
    "vi": [r"ĐỦ TIN CẬY \(test case PASS #.+\)", r'ĐỦ TIN CẬY \(PO/Dev confirm: ".+" — .+\)', r"CHƯA ĐỦ — cần re-explore"],
    "en": [r"TRUSTED \(test case PASS #.+\)", r'TRUSTED \(PO/Dev confirm: ".+" — .+\)', r"NOT ENOUGH — needs re-explore"],
}
STATUSES = ("PENDING", "ATTACHED", "SUBMITTED", "DROPPED")
OPEN = ("PENDING", "ATTACHED")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read().split("\n")


def items_of(tpl):
    """Template → danh sách item: ('lit', line) · ('ph', regex, line) · ('free',) · ('row', regex, line)."""
    out, i = [], 0
    while i < len(tpl):
        ln = tpl[i]
        if ln.startswith(GUIDE_PREFIX):
            out.append(("guide", ln)); i += 1; continue
        if ln.strip() == "```":
            j = i + 1
            while j < len(tpl) and tpl[j].strip() != "```":
                j += 1
            body = tpl[i + 1:j]
            if any("<<<" in b for b in body):
                out.append(("free", "```")); i = j + 1; continue
        if "<<<" in ln and LITERAL_PH not in ln:
            parts = PH.split(ln)
            rx = "^" + "(.*?)".join(re.escape(p) for p in parts) + "$"
            kind = "row" if ln.startswith("| `<<<") else "ph"
            out.append((kind, re.compile(rx), ln)); i += 1; continue
        out.append(("lit", ln)); i += 1
    return out


def norm_blank(lines):
    """Gộp dòng trống liên tiếp (xoá dòng hướng dẫn đầu file để lại 2 dòng trống)."""
    out, prev = [], None
    for idx, ln in enumerate(lines):
        if ln.strip() == "" and prev == "":
            continue
        out.append((idx + 1, ln)); prev = ln.strip()
    return out


def match(ccr_path, tpl_path, lang):
    """Trả (errors, spans) — spans = số dòng CCR ứng với từng item, để so khớp Việt/Anh."""
    errs, spans = [], []
    items = items_of([l for l in read(tpl_path)])
    lines = norm_blank(read(ccr_path))
    # dòng hướng dẫn: phải xoá; dòng trống thừa đi kèm đã gộp
    k = 0

    def cur():
        return lines[k] if k < len(lines) else (None, None)

    for it in items:
        kind = it[0]
        no, ln = cur()
        if kind == "guide":
            if ln is not None and ln.startswith(GUIDE_PREFIX):
                errs.append(f"dòng {no}: chưa xoá dòng hướng dẫn đầu file (template dặn xoá)")
                k += 1
            # nếu đã xoá thì dòng trống sau nó bị gộp — bỏ qua dòng trống kế tiếp của template
            spans.append(0); continue
        if ln is None:
            errs.append(f"hết file khi còn chờ dòng khung: {it[-1][:80]!r}"); break
        if kind == "lit":
            if it[1].strip() == "" and ln.strip() == "":
                k += 1; spans.append(1); continue
            if it[1].strip() == "" and ln.strip() != "":
                # template có dòng trống mà CCR không có: chỉ chấp nhận khi vừa xoá dòng hướng dẫn
                spans.append(0); continue
            want = it[1]
            if ln == want or (want.startswith("- [ ]") and ln == "- [x]" + want[5:]):
                k += 1; spans.append(1); continue
            errs.append(f"dòng {no}: dòng khung bị sửa/xoá.\n    cần : {want[:160]}\n    thấy: {ln[:160]}")
            # thử đồng bộ lại: tìm dòng khung ở phía trước
            for look in range(k + 1, min(k + 40, len(lines))):
                if lines[look][1] == want:
                    k = look + 1; break
            else:
                k += 1  # coi dòng này là bản sửa của dòng khung, đi tiếp
            spans.append(1); continue
        if kind == "ph":
            if it[1].match(ln) and "<<<" not in ln:
                k += 1; spans.append(1); continue
            if "<<<" in ln:
                errs.append(f"dòng {no}: còn placeholder chưa điền: {ln[:160]}")
            else:
                errs.append(f"dòng {no}: phần ngoài <<< >>> bị sửa.\n    khung: {it[2][:160]}\n    thấy : {ln[:160]}")
            k += 1; spans.append(1); continue
        if kind == "free":
            if ln.strip() != "```":
                errs.append(f"dòng {no}: thiếu ``` mở khối điền tự do"); spans.append(0); continue
            j = k + 1
            while j < len(lines) and lines[j][1].strip() != "```":
                if "<<<" in lines[j][1]:
                    errs.append(f"dòng {lines[j][0]}: còn placeholder chưa điền trong khối ```")
                j += 1
            if j - k - 1 == 0:
                errs.append(f"dòng {no}: khối ``` để trống")
            spans.append(j - k + 1); k = j + 1; continue
        if kind == "row":
            n = 0
            while k < len(lines) and lines[k][1].startswith("|"):
                rno, row = lines[k]
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if "<<<" in row:
                    errs.append(f"dòng {rno}: hàng bảng còn placeholder")
                elif len(cells) != 5:
                    errs.append(f"dòng {rno}: hàng bảng re-explore phải đúng 5 cột (thấy {len(cells)})")
                else:
                    t = cells[4].strip("`").strip()
                    if not any(re.fullmatch(p, t) for p in TRUST[lang]):
                        errs.append(f"dòng {rno}: cột Độ tin cậy sai dạng (chỉ 1 trong 3 dạng, không thêm chữ): {t[:120]}")
                n += 1; k += 1
            if n == 0:
                errs.append(f"dòng {no}: bảng 'Phạm vi cần re-explore' không có hàng nào")
            spans.append(n); continue
    if k < len(lines):
        rest = [l for _, l in lines[k:] if l.strip()]
        if rest:
            errs.append(f"dòng {lines[k][0]}+: có nội dung thừa sau checklist cuối")
    return errs, spans


def cmd_lint(a):
    tpl_vi = os.path.join(SKILL, "template.md")
    tpl_en = os.path.join(SKILL, "template.en.md")
    errs, sp_vi = match(a.file, tpl_vi, "vi")
    files = [a.file]
    if a.en:
        e2, sp_en = match(a.en, tpl_en, "en")
        errs += [f"[EN] {e}" for e in e2]
        files.append(a.en)
        if not e2 and not [e for e in errs if not e.startswith("[EN]")] and sp_vi != sp_en:
            for idx, (x, y) in enumerate(zip(sp_vi, sp_en)):
                if x != y:
                    errs.append(f"[EN] bản Anh lệch dòng với bản Việt ở mục thứ {idx + 1} ({x} dòng ≠ {y} dòng)")
                    break
    waits = []
    for f in files:
        for i, l in enumerate(read(f), 1):
            if "⏳" in l:
                waits.append(f"{os.path.basename(f)}:{i}: {l.strip()[:140]}")
    if a.final and waits:
        errs += [f"còn câu chờ trả lời — {w}" for w in waits]
    if errs:
        print("❌ CCR lệch template:")
        for e in errs:
            print("  - " + e)
        sys.exit(1)
    print("✅ Khớp template" + (" (Việt + Anh)" if a.en else "") + f" · {len(waits)} chỗ ⏳ chờ trả lời")
    for w in waits:
        print("  ⏳ " + w)


def status_path(ccr):
    base = re.sub(r"(\.en)?\.md$", "", ccr)
    return base + ".status.json"


def load_status(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def all_status(key=None):
    pat = os.path.join(APPS, key or "*", "ccr", "*.status.json")
    for p in sorted(glob.glob(pat)):
        s = load_status(p)
        if s:
            yield p, s


def cmd_open(a):
    rows = [(p, s) for p, s in all_status(a.key) if s.get("status") in OPEN]
    if a.rules:
        m = {}
        for p, s in rows:
            for r in s.get("rules", []):
                m.setdefault(r, []).append(os.path.basename(p).replace(".status.json", ".md"))
        print(json.dumps(m, ensure_ascii=False, indent=1)); return
    if not rows:
        print("Không có CCR đang mở" + (f" cho {a.key}" if a.key else "")); return
    for p, s in rows:
        print(f"{s.get('status'):9} {s.get('urgency') or '-':6} task={s.get('taskId') or '-':10} "
              f"tickets={','.join(s.get('tickets', []))}  {p.replace('.status.json', '.md')}")


def cmd_find(a):
    want = {t.strip().upper() for t in a.tickets.split(",") if t.strip()}
    hit = [(p, s) for p, s in all_status(a.key) if s.get("status") in OPEN and want & {t.upper() for t in s.get("tickets", [])}]
    for p, s in hit:
        print(f"ĐÃ CÓ CCR {s['status']}: {p.replace('.status.json', '.md')} (tickets {','.join(s.get('tickets', []))})")
    sys.exit(2 if hit else 0)


def cmd_hub_copy(a):
    out = []
    for ln in read(a.file):
        if LITERAL_PH in ln and ("placeholder" in ln):
            ln = ln.replace(LITERAL_PH, "`‹‹‹ ... ›››`")
        out.append(ln)
    text = "\n".join(out)
    if "<<<" in text:
        bad = [i for i, l in enumerate(out, 1) if "<<<" in l]
        print(f"❌ Còn '<<<' ở dòng {bad} — QA Hub sẽ từ chối Submit."); sys.exit(1)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✅ Bản gửi QA Hub: {a.out} ({len(text)} ký tự)")


def cmd_status(a):
    p = status_path(a.file)
    s = load_status(p)
    if s is None:
        print(f"Chưa có file trạng thái: {p}"); sys.exit(1)
    changed = False
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    if a.set:
        if s.get("status") == "SUBMITTED" and a.set != "SUBMITTED":
            print("CCR đã SUBMITTED — không đổi trạng thái được."); sys.exit(1)
        s["status"] = a.set; s[a.set.lower() + "_at"] = now; changed = True
    if a.urgency:
        s["urgency"] = a.urgency; changed = True
    if a.note:
        s["note"] = a.note; changed = True
    if a.task:
        s["taskId"] = a.task; changed = True
    if a.reason:
        s["drop_reason"] = a.reason; changed = True
    if changed:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1); f.write("\n")
    print(json.dumps(s, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lint"); p.add_argument("file"); p.add_argument("--en"); p.add_argument("--final", action="store_true"); p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("open"); p.add_argument("--key"); p.add_argument("--rules", action="store_true"); p.set_defaults(fn=cmd_open)
    p = sub.add_parser("find"); p.add_argument("--tickets", required=True); p.add_argument("--key"); p.set_defaults(fn=cmd_find)
    p = sub.add_parser("hub-copy"); p.add_argument("file"); p.add_argument("--out", required=True); p.set_defaults(fn=cmd_hub_copy)
    p = sub.add_parser("status"); p.add_argument("file"); p.add_argument("--set", choices=STATUSES)
    p.add_argument("--urgency", choices=("HIGH", "MEDIUM", "LOW")); p.add_argument("--note"); p.add_argument("--task"); p.add_argument("--reason")
    p.set_defaults(fn=cmd_status)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
