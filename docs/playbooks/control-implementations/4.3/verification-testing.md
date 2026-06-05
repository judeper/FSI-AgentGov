# Control 4.3: Site and Document Retention Management - Verification & Testing

> This playbook provides verification and testing guidance for [Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md).

---

## Test Procedure

### Step 1: Verify Site Lifecycle Policies (SharePoint Admin Center)

1. Navigate to **SharePoint Admin Center > Policies > Site lifecycle management**.
2. Open **Inactive site policies** — confirm at least one policy is **Enabled** with the agreed inactivity threshold and graduated enforcement actions.
3. Open **Site ownership policies** — confirm orphan-detection policy is enabled.
4. Capture the policy summary screen for evidence.

### Step 2: Verify Organization Retention Defaults

1. In **SharePoint Admin Center > Settings**, open **OneDrive retention** and confirm the configured period (≥ 365 days for regulated tenants).
2. Confirm version-history settings align with the records-retention schedule.

### Step 3: Verify Retention Labels and Policies (Microsoft Purview)

1. In Microsoft Purview, open **Data Lifecycle Management > Labels** and confirm each FSI label is **Published**.
2. Open **Policies** and confirm each policy has `Enabled = True`, `DistributionStatus = Success`, and the expected `SharePointLocation`.
3. For policies in SEC 17a-4(f) scope, confirm `RestrictiveRetention = True` (Preservation Lock applied).

### Step 4: Functional Test — Retention Behavior

1. In a **non-production** Zone 3 test site, upload a sample file and apply the `FSI-Communications-3Y` label (or equivalent test label).
2. Attempt to delete the file as a standard user. Confirm the file moves to the **Preservation Hold Library** (not permanently deleted).
3. As an admin, verify the file is recoverable from the Preservation Hold Library and that the deletion event appears in the **Purview Audit log** (search for `FileDeletedFirstStageRecycleBin` and `ComplianceSettingChanged`).

### Step 5: Functional Test — Legal Hold Override

1. Coordinate with the eDiscovery owner (Control 1.19) to place a temporary hold on the test site.
2. Confirm content under hold is **not** deleted when retention expiry would otherwise apply.
3. Document the override behavior; release the hold after the test.

---

## Expected Results Checklist

- [ ] Inactive site policy enabled in SharePoint Admin Center
- [ ] Site ownership policy enabled (recommended/regulated tiers)
- [ ] OneDrive retention set per requirements (≥ 365 days regulated)
- [ ] All FSI retention labels published with `DistributionStatus = Success`
- [ ] Preservation Lock applied where required (verified `RestrictiveRetention = True`)
- [ ] User-initiated deletion of labeled content lands in Preservation Hold Library
- [ ] Deletion events visible in Purview audit log
- [ ] Legal hold overrides retention deletion in test
- [ ] All Copilot/agent knowledge-source sites covered by a retention policy (no gaps in coverage report)

---

## Verification Evidence

| Evidence Type | Location | Hash | Retention |
|---------------|----------|------|-----------|
| Inactive/ownership policy export (CSV/JSON) | SharePoint Admin Center | SHA-256 in `manifest.json` | 6 years |
| Retention policy + rule export (JSON) | Purview / PowerShell | SHA-256 in `manifest.json` | 6 years |
| Retention label inventory (JSON) | Purview / PowerShell | SHA-256 in `manifest.json` | 6 years |
| Preservation Lock confirmation transcript | PowerShell `Start-Transcript` | SHA-256 in `manifest.json` | 7 years (regulatory) |
| Site coverage report (sites without retention) | PowerShell `Get-SPOSite` | SHA-256 in `manifest.json` | 6 years |
| Functional test evidence (deletion → Preservation Hold) | Purview audit log export | SHA-256 in `manifest.json` | 6 years |

> All evidence emitted by the Control 4.3 PowerShell setup is hashed and listed in `manifest.json` per the [PowerShell Authoring Baseline §4](../../_shared/powershell-baseline.md). Land artifacts in WORM-configured storage to support SEC 17a-4(f) record-keeping.

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-4.3-01 | Inactive site policy enabled | Policy shows **Active** in Site lifecycle management | |
| TC-4.3-02 | Site inactive beyond threshold | Site owner receives notification email; site flagged in policy report | |
| TC-4.3-03 | Site ownership policy detects orphan | Orphaned site appears in policy report; admin notified | |
| TC-4.3-04 | Retention policy applied to Zone 3 site | Policy lists site URL with `Enabled = True`, `DistributionStatus = Success` | |
| TC-4.3-05 | Retention label published | Label visible to authoring users in document libraries | |
| TC-4.3-06 | User deletes labeled document | Document moves to Preservation Hold Library | |
| TC-4.3-07 | Retention period expires | Disposition review triggered (if configured); audit event recorded | |
| TC-4.3-08 | OneDrive retention setting | Tenant value matches documented requirement | |
| TC-4.3-09 | Preservation Lock applied | `Get-RetentionCompliancePolicy` returns `RestrictiveRetention = True` | |
| TC-4.3-10 | Legal hold overrides retention deletion | Held content remains preserved past retention expiry | |
| TC-4.3-11 | Coverage report — agent knowledge sites | Every Copilot/agent knowledge source appears in `SiteRetention` (no gaps) | |

---

## PowerShell Validation Commands

```powershell
# Policy distribution health
Get-RetentionCompliancePolicy |
    Select-Object Name, Enabled, Mode, DistributionStatus, RestrictiveRetention |
    Format-Table

# Surface any policies that failed to deploy (DistributionStatus != Success)
Get-RetentionCompliancePolicy | Where-Object { $_.DistributionStatus -ne 'Success' } |
    Select-Object Name, DistributionStatus, DistributionResults

# Confirm rules attached to each policy
Get-RetentionComplianceRule |
    Select-Object Name, Policy, RetentionDuration, RetentionComplianceAction, ExpirationDateOption |
    Format-Table

# Confirm published labels
Get-ComplianceTag |
    Select-Object Name, RetentionDuration, RetentionAction, IsRecordLabel, Regulatory |
    Format-Table
```

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

- [ ] Baseline retention policies applied where applicable
- [ ] Exceptions documented for personal agents
- [ ] Minimal scope beyond user's own data

### Zone 2 (Team Collaboration)

- [ ] Agent knowledge sources follow retention rules
- [ ] Identified site owner and approval trail
- [ ] Configuration validated in pilot before broad publication
- [ ] Evidence of label/policy assignment retained with SHA-256 manifest

### Zone 3 (Enterprise Managed)

- [ ] Strictest retention configuration enforced via policy
- [ ] Preservation Lock applied for SEC 17a-4(f) scope policies
- [ ] Changes governed by change ticket + documented testing evidence
- [ ] Functional test of legal-hold override executed and documented annually
- [ ] Coverage report confirms zero agent knowledge sources without retention

---

## Compliance Attestation Template

```markdown
# Retention Management Compliance Attestation

**Control:** 4.3 - Site and Document Retention Management
**Attestation Date:** [Date]
**Attested By:** [Name / Role]
**Tenant:** [Tenant ID]
**Cloud:** Commercial

## Policy Status

- [ ] Inactive site policies configured (SharePoint Admin Center)
- [ ] Site ownership policies configured
- [ ] Retention labels published (Microsoft Purview)
- [ ] Zone-specific policies applied
- [ ] Preservation Lock applied where required
- [ ] Legal-hold override tested with eDiscovery owner

## Evidence Collected

| Item | Date Collected | Path | SHA-256 |
|------|---------------|------|---------|
| Policy export (JSON) | [Date] | [Path] | [Hash] |
| Label export (JSON) | [Date] | [Path] | [Hash] |
| Site coverage report | [Date] | [Path] | [Hash] |
| Functional test transcript | [Date] | [Path] | [Hash] |

## Findings

[Document any gaps or issues identified]

## Remediation Actions

[Document any required remediation with target dates and owners]

## Sign-Off

Attested By: _________________ Date: _________
Reviewed By: _________________ Date: _________
```

---

[Back to Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
