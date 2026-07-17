"""Drift guards for the Control 1.10 (Communication Compliance) playbooks.

These regression tests lock in two classes of corrections made under
OceanSquad#222 that generic validators do not catch:

1. Shell attribution. The ``*-SupervisoryReview*`` cmdlet family
   (``Get-SupervisoryReviewPolicyV2``/``-Rule``/``-Activity``) is available
   **only** in Security & Compliance PowerShell (IPPS,
   ``Connect-IPPSSession`` / ``*.ps.compliance.protection.outlook.com``).
   It must never be attributed to Exchange Online
   (``Connect-ExchangeOnline`` / ``outlook.office365.com``).

2. Cross-reference targets in verification-testing.md. Records-retention /
   SEC 17a-4 must point at Control 1.9 (never 1.12); the eDiscovery
   escalation target is Control 1.19; the supervisory-population /
   FINRA Rule 3110 source is Control 2.12.

Scope is deliberately limited to the 1.10 playbooks to avoid brittle
repo-wide coupling.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PLAYBOOK_DIR = REPO_ROOT / "docs" / "playbooks" / "control-implementations" / "1.10"

PLAYBOOKS = [
    "portal-walkthrough.md",
    "powershell-setup.md",
    "troubleshooting.md",
    "verification-testing.md",
]

SUPERVISORY_CMDLET_RE = re.compile(r"(?:New|Get|Set)-SupervisoryReview\w+", re.IGNORECASE)

# Canonical endpoints. These are compared against *parsed hostnames*, never used
# as substring probes against raw text — a substring test such as
# ``"outlook.office365.com" in line`` is unsafe (it would also match
# ``eviloutlook.office365.com`` or ``outlook.office365.com.evil``), which is
# exactly the incomplete-URL-substring-sanitization pattern CodeQL flags.
EXO_HOST = "outlook.office365.com"  # Exchange Online PowerShell endpoint (exact host).
IPPS_DOMAIN = "ps.compliance.protection.outlook.com"  # IPPS endpoint (host or subdomain).

# A URL is a scheme followed by ':' and one-or-more slash/backslash separators.
# Backslashes are tolerated because some parsers/browsers treat them as slashes.
_URL_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*:[\\/]+[^\s`)\]<>\"']*")
# A bare hostname: optional wildcard label, >=2 dot-separated labels, alpha TLD.
_BARE_HOST_RE = re.compile(
    r"(?<![\w.\-])(?:\*\.)?(?:[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,63}(?![\w\-])"
)


def _normalize_host(host: str | None) -> str | None:
    """Lowercase, strip a wildcard/userinfo/port/trailing-dot; reject non-hosts."""
    if not host:
        return None
    host = host.strip().lower()
    # Drop any userinfo remnant (``user@host``) and port (``host:443``).
    if "@" in host:
        host = host.rsplit("@", 1)[-1]
    if ":" in host:
        host = host.split(":", 1)[0]
    if host.startswith("*."):
        host = host[2:]
    while host.endswith("."):
        host = host[:-1]
    labels = host.split(".")
    if len(labels) < 2 or any(not label for label in labels):
        return None
    return host


def _hostname_from_url(token: str) -> str | None:
    """Parse a URL token to its real hostname (handles userinfo / backslashes)."""
    candidate = token.replace("\\", "/")
    parts = urlsplit(candidate)
    return _normalize_host(parts.hostname)


def _extract_hosts(text: str) -> set[str]:
    """Return the set of real hostnames referenced in ``text``.

    URL tokens are parsed with :func:`urllib.parse.urlsplit` so that userinfo,
    ports and backslash tricks resolve to the *authoritative* host. URL spans
    are then blanked before scanning for bare hostnames, so a userinfo label
    (``https://outlook.office365.com@evil.com``) is never mistaken for a host.
    """
    hosts: set[str] = set()
    for match in _URL_RE.finditer(text):
        host = _hostname_from_url(match.group(0))
        if host:
            hosts.add(host)
    residual = _URL_RE.sub(" ", text)
    for match in _BARE_HOST_RE.finditer(residual):
        host = _normalize_host(match.group(0))
        if host:
            hosts.add(host)
    return hosts


def _host_equals(host: str, expected: str) -> bool:
    """Exact hostname equality (label-safe, no substring trust)."""
    return host.split(".") == expected.split(".")


def _host_in_domain(host: str, base: str) -> bool:
    """True when ``host`` is exactly ``base`` or a label-boundary subdomain of it."""
    host_labels = host.split(".")
    base_labels = base.split(".")
    if host_labels == base_labels:
        return True
    return (
        len(host_labels) > len(base_labels)
        and host_labels[-len(base_labels):] == base_labels
    )


def _references_exo_host(text: str) -> bool:
    return any(_host_equals(host, EXO_HOST) for host in _extract_hosts(text))


def _references_ipps_host(text: str) -> bool:
    return any(_host_in_domain(host, IPPS_DOMAIN) for host in _extract_hosts(text))


def _read(name: str) -> str:
    path = PLAYBOOK_DIR / name
    assert path.exists(), f"expected 1.10 playbook missing: {path}"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("name", PLAYBOOKS)
def test_supervisory_cmdlets_never_attributed_to_exchange_online(name: str) -> None:
    """No line may positively bind a SupervisoryReview cmdlet to Exchange Online.

    The corrected 'wrong-shell trap' legitimately names Exchange Online while
    *negating* it, so we only flag the affirmative-inversion signatures: the
    Exchange Online connection host (matched by exact parsed-hostname equality,
    not substring) or the phrase 'Exchange Online cmdlets' appearing on the
    same line as a SupervisoryReview cmdlet.
    """
    offenders: list[str] = []
    for lineno, line in enumerate(_read(name).splitlines(), start=1):
        if not SUPERVISORY_CMDLET_RE.search(line):
            continue
        if _references_exo_host(line) or "Exchange Online cmdlets" in line:
            offenders.append(f"{name}:{lineno}: {line.strip()}")
    assert not offenders, (
        "SupervisoryReview cmdlets wrongly attributed to Exchange Online "
        "(they are Security & Compliance PowerShell / IPPS only):\n"
        + "\n".join(offenders)
    )


def test_wrong_shell_trap_names_ipps() -> None:
    """verification-testing.md must state the cmdlets live in IPPS, not Exchange Online."""
    text = _read("verification-testing.md")
    assert "Security & Compliance PowerShell" in text
    assert "Connect-IPPSSession" in text
    assert _references_ipps_host(text), "IPPS endpoint host not found in verification-testing.md"


def test_records_retention_never_points_at_control_112() -> None:
    """SEC 17a-4 / records-retention cross-refs must target 1.9, not the old 1.12."""
    text = _read("verification-testing.md")
    bad = re.findall(r"records[- ]retention[^\n]*Control 1\.12", text, re.IGNORECASE)
    bad += re.findall(r"Control 1\.12[^\n]*records[- ]retention", text, re.IGNORECASE)
    assert not bad, f"records-retention wrongly cross-referenced to Control 1.12: {bad}"
    assert "records retention is verified under Control 1.9." in text


def test_cross_links_block_targets() -> None:
    """The §8 cross-links block must map records/eDiscovery/supervision correctly."""
    text = _read("verification-testing.md")
    expected = [
        "[Control 1.9 — Data Retention and Deletion Policies](../1.9/",
        "[Control 1.19 — eDiscovery for Agent Interactions](../1.19/",
        "[Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../2.12/",
    ]
    missing = [link for link in expected if link not in text]
    assert not missing, f"missing/incorrect 1.10 cross-links: {missing}"


# ---------------------------------------------------------------------------
# Adversarial coverage for the host-parsing helpers. These prove the guards
# reason about *hostnames*, not substrings, so evil suffix/prefix, userinfo,
# encoded/backslash ambiguity and missing-host tricks cannot fool them.
# ---------------------------------------------------------------------------

EXO_POSITIVE = [
    "outlook.office365.com",
    "`outlook.office365.com`",
    "https://outlook.office365.com/powershell-liveid",
    "https://admin@outlook.office365.com/psession",
    r"https:\\outlook.office365.com\psession",
    "HTTPS://OUTLOOK.OFFICE365.COM/",
]

EXO_NEGATIVE = [
    "eviloutlook.office365.com",
    "outlook.office365.com.evil",
    "outlook.office365.com.evil.com",
    "https://outlook.office365.com.evil.com/x",
    "https://outlook.office365.com@evil.com/psession",
    "https://evil.com/outlook.office365.com",
    "outlook-office365.com",
    "Connect to Exchange Online later in the runbook",
    "https:///no-host/path",
]

IPPS_POSITIVE = [
    "*.ps.compliance.protection.outlook.com",
    "`*.ps.compliance.protection.outlook.com`",
    "nam12b.ps.compliance.protection.outlook.com",
    "https://nam12b.ps.compliance.protection.outlook.com/psession",
]

IPPS_NEGATIVE = [
    "evilps.compliance.protection.outlook.com",
    "ps.compliance.protection.outlook.com.evil.com",
    "https://ps.compliance.protection.outlook.com@evil.com/x",
    "ps-compliance-protection-outlook.com",
]


@pytest.mark.parametrize("text", EXO_POSITIVE)
def test_exo_host_detected(text: str) -> None:
    assert _references_exo_host(text), f"expected EXO host in: {text!r}"


@pytest.mark.parametrize("text", EXO_NEGATIVE)
def test_exo_host_not_falsely_detected(text: str) -> None:
    assert not _references_exo_host(text), f"unexpected EXO host match in: {text!r}"


@pytest.mark.parametrize("text", IPPS_POSITIVE)
def test_ipps_host_detected(text: str) -> None:
    assert _references_ipps_host(text), f"expected IPPS host in: {text!r}"


@pytest.mark.parametrize("text", IPPS_NEGATIVE)
def test_ipps_host_not_falsely_detected(text: str) -> None:
    assert not _references_ipps_host(text), f"unexpected IPPS host match in: {text!r}"


def test_exact_host_equality_rejects_evil_neighbors() -> None:
    assert _host_equals("outlook.office365.com", EXO_HOST)
    assert not _host_equals("eviloutlook.office365.com", EXO_HOST)
    assert not _host_equals("outlook.office365.com.evil", EXO_HOST)


def test_subdomain_check_is_label_bounded() -> None:
    assert _host_in_domain("ps.compliance.protection.outlook.com", IPPS_DOMAIN)
    assert _host_in_domain("nam12b.ps.compliance.protection.outlook.com", IPPS_DOMAIN)
    assert not _host_in_domain("evilps.compliance.protection.outlook.com", IPPS_DOMAIN)
    assert not _host_in_domain("ps.compliance.protection.outlook.com.evil", IPPS_DOMAIN)


def test_userinfo_authority_wins_over_label() -> None:
    hosts = _extract_hosts("https://outlook.office365.com@evil.com/psession")
    assert "evil.com" in hosts
    assert EXO_HOST not in hosts

