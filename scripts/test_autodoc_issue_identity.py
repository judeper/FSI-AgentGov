"""Tests for exact autodoc issue identity parsing."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_issue_identity as identity  # noqa: E402


def test_issue_identity_ignores_fenced_endpoint_markers() -> None:
    parsed = identity.parse_issue_body_identity(
        """AUTODOC-FINGERPRINT: sha256:fp
```text
Source: https://learn.microsoft.com/en-us/wrong
Destination: https://learn.microsoft.com/en-us/wrong-destination
```
Source: https://learn.microsoft.com/en-us/actual
Destination: https://learn.microsoft.com/en-us/actual-destination
"""
    )

    assert parsed.redirect_identity == (
        "https://learn.microsoft.com/en-us/actual",
        "https://learn.microsoft.com/en-us/actual-destination",
    )


def test_issue_identity_ignores_quoted_endpoint_markers() -> None:
    parsed = identity.parse_issue_body_identity(
        """> Source: https://learn.microsoft.com/en-us/quoted
> Destination: https://learn.microsoft.com/en-us/quoted-destination
Source: https://learn.microsoft.com/en-us/actual
Destination: https://learn.microsoft.com/en-us/actual-destination
"""
    )

    assert parsed.redirect_identity == (
        "https://learn.microsoft.com/en-us/actual",
        "https://learn.microsoft.com/en-us/actual-destination",
    )


def test_issue_identity_conflicting_endpoint_markers_fail_closed() -> None:
    parsed = identity.parse_issue_body_identity(
        """Source: https://learn.microsoft.com/en-us/one
Source: https://learn.microsoft.com/en-us/two
Destination: https://learn.microsoft.com/en-us/a
Destination: https://learn.microsoft.com/en-us/b
Content-Hash: sha256:abc
"""
    )

    assert parsed.identity is None
    assert parsed.redirect_identity is None


def test_issue_identity_duplicate_same_endpoint_markers_are_accepted() -> None:
    parsed = identity.parse_issue_body_identity(
        """Source: https://learn.microsoft.com/en-us/actual
Source: https://learn.microsoft.com/en-us/actual
Destination: https://learn.microsoft.com/en-us/actual-destination
Destination: https://learn.microsoft.com/en-us/actual-destination
"""
    )

    assert parsed.redirect_identity == (
        "https://learn.microsoft.com/en-us/actual",
        "https://learn.microsoft.com/en-us/actual-destination",
    )


def test_issue_identity_source_only_body_has_no_non_redirect_identity() -> None:
    parsed = identity.parse_issue_body_identity("Source: https://learn.microsoft.com/en-us/source-only\n")

    assert parsed.source_url is None
    assert parsed.identity is None
    assert parsed.redirect_identity is None


def test_issue_identity_plaintext_json_destination_disagreement_rejects_complete_identity() -> None:
    parsed = identity.parse_issue_body_identity(
        """AUTODOC-FINGERPRINT: sha256:fp
Source: https://learn.microsoft.com/en-us/source
Destination: https://learn.microsoft.com/en-us/plaintext-destination
Content-Hash: sha256:content
```json
{
  "fingerprint": "sha256:fp",
  "source_url": "https://learn.microsoft.com/en-us/source",
  "destination_url": "https://learn.microsoft.com/en-us/json-destination",
  "content_hash": "sha256:content"
}
```
"""
    )

    assert parsed.fingerprint is None
    assert parsed.identity is None
    assert parsed.redirect_identity is None


def test_issue_identity_conflicting_fingerprints_reject_complete_content_identity() -> None:
    parsed = identity.parse_issue_body_identity(
        """AUTODOC-FINGERPRINT: sha256:first
AUTODOC-FINGERPRINT: sha256:second
Source: https://learn.microsoft.com/en-us/content
Content-Hash: sha256:content
"""
    )

    assert parsed.fingerprint is None
    assert parsed.source_url is None
    assert parsed.content_hash is None
    assert parsed.identity is None
