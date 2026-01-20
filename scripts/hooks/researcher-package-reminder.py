#!/usr/bin/env python3
"""
Claude Code Hook: Researcher Package Reminder

Triggers after Edit/Write operations on pillar control files.
Reminds the user to update the researcher package when controls change.

Hook Type: PostToolUse
Matcher: Edit, Write
"""

import json
import sys
import re


def main():
    """Process PostToolUse hook for Edit/Write operations."""
    try:
        # Read hook input from stdin
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            return  # No input provided

        hook_input = json.loads(stdin_data)

        # Get the tool name and parameters
        tool_name = hook_input.get("tool_name", "")
        tool_input = hook_input.get("tool_input", {})

        # Only process Edit and Write tools
        if tool_name not in ["Edit", "Write"]:
            return

        # Get the file path from tool input
        file_path = tool_input.get("file_path", "")
        if not file_path:
            return

        # Check if the file is a pillar control document
        # Match patterns like: docs/controls/pillar-1-security/1.1-xxx.md
        pillar_pattern = r"docs[/\\]controls[/\\]pillar-\d+-\w+[/\\]\d+\.\d+.*\.md"

        if re.search(pillar_pattern, file_path, re.IGNORECASE):
            # Output reminder message
            reminder = {
                "message": "Pillar control updated. Remember to regenerate the researcher package:\n  python scripts/compile_researcher_package.py\n  (Output: maintainers-local/researcher-package/)"
            }
            print(json.dumps(reminder))

    except json.JSONDecodeError:
        # Silent exit on invalid JSON - don't break the workflow
        pass
    except Exception:
        # Catch all other errors silently to avoid breaking Claude Code
        pass


if __name__ == "__main__":
    main()
