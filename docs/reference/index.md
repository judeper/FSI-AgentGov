---
description: "Supporting reference materials for the FSI Agent Governance Framework."
search:
  boost: 2
---
# Reference Materials

Supporting reference materials for the FSI Agent Governance Framework — 79 controls across 4 pillars, 3 governance zones.

---

## Overview

This section provides regulatory crosswalks, role quick-references, licensing guidance, architecture documentation, solution coverage analysis, and supporting reference materials for implementing and auditing the governance framework. Use the group headings below to navigate to the area most relevant to your role.

---

## Regulatory Crosswalks & Mappings

*For compliance officers, legal, and model risk functions mapping framework controls to specific regulatory obligations.*

| Document | Who it's for / when to use |
|----------|---------------------------|
| [Regulatory Mappings](regulatory-mappings.md) | **Primary cross-reference.** Maps all relevant US FSI regulations (FINRA, SEC, SOX, GLBA, OCC, Fed, CFTC, NYDFS, state AI laws) to specific controls. Use during audit prep or when a regulator asks which controls address a given rule. |
| [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) | Maps GOVERN / MAP / MEASURE / MANAGE functions to framework controls. Use when your governance committee speaks in NIST vocabulary. |
| [ISO/IEC 42001 Mapping](iso-42001-mapping.md) | AI management system standard alignment. Use for organizations pursuing ISO 42001 certification or using it as a governance baseline. |
| [OWASP LLM Top 10 Crosswalk](owasp-llm-top10-crosswalk.md) | Maps OWASP LLM-specific risks (prompt injection, model theft, etc.) to mitigating framework controls. Use during red-team and application-security reviews. |
| [Microsoft Responsible AI v2 Mapping](microsoft-rai-v2-mapping.md) | Aligns Microsoft's Responsible AI principles (v2) to framework controls. Use when answering vendor-questionnaire or board-level RAI questions. |
| [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) | **Comprehensive strategic reference.** Six Frontier Transformation Patterns × 79-control deep-dives with US FSI regulatory overlays. Use when a CAPE pattern conversation needs FSI governance grounding. |
| [Agent Essentials Control Mapping](agent-essentials-control-mapping.md) | Maps Microsoft Agent Essentials capabilities to framework controls. Use when a customer asks what Agent Essentials covers vs. what requires additional configuration. |
| [Power Platform SSPM Control Mapping](power-platform-sspm-control-mapping.md) | Maps Power Platform SaaS Security Posture Management recommendations to framework controls. Use when reviewing SSPM findings against the governance baseline. |

---

## Role & Quick-Reference Cards

*For CSAs, CCOs, examiners, and SOC analysts needing fast answers during meetings or examinations.*

| Document | Who it's for / when to use |
|----------|---------------------------|
| [Administrator Role Catalog](role-catalog.md) | Canonical admin role names, aliases, and Microsoft RBAC definitions. Use when authoring controls, playbooks, or RACI assignments to ensure consistent role naming. |
| [SOC Analyst Purview Roles](purview-soc-analyst-roles.md) | Purview role assignments scoped for SOC and security-analyst personas. Use when configuring least-privilege Purview access for non-admin analyst roles. |
| [CCO Quick Reference](cco-quick-reference.md) | **Examiner-facing.** Twelve questions an OCC, FINRA, or SEC examiner is likely to ask, each with a one-line CCO answer plus the supporting controls and playbooks. Use during exam prep or live examiner meetings. |
| [CSA Quick Reference](csa-quick-reference.md) | **Customer-meeting lookup.** Conversation openers, pattern × zone quick-map, objection reframes, and decision trees for Microsoft CSAs. Use live in a customer meeting when you need fast FSI-specific positioning. |
| [CSA Positioning Guide](csa-positioning-guide.md) | Long-form narrative companion for CSAs: 6-pattern conversation playbook, brand boundary, and complete objection-handling guide. Use when onboarding to the framework or preparing for a new customer engagement. |
| [Examiner First-Day-Letter Response](examiner-first-day-letter-response.md) | Maps common examiner document requests to specific framework artifacts and evidence packages. Use when a regulatory examination letter arrives and you need to know which framework outputs satisfy each request. |

---

## Licensing & Platform Requirements

*For administrators and procurement leads confirming license prerequisites for each control.*

| Document | Who it's for / when to use |
|----------|---------------------------|
| [License Requirements](license-requirements.md) | **Primary license reference.** Control-by-control license matrix covering all 79 controls. Includes the July 1 2026 Defender→Agent 365 transition details and GSA licensing prerequisites. Use when budgeting or validating that your SKU covers a specific control. [Download the matching role checklist →](../downloads/index.md) |
| [SharePoint Advanced Management Licensing](sharepoint-advanced-management-licensing.md) | Detailed SAM feature and licensing guide for Pillar 4 SharePoint controls. Use when scoping IAG, RCD, or Restricted SharePoint Search deployments. |
| [Agent 365 Capabilities Summary](agent-365-capabilities-summary.md) | Overview of Microsoft Agent 365 features, governance surfaces, and licensing tiers. Use when a customer asks what Agent 365 adds over the base E5/E3 stack. |
| [Windows 365 for Agents](windows-365-for-agents.md) | W365A scoping reference for agent Cloud PC execution, Intune policy hooks, audit evidence, and control touchpoints (1.7, 1.20, 1.29, 2.25). Use when evaluating Windows 365 for Agents as an execution substrate. |

---

## Architecture & Monitoring

*For administrators, architects, and monitoring engineers building or validating the framework's technical implementation.*

| Document | Who it's for / when to use |
|----------|---------------------------|
| [Monitoring Architecture](monitoring-architecture.md) | Unified monitoring system and telemetry architecture across Purview, Sentinel, PPAC, and Agent 365. Use when designing the monitoring layer for a Zone 2–3 deployment. |
| [Learn Monitor Guide](learn-monitor-guide.md) | How the documentation monitor works and how to interpret drift alerts. Use when the monitor flags a Microsoft Learn URL change that may affect framework accuracy. |
| [Learn Monitor AI Enhancement](learn-monitor-ai-enhancement.md) | AI-assisted review implementation details for monitoring Microsoft Learn changes. Use when configuring or extending the autodoc pipeline. |
| [Diagram Catalog](diagram-catalog.md) | Catalog of exportable PNG/SVG architecture diagrams. Use when building a customer presentation or an internal governance architecture review. |
| [Portal Paths Quick Reference](portal-paths-quick-reference.md) | Consolidated admin portal navigation shortcuts for all major control configuration paths. Use when following a playbook step that references a portal path. |
| [Microsoft Learn URLs](microsoft-learn-urls.md) | Curated list of official documentation links for all major governance surfaces. Use when verifying that a control implementation reference points to current documentation. |
| [FSI Configuration Examples](fsi-configuration-examples.md) | Financial services-specific sample configurations for common control scenarios. Use during a playbook walkthrough when you need concrete FSI-tuned values. |
| [Agent Audit Event Taxonomy](agent-audit-event-taxonomy.md) | Consolidated audit event reference with KQL queries for all 79 controls. Use when building Sentinel workbooks or Purview audit queries for specific control evidence. |
| [Evidence Standards](evidence-standards.md) | Documentation and retention requirements for regulatory examinations. Use when assembling an evidence package for an audit or examination. [Download the Compliance Officer Checklist →](../downloads/index.md) |

---

## Solutions & Coverage

*For AI governance leads, architects, and assessment engineers tracking solution availability and automated coverage.*

| Document | Who it's for / when to use |
|----------|---------------------------|
| [Solutions Index](solutions-index.md) | Catalog of 36 companion deployable solutions (35 live + 1 preview) mapped to the 79-control baseline. Use when a customer asks for packaged automation for a specific control. |
| [Solutions Contract](solutions-contract.md) | Inter-repository coupling contract and SemVer pinning rules between this framework and the Solutions repository. Use when coordinating a framework control change that may break Solutions CI validation. |
| [Solutions Architecture Guide](solutions-architecture-guide.md) | Architecture patterns, design principles, and integration guidelines for governance solutions. Use when designing a new companion solution or extending an existing one. |
| [Solutions Coverage Gaps](solutions-coverage-gaps.md) | Gap analysis of the 49.4% of controls currently without a live companion solution. Use when prioritizing solution development or explaining to a customer why a control is playbook-led rather than solution-packaged. |
| [Assessment Engine Coverage](assessment-coverage.md) | Per-control evaluator state (`auto_evaluable`, `manual_only`, `unimplemented_evaluator`). Use before running the assessment to set honest expectations about which controls will self-score vs. require manual responses. |
| [Frontier Readiness Coverage](frontier-assessment-coverage.md) | Honest 0% auto-evaluator coverage report for the Frontier Readiness diagnostic (facilitator-answered). Use when a customer asks how automated the Frontier assessment is. |
| [CAPE Pattern Coverage](pattern-coverage.md) | Generated 79×6 control-to-pattern matrix. Use when mapping a specific control to the CAPE pattern(s) it supports, or when building a pattern-specific control shortlist for a customer. |
| [Known Limitations](known-limitations.md) | Documented framework constraints and workaround guidance. Use before a customer meeting or examination when you want to proactively name what the framework does not cover. |
| [Versioning and Support](versioning-and-support.md) | SemVer policy, breaking-change definitions, and support windows for framework releases. Use when evaluating whether a control change in a framework PR requires a major, minor, or patch version bump. |

---

## Glossary, FAQ & Disclaimer

*For anyone needing term definitions, common implementation questions, or supplementary governance context.*

| Document | Who it's for / when to use |
|----------|---------------------------|
| [Glossary](glossary.md) | 70+ terms and regulatory acronyms used across the framework. Use when a document uses an abbreviation (ALIM, CAPE, CCO, CDAO, CoE, etc.) you need to look up. |
| [FAQ](faq.md) | Frequently asked questions organized by audience and topic. Use as the first stop when a question about zone classification, implementation timing, or regulatory scope doesn't have an obvious doc to cite. |
| [Work IQ Governance Reference](work-iq-governance.md) | Governance considerations for Work IQ MCP tools, business skills, admin consent, data boundaries, and audit evidence. Use when Work IQ surfaces are being evaluated for Zone 2–3 use. |
| [Compliance Manager Templates](compliance-manager-templates.md) | Microsoft Compliance Manager assessment templates aligned to framework controls. Use when a customer wants Compliance Manager scores alongside the framework assessment. |
| [Service Trust Portal Attestation Guide](service-trust-portal-attestation-guide.md) | Guide to using Microsoft STP audit reports (SOC 2, ISO 27001, etc.) as supporting evidence for framework controls. Use when assembling evidence that Microsoft's platform-level controls satisfy examiner requests. |

---

## Downloads & Templates

*Role-based Excel checklists for tracking implementation progress against all 79 controls.*

| Download | Target Role | File |
|----------|-------------|------|
| [Downloads & Templates](../downloads/index.md) | All roles | Role-specific Excel checklists (XLSX, ~6 KB each) for Entra Global Admin, Power Platform Admin, Purview Compliance Admin, SharePoint Admin, Compliance Officer, and AI Governance Lead. |

---

## Quick Links

**For Compliance Officers and CCOs:**

- [CCO Quick Reference](cco-quick-reference.md) — Examiner questions with one-line answers
- [Examiner First-Day-Letter Response](examiner-first-day-letter-response.md) — Map examiner requests to framework artifacts
- [Regulatory Mappings](regulatory-mappings.md) — Control-to-regulation traceability
- [Evidence Standards](evidence-standards.md) — What to document for examinations
- [Download the Compliance Officer Checklist →](../downloads/index.md)

**For CSAs and Account Teams:**

- [CSA Quick Reference](csa-quick-reference.md) — Live meeting reference card
- [CSA Positioning Guide](csa-positioning-guide.md) — Full onboarding and objection guide
- [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) — Pattern × control deep-dives

**For Platform Administrators:**

- [Portal Paths Quick Reference](portal-paths-quick-reference.md) — Navigation shortcuts
- [License Requirements](license-requirements.md) — What licenses are needed
- [Role Catalog](role-catalog.md) — Admin role assignments
- [Download the matching role checklist →](../downloads/index.md)

**For AI Governance Leads:**

- [Solutions Index](solutions-index.md) — Available companion solutions
- [Assessment Engine Coverage](assessment-coverage.md) — What auto-scores vs. what needs manual input
- [Known Limitations](known-limitations.md) — Framework constraints to communicate proactively

---

## Related Sections

- [Framework](../framework/index.md) — Governance principles and structure
- [Control Catalog](../controls/index.md) — All 79 control requirements
- [Playbooks](../playbooks/index.md) — Step-by-step implementation procedures

---

*Updated: June 2026 | Version: v1.6.2 | UI Verification Status: Current*
