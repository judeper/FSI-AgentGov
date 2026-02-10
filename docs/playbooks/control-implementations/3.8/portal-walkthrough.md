# Control 3.8: Copilot Hub and Governance Dashboard - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md).

---

## Prerequisites

- Entra Global Admin role
- Power Platform Admin role
- Microsoft 365 Copilot licenses assigned

---

## Part 1: M365 Admin Center - Copilot Section

### Step 1: Access Copilot Management

**Portal Path:** Microsoft 365 Admin Center > Copilot

1. Navigate to [M365 Admin Center](https://admin.microsoft.com)
2. Select **Copilot** in left navigation
3. Review the five navigation sections

---

### Step 2: Review Copilot Navigation Structure

| Section | Path | Purpose |
|---------|------|---------|
| **Overview** | Copilot > Overview | Copilot Control System dashboard |
| **Connectors** | Copilot > Connectors | External data connections |
| **Search** | Copilot > Search | Bookmarks and acronyms |
| **Billing & usage** | Copilot > Billing & usage | Pay-as-you-go policies |
| **Settings** | Copilot > Settings | Comprehensive configuration |

---

### Step 3: Configure Copilot Settings

**Portal Path:** M365 Admin Center > Copilot > Settings

Navigate through the four settings tabs:

**User Access Tab:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Self-service purchases | Disable |
| Copilot in Edge | Managed users only |
| Consumer Copilot access | Disable |

**Data Access Tab:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Web search for M365 Copilot | Disable for compliance |
| External AI providers | Block |
| Third-party LLM access | Block |
| Agents | Approval required |

**Copilot Actions Tab:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Image generation | Disable |
| Video generation | Disable |
| Teams meeting Copilot | Enable with retention |

---

### Step 3A: Configure AI Feature Access Control

!!! info "GA Feature"
    AI Feature Access Control settings are generally available and provide granular user-level and feature-level controls for Microsoft 365 Copilot.

**Portal Path:** M365 Admin Center > Copilot > Settings

Configure user-level feature access to manage Copilot availability by user, group, and compliance requirements:

#### 1. Create Admin Exclusion Group (Entra ID)

**Portal Path:** Microsoft Entra admin center > Groups > All groups > New group

1. Navigate to [Microsoft Entra admin center](https://entra.microsoft.com)
2. Select **Groups** > **All groups** > **New group**
3. Configure group:
   - **Group type:** Security
   - **Group name:** `CopilotForM365AdminExclude` (exact name required)
   - **Group description:** "Users excluded from Microsoft 365 Copilot access for compliance reasons"
   - **Membership type:** Assigned (or Dynamic if using attribute-based rules)
4. Click **Create**

**Add members to exclusion group:**

- Navigate to the newly created group > **Members** > **Add members**
- Select users or nested groups to exclude from Copilot access
- Common FSI populations:
  - Traders during blackout periods (temporary)
  - Employees under compliance investigation (temporary)
  - Restricted persons lists (permanent or semi-permanent)
  - Customer-facing roles during pilot phase (temporary)

**Zone-specific notes:**

- **Zone 1:** Admin Exclusion Groups typically not required for personal productivity agents
- **Zone 2:** Use for compliance-sensitive roles (e.g., traders on MNPI teams)
- **Zone 3:** Mandatory for traders, restricted persons, and roles under enhanced supervision per FINRA 3110

!!! warning "Propagation Delay"
    Admin Exclusion Group membership changes take up to **24 hours** to propagate. Plan additions/removals accordingly. Users will retain access until propagation completes.

#### 2. Configure User Access Settings

**Portal Path:** M365 Admin Center > Copilot > Settings > User access tab

1. Navigate to [M365 Admin Center](https://admin.microsoft.com)
2. Select **Copilot** > **Settings** > **User access** tab
3. Configure settings:
   - **Self-service purchases:** Set to "Disabled" (FSI recommendation: prevent shadow IT)
   - **Copilot in Edge:** Set to "Managed users only" (enforces organizational account usage)
   - **Consumer Copilot access:** Set to "Disabled" (prevents consumer account mixing)

**Zone-specific notes:**

- **Zone 3:** All settings must be "Disabled" or "Managed users only" to ensure organizational control

#### 3. Configure Deployment Groups for Staged Rollout

**Portal Path:** M365 Admin Center > Copilot > Settings > (check for Deployment tab or section)

1. In M365 Admin Center > Copilot > Settings, locate deployment group configuration
2. Create deployment groups aligned with rollout phases:

   **Pilot Deployment Group:**
   - Name: `Copilot-Pilot-IT-Compliance`
   - Members: IT staff, Compliance team, AI Governance Lead (10-50 users)
   - Duration: 4-6 weeks
   - Validation: Feature functionality, no compliance violations, positive feedback

   **Wave 1 Deployment Group:**
   - Name: `Copilot-Wave1-NonCustomerFacing`
   - Members: Non-customer-facing business units (100-500 users)
   - Duration: 8-12 weeks
   - Validation: Usage metrics healthy, DLP policies effective, no audit findings

   **Wave 2 Deployment Group:**
   - Name: `Copilot-Wave2-SupervisedCustomerFacing`
   - Members: Customer-facing roles with supervision (500-2000 users)
   - Duration: 12-16 weeks
   - Validation: Supervision workflows validated, regulatory reporting functional

   **Wave 3 (Full Rollout):**
   - All licensed users (excludes Admin Exclusion Group members)
   - Ongoing monitoring and quarterly compliance review

3. Assign users to appropriate deployment group based on current phase
4. Document group membership and phase transition approval process

**Zone-specific notes:**

- **Zone 1:** Deployment groups optional; useful for managing support load during large-scale rollout
- **Zone 2:** Recommended to validate team collaboration patterns before full enablement
- **Zone 3:** Mandatory; align deployment group phases with change control approval gates

#### 4. Configure Data Access Settings

**Portal Path:** M365 Admin Center > Copilot > Settings > Data access tab

1. Navigate to **Data access** tab
2. Configure settings:
   - **Web search for M365 Copilot:**
     - Zone 1: Enabled (personal productivity)
     - Zone 2: Disabled for MNPI teams (Material Non-Public Information protection)
     - Zone 3: Disabled organization-wide (GLBA 501(b): prevent external data leakage)
   - **External AI providers:** Set to "Block" (all zones)
   - **Third-party LLM access:** Set to "Block" (all zones)

**Zone-specific notes:**

- **Zone 3 (customer-facing):** Web search MUST be disabled to prevent inadvertent exposure of customer data to external search providers
- **MNPI environments:** Disable web search to comply with insider trading prevention controls

#### 5. Configure Actions Settings (Agent Access Control)

**Portal Path:** M365 Admin Center > Copilot > Settings > Actions tab

1. Navigate to **Actions** tab (previously "Copilot Actions")
2. Configure agent access controls:
   - **Allowed agent types:**
     - Zone 1: All agents allowed (Microsoft + Organizational + Verified third-party)
     - Zone 2: Organizational + Microsoft verified agents only
     - Zone 3: Organizational agents only, with approval workflow required (FINRA 4511)
   - **Image generation:** Disable (FSI recommendation for all zones)
   - **Video generation:** Disable (FSI recommendation for all zones)
   - **Teams meeting Copilot:** Enable with retention policies configured (align with FINRA 4511 books and records)

**Zone-specific notes:**

- **Zone 3:** Restrict agent access to pre-approved organizational agents only; require governance review before enabling any new agent capabilities

#### 6. Configure End-User Experience

**Portal Path:** M365 Admin Center > Copilot > Settings > (check for End-User Experience section)

1. Locate End-User Experience or similar settings section
2. Configure Copilot Chat pinning:
   - **Copilot Chat pinned in Teams:**
     - Zone 1: User preference
     - Zone 2: Enabled for collaboration teams
     - Zone 3: Controlled per department based on supervision requirements
   - **Copilot Chat pinned in Outlook:** Configure similarly based on zone

**Zone-specific notes:**

- **Zone 3:** Align pinning with supervision requirements — disable for unsupervised roles to reduce inadvertent AI usage without oversight

#### 7. Verify Settings Propagation

**After completing configuration:**

1. Allow **up to 8 hours** for settings to propagate across the tenant
2. Test with pilot users in each deployment group:
   - Sign in as user in deployment group → Verify Copilot access granted
   - Sign in as user NOT in deployment group → Verify Copilot access denied
   - Sign in as user in Admin Exclusion Group → Verify Copilot access denied (may take up to 24 hours)
3. Verify web search disabled (if configured):
   - Test Copilot chat with query requiring external data
   - Confirm response uses only organizational data, no web results
4. Document test results for compliance evidence

**Troubleshooting:**

- If settings not applying: Wait full 8-hour propagation window before escalating
- If Admin Exclusion not working: Verify group name exactly matches `CopilotForM365AdminExclude` (case-sensitive)
- If deployment group not limiting access: Verify group type is Security group, check license assignment

!!! tip "FSI Governance Best Practice"
    Create the Admin Exclusion Group and add all compliance-restricted users BEFORE enabling Copilot organization-wide. This prevents inadvertent access during the 24-hour propagation window.

---

## Part 2: M365 Admin Center - Agents Section

### Step 4: Access Agents Management

**Portal Path:** M365 Admin Center > Agents

1. Navigate to **Agents** in left navigation
2. Review the four navigation sections

---

### Step 5: Review Agents Overview Dashboard

**Portal Path:** M365 Admin Center > Agents > Overview

Key metrics to monitor:

| Metric | Description | Action |
|--------|-------------|--------|
| Agent registry count | Total agents | Track growth |
| Active users | Users interacting with agents | Monitor adoption |
| Pending requests | Agents awaiting approval | Review/approve |
| Ownerless agents | Agents without owner | Assign immediately |

---

### Step 6: Configure Agent Registry

**Portal Path:** M365 Admin Center > Agents > All agents > Registry

Review and filter agents by:

| Filter | Options |
|--------|---------|
| Publisher | Microsoft, External, Your organization |
| Availability | All users, Some users |
| Channel | Copilot, Teams, Outlook, M365 |
| Platform | M365 Copilot, Agent Builder, Other |

---

### Step 7: Manage MCP Servers (Tools)

**Portal Path:** M365 Admin Center > Agents > Tools

Review MCP Server availability:

| Action | When to Use |
|--------|-------------|
| Block server | Prevent specific data access |
| Allow server | Enable capabilities |

---

### Step 8: Configure Agent Settings

**Portal Path:** M365 Admin Center > Agents > Settings

| Setting | Description | FSI Action |
|---------|-------------|------------|
| Allowed agent types | Control agent sources | Restrict to approved |
| Sharing | Manage sharing scope | Limit appropriately |
| Templates | Pre-set governance policies | Create FSI templates |
| User access | Control agent interactions | Define by role |

---

## Part 3: PPAC Copilot Section

### Step 9: Access PPAC Copilot

**Portal Path:** Power Platform Admin Center > Copilot

1. Navigate to [PPAC](https://admin.powerplatform.microsoft.com)
2. Select **Copilot** in left navigation

---

### Step 10: Configure PPAC Copilot Settings

**Portal Path:** PPAC > Copilot > Settings

**Power Platform Settings:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Copilot feedback | Review before sending |
| Generative AI | Enable with monitoring |
| Preview AI models | Disable in production |

**Copilot Studio Settings:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Computer Use | Disable |
| Code generation | Controlled approval |
| External Models | Disable |
| Channel access | Internal only |

---

## Validation

After completing the configuration, verify:

1. [ ] M365 Admin Center Copilot Settings configured (User Access, Data Access, Copilot Actions)
2. [ ] Admin Exclusion Groups created and assigned to compliance-restricted users
3. [ ] Deployment groups configured for staged rollout
4. [ ] Feature access controls applied and propagated (allow 8 hours)
5. [ ] Agent registry displays all deployed agents with accurate metadata
6. [ ] PPAC Copilot Settings configured with FSI recommendations applied
7. [ ] Ownerless agents identified and assigned owners
8. [ ] AI Prompts toggle disabled in PPAC for Zone 2/3 environments
9. [ ] Generative Actions disabled for agents without documented approval
10. [ ] File Analysis disabled for agents without data classification review
11. [ ] Model Knowledge disabled for agents handling sensitive data
12. [ ] Semantic Search disabled for agents without approved and scoped knowledge bases
13. [ ] Conversational transcript access restricted to authorized personnel
14. [ ] DLP policies block agent publishing connectors in restricted environments

**Expected Result:** Copilot and Agent governance dashboards provide visibility into agent deployments, settings enforce organizational policies, and AI feature toggles are governed per zone requirements.

---

## Part 4: PPAC Copilot Studio AI Feature Controls

### Step 11: Configure AI Feature Toggles Per Environment

**Portal Path:** PPAC > Environments > [Select Environment] > Settings > Product > Features

1. Navigate to the environment settings in PPAC
2. Review and configure each AI feature toggle:

| Toggle | Action for Zone 2/3 |
|--------|---------------------|
| **AI Prompts** | Set to **Off** unless approved |

3. Select **Save**

### Step 12: Configure Per-Environment Generative AI Features

**Portal Path:** PPAC > Environments > [Select Environment] > Generative AI features

1. Navigate to the environment's Generative AI features page
2. Review and configure each feature:

| Feature | Action for Zone 2/3 |
|---------|---------------------|
| **Generative AI features** | Restrict by default |
| **Move Data Across Regions** | Set to **Off** |
| **Bing Search** | Set to **Off** |
| **Microsoft 365 Services** | Review with compliance before enabling |

3. Select **Save**

### Step 13: Configure Agent-Level AI Settings (Copilot Studio)

1. Open **Copilot Studio** ([https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com))
2. For each agent in Zone 2/3 environments:
   - Go to **Overview** > **Orchestration** > disable **Generative Actions** toggle
   - Go to **Settings** > **Generative AI** > disable **File processing** toggle
   - Go to **Settings** > **Generative AI** > disable **Use model knowledge** toggle
   - Go to **Settings** > **Generative AI** > disable **Use semantic search** toggle
3. Enable any of these only with:
   - Documented business justification
   - Data classification review
   - Risk assessment with mitigating controls
   - Compliance officer sign-off
   - Quarterly re-attestation

### Step 14: Configure Conversational Transcript Access

**Portal Path:** PPAC > Environments > [Select Environment] > Settings > Product > Features > Copilot Studio Agents

1. Navigate to the environment's Features settings
2. Under **Copilot Studio Agents**, configure transcript access controls
3. Restrict access to authorized personnel only (compliance, governance, security teams)

### Step 15: Configure DLP for Agent Publishing Connectors

1. In PPAC, navigate to **Data policies**
2. Select or create a DLP policy for the target environment
3. Block the following connectors in environments where agent publishing should be restricted:
   - **Copilot Studio for Microsoft Teams**
   - **M365 Copilot channel**
4. Select **Save**
5. See [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) for comprehensive DLP policy configuration

---

[Back to Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: February 2026 | Version: v1.3*
