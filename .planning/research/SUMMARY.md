# Project Research Summary

**Project:** Audit Configuration Validator
**Domain:** Microsoft 365 / Power Platform audit configuration validation for financial services
**Researched:** 2026-02-06
**Confidence:** HIGH

## Executive Summary

The Audit Configuration Validator is an automated validation solution that confirms audit logging is properly enabled and configured across Microsoft 365, Power Platform, and Microsoft Purview. Unlike existing solutions that analyze audit log contents (Deny Event Correlation Report), this solution validates the audit pipeline itself is working - the "pre-flight check" before you need logs for regulatory examinations.

The recommended approach follows the established FSI-AgentGov-Solutions Tier 2 pattern: PowerShell scripts for validation logic, Power Automate flows for orchestration and alerting, and Dataverse tables for status tracking. The solution spans three audit surfaces that require different APIs: tenant-level unified audit (ExchangeOnlineManagement 3.9.2+), per-environment Power Platform audit (Dataverse Web API), and audit retention policies (Security & Compliance PowerShell). All three surfaces support service principal authentication with certificates, meeting FSI audit requirements.

The critical risk is reliability of the Search-UnifiedAuditLog cmdlet, which Microsoft acknowledges "can't be completely trusted" for result completeness. This creates regulatory examination risk if validation reports audit as enabled when logging is silently failing. Mitigation requires a dual validation strategy: cross-check cmdlet results with Get-OrganizationConfig, generate canary test events to verify actual log capture, and build in 24-hour grace periods to account for audit log ingestion lag. Additional critical risks include confusing unified audit log with mailbox audit (two separate systems), missing audit gap documentation required by SEC 17a-4, and inadvertently enabling audit in the Default environment (which undermines the framework's migration strategy).

## Key Findings

### Recommended Stack

The solution requires a multi-module PowerShell approach because no single module covers all three audit surfaces (tenant, environment, retention policies). The stack emphasizes certificate-based authentication for FSI compliance and REST API-backed cmdlets to avoid deprecated WinRM dependencies.

**Core technologies:**
- **ExchangeOnlineManagement 3.9.2+**: Tenant-level unified audit status via Get-AdminAuditLogConfig, mailbox audit validation, and retention policy management via Get-UnifiedAuditLogRetentionPolicy. Version 3.x is GA (Jan 2026), REST API-backed, supports certificate authentication without WinRM.
- **Microsoft.PowerApps.Administration.PowerShell 2.0.214+**: Environment discovery via Get-AdminPowerAppEnvironment. Note: Does NOT expose audit configuration cmdlets - audit settings require separate Dataverse Web API calls.
- **Dataverse Web API v9.2**: Direct access to Organization table properties (isauditenabled, auditretentionperiodv2, isuseraccessauditenabled) for per-environment audit validation. OAuth 2.0 client credentials flow via MSAL.PS, requires Application User with System Customizer role.
- **MSAL.PS 4.x**: OAuth token acquisition for Dataverse Web API authentication, simplifies service principal credential flow with token caching.

**Critical version considerations:**
- ExchangeOnlineManagement 3.x requires PowerShell 7.4.0+ for v3.5.0+
- Security & Compliance PowerShell certificate authentication rolled out mid-February 2025 (GA)
- Pin to v3.x line for Exchange module, allow minor updates for security patches

**What NOT to use:**
- PnP.PowerShell (SharePoint-focused, no audit capabilities)
- Microsoft365DSC (Desired State Configuration overkill for targeted validator)
- ExchangeOnlineManagement v2.x (deprecated, replaced by v3.x in September 2022)

### Expected Features

The solution sits at the intersection of Control 1.7 (Comprehensive Audit Logging documentation), Deny Event Correlation Report (which requires working audit to analyze), and Compliance Dashboard (which aggregates compliance status). The key distinction: this validates the audit PIPELINE works, not the log CONTENTS.

**Must have (table stakes):**
- M365 unified audit log enablement check (Get-AdminAuditLogConfig)
- Per-environment Power Platform audit check (Dataverse API per environment)
- Mailbox audit on-by-default verification (Get-OrganizationConfig separate from unified audit)
- Purview audit retention policy validation (3-6 year FSI requirements, 10-year option)
- Configuration drift detection (baseline + continuous monitoring)
- Multi-source validation (single pane across M365/Power Platform/Purview)
- Zone-specific retention validation (Enterprise zone requires longer retention)
- Evidence export for examinations (CSV/JSON with SHA-256 integrity hashes)
- Scheduled validation runs (daily/weekly cadence)

**Should have (competitive differentiators):**
- SEC 17a-4(f) automatic verification requirement fulfillment (regulatory mandate for validation itself)
- FINRA 2026 compliance evidence (aligns with 2026 Annual Regulatory Oversight Report)
- Audit event type coverage validation (verify CopilotInteraction, AgentPublished events captured)
- Audit-trail alternative compliance check (2022 SEC amendment comprehensive audit option)
- Remediation automation with rollback (auto-enable with safety checks)
- Integration with Environment Lifecycle Management (auto-validate new environments)

**Defer (v2+):**
- WORM storage verification (Azure Immutable Blob validation - broker-dealer specific)
- Purview audit log ingestion delay monitoring (timestamp comparison - edge case)
- Per-agent audit trail validation (agent-level granularity - high complexity)
- Cross-tenant audit configuration comparison (multi-tenant consistency - limited use case)

**Explicit anti-features:**
- Audit log content analysis (duplicates Deny Event Correlation Report)
- Audit log search interface (duplicates Purview Audit portal)
- Historical audit log retention (storage solution, not validator)
- Real-time audit event streaming (SIEM's job)
- User activity monitoring dashboard (Control 3.2 Usage Analytics covers this)

### Architecture Approach

The solution follows the established FSI-AgentGov-Solutions Tier 2 pattern: PowerShell-first validation, Power Automate orchestration, Dataverse status tracking, and Teams/email alerting. This matches patterns from deny-event-correlation-report, scope-drift-monitor, and conditional-access-automation.

**Major components:**

1. **PowerShell Validation Scripts** (5 scripts in scripts/ directory)
   - Test-TenantAuditConfig.ps1: Unified audit log + mailbox audit
   - Test-EnvironmentAuditConfig.ps1: Per-environment retention validation
   - Test-PurviewRetention.ps1: Retention policy compliance
   - Export-AuditConfigEvidence.ps1: Quarterly evidence with SHA-256 hashes
   - Invoke-AuditConfigValidation.ps1: Orchestration wrapper

2. **Dataverse Status Tables** (4 tables with fsi_ publisher prefix)
   - fsi_audittenantconfig: Tenant-level status (unified audit, mailbox audit)
   - fsi_auditenvironmentconfig: Per-environment status with zone classification
   - fsi_purviewretentionconfig: Retention policy details
   - fsi_auditvalidationhistory: Immutable audit log (org-owned, read-only for non-admins)

3. **Power Automate Flows** (2 flows with connection references)
   - ACV-DailyValidator: Scheduled trigger (daily 6 AM UTC), runs PowerShell scripts, upserts Dataverse, creates immutable history record
   - ACV-AlertDispatcher: Dataverse trigger on validation failure, posts Teams adaptive card, sends email to compliance team

4. **Evidence Export Pipeline**
   - Quarterly exports to exports/Q1-2026/ with manifest.json
   - SHA-256 integrity hashing for examiner admissibility
   - Both machine-readable (JSON) and human-readable (PDF report) formats

**Key architectural patterns:**
- PowerShell-first validation (complex API logic in scripts, not Power Automate expressions)
- Immutable audit log table (fsi_auditvalidationhistory is org-owned, create-only)
- Connection reference abstraction (fsi_cr_* naming, portable across environments)
- Environment variable configuration (fsi_ACV_* for tenant-specific settings)
- Adaptive card alerts over webhooks (native connector, Office 365 webhooks deprecated March 31, 2026)

**Build order:** Phase 1: PowerShell scripts (Week 1), Phase 2: Dataverse schema (Week 1), Phase 3: Power Automate flows (Week 2), Phase 4: Evidence export (Week 2), Phase 5: Documentation (Week 3), Phase 6: Control 1.7 integration (Week 3)

### Critical Pitfalls

Research identified 14 pitfalls across severity levels. The 5 critical pitfalls must be addressed in Phase 1 core validation logic to avoid regulatory examination risk.

1. **Search-UnifiedAuditLog cmdlet reliability issues** (CRITICAL, Phase 1)
   - Microsoft acknowledges cmdlet "can't be completely trusted" for result completeness
   - Prevention: Dual validation with Get-OrganizationConfig, canary event generation, result set validation with SessionId paging, native API fallback for critical validations

2. **Audit log availability lag creating false negatives** (CRITICAL, Phase 1)
   - 60-90 minute typical lag (up to 24 hours documented maximum) creates false alerts immediately after enablement
   - Prevention: 2-hour minimum grace period after audit enable, suppress alerts for 24 hours post-change, tag results as "pending_confirmation" during lag window

3. **Unified audit log vs mailbox audit confusion** (CRITICAL, Phase 1)
   - Two separate systems with different scopes, both must be validated independently
   - Prevention: Check Get-OrganizationConfig AuditDisabled=False AND per-mailbox audit status, separate reporting for each system

4. **SEC 17a-4 audit gap period documentation failure** (CRITICAL, Phase 1 + Phase 3)
   - Validator detects gap but doesn't create admissible documentation explaining it
   - Prevention: Create immutable gap record (start/end/detection/remediation times), export to WORM storage, alert compliance officer immediately, flag need for compensating controls

5. **Auto-enabling audit in Default environment** (CRITICAL, Phase 2)
   - Auto-remediation in Default undermines framework strategy to migrate apps OUT of Default to Managed Environments
   - Prevention: Exclude Default from auto-enable, recommend migration instead, separate approval path requiring compliance sign-off

**Additional high-severity pitfalls:**
- Purview Audit Standard vs Premium confusion (retention gap - 180 days vs required 3-6 years)
- Power Platform Admin API rate limiting (6,000 requests / 5 minutes, requires exponential backoff)
- ExchangeOnlineManagement module version conflicts (v2.x vs v3.x breaking changes)
- Service principal connection refresh failures (90-day token expiration, silent failures)
- Breaking existing audit retention policies (Set-UnifiedAuditLogRetentionPolicy overwrites UserIds)

## Implications for Roadmap

Based on research, the roadmap must prioritize reliability over speed (multiple validation sources, grace periods) and regulatory evidence before automation (immutable gap documentation before auto-remediation). The phase structure follows dependency chains: core validation → drift detection → auto-remediation → compliance reporting.

### Phase 1: Core Validation Engine (MVP)
**Rationale:** Foundation must address all 5 critical pitfalls before building automation on top. Dual validation strategy and lag awareness prevent false positives that would undermine trust in the tool.

**Delivers:**
- PowerShell scripts with robust error handling (Test-TenantAuditConfig, Test-EnvironmentAuditConfig, Test-PurviewRetention)
- Dual validation strategy (Search-UnifiedAuditLog + Get-OrganizationConfig cross-check)
- Canary event generation for actual log capture verification
- 24-hour grace period handling for audit lag
- Separate unified audit log and mailbox audit validation
- Environment type filtering (exclude trial/developer environments)
- Module version validation (ExchangeOnlineManagement 3.x enforcement)

**Addresses features:**
- M365 unified audit log enablement check (table stakes)
- Mailbox audit on-by-default verification (table stakes)
- Zone-specific retention validation (table stakes)

**Avoids pitfalls:**
- Pitfall 1: Search-UnifiedAuditLog reliability (dual validation)
- Pitfall 2: Audit lag false negatives (grace periods)
- Pitfall 3: UAL vs mailbox confusion (separate checks)
- Pitfall 8: Module version conflicts (version enforcement)
- Pitfall 11: Trial/dev environment false positives (type filtering)

### Phase 2: Dataverse Status Tracking
**Rationale:** Required before Power Automate flows can store validation results. Immutable audit log table pattern (from environment-lifecycle-management ProvisioningLog) ensures validation history cannot be tampered with for regulatory evidence.

**Delivers:**
- Dataverse schema with 4 tables (fsi_audittenantconfig, fsi_auditenvironmentconfig, fsi_purviewretentionconfig, fsi_auditvalidationhistory)
- Immutable history table (org-owned, create-only privileges)
- Security roles (Viewer, Operator, Admin)
- Connection references (fsi_cr_dataverse, fsi_cr_exchangeonline, fsi_cr_http_azuread)
- Environment variables (fsi_ACV_TenantId, fsi_ACV_ComplianceTeamEmail, fsi_ACV_TeamsChannelId)

**Uses stack:**
- Dataverse Web API v9.2 for Organization table audit settings
- MSAL.PS for OAuth token acquisition

**Implements architecture:**
- 4 Dataverse tables with fsi_ publisher prefix
- Connection reference abstraction pattern
- Environment variable configuration pattern

**Avoids pitfalls:**
- Pitfall 13: Integration with existing solutions (shared Dataverse instance)

### Phase 3: Automated Orchestration
**Rationale:** Automates script execution and result storage. Must include connection health monitoring to avoid silent failures (Pitfall 9).

**Delivers:**
- ACV-DailyValidator Power Automate flow (scheduled trigger, script execution, Dataverse upsert)
- ACV-AlertDispatcher Power Automate flow (Dataverse trigger, Teams adaptive card, email notifications)
- Connection health monitoring (detect expired tokens before failures)
- Scheduled validation runs (daily 6 AM UTC)
- Alert delivery (Teams adaptive card + email)

**Addresses features:**
- Scheduled validation runs (table stakes)
- Multi-source validation (table stakes - aggregates all checks)
- Configuration drift detection (table stakes - baseline comparison)

**Avoids pitfalls:**
- Pitfall 9: Service principal connection refresh failures (health monitoring)

### Phase 4: Compliance Evidence Export
**Rationale:** Regulatory requirement for admissible audit gap documentation. Must be implemented before auto-remediation to ensure gaps are documented before being "fixed."

**Delivers:**
- Export-AuditConfigEvidence.ps1 script
- Quarterly evidence export (Q1-2026/, Q2-2026/, etc.)
- SHA-256 integrity hashing in manifest.json
- Human-readable report generation (PDF)
- Immutable audit gap documentation (start/end/detection/remediation timestamps)
- Purview retention label integration
- Chain of custody logging

**Addresses features:**
- Evidence export for examinations (table stakes)
- SEC 17a-4(f) automatic verification requirement (differentiator)
- FINRA 2026 compliance evidence (differentiator)

**Avoids pitfalls:**
- Pitfall 4: SEC 17a-4 gap documentation failure (immutable gap records)
- Pitfall 12: Evidence not admissible for examination (WORM storage, Purview labels)

### Phase 5: Auto-Remediation with Safety Checks
**Rationale:** Auto-enablement is valuable but must NOT be applied to Default environment (Pitfall 5) or break existing retention policies (Pitfall 10). Requires approval workflow, especially for policy modifications.

**Delivers:**
- Auto-enable audit for non-Default environments with approval workflow
- Default environment exclusion (flag for manual review + migration recommendation)
- Read existing retention policies before modifications
- Approval workflow for retention policy changes (compliance officer sign-off)
- Rollback capability for failed remediation
- Integration with Environment Lifecycle Management (post-provisioning validation hook)

**Addresses features:**
- Remediation automation with rollback (differentiator)
- Integration with Environment Lifecycle Management (differentiator)

**Avoids pitfalls:**
- Pitfall 5: Auto-enabling audit in Default environment (exclusion logic)
- Pitfall 10: Breaking existing retention policies (read before write, approval workflow)

### Phase 6: Advanced Validation Features
**Rationale:** Differentiators that provide FSI-specific value but require solid foundation from Phases 1-5.

**Delivers:**
- Audit event type coverage validation (test events for CopilotInteraction, AgentPublished)
- Purview Audit Standard vs Premium license tier detection
- WORM storage verification for broker-dealers
- Audit-trail alternative compliance check (2022 SEC amendment)
- Compliance Dashboard integration (export findings to dashboard format)

**Addresses features:**
- Audit event type coverage validation (differentiator)
- WORM storage verification (differentiator - v2 candidate)

**Avoids pitfalls:**
- Pitfall 6: Audit Standard vs Premium confusion (license tier validation)

### Phase Ordering Rationale

- **Phases 1-2 are parallel-eligible:** PowerShell scripts (Phase 1) and Dataverse schema (Phase 2) have no mutual dependencies, can be built concurrently
- **Phase 3 requires Phases 1-2 complete:** Power Automate flows orchestrate scripts (Phase 1) and write to Dataverse (Phase 2)
- **Phase 4 before Phase 5:** Evidence export (Phase 4) must capture audit gaps BEFORE auto-remediation (Phase 5) fixes them, ensuring regulatory documentation exists
- **Phase 5 is optional for MVP:** Auto-remediation provides value but is NOT required for compliance validation (read-only validation meets SEC 17a-4(f) automatic verification requirement)
- **Phase 6 is post-MVP:** Advanced features build on proven foundation, address niche use cases (WORM storage for broker-dealers only)

**Critical path:** Phase 1 → Phase 3 → Phase 4 (Core validation → Automation → Evidence export)
**MVP definition:** Phases 1-4 (validation + evidence export without auto-remediation)
**Nice-to-have:** Phase 5 (auto-remediation reduces manual effort but increases risk if not carefully implemented)

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3:** Power Automate flow configuration with Azure Automation integration for PowerShell script execution (existing solutions use different patterns - deny-event-correlation-report uses direct PowerShell, environment-lifecycle-management uses HTTP connectors)
- **Phase 5:** Default environment migration recommendation logic (requires understanding of Environment Lifecycle Management v1.1.2 zone classification and migration workflows)
- **Phase 6:** WORM storage verification (broker-dealer specific, requires research into Azure Immutable Blob Storage validation patterns and SEC 17a-4 WORM format requirements)

Phases with standard patterns (skip research-phase):
- **Phase 1:** PowerShell validation scripts follow established patterns from deny-event-correlation-report and conditional-access-automation
- **Phase 2:** Dataverse schema follows established patterns from scope-drift-monitor (fsi_ prefix, immutable history table from environment-lifecycle-management ProvisioningLog)
- **Phase 4:** Evidence export follows SHA-256 hashing pattern from deny-event-correlation-report

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | All module versions verified on PowerShell Gallery (ExchangeOnlineManagement 3.9.2 released Jan 5, 2026), cmdlet documentation current, service principal authentication patterns documented in official Microsoft Learn articles |
| Features | **HIGH** | Table stakes based on Control 1.7 requirements, differentiators aligned with SEC 17a-4 and FINRA 2026 Annual Regulatory Oversight Report, anti-features clearly bounded (no overlap with Deny Event Correlation Report) |
| Architecture | **HIGH** | Based on direct code review of 3 existing FSI-AgentGov-Solutions (scope-drift-monitor, deny-event-correlation-report, conditional-access-automation), follows established Tier 2 pattern, component naming conventions verified |
| Pitfalls | **HIGH** | All critical pitfalls sourced from Microsoft Learn official docs, community incident reports (Practical365, Michev blog), and official regulatory guidance (SEC 17a-4 text, FINRA rules), 5 critical + 5 high + 4 medium severity classification validated |

**Overall confidence:** HIGH

### Gaps to Address

Research was comprehensive but identified areas requiring validation during implementation:

- **Dataverse Application User permissions:** Can System Customizer role modify Organization.isauditenabled, or is System Administrator required? VERIFY in non-production environment before deployment (STACK.md Open Question 2).

- **Search-UnifiedAuditLog result truncation detection:** Exact behavior when result sets exceed internal limits not documented. Implement SessionId paging and ResultIndex validation, TEST with large result sets during Phase 1 to detect truncation patterns.

- **Power Automate + Azure Automation integration:** Existing solutions show varied patterns for PowerShell script execution from flows. RESEARCH best practice for FSI scenarios (Azure Automation runbooks vs HTTP trigger endpoints vs direct PowerShell connector) during Phase 3 planning.

- **Default environment migration recommendations:** How to automatically suggest target Managed Environment for Default migration. COORDINATE with Environment Lifecycle Management solution maintainers during Phase 5 to understand zone classification and environment recommendation logic.

- **Certificate rotation automation:** Does Azure Key Vault managed certificates work with Connect-ExchangeOnline -CertificateThumbprint? TEST certificate stored in Key Vault vs local certificate store during Phase 1 authentication setup (STACK.md Open Question 4).

- **Audit event type coverage validation:** Generating test CopilotInteraction and AgentPublished events programmatically requires understanding of Microsoft 365 Copilot and Agent Builder event triggers. RESEARCH test event generation patterns during Phase 6 planning if this differentiator is prioritized.

## Sources

### Primary (HIGH confidence)

**Official Microsoft Documentation:**
- [PowerShell Gallery - ExchangeOnlineManagement 3.9.2](https://www.powershellgallery.com/packages/ExchangeOnlineManagement/3.9.2) - Version verification, release date
- [Microsoft Learn - About Exchange Online PowerShell V3](https://learn.microsoft.com/en-us/powershell/exchange/exchange-online-powershell-v2?view=exchange-ps) - Module capabilities, REST API migration
- [Microsoft Learn - Turn auditing on or off](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable) - Unified audit log enablement
- [Microsoft Learn - Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies) - Purview retention requirements
- [Microsoft Learn - Configure auditing (Dataverse)](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/configure) - Dataverse Web API endpoints
- [Microsoft Learn - Service protection API limits](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits) - Power Platform throttling limits

**Regulatory Sources:**
- [FINRA Rule 4511](https://www.finra.org/rules-guidance/rulebooks/finra-rules/4511) - Books and records requirements
- [FINRA 2026 Annual Regulatory Oversight Report](https://www.finra.org/rules-guidance/guidance/reports/2026-annual-regulatory-oversight-report) - Validation emphasis
- [SEC Rule 17a-4](https://www.law.cornell.edu/cfr/text/17/240.17a-4) - Recordkeeping requirements with automatic verification clause

**Existing Solution Code:**
- FSI-AgentGov-Solutions/scope-drift-monitor/README.md - Dataverse schema patterns, connection references
- FSI-AgentGov-Solutions/deny-event-correlation-report/README.md - Evidence export with SHA-256 hashing
- FSI-AgentGov-Solutions/environment-lifecycle-management/README.md - Immutable audit log pattern (ProvisioningLog)
- FSI-AgentGov/docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md - Framework requirements

### Secondary (MEDIUM confidence)

**Community Analysis:**
- [Practical365 - Search-UnifiedAuditLog cmdlet changes](https://practical365.com/search-unifiedauditlog-cmdlet-changes/) - Cmdlet reliability issues
- [Michev - Microsoft 365 audit log latency data](https://michev.info/blog/post/5749/microsoft-365-azure-ad-audit-logs-and-reports-latency-data) - Lag timing analysis
- [Invictus-IR - DFIR experts on unified audit log reliability](https://www.invictus-ir.com/news/what-dfir-experts-need-to-know-about-the-current-state-of-the-unified-audit-log) - Forensics perspective on UAL gaps
- [Albert Hoitingh - Different types of logging – Microsoft Purview Audit](https://alberthoitingh.com/2022/05/20/different-types-of-logging-microsoft-purview-audit/) - UAL vs mailbox audit distinction

### Tertiary (LOW confidence)

**Vendor and Blog Content:**
- [PageFreezer - SEC Rule 17a-3 & FINRA Records Retention Requirements](https://blog.pagefreezer.com/sec-finra-books-records-retention-requirements/) - Retention period interpretations (vendor perspective, validate with legal)
- [Laserfiche - What Is SEC 17a-4?](https://www.laserfiche.com/resources/blog/what-is-sec-17a-4/) - Compliance overview (vendor perspective)
- [Global Relay - SEC Rules 17a-4 and 17a-3 Explained](https://www.globalrelay.com/resources/the-compliance-hub/rules-and-regulations/sec-rules-17a-4-and-17a-3-explained/) - Audit trail alternative explanation (vendor perspective, validate with 2022 SEC amendment text)

---
*Research completed: 2026-02-06*
*Ready for roadmap: yes*
