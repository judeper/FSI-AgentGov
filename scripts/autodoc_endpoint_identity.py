#!/usr/bin/env python3
"""Canonical endpoint identity helpers for autodoc redirect matching."""

from __future__ import annotations

import urllib.parse
from typing import Any

if __package__:
    from . import autodoc_classifier as classifier
else:
    import autodoc_classifier as classifier

NO_DESTINATION = "autodoc:none"


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
