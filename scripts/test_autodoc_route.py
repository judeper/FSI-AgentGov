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


def test_redirect_fingerprint_distinguishes_a_to_b_from_a_to_c():
    common = (
        "learn-changes-2026-06-18.md",
        "https://learn.microsoft.com/a?msockid=tracked",
        "REDIRECT",
        [route.REDIRECT_TARGET_FILE],
    )
    to_b = route.compute_fingerprint(*common, "https://learn.microsoft.com/b?utm_source=monitor")
    to_b_untracked = route.compute_fingerprint(*common, "https://learn.microsoft.com/b")
    to_c = route.compute_fingerprint(*common, "https://learn.microsoft.com/c")
    assert to_b == to_b_untracked
    assert to_b != to_c


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


def test_build_contract_includes_content_hash():
    # The contract must carry the change's content_hash so the runner can stamp it into the
    # escalation issue body, where the advance step matches it back to the pending blob.
    change = ac.Change(
        topic="Neutral additive change",
        url="https://learn.microsoft.com/en-us/neutral",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+Added a neutral portal navigation note.",
        content_hash="sha256:abc123",
    )
    decision = ac.classify_change(change)
    contract = route.build_contract(decision, "report.md", ["docs/example.md"], "sha256:fp")
    assert contract["content_hash"] == "sha256:abc123"


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


def test_build_contract_redirect_uses_target_file_headings(tmp_path):
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text(
        "# Microsoft Learn URLs\n\n## Copilot Studio\n- https://old\n\n## Microsoft Purview\n- https://x\n",
        encoding="utf-8",
    )
    change = ac.Change(
        topic="URL redirect: https://old",
        url="https://old",
        classification="REDIRECT",
        reason="redirects to https://new",
        kind="redirect",
        destination_url="https://new?utm_source=test",
    )
    decision = ac.classify_change(change)
    assert decision.kind == "redirect"
    fingerprint = route.compute_fingerprint("report.md", change.url, decision.classification, ["docs/reference/microsoft-learn-urls.md"])
    contract = route.build_contract(
        decision, "report.md", ["docs/reference/microsoft-learn-urls.md"], fingerprint, repo_root=tmp_path
    )
    # The redirect contract carries the URL file's OWN topic headings, not the control headings.
    assert "Copilot Studio" in contract["allowed_headings"]
    assert "Microsoft Purview" in contract["allowed_headings"]
    assert contract["allowed_headings"] != route.ALLOWED_HEADINGS
    assert contract["destination_url"] == "https://new"


def test_build_contract_redirect_missing_file_yields_empty_headings(tmp_path):
    change = ac.Change(topic="URL redirect", url="https://old", classification="REDIRECT", reason="redirects to https://new", kind="redirect")
    decision = ac.classify_change(change)
    contract = route.build_contract(decision, "report.md", ["docs/reference/missing.md"], "sha256:x", repo_root=tmp_path)
    # Fail closed: if the target file can't be read, no headings are allowed (edit will be blocked).
    assert contract["allowed_headings"] == []


def test_build_contract_content_change_uses_generic_headings():
    change = ac.Change(topic="content", url="https://learn.microsoft.com/x", classification="MEDIUM", diff_text="+note", kind="content")
    decision = ac.classify_change(change)
    contract = route.build_contract(decision, "report.md", ["docs/example.md"], "sha256:y")
    assert contract["allowed_headings"] == list(route.ALLOWED_HEADINGS)


def test_redirect_allowed_files_ignores_control_block_files():
    # A URL appearing in BOTH a detailed change block (control file) and the redirect table must
    # never let a redirect inherit the control file — redirects only ever edit the URL list.
    block_with_control = "**URL:** https://old\n- File: `docs/controls/pillar-2-management/2.5-testing.md`\n"
    change = ac.Change(topic="redirect", url="https://old", classification="REDIRECT", kind="redirect")
    files = route._allowed_files_for_change(change, block_with_control)
    assert files == [route.REDIRECT_TARGET_FILE]


def test_content_allowed_files_still_extracts_block_files():
    block = "**URL:** https://x\n- File: `docs/controls/pillar-1-security/1.1-x.md`\n"
    change = ac.Change(topic="content", url="https://x", classification="MEDIUM", kind="content")
    files = route._allowed_files_for_change(change, block)
    assert "docs/controls/pillar-1-security/1.1-x.md" in files


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
