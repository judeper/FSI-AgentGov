#!/usr/bin/env python3
"""
Regulatory Monitoring Source Adapter for FSI-AgentGov

Monitors regulatory changes from Federal Register API and FINRA notices page
that may require updates to the FSI-AgentGov framework. This is a source
adapter for the unified monitoring framework - it uses shared utilities from
monitoring_shared.py.

Sources:
- Federal Register API (SEC, CFTC, OCC, Federal Reserve)
- FINRA Regulatory Notices (HTML scraping)

Usage:
    python scripts/regulatory_monitor.py [--dry-run] [--limit N] [--verbose] [--source SOURCE]

Exit Codes:
    0 - No new regulatory items detected
    1 - New regulatory items detected (triggers PR in CI)
    2 - Error during execution

Environment Variables:
    REGULATORY_MONITOR_DEBUG=1  - Enable debug output
"""

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Import shared monitoring framework
from monitoring_shared import (
    fetch_page,
    compute_hash,
    load_state,
    save_state_atomic,
    get_source_state,
    set_source_state,
    generate_report_header,
    generate_executive_summary,
    format_change_summary,
    write_report,
    CLASSIFICATION_CRITICAL,
    CLASSIFICATION_HIGH,
    CLASSIFICATION_MEDIUM,
    CLASSIFICATION_NOISE,
)

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install with: pip install requests beautifulsoup4")
    sys.exit(2)

# === Configuration ===
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'
REPORTS_DIR = PROJECT_ROOT / 'reports' / 'monitoring'
STATE_FILE = DATA_DIR / 'monitor-state.json'

# Source keys for unified state file
SOURCE_KEY_FEDERAL_REGISTER = "regulatory-federal-register"
SOURCE_KEY_FINRA = "regulatory-finra"

# Federal Register API configuration
FEDERAL_REGISTER_API_BASE = "https://www.federalregister.gov/api/v1"
FEDERAL_REGISTER_AGENCIES = [
    'securities-and-exchange-commission',  # SEC
    'commodity-futures-trading-commission',  # CFTC
    'comptroller-of-the-currency',  # OCC
    'federal-reserve-system',  # Federal Reserve / Fed SR 11-7
]
FEDERAL_REGISTER_DOC_TYPES = ['RULE', 'PRORULE', 'NOTICE']

# FINRA notices page
FINRA_NOTICES_URL = "https://www.finra.org/rules-guidance/notices"

# Keyword-to-control mapping for actionable suggestions
KEYWORD_CONTROL_MAP = {
    'supervision': ['2.12', '2.18'],
    'recordkeeping': ['1.7', '1.10'],
    'retention': ['1.7', '1.10'],
    'data loss prevention': ['1.3', '1.5'],
    'dlp': ['1.3', '1.5'],
    'audit': ['1.7', '3.1', '3.2'],
    'access control': ['1.1', '1.2', '1.11'],
    'encryption': ['1.14', '1.15'],
    'risk management': ['2.6', '2.7'],
    'incident': ['2.14', '2.15'],
    'disaster recovery': ['2.16', '2.17'],
    'information barrier': ['1.22', '1.23'],
    'communication': ['1.10', '2.18', '2.19'],
    'ai': ['2.6', '2.12', '3.8'],
    'artificial intelligence': ['2.6', '2.12', '3.8'],
    'machine learning': ['2.6', '2.12'],
    'model risk': ['2.6'],
    'chatbot': ['2.6', '2.12'],
    'generative': ['2.6', '2.12'],
    'automated advice': ['2.6', '2.12'],
    'broker-dealer': ['1.10', '2.18'],
    'investment adviser': ['1.10', '2.18'],
    'cybersecurity': ['1.14', '2.6', '2.14'],
    'data protection': ['1.3', '1.14', '1.15'],
    'privacy': ['1.3', '1.14', '1.15'],
    'compliance': ['2.6', '3.1', '3.2'],
}

# Configure logging
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if os.environ.get("REGULATORY_MONITOR_DEBUG") else (
        logging.INFO if verbose else logging.WARNING
    )

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)


logger = logging.getLogger(__name__)


@dataclass
class RegulatoryItem:
    """Represents a regulatory document or notice."""
    source: str  # 'Federal Register' or 'FINRA'
    agency: str  # 'SEC', 'CFTC', 'OCC', 'Federal Reserve', 'FINRA'
    title: str
    url: str
    publication_date: str  # ISO format YYYY-MM-DD
    doc_type: Optional[str] = None  # 'RULE', 'PRORULE', 'NOTICE' (Federal Register only)
    abstract: str = ""
    document_id: str = ""  # Federal Register document number or FINRA URL
    classification: str = CLASSIFICATION_NOISE
    classification_reason: str = ""
    affected_controls: list = None

    def __post_init__(self):
        if self.affected_controls is None:
            self.affected_controls = []


def classify_regulatory_relevance(title: str, abstract: str) -> tuple[str, str]:
    """
    Classify regulatory item for FSI AI agent governance relevance.

    Uses the unified 4-tier system (CRITICAL/HIGH/MEDIUM/NOISE) for consistency
    with Learn Monitor.

    Returns:
        tuple: (tier, reason)
    """
    # Handle None values
    title = title or ""
    abstract = abstract or ""
    combined = f"{title.lower()} {abstract.lower()}"

    # CRITICAL: Directly mentions AI agents, copilot, or automated advice in FSI context
    critical_patterns = [
        r'\bai\s+agent',
        r'\bagent\s+ai',
        r'\bcopilot',
        r'\bautomated\s+advice',
        r'\bautomated\s+investment\s+advice',
        r'\brobo-advisor',
        r'\brobo\s+advisor',
    ]
    for pattern in critical_patterns:
        if re.search(pattern, combined):
            return (CLASSIFICATION_CRITICAL, f"Directly mentions AI agents/copilot in regulatory context")

    # HIGH: AI, ML, automation terms + FSI-specific requirements
    high_patterns = [
        (r'\bartificial\s+intelligence', "References artificial intelligence"),
        (r'\bmachine\s+learning', "References machine learning"),
        (r'\bllm\b', "References large language models"),
        (r'\bgenerative\s+ai', "References generative AI"),
        (r'\bchatbot', "References chatbots"),
        (r'\bautomation', "References automation in FSI context"),
        (r'\bsupervision.*(?:electronic|automated|technology)', "References supervision of automated systems"),
        (r'\bfinra\s+3110', "References FINRA 3110 (supervision)"),
        (r'\bfinra\s+4511', "References FINRA 4511 (recordkeeping)"),
        (r'\bsec\s+17a-[34]', "References SEC 17a-3 or 17a-4 (recordkeeping)"),
        (r'\brecordkeeping.*(?:electronic|automated)', "References electronic recordkeeping"),
        (r'\bmodel\s+risk\s+management', "References model risk management"),
    ]
    for pattern, reason in high_patterns:
        if re.search(pattern, combined):
            return (CLASSIFICATION_HIGH, reason)

    # MEDIUM: General FSI regulations that may indirectly affect AI agents
    medium_patterns = [
        (r'\bbroker-dealer', "Broker-dealer regulation (may affect AI agent deployments)"),
        (r'\binvestment\s+adviser', "Investment adviser regulation (may affect AI agent deployments)"),
        (r'\bcustomer\s+communication', "Customer communication rules (affects AI agent outputs)"),
        (r'\bcybersecurity', "Cybersecurity requirements (affects AI agent security)"),
        (r'\bdata\s+protection', "Data protection requirements"),
        (r'\bprivacy', "Privacy requirements"),
        (r'\bcompliance\s+program', "Compliance program requirements"),
        (r'\baudit\s+trail', "Audit trail requirements"),
        (r'\binformation\s+barrier', "Information barriers (affects AI agent data access)"),
    ]
    for pattern, reason in medium_patterns:
        if re.search(pattern, combined):
            return (CLASSIFICATION_MEDIUM, reason)

    # NOISE: Everything else (general regulatory items with no FSI/AI relevance)
    return (CLASSIFICATION_NOISE, "No FSI AI agent governance relevance detected")


def find_affected_controls_by_keywords(title: str, abstract: str) -> list[str]:
    """
    Find potentially affected controls based on keyword matching.

    Returns:
        list: Control IDs (e.g., ['1.3', '1.5', '2.6'])
    """
    # Handle None values
    title = title or ""
    abstract = abstract or ""
    combined = f"{title.lower()} {abstract.lower()}"
    affected = set()

    for keyword, controls in KEYWORD_CONTROL_MAP.items():
        # Use word boundary matching to avoid partial matches
        pattern = rf'\b{re.escape(keyword)}\b'
        if re.search(pattern, combined, re.IGNORECASE):
            affected.update(controls)

    return sorted(list(affected))


def fetch_federal_register_documents(session: requests.Session, since_date: str, limit: Optional[int] = None) -> list[RegulatoryItem]:
    """
    Fetch documents from Federal Register API.

    Args:
        session: requests.Session instance
        since_date: ISO date string (YYYY-MM-DD) - fetch documents published on or after this date
        limit: Maximum documents to fetch (for testing)

    Returns:
        list[RegulatoryItem]: New regulatory items
    """
    items = []

    # Build query parameters
    params = {
        'conditions[agencies][]': FEDERAL_REGISTER_AGENCIES,
        'conditions[type][]': FEDERAL_REGISTER_DOC_TYPES,
        'conditions[publication_date][gte]': since_date,
        'per_page': 100,  # API max is 1000
        'order': 'newest',
        'fields[]': ['document_number', 'title', 'abstract', 'publication_date', 'type', 'html_url', 'agencies'],
    }

    try:
        logger.info(f"Querying Federal Register API for documents since {since_date}...")
        response = session.get(
            f"{FEDERAL_REGISTER_API_BASE}/documents.json",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        documents = data.get('results', [])
        logger.info(f"Federal Register API returned {len(documents)} documents")

        # Apply limit if specified
        if limit:
            documents = documents[:limit]
            logger.info(f"Limited to {limit} documents for testing")

        for doc in documents:
            # Extract agency names
            agencies = [agency.get('name', 'Unknown') for agency in doc.get('agencies', [])]
            agency_name = ', '.join(agencies) if agencies else 'Unknown'

            # Map to canonical short names
            if 'Securities and Exchange Commission' in agency_name:
                agency_short = 'SEC'
            elif 'Commodity Futures Trading Commission' in agency_name:
                agency_short = 'CFTC'
            elif 'Comptroller of the Currency' in agency_name:
                agency_short = 'OCC'
            elif 'Federal Reserve' in agency_name:
                agency_short = 'Federal Reserve'
            else:
                agency_short = agency_name

            title = doc.get('title', 'Untitled')
            abstract = doc.get('abstract', '')

            # Classify for FSI AI agent governance relevance
            tier, reason = classify_regulatory_relevance(title, abstract)

            # Find affected controls by keywords
            affected_controls = find_affected_controls_by_keywords(title, abstract)

            item = RegulatoryItem(
                source='Federal Register',
                agency=agency_short,
                title=title,
                url=doc.get('html_url', ''),
                publication_date=doc.get('publication_date', ''),
                doc_type=doc.get('type', ''),
                abstract=abstract,
                document_id=doc.get('document_number', ''),
                classification=tier,
                classification_reason=reason,
                affected_controls=affected_controls,
            )
            items.append(item)

    except requests.RequestException as e:
        logger.error(f"Federal Register API error: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Federal Register API response parsing error: {e}")

    return items


def fetch_finra_notices(session: requests.Session, limit: Optional[int] = None) -> list[RegulatoryItem]:
    """
    Scrape FINRA regulatory notices page.

    Args:
        session: requests.Session instance
        limit: Maximum notices to fetch (for testing)

    Returns:
        list[RegulatoryItem]: FINRA notices
    """
    items = []

    try:
        logger.info(f"Fetching FINRA notices from {FINRA_NOTICES_URL}...")
        result = fetch_page(FINRA_NOTICES_URL, session)

        if result['status_code'] != 200:
            logger.error(f"FINRA notices page returned status {result['status_code']}")
            return items

        soup = BeautifulSoup(result['content'], 'html.parser')

        # FINRA notices are in a table with class 'notices-table' or similar
        # The structure may vary, so we look for common patterns
        notice_links = []

        # Strategy 1: Look for article elements with notice links
        for article in soup.find_all(['article', 'div'], class_=re.compile(r'notice|regulatory')):
            link = article.find('a', href=re.compile(r'/rules-guidance/notices/'))
            if link:
                notice_links.append(link)

        # Strategy 2: Look for all links to /rules-guidance/notices/
        if not notice_links:
            notice_links = soup.find_all('a', href=re.compile(r'/rules-guidance/notices/\d{2}-\d{2}'))

        logger.info(f"Found {len(notice_links)} FINRA notice links")

        # Apply limit if specified
        if limit:
            notice_links = notice_links[:limit]
            logger.info(f"Limited to {limit} notices for testing")

        for link in notice_links:
            title = link.get_text(strip=True)
            url = link.get('href', '')

            # Make URL absolute
            if url.startswith('/'):
                url = f"https://www.finra.org{url}"

            # Extract date from notice ID (e.g., /notices/24-15 → 2024)
            # Note: This is a heuristic - actual publication date requires fetching the notice page
            match = re.search(r'/notices/(\d{2})-(\d{2})', url)
            if match:
                year_short = match.group(1)
                notice_num = match.group(2)
                year = f"20{year_short}"
                # Assume January 1 for notices without specific dates
                publication_date = f"{year}-01-01"
                document_id = f"FINRA {year_short}-{notice_num}"
            else:
                publication_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                document_id = url

            # Classify for FSI AI agent governance relevance
            # For FINRA notices, we don't have abstracts without fetching individual pages
            tier, reason = classify_regulatory_relevance(title, "")

            # Find affected controls by keywords
            affected_controls = find_affected_controls_by_keywords(title, "")

            item = RegulatoryItem(
                source='FINRA',
                agency='FINRA',
                title=title,
                url=url,
                publication_date=publication_date,
                doc_type='NOTICE',
                abstract="",
                document_id=document_id,
                classification=tier,
                classification_reason=reason,
                affected_controls=affected_controls,
            )
            items.append(item)

    except Exception as e:
        logger.error(f"FINRA notices scraping error: {e}")

    return items


def check_for_new_items(source_key: str, items: list[RegulatoryItem], source_state: dict) -> list[RegulatoryItem]:
    """
    Compare fetched items against source state to find new items.

    Args:
        source_key: Source key in unified state file
        items: List of fetched regulatory items
        source_state: Source-specific state dict

    Returns:
        list[RegulatoryItem]: New items not in state
    """
    new_items = []
    existing_entries = source_state.get('entries', {})

    for item in items:
        # Use document_id or URL as the key
        entry_key = item.document_id if item.document_id else item.url

        # Compute hash of the item content
        content_to_hash = f"{item.title}|{item.abstract}|{item.publication_date}"
        content_hash = compute_hash(content_to_hash)

        # Check if this is a new item or changed item
        if entry_key not in existing_entries:
            logger.info(f"  New item: {item.title[:60]}... ({item.agency})")
            new_items.append(item)
        elif existing_entries[entry_key] != content_hash:
            logger.info(f"  Updated item: {item.title[:60]}... ({item.agency})")
            new_items.append(item)

    return new_items


def update_source_state(source_key: str, items: list[RegulatoryItem], state: dict) -> None:
    """
    Update source state with new item hashes.

    Args:
        source_key: Source key in unified state file
        items: List of regulatory items to add to state
        state: Full state dict (modified in place)
    """
    source_state = get_source_state(state, source_key)
    entries = source_state.get('entries', {})

    for item in items:
        entry_key = item.document_id if item.document_id else item.url
        content_to_hash = f"{item.title}|{item.abstract}|{item.publication_date}"
        entries[entry_key] = compute_hash(content_to_hash)

    source_state['entries'] = entries
    source_state['last_run'] = datetime.now(timezone.utc).isoformat()

    set_source_state(state, source_key, source_state)


def generate_regulatory_report(
    all_new_items: list[RegulatoryItem],
    report_path: Path
) -> None:
    """
    Generate regulatory change report using shared report format helpers.

    Args:
        all_new_items: All new regulatory items from all sources
        report_path: Path to write report
    """
    # Categorize by classification tier
    critical_items = [item for item in all_new_items if item.classification == CLASSIFICATION_CRITICAL]
    high_items = [item for item in all_new_items if item.classification == CLASSIFICATION_HIGH]
    medium_items = [item for item in all_new_items if item.classification == CLASSIFICATION_MEDIUM]
    noise_items = [item for item in all_new_items if item.classification == CLASSIFICATION_NOISE]

    # Build report content
    lines = []

    # Header
    run_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    lines.append(f"# Regulatory Monitor Report - {run_date}\n\n")
    lines.append(generate_report_header(
        title="Regulatory Monitor Report",
        run_date=run_date,
        metadata={
            "New Items": len(all_new_items),
            "Sources": "Federal Register (SEC, CFTC, OCC, Federal Reserve) + FINRA Regulatory Notices"
        }
    ))

    # Executive summary
    lines.append(generate_executive_summary({
        'CRITICAL': len(critical_items),
        'HIGH': len(high_items),
        'MEDIUM': len(medium_items),
        'NOISE': len(noise_items),
    }))

    # Summary table (for CRITICAL + HIGH only, for quick scanning)
    priority_items = critical_items + high_items
    if priority_items:
        lines.append("## Summary (Quick Scan)\n")
        lines.append("| # | Source | Agency | Classification | Affected Controls | Action |\n")
        lines.append("|---|--------|--------|----------------|-------------------|--------|\n")

        for i, item in enumerate(priority_items, 1):
            # Shorten URL for table
            url_short = item.title[:40] + "..." if len(item.title) > 40 else item.title
            controls = ", ".join(item.affected_controls) if item.affected_controls else "None identified"
            action = "Review and update framework" if item.classification == CLASSIFICATION_CRITICAL else "Review"

            lines.append(f"| {i} | {item.source} | {item.agency} | {item.classification} | {controls} | {action} |\n")

        lines.append("\n")

    # CRITICAL items (detailed)
    if critical_items:
        lines.append("## CRITICAL Items\n")
        lines.append("These regulatory changes directly mention AI agents, copilot, or automated advice in FSI context.\n\n")

        for i, item in enumerate(critical_items, 1):
            lines.append(f"### {i}. [{item.title}]({item.url})\n\n")
            lines.append(f"- **Source:** {item.agency} via {item.source}\n")
            lines.append(f"- **Published:** {item.publication_date}\n")
            if item.doc_type:
                lines.append(f"- **Type:** {item.doc_type}\n")
            lines.append(f"- **Classification:** {item.classification} — {item.classification_reason}\n")

            if item.abstract:
                lines.append(f"- **Abstract:** {item.abstract[:500]}{'...' if len(item.abstract) > 500 else ''}\n")

            if item.affected_controls:
                lines.append(f"- **Potentially Affected Controls:**\n")
                for control in item.affected_controls:
                    lines.append(f"  - Control {control}\n")

            lines.append("\n")

    # HIGH items (detailed)
    if high_items:
        lines.append("## HIGH Priority Items\n")
        lines.append("These regulatory changes reference AI, ML, automation, or FSI-specific requirements relevant to AI agent governance.\n\n")

        for i, item in enumerate(high_items, 1):
            lines.append(f"### {i}. [{item.title}]({item.url})\n\n")
            lines.append(f"- **Source:** {item.agency} via {item.source}\n")
            lines.append(f"- **Published:** {item.publication_date}\n")
            if item.doc_type:
                lines.append(f"- **Type:** {item.doc_type}\n")
            lines.append(f"- **Classification:** {item.classification} — {item.classification_reason}\n")

            if item.abstract:
                lines.append(f"- **Abstract:** {item.abstract[:300]}{'...' if len(item.abstract) > 300 else ''}\n")

            if item.affected_controls:
                lines.append(f"- **Potentially Affected Controls:** {', '.join(item.affected_controls)}\n")

            lines.append("\n")

    # MEDIUM items (abbreviated)
    if medium_items:
        lines.append("## MEDIUM Priority Items\n")
        lines.append("General FSI regulations that may indirectly affect AI agent deployments.\n\n")

        for item in medium_items:
            lines.append(f"- [{item.title}]({item.url}) ({item.agency}, {item.publication_date})\n")

        lines.append("\n")

    # NOISE items (list only)
    if noise_items:
        lines.append("## NOISE Items\n")
        lines.append("Regulatory items with no FSI AI agent governance relevance.\n\n")

        for item in noise_items:
            lines.append(f"- [{item.title}]({item.url}) ({item.agency})\n")

        lines.append("\n")

    # Write report
    content = "".join(lines)
    write_report(content, REPORTS_DIR, report_path.name)
    logger.info(f"Report written to {report_path}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Monitor regulatory changes from Federal Register and FINRA"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Fetch and analyze without updating state file"
    )
    parser.add_argument(
        '--limit',
        type=int,
        help="Limit number of items per source (for testing)"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Enable verbose output"
    )
    parser.add_argument(
        '--source',
        choices=['federal-register', 'finra', 'all'],
        default='all',
        help="Which source(s) to monitor"
    )

    args = parser.parse_args()

    # Setup logging
    global logger
    logger = setup_logging(verbose=args.verbose)

    logger.info("=== Regulatory Monitor ===")
    logger.info(f"Source: {args.source}")
    logger.info(f"Dry run: {args.dry_run}")
    if args.limit:
        logger.info(f"Limit: {args.limit} items per source")

    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load unified state
    state = load_state(STATE_FILE)

    # Create session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'FSI-AgentGov-Regulatory-Monitor/1.0 (https://github.com/judeper/FSI-AgentGov)'
    })

    all_new_items = []

    # Fetch from Federal Register
    if args.source in ['federal-register', 'all']:
        logger.info("\n--- Federal Register ---")
        fed_state = get_source_state(state, SOURCE_KEY_FEDERAL_REGISTER)

        # Determine since_date (last check or 30 days ago)
        since_date = fed_state.get('last_checked')
        if not since_date:
            since_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%d')
            logger.info(f"No prior state, fetching documents from last 30 days")
        else:
            logger.info(f"Fetching documents since {since_date}")

        fed_items = fetch_federal_register_documents(session, since_date, limit=args.limit)
        new_fed_items = check_for_new_items(SOURCE_KEY_FEDERAL_REGISTER, fed_items, fed_state)

        logger.info(f"Federal Register: {len(new_fed_items)} new items")
        all_new_items.extend(new_fed_items)

        # Update state
        if not args.dry_run:
            update_source_state(SOURCE_KEY_FEDERAL_REGISTER, fed_items, state)
            # Update last_checked to today
            fed_state = get_source_state(state, SOURCE_KEY_FEDERAL_REGISTER)
            fed_state['last_checked'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            set_source_state(state, SOURCE_KEY_FEDERAL_REGISTER, fed_state)

    # Fetch from FINRA
    if args.source in ['finra', 'all']:
        logger.info("\n--- FINRA Notices ---")
        finra_state = get_source_state(state, SOURCE_KEY_FINRA)

        finra_items = fetch_finra_notices(session, limit=args.limit)
        new_finra_items = check_for_new_items(SOURCE_KEY_FINRA, finra_items, finra_state)

        logger.info(f"FINRA: {len(new_finra_items)} new items")
        all_new_items.extend(new_finra_items)

        # Update state
        if not args.dry_run:
            update_source_state(SOURCE_KEY_FINRA, finra_items, state)

    # Generate report if new items found
    if all_new_items:
        logger.info(f"\n=== {len(all_new_items)} total new regulatory items detected ===")

        report_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        report_path = REPORTS_DIR / f"regulatory-changes-{report_date}.md"

        generate_regulatory_report(all_new_items, report_path)

        # Save state
        if not args.dry_run:
            save_state_atomic(STATE_FILE, state)
            logger.info(f"State updated: {STATE_FILE}")
        else:
            logger.info("Dry run: state not updated")

        # Exit code 1 indicates new items (triggers PR in CI)
        sys.exit(1)

    else:
        logger.info("\n=== No new regulatory items detected ===")

        # Save state even if no changes (updates last_run timestamps)
        if not args.dry_run:
            save_state_atomic(STATE_FILE, state)

        # Exit code 0 indicates no changes
        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.debug("Traceback:", exc_info=True)
        sys.exit(2)
