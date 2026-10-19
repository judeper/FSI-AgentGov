# Sponsorship Lifecycle Workflows

**Last Verified:** 2026-10-18 (live Microsoft Learn technical documentation review; no tenant execution, UI verification, or screenshots).

!!! important "Native capabilities versus custom implementation"
    This playbook defines an organizational sponsorship process, not a deployable automation package. Microsoft documents native **human sponsor mover/leaver tasks**; quarterly approvals, zone-aware cascades, evidence signatures, and cross-platform containment require separately implemented and tested orchestration. The [verification ledger](#documentation-verification-ledger) records the technical corrections and primary sources. Regulatory mappings and compliance wording were not re-evaluated.

> Supplemental playbook for [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md). This document specifies the **human accountability layer** that wraps every Microsoft 365 AI agent: the named sponsors, owners, backup owners, and compliance reviewers who carry regulatory responsibility for the agent across its lifecycle, and the native capabilities / custom implementation requirements for operationalizing that accountability.
>
> Companion playbooks (do **not** duplicate content from these — link to them):
>
> - [Portal Walkthrough](./portal-walkthrough.md) — registry portal configuration
> - [PowerShell Setup](./powershell-setup.md) — read-only collection examples, not sponsor-signature or lifecycle-mutation automation
> - [Verification Testing](./verification-testing.md) — registry test cases
> - [Troubleshooting](./troubleshooting.md) — registry common issues
>
> Cross-control dependencies:
>
> - [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — authoritative lifecycle state machine
> - [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — sponsor signature capture and retention
> - [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — sponsor approval correspondence supervision
> - [Control 1.6 implementation playbooks](../1.6/portal-walkthrough.md) — DSPM for AI alerting that escalates to sponsors
> - [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) — sponsor on-call obligations during incidents

---

## 1. Overview

Human sponsorship is a foundational requirement for Microsoft Entra agent identities and blueprints and a core supervisory expectation under FINRA Rule 3110, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), and Federal Reserve SR 26-2 (formerly SR 11-7). An AI agent without a named, attested, currently employed sponsor is — for examination purposes — an **unsupervised system**, and the residual risk of unsupervised automation in a regulated FSI environment is the central concern this playbook addresses.

This playbook provides:

1. The **four sponsorship roles** (Agent Sponsor, Agent Owner, Backup Owner, Compliance Reviewer) with duties, authority boundaries, and escalation paths.
2. The **lifecycle integration** that aligns sponsor approvals with the [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) state machine (Draft → In Review → Approved → Active → Deprecated → Decommissioned).
3. **Zone-differentiated sponsorship requirements** (Z1 informal, Z2 sponsor + backup mandatory, Z3 dual sponsor + backup + compliance).
4. **Attestation cadence** (quarterly sponsor signature, annual external compliance review) with a working calendar.
5. The **departed sponsor / owner cascade workflow** including manager-hierarchy fallback, AI Governance Lead escalation, and the emergency Decommissioned transition.
6. **Approval workflow integration requirements** correlating distinct native approval actions with a separate business attestation; no universal approval API or automatic signature flow is supplied.
7. The **sponsorship evidence pack** specifying every artifact captured per attestation, including SHA-256 hash chaining for tamper-evidence.
8. **Examiner readiness framing** mapping each artifact to specific regulations.

!!! note "Collection dependency reviewed 2026-10-18"
    Do not carry April 2026 blanket preview assumptions into current operation. Verify each feature's present entitlement and support terms using the [Control 1.2 source ledger](powershell-setup.md#documentation-verification-ledger). Its signed file catalog authenticates collected files, not the three-person sponsor attestation chain, prior-cycle hash chain, lifecycle workflow, or retention configuration specified here. Those remain separate implementation and tenant-test requirements; no UI or workflow execution was performed in this review.

!!! warning "Language and liability"
    This playbook helps meet — and is required for — supervisory expectations across FINRA, SEC, OCC, Federal Reserve, NYDFS, and FTC Safeguards regimes. It does **not** by itself constitute compliance. Implementation requires legal, compliance, and risk review tailored to your firm's business activities and regulatory profile. Organizations should verify every assertion against their own examination history.

---

## 2. Examiner Readiness Framing

Sponsorship is the artifact examiners look for first when evaluating AI agent governance. Each of the four sponsorship roles in this playbook maps to specific regulatory expectations:

| Regulation | Expectation | How sponsorship supports it |
|---|---|---|
| **FINRA Rule 3110** (Supervision) | Written supervisory procedures with named supervisors | Agent Sponsor is the named supervisor of record for the agent's business use; quarterly attestation produces the written evidence |
| **FINRA Rule 4511** (Books and Records) | Preservation of supervisory records in non-erasable, non-rewriteable form | Sponsorship evidence pack (Section 11) captures attestation in WORM-eligible form |
| **FINRA RN 24-09 / Rule 3110** (Generative AI) | Member firms remain responsible for compliance regardless of AI use; supervisory framework must address gen-AI specifically | Sponsor attestation explicitly references gen-AI risk categories (hallucination, inappropriate disclosure, unauthorized advice) |
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

The framework defines **four** sponsorship roles. Every agent — regardless of zone — must have at minimum an Agent Owner. Higher zones layer on Sponsor, Backup Owner, and Compliance Reviewer. These business roles are distinct from native directory relationships. Zone 1 owner-self-sponsorship does not waive the native sponsor requirement when creating an Entra agent identity or blueprint; an optional agent user has different relationship rules. See [agent owners, sponsors, and managers](https://learn.microsoft.com/en-us/entra/agent-id/agent-owners-sponsors-managers).

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

An eligibility group or team alias is governance metadata, not a native agent identity owner assignment. Assign supported named user owners separately and verify backup coverage; the security groups in Section 7.3 do not grant native ownership or sponsorship.

**Duties.**

1. Build, configure, and maintain the agent in Microsoft 365 Admin Center, Copilot Studio, Power Platform, or Agent 365.
2. Operate the agent within the scope authorized by the Sponsor.
3. Triage and respond to alerts from [Control 1.6](../1.6/portal-walkthrough.md) (DSPM for AI), [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), and Defender XDR within the Zone SLA.
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

This is the framework's organizational role policy, not a Microsoft requirement for responding to an approval. Grant product administration / evidence access separately using least privilege.

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

The timers and automatic transitions below are **organizational policy requirements for custom orchestration**, not native Microsoft defaults. Microsoft workflow availability or a successful notification does not demonstrate that these policies are implemented.

This expands the registry-level zone matrix from Control 1.2 with sponsorship-specific rules. Store sponsor / owner assignments in the Control 3.1 governance register and reconcile them with the supported relationships on each source identity. Not every agent has an agent user account. The `extension_*` names in this playbook are **logical custom-field aliases**, not built-in Microsoft Graph properties; record the registered extension names and supported object types before implementing directory write-back.

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

This section binds sponsorship signatures to the [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) lifecycle state machine. Each transition has a required signature set, a captured evidence artifact, and a hash-chained audit record (Section 11).

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

Sections 7–9 distinguish native Entra Lifecycle Workflows from the custom orchestration needed to drive these state transitions. `extension_LifecycleState` and `agt_AgentInventory` are proposed custom schema names, not provisioned Microsoft features. Map the six governance states to a dedicated custom lifecycle column; do not assume Dataverse `statecode` exposes these six values. A register update does not itself activate, suspend, or decommission a source agent.

---

## 6. Attestation Cadence

### 6.1 Calendar

| Cadence | Activity | Performed by | Evidence |
|---|---|---|---|
| **Daily** | Automated DSPM for AI alert review | Agent Owner (or Backup) | Alert disposition log |
| **Weekly (Z3)** | Activity summary review | Agent Owner; Sponsor receives digest | Sponsor digest acknowledgment |
| **Monthly (Z2)** | Activity summary review | Agent Owner; Sponsor receives digest | Sponsor digest acknowledgment |
| **Quarterly** | Sponsor attestation (Q1: Apr 15 / Q2: Jul 15 / Q3: Oct 15 / Q4: Jan 15) | Sponsor sign; Owner + Backup Owner co-acknowledge; Compliance Reviewer co-sign for Z3 | Signed attestation artifact (Section 11) |
| **Semi-annual** | Backup Owner reachability test | AI Governance team | Test result log |
| **Annual** | External compliance review — Z3 100%, Z2 ≥10% sample | Compliance Reviewer; independent of Sponsor and Owner | Written review report retained 7 years |
| **Annual** | Sponsor and Owner training refresh | Learning & Development | Completion records |
| **Triggered** | On material change (Section 5.3) | Sponsor + Compliance (Z3) | Change attestation record |
| **Triggered** | On Sponsor / Owner / Backup departure | Cascade workflow (Section 9) | Cascade execution record |

### 6.2 Quarterly Attestation Procedure

The quarterly attestation is the workhorse evidence artifact examiners request first. It must be:

1. **Initiated** by the separately implemented custom quarterly process (Section 8) on the cycle date; no such service is deployed by enabling Lifecycle Workflows.
2. **Reviewed** by the Sponsor against an activity pack with demonstrated collection coverage (last 90 days of agent activity, alerts, material changes, NPPI exposure summary). Export/retention must already cover that interval; missing evidence is an exception, not no activity.
3. **Signed** within 14 calendar days of initiation. Late attestations escalate per Section 9.
4. **Co-signed** by Compliance Reviewer for Z3 within 7 additional days.
5. **Archived** to the WORM-eligible store under Control 1.7 retention rules with SHA-256 chain (Section 11).

### 6.3 Annual External Review

The annual review is a **separate** activity from quarterly attestation. The Compliance Reviewer evaluates each Z3 agent against:

- FINRA RN 24-09 / Rule 3110 supervisory expectations for gen-AI.
- Reg BI / Advisers Act applicability where the agent influences customer recommendations.
- OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) effective challenge: was the model challenged by an independent party in the last 12 months?
- DSPM for AI policy alignment: are policies still calibrated to the agent's data sensitivity?

Output is a written report filed in the firm's compliance review repository, cross-referenced to FINRA Rule 3120 / Advisers Act Rule 206(4)-7 annual review packages where applicable.

---

## 7. Prerequisites and Lifecycle Workflow Foundations

### 7.1 Licensing and Prerequisites

| Requirement | Source |
|---|---|
| Microsoft Entra ID Governance or Microsoft Entra Suite | Employee Lifecycle Workflows; Entra ID P2 alone is not sufficient. Basic access reviews have separate P2 eligibility; confirm the specific review feature |
| Microsoft 365 E7, or Microsoft Agent 365 paired with at least Entra P1 or Microsoft 365 E3 | Current agent sponsorship-task entitlement; verify the scenario-specific [agent sponsor task prerequisites](https://learn.microsoft.com/en-us/entra/id-governance/agent-sponsor-tasks) and [licensing matrix](https://learn.microsoft.com/en-us/entra/id-governance/licensing-fundamentals) |
| Microsoft Entra Verified ID (optional custom credential design) | Credential issuance/presentation does not itself sign the evidence pack as the human Sponsor (Section 11.3) |
| Lifecycle Workflows enabled in tenant | Entra admin center → Identity Governance |
| Approved Power Automate / Logic Apps implementation and its connector entitlements | Custom scheduling, approvals, escalations, and evidence export; no generic PPAC approval-center switch is assumed |
| Microsoft Purview Audit (Standard or Premium), with applicable audited workloads | Collect available workload events; separately export custom approval decisions and signatures |
| Log Analytics workspace and ingestion configuration; Microsoft Sentinel if analytics rules are used | Custom approval / inventory telemetry and KQL; Defender XDR alone does not provision a workspace table or archive |
| Agent inventory metadata schema (Control 3.1) deployed | `agt_AgentInventory` Dataverse table with sponsor / owner / backup columns |
| Sponsor eligibility security groups | Created per Section 7.3 |
| AI Governance Lead role designated | Named individual with email + Teams reachability |

**Required Entra roles** (from [role catalog](../../../reference/role-catalog.md)):

- **Lifecycle Workflows Administrator** (Microsoft built-in role; map the framework's Entra Identity Governance Admin responsibility to this role) — to create and manage Lifecycle Workflows.
- **Entra Agent ID Admin** — to manage Agentic User attributes.
- **Power Platform Admin** — to configure agent approval workflows.
- **Purview Compliance Admin** — to scope attestation correspondence under Control 1.10; not a prerequisite merely to respond to a business approval.
- **AI Administrator** — to manage Copilot agent governance settings.
- **Entra Privileged Role Admin** — to configure PIM-eligible escalation for AI Governance Lead.

### 7.2 Enable Lifecycle Workflows

**Portal path:** Microsoft Entra admin center → **Identity Governance** → **Lifecycle Workflows**

1. Sign in with at least the Lifecycle Workflows Administrator role.
2. Navigate to **Lifecycle Workflows** → **Workflow settings**.
3. Configure a verified sender domain and optional company branding through the documented [email settings](https://learn.microsoft.com/en-us/entra/id-governance/customize-workflow-email). Inspect a delivered message before setting mail-flow exceptions; do not assume a tenant-specific `lifecycle-noreply` sender exists.
4. Set the tenant workflow schedule to the approved interval (1–24 hours; default 3 hours). This is evaluation frequency, not a quarterly recurrence trigger.
5. Configure any access review separately. There is no assumed **Access reviews integration** switch that turns email tasks into attestation or review packages.

*Evidence instruction: capture the actual native human leaver workflow, supported task configuration, schedule, and run details. Capture the custom quarterly attestation service separately. The `FSI-*` process names in this playbook are not preinstalled portal templates; no screenshot or tenant execution was produced in this documentation review.*

The [native sponsorship tasks](https://learn.microsoft.com/en-us/entra/id-governance/agent-sponsor-tasks) apply to **mover and leaver workflows for the human sponsor**:

| Task | Supported effect |
|---|---|
| Send email to manager about sponsorship changes | Notifies the moved/departing employee's manager about sponsored agent identities |
| Send email to co-sponsors about sponsor changes | Notifies other sponsors about the employee's move/departure |
| Transfer agent identity sponsorships to manager | Adds the employee's configured manager as sponsor and removes the employee from sponsored agent identities; requires a populated manager |

Include the intended tasks in an enabled workflow with the appropriate trigger, subject scope, and scheduling state. Do not assume a default-on transfer in an unconfigured tenant. The native transfer does not implement eligibility-aware multi-hop fallback, reviewer acceptance, backup-owner promotion, or zone grace periods. The current task guide does not label these three tasks preview; adjacent features must be checked separately.

For custom integration, Lifecycle Workflows supports registered extensions invoking compatible **consumption-based Azure Logic Apps**. The built-in **Run a custom task extension** task references the registered extension; a placeholder extension name is not a `taskDefinitionId`. Launch-and-continue success is not approval completion. The documented [callback wait](https://learn.microsoft.com/en-us/graph/api/resources/identitygovernance-customtaskextensioncallbackconfiguration?view=graph-rest-1.0) is **30 minutes to 3 hours**, so multi-day approvals need separate durable orchestration. Resolve task-definition metadata against the current [task catalog](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-tasks) before implementation; examples in the task-arguments documentation have differing extension IDs and are not tenant-tested deployment artifacts here.

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

These assigned security groups are **eligibility / review scope only**. They are not valid substitutes for native individual owners or universally valid native agent identity sponsor groups; follow the object-specific [relationship restrictions](https://learn.microsoft.com/en-us/entra/agent-id/agent-owners-sponsors-managers).

---

## 8. Periodic Attestation Workflows

### 8.1 Zone 2 Quarterly Sponsor Attestation Workflow

**Implementation boundary:** this is a custom recurring approval process, not a deployable Lifecycle Workflows definition. Use a separately approved scheduled orchestration that reads the governance register. The process names below are organizational identifiers, not Microsoft templates or task IDs.

| Setting | Value |
|---|---|
| Name | `FSI-Z2-Quarterly-Sponsor-Attestation` |
| Description | Quarterly Sponsor signature for Z2 agents (calendar dates in Section 6) |
| Execution platform | Tenant-implemented scheduler and approval workflow |
| Trigger | Quarterly calendar in Section 6; select due records from the governance register |
| Scope | Registered Zone 2 agents, joined to their source identity IDs and named human reviewers |

**Tasks (in order):**

| # | Task | Configuration summary |
|---|---|---|
| 1 | Generate activity pack | Custom service collects the covered interval and publishes the summary / collection gaps to supported storage |
| 2 | Send email to Sponsor | Subject: `ACTION REQUIRED: Quarterly attestation — {{displayName}}` |
| 3 | Send email to Owner + Backup Owner | Co-signature notification |
| 4 | Request approval (Sponsor) | Single-stage; 14-day deadline; escalate to Sponsor's manager at day 10 |
| 5 | Update `extension_LastAttestationDate` | On approval |
| 6 | Capture signature artifact | Separate signature/evidence service → evidence pack (Section 11) |
| 7 | On rejection / non-response | Trigger cascade — see Section 9 |

The former Graph creation example is withdrawn: `category = "custom"` is not a documented workflow category; the stable date trigger does not accept `extension_LastAttestationDate`; and `userType eq 'AgenticUser'` is invalid. The task ID formerly labeled "Request Sponsor attestation" identifies **Add user to groups**, not an approval task. Notification IDs/arguments and extension invocation were also not valid deployment definitions. See the [workflow schema](https://learn.microsoft.com/en-us/graph/api/resources/identitygovernance-workflow?view=graph-rest-1.0), [date-trigger schema](https://learn.microsoft.com/en-us/graph/api/resources/identitygovernance-timebasedattributetrigger?view=graph-rest-1.0), and [task catalog](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-tasks).

Before automation is accepted, supply the actual flow definition, approved permissions, explicit rejection/timeout handling, and evidence of a complete approval cycle. An enabled workflow or an email notification is not proof of attestation.

### 8.2 Zone 3 Quarterly Attestation with Dual Sign-Off

The Z3 workflow extends Z2 with:

- A second-stage approval task targeting the **Compliance Reviewer** (`sg-compliance-reviewers`) after Sponsor approval.
- Tighter escalation (7-day Sponsor SLA, 7-day Compliance SLA).
- Auto-trigger of Section 9.4 emergency cascade if either stage rejects or both stages lapse 7 days past escalation.

Implement these stages in the approved custom approval service. Resolve the actual named reviewers and preserve each decision separately; membership in `sg-compliance-reviewers` does not itself produce a co-signature. No built-in Lifecycle Workflows approval task or deployable Z3 flow is supplied here.

### 8.3 Backup Owner Reachability Test (Semi-Annual)

The proposed custom process `FSI-Backup-Owner-Reachability` runs twice per calendar year on dates defined in the firm's operating calendar. It sends a confirmation request to every Backup Owner of record. Non-response requires a Sponsor notification and a 14-day window to designate a replacement Backup Owner before the agent moves to Deprecated. No native recurring workflow or automated transition is deployed by this document.

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

`FSI-Owner-Departure-Cascade` is a custom process requirement. Join the departing **human** owner's approved personnel signal to the inventory, identify affected agents and backups, obtain the required reassignment authorization, and verify the actual source ownership after mutation. The former `groupBasedTrigger` example conflated group removal with an `accountEnabled` change and is not a supported deployment definition. Do not infer a departure event, successor acceptance, or successful ownership update from group membership alone.

### 9.3 Sponsor Departure Workflow

The proposed custom cascade follows 9.2 and considers the **Sponsor's manager** (resolved via the Entra `manager` relationship) as an interim Sponsor under the eligibility rules in 9.5. It notifies the AI Governance Lead and, for Z3, the Compliance Reviewer. A proposed `FSI-Z3-Sponsor-Vacant` review needs either an explicitly supported access-review resource/assignment scope or a custom business-review record; naming it does not create an Entra review of an arbitrary inventory row. Cascade completes only when:

1. A new Sponsor is named and accepts (recorded as approval artifact).
2. The new Sponsor signs an out-of-cycle attestation within the grace period.
3. The native agent identity sponsor relationship, any separately required agent-user relationship, and the custom inventory mapping are updated and independently read back. Updating `extension_SponsorId` alone does not assign native sponsorship.

The manager-hierarchy fallback, reviewer acceptance, out-of-cycle attestation, zone timer, and inventory write-back are custom steps. A notification to the departing sponsor's manager does not assign that manager as a sponsor. Record the native task result and the independently verified sponsorship change as different evidence artifacts.

### 9.4 Emergency Decommissioned Transition

Triggered when:

- Grace period expires without a successor Sponsor or Owner.
- Compliance Reviewer issues a regulatory veto.
- AI Governance Lead determines the agent represents an unmitigated risk.
- DSPM for AI ([Control 1.6](../1.6/portal-walkthrough.md)) produces an alert triaged as Severity 1 under the firm's incident process and no Owner can be reached.

**Required custom behavior.** An approved containment implementation must perform and verify each applicable action; this list is not delivered by a built-in emergency workflow:

1. Records `Decommissioned` in the custom governance lifecycle column and its registered mappings.
2. Performs supported containment on the actual agent identity and, if present, its separate agent user account; verifies each result independently.
3. Removes group memberships that grant data access.
4. Removes the agent from active Copilot Studio / Power Platform / Agent 365 environments (preserves the artifact for forensic review per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)).
5. Files an emergency-cascade record with the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) intake queue.
6. Notifies AI Governance Lead, on-call Compliance, Sponsor's chain of command, and Security Operations.

Use the documented control for each source identity and publishing surface. Disabling a human workflow subject is not equivalent to disabling an agent identity or its paired agent user; changing the governance register is not runtime containment. Preserve source-specific action results, post-action read-backs, incident references, and any failures. Do not delete forensic artifacts or claim that one directory mutation retires an agent across all environments.

!!! warning "Emergency cascade is reversible only via re-onboarding"
    This is a **framework process rule**, not a native irreversibility guarantee. Once an agent is in Decommissioned state, restoration requires returning it to Draft and walking the full lifecycle again, including a new In Review → Approved gate with fresh signatures. This is intentional and supports the supervisory expectation that an agent without a current responsible party cannot resume operation without renewed risk acceptance.

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

This section defines a **custom business-approval correlation design**, not one native approval transaction. Record Sponsor decisions separately from native administrative approvals and actual enforcement. Some Microsoft 365 agent publishing experiences already include permission/consent review; a custom card must not bypass those role and permission boundaries.

### 10.1 The Three Approval Surfaces

| Surface | What it gates | Native admin |
|---|---|---|
| **Entra admin consent workflow** | Requests for application permissions requiring admin consent | Designated reviewer with the appropriate administrative role; Graph reads requests but cannot approve/deny them |
| **Entra agent identity administration / access-package approvals** | Documented identity lifecycle actions and supported entitlement requests | Agent ID / entitlement administrators and authorized sponsors, as applicable; no universal agent-change approval API is established here |
| **Copilot Studio publishing and Microsoft 365 agent requests** | Distinct authoring/publishing and organization publication/deployment actions | Authorized maker / administrator for the selected surface; not a universal Power Platform approval-center webhook |

Correlate business decisions with the specific native request IDs and results. A Sponsor response can authorize the organization's next step, but does not grant platform privileges or automatically complete native consent, publication, or deployment.

### 10.2 Unified Flow Architecture

```
┌────────────────────────────────────────────────────────────┐
│  Trigger source (any of):                                  │
│  • Validated native request / reviewed intake record        │
│  • Custom agent change request in governance register       │
│  • Selected publication / deployment request                │
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
│  • Records business approval (not native authorization)     │
│  • Routes native actions to authorized administrators      │
│  • Tracks enforcement and evidence completion separately   │
│  • Notifies Owner + Backup + (Z3) Compliance Reviewer      │
└────────────────────────────────────────────────────────────┘
```

### 10.3 Implementation Outline

1. Provision the custom request table and select a documented intake mechanism for the chosen platform. `agt_AgentApprovalRequest` is a proposed Dataverse table, not a built-in queue. Do **not** subscribe to `directory/auditLogs`: directory audit logs are not a documented [Graph change-notification resource](https://learn.microsoft.com/en-us/graph/change-notifications-overview). An audit event about an executed grant is not a pre-action approval request.
2. Resolve the actual agent identity and business reviewers from the governance register. A [Power Automate Approvals](https://learn.microsoft.com/en-us/connectors/approvals/) action can collect a decision and responder data; it does not automatically produce a cryptographic signature over the evidence pack.
3. Record the business approval, then route native actions to authorized operators. Microsoft explicitly states that [Graph cannot approve or deny admin consent requests](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/review-admin-consent-requests). Do not replace this limitation with a direct permission grant disguised as approval.
4. Use the actual [Microsoft 365 agent requests experience](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-requests) or the documented operation for the selected Copilot Studio / deployment surface. No generic Agent ID change-request API, Power Platform agent-approval-center webhook, or universal write-back operation is established by this playbook. [Connector action control](https://learn.microsoft.com/en-us/power-platform/admin/connector-action-control) is data policy, not this approval mechanism.
5. For Z3, collect the separate Compliance Reviewer decision. Track business approval, native approval, source enforcement, and evidence publication as distinct states, with timeout/rejection handling and independent read-backs.

!!! tip "Why unify"
    Examiners ask "show me the supervisor's approval" — singular. A unified flow lets you produce one signed artifact per change rather than three correlated artifacts. This matches the FINRA Rule 3110 expectation that supervision is a documented decision, not a series of disjoint clicks.

### 10.4 Configuration Reference

The [PowerShell Setup](./powershell-setup.md) playbook supplies read-only registration collection and a signed file catalog. It does **not** supply deployable approval flows, Adaptive Card schemas, sponsor signatures, lifecycle mutations, or the evidence-pack helpers described here. Those are separate implementation prerequisites and must not be inferred from a successful collection run.

---

## 11. Sponsorship Evidence Pack

Every attestation, every cascade execution, and every emergency decommission produces a **sponsorship evidence pack**. Examiners and internal audit consume these packs directly; the format is therefore deliberately rigid.

### 11.1 Pack Contents

| Artifact | Format | Source | Required for |
|---|---|---|---|
| Attestation request record | JSON | Deployed custom approval service; native workflow correlation where applicable | All quarterly attestations |
| Sponsor signature | Organization-defined, identity-bound signature format | Separately implemented signing service; not automatic Approvals / Verified ID output | All quarterly attestations |
| Compliance Reviewer co-signature (Z3) | Organization-defined, identity-bound signature format | Separately implemented signing service | Z3 attestations and material changes |
| Activity pack snapshot | PDF + raw JSON | Generated by Section 8.1 task 1 | All quarterly attestations |
| DSPM alert summary (last 90d) | CSV | DSPM for AI export | Z2 + Z3 attestations |
| Communication Compliance disposition (last 90d) | CSV | Control 1.10 export | Z3 attestations and any agent under supervised-comms scope |
| Material change log (last 90d) | CSV | Control 3.1 inventory diff | All attestations |
| Approval timestamp chain | JSON | Deployed business approval service, correlated with native run records | All attestations |
| Audit trail correlation IDs | JSON | Purview Audit + Sentinel custom table | All attestations |
| SHA-256 hash of pack contents | Text file `pack.sha256` | Computed at pack close | All attestations |
| SHA-256 of previous pack (chain) | Text file `previous.sha256` | Read from previous pack | All attestations after the first |

### 11.2 Hash Chaining for Tamper Evidence

Each pack contains the SHA-256 of the prior pack for the same agent, producing a per-agent hash chain that supports SEC 17a-4(f) WORM-equivalent verification:

**Implementation prerequisite:** no `Export-AttestationRecord`, `Export-SponsorSignature`, `Get-PreviousPackHash`, or `Publish-EvidencePackToWorm` implementation is supplied by the peer collection playbook. The former function was illustrative, not an executable evidence pipeline, and is withdrawn.

The approved pack builder must hash an unambiguous manifest of relative filenames, file sizes, and SHA-256 digests; include the agent ID, cycle ID, and previous pack digest in the signed attestation. Concatenating file bytes without names or boundaries is not a sufficient manifest. Reject missing required artifacts and unexpected files, and independently test verification after transfer. A hash chain is tamper evidence, not a retention setting or a signature identifying the human approver. Apply and verify the actual destination's retention / record settings separately.

### 11.3 Cryptographic Sponsor Signatures (Recommended for Z3)

For Z3 agents, use a separately specified identity-bound signing solution. **AgentSponsorAttestation** is a proposed custom credential design, not a Microsoft template or a deployed signing service.

1. Enforce and record any required phishing-resistant authentication in the attestation application separately; Verified ID issuance does not prove that FIDO2 or Windows Hello for Business was used.
2. In [Verified ID](https://learn.microsoft.com/en-us/entra/verified-id/decentralized-identifier-overview), the **issuer signs the credential** and the holder can sign a presentation. Neither automatically proves that the human Sponsor signed an approval statement or pack digest. Define subject/holder binding, the exact signed statement and digest, nonce/replay controls, and trusted time.
3. The [issuance API](https://learn.microsoft.com/en-us/entra/verified-id/issuance-request-api) does not promise an archival `sponsor-signature.jws` response. Claims/validity require a configured credential contract. The [presentation API](https://learn.microsoft.com/en-us/entra/verified-id/presentation-request-api) returns verification results; its optional receipt is for debugging, not a stable long-term signature format.
4. The hosted verifier and [revocation checks](https://learn.microsoft.com/en-us/entra/verified-id/how-to-issuer-revoke) have online dependencies. A `did:web` resolver retrieves trust material; it is not a complete offline credential verifier. Open-standard verification may avoid Microsoft's hosted verifier, but this playbook does not establish offline archival verification.
5. Test key rotation, domain/DID loss, credential expiry, revocation-at-decision evidence, and preservation of trust material over the required archive lifetime. A proposed 100-day credential lifetime does not establish multi-year verifiability.

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

**Technical implementation boundary:** apply and verify the chosen record controls in supported storage. An ordinary retention label permits behavior different from a locked record or regulatory record; naming a label does not make content immutable. Labels do not protect arbitrary Dataverse rows, local files, or Log Analytics tables. Define file preservation, native Lifecycle Workflows history export (the portal offers up to 30 days), Purview audit retention, and Log Analytics analytics/long-term retention separately. A seven-/ten-year policy target neither configures these services nor recovers expired data. See [Records Management](https://learn.microsoft.com/en-us/purview/records-management), [Audit](https://learn.microsoft.com/en-us/purview/audit-solutions-overview), and [Log Analytics retention](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure).

---

## 12. Verification, Reporting, and KQL

### 12.1 Quarterly Compliance Report

The former `Get-SponsorshipAttestationReport` example is withdrawn: it used the invalid `userType eq 'AgenticUser'` filter, unregistered extension aliases, and an optional agent-user population as if it were the complete inventory. The documented agent-user collection is [`/users/microsoft.graph.agentUser`](https://learn.microsoft.com/en-us/graph/api/agentuser-list?view=graph-rest-1.0); agent identities and platform agent records must be reconciled separately.

A deployed report must read the authoritative inventory and output agent/source IDs, zone, policy state, actual source enforcement state, current named role assignments, required cycle/due date, approval references, evidence-pack verification, and observation freshness. Missing/invalid dates, unresolved people, missing native sponsorship, or absent telemetry must be explicit **Unknown / ManualEvidenceRequired**, not a synthetic old date or zero overdue rows. Check employment, eligibility, acceptance, separation of duties, and both Z3 Sponsors; populated strings alone are not staffing proof. Apply the calendar and grace rules explicitly rather than substituting a fixed 90-day offset.

### 12.2 KQL — Attestation Audit Trail

The former query is withdrawn. [Lifecycle Workflows auditing](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-audits) documents **Other**, **TaskManagement**, and **WorkflowManagement** categories, not the asserted `Category == "LifecycleWorkflows"` contract. A workflow display name is not necessarily `OperationName`; the first target/detail is not necessarily an agent/workflow ID; an initiating application is not the human approver.

Before writing a production query, configure [Entra diagnostic export](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-integrate-activity-logs-with-azure-monitor-logs), inspect actual operations, target types, actors, and named details in the [`AuditLogs` schema](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs), and test against known native task events. Correlate those events with independently exported business-approval records. A 90-/120-day query requires prior ingestion and sufficient queryable retention; the 30-day native history cannot supply it retrospectively.

### 12.3 KQL — Overdue Attestations Alert

`AgentInventory_CL` is a proposed custom table, not a Microsoft-provided Control 3.1 feed. Implement its exact schema, authorized ingestion/DCR transformation, freshness heartbeat, and retention before publishing a query. The [Logs Ingestion API prerequisites](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview) include an existing destination table and matching data collection configuration.

Use the same due-date/grace policy as the report. Alert separately on missing/stale ingestion, missing dates, invalid relationships, and overdue approvals; an empty result set is not a clean attestation. After known-event query tests, separately configure a [Sentinel scheduled analytics rule](https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-custom) and notification automation. No incident rule or Sponsor routing is deployed by this playbook.

### 12.4 Verification Checklist

1. Each Active agent has the supported native sponsorship and source ownership required for its object type, reconciled with actual registered inventory mappings for Sponsor / Backup Owner. Populated logical `extension_*` aliases are insufficient.
2. Each Z3 Active agent has named eligible Sponsors and a Compliance Reviewer, with actual assignments, acceptance, and role separation verified.
3. The custom attestation record is within the approved calendar and zone/stage deadline in Sections 6 and 8; do not substitute one universal 14-day timer for all stages.
4. Record the actual native mover/leaver workflow IDs, versions, subject scopes, enabled/scheduling state, and selected task definitions. Verify the custom quarterly, reachability, cascade, and containment processes separately; matching `FSI-*` display names do not prove implementation.
5. Reconcile every expected approval cycle with completed named reviewer decisions and preserved artifacts. Reconcile each departure with native task outcomes, accepted reassignment, and source read-backs. Export history before expiry; an enabled or completed workflow alone is not PASS.
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
| Workflow enabled but never runs | Scheduling, trigger, or subject scope is wrong | Check enabled **and** scheduling state and documented [execution conditions](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-execution-conditions). Never set `userType` to `AgenticUser` |
| Sponsor not receiving email | Recipient resolution, sender-domain configuration, or mail flow | Inspect the actual task configuration and delivered headers with the Exchange Online Admin; do not allow-list an assumed sender |
| Approval received but signature missing | Signing/evidence step absent or failed | Inspect the deployed approval, signing, callback, and publication steps independently; read-only directory permissions do not generate signatures |
| Source reassignment and inventory disagree | Custom synchronization absent or failed | Identify the actual connection/error and compare before/after source relationships; do not refresh credentials without a diagnosed authentication failure |
| Compliance stage stuck | Reviewer assignment or custom flow failure | Resolve named recipients and inspect approval/run state. Purview administrator privilege is not required merely to answer an approval |
| Emergency containment incomplete | Wrong target, permissions, or missing surface-specific action | Identify the exact identity/resource and documented least-privilege operation; verify each source read-back rather than granting blanket permissions |
| Hash chain breaks | Missing/modified files, manifest defect, wrong predecessor, or publication failure | Preserve the discrepant artifacts and investigate. Verify any archive and record settings independently before recovery |
| Manager fallback cannot find eligible successor | Custom fallback exhausted or not implemented | Route explicitly to the AI Governance Lead; native direct-manager transfer does not perform the three-hop policy |
| Sponsor departure not detected | Authoritative HR signal or configured trigger/scope missing | Test the documented human leaver trigger and ingestion freshness; account disablement and group removal are distinct signals |
| Failures hidden by workflow completion | `continueOnError` or launch-and-continue masks downstream failure | Set and inspect `continueOnError` explicitly; require completed approval/evidence and source results independently of native run status |

Refer to [Troubleshooting](./troubleshooting.md) for registry-level issues and the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) for cascade-driven incident response.

---

## 14. Related Resources

### Framework and controls

- [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)
- [Control 1.6 implementation playbooks](../1.6/portal-walkthrough.md)
- [Agent Identity Architecture](../../../framework/agent-identity-architecture.md)
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)

### Peer playbooks (Control 1.2)

- [Portal Walkthrough](./portal-walkthrough.md)
- [PowerShell Setup](./powershell-setup.md)
- [Verification Testing](./verification-testing.md)
- [Troubleshooting](./troubleshooting.md)

### Microsoft Learn

- [Microsoft Entra Identity Governance — Lifecycle Workflows overview](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows)
- [Microsoft Entra Identity Governance — Access reviews](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Microsoft Entra ID Governance — Custom workflow tasks](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-extensibility)
- [Microsoft Entra Verified ID — Overview](https://learn.microsoft.com/en-us/entra/verified-id/decentralized-identifier-overview)
- [Microsoft Entra Agent ID — Overview](https://learn.microsoft.com/en-us/entra/agent-id/what-is-agent-id-platform)
- [Power Platform — Connector action control and consent](https://learn.microsoft.com/en-us/power-platform/admin/connector-action-control)
- [Microsoft Purview — Records Management and retention labels](https://learn.microsoft.com/en-us/purview/records-management)
- [Microsoft Purview — Audit (Standard and Premium)](https://learn.microsoft.com/en-us/purview/audit-solutions-overview)
- [Microsoft Sentinel — Custom log tables and analytics rules](https://learn.microsoft.com/en-us/azure/sentinel/create-custom-connector)

### Regulatory references

- FINRA Rule 3110 — Supervision
- FINRA Rule 3120 — Supervisory control system
- FINRA Rule 4511 — General requirements for books and records
- FINRA RN 24-09 / Rule 3110 — Generative AI member firm responsibilities
- SEC Rule 17a-4(b)(4) and 17a-4(f) — Records preservation
- SOX §302 / §404 — Officer certification and ICFR
- GLBA §501(b) and FTC Safeguards 16 CFR §314.4(c) — Information security program
- NYDFS 23 NYCRR Part 500.07 (access privileges) and 500.16 (incident response)
- OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) — Sound practices for model risk management
- Federal Reserve SR 26-2 (formerly SR 11-7) — Guidance on model risk management
- NIST AI Risk Management Framework — GOVERN 1.4 and GOVERN 1.6

## Documentation verification ledger

**Verified 2026-10-18 against live official Microsoft documentation.** This was a technical source review, not a compliance determination, UI verification, deployment, or tenant test. The prior April 2026 source stamp did not establish an executable implementation.

### Discrepancies and sources

| Rechecked claim / discrepancy | Correction and primary Microsoft source |
|---|---|
| Identity population, optional agent user, native sponsorship versus custom metadata | Agent identities, optional agent users, and platform records require distinct IDs / collection. `userType = AgenticUser` is invalid; use the [documented agent-user collection](https://learn.microsoft.com/en-us/graph/api/agentuser-list?view=graph-rest-1.0). Verify [optional user creation](https://learn.microsoft.com/en-us/entra/agent-id/agent-users) and [native relationship restrictions](https://learn.microsoft.com/en-us/entra/agent-id/agent-owners-sponsors-managers). |
| Unregistered extension aliases and six-state Dataverse assumption | Register [directory extensions](https://learn.microsoft.com/en-us/graph/api/application-post-extensionproperty?view=graph-rest-1.0) and record their actual target/name mapping. The custom governance lifecycle is not the native Dataverse [`statecode` / `statuscode` pair](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/update-delete-entities-using-web-api). |
| P2 includes Lifecycle Workflows; blanket preview task labels | Employee workflows require Governance / Suite, not P2 alone. Check [scenario-specific licensing](https://learn.microsoft.com/en-us/entra/id-governance/licensing-fundamentals). The current [three native sponsor tasks](https://learn.microsoft.com/en-us/entra/id-governance/agent-sponsor-tasks) have separate prerequisites and no preview label in that guide. |
| Default-on transfer, per-agent quarterly trigger, backup cascade, acceptance, and suspension | Native sponsor tasks apply to **human mover/leaver workflows** and require explicit configuration. Direct-manager transfer is not owner reassignment, three-hop fallback, business acceptance, or containment. Quarterly / semiannual processes remain custom. See [task scope](https://learn.microsoft.com/en-us/entra/id-governance/agent-sponsor-tasks) and [execution conditions](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-execution-conditions). |
| Invalid quarterly/departure/emergency JSON and approval task IDs | Withdrawn rather than substituted with another speculative payload. Validate [workflow categories/schema](https://learn.microsoft.com/en-us/graph/api/resources/identitygovernance-workflow?view=graph-rest-1.0), [date-trigger attributes](https://learn.microsoft.com/en-us/graph/api/resources/identitygovernance-timebasedattributetrigger?view=graph-rest-1.0), and [task definitions](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-tasks). The former approval GUID is an **Add user to groups** task. |
| Invented sender / integration switch; schedule mistaken for recurrence | Use documented [email settings](https://learn.microsoft.com/en-us/entra/id-governance/customize-workflow-email) and [workflow settings](https://learn.microsoft.com/en-us/graph/api/resources/identitygovernance-lifecyclemanagementsettings?view=graph-rest-1.0). A 1–24-hour evaluation schedule (default 3 hours) is not a quarterly calendar or immediate SLA. |
| Multi-day Logic App callback / placeholder extension task | Register a compatible [consumption Logic App extension](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-extensibility); [callback wait is 30 minutes–3 hours](https://learn.microsoft.com/en-us/graph/api/resources/identitygovernance-customtaskextensioncallbackconfiguration?view=graph-rest-1.0). Long approvals require separate durable state. |
| One Graph approval write-back / audit subscription / generic approval center | Graph [cannot approve or deny admin consent requests](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/review-admin-consent-requests). `directory/auditLogs` is not a documented [subscription resource](https://learn.microsoft.com/en-us/graph/change-notifications-overview). Use the actual [agent requests experience](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-requests); [connector action control](https://learn.microsoft.com/en-us/power-platform/admin/connector-action-control) is not a universal approval API. |
| Approvals / Verified ID automatically sign as the human Sponsor | [Approvals](https://learn.microsoft.com/en-us/connectors/approvals/) records decisions. In [Verified ID](https://learn.microsoft.com/en-us/entra/verified-id/decentralized-identifier-overview), the issuer signs the credential and the holder signs a presentation; neither automatically binds the human Sponsor to this pack digest. [Issuance](https://learn.microsoft.com/en-us/entra/verified-id/issuance-request-api) does not return the promised archival JWS; [presentation receipts](https://learn.microsoft.com/en-us/entra/verified-id/presentation-request-api) are debugging output. [Revocation/trust](https://learn.microsoft.com/en-us/entra/verified-id/how-to-issuer-revoke) introduces online dependencies. |
| Executable evidence helper, byte-concatenation digest, hash as immutability | Withdrawn placeholder helper; require canonical file/digest manifest, explicit human-to-statement binding, and independent archive verification. [Records Management](https://learn.microsoft.com/en-us/purview/records-management) distinguishes ordinary retention, records, and regulatory records; hashes do not configure any of them. |
| Guaranteed audit category / approver fields and retrospective long lookback | Use documented [audit categories](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-audits), [history limits](https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflow-history), and observed [`AuditLogs` schema](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs). Native history offers up to 30 days. Custom approvals, [Purview Audit](https://learn.microsoft.com/en-us/purview/audit-solutions-overview), and [Log Analytics retention](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure) are separate. |
| Ready-made inventory KQL / automatic alerting and empty-results PASS | `AgentInventory_CL` requires deployed [ingestion and schema](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview), known-event tests, freshness monitoring, and a separately configured [analytics rule](https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-custom). Missing data/implementation is Unknown / ManualEvidenceRequired. |
| Wrong DSPM dependency and evidence references | Corrected Control 2.1 (Managed Environments) links to Control 1.6 (DSPM for AI) and evidence-pack references to Section 11. This changes routing, not regulatory interpretation. |

**Remaining implementation unknowns:** actual registered schemas, task metadata, source mutation permissions, approval/signature service, cross-surface containment, collection completeness, retention/trust configuration, and tenant rollout must be demonstrated separately. Task-arguments documentation contains inconsistent extension IDs/capitalization; no replacement deployment payload is claimed validated. No implementation script, schema, workflow, configuration, or live tenant was changed by this review.

### Downstream artifacts reviewed

Paths below are relative to `docs/` unless stated otherwise. A family listing explicitly names each reviewed peer file; unchanged means no propagation of the corrected sponsorship claims was needed, not that every unrelated claim was re-verified.

| Artifact(s) | Disposition and reason |
|---|---|
| `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` | **Changed:** source corrections, evidence boundaries, canonical verification date, and this ledger. |
| `controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md` | **Changed:** distinguishes organizational sponsorship process from delivered automation. |
| `playbooks/control-implementations/1.2/portal-walkthrough.md`, `verification-testing.md`, `troubleshooting.md` | **Changed:** corrected section/routing references, custom implementation boundary, native versus custom evidence, signature binding, and departure-policy acceptance criteria. |
| `playbooks/control-implementations/1.2/powershell-setup.md` | **Unchanged:** already explicitly supplies read-only collection / catalog verification, not sponsor mutation or custom orchestration. |
| `framework/agent-identity-architecture.md`, `framework/governance-fundamentals.md` | **Changed:** removed fabricated workflow payload / default-on transfer promises, corrected licensing/task availability, separated custom quarterly reviews and containment. |
| `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md` | **Changed:** configured native task scope and licensing, no unconditional transfer or native acceptance timer. |
| `playbooks/control-implementations/2.26/portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md` | **Changed:** setup, illustrative helper assumptions, withdrawn invalid Pester assertions, outcome checks, and incident response now use the same native/custom boundary. |
| `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md` | **Changed:** only factual product cells/statements about native transfer, preview status, and custom attestation logging; regulatory requirements/mappings were not reinterpreted. |
| `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`; `playbooks/control-implementations/3.6/portal-walkthrough.md`, `troubleshooting.md` | **Changed:** configured transfer / actual outcome, not default-on behavior or guaranteed processing latency. |
| `playbooks/control-implementations/3.6/powershell-setup.md`, `verification-testing.md` | **Unchanged:** custom reconciliation / approved remediation is not asserted to be a native default transfer or sponsor attestation. |
| `reference/agent-365-capabilities-summary.md` | **Changed:** coverage describes custom process requirements, not comprehensive delivered attestation automation. |
| `reference/agent-essentials-control-mapping.md` | **Unchanged:** high-level sponsorship / inventory mapping does not promise the withdrawn trigger, signing, or cascade implementation. |
| `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`; `playbooks/control-implementations/3.1/portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md` | **Unchanged:** separate canonical inventory, custom lifecycle policy, and collection/signing checks; no source-specific native workflow payload or default transfer promise to propagate. |
| `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`; `playbooks/control-implementations/1.7/portal-walkthrough.md`, `powershell-setup.md`, `troubleshooting.md` | **Unchanged:** separate audit capture/preservation configuration; no custom sponsor approval implementation supplied. |
| `playbooks/control-implementations/1.7/verification-testing.md` | **Changed:** clarifies Verified ID credential/presentation versus a named human's signature over the evidence manifest. |
| `controls/pillar-1-security/1.10-communication-compliance-monitoring.md`; `playbooks/control-implementations/1.10/portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md` | **Unchanged:** correspondence supervision/export is separate from executing sponsorship approvals, signatures, or native transfer. |
| `playbooks/control-implementations/1.6/portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md` | **Unchanged:** correct DSPM dependency; these guides do not deploy the custom sponsorship cascade. |
| `playbooks/control-implementations/2.1/portal-walkthrough.md`, `powershell-setup.md` | **Unchanged:** Managed Environments, not DSPM; corrected the source's misplaced links instead. |
| `playbooks/incident-and-risk/ai-incident-response-playbook.md`, `playbooks/agent-lifecycle/agent-decommissioning.md` | **Unchanged:** separate authorized incident/retirement procedures, not an automatic sponsor-workflow deployment. |
| `images/1.2/EXPECTED.md`, `images/2.26/EXPECTED.md` | **Unchanged:** registry / generic workflow evidence checklists do not specify the withdrawn fabricated task payload or default-on transfer. No screenshots or UI verification were produced. |
| Repository `CHANGELOG.md` | **Changed:** records this technical correction and its documentation-only boundary. |

### Generated artifacts

No `scripts/build_content_graph.py` or generated documentation dependency graph exists in this checkout. The assessment code graph is unrelated to these prose changes.

| Artifact | Generator / check and disposition |
|---|---|
| `javascripts/control-explorer-data.json` | `python scripts/gen_explorer_data.py` **passed**; regenerated payload is unchanged (only generation time differed, so timestamp-only churn was discarded). `python scripts/check_explorer_data_drift.py --check` passed. No mirrored verification-date field exists. |
| Repository `tests/e2e/fixtures/render-expectations.json` | `node scripts/generate-render-expectations.mjs --out tests/e2e/fixtures/render-expectations.json` **passed**; 697 pages, unchanged semantic oracle. Timestamp-only churn discarded; the same command with `--check` passed. |
| Repository `maintainers-local/researcher-package/01-Pillar-1-Security-Controls.md`, `02-Pillar-2-Management-Controls.md`, `03-Pillar-3-Reporting-Controls.md`, `04-Pillar-4-SharePoint-Controls.md` | `python scripts/compile_researcher_package.py` **passed**, regenerating four local/ignored pillar compilations including the changed controls. These are not publication artifacts or a substitute for source controls. |
| `javascripts/change-radar-data.json`; FAQ JSON-LD; assessment coverage report | **Unchanged:** no release-radar, FAQ source, or evaluator wiring changed. `check_change_radar_data_drift.py --check`, `check_faq_jsonld_drift.py --check`, and `generate_coverage_matrix.py --check` passed. |
| `controls/CONTROL-INDEX.md`; repository `mkdocs.yml` | **Unchanged:** no control ID/title/path, playbook title/path, or navigation entry changed. `check_manifest_doc_drift.py --check` and `verify_xref_graph.py` passed. |
| Repository `site/` pages, search index, sitemap, and generated metadata | Regenerated from current prose by `mkdocs build --strict`; local/ignored outputs, not hand-edited or committed. Built-site completeness, metadata, and internal-link checks are recorded with exact results in the local publication handoff. |
| `version.json` | Build-hook SHA/time output is not source verification metadata. Discard incidental local build churn; publication regenerates it for the published commit. |

---

[Back to Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) · [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Verification Testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (technical documentation verified 2026-10-18; no tenant/UI execution)*
