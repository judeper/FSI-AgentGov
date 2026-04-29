#!/usr/bin/env python3
"""
Microsoft Learn Documentation Monitor

Monitors Microsoft Learn URLs for content changes that may require updates
to the FSI-AgentGov framework. Detects UI step changes, policy updates,
deprecations, and maps changes to affected controls and playbooks.

This is a source adapter for the unified monitoring framework. It uses
shared utilities from monitoring_shared.py.

Usage:
    python scripts/learn_monitor.py [--dry-run] [--limit N] [--verbose] [--debug]

Exit Codes:
    0 - No meaningful changes detected
    1 - Meaningful changes detected (triggers PR in CI)
    2 - Error during execution

Environment Variables:
    LEARN_MONITOR_DEBUG=1  - Enable debug output
"""

import logging
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# Import shared monitoring framework
from monitoring_shared import (
    CLASSIFICATION_CRITICAL,
    CLASSIFICATION_HIGH,
    CLASSIFICATION_MEDIUM,
    CLASSIFICATION_NOISE,
    DEFAULT_CONFIG_PATH,
    classify_change,
    compute_hash,
    fetch_page,
    find_affected_controls,
    format_change_summary,
    generate_executive_summary,
    generate_report_header,
    get_source_state,
    load_monitoring_config,
    load_state,
    normalize_content,
    save_state_atomic,
    set_source_state,
    validate_config,
    write_report,
)

# Handle Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(verbose: bool = False, debug: bool = False) -> logging.Logger:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)

    # Check environment variable
    if os.environ.get("LEARN_MONITOR_DEBUG", "").lower() in ("1", "true", "yes"):
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)


logger = logging.getLogger(__name__)


try:
    import requests
    from bs4 import BeautifulSoup  # noqa: F401  (imported for availability check)
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install with: pip install requests beautifulsoup4")
    print("\nDebug info:")
    print(f"  Python version: {sys.version}")
    print(f"  Python executable: {sys.executable}")
    print(f"  sys.path: {sys.path[:3]}...")
    sys.exit(2)

# === Configuration ===
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DOCS_DIR = PROJECT_ROOT / "docs"

WATCHLIST_PATH = DOCS_DIR / "reference" / "microsoft-learn-urls.md"
STATE_FILE_PATH = PROJECT_ROOT / "data" / "monitor-state.json"  # Unified state file
REPORTS_DIR = PROJECT_ROOT / "reports" / "monitoring"  # Unified reports directory

SOURCE_KEY = "learn"  # Key in unified state file
REPORT_PREFIX = "learn-changes"  # Report filename prefix

# === Data Classes ===
@dataclass
class URLEntry:
    url: str
    topic: str
    section: str


@dataclass
class ChangeRecord:
    url: str
    topic: str
    section: str
    classification: str  # CRITICAL, HIGH, MEDIUM, NOISE
    reason: str
    diff_text: str
    affected_controls: list = field(default_factory=list)
    affected_playbooks: list = field(default_factory=list)
    priority: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, NOISE


# === Watchlist Parsing ===
def parse_watchlist(watchlist_path: Path) -> list[URLEntry]:
    """
    Extract Microsoft Learn URLs from microsoft-learn-urls.md.
    Skips Admin Portals and Regulatory References sections.
    """
    content = watchlist_path.read_text(encoding='utf-8')
    urls = []

    # Sections to skip (not Learn URLs)
    skip_sections = [
        "Admin Portals",
        "Microsoft Open Source Tools",
        "Regulatory References",
    ]

    # Match section headers
    section_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)

    # Match table rows with Learn URLs
    row_pattern = re.compile(
        r"\|\s*\*?\*?([^|]+?)\*?\*?\s*\|\s*(https://learn\.microsoft\.com[^\s|]+)\s*\|",
        re.MULTILINE
    )

    # Track sections by position
    sections = [(m.start(), m.group(1).strip()) for m in section_pattern.finditer(content)]

    for match in row_pattern.finditer(content):
        topic = match.group(1).strip().replace('**', '')
        url = match.group(2).strip()

        # Find which section this URL is in
        pos = match.start()
        section = "Unknown"
        for sec_pos, sec_name in reversed(sections):
            if pos > sec_pos:
                section = sec_name
                break

        # Skip non-Learn sections
        if any(skip in section for skip in skip_sections):
            continue

        urls.append(URLEntry(url=url, topic=topic, section=section))

    return urls


# === Priority Determination ===
def determine_priority(change: ChangeRecord) -> str:
    """Determine overall priority based on affected files."""
    if any(p.get('priority') == CLASSIFICATION_CRITICAL for p in change.affected_playbooks):
        return CLASSIFICATION_CRITICAL
    if change.affected_playbooks or change.classification == CLASSIFICATION_HIGH:
        return CLASSIFICATION_HIGH
    if change.affected_controls:
        return CLASSIFICATION_MEDIUM
    return CLASSIFICATION_MEDIUM


# === Report Generation ===
def generate_report(changes: list[ChangeRecord], redirects: list[dict],
                    errors: list[dict], run_time: str, total_urls: int) -> str:
    """
    Generate markdown change report using unified format.

    Uses shared framework helpers for header, executive summary, and change summary table,
    then adds detailed change sections.
    """
    # Count by tier
    tier_counts = {
        CLASSIFICATION_CRITICAL: sum(1 for c in changes if c.priority == CLASSIFICATION_CRITICAL),
        CLASSIFICATION_HIGH: sum(1 for c in changes if c.priority == CLASSIFICATION_HIGH),
        CLASSIFICATION_MEDIUM: sum(1 for c in changes if c.classification == CLASSIFICATION_MEDIUM or c.priority == CLASSIFICATION_MEDIUM),
        CLASSIFICATION_NOISE: sum(1 for c in changes if c.classification == CLASSIFICATION_NOISE),
        'redirects': len(redirects),
        'errors': len(errors),
    }

    # Build report
    lines = []

    # Header
    lines.append(generate_report_header(
        title="Microsoft Learn Documentation Changes",
        run_date=run_time,
        metadata={
            'Total URLs Checked': total_urls,
        }
    ))

    # Executive Summary
    lines.append(generate_executive_summary(tier_counts))

    # Summary Table
    if changes:
        lines.append(format_change_summary(changes))

    # Detailed CRITICAL changes
    critical_changes = [c for c in changes if c.priority == CLASSIFICATION_CRITICAL]
    if critical_changes:
        lines.extend([
            "## CRITICAL: Playbook Updates Required",
            "",
            "These changes affect step-by-step procedures and must be addressed.",
            "",
        ])
        for i, c in enumerate(critical_changes, 1):
            lines.extend(_format_change(c, i))

    # Detailed HIGH priority changes
    high_changes = [c for c in changes if c.priority == CLASSIFICATION_HIGH and c not in critical_changes]
    if high_changes:
        lines.extend([
            "## HIGH: Control Review Recommended",
            "",
        ])
        for i, c in enumerate(high_changes, 1):
            lines.extend(_format_change(c, i))

    # MEDIUM changes
    medium_changes = [c for c in changes if c.classification == CLASSIFICATION_MEDIUM or (c.priority == CLASSIFICATION_MEDIUM and c not in critical_changes and c not in high_changes)]
    if medium_changes:
        lines.extend([
            "## MEDIUM: Minor Changes (Review Optional)",
            "",
        ])
        for i, c in enumerate(medium_changes, 1):
            lines.append(f"### {i}. {c.topic}")
            lines.append(f"**URL:** {c.url}")
            lines.append(f"**Classification:** {c.classification} ({c.reason})")
            lines.extend(["", "---", ""])

    # Redirects
    if redirects:
        lines.extend([
            "## URL Redirects Detected",
            "",
            "Consider updating microsoft-learn-urls.md:",
            "",
            "| Original URL | Redirects To |",
            "|--------------|--------------|",
        ])
        for r in redirects:
            lines.append(f"| {r['original']} | {r['final']} |")
        lines.extend(["", "---", ""])

    # Errors
    if errors:
        lines.extend([
            "## Errors",
            "",
        ])
        for e in errors:
            lines.append(f"- **{e['topic']}** (HTTP {e['status']}): {e['url']}")
            if e.get('error'):
                lines.append(f"  - Error: {e['error']}")
        lines.append("")
    else:
        lines.extend(["## Errors", "", "No errors detected.", ""])

    lines.extend([
        "---",
        "",
        "*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*",
    ])

    return "\n".join(lines)


def _format_change(c: ChangeRecord, index: int) -> list[str]:
    """Format a single change record for the report."""
    lines = [
        f"### {index}. {c.topic}",
        "",
        f"**URL:** {c.url}",
        f"**Section:** {c.section}",
        f"**Classification:** {c.classification} ({c.reason})",
        "",
    ]

    if c.affected_controls:
        lines.append("**Affected Controls:**")
        for ctrl in c.affected_controls:
            lines.append(f"- Control {ctrl['control_id']}: {ctrl['title']}")
            lines.append(f"  - File: `{ctrl['file_path']}`")
        lines.append("")

    if c.affected_playbooks:
        lines.append("**Affected Playbooks:**")
        for p in c.affected_playbooks:
            priority_icon = "⚠️" if p.get('priority') == CLASSIFICATION_CRITICAL else "ℹ️"
            lines.append(f"- {priority_icon} `{p['file_path']}` ({p.get('priority', 'HIGH')})")
        lines.append("")

    if c.diff_text:
        lines.extend([
            "**What Changed:**",
            "```diff",
            c.diff_text[:2000],  # Limit diff size
            "```",
            "",
        ])

    lines.extend(["---", ""])
    return lines


# === Debug Functions ===
def _debug_single_url(url: str, config: dict):
    """Debug a single URL - useful for troubleshooting."""
    print("\nDebug mode: checking single URL")
    print(f"URL: {url}")
    print("=" * 60)

    session = requests.Session()
    session.headers["User-Agent"] = "FSI-AgentGov-Monitor/1.0"

    print("\n1. Fetching page...")
    result = fetch_page(url, session)
    print(f"   Status: {result['status_code']}")
    print(f"   Final URL: {result['final_url']}")
    print(f"   Redirected: {result['was_redirected']}")
    if result['error']:
        print(f"   Error: {result['error']}")
        return

    print(f"   Content length: {len(result['content'])} bytes")

    print("\n2. Extracting content...")
    try:
        normalized = normalize_content(result['content'])
        print(f"   Normalized length: {len(normalized)} chars")
        print("   First 500 chars:\n   ---")
        print("   " + normalized[:500].replace("\n", "\n   "))
        print("   ---")
    except Exception as e:
        print(f"   ERROR extracting content: {e}")
        logger.debug(traceback.format_exc())
        return

    print("\n3. Computing hash...")
    content_hash = compute_hash(normalized)
    print(f"   Hash: {content_hash}")

    print("\n4. Finding affected files...")
    affected = find_affected_controls(url, DOCS_DIR)
    print(f"   Controls: {len(affected['controls'])}")
    for ctrl in affected['controls']:
        print(f"     - {ctrl['control_id']}: {ctrl['file_path']}")
    print(f"   Playbooks: {len(affected['playbooks'])}")
    for pb in affected['playbooks']:
        print(f"     - {pb['control_id']}/{pb['playbook_type']} ({pb['priority']})")

    print("\n5. State check...")
    unified_state = load_state(STATE_FILE_PATH)
    source_state = get_source_state(unified_state, SOURCE_KEY)

    if source_state and url in source_state.get("urls", {}):
        old_state = source_state["urls"][url]
        print("   Found in state file")
        print(f"   Last checked: {old_state.get('last_checked', 'unknown')}")
        print(f"   Last changed: {old_state.get('last_changed', 'unknown')}")
        if old_state.get("content_hash") == content_hash:
            print("   Content: UNCHANGED")
        else:
            print("   Content: CHANGED")
            if old_state.get("normalized_content"):
                classification, reason, diff_text = classify_change(
                    old_state["normalized_content"], normalized, url, config=config
                )
                print(f"   Classification: {classification} ({reason})")
    else:
        print("   Not found in state file (new URL)")

    print("\nDebug complete.")
    sys.exit(0)


# === Main Function ===
def main():
    """Main monitoring routine."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Microsoft Learn Documentation Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit Codes:
  0 - No meaningful changes detected
  1 - Meaningful changes detected (triggers PR in CI)
  2 - Error during execution

Examples:
  python scripts/learn_monitor.py                    # Normal run
  python scripts/learn_monitor.py --dry-run          # Test without saving
  python scripts/learn_monitor.py --limit 5 --debug  # Debug with 5 URLs
        """
    )
    parser.add_argument("--dry-run", action="store_true",
                       help="Don't save state or write report")
    parser.add_argument("--limit", type=int,
                       help="Limit number of URLs to check (for testing)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--debug", "-d", action="store_true",
                       help="Enable debug output (very verbose)")
    parser.add_argument("--url", type=str,
                       help="Check a single URL (for debugging)")
    parser.add_argument("--config", type=str, default=None,
                       help='Path to config file (default: scripts/config/monitoring-config.yaml)')
    parser.add_argument("--validate", action="store_true",
                       help='Validate config file and exit without running')
    args = parser.parse_args()

    # Setup logging
    global logger
    logger = setup_logging(verbose=args.verbose, debug=args.debug)

    # Load and validate config
    config_path = args.config or DEFAULT_CONFIG_PATH
    config = load_monitoring_config(config_path)

    if args.validate:
        is_valid, errors = validate_config(config)
        if is_valid:
            print(f"Config valid: {config_path}")
            sys.exit(0)
        else:
            print(f"Config errors in {config_path}:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(2)

    print("Microsoft Learn Documentation Monitor")
    print("=" * 50)
    logger.debug(f"Arguments: {args}")
    logger.debug(f"PROJECT_ROOT: {PROJECT_ROOT}")
    logger.debug(f"WATCHLIST_PATH: {WATCHLIST_PATH}")
    logger.debug(f"STATE_FILE_PATH: {STATE_FILE_PATH}")
    logger.debug(f"CONFIG_PATH: {config_path}")

    try:
        return _run_monitor(args, config)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())
        print(f"\nERROR: {e}")
        print("\nFor debugging, run with --debug flag:")
        print("  python scripts/learn_monitor.py --debug")
        sys.exit(2)


def _run_monitor(args, config: dict):
    """Internal monitor implementation."""

    # Get operational settings from config
    request_delay = config.get('operational', {}).get('request_delay', 1.0)

    # Handle single URL mode for debugging
    if args.url:
        return _debug_single_url(args.url, config)

    # 1. Parse watchlist
    if not WATCHLIST_PATH.exists():
        print(f"ERROR: Watchlist not found: {WATCHLIST_PATH}")
        logger.debug(f"Checked path: {WATCHLIST_PATH.absolute()}")
        sys.exit(2)

    try:
        url_entries = parse_watchlist(WATCHLIST_PATH)
    except Exception as e:
        logger.error(f"Failed to parse watchlist: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(2)

    print(f"Found {len(url_entries)} Learn URLs in watchlist")
    logger.debug(f"First 3 URLs: {[e.url for e in url_entries[:3]]}")

    if args.limit:
        url_entries = url_entries[:args.limit]
        print(f"Limited to {args.limit} URLs for testing")

    # 2. Load unified state and get source-specific section
    unified_state = load_state(STATE_FILE_PATH)
    source_state = get_source_state(unified_state, SOURCE_KEY)

    # Handle migration from old format
    if not source_state and "schema_version" in unified_state.get("sources", {}).get(SOURCE_KEY, {}):
        # Already migrated
        source_state = unified_state["sources"][SOURCE_KEY]
    elif not source_state:
        # New state - initialize
        source_state = {
            "schema_version": 2,
            "last_run": None,
            "urls": {},
            "statistics": {}
        }

    is_baseline = source_state.get("last_run") is None
    if is_baseline:
        print("First run - establishing baseline (no report will be generated)")

    # 3. Check each URL
    session = requests.Session()
    session.headers["User-Agent"] = "FSI-AgentGov-Monitor/1.0 (+https://github.com/judeper/FSI-AgentGov)"

    changes: list[ChangeRecord] = []
    redirects: list[dict] = []
    errors: list[dict] = []
    now = datetime.now(timezone.utc).isoformat()

    for i, entry in enumerate(url_entries):
        print(f"[{i+1}/{len(url_entries)}] {entry.topic[:50]}...")

        result = fetch_page(entry.url, session)

        # Handle errors
        if result['status_code'] != 200:
            if result['error']:
                print(f"  ERROR: {result['error']}")
            else:
                print(f"  ERROR: HTTP {result['status_code']}")

            errors.append({
                'url': entry.url,
                'topic': entry.topic,
                'status': result['status_code'],
                'error': result['error'],
            })

            # Preserve previous state if exists
            if entry.url in source_state.get("urls", {}):
                source_state["urls"][entry.url]["last_checked"] = now
                source_state["urls"][entry.url]["last_status"] = result['status_code']

            time.sleep(request_delay)
            continue

        # Track redirects
        if result['was_redirected']:
            print(f"  Redirected to: {result['final_url']}")
            redirects.append({
                'original': entry.url,
                'final': result['final_url'],
                'topic': entry.topic,
            })

        # Extract and hash content
        normalized = normalize_content(result['content'])
        new_hash = compute_hash(normalized)

        # Compare to previous state
        url_state = source_state.get("urls", {}).get(entry.url, {})
        old_hash = url_state.get("content_hash")
        old_content = url_state.get("normalized_content", "")

        if old_hash is None:
            # New URL - baseline
            print("  NEW: Establishing baseline")
            if "urls" not in source_state:
                source_state["urls"] = {}
            source_state["urls"][entry.url] = {
                "content_hash": new_hash,
                "normalized_content": normalized,
                "last_checked": now,
                "last_status": 200,
                "last_changed": now,
                "topic": entry.topic,
                "section": entry.section,
            }
        elif new_hash != old_hash:
            # Content changed
            classification, reason, diff_text = classify_change(old_content, normalized, entry.url, config=config)
            print(f"  CHANGED: {classification} ({reason})")

            # Find affected files
            affected = find_affected_controls(entry.url, DOCS_DIR)

            change = ChangeRecord(
                url=entry.url,
                topic=entry.topic,
                section=entry.section,
                classification=classification,
                reason=reason,
                diff_text=diff_text,
                affected_controls=affected['controls'],
                affected_playbooks=affected['playbooks'],
            )
            change.priority = determine_priority(change)
            changes.append(change)

            # Update state
            source_state["urls"][entry.url] = {
                "content_hash": new_hash,
                "normalized_content": normalized,
                "last_checked": now,
                "last_status": 200,
                "last_changed": now,
                "topic": entry.topic,
                "section": entry.section,
            }
        else:
            # No change
            source_state["urls"][entry.url]["last_checked"] = now
            source_state["urls"][entry.url]["last_status"] = 200

        time.sleep(request_delay)

    # 4. Update statistics
    meaningful_changes = [c for c in changes if c.classification in [CLASSIFICATION_CRITICAL, CLASSIFICATION_HIGH]]

    source_state["last_run"] = now
    source_state["statistics"] = {
        "total_urls": len(url_entries),
        "last_run_checked": len(url_entries),
        "last_run_critical_changes": sum(1 for c in changes if c.priority == CLASSIFICATION_CRITICAL),
        "last_run_high_changes": sum(1 for c in changes if c.priority == CLASSIFICATION_HIGH),
        "last_run_medium_changes": sum(1 for c in changes if c.classification == CLASSIFICATION_MEDIUM),
        "last_run_redirects": len(redirects),
        "last_run_errors": len(errors),
    }

    # Save unified state
    set_source_state(unified_state, SOURCE_KEY, source_state)
    if not args.dry_run:
        save_state_atomic(unified_state, STATE_FILE_PATH)
        print(f"\nState saved to {STATE_FILE_PATH} (source: {SOURCE_KEY})")

    # 5. Generate report
    print("\n" + "=" * 50)
    print(f"CRITICAL changes: {source_state['statistics']['last_run_critical_changes']}")
    print(f"HIGH changes: {source_state['statistics']['last_run_high_changes']}")
    print(f"MEDIUM changes: {source_state['statistics']['last_run_medium_changes']}")
    print(f"Redirects: {len(redirects)}")
    print(f"Errors: {len(errors)}")

    if is_baseline:
        print("\nBaseline established. No report generated on first run.")
        sys.exit(0)

    if meaningful_changes or errors:
        report = generate_report(changes, redirects, errors, now, len(url_entries))
        report_filename = f"{REPORT_PREFIX}-{now[:10]}.md"

        if not args.dry_run:
            report_path = write_report(report, REPORTS_DIR, report_filename)
            print(f"Report saved to {report_path}")

        print(f"\n{len(meaningful_changes)} meaningful changes detected - exit code 1 for CI")
        sys.exit(1)
    else:
        print("\nNo meaningful changes detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
