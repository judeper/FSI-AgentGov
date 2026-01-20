#!/usr/bin/env python3
"""
Microsoft Learn Documentation Monitor

Monitors Microsoft Learn URLs for content changes that may require updates
to the FSI-AgentGov framework. Detects UI step changes, policy updates,
deprecations, and maps changes to affected controls and playbooks.

Usage:
    python scripts/learn_monitor.py [--dry-run] [--limit N] [--verbose] [--debug]

Exit Codes:
    0 - No meaningful changes detected
    1 - Meaningful changes detected (triggers PR in CI)
    2 - Error during execution

Environment Variables:
    LEARN_MONITOR_DEBUG=1  - Enable debug output
"""

import difflib
import hashlib
import json
import logging
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

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
    from bs4 import BeautifulSoup
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
STATE_FILE_PATH = PROJECT_ROOT / "data" / "learn-monitor-state.json"
REPORTS_DIR = PROJECT_ROOT / "reports" / "learn-changes"

REQUEST_TIMEOUT = 30  # seconds
REQUEST_DELAY = 1.0   # seconds between requests
MAX_RETRIES = 3

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
    classification: str  # meaningful, minor, noise
    reason: str
    diff_text: str
    affected_controls: list = field(default_factory=list)
    affected_playbooks: list = field(default_factory=list)
    priority: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW


@dataclass
class FetchResult:
    url: str
    status_code: int
    content: str
    final_url: str
    was_redirected: bool
    error: Optional[str] = None


# === Watchlist Parsing ===
def parse_watchlist(watchlist_path: Path) -> list[URLEntry]:
    """
    Extract Microsoft Learn URLs from microsoft-learn-urls.md.
    Skips Admin Portals and Regulatory References sections.
    """
    content = watchlist_path.read_text(encoding='utf-8')
    urls = []
    current_section = "Unknown"

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


# === Content Fetching ===
def fetch_page(url: str, session: requests.Session) -> FetchResult:
    """Fetch a page with retry logic and redirect tracking."""
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)

            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 60))
                print(f"  Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            return FetchResult(
                url=url,
                status_code=response.status_code,
                content=response.text if response.status_code == 200 else "",
                final_url=response.url,
                was_redirected=response.url != url,
            )

        except requests.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                return FetchResult(
                    url=url,
                    status_code=0,
                    content="",
                    final_url=url,
                    was_redirected=False,
                    error=str(e)
                )
            time.sleep(2 ** attempt)

    return FetchResult(
        url=url,
        status_code=0,
        content="",
        final_url=url,
        was_redirected=False,
        error="Max retries exceeded"
    )


# === Content Extraction ===
def extract_main_content(html: str) -> str:
    """Extract and normalize main content from Learn page using BeautifulSoup."""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove non-content elements
    for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
        tag.decompose()

    # Remove Learn page chrome (feedback, metadata sections)
    for selector in ['.feedback-section', '.metadata', '.contributors', '.page-metadata']:
        for elem in soup.select(selector):
            elem.decompose()

    # Find main content area
    main = soup.find('main') or soup.find('article') or soup.find('div', class_='content')

    if main:
        text = main.get_text(separator='\n', strip=True)
    else:
        text = soup.get_text(separator='\n', strip=True)

    # Normalize
    text = re.sub(r'\n{3,}', '\n\n', text)  # Collapse blank lines
    text = re.sub(r'[ \t]+', ' ', text)      # Collapse whitespace
    text = re.sub(r'\d{1,2}/\d{1,2}/\d{4}', '[DATE]', text)  # Mask dates

    return text.strip()


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash of content."""
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


# === Change Classification ===
def classify_change(old_text: str, new_text: str) -> tuple[str, str, str]:
    """
    Classify change and generate diff.
    Returns (classification, reason, diff_text)
    """
    # Generate unified diff
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff_lines = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))

    if not diff_lines:
        return ('noise', 'No text changes detected', '')

    diff_text = ''.join(diff_lines[:100])  # Limit diff size

    # MEANINGFUL patterns (aligned with FSI-AgentGov priorities)
    meaningful_patterns = [
        # UI Navigation (CRITICAL for playbooks)
        (r'\d+\.\s+(click|select|go to|navigate)', 'UI navigation steps'),
        (r'(Admin center|portal|Power Platform|Purview)', 'Portal references'),
        (r'(button|menu|tab|panel|dialog|blade)', 'UI element names'),

        # Policy/Compliance (HIGH for controls)
        (r'(Important|Warning|Note|Caution):', 'Policy callout blocks'),
        (r'(required|must|should not|prohibited)', 'Policy language'),
        (r'(compliance|audit|retention|DLP)', 'Compliance features'),

        # Deprecation (HIGH - requires action)
        (r'(deprecated|removed|no longer|retired)', 'Deprecation notice'),
        (r'(preview|GA|generally available)', 'Feature availability'),
        (r'(breaking change|migration)', 'Breaking changes'),

        # Configuration (MEDIUM-HIGH)
        (r'(enable|disable|configure|set to)', 'Configuration instructions'),
        (r'(PowerShell|cmdlet|Graph API)', 'Automation references'),
        (r'(license|SKU|E5|E3)', 'Licensing requirements'),
    ]

    # Check diff lines for meaningful patterns
    for line in diff_lines:
        if line.startswith('+') or line.startswith('-'):
            for pattern, reason in meaningful_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return ('meaningful', reason, diff_text)

    # NOISE patterns
    noise_patterns = [
        r'^[-+]\s*$',
        r'ms\.(date|author|reviewer|topic)',
        r'(Article|Contributor|Feedback)',
    ]

    noise_only = True
    for line in diff_lines:
        if line.startswith('+') or line.startswith('-'):
            is_noise = any(re.search(p, line, re.IGNORECASE) for p in noise_patterns)
            if not is_noise and line.strip() not in ['+', '-', '+++', '---']:
                noise_only = False
                break

    if noise_only:
        return ('noise', 'Metadata or formatting only', diff_text)

    return ('minor', 'General content update', diff_text)


# === Impact Mapping ===
def find_affected_files(url: str, docs_dir: Path) -> dict:
    """
    Find controls and playbooks that reference this URL.
    """
    affected = {'controls': [], 'playbooks': []}

    # Scan controls
    controls_dir = docs_dir / 'controls'
    if controls_dir.exists():
        for pillar_dir in controls_dir.glob('pillar-*'):
            for control_file in pillar_dir.glob('*.md'):
                try:
                    content = control_file.read_text(encoding='utf-8')
                    if url in content:
                        control_id = control_file.stem.split('-')[0]
                        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                        affected['controls'].append({
                            'control_id': control_id,
                            'title': title_match.group(1) if title_match else control_file.stem,
                            'file_path': str(control_file.relative_to(docs_dir)),
                        })
                except Exception:
                    continue

    # Scan playbooks
    playbooks_dir = docs_dir / 'playbooks' / 'control-implementations'
    if playbooks_dir.exists():
        for control_dir in playbooks_dir.glob('*'):
            for playbook_file in control_dir.glob('*.md'):
                try:
                    content = playbook_file.read_text(encoding='utf-8')
                    if url in content:
                        playbook_type = playbook_file.stem
                        priority = 'CRITICAL' if playbook_type == 'portal-walkthrough' else 'HIGH'
                        affected['playbooks'].append({
                            'control_id': control_dir.name,
                            'playbook_type': playbook_type,
                            'file_path': str(playbook_file.relative_to(docs_dir)),
                            'priority': priority,
                        })
                except Exception:
                    continue

    return affected


def determine_priority(change: ChangeRecord) -> str:
    """Determine overall priority based on affected files."""
    if any(p.get('priority') == 'CRITICAL' for p in change.affected_playbooks):
        return 'CRITICAL'
    if change.affected_playbooks or change.classification == 'meaningful':
        return 'HIGH'
    if change.affected_controls:
        return 'MEDIUM'
    return 'LOW'


# === State Management ===
def load_state(state_path: Path) -> dict:
    """Load state from JSON file."""
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            print("WARNING: State file corrupt, starting fresh")
    return {
        "schema_version": 2,
        "last_run": None,
        "urls": {},
        "statistics": {}
    }


def save_state(state: dict, state_path: Path):
    """Save state to JSON file."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


# === Report Generation ===
def generate_report(changes: list[ChangeRecord], redirects: list[dict],
                    errors: list[dict], run_time: str, total_urls: int) -> str:
    """Generate markdown change report."""
    meaningful = [c for c in changes if c.classification == 'meaningful']
    minor = [c for c in changes if c.classification == 'minor']

    # Count by priority
    critical_count = sum(1 for c in changes if c.priority == 'CRITICAL')
    high_count = sum(1 for c in changes if c.priority == 'HIGH')

    lines = [
        f"# Microsoft Learn Documentation Changes - {run_time[:10]}",
        "",
        f"**Run Time:** {run_time}",
        f"**Total URLs Checked:** {total_urls}",
        f"**Meaningful Changes:** {len(meaningful)}",
        f"**Minor Changes:** {len(minor)}",
        f"**Redirects:** {len(redirects)}",
        f"**Errors:** {len(errors)}",
        "",
        "---",
        "",
    ]

    # Summary table
    if changes:
        lines.extend([
            "## Summary of Required Actions",
            "",
            "| Priority | Count | Action Required |",
            "|----------|-------|-----------------|",
        ])
        if critical_count:
            lines.append(f"| CRITICAL | {critical_count} | Playbook portal-walkthrough.md needs update |")
        if high_count:
            lines.append(f"| HIGH | {high_count} | Control/playbook may need review |")
        if len(minor):
            lines.append(f"| MEDIUM | {len(minor)} | Minor content change - review optional |")
        lines.extend(["", "---", ""])

    # CRITICAL changes
    critical_changes = [c for c in changes if c.priority == 'CRITICAL']
    if critical_changes:
        lines.extend([
            "## CRITICAL: Playbook Updates Required",
            "",
            "These changes affect step-by-step procedures and must be addressed.",
            "",
        ])
        for i, c in enumerate(critical_changes, 1):
            lines.extend(_format_change(c, i))
        lines.extend(["---", ""])

    # HIGH priority changes
    high_changes = [c for c in changes if c.priority == 'HIGH' and c not in critical_changes]
    if high_changes:
        lines.extend([
            "## HIGH: Control Review Recommended",
            "",
        ])
        for i, c in enumerate(high_changes, 1):
            lines.extend(_format_change(c, i))
        lines.extend(["---", ""])

    # Minor changes
    if minor:
        lines.extend([
            "## MEDIUM: Minor Changes (Review Optional)",
            "",
        ])
        for i, c in enumerate(minor, 1):
            lines.append(f"### {i}. {c.topic}")
            lines.append(f"**URL:** {c.url}")
            lines.append(f"**Classification:** Minor ({c.reason})")
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
        "*Generated by `scripts/learn_monitor.py`*",
    ])

    return "\n".join(lines)


def _format_change(c: ChangeRecord, index: int) -> list[str]:
    """Format a single change record for the report."""
    lines = [
        f"### {index}. {c.topic}",
        "",
        f"**URL:** {c.url}",
        f"**Section:** {c.section}",
        f"**Classification:** {c.classification.title()} ({c.reason})",
        "",
    ]

    if c.affected_playbooks:
        lines.append("**Affected Playbooks:**")
        for p in c.affected_playbooks:
            priority_icon = "⚠️" if p.get('priority') == 'CRITICAL' else ""
            lines.append(f"- `{p['file_path']}` {priority_icon}")
        lines.append("")

    if c.affected_controls:
        lines.append("**Affected Controls:**")
        for ctrl in c.affected_controls:
            lines.append(f"- Control {ctrl['control_id']}: {ctrl['title']} (`{ctrl['file_path']}`)")
        lines.append("")

    if c.diff_text:
        lines.extend([
            "**What Changed:**",
            "```diff",
            c.diff_text[:2000],  # Limit diff size
            "```",
            "",
        ])

    return lines


# === Debug Functions ===
def _debug_single_url(url: str):
    """Debug a single URL - useful for troubleshooting."""
    print(f"\nDebug mode: checking single URL")
    print(f"URL: {url}")
    print("=" * 60)

    session = requests.Session()
    session.headers["User-Agent"] = "FSI-AgentGov-Monitor/1.0"

    print("\n1. Fetching page...")
    result = fetch_page(url, session)
    print(f"   Status: {result.status_code}")
    print(f"   Final URL: {result.final_url}")
    print(f"   Redirected: {result.was_redirected}")
    if result.error:
        print(f"   Error: {result.error}")
        return

    print(f"   Content length: {len(result.content)} bytes")

    print("\n2. Extracting content...")
    try:
        normalized = extract_main_content(result.content)
        print(f"   Normalized length: {len(normalized)} chars")
        print(f"   First 500 chars:\n   ---")
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
    affected = find_affected_files(url, DOCS_DIR)
    print(f"   Controls: {len(affected['controls'])}")
    for ctrl in affected['controls']:
        print(f"     - {ctrl['control_id']}: {ctrl['file_path']}")
    print(f"   Playbooks: {len(affected['playbooks'])}")
    for pb in affected['playbooks']:
        print(f"     - {pb['control_id']}/{pb['playbook_type']} ({pb['priority']})")

    print("\n5. State check...")
    state = load_state(STATE_FILE_PATH)
    if url in state.get("urls", {}):
        old_state = state["urls"][url]
        print(f"   Found in state file")
        print(f"   Last checked: {old_state.get('last_checked', 'unknown')}")
        print(f"   Last changed: {old_state.get('last_changed', 'unknown')}")
        if old_state.get("content_hash") == content_hash:
            print("   Content: UNCHANGED")
        else:
            print("   Content: CHANGED")
            if old_state.get("normalized_content"):
                classification, reason, diff_text = classify_change(
                    old_state["normalized_content"], normalized
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
    args = parser.parse_args()

    # Setup logging
    global logger
    logger = setup_logging(verbose=args.verbose, debug=args.debug)

    print("Microsoft Learn Documentation Monitor")
    print("=" * 50)
    logger.debug(f"Arguments: {args}")
    logger.debug(f"PROJECT_ROOT: {PROJECT_ROOT}")
    logger.debug(f"WATCHLIST_PATH: {WATCHLIST_PATH}")
    logger.debug(f"STATE_FILE_PATH: {STATE_FILE_PATH}")

    try:
        return _run_monitor(args)
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


def _run_monitor(args):
    """Internal monitor implementation."""

    # Handle single URL mode for debugging
    if args.url:
        return _debug_single_url(args.url)

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

    # 2. Load state
    state = load_state(STATE_FILE_PATH)
    is_baseline = state["last_run"] is None
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
        if result.status_code != 200:
            if result.error:
                print(f"  ERROR: {result.error}")
            else:
                print(f"  ERROR: HTTP {result.status_code}")

            errors.append({
                'url': entry.url,
                'topic': entry.topic,
                'status': result.status_code,
                'error': result.error,
            })

            # Preserve previous state if exists
            if entry.url in state["urls"]:
                state["urls"][entry.url]["last_checked"] = now
                state["urls"][entry.url]["last_status"] = result.status_code

            time.sleep(REQUEST_DELAY)
            continue

        # Track redirects
        if result.was_redirected:
            print(f"  Redirected to: {result.final_url}")
            redirects.append({
                'original': entry.url,
                'final': result.final_url,
                'topic': entry.topic,
            })

        # Extract and hash content
        normalized = extract_main_content(result.content)
        new_hash = compute_hash(normalized)

        # Compare to previous state
        url_state = state["urls"].get(entry.url, {})
        old_hash = url_state.get("content_hash")
        old_content = url_state.get("normalized_content", "")

        if old_hash is None:
            # New URL - baseline
            print("  NEW: Establishing baseline")
            state["urls"][entry.url] = {
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
            classification, reason, diff_text = classify_change(old_content, normalized)
            print(f"  CHANGED: {classification} ({reason})")

            # Find affected files
            affected = find_affected_files(entry.url, DOCS_DIR)

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
            state["urls"][entry.url] = {
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
            state["urls"][entry.url]["last_checked"] = now
            state["urls"][entry.url]["last_status"] = 200

        time.sleep(REQUEST_DELAY)

    # 4. Update state
    meaningful_changes = [c for c in changes if c.classification == 'meaningful']

    state["last_run"] = now
    state["statistics"] = {
        "total_urls": len(url_entries),
        "last_run_checked": len(url_entries),
        "last_run_meaningful_changes": len(meaningful_changes),
        "last_run_minor_changes": len(changes) - len(meaningful_changes),
        "last_run_redirects": len(redirects),
        "last_run_errors": len(errors),
    }

    if not args.dry_run:
        save_state(state, STATE_FILE_PATH)
        print(f"\nState saved to {STATE_FILE_PATH}")

    # 5. Generate report
    print("\n" + "=" * 50)
    print(f"Meaningful changes: {len(meaningful_changes)}")
    print(f"Minor changes: {len(changes) - len(meaningful_changes)}")
    print(f"Redirects: {len(redirects)}")
    print(f"Errors: {len(errors)}")

    if is_baseline:
        print("\nBaseline established. No report generated on first run.")
        sys.exit(0)

    if meaningful_changes or errors:
        report = generate_report(changes, redirects, errors, now, len(url_entries))
        report_path = REPORTS_DIR / f"learn-changes-{now[:10]}.md"

        if not args.dry_run:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report, encoding='utf-8')
            print(f"Report saved to {report_path}")

        print(f"\n{len(meaningful_changes)} meaningful changes detected - exit code 1 for CI")
        sys.exit(1)
    else:
        print("\nNo meaningful changes detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
