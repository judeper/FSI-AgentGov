# Control 1.14 — Portal Walkthrough: Data Minimization and Agent Scope Control

**Control:** [1.14 Data Minimization and Agent Scope Control](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md)
**Audience:** Power Platform Admin, AI Administrator, SharePoint Admin, Purview Compliance Admin, Purview Data Security AI Admin, Entra Identity Governance Admin, AI Governance Lead
**Surfaces:** Copilot Studio · Power Platform Admin Center (PPAC) · Microsoft Purview portal (DSPM for AI, Audit, DLP, Alert policies, Activity Explorer) · SharePoint Admin Center (SPAC) · Microsoft Entra admin center · Microsoft Sentinel (Zone 3 only)
**Estimated time:** 8–14 hours initial setup per zone (excluding Control 1.2 inventory build and Control 4.6 SharePoint enforcement); monthly review cadence in Zone 3, quarterly in Zone 2, annual in Zone 1
**Last UI Verified:** April 2026

!!! danger "READ FIRST — boundaries with Controls 1.2, 1.4, 1.13, 1.18, and 4.6"
    This walkthrough governs **per-agent data minimization**: which grounding surfaces an agent may reach (SharePoint libraries, OneDrive, Dataverse tables, Graph connectors, file uploads, image uploads, public web, enterprise URLs, connector references, declarative agents / API plugins), how that scope is approved, and how scope drift is detected.

    | If you need to … | Use … |
    |---|---|
    | Establish the **system-of-record agent inventory** (agents, owners, environments, knowledge sources) | [Control 1.2 — Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
    | Author **general Power Platform DLP** policies (connector classification across all makers, not just agent-specific connectors) | [Control 1.4 — Advanced Connector Policies](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) |
    | Apply **Restricted Content Discovery (RCD)**, **Restricted SharePoint Search (RSS ≤100-site allowed list)**, or run **Data Access Governance (DAG)** reports | [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) |
    | Author **Sensitive Information Types (SITs)**, EDM, document fingerprints, or trainable classifiers | [Control 1.13 — SITs and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) |
    | Configure **OAuth scopes**, application permissions, or RBAC for agent identities | [Control 1.18 — RBAC](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) |
    | Configure **endpoint DLP** for file upload egress on user devices | [Control 1.17 — Endpoint DLP for AI Agents](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) |

    Control 1.14 **consumes** all six of those controls; it does not replace any of them. If a step below appears to overlap, the canonical authoring surface is the linked control — this walkthrough only configures the agent-scope-specific knobs.

!!! warning "This control supports — it does not guarantee — compliance"
    The portal steps below help support GLBA 501(b) (safeguards), SEC Regulation S-P (2024 amendments — written safeguards and 30-day customer notification), FINRA Rule 4511 (books and records), FINRA Rule 3110 + Regulatory Notice 25-07 (AI supervision), and CCPA §1798.100 (data minimization for non-GLBA personal information). They do not by themselves satisfy any single rule. Your compliance, legal, and risk teams remain accountable for full obligation coverage. Implementation requires named operators, change records, and zone-appropriate approvals; organizations should verify feature parity in their sovereign cloud at deploy time.

---

## What this walkthrough covers

| Surface | What you will configure | Why it matters for Control 1.14 |
| --- | --- | --- |
| **Copilot Studio → agent → Knowledge** | Scope each knowledge source to a specific document library or folder; toggle public web grounding off for Zone 3; constrain file upload and image upload posture per zone. | Per-agent grounding surface minimization. |
| **Copilot Studio → agent → Settings → Generative AI** | Disable web search for Zone 3 agents handling NPI; review tone, instructions, and orchestration mode for scope-appropriate behavior. | Removes the "anything on the public internet" grounding path from regulated agents. |
| **PPAC → Security → Data and privacy → Data policies** | Classify the Copilot Studio knowledge connectors and the connectors used as agent actions into Business / Non-Business / Blocked groups; scope policies to environments hosting Zone 2 / Zone 3 agents. | Constrains which connectors an agent may use; complements but does not replace OAuth scope minimization (Control 1.18). |
| **Purview portal → DSPM for AI → Policies + Activity Explorer** | Enable the recommended one-click DSPM-for-AI policies; review sensitive-interactions activity at the zone cadence; export weekly evidence. | Primary detective surface for sensitive-data interactions with Copilot and agents. |
| **Purview portal → Data loss prevention → Policies** | Author DLP policies at the **Microsoft 365 Copilot** location with rules tied to sensitivity labels and SITs (Control 1.13). | Runtime enforcement that excludes labeled / SIT-matched content from agent grounding. |
| **Purview portal → Audit → Search** | Discover the canonical Copilot and Power Platform audit operations in your tenant (record types `CopilotInteraction`, `BotsRuntimeService`, `MicrosoftFlow`, `PowerAppsPlan`, `AzureActiveDirectory`); export evidence. | Forensic and supervisory record (FINRA 4511, FINRA 3110 / 25-07). |
| **Purview portal → Policies → Alert policies** *(or Defender XDR → Email & collaboration → Policies & rules → Alert policy)* | Create alert policies on discovered audit operations. For Zone 3, replace with a Microsoft Sentinel analytic rule sourcing the M365 connector. | Near-real-time scope-drift detection. |
| **Microsoft Entra admin center → Identity governance → Access reviews** | Run scheduled access reviews on agent identities (Entra Agent ID), connector connections, and SharePoint groups gating knowledge sources. | Periodic recertification (FINRA 3110, OCC 2011-12). |
| **SPAC** *(coordinate with Control 4.6)* | Reconcile the §3 grounding inventory against the Control 4.6 RCD exclusion list and RSS allowed list. | Ensures inventory-time minimization is enforced at the tenant SharePoint layer. |

What this walkthrough does **not** cover (use the linked playbooks instead):

- Bulk PowerShell automation across thousands of agents → see [`powershell-setup.md`](powershell-setup.md).
- Repeatable verification queries (KQL, Graph, audit search) you run after each change → see [`verification-testing.md`](verification-testing.md).
- Common failure modes and recovery (broken agents after DLP block, false-positive scope-drift alerts, OneDrive vs SharePoint surface confusion) → see [`troubleshooting.md`](troubleshooting.md).

---

## §0 Coverage boundary, surface inventory, and portal vs PowerShell matrix

### 0.1 In scope vs out of scope

In scope for Control 1.14 — and for this walkthrough:

- **Copilot Studio agents** (custom agents, declarative agents, and Microsoft 365 agents created in Copilot Studio) and their per-agent grounding surfaces.
- **Microsoft 365 Copilot** runtime grounding behavior — to the extent it is governed by DLP-for-Copilot, DSPM for AI, and the Copilot location itself. Tenant-wide Copilot enablement is governed by separate controls.
- **Per-agent connector references** (Power Platform standard, premium, and custom connectors used as agent actions or knowledge connectors).
- **Per-agent file upload and image upload posture** as configured inside the agent.
- **Per-agent public web grounding** and **enterprise web URL** grounding.
- **Per-agent Copilot extensions, declarative agents, and API plugins.**
- **Agent identity governance** to the minimum extent needed to scope SharePoint groups (Entra Agent ID, managed identities, and the delegated-vs-application identity model — full RBAC is owned by Control 1.18).
- **Scope-drift detection** through DSPM for AI Activity Explorer, the Copilot/Power Platform audit schemas, Purview Alert policies, and Sentinel.

Out of scope for Control 1.14 (covered by sibling controls):

- The system-of-record agent registry → Control 1.2.
- General Power Platform DLP authoring across all makers, environment strategy, and connector-action authoring → Control 1.4.
- SIT and trainable-classifier authoring → Control 1.13.
- DSPM for AI policy authoring beyond what is needed to feed agent-scope minimization → Control 1.6.
- Endpoint DLP on user devices for file upload egress → Control 1.17.
- OAuth scope minimization, app registrations, and role-based access control on agent identities → Control 1.18.
- Tenant-wide SharePoint scope reduction (RCD, RSS, DAG) → Control 4.6.
- eDiscovery over `CopilotInteraction` records → Control 1.19.
- Communication compliance review of agent-mediated communications → Control 1.10.

### 0.2 Surface inventory (where each setting actually lives in April 2026)

| # | Setting | Portal path (April 2026 UI) | Sovereign clouds where path applies |
| --- | --- | --- | --- |
| S1 | Per-agent knowledge sources | `Copilot Studio → [agent] → Knowledge → + Add knowledge` | Commercial, GCC; verify GCC High limited preview, DoD verify |
| S2 | Per-agent SharePoint knowledge — folder scope | `Copilot Studio → [agent] → Knowledge → + Add knowledge → SharePoint → choose specific document library or folder` | Commercial, GCC; verify GCC High / DoD |
| S3 | Per-agent public web grounding toggle | `Copilot Studio → [agent] → Settings → Generative AI → Web search` | Commercial, GCC; verify GCC High / DoD |
| S4 | Per-agent file upload posture | `Copilot Studio → [agent] → Settings → Generative AI → File uploads` (and per-knowledge-source toggles) | Commercial, GCC; verify GCC High / DoD |
| S5 | Per-agent image upload posture | `Copilot Studio → [agent] → Settings → Generative AI → Image uploads` | Commercial, GCC; verify GCC High / DoD |
| S6 | Power Platform DLP — connector classification | `PPAC → Security → Data and privacy → Data policies → + New Policy` | Commercial, GCC, GCC High, DoD |
| S7 | Power Platform DLP — environment scope | Same wizard, **Scope** step | Commercial, GCC, GCC High, DoD |
| S8 | Purview DSPM for AI — recommended policies | `Purview portal → Solutions → DSPM for AI → Policies` (one-click recommended policies) | Commercial GA; GCC rolling; **GCC High / DoD lag — verify** |
| S9 | Purview DSPM for AI — Activity Explorer | `Purview portal → Solutions → DSPM for AI → Activity explorer` | Commercial GA; GCC rolling; GCC High / DoD verify |
| S10 | Purview DLP — Microsoft 365 Copilot location | `Purview portal → Solutions → Data loss prevention → Policies → + Create policy → Custom → Location: Microsoft 365 Copilot and Copilot Chat` | Commercial GA; GCC rolling; GCC High / DoD verify |
| S11 | Purview Audit — search and discover operations | `Purview portal → Solutions → Audit → Search` | Commercial, GCC, GCC High, DoD |
| S12 | Purview Alert policies | `Purview portal → Solutions → Policies → Alert policies` | Commercial, GCC; verify GCC High / DoD per release |
| S12-alt | Defender XDR alert policy | `https://security.microsoft.com → Email & collaboration → Policies & rules → Alert policy` | Commercial, GCC, GCC High, DoD |
| S13 | Microsoft Sentinel analytic rule (Zone 3 drift) | `Sentinel workspace → Analytics → + Create → Scheduled query rule`, sourced from the **Office 365** / **Microsoft 365** data connector | Commercial, GCC; verify Azure Government parity |
| S14 | Entra ID Governance — Access Reviews | `Microsoft Entra admin center → Identity governance → Access reviews → + New access review` | Commercial, GCC, GCC High, DoD |
| S15 | Cross-link to Control 4.6 — RCD / RSS / DAG | See Control 4.6 portal walkthrough | Commercial, GCC, GCC High, DoD |

### 0.3 Portal vs PowerShell — when to use which

| Operation | Portal path (this walkthrough) | PowerShell mirror | Recommended primary surface |
| --- | --- | --- | --- |
| Inventory all agents in an environment | Copilot Studio agent list + PPAC → Resources → Copilots | `Get-AdminPowerAppEnvironment` + `Get-AdminPowerApp` + `Get-CopilotEnvironment` (verify cmdlet names per `Get-Command -Module Microsoft.PowerApps.Administration.PowerShell`) | PowerShell for ≥10 environments; portal for spot checks |
| Read knowledge sources for a specific agent | Copilot Studio → agent → Knowledge | Microsoft Graph beta `agents` endpoint (verify availability per release) or M365 Copilot Studio admin APIs (preview) | Portal for first-pass review; Graph for inventory automation |
| Create / edit a Power Platform DLP policy | PPAC wizard | `New-DlpPolicy` / `Set-DlpPolicy` (Power Apps cmdlets) | Portal for first authoring + change-managed UI evidence; PowerShell for promotion across environments |
| Create / edit a Purview DLP policy at the M365 Copilot location | Purview portal wizard | `New-DlpCompliancePolicy` / `New-DlpComplianceRule` via Security & Compliance PowerShell (IPPS) | Portal for first authoring; PowerShell for export and reproducible audit |
| Search the unified audit log for Copilot or Power Platform operations | Purview → Audit → Search | `Search-UnifiedAuditLog -RecordType` (filter to Copilot Studio and Power Platform record types) | PowerShell for evidence export and SIEM hand-off |
| Schedule an access review | Entra → Identity governance → Access reviews | Microsoft Graph `accessReviews` API | Portal for first authoring; Graph API for at-scale automation |

!!! note "Why both surfaces are required"
    The portal gives you change-managed UI evidence (screenshots) that auditors expect for SOX 302/404 control walkthroughs and FINRA 3110 supervisory documentation. PowerShell and Graph give you the deterministic, reproducible read-backs that satisfy SEC 17a-4 / FINRA 4511 evidence preservation and let you scale beyond what UI can handle. Use both — never one alone.

---
## §1 Sovereign cloud applicability matrix

Use this matrix at the top of every change record so reviewers can see at a glance whether the steps in §3–§11 apply to your tenant.

| Capability | Commercial | GCC | GCC High | DoD | Gallatin (China 21Vianet) |
| --- | --- | --- | --- | --- | --- |
| Copilot Studio agent runtime | ✅ Available | ✅ Available | ⚠️ Limited preview as of early 2026 — verify | ⚠️ Verify per release | ❌ Not available |
| SharePoint / OneDrive knowledge connector (folder scope) | ✅ Available | ✅ Available | ⚠️ Verify connector parity | ⚠️ Verify connector parity | ❌ Not available |
| Public website knowledge connector / Web search toggle | ✅ Available | ✅ Available | ⚠️ Verify per release | ⚠️ Verify per release | ❌ Not available |
| File upload + image upload | ✅ Available | ✅ Available | ⚠️ Verify; payload limits differ (≈ 450 KB GCC High vs 5 MB Commercial) | ⚠️ Verify | ❌ Not available |
| Power Platform DLP (connector classification) | ✅ Available | ✅ Available | ✅ Available (verify connector list per environment) | ✅ Available (verify) | ❌ Not available |
| Purview DSPM for AI — recommended policies | ✅ GA | ⚠️ Rolling — verify | ❌ Often lagging — verify per release | ❌ Often lagging — verify per release | ❌ Not available |
| Purview DSPM for AI — Activity Explorer | ✅ GA | ⚠️ Rolling — verify | ❌ Often lagging — verify | ❌ Often lagging — verify | ❌ Not available |
| Purview DLP for Microsoft 365 Copilot location | ✅ GA | ⚠️ Rolling — verify | ❌ Often lagging — verify | ❌ Often lagging — verify | ❌ Not available |
| Purview Audit — `CopilotInteraction` record type | ✅ GA | ✅ GA | ⚠️ Verify per release | ⚠️ Verify per release | ❌ Not available |
| Purview Audit — Power Platform record types | ✅ GA | ✅ GA | ✅ GA | ✅ GA | ❌ Not available |
| Purview Alert policies | ✅ GA | ✅ GA | ⚠️ Verify per release | ⚠️ Verify per release | ❌ Not available |
| Microsoft Sentinel (M365 connector) | ✅ Azure Commercial | ✅ Azure Government | ✅ Azure Government | ✅ Azure Government Secret/Top Secret | ❌ Not applicable |
| Entra ID Governance Access Reviews | ✅ GA | ✅ GA | ✅ GA | ✅ GA | ⚠️ Verify per release |
| SharePoint Advanced Management (RCD / RSS / DAG — Control 4.6) | ✅ GA | ✅ GA | ⚠️ Limited — verify per release | ⚠️ Limited — verify per release | ❌ Not available |

### 1.1 Compensating controls when a capability is not available

If you operate in **GCC High**, **DoD**, or **Gallatin** and a capability above is unavailable or lagging, do not skip Control 1.14 — apply the following compensating controls and record the deviation in your control register:

- **Compensate for missing DSPM for AI:** Stand up daily `Search-UnifiedAuditLog -RecordType CopilotInteraction` exports into a SIEM (Sentinel or your firm's equivalent), and tighten Purview DLP-for-Copilot rules so detection happens at enforcement time even without DSPM dashboards.
- **Compensate for missing DLP-for-Copilot location:** Increase reliance on sensitivity-label-driven exclusion (Control 1.5) — published labels with the "exclude from Copilot processing" property still apply at the runtime; pair with tighter SharePoint scope (Control 4.6 RCD) so the surface never reaches the agent in the first place.
- **Compensate for missing public-web grounding parity:** If the Web search toggle is unavailable in your cloud, do not enable any agent that requires public web grounding for a Zone 3 workload — the absence of the toggle is itself the control.
- **Compensate for missing SharePoint Advanced Management (RCD / RSS):** Use sensitivity-label encryption + `Set-SPOSite -NoCrawl $true` on canary sites only (never as a production strategy — `NoCrawl` removes the site from the index entirely); document the deviation and re-evaluate per Microsoft 365 roadmap.
- **Compensate for missing Sentinel parity:** Increase the cadence of manual Audit search exports (Zone 3: weekly minimum), and route findings into your firm's SOC ticketing system manually.

### 1.2 Per-surface caveats you must record before acting

| Caveat | What it means in practice |
| --- | --- |
| **Public web grounding is OFF for Zone 3 NPI agents.** | The Web search toggle in Copilot Studio Generative AI settings must be off for any agent grounding on customer NPI. Capture a screenshot of the toggle state in the evidence pack at every quarterly review. |
| **GCC High / DoD payload limits.** | The Copilot Studio SharePoint / OneDrive knowledge connector enforces a smaller payload limit in GCC High (≈ 450 KB) than in commercial (≈ 5 MB). Test agents must use representative content sizes; large PDFs that ground successfully in commercial may silently truncate or fail in regulated clouds. |
| **DSPM for AI lag.** | Activity Explorer signals can lag actual agent activity by minutes to hours depending on tenant size and signal type. Do not treat the absence of a signal as the absence of the activity — pair DSPM with the audit log. |
| **No native `AgentScopeExpansion` audit event.** | There is no out-of-the-box "agent scope expanded" audit operation. Scope drift is derived through SIEM correlation against `CopilotInteraction` records joined to the Control 1.2 inventory, plus Power Platform admin events for connector and knowledge-source changes. |
| **Power Platform DLP does not configure OAuth scopes.** | DLP classifies connectors as Business / Non-Business / Blocked; it does not narrow OAuth delegated or application permissions. OAuth scope minimization on custom connectors and on agent identities is owned by Control 1.18. |
| **Identity model — delegated vs application.** | Copilot Studio agents that ground on SharePoint via an authenticated user typically execute knowledge calls **as the invoking user** (delegated). A SharePoint group keyed to a "shared service account" does **not** constrain a user-bound agent. Only when the agent is configured with an **authenticated connection**, **managed identity**, or **Entra Agent ID** does a service-principal-keyed group apply. Confirm the agent's auth mode before designing groups (see §10). |
| **OneDrive cannot have RCD applied.** | Any "remove this from Copilot grounding" requirement targeted at OneDrive must be implemented through DLP, sensitivity labels, or the agent-side knowledge-source removal — never RCD. See Control 4.6. |

---

## §2 Pre-flight gates

Do not proceed past §2 until every gate below is signed off. Each gate maps to a concrete artifact you will produce; the artifact name appears in the Evidence Pack table in §15.

### 2.1 License and capability gate

| Gate | Required state | How to verify | Evidence artifact |
| --- | --- | --- | --- |
| Microsoft 365 Copilot license present | At least one assigned seat in the tenant; required for `CopilotInteraction` audit emission and DLP-for-Copilot location coverage. | `Microsoft 365 admin center → Billing → Licenses` | E1 — License posture screenshot |
| Microsoft 365 E5 Compliance (or E5 Information Protection & Governance) | Required for Purview DSPM for AI, DLP for M365 Copilot location, and Activity Explorer. | Same Licenses page; record SKU. | E1 (combined) |
| SharePoint Advanced Management (SAM) | Included with Microsoft 365 Copilot license; provides RCD, RSS, and DAG (consumed by Control 4.6 from this walkthrough). | Microsoft 365 admin center → Billing → Licenses | E1 (combined) |
| Microsoft Entra ID Governance (Entra ID P2 or Microsoft Entra Suite) | Required for Access Reviews on agent identities, connector connections, and knowledge-source SharePoint groups. | Entra admin center → Billing → Licenses | E1 (combined) |
| Copilot Studio per-message capacity (or per-user license) | Required for Copilot Studio agent runtime in production. | PPAC → Billing → Capacity | E1 (combined) |

!!! warning "Common license misconception"
    DSPM for AI and DLP-for-Copilot are **not** covered by the base Microsoft 365 Copilot license alone — they require an E5 Compliance / Information Protection & Governance add-on. If your tenant has Copilot but not E5 Compliance, several detective steps in §6, §7, and §8 will not be available; substitute the compensating controls listed in §1.1.

### 2.2 Role and PIM gate

You will need the following Entra / workload roles assigned to the named operator(s) for the duration of this walkthrough. Use canonical names from the [Role Catalog](../../../reference/role-catalog.md). Do **not** perform any §3–§11 step as Entra Global Admin; Global Admin must remain a break-glass role.

| Role | Required for | Assigned to (named operator) | Time-bound? |
| --- | --- | --- | --- |
| **AI Administrator** | Steps §3 (inventory reconcile), §6 (DSPM for AI), §7 (DLP-for-Copilot read), §8 (audit), agent-level configuration | _name + UPN_ | Yes — PIM eligible, activate for the change window |
| **Power Platform Admin** | Step §4 (Power Platform DLP) | _name + UPN_ | Yes — PIM eligible |
| **SharePoint Admin** | Step §5 (knowledge-source minimization, coordinate with Control 4.6); §10 SharePoint group hygiene | _name + UPN_ | Yes — PIM eligible |
| **Purview Compliance Admin** | Step §7 (DLP for M365 Copilot location), §8 (Audit search), §9 (Alert policies) | _name + UPN_ | Yes — PIM eligible |
| **Purview Data Security AI Admin** | Step §6 (DSPM for AI policies + Activity Explorer) | _name + UPN_ | Yes — PIM eligible |
| **Entra Identity Governance Admin** | Step §10 (Access Reviews) | _name + UPN_ | Yes — PIM eligible |
| **AI Governance Lead** | Approval of Zone 2 / Zone 3 scope changes; sign-off on quarterly access reviews (§11) | _name_ | Standing |
| **Compliance Officer** | Counter-sign change records; Zone 3 approvals | _name_ | Standing |
| **CISO** | Approve Zone 3 scope changes; own residual-risk acceptance | _name_ | Standing |
| **Entra Global Admin** | Break-glass only (do not use for routine steps) | _break-glass account_ | Standing, monitored |

Record PIM activations in the change record and include the activation timestamps in evidence artifact E2.

### 2.3 Tenant readiness gate

| Gate | Required state | How to verify |
| --- | --- | --- |
| Unified Audit Log (UAL) ingestion confirmed | UAL has been on for ≥ 90 days (or since tenant creation if newer); `CopilotInteraction` and Power Platform record types are emitting. | `Purview → Audit → Search` returns results for `RecordType=CopilotInteraction` over the last 7 days. |
| Sensitivity labels published | Required for DLP-for-Copilot rule conditions; cross-reference to Control 1.5. | `Purview → Information protection → Labels` shows ≥ 1 published label. |
| At least one SIT or trainable classifier published | Required for DLP-for-Copilot SIT-condition rules; cross-reference to Control 1.13. | `Purview → Information protection → Classifiers → Sensitive info types` shows ≥ 1 published custom or built-in SIT in active use. |
| Control 1.2 agent registry exists and is current within the last 30 days | Source-of-truth inventory for §3 reconciliation. | Open the registry (SharePoint List or Dataverse table) and confirm last-modified date. |
| Control 4.6 RCD/RSS posture documented | Required for §5 reconciliation. | Open the Control 4.6 evidence pack; confirm latest DAG snapshot and RCD list. |

### 2.4 Test fixtures gate (canary environment, agents, identities)

Before any production change, the following test fixtures must exist in a canary Power Platform environment. These names appear throughout §3–§9.

**Canary environment:**

| Item | Value |
| --- | --- |
| Environment name | `cs-scope-canary` (or your firm's equivalent) |
| Environment type | Production, with isolated Dataverse |
| DLP policy applied | `dlp-1.14-canary` (built in §4) |
| Test agents allowed to publish | Only the test agents below |

**Test agents (Copilot Studio):**

| Agent | Bound knowledge source(s) | Purpose |
| --- | --- | --- |
| `scope-test-Z2-001` | One scoped SharePoint document library | Zone 2 representative — must reflect knowledge-source folder scope and PPAC DLP. |
| `scope-test-Z3-001` | One scoped library + one Dataverse table; web search **off**; file upload **restricted by label** | Zone 3 representative — full minimization stack. |
| `scope-test-drift-001` | Identical to `scope-test-Z2-001` at baseline; used to deliberately add an out-of-scope knowledge source for §8 / §9 drift testing | Drift detection canary. |

**Test identities:**

| Identity | Purpose |
| --- | --- |
| `svc-scope-pos@<tenant>` | "Positive" identity — has direct permission on the in-scope library; expected to receive grounded answers. |
| `svc-scope-neg@<tenant>` | "Negative" identity — does not have permission on the in-scope library; expected to receive no grounded answer. |
| `svc-scope-drift-actor@<tenant>` | Account used to perform the deliberate scope-expansion change in §8.4 drift testing. |

### 2.5 Two-portal precondition

Sessions in **Copilot Studio**, **PPAC**, **Purview portal**, and **Entra admin center** must all be open and authenticated **as the named operator role** (not as Global Admin) before you start §3. The §3 inventory reconciliation depends on data from all four surfaces; do not begin if any portal is unreachable for the named operator.

### 2.6 Separation of duties

The operator who **applies** a scope change (e.g., narrows a knowledge source, adds a connector, edits DLP) must not be the same operator who **approves** the change record, and must not be the same operator who **collects** the post-change evidence. At minimum:

- Approver: Compliance Officer or AI Governance Lead (Zone 3 also requires CISO).
- Operator (applies change): Named AI Administrator / Power Platform Admin / SharePoint Admin / Purview Data Security AI Admin (per the §2 roles matrix).
- Evidence collector: Purview Compliance Admin (read-only Audit + Activity Explorer).

Document the three named individuals and their email approvals in the change record before proceeding.

---
## §3 Step 1 — Build the agent grounding-surface inventory

**Purpose:** Reconcile every Copilot Studio agent in the tenant against the Control 1.2 agent registry, capturing for each agent the full set of grounding surfaces it can reach: SharePoint sites and libraries, OneDrive accounts, Dataverse tables, Microsoft Graph connectors, per-conversation file uploads, image uploads, public web grounding, enterprise web URLs, connector references (standard, premium, custom), and Copilot extensions / declarative agents / API plugins. Without this inventory you cannot evaluate minimization — you can only assert it.

**Operator:** AI Administrator (with read access to PPAC, Copilot Studio admin, Purview DSPM for AI)
**Estimated time:** 60–120 minutes for ≤ 50 agents; longer for larger fleets — automate via the [`powershell-setup.md`](powershell-setup.md) once volume warrants it
**Outcome:** Per-agent inventory rows in the Control 1.2 registry, each with all eleven grounding-surface fields populated, owner and zone tagged, and last-reconciled timestamp.

### 3.1 Pull the three authoritative agent lists

There is no single tenant view that lists every agent. You must reconcile three lists. Discrepancies between them are themselves a finding — record them.

**List A — Copilot Studio admin agent inventory (the authoring surface):**

1. Sign in to **Copilot Studio** (`https://copilotstudio.microsoft.com`) as AI Administrator.
2. In the top-right environment switcher, iterate through every Power Platform environment your tenant uses for agent hosting.
3. In each environment, capture the agent list (name, owner, last modified, published status). Export to CSV (use the agent list page's **Export** action, or the PowerShell mirror in [`powershell-setup.md`](powershell-setup.md)).
4. Save as artifact E3-A.

**List B — PPAC Copilots / Agents resource view:**

1. Sign in to **Power Platform Admin Center** (`https://admin.powerplatform.microsoft.com`).
2. Navigate to **Resources → Copilots** (the menu label varies — recent releases also use **Resources → Agents**; verify in your tenant).
3. Filter by environment; export the list per environment.
4. Save as artifact E3-B.

**List C — Purview DSPM for AI agent inventory:**

1. Sign in to the **Microsoft Purview portal** (`https://purview.microsoft.com`) as Purview Data Security AI Admin.
2. Navigate to **Solutions → DSPM for AI → Reports → AI apps and agents** (the exact heading evolves; verify against [Microsoft Learn — DSPM for AI overview](https://learn.microsoft.com/en-us/purview/dspm-for-ai)).
3. Export the AI apps list. Note: DSPM for AI only sees agents that have **generated activity** during the report window; an agent that is published but unused will not appear here.
4. Save as artifact E3-C.

### 3.2 Reconcile the three lists against Control 1.2

Open the Control 1.2 agent registry and join on agent name + environment + owner UPN. Flag the following diffs as findings to remediate before proceeding:

| Diff | Action |
| --- | --- |
| Agent in List A but not in 1.2 registry | Open a registry intake ticket; do not allow the agent to be promoted to Zone 2/3 until intake completes. |
| Agent in 1.2 registry but not in List A | Confirm agent has been retired; if not, the registry is stale — refresh and reassign owner. |
| Agent in List A but not in DSPM (List C) | Verify the agent has actually been used in the DSPM lookback window; if it has been used and DSPM did not see it, escalate to [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) tenant onboarding. |
| Agent in List B but not in List A | Likely an environment-mismatch artifact; reconcile by opening the agent in Copilot Studio. |
| Owner UPN mismatch across lists | Update the registry to match the Copilot Studio author of record; notify the previous owner. |

Persist the reconciled view as artifact E3 — Reconciled Agent Inventory.

### 3.3 For each agent, capture the eleven grounding-surface fields

For every agent in the reconciled inventory, open the agent in Copilot Studio (`Copilot Studio → [agent]`) and capture the following fields. Persist to the Control 1.2 registry; do not maintain a parallel store.

| Field | Source surface | How to capture |
| --- | --- | --- |
| **F1 — SharePoint sites and libraries** | `Knowledge` tab → expand each SharePoint knowledge source | Record full path including site collection, site, library, and (if scoped) folder |
| **F2 — OneDrive accounts** | `Knowledge` tab → SharePoint / OneDrive knowledge source entries pointing at `-my.sharepoint.com` URLs | Record OneDrive owner UPN and folder path |
| **F3 — Dataverse tables** | `Knowledge` tab → Dataverse knowledge sources | Record environment, table logical name, columns referenced |
| **F4 — Microsoft Graph connectors** | `Knowledge` tab → Graph connector knowledge sources (e.g., file shares, ServiceNow, Salesforce indexes) | Record connector name, connection ID, source system |
| **F5 — Per-conversation file uploads** | `Settings → Generative AI → File uploads` toggle and per-knowledge-source file upload toggle | Record the toggle state per zone (allowed, sensitivity-label-gated, blocked) |
| **F6 — Image uploads (vision grounding)** | `Settings → Generative AI → Image uploads` toggle | Record the toggle state per zone |
| **F7 — Public web grounding** | `Settings → Generative AI → Web search` toggle | Record state — **must be OFF for any Zone 3 NPI agent** (see §6) |
| **F8 — Enterprise web URLs** | `Knowledge` tab → Public website / enterprise URL entries; also see [Microsoft Learn — Public website knowledge sources](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-public-websites) | Record exact URL allowlist; ≤ 4 URLs per agent recommended |
| **F9 — Connector references (actions)** | `Tools` or `Actions` tab; review each Power Platform connector reference, both standard and custom | Record connector name and any premium / custom designation; cross-link to PPAC environment DLP scope |
| **F10 — Copilot extensions / declarative agents / API plugins** | `Tools` tab → API plugins / declarative agents / custom connectors used as tools | Record manifest source (Copilot Studio export, Microsoft 365 Agents Toolkit, custom GPT) and target API endpoint |
| **F11 — Agent identity model** | `Settings → Security → Authentication`; identify whether the agent uses delegated user identity, an authenticated connection, a managed identity, or an Entra Agent ID | Record the identity model — this drives §10 SharePoint group hygiene and §10 Access Reviews |

### 3.4 Document the business justification for each agent ↔ surface pair

For every (agent, surface) pair captured in §3.3, record the business justification on the registry row. The minimum justification fields are:

- **Justification text** (one to three sentences; what business outcome the surface enables for this agent).
- **Approver** (per zone: Zone 1 self-service; Zone 2 manager; Zone 3 CISO + AI Governance Lead).
- **Approval ticket ID** (ServiceNow / Jira / approvals app reference).
- **Data classification** at the surface (Public / Internal / Confidential / Highly Confidential / Regulated / NPI).
- **Re-review date** (per zone cadence — Zone 1 annual, Zone 2 quarterly, Zone 3 monthly).

Any (agent, surface) pair without all five fields populated is a finding; the agent must not be allowed to publish until the gap is closed.

### 3.5 Establish the change-trigger discipline

Make every future change to an agent's grounding surface — adding a knowledge source, enabling file upload, switching on web search, adding a connector reference — a registry-tracked event:

1. Maker submits a scope-change request against the Control 1.2 registry (Power Automate flow against the SharePoint List, or equivalent in your firm's request system).
2. Approver of the agent's zone counter-signs the request (Zone 1 self-service; Zone 2 manager; Zone 3 CISO + AI Governance Lead).
3. Approver UPN and approval ticket ID are written to a new registry row for the (agent, surface) pair.
4. Maker performs the change in Copilot Studio.
5. Evidence collector captures the post-change inventory snapshot (artifact E3-update) and reconciles against §3.3.

This discipline is what makes the §8 / §9 scope-drift detection meaningful — without an approved baseline, drift detection has nothing to compare against.

### 3.6 Common pitfalls in §3

- **Treating DSPM for AI as authoritative.** DSPM only sees agents that have generated activity during the report window. A new but unused agent will be invisible to DSPM and visible only in Lists A and B. Do not rely on DSPM for the master list.
- **Confusing the agent author with the agent owner.** The agent author (the user who clicked **Create**) is recorded in Copilot Studio; the agent owner (the named accountable individual under your governance model) is recorded in the Control 1.2 registry. They are often different. Reconcile both.
- **Missing connector references on agents that look "knowledge only".** Many declarative agents and Copilot Studio agents now expose **actions** as well as knowledge — capture F9 even for agents you assume are read-only.
- **Forgetting OneDrive grounding.** OneDrive grounding is governed by the same SharePoint / OneDrive knowledge connector but does not show up under SPAC RCD posture. Enumerate F2 explicitly.

---

## §4 Step 2 — Power Platform DLP for connector classification

**Purpose:** Classify the connectors used by Copilot Studio agents into Business / Non-Business / Blocked groups using a Power Platform DLP policy scoped to the environments hosting Zone 2 / Zone 3 agents. This is **inventory-time** enforcement — a connector classified as Blocked cannot be added to an agent in the scoped environment.

**Operator:** Power Platform Admin
**Estimated time:** 30–60 minutes for the first policy; 10–20 minutes for subsequent edits
**Outcome:** A DLP policy named (suggested) `dlp-1.14-zone-2` and a Zone 3 sibling `dlp-1.14-zone-3` apply to the corresponding environments; every connector used by any agent in the inventory is classified; no agent is using a connector that is not in the Business group of its environment's policy.

!!! note "Boundary with Control 1.4"
    General Power Platform DLP authoring (across all makers, all apps, and all flows) is owned by [Control 1.4 — Advanced Connector Policies](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). Step §4 here configures only the **agent-relevant** dimension: the connectors used by Copilot Studio agents (knowledge connectors and action connectors) within the environments designated for Zone 2 / Zone 3 agent hosting. If your firm has a tenant-wide DLP policy already authored under Control 1.4, layer the agent-specific policy on top of it (DLP policies stack — most-restrictive wins per environment).

!!! warning "Power Platform DLP does not configure OAuth scopes"
    Power Platform DLP classifies connectors as Business / Non-Business / Blocked. It does **not** narrow the OAuth delegated or application permissions a connector requests at runtime. OAuth scope minimization on custom connectors and on agent identities is owned by [Control 1.18 — RBAC](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md). This step gates **whether** an agent can use a connector; Control 1.18 gates **what scopes** that connector requests.

### 4.1 Open PPAC and create the policy

1. Sign in to **Power Platform Admin Center** (`https://admin.powerplatform.microsoft.com`) as the named Power Platform Admin (PIM-activated).
2. In the left navigation, expand **Security → Data and privacy → Data policies** (the menu was reorganized in the H2 2025 PPAC refresh; older builds may still show **Policies → Data policies**).
3. Click **+ New Policy**.
4. **Name:** `dlp-1.14-zone-2` (or your equivalent naming convention).
5. Click **Next**.

### 4.2 Classify the prebuilt connector list per zone

The wizard presents the full connector catalog (standard, premium, and custom) split into the three default groups: **Business**, **Non-Business**, and **Blocked**. Connectors default to Non-Business until you classify them.

For Control 1.14 you must classify, at minimum:

**The Copilot Studio knowledge connectors:**

| Connector (April 2026 display name — verify in your tenant) | Zone 1 | Zone 2 | Zone 3 |
| --- | --- | --- | --- |
| Knowledge source with SharePoint and OneDrive in Copilot Studio | Business | Business | Business (allowlisted sites only — coordinate with Control 4.6 RCD posture in §5) |
| Knowledge source with public websites in Copilot Studio | Non-Business | Non-Business | **Blocked** |
| Knowledge source with documents in Copilot Studio (uploaded files) | Business | Non-Business | **Blocked** unless §7 file-upload posture allows label-gated upload |
| Knowledge source with Dataverse in Copilot Studio | Business | Business | Business (RBAC-scoped tables only — coordinate with Control 1.18) |

**The standard connectors used as agent actions** (the exact set varies by environment — pull from §3.3 field F9):

| Class of connector | Zone 1 | Zone 2 | Zone 3 |
| --- | --- | --- | --- |
| Microsoft 365 first-party (SharePoint, OneDrive for Business, Outlook, Teams, Planner, Excel) | Business | Business | Business (sub-set per agent justification) |
| First-party Azure data services (Dataverse, Azure SQL, Azure Cosmos DB, Azure Blob) | Business | Business | Business (per-table scope) |
| Premium business-line connectors used by your firm (e.g., Bloomberg, FactSet, ServiceNow, Salesforce — verify license eligibility) | Non-Business | Business (per justification) | Business (allowlist; CISO approval) |
| Consumer / personal connectors (X / Twitter, Facebook, Instagram, RSS, public Outlook.com) | Non-Business | **Blocked** | **Blocked** |
| File-sharing connectors not approved by your firm (Dropbox personal, Google Drive consumer, Box personal) | Non-Business | **Blocked** | **Blocked** |
| Custom connectors (your firm's internal APIs) | Per Control 1.4 review | Per Control 1.4 review | Per Control 1.4 review + Zone 3 CISO sign-off |

For each connector, click the connector row and choose **Move to Business**, **Move to Non-Business**, or **Block**. Capture the connector classification screenshot for evidence artifact E4.

!!! warning "Connector display names evolve"
    Microsoft has renamed and split the Copilot Studio knowledge connectors several times across 2025 and early 2026 releases. Verify the exact display names in your tenant before authoring the policy. If you do not see the expected connector, search for `Copilot` and `SharePoint` separately, and document the actual name(s) in the change record. The [Microsoft Learn — Connector classification](https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification) page is the system of record for connector taxonomy.

### 4.3 Default group for new connectors

Set the **Default group** for connectors not explicitly classified to **Blocked** for Zone 3 environments. New connectors that appear in the Microsoft connector catalog will be blocked by default until reviewed; this is the correct posture for regulated agent hosting. For Zone 2, Default group = Non-Business is acceptable. For Zone 1, leave Default group = Non-Business (the canary / personal sandbox tolerates discoverability).

### 4.4 Scope the policy to environments

1. Click **Next** to move to the **Scope** step.
2. Select **Add multiple environments** and pick the environment(s) hosting Zone 2 agents (for `dlp-1.14-zone-2`) or Zone 3 agents (for `dlp-1.14-zone-3`).
3. Do **not** apply Zone 2 and Zone 3 policies to the same environment. Do **not** apply either policy to the **default** Power Platform environment unless your firm has explicitly ratified the default environment as a managed agent host (most firms have not — the default environment is open to all makers tenant-wide and is not appropriate for Zone 2 / Zone 3 hosting).
4. Click **Next**.

### 4.5 Review and create

1. Review the policy summary: name, environments, connector classifications, default group.
2. Click **Create policy**.
3. Capture the final policy summary screenshot for evidence artifact E5.

### 4.6 Sibling Zone 3 policy

Repeat §4.1–§4.5 with these differences for `dlp-1.14-zone-3`:

- Tighter Business group — only the connectors with explicit Zone 3 justification in the Control 1.2 registry.
- Default group = **Blocked**.
- Environment scope = Zone 3 environments only.
- Approval = CISO + AI Governance Lead (counter-sign required on the change record).

### 4.7 Validate against the test agents

1. Open `scope-test-Z2-001` in the Zone 2 canary environment.
2. Attempt to add a connector that is **Blocked** in `dlp-1.14-zone-2` (e.g., a consumer file-sharing connector from §4.2). Expected: Copilot Studio surfaces a "blocked by data policy" message and the connector cannot be added. Capture the screenshot as artifact E6 (DLP block — negative path).
3. Attempt to add a connector that is **Business** (e.g., SharePoint). Expected: the connector adds successfully. Capture the screenshot as artifact E6 (DLP allow — positive path).
4. Repeat for `scope-test-Z3-001` in the Zone 3 canary; the public-website knowledge connector should be blocked.

### 4.8 Common pitfalls in §4

- **Authoring DLP in the default environment.** The default environment hosts ad-hoc maker activity tenant-wide. Restricting connectors there breaks unrelated apps and flows. Always scope DLP to a named, governed environment.
- **Forgetting that agents grandfather in.** Existing agents that already use a now-Blocked connector continue to run until republished. Audit existing agents for blocked-connector usage and republish them deliberately.
- **Treating Power Platform DLP as a substitute for OAuth scope minimization.** It is not — see Control 1.18.
- **Not reconciling against §3 inventory.** Every connector in the §3 F9 field must appear in the Business group of the agent's environment policy. Run the reconciliation after every DLP edit.

---
## §5 Step 3 — SharePoint knowledge-source minimization

**Purpose:** Constrain each agent's SharePoint knowledge surface to the smallest set of sites, libraries, and (where supported) folders that meet the agent's documented business purpose. Ensure that the SharePoint posture (Restricted Content Discovery, Restricted SharePoint Search, Data Access Governance, sensitivity labels) underneath those sources is consistent with the zone of the agent.

**Operator:** AI Administrator (agent author) co-authoring with SharePoint Admin
**Estimated time:** 20–40 minutes per agent (first time); 10 minutes for incremental edits
**Outcome:** Each agent's `Knowledge` tab references only justified, registry-approved SharePoint scopes; the corresponding sites have RCD / RSS / DAG posture per [Control 4.6 — Knowledge Source Restrictions and SharePoint Hygiene](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md); SG-AgentAccess groups (where the agent uses an authenticated connection or managed identity rather than delegated user identity) are scoped to the principal of record.

!!! warning "Identity model determines what minimization actually does"
    Most Copilot Studio agents grounded in SharePoint execute as the **invoking user** (delegated identity). For these agents, narrowing the agent's knowledge source to a specific library does **not** prevent the user from asking the agent about content the user can already see in the broader site — the agent's effective reach is the intersection of its declared knowledge sources and the user's own SharePoint permissions. SG-AgentAccess groups apply only when the agent uses an **authenticated connection** or **managed identity** or **Entra Agent ID** that grounds as a service principal. Capture the identity model per agent (§3.3 field F11) and choose the §5 approach accordingly.

### 5.1 Boundary with Control 4.6

Control 4.6 owns:

- Restricted Content Discovery (RCD) configuration on Tier-1 sites.
- Restricted SharePoint Search (RSS) tenant-wide.
- Data Access Governance (DAG) reports and oversharing remediation.
- Sensitivity-label inheritance to SharePoint sites.

Control 1.14 §5 owns:

- The per-agent decision of **which** SharePoint scopes the agent's `Knowledge` tab references.
- The reconciliation that those scopes have the §4.6 posture appropriate to the agent's zone.
- The negative-path verification that the agent does not return content from out-of-scope sites for the test fixtures.

If a Zone 3 agent needs grounding from a site that does not yet have RCD enabled, **stop**. Open a Control 4.6 RCD enablement ticket for that site before adding it to the agent. Do not work around the gap by adding the site to the agent's `Knowledge` tab and trusting the agent's scope to substitute for site-level posture.

### 5.2 Open the agent and review the current knowledge sources

1. Sign in to **Copilot Studio** (`https://copilotstudio.microsoft.com`) as the agent author or AI Administrator.
2. Open the agent under review.
3. Navigate to the **Knowledge** tab.
4. For each existing knowledge source, capture:
   - Source type (SharePoint site, SharePoint library, OneDrive, public website, Dataverse, Graph connector, file).
   - Full path / URL.
   - Date added and the registry approval ticket reference.
5. Compare against the §3.3 inventory rows for this agent. Any source present in Copilot Studio but not in the registry is a finding — open a registry intake or remove the source.

### 5.3 Add the smallest-scope SharePoint source

When adding a new SharePoint source:

1. On the **Knowledge** tab, click **+ Add knowledge**.
2. Select **SharePoint**.
3. In the picker, **do not** paste the root site URL when a library or folder URL will do. The picker accepts:
   - Site collection URL (broadest — avoid for Zone 2 / Zone 3 unless the entire site has been classified for that zone).
   - Document library URL (preferred default for Zone 2).
   - Folder URL within a library (preferred default for Zone 3).
4. Paste the most specific URL the picker accepts. Verify the breadcrumb in the picker resolves to the expected scope before clicking **Add**.
5. After adding, click into the source row and confirm the resolved path matches what you intended.

### 5.4 Reconcile against the underlying SharePoint site posture

For each SharePoint source on the agent, verify that the corresponding site has the §4.6 posture for the agent's zone:

| Zone | Required SharePoint site posture | Verify in |
| --- | --- | --- |
| Zone 1 (Personal) | Sensitivity label applied; standard sharing posture | SPAC → Active sites → [site] → Settings |
| Zone 2 (Team) | Sensitivity label applied; sharing restricted to specified domains; RCD enabled if site contains Confidential or higher | SPAC → Policies → Sharing; SPAC → Reports → Restricted Content Discovery |
| Zone 3 (Enterprise / Regulated) | Sensitivity label applied (Confidential / Highly Confidential / Regulated / NPI); sharing restricted to internal only; **RCD enabled and effective**; DAG report ≤ 30 days old; oversharing remediation closed | SPAC → Policies → Sharing; SPAC → Reports → Restricted Content Discovery; SPAC → Reports → Data Access Governance |

If any cell in the row for an agent's zone is unmet, the agent must not be permitted to ground on that site at that zone classification. Open the corresponding Control 4.6 work item and hold the agent at the prior zone until remediation completes.

### 5.5 Group hygiene for service-principal-grounded agents

If §3.3 field F11 indicates the agent grounds via an authenticated connection, managed identity, or Entra Agent ID (rather than delegated user identity):

1. Identify the service principal of record for the agent (Copilot Studio → agent → **Settings → Security → Authentication**, or the connection reference in the action).
2. Confirm there is a dedicated security group of the form `SG-AgentAccess-<agent-id>` in Entra ID.
3. The group membership is the service principal only — no human users.
4. The group is granted SharePoint access at exactly the scope on the agent's `Knowledge` tab — not broader.
5. The group is reviewed quarterly under §13 (Zone 3 monthly).

If the agent grounds via delegated user identity, SG-AgentAccess groups are not the right control — instead, the user's own SharePoint permissions and the §4.6 site posture are what minimize the surface. Document the identity model on the registry row so reviewers do not chase the wrong control.

### 5.6 Positive- and negative-path validation

Using the test fixtures from §2.4:

1. **Positive path.** Sign in as `svc-scope-pos` (a user with permission to the in-scope site only). Ask `scope-test-Z2-001` a question whose answer is in the in-scope library. Expected: agent answers and cites the in-scope source. Capture transcript as artifact E7-pos.
2. **Negative path — out-of-scope site, in-permission user.** Sign in as a user who has permission to both the in-scope site and an adjacent out-of-scope site. Ask the agent a question whose answer is only in the out-of-scope site. Expected: agent does not return content from the out-of-scope site (it may say it has no information). Capture transcript as artifact E7-neg-1.
3. **Negative path — in-scope site, out-of-permission user.** Sign in as `svc-scope-neg` (a user with no permission to the in-scope site). Ask the agent a question whose answer is in the in-scope library. Expected: agent does not return content because the user lacks underlying SharePoint permission (delegated identity model). Capture transcript as artifact E7-neg-2.
4. **Negative path — image / file upload not present in source.** Upload a synthetic test PDF that contains the string `SCOPE-DRIFT-PROBE-{date}` and ask the agent to summarize it. If file upload is allowed by §7, expected: agent summarizes the uploaded file and cites it as the upload (not as a knowledge source). If file upload is blocked, expected: upload is rejected. Capture transcript as artifact E7-neg-3.

### 5.7 Common pitfalls in §5

- **Adding the root site collection when a library would do.** This is the single most common scope-creep finding. Force the maker to pick the library or folder URL.
- **Skipping the §4.6 RCD verification on Zone 3.** RCD is the underlying mechanism that prevents Copilot from indexing content beyond the agent's declared scope when the user has broad organization-level access. Without RCD, scoping the agent alone is insufficient.
- **Confusing OneDrive grounding with SharePoint grounding.** Both are added through the SharePoint knowledge source picker, but OneDrive grounding implicates the OneDrive owner's personal store. Capture OneDrive separately on the registry (§3.3 field F2) and require explicit owner consent for Zone 2 / Zone 3.
- **Building SG-AgentAccess groups for delegated-identity agents.** This is wasted effort and creates the false impression of control. Confirm the identity model first.

---

## §6 Step 4 — Disable public web grounding for Zone 3 NPI agents

**Purpose:** Ensure that no agent classified Zone 3 — and specifically no agent whose data classification (§3.4) is Regulated or NPI — can issue queries to the public web, exfiltrate prompt context to a public search index, or return public-web content as authoritative grounding to the user.

**Operator:** AI Administrator (agent author) under counter-sign by AI Governance Lead
**Estimated time:** 5 minutes per agent
**Outcome:** Every Zone 3 NPI agent has the **Web search** toggle OFF; the §4 DLP policy `dlp-1.14-zone-3` blocks the public-website knowledge connector at the environment level as a defence-in-depth backstop; the change is logged in the audit trail and on the registry.

### 6.1 Locate the toggle

1. Sign in to **Copilot Studio** as the agent author.
2. Open the Zone 3 agent under review.
3. Navigate to **Settings → Generative AI** (the section heading evolves — recent builds also use **Settings → AI orchestration → Generative AI**; verify in your tenant).
4. Locate the **Web search** toggle (also labelled **Search the web** or **Public web grounding** in some builds; the underlying capability is the Bing-backed public web grounding source described in [Microsoft Learn — Web search in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-boost-conversations)).

### 6.2 Disable web search

1. Set the toggle to **Off**.
2. In the same panel, also set:
   - **General knowledge** (the "answer from the model's training data" toggle, where surfaced) to **Off** for Regulated / NPI agents — model-training-data answers cannot be cited or audited at the same fidelity as enterprise grounding.
   - **Image uploads** to **Off** for Regulated / NPI agents unless §7 documents an explicit business justification.
3. Click **Save** and **Publish** the agent.
4. Capture a screenshot of the **Settings → Generative AI** panel showing all the relevant toggles in their post-change state. Save as artifact E8.

### 6.3 Verify the §4 DLP backstop

1. In PPAC, open the `dlp-1.14-zone-3` policy.
2. Confirm the **Knowledge source with public websites in Copilot Studio** connector is in the **Blocked** group.
3. Confirm the policy is scoped to the environment hosting the Zone 3 agent.
4. This is the defence-in-depth: even if a future maker re-enables the agent's **Web search** toggle, the DLP policy prevents the public-website connector from being added at the environment level. Capture the PPAC view as artifact E9.

### 6.4 Validation

1. As `svc-scope-pos`, ask the Zone 3 agent a question that can only be answered by current public information (e.g., "What is today's headline at <public-news-site>?"). Expected: the agent declines or answers from enterprise sources only — it does not return public-web content.
2. As the maker, attempt to re-enable **Web search** in the agent. The toggle may be re-enabled in the UI, but at publish time the §4 DLP policy will fail the publish if the public-website knowledge connector is referenced. Capture the failure screenshot as artifact E10.
3. Inspect the audit trail (§10) for the toggle change event under `CopilotInteractionAdminAction` (or the closest current operation name — verify per release).

### 6.5 Common pitfalls in §6

- **Toggling Web search off without the §4 DLP backstop.** A future maker can re-enable the toggle in seconds. Always pair the toggle setting with the environment-level DLP block.
- **Leaving General knowledge / model knowledge enabled on NPI agents.** Model knowledge is not auditable to the same standard as enterprise grounding and may produce uncitable answers. Disable for NPI workloads.
- **Forgetting to republish.** Many Copilot Studio settings only take effect after the agent is republished. Always republish and capture the publish event.

---

## §7 Step 5 — File and image upload posture per zone

**Purpose:** Define and enforce, per zone, whether end users can upload files or images to an agent during a conversation, and whether sensitivity-label gating applies. Per-conversation uploads are a frequently overlooked grounding surface — they bypass §3 inventory because they are user-supplied at runtime.

**Operator:** AI Administrator co-authoring with Purview Compliance Admin (label policy) and SharePoint Admin (Office attachment posture)
**Estimated time:** 30 minutes for the first agent; 10 minutes per subsequent agent
**Outcome:** Each agent has documented, registry-tracked file-upload and image-upload posture aligned to its zone; sensitivity-label gating is enforced where the zone demands it; uploaded content does not leak into the agent's persistent knowledge surface or into other users' conversations.

### 7.1 Per-zone posture matrix

| Posture | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise / Regulated / NPI) |
| --- | --- | --- | --- |
| File upload allowed? | Yes — author choice | Yes if business case documented | **No** by default; case-by-case label-gated exception with CISO sign-off |
| Image upload allowed? | Yes | Yes if business case documented | **No** by default for Regulated / NPI; case-by-case |
| Maximum size | Microsoft default | Microsoft default; document any per-tenant cap | Microsoft default; cap per Control 1.13 SIT performance profile |
| Sensitivity-label gating | Optional | Required — uploads of `Confidential` or higher prompt a label-aware DLP warning or block | Required — uploads of `Highly Confidential` / `Regulated` / `NPI` are blocked or require step-up authentication per Control 1.17 |
| Audit | Standard `CopilotInteraction` event | Standard event + DSPM for AI activity capture | Standard event + DSPM for AI capture + Sentinel correlation under §10 |
| Persistence | Conversation-scoped (uploads do not enrich the agent's knowledge for other users) — verify per release | Conversation-scoped | Conversation-scoped + retained per Control 5.x record-retention policy on the conversation transcript |

### 7.2 Configure the agent toggles

1. In Copilot Studio → agent → **Settings → Generative AI**, set **File uploads** and **Image uploads** per the §7.1 row for the agent's zone.
2. For per-knowledge-source upload (where the source itself accepts uploaded documents — e.g., the "Knowledge source with documents" connector), configure within the knowledge source row.
3. Save and publish.

### 7.3 Configure sensitivity-label gating

For Zone 2 and Zone 3 agents, the upload-time label check is enforced through the [Control 1.13 — Sensitive Information Types and Sensitivity Labels](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) infrastructure and the §9 Purview DLP policy targeting the **Microsoft 365 Copilot** location.

1. Verify that the relevant SITs and labels exist in Purview (Control 1.13 §3 SIT inventory).
2. In §9 below, the DLP policy authored for the Microsoft 365 Copilot location includes a rule that inspects user-supplied content for the SITs and either warns or blocks per the §7.1 row.
3. For endpoint-level upload control (e.g., blocking upload from an unmanaged device), the [Control 1.17 — Endpoint and Network Controls](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) endpoint DLP profile is the enforcement point.

### 7.4 Validation

1. As `svc-scope-pos`, upload `scope-test-public.pdf` (a synthetic file containing only the literal string `SCOPE-PROBE-PUBLIC`) to a Zone 2 agent. Expected: upload accepted, agent answers from upload.
2. As `svc-scope-pos`, upload `scope-test-confidential.pdf` (a synthetic file containing the string `SCOPE-PROBE-CONFIDENTIAL` and labelled Confidential via Control 1.13) to a Zone 2 agent. Expected: per §7.1 row, either prompt or block; transcript captured as artifact E11.
3. As `svc-scope-pos`, attempt the same upload to a Zone 3 NPI agent. Expected: blocked.
4. Verify the uploaded content does not appear as a citation in a different user's conversation with the same agent. Capture as artifact E12.

### 7.5 Common pitfalls in §7

- **Treating upload as out of scope for inventory.** Uploads bypass §3 because they are user-supplied. The compensating control is §7 + §9 — do not skip either.
- **Assuming uploads are not retained.** Whether and where uploads are retained varies by release and by knowledge-source configuration. Verify per release before classifying upload-only as ephemeral.
- **Missing Control 1.17 endpoint enforcement.** A user on an unmanaged device can still upload Highly Confidential content to a Zone 2 agent if endpoint DLP is not configured. Coordinate with Control 1.17.

---
## §8 Step 6 — Purview DSPM for AI policies and Activity Explorer

**Purpose:** Layer DSPM-for-AI insider risk and oversharing detections on top of the §3 inventory and §4–§7 minimization, so that scope drift, unsanctioned grounding sources, and risky prompt patterns surface as auditable signals rather than as silent regressions.

**Operator:** Purview Data Security AI Admin
**Estimated time:** 45–90 minutes for the first policy set; 15 minutes per incremental edit
**Outcome:** DSPM for AI is opted in for the tenant; the recommended detection policies are enabled and tuned per zone; Activity Explorer queries return the agent / user / SIT / sensitivity-label dimensions needed for §10 scope-drift hunts.

!!! note "Boundary with Control 1.6"
    Tenant-wide DSPM-for-AI onboarding (audit ingestion, role assignment, recommendation review) is owned by [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md). Step §8 here configures the **agent-scope-drift-relevant** detections only. If DSPM for AI has not been onboarded under Control 1.6, stop and complete that prerequisite first.

### 8.1 Verify DSPM for AI prerequisites

1. Sign in to the **Microsoft Purview portal** (`https://purview.microsoft.com`) as Purview Data Security AI Admin.
2. Navigate to **Solutions → DSPM for AI → Overview**.
3. Confirm:
   - Audit log ingestion is on (Control 6.x prerequisite).
   - The tenant has at least one Microsoft 365 Copilot license assigned (DSPM for AI signal source).
   - The Insider Risk Management connector is configured if your firm uses IRM correlation.
4. If any item is unmet, hand back to Control 1.6.

### 8.2 Enable the policy bundle

1. Navigate to **Solutions → DSPM for AI → Policies**.
2. Microsoft surfaces a curated set of recommended policies (the exact list evolves — verify against [Microsoft Learn — DSPM for AI policies](https://learn.microsoft.com/en-us/purview/dspm-for-ai-policies)). The minimum set for Control 1.14 scope-drift coverage is:

| Policy | Purpose | Zone applicability |
| --- | --- | --- |
| Detect risky AI usage | Flags prompts and responses with risky intent indicators | All zones; tune signal threshold per zone |
| Detect unethical behavior in AI | Flags prompts probing for jailbreaks or policy circumvention | All zones |
| Detect sensitive info in AI | Flags prompts and responses containing SITs from Control 1.13 | Zone 2 / Zone 3 |
| Sensitive info shared with third-party AI | Flags posting of sensitive content to non-sanctioned AI endpoints | All zones — pair with Control 1.17 |

3. For each policy, click **Use this template** (or **Configure**), confirm scope (all users, or scoped per zone), and create.

### 8.3 Tune signal thresholds per zone

For Zone 3 / Regulated / NPI agents, lower the signal-to-alert threshold so a single SIT match in a prompt or response generates an alert. For Zone 1, leave the default (which typically requires a pattern over time) so the canary is not noisy.

Capture the tuned threshold per policy as artifact E13.

### 8.4 Activity Explorer queries for §10 scope-drift hunts

Navigate to **Solutions → DSPM for AI → Activity explorer** (the heading evolves; verify per release). The dimensions you need available for §10 are:

- Agent name / app ID.
- User UPN.
- Activity type (prompt, response, file upload, citation source).
- SIT match name and count.
- Sensitivity label of cited content.
- Source URL or knowledge source ID.

Pin a saved query named `q-1.14-scope-drift-baseline` filtered to the agents in the §3 inventory; this becomes the baseline view referenced in §10. Capture as artifact E14.

### 8.5 Common pitfalls in §8

- **Skipping the Control 1.6 onboarding prerequisite.** Without DSPM ingestion, the §10 scope-drift hunt has no signal source.
- **Leaving Zone 1 thresholds at Zone 3 sensitivity.** The canary will produce alert fatigue and be ignored.
- **Treating DSPM for AI as a substitute for §9 DLP enforcement.** DSPM detects; DLP enforces. You need both.

---

## §9 Step 7 — Purview DLP for the Microsoft 365 Copilot location

**Purpose:** Enforce sensitivity-aware blocks and warnings on prompts and responses that flow through Copilot Studio agents and Microsoft 365 Copilot, including the per-conversation file uploads from §7. This is **runtime** enforcement complementing §4 (inventory-time enforcement) and §8 (detection).

**Operator:** Purview Compliance Admin
**Estimated time:** 60–90 minutes for the first policy; 15 minutes per incremental rule
**Outcome:** A Purview DLP policy named (suggested) `dlp-1.14-copilot-runtime` targets the **Microsoft 365 Copilot and Copilot Chat** location with rules that warn or block based on the SITs and sensitivity labels from Control 1.13; positive- and negative-path validation transcripts captured.

### 9.1 Open Purview DLP

1. Sign in to the **Microsoft Purview portal** (`https://purview.microsoft.com`) as Purview Compliance Admin.
2. Navigate to **Solutions → Data Loss Prevention → Policies**.
3. Click **+ Create policy**.

### 9.2 Choose the Custom template

1. Under **Categories**, select **Custom**.
2. Under **Templates**, select **Custom policy**.
3. Click **Next**.

### 9.3 Name and scope

1. **Name:** `dlp-1.14-copilot-runtime`.
2. **Description:** `Runtime DLP for Copilot Studio agents and M365 Copilot — Control 1.14`.
3. **Admin units:** select the relevant admin units (or Full directory if your firm does not use AU scoping).
4. Click **Next**.

### 9.4 Choose the Microsoft 365 Copilot location

1. On the **Locations to apply the policy** step, toggle **on** the **Microsoft 365 Copilot and Copilot Chat** location. Toggle off all other locations for this Control 1.14 policy (other locations are owned by other DLP policies under Controls 1.13, 4.6, 5.x).
2. Under **Include** / **Exclude**, scope to specific users or groups if your firm rolls out per zone; otherwise leave at **All users**.
3. Click **Next**.

### 9.5 Define the rules

Create one rule per detection bucket. Suggested minimum rules:

**Rule R1 — Block NPI in prompts:**

- Conditions: Content contains SIT `SIT-1.13-NPI-Aggregate` (or your equivalent NPI SIT).
- Actions: Restrict access — Block.
- User notifications: On — surface the policy tip text from Control 1.13 to the end user.
- User overrides: Off (Zone 3); Allow with business justification (Zone 2).
- Incident reports: On — notify Purview Compliance Admin and the Compliance Officer mailbox.

**Rule R2 — Warn on Confidential label in prompts:**

- Conditions: Content has sensitivity label `Confidential`.
- Actions: Restrict access — Notify only.
- User notifications: On.

**Rule R3 — Block Highly Confidential / Regulated label in responses:**

- Conditions: Response content has sensitivity label `Highly Confidential` or `Regulated`.
- Actions: Restrict access — Block (the response is suppressed; the user receives a policy tip).
- Incident reports: On.

**Rule R4 — Block uploads of Confidential-or-higher to Zone 2 / Zone 3 agents:**

- Conditions: User uploaded content via Copilot Studio agent in environment `<Zone 2 / Zone 3>` AND content has sensitivity label `Confidential` or higher OR contains any SIT from the Control 1.13 NPI bundle.
- Actions: Restrict access — Block.
- User notifications: On — refer the user to the §7 file-upload policy text.

For each rule, click **Save**, then **Next**.

### 9.6 Test mode then enforce

1. Set the policy to **Test it out first** with notifications enabled. Run for 5–10 business days against the canary agents.
2. Review the **DLP alerts** dashboard (`Solutions → Data Loss Prevention → Alerts`) and the **Activity explorer** for false positives.
3. Tune rules; flip to **Turn it on right away**.
4. Capture the active policy summary as artifact E15.

### 9.7 Validation

1. As `svc-scope-pos`, ask the Zone 3 agent a prompt containing a synthetic NPI string (e.g., `SSN 123-45-6789`). Expected: prompt is blocked; user sees the R1 policy tip; incident report fires. Capture as artifact E16-pos.
2. Ask the Zone 2 agent the same prompt. Expected: per R1 configuration, either block or allow-with-justification; capture transcript.
3. Have the agent attempt to surface a citation from a `Highly Confidential`-labelled document. Expected: response suppressed by R3; capture as artifact E16-neg.
4. Upload a Confidential-labelled file to the Zone 2 agent. Expected: blocked by R4; capture transcript.

### 9.8 Common pitfalls in §9

- **Only configuring the Microsoft 365 Copilot location and forgetting Copilot Chat.** The location toggle covers both — verify the toggle label in your tenant.
- **Leaving the policy in Test mode indefinitely.** Test mode produces detections but does not enforce. Set a calendar reminder to flip to enforce.
- **Authoring rules that overlap with Control 1.13 policies.** Cross-coordinate with the Control 1.13 owner to avoid double-blocking and conflicting policy tips.

---

## §10 Step 8 — Scope-drift detection via the Microsoft 365 Copilot audit schema

**Purpose:** Build the audit-driven hunt that detects scope drift — agents grounding from sources outside their §3 inventory baseline, prompts probing for out-of-scope content, citations resolving to unsanctioned SharePoint sites, or DLP overrides. This is the detection backbone behind §11 alerting.

**Operator:** Purview Compliance Admin co-authoring with Sentinel / SIEM engineer
**Estimated time:** 90–120 minutes for the initial query set; 30 minutes per incremental hunt
**Outcome:** A documented set of audit queries persisted in the Purview Audit search history (and exported to Sentinel as scheduled analytics rules where the firm uses Sentinel) that detect each named scope-drift pattern.

### 10.1 Confirm the Copilot audit schema is populated

1. Sign in to the **Microsoft Purview portal** as Purview Compliance Admin.
2. Navigate to **Solutions → Audit → Search**.
3. Set the date range to the last 24 hours.
4. Set **Activities — friendly names** filter to include the Copilot record types. The current record types include:
   - `CopilotInteraction` — user prompts and Copilot responses across Copilot Chat and Copilot Studio agents.
   - `BotsRuntimeService` — Copilot Studio agent runtime events (Bot Framework / Power Virtual Agents lineage).
   - `MicrosoftFlow` — Power Automate flows invoked by agent actions.
   - `PowerAppsPlan` — Power Apps and connector activity used by agents.
   - `AzureActiveDirectory` — sign-in and consent events for agent service principals.
   - Verify the active record-type names per the [Microsoft Learn — Audit log activities](https://learn.microsoft.com/en-us/purview/audit-log-activities) reference for your release.
5. Run the search; confirm rows return.

### 10.2 Hunt H1 — Out-of-inventory grounding source

**Question:** Did any agent in the §3 inventory cite a SharePoint URL that is **not** in the agent's approved knowledge sources?

1. Run an audit search filtered to `CopilotInteraction` for the last 7 days.
2. Export the results.
3. Join the export against the §3 inventory on `AppId` / agent name; flag rows where the cited SharePoint URL does not match any approved knowledge source URL for that agent.
4. Persist the join logic as a saved Sentinel KQL rule (where Sentinel is in use) named `1.14-H1-grounding-out-of-inventory`. Capture as artifact E17.

### 10.3 Hunt H2 — Web search re-enabled on a Zone 3 NPI agent

**Question:** Did any administrator re-enable the **Web search** toggle on a Zone 3 NPI agent after §6 disabled it?

1. Search `BotsRuntimeService` and the agent admin operation event (verify operation name per release — recent builds use `CopilotStudioAgentSettingChanged` or similar).
2. Filter to the Zone 3 agent app IDs from §3.
3. Filter to the setting key for web search.
4. Persist as `1.14-H2-web-search-reenabled`. Capture as artifact E18.

### 10.4 Hunt H3 — Connector added that is Blocked under §4

**Question:** Did any maker successfully add a connector to an agent that should have been blocked by `dlp-1.14-zone-2` or `dlp-1.14-zone-3`?

1. Search `PowerAppsPlan` and `MicrosoftFlow` for the connector-added operations.
2. Filter to the environments scoped under §4.
3. Cross-reference against the Blocked group per environment.
4. Persist as `1.14-H3-blocked-connector-added`. Capture as artifact E19.

### 10.5 Hunt H4 — DLP override / business-justification override

**Question:** Did any Zone 2 user override a §9 DLP rule using business justification, and was the justification reviewed?

1. Search the DLP audit events for override actions.
2. Filter to policy `dlp-1.14-copilot-runtime`.
3. Persist as `1.14-H4-dlp-override`. Capture as artifact E20.

### 10.6 Hunt H5 — Sign-in anomaly on agent service principal

**Question:** Did any agent service principal sign in from an unexpected geography or IP range?

1. Search `AzureActiveDirectory` for service principal sign-ins.
2. Filter to the SPNs listed in §3 field F11 (where applicable).
3. Cross-reference Conditional Access named-location policies under [Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md).
4. Persist as `1.14-H5-spn-signin-anomaly`. Capture as artifact E21.

### 10.7 Sentinel correlation and retention

If your firm operates Microsoft Sentinel:

1. Forward the Office 365 Management Activity API and Purview Audit data via the **Microsoft 365** connector and the **Microsoft Purview Information Protection** connector.
2. Convert hunts H1–H5 to scheduled analytics rules with severity tagged per zone.
3. Route alerts to the SOC queue per the run-book.
4. Retain audit data per Control 6.x record-retention policy — the default Purview retention may not satisfy SEC 17a-4 / FINRA 4511 timelines without the M365 Archiving / Communication Compliance retention add-on.

### 10.8 Common pitfalls in §10

- **Hard-coding record-type names in saved searches.** Microsoft renames record types between releases. Re-validate every quarter and on each new tenant onboarding.
- **Searching only `CopilotInteraction` and missing `BotsRuntimeService`.** Studio-built agents emit both; missing `BotsRuntimeService` will hide admin-action drift.
- **Forwarding audit to Sentinel without reconciling the lookback window.** Sentinel's KQL window does not equal Purview's UI window; verify both.

---

## §11 Step 9 — Alert policies for scope-drift events

**Purpose:** Convert the §10 hunts into named, on-call-routable alert policies so that scope-drift events page the right responder within the SLA defined in the firm's incident response plan.

**Operator:** Purview Compliance Admin (Purview alert policies) and / or Microsoft Defender XDR Admin (XDR alert policies)
**Estimated time:** 45 minutes for the first alert; 10 minutes per subsequent alert
**Outcome:** Named alert policies route §10 hunts H1–H5 to the on-call queue with severity tagged per zone; alert acknowledgement and resolution are evidenced.

!!! warning "Authoring location"
    Alert policies are authored in **Purview portal → Solutions → Policies → Alert policies** (current Purview surface) and / or **Defender XDR portal → Email & collaboration → Policies & rules → Alert policy** (Defender XDR surface for cross-workload alerts). They are **not** authored from "Audit log search → Create alert policy" — that breadcrumb does not exist in the current portal. Use one or both surfaces per your firm's SOC routing.

### 11.1 Create the H1 alert (out-of-inventory grounding)

1. Sign in to the **Purview portal** as Purview Compliance Admin.
2. Navigate to **Solutions → Policies → Alert policies**.
3. Click **+ New alert policy**.
4. **Name:** `alert-1.14-H1-grounding-out-of-inventory`.
5. **Severity:** High for Zone 3; Medium for Zone 2.
6. **Category:** Information governance.
7. **Activity:** Select the underlying `CopilotInteraction` activity matching the H1 hunt logic; where the activity-picker does not natively support the join, configure the alert to fire on the related raw event and use the §10 Sentinel rule for join-based suppression.
8. **Recipients:** the Compliance Officer mailbox + the SOC on-call distribution list.
9. **Email threshold:** 1 (do not throttle on a Zone 3 finding).
10. Click **Save**. Capture as artifact E22.

### 11.2 Create the remaining alerts

Repeat §11.1 for H2 (`alert-1.14-H2-web-search-reenabled`, Severity High), H3 (`alert-1.14-H3-blocked-connector-added`, Severity Medium), H4 (`alert-1.14-H4-dlp-override`, Severity Medium for Zone 2 / High for Zone 3), and H5 (`alert-1.14-H5-spn-signin-anomaly`, Severity High).

### 11.3 Defender XDR cross-workload alert option

For firms that consolidate alerts in Defender XDR:

1. Sign in to **Defender XDR portal** (`https://security.microsoft.com`) as the appropriate Defender XDR role.
2. Navigate to **Email & collaboration → Policies & rules → Alert policy**.
3. Author the same alerts referencing the same underlying activities; tag the alert with the `Control 1.14` custom tag for SOC routing.

### 11.4 Validation

1. Trigger H2 deliberately on the canary Zone 3 agent (toggle Web search on, then off). Expected: the H2 alert fires within the documented SLA; the SOC ticket opens; the on-call acknowledges and resolves; the agent setting is reverted. Capture the alert email, the Sentinel incident, and the resolution notes as artifact E23.
2. Repeat per alert until each fires on a synthetic trigger.

### 11.5 Common pitfalls in §11

- **Authoring the alert at "Audit log search → Create alert policy".** That breadcrumb is from the legacy Security & Compliance Center and does not reflect current Purview navigation. Use the breadcrumb in the §11 warning admonition.
- **Throttling Zone 3 alerts.** A single out-of-inventory grounding on a NPI agent is a finding; do not throttle.
- **Routing to a shared mailbox without on-call escalation.** Pair the Purview alert with PagerDuty / Opsgenie / equivalent so an unresponded alert escalates.

---

## §12 Step 10 — Microsoft Entra ID Governance Access Reviews for agent identities

**Purpose:** Wrap every agent service principal, every SG-AgentAccess group, and every privileged role assignment that grants agent administration with periodic Access Reviews so unused identities and stale memberships are removed before they accumulate scope.

**Operator:** Entra Identity Governance Admin
**Estimated time:** 45 minutes per review template; 15 minutes per zone-specific instance
**Outcome:** Access Review templates exist for (a) SG-AgentAccess groups, (b) agent service principal owners, (c) Copilot Studio author / maker role assignments; reviewers and cadence match the §13 review process.

!!! note "Licensing prerequisite"
    Entra ID Governance Access Reviews require the Entra ID P2 license (or Microsoft Entra ID Governance SKU) on the reviewers and the reviewed principals where the principal is a user. Verify per the licensing matrix in §2.1.

### 12.1 Open Access Reviews

1. Sign in to the **Microsoft Entra admin center** (`https://entra.microsoft.com`) as Entra Identity Governance Admin.
2. Navigate to **Identity governance → Access reviews**.
3. Click **+ New access review**.

### 12.2 Review template AR1 — SG-AgentAccess groups

- **Select what to review:** Teams + Groups.
- **Review scope:** Select groups → pick all groups matching `SG-AgentAccess-*`.
- **Reviewers:** Group owners + the agent owner of record (from the §3 registry) as a fallback reviewer.
- **Recurrence:** Quarterly for Zone 2; Monthly for Zone 3 (author two AR1 instances if you mix zones).
- **Duration:** 14 days.
- **Settings:** require justification on Approve; require justification on Deny; auto-apply results after the review closes; if no response, deny by default.
- **Save** and capture as artifact E24.

### 12.3 Review template AR2 — Agent service principal owners

- **Select what to review:** Applications.
- **Review scope:** Service principals tagged with `Tag = Control 1.14 agent` (apply this tag at SPN provisioning time as part of the §3 intake).
- **Reviewers:** the AI Governance Lead + the named agent owner.
- **Recurrence:** Quarterly.
- **Save** and capture as artifact E25.

### 12.4 Review template AR3 — Privileged Copilot Studio role assignments

- **Select what to review:** Microsoft Entra roles → Copilot Studio admin role (or the equivalent admin role for your tenant).
- **Reviewers:** the AI Governance Lead.
- **Recurrence:** Quarterly.
- **Save** and capture as artifact E26.

### 12.5 Common pitfalls in §12

- **Missing the SPN tagging step.** Without the `Control 1.14 agent` tag on SPNs, AR2 cannot scope. Make tagging mandatory at intake.
- **Allowing reviewers to silently approve.** Require justification on every decision; without it, reviews are theatre.
- **Letting the default reviewer be the SPN itself.** Service principals cannot review themselves; configure the agent owner of record as reviewer.

---

## §13 Step 11 — Quarterly access review process and zone cadence

**Purpose:** Define the operational rhythm — who reviews what, when, with what evidence template — that turns the §12 Access Review machinery into a documented, repeatable governance process auditors can sample.

**Operator:** AI Governance Lead with input from Compliance Officer, Internal Audit, and the agent owners
**Estimated time:** 2–4 hours per quarter (Zone 2); 1–2 hours per month (Zone 3)
**Outcome:** A reviewed-and-signed quarterly attestation per zone, persisted in the firm's evidence repository, including the §12 review outcomes, the §3 reconciliation deltas, the §10 hunt findings, and any §11 alerts that fired and were resolved.

### 13.1 Cadence matrix

| Zone | §3 inventory reconcile | §12 Access Reviews | §10 hunts run | §11 alerts triaged | §13 attestation |
| --- | --- | --- | --- | --- | --- |
| Zone 1 | Annual | Annual (AR1 only) | Quarterly | Continuously | Annual |
| Zone 2 | Quarterly | Quarterly (AR1, AR2, AR3) | Monthly | Continuously | Quarterly |
| Zone 3 | Monthly | Monthly (AR1) + Quarterly (AR2, AR3) | Weekly | Continuously, On-call | Monthly |

### 13.2 Per-cycle responsibilities

| Step | Owner | Input | Output |
| --- | --- | --- | --- |
| Pull §3 inventory for the cycle | AI Administrator | Lists A, B, C from §3.1 | Reconciled inventory (artifact for the cycle) |
| Run §12 Access Reviews | Reviewers per AR template | AR1 / AR2 / AR3 instances | Review decisions auto-applied |
| Run §10 hunts | Purview Compliance Admin | Saved searches H1–H5 | Hunt result CSVs |
| Triage §11 alerts | SOC + Compliance Officer | Alert queue | Resolution notes per ticket |
| Compile attestation packet | AI Governance Lead | All of the above | Signed attestation PDF (artifact E27) |
| File attestation | Compliance Officer | Attestation packet | Stored in evidence repository for the cycle |

### 13.3 Attestation template

The attestation per cycle is a short structured document containing:

1. Cycle identifier (e.g., `1.14-Zone-3-2026-Q2-M02`).
2. Reviewer roster with UPNs and signature timestamps.
3. §3 inventory delta vs. prior cycle (added agents, removed agents, surface changes).
4. §12 review outcomes per template (approved, denied, pending; numeric counts).
5. §10 hunt result summary per H-rule.
6. §11 alert summary (count, severity distribution, mean time to resolve).
7. Open findings with owner and target close date.
8. Sign-off block (AI Governance Lead, CISO for Zone 3, Compliance Officer).

A skeleton template is published alongside this playbook at `templates/1.14-attestation-template.md` (where your firm uses the FSI-AgentGov-Solutions companion repo, the deployable template lives under `solutions/1.14-attestation-template/`).

### 13.4 Common pitfalls in §13

- **Cycle drift.** A Zone 3 monthly cycle that slips to bimonthly creates an audit finding. Calendar the cycle on the AI Governance Lead's recurring agenda.
- **Reviewers signing without reading.** Require numeric responses (count of approved / denied) on the attestation, not just a signature, to surface attention failures.
- **Storing attestations only in email.** Persist to the firm's evidence repository with retention per Control 6.x.

---

## §14 Step 12 — Verification handoff

The procedural enforcement above is necessary but not sufficient. The verification suite — synthetic prompts, scope-probe transcripts, evidence collection, and reproducible test harnesses — lives in the companion playbook:

- [`verification-testing.md`](verification-testing.md)

That playbook covers, for Control 1.14:

- The `scope-test-Z*-001` and `scope-test-drift-001` test fixtures introduced in §2.4 above, with the full prompt set and expected outputs per zone.
- The `svc-scope-pos` / `svc-scope-neg` / `svc-scope-drift-actor` synthetic identities and the steps to provision and decommission them.
- The §5.6 positive- / negative-path validation expanded to the full SIT and label matrix.
- The §6 Web search re-enable test and audit lookup.
- The §7 file-upload posture matrix tests.
- The §9 DLP runtime tests (block, warn, override).
- The §10 hunt H1–H5 synthetic trigger procedures.
- The §11 alert-fires-within-SLA verification.
- The evidence-collection checklist mapping each test to the artifact ID in §15.

Hand off to `verification-testing.md` after publishing the agents under §3–§9 and after the §10 / §11 / §12 alerting and review machinery is enabled.

---

## §15 Step 13 — Evidence pack, anti-patterns, FSI incident handling, and troubleshooting handoff

### 15.1 Evidence pack manifest (E1–E27)

The artifacts collected in §2–§14 form the Control 1.14 evidence pack. Each artifact has an ID, owner, format, retention tag, and SHA-256 checksum recorded in the manifest. Manifest generation is automated by `scripts/build-evidence-manifest.ps1` in the FSI-AgentGov-Solutions companion repo; the schema is below.

| ID | Description | Source surface | Owner | Format | Retention tag | Section |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | License inventory snapshot (Copilot, Entra ID P2 / Governance, Purview SKUs) | Microsoft 365 admin center → Billing → Licenses | AI Administrator | CSV | 7y per Control 6.x | §2.1 |
| E2 | Role assignment snapshot (Entra PIM eligibility + active assignments for the §2.2 roles) | Entra admin center → Roles and admins | Entra Identity Governance Admin | JSON | 7y | §2.2 |
| E3-A | Copilot Studio agent list per environment | Copilot Studio → admin agent inventory | AI Administrator | CSV | 7y | §3.1 |
| E3-B | PPAC Resources → Copilots / Agents export per environment | Power Platform Admin Center | Power Platform Admin | CSV | 7y | §3.1 |
| E3-C | Purview DSPM for AI — AI apps and agents export | Purview portal → DSPM for AI → Reports | Purview Data Security AI Admin | CSV | 7y | §3.1 |
| E3 | Reconciled agent inventory (the §3.2 join) | Control 1.2 registry | AI Governance Lead | XLSX or registry export | 7y | §3.2 |
| E4 | PPAC DLP — connector classification screenshots per zone policy | PPAC → Security → Data and privacy → Data policies | Power Platform Admin | PNG bundle | 7y | §4.2 |
| E5 | PPAC DLP — final policy summary screenshot per zone | PPAC | Power Platform Admin | PNG | 7y | §4.5 |
| E6 | DLP block (negative) and DLP allow (positive) test transcripts in Copilot Studio | Copilot Studio canary | AI Administrator | PNG + transcript text | 7y | §4.7 |
| E7-pos / E7-neg-1 / E7-neg-2 / E7-neg-3 | SharePoint scope positive- and negative-path transcripts | Copilot Studio canary | AI Administrator | Transcript text + screenshots | 7y | §5.6 |
| E8 | Copilot Studio Generative AI panel screenshot per Zone 3 NPI agent (Web search OFF + adjacent toggles) | Copilot Studio | AI Administrator | PNG | 7y | §6.2 |
| E9 | PPAC `dlp-1.14-zone-3` policy showing public-website connector blocked | PPAC | Power Platform Admin | PNG | 7y | §6.3 |
| E10 | Publish-time failure when web-search re-enabled on Zone 3 agent | Copilot Studio | AI Administrator | PNG + transcript | 7y | §6.4 |
| E11 | File-upload sensitivity-label gating transcript (Confidential block / warn) | Copilot Studio canary | AI Administrator | Transcript text | 7y | §7.4 |
| E12 | Cross-user upload non-leakage verification transcript | Copilot Studio canary | AI Administrator | Transcript text | 7y | §7.4 |
| E13 | DSPM for AI policy threshold tuning per zone | Purview portal | Purview Data Security AI Admin | PNG | 7y | §8.3 |
| E14 | DSPM for AI Activity Explorer saved query `q-1.14-scope-drift-baseline` | Purview portal | Purview Data Security AI Admin | KQL or saved-search export | 7y | §8.4 |
| E15 | Active `dlp-1.14-copilot-runtime` policy summary | Purview portal → DLP → Policies | Purview Compliance Admin | PNG + JSON export | 7y | §9.6 |
| E16-pos / E16-neg | Copilot DLP block (NPI) and response-suppression (Highly Confidential) transcripts | Copilot Studio canary | Purview Compliance Admin | Transcript text | 7y | §9.7 |
| E17 | H1 hunt — saved Sentinel KQL or Purview audit query for out-of-inventory grounding | Sentinel / Purview Audit | Purview Compliance Admin | KQL file | 7y | §10.2 |
| E18 | H2 hunt — Web search re-enabled on Zone 3 agent | Sentinel / Purview Audit | Purview Compliance Admin | KQL file | 7y | §10.3 |
| E19 | H3 hunt — Blocked connector added | Sentinel / Purview Audit | Purview Compliance Admin | KQL file | 7y | §10.4 |
| E20 | H4 hunt — DLP override / business-justification override | Sentinel / Purview Audit | Purview Compliance Admin | KQL file | 7y | §10.5 |
| E21 | H5 hunt — agent SPN sign-in anomaly | Sentinel / Purview Audit | Purview Compliance Admin | KQL file | 7y | §10.6 |
| E22 | `alert-1.14-H1-grounding-out-of-inventory` alert policy summary | Purview portal → Policies → Alert policies | Purview Compliance Admin | PNG | 7y | §11.1 |
| E23 | Synthetic-trigger alert validation packet (alert email + SOC ticket + resolution) | Email + ITSM | SOC + Compliance Officer | PDF bundle | 7y | §11.4 |
| E24 | Access Review template AR1 (SG-AgentAccess groups) | Entra → Identity governance → Access reviews | Entra Identity Governance Admin | PNG + JSON | 7y | §12.2 |
| E25 | Access Review template AR2 (agent SPN owners) | Entra | Entra Identity Governance Admin | PNG + JSON | 7y | §12.3 |
| E26 | Access Review template AR3 (privileged Copilot Studio role) | Entra | Entra Identity Governance Admin | PNG + JSON | 7y | §12.4 |
| E27 | Per-cycle attestation packet (signed) | Evidence repository | AI Governance Lead | PDF | 7y | §13.3 |

Generate a SHA-256 manifest for the bundle:

```powershell
Get-ChildItem -Path .\evidence\1.14\*\* -Recurse -File |
    ForEach-Object {
        [pscustomobject]@{
            Path   = $_.FullName.Replace((Resolve-Path .\evidence\1.14).Path + '\', '')
            SHA256 = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
            Size   = $_.Length
            Mtime  = $_.LastWriteTimeUtc.ToString('o')
        }
    } | Export-Csv -NoTypeInformation -Path .\evidence\1.14\manifest-1.14-$(Get-Date -Format 'yyyyMMdd').csv
```

Persist the CSV manifest to the firm's evidence repository with the same retention tag.

### 15.2 Anti-patterns to avoid

The following patterns appear repeatedly in agent governance assessments. Each is an audit finding waiting to happen.

1. **Treating the Copilot Studio agent list as the system of record.** It is one of three lists. Reconcile per §3.
2. **Adding the SharePoint root site collection as a knowledge source instead of the smallest library or folder.** This silently expands scope for every future user query — see §5.3.
3. **Authoring the `dlp-1.14-zone-2` policy in the default Power Platform environment.** The default environment hosts unrelated maker activity tenant-wide; restricting connectors there produces collateral damage. Always scope to a named, governed environment — see §4.4.
4. **Disabling the **Web search** toggle on a Zone 3 agent without the §4 DLP backstop.** The toggle can be re-enabled in seconds; the DLP block at the environment level is the durable control — see §6.3.
5. **Building SG-AgentAccess groups for delegated-identity agents.** SG-AgentAccess groups apply only to authenticated-connection / managed-identity / Entra Agent ID grounded agents — see §5.1 and §5.5.
6. **Authoring alert policies at "Audit log search → Create alert policy".** That path does not exist in the current portal. Use Purview → Policies → Alert policies or Defender XDR → Email & collaboration → Policies & rules — see §11.
7. **Leaving Purview DLP for Microsoft 365 Copilot in Test mode indefinitely.** Test mode produces detections but does not enforce — see §9.6.
8. **Skipping the §12 SPN tagging step.** Without the `Control 1.14 agent` tag, AR2 cannot scope. Tag at SPN provisioning.
9. **Hard-coding Microsoft audit record-type names in saved searches.** They evolve. Re-validate every quarter — see §10.8.
10. **Treating DSPM for AI as authoritative for the agent inventory.** DSPM only sees agents that produced activity in the lookback window — see §3.6.
11. **Assuming Power Platform DLP narrows OAuth scopes.** It does not — that's Control 1.18's job — see §4 callout.
12. **Compressing the §13 review cycle when the AI Governance Lead is on PTO.** Build a deputy into the cycle calendar; cycle drift is itself a finding.

### 15.3 FSI incident handling — when scope drift becomes a notifiable event

A Control 1.14 finding that escalates to an actual unauthorized disclosure of NPI, MNPI, or regulated client data may trigger a regulatory notification obligation. The exact trigger and timeline depend on the regulation, the data class, and the firm's incident response plan. The table below is a quick reference — it is not legal advice; consult the firm's Compliance and Legal teams before any external notification.

| Regulation / authority | Indicative trigger | Indicative timeline | Owner of the notification |
| --- | --- | --- | --- |
| SEC Regulation S-P (amended 2024) | Unauthorized access to or use of customer information | Notify affected individuals as soon as practicable, but no later than 30 days after discovery | Compliance Officer + General Counsel |
| SEC cybersecurity disclosure (Form 8-K Item 1.05) | Material cybersecurity incident at a registrant | File 8-K Item 1.05 within 4 business days after determining materiality | General Counsel + CFO |
| FINRA Rule 4530 | Specified events including customer-information compromise | Report to FINRA within 30 calendar days | Compliance Officer |
| GLBA / Interagency Guidance on Response Programs | Unauthorized access to sensitive customer information | Notify primary federal regulator and affected customers as soon as possible | Compliance Officer + CISO |
| State breach notification statutes (varies — e.g., NY DFS Part 500 §500.17) | Cybersecurity event affecting the covered entity | NY DFS: 72 hours from determination | Compliance Officer + CISO |
| OCC Heightened Standards / Federal Reserve SR 11-7 (model risk) | Material model failure where the agent constitutes a covered model | Per the firm's MRM escalation matrix | CRO + Model Risk Management |
| CFTC Rule 1.31 (recordkeeping) | Loss of required records — including agent transcripts subject to recordkeeping | Per the CFTC notification matrix | Compliance Officer |

For each scope-drift incident, the §13 attestation cycle should reference the incident ticket and the disposition (notified / not notifiable / under review by Legal) so that the audit trail of the decision is preserved.

### 15.4 Troubleshooting handoff

For symptom-driven recovery — "the agent stopped citing the in-scope library", "DSPM for AI shows zero rows for an agent we know is in use", "the §11 alert fired but the SOC ticket has no payload", "users are seeing a `dlp-1.14-copilot-runtime` block that we did not author" — see the companion playbook:

- [`troubleshooting.md`](troubleshooting.md)

That playbook indexes symptoms to the section in this walkthrough that owns the recovery procedure and to the artifact in §15.1 that demonstrates the recovery worked.

---

## Cross-references

- Control of record: [Control 1.14 — Data Minimization and Agent Scope Control](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md)
- Adjacent and depended-upon controls:
  - [Control 1.2 — Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) (system of record for the §3 inventory)
  - [Control 1.4 — Advanced Connector Policies](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) (tenant-wide DLP)
  - [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) (tenant onboarding for §8)
  - [Control 1.13 — Sensitive Information Types and Sensitivity Labels](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) (SIT and label inventory powering §7 and §9)
  - [Control 1.17 — Endpoint and Network Controls](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) (endpoint DLP and Conditional Access for §5.5 SPN sign-in and §7 endpoint upload)
  - [Control 1.18 — Application-Level Authorization and RBAC](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) (OAuth scope minimization)
  - [Control 4.6 — Knowledge Source Restrictions and SharePoint Hygiene](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) (RCD / RSS / DAG underneath §5)

- Companion playbooks for Control 1.14:
  - [`powershell-setup.md`](powershell-setup.md) — automation of §3 inventory and §10 hunt scheduling
  - [`verification-testing.md`](verification-testing.md) — synthetic test suite per §14
  - [`troubleshooting.md`](troubleshooting.md) — symptom-to-section index per §15.4

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*