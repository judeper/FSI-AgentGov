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
import platform

# Project root - detect dynamically based on script location
# Script is at: {PROJECT_ROOT}/scripts/hooks/boundary-check.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Also define platform-specific patterns for detection
IS_WINDOWS = platform.system() == "Windows"
PROJECT_ROOT_UNIX = PROJECT_ROOT.replace("\\", "/")  # Unix-style path


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
    project_lower = PROJECT_ROOT.lower()

    # Patterns that indicate potential boundary escape
    risky_patterns = [
        # Parent directory traversal that might escape
        (r'\.\./\.\./\.\./\.\./', "Excessive parent directory traversal"),

        # Dangerous recursive operations from root
        (r'rm\s+-rf?\s+/$', "Recursive delete from root"),
        (r'rm\s+-rf?\s+/\s*$', "Recursive delete from root"),
    ]

    # Add Windows-specific risky patterns
    if IS_WINDOWS:
        risky_patterns.extend([
            (r'(?<![a-z])c:\\(?!dev\\fsi-agentgov)', "Absolute C:\\ path outside project"),
            (r'(?<![a-z])/c/(?!dev/fsi-agentgov)', "Unix-style /c/ path outside project"),
            (r'(?<![a-z])d:\\', "D:\\ drive access"),
            (r'(?<![a-z])/d/', "Unix-style /d/ access"),
            (r'^find\s+/c\b', "find command on C: root"),
            (r'^find\s+c:\\', "find command on C: root"),
            (r'^ls\s+/c\s*$', "ls on C: root"),
            (r'^dir\s+c:\\s*$', "dir on C: root"),
        ])

    for pattern, reason in risky_patterns:
        if re.search(pattern, command_lower, re.IGNORECASE):
            return False, reason

    # Safe patterns - explicitly allowed
    safe_patterns = [
        r'cd\s+["\']?\.', # cd to relative path
        r'^git\s+',  # git commands (operate in current repo)
        r'^mkdocs\s+',  # mkdocs commands
        r'^python\s+',  # python scripts
        r'^python3\s+',  # python3 scripts
        r'^pip\s+',  # pip commands
        r'^npm\s+',  # npm commands
        r'^source\s+',  # source commands (activate venv)
        r'^which\s+',  # which commands
        r'^echo\s+',  # echo commands
        r'^mkdir\s+',  # mkdir commands
        r'^ls\s+',  # ls commands (general)
        r'^wc\s+',  # wc commands
        r'^rm\s+',  # rm commands (general, checked above for dangerous patterns)
    ]

    # If command contains the project path, it's likely intentional
    if project_lower in command_lower or PROJECT_ROOT_UNIX.lower() in command_lower:
        return True, "Command explicitly targets project directory"

    # Check for any safe patterns
    for pattern in safe_patterns:
        if re.search(pattern, command_lower):
            return True, "Command matches safe pattern"

    # If no absolute paths detected and no risky patterns, allow
    # (relative paths are fine - they operate from current directory)
    # On Unix, check for paths starting with / that aren't the project
    if not IS_WINDOWS:
        # Check if command has absolute paths
        command_parts = command_lower.split()
        has_absolute_path = False
        if command_parts:
            # Check first part and any arguments for absolute paths
            for part in command_parts:
                if part.startswith('/') and not part.startswith(project_lower):
                    has_absolute_path = True
                    break

        if not has_absolute_path:
            return True, "No absolute paths detected"

        # Check if any absolute path in command is within project
        if project_lower in command_lower:
            return True, "Command targets project directory"
    else:
        if not re.search(r'(?<![a-z])[a-z]:\\|^/', command_lower):
            return True, "No absolute paths detected"

    # Default: allow most commands (be permissive on macOS/Linux)
    return True, "Command allowed by default"


def main():
    """Main hook entry point."""
    try:
        # Read input from stdin
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            # No input - allow by default
            print(json.dumps({"decision": "allow"}))
            return

        input_data = json.loads(stdin_data)

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

    except json.JSONDecodeError:
        # Invalid JSON input - allow by default
        print(json.dumps({"decision": "allow"}))
    except Exception as e:
        # On any error, allow the command (fail open)
        print(json.dumps({
            "decision": "allow",
            "message": f"Boundary check error (allowing): {str(e)}"
        }))


if __name__ == "__main__":
    main()
