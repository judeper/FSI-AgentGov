# Sponsorship Lifecycle Workflows

> Supplemental playbook for [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md). This document specifies the **human accountability layer** that wraps every Microsoft 365 AI agent: the named sponsors, owners, backup owners, and compliance reviewers who carry regulatory responsibility for the agent across its lifecycle, and the Microsoft Entra ID Governance / Power Platform automation that makes that accountability machine-enforceable.
>
> Companion playbooks (do **not** duplicate content from these — link to them):
>
> - [Portal Walkthrough](./portal-walkthrough.md) — registry portal configuration
> - [PowerShell Setup](./powershell-setup.md) — registry automation
> - [Verification Testing](./verification-testing.md) — registry test cases
> - [Troubleshooting](./troubleshooting.md) — registry common issues
>
> Cross-control dependencies:
>
> - [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — authoritative lifecycle state machine
> - [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — sponsor signature capture and retention
> - [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — sponsor approval correspondence supervision
> - [Control 2.1 implementation playbooks](../2.1/portal-walkthrough.md) — DSPM for AI alerting that escalates to sponsors
> - [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) — sponsor on-call obligations during incidents

---

## 1. Overview

Human sponsorship is a foundational requirement for Agentic Users in Microsoft Entra ID and a core supervisory expectation under FINRA Rule 3110, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), and Federal Reserve SR 26-2 (formerly SR 11-7). An AI agent without a named, attested, currently employed sponsor is — for examination purposes — an **unsupervised system**, and the residual risk of unsupervised automation in a regulated FSI environment is the central concern this playbook addresses.

This playbook provides:

1. The **four sponsorship roles** (Agent Sponsor, Agent Owner, Backup Owner, Compliance Reviewer) with duties, authority boundaries, and escalation paths.
2. The **lifecycle integration** that aligns sponsor approvals with the [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) state machine (Draft → In Review → Approved → Active → Deprecated → Decommissioned).
3. **Zone-differentiated sponsorship requirements** (Z1 informal, Z2 sponsor + backup mandatory, Z3 dual sponsor + backup + compliance).
4. **Attestation cadence** (quarterly sponsor signature, annual external compliance review) with a working calendar.
5. The **departed sponsor / owner cascade workflow** including manager-hierarchy fallback, AI Governance Lead escalation, and the emergency Decommissioned transition.
6. **Approval workflow integration** unifying Entra admin consent, Entra agent approval, and Power Platform agent approval into a single signature flow.
7. The **sponsorship evidence pack** specifying every artifact captured per attestation, including SHA-256 hash chaining for tamper-evidence.
8. **Examiner readiness framing** mapping each artifact to specific regulations.

!!! note "Preview features as of April 2026"
    Microsoft Entra Agent ID, Agentic User accounts, and Power Platform agent approval centers remain in preview or staged GA in many regions. Lifecycle Workflows for Agentic Users have a narrower task catalog than for human users; several integrations in this playbook depend on custom extensions (Logic Apps or Azure Functions) that organizations must deploy. Verify feature availability in your tenant before implementation.

!!! warning "Language and liability"
    This playbook helps meet — and is required for — supervisory expectations across FINRA, SEC, OCC, Federal Reserve, NYDFS, and FTC Safeguards regimes. It does **not** by itself constitute compliance. Implementation requires legal, compliance, and risk review tailored to your firm's business activities and regulatory profile. Organizations should verify every assertion against their own examination history.

---

## 2. Examiner Readiness Framing

Sponsorship is the artifact examiners look for first when evaluating AI agent governance. Each of the four sponsorship roles in this playbook maps to specific regulatory expectations:

| Regulation | Expectation | How sponsorship supports it |
|---|---|---|
| **FINRA Rule 3110** (Supervision) | Written supervisory procedures with named supervisors | Agent Sponsor is the named supervisor of record for the agent's business use; quarterly attestation produces the written evidence |
| **FINRA Rule 4511** (Books and Records) | Preservation of supervisory records in non-erasable, non-rewriteable form | Sponsorship evidence pack (Section 12) captures attestation in WORM-eligible form |
| **FINRA Notice 25-07** (Generative AI) | Member firms remain responsible for compliance regardless of AI use; supervisory framework must address gen-AI specifically | Sponsor attestation explicitly references gen-AI risk categories (hallucination, inappropriate disclosure, unauthorized advice) |
| **SEC Rule 17a-4(b)(4)** | Retention of supervisory communications | Sponsor approval correspondence supervised under [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) and retained 7 years |
| **SOX §302/§404** | Officer certification of internal controls; ICFR effectiveness | Compliance Reviewer sign-off feeds quarterly ICFR attestation packages for any Z3 agent touching financial reporting |
| **GLBA §501(b) / FTC Safeguards 16 CFR §314.4(c)** | Designated qualified individual; access controls; monitoring | Agent Owner is the designated technical custodian; attestation cadence aids continuous monitoring |
| **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** (Model Risk Management) | Identified model owner; effective challenge; ongoing monitoring | Agent Owner = model owner of record; Compliance Reviewer performs effective challenge for Z3 agents |
| **Federal Reserve SR 26-2 (formerly SR 11-7)** (Model Risk) | Model inventory with accountable parties; lifecycle controls | Sponsorship metadata feeds the Control 3.1 inventory; lifecycle approvals (Section 5) are the documented control points |
| **NYDFS Part 500.07 / 500.16** (Access privileges; Incident response) | Documented access governance; defined incident roles | Backup Owner provides 24×7 incident reachability; departure cascade (Section 9) prevents orphaned privileged identity |
| **NIST AI RMF GOVERN 1.4 / 1.6** | Roles, responsibilities, and lines of communication for AI risk | Section 3 role definitions are the framework's GOVERN 1.4/1.6 evidence |

!!! tip "What an examiner asks"
    "Show me the named supervisor for *this* agent, the date of their most recent attestation, the evidence package supporting that attestation, and what happens if that supervisor leaves the firm." Every section of this playbook helps you answer that question in under five minutes.

---

## 3. Sponsorship Role Definitions

The framework defines **four** sponsorship roles. Every agent — regardless of zone — must have at minimum an Agent Owner. Higher zones layer on Sponsor, Backup Owner, and Compliance Reviewer.

### 3.1 Agent Sponsor (Business Accountability)

**Role summary.** The named business executive who is *accountable* for the agent's existence, business value, and risk acceptance. The Sponsor is the person an examiner, auditor, or board committee will name when asking "who decided this AI agent should operate?"

**Required role / seniority.**

| Zone | Minimum seniority | Common titles |
|---|---|---|
| Z1 (Personal) | Not required | n/a — Owner-only model |
| Z2 (Team) | Manager (P5/M3 or equivalent) | Line of business manager, Director |
| Z3 (Enterprise) | Director or above; for agents touching financial reporting, customer funds, trading, or fiduciary advice: Managing Director / Executive Officer | LOB Head, Chief Risk Officer designate, Chief Compliance Officer designate |

**Duties.**

1. Authorize the initial business case and risk acceptance for the agent.
2. Approve every transition from Draft → In Review → Approved → Active (see Section 5).
3. Sign quarterly attestation that the agent (a) remains required, (b) operates within scope, (c) has had no unmitigated incidents.
4. Designate the Agent Owner and Backup Owner.
5. Acknowledge material configuration changes (scope, data sources, sensitivity labels).
6. Authorize Decommissioned transitions.

**Authority boundaries.**

- **MAY** approve Active operation of the agent within its registered scope.
- **MAY** authorize temporary scope changes up to the approved zone ceiling.
- **MAY NOT** approve zone elevation (Z2 → Z3) without dual sponsor + Compliance Reviewer.
- **MAY NOT** waive [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) audit logging or DSPM for AI policies.
- **MAY NOT** approve an agent for which they are also the Agent Owner (separation of duties for Z2/Z3).

**Escalation path.** Sponsor unreachable >5 business days → Backup Owner notifies Sponsor's manager → unresolved at 10 business days → AI Governance Lead → unresolved at 15 business days → emergency Decommissioned transition (Section 9.4).

---

### 3.2 Agent Owner (Technical Accountability)

**Role summary.** The named technical custodian responsible for the agent's configuration, monitoring, and day-to-day operation. The Agent Owner is the OCC Bulletin 2026-13 (formerly OCC 2011-12) "model owner" of record.

**Required role / seniority.**

| Zone | Minimum profile | Required training |
|---|---|---|
| Z1 | The user themselves (self-owned) | Recommended: AI Acceptable Use module |
| Z2 | Identified individual or shared mailbox-backed team alias mapped to ≥2 named technical staff | Required: Microsoft Copilot Studio Maker fundamentals; Acceptable Use |
| Z3 | Named individual technical lead with backup | Required: Copilot Studio Maker fundamentals; FSI Agent Governance certification; tabletop incident response participation in last 12 months |

**Duties.**

1. Build, configure, and maintain the agent in Microsoft 365 Admin Center, Copilot Studio, Power Platform, or Agent 365.
2. Operate the agent within the scope authorized by the Sponsor.
3. Triage and respond to alerts from [Control 2.1](../2.1/portal-walkthrough.md) (DSPM for AI), [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), and Defender XDR within the Zone SLA.
4. Maintain Control 3.1 inventory metadata (data sources, connectors, sensitivity, business owner).
5. Execute the technical work authorized by the Sponsor's quarterly attestation (e.g., decommission, scope change).
6. Co-sign material configuration changes with the Sponsor.

**Authority boundaries.**

- **MAY** make non-material configuration changes (UI/prompt copy, intent expansions within registered topics).
- **MAY NOT** add new data sources, connectors, or sensitivity-labeled content scopes without Sponsor approval.
- **MAY NOT** disable logging, audit, DSPM for AI, or Communication Compliance scoping.
- **MAY NOT** sign their own quarterly attestation — separation from Sponsor required for Z2/Z3.

**Escalation path.** Agent Owner unreachable >2 business days → Backup Owner assumes operational control automatically (Section 9.1) → if Owner status not resolved within 10 business days, the cascade workflow promotes Backup Owner to Agent Owner and Sponsor must designate a new Backup Owner within 5 additional business days.

---

### 3.3 Backup Owner (Continuity)

**Role summary.** Named secondary technical custodian who provides operational continuity when the Agent Owner is unavailable, departs, or is reassigned. Mandatory for Z2 and Z3.

**Required role / seniority.** Same profile as Agent Owner; **must not** report to the Agent Owner (independent reporting line for Z3 to maintain effective challenge per OCC Bulletin 2026-13 (formerly OCC 2011-12)).

**Duties.**

1. Maintain operational read access to the agent and its supporting infrastructure at all times.
2. Receive duplicate copies of all alerts routed to the Agent Owner.
3. Assume Agent Owner authority automatically per the cascade rules in Section 9.
4. Participate in at least one tabletop incident exercise per year (Z3 only).
5. Acknowledge quarterly attestation (witness signature, not approver).

**Authority boundaries.**

- **MAY** execute any action the Agent Owner may execute, but only after activation per Section 9.1.
- **MAY NOT** make material changes during routine periods (Owner present) without Owner consent.

---

### 3.4 Compliance Reviewer (Regulatory Sign-Off)

**Role summary.** Named compliance officer who provides independent regulatory review for Z3 agents and any agent processing customer non-public personal information (NPPI), MNPI, supervised electronic communications, or material relating to investment advice.

**Required role / seniority.** Designated officer within the Compliance department holding the **Purview Compliance Admin** or **Purview Compliance Reader** Entra role plus written delegated authority from the Chief Compliance Officer.

**Duties.**

1. Sign off on initial Z3 agent risk assessment (In Review → Approved transition).
2. Co-sign quarterly Sponsor attestation for Z3 agents.
3. Conduct annual external compliance review — independent of Sponsor and Owner — producing a written assessment that feeds the firm's annual 3120 / Reg BI / Advisers Act compliance review.
4. Authorize releases that change the agent's regulatory footprint (new data class, new jurisdiction, new customer-facing capability).
5. Require Decommissioned transition for any agent that materially deviates from approved scope and cannot be remediated.

**Authority boundaries.**

- **MAY** veto any Approved or Active transition for a Z3 agent on regulatory grounds.
- **MAY** require an immediate move to Decommissioned for Section 9.4 emergency cases.
- **MAY NOT** also serve as Agent Owner or Sponsor for the same agent.

---

### 3.5 Role Separation Matrix

| Role pair | Z1 | Z2 | Z3 |
|---|---|---|---|
| Sponsor = Owner | Allowed (no formal sponsor) | **Prohibited** | **Prohibited** |
| Owner = Backup Owner | Allowed (no backup) | **Prohibited** | **Prohibited** |
| Sponsor = Compliance Reviewer | n/a | n/a | **Prohibited** |
| Owner reports to Sponsor | Allowed | Allowed | Allowed |
| Backup Owner reports to Owner | Allowed | Allowed | **Prohibited** |
| Compliance Reviewer reports to Sponsor | n/a | n/a | **Prohibited** |

---

## 4. Zone-Specific Sponsorship Requirements

This expands the registry-level zone matrix from Control 1.2 with sponsorship-specific rules. All sponsor / owner identities are persisted as Entra ID extension attributes on the Agentic User and mirrored to the Control 3.1 Dataverse inventory.

| Requirement | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---|---|---|---|
| **Agent Sponsor** | Not required (owner self-sponsors) | Required: Manager+ | Required: Director+ (MD/EO for fiduciary scope) |
| **Agent Owner** | The user (self) | Named individual or 2-person team alias | Named individual + tabletop-trained |
| **Backup Owner** | Optional | **Mandatory** | **Mandatory** (separate reporting line) |
| **Compliance Reviewer** | Not required | Not required (recommended for regulated functions) | **Mandatory** |
| **Dual Sponsor approval** | n/a | n/a | **Required** for In Review → Approved |
| **Maximum agents per Sponsor** | n/a | 25 | 10 |
| **Maximum agents per Owner** | 10 | 5 | 3 |
| **Sponsor training** | n/a | Recommended: governance overview | Required: FSI Agent Governance certification + annual refresh |
| **Owner training** | Recommended: AUP module | Required: Maker fundamentals + AUP | Required: certification + tabletop participation |
| **Quarterly attestation** | Optional self-affirmation | Sponsor signature required | Sponsor + Compliance co-signature required |
| **Annual external review** | Not required | Spot-check sample (≥10%) | **100%** of Z3 agents |
| **Activity review cadence** | Self-monitor | Monthly summary to Sponsor | Weekly summary; alert-driven escalation |
| **Departure grace period** | 30 days then auto-suspend | 14 days then auto-suspend | **0 days** — immediate Decommissioned transition pending reassignment |
| **Approval workflow** | Self-approve | Single-stage Sponsor approval | Dual Sponsor + Compliance gate |

!!! warning "Z3 agents touching customer NPPI, MNPI, or fiduciary advice"
    For Z3 agents whose scope includes customer non-public personal information (GLBA), material non-public information, fiduciary investment advice (Advisers Act / Reg BI), or trading operations, the Sponsor must hold a **registered principal** designation under FINRA Rule 1220 where applicable. Verify with Compliance before authorizing the In Review → Approved transition.

---

## 5. Lifecycle Integration

This section binds sponsorship signatures to the [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) lifecycle state machine. Each transition has a required signature set, a captured evidence artifact, and a hash-chained audit record (Section 12).

### 5.1 State Machine Overview

```
   ┌────────┐  Owner submits   ┌──────────┐  Sponsor +     ┌──────────┐
   │ Draft  │ ───────────────► │In Review │  Compliance ──►│ Approved │
   └────────┘                  └──────────┘  (Z3) sign     └─────┬────┘
                                                                 │ Sponsor
                                                                 │ activate
                                                                 ▼
   ┌──────────────┐  Owner+Sponsor    ┌────────────┐ Sponsor   ┌────────┐
   │Decommissioned│◄──── decommission│ Deprecated │◄─ deprecate│ Active │
   └──────────────┘                   └────────────┘            └────────┘
            ▲                                                        │
            └────── emergency cascade (Section 9.4) ─────────────────┘
```

### 5.2 Required Signatures Per Transition

| Transition | Z1 signatures | Z2 signatures | Z3 signatures | Evidence captured |
|---|---|---|---|---|
| `→ Draft` (creation) | Owner | Owner | Owner | Initial registration record |
| `Draft → In Review` | Owner self-submit | Owner submit | Owner submit | Submission timestamp, intended scope |
| `In Review → Approved` | n/a (Z1 skips) | Sponsor | **Sponsor + 2nd Sponsor + Compliance Reviewer** | Risk assessment, approval record, dual approval chain |
| `Approved → Active` | Owner | Owner + Sponsor witness | Owner + Sponsor co-sign | Activation timestamp, configuration baseline hash |
| `Active → Active` (material change) | Owner | Owner + Sponsor | Owner + Sponsor + Compliance Reviewer | Change record, before/after config diff |
| `Active → Deprecated` | Owner | Sponsor | Sponsor + Compliance Reviewer | Deprecation rationale, sunset timeline |
| `Deprecated → Decommissioned` | Owner | Owner + Sponsor | Owner + Sponsor + Compliance Reviewer | Final activity export, identity revocation evidence |
| `* → Decommissioned` (emergency) | Owner or AI Governance Lead | AI Governance Lead | AI Governance Lead + on-call Compliance | Incident reference, emergency cascade record (Section 9.4) |

### 5.3 Material Change Definition

A configuration change is **material** (and therefore requires the signatures in row 5 above) when it does any of:

- Adds a new data source, connector, or knowledge index.
- Changes the agent's sensitivity-label scope.
- Adds an agent action with write-back to a system of record.
- Expands the agent to a new audience security group.
- Crosses a jurisdictional boundary (e.g., adds an EEA or APAC user audience).
- Touches customer NPPI, MNPI, or supervised-communications scope.

Non-material changes (UI copy, prompt refinements within registered topics, minor performance tuning) are owner-only and logged for the next quarterly attestation review.

### 5.4 Lifecycle Workflow Implementation

The technical Entra Lifecycle Workflows that drive the state transitions appear in Sections 7–9. The state attribute is persisted on the Agentic User as `extension_LifecycleState` and mirrored to the Control 3.1 Dataverse table `agt_AgentInventory.statecode`.

---

## 6. Attestation Cadence

### 6.1 Calendar

| Cadence | Activity | Performed by | Evidence |
|---|---|---|---|
| **Daily** | Automated DSPM for AI alert review | Agent Owner (or Backup) | Alert disposition log |
| **Weekly (Z3)** | Activity summary review | Agent Owner; Sponsor receives digest | Sponsor digest acknowledgment |
| **Monthly (Z2)** | Activity summary review | Agent Owner; Sponsor receives digest | Sponsor digest acknowledgment |
| **Quarterly** | Sponsor attestation (Q1: Apr 15 / Q2: Jul 15 / Q3: Oct 15 / Q4: Jan 15) | Sponsor sign; Owner + Backup Owner co-acknowledge; Compliance Reviewer co-sign for Z3 | Signed attestation artifact (Section 12) |
| **Semi-annual** | Backup Owner reachability test | AI Governance team | Test result log |
| **Annual** | External compliance review — Z3 100%, Z2 ≥10% sample | Compliance Reviewer; independent of Sponsor and Owner | Written review report retained 7 years |
| **Annual** | Sponsor and Owner training refresh | Learning & Development | Completion records |
| **Triggered** | On material change (Section 5.3) | Sponsor + Compliance (Z3) | Change attestation record |
| **Triggered** | On Sponsor / Owner / Backup departure | Cascade workflow (Section 9) | Cascade execution record |

### 6.2 Quarterly Attestation Procedure

The quarterly attestation is the workhorse evidence artifact examiners request first. It must be:

1. **Initiated** automatically by the `FSI-Quarterly-Sponsor-Attestation` workflow (Section 7.2) on the cycle date.
2. **Reviewed** by the Sponsor against the auto-generated activity pack (last 90 days of agent activity, alerts, material changes, NPPI exposure summary).
3. **Signed** within 14 calendar days of initiation. Late attestations escalate per Section 9.
4. **Co-signed** by Compliance Reviewer for Z3 within 7 additional days.
5. **Archived** to the WORM-eligible store under Control 1.7 retention rules with SHA-256 chain (Section 12).

### 6.3 Annual External Review

The annual review is a **separate** activity from quarterly attestation. The Compliance Reviewer evaluates each Z3 agent against:

- FINRA Notice 25-07 supervisory expectations for gen-AI.
- Reg BI / Advisers Act applicability where the agent influences customer recommendations.
- OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) effective challenge: was the model challenged by an independent party in the last 12 months?
- DSPM for AI policy alignment: are policies still calibrated to the agent's data sensitivity?

Output is a written report filed in the firm's compliance review repository, cross-referenced to FINRA Rule 3120 / Advisers Act Rule 206(4)-7 annual review packages where applicable.

---

## 7. Prerequisites and Lifecycle Workflow Foundations

### 7.1 Licensing and Prerequisites

| Requirement | Source |
|---|---|
| Microsoft Entra ID Governance (P2 / Governance SKU) | Required for Lifecycle Workflows and Access Reviews |
| Microsoft Entra Verified ID (optional but recommended for Z3) | Cryptographic sponsor signature (Section 12) |
| Lifecycle Workflows enabled in tenant | Entra admin center → Identity Governance |
| Power Platform admin center with approval centers enabled | Power Platform admin |
| Microsoft Purview Audit (Standard or Premium) | Sponsor approval audit trail |
| Microsoft Sentinel or Defender XDR with custom log table | Long-term sponsor signature retention and KQL query |
| Agent inventory metadata schema (Control 3.1) deployed | `agt_AgentInventory` Dataverse table with sponsor / owner / backup columns |
| Sponsor eligibility security groups | Created per Section 7.3 |
| AI Governance Lead role designated | Named individual with email + Teams reachability |

**Required Entra roles** (from [role catalog](../../../reference/role-catalog.md)):

- **Entra Identity Governance Admin** — to create and manage Lifecycle Workflows.
- **Entra Agent ID Admin** — to manage Agentic User attributes.
- **Power Platform Admin** — to configure agent approval workflows.
- **Purview Compliance Admin** — to scope attestation correspondence under Control 1.10.
- **AI Administrator** — to manage Copilot agent governance settings.
- **Entra Privileged Role Admin** — to configure PIM-eligible escalation for AI Governance Lead.

### 7.2 Enable Lifecycle Workflows

**Portal path:** Microsoft Entra admin center → **Identity Governance** → **Lifecycle Workflows**

1. Sign in as Entra Identity Governance Admin.
2. Navigate to **Lifecycle Workflows** → **Workflow settings**.
3. Confirm "Email notifications" sender is `lifecycle-noreply@<your-tenant>` (or your branded sender).
4. Set **Workflow processing schedule** to every 1 hour (default 3 — recommend tighter for FSI).
5. Enable **Access reviews integration** so attestation tasks can chain to access review packages.

*Screenshot description: Entra admin center Lifecycle Workflows landing page with three workflows visible (FSI-Quarterly-Sponsor-Attestation, FSI-Sponsor-Departure-Cascade, FSI-Owner-Departure-Cascade), each showing "Enabled" status pill and last run timestamp.*

### 7.3 Create Sponsor and Owner Eligibility Groups

```powershell
# Create role-based eligibility groups for sponsorship governance
Connect-MgGraph -Scopes "Group.ReadWrite.All","User.Read.All"

$groups = @(
    @{ DisplayName = "sg-agent-sponsors-zone2";   Description = "Eligible Z2 sponsors (Manager+)";        MailNickname = "agent-sponsors-z2" },
    @{ DisplayName = "sg-agent-sponsors-zone3";   Description = "Eligible Z3 sponsors (Director+)";       MailNickname = "agent-sponsors-z3" },
    @{ DisplayName = "sg-agent-owners";           Description = "Trained agent owners (all zones)";       MailNickname = "agent-owners" },
    @{ DisplayName = "sg-agent-backup-owners";    Description = "Trained backup owners (all zones)";      MailNickname = "agent-backup-owners" },
    @{ DisplayName = "sg-compliance-reviewers";   Description = "Designated compliance reviewers (Z3)";   MailNickname = "agent-compliance-reviewers" },
    @{ DisplayName = "sg-ai-governance-leads";    Description = "AI Governance Lead escalation group";    MailNickname = "ai-governance-leads" }
)

foreach ($g in $groups) {
    New-MgGroup -DisplayName $g.DisplayName `
                -Description $g.Description `
                -MailNickname $g.MailNickname `
                -MailEnabled:$false `
                -SecurityEnabled:$true | Out-Null
    Write-Host "Created $($g.DisplayName)"
}
```

Membership of `sg-agent-sponsors-zone3` and `sg-compliance-reviewers` should be governed by **Entra Identity Governance access reviews** on a quarterly cadence. See [Microsoft Learn — Access reviews](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview).

---

## 8. Periodic Attestation Workflows

### 8.1 Zone 2 Quarterly Sponsor Attestation Workflow

**Portal path:** Lifecycle Workflows → **+ New workflow** → Custom workflow.

| Setting | Value |
|---|---|
| Name | `FSI-Z2-Quarterly-Sponsor-Attestation` |
| Description | Quarterly Sponsor signature for Z2 agents (90-day cadence) |
| Category | Custom |
| Trigger | Time-based, every 90 days from `extension_LastAttestationDate` |
| Scope | `(user.userType eq 'AgenticUser') and (user.extension_GovernanceZone eq 'Zone2')` |

**Tasks (in order):**

| # | Task | Configuration summary |
|---|---|---|
| 1 | Generate activity pack | Custom extension → Logic App posts last 90 days summary to SharePoint |
| 2 | Send email to Sponsor | Subject: `ACTION REQUIRED: Quarterly attestation — {{displayName}}` |
| 3 | Send email to Owner + Backup Owner | Co-signature notification |
| 4 | Request approval (Sponsor) | Single-stage; 14-day deadline; escalate to Sponsor's manager at day 10 |
| 5 | Update `extension_LastAttestationDate` | On approval |
| 6 | Capture signature artifact | Custom extension → write to evidence pack (Section 12) |
| 7 | On rejection / non-response | Trigger cascade — see Section 9 |

```powershell
# Create the Z2 quarterly attestation workflow
$z2Workflow = @{
    displayName = "FSI-Z2-Quarterly-Sponsor-Attestation"
    description = "Quarterly Sponsor attestation for Zone 2 agents"
    isEnabled = $true
    isSchedulingEnabled = $true
    category = "custom"
    executionConditions = @{
        "@odata.type" = "#microsoft.graph.identityGovernance.triggerAndScopeBasedConditions"
        scope = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.ruleBasedSubjectSet"
            rule = "(user.userType eq 'AgenticUser') and (user.extension_GovernanceZone eq 'Zone2')"
        }
        trigger = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.timeBasedAttributeTrigger"
            timeBasedAttribute = "extension_LastAttestationDate"
            offsetInDays = 90
        }
    }
    tasks = @(
        @{ taskDefinitionId = "<generate-activity-pack-extension>";    displayName = "Generate activity pack" },
        @{ taskDefinitionId = "aab41899-9972-422a-9a53-f4bb8b36b8ae";  displayName = "Notify Sponsor"; arguments = @(
              @{ name = "emailSubject"; value = "ACTION REQUIRED: Quarterly attestation — {{displayName}}" }
              @{ name = "emailRecipients"; value = "{{manager}}" }) },
        @{ taskDefinitionId = "22085229-5809-45e8-97fd-270d28d66910";  displayName = "Request Sponsor attestation"; arguments = @(
              @{ name = "approvers"; value = "{{manager}}" }
              @{ name = "escalationRecipients"; value = "sg-ai-governance-leads" }
              @{ name = "escalationAfterDays"; value = "10" }) },
        @{ taskDefinitionId = "<update-attestation-date-extension>";   displayName = "Update last attestation date" },
        @{ taskDefinitionId = "<capture-signature-extension>";         displayName = "Capture signature artifact" }
    )
}

New-MgIdentityGovernanceLifecycleWorkflow -BodyParameter $z2Workflow
```

### 8.2 Zone 3 Quarterly Attestation with Dual Sign-Off

The Z3 workflow extends Z2 with:

- A second-stage approval task targeting the **Compliance Reviewer** (`sg-compliance-reviewers`) after Sponsor approval.
- Tighter escalation (7-day Sponsor SLA, 7-day Compliance SLA).
- Auto-trigger of Section 9.4 emergency cascade if either stage rejects or both stages lapse 7 days past escalation.

```powershell
# Z3 dual-stage attestation tasks (replaces tasks 4-5 in Section 8.1)
$z3DualStage = @(
    @{ taskDefinitionId = "22085229-5809-45e8-97fd-270d28d66910"
       displayName = "Stage 1 — Sponsor attestation"
       arguments = @(
           @{ name = "approvers"; value = "{{manager}}" }
           @{ name = "escalationRecipients"; value = "sg-ai-governance-leads" }
           @{ name = "escalationAfterDays"; value = "7" }
       ) },
    @{ taskDefinitionId = "22085229-5809-45e8-97fd-270d28d66910"
       displayName = "Stage 2 — Compliance Reviewer co-sign"
       arguments = @(
           @{ name = "approvers"; value = "sg-compliance-reviewers" }
           @{ name = "escalationRecipients"; value = "sg-ai-governance-leads" }
           @{ name = "escalationAfterDays"; value = "7" }
       ) }
)
```

### 8.3 Backup Owner Reachability Test (Semi-Annual)

Workflow `FSI-Backup-Owner-Reachability` runs every 180 days. It sends a low-friction confirmation request to every Backup Owner of record. Non-response triggers a Sponsor notification and a 14-day window to designate a replacement Backup Owner before the agent moves to Deprecated.

---

## 9. Departed Sponsor / Owner Cascade Workflow

This is the highest-impact workflow in the playbook. A departed Sponsor or Owner without cascade handling produces an **orphaned privileged identity** — exactly the condition NYDFS Part 500.07 and FINRA Rule 3110 examiners look for.

### 9.1 Decision Tree

```
                       Sponsor / Owner / Backup
                       departure event detected
                                  │
                  ┌───────────────┴────────────────┐
                  │                                │
            Owner departed                  Sponsor departed
                  │                                │
        Backup Owner exists?              Backup Owner exists?
        ├─ Yes ──► Promote Backup;        ├─ Yes ──► Notify Backup;
        │         Sponsor names new       │         escalate to
        │         Backup in 5 BD          │         Sponsor's manager
        │                                 │
        └─ No ──► AI Governance Lead      └─ No ──► AI Governance Lead
                  takes operational               assumes Sponsor on
                  custody; Z grace period         interim; Compliance
                  begins (Z1=30 / Z2=14           notified; Z grace
                  / Z3=0 days)                    period begins
                                  │
                       Reassignment within
                       grace period?
                       ├─ Yes ──► Update inventory; new attestation cycle
                       └─ No  ──► Emergency Decommissioned (Section 9.4)
```

### 9.2 Owner Departure Workflow

```powershell
$ownerDeparture = @{
    displayName = "FSI-Owner-Departure-Cascade"
    description = "Cascade reassignment when an Agent Owner departs"
    isEnabled = $true
    category = "leaver"
    executionConditions = @{
        "@odata.type" = "#microsoft.graph.identityGovernance.triggerAndScopeBasedConditions"
        scope = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.ruleBasedSubjectSet"
            rule = "(user.memberOf any (group.displayName eq 'sg-agent-owners'))"
        }
        trigger = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.groupBasedTrigger"
            triggerAttribute = "accountEnabled"
            changeType = "delete"
        }
    }
    tasks = @(
        @{ taskDefinitionId = "<find-owned-agents-extension>";       displayName = "Find owned agents" },
        @{ taskDefinitionId = "<promote-backup-owner-extension>";    displayName = "Promote Backup Owner to Owner" },
        @{ taskDefinitionId = "aab41899-9972-422a-9a53-f4bb8b36b8ae"; displayName = "Notify Sponsor — designate new Backup within 5 BD" },
        @{ taskDefinitionId = "<start-reassignment-timer-extension>"; displayName = "Start reassignment timer (per zone)" }
    )
}
```

### 9.3 Sponsor Departure Workflow

The Sponsor departure workflow follows the same pattern as 9.2 but the cascade promotes the **Sponsor's manager** (resolved via Entra `manager` attribute) to interim Sponsor and notifies the AI Governance Lead. For Z3 agents, the workflow simultaneously notifies the Compliance Reviewer and opens a `FSI-Z3-Sponsor-Vacant` access review against the agent. Cascade completes only when:

1. A new Sponsor is named and accepts (recorded as approval artifact).
2. The new Sponsor signs an out-of-cycle attestation within the grace period.
3. The agent's `extension_SponsorId` is updated and audit log entry written.

```powershell
$sponsorDeparture = @{
    displayName = "FSI-Sponsor-Departure-Cascade"
    description = "Cascade Sponsor reassignment with manager-hierarchy fallback"
    isEnabled = $true
    category = "leaver"
    tasks = @(
        @{ taskDefinitionId = "<find-sponsored-agents-extension>";     displayName = "Find sponsored agents" },
        @{ taskDefinitionId = "<resolve-manager-extension>";           displayName = "Resolve departing Sponsor's manager" },
        @{ taskDefinitionId = "<notify-interim-sponsor-extension>";    displayName = "Notify interim Sponsor + AI Governance Lead" },
        @{ taskDefinitionId = "<open-z3-access-review-extension>";     displayName = "Open Z3 vacant-Sponsor access review (Z3 only)" },
        @{ taskDefinitionId = "<start-zone-grace-timer-extension>";    displayName = "Start zone-specific grace timer" }
    )
}
```

### 9.4 Emergency Decommissioned Transition

Triggered when:

- Grace period expires without a successor Sponsor or Owner.
- Compliance Reviewer issues a regulatory veto.
- AI Governance Lead determines the agent represents an unmitigated risk.
- DSPM for AI ([Control 2.1](../2.1/portal-walkthrough.md)) raises a Severity 1 alert for which no Owner can be reached.

**Behavior.** The workflow:

1. Sets `extension_LifecycleState = "Decommissioned"` on the Agentic User.
2. Disables the Agentic User account (`accountEnabled = false`).
3. Removes group memberships that grant data access.
4. Removes the agent from active Copilot Studio / Power Platform / Agent 365 environments (preserves the artifact for forensic review per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)).
5. Files an emergency-cascade record with the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) intake queue.
6. Notifies AI Governance Lead, on-call Compliance, Sponsor's chain of command, and Security Operations.

```powershell
$emergencyDecom = @{
    displayName = "FSI-Emergency-Decommission"
    description = "Emergency Decommissioned transition for unrecoverable cases"
    isEnabled = $true
    category = "custom"
    tasks = @(
        @{ taskDefinitionId = "<set-state-decommissioned-extension>";   displayName = "Set lifecycle state to Decommissioned" },
        @{ taskDefinitionId = "1dfdfcc7-52fa-4c2e-bf3a-e3919cc12950";   displayName = "Disable Agentic User account" },
        @{ taskDefinitionId = "<remove-data-access-groups-extension>";  displayName = "Remove data-access group memberships" },
        @{ taskDefinitionId = "<file-incident-record-extension>";       displayName = "File emergency cascade record" },
        @{ taskDefinitionId = "aab41899-9972-422a-9a53-f4bb8b36b8ae";   displayName = "Notify AI Governance Lead + Compliance + SecOps" }
    )
}
```

!!! warning "Emergency cascade is reversible only via re-onboarding"
    Once an agent is in Decommissioned state, restoration requires returning it to Draft and walking the full lifecycle again, including a new In Review → Approved gate with fresh signatures. This is intentional and supports the supervisory expectation that an agent without a current responsible party cannot resume operation without renewed risk acceptance.

### 9.5 Manager Hierarchy Fallback

The cascade resolves successor identities via Entra `manager` chain with these rules:

| Scenario | Successor resolution |
|---|---|
| Sponsor departed; manager is also a member of `sg-agent-sponsors-zone2/3` | Manager becomes interim Sponsor |
| Sponsor departed; manager is **not** sponsor-eligible | Walk up to first eligible manager; cap at 3 hops |
| 3 hops with no eligible successor | AI Governance Lead becomes interim Sponsor; opens 14-day designation window |
| Owner departed; Backup Owner is active and reachable | Backup auto-promotes |
| Owner departed; Backup unreachable for 48h | AI Governance Lead assumes operational custody; emergency cascade timer starts |

---

## 10. Approval Workflow Integration

This section unifies three otherwise-disjoint Microsoft approval surfaces into a **single Sponsor signature flow** with one audit trail.

### 10.1 The Three Approval Surfaces

| Surface | What it gates | Native admin |
|---|---|---|
| **Entra Admin Consent Workflow** | App registration permission grants consumed by an agent's connected app | Entra App Admin / Global Admin |
| **Entra Agent Approval Workflow** (Agentic User governance) | Creation, scope changes, decommission of an Agentic User | Entra Agent ID Admin |
| **Power Platform Agent Approval** (Copilot Studio / Power Apps) | Publishing, sharing, or environment-promoting Copilot Studio agents | Power Platform Admin / Environment Admin |

By default these emit independent approval requests with independent audit trails. The unified flow funnels all three to a single approval record signed by the Sponsor.

### 10.2 Unified Flow Architecture

```
┌────────────────────────────────────────────────────────────┐
│  Trigger source (any of):                                  │
│  • Entra admin consent request raised                      │
│  • Agentic User scope change requested                     │
│  • Copilot Studio publish requested                        │
└───────────────┬────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│  Power Automate orchestration flow                         │
│  • Resolves agent ID                                       │
│  • Reads Sponsor + Compliance from Control 3.1 inventory   │
│  • Builds unified approval card                            │
│  • Sends single Approvals action via Teams / Outlook       │
└───────────────┬────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│  Sponsor approves once →                                   │
│  • Approves the originating Entra / Agent / PP request     │
│  • Writes signature artifact to evidence pack              │
│  • Updates Control 3.1 inventory                           │
│  • Notifies Owner + Backup + (Z3) Compliance Reviewer      │
└────────────────────────────────────────────────────────────┘
```

### 10.3 Implementation Outline

1. **Power Automate cloud flow** `flow-fsi-unified-agent-approval` triggers on:
    - Microsoft Graph subscription to `directory/auditLogs` for `ConsentToApplication` events scoped to the agent app pattern.
    - Dataverse trigger on `agt_AgentApprovalRequest` table.
    - Power Platform Connector Approval Center webhook.
2. The flow looks up the agent in `agt_AgentInventory` (Control 3.1) to resolve current Sponsor, Backup Owner, and Compliance Reviewer.
3. The flow posts a **single Adaptive Card** to the Sponsor with all change details and a single Approve/Reject action.
4. On Sponsor approval, the flow writes back to:
    - The Entra admin consent request (via Microsoft Graph `appConsentRequests` API).
    - The Agent ID change request (via Microsoft Graph identity governance API).
    - The Power Platform request (via Power Platform admin API).
    - The signature artifact store (Section 12).
5. For Z3, the same flow chains a second Adaptive Card to the Compliance Reviewer.

!!! tip "Why unify"
    Examiners ask "show me the supervisor's approval" — singular. A unified flow lets you produce one signed artifact per change rather than three correlated artifacts. This matches the FINRA Rule 3110 expectation that supervision is a documented decision, not a series of disjoint clicks.

### 10.4 Configuration Reference

Detailed Power Automate flow JSON, Adaptive Card schema, and Microsoft Graph API call examples live in [PowerShell Setup](./powershell-setup.md). This playbook owns the policy, signatures, and evidence semantics; the technical scaffolding lives in the peer playbooks.

---

## 11. Sponsorship Evidence Pack

Every attestation, every cascade execution, and every emergency decommission produces a **sponsorship evidence pack**. Examiners and internal audit consume these packs directly; the format is therefore deliberately rigid.

### 11.1 Pack Contents

| Artifact | Format | Source | Required for |
|---|---|---|---|
| Attestation request record | JSON | Lifecycle Workflows audit | All quarterly attestations |
| Sponsor signature | JWS or Entra Verified ID VC (Z3) | Approval action | All quarterly attestations |
| Compliance Reviewer co-signature (Z3) | JWS or Verified ID VC | Approval action | Z3 attestations and material changes |
| Activity pack snapshot | PDF + raw JSON | Generated by Section 8.1 task 1 | All quarterly attestations |
| DSPM alert summary (last 90d) | CSV | DSPM for AI export | Z2 + Z3 attestations |
| Communication Compliance disposition (last 90d) | CSV | Control 1.10 export | Z3 attestations and any agent under supervised-comms scope |
| Material change log (last 90d) | CSV | Control 3.1 inventory diff | All attestations |
| Approval timestamp chain | JSON | Lifecycle Workflows + Power Automate | All attestations |
| Audit trail correlation IDs | JSON | Purview Audit + Sentinel custom table | All attestations |
| SHA-256 hash of pack contents | Text file `pack.sha256` | Computed at pack close | All attestations |
| SHA-256 of previous pack (chain) | Text file `previous.sha256` | Read from previous pack | All attestations after the first |

### 11.2 Hash Chaining for Tamper Evidence

Each pack contains the SHA-256 of the prior pack for the same agent, producing a per-agent hash chain that supports SEC 17a-4(f) WORM-equivalent verification:

```powershell
# Generate sponsorship evidence pack with hash chain
function New-SponsorshipEvidencePack {
    param(
        [Parameter(Mandatory)] [string] $AgentId,
        [Parameter(Mandatory)] [string] $AttestationCycle,   # e.g. "2026-Q2"
        [Parameter(Mandatory)] [string] $PackOutputPath
    )

    $packDir = Join-Path $PackOutputPath "$AgentId-$AttestationCycle"
    New-Item -ItemType Directory -Path $packDir -Force | Out-Null

    # 1. Collect artifacts (placeholder calls — implementations live in powershell-setup.md)
    Export-AttestationRecord       -AgentId $AgentId -Cycle $AttestationCycle -OutFile (Join-Path $packDir "attestation.json")
    Export-SponsorSignature        -AgentId $AgentId -Cycle $AttestationCycle -OutFile (Join-Path $packDir "sponsor-signature.jws")
    Export-ActivityPack            -AgentId $AgentId -DaysBack 90             -OutFile (Join-Path $packDir "activity-pack.pdf")
    Export-DspmAlertSummary        -AgentId $AgentId -DaysBack 90             -OutFile (Join-Path $packDir "dspm-alerts.csv")
    Export-MaterialChangeLog       -AgentId $AgentId -DaysBack 90             -OutFile (Join-Path $packDir "material-changes.csv")
    Export-ApprovalTimestampChain  -AgentId $AgentId -Cycle $AttestationCycle -OutFile (Join-Path $packDir "timestamps.json")

    # 2. Read previous pack hash if present
    $prevHashFile = Get-PreviousPackHash -AgentId $AgentId
    if ($prevHashFile) {
        Copy-Item $prevHashFile -Destination (Join-Path $packDir "previous.sha256")
    }

    # 3. Compute pack hash over sorted file list
    $files = Get-ChildItem $packDir -File | Sort-Object Name
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $stream = New-Object System.IO.MemoryStream
    foreach ($f in $files) {
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
        $stream.Write($bytes, 0, $bytes.Length)
    }
    $stream.Position = 0
    $hash = [BitConverter]::ToString($sha256.ComputeHash($stream)).Replace("-","").ToLower()
    Set-Content -Path (Join-Path $packDir "pack.sha256") -Value $hash

    # 4. Write to WORM-eligible store (Purview Records Management with retention label)
    Publish-EvidencePackToWorm -PackPath $packDir -RetentionLabel "FSI-Agent-Sponsorship-7yr"

    return $hash
}
```

### 11.3 Cryptographic Sponsor Signatures (Recommended for Z3)

For Z3 agents, the framework recommends Microsoft Entra Verified ID-issued **AgentSponsorAttestation** verifiable credentials rather than plain audit-log entries. The Verified ID issuance flow:

1. The Sponsor authenticates with Entra ID using a phishing-resistant method (FIDO2 or Windows Hello for Business).
2. The Verified ID issuer (configured under your tenant) issues a credential containing: `agentId`, `cycleId`, `sponsorObjectId`, `attestationStatement`, `issuedAt`, `expiresAt = issuedAt + 100 days`.
3. The credential is captured into the evidence pack as `sponsor-signature.jws`.
4. Verification at examination time uses the Entra Verified ID verifier API or the open `did:web` resolver — the artifact does not require Microsoft to be reachable to validate.

See [Microsoft Learn — Entra Verified ID](https://learn.microsoft.com/en-us/entra/verified-id/decentralized-identifier-overview) and the framework's [identity architecture](../../../framework/agent-identity-architecture.md).

### 11.4 Retention

| Artifact | Retention | Authority |
|---|---|---|
| Z1 attestations | 3 years | Internal policy |
| Z2 attestations | 7 years | FINRA Rule 4511, SEC 17a-4(b)(4) |
| Z3 attestations | 7 years | FINRA Rule 4511, SEC 17a-4(b)(4); 10 years recommended for SOX-scoped agents |
| Annual external review reports | 7 years | FINRA Rule 3120; Advisers Act Rule 204-2 |
| Cascade execution records | 7 years | NYDFS Part 500.06 |
| Emergency Decommissioned records | 10 years | Internal policy aligned with longest applicable retention |

Retention is implemented via Purview Records Management labels published under [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## 12. Verification, Reporting, and KQL

### 12.1 Quarterly Compliance Report

```powershell
function Get-SponsorshipAttestationReport {
    [CmdletBinding()]
    param(
        [int] $DaysBack = 95,
        [ValidateSet("Zone1","Zone2","Zone3","All")] [string] $Zone = "All"
    )

    $filter = "userType eq 'AgenticUser'"
    if ($Zone -ne "All") { $filter += " and extension_GovernanceZone eq '$Zone'" }

    $agents = Get-MgUser -Filter $filter -All -ConsistencyLevel eventual -CountVariable c

    foreach ($a in $agents) {
        $ext = (Get-MgUser -UserId $a.Id -Property "extension_LastAttestationDate,extension_SponsorId,extension_BackupOwnerId,extension_ComplianceReviewerId,extension_GovernanceZone,extension_LifecycleState").AdditionalProperties

        $required = switch ($ext.extension_GovernanceZone) {
            "Zone3" { 90 }
            "Zone2" { 90 }
            default { 365 }
        }

        $lastAttest = if ($ext.extension_LastAttestationDate) { [datetime]$ext.extension_LastAttestationDate } else { [datetime]"1900-01-01" }
        $daysSince  = ((Get-Date) - $lastAttest).Days

        [pscustomobject]@{
            AgentId             = $a.Id
            AgentName           = $a.DisplayName
            Zone                = $ext.extension_GovernanceZone
            LifecycleState      = $ext.extension_LifecycleState
            SponsorId           = $ext.extension_SponsorId
            BackupOwnerId       = $ext.extension_BackupOwnerId
            ComplianceReviewer  = $ext.extension_ComplianceReviewerId
            LastAttestation     = $lastAttest
            DaysSinceAttest     = $daysSince
            RequiredCadenceDays = $required
            Overdue             = ($daysSince -gt $required)
            HasBackup           = [bool]$ext.extension_BackupOwnerId
            Z3CompletelyStaffed = ($ext.extension_GovernanceZone -ne "Zone3") -or ($ext.extension_SponsorId -and $ext.extension_BackupOwnerId -and $ext.extension_ComplianceReviewerId)
        }
    }
}

# Examiner-ready dashboard CSV
Get-SponsorshipAttestationReport |
    Sort-Object Overdue, Zone -Descending |
    Export-Csv "SponsorshipReport-$(Get-Date -Format yyyy-MM-dd).csv" -NoTypeInformation
```

### 12.2 KQL — Attestation Audit Trail

```kql
// Sponsor + Compliance attestation events for the current quarter
AuditLogs
| where TimeGenerated > startofday(ago(120d))
| where Category == "LifecycleWorkflows"
| where OperationName has_any ("FSI-Z2-Quarterly-Sponsor-Attestation",
                              "FSI-Z3-Quarterly-Sponsor-Attestation",
                              "FSI-Sponsor-Departure-Cascade",
                              "FSI-Owner-Departure-Cascade",
                              "FSI-Emergency-Decommission")
| extend agentId    = tostring(TargetResources[0].id),
         agentName  = tostring(TargetResources[0].displayName),
         actorId    = tostring(InitiatedBy.user.id),
         actorUpn   = tostring(InitiatedBy.user.userPrincipalName),
         outcome    = tostring(Result),
         workflowId = tostring(AdditionalDetails[0].value)
| project TimeGenerated, OperationName, agentId, agentName, actorUpn, outcome, workflowId, CorrelationId
| order by TimeGenerated desc
```

### 12.3 KQL — Overdue Attestations Alert

```kql
// Agents whose last attestation is past the zone cadence by >7 days
let now = now();
AgentInventory_CL                                 // Control 3.1 mirrored table
| where LifecycleState_s == "Active"
| extend cadenceDays = case(GovernanceZone_s == "Zone3", 90,
                            GovernanceZone_s == "Zone2", 90,
                            365)
| extend daysSince = datetime_diff('day', now, todatetime(LastAttestationDate_t))
| where daysSince > cadenceDays + 7
| project AgentId_g, AgentName_s, GovernanceZone_s, SponsorUpn_s, LastAttestationDate_t, daysSince, cadenceDays
| order by daysSince desc
```

This KQL feeds a Sentinel scheduled analytics rule that creates an incident routed to AI Governance Lead and the agent's Sponsor.

### 12.4 Verification Checklist

1. Each Active agent has a populated `extension_SponsorId` (Z2/Z3) and `extension_BackupOwnerId` (Z2/Z3).
2. Each Z3 Active agent has a populated `extension_ComplianceReviewerId`.
3. `extension_LastAttestationDate` is within cadence + 14-day grace.
4. Lifecycle Workflows `FSI-Quarterly-Sponsor-Attestation`, `FSI-Sponsor-Departure-Cascade`, `FSI-Owner-Departure-Cascade`, `FSI-Emergency-Decommission`, `FSI-Backup-Owner-Reachability` exist and report `IsEnabled = true`.
5. Last 90 days contain at least one successful workflow run per Active Z2/Z3 agent.
6. Sponsorship evidence pack count = expected count (per cycle × per agent).
7. SHA-256 chain validates end-to-end for sampled agents.
8. No agent in Active state has an Owner whose Entra account is disabled.
9. No agent in Active state has a Sponsor whose Entra account is disabled.
10. Annual Compliance Reviewer report exists for each Z3 Active agent.

Detailed test cases live in [Verification Testing](./verification-testing.md).

---

## 13. Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| Workflow shows `IsEnabled = true` but never runs | Scope filter does not match any user | Verify `extension_GovernanceZone` and `userType` populated on Agentic Users |
| Sponsor not receiving email | Sponsor's mailbox routes via on-prem; Lifecycle email sender blocked | Allow-list `lifecycle-noreply@<tenant>` in Exchange Online transport rules ([Exchange Online Admin](../../../reference/role-catalog.md)) |
| Approval action received but signature artifact missing | Custom extension Logic App returned non-200 | Inspect Logic App run history; verify managed identity has `Group.Read.All` and `User.Read.All` |
| Cascade promoted Backup Owner but inventory not updated | Dataverse write-back step lacks Power Platform connection auth | Refresh service principal credentials in `flow-fsi-unified-agent-approval` |
| Z3 attestation stuck at Compliance stage | Compliance Reviewer group is empty or members lack Purview Compliance Admin role | Populate `sg-compliance-reviewers`; verify role assignments |
| Emergency Decommission did not disable account | `User.ReadWrite.All` consent missing on workflow service principal | Re-consent via [admin consent workflow](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
| Hash chain breaks at cycle N | Pack N–1 missing or modified after publication | Investigate Records Management retention label drift; restore from immutable archive |
| Manager-hierarchy fallback walks past 3 hops | No Sponsor-eligible manager in chain (rare in flat orgs) | AI Governance Lead assumes interim Sponsor automatically — confirm escalation alert delivered |
| Sponsor departure not detected | Trigger fires on group membership delete; user's accountEnabled may flip first | Add secondary trigger on `user.accountEnabled` change to `false` |
| Workflow run history shows ContinueOnError swallowing failures | Default false but may have been changed | Audit each task's `ContinueOnError`; for sponsorship workflows, all signature tasks must be `false` |

Refer to [Troubleshooting](./troubleshooting.md) for registry-level issues and the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) for cascade-driven incident response.

---

## 14. Related Resources

### Framework and controls

- [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)
- [Control 2.1 implementation playbooks](../2.1/portal-walkthrough.md)
- [Agent Identity Architecture](../../../framework/agent-identity-architecture.md)
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)

### Peer playbooks (Control 1.2)

- [Portal Walkthrough](./portal-walkthrough.md)
- [PowerShell Setup](./powershell-setup.md)
- [Verification Testing](./verification-testing.md)
- [Troubleshooting](./troubleshooting.md)

### Microsoft Learn (verified April 2026)

- [Microsoft Entra Identity Governance — Lifecycle Workflows overview](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows)
- [Microsoft Entra Identity Governance — Access reviews](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Microsoft Entra ID Governance — Custom workflow tasks](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-extensibility)
- [Microsoft Entra Verified ID — Overview](https://learn.microsoft.com/en-us/entra/verified-id/decentralized-identifier-overview)
- [Microsoft Entra Agent ID — Overview](https://learn.microsoft.com/en-us/entra/agent-id/what-is-agent-id-platform) *(preview)*
- [Power Platform — Connector action control and consent](https://learn.microsoft.com/en-us/power-platform/admin/connector-action-control)
- [Microsoft Purview — Records Management and retention labels](https://learn.microsoft.com/en-us/purview/records-management)
- [Microsoft Purview — Audit (Standard and Premium)](https://learn.microsoft.com/en-us/purview/audit-solutions-overview)
- [Microsoft Sentinel — Custom log tables and analytics rules](https://learn.microsoft.com/en-us/azure/sentinel/create-custom-connector)

### Regulatory references

- FINRA Rule 3110 — Supervision
- FINRA Rule 3120 — Supervisory control system
- FINRA Rule 4511 — General requirements for books and records
- FINRA Notice 25-07 — Generative AI member firm responsibilities
- SEC Rule 17a-4(b)(4) and 17a-4(f) — Records preservation
- SOX §302 / §404 — Officer certification and ICFR
- GLBA §501(b) and FTC Safeguards 16 CFR §314.4(c) — Information security program
- NYDFS 23 NYCRR Part 500.07 (access privileges) and 500.16 (incident response)
- OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) — Sound practices for model risk management
- Federal Reserve SR 26-2 (formerly SR 11-7) — Guidance on model risk management
- NIST AI Risk Management Framework — GOVERN 1.4 and GOVERN 1.6

---

[Back to Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) · [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Verification Testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
