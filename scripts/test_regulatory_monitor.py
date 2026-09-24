"""Regression tests for scripts/regulatory_monitor.py.

The critical guard here is test_save_state_atomic_arg_order: regulatory_monitor
must call save_state_atomic(state, STATE_FILE) — dict first, path second — to
match the signature in monitoring_shared.save_state_atomic(state, state_path).
A prior bug swapped these arguments, raising TypeError that was swallowed by the
workflow's continue-on-error, so the monitor never persisted state.

This test exercises the REAL save path (NOT --dry-run, which short-circuits
before any save) by stubbing out the network fetches and capturing the args
passed to save_state_atomic.
"""
from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import pytest
from bs4 import BeautifulSoup

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import monitoring_shared  # noqa: E402
import regulatory_monitor  # noqa: E402
from monitoring_shared import compute_hash  # noqa: E402

# Anti-truncation floors for the shipped recovery state. These sit just under
# the recovered 2026-08-09 baseline so legitimate archive growth never freezes
# the suite, while any regression toward the 332/2-entry incident state fails.
MIN_FEDERAL_REGISTER_ENTRIES = 500
MIN_FINRA_ENTRIES = 3600
MIN_FINRA_ALIASES = 600
MIN_FINRA_LISTING_PAGES = 90
MIN_FINRA_RAW_LISTING_ROWS = 3650
RECOVERY_WATERMARK_DATE = "2026-08-09"


def _make_item(title, doc_id, *, abstract="", pub_date="2026-01-01",
               source="Federal Register", agency="SEC", url=None):
    """Construct a RegulatoryItem for tests."""
    return regulatory_monitor.RegulatoryItem(
        source=source,
        agency=agency,
        title=title,
        url=url or f"https://example.test/{doc_id}",
        publication_date=pub_date,
        document_id=doc_id,
        abstract=abstract,
    )


def _item_hash(item):
    """Mirror the hash computed inside check_for_new_items/update_source_state."""
    return compute_hash(f"{item.title}|{item.abstract}|{item.publication_date}")


def _alias(old_identity, canonical_identity, source_hash):
    return {
        "old_identity": old_identity,
        "canonical_identity": canonical_identity,
        "source_hash": source_hash,
        "evidence": {
            "source_hash_at_migration": source_hash,
            "canonical_hash_at_migration": source_hash,
            "reason": "legacy duplicate migrated to canonical node identity",
        },
    }


def _detail_identity_proof(notice_number, node_url):
    node_id = node_url.rsplit("/", 1)[-1]
    notice_url = (
        f"https://www.finra.org/rules-guidance/notices/{notice_number}"
    )
    return "\n".join((
        f'<link href="{notice_url}" rel="canonical"/>',
        f'<link href="{node_url}" rel="shortlink"/>',
        f'<body class="layout-two-sidebars page-node-{node_id}"></body>',
        (
            '<span class="field field--name-title" id="node-title">'
            f'<span>Notice to Members {notice_number}</span></span>'
        ),
    ))


def _page_row_digest(payloads):
    """Mirror the production page-row digest over raw listing payloads."""
    return compute_hash(json.dumps(
        payloads,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ))


def _synthetic_href_for_identity(identity, index):
    """Return a resolvable FINRA detail href that maps back to *identity*.

    Mirrors production: a listing row resolves through
    ``_finra_normalize_detail_link`` -> ``_extract_finra_document_id`` to the
    canonical entry identity. FINRA notice numbers map to their canonical
    notices URL; full node/notices URLs are used in their normalized form.
    """
    text = str(identity)
    match = re.fullmatch(r"FINRA (\d{2}-\d{2})", text)
    if match:
        return f"https://www.finra.org/rules-guidance/notices/{match.group(1)}"
    normalized, _ = regulatory_monitor._finra_normalize_detail_link(text)
    if normalized is not None:
        return normalized
    return f"https://www.finra.org/node/{900000 + index}"


def _synthetic_row_payload(identity, index):
    """Build one resolvable raw listing-row payload for a synthetic identity."""
    return {
        "text": str(identity),
        "links": [
            {
                "href": _synthetic_href_for_identity(identity, index),
                "text": str(identity),
            }
        ],
    }


def _synthetic_pass_proofs(identities):
    """Build two pass proofs whose every derived value recomputes from payloads."""
    payloads = [
        _synthetic_row_payload(identity, index)
        for index, identity in enumerate(identities)
    ]
    proof = {
        "token": "test-pass-1",
        "declared_pages": 1,
        "pages_fetched": 1,
        "page_numbers": [0],
        "page_identities": [{"requested": 0, "final": 0, "active": 0}],
        "page_row_counts": [len(payloads)],
        "page_row_digests": [_page_row_digest(payloads)],
        "page_row_payloads": [payloads],
        "raw_row_count": len(payloads),
        "resolved_row_count": len(payloads),
        "unresolved_row_count": 0,
        "unique_node_count": len(payloads),
    }
    return [proof, dict(deepcopy(proof), token="test-pass-2")]


def test_finra_alias_migration_removes_duplicate_entries_and_requires_evidence():
    """Legacy aliases are ledger-only and cannot be inferred from a partial refresh."""
    source_hash = "sha256:legacy"
    old_identity = "FINRA 26-01"
    canonical_identity = "https://www.finra.org/node/382801"
    notice_url = "https://www.finra.org/rules-guidance/notices/26-01"
    detail_proofs = [_detail_identity_proof("26-01", canonical_identity)]
    binding_digest = regulatory_monitor._finra_detail_identity_binding_digest(
        {notice_url: canonical_identity}
    )
    migrated = regulatory_monitor._build_finra_alias_ledger(
        {old_identity: source_hash},
        {canonical_identity: source_hash},
        legacy_migration_ledger=[
            {"identity": old_identity, "reason": "verified duplicate"},
        ],
        detail_identity_proofs=detail_proofs,
        retained_detail_urls={notice_url},
        immutable_binding_digest=binding_digest,
    )
    assert migrated[0]["old_identity"] == old_identity
    assert migrated[0]["canonical_identity"] == canonical_identity
    assert migrated[0]["source_hash"] == source_hash
    assert migrated[0]["evidence"]["reason"] == "verified duplicate"
    with pytest.raises(
        ValueError,
        match="lack explicit migration evidence",
    ):
        regulatory_monitor._build_finra_alias_ledger(
            {old_identity: source_hash},
            {canonical_identity: source_hash},
            detail_identity_proofs=detail_proofs,
            retained_detail_urls={notice_url},
            immutable_binding_digest=binding_digest,
        )


def test_finra_alias_survives_canonical_content_update_with_recorded_transition():
    """A later canonical update must be recorded, not silently absorbed."""
    old_hash = "sha256:old"
    new_hash = "sha256:new"
    old_identity = "FINRA 26-01"
    canonical_identity = "https://www.finra.org/node/382801"
    notice_url = "https://www.finra.org/rules-guidance/notices/26-01"
    detail_proofs = [_detail_identity_proof("26-01", canonical_identity)]
    binding_digest = regulatory_monitor._finra_detail_identity_binding_digest(
        {notice_url: canonical_identity}
    )
    ledger = [_alias(old_identity, canonical_identity, old_hash)]
    unchanged_entries = {canonical_identity: old_hash}
    updated_entries = {canonical_identity: new_hash}

    assert regulatory_monitor._validate_finra_alias_ledger(
        ledger,
        unchanged_entries,
        [canonical_identity],
        detail_identity_proofs=detail_proofs,
        retained_detail_urls={notice_url},
        immutable_binding_digest=binding_digest,
    ) == []

    # An unrecorded canonical content change breaks the alias binding.
    stale_errors = regulatory_monitor._validate_finra_alias_ledger(
        ledger,
        updated_entries,
        [canonical_identity],
        detail_identity_proofs=detail_proofs,
        retained_detail_urls={notice_url},
        immutable_binding_digest=binding_digest,
    )
    assert any(
        "not bound to its canonical entry hash" in error for error in stale_errors
    )

    source_state = {"coverage": {"alias_ledger": ledger}}
    assert regulatory_monitor._resolve_finra_identity(
        source_state, old_identity
    ) == canonical_identity

    rebuilt = regulatory_monitor._build_finra_alias_ledger(
        updated_entries,
        updated_entries,
        existing_alias_ledger=ledger,
        detail_identity_proofs=detail_proofs,
        retained_detail_urls={notice_url},
        immutable_binding_digest=binding_digest,
    )
    assert rebuilt[0]["source_hash"] == old_hash
    assert rebuilt[0]["evidence"]["content_updates"] == [
        {"from": old_hash, "to": new_hash},
    ]
    assert regulatory_monitor._validate_finra_alias_ledger(
        rebuilt,
        updated_entries,
        [canonical_identity],
        detail_identity_proofs=detail_proofs,
        retained_detail_urls={notice_url},
        immutable_binding_digest=binding_digest,
    ) == []
    assert old_identity not in updated_entries
    # The recorded transition is append-only and stable across reruns.
    assert regulatory_monitor._build_finra_alias_ledger(
        updated_entries,
        updated_entries,
        existing_alias_ledger=rebuilt,
        detail_identity_proofs=detail_proofs,
        retained_detail_urls={notice_url},
        immutable_binding_digest=binding_digest,
    ) == rebuilt


def test_finra_alias_cannot_be_redirected_to_an_unrelated_notice():
    """Recomputing the ledger digest cannot launder a forged alias target."""
    entries = {
        "FINRA 26-15": "sha256:unrelated",
        "https://www.finra.org/node/6547": "sha256:canonical",
    }
    forged_notice_redirect = [{
        # Every self-referential evidence field is recomputed to agree with the
        # forged target, and the ledger digest would recompute cleanly too.
        "old_identity": "FINRA 00-01",
        "canonical_identity": "FINRA 26-15",
        "source_hash": "sha256:unrelated",
        "evidence": {
            "source_hash_at_migration": "sha256:unrelated",
            "canonical_hash_at_migration": "sha256:unrelated",
            "reason": "legacy duplicate migrated to canonical node identity",
        },
    }]
    notice_errors = regulatory_monitor._validate_finra_alias_ledger(
        forged_notice_redirect,
        entries,
        sorted(entries),
    )
    assert any(
        "migrates between different notices" in error for error in notice_errors
    )

    forged_node_redirect = [
        _alias("FINRA 00-01", "https://www.finra.org/node/6547", "sha256:legacy")
    ]
    node_errors = regulatory_monitor._validate_finra_alias_ledger(
        forged_node_redirect,
        entries,
        sorted(entries),
    )
    assert any(
        "not bound to its canonical entry hash" in error for error in node_errors
    )

    forged_chain = deepcopy(forged_node_redirect)
    forged_chain[0]["evidence"]["content_updates"] = [
        {"from": "sha256:unrelated", "to": "sha256:canonical"},
    ]
    chain_errors = regulatory_monitor._validate_finra_alias_ledger(
        forged_chain,
        entries,
        sorted(entries),
    )
    assert any("not contiguous" in error for error in chain_errors)


def test_finra_pass_proofs_must_recompute_from_retained_payloads():
    """Replaced pass payloads cannot hide behind retained digests and counts."""
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    assert regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    ) == []

    forged = deepcopy(source_state)
    for proof in forged["coverage"]["pass_proofs"]:
        # Keep every duplicated count/digest evidence field byte-identical and
        # swap only the underlying payload the proof claims to summarize.
        proof["page_row_payloads"][0] = [
            {"text": "forged", "links": []}
            for _ in proof["page_row_payloads"][0]
        ]
    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
    )
    assert any("not recomputable from payloads" in error for error in errors)

    dropped = deepcopy(source_state)
    for proof in dropped["coverage"]["pass_proofs"]:
        proof.pop("page_row_payloads")
    dropped_errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        dropped,
    )
    assert any(
        "page row payloads are missing or invalid" in error
        for error in dropped_errors
    )

    emptied = deepcopy(source_state)
    emptied["coverage"]["duplicate_ledger"] = []
    duplicate_errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        emptied,
    )
    assert any(
        "duplicate ledger does not account for coalesced rows" in error
        for error in duplicate_errors
    )


def _load_shipped_state():
    """Return a deep copy of the shipped, checked-in unified state."""
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    return json.loads(state_path.read_text(encoding="utf-8"))


def _load_shipped_finra_source_state():
    """Return a deep copy of the shipped, checked-in FINRA source state."""
    state = _load_shipped_state()
    return deepcopy(state["sources"][regulatory_monitor.SOURCE_KEY_FINRA])


def test_finra_alias_redirect_with_recomputed_evidence_rejected_by_node_binding():
    """A self-consistent alias repoint still fails its independent node binding."""
    source_state = _load_shipped_finra_source_state()
    assert regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA, source_state
    ) == []

    coverage = source_state["coverage"]
    entries = source_state["entries"]
    alias_ledger = coverage["alias_ledger"]
    alias_canonicals = {alias["canonical_identity"] for alias in alias_ledger}
    victim_original_canonical = alias_ledger[0]["canonical_identity"]

    # An unrelated node entry that is NOT any alias's canonical target (one of
    # the raw-listing node docids), so repointing to it keeps the ledger's
    # one-to-one target constraint intact.
    unrelated_node = next(
        identity
        for identity in entries
        if identity.startswith("https://www.finra.org/node/")
        and identity not in alias_canonicals
        and identity != victim_original_canonical
    )

    forged = deepcopy(source_state)
    forged_alias = forged["coverage"]["alias_ledger"][0]
    forged_alias["canonical_identity"] = unrelated_node
    forged_alias["source_hash"] = entries[unrelated_node]
    forged_alias["evidence"] = {
        "source_hash_at_migration": entries[unrelated_node],
        "canonical_hash_at_migration": entries[unrelated_node],
        "reason": forged_alias["evidence"]["reason"],
    }
    # Recompute the ledger digest so the digest guard cannot catch the forgery.
    forged["coverage"]["alias_ledger_digest"] = regulatory_monitor._alias_ledger_digest(
        forged["coverage"]["alias_ledger"]
    )

    alias_errors = regulatory_monitor._validate_finra_alias_ledger(
        forged["coverage"]["alias_ledger"],
        forged["entries"],
        forged["coverage"]["fetched_entry_identities"],
        detail_identity_proofs=forged["coverage"]["detail_identity_proofs"],
        retained_detail_urls=(
            regulatory_monitor._finra_retained_listing_detail_urls(
                forged["coverage"]["pass_proofs"]
            )
        ),
        immutable_binding_digest=(
            regulatory_monitor.FINRA_DETAIL_IDENTITY_ANCHORS[
                forged["coverage"]["detail_identity_anchor"]
            ]
        ),
    )
    assert any(
        "immutable detail-page binding" in error for error in alias_errors
    )

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA, forged
    )
    assert any(
        "immutable detail-page binding" in error for error in errors
    )
    assert any(
        "do not reconstruct the fetched entry identities" in error
        for error in errors
    )


def test_finra_swapped_aliases_and_mutable_evidence_fail_immutable_anchor():
    """Mutable alias evidence cannot rewrite the code-held recovery root."""
    source_state = _load_shipped_finra_source_state()
    forged = deepcopy(source_state)
    first, second = forged["coverage"]["alias_ledger"][:2]
    first_source = regulatory_monitor._finra_alias_source_url(
        first["old_identity"]
    )
    second_source = regulatory_monitor._finra_alias_source_url(
        second["old_identity"]
    )
    first_target = first["canonical_identity"]
    second_target = second["canonical_identity"]
    first["canonical_identity"] = second_target
    second["canonical_identity"] = first_target

    for alias in (first, second):
        target_hash = forged["entries"][alias["canonical_identity"]]
        alias["source_hash"] = target_hash
        alias["evidence"] = {
            "source_hash_at_migration": target_hash,
            "canonical_hash_at_migration": target_hash,
            "reason": "forged alias swap with rebound self-attestation",
        }
    forged["fallback_urls"][first_source] = second_target
    forged["fallback_urls"][second_source] = first_target

    # Rebind every mutable node mapping inside each retained envelope too.
    # The forged envelopes remain internally self-consistent, so only the
    # immutable code-held recovery anchor can reject the swapped mapping.
    rebound_proofs = []
    for proof in forged["coverage"]["detail_identity_proofs"]:
        soup = BeautifulSoup(proof, "html.parser")
        canonical = soup.select_one('link[rel="canonical"][href]')
        shortlink = soup.select_one('link[rel="shortlink"][href]')
        body = soup.body
        canonical_url = canonical.get("href") if canonical else None
        if canonical_url == first_source:
            shortlink["href"] = second_target
            replacement_node = second_target.rsplit("/", 1)[-1]
        elif canonical_url == second_source:
            shortlink["href"] = first_target
            replacement_node = first_target.rsplit("/", 1)[-1]
        else:
            replacement_node = None
        if replacement_node is not None:
            body["class"] = [
                (
                    f"page-node-{replacement_node}"
                    if str(css_class).startswith("page-node-")
                    else css_class
                )
                for css_class in body.get("class", [])
            ]
        rebound_proofs.append(str(soup))
    forged["coverage"]["detail_identity_proofs"] = rebound_proofs
    forged["coverage"]["detail_identity_proof_digest"] = (
        regulatory_monitor._finra_detail_identity_proof_digest(
            rebound_proofs
        )
    )
    forged["coverage"]["alias_ledger_digest"] = (
        regulatory_monitor._alias_ledger_digest(
            forged["coverage"]["alias_ledger"]
        )
    )

    alias_errors = regulatory_monitor._validate_finra_alias_ledger(
        forged["coverage"]["alias_ledger"],
        forged["entries"],
        forged["coverage"]["fetched_entry_identities"],
        detail_identity_proofs=forged["coverage"]["detail_identity_proofs"],
        retained_detail_urls=(
            regulatory_monitor._finra_retained_listing_detail_urls(
                forged["coverage"]["pass_proofs"]
            )
        ),
        immutable_binding_digest=(
            regulatory_monitor.FINRA_DETAIL_IDENTITY_ANCHORS[
                forged["coverage"]["detail_identity_anchor"]
            ]
        ),
    )
    assert any(
        "immutable recovery anchor" in error
        for error in alias_errors
    )
    assert not any(
        "retained detail-page evidence is malformed" in error
        for error in alias_errors
    )
    assert not any(
        "alias target does not match" in error for error in alias_errors
    )

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
    )
    assert any(
        "immutable recovery anchor" in error
        for error in errors
    )
    assert not any(
        "do not reconstruct the fetched entry identities" in error
        for error in errors
    )
    assert not any(
        "detail identity proof digest is invalid" in error
        or "alias ledger digest is invalid" in error
        for error in errors
    )


def _first_uniquely_resolved_row(proof):
    """Locate a listing row whose node identity is unique across the proof."""
    from collections import Counter

    counts: Counter = Counter()
    positions: dict = {}
    for page_index, page in enumerate(proof["page_row_payloads"]):
        for row_index, row in enumerate(page):
            targets = set()
            for link in row.get("links") or []:
                href = link.get("href")
                if isinstance(href, str):
                    detail_url, node_identity = (
                        regulatory_monitor._finra_normalize_detail_link(href)
                    )
                    if detail_url:
                        targets.add(node_identity)
            if len(targets) == 1:
                node_identity = next(iter(targets))
                counts[node_identity] += 1
                positions.setdefault(node_identity, (page_index, row_index))
    for node_identity, count in counts.items():
        if count == 1:
            return positions[node_identity]
    raise AssertionError("no uniquely resolved listing row found")


def test_finra_forged_pass_row_target_outside_fetched_is_rejected():
    """A retained row that recomputes cleanly but points elsewhere is rejected.

    Blocker 6: pass proofs are self-supplied. Repointing a single retained row
    to a node that is not a fetched entry keeps every recomputable count and
    digest internally consistent (same raw/resolved/unique counts, freshly
    recomputed page digest), yet the row now resolves outside the fetched
    entries. Only the entry binding -- not the self-recomputation proof --
    catches it, in BOTH passes.
    """
    source_state = _load_shipped_finra_source_state()
    assert regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA, source_state
    ) == []

    forged = deepcopy(source_state)
    forged_href = "https://www.finra.org/node/99999999"
    for proof in forged["coverage"]["pass_proofs"]:
        page_index, row_index = _first_uniquely_resolved_row(proof)
        row = proof["page_row_payloads"][page_index][row_index]
        row["links"] = [{"href": forged_href, "text": "forged"}]
        # Recompute the page digest so the self-recomputation proof still passes.
        proof["page_row_digests"][page_index] = _page_row_digest(
            proof["page_row_payloads"][page_index]
        )

    # The self-recomputation proof is satisfied (counts/digests all recompute).
    for index, proof in enumerate(forged["coverage"]["pass_proofs"]):
        assert regulatory_monitor._finra_pass_proof_recomputation_errors(
            regulatory_monitor.SOURCE_KEY_FINRA, proof, index
        ) == []

    # The entry binding still rejects the forged target in both passes.
    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA, forged
    )
    assert [
        error for error in errors
        if "resolve to identities outside the fetched entries" in error
    ], errors


def test_finra_duplicate_ledger_rejects_empty_and_forged_records():
    """Duplicate records must carry real, resolvable coalesced-row evidence.

    Blocker 6: replacing every duplicate record with an empty dict preserves the
    ledger length (so the count floor still passes) but strips the evidence, and
    a forged payload whose digest is recomputed cannot point at a node outside
    the fetched entries.
    """
    source_state = _load_shipped_finra_source_state()
    assert regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA, source_state
    ) == []

    emptied = deepcopy(source_state)
    record_count = len(emptied["coverage"]["duplicate_ledger"])
    emptied["coverage"]["duplicate_ledger"] = [{} for _ in range(record_count)]
    empty_errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA, emptied
    )
    assert any(
        "is missing required duplicate evidence" in error
        for error in empty_errors
    )

    forged = deepcopy(source_state)
    record = forged["coverage"]["duplicate_ledger"][0]
    record["raw_payload"] = {
        "text": "forged duplicate",
        "links": [{"href": "https://www.finra.org/node/99999999", "text": "x"}],
    }
    record["raw_row_digest"] = compute_hash(json.dumps(
        record["raw_payload"],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ))
    forged_errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA, forged
    )
    assert any(
        "does not coalesce into a fetched entry" in error
        for error in forged_errors
    )


@pytest.mark.parametrize(
    "tamper",
    (
        "fabricated-payload",
        "target",
        "node-identity",
        "detail-hash",
        "missing-record",
        "extra-record",
        "duplicate-occurrence",
        "date-conflict",
        "date-resolver",
    ),
)
def test_finra_duplicate_ledger_exactly_matches_both_retained_passes(tamper):
    """Every duplicate record must be the exact occurrence proven by both passes."""
    source_state = _load_shipped_finra_source_state()
    forged = deepcopy(source_state)
    ledger = forged["coverage"]["duplicate_ledger"]

    if tamper == "fabricated-payload":
        ledger[0]["raw_payload"]["text"] += " fabricated"
        ledger[0]["raw_row_digest"] = _page_row_digest(
            ledger[0]["raw_payload"]
        )
    elif tamper == "target":
        ledger[0]["raw_payload"] = deepcopy(ledger[1]["raw_payload"])
        ledger[0]["raw_row_digest"] = _page_row_digest(
            ledger[0]["raw_payload"]
        )
    elif tamper == "node-identity":
        ledger[0]["node_identity"] = "node:99999999"
    elif tamper == "detail-hash":
        ledger[0]["detail_hash"] = "sha256:" + ("0" * 64)
    elif tamper == "missing-record":
        ledger.pop()
    elif tamper == "extra-record":
        ledger.append(deepcopy(ledger[0]))
    elif tamper == "duplicate-occurrence":
        ledger[0]["row_index"] += 1
    elif tamper == "date-conflict":
        ledger[0]["listing_date_conflict"] = not (
            ledger[0]["listing_date_conflict"]
        )
    elif tamper == "date-resolver":
        resolver = next(
            record
            for record in ledger
            if record["resolves_listing_date_conflict"]
        )
        resolver["resolves_listing_date_conflict"] = False
    else:  # pragma: no cover - parametrization is closed above
        raise AssertionError(f"unknown tamper case: {tamper}")

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
    )

    assert any(
        "duplicate ledger does not exactly match duplicates proven by both passes"
        in error
        for error in errors
    ), errors


@pytest.mark.parametrize(
    "tamper",
    (
        "missing-record",
        "missing-resolver",
        "mutated-resolver",
        "fabricated-resolver",
        "mutated-detail-date",
    ),
)
def test_finra_date_resolution_evidence_is_proof_bound(tamper):
    """Persisted duplicate-date resolution must replay from rows and detail hash."""
    source_state = _load_shipped_finra_source_state()
    forged = deepcopy(source_state)
    ledger = forged["coverage"]["date_resolution_ledger"]
    record_index = next(
        index
        for index, record in enumerate(ledger)
        if record["node_identity"] == "node:126166"
    )
    record = ledger[record_index]

    if tamper == "missing-record":
        ledger.pop(record_index)
    elif tamper == "missing-resolver":
        record.pop("resolver")
    elif tamper == "mutated-resolver":
        record["resolver"]["row_index"] += 1
    elif tamper == "fabricated-resolver":
        record["resolver"] = deepcopy(record["conflicts"][0])
    elif tamper == "mutated-detail-date":
        old_date = record["publication_date"]
        new_date = record["conflicts"][0]["listing_date"]
        record["detail_content"] = record["detail_content"].replace(
            f"Published Date: {old_date}",
            f"Published Date: {new_date}",
            1,
        )
    else:  # pragma: no cover - parametrization is closed above
        raise AssertionError(f"unknown tamper case: {tamper}")

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
    )

    assert any("date resolution" in error for error in errors), errors


def _retained_finra_rows_for_node(source_state, proof, node_identity):
    """Yield page positions whose canonical/fallback target reaches one node."""
    fallbacks = source_state.get("fallback_urls", {})
    for page_index, rows in enumerate(proof["page_row_payloads"]):
        page_number = proof["page_numbers"][page_index]
        for row_index, row in enumerate(rows):
            target = regulatory_monitor._finra_row_detail_target(row)
            if target is None:
                continue
            _, target_node = regulatory_monitor._finra_normalize_detail_link(
                target
            )
            fallback = fallbacks.get(target, "")
            _, fallback_node = regulatory_monitor._finra_normalize_detail_link(
                fallback
            )
            if node_identity in {target_node, fallback_node}:
                yield page_index, page_number, row_index, row


def _rewrite_finra_row_date(row, replacement):
    date_prefix = re.compile(
        r"^(?:(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|"
        r"Sunday),?\s+)?"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
        re.IGNORECASE,
    )
    rewritten, count = date_prefix.subn(replacement, row["text"], count=1)
    assert count == 1
    row["text"] = rewritten


def _coherently_rewrite_finra_duplicate_authority(
    state,
    *,
    node_identity,
    replacement_display_date,
    replacement_date,
):
    """Rewrite every mutable field that previously self-attested one date."""
    source_state = state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    coverage = source_state["coverage"]
    resolution = next(
        record
        for record in coverage["date_resolution_ledger"]
        if record["node_identity"] == node_identity
    )
    old_date = resolution["publication_date"]

    for proof in coverage["pass_proofs"]:
        affected_pages = set()
        rows = list(_retained_finra_rows_for_node(
            source_state, proof, node_identity
        ))
        assert len(rows) == 2
        for page_index, _page, _row_index, row in rows:
            _rewrite_finra_row_date(row, replacement_display_date)
            affected_pages.add(page_index)
        for page_index in affected_pages:
            proof["page_row_digests"][page_index] = _page_row_digest(
                proof["page_row_payloads"][page_index]
            )

    detail_proof = BeautifulSoup(
        resolution["detail_date_proof"], "html.parser"
    )
    time_node = detail_proof.select_one(
        ".field--name-field-core-official-dt time[datetime]"
    )
    assert time_node is not None
    old_datetime = time_node["datetime"]
    time_node["datetime"] = replacement_date + old_datetime[10:]
    time_node.string = replacement_display_date.split(", ", 1)[-1]
    resolution["detail_date_proof"] = str(detail_proof)
    resolution["detail_date_proof_hash"] = compute_hash(
        resolution["detail_date_proof"]
    )
    resolution["detail_content"] = resolution["detail_content"].replace(
        f"Published Date: {old_date}",
        f"Published Date: {replacement_date}",
        1,
    )
    replacement_hash = compute_hash(resolution["detail_content"])
    resolution["detail_hash"] = replacement_hash
    resolution["publication_date"] = replacement_date

    proof_facts = regulatory_monitor._finra_duplicate_date_proof_facts(
        resolution["detail_date_proof"]
    )
    assert proof_facts is not None
    assert proof_facts[2] == replacement_date
    entry_identity = regulatory_monitor._finra_resolve_identity_via_ledger(
        regulatory_monitor._extract_finra_document_id(proof_facts[0]),
        regulatory_monitor._finra_alias_map(coverage["alias_ledger"]),
    )
    source_state["entries"][entry_identity] = replacement_hash

    retained_occurrences = []
    first_proof = coverage["pass_proofs"][0]
    retained_rows = list(_retained_finra_rows_for_node(
        source_state, first_proof, node_identity
    ))
    for _page_index, page, row_index, row in retained_rows:
        target = regulatory_monitor._finra_row_detail_target(row)
        retained_occurrences.append(
            regulatory_monitor._finra_date_occurrence(
                page=page,
                row_index=row_index,
                target=target,
                raw_row_digest=_page_row_digest(row),
                listing_date=(
                    regulatory_monitor._finra_listing_date_from_payload(row)
                ),
            )
        )
    assert all(
        occurrence["listing_date"] == replacement_date
        for occurrence in retained_occurrences
    )
    resolution["resolver"] = retained_occurrences[0]
    resolution["conflicts"] = []

    duplicate = next(
        record
        for record in coverage["duplicate_ledger"]
        if record["node_identity"] == node_identity
    )
    duplicate_row = next(
        row
        for _page_index, page, row_index, row in retained_rows
        if (
            page == duplicate["page"]
            and row_index == duplicate["row_index"]
        )
    )
    duplicate["raw_payload"] = deepcopy(duplicate_row)
    duplicate["raw_row_digest"] = _page_row_digest(duplicate_row)
    duplicate["detail_hash"] = replacement_hash
    duplicate["raw_row_conflicts_with_first"] = (
        retained_occurrences[0]["raw_row_digest"]
        != duplicate["raw_row_digest"]
    )
    duplicate["listing_date_conflict"] = False
    duplicate["resolves_listing_date_conflict"] = False
    coverage["entries_digest"] = regulatory_monitor._entries_digest(
        source_state["entries"]
    )
    return resolution


def test_finra_full_coherent_duplicate_forgery_is_rejected_by_reviewed_anchor(
    monkeypatch,
):
    """Every mutable proof may agree and still cannot rewrite reviewed facts."""
    forged_state = _load_shipped_state()
    _coherently_rewrite_finra_duplicate_authority(
        forged_state,
        node_identity="node:126166",
        replacement_display_date="Thursday, October 31, 2002",
        replacement_date="2002-10-31",
    )

    # Prove this is the reported exploit rather than an ordinary broken digest:
    # with only the duplicate trust root disabled, every mutable invariant
    # validates after the attacker recomputes the complete state.
    mutable_only = deepcopy(forged_state)
    mutable_coverage = mutable_only["sources"][
        regulatory_monitor.SOURCE_KEY_FINRA
    ]["coverage"]
    test_version = "test-mutable-only-recovery-anchor"
    monkeypatch.setitem(
        regulatory_monitor.FINRA_DETAIL_IDENTITY_ANCHORS,
        test_version,
        (
            regulatory_monitor
            .FINRA_RECOVERY_DUPLICATE_ANCHOR_DETAIL_IDENTITY_BINDING_DIGEST
        ),
    )
    mutable_coverage["detail_identity_anchor"] = test_version
    mutable_coverage.pop("duplicate_recovery_anchor_digest")
    assert regulatory_monitor._validate_regulatory_state(
        mutable_only,
        [regulatory_monitor.SOURCE_KEY_FINRA],
    ) == []

    errors = regulatory_monitor._validate_regulatory_state(
        forged_state,
        [regulatory_monitor.SOURCE_KEY_FINRA],
    )
    assert any(
        "reviewed duplicate recovery anchor" in error for error in errors
    ), errors


@pytest.mark.parametrize(
    "mutation",
    ("date", "proof", "content", "node", "url"),
)
def test_finra_reviewed_duplicate_anchor_rejects_single_fact_mutations(
    mutation,
):
    """Each minimum bound fact is independently outside mutable state trust."""
    state = _load_shipped_state()
    source_state = state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    coverage = source_state["coverage"]
    record = next(
        item
        for item in coverage["date_resolution_ledger"]
        if item["node_identity"] == "node:126166"
    )

    if mutation == "date":
        record["publication_date"] = "2002-10-31"
    elif mutation == "proof":
        record["detail_date_proof"] += "\n<!-- coherent proof rewrite -->"
        record["detail_date_proof_hash"] = compute_hash(
            record["detail_date_proof"]
        )
    elif mutation == "content":
        record["detail_content"] += "\n\nCoherently rewritten detail."
        replacement_hash = compute_hash(record["detail_content"])
        record["detail_hash"] = replacement_hash
        proof_facts = regulatory_monitor._finra_duplicate_date_proof_facts(
            record["detail_date_proof"]
        )
        entry_identity = (
            regulatory_monitor._finra_resolve_identity_via_ledger(
                regulatory_monitor._extract_finra_document_id(
                    proof_facts[0]
                ),
                regulatory_monitor._finra_alias_map(
                    coverage["alias_ledger"]
                ),
            )
        )
        source_state["entries"][entry_identity] = replacement_hash
        for duplicate in coverage["duplicate_ledger"]:
            if duplicate["node_identity"] == record["node_identity"]:
                duplicate["detail_hash"] = replacement_hash
        coverage["entries_digest"] = regulatory_monitor._entries_digest(
            source_state["entries"]
        )
    elif mutation == "node":
        record["node_identity"] = "node:999999"
    elif mutation == "url":
        old_url = (
            "https://www.finra.org/rules-guidance/notices/FYI-10-2002"
        )
        new_url = (
            "https://www.finra.org/rules-guidance/notices/"
            "forged-recovery-url"
        )
        record["detail_date_proof"] = record[
            "detail_date_proof"
        ].replace(old_url, new_url, 1)
        record["detail_date_proof_hash"] = compute_hash(
            record["detail_date_proof"]
        )
    else:  # pragma: no cover - parametrization is closed above
        raise AssertionError(f"unknown mutation: {mutation}")

    errors = regulatory_monitor._validate_regulatory_state(
        state,
        [regulatory_monitor.SOURCE_KEY_FINRA],
    )
    assert any("duplicate recovery anchor" in error for error in errors), errors


@pytest.mark.parametrize("mutation", ("missing", "extra"))
def test_finra_reviewed_duplicate_anchor_requires_complete_state_set(
    mutation,
):
    """The retained recovery subset cannot omit or duplicate anchor members."""
    state = _load_shipped_state()
    ledger = state["sources"][regulatory_monitor.SOURCE_KEY_FINRA][
        "coverage"
    ]["date_resolution_ledger"]
    if mutation == "missing":
        ledger.pop()
    else:
        ledger.append(deepcopy(ledger[0]))

    errors = regulatory_monitor._validate_regulatory_state(
        state,
        [regulatory_monitor.SOURCE_KEY_FINRA],
    )
    assert any(
        "reviewed duplicate recovery anchor" in error
        or "duplicate recovery anchor records are duplicated" in error
        for error in errors
    ), errors


@pytest.mark.parametrize(
    ("mutation", "expected"),
    (
        ("missing", "record count"),
        ("extra", "record count"),
        ("reordered", "canonical order"),
        ("duplicate", "duplicate or ambiguous"),
    ),
)
def test_finra_code_held_anchor_rejects_incomplete_or_ambiguous_catalog(
    monkeypatch,
    mutation,
    expected,
):
    """The repository trust root itself has exact ordered-set semantics."""
    records = list(
        regulatory_monitor.FINRA_RECOVERY_DUPLICATE_ANCHOR_RECORDS
    )
    if mutation == "missing":
        records.pop()
    elif mutation == "extra":
        records.append((
            "https://www.finra.org/rules-guidance/notices/future-anchor",
            "https://www.finra.org/node/999999",
            "2026-08-10",
            "sha256:" + ("0" * 64),
            "sha256:" + ("1" * 64),
        ))
    elif mutation == "reordered":
        records.reverse()
    elif mutation == "duplicate":
        records[-1] = records[0]
    else:  # pragma: no cover - parametrization is closed above
        raise AssertionError(f"unknown mutation: {mutation}")
    monkeypatch.setattr(
        regulatory_monitor,
        "FINRA_RECOVERY_DUPLICATE_ANCHOR_RECORDS",
        tuple(records),
    )

    errors = (
        regulatory_monitor._finra_recovery_duplicate_anchor_catalog_errors()
    )
    assert any(expected in error for error in errors), errors


def test_finra_reviewed_duplicate_anchor_matches_current_recovery_state():
    """The legitimate reviewed recovery succeeds against the code-held root."""
    source_state = _load_shipped_finra_source_state()
    coverage = source_state["coverage"]
    assert (
        coverage["detail_identity_anchor"]
        == regulatory_monitor.FINRA_RECOVERY_DUPLICATE_ANCHOR_VERSION
    )
    assert coverage["duplicate_recovery_anchor_digest"] == (
        regulatory_monitor.FINRA_RECOVERY_DUPLICATE_ANCHOR_DIGEST
    )
    assert (
        regulatory_monitor._finra_recovery_duplicate_anchor_digest()
        == regulatory_monitor.FINRA_RECOVERY_DUPLICATE_ANCHOR_DIGEST
    )
    assert regulatory_monitor._validate_finra_recovery_duplicate_anchor(
        coverage["date_resolution_ledger"],
        detail_identity_anchor=coverage["detail_identity_anchor"],
        persisted_anchor_digest=coverage[
            "duplicate_recovery_anchor_digest"
        ],
    ) == []


def test_finra_reviewed_anchor_does_not_freeze_future_duplicate_records():
    """A valid later duplicate outside the reviewed recovery set is unanchored."""
    source_state = _load_shipped_finra_source_state()
    coverage = source_state["coverage"]
    future = deepcopy(coverage["date_resolution_ledger"][0])
    facts = regulatory_monitor._finra_duplicate_date_proof_facts(
        future["detail_date_proof"]
    )
    old_url, old_node_url, _date = facts
    new_url = (
        "https://www.finra.org/rules-guidance/notices/"
        "post-recovery-future-duplicate"
    )
    new_node_url = "https://www.finra.org/node/999999"
    old_node_id = old_node_url.rsplit("/", 1)[-1]
    future["node_identity"] = "node:999999"
    future["detail_date_proof"] = (
        future["detail_date_proof"]
        .replace(old_url, new_url, 1)
        .replace(old_node_url, new_node_url, 1)
        .replace(f"page-node-{old_node_id}", "page-node-999999", 1)
    )
    future["detail_date_proof_hash"] = compute_hash(
        future["detail_date_proof"]
    )

    assert regulatory_monitor._validate_finra_recovery_duplicate_anchor(
        [*coverage["date_resolution_ledger"], future],
        detail_identity_anchor=coverage["detail_identity_anchor"],
        persisted_anchor_digest=coverage[
            "duplicate_recovery_anchor_digest"
        ],
    ) == []


def test_finra_anchored_proofs_allow_new_supplemental_binding():
    source_state = _load_shipped_finra_source_state()
    coverage = source_state["coverage"]
    new_url = "https://www.finra.org/rules-guidance/notices/26-16"
    new_node = "https://www.finra.org/node/999999"
    supplemental = [_detail_identity_proof("26-16", new_node)]
    entries = {
        **source_state["entries"],
        new_node: "sha256:new",
    }
    fetched = [
        *coverage["fetched_entry_identities"],
        new_node,
    ]

    errors = regulatory_monitor._validate_finra_alias_ledger(
        coverage["alias_ledger"],
        entries,
        fetched,
        detail_identity_proofs=coverage["detail_identity_proofs"],
        supplemental_detail_identity_proofs=supplemental,
        retained_detail_urls={
            *regulatory_monitor._finra_retained_listing_detail_urls(
                coverage["pass_proofs"]
            ),
            new_url,
        },
        immutable_binding_digest=(
            regulatory_monitor.FINRA_DETAIL_IDENTITY_ANCHORS[
                coverage["detail_identity_anchor"]
            ]
        ),
    )

    assert errors == []
    assert regulatory_monitor._finra_detail_identity_proof_digest(
        coverage["detail_identity_proofs"]
    ) == coverage["detail_identity_proof_digest"]


def test_finra_removed_anchor_proof_remains_inert_trust_evidence():
    source_state = _load_shipped_finra_source_state()
    coverage = source_state["coverage"]
    removed_alias = coverage["alias_ledger"][0]
    removed_target = removed_alias["canonical_identity"]
    aliases = [
        alias for alias in coverage["alias_ledger"]
        if alias is not removed_alias
    ]
    entries = {
        identity: content_hash
        for identity, content_hash in source_state["entries"].items()
        if identity != removed_target
    }
    fetched = [
        identity for identity in coverage["fetched_entry_identities"]
        if identity != removed_target
    ]

    errors = regulatory_monitor._validate_finra_alias_ledger(
        aliases,
        entries,
        fetched,
        detail_identity_proofs=coverage["detail_identity_proofs"],
        supplemental_detail_identity_proofs=[],
        retained_detail_urls=(
            regulatory_monitor._finra_retained_listing_detail_urls(
                coverage["pass_proofs"]
            )
            - {
                regulatory_monitor._finra_alias_source_url(
                    removed_alias["old_identity"]
                )
            }
        ),
        immutable_binding_digest=(
            regulatory_monitor.FINRA_DETAIL_IDENTITY_ANCHORS[
                coverage["detail_identity_anchor"]
            ]
        ),
    )

    assert errors == []


def test_finra_supplemental_proof_digest_tracks_add_update_remove():
    first = _detail_identity_proof(
        "26-16",
        "https://www.finra.org/node/999999",
    )
    updated = first.replace("Notice to Members", "Regulatory Notice")

    empty_digest = regulatory_monitor._finra_detail_identity_proof_digest([])
    added_digest = regulatory_monitor._finra_detail_identity_proof_digest(
        [first]
    )
    updated_digest = regulatory_monitor._finra_detail_identity_proof_digest(
        [updated]
    )

    assert added_digest != empty_digest
    assert updated_digest != added_digest
    assert regulatory_monitor._finra_detail_identity_proof_digest([]) == (
        empty_digest
    )


def test_finra_coherent_duplicate_date_rewrite_without_authority_is_rejected():
    """Recomputed rows/flags cannot replace independent detail-date authority."""
    forged_state = _load_shipped_state()
    forged = forged_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    coverage = forged["coverage"]
    node_identity = "node:126166"

    for proof in coverage["pass_proofs"]:
        affected_pages = set()
        rows = list(_retained_finra_rows_for_node(
            forged, proof, node_identity
        ))
        assert len(rows) == 2
        for page_index, _page, _row_index, row in rows:
            _rewrite_finra_row_date(row, "Thursday, October 31, 2002")
            affected_pages.add(page_index)
        for page_index in affected_pages:
            proof["page_row_digests"][page_index] = _page_row_digest(
                proof["page_row_payloads"][page_index]
            )

    duplicate = next(
        record
        for record in coverage["duplicate_ledger"]
        if record["node_identity"] == node_identity
    )
    proof = coverage["pass_proofs"][0]
    retained = next(
        row
        for _page_index, page, row_index, row
        in _retained_finra_rows_for_node(forged, proof, node_identity)
        if page == duplicate["page"] and row_index == duplicate["row_index"]
    )
    duplicate["raw_payload"] = deepcopy(retained)
    duplicate["raw_row_digest"] = _page_row_digest(retained)
    duplicate["listing_date_conflict"] = False
    duplicate["resolves_listing_date_conflict"] = False
    coverage["date_resolution_ledger"] = [
        record
        for record in coverage["date_resolution_ledger"]
        if record["node_identity"] != node_identity
    ]

    for index, retained_proof in enumerate(coverage["pass_proofs"]):
        assert regulatory_monitor._finra_pass_proof_recomputation_errors(
            regulatory_monitor.SOURCE_KEY_FINRA,
            retained_proof,
            index,
        ) == []

    errors = regulatory_monitor._validate_regulatory_state(
        forged_state,
        [regulatory_monitor.SOURCE_KEY_FINRA],
    )
    assert not any(
        "duplicate ledger does not exactly match duplicates proven by both passes"
        in error
        for error in errors
    ), errors
    assert any("every duplicate node" in error for error in errors), errors


def test_finra_pass_proof_rejects_fabricated_listing_date_field():
    """Persisted rows accept only text/links, exactly as production emits."""
    source_state = _load_shipped_finra_source_state()
    forged = deepcopy(source_state)
    for proof in forged["coverage"]["pass_proofs"]:
        proof["page_row_payloads"][0][0]["listing_date"] = "2026-01-01"
        proof["page_row_digests"][0] = _page_row_digest(
            proof["page_row_payloads"][0]
        )

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
    )
    assert any(
        "production row evidence schema" in error for error in errors
    ), errors


@pytest.mark.parametrize(
    ("tamper", "expected"),
    (
        ("wrong-node", "bound to the wrong node"),
        ("wrong-date", "authoritative publication date"),
        ("wrong-detail-hash", "detail content does not match its hash"),
        ("wrong-proof-hash", "date proof does not match its hash"),
    ),
)
def test_finra_duplicate_authority_rejects_wrong_node_date_or_hash(
    tamper,
    expected,
):
    """The raw date proof, detail payload, node, and both hashes must agree."""
    source_state = _load_shipped_finra_source_state()
    forged = deepcopy(source_state)
    record = next(
        item
        for item in forged["coverage"]["date_resolution_ledger"]
        if item["node_identity"] == "node:126166"
    )

    if tamper == "wrong-node":
        record["detail_date_proof"] = record["detail_date_proof"].replace(
            "126166", "999999"
        )
        record["detail_date_proof_hash"] = compute_hash(
            record["detail_date_proof"]
        )
    elif tamper == "wrong-date":
        record["publication_date"] = "2002-10-31"
    elif tamper == "wrong-detail-hash":
        record["detail_hash"] = "sha256:" + ("0" * 64)
    elif tamper == "wrong-proof-hash":
        record["detail_date_proof_hash"] = "sha256:" + ("0" * 64)
    else:  # pragma: no cover - parametrization is closed above
        raise AssertionError(f"unknown tamper case: {tamper}")

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
    )
    assert any(expected in error for error in errors), errors


def test_finra_every_duplicate_has_legitimate_authoritative_date_evidence():
    """Matching duplicates remain valid, but none may omit detail-date proof."""
    source_state = _load_shipped_finra_source_state()
    coverage = source_state["coverage"]
    duplicate_nodes = {
        record["node_identity"] for record in coverage["duplicate_ledger"]
    }
    authority_nodes = {
        record["node_identity"]
        for record in coverage["date_resolution_ledger"]
    }

    assert len(coverage["duplicate_ledger"]) == 55
    assert len(duplicate_nodes) == 55
    assert authority_nodes == duplicate_nodes
    assert len(coverage["date_resolution_ledger"]) == 55
    assert any(
        not record["conflicts"]
        for record in coverage["date_resolution_ledger"]
    )
    assert regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    ) == []


@pytest.mark.parametrize(
    "ledger, expected",
    [
        (
            [
                _alias("a", "b", "sha256:x"),
                _alias("b", "c", "sha256:x"),
            ],
            "cycle",
        ),
        (
            [
                _alias("a", "b", "sha256:x"),
                _alias("a", "c", "sha256:x"),
            ],
            "multiple targets",
        ),
        (
            [
                _alias("a", "b", "sha256:x"),
                _alias("c", "b", "sha256:x"),
            ],
            "one-to-one",
        ),
        (
            [
                {
                    **_alias("a", "b", "sha256:x"),
                    "evidence": {
                        "source_hash_at_migration": "sha256:wrong",
                        "canonical_hash_at_migration": "sha256:x",
                        "reason": "unverified",
                    },
                }
            ],
            "source hash evidence",
        ),
    ],
)
def test_finra_alias_ledger_rejects_cycles_conflicts_and_unverified_evidence(
    ledger, expected
):
    errors = regulatory_monitor._validate_finra_alias_ledger(
        ledger,
        {"b": "sha256:x", "c": "sha256:x"},
        ["b", "c"],
    )
    assert any(expected in error for error in errors)


def test_finra_unaccounted_leftover_identity_fails_closed():
    """A persisted identity outside the fetched set cannot hide behind a watermark."""
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "entries": {"node-123": "sha256:x", "stale": "sha256:y"},
                "coverage": {
                    "schema_version": 1,
                    "source": regulatory_monitor.SOURCE_KEY_FINRA,
                    "entry_count": 2,
                    "entries_digest": regulatory_monitor._entries_digest(
                        {"node-123": "sha256:x", "stale": "sha256:y"}
                    ),
                    "listing_mode": "complete-unfiltered",
                    "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
                    "listing_record_count": 1,
                    "raw_row_count": 1,
                    "resolved_row_count": 1,
                    "unresolved_row_count": 0,
                    "unique_node_count": 1,
                    "pages_fetched": 1,
                    "declared_pages": 1,
                    "detail_count": 1,
                    "page_numbers": [0],
                    "pass_proofs": [],
                    "duplicate_ledger": [],
                    "date_resolution_ledger": [],
                    "conflict_ledger": [],
                    "fetched_entry_identities": ["node-123"],
                    "fetched_entry_identity_digest": regulatory_monitor._identity_digest(
                        ["node-123"]
                    ),
                    "entry_identity_digest": regulatory_monitor._identity_digest(
                        ["node-123", "stale"]
                    ),
                    "alias_ledger": [],
                    "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
                    "detail_identity_proofs": [],
                    "detail_identity_proof_digest": (
                        regulatory_monitor._finra_detail_identity_proof_digest([])
                    ),
                    "detail_identity_anchor": None,
                },
            }
        }
    }
    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA],
    )
    assert any("stale or unaccounted identities" in error for error in errors)


def test_save_state_atomic_arg_order(monkeypatch):
    """Real (non-dry-run) save path must pass (dict, path), not (path, dict)."""
    captured = {}

    def fake_save(*args, **kwargs):
        captured['args'] = args
        captured['kwargs'] = kwargs

    # Capture the save call instead of writing to disk.
    monkeypatch.setattr(regulatory_monitor, 'save_state_atomic', fake_save)

    run_state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "last_checked": "2026-08-01",
                "entries": {},
                "coverage": {
                    "schema_version": 1,
                    "source": regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
                    "entry_count": 0,
                    "entries_digest": regulatory_monitor._entries_digest({}),
                    "watermark": {
                        "last_run": "2026-08-01T00:00:00+00:00",
                        "last_checked": "2026-08-01",
                    },
                    "complete": True,
                    "window_start": "2026-08-01",
                    "query": {},
                    "expected_count": 0,
                    "fetched_count": 0,
                    "pages_fetched": 1,
                    "declared_pages": 1,
                    "page_numbers": [1],
                },
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": {},
                "coverage": {
                    "schema_version": 1,
                    "source": regulatory_monitor.SOURCE_KEY_FINRA,
                    "entry_count": 0,
                    "entries_digest": regulatory_monitor._entries_digest({}),
                    "watermark": {"last_run": "2026-08-01T00:00:00+00:00"},
                    "complete": True,
                    "listing_mode": "complete-unfiltered",
                    "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
                    "listing_record_count": 0,
                    "pages_fetched": 1,
                    "declared_pages": 1,
                    "detail_count": 0,
                    "page_numbers": [0],
                    "page_identities": [
                        {"requested": 0, "final": 0, "active": 0},
                    ],
                    "fetched_entry_identities": [],
                    "fetched_entry_identity_digest": regulatory_monitor._identity_digest([]),
                    "entry_identity_digest": regulatory_monitor._identity_digest([]),
                    "alias_ledger": [],
                    "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
                    "detail_identity_proofs": [],
                    "detail_identity_proof_digest": (
                        regulatory_monitor._finra_detail_identity_proof_digest([])
                    ),
                    "detail_identity_anchor": None,
                    "raw_row_count": 0,
                    "resolved_row_count": 0,
                    "unresolved_row_count": 0,
                    "unique_node_count": 0,
                    "pass_proofs": [
                        {
                            "token": "test-pass-1",
                            "declared_pages": 1,
                            "pages_fetched": 1,
                            "page_numbers": [0],
                            "page_identities": [{"requested": 0, "final": 0, "active": 0}],
                            "page_row_counts": [0],
                            "page_row_digests": [compute_hash("[]")],
                            "page_row_payloads": [[]],
                            "raw_row_count": 0,
                            "resolved_row_count": 0,
                            "unresolved_row_count": 0,
                            "unique_node_count": 0,
                        },
                        {
                            "token": "test-pass-2",
                            "declared_pages": 1,
                            "pages_fetched": 1,
                            "page_numbers": [0],
                            "page_identities": [{"requested": 0, "final": 0, "active": 0}],
                            "page_row_counts": [0],
                            "page_row_digests": [compute_hash("[]")],
                            "page_row_payloads": [[]],
                            "raw_row_count": 0,
                            "resolved_row_count": 0,
                            "unresolved_row_count": 0,
                            "unique_node_count": 0,
                        },
                    ],
                    "duplicate_ledger": [],
                    "date_resolution_ledger": [],
                    "conflict_ledger": [],
                },
            },
        },
    }
    # Stub complete, proof-carrying source results so the no-changes path
    # reaches the real save after post-update state validation.
    monkeypatch.setattr(
        regulatory_monitor,
        'fetch_federal_register_documents',
        lambda *a, **k: regulatory_monitor.FetchResult(
            [],
            complete=True,
            coverage=deepcopy(
                run_state["sources"][
                    regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER
                ]["coverage"]
            ),
        ),
    )
    monkeypatch.setattr(
        regulatory_monitor,
        'fetch_finra_notices',
        lambda *a, **k: regulatory_monitor.FetchResult(
            [],
            complete=True,
            coverage=deepcopy(
                run_state["sources"][
                    regulatory_monitor.SOURCE_KEY_FINRA
                ]["coverage"]
            ),
        ),
    )
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: run_state)

    # Run the real (non --dry-run) code path.
    monkeypatch.setattr(sys, 'argv', ['regulatory_monitor.py'])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 0, "no-changes run should exit 0"
    assert 'args' in captured, "save_state_atomic was never called on the real save path"

    args = captured['args']
    assert len(args) >= 2, f"expected (state, path) positional args, got {args!r}"

    # First positional arg MUST be the state dict.
    assert isinstance(args[0], dict), (
        f"save_state_atomic first arg must be the state dict, got {type(args[0]).__name__}. "
        "Arguments are likely swapped (path, dict) instead of (dict, path)."
    )

    # Second positional arg MUST be the state file path.
    assert args[1] == regulatory_monitor.STATE_FILE, (
        f"save_state_atomic second arg must be STATE_FILE, got {args[1]!r}"
    )


def _run_main(monkeypatch, *, state, fed_items, finra_items, args=None):
    """Run regulatory_monitor.main() with network + disk side effects stubbed.

    Returns (exit_code, saved_state, reported_items).
    """
    for source_key in (
        regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
        regulatory_monitor.SOURCE_KEY_FINRA,
    ):
        source_state = state.get("sources", {}).get(source_key)
        if not isinstance(source_state, dict) or "coverage" in source_state:
            continue
        entries = source_state.get("entries", {})
        if not isinstance(entries, dict):
            continue
        common = {
            "schema_version": 1,
            "source": source_key,
            "entry_count": len(entries),
            "entries_digest": regulatory_monitor._entries_digest(entries),
            "watermark": regulatory_monitor._coverage_watermark(source_state),
            "complete": True,
        }
        if source_key == regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER:
            common.update({
                "window_start": source_state.get("last_checked", "2026-01-01"),
                "query": {},
                "expected_count": len(entries),
                "fetched_count": len(entries),
                "pages_fetched": 1,
                "declared_pages": 1,
                "page_numbers": [1],
            })
        else:
            common.update({
                "listing_mode": "complete-unfiltered",
                "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
                "listing_record_count": len(entries),
                "pages_fetched": 1,
                "declared_pages": 1,
                "detail_count": len(entries),
                "page_numbers": [0],
                "page_identities": [
                    {"requested": 0, "final": 0, "active": 0},
                ],
                "fetched_entry_identities": sorted(entries),
                "fetched_entry_identity_digest": regulatory_monitor._identity_digest(
                    entries
                ),
                "entry_identity_digest": regulatory_monitor._identity_digest(
                    entries
                ),
                "alias_ledger": [],
                "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
                "detail_identity_proofs": [],
                "detail_identity_proof_digest": (
                    regulatory_monitor._finra_detail_identity_proof_digest([])
                ),
                "detail_identity_anchor": None,
                "raw_row_count": len(entries),
                "resolved_row_count": len(entries),
                "unresolved_row_count": 0,
                "unique_node_count": len(entries),
                "pass_proofs": _synthetic_pass_proofs(sorted(entries)),
                "duplicate_ledger": [],
                "date_resolution_ledger": [],
                "conflict_ledger": [],
            })
        source_state["coverage"] = common
    captured = {'saved_state': None, 'report_items': None}

    monkeypatch.setattr(regulatory_monitor, 'load_state', lambda *a, **k: state)

    def fake_save(saved_state, _path):
        captured['saved_state'] = saved_state

    monkeypatch.setattr(regulatory_monitor, 'save_state_atomic', fake_save)

    def fake_report(items, _path):
        captured['report_items'] = list(items)

    monkeypatch.setattr(regulatory_monitor, 'generate_regulatory_report', fake_report)

    def as_result(items, source_key):
        if isinstance(items, regulatory_monitor.FetchResult):
            return items
        items = list(items)
        if source_key == regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER:
            coverage = {
                "complete": True,
                "window_start": "2026-01-01",
                "query": {},
                "expected_count": len(items),
                "fetched_count": len(items),
                "pages_fetched": 1,
                "declared_pages": 1,
                "page_numbers": [1],
            }
        else:
            coverage = {
                "complete": True,
                "listing_mode": "complete-unfiltered",
                "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
                "listing_record_count": len(items),
                "pages_fetched": 1,
                "declared_pages": 1,
                "detail_count": len(items),
                "page_numbers": [0],
                "page_identities": [
                    {"requested": 0, "final": 0, "active": 0},
                ],
                "fetched_entry_identities": sorted(
                    item.document_id if item.document_id else item.url
                    for item in items
                ),
                "fetched_entry_identity_digest": regulatory_monitor._identity_digest(
                    item.document_id if item.document_id else item.url
                    for item in items
                ),
                "entry_identity_digest": regulatory_monitor._identity_digest(
                    item.document_id if item.document_id else item.url
                    for item in items
                ),
                "alias_ledger": [],
                "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
                "detail_identity_proofs": [],
                "detail_identity_proof_digest": (
                    regulatory_monitor._finra_detail_identity_proof_digest([])
                ),
                "detail_identity_anchor": None,
                "raw_row_count": len(items),
                "resolved_row_count": len(items),
                "unresolved_row_count": 0,
                "unique_node_count": len(items),
                "pass_proofs": _synthetic_pass_proofs(sorted(
                    item.document_id if item.document_id else item.url
                    for item in items
                )),
                "duplicate_ledger": [],
                "date_resolution_ledger": [],
                "conflict_ledger": [],
            }
        return regulatory_monitor.FetchResult(
            items,
            complete=True,
            coverage=coverage,
        )

    monkeypatch.setattr(
        regulatory_monitor, 'fetch_federal_register_documents',
        lambda *a, **k: as_result(fed_items, regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER),
    )
    monkeypatch.setattr(
        regulatory_monitor, 'fetch_finra_notices',
        lambda *a, **k: as_result(finra_items, regulatory_monitor.SOURCE_KEY_FINRA),
    )

    monkeypatch.setattr(
        sys,
        'argv',
        ['regulatory_monitor.py', *(args or [])],
    )

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    return exc.value.code, captured['saved_state'], captured['report_items']


def test_first_run_establishes_baseline_without_reporting(monkeypatch):
    """Explicitly approved baseline mode persists a baseline without reporting.

    Regression guard for the burst-report defect: without first-run suppression,
    a no-prior-state run flags every fetched item as new and emits a noisy
    ~30-day report with exit 1. Only the explicitly approved manual mode records
    the baseline silently (exit 0).
    """
    # CI sets GITHUB_ACTIONS globally; this test explicitly models the
    # operator-approved local-only baseline path.
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    fed_items = [
        _make_item("SEC Rule A", "fr-1"),
        _make_item("CFTC Rule B", "fr-2", agency="CFTC"),
    ]
    finra_items = [
        _make_item(
            "FINRA Notice 26-01",
            "FINRA 26-01",
            source="FINRA",
            agency="FINRA",
            url="https://www.finra.org/rules-guidance/notices/26-01",
        ),
    ]

    # Empty unified state => no prior state for either source.
    monkeypatch.setenv("REGULATORY_MONITOR_BASELINE_APPROVED", "I_UNDERSTAND")
    code, saved_state, report_items = _run_main(
        monkeypatch,
        state={},
        fed_items=fed_items,
        finra_items=finra_items,
        args=["--initialize-baseline"],
    )

    assert code == 0, "first run should exit 0 (no burst report)"
    assert report_items is None, "first run must NOT generate a report"

    # Baseline persisted so subsequent runs are incremental.
    fed_state = saved_state['sources'][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]
    finra_state = saved_state['sources'][regulatory_monitor.SOURCE_KEY_FINRA]
    assert fed_state.get('last_run'), "fed baseline last_run must be recorded"
    assert set(fed_state['entries']) == {'fr-1', 'fr-2'}, "fed baseline entries persisted"
    assert finra_state.get('last_run'), "finra baseline last_run must be recorded"
    assert set(finra_state['entries']) == {'FINRA 26-01'}, (
        "finra baseline entries persisted"
    )


def test_missing_regulatory_state_fails_before_fetch_or_write(monkeypatch):
    """A scheduled run must not baseline an absent regulatory section silently."""
    state = {
        "version": 1,
        "sources": {
            "learn": {"last_run": "2026-08-01T00:00:00+00:00"},
        },
    }
    fetch_calls = []
    save_calls = []

    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: state)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_federal_register_documents",
        lambda *a, **k: fetch_calls.append("federal") or [],
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_finra_notices",
        lambda *a, **k: fetch_calls.append("finra") or [],
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "save_state_atomic",
        lambda *a, **k: save_calls.append(a),
    )
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2
    assert fetch_calls == []
    assert save_calls == []


def test_corrupt_regulatory_state_fails_before_baseline_suppression(monkeypatch):
    """Malformed entries/last_run cannot trigger implicit first-run baseline mode."""
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "not-a-timestamp",
                "entries": [],
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": {},
            },
        },
    }
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: state)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_federal_register_documents",
        lambda *a, **k: pytest.fail("corrupt state must stop before fetching"),
    )
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2


def test_known_incident_state_rejects_watermarks_without_coverage_proof(monkeypatch):
    """The e802babd 332/2 state cannot advance Aug-9 watermarks."""
    corrupt_state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-08-09T08:21:38+00:00",
                "last_checked": "2026-08-09",
                "entries": {
                    f"2026-{number:05d}": "sha256:corrupt"
                    for number in range(332)
                },
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-09T08:21:38+00:00",
                "entries": {
                    f"FINRA 26-{number:02d}": "sha256:corrupt"
                    for number in range(1, 3)
                },
            },
        },
    }
    fetch_calls = []
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: corrupt_state)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_federal_register_documents",
        lambda *a, **k: fetch_calls.append("federal") or [],
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_finra_notices",
        lambda *a, **k: fetch_calls.append("finra") or [],
    )
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2
    assert fetch_calls == []


def test_coverage_proof_rejects_entry_count_or_digest_drift():
    """A proof cannot be reused after entries change under the watermark."""
    source_state = {
        "last_run": "2026-08-09T08:21:38+00:00",
        "last_checked": "2026-08-09",
        "entries": {"2026-00001": "sha256:one"},
        "coverage": {
            "schema_version": 1,
            "source": regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
            "entry_count": 1,
            "entries_digest": regulatory_monitor._entries_digest(
                {"2026-00001": "sha256:old"}
            ),
            "watermark": {
                "last_run": "2026-08-09T08:21:38+00:00",
                "last_checked": "2026-08-09",
            },
            "complete": True,
            "window_start": "2026-08-09",
            "query": {},
            "expected_count": 1,
            "fetched_count": 1,
            "pages_fetched": 1,
            "declared_pages": 1,
            "page_numbers": [1],
        },
    }

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
        source_state,
    )

    assert any("entries_digest" in error for error in errors)


def test_finra_zero_result_coverage_proof_is_valid():
    """The explicit zero-result response is a complete, verifiable shape."""
    source_state = {
        "last_run": "2026-08-09T08:21:38+00:00",
        "entries": {},
        "coverage": {
            "schema_version": 1,
            "source": regulatory_monitor.SOURCE_KEY_FINRA,
            "entry_count": 0,
            "entries_digest": regulatory_monitor._entries_digest({}),
            "watermark": {"last_run": "2026-08-09T08:21:38+00:00"},
            "complete": True,
            "listing_mode": "complete-unfiltered",
            "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
            "listing_record_count": 0,
            "pages_fetched": 1,
            "declared_pages": 0,
            "detail_count": 0,
            "page_numbers": [0],
            "page_identities": [
                {"requested": 0, "final": 0, "active": 0},
            ],
            "fetched_entry_identities": [],
            "fetched_entry_identity_digest": regulatory_monitor._identity_digest([]),
            "entry_identity_digest": regulatory_monitor._identity_digest([]),
            "alias_ledger": [],
            "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
            "detail_identity_proofs": [],
            "detail_identity_proof_digest": (
                regulatory_monitor._finra_detail_identity_proof_digest([])
            ),
            "detail_identity_anchor": None,
            "raw_row_count": 0,
            "resolved_row_count": 0,
            "unresolved_row_count": 0,
            "unique_node_count": 0,
            "pass_proofs": [
                {
                    "token": "zero-pass-1",
                    "declared_pages": 0,
                    "pages_fetched": 1,
                    "page_numbers": [0],
                    "page_identities": [
                        {"requested": 0, "final": 0, "active": 0},
                    ],
                    "page_row_counts": [0],
                    "page_row_digests": [compute_hash("[]")],
                    "page_row_payloads": [[]],
                    "raw_row_count": 0,
                    "resolved_row_count": 0,
                    "unresolved_row_count": 0,
                    "unique_node_count": 0,
                },
                {
                    "token": "zero-pass-2",
                    "declared_pages": 0,
                    "pages_fetched": 1,
                    "page_numbers": [0],
                    "page_identities": [
                        {"requested": 0, "final": 0, "active": 0},
                    ],
                    "page_row_counts": [0],
                    "page_row_digests": [compute_hash("[]")],
                    "page_row_payloads": [[]],
                    "raw_row_count": 0,
                    "resolved_row_count": 0,
                    "unresolved_row_count": 0,
                    "unique_node_count": 0,
                },
            ],
            "duplicate_ledger": [],
            "date_resolution_ledger": [],
            "conflict_ledger": [],
        },
    }

    assert regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    ) == []


def test_finra_coverage_rejects_stale_unseen_entry():
    """A watermark cannot advance with an entry absent from fetched identities."""
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    source_state["entries"]["FINRA stale-unseen"] = "sha256:stale"
    source_state["coverage"]["entry_count"] = len(source_state["entries"])
    source_state["coverage"]["entries_digest"] = regulatory_monitor._entries_digest(
        source_state["entries"]
    )
    source_state["coverage"]["entry_identity_digest"] = (
        regulatory_monitor._identity_digest(source_state["entries"])
    )

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any("stale or unaccounted identities" in error for error in errors)


def test_baseline_mode_requires_manual_approval_and_rejects_ci(monkeypatch):
    """Baseline initialization cannot be reached from an unattended workflow."""
    monkeypatch.delenv("REGULATORY_MONITOR_BASELINE_APPROVED", raising=False)
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py", "--initialize-baseline"])
    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()
    assert exc.value.code == 2

    monkeypatch.setenv("REGULATORY_MONITOR_BASELINE_APPROVED", "I_UNDERSTAND")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()
    assert exc.value.code == 2


def test_recovery_findings_do_not_suppress_post_watermark_high_items():
    """Trusted July-20 history must leave FINRA 26-15 and later items reportable."""
    pre_watermark = _make_item(
        "Historical notice",
        "FINRA 26-01",
        pub_date="2026-07-20",
        source="FINRA",
        agency="FINRA",
    )
    post_watermark = _make_item(
        "FINRA Requests Comment on Modernizing Best Execution Guidance",
        "FINRA 26-15",
        pub_date="2026-07-24",
        source="FINRA",
        agency="FINRA",
    )
    post_watermark.classification = regulatory_monitor.CLASSIFICATION_HIGH
    changed_known = _make_item(
        "Edited historical notice",
        "FINRA 26-01",
        abstract="Edited after the trusted watermark.",
        pub_date="2026-07-20",
        source="FINRA",
        agency="FINRA",
    )
    trusted = {
        "last_run": "2026-07-20T09:56:38.066467+00:00",
        "entries": {
            "FINRA 26-01": _item_hash(pre_watermark),
        },
    }

    findings = regulatory_monitor.check_for_recovery_items(
        regulatory_monitor.SOURCE_KEY_FINRA,
        [pre_watermark, post_watermark, changed_known],
        trusted,
    )

    assert {item.document_id for item in findings} == {
        "FINRA 26-15",
        "FINRA 26-01",
    }
    assert post_watermark.classification == regulatory_monitor.CLASSIFICATION_HIGH


def test_recovery_reports_absent_identity_on_watermark_calendar_day():
    """Same-day recovery reports absent identities but not unchanged known ones."""
    same_day_missing = _make_item(
        "Same-day missing notice",
        "FINRA 26-02",
        pub_date="2026-07-20T23:30:00-05:00",
        source="FINRA",
        agency="FINRA",
    )
    same_day_known = _make_item(
        "Same-day known notice",
        "FINRA 26-01",
        pub_date="2026-07-20T08:00:00+09:00",
        source="FINRA",
        agency="FINRA",
    )
    earlier_missing = _make_item(
        "Earlier missing notice",
        "FINRA 25-99",
        pub_date="2026-07-19T23:59:59-05:00",
        source="FINRA",
        agency="FINRA",
    )
    trusted = {
        "last_run": "2026-07-20T09:56:38.066467+00:00",
        "entries": {
            same_day_known.document_id: _item_hash(same_day_known),
        },
    }

    findings = regulatory_monitor.check_for_recovery_items(
        regulatory_monitor.SOURCE_KEY_FINRA,
        [same_day_missing, same_day_known, earlier_missing],
        trusted,
    )

    assert [item.document_id for item in findings] == ["FINRA 26-02"]


def test_subsequent_run_still_detects_new_items(monkeypatch):
    """A run WITH prior state must still detect and report genuinely new items.

    Ensures the baseline suppression only affects the FIRST run, not legitimate
    incremental change detection on later runs.
    """
    known_fed = _make_item("SEC Rule A", "fr-1")
    new_fed = _make_item("SEC Rule C (new)", "fr-3")
    known_finra = _make_item(
        "FINRA Notice 26-01",
        "FINRA 26-01",
        source="FINRA",
        agency="FINRA",
        url="https://www.finra.org/rules-guidance/notices/26-01",
    )

    # Prior persisted state: last_run set (not a baseline) with the known items.
    prior_state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-01-01T00:00:00+00:00",
                "last_checked": "2026-01-01",
                "entries": {"fr-1": _item_hash(known_fed)},
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-01-01T00:00:00+00:00",
                "entries": {"FINRA 26-01": _item_hash(known_finra)},
            },
        },
    }

    code, saved_state, report_items = _run_main(
        monkeypatch,
        state=prior_state,
        fed_items=[known_fed, new_fed],
        finra_items=[known_finra],
    )

    assert code == 1, "new items should trigger exit 1 (PR in CI)"
    assert report_items is not None, "a report must be generated for new items"
    reported_ids = {item.document_id for item in report_items}
    assert reported_ids == {'fr-3'}, "only the genuinely new item should be reported"
    saved_fed = saved_state['sources'][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]
    assert saved_fed['entries']['fr-3'] == _item_hash(new_fed)


def test_successful_no_findings_runs_advance_cursor_across_committed_state(monkeypatch):
    """Exit-0 refresh progress must persist and continue from the next batch."""
    known_items = [
        _make_item(
            f"FINRA Notice 26-{number:02d}",
            f"FINRA 26-{number:02d}",
            source="FINRA",
            agency="FINRA",
            url=f"https://www.finra.org/rules-guidance/notices/26-{number:02d}",
        )
        for number in range(1, 41)
    ]
    entries = {
        item.document_id: _item_hash(item)
        for item in known_items
    }
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": entries,
                "refresh_cursor": 0,
            },
        },
    }

    first_code, first_state, first_report = _run_main(
        monkeypatch,
        state=deepcopy(state),
        fed_items=[],
        finra_items=known_items,
        args=["--source", "finra"],
    )
    second_code, second_state, second_report = _run_main(
        monkeypatch,
        state=deepcopy(first_state),
        fed_items=[],
        finra_items=known_items,
        args=["--source", "finra"],
    )

    assert first_code == second_code == 0
    assert first_report is None and second_report is None
    first_finra = first_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    second_finra = second_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    assert first_finra["refresh_cursor"] == 25
    assert second_finra["refresh_cursor"] == 10
    assert second_finra["last_run"] != "2026-08-01T00:00:00+00:00"


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class _FakeHttpResponse:
    def __init__(self, status_code, *, retry_after=None, url="https://example.test"):
        self.status_code = status_code
        self.headers = {"Retry-After": str(retry_after)} if retry_after is not None else {}
        self.url = url
        self.text = "ok" if status_code == 200 else ""


def test_shared_fetch_page_honors_valid_retry_after(monkeypatch):
    """Shared monitor callers must wait the server-advertised 60 seconds."""
    responses = [
        _FakeHttpResponse(429, retry_after=60),
        _FakeHttpResponse(200),
    ]
    sleeps = []

    class Session:
        def get(self, *_args, **_kwargs):
            return responses.pop(0)

    monkeypatch.setattr(monitoring_shared.time, "sleep", sleeps.append)
    result = monitoring_shared.fetch_page("https://example.test", Session(), max_retries=2)

    assert result["status_code"] == 200
    assert sleeps == [60]


class _FakeSession:
    def __init__(self, responses, *, allow_legacy_finra=True):
        self.responses = list(responses)
        self.calls = []
        if allow_legacy_finra:
            self._finra_legacy_fixture_capability = (
                regulatory_monitor._FINRA_LEGACY_FIXTURE_CAPABILITY
            )
        self._finra_skip_phase_cooldown = True

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeResponse(self.responses.pop(0))


def _federal_doc(document_id):
    return {
        "document_number": document_id,
        "title": f"Document {document_id}",
        "abstract": "",
        "publication_date": "2026-08-01",
        "type": "NOTICE",
        "html_url": f"https://www.federalregister.gov/{document_id}",
        "raw_text_url": (
            "https://www.federalregister.gov/documents/full_text/text/"
            f"2026/08/01/{document_id}.txt"
        ),
        "agencies": [{"slug": "securities-and-exchange-commission", "name": "SEC"}],
    }


def test_federal_register_fetches_and_validates_all_pages():
    """All API pages must be consumed and reconciled with the declared count."""
    session = _FakeSession([
        {
            "count": 3,
            "total_pages": 2,
            "results": [_federal_doc("fr-1"), _federal_doc("fr-2")],
            "next_page_url": "https://www.federalregister.gov/api/v1/documents?page=2",
        },
        {
            "count": 3,
            "total_pages": 2,
            "results": [_federal_doc("fr-3")],
            "next_page_url": None,
        },
    ])
    config = {
        "federal_register": {
            "agencies": [{"slug": "securities-and-exchange-commission", "short_name": "SEC"}],
            "document_types": ["NOTICE"],
        },
        "regulatory": {},
        "keyword_control_map": [],
    }

    result = regulatory_monitor.fetch_federal_register_documents(session, "2026-08-01", config)

    assert result.complete is True
    assert result.expected_count == 3
    assert result.pages_fetched == 2
    assert [item.document_id for item in result] == ["fr-1", "fr-2", "fr-3"]
    assert result[0].url.endswith("/2026/08/01/fr-1.txt")
    assert "raw_text_url" in session.calls[0][1]["params"]["fields[]"]
    assert len(session.calls) == 2


def test_federal_register_zero_results_are_verified():
    """A valid zero-result response is complete; malformed emptiness is not."""
    session = _FakeSession([{"count": 0, "total_pages": None, "results": None, "next_page_url": None}])
    config = {"federal_register": {}, "regulatory": {}, "keyword_control_map": []}

    result = regulatory_monitor.fetch_federal_register_documents(session, "2999-01-01", config)

    assert result.complete is True
    assert result.expected_count == 0
    assert result == []


def test_federal_register_missing_page_link_fails_closed():
    """Declared pages must reconcile even when next_page_url disappears."""
    session = _FakeSession([{
        "count": 3,
        "total_pages": 2,
        "results": [_federal_doc("fr-1"), _federal_doc("fr-2"), _federal_doc("fr-3")],
        "next_page_url": None,
    }])
    config = {"federal_register": {}, "regulatory": {}, "keyword_control_map": []}

    result = regulatory_monitor.fetch_federal_register_documents(session, "2026-08-01", config)

    assert result.complete is False
    assert "declared 2 page(s), fetched 1" in result.error


def test_federal_register_contradictory_zero_metadata_fails_closed():
    """count=0 with a declared page is contradictory, not a valid empty result."""
    session = _FakeSession([{
        "count": 0,
        "total_pages": 1,
        "results": None,
        "next_page_url": None,
    }])
    config = {"federal_register": {}, "regulatory": {}, "keyword_control_map": []}

    result = regulatory_monitor.fetch_federal_register_documents(session, "2999-01-01", config)

    assert result.complete is False
    assert "zero-result" in result.error


def test_federal_register_overlap_fails_closed():
    """Overlapping pages must not silently overwrite or advance the watermark."""
    session = _FakeSession([
        {
            "count": 3,
            "total_pages": 2,
            "results": [_federal_doc("fr-1"), _federal_doc("fr-2")],
            "next_page_url": "https://www.federalregister.gov/api/v1/documents?page=2",
        },
        {
            "count": 3,
            "total_pages": 2,
            "results": [_federal_doc("fr-2")],
            "next_page_url": None,
        },
    ])
    config = {
        "federal_register": {
            "agencies": [{"slug": "securities-and-exchange-commission", "short_name": "SEC"}],
            "document_types": ["NOTICE"],
        },
        "regulatory": {},
        "keyword_control_map": [],
    }

    result = regulatory_monitor.fetch_federal_register_documents(session, "2026-08-01", config)

    assert result.complete is False
    assert "overlap" in result.error


def test_main_does_not_advance_state_on_incomplete_source(monkeypatch):
    """A partial source fetch must fail without saving state or generating a report."""
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "last_checked": "2026-08-01",
                "entries": {"fr-1": "sha256:old"},
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": {},
            },
        },
    }
    original_state = repr(state)
    save_calls = []
    report_calls = []

    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: state)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_federal_register_documents",
        lambda *a, **k: regulatory_monitor.FetchResult(
            [_make_item("Partial", "fr-2")],
            complete=False,
            error="declared count mismatch",
        ),
    )
    monkeypatch.setattr(regulatory_monitor, "fetch_finra_notices", lambda *a, **k: [])
    monkeypatch.setattr(regulatory_monitor, "save_state_atomic", lambda *a, **k: save_calls.append(a))
    monkeypatch.setattr(regulatory_monitor, "generate_regulatory_report", lambda *a, **k: report_calls.append(a))
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2
    assert save_calls == []
    assert report_calls == []
    assert repr(state) == original_state


def test_main_preserves_unrelated_learn_state(monkeypatch):
    """Regulatory updates must not roll back the unrelated Learn source."""
    learn_state = {
        "schema_version": 2,
        "last_run": "2026-08-08T06:54:59.825001+00:00",
        "urls": {"https://learn.example/item": {
            "last_checked": "2026-08-08T06:54:59.825001+00:00",
            "content_hash": "sha256:learn",
        }},
        "statistics": {
            "total_urls": 1,
            "last_run_critical_changes": 4,
            "last_run_high_changes": 3,
            "last_run_medium_changes": 2,
            "last_run_noise_changes": 1,
            "last_run_redirects": 0,
            "last_run_errors": 0,
        },
    }
    state = {
        "version": 1,
        "sources": {
            "learn": deepcopy(learn_state),
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-08-07T00:00:00+00:00",
                "last_checked": "2026-08-07",
                "entries": {},
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-07T00:00:00+00:00",
                "entries": {},
            },
        },
    }
    code, saved_state, _ = _run_main(
        monkeypatch,
        state=state,
        fed_items=[],
        finra_items=[],
    )

    assert code == 0
    assert saved_state["sources"]["learn"] == learn_state


def _finra_listing_page(page, total_pages, records):
    rows = "\n".join(
        f'<tr><td><time datetime="{date}T12:00:00Z"></time>'
        f'<a href="{href}">{title}</a></td></tr>'
        for href, title, date in records
    )
    pager = (
        '<nav class="pagination">'
        f'<li class="page-item active"><span class="page-link">{page + 1}</span></li>'
        f'<a href="?page={total_pages - 1}">Last >> Last page</a>'
        '</nav>'
    )
    return f"<html><body>{rows}{pager}</body></html>"


def _finra_detail_page(title, date, summary):
    return f"""
    <html><body>
      <h1>{title}</h1>
      <div class="field--name-field-core-official-dt">
        <time datetime="{date}T12:00:00Z">{date}</time>
      </div>
      <div class="field--name-body"><h2>Summary</h2><p>{summary}</p>
        <h2>Action Required</h2><p>Comments are requested.</p>
      </div>
    </body></html>
    """


def _finra_detail_page_with_identity(
    title,
    date,
    summary,
    *,
    canonical_url,
    node_id,
):
    """Add the raw canonical/node/title envelope production retains."""
    detail = _finra_detail_page(title, date, summary)
    return (
        detail.replace(
            "<html><body>",
            (
                f'<html><link rel="canonical" href="{canonical_url}">'
                f'<body class="layout-two-sidebars page-node-{node_id}">'
                f'<span id="node-title">{title}</span>'
            ),
            1,
        )
        .replace(
            "</body>",
            (
                '<link rel="shortlink" '
                f'href="https://www.finra.org/node/{node_id}"></body>'
            ),
            1,
        )
    )


def _finra_request_base(url):
    """Remove only the pass cache token from a test request URL."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query.pop(regulatory_monitor.FINRA_CACHE_BUST_PARAM, None)
    base = parsed._replace(query=urlencode(query, doseq=True))
    return urlunparse(base)


def _synthetic_finra_listing(rows):
    """Build a complete listing result for detail/duplicate unit tests."""
    for row_index, row in enumerate(rows):
        row["row_index"] = row_index
        row["page"] = 0
        normalized_date = regulatory_monitor._normalize_finra_date(
            row["listing_date"]
        )
        if normalized_date:
            year, month, day = normalized_date.split("-")
            month_name = (
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November",
                "December",
            )[int(month) - 1]
            date_prefix = f"{month_name} {int(day)}, {year} "
        else:
            date_prefix = ""
        row["raw_payload"] = {
            "text": f"{date_prefix}{row['title']}",
            "links": deepcopy(row["raw_payload"]["links"]),
        }
        row["raw_row_digest"] = _page_row_digest(row["raw_payload"])
    payloads = [row["raw_payload"] for row in rows]
    proof = {
        "token": "test-pass-1",
        "declared_pages": 1,
        "pages_fetched": 1,
        "page_numbers": [0],
        "page_identities": [{"requested": 0, "final": 0, "active": 0}],
        "page_row_counts": [len(rows)],
        "page_row_digests": [_page_row_digest(payloads)],
        "page_row_payloads": [payloads],
        "raw_row_count": len(rows),
        "resolved_row_count": len(rows),
        "unresolved_row_count": 0,
        "unique_node_count": len({row["node_identity"] for row in rows}),
    }
    proof2 = dict(deepcopy(proof), token="test-pass-2")
    return {
        "complete": True,
        "rows": rows,
        "pass_proof": proof,
        "pages_fetched": 1,
        "declared_pages": 1,
        "cutoff_page": None,
        "coverage": {
            "complete": True,
            "listing_mode": "complete-unfiltered",
            "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
            "listing_record_count": len(rows),
            "raw_row_count": len(rows),
            "resolved_row_count": len(rows),
            "unresolved_row_count": 0,
            "unique_node_count": len({row["node_identity"] for row in rows}),
            "pages_fetched": 1,
            "declared_pages": 1,
            "page_numbers": [0],
            "pass_proofs": [proof, proof2],
            "duplicate_ledger": [],
            "date_resolution_ledger": [],
            "conflict_ledger": [],
        },
    }


def _synthetic_finra_pass_result(pages, token):
    rows = []
    page_digests = []
    page_payloads = []
    for page, page_urls in enumerate(pages):
        page_rows = []
        for row_index, slug in enumerate(page_urls):
            row = _synthetic_finra_row(
                f"https://www.finra.org/rules-guidance/notices/{slug}",
                f"url:/rules-guidance/notices/{slug}",
                title=slug,
            )
            row["page"] = page
            row["row_index"] = row_index
            page_rows.append(row)
        rows.extend(page_rows)
        payloads = [row["raw_payload"] for row in page_rows]
        page_payloads.append(payloads)
        page_digests.append(compute_hash(json.dumps(
            payloads,
            sort_keys=True,
            separators=(",", ":"),
        )))
    proof = {
        "token": token,
        "declared_pages": len(pages),
        "pages_fetched": len(pages),
        "page_numbers": list(range(len(pages))),
        "page_identities": [
            {"requested": page, "final": page, "active": page}
            for page in range(len(pages))
        ],
        "page_row_counts": [len(page) for page in pages],
        "page_row_digests": page_digests,
        "page_row_payloads": page_payloads,
        "raw_row_count": len(rows),
        "resolved_row_count": len(rows),
        "unresolved_row_count": 0,
        "unique_node_count": len({row["node_identity"] for row in rows}),
    }
    return {
        "complete": True,
        "rows": rows,
        "records": [
            (row["detail_url"], row["title"], row["listing_date"])
            for row in rows
        ],
        "pages_fetched": len(pages),
        "declared_pages": len(pages),
        "cutoff_page": None,
        "pass_proof": proof,
    }


def _synthetic_finra_row(url, node_identity, title="Notice 26-14"):
    listing_date = "2026-07-09"
    payload = {
        "text": f"July 9, 2026 {title}",
        "links": [{"href": url, "text": title}],
    }
    return {
        "row_index": 0,
        "page": 0,
        "raw_payload": payload,
        "raw_row_digest": compute_hash(json.dumps(
            payload, sort_keys=True, separators=(",", ":")
        )),
        "detail_url": url,
        "node_identity": node_identity,
        "title": title,
        "listing_date": listing_date,
        "unresolved": False,
    }


def test_finra_normalizes_index_php_and_numeric_node_links():
    """Legacy and node links resolve to stable same-origin identities."""
    assert regulatory_monitor._finra_normalize_detail_link(
        "/index.php/rules-guidance/notices/26-14"
    ) == (
        "https://www.finra.org/rules-guidance/notices/26-14",
        "url:/rules-guidance/notices/26-14",
    )
    assert regulatory_monitor._finra_normalize_detail_link(
        "/node/382806"
    ) == ("https://www.finra.org/node/382806", "node:382806")
    assert regulatory_monitor._finra_normalize_detail_link(
        "https://evil.example/notice"
    ) == (None, None)


def test_finra_listing_rows_preserve_legacy_targets_and_unresolved_rows():
    """Scoped Drupal rows retain supported aliases and fail closed on bad links."""
    soup = BeautifulSoup(
        """
        <div class="view-content">
          <div class="views-row">
            <a href="/index.php/rules-guidance/notices/26-14">Legacy notice</a>
          </div>
          <div class="views-row">
            <a href="/node/382806">Numeric node</a>
          </div>
          <div class="views-row">
            <a href="https://evil.example/notices/26-15">Unsupported notice</a>
          </div>
        </div>
        """,
        "html.parser",
    )

    rows, unresolved = regulatory_monitor._extract_finra_listing_rows(soup)

    assert len(rows) == 3
    assert unresolved == 1
    assert rows[0]["node_identity"] == "url:/rules-guidance/notices/26-14"
    assert rows[1]["node_identity"] == "node:382806"
    assert rows[2]["detail_url"] is None


def _finra_live_empty_scoped_notice_view():
    return """
    <html><body>
      <div class="notice-by-date"></div>
      <div class="topic-navigation">
        <div class="view-content">
          <div class="views-row">
            <a href="/rules-guidance/notices/by-topic?topic=market">
              Market Topic
            </a>
          </div>
          <div class="views-row">
            <a href="/rules-guidance/notices/by-topic?topic=trading">
              Trading Topic
            </a>
          </div>
        </div>
      </div>
    </body></html>
    """


def test_finra_filtered_empty_scoped_view_ignores_unrelated_topic_rows():
    url = regulatory_monitor._finra_query_page_url(
        0,
        {
            "combine_1": "44",
            "field_core_content_type_tax_target_id": "5",
        },
    )

    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(url, _finra_live_empty_scoped_notice_view()),
        url,
        0,
        partition_label=(
            "pass-1/year=1983/type=-Election Notice"
        ),
    )

    assert result["complete"] is True
    assert result["page_declared"] == 0
    assert result["pager_mode"] == "explicit-zero"
    assert result["page_rows"] == []


def test_finra_scoped_notice_rows_win_over_unrelated_global_rows():
    soup = BeautifulSoup(
        """
        <html><body>
          <div class="notice-by-date">
            <div class="view-content">
              <div class="views-row">
                <a href="/rules-guidance/notices/26-15">
                  Regulatory Notice 26-15
                </a>
              </div>
            </div>
          </div>
          <div class="view-content">
            <div class="views-row">
              <a href="/rules-guidance/notices/by-topic?topic=market">
                Market Topic
              </a>
            </div>
          </div>
        </body></html>
        """,
        "html.parser",
    )

    rows, unresolved = regulatory_monitor._extract_finra_listing_rows(soup)

    assert unresolved == 0
    assert len(rows) == 1
    assert rows[0]["detail_url"] == (
        "https://www.finra.org/rules-guidance/notices/26-15"
    )
    assert all(
        "by-topic" not in link["href"]
        for link in rows[0]["raw_payload"]["links"]
    )


def test_finra_filtered_scoped_unsupported_only_row_fails_closed():
    url = regulatory_monitor._finra_query_page_url(
        0,
        {
            "combine_1": "44",
            "field_core_content_type_tax_target_id": "5",
        },
    )
    content = """
    <html><body>
      <div class="notice-by-date">
        <table><tbody><tr><td>
          <a href="https://evil.example/notices/83-01">
            Unsupported Notice
          </a>
        </td></tr></tbody></table>
      </div>
    </body></html>
    """

    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(url, content),
        url,
        0,
        partition_label=(
            "pass-1/year=1983/type=-Election Notice"
        ),
    )

    assert result["complete"] is False
    assert '"unresolved_count":1' in result["error"]


def test_finra_unfiltered_empty_scoped_view_remains_fail_closed():
    url = regulatory_monitor.FINRA_NOTICES_URL

    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(url, _finra_live_empty_scoped_notice_view()),
        url,
        0,
        partition_label="pass-1/unfiltered-reconciliation",
    )

    assert result["complete"] is False
    assert "pagination metadata" in result["error"]
    assert '"row_count":0' in result["error"]


def test_finra_scoped_zero_pager_evidence_tampering_fails_recomputation(
    monkeypatch,
):
    filters = _finra_filter_form(
        years=(("44", "1983"),),
        notice_types=(("5", "-Election Notice"),),
    )
    unfiltered_row = (
        "/rules-guidance/notices/83-01",
        "Regulatory Notice 83-01",
        "1983-01-02",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [unfiltered_row], filters=filters
        ),
        ("44", None, 0): _finra_live_empty_scoped_notice_view(),
    }
    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
    proof = deepcopy(result["pass_proof"])
    proof["partition_manifest"][0]["page_identities"][0][
        "pager_mode"
    ] = "inferred-single"

    errors = regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        proof,
        0,
    )

    assert any("pager evidence is invalid" in error for error in errors)


def test_finra_active_last_page_is_included_in_declared_total():
    """An active zero-based page 91 proves a 92-page listing."""
    soup = BeautifulSoup(
        """
        <nav aria-labelledby="pagination-heading"><ul class="pagination">
          <li class="page-item active"><span class="page-link">92</span></li>
          <li><a href="?page=90">Last</a></li>
        </ul></nav>
        """,
        "html.parser",
    )
    assert regulatory_monitor._extract_finra_declared_pages(soup) == 92


def test_finra_same_numeric_node_duplicate_coalesces_after_detail_proof(monkeypatch):
    """Repeated numeric-node rows coalesce after identical authoritative details."""
    rows = [
        _synthetic_finra_row(
            "https://www.finra.org/node/382806",
            "node:382806",
            title="Legacy duplicate listing",
        ),
        _synthetic_finra_row(
            "https://www.finra.org/node/382806",
            "node:382806",
        ),
    ]
    listing = _synthetic_finra_listing(rows)
    detail = _finra_detail_page_with_identity(
        "Notice 26-14",
        "2026-07-09",
        "Stable content.",
        canonical_url="https://www.finra.org/rules-guidance/notices/26-14",
        node_id="382806",
    )

    monkeypatch.setattr(
        regulatory_monitor, "_fetch_finra_listing_records",
        lambda *_args: listing,
    )
    monkeypatch.setattr(
        regulatory_monitor, "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": detail,
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )
    assert result.complete is True
    assert len(result) == 1
    assert result.coverage["unique_node_count"] == 1
    assert len(result.coverage["duplicate_ledger"]) == 1
    assert result.coverage["duplicate_ledger"][0]["raw_row_conflicts_with_first"] is True
    authority = result.coverage["date_resolution_ledger"]
    assert len(authority) == 1
    assert authority[0]["publication_date"] == "2026-07-09"
    assert authority[0]["conflicts"] == []
    assert regulatory_monitor._finra_duplicate_date_proof_facts(
        authority[0]["detail_date_proof"]
    ) == (
        "https://www.finra.org/rules-guidance/notices/26-14",
        "https://www.finra.org/node/382806",
        "2026-07-09",
    )
    assert authority[0]["detail_date_proof_hash"] == compute_hash(
        authority[0]["detail_date_proof"]
    )


def test_finra_same_numeric_node_conflicting_detail_fails_closed(monkeypatch):
    """A duplicate node whose authoritative content changes is unverifiable."""
    rows = [
        _synthetic_finra_row(
            "https://www.finra.org/rules-guidance/notices/26-14",
            "url:/rules-guidance/notices/26-14",
        ),
        _synthetic_finra_row(
            "https://www.finra.org/node/382806",
            "node:382806",
        ),
    ]
    listing = _synthetic_finra_listing(rows)
    details = {
        "https://www.finra.org/rules-guidance/notices/26-14":
            _finra_detail_page("Notice 26-14", "2026-07-09", "Version one."),
        "https://www.finra.org/node/382806":
            _finra_detail_page("Notice 26-14", "2026-07-09", "Version two."),
    }
    for key in details:
        details[key] = details[key].replace(
            "</body>", '<link rel="shortlink" href="/node/382806"></body>'
        )
    monkeypatch.setattr(
        regulatory_monitor, "_fetch_finra_listing_records",
        lambda *_args: listing,
    )
    monkeypatch.setattr(
        regulatory_monitor, "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": details[url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )
    assert result.complete is False
    assert "duplicate detail conflict" in result.error


def _fetch_finra_duplicate_date_case(
    monkeypatch,
    listing_dates,
    publication_date="2002-10-02",
):
    rows = [
        _synthetic_finra_row(
            "https://www.finra.org/rules-guidance/notices/fyi-10-2002",
            "url:/rules-guidance/notices/fyi-10-2002",
            title="FYI 10-2002",
        ),
        _synthetic_finra_row(
            "https://www.finra.org/node/126166",
            "node:126166",
            title="FYI 10-2002 (legacy)",
        ),
    ]
    for row, listing_date in zip(rows, listing_dates, strict=True):
        row["listing_date"] = listing_date
    listing = _synthetic_finra_listing(rows)
    detail = _finra_detail_page_with_identity(
        "FYI 10-2002",
        publication_date,
        "Stable content.",
        canonical_url=(
            "https://www.finra.org/rules-guidance/notices/fyi-10-2002"
        ),
        node_id="126166",
    )
    monkeypatch.setattr(
        regulatory_monitor, "_fetch_finra_listing_records",
        lambda *_args: listing,
    )
    monkeypatch.setattr(
        regulatory_monitor, "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": detail,
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )

    return regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )


def test_finra_authoritative_node_resolves_duplicate_listing_date_conflict(monkeypatch):
    """A stale row is safe only when a retained duplicate matches the detail date."""
    result = _fetch_finra_duplicate_date_case(
        monkeypatch,
        ("2002-10-01", "October 2, 2002"),
    )

    assert result.complete is True
    assert len(result) == 1
    duplicate = result.coverage["duplicate_ledger"][0]
    assert duplicate["resolves_listing_date_conflict"] is True
    resolution = result.coverage["date_resolution_ledger"]
    assert len(resolution) == 1
    assert resolution[0]["publication_date"] == "2002-10-02"
    assert resolution[0]["resolver"]["row_index"] == 1
    assert resolution[0]["conflicts"][0]["listing_date"] == "2002-10-01"


@pytest.mark.parametrize(
    "listing_dates",
    [
        ("2002-10-01", "2002-10-03"),
        ("2002-10-01", ""),
        ("", ""),
        ("2002-10-01", "not-a-date"),
    ],
    ids=(
        "two-conflicting-dates",
        "missing-duplicate-date",
        "all-dates-missing",
        "ambiguous-duplicate-date",
    ),
)
def test_finra_duplicate_dates_without_authoritative_match_fail_closed(
    monkeypatch,
    listing_dates,
):
    """Conflicting or absent duplicate dates cannot erase an unresolved conflict."""
    result = _fetch_finra_duplicate_date_case(monkeypatch, listing_dates)

    assert result.complete is False
    assert "listing/detail date conflict" in result.error
    assert result.coverage["date_resolution_ledger"] == []


def test_finra_matching_first_row_resolves_later_duplicate_conflict(monkeypatch):
    """Resolution is order-independent when the retained first row matches."""
    result = _fetch_finra_duplicate_date_case(
        monkeypatch,
        ("2002-10-02", "2002-10-03"),
    )

    assert result.complete is True
    duplicate = result.coverage["duplicate_ledger"][0]
    assert duplicate["listing_date_conflict"] is True
    assert duplicate["resolves_listing_date_conflict"] is False
    resolution = result.coverage["date_resolution_ledger"][0]
    assert resolution["resolver"]["row_index"] == 0
    assert resolution["conflicts"][0]["row_index"] == 1


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2002-10-02T12:00:00Z", "2002-10-02"),
        ("October 2, 2002", "2002-10-02"),
        ("10/2/2002", "2002-10-02"),
        ("2002-02-30", ""),
        ("October 2, 2002 and October 3, 2002", ""),
    ],
)
def test_finra_duplicate_date_normalization_is_unambiguous(value, expected):
    assert regulatory_monitor._normalize_finra_date(value) == expected


def test_finra_unresolved_listing_row_fails_closed(monkeypatch):
    """A scoped row without a supported detail target cannot complete."""
    listing = """
    <nav aria-labelledby="pagination-heading"><ul class="pagination">
      <li class="page-item active"><span class="page-link">1</span></li>
    </ul></nav>
    <table><tbody><tr><td><a href="https://evil.example/notices/26-14">
      Notice 26-14</a></td></tr></tbody></table>
    """
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing,
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor._fetch_finra_listing_pass(
        _FakeSession([]),
        None,
        "test-token",
    )
    assert result["complete"] is False
    assert "unresolved" in result["error"]


def test_finra_reserved_by_topic_route_is_not_a_detail_document():
    assert regulatory_monitor._finra_normalize_detail_link(
        "/rules-guidance/notices/by-topic"
    ) == (None, None)

    soup = BeautifulSoup(
        """
        <table><tbody><tr><td>
          <a href="/rules-guidance/notices/by-topic">Browse by Topic</a>
        </td></tr></tbody></table>
        """,
        "html.parser",
    )
    rows, unresolved = regulatory_monitor._extract_finra_listing_rows(soup)

    assert unresolved == 1
    assert len(rows) == 1
    assert rows[0]["detail_url"] is None
    assert rows[0]["raw_payload"]["links"] == []


def test_finra_reserved_navigation_anchor_is_ignored_beside_valid_detail():
    soup = BeautifulSoup(
        """
        <table><tbody><tr><td>
          <a href="/rules-guidance/notices/by-topic">Browse by Topic</a>
          <a href="/rules-guidance/notices/26-15">
            Regulatory Notice 26-15
          </a>
        </td></tr></tbody></table>
        """,
        "html.parser",
    )

    rows, unresolved = regulatory_monitor._extract_finra_listing_rows(soup)

    assert unresolved == 0
    assert len(rows) == 1
    assert rows[0]["detail_url"] == (
        "https://www.finra.org/rules-guidance/notices/26-15"
    )
    assert rows[0]["raw_payload"]["links"] == [
        {
            "href": "/rules-guidance/notices/26-15",
            "text": "Regulatory Notice 26-15",
        }
    ]


@pytest.mark.parametrize(
    "slug",
    [
        "information-notice-20260803",
        "election-notice-060826",
    ],
)
def test_finra_reserved_route_filter_does_not_overblock_notice_slugs(slug):
    canonical, identity = regulatory_monitor._finra_normalize_detail_link(
        f"/rules-guidance/notices/{slug}"
    )

    assert canonical == f"{regulatory_monitor.FINRA_NOTICES_URL}/{slug}"
    assert identity == f"url:/rules-guidance/notices/{slug}"


def test_finra_pass_proof_rejects_reserved_route_payload_injection():
    proof = _synthetic_pass_proofs(["FINRA 26-15"])[0]
    proof["page_row_payloads"][0][0]["links"].append({
        "href": "/rules-guidance/notices/by-topic",
        "text": "Browse by Topic",
    })
    proof["page_row_counts"] = [1]
    proof["page_row_digests"] = [
        _page_row_digest(proof["page_row_payloads"][0])
    ]

    errors = regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        proof,
        0,
    )

    assert any("production row evidence schema" in error for error in errors)


@pytest.mark.parametrize(
    "surface",
    ["entries", "fetched", "alias", "fallback"],
)
def test_finra_committed_state_rejects_reserved_route_identity_injection(
    surface,
):
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    coverage = source_state["coverage"]
    reserved = f"{regulatory_monitor.FINRA_NOTICES_URL}/by-topic"
    if surface == "entries":
        source_state["entries"][reserved] = "sha256:reserved"
        coverage["entry_count"] = len(source_state["entries"])
        coverage["entries_digest"] = regulatory_monitor._entries_digest(
            source_state["entries"]
        )
    elif surface == "fetched":
        coverage["fetched_entry_identities"] = sorted([
            *coverage["fetched_entry_identities"],
            reserved,
        ])
        coverage["fetched_entry_identity_digest"] = (
            regulatory_monitor._identity_digest(
                coverage["fetched_entry_identities"]
            )
        )
    elif surface == "alias":
        coverage["alias_ledger"].append({
            "old_identity": reserved,
            "canonical_identity": next(iter(source_state["entries"])),
            "source_hash": "sha256:reserved",
            "evidence": {
                "reason": "forged",
                "source_hash_at_migration": "sha256:reserved",
                "canonical_hash_at_migration": "sha256:reserved",
                "content_updates": [],
            },
        })
        coverage["alias_ledger_digest"] = (
            regulatory_monitor._alias_ledger_digest(
                coverage["alias_ledger"]
            )
        )
    else:
        source_state["fallback_urls"] = {
            reserved: "https://www.finra.org/node/382806"
        }

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any("reserved notice route" in error for error in errors)


def _finra_filter_form(years=(("1", "2026"),), notice_types=(("1", "Regulatory Notice"),)):
    year_options = '<option value="All">- Any -</option>' + "".join(
        f'<option value="{value}">{label}</option>'
        for value, label in years
    )
    type_options = '<option value="All">- Any -</option>' + "".join(
        f'<option value="{value}">{label}</option>'
        for value, label in notice_types
    )
    return (
        '<select name="combine_1">'
        f"{year_options}</select>"
        '<select name="field_core_content_type_tax_target_id">'
        f"{type_options}</select>"
    )


def _finra_filtered_listing_page(
    page,
    total_pages,
    records,
    *,
    filters="",
):
    return _finra_listing_page(page, total_pages, records).replace(
        "<body>", f"<body>{filters}", 1
    )


def test_finra_filter_option_discovery_is_dynamic_and_deterministic():
    soup = BeautifulSoup(
        _finra_filter_form(
            years=(("7", "2024"), ("3", "2026"), ("5", "2025")),
            notice_types=(("9", "Special Notice"), ("2", "Regulatory Notice")),
        ),
        "html.parser",
    )

    assert regulatory_monitor._extract_finra_filter_manifest(soup) == {
        "year_field": "combine_1",
        "years": [
            {"label": "2024", "value": "7"},
            {"label": "2025", "value": "5"},
            {"label": "2026", "value": "3"},
        ],
        "notice_type_field": "field_core_content_type_tax_target_id",
        "notice_types": [
            {"label": "Regulatory Notice", "value": "2"},
            {"label": "Special Notice", "value": "9"},
        ],
    }


def test_finra_filter_option_discovery_accepts_exact_live_select_markup():
    markup = """
    <select data-drupal-selector="edit-combine-1" id="edit-combine-1"
      name="combine_1" class="form-select form-control"
      aria-label="Filter options">
      <option value="All" selected="selected">- Any -</option>
      <option value="1">2026</option>
      <option value="2">2025</option>
    </select>
    <select data-drupal-selector="edit-field-core-content-type-tax-target-id"
      id="edit-field-core-content-type-tax-target-id"
      name="field_core_content_type_tax_target_id"
      class="form-select form-control" aria-label="Filter options">
      <option value="All" selected="selected">- Any -</option>
      <option value="1">-Trade Reporting Notice</option>
      <option value="2">-Regulatory Notice</option>
    </select>
    """

    assert regulatory_monitor._extract_finra_filter_manifest(
        BeautifulSoup(markup, "html.parser")
    ) == {
        "year_field": "combine_1",
        "years": [
            {"label": "2025", "value": "2"},
            {"label": "2026", "value": "1"},
        ],
        "notice_type_field": "field_core_content_type_tax_target_id",
        "notice_types": [
            {"label": "-Regulatory Notice", "value": "2"},
            {"label": "-Trade Reporting Notice", "value": "1"},
        ],
    }


@pytest.mark.parametrize(
    ("sentinel_value", "sentinel_label"),
    [
        ("All", "- Any -"),
        ("  aLl  ", " \u00a0-\u00a0 aNy \u00a0-\u00a0 "),
        ("ALL", "\u2014 ANY \u2014"),
        ("all", "\u2011Any\u2011"),
        ("Ａｌｌ", "\uff0d Any \uff0d"),
    ],
)
def test_finra_filter_sentinel_accepts_normalized_live_variants(
    sentinel_value,
    sentinel_label,
):
    markup = (
        '<select name="combine_1">'
        f'<option value="{sentinel_value}">{sentinel_label}</option>'
        '<option value="1">2026</option></select>'
        '<select name="field_core_content_type_tax_target_id">'
        f'<option value="{sentinel_value}">{sentinel_label}</option>'
        '<option value="2">-Regulatory Notice</option></select>'
    )

    manifest = regulatory_monitor._extract_finra_filter_manifest(
        BeautifulSoup(markup, "html.parser")
    )

    assert manifest["years"] == [{"label": "2026", "value": "1"}]
    assert manifest["notice_types"] == [
        {"label": "-Regulatory Notice", "value": "2"}
    ]


@pytest.mark.parametrize(
    "markup",
    [
        _finra_filter_form(years=(("1", "2026"), ("2", "2026"))),
        _finra_filter_form(years=(("1", "2026"), ("1", "2025"))),
        _finra_filter_form(years=(("1", "FY 2026"),)),
        _finra_filter_form(notice_types=(("1", "Regulatory Notice"), ("2", "Regulatory Notice"))),
        _finra_filter_form(notice_types=(("1", "Regulatory Notice"), ("1", "Special Notice"))),
        _finra_filter_form(notice_types=(("", "Regulatory Notice"),)),
        '<select name="combine_1"><option value="All">- Any -</option>'
        '<option value="1">2026</option></select>',
        _finra_filter_form(years=(("All", "2026"),)),
        _finra_filter_form(years=(("1", "- Any -"),)),
        _finra_filter_form(years=(("All", "Any"),)),
    ],
)
def test_finra_filter_option_discovery_rejects_malformed_or_duplicate_maps(markup):
    with pytest.raises(ValueError, match="FINRA filter"):
        regulatory_monitor._extract_finra_filter_manifest(
            BeautifulSoup(markup, "html.parser")
        )


def _run_partitioned_finra_pass(
    monkeypatch,
    pages,
    *,
    legacy_fixture=False,
    prior_filter_manifest=None,
    subdivide_year_values=None,
):
    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(_finra_request_base(url))
        parsed = urlparse(_finra_request_base(url))
        query = parse_qs(parsed.query, keep_blank_values=True)
        page = int(query.get("page", ["0"])[0])
        key = (
            query.get("combine_1", [None])[0],
            query.get("field_core_content_type_tax_target_id", [None])[0],
            page,
        )
        content = pages[key]
        return {
            "status_code": 200,
            "content": content,
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "_fetch_finra_page", fake_fetch_page)
    result = regulatory_monitor._fetch_finra_listing_pass(
        _FakeSession([], allow_legacy_finra=legacy_fixture),
        None,
        "1-test",
        prior_filter_manifest=prior_filter_manifest,
        subdivide_year_values=subdivide_year_values,
    )
    return result, requested


def test_finra_partitioned_pass_uses_stable_one_page_year_shards(monkeypatch):
    filters = _finra_filter_form(
        years=(("1", "2026"), ("2", "2025")),
        notice_types=(("1", "Regulatory Notice"), ("2", "Special Notice")),
    )
    row_2026 = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    row_2025 = (
        "/rules-guidance/notices/25-01",
        "Regulatory Notice 25-01",
        "2025-01-02",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row_2026, row_2025], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 1, [row_2026]),
        ("2", None, 0): _finra_listing_page(0, 1, [row_2025]),
    }

    result, requested = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    assert [row["title"] for row in result["rows"]] == [
        "Regulatory Notice 25-01",
        "Regulatory Notice 26-15",
    ]
    assert result["pass_proof"]["filter_manifest"]["years"][0]["value"] == "2"
    assert [
        shard["query"] for shard in result["pass_proof"]["partition_manifest"]
    ] == [{"combine_1": "2"}, {"combine_1": "1"}]
    assert not any("field_core_content_type_tax_target_id" in url for url in requested)


def test_finra_partitioned_pass_subdivides_multi_page_year_by_every_type(monkeypatch):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    regulatory_row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    special_row = (
        "/rules-guidance/notices/special-notice-26-1",
        "Special Notice 26-1",
        "2026-06-01",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [regulatory_row, special_row], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 2, [regulatory_row]),
        ("1", "3", 0): _finra_listing_page(0, 1, [regulatory_row]),
        ("1", "7", 0): _finra_listing_page(0, 1, [special_row]),
    }

    result, requested = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    assert {row["title"] for row in result["rows"]} == {
        "Regulatory Notice 26-15",
        "Special Notice 26-1",
    }
    assert {
        tuple(sorted(shard["query"].items()))
        for shard in result["pass_proof"]["partition_manifest"]
    } == {
        (
            ("combine_1", "1"),
            ("field_core_content_type_tax_target_id", "3"),
        ),
        (
            ("combine_1", "1"),
            ("field_core_content_type_tax_target_id", "7"),
        ),
    }
    assert len(requested) == 4


def test_finra_partitioned_pass_proof_binds_unclassified_year_page_zero_row(
    monkeypatch,
):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    present = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omitted = (
        "/rules-guidance/notices/new-notice-26-1",
        "New Notice 26-1",
        "2026-07-01",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [present], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 2, [present, omitted]),
        ("1", "3", 0): _finra_listing_page(0, 1, [present]),
        ("1", "7", 0): (
            "<html><body><div class=\"view-empty\">No regulatory notices</div>"
            "</body></html>"
        ),
    }

    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    evidence = result["pass_proof"]["unclassified_evidence"]
    assert evidence["raw_row_count"] == 1
    assert len(evidence["observations"]) == 1
    assert evidence["observations"][0]["source"] == "year-page-zero"
    assert evidence["observations"][0]["year"] == {
        "label": "2026",
        "value": "1",
    }
    assert evidence["observations"][0]["page_numbers"] == [0]
    assert evidence["observations"][0]["page_identities"][0][
        "pager_mode"
    ] == "explicit"
    assert {
        row["title"] for row in result["rows"]
    } == {"Regulatory Notice 26-15", "New Notice 26-1"}


def test_finra_identical_global_and_year_unclassified_overlap_is_counted_once(
    monkeypatch,
):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    present = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omitted = (
        "/rules-guidance/notices/new-notice-26-1",
        "New Notice 26-1",
        "2026-07-01",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [present, omitted], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 2, [present, omitted]),
        ("1", "3", 0): _finra_listing_page(0, 1, [present]),
        ("1", "7", 0): (
            "<html><body><div class=\"view-empty\">No regulatory notices</div>"
            "</body></html>"
        ),
    }

    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    evidence = result["pass_proof"]["unclassified_evidence"]
    assert {item["source"] for item in evidence["observations"]} == {
        "global-unfiltered",
        "year-page-zero",
    }
    assert evidence["raw_row_count"] == 1
    assert len(evidence["row_payloads"]) == 1


def test_finra_partition_proof_rejects_missing_type_shard_with_equal_row_union(
    monkeypatch,
):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 2, [row]),
        ("1", "3", 0): _finra_listing_page(0, 1, [row]),
        ("1", "7", 0): _finra_listing_page(0, 1, [row]),
    }
    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
    proof = deepcopy(result["pass_proof"])
    proof["partition_manifest"].pop()

    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    coverage = source_state["coverage"]
    coverage["schema_version"] = (
        regulatory_monitor.FINRA_DETERMINISTIC_COVERAGE_SCHEMA_VERSION
    )
    coverage["listing_mode"] = "deterministic-year-type-partitions"
    second_proof = deepcopy(proof)
    second_proof["token"] = "pass-2"
    coverage["pass_proofs"] = [proof, second_proof]
    for key in (
        "declared_pages",
        "pages_fetched",
        "page_numbers",
        "page_identities",
        "raw_row_count",
        "resolved_row_count",
        "unresolved_row_count",
        "unique_node_count",
    ):
        coverage[key] = deepcopy(proof[key])
    coverage["listing_record_count"] = proof["resolved_row_count"]
    for key in regulatory_monitor.FINRA_DETERMINISTIC_PROOF_FIELDS:
        coverage[key] = deepcopy(proof[key])

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any("topology" in error for error in errors)


def test_finra_partition_proof_rejects_missing_discovered_year_with_equal_union(
    monkeypatch,
):
    filters = _finra_filter_form(
        years=(("1", "2026"), ("2", "2025")),
        notice_types=(("3", "Regulatory Notice"),),
    )
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 1, [row]),
        ("2", None, 0): _finra_listing_page(0, 1, [row]),
    }
    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
    proof = deepcopy(result["pass_proof"])
    proof["partition_manifest"] = proof["partition_manifest"][:1]
    proof["year_observations"] = proof["year_observations"][:1]

    errors = regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        proof,
        0,
    )

    assert any("discovered year" in error for error in errors)


def test_finra_partition_listing_budget_fails_before_extra_request(
    monkeypatch,
):
    monkeypatch.setattr(regulatory_monitor, "FINRA_LISTING_REQUEST_BUDGET", 3)
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 2, [row]),
        ("1", "3", 0): _finra_listing_page(0, 2, [row]),
    }

    result, requested = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is False
    assert "budget exceeded" in result["error"]
    assert len(requested) == 3


def _finra_observed_44_year_topology_pages():
    years = tuple(
        (str(2027 - year), str(year))
        for year in range(1983, 2027)
    )
    notice_types = (
        ("1", "-Trade Reporting Notice"),
        ("2", "-Regulatory Notice"),
        ("3", "-Notice to Members"),
        ("4", "-Information Notice"),
        ("5", "-Election Notice"),
        ("6", "-Special Notice"),
        ("7", "-Request for Comment"),
    )
    filters = _finra_filter_form(
        years=years,
        notice_types=notice_types,
    )
    rows_by_value = {}
    for value, year_label in years:
        suffix = int(year_label) % 100
        rows_by_value[value] = (
            f"/rules-guidance/notices/{suffix:02d}-01",
            f"Regulatory Notice {suffix:02d}-01",
            f"{year_label}-01-02",
        )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0,
            1,
            list(rows_by_value.values()),
            filters=filters,
        ),
    }
    zero_page = (
        "<html><body><div class=\"view-empty\">No regulatory notices</div>"
        "</body></html>"
    )
    for value, _year_label in years:
        row = rows_by_value[value]
        pages[(value, None, 0)] = _finra_listing_page(0, 2, [row])
        for type_value, _type_label in notice_types:
            if type_value == "1":
                pages[(value, type_value, 0)] = (
                    _finra_live_shaped_filtered_rows()
                    .replace("/rules-guidance/notices/26-16", row[0])
                    .replace("Regulatory Notice 26-16", row[1])
                    .replace("2026-08-26", row[2])
                )
            else:
                pages[(value, type_value, 0)] = zero_page
    return pages


def test_finra_live_44_year_type_cross_product_requires_more_than_220_requests(
    monkeypatch,
):
    assert regulatory_monitor.FINRA_LISTING_REQUEST_BUDGET == 420
    pages = _finra_observed_44_year_topology_pages()
    monkeypatch.setattr(
        regulatory_monitor,
        "FINRA_LISTING_REQUEST_BUDGET",
        220,
    )

    rejected, rejected_requests = _run_partitioned_finra_pass(
        monkeypatch,
        pages,
    )

    assert rejected["complete"] is False
    assert "budget exceeded" in rejected["error"]
    assert len(rejected_requests) == 220

    monkeypatch.setattr(
        regulatory_monitor,
        "FINRA_LISTING_REQUEST_BUDGET",
        420,
    )
    completed, completed_requests = _run_partitioned_finra_pass(
        monkeypatch,
        pages,
    )

    assert completed["complete"] is True
    assert len(completed_requests) == 353


def test_finra_listing_budget_rejects_request_421(monkeypatch):
    calls = []

    def fake_fetch(url, _session, **_kwargs):
        calls.append(url)
        return {
            "status_code": 200,
            "content": "",
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "_fetch_finra_page", fake_fetch)
    budget = {"used": 0, "limit": 420, "last_completed": "fixture"}
    for request_number in range(1, 421):
        result = regulatory_monitor._fetch_finra_listing_page_with_budget(
            regulatory_monitor.FINRA_NOTICES_URL,
            _FakeSession([], allow_legacy_finra=False),
            budget,
            progress=f"fixture/request={request_number}",
        )
        assert result["status_code"] == 200

    rejected = regulatory_monitor._fetch_finra_listing_page_with_budget(
        regulatory_monitor.FINRA_NOTICES_URL,
        _FakeSession([], allow_legacy_finra=False),
        budget,
        progress="fixture/request=421",
    )

    assert rejected["status_code"] == 0
    assert "budget exceeded (420/420)" in rejected["error"]
    assert len(calls) == 420


def test_finra_listing_retries_consume_the_same_pass_budget(monkeypatch):
    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", lambda _seconds: None)
    calls = []

    def rate_limited(url, _session, **_kwargs):
        calls.append(url)
        return {
            "status_code": 429,
            "content": "",
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": "rate limited",
            "retry_after": 0,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", rate_limited)
    budget = {"used": 1, "limit": 2}
    result = regulatory_monitor._fetch_finra_page(
        regulatory_monitor.FINRA_NOTICES_URL,
        _FakeSession([], allow_legacy_finra=False),
        min_interval_seconds=0,
        request_budget=budget,
        first_attempt_reserved=True,
    )

    assert result["status_code"] == 0
    assert "budget exceeded" in result["error"]
    assert budget == {"used": 2, "limit": 2}
    assert len(calls) == 2


def test_finra_partitioned_pass_accepts_explicit_zero_result_type_shard(
    monkeypatch,
):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    zero_page = (
        "<html><body><div class=\"view-empty\">No regulatory notices</div>"
        "</body></html>"
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 2, [row]),
        ("1", "3", 0): _finra_listing_page(0, 1, [row]),
        ("1", "7", 0): zero_page,
    }

    result, requested = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    assert len(requested) == 4
    zero_shard = next(
        shard
        for shard in result["pass_proof"]["partition_manifest"]
        if shard["notice_type"]["value"] == "7"
    )
    assert zero_shard["declared_pages"] == 0
    assert zero_shard["page_identities"] == [
        {
            "requested": 0,
            "final": 0,
            "active": 0,
            "pager_mode": "explicit-zero",
        }
    ]
    assert zero_shard["row_payloads"] == []


def test_finra_partition_pass_rejects_persisted_filter_shrinkage(monkeypatch):
    prior = {
        "year_field": "combine_1",
        "years": [
            {"label": "2025", "value": "2"},
            {"label": "2026", "value": "1"},
        ],
        "notice_type_field": "field_core_content_type_tax_target_id",
        "notice_types": [
            {"label": "Regulatory Notice", "value": "3"},
            {"label": "Special Notice", "value": "7"},
        ],
    }
    filters = _finra_filter_form(
        years=(("2", "2025"),),
        notice_types=(("3", "Regulatory Notice"),),
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [], filters=filters
        ),
    }

    result, requested = _run_partitioned_finra_pass(
        monkeypatch,
        pages,
        prior_filter_manifest=prior,
    )

    assert result["complete"] is False
    assert "current year is absent" in result["error"]
    assert len(requested) == 1


def test_finra_partitioned_pass_deduplicates_identical_topology_overlap(monkeypatch):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(0, 1, [row], filters=filters),
        ("1", None, 0): _finra_listing_page(0, 2, [row]),
        ("1", "3", 0): _finra_listing_page(0, 1, [row]),
        ("1", "7", 0): _finra_listing_page(0, 1, [row]),
    }

    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    assert len(result["rows"]) == 1
    assert result["pass_proof"]["raw_row_count"] == 1


def _finra_semantic_25_15_pages(
    *,
    second_href="/rules-guidance/notices/25-15",
    second_title="Regulatory Notice 25-15",
    second_date="2025-09-15",
):
    filters = _finra_filter_form(
        years=(("2", "2025"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    canonical = (
        "/rules-guidance/notices/25-15",
        "Regulatory Notice 25-15",
        "2025-09-15",
    )
    legacy = (
        "/index.php/rules-guidance/notices/25-15",
        "Regulatory Notice 25-15",
        "2025-09-15",
    )
    return {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [canonical], filters=filters
        ),
        ("2", None, 0): _finra_listing_page(0, 2, [canonical]),
        ("2", "3", 0): _finra_listing_page(0, 1, [legacy]),
        ("2", "7", 0): _finra_listing_page(
            0,
            1,
            [(second_href, second_title, second_date)],
        ),
    }


def test_finra_semantic_rows_dedupe_canonical_and_index_php_hrefs(monkeypatch):
    result, _ = _run_partitioned_finra_pass(
        monkeypatch,
        _finra_semantic_25_15_pages(),
    )

    assert result["complete"] is True
    assert len(result["rows"]) == 1
    shard_payloads = result["pass_proof"]["partition_manifest"]
    assert shard_payloads[0]["row_payloads"] != shard_payloads[1][
        "row_payloads"
    ]
    assert shard_payloads[0]["semantic_row_payloads"] == shard_payloads[1][
        "semantic_row_payloads"
    ]


@pytest.mark.parametrize(
    ("title", "date"),
    [
        ("Changed Notice 25-15", "2025-09-15"),
        ("Regulatory Notice 25-15", "2025-09-16"),
    ],
)
def test_finra_semantic_rows_still_conflict_on_text_or_date(
    monkeypatch,
    title,
    date,
):
    result, _ = _run_partitioned_finra_pass(
        monkeypatch,
        _finra_semantic_25_15_pages(
            second_title=title,
            second_date=date,
        ),
    )

    assert result["complete"] is False
    assert "conflicting partition evidence" in result["error"]


def test_finra_semantic_rows_conflict_on_different_canonical_targets(
    monkeypatch,
):
    result, _ = _run_partitioned_finra_pass(
        monkeypatch,
        _finra_semantic_25_15_pages(
            second_href="/rules-guidance/notices/25-14",
        ),
    )

    assert result["complete"] is False
    assert "canonical targets" in result["error"]


def test_finra_semantic_digest_tampering_fails_recomputation(monkeypatch):
    result, _ = _run_partitioned_finra_pass(
        monkeypatch,
        _finra_semantic_25_15_pages(),
    )
    proof = deepcopy(result["pass_proof"])
    proof["partition_manifest"][0][
        "semantic_row_evidence_digest"
    ] = "sha256:forged"

    errors = regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        proof,
        0,
    )

    assert any("semantic row evidence is invalid" in error for error in errors)


def test_finra_raw_payload_tampering_fails_with_semantic_digest_unchanged(
    monkeypatch,
):
    result, _ = _run_partitioned_finra_pass(
        monkeypatch,
        _finra_semantic_25_15_pages(),
    )
    proof = deepcopy(result["pass_proof"])
    proof["partition_manifest"][0]["row_payloads"][0]["links"][0][
        "href"
    ] = "/rules-guidance/notices/25-99"

    errors = regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        proof,
        0,
    )

    assert errors


def test_finra_partitioned_pass_rejects_conflicting_overlap(monkeypatch):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    first = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    conflicting = (
        "/rules-guidance/notices/26-15",
        "Conflicting title",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(0, 1, [first], filters=filters),
        ("1", None, 0): _finra_listing_page(0, 2, [first]),
        ("1", "3", 0): _finra_listing_page(0, 1, [first]),
        ("1", "7", 0): _finra_listing_page(0, 1, [conflicting]),
    }

    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is False
    assert "conflicting partition evidence" in result["error"]


def test_finra_partitioned_pass_reconciliation_proves_unclassified_omission(
    monkeypatch,
):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"),),
    )
    present = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omitted = (
        "/rules-guidance/notices/26-14",
        "Regulatory Notice 26-14",
        "2026-07-09",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [present, omitted], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 1, [present]),
    }

    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    assert result["pass_proof"]["unclassified_evidence"]["row_payloads"] == [
        result["rows"][0]["raw_payload"]
    ] or result["pass_proof"]["unclassified_evidence"]["row_payloads"] == [
        result["rows"][1]["raw_payload"]
    ]


def test_finra_unfiltered_reconciliation_observes_page_one_taxonomy_omission(
    monkeypatch,
):
    filters = _finra_filter_form(
        years=(("1", "2026"),),
        notice_types=(("3", "Regulatory Notice"),),
    )
    present = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omitted = (
        "/rules-guidance/notices/information-notice-20260701",
        "Information Notice 7/1/26",
        "2026-07-01",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 2, [present], filters=filters
        ),
        (None, None, 1): _finra_listing_page(1, 2, [omitted]),
        ("1", None, 0): _finra_listing_page(0, 1, [present]),
    }

    result, requested = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    reconciliation = result["pass_proof"]["unfiltered_reconciliation"]
    assert reconciliation["pages_observed"] == 2
    assert reconciliation["page_numbers"] == [0, 1]
    assert reconciliation["page_row_counts"] == [1, 1]
    assert result["pass_proof"]["unclassified_evidence"]["raw_row_count"] == 1
    assert any("page=1" in url for url in requested)


def test_finra_partition_manifests_are_recomputed_and_cross_pass_bound(monkeypatch):
    filters = _finra_filter_form()
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(0, 1, [row], filters=filters),
        ("1", None, 0): _finra_listing_page(0, 1, [row]),
    }
    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
    first = result["pass_proof"]
    second = deepcopy(first)
    second["token"] = "pass-2"

    assert regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        first,
        0,
    ) == []
    assert regulatory_monitor._compare_finra_listing_pass_proofs(
        first,
        second,
    ) is None

    second["filter_manifest"]["years"][0]["value"] = "changed"
    assert "filter manifest" in (
        regulatory_monitor._compare_finra_listing_pass_proofs(first, second)
        or ""
    )

    forged = deepcopy(first)
    forged["partition_manifest"][0]["row_payloads"][0]["text"] = "forged"
    assert regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
        0,
    )


def _finra_pass_with_observation_and_partition_rows(
    monkeypatch,
    observation_rows,
    partition_rows,
):
    filters = _finra_filter_form()
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0,
            1,
            observation_rows,
            filters=filters,
        ),
        ("1", None, 0): _finra_listing_page(
            0,
            1,
            partition_rows,
        ),
    }
    return _run_partitioned_finra_pass(monkeypatch, pages)[0]


def test_finra_different_unfiltered_subsets_of_same_partition_reach_consensus(
    monkeypatch,
):
    first_row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    second_row = (
        "/rules-guidance/notices/26-14",
        "Regulatory Notice 26-14",
        "2026-07-09",
    )
    first = _finra_pass_with_observation_and_partition_rows(
        monkeypatch,
        [first_row],
        [first_row, second_row],
    )
    second = _finra_pass_with_observation_and_partition_rows(
        monkeypatch,
        [second_row],
        [first_row, second_row],
    )
    second["pass_proof"]["token"] = "pass-2"
    results = iter([first, second])
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        lambda *_args, **_kwargs: next(results),
    )

    consensus = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([], allow_legacy_finra=False),
        None,
    )

    assert consensus["complete"] is True
    assert consensus["pass_proofs"][0][
        "unfiltered_reconciliation"
    ] != consensus["pass_proofs"][1]["unfiltered_reconciliation"]
    assert {
        row["title"] for row in consensus["rows"]
    } == {"Regulatory Notice 26-14", "Regulatory Notice 26-15"}


def test_finra_different_unfiltered_views_with_same_unclassified_reach_consensus(
    monkeypatch,
):
    first_row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    second_row = (
        "/rules-guidance/notices/26-14",
        "Regulatory Notice 26-14",
        "2026-07-09",
    )
    omitted = (
        "/rules-guidance/notices/information-notice-20260701",
        "Information Notice 7/1/26",
        "2026-07-01",
    )
    partition_rows = [first_row, second_row]
    first = _finra_pass_with_observation_and_partition_rows(
        monkeypatch,
        [first_row, omitted],
        partition_rows,
    )
    second = _finra_pass_with_observation_and_partition_rows(
        monkeypatch,
        [second_row, omitted],
        partition_rows,
    )
    second["pass_proof"]["token"] = "pass-2"

    assert first["pass_proof"]["unclassified_evidence"] == second[
        "pass_proof"
    ]["unclassified_evidence"]
    assert regulatory_monitor._compare_finra_listing_pass_proofs(
        first["pass_proof"],
        second["pass_proof"],
    ) is None


def test_finra_different_derived_unclassified_evidence_fails_consensus(
    monkeypatch,
):
    classified = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omitted_a = (
        "/rules-guidance/notices/information-notice-20260701",
        "Information Notice A",
        "2026-07-01",
    )
    omitted_b = (
        "/rules-guidance/notices/information-notice-20260702",
        "Information Notice B",
        "2026-07-02",
    )
    first = _finra_pass_with_observation_and_partition_rows(
        monkeypatch,
        [classified, omitted_a],
        [classified],
    )
    second = _finra_pass_with_observation_and_partition_rows(
        monkeypatch,
        [classified, omitted_b],
        [classified],
    )

    mismatch = regulatory_monitor._compare_finra_listing_pass_proofs(
        first["pass_proof"],
        second["pass_proof"],
    )

    assert "unclassified evidence" in (mismatch or "")


def test_finra_tampered_per_pass_reconciliation_fails_state_validation(
    monkeypatch,
):
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    result = _finra_pass_with_observation_and_partition_rows(
        monkeypatch,
        [row],
        [row],
    )
    proof = deepcopy(result["pass_proof"])
    proof["unfiltered_reconciliation"]["request_identities"][0] = [
        ["combine_1", "forged"]
    ]
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    coverage = source_state["coverage"]
    coverage["schema_version"] = (
        regulatory_monitor.FINRA_DETERMINISTIC_COVERAGE_SCHEMA_VERSION
    )
    coverage["listing_mode"] = "deterministic-year-type-partitions"
    second_proof = deepcopy(proof)
    second_proof["token"] = "pass-2"
    coverage["pass_proofs"] = [proof, second_proof]
    for key in (
        "declared_pages",
        "pages_fetched",
        "page_numbers",
        "page_identities",
        "raw_row_count",
        "resolved_row_count",
        "unresolved_row_count",
        "unique_node_count",
    ):
        coverage[key] = deepcopy(proof[key])
    coverage["listing_record_count"] = proof["resolved_row_count"]
    for key in regulatory_monitor.FINRA_DETERMINISTIC_PROOF_FIELDS:
        coverage[key] = deepcopy(proof[key])

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any(
        "bounded unfiltered reconciliation is invalid" in error
        for error in errors
    )


def test_finra_unclassified_evidence_must_be_stable_across_passes(monkeypatch):
    filters = _finra_filter_form()
    classified = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omitted_a = (
        "/rules-guidance/notices/information-notice-20260701",
        "Information Notice A",
        "2026-07-01",
    )
    omitted_b = (
        "/rules-guidance/notices/information-notice-20260702",
        "Information Notice B",
        "2026-07-02",
    )

    def proof_for(omitted):
        pages = {
            (None, None, 0): _finra_filtered_listing_page(
                0, 2, [classified], filters=filters
            ),
            (None, None, 1): _finra_listing_page(1, 2, [omitted]),
            ("1", None, 0): _finra_listing_page(0, 1, [classified]),
        }
        result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
        return result["pass_proof"]

    first = proof_for(omitted_a)
    second = proof_for(omitted_b)

    assert "unclassified evidence" in (
        regulatory_monitor._compare_finra_listing_pass_proofs(first, second)
        or ""
    )


def test_finra_year_unclassified_evidence_must_be_stable_across_passes(
    monkeypatch,
):
    filters = _finra_filter_form(
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    classified = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omissions = [
        (
            "/rules-guidance/notices/26-14",
            "Regulatory Notice 26-14",
            "2026-07-09",
        ),
        (
            "/rules-guidance/notices/26-13",
            "Regulatory Notice 26-13",
            "2026-06-30",
        ),
    ]
    proofs = []
    for omitted in omissions:
        pages = {
            (None, None, 0): _finra_filtered_listing_page(
                0, 1, [classified], filters=filters
            ),
            ("1", None, 0): _finra_listing_page(
                0, 2, [classified, omitted]
            ),
            ("1", "3", 0): _finra_listing_page(0, 1, [classified]),
            ("1", "7", 0): (
                "<html><body><div class=\"view-empty\">"
                "No regulatory notices</div></body></html>"
            ),
        }
        result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
        proofs.append(result["pass_proof"])

    mismatch = regulatory_monitor._compare_finra_listing_pass_proofs(
        proofs[0],
        proofs[1],
    )

    assert "unclassified evidence" in (mismatch or "")
    assert "year" in (mismatch or "")


@pytest.mark.parametrize("tamper", ["year", "source", "digest"])
def test_finra_year_unclassified_provenance_tampering_fails_validation(
    monkeypatch,
    tamper,
):
    filters = _finra_filter_form(
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    present = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omitted = (
        "/rules-guidance/notices/26-14",
        "Regulatory Notice 26-14",
        "2026-07-09",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [present], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 2, [present, omitted]),
        ("1", "3", 0): _finra_listing_page(0, 1, [present]),
        ("1", "7", 0): (
            "<html><body><div class=\"view-empty\">No regulatory notices</div>"
            "</body></html>"
        ),
    }
    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
    proof = deepcopy(result["pass_proof"])
    observation = proof["unclassified_evidence"]["observations"][0]
    if tamper == "year":
        observation["year"]["value"] = "forged"
    elif tamper == "source":
        observation["source"] = "forged"
    else:
        observation["row_evidence_digest"] = "sha256:forged"

    errors = regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        proof,
        0,
    )

    assert any(
        "unclassified" in error and (
            "year=2026" in error or "provenance" in error
        )
        for error in errors
    )


def test_finra_unstable_unclassified_evidence_fails_closed_after_three_passes(
    monkeypatch,
):
    filters = _finra_filter_form()
    classified = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    omitted_rows = [
        (
            f"/rules-guidance/notices/information-notice-2026070{index}",
            f"Information Notice {index}",
            f"2026-07-0{index}",
        )
        for index in (1, 2, 3)
    ]
    results = []
    for index, omitted in enumerate(omitted_rows, start=1):
        pages = {
            (None, None, 0): _finra_filtered_listing_page(
                0, 2, [classified], filters=filters
            ),
            (None, None, 1): _finra_listing_page(1, 2, [omitted]),
            ("1", None, 0): _finra_listing_page(0, 1, [classified]),
        }
        result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
        result["pass_proof"]["token"] = f"pass-{index}"
        results.append(result)

    result_iterator = iter(results)
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        lambda *_args, **_kwargs: next(result_iterator),
    )

    result = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([], allow_legacy_finra=False),
        None,
    )

    assert result["complete"] is False
    assert "unclassified evidence" in result["error"]


def test_finra_single_page_instability_subdivides_pass_three_then_fails_closed(
    monkeypatch,
):
    filters = _finra_filter_form(
        notice_types=(("3", "Regulatory Notice"), ("7", "Special Notice")),
    )
    row_a = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    row_b = (
        "/rules-guidance/notices/26-14",
        "Regulatory Notice 26-14",
        "2026-07-09",
    )

    def direct_result(row):
        pages = {
            (None, None, 0): _finra_filtered_listing_page(
                0, 1, [row], filters=filters
            ),
            ("1", None, 0): _finra_listing_page(0, 1, [row]),
        }
        return _run_partitioned_finra_pass(monkeypatch, pages)[0]

    subdivided_pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row_b], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 1, [row_b]),
        ("1", "3", 0): _finra_listing_page(0, 1, [row_b]),
        ("1", "7", 0): (
            "<html><body><div class=\"view-empty\">No regulatory notices</div>"
            "</body></html>"
        ),
    }
    first = direct_result(row_a)
    second = direct_result(row_b)
    stable, _ = _run_partitioned_finra_pass(
        monkeypatch,
        subdivided_pages,
        subdivide_year_values=frozenset({"1"}),
    )
    results = iter([first, second, stable])
    subdivisions = []

    def fake_pass(*_args, **kwargs):
        subdivisions.append(kwargs.get("subdivide_year_values", frozenset()))
        return next(results)

    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        fake_pass,
    )

    result = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([], allow_legacy_finra=False),
        None,
    )

    assert result["complete"] is False
    assert (
        "single-page year subdivision could not produce two matching proofs "
        "within the 3-pass limit"
    ) in result["error"]
    assert subdivisions == [
        frozenset(),
        frozenset(),
        frozenset({"1"}),
    ]
    assert len(result["pass_proofs"]) == 3


def test_finra_partition_progress_logs_include_budget_and_last_partition(
    monkeypatch,
    caplog,
):
    filters = _finra_filter_form()
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 1, [row]),
    }

    with caplog.at_level("INFO", logger="regulatory_monitor"):
        result, _ = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is True
    messages = [record.getMessage() for record in caplog.records]
    assert any(
        "pass=pass-1" in message
        and "year=2026" in message
        and "type=all" in message
        and "budget=" in message
        and "last_completed=" in message
        for message in messages
    )
    assert any(
        "listing pass complete" in message
        and "budget=" in message
        and "last_completed=" in message
        for message in messages
    )


def test_finra_deterministic_coverage_rejects_empty_partition_evidence():
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    coverage = source_state["coverage"]
    coverage["schema_version"] = (
        regulatory_monitor.FINRA_DETERMINISTIC_COVERAGE_SCHEMA_VERSION
    )
    coverage["listing_mode"] = "deterministic-year-type-partitions"
    for key, value in (
        ("proof_version", None),
        ("filter_manifest", {}),
        ("partition_manifest", []),
        ("year_observations", []),
        ("unfiltered_reconciliation", {}),
        ("unclassified_evidence", {}),
    ):
        coverage[key] = value
        for proof in coverage["pass_proofs"]:
            proof[key] = deepcopy(value)

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any(
        "deterministic coverage filter_manifest is missing or empty" in error
        for error in errors
    )
    assert any(
        "deterministic coverage partition_manifest is missing or empty" in error
        for error in errors
    )
    assert any(
        "deterministic coverage unfiltered_reconciliation is missing or empty"
        in error
        for error in errors
    )


def test_finra_coverage_schema_versions_separate_legacy_and_deterministic():
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    legacy = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )

    assert legacy["coverage"]["schema_version"] == 1
    assert regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        legacy,
    ) == []

    forged = deepcopy(legacy)
    forged["coverage"]["listing_mode"] = (
        "deterministic-year-type-partitions"
    )
    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
    )
    assert any(
        "legacy coverage schema cannot claim deterministic partitions" in error
        for error in errors
    )

    forged = deepcopy(legacy)
    forged["coverage"]["schema_version"] = (
        regulatory_monitor.FINRA_DETERMINISTIC_COVERAGE_SCHEMA_VERSION
    )
    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        forged,
    )
    assert any(
        "deterministic coverage schema requires partition listing mode" in error
        for error in errors
    )


def test_finra_deterministic_proof_field_set_is_centralized(monkeypatch):
    filters = _finra_filter_form()
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 1, [row]),
    }

    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)

    assert set(regulatory_monitor.FINRA_DETERMINISTIC_PROOF_FIELDS) <= set(
        result["pass_proof"]
    )


def test_finra_committed_state_rejects_unequal_partition_page_identities():
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    coverage = source_state["coverage"]
    invalid = {"requested": 0, "final": 1, "active": 1}
    coverage["page_identities"][0] = deepcopy(invalid)
    for proof in coverage["pass_proofs"]:
        proof["page_identities"][0] = deepcopy(invalid)

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any("pass proof 0 page identities are invalid" in error for error in errors)


def test_finra_committed_state_rejects_tampered_pager_mode():
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    coverage = source_state["coverage"]
    coverage["page_identities"][0]["pager_mode"] = "fabricated"
    for proof in coverage["pass_proofs"]:
        proof["page_identities"][0]["pager_mode"] = "fabricated"

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any("pass proof 0 page identities are invalid" in error for error in errors)


def test_finra_partition_proof_rejects_tampered_pager_mode(monkeypatch):
    filters = _finra_filter_form()
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {
        (None, None, 0): _finra_filtered_listing_page(
            0, 1, [row], filters=filters
        ),
        ("1", None, 0): _finra_listing_page(0, 1, [row]),
    }
    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)
    proof = deepcopy(result["pass_proof"])
    proof["partition_manifest"][0]["page_identities"][0]["pager_mode"] = (
        "fabricated"
    )

    errors = regulatory_monitor._finra_pass_proof_recomputation_errors(
        regulatory_monitor.SOURCE_KEY_FINRA,
        proof,
        0,
    )

    assert any("pager evidence is invalid" in error for error in errors)


def test_finra_listing_pass_rejects_missing_filter_controls_by_default(
    monkeypatch,
):
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {(None, None, 0): _finra_listing_page(0, 1, [row])}

    result, _ = _run_partitioned_finra_pass(monkeypatch, pages)

    assert result["complete"] is False
    assert "filter controls" in result["error"]


def test_finra_listing_pass_allows_explicit_legacy_fixture_fallback(
    monkeypatch,
):
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    pages = {(None, None, 0): _finra_listing_page(0, 1, [row])}

    result, _ = _run_partitioned_finra_pass(
        monkeypatch,
        pages,
        legacy_fixture=True,
    )

    assert result["complete"] is True
    assert result["pass_proof"].get("filter_manifest") is None
    assert result["pass_proof"].get("partition_manifest") is None


def test_finra_legacy_fallback_rejects_unrecognized_session_marker(monkeypatch):
    row = (
        "/rules-guidance/notices/26-15",
        "Regulatory Notice 26-15",
        "2026-07-24",
    )
    content = _finra_listing_page(0, 1, [row])
    session = _FakeSession([], allow_legacy_finra=False)
    session._finra_legacy_fixture = True
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": content,
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        },
    )

    result = regulatory_monitor._fetch_finra_listing_pass(
        session,
        None,
        "1-test",
    )

    assert result["complete"] is False
    assert "filter controls" in result["error"]


def test_finra_two_pass_shifted_rows_fail_closed(monkeypatch):
    """A [A,B]/[C] -> [X,A]/[B,C] shift fails after both passes complete."""
    results = iter([
        _synthetic_finra_pass_result([["A", "B"], ["C"]], "pass-1"),
        _synthetic_finra_pass_result([["X", "A"], ["B", "C"]], "pass-2"),
        _synthetic_finra_pass_result([["A", "B"], ["Y", "C"]], "pass-3"),
    ])
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        lambda *_args: next(results),
    )
    result = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([]), None
    )
    assert result["complete"] is False
    assert "independent-pass mismatch" in result["error"]


def test_finra_uses_later_consensus_when_source_changes(monkeypatch):
    """A bounded third pass accepts the newer snapshot when passes two and three agree."""
    results = iter([
        _synthetic_finra_pass_result([["A", "B"], ["C"]], "pass-1"),
        _synthetic_finra_pass_result([["X", "A"], ["B", "C"]], "pass-2"),
        _synthetic_finra_pass_result([["X", "A"], ["B", "C"]], "pass-3"),
    ])
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        lambda *_args: next(results),
    )

    result = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([]), None
    )

    assert result["complete"] is True
    assert [row["title"] for row in result["rows"]] == ["X", "A", "B", "C"]
    assert [proof["token"] for proof in result["pass_proofs"]] == [
        "pass-2",
        "pass-3",
    ]


def test_finra_two_pass_same_rows_reordered_are_equivalent(monkeypatch):
    """Same-date rows may move across page boundaries without changing coverage."""
    results = iter([
        _synthetic_finra_pass_result([["A", "B"], ["C", "D"]], "pass-1"),
        _synthetic_finra_pass_result([["B", "C"], ["D", "A"]], "pass-2"),
    ])
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        lambda *_args: next(results),
    )

    result = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([]), None
    )

    assert result["complete"] is True
    assert [row["title"] for row in result["rows"]] == ["A", "B", "C", "D"]


def test_finra_passes_create_independent_sessions_sequentially(monkeypatch):
    """Pass two starts only after pass one has fully closed."""
    events = []

    class _PassSession:
        def close(self):
            events.append("close")

    proof = {
        "token": "pass",
        "declared_pages": 1,
        "pages_fetched": 1,
        "page_numbers": [0],
        "page_identities": [{"requested": 0, "final": 0, "active": 0}],
        "page_row_counts": [0],
        "page_row_digests": [compute_hash("[]")],
        "page_row_payloads": [[]],
        "raw_row_count": 0,
        "resolved_row_count": 0,
        "unresolved_row_count": 0,
        "unique_node_count": 0,
    }

    monkeypatch.setattr(
        regulatory_monitor,
        "_new_finra_pass_session",
        lambda _template: (events.append("new") or _PassSession()),
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        lambda *_args: (
            events.append("fetch")
            or {
                "complete": True,
                "rows": [],
                "records": [],
                "pages_fetched": 1,
                "declared_pages": 1,
                "cutoff_page": None,
                "pass_proof": proof,
            }
        ),
    )

    result = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([]), None
    )

    assert result["complete"] is True
    assert events == ["new", "fetch", "close", "new", "fetch", "close"]


def test_finra_complete_unfiltered_listing_catches_taxonomy_omissions(monkeypatch):
    """Selected-year taxonomy omissions cannot make the unfiltered crawl incomplete."""
    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    page_records = {
        0: [
            ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24"),
        ],
        1: [
            ("/rules-guidance/notices/26-05", "Regulatory Notice 26-05", "2026-02-27"),
        ],
    }
    details = {
        "/rules-guidance/notices/26-15": _finra_detail_page(
            "Notice 26-15", "2026-07-24", "Current notice content."
        ),
        "/rules-guidance/notices/26-05": _finra_detail_page(
            "Notice 26-05", "2026-02-27", "Omitted by selected-year taxonomy."
        ),
    }
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        if base_url == regulatory_monitor.FINRA_NOTICES_URL:
            page = 0
        elif "?page=" in base_url:
            page = int(base_url.rsplit("=", 1)[1])
        else:
            path = base_url.removeprefix("https://www.finra.org")
            return {
                "status_code": 200,
                "content": details[path],
                "final_url": url,
                "url": url,
                "was_redirected": False,
                "error": None,
            }
        content = _finra_listing_page(page, 2, page_records[page])
        return {
            "status_code": 200,
            "content": content,
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        since_date="2026-08-08",
    )

    assert result.complete is True
    assert {item.document_id for item in result} == {"FINRA 26-15", "FINRA 26-05"}
    assert not any("combine_1" in url for url in requested)


def test_finra_paginates_to_cutoff_and_refetches_overlap_window(monkeypatch):
    """A 92-page listing is fully traversed despite an old-page cutoff."""
    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    total_pages = 92
    page_records = {
        0: [
            ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24"),
            ("/rules-guidance/notices/information-notice-20260808",
             "Information Notice 8/8/26", "2026-08-08"),
        ],
        1: [("/rules-guidance/notices/26-14", "Regulatory Notice 26-14", "2026-07-10")],
        2: [("/rules-guidance/notices/26-13", "Regulatory Notice 26-13", "2026-08-01")],
        3: [("/rules-guidance/notices/26-12", "Regulatory Notice 26-12", "2026-07-01")],
        91: [("/rules-guidance/notices/26-99", "Regulatory Notice 26-99", "2026-06-15")],
    }
    for page in range(4, 91):
        page_records[page] = [(
            f"/rules-guidance/notices/information-notice-2026{page:04d}",
            f"Information Notice page {page}",
            "2026-06-01",
        )]
    details = {
        "/rules-guidance/notices/26-15": _finra_detail_page(
            "FINRA Requests Comment on Modernizing FINRA's Best Execution Guidance",
            "2026-07-24",
            "Edited summary for FINRA Rule 5310.",
        ),
        "/rules-guidance/notices/information-notice-20260808": _finra_detail_page(
            "Information Notice", "2026-08-08", "Current notice content."
        ),
        "/rules-guidance/notices/26-14": _finra_detail_page(
            "Older notice", "2026-07-10", "Older content."
        ),
        "/rules-guidance/notices/26-13": _finra_detail_page(
            "Backdated notice", "2026-08-01", "Backdated content."
        ),
        "/rules-guidance/notices/26-12": _finra_detail_page(
            "Overlap-window notice", "2026-07-01", "Overlap content."
        ),
        "/rules-guidance/notices/26-99": _finra_detail_page(
            "Backdated page 92 notice", "2026-06-15", "Page 92 content."
        ),
    }
    for page, records in page_records.items():
        for path, title, date in records:
            details.setdefault(
                path,
                _finra_detail_page(title, date, f"Content from listing page {page}."),
            )
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        if base_url == regulatory_monitor.FINRA_NOTICES_URL:
            page = 0
        elif "?page=" in base_url:
            page = int(base_url.rsplit("=", 1)[1])
        else:
            path = base_url.removeprefix("https://www.finra.org")
            content = details[path]
            return {
                "status_code": 200,
                "content": content,
                "final_url": url,
                "was_redirected": False,
                "error": None,
            }
        content = _finra_listing_page(page, total_pages, page_records[page])
        return {
            "status_code": 200,
            "content": content,
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        since_date="2026-08-08",
    )

    assert result.complete is True
    assert result.declared_pages == total_pages
    assert result.cutoff_page == 1
    assert result.pages_fetched == total_pages
    ids = {item.document_id for item in result}
    assert "FINRA 26-12" in ids
    assert "FINRA 26-99" in ids
    assert len(ids) == sum(len(records) for records in page_records.values())
    requested_bases = {_finra_request_base(url) for url in requested}
    assert "https://www.finra.org/rules-guidance/notices?page=2" in requested_bases
    assert "https://www.finra.org/rules-guidance/notices?page=3" in requested_bases
    assert "https://www.finra.org/rules-guidance/notices?page=91" in requested_bases
    edited = next(item for item in result if item.document_id == "FINRA 26-15")
    assert "Edited summary" in edited.abstract


def test_finra_pagination_overlap_detail_date_conflict_fails_closed(monkeypatch):
    """An unpaired listing/detail date conflict fails closed."""
    record = ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")
    pages = {
        regulatory_monitor.FINRA_NOTICES_URL: _finra_listing_page(0, 1, [record]),
        "https://www.finra.org/rules-guidance/notices/26-15": _finra_detail_page(
            "Notice 26-15", "2026-07-23", "Stable authoritative content."
        ),
    }

    def fake_fetch_page(url, _session, **_kwargs):
        lookup_url = _finra_request_base(url)
        return {
            "status_code": 200,
            "content": pages[lookup_url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )

    assert result.complete is False
    assert "date conflict" in result.error


def test_finra_identical_listing_overlap_is_coalesced(monkeypatch):
    """Stable cross-page duplicate rows coalesce after detail verification."""
    record = ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")
    listing = {
        regulatory_monitor.FINRA_NOTICES_URL: _finra_listing_page(0, 2, [record]),
        "https://www.finra.org/rules-guidance/notices?page=1": _finra_listing_page(
            1, 2, [record]
        ),
        "https://www.finra.org/rules-guidance/notices/26-15":
        _finra_detail_page_with_identity(
            "Regulatory Notice 26-15",
            "2026-07-24",
            "Stable content.",
            canonical_url=(
                "https://www.finra.org/rules-guidance/notices/26-15"
            ),
            node_id="382807",
        ),
    }

    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing[_finra_request_base(url)],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )

    assert result.complete is True
    assert len(result) == 1
    assert len(result.coverage["duplicate_ledger"]) == 1
    assert len(result.coverage["date_resolution_ledger"]) == 1


def test_finra_repeated_page_identity_fails_closed(monkeypatch):
    """A response claiming the previous page cannot advance coverage."""
    record = ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")
    listing = {
        regulatory_monitor.FINRA_NOTICES_URL: _finra_listing_page(0, 2, [record]),
        "https://www.finra.org/rules-guidance/notices?page=1": _finra_listing_page(
            0, 2, [record]
        ),
    }

    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing[_finra_request_base(url)],
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )

    assert result.complete is False
    assert "identity mismatch" in result.error


def test_finra_active_pager_ignores_global_navigation_current_page():
    """Global aria-current navigation must not mask the listing pager."""
    soup = BeautifulSoup(
        """
        <a aria-current="page" class="nav-link active">Notices</a>
        <nav aria-labelledby="pagination-heading">
          <ul class="pagination">
            <li class="page-item active"><span class="page-link">1</span></li>
            <li class="page-item"><a class="page-link" href="?page=1">2</a></li>
          </ul>
        </nav>
        """,
        "html.parser",
    )

    assert regulatory_monitor._extract_finra_active_page(soup) == 0


def test_finra_listing_collects_all_notice_slug_types():
    """Election/trade notices are not silently omitted from full coverage."""
    soup = BeautifulSoup(
        """
        <table><tbody>
          <tr><td><a href="/rules-guidance/notices/election-notice-091809">
            Election Notice - 9/18/09</a></td></tr>
          <tr><td><a href="/rules-guidance/notices/trade-reporting-notice-022409">
            Trade Reporting Notice</a></td></tr>
          <tr><td><a href="/rules-guidance/notices/09-29">
            Regulatory Notice 09-29</a></td></tr>
        </tbody></table>
        """,
        "html.parser",
    )

    records = regulatory_monitor._extract_finra_notice_links(soup)

    assert [record[0].rsplit("/", 1)[-1] for record in records] == [
        "election-notice-091809",
        "trade-reporting-notice-022409",
        "09-29",
    ]


def test_finra_uses_authoritative_detail_fields_and_classifies_26_15(monkeypatch):
    """FINRA 26-15 must use its published date/summary, not URL heuristics."""
    listing_html = """
    <html><body>
      <nav aria-labelledby="pagination-heading">
        <ul class="pagination"><li class="page-item active"><span class="page-link">1</span></li></ul>
      </nav>
      <a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>
      <a href="/rules-guidance/notices/26-14">Regulatory Notice 26-14</a>
    </body></html>
    """
    detail_26_15 = """
    <html><body>
      <h1>FINRA Requests Comment on Modernizing FINRA's Best Execution Guidance</h1>
      <div class="field--name-field-core-official-dt">
        <time datetime="2026-07-24T12:00:00Z">July 24, 2026</time>
      </div>
      <div class="field--name-body"><h2>Summary</h2>
        <p>A broker-dealer duty under FINRA Rule 5310 requires best execution.</p>
        <h2>Action Required</h2><p>Comments are requested.</p>
      </div>
    </body></html>
    """
    detail_26_14 = """
    <html><body>
      <h1>Older notice</h1>
      <div class="field--name-field-core-official-dt">
        <time datetime="2026-07-18T12:00:00Z">July 18, 2026</time>
      </div>
      <div class="field--name-body"><h2>Summary</h2><p>Older content.</p></div>
    </body></html>
    """

    def fake_fetch_page(url, _session, **_kwargs):
        pages = {
            regulatory_monitor.FINRA_NOTICES_URL: listing_html,
            "https://www.finra.org/rules-guidance/notices/26-15": detail_26_15,
            "https://www.finra.org/rules-guidance/notices/26-14": detail_26_14,
        }
        lookup_url = _finra_request_base(url)
        return {
            "status_code": 200,
            "content": pages[lookup_url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    config = {
        "regulatory": {
            "medium_patterns": [
                {"pattern": r"\bbroker-dealer", "reason": "Broker-dealer regulation"}
            ]
        },
        "keyword_control_map": [],
    }

    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), config, since_date="2026-07-20"
    )

    assert result.complete is True
    assert {item.document_id for item in result} == {"FINRA 26-15", "FINRA 26-14"}
    item = next(item for item in result if item.document_id == "FINRA 26-15")
    assert item.title == "FINRA Requests Comment on Modernizing FINRA's Best Execution Guidance"
    assert item.publication_date == "2026-07-24"
    assert "broker-dealer" in item.abstract
    assert "Action Required" in item.substantive_content
    assert item.classification == regulatory_monitor.CLASSIFICATION_MEDIUM
    assert item.classification_reason == "Broker-dealer regulation"
    assert regulatory_monitor._item_content_hash(item) == compute_hash(item.substantive_content)


def test_finra_missing_date_remains_unknown(monkeypatch):
    """Missing FINRA publication metadata must remain empty, never January 1/current date."""
    listing_html = """
    <nav aria-labelledby="pagination-heading">
      <ul class="pagination"><li class="page-item active"><span class="page-link">1</span></li></ul>
    </nav>
    <a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>
    """
    detail_html = """
    <html><body><h1>Notice title</h1>
      <div class="field--name-body"><h2>Summary</h2><p>Broker-dealer content.</p></div>
    </body></html>
    """

    def fake_fetch_page(url, _session, **_kwargs):
        content = (
            listing_html
            if _finra_request_base(url) == regulatory_monitor.FINRA_NOTICES_URL
            else detail_html
        )
        return {"status_code": 200, "content": content, "final_url": url,
                "was_redirected": False, "error": None}

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
    )

    assert result.complete is True
    assert result[0].publication_date == ""
    assert "2026-01-01" not in result[0].publication_date


def test_workflow_documents_fail_closed_exit_two_and_rejects_unknown_statuses():
    """Exit 2 is a known failure contract; unknown statuses still fail closed."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert 'exit "$EXIT_CODE"' in workflow
    assert '0|1)' in workflow
    assert "documented fail-closed exit code 2" in workflow
    assert "undocumented exit code" in workflow
    assert "- name: Validate monitor outcome and outputs" in workflow
    assert 'if: always()' in workflow
    assert 'steps.monitor.outcome' in workflow
    assert "exit_code output is missing" in workflow
    assert "exit_code output is undocumented" in workflow
    assert "continue-on-error:" not in workflow


def test_workflow_gives_finra_partition_budget_explicit_timeout_headroom():
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert workflow.count("timeout-minutes: 360") == 2
    assert workflow.count("'scripts/regulatory_monitor.py'") == 2
    assert workflow.count("'.github/workflows/regulatory-monitoring.yml'") == 2
    workflow_timeout_minutes = 360
    assert workflow_timeout_minutes <= 360
    assert regulatory_monitor.FINRA_LISTING_REQUEST_BUDGET == 420
    assert regulatory_monitor.FINRA_LISTING_REQUEST_INTERVAL_SECONDS == 12.0
    assert regulatory_monitor.FINRA_MAX_LISTING_PASSES == 3
    assert regulatory_monitor.FINRA_DETAIL_REFRESH_HEADROOM_MINUTES == 75
    assert (
        regulatory_monitor.FINRA_LISTING_TO_DETAIL_COOLDOWN_SECONDS
        == 1800
    )
    listing_minutes = (
        regulatory_monitor.FINRA_MAX_LISTING_PASSES
        * regulatory_monitor.FINRA_LISTING_REQUEST_BUDGET
        * regulatory_monitor.FINRA_LISTING_REQUEST_INTERVAL_SECONDS
        / 60
    )
    assert listing_minutes == 252
    total_minutes = (
        listing_minutes
        + regulatory_monitor.FINRA_DETAIL_REFRESH_HEADROOM_MINUTES
        + (
            regulatory_monitor.FINRA_LISTING_TO_DETAIL_COOLDOWN_SECONDS
            / 60
        )
    )
    assert total_minutes == 357
    assert workflow_timeout_minutes - total_minutes == 3


def test_workflow_persists_exit0_dirty_state_without_clean_run_pr_noise():
    """Exit-0 state progress gets a maintenance PR; a clean run stays silent."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert "- name: Detect persisted monitor changes" in workflow
    assert "git status --porcelain=v1 --untracked-files=all" in workflow
    assert 'echo "changed=true"' in workflow
    assert 'echo "changed=false"' in workflow
    assert (
        'if [ "$EXIT_CODE" = "1" ] || { [ "$EXIT_CODE" = "0" ] && '
        '[ "$STATE_CHANGED" = "true" ]; }; then'
    ) in workflow
    assert "steps.should_create_pr.outputs.create_pr == 'true'" in workflow
    assert "successful state maintenance" in workflow
    # Blocker 1: this privileged monitor workflow no longer computes an
    # auto-merge-eligibility signal or auto-merges at all.
    assert "automerge_eligible" not in workflow


def test_workflow_exit_semantics_keep_findings_and_fail_closed_runs_distinct():
    """Exit 1 stages findings; exit >=2 cannot reach state PR creation."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert "reports/monitoring/*.md" in workflow
    assert "data/monitor-state.json.backup" in workflow
    assert "echo \"run_kind=findings\"" in workflow
    assert "steps.monitor.outputs.exit_code == '0' ||" in workflow
    assert "steps.monitor.outputs.exit_code == '1'" in workflow
    assert 'if [ "$EXIT_CODE" -eq 1 ]; then' in workflow
    assert "if: steps.create_pr.outputs.pull-request-number && steps.monitor.outputs.exit_code == '1'" in workflow
    assert "steps.should_create_pr.outputs.create_pr == 'true'" in workflow
    assert "steps.monitor.outputs.exit_code == '0' ||" in workflow


def test_workflow_mutation_is_default_branch_only_and_cas_checked():
    """Feature refs are read-only; mutation has isolated write permissions and CAS."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert "validate-read-only:" in workflow
    assert "monitor-regulatory:" in workflow
    assert "contents: read" in workflow
    assert "contents: write" in workflow
    assert "pull-requests: read" in workflow
    assert "pull-requests: write" in workflow
    assert "python scripts/regulatory_monitor.py --dry-run" in workflow
    assert workflow.count("scripts/regulatory_recovery_anchors.py") == 2
    assert "persist-credentials: false" in workflow
    assert "Checkout trusted default branch" in workflow
    assert "Verify trusted default-branch checkout" in workflow
    assert "Generate GitHub App token" in workflow
    assert "STATE_SHA_BEFORE=$(sha256sum data/monitor-state.json" in workflow
    assert "- name: Validate default-branch monitor CAS" in workflow
    assert 'git fetch --no-tags origin "$DEFAULT_BRANCH"' in workflow
    assert 'BASE_STATE=$(git show "$EXPECTED_BASE:data/monitor-state.json"' in workflow
    assert "steps.cas.outputs.valid == 'true'" in workflow
    assert "baseRefName,baseRefOid" in workflow
    # The removed auto-merge step's "Maintenance PR base CAS mismatch" is gone;
    # the post-create verification step is what now binds the PR to the exact
    # default branch and validated head.
    assert "- name: Verify created PR binds the validated generated output" in workflow
    assert "Created PR is not based on the default branch" in workflow

    state_changes_block = workflow.split(
        "- name: Detect persisted monitor changes", 1
    )[1].split("- name:", 1)[0]
    cas_block = workflow.split(
        "- name: Validate default-branch monitor CAS", 1
    )[1].split("- name:", 1)[0]
    for block in (state_changes_block, cas_block):
        assert "steps.monitor.outcome == 'success'" in block
        assert "github.event_name != 'pull_request'" in block
        assert (
            "github.ref_name == github.event.repository.default_branch"
            in block
        )

    read_only_block = workflow.split("validate-read-only:", 1)[1].split(
        "monitor-regulatory:", 1
    )[0]
    assert "contents: write" not in read_only_block
    assert "pull-requests: write" not in read_only_block
    assert "private-key:" not in read_only_block


def _workflow_text() -> str:
    return (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")


def test_cas_step_publishes_a_manifest_of_the_exact_generated_output():
    """The CAS step must record every mutated path with its blob AND content hash.

    Without a manifest the post-create verification can only reason about a
    shape ("looks like state files"), which cannot distinguish the validated
    output from any other state-shaped payload pushed onto the same branch.
    """
    workflow = _workflow_text()
    cas_block = workflow.split(
        "- name: Validate default-branch monitor CAS", 1
    )[1].split("- name:", 1)[0]

    assert "ALLOWED_PATHS=" in cas_block
    assert "git status --porcelain=v1 --untracked-files=all" in cas_block
    assert "Unexpected generated file" in cas_block
    assert "Generated path is missing" in cas_block
    assert "git hash-object" in cas_block
    assert "sha256sum -- \"$generated_path\"" in cas_block
    assert "Generated manifest does not bind the validated state" in cas_block
    assert "generated_manifest<<GENERATED_MANIFEST_EOF" in cas_block
    assert 'echo "state_sha_after=$CURRENT_STATE" >> "$GITHUB_OUTPUT"' in cas_block

    # Every fail-closed branch must exit non-zero, never fall through to `valid=true`.
    for message in (
        "Unexpected generated file",
        "Generated path is missing",
        "Could not hash generated path",
        "Generated manifest does not bind the validated state",
    ):
        tail = cas_block.split(message, 1)[1].split("fi", 1)[0]
        assert "exit 2" in tail, message


def test_workflow_stops_at_verified_pr_without_auto_merge():
    """Blockers 1 and 2: no auto-merge; stop at a PR proven to carry the output.

    Blocker 1: no GitHub merge primitive binds BOTH the exact base and head
    atomically, and there is no branch protection/ruleset, so an unattended
    auto-merge cannot be made fail-closed against a stale-main race. The
    workflow therefore must not merge at all — it stops at a validated PR for
    the existing external guarded sweep / human gate.

    Blocker 2: create-pull-request restores the base checkout after opening the
    PR, so the generated files are no longer on disk and cannot be re-hashed
    from the workspace. The created PR is instead bound to the exact validated
    output via the PR head commit's git blobs (content-addressed) and an exact
    file-set check, all read through the API.
    """
    workflow = _workflow_text()

    # Blocker 1: every auto-merge primitive is gone from the entire workflow.
    assert "- name: Enable auto-merge" not in workflow
    assert "gh pr merge" not in workflow
    assert "--auto" not in workflow
    assert "--match-head-commit" not in workflow
    assert "automerge_eligible" not in workflow
    assert "--disable-auto" not in workflow

    assert (
        "- name: Verify created PR binds the validated generated output" in workflow
    )
    consolidate_name = "- name: Consolidate superseded Regulatory-monitor PRs"
    verify_block = workflow.split(
        "- name: Verify created PR binds the validated generated output", 1
    )[1].split(consolidate_name, 1)[0]

    # Bindings are injected via env (not inline expansion) and are all required.
    for binding in (
        "NEW_PR: ${{ steps.create_pr.outputs.pull-request-number }}",
        "EXPECTED_HEAD: ${{ steps.create_pr.outputs.pull-request-head-sha }}",
        "EXPECTED_BASE: ${{ steps.cas.outputs.base_sha }}",
        "EXPECTED_STATE_AFTER: ${{ steps.cas.outputs.state_sha_after }}",
        "GENERATED_MANIFEST: ${{ steps.cas.outputs.generated_manifest }}",
        "DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}",
    ):
        assert binding in verify_block, binding
    assert "set -euo pipefail" in verify_block
    assert "flag_for_review()" in verify_block
    assert "Missing CAS/generated-output binding" in verify_block

    # The PR must be based on the default branch and point at the exact head the
    # create step produced (the immutable commit the blob checks below bind to).
    assert (
        'gh pr view "$NEW_PR" --json baseRefName,baseRefOid,headRefOid'
        in verify_block
    )
    assert '[ "$PR_BASE_NAME" != "$DEFAULT_BRANCH" ]' in verify_block
    assert '[ "$PR_BASE_SHA" != "$EXPECTED_BASE" ]' in verify_block
    assert '[ "$PR_HEAD_SHA" != "$EXPECTED_HEAD" ]' in verify_block

    # Blocker 2: each manifested path is bound to the EXACT git blob carried by
    # the PR head commit (read via the API, not the restored workspace), and the
    # state blob additionally binds the CAS-validated content hash.
    assert "contents/${manifest_path}?ref=${EXPECTED_HEAD}" in verify_block
    assert '[ "$HEAD_BLOB" != "$manifest_blob" ]' in verify_block
    assert '[ "$manifest_content" != "$EXPECTED_STATE_AFTER" ]' in verify_block
    # Consumed via a here-string (not a pipe) so an inner `exit 2` propagates.
    assert 'done <<< "$(printf' in verify_block

    # The PR must carry EXACTLY the validated file set, compared as
    # "<path> <blob sha>" pairs so an extra/substituted blob is a mismatch.
    assert (
        'gh api "repos/${GITHUB_REPOSITORY}/pulls/${NEW_PR}/files" --paginate'
        in verify_block
    )
    assert '--jq \'.[] | "\\(.filename) \\(.sha)"\'' in verify_block
    assert "awk 'NF {print $1, $2}'" in verify_block
    assert '[ "$PR_FILES" != "$EXPECTED_FILES" ]' in verify_block

    # It proves the PR; it never merges. It surfaces the hand-off explicitly.
    assert "external guarded sweep / human merge gate" in verify_block
    assert "verified=true" in verify_block

    # Every mismatch path must both flag for review and fail closed (exit 2).
    for message in (
        "Missing CAS/generated-output binding",
        "Created PR is not based on the default branch",
        "Created PR base moved after validation",
        "Created PR head moved after creation",
        "does not match the validated generated blob",
        "Manifest state content hash does not match",
        "contains non-state file(s)",
        "does not carry exactly the validated generated output",
    ):
        tail = verify_block.split(message, 1)[1].split("fi", 1)[0]
        assert "flag_for_review" in tail, message
        assert "exit 2" in tail, message


def test_workflow_consolidates_only_after_successful_pr_verification():
    """Older trusted PRs survive unless the newest PR is fully verified."""
    workflow = _workflow_text()
    verify_name = "- name: Verify created PR binds the validated generated output"
    consolidate_name = "- name: Consolidate superseded Regulatory-monitor PRs"

    assert workflow.index(verify_name) < workflow.index(consolidate_name)
    consolidate_block = workflow.split(consolidate_name, 1)[1]
    condition = consolidate_block.split("env:", 1)[0]
    for guard in (
        "steps.create_pr.outputs.pull-request-number",
        "steps.cas.outputs.valid == 'true'",
        "steps.verify_pr.outputs.verified == 'true'",
        "vars.REGULATORY_STATE_AUTOMERGE == 'true'",
    ):
        assert guard in condition, guard

    verify_block = workflow.split(verify_name, 1)[1].split(
        consolidate_name, 1
    )[0]
    assert 'echo "verified=true" >> "$GITHUB_OUTPUT"' in verify_block
    assert "gh pr close" not in verify_block
    assert "gh pr close" in consolidate_block
    assert "--delete-branch" in consolidate_block


def test_workflow_rechecks_exact_base_immediately_before_consolidation():
    """A moved default branch must strand older PRs instead of closing them."""
    workflow = _workflow_text()
    consolidate_name = "- name: Consolidate superseded Regulatory-monitor PRs"
    consolidate_block = workflow.split(consolidate_name, 1)[1]

    for binding in (
        "EXPECTED_HEAD: ${{ steps.create_pr.outputs.pull-request-head-sha }}",
        "EXPECTED_BASE: ${{ steps.cas.outputs.base_sha }}",
        "DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}",
    ):
        assert binding in consolidate_block, binding

    assert "CANDIDATES=$(gh pr list" in consolidate_block
    assert (
        'CONSOLIDATION_VIEW=$(gh pr view "$NEW_PR" '
        "--json baseRefName,baseRefOid,headRefOid"
    ) in consolidate_block
    assert (
        'CURRENT_BASE=$(gh api "repos/${GITHUB_REPOSITORY}/commits/'
        '${DEFAULT_BRANCH}" --jq \'.sha\')'
    ) in consolidate_block
    assert '[ "$PR_BASE_SHA" != "$EXPECTED_BASE" ]' in consolidate_block
    assert '[ "$CURRENT_BASE" != "$EXPECTED_BASE" ]' in consolidate_block
    assert '[ "$PR_HEAD_SHA" != "$EXPECTED_HEAD" ]' in consolidate_block

    list_index = consolidate_block.index("CANDIDATES=$(gh pr list")
    recheck_index = consolidate_block.index("CONSOLIDATION_VIEW=$(gh pr view")
    current_base_index = consolidate_block.index("CURRENT_BASE=$(gh api")
    loop_index = consolidate_block.index("while read -r n branch")
    close_index = consolidate_block.index('gh pr close "$n"')
    assert list_index < recheck_index < current_base_index < loop_index < close_index

    for message in (
        "Could not read PR metadata before consolidation",
        "Created PR base changed before consolidation",
        "Default branch moved before consolidation",
        "Created PR head changed before consolidation",
    ):
        tail = consolidate_block.split(message, 1)[1].split("fi", 1)[0]
        assert "flag_for_review" in tail, message
        assert "exit 2" in tail, message


def test_baseline_initialization_requires_manual_approval_and_is_not_in_workflow():
    """The exceptional baseline path cannot be invoked by Actions automation."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert "--initialize-baseline" not in workflow
    assert "REGULATORY_MONITOR_BASELINE_APPROVED=I_UNDERSTAND" not in workflow


def test_recovery_state_restores_complete_regulatory_baseline_without_watermark_only_corruption():
    """Recovery state must stay complete, self-consistent and safely rollback-able.

    Deliberately expressed as floors plus internal reconciliation rather than
    frozen live-source totals: the FINRA archive and the Federal Register
    accumulate over time, so equality assertions on today's counts would fail
    the moment a legitimate future run adds a notice. The floors sit just under
    the recovered Aug-2026 baseline (506 Federal Register entries, 3,616 FINRA
    entries across 92 listing pages, 3,671 raw rows, 622 aliases) so truncation
    or regression toward the 332/2-entry incident state still fails closed.

    Byte-equality between primary and backup is intentionally NOT asserted:
    ``save_state_atomic`` stores the *previous* primary in the backup before
    writing the new primary, so a legitimate future state PR necessarily makes
    them differ. Instead both snapshots are validated as complete baselines in
    their own right, and the relationship between them is checked for safe
    rollback (primary never regresses below the backup it supersedes).
    """
    primary_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    backup_path = primary_path.with_name("monitor-state.json.backup")

    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    backup = json.loads(backup_path.read_text(encoding="utf-8"))

    def _assert_complete_baseline(state):
        """Every snapshot must independently prove a usable, complete baseline."""
        assert regulatory_monitor._validate_regulatory_state(
            state,
            [
                regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
                regulatory_monitor.SOURCE_KEY_FINRA,
            ],
        ) == []

        federal = state["sources"][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]
        federal_coverage = federal["coverage"]
        assert len(federal["entries"]) >= MIN_FEDERAL_REGISTER_ENTRIES
        assert federal_coverage["entry_count"] == len(federal["entries"])
        assert federal_coverage["expected_count"] == federal_coverage["fetched_count"]
        assert federal["last_checked"] >= RECOVERY_WATERMARK_DATE

        finra = state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
        entries = finra["entries"]
        finra_coverage = finra["coverage"]
        assert finra["last_run"] >= RECOVERY_WATERMARK_DATE
        assert len(entries) >= MIN_FINRA_ENTRIES
        assert finra_coverage["pages_fetched"] >= MIN_FINRA_LISTING_PAGES
        assert finra_coverage["raw_row_count"] >= MIN_FINRA_RAW_LISTING_ROWS

        # Internal reconciliation replaces frozen totals.
        assert finra_coverage["entry_count"] == len(entries)
        assert finra_coverage["detail_count"] == len(entries)
        assert finra_coverage["unique_node_count"] == finra_coverage["detail_count"]
        assert finra_coverage["unresolved_row_count"] == 0
        assert finra_coverage["raw_row_count"] == (
            finra_coverage["resolved_row_count"]
            + finra_coverage["unresolved_row_count"]
        )
        assert finra_coverage["listing_record_count"] == finra_coverage["resolved_row_count"]
        assert finra_coverage["pages_fetched"] == finra_coverage["declared_pages"]
        assert len(finra_coverage["page_numbers"]) == finra_coverage["pages_fetched"]
        # Every listing row coalesced into a shared node must be ledgered.
        assert len(finra_coverage["duplicate_ledger"]) >= (
            finra_coverage["resolved_row_count"] - finra_coverage["unique_node_count"]
        )
        assert finra_coverage["conflict_ledger"] == []

        # Proof/count/digest reconciliation, recomputed rather than trusted.
        assert len(finra_coverage["fetched_entry_identities"]) == finra_coverage["detail_count"]
        assert finra_coverage["fetched_entry_identity_digest"] == (
            regulatory_monitor._identity_digest(
                finra_coverage["fetched_entry_identities"]
            )
        )
        assert finra_coverage["entry_identity_digest"] == regulatory_monitor._identity_digest(
            sorted(entries)
        )
        assert finra_coverage["entries_digest"] == regulatory_monitor._entries_digest(entries)
        assert set(finra_coverage["fetched_entry_identities"]) == set(entries)
        for index, proof in enumerate(finra_coverage["pass_proofs"]):
            assert regulatory_monitor._finra_pass_proof_recomputation_errors(
                regulatory_monitor.SOURCE_KEY_FINRA, proof, index
            ) == []

        # Alias ledger: recovered aliases stay ledger-only and hash-bound.
        alias_ledger = finra_coverage["alias_ledger"]
        assert len(alias_ledger) >= MIN_FINRA_ALIASES
        assert finra_coverage["alias_ledger_digest"] == regulatory_monitor._alias_ledger_digest(
            alias_ledger
        )
        assert not (
            {item["old_identity"] for item in alias_ledger} & set(entries)
        )
        for alias in alias_ledger:
            head, chain_errors = regulatory_monitor._finra_alias_chain_head(alias)
            assert chain_errors == []
            assert entries[alias["canonical_identity"]] == head

    # Both the live primary and the backup it supersedes must independently be
    # complete, fail-closed baselines -- the backup is only a safe fallback if
    # it too proves a usable state.
    _assert_complete_baseline(primary)
    _assert_complete_baseline(backup)

    # Relationship / rollback semantics between the two snapshots. The backup is
    # the state the primary superseded, so the primary may only move forward:
    # watermarks never regress and the complete FINRA archive never shrinks.
    primary_fr = primary["sources"][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]
    backup_fr = backup["sources"][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]
    assert primary_fr["last_checked"] >= backup_fr["last_checked"]

    primary_finra = primary["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    backup_finra = backup["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    assert primary_finra["last_run"] >= backup_finra["last_run"]
    assert len(primary_finra["entries"]) >= len(backup_finra["entries"])

    # Coverage preservation: no notice the backup covered may vanish across the
    # save. Every backup FINRA identity must remain reachable in the primary --
    # either still a canonical entry or migrated to one through an alias -- so a
    # rollback never resurrects a notice the primary already dropped, and a roll
    # forward never silently loses coverage.
    primary_alias_old_identities = {
        alias["old_identity"]
        for alias in primary_finra["coverage"]["alias_ledger"]
    }
    primary_reachable = set(primary_finra["entries"]) | primary_alias_old_identities
    missing_from_primary = set(backup_finra["entries"]) - primary_reachable
    assert not missing_from_primary, (
        "primary lost FINRA coverage present in the backup: "
        f"{sorted(missing_from_primary)[:5]}"
    )


def test_legacy_finra_proof_requires_explicit_recovery_migration():
    """Legacy FINRA coverage is admitted only by the approved recovery path."""
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    legacy_state = deepcopy(state)
    coverage = legacy_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["coverage"]
    prior_alias_ledger = coverage.get("alias_ledger", [])
    prior_migration_ledger = coverage.get("migration_ledger", [])
    for key in (
        "alias_ledger",
        "alias_ledger_digest",
    ):
        coverage.pop(key, None)
    coverage["migration_ledger"] = prior_migration_ledger or [
        {
            "identity": item["old_identity"],
            "reason": item["evidence"]["reason"],
        }
        for item in prior_alias_ledger
    ]
    for item in prior_alias_ledger:
        legacy_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"][
            item["old_identity"]
        ] = legacy_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA][
            "entries"
        ][item["canonical_identity"]]
    legacy_entries = legacy_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA][
        "entries"
    ]
    coverage["entry_count"] = len(legacy_entries)
    coverage["entries_digest"] = regulatory_monitor._entries_digest(legacy_entries)

    normal_errors = regulatory_monitor._validate_regulatory_state(
        legacy_state,
        [
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
            regulatory_monitor.SOURCE_KEY_FINRA,
        ],
    )
    assert any("alias_ledger" in error for error in normal_errors)

    recovery_errors = regulatory_monitor._validate_regulatory_state(
        legacy_state,
        [
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
            regulatory_monitor.SOURCE_KEY_FINRA,
        ],
        allow_legacy_finra_identity_proof=True,
    )
    assert recovery_errors == []


def test_known_corrupt_incident_state_fails_coverage_validation():
    """The 332/2 state cannot hide behind Aug-9 watermarks."""
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    incident = json.loads(state_path.read_text(encoding="utf-8"))
    incident["sources"][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]["entries"] = dict(
        list(
            incident["sources"][
                regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER
            ]["entries"].items()
        )[:332]
    )
    incident["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"] = dict(
        list(
            incident["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"].items()
        )[:2]
    )
    for source_key in (
        regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
        regulatory_monitor.SOURCE_KEY_FINRA,
    ):
        source_state = incident["sources"][source_key]
        source_state["last_run"] = "2026-08-09T20:39:20+00:00"
        coverage = source_state["coverage"]
        coverage["entry_count"] = len(source_state["entries"])
        coverage["entries_digest"] = regulatory_monitor._entries_digest(
            source_state["entries"]
        )
        coverage["watermark"]["last_run"] = source_state["last_run"]
    fr_coverage = incident["sources"][
        regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER
    ]["coverage"]
    fr_coverage["expected_count"] = 332
    fr_coverage["fetched_count"] = 332
    errors = regulatory_monitor._validate_regulatory_state(
        incident,
        [
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
            regulatory_monitor.SOURCE_KEY_FINRA,
        ],
    )
    assert any(
        "identity digest" in error or "unaccounted identities" in error
        for error in errors
    )


def test_dry_run_does_not_fetch_or_persist_watermarks(monkeypatch):
    """Feature/PR validation must not call sources or write monitor state."""
    def fail_fetch(*_args, **_kwargs):
        raise AssertionError("dry-run must not fetch source data")

    def fail_save(*_args, **_kwargs):
        raise AssertionError("dry-run must not persist state")

    monkeypatch.setattr(regulatory_monitor, "fetch_federal_register_documents", fail_fetch)
    monkeypatch.setattr(regulatory_monitor, "fetch_finra_notices", fail_fetch)
    monkeypatch.setattr(regulatory_monitor, "save_state_atomic", fail_save)
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: {})
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py", "--dry-run"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 0


def test_finra_missing_pager_fails_closed(monkeypatch):
    """Notice links without authoritative pager metadata must not imply one page."""
    listing_html = '<a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>'

    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda _url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing_html,
            "final_url": regulatory_monitor.FINRA_NOTICES_URL,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
    )

    assert result.complete is False
    assert "pagination metadata" in result.error


def _finra_page_result(url, content):
    return {
        "status_code": 200,
        "content": content,
        "final_url": url,
        "url": url,
        "was_redirected": False,
        "error": None,
    }


def _finra_live_shaped_filtered_rows(filters=""):
    return f"""
    <html><body>{filters}
      <table><tbody>
        <tr><td><time datetime="2026-08-26T12:00:00Z"></time>
          <a href="/rules-guidance/notices/26-16">
            Regulatory Notice 26-16
          </a>
        </td></tr>
      </tbody></table>
    </body></html>
    """


def test_finra_filtered_page_zero_infers_single_page_with_resolved_rows():
    url = regulatory_monitor._finra_query_page_url(
        0,
        {"combine_1": "1"},
    )

    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(
            url,
            _finra_live_shaped_filtered_rows(_finra_filter_form()),
        ),
        url,
        0,
    )

    assert result["complete"] is True
    assert result["page_declared"] == 1
    assert result["active_page"] == 0
    assert result["final_page"] == 0
    assert result["pager_mode"] == "inferred-single"
    assert len(result["page_rows"]) == 1


def test_finra_filtered_page_zero_infers_explicit_zero_without_pager():
    url = regulatory_monitor._finra_query_page_url(
        0,
        {"combine_1": "1"},
    )
    content = (
        "<html><body>"
        '<div class="view-empty">No regulatory notices</div>'
        "</body></html>"
    )

    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(url, content),
        url,
        0,
    )

    assert result["complete"] is True
    assert result["page_declared"] == 0
    assert result["active_page"] == 0
    assert result["pager_mode"] == "explicit-zero"
    assert result["page_rows"] == []


def test_finra_filtered_page_zero_without_rows_or_zero_shape_fails_closed():
    url = regulatory_monitor._finra_query_page_url(
        0,
        {"combine_1": "1"},
    )

    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(
            url,
            "<html><body><div class=\"view-content\"></div></body></html>",
        ),
        url,
        0,
    )

    assert result["complete"] is False
    assert "pagination metadata" in result["error"]


def test_finra_unfiltered_page_zero_without_pager_still_fails_closed():
    url = regulatory_monitor.FINRA_NOTICES_URL

    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(url, _finra_live_shaped_filtered_rows()),
        url,
        0,
    )

    assert result["complete"] is False
    assert "pagination metadata" in result["error"]


def test_finra_filtered_page_after_zero_without_pager_still_fails_closed():
    url = regulatory_monitor._finra_query_page_url(
        1,
        {"combine_1": "1"},
    )

    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(url, _finra_live_shaped_filtered_rows()),
        url,
        1,
    )

    assert result["complete"] is False
    assert "pagination metadata" in result["error"]


@pytest.mark.parametrize(
    ("case", "url", "content", "final_url", "page"),
    [
        (
            "missing-pager",
            (
                "https://www.finra.org/rules-guidance/notices"
                "?combine_1=1&_finra_pass=secret-token"
            ),
            "<html><body><div class=\"view-content\"></div></body></html>",
            (
                "https://www.finra.org/rules-guidance/notices"
                "?combine_1=1&_finra_pass=secret-token"
            ),
            0,
        ),
        (
            "identity-mismatch",
            (
                "https://www.finra.org/rules-guidance/notices"
                "?combine_1=1&_finra_pass=secret-token"
            ),
            _finra_listing_page(
                0,
                1,
                [(
                    "/rules-guidance/notices/26-15",
                    "Regulatory Notice 26-15",
                    "2026-07-24",
                )],
            ),
            (
                "https://www.finra.org/rules-guidance/notices"
                "?combine_1=2&_finra_pass=other-secret"
            ),
            0,
        ),
        (
            "malformed-filtered",
            (
                "https://www.finra.org/rules-guidance/notices"
                "?combine_1=1&_finra_pass=secret-token"
            ),
            """
            <nav aria-labelledby="pagination-heading">
              <ul class="pagination">
                <li><a href="?page=not-a-number">Next</a></li>
              </ul>
            </nav>
            """,
            (
                "https://www.finra.org/rules-guidance/notices"
                "?combine_1=1&_finra_pass=secret-token"
            ),
            0,
        ),
        (
            "unfiltered",
            (
                "https://www.finra.org/rules-guidance/notices"
                "?_finra_pass=secret-token"
            ),
            _finra_live_shaped_filtered_rows(),
            (
                "https://www.finra.org/rules-guidance/notices"
                "?_finra_pass=secret-token"
            ),
            0,
        ),
    ],
)
def test_finra_listing_page_errors_include_redacted_structured_context(
    case,
    url,
    content,
    final_url,
    page,
):
    result = regulatory_monitor._finra_validate_listing_page_result(
        _finra_page_result(url, content) | {"final_url": final_url},
        url,
        page,
        partition_label=(
            "pass-2/year=2026/type=-Regulatory Notice"
            if case != "unfiltered"
            else "pass-2/unfiltered-reconciliation"
        ),
        last_completed="pass-2/year=2025/type=all/page=0",
    )

    assert result["complete"] is False
    error = result["error"]
    for field in (
        "requested_url",
        "pass_number",
        "partition",
        "year",
        "notice_type",
        "requested_page",
        "final_url",
        "http_status",
        "content_length",
        "active_page",
        "zero_shape",
        "row_count",
        "unresolved_count",
        "pager_mode",
        "page_declared",
        "last_completed",
    ):
        assert f'"{field}"' in error
    assert "secret-token" not in error
    assert "other-secret" not in error
    assert "_finra_pass=REDACTED" in error
    assert '"pass_number":"2"' in error
    assert '"requested_page":0' in error
    assert (
        '"partition":"unfiltered-reconciliation"' in error
        if case == "unfiltered"
        else '"year":"2026"' in error
    )


def test_finra_malformed_pager_fails_closed(monkeypatch):
    """A pager with an unparseable page value is not silently treated as page one."""
    listing_html = """
    <nav aria-labelledby="pagination-heading">
      <ul class="pagination"><li><a href="?page=not-a-number">Next</a></li></ul>
    </nav>
    <a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>
    """

    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda _url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing_html,
            "final_url": regulatory_monitor.FINRA_NOTICES_URL,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
    )

    assert result.complete is False
    assert "pagination metadata" in result.error


def test_finra_authoritative_single_page_and_unfiltered_zero_result_shapes(
    monkeypatch,
):
    """Explicit pager markup completes; unfiltered pager-less zero fails closed."""
    detail = _finra_detail_page("Notice title", "2026-07-24", "Summary text.")
    requested = []

    def fake_single_page(url, _session, **_kwargs):
        requested.append(url)
        if _finra_request_base(url) == regulatory_monitor.FINRA_NOTICES_URL:
            content = """
            <nav aria-labelledby="pagination-heading">
              <ul class="pagination">
                <li class="page-item active"><span class="page-link">1</span></li>
              </ul>
            </nav>
            <a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>
            """
        else:
            content = detail
        return {"status_code": 200, "content": content, "final_url": url,
                "was_redirected": False, "error": None}

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_single_page)
    one_page = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )
    assert one_page.complete is True
    assert one_page.declared_pages == 1

    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": '<div class="view-empty">No results found.</div>',
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    zero = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )
    assert zero.complete is False
    assert "pagination metadata" in zero.error


def test_finra_known_notice_outside_listing_proof_is_pruned(monkeypatch):
    """A prior refresh target absent from the complete listing is removed."""
    listing = _finra_listing_page(
        0, 1, [("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")]
    )
    details = {
        "https://www.finra.org/rules-guidance/notices/26-15": _finra_detail_page(
            "Current notice", "2026-07-24", "Current summary."
        ),
        "https://www.finra.org/rules-guidance/notices/26-14": _finra_detail_page(
            "Edited old notice", "2026-07-09", "Edited background."
        ),
    }
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        return {
            "status_code": 200,
            "content": listing if base_url == regulatory_monitor.FINRA_NOTICES_URL
            else details[base_url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        since_date="2026-07-24",
        known_urls=["https://www.finra.org/rules-guidance/notices/26-14"],
    )

    assert result.complete is True
    assert {item.document_id for item in result} == {"FINRA 26-15"}
    assert "https://www.finra.org/rules-guidance/notices/26-14" not in requested


def test_finra_known_node_refresh_uses_independent_listing_binding(monkeypatch):
    """A known node is proof-bound when its listing URL maps to that node."""
    listing_url = "https://www.finra.org/rules-guidance/notices/26-14"
    node_url = "https://www.finra.org/node/382806"
    listing = _finra_listing_page(
        0, 1, [("/rules-guidance/notices/26-14", "Regulatory Notice 26-14", "2026-07-09")]
    )
    detail = _finra_detail_page(
        "Current notice", "2026-07-09", "Current summary."
    ).replace(
        "</body>", '<link rel="shortlink" href="/node/382806"></body>'
    )
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        is_listing = base_url == regulatory_monitor.FINRA_NOTICES_URL
        return {
            "status_code": 200,
            "content": listing if is_listing else detail,
            "final_url": url if is_listing else node_url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        known_urls=[node_url],
        fallback_urls={listing_url: node_url},
    )

    assert result.complete is True
    assert [item.document_id for item in result] == [node_url]
    assert node_url not in requested


def test_main_rejects_detail_state_not_reconstructable_from_listing_proofs(
    monkeypatch,
):
    """A falsely complete known refresh cannot report or save invalid state."""
    listed = _make_item(
        "FINRA Notice 26-15",
        "FINRA 26-15",
        source="FINRA",
        agency="FINRA",
        url="https://www.finra.org/rules-guidance/notices/26-15",
    )
    outside_listing = _make_item(
        "FINRA Notice 26-14",
        "FINRA 26-14",
        source="FINRA",
        agency="FINRA",
        url="https://www.finra.org/rules-guidance/notices/26-14",
    )
    fetched_identities = ["FINRA 26-14", "FINRA 26-15"]
    divergent = regulatory_monitor.FetchResult(
        [listed, outside_listing],
        complete=True,
        coverage={
            "complete": True,
            "listing_mode": "complete-unfiltered",
            "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
            "listing_record_count": 1,
            "pages_fetched": 1,
            "declared_pages": 1,
            "detail_count": 2,
            "page_numbers": [0],
            "page_identities": [
                {"requested": 0, "final": 0, "active": 0},
            ],
            "fetched_entry_identities": fetched_identities,
            "fetched_entry_identity_digest": (
                regulatory_monitor._identity_digest(fetched_identities)
            ),
            "entry_identity_digest": (
                regulatory_monitor._identity_digest(fetched_identities)
            ),
            "alias_ledger": [],
            "alias_ledger_digest": (
                regulatory_monitor._alias_ledger_digest([])
            ),
            "detail_identity_proofs": [],
            "detail_identity_proof_digest": (
                regulatory_monitor._finra_detail_identity_proof_digest([])
            ),
            "detail_identity_anchor": None,
            "raw_row_count": 1,
            "resolved_row_count": 1,
            "unresolved_row_count": 0,
            "unique_node_count": 1,
            "pass_proofs": _synthetic_pass_proofs(["FINRA 26-15"]),
            "duplicate_ledger": [],
            "date_resolution_ledger": [],
            "conflict_ledger": [],
        },
    )
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": {
                    outside_listing.document_id: _item_hash(outside_listing),
                },
                "refresh_cursor": 0,
            },
        },
    }

    code, saved_state, report_items = _run_main(
        monkeypatch,
        state=state,
        fed_items=[],
        finra_items=divergent,
        args=["--source", "finra"],
    )

    assert code == 2
    assert saved_state is None
    assert report_items is None


def test_finra_known_refresh_is_bounded_and_resumable():
    """Known historical URLs advance through a deterministic round-robin batch."""
    source_state = {
        "entries": {
            f"FINRA 26-{number:02d}": "sha256:old"
            for number in range(1, 41)
        },
        "refresh_cursor": 39,
    }

    batch = regulatory_monitor._finra_refresh_batch(source_state)

    assert len(batch) == regulatory_monitor.FINRA_REFRESH_BATCH_SIZE
    assert batch[0].endswith("/26-40")
    assert batch[1].endswith("/26-01")
    assert len(set(batch)) == len(batch)


def test_finra_alias_pruning_retains_node_keys_and_prunes_absent_url_sources():
    state = {
        "coverage": {
            "alias_ledger": [
                _alias(
                    "node:12345",
                    "https://www.finra.org/node/99999",
                    "sha256:node",
                ),
                _alias(
                    "FINRA 26-01",
                    "https://www.finra.org/node/99998",
                    "sha256:url",
                ),
            ]
        }
    }

    retained = regulatory_monitor._finra_pruned_alias_ledger(
        state,
        set(),
    )

    assert [item["old_identity"] for item in retained] == ["node:12345"]


def test_finra_refresh_ring_sweeps_alias_and_fallback_urls():
    urls = [
        f"https://www.finra.org/rules-guidance/notices/26-{index:02d}"
        for index in range(1, 31)
    ]
    state = {
        "entries": {
            f"https://www.finra.org/node/{1000 + index}": "sha256:old"
            for index in range(30)
        },
        "fallback_urls": {
            url: f"https://www.finra.org/node/{1000 + index}"
            for index, url in enumerate(urls)
        },
        "coverage": {"alias_ledger": []},
        "refresh_cursor": 0,
    }
    selected = []
    for _ in range(2):
        batch = regulatory_monitor._finra_refresh_batch(state)
        selected.extend(batch)
        state["refresh_cursor"] = (
            state["refresh_cursor"] + len(batch)
        ) % len(urls)

    assert set(selected) == set(urls)


def test_finra_legacy_identity_resurfacing_carries_canonical_entry():
    url = "https://www.finra.org/rules-guidance/notices/26-01"
    row = _synthetic_finra_row(
        url,
        "url:/rules-guidance/notices/26-01",
    )
    canonical = "https://www.finra.org/node/99999"
    state = {
        "entries": {canonical: "sha256:canonical"},
        "fallback_urls": {url: canonical},
        "coverage": {
            "alias_ledger": [
                _alias("FINRA 26-01", canonical, "sha256:canonical")
            ],
            "pass_proofs": [
                {"page_row_payloads": [[deepcopy(row["raw_payload"])]]},
            ],
        },
    }

    plan = regulatory_monitor._plan_finra_detail_refresh(
        [row],
        state,
        [],
        limit=None,
    )

    assert plan["fetch_rows"] == []
    assert plan["carried_entries"] == {canonical: "sha256:canonical"}


def test_finra_cursor_advances_across_unrepresented_scheduled_batch():
    rows, state = _bounded_detail_fixture(40, cursor=0)
    scheduled = regulatory_monitor._finra_refresh_batch(state)
    represented = rows[25:]

    plan = regulatory_monitor._plan_finra_detail_refresh(
        represented,
        state,
        scheduled,
        limit=None,
    )

    assert plan["scheduled_current_urls"] == []
    assert plan["scheduled_skipped_urls"] == scheduled
    assert plan["refresh_cursor_output"] == 25


def test_finra_removal_plan_prunes_only_absent_canonical_identity():
    rows, state = _bounded_detail_fixture(3)
    removed_row = rows.pop()
    removed_identity = removed_row["detail_url"]

    plan = regulatory_monitor._plan_finra_detail_refresh(
        rows,
        state,
        [],
        limit=None,
    )

    assert [record["prior_canonical_identity"] for record in plan[
        "removal_candidates"
    ]] == [removed_identity]
    assert plan["removal_candidates"][0]["prior_hash"] == state[
        "entries"
    ][removed_identity]


def test_finra_fallback_represented_node_is_not_removed():
    url = "https://www.finra.org/rules-guidance/notices/26-01"
    canonical = "https://www.finra.org/node/99999"
    row = _synthetic_finra_row(
        url,
        "url:/rules-guidance/notices/26-01",
    )
    state = {
        "entries": {canonical: "sha256:canonical"},
        "fallback_urls": {url: canonical},
        "coverage": {
            "alias_ledger": [],
            "pass_proofs": [
                {"page_row_payloads": [[deepcopy(row["raw_payload"])]]}
            ],
        },
    }

    plan = regulatory_monitor._plan_finra_detail_refresh(
        [row],
        state,
        [],
        limit=None,
    )

    assert plan["removal_candidates"] == []
    assert plan["carried_entries"] == {canonical: "sha256:canonical"}


def test_finra_no_removal_evidence_when_prior_and_current_sets_match():
    rows, state = _bounded_detail_fixture(3)

    plan = regulatory_monitor._plan_finra_detail_refresh(
        rows,
        state,
        [],
        limit=None,
    )

    assert plan["removal_candidates"] == []


def test_finra_removed_identity_reappears_as_forced_new_fetch():
    rows, state = _bounded_detail_fixture(2)
    removed = rows.pop()
    state["entries"].pop(removed["detail_url"])
    state["fallback_urls"].pop(removed["detail_url"])

    plan = regulatory_monitor._plan_finra_detail_refresh(
        [removed],
        state,
        [],
        limit=None,
    )

    assert plan["fetch_rows"] == [removed]
    assert "new-listing-identity" in plan["forced_fetch_reasons"][
        removed["detail_url"]
    ]


def _bounded_detail_fixture(count=100, *, cursor=0):
    rows = []
    entries = {}
    fallbacks = {}
    payloads = []
    for index in range(count):
        url = (
            "https://www.finra.org/rules-guidance/notices/"
            f"information-notice-{20000000 + index}"
        )
        row = _synthetic_finra_row(
            url,
            f"url:{urlparse(url).path}",
            title=f"Information Notice {index}",
        )
        rows.append(row)
        entries[url] = f"sha256:{index:064x}"
        fallbacks[url] = f"https://www.finra.org/node/{100000 + index}"
        payloads.append(row["raw_payload"])
    state = {
        "entries": entries,
        "fallback_urls": fallbacks,
        "refresh_cursor": cursor,
        "coverage": {
            "alias_ledger": [],
            "pass_proofs": [
                {"page_row_payloads": [deepcopy(payloads)]},
                {"page_row_payloads": [deepcopy(payloads)]},
            ],
        },
    }
    return rows, state


def test_finra_bounded_detail_plan_limits_3600_entries_to_refresh_batch():
    rows, state = _bounded_detail_fixture(3600)
    scheduled = regulatory_monitor._finra_refresh_batch(state)

    plan = regulatory_monitor._plan_finra_detail_refresh(
        rows,
        state,
        scheduled,
        limit=None,
    )

    assert len(plan["fetch_rows"]) == regulatory_monitor.FINRA_REFRESH_BATCH_SIZE
    assert len(plan["carried_entries"]) == 3575
    assert len(plan["fetch_rows"]) < len(rows)
    assert all(
        plan["forced_fetch_reasons"][url] == ["scheduled-refresh"]
        for url in scheduled
    )


def test_finra_bounded_detail_plan_forces_new_and_missing_prior_proof():
    rows, state = _bounded_detail_fixture(3)
    new_row = _synthetic_finra_row(
        "https://www.finra.org/rules-guidance/notices/information-notice-new",
        "url:/rules-guidance/notices/information-notice-new",
    )
    rows.append(new_row)
    state["coverage"]["pass_proofs"][0]["page_row_payloads"][0].pop()
    state["coverage"]["pass_proofs"][1]["page_row_payloads"][0].pop()

    plan = regulatory_monitor._plan_finra_detail_refresh(
        rows,
        state,
        [],
        limit=None,
    )

    reasons = plan["forced_fetch_reasons"]
    assert "new-listing-identity" in reasons[new_row["detail_url"]]
    assert any(
        "listing-evidence-changed" in reason_set
        for reason_set in reasons.values()
    )


def test_finra_bounded_detail_plan_prunes_removed_identity_and_advances_cursor():
    rows, state = _bounded_detail_fixture(40, cursor=39)
    removed = rows.pop()
    scheduled = regulatory_monitor._finra_refresh_batch(state)

    plan = regulatory_monitor._plan_finra_detail_refresh(
        rows,
        state,
        scheduled,
        limit=None,
    )

    assert removed["detail_url"] not in plan["current_listing_identities"]
    scheduled_current = [
        url for url in scheduled
        if url != removed["detail_url"]
    ]
    assert plan["refresh_cursor_output"] == (
        (39 + len(scheduled_current)) % 39
    )


def test_finra_bounded_detail_refresh_carries_hashes_and_reports_changed_item(
    monkeypatch,
):
    urls = [
        f"https://www.finra.org/rules-guidance/notices/26-0{index}"
        for index in (1, 2, 3)
    ]
    rows = [
        _synthetic_finra_row(
            url,
            f"url:{urlparse(url).path}",
            title=f"Regulatory Notice 26-0{index}",
        )
        for index, url in enumerate(urls, start=1)
    ]
    listing = _synthetic_finra_listing(rows)
    prior_items = [
        _make_item(
            f"Regulatory Notice 26-0{index}",
            f"FINRA 26-0{index}",
            source="FINRA",
            agency="FINRA",
            url=url,
            abstract=f"Prior content {index}",
        )
        for index, url in enumerate(urls, start=1)
    ]
    prior_state = {
        "entries": {
            item.document_id: _item_hash(item)
            for item in prior_items
        },
        "fallback_urls": {
            url: f"https://www.finra.org/node/{380000 + index}"
            for index, url in enumerate(urls, start=1)
        },
        "refresh_cursor": 0,
        "coverage": {
            "alias_ledger": [],
            "pass_proofs": listing["coverage"]["pass_proofs"],
        },
    }
    requested = []
    sleeps = []
    session = _FakeSession([])
    session._finra_skip_phase_cooldown = False
    session._finra_cooldown_until = 9999.0
    session._finra_backoff_seconds = 60
    session._finra_request_interval_seconds = 60
    session._finra_last_request_at = 9999.0
    monkeypatch.setattr(regulatory_monitor.time, "sleep", sleeps.append)
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_records",
        lambda *_args: listing,
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_page",
        lambda url, _session, **_kwargs: (
            requested.append(url)
            or {
                "status_code": 200,
                "content": _finra_detail_page(
                    "Regulatory Notice 26-01",
                    rows[0]["listing_date"] or "2026-01-01",
                    "Changed refreshed content.",
                ),
                "final_url": url,
                "url": url,
                "was_redirected": False,
                "error": None,
            }
        ),
    )

    result = regulatory_monitor.fetch_finra_notices(
        session,
        {"regulatory": {}, "keyword_control_map": []},
        known_urls=[urls[0]],
        fallback_urls=prior_state["fallback_urls"],
        prior_source_state=prior_state,
    )

    assert result.complete is True
    assert sleeps == [1800]
    assert requested == [urls[0]]
    assert len(result) == 1
    assert result.coverage["detail_mode"] == "bounded-refresh"
    assert len(result.coverage["carried_entry_identities"]) == 2
    assert len(result.coverage["fetched_entry_identities"]) == 3
    assert result.coverage["detail_phase_cooldown_seconds"] == 1800
    assert (
        result.coverage["detail_phase_start_marker"]
        == "phase-cooldown-complete"
    )
    assert session._finra_cooldown_until == 0.0
    assert session._finra_backoff_seconds == (
        regulatory_monitor.FINRA_RETRY_BASE_WAIT_SECONDS
    )
    assert session._finra_request_interval_seconds == 1.0
    assert session._finra_last_request_at == 0.0
    assert regulatory_monitor.check_for_new_items(
        regulatory_monitor.SOURCE_KEY_FINRA,
        list(result),
        prior_state,
    ) == list(result)

    state = {
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: deepcopy(prior_state)
        }
    }
    regulatory_monitor.update_source_state(
        regulatory_monitor.SOURCE_KEY_FINRA,
        list(result),
        state,
        refreshed_urls=[urls[0]],
        fallback_urls=result.fallback_urls,
        coverage=result.coverage,
    )
    persisted = state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    assert len(persisted["entries"]) == 3
    assert persisted["refresh_cursor"] == 1


def test_finra_zero_detail_plan_has_no_phase_cooldown(monkeypatch):
    rows, prior = _bounded_detail_fixture(2)
    listing = _synthetic_finra_listing(rows)
    sleeps = []
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_records",
        lambda *_args: listing,
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_page",
        lambda *_args, **_kwargs: pytest.fail(
            "zero-detail plan must not fetch"
        ),
    )
    monkeypatch.setattr(regulatory_monitor.time, "sleep", sleeps.append)

    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        prior_source_state=prior,
    )

    assert result.complete is True
    assert sleeps == []
    assert result.coverage["expected_detail_request_count"] == 0
    assert result.coverage["detail_phase_cooldown_seconds"] == 0
    assert (
        result.coverage["detail_phase_start_marker"]
        == "no-detail-requests"
    )


def test_finra_bounded_detail_carried_hash_tampering_is_rejected():
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    coverage = source_state["coverage"]
    identities = sorted(source_state["entries"])
    listing_identities = sorted({
        regulatory_monitor._extract_finra_document_id(url)
        for url in regulatory_monitor._finra_retained_listing_detail_urls(
            coverage["pass_proofs"]
        )
    })
    coverage.update({
        "schema_version": 2,
        "listing_mode": "deterministic-year-type-partitions",
        "detail_mode": "bounded-refresh",
        "refreshed_entry_identities": [],
        "refreshed_urls": [],
        "carried_entry_identities": identities,
        "carried_entry_hash_digest": "sha256:forged",
        "current_listing_identities": listing_identities,
        "current_listing_identity_digest": (
            regulatory_monitor._identity_digest(listing_identities)
        ),
        "refresh_cursor_input": 0,
        "refresh_cursor_output": 0,
        "forced_fetch_reasons": {},
        "expected_detail_request_count": 0,
        "detail_phase_cooldown_seconds": 0,
        "detail_phase_start_marker": "no-detail-requests",
    })

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any("carried entry hash digest is invalid" in error for error in errors)


def test_finra_detail_phase_cooldown_tampering_is_rejected():
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    coverage = source_state["coverage"]
    coverage.update({
        "schema_version": 2,
        "listing_mode": "deterministic-year-type-partitions",
        "detail_mode": "bounded-refresh",
        "refreshed_entry_identities": [],
        "refreshed_urls": [],
        "carried_entry_identities": sorted(source_state["entries"]),
        "carried_entry_hash_digest": compute_hash(json.dumps(
            sorted(source_state["entries"].items()),
            ensure_ascii=False,
            separators=(",", ":"),
        )),
        "current_listing_identities": sorted(source_state["entries"]),
        "current_listing_identity_digest": (
            regulatory_monitor._identity_digest(source_state["entries"])
        ),
        "refresh_cursor_input": 0,
        "refresh_cursor_output": 0,
        "refresh_ring_urls": [],
        "skipped_scheduled_urls": [],
        "forced_fetch_reasons": {},
        "expected_detail_request_count": 0,
        "detail_phase_cooldown_seconds": 1800,
        "detail_phase_start_marker": "phase-cooldown-complete",
    })

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any(
        "detail phase cooldown evidence is invalid" in error
        for error in errors
    )


def test_finra_limited_result_never_exposes_private_complete_hashes(monkeypatch):
    url = "https://www.finra.org/rules-guidance/notices/26-01"
    row = _synthetic_finra_row(
        url,
        "url:/rules-guidance/notices/26-01",
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_records",
        lambda *_args: _synthetic_finra_listing([row]),
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_page",
        lambda requested_url, _session, **_kwargs: {
            "status_code": 200,
            "content": _finra_detail_page(
                "Regulatory Notice 26-01",
                row["listing_date"] or "2026-01-01",
                "Limited content.",
            ),
            "final_url": requested_url,
            "url": requested_url,
            "was_redirected": False,
            "error": None,
        },
    )
    sleeps = []
    monkeypatch.setattr(regulatory_monitor.time, "sleep", sleeps.append)

    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        limit=1,
    )

    assert result.complete is False
    assert "_complete_entry_hashes" not in result.coverage
    assert 1800 not in sleeps
    assert result.coverage["detail_phase_cooldown_seconds"] == 0


def test_finra_validated_legacy_migration_carries_historical_archive():
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    prior = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    rows = [
        _synthetic_finra_row(
            url,
            f"url:{urlparse(url).path}",
            title=f"Historical notice {index}",
        )
        for index, url in enumerate(
            sorted(prior["fallback_urls"]),
            start=1,
        )
    ]
    new_url = (
        "https://www.finra.org/rules-guidance/notices/26-16"
    )
    rows.append(_synthetic_finra_row(
        new_url,
        "url:/rules-guidance/notices/26-16",
        title="Regulatory Notice 26-16",
    ))
    scheduled = regulatory_monitor._finra_refresh_batch(prior)

    plan = regulatory_monitor._plan_finra_detail_refresh(
        rows,
        prior,
        scheduled,
        limit=None,
        prior_state_validated=True,
    )

    assert any(
        row["detail_url"] == new_url for row in plan["fetch_rows"]
    )
    assert len(plan["fetch_rows"]) <= (
        regulatory_monitor.FINRA_REFRESH_BATCH_SIZE + 1 + 120
    )
    assert len(plan["fetch_rows"]) < 500
    assert len(plan["legacy_migration_bindings"]) > 3000
    assert plan["forced_fetch_reasons"][new_url] == [
        "missing-prior-canonical-hash",
        "missing-prior-identity-binding",
        "new-listing-identity",
    ]


@pytest.mark.parametrize("tamper", ["hash", "fallback", "alias"])
def test_finra_legacy_migration_tampering_forces_detail_fetch(tamper):
    row, prior = _bounded_detail_fixture(1)
    prior["coverage"].update({
        "schema_version": 1,
        "listing_mode": "complete-unfiltered",
        "complete": True,
    })
    url = row[0]["detail_url"]
    identity = next(iter(prior["entries"]))
    if tamper == "hash":
        prior["entries"][identity] = ""
    elif tamper == "fallback":
        prior["fallback_urls"].pop(url)
    else:
        prior["coverage"]["alias_ledger"] = [
            _alias(identity, "https://www.finra.org/node/99999", "sha256:x")
        ]

    plan = regulatory_monitor._plan_finra_detail_refresh(
        row,
        prior,
        [],
        limit=None,
        prior_state_validated=True,
    )

    assert plan["fetch_rows"] == row
    assert not plan["legacy_migration_bindings"]


def test_finra_second_v2_run_has_no_legacy_migration_marker():
    rows, prior = _bounded_detail_fixture(3)
    prior["coverage"].update({
        "schema_version": 2,
        "listing_mode": "deterministic-year-type-partitions",
        "complete": True,
    })

    plan = regulatory_monitor._plan_finra_detail_refresh(
        rows,
        prior,
        [],
        limit=None,
        prior_state_validated=True,
    )

    assert plan["legacy_migration_mode"] is False
    assert plan["legacy_migration_bindings"] == []


def test_finra_hashes_and_classifies_non_summary_edits(monkeypatch):
    """Changes in Action Required/Background content affect provenance and tier."""
    listing = _finra_listing_page(
        0, 1, [("/rules-guidance/notices/26-14", "Regulatory Notice 26-14", "2026-07-09")]
    )
    base_detail = """
    <main><h1>Notice</h1>
      <div class="field--name-field-core-official-dt"><time datetime="2026-07-09T00:00:00Z"></time></div>
      <div class="field--name-body"><h2>Summary</h2><p>Stable summary.</p>
      <h2>Action Required</h2><p>Stable action.</p>
      <h2>Background &amp; Discussion</h2><p>Stable background.</p>
      <h2>Endnotes</h2><p>Stable note.</p></div>
    </main>
    """
    edited_detail = base_detail.replace("Stable background.", "urgent marker in the background.")
    pages = {regulatory_monitor.FINRA_NOTICES_URL: listing}

    def run(detail):
        pages["https://www.finra.org/rules-guidance/notices/26-14"] = detail
        monkeypatch.setattr(
            regulatory_monitor,
            "fetch_page",
            lambda url, _session, **_kwargs: {
                "status_code": 200,
                "content": pages[_finra_request_base(url)],
                "final_url": url,
                "was_redirected": False,
                "error": None,
            },
        )
        return regulatory_monitor.fetch_finra_notices(
            _FakeSession([]),
            {
                "regulatory": {
                    "critical_patterns": [
                        {"pattern": r"urgent marker", "reason": "Urgent notice content"}
                    ]
                },
                "keyword_control_map": [],
            },
        )[0]

    first = run(base_detail)
    second = run(edited_detail)
    assert "Background & Discussion" in first.substantive_content
    assert "Endnotes" in first.substantive_content
    assert regulatory_monitor._item_content_hash(first) != regulatory_monitor._item_content_hash(second)
    assert second.classification == regulatory_monitor.CLASSIFICATION_CRITICAL


def _finra_canonicalization_fixture(
    *,
    comments: str = "No comments.",
    attachment_href: str = "/sites/default/files/attachment-v1.pdf",
    deadline: str = "09/11/2026",
    contact_href: str = "",
    formatted: bool = False,
) -> str:
    """Build a notice with separate mutable comments and authoritative content."""
    action = (
        "<p>Action <strong>required</strong>.</p>"
        if formatted
        else "<p>Action required.</p>"
    )
    contact = (
        f'<p>Contact <a href="{contact_href}">FINRA staff</a>.</p>'
        if contact_href
        else ""
    )
    return f"""
    <html><body>
      <h1>Regulatory Notice 26-14</h1>
      <div class="field--name-field-core-official-dt">
        <time datetime="2026-07-09T00:00:00Z"></time>
      </div>
      <div class="field--name-field-notice-subtitle-tx">
        Comment Period Expires: {deadline}
      </div>
      <div id="notice" class="tab-pane">
        <h2>Summary</h2><p>Stable authoritative summary.</p>
        <h2>Action Required</h2>{action}
        {contact}
        <h2>Endnotes</h2>
        <p><a href="#_ednref1">1</a> Authoritative endnote.</p>
      </div>
      <div id="block-noticeattachment">
        <a href="{attachment_href}?utm_source=tracking">Attachment A</a>
      </div>
      <div id="comments" class="tab-pane">
        <h2>Comments (1)</h2><p>{comments}</p>
      </div>
    </body></html>
    """


def test_finra_comments_do_not_change_authoritative_hash_or_classification():
    """Mutable public comments must be excluded from FINRA provenance."""
    base = BeautifulSoup(
        _finra_canonicalization_fixture(comments="Alice Example"),
        "html.parser",
    )
    changed = BeautifulSoup(
        _finra_canonicalization_fixture(
            comments="Bob Example: urgent marker; 999 additional comments"
        ),
        "html.parser",
    )

    base_content = regulatory_monitor._extract_finra_substantive_content(base)
    changed_content = regulatory_monitor._extract_finra_substantive_content(changed)
    assert "Alice Example" not in base_content
    assert "Bob Example" not in changed_content
    assert regulatory_monitor.compute_hash(base_content) == (
        regulatory_monitor.compute_hash(changed_content)
    )

    config = {
        "regulatory": {
            "critical_patterns": [
                {"pattern": r"urgent marker", "reason": "Comment-only signal"}
            ]
        }
    }
    assert regulatory_monitor.classify_regulatory_relevance(
        "Regulatory Notice 26-14", base_content, config
    ) == regulatory_monitor.classify_regulatory_relevance(
        "Regulatory Notice 26-14", changed_content, config
    )


def test_finra_canonicalization_preserves_attachment_targets_and_dates():
    """Attachment revisions and substantive deadline revisions change hashes."""
    attachment_v1 = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(
                attachment_href="/sites/default/files/attachment-v1.pdf"
            ),
            "html.parser",
        ),
        "https://www.finra.org/rules-guidance/notices/26-14",
    )
    attachment_v2 = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(
                attachment_href="/sites/default/files/attachment-v2.pdf"
            ),
            "html.parser",
        )
    )
    deadline_v1 = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(deadline="09/11/2026"),
            "html.parser",
        )
    )
    deadline_v2 = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(deadline="09/25/2026"),
            "html.parser",
        )
    )

    assert "attachment-v1.pdf" in attachment_v1
    assert "notices/26-14#_ednref1" in attachment_v1
    assert "2026-09-11" in deadline_v1
    assert regulatory_monitor.compute_hash(attachment_v1) != (
        regulatory_monitor.compute_hash(attachment_v2)
    )
    assert regulatory_monitor.compute_hash(deadline_v1) != (
        regulatory_monitor.compute_hash(deadline_v2)
    )


def test_finra_canonicalization_ignores_formatting_and_tracking_noise():
    """Markup-only and tracking-query changes must not create provenance churn."""
    plain = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(
                attachment_href="/sites/default/files/attachment-v1.pdf"
            ),
            "html.parser",
        )
    )
    formatted = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(
                attachment_href="/sites/default/files/attachment-v1.pdf",
                formatted=True,
            ),
            "html.parser",
        )
    )

    assert regulatory_monitor.compute_hash(plain) == (
        regulatory_monitor.compute_hash(formatted)
    )


def _cloudflare_email_href(email: str, key: int) -> str:
    """Encode a fixture email using Cloudflare's XOR email-protection format."""
    encoded = bytes(ord(character) ^ key for character in email)
    return (
        "https://www.finra.org/cdn-cgi/l/email-protection#"
        f"{key:02x}{encoded.hex()}"
    )


def test_finra_cloudflare_email_tokens_are_canonicalized_before_hashing():
    """Randomized Cloudflare tokens for one email must not churn provenance."""
    token_v1 = _cloudflare_email_href("notices@example.test", 0x12)
    token_v2 = _cloudflare_email_href("notices@example.test", 0xA7)
    different_email = _cloudflare_email_href("changed@example.test", 0x12)

    def content(token):
        return regulatory_monitor._extract_finra_substantive_content(
            BeautifulSoup(
                _finra_canonicalization_fixture(contact_href=token),
                "html.parser",
            ),
            "https://www.finra.org/rules-guidance/notices/26-14",
        )

    content_v1 = content(token_v1)
    content_v2 = content(token_v2)
    content_different = content(different_email)

    assert "mailto:notices@example.test" in content_v1
    assert regulatory_monitor.compute_hash(content_v1) == (
        regulatory_monitor.compute_hash(content_v2)
    )
    assert regulatory_monitor.compute_hash(content_v1) != (
        regulatory_monitor.compute_hash(content_different)
    )


def test_finra_rate_limit_retry_resumes_same_url(monkeypatch):
    """A transient 429 honors Retry-After and retries the exact URL."""
    responses = [
        {"status_code": 429, "content": "", "final_url": "https://example.test/finra",
         "was_redirected": False, "error": "rate limited", "retry_after": 60},
        {"status_code": 200, "content": "ok", "final_url": "https://example.test/finra",
         "was_redirected": False, "error": None},
    ]
    sleeps = []
    calls = []

    def fake_fetch_page(url, _session, **kwargs):
        calls.append(url)
        calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", sleeps.append)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: 0.0)

    result = regulatory_monitor._fetch_finra_page("https://example.test/finra", _FakeSession([]))

    assert result["status_code"] == 200
    assert responses == []
    assert regulatory_monitor.FINRA_REQUEST_INTERVAL_SECONDS in sleeps
    assert 60 in sleeps
    assert calls[0] == "https://example.test/finra"
    assert calls[1]["max_retries"] == 1
    assert calls[2] == "https://example.test/finra"
    assert calls[3]["max_retries"] == 1


def test_finra_rate_limit_preserves_listing_page_url(monkeypatch):
    """A 429 on page 1 must retry page 1, never page 0 or a slash variant."""
    responses = [
        {
            "status_code": 429,
            "content": "",
            "final_url": "https://example.test/finra?page=1",
            "was_redirected": False,
            "error": "rate limited",
            "retry_after": 0,
        },
        {
            "status_code": 200,
            "content": "notice",
            "final_url": "https://example.test/finra?page=1",
            "was_redirected": False,
            "error": None,
        },
    ]
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        return responses.pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: 0.0)

    result = regulatory_monitor._fetch_finra_page(
        "https://example.test/finra?page=1", _FakeSession([])
    )

    assert result["status_code"] == 200
    assert requested == [
        "https://example.test/finra?page=1",
        "https://example.test/finra?page=1",
    ]


def test_finra_rate_limit_exhaustion_reports_aggregate_attempts(monkeypatch):
    """The terminal 429 reports the FINRA retry loop, not one inner attempt."""
    responses = [
        {
            "status_code": 429,
            "content": "",
            "final_url": "https://example.test/finra?page=6",
            "was_redirected": False,
            "error": "rate limited after 1 attempt",
            "retry_after": 0,
        }
        for _ in range(regulatory_monitor.FINRA_MAX_RETRY_ATTEMPTS)
    ]
    requested = []

    def fake_fetch_page(url, _session, **kwargs):
        requested.append((url, kwargs))
        return responses.pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: 0.0)

    result = regulatory_monitor._fetch_finra_page(
        "https://example.test/finra?page=6", _FakeSession([])
    )

    assert result["status_code"] == 429
    assert result["error"] == "rate limited after 6 attempts"
    assert len(requested) == regulatory_monitor.FINRA_MAX_RETRY_ATTEMPTS
    assert all(
        url == "https://example.test/finra?page=6"
        and kwargs["max_retries"] == 1
        for url, kwargs in requested
    )


def test_finra_rate_limit_uses_persisted_authoritative_node_fallback(monkeypatch):
    """A learned FINRA node shortlink can recover a canonical-page 429."""
    canonical = "https://www.finra.org/rules-guidance/notices/26-14"
    node_url = "https://www.finra.org/node/382806"
    listing = _finra_listing_page(
        0, 1, [("/rules-guidance/notices/26-14", "Regulatory Notice 26-14", "2026-07-09")]
    )
    detail = _finra_detail_page("Regulatory Notice 26-14", "2026-07-09", "Stable content.")
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        if base_url == regulatory_monitor.FINRA_NOTICES_URL:
            content = listing
            status = 200
        elif base_url == node_url:
            content = detail
            status = 200
        else:
            content = ""
            status = 429
        return {
            "status_code": status,
            "content": content,
            "final_url": url,
            "was_redirected": False,
            "error": "rate limited" if status == 429 else None,
            "retry_after": 0,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", lambda _seconds: None)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        fallback_urls={canonical: node_url},
    )

    assert result.complete is True
    assert result[0].url == canonical
    assert node_url in requested
    assert requested.count(canonical) == 1
    assert result.fallback_urls[canonical] == node_url
    state = {"sources": {regulatory_monitor.SOURCE_KEY_FINRA: {"entries": {}}}}
    regulatory_monitor.update_source_state(
        regulatory_monitor.SOURCE_KEY_FINRA,
        list(result),
        state,
        fallback_urls=result.fallback_urls,
    )
    assert state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["fallback_urls"] == {
        canonical: node_url
    }


def test_finra_node_transport_fallback_preserves_canonical_identity(monkeypatch):
    """A node-URL transport fallback must not rewrite an existing notice identity."""
    canonical = "https://www.finra.org/rules-guidance/notices/26-14"
    node_url = "https://www.finra.org/node/382806"
    listing = _finra_listing_page(
        0, 1, [("/rules-guidance/notices/26-14", "Regulatory Notice 26-14", "2026-07-09")]
    )
    detail = _finra_detail_page(
        "Regulatory Notice 26-14", "2026-07-09", "Updated content."
    )

    def fake_fetch_page(url, _session, **_kwargs):
        base_url = _finra_request_base(url)
        if base_url == regulatory_monitor.FINRA_NOTICES_URL:
            content, status = listing, 200
        elif base_url == node_url:
            content, status = detail, 200
        else:
            content, status = "", 429
        return {
            "status_code": status,
            "content": content,
            "final_url": url,
            "was_redirected": False,
            "error": "rate limited" if status == 429 else None,
            "retry_after": 0,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", lambda _seconds: None)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        fallback_urls={canonical: node_url},
    )

    assert result.complete is True
    assert result[0].document_id == "FINRA 26-14"
    assert result[0].url == canonical
    assert result.coverage["fetched_entry_identities"] == ["FINRA 26-14"]

    # The existing canonical entry updates in place: no orphaned identity, no
    # alias migration, and the change is still reported as an update.
    finra_state = {
        "entries": {"FINRA 26-14": "sha256:previous"},
        "coverage": {"alias_ledger": []},
    }
    state = {"sources": {regulatory_monitor.SOURCE_KEY_FINRA: finra_state}}
    new_items = regulatory_monitor.check_for_new_items(
        regulatory_monitor.SOURCE_KEY_FINRA, list(result), finra_state
    )
    assert [item.document_id for item in new_items] == ["FINRA 26-14"]

    regulatory_monitor.update_source_state(
        regulatory_monitor.SOURCE_KEY_FINRA,
        list(result),
        state,
        fallback_urls=result.fallback_urls,
        coverage=deepcopy(dict(result.coverage)),
    )
    persisted = state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    assert set(persisted["entries"]) == {"FINRA 26-14"}
    assert persisted["entries"]["FINRA 26-14"] != "sha256:previous"
    assert persisted["coverage"]["alias_ledger"] == []
    assert persisted["fallback_urls"] == {canonical: node_url}

    # Alias migration stays fail closed: an identity that leaves the complete
    # crawl without explicit evidence still refuses to persist.
    orphaned = {
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "entries": {
                    "FINRA 26-14": "sha256:previous",
                    "FINRA 26-13": "sha256:orphan",
                },
                "coverage": {"alias_ledger": []},
            }
        }
    }
    with pytest.raises(
        ValueError,
        match="removal evidence does not match prior minus current identities",
    ):
        regulatory_monitor.update_source_state(
            regulatory_monitor.SOURCE_KEY_FINRA,
            list(result),
            orphaned,
            fallback_urls=result.fallback_urls,
            coverage=deepcopy(dict(result.coverage)),
        )


def test_finra_fallback_identity_resolves_through_existing_alias_ledger(
    monkeypatch,
):
    """A fetched identity production already aliased updates its canonical node.

    Blocker 4: with a real, NON-EMPTY alias ledger mapping "FINRA 00-01" to the
    canonical node/6547 entry, a later fetch that surfaces the notice number
    (e.g. via node-transport fallback) must resolve through that trusted alias
    and update the existing canonical node entry in place -- not orphan a fresh
    "FINRA 00-01" entry and strand (or crash on) the canonical node whose only
    reachability is that alias.
    """
    canonical_identity = "https://www.finra.org/node/6547"
    fetched_item = _make_item(
        "Regulatory Notice 00-01",
        "FINRA 00-01",
        source="FINRA",
        agency="FINRA",
        url="https://www.finra.org/rules-guidance/notices/00-01",
        pub_date="2000-01-15",
        abstract="Legacy notice served from a node detail page.",
    )
    canonical_hash = _item_hash(fetched_item)
    notice_url = "https://www.finra.org/rules-guidance/notices/00-01"
    test_anchor = "test-single-alias"
    monkeypatch.setitem(
        regulatory_monitor.FINRA_DETAIL_IDENTITY_ANCHORS,
        test_anchor,
        regulatory_monitor._finra_detail_identity_binding_digest(
            {notice_url: canonical_identity}
        ),
    )

    alias = _alias("FINRA 00-01", canonical_identity, canonical_hash)
    finra_state = {
        "entries": {canonical_identity: canonical_hash},
        "fallback_urls": {
            notice_url: canonical_identity,
        },
        "coverage": {
            "alias_ledger": [alias],
            "detail_identity_anchor": test_anchor,
        },
    }
    state = {"sources": {regulatory_monitor.SOURCE_KEY_FINRA: finra_state}}

    # The caller-supplied coverage carries the RAW fetched identity, exactly as
    # fetch_finra_notices emits it before any prior-ledger resolution.
    coverage = {
        "fetched_entry_identities": ["FINRA 00-01"],
        "fetched_entry_identity_digest": regulatory_monitor._identity_digest(
            ["FINRA 00-01"]
        ),
        "pass_proofs": _synthetic_pass_proofs(["FINRA 00-01"]),
        "detail_identity_proofs": [
            _detail_identity_proof("00-01", canonical_identity),
        ],
    }

    regulatory_monitor.update_source_state(
        regulatory_monitor.SOURCE_KEY_FINRA,
        [fetched_item],
        state,
        coverage=coverage,
    )

    persisted = state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    # The canonical node entry is updated in place; no orphan notice-number key.
    assert set(persisted["entries"]) == {canonical_identity}
    assert "FINRA 00-01" not in persisted["entries"]
    assert persisted["entries"][canonical_identity] == canonical_hash
    # The trusted alias relationship is preserved, not rebuilt into an orphan.
    persisted_ledger = persisted["coverage"]["alias_ledger"]
    assert [item["old_identity"] for item in persisted_ledger] == ["FINRA 00-01"]
    assert persisted_ledger[0]["canonical_identity"] == canonical_identity
    # Coverage identities are updated to the resolved canonical set.
    assert persisted["coverage"]["fetched_entry_identities"] == [canonical_identity]
    assert persisted["coverage"]["fetched_entry_identity_digest"] == (
        regulatory_monitor._identity_digest([canonical_identity])
    )


def test_finra_rate_limit_cooldown_is_shared_across_urls(monkeypatch):
    """A 429 cooldown applies to the next FINRA request, not just one URL."""
    clock = [0.0]
    sleeps = []
    responses = {
        "https://example.test/first": [
            {
                "status_code": 429,
                "content": "",
                "final_url": "https://example.test/first",
                "was_redirected": False,
                "error": "rate limited",
                "retry_after": 10,
            },
            {
                "status_code": 200,
                "content": "first",
                "final_url": "https://example.test/first",
                "was_redirected": False,
                "error": None,
            },
        ],
        "https://example.test/second": [
            {
                "status_code": 200,
                "content": "second",
                "final_url": "https://example.test/second",
                "was_redirected": False,
                "error": None,
            },
        ],
    }

    def fake_sleep(seconds):
        sleeps.append(seconds)
        clock[0] += seconds

    def fake_fetch_page(url, _session, **_kwargs):
        key = url.split("?", 1)[0].rstrip("/")
        return responses[key].pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", fake_sleep)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: clock[0])
    session = _FakeSession([])

    assert regulatory_monitor._fetch_finra_page(
        "https://example.test/first",
        session,
        retain_adaptive_interval=True,
    )["status_code"] == 200
    assert regulatory_monitor._fetch_finra_page(
        "https://example.test/second",
        session,
        retain_adaptive_interval=True,
    )["status_code"] == 200
    assert 10 in sleeps
    assert sleeps.count(10) == 2


def test_finra_rate_limit_recovery_keeps_adaptive_pacing(monkeypatch):
    """A recovered 429 slows later page requests instead of immediately re-throttling."""
    clock = [0.0]
    last_success_at = [None]
    rate_limited_urls = []
    page_one_attempts = [0]

    def fake_sleep(seconds):
        clock[0] += seconds

    def fake_fetch_page(url, _session, **_kwargs):
        if url.endswith("page=1"):
            page_one_attempts[0] += 1
            if page_one_attempts[0] == 1:
                rate_limited_urls.append(url)
                return {
                    "status_code": 429,
                    "content": "",
                    "final_url": url,
                    "was_redirected": False,
                    "error": "rate limited",
                    "retry_after": 5,
                }
        if (
            url.endswith("page=2")
            and last_success_at[0] is not None
            and clock[0] - last_success_at[0] < 5
        ):
            rate_limited_urls.append(url)
            return {
                "status_code": 429,
                "content": "",
                "final_url": url,
                "was_redirected": False,
                "error": "rate limited",
                "retry_after": 5,
            }
        last_success_at[0] = clock[0]
        return {
            "status_code": 200,
            "content": "ok",
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", fake_sleep)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 1)
    session = _FakeSession([])

    for page in range(3):
        result = regulatory_monitor._fetch_finra_page(
            f"https://example.test/finra?page={page}",
            session,
            retain_adaptive_interval=True,
        )
        assert result["status_code"] == 200

    assert rate_limited_urls == ["https://example.test/finra?page=1"]


def test_finra_detail_recovery_returns_to_fast_baseline(monkeypatch):
    """A recovered detail-page 429 must not slow every remaining historical URL."""
    clock = [0.0]
    sleeps = []
    responses = {
        "https://example.test/first": [
            {
                "status_code": 429,
                "content": "",
                "final_url": "https://example.test/first",
                "was_redirected": False,
                "error": "rate limited",
                "retry_after": 10,
            },
            {
                "status_code": 200,
                "content": "first",
                "final_url": "https://example.test/first",
                "was_redirected": False,
                "error": None,
            },
        ],
        "https://example.test/second": [
            {
                "status_code": 200,
                "content": "second",
                "final_url": "https://example.test/second",
                "was_redirected": False,
                "error": None,
            },
        ],
    }

    def fake_sleep(seconds):
        sleeps.append(seconds)
        clock[0] += seconds

    def fake_fetch_page(url, _session, **_kwargs):
        return responses[url].pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", fake_sleep)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: clock[0])
    session = _FakeSession([])

    assert regulatory_monitor._fetch_finra_page(
        "https://example.test/first", session
    )["status_code"] == 200
    assert regulatory_monitor._fetch_finra_page(
        "https://example.test/second", session
    )["status_code"] == 200

    assert sleeps == [1, 10, 1]


def test_finra_listing_pacing_never_exceeds_five_requests_per_rolling_minute(
    monkeypatch,
):
    """Twelve-second pacing avoids a sixth request in any rolling minute."""
    clock = [0.0]
    request_times = []
    rate_limited_urls = []

    def fake_sleep(seconds):
        clock[0] += seconds

    def fake_fetch_page(url, _session, **_kwargs):
        request_times[:] = [
            timestamp
            for timestamp in request_times
            if timestamp > clock[0] - 60
        ]
        if len(request_times) >= 5:
            rate_limited_urls.append(url)
            return {
                "status_code": 429,
                "content": "",
                "final_url": url,
                "was_redirected": False,
                "error": "rate limited",
                "retry_after": 60,
            }
        request_times.append(clock[0])
        return {
            "status_code": 200,
            "content": "ok",
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", fake_sleep)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: clock[0])
    session = _FakeSession([])

    for page in range(6):
        result = regulatory_monitor._fetch_finra_page(
            f"https://example.test/finra?page={page}",
            session,
            min_interval_seconds=(
                regulatory_monitor.FINRA_LISTING_REQUEST_INTERVAL_SECONDS
            ),
        )
        assert result["status_code"] == 200

    assert rate_limited_urls == []


def test_finra_listing_pacing_does_not_slow_detail_requests(monkeypatch):
    """Listing pages use the safe baseline without imposing it on detail fetches."""
    clock = [0.0]
    sleeps = []

    def fake_sleep(seconds):
        sleeps.append(seconds)
        clock[0] += seconds

    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": "ok",
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    monkeypatch.setattr(regulatory_monitor.time, "sleep", fake_sleep)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: clock[0])

    listing_session = _FakeSession([])
    detail_session = _FakeSession([])
    regulatory_monitor._fetch_finra_page(
        "https://example.test/finra?page=0",
        listing_session,
        min_interval_seconds=(
            regulatory_monitor.FINRA_LISTING_REQUEST_INTERVAL_SECONDS
        ),
    )
    clock[0] = 0.0
    regulatory_monitor._fetch_finra_page(
        "https://example.test/finra/detail",
        detail_session,
    )

    assert sleeps == [
        regulatory_monitor.FINRA_LISTING_REQUEST_INTERVAL_SECONDS,
        regulatory_monitor.FINRA_REQUEST_INTERVAL_SECONDS,
    ]


def test_main_does_not_advance_finra_on_detail_failure(monkeypatch):
    """A failed refresh leaves the entire persisted state untouched."""
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-08T00:00:00+00:00",
                "entries": {"FINRA 26-14": "sha256:old"},
            }
        },
    }
    original_state = repr(state)
    incomplete = regulatory_monitor.FetchResult(
        [], complete=False, error="FINRA notice detail page returned status 429"
    )
    save_calls = []
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: state)
    monkeypatch.setattr(regulatory_monitor, "save_state_atomic", lambda *a, **k: save_calls.append(a))
    monkeypatch.setattr(regulatory_monitor, "fetch_finra_notices", lambda *a, **k: incomplete)
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py", "--source", "finra"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2
    assert save_calls == []
    assert repr(state) == original_state
