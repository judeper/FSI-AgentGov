# Changelog

All notable changes to the FSI Agent Governance Framework are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

---

## [1.0] — January 2026

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
  - **Control 2.1** - Expanded Managed Environment features to full 23-capability list
  - **Control 2.2** - Updated environment group rules count to 21 with source citations
  - **Control 2.7** - Links to Supply Chain Risk Register Entry template
  - **Control 2.12** - Links to Escalation Matrix and Action Authorization Matrix
  - **Control 2.15** - Added environment routing fallback warning (users route to default environment if no rule matches)
  - **Control 3.1** - Clarified two agent inventories (M365 Admin Center vs Power Platform Admin Center)
  - **Control 3.8** - Renamed from "Copilot Command Center" to "Copilot Hub and Governance Dashboard" (official Microsoft terminology); links to Real-time Compliance Dashboard and Evidence Pack Assembly
  - **Control 4.1** - Added Restricted SharePoint Search (RSS) allow-list guidance and Restricted Access Control (RAC) for ethical walls
  - Multiple list formatting, cross-linking, and Microsoft Learn citation improvements across all pillars

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
