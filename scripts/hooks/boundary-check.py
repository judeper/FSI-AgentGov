#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook: Project Boundary Check

Intercepts Bash commands and blocks any that might operate
outside the project directory.

Usage: Configured in .claude/settings.local.json as PreToolUse hook
"""

import sys
import json
import os
import re

# Project root - all operations should stay within this directory
PROJECT_ROOT = r"C:\dev\FSI-AgentGov"
PROJECT_ROOT_UNIX = "/c/dev/FSI-AgentGov"  # Git Bash style


def normalize_path(path):
    """Normalize a path for comparison."""
    return os.path.normpath(path).lower()


def is_within_project(path):
    """Check if a path is within the project boundary."""
    normalized = normalize_path(path)
    project_normalized = normalize_path(PROJECT_ROOT)
    return normalized.startswith(project_normalized)


def check_command(command):
    """
    Analyze a Bash command for potential boundary violations.
    Returns (allow: bool, reason: str)
    """
    command_lower = command.lower()

    # Patterns that indicate potential boundary escape
    risky_patterns = [
        # Absolute paths outside project
        (r'(?<![a-z])c:\\(?!dev\\fsi-agentgov)', "Absolute C:\\ path outside project"),
        (r'(?<![a-z])/c/(?!dev/fsi-agentgov)', "Unix-style /c/ path outside project"),
        (r'(?<![a-z])d:\\', "D:\\ drive access"),
        (r'(?<![a-z])/d/', "Unix-style /d/ access"),

        # Parent directory traversal that might escape
        (r'\.\./\.\./\.\./\.\./', "Excessive parent directory traversal"),

        # Root-level operations
        (r'^find\s+/c\b', "find command on C: root"),
        (r'^find\s+c:\\', "find command on C: root"),
        (r'^ls\s+/c\s*$', "ls on C: root"),
        (r'^dir\s+c:\\s*$', "dir on C: root"),

        # Dangerous recursive operations without path constraint
        (r'rm\s+-rf?\s+/', "Recursive delete from root"),
    ]

    for pattern, reason in risky_patterns:
        if re.search(pattern, command_lower, re.IGNORECASE):
            return False, reason

    # Safe patterns - explicitly allowed
    safe_patterns = [
        r'c:\\dev\\fsi-agentgov',
        r'/c/dev/fsi-agentgov',
        r'cd\s+["\']?\.', # cd to relative path
        r'^git\s+',  # git commands (operate in current repo)
        r'^mkdocs\s+',  # mkdocs commands
        r'^python\s+',  # python scripts
        r'^pip\s+',  # pip commands
        r'^npm\s+',  # npm commands
    ]

    # If command contains the project path, it's likely intentional
    if PROJECT_ROOT.lower() in command_lower or PROJECT_ROOT_UNIX.lower() in command_lower:
        return True, "Command explicitly targets project directory"

    # Check for any safe patterns
    for pattern in safe_patterns:
        if re.search(pattern, command_lower):
            return True, "Command matches safe pattern"

    # If no absolute paths detected and no risky patterns, allow
    # (relative paths are fine - they operate from current directory)
    if not re.search(r'(?<![a-z])[a-z]:\\|^/', command_lower):
        return True, "No absolute paths detected"

    # Default: block commands with absolute paths outside project
    return False, "Command contains absolute path - verify it targets the project"


def main():
    """Main hook entry point."""
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())

        tool_input = input_data.get("tool_input", {})
        command = tool_input.get("command", "")

        if not command:
            # No command to check
            print(json.dumps({"decision": "allow"}))
            return

        allowed, reason = check_command(command)

        if allowed:
            print(json.dumps({"decision": "allow"}))
        else:
            print(json.dumps({
                "decision": "block",
                "reason": f"Boundary check failed: {reason}\n"
                         f"Project boundary: {PROJECT_ROOT}\n"
                         f"Command: {command[:100]}..."
            }))

    except Exception as e:
        # On error, allow the command but log warning
        print(json.dumps({
            "decision": "allow",
            "message": f"Boundary check error (allowing): {str(e)}"
        }))


if __name__ == "__main__":
    main()
