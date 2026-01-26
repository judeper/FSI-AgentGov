# Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).

---

## Prerequisites

Before starting, confirm:

- E5 or E5 Compliance licenses assigned to users
- Sensitivity label taxonomy defined for organization
- Labels published to target users and groups
- DLP administrator access verified
- Agent inventory completed (know what agents access which data)
- Control 1.13 SITs implemented and validated

---

## DLP Enforcement Status (2025)

As of early 2025, **data policy enforcement for Copilot Studio is enabled by default** for all tenants (per Microsoft message center alert MC973179). Organizations no longer need to manually enable DLP enforcement.

---

## Step 1: Configure AI-Specific DLP Policies

1. Open [Microsoft Purview](https://purview.microsoft.com)
2. Navigate to **Data loss prevention** > **Policies**
3. Select **+ Create policy**
4. Choose a template (Financial/Privacy) or start from **Custom**
5. Name the policy: `FSI-AI-DLP-Data-Protection`
6. Select AI locations:
   - **Microsoft 365 Copilot** (prompts and responses)
   - **Copilot Studio** (agent interactions)
   - Optional: **Devices** if Endpoint DLP is in scope
7. Configure conditions using SITs and/or sensitivity labels
8. Choose actions appropriate to governance tier:
   - **Tier 1**: Audit only
   - **Tier 2**: Warn user, log event
   - **Tier 3**: Block access, notify compliance
9. Start in **Test with notifications**
10. Save and allow time for propagation

---

## Step 2: Configure Copilot Studio Channel DLP

DLP policies can control which publishing channels Copilot Studio agents can use. Microsoft supports **6 channel connectors**:

| # | Channel Connector | Description |
|---|-------------------|-------------|
| 1 | **Direct Line channels** | Web chat, custom apps via Direct Line API |
| 2 | **Microsoft Teams + M365** | Teams chat and M365 surfaces |
| 3 | **Facebook** | Facebook Messenger integration |
| 4 | **Omnichannel** | Dynamics 365 Omnichannel for Customer Service |
| 5 | **SharePoint** | SharePoint site embedding |
| 6 | **WhatsApp** | WhatsApp Business integration |

**To block agent publishing:** Block ALL 6 channel connectors via DLP. If no channels are allowed, agents cannot be published to any audience.

---

## Step 3: Configure Sensitivity Labels

### Create Labels

1. Navigate to **Information protection** > **Labels**
2. Create labels following U.S.-only taxonomy:

| Label | What it means | Default AI/DLP posture |
|-------|---------------|------------------------|
| **Public** | Approved for public release | Allow; audit optional |
| **Internal** | Business-use only; low sensitivity | Allow; audit recommended |
| **Confidential** | Customer NPI / regulated internal data | Warn or block; always log |
| **Highly Confidential** | High impact if exposed | Block by default; incident report |

### Publish Labels

1. Navigate to **Label policies**
2. Create policy to publish labels to:
   - Users who create or handle content
   - Owners/operators of agents that access labeled knowledge sources
   - Compliance/SecOps roles who investigate DLP events

---

## Step 4: Configure Label-Based DLP Rules

1. In your DLP policy, add rules with label conditions
2. Configure actions:
   - **Highly Confidential**: Block agent access
   - **Confidential**: Warn user, log access
   - **Internal/Public**: Allow access

---

## Step 5: Configure DSPM for AI Integration

### View DLP Policies in DSPM

1. Navigate to **DSPM for AI** > **Policies**
2. Expand **Data Loss Prevention** section
3. View AI-related DLP policies and status

### Create Oversharing Assessment

1. Navigate to **DSPM for AI** > **Data risk assessments**
2. Review **Assess and prevent oversharing** section
3. Click **+ Create custom assessment**
4. Select data sources (SharePoint sites used by agents)
5. Define user scope
6. Review overshared items count
7. Remediate excessive permissions

---

## Policy Templates for FSI

### Customer Data Protection

```
Policy: Protect Customer PII in AI
Locations: M365 Copilot, Copilot Studio
Conditions:
  - Sensitive info types: SSN, Account Numbers, Credit Card
  - OR Sensitivity label: Confidential, Highly Confidential
Actions:
  - Tier 1-2: Warn user, log event
  - Tier 3: Block access, notify compliance
```

### Financial Data Protection

```
Policy: Block Financial Data in AI Responses
Locations: Copilot Studio agents
Conditions:
  - Sensitive info types: Financial statements, Trading data
  - Sensitivity label: Highly Confidential
Actions:
  - Tier 2: Warn, log event, incident report
  - Tier 3: Block, notify security team
```

---

## Governance Tier Configuration

| Tier | DLP Mode | Label Requirement | Oversharing Review |
|------|----------|-------------------|-------------------|
| Tier 1 | Audit only | Optional | Annual |
| Tier 2 | Warn | Recommended | Quarterly |
| Tier 3 | Block | **Mandatory** | Monthly |

---

## Zone-Specific Configuration

### Zone 1 (Personal Productivity)

- Apply baseline DLP policies for tenant-wide safety
- Avoid expanding scope beyond user's own data
- Keep friction low while maintaining safety

### Zone 2 (Team Collaboration)

- Apply DLP to AI locations (Copilot/M365, Copilot Studio)
- Require identified owner and approval trail
- Validate in pilot before broader rollout

### Zone 3 (Enterprise Managed)

- Require strictest DLP configuration
- Enforce via policy where possible
- Treat changes as controlled with change tickets

---

## Validation

After completing the configuration, verify:

1. [ ] DLP policy `FSI-AI-DLP-Data-Protection` is created and enabled in Microsoft Purview
2. [ ] Sensitivity labels are published and visible to users in Office applications
3. [ ] DLP policy locations include Microsoft 365 Copilot and Copilot Studio
4. [ ] Oversharing assessment completed in DSPM for AI with remediation items documented

**Expected Result:** DLP policies detect and act on sensitive information in AI interactions, and sensitivity labels are available for content classification.

---

[Back to Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
