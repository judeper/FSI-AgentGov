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

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

# Import shared monitoring framework
from monitoring_shared import (
    CLASSIFICATION_CRITICAL,
    CLASSIFICATION_HIGH,
    CLASSIFICATION_MEDIUM,
    CLASSIFICATION_NOISE,
    DEFAULT_CONFIG_PATH,
    compute_hash,
    fetch_page,
    generate_executive_summary,
    generate_report_header,
    get_source_state,
    load_monitoring_config,
    load_state,
    save_state_atomic,
    set_source_state,
    validate_config,
    write_report,
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

# FINRA notices page
FINRA_NOTICES_URL = "https://www.finra.org/rules-guidance/notices"
FINRA_MAX_PAGES = 100
FINRA_REFETCH_PAGES = 1
FINRA_REFRESH_BATCH_SIZE = 25
FINRA_REQUEST_INTERVAL_SECONDS = 1.00
FINRA_RETRY_BASE_WAIT_SECONDS = 5
FINRA_MAX_RETRY_WAIT_SECONDS = 60
FINRA_MAX_RETRY_ATTEMPTS = 4

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


class FetchResult(list):
    """List-compatible fetch result carrying a fail-closed completeness verdict."""

    def __init__(
        self,
        items=(),
        *,
        complete: bool,
        expected_count: Optional[int] = None,
        pages_fetched: int = 0,
        declared_pages: Optional[int] = None,
        cutoff_page: Optional[int] = None,
        error: Optional[str] = None,
        limited: bool = False,
    ):
        super().__init__(items)
        self.complete = complete
        self.expected_count = expected_count
        self.pages_fetched = pages_fetched
        self.declared_pages = declared_pages
        self.cutoff_page = cutoff_page
        self.error = error
        self.limited = limited


def _complete_result(items: list[RegulatoryItem], **kwargs) -> FetchResult:
    """Build a successful result while retaining list compatibility for callers."""
    return FetchResult(items, complete=True, **kwargs)


def _incomplete_result(items=(), *, error: str, **kwargs) -> FetchResult:
    """Build an incomplete result; callers must not advance source state from it."""
    logger.error(error)
    return FetchResult(items, complete=False, error=error, **kwargs)


def _coerce_fetch_result(value) -> FetchResult:
    """Keep tests and source adapters that return a plain list backward compatible."""
    if isinstance(value, FetchResult):
        return value
    return FetchResult(value or [], complete=True, expected_count=len(value or []))


def _item_content_hash(item: RegulatoryItem) -> str:
    """Hash normalized substantive source content without inventing provenance."""
    if item.substantive_content:
        return compute_hash(item.substantive_content)
    fields = [item.title or "", item.abstract or "", item.publication_date or ""]
    if not any(fields):
        # A URL is still authoritative identity when the source exposes no content.
        return compute_hash(item.url or "")
    return compute_hash("|".join(fields))


def _state_date(source_state: dict) -> Optional[str]:
    """Return an ISO date watermark from source state without fabricating one."""
    for key in ("last_checked", "last_run"):
        value = source_state.get(key)
        if isinstance(value, str) and re.match(r"^\d{4}-\d{2}-\d{2}", value):
            return value[:10]
    return None


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
    substantive_content: str = ""

    def __post_init__(self):
        if self.affected_controls is None:
            self.affected_controls = []


def classify_regulatory_relevance(title: str, abstract: str, config: dict) -> tuple[str, str]:
    """
    Classify regulatory item for FSI AI agent governance relevance.

    Uses the unified 4-tier system (CRITICAL/HIGH/MEDIUM/NOISE) for consistency
    with Learn Monitor. Patterns are loaded from config.

    Args:
        title: Document title
        abstract: Document abstract
        config: Configuration dict with pattern definitions

    Returns:
        tuple: (tier, reason)
    """
    # Handle None values
    title = title or ""
    abstract = abstract or ""
    combined = f"{title.lower()} {abstract.lower()}"

    # Get regulatory patterns from config
    regulatory_config = config.get('regulatory', {})

    # CRITICAL: Directly mentions AI agents, copilot, or automated advice in FSI context
    critical_patterns = [
        (p['pattern'], p['reason'])
        for p in regulatory_config.get('critical_patterns', [])
    ]
    for pattern, reason in critical_patterns:
        if re.search(pattern, combined):
            return (CLASSIFICATION_CRITICAL, reason)

    # HIGH: AI, ML, automation terms + FSI-specific requirements
    high_patterns = [
        (p['pattern'], p['reason'])
        for p in regulatory_config.get('high_patterns', [])
    ]
    for pattern, reason in high_patterns:
        if re.search(pattern, combined):
            return (CLASSIFICATION_HIGH, reason)

    # MEDIUM: General FSI regulations that may indirectly affect AI agents
    medium_patterns = [
        (p['pattern'], p['reason'])
        for p in regulatory_config.get('medium_patterns', [])
    ]
    for pattern, reason in medium_patterns:
        if re.search(pattern, combined):
            return (CLASSIFICATION_MEDIUM, reason)

    # NOISE: Everything else (general regulatory items with no FSI/AI relevance)
    return (CLASSIFICATION_NOISE, "No FSI AI agent governance relevance detected")


def find_affected_controls_by_keywords(title: str, abstract: str, config: dict) -> list[str]:
    """
    Find potentially affected controls based on keyword matching.

    Args:
        title: Document title
        abstract: Document abstract
        config: Configuration dict with keyword_control_map

    Returns:
        list: Control IDs (e.g., ['1.3', '1.5', '2.6'])
    """
    # Handle None values
    title = title or ""
    abstract = abstract or ""
    combined = f"{title.lower()} {abstract.lower()}"
    affected = set()

    # Build keyword map from config
    keyword_map = {
        entry['keyword']: [c['id'] for c in entry['controls']]
        for entry in config.get('keyword_control_map', [])
    }

    for keyword, controls in keyword_map.items():
        # Use word boundary matching to avoid partial matches
        pattern = rf'\b{re.escape(keyword)}\b'
        if re.search(pattern, combined, re.IGNORECASE):
            affected.update(controls)

    return sorted(list(affected))


def fetch_federal_register_documents(
    session: requests.Session,
    since_date: str,
    config: dict,
    limit: Optional[int] = None,
) -> FetchResult:
    """
    Fetch documents from Federal Register API.

    Args:
        session: requests.Session instance
        since_date: ISO date string (YYYY-MM-DD) - fetch documents published on or after this date
        config: Configuration dict with federal_register settings
        limit: Maximum documents to fetch (for testing)

    Returns:
        FetchResult: List-compatible items plus a completeness verdict.
    """
    # Get agencies and doc types from config
    fed_config = config.get('federal_register', {})
    agencies = [a['slug'] for a in fed_config.get('agencies', [])]
    doc_types = fed_config.get('document_types', ['RULE', 'PRORULE', 'NOTICE'])

    # Build agency short name map from config
    agency_short_map = {
        a['slug']: a.get('short_name', a['slug'])
        for a in fed_config.get('agencies', [])
    }

    # Build query parameters
    params = {
        'conditions[agencies][]': agencies,
        'conditions[type][]': doc_types,
        'conditions[publication_date][gte]': since_date,
        'per_page': 100,  # API max is 1000
        'order': 'newest',
        'fields[]': ['document_number', 'title', 'abstract', 'publication_date', 'type', 'html_url', 'agencies'],
    }

    if limit is not None and limit < 0:
        return _incomplete_result(error=f"Federal Register limit must be non-negative, got {limit}")

    items = []
    seen_document_ids = set()
    per_page = 100
    expected_count = None
    pages_fetched = 0

    try:
        logger.info(f"Querying Federal Register API for documents since {since_date}...")
        next_url = f"{FEDERAL_REGISTER_API_BASE}/documents.json"
        next_params = params
        expected_pages = None

        while True:
            response = session.get(next_url, params=next_params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                return _incomplete_result(
                    items,
                    error="Federal Register API returned a non-object response",
                    expected_count=expected_count,
                    pages_fetched=pages_fetched,
                )

            if pages_fetched == 0:
                count = data.get('count')
                if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                    return _incomplete_result(
                        items,
                        error="Federal Register API response omitted a valid result count",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                expected_count = count

                total_pages = data.get('total_pages')
                if total_pages is not None and (
                    not isinstance(total_pages, int)
                    or isinstance(total_pages, bool)
                    or total_pages < 0
                ):
                    return _incomplete_result(
                        items,
                        error="Federal Register response contained invalid total_pages",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                if count == 0:
                    # The live API legitimately returns count=0, total_pages=null,
                    # results=null. A zero-result query still has one response to
                    # validate, while total_pages=1 would be contradictory.
                    if total_pages not in (None, 0):
                        return _incomplete_result(
                            items,
                            error="Federal Register zero-result response declared pages",
                            expected_count=expected_count,
                            pages_fetched=pages_fetched,
                        )
                    expected_pages = 1
                elif total_pages is not None:
                    expected_pages = total_pages
                else:
                    # Some valid zero-result responses omit total_pages; infer pages
                    # only when a non-zero count makes the expectation unambiguous.
                    expected_pages = math.ceil(count / per_page)
                if count > 0 and expected_pages == 0:
                    return _incomplete_result(
                        items,
                        error="Federal Register response declared pages=0 for non-zero results",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
            else:
                if data.get('count') is not None and data.get('count') != expected_count:
                    return _incomplete_result(
                        items,
                        error="Federal Register page count changed during pagination",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                page_total_pages = data.get('total_pages')
                if page_total_pages is not None and (
                    not isinstance(page_total_pages, int)
                    or isinstance(page_total_pages, bool)
                    or page_total_pages < 0
                ):
                    return _incomplete_result(
                        items,
                        error="Federal Register page contained invalid total_pages",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                if page_total_pages is not None:
                    expected_total_pages = 0 if expected_count == 0 else expected_pages
                    if page_total_pages != expected_total_pages:
                        return _incomplete_result(
                            items,
                            error="Federal Register total_pages changed during pagination",
                            expected_count=expected_count,
                            pages_fetched=pages_fetched,
                        )

            raw_documents = data.get('results', [])
            if raw_documents is None and expected_count == 0:
                raw_documents = []
            if not isinstance(raw_documents, list):
                return _incomplete_result(
                    items,
                    error="Federal Register API returned malformed results",
                    expected_count=expected_count,
                    pages_fetched=pages_fetched,
                )

            pages_fetched += 1
            logger.info(
                f"Federal Register API page {pages_fetched}"
                f"{f'/{expected_pages}' if expected_pages is not None else ''}: "
                f"{len(raw_documents)} documents"
            )

            if expected_count == 0 and raw_documents:
                return _incomplete_result(
                    items,
                    error="Federal Register reported zero results but returned documents",
                    expected_count=expected_count,
                    pages_fetched=pages_fetched,
                )

            for doc in raw_documents:
                if not isinstance(doc, dict):
                    return _incomplete_result(
                        items,
                        error="Federal Register page contained a non-object document",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                document_id = doc.get('document_number')
                if not isinstance(document_id, str) or not document_id.strip():
                    return _incomplete_result(
                        items,
                        error="Federal Register document omitted document_number",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                if document_id in seen_document_ids:
                    return _incomplete_result(
                        items,
                        error=f"Federal Register pagination overlap/conflict for {document_id}",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                seen_document_ids.add(document_id)

            # Extract agency names
                doc_agencies = doc.get('agencies', [])
                if not isinstance(doc_agencies, list):
                    return _incomplete_result(
                        items,
                        error=f"Federal Register document {document_id} has malformed agencies",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                agency_slugs = [agency.get('slug', '') for agency in doc_agencies if isinstance(agency, dict)]
                agency_names = [agency.get('name', 'Unknown') for agency in doc_agencies if isinstance(agency, dict)]
                agency_name = ', '.join(agency_names) if agency_names else 'Unknown'

                # Map to canonical short names using config
                agency_short = 'Unknown'
                for slug in agency_slugs:
                    if slug in agency_short_map:
                        agency_short = agency_short_map[slug]
                        break
                if agency_short == 'Unknown':
                    agency_short = agency_name

                title = doc.get('title') or 'Untitled'
                abstract = doc.get('abstract') or ''

                # Classify for FSI AI agent governance relevance
                tier, reason = classify_regulatory_relevance(title, abstract, config)

                # Find affected controls by keywords
                affected_controls = find_affected_controls_by_keywords(title, abstract, config)

                item = RegulatoryItem(
                    source='Federal Register',
                    agency=agency_short,
                    title=title,
                    url=doc.get('html_url') or '',
                    publication_date=doc.get('publication_date') or '',
                    doc_type=doc.get('type') or '',
                    abstract=abstract,
                    document_id=document_id,
                    classification=tier,
                    classification_reason=reason,
                    affected_controls=affected_controls,
                )
                items.append(item)

            next_url = data.get('next_page_url')
            if next_url is not None and not isinstance(next_url, str):
                return _incomplete_result(
                    items,
                    error="Federal Register response contained a malformed next_page_url",
                    expected_count=expected_count,
                    pages_fetched=pages_fetched,
                )
            if expected_count == 0:
                if next_url:
                    return _incomplete_result(
                        items,
                        error="Federal Register zero-result response unexpectedly paginated",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                break
            if expected_pages is not None and pages_fetched > expected_pages:
                return _incomplete_result(
                    items,
                    error="Federal Register returned more pages than declared",
                    expected_count=expected_count,
                    pages_fetched=pages_fetched,
                )
            if next_url:
                if expected_pages is not None and pages_fetched >= expected_pages:
                    return _incomplete_result(
                        items,
                        error="Federal Register returned an unexpected extra page",
                        expected_count=expected_count,
                        pages_fetched=pages_fetched,
                    )
                next_params = None
                next_url = urljoin(f"{FEDERAL_REGISTER_API_BASE}/", next_url)
                continue
            break

        if expected_pages is None or pages_fetched != expected_pages:
                return _incomplete_result(
                    items,
                    error=(
                        "Federal Register pagination incomplete: "
                        f"declared {expected_pages} page(s), fetched {pages_fetched}"
                    ),
                    expected_count=expected_count,
                    pages_fetched=pages_fetched,
                )

        if expected_count is None or len(items) != expected_count:
            return _incomplete_result(
                items,
                error=(
                    "Federal Register pagination incomplete: "
                    f"expected {expected_count} unique documents, fetched {len(items)}"
                ),
                expected_count=expected_count,
                pages_fetched=pages_fetched,
            )

        if limit is not None:
            logger.info(f"Limited to {limit} documents for testing; state will not advance")
            return _incomplete_result(
                items[:limit],
                error="Federal Register fetch was explicitly limited",
                expected_count=expected_count,
                pages_fetched=pages_fetched,
                limited=True,
            )

        return _complete_result(
            items,
            expected_count=expected_count,
            pages_fetched=pages_fetched,
        )

    except requests.RequestException as e:
        return _incomplete_result(
            items,
            error=f"Federal Register API error: {e}",
            expected_count=expected_count,
            pages_fetched=pages_fetched,
        )
    except (json.JSONDecodeError, ValueError) as e:
        return _incomplete_result(
            items,
            error=f"Federal Register API response parsing error: {e}",
            expected_count=expected_count,
            pages_fetched=pages_fetched,
        )


def _extract_finra_publication_date(soup: BeautifulSoup) -> str:
    """Read FINRA's official datetime field; return empty when the source omits it."""
    official_field = soup.select_one('.field--name-field-core-official-dt')
    if not official_field:
        return ""

    time_tag = official_field.select_one('time[datetime]')
    raw_value = time_tag.get('datetime', '') if time_tag else ''
    if raw_value:
        match = re.match(r'^(\d{4}-\d{2}-\d{2})', raw_value)
        if match:
            return match.group(1)

    visible = official_field.select_one('.field__item')
    if visible:
        for fmt in ('%B %d, %Y', '%b %d, %Y'):
            try:
                return datetime.strptime(visible.get_text(' ', strip=True), fmt).date().isoformat()
            except ValueError:
                continue
    return ""


def _extract_listing_date(link) -> str:
    """Read the optional authoritative date rendered beside a FINRA listing link."""
    row = link.find_parent('tr')
    if row is None:
        return ""
    time_tag = row.select_one('time[datetime]')
    if time_tag:
        match = re.match(r'^(\d{4}-\d{2}-\d{2})', time_tag.get('datetime', ''))
        if match:
            return match.group(1)
    return ""


def _extract_finra_summary(soup: BeautifulSoup) -> str:
    """Extract only the authoritative FINRA Summary section, not page chrome."""
    summary_heading = next(
        (
            heading
            for heading in soup.find_all(['h2', 'h3'])
            if heading.get_text(' ', strip=True).casefold() == 'summary'
        ),
        None,
    )
    if summary_heading is None:
        return ""

    parts = []
    for sibling in summary_heading.next_siblings:
        if getattr(sibling, 'name', None) in ('h2', 'h3'):
            break
        if getattr(sibling, 'name', None):
            text = ' '.join(sibling.get_text(' ', strip=True).split())
            if text:
                parts.append(text)
    return ' '.join(parts)


_FINRA_TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "source",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


def _decode_cloudflare_email_token(token: str) -> Optional[str]:
    """Decode Cloudflare's XOR-obfuscated email token when it is well formed."""
    if not re.fullmatch(r"[0-9a-fA-F]{4,}", token or "") or len(token) % 2:
        return None
    try:
        key = int(token[:2], 16)
        encoded = bytes.fromhex(token[2:])
    except (UnicodeDecodeError, ValueError):
        return None
    return bytes(value ^ key for value in encoded).decode("utf-8", errors="strict")


def _normalize_finra_date_values(text: str) -> str:
    """Keep substantive dates while making equivalent display formats stable."""
    month_date = re.compile(
        r"\b(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(\d{1,2}),\s+(\d{4})\b",
        re.IGNORECASE,
    )
    numeric_date = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")

    def month_replacement(match: re.Match) -> str:
        try:
            value = datetime.strptime(
                f"{match.group(1)} {match.group(2)} {match.group(3)}",
                "%B %d %Y",
            )
        except ValueError:
            return match.group(0)
        return value.date().isoformat()

    def numeric_replacement(match: re.Match) -> str:
        try:
            value = datetime.strptime(
                f"{match.group(1)}/{match.group(2)}/{match.group(3)}",
                "%m/%d/%Y",
            )
        except ValueError:
            return match.group(0)
        return value.date().isoformat()

    text = month_date.sub(month_replacement, text)
    return numeric_date.sub(numeric_replacement, text)


def _canonicalize_finra_href(href: str, base_url: str) -> str:
    """Retain authoritative link targets while removing tracking-only noise."""
    absolute = urljoin(base_url, href)
    parsed = urlparse(absolute)
    if (
        parsed.path.rstrip("/") == "/cdn-cgi/l/email-protection"
        and parsed.fragment
    ):
        email = _decode_cloudflare_email_token(parsed.fragment)
        if email:
            return f"mailto:{email.strip().casefold()}"
    query = parse_qs(parsed.query, keep_blank_values=True)
    filtered = [
        (key, value)
        for key, values in query.items()
        if key.casefold() not in _FINRA_TRACKING_QUERY_KEYS
        for value in values
    ]
    filtered.sort()
    return parsed._replace(
        scheme=parsed.scheme.casefold(),
        netloc=parsed.netloc.casefold(),
        query=urlencode(filtered),
    ).geturl()


def _canonicalize_finra_fragment(node, base_url: str) -> str:
    """Canonicalize one authoritative FINRA fragment without page chrome."""
    fragment = BeautifulSoup(str(node), 'html.parser')
    for tag in fragment.find_all(
        ['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']
    ):
        tag.decompose()
    for selector in (
        '.breadcrumb',
        '.pagination',
        '.pager',
        '#comments',
        '#comments-tab',
        '#block-views-block-notice-comments-block-1',
        '[id*="comment" i]',
        '[class*="comment" i]',
    ):
        for element in fragment.select(selector):
            element.decompose()

    for link in fragment.find_all('a', href=True):
        label = ' '.join(link.get_text(' ', strip=True).split())
        target = _canonicalize_finra_href(link['href'], base_url)
        replacement = f"{label} [href:{target}]" if label else f"[href:{target}]"
        link.replace_with(replacement)

    text = ' '.join(fragment.get_text(' ', strip=True).split())
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    return _normalize_finra_date_values(text)


def _extract_finra_substantive_content(
    soup: BeautifulSoup,
    base_url: str = FINRA_NOTICES_URL,
) -> str:
    """Canonicalize only the authoritative notice, metadata, and attachments.

    FINRA renders public comments in a sibling ``#comments`` tab.  Starting
    from ``main`` accidentally included that mutable public content, so the
    primary root is the ``#notice`` tab and the fallback is a narrowly scoped
    notice body used by older templates and test fixtures.
    """
    notice = soup.select_one('#notice')
    body = soup.select_one('.field--name-body')
    content = notice or body or soup.select_one('.notice-body, .notice-content')
    if content is None:
        return ""

    parts = []
    title_node = soup.select_one('.field--name-field-notice-title-tx') or soup.find('h1')
    if title_node:
        title = _canonicalize_finra_fragment(title_node, base_url)
        if title:
            parts.append(title)

    publication_date = _extract_finra_publication_date(soup)
    official_date_node = soup.select_one('.field--name-field-core-official-dt')
    if official_date_node:
        date_text = _canonicalize_finra_fragment(official_date_node, base_url)
        if publication_date:
            date_text = f"Published Date: {publication_date}"
        if date_text:
            parts.append(date_text)

    subtitle_node = soup.select_one('.field--name-field-notice-subtitle-tx')
    if subtitle_node:
        subtitle = _canonicalize_finra_fragment(subtitle_node, base_url)
        if subtitle:
            parts.append(subtitle)

    notice_text = _canonicalize_finra_fragment(content, base_url)
    if notice_text:
        parts.append(notice_text)

    # These authoritative download/attachment targets live in the notice
    # sidebar, outside #notice, while the public comments tab is excluded.
    for selector in ('#block-noticedocument', '#block-noticeattachment'):
        attachment = soup.select_one(selector)
        if attachment:
            attachment_text = _canonicalize_finra_fragment(
                attachment, base_url
            )
            if attachment_text:
                parts.append(attachment_text)

    return '\n\n'.join(parts)


def _extract_finra_document_id(url: str) -> str:
    """Use the authoritative notice number, falling back to the canonical URL."""
    match = re.search(r'/notices/(\d{2}-\d{2})(?:/)?$', url)
    if match:
        return f"FINRA {match.group(1)}"
    return url


def _finra_page_url(page: int) -> str:
    """Build FINRA's zero-based listing page URL."""
    if page == 0:
        return FINRA_NOTICES_URL
    return f"{FINRA_NOTICES_URL}?{urlencode({'page': page})}"


def _extract_finra_declared_pages(soup: BeautifulSoup) -> Optional[int]:
    """Read authoritative FINRA pager metadata without guessing a page count."""
    pager = soup.select_one('nav[aria-labelledby="pagination-heading"] .pagination')
    if pager is None:
        pager = soup.select_one('.pagination')
    if pager is None:
        empty = soup.select_one('.view-empty, .views-empty, .view-empty-message')
        if empty and re.search(
            r'\bno (?:regulatory )?notices?\b|\bno results?\b',
            empty.get_text(' ', strip=True),
            re.IGNORECASE,
        ):
            return 0
        return None

    page_numbers = []
    for link in pager.select('a[href]'):
        href = urljoin(FINRA_NOTICES_URL, link['href'])
        query = parse_qs(urlparse(href).query, keep_blank_values=True)
        if 'page' not in query:
            if urlparse(href).path.rstrip('/') == urlparse(FINRA_NOTICES_URL).path.rstrip('/'):
                page_numbers.append(0)
            continue
        raw_pages = query['page']
        if len(raw_pages) != 1 or not re.fullmatch(r'\d+', raw_pages[0]):
            return None
        page_numbers.append(int(raw_pages[0]))

    if page_numbers:
        return max(page_numbers) + 1

    active_page = pager.select_one('.page-item.active .page-link, .pager__item.is-active')
    if active_page and active_page.get_text(' ', strip=True) == '1':
        return 1
    return None


def _finra_is_explicit_zero_result(soup: BeautifulSoup) -> bool:
    """Recognize only an explicit FINRA empty-result shape."""
    empty = soup.select_one('.view-empty, .views-empty, .view-empty-message')
    return bool(
        empty
        and re.search(
            r'\bno (?:regulatory )?notices?\b|\bno results?\b',
            empty.get_text(' ', strip=True),
            re.IGNORECASE,
        )
    )


def _fetch_finra_page(url: str, session: requests.Session) -> dict:
    """Use one request per attempt with a coordinated session-wide cooldown."""
    for attempt in range(FINRA_MAX_RETRY_ATTEMPTS):
        last_request = getattr(session, '_finra_last_request_at', 0.0)
        now = time.monotonic()
        cooldown_until = getattr(session, '_finra_cooldown_until', 0.0)
        if cooldown_until > now:
            time.sleep(cooldown_until - now)
            now = time.monotonic()
        elapsed = now - last_request
        if elapsed < FINRA_REQUEST_INTERVAL_SECONDS:
            time.sleep(FINRA_REQUEST_INTERVAL_SECONDS - elapsed)
        # The shared helper normally retries 429s itself. FINRA uses one
        # attempt here so the session cooldown remains the only retry loop.
        result = fetch_page(url, session, max_retries=1)
        try:
            session._finra_last_request_at = time.monotonic()
        except AttributeError:
            pass
        if result['status_code'] not in (0, 429) or attempt == FINRA_MAX_RETRY_ATTEMPTS - 1:
            if result['status_code'] not in (0, 429):
                try:
                    session._finra_backoff_seconds = FINRA_RETRY_BASE_WAIT_SECONDS
                except AttributeError:
                    pass
            return result
        previous_wait = getattr(
            session,
            '_finra_backoff_seconds',
            FINRA_RETRY_BASE_WAIT_SECONDS,
        )
        retry_after = result.get('retry_after')
        wait_time = max(
            retry_after if isinstance(retry_after, int) else 0,
            previous_wait,
        )
        wait_time = min(FINRA_MAX_RETRY_WAIT_SECONDS, wait_time)
        try:
            session._finra_cooldown_until = (
                time.monotonic() + wait_time
            )
            session._finra_backoff_seconds = min(
                FINRA_MAX_RETRY_WAIT_SECONDS,
                max(FINRA_RETRY_BASE_WAIT_SECONDS, previous_wait * 2),
            )
        except AttributeError:
            pass
        logger.warning(
            "FINRA request for %s returned %s; retrying in %ss",
            url,
            result['status_code'],
            wait_time,
        )
        time.sleep(wait_time)
    return result


def _finra_known_notice_urls(source_state: dict) -> list[str]:
    """Resolve persisted FINRA identities to canonical URLs for refresh."""
    urls = []
    for key in source_state.get('entries', {}):
        if isinstance(key, str) and key.startswith('http'):
            if '/rules-guidance/notices/' in key:
                urls.append(key)
            continue
        match = re.fullmatch(r'FINRA (\d{2}-\d{2})', str(key))
        if match:
            urls.append(f"{FINRA_NOTICES_URL}/{match.group(1)}")
    return sorted(set(urls))


def _finra_refresh_batch(source_state: dict) -> list[str]:
    """Select a deterministic bounded batch of known URLs for this run."""
    urls = _finra_known_notice_urls(source_state)
    if not urls:
        return []
    cursor = source_state.get('refresh_cursor', 0)
    if not isinstance(cursor, int) or isinstance(cursor, bool) or cursor < 0:
        cursor = 0
    cursor %= len(urls)
    return [urls[(cursor + offset) % len(urls)] for offset in range(
        min(FINRA_REFRESH_BATCH_SIZE, len(urls))
    )]


def _extract_finra_notice_links(soup: BeautifulSoup) -> list[tuple[str, str, str]]:
    """Collect canonical notice links and their optional listing dates from one page."""
    notice_pattern = re.compile(
        r'^/rules-guidance/notices/(?:\d{2}-\d{2}|information-notice-\d{8})/?$'
    )
    notice_urls = []
    seen_urls = set()
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').split('#', 1)[0]
        if not notice_pattern.match(href):
            continue
        url = urljoin(FINRA_NOTICES_URL, href)
        if url not in seen_urls:
            seen_urls.add(url)
            notice_urls.append(
                (url, link.get_text(' ', strip=True), _extract_listing_date(link))
            )
    return notice_urls


def fetch_finra_notices(
    session: requests.Session,
    config: dict,
    limit: Optional[int] = None,
    since_date: Optional[str] = None,
    known_urls: Optional[list[str]] = None,
) -> FetchResult:
    """
    Scrape FINRA regulatory notices page.

    Args:
        session: requests.Session instance
        config: Configuration dict for classification
        limit: Maximum notices to fetch (for testing)
        known_urls: Persisted notice URLs that must be refreshed even when the
            listing cutoff stops before their historical page. The unchanged
            source watermark makes a failed refresh safely resumable on the
            next scheduled run.

    Returns:
        FetchResult: List-compatible items plus a completeness verdict.
    """
    items = []

    if limit is not None and limit < 0:
        return _incomplete_result(error=f"FINRA limit must be non-negative, got {limit}")

    try:
        logger.info(f"Fetching FINRA notices from {FINRA_NOTICES_URL}...")
        page_records = []
        seen_urls = set()
        declared_pages = None
        cutoff_page = None
        pages_fetched = 0
        target_page = None

        for page in range(FINRA_MAX_PAGES):
            result = _fetch_finra_page(_finra_page_url(page), session)
            if result['status_code'] != 200:
                return _incomplete_result(
                    error=(
                        f"FINRA notices page {page} returned status "
                        f"{result['status_code']}: {result.get('error') or 'unavailable'}"
                    ),
                    expected_count=len(page_records),
                    pages_fetched=pages_fetched,
                    declared_pages=declared_pages,
                    cutoff_page=cutoff_page,
                )

            soup = BeautifulSoup(result['content'], 'html.parser')
            page_declared = _extract_finra_declared_pages(soup)
            if declared_pages is None:
                if page_declared is None:
                    return _incomplete_result(
                        error="FINRA pagination metadata was missing or unparseable",
                        pages_fetched=pages_fetched,
                        declared_pages=declared_pages,
                    )
                declared_pages = page_declared
                if declared_pages > FINRA_MAX_PAGES:
                    return _incomplete_result(
                        error=(
                            f"FINRA pagination declared {declared_pages} pages, "
                            f"exceeding safe cutoff {FINRA_MAX_PAGES}"
                        ),
                        pages_fetched=pages_fetched,
                        declared_pages=declared_pages,
                    )
            elif page_declared is None or page_declared > declared_pages or (
                page < declared_pages - 1 and page_declared != declared_pages
            ):
                return _incomplete_result(
                    error="FINRA pagination metadata changed or disappeared while traversing pages",
                    expected_count=len(page_records),
                    pages_fetched=pages_fetched,
                    declared_pages=declared_pages,
                    cutoff_page=cutoff_page,
                )

            records = _extract_finra_notice_links(soup)
            pages_fetched += 1
            logger.info(
                f"FINRA listing page {page + 1}/{declared_pages}: "
                f"{len(records)} notice links"
            )

            if not records:
                if page == 0 and declared_pages == 0 and _finra_is_explicit_zero_result(soup):
                    break
                return _incomplete_result(
                    error=f"FINRA page {page} contained no recognizable notice links",
                    expected_count=len(page_records),
                    pages_fetched=pages_fetched,
                    declared_pages=declared_pages,
                    cutoff_page=cutoff_page,
                )

            if declared_pages == 0:
                return _incomplete_result(
                    error="FINRA pagination declared zero pages but returned notice links",
                    expected_count=len(page_records),
                    pages_fetched=pages_fetched,
                    declared_pages=declared_pages,
                )

            for record in records:
                url = record[0]
                if url in seen_urls:
                    return _incomplete_result(
                        error=f"FINRA pagination overlap/conflict for {url}",
                        expected_count=len(page_records),
                        pages_fetched=pages_fetched,
                        declared_pages=declared_pages,
                        cutoff_page=cutoff_page,
                    )
                seen_urls.add(url)
                page_records.append(record)

            # The listing date controls only how far pagination proceeds. Every
            # record in the fetched window is still detailed and hashed below so
            # backdated/new notices and edits to known notices are not skipped.
            if (
                cutoff_page is None
                and since_date
                and all(listing_date and listing_date < since_date for _, _, listing_date in records)
            ):
                cutoff_page = page
                target_page = min(declared_pages - 1, page + FINRA_REFETCH_PAGES)
                logger.info(
                    f"FINRA safe cutoff reached at page {page}; "
                    f"refetch window extends through page {target_page}"
                )

            if page + 1 >= declared_pages:
                break
            if target_page is not None and page >= target_page:
                break
        else:
            return _incomplete_result(
                error=f"FINRA pagination exceeded safe cutoff of {FINRA_MAX_PAGES} pages",
                expected_count=len(page_records),
                pages_fetched=pages_fetched,
                declared_pages=declared_pages,
                cutoff_page=cutoff_page,
            )

        if declared_pages is None or (
            declared_pages != 0 and pages_fetched > declared_pages
        ):
            return _incomplete_result(
                error="FINRA pagination metadata was not verifiable",
                expected_count=len(page_records),
                pages_fetched=pages_fetched,
                declared_pages=declared_pages,
                cutoff_page=cutoff_page,
            )
        if (
            cutoff_page is None
            and declared_pages != 0
            and pages_fetched != declared_pages
        ):
            return _incomplete_result(
                error=(
                    "FINRA pagination incomplete: "
                    f"declared {declared_pages} pages, fetched {pages_fetched}"
                ),
                expected_count=len(page_records),
                pages_fetched=pages_fetched,
                declared_pages=declared_pages,
            )

        for known_url in sorted(set(known_urls or [])):
            if known_url not in seen_urls:
                page_records.append((known_url, '', ''))
                seen_urls.add(known_url)

        if limit is not None:
            page_records = page_records[:limit]
            logger.info(f"Limited to {limit} notices for testing; state will not advance")

        seen_document_ids = {}
        for url, listing_title, listing_date in page_records:
            detail = _fetch_finra_page(url, session)
            if detail['status_code'] != 200:
                return _incomplete_result(
                    items,
                    error=(
                        f"FINRA notice detail page returned status "
                        f"{detail['status_code']}: {url}: "
                        f"{detail.get('error') or 'unavailable'}"
                    ),
                    expected_count=len(page_records),
                    pages_fetched=pages_fetched,
                    declared_pages=declared_pages,
                    cutoff_page=cutoff_page,
                    limited=limit is not None,
                )

            detail_soup = BeautifulSoup(detail['content'], 'html.parser')
            title_node = detail_soup.select_one('.field--name-field-notice-title-tx') or detail_soup.find('h1')
            title = (
                ' '.join(title_node.get_text(' ', strip=True).split())
                if title_node
                else ' '.join((listing_title or '').split())
            )
            publication_date = _extract_finra_publication_date(detail_soup)
            abstract = _extract_finra_summary(detail_soup)
            substantive_content = _extract_finra_substantive_content(detail_soup, url)
            if not substantive_content:
                return _incomplete_result(
                    items,
                    error=f"FINRA notice detail had no substantive content: {url}",
                    expected_count=len(page_records),
                    pages_fetched=pages_fetched,
                    declared_pages=declared_pages,
                    cutoff_page=cutoff_page,
                    limited=limit is not None,
                )
            document_id = _extract_finra_document_id(url)

            if listing_date and publication_date and listing_date != publication_date:
                return _incomplete_result(
                    items,
                    error=f"FINRA listing/detail date conflict for {document_id}",
                    expected_count=len(page_records),
                    pages_fetched=pages_fetched,
                    declared_pages=declared_pages,
                    cutoff_page=cutoff_page,
                    limited=limit is not None,
                )

            previous_url = seen_document_ids.get(document_id)
            if previous_url is not None and previous_url != url:
                return _incomplete_result(
                    items,
                    error=f"FINRA listing contained conflicting URLs for {document_id}",
                    expected_count=len(page_records),
                    pages_fetched=pages_fetched,
                    declared_pages=declared_pages,
                    cutoff_page=cutoff_page,
                    limited=limit is not None,
                )
            seen_document_ids[document_id] = url

            # Unknown source dates are retained as unknown. Never infer a date
            # from the notice number or from the local clock.
            tier, reason = classify_regulatory_relevance(title, substantive_content, config)
            affected_controls = find_affected_controls_by_keywords(
                title, substantive_content, config
            )

            items.append(
                RegulatoryItem(
                    source='FINRA',
                    agency='FINRA',
                    title=title,
                    url=url,
                    publication_date=publication_date,
                    doc_type='NOTICE',
                    abstract=abstract,
                    document_id=document_id,
                    classification=tier,
                    classification_reason=reason,
                    affected_controls=affected_controls,
                    substantive_content=substantive_content,
                )
            )

        if limit is not None:
            return _incomplete_result(
                items,
                error="FINRA fetch was explicitly limited",
                expected_count=len(page_records),
                pages_fetched=pages_fetched,
                declared_pages=declared_pages,
                cutoff_page=cutoff_page,
                limited=True,
            )

        return _complete_result(
            items,
            expected_count=len(page_records),
            pages_fetched=pages_fetched,
            declared_pages=declared_pages,
            cutoff_page=cutoff_page,
        )

    except requests.RequestException as e:
        return _incomplete_result(items, error=f"FINRA notices scraping error: {e}")
    except (ValueError, TypeError) as e:
        return _incomplete_result(items, error=f"FINRA notices parsing error: {e}")


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
        content_hash = _item_content_hash(item)

        # Check if this is a new item or changed item
        if entry_key not in existing_entries:
            logger.info(f"  New item: {item.title[:60]}... ({item.agency})")
            new_items.append(item)
        elif existing_entries[entry_key] != content_hash:
            logger.info(f"  Updated item: {item.title[:60]}... ({item.agency})")
            new_items.append(item)

    return new_items


def update_source_state(
    source_key: str,
    items: list[RegulatoryItem],
    state: dict,
    *,
    refreshed_urls: Optional[list[str]] = None,
) -> None:
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
        entries[entry_key] = _item_content_hash(item)

    source_state['entries'] = entries
    if source_key == SOURCE_KEY_FINRA and refreshed_urls is not None:
        known_urls = _finra_known_notice_urls(source_state)
        if known_urls:
            cursor = source_state.get('refresh_cursor', 0)
            if not isinstance(cursor, int) or isinstance(cursor, bool) or cursor < 0:
                cursor = 0
            source_state['refresh_cursor'] = (
                cursor + len(refreshed_urls)
            ) % len(known_urls)
        else:
            source_state['refresh_cursor'] = 0
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
    def display_date(item: RegulatoryItem) -> str:
        return item.publication_date or "Unknown (not provided by source)"

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
            lines.append(f"- **Published:** {display_date(item)}\n")
            if item.doc_type:
                lines.append(f"- **Type:** {item.doc_type}\n")
            lines.append(f"- **Classification:** {item.classification} — {item.classification_reason}\n")

            if item.abstract:
                lines.append(f"- **Abstract:** {item.abstract[:500]}{'...' if len(item.abstract) > 500 else ''}\n")

            if item.affected_controls:
                lines.append("- **Potentially Affected Controls:**\n")
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
            lines.append(f"- **Published:** {display_date(item)}\n")
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
            lines.append(
                f"- [{item.title}]({item.url}) ({item.agency}, {display_date(item)})"
                f" — **Classification:** {item.classification} — {item.classification_reason}\n"
            )
            if item.abstract:
                lines.append(f"  - **Evidence:** {item.abstract[:500]}{'...' if len(item.abstract) > 500 else ''}\n")

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
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: scripts/config/monitoring-config.yaml)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate config file and exit without running'
    )

    args = parser.parse_args()

    # Setup logging
    global logger
    logger = setup_logging(verbose=args.verbose)

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

    logger.info("=== Regulatory Monitor ===")
    logger.info(f"Source: {args.source}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Config: {config_path}")
    if args.limit is not None:
        logger.info(f"Limit: {args.limit} items per source")

    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load unified state
    state = load_state(STATE_FILE)

    # Graceful degradation: --dry-run skips all network calls so the script
    # can be smoke-tested in CI environments without outbound access.
    if args.dry_run:
        logger.info("Dry run: skipping all network calls (offline mode)")
        print("INFO: regulatory_monitor dry-run — network calls skipped (offline mode).")
        sys.exit(0)

    # Create session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'FSI-AgentGov-Regulatory-Monitor/1.0 (https://github.com/judeper/FSI-AgentGov)'
    })

    all_new_items = []
    source_runs = []
    finra_refresh_urls = []

    # Fetch from Federal Register
    if args.source in ['federal-register', 'all']:
        logger.info("\n--- Federal Register ---")
        fed_state = get_source_state(state, SOURCE_KEY_FEDERAL_REGISTER)

        # First-run baseline suppression: when there is no prior persisted state
        # for this source, record the current items as the baseline silently
        # rather than flagging every fetched item as "new". Without this guard a
        # first run would emit ~30 days of items as a single noisy report.
        fed_is_baseline = fed_state.get('last_run') is None

        # Determine since_date (last check or 30 days ago)
        since_date = fed_state.get('last_checked')
        if not since_date:
            since_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%d')
            logger.info("No prior state, fetching documents from last 30 days")
        else:
            logger.info(f"Fetching documents since {since_date}")

        fed_result = _coerce_fetch_result(
            fetch_federal_register_documents(session, since_date, config, limit=args.limit)
        )
        source_runs.append((
            SOURCE_KEY_FEDERAL_REGISTER,
            fed_state,
            fed_is_baseline,
            fed_result,
        ))

    # Fetch from FINRA
    if args.source in ['finra', 'all']:
        logger.info("\n--- FINRA Notices ---")
        finra_state = get_source_state(state, SOURCE_KEY_FINRA)

        # First-run baseline suppression (mirrors Federal Register / learn_monitor).
        finra_is_baseline = finra_state.get('last_run') is None
        finra_refresh_urls = _finra_refresh_batch(finra_state)

        finra_result = _coerce_fetch_result(
            fetch_finra_notices(
                session,
                config,
                limit=args.limit,
                since_date=_state_date(finra_state),
                known_urls=finra_refresh_urls,
            )
        )
        source_runs.append((
            SOURCE_KEY_FINRA,
            finra_state,
            finra_is_baseline,
            finra_result,
        ))

    incomplete_runs = [
        (source_key, result.error or "source returned unverifiable data")
        for source_key, _, _, result in source_runs
        if not result.complete
    ]
    if incomplete_runs:
        for source_key, error in incomplete_runs:
            logger.error(f"{source_key}: state watermark not advanced: {error}")
        sys.exit(2)

    # Only complete, unbounded source fetches may affect state or reports.
    if not args.dry_run:
        for source_key, source_state, is_baseline, result in source_runs:
            items = list(result)
            if is_baseline:
                logger.info(
                    f"{source_key}: first run - baseline established, no changes "
                    f"reported on first run ({len(items)} items recorded)"
                )
            else:
                new_items = check_for_new_items(source_key, items, source_state)
                logger.info(f"{source_key}: {len(new_items)} new items")
                all_new_items.extend(new_items)
            update_source_state(
                source_key,
                items,
                state,
                refreshed_urls=(
                    finra_refresh_urls if source_key == SOURCE_KEY_FINRA else None
                ),
            )
            if source_key == SOURCE_KEY_FEDERAL_REGISTER:
                updated_state = get_source_state(state, source_key)
                updated_state['last_checked'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                set_source_state(state, source_key, updated_state)
    else:
        # The dry-run path exits before fetching, but keep this guard explicit
        # if a caller exercises main with a patched source in the future.
        for source_key, source_state, is_baseline, result in source_runs:
            items = list(result)
            if not is_baseline:
                all_new_items.extend(check_for_new_items(source_key, items, source_state))

    # Generate report if new items found
    if all_new_items:
        logger.info(f"\n=== {len(all_new_items)} total new regulatory items detected ===")

        report_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        report_path = REPORTS_DIR / f"regulatory-changes-{report_date}.md"

        generate_regulatory_report(all_new_items, report_path)

        # Save state
        if not args.dry_run:
            save_state_atomic(state, STATE_FILE)
            logger.info(f"State updated: {STATE_FILE}")
        else:
            logger.info("Dry run: state not updated")

        # Exit code 1 indicates new items (triggers PR in CI)
        sys.exit(1)

    else:
        logger.info("\n=== No new regulatory items detected ===")

        # Save state even if no changes (updates last_run timestamps)
        if not args.dry_run:
            save_state_atomic(state, STATE_FILE)

        # Exit code 0 indicates no changes
        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.debug("Traceback:", exc_info=True)
        sys.exit(2)
