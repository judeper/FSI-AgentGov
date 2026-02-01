# Changelog

All notable changes to the FSI Agent Governance Framework are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

---

## [1.2.35] — February 1, 2026 (Phase 4 Technical Review Integration)

### Overview

Integration of Phase 4 comprehensive technical review deliverables, enhancing implementation roadmap with effort estimates, adding solution development backlog, and documenting DSPM for AI naming history.

### Added

**Control 1.6 - DSPM for AI Rebranding Note:**

- Added info callout documenting naming history: "AI Hub DSPM" → "DSPM for AI" (November 2024)
- Provides historical context for customers familiar with prior terminology

**Solutions Coverage Gaps - Enhanced Roadmap:**

| Enhancement | Description |
|-------------|-------------|
| **Effort Estimates** | Added effort column (weeks) to all roadmap phases |
| **Approach Column** | Added implementation approach classification (Portal, Process, Custom Development) |
| **Phase 4 (Q4 2026)** | New maturity phase with 5 additional controls |
| **Solution Development Backlog** | Priority-ranked (P0/P1/P2) solution development queue with regulatory drivers |

New solution backlog includes:
- P0: finra-supervision-workflow, conditional-access-automation, compliance-dashboard
- P1: segregation-detector, scope-drift-monitor, rag-source-validator
- P2: coi-testing-automation, hallucination-tracker, dr-testing-framework

**GitHub Issues Resolved:**

| Issue | Repository | Solution |
|-------|------------|----------|
| #1 - FINRA 3110 Supervision Solution | FSI-AgentGov-Solutions | [finra-supervision-workflow v1.0.0](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow) |
| #2 - Conditional Access MFA Solution | FSI-AgentGov-Solutions | [conditional-access-automation v1.0.0](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation) |

**Solutions Released:**

| Solution | Version | Target Control | Description |
|----------|---------|----------------|-------------|
| **FINRA Supervision Workflow** | v1.0.0 | 2.12 | Automated supervision queue for AI agent outputs with FINRA 3110 compliance, Communication Compliance integration, SLA tracking, and SHA-256 evidence hashing |
| **Conditional Access Automation** | v1.0.0 | 1.11, 1.23, 1.18 | 8 CA policy templates for Copilot Studio, Agent Builder, M365 Copilot with zone-based requirements, drift detection, and ELM integration |

**Coverage Updates:**

| Metric | Previous | Current |
|--------|----------|---------|
| Controls with Solutions | 8 | 10 |
| Overall Coverage | 12.9% | 16.1% |
| Pillar 1 Coverage | 8.3% | 12.5% |
| Pillar 2 Coverage | 23.8% | 28.6% |

### Verified (No Changes Needed)

Phase 4 review validated 97% framework alignment with existing documentation:

| Item | Status | Version |
|------|--------|---------|
| Control 1.5 - DLP for Copilot Prompts | Already documented | v1.2.33 |
| Control 2.6 - OCC 2011-12 Clarification | Already documented | v1.2.24 |
| Control 3.8 - Copilot Hub Security Pivot | Already documented | v1.2.33 |
| DEC - x-api-key Deprecation | Already documented | v1.2.33 |
| License - M365 Copilot Business | Already documented | v1.2.33 |
| Solutions Coverage Gaps | Already documented | v1.2.34 |

---

## [1.2.34] — February 1, 2026 (Solutions Coverage Gap Analysis)

### Overview

New reference document analyzing FSI-AgentGov-Solutions coverage against the 62-control framework. Documents coverage metrics, gap classification, high-risk gaps, and implementation prioritization guidance.

### Added

**Solutions Coverage Gap Analysis (`docs/reference/solutions-coverage-gaps.md`):**

| Metric | Value |
|--------|-------|
| Total Controls | 62 |
| Controls with Deployable Solutions | 8 |
| Coverage Percentage | 12.9% |

Key sections:

- **Coverage by Pillar** - Pillar 1: 8.3%, Pillar 2: 23.8%, Pillar 3: 10.0%, Pillar 4: 0.0%
- **Gap Classification** - Three categories: Native Microsoft Features, Custom Solution Recommended, Process/Documentation Controls
- **High-Risk Gaps (Zone 3)** - 32 controls applicable to enterprise-managed agents requiring attention
- **Critical Regulatory Gaps** - FINRA 3110 supervision and OCC 2011-12 model risk management mitigation guidance
- **Implementation Roadmap** - Q1-Q3 2026 prioritization for addressing gaps

**Important Clarification:**

Many "gaps" are addressed by native Microsoft 365 and Power Platform features configured through admin portals. The gap analysis focuses specifically on deployable automation from FSI-AgentGov-Solutions. A control without a custom solution is not necessarily unimplemented.

---

## [1.2.33] — February 1, 2026 (Phase 2 Technical Accuracy Remediation)

### Overview

Phase 2 technical accuracy remediation addressing 4 items identified during research report verification. The Phase 2 report verified 45 items as accurate and identified 4 documentation gaps requiring updates.

### Added

**Control 1.5 - DLP for Copilot Prompts (Public Preview):**

| Aspect | Details |
|--------|---------|
| **Feature** | DLP for Copilot prompts (blocks sensitive data in user prompts) |
| **Status** | Public Preview (November 2025) |
| **License** | Included with M365 Copilot/Copilot Chat (no additional cost) |
| **Distinction** | Separate from DLP for files/email which requires A5/E5 |

- Prevents sensitive data (SSN, account numbers) from being submitted in AI prompts
- Uses existing SITs from DLP configuration
- Available to ALL Microsoft 365 Copilot and Copilot Chat users

**Control 3.8 - January 2026 Copilot Hub Enhancements (MC1187780):**

| Enhancement | Description |
|-------------|-------------|
| **Security Pivot** | New Security pivot on Copilot overview page in M365 Admin Center |
| **Readiness Page** | Organizes settings into Deployment Essentials, End-User Experience, Data Security |
| **Success Metrics** | Chat Active Users, Assisted Hours, Satisfaction Rate |

- Consolidates governance visibility previously spread across multiple admin center locations

**Microsoft 365 Copilot Business License (license-requirements.md):**

| Aspect | Details |
|--------|---------|
| **Price** | $21/user/month |
| **User Limit** | Up to 300 users per tenant |
| **GA Date** | December 1, 2025 |
| **Target** | SMB organizations with M365 Business SKUs |

- Added FSI applicability guidance for smaller broker-dealers, RIAs, credit unions
- Noted E5 Compliance may still be needed for comprehensive audit/retention

**DEC Playbook - x-api-key Deprecation Warning (app-insights-rai-telemetry.md):**

| Aspect | Details |
|--------|---------|
| **Deprecation Date** | March 31, 2026 |
| **Impact** | Export-RaiTelemetry.ps1 will fail after this date |
| **Migration Path** | Entra ID authentication (service principals/managed identities) |
| **Reference** | FSI-AgentGov-Solutions DEC v1.1.0 for updated scripts |

- Added danger callout with deprecation timeline
- Cross-referenced solutions repo for migration guidance

### Verified (No Changes Needed)

**Control 2.6 - OCC 2011-12 Customer Implementation:**

- Already contains explicit info box (lines 49-50) clarifying Microsoft provides infrastructure, not pre-built MRM solutions
- No update required

---

## [1.2.32] — February 1, 2026 (Research Report Remediation - Phase 1-6)

### Overview

Phases 1-6 of comprehensive research report remediation addressing regulatory citation corrections, technical architecture fixes, licensing & prerequisites updates, implementation guidance corrections, industry framework alignment, and documentation enhancements. Key fixes: NIST AI RMF Treasury position, ISO 42001 positioning, CopilotInteraction schema clarification, UPIA/XPIA detection locations, Sentinel MCP Server integration, SEC 17a-4 audit trail alternative, PAYG licensing limitation, E5 license distinctions, premium connector clarification, Azure Key Vault API retirement, approval gates architecture distinction, Service Principal security group bypass warning, Information Barriers channel agent scope, DLP enforcement phased timeline, FINOS AIGF v2.0, SR 11-7 vendor model governance, GLBA Safeguards Rule 10 elements.

### Critical Fixes

**NIST AI RMF Treasury Position Correction:**

| Location | Previous | Corrected |
|----------|----------|-----------|
| `nist-ai-rmf-crosswalk.md` | "recommended by U.S. Treasury for financial services" | "Stakeholders have expressed support for voluntary adoption; Treasury committed to clarifying applicability" |

- Treasury's December 2024 report references NIST AI RMF only when summarizing stakeholder feedback, not as a Treasury recommendation
- Updated language to accurately reflect Treasury's cautious, clarification-focused approach

**ISO/IEC 42001 Positioning Correction:**

| Aspect | Previous | Corrected |
|--------|----------|-----------|
| Relationship to NIST AI RMF | "alternative" | "complementary" |
| Section title | "Alternative Framework" | "Complementary Framework" |

- ISO 42001 and NIST AI RMF serve different purposes: ISO provides certifiable governance structures; NIST provides flexible risk identification
- Added recommended implementation approach: Begin with NIST AI RMF, formalize into ISO 42001, pursue certification

**API Deprecation Timeline Correction:**

| API | Previous Date | Corrected Date | Notes |
|-----|---------------|----------------|-------|
| Exchange Online Basic Auth (SMTP AUTH) | December 2026 | March 1 – April 30, 2026 | Applies to SMTP AUTH only; other protocols deprecated 2021-2023 |

### Phase 2: Technical Architecture Fixes

**CopilotInteraction Audit Schema Clarification (Control 1.7):**

- Added warning box clarifying audit schema captures **metadata only** (message IDs, timestamps, model info, detection flags)
- Full prompt/response content requires eDiscovery, DSPM for AI, or Communication Compliance
- Critical distinction for compliance design: audit logs provide evidence trail; eDiscovery provides content

**UPIA/XPIA Detection Location Correction (Control 1.8):**

| Location | What It Provides |
|----------|------------------|
| **Purview CopilotInteraction** | `JailbreakDetected` and `XPIADetected` boolean flags (audit trail) |
| **Defender CloudAppEvents** | Threat analysis context, attack patterns (security operations) |

- Corrected from "not in Purview" to "available in BOTH locations"
- Clarified Purview provides audit trail; Defender provides investigation context

**Sentinel MCP Server Integration (Control 3.9):**

- Updated from "No dedicated connector exists" to document Sentinel MCP Server (GA November 2025)
- Added configuration steps for MCP Server integration via Copilot Studio Tools
- Documented natural language query capabilities against Sentinel data lake
- Added requirements note: Entra authentication, AI model costs, data residency

**SEC 17a-4 Audit Trail Alternative (solutions-architecture-guide.md):**

- Added October 2022 SEC amendments (effective May 2023) documentation
- Documented two compliance approaches: WORM storage OR audit trail alternative
- Added Azure implementation options for each approach
- Clarified CFTC does not require WORM (principles-based standard)

### Phase 3: Licensing & Prerequisites Fixes

**Pay-As-You-Go (PAYG) Licensing Limitation (Control 2.1):**

- Added critical warning: PAYG does NOT satisfy Managed Environment licensing for active users
- Users without standalone Power Apps/Power Automate licenses in PAYG environments do not meet licensing requirements
- Added Microsoft Learn source citation

**E5 License Distinction (license-requirements.md):**

| License | Includes |
|---------|----------|
| Microsoft 365 E5 | Full suite: E3 + E5 Compliance + E5 Security + additional |
| Microsoft 365 E5 Compliance | Microsoft Purview suite (DLP, IRM, eDiscovery, etc.) |
| Microsoft 365 E5 Security | Microsoft Defender suite (Defender for Office 365, Endpoint, etc.) |

- Added capability matrix showing which features require which E5 variant
- Added documentation guidance for precise E5 requirement references

**Premium Connector Clarification (license-requirements.md):**

- Clarified Copilot Studio includes ALL premium connectors and Dataverse (5 GB) at no additional cost
- Power Apps/Power Automate require separate premium licensing for connectors
- Added product-specific licensing table to prevent common misconception

**Azure Key Vault API Retirement (solutions-architecture-guide.md):**

- Added warning: Pre-February 2026 APIs retire February 27, 2027
- New instances enforce Azure RBAC as default permission model
- Added migration guidance: Access Policy → RBAC transition

### Phase 4: Implementation Guidance Fixes

**Approval Gates Architecture Distinction (Control 2.3):**

- Added distinction table: Native Copilot Studio approvals vs. ALM pipeline approvals
- Copilot Studio has built-in publishing approval workflow (no custom development required)
- ALM pipeline approvals require custom Power Automate (OnApprovalStarted trigger)
- FSI recommendation: Native approvals for Zone 2, pipeline approvals for Zone 3

**Service Principal Security Group Bypass (ELM architecture.md):**

- Added critical warning: Service Principals bypass environment-level Security Group restrictions
- Service Principal can access ANY environment regardless of Security Group configuration
- Added mitigation table: RLS, column-level security, audit, credential rotation, privilege review
- Added quarterly audit requirement for Service Principal permissions
- Source citation: Zenity research on Power Platform SP permissions (June 2025)

**Information Barriers Channel Agent Scope (Control 1.22):**

| Agent Type | IB Supported |
|------------|--------------|
| M365 Copilot | ✅ Yes |
| Copilot Studio agents in Teams | ✅ Yes |
| Channel Agent | ❌ No |

- Clarified: Copilot Studio agents in Teams DO support IB; Channel Agents do NOT
- Added testing note for verifying barrier enforcement before deployment

**DLP Enforcement Phased Timeline (Control 1.5):**

| Phase | Date | Status |
|-------|------|--------|
| Soft-Enabled | January 2025 | Complete |
| Enabled | February 2025 | Complete |
| Complete | March 2025 | Complete |

- Added MC973179 reference with three-phase rollout timeline
- Documented 11 virtual governance connectors for AI capabilities

**February 2026 Pipeline Deadline (Verified):**

- Control 2.1 already has danger callout (Phase 3 verification confirmed)
- solutions-index.md already has warning
- FAQ.md already documents deadline
- No additional changes needed

### Phase 5: Industry Framework Alignment

**FINOS AIGF v2.0 Update (regulatory-mappings.md):**

- Updated from generic FINOS reference to AIGF v2.0 (released November 11, 2025)
- Added 46 agentic AI-specific risk categories:
  - Action Autonomy Risks (12 risks)
  - Tool Integration Risks (8 risks)
  - Multi-Agent Risks (9 risks)
  - Data Access Risks (10 risks)
  - Governance Gaps (7 risks)
- Added multi-agent coordination and tool chain exploitation to control mapping table

**Sardine AOF Interpretation Layer (human-in-the-loop-triggers.md):**

- Added note clarifying FSI-AgentGov mapping is an interpretation of Sardine's framework
- Original Sardine whitepaper addresses general agentic AI; specific control mappings are FSI-AgentGov extensions

**SR 11-7 Vendor Model Governance (Control 2.6):**

- Added Section V requirements: vendor models must be validated with equal rigor as internal models
- Added vendor model governance table with documentation, validation, monitoring, change assessment requirements
- Added cross-reference to SR 13-19 for third-party relationship supervision

**SOX AI Governance Framework (Control 2.6):**

- Added SOX applies implicitly through ICFR for AI systems affecting financial data
- Added PCAOB AI audit standards note (AS 1105/AS 2301 under review, July 2024 statement)
- Added AI system documentation table for SOX compliance (Agent Card, validation, change log, monitoring)

**GLBA Safeguards Rule 10 Elements (regulatory-mappings.md):**

| # | Required Element | FSI-AgentGov Control |
|---|-----------------|---------------------|
| 1 | Qualified Individual | 2.12 |
| 2 | Risk Assessment | 2.6 |
| 3 | Safeguards | Pillar 1 (1.1-1.24) |
| 4 | Service Provider Oversight | 2.7 |
| 5 | Continuous Monitoring | 3.2, 3.7 |
| 6 | Staff Training | 2.14 |
| 7 | Board Reporting | 3.3 |
| 8 | Encryption | 1.15 |
| 9 | MFA | 1.11 |
| 10 | Incident Response | 3.4, 2.4 |

- Added 30-day FTC breach notification requirement for incidents affecting 500+ customers

### Phase 6: Enhancements & Documentation

**Defender AI-SPM Updates (Control 1.24):**

- Added "Recent Enhancements" table documenting November 2025-January 2026 capabilities
- GCP Vertex AI support now GA (November 2025)
- Agent-specific security recommendations (January 2026)
- Attack path expansion for AI-specific scenarios
- Agent 365 SDK discovery (Preview)

**Sentinel Data Pathways Documentation (Control 3.9):**

- Added "Three Data Ingestion Pathways" section documenting all three primary paths:
  - Power Platform Admin Activity (administrative oversight)
  - Purview Unified Audit Log (compliance and interaction monitoring)
  - Defender CloudAppEvents (security operations)
- Added pathway selection guidance for FSI organizations
- Expanded data sources table to include Purview UAL with CopilotInteraction events

**Custom Power BI Analytics Infrastructure (Control 3.2):**

- Added custom pipeline documentation: Dataverse → Synapse Link → Data Lake → Power BI
- Added infrastructure components table with FSI considerations
- Added decision matrix: when to use native PPAC vs. custom pipeline
- Added licensing warning for Synapse Link and Power BI Premium requirements

**SharePoint Admin Agent vs. Content Governance Agent (Control 4.5):**

- Added distinction table differentiating the two agents:
  - SharePoint Admin Agent (GA November 2025): Administrative queries
  - Content Governance Agent (Preview): Content lifecycle management
- Added capability descriptions for each agent
- Added access locations

**Verified Items (Already Complete):**

- **6.4 OWASP LLM Top 10 2025** — Controls 2.7 and 2.20 already reference 2025 version (verified)
- **6.6 Agent 365 Observability SDK** — Control 3.2 already has comprehensive section (lines 175-269)
- **6.7 Schema Field Path Documentation** — DEC playbook (purview-audit-extraction.md) already documents XPIADetected and JailbreakDetected field paths
- **6.3 Channel Controls** — Plan referenced non-existent file; channel controls documented in Controls 1.5 and 2.2

### Verified Fixes (Already Applied)

The following items from Phase 1 were already correctly remediated in previous versions:

- **OCC 2021-18 Reference** — Removed in v1.2.18 (no references remain in docs/)
- **CFTC Rule 1.31 WORM** — Correctly documents WORM elimination in 2017 (v1.2.29)
- **FINRA Notice 25-07** — Correctly characterized as workplace modernization, not AI governance (v1.2.30)
- **CFPB ECOA/UDAAP Distinction** — Correctly documented with distinction table (v1.2.29)

### Files Changed

| File | Changes |
|------|---------|
| `docs/reference/nist-ai-rmf-crosswalk.md` | Treasury position correction, ISO 42001 positioning fix |
| `docs/reference/faq.md` | Exchange Basic Auth deprecation date correction |
| `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Added audit schema metadata clarification |
| `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md` | Corrected UPIA/XPIA detection locations |
| `docs/controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md` | Added Sentinel MCP Server integration path, three data pathways documentation |
| `docs/reference/solutions-architecture-guide.md` | Added SEC 17a-4 audit trail alternative, Azure Key Vault API retirement warning |
| `docs/controls/pillar-2-management/2.1-managed-environments.md` | Added PAYG licensing limitation warning |
| `docs/reference/license-requirements.md` | Added E5 license distinction table, premium connector clarification |
| `docs/reference/sharepoint-advanced-management-licensing.md` | Updated version footer |
| `docs/controls/pillar-2-management/2.3-change-management-and-release-planning.md` | Added native vs. pipeline approval workflow distinction |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/architecture.md` | Added Service Principal security group bypass warning |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/evidence-and-audit.md` | Added quarterly Service Principal audit requirement |
| `docs/controls/pillar-1-security/1.22-information-barriers.md` | Clarified Channel Agent vs. Copilot Studio IB support |
| `docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` | Added DLP enforcement phased timeline |
| `docs/reference/regulatory-mappings.md` | FINOS AIGF v2.0 update, GLBA Safeguards Rule 10 elements |
| `docs/playbooks/advanced-implementations/human-in-the-loop-triggers.md` | Added Sardine AOF interpretation layer note |
| `docs/controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md` | SR 11-7 vendor model governance, SOX AI governance |
| `docs/controls/pillar-1-security/1.24-defender-ai-security-posture-management.md` | Added recent enhancements table (GCP Vertex AI GA, January 2026 updates) |
| `docs/controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md` | Added custom Power BI analytics infrastructure section |
| `docs/controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md` | Added SharePoint Admin Agent vs. Content Governance Agent distinction |
| `docs/reference/solutions-index.md` | Fixed ELM version discrepancy (v1.1.1 → v1.1.2) in Available Solutions table |

---

## [1.2.31] — January 31, 2026 (State AI Laws Research Remediation)

### Overview

Remediation of findings from 5 state AI law research validation reports. Key corrections: Texas TRAIGA scope, NYC LL 144 effective date, NYDFS Part 500 2024 updates, and clarifications for Illinois HB 3773 and Colorado SB24-205.

### Critical Fixes

**Texas TRAIGA Scope Correction:**

- Corrected description from "High-risk AI systems, discrimination prevention" to accurately reflect narrower enacted law (HB 149)
- TRAIGA imposes substantive requirements on **state agencies only**; private sector has intent-based prohibitions only
- Added scope note clarifying TRAIGA does not require private sector impact assessments, bias audits, or consumer disclosure (unlike Colorado)

**NYC Local Law 144 Effective Date:**

- Added missing effective date: January 1, 2023 (enforcement began July 5, 2023)
- Prior documentation did not specify effective date

### Enhancements

**NYDFS Part 500 2024 Updates:**

- Added dual-signature certification requirement (April 15, 2024): Must be signed by BOTH highest-ranking executive AND CISO
- Added October 16, 2024 AI Cybersecurity Guidance reference (industry letter on AI-related risks)
- Added 24-hour extortion/ransomware payment reporting requirement

**Illinois HB 3773 Clarification:**

- Updated description to "Employment AI notice requirements (no audit mandates)"
- Clarifies Illinois requires notice but not bias audits (unlike Colorado/NYC)

**Colorado SB24-205 Clarification:**

- Added note that proposed small business exemptions (HB 25B-1009, August 2025) were not enacted
- Added note that no implementing regulations have been issued as of January 2026

### Files Changed

| File | Changes |
|------|---------|
| `docs/reference/regulatory-mappings.md` | TRAIGA scope correction, LL 144 date, NYDFS 2024 updates, IL/CO clarifications |

---

## [1.2.30] — January 31, 2026 (FINRA Research Report Remediation)

### Overview

Remediation of findings from FINRA research reports. Key corrections: communications retention period (3 years, not 6), Notice 25-07 RFI clarification, Rule 3120 testing requirements, and 2026 Annual Regulatory Oversight Report integration.

### Critical Fixes

**Retention Period Corrections (Priority 1):**

| Record Type | Previous | Corrected | Regulation |
|-------------|----------|-----------|------------|
| Communications (agent logs, chat) | 6 years | 3 years | SEC 17a-4(b)(4) |
| Financial/Accounting Records | 6 years | 6 years (unchanged) | SEC 17a-4(a) |
| Customer Account Records | 6 years | 6 years after close | SEC 17a-4(c)(e)(5) |

- Added retention period matrix to `regulatory-framework.md` and `regulatory-mappings.md`
- Updated Controls 1.7, 2.13, 4.3 with correct retention periods
- Fixed PowerShell playbook: `FSI-Communications-6Y` → `FSI-Communications-3Y` (1095 days)

**Notice 25-07 Clarification (Control 1.7):**

- Clarified FINRA Notice 25-07 is a **Request for Comment (RFI)**, not final guidance
- Updated all references to indicate "anticipated" requirements pending final rule

### New Content

**FINRA 2026 Annual Regulatory Oversight Report:**

- Added comprehensive references to December 2025 report across framework
- Integrated AI agent supervision guidance (audit trail completeness, decision reconstruction, autonomy limits)
- Updated Controls 1.7, 2.12, and regulatory mappings with 2026 Report citations

**Rule 3120 Annual Testing Requirements (Control 2.12):**

- Added new section with annual testing checklist for AI supervisory controls
- Added testing attestation template to verification-testing playbook
- Mapped testing requirements to 2026 Report examination focus

**Rule 2210 Communication Classifications:**

- Added classification table (Correspondence vs. Retail Communication vs. Institutional)
- Added Zone 3 pre-approval guidance based on communication type
- Updated Controls 2.12 and 2.21 with classification requirements

**AI Agent Autonomy Levels:**

- Added autonomy level definitions from 2026 Report (Assisted, Augmented, Automated, Autonomous)
- Added supervision requirements per autonomy level
- Updated HITL triggers playbook with autonomy-to-HITL mapping

### Enhancements

**Control 2.5 — Testing and Validation:**

- Added FINRA Notice 15-09 (algorithmic trading) as testing precedent
- Mapped algorithmic supervision principles to AI agent testing

**Control 1.9 — Data Retention:**

- Added storage tier requirements for "readily accessible" compliance
- Defined Hot/Cool/Archive storage with access time expectations

### Files Updated

| File | Changes |
|------|---------|
| `docs/framework/regulatory-framework.md` | Retention matrix, Rule 3120 section, 2026 Report reference |
| `docs/reference/regulatory-mappings.md` | Retention matrix, Rule 2210 classifications, Notice 15-09, 2026 Report |
| `docs/controls/pillar-1-security/1.7-*.md` | Retention clarification, Notice 25-07 RFI status, 2026 Report reference |
| `docs/controls/pillar-1-security/1.9-*.md` | Storage tier guidance |
| `docs/controls/pillar-2-management/2.5-*.md` | Notice 15-09 precedent |
| `docs/controls/pillar-2-management/2.12-*.md` | Autonomy levels, Rule 2210, Rule 3120 testing |
| `docs/controls/pillar-2-management/2.13-*.md` | Retention period corrections |
| `docs/controls/pillar-2-management/2.21-*.md` | Rule 2210 classifications |
| `docs/controls/pillar-4-sharepoint/4.3-*.md` | Retention period corrections |
| `docs/playbooks/control-implementations/4.3/powershell-setup.md` | Label name correction |
| `docs/playbooks/control-implementations/2.12/verification-testing.md` | Rule 3120 testing checklist |
| `docs/playbooks/advanced-implementations/human-in-the-loop-triggers.md` | Autonomy level mapping |
| `.claude/CLAUDE.md` | Version update to 1.2.30 |
| `CHANGELOG.md` | Added v1.2.30 entry |

### Verification

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: All 62 controls valid

---

## [1.2.29] — January 31, 2026 (SEC Rules Research Report Remediation)

### Overview

Remediation of findings from SEC rules research reports. Corrects CFTC WORM misattribution and enhances CFPB regulatory clarity.

### Critical Fix

**CFTC Rule 1.31 WORM Correction (`docs/reference/regulatory-mappings.md`):**

| Issue | Correction |
|-------|------------|
| CFTC WORM requirement misattributed | CFTC eliminated WORM requirement in May 2017; updated to principles-based "authenticity and reliability" standard per 17 CFR § 1.31(c) |
| Dual-registrant guidance missing | Added warning box clarifying SEC maintains WORM while CFTC uses principles-based approach |

### Enhancements

**CFPB Section Clarity (`docs/reference/regulatory-mappings.md`):**

- Added ECOA vs. UDAAP distinction table clarifying primary framework for AI credit decisions
- ECOA (Regulation B) is primary for credit decisions; UDAAP applies broadly to all consumer products
- Referenced CFPB Circulars 2022-03 and 2023-03 for adverse action notification requirements

**Control 2.19 Update:**

- Clarified CFPB Chatbots in Consumer Finance is a research report, not binding regulation
- Added note that binding chatbot regulations are pending

**SOX AI Coverage (`docs/framework/regulatory-framework.md`):**

- Added info box clarifying SOX does not explicitly address AI
- AI agents governed implicitly through existing ICFR frameworks
- Referenced PCAOB July 2024 Spotlight on GenAI research

### Research Report Findings Summary

| Report | Framework Status | Action Taken |
|--------|-----------------|--------------|
| CFTC Rule 1.31 | WORM misattributed | Critical fix - removed WORM references |
| CFPB UDAAP/ECOA | Accurate but unclear | Added distinction table |
| CFPB Chatbots | Reference lacked context | Added non-binding status note |
| SOX 302/404/802 | Accurate | Added AI coverage clarification |
| GLBA Section 501(b) | Accurate | No changes needed |

### Files Updated

| File | Changes |
|------|---------|
| `docs/reference/regulatory-mappings.md` | CFTC WORM fix, dual-registrant warning, ECOA/UDAAP distinction |
| `docs/controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md` | CFPB chatbot reference clarification |
| `docs/framework/regulatory-framework.md` | SOX AI coverage note |
| `.claude/CLAUDE.md` | Version update |
| `CHANGELOG.md` | Added v1.2.29 entry |

### Verification

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: All 62 controls valid

---

## [1.2.28] — January 31, 2026 (Research Report Remediation)

### Overview

Comprehensive remediation of outstanding items from 15 research reports across 5 categories. Key focus areas: DEC solution deprecation warnings, security control clarifications, and API deprecation timeline documentation.

### Critical Updates

**Deny Event Correlation Report Solution (FSI-AgentGov-Solutions v1.1.0):**

| Issue | Fix |
|-------|-----|
| x-api-key authentication deprecated March 31, 2026 | Added deprecation warnings to README, architecture.md, prerequisites.md, and PowerShell script |
| XPIADetected/JailbreakDetected fields incorrect | Corrected: fields not in CopilotInteraction schema; UPIA/XPIA in Defender CloudAppEvents |
| Missing CloudAppEvents integration | Added CloudAppEvents section with KQL query for prompt injection detection |
| Authentication migration path | Added complete Entra ID OAuth 2.0 migration guide in prerequisites.md |

### Security Control Updates

- **Control 1.8:** Corrected RAI telemetry table - UPIA/XPIA detections are in Defender CloudAppEvents, not Purview CopilotInteraction audit schema
- **Control 1.22:** Added warning that Information Barriers are NOT supported for Channel Agent in Teams; added compensating controls guidance

### Framework Documentation

- **FAQ:** Added new "API Deprecations and Platform Changes" section with deprecation timeline table:
  - March 31, 2026: App Insights x-api-key, Office 365 Connectors
  - April 6, 2026: Reporting Webservice
  - December 2026: Connect-ExchangeOnline Basic Auth
- **NIST AI RMF Crosswalk:** Added ISO/IEC 42001 alternative framework reference with comparison table
- **License Requirements:** Updated control count from 61 to 62

### Minor Updates

- **MCM Solution:** Added Office 365 Connectors deprecation context (informational - solution unaffected)
- **.gitignore:** Added prompts/ directory for local research prompts

### FSI-AgentGov-Solutions Updates

| Solution | Version | Changes |
|----------|---------|---------|
| `deny-event-correlation-report/` | v1.1.0 | Deprecation warnings, schema corrections, auth migration guide |
| `message-center-monitor/` | v2.1.1 | O365 Connectors deprecation context note |

### Verification

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: All 62 controls valid

---

## [1.2.27] — January 31, 2026 (ELM Technical Accuracy Remediation)

### Overview

Technical accuracy corrections for Environment Lifecycle Management playbook based on research validation. Clarifies that ProvisioningLog access controls are defense-in-depth measures, not true cryptographic immutability.

### Changed

- **architecture.md:** Changed "Immutable Audit Trail" to "Append-Only Audit Trail" with access control limitations table
- **evidence-and-audit.md:** Added "What These Controls Prevent vs. Allow" table distinguishing protected vs. unprotected threat scenarios
- **evidence-and-audit.md:** Added transparency guidance for examiner discussions recommending honest acknowledgment of System Administrator access
- **index.md:** Updated terminology from "immutable" to "append-only" in 4 locations

### Research Validation Summary

Environment Lifecycle Management v1.1.1 technical accuracy validation (71% accurate, 29% updated):

| Finding | Status | Action |
|---------|--------|--------|
| Dataverse Web API (v9.2, OData 4.0) | ✅ Accurate | No change |
| Security Roles (4-role structure) | ✅ Accurate | No change |
| Business Rules (conditional validation) | ✅ Accurate | No change |
| Immutability claims | ⚠️ Overclaimed | Corrected to "access controls" |
| Environment Groups API claim | ⚠️ Incorrect | API exists, corrected |
| Python dependency versions | ⚠️ Outdated | Updated in FSI-AgentGov-Solutions |

### Key Correction

The ProvisioningLog table uses role-based access controls that prevent standard users from modifying records. However:

- System Administrators retain full Dataverse access regardless of role configuration
- Direct API access could bypass role-based security for privileged users
- For SEC 17a-4 WORM compliance, export to Azure Blob Storage with immutability policies is required

### FSI-AgentGov-Solutions Updates

- Environment Lifecycle Management bumped to v1.1.2
- Updated Python dependencies (msal>=1.30.0, requests>=2.32.0, azure-identity>=1.18.0)
- Corrected Environment Groups API documentation

### Files Updated

| File | Changes |
|------|---------|
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/architecture.md` | Immutability → access controls |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/evidence-and-audit.md` | Added limitations table, examiner guidance |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/index.md` | Terminology updates |
| `.claude/CLAUDE.md` | Updated version and recent additions |
| `CHANGELOG.md` | Added v1.2.27 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: All 62 controls valid

### Research Reference

Research report: `prompts/04-solutions-technical/01-environment-lifecycle-management/`

---

## [1.2.26] — January 31, 2026 (Solutions Architecture Guide)

### Overview

New enterprise scalability and architecture reference documentation for FSI-AgentGov-Solutions. Documents platform limits, alternative architectures, CoE Starter Kit alignment, and operational best practices based on Microsoft Learn research.

### Added

**New Reference Documentation:**

- **Solutions Architecture Guide** (`docs/reference/solutions-architecture-guide.md`) - Comprehensive architecture reference including:
  - Platform selection guide (Power Automate vs Logic Apps vs Azure Functions)
  - Power Platform request limits by license tier
  - Microsoft Graph API throttling guidance
  - Dataverse capacity limits (December 2025 updates)
  - Power BI refresh limits for reporting solutions
  - Secret management best practices with Azure Key Vault
  - Compliance storage patterns (Azure Immutable Blob Storage for SEC 17a-4/FINRA 4511)
  - CoE Starter Kit alignment and integration guidance
  - Alternative architecture patterns (VNet isolation, streaming)

**Documentation Cross-References:**

- Added Architecture and Scalability section to Solutions Index
- Added CoE Starter Kit Alignment section to Solutions Integration
- Added Scalability Considerations section to Deny Event Correlation Report playbook

### Files Updated

| File | Changes |
|------|---------|
| `docs/reference/solutions-architecture-guide.md` | New architecture reference document |
| `docs/reference/solutions-index.md` | Added Architecture and Scalability section |
| `docs/framework/solutions-integration.md` | Added CoE Starter Kit alignment, architecture guide link |
| `docs/playbooks/advanced-implementations/deny-event-correlation-report/index.md` | Added scalability considerations section |
| `mkdocs.yml` | Added solutions-architecture-guide to navigation |
| `CHANGELOG.md` | Added v1.2.26 entry |

### Research Sources

- [Integration platform options in Azure](https://learn.microsoft.com/en-us/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs)
- [Microsoft Graph throttling limits](https://learn.microsoft.com/en-us/graph/throttling-limits)
- [Power Automate limits](https://learn.microsoft.com/en-us/power-automate/limits-and-config)
- [Dataverse capacity-based storage](https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage)
- [Power BI data refresh](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data)
- [Azure Immutable Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)
- [Key Vault secret rotation](https://learn.microsoft.com/en-us/azure/key-vault/secrets/tutorial-rotation)
- [CoE Starter Kit overview](https://learn.microsoft.com/en-us/power-platform/guidance/coe/overview)

---

## [1.2.25] — January 31, 2026 (February 2026 Pipeline Deadline Documentation)

### Overview

Added critical compliance deadline documentation based on Pipeline Governance Cleanup technical validation research. The February 2026 Managed Environment enforcement for pipeline targets is a Microsoft-enforced deadline with automatic enablement and licensing implications.

### Added

- **Control 2.1 Critical Warning Section** - Added "Critical Deadline: February 2026 Pipeline Requirement" section with danger callout box documenting automatic Managed Environment enablement for pipeline targets, licensing implications, and required actions
- **Solutions Index Urgency Context** - Added warning callout to Pipeline Governance Cleanup section highlighting the February 2026 deadline and linking to Control 2.1

### Research Validation

Pipeline Governance Cleanup solution technical accuracy validation (87.5% of claims validated):

- February 2026 Managed Environment deadline: ✅ CONFIRMED (Microsoft Learn: Admin Deployment Hub)
- PAC CLI `pac admin list --json` command: ✅ ACCURATE
- `pac pipeline list` no JSON support: ✅ ACCURATE
- Microsoft Graph integration (Mail.Send, Send-MgUserMail): ✅ ACCURATE
- PAC CLI authentication methods: ✅ ACCURATE
- Pipeline detection directionality: ⚠️ CLARIFIED (Dataverse API access available with host authentication)
- DeploymentPipeline table API access: ⚠️ CLARIFIED (Dataverse Web API available, not public REST API)

### Files Updated

| File | Changes |
|------|---------|
| `docs/controls/pillar-2-management/2.1-managed-environments.md` | Added February 2026 pipeline deadline critical warning section |
| `docs/reference/solutions-index.md` | Added urgency warning to Pipeline Governance Cleanup section |
| `.claude/CLAUDE.md` | Updated version and recent additions |
| `CHANGELOG.md` | Added v1.2.25 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: All 62 controls valid

### Research Reference

Research report: `prompts/04-solutions-technical/02-pipeline-governance-cleanup/`

---

## [1.2.24] — January 31, 2026 (Pillar 2 Management Controls Technical Accuracy Clarifications)

### Overview

Technical accuracy improvements for 6 Pillar 2 Management Controls based on research validation. Clarifies distinction between built-in platform capabilities and custom implementation requirements.

### Changed

- **Control 2.3 (Change Management):** Clarified that approval gates require Power Automate integration rather than being built-in ALM pipeline feature. Added info box explaining OnApprovalStarted trigger requirement. Added Implementation column to capability table.
- **Control 2.6 (Model Risk Management):** Clarified Microsoft provides infrastructure platforms that can support MRM but organizations must design their own MRM frameworks. Added info box distinguishing infrastructure vs MRM solution. Split Key Configuration Points into organization-designed and platform-enabled sections.
- **Control 2.9 (Performance Monitoring):** Added explicit "Built-In vs Custom Monitoring Capabilities" table distinguishing native Copilot Studio analytics from custom RAI telemetry implementation. Added warning that hallucination tracking and RAI metrics require Azure AI Evaluation SDK or custom Application Insights events.
- **Control 2.16 (RAG Source Integrity):** Clarified SharePoint provides basic features (sync, permissions, versioning) but comprehensive integrity validation (checksums, drift detection) requires custom implementation. Added built-in vs custom capabilities table.
- **Control 2.17 (Multi-Agent Orchestration):** Clarified orchestration limits are design patterns requiring custom implementation, not platform-enforced constraints. Added warning that Copilot Studio does not provide built-in circuit breakers, depth limits, or financial stop-loss controls.
- **Control 2.21 (AI Marketing Claims):** Reframed as process/policy control using general-purpose tools rather than specialized compliance system configuration. Added note that no FINRA/SEC-specific compliance tools exist in Microsoft 365.

### Validated (No Changes Needed)

All regulatory citations in these controls were previously validated:
- OCC 2011-12, Fed SR 11-7 (Control 2.6)
- FINRA 4511, SOX 404, GLBA 501(b), SEC 17a-4 (Control 2.3)
- SEC Marketing Rule 206(4)-1, FINRA 2210 (Control 2.21)

### Files Updated

| File | Changes |
|------|---------|
| `docs/controls/pillar-2-management/2.3-change-management-and-release-planning.md` | Clarified approval gates implementation |
| `docs/controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md` | Clarified infrastructure vs MRM framework |
| `docs/controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md` | Added RAI telemetry distinction |
| `docs/controls/pillar-2-management/2.16-rag-source-integrity-validation.md` | Clarified built-in vs custom integrity features |
| `docs/controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md` | Clarified design patterns vs platform enforcement |
| `docs/controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md` | Reframed as process/policy control |
| `CHANGELOG.md` | Added v1.2.24 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: All 62 controls valid

### Research Reference

Research report: `prompts/02-documentation-technical/02-pillar-2-management/`

---

## [1.2.23] — January 31, 2026 (Pillar 4 SharePoint Controls Technical Accuracy Updates)

### Overview

Technical accuracy enhancements for all 7 Pillar 4 SharePoint Controls (4.1-4.7) based on comprehensive validation research. All controls validated as technically accurate; updates add 2025-2026 feature documentation, technical depth, and risk contextualization.

### Added

**Control Updates:**

- **Control 4.1 (RCD):** RCD reindexing latency notes, site admin control (January 2026), recent interaction discovery exception
- **Control 4.2 (Site Access Reviews):** SharePoint vs. Entra ID Access Reviews comparison table, DAG report integration details, email template customization (December 2025)
- **Control 4.3 (Retention):** Dual retention strategy guidance (policies + labels), Site Lifecycle Policy clarification, Copilot interaction retention (Exchange Online mailbox), ROT content quality impact
- **Control 4.4 (Guest Access):** Domain allow/block list details, access expiration automation, B2B integration changes (July 2025), link type recommendations table
- **Control 4.5 (Security Monitoring):** Agent Insights metrics table (November 2025), SharePoint Admin Agent (November-December 2025), Site Permissions for Users Report (December 2025), DSPM item-level remediation
- **Control 4.6 (Grounding Scope):** DLP policy enforcement via "Knowledge source with SharePoint and OneDrive in Copilot Studio" connector, endpoint filtering configuration, technical limits table (1,000 files, 512 MB, 4-6 hour sync), supported content types
- **Control 4.7 (Copilot Data Governance):** Permission hygiene prerequisite section, EEEU risk documentation, discovery amplification explanation, no elevated access clarification

**New Reference Documentation:**

- **SharePoint Advanced Management Licensing Guide** (`docs/reference/sharepoint-advanced-management-licensing.md`) - Documents 11 of 12 SAM features included free with Microsoft 365 Copilot license, standalone pricing ($3/user/month), activation requirements

**New Playbook:**

- **SharePoint Governance Pre-Flight Checklist** (`docs/playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md`) - Comprehensive 5-phase pre-deployment checklist for Copilot: Permission Audit, Grounding Scope Configuration, External Access Controls, Security/Monitoring, Access Review Cadence

### Files Updated

| File | Changes |
|------|---------|
| `docs/controls/pillar-4-sharepoint/4.1-*.md` | Technical Implementation Notes section |
| `docs/controls/pillar-4-sharepoint/4.2-*.md` | Technical Implementation Notes section |
| `docs/controls/pillar-4-sharepoint/4.3-*.md` | Technical Implementation Notes section |
| `docs/controls/pillar-4-sharepoint/4.4-*.md` | Technical Implementation Notes section |
| `docs/controls/pillar-4-sharepoint/4.5-*.md` | Technical Implementation Notes section |
| `docs/controls/pillar-4-sharepoint/4.6-*.md` | Technical Implementation Notes section |
| `docs/controls/pillar-4-sharepoint/4.7-*.md` | Technical Implementation Notes section |
| `docs/reference/sharepoint-advanced-management-licensing.md` | **NEW** - SAM licensing guide |
| `docs/playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` | **NEW** - Pre-flight checklist |
| `mkdocs.yml` | Navigation entries for new files |
| `CHANGELOG.md` | Added v1.2.23 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: All 62 controls valid

### Research Reference

Research report: `prompts/02-documentation-technical/04-pillar-4-sharepoint/Pillar 4 SharePoint Controls Technical Accuracy Va.md`

---

## [1.2.22] — January 31, 2026 (Industry Framework Alignment References)

### Overview

Added external industry framework references to strengthen FSI-AgentGov's alignment with financial services AI governance standards. These additions were identified through external research validation (Perplexity AI analysis of 150+ industry sources).

### Added

- **FINOS AI Governance Framework Reference** - Added alignment section to `docs/reference/regulatory-mappings.md` documenting how FSI-AgentGov controls address FINOS-identified agentic AI risks (authorization bypass, privilege escalation, workflow circumvention)
- **Sardine Agentic Oversight Framework Reference** - Added industry context section to HITL triggers playbook mapping the 5-component oversight model (Access, Agent Operation, Decision and Presentation, Comprehensive Audit Trail, Board Governance) to framework controls

### Research Validation

External research analysis (Perplexity AI, 150+ industry sources) validated framework architecture:

- Three-layer architecture rated "industry-standard"
- 10-section control template exceeds industry norms
- 4 playbooks per control rated "exceptional implementation depth"
- Overall framework grade: A- (industry-leading for specialized domain)

### Files Updated

| File | Changes |
|------|---------|
| `docs/reference/regulatory-mappings.md` | Added FINOS AI Governance Framework section with risk mapping table |
| `docs/playbooks/advanced-implementations/human-in-the-loop-triggers.md` | Added Industry Context section with Sardine framework mapping |
| `CHANGELOG.md` | Added v1.2.22 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: Pass

---

## [1.2.21] — January 31, 2026 (Pillar 3 Reporting Controls Technical Accuracy Updates)

### Overview

Technical accuracy improvements for Pillar 3 Reporting Controls (3.1-3.10) based on research validation. Critical clarifications added for Controls 3.9 and 3.10, plus feature and capability updates across 6 additional controls reflecting 2025-2026 Microsoft platform changes.

### Fixed (Critical Clarifications)

- **Control 3.9 (Sentinel Integration):** Added explicit warning that no dedicated Copilot Studio connector exists for Microsoft Sentinel. Clarified that Copilot Studio events are captured via Power Platform Admin Activity connector (`PowerPlatformAdminActivity` table). Documented custom integration path: Application Insights → Log Analytics → Sentinel.
- **Control 3.10 (Hallucination Feedback):** Added explicit warning that no automated hallucination detection exists in Copilot Studio. Clarified all detection relies on manual user feedback (CSAT, explicit flagging). Added industry context on 3-10% hallucination rates as inherent LLM limitation. Added mitigation strategies table.

### Added (Feature Updates)

- **Control 3.1 (Agent Inventory):** Added Power Platform Inventory preview status (October 2025), documented 24-hour refresh cycle, 500-agent display limit, and 48-hour deleted agent visibility. Added Azure Resource Graph query and PowerShell examples for programmatic access.
- **Control 3.2 (Usage Analytics):** Added new 2025-2026 features table: Agent Dashboard (Ignite 2025), Action Usage Analytics (GA November 2025), Copilot Benchmarks, Copilot Chat Insights expansion (February 2026), New Usage Page in PPAC (preview January 2026). Added data availability notes for DAU/MAU metrics and 28-day native retention.
- **Control 3.3 (Compliance Reporting):** Added Microsoft Compliance Manager AI assessment templates section (EU AI Act, NIST AI RMF, ISO/IEC 42001, ISO/IEC 23894). Added Azure AI Foundry integration for automated compliance evaluations. Noted 320+ regulatory framework templates and AI-powered regulatory intelligence (GA January 2026).
- **Control 3.6 (Orphaned Agent Detection):** Added Agent Ownership Reassignment (GA October 2025) section with PPAC portal, PowerShell, and Power Automate methods. Documented new owner requirements and PowerShell reassignment command.
- **Control 3.7 (Security Posture):** Added qualitative scoring scale (Low/Medium/High) with FSI actions. Added recommendation trigger conditions table (10+ admins, auditing off, no DLP policy, etc.). Added three proactive policy categories (Data Protection, IAM, Compliance).
- **Control 3.8 (Copilot Hub):** Added explicit preview status designation. Added terminology clarification (admin Copilot Hub vs. user portal copilot.cloud.microsoft). Added Microsoft Agent 365 strategic context from Ignite 2025. Added 8-hour settings propagation note.

### Validated (No Changes Needed)

The following controls were validated as accurate:
- Control 3.4 (Incident Reporting) - Reviewed, no updates required
- Control 3.5 (Cost Tracking) - Reviewed, no updates required

### Files Updated

| File | Changes |
|------|---------|
| `docs/controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md` | Connector availability warning, data sources table, custom integration guidance |
| `docs/controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md` | Detection limitations warning, mitigation strategies, feedback mechanisms table |
| `docs/controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md` | Preview status, limitations, programmatic access examples |
| `docs/controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md` | 2025-2026 features table, data availability notes |
| `docs/controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md` | AI assessment templates, Azure AI Foundry integration |
| `docs/controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md` | Ownership reassignment GA section |
| `docs/controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md` | Scoring scale, trigger conditions, policy categories |
| `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` | Preview status, terminology, Agent 365 context |
| `CHANGELOG.md` | Added v1.2.21 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: Pass

### Research Reference

Research report: `prompts/02-technical/pillar-3-reporting-controls/`

---

## [1.2.20] — January 31, 2026 (State Regulations and Framework Standards Citation Updates)

### Overview

Regulatory citation accuracy improvements based on research validation of state AI laws, OWASP LLM Top 10, NIST AI RMF references, and MITRE ATLAS framework.

### Fixed

- **Colorado SB24-205 Effective Date:** Changed from February 1, 2026 to June 30, 2026 (extended via SB 25B-004 signed August 28, 2025)
  - `docs/reference/regulatory-mappings.md`
  - `docs/playbooks/regulatory-modules/colorado-ai-impact-assessment.md`
- **OWASP LLM Top 10 Version:** Updated from 2023 to 2025 version (released November 2024)
  - `docs/controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md` - Updated version and LLM05→LLM03 (Supply Chain moved in 2025)
  - `docs/controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md` - Added (2025) to references
- **Treasury NIST AI RMF Claim:** Changed "endorsed by the U.S. Treasury" to "recommended by U.S. Treasury" in crosswalk
  - `docs/reference/nist-ai-rmf-crosswalk.md`

### Added

- **MITRE ATLAS Context:** Added technique count (15 tactics, 66 techniques as of October 2025) to Control 2.20
- **State AI Law Monitoring Section:** Added table of other state AI laws effective 2026 (Texas TRAIGA, Illinois HB 3773, California TFAIA) with federal preemption note

### Validated (No Changes Needed)

The following were validated as accurate:
- NIST AI RMF 1.0 core function descriptions
- MITRE ATLAS framework purpose and URL
- OWASP LLM Top 10 project URL

### Files Updated

| File | Changes |
|------|---------|
| `docs/reference/regulatory-mappings.md` | Colorado date fix, state AI law monitoring section |
| `docs/playbooks/regulatory-modules/colorado-ai-impact-assessment.md` | Colorado date fix |
| `docs/controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md` | OWASP 2023→2025, LLM05→LLM03 |
| `docs/controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md` | OWASP (2025) refs, MITRE ATLAS stats |
| `docs/reference/nist-ai-rmf-crosswalk.md` | Treasury "endorsed"→"recommended" |
| `CHANGELOG.md` | Added v1.2.20 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: Pass

### Research Reference

Research report: `prompts/01-regulatory/04-state-and-framework-citations/`

---

## [1.2.19] — January 31, 2026 (SEC Rule 17a-4 Citation Correction)

### Overview

Regulatory citation accuracy improvement correcting SEC Rule 17a-4 retention period from "6 years + 3 years accessible" to "6 years, first 2 years readily accessible" per 17 CFR § 240.17a-4.

### Fixed

- **SEC Rule 17a-4 retention period:** Corrected across 5 files (8 instances) from "6 years + 3 years accessible" to "6 years, first 2 years readily accessible":
  - `docs/framework/regulatory-framework.md` (4 instances)
  - `docs/framework/zones-and-tiers.md` (1 instance)
  - `docs/playbooks/agent-lifecycle/agent-decommissioning.md` (1 instance)
  - `docs/reference/faq.md` (1 instance)
  - `docs/playbooks/advanced-implementations/platform-change-governance/architecture.md` (1 instance - also fixed 3+3 to 2+4 split)

### Validated (No Changes Needed)

The following SEC citations were validated as accurate:

- SEC Marketing Rule 206(4)-1 - AI disclosure requirements correctly characterized
- SEC Regulation S-P - Privacy safeguards correctly described
- SEC Regulation BI - Best interest standard correctly referenced
- SEC Regulation S-ID - Identity theft prevention correctly referenced
- SEC Rule 10b-5 - Anti-fraud provisions correctly cited
- SEC 2026 Examination Priorities - AI risk focus correctly characterized

### Files Updated

| File | Changes |
|------|---------|
| `docs/framework/regulatory-framework.md` | Fixed 17a-4 retention (4 places) |
| `docs/framework/zones-and-tiers.md` | Fixed 17a-4 retention (1 place) |
| `docs/playbooks/agent-lifecycle/agent-decommissioning.md` | Fixed 17a-4 retention |
| `docs/reference/faq.md` | Fixed 17a-4 retention |
| `docs/playbooks/advanced-implementations/platform-change-governance/architecture.md` | Fixed audit trail retention split |
| `CHANGELOG.md` | Added v1.2.19 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- SEC Rule 17a-4 verified against 17 CFR § 240.17a-4(f)

### Research Reference

Research report: `prompts/01-regulatory/02-sec-citations/`

---

## [1.2.18] — January 31, 2026 (Banking Regulator Citation Remediation)

### Overview

Regulatory citation accuracy improvements based on research validation of OCC, Fed, FDIC, and GLBA references. Corrects erroneous FDIC FIL citation and clarifies AI guidance status.

### Fixed

- **Control 2.16 (RAG Source Integrity):** Replaced incorrect `FDIC FIL-15-2025` citation (which addresses deposits surveys) with `Interagency Third-Party Guidance (2023)` for third-party knowledge source governance
- **Control 2.6 (Model Risk Management):** Replaced incorrect `OCC 2021-18: AI/ML-specific risk management guidance` with `Interagency RFI on AI (2021): Confirmed OCC 2011-12 applies to AI/ML systems` - no standalone AI-specific OCC guidance exists
- **Control 2.6:** Added clarification that Fed SR 11-7 is identical to OCC 2011-12 (jointly issued)

### Validated (No Changes Needed)

The following citations were validated as accurate:

- OCC Bulletin 2011-12 - Technology-neutral, applies to AI via broad model definition
- Fed SR 11-7 - Identical to OCC 2011-12 (joint issuance)
- SOX Sections 302, 404, 802 - All correctly characterized
- GLBA Section 501(b) - Correctly describes safeguards (72-hour claim removal in v1.2.7 validated)
- OCC Heightened Standards - Correctly described

### Files Updated

| File | Changes |
|------|---------|
| `docs/controls/pillar-2-management/2.16-rag-source-integrity-validation.md` | Replaced FDIC FIL-15-2025 with Interagency Third-Party Guidance (2023) |
| `docs/controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md` | Fixed OCC 2021-18 reference, added SR 11-7 joint issuance note |
| `CHANGELOG.md` | Added v1.2.18 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)

### Research Reference

Research report: `prompts/01-regulatory/03-banking-regulator-citations/`

---

## [1.2.17] — January 31, 2026 (FINRA Citation Remediation)

### Overview

Regulatory citation accuracy improvements based on research validation of FINRA references. Corrects retention period errors, adds official FINRA guidance references, and clarifies Notice 25-07 status.

### Fixed

- **FINRA Rule 4511 retention period:** Corrected from "6 years + 1 year readily accessible" to "6 years, first 2 years in easily accessible place" across 5 files:
  - `docs/framework/regulatory-framework.md` (3 instances)
  - `docs/reference/faq.md`
  - `docs/playbooks/agent-lifecycle/agent-decommissioning.md`
- **FINRA Notice 25-07 link text:** Changed from "AI Communications Recordkeeping" to "Workplace Modernization (RFC - Request for Comment)" to accurately reflect document purpose (Control 2.12)

### Added

- **FINRA Regulatory Notice 24-09 (June 2024):** Official Gen AI and LLM guidance added to:
  - `docs/framework/regulatory-framework.md` (new info callout)
  - `docs/reference/regulatory-mappings.md` (new info callout and overview list)
  - `docs/controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md` (Additional Resources)
- **FINRA Rule 3120 (Supervisory Control System):** Added cross-reference in Control 2.12 Related Controls section
- **FINRA FAQ D.8 citation:** Added firm responsibility quote for AI-generated communications to regulatory-mappings.md
- **FINRA Rule 2210 (Communications):** Added to regulatory-mappings.md FINRA AI overview

### Files Updated

| File | Changes |
|------|---------|
| `docs/framework/regulatory-framework.md` | Fixed 4511 retention (3 places), added Notice 24-09 callout |
| `docs/reference/regulatory-mappings.md` | Added Notice 24-09 callout, FAQ D.8 quote, Rule 3120/2210 |
| `docs/controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md` | Fixed 25-07 link text, added 24-09/3120/FAQ D.8 resources |
| `docs/reference/faq.md` | Fixed 4511 retention |
| `docs/playbooks/agent-lifecycle/agent-decommissioning.md` | Fixed 4511 retention |
| `CHANGELOG.md` | Added v1.2.17 entry |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- All FINRA URLs verified against official FINRA website

### Research Reference

Research report: `prompts/01-regulatory/01-finra-citations/`

---

## [1.2.16] — January 31, 2026 (Cross-Repository Documentation Parity)

### Overview

Bidirectional cross-references between FSI-AgentGov (framework) and FSI-AgentGov-Solutions (deployable artifacts) to enable seamless navigation between documentation and implementation.

### Added

- **Control tip boxes:** Deployable solution links added to Controls 2.1, 2.10, and 1.7
- **Playbook solution links:** Added "Deployable Solution" sections to PowerShell playbooks for Controls 2.1 and 1.7
- **Playbooks index callout:** Info box linking to Solutions Index and FSI-AgentGov-Solutions

### Enhanced (FSI-AgentGov-Solutions)

- **deny-event-correlation-report/README.md:** Fixed broken playbook URL, standardized Related Controls format
- **message-center-monitor/README.md:** Added Related Controls (2.3, 2.10) and Playbook Reference sections
- **README.md:** Added Controls column to solutions table with control mappings
- **CLAUDE.md:** Added Control Implementations table with solution-to-control mappings

### Files Updated

| Repository | File | Changes |
|------------|------|---------|
| FSI-AgentGov | `docs/controls/pillar-2-management/2.1-managed-environments.md` | Added ELM solution link |
| FSI-AgentGov | `docs/controls/pillar-2-management/2.10-patch-management-and-system-updates.md` | Added message-center-monitor tip |
| FSI-AgentGov | `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Added deny-event tip |
| FSI-AgentGov | `docs/playbooks/control-implementations/2.1/powershell-setup.md` | Added Deployable Solution section |
| FSI-AgentGov | `docs/playbooks/control-implementations/1.7/powershell-setup.md` | Added Deployable Solution section |
| FSI-AgentGov | `docs/playbooks/advanced-implementations/deny-event-correlation-report/index.md` | Added direct solution link |
| FSI-AgentGov | `docs/playbooks/index.md` | Added Solutions callout |
| FSI-AgentGov-Solutions | `deny-event-correlation-report/README.md` | Fixed URL, added Related Controls |
| FSI-AgentGov-Solutions | `message-center-monitor/README.md` | Added Related Controls, Playbook Reference |
| FSI-AgentGov-Solutions | `README.md` | Added Controls column |
| FSI-AgentGov-Solutions | `CLAUDE.md` | Added Control Implementations table |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- All GitHub URLs use `/blob/main/` format for direct file links

---

## [1.2.15] — January 31, 2026 (Solutions Documentation and Cross-References)

### Overview

Comprehensive documentation update to improve discoverability and traceability between the FSI-AgentGov framework and FSI-AgentGov-Solutions deployable automation. Addresses P4 audit backlog tasks (P4-006, P4-009, P4-011, P4-012, P4-013, P4-014, P4-015).

### Added

- **Solutions Index (`docs/reference/solutions-index.md`):** Complete catalog of all FSI-AgentGov-Solutions with versions, descriptions, and control mappings
- **Solutions Integration (`docs/framework/solutions-integration.md`):** Architecture document mapping solutions to pillars (1-4) and zones (1-3) with Mermaid diagrams
- **FSI-AgentGov-Solutions Documentation:**
  - `scripts/README.md` - Documents hooks folder (boundary-check.py, researcher-package-reminder.py)
  - `.claude/README.md` - Documents Claude Code configuration and cross-repo workflow

### Enhanced

- **CONTROL-INDEX.md:** Added "Implementation" column for all 62 controls showing Portal/PowerShell and solution links
- **Platform Change Governance (`index.md`):** Added explicit cross-reference to message-center-monitor solution
- **Adoption Roadmap (`adoption-roadmap.md`):**
  - Added automation tips with solution links to Phase 0, Phase 1, and Phase 2
  - Added "Automation Solutions" summary table mapping solutions to phases
- **mkdocs.yml:** Added navigation entries for Solutions Integration and Solutions Index

### Files Updated

| Repository | File | Changes |
|------------|------|---------|
| FSI-AgentGov | `docs/reference/solutions-index.md` | Created - complete solutions catalog |
| FSI-AgentGov | `docs/framework/solutions-integration.md` | Created - solutions-to-framework mapping |
| FSI-AgentGov | `docs/controls/CONTROL-INDEX.md` | Added Implementation column with solution links |
| FSI-AgentGov | `docs/framework/adoption-roadmap.md` | Added solution references and automation tips |
| FSI-AgentGov | `docs/playbooks/advanced-implementations/platform-change-governance/index.md` | Added message-center-monitor cross-reference |
| FSI-AgentGov | `mkdocs.yml` | Added nav entries for new docs |
| FSI-AgentGov | `.claude/CLAUDE.md` | Updated to v1.2.15 with new file references |
| FSI-AgentGov-Solutions | `scripts/README.md` | Created - hooks documentation |
| FSI-AgentGov-Solutions | `.claude/README.md` | Created - Claude configuration guide |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: Pass (62 controls valid)

---

## [1.2.14] — January 31, 2026 (Technical Review Validation Fixes)

### Overview

Documentation accuracy fixes addressing validated items from technical review (P3-001, P3-005). The review validated 15 items, finding 10 invalid (false claims), 3 partially valid, and 2 requiring action.

### Fixed

- **SECURITY.md version (P3-001):** Updated framework version in footer from `v1.1` to `v1.2.14`
- **Control 2.1 licensing prerequisites (P3-005):** Added explicit "Prerequisites" section documenting Power Platform Premium capacity requirements and licensing details for Managed Environments

### Files Updated

| File | Changes |
|------|---------|
| `SECURITY.md` | Updated version footer to v1.2.14 |
| `docs/controls/pillar-2-management/2.1-managed-environments.md` | Added Prerequisites section with licensing requirements |
| `.claude/CLAUDE.md` | Updated version to 1.2.14, added recent additions |

### Validation

- `mkdocs build --strict`: Pass (no errors)
- `python scripts/verify_controls.py`: Pass (62 controls valid)
- Researcher package regenerated

---

## [1.2.13] — January 31, 2026 (Documentation Parity Fix)

### Overview

Documentation parity update to correct control counts across all documentation files. Control 1.24 (Defender AI-SPM) was added in v1.2.10 but several documentation files were not updated to reflect the new total of 62 controls.

### Fixed

- **Control count parity:** Updated all references from 61 to 62 controls
- **Pillar 1 range:** Corrected "1.1-1.23" to "1.1-1.24" (24 security controls)
- **Playbook count:** Updated from 244 to 248 playbooks (62 controls × 4)

### Files Updated

| File | Changes |
|------|---------|
| `README.md` | Control counts, pillar range, playbook counts (9 changes) |
| `docs/reference/faq.md` | Control counts, pillar breakdown |
| `docs/reference/regulatory-mappings.md` | Updated all X/61 ratios to X/62 |
| `docs/framework/governance-fundamentals.md` | Control count and pillar table |
| `docs/downloads/index.md` | Dashboard description |
| `docs/getting-started/quick-start.md` | Zone 3 control count |
| `docs/playbooks/getting-started/phase-2-hardening.md` | Annual review checklist |
| `docs/playbooks/governance-operations/governance-operating-calendar.md` | Calendar description |
| `docs/playbooks/control-implementations/3.3/verification-testing.md` | Verification step |
| `releases/README.md` | PDF description |
| `scripts/README.md` | Script description |
| `scripts/update_excel_templates.py` | Control dictionary comment |
| `scripts/normalize_controls.py` | Module docstring |
| `docs/framework/executive-summary.md` | Total controls count |
| `maintainers-local/researcher-package/00-*.md` | Summary guide counts and ranges |

### Audit Trail

Identified via automated audit task execution (P2-001 through P2-015). P2-001 confirmed as false positive; actual issue was stale control counts in README.md and propagated to other files.

### Validation

- `python scripts/verify_controls.py`: Pass (62 controls valid)
- No remaining references to "61 controls" or "1.1-1.23" in updated files

---

## [1.2.12] — January 30, 2026 (ELM Automation Documentation)

### Overview

Documentation updates to reflect the new automated deployment capabilities in FSI-AgentGov-Solutions Environment Lifecycle Management v1.1.0.

### Enhanced

- **Environment Lifecycle Management Playbook**
  - `index.md` - Added automated deployment quick start with `deploy.py` usage examples
  - `labs.md` - Added "Option A: Automated Deployment" as alternative to manual Lab 1 setup
  - Updated all playbook file versions to v1.2.12

### Related

- FSI-AgentGov-Solutions Environment Lifecycle Management v1.1.0
- New automation scripts: `deploy.py`, `create_dataverse_schema.py`, `create_security_roles.py`, `create_business_rules.py`, `create_views.py`, `create_field_security.py`

---

## [1.2.11] — January 29, 2026 (Solutions Cross-Reference)

### Overview

Documentation updates to add cross-references between the FSI-AgentGov framework and the new Environment Lifecycle Management solution scripts in FSI-AgentGov-Solutions.

### Enhanced

- **Environment Lifecycle Management Playbook**
  - `evidence-and-audit.md` - Added tip box cross-referencing automated export scripts (`export_quarterly_evidence.py`, `validate_immutability.py`) in FSI-AgentGov-Solutions
  - `index.md` - Updated Implementation Kit table to reflect actual solution structure (docs, scripts, templates, setup checklist) with direct repository links

### Changed

- **boundary-check.py** - Updated hook response from `"allow"` to `"approve"` (Claude Code hook API alignment)

### Files Summary

| Action | Count | Key Files |
|--------|-------|-----------|
| UPDATE | 3 | evidence-and-audit.md, index.md, boundary-check.py |

### Related

- FSI-AgentGov-Solutions Environment Lifecycle Management v1.0.1

---

## [1.2.10] — January 29, 2026 (AI-SPM and DLP Updates)

### Overview

Addresses verified findings from external feedback review (Manus AI analysis). This release adds Defender AI-SPM as a new control and updates DLP and DSPM documentation with current Microsoft capabilities.

### Feedback Review Summary

| Finding | Feedback Claim | Validity | Action |
|---------|---------------|----------|--------|
| Entra Agent ID | "Complete rewrite needed" | **INVALID** | None - already comprehensive in agent-identity-architecture.md |
| Runtime Protection | "Lacks webhook detail" | **PARTIALLY VALID** | Enhanced Security Webhooks API section |
| AI-SPM | "Missing AI-SPM" | **VALID** | New Control 1.24 created |
| Foundry Control Plane | "No mention" | **OUT OF SCOPE** | Azure AI Foundry outside Power Platform focus |
| DLP Mandatory | "Needs update" | **VALID** | Updated Control 1.5 |
| DSPM Expansion | "Needs expansion" | **PARTIALLY VALID** | Updated Control 1.6 |

### Added

- **Control 1.24: Defender AI Security Posture Management (AI-SPM)** (`docs/controls/pillar-1-security/1.24-defender-ai-security-posture-management.md`)
  - Multi-cloud AI security posture for Azure, AWS Bedrock, GCP Vertex AI
  - Agent discovery and AI Bill of Materials (AI BOM)
  - Attack path analysis for AI workloads
  - Risk factor assessment (prompt injection, data exfiltration)
  - Relationship to DSPM for AI (complementary controls)
  - Zone-specific requirements (monthly/weekly/daily reviews)

- **Control 1.24 Playbooks** (`docs/playbooks/control-implementations/1.24/`)
  - `portal-walkthrough.md` - Defender for Cloud AI-SPM configuration
  - `powershell-setup.md` - Az.Security and Resource Graph scripts
  - `verification-testing.md` - Test cases and attestation template
  - `troubleshooting.md` - Common issues and resolutions

### Enhanced

- **Control 1.5 (DLP and Sensitivity Labels)**
  - Added mandatory DLP enforcement notice (since early 2025, no opt-out)
  - Added Copilot Studio DLP Connector Categories table (Knowledge Sources, Channels, Actions, AI Services)
  - Added HTTP Endpoint Filtering section with allow/block list examples

- **Control 1.6 (DSPM for AI)**
  - Added Supported AI Workloads table (M365 Copilot, Copilot Studio, ChatGPT Enterprise, Gemini, Purview SDK apps)
  - Added Extended Insights configuration note for third-party AI monitoring

- **Control 1.8 (Runtime Protection)**
  - Expanded Security Webhooks API section with provider types and integration patterns
  - Added configuration requirements (Entra app, webhook endpoint, response format, SLA)
  - Added vendor assessment checklist for third-party security providers

### Changed

- **Control count:** 61 → 62 controls
- **Pillar 1 count:** 23 → 24 controls
- Updated `CONTROL-INDEX.md` with Control 1.24
- Updated `pillar-1-security/index.md` with Control 1.24 and category updates
- Updated `mkdocs.yml` navigation for Control 1.24 and playbooks

### Files Summary

| Action | Count | Key Files |
|--------|-------|-----------|
| CREATE | 5 | Control 1.24 + 4 playbooks |
| UPDATE | 7 | Controls 1.5, 1.6, 1.8, CONTROL-INDEX, pillar index, mkdocs.yml, CHANGELOG |

### Cross-Reference Enhancements

Minor additions to improve control interconnection based on verification report review:

- **Control 3.9 (Sentinel Integration)** - Added XDR detection scenario row and Control 1.24 (AI-SPM) cross-reference
- **Control 2.17 (Multi-Agent Orchestration)** - Added Control 1.24 (AI-SPM) cross-reference for coordinator agent visibility
- **Control 4.1 (SharePoint IAG)** - Added Control 1.6 (DSPM for AI) cross-reference for oversharing assessment

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: Pass (62 controls valid)
- All internal links resolve

---

## [1.2.9] — January 29, 2026 (Environment Lifecycle Management)

### Overview

Added Environment Lifecycle Management advanced implementation playbook for automated, governed Power Platform environment provisioning.

**Problem:** Manual environment provisioning creates governance gaps. Inconsistent security controls (auditing, DLP, session timeouts) applied post-creation. No structured audit trail of who requested what environment, why, and who approved it.

**Solution:** Copilot Studio intake agent with zone classification, Power Automate provisioning via Service Principal, Dataverse tracking with immutable ProvisioningLog, automated baseline configuration applied at creation.

### Added

- **Environment Lifecycle Management Playbook** (6 docs)
  - `index.md` - Overview, regulatory alignment, framework integration
  - `architecture.md` - Dataverse schema, Service Principal lifecycle, security model, fault tolerance patterns
  - `implementation-copilot-intake.md` - Copilot Studio intake agent with zone classification
  - `implementation-provisioning.md` - Power Automate flows with async polling, baseline config
  - `labs.md` - Hands-on labs 1-4
  - `evidence-and-audit.md` - ProvisioningLog immutability, evidence standards

### Enhanced

- **Control 2.1** - Added Environment Lifecycle Management cross-reference (creates environments as Managed from start)
- **Control 2.2** - Added Environment Lifecycle Management cross-reference (auto-assigns to Environment Groups)
- **Control 2.3** - Added Environment Lifecycle Management cross-reference (treats provisioning as controlled change)
- **Control 2.8** - Added Environment Lifecycle Management cross-reference (requester ≠ approver enforcement)
- **Control 2.13** - Added Environment Lifecycle Management cross-reference (immutable provisioning audit trail)
- **Control 2.15** - Added Environment Lifecycle Management cross-reference (zone-based request routing)
- **Control 1.7** - Added Environment Lifecycle Management cross-reference (provisioning audit logging)
- **Control 3.1** - Added Environment Lifecycle Management cross-reference (automatic inventory registration)
- **Control 3.2** - Added Environment Lifecycle Management cross-reference (usage insights from creation)
- **Control 3.6** - Added Environment Lifecycle Management cross-reference (prevents orphaned environments)

### Regulatory Alignment

| Regulation | Requirement | How This Solution Helps |
|------------|-------------|------------------------|
| **FINRA 4511** | Records of business activities (6+ years) | ProvisioningLog provides immutable request/approval/action audit trail |
| **SEC 17a-3/4** | Records preservation with audit trail | Dataverse change tracking, quarterly export to compliant storage |
| **SOX 302/404** | Internal control assessment and certification | Documented approval workflows, segregation of duties |
| **GLBA 501(b)** | Administrative safeguards for customer information | Baseline configuration applies consistent security controls at creation |
| **OCC 2011-12** | Model risk documentation | Zone classification documents risk tier for agent workloads |

### Key Architecture Features

- **Service Principal Identity** - Decouples provisioning from human credential lifecycle
- **Immutable ProvisioningLog** - Organization-owned table with no update/delete privileges
- **Async Polling Pattern** - Handles non-deterministic environment creation (1-30+ minutes)
- **Fault Tolerance** - Error handling, timeout definitions, rollback procedures
- **Zone Classification Review** - Auto-triggers flag for Compliance review, not auto-approve
- **DLP Policy Inheritance** - Environment Group assignment ensures no policy gap

### Files Modified

| File | Change |
|------|--------|
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/index.md` | Created - Overview and regulatory alignment |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/architecture.md` | Created - Schema, security model, fault tolerance |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/implementation-copilot-intake.md` | Created - Intake agent configuration |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/implementation-provisioning.md` | Created - Provisioning flow implementation |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/labs.md` | Created - Hands-on labs 1-4 |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/evidence-and-audit.md` | Created - Evidence standards and audit |
| `mkdocs.yml` | Added Environment Lifecycle Management navigation |
| `docs/controls/pillar-2-management/2.1-managed-environments.md` | Added cross-reference |
| `docs/controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md` | Added cross-reference |
| `docs/controls/pillar-2-management/2.3-change-management-and-release-planning.md` | Added cross-reference |
| `docs/controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md` | Added cross-reference |
| `docs/controls/pillar-2-management/2.13-documentation-and-record-keeping.md` | Added cross-reference |
| `docs/controls/pillar-2-management/2.15-environment-routing.md` | Added cross-reference |
| `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md` | Added cross-reference |
| `CHANGELOG.md` | This entry |

### Validation

- `mkdocs build --strict`: Pass
- All cross-references resolve
- Navigation renders correctly

---

## [1.2.8] — January 28, 2026 (Pipeline Governance Cleanup Cross-Reference)

### Overview

Added documentation cross-references to the new Pipeline Governance Cleanup Solution in FSI-AgentGov-Solutions repository.

### Added

- **Control 2.3 Cross-Reference** - Added tip admonition referencing Pipeline Governance Cleanup Solution for organizations needing to clean up personal pipelines before enforcing centralized ALM governance
- **Troubleshooting Entry** - Added pre-existing personal pipelines cleanup guidance to Control 2.3 troubleshooting playbook

### Changed

- **Boundary Check Hook** - Updated `scripts/hooks/boundary-check.py` to allow commands targeting the companion FSI-AgentGov-Solutions repository

### Files Modified

| File | Change |
|------|--------|
| `docs/controls/pillar-2-management/2.3-change-management-and-release-planning.md` | Added Pipeline Governance Cleanup tip admonition |
| `docs/playbooks/control-implementations/2.3/troubleshooting.md` | Added pre-existing personal pipelines section |
| `scripts/hooks/boundary-check.py` | Added FSI-AgentGov-Solutions to allowed directories |
| `CHANGELOG.md` | This entry |

### Related

- [Pipeline Governance Cleanup Solution](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup) (new in FSI-AgentGov-Solutions v1.0.0)

### Validation

- `mkdocs build --strict`: Pass
- All cross-references resolve

---

## [1.2.7] — January 28, 2026 (Regulatory Accuracy Remediation)

### Overview

Addresses findings from consolidated technical and regulatory review (Feedback01). This release focuses on regulatory citation accuracy, language precision, and framework enhancements.

### Critical Fixes

- **FINRA Notice 25-07 Citation Correction** (35+ files)
  - Corrected misattribution of FINRA Notice 25-07 as AI governance guidance
  - FINRA 25-07 (April 2025) addresses workplace modernization rules, NOT AI governance
  - AI supervision citations now reference FINRA Rule 3110 (Supervision) and Rule 2111 (Suitability)
  - AI communications recordkeeping references retained with proper context
  - Control 2.11 renamed from `2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md` to `2.11-bias-testing-and-fairness-assessment.md`

- **GLBA 72-Hour Claim Removal** (Control 3.4, ai-incident-response-playbook.md)
  - Removed unsupported 72-hour GLBA notification claim
  - Replaced with accurate guidance: notification timelines vary by regulator and incident type

- **SEC Reg S-P Notification Precision** (Control 3.4)
  - Updated to reflect 2024 amendments (effective December 3, 2025)
  - Specifies ≤30 days notification requirement after awareness of unauthorized access

- **NYDFS Part 500.13 RPO Clarification** (Control 3.1)
  - Separated minimum NYDFS required fields from FSI recommended fields
  - RPO, criticality tier, and backup compliance status now identified as recommended enhancements

- **Zone 3 Retention Period Clarification** (zones-and-tiers.md)
  - Clarified 10-year retention as conservative buffer exceeding SEC 17a-3/4 (6+3 years)

- **Zone 1 Regulatory Exemption Language** (zones-and-tiers.md)
  - Changed from absolute exemption to conditional guidance
  - Added recommendation to confirm applicability with compliance/legal

### High Priority Fixes

- **GLBA Section Standardization** (Controls 1.6, 2.14, 4.1, 4.4)
  - Standardized GLBA 501(a) references to 501(b) where appropriate
  - Added 504(b) pretexting footnote where retained

- **Control 1.22 Information Barriers** - Expanded regulatory citations to include SEC Rules 14e-5, Regulation M; FINRA Rules 2241, 5270

- **Agent 365 Preview Disclaimers** (6 controls) - Added prominent warning admonitions for preview status

- **OWASP Citation Correction** (Control 2.7) - Changed unverified "OWASP Agentic AI Top 10" to "OWASP LLM Top 10 (2023)" with LLM05 reference

- **MCP Governance Clarification** (Controls 1.4, 2.7) - Clarified MCP as open protocol requiring vendor risk management

- **Pricing Examples** (Control 3.5) - Marked as illustrative with links to Microsoft pricing portal

- **Agent 365 Code Examples** (observability playbook) - Marked as illustrative pseudocode with verification note

### Medium Priority Fixes

- **Observability Guidance Separation** (Controls 1.7, 3.2) - Added agent type-specific guidance (Copilot Studio vs Agent 365 SDK)

- **Conflict of Interest Types** (Control 2.18) - Added table specifying conflict types to test

- **SharePoint RSS Limit Note** (Control 4.1) - Added verification note for 100-site limit

### Low Priority Fixes

- **Character Encoding** (pillar-4 index) - Fixed em-dash encoding artifact

- **Licensing Prerequisites** (Control 4.1) - Added SharePoint Advanced Management licensing section

- **DSPM for AI Evolving Feature** (Controls 1.5, 1.6) - Added note about actively developing feature set

### Framework Enhancements

- **AML/KYC/OFAC Awareness** (Control 3.3) - Added assessment questions and scope note

- **SEC Reg S-ID Reference** (regulatory-mappings.md) - Acknowledged Red Flags Rule with related controls

- **AI RIA Scoring Rubrics** (ai-risk-assessment-template.md) - Added detailed scoring criteria and simplified assessment path

- **Exception Criteria** (Control 2.2) - Added risk-based exception criteria for simplified classification

- **Emergency Change Procedures** (Control 2.3) - Added CAB emergency path with rollback authority

### Files Summary

| Action | Count | Key Files |
|--------|-------|-----------|
| RENAME | 1 | Control 2.11 (removed FINRA 25-07 from filename) |
| UPDATE | 60+ | Controls, playbooks, framework, reference documents |

### Validation

- `python scripts/verify_controls.py`: Pass (61 controls valid)
- FINRA 25-07 grep validation: Only recordkeeping context remains
- GLBA 72-hour grep validation: No claims remain
- Old Control 2.11 filename: No references remain

---

## [1.2.6] — January 27, 2026 (Agent 365 Operational Depth Enhancements)

### Overview

Addresses 6 enhancement opportunities identified in external advisory reviews (Manus AI v1/v2, January 2026). These are "operational deepening" items—the framework already has correct conceptual alignment; these add implementer-ready artifacts.

### Added

- **Conditional Access Agent Identity Templates** (`docs/playbooks/control-implementations/1.11/conditional-access-agent-templates.md`)
  - 5 CA policy recipes for agent identity targeting across zones
  - Zone 1 baseline MFA, Zone 2 phishing-resistant + device compliance, Zone 3 maximum security with PIM
  - Break-glass emergency access patterns
  - CI/CD service principal policies
  - Agentic User CA policies (preview)
  - Complete PowerShell implementations and evidence queries

- **Agent Audit Event Taxonomy Reference** (`docs/reference/agent-audit-event-taxonomy.md`)
  - Consolidated event table with 25+ event types
  - Category organization: Identity Lifecycle, Blueprint Lifecycle, Agent Interaction, Configuration, Security
  - Event-to-control mapping for evidence purposes
  - Key field schemas for all event types
  - Alert severity recommendations by zone
  - KQL query pack with 5 production-ready queries
  - UAL PowerShell equivalents for non-Sentinel environments

- **Blueprint Promotion Gates Playbook** (`docs/playbooks/advanced-implementations/agent-blueprint-promotion-gates/`)
  - `index.md` - Overview, gate model summary, quick start
  - `gate-definitions.md` - Detailed criteria for Gates 1-4, evidence artifacts, approval templates
  - `implementation-guide.md` - SharePoint setup, Dataverse tables, Power Automate workflows, ALM integration

- **Agent Essentials Control Mapping Reference** (`docs/reference/agent-essentials-control-mapping.md`)
  - Microsoft's 8 Agent Essentials categories mapped to FSI controls
  - Implementation notes and checklist items per category
  - Quick reference matrix by zone
  - Implementation priority phasing

- **Sponsorship Lifecycle Workflows Playbook** (`docs/playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md`)
  - Zone 2 quarterly and Zone 3 monthly review workflows
  - Sponsor departure handling with automated reassignment
  - Zone 3 immediate suspension on sponsor loss
  - Evidence collection and attestation reporting
  - Integration with Control 3.6 orphan detection

- **Agent 365 Observability Implementation Guide** (`docs/playbooks/advanced-implementations/agent-365-observability/`)
  - `index.md` - Architecture overview, telemetry signal categories, zone requirements
  - `opentelemetry-setup.md` - Collector configuration, zone-specific settings, SDK integration
  - `application-insights-workbooks.md` - 5 workbook templates (Performance, Interaction, Security, Sponsor, Incident)
  - `alerting-configuration.md` - Zone-based thresholds, 13 alert definitions, escalation matrix

### Enhanced

- **mkdocs.yml** - Added navigation for all new playbooks and reference documents
- **docs/reference/index.md** - Added links to new reference documents

### Files Summary

| Action | Count | Files |
|--------|-------|-------|
| CREATE | 11 | New playbooks and reference documents |
| UPDATE | 3 | mkdocs.yml, reference/index.md, CHANGELOG.md |

### Gap Source

- Manus AI Advisory Review v1 (January 27, 2026) - Gaps 1-6
- Agent 365 & Copilot Studio Enhancement Plan

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: Pass (61 controls valid)
- All internal links resolve

---

## [1.2.5] — January 27, 2026 (Agent 365 v2 Review Minor Gap Remediation)

### Overview

Addresses 3 minor gaps identified in the Manus AI v2 advisory review. The v2 review confirmed that all major gaps from the v1 remediation were successfully addressed; these are minor enhancements to provide additional depth.

### Added

- **Agentic User Identity Characteristics** (`docs/framework/agent-identity-architecture.md`)
  - New subsection explaining Agentic User as a distinct identity type in Entra ID
  - Characteristics table: no credentials, can have licenses, directory visibility, sponsorship required
  - FSI relevance: audit trail separation, access governance, regulatory visibility, accountability chain
  - Directory representation attributes (userType, accountEnabled, sponsorId, agentMetadata)

- **Agent Sponsorship Governance** (`docs/framework/agent-identity-architecture.md`)
  - Sponsor requirements table (eligibility, approval chain, limits, documentation)
  - Lifecycle Workflows integration with Entra ID Governance
  - Periodic sponsor reviews by zone (semi-annual/quarterly/monthly)
  - Re-attestation workflow with auto-suspend after 14 days
  - Sponsor departure handling with automatic reassignment triggers
  - Entra ID configuration steps for lifecycle workflows
  - Sponsorship best practices (backup sponsors, training, activity visibility)

- **Shadow Agent Detection** (`docs/controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`)
  - New orphan category: "Shadow Agent (Unmanaged)" with Critical risk and 7-day SLA
  - Definition: Agents in tenant but not in registry (vs. orphaned = known agents losing owners)
  - FSI regulatory importance (audit gaps, data exposure, compliance failures)
  - Discovery methods table (PowerShell, Defender for Cloud Apps, Entra, M365 Admin)
  - 4-step discovery process with PowerShell examples
  - Risk assessment factors and remediation decision matrix
  - Zone-specific scanning requirements (monthly/weekly/daily by zone)
  - Integration with Control 3.1 (Agent Inventory)
  - Defender for Cloud Apps integration steps

### Enhanced

- **Microsoft Learn URLs** - Added 4 new URLs:
  - Agent 365 Identity (Preview): `https://learn.microsoft.com/en-us/microsoft-agent-365/developer/identity`
  - Agent 365 Observability (Preview): `https://learn.microsoft.com/en-us/microsoft-agent-365/developer/observability`
  - Entra ID Lifecycle Workflows: `https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows`
  - Defender for Cloud Apps Shadow IT: `https://learn.microsoft.com/en-us/defender-cloud-apps/tutorial-shadow-it`

### Files Modified

| File | Change |
|------|--------|
| `docs/framework/agent-identity-architecture.md` | Added Agentic User characteristics + Sponsorship Governance sections (+98 lines) |
| `docs/controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md` | Added Shadow Agent Detection section (+106 lines) |
| `CHANGELOG.md` | This entry |

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: Pass (61 controls valid)
- Researcher package regenerated

### Gap Source

Manus AI Advisory Review v2 (January 27, 2026) - Minor gaps 4.1, 4.2, 4.3

---

## [1.2.4] — January 27, 2026 (Microsoft 365 Agent Governance Integration)

### Overview

Integrated Microsoft's new Agent 365 governance documentation into the FSI-AgentGov framework. This includes new conceptual documentation explaining the Agent ID vs Blueprint architecture, 5 new Microsoft Learn URLs for monitoring, and updates to 15 controls with Agent 365 references.

**Problem Solved:** Microsoft released new "Agent Essentials" and "Agent 365 SDK" preview documentation introducing the Blueprint concept for enterprise agent governance. The framework lacked guidance on when to use Agent ID vs. Blueprint approaches, and the Learn monitor wasn't tracking these new URLs.

### Added

- **Agent Identity Architecture Document** (`docs/framework/agent-identity-architecture.md`)
  - Explains layered relationship between Agent 365 Blueprints and Microsoft Entra Agent ID
  - Layer 1: Blueprints (governance foundation) - registration, permission inheritance, multi-tenant support
  - Layer 2: Agent ID (identity management) - Conditional Access, lifecycle governance, sponsorship
  - Layer 3: Conditional Access (policy enforcement) - risk-based access control
  - Decision matrix for when to use Agent ID only vs. Agent ID + Blueprint
  - Implementation approach (Foundation → Scale → Governance phases)

- **5 New Microsoft Learn URLs** added to Learn monitor (`data/learn-monitor-state.json`)
  - `m365-agents-visual-map` - Visual governance guide
  - `m365-agents-checklist` - 8-category deployment checklist
  - `m365-agents-blueprint` - 3-phase deployment framework
  - `microsoft-agent-365/developer/registration` - Blueprint registration
  - `microsoft-agent-365/developer/` - Agent 365 SDK overview

- **Agent Essentials & Agent 365 SDK Section** (`docs/reference/microsoft-learn-urls.md`)
  - Preview documentation note
  - 5 new URL entries with cross-reference to Agent Identity Architecture

### Enhanced (15 Controls)

| Control | Enhancement |
|---------|-------------|
| **1.1** | Added Agent Essentials checklist and visual guide references |
| **1.2** | Added Blueprint registration and Agent ID identity references |
| **1.5** | Added Agent Essentials Category 7 data security reference |
| **1.6** | Added Agent Essentials data security alignment reference |
| **1.7** | Added Agent 365 audit event types (BlueprintRegistration, BlueprintPromotion, AgentIdentityCreated) |
| **1.11** | **Added Agent ID vs Blueprint decision matrix** with zone-specific guidance |
| **1.18** | Added Agent-level RBAC via Entra Agent ID references |
| **2.1** | Added Blueprint 3-phase lifecycle reference |
| **2.3** | Added Blueprint deployment framework reference |
| **2.5** | Added Agent 365 SDK testing capabilities reference |
| **3.1** | Added Agent Essentials Category 6 inventory guidance |
| **3.2** | Added Agent 365 OpenTelemetry observability reference |
| **3.5** | Added Agent Essentials Category 8 billing reference |
| **3.6** | Added Agent ID lifecycle governance for orphan detection |
| **3.8** | Added Agent Essentials visual governance map reference |

### Changed

- **mkdocs.yml** - Added Agent Identity Architecture to Framework navigation
- **Learn monitor URL count** - Increased from 191 to 196 tracked URLs
- **microsoft-learn-urls.md** - Updated total URL count from 159 to 164

### Microsoft Checklist Category Mapping

Maps Microsoft's 8 Agent Essentials categories to FSI controls:

| MS Category | FSI Controls |
|-------------|--------------|
| 1. Access & Availability | 1.1, 1.11, 2.8 |
| 2. Copilot Studio Experience | 2.1, 3.8 |
| 3. Agent Builder | 1.1, 1.2, 2.1 |
| 4. Application Lifecycle | 2.3, 2.5 |
| 5. Copilot Studio Creation | 1.1, 2.1, 2.5, 3.8 |
| 6. Inventory & Lifecycle | 3.1, 3.6 |
| 7. Data Security/Compliance | 1.5, 1.6, 1.7, 1.14 |
| 8. Billing & Capacity | 3.5, 3.2 |

### Files Modified

| File | Change |
|------|--------|
| **NEW:** `docs/framework/agent-identity-architecture.md` | Agent ID vs Blueprint conceptual guide |
| `data/learn-monitor-state.json` | Added 5 new URL entries |
| `docs/reference/microsoft-learn-urls.md` | Added Agent Essentials section |
| `mkdocs.yml` | Added framework navigation entry |
| 15 control files | Added Agent 365 preview references |
| `CHANGELOG.md` | This entry |
| `.claude/CLAUDE.md` | Updated key files and framework doc count |

### Notes

- All Agent 365 URLs are preview documentation (Frontier preview program)
- Learn monitor will track changes daily
- Preview references include admonitions noting content may change

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: Pass (61 controls valid)
- All internal links resolve

---

## [1.2.3] — January 26, 2026 (Deny Event Correlation Report)

### Overview

Added a new advanced implementation playbook for daily operational reporting of "deny/no content returned" events across Microsoft Copilot and Copilot Studio agents. The solution correlates events from three data sources: Purview CopilotInteraction audit, Purview DLP events, and Application Insights RAI telemetry.

**Problem Solved:** FSI organizations need to demonstrate that AI governance controls are actively working by producing daily evidence of policy blocks, RAI filters, and DLP enforcement. These events are logged in three separate systems with no native correlation.

### Added

- **Deny Event Correlation Report Playbook** (`docs/playbooks/advanced-implementations/deny-event-correlation-report/`)
  - `index.md` - Overview, architecture diagram, and quick start
  - `purview-audit-extraction.md` - CopilotInteraction deny event extraction with PowerShell
  - `dlp-event-extraction.md` - DLP signal correlation for Copilot location
  - `app-insights-rai-telemetry.md` - Copilot Studio RAI telemetry setup
  - `power-bi-correlation.md` - Dashboard correlation model and DAX measures
  - `deployment-guide.md` - End-to-end Azure Automation deployment

- **FSI-AgentGov-Solutions Repository Addition** (`deny-event-correlation-report/`)
  - 4 PowerShell scripts for automated extraction
  - 4 KQL query files for all data sources
  - Solution documentation (architecture, prerequisites, troubleshooting)

### Enhanced

- **Control 3.2 (Usage Analytics)** - Added "Daily Operational Monitoring" section with deny event categories, cadence by zone, and playbook reference
- **Control 1.8 (Runtime Protection)** - Added "RAI Telemetry Capture" section with Application Insights setup, KQL queries, and zone requirements
- **Purview Audit Query Pack** - Added DLP correlation queries (Section 8), daily export procedures (Section 9), and storage recommendations

### Regulatory Alignment

Supports compliance evidence for:
- **FINRA 25-07** - Daily evidence of AI governance controls
- **FINRA 4511** - Records retention for deny events
- **SEC 17a-3/4** - Supervision evidence for AI agents
- **GLBA 501(b)** - Safeguards evidence via DLP blocking
- **OCC 2011-12** - Model risk controls via RAI telemetry

### Files Modified

| File | Change |
|------|--------|
| `docs/controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md` | Added Daily Operational Monitoring section |
| `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md` | Added RAI Telemetry Capture section |
| `docs/playbooks/monitoring-and-validation/purview-audit-query-pack.md` | Added DLP correlation and daily export sections |
| `docs/playbooks/advanced-implementations/deny-event-correlation-report/*.md` | Created (6 files) |
| `mkdocs.yml` | Added navigation for new playbook |
| `CHANGELOG.md` | This entry |

### FSI-AgentGov-Solutions Files Created

| File | Purpose |
|------|---------|
| `deny-event-correlation-report/README.md` | Solution overview and quick start |
| `deny-event-correlation-report/scripts/Export-CopilotDenyEvents.ps1` | Purview audit extraction |
| `deny-event-correlation-report/scripts/Export-DlpCopilotEvents.ps1` | DLP event extraction |
| `deny-event-correlation-report/scripts/Export-RaiTelemetry.ps1` | App Insights extraction |
| `deny-event-correlation-report/scripts/Invoke-DailyDenyReport.ps1` | Orchestration script |
| `deny-event-correlation-report/kql-queries/*.kql` | KQL queries (4 files) |
| `deny-event-correlation-report/docs/*.md` | Documentation (3 files) |

### Fixed

- **`scripts/verify_controls.py`** - Updated `CANON_VERSION` from "v1.1" to "v1.2" to match current framework version

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: Pass (61 controls valid)
- All internal links resolve
- Navigation renders correctly

---

## [1.2.2] — January 26, 2026 (Learn Monitor End-to-End Verification)

### Overview

Verified the Microsoft Learn Documentation Monitor works end-to-end. PR #2 merged successfully, establishing the production baseline with 191 monitored URLs. Local verification confirmed change detection and report generation function correctly.

### Verified

- **Baseline establishment**: First run correctly creates state file with SHA-256 hashes for all 191 URLs
- **No-change detection**: Subsequent runs correctly detect "Meaningful changes: 0" when content hasn't changed
- **Change detection**: Content modifications trigger "CHANGED: meaningful" classification
- **Report generation**: Reports include diff, affected controls, priority classification (HIGH/MEDIUM/NOISE)
- **Exit codes**: Exit code 1 triggers CI/GitHub workflow for PR creation

### Merged

- **PR #2**: "Learn Monitor: Microsoft Learn Documentation Update (7)"
  - Contains: `data/learn-monitor-state.json` (1733 lines, 191 URLs)
  - Baseline captured: 2026-01-25T23:12:28Z
  - No reports generated (correct for baseline run)

### Current State

- **State file**: `data/learn-monitor-state.json` in main branch
- **URLs monitored**: 191 Microsoft Learn pages
- **Next run**: Daily at 6:00 AM UTC via GitHub Actions
- **Workflow behavior**: Creates PR when changes detected or on Sundays

### Files Modified

| File | Change |
|------|--------|
| `data/learn-monitor-state.json` | Merged from PR #2 (production baseline) |
| `docs/reference/learn-monitor-guide.md` | Added verification procedure section |
| `CHANGELOG.md` | This entry |

---

## [1.2.1] — January 25, 2026 (Learn Monitor PR Body Fix)

### Overview

Fixed misleading PR body messaging in the Learn Monitor workflow for baseline runs. When the monitor runs for the first time (no prior state file), the PR body now correctly indicates this is a baseline run rather than suggesting users check for change reports that don't exist.

### Fixed

- **Learn Monitor workflow** (`.github/workflows/learn-monitor.yml`)
  - Added baseline run detection (checks if state file exists before running)
  - Updated PR body with contextual messaging based on run type
  - Baseline runs now show: "BASELINE RUN" callout, simplified 2-step review instructions, accurate file descriptions
  - Change detection runs continue to show full 5-step review instructions

### Files Modified

| File | Change |
|------|--------|
| `.github/workflows/learn-monitor.yml` | Added baseline detection, contextual PR body |
| `docs/reference/learn-monitor-guide.md` | Documented baseline vs. change detection runs |
| `CHANGELOG.md` | This entry |

### Validation

- Workflow YAML syntax valid
- Conditional expressions tested

---

## [1.2.0] — January 25, 2026 (Platform Change Governance)

### Overview

Added Platform Change Governance advanced implementation playbook providing canonical reference architecture for operationalizing Microsoft Message Center changes in regulated environments with Dataverse as the governance system-of-record.

**The Problem:** Financial services organizations receive 100+ Message Center posts monthly, creating alert fatigue while regulatory requirements (FINRA 4511, SEC 17a-3/4, SOX 302/404) mandate documented change management with audit trails.

**The Solution:** Dataverse-based governance workflow with structured triage, assessment, decision logging, and immutable audit trails. Two implementation paths support different organizational needs.

### Added

- **Platform Change Governance Playbook** (`docs/playbooks/advanced-implementations/platform-change-governance/`)
  - `index.md` - Overview, problem statement, and path selection decision framework
  - `architecture.md` - Canonical reference architecture with Dataverse schema, security model, and state machine
  - `implementation-path-a.md` - Dataverse-only implementation (baseline governance)
  - `implementation-path-b.md` - Dataverse + Azure DevOps bi-directional integration
  - `labs.md` - Hands-on labs 1-3 (ingestion, model-driven app, ADO integration)
  - `evidence-and-audit.md` - Evidence standards mapping, retention requirements, examination response

- **Implementation Paths**
  - **Path A:** Dataverse-only baseline for most organizations
  - **Path B:** Dataverse + Azure DevOps for engineering teams with ALM requirements

- **Dataverse Schema**
  - MessageCenterPost table with 15+ fields for complete post tracking
  - AssessmentLog table for impact assessment history
  - DecisionLog table (organization-owned/immutable) for governance decisions
  - Security roles: MC Admin, MC Owner, MC Compliance Reviewer, MC Auditor

- **Power Automate Flows**
  - Message Center ingestion via Graph API polling
  - Dataverse → ADO work item creation (Path B)
  - ADO → Dataverse webhook handler (Path B)

### Enhanced

- **Control 2.3 (Change Management)** - Added cross-reference to Platform Change Governance playbook
- **Control 2.10 (Patch Management)** - Added link to Platform Change Governance in Additional Resources
- **Control 2.13 (Documentation)** - Added cross-reference to Platform Change Governance evidence standards
- **Playbooks Overview** - Added Platform Change Governance to Advanced Implementations table

### Regulatory Alignment

Supports compliance with:
- **FINRA 4511** - Books and records via DecisionLog immutable records
- **SEC 17a-4** - Audit-trail alternative via Dataverse change tracking
- **SOX 302/404** - Documented approval workflows with segregation of duties
- **GLBA 501(b)** - Administrative safeguards for customer-impacting changes

### Files Modified

| File | Change |
|------|--------|
| `docs/playbooks/advanced-implementations/platform-change-governance/index.md` | Created |
| `docs/playbooks/advanced-implementations/platform-change-governance/architecture.md` | Created |
| `docs/playbooks/advanced-implementations/platform-change-governance/implementation-path-a.md` | Created |
| `docs/playbooks/advanced-implementations/platform-change-governance/implementation-path-b.md` | Created |
| `docs/playbooks/advanced-implementations/platform-change-governance/labs.md` | Created |
| `docs/playbooks/advanced-implementations/platform-change-governance/evidence-and-audit.md` | Created |
| `mkdocs.yml` | Added navigation entries for Platform Change Governance |
| `docs/playbooks/index.md` | Added to Advanced Implementations table |
| `docs/controls/pillar-2-management/2.3-change-management-and-release-planning.md` | Added cross-reference |
| `docs/controls/pillar-2-management/2.10-patch-management-and-system-updates.md` | Added cross-reference |
| `docs/controls/pillar-2-management/2.13-documentation-and-record-keeping.md` | Added cross-reference |
| `CHANGELOG.md` | This entry |

### Validation

- `mkdocs build --strict`: Pass
- All internal links resolve
- Navigation renders correctly

---

## [1.1.9] — January 24, 2026 (Learn Monitor Documentation)

### Overview

Added comprehensive documentation explaining how the Microsoft Learn Documentation Monitor works, including verification that the system is operating correctly.

### Added

- **Learn Monitor Guide** (`docs/reference/learn-monitor-guide.md`) - Detailed documentation covering:
  - When the monitor runs (daily at 6 AM UTC)
  - When PRs are created (Sundays or when changes detected)
  - Change classification (CRITICAL/HIGH/MEDIUM/NOISE)
  - Local testing commands
  - Troubleshooting guide
- **Navigation updates** - Added guide to mkdocs.yml and reference index

### Verified

- Learn monitor script syntax valid
- Dependencies installed (requests, beautifulsoup4)
- Dry-run mode working correctly
- Single URL debug mode operational
- GitHub Actions workflow running successfully (5 consecutive daily passes)

### Files Modified

| File | Changes |
|------|---------|
| `docs/reference/learn-monitor-guide.md` | New file - comprehensive monitor documentation |
| `docs/reference/index.md` | Added Learn Monitor Guide to Technical Reference section |
| `mkdocs.yml` | Added navigation entry for Learn Monitor Guide |
| `.claude/CLAUDE.md` | Added guide to Key Files and Quick Navigation |
| `CHANGELOG.md` | This entry |

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/learn_monitor.py --dry-run --limit 3`: Pass

---

## [1.1.8] — January 24, 2026 (Documentation Consistency Fixes)

### Overview

This release addresses documentation inconsistencies identified during a review, including version alignment, regulatory coverage, maturity level clarification, and retention period standardization.

### Fixed

- **Version Alignment** - Updated governance-fundamentals.md, zones-and-tiers.md, CONTROL-INDEX.md to v1.1.8
- **Regulatory Coverage** - Added FDIC and NCUA to governance-fundamentals.md
- **Maturity Levels** - Clarified distinction between implementation levels (3) and maturity scale (0-4)
- **Retention Periods** - Aligned Zone 3 retention across zones and controls (7-10 years); added rationale

### Added

- **Microsoft-Built Agents Applicability** - Control mapping for Researcher, Analyst, Facilitator agents in governance-fundamentals.md

### Files Modified

| File | Changes |
|------|---------|
| `README.md` | Version (1.1.7→1.1.8), maturity levels clarification |
| `docs/framework/governance-fundamentals.md` | Version, regulators (FDIC/NCUA), maturity note, Microsoft-built agents section |
| `docs/framework/zones-and-tiers.md` | Version, retention rationale note |
| `docs/controls/CONTROL-INDEX.md` | Version |
| `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Zone 3 retention (7-10 years) |
| `docs/controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md` | Zone 3 retention (7-10 years) |
| `CHANGELOG.md` | This entry |

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: All 61 controls valid

---

## [1.1.7] — January 23, 2026 (Documentation Accuracy Fixes)

### Overview

This release addresses technical inaccuracies identified during a comprehensive deep review, including invalid KQL queries, incorrect PowerShell parameters, outdated regulatory references, and missing admin settings documentation.

### Fixed

- **KQL Queries** - Corrected 6 queries using non-existent tables (`CopilotInteraction`, `SharePointAuditLogs`, `SharePointSiteProperties`, `SharePointFileProperties`, `DlpAll`). Now use correct `OfficeActivity` and `CloudAppEvents` tables with appropriate RecordType filtering.

- **PowerShell Parameter** - Replaced `RestrictContentOrgWideSearchAndCopilot` with correct GA parameter `RestrictContentOrgWideSearch` across 9 files (4.6/4.7 playbooks, semantic-index-governance-queries.md, control 4.6).

- **SEC 17a-4 References** - Updated ~15 files to reflect October 2022 amendments (effective May 2023) that made WORM optional. Broker-dealers can now use either WORM storage or audit-trail alternative.

- **FINRA Notice 25-07 Status** - Added RFC disclaimer to key files clarifying that Notice 25-07 is a Request for Comment with comment period extending to July 2025 (not final requirements). Changed language from "requires" to "proposes" where applicable.

### Added

- **Data Source Limitations** - Added explanatory notes in KQL query documentation explaining hybrid PowerShell/KQL approach needed for site/file property data not available in Log Analytics.

- **Agent 365 Admin Settings** - Added reference to Microsoft 365 Admin Center "Agent settings" page in Control 1.2 and its portal walkthrough, including:
  - Allowed Agent Types configuration
  - Sharing controls
  - Templates (Agent 365 license)
  - User Access controls
  - FSI zone-specific recommended settings table

- **Parameter Status Notes** - Added admonitions clarifying GA vs. preview status for PowerShell parameters.

### Files Modified

| Area | Files Updated |
|------|---------------|
| KQL Queries | `semantic-index-governance-queries.md`, `3.9/powershell-setup.md`, `1.7` control |
| PowerShell Parameter | 9 files in 4.6, 4.7 playbooks and control docs |
| SEC 17a-4 | ~15 files including controls 1.7, 1.9, 2.13 and playbooks |
| FINRA 25-07 | ~6 key files including control 2.11, regulatory-mappings.md |
| Agent 365 | Control 1.2 and `1.2/portal-walkthrough.md` |

### Validation

- `python scripts/verify_controls.py`: ✅ All 61 controls valid
- Control structure: ✅ Pass

---

## [1.1.6] — January 20, 2026 (Microsoft Learn Documentation Monitor)

### Overview

This release adds an automated monitoring system to detect changes in Microsoft Learn documentation that may require updates to the FSI-AgentGov framework. The monitor runs daily, classifies changes by impact, identifies affected controls and playbooks, and creates PRs for human review.

### Added

- **Microsoft Learn Documentation Monitor** (`scripts/learn_monitor.py`)
  - Monitors ~190 Microsoft Learn URLs from the watchlist
  - Detects content changes using BeautifulSoup + SHA-256 hashing
  - Classifies changes as meaningful/minor/noise based on:
    - UI navigation steps (CRITICAL for playbooks)
    - Policy language and compliance features (HIGH)
    - Deprecation notices and breaking changes (HIGH)
    - Configuration instructions (MEDIUM)
  - Maps changes to affected controls and playbooks
  - Generates markdown reports with diff snippets
  - Supports debugging: `--url`, `--debug`, `--verbose`, `--limit`, `--dry-run`

- **GitHub Actions Workflow** (`.github/workflows/learn-monitor.yml`)
  - Daily scheduled runs at 6:00 AM UTC
  - Manual trigger via workflow_dispatch
  - Creates PRs on meaningful changes or weekly baseline (Sundays)
  - Labels: `documentation`, `automated`, `learn-watch`

- **State and Report Directories**
  - `data/` - Stores `learn-monitor-state.json` with content hashes
  - `reports/learn-changes/` - Stores dated change reports

### Changed

- **Fixed cross-platform path issue** (`scripts/compile_researcher_package.py`)
  - Changed from hardcoded Windows path to dynamic detection
  - Now works on Windows, macOS, and Linux

- **Improved hook error handling** (`scripts/hooks/boundary-check.py`)
  - Added empty input handling
  - Added JSONDecodeError catch
  - Simplified confusing conditional logic

- **Improved hook error handling** (`scripts/hooks/researcher-package-reminder.py`)
  - Added empty input handling
  - Added broad exception catch
  - Both hooks now fail open (allow on error)

### Files Modified

| File | Action |
|------|--------|
| `scripts/learn_monitor.py` | Created (~750 lines) |
| `.github/workflows/learn-monitor.yml` | Created |
| `data/.gitkeep` | Created |
| `reports/learn-changes/.gitkeep` | Created |
| `scripts/compile_researcher_package.py` | Fixed path detection |
| `scripts/hooks/boundary-check.py` | Improved error handling |
| `scripts/hooks/researcher-package-reminder.py` | Improved error handling |

### Validation

- `mkdocs build --strict`: ✅ Pass
- `python scripts/learn_monitor.py --limit 3 --dry-run`: ✅ Pass
- `python scripts/compile_researcher_package.py`: ✅ Pass
- Hook scripts handle edge cases without errors

---

## [1.1.5] — January 20, 2026 (Claude Code Configuration Update)

### Overview

This release updates the Claude Code configuration to align with latest Anthropic documentation (v2.1+, January 2026), including YAML frontmatter for skills and a split settings architecture.

### Added

- **Team-shared settings file** (`.claude/settings.json`)
  - Base permissions for git, mkdocs, python, pip commands
  - Deny rules for dangerous operations (`rm -rf /`, `.env` access)
  - Hook configurations (PreToolUse, PostToolUse)
  - Version-controlled for team consistency

- **YAML frontmatter to all 4 skills**
  - `name` - Skill identifier for invocation
  - `description` - Enables auto-suggestion based on task context
  - `allowed-tools` - Restricts tool access per skill
  - `user-invocable: true` - Enables `/skill-name` invocation

### Changed

- **Settings architecture split**
  - `settings.json` - Team-shared configuration (committed)
  - `settings.local.json` - Local overrides only (not committed)
  - Settings merge at runtime for flexibility

- **Slimmed settings.local.json**
  - Reduced from 30 rules to 5 local-only rules
  - Contains: `includeCoAuthoredBy`, WebFetch domains, GitHub CLI permissions

- **Updated CLAUDE.md documentation**
  - New "Configuration" section with settings file reference
  - Updated directory structure showing both settings files
  - Enhanced Skills section with frontmatter description
  - Detailed hooks documentation with JSON output format

### Skills Updated

| Skill | Allowed Tools |
|-------|---------------|
| `/update-control` | Read, Edit, Glob, Grep, Bash |
| `/add-control` | Read, Write, Edit, Glob, Grep, Bash |
| `/update-excel` | Read, Bash, Glob |
| `/verify-ui` | Read, Edit, Glob, Grep, WebFetch |

### Files Modified

| File | Action |
|------|--------|
| `.claude/skills/update-control.md` | Added YAML frontmatter |
| `.claude/skills/add-control.md` | Added YAML frontmatter |
| `.claude/skills/update-excel.md` | Added YAML frontmatter |
| `.claude/skills/verify-ui.md` | Added YAML frontmatter |
| `.claude/settings.json` | Created (team-shared) |
| `.claude/settings.local.json` | Slimmed to local-only |
| `.claude/CLAUDE.md` | Updated configuration documentation |

### Validation

- `mkdocs build --strict`: ✅ Pass
- All 4 skills have valid YAML frontmatter
- Hook scripts output correct JSON format
- Boundary check hook blocks dangerous commands

---

## [1.1.4] — January 20, 2026 (Microsoft Audit Reporting Tools Integration)

### Overview

This release integrates two Microsoft Engineering open-source tools that address a common FSI pain point: M365 Admin Center provides limited Copilot/AI reporting data, and Viva Insights data is de-identified. These tools enable enterprise-scale audit data extraction and adoption analytics.

### Added

- **Microsoft Audit Reporting Tools Playbook** (`docs/playbooks/advanced-implementations/microsoft-audit-reporting-tools.md`)
  - Comprehensive guide for AI-in-One Dashboard and PAX (Portable Audit eXporter)
  - FSI-specific implementation considerations and use cases
  - Integration guidance for FINRA 25-07 prompt/response capture
  - SEC 17a-4 WORM storage workflow support
  - Compliance considerations (data handling, permissions, classification)

- **Microsoft Open Source Tools Section** (`docs/reference/microsoft-learn-urls.md`)
  - AI-in-One Dashboard GitHub repository link
  - PAX (Portable Audit eXporter) GitHub repository link
  - Cross-reference to implementation playbook

### Enhanced

- **Control 1.7 (Comprehensive Audit Logging)** - Added cross-reference to Microsoft Audit Reporting Tools playbook for enterprise-scale audit extraction
- **Control 3.2 (Usage Analytics)** - Added cross-reference to Microsoft Audit Reporting Tools playbook for enhanced adoption analytics
- **Control 3.3 (Compliance Reporting)** - Added cross-reference to Microsoft Audit Reporting Tools playbook for examination evidence generation
- **Control 3.8 (Copilot Hub)** - Added cross-reference to Microsoft Audit Reporting Tools playbook for supplemental reporting capabilities

### Changed

- **mkdocs.yml** - Added navigation entry for Microsoft Audit Reporting Tools under Advanced Implementations

### Tools Integrated

| Tool | GitHub Repository | Purpose |
|------|-------------------|---------|
| AI-in-One Dashboard | microsoft/AI-in-One-Dashboard | Power BI template for Copilot adoption analytics |
| PAX (Portable Audit eXporter) | microsoft/PAX | PowerShell scripts to export audit log data at scale |

### Gaps Addressed

These tools address the following capability gaps identified in the framework:

| Gap | Tool | How Addressed |
|-----|------|---------------|
| Real-Time Executive Dashboard | AI-in-One Dashboard | Pre-built Power BI template with department segmentation |
| Advanced Data Analytics | PAX | Raw data export for custom analytics pipelines |
| Trend Analysis | AI-in-One Dashboard | Time-series adoption tracking by department/role |
| Third-Party Integration | PAX | CSV/Excel export compatible with any BI tool |
| 50K Record Export Limit | PAX | Incremental exports with watermarking bypass native limits |

### Files Modified

| File | Change |
|------|--------|
| `docs/playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` | **Created** - New playbook |
| `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` | Added cross-reference |
| `docs/reference/microsoft-learn-urls.md` | Added Microsoft Open Source Tools section |
| `mkdocs.yml` | Added nav entry for new playbook |

### Validation

- `mkdocs build --strict`: ✅ Pass
- All cross-references resolve correctly
- GitHub repository links verified accessible

---

## [1.1.3] — January 19, 2026 (Deep Review & Enhancements)

### Overview

This release completes a comprehensive 10-agent deep review of the entire repository, verifying completeness, regulatory coverage, and alignment with framework objectives. All identified enhancements have been implemented.

### Added

- **Microsoft Learn URL Tracking** (`docs/reference/microsoft-learn-urls.md`)
  - Expanded from 48 to 159 tracked URLs (100% coverage of links used in documentation)
  - Added 12 new product categories: Azure Services, Microsoft Defender, Power Automate, Power Apps, Microsoft Teams, Microsoft Graph API, Power BI, Microsoft Viva, Security Operations, PowerShell References, Office 365 Management API, Microsoft Entra Agent ID
  - All links verified as of January 2026
  - Purpose: Enable automated monitoring for Microsoft documentation changes

- **Microsoft Platform Update Monitoring** (`docs/playbooks/control-implementations/2.7/troubleshooting.md`)
  - New section: Monitoring Channels (Message Center, Service Health, Release Plans, What's New, Roadmap)
  - Recommended monitoring process (weekly/monthly/quarterly cadence)
  - Re-validation triggers for Microsoft platform changes
  - PowerShell script for Message Center monitoring

- **ECOA Quarterly Testing Requirements** (`docs/playbooks/control-implementations/2.11/verification-testing.md`)
  - ECOA 9 protected classes reference table with citations (15 U.S.C. § 1691)
  - Quarterly testing checklist with due dates and owners
  - Minimum sample sizes per protected class category
  - New Test 5: Verify Quarterly Cadence for Zone 3 agents

### Documentation

- **CLAUDE.md Updates**
  - Added Comprehensive Deep Review section documenting 10-agent analysis
  - Added Review Directory (`review/`) documentation explaining external validation artifacts
  - Updated version to v1.1.3

### Verified (No Changes Needed)

The deep review confirmed the following are already adequately covered:

| Gap Candidate | Status | Existing Coverage |
|---------------|--------|-------------------|
| IP Cookie Binding | ✅ Covered | Control 1.20 |
| AI Data Sharing Tenant Setting | ✅ Covered | Controls 2.1, 4.7 |
| Cross-Geographic Data Movement | ✅ Covered | Controls 2.1, 1.20 |
| Maker Welcome Content | ✅ Covered | Control 2.1 Section 4 |
| AI Plugin Governance | ✅ Covered | Controls 1.4, 2.7, 4.7 |
| Skills Connector Governance | ✅ Covered | Controls 1.4, 2.17 |
| Web Channel Security | ✅ Covered | Controls 4.7, 4.1 |
| Colorado AI Act | ✅ Covered | `docs/playbooks/regulatory-modules/` |

### Deep Review Summary

| Area | Score | Status |
|------|-------|--------|
| Framework Alignment | 9.5/10 | Excellent |
| Control Completeness | 10/10 | Complete |
| Cross-Reference Integrity | 9.5/10 | Excellent |
| Stale Documentation | 1/10 (staleness) | Very Clean |
| Regulatory Coverage | 85/100 | Strong |
| Microsoft Learn Links | 100% | Complete |
| Copilot Studio DLP | 94% | Strong |
| Power Platform Architecture | 100% | Complete |

---

## [1.1.2] — January 19, 2026 (NIST AI RMF Crosswalk Correction)

### Fixed

- **NIST AI RMF Crosswalk Accuracy** (`docs/reference/nist-ai-rmf-crosswalk.md`)
  - Corrected subcategory counts in summary table (was 61, actual 67 subcategories addressed)
  - Added methodology section explaining coverage calculation against NIST AI RMF 1.0 (72 total subcategories)
  - Updated coverage figures: 93% of NIST subcategories addressed, 97% effective coverage of applicable areas
  - Documented 5 subcategories not explicitly addressed (MEASURE 2.12/2.13, MAP 3.4/3.5, GOVERN 4.4) with rationale
  - Updated auditor guidance with accurate coverage metrics

### Changed

- **Coverage Summary Table:** Now shows correct subcategory counts per function (GOVERN 19, MAP 16, MEASURE 19, MANAGE 13)
- **Coverage Claim:** Changed from "92% Full coverage" to "93% subcategories addressed, 97% effective coverage of applicable areas"

### Context

This fix was identified during a comprehensive 18-agent framework review. The original summary table had arithmetic errors in the subcategory counts, and the coverage calculation did not account for the full NIST AI RMF 1.0 structure (72 subcategories). The crosswalk content and control mappings remain accurate; only the summary statistics were corrected.

---

## [1.1.1] — January 2026 (Researcher Gap Analysis Response)

### Overview

This release addresses findings from an external researcher gap analysis, implementing valid recommendations and documenting rationale for rejected items.

**Summary:** Of 19 claimed gaps, 8 were invalid (already covered), 5 were partially valid (minor enhancements), 2 were valid (new content created), and 4 were out of scope.

### Added

- **Control 2.21: AI Marketing Claims and Substantiation** — New control addressing SEC Marketing Rule (206(4)-1) and "AI washing" enforcement precedent (Delphia, Global Predictions 2024 settlements)
- **4 Playbooks for Control 2.21:**
  - `portal-walkthrough.md` — Claims inventory setup and review workflow
  - `powershell-setup.md` — SharePoint list and automation scripts
  - `verification-testing.md` — Test cases and attestation template
  - `troubleshooting.md` — Common issues and resolutions
- **NIST AI RMF Crosswalk** (`docs/reference/nist-ai-rmf-crosswalk.md`) — Maps all 61 controls to NIST AI RMF GOVERN/MAP/MEASURE/MANAGE functions (92% coverage)
- **SEC Marketing Rule section** in `docs/reference/regulatory-mappings.md`

### Enhanced (8 Controls)

- **Control 1.7:** Added AI-generated communication tagging guidance per FINRA 25-07 (AI vs human attribution, event types)
- **Control 1.10:** Added monitored Copilot and AI locations table with audit event names and friendly names
- **Control 1.8:** Added AI-enabled threat patterns section (deepfakes, AI phishing, synthetic identities) per NYDFS cyber guidance
- **Control 1.11:** Added PIM baselines table for AI administration roles with activation durations and approvers
- **Control 1.23:** Added PIM integration for sensitive agent operations (publishing, deletion, policy changes)
- **Control 1.4:** Added Copilot plugins and extensions terminology table clarifying governance scope
- **Control 2.7:** Added FSI-specific vendor categories table including archiving vendors (Smarsh, Global Relay, etc.)
- **Control 3.3:** Added AI regulatory impact assessment template with regulatory driver mapping

### Changed

- **Control count:** 60 → 61 controls
- **Pillar 2 count:** 20 → 21 controls
- Updated `docs/controls/CONTROL-INDEX.md` with Control 2.21
- Updated `mkdocs.yml` navigation for Control 2.21 and NIST crosswalk
- Updated `docs/reference/regulatory-mappings.md` coverage table to 61 controls

### Researcher Gap Analysis Summary

| Gap Category | Count | Action |
|--------------|-------|--------|
| **INVALID (Already Covered)** | 8 | No action - researcher missed existing coverage |
| **PARTIALLY VALID (Enhancement)** | 5 | Minor documentation improvements (completed) |
| **VALID (New Content)** | 2 | Control 2.21 + NIST crosswalk (completed) |
| **OUT OF SCOPE** | 4 | Rejected - outside M365 framework focus |

**Rejected Items (Out of Scope):**
- REG-004: SEC predictive analytics (proposal not finalized)
- REG-007: NAIC AI Model Bulletin (insurance outside primary scope)
- CC-012: ISO 42001/23894 (US FSI-focused, not multi-jurisdiction)
- IND-015: SEC/FINRA exam focus (restatement, not gap)

---

## [1.1] — January 2026

### Architecture

- **Three-Layer Documentation Model:**
  - **Layer 1 - Framework** (`docs/framework/`): Governance principles for executives and compliance
  - **Layer 2 - Controls** (`docs/controls/`): Technical specifications (60 controls across 4 pillars)
  - **Layer 3 - Playbooks** (`docs/playbooks/`): Step-by-step implementation procedures
- Renamed `docs/reference/pillar-*/` to `docs/controls/pillar-*/` for clarity
- Reorganized `docs/operational-templates/` content into `docs/playbooks/`
- Added role-based navigation on homepage

### Added

- **Framework Layer (9 documents):**
  - `executive-summary.md` — Board-level overview
  - `zones-and-tiers.md` — Zone 1/2/3 classification guidance
  - `adoption-roadmap.md` — 30/60/90-day phased implementation
  - `agent-lifecycle.md` — Agent lifecycle management
  - `operating-model.md` — RACI and accountability
  - `governance-fundamentals.md` — Core governance principles
  - `governance-cadence.md` — Recurring governance activities
  - `regulatory-framework.md` — FSI regulatory landscape
  - `index.md` — Framework layer overview

- **Control Implementation Playbooks (240 files):**
  - Created 4 playbooks per control (60 controls × 4 = 240 files)
  - Playbook types for each control:
    - `portal-walkthrough.md` — Step-by-step portal configuration
    - `powershell-setup.md` — PowerShell automation scripts
    - `verification-testing.md` — Test cases and evidence collection
    - `troubleshooting.md` — Common issues and resolutions
  - Located at `docs/playbooks/control-implementations/{control-id}/`
  - Each playbook includes: prerequisites, step-by-step instructions, configuration by governance level, FSI example configurations, validation checklists

- **Playbook Categories:**
  - `governance-operations/` — Standing procedures (weekly reviews, quarterly assessments)
  - `compliance-and-audit/` — Audit preparation, evidence collection, examination response
  - `incident-and-risk/` — Data exposure, compliance violation handling
  - `agent-lifecycle/` — Agent provisioning, retirement, updates

- **Scripts Directory Enhancement:**
  - `scripts/README.md` — Usage guide
  - `scripts/requirements.txt` — Python dependencies
  - `scripts/governance/` — Governance automation (placeholder)
  - `scripts/reporting/` — Reporting automation (placeholder)
  - `scripts/hooks/boundary-check.py` — Project boundary protection hook

- **GitHub Issue Templates:**
  - `bug-report.md` — Bug reporting template
  - `feature-request.md` — Feature request template
  - `ui-verification.md` — UI verification checklist

### Changed

- Zone 1 regulatory language softened to conditional phrasing
- Pillar 4 explicitly positions as SharePoint specialization of Pillars 1-3
- HITL patterns explicitly defined (Pre-Approval, Sampled Review, Escalation-on-Threshold)
- Controls 2.12 and 2.19 updated with customer-facing conduct notes
- Updated `.claude/claude.md` with three-layer documentation guidance
- Updated `.github/copilot-instructions.md` with new directory structure
- Updated `scripts/verify_controls.py` to use `docs/controls/` path
- Updated `scripts/compile_researcher_package.py` to use `docs/controls/` path
- Updated `scripts/hooks/researcher-package-reminder.py` to detect both old and new paths

### Fixed

- **Fixed `verify_controls.py` validation mismatch** (CI failure):
  - Updated footer constants to match actual control format (`Updated: January 2026`, `Version: v1.1`, `UI Verification Status:`)
  - Updated required headings to match actual control structure (`## Objective`, `## Why This Matters for FSI`, `## Control Description`, etc.)
  - Updated required metadata fields to match actual control files (`**Control ID:**`, `**Pillar:**`, `**Regulatory Reference:**`)
  - Changed Primary Owner validation to check for `## Roles & Responsibilities` section
  - Fixed missing `UI Verification Status` in controls 2.1 and 2.2 footers
- Fixed 6 broken cross-references between controls:
  - Control 2.16 → 4.1 (wrong filename)
  - Control 2.19 → 1.6 (wrong filename)
  - Control 2.4 → 3.4 (wrong filename)
  - Control 2.6 → 3.3 (wrong filename)
  - Control 3.5 → 2.2 (wrong filename)
  - Control 3.6 → 2.3 (wrong filename)
- Fixed relative path issues in playbooks (1.1, 3.1, 3.2)
- Resolved all link warnings in mkdocs build

### Removed (Legacy Cleanup - January 18, 2026)

- **Deleted legacy pillar directories** (64 files):
  - `docs/reference/pillar-1-security/` — superseded by `docs/controls/pillar-1-security/`
  - `docs/reference/pillar-2-management/` — superseded by `docs/controls/pillar-2-management/`
  - `docs/reference/pillar-3-reporting/` — superseded by `docs/controls/pillar-3-reporting/`
  - `docs/reference/pillar-4-sharepoint/` — superseded by `docs/controls/pillar-4-sharepoint/`
- **Deleted legacy operational-templates** (21 files):
  - `docs/operational-templates/` — content migrated to `docs/playbooks/`
- **Deleted excluded getting-started duplicates** (4 files):
  - `docs/getting-started/overview.md` — duplicate of `docs/framework/index.md`
  - `docs/getting-started/zones.md` — duplicate of `docs/framework/zones-and-tiers.md`
  - `docs/getting-started/lifecycle.md` — duplicate of `docs/framework/agent-lifecycle.md`
  - `docs/getting-started/governance-review-cadence.md` — duplicate of `docs/framework/governance-cadence.md`
- **Updated mkdocs.yml** — removed exclude_docs entries for deleted files
- **Fixed docs/downloads/index.md** — corrected control count (58→60) and version (v1.0→v1.1)

### Documentation Cleanup (January 18, 2026)

Fixed stale documentation after v1.1 restructuring:

- **docs/reference/regulatory-mappings.md** — Fixed broken hyperlink to Colorado AI Impact Assessment (changed from deleted `../operational-templates/...` to `../playbooks/regulatory-modules/...`)
- **docs/getting-started/checklist.md** — Updated control counts from 48 to 60; fixed pillar counts (19→23, 15→20, 9→10, 5→7); updated version footer from v1.0 to v1.1
- **docs/reference/faq.md** — Updated control counts from 48 to 60 with corrected pillar breakdown
- **docs/images/README.md** — Updated documentation paths from `docs/reference/pillar-*` to `docs/controls/pillar-*`
- **docs/images/VERIFY.md** — Updated path pattern from `docs/reference/...` to `docs/controls/...`
- **docs/templates/README.md** — Removed references to non-existent JSON files; updated control count from 48 to 60; updated "After Creating a Control" steps to reference CONTROL-INDEX.md
- **mkdocs.yml** — Added `playbooks/control-implementations/*/` to exclude_docs to suppress 240 "not in nav" warnings

### Comprehensive Repository Verification (January 18, 2026)

Exhaustive verification of all repository content (scripts, Excel files, documentation) with automated tooling.

**Scripts Deleted (6 legacy one-time migration scripts with stale paths):**
- `scripts/apply_primary_owner_roles.py`
- `scripts/fix_zone_guidance_grammar.py`
- `scripts/tailor_zone_guidance.py`
- `scripts/fix_controls_targeted_cleanup.py`
- `scripts/audit_controls_zone_hygiene.py`
- `scripts/generate_zone_cleanup_plan.py`

**Scripts Added:**
- `scripts/verify_excel_templates.py` — Validates Excel template control counts and stale content
- `scripts/update_excel_templates.py` — Updates Excel templates (version references, missing controls)

**Documentation Fixed:**
- **docs/reference/microsoft-learn-urls.md** — Updated footer date from "December 2025" to "January 2026"
- **docs/reference/faq.md** — Updated preview feature table header from "Dec 2025" to "Jan 2026"

**Excel Templates Updated (all 6 files):**
- Updated version footer from "v1.0 Beta" to "v1.1" in all 6 Excel files
- Added missing controls 1.23 and 2.20 to `governance-maturity-dashboard.xlsx` (58→60 controls)

**Validation Results:**
- All documentation layers verified clean (framework, reference, controls, playbooks, getting-started)
- All Excel templates pass verification (`verify_excel_templates.py`)
- Zero stale "48 control" references in docs
- Zero stale `docs/reference/pillar-*` paths in active scripts
- Zero stale "v1.0" references (except CHANGELOG historical entries)

### Playbook Navigation Integration Fix (January 19, 2026)

**Problem Fixed:** 240 playbook files were excluded from MkDocs build and not published to GitHub Pages, causing broken links in control documentation Section 8 (Implementation Guides).

**Root Cause:** The `playbooks/control-implementations/*/` directory pattern was listed in `mkdocs.yml` under `exclude_docs` (added during v1.1 to suppress "not in nav" warnings), which prevented the playbook files from being published.

**Solution:**
- Removed `playbooks/control-implementations/*/` from `exclude_docs` in `mkdocs.yml`
- Added all 60 control playbook sections to site navigation under `Playbooks → Control Implementations` (~305 lines)
- Each control now has 4 nested playbook links: Portal Walkthrough, PowerShell Setup, Verification, Troubleshooting

**Files Modified:**
- `mkdocs.yml` - Removed exclusion pattern, added nested playbook nav structure (lines 163-468)
- `.claude/CLAUDE.md` - Added context section documenting this fix
- `.claude/settings.local.json` - Added `includeCoAuthoredBy: false` setting

**Validation:**
- `mkdocs build --strict` passes
- All 240 playbook HTML files now generated in site/
- Navigation hierarchy complete: Framework → Controls → Playbooks (with nested control sections)

---

## [1.0] — January 2026

### Researcher Feedback v2 - Agentic AI and 2025/2026 Compliance (January 17, 2026)

**Status:** New controls and enhancements addressing researcher feedback
**Date:** January 17, 2026
**Scope:** 2 new controls + 6 control enhancements (58 → 60 controls)

#### New Controls Added

- **Control 1.23: Step-up Authentication for Agent Operations** (HIGH priority)
  - Risk-based authentication escalation for sensitive agent actions
  - Multi-factor authentication triggers for financial transactions
  - Zone-specific step-up thresholds
  - Regulatory alignment: FFIEC Authentication Guidance, GLBA 501(b), FINRA 3110

- **Control 2.20: Adversarial Testing and Red Team Framework** (HIGH priority)
  - Structured red team exercises for AI agents
  - Prompt injection and jailbreak testing procedures
  - Data exfiltration and boundary testing
  - Regulatory alignment: OCC 2011-12, Fed SR 11-7, NIST AI RMF

#### Control Enhancements

- **Control 1.18 (Application-Level Authorization)** - Enhanced RBAC guidance for agentic scenarios
- **Control 2.3 (Change Management)** - Added AI-specific change categories and risk assessment
- **Control 2.5 (Testing and Validation)** - Expanded test scenarios for agent behaviors
- **Control 2.6 (Model Risk Management)** - Enhanced OCC 2011-12 alignment with agentic AI considerations
- **Control 2.12 (Supervision and Oversight)** - Updated FINRA 3110 guidance for automated supervision
- **Control 4.7 (Copilot Data Governance)** - Enhanced data governance for M365 Copilot grounding

#### Supporting Materials Added

- **Evidence Standards Reference** (`docs/reference/evidence-standards.md`)
- **Governance Operating Calendar** (`docs/operational-templates/templates/governance-operating-calendar.md`)
- **Screenshot Specifications** for controls 1.20, 1.21, 2.16, 4.6
- **Researcher Package Compiler** (`scripts/compile_researcher_package.py`)

#### Framework Statistics Update

- **Total controls:** 58 → 60 (+2)
- **Pillar 1 (Security):** 22 → 23 (+1)
- **Pillar 2 (Management):** 19 → 20 (+1)

---

### Feature Gap Analysis Implementation (January 16, 2026)

**Status:** New controls and enhancements addressing identified feature gaps
**Date:** January 16, 2026
**Scope:** 2 new controls + 1 control enhancement (55 → 57 controls)

#### New Controls Added

- **Control 2.19: Customer AI Disclosure and Transparency** (HIGH priority)
  - Formal processes for disclosing AI agent use to customers
  - Disclosure templates by zone (Basic/Standard/Comprehensive)
  - Human escalation path requirements
  - Regulatory alignment: SEC Reg BI, CFPB UDAAP, FINRA 25-07, GLBA 501(b)
  - Change management workflow for disclosure updates

- **Control 4.7: Microsoft 365 Copilot Data Governance** (MEDIUM-HIGH priority)
  - Governance for embedded M365 Copilot (Word, Excel, Teams, etc.)
  - Knowledge source boundaries via Restricted Content Discovery
  - Plugin and web access governance
  - User behavior guardrails and acceptable use policy
  - Output review processes for customer-facing content
  - Distinction from Copilot Studio agent governance

#### Control Enhancements

- **Control 3.10 (Hallucination Feedback Loop)** - Added 4 new sections:
  - **Proactive Output Quality Monitoring** - Pre-delivery content scanning, quality scoring thresholds, automated flagging
  - **Content Safety Guardrails** - Tone monitoring, financial advice boundaries, harmful content prevention
  - **Sensitive Topic Handling** - Financial hardship, complaints, crisis, regulatory inquiry procedures
  - **Real-Time Quality Scoring** - Confidence-based routing, quality dashboards, degradation alerting

#### Supporting Files Updated

- **CONTROL-INDEX.md** - Added 2.19, 4.7; updated counts (55 → 57)
- **regulatory-mappings.md** - Added new controls to applicable regulations; updated coverage summary
- **mkdocs.yml** - Added navigation entries for 2.19, 4.7

#### Framework Statistics Update

- **Total controls:** 55 → 57 (+2)
- **Pillar 2 (Management):** 18 → 19 (+1)
- **Pillar 4 (SharePoint):** 6 → 7 (+1)

#### Gap Analysis Source

These additions address gaps identified during framework self-review:
1. Customer AI disclosure (partial coverage → dedicated control)
2. Output quality/content safety (reactive → proactive monitoring)
3. M365 Copilot governance (minimal → dedicated control)

---

### Link Validation CI Fix (January 16, 2026)

**Status:** Fixed broken external URLs causing CI failure
**Date:** January 16, 2026
**Scope:** 8 broken external URLs across 5 control files

#### Configuration Update

- **mlc-config.json** - Expanded SEC.gov ignore pattern to handle 403 blocks on regulation pages

#### URL Fixes

| File | Issue | Fix |
|------|-------|-----|
| 1.21 (Adversarial Input Logging) | Dead link to Defender for Cloud Apps AI protection | Updated to AI Agent Inventory URL |
| 2.16 (RAG Source Integrity) | Dead links + placeholder URL parsed as link | Fixed Copilot Studio knowledge URL, SharePoint management URL, escaped placeholder |
| 2.17 (Multi-Agent Orchestration) | Dead link to Power Automate error handling | Updated to coding guidelines error handling URL |
| 4.6 (Grounding Scope Governance) | Dead links to SharePoint restricted content | Updated to restricted-content-discovery and data-access-governance-reports URLs |

#### Verification

- All 5 affected files pass `markdown-link-check` validation
- `mkdocs build --strict` passes with zero errors

---

### Link Consistency and Regulatory Mappings Update (January 16, 2026)

**Status:** Self-review implementation - cross-reference and link improvements
**Date:** January 16, 2026
**Scope:** Link standardization, regulatory mappings update, navigation improvements

#### Link Standardization

- **Standardized Related Controls format** across all controls to Style A pattern: `| [X.Y - Control Name](path.md) | Description |`
- **Fixed Control 1.5** - Changed from Style B (`[Control 1.6: DSPM for AI]`) to Style A
- **Fixed Control 4.2** - Removed unique Priority column, standardized link format
- **Fixed Control 2.18** - Added missing reciprocal link to 2.12 (Supervision)

#### Dependencies Converted to Clickable Links

Converted plain text dependencies to markdown links in 7 Pillar 2 controls:
- Control 2.8 (Access Control and Segregation of Duties)
- Control 2.9 (Agent Performance Monitoring)
- Control 2.10 (Patch Management)
- Control 2.11 (Bias Testing)
- Control 2.12 (Supervision and Oversight)
- Control 2.13 (Documentation and Record Keeping)
- Control 2.14 (Training and Awareness)

#### Regulatory Mappings Update

- **Added 7 missing controls** to `regulatory-mappings.md`: 1.20, 1.21, 2.16, 2.17, 2.18, 3.10, 4.6
- **Updated Control Coverage Summary** from 48/48 to 55/55 controls
- **Recalculated percentages** for all 15 regulations

#### Cross-Pillar Navigation

- Added Control 4.1 (SharePoint IAG) reference to Control 1.4 (Advanced Connector Policies)
- Verified existing cross-pillar links (2.1→1.20, 3.8→3.1/3.2, 1.14→1.3)

#### Verification

- Confirmed mkdocs.yml includes all 55 controls in correct numerical order
- `mkdocs build --strict` passes with zero errors

---

### Gap Analysis Response Update (January 16, 2026)

**Status:** Implementation of AI Governance Research Unit gap analysis recommendations
**Date:** January 16, 2026
**Scope:** 6 new controls + 4 control enhancements + 3 supporting documents (49 → 55 controls)

#### New Controls Added

- **Control 1.21: Adversarial Input Logging** (Critical)
  - Detection patterns for prompt injection, jailbreaking, encoding attacks
  - KQL queries for Sentinel integration
  - Zone-specific configuration (Zone 1: monitoring only, Zone 2-3: blocking)
  - Regulatory alignment: FFIEC CAT 2025, GLBA 501(b)

- **Control 2.16: RAG Source Integrity Validation** (Critical)
  - Knowledge source approval workflows
  - Content versioning and staleness detection
  - Citation logging requirements
  - Regulatory alignment: Fed SR 11-7, FDIC FIL-15-2025

- **Control 2.17: Multi-Agent Orchestration Limits** (High)
  - Delegation depth limits by zone (Zone 1: 0, Zone 2: 2, Zone 3: 3)
  - Circuit breaker configuration for cascade failure prevention
  - HITL checkpoint integration
  - Regulatory alignment: FINRA 2026 Priorities

- **Control 2.18: Automated Conflict of Interest Testing** (Critical)
  - Test scenarios for proprietary bias, commission bias, cross-selling
  - SEC Reg BI compliance testing procedures
  - Automated test execution scripts
  - Regulatory alignment: SEC Reg BI, SEC 10b-5

- **Control 3.10: Hallucination Feedback Loop** (Medium)
  - User feedback collection mechanisms
  - Hallucination categorization taxonomy
  - Remediation tracking workflow
  - Regulatory alignment: CFPB UDAAP, SOX 302

- **Control 4.6: Grounding Scope Governance** (Critical)
  - Semantic Index site scoping configuration
  - Exclusion rules for Draft, Archived, Personal content
  - PowerShell for auditing indexed content scope
  - Regulatory alignment: SEC 17a-3/4, GLBA

#### Control Enhancements

- **Control 1.7 (Audit Logging)** - Added Adversarial Input Pattern Detection section with encoding attack detection (Base64, Unicode obfuscation, prompt chaining)
- **Control 2.6 (Model Risk Management)** - Added Step 6a: Prompt Engineering Change Review with checklist for system prompt, topic, fallback, and grounding instruction changes
- **Control 3.4 (Incident Reporting)** - Added Step 5a: RAG Citation Logging for Incident Investigation with KQL queries
- **Control 4.2 (Site Access Reviews)** - Added AI Agent Service Account Access Reviews section with least privilege checklist for service principals

#### New Operational Templates

- **AI Incident Response Playbook** (`specs/ai-incident-response-playbook.md`)
  - Incident categories: Hallucination, Prompt Injection, Data Leakage, Bias
  - Response procedures with timelines (T+0 through T+48 hours)
  - Regulatory notification requirements (GLBA, FINRA 4530, SEC)
  - Post-incident review checklist

- **Human-in-the-Loop Trigger Definitions** (`specs/human-in-the-loop-triggers.md`)
  - Mandatory HITL triggers (financial thresholds, suitability determinations)
  - Configurable triggers (confidence scores, complexity indicators)
  - Zone-specific HITL configurations
  - SLA definitions and breach handling

- **Semantic Index Governance Queries** (`templates/semantic-index-governance-queries.md`)
  - PowerShell: Get-CopilotRestrictionAudit, Get-HighRiskIndexedContent
  - KQL queries for Sentinel monitoring
  - Weekly audit automation script

#### Framework Statistics Update

- **Total controls:** 49 → 55 (+6)
- **Pillar 1 (Security):** 20 → 21 (+1)
- **Pillar 2 (Management):** 15 → 18 (+3)
- **Pillar 3 (Reporting):** 9 → 10 (+1)
- **Pillar 4 (SharePoint):** 5 → 6 (+1)
- **Operational templates:** 9 → 10 (+1)
- **Operational specifications:** 5 → 7 (+2)

---

### Operational Templates & Comprehensive Framework Validation

**Status:** Operational templates released + comprehensive validation against Microsoft Learn documentation
**Date:** January 10, 2026
**Scope:** Enhancements to existing 48 controls; no breaking changes

#### Added

- **Operational Templates Section** - 14 new production-ready templates and specifications
  - 9 implementation templates (matrices, schemas, registries)
  - 5 technical specifications (dashboards, detection, routing)
  - Optional Colorado AI Act readiness module (conditional for CO operations)
- **Infrastructure & Documentation**
  - `.claude/claude.md` - Claude Code agent instructions (mirrors GitHub Copilot guidance)
  - Comprehensive validation report with regulatory and technical feasibility assessment
  - Cross-reference links from existing controls (1.7, 2.7, 2.12, 3.8) to related templates
- **Review & Validation Materials**
  - `review/validation-findings.md` - Comprehensive review against Microsoft Learn (697 lines)
  - `review/validation-review-response.md` - Validation results (12 findings validated, 4 rejected as outdated)
  - `review/Copilot Studio Governance Review.docx` - External review documentation

#### Enhanced

- **73 control and documentation files** updated based on Microsoft Learn validation (Jan 2026)
  - **Control 1.1** - Added agent creation limitation warning and sterile containment strategy
  - **Control 1.5** - Added 6 Copilot Studio channel connectors documentation; noted DLP enforcement now enabled by default
  - **Control 1.7** - Added automatic security scan pre-publish feature; links to Decision Log Schema, Zone 1 Explainability, Evidence Pack Assembly
  - **Control 2.1** - Expanded Managed Environment features to full 24-capability list
  - **Control 2.2** - Updated environment group rules count to 21 with source citations
  - **Control 2.7** - Links to Supply Chain Risk Register Entry template
  - **Control 2.12** - Links to Escalation Matrix and Action Authorization Matrix
  - **Control 2.15** - Added environment routing fallback warning (users route to default environment if no rule matches)
  - **Control 3.1** - Clarified two agent inventories (M365 Admin Center vs Power Platform Admin Center)
  - **Control 3.8** - Renamed from "Copilot Command Center" to "Copilot Hub and Governance Dashboard" (official Microsoft terminology); links to Real-time Compliance Dashboard and Evidence Pack Assembly
  - **Control 4.1** - Added Restricted SharePoint Search (RSS) allow-list guidance and Restricted Access Control (RAC) for ethical walls
  - Multiple list formatting, cross-linking, and Microsoft Learn citation improvements across all pillars
- **Gap Analysis Enhancements (January 2026)**
  - **Control 2.1** - Added cross-tenant inbound/outbound restrictions (capability #19); updated to 24 total Managed Environment capabilities
  - **Control 1.7** - Added granular Copilot Studio audit operations tables (25+ operation names for targeted audit searches)
  - **Control 1.4** - Added Copilot Studio DLP examples (4 scenarios: social media blocking, HTTP restrictions, knowledge sources, channel restrictions)

#### Fixed

- Repository folder structure - Eliminated nested duplication (was `FSI-AgentGov/FSI-AgentGov/`, now `FSI-AgentGov/`)
- 615 markdown list formatting issues resolved
- Broken Microsoft Learn URLs corrected across all documentation
- Control navigation and cross-reference accuracy

#### Validation & Compliance

- **Regulatory citations verified:** FINRA 2026 Report, SEC 2026 Exam Priorities, Colorado SB24-205
- **Technical feasibility assessed:** Purview audit capabilities with documented workarounds
- **Microsoft Learn validation:** All 48 controls validated against current Microsoft documentation (Jan 2026)
  - 12 corrections validated and incorporated
  - 4 outdated claims rejected
  - 12 missing governance controls identified for future consideration
- **Alignment confirmed:** All 10 operational template gaps enhance existing 48 controls with zero conflicts

#### Documentation

- CONTRIBUTING.md - Added reference to `.claude/claude.md` for Claude Code users
- Multiple control files - Enhanced with comprehensive FSI guidance and regulatory alignment
- 2,597 total insertions, 426 deletions across 73 files

---

## [Beta] — December 2025

### Initial Beta Release

**Status:** First public beta  
**Date:** December 2025  
**Validation:** Awaiting customer feedback and testing; will advance to Final Release after at least one FSI customer validation and confirmation that no major control gaps exist.

#### Added

- **48 Governance Controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **Markdown documentation** (single source of truth) with structured organization
  - Getting Started: 4 guides (overview, scope, quick-start, governance zones)
  - Reference: 48 control files + RACI, regulatory mappings, glossary, FAQ
- **Role-based Excel templates** (6 downloads)
  - Role-specific checklists (Entra, Power Platform, Purview, SharePoint, Compliance)
  - Governance maturity dashboard for tracking all 48 controls
- **Release Notes** (`CHANGELOG.md`)
- **Regulatory Mappings**
  - FINRA 4511/3110: 100% coverage (6-year retention)
  - SEC 17a-3/17a-4: 88% coverage (6-year retention)
  - SOX 302/404: 81% coverage (7-year retention)
  - GLBA 501b: 93% coverage (5-7 year retention)
  - OCC 2011-12 & Fed SR 11-7: 58% coverage (per-model retention)
- **Governance Zone Model** (Personal, Team, Enterprise)
  - Graduated controls based on agent risk and scope
  - Zone-specific implementation guidance
- **Operational Procedures**
  - Daily, weekly, monthly, quarterly operations checklist
  - 37 documented runbooks with step-by-step navigation
- **RACI Matrix**
  - Clear role definitions (AI Administrator, Power Platform Admin, Compliance Admin, Security Admin, SharePoint Admin)
  - Escalation and reporting lines
- **Exam Preparation Guides**
  - FINRA, SEC, SOX, GLBA, OCC, and Federal Reserve exam focus areas
  - Control-to-regulation mapping for auditor Q&A

#### Documentation Features

### Known Limitations (Beta)

- **Microsoft Graph Connectors**: Deep auditing for custom connector actions is still in preview by Microsoft.
- **Model Risk Management**: "Bias Testing" control relies on emerging tooling (Azure AI Content Safety) which may require custom implementation.
- **Cost Allocation**: Granular token-level cost tracking per user/department is currently an estimation based on capacity units, not exact consumption.

### Planned for Final Release

- **Automated Policy Scripts**: PowerShell scripts to apply baseline DLP policies automatically.
- **PowerBI Dashboard Template**: A `.pbix` file to visualize the inventory and compliance status.
- **Terraform/Bicep Modules**: Infrastructure-as-Code for deploying the management zones.

### Feedback

**Beta users:** Please report issues, gaps, or clarification requests via GitHub Issues. Include:
- Control ID (if applicable)
- Scenario description
- Suggested improvement

All feedback will be evaluated for inclusion in the Final Release.



---

**Note:** This framework is maintained as a living document. See README.md for review triggers and update frequency.
