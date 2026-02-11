# Control 1.7: Comprehensive Audit Logging - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to purview.microsoft.com > Audit | Audit dashboard displayed |
| 2 | Access Search page | Search form with all fields visible |
| 3 | Search for Copilot events (last 24 hours) | Results returned (if activity exists) |
| 4 | Check retention policies | Policies configured per governance tier |
| 5 | Verify export capability | Export completes successfully |
| 6 | Test SIEM integration | Logs appearing in external system |

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

- [ ] Screenshot: Purview **Audit > Policies** list
- [ ] Change record: Ticket/approval reference for configuration changes

### Export and Preservation (If Exporting to External Storage)

- [ ] Export log: Evidence of export run (job output, filenames, window)
- [ ] File hash: SHA-256 of each exported file
- [ ] Screenshot: Storage container and immutable policy settings

### Monitoring and Alerting

- [ ] SIEM proof: Screenshot showing events ingested with timestamp alignment

---

## Confirmation Checklist

- [ ] Unified audit logging is enabled
- [ ] Copilot/agent events are being logged
- [ ] Retention policies configured per governance tier
- [ ] Export capability verified
- [ ] SIEM integration functional (if applicable)
- [ ] WORM storage configured (if broker-dealer)
- [ ] Evidence artifacts collected and stored

---

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|-------------------|-----------------|-------------|----------|
| SSPM-1.7-01 | Dataverse environment auditing | Enabled at environment level | PPAC > Environments > {env} > Settings > Audit and logs > Audit settings | Screenshot |
| SSPM-1.7-02 | Audit log retention period | ≥ 180d (Zone 1), ≥ 365d (Zone 2), ≥ 730d (Zone 3) | PPAC > Environments > {env} > Settings > Audit and logs > Audit settings | Screenshot |
| SSPM-1.7-03 | Tenant-level Dataverse auditing | Enabled with User Sign-In and Activity logging | M365 Admin > Settings > Org Settings > Auditing | Screenshot |

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

1. Navigate to **M365 Admin Center** > **Settings** > **Org Settings** > **Auditing**
2. Verify unified audit logging is enabled
3. Verify "User Sign-In Activity" logging is active
4. Verify "Activity" logging is active
5. **Pass criteria:** Tenant-level auditing is enabled with both sign-in and activity logging active
6. **Evidence:** Screenshot showing Org Settings auditing page with all logging options enabled

---

*Updated: February 2026 | Version: v1.3 | Classification: Verification Testing*
