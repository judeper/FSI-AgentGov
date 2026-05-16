# Changelog — v1.3.x

All notable changes to the FSI Agent Governance Framework v1.3.x releases are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

**Other versions:** [Index](CHANGELOG.md) | v1.2.x and earlier — archived (see git history prior to April 2026)

---

## [1.3.5] — April 2026 (Opus 4.7 Council Catalog Completion)

### Changed

- **52 controls fully uplifted** by autonomous AI Council (Claude Opus 4.7) covering control documentation **and** all 4 implementation playbooks each (208 playbooks total). Each council:
  - Researched current Microsoft Learn documentation (April 2026)
  - Mapped to FSI regulations: FINRA 4511 / 3110 / 25-07 / 4530 / 8210, SEC 17a-3 / 17a-4 (incl. May 2023 amendments) / Reg S-P / Reg BI, SOX 302 / 404, GLBA Safeguards Rule (16 CFR §314), OCC 2011-12 / 2013-29 / 2020-10 / Heightened Standards (12 CFR 30 App. D), Fed SR 11-7 / SR 23-04, NIST SP 800-53 (AC-5, AC-6, IA-2, SC-28), NIST AI RMF 1.0, NIST CSF 2.0, NYDFS 23 NYCRR 500 (incl. §500.12, §500.15), CFTC 1.31, Interagency Third-Party Guidance, FFIEC BCM Handbook, MSRB G-23 / G-37, OWASP LLM Top 10 2025
  - Tightened regulatory headers with precise sub-section citations
  - Strengthened Zone 1 / Zone 2 / Zone 3 requirements with cumulative thresholds, cadence, and licensing prerequisites
  - Updated portal paths and `Last UI Verified` to April 2026
  - Replaced thin role lists with canonical names from `docs/reference/role-catalog.md` (added AI Administrator, Model Risk Manager, Entra Identity Governance Admin where appropriate)
  - Expanded Verification Criteria to evidence-driven, examiner-mappable checks
  - Refreshed Microsoft Learn Additional Resources with current URLs
- **All 4 playbooks per control rewritten gold-standard:**
  - `portal-walkthrough.md` — zone-aware numbered steps with April 2026 admin-center paths and per-zone configuration matrix
  - `powershell-setup.md` — idempotent scripts using `[CmdletBinding(SupportsShouldProcess)]`, pinned module versions, sovereign-cloud (GCC / GCC High / DoD) connection blocks, SHA-256 evidence-manifest emission, and validation exit codes
  - `verification-testing.md` — numbered test cases (TC-`<id>`-NN) with PASS / FAIL criteria, KQL detections, evidence checklist, signed attestation template with independence note (FINRA 3110)
  - `troubleshooting.md` — symptom matrix, H2 issue / H3 symptom-cause-fix structure, 4–6 tier escalation, known-limitations table

### Controls Reviewed in This Wave

- **Pillar 1 (Security):** 1.22 Information Barriers, 1.23 Step-Up Authentication, 1.24 Defender AI-SPM, 1.25 MIME Type Restrictions, 1.26 File Upload & Analysis, 1.27 Content Moderation, 1.28 Policy-Based Publishing, 1.29 Global Secure Access (plus stray uplifts to 1.1, 1.5, 1.15)
- **Pillar 2 (Management):** 2.3 Change Management, 2.4 BCDR, 2.7 Vendor & Third-Party Risk, 2.8 Access Control & SoD, 2.9 Performance Monitoring, 2.10 Patch Management, 2.11 Bias Testing, 2.13 Documentation & Records, 2.14 Training & Awareness, 2.15 Environment Routing, 2.16 RAG Source Integrity, 2.17 Multi-Agent Orchestration, 2.18 Conflict-of-Interest Testing, 2.19 Customer AI Disclosure, 2.20 Adversarial / Red-Team, 2.21 AI Marketing Claims, 2.22 Inactivity Timeout, 2.23 User Consent
- **Pillar 3 (Reporting):** 3.3 Compliance Reporting, 3.5 Cost Allocation, 3.7 PPAC Posture, 3.8 Copilot Hub, 3.10 Hallucination Feedback, 3.11 Inventory Enforcement, 3.12 Exception & Override, 3.13 Agent 365 Analytics, 3.14 Agent 365 Observability SDK
- **Pillar 4 (SharePoint):** 4.3 Site & Document Retention, 4.4 Guest & External Access, 4.5 Security & Compliance Monitoring, 4.8 Item-Level Permission Scanning, 4.9 Embedded File Content Governance

### Notable FSI Findings Surfaced (Recommended Follow-Up)

- **Customer Key revocation is irreversible** (Control 1.15) — data-loss risk; GCC High has limited Customer Key surface
- **Preservation Lock alone does NOT satisfy SEC 17 CFR 240.17a-4(f)** (Control 1.9) — D3P (designated third-party) letter required; Microsoft does not act as D3P
- **Channel Agent IB inheritance gap** (Control 1.22) — documented residual risk; Z3 prohibition reaffirmed
- **PIM-for-Groups requires Entra ID P2** (Control 1.18) — not in E5 baseline
- **`Get/Set-AdminPowerAppEnvironmentRoleAssignment` does NOT work on Dataverse-backed environments** (Control 1.18) — affects all Copilot Studio environments
- **Native PPAC retention is 28 days** (Control 3.2) — not the FINRA 6-year requirement; export pipeline mandatory
- **`Search-UnifiedAuditLog` deprecated** (Control 3.2) — migrate to Graph `/security/auditLog/queries`
- **Service principals bypass PIM and Access Reviews entirely** (Control 2.8) — compensating controls required
- **Anthropic / OpenAI native integration in Copilot Studio reclassifies the vendor relationship** (Control 2.7) — firms with direct contracts must decommission to avoid duplicative clauses
- **AI-SPM coverage is partially traffic-driven** (Control 1.24) — newly published agents may not appear until first inference; cross-reference PPAC inventory
- **NIST SP 800-53 IA-2** added to Step-Up Authentication (Control 1.23) regulatory header
- **MSRB G-23 / G-37** added to Information Barriers (Control 1.22) for muni-underwriting / pay-to-play obligations

### Methodology

Autonomous Claude Opus 4.7 council with **no-commit protocol**: each agent wrote files only; orchestrator committed serially after each report to eliminate the parallel-git race conditions seen in earlier waves. 4 dispatch waves, 23 parallel agents at peak, 56 commits.

### Footer Convention

Council agents were instructed to set the per-control footer to `*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*`. The version label reflects the framework baseline at agent dispatch time. Subsequent council passes may revise individual control footers; the source of truth for framework version is this changelog.

---

## [1.3.4] — April 2026 (Autonomous Dual-Model Council Review)

### Changed

- **All 78 controls**: Added FINRA Regulatory Notice 25-07 (April 2025) to regulatory reference headers — the most significant 2025 AI-specific FINRA guidance was missing from every control
- **All 128 playbooks**: Synchronized version footers from v1.2 to v1.3 across all four playbook types (portal-walkthrough, powershell-setup, verification-testing, troubleshooting)
- **Pillar 1 controls (deep review)**: Applied targeted fixes from dual-model council review (GPT-5.4 + Claude Opus 4.6) covering accuracy, currency, regulatory alignment, and Copilot Studio alignment

### Fixed

- **Control 1.4** (Advanced Connector Policies): Corrected two critical factual errors — per-environment ACP IS available (was claimed unavailable); MCP tool-level DLP NOT available in ACP (was claimed it was, only server-level blocking is supported)
- **Control 1.7** (Audit Logging): Fixed broken SEC 17a-4 URL (HTTP 403) — replaced with 2022 amendments URL
- **Control 1.7** (Audit Logging): Fixed FINRA 25-07 abbreviation from "RFI" to "RFC" (Request for Comment) and corrected scope characterization
- **Control 1.9** (Data Retention): Fixed Copilot Studio location classification — moved from "Enterprise AI Apps" to correct "Microsoft Copilot experiences" location
- **Control 1.12** (Insider Risk): Added Adaptive Protection (GA feature that was completely missing from the control)
- **Control 1.21** (Adversarial Input Logging): Replaced retired FFIEC CAT (sunset August 2025) with NIST CSF 2.0 DE.CM/DE.AE
- **Control 1.22** (Information Barriers): Fixed SEC Regulation SHO misattribution — SHO governs short-selling, not information barriers. Replaced with SEC Exchange Act §15(g) (the actual MNPI-barrier statute)
- **Control 1.1** (Restrict Publishing): Fixed authentication timing language ("Always" vs "As Needed" not current Learn terminology), sharing path (Channels > Share Settings → … > Share), GenAI publishing label, and audit event name (Published bot → BotUpdateOperation-BotPublish)
- **Control 1.2** (Agent Registry): Updated Agent 365 from Preview to GA (May 2026); fixed shadow agent definition, Researcher/Analyst governance exception wording
- **Control 1.3** (SharePoint Governance): Distinguished M365 Copilot vs Copilot Studio governance surfaces; fixed RAC/RCD/IAG terminology conflation
- **Control 1.5** (DLP): Updated DLP for Copilot Prompts status; fixed Block Labeled Files behavior description; removed stale MCP timeline claims
- **Control 1.6** (DSPM for AI): Fixed unified DSPM GA timeline (June → May 2026); corrected AI Administrator role to view-only; added e-discovery and examination readiness guidance
- **Control 1.8** (Runtime Protection): Fixed Defender integration from "GA February 2026" to "Preview — verify GA status"
- **Control 1.15** (Encryption): Fixed SEC 17a-4 WORM/encryption conflation; added NYDFS 23 NYCRR 500.15

### Added

- **Regulatory coverage**: SEC Reg S-P 2024 amendments, NIST SP 800-53 control mappings, OCC 2023-17 (Interagency Third-Party Guidance), NIST AI RMF references, CFTC 1.31, Fed SR 11-7, NYDFS 23 NYCRR 500 citations added to relevant controls
- **Control 1.1**: Added Copilot Studio data policies subsection, data residency verification subsection
- **Control 1.4**: Added ACP-only mode guidance, virtual connector transition awareness, custom connector limitation callout
- **Control 1.7**: Added CFTC 1.31 regulatory bullet for dual-registered firms
- **Control 1.10**: Added Copilot interactions policy template reference, Policy Match Preservation setting (7 years for Zone 3)
- **Control 1.11**: Added Windows Hello for Business to phishing-resistant MFA methods
- **Control 1.19**: Added FINRA 8210 and FRCP 37(e) for litigation readiness
- **Control 1.24**: Replaced retired FFIEC CAT with NIST AI RMF reference

### Review Methodology

Autonomous dual-model council review using GPT-5.4 (Security & Compliance Architect) and Claude Opus 4.6 (FSI Regulatory Specialist). Each model independently reviewed all 78 controls against current Microsoft Learn documentation and financial services regulatory requirements. Results: 184 council agreements, 0 disagreements, 0 researcher invocations needed, 5 broken URLs found.

---

## [1.3.3] — April 2026 (Learn Monitor Response — URL Redirects & Content Updates)

### Fixed

- **Learn Monitor workflow bug**: Corrected 4 regex patterns in `.github/workflows/learn-monitor.yml` that caused PR descriptions to always show "0 HIGH, 0 MEDIUM" counts. Patterns now match the actual Markdown table format used in change reports.
- **56 Microsoft Learn URL redirects**: Updated 50 Copilot URL paths (`/copilot/microsoft-365/` → `/microsoft-365/copilot/`) and 6 MCP server URLs (consolidated into planned-features page) across 28 documentation files.

### Changed

- **Control 1.9** (Data Retention and Deletion Policies): Updated sensitivity label publishing scope to include Viva Engage communities and Loop workspaces, reflecting Microsoft's expanded container support.
- **Control 1.12** (Insider Risk Detection and Response): Added Content Preview (Preview) as an Activity Explorer triage capability for SharePoint, Exchange, and OneDrive files during alert investigation.
- **Control 1.17** (Endpoint DLP): Added new Microsoft Learn URLs for restructured just-in-time (JIT) protection documentation (conceptual and deployment articles).
- **Control 1.5** (DLP and Sensitivity Labels): Clarified DLP-for-Copilot prompt licensing — available to all M365 Copilot/Copilot Chat users at no additional cost (any SKU).
- **License requirements**: Added note that DLP for Copilot prompts is available across all SKUs, while DLP to restrict Copilot from processing files/emails still requires E5/Purview Suite.

### Reviewed (No Action Needed)

- Processed Learn Monitor Run 81 (PR #95): 24 HIGH, 13 MEDIUM, 26 redirects, 3 errors across 229 monitored URLs. After investigation, 30 potentially affected controls were found to already be current — only 1 content update and 56 URL fixes were needed. Two CRITICAL classifications (session lifetime deprecation, activity logging deprecation) were confirmed as false positives.
- Processed Learn Monitor Run 82 (PR #96): 4 HIGH, 3 MEDIUM, 14 redirects, 3 errors across 229 monitored URLs. 3 HIGH items required documentation updates (Controls 1.12, 1.17, 1.5); 1 HIGH (What's New) was informational only.

---

## [1.3.2] — March 2026 (Agent 365 GA Update + Learn Monitor Baseline)

### Changed

- **Agent 365 GA update**: Updated all Agent 365 references from "Frontier preview" to reflect general availability on May 1, 2026 with per-user licensing (Agent 365 or Microsoft 365 E7). Updated governance-fundamentals.md, Controls 2.25, 2.26, 2.12, 3.6, 3.8, 3.11, 3.13, 3.14, and all reference docs (glossary, license-requirements, FAQ, agent-365-capabilities-summary, agent-essentials-control-mapping, microsoft-learn-urls, agent-identity-architecture, zones-and-tiers). Playbook files retain historically accurate "Frontier preview" verification context with GA timeline notes.

### Added

- **MCP Server Governance playbook**: New advanced implementation playbook covering Model Context Protocol (MCP) governance for FSI — DLP connector policy scoping, authentication governance (OAuth 2.0 / API key), FSI-specific risks for regulated data sources, VNet integration, and audit requirements.
- **Agent evaluations enhancement**: Expanded Controls 2.5 and 2.18 with set-level grading frameworks, multi-dimensional graders, Purview audit integration, import/export test sets, and SR 11-7 model validation mapping.
- **2026 Wave 1 feature tracking**: Added new Microsoft Learn URLs to watchlist for Enhanced Admin Controls, Agentic Center of Enablement, Safe Sharing enhancements, and Custom MCP Servers.
- **Architecting Agent Solutions guidance**: Cross-referenced Microsoft's January 2026 guidance hub covering ALM strategy, multi-agent orchestration patterns, and responsible AI into relevant framework controls.

### Fixed

- **Learn Monitor baseline reset**: Squash-merged PR #87 (cumulative state from 18 monitoring runs); closed 17 superseded PRs (#70-#86). Processed 34 HIGH and 24 MEDIUM priority Microsoft Learn content changes affecting 30+ controls. Updated 25 URL redirects.

---

## [1.3.1] — March 2026 (PII Remediation)

### Fixed

- **Email address PII remediation**: Replaced all `@company.com` and `@firm.com` email addresses with RFC 2606 reserved `@example.com` domain across both repositories. Addressed 26 occurrences in 12 FSI-AgentGov documentation files and 5 occurrences in 4 FSI-AgentGov-Solutions files. Removed person-name email pattern (`john.smith@company.com` → `j.reviewer@example.com`). No actual customer PII was found — all addresses were example placeholders using real registered domains (`company.com`, `firm.com`) that could be confused with real organizational emails.

---

## [1.3.0] — March 2026 (Agent 365 Catalog Expansion)

### Added

- **Six new controls** covering Agent 365 governance, Entra Agent ID lifecycle controls, analytics, observability, Global Secure Access network controls, and embedded file governance:
  - `1.29` — Global Secure Access: Network Controls for Copilot Studio Agents
  - `2.25` — Microsoft Agent 365: Admin Center Governance Console
  - `2.26` — Entra Agent ID: Identity Governance for Agents
  - `3.13` — Agent 365 Admin Center Analytics and Reporting
  - `3.14` — Agent 365 Observability SDK and Custom Agent Telemetry
  - `4.9` — Embedded File Content Governance
- **24 implementation playbooks** for the six new controls (`portal-walkthrough`, `powershell-setup`, `verification-testing`, and `troubleshooting` for each control)
- **Screenshot expectation files** for the new controls under `docs/images/1.29/`, `2.25/`, `2.26/`, `3.13/`, `3.14/`, and `4.9/`
- **Release metadata stream** for `v1.3.x`
- **Validated March 2026 preview governance guidance** for safe-sharing / credential-oversharing controls and human-in-the-loop supervisory workflows:
  - Controls `1.18`, `2.3`, `2.8`, and `3.8` now document preview safe-sharing / credential-oversharing signals, approval checkpoints, and production-use caveats
  - Control `2.12` now documents request/response-based human-in-the-loop workflows, checkpoint persistence, and pending-request evidence handling for supervisory review patterns

### Changed

- **Framework total:** 72 → 78 controls
- **Pillar totals:** Security 29, Management 26, Reporting 14, SharePoint 9
- **Per-control playbooks:** 288 → 312
- **Catalog navigation and index surfaces:** updated `mkdocs.yml`, `CONTROL-INDEX.md`, pillar landing pages, control catalog pages, and playbook indexes for the expanded control set
- **Companion catalog reconciliation:** README and `docs/reference/solutions-index.md` align to 33 live companion solutions, document 2 documentation-only preview placeholders separately, and preserve the validated 78-control baseline; framework-native assets remain documented in FSI-AgentGov and are not counted as live companion solutions
- **Companion reporting references:** Compliance Dashboard references now align to the validated framework control catalog instead of older reduced-control descriptions
- **Agent 365 governance boundaries:** clarified when native Agent 365 Admin Center registry, pending-request, ownerless-agent, and overview analytics surfaces apply versus when companion solution automation should be used
- **Terminology cleanup:** active March 2026 guidance now uses Microsoft Entra naming where current Microsoft product language replaces Azure AD terminology
- **Existing controls updated with Agent 365 / Entra Agent ID / preview governance content:**
  - `1.2` — Agent type taxonomy, shadow agent terminology, registry export guidance, and inventory boundary notes
  - `1.7` — Agent sign-in logging, correlation fields, and `MicrosoftServicePrincipalSignInLogs`
  - `1.11` — Agent-specific Conditional Access and Identity Protection guidance
  - `1.18` — Safe-sharing / credential-oversharing preview guidance and Entra role-review checkpoints
  - `2.3` — Safe-sharing / credential-oversharing approval gating and publish/share workflow guidance
  - `2.8` — Maker/checker review expectations for safe-sharing / credential-oversharing signals
  - `2.12` — Human-in-the-loop request/response supervision guidance with checkpoint and pending-request handling
  - `2.24` — Researcher and Analyst governance exception guidance
  - `3.6` — Ownerless Agents governance card workflow and updated shadow agent terminology
  - `3.8` — Agent overview reporting surfaces, safe-sharing preview visibility, and admin-center operational queues
- **Assessment and export tooling:** updated script baselines, control ranges, and template expectations for the 78-control catalog

