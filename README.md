# FSI Agent Governance Framework v1.2

[![Publish Docs](https://github.com/judeper/FSI-AgentGov/actions/workflows/publish_docs.yml/badge.svg)](https://github.com/judeper/FSI-AgentGov/actions/workflows/publish_docs.yml)
[![Link Validation](https://github.com/judeper/FSI-AgentGov/actions/workflows/link-check.yml/badge.svg)](https://github.com/judeper/FSI-AgentGov/actions/workflows/link-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Repo stars](https://img.shields.io/github/stars/judeper/FSI-AgentGov?style=social)](https://github.com/judeper/FSI-AgentGov/stargazers)

**Governance framework for Microsoft 365 AI agents in US financial services.**

> **New to this framework? [Start Here](docs/start-here.md)** — understand what FSI-AgentGov covers, why it exists, and where to begin.

> ⚠️ **Scope:** This framework is designed exclusively for **US financial institutions** using **Microsoft 365 AI agents** (Copilot Studio, Agent Builder). Non-US regulations (EU AI Act, GDPR, DORA) and non-M365 AI platforms are out of scope.

> **Important:** This framework is provided for informational purposes only and does not constitute legal, regulatory, or compliance advice. See [Disclaimer](docs/disclaimer.md) for full details.

## Why This Repository Exists

Financial institutions can build and publish agents faster than they can consistently govern who may create them, what data and connectors they can access, how they move from experimentation to production, and what evidence must be retained for risk and compliance review. Microsoft product documentation explains how to create agents; FSI-AgentGov explains how to govern them in a regulated operating model.

This repository helps teams:

- classify agents into governance zones before rollout
- identify the foundational controls needed before broader adoption
- implement technical and procedural controls with step-by-step playbooks
- support risk, compliance, and operational review with a common reference point

**Version:** 1.2.53 (March 2026)
**Primary Audience:** AI governance leads, Power Platform Admins, compliance teams, security architects, internal audit, and business sponsors in US financial services
**Regulatory Focus:** FINRA, SEC, SOX, GLBA, OCC, Federal Reserve, FDIC, NCUA

## Who Should Use This Repository

Use this repository if you are:

- deploying or reviewing **Copilot Studio**, **Agent Builder**, or related Microsoft 365 AI agents
- responsible for **managed environments, connector governance, lifecycle controls, or approval workflows**
- preparing a more defensible governance approach for **regulated agent deployments** in financial services

This is not the right starting point if you are:

- governing **Microsoft 365 Copilot** in Word, Excel, PowerPoint, Outlook, Teams, Copilot Chat, or Copilot Pages — use **[FSI-CopilotGov](https://github.com/judeper/FSI-CopilotGov)**
- looking for **end-user prompting tips** or general user adoption guidance
- working outside **regulated US financial services**

## Relationship to FSI-CopilotGov

FSI-AgentGov and FSI-CopilotGov are complementary:

- **FSI-AgentGov** focuses on agent creation, publishing, environments, connectors, lifecycle, and agent-specific governance controls.
- **FSI-CopilotGov** focuses on Microsoft 365 Copilot experiences embedded across M365 applications.
- **If your program includes both**, use both repositories. See [Relationship to FSI-CopilotGov](docs/framework/relationship-to-copilotgov.md) for scope boundaries and routing guidance.

To stay current: **Star** this repository, use **Watch → Releases** for low-noise update notifications, and **share with your compliance team** as part of your review.

---

## 🎯 Framework Structure

### Four Governance Pillars

| Pillar | Controls | Focus | Examples |
|--------|----------|-------|----------|
| **1. Security** | 28 | Protect data and systems | DLP, Audit, Encryption, MFA, eDiscovery, Network Isolation, Information Barriers, Content Moderation, Publishing Restrictions |
| **2. Management** | 24 | Govern lifecycle and risk | Change Control, Testing, Model Risk, Multi-Agent Orchestration, HITL Framework, Inactivity Timeout, Feature Governance |
| **3. Reporting** | 12 | Monitor and track | Inventory, Usage, Incidents, PPAC, Sentinel, Hallucination Feedback, Exception Management |
| **4. SharePoint Mgmt** | 7 | SharePoint-specific controls | Access, Retention, External Sharing, Grounding Scope, Copilot Data Governance |

**Total: 71 Comprehensive Controls**

### Three Governance Zones

| Zone | Level | Risk | Data Access | Approval |
|------|-------|------|-------------|----------|
| **Zone 1: Personal** | Low | Individual development | M365 Graph only | Self-service |
| **Zone 2: Team** | Medium | Departmental agents | Internal data | Manager approval |
| **Zone 3: Enterprise** | High | Production/customer-facing | Regulated data | Governance committee |

```mermaid
graph LR
    subgraph "Zone 1: Personal"
        Z1[Individual Use]
    end
    subgraph "Zone 2: Team"
        Z2[Departmental Use]
    end
    subgraph "Zone 3: Enterprise"
        Z3[Production Use]
    end
    Z1 -->|Promote| Z2
    Z2 -->|Promote| Z3
    Z3 -.->|Demote| Z2
    Z2 -.->|Demote| Z1

    style Z1 fill:#66BB6A,color:#fff
    style Z2 fill:#FFA726,color:#fff
    style Z3 fill:#EF5350,color:#fff
```

---

## 📁 What's Included

### Framework Documents (12 Files)
Strategic governance principles in `docs/framework/`:
- Executive summary and adoption roadmap
- Governance zones and tiers
- Agent lifecycle management
- Operating model and regulatory framework
- Agent identity architecture and solutions integration

### Control Files (71 Total)
Technical specifications in `docs/controls/`:
- **Pillar 1:** 28 Security Controls (1.1-1.28)
- **Pillar 2:** 24 Management Controls (2.1-2.24)
- **Pillar 3:** 12 Reporting Controls (3.1-3.12)
- **Pillar 4:** 7 SharePoint Controls (4.1-4.7)

Each control includes:
- Overview and regulatory reference
- 3 governance levels (Baseline, Recommended, Regulated)
- Zone-specific requirements
- Verification and testing procedures

### Implementation Playbooks (284 Files)
Step-by-step procedures in `docs/playbooks/control-implementations/`:
- **4 playbooks per control** (71 controls × 4 = 284 playbooks)
- Portal walkthrough guides with click-by-click navigation
- PowerShell automation scripts with validation
- Verification testing procedures with evidence checklists
- Troubleshooting guides with common issues and resolutions

### Documentation Files
- **README.md** - This file (overview)
- **Start-Here.md** - [New user orientation](docs/start-here.md)
- **Relationship-to-CopilotGov.md** - [Scope boundary with the companion framework](docs/framework/relationship-to-copilotgov.md)
- **Zones-Overview.md** - [Detailed governance zones](docs/framework/zones-and-tiers.md)
- **Regulatory-Mappings.md** - [Regulation-to-control mapping](docs/reference/regulatory-mappings.md)
- **Quick-Start-Guide.md** - [How to use the framework](docs/getting-started/quick-start.md)
- **Glossary.md** - [Key terms and definitions](docs/reference/glossary.md)
- **RACI-Matrix.md** - [Roles and responsibilities](docs/reference/raci-matrix.md)
- **Implementation-Checklist.md** - [Implementation roadmap](docs/getting-started/checklist.md)
- **FAQ.md** - [Frequently asked questions](docs/reference/faq.md)

### Companion Solutions (27 Automation Packages)
Deployable Power Platform solutions in the **[FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions)** repository:
- 20 completed, 3 validated, 4 in progress
- Covers security, management, reporting, and cross-cutting automation
- See [Solutions Index](docs/reference/solutions-index.md) for full catalog

### Supporting Files
- **CONTROL-INDEX.md** - [Master index of all controls](docs/controls/CONTROL-INDEX.md)
- **Administrator Excel Templates** - Role-specific checklists and dashboards (see [Downloads](docs/downloads/index.md))
- **Offline Deliverables** - This repository ships **web docs + Excel templates only** (no Word/PDF document bundle)

---

## 🚀 Quick Start

### For First-Time Users
1. Read **[Start Here](docs/start-here.md)** to understand why the framework exists and when to use it
2. Review **[Zones Overview](docs/framework/zones-and-tiers.md)** to classify your agents
3. Use the **[Quick Start Guide](docs/getting-started/quick-start.md)** for the initial implementation path
4. If needed, compare scope with **[FSI-CopilotGov](docs/framework/relationship-to-copilotgov.md)**

### For Implementation
1. Use **[Implementation Checklist](docs/getting-started/checklist.md)** for step-by-step guidance
2. Reference individual control files for detailed procedures
3. Document evidence in your compliance system
4. Schedule quarterly reviews

### For Governance
1. Use **[RACI Matrix](docs/reference/raci-matrix.md)** to assign roles and responsibilities
2. Establish governance committee per **[Zones Overview](docs/framework/zones-and-tiers.md)**
3. Schedule recurring compliance reviews
4. Track incidents and remediation

---

## 📚 Three-Layer Documentation Architecture

The framework uses a three-layer documentation model designed to serve different audiences and use cases:

### Layer 1: Framework (`docs/framework/`)
**Purpose:** Strategic governance principles and organizational context
**Audience:** Executives, compliance officers, governance leads

12 comprehensive documents covering:
- Executive summary for leadership buy-in
- Governance zone definitions (Zone 1/2/3)
- 30/60/90-day adoption roadmap
- Agent lifecycle management process
- Operating model with RACI
- Regulatory framework landscape

**Start here:** [Framework Overview](docs/framework/index.md)

### Layer 2: Controls (`docs/controls/`)
**Purpose:** Technical control specifications
**Audience:** Administrators, engineers, security teams

71 detailed controls organized by pillar:
- **Pillar 1 - Security:** 28 controls (1.1-1.28)
- **Pillar 2 - Management:** 24 controls (2.1-2.24)
- **Pillar 3 - Reporting:** 12 controls (3.1-3.12)
- **Pillar 4 - SharePoint:** 7 controls (4.1-4.7)

Each control follows a 10-section format including objective, regulatory alignment, configuration points, zone-specific requirements, and verification criteria.

**Start here:** [Control Index](docs/controls/CONTROL-INDEX.md)

### Layer 3: Playbooks (`docs/playbooks/`)
**Purpose:** Step-by-step implementation procedures
**Audience:** Hands-on implementers, auditors

284 implementation playbooks (4 per control):
1. **Portal Walkthrough** - Click-by-click configuration in admin portals
2. **PowerShell Setup** - Automation scripts with validation
3. **Verification Testing** - Test cases, evidence collection, attestation templates
4. **Troubleshooting** - Common issues, resolutions, escalation paths

**Start here:** [Playbooks Overview](docs/playbooks/control-implementations/index.md)

```mermaid
graph TD
    A[Layer 1: Framework] -->|Defines principles| B[Layer 2: Controls]
    B -->|Specifies requirements| C[Layer 3: Playbooks]
    C -->|Provides evidence| B
    B -->|Validates strategy| A

    style A fill:#66BB6A,color:#fff
    style B fill:#FFA726,color:#fff
    style C fill:#42A5F5,color:#fff
```

---

## 🔗 Companion Solutions

The **[FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions)** repository provides ready-to-deploy Power Platform automation that operationalizes framework controls. Each solution includes Power Automate flows, Dataverse components, and configuration guidance.

**27 solutions** (20 completed, 3 validated, 4 in progress) covering 34 controls across all four pillars.

| Category | Solutions | Controls Addressed |
|----------|-----------|-------------------|
| **Security Automation** | Audit Compliance Manager, Session Security Configurator, Conditional Access Automation, Scope Drift Monitor, Content Moderation Monitor, File Upload Security, MIME Type Restrictions, Configuration Hardening Baseline | 1.1, 1.4, 1.5, 1.7, 1.8, 1.11, 1.14, 1.18, 1.23, 1.25, 1.27 |
| **Management Automation** | Environment Lifecycle Management, Message Center Monitor, Pipeline Governance Cleanup, Segregation of Duties Detector, Inactivity Timeout Enforcement | 2.1, 2.2, 2.3, 2.8, 2.10, 2.22 |
| **Reporting & Monitoring** | Compliance Dashboard, Agent Access Governance Monitor, Deny Event Correlation, Agent Usage & Performance Workbook, Unrestricted Agent Sharing Detector, FINRA Supervision Workflow | 3.1, 3.2, 3.3, 3.4, 3.7, 3.8, 3.9 |
| **Cross-Cutting** | Cross-Solution Integration, Agent Security Configuration Governance, Agent Sharing Access Restriction Detector | Multiple pillars |

> **Full catalog:** See [Solutions Index](docs/reference/solutions-index.md) for version details, deployment status, and repository links. See [Solutions Integration](docs/framework/solutions-integration.md) for architecture and control mappings.

---

## 🔧 Setup & Verification Workflow

Each control in this framework follows a consistent documentation structure.

Each control includes linked **implementation playbooks** with step-by-step portal walkthroughs, PowerShell automation, verification testing, and troubleshooting.

Use this workflow for implementing controls:

### Control Documentation Structure

Every control file (1.1–4.7) follows this standardized 10-section structure:

| Section | Purpose |
|---------|---------|
| **Objective** | Concise purpose statement |
| **Why This Matters for FSI** | Regulatory justifications with specific regulation references |
| **Control Description** | Detailed technical explanation |
| **Key Configuration Points** | Specific settings to configure |
| **Zone-Specific Requirements** | Zone 1/2/3 requirements and rationale |
| **Roles & Responsibilities** | Admin roles mapped to responsibilities |
| **Related Controls** | Cross-references to related controls |
| **Implementation Playbooks** | Links to portal-walkthrough, PowerShell-setup, verification-testing, and troubleshooting guides |
| **Verification Criteria** | Numbered checklist for validating effectiveness |
| **Additional Resources** | Microsoft Learn links and admin portal URLs |

### Implementation Steps

```mermaid
graph LR
    A[1. Check Prerequisites] --> B[2. Follow Setup Steps]
    B --> C[3. Configure per Zone]
    C --> D[4. Verify Configuration]
    D --> E[5. Document Evidence]
    E --> F[6. Schedule Review]
```

1. **Check Prerequisites**: Verify licenses, admin roles, and dependencies (other controls that must be configured first)
2. **Follow Setup Steps**: Use portal-based or PowerShell configuration methods
3. **Configure per Zone**: Apply settings appropriate for Zone 1, 2, or 3
4. **Verify Configuration**: Execute verification steps to confirm active controls
5. **Document Evidence**: Capture screenshots, export logs, record in compliance system
6. **Schedule Review**: Set quarterly review cadence for control effectiveness

### Maintainers: Validate Locally

Run these from the repo root (`FSI-AgentGov/`):

- `python scripts/verify_controls.py`
- `python scripts/verify_templates.py`
- `python scripts/verify_excel_templates.py`
- `mkdocs build --strict`

### Quick Reference Resources

| Resource | Description | Location |
|----------|-------------|----------|
| **Control Template** | Standard template for control documentation | [templates/control-setup-template.md](docs/templates/control-setup-template.md) |
| **Microsoft Learn URLs** | Master list of official documentation | [reference/microsoft-learn-urls.md](docs/reference/microsoft-learn-urls.md) |
| **Portal Navigation Paths** | Quick reference for admin center navigation | [reference/portal-paths-quick-reference.md](docs/reference/portal-paths-quick-reference.md) |
| **License Requirements** | License mapping for all 71 controls | [reference/license-requirements.md](docs/reference/license-requirements.md) |
| **FSI Configuration Examples** | Bank, broker-dealer, and insurance scenarios | [reference/fsi-configuration-examples.md](docs/reference/fsi-configuration-examples.md) |
| **Solutions Index** | Catalog of 27 deployable automation solutions | [reference/solutions-index.md](docs/reference/solutions-index.md) |

### Priority Controls (Start Here)

These foundation controls should be implemented first as other controls depend on them:

| Priority | Control | Why First |
|----------|---------|-----------|
| 1 | [2.1 - Managed Environments](docs/controls/pillar-2-management/2.1-managed-environments.md) | Required for 15+ other controls |
| 2 | [1.7 - Audit Logging](docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Compliance evidence for all controls |
| 3 | [1.11 - Conditional Access & MFA](docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Security baseline |
| 4 | [1.5 - DLP & Sensitivity Labels](docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Data protection foundation |
| 5 | [1.4 - Advanced Connector Policies](docs/controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Connector governance for agents |

### Admin Portal Quick Access

| Portal | URL | Primary Use |
|--------|-----|-------------|
| Power Platform Admin Center | [admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com) | Environments, DLP, connectors |
| Microsoft Purview Portal | [purview.microsoft.com](https://purview.microsoft.com) | Audit, DLP, retention |
| Microsoft Entra Admin Center | [entra.microsoft.com](https://entra.microsoft.com) | Conditional access, MFA, roles |
| SharePoint Admin Center | [admin.microsoft.com/sharepoint](https://admin.microsoft.com/sharepoint) | SharePoint governance |
| Copilot Studio | [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com) | Agent development |

---

## Regulatory Coverage

Regulatory mappings and coverage are maintained in a single canonical table:

- See [Regulatory Mappings](docs/reference/regulatory-mappings.md)

> **Note:** Coverage indicates which framework controls address aspects of each regulation. Actual compliance requires implementation, validation, and ongoing maintenance. Consult legal counsel for regulatory interpretation. See [Disclaimer](docs/disclaimer.md).

---

## 💡 Key Concepts

### Governance Maturity Levels

Each control supports **three implementation levels** with a **five-point maturity scale**:

**Implementation Levels:**

- **Baseline:** Minimum required (Zone 1)
- **Recommended:** Best practice (Zone 2)
- **Regulated:** Comprehensive controls (Zone 3)

**Maturity Assessment (0-4):**

- **Level 0 (0%):** Not implemented
- **Level 1 (25%):** Baseline
- **Level 2-3 (50-75%):** Recommended
- **Level 4 (100%):** Regulated

### Control Implementation Approach

1. **Assess** - Current state vs. required level
2. **Implement** - Follow control guidance
3. **Verify** - Use verification procedures
4. **Document** - Record evidence for audit
5. **Review** - Schedule recurring reviews (quarterly)

---

## 📋 Governance Roles

Key roles from **[RACI Matrix](docs/reference/raci-matrix.md)**:

| Role | Responsibility |
|------|-----------------|
| **AI Governance Lead** | Framework oversight, policy decisions |
| **Compliance Officer** | Regulatory alignment, audit coordination |
| **CISO** | Security policy, threat response |
| **Power Platform Admin** | Technical implementation, environments |
| **Internal Audit** | Independent control testing |

---

## 🔧 Implementation Timeline

Typical 8-week rollout:

- **Phase 1 (Weeks 1-2):** Regulatory Compliance Baseline (11 tasks)
- **Phase 2 (Weeks 3-4):** Security Enhancements (10 tasks)
- **Phase 3 (Weeks 5-6):** Advanced Governance (8 tasks)
- **Phase 4 (Weeks 7-8):** Finalization & Operationalization (9 tasks)

See **[Implementation Checklist](docs/getting-started/checklist.md)** for detailed tasks.

---

## ❓ Support & Questions

### For Different Questions:
- **"How do I get started?"** → Read **[Quick Start Guide](docs/getting-started/quick-start.md)**
- **"What's my governance zone?"** → See **[Zones Overview](docs/framework/zones-and-tiers.md)**
- **"Which controls apply to my regulation?"** → Check **[Regulatory Mappings](docs/reference/regulatory-mappings.md)**
- **"Who does what?"** → Review **[RACI Matrix](docs/reference/raci-matrix.md)**
- **"What does this term mean?"** → Look up **[Glossary](docs/reference/glossary.md)**
- **"How do I implement this?"** → Use **[Implementation Checklist](docs/getting-started/checklist.md)**
- **"Common questions?"** → See **[FAQ](docs/reference/faq.md)**
- **"How do I automate this?"** → See **[Solutions Index](docs/reference/solutions-index.md)**

### For Technical Implementation:
- Reference individual control files (1.1-4.7)
- Each control includes step-by-step verification procedures
- Contact your Power Platform Admin for platform-specific setup

### For Regulatory Questions:
- Review **[Regulatory Mappings](docs/reference/regulatory-mappings.md)** for regulation-to-control alignment
- Contact your Compliance Officer for regulatory interpretation
- Escalate to General Counsel for legal questions

---

## 📈 Continuous Improvement

This framework is designed for continuous evolution:

- **Quarterly Reviews:** Assess control effectiveness
- **Annual Updates:** Incorporate regulatory changes and Microsoft updates
- **Version History:** Track changes and improvements
- **Feedback Loop:** Gather input from governance team

---

## 📄 Document Version History

> For detailed changes, see the [Changelog](CHANGELOG.md) index. Current: [v1.2.x](CHANGELOG-v1.2.md) | [v1.1.x](CHANGELOG-v1.1.md) | [v1.0.x](CHANGELOG-v1.0.md)

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| [1.2.53](CHANGELOG-v1.2.md#1253--march-2026-governance-readiness-assessment-tool) | Mar 2026 | Interactive Governance Readiness Assessment tool, assessment data extraction | [@judeper](https://github.com/judeper) |
| [1.2.52](CHANGELOG-v1.2.md#1252--february-2026-sspm-coverage-remediation) | Feb 2026 | SSPM coverage remediation | [@judeper](https://github.com/judeper) |
| [1.2.51](CHANGELOG-v1.2.md#1251--february-2026-uasd-review-remediation) | Feb 2026 | UASD review remediation — 6 critical script fixes, troubleshooting expansion | [@judeper](https://github.com/judeper) |
| [1.2.0](CHANGELOG-v1.2.md#120--january-25-2026-platform-change-governance) | Jan 2026 | Four-pillar expansion (71 controls), 284 playbooks, companion solutions | [@judeper](https://github.com/judeper) |
| [1.1.0](CHANGELOG-v1.1.md#11--january-2026) | Jan 2026 | Three-layer documentation architecture, 252 playbooks, framework layer | [@judeper](https://github.com/judeper) |
| [1.0.0](CHANGELOG-v1.0.md#10--january-2026) | Jan 2026 | Evaluation gates, adversarial testing, multi-agent governance, RACI | [@judeper](https://github.com/judeper) |
| [Beta](CHANGELOG-v1.0.md#beta--december-2025) | Dec 2025 | DSPM, bias testing, runtime protection, FINRA Notice 25-07 alignment | [@judeper](https://github.com/judeper) |

---

## 📝 License

This framework is provided for use by financial services organizations. Modify as needed for your organization's specific requirements.

---

## ⚠️ Legal Disclaimer

See [Disclaimer](docs/disclaimer.md).

---

## 🎯 Next Steps

1. **Review** the [Quick Start Guide](docs/getting-started/quick-start.md)
2. **Assess** your current state against the framework
3. **Implement** using the step-by-step guidance
4. **Document** evidence for audit compliance
5. **Review** quarterly and update as regulations change

---

*FSI Agent Governance Framework v1.2.53 - March 2026*
*Comprehensive governance for Microsoft 365 agents in financial services*
