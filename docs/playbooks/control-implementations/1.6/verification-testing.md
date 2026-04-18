# Control 1.6 — Verification & Testing: DSPM for AI

**Control:** [1.6 Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)
**Reference template:** `1.7/verification-testing.md`, `2.1/verification-testing.md`
**Last UI Verified:** April 2026

---

## Re-verification cadence (SR 11-7 alignment)

| Cadence | Activity | Owner |
|---|---|---|
| Daily (Zone 3) | Activity Explorer review for in-scope users; oversharing remediation aging |  AI Governance Lead delegate |
| Weekly | Default Weekly Risk Assessment review (top 100 sites); deterministic `1.6-ACT-01` test | Compliance Admin |
| Monthly | License entitlement reconciliation (`1.6-LIC-01`); one-click policy inventory (`1.6-POL-01`) | Compliance Admin |
| Quarterly | Negative test suite (`1.6-NEG-01`…`1.6-NEG-05`); attestation pack | Compliance Admin + AI Governance Lead |
| On-change | Re-run any test affected by license change, role change, policy change, sovereign-cloud change | Change requester |
| On-incident | `1.6-INC-01` — full evidence preservation per troubleshooting playbook | Incident commander |

---

## Test catalog

Each test specifies prerequisites, deterministic input/output, and audit-binder evidence.

### `1.6-ACT-01` — Deterministic Copilot interaction is logged

**Prereq:** A named M365 Copilot–licensed user; tenant in scope of a `Capture interactions for Copilot experiences` template with content capture **on**.

| Step | Action | Expected | Evidence |
|---|---|---|---|
| 1 | Record UTC timestamp | — | tester log |
| 2 | User issues a known prompt referencing a labeled doc | — | tester log |
| 3 | Wait 24 h (per Learn) | — | — |
| 4 | Activity Explorer: filter `User=<UPN>` AND time window | Event count ≥ 1, app=Microsoft 365 Copilot | CSV export + SHA-256 |
| 5 | `Search-UnifiedAuditLog -RecordType CopilotInteraction` over same window | Same event count and `UserId` | CSV export + SHA-256 |

**Pass:** Both steps 4 and 5 return ≥ 1 with reconciled count. **Fail (silent-zero-row):** Either returns 0 — investigate license, audit ingestion (correct shell), scope, content capture.

### `1.6-LIC-01` — License entitlement coverage

**Pass:** 100% of in-scope monitored users carry M365 Copilot SKU per `Get-MgUserLicenseDetail`; PAYG billing active where non-MS AI in scope. **Fail:** Any unlicensed in-scope user — silent under-reporting risk.

### `1.6-POL-01` — One-click policy inventory + content-capture state

**Pass:** Each enabled template has recorded {name, mode, scope, exclusions, content-capture state, role used}. Templates with "Capture" in name have content capture **on**. **Fail:** Any "Capture …" template with content capture off — Activity Explorer rows render but content is empty.

### `1.6-LBL-01` — Sensitivity-label propagation to Copilot response

Label a source doc → invoke Copilot summarization → assert response carries label or restriction per Copilot label inheritance behavior. (Per Learn `microsoft-365-copilot-architecture-data-protection-auditing`.)

### `1.6-AP-01` — Adaptive Protection threshold fires (Commercial / GCC only)

Induce a user into the elevated risk tier (test tenant) → attempt sensitive prompt → assert configured DLP action (warn / audit / block) fires and Activity Explorer + IRM both reflect the event. **Skip on GCC High / DoD** with documented exception.

### `1.6-WRA-01` — Weekly Risk Assessment cadence

| Check | Expected | Source |
|---|---|---|
| Default Weekly Assessment runs each week | Yes | Data risk assessments page |
| First-results delay tolerance | ≤ 4 days | Learn `dspm-for-ai-considerations` |
| Refresh tolerance | ≥ 48 h post-completion | Learn |
| Custom assessments scheduled for Zone 3 sites > top 100 | All in-scope sites covered | CAB-tracked register |

### `1.6-NEG-01..05` — Negative tests

| ID | Scenario | Expected |
|---|---|---|
| NEG-01 | Unauthorized role opens DSPM for AI | Access denied |
| NEG-02 | One-click policy paused (`Mode=Disable`) → test interaction | Event logged but no enforcement; documented |
| NEG-03 | Browser extension absent on managed Windows endpoint → ChatGPT visit | Third-party AI event **not** in Activity Explorer |
| NEG-04 | Unlicensed Copilot user attempts interaction | Documented behavior (event still in audit vs. dropped) |
| NEG-05 | Restricted-AU admin attempts to create one-click DSPM policy | Refused (AU not supported) |

### `1.6-WORM-01` — Evidence integrity & immutable storage

**Pass:** Every CSV / JSON / PDF artifact has a paired `.sha256` sidecar; storage location is immutable (Purview retention label, SharePoint hold, or WORM blob) with retention aligned to Control 1.7. **Fail:** Any artifact without sidecar or stored on writable share.

### `1.6-DSPMv-01` — Unified DSPM (preview) accessibility

If tenant is opted into the preview, verify the **DSPM (preview)** node loads and `Posture / Objectives / AI observability / Discover > Activity explorer / Discover > Data risk assessments` are reachable. If not opted in, document and skip — do not assert preview-specific UI affordances.

---

## Evidence pack (audit-binder)

```
Control-1.6_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}
Control-1.6_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}.sha256
```

Required artifacts per quarter:

- `1.6-ACT-01` deterministic-test result (CSV) + tester log (TXT)
- `1.6-LIC-01` license entitlement reconciliation (CSV)
- `1.6-POL-01` one-click policy inventory (JSON)
- `1.6-LBL-01` propagation test result (PDF + screenshots)
- `1.6-AP-01` Adaptive Protection result (CSV + IRM event export) **or** documented sovereign exception
- `1.6-WRA-01` weekly assessment summaries × 13 weeks (PDF + CSV)
- `1.6-NEG-01..05` negative-test results (CSV + screenshots)
- `1.6-WORM-01` immutable-storage attestation (signed)
- Tenant cloud + role-by-step attestation
- PowerShell transcripts from all runs

---

## Attestation template

```text
Control 1.6 — Microsoft Purview DSPM for AI
Quarter: Q_____ FY_____
Tenant: __________________________  Cloud: ☐ Commercial ☐ GCC ☐ GCC High ☐ DoD  Zone: ☐ 1 ☐ 2 ☐ 3

I have executed the test catalog above for the period covered. The evidence pack referenced
in this attestation supports — but does not by itself establish — the firm's compliance with:

  • FINRA Rule 3110 / 25-07 supervisory-system requirements applicable to AI surfaces
  • SEC 17a-4(f) / FINRA 4511 record-preservation expectations (paired with Audit Premium / Control 1.7)
  • SEC Reg S-P §248.30(a)(4) detection support for events that may trigger customer notification
  • GLBA 501(b) safeguards expectations for customer information processed by AI
  • OCC 2011-12 / Fed SR 11-7 model risk management ongoing-monitoring expectations
  • Interagency Guidance on Third-Party Relationships (OCC/FRB/FDIC) for ongoing monitoring of third-party AI

This evidence does not constitute a legal determination. Reportability decisions remain with
Compliance and Legal counsel.

Reviewer: __________________________   Role: __________________________
Signature: _________________________   Date (UTC): ____________________
```

---

## Cross-references

- [Control 1.6 Portal Walkthrough](portal-walkthrough.md)
- [Control 1.6 PowerShell Setup](powershell-setup.md)
- [Control 1.6 Troubleshooting](troubleshooting.md) — for any FAIL or `1.6-INC-01`
- [Control 1.7 Verification & Testing](../1.7/verification-testing.md) — pair for durable evidence

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
