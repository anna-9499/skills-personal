# Áp vào ~/.claude/settings.json:  jq -f settings-patch.jq settings.json.bak > settings.json
.hooks.PreToolUse += [{
  "matcher": "mcp__playwright__browser_navigate|mcp__playwright__browser_tabs|mcp__chrome__navigate|mcp__chrome__new_tab|mcp__claude-in-chrome__navigate|mcp__claude-in-chrome__tabs_create_mcp",
  "hooks": [{
    "type": "command",
    "command": "bash \"/Users/nngangaa/Downloads/AI Agent/skills-personal/hae/hooks/env-guard.sh\"",
    "shell": "bash"
  }]
}]
| .permissions.ask = ((.permissions.ask // []) + ["mcp__testlane__delete_bug", "mcp__testlane__delete_knowledge"] | unique)
