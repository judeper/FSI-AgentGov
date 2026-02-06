# Feature Landscape: Audit Configuration Validator

**Domain:** Microsoft 365 / Power Platform audit configuration validation for financial services
**Researched:** 2026-02-06
**Overall Confidence:** HIGH

---

## Executive Summary

An Audit Configuration Validator verifies that audit logging is properly **enabled and configured** across Microsoft 365, Power Platform, and Microsoft Purview, not analyzing audit log contents (that's Deny Event Correlation's job). This is the "pipeline health check" — confirming the audit trail is working before you need it for examinations.

Key insight: Financial services regulations emphasize the **validation requirement itself**. SEC 17a-4(f) requires automatic verification of the electronic recordkeeping system, and FINRA's 2026 Annual Regulatory Oversight Report emphasizes that firms must validate their audit infrastructure supports complete decision reconstruction.

This solution sits between:
- **Control 1.7 (Comprehensive Audit Logging)** - Documentation of what to audit
- **Deny Event Correlation Report** - Analysis of audit log contents
- **Compliance Dashboard** - Aggregated compliance reporting

---

## Table Stakes

Features users expect from audit configuration validation. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Confidence | Notes |
|---------|--------------|------------|------------|-------|
| **M365 Unified Audit Log enablement check** | Tenant-wide requirement | Low | HIGH | `Get-AdminAuditLogConfig` PowerShell cmdlet |
| **Per-environment Power Platform audit check** | Each environment has independent settings | Medium | HIGH | Must query each environment; no tenant-wide view |
| **Mailbox audit on-by-default verification** | Exchange communications are recordkeeping | Low | HIGH | `Get-OrganizationConfig` shows org-wide status |
| **Purview audit retention policy validation** | Retention periods must match regulatory requirements | Medium | HIGH | 3-6 year retention for FSI; 10 year option exists |
| **Admin audit log enablement** | Admin activities require separate logging | Low | HIGH | Exchange admin audit log flag |
| **Configuration drift detection** | Settings change without authorization | High | MEDIUM | Requires baseline + continuous monitoring |
| **Multi-source validation** | Single pane across M365/Power Platform/Purview | Medium | HIGH | 3+ data sources to correlate |
| **Zone-specific retention validation** | Enterprise zone requires longer retention than personal | Medium | HIGH | Aligns with framework's zone architecture |
| **Evidence export for examinations** | Examiners require proof audit is enabled | Low | HIGH | CSV/JSON export of configuration state |
| **Scheduled validation runs** | Configuration can drift; needs periodic checks | Medium | HIGH | Daily or weekly cadence standard |

### Implementation Dependencies

**PowerShell modules required:**
- `ExchangeOnlineManagement` - For M365 audit and mailbox settings
- `Microsoft.PowerApps.Administration.PowerShell` - For Power Platform per-environment checks
- `Az.OperationalInsights` - For Log Analytics workspace validation (if SIEM integration)

**API access required:**
- Microsoft Graph `AuditLog.Read.All` - For Purview audit policy access
- Microsoft Graph `Organization.Read.All` - For tenant-wide configuration
- Power Platform Admin API - For environment-level audit settings

---

## Differentiators

Features that set this solution apart for FSI. Not expected, but highly valued.

| Feature | Value Proposition | Complexity | Confidence | Notes |
|---------|-------------------|------------|------------|-------|
| **SEC 17a-4(f) automatic verification requirement** | Regulatory mandate for automatic validation | Medium | HIGH | "Verify automatically the completeness and accuracy of the processes" |
| **FINRA 2026 compliance evidence** | Report cites validation of decision reconstruction capability | Medium | HIGH | Aligns with FINRA 2026 Annual Regulatory Oversight Report |
| **Audit event type coverage validation** | Verify CopilotInteraction, AgentPublished events are captured | High | MEDIUM | Requires test event generation and validation |
| **WORM storage verification** | Broker-dealers need immutable storage confirmation | High | MEDIUM | Azure Immutable Blob Storage validation |
| **Purview audit log ingestion delay monitoring** | Detect when audit log ingestion is lagging | High | LOW | Requires timestamp comparison across sources |
| **Per-agent audit trail validation** | Confirm each agent's activity is logged | High | MEDIUM | Agent-specific audit event verification |
| **Audit-trail alternative compliance check** | Validate 2022 SEC amendment compliance option | High | MEDIUM | Comprehensive audit trail vs WORM format |
| **Adversarial pattern detection enablement** | Verify UPIA/XPIA detection is configured | Medium | MEDIUM | Defender integration with Copilot audit |
| **Remediation automation with rollback** | Auto-enable audit with safety checks | High | MEDIUM | Risk: incorrect automation could disable audit |
| **Integration with Environment Lifecycle Management** | Auto-validate audit on new environment provisioning | Medium | HIGH | Dependency: ELM v1.1.2 already exists |
| **Cross-tenant audit configuration comparison** | Multi-tenant orgs need consistency validation | High | LOW | Complex; limited use case |

### FSI-Specific Value

**Regulatory alignment features:**
- SEC 17a-4(f) automatic verification fulfillment - CRITICAL for broker-dealers
- FINRA 4511 books and records validation - Table stakes for member firms
- SOX 404 IT general controls evidence - Audit pipeline is a key control
- GLBA 501(b) safeguards documentation - Audit trail completeness proof

**Differentiation from existing solutions:**
- **Deny Event Correlation** analyzes audit LOG CONTENTS (deny events)
- **Audit Configuration Validator** validates audit PIPELINE IS WORKING
- **Compliance Dashboard** aggregates compliance SCORES across controls
- This solution provides the EVIDENCE that audit logging is configured correctly

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Audit log content analysis** | Duplicates Deny Event Correlation Report | Link to existing solution; validate CONFIG only |
| **Audit log search interface** | Duplicates Purview Audit portal | Provide export; don't rebuild search UI |
| **Historical audit log retention** | Storage solution, not validation tool | Validate retention POLICY, not store logs |
| **Real-time audit event streaming** | SIEM's job (Sentinel integration exists) | Validate SIEM integration is configured |
| **Audit log parsing/transformation** | Data engineering, not configuration validation | Export raw config state only |
| **User activity monitoring dashboard** | Control 3.2 (Usage Analytics) covers this | Focus on configuration, not usage patterns |
| **Manual audit enablement without safety checks** | Risk of misconfiguration | Require approval workflow for remediation |
| **Tenant-wide auto-remediation** | Too risky; could disable audit accidentally | Require per-environment approval |
| **Custom audit log storage** | Azure/M365 handles this; don't reinvent | Validate built-in retention policies |
| **Compliance score calculation** | Compliance Dashboard does this | Provide pass/fail for audit config only |

### Critical Boundary

**DO NOT analyze audit log contents.** That is the domain of:
- Deny Event Correlation Report (deny events)
- FINRA Supervision Workflow (supervision queue)
- eDiscovery tools (legal hold and investigation)
- Communication Compliance (policy-based content review)

This solution validates the **audit pipeline is working** so those other tools have data to analyze.

---

## Feature Dependencies

### Dependency Graph

```
Audit Configuration Validator
├── Control 1.7 (Comprehensive Audit Logging) - Documentation of what to audit
├── Compliance Dashboard - Consumes validation results as control evidence
├── Environment Lifecycle Management - Auto-validate new environments
└── Deny Event Correlation Report - Requires working audit pipeline to function
```

### Integration Points

| Integration | Direction | Purpose |
|-------------|-----------|---------|
| **Environment Lifecycle Management v1.1.2** | Validator → ELM | Validate audit on new environment provisioning |
| **Compliance Dashboard v1.0.0** | Validator → Dashboard | Push validation results as Control 1.7 evidence |
| **Deny Event Correlation Report v1.1.0** | Validator validates → DECR analyzes | DECR requires working audit log to analyze |
| **Control 1.7 documentation** | Control defines → Validator checks | Control 1.7 defines what to audit; validator confirms it's enabled |

---

## MVP Recommendation

For MVP, prioritize:

### Phase 1: Core Validation (MVP)
1. **M365 unified audit log enablement check** (table stakes, LOW complexity)
2. **Purview retention policy validation** (table stakes, MEDIUM complexity)
3. **Mailbox audit on-by-default verification** (table stakes, LOW complexity)
4. **Evidence export for examinations** (table stakes, LOW complexity)
5. **Zone-specific retention validation** (table stakes, MEDIUM complexity)

**Rationale:** These 5 features provide the minimum viable product for FSI compliance validation.

### Phase 2: Drift Detection
1. **Configuration drift detection** (table stakes, HIGH complexity)
2. **Scheduled validation runs** (table stakes, MEDIUM complexity)
3. **Alerting with SIEM integration** (differentiator, MEDIUM complexity)

**Rationale:** Drift detection is table stakes but higher complexity. Defer to Phase 2 after core validation works.

### Phase 3: Advanced Features
1. **SEC 17a-4(f) automatic verification requirement** (differentiator, MEDIUM complexity)
2. **FINRA 2026 compliance evidence** (differentiator, MEDIUM complexity)
3. **Audit event type coverage validation** (differentiator, HIGH complexity)
4. **Integration with Environment Lifecycle Management** (differentiator, MEDIUM complexity)

**Rationale:** These features provide competitive advantage for FSI but require Phase 1/2 foundation.

### Defer to Post-MVP:
- **WORM storage verification** (HIGH complexity; limited to broker-dealers only)
- **Purview audit log ingestion delay monitoring** (HIGH complexity; edge case)
- **Per-agent audit trail validation** (HIGH complexity; requires agent-level granularity)
- **Remediation automation with rollback** (HIGH complexity; requires extensive safety checks)

**Rationale:** These features are high complexity with limited ROI for MVP. Address in future releases based on customer demand.

---

## Sources

### Audit Enablement and Configuration
- [Microsoft Learn: Turn auditing on or off](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable)
- [Microsoft Learn: Manage Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing)
- [Microsoft Learn: Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies)
- [Microsoft Learn: Manage mailbox auditing](https://learn.microsoft.com/en-us/purview/audit-mailboxes)

### Regulatory Requirements
- [FINRA Rule 4511](https://www.finra.org/rules-guidance/rulebooks/finra-rules/4511)
- [FINRA 2026 Annual Regulatory Oversight Report](https://www.finra.org/rules-guidance/guidance/reports/2026-annual-regulatory-oversight-report)
- [SEC Rule 17a-4 Audit Trail Requirements](https://www.law.cornell.edu/cfr/text/17/240.17a-4)
- [PageFreezer: SEC Rule 17a-3 & FINRA Records Retention Requirements](https://blog.pagefreezer.com/sec-finra-books-records-retention-requirements)
- [Laserfiche: What Is SEC 17a-4?](https://www.laserfiche.com/resources/blog/what-is-sec-17a-4/)

### Configuration Drift and Alerting
- [CoreView: Microsoft 365 Configuration Drift Management](https://www.coreview.com/blog/configuration-drift-m365)
- [Reach Security: What is Configuration Drift? 2026 Explainer](https://www.reach.security/blog/what-is-configuration-drift-5-best-practices-for-your-teams-security-posture)

### Automated Remediation
- [Petri: AI-Scaled Attacks and Automated Remediation in Microsoft 365](https://petri.com/ai-scaled-attacks-automated-remediation-m365/)

---

*Research completed: 2026-02-06 | Confidence: HIGH (regulatory requirements, audit cmdlets) to MEDIUM (drift detection, remediation patterns)*
