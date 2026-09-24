"""PreToolUse hook: blocks Claude from reading .env (allows .env.example)."""

import json
import re
import sys


def hits_env(text: str) -> bool:
    return bool(re.search(r"(^|[\s/])\.env($|[^.\w])", text + " "))


def main() -> None:
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})

    candidates = [
        tool_input.get("file_path") or "",
        tool_input.get("path") or "",
        tool_input.get("command") or "",
    ]

    if any(hits_env(c) for c in candidates if c):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Blocked by project hook: reading .env is not allowed to protect secrets.",
            }
        }))


if __name__ == "__main__":
    main()
