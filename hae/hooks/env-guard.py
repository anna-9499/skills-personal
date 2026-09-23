#!/usr/bin/env python3
"""
Hae — PreToolUse guard: chặn sub-agent (sonder/ash/…) điều hướng browser tới
môi trường production. Ba kết quả, giống bài học của Blacksmith guard.sh:

  allow  -> im lặng (không in gì, exit 0)
  deny   -> URL có hình dáng production -> tool KHÔNG chạy, lý do trả về cho agent
  (lỗi)  -> shim env-guard.sh chuyển thành ask; KHÔNG bao giờ lặng lẽ allow

Vì sao deny chứ không ask: ở auto mode, `ask` được classifier tự duyệt, chị không
thấy gì (đã kiểm chứng 2026-09-17). Muốn mở production thật, CHỊ gõ trong Terminal:
    touch ~/.hae-allow-production
cửa mở 30 phút rồi tự đóng. Hae/sub-agent KHÔNG BAO GIỜ tự tạo file này.

Chỉnh danh sách bên dưới khi thêm app / đổi domain. Không parse JSON bằng
sed/grep (BSD sed trên macOS đã làm Blacksmith allow-all suốt nhiều tháng).
"""
import json
import os
import re
import sys
import time
from urllib.parse import urlparse

# Host khớp một trong các suffix này là "đáng ngờ" nếu KHÔNG có dấu hiệu staging.
PRODUCTION_SUFFIXES = (
    "mailtro.ai",        # Mailtro app / id / api
    "myshopify.com",     # store live
)
# admin.shopify.com/store/<handle>/... -> xét <handle>
SHOPIFY_ADMIN_HOST = "admin.shopify.com"

# Có một trong các marker này (trong host hoặc store handle) -> coi là staging/dev.
STAGING_MARKERS = ("staging", "stg", "dev", "test", "qa", "sandbox", "preview", "localhost", "127.0.0.1")

# Host/suffix luôn allow, kể cả không có marker (workspace staging, tool nội bộ).
ALWAYS_ALLOW_SUFFIXES = (
    "wisle.app",          # workspace Mailtro staging
    "qa-hub.ownego.com",
    "ownego.atlassian.net",
    "github.com",
)

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)


def has_marker(text: str) -> bool:
    t = text.lower()
    return any(m in t for m in STAGING_MARKERS)


def classify(url: str):
    """Trả về None nếu allow, hoặc chuỗi lý do nếu cần ask."""
    p = urlparse(url)
    host = (p.hostname or "").lower()
    if not host:
        return None
    if host.endswith(ALWAYS_ALLOW_SUFFIXES) or has_marker(host):
        return None
    if host == SHOPIFY_ADMIN_HOST:
        m = re.match(r"^/store/([^/]+)", p.path or "")
        if m and not has_marker(m.group(1)):
            return f"Shopify admin của store live `{m.group(1)}`"
        return None
    for suf in PRODUCTION_SUFFIXES:
        if host == suf or host.endswith("." + suf):
            return f"host `{host}` không có dấu hiệu staging"
    return None


def iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from iter_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from iter_strings(v)


LOG = "/tmp/hae-env-guard.log"
OVERRIDE = os.path.expanduser("~/.hae-allow-production")
OVERRIDE_TTL_SEC = 30 * 60


def override_active() -> bool:
    try:
        age = time.time() - os.stat(OVERRIDE).st_mtime
        return 0 <= age <= OVERRIDE_TTL_SEC
    except FileNotFoundError:
        return False


def log(tool, decision, reasons):
    try:
        import datetime
        with open(LOG, "a") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {decision:5} {tool} {'; '.join(reasons) or '-'}\n")
    except Exception:
        pass


def main() -> int:
    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    reasons = []
    for s in iter_strings(tool_input):
        for url in URL_RE.findall(s):
            r = classify(url)
            if r:
                reasons.append(f"{url} — {r}")

    if not reasons:
        log(tool, "allow", reasons)
        return 0  # allow, im lặng

    if override_active():
        log(tool, "allow*", reasons)  # chị đã mở cửa bằng ~/.hae-allow-production
        return 0

    log(tool, "deny", reasons)
    reason = (
        "Hae env-guard: CHẶN — URL có hình dáng PRODUCTION, sub-agent chỉ được chạy trên staging/dev store. "
        + "; ".join(dict.fromkeys(reasons))
        + f" (tool: {tool}). Báo lại cho chị. Nếu chị thật sự muốn vào, chị tự gõ trong Terminal: "
        "`touch ~/.hae-allow-production` (mở 30 phút). Agent không được tự tạo file này."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
