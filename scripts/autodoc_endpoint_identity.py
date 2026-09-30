#!/usr/bin/env python3
"""Canonical endpoint identity helpers for autodoc redirect matching."""

from __future__ import annotations

import re
import urllib.parse
from typing import Any

if __package__:
    from . import autodoc_classifier as classifier
else:
    import autodoc_classifier as classifier

NO_DESTINATION = "autodoc:none"
_URL_WELL_FORMED_RE = re.compile(r"^https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$")


def is_redirect_classification(value: Any) -> bool:
    return str(value or "").strip().upper().startswith("REDIRECT")


def canonicalize_endpoint_url(value: Any) -> str:
    """Return the conservative URL identity used for redirect endpoints.

    This intentionally starts with the existing classifier URL normalizer so known tracking
    query parameters are stripped consistently. Beyond that, endpoint identity lowercases only
    the scheme/host and drops the fragment. It does not normalize path case, locale path
    segments, trailing slashes, functional query keys/values, or query order; those remain
    identity-significant so genuinely different Learn pages do not merge.
    """

    if not isinstance(value, str):
        return ""
    text = value.strip()
    if not text:
        return ""
    if text == NO_DESTINATION:
        return NO_DESTINATION

    canonical = classifier._canonicalize_url(text)  # noqa: SLF001 - shared tracking-query rule.
    try:
        parsed = urllib.parse.urlsplit(canonical)
    except ValueError:
        return canonical
    return urllib.parse.urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.query,
            "",
        )
    )


def canonicalize_destination_identity(value: Any) -> str:
    return canonicalize_endpoint_url(value) or NO_DESTINATION


def canonicalize_fingerprint_url(value: Any) -> str:
    """Return the operational URL identity used inside redirect fingerprints.

    Unlike endpoint identity, fingerprint identity preserves URL fragments so two entries for
    different anchors on the same Learn page remain independently processable. It still shares
    the classifier's tracking-query stripping, matching the pre-endpoint-identity fingerprint
    behavior for URL components without reintroducing report-name/date identity.
    """

    if not isinstance(value, str):
        return ""
    text = value.strip()
    if not text:
        return ""
    if text == NO_DESTINATION:
        return NO_DESTINATION
    return classifier._canonicalize_url(text)  # noqa: SLF001 - shared tracking-query rule.


def canonicalize_destination_fingerprint_url(value: Any) -> str:
    canonical = canonicalize_fingerprint_url(value)
    if canonical == NO_DESTINATION:
        return NO_DESTINATION
    if not canonical:
        return NO_DESTINATION
    if not _URL_WELL_FORMED_RE.match(canonical):
        return NO_DESTINATION
    try:
        parsed = urllib.parse.urlsplit(canonical)
    except ValueError:
        return NO_DESTINATION
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return NO_DESTINATION
    return canonical
