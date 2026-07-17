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


def _read(name: str) -> str:
    path = PLAYBOOK_DIR / name
    assert path.exists(), f"expected 1.10 playbook missing: {path}"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("name", PLAYBOOKS)
def test_supervisory_cmdlets_never_attributed_to_exchange_online(name: str) -> None:
    """No line may positively bind a SupervisoryReview cmdlet to Exchange Online.

    The corrected 'wrong-shell trap' legitimately names Exchange Online while
    *negating* it, so we only flag the affirmative-inversion signatures:
    the Exchange Online connection URI or the phrase 'Exchange Online cmdlets'
    appearing on the same line as a SupervisoryReview cmdlet.
    """
    offenders: list[str] = []
    for lineno, line in enumerate(_read(name).splitlines(), start=1):
        if not SUPERVISORY_CMDLET_RE.search(line):
            continue
        if "outlook.office365.com" in line or "Exchange Online cmdlets" in line:
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
    assert "ps.compliance.protection.outlook.com" in text


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
