#!/usr/bin/env python3
"""Parse exact identity markers from autodoc issue bodies/snapshots."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

if __package__:
    from . import autodoc_endpoint_identity as endpoint_identity
else:
    import autodoc_endpoint_identity as endpoint_identity

_FINGERPRINT_LINE_RE = re.compile(r"^AUTODOC-FINGERPRINT:\s*(\S+)\s*$", re.MULTILINE)
_SOURCE_LINE_RE = re.compile(r"^Source:\s*(\S+)\s*$", re.MULTILINE)
_DESTINATION_LINE_RE = re.compile(r"^Destination:\s*(\S+)\s*$", re.MULTILINE)
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


def _iter_visible_lines(body: str) -> Iterable[str]:
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in body.splitlines():
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        marker_char = stripped[:1]
        marker_len = len(stripped) - len(stripped.lstrip(marker_char)) if marker_char in {"`", "~"} else 0
        is_fence = indent <= 3 and marker_char in {"`", "~"} and marker_len >= 3
        if is_fence:
            if in_fence and marker_char == fence_char and marker_len >= fence_len and not stripped[marker_len:].strip():
                in_fence = False
                fence_char = ""
                fence_len = 0
                continue
            if not in_fence:
                in_fence = True
                fence_char = marker_char
                fence_len = marker_len
                continue
        if in_fence or stripped.startswith(">"):
            continue
        yield line


def _unique_visible_marker(body: str, pattern: re.Pattern[str]) -> tuple[str | None, bool]:
    values: list[str] = []
    for line in _iter_visible_lines(body):
        match = pattern.match(line)
        if match:
            value = _as_non_empty_string(match.group(1))
            if value:
                values.append(value)
    if not values:
        return None, False
    first = values[0]
    if all(value == first for value in values):
        return first, False
    return None, True


@dataclass(frozen=True)
class IssueBodyIdentity:
    """Exact identity fields parsed from one issue body."""

    fingerprint: str | None
    source_url: str | None
    content_hash: str | None
    source_kind: str  # source_line | contract | missing
    destination_url: str | None = None

    @property
    def identity(self) -> tuple[str, str] | None:
        if self.source_url and self.content_hash:
            return (self.source_url, self.content_hash)
        return None

    @property
    def redirect_identity(self) -> tuple[str, str] | None:
        if self.source_url and self.destination_url:
            return (self.source_url, self.destination_url)
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
    destination_url: str | None = None

    @property
    def identity(self) -> tuple[str, str] | None:
        if self.source_url and self.content_hash:
            return (self.source_url, self.content_hash)
        return None

    @property
    def redirect_identity(self) -> tuple[str, str] | None:
        if self.source_url and self.destination_url:
            return (self.source_url, self.destination_url)
        return None


def parse_issue_body_identity(body: str | None) -> IssueBodyIdentity:
    """Parse fingerprint/source/hash identity from an issue body.

    Source equality is exact string equality on canonical `Source:` or structured
    `source_url` values. No tokenized substring matching is used.
    """
    if not body:
        return IssueBodyIdentity(fingerprint=None, source_url=None, content_hash=None, source_kind="missing")

    fingerprint_line, _fingerprint_conflict = _unique_visible_marker(body, _FINGERPRINT_LINE_RE)
    source_line, source_conflict = _unique_visible_marker(body, _SOURCE_LINE_RE)
    destination_line, destination_conflict = _unique_visible_marker(body, _DESTINATION_LINE_RE)
    content_hash_line, content_hash_conflict = _unique_visible_marker(body, _CONTENT_HASH_LINE_RE)

    contract_source: str | None = None
    contract_destination: str | None = None
    contract_hash: str | None = None
    contract_fingerprint: str | None = None
    for contract in _iter_json_contracts(body):
        current_fingerprint = _as_non_empty_string(contract.get("fingerprint"))
        current_source = _as_non_empty_string(contract.get("source_url"))
        current_destination = _as_non_empty_string(contract.get("destination_url"))
        current_hash = _as_non_empty_string(contract.get("content_hash"))
        if contract_source is None:
            contract_source = current_source
        if contract_destination is None:
            contract_destination = current_destination
        if contract_hash is None:
            contract_hash = current_hash
        if contract_fingerprint is None:
            contract_fingerprint = current_fingerprint
        if fingerprint_line and current_fingerprint == fingerprint_line:
            contract_source = current_source
            contract_destination = current_destination
            contract_hash = current_hash
            contract_fingerprint = current_fingerprint
            break

    if source_conflict or destination_conflict or content_hash_conflict:
        return IssueBodyIdentity(
            fingerprint=fingerprint_line or contract_fingerprint,
            source_url=None,
            content_hash=None,
            source_kind="missing",
            destination_url=None,
        )

    plaintext_pair = source_line and content_hash_line
    plaintext_redirect_pair = source_line and destination_line
    contract_pair = contract_source and contract_hash
    if plaintext_pair:
        source_url = source_line
        content_hash = content_hash_line
        source_kind = "source_line"
        destination_url = (
            endpoint_identity.canonicalize_destination_identity(destination_line)
            if destination_line
            else None
        )
    elif plaintext_redirect_pair:
        source_url = endpoint_identity.canonicalize_endpoint_url(source_line)
        content_hash = None
        source_kind = "source_line"
        destination_url = endpoint_identity.canonicalize_destination_identity(destination_line)
    elif contract_pair:
        source_url = contract_source
        content_hash = contract_hash
        source_kind = "contract"
        destination_url = (
            endpoint_identity.canonicalize_destination_identity(contract_destination)
            if contract_destination
            else None
        )
    elif contract_source and contract_destination:
        source_url = endpoint_identity.canonicalize_endpoint_url(contract_source)
        content_hash = None
        source_kind = "contract"
        destination_url = endpoint_identity.canonicalize_destination_identity(contract_destination)
    else:
        source_url = None
        content_hash = None
        source_kind = "missing"
        destination_url = None

    fingerprint = fingerprint_line or contract_fingerprint
    return IssueBodyIdentity(
        fingerprint=fingerprint,
        source_url=source_url,
        content_hash=content_hash,
        source_kind=source_kind,
        destination_url=destination_url,
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
        destination_url=identity.destination_url,
    )


def parse_issue_records(issues: Iterable[Mapping[str, Any]]) -> list[IssueRecord]:
    return [parse_issue_record(issue) for issue in issues]
