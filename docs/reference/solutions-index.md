# Solutions Index

Deployable Power Platform solutions for the FSI Agent Governance Framework.

---

## Overview

The **FSI-AgentGov-Solutions** repository contains ready-to-deploy automation solutions that implement framework controls. Each solution includes Power Automate flows, Dataverse components, and configuration guidance.

**Repository:** [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions)

---

## Available Solutions

| Solution | Version | Description | Related Controls |
|----------|---------|-------------|------------------|
| [Environment Lifecycle Management](#environment-lifecycle-management) | v1.1.1 | Automated Power Platform environment provisioning with zone-based governance classification | 2.1, 2.2, 2.15 |
| [Message Center Monitor](#message-center-monitor) | v2.1.1 | Monitor M365 Message Center for platform changes affecting AI agents | 2.3, 2.10 |
| [Pipeline Governance Cleanup](#pipeline-governance-cleanup) | v1.0.8 | Discover, notify, and clean up personal pipelines before enforcing centralized ALM governance | 2.3 |
| [Deny Event Correlation Report](#deny-event-correlation-report) | v1.1.0 | Daily deny event correlation across Purview Audit, DLP, and Application Insights | 1.5, 1.7, 3.4 |

---

## Solution Details

### Environment Lifecycle Management

Automates Power Platform environment provisioning using a Copilot Studio intake agent. Ensures consistent zone classification and governance controls from day one.

**Components:**
- Copilot Studio intake agent for environment requests
- Power Automate provisioning flows
- Dataverse tables for request tracking
- Zone classification automation

**Framework Playbook:** [Environment Lifecycle Management](../playbooks/advanced-implementations/environment-lifecycle-management/index.md)

**Repository Link:** [environment-lifecycle-management](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management)

---

### Message Center Monitor

Polls Microsoft 365 Message Center for platform announcements and delivers structured notifications to Teams. Supports governance workflows for change assessment and decision documentation.

**Components:**
- Power Automate polling flow (Graph API)
- Teams adaptive card notifications
- Microsoft Entra ID app registration with `ServiceMessage.Read.All`
- Dataverse integration (optional)

**Framework Playbook:** [Platform Change Governance](../playbooks/advanced-implementations/platform-change-governance/index.md)

**Repository Link:** [message-center-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor)

---

### Pipeline Governance Cleanup

!!! warning "February 2026 Deadline"
    Microsoft will automatically enable Managed Environments for pipeline target environments starting February 2026. Use this solution to audit and remediate personal pipelines before enforcement. See [Control 2.1](../controls/pillar-2-management/2.1-managed-environments.md#critical-deadline-february-2026-pipeline-requirement) for details.

Discovers personal deployment pipelines across environments and notifies owners before enforcing centralized ALM governance. Supports transition from ad-hoc to governed deployment patterns.

**Components:**
- PowerShell discovery scripts
- Owner notification workflows
- Cleanup automation with safety checks
- Dry-run mode for impact assessment

**Related Control:** [2.3 - Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

**Repository Link:** [pipeline-governance-cleanup](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup)

---

### Deny Event Correlation Report

Aggregates and correlates deny events from multiple Microsoft sources to provide unified visibility into blocked agent activities.

**Data Sources:**
- Purview Unified Audit Log
- DLP policy violations
- Application Insights RAI telemetry

**Components:**
- Power BI report template
- Data extraction scripts
- Correlation logic

**Framework Playbook:** [Deny Event Correlation Report](../playbooks/advanced-implementations/deny-event-correlation-report/index.md)

**Repository Link:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)

---

## Getting Started

1. Review the relevant framework playbook for architecture and requirements
2. Clone the [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) repository
3. Navigate to the solution folder and follow the README
4. Configure Microsoft Entra ID app registrations as documented
5. Deploy Power Automate flows and test in a non-production environment

---

## Version History

Solutions follow semantic versioning. See each solution's README for detailed changelog.

| Solution | Current | Last Updated |
|----------|---------|--------------|
| Environment Lifecycle Management | v1.1.2 | January 2026 |
| Message Center Monitor | v2.1.1 | January 2026 |
| Pipeline Governance Cleanup | v1.0.8 | January 2026 |
| Deny Event Correlation Report | v1.1.0 | January 2026 |

---

*FSI Agent Governance Framework v1.2 - January 2026*
