# Verification & Testing: Control 1.16 — Information Rights Management (IRM)

**Last Updated:** May 2026
**Cadence:** Initial implementation, then quarterly (Zone 3) / semi-annually (Zone 2) — aligned with [Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) access review cadence.

---

## Manual Verification Steps

### Test 1 — Azure RMS Activation

1. Sign in to the Microsoft 365 Admin Center.
2. Navigate to **Settings** → **Org settings** → **Microsoft Azure Information Protection**.
3. **Expected:** Status reads **Protection is activated**.
4. Cross-check from PowerShell: `Connect-AipService; Get-AipService` returns `Enabled`.

### Test 2 — IRM-Enabled Sensitivity Label is Published

1. Open the [Microsoft Purview portal](https://purview.microsoft.com) → **Information Protection** → **Labels**.
2. Open the FSI IRM-enabled label (e.g., `FSI Confidential — IRM`).
3. **Expected:** Encryption is configured with **Assign permissions now**, the agent service identity is present at **Viewer**, and the label appears in at least one **active** label policy targeted at the consuming user populations.

### Test 3 — Tenant SharePoint IRM Enabled

1. Open SharePoint Admin Center → **Policies** → **Access control** → **Information Rights Management (IRM)**.
2. **Expected:** "Use the IRM service specified in your configuration" is selected.

### Test 4 — Library-Level IRM Enforces Egress on Download

1. Locate a Zone 3 agent knowledge-source library.
2. As a non-super-user account that has at least Read on the library, upload a benign test file (e.g., `1.16-test.docx`) and then download a copy.
3. Open the downloaded file in Microsoft 365 Apps for enterprise.
4. **Expected:** The file opens with the IRM banner showing the policy title, and the configured restrictions (no print, no copy, no forward) are enforced. Attempts to copy text or print fail with the IRM message.

### Test 5 — Agent Grounds on Protected Content Without Stripping Protection

1. Trigger a Microsoft Copilot Studio agent (Zone 3) whose knowledge source is the IRM-enabled library.
2. Ask a question whose answer requires content from `1.16-test.docx`.
3. **Expected:** The agent returns a grounded answer referencing the document. The document itself is not surfaced as a downloadable, unprotected attachment.
4. **Negative test:** Sign in as a user not entitled to the document, ask the same question — the agent should not return content from the protected file (this also exercises Control 1.5 / 4.1).

### Test 6 — Document Tracking Captures Access

1. Within 30 minutes of Test 4, open Microsoft Purview → **Information Protection** → **Track and revoke documents**.
2. Locate `1.16-test.docx`.
3. **Expected:** The access event is listed with the test user's identity, timestamp, and approximate location.
4. Cross-check the Unified Audit Log (`Search-UnifiedAuditLog -Operations 'FileAccessed','RmsAccess'`) for a matching record.

### Test 7 — Revocation Takes Effect

1. From the tracking dashboard for `1.16-test.docx`, revoke access.
2. As the test user, attempt to re-open the previously downloaded copy after the offline-license validity window.
3. **Expected:** The file fails to open with an "Access has been revoked" or "You no longer have permission" message.

### Test 8 — Super-User Group Inventory and Membership

1. Run `Get-AipServiceSuperUserGroup` and confirm it returns the approved compliance group.
2. Inspect the group membership in Entra ID.
3. **Expected:** Membership is limited to named compliance personnel and matches the latest [Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) access review record.

---

## Test Case Matrix

| Test ID | Scenario | Expected Result | Pass / Fail |
|---|---|---|---|
| TC-1.16-01 | Azure RMS status (`Get-AipService`) | `Enabled` | |
| TC-1.16-02 | IRM-enabled label published in active policy | Label visible in target user's Office apps | |
| TC-1.16-03 | Tenant SharePoint IRM enabled | "Use the IRM service…" selected | |
| TC-1.16-04 | Library IRM applied on download (Zone 3) | Downloaded doc opens with IRM banner; print/copy blocked | |
| TC-1.16-05 | Agent grounds on IRM content for entitled user | Grounded answer returned; source file not redistributed | |
| TC-1.16-06 | Agent denies IRM content to non-entitled user | No grounded answer / redacted | |
| TC-1.16-07 | Document tracking surfaces access event | Event visible in Purview within 30 min | |
| TC-1.16-08 | Revocation propagates to offline copy | Subsequent open after license expiry blocked | |
| TC-1.16-09 | Content expiration applied (Zone 3 = 90 days) | License denies access after configured period (test with shortened policy in dev tenant) | |
| TC-1.16-10 | Super-user group matches approved roster | `Get-AipServiceSuperUserGroup` returns expected group | |
| TC-1.16-11 | Auto-labeling applies IRM label to SSN-bearing doc | Test doc auto-receives label within policy SLA | |
| TC-1.16-12 | Drift report (`Export-IRMReport.ps1`) shows zero FAIL rows | Every agent-KB library has IRM enabled | |

---

## Evidence Collection Checklist

Store evidence in `maintainers-local/tenant-evidence/1.16/<YYYYMMDD>/`. Do not commit.

### Azure RMS
- [ ] Screenshot — Microsoft 365 Admin Center "Microsoft Azure Information Protection" pane showing **Protection is activated**.
- [ ] Console capture — `Get-AipService` and `Get-AipServiceConfiguration` output.

### Sensitivity Labels
- [ ] Screenshot — Purview label encryption page (permissions list with agent identity at Viewer).
- [ ] Screenshot — Label policy publication target groups.
- [ ] Export — `Get-Label` (Purview) for the FSI IRM label.

### SharePoint IRM
- [ ] Screenshot — SharePoint Admin Center **Information Rights Management** page.
- [ ] Screenshot — Library settings → Information Rights Management page for one Zone 3 library.
- [ ] CSV — `Control-1.16_IRMReport_<date>.csv` with SHA-256 hash recorded in change log.

### Document Tracking and Revocation
- [ ] Screenshot — Track and revoke dashboard showing the test access event.
- [ ] Screenshot — Confirmation of revocation action.
- [ ] Audit log export — `Search-UnifiedAuditLog` results for the test events.

### Super-User Governance
- [ ] Console capture — `Get-AipServiceSuperUserFeature` and `Get-AipServiceSuperUserGroup`.
- [ ] Membership snapshot — Entra ID export of the compliance super-user group.

---

## Evidence Artifact Naming Convention

```
Control-1.16_<ArtifactType>_<YYYYMMDD>.<ext>

Examples:
  Control-1.16_AzureRMSStatus_20260415.png
  Control-1.16_LabelPermissions_20260415.png
  Control-1.16_LibraryIRM_AdvisoryClientDocs_20260415.png
  Control-1.16_DriftReport_20260415.csv
  Control-1.16_TrackUsage_20260415.png
  Control-1.16_Revocation_20260415.png
  Control-1.16_SuperUserGroup_20260415.txt
```

---

## Attestation Statement Template

```markdown
## Control 1.16 Attestation — Information Rights Management

**Organization:** [Organization Name]
**Control Owner:** [Name / Role]
**Reporting Period:** [Start] to [End]
**Date Signed:** [Date]

I attest, based on the evidence collected above, that for the reporting period:

1. The Azure Rights Management Service was activated and operational.
2. The IRM-enabled sensitivity label(s) listed below were published and applied to agent knowledge content:
   - [Label name] — [Label policy] — [Target groups]
3. The following SharePoint document libraries used as Copilot Studio / Microsoft 365 Copilot agent knowledge sources had IRM enabled with Zone-appropriate settings:
   - [Site] / [Library] — Zone [N] — Last verified [Date]
4. The agent service identity (Copilot Studio app registration / M365 Copilot identity) was scoped to Viewer rights only.
5. Document tracking and revocation were operational; [N] revocation events were issued during the period.
6. The Azure RMS super-user group was reviewed on [Date] and contained [N] members, all approved compliance personnel.
7. Drift report `Control-1.16_DriftReport_<date>.csv` (SHA-256: [hash]) reported zero agent-KB libraries missing IRM.

Findings or exceptions: [None / list]

**Signature:** _______________________  **Date:** _______________________
```

---

[Back to Control 1.16](../../../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
