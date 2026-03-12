# Control 1.7: Comprehensive Audit Logging - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

!!! tip "Automated Validation Available"
    For automated validation of these checks with drift detection and evidence hashing, see the [Audit Compliance Manager (ACM)](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager) solution.

---

## Verification Steps

!!! note "Connection Requirements"
    Steps 1–6 are portal-based. Steps 7–8 require `Connect-ExchangeOnline`. Step 3 search can also be performed via `Connect-IPPSSession` using `Search-UnifiedAuditLog`.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to **purview.microsoft.com** > **Solutions** > **Audit** | Audit dashboard displayed with Search and Audit retention policies tabs |
| 2 | Select **Search** tab and verify form fields | Search form with date range, activities, record types, and users fields visible |
| 3 | Search for **CopilotInteraction** record type (last 24 hours) | Results returned (if Copilot activity exists); zero results acceptable for new deployments |
| 4 | Navigate to **Audit** > **Audit retention policies** tab | Retention policies listed matching governance zone requirements (Zone 1: ≥180d, Zone 2: ≥1yr, Zone 3: ≥7yr) |
| 5 | Export a search result to CSV | Export completes successfully with CreationDate, UserIds, Operations, and AuditData columns |
| 6 | Verify SIEM integration (if applicable) | Query Sentinel/SIEM for recent audit events; logs should appear within 15 minutes of generation |
| 7 | Run `Get-AdminAuditLogConfig` via Exchange Online PowerShell (`Connect-ExchangeOnline`) | `UnifiedAuditLogIngestionEnabled` shows `True` |
| 8 | Run `Get-OrganizationConfig` via Exchange Online PowerShell (`Connect-ExchangeOnline`) | `AuditDisabled` shows `False` |

---

## Evidence Pack (US-Focused Exam Readiness)

### Purview Audit Access

- [ ] Screenshot: Purview **Audit > Search** page visible
- [ ] Screenshot/export: Operator role assignment evidence

### Audit Ingestion Enabled

- [ ] PowerShell transcript: `Get-AdminAuditLogConfig` showing `UnifiedAuditLogIngestionEnabled`

### Agent/Copilot Event Retrieval

- [ ] Screenshot: Audit search parameters and resulting record list
- [ ] Export: CSV export of representative result set

### Retention Policy Configuration

- [ ] Screenshot: Purview **Audit > Audit retention policies** tab
- [ ] Change record: Ticket/approval reference for configuration changes

### Export and Preservation (If Exporting to External Storage)

- [ ] Export log: Evidence of export run (job output, filenames, window)
- [ ] File hash: SHA-256 of each exported file
- [ ] Screenshot: Storage container and immutable policy settings

### Monitoring and Alerting

- [ ] SIEM proof: Screenshot showing events ingested with timestamp alignment

---

## Confirmation Checklist

- [ ] Unified audit logging is enabled (`UnifiedAuditLogIngestionEnabled: True`)
- [ ] Mailbox audit logging is enabled (`AuditDisabled: False`)
- [ ] Copilot/agent events are being logged (CopilotInteraction records appear in search)
- [ ] Retention policies configured per governance tier (Zone 1: ≥180d, Zone 2: ≥1yr, Zone 3: ≥7yr)
- [ ] Export capability verified (CSV export completes successfully)
- [ ] SIEM integration functional (if applicable)
- [ ] WORM storage configured (if broker-dealer — verify with compliance team)
- [ ] Dataverse environment-level auditing enabled (PPAC > Environments > Settings > Audit settings)
- [ ] Dataverse audit log retention meets zone requirements (Zone 1: ≥180d, Zone 2: ≥365d, Zone 3: ≥730d)
- [ ] Tenant-level Dataverse auditing enabled with User Sign-In and Activity logging
- [ ] Evidence artifacts collected and stored

---

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate **Dataverse** audit configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md). Dataverse retention thresholds differ from Purview Audit retention — see the [Portal Walkthrough](portal-walkthrough.md#dataverse-environment-level-audit-configuration) for details.

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|-------------------|-----------------|-------------|----------|
| SSPM-1.7-01 | Dataverse environment auditing | Enabled at environment level | PPAC > Environments > {env} > Settings > Audit and logs > Audit settings | Screenshot |
| SSPM-1.7-02 | Audit log retention period | ≥ 180d (Zone 1), ≥ 365d (Zone 2), ≥ 730d (Zone 3) | PPAC > Environments > {env} > Settings > Audit and logs > Audit settings | Screenshot |
| SSPM-1.7-03 | Tenant-level Dataverse auditing | Enabled with User Sign-In and Activity logging | PPAC > Security > Compliance > Auditing | Screenshot |

### Test Procedures

**SSPM-1.7-01: Dataverse Environment Auditing**

1. Navigate to **PPAC** > **Environments** > select target environment > **Settings** > **Audit and logs** > **Audit settings**
2. Verify "Start Auditing" is enabled
3. Verify "Log access" and "Read logs" checkboxes are enabled
4. **Pass criteria:** Auditing is enabled at the environment level with access logging active
5. **Evidence:** Screenshot showing audit settings page with all toggles enabled

**SSPM-1.7-02: Audit Log Retention Period**

1. Navigate to **PPAC** > **Environments** > select target environment > **Settings** > **Audit and logs** > **Audit settings**
2. Check the configured retention period
3. Verify retention meets zone requirements:
    - Zone 1 (Personal Productivity): ≥ 180 days
    - Zone 2 (Team Collaboration): ≥ 365 days
    - Zone 3 (Enterprise Managed): ≥ 730 days
4. **Pass criteria:** Retention period meets or exceeds the zone-specific minimum
5. **Evidence:** Screenshot showing retention configuration with zone classification documented

**SSPM-1.7-03: Tenant-Level Dataverse Auditing**

1. Navigate to **Power Platform Admin Center** > **Security** > **Compliance** > **Auditing**
2. Verify unified audit logging is enabled
3. Verify "User Sign-In" logging is active
4. Verify "Activity" logging is active
5. **Pass criteria:** Tenant-level auditing is enabled with both sign-in and activity logging active
6. **Evidence:** Screenshot showing Org Settings auditing page with all logging options enabled

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: February 2026 | Version: v1.3 | Classification: Verification Testing*
