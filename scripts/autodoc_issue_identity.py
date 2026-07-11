#!/usr/bin/env python3
"""Parse exact identity markers from autodoc issue bodies/snapshots."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

_FINGERPRINT_LINE_RE = re.compile(r"^AUTODOC-FINGERPRINT:\s*(\S+)\s*$", re.MULTILINE)
_SOURCE_LINE_RE = re.compile(r"^Source:\s*(\S+)\s*$", re.MULTILINE)
_CONTENT_HASH_LINE_RE = re.compile(r"^Content-Hash:\s*(\S+)\s*$", re.MULTILINE)
_JSON_CONTRACT_RE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def _as_non_empty_string(value: Any) -> str | None:
    if isinstance(value, str):
        text = value.strip()
        if text:
            return text
    return None


def normalize_state_reason(value: Any) -> str:
    """Normalize GitHub issue stateReason values (None/completed/COMPLETED)."""
    return str(value or "").strip().upper()


def _iter_json_contracts(body: str) -> Iterable[dict[str, Any]]:
    for match in _JSON_CONTRACT_RE.finditer(body):
        try:
            payload = json.loads(match.group(1))
        except (TypeError, ValueError):
            continue
        if isinstance(payload, dict):
            yield payload


@dataclass(frozen=True)
class IssueBodyIdentity:
    """Exact identity fields parsed from one issue body."""

    fingerprint: str | None
    source_url: str | None
    content_hash: str | None
    source_kind: str  # source_line | contract | missing

    @property
    def identity(self) -> tuple[str, str] | None:
        if self.source_url and self.content_hash:
            return (self.source_url, self.content_hash)
        return None


@dataclass(frozen=True)
class IssueRecord:
    """Classified issue snapshot row with exact parsed identity fields."""

    number: int | None
    url: str | None
    state: str
    state_reason: str
    fingerprint: str | None
    source_url: str | None
    content_hash: str | None
    source_kind: str

    @property
    def identity(self) -> tuple[str, str] | None:
        if self.source_url and self.content_hash:
            return (self.source_url, self.content_hash)
        return None


def parse_issue_body_identity(body: str | None) -> IssueBodyIdentity:
    """Parse fingerprint/source/hash identity from an issue body.

    Source equality is exact string equality on canonical `Source:` or structured
    `source_url` values. No tokenized substring matching is used.
    """
    if not body:
        return IssueBodyIdentity(fingerprint=None, source_url=None, content_hash=None, source_kind="missing")

    fingerprint_line = _as_non_empty_string(_FINGERPRINT_LINE_RE.search(body).group(1)) if _FINGERPRINT_LINE_RE.search(body) else None
    source_line = _as_non_empty_string(_SOURCE_LINE_RE.search(body).group(1)) if _SOURCE_LINE_RE.search(body) else None
    content_hash_line = (
        _as_non_empty_string(_CONTENT_HASH_LINE_RE.search(body).group(1))
        if _CONTENT_HASH_LINE_RE.search(body)
        else None
    )

    contract_source: str | None = None
    contract_hash: str | None = None
    contract_fingerprint: str | None = None
    for contract in _iter_json_contracts(body):
        current_fingerprint = _as_non_empty_string(contract.get("fingerprint"))
        current_source = _as_non_empty_string(contract.get("source_url"))
        current_hash = _as_non_empty_string(contract.get("content_hash"))
        if contract_source is None:
            contract_source = current_source
        if contract_hash is None:
            contract_hash = current_hash
        if contract_fingerprint is None:
            contract_fingerprint = current_fingerprint
        if fingerprint_line and current_fingerprint == fingerprint_line:
            contract_source = current_source
            contract_hash = current_hash
            contract_fingerprint = current_fingerprint
            break

    source_url = source_line or contract_source
    content_hash = content_hash_line or contract_hash
    fingerprint = fingerprint_line or contract_fingerprint
    if source_line:
        source_kind = "source_line"
    elif contract_source:
        source_kind = "contract"
    else:
        source_kind = "missing"
    return IssueBodyIdentity(
        fingerprint=fingerprint,
        source_url=source_url,
        content_hash=content_hash,
        source_kind=source_kind,
    )


def parse_issue_record(issue: Mapping[str, Any]) -> IssueRecord:
    """Parse one GitHub issue JSON record from `gh issue list --json ...`."""
    identity = parse_issue_body_identity(_as_non_empty_string(issue.get("body")))
    number_raw = issue.get("number")
    number = int(number_raw) if isinstance(number_raw, int) else None
    return IssueRecord(
        number=number,
        url=_as_non_empty_string(issue.get("url")),
        state=str(issue.get("state") or "").strip().upper(),
        state_reason=normalize_state_reason(issue.get("stateReason")),
        fingerprint=identity.fingerprint,
        source_url=identity.source_url,
        content_hash=identity.content_hash,
        source_kind=identity.source_kind,
    )


def parse_issue_records(issues: Iterable[Mapping[str, Any]]) -> list[IssueRecord]:
    return [parse_issue_record(issue) for issue in issues]
