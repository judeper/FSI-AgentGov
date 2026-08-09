#!/usr/bin/env python3
"""
Unified Monitoring Framework for FSI-AgentGov

Provides shared utilities, state management, and reporting for all monitoring
source adapters (Learn documentation, regulatory sources, etc.). This is the
core of a unified monitoring system with pluggable source adapters - not
separate monitoring systems.

Architecture:
- One unified state file (data/monitor-state.json) with source-keyed sections
- Consistent classification tiers (CRITICAL/HIGH/MEDIUM/NOISE) across all sources
- Shared report format for all source types
- Common utilities for fetch, normalize, hash, classify operations

Source adapters (e.g., learn_monitor.py, regulatory_monitor.py) use this
shared framework to provide their specific monitoring logic.
"""

import difflib
import hashlib
import json
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install with: pip install requests beautifulsoup4")
    raise

try:
    import yaml
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install with: pip install pyyaml")
    raise

# === Configuration Constants ===
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
MAX_RATE_LIMIT_WAIT = 15  # seconds; never let one 429 stall a monitor run indefinitely

# Default path to monitoring configuration file
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "monitoring-config.yaml"

# Classification tiers (used by all source adapters)
CLASSIFICATION_CRITICAL = "CRITICAL"
CLASSIFICATION_HIGH = "HIGH"
CLASSIFICATION_MEDIUM = "MEDIUM"
CLASSIFICATION_NOISE = "NOISE"

# === HTTP Fetching ===
def fetch_page(url: str, session: requests.Session, max_retries: int = MAX_RETRIES) -> dict:
    """
    Fetch a page with retry logic and redirect tracking.

    Args:
        url: URL to fetch
        session: requests.Session instance
        max_retries: Maximum number of retry attempts

    Returns:
        dict with keys: url, status_code, content, final_url, was_redirected, error
    """
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                try:
                    retry_after_seconds = max(0, int(retry_after))
                except (TypeError, ValueError):
                    retry_after_seconds = 0
                # Honor a server hint when it is reasonable, but cap it and
                # apply exponential backoff so a bad/missing header cannot
                # stall a scheduled monitor for minutes per URL.
                wait_time = min(
                    MAX_RATE_LIMIT_WAIT,
                    max(retry_after_seconds, 2 ** attempt),
                )
                if attempt == max_retries - 1:
                    return {
                        'url': url,
                        'status_code': 429,
                        'content': "",
                        'final_url': response.url,
                        'was_redirected': response.url != url,
                        'error': f"rate limited after {max_retries} attempts",
                    }
                print(f"  Rate limited, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            return {
                'url': url,
                'status_code': response.status_code,
                'content': response.text if response.status_code == 200 else "",
                'final_url': response.url,
                'was_redirected': response.url != url,
                'error': None,
            }

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                return {
                    'url': url,
                    'status_code': 0,
                    'content': "",
                    'final_url': url,
                    'was_redirected': False,
                    'error': str(e),
                }
            time.sleep(2 ** attempt)

    return {
        'url': url,
        'status_code': 0,
        'content': "",
        'final_url': url,
        'was_redirected': False,
        'error': "Max retries exceeded",
    }


# === Content Normalization ===
def normalize_content(html: str) -> str:
    """
    Normalize HTML content using BeautifulSoup.

    Strips scripts, styles, nav elements, normalizes whitespace, and masks dates
    to reduce noise in change detection.

    Args:
        html: Raw HTML content

    Returns:
        Normalized text content
    """
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


# === Content Hashing ===
def compute_hash(content: str) -> str:
    """
    Compute SHA-256 hash of content.

    Args:
        content: Text content to hash

    Returns:
        Hash string in format "sha256:hexdigest"
    """
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


# === Change Classification ===
def classify_change(old_text: str, new_text: str, url: str = "", config: dict = None) -> tuple[str, str, str]:
    """
    Classify change severity and generate diff.

    Uses pattern matching to classify changes as CRITICAL/HIGH/MEDIUM/NOISE
    based on FSI-AgentGov priorities (UI steps, policy language, deprecations).
    Patterns are loaded from the monitoring configuration file.

    Args:
        old_text: Previous content
        new_text: Current content
        url: URL being checked (for context in classification)
        config: Configuration dict with pattern definitions. If None, loads default config.

    Returns:
        Tuple of (classification, reason, diff_text)
        - classification: CRITICAL, HIGH, MEDIUM, or NOISE
        - reason: Human-readable explanation
        - diff_text: Unified diff (truncated based on config)
    """
    # Load config if not provided (backward compatible)
    if config is None:
        config = load_monitoring_config()

    # Get operational settings
    max_diff_lines = config.get('operational', {}).get('max_diff_lines', 100)

    # Generate unified diff
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff_lines = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))

    if not diff_lines:
        return (CLASSIFICATION_NOISE, 'No text changes detected', '')

    diff_text = ''.join(diff_lines[:max_diff_lines])

    # Build pattern lists from config
    learn_config = config.get('learn', {})

    critical_patterns = [
        (p['pattern'], p['reason'])
        for p in learn_config.get('critical_patterns', [])
    ]

    high_patterns = [
        (p['pattern'], p['reason'])
        for p in learn_config.get('high_patterns', [])
    ]

    noise_patterns = [
        p['pattern']
        for p in learn_config.get('noise_patterns', [])
    ]

    # CRITICAL patterns (require immediate action)
    for line in diff_lines:
        if line.startswith('+') or line.startswith('-'):
            for pattern, reason in critical_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return (CLASSIFICATION_CRITICAL, reason, diff_text)

    # HIGH patterns (require review)
    for line in diff_lines:
        if line.startswith('+') or line.startswith('-'):
            for pattern, reason in high_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return (CLASSIFICATION_HIGH, reason, diff_text)

    # NOISE patterns
    noise_only = True
    for line in diff_lines:
        if line.startswith('+') or line.startswith('-'):
            is_noise = any(re.search(p, line, re.IGNORECASE) for p in noise_patterns)
            if not is_noise and line.strip() not in ['+', '-', '+++', '---']:
                noise_only = False
                break

    if noise_only:
        return (CLASSIFICATION_NOISE, 'Metadata or formatting only', diff_text)

    return (CLASSIFICATION_MEDIUM, 'General content update', diff_text)


# === Control-to-URL Impact Mapping ===
def find_affected_controls(url: str, docs_dir: Path) -> dict:
    """
    Find controls and playbooks that reference a given URL.

    Scans docs/controls/pillar-*/ and docs/playbooks/ to identify which
    framework controls and implementation playbooks reference the changed URL.

    Args:
        url: URL to search for
        docs_dir: Path to docs/ directory

    Returns:
        dict with keys:
        - 'controls': list of {control_id, title, file_path}
        - 'playbooks': list of {control_id, playbook_type, file_path, priority}
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
                        priority = CLASSIFICATION_CRITICAL if playbook_type == 'portal-walkthrough' else CLASSIFICATION_HIGH
                        affected['playbooks'].append({
                            'control_id': control_dir.name,
                            'playbook_type': playbook_type,
                            'file_path': str(playbook_file.relative_to(docs_dir)),
                            'priority': priority,
                        })
                except Exception:
                    continue

    # Cross-cutting playbook folders (everything under playbooks/ except
    # control-implementations). These have no control_id, so key them by the
    # cross-cutting folder name and scan recursively. Previously these sibling
    # folders (governance-operations, compliance-and-audit, incident-and-risk,
    # regulatory-modules, getting-started, etc.) were invisible to the monitor.
    playbooks_root = docs_dir / 'playbooks'
    if playbooks_root.exists():
        for section_dir in sorted(playbooks_root.glob('*')):
            if not section_dir.is_dir() or section_dir.name == 'control-implementations':
                continue
            for playbook_file in section_dir.rglob('*.md'):
                try:
                    content = playbook_file.read_text(encoding='utf-8')
                    if url in content:
                        affected['playbooks'].append({
                            'control_id': section_dir.name,
                            'playbook_type': playbook_file.stem,
                            'file_path': str(playbook_file.relative_to(docs_dir)),
                            'priority': CLASSIFICATION_HIGH,
                        })
                except Exception:
                    continue

    return affected


# === Summary Table Generation ===
def format_change_summary(changes: list) -> str:
    """
    Generate a summary table for change reports.

    Creates a quick-scan table showing: Change #, URL (shortened), Classification,
    Affected Controls, and Action Required.

    Args:
        changes: List of change records (must have url, classification, affected_controls attributes)

    Returns:
        Markdown table as string
    """
    if not changes:
        return ""

    lines = [
        "## Change Summary (Quick Scan)",
        "",
        "| # | URL | Classification | Affected Controls | Action Required |",
        "|---|-----|----------------|-------------------|-----------------|",
    ]

    for i, change in enumerate(changes, 1):
        # Shorten URL to last path segment
        url_short = urlparse(change.url).path.split('/')[-1] or change.url
        if len(url_short) > 40:
            url_short = "..." + url_short[-37:]

        # Format affected controls
        if hasattr(change, 'affected_controls') and change.affected_controls:
            controls_str = ", ".join(c['control_id'] for c in change.affected_controls)
        else:
            controls_str = "None"

        # Determine action
        classification = getattr(change, 'classification', CLASSIFICATION_MEDIUM)
        priority = getattr(change, 'priority', CLASSIFICATION_MEDIUM)

        if priority == CLASSIFICATION_CRITICAL:
            action = "Update portal-walkthrough"
        elif priority == CLASSIFICATION_HIGH or classification == CLASSIFICATION_HIGH:
            action = "Review and update"
        elif classification == CLASSIFICATION_MEDIUM:
            action = "Review optional"
        else:
            action = "Monitor"

        lines.append(f"| {i} | {url_short} | {classification} | {controls_str} | {action} |")

    lines.extend(["", "---", ""])
    return "\n".join(lines)


# === Unified State Management ===
def load_state(state_path) -> dict:
    """
    Load unified monitoring state from JSON file.

    The unified state format supports multiple source types in a single file:
    {
      "version": 1,
      "sources": {
        "learn": { "last_run": "...", "entries": {...} },
        "regulatory-federal-register": { "last_run": "...", "entries": {...} }
      }
    }

    Backward compatibility: If old format (data/learn-monitor-state.json) exists,
    migrates it into unified format under "learn" source key.

    Args:
        state_path: Path to state file (should be data/monitor-state.json)

    Returns:
        dict with unified state structure
    """
    # Ensure Path object
    state_path = Path(state_path) if not isinstance(state_path, Path) else state_path

    # Load unified format first (if it exists)
    state = None
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding='utf-8'))
            if "version" not in state:
                state["version"] = 1
            if "sources" not in state:
                state["sources"] = {}
        except json.JSONDecodeError:
            print("WARNING: State file corrupt, will attempt migration or start fresh")
            state = None

    # Check for old format and migrate if unified state is missing or empty
    old_state_path = state_path.parent / "learn-monitor-state.json"
    needs_migration = (
        old_state_path.exists()
        and (state is None or not state.get("sources", {}).get("learn"))
    )
    if needs_migration:
        print(f"Migrating old state file from {old_state_path} to unified format...")
        try:
            old_state = json.loads(old_state_path.read_text(encoding='utf-8'))
            if old_state.get("urls") or old_state.get("last_run"):
                if state is None:
                    state = {"version": 1, "sources": {}}
                state["sources"]["learn"] = old_state
                # Persist the migrated state and back up the old file
                save_state_atomic(state, state_path)
                backup_path = old_state_path.with_suffix('.json.migrated')
                old_state_path.rename(backup_path)
                print(f"Migration complete. Old file backed up to {backup_path.name}")
                return state
        except json.JSONDecodeError:
            print("WARNING: Old state file corrupt, starting fresh")

    if state is not None:
        return state

    # Return empty unified state
    return {
        "version": 1,
        "sources": {}
    }


def save_state_atomic(state: dict, state_path):
    """
    Save state to JSON file atomically.

    Uses temp file + rename for atomic writes with backup of previous state.

    Args:
        state: State dict to save
        state_path: Path to state file
    """
    # Ensure Path object
    state_path = Path(state_path) if not isinstance(state_path, Path) else state_path

    state_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing state if it exists
    if state_path.exists():
        backup_path = state_path.with_suffix('.json.backup')
        try:
            backup_path.write_text(state_path.read_text(encoding='utf-8'), encoding='utf-8')
        except Exception:
            pass  # Best effort backup

    # Write to temp file then rename (atomic)
    with tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        dir=state_path.parent,
        delete=False,
        suffix='.tmp'
    ) as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        temp_path = f.name

    # Atomic rename
    Path(temp_path).replace(state_path)


def get_source_state(state: dict, source_key: str) -> dict:
    """
    Get state section for a specific source.

    Args:
        state: Unified state dict
        source_key: Source identifier (e.g., "learn", "regulatory-finra")

    Returns:
        Source-specific state dict (empty dict if new source)
    """
    return state.get("sources", {}).get(source_key, {})


def set_source_state(state: dict, source_key: str, source_state: dict):
    """
    Update state section for a specific source.

    Args:
        state: Unified state dict
        source_key: Source identifier (e.g., "learn", "regulatory-finra")
        source_state: Source-specific state to save
    """
    if "sources" not in state:
        state["sources"] = {}
    state["sources"][source_key] = source_state


# === Unified Report Format Helpers ===
def generate_report_header(title: str, run_date: str, metadata: dict) -> str:
    """
    Generate standard report header.

    Args:
        title: Report title
        run_date: ISO format date string
        metadata: dict of metadata key-value pairs

    Returns:
        Markdown header as string
    """
    lines = [
        f"# {title}",
        "",
        f"**Run Date:** {run_date[:10]}",
        f"**Run Time:** {run_date}",
    ]

    for key, value in metadata.items():
        lines.append(f"**{key}:** {value}")

    lines.extend(["", "---", ""])
    return "\n".join(lines)


def generate_executive_summary(changes_by_tier: dict) -> str:
    """
    Generate standard executive summary for reports.

    Args:
        changes_by_tier: dict with tier counts, e.g.:
            {
                'CRITICAL': 2,
                'HIGH': 5,
                'MEDIUM': 10,
                'NOISE': 3,
                'redirects': 1,
                'errors': 0
            }

    Returns:
        Markdown executive summary as string
    """
    lines = [
        "## Executive Summary",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]

    if changes_by_tier.get('CRITICAL', 0) > 0:
        lines.append(f"| CRITICAL Changes | {changes_by_tier['CRITICAL']} |")
    if changes_by_tier.get('HIGH', 0) > 0:
        lines.append(f"| HIGH Changes | {changes_by_tier['HIGH']} |")
    if changes_by_tier.get('MEDIUM', 0) > 0:
        lines.append(f"| MEDIUM Changes | {changes_by_tier['MEDIUM']} |")
    if changes_by_tier.get('NOISE', 0) > 0:
        lines.append(f"| NOISE Changes | {changes_by_tier['NOISE']} |")
    if changes_by_tier.get('redirects', 0) > 0:
        lines.append(f"| Redirects | {changes_by_tier['redirects']} |")
    if changes_by_tier.get('errors', 0) > 0:
        lines.append(f"| Errors | {changes_by_tier['errors']} |")

    lines.extend(["", "---", ""])
    return "\n".join(lines)


def write_report(report_content: str, report_dir: Path, filename: str):
    """
    Write report to disk.

    Args:
        report_content: Report markdown content
        report_dir: Directory to write report to
        filename: Report filename
    """
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / filename
    report_path.write_text(report_content, encoding='utf-8')
    return report_path


# === Configuration Loading ===
def load_monitoring_config(config_path: Optional[Path] = None) -> dict:
    """
    Load and validate monitoring configuration from YAML file.

    Performs fail-fast validation:
    - File must exist
    - YAML syntax must be valid
    - All regex patterns must compile

    Args:
        config_path: Path to config file. Defaults to DEFAULT_CONFIG_PATH.

    Returns:
        Parsed configuration dict with keys: learn, regulatory, keyword_control_map,
        federal_register, operational

    Exits:
        sys.exit(2) on any validation error with clear error message
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    config_path = Path(config_path) if not isinstance(config_path, Path) else config_path

    # Check file exists
    if not config_path.exists():
        print("ERROR: Configuration file not found")
        print(f"  Expected: {config_path}")
        print("  Please ensure the monitoring config file exists.")
        sys.exit(2)

    # Load YAML
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print("ERROR: Invalid YAML syntax in configuration file")
        print(f"  File: {config_path}")
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            print(f"  Line: {mark.line + 1}, Column: {mark.column + 1}")
        print(f"  Error: {e}")
        sys.exit(2)

    # Validate configuration
    is_valid, errors = validate_config(config)
    if not is_valid:
        print(f"ERROR: Invalid configuration in {config_path}")
        for error in errors:
            print(f"  {error}")
        sys.exit(2)

    return config


def validate_config(config: dict) -> tuple[bool, list[str]]:
    """
    Validate monitoring configuration structure and regex patterns.

    Checks:
    - Required top-level keys exist
    - All patterns compile as valid regex

    Args:
        config: Parsed configuration dict

    Returns:
        tuple: (is_valid: bool, errors: list[str])
    """
    errors = []

    if config is None:
        return (False, ["Configuration is empty"])

    # Check required sections
    required_sections = ['learn', 'regulatory']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    # Validate learn patterns
    if 'learn' in config:
        learn = config['learn']
        for tier in ['critical_patterns', 'high_patterns', 'noise_patterns']:
            if tier in learn:
                for i, entry in enumerate(learn[tier]):
                    if 'pattern' not in entry:
                        errors.append(f"learn.{tier}[{i}]: missing 'pattern' key")
                    else:
                        pattern = entry['pattern']
                        try:
                            re.compile(pattern)
                        except re.error as e:
                            errors.append(
                                f"Invalid regex pattern in config\n"
                                f"    Location: learn.{tier}[{i}].pattern\n"
                                f"    Value: '{pattern}'\n"
                                f"    Error: {e}"
                            )

    # Validate regulatory patterns
    if 'regulatory' in config:
        regulatory = config['regulatory']
        for tier in ['critical_patterns', 'high_patterns', 'medium_patterns']:
            if tier in regulatory:
                for i, entry in enumerate(regulatory[tier]):
                    if 'pattern' not in entry:
                        errors.append(f"regulatory.{tier}[{i}]: missing 'pattern' key")
                    else:
                        pattern = entry['pattern']
                        try:
                            re.compile(pattern)
                        except re.error as e:
                            errors.append(
                                f"Invalid regex pattern in config\n"
                                f"    Location: regulatory.{tier}[{i}].pattern\n"
                                f"    Value: '{pattern}'\n"
                                f"    Error: {e}"
                            )

    # Validate keyword_control_map structure
    if 'keyword_control_map' in config:
        for i, entry in enumerate(config['keyword_control_map']):
            if 'keyword' not in entry:
                errors.append(f"keyword_control_map[{i}]: missing 'keyword' key")
            if 'controls' not in entry:
                errors.append(f"keyword_control_map[{i}]: missing 'controls' key")
            elif not isinstance(entry['controls'], list):
                errors.append(f"keyword_control_map[{i}].controls: must be a list")

    return (len(errors) == 0, errors)


# === Module Exports ===
__all__ = [
    # Configuration loading
    'load_monitoring_config',
    'validate_config',
    'DEFAULT_CONFIG_PATH',
    # HTTP fetching
    'fetch_page',
    # Content processing
    'normalize_content',
    'compute_hash',
    # Change classification
    'classify_change',
    'CLASSIFICATION_CRITICAL',
    'CLASSIFICATION_HIGH',
    'CLASSIFICATION_MEDIUM',
    'CLASSIFICATION_NOISE',
    # Impact mapping
    'find_affected_controls',
    'format_change_summary',
    # State management
    'load_state',
    'save_state_atomic',
    'get_source_state',
    'set_source_state',
    # Report generation
    'generate_report_header',
    'generate_executive_summary',
    'write_report',
]
