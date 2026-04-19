# Verification & Testing: Control 2.2 — Environment Groups and Tier Classification

**Last Updated:** April 2026

---

## Manual verification — quick path

| Check | Where to look (April 2026 PPAC) | Expected |
|---|---|---|
| 1. Groups exist per zone | **Manage → Environment groups** | One or more `FSI-Z1-*`, `FSI-Z2-*`, `FSI-Z3-*` groups present |
| 2. Production environments grouped | Group → **Environments** tab | Every production Managed Environment listed in the correct zone group |
| 3. Rules published | Group → **Rules** tab → Status column | All 23 rules show **Published** with timestamp |
| 4. Inheritance works | Add a test Managed Environment to a group → wait 15 min → open env Settings | Affected settings show **Locked by environment group** |
| 5. Quarterly re-baseline current | Governance change log | Last re-baseline date within 90 days |
| 6. CUA disabled tenant-wide | Copilot Studio admin / [Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | CUA = Disabled |

---

## Test cases

| Test ID | Scenario | Steps | Expected | Result |
|---------|----------|-------|----------|--------|
| TC-2.2-01 | Zone groups exist | Open PPAC → Environment groups | At least one group per zone with `FSI-Z{n}-*` name | |
| TC-2.2-02 | Production environments grouped | Filter env list by Type = Production | Zero ungrouped production environments | |
| TC-2.2-03 | All 23 rules published | Open each group's Rules tab | All rules show **Published** + timestamp | |
| TC-2.2-04 | Rule inheritance / lock | Add a test env to a group; open its Settings after 15 min | Setting shows **Locked by environment group** | |
| TC-2.2-05 | Sharing-Editor cap (Zone 1) | Try to share a test agent with Editor permissions in Zone 1 | Sharing blocked / capped per rule 14 | |
| TC-2.2-06 | Solution checker = Block (Zone 3) | Import a solution with known checker errors into a Zone 3 env | Import blocked per rule 19 | |
| TC-2.2-07 | External models disabled | Try to add an external model in any zone | Option unavailable per rule 9 | |
| TC-2.2-08 | Preview models disabled (Zone 2/3) | Try to enable a preview/experimental model in Zone 2 or Zone 3 | Option unavailable per rule 12 | |
| TC-2.2-09 | Unmanaged customizations blocked (Zone 3) | Attempt unmanaged change to a solution component in Zone 3 | Change rejected per rule 20 | |
| TC-2.2-10 | Transcript access enabled | Confirm rule 1 = Enabled in every zone | Transcripts available for FINRA / SEC review | |
| TC-2.2-11 | Back-up retention set per zone | Open rule 6 in each group | Z1 = 7 d, Z2 = 14 d, Z3 = 28 d (or org standard) | |
| TC-2.2-12 | CSP rule applied (Zone 3) | Open rule 23 in `FSI-Z3-*` | Set to Strict / Enforced | |
| TC-2.2-13 | CUA tenant-wide disable | Verify in Control 2.24 evidence | CUA = Disabled | |
| TC-2.2-14 | Quarterly re-baseline recent | Check governance change log | Date within 90 days | |
| TC-2.2-15 | Validation script passes | Run `Validate-Control-2.2.ps1` | Exit code 0 | |

---

## Evidence collection checklist

### Group inventory
- [ ] Screenshot: Environment groups list with member counts
- [ ] Screenshot: Each group's properties (name, description with zone classification)
- [ ] CSV: `EnvironmentGroups.csv` from the [PowerShell setup](powershell-setup.md) export

### Membership
- [ ] Screenshot: Each group's **Environments** tab
- [ ] CSV: `EnvironmentMembership.csv` from the export
- [ ] CSV: `GroupSummary.csv` from the export

### Rule configuration
- [ ] Screenshot: Each group's **Rules** tab showing all 23 rules in **Published** status with timestamps
- [ ] Screenshot: One member environment showing a setting with **Locked by environment group**
- [ ] Document: Deviations from the FSI zone matrix with named approver and rationale

### Cross-control evidence (linked, not duplicated)
- [ ] Reference: Control 2.1 evidence — Managed Environment status for all member environments
- [ ] Reference: Control 2.24 evidence — CUA tenant-wide disabled
- [ ] Reference: Control 1.5 evidence — DLP policies covering tenants in scope

### Change management
- [ ] Change ticket reference for every Zone 3 group or rule change in the review period
- [ ] Approver sign-off: AI Administrator (AI-related rules), Purview Compliance Admin (retention / supervisory rules)
- [ ] SHA-256 manifest (`manifest.sha256.csv`) for the evidence pack

---

## Evidence artifact naming convention

```
Control-2.2_<GroupName>_<ArtifactType>_<YYYYMMDD>.<ext>

Examples:
Control-2.2_FSI-Z3-Enterprise-Prod_RulesTab_20260418.png
Control-2.2_FSI-Z2-WealthMgmt_Environments_20260418.png
Control-2.2_EnvironmentMembership_20260418.csv
Control-2.2_manifest.sha256_20260418.csv
```

---

## Attestation statement template

```markdown
## Control 2.2 Attestation — Environment Groups and Tier Classification

**Review Period:** [Start] to [End]
**Control Owner:** [Power Platform Admin name / role]
**Approvers:** [AI Administrator], [Purview Compliance Admin]
**Date:** [Date]

I attest that during the review period:

1. Environment groups existed per zone with the FSI naming convention:
   - Zone 1: [group names]
   - Zone 2: [group names]
   - Zone 3: [group names]

2. Every production Managed Environment was assigned to the correct zone group; the
   ungrouped-production count was zero throughout the period (per `Validate-Control-2.2.ps1`
   exit code 0 on [dates]).

3. All 23 environment group rules were configured per the FSI zone matrix in the
   Control 2.2 specification and were in **Published** status. Deviations are documented
   in [evidence-pack/deviations.md] with named approver and rationale.

4. The matrix was re-baselined against the Microsoft Learn rules list on [date], within
   the 90-day cadence.

5. Settings that are not group rules (CUA, IP firewall, CMK, agent authentication, channel
   publishing) were verified under their owning controls (2.24, 2.1, 1.15) — references in
   the evidence pack.

6. Evidence artifacts (CSVs, screenshots, SHA-256 manifest) are retained per
   `docs/reference/evidence-retention.md` in US-only repositories.

**Signature:** _______________________
**Date:** _______________________
```

---

## Evidence pack contents

| Artifact | Description | Retention |
|---|---|---|
| `EnvironmentGroups.csv` | Group inventory | Per evidence retention policy |
| `EnvironmentMembership.csv` | Environment-to-group mapping | Per policy |
| `GroupSummary.csv` | Member counts per group | Per policy |
| Rules-tab screenshots | One per group | Per policy |
| Settings-locked screenshot | Proof of inheritance | Per policy |
| `manifest.sha256.csv` | SHA-256 of all CSVs | Per policy |
| Change tickets | Approvals for Zone 3 changes | Per policy |
| Attestation | Signed statement | Per policy |
| `deviations.md` | Documented departures from FSI zone matrix | Per policy |

---

*Updated: April 2026 | Version: v1.4.0*

[Back to Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
