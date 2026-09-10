#!/usr/bin/env python3
"""Rút gọn task Testlane của chính mình xuống mức đọc được trong một màn hình.

VÌ SAO CÓ FILE NÀY
MCP tool `list_tasks` trả về cả field `notes` — nguyên bản phân tích requirement,
có task nặng hơn 10K token. Gọi cho 8 project là vỡ context của session. Script
gọi thẳng endpoint MCP qua HTTP rồi vứt `notes` đi trước khi in, nên output chỉ
còn vài KB.

VÌ SAO DÙNG curl CHỨ KHÔNG PHẢI urllib
QA Hub đứng sau Cloudflare. urllib bị chặn bằng error 1010
(`browser_signature_banned`) — CF chặn theo TLS fingerprint, không phải theo
User-Agent, nên đổi UA không cứu được. curl thì qua. ĐỪNG đổi lại sang urllib
hay requests nếu chưa kiểm chứng lại chỗ này.

Token đọc từ ~/.claude.json (nơi Claude Code đã lưu) — KHÔNG hardcode, KHÔNG in ra.

Dùng:  python3 testlane-digest.py [--json] [--all-assignees]
"""
import json, os, sys, subprocess, datetime

CFG = os.path.expanduser("~/.claude.json")
ACTIVE = ("todo", "in-progress", "waiting-for-dev", "ready-to-deploy")


def rpc(url, token, tool, args=None):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                          "params": {"name": tool, "arguments": args or {}}})
    p = subprocess.run(
        ["curl", "-sS", "--fail-with-body", "-X", "POST", url,
         "-H", f"Authorization: {token}",
         "-H", "Content-Type: application/json",
         "-H", "Accept: application/json, text/event-stream",
         "--data-binary", "@-"],
        input=payload, capture_output=True, text=True, timeout=90)
    if p.returncode != 0:
        raise SystemExit(f"Gọi Testlane thất bại ({tool}): {p.stderr.strip() or p.stdout[:300]}")
    body = json.loads(p.stdout)
    if "error" in body:
        raise SystemExit(f"Testlane trả lỗi khi gọi {tool}: {body['error']}")
    return json.loads(body["result"]["content"][0]["text"])


def cases(tc):
    """caseCounts.byStatus = {status: {priority: n}} -> {status: tổng}"""
    return {st: sum(by.values()) for st, by in (tc.get("byStatus") or {}).items()}


def main():
    as_json = "--json" in sys.argv
    mine_only = "--all-assignees" not in sys.argv

    try:
        cfg = json.load(open(CFG))["mcpServers"]["testlane"]
        url, token = cfg["url"], cfg["headers"]["Authorization"]
    except (OSError, KeyError):
        raise SystemExit(f"Không tìm thấy cấu hình MCP 'testlane' trong {CFG}. "
                         "Chạy /mcp trong Claude Code để kiểm tra.")

    me = rpc(url, token, "whoami")
    projects = [p for p in rpc(url, token, "list_projects") if p.get("isMember")]

    now = datetime.datetime.now(datetime.timezone.utc)
    out = []
    for p in projects:
        for t in rpc(url, token, "list_tasks", {"projectId": p["id"]}):
            if t.get("status") not in ACTIVE:
                continue
            if mine_only and t.get("assigneeId") != me["id"]:
                continue
            upd = t.get("updatedAt") or t.get("createdAt")
            age = None
            if upd:
                age = (now - datetime.datetime.fromisoformat(
                    upd.replace("Z", "+00:00"))).days
            out.append({
                "project": p["key"], "id": t["id"],
                "title": (t.get("description") or "").strip(),
                "status": t.get("status"), "priority": t.get("priority"),
                "jiraKey": t.get("jiraKey"), "tags": t.get("tags") or [],
                "daysSinceUpdate": age,
                "cases": cases(t.get("caseCounts") or {}),
                "casesWithBugs": (t.get("caseCounts") or {}).get("withBugs", 0),
            })

    out.sort(key=lambda r: (-(r["daysSinceUpdate"] or 0), r["project"]))
    result = {"user": me["name"], "generatedAt": now.isoformat(timespec="seconds"),
              "projectsChecked": [p["key"] for p in projects],
              "activeTaskCount": len(out), "tasks": out}

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return

    print(f"# Task đang mở của {result['user']}  ({len(out)} task)")
    print(f"Project đã quét: {', '.join(result['projectsChecked'])}\n")
    if not out:
        print("Không có task nào đang mở."); return
    print("| Project | ID | Task | Status | Prio | Chưa đụng | Case | Bug |")
    print("|---|---|---|---|---|---|---|---|")
    for r in out:
        cs = ", ".join(f"{k}:{v}" for k, v in sorted(r["cases"].items())) or "—"
        title = r["title"][:58] + ("…" if len(r["title"]) > 58 else "")
        d = f"{r['daysSinceUpdate']}n" if r["daysSinceUpdate"] is not None else "—"
        print(f"| {r['project']} | {r['id']} | {title} | {r['status']} | "
              f"{r['priority']} | {d} | {cs} | {r['casesWithBugs'] or '—'} |")


if __name__ == "__main__":
    main()
