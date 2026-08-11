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
import uuid
from copy import deepcopy
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
    StateLoadError,
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
FINRA_REFRESH_BATCH_SIZE = 25
FINRA_REQUEST_INTERVAL_SECONDS = 1.00
FINRA_RETRY_BASE_WAIT_SECONDS = 5
FINRA_MAX_RETRY_WAIT_SECONDS = 60
FINRA_MAX_RETRY_ATTEMPTS = 6
FINRA_CACHE_BUST_PARAM = "_finra_pass"

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
        fallback_urls: Optional[dict[str, str]] = None,
        coverage: Optional[dict] = None,
    ):
        super().__init__(items)
        self.complete = complete
        self.expected_count = expected_count
        self.pages_fetched = pages_fetched
        self.declared_pages = declared_pages
        self.cutoff_page = cutoff_page
        self.error = error
        self.limited = limited
        self.fallback_urls = dict(fallback_urls or {})
        self.coverage = dict(coverage or {})


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


def _entries_digest(entries: dict) -> str:
    """Compute a stable digest over the complete persisted entry map."""
    return compute_hash(
        json.dumps(
            entries,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def _identity_digest(identities) -> str:
    """Compute a stable digest over a sorted set of persisted identities."""
    return compute_hash(json.dumps(
        sorted(set(identities)),
        ensure_ascii=False,
        separators=(",", ":"),
    ))


def _alias_ledger_digest(ledger: list[dict]) -> str:
    """Compute a stable digest over validated FINRA alias mappings."""
    normalized = sorted(
        ledger,
        key=lambda item: (
            item.get("old_identity", ""),
            item.get("canonical_identity", ""),
        ),
    )
    return compute_hash(json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ))


def _finra_identity_notice_number(identity: object) -> Optional[str]:
    """Derive the immutable FINRA notice number an identity denotes, if any."""
    if not isinstance(identity, str) or not identity:
        return None
    match = re.fullmatch(r"FINRA (\d{2}-\d{2})", identity.strip())
    if match:
        return match.group(1)
    canonical_url, _ = _finra_normalize_detail_link(identity)
    if not canonical_url:
        return None
    match = re.search(r"/notices/(\d{2}-\d{2})$", urlparse(canonical_url).path)
    return match.group(1) if match else None


def _finra_alias_source_url(identity: object) -> Optional[str]:
    """Resolve a legacy identity to the listing URL that produced it."""
    notice_number = _finra_identity_notice_number(identity)
    if notice_number:
        return f"{FINRA_NOTICES_URL}/{notice_number}"
    if not isinstance(identity, str):
        return None
    canonical_url, node_identity = _finra_normalize_detail_link(identity)
    if canonical_url and node_identity and node_identity.startswith("url:"):
        return canonical_url
    return None


def _finra_alias_chain_head(alias: dict) -> tuple[Optional[str], list[str]]:
    """Replay an alias content-update chain from its immutable migration hash."""
    errors: list[str] = []
    evidence = alias.get("evidence")
    source_hash = alias.get("source_hash")
    if not isinstance(evidence, dict) or not isinstance(source_hash, str):
        return None, ["regulatory-finra alias evidence is malformed"]
    updates = evidence.get("content_updates", [])
    if not isinstance(updates, list):
        return None, ["regulatory-finra alias content update chain is invalid"]
    head = source_hash
    for update in updates:
        if (
            not isinstance(update, dict)
            or not isinstance(update.get("from"), str)
            or not update["from"]
            or not isinstance(update.get("to"), str)
            or not update["to"]
            or update["from"] == update["to"]
            or update["from"] != head
        ):
            errors.append(
                "regulatory-finra alias content update chain is not contiguous"
            )
            return None, errors
        head = update["to"]
    return head, errors


def _resolve_finra_identity(source_state: dict, identity: str) -> str:
    """Resolve a historical FINRA identity through the alias ledger."""
    coverage = source_state.get("coverage")
    ledger = coverage.get("alias_ledger", []) if isinstance(coverage, dict) else []
    aliases = {
        item.get("old_identity"): item.get("canonical_identity")
        for item in ledger
        if isinstance(item, dict)
    }
    current = identity
    seen = set()
    while current in aliases:
        if current in seen:
            raise ValueError(f"FINRA alias cycle detected for {identity}")
        seen.add(current)
        current = aliases[current]
    return current


def _validate_finra_alias_ledger(
    ledger: object,
    entries: dict,
    fetched_entry_identities: list[str],
    *,
    fallback_urls: object = None,
) -> list[str]:
    """Validate aliases against verifiable state, not self-duplicating evidence.

    Every alias must be bound to facts that live outside the alias record: the
    immutable FINRA notice number, the canonical entry hash currently persisted
    in ``entries``, and the independently learned listing-URL -> numeric-node
    mapping from FINRA's authoritative detail-page shortlink. Evidence fields
    that merely repeat one another prove nothing, so an alias may only claim a
    hash the canonical entry actually carries, reached through an explicit,
    contiguous content-update chain that starts at the migration hash.
    """
    errors = []
    if not isinstance(ledger, list):
        return ["regulatory-finra alias ledger is invalid"]

    fetched = set(fetched_entry_identities)
    old_identities = set()
    canonical_identities = set()
    for item in ledger:
        if not isinstance(item, dict):
            errors.append("regulatory-finra alias ledger contains a malformed item")
            continue
        old_identity = item.get("old_identity")
        canonical_identity = item.get("canonical_identity")
        source_hash = item.get("source_hash")
        evidence = item.get("evidence")
        if (
            not isinstance(old_identity, str)
            or not old_identity
            or not isinstance(canonical_identity, str)
            or not canonical_identity
            or not isinstance(source_hash, str)
            or not source_hash
            or not isinstance(evidence, dict)
        ):
            errors.append("regulatory-finra alias ledger item is malformed")
            continue
        if old_identity == canonical_identity:
            errors.append(
                f"regulatory-finra alias points at itself: {old_identity}"
            )
        if old_identity in old_identities:
            errors.append(
                f"regulatory-finra alias has multiple targets: {old_identity}"
            )
        old_identities.add(old_identity)
        if canonical_identity in canonical_identities:
            errors.append(
                "regulatory-finra alias ledger violates one-to-one targets"
            )
        canonical_identities.add(canonical_identity)
        if old_identity in entries:
            errors.append(
                f"regulatory-finra alias is also persisted as an entry: {old_identity}"
            )
        if old_identity in fetched:
            errors.append(
                f"regulatory-finra alias conflicts with canonical identity: {old_identity}"
            )
        if canonical_identity not in entries or canonical_identity not in fetched:
            errors.append(
                "regulatory-finra alias target is not a fetched persisted identity"
            )
        if evidence.get("source_hash_at_migration") != source_hash:
            errors.append(
                "regulatory-finra alias source hash evidence is invalid"
            )
        if evidence.get("canonical_hash_at_migration") != source_hash:
            errors.append(
                "regulatory-finra alias canonical hash evidence is invalid"
            )
        if not isinstance(evidence.get("reason"), str) or not evidence["reason"]:
            errors.append("regulatory-finra alias evidence is missing a reason")

        # Immutable identity binding: when both sides denote a FINRA notice
        # number, a migration may never move between two different notices.
        old_notice = _finra_identity_notice_number(old_identity)
        canonical_notice = _finra_identity_notice_number(canonical_identity)
        if old_notice and canonical_notice and old_notice != canonical_notice:
            errors.append(
                "regulatory-finra alias migrates between different notices: "
                f"{old_identity} -> {canonical_identity}"
            )

        source_url = _finra_alias_source_url(old_identity)
        observed_node = (
            _validate_finra_node_url(fallback_urls.get(source_url, ""))
            if isinstance(fallback_urls, dict) and source_url
            else None
        )
        if observed_node is None:
            errors.append(
                "regulatory-finra alias lacks an independent detail-node "
                f"binding: {old_identity}"
            )
        elif observed_node != canonical_identity:
            errors.append(
                "regulatory-finra alias target does not match its "
                f"independent detail-node binding: {old_identity}"
            )

        # Verifiable content binding: replay the recorded migration transition
        # against the persisted canonical entry hash instead of trusting the
        # duplicated evidence fields above.
        chain_head, chain_errors = _finra_alias_chain_head(item)
        errors.extend(chain_errors)
        if chain_head is not None and canonical_identity in entries:
            if entries[canonical_identity] != chain_head:
                errors.append(
                    "regulatory-finra alias is not bound to its canonical "
                    f"entry hash: {old_identity}"
                )

    if old_identities & canonical_identities:
        errors.append("regulatory-finra alias ledger contains a cycle")
    return errors


def _rebind_finra_alias(alias: dict, fetched_entries: dict) -> dict:
    """Record an observed canonical content transition without rewriting history."""
    canonical_identity = alias.get("canonical_identity")
    if canonical_identity not in fetched_entries:
        raise ValueError(
            "FINRA alias target is not a fetched canonical identity: "
            f"{canonical_identity}"
        )
    head, errors = _finra_alias_chain_head(alias)
    if head is None:
        raise ValueError(errors[0] if errors else "FINRA alias evidence is malformed")
    current_hash = fetched_entries[canonical_identity]
    if current_hash == head:
        return deepcopy(alias)
    rebound = deepcopy(alias)
    evidence = rebound["evidence"]
    evidence["content_updates"] = [
        *evidence.get("content_updates", []),
        {"from": head, "to": current_hash},
    ]
    return rebound


def _build_finra_alias_ledger(
    previous_entries: dict,
    fetched_entries: dict,
    *,
    existing_alias_ledger: Optional[list[dict]] = None,
    legacy_migration_ledger: Optional[list[dict]] = None,
    fallback_urls: object = None,
) -> list[dict]:
    """Migrate legacy duplicate identities to one canonical fetched identity."""
    existing_alias_ledger = list(existing_alias_ledger or [])
    legacy_migration_ledger = list(legacy_migration_ledger or [])
    legacy_reasons = {
        item.get("identity"): item.get("reason")
        for item in legacy_migration_ledger
        if isinstance(item, dict)
    }
    previous_ids = set(previous_entries)
    fetched_ids = set(fetched_entries)
    legacy_ids = previous_ids - fetched_ids
    if legacy_ids and not legacy_migration_ledger:
        raise ValueError(
            "FINRA prior identities are outside the complete fetch and lack "
            "explicit migration evidence"
        )
    if legacy_migration_ledger and set(legacy_reasons) != legacy_ids:
        raise ValueError(
            "FINRA legacy migration ledger does not account for every alias"
        )

    ledger = []
    target_ids = set()
    old_ids = set()
    for item in existing_alias_ledger:
        if not isinstance(item, dict):
            raise ValueError("FINRA alias ledger is malformed")
        old_identity = item.get("old_identity")
        canonical_identity = item.get("canonical_identity")
        if old_identity in old_ids or canonical_identity in target_ids:
            raise ValueError("FINRA alias ledger violates one-to-one constraints")
        old_ids.add(old_identity)
        target_ids.add(canonical_identity)
        ledger.append(_rebind_finra_alias(item, fetched_entries))

    for old_identity in sorted(legacy_ids):
        source_hash = previous_entries[old_identity]
        candidates = [
            identity
            for identity, content_hash in fetched_entries.items()
            if content_hash == source_hash
        ]
        if len(candidates) != 1:
            raise ValueError(
                "FINRA legacy identity lacks exactly one matching canonical "
                f"detail identity: {old_identity}"
            )
        canonical_identity = candidates[0]
        if old_identity in old_ids or canonical_identity in target_ids:
            raise ValueError("FINRA alias ledger violates one-to-one constraints")
        old_ids.add(old_identity)
        target_ids.add(canonical_identity)
        reason = legacy_reasons.get(old_identity) or (
            "legacy identity migrated to the unique fetched canonical detail "
            "with matching content hash"
        )
        ledger.append({
            "old_identity": old_identity,
            "canonical_identity": canonical_identity,
            "source_hash": source_hash,
            "evidence": {
                "source_hash_at_migration": source_hash,
                "canonical_hash_at_migration": fetched_entries[canonical_identity],
                "reason": reason,
            },
        })

    errors = _validate_finra_alias_ledger(
        ledger,
        fetched_entries,
        sorted(fetched_ids),
        fallback_urls=fallback_urls,
    )
    if errors:
        raise ValueError(errors[0])
    return sorted(
        ledger,
        key=lambda item: (item["old_identity"], item["canonical_identity"]),
    )


def _finra_pass_proof_recomputation_errors(
    source_key: str,
    proof: dict,
    index: int,
) -> list[str]:
    """Recompute every derived pass-proof value from the retained raw payloads."""
    errors: list[str] = []
    label = f"{source_key} pass proof {index}"
    payloads = proof.get("page_row_payloads")
    if not isinstance(payloads, list) or any(
        not isinstance(page, list)
        or any(not isinstance(row, dict) for row in page)
        for page in payloads
    ):
        return [f"{label} page row payloads are missing or invalid"]

    for key in (
        "page_numbers",
        "page_identities",
        "page_row_counts",
        "page_row_digests",
    ):
        value = proof.get(key)
        if not isinstance(value, list) or len(value) != len(payloads):
            errors.append(f"{label} {key} do not match the retained payloads")
    if proof.get("pages_fetched") != len(payloads):
        errors.append(f"{label} pages_fetched does not match the retained payloads")

    recomputed_counts = [len(page) for page in payloads]
    recomputed_digests = [
        compute_hash(json.dumps(
            page,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ))
        for page in payloads
    ]
    if proof.get("page_row_counts") != recomputed_counts:
        errors.append(f"{label} page row counts are not recomputable from payloads")
    if proof.get("page_row_digests") != recomputed_digests:
        errors.append(f"{label} page row digests are not recomputable from payloads")

    resolved = 0
    unresolved = 0
    node_identities = set()
    for page in payloads:
        for row in page:
            links = row.get("links")
            targets = set()
            for link in links if isinstance(links, list) else []:
                if not isinstance(link, dict):
                    continue
                href = link.get("href")
                if not isinstance(href, str):
                    continue
                detail_url, node_identity = _finra_normalize_detail_link(href)
                if detail_url:
                    targets.add((detail_url, node_identity))
            if len(targets) == 1:
                resolved += 1
                node_identities.add(next(iter(targets))[1])
            else:
                unresolved += 1

    if proof.get("raw_row_count") != sum(recomputed_counts):
        errors.append(f"{label} raw row count is not recomputable from payloads")
    if proof.get("resolved_row_count") != resolved:
        errors.append(f"{label} resolved row count is not recomputable from payloads")
    if proof.get("unresolved_row_count") != unresolved:
        errors.append(
            f"{label} unresolved row count is not recomputable from payloads"
        )
    if proof.get("unique_node_count") != len(node_identities):
        errors.append(f"{label} unique node count is not recomputable from payloads")
    return errors


def _finra_alias_map(alias_ledger: object) -> dict:
    """Build an old->canonical resolver from a (possibly malformed) ledger."""
    alias_map: dict[str, str] = {}
    if not isinstance(alias_ledger, list):
        return alias_map
    for item in alias_ledger:
        if (
            isinstance(item, dict)
            and isinstance(item.get("old_identity"), str)
            and item["old_identity"]
            and isinstance(item.get("canonical_identity"), str)
            and item["canonical_identity"]
        ):
            alias_map[item["old_identity"]] = item["canonical_identity"]
    return alias_map


def _finra_resolve_identity_via_ledger(identity: str, alias_map: dict) -> str:
    """Resolve a raw FINRA identity to canonical through an alias map."""
    current = identity
    seen: set[str] = set()
    while current in alias_map and current not in seen:
        seen.add(current)
        current = alias_map[current]
    return current


def _finra_row_detail_target(row: object) -> Optional[str]:
    """Return the single canonical detail URL a retained raw row denotes."""
    if not isinstance(row, dict):
        return None
    targets: set[str] = set()
    links = row.get("links")
    if isinstance(links, list):
        for link in links:
            if not isinstance(link, dict):
                continue
            href = link.get("href")
            if isinstance(href, str):
                detail_url, _ = _finra_normalize_detail_link(href)
                if detail_url:
                    targets.add(detail_url)
    # Known-refresh rows carry their canonical URL directly rather than links.
    known_refresh = row.get("known_refresh_url")
    if isinstance(known_refresh, str):
        detail_url, _ = _finra_normalize_detail_link(known_refresh)
        if detail_url:
            targets.add(detail_url)
    if len(targets) != 1:
        return None
    return next(iter(targets))


def _finra_pass_proof_entry_identities(proof: dict, alias_map: dict) -> set:
    """Map a pass proof's resolvable rows to canonical entry identities.

    Each retained listing row denotes exactly one detail URL; the canonical
    entry identity is the same ``document_id`` production persists, resolved
    through the trusted alias ledger. Rows that do not resolve to a single
    supported detail target contribute nothing here (they are counted as
    unresolved by the recomputation proof).
    """
    identities: set[str] = set()
    payloads = proof.get("page_row_payloads")
    if not isinstance(payloads, list):
        return identities
    for page in payloads:
        if not isinstance(page, list):
            continue
        for row in page:
            detail_url = _finra_row_detail_target(row)
            if detail_url is None:
                continue
            document_id = _extract_finra_document_id(detail_url)
            identities.add(
                _finra_resolve_identity_via_ledger(document_id, alias_map)
            )
    return identities


def _coverage_watermark(source_state: dict) -> dict:
    """Return the persisted watermark fields bound by a coverage proof."""
    return {
        key: source_state.get(key)
        for key in ("last_run", "last_checked")
        if source_state.get(key) is not None
    }


def _validate_source_coverage(
    source_key: str,
    source_state: dict,
    *,
    allow_legacy_finra_identity_proof: bool = False,
) -> list[str]:
    """Validate the proof tying a source watermark to complete fetched data."""
    errors = []
    coverage = source_state.get("coverage")
    if not isinstance(coverage, dict):
        return [f"{source_key} state coverage proof is missing or not an object"]
    if coverage.get("schema_version") != 1:
        errors.append(f"{source_key} state coverage proof schema is unsupported")
    if coverage.get("source") != source_key:
        errors.append(f"{source_key} state coverage proof source identity is invalid")
    entries = source_state.get("entries")
    if not isinstance(entries, dict):
        return errors
    entry_count = coverage.get("entry_count")
    if not isinstance(entry_count, int) or isinstance(entry_count, bool) or entry_count < 0:
        errors.append(f"{source_key} state coverage entry_count is invalid")
    elif entry_count != len(entries):
        errors.append(
            f"{source_key} state coverage entry_count does not match entries"
        )
    if coverage.get("entries_digest") != _entries_digest(entries):
        errors.append(f"{source_key} state coverage entries_digest does not match entries")

    watermark = coverage.get("watermark")
    if not isinstance(watermark, dict):
        errors.append(f"{source_key} state coverage watermark is missing")
    elif watermark != _coverage_watermark(source_state):
        errors.append(f"{source_key} state coverage watermark does not match state")

    if coverage.get("complete") is not True:
        errors.append(f"{source_key} state coverage is not marked complete")
    if source_key == SOURCE_KEY_FEDERAL_REGISTER:
        required = (
            "window_start",
            "query",
            "expected_count",
            "fetched_count",
            "pages_fetched",
            "declared_pages",
            "page_numbers",
        )
        for key in required:
            if key not in coverage:
                errors.append(f"{source_key} coverage is missing {key}")
        if not isinstance(coverage.get("window_start"), str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", coverage.get("window_start", "")
        ):
            errors.append(f"{source_key} coverage window_start is invalid")
        if not isinstance(coverage.get("query"), dict):
            errors.append(f"{source_key} coverage query metadata is invalid")
        pages_fetched = coverage.get("pages_fetched")
        declared_pages = coverage.get("declared_pages")
        if (
            not isinstance(pages_fetched, int)
            or isinstance(pages_fetched, bool)
            or pages_fetched < 0
            or not isinstance(declared_pages, int)
            or isinstance(declared_pages, bool)
            or declared_pages < 0
        ):
            errors.append(f"{source_key} coverage page counts are invalid")
        elif pages_fetched != declared_pages:
            errors.append(f"{source_key} coverage pages are incomplete")
        expected_count = coverage.get("expected_count")
        fetched_count = coverage.get("fetched_count")
        if (
            not isinstance(expected_count, int)
            or isinstance(expected_count, bool)
            or expected_count < 0
            or not isinstance(fetched_count, int)
            or isinstance(fetched_count, bool)
            or fetched_count < 0
        ):
            errors.append(f"{source_key} coverage document counts are invalid")
        elif expected_count != fetched_count:
            errors.append(f"{source_key} coverage fetched_count is incomplete")
        if (
            isinstance(pages_fetched, int)
            and not isinstance(pages_fetched, bool)
            and pages_fetched >= 0
            and coverage.get("page_numbers")
            != list(range(1, pages_fetched + 1))
        ):
            errors.append(f"{source_key} coverage page identities are invalid")
    elif source_key == SOURCE_KEY_FINRA:
        identity_proof_fields = (
            "fetched_entry_identities",
            "fetched_entry_identity_digest",
            "entry_identity_digest",
            "alias_ledger",
            "alias_ledger_digest",
        )
        legacy_identity_proof = (
            allow_legacy_finra_identity_proof
            and "alias_ledger" not in coverage
            and "migration_ledger" in coverage
        )
        required = (
            "listing_mode",
            "listing_url",
            "listing_record_count",
            "raw_row_count",
            "resolved_row_count",
            "unresolved_row_count",
            "unique_node_count",
            "pages_fetched",
            "declared_pages",
            "detail_count",
            "page_numbers",
            "pass_proofs",
            "duplicate_ledger",
            "conflict_ledger",
        )
        if not legacy_identity_proof:
            required += identity_proof_fields
        for key in required:
            if key not in coverage:
                errors.append(f"{source_key} coverage is missing {key}")
        if coverage.get("listing_mode") != "complete-unfiltered":
            errors.append(
                f"{source_key} coverage is not a complete unfiltered listing"
            )
        if coverage.get("listing_url") != FINRA_NOTICES_URL:
            errors.append(f"{source_key} coverage listing_url is not authoritative")
        if coverage.get("unresolved_row_count") != 0:
            errors.append(f"{source_key} coverage contains unresolved listing rows")
        raw_row_count = coverage.get("raw_row_count")
        resolved_row_count = coverage.get("resolved_row_count")
        unresolved_row_count = coverage.get("unresolved_row_count")
        unique_node_count = coverage.get("unique_node_count")
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in (
                raw_row_count,
                resolved_row_count,
                unresolved_row_count,
                unique_node_count,
            )
        ):
            errors.append(f"{source_key} coverage row counts are invalid")
        elif raw_row_count != resolved_row_count + unresolved_row_count:
            errors.append(f"{source_key} coverage row counts do not reconcile")
        pages_fetched = coverage.get("pages_fetched")
        declared_pages = coverage.get("declared_pages")
        if (
            not isinstance(pages_fetched, int)
            or isinstance(pages_fetched, bool)
            or pages_fetched < 0
            or not isinstance(declared_pages, int)
            or isinstance(declared_pages, bool)
            or declared_pages < 0
        ):
            errors.append(f"{source_key} coverage page counts are invalid")
        elif not (
            pages_fetched == declared_pages
            or (declared_pages == 0 and pages_fetched == 1)
        ):
            errors.append(f"{source_key} coverage pages are incomplete")
        listing_count = coverage.get("listing_record_count")
        detail_count = coverage.get("detail_count")
        if (
            not isinstance(listing_count, int)
            or isinstance(listing_count, bool)
            or listing_count < 0
            or not isinstance(detail_count, int)
            or isinstance(detail_count, bool)
            or detail_count < 0
        ):
            errors.append(f"{source_key} coverage detail counts are invalid")
        elif listing_count != resolved_row_count:
            errors.append(f"{source_key} listing row count is incomplete")
        entry_identities = sorted(entries)
        fetched_entry_identities = []
        fetched_entry_identities = coverage.get("fetched_entry_identities")
        if (
            not isinstance(fetched_entry_identities, list)
            or any(
                not isinstance(identity, str) or not identity
                for identity in fetched_entry_identities
            )
            or fetched_entry_identities != sorted(set(fetched_entry_identities))
        ):
            errors.append(f"{source_key} fetched entry identities are invalid")
            fetched_entry_identities = []
        if coverage.get("fetched_entry_identity_digest") != _identity_digest(
            fetched_entry_identities
        ):
            errors.append(
                f"{source_key} fetched entry identity digest is invalid"
            )
        if not legacy_identity_proof:
            if coverage.get("entry_identity_digest") != _identity_digest(
                entry_identities
            ):
                errors.append(f"{source_key} entry identity digest is invalid")
            if set(entry_identities) != set(fetched_entry_identities):
                errors.append(
                    f"{source_key} entries contain stale or unaccounted identities"
                )
            alias_ledger = coverage.get("alias_ledger")
            errors.extend(
                _validate_finra_alias_ledger(
                    alias_ledger,
                    entries,
                    fetched_entry_identities,
                    fallback_urls=source_state.get("fallback_urls"),
                )
            )
            if coverage.get("alias_ledger_digest") != _alias_ledger_digest(
                alias_ledger if isinstance(alias_ledger, list) else []
            ):
                errors.append(f"{source_key} alias ledger digest is invalid")
            if (
                isinstance(detail_count, int)
                and not isinstance(detail_count, bool)
                and len(fetched_entry_identities) != detail_count
            ):
                errors.append(
                    f"{source_key} fetched identity count is not detail-bound"
                )
        else:
            migration_ledger = coverage.get("migration_ledger")
            if (
                not isinstance(migration_ledger, list)
                or any(
                    not isinstance(item, dict)
                    or not isinstance(item.get("identity"), str)
                    or not item.get("identity")
                    or not isinstance(item.get("reason"), str)
                    or not item.get("reason")
                    for item in migration_ledger
                )
            ):
                errors.append(f"{source_key} migration ledger is invalid")
                migration_ledger = []
            migration_identities = {
                item["identity"] for item in migration_ledger
            }
            expected_entry_identities = (
                set(fetched_entry_identities) | migration_identities
            )
            if set(entry_identities) != expected_entry_identities:
                errors.append(
                    f"{source_key} entries contain stale or unaccounted identities"
                )
        expected_page_numbers = (
            [0] if declared_pages == 0 and pages_fetched == 1
            else list(range(pages_fetched))
            if isinstance(pages_fetched, int)
            and not isinstance(pages_fetched, bool)
            and pages_fetched >= 0
            else None
        )
        if expected_page_numbers is not None and (
            coverage.get("page_numbers") != expected_page_numbers
        ):
            errors.append(f"{source_key} coverage page identities are invalid")
        proofs = coverage.get("pass_proofs")
        if not isinstance(proofs, list) or len(proofs) != 2:
            errors.append(f"{source_key} coverage must contain two pass proofs")
        else:
            comparable = (
                "declared_pages",
                "pages_fetched",
                "page_numbers",
                "page_identities",
                "page_row_counts",
                "page_row_digests",
                "page_row_payloads",
                "raw_row_count",
                "resolved_row_count",
                "unresolved_row_count",
                "unique_node_count",
            )
            if any(not isinstance(proof, dict) for proof in proofs):
                errors.append(f"{source_key} coverage pass proof is malformed")
            else:
                tokens = [proof.get("token") for proof in proofs]
                if (
                    not all(isinstance(token, str) and token for token in tokens)
                    or tokens[0] == tokens[1]
                ):
                    errors.append(f"{source_key} coverage pass tokens are invalid")
                for proof in proofs:
                    if proof.get("unresolved_row_count") != 0:
                        errors.append(
                            f"{source_key} pass proof contains unresolved rows"
                        )
                    if proof.get("raw_row_count") != raw_row_count:
                        errors.append(
                            f"{source_key} pass proof raw row count is inconsistent"
                        )
                    if proof.get("resolved_row_count") != resolved_row_count:
                        errors.append(
                            f"{source_key} pass proof resolved row count is "
                            "inconsistent"
                        )
                    if proof.get("unresolved_row_count") != unresolved_row_count:
                        errors.append(
                            f"{source_key} pass proof unresolved row count is "
                            "inconsistent"
                        )
                    if proof.get("unique_node_count") != unique_node_count:
                        errors.append(
                            f"{source_key} pass proof unique node count is "
                            "inconsistent"
                        )
                for index, proof in enumerate(proofs):
                    errors.extend(
                        _finra_pass_proof_recomputation_errors(
                            source_key, proof, index
                        )
                    )
                if all(isinstance(proof, dict) for proof in proofs):
                    for key in comparable:
                        if proofs[0].get(key) != proofs[1].get(key):
                            errors.append(
                                f"{source_key} pass proofs disagree on {key}"
                            )
                    if proofs[0].get("declared_pages") != declared_pages:
                        errors.append(
                            f"{source_key} coverage declared_pages is not proof-bound"
                        )
                    if proofs[0].get("pages_fetched") != pages_fetched:
                        errors.append(
                            f"{source_key} coverage pages_fetched is not proof-bound"
                        )
                    if proofs[0].get("page_numbers") != coverage.get("page_numbers"):
                        errors.append(
                            f"{source_key} coverage page identities are not proof-bound"
                        )
                    if proofs[0].get("page_identities") != coverage.get(
                        "page_identities"
                    ):
                        errors.append(
                            f"{source_key} coverage page identity proof is not bound"
                        )
        # Blockers 5 & 6: bind the retained listing rows to the canonical
        # fetched entries. Every resolvable row must map, through the validated
        # alias ledger, onto a fetched entry, and together the two passes must
        # reconstruct exactly the fetched entry set. This is the check that
        # actually rejects a redirected alias -- the repointed canonical becomes
        # unreachable from the independent listing rows -- or a forged/injected
        # pass row (it resolves outside the fetched entries), even when every
        # self-supplied evidence field and digest has been recomputed to agree.
        if (
            not legacy_identity_proof
            and isinstance(proofs, list)
            and len(proofs) == 2
            and all(isinstance(proof, dict) for proof in proofs)
        ):
            alias_map = _finra_alias_map(coverage.get("alias_ledger"))
            fetched_identity_set = set(fetched_entry_identities)
            for index, proof in enumerate(proofs):
                resolved_identities = _finra_pass_proof_entry_identities(
                    proof, alias_map
                )
                if not resolved_identities <= fetched_identity_set:
                    errors.append(
                        f"{source_key} pass proof {index} rows resolve to "
                        "identities outside the fetched entries"
                    )
                elif resolved_identities != fetched_identity_set:
                    errors.append(
                        f"{source_key} pass proof {index} rows do not "
                        "reconstruct the fetched entry identities"
                    )

        duplicate_ledger = coverage.get("duplicate_ledger")
        if not isinstance(duplicate_ledger, list):
            errors.append(f"{source_key} duplicate ledger is invalid")
        else:
            if (
                isinstance(resolved_row_count, int)
                and not isinstance(resolved_row_count, bool)
                and isinstance(unique_node_count, int)
                and not isinstance(unique_node_count, bool)
                and len(duplicate_ledger)
                < resolved_row_count - unique_node_count
            ):
                errors.append(
                    f"{source_key} duplicate ledger does not account for coalesced rows"
                )
            # Blocker 6: a duplicate record must carry real coalesced-row
            # evidence, not just occupy a slot. Validate each record's payload
            # digest and bind it to an actual repeated row that resolves, via
            # the alias ledger, to a fetched entry -- so an empty dict or a
            # forged payload pointing nowhere fails closed.
            if not legacy_identity_proof:
                dup_alias_map = _finra_alias_map(coverage.get("alias_ledger"))
                dup_fetched = set(fetched_entry_identities)
                for d_index, record in enumerate(duplicate_ledger):
                    label = f"{source_key} duplicate ledger record {d_index}"
                    if not isinstance(record, dict):
                        errors.append(f"{label} is malformed")
                        continue
                    node_identity = record.get("node_identity")
                    detail_hash = record.get("detail_hash")
                    raw_row_digest = record.get("raw_row_digest")
                    raw_payload = record.get("raw_payload")
                    if (
                        not isinstance(node_identity, str) or not node_identity
                        or not isinstance(detail_hash, str) or not detail_hash
                        or not isinstance(raw_row_digest, str) or not raw_row_digest
                        or not isinstance(raw_payload, dict)
                    ):
                        errors.append(
                            f"{label} is missing required duplicate evidence"
                        )
                        continue
                    recomputed_digest = compute_hash(json.dumps(
                        raw_payload,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ))
                    if recomputed_digest != raw_row_digest:
                        errors.append(
                            f"{label} raw row digest is not recomputable from its payload"
                        )
                    detail_url = _finra_row_detail_target(raw_payload)
                    if detail_url is None:
                        errors.append(
                            f"{label} payload does not resolve to a single detail target"
                        )
                    elif _finra_resolve_identity_via_ledger(
                        _extract_finra_document_id(detail_url), dup_alias_map
                    ) not in dup_fetched:
                        errors.append(
                            f"{label} does not coalesce into a fetched entry"
                        )
        if not isinstance(coverage.get("conflict_ledger"), list):
            errors.append(f"{source_key} conflict ledger is invalid")
        elif coverage.get("conflict_ledger"):
            errors.append(f"{source_key} coverage contains conflicts")
        if (
            isinstance(detail_count, int)
            and not isinstance(detail_count, bool)
            and isinstance(unique_node_count, int)
            and not isinstance(unique_node_count, bool)
            and detail_count != unique_node_count
        ):
            errors.append(f"{source_key} detail count is not node-bound")
    return errors


def _state_date(source_state: dict) -> Optional[str]:
    """Return an ISO date watermark from source state without fabricating one."""
    for key in ("last_checked", "last_run"):
        value = source_state.get(key)
        if isinstance(value, str) and re.match(r"^\d{4}-\d{2}-\d{2}", value):
            return value[:10]
    return None


def _validate_regulatory_state(
    state: object,
    source_keys: list[str],
    *,
    allow_legacy_finra_identity_proof: bool = False,
) -> list[str]:
    """Prove that scheduled monitoring has a usable prior regulatory state."""
    errors = []
    if not isinstance(state, dict):
        return ["unified state is not a JSON object"]
    sources = state.get("sources")
    if not isinstance(sources, dict):
        return ["unified state is missing an object-valued sources section"]

    for source_key in source_keys:
        source_state = sources.get(source_key)
        if not isinstance(source_state, dict):
            errors.append(f"{source_key} state section is missing or not an object")
            continue
        entries = source_state.get("entries")
        if not isinstance(entries, dict):
            errors.append(f"{source_key} state entries are missing or not an object")
        last_run = source_state.get("last_run")
        if not isinstance(last_run, str) or not last_run.strip():
            errors.append(f"{source_key} state last_run is missing")
            continue
        try:
            datetime.fromisoformat(last_run.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{source_key} state last_run is not a valid ISO timestamp")
        errors.extend(
            _validate_source_coverage(
                source_key,
                source_state,
                allow_legacy_finra_identity_proof=(
                    allow_legacy_finra_identity_proof
                    and source_key == SOURCE_KEY_FINRA
                ),
            )
        )
    return errors


def _baseline_approval_is_manual() -> bool:
    """Baseline initialization is local-only and requires an explicit approval."""
    return (
        os.environ.get("GITHUB_ACTIONS", "").lower() != "true"
        and os.environ.get("REGULATORY_MONITOR_BASELINE_APPROVED") == "I_UNDERSTAND"
    )


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
        'fields[]': [
            'document_number',
            'title',
            'abstract',
            'publication_date',
            'type',
            'html_url',
            'raw_text_url',
            'agencies',
        ],
    }

    if limit is not None and limit < 0:
        return _incomplete_result(error=f"Federal Register limit must be non-negative, got {limit}")

    items = []
    seen_document_ids = set()
    per_page = 100
    expected_count = None
    pages_fetched = 0
    page_numbers = []

    try:
        logger.info(
            "Querying Federal Register API for the validated document window..."
        )
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
            page_numbers.append(pages_fetched)
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
                    # The Federal Register HTML frontend intermittently returns
                    # 5xx responses under link-check concurrency. The official
                    # plain-text document is stable, human-readable, and still
                    # bound to the same immutable document number.
                    url=doc.get('raw_text_url') or doc.get('html_url') or '',
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
            coverage={
                "complete": True,
                "window_start": since_date,
                "query": {
                    "agencies": sorted(agencies),
                    "document_types": sorted(doc_types),
                    "per_page": per_page,
                    "order": "newest",
                },
                "expected_count": expected_count,
                "fetched_count": len(items),
                "pages_fetched": pages_fetched,
                "declared_pages": expected_pages,
                "page_numbers": page_numbers,
            },
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


def _extract_finra_shortlink(soup: BeautifulSoup) -> Optional[str]:
    """Read FINRA's stable numeric node URL for rate-limit fallback."""
    link = soup.select_one('link[rel="shortlink"][href]')
    if link is None:
        return None
    return _validate_finra_node_url(
        urljoin(FINRA_NOTICES_URL, link.get("href", ""))
    )


def _validate_finra_node_url(href: str) -> Optional[str]:
    """Accept only same-origin numeric FINRA node URLs as fallbacks."""
    parsed = urlparse(href)
    if (
        parsed.scheme.casefold() == "https"
        and parsed.netloc.casefold() == "www.finra.org"
        and re.fullmatch(r"/node/\d+", parsed.path)
        and not parsed.query
        and not parsed.fragment
    ):
        return href
    return None


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


def _finra_cache_busted_url(url: str, token: str) -> str:
    """Add a pass-specific cache token without changing the page identity."""
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{FINRA_CACHE_BUST_PARAM}={token}"


def _finra_query_page_url(page: int, query: Optional[dict[str, str]] = None) -> str:
    """Build a FINRA listing URL while preserving authoritative filters."""
    params = dict(query or {})
    if page:
        params["page"] = str(page)
    if not params:
        return FINRA_NOTICES_URL
    return f"{FINRA_NOTICES_URL}?{urlencode(params)}"


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

    active_page = pager.select_one('.page-item.active .page-link, .pager__item.is-active')
    if active_page:
        value = active_page.get_text(' ', strip=True)
        if not re.fullmatch(r"\d+", value):
            return None
        active_number = int(value) - 1
        if active_number < 0:
            return None
        page_numbers.append(active_number)
    return max(page_numbers) + 1 if page_numbers else None


def _extract_finra_active_page(soup: BeautifulSoup) -> Optional[int]:
    """Read the one-based active pager identity and return a zero-based page."""
    pager = soup.select_one('nav[aria-labelledby="pagination-heading"]')
    if pager is None:
        pager = soup.select_one('.pagination')
    if pager is None:
        return None
    active = pager.select_one(
        '.page-item.active .page-link, .pager__item.is-active, '
        '[aria-current="page"]'
    )
    if active is None:
        return None
    value = active.get_text(" ", strip=True)
    if not re.fullmatch(r"\d+", value):
        return None
    return int(value) - 1


def _finra_listing_page_number(url: str) -> Optional[int]:
    """Parse FINRA's zero-based page query without accepting URL mutations."""
    parsed = urlparse(urljoin(FINRA_NOTICES_URL, url))
    if parsed.path.rstrip("/") != urlparse(FINRA_NOTICES_URL).path.rstrip("/"):
        return None
    query = parse_qs(parsed.query, keep_blank_values=True)
    values = query.get("page", ["0"])
    if len(values) != 1 or not re.fullmatch(r"\d+", values[0]):
        return None
    return int(values[0])


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


def _finra_retry_url(url: str, attempt: int) -> str:
    """Retry the exact source URL so page identity cannot be changed."""
    return url


def _fetch_finra_page(
    url: str,
    session: requests.Session,
    *,
    max_attempts: Optional[int] = None,
) -> dict:
    """Use one request per attempt with a coordinated session-wide cooldown."""
    attempts = (
        FINRA_MAX_RETRY_ATTEMPTS
        if max_attempts is None
        else max(1, min(FINRA_MAX_RETRY_ATTEMPTS, max_attempts))
    )
    for attempt in range(attempts):
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
        request_url = _finra_retry_url(url, attempt)
        result = fetch_page(request_url, session, max_retries=1)
        try:
            session._finra_last_request_at = time.monotonic()
        except AttributeError:
            pass
        if result['status_code'] not in (0, 429) or attempt == attempts - 1:
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
        if isinstance(retry_after, int) and retry_after > 0:
            # Retry-After is an authoritative server cooldown. Do not shorten
            # it merely to fit the monitor's fallback backoff ceiling.
            wait_time = retry_after
        else:
            wait_time = min(
                FINRA_MAX_RETRY_WAIT_SECONDS,
                max(FINRA_RETRY_BASE_WAIT_SECONDS, previous_wait),
            )
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
        # The next loop iteration consumes the shared cooldown. Sleeping here
        # as well would double-wait every 429 and create a nested retry storm.
    return result


def _finra_known_notice_urls(source_state: dict) -> list[str]:
    """Resolve persisted FINRA identities to canonical URLs for refresh."""
    identities = set(source_state.get("entries", {}))
    coverage = source_state.get("coverage")
    if isinstance(coverage, dict):
        for alias in coverage.get("alias_ledger", []):
            if isinstance(alias, dict) and isinstance(
                alias.get("old_identity"), str
            ):
                identities.add(
                    _resolve_finra_identity(
                        source_state,
                        alias["old_identity"],
                    )
                )

    urls = []
    for key in identities:
        if isinstance(key, str) and key.startswith("http"):
            canonical_url, _ = _finra_normalize_detail_link(key)
            if canonical_url:
                urls.append(canonical_url)
            continue
        match = re.fullmatch(r"FINRA (\d{2}-\d{2})", str(key))
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
    """Collect every resolved notice link from scoped listing rows."""
    return [
        (row["detail_url"], row["title"], row["listing_date"])
        for row in _extract_finra_listing_rows(soup)[0]
        if row["detail_url"]
    ]


def _finra_normalize_detail_link(href: str) -> tuple[Optional[str], Optional[str]]:
    """Resolve supported same-origin FINRA notice forms to stable identities."""
    base = urlparse(FINRA_NOTICES_URL)
    parsed = urlparse(urljoin(FINRA_NOTICES_URL, href.strip()))
    if parsed.scheme != base.scheme or parsed.netloc.lower() != base.netloc.lower():
        return None, None
    path = parsed.path.rstrip("/") or "/"
    if path.startswith("/index.php/rules-guidance/notices/"):
        path = path[len("/index.php"):]
    node_match = re.fullmatch(r"/node/(\d+)", path)
    if node_match:
        node_id = f"node:{node_match.group(1)}"
        return f"{base.scheme}://{base.netloc}/node/{node_match.group(1)}", node_id
    if re.fullmatch(r"/rules-guidance/notices/[^/]+", path):
        canonical = f"{base.scheme}://{base.netloc}{path}"
        return canonical, f"url:{path}"
    return None, None


def _finra_listing_row_payload(row) -> dict:
    """Build a stable raw-row payload without discarding duplicate rows."""
    links = []
    row_links = (
        [row] if row.name == "a" and row.get("href") else row.find_all("a", href=True)
    )
    for link in row_links:
        links.append({
            "href": " ".join(str(link.get("href", "")).split()),
            "text": " ".join(link.get_text(" ", strip=True).split()),
        })
    return {
        "text": " ".join(row.get_text(" ", strip=True).split()),
        "links": links,
    }


def _extract_finra_listing_rows(
    soup: BeautifulSoup,
) -> tuple[list[dict], int]:
    """Parse all scoped rows and count rows that cannot resolve a detail target."""
    table_rows = soup.select("table tbody tr")
    if table_rows:
        rows = table_rows
    else:
        # Some live/legacy views use Drupal row containers instead of a table.
        # Prefer those containers so unsupported links remain visible as
        # unresolved rows instead of being silently filtered out.
        rows = []
        for selector in (".views-row", ".view-content > li", ".view-content > div"):
            rows = soup.select(selector)
            if rows:
                break
        if not rows:
            # Small synthetic pages may omit both the table and row wrapper.
            # Treat supported notice anchors as individual rows.
            rows = [
                link
                for link in soup.find_all("a", href=True)
                if _finra_normalize_detail_link(link.get("href", ""))[0]
            ]
    parsed_rows = []
    unresolved = 0
    for row_index, row in enumerate(rows):
        payload = _finra_listing_row_payload(row)
        candidates = []
        row_links = (
            [row]
            if row.name == "a" and row.get("href")
            else row.find_all("a", href=True)
        )
        for link in row_links:
            detail_url, node_identity = _finra_normalize_detail_link(
                link.get("href", "")
            )
            if detail_url:
                candidates.append((detail_url, node_identity, link))
        distinct_targets = {(url, node) for url, node, _ in candidates}
        if len(distinct_targets) != 1:
            unresolved += 1
            detail_url = None
            node_identity = None
            title = ""
            listing_date = ""
        else:
            detail_url, node_identity = next(iter(distinct_targets))
            link = next(
                link for url, node, link in candidates
                if (url, node) == (detail_url, node_identity)
            )
            title = " ".join(link.get_text(" ", strip=True).split())
            listing_date = _extract_listing_date(link)
        parsed_rows.append({
            "row_index": row_index,
            "raw_payload": payload,
            "raw_row_digest": compute_hash(json.dumps(
                payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )),
            "detail_url": detail_url,
            "node_identity": node_identity,
            "title": title,
            "listing_date": listing_date,
        })
    return parsed_rows, unresolved


def _merge_finra_listing_records(
    records: list[tuple[str, str, str]],
    seen_urls: set[str],
    seen_records: dict[str, tuple[str, str, str]],
    page_records: list[tuple[str, str, str]],
) -> Optional[str]:
    """Merge one listing page, rejecting conflicting overlaps."""
    for record in records:
        url = record[0]
        if url in seen_urls:
            return f"FINRA pagination overlap/repeated record for {url}"
        seen_urls.add(url)
        seen_records[url] = record
        page_records.append(record)
    return None


def _fetch_finra_listing_records_legacy(
    session: requests.Session,
    since_date: Optional[str],
) -> dict:
    """Fetch every page of FINRA's unfiltered listing, fail closed on gaps."""
    page_records: list[tuple[str, str, str]] = []
    seen_urls: set[str] = set()
    seen_records: dict[str, tuple[str, str, str]] = {}
    pages_fetched = 0
    cutoff_page = None
    seen_page_numbers: set[int] = set()

    # FINRA's selected-year taxonomy is advisory only: live pages omit valid
    # notices from the selected year. Completeness therefore requires the
    # unfiltered listing pager, including every declared page.
    # Traverse the complete unfiltered listing and fail closed on any
    # missing, contradictory, or repeated page identity.
    declared_pages = None
    page_numbers = []
    first_url = _finra_page_url(0)
    first_result = _fetch_finra_page(first_url, session)
    if first_result["status_code"] != 200:
        return {
            "complete": False,
            "error": (
                f"FINRA notices page 0 returned status "
                f"{first_result['status_code']}: "
                f"{first_result.get('error') or 'unavailable'}"
            ),
            "expected_count": 0,
            "pages_fetched": 0,
            "declared_pages": None,
            "cutoff_page": cutoff_page,
        }
    first_soup = BeautifulSoup(first_result["content"], "html.parser")
    for page in range(FINRA_MAX_PAGES):
        result = first_result if page == 0 else _fetch_finra_page(
            _finra_page_url(page), session
        )
        if result["status_code"] != 200:
            return {
                "complete": False,
                "error": (
                    f"FINRA notices page {page} returned status "
                    f"{result['status_code']}: "
                    f"{result.get('error') or 'unavailable'}"
                ),
                "expected_count": len(page_records),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "cutoff_page": cutoff_page,
            }
        soup = first_soup if page == 0 else BeautifulSoup(
            result["content"], "html.parser"
        )
        expected_url = _finra_page_url(page)
        returned_url = result.get("url") or expected_url
        if returned_url != expected_url:
            return {
                "complete": False,
                "error": (
                    f"FINRA listing request URL changed for page {page}: "
                    f"expected {expected_url}, got {returned_url}"
                ),
                "expected_count": len(page_records),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "cutoff_page": cutoff_page,
            }
        final_page = _finra_listing_page_number(
            result.get("final_url") or expected_url
        )
        active_page = _extract_finra_active_page(soup)
        zero_shape = page == 0 and _finra_is_explicit_zero_result(soup)
        page_declared = _extract_finra_declared_pages(soup)
        if page_declared is None:
            return {
                "complete": False,
                "error": "FINRA pagination metadata was missing or unparseable",
                "expected_count": len(page_records),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "cutoff_page": cutoff_page,
            }
        if final_page != page or (active_page != page and not zero_shape):
            return {
                "complete": False,
                "error": (
                    f"FINRA listing page identity mismatch for page {page}: "
                    f"final={final_page}, active={active_page}"
                ),
                "expected_count": len(page_records),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "cutoff_page": cutoff_page,
            }
        if page in seen_page_numbers:
            return {
                "complete": False,
                "error": f"FINRA listing page {page} was repeated",
                "expected_count": len(page_records),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "cutoff_page": cutoff_page,
            }
        seen_page_numbers.add(page)
        page_numbers.append(page)
        if declared_pages is None:
            declared_pages = page_declared
            if declared_pages > FINRA_MAX_PAGES:
                return {
                    "complete": False,
                    "error": (
                        f"FINRA pagination declared {declared_pages} pages, "
                        f"exceeding safe cutoff {FINRA_MAX_PAGES}"
                    ),
                    "pages_fetched": pages_fetched,
                    "declared_pages": declared_pages,
                }
        elif page_declared is None or page_declared != declared_pages:
            return {
                "complete": False,
                "error": "FINRA pagination metadata changed or disappeared while traversing pages",
                "expected_count": len(page_records),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "cutoff_page": cutoff_page,
            }
        records = _extract_finra_notice_links(soup)
        pages_fetched += 1
        if not records:
            if page == 0 and declared_pages == 0 and _finra_is_explicit_zero_result(soup):
                break
            return {
                "complete": False,
                "error": f"FINRA page {page} contained no recognizable notice links",
                "expected_count": len(page_records),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "cutoff_page": cutoff_page,
            }
        if declared_pages == 0:
            return {
                "complete": False,
                "error": "FINRA pagination declared zero pages but returned notice links",
                "expected_count": len(page_records),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
            }
        candidate_seen_urls = set(seen_urls)
        candidate_seen_records = dict(seen_records)
        candidate_page_records = list(page_records)
        conflict = _merge_finra_listing_records(
            records,
            candidate_seen_urls,
            candidate_seen_records,
            candidate_page_records,
        )
        if conflict:
            # FINRA's live listing can briefly straddle a moving boundary
            # while pages are being served. Re-fetch the exact page once to
            # distinguish that transient race from a stable overlap. A
            # duplicate that survives the re-fetch remains unverifiable.
            retry = _fetch_finra_page(expected_url, session)
            retry_soup = (
                BeautifulSoup(retry["content"], "html.parser")
                if retry["status_code"] == 200
                else None
            )
            retry_records = (
                _extract_finra_notice_links(retry_soup)
                if retry_soup is not None
                else []
            )
            retry_identity = (
                _finra_listing_page_number(retry.get("final_url") or expected_url)
                if retry_soup is not None
                else None
            )
            retry_active = (
                _extract_finra_active_page(retry_soup)
                if retry_soup is not None
                else None
            )
            retry_declared = (
                _extract_finra_declared_pages(retry_soup)
                if retry_soup is not None
                else None
            )
            if (
                retry["status_code"] == 200
                and (retry.get("url") or expected_url) == expected_url
                and retry_identity == page
                and retry_active == page
                and retry_declared == declared_pages
                and retry_records
            ):
                retry_conflict = _merge_finra_listing_records(
                    retry_records,
                    set(seen_urls),
                    dict(seen_records),
                    list(page_records),
                )
                if retry_conflict is None:
                    records = retry_records
                    conflict = None
                    candidate_seen_urls = set(seen_urls)
                    candidate_seen_records = dict(seen_records)
                    candidate_page_records = list(page_records)
                    _merge_finra_listing_records(
                        retry_records,
                        candidate_seen_urls,
                        candidate_seen_records,
                        candidate_page_records,
                    )
            if conflict:
                return {
                    "complete": False,
                    "error": conflict,
                    "expected_count": len(page_records),
                    "pages_fetched": pages_fetched,
                    "declared_pages": declared_pages,
                    "cutoff_page": cutoff_page,
                }
        seen_urls = candidate_seen_urls
        seen_records = candidate_seen_records
        page_records = candidate_page_records
        if (
            cutoff_page is None
            and since_date
            and all(
                listing_date and listing_date < since_date
                for _, _, listing_date in records
            )
        ):
            cutoff_page = page
        if page + 1 >= declared_pages:
            break
    else:
        return {
            "complete": False,
            "error": f"FINRA pagination exceeded safe cutoff of {FINRA_MAX_PAGES} pages",
            "expected_count": len(page_records),
            "pages_fetched": pages_fetched,
            "declared_pages": declared_pages,
            "cutoff_page": cutoff_page,
        }
    if declared_pages is None or (
        declared_pages != 0 and pages_fetched != declared_pages
    ):
        return {
            "complete": False,
            "error": (
                "FINRA pagination incomplete: "
                f"declared {declared_pages} pages, fetched {pages_fetched}"
            ),
            "expected_count": len(page_records),
            "pages_fetched": pages_fetched,
            "declared_pages": declared_pages,
            "cutoff_page": cutoff_page,
        }
    return {
        "complete": True,
        "records": page_records,
        "pages_fetched": pages_fetched,
        "declared_pages": declared_pages,
        "cutoff_page": cutoff_page,
        "coverage": {
            "complete": True,
            "listing_mode": "complete-unfiltered",
            "listing_url": FINRA_NOTICES_URL,
            "listing_record_count": len(page_records),
            "pages_fetched": pages_fetched,
            "declared_pages": declared_pages,
            "page_numbers": page_numbers,
        },
    }


def _finra_pass_token(pass_number: int) -> str:
    """Create a distinct opaque cache token for each listing pass."""
    return f"{pass_number}-{uuid.uuid4().hex}"


def _fetch_finra_listing_pass(
    session: requests.Session,
    since_date: Optional[str],
    token: str,
) -> dict:
    """Fetch one complete, tokenized FINRA listing pass without coalescing rows."""
    rows: list[dict] = []
    page_numbers: list[int] = []
    page_identities: list[dict[str, Optional[int]]] = []
    page_row_counts: list[int] = []
    page_row_digests: list[str] = []
    page_row_payloads: list[list[dict]] = []
    pages_fetched = 0
    declared_pages = None
    cutoff_page = None

    for page in range(FINRA_MAX_PAGES):
        expected_url = _finra_cache_busted_url(_finra_page_url(page), token)
        result = _fetch_finra_page(expected_url, session)
        if result["status_code"] != 200:
            return {
                "complete": False,
                "error": (
                    f"FINRA notices page {page} returned status "
                    f"{result['status_code']}: "
                    f"{result.get('error') or 'unavailable'}"
                ),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
            }
        returned_url = result.get("url") or expected_url
        if returned_url != expected_url:
            return {
                "complete": False,
                "error": (
                    f"FINRA listing request URL changed for page {page}: "
                    f"expected {expected_url}, got {returned_url}"
                ),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
            }
        soup = BeautifulSoup(result["content"], "html.parser")
        final_page = _finra_listing_page_number(
            result.get("final_url") or expected_url
        )
        active_page = _extract_finra_active_page(soup)
        zero_shape = page == 0 and _finra_is_explicit_zero_result(soup)
        page_declared = _extract_finra_declared_pages(soup)
        if page_declared is None:
            return {
                "complete": False,
                "error": "FINRA pagination metadata was missing or unparseable",
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
            }
        if final_page != page or (active_page != page and not zero_shape):
            return {
                "complete": False,
                "error": (
                    f"FINRA listing page identity mismatch for page {page}: "
                    f"final={final_page}, active={active_page}"
                ),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
            }
        if declared_pages is None:
            declared_pages = page_declared
            if declared_pages > FINRA_MAX_PAGES:
                return {
                    "complete": False,
                    "error": (
                        f"FINRA pagination declared {declared_pages} pages, "
                        f"exceeding safe cutoff {FINRA_MAX_PAGES}"
                    ),
                    "pages_fetched": pages_fetched,
                    "declared_pages": declared_pages,
                }
        elif page_declared != declared_pages:
            return {
                "complete": False,
                "error": (
                    "FINRA pagination metadata changed or disappeared "
                    "while traversing pages"
                ),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
            }

        page_rows, unresolved = _extract_finra_listing_rows(soup)
        pages_fetched += 1
        page_numbers.append(page)
        page_identities.append({
            "requested": page,
            "final": final_page,
            "active": active_page,
        })
        page_row_counts.append(len(page_rows))
        page_row_digests.append(compute_hash(json.dumps(
            [row["raw_payload"] for row in page_rows],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )))
        page_row_payloads.append([row["raw_payload"] for row in page_rows])
        for row in page_rows:
            row["page"] = page
            row["unresolved"] = not row["detail_url"]
        rows.extend(page_rows)

        if unresolved:
            return {
                "complete": False,
                "error": (
                    f"FINRA page {page} contained {unresolved} "
                    "unresolved listing row(s)"
                ),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "rows": rows,
            }
        if not page_rows:
            if page == 0 and declared_pages == 0 and zero_shape:
                break
            return {
                "complete": False,
                "error": f"FINRA page {page} contained no scoped listing rows",
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "rows": rows,
            }
        if declared_pages == 0:
            return {
                "complete": False,
                "error": (
                    "FINRA pagination declared zero pages but returned "
                    "listing rows"
                ),
                "pages_fetched": pages_fetched,
                "declared_pages": declared_pages,
                "rows": rows,
            }
        if (
            cutoff_page is None
            and since_date
            and all(
                row["listing_date"] and row["listing_date"] < since_date
                for row in page_rows
            )
        ):
            cutoff_page = page
        if page + 1 >= declared_pages:
            break
    else:
        return {
            "complete": False,
            "error": f"FINRA pagination exceeded safe cutoff of {FINRA_MAX_PAGES} pages",
            "pages_fetched": pages_fetched,
            "declared_pages": declared_pages,
            "rows": rows,
        }

    if declared_pages is None or (
        declared_pages != 0 and pages_fetched != declared_pages
    ):
        return {
            "complete": False,
            "error": (
                "FINRA pagination incomplete: "
                f"declared {declared_pages} pages, fetched {pages_fetched}"
            ),
            "pages_fetched": pages_fetched,
            "declared_pages": declared_pages,
            "rows": rows,
        }

    resolved_rows = [row for row in rows if row["detail_url"]]
    pass_proof = {
        # The opaque cache token is intentionally request-only. Persist a
        # stable pass identity so identical source data does not dirty state
        # on every scheduled run.
        "token": f"pass-{token.split('-', 1)[0]}",
        "declared_pages": declared_pages,
        "pages_fetched": pages_fetched,
        "page_numbers": page_numbers,
        "page_identities": page_identities,
        "page_row_counts": page_row_counts,
        "page_row_digests": page_row_digests,
        "page_row_payloads": page_row_payloads,
        "raw_row_count": len(rows),
        "resolved_row_count": len(resolved_rows),
        "unresolved_row_count": len(rows) - len(resolved_rows),
        "unique_node_count": len({
            row["node_identity"] for row in resolved_rows
        }),
    }
    return {
        "complete": True,
        "rows": rows,
        "records": [
            (row["detail_url"], row["title"], row["listing_date"])
            for row in rows
        ],
        "pages_fetched": pages_fetched,
        "declared_pages": declared_pages,
        "cutoff_page": cutoff_page,
        "pass_proof": pass_proof,
    }


def _fetch_finra_listing_page(
    session: requests.Session,
    page: int,
    token: str,
) -> dict:
    """Fetch and validate one tokenized FINRA listing page."""
    expected_url = _finra_cache_busted_url(_finra_page_url(page), token)
    result = _fetch_finra_page(expected_url, session)
    if result["status_code"] != 200:
        return {
            "complete": False,
            "error": (
                f"FINRA notices page {page} returned status "
                f"{result['status_code']}: "
                f"{result.get('error') or 'unavailable'}"
            ),
        }
    returned_url = result.get("url") or expected_url
    if returned_url != expected_url:
        return {
            "complete": False,
            "error": (
                f"FINRA listing request URL changed for page {page}: "
                f"expected {expected_url}, got {returned_url}"
            ),
        }
    soup = BeautifulSoup(result["content"], "html.parser")
    final_page = _finra_listing_page_number(
        result.get("final_url") or expected_url
    )
    active_page = _extract_finra_active_page(soup)
    zero_shape = page == 0 and _finra_is_explicit_zero_result(soup)
    page_declared = _extract_finra_declared_pages(soup)
    if page_declared is None:
        return {
            "complete": False,
            "error": "FINRA pagination metadata was missing or unparseable",
        }
    if final_page != page or (active_page != page and not zero_shape):
        return {
            "complete": False,
            "error": (
                f"FINRA listing page identity mismatch for page {page}: "
                f"final={final_page}, active={active_page}"
            ),
        }
    page_rows, unresolved = _extract_finra_listing_rows(soup)
    return {
        "complete": True,
        "page_declared": page_declared,
        "final_page": final_page,
        "active_page": active_page,
        "zero_shape": zero_shape,
        "page_rows": page_rows,
        "unresolved": unresolved,
    }


def _finra_listing_pass_proof(state: dict) -> dict:
    """Build a deterministic proof from one accumulated listing pass."""
    rows = state["rows"]
    resolved_rows = [row for row in rows if row["detail_url"]]
    return {
        "token": f"pass-{state['token'].split('-', 1)[0]}",
        "declared_pages": state["declared_pages"],
        "pages_fetched": state["pages_fetched"],
        "page_numbers": state["page_numbers"],
        "page_identities": state["page_identities"],
        "page_row_counts": state["page_row_counts"],
        "page_row_digests": state["page_row_digests"],
        "page_row_payloads": state["page_row_payloads"],
        "raw_row_count": len(rows),
        "resolved_row_count": len(resolved_rows),
        "unresolved_row_count": len(rows) - len(resolved_rows),
        "unique_node_count": len({
            row["node_identity"] for row in resolved_rows
        }),
    }


def _new_finra_pass_session(template: requests.Session) -> requests.Session:
    """Create an independent FINRA session while preserving request headers."""
    session = requests.Session()
    headers = getattr(template, "headers", None)
    if headers:
        session.headers.update(dict(headers))
    return session


def _compare_finra_listing_pass_proofs(
    first: dict,
    second: dict,
) -> Optional[str]:
    """Compare all ordered page and raw-row proof fields from two passes."""
    for key, label in (
        ("declared_pages", "declared page count"),
        ("pages_fetched", "fetched page count"),
        ("page_numbers", "page numbers"),
        ("page_identities", "page identities"),
        ("page_row_counts", "page row counts"),
        ("page_row_digests", "page row digests"),
        ("page_row_payloads", "page row payloads"),
        ("raw_row_count", "raw row count"),
        ("resolved_row_count", "resolved row count"),
        ("unresolved_row_count", "unresolved row count"),
        ("unique_node_count", "unique node count"),
    ):
        if first.get(key) != second.get(key):
            return (
                f"FINRA independent-pass mismatch in {label}: "
                f"{first.get(key)!r} != {second.get(key)!r}"
            )
    return None


def _fetch_finra_listing_passes_sequential(
    session: requests.Session,
    since_date: Optional[str],
) -> dict:
    """Fetch two complete passes sequentially using independent sessions."""
    pass_results = []
    for index in (1, 2):
        pass_session = _new_finra_pass_session(session)
        try:
            result = _fetch_finra_listing_pass(
                pass_session,
                since_date,
                _finra_pass_token(index),
            )
            pass_results.append(result)
        finally:
            close = getattr(pass_session, "close", None)
            if callable(close):
                close()
        if not result.get("complete"):
            return {
                "complete": False,
                "error": result.get("error") or (
                    f"FINRA independent pass {index} was incomplete"
                ),
                "pages_fetched": result.get("pages_fetched", 0),
                "declared_pages": result.get("declared_pages"),
                "pass_proofs": [
                    *[
                        prior.get("pass_proof", {})
                        for prior in pass_results[:-1]
                    ],
                    result.get("pass_proof", {}),
                ],
            }

    first, second = pass_results
    mismatch = _compare_finra_listing_pass_proofs(
        first["pass_proof"],
        second["pass_proof"],
    )
    if mismatch:
        return {
            "complete": False,
            "error": mismatch,
            "pages_fetched": min(
                first["pages_fetched"],
                second["pages_fetched"],
            ),
            "declared_pages": first.get("declared_pages"),
            "pass_proofs": [
                first["pass_proof"],
                second["pass_proof"],
            ],
        }

    proofs = [pass_results[0]["pass_proof"], pass_results[1]["pass_proof"]]
    return {
        "complete": True,
        "rows": pass_results[0]["rows"],
        "records": [
            (row["detail_url"], row["title"], row["listing_date"])
            for row in pass_results[0]["rows"]
        ],
        "pages_fetched": pass_results[0]["pages_fetched"],
        "declared_pages": pass_results[0]["declared_pages"],
        "cutoff_page": pass_results[0]["cutoff_page"],
        "pass_proofs": proofs,
        "coverage": {
            "complete": True,
            "listing_mode": "complete-unfiltered",
            "listing_url": FINRA_NOTICES_URL,
            "listing_record_count": proofs[0]["resolved_row_count"],
            "raw_row_count": proofs[0]["raw_row_count"],
            "resolved_row_count": proofs[0]["resolved_row_count"],
            "unresolved_row_count": proofs[0]["unresolved_row_count"],
            "unique_node_count": proofs[0]["unique_node_count"],
            "pages_fetched": proofs[0]["pages_fetched"],
            "declared_pages": proofs[0]["declared_pages"],
            "page_numbers": proofs[0]["page_numbers"],
            "page_identities": proofs[0]["page_identities"],
            "pass_proofs": proofs,
            "duplicate_ledger": [],
            "conflict_ledger": [],
        },
    }


def _fetch_finra_listing_records(
    session: requests.Session,
    since_date: Optional[str],
) -> dict:
    """Require two stable, independently cache-busted listing passes."""
    return _fetch_finra_listing_passes_sequential(session, since_date)


def fetch_finra_notices(
    session: requests.Session,
    config: dict,
    limit: Optional[int] = None,
    since_date: Optional[str] = None,
    known_urls: Optional[list[str]] = None,
    fallback_urls: Optional[dict[str, str]] = None,
) -> FetchResult:
    """Fetch FINRA listing rows and authoritative notice details fail-closed."""
    items: list[RegulatoryItem] = []
    resolved_fallback_urls = dict(fallback_urls or {})

    if limit is not None and limit < 0:
        return _incomplete_result(error=f"FINRA limit must be non-negative, got {limit}")

    try:
        logger.info("Fetching FINRA notices from %s...", FINRA_NOTICES_URL)
        listing = _fetch_finra_listing_records(session, since_date)
        if not listing.get("complete"):
            return _incomplete_result(
                error=listing.get("error") or "FINRA listing was incomplete",
                expected_count=listing.get("expected_count"),
                pages_fetched=listing.get("pages_fetched", 0),
                declared_pages=listing.get("declared_pages"),
                cutoff_page=listing.get("cutoff_page"),
                coverage={"pass_proofs": listing.get("pass_proofs", [])},
            )

        rows = [dict(row) for row in listing.get("rows", [])]
        # Keep compatibility with callers/tests that provide the pre-row
        # listing shape; production crawls always include raw row proofs.
        if not rows and listing.get("records"):
            for row_index, (detail_url, title, listing_date) in enumerate(
                listing["records"]
            ):
                canonical_url, node_identity = _finra_normalize_detail_link(
                    detail_url
                )
                if not canonical_url:
                    return _incomplete_result(
                        error=f"FINRA listing record was unresolved: {detail_url}",
                        coverage=listing.get("coverage", {}),
                    )
                payload = {
                    "text": " ".join(f"{title} {listing_date}".split()),
                    "links": [{"href": canonical_url, "text": title}],
                }
                rows.append({
                    "row_index": row_index,
                    "page": None,
                    "raw_payload": payload,
                    "raw_row_digest": compute_hash(json.dumps(
                        payload,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )),
                    "detail_url": canonical_url,
                    "node_identity": node_identity,
                    "title": title,
                    "listing_date": listing_date,
                    "unresolved": False,
                })
        seen_urls = {row["detail_url"] for row in rows if row.get("detail_url")}
        seen_node_urls = {
            node_url
            for listing_url in seen_urls
            if (
                node_url := (
                    _validate_finra_node_url(listing_url)
                    or _validate_finra_node_url(
                        resolved_fallback_urls.get(listing_url, "")
                    )
                )
            )
        }
        unproven_known_urls = []
        for known_url in sorted(set(known_urls or [])):
            canonical_url, node_identity = _finra_normalize_detail_link(known_url)
            if not canonical_url:
                return _incomplete_result(
                    error=f"FINRA known refresh URL was unsupported: {known_url}",
                    coverage=listing.get("coverage", {}),
                )
            known_node_url = (
                canonical_url
                if node_identity and node_identity.startswith("node:")
                else _validate_finra_node_url(
                    resolved_fallback_urls.get(canonical_url, "")
                )
            )
            represented_by_listing = (
                canonical_url in seen_urls
                or (
                    known_node_url is not None
                    and known_node_url in seen_node_urls
                )
            )
            if not represented_by_listing:
                raw_payload = {"known_refresh_url": canonical_url}
                rows.append({
                    "row_index": -1,
                    "page": None,
                    "raw_payload": raw_payload,
                    "raw_row_digest": compute_hash(json.dumps(
                        raw_payload,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )),
                    "detail_url": canonical_url,
                    "node_identity": node_identity,
                    "title": "",
                    "listing_date": "",
                    "unresolved": False,
                })
                seen_urls.add(canonical_url)
                unproven_known_urls.append(canonical_url)

        if limit is not None:
            rows = rows[:limit]
            logger.info("Limited to %s notices for testing; state will not advance", limit)

        detail_cache: dict[str, dict] = {}
        node_groups: dict[str, dict] = {}
        duplicate_ledger: list[dict] = []
        conflict_ledger: list[dict] = []

        for row in rows:
            url = row["detail_url"]
            listing_title = row.get("title", "")
            listing_date = row.get("listing_date", "")
            fallback_url = _validate_finra_node_url(
                resolved_fallback_urls.get(url, "")
            )
            detail = detail_cache.get(url)
            if detail is None:
                detail = _fetch_finra_page(
                    url,
                    session,
                    max_attempts=1 if fallback_url and fallback_url != url else None,
                )
                detail_cache[url] = detail
            if detail["status_code"] != 200 and fallback_url and fallback_url != url:
                logger.warning(
                    "FINRA canonical detail for %s was unavailable; retrying "
                    "authoritative node fallback %s",
                    url,
                    fallback_url,
                )
                detail = _fetch_finra_page(fallback_url, session)
                # The node URL is transport only. Record that this response did
                # not come from the canonical document URL so the notice keeps
                # its listing identity instead of adopting the transport URL.
                detail["transport_fallback_url"] = fallback_url
                detail_cache[url] = detail
            if detail["status_code"] != 200:
                return _incomplete_result(
                    items,
                    error=(
                        f"FINRA notice detail page returned status "
                        f"{detail['status_code']}: {url}: "
                        f"{detail.get('error') or 'unavailable'}"
                    ),
                    expected_count=len(rows),
                    pages_fetched=listing["pages_fetched"],
                    declared_pages=listing["declared_pages"],
                    cutoff_page=listing["cutoff_page"],
                    limited=limit is not None,
                    fallback_urls=resolved_fallback_urls,
                    coverage=listing.get("coverage", {}),
                )

            detail_soup = BeautifulSoup(detail["content"], "html.parser")
            shortlink = _extract_finra_shortlink(detail_soup)
            _, shortlink_node_identity = (
                _finra_normalize_detail_link(shortlink)
                if shortlink
                else (None, None)
            )
            if shortlink:
                resolved_fallback_urls[url] = shortlink
            title_node = (
                detail_soup.select_one(".field--name-field-notice-title-tx")
                or detail_soup.find("h1")
            )
            title = (
                " ".join(title_node.get_text(" ", strip=True).split())
                if title_node
                else " ".join(listing_title.split())
            )
            publication_date = _extract_finra_publication_date(detail_soup)
            abstract = _extract_finra_summary(detail_soup)
            substantive_content = _extract_finra_substantive_content(
                detail_soup, url
            )
            if not substantive_content:
                return _incomplete_result(
                    items,
                    error=f"FINRA notice detail had no substantive content: {url}",
                    expected_count=len(rows),
                    pages_fetched=listing["pages_fetched"],
                    declared_pages=listing["declared_pages"],
                    cutoff_page=listing["cutoff_page"],
                    limited=limit is not None,
                    coverage=listing.get("coverage", {}),
                )

            final_url, final_node_identity = _finra_normalize_detail_link(
                detail.get("final_url") or url
            )
            # A node URL used purely as a rate-limit transport must never
            # replace the listing/canonical document identity; doing so would
            # orphan the existing canonical entry and force an alias migration
            # that has no legitimate evidence behind it.
            transport_fallback = bool(detail.get("transport_fallback_url"))
            identity_url = url if transport_fallback else (final_url or url)
            node_identity = (
                shortlink_node_identity
                or
                final_node_identity
                or row.get("node_identity")
                or f"url:{url}"
            )
            detail_hash = compute_hash(substantive_content)
            listing_date_conflict = bool(
                listing_date
                and publication_date
                and listing_date != publication_date
            )
            existing = node_groups.get(node_identity)
            if existing is not None:
                if existing["detail_hash"] != detail_hash:
                    conflict = {
                        "node_identity": node_identity,
                        "existing_detail_hash": existing["detail_hash"],
                        "new_detail_hash": detail_hash,
                        "existing_raw_row_digest": existing["raw_row_digest"],
                        "new_raw_row_digest": row["raw_row_digest"],
                        "existing_url": existing["url"],
                        "new_url": url,
                    }
                    conflict_ledger.append(conflict)
                    return _incomplete_result(
                        items,
                        error=f"FINRA duplicate detail conflict for {node_identity}",
                        expected_count=len(rows),
                        pages_fetched=listing["pages_fetched"],
                        declared_pages=listing["declared_pages"],
                        cutoff_page=listing["cutoff_page"],
                        limited=limit is not None,
                        coverage={
                            **listing.get("coverage", {}),
                            "duplicate_ledger": duplicate_ledger,
                            "conflict_ledger": conflict_ledger,
                        },
                    )
                duplicate_ledger.append({
                    "node_identity": node_identity,
                    "detail_hash": detail_hash,
                    "page": row.get("page"),
                    "row_index": row.get("row_index"),
                    "raw_row_digest": row["raw_row_digest"],
                    "raw_row_conflicts_with_first": (
                        existing["raw_row_digest"] != row["raw_row_digest"]
                    ),
                    "listing_date_conflict": listing_date_conflict,
                    "resolves_listing_date_conflict": bool(
                        existing.get("listing_date_conflicts")
                    ),
                    "raw_payload": row["raw_payload"],
                })
                if existing.get("listing_date_conflicts"):
                    existing["listing_date_conflicts"] = []
                continue

            document_id = _extract_finra_document_id(identity_url)
            tier, reason = classify_regulatory_relevance(
                title, substantive_content, config
            )
            affected_controls = find_affected_controls_by_keywords(
                title, substantive_content, config
            )
            node_groups[node_identity] = {
                "detail_hash": detail_hash,
                "raw_row_digest": row["raw_row_digest"],
                "url": url,
                "listing_date_conflicts": (
                    [{
                        "listing_date": listing_date,
                        "publication_date": publication_date,
                        "url": url,
                    }]
                    if listing_date_conflict
                    else []
                ),
            }
            items.append(
                RegulatoryItem(
                    source="FINRA",
                    agency="FINRA",
                    title=title,
                    url=url,
                    publication_date=publication_date,
                    doc_type="NOTICE",
                    abstract=abstract,
                    document_id=document_id,
                    classification=tier,
                    classification_reason=reason,
                    affected_controls=affected_controls,
                    substantive_content=substantive_content,
                )
            )

        unresolved_date_conflicts = [
            node_identity
            for node_identity, group in node_groups.items()
            if group.get("listing_date_conflicts")
        ]
        if unresolved_date_conflicts:
            return _incomplete_result(
                items,
                error=(
                    "FINRA listing/detail date conflict for "
                    f"{unresolved_date_conflicts[0]}"
                ),
                expected_count=len(rows),
                pages_fetched=listing["pages_fetched"],
                declared_pages=listing["declared_pages"],
                cutoff_page=listing["cutoff_page"],
                limited=limit is not None,
                fallback_urls=resolved_fallback_urls,
                coverage={
                    **listing.get("coverage", {}),
                    "duplicate_ledger": duplicate_ledger,
                    "conflict_ledger": conflict_ledger,
                },
            )

        coverage = {
            **listing.get("coverage", {}),
            "detail_count": len(items),
            "unique_node_count": len(node_groups),
            "fetched_entry_identities": sorted({
                item.document_id or item.url for item in items
            }),
            "alias_ledger": [],
            "duplicate_ledger": duplicate_ledger,
            "conflict_ledger": conflict_ledger,
        }
        coverage["fetched_entry_identity_digest"] = _identity_digest(
            coverage["fetched_entry_identities"]
        )
        coverage["alias_ledger_digest"] = _alias_ledger_digest(
            coverage["alias_ledger"]
        )
        if unproven_known_urls:
            return _incomplete_result(
                items,
                error=(
                    "FINRA known refresh target was absent from both complete "
                    f"listing proofs: {unproven_known_urls[0]}"
                ),
                expected_count=listing.get("coverage", {}).get(
                    "listing_record_count"
                ),
                pages_fetched=listing["pages_fetched"],
                declared_pages=listing["declared_pages"],
                cutoff_page=listing["cutoff_page"],
                fallback_urls=resolved_fallback_urls,
                coverage=coverage,
            )
        if limit is not None:
            return _incomplete_result(
                items,
                error="FINRA fetch was explicitly limited",
                expected_count=len(rows),
                pages_fetched=listing["pages_fetched"],
                declared_pages=listing["declared_pages"],
                cutoff_page=listing["cutoff_page"],
                limited=True,
                coverage=coverage,
            )
        return _complete_result(
            items,
            expected_count=len(rows),
            pages_fetched=listing["pages_fetched"],
            declared_pages=listing["declared_pages"],
            cutoff_page=listing["cutoff_page"],
            fallback_urls=resolved_fallback_urls,
            coverage=coverage,
        )
    except requests.RequestException as e:
        return _incomplete_result(items, error=f"FINRA notices scraping error: {e}")
    except (ValueError, TypeError) as e:
        return _incomplete_result(items, error=f"FINRA notices parsing error: {e}")


def _fetch_finra_notices_legacy(
    session: requests.Session,
    config: dict,
    limit: Optional[int] = None,
    since_date: Optional[str] = None,
    known_urls: Optional[list[str]] = None,
    fallback_urls: Optional[dict[str, str]] = None,
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
        fallback_urls: Persisted FINRA numeric node URLs learned from an
            authoritative notice page's shortlink. These are transport-only
            fallbacks for edge-cache 429 responses; the canonical notice URL
            remains the item identity and hashing base.

    Returns:
        FetchResult: List-compatible items plus a completeness verdict.
    """
    items = []
    resolved_fallback_urls = dict(fallback_urls or {})

    if limit is not None and limit < 0:
        return _incomplete_result(error=f"FINRA limit must be non-negative, got {limit}")

    try:
        logger.info(f"Fetching FINRA notices from {FINRA_NOTICES_URL}...")
        listing = _fetch_finra_listing_records(session, since_date)
        if not listing.get("complete"):
            return _incomplete_result(
                error=listing.get("error") or "FINRA listing was incomplete",
                expected_count=listing.get("expected_count"),
                pages_fetched=listing.get("pages_fetched", 0),
                declared_pages=listing.get("declared_pages"),
                cutoff_page=listing.get("cutoff_page"),
            )
        page_records = list(listing["records"])
        pages_fetched = listing["pages_fetched"]
        declared_pages = listing["declared_pages"]
        cutoff_page = listing["cutoff_page"]
        seen_urls = {record[0] for record in page_records}

        for known_url in sorted(set(known_urls or [])):
            if known_url not in seen_urls:
                page_records.append((known_url, '', ''))
                seen_urls.add(known_url)

        if limit is not None:
            page_records = page_records[:limit]
            logger.info(f"Limited to {limit} notices for testing; state will not advance")

        seen_document_ids = {}
        for url, listing_title, listing_date in page_records:
            fallback_url = _validate_finra_node_url(
                resolved_fallback_urls.get(url, "")
            )
            detail = _fetch_finra_page(
                url,
                session,
                max_attempts=1 if fallback_url and fallback_url != url else None,
            )
            if detail['status_code'] != 200 and fallback_url and fallback_url != url:
                logger.warning(
                    "FINRA canonical detail for %s was unavailable; "
                    "retrying authoritative node fallback %s",
                    url,
                    fallback_url,
                )
                detail = _fetch_finra_page(fallback_url, session)
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
                    fallback_urls=resolved_fallback_urls,
                )

            detail_soup = BeautifulSoup(detail['content'], 'html.parser')
            shortlink = _extract_finra_shortlink(detail_soup)
            if shortlink:
                resolved_fallback_urls[url] = shortlink
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
            fallback_urls=resolved_fallback_urls,
            coverage={
                **listing.get("coverage", {}),
                "detail_count": len(items),
            },
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

        comparison_key = entry_key
        if source_key == SOURCE_KEY_FINRA:
            comparison_key = _resolve_finra_identity(source_state, entry_key)

        # Check if this is a new item or changed item
        if comparison_key not in existing_entries:
            logger.info(f"  New item: {item.title[:60]}... ({item.agency})")
            new_items.append(item)
        elif existing_entries[comparison_key] != content_hash:
            logger.info(f"  Updated item: {item.title[:60]}... ({item.agency})")
            new_items.append(item)

    return new_items


def check_for_recovery_items(
    source_key: str,
    items: list[RegulatoryItem],
    trusted_source_state: dict,
) -> list[RegulatoryItem]:
    """Find findings after a trusted watermark without baselining them away."""
    trusted_entries = trusted_source_state.get("entries", {})
    if not isinstance(trusted_entries, dict):
        raise ValueError(f"{source_key} trusted entries are malformed")
    watermark = _state_date(trusted_source_state)
    if not watermark:
        raise ValueError(f"{source_key} trusted watermark is missing")

    findings = []
    for item in items:
        entry_key = item.document_id if item.document_id else item.url
        content_hash = _item_content_hash(item)
        publication_date = item.publication_date[:10] if (
            isinstance(item.publication_date, str)
            and re.match(r"^\d{4}-\d{2}-\d{2}", item.publication_date)
        ) else None
        if publication_date is None or publication_date > watermark:
            findings.append(item)
        elif (
            entry_key in trusted_entries
            and trusted_entries[entry_key] != content_hash
        ):
            findings.append(item)
    return findings


def update_source_state(
    source_key: str,
    items: list[RegulatoryItem],
    state: dict,
    *,
    refreshed_urls: Optional[list[str]] = None,
    fallback_urls: Optional[dict[str, str]] = None,
    coverage: Optional[dict] = None,
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
    fetched_entries = {}
    finra_fallback_urls = None

    if source_key == SOURCE_KEY_FINRA:
        persisted_fallbacks = source_state.get('fallback_urls', {})
        finra_fallback_urls = (
            dict(persisted_fallbacks)
            if isinstance(persisted_fallbacks, dict)
            else {}
        )
        if fallback_urls is not None:
            for canonical_url, node_url in fallback_urls.items():
                valid_node_url = _validate_finra_node_url(node_url)
                if valid_node_url:
                    finra_fallback_urls[canonical_url] = valid_node_url

    for item in items:
        entry_key = item.document_id if item.document_id else item.url
        fetched_entries[entry_key] = _item_content_hash(item)

    if (
        source_key == SOURCE_KEY_FINRA
        and isinstance(coverage, dict)
        and "fetched_entry_identities" in coverage
    ):
        fetched_identities = coverage.get("fetched_entry_identities")
        if (
            not isinstance(fetched_identities, list)
            or set(fetched_identities) != set(fetched_entries)
        ):
            raise ValueError(
                "FINRA coverage identities do not match fetched detail identities"
            )
        prior_coverage = source_state.get("coverage", {})
        existing_alias_ledger = (
            prior_coverage.get("alias_ledger", [])
            if isinstance(prior_coverage, dict)
            else []
        )
        # Blocker 4: a listing/detail fetch (e.g. via node-transport fallback)
        # can surface an identity that production already migrated to a
        # canonical node entry -- e.g. "FINRA 00-01" for the canonical
        # node/6547. Resolve every fetched identity through the trusted prior
        # alias ledger BEFORE rebuilding entries so it updates the existing
        # canonical entry in place instead of orphaning it (which would both
        # break the alias chain-head binding and strand the canonical node).
        alias_map = _finra_alias_map(existing_alias_ledger)
        resolved_fetched: dict[str, str] = {}
        for raw_key, content_hash in fetched_entries.items():
            canonical_key = _finra_resolve_identity_via_ledger(raw_key, alias_map)
            if (
                canonical_key in resolved_fetched
                and resolved_fetched[canonical_key] != content_hash
            ):
                raise ValueError(
                    "FINRA fetched identities collide on canonical identity "
                    f"{canonical_key} with conflicting content"
                )
            resolved_fetched[canonical_key] = content_hash
        fetched_entries = resolved_fetched
        coverage["fetched_entry_identities"] = sorted(fetched_entries)
        coverage["fetched_entry_identity_digest"] = _identity_digest(
            coverage["fetched_entry_identities"]
        )
        legacy_migration_ledger = coverage.get("migration_ledger")
        if legacy_migration_ledger is None and isinstance(prior_coverage, dict):
            legacy_migration_ledger = prior_coverage.get("migration_ledger")
        alias_ledger = _build_finra_alias_ledger(
            entries,
            fetched_entries,
            existing_alias_ledger=existing_alias_ledger,
            legacy_migration_ledger=legacy_migration_ledger,
            fallback_urls=finra_fallback_urls,
        )
        coverage["alias_ledger"] = alias_ledger
        coverage["alias_ledger_digest"] = _alias_ledger_digest(alias_ledger)
        coverage.pop("migration_ledger", None)
        entries = dict(fetched_entries)
    else:
        for entry_key, content_hash in fetched_entries.items():
            entries[entry_key] = content_hash

    source_state['entries'] = entries
    if (
        source_key == SOURCE_KEY_FINRA
        and fallback_urls is not None
        and finra_fallback_urls is not None
    ):
        source_state['fallback_urls'] = finra_fallback_urls
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
    if source_key == SOURCE_KEY_FEDERAL_REGISTER:
        source_state['last_checked'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    coverage_proof = dict(coverage or {})
    coverage_proof.update({
        "schema_version": 1,
        "source": source_key,
        "entry_count": len(entries),
        "entries_digest": _entries_digest(entries),
        "watermark": _coverage_watermark(source_state),
    })
    if source_key == SOURCE_KEY_FINRA:
        coverage_proof["entry_identity_digest"] = _identity_digest(entries)
        coverage_proof["alias_ledger_digest"] = _alias_ledger_digest(
            coverage_proof.get("alias_ledger", [])
        )
        coverage_proof.pop("migration_ledger", None)
    source_state["coverage"] = coverage_proof

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
    parser.add_argument(
        '--initialize-baseline',
        action='store_true',
        help=(
            "Explicitly initialize missing regulatory source state; requires "
            "REGULATORY_MONITOR_BASELINE_APPROVED=I_UNDERSTAND and cannot run in CI"
        ),
    )
    parser.add_argument(
        '--recovery-from-state',
        type=str,
        default=None,
        help=(
            "Explicitly compare findings against a trusted pre-incident state "
            "file; requires REGULATORY_MONITOR_BASELINE_APPROVED=I_UNDERSTAND "
            "and cannot run in CI"
        ),
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

    recovery_mode = args.recovery_from_state is not None
    if (
        (args.initialize_baseline or recovery_mode)
        and not _baseline_approval_is_manual()
    ):
        logger.error(
            "Baseline/recovery mode requires local manual approval via "
            "REGULATORY_MONITOR_BASELINE_APPROVED=I_UNDERSTAND"
        )
        sys.exit(2)

    logger.info("=== Regulatory Monitor ===")
    logger.info(f"Source: {args.source}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Config: {config_path}")
    if args.limit is not None:
        logger.info(f"Limit: {args.limit} items per source")

    source_keys = []
    if args.source in ['federal-register', 'all']:
        source_keys.append(SOURCE_KEY_FEDERAL_REGISTER)
    if args.source in ['finra', 'all']:
        source_keys.append(SOURCE_KEY_FINRA)

    # Normal scheduled runs must prove a valid prior regulatory state before
    # any source fetch or write. Read-only dry validation may operate without
    # state because it performs no fetch or write. Only the explicitly approved
    # local baseline mode may recover missing source sections.
    strict_state = (
        not args.initialize_baseline
        and not recovery_mode
        and not args.dry_run
    )
    try:
        state = load_state(
            STATE_FILE,
            allow_empty=args.initialize_baseline or args.dry_run,
            migrate=args.initialize_baseline,
        )
    except StateLoadError as exc:
        logger.error("Regulatory monitor state is unavailable: %s", exc)
        sys.exit(2)

    trusted_state = None
    if recovery_mode:
        trusted_path = Path(args.recovery_from_state).resolve()
        if trusted_path == STATE_FILE.resolve():
            logger.error("Recovery reference must be distinct from live state")
            sys.exit(2)
        try:
            trusted_state = load_state(
                trusted_path,
                allow_empty=False,
                migrate=False,
            )
        except StateLoadError as exc:
            logger.error("Trusted recovery state is unavailable: %s", exc)
            sys.exit(2)
        for source_key in source_keys:
            trusted_source = get_source_state(trusted_state, source_key)
            if (
                not isinstance(trusted_source.get("entries"), dict)
                or not _state_date(trusted_source)
            ):
                logger.error(
                    "Trusted recovery state is missing %s entries or watermark",
                    source_key,
                )
                sys.exit(2)

    if strict_state or recovery_mode:
        state_errors = _validate_regulatory_state(
            state,
            source_keys,
            allow_legacy_finra_identity_proof=recovery_mode,
        )
        if state_errors:
            for error in state_errors:
                logger.error("Regulatory monitor state invalid: %s", error)
            sys.exit(2)
    elif args.initialize_baseline:
        for source_key in source_keys:
            if _validate_regulatory_state(state, [source_key]):
                set_source_state(state, source_key, {})

    # Ensure directories exist only after state validation has succeeded.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

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
    finra_fallback_urls = {}

    # Fetch from Federal Register
    if args.source in ['federal-register', 'all']:
        logger.info("\n--- Federal Register ---")
        fed_state = get_source_state(state, SOURCE_KEY_FEDERAL_REGISTER)
        comparison_fed_state = (
            get_source_state(trusted_state, SOURCE_KEY_FEDERAL_REGISTER)
            if recovery_mode
            else fed_state
        )

        # First-run baseline suppression: when there is no prior persisted state
        # for this source, record the current items as the baseline silently
        # rather than flagging every fetched item as "new". Without this guard a
        # first run would emit ~30 days of items as a single noisy report.
        fed_is_baseline = (
            args.initialize_baseline
            and bool(_validate_regulatory_state(state, [SOURCE_KEY_FEDERAL_REGISTER]))
        )

        # Determine since_date (last check or 30 days ago)
        since_date = comparison_fed_state.get('last_checked')
        if not since_date:
            since_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%d')
            logger.info("No prior state, fetching documents from last 30 days")
        else:
            logger.info(
                "Fetching Federal Register documents from the validated watermark"
            )

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
        comparison_finra_state = (
            get_source_state(trusted_state, SOURCE_KEY_FINRA)
            if recovery_mode
            else finra_state
        )

        # First-run baseline suppression (mirrors Federal Register / learn_monitor).
        finra_is_baseline = (
            args.initialize_baseline
            and bool(_validate_regulatory_state(state, [SOURCE_KEY_FINRA]))
        )
        finra_refresh_urls = _finra_refresh_batch(finra_state)
        persisted_fallback_urls = finra_state.get('fallback_urls', {})
        if isinstance(persisted_fallback_urls, dict):
            finra_fallback_urls = {
                canonical_url: node_url
                for canonical_url, node_url in persisted_fallback_urls.items()
                if isinstance(canonical_url, str)
                and _validate_finra_node_url(node_url)
            }

        finra_result = _coerce_fetch_result(
            fetch_finra_notices(
                session,
                config,
                limit=args.limit,
                since_date=_state_date(comparison_finra_state),
                known_urls=finra_refresh_urls,
                fallback_urls=finra_fallback_urls,
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
            if recovery_mode:
                trusted_source = get_source_state(trusted_state, source_key)
                new_items = check_for_recovery_items(
                    source_key,
                    items,
                    trusted_source,
                )
                logger.info(
                    f"{source_key}: {len(new_items)} recovered findings "
                    "after trusted watermark"
                )
                all_new_items.extend(new_items)
            elif is_baseline:
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
                fallback_urls=(
                    result.fallback_urls
                    if source_key == SOURCE_KEY_FINRA
                    else None
                ),
                coverage=result.coverage,
            )
        updated_state_errors = _validate_regulatory_state(state, source_keys)
        if updated_state_errors:
            for error in updated_state_errors:
                logger.error("Updated regulatory monitor state invalid: %s", error)
            sys.exit(2)
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
