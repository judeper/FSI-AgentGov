# Control 3.8: Copilot Hub and Governance Dashboard — Portal Walkthrough

> Step-by-step portal configuration guidance for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md). Use this playbook to configure the Microsoft 365 Admin Center Copilot Hub, the Agents page, and the Power Platform Admin Center (PPAC) Copilot section in line with FSI governance requirements.

!!! warning "UI Drift Warning (April 2026)"
    Microsoft is actively restructuring the Copilot Hub surfaces (Security pivot, Readiness page, product pages, Agent overview GA on **May 1, 2026**). Portal labels and navigation paths shown below were verified in **April 2026**. If a label has moved, search the [Microsoft 365 Roadmap](https://www.microsoft.com/en-us/microsoft-365/roadmap) and your tenant Message Center before assuming the control is broken. Hedged regulatory language is required throughout — these settings **support** compliance; they do not guarantee it.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **AI Administrator** role (preferred) | Sufficient for Copilot Settings, feature access, deployment groups, Admin Exclusion Groups, agent registry review. Aligns with FINRA 3110 / SOX 404 least-privilege guidance. |
| **Entra Global Admin** role | Required only for initial tenant setup, broad Graph API consent, billing changes, and creating the `CopilotForM365AdminExclude` security group. Use Entra PIM for just-in-time elevation. |
| **Power Platform Admin** role | Required for PPAC Copilot Studio settings, environment-level generative AI features, and tenant DLP policies. |
| Microsoft 365 Copilot licensing | Required for the Copilot Hub surfaces to render. |
| (Optional) Agent 365 or M365 E7 per-user licensing | Required to view Agent overview hero metrics at GA on May 1, 2026. |

> Capture the role assignments used for each step in your change ticket — examiners commonly request role-evidence under SOX 404 and OCC 2011-12.

---

## Part 1 — Microsoft 365 Admin Center: Copilot Section

### Step 1. Open the Copilot Hub

**Portal Path:** [Microsoft 365 Admin Center](https://admin.microsoft.com) → **Copilot**

1. Sign in with the AI Administrator role (preferred) or Entra Global Admin (initial setup only).
2. Confirm the five hub sections render: **Overview**, **Connectors**, **Search**, **Billing & usage**, **Settings**.
3. If the **Security** pivot is visible on the Overview page, confirm MC1187780 has rolled out to your tenant.

### Step 2. Inspect the Readiness page (post MC1187780)

**Portal Path:** Copilot → **Overview** → **Readiness**

Confirm the three categories render and capture a screenshot of each for evidence:

| Category | What to verify |
|---|---|
| **Deployment Essentials** | License assignment counts, user enablement status, rollout planning view |
| **End-User Experience** | Web search state, plug-in policy, agent access, personalization |
| **Data Security** | DLP policies, sensitivity label coverage, audit configuration |

Note the **Chat Active Users**, **Assisted Hours**, and **Satisfaction Rate** metrics — these are the supervision signals you will export monthly under FINRA 4511 / 25-07.

### Step 3. Configure Copilot Settings — User Access tab

**Portal Path:** Copilot → **Settings** → **User access**

| Setting | FSI Recommendation | Rationale |
|---|---|---|
| Self-service purchases | **Disabled** | Prevents shadow IT licensing; supports SOX 404 change control |
| Copilot in Edge | **Managed users only** | Forces organizational identity; helps meet GLBA 501(b) |
| Consumer Copilot access | **Disabled** | Blocks consumer-account spillover; supports FINRA 3110 supervision |

> Zone 3: every setting in this tab must be Disabled or Managed-users-only before sign-off.

### Step 4. Configure Admin Exclusion Group

**Portal Path:** [Microsoft Entra admin center](https://entra.microsoft.com) → **Groups** → **All groups** → **New group**

1. Group type: **Security**
2. Group name: **`CopilotForM365AdminExclude`** (case-sensitive — exact match required)
3. Description: "Users excluded from Microsoft 365 Copilot admin-center features for compliance reasons."
4. Membership type: Assigned (or Dynamic if attribute-driven and reviewed by Compliance).
5. Add members representative of the FSI populations below.

| Population | Driver | Duration |
|---|---|---|
| Traders during blackout | SEC Reg FD, insider-trading prevention | Temporary |
| Employees under investigation | FINRA 3110 enhanced supervision | Investigation duration |
| Restricted-persons list | FINRA 2111 conflict management | Permanent / semi-permanent |
| Customer-facing pilot exclusions | Risk management during rollout | Temporary |

!!! warning "Propagation"
    Membership changes take **up to 24 hours** to take effect. Plan additions/removals accordingly. The exclusion governs **admin-center** Copilot features; end-user Copilot in Word/Excel/Teams requires separate license or policy controls.

### Step 5. Configure Deployment Groups for Staged Rollout

**Portal Path:** Copilot → **Settings** → Deployment section (label may vary post-MC1187780)

Create one Entra security group per wave and add it to the deployment configuration:

| Wave | Group Name (suggested) | Population | Duration |
|---|---|---|---|
| Pilot | `Copilot-Pilot-IT-Compliance` | IT, Compliance, AI Governance Lead (10–50 users) | 4–6 weeks |
| Wave 1 | `Copilot-Wave1-NonCustomerFacing` | Non-customer-facing BUs (100–500 users) | 8–12 weeks |
| Wave 2 | `Copilot-Wave2-SupervisedCustomerFacing` | Customer-facing with supervision (500–2 000 users) | 12–16 weeks |
| Wave 3 | `Copilot-Wave3-Production` | All licensed users excluding Admin Exclusion Group | Ongoing |

Document the wave-transition approval gate (compliance review, DLP effectiveness, audit findings) in your change ticket.

### Step 6. Configure Copilot Settings — Data access tab

**Portal Path:** Copilot → **Settings** → **Data access**

| Setting | Zone 1 | Zone 2 | Zone 3 | Regulatory Driver |
|---|---|---|---|---|
| Web search for M365 Copilot | Enabled | Disabled for MNPI teams | **Disabled tenant-wide** | GLBA 501(b); MNPI controls |
| External AI providers | Block | Block | Block | FINRA 3110, FINRA 4511 |
| Third-party LLM access | Block | Block | Block | FINRA 4511, SEC 17a-4 |

### Step 7. Configure Copilot Settings — Actions tab

**Portal Path:** Copilot → **Settings** → **Actions**

| Setting | Zone 1 | Zone 2 | Zone 3 |
|---|---|---|---|
| Allowed agent types | All allowed | Organizational + Microsoft verified | Organizational only, approval workflow required |
| Image generation | Disabled | Disabled | Disabled |
| Video generation | Disabled | Disabled | Disabled |
| Teams meeting Copilot | Enable with retention | Enable with retention | Enable with retention (FINRA 4511 books and records) |

### Step 8. Verify settings propagation

After saving the four tabs:

1. Allow **up to 8 hours** for tenant-wide propagation.
2. Sign in as a deployment-group member → confirm Copilot access.
3. Sign in as a non-member → confirm access is denied.
4. Sign in as an Admin Exclusion Group member → confirm admin-center Copilot features are unavailable (allow up to 24 hours for the exclusion to take effect).
5. Capture screenshots and timestamps for the change ticket.

---

## Part 2 — Microsoft 365 Admin Center: Agents Section

### Step 9. Review the Agent overview page

**Portal Path:** Microsoft 365 Admin Center → **Agents** → **Overview**

| Hero metric | Action |
|---|---|
| Agent registry count | Reconcile against approved-agent inventory (Control 1.2) |
| Active users | Track adoption and report monthly |
| Pending requests | Triage within governance SLA |
| Ownerless agents | Assign owner within **14 days** (FINRA 3110 supervisory ownership) |

> Hero metrics for Agent Builder, SharePoint agents, M365 Agents Toolkit, and Agent 365 Observability SDK–instrumented agents reach GA on **May 1, 2026** with Agent 365 or M365 E7 licensing. Document coverage gaps for unsupported agent types in your monthly governance review.

### Step 10. Review the Agent Registry

**Portal Path:** Agents → **All agents** → **Registry**

Filter by Publisher, Availability, Channel, and Platform. Export the registry monthly and reconcile against:

- Control 1.2 Agent Registry inventory.
- Control 1.1 publishing-authorization approvals.
- Pending governance approvals.

### Step 11. Govern MCP Servers (Tools)

**Portal Path:** Agents → **Tools**

Block any MCP server not on the approved-data-access list. The April 2026 preview adds custom MCP servers — extend monthly review scope when these are enabled in your tenant.

### Step 12. Configure Agent Settings

**Portal Path:** Agents → **Settings**

| Setting | FSI action |
|---|---|
| Allowed agent types | Restrict to approved publishers per zone |
| Sharing | Limit to approved scope; complement with Unrestricted Agent Sharing Detector |
| Templates | Create FSI-approved templates that pre-set governance defaults |
| User access | Define by role; align with deployment groups |

---

## Part 3 — Power Platform Admin Center: Copilot Section

### Step 13. Open PPAC Copilot

**Portal Path:** [Power Platform Admin Center](https://admin.powerplatform.microsoft.com) → **Copilot**

### Step 14. Configure PPAC Copilot Settings

**Portal Path:** PPAC → **Copilot** → **Settings**

| Setting | FSI Recommendation |
|---|---|
| Copilot feedback | Review before sending to Microsoft |
| Generative AI | Enable with monitoring |
| Preview AI models | **Disabled** in production environments |

**Copilot Studio:**

| Setting | FSI Recommendation |
|---|---|
| Computer Use | **Disabled** (introduces autonomous browser actions) |
| Code generation | Approval-gated |
| External Models | **Disabled** |
| Channel access | Internal channels only for Zone 3 |

---

## Part 4 — PPAC Copilot Studio AI Feature Toggles

### Step 15. Configure tenant-level AI feature toggles

**Portal Path:** PPAC → **Copilot** → **Settings** *(previously Environments → [env] → Settings → Product → Features)*

| Toggle | Zone 2/3 action |
|---|---|
| AI Prompts | **Off** unless approved |

### Step 16. Configure per-environment Generative AI features

**Portal Path:** PPAC → **Environments** → [select environment] → **Generative AI features**

| Feature | Zone 2/3 action |
|---|---|
| Generative AI features | Restrict by default |
| Move Data Across Regions | **Off** (data residency) |
| Bing Search | **Off** (external grounding) |
| Microsoft 365 Services | Compliance review before enabling |

### Step 17. Configure agent-level AI settings (Copilot Studio)

For each agent in Zone 2/3 environments, open [Copilot Studio](https://copilotstudio.microsoft.com) and disable:

- **Overview → Orchestration → Generative Actions**
- **Settings → Generative AI → File processing**
- **Settings → Generative AI → Use model knowledge**
- **Settings → Generative AI → Use semantic search**

Enable any of these only with: documented business justification, data classification review, risk assessment with mitigating controls, Compliance Officer sign-off, and quarterly re-attestation.

### Step 18. Restrict transcript access

**Portal Path:** PPAC → **Copilot** → **Settings** *(transcript controls; previously under Environment → Features → Copilot Studio Agents)*

Restrict transcript access to Compliance Officers and designated Supervisors. Apply separation of duties — agent creators must not access transcripts for agents they built (FINRA 3110). See the control document section "Conversational Transcript Access Governance" for the full role matrix.

### Step 19. DLP for Agent Publishing Connectors

**Portal Path:** PPAC → **Policies** → **Data policies**

In any environment where agent publishing should be restricted, block:

- **Copilot Studio for Microsoft Teams**
- **M365 Copilot channel**

See [Control 1.5 — Data Loss Prevention](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) for full DLP policy authoring guidance.

---

## Validation Checklist

| # | Item | Where verified |
|---|---|---|
| 1 | Copilot Settings configured across all four tabs | M365 Admin → Copilot → Settings |
| 2 | `CopilotForM365AdminExclude` group created with correct name and members | Entra → Groups |
| 3 | Deployment groups created and assigned per wave | M365 Admin → Copilot → Settings |
| 4 | Feature access propagated (≤ 8 hours) and tested | Test sign-in evidence |
| 5 | Agent registry reconciled against approved inventory | M365 Admin → Agents → Registry |
| 6 | PPAC Copilot Settings configured per FSI defaults | PPAC → Copilot → Settings |
| 7 | Ownerless agents assigned within 14 days | M365 Admin → Agents → Overview |
| 8 | AI Prompts toggle Off (Zone 2/3) | PPAC → Copilot → Settings |
| 9 | Generative Actions Off without documented approval | Copilot Studio → Agent → Orchestration |
| 10 | File Analysis Off without classification review | Copilot Studio → Agent → Settings → Generative AI |
| 11 | Model Knowledge Off for sensitive-data agents | Copilot Studio → Agent → Settings → Generative AI |
| 12 | Semantic Search Off without scoped knowledge bases | Copilot Studio → Agent → Settings → Generative AI |
| 13 | Move Data Across Regions / Bing Search Off | PPAC → Environments → Generative AI features |
| 14 | Transcript access restricted to Compliance roles | PPAC → Copilot → Settings |
| 15 | DLP blocks agent publishing connectors in restricted environments | PPAC → Policies → Data policies |

**Expected outcome:** Copilot Hub and Agent governance surfaces provide the visibility needed for monthly supervision evidence, and AI feature toggles are governed per zone. These settings **support** FINRA 4511 / 25-07, SEC 17a-3/4, GLBA 501(b), and SOX 404 obligations; they do not by themselves constitute compliance.

---

[Back to Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
