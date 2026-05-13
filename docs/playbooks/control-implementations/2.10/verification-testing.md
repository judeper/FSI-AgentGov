# Control 2.10: Patch Management and System Updates — Verification & Testing

> Verification companion to [Control 2.10: Patch Management and System Updates](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md).
>
> **Audience:** Power Platform Admins, AI Administrators, AI Governance Leads, and internal/external auditors.
>
> **Prerequisite:** Configuration completed per the [Portal Walkthrough](portal-walkthrough.md) and at least one run of the read-only validation script in the [PowerShell Setup](powershell-setup.md) playbook.

---

## Overview

This playbook covers four verification activities, in order of typical engagement:

1. **Steady-state checks** — periodic confirmation that subscriptions, channels, and alerts remain configured
2. **Wave validation drill** — full end-to-end test that a Microsoft release wave is detected, validated, and deployed
3. **Rollback drill** — annual test that a failed deployment can be reverted within the documented Recovery Time Objective (RTO)
4. **Evidence collection** — what to capture and how to hash it for examiner-grade audit defense

---

## Part 1: Steady-State Verification

Run monthly. All checks below are **read-only**.

### Test 1.1: Message Center subscription is current

| Step | Action |
|------|--------|
| 1 | Open Microsoft 365 Admin Center > **Health > Message center > Preferences > Email** |
| 2 | Confirm the change-intake distribution list is listed |
| 3 | Confirm Microsoft Copilot, Microsoft Copilot Studio, Power Platform, Power Automate, Power Apps, Microsoft Dataverse are checked under **Choose services** |
| 4 | Confirm at least one Message Center email digest has been received in the last 14 days |

**Expected:** All four conditions true. If any false, raise an issue per [Troubleshooting](troubleshooting.md) §1.

### Test 1.2: Azure Service Health alert is firing

| Step | Action |
|------|--------|
| 1 | In the Azure Portal, open **Service Health > Health alerts** |
| 2 | Confirm the alert rule (e.g., `alert-fsi-pp-service-health`) is **Enabled** |
| 3 | Open **Monitor > Alerts** and filter to the last 30 days for the action group `ag-fsi-platform-ops` |
| 4 | Confirm at least one alert has fired in the last 90 days, **or** trigger a test alert by raising a low-impact Azure Activity Log alert and confirming the action group delivers |

**Expected:** Alert rule enabled and action group delivers within 5 minutes of a triggering event.

### Test 1.3: Release channels match policy

| Step | Action |
|------|--------|
| 1 | Run `Get-EnvironmentReleaseChannels.ps1` from the [PowerShell Setup](powershell-setup.md) playbook |
| 2 | Open the resulting JSON evidence file |
| 3 | Confirm validation environments report **Monthly** and production environments report **Semi-annual** |
| 4 | Cross-check at PPAC > Environments > [env] > Settings > Product > Behavior for any environment that reports `Unknown` |

**Expected:** Channel values match the zone matrix in the [Portal Walkthrough](portal-walkthrough.md) Part 3. Any mismatch is a finding.

### Test 1.4: Evidence retention is enforced

| Step | Action |
|------|--------|
| 1 | Open the `FSI-Patch-Evidence` SharePoint library |
| 2 | Confirm a retention label is applied (Library settings > Apply label to items in this library) |
| 3 | Open Microsoft Purview > Records management > Retention labels and confirm the label has a duration aligned to your firm's policy (typically 6 years for FSI per FINRA 4511 / SEC 17a-4(b)(4)) |
| 4 | Attempt to delete a sample evidence file; confirm the deletion is blocked or routed to disposition review |

**Expected:** Retention label active, duration meets policy, deletion blocked.

---

## Part 2: Wave Validation Drill

Run **before each major release wave** (April Wave 1, October Wave 2). Estimated duration: 1–2 hours per agent in scope.

### Step 2.1: Identify in-scope changes

1. Filter Message Center to posts where:
    - `IsMajorChange = true`, **or**
    - `ActionRequiredByDateTime` is within the next 60 days, **or**
    - `Category = "Plan for change"` and the post mentions an AI service from Part 1.1
2. Triage each post into Impact / No Impact / Awaiting Microsoft clarification.
3. Record the triage decision and owner in the `FSI-Patch-Evidence` library.

### Step 2.2: Validate in the Monthly-channel sandbox

For each Impact post:

1. Confirm the validation environment is running the **Monthly** release channel and shows the changed behavior (the Monthly channel typically receives the change 4–8 weeks ahead of Semi-annual).
2. Run the agent's regression test suite (see Test Cases below).
3. Capture pass/fail per test case.
4. If any test fails:
    - Log a deployment hold against the production environment.
    - Open a Microsoft support case if the change appears unintended.
    - Document the workaround or rollback plan.

### Step 2.3: Schedule the production deployment

1. Open the next maintenance window in the `FSI Platform Maintenance` calendar.
2. Confirm CAB approval (Zone 3) or AI Governance Lead approval (Zone 2).
3. Pre-stage the deployment artifacts (no manual deployment is required for Microsoft platform updates — this step records readiness).
4. On the day Microsoft applies the change to the Semi-annual channel:
    - Re-run the regression test suite against production.
    - Confirm pass.
    - Record the deployment in the evidence library with `Status = Validated` and `Status = Deployed`.

---

## Part 3: Rollback Drill (Annual)

Run at least once per calendar year. Required for Zone 3.

### Drill scenario

A simulated platform update has caused a regression in the production agent. Execute the documented rollback within the published RTO (typically 4 hours for Zone 3).

### Drill steps

| Step | Action | Pass Criterion |
|------|--------|----------------|
| 1 | Declare the simulated incident in the change-intake channel | Acknowledgment within 15 min |
| 2 | Open the most recent change ticket and locate the rollback plan | Plan present and references a specific previous solution version |
| 3 | Re-import the previous managed solution version into the affected environment | Import succeeds without errors |
| 4 | Re-run regression test suite | All critical tests pass |
| 5 | Communicate restoration to stakeholders | Communication within RTO |
| 6 | Document the drill outcome in `FSI-Patch-Evidence` with `Status = Rolled back` and a post-incident review entry | Drill documented within 5 business days |

> **FSI Note:** Some platform-driven changes (e.g., a connector authentication change initiated by Microsoft) **cannot be rolled back** by the customer. For those scenarios, the rollback plan must document the **mitigation** (e.g., temporarily disable the affected agent topic) rather than reversion. Do not claim a rollback capability that does not exist — examiners test for accuracy.

---

## Part 4: Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.10-01 | Message Center email digest received in last 14 days | At least one email with AI-service-tagged posts | |
| TC-2.10-02 | Service Health action group delivers within 5 min of triggering event | Email + ITSM webhook both fire | |
| TC-2.10-03 | Validation env reports Monthly channel via PowerShell | Channel = "Monthly" or equivalent property value | |
| TC-2.10-04 | Production env reports Semi-annual channel via PowerShell | Channel = "Semi-annual" or equivalent | |
| TC-2.10-05 | `FSI-Patch-Evidence` library has retention label applied | Label active, duration ≥ 6 years (or per policy) | |
| TC-2.10-06 | Wave validation drill executed for current wave | Triage + sandbox validation + production confirmation all logged | |
| TC-2.10-07 | Rollback drill completed within RTO | Restoration within documented window; outcome logged | |
| TC-2.10-08 | Patch history CSV passes SHA-256 integrity check (re-hash matches manifest) | Hash matches recorded value in `manifest.json` | |
| TC-2.10-09 | Sovereign-cloud script reports correct endpoint (GCC/GCCHigh/DoD only) | `Connect-MgGraph` shows USGov / USGovDoD environment | |
| TC-2.10-10 | Agent regression test suite passes after most recent platform change | All critical and high-priority tests pass | |

---

## Part 5: Evidence Collection Checklist

For each Zone 3 patch event, retain in `FSI-Patch-Evidence` (retention-locked) **all** of the following:

- [ ] Message Center post export (JSON, hashed) — produced by `Get-MessageCenterPosts.ps1`
- [ ] Environment release channel snapshot (JSON, hashed) — produced by `Get-EnvironmentReleaseChannels.ps1`
- [ ] Service Health alert coverage report (JSON, hashed) — produced by `Test-ServiceHealthAlertCoverage.ps1`
- [ ] Patch history CSV (hashed) — produced by `Export-PatchHistory.ps1`
- [ ] Validation environment regression test results (test runner output + screenshots if applicable)
- [ ] Change ticket reference (CAB approval record)
- [ ] Maintenance window entry from `FSI Platform Maintenance` calendar
- [ ] `manifest.json` listing every artifact with SHA-256, byte count, UTC timestamp, and script version

For Zone 2 patches, retain at minimum the patch history CSV and the change ticket reference.

---

## Part 6: Attestation Statement Template

Use at the close of each fiscal quarter. File the signed attestation in the evidence library.

```markdown
## Control 2.10 Attestation — Patch Management and System Updates

**Organization:** [Organization Name]
**Tenant:** [Tenant ID]
**Sovereign Cloud:** Commercial | GCC | GCCHigh | DoD
**Control Owner:** [Power Platform Admin name and UPN]
**Period Covered:** [Quarter, e.g., Q2 2026]

I attest, based on review of the artifacts in `FSI-Patch-Evidence`, that during the period covered:

1. The Microsoft 365 Message Center subscription was active and the change-intake distribution list received digests for the AI services in scope.
2. Azure Service Health alert rules were enabled for `Microsoft.PowerPlatform` and dependent resource providers, and the action group delivered to the operations team.
3. Validation environments were configured on the **Monthly** release channel and production environments on the **Semi-annual** release channel, except where documented exceptions were approved by the CAB.
4. Each Message Center post tagged `FSI-Action-Required` was triaged and either validated, deployed, or formally accepted as no-impact, with the disposition recorded in `FSI-Patch-Evidence`.
5. Evidence artifacts produced during the period were retained under a Microsoft Purview retention label aligned to the firm's record-retention schedule, and the SHA-256 manifest matches re-hash results for a sample of [N] artifacts.
6. The rollback drill required by this control was [executed on YYYY-MM-DD with outcome PASS / not yet due / overdue (action plan attached)].

**Last Patch Event:** [Date and Message ID]
**Validation Environment Name:** [Name]
**Production Environments in Scope:** [List]
**Open Findings:** [None | List with remediation owner and due date]

**Signature:** _______________________
**Date:** _______________________
```

---

## Validation

After completing all four parts, confirm:

- [ ] All 10 test cases above have a recorded Pass result, or open findings have remediation plans
- [ ] Wave validation drill executed for the most recent Microsoft release wave
- [ ] Rollback drill executed within the last 12 months (Zone 3)
- [ ] Quarterly attestation signed and filed
- [ ] Manifest SHA-256 re-hash audit performed on a sample of artifacts (Zone 3)

**Expected Result:** Steady-state verification produces evidence quarterly; wave drills run twice annually; rollback drill runs annually; all evidence is hashed and retention-locked.

---

[Back to Control 2.10](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.6.2*
