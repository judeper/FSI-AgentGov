# Changelog — v1.3.x

All notable changes to the FSI Agent Governance Framework v1.3.x releases are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

**Other versions:** [Index](CHANGELOG.md) | [v1.2.x](CHANGELOG-v1.2.md) | [v1.1.x](CHANGELOG-v1.1.md) | [v1.0.x and earlier](CHANGELOG-v1.0.md)

---

## [1.3.3] — April 2026 (Learn Monitor Response — URL Redirects & Content Updates)

### Fixed

- **Learn Monitor workflow bug**: Corrected 4 regex patterns in `.github/workflows/learn-monitor.yml` that caused PR descriptions to always show "0 HIGH, 0 MEDIUM" counts. Patterns now match the actual Markdown table format used in change reports.
- **56 Microsoft Learn URL redirects**: Updated 50 Copilot URL paths (`/copilot/microsoft-365/` → `/microsoft-365/copilot/`) and 6 MCP server URLs (consolidated into planned-features page) across 28 documentation files.

### Changed

- **Control 1.9** (Data Retention and Deletion Policies): Updated sensitivity label publishing scope to include Viva Engage communities and Loop workspaces, reflecting Microsoft's expanded container support.

### Reviewed (No Action Needed)

- Processed Learn Monitor Run 81 (PR #95): 24 HIGH, 13 MEDIUM, 26 redirects, 3 errors across 229 monitored URLs. After investigation, 30 potentially affected controls were found to already be current — only 1 content update and 56 URL fixes were needed. Two CRITICAL classifications (session lifetime deprecation, activity logging deprecation) were confirmed as false positives.

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

