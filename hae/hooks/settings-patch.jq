# Áp vào ~/.claude/settings.json qua apply-settings.sh (truyền --arg guard <đường dẫn tuyệt đối env-guard.sh>).
# Chạy tay: jq --arg guard "$PWD/env-guard.sh" -f settings-patch.jq settings.json.bak > settings.json
# 2026-11-02: bỏ đường dẫn hardcode — clone chỗ khác vẫn đúng (sai path = hook lỗi = harness cho qua).
# Idempotent: gỡ khối env-guard cũ (nếu có) rồi thêm lại với matcher mới nhất.
# 2026-10-24: thêm browser_evaluate / run_code / javascript_* — sonder sửa request cho case Security.
.hooks.PreToolUse = (((.hooks.PreToolUse // []) | map(select(([.hooks[]?.command // ""] | any(test("env-guard"))) | not))) + [{
  "matcher": "mcp__playwright__browser_navigate|mcp__playwright__browser_tabs|mcp__playwright__browser_evaluate|mcp__playwright__browser_run_code|mcp__playwright__browser_run_code_unsafe|mcp__chrome__navigate|mcp__chrome__new_tab|mcp__chrome__javascript_eval|mcp__claude-in-chrome__navigate|mcp__claude-in-chrome__tabs_create_mcp|mcp__claude-in-chrome__javascript_tool",
  "hooks": [{
    "type": "command",
    "command": ("bash \"" + $guard + "\""),
    "shell": "bash"
  }]
}])
| .permissions.ask = ((.permissions.ask // []) + ["mcp__testlane__delete_bug", "mcp__testlane__delete_knowledge"] | unique)
