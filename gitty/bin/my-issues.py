#!/usr/bin/env python3
"""Gitty — tình trạng các issue chị tạo trong một repo (mặc định ownego/support-hub). Chỉ đọc.

  python3 my-issues.py                       # ownego/support-hub, issue đóng trong 7 ngày qua
  python3 my-issues.py -R owner/repo --days 14
  python3 my-issues.py --json
"""
import json, subprocess, sys, datetime as dt

args = sys.argv[1:]
repo = args[args.index("-R") + 1] if "-R" in args else "ownego/support-hub"
days = int(args[args.index("--days") + 1]) if "--days" in args else 7
as_json = "--json" in args

def gh(*a):
    r = subprocess.run(["gh", *a], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"gh lỗi: {r.stderr.strip()}")
    return json.loads(r.stdout)

me = gh("api", "user")["login"]
issues = gh("issue", "list", "-R", repo, "--author", me, "--state", "all", "--limit", "500", "--json",
            "number,title,url,state,stateReason,createdAt,closedAt,updatedAt,assignees,labels,"
            "closedByPullRequestsReferences")
now = dt.datetime.now(dt.timezone.utc)
ts = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
cutoff = now - dt.timedelta(days=days)

def row(i):
    prs = [f"#{p['number']}" for p in i.get("closedByPullRequestsReferences") or []]
    return {
        "number": i["number"], "title": i["title"], "url": i["url"], "state": i["state"],
        "reason": (i.get("stateReason") or "").lower() or None,
        "assignees": [a["login"] for a in i["assignees"]], "labels": [l["name"] for l in i["labels"]],
        "linked_prs": prs, "created": i["createdAt"][:10], "closed": (i["closedAt"] or "")[:10] or None,
        "idle_days": (now - ts(i["updatedAt"])).days,
    }

open_ = sorted([row(i) for i in issues if i["state"] == "OPEN"], key=lambda r: -r["idle_days"])
closed_recent = sorted([row(i) for i in issues if i["state"] == "CLOSED" and ts(i["closedAt"]) >= cutoff],
                       key=lambda r: r["closed"], reverse=True)
total_closed = sum(1 for i in issues if i["state"] == "CLOSED")

if as_json:
    print(json.dumps({"repo": repo, "author": me, "open": open_, "closed_recent": closed_recent,
                      "total_open": len(open_), "total_closed": total_closed, "days": days},
                     ensure_ascii=False, indent=1))
    sys.exit()

print(f"{repo} — issue @{me} tạo: {len(open_)} open · {total_closed} closed\n")
print(f"OPEN ({len(open_)}) — xếp theo lâu chưa cập nhật nhất")
for r in open_:
    who = ", ".join("@" + a for a in r["assignees"]) or "chưa assign"
    pr = f" · PR {' '.join(r['linked_prs'])}" if r["linked_prs"] else ""
    print(f"  #{r['number']:<5} {r['title'][:80]}\n         {who} · {r['idle_days']} ngày chưa cập nhật{pr}")
print(f"\nCLOSED trong {days} ngày qua ({len(closed_recent)})")
for r in closed_recent:
    flag = "  ⚠ not planned" if r["reason"] == "not_planned" else ("  ⚠ không có PR liên kết" if not r["linked_prs"] else "")
    pr = f" · PR {' '.join(r['linked_prs'])}" if r["linked_prs"] else ""
    print(f"  #{r['number']:<5} {r['title'][:80]}\n         đóng {r['closed']}{pr}{flag}")
