# Verification & Testing: Control 1.22 — Information Barriers for AI Agents

**Last Updated:** April 2026
**Audience:** M365 administrators, Compliance Officers, internal-audit and SOC analysts validating Control 1.22

---

## Verification Strategy

Control 1.22 is verified through three concurrent test tracks. Each track produces evidence retained **6+ years** to align with SEC 17a-4(b), FINRA 4511(b), and CFTC 1.31:

1. **Configuration verification** — that segments, policies, modes, and SharePoint site segments match the design.
2. **Behavioral verification** — that AI agent surfaces (M365 Copilot, declarative agents, Microsoft Copilot Studio per-user agents, Channel Agents) actually trim cross-segment retrieval.
3. **Operational verification** — that wall-crossing, monitoring, and exception workflows function as documented and produce records.

---

## Track 1 — Configuration Verification

### Test 1.1 — IB Mode

1. Connect Compliance PowerShell (`Connect-IPPSSession`).
2. Run `Get-InformationBarrierMode`.
3. **Expected:** `MultiSegment` (recommended for FSI). `SingleSegment` is acceptable in narrow scenarios. `Legacy` is a remediation finding.

### Test 1.2 — Segment Inventory

1. Run `Get-OrganizationSegment | Select-Object Name, UserGroupFilter, Type`.
2. **Expected:** Every segment in the design matrix is present, with the agreed user-attribute filter, sourced from HR-of-record attributes.

### Test 1.3 — Active Policies and Allow-List Matrix

1. Run `Get-InformationBarrierPolicy | Where-Object State -eq 'Active' | Select-Object Name, AssignedSegment, SegmentsAllowed, SegmentsBlocked`.
2. **Expected:** The active set matches the approved allow-list (Multi-Segment) or block-list (Single-Segment). Each segment appears as `AssignedSegment` for exactly one policy.

### Test 1.4 — Last Application Status

1. Run `Get-InformationBarrierPoliciesApplicationStatus | Sort-Object StartTime -Descending | Select-Object -First 1`.
2. **Expected:** `Status = Completed`, `EndTime` within the last attestation period (default: 30 days).

### Test 1.5 — Segment Coverage

1. Run the `Export-IBSegmentCoverage` script from the [PowerShell Setup](powershell-setup.md) playbook.
2. **Expected:** Coverage ≥99.5% (Zone 2) or 100% (Zone 3 for MNPI-handling personnel). Any uncovered users are tracked to remediation in the change log.

### Test 1.6 — SharePoint Site Segment Assignment

1. From SharePoint Online Management Shell or PnP PowerShell, enumerate sites used as Copilot Studio knowledge sources or storing regulated content; verify each has an assigned segment.
2. **Expected:** All in-scope sites have a segment value matching the owning business unit, and the site IB mode is `Explicit` for MNPI-bearing sites.

---

## Track 2 — Behavioral Verification (AI Agent Surfaces)

### Canary Setup

Create a controlled "canary" document set used only for testing:

- A document **`Trading-Canary.docx`** in an `IB-Trading`-segmented SharePoint site, containing a unique non-sensitive marker phrase (e.g., `CANARY-1.22-TRADING-{GUID}`).
- A document **`Research-Canary.docx`** in an `IB-Research`-segmented SharePoint site, with its own marker phrase.
- A test user **`research.tester@<tenant>`** assigned to `IB-Research` only.
- A test user **`trading.tester@<tenant>`** assigned to `IB-Trading` only.

### Test 2.1 — M365 Copilot (BizChat) Trimming

1. Sign in as `research.tester` to a Copilot-licensed Word, Outlook, or Teams app and to BizChat.
2. Prompt: `Find any document containing CANARY-1.22-TRADING and summarize it.`
3. **Expected:** Copilot returns no result, or a "no relevant content found" response. The marker phrase must not appear in the response.

### Test 2.2 — Declarative Agent Trimming

1. As `research.tester`, invoke a declarative agent that has `Trading-Canary.docx`'s containing site as a permitted knowledge source.
2. Issue the same canary prompt.
3. **Expected:** No retrieval of the trading canary marker.

### Test 2.3 — Copilot Studio Per-User Teams Agent Trimming

1. As `research.tester`, invoke a Copilot Studio agent published as a per-user Teams app, configured with the trading SharePoint site as a knowledge source.
2. Issue the canary prompt.
3. **Expected:** No retrieval of the trading canary marker.

### Test 2.4 — Channel Agent Residual-Risk Test

1. Publish a Copilot Studio agent as a Channel Agent into a Teams channel that includes both `research.tester` and `trading.tester`.
2. As `research.tester`, invoke the Channel Agent and issue the canary prompt.
3. **Expected:** The Channel Agent **may return** the trading canary content because per-invoker IB context is not consistently applied. **This is the documented residual risk.** Compensating controls (knowledge-source curation, connector DLP, channel-membership restriction) must be evidenced in the change record.

### Test 2.5 — Wall-Crossing Recheck

1. Submit and approve a wall-crossing for `research.tester` to access `IB-Trading` for 24 hours.
2. After IB application completes, repeat Test 2.1.
3. **Expected:** The trading canary is now retrievable. After the wall-crossing expires and IB is re-applied, repeat the test; the canary must again be untrimmed.

### Test 2.6 — Cross-Workload Consistency

Repeat Test 2.1's prompt across:

- Teams 1:1 chat with Copilot.
- Outlook on the Web with Copilot.
- Word for the Web with Copilot.
- SharePoint search.
- Microsoft Planner cross-segment plan share attempt.

**Expected:** Consistent trimming behavior across all surfaces. Any inconsistency is a P1 finding.

---

## Track 3 — Operational Verification

### Test 3.1 — Wall-Crossing Workflow

1. Submit a synthetic wall-crossing request with a clear test marker.
2. Confirm routing to Compliance Officer → Legal → source BU head → target BU head.
3. Confirm provisioning, expiration, and closeout records are written to the GRC system.
4. **Expected:** Full workflow completes; closeout record present with timestamps; retention configured for 6+ years.

### Test 3.2 — Audit-Log Coverage

Run the following Microsoft Purview Audit query (Search portal or `Search-UnifiedAuditLog`):

```powershell
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
    -RecordType InformationBarrierPolicyApplication -ResultSize 5000
```

**Expected:** Recent IB application events present; entries include initiator and outcome.

### Test 3.3 — Defender XDR / Sentinel Detection

Sample KQL for Microsoft Sentinel (`OfficeActivity` table):

```kusto
OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType in ("InformationBarrierPolicyApplication","ComplianceSupervisionExchange")
| project TimeGenerated, UserId, Operation, ResultStatus, OfficeWorkload, AdditionalDetails
| order by TimeGenerated desc
```

**Expected:** Events surface in the SIEM; SOC has a documented response runbook for cross-barrier anomalies.

### Test 3.4 — Channel Agent Inventory Review

1. From PPAC, export the Copilot agents inventory.
2. Filter to agents published via Teams channel.
3. Confirm each Channel Agent's hosting channel does **not** span barrier-protected segments, or has documented compensating controls.
4. **Expected:** Zone 3 environments have zero Channel Agents in mixed-segment channels.

---

## Test Case Matrix

| Test ID | Track | Scenario | Expected Result | Evidence Artifact |
|---|---|---|---|---|
| TC-1.22-01 | 1 | `Get-InformationBarrierMode` returns intended mode | `MultiSegment` (or approved alternative) | `IB-Mode-*.json` |
| TC-1.22-02 | 1 | Segment inventory matches design | All required segments present | `IB-Segments-*.csv` |
| TC-1.22-03 | 1 | Active policy matrix matches design | Allow-list correct for every segment | `IB-Policies-*.csv` |
| TC-1.22-04 | 1 | Last application reached `Completed` | Within attestation window | `IB-AppStatus-*.json` |
| TC-1.22-05 | 1 | Segment coverage ≥ threshold | ≥99.5% (Zone 2) / 100% MNPI (Zone 3) | `IB-CoverageSummary-*.json` |
| TC-1.22-06 | 1 | SharePoint site segments assigned | All in-scope sites segmented | SPO export |
| TC-1.22-07 | 2 | M365 Copilot trims trading canary for research user | Canary not retrieved | Screenshot + prompt log |
| TC-1.22-08 | 2 | Declarative agent trims canary | Canary not retrieved | Screenshot + prompt log |
| TC-1.22-09 | 2 | Per-user Copilot Studio agent trims canary | Canary not retrieved | Screenshot + prompt log |
| TC-1.22-10 | 2 | Channel Agent residual risk acknowledged | Result documented; compensating controls in place | Risk-acceptance memo |
| TC-1.22-11 | 2 | Wall-crossing temporarily permits retrieval; reverts on expiry | Behavior matches lifecycle | Prompt logs pre/post |
| TC-1.22-12 | 3 | Wall-crossing routes through Compliance + Legal + BU heads | Full chain executes | GRC workflow record |
| TC-1.22-13 | 3 | Audit log contains IB application events | Events present in Audit | Audit export |
| TC-1.22-14 | 3 | Sentinel / Defender XDR query returns events | SIEM detection working | KQL screenshot |
| TC-1.22-15 | 3 | No Channel Agents in mixed-segment channels (Zone 3) | Inventory clean | PPAC export |

---

## Evidence Collection Checklist

Capture per attestation cycle (Zone 2: quarterly; Zone 3: monthly) and retain ≥6 years:

- [ ] `IB-Mode-*.json` with SHA-256 hash
- [ ] `IB-Segments-*.csv` with SHA-256 hash
- [ ] `IB-Policies-*.csv` with SHA-256 hash
- [ ] `IB-AppStatus-*.json` showing latest `Completed` run
- [ ] `IB-CoverageSummary-*.json` and `IB-UncoveredUsers-*.csv`
- [ ] SharePoint site-segment assignment export
- [ ] Behavioral test screenshots (TC-1.22-07 through TC-1.22-11) with timestamp watermarks
- [ ] Channel Agent inventory and risk-acceptance memo (if applicable)
- [ ] Audit-log export (`Search-UnifiedAuditLog ... InformationBarrierPolicyApplication`)
- [ ] Wall-crossing workflow synthetic-test record
- [ ] Signed Compliance Officer attestation statement (template below)

---

## Attestation Statement Template

```markdown
## Control 1.22 Attestation — Information Barriers for AI Agents

**Organization:** [Legal entity name]
**Tenant:** [Microsoft 365 tenant ID]
**Control Owner:** [Name / Role]
**Attestation Period:** [YYYY-Qx or YYYY-MM]
**Date:** [YYYY-MM-DD]

I attest that, for the period above:

1. The Microsoft Purview Information Barriers mode is `[MultiSegment / SingleSegment]`,
   verified by Get-InformationBarrierMode.
2. The following organization segments are defined and active:
   [List from Get-OrganizationSegment]
3. The following IB policies are Active and reflect the approved allow-list matrix:
   [List from Get-InformationBarrierPolicy]
4. The most recent Start-InformationBarrierPoliciesApplication completed successfully
   on [YYYY-MM-DD HH:MM UTC].
5. Segment coverage of enabled member users is [XX.XX]% with [N] uncovered users
   tracked to remediation under change ticket [TICKET-ID].
6. SharePoint sites referenced as agent knowledge sources have site segments
   assigned matching the owning business unit.
7. Behavioral tests TC-1.22-07 through TC-1.22-11 were executed and produced the
   expected results; evidence is retained in [evidence repository path].
8. Channel Agents in mixed-segment Teams channels are [absent (Zone 3) /
   covered by documented compensating controls (Zone 2)].
9. Wall-crossing requests in this period: [N], all routed through Compliance,
   Legal, and BU-head approvals; closeout records retained.
10. Audit-log and SIEM detection coverage is operational and within retention.

This attestation supports compliance with FINRA Rules 2241, 2242, 3110 (and
Notice 25-07 for AI supervision), 5270, 5280; SEC Exchange Act §15(g);
SEC Regulation Best Interest; SEC Regulation S-P; MSRB Rules G-23 and G-37;
OCC 2026-13 (formerly OCC 2011-12); and Fed SR 26-2 (formerly SR 11-7). It does not, on its own, evidence compliance
with any single regulation.

**Compliance Officer Signature:** _______________________
**Date:** _______________________
**Witnessed by (Audit Liaison):** _______________________
```

---

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
