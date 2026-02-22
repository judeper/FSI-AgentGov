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
8. Choose actions appropriate to governance zone:
   - **Zone 1**: Audit only
   - **Zone 2**: Warn user, log event
   - **Zone 3**: Block access, notify compliance
9. Start in **Test with notifications**
10. Save and allow time for propagation

---

## Step 2: Configure Virtual Governance Connectors

Power Platform DLP policies enforce data protection through 11 virtual governance connectors for Copilot Studio agents. These connectors control AI capabilities, knowledge sources, and publishing channels.

### Classify Virtual Governance Connectors

!!! info "GA Feature"
    Virtual governance connectors are generally available as of Q1 2025. This configuration step applies to all Power Platform DLP policies.

1. Navigate to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select **Policies** > **Data policies**
3. Select an existing DLP policy or create a new one
4. In the **Connectors** tab, locate the virtual governance connectors:
   - AI Builder (GPT)
   - AI Builder (Document Processing)
   - Copilot Studio Topics
   - Copilot Studio Skills
   - Copilot Studio Knowledge
   - HTTP with Microsoft Entra ID
   - HTTP Webhook
   - Direct Line
   - Microsoft Teams Channel
   - SharePoint Channel
   - Custom Website Channel

5. Classify each connector into one of three categories:
   - **Business** - Allowed for use in environments within policy scope
   - **Non-Business** - Cannot be used alongside Business connectors in the same agent
   - **Blocked** - Completely prohibited from use

### Zone-Specific Classification Configuration

#### Zone 1 (Personal Productivity) Configuration

For Zone 1 environments, apply minimal restrictions to enable self-service agent development:

| Connector | Classification | Rationale |
|-----------|----------------|-----------|
| AI Builder (GPT) | Business | Enable generative AI capabilities |
| AI Builder (Document Processing) | Business | Enable document understanding |
| Copilot Studio Topics | Business | Core agent functionality |
| Copilot Studio Skills | Business | Enable Power Automate integration |
| Copilot Studio Knowledge | Business | Enable knowledge source grounding |
| HTTP with Microsoft Entra ID | Business or Non-Business | Allow authenticated HTTP; block list social media |
| HTTP Webhook | Non-Business or Blocked | Minimize unauthenticated external calls |
| Direct Line | Business | Enable web chat deployment |
| Microsoft Teams Channel | Business | Primary publishing channel |
| SharePoint Channel | Non-Business | Use with caution |
| Custom Website Channel | Non-Business or Blocked | Restrict external publishing |

**Zone 1 Configuration Steps:**

1. Classify all AI Builder and Copilot Studio connectors as Business
2. Classify HTTP Webhook as Non-Business or Blocked
3. Classify Custom Website Channel as Non-Business or Blocked
4. For HTTP with Microsoft Entra ID, configure block list for social media domains (see below)
5. Save policy and verify propagation

#### Zone 2 (Team Collaboration) Configuration

For Zone 2 environments, balance team collaboration with controlled external access:

| Connector | Classification | Rationale |
|-----------|----------------|-----------|
| AI Builder (GPT) | Business | Required for team agents |
| AI Builder (Document Processing) | Business | Required for team document processing |
| Copilot Studio Topics | Business | Core agent functionality |
| Copilot Studio Skills | Business | Enable approved Power Automate flows |
| Copilot Studio Knowledge | Business | Enable team knowledge sources |
| HTTP with Microsoft Entra ID | Business | Allow with block list for risky endpoints |
| HTTP Webhook | **Blocked** | Prevent unauthenticated external calls |
| Direct Line | Business | Enable web chat for team agents |
| Microsoft Teams Channel | Business | Primary publishing channel |
| SharePoint Channel | Non-Business or Blocked | Require approval per agent |
| Custom Website Channel | **Blocked** | External publishing requires security review |

**Zone 2 Configuration Steps:**

1. Classify all AI Builder and Copilot Studio connectors as Business
2. Classify HTTP Webhook as Blocked (not Non-Business)
3. Classify Custom Website Channel as Blocked
4. For HTTP with Microsoft Entra ID, configure block list for social media and file-sharing domains
5. Classify SharePoint Channel as Non-Business (requires per-agent justification to use)
6. Save policy and document approved connectors

#### Zone 3 (Enterprise Managed) Configuration

For Zone 3 environments, apply strictest controls for customer-facing and regulated agents:

| Connector | Zone 3 Classification | Governance Control |
|-----------|----------------------|-------------------|
| AI Builder (GPT) | Business | Monitor via Control 3.2 (Usage Analytics and Activity Monitoring) |
| AI Builder (Document Processing) | Business | Log all document uploads |
| Copilot Studio Topics | Business | Core functionality; no restrictions |
| Copilot Studio Skills | Business | Require flow approval per Control 2.2 |
| Copilot Studio Knowledge | Business | **Prerequisites:** Control 1.3 + Control 4.1 must be implemented |
| HTTP with Microsoft Entra ID | Business | **Required:** HTTP endpoint allow list filtering (see below) |
| HTTP Webhook | **Blocked** | Data exfiltration risk; use Entra-authenticated alternative |
| Direct Line | Business | Monitor via Control 3.3 (Compliance and Regulatory Reporting) |
| Microsoft Teams Channel | Business | Approved internal publishing channel |
| SharePoint Channel | **Blocked** | Embedding poses XSS risk; requires security review |
| Custom Website Channel | **Blocked** | External publishing requires penetration testing |

**Zone 3 Configuration Steps:**

1. Classify AI Builder (GPT) and AI Builder (Document Processing) as Business
2. Classify all Copilot Studio connectors as Business
3. Classify HTTP Webhook as **Blocked** (not Non-Business)
4. Classify SharePoint Channel as **Blocked** (not Non-Business)
5. Classify Custom Website Channel as **Blocked**
6. For HTTP with Microsoft Entra ID:
   - Classify as Business
   - **REQUIRED:** Configure HTTP endpoint filtering with allow list (see next section)
7. Save policy and document configuration in change control system (Control 2.1)

### Configure HTTP Endpoint Filtering

!!! warning "Zone 3 Requirement"
    Zone 3 environments MUST configure HTTP endpoint filtering with allow list mode. Failure to configure endpoint filtering creates data exfiltration risk.

For HTTP with Microsoft Entra ID connector classified as Business, configure endpoint filtering:

#### Step 1: Access Endpoint Filtering Configuration

1. In the DLP policy, locate **HTTP with Microsoft Entra ID** connector in the Business classification group
2. Click the connector name or select **Configure connector** from the three-dot menu
3. Select **Endpoint filtering** tab
4. Choose filtering mode:
   - **Allow list** (Zone 3 requirement) - Only specified domains/patterns permitted; all others blocked
   - **Block list** (Zone 1-2 option) - Specified domains/patterns blocked; all others allowed

#### Step 2: Configure Zone-Specific Patterns

**For Zone 1 (Block list mode):**

Block social media and consumer file-sharing APIs:

```
https://*.twitter.com/*
https://api.twitter.com/*
https://*.linkedin.com/oauth/*
https://api.linkedin.com/*
https://*.facebook.com/*
https://graph.facebook.com/*
https://*.dropbox.com/*
https://api.dropbox.com/*
https://*.box.com/*
https://api.box.com/*
http://*                          # Block all unencrypted HTTP
```

**For Zone 2 (Block list or Allow list):**

If using block list, add to Zone 1 patterns:

```
https://*.file-sharing.com/*
https://*.free-tier.com/*
```

If using allow list, specify approved internal and regulatory endpoints only.

**For Zone 3 (Allow list mode - REQUIRED):**

Specify approved internal APIs and regulatory data sources only:

```
*.internal.yourbank.com           # Internal domain (all subdomains)
api.yourbank.com                  # Primary API gateway
*.core-banking-system.local       # On-premises core banking APIs
https://api.sec.gov/*             # SEC EDGAR API
https://api.finra.org/*           # FINRA regulatory APIs
https://www.ffiec.gov/*           # FFIEC data repository
https://data.treasury.gov/*       # U.S. Treasury data feeds
```

For approved partner bank APIs (with BAA):

```
https://api.partner-bank.com/*
```

For approved market data vendors (Bloomberg, Refinitiv):

```
https://api.bloomberg.com/*       # Requires vendor approval + BAA
https://api.refinitiv.com/*       # Requires vendor approval + BAA
```

#### Step 3: Document and Verify Configuration

1. Click **Save** to apply endpoint filters
2. **Screenshot:** Capture the endpoint filtering configuration for audit evidence
3. Document all allowed endpoints in your IT change control system (Control 2.1)
4. For Zone 3, obtain dual approval from Power Platform Admin + AI Governance Lead
5. Allow 1-2 hours for policy propagation before testing

#### Step 4: Portal Verification Steps

After configuration, verify in PPAC:

1. Navigate to Policies > Data policies > [Your Policy] > Connectors
2. Locate **HTTP with Microsoft Entra ID** in Business classification
3. Verify endpoint filtering icon/badge appears next to connector name
4. Click connector to verify filtering mode and patterns are correct
5. Confirm policy scope includes target environments

**Expected Portal Display:**

- Connector shows "Endpoint filtering configured" badge or icon
- Clicking connector displays configured patterns
- Filtering mode (Allow list / Block list) is correct for zone
- No syntax errors in URL patterns

### Verify Connector Classification

After completing zone-specific configuration, verify all settings:

1. In the DLP policy, review the **Connectors** tab
2. Confirm all 11 virtual governance connectors appear with expected classifications per zone
3. Verify HTTP with Microsoft Entra ID shows endpoint filtering configured (Zone 3 requirement)
4. Note that policies apply to all environments within the policy scope
5. Export policy configuration via PowerShell (see PowerShell Setup playbook) for audit evidence
6. Document configuration in change control system per Control 2.1
7. Allow 1-2 hours for policy propagation before executing test cases

---

## Step 3: Configure Copilot Studio Channel DLP

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

## Step 4: Configure Sensitivity Labels

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

## Step 5: Configure Label-Based DLP Rules

1. In your DLP policy, add rules with label conditions
2. Configure actions:
   - **Highly Confidential**: Block agent access
   - **Confidential**: Warn user, log access
   - **Internal/Public**: Allow access

---

## Step 6: Configure DSPM for AI Integration

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
  - Zone 1-2: Warn user, log event
  - Zone 3: Block access, notify compliance
```

### Financial Data Protection

```
Policy: Block Financial Data in AI Responses
Locations: Copilot Studio agents
Conditions:
  - Sensitive info types: Financial statements, Trading data
  - Sensitivity label: Highly Confidential
Actions:
  - Zone 2: Warn, log event, incident report
  - Zone 3: Block, notify security team
```

---

## Governance Zone Configuration

| Zone | DLP Mode | Label Requirement | Oversharing Review |
|------|----------|-------------------|-------------------|
| Zone 1 | Audit only | Optional | Annual |
| Zone 2 | Warn | Recommended | Quarterly |
| Zone 3 | Block | **Mandatory** | Monthly |

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
2. [ ] All 11 virtual governance connectors are classified in Power Platform DLP policy
3. [ ] HTTP endpoint filtering configured for HTTP with Microsoft Entra ID connector (Zone 3)
4. [ ] Sensitivity labels are published and visible to users in Office applications
5. [ ] DLP policy locations include Microsoft 365 Copilot and Copilot Studio
6. [ ] Oversharing assessment completed in DSPM for AI with remediation items documented

**Expected Result:** DLP policies detect and act on sensitive information in AI interactions, virtual governance connectors are appropriately classified for FSI risk posture, and sensitivity labels are available for content classification.

---

[Back to Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
