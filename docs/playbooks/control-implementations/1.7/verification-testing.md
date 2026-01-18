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

*Updated: January 2026 | Version: v1.1*
