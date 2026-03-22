# Changelog — v1.3.x

All notable changes to the FSI Agent Governance Framework v1.3.x releases are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

**Other versions:** [Index](CHANGELOG.md) | [v1.2.x](CHANGELOG-v1.2.md) | [v1.1.x](CHANGELOG-v1.1.md) | [v1.0.x and earlier](CHANGELOG-v1.0.md)

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

### Changed

- **Framework total:** 72 → 78 controls
- **Pillar totals:** Security 29, Management 26, Reporting 14, SharePoint 9
- **Per-control playbooks:** 288 → 312
- **Catalog navigation and index surfaces:** updated `mkdocs.yml`, `CONTROL-INDEX.md`, pillar landing pages, control catalog pages, and playbook indexes for the expanded control set
- **Existing controls updated with Agent 365 / Entra Agent ID content:**
  - `1.2` — Agent type taxonomy, shadow agent terminology, and registry export guidance
  - `1.7` — Agent sign-in logging, correlation fields, and `MicrosoftServicePrincipalSignInLogs`
  - `1.11` — Agent-specific Conditional Access and Identity Protection guidance
  - `2.24` — Researcher and Analyst governance exception guidance
  - `3.6` — Ownerless Agents governance card workflow and updated shadow agent terminology
- **Assessment and export tooling:** updated script baselines, control ranges, and template expectations for the 78-control catalog

