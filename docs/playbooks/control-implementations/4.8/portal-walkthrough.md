# Control 4.8: Portal Walkthrough — Item-Level Permission Scanning for Agent Knowledge Sources

> **Parent Control:** [Control 4.8 — Item-Level Permission Scanning](../../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md)
>
> **Related Playbooks:** [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

## Overview

This walkthrough guides administrators through identifying agent knowledge sources, reviewing item-level permissions, and establishing the pre-deployment gate for Copilot Studio agents in regulated financial services environments.

!!! warning "Pre-Deployment Gate"
    This control establishes a **hard gate**: agents must not go to production if CRITICAL risk items exist in their knowledge source libraries. This is a requirement, not a recommendation.

---

## Prerequisites

Before beginning this walkthrough:

- [ ] **Control 4.1** (IAG/RCD/RSS) is configured — site-level access governance is in place
- [ ] **Control 4.5** (Security Monitoring) is enabled — DSPM provides baseline risk scoring
- [ ] SharePoint Admin role assigned to implementing administrator
- [ ] Access to Copilot Studio environment where agents are deployed
- [ ] Access to SharePoint Admin Center for permission review
- [ ] `Get-KnowledgeSourceItemPermissions.ps1` available from [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner)

---

## Step 1: Identify Agent Knowledge Sources

### 1.1 — Locate Agent Definitions in Copilot Studio

1. Navigate to **Copilot Studio** → [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. Select the target **environment** from the environment picker
3. Navigate to **Agents** in the left navigation
4. For each deployed agent, select the agent to open its configuration
5. Navigate to **Knowledge** in the agent settings

### 1.2 — Document Connected SharePoint Libraries

For each agent, record all SharePoint knowledge sources:

| Agent Name | Environment | SharePoint Site URL | Library/Folder Path | Files Count | Last Reviewed |
|-----------|-------------|--------------------|--------------------|-------------|---------------|
| *Example: HR Policy Agent* | *Production* | *contoso.sharepoint.com/sites/hr-policies* | */Documents/Current Policies* | *127* | *YYYY-MM-DD* |

!!! tip "Agent Insights Shortcut"
    If Control 4.5 is implemented, use **SharePoint Admin Center > Reports > Agent insights** to quickly identify which sites have agents connected. This provides a tenant-wide view of agent-to-site relationships.

### 1.3 — Verify Knowledge Source Configuration

For each knowledge source, confirm:

- [ ] The SharePoint site is in the RCD/RSS allowed scope (Control 4.1/4.6)
- [ ] The library is within Copilot Studio SharePoint unstructured-data knowledge source limits: **1,000 files, 50 folders, 10 layers of subfolders, 512 MB per file** (per Microsoft Learn, April 2026). Items beyond these limits are silently not indexed but remain a sharing risk.
- [ ] Sensitivity labels are applied to content in the library

!!! info "Platform behavior — labeled items are not indexed"
    Per Microsoft Learn, items labeled **Confidential** or **Highly Confidential** (and password-protected files) are not indexed by Copilot Studio knowledge sources. A correctly labeled file should not be retrieved by the agent. CRITICAL findings most often signal **mislabeling, missing labels, or label removal** rather than active retrieval — but the file still represents an oversharing risk that could become active if labels change or if the file is reused elsewhere.

---

## Step 2: Review Item-Level Permissions in SharePoint Admin Center

### 2.1 — Access Site Permissions

1. Navigate to **SharePoint Admin Center** → [https://admin.microsoft.com/sharepoint](https://admin.microsoft.com/sharepoint)
2. Select **Sites** → **Active sites**
3. Locate the site containing the agent knowledge source
4. Select the site name → **Permissions** tab

### 2.2 — Identify Permission Inheritance Breaks

1. Navigate to the knowledge source library in the site
2. Select **Settings** (gear icon) → **Library settings**
3. Select **Permissions for this document library**
4. Review the **Manage Access** panel for items with unique permissions

!!! note "Unique Permissions Indicator"
    Items with broken inheritance (unique permissions) are the highest-risk items because their permissions differ from the library defaults. These items require individual review.

### 2.3 — Check for Oversharing Indicators

Review each item with unique permissions for:

| Indicator | Risk | Action |
|-----------|------|--------|
| **Anyone links** | HIGH | Remove link; restrict to specific people |
| **External user access** | HIGH | Remove external access unless business-justified |
| **Everyone Except External Users (EEEU)** | MEDIUM | Restrict to agent user group |
| **Organization-wide sharing** | MEDIUM | Scope to specific security group |
| **Confidential/Highly Confidential label + broad access** | CRITICAL | Disconnect agent or restrict immediately |

---

## Step 3: Run Item-Level Permission Scan

### 3.1 — Configure Scan Scope

Before running the automated scan:

1. Ensure `config/item-scope-config.json` reflects your organization's sensitivity label taxonomy
2. Identify the target libraries from the inventory created in Step 1
3. Confirm the scanning account has **Site Collection Administrator** or **SharePoint Admin** permissions on target sites

### 3.2 — Execute Scan

!!! info "Automated Scanning"
    For automated scanning, see the [PowerShell Setup](powershell-setup.md) playbook. The `Get-KnowledgeSourceItemPermissions.ps1` script from [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner) automates the item-level scanning process.

For manual portal-based review of smaller libraries:

1. Navigate to the knowledge source library
2. Select **Settings** → **Library settings** → **Permissions for this document library**
3. For each item with unique permissions, review the **Manage Access** panel
4. Document findings using the risk classification table in Step 2.3

---

## Step 4: Review and Prioritize Findings

### 4.1 — Review Scan Output

The scan produces a CSV output with item-level risk classifications. Review findings by priority:

| Priority | Review Approach | Governance Level |
|----------|----------------|-----------------|
| **CRITICAL** | Immediate review — disconnect agent or remediate within 4 hours | All levels |
| **HIGH** | Same-day review — remediate within 24 hours | Recommended + Regulated |
| **MEDIUM** | Business-week review — remediate within 5 business days | Regulated |
| **LOW** | Scheduled review — document in next scan cycle | All levels |

### 4.2 — Governance Level Requirements

| Governance Level | Scanning Requirement | Pre-Deployment Gate | Recurring Cadence |
|-----------------|---------------------|--------------------|--------------------|
| **Baseline** | Recommended before deployment | Advisory (document exceptions) | Quarterly |
| **Recommended** | Required before deployment | Required for CRITICAL items | Monthly |
| **Regulated** | Mandatory before deployment | Mandatory — no exceptions for CRITICAL or HIGH | Monthly + on-demand |

---

## Step 5: Remediate Findings

### 5.1 — CRITICAL Items

For items classified as CRITICAL (Confidential/Highly Confidential AND accessible outside agent user group):

**Option A — Disconnect Knowledge Source:**

1. In Copilot Studio, navigate to the agent's **Knowledge** settings
2. Remove the affected SharePoint library as a knowledge source
3. Document the disconnection with business justification
4. Re-enable only after item permissions are remediated

**Option B — Restrict Item Permissions:**

1. Navigate to the item in SharePoint
2. Select **Manage Access** → **Stop sharing** for unauthorized users/groups
3. Set permissions to the agent's intended user group only
4. Verify the item no longer appears in scan output as CRITICAL
5. Document the remediation action

### 5.2 — HIGH Items

For items with Anyone links or external user access:

1. Navigate to the item in SharePoint
2. Select **Manage Access** → remove Anyone links
3. Remove external user access unless business-justified and documented
4. Log remediation evidence for compliance

### 5.3 — MEDIUM Items

For items shared with broad internal groups beyond agent audience:

3. Review sharing scope with the Agent Owner
2. Restrict to the agent's intended user security group
3. Document business justification if broad access is retained

---

## Step 6: Configure Recurring Scans

### 6.1 — Monthly Schedule

1. Configure `Get-KnowledgeSourceItemPermissions.ps1` to run monthly via:
   - Azure Automation runbook (recommended for Zone 3)
   - Windows Task Scheduler (acceptable for Zone 1/2)
   - Power Automate scheduled flow

2. Configure output to be stored in a compliance-accessible location with 7-year retention

### 6.2 — Alert Configuration

Configure alerts for:

- [ ] New CRITICAL items detected in any agent knowledge source
- [ ] New sharing activity on agent-connected libraries (via SharePoint Admin alerts)
- [ ] Agent knowledge source additions or changes in Copilot Studio

---

## Validation Checklist

After completing this walkthrough, confirm:

- [ ] All agent knowledge sources identified and inventoried
- [ ] Item-level permission scan executed on every knowledge source library
- [ ] CRITICAL items remediated or agent disconnected
- [ ] HIGH items remediated within SLA
- [ ] Pre-deployment gate documented and enforced
- [ ] Monthly recurring scan schedule configured
- [ ] Scan output retained with 7-year retention policy
- [ ] Remediation evidence documented for compliance

---

## Audit Evidence Note

Agent responses that use SharePoint as a knowledge source are **not included in Copilot Studio conversation transcripts** (per Microsoft Learn). Where firms rely on this control to help support SEC Rule 17a-4 record-keeping for AI-served content, the evidence chain should combine:

- Item-level scan output CSVs (generated here)
- SharePoint unified audit log entries for `FileAccessed` / `FileDownloaded` events on knowledge source libraries
- Pre-deployment gate sign-offs

This combined evidence aids in supporting examiner inquiries when transcripts alone are incomplete.

---

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
