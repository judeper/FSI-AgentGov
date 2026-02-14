# Project Milestones: FSI-AgentGov Comprehensive Audit & Enhancement

## v23 Comprehensive Review & Remediation (Completed: 2026-02-14)

**Delivered:** Full-repo review and remediation covering both FSI-AgentGov and FSI-AgentGov-Solutions. Migrated all `src/` solution artifacts to companion repo (24 files across 2 rounds), resolved 3 unmerged branches (cherry-picked Agent 365 content, merged Learn Monitor URL updates, deleted superseded branch), fixed 12 issues found by 10-agent parallel review (version bumps, role names, footers, regulatory mappings, CHANGELOG catch-up, git hygiene). Framework version bumped to v1.2.41.

**Key accomplishments:**

- **src/ Migration:** Migrated 17 original + 7 ASARD solution artifacts from FSI-AgentGov src/ to 7 solution folders in FSI-AgentGov-Solutions companion repo; deleted src/ directory
- **Branch Resolution:** Cherry-picked eloquent-jang (Agent 365 capabilities summary, Agent Store Governance, MCP Server Governance, Unified Visibility Architecture); merged learn-monitor/update-14 (30+ URL redirects, eDiscovery/Sentinel notices); deleted learn-monitor/update-6
- **Companion Repo Scaffolding:** Created README + CHANGELOG for 3 new solutions, CHANGELOG for 2 existing solutions
- **Quality Fixes:** 10 non-canonical role names, 3 footer metadata values, 11 missing regulatory-mappings entries, 24 stale version footers
- **CHANGELOG:** Added [1.2.41] entry covering milestones v11-v22
- **Git Hygiene:** Removed 2 stale worktrees, deleted 5 stale branches (local + remote)
- **Version Bump:** v1.2.39c → v1.2.41 across 5 config files

**Stats:**

- 8 remediation plans executed
- Both repos committed and pushed
- Build validated: mkdocs build --strict (0 errors), verify_controls.py (71/71)
- Deferred: Excel template re-save (manual), Learn Monitor content changes (informational only)
- 1 day (2026-02-14)

**What's next:** No active milestone. Excel template re-save requires manual intervention.

---

## v22 Solutions Status Reconciliation (Completed: 2026-02-13)

**Delivered:** Fixed stale "Work In Progress" statuses in solutions-index.md for 2 solutions confirmed shipped in prior milestones — File Upload Security Configurator (v8) and Content Moderation Governance Monitor (v7). Added Production Ready admonitions to detail sections.

**Stats:**

- 1 phase, 1 plan, 3 requirements (100% satisfied — STS-01, STS-02, VAL-01)
- Documentation-only housekeeping milestone
- 1 day (2026-02-13)

**What's next:** v23 — Comprehensive Review & Remediation

---

## v21 Audit Logging Compliance Automation (Completed: 2026-02-13)

**Delivered:** Enterprise-grade audit logging compliance solution for Power Platform environments — automated detection/remediation of Purview unified audit and Dataverse audit logging gaps with Azure Automation Managed Identity auth, entity-level audit enablement, approval-gated remediation, and Dataverse compliance tracking. Complements existing ACV (v4). Maps to Control 1.7 (no new control, framework stays at 71 controls).

**Key accomplishments:**

- **Phase 1 — Helper Module & Tests:** AuditComplianceHelpers.psm1 (6 functions: Invoke-WithRetry, Get-ManagedIdentityToken, Get-DataverseToken, Invoke-DataverseRequest, Write-DataverseComplianceRecord, Send-ComplianceNotification), module manifest, Pester 5 unit tests
- **Phase 2 — Dataverse Schema:** fsi_auditenvironmentcompliance table, Python creation script, seed data docs
- **Phase 3 — Detection Runbook:** Check-AuditLoggingCompliance.ps1 with MI + Exchange Online + BAP auth, per-environment scanning, compliance determination, CSV + email output
- **Phase 4 — Remediation Runbook:** Enable-AuditLogging.ps1 with org-level + entity-level audit enablement (6 Copilot Studio entities), WhatIf, validation
- **Phase 5 — Deployment & Documentation:** Deployment guide (Azure Automation, MI permissions, scheduling), 15 testing scenarios, 10-issue troubleshooting guide
- **Phase 6 — Approval Flow:** Power Automate approval flow specification and template
- **Phase 7 — Framework Integration:** Solutions-index entry, Control 1.7 ALCA tip box, ACV cross-reference, build validated (mkdocs build --strict, verify_controls 71/71)

**Stats:**

- 7 phases, 13 plans, 21 requirements (100% satisfied — MOD-3, DET-3, REM-3, DVS-2, DPL-3, FLW-2, TST-2, FRM-3)
- Enterprise auth: System-Assigned Managed Identity in Azure Automation (evolution from lab-grade interactive in v4-v18)
- Key decisions: fsi_ prefix, upsert pattern, audit enablement only (retention out of scope), complementary to ACV
- 1 day (2026-02-13)

**What's next:** v22 — Solutions Status Reconciliation

---

## v20.5 Control Framework Expansion (Completed: 2026-02-13)

**Delivered:** 7 new controls expanding the framework from 64 to 71 controls — 3 security controls (1.26, 1.27, 1.28), 2 management controls (2.23, 2.24), and 2 reporting controls (3.11, 3.12). Each with 4 implementation playbooks and screenshot specification. Full framework integration (CONTROL-INDEX, mkdocs.yml, count references across all docs).

**Key accomplishments:**

- **Control 1.26 — Agent File Upload and File Analysis Restrictions:** Per-agent file upload enablement with zone-based restrictions to prevent data exfiltration through unmonitored file ingestion (GLBA 501(b), FINRA 4511/3110, OCC 2011-12, SEC 17a-4)
- **Control 1.27 — AI Agent Content Moderation Enforcement:** Content moderation level enforcement (Low/Medium/High) at agent and topic levels (FINRA 3110/25-07, SEC 17a-3/4, GLBA 501(b))
- **Control 1.28 — Policy-Based Agent Publishing Restrictions:** Publishing gates for DLP violations, security scan failures, incomplete approvals (SOX 302/404, FINRA 3110, OCC 2011-12, Fed SR 11-7)
- **Control 2.23 — User Consent and AI Disclosure Enforcement:** AI disclaimer toggles, custom disclosure URLs, consent acknowledgment tracking (FINRA 3110/25-07, GLBA 501(b), SEC AI Guidance)
- **Control 2.24 — Agent Feature Enablement and Restriction Governance:** Zone-based feature allowlists/denylists for generative actions, preview capabilities, tools, orchestration (SOX 302/404, FINRA 3110, OCC 2011-12, GLBA 501(b))
- **Control 3.11 — Centralized Agent Inventory Enforcement:** Automated agent discovery, mandatory registration, orphan/unmanaged agent remediation (FINRA 4511, SOX 404, OCC 2011-12, Fed SR 11-7)
- **Control 3.12 — Agent Governance Exception and Override Management:** Formal exception request/approval/monitoring with time-bound overrides and audit trails (SOX 302/404, FINRA 3110, OCC 2011-12, Fed SR 11-7)

**Stats:**

- 7 new controls, 28 playbooks (7 × 4), 7 EXPECTED.md screenshot specifications
- Framework: 64→71 controls (Pillar 1: 25→28, Pillar 2: 22→24, Pillar 3: 10→12)
- Playbook count: 256→284
- All validations pass (mkdocs build --strict, verify_controls.py 71/71)

**What's next:** v21 — Audit Logging Compliance Automation (ALCA)

---

## v19 Inactivity Timeout Enforcement (Completed: 2026-02-13)

**Delivered:** New Control 2.22 (Inactivity Timeout Enforcement) in the Management Pillar with companion solution — Cloud Flow for daily compliance scanning via BAP Admin API, PowerShell remediation script (Set-InactivityTimeout.ps1), Dataverse schema for policy management and immutable compliance persistence, zone-based maximum duration enforcement (Zone 2: ≤120 min, Zone 3: ≤60 min), and full framework integration (63→64 controls).

**Phases completed:** 1-5 (10 plans total)

**Key accomplishments:**

- **Phase 1 — Control Documentation & Playbooks (2 plans):** Created Control 2.22 documentation (10-section template) with zone-specific inactivity timeout requirements (Zone 1 optional/Zone 2 required ≤120 min/Zone 3 required ≤60 min), regulatory references (GLBA 501(b), SOX 302, FINRA 4511, NIST 800-53 AC-11/AC-12), 4 implementation playbooks (portal-walkthrough, powershell-setup, verification-testing, troubleshooting), screenshot specification (EXPECTED.md)
- **Phase 2 — Dataverse Data Model (2 plans):** Created 3 Dataverse table schemas — `fsi_environmentpolicy` (zone-based policy with required max duration), `fsi_inactivitytimeout_compliance` (immutable append-only compliance records), `fsi_inactivitytimeout_errorlog` (error tracking); environment variables (concurrency limit, notification recipients); connection references (Dataverse, BAP Admin API)
- **Phase 3 — Cloud Flow & Validation Logic (2 plans):** Created `Detect-InactivityTimeout-NonCompliance` flow template — daily scheduled scan enumerating environments via Power Platform for Admins V2, policy lookup from `fsi_environmentpolicy`, per-environment BAP Admin API privacy settings retrieval, compliance determination (no policy → Unknown, disabled → Non-Compliant, duration > max → Non-Compliant), guarded notification (email only when Non-Compliant or Unknown count > 0)
- **Phase 4 — PowerShell Remediation (2 plans):** Created `Set-InactivityTimeout.ps1` (478 lines, 7 parameters, GET-PATCH-GET pattern) with BAP Admin API PATCH, `-WhatIf` support, Dataverse audit record writing; `Test-InactivityTimeoutRemediation.ps1` Pester 5 test suite (27/27 tests passing)
- **Phase 5 — Framework Integration & Validation (2 plans):** Updated CONTROL-INDEX.md (added 2.22 row), mkdocs.yml navigation (controls + playbooks), "63→64 controls" across 20 files, "21→22 management controls", "252→256 playbooks", solutions-index.md catalog entry, hardening baseline item 30 cross-references Control 2.22; all validations pass (mkdocs build --strict, verify_controls.py 64/64, verify_language_rules.py 0 violations)

**Stats:**

- 5 phases, 10 plans, 14 requirements (100% satisfied — CTL-3, DVM-3, FLW-3, REM-2, FRM-3)
- Source: AI Implementation Specification — "Inactivity Timeout Enforcement (Policy-Driven Maximum)"
- Key artifacts: Control 2.22 doc + 4 playbooks, 3 Dataverse schema scripts, Cloud Flow template, Set-InactivityTimeout.ps1, Test-InactivityTimeoutRemediation.ps1 (27 tests)
- Controls created: 2.22 (new — framework 63→64, Pillar 2: 21→22)
- 1 day (2026-02-13)

**What's next:** v20.5 — Control Framework Expansion

---

## v18 MIME Type Restrictions for File Uploads (Completed: 2026-02-12)

**Delivered:** New Control 1.25 (MIME Type Restrictions for File Uploads) with companion solution — PowerShell module (FsiMimeControl.psm1) with 3 cmdlets (Get/Set/Test), zone-based MIME configuration templates, Dataverse plugin for server-side magic bytes validation (Zone 3), Purview DLP policy template, Sentinel KQL monitoring queries and alert rule, exception management system, and full framework integration (62→63 controls).

**Phases completed:** 1-5 (10 plans total)

**Key accomplishments:**

- **Phase 1 — Control Documentation & Playbooks (2 plans):** Created Control 1.25 documentation (10-section template) with zone-specific MIME type restriction requirements (Zone 1 baseline/Zone 2 recommended/Zone 3 regulated), 4 implementation playbooks (portal-walkthrough, powershell-setup, verification-testing, troubleshooting), screenshot specification (EXPECTED.md)
- **Phase 2 — PowerShell Module & Zone Templates (2 plans):** Built FsiMimeControl.psm1 with `Get-FsiMimeConfig`, `Set-FsiMimeConfig`, `Test-FsiMimeCompliance` cmdlets via Dataverse Web API; zone template JSONs (zone1/2/3); Pester test suite with mocked API responses
- **Phase 3 — DLP Policy & Sentinel Monitoring (2 plans):** Created Purview DLP policy template blocking executable file patterns in Power Platform locations; Sentinel KQL queries for blocked upload attempts and exception usage analysis; ARM template for high-volume blocks alert rule with MITRE ATT&CK mapping
- **Phase 4 — Dataverse Plugin & Exception Management (2 plans):** Built ValidateMimeTypePlugin.cs with config-driven magic bytes validation (PE/ELF/Mach-O detection, OpenXML verification, configurable enforcement mode); plugin deployment scripts; exception register CSV template with validation script; exception request markdown template
- **Phase 5 — Framework Integration & Validation (2 plans):** Updated CONTROL-INDEX.md (added 1.25 row), mkdocs.yml navigation, "62→63 controls" across 17 files, solutions-index.md catalog entry; all validations pass (mkdocs build --strict, verify_controls.py 63/63, verify_language_rules.py 0 violations)

**Stats:**

- 5 phases, 10 plans, 16 requirements (100% satisfied — CTL-3, MOD-3, MON-3, PLG-2, EXC-2, FRM-3)
- Source: Production-ready solution spec (PDF, 29 pages), Control ID reassigned 1.20→1.25
- Key artifacts: FsiMimeControl.psm1, zone templates (3), ValidateMimeTypePlugin.cs, dlp-policy-template.json, query-mime-blocks.kql, query-exception-usage.kql, high-volume-blocks.json, MimeConfig.json, exception templates
- Controls created: 1.25 (new — framework 62→63)
- 1 day (2026-02-12)

**What's next:** v19 — Inactivity Timeout Enforcement (Policy-Driven Maximum)

---

## v17 Agent Security Configuration Governance (Completed: 2026-02-12)

**Delivered:** Three PowerShell governance scripts automating per-agent authentication enforcement (6 SSPM items), publishing restriction validation (6 criteria), and zone-based agent access configuration verification — closing the manual attestation gap across Controls 1.1, 3.7, and 3.8. Includes drift detection, SHA-256 evidence export, adaptive card alerting, hardening baseline integration, and full framework documentation updates.

**Phases completed:** 1-4 (8 plans total)

**Key accomplishments:**

- **Phase 1 — Agent Authentication Enforcement (2 plans):** Created `Test-AgentAuthConfiguration.ps1` validating 6 SSPM items (SSPM-1.1-01 through SSPM-1.1-06) per agent via BAP/PPAC REST endpoints with zone-based logic (Zone 1 permissive, Zone 2/3 enforce "Always" auth timing), drift detection comparing against previous scan baseline, SHA-256 evidence hashing, and JSON output structured for Dataverse ingestion
- **Phase 2 — Publishing Restriction Governance (2 plans):** Created `restrict-agent-publishing.ps1` (previously phantom — listed in README but file didn't exist) validating 6 publishing criteria (Environment Maker role removal, authorized security groups, Share with Everyone disabled, DLP connector blocking, Managed Environment sharing limits, approval workflow); integrated with `Invoke-HardeningBaselineCheck.ps1` items 1-6 cross-reference; SHA-256 evidence export
- **Phase 3 — Zone Access Validation (2 plans):** Created `Test-ZoneAgentAccess.ps1` with 4 check groups (agent access policy, admin exclusion group, deployment groups, web search control); validates M365 Admin Center settings against zone policy (Zone 1: all agents, Zone 2: Org + MS verified, Zone 3: Org only); drift detection with baseline comparison; companion adaptive card template (`src/adaptive-card-zone-access-alert.json`) for Teams webhook notifications
- **Phase 4 — Framework Integration & Validation (2 plans):** Added tip admonitions to Controls 1.1 (2 tips: auth enforcement + publishing restriction), 3.7 (1 tip: publishing restriction), 3.8 (1 tip: zone access validation); added Agent Security Configuration Governance entry to solutions-index.md; updated hardening baseline playbook items 1-6 with automation reference; cleaned governance README (removed 3 phantom scripts, added 5 missing UASD scripts); all validations pass (mkdocs build --strict, verify_controls.py 62/62, verify_language_rules.py 0 violations across 493 files)

**Stats:**

- 4 phases, 8 plans, 12 requirements (100% satisfied — AUTH-3, PUB-3, ZAV-3, FRM-3)
- Source: Three pending todos from v16 research addressing manual attestation gaps
- Key artifacts: `Test-AgentAuthConfiguration.ps1`, `restrict-agent-publishing.ps1`, `Test-ZoneAgentAccess.ps1`, `src/adaptive-card-zone-access-alert.json`
- Controls modified: 1.1, 3.7, 3.8
- Playbooks modified: configuration-hardening-baseline/index.md
- Reference docs modified: solutions-index.md, scripts/governance/README.md
- 1 day (2026-02-12)

**What's next:** Define next milestone or assess backlog.

---

## v16 Unrestricted Agent Sharing Detector (Completed: 2026-02-12)

**Delivered:** Continuous agent sharing compliance solution using BAP APIs to detect unsafe sharing configurations across Power Platform environments, record violations in Dataverse, drive remediation through Power Automate with approval workflows, and enforce time-bound exceptions via an Exception Manager canvas app. Complements the existing Agent Access Governance Monitor (AAM = environment-level; UASD = per-agent sharing). Includes 5-table Dataverse schema, detector flow with 5 violation rules, remediation flow with exception suppression, dual-approval exception lifecycle, deployment scripts, violation export with SHA-256 evidence hashing, and full framework integration.

**Phases completed:** 1-5 (10 plans total)

**Key accomplishments:**

- **Phase 1 — Solution Infrastructure (2 plans):** Created Dataverse schema with 5 tables (`fsi_AgentSharingSetting`, `fsi_SharingViolation`, `fsi_SharingException`, `fsi_ApprovedSecurityGroup`, `fsi_SharingPolicy`) using `fsi_` prefix, 6 solution-specific option sets (`fsi_UASD_*`), reusing `fsi_acv_zone`/`fsi_acv_severity` shared option sets; defined 4 environment variables and 2 connection references; documented seed policy row
- **Phase 2 — Detection Engine (2 plans):** Built detector flow JSON (`fsi-UASD-Detector-ScanAgents`) with scheduled trigger, BAP API agent enumeration and principal retrieval, Dataverse upsert, all 5 violation rules (ORG_WIDE_SHARING, PUBLIC_INTERNET_LINK, UNAPPROVED_GROUP, EXCESSIVE_INDIVIDUAL, CROSS_TENANT_ACCESS); created `Invoke-SharingAudit.ps1` on-demand PowerShell script; built adaptive card template for Teams notifications
- **Phase 3 — Remediation & Exception Management (2 plans):** Built remediation flow triggered on violation creation with exception check and approval/auto paths (auto only for PUBLIC_INTERNET_LINK when enabled), BAP PATCH to overwrite principals; built exception approval flow with sequential dual approval (Security → Data Owner) and 90-day default expiration; created Exception Manager canvas app JSON; built `Import-ApprovedSecurityGroups.ps1` with idempotent CSV/JSON upsert
- **Phase 4 — Deployment & Operations (2 plans):** Created `Deploy-DetectionFlow.ps1` and `Deploy-RemediationFlow.ps1` deployment scripts with connection reference binding; built `Export-ViolationReport.ps1` with CSV/JSON output and `-IncludeEvidence` SHA-256 hash support; created comprehensive deployment guide with prerequisites and validation checklist
- **Phase 5 — Framework Integration & Validation (2 plans):** Added UASD entry to solutions-index.md with regulatory alignment (FINRA 4511, SOX 404, SEC 17a-3/4, GLBA 501(b)); updated Controls 1.1 and 3.8 with tip admonitions; created architecture overview doc; updated mkdocs.yml nav; reconciled AAM status (WIP → Completed); all validations pass (mkdocs build --strict, verify_controls.py 62/62, verify_language_rules.py 0 violations)

**Stats:**

- 5 phases, 10 plans, 16 requirements (100% satisfied — INFRA-3, DET-3, REM-3, OPS-3, FRM-3, VAL-1)
- Source: User-provided Unrestricted Agent Sharing Detector AI Implementation Spec
- Key artifacts: 3 schema/config scripts, 3 flow JSONs, 1 canvas app JSON, 1 adaptive card JSON, 4 governance PowerShell scripts, deployment guide, architecture overview
- Controls modified: 1.1, 3.8
- 1 day (2026-02-12)

**What's next:** Define next milestone or assess backlog.

---

## v15 Agent Usage & Performance Workbook (Completed: 2026-02-11)

**Delivered:** Deployable Azure Monitor Workbook template for Copilot Studio agent usage, performance, and error visibility — solving the ALM separation-of-duties gap for FSI organizations where production Analytics tab access is restricted. Includes telemetry schema documentation, 3-tab workbook JSON template, deployment guide, customization guide, and full framework integration across 3 controls and the solutions catalog.

**Phases completed:** 1-4 (8 plans total)

**Key accomplishments:**

- **Phase 1 — Telemetry Research & KQL Query Library (2 plans):** Documented native Copilot Studio Application Insights telemetry schema (customEvents types: BotMessageReceived, BotMessageSend, TopicStart, etc.), built parameterized KQL query library covering all 3 workbook tabs (~23 queries across Usage/Business Value, Performance/Errors, Operational Health)
- **Phase 2 — Workbook Template Development (2 plans):** Built deployable `src/agent-usage-workbook.json` (46.7KB, 795 lines) with 3-tab layout, global parameters (time range, agent ID, channel), zone-aware thresholds on 6 KPI items, 25 query items (Q01-Q23), enhanced header with version and prerequisites
- **Phase 3 — Deployment & Customization (2 plans):** Created deployment guide with RBAC configuration (Application Insights Reader role), manual import and ARM template instructions, validation checklist; created customization guide for extending workbook with custom telemetry panels, adjusting thresholds per zone, and integrating organization-specific KPIs
- **Phase 4 — Framework Integration & Validation (2 plans):** Added tip admonitions to Controls 3.2, 3.9, 2.9 linking to workbook solution; added complete solutions-index.md catalog entry (overview row, detail section, version history); updated workbook playbook status to Complete; all validations pass (mkdocs build --strict, verify_controls.py 62/62, verify_language_rules.py 0 violations)

**Stats:**

- 4 phases, 8 plans, 12 requirements (100% satisfied — TEL-2, WBK-4, DEP-2, FRM-3, VAL-1)
- Source: Deferred v13 todo — refined as v15 with 12 requirements
- Key artifacts: `src/agent-usage-workbook.json`, telemetry-schema.md, deployment-guide.md, customization-guide.md
- Controls modified: 2.9, 3.2, 3.9
- 1 day (2026-02-11)

**What's next:** Define next milestone or assess backlog.

---

## v14 SSPM Control Coverage Remediation (Completed: 2026-02-11)

**Delivered:** Remediated SSPM control coverage gaps across 7 controls (1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8) identified by SSPM alert-to-control mapping analysis. Aligned all 27 in-scope SSPM alerts to framework coverage (controls, playbooks, verification criteria), created a PowerShell hardening baseline verification script, and updated reference catalogs.

**Phases completed:** 1-4 (8 plans total)

**Key accomplishments:**

- **Phase 1 — Control SSPM Alignment (2 plans):** Bumped Control 3.7 to v1.3, audited 27 SSPM alert configuration points against verification criteria in 7 controls, added GLIC cross-reference advisory notes to Controls 1.1 and 1.11
- **Phase 2 — Hardening Baseline Production (2 plans):** Added automation feasibility classification (Automated/Semi-Automated/Manual Attestation) to 27-item checklist, created `Invoke-HardeningBaselineCheck.ps1` PowerShell verification script for automatable items (audit logging, environment provisioning), documented evidence export procedures with SHA-256 hash pattern and zone-specific review cadence
- **Phase 3 — Playbook Remediation (2 plans):** Remediated 7 portal-walkthrough playbooks with SSPM-detectable portal steps, updated 7 verification-testing playbooks with 31 SSPM-informed test cases, added Configuration Hardening Baseline cross-links to Section 8 of all 7 SSPM-mapped controls
- **Phase 4 — Reference Updates & Validation (2 plans):** Added Configuration Hardening Baseline to solutions-index.md, updated solutions-coverage-gaps.md (20→23 covered controls, 32.3%→37.1%), enhanced CONTROL-INDEX.md with Hardening Baseline references for all 7 controls, all validations pass (mkdocs build --strict, verify_controls.py 62/62, verify_language_rules.py 487 files 0 violations)

**Stats:**

- 4 phases, 8 plans, 13 requirements (100% satisfied — CTL-3, HBL-3, PLB-3, REF-2, VAL-2)
- Source: SSPM alert-to-control mapping analysis — 42 alerts analyzed, 27 in-scope
- Controls modified: 1.1, 1.7, 1.8, 1.11, 1.18, 2.1, 3.7, 3.8
- 1 day (2026-02-11)

**What's next:** Deferred v13 (Agent Usage & Performance Workbook) or new milestone.

---

## v13 Agent Usage & Performance Workbook (Deferred: 2026-02-11)

**Status:** DEFERRED — Roadmap was created (3 phases, 6 plans, 11 requirements) but no phases were executed. Shelved to prioritize v14 (SSPM Control Coverage Remediation).

**Planned scope:** Deployable Azure Monitor Workbook template for Copilot Studio agent usage, performance, and error visibility — solving the ALM separation-of-duties gap for FSI organizations.

**Deferred deliverables:** Workbook JSON template (3 tabs), KQL queries, framework integration (Controls 3.2, 3.9, 2.9), deployment guide, customization guide, ALM scenario documentation.

**Pending todo:** [Agent Usage & Performance Workbook for Enterprise ALM](todos/pending/2026-02-11-agent-usage-workbook-for-enterprise-alm.md) — to be picked up in a future milestone.

---

## v12 Quality & Consistency Polish (Completed: 2026-02-11)

**Delivered:** Closed 16 polish-level gaps identified by codebase mapping analysis after v11 Technical Remediation. Fixed user-facing broken links, completed Azure AD → Microsoft Entra ID rename and Tier → Zone terminology sweeps, built quality automation infrastructure (language linter, CI integration), and performed housekeeping (stale file cleanup, screenshot specs, Excel count fix).

**Phases completed:** 1-3 (8 plans total)

**Key accomplishments:**

- **Phase 1 — Broken Links & Content Consistency (4 plans):** Removed exclude_docs entries blocking regulatory-mappings.md and CONTROL-INDEX.md from navigation, fixed 5 docs linking to excluded files, synced solutions-integration.md with solutions-index.md, completed Azure AD → Microsoft Entra ID rename (zero instances remaining), completed Tier/Level → Zone normalization across all controls and playbooks (~80+ additional instances swept in gap closure)
- **Phase 2 — Quality Automation & Infrastructure (2 plans):** Created scripts/verify_language_rules.py linter catching prohibited FSI phrases, added verify_controls.py step to CI publish workflow, synced control-setup-template.md heading and footer conventions, updated verify_templates.py for current canonical footer values, added playbook existence validation (4 files per control) to verify_controls.py
- **Phase 3 — Housekeeping (2 plans):** Deleted 10 stale root output files (build_*.txt, verify_*.txt) and added .gitignore patterns, created EXPECTED.md screenshot specs for 10 missing controls (1.22-1.24, 2.17-2.21, 3.10, 4.7), updated v11 REQUIREMENTS.md checkboxes to reflect delivery status, fixed Excel expected control count from 61 to 62

**Stats:**

- 3 phases, 8 plans, 16 requirements (100% satisfied — BLK-3, CSW-4, QAI-5, HSK-4)
- Gap source: codebase mapping analysis across tech, architecture, quality, and concern dimensions
- 1 day (2026-02-11)

**What's next:** Framework at production quality through v12. All polish gaps closed.

---

## v11 Technical Remediation (Completed: 2026-02-11)

**Delivered:** Comprehensive remediation of 107 findings and 42 gaps identified by full technical audit of all solutions (CAA, DEC, ELM, PCG), framework docs, reference docs, operational playbooks, control implementation playbooks, and scripts. Fixed runtime deployment failures, regulatory citation errors, terminology drift, cross-reference gaps, PowerShell bugs, and backfilled missing guides.

**Phases completed:** 1-6 (12 plans total)

**Key accomplishments:**

- **Phase 1 — Critical Runtime Fixes:** Fixed CAA Dataverse column mismatches (fsi_result_json + 6 missing columns), corrected documentation URL slugs, created 3 missing private helper scripts, aligned FSI-* policy naming convention; rewrote DEC deployment guide for v2.0 Dataverse architecture, fixed severity/zone option set mismatches, updated Power BI playbook to Dataverse connector, eliminated hardcoded zone values
- **Phase 2 — Regulatory & Technical Accuracy:** Corrected Pillar 1 control count (23→24) and total (61→62), audited FINRA 25-07 references, fixed SEC 17a-3/4 retention period language (3-year vs 6-year), resolved Zone 3 retention period conflict, fixed solution count inconsistencies; corrected ELM Lab 3/5 instructions, PCG upsert patterns, replaced "Azure AD" with "Microsoft Entra ID", fixed DEC column name prefixes
- **Phase 3 — Terminology & Version Normalization:** Standardized Zone 1/2/3 terminology across all playbooks (replaced Tier/Level variants), normalized role names to role-catalog.md canonical forms, added Zone/Tier/Level equivalence mapping note, aligned version footers to v1.2.38, added glossary entries (Agent 365, Entra Agent ID, Blueprint, Sponsor, DSPM), fixed framework document count
- **Phase 4 — Cross-Reference & Link Integrity:** Added CAA solution references to Controls 1.23 and 1.18, added Control 1.8 to DEC coverage, added AAM/FUS to solutions-coverage-gaps.md, fixed evidence-pack-assembly.md file paths, replaced legacy "Gap N" placeholders with actual references, fixed ELM environment group naming and solutions-index version numbers
- **Phase 5 — Script & Code Fixes:** Fixed $isBlock variable scoping in Test-PolicyCompliance.ps1, corrected CAA module manifest exports, fixed Control 4.7 PowerShell SKU filter to use SkuPartNumber, marked pseudocode cmdlets in ELM promotion gates, aligned cross-solution integration parameter names, added Search-UnifiedAuditLog pagination warnings
- **Phase 6 — Gap Backfill & Design Improvements:** Created CAA end-to-end deployment guide, documented ELM approval flow implementation, added parent control caveats to Pillar 4 portal walkthroughs, added DSPM portal deployment steps, interlinked spec-level playbooks, added FAQ timeline reconciliation note, fixed footnote markers in governance-ops, removed quick-start emojis

**Stats:**

- 6 phases, 12 plans, 46 requirements (100% satisfied — 38 core + 8 advisory)
- Audit scope: 19 solutions, 62 controls, ~250 playbooks, 12 framework docs, 21 reference docs, 30 operational playbooks
- Findings addressed: 20 Critical/High, 36 Medium, 51 Low
- 2 days (2026-02-10 → 2026-02-11)

**What's next:** Solution series and technical remediation complete (v1-v11). Framework at production quality.

---

## v10 Conditional Access Automation (Shipped: 2026-02-10)

**Delivered:** Complete Conditional Access policy lifecycle management solution with Tier 2 governance infrastructure — PowerShell module modernization, Dataverse persistence, Power Automate daily compliance scanning with drift detection, Teams alerting, SHA-256 evidence export, and framework integration for Controls 1.11, 1.23, and 1.18.

**Phases completed:** 1-4 (14 plans total)

**Key accomplishments:**

- Built CAAClient PowerShell module (v1.1.0) with 5 public functions, Tier 2 conventions (#Requires, ErrorAction, SupportsShouldProcess), and Graph session management
- Validated all 8 zone-specific CA policy templates against Graph API v1.0 schema, replaced hardcoded app IDs with placeholders, added metadata blocks
- Created zone lookup integration with ELM Dataverse table + naming convention fallback for zone-appropriate policy deployment
- Implemented policy drift detection comparing deployed CA policies against baselines across 5 dimensions (state, conditions, grants, sessions, additions/removals) with zone severity escalation
- Deployed Dataverse infrastructure: 3 tables (baselines, validation history, violations) reusing ACV option sets, 7 environment variables, 4 connection references
- Built Python deployment scripts (caa_client.py, create_dataverse_schema.py, create_environment_variables.py, create_connection_references.py, deploy.py) — all idempotent with dry-run support
- Created Power Automate daily compliance scan flow with Azure Automation runbook, 30s job polling, Dataverse persistence, and alert routing
- Delivered Teams adaptive card alerts with severity classification (Zone 3 CRITICAL, Zone 2 HIGH, Zone 1 WARNING)
- Built ELM provisioning hook flow for auto-deploying zone-appropriate CA policies to newly provisioned environments
- Delivered SHA-256 integrity-hashed compliance evidence export (Export-CAAComplianceEvidence.ps1 + Test-EvidenceIntegrity.ps1)
- Integrated into framework: Control 1.11 tip admonition, solutions-index.md catalog entry (Completed), Compliance Dashboard feed with worst-of-two resolution (SSC vs CAA)
- Complete companion repo documentation suite: SCHEMA, EVIDENCE_EXPORT, prerequisites, troubleshooting, CHANGELOG v1.1.0

**Stats:**

- 4 phases, 14 plans, 18 requirements (100% satisfied)
- 1 day (2026-02-10)

**What's next:** Solution series complete (v4-v10). All 6 Tier 2 solutions built, integrated, and documented.

---

## v9 Cross-Solution Integration (Shipped: 2026-02-10)

**Delivered:** Integration layer wiring 5 Tier 2 governance solutions (ACV, SSC, AAM, CMM, FUS) into the Compliance Dashboard, ELM provisioning hooks for auto-registration, and unified evidence export with SHA-256 hash chain for regulatory examinations.

**Phases completed:** 1-5 (16 plans total)

**Key accomplishments:**

- Created IntegrationConfig.psm1 shared module with solution-to-control mappings (5 solutions → 7 controls), status translation (Choice/String/Percentage → 4-value CD scale), and canonical zone/severity constants
- Built Sync-SolutionAssessments.ps1 batch pipeline querying 5 solution validation tables, translating status, and upserting CD assessment records with same-day deduplication
- Delivered CD-SolutionFeedCollector Power Automate flow template for daily automated dashboard feeds
- Created ELM-SolutionInitializer event-driven flow triggering on ProvisioningCompleted (action=13) to auto-register environments in ACV's registry
- Built Register-ProvisionedEnvironment.ps1 PowerShell alternative for ACV registration with idempotent upsert
- Delivered Export-UnifiedComplianceEvidence.ps1 aggregating governance data from all solutions into timestamped evidence packages
- Created Test-UnifiedEvidenceIntegrity.ps1 for SHA-256 hash chain verification of evidence packages
- Complete documentation suite: SCHEMA_CONTRACT, STATUS_MAPPING, CONFIGURATION, TROUBLESHOOTING, ELM_INTEGRATION, EVIDENCE_EXPORT, SCORE_CALCULATOR_UPDATE
- Updated framework docs: solutions-integration.md (architecture diagram, cross-solution section), solutions-index.md (new solution entry)

**Stats:**

- 5 phases, 16 plans, 18 requirements (100% satisfied)
- 1 day (2026-02-10)

**What's next:** Series complete (v4-v9). All Tier 2 solutions built, integrated, and documented.

---

## v8 File Upload Security Configurator (Shipped: 2026-02-10)

**Delivered:** Automated per-agent file upload validation against zone governance policies for Control 1.14 (Data Minimization and Agent Scope Control). Binary drift detection (enabled/disabled changes), content moderation cross-check, Teams alerting, and SHA-256 compliance evidence export.

**Phases completed:** 1-4 (12 plans total)

**Key accomplishments:**

- Built per-agent file upload setting enumeration via Dataverse bot table queries with FUSClient.psm1 module
- Established zone compliance validation (Zone 1: Allowed, Zone 2: Restricted, Zone 3: Disabled by default) with severity classification
- Content moderation cross-check validates minimum moderation level when file uploads are enabled
- Created Dataverse infrastructure with file upload baselines, validation history, and violation tables (reusing ACV option sets)
- Deployed Power Automate daily drift detection with Teams adaptive card alerts and Azure Automation runbook
- Delivered SHA-256 integrity-hashed compliance evidence export for SEC 17a-4(f) examination support
- Complete docs suite: PREREQUISITES, SCHEMA, EVIDENCE_EXPORT, FLOW_SETUP, TROUBLESHOOTING
- Integrated into framework (Control 1.14 tip admonition + solutions-index.md catalog entry)

**Stats:**

- 4 phases, 12 plans, 17 requirements (100% satisfied)
- 1 day (2026-02-10)

**What's next:** v9 — Integration (ELM + Dashboard + cross-solution)

---

## v7.1 Framework Currency Reviews (Completed: 2026-02-10)

**Delivered:** Maintenance milestone addressing 4 pending todos to keep the framework current: Dataverse audit deprecation warning on Control 1.7, Agent 365 GA readiness updates across controls and architecture docs, Copilot Studio evaluation framework enhancements, and multi-source governance agent investigation recommendation (deferred to v10+).

**Phases completed:** 1-2 (5 plans total)

**Key accomplishments:**

- Control 1.7 updated with deprecation warning for Dataverse Purview audit event changes (May 2026 deadline), regulatory-mappings.md updated with Dataverse API alternatives
- agent-365-architecture.md updated with GA readiness, deployment limitations, shadow AI discovery, licensing caveats
- Controls 1.11, 2.12, 3.8 updated with Agent 365 findings; role-catalog.md notes AI Admin limitations; Defender controls (1.5, 1.6, 1.8) reviewed
- Controls 2.18, 2.8, 3.1 enhanced with Copilot Studio evaluation framework references; verification-testing playbook for 2.18 enhanced
- Multi-source governance agent investigation completed — recommendation: defer to v10+

**Stats:**

- 2 phases, 5 plans, 17 requirements (100% satisfied)
- 1 day (2026-02-10)

**What's next:** v8 — File Upload Security Configurator

---

## v7 Content Moderation Governance Monitor (Shipped: 2026-02-10)

**Delivered:** Automated validation and drift detection of Copilot Studio agent content moderation levels per governance zone for Control 1.8, with Dataverse-backed persistent state, Power Automate daily scanning, and SHA-256 compliance evidence export.

**Phases completed:** 1-4 (12 plans total)

**Key accomplishments:**

- Built per-agent content moderation level enumeration via Copilot Studio bot metadata queries
- Established zone compliance validation (Zone 1: Medium min, Zone 2: High, Zone 3: High) with severity classification
- Created Dataverse infrastructure with moderation baselines, validation history, and violation tables (reusing ACV option sets)
- Deployed Power Automate daily drift detection with Teams adaptive card alerts
- Delivered SHA-256 integrity-hashed compliance evidence export for FINRA/SEC examination support
- Integrated into framework (Control 1.8 tip admonition + solutions-index.md catalog entry)

**Stats:**

- 4 phases, 12 plans, 18 requirements (100% satisfied)
- 1 day (2026-02-10)

**What's next:** v7.1 — Framework Currency Reviews

---

## v6 Agent Access Governance Monitor (Shipped: 2026-02-10)

**Delivered:** Automated detection of unrestricted agent access across Power Platform environments with zone-based validation, drift detection, and compliance evidence export for Control 1.11.

**Phases completed:** 1-4 (12 plans total)

**Key accomplishments:**

- Built environment-level agent access setting validation with zone compliance rules
- Established Dataverse infrastructure reusing ACV option sets (fsi_acv_zone, fsi_acv_severity)
- Created daily automated scan with Teams alerting and 48-hour grace period for new environments
- Delivered compliance evidence export with SHA-256 integrity hashing
- Detect-only mode for Zone 3 (no auto-remediation per SOX/FINRA change control)

**Stats:**

- 4 phases, 12 plans, 18 requirements (100% satisfied)

**What's next:** v7 — Content Moderation Governance Monitor

---

## v5 Session Security Configurator (Shipped: 2026-02-09)

**Delivered:** Automated session security enforcement (inactivity timeouts, sign-in frequency, session lifetime) per governance zone with drift detection and compliance reporting for Control 1.23.

**Phases completed:** 1-4 (12 plans total)

**Key accomplishments:**

- Built zone-specific session lifetime enforcement (8h / 4h / 1h per Control 1.23)
- Conditional Access policy deployment and validation
- Session security drift detection with alerting
- Compliance evidence export for regulatory examinations
- Control 1.23 framework integration

**Stats:**

- 4 phases, 12 plans, 19 requirements (100% satisfied)

**What's next:** v6 — Agent Access Governance Monitor

---

## v4 Audit Configuration Validator (Shipped: 2026-02-06)

**Delivered:** Automated audit configuration validation solution for M365 and Power Platform environments with continuous monitoring, drift detection, multi-channel alerting, and SEC 17a-4(f) compliance evidence export.

**Phases completed:** 1-4 (11 plans total)

**Key accomplishments:**

- Built PowerShell tenant-level audit validation with dual strategy (cmdlet + canary event) preventing false positives
- Established Dataverse-backed infrastructure with immutable validation history and zone-specific retention rules
- Created automated daily validation via Power Automate with drift detection and multi-channel alerting (Teams + email)
- Delivered compliance evidence export with SHA-256 integrity hashing for SEC 17a-4(f) support
- Integrated solution into framework (Control 1.7 tip admonition + solutions-index.md catalog entry)
- Shipped Audit Configuration Validator v1.0.0 (18 PowerShell scripts, 7 Python scripts, 2 flows, 7 docs)

**Stats:**

- 40 files created/modified
- 11,975 lines added, 2,715 removed
- 4 phases, 11 plans, 28 requirements (100% satisfied)
- 1 day (2026-02-06)

**Git range:** `2c5dac9` → `31e5db5`

**What's next:** v5 — Session Security Configurator (Control 1.9)

---

## v3 Observability & Documentation Updates (Shipped: 2026-02-06)

**Delivered:** Production-ready Agent Observability Foundation solution with FSI-compliant telemetry, KQL queries, workbooks, alerts, and Power BI integration, plus Agent 365 architecture documentation and Q1 2026 control enhancements.

**Phases completed:** 1-7 (27 plans total)

**Key accomplishments:**

- Deployed Agent Observability Foundation solution with telemetry pipeline, 14 KQL queries, 3 Azure Monitor workbooks, and 4 alert rules
- Created Power BI semantic model with dual-grain star schema, 19 DAX measures, zone-based RLS, and Viva Insights reconciliation
- Built idempotent deployment automation (deploy-workbooks.ps1, deploy-alerts.ps1) with validation checklist
- Documented unified Agent 365 control plane and Entra Agent ID architecture with 17-control impact analysis
- Enhanced 4 controls with Q1 2026 capabilities (virtual connectors, DSPM, AI Feature Access, SharePoint Restricted Search)
- Expanded role catalog with AI Administrator and Defender XDR Admin documentation

**Stats:**

- 123 files created/modified
- 28,465 lines added, 618 removed
- 7 phases, 27 plans, 44 requirements (100% satisfied)
- 2 days from start to ship (2026-02-05 -> 2026-02-06)

**Git range:** `169986a` -> `ba5eebe`

**What's next:** v4 — MCP server, Copilot Studio agent, complete remaining WIP/planned solutions

---

## v2 Tech Debt, Architecture & Solution Completion (Shipped: 2026-02-05)

**Delivered:** Resolved all PowerShell security issues, modernized documentation architecture with breadcrumb navigation and playbook discovery, externalized monitoring configuration, and completed Compliance Dashboard and Scope Drift Monitor to production-ready status.

**Phases completed:** 1-5 (17 plans total)

**Key accomplishments:**

- Eliminated all ConvertTo-SecureString security vulnerabilities across 14 PowerShell scripts
- Added comprehensive error handling to production scripts (4 try-catch blocks)
- Enabled breadcrumb navigation and added INFO admonition boxes to all 62 control pages
- Externalized monitoring classification patterns to 391-line YAML configuration
- Completed Compliance Dashboard v1.0.0 with 2 flows, sample data, and deployment documentation
- Completed Scope Drift Monitor v1.1.0 with 3 scripts, 4 tables, 3 flows, and deployment documentation

**Stats:**

- 135 files created/modified
- 18,287 lines added, 3,210 lines removed
- 5 phases, 17 plans
- 2 days from start to ship (2026-02-04 → 2026-02-05)

**Git range:** `3c3ec36` → `54e7a24`

**What's next:** v3 — MCP server, Copilot Studio agent, complete remaining Planned solutions

---

## v1 Comprehensive Audit & Enhancement (Shipped: 2026-02-04)

**Delivered:** Complete framework audit verifying all 62 controls, Agent 365 architecture documentation, feature enhancements, regulatory validation, solutions audit with functional testing, and unified monitoring system.

**Phases completed:** 1-8 (35 plans total)

**Key accomplishments:**

- Verified all 62 controls against current Microsoft capabilities with "Last Verified: 2026-02-03" metadata
- Documented Agent 365 unified control plane architecture
- Added 5 feature enhancements (virtual connectors, DSPM, AI feature access, Defender, roles)
- Validated 7 federal regulations + 4 state AI laws
- Audited 13 solutions with status classifications (3 Completed, 1 Validated, 6 WIP, 3 Planned)
- Achieved 58/59 solution artifacts passing functional validation
- Created unified monitoring system with Learn and Regulatory adapters

**Stats:**

- 248 control playbooks + 27 advanced implementation docs
- 8 phases, 35 plans
- 33 requirements satisfied

**Git range:** See v1-MILESTONE-AUDIT.md

**What's next:** v2 — Tech debt resolution, architecture improvements, solution completion

---

*Last updated: 2026-02-12 after v18 milestone*
