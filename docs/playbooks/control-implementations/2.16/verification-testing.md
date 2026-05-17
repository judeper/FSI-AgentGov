# Control 2.16: RAG Source Integrity Validation — Verification & Testing

> Verification, evidence collection, and attestation guidance for [Control 2.16: RAG Source Integrity Validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md).
>
> **Audience:** AI Governance Leads, Compliance Officers, and SOC Analysts assembling regulator-defensible evidence under FINRA / SEC / GLBA / OCC / Fed SR 26-2 (formerly SR 11-7).

---

## Verification Strategy

Three complementary lines of evidence are required:

1. **Configuration evidence** — proof that the platform is configured per the [Portal Walkthrough](portal-walkthrough.md) (versioning, content approval, citations, filters, approval flow).
2. **Operating-effectiveness evidence** — proof that the configuration *worked* over the audit period (approval flow run history, staleness alert run history, citation telemetry, source-binding diff history).
3. **Negative-test evidence** — proof that **un**approved content does *not* surface in agent responses, captured as scripted test runs.

The PowerShell scripts in [PowerShell Setup](powershell-setup.md) emit configuration evidence with SHA-256 manifests. The tests below produce operating-effectiveness and negative-test evidence.

---

## Manual Verification Tests

### Test 1 — Knowledge source inventory matches binding

| Step | Action |
|------|--------|
| 1 | Open the approved-sources register (the SharePoint list maintained by the AI Governance Lead) |
| 2 | Run `Get-AgentKnowledgeBindings.ps1` and obtain the latest snapshot from `evidence\2.16\agent-knowledge-bindings-*.json` |
| 3 | Diff the snapshot against the register, agent by agent |
| **Expected** | Zero unapproved sources bound to any in-scope agent. Any drift is a finding. |
| **Evidence** | The snapshot JSON, its SHA-256 in `manifest.json`, and the diff report (CSV) |

### Test 2 — Library hardening enforced

| Step | Action |
|------|--------|
| 1 | Run `Test-LibraryHardening.ps1` against each in-scope site |
| 2 | Inspect the `library-hardening-*.json` evidence file |
| **Expected** | Every library in scope reports `Status = PASS` |
| **Evidence** | The hardening JSON and SHA-256 manifest entry |

### Test 3 — Approval flow blocks unapproved content (negative test)

| Step | Action |
|------|--------|
| 1 | In a pre-production tenant or test site, upload a new document to a knowledge library as a non-approver account |
| 2 | Without approving it, ask the bound agent a question whose answer is contained only in that document |
| 3 | Wait the documented index-propagation window (default 24 hours), then re-test |
| **Expected** | Agent does not return information from the unapproved document and does not cite it |
| **Evidence** | Screenshot of the agent response, screenshot of the document in *Pending Approval* state, Power Automate run history JSON for the approval flow |

### Test 4 — Approved content surfaces with a citation

| Step | Action |
|------|--------|
| 1 | Approve the test document from Test 3 |
| 2 | Wait the documented index window |
| 3 | Re-ask the same question |
| **Expected** | Agent returns the answer **with a citation** linking to the source document |
| **Evidence** | Screenshot of the response with citation visible; URL of the cited document |

### Test 5 — Staleness alert fires on overdue review

| Step | Action |
|------|--------|
| 1 | In a pre-production site, set a document's `Next Review Date` to a past date |
| 2 | Wait for the next scheduled run of the staleness flow (or trigger manually) |
| **Expected** | The `Source Owner` and AI Governance Lead receive the alert; the document appears in the Dataverse staleness table |
| **Evidence** | Power Automate run history JSON, screenshot of the Teams alert, Dataverse row export |

### Test 6 — Citation rendering parity across channels

| Step | Action |
|------|--------|
| 1 | Publish the agent to every channel in scope (Teams, M365 Chat, custom website, embedded SDK) |
| 2 | Ask the same knowledge-bound question on each channel |
| **Expected** | Citations render correctly on every channel. Channels that suppress citations are flagged as out-of-scope for Zone 3 use |
| **Evidence** | Screenshot per channel; channel-eligibility decision recorded by AI Governance Lead |

### Test 7 — Sovereign-cloud connectivity proven (GCC / GCC High / DoD only)

| Step | Action |
|------|--------|
| 1 | Run `Test-LibraryHardening.ps1` with `-Cloud GCCHigh` (or appropriate value) and confirm the script connects to the sovereign endpoints documented in baseline section 3 |
| 2 | Inspect the JSON output for at least one expected library |
| **Expected** | Non-zero results returned, confirming connection landed on the correct cloud (no false-clean) |
| **Evidence** | Script transcript, library-hardening JSON, SHA-256 manifest |

---

## Test Case Register

| Test ID | Scenario | Evidence artifact | Pass / Fail |
|---------|----------|-------------------|-------------|
| TC-2.16-01 | Knowledge bindings match approved-sources register | `agent-knowledge-bindings-*.json` + diff CSV | |
| TC-2.16-02 | Versioning + content approval enforced on every library | `library-hardening-*.json` | |
| TC-2.16-03 | Unapproved content not surfaced (negative test) | Run-history JSON + agent screenshot | |
| TC-2.16-04 | Approved content surfaced with citation | Agent screenshot with cited link | |
| TC-2.16-05 | Staleness alert fires on overdue review | Run-history JSON + alert screenshot | |
| TC-2.16-06 | Citation parity across channels | Per-channel screenshot set | |
| TC-2.16-07 | Sovereign-cloud connectivity proven | Transcript + JSON evidence | |
| TC-2.16-08 | Drift between two snapshots highlights unauthorized binding | Diff CSV across two snapshots | |
| TC-2.16-09 | Bing Custom Search prohibited in Zone 3 | Snapshot showing zero Bing sources bound | |
| TC-2.16-10 | Source-approval evidence library retention-locked | Purview retention-policy export | |

---

## Evidence Collection Checklist

### Configuration evidence (per audit period)

- [ ] `library-hardening-*.json` for every site in scope, with SHA-256 manifest
- [ ] `agent-knowledge-bindings-*.json` snapshots covering the audit period
- [ ] Power Automate flow definitions (export from `make.powerautomate.com`)
- [ ] Copilot Studio agent settings export (citations enabled, refusal-if-ungrounded for Zone 3)
- [ ] Site column schema export confirming the FSI metadata schema is applied

### Operating-effectiveness evidence

- [ ] Power Automate **approval flow** run history covering the audit period (CSV export)
- [ ] Power Automate **staleness flow** run history covering the audit period (CSV export)
- [ ] Stale-content reports for each scheduled run (`stale-content-*.json` + manifest)
- [ ] Source-approval forms (PDFs) for every source added during the audit period
- [ ] Diff reports between consecutive `agent-knowledge-bindings-*.json` snapshots

### Negative-test evidence

- [ ] Test 3 evidence package (unapproved content does not surface)
- [ ] Test 5 evidence package (staleness alert fires)

### Retention evidence

- [ ] Purview retention policy export covering `FSI-RAG-Source-Approvals` library
- [ ] SharePoint version history export for at least one production source document, demonstrating major / minor / approval lifecycle

---

## Evidence Artifact Naming Convention

```
Control-2.16_<ArtifactType>_<YYYYMMDD>.<ext>

Examples:
- Control-2.16_LibraryHardening_20260415.json
- Control-2.16_AgentKnowledgeBindings_20260415.json
- Control-2.16_ApprovalFlowRunHistory_2026Q1.csv
- Control-2.16_StalenessFlowRunHistory_2026Q1.csv
- Control-2.16_NegativeTestEvidence_20260415.zip
- Control-2.16_BindingsDiff_20260101-to-20260331.csv
- Control-2.16_RetentionPolicyExport_20260415.json
```

Every evidence artifact must appear in `manifest.json` with its SHA-256, byte length, and UTC generation timestamp. Artifacts not in the manifest are not auditable.

---

## Attestation Statement Template

```markdown
## Control 2.16 Attestation — RAG Source Integrity Validation

**Organization:** [Organization Name]
**Control Owner:** [Name / Role]
**Attestation period:** [Start date] to [End date]
**Date signed:** [Date]

I attest that, for the attestation period stated above and based on the evidence
listed below, the controls described in Control 2.16 were configured, operating,
and monitored as documented:

1. The knowledge source inventory was maintained and reconciled to agent bindings
   on at least the cadence required for the applicable governance zone.
2. The Power Automate approval flow was configured to gate new content as a major
   version, and run-history evidence shows the flow operated over the period.
3. SharePoint content versioning and content approval were enabled on every
   knowledge library in scope, evidenced by `library-hardening` JSON snapshots.
4. Staleness monitoring operated at the cadence required for the applicable zone,
   evidenced by run-history exports.
5. Agent citations were rendered on every approved channel, evidenced by the
   per-channel screenshots in the negative-test package.
6. No unapproved knowledge sources were bound to any in-scope agent, evidenced
   by the binding-snapshot diffs over the period.
7. Source-approval evidence was retained in the retention-locked
   `FSI-RAG-Source-Approvals` library.

Identified findings and their remediation status are listed in the appended
findings register.

**Knowledge sources in scope (count):** [Number]
**Agents in scope (count):** [Number]
**Open findings (count):** [Number]
**Evidence manifest SHA-256:** [Hash of manifest.json]

**Signature:** _______________________
**Date:** _______________________
```

> **Language note:** This template uses hedged statements that describe what the evidence supports, not absolute compliance. Do not modify to claim the control "ensures" or "guarantees" any regulatory outcome.

---

[Back to Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
