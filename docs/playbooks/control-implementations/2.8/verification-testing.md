# Verification & Testing: Control 2.8 — Access Control and Segregation of Duties

**Last Updated:** April 2026
**Audience:** M365 administrators in US financial services; internal audit; Compliance Officer
**Pre-requisite:** Portal Walkthrough and PowerShell Setup completed; evidence directory at `.\evidence\2.8\`

---

## Manual Verification Steps

### Test 1 — Security groups exist with correct role-assignable flag

1. Open **Entra Admin Center → Identity → Groups → All groups**.
2. Search `SG-Agent-`.
3. Open each group and inspect **Properties → Microsoft Entra roles can be assigned to the group**.
4. **Expected:** All 5 groups present. Approvers, Release Managers, and Platform Admins show **Yes**; Developers and Reviewers show **No**.

### Test 2 — SoD detector returns clean

1. Run `.\Test-Control28-SoD.ps1 -IncludePIMEligible -EvidencePath .\evidence\2.8`.
2. Open the emitted `SoD-Violations-*.csv`.
3. **Expected:** File is empty (header only). Exit code 0. Hash recorded in `evidence-hashes.txt`.

### Test 3 — Self-approval is mechanically rejected

1. Sign in as a member of `SG-Agent-Developers` who is **not** in `SG-Agent-Approvers`.
2. Submit an agent for production publish via the standard pipeline.
3. From the same browser session, attempt to act on the resulting approval task.
4. **Expected:** Approval task does not appear in your queue. Power Automate run history shows the **SoD reject** branch fired with reason `requestor cannot approve own work`. An audit row exists in `agent_sod_decisions`.

### Test 4 — PIM activation enforces MFA, justification, and approval

1. Sign in as a PIM-eligible member of `SG-Agent-PlatformAdmins`.
2. Activate **Power Platform Administrator** via PIM → My roles.
3. **Expected:** You are prompted for phishing-resistant MFA, must enter a ticket number / justification, and the activation is queued for approval by a member of `SG-Agent-Approvers` who is not you.

### Test 5 — Access Reviews are scheduled with auto-apply

1. Open **Identity governance → Access reviews → Reviews**.
2. **Expected:** Four series visible (Zone 3 privileged monthly, Zone 3 approver/release quarterly, Zone 2 maker quarterly, Zone 1 broad maker annual). Each shows **Auto apply results = Enabled** and a non-empty reviewer of record.

### Test 6 — Copilot Studio author/admin separation

1. From the SoD detector CSV, look at the rule `Maker cannot hold platform admin`.
2. Cross-check by signing in to PPAC as a sample maker and confirming **no** Power Platform Admin tile appears in the admin center landing page.
3. **Expected:** No overlap. If a sandbox-only exception exists, it is logged in the SoD exception register with an expiry date.

### Test 7 — Dataverse System Administrator is PIM-gated in Zone 3

1. Run Script 4 (`Dataverse-SysAdmins`).
2. Filter to `EnvironmentType = Production`.
3. **Expected:** Only break-glass identities listed; all are documented in the incident-response runbook and subject to monitored alert.

### Test 8 — CAE revokes tokens on disabled-user event

1. Coordinate with HR to disable a non-production test identity that is a member of `SG-Agent-Approvers`.
2. Within 5 minutes, attempt to use a previously-issued access token (e.g., via `Get-MgGroup`).
3. **Expected:** Token call returns 401 with `claim_challenge` indicating CAE revocation.

---

## Test Cases (record pass/fail)

| Test ID | Scenario | Expected Result | Pass/Fail |
|---|---|---|---|
| TC-2.8-01 | All 5 SG-Agent-* groups exist with correct role-assignable flag | Verified in portal + Validation script | |
| TC-2.8-02 | SoD detector (Script 2) returns zero violations with `-IncludePIMEligible` | Exit code 0, empty CSV | |
| TC-2.8-03 | Self-approval blocked by Power Automate flow | Reject branch fires; audit row written | |
| TC-2.8-04 | PIM activation requires MFA + justification + approval (Zone 3) | Approval queued; not auto-active | |
| TC-2.8-05 | Access Reviews scheduled at correct cadence per zone | Four series visible | |
| TC-2.8-06 | Copilot Studio maker is **not** Platform Admin | No overlap or documented exception | |
| TC-2.8-07 | Dataverse System Administrator population in Zone 3 = break-glass only | Documented in runbook | |
| TC-2.8-08 | CAE revokes token within 5 min of user disable | 401 with claims challenge | |
| TC-2.8-09 | Approver group membership recertified within review window | 100% completion or documented escalation | |
| TC-2.8-10 | Stale account detection (no sign-in &gt; 90 days in privileged groups) | Zero stale, or removal scheduled | |

---

## Evidence Collection Checklist

Store under `maintainers-local/tenant-evidence/2.8/` (gitignored):

- [ ] Screenshot — Entra Groups list filtered to `SG-Agent-`
- [ ] Screenshot — Group **Properties** page showing role-assignable flag for each privileged group
- [ ] Screenshot — Each Dataverse environment **Security roles** view with team bindings
- [ ] Screenshot — PIM → Microsoft Entra roles → **Settings** for Power Platform Administrator
- [ ] Screenshot — PIM → Groups → onboarded list and per-group settings
- [ ] Screenshot — Identity governance → Access reviews schedule
- [ ] Screenshot — Power Automate flow run history showing SoD reject branch
- [ ] Screenshot — Conditional Access policy CA-Agent-Privileged-Path summary
- [ ] Export — `SoD-Violations-*.csv` (Script 2)
- [ ] Export — `Membership-*.csv` and `PIM-Eligible-*.csv` (Script 3)
- [ ] Export — `Dataverse-SysAdmins-*.csv` (Script 4)
- [ ] Hash file — `evidence-hashes.txt` (SHA-256 over every CSV above)

---

## Attestation Statement Template

```markdown
## Control 2.8 Attestation — Access Control and Segregation of Duties

**Organization:** [Organization Name]
**Control Owner (Accountable):** AI Governance Lead — [Name]
**Independent Reviewer:** Compliance Officer — [Name]
**Reporting Period:** [YYYY-Qn]
**Date Signed:** [YYYY-MM-DD]

I attest that, for the reporting period above:

1. The five SG-Agent-* security groups are established and the privileged
   three (Approvers, Release Managers, Platform Admins) are role-assignable.

   | Group | Member count | Role-assignable |
   |---|---|---|
   | SG-Agent-Developers | [N] | No |
   | SG-Agent-Reviewers | [N] | No |
   | SG-Agent-Approvers | [N] | Yes |
   | SG-Agent-ReleaseManagers | [N] | Yes |
   | SG-Agent-PlatformAdmins | [N] | Yes |

2. The automated SoD detector (Script 2) was executed [N] times during the
   reporting period. Violations: [N]. Open exceptions at period close: [N],
   each with documented justification and expiry.

3. Privileged Identity Management is enforced for Power Platform Administrator,
   AI Administrator, Entra Global Administrator, Privileged Role Administrator,
   and Dataverse System Administrator. Standing (Active) assignments at period
   close: [N break-glass] documented in IR runbook ID [###].

4. Entra Access Reviews ran on schedule:
   - Zone 3 privileged (monthly): [N] runs, [%] completion
   - Zone 3 approver/release (quarterly): [N] runs, [%] completion
   - Zone 2 maker (quarterly): [N] runs, [%] completion
   - Zone 1 broad maker (annual): [status]

5. The Agent Production Publish — SoD Approval flow rejected [N] self-approval
   attempts; all rejections are logged in `agent_sod_decisions`.

6. Copilot Studio authoring identities are disjoint from Power Platform admin
   identities in all Zone 3 environments. Exceptions: [list, with expiry].

**Evidence package SHA-256:** [hash of evidence-hashes.txt]

**Signature (AI Governance Lead):** _______________________
**Signature (Compliance Officer):** _______________________
```

---

## Independence Note

Per FINRA Rule 3110 supervisory expectations, the **signer of this attestation must not be the same person who executed the controls being attested to**. The AI Governance Lead may operate the controls; the Compliance Officer signs the independent attestation.

---

[Back to Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
