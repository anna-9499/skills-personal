#!/usr/bin/env python3
"""Gitty inbox — liệt kê việc GitHub đang chờ chị (mention / review request / assign).

  python3 inbox.py            # bảng gọn, chỉ việc còn chờ
  python3 inbox.py --json     # JSON cho Gitty đọc
  python3 inbox.py --all      # cả việc đã trả lời rồi (để đối chiếu)
  python3 inbox.py --days 30  # cửa sổ thời gian (mặc định 14 ngày)

"Còn chờ" =
  - mention: có comment nhắc @<login> MỚI HƠN hoạt động cuối của chị (comment / review) trên issue/PR đó
  - review:  PR đang requested review chị, chị chưa review sau lần request
  - assign:  issue/PR open giao cho chị mà chị chưa có comment nào sau lần cập nhật cuối của người khác
Chỉ đọc. Không đánh dấu notification, không comment.
"""
import json, subprocess, sys, datetime as dt

def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"gh {' '.join(args)}\n{r.stderr}")
        return None
    return json.loads(r.stdout) if r.stdout.strip() else None

def paged(path):
    out = gh("api", "--paginate", "--slurp", path) or []
    return [x for page in out for x in page]

args = sys.argv[1:]
as_json, show_all = "--json" in args, "--all" in args
days = int(args[args.index("--days") + 1]) if "--days" in args else 14
since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%d")
me = gh("api", "user")["login"]
tag = f"@{me}".lower()

fields = "repository,number,title,url,updatedAt,isPullRequest,author"
items = {}
def collect(kind, res):
    for it in res or []:
        key = it["url"]
        e = items.setdefault(key, {**it, "repo": it["repository"]["nameWithOwner"], "kinds": set()})
        e["kinds"].add(kind)

collect("mention", gh("search", "issues", "--include-prs", f"--mentions={me}", "--state=open",
                      f"--updated=>={since}", "--json", fields, "--limit", "100"))
collect("review", gh("search", "prs", f"--review-requested={me}", "--state=open",
                     "--json", fields.replace(",isPullRequest", ""), "--limit", "100"))
collect("assign", gh("search", "issues", "--include-prs", f"--assignee={me}", "--state=open",
                     f"--updated=>={since}", "--json", fields, "--limit", "100"))

rows = []
for e in items.values():
    repo, n = e["repo"], e["number"]
    is_pr = e.get("isPullRequest", "review" in e["kinds"])
    comments = paged(f"repos/{repo}/issues/{n}/comments?per_page=100")
    if is_pr:
        comments += paged(f"repos/{repo}/pulls/{n}/comments?per_page=100")
        reviews = paged(f"repos/{repo}/pulls/{n}/reviews?per_page=100")
    else:
        reviews = []
    for c in comments:
        c["_t"] = c.get("created_at")
    my_times = [c["_t"] for c in comments if c["user"]["login"] == me] + \
               [r["submitted_at"] for r in reviews if r["user"]["login"] == me and r.get("submitted_at")]
    my_last = max(my_times) if my_times else ""
    mentions = [c for c in comments if c["user"]["login"] != me and tag in (c.get("body") or "").lower()]
    # mention trong body issue/PR (không phải comment)
    body = gh("api", f"repos/{repo}/issues/{n}") or {}
    if tag in (body.get("body") or "").lower() and body.get("user", {}).get("login") != me:
        mentions.append({"_t": body["created_at"], "user": body["user"], "body": body["body"],
                         "html_url": body["html_url"]})
    mentions.sort(key=lambda c: c["_t"])
    pending_mentions = [c for c in mentions if c["_t"] > my_last]
    others = [c for c in comments if c["user"]["login"] != me]
    last_other = max([c["_t"] for c in others], default=body.get("created_at", ""))

    reasons = []
    if pending_mentions:
        reasons.append("mention")
    if "review" in e["kinds"]:  # GitHub tự gỡ review request khi chị đã review → còn trong search = còn chờ
        reasons.append("review")
    if "assign" in e["kinds"] and last_other > my_last:
        reasons.append("assign")
    if not reasons and not show_all:
        continue
    last = pending_mentions[-1] if pending_mentions else None
    rows.append({
        "repo": repo, "number": n, "type": "PR" if is_pr else "issue", "title": e["title"],
        "url": e["url"], "reasons": reasons or ["done"],
        "from": last["user"]["login"] if last else e["author"]["login"],
        "at": last["_t"] if last else e["updatedAt"],
        "comment_url": last.get("html_url") if last else e["url"],
        "ask": (last.get("body") or "").strip() if last else "",
        "pending_mentions": len(pending_mentions),
        "my_last_activity": my_last or None,
    })

rows.sort(key=lambda r: r["at"], reverse=True)
if as_json:
    print(json.dumps({"login": me, "since": since, "items": rows}, ensure_ascii=False, indent=1))
else:
    if not rows:
        print(f"Không có việc nào đang chờ @{me} (từ {since}).")
    for i, r in enumerate(rows, 1):
        ask = " ".join(r["ask"].split())[:140]
        print(f"{i:>2}. [{'/'.join(r['reasons'])}] {r['repo']}#{r['number']} ({r['type']}) {r['title']}")
        print(f"    từ @{r['from']} lúc {r['at']} · {r['comment_url']}")
        if ask:
            print(f"    “{ask}”")
