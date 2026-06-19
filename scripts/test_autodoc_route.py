"""Tests for autodoc_route.py — deterministic issue specs and contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path

import autodoc_classifier as ac
import autodoc_route as route

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = PROJECT_ROOT / "reports" / "monitoring" / "learn-changes-2026-06-18.md"


def _contract_from_body(body: str) -> dict:
    match = re.search(r"```json\n(.*?)\n```", body, re.DOTALL)
    assert match, "issue body should include a fenced JSON contract"
    return json.loads(match.group(1))


def test_compute_fingerprint_is_stable_and_sorts_allowed_files():
    one = route.compute_fingerprint(
        "learn-changes-2026-06-18.md",
        "https://learn.microsoft.com/a",
        "MEDIUM",
        ["docs/b.md", "docs/a.md"],
    )
    two = route.compute_fingerprint(
        "learn-changes-2026-06-18.md",
        "https://learn.microsoft.com/a",
        "MEDIUM",
        ["docs/a.md", "docs/b.md"],
    )
    three = route.compute_fingerprint(
        "learn-changes-2026-06-18.md",
        "https://learn.microsoft.com/a",
        "HIGH",
        ["docs/a.md", "docs/b.md"],
    )

    assert one == two
    assert one.startswith("sha256:")
    assert one != three


def test_extract_allowed_files_prefixes_docs_and_reads_playbooks():
    block = """
### 1. Synthetic

**Affected Controls:**
- Control 1.1: Example
  - File: `controls/pillar-1-security/1.1-example.md`
- Control 1.2: Already prefixed
  - File: `docs/controls/pillar-1-security/1.2-example.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.1/portal-walkthrough.md` (CRITICAL)
- ℹ️ `docs/playbooks/control-implementations/1.2/verification-testing.md` (HIGH)

**What Changed:**
```diff
+Example
```
"""

    assert route.extract_allowed_files(block) == [
        "docs/controls/pillar-1-security/1.1-example.md",
        "docs/controls/pillar-1-security/1.2-example.md",
        "docs/playbooks/control-implementations/1.1/portal-walkthrough.md",
        "docs/playbooks/control-implementations/1.2/verification-testing.md",
    ]


def test_autodraft_issue_labels_and_contract_body():
    change = ac.Change(
        topic="Neutral additive change",
        url="https://learn.microsoft.com/en-us/neutral",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+Added a neutral portal navigation note.",
    )
    decision = ac.classify_change(change)
    fingerprint = route.compute_fingerprint("report.md", change.url, decision.classification, ["docs/example.md"])
    contract = route.build_contract(decision, "report.md", ["docs/example.md"], fingerprint)
    issue = route.build_issue(decision, change, contract, fingerprint)

    assert decision.route == "autodraft"
    assert issue["labels"] == ["autodoc", "squad:copilot"]
    assert f"AUTODOC-FINGERPRINT: {fingerprint}" in issue["body"]
    assert "AUTODOC-ROUTE: autodraft" in issue["body"]
    parsed_contract = _contract_from_body(issue["body"])
    assert parsed_contract["fingerprint"] == fingerprint
    assert parsed_contract["allowed_headings"] == route.ALLOWED_HEADINGS
    assert parsed_contract["forbidden_paths"] == route.FORBIDDEN_PATHS


def test_human_issue_labels_and_human_instruction():
    change = ac.Change(
        topic="Control-sensitive change",
        url="https://learn.microsoft.com/en-us/sensitive",
        classification="HIGH",
        affected_controls=["1.1"],
        diff_text="--- +++ @@\n+Added a neutral portal navigation note.",
    )
    decision = ac.classify_change(change)
    fingerprint = route.compute_fingerprint("report.md", change.url, decision.classification, ["docs/example.md"])
    contract = route.build_contract(decision, "report.md", ["docs/example.md"], fingerprint)
    issue = route.build_issue(decision, change, contract, fingerprint)

    assert decision.route == "human"
    assert issue["labels"] == ["autodoc", "escalate", "needs-review"]
    assert "Human analysis required" in issue["body"]
    assert "No agent draft" in issue["body"]


def test_ledger_load_save_and_already_processed(tmp_path):
    ledger_path = tmp_path / "autodoc-ledger.json"
    ledger = route.load_ledger(ledger_path)
    assert ledger == {"schema_version": 1, "changes": {}}
    assert route.already_processed(ledger, "sha256:abc") is False

    ledger["changes"]["sha256:abc"] = {"issue_number": 1}
    route.save_ledger(ledger_path, ledger)

    loaded = route.load_ledger(ledger_path)
    assert route.already_processed(loaded, "sha256:abc") is True


def test_route_report_skips_already_ledgered_fingerprint():
    report_text = FIXTURE.read_text(encoding="utf-8")
    first_pass = route.route_report(report_text, FIXTURE.name, {"schema_version": 1, "changes": {}})
    assert first_pass

    ledger = {"schema_version": 1, "changes": {first_pass[0]["fingerprint"]: {"issue_number": 123}}}
    second_pass = route.route_report(report_text, FIXTURE.name, ledger)

    assert len(second_pass) == len(first_pass) - 1
    assert first_pass[0]["fingerprint"] not in {item["fingerprint"] for item in second_pass}


def test_route_report_real_fixture_expected_split():
    report_text = FIXTURE.read_text(encoding="utf-8")
    specs = route.route_report(report_text, FIXTURE.name, {"schema_version": 1, "changes": {}})

    assert len(specs) == 23
    assert sum(1 for item in specs if item["route"] == "autodraft") == 1
    assert sum(1 for item in specs if item["route"] == "human") == 22
    assert sum(1 for item in specs if item["automerge_eligible"]) == 1
    autodraft = next(item for item in specs if item["route"] == "autodraft")
    assert autodraft["labels"] == ["autodoc", "squad:copilot"]
    assert "AUTODOC-FINGERPRINT:" in autodraft["body"]
    assert "docs/reference/microsoft-learn-urls.md" in autodraft["body"]
