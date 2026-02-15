# Unrestricted Agent Sharing Detector

**Status:** Complete — February 2026
**Related Controls:** 1.1, 3.8

---

## Overview

The Unrestricted Agent Sharing Detector (UASD) is a continuous compliance solution that scans Copilot Studio agents for sharing configurations that violate organizational policy. It complements the existing Agent Access Governance Monitor (AAM) — where AAM validates environment-level access settings, UASD operates at the per-agent sharing level.

UASD detects five violation types, records findings in Dataverse, drives remediation through Power Automate approval workflows, and manages time-bound exceptions via a canvas app.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Scheduled Trigger                         │
│                  (Recurrence: Daily)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Detection Flow (Detector)                       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ BAP API  │→ │ 5 Violation  │→ │  Dataverse Write +   │  │
│  │ Scan     │  │ Rule Engine  │  │  Teams Adaptive Card  │  │
│  └──────────┘  └──────────────┘  └───────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ New Violation (Status = Open)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Remediation Flow (Auto-triggered)                  │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Exception│→ │ Approval     │→ │  BAP PATCH: Overwrite │  │
│  │ Check    │  │ Flow         │  │  Principals           │  │
│  └──────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         Exception Manager (Canvas App)                       │
│  ┌──────────────┐  ┌────────────┐  ┌─────────────────────┐  │
│  │  Submit       │  │  Dual      │  │  Status + Expiry    │  │
│  │  Exception    │  │  Approval  │  │  Tracking           │  │
│  └──────────────┘  └────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Violation Rules

| # | Rule | Trigger Condition | Severity |
|---|------|-------------------|----------|
| 1 | `ORG_WIDE_SHARING` | Agent shared with "Everyone" or "All Users" | Critical |
| 2 | `PUBLIC_INTERNET_LINK` | Agent has public internet-facing link enabled | Critical |
| 3 | `UNAPPROVED_GROUP` | Agent shared with group not in approved security groups list | High |
| 4 | `EXCESSIVE_INDIVIDUAL` | Agent shared with more individuals than `MaxIndividualSharesPerAgent` policy threshold | Medium |
| 5 | `CROSS_TENANT_ACCESS` | Agent shared with external tenant principals | Critical |

---

## Components

| Component | Type | File |
|-----------|------|------|
| Detector Flow | Power Automate Cloud Flow | `unrestricted-agent-sharing-detector/src/uasd-detector-scan-agents.json` (FSI-AgentGov-Solutions) |
| Remediation Flow | Power Automate Cloud Flow | `unrestricted-agent-sharing-detector/src/uasd-remediation-apply-sharing-policy.json` (FSI-AgentGov-Solutions) |
| Exception Approval Flow | Power Automate Cloud Flow | `unrestricted-agent-sharing-detector/src/uasd-exception-approval-workflow.json` (FSI-AgentGov-Solutions) |
| Exception Manager App | Canvas App | `unrestricted-agent-sharing-detector/src/uasd-exception-manager-app.json` (FSI-AgentGov-Solutions) |
| Alert Adaptive Card | Teams Notification | `unrestricted-agent-sharing-detector/src/adaptive-card-uasd-alert.json` (FSI-AgentGov-Solutions) |
| Dataverse Schema | Python Script | `scripts/create_uasd_dataverse_schema.py` |
| Environment Variables | Python Script | `scripts/create_uasd_environment_variables.py` |
| Connection References | Python Script | `scripts/create_uasd_connection_references.py` |
| On-Demand Audit | PowerShell Script | `scripts/governance/Invoke-SharingAudit.ps1` |
| Deploy Detection Flow | PowerShell Script | `scripts/governance/Deploy-DetectionFlow.ps1` |
| Deploy Remediation Flow | PowerShell Script | `scripts/governance/Deploy-RemediationFlow.ps1` |
| Export Violations | PowerShell Script | `scripts/governance/Export-ViolationReport.ps1` |
| Import Approved Groups | PowerShell Script | `scripts/governance/Import-ApprovedSecurityGroups.ps1` |

---

## Dataverse Tables

| Table | Purpose |
|-------|---------|
| `fsi_AgentSharingSetting` | Per-agent sharing configuration snapshots with scope, principal count, and auth mode |
| `fsi_SharingViolation` | Detected sharing policy violations with agent identity, violation type, and remediation status |
| `fsi_SharingException` | Approved exceptions with dual-approval audit trail and expiration tracking |
| `fsi_ApprovedSecurityGroup` | Whitelist of security groups approved for agent sharing |
| `fsi_SharingPolicy` | Per-zone sharing policy definitions including maximum individual shares threshold |

---

## Regulatory Alignment

| Regulation | Requirement | How UASD Helps |
|------------|-------------|-----------------|
| FINRA 4511 | Books and Records | Violation records with SHA-256 evidence hashing |
| SEC 17a-4 | Recordkeeping | Immutable audit log of sharing configuration changes |
| GLBA 501(b) | Customer Information Safeguards | Detects and remediates overly permissive agent sharing |
| SOX 404 | Internal Controls | Automated control testing with evidence export |

!!! warning "Implementation Caveat"
    This solution supports compliance with the listed regulatory requirements but does not by itself satisfy all obligations. Organizations should validate the deployment against their specific compliance program.

---

## Related Controls

| Control | Relationship |
|---------|--------------|
| [1.1 - Restrict Agent Publishing](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | UASD enforces per-agent sharing restrictions that complement publishing authorization controls |
| [3.8 - Copilot Hub and Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | UASD extends governance visibility into per-agent sharing configurations |

---

## Available Documentation

| Document | Description |
|----------|-------------|
| [Deployment Guide](deployment-guide.md) | End-to-end deployment walkthrough with prerequisites, step-by-step instructions, and validation checklist |

---

*Updated: February 2026 | Version: v1.0 | Framework: FSI Agent Governance v1.2.48*
