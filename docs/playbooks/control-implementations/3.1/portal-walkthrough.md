# Control 3.1 — Portal Walkthrough: Agent Inventory and Metadata Management

**Control ID:** 3.1
**Pillar:** Reporting (Foundation)
**Playbook Type:** Portal Walkthrough (Admin Center UI)
**Last UI Verified:** April 2026
**Estimated Time:** 12–20 hours initial baseline build; 4–6 hours per quarterly attestation cycle thereafter
**Audience:** AI Governance Lead, AI Administrator, Power Platform Admin, Entra Agent ID Admin, Entra Global Reader, Purview Compliance Admin, Purview Records Manager, SharePoint Admin, Compliance Officer, Designated Supervisor / Registered Principal, CISO observer
**Prerequisites:** Pre-flight gates PRE-01 through PRE-05 (see §2) completed and evidenced; canonical metadata schema (§1.2) ratified by the AI Governance Council; SharePoint registry-of-record library provisioned and bound to a Purview retention policy

---

!!! danger "READ FIRST — Scope and routing"
    This walkthrough is the **portal-driven operating procedure for the canonical agent register** that every other Pillar 3 control consumes. It covers click-paths, evidence anchors, lifecycle-state procedures, and the quarterly attestation workflow across the **six discovery planes** enumerated in §0.3. It produces the stitched **system of record** that feeds Controls 3.2, 3.4, 3.6, 3.8, 3.9, 3.11, and 3.13.

    **Use the sibling playbooks for adjacent work:**

    | If you need… | Use this sibling |
    |---|---|
    | Bulk export, scheduled reconciliation, SHA-256 hashing, idempotent diffing | [PowerShell Setup](powershell-setup.md) |
    | Pre-attestation readiness checks, evidence validation, audit-pack completeness | [Verification & Testing](verification-testing.md) |
    | Stale exports, owner mismatches, missing-portal symptoms, sovereign-cloud surface gaps | [Troubleshooting](troubleshooting.md) |
    | Live-incident response when an inventory review surfaces an active high-risk or mis-scoped agent | [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) |
    | The "why" — regulatory mapping, zone tiering, related controls | [Control 3.1 specification](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) |

    **This is *not*…** the surface that authors any of the following. Each row tells you where the authority actually lives:

    | If you are looking for… | Go to… |
    |---|---|
    | Agent registration, intake form, approval workflow | [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
    | Audit-log pipeline, UAL retention, Sentinel ingestion | [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
    | Records Management, Preservation Lock, SEC 17a-4(f) WORM binding | [Control 1.9 — Records Management and Preservation Lock](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |
    | eDiscovery case authoring, custodian holds, evidence preservation | [Control 1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
    | Adversarial-input detection and incident telemetry | [Control 1.21 — Adversarial Input Logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) |
    | Managed Environments, environment classification, DLP grouping | [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) |
    | Validation evidence, regression testing, model-swap re-validation | [Control 2.5 — Testing, Validation, and Quality Assurance](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) |
    | Conflict-of-interest evaluation, comparative monitoring | [Control 2.11 — Bias Testing and Fairness Assessment](../../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) |
    | Orphan workflow execution, departed-owner remediation | [Control 3.6 — Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
    | Tenant-wide governance dashboard and reporting | [Control 3.8 — Copilot Hub and Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) |
    | Inventory-enforcement gating (publish blocks on incomplete metadata) | [Control 3.11 — Centralized Agent Inventory Enforcement](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) |
    | SharePoint grounding-source inventory and oversharing remediation | [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) and [Control 4.7 — Microsoft 365 Copilot Data Governance](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) |

!!! warning "Hedged-language reminder"
    Maintaining this inventory **helps support compliance with** FINRA Rule 4511 (books-and-records), FINRA Regulatory Notice 25-07 (AI/predictive-analytics supervision), SEC Rule 17a-3(a)(17) and 17a-4(b)(4) (six-year preservation), SOX Sections 302/404 (internal control over financial reporting), GLBA 501(b) (administrative safeguards inventory), OCC Bulletin 2011-12 / Federal Reserve SR 11-7 (model inventory and ongoing monitoring), CFTC Rule 1.31 (recordkeeping), NYDFS 23 NYCRR Part 500.13 / 500.16 / 500.17 (asset inventory and incident response), NIST AI RMF GOVERN 1.6, and FTC Safeguards Rule 16 CFR §314. It does **not** by itself satisfy any obligation. Inventory completeness, attestation timeliness, owner accountability, and evidence integrity are operational disciplines — not one-click settings.

    **Prohibited overclaims for this control** (do not write into your WSP, attestation memo, or examiner cover letter): *"complete inventory", "real-time discoverability", "guarantees agent visibility", "single pane of glass", "ensures lineage", "automatic enrollment", "zero shadow AI", "zero blind spots", "eliminates orphan risk", "will prevent unauthorized agents".*

    **Mandatory hedged substitutes:** *helps support / required for / aids in / contributes to / supports / is intended to / organizations should verify / authoritative system of record fed by multiple discovery surfaces and periodic reconciliation*.

!!! info "License Requirements"
    Verify SKU and preview availability at deploy time against current Microsoft Learn licensing guidance and your tenant Message Center. Per-surface floor:

    - **Microsoft 365 Copilot** (E3/E5 + Copilot license) — required for the Microsoft 365 Copilot Hub Inventory surface (Plane 1) and Copilot Studio agent metadata surfacing.
    - **Power Platform per-app / per-user / Process licenses** — entitlement metadata flows into the Plane 2 export; **Managed Environments** is required to surface environment-level governance attributes (see [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)).
    - **Microsoft Entra ID P1** (P2 recommended for PIM-elevated reads of Enterprise App registrations and the emerging Agent Registry blade).
    - **Microsoft Purview Audit (Standard or Premium)** — required for retention of registry-mutation events; Premium is recommended for Zone 3 long-horizon (≥ 1 year) audit retention.
    - **Microsoft Purview Records Management** — required for Preservation Lock on the registry document library when the firm treats the registry export as a SEC 17a-4(f)-format record.
    - **Microsoft Sentinel** (Control 3.9) — required for cross-surface registry-deviation alerting (orphan, dormant, drift).
    - **Microsoft Agent 365** (Plane 4) — preview-to-GA across 2026; verify entitlement and per-cloud availability before relying on it as a primary evidence source. Treat as additive, not authoritative, while in preview.
    - **SharePoint Premium** — may be required for some Plane 6 Connected Apps export and Data Access Governance (DAG) report exports; verify in your tenant.

!!! warning "Sovereign cloud parity (verify at deploy time)"
    Cross-cloud parity is **not symmetric** — verify at deploy time. The matrix below reflects the field as of April 2026 and is subject to change in any monthly release.

    | Surface / capability | Commercial | GCC | GCC High | DoD | 21Vianet (Gallatin) |
    |---|---|---|---|---|---|
    | M365 Copilot Hub Inventory (Plane 1) | GA | GA | Lagging — verify | Lagging — verify | N/A |
    | Power Platform Admin Center inventory (Plane 2) | GA | GA | GA — some columns lag | GA — some columns lag | Limited |
    | Entra Enterprise Apps (Plane 3) | GA | GA | GA | GA | GA |
    | Entra Agent Registry blade (preview) | Preview | Verify | Verify | Verify | Verify |
    | Agent 365 Admin Center (Plane 4) | Preview / Frontier | Limited / verify | Likely not at first GA | Likely not at first GA | N/A |
    | Purview retention binding (Plane 5) | GA | GA | GA — verify per release | GA — verify per release | Limited |
    | SharePoint Connected Apps + DAG (Plane 6) | GA | GA | Rolling — verify | Rolling — verify | Limited |
    | Programmatic agent inventory APIs / Graph exports | Rolling | Rolling — verify | Verify | Verify | Limited |

    Treat any parity gap as a **compensating-control conversation**, documented in the §1.5 sovereign-cloud determination memo and in the quarterly attestation memo. Do not assume feature equivalence across clouds.

---

## §0. Coverage boundary, registry-plane inventory, and portal-vs-PowerShell decision matrix

This section sets the operational boundary of the walkthrough and tells the operator when to switch to automation.

### 0.1 What this playbook covers

- Configuration and quarterly attestation of the **canonical agent register** across all six portal surfaces (the "discovery planes").
- Authoring and validation of the **canonical metadata schema** (§1.2) for every agent record.
- **Lifecycle state transitions** (Draft → In Review → Approved → Active → Deprecated → Decommissioned) executed via portal procedures with audit-log capture.
- **Orphaned-agent identification** (departed-owner, dormant beyond zone threshold, unowned shared agent, license-stripped) using the Microsoft 365 admin center "Manage Ownerless" action and equivalents in PPAC, Entra, and Agent 365.
- **DLP-policy mapping verification** per inventory entry, including the cross-plane reconciliation between Purview DLP for Microsoft 365 Copilot and Power Platform data policies for Copilot Studio.
- **Sensitivity-label inheritance check** per registry entry against grounding sources (SharePoint sites, OneDrive containers, Dataverse tables, web URLs).
- **Zone-specific portal workflows** with differentiated metadata depth, attestation cadence, and approval chains for Zone 1 / Zone 2 / Zone 3.
- **Quarterly attestation procedure** with the three-signature workflow (Inventory Owner → AI Governance Lead → Compliance Officer).
- **Examiner audit-pull procedure** for FINRA Rule 8210, OCC examination, Federal Reserve SR 11-7, SEC inquiry, NYDFS 500.13, and CFTC Rule 1.31, including point-in-time snapshot reconstruction and chain-of-custody record.
- **Sovereign-cloud caveats** per surface, with compensating-control language for surfaces not yet GA in your cloud.
- **Connection to downstream controls** that consume the register on the canonical AgentID join key.

### 0.2 What this playbook does NOT cover

| Out of scope here | Where it lives |
|---|---|
| Agent intake form, approval workflow, registry of approved agents | [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
| Unified Audit Log enablement, Sentinel ingestion, SIEM correlation rules | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
| Sensitivity-label authoring and policy publication | [Control 1.13 — Sensitive Information Types](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) |
| eDiscovery case management, custodian holds, search-and-export | [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
| Managed Environments enablement, environment groups, tier classification | [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) and [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) |
| Validation framework, regression suites, model-swap re-validation | [Control 2.5](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) |
| Orphan **remediation workflow** itself (this playbook detects and routes; remediation is here) | [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
| Reporting, dashboarding, governance dashboard build-out | [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) |
| Publish-time enforcement that blocks an agent without complete metadata | [Control 3.11](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) |
| SharePoint grounding-scope inventory and oversharing remediation | [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) and [Control 4.7](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) |

### 0.3 The six registry-source planes

No single Microsoft surface returns the complete agent register for an FSI tenant as of April 2026. Each surface is authoritative for a subset. The register of record is the **stitched export** produced by the §7 manual stitching procedure, signed by the AI Governance Lead, and archived under Preservation Lock.

| # | Plane | Source surface | Authoritative for | Typical refresh latency | Sovereign parity |
|---|---|---|---|---|---|
| 1 | **M365 Copilot Hub plane** | `https://admin.microsoft.com → Copilot → Inventory` | M365 Copilot agents, declarative agents, M365 Copilot extensions, Microsoft-provided agents | Hours (ad-hoc capture); some columns refresh on portal navigation | GA Commercial / GCC; lag in GCC High / DoD |
| 2 | **Power Platform plane** | `https://admin.powerplatform.microsoft.com → Resources → Copilot agents` (and `Manage → Inventory` legacy view) | Copilot Studio agents (custom and Studio-published declarative), environment-scoped attributes, Maker-side ownership | ~15 minutes inventory refresh; up to 48 h for deletion visibility; PPAC display capped at ~500 agents | GA broadly |
| 3 | **Entra plane** | `https://entra.microsoft.com → Identity → Applications → Enterprise applications` plus the **Agent Registry** blade (preview) and **App registrations** | App-registered declarative agents, plugin/connector OAuth posture, agent service principal IDs | Minutes for app changes; near-real-time for sign-in telemetry | GA Enterprise apps; preview Agent Registry — verify per cloud |
| 4 | **Agent 365 plane** | `https://admin.agent365.microsoft.com` (preview hostname — verify at deploy time) | Cross-cloud agent observability, ownerless-agent queue, governance cards, agent identity → telemetry join | Hours | Preview / Frontier program; likely not in GCC High / DoD / Gallatin at first GA |
| 5 | **Purview plane** | `https://purview.microsoft.com → Solutions → Data lifecycle management` (and **Records management**) | Retention / Preservation Lock binding for the registry document library, evidence-package retention | Per policy; binding propagates within hours | GA Commercial / GCC; verify per release in GCC High / DoD |
| 6 | **SharePoint plane** | SharePoint Admin → **Connected apps**; SharePoint Admin → **Reports → Data access governance** | SharePoint-grounded agent inventory, Connected App registrations, container ownership | Hours | GA Commercial / GCC; rolling sovereign |

!!! warning "There is no single pane"
    There is **no single Microsoft surface** that returns the complete register for an FSI tenant as of April 2026. Each surface is authoritative for a subset; some agents surface in only one plane. **The register of record is the stitched export produced by the §7 manual stitching procedure and signed by the AI Governance Lead.** Operators who treat any single surface as "the inventory" will undercount agents and miss the orphan and shadow signals. The §11 quarterly attestation enforces stitching; the §12 examiner audit-pull procedure produces the regulator-facing artifact.

### 0.4 Portal-vs-PowerShell decision matrix

Use this table to decide whether to stay in this portal walkthrough or switch to [PowerShell Setup](powershell-setup.md). The criterion is **scale, repeatability, and evidence integrity**.

| Task | Portal (this playbook) | PowerShell (sibling) | Reason for split |
|---|:---:|:---:|---|
| Initial register baseline (≤ 50 agents) | ✅ Primary | Optional | Faster click-through; screenshot evidence anchors |
| Register baseline (> 50 agents, > 500 agents in PPAC) | ⚠️ Reference only | ✅ Primary | PPAC display capped at ~500 — Azure Resource Graph required for full enumeration |
| Quarterly attestation diff (snapshot N vs N-1) | ❌ | ✅ Primary | Diff requires scripted hash and stable-sort key |
| Single-agent lifecycle state transition (record move) | ✅ Primary | Optional | Click-through with named-human attribution |
| Bulk lifecycle state transition (e.g., environment retirement) | ❌ | ✅ Primary | Repeatable, idempotent, audit-stamped |
| Orphan detection — departed-owner Graph join | ⚠️ Spot-check only | ✅ Primary | Tenant-scale Graph user enumeration |
| Dormant detection — no activity beyond Zone threshold | ⚠️ Spot-check only | ✅ Primary | Activity windows require unified-audit-log query |
| DLP-mapping verification per agent | ✅ Primary (spot-check) | ✅ Primary (bulk) | Zone-3 spot-check at attestation; bulk for full sweep |
| Sensitivity-label inheritance verification | ✅ Primary (spot-check) | ✅ Primary (bulk) | Same split |
| Examiner audit-pull packaging (FINRA 8210 etc.) | ⚠️ Cover memo + signatures | ✅ Primary | Hash + chain-of-custody manifest is scripted |
| Connected Apps export (SharePoint Plane 6) | ✅ Portal-only in some clouds | Where Graph is available | Portal screenshot is sometimes the only artifact in sovereign clouds |
| Evidence-pack hashing (SHA-256 of all artifacts) | ❌ | ✅ Primary | Tamper-evident manifest required for books-and-records |

**Rule of thumb:** Portal for **set-up, attestation review, single-agent transitions, and examiner-facing walkthroughs**. PowerShell for **scale, recurrence, hashing, and diffing**. If you find yourself clicking the same blade more than three times in one session, switch to the sibling.

---

## §1. Canonical metadata schema and surface inventory

The schema authored here is the **contract** that every other Pillar 3 control consumes. Get it wrong here and every downstream dashboard, report, and examiner pull is wrong.

### 1.1 Surface inventory (April 2026)

| Surface | Hosting | Authoritative for | GA status (Commercial) | Authoring artifact | Owner role |
|---|---|---|---|---|---|
| M365 Copilot Hub — **Agents** tab | `admin.microsoft.com → Copilot → Inventory → Agents` | Custom Copilot agents (Studio-published), tenant-installed agents | GA | Per-agent metadata side-panel + CSV export | AI Administrator |
| M365 Copilot Hub — **Declarative agents** tab | Same path, separate tab | Declarative agents (manifest-authored) | GA | Manifest + admin-side metadata | AI Administrator |
| M365 Copilot Hub — **Extensions / Connectors** | Same path, **Extensions** tab | M365 Copilot extensions, Graph connectors, API plugins | GA | Per-extension Entra app ID + permissions | AI Administrator |
| Power Platform Admin — **Resources → Copilot agents** | `admin.powerplatform.microsoft.com → Resources → Copilot agents` | Copilot Studio agents (env-scoped) | GA | Per-agent side panel + CSV export | Power Platform Admin |
| Power Platform Admin — **Manage → Inventory** (legacy Maker Inventory) | `Manage → Inventory` with `Item type = Agent` filter | Departed-owner cross-check, System Account ownership detection | GA | Per-item view + CSV export | Power Platform Admin |
| Entra Admin — **Enterprise applications** | `entra.microsoft.com → Identity → Applications → Enterprise applications` | Service principals, app ownership, OAuth permissions | GA | App list + per-app properties + CSV download | Entra Global Reader / Entra App Admin (write) |
| Entra Admin — **Agent Registry** (preview) | `Identity → Applications → Agent Registry` | Agent-classified app identities, agent ID directory | Preview | Agent-classified app catalog | Entra Agent ID Admin |
| Entra Admin — **App registrations** | `Identity → Applications → App registrations` | Developer-side declarative agent registrations | GA | App registration manifest | Entra App Admin |
| Agent 365 Admin Center | `admin.agent365.microsoft.com` (verify at deploy) | Cross-cloud agent observability, ownerless queue | Preview | Governance cards + export | Agent 365 Admin |
| Purview compliance portal — **Data lifecycle / Records management** | `purview.microsoft.com → Solutions → Data lifecycle management` | Retention / Preservation Lock for register library | GA | Retention policy + label policy | Purview Records Manager / Purview Compliance Admin |
| SharePoint Admin — **Connected apps** | SP Admin → Settings → Manage Connected apps | Site-registered Copilot extensions, Graph connectors | GA | Per-app permission record | SharePoint Admin |
| SharePoint Admin — **Reports → Data access governance** | SP Admin → Reports → Data access governance | Sites with Copilot grounding scope (joins to Plane 1 agents) | GA | DAG report + CSV export | SharePoint Admin |
| (Optional) Microsoft Defender for Cloud Apps — App Governance | Defender XDR → Cloud Apps → App governance | Third-party agent visibility for shadow-AI cross-check | GA | App catalog + risk score | Entra Security Admin |

### 1.2 The canonical metadata schema

This single authoritative table is the contract every other Pillar 3 control references. Any field added or removed here requires sign-off by the **AI Governance Lead** and a coordinated update across consuming controls (3.2, 3.4, 3.6, 3.8, 3.9, 3.11, 3.13).

| Field | Type | Required for | Authoritative source surface | Refresh cadence | Examiner-facing label | Validation rule |
|---|---|---|---|---|---|---|
| **AgentID** (canonical) | string (GUID or composite) | All zones | Source-surface native ID — Power Platform `botId`, Entra `appId`, M365 Copilot Hub `agentId` — promoted to canonical at first registration | Immutable post-create | "System identifier" | Non-null; immutable; primary join key across all planes |
| **Display Name** | string | All zones | Source surface (Plane 1 / Plane 2) | Real-time | "Agent name" | Non-null; ≤ 80 chars; matches WSP naming convention |
| **Agent Type** | enum {Copilot Studio Custom, Declarative, M365 Copilot Extension, Microsoft-Provided, Connected/Partner, Custom Engine Agent} | All zones | Plane 1 + Plane 2 | At promotion | "Agent classification" | Must be one enumerated value |
| **Platform / Source Surface** | multi-enum (Planes 1–6 a row was sourced from) | All zones | Stitching workbook | Per attestation | "Surfaces of record" | At least one plane sourced; "1+2+3" is healthy; "2 only" is a shadow-candidate |
| **Owner** | UPN | All zones | Plane 1 / Plane 2 / Plane 3 | Real-time | "Named human accountable" | Must be active employee per Graph; **named human, not a group** |
| **Backup Owner** | UPN | Zone 2 + Zone 3 | Manual; SharePoint register list | Quarterly review | "Backup accountable human" | Non-null for Zone 2/3; distinct from Owner; not a group |
| **Business Justification** | text | All zones | Manual; register list | At promotion + on material change | "Documented business purpose" | Non-null; ≥ 100 characters; references approving committee minute or change ticket |
| **Zone** | enum {1, 2, 3} | All zones | Manual classification per Control 2.1 + Control 1.2 | At promotion; reviewed quarterly | "Governance zone" | Must reconcile with environment Managed-Environment classification |
| **Data Classification** | enum {Public, Internal, Confidential, Highly Confidential / NPI / MNPI} | All zones | Sensitivity-label propagation per Control 1.13 | At promotion + on grounding-source change | "Data sensitivity" | Must reconcile with §9 Sensitivity-label inheritance check; defaults to **highest** label across grounding sources |
| **Regulatory Scope** | multi-enum {FINRA 4511, SEC 17a-3/4, SOX 404, GLBA 501(b), OCC 2011-12, Fed SR 11-7, NYDFS 500, CFTC 1.31, Reg BI, Reg S-P, BSA/AML, FINRA 25-07} | All zones | Manual at promotion | At promotion + on regulatory change | "Regulations the agent's outputs may touch" | At least one entry for any Zone 3 customer-facing or recordkeeping-scope agent |
| **Approval Records** | URL list (SharePoint document IDs / change tickets) | Zone 2 + Zone 3 | Manual at promotion | At promotion | "Approval evidence pack" | At least one record per zone-required signer |
| **Lifecycle State** | enum {Draft, In Review, Approved, Active, Deprecated, Decommissioned} | All zones | Register list (canonical); source surface (advisory) | On state change | "Current lifecycle state" | Transitions logged with author UPN + timestamp; canonical state lives in the register, **not** in the source surface |
| **Last Reviewed** | date | All zones | Register list | At each attestation | "Last attestation date" | ≤ 90 days for Zone 3; ≤ 180 days Zone 2; ≤ 365 days Zone 1 |
| **Next Review Due** | date (computed) | All zones | Register list | Computed at attestation | "Next attestation due" | Non-null; future-dated; drives attestation queue |
| **Connected Knowledge Sources** | URL list (SP sites, OneDrive, Dataverse tables, web URLs, external knowledge) | All zones | Plane 1 / Plane 2 metadata side-panel + Plane 6 DAG | At promotion + on grounding change | "Sources the agent grounds on" | Reconciled to Control 4.6 grounding inventory at attestation |
| **Connected Actions / Connectors** | list of (action ID, connector ID, OAuth posture) | All zones | Plane 1 + Plane 2 + Plane 3 Enterprise apps | At promotion + on action change | "Actions the agent can invoke" | Each connector tagged with DLP business-data-group classification (Control 1.5) |
| **Plugins / Connected Apps** | list (name + Entra appId where applicable) | All zones | Plane 1 Extensions + Plane 6 Connected apps + Plane 3 App registrations | At promotion + on plugin change | "Plugins / extensions / connected apps" | Each entry mapped to Entra appId where applicable |
| **Foundation Model / Runtime** | string {GPT-4o, GPT-4.1, GPT-5, o-series, Phi, Anthropic via Bedrock-equivalent, customer BYO Foundry deployment, etc.} | Zone 2 + Zone 3 | Copilot Studio model picker / Foundry deployment ID | At promotion + on model swap | "Foundation model in use" | Triggers re-validation under Control 2.5 on change |
| **Effective Sensitivity Label** | string (highest label across grounding sources) | Zone 2 + Zone 3 | §9 verification procedure | At promotion + at each attestation | "Inherited sensitivity posture" | If grounding sources include Highly Confidential / NPI / MNPI, agent must be Zone 3 |
| **DLP Policy Mapping** | URL / policy name | All zones | §8 verification procedure (Purview DLP for M365 Copilot + Power Platform data policies) | At promotion + on policy change | "Linked DLP policy" | Non-null Zone 3; documented exception otherwise |
| **Sovereign Cloud Boundary** | enum {Commercial, GCC, GCC High, DoD, Gallatin} + multi-region annotation | All zones | Tenant determination (per Control 4.7) | At promotion + on tenant move | "Cloud boundary" | Must match tenant's actual cloud; flagged at attestation if mismatch |
| **Environment / Tenant / Region** | string (Power Platform environment ID + tenant ID + Azure region) | All zones | Plane 2 + Plane 3 | At promotion + on environment change | "Hosting environment" | Reconciled to Control 2.1 environment list |
| **Enterprise App / Service Principal ID** | GUID | Zone 2 + Zone 3 (where Entra-backed) | Plane 3 | Real-time | "Entra service principal" | Non-null where the agent is Entra-backed; cross-join key |
| **Audit-Log Reference** | string (UAL operation prefix + Sentinel rule reference) | Zone 2 + Zone 3 | Control 1.7 + Control 3.9 mapping | At promotion | "Audit pipeline binding" | Non-null Zone 3 |
| **Risk Register Reference** | URL | Zone 2 + Zone 3 | Control 1.2 risk register | At promotion + quarterly | "Risk register entry" | Non-null Zone 3 |
| **Validation Evidence Pack** | URL | Zone 2 + Zone 3 | Control 2.5 evidence pack | At promotion + on material change | "Validation evidence pack" | Non-null Zone 3 |
| **Incident History** | list of incident IDs | Zone 2 + Zone 3 | Control 3.4 incident records | On incident closure | "Linked incidents" | Reconciled at quarterly attestation |
| **Decommission Date** | date (nullable) | All zones (when applicable) | Register list | On Decommission transition | "Retirement date" | Non-null only when state = Decommissioned |
| **Exception Reference** | URL (nullable) | All zones (when applicable) | GRC tool / Compliance Officer log | On exception grant | "Approved exception" | Required when any field's validation rule is waived |
| **Evidence Reference / Export Hash** | string (SHA-256) + URL | Zone 2 + Zone 3 | PowerShell hashing per `powershell-setup.md` | At each attestation | "Evidence pack ID + hash" | Non-null Zone 3; tamper-evident |

> **Schema contract notice:** This schema is the contract that Controls 3.2, 3.4, 3.6, 3.8, 3.9, 3.11, and 3.13 consume. Any field added or removed here requires sign-off by the AI Governance Lead and a coordinated update across consuming controls. Versioned schema definitions are stored in the register-of-record SharePoint library under `/_schema/3.1-canonical-schema-v{n}.json`.

### 1.3 Propagation and refresh latency

Operators must understand how long a portal-side change takes to surface in the next plane's view. Quarterly stitching that runs immediately after a bulk owner change will surface false-positive orphans.

| Change | Typical propagation | Worst case observed | Validation step |
|---|---|---|---|
| New Copilot Studio agent published → Plane 2 visibility | < 15 minutes | 1 hour | Refresh PPAC Resources view |
| New Copilot Studio agent published → Plane 1 visibility (when published to M365 Copilot) | 1–4 hours | 24 hours | Re-open Copilot Hub Inventory |
| Agent deletion in PPAC → removal from Plane 2 | Immediate visual; ledger row may persist | 48 hours | Confirm via the legacy Maker Inventory |
| Owner change in Entra (UPN updated, manager-of-record updated) → Plane 1 / Plane 2 owner column | 1–24 hours | 48 hours | Re-open agent detail page |
| License strip / user soft-delete → orphan signal in Plane 1 / Plane 2 | 1–4 hours | 24 hours | PPAC `Owner = System Account` filter |
| Entra Enterprise apps refresh (new app installed) | Minutes | 1 hour | Refresh app list |
| Agent Registry (preview) refresh | Hours | Verify | Re-open blade |
| Agent 365 (preview) refresh | Hours | Verify | Re-open blade |
| Purview retention policy publish → SharePoint library binding | 1–24 hours | 48 hours | Confirm In-place hold indicator on a library item |
| SharePoint Connected apps inventory update | Hours | 24 hours | Refresh SP admin Connected apps view |
| DAG report re-computation | Daily by default | 7 days | Confirm last-run timestamp on the report card |

!!! warning "Pilot soak time"
    Allow **at least 24 hours between any owner change and quarterly stitching** to avoid stale-state false positives. For tenant-wide owner-bulk events (e.g., reorganization, M&A integration), allow 72 hours soak before treating any orphan signal as actionable.

### 1.4 The "shadow AI" callout

The most common FSI inventory failure is **agents created in the personal-productivity Default environment that never enter the register**. They are visible only via the PPAC Maker Inventory **and** the Entra Enterprise apps blade — they will not appear in the M365 Copilot Hub Agents tab if they were never published to M365 Copilot.

- **Pre-attestation requirement:** the §11 procedure **must** stitch all six planes; running attestation off Copilot Hub alone will undercount.
- **Cross-link** to [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) (Default environment governance) and [Control 3.6 — Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) (shadow-agent intake workflow).

### 1.5 Sovereign-cloud determination memo

Before any baseline build, the AI Governance Lead and CISO sign a one-page memo documenting:

1. The tenant's primary sovereign cloud (Commercial / GCC / GCC High / DoD / Gallatin).
2. Multi-geo or multi-region annotation if applicable.
3. The list of surfaces (per the §1.1 table) that are **not GA in this cloud** as of the memo date.
4. The compensating control adopted for each gap (e.g., manual screenshot evidence for Plane 6 in DoD; quarterly Defender for Cloud Apps cross-check while Agent 365 is preview).

The memo is filed in the register-of-record library under `/_governance/3.1-sovereign-cloud-determination-{YYYY-MM}.pdf` and re-signed annually.

---

## §2. Pre-flight gates

Five gates must be signed off before opening any portal in §3 onward. Each gate is a checklist the operator countersigns. Failure of any gate halts the baseline build and is logged as a Sev-2 governance finding under [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md).

### 2.1 Gate PRE-01 — License gate

Confirm and document each licensing floor:

- [ ] **Microsoft 365 Copilot** — at least one E3/E5 + Copilot license is active in the tenant; the `Copilot` node appears in `admin.microsoft.com`. (Verify via `admin.microsoft.com → Billing → Licenses`.)
- [ ] **Power Platform Managed Environments** — at least one Managed Environment is configured (verify in `admin.powerplatform.microsoft.com → Manage → Environments`, filter `Managed = Yes`).
- [ ] **Entra ID P1 (P2 recommended)** — verify in `entra.microsoft.com → Identity → Overview → Licenses`.
- [ ] **Purview Audit (Standard or Premium)** — verify the Audit solution is provisioned in `purview.microsoft.com`.
- [ ] **Purview Records Management** — verify the Records management solution is enabled if Preservation Lock will be used on the register library.
- [ ] **Microsoft Sentinel** — verify the AI content hub solution is installed (Control 3.9 dependency).
- [ ] **Agent 365** — entitlement verified or marked "preview not entitled" in the §1.5 sovereign-cloud determination memo.
- [ ] **SharePoint Premium** — verified or marked "compensating screenshot evidence" in the memo.

**Sign-off:** Compliance Officer countersigns the license-gate checklist; archive as `3.1-PRE-01-license-gate-{YYYY-MM-DD}.pdf`.

### 2.2 Gate PRE-02 — Role gate

Use only the framework's canonical role names from `docs/reference/role-catalog.md`. Do **not** revert to long-form Microsoft titles in the WSP, the attestation memo, or the examiner cover letter.

| Role | Tenant scope | Surface coverage | PIM posture |
|---|---|---|---|
| **AI Governance Lead** | Owns the register of record | All six planes (read across) | Standing |
| **AI Administrator** | M365 Copilot Hub Inventory authoring | Plane 1 | Standing read; PIM for write |
| **Power Platform Admin** | PPAC Resources → Copilot agents; Maker Inventory | Plane 2 | PIM-elevated for environment-scoped writes |
| **Entra Global Reader** | Enterprise apps + Agent Registry read | Plane 3 | Standing |
| **Entra App Admin** | App registrations write (rare) | Plane 3 | PIM-only |
| **Entra Agent ID Admin** | Agent Registry blade (preview) write | Plane 3 / Plane 4 boundary | PIM-only |
| **Agent 365 Admin** | Agent 365 Admin Center | Plane 4 | PIM-only (preview surface) |
| **Purview Compliance Admin** | Retention / Records Management linkage | Plane 5 | Standing |
| **Purview Records Manager** | Preservation Lock for register library (Control 1.9 handoff) | Plane 5 | Standing |
| **SharePoint Admin** | Connected apps inventory + DAG | Plane 6 | Standing |
| **Compliance Officer** | Quarterly attestation third signer; examiner-pull approver | Cross-surface | Standing |
| **Designated Supervisor / Registered Principal** | FINRA Rule 3110 supervisory sign-off on examiner pull | Cross-surface | Named per WSP |
| **CISO observer** | Sovereign-cloud determination; sign-off on shadow-AI register | Tenant-wide | Standing |

**Separation-of-duties rule:** A single human MUST NOT hold both **Owner** of an agent and **AI Governance Lead** sign-off on the attestation for that agent — collapsing those roles undermines the FINRA 3110 supervisory-independence defense and the FINRA 25-07 governance posture.

**Sign-off:** AI Governance Lead countersigns `3.1-PRE-02-role-gate-{YYYY-MM-DD}.pdf`.

### 2.3 Gate PRE-03 — Tenant settings gate

Confirm pre-existing controls that the register depends on:

- [ ] **Control 1.7 Unified Audit Log** is enabled and capturing `AgentCreate`, `AgentUpdate`, `AgentDelete`, `OwnerChanged`, and SharePoint list `Update` operations on the register library.
- [ ] **Control 1.7 Advanced Audit retention** for Zone 3 (≥ 1 year) is configured (Premium SKU).
- [ ] **Control 1.13 Sensitivity labels** are published to all in-scope sites (drives Data Classification inheritance check in §9).
- [ ] **Control 1.9 Retention policies** authored and reconciled with the Records Manager for register-export Preservation Lock.
- [ ] **Control 2.1 Managed Environments** enabled (drives Zone classification reconciliation).
- [ ] **Control 4.6 Grounding-source inventory** current (joins on AgentID at §9).
- [ ] **Control 1.2 Risk register** active (joins on AgentID).
- [ ] **Control 3.9 Sentinel content hub for AI** installed (register-deviation alerts).

**Sign-off:** AI Governance Lead + Entra Global Reader cross-confirm; archive as `3.1-PRE-03-tenant-settings-{YYYY-MM-DD}.pdf`.

### 2.4 Gate PRE-04 — WSP / change-control gate

The Written Supervisory Procedures (WSP) must include the following elements before the baseline build is considered authoritative:

- Register-of-record location, owner, and retention horizon (≥ 6 years per SEC 17a-4(b)(4); longer if firm policy requires).
- Quarterly attestation cadence and three-signature workflow (§11).
- Lifecycle state-transition approval matrix (who can move Draft → In Review → Approved → Active → Deprecated → Decommissioned).
- Orphan-remediation SLA: Zone 3 = 5 business days; Zone 2 = 10 business days; Zone 1 = 30 business days.
- Examiner audit-pull SLA: target ≤ 5 business days for FINRA 8210; ≤ 30 calendar days for OCC; ≤ 24 hours for ad-hoc supervisory request.
- Sovereign-cloud determination procedure (per agent, per environment).
- Shadow-AI handling procedure: discovered agent placed in Draft state with Owner assigned within 5 business days, otherwise transitioned to Decommissioned.

**Sign-off:** Compliance Officer + Designated Supervisor; archive as `3.1-PRE-04-wsp-excerpt-{YYYY-MM-DD}.pdf`.

### 2.5 Gate PRE-05 — Test fixtures gate

Before walking through §3 in production, validate the procedure in a sandbox or non-prod tenant:

- Sandbox tenant or non-prod environment available with at least one Managed Environment.
- Test agent in each Zone (1, 2, 3) with full canonical metadata populated.
- **Canary agent** with traceable naming pattern `FSI-CANARY-3.1-{YYYYMMQ}-{n}` for round-trip verification through the register.
- Test "departed-owner" account (license-stripped, soft-deleted Graph user) for the §6 orphan-detection drill.

**Sign-off:** AI Administrator + Power Platform Admin; archive as `3.1-PRE-05-test-fixtures-{YYYY-MM-DD}.pdf`.

---

## §3. Plane 1 — Microsoft 365 Copilot Hub Inventory walkthrough

This is the primary first-party governance surface for organization-wide Copilot agents. Refresh cadence is on-demand at portal navigation; some columns (License consumption, Last activity) lag the underlying telemetry.

### 3.1 Open the Copilot Hub Inventory

1. Sign in to `https://admin.microsoft.com` as **AI Administrator** (or **Entra Global Reader** for read-only review).
2. In the left navigation, expand **Copilot**. If the **Copilot** node is not present:
   - Verify the Microsoft 365 Copilot SKU is licensed in the tenant (Gate PRE-01).
   - Verify the operator holds at least **AI Administrator** or **Entra Global Reader**.
   - In sovereign clouds where the node label differs, look for **AI agents** or **Copilot agents** as alternate labels.
3. Click **Inventory** (label may read **Agent inventory** or **Copilot agent inventory** depending on monthly build — verify exact heading at deploy time and capture in the §13 evidence pack).
4. Confirm the page header reads as expected. *Screenshot description: M365 admin center top breadcrumb showing `Home > Copilot > Inventory`, with the page heading "Copilot agent inventory" and three tabs labeled "Agents", "Declarative agents", and "Extensions" visible at the top of the content area.*

!!! tip "Legacy navigation note"
    The older path **Settings → Integrated apps → Agents** is **legacy** as of April 2026. Operators may still see it during a tenant rollout window; treat it as a compatibility fallback only and migrate to **Copilot → Inventory** as soon as the new node appears.

### 3.2 The Agents tab

The Agents tab enumerates Custom Copilot agents (Studio-published), tenant-installed agents, and Microsoft-provided agents that have been enabled.

1. Click the **Agents** tab (or **All agents** depending on build).
2. Click the **column picker** (gear icon top-right of the grid) and enable at minimum:
   - **Name**
   - **Owner**
   - **Type** (Custom / Declarative / Extension)
   - **Source** (Copilot Studio / Agent Builder / Marketplace)
   - **Created date**
   - **Modified date**
   - **Status** (Published / Draft / Disabled)
   - **Environment** (Power Platform environment binding)
   - **Sovereign cloud** (where exposed)
   - **Risks** (where exposed — flags ownerless, departed-owner, license-stripped)
   - **License consumption** (preview as of April 2026 — verify availability in your build)
   - **Last activity** (preview as of April 2026)
3. Sort by **Modified date** descending to surface recent activity.
4. For each Zone 3 agent in the grid, click into the agent row → confirm the metadata side-panel exposes:
   - **Owner** (with hover tooltip showing UPN)
   - **Description** (maps to canonical **Business Justification**)
   - **Knowledge sources** (maps to canonical **Connected Knowledge Sources**)
   - **Actions** (maps to canonical **Connected Actions / Connectors**)
   - **Plugins** (maps to canonical **Plugins / Connected Apps**)
5. *Screenshot description: Agents tab grid view with all canonical-schema columns visible, the Risks column showing one "Ownerless" red badge and two "Owner inactive" amber badges, and the side-panel open on a Zone 3 agent revealing Knowledge sources listing two SharePoint sites and one Dataverse table, Actions listing three connectors with their OAuth posture, and the Owner field showing the displayName + UPN.*

**Evidence capture:** Screenshot the Agents tab with all canonical-schema columns visible. Save as `3.1-Plane1-Agents-{YYYY-MM-DD}.png` in the register-of-record SharePoint library under `/_evidence/{YYYY-Qn}/`.

### 3.3 The Declarative agents tab

Declarative agents are manifest-authored (Copilot Studio Lite, Agents Toolkit, Copilot Studio declarative-agent path). They are the most likely surface for partner-published or developer-side agents.

1. Click the **Declarative agents** tab.
2. Enable columns: **Name, Owner, Manifest version, Capabilities (Knowledge / Actions / Code Interpreter), Last published, Source**.
3. For each row, capture the **manifest provenance** — the manifest is the source of truth for plugins/connected apps; the register mirrors but does not author the manifest.
4. *Screenshot description: Declarative agents tab grid with eight rows visible, columns showing Manifest version (e.g., "1.4"), Capabilities cells with chips for "Knowledge" and "Actions", and a side-panel open on one agent showing the manifest JSON snippet with the plugin Entra appId highlighted for the §5 cross-check.*

**Evidence capture:** `3.1-Plane1-Declarative-{YYYY-MM-DD}.png` plus CSV export per §3.6.

### 3.4 The Extensions tab

Microsoft 365 Copilot extensions (formerly "plugins") include message extensions, Graph connectors, and API plugins. Each entry maps to an Entra App ID — capture the App ID for the §5 Entra cross-check.

1. Click the **Extensions** tab (or **Connectors** depending on build).
2. Enable columns: **Name, Publisher, Type (Message extension / Graph connector / API plugin), Entra App ID, Permissions, Status, Owner**.
3. For each Zone 3 extension, click the row → side-panel shows the OAuth permission scopes (delegated vs application) and the consent state.
4. *Screenshot description: Extensions tab showing twelve extensions, three flagged with "Admin consent required" amber badges, and the side-panel open on a Graph connector revealing the App ID `00000003-0000-0000-c000-000000000000`-style GUID copyable to clipboard.*

**Evidence capture:** `3.1-Plane1-Extensions-{YYYY-MM-DD}.png` and CSV.

### 3.5 Filters, views, and the Risks column

The Copilot Hub provides governance filters that drive the §6 orphan workflow:

| Filter | Value | What it surfaces |
|---|---|---|
| **Status** | `Published` | Active agents — count for Zone-classification reconciliation |
| **Status** | `Disabled` | Deprecated candidates that may need state transition to Decommissioned |
| **Owner** | `(any user filter)` | Per-owner enumeration for departed-owner detection |
| **Risks** | `Ownerless` | Surface for the **Manage Ownerless** action (see below) |
| **Risks** | `Owner inactive` | Departed-owner candidates — feed §6 orphan workflow |
| **Type** | `Declarative` | Cross-check against manifest source-of-truth |
| **Sovereign cloud** | (current cloud) | Confirm no agents are mis-tagged across cloud boundary |

**Save filtered views per Zone** for the quarterly attestation. Click **Save view** at the top of the grid; name as `3.1-Z{n}-attestation-{YYYY-Qn}`.

**Manage Ownerless action:** When the Risks column shows one or more **Ownerless** badges, the toolbar exposes a **Manage Ownerless** button. Click it to open the ownerless-agent dialog:

1. Select agents to remediate.
2. Choose: **Assign Owner** (UPN picker — must be a named human, not a group) or **Disable** (transitions the agent to a non-published state pending decision).
3. The action is logged in the Unified Audit Log as `OwnerChanged` with the operator's UPN — capture this entry in the §11 attestation evidence.
4. *Screenshot description: "Manage ownerless agents" dialog overlay showing four agents with checkboxes, an "Assign Owner" picker with autocomplete, and a "Disable" option below; the dialog footer shows "Action will be logged" with a tooltip "This action is recorded to the Unified Audit Log as OwnerChanged".*

### 3.6 Bulk export from Plane 1

1. With the desired filter applied (or no filter for full export), click **Export** (top-right; label may read **Export to CSV**).
2. Confirm the export contains all visible columns. If the export omits columns visible in the grid, document the omission in the §13 evidence pack and capture additional screenshots as compensating evidence.
3. Save the file with the naming convention: `3.1-Plane1-Export-{YYYY-MM-DD}-{cloud}.csv` (e.g., `3.1-Plane1-Export-2026-04-15-Commercial.csv`).
4. Compute SHA-256 immediately (one-liner):
   ```powershell
   Get-FileHash -Algorithm SHA256 .\3.1-Plane1-Export-2026-04-15-Commercial.csv
   ```
5. Record the hash in the §13 evidence manifest. Defer recurring scheduled exports to [PowerShell Setup](powershell-setup.md).
6. Upload the export to the register-of-record SharePoint library under `/_evidence/{YYYY-Qn}/`. The library must already be bound to a Purview retention policy per Gate PRE-03.

### 3.7 What this surface does NOT show

Mandatory operator awareness — Plane 1 alone undercounts the register:

- Agents in non-Default environments **created via Copilot Studio but never published** to M365 Copilot.
- Agents in the Power Platform Default environment that have not been promoted to a Managed Environment.
- **Custom Engine Agents (CEAs)** hosted in Azure that authenticate via Entra App Registration only.
- Agent Builder–authored agents pending publish.
- Third-party agents enrolled via Entra Workload Identity Federation (visible only in Plane 3 / Plane 4).

These gaps are filled by §4 (Plane 2) and §5 (Plane 3). Do **not** treat Plane 1 alone as the register.

---

## §4. Plane 2 — Power Platform Admin Center: Resources → Copilot agents (and the legacy Maker Inventory)

This is the **authoritative surface for Copilot Studio agents** and the only surface that exposes environment-scoped governance attributes. The PPAC display is capped at approximately 500 agents; tenants exceeding that threshold must use the [PowerShell Setup](powershell-setup.md) Azure Resource Graph procedure for full enumeration.

### 4.1 Open Resources → Copilot agents

1. Sign in to `https://admin.powerplatform.microsoft.com` as **Power Platform Admin** (PIM-elevated).
2. In the left navigation, expand **Resources**.
3. Click **Copilot agents**.
4. The grid loads with the tenant-scoped Copilot Studio agent list. Confirm the breadcrumb reads `Resources > Copilot agents`. *Screenshot description: PPAC left rail expanded to Resources > Copilot agents; the grid shows columns Name, Owner, Environment, Status, Created, Modified, with twelve agents visible and a "Filter" pill row above showing the current filter set.*

### 4.2 Configure columns

Click **Choose columns** and enable at minimum:

- **Name** / **Display name**
- **Owner** (UPN)
- **Environment** (joins to Control 2.1 environment list — drives Zone classification reconciliation)
- **Status** (Published / Draft / Disabled)
- **Type** (Custom Copilot / Declarative / Connected)
- **Authentication** (No auth / Microsoft / Manual / Custom — drives Plane 3 cross-check)
- **Channels** (Teams / Web / Custom — drives examiner-facing exposure surface mapping)
- **Created on** + **Modified on**
- **botId** / **Bot ID** (canonical AgentID join key for Plane 2 → Plane 3 stitching)
- **Solution** (the Power Platform solution containing the agent — joins to ALM evidence)

### 4.3 Filter, sort, and per-environment pivot

| Filter | Operational use |
|---|---|
| **Environment = Default** | Surface candidate shadow agents — every row here is a §11 review item |
| **Owner contains `(System Account)` or `# (deleted)`** | Departed-owner orphan signal — feed §6 orphan workflow |
| **Status = Disabled** + **Modified on < 90 days ago** | Recent disablement — possible candidate for state transition to Decommissioned |
| **Authentication = No auth** + **Channels contains `Web`** | High-risk public-facing agent — Zone-classification escalation candidate |

Save per-environment views named `3.1-Plane2-Env-{environment-name}-{YYYY-Qn}` for the §11 attestation pack.

### 4.4 Per-agent metadata side panel

Click into a row to open the agent details. Capture for each Zone 3 agent:

- **Owner** (must reconcile with Plane 1 owner if also published to M365 Copilot).
- **Environment** (must reconcile with Control 2.1 Managed-Environment classification).
- **Knowledge sources** (must reconcile with Plane 6 SharePoint Connected apps and Control 4.6 grounding inventory).
- **Topics / Actions** (each connector mapped to its DLP business-data-group classification per Control 1.5).
- **Authentication mode** (joins to Plane 3 Entra service principal where Microsoft auth is used).
- **Solution** (joins to ALM evidence per Control 2.7).

*Screenshot description: PPAC Copilot agent details blade for a Zone 3 customer-service agent; the Knowledge sources section lists three SharePoint URLs with "Inherited sensitivity: Confidential" badges; the Actions section lists five connectors with green "DLP Business" or amber "DLP Non-Business" pills; the Authentication section reads "Microsoft" with the Entra App ID copyable.*

### 4.5 The legacy Maker Inventory (Manage → Inventory)

The legacy **Manage → Inventory** view remains the most reliable surface for **departed-owner cross-check** because it surfaces the System Account ownership transition and the per-environment ledger. Use it in addition to (not instead of) **Resources → Copilot agents**.

1. In PPAC, navigate to **Manage → Inventory**.
2. In the **Item type** filter, select **Agent** (or **Bot** depending on build label — verify in your tenant).
3. The grid surfaces the per-environment, per-item ledger. Filter columns:
   - **Owner = System Account** → license-stripped or deleted owner
   - **Owner contains `# (deleted)`** → soft-deleted Graph user
   - **Last modified < threshold** → dormant candidates
4. Export to CSV via the toolbar **Export** action.
5. *Screenshot description: PPAC Manage > Inventory grid filtered to Item type = Agent and Owner = System Account, showing four rows highlighted amber, with the Owner column reading "System Account" and the Environment column showing one Default-environment row that the operator should escalate to a §11 review item.*

**Evidence capture:** `3.1-Plane2-MakerInventory-{YYYY-MM-DD}.csv` and screenshot.

### 4.6 Bulk export from Plane 2

1. From **Resources → Copilot agents**, click **Export to CSV** in the toolbar.
2. PPAC export caps at ~500 rows in the UI. **If the tenant exceeds 500 Copilot Studio agents, do not rely on the UI export** — switch to [PowerShell Setup](powershell-setup.md) (Azure Resource Graph + Power Platform admin connectors).
3. Save as `3.1-Plane2-Export-{YYYY-MM-DD}.csv`. Compute SHA-256 and record in the evidence manifest.

### 4.7 What this surface does NOT show

- M365 Copilot extensions / Graph connectors (Plane 1).
- Entra-registered service principals for Custom Engine Agents that are not Power Platform–hosted (Plane 3).
- SharePoint-grounded site exposure (Plane 6).
- Agent telemetry beyond the activity timestamp (Control 3.9 / Sentinel).

---

## §5. Plane 3 — Microsoft Entra: Enterprise applications + Agent Registry blade + App registrations

The Entra plane is the **identity authoritative source** for any agent that holds an Entra service principal — declarative agents with plugins, Custom Engine Agents, M365 Copilot extensions backed by an Entra App, and any third-party agent installed via Entra App Gallery.

### 5.1 Enterprise applications view

1. Sign in to `https://entra.microsoft.com` as **Entra Global Reader** (read) or **Entra Cloud Application Admin** (PIM-elevated for write).
2. Navigate to **Identity → Applications → Enterprise applications**.
3. Set **Application type = All applications** and **Application status = Any**.
4. Apply filter: **Application visibility = Hidden** *or* **All** (some agent-class apps register hidden).
5. Use the search field with the agent name pattern from your WSP. For broad sweep, filter by **Created date** to surface recent installs.
6. *Screenshot description: Entra Enterprise applications list filtered to Application type = All applications, showing a search bar populated with `Copilot` returning 47 hits; columns visible include Name, Object ID, Application ID, Homepage URL, Created date, Sign-in date.*

### 5.2 Per-app deep dive

Click into a Zone 3 agent's enterprise app entry and capture:

- **Application ID** (the canonical Entra `appId` — primary join key for Plane 3 stitching).
- **Object ID** (service principal object ID).
- **Owners** (named human owners of the app — reconcile with the agent's canonical Owner).
- **Permissions → Configured permissions** — list every Graph and connector permission scope, classify each as delegated or application; flag any application-level permission for the §11 review.
- **Sign-in logs** (last sign-in timestamp — joins to Plane 4 / Sentinel for activity reconciliation; informational only — authoritative activity reporting lives in Control 3.9).
- **Properties → Assignment required** — must be `Yes` for any Zone 3 agent unless an explicit exception is filed.
- **Properties → Visible to users** — set per WSP.

*Screenshot description: Enterprise app overview blade for a Custom Engine Agent showing Application ID and Object ID GUID values; the Permissions section reveals two delegated Graph scopes (Files.Read, Sites.Read.All) and one application scope (Sites.Selected) flagged with a red "Application permission" badge that must be reviewed at §11.*

### 5.3 The Agent Registry blade (preview, April 2026)

The Agent Registry is the emerging Entra surface that promotes Entra App Registrations into a first-class **Agent ID** taxonomy. Treat as **additive evidence** while preview; do not retire Plane 1 / Plane 2 procedures based on it.

1. In `entra.microsoft.com`, navigate to **Identity → Applications → Agent Registry** (preview — verify exact label at deploy time; sovereign-cloud parity not assured).
2. The blade enumerates apps that the tenant administrator has classified as **Agent** type.
3. Capture the agent ID, classification, owners, and any agent-specific governance attributes (Risk band, Sovereign cloud binding) the blade exposes in your build.
4. Cross-reference each Agent Registry entry with the Enterprise apps view to confirm no agent-classified app is missing the canonical Owner field.
5. *Screenshot description: Agent Registry preview blade showing ten classified agents with columns Agent ID, Display name, Classification, Owners, Risk band; the toolbar exposes a "Promote from Enterprise apps" action and a "Demote" action with PIM elevation banner at the top.*

!!! warning "Preview status"
    The Agent Registry is **preview** as of April 2026 with rolling sovereign-cloud availability. Maintain the §1.5 sovereign-cloud determination memo entry stating whether your tenant treats this surface as authoritative or as additive cross-check evidence.

### 5.4 App registrations (developer-side)

App registrations surface developer-authored declarative agents and Custom Engine Agents pre-publish.

1. Navigate to **Identity → Applications → App registrations**.
2. Filter by **Created date** and your firm's app-naming convention.
3. For each agent-class app registration, capture: **Application (client) ID**, **Object ID**, **Supported account types**, **Redirect URIs**, **API permissions**, **Owners**.
4. Reconcile every developer-side registration with the Enterprise apps tenant view (the tenant install creates the matching Service Principal). Any app registration without a corresponding Enterprise app entry is a pre-publish or ungoverned object — feed to §11 review.

### 5.5 Bulk export from Plane 3

1. From Enterprise applications, click **Download (Export)** in the toolbar (top right). The export covers the visible columns only; ensure the column picker includes Application ID, Object ID, Created date, and Last sign-in.
2. Save as `3.1-Plane3-EnterpriseApps-{YYYY-MM-DD}.csv`.
3. From App registrations, the portal does not provide a bulk-export button as of April 2026 — switch to [PowerShell Setup](powershell-setup.md) (`Get-MgApplication`).
4. Compute SHA-256 and record in evidence manifest.

### 5.6 What this surface does NOT show

- Power Platform environment binding (Plane 2).
- M365 Copilot Hub agent classification (Plane 1).
- Grounding-source exposure (Plane 6 / Control 4.6).
- Cross-cloud agent telemetry (Plane 4).

---

## §6. Plane 4 — Agent 365 Admin Center (preview)

Agent 365 is the cross-cloud agent observability surface rolling to GA across calendar 2026. **Verify availability and entitlement at deploy time.** Treat as additive cross-check evidence while in preview; treat as a primary surface only after GA in your sovereign cloud and after the §1.5 memo is updated.

### 6.1 Open Agent 365

1. Navigate to `https://admin.agent365.microsoft.com` (preview hostname — verify with Microsoft Learn at deploy time; the hostname has changed during preview).
2. Sign in as **Agent 365 Admin** (PIM-elevated).
3. If the tenant is not entitled, the portal returns a "not provisioned" page — capture screenshot, file under `/_governance/3.1-agent365-not-entitled-{YYYY-MM-DD}.png`, and document the compensating control in the §1.5 memo.

### 6.2 Cross-cloud agent inventory

Where entitled, the Agent 365 Admin Center exposes:

- A consolidated agent list spanning Microsoft 365 Copilot, Copilot Studio, Custom Engine Agents, and (where rolled out) third-party agent integrations.
- **Governance cards** per agent surfacing Owner, Sensitivity, Risk band, Last activity.
- An **Ownerless agents** queue analogous to the Manage Ownerless action in Plane 1 — drives the §6 orphan workflow.
- Cross-tenant agent visibility for B2B-collaborated agents (where tenant has B2B agent invitations enabled).

### 6.3 Sovereign-cloud caveat

Agent 365 is **likely not GA in GCC High, DoD, or Gallatin at first GA**. For sovereign-cloud tenants:

- File the determination memo entry stating Plane 4 is **not in scope** for this attestation cycle.
- Use the compensating quarterly cross-check via Microsoft Defender for Cloud Apps → App Governance (where licensed) plus the §5 Entra Enterprise apps export.
- Re-evaluate scope at every Microsoft Roadmap update; transition Plane 4 into scope only after GA-in-cloud is confirmed and the §1.5 memo is re-signed by the AI Governance Lead and CISO.

### 6.4 Evidence capture from Plane 4

If entitled, export the cross-cloud agent list and ownerless queue. Save as `3.1-Plane4-AgentList-{YYYY-MM-DD}.csv` and `3.1-Plane4-Ownerless-{YYYY-MM-DD}.csv`. Compute SHA-256.

If not entitled, the screenshot evidence of the entitlement-denied page plus the determination-memo entry is the compensating artifact. Both must be present in the §13 evidence pack for any quarter where Plane 4 is referenced in WSP.

---

## §7. The manual stitching procedure (Plane 1 + 2 + 3 + 4 → register of record)

The register of record lives in a **SharePoint list** (or Dataverse table, where the firm prefers) under the AI Governance Lead's ownership. The stitching procedure converts the per-plane exports into a single canonical-schema row per agent. This procedure is the contract that defines "the inventory" for examiner purposes.

### 7.1 Prerequisites

- Per-plane exports captured per §3.6, §4.6, §5.5, §6.4.
- All exports SHA-256 hashed and timestamped.
- Register-of-record SharePoint list provisioned per the §1.2 schema and bound to a Purview retention policy per Gate PRE-03.
- Stitching workbook template under version control (the template is owned by the AI Governance Lead; changes follow Control 1.2 change-control).

### 7.2 The join keys

| Join | Primary key | Fallback keys |
|---|---|---|
| Plane 1 ↔ Plane 2 | Plane 1 `agentId` ↔ Plane 2 `botId` (where M365-published) | Display Name + Owner UPN + Environment |
| Plane 2 ↔ Plane 3 | Plane 2 `Microsoft auth → App ID` ↔ Plane 3 `appId` | Display Name + Owner UPN |
| Plane 3 ↔ Plane 4 | Plane 3 `appId` ↔ Plane 4 `agentId` | Display Name + Owner UPN |
| Any ↔ Plane 6 | Connected Knowledge Sources URL list ↔ Plane 6 site URL | Site display name |
| Any ↔ Control 4.6 grounding inventory | Connected Knowledge Sources URL ↔ grounding-source URL | Site URL |

### 7.3 Stitching steps

1. Open the stitching workbook (Excel or Power BI desktop file under version control).
2. Load each plane's export as a separate query.
3. Apply the join keys per §7.2 to produce a single canonical-schema row per agent.
4. Where multiple planes disagree (e.g., Plane 1 owner = `alice@`, Plane 2 owner = `bob@`), flag the row with **Owner-mismatch** and route to §11 review. **Do not silently pick a winner.**
5. Where an agent appears in only one plane (e.g., Plane 2 only), flag with **Single-plane** and route to §11 review.
6. Where an agent has been newly created since last stitching, flag with **New** and confirm Owner + Zone + Lifecycle State are populated before promoting to the register.
7. Where an agent appeared in last stitching but is missing from this stitching, flag with **Disappeared** and route to §6 orphan workflow before transitioning to Decommissioned.
8. Save the stitched output as `3.1-Register-{YYYY-MM-DD}.xlsx` and `3.1-Register-{YYYY-MM-DD}.csv`. Compute SHA-256 of both. Upload to the register-of-record library.
9. The AI Governance Lead reviews and signs the stitched register; signature is a SharePoint list item update with the AI Governance Lead's UPN and the timestamp captured in the Unified Audit Log.
10. Once signed, the SharePoint list is the authoritative register; downstream controls (3.2, 3.4, 3.6, 3.8, 3.9, 3.11, 3.13) read from it on the canonical AgentID.

### 7.4 Stitching cadence

| Cadence | Trigger | Owner |
|---|---|---|
| **Quarterly** | Calendar-based, per WSP attestation cycle | AI Governance Lead |
| **Ad-hoc** | Examiner request, M&A integration, Sev-1 governance incident | AI Governance Lead |
| **Continuous (advisory)** | Sentinel detects register-deviation alert (Control 3.9) | AI Administrator triages within SLA |

### 7.5 What to do when a row will not stitch

- **Owner-mismatch:** Open a Plane 1 / Plane 2 / Plane 3 reconciliation ticket; the canonical Owner is decided by the AI Governance Lead with documentation in the ticket. Update all planes to converge on the canonical value within the orphan SLA.
- **Single-plane (Plane 2 only):** This is the shadow-AI signal. Open a Draft register entry, assign a tentative Owner (the Plane 2 ownership row), and run the §6 orphan/shadow workflow.
- **Disappeared:** Confirm via the Plane 2 Maker Inventory that the agent was not silently deleted by an unauthorized user. If deletion was authorized, transition the register row to Decommissioned with the deletion ticket reference. If unauthorized, escalate to Sev-2 governance incident under [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).
- **Plane 4 entitlement gap:** Note the gap in the stitching workbook and reference the §1.5 memo. Do not block the cycle on a non-GA preview surface.

---

## §8. Plane 5 — Microsoft Purview: retention and Records Management binding for the register library

The register-of-record SharePoint library MUST be bound to a Purview retention policy (and, for SEC 17a-4(f) WORM treatment, a Records Management Preservation Lock). This binding is what makes the register itself a record — without it, the register is operational data, not evidence.

### 8.1 Open Purview

1. Sign in to `https://purview.microsoft.com` as **Purview Compliance Admin** (read) or **Purview Records Manager** (write).
2. Navigate to **Solutions → Data lifecycle management** for retention; **Records management** for Preservation Lock.

### 8.2 Author / verify the retention policy

1. Under **Data lifecycle management → Policies**, confirm a policy exists named per WSP convention (e.g., `Retention - Pillar3 Register - 7yr`).
2. Confirm the policy is **scoped to the SharePoint sites** that host the register-of-record library (do not scope tenant-wide).
3. Confirm the retention period meets or exceeds 6 years (SEC 17a-4(b)(4) floor; Zone 3 firm policy may extend to 7 years).
4. Confirm the policy is **published** (not draft).
5. *Screenshot description: Purview retention policy details page showing Name "Retention - Pillar3 Register - 7yr", Locations restricted to two SharePoint site URLs, Retention period 7 years, Action at end of period "Do nothing", Status "On".*

### 8.3 Author / verify Preservation Lock (Records Management)

For tenants treating the register export as a SEC 17a-4(f)-format record:

1. Under **Records management → Retention labels**, confirm a label exists with **Records mark = Yes** (regulatory record) or **Records mark = Yes** with **Apply Preservation Lock = Yes**.
2. Apply (or auto-apply) the label to the register-of-record library.
3. Once Preservation Lock is applied, the policy is **immutable** (cannot be reduced in scope, cannot be deleted, cannot have retention period shortened). This is the WORM guarantee for SEC 17a-4(f).
4. *Screenshot description: Records management retention label details showing "Mark items as records" toggled on, "Apply Preservation Lock" toggled on with the warning banner "Preservation Lock cannot be turned off — this is irreversible", and the auto-apply policy showing it is bound to the register library URL.*

!!! danger "Preservation Lock is irreversible"
    Preservation Lock cannot be removed once applied. Verify the policy scope, retention period, and library binding **twice** before applying. Record the application event in the §13 evidence pack and obtain Compliance Officer countersignature in the WSP-approved evidence template.

### 8.4 Verify retention is binding

1. Navigate to the SharePoint register-of-record library.
2. Open a recent evidence file (e.g., a stitched register CSV).
3. Open file properties → **Compliance details**. Confirm the retention label is visible and shows the policy name and retention period.
4. *Screenshot description: SharePoint file Compliance details flyout showing Retention label "Pillar3 Register Record", Status "Applied via auto-apply policy", Retention period "7 years from creation", Records declaration "Yes — record (Preservation Lock)".*

### 8.5 Cross-link to Control 1.9

Records-Management procedure detail, retention-policy authoring, and Preservation Lock operational procedure live in [Control 1.9 — Records Management and Preservation Lock](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). This playbook only verifies the binding to the register library — it does not author records policy.

---

## §9. Plane 6 — SharePoint Admin: Connected apps and Data Access Governance

The SharePoint plane provides two distinct surfaces:

- **Connected apps** — the per-site registration of M365 Copilot extensions and Graph connectors (joins to Plane 1 Extensions tab).
- **Data Access Governance (DAG) report** — the tenant-wide report of sites with Copilot grounding scope, oversharing risk indicators, and last-activity timestamps.

### 9.1 Connected apps inventory

1. Sign in to the SharePoint Admin Center (`https://{tenant}-admin.sharepoint.com`) as **SharePoint Admin**.
2. Navigate to **Settings → Manage Connected apps** (label may vary by build; in newer builds, **Settings → Connected apps**).
3. The grid surfaces every Connected App registered against the tenant or against any site, with columns Name, Publisher, Type, Created date, Status.
4. For each entry, click into the row and confirm the **App ID** and **Permissions**. Cross-join to Plane 1 Extensions tab and Plane 3 Enterprise apps on the App ID.
5. *Screenshot description: SharePoint Admin Connected apps grid showing eight registered apps, three with "Tenant-wide" scope and five with site-scoped registrations; the side-panel open on a Graph connector revealing the Permissions list and the App ID copyable to clipboard.*

**Evidence capture:** `3.1-Plane6-ConnectedApps-{YYYY-MM-DD}.csv` (export via toolbar). If the export action is unavailable in your sovereign cloud, capture the screenshot as compensating evidence.

### 9.2 Data Access Governance report

1. In SharePoint Admin, navigate to **Reports → Data access governance**.
2. Locate the **Sites with Copilot grounding scope** report (label may vary). Click into it.
3. The report enumerates sites with at least one Copilot agent grounding on them, with oversharing-risk indicators and "Everyone except external users" (EEEU) and "People in your organization" link counts.
4. Each row joins to the Connected Knowledge Sources canonical-schema field on Site URL.
5. Export to CSV via the report toolbar. Save as `3.1-Plane6-DAG-{YYYY-MM-DD}.csv`.
6. *Screenshot description: DAG report card "Sites with Copilot grounding scope" showing twelve sites, three flagged with red "EEEU - Org wide" badges, the Last activity column populated, and the Export button visible at top right.*

!!! info "DAG and Control 4.6 / Control 4.7 boundary"
    The DAG report is the **discovery surface**. The grounding-source inventory and the oversharing-remediation procedure live in [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) and [Control 4.7](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md). This playbook only consumes the DAG output to populate the Connected Knowledge Sources field of the canonical schema.

### 9.3 Sensitivity-label inheritance check

For each Zone 2/3 register row:

1. From the canonical Connected Knowledge Sources list, take each grounding URL.
2. For SharePoint URLs, navigate to the site → **Settings → Site information → Site classification** (or the new **Information protection → Sensitivity** path) and capture the site sensitivity label.
3. For OneDrive URLs, navigate to the user's OneDrive root → confirm the container sensitivity label (or default to "no container label — file labels apply").
4. For Dataverse tables (Copilot Studio knowledge), capture the environment sensitivity label per Control 2.1.
5. Compute the **effective sensitivity** as the **highest label across all grounding sources**.
6. Update the canonical-schema **Effective Sensitivity Label** and **Data Classification** fields. **If any grounding source is Highly Confidential / NPI / MNPI, the agent's Zone classification must be 3** — escalate to §11 review for any mismatch.
7. *Screenshot description: SharePoint site information panel showing Sensitivity label "Confidential - FSI Internal Restricted" applied at site scope; below it the SharePoint label-policy banner reads "Inherited by all files and Copilot grounding".*

### 9.4 DLP-policy mapping verification

For each Zone 3 register row, verify the agent is in scope of at least one DLP policy:

1. **For Microsoft 365 Copilot agents (Plane 1):** Sign in to Purview → **Solutions → Data Loss Prevention → Policies**. For each policy, expand **Locations** and confirm whether **Microsoft 365 Copilot** is listed and whether the policy scope includes the agent's owners or the tenant.
2. **For Copilot Studio agents (Plane 2):** Sign in to PPAC → **Policies → Data Policies**. Confirm the agent's environment is in scope of the data policy and that the connectors used by the agent are correctly classified into Business / Non-Business / Blocked groups per [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).
3. Capture the policy name(s) and update the canonical-schema **DLP Policy Mapping** field for the register row.
4. **Cross-plane reconciliation:** an M365-published Copilot Studio agent (visible in both Plane 1 and Plane 2) must be in scope of **both** Purview DLP for M365 Copilot **and** the Power Platform data policy for its environment. A gap here is a §11 review item.
5. *Screenshot description: Purview DLP policy details showing Locations checkbox list with "Microsoft 365 Copilot" toggled on, Scope set to "All users", and Status "On"; alongside, the PPAC Data Policies blade showing the matching environment-scoped data policy.*

---

## §10. Lifecycle state transitions (the canonical state machine)

The canonical Lifecycle State lives in the register list, **not** in any source surface. State transitions follow this state machine:

```
Draft  →  In Review  →  Approved  →  Active  →  Deprecated  →  Decommissioned
                ↓             ↑           ↑              ↓
                └─────────────┴───────────┴──────── Withdrawn (back to Draft)
```

| State | Authoritative meaning | Allowed transitions | Required signature |
|---|---|---|---|
| **Draft** | Newly registered or returned-from-review | → In Review, → Decommissioned | Owner |
| **In Review** | Submitted for governance review | → Approved, → Withdrawn, → Decommissioned | AI Governance Lead |
| **Approved** | Approved but not yet promoted to production | → Active, → Withdrawn, → Decommissioned | AI Governance Lead + (Zone 3) Compliance Officer |
| **Active** | Live, in production, in scope of attestation | → Deprecated, → Decommissioned | Owner with notification to AI Governance Lead |
| **Deprecated** | Scheduled for decommission; no new use; existing use grandfathered | → Decommissioned, → Active (rare; requires Compliance Officer countersignature) | Owner + AI Governance Lead |
| **Decommissioned** | Removed from service; record retained | (terminal) | AI Governance Lead + Records Manager (binds the record under retention) |

### 10.1 Portal procedure for a single state transition

1. Open the register-of-record SharePoint list as the operator authorized for the target state per the table above.
2. Locate the register item by AgentID (canonical join key).
3. Click **Edit**. Update the Lifecycle State field. Update Last Reviewed and Next Review Due. Add a comment entry stating the transition reason and reference (change ticket, attestation cycle, incident ID).
4. Save. The SharePoint list update is logged in the Unified Audit Log under operations `SharePointFileOperation` / `ListItemUpdated` with the operator's UPN and timestamp.
5. *Screenshot description: SharePoint register list item edit form with Lifecycle State dropdown changed from "Active" to "Deprecated", a Comments box populated with "Deprecated per change ticket CHG-2026-04-0119; superseded by AgentID 8c3f...; deprecation effective 2026-05-01", and the audit-log timestamp banner at the top.*

### 10.2 Bulk state transition — defer to PowerShell

For environment retirement, bulk-deprecation, or any transition exceeding ~10 register items, switch to [PowerShell Setup](powershell-setup.md). The portal procedure is acceptable but loses the idempotency and hashing guarantees of the scripted flow.

### 10.3 Decommission gating

A transition to **Decommissioned** requires, in addition to the signatures above:

- Confirmation that the underlying agent has been disabled in its source surface (Plane 1 / Plane 2 / Plane 3) and that the disablement event is in the Unified Audit Log.
- Confirmation that all grounding sources have been re-evaluated (Control 4.6 hand-back).
- Confirmation that any in-flight conversations or transcripts have been preserved per [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) and the records have been bound under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
- Capture of the final-state evidence pack (`3.1-Decommission-{AgentID}-{YYYY-MM-DD}.zip`).

### 10.4 Withdrawn transition (recovery from In Review or Approved)

A Withdrawn transition returns an agent to Draft. It is used when the Owner wishes to revise the registration before re-submission, or when the AI Governance Lead identifies a gap that requires Owner-side rework. Withdrawn is **not** the same as Decommissioned; the register row remains in Draft and is not a record-of-removal event.

---

## §11. Orphaned, dormant, and shadow-agent workflows (portal procedure)

This playbook **detects and routes**. The remediation procedure itself lives in [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). The handoff is on the AgentID.

### 11.1 Orphan categories and detection

| Category | Definition | Primary detection surface | Secondary detection |
|---|---|---|---|
| **Departed-owner** | Owner UPN is soft-deleted, hard-deleted, or marked as `# (deleted)` | Plane 2 Maker Inventory `Owner = System Account` filter | Plane 1 Risks column "Owner inactive"; Graph user enumeration via PowerShell |
| **License-stripped** | Owner's M365 Copilot or Power Platform license was removed | Plane 1 Risks column; Plane 2 owner inactivity | Entra license assignment audit log |
| **Group-owned (anti-pattern)** | Owner is a security group rather than a named human | Manual scan of Owner column | Stitching workbook validation rule |
| **Dormant** | No agent activity beyond the zone threshold | Plane 1 Last activity column (preview); Sentinel telemetry per Control 3.9 | Plane 2 Modified date as proxy |
| **Shadow** | Agent exists in Plane 2 / Plane 3 but not in the register list | §7 stitching `Single-plane` flag | Manual sweep of PPAC Default environment |
| **Mis-registered** | Register row exists but no live agent in any plane | §7 stitching `Disappeared` flag | Owner attestation contradiction |

### 11.2 Departed-owner portal workflow

1. From Plane 1 (Copilot Hub Inventory → Agents tab), filter Risks = "Owner inactive" or "Ownerless".
2. For each result:
   - Click **Manage Ownerless** → assign Owner to a named human (the agent's business-line manager or the AI Governance Lead's designate); **never assign to a group**.
   - The action logs `OwnerChanged` in the Unified Audit Log; capture the entry as evidence.
3. From Plane 2 (PPAC Manage → Inventory), filter `Owner = System Account` for cross-confirmation.
4. Update the register row to reflect the new Owner; transition Lifecycle State to **In Review** until the new Owner countersigns the attestation.
5. **SLA:** Zone 3 = 5 business days from detection to new-Owner sign-off; Zone 2 = 10 business days; Zone 1 = 30 business days.

### 11.3 Dormant workflow

1. Identify dormant candidates from Plane 1 Last activity (where exposed) and Plane 2 Modified date.
2. Open the agent details and confirm zero activity beyond the zone threshold (default: Zone 3 = 90 days, Zone 2 = 180 days, Zone 1 = 365 days; verify firm-specific WSP).
3. Notify the Owner with a 30-day cure period.
4. If the Owner does not respond, transition Lifecycle State to **Deprecated** and notify the AI Governance Lead. After a further 60 days, transition to **Decommissioned** per §10.3.

### 11.4 Shadow-agent workflow

Shadow agents — created in Plane 2 (typically Default environment) but never registered — are the most common Zone-classification bypass.

1. From Plane 2 (PPAC Resources → Copilot agents), filter Environment = Default. Every row is a candidate.
2. For each candidate, open a Draft register row. Capture the Plane 2 owner as the tentative Owner. Notify the tentative Owner with a 5-business-day cure window.
3. If the Owner accepts ownership: complete the canonical metadata, classify Zone (most Default-environment agents are Zone 1; any with Highly Confidential grounding must escalate to Zone 3 and migrate to a Managed Environment per Control 2.1).
4. If the Owner rejects ownership or does not respond within the cure window: transition to **Decommissioned** with the AI Governance Lead's countersignature. The deletion event must be captured in the §13 evidence pack.

### 11.5 Mis-registered (Disappeared) workflow

1. From the §7 stitching flag list, take each `Disappeared` row.
2. Cross-check the Plane 2 Maker Inventory ledger for a deletion event.
3. If deletion is authorized (change ticket on file): transition to **Decommissioned**.
4. If deletion is **unauthorized**: open a Sev-2 governance incident under [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md). The unauthorized-deletion event is also a Records Management investigation per [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---

## §12. Quarterly attestation procedure (the three-signature workflow)

The quarterly attestation is the operational discipline that makes the register defensible. Every Zone 3 agent **must** be attested every 90 days; Zone 2 every 180 days; Zone 1 every 365 days.

### 12.1 Pre-attestation readiness

- Per-plane exports captured per §3.6, §4.6, §5.5, §6.4 within 7 calendar days of the attestation date.
- Stitching completed per §7 and AI Governance Lead has signed the stitched register.
- Orphan workflows from §11 cleared (no open orphan tickets older than the zone SLA).
- DLP and sensitivity-label checks per §9.3 and §9.4 completed for every Zone 2/3 register row.

### 12.2 The three signatures

The attestation requires three signatures, in this order, by **three distinct human individuals**. Group sign-off is prohibited; SoD requires that the same human MUST NOT sign as both Owner and AI Governance Lead for the same register row.

| Signer | Attests to | Signature artifact |
|---|---|---|
| **Inventory Owner** (the agent's named-human Owner) | Per-row attestation: "I confirm the canonical metadata is current and the agent operates within the registered Zone, grounding scope, and DLP/sensitivity posture." | SharePoint list item update with Owner UPN + timestamp + free-text comment |
| **AI Governance Lead** | Per-row review: "I have reviewed the per-plane evidence, confirmed the stitching, reconciled orphan workflows, and confirm the register accurately reflects the agent estate as of {date}." | SharePoint list item update with AI Governance Lead UPN + timestamp + free-text comment |
| **Compliance Officer** (Zone 3 only; Zone 2 may be delegated to a Compliance Officer designate per WSP) | Per-cycle attestation: "I have reviewed the AI Governance Lead's sign-off, the orphan SLA report, the sovereign-cloud determination, and confirm the cycle satisfies the firm's WSP and the regulatory commitments enumerated in the attestation memo." | Cycle-level signed PDF attestation memo countersigned by Compliance Officer |

### 12.3 The attestation memo

Each cycle produces a single attestation memo (PDF) with:

- Cycle ID (`{YYYY-Qn}`).
- Cycle date and signature timestamps.
- Counts: total agents, by Zone, by Lifecycle State, by Sovereign Cloud.
- Orphan SLA report (open / closed / SLA-breach).
- Stitching evidence reference (SHA-256 of the stitched register).
- Per-plane evidence reference (SHA-256 of each plane export).
- Sovereign-cloud determination reference.
- Hedged-language attestation statement (per §0.0 above).
- Three signatures (Owner row-level signatures referenced; AI Governance Lead and Compliance Officer per-cycle signatures embedded).
- Next cycle target date.

The memo is filed under `/_attestations/3.1-Attestation-{YYYY-Qn}.pdf`, hashed (SHA-256), and the hash is recorded in the register library metadata.

### 12.4 Cadence and calendar

| Zone | Attestation cadence | Calendar gating |
|---|---|---|
| **Zone 3** | ≤ 90 days | Calendar-quarter-aligned; no exception without Compliance Officer countersignature |
| **Zone 2** | ≤ 180 days | Calendar-half-aligned |
| **Zone 1** | ≤ 365 days | Calendar-year-aligned |

A missed attestation by more than the cadence threshold is a Sev-2 governance finding; by more than 2× the threshold is a Sev-1 escalation to the CISO and the AI Governance Council.

### 12.5 Bulk Owner attestation (portal-supported pattern)

For tenants with > 50 Zone 3 agents per attestation cycle, the per-row Owner sign-off is most efficiently driven via a SharePoint list view filtered by Owner UPN, surfaced to each Owner via Microsoft Lists desktop or mobile. Each Owner sees only their own rows and can attest in-place by editing the Last Reviewed and Comments fields, which records the SharePoint audit event. **Do not** use a Forms survey or generic SharePoint page for Owner attestation — the SharePoint list edit IS the audit-of-record event; a survey is not.

---

## §13. Examiner audit-pull procedure

The examiner audit-pull is the highest-stakes operational use of this playbook. The procedure is invoked by FINRA Rule 8210 request, OCC examination, Federal Reserve SR 11-7 inquiry, SEC inquiry, NYDFS Part 500.13/.16/.17 request, CFTC Rule 1.31 request, or ad-hoc supervisory request from the Designated Supervisor / Registered Principal.

### 13.1 SLA targets (verify against firm WSP)

| Trigger | Target SLA | Notes |
|---|---|---|
| FINRA Rule 8210 written request | ≤ 5 business days from receipt | WSP-confirmed |
| OCC examination request (in-cycle) | ≤ 30 calendar days | Per OCC examination procedures |
| Federal Reserve SR 11-7 inquiry | ≤ 30 calendar days | Per firm escalation procedure |
| SEC inquiry (formal) | Per SEC subpoena timeline | Coordinate with General Counsel |
| NYDFS Part 500.17 (cybersecurity event) | ≤ 72 hours notification; 90 days remediation | Coordinate with CISO |
| CFTC Rule 1.31 (recordkeeping) | Per CFTC request timeline | |
| Ad-hoc supervisory (Designated Supervisor) | ≤ 24 hours | Per FINRA Rule 3110 supervision |

### 13.2 Point-in-time snapshot reconstruction

The examiner request will specify a date (or date range). Reconstruction proceeds as follows:

1. Locate the most recent stitched register snapshot **on or before** the examiner-specified date in `/_evidence/{YYYY-Qn}/3.1-Register-{YYYY-MM-DD}.csv`.
2. If no snapshot exists on or before the date, the next-best evidence is the per-plane exports captured nearest the date plus the prior cycle's stitched register; document the gap in the cover memo.
3. Verify SHA-256 of each artifact against the manifest. Any hash mismatch is an evidence-integrity escalation per Control 1.9.
4. Pull the corresponding Unified Audit Log range covering register-list mutations (operations `ListItemUpdated` / `FileModified` on the register library) for the period bracketing the snapshot — these are the Owner-attestation timestamps that prove the register was attested as of the snapshot date.
5. Pull the corresponding attestation memo PDF(s).

### 13.3 Examiner package contents

The package delivered to the examiner contains:

- **Cover memo** (signed by Designated Supervisor / Registered Principal): describes scope, date range, snapshot reconstruction approach, hedged-language statement of what the inventory does and does not represent, list of attached artifacts with SHA-256 hashes.
- **Stitched register CSV** (or the closest-available snapshot, with gap memo if applicable).
- **Per-plane exports** for the snapshot period.
- **Attestation memos** covering the period.
- **Sovereign-cloud determination memo** in force at the snapshot date.
- **Orphan-SLA report** for the period.
- **Unified Audit Log extract** for register mutations during the period.
- **Schema definition file** (`3.1-canonical-schema-v{n}.json`) in force at the snapshot date.
- **Manifest** (text or PDF) listing every file with SHA-256.

### 13.4 Chain of custody

Every examiner-pull invocation creates a chain-of-custody record stored under `/_examiner-pulls/{YYYY-MM-DD}-{request-ID}.pdf` containing:

- Examiner identity, agency, and request reference.
- Designated Supervisor / Registered Principal who authorized the pull.
- Manifest of artifacts included with SHA-256 hashes.
- Delivery method (encrypted file transfer, secure portal, paper) with delivery confirmation.
- Receiving examiner acknowledgement (where obtainable).

### 13.5 Reverse-burden language

The cover memo MUST include the hedged-language statement from §0.0. Do **not** state "this is a complete record of all AI agents in the tenant." State instead: "This package represents the canonical agent register stitched from the six discovery surfaces enumerated in §0.3 of the firm's Control 3.1 procedure, attested as of {date}, with the limitations and sovereign-cloud caveats documented in the attached determination memo."

---

## §14. Zone-specific portal workflow differentials

| Step | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---|---|---|---|
| Required canonical fields (§1.2) | Owner, Display Name, Agent Type, Platform, Zone, Lifecycle State, Last Reviewed, Next Review Due | Above + Backup Owner, Business Justification, Data Classification, Connected Knowledge Sources, Connected Actions, Plugins, Foundation Model, Environment, Effective Sensitivity Label, DLP Policy Mapping, Sovereign Cloud, Approval Records | All fields |
| Pre-flight gates (§2) | PRE-01, PRE-02 (subset) | PRE-01, PRE-02, PRE-03, PRE-04 | All five gates |
| Stitching cadence (§7) | Annual | Semi-annual | Quarterly |
| Orphan SLA (§11) | 30 business days | 10 business days | 5 business days |
| Attestation cadence (§12) | ≤ 365 days | ≤ 180 days | ≤ 90 days |
| Attestation signers (§12.2) | Owner | Owner + AI Governance Lead | Owner + AI Governance Lead + Compliance Officer |
| Examiner-pull readiness (§13) | Best-effort within SLA | Standard | Pre-staged; ≤ 5 business days for FINRA 8210 |
| Audit-Log Reference (§1.2) | Optional | Recommended | Required |
| Risk Register Reference | Optional | Recommended | Required |
| Validation Evidence Pack | Optional | Recommended | Required |
| Sovereign-cloud determination memo | Tenant-level | Tenant-level | Per-agent annotation |
| Sentinel register-deviation alert (Control 3.9) | Optional | Recommended | Required |
| Preservation Lock on register library (§8.3) | Recommended | Required | Required |
| Per-row Owner attestation interface (§12.5) | Annual reminder email | Semi-annual SharePoint list view | Quarterly Microsoft Lists dashboard |

### 14.1 Zone-3 customer-facing reverse burden

Any Zone 3 agent that touches customer interactions, customer NPI/MNPI data, recordkeeping outputs, or trade-related decisions carries a **reverse-burden** posture: in any examination, the firm must affirmatively demonstrate the agent was registered, attested, and DLP/sensitivity-mapped at the time of the customer touch. The §13 procedure is the demonstration vehicle.

### 14.2 Zone migration

When an agent's grounding scope, data classification, or business use changes such that its Zone classification must change:

- **Up-zone (Zone 1 → 2 or 2 → 3):** Required immediately upon discovery; freeze the agent (transition to In Review) until the higher-zone metadata is fully populated and the higher-zone signers attest. Migrate environment per [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md). The §11 §11.4 shadow-agent workflow may be the trigger.
- **Down-zone (Zone 3 → 2 or 2 → 1):** Allowed only with Compliance Officer countersignature and only after a full attestation cycle's evidence supports the lower-risk classification. Down-zoning a Zone 3 agent is a §11 governance review item.

---

## §15. Anti-pattern catalog

Each anti-pattern below has been observed in FSI tenants. Detection is part of the §11 review and the §12 attestation. Any occurrence is a finding.

### 15.1 The "spreadsheet register"

**Pattern:** Register lives in an Excel file on a shared drive or in a Teams chat.
**Why it fails:** No retention binding, no audit log of mutations, no Preservation Lock, fails SEC 17a-4(f), fails Control 1.9.
**Fix:** Migrate to a SharePoint list with auto-apply retention label per §8 within 30 days.

### 15.2 The "single-pane illusion"

**Pattern:** Operator treats the M365 Copilot Hub Inventory (Plane 1) as the complete register.
**Why it fails:** Plane 1 misses Copilot Studio agents not published to M365, Custom Engine Agents with Entra-only registration, Default-environment shadow agents.
**Fix:** Stitch all six planes per §7 every cycle; no exceptions.

### 15.3 The "group-owner" anti-pattern

**Pattern:** Owner field set to a security group, distribution list, or dynamic group.
**Why it fails:** Group ownership defeats FINRA 3110 supervisory accountability, defeats orphan detection (no individual to leave the firm), defeats attestation (no individual to sign).
**Fix:** Owner MUST be a named human; Backup Owner MUST be a distinct named human. Group ownership is a finding at any zone.

### 15.4 The "service-account-as-Owner" anti-pattern

**Pattern:** Owner is a service account or unattended automation account.
**Why it fails:** Same supervisory failure as group ownership; service accounts cannot attest.
**Fix:** Service-account creation may be acceptable for runtime authentication, but the Owner field must be a named human accountable for the service account.

### 15.5 The "self-attest" anti-pattern

**Pattern:** The same human signs as both Owner and AI Governance Lead for the same register row.
**Why it fails:** Defeats SoD; defeats FINRA 3110 supervisory independence; defeats FINRA 25-07 governance posture.
**Fix:** Enforced by the §12.2 SoD rule; flagged at attestation.

### 15.6 The "annual-only" anti-pattern

**Pattern:** Zone 3 agent attested only annually because Zone 1 cadence was applied by default.
**Why it fails:** Misses 3 quarterly cycles of FINRA 4511 / SEC 17a-4 evidence; reverse-burden defeated.
**Fix:** Drive attestation cadence from Zone field; flag any Zone 3 with Last Reviewed > 90 days.

### 15.7 The "Default environment" anti-pattern

**Pattern:** Production agents created in the Power Platform Default environment.
**Why it fails:** Default environment cannot be a Managed Environment in many tenant configurations; DLP-policy mapping is weakest; orphan signal is silent.
**Fix:** Migrate to a Managed Environment per [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md); use the §11.4 shadow workflow for any Default-environment agent surviving discovery.

### 15.8 The "missing AppID" anti-pattern

**Pattern:** Register row has no Enterprise App / Service Principal ID for an Entra-backed agent.
**Why it fails:** Breaks the Plane 3 ↔ Plane 1/2 join; breaks Sentinel correlation per Control 3.9; breaks the §6 orphan workflow when a service principal is removed independently.
**Fix:** Stitching workbook validation rule must reject a Zone 2/3 register row missing the AppID.

### 15.9 The "stale stitching" anti-pattern

**Pattern:** Stitching is run once and treated as authoritative for multiple cycles.
**Why it fails:** Misses new agents, owner changes, environment moves, orphan emergence.
**Fix:** Stitching MUST be run at every attestation cycle; ad-hoc on examiner trigger; opportunistically on Sentinel deviation alert.

### 15.10 The "preview-as-authoritative" anti-pattern

**Pattern:** Treating Plane 4 (Agent 365 preview) as the sole or primary register surface.
**Why it fails:** Preview surfaces lack stable schema, lack sovereign-cloud parity, may regress between monthly builds.
**Fix:** Preview surfaces are additive cross-check evidence until GA in the operating cloud and re-signed in the §1.5 memo.

### 15.11 The "screenshot-only" anti-pattern

**Pattern:** Attestation evidence consists of screenshots only, with no CSV exports and no SHA-256 hashes.
**Why it fails:** Screenshots are not tamper-evident; not machine-comparable cycle-over-cycle; weak under SEC 17a-4(f).
**Fix:** Screenshots are supplementary; the CSV export with SHA-256 hash is the primary artifact.

### 15.12 The "implied-consent" anti-pattern

**Pattern:** AI Governance Lead "approves" attestation by failing to object within a window.
**Why it fails:** Implicit approval is not a signature; not auditable; defeats the three-signature workflow.
**Fix:** Each signer MUST explicitly attest in the SharePoint list (rows) and in the memo PDF (cycle); silence is not consent.

### 15.13 The "Copilot Studio = inventory" anti-pattern

**Pattern:** Power Platform Admin treats PPAC as the register and ignores M365 Copilot Hub, Entra, SharePoint.
**Why it fails:** Misses Plane 1 declarative agents, Plane 3 Custom Engine Agents, Plane 6 Connected Apps.
**Fix:** AI Governance Lead owns the cross-plane stitching; PPAC alone is not the register.

### 15.14 The "license-strip = decommission" anti-pattern

**Pattern:** Operator believes that revoking the Owner's M365 Copilot license decommissions the agent.
**Why it fails:** License strip removes the Owner's ability to use the agent but does not remove the agent itself; the agent persists ownerless and may continue to serve other users until disabled in source surface.
**Fix:** Decommission is a Lifecycle State transition per §10.3 with explicit source-surface disablement; license strip is a §11 orphan-detection signal, not a decommission.

### 15.15 The "exception without evidence" anti-pattern

**Pattern:** A canonical-schema validation rule is waived without a corresponding Exception Reference.
**Why it fails:** Defeats the schema contract; downstream controls cannot distinguish a populated waiver from a missing field.
**Fix:** Every waived field MUST have an Exception Reference URL pointing to a Compliance Officer–signed exception with expiry; the exception expiry MUST be re-attested at the next attestation cycle.

---

## §16. Verification handoff

Verification of this playbook's outputs lives in [Verification & Testing](verification-testing.md). The handoff is:

- This playbook **produces** the per-plane exports, the stitched register, the attestation memo, the chain-of-custody record, and the §13 examiner package.
- Verification & Testing **validates** the integrity, completeness, and SLA-conformance of those outputs.

Verification entry criteria:

- All §2 pre-flight gates signed off.
- Per-plane exports captured per §3.6, §4.6, §5.5, §6.4 with SHA-256 in the manifest.
- Stitching completed per §7 with the AI Governance Lead's signature.
- Orphan workflow per §11 closed within zone SLA.
- Attestation memo per §12 prepared and ready for Compliance Officer countersignature.

Verification will return one of: **PASS** (Compliance Officer can sign), **CONDITIONAL** (named gaps to remediate before sign), or **FAIL** (cycle restart required).

---

## §17. Troubleshooting handoff

Symptom-driven diagnosis lives in [Troubleshooting](troubleshooting.md). Most-common entry points:

- "Plane 1 export is missing columns visible in the grid" — Troubleshooting §T-01.
- "Plane 2 grid is capped at 500 rows but the tenant has more agents" — Troubleshooting §T-02.
- "Plane 3 Agent Registry blade is unavailable in our cloud" — Troubleshooting §T-03.
- "Stitching produces a high `Owner-mismatch` count" — Troubleshooting §T-04.
- "Manage Ownerless action returns an error" — Troubleshooting §T-05.
- "Attestation Owner cannot edit the SharePoint list" — Troubleshooting §T-06.
- "DAG report shows zero sites with Copilot grounding scope" — Troubleshooting §T-07.
- "Preservation Lock cannot be applied — error 'records management not enabled'" — Troubleshooting §T-08.
- "Examiner pull SHA-256 hash mismatch" — Troubleshooting §T-09.
- "Per-plane export hash matches manifest but stitched register hash does not" — Troubleshooting §T-10.

---

## §18. Evidence pack — the 25 artifacts

A complete cycle produces (at least) the following artifacts, all hashed and stored under the register-of-record library with retention/Preservation Lock binding:

| # | Artifact | Naming | Source |
|---|---|---|---|
| 1 | Plane 1 Agents export | `3.1-Plane1-Agents-{date}.csv` | §3.6 |
| 2 | Plane 1 Declarative agents export | `3.1-Plane1-Declarative-{date}.csv` | §3.3 |
| 3 | Plane 1 Extensions export | `3.1-Plane1-Extensions-{date}.csv` | §3.4 |
| 4 | Plane 2 Resources → Copilot agents export | `3.1-Plane2-Resources-{date}.csv` | §4.6 |
| 5 | Plane 2 Maker Inventory export | `3.1-Plane2-MakerInventory-{date}.csv` | §4.5 |
| 6 | Plane 3 Enterprise apps export | `3.1-Plane3-EnterpriseApps-{date}.csv` | §5.5 |
| 7 | Plane 3 App registrations export (PowerShell-sourced) | `3.1-Plane3-AppRegistrations-{date}.csv` | sibling PowerShell |
| 8 | Plane 3 Agent Registry export (where GA) | `3.1-Plane3-AgentRegistry-{date}.csv` | §5.3 |
| 9 | Plane 4 Agent 365 export (where entitled) | `3.1-Plane4-AgentList-{date}.csv` | §6.4 |
| 10 | Plane 4 Agent 365 ownerless queue (where entitled) | `3.1-Plane4-Ownerless-{date}.csv` | §6.4 |
| 11 | Plane 6 Connected Apps export | `3.1-Plane6-ConnectedApps-{date}.csv` | §9.1 |
| 12 | Plane 6 DAG report export | `3.1-Plane6-DAG-{date}.csv` | §9.2 |
| 13 | Stitched register | `3.1-Register-{date}.csv` (+ `.xlsx` workbook) | §7 |
| 14 | Schema definition in force | `3.1-canonical-schema-v{n}.json` | §1.2 |
| 15 | Sovereign-cloud determination memo | `3.1-sovereign-cloud-determination-{YYYY-MM}.pdf` | §1.5 |
| 16 | Pre-flight gate sign-offs (PRE-01 through PRE-05) | `3.1-PRE-{n}-{name}-{date}.pdf` | §2 |
| 17 | Per-Owner row attestation log (SharePoint list export) | `3.1-OwnerAttestations-{YYYY-Qn}.csv` | §12.5 |
| 18 | AI Governance Lead cycle sign-off | embedded in attestation memo | §12.2 |
| 19 | Compliance Officer cycle sign-off | embedded in attestation memo | §12.2 |
| 20 | Cycle attestation memo | `3.1-Attestation-{YYYY-Qn}.pdf` | §12.3 |
| 21 | Orphan-SLA report | `3.1-OrphanSLA-{YYYY-Qn}.csv` | §11 |
| 22 | Sentinel register-deviation alert log (Zone 3) | `3.1-SentinelDeviations-{YYYY-Qn}.csv` | Control 3.9 |
| 23 | Unified Audit Log extract for register library mutations | `3.1-UAL-RegisterMutations-{YYYY-Qn}.csv` | Control 1.7 |
| 24 | Manifest with SHA-256 of all above | `3.1-Manifest-{YYYY-Qn}.txt` (or `.pdf`) | sibling PowerShell |
| 25 | Examiner-pull chain-of-custody record (when invoked) | `3.1-ExaminerPull-{date}-{request-ID}.pdf` | §13.4 |

The manifest is the **first artifact a Compliance Officer or examiner reads**. Without it, the package has no integrity.

---

## §19. Cross-references

This playbook depends on or is consumed by the following controls. Implementers must verify each link is current at deploy time.

**Upstream (this playbook depends on):**

- [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — agent intake and approval that feeds Lifecycle State Draft → In Review.
- [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — UAL pipeline that captures register-mutation events.
- [Control 1.9 — Records Management and Preservation Lock](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — Preservation Lock on register library.
- [Control 1.13 — Sensitive Information Types](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) — sensitivity-label authoring that feeds §9.3 inheritance check.
- [Control 1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) — preserves transcripts at §10.3 decommission.
- [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) — environment classification reconciled at §1.2 Zone field.
- [Control 2.5 — Testing, Validation, and Quality Assurance](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) — Validation Evidence Pack referenced in §1.2.
- [Control 1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — DLP business-data-group classifications consumed at §9.4.
- [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) — grounding inventory joined at §9.3.
- [Control 4.7 — Microsoft 365 Copilot Data Governance](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) — sensitivity-label propagation reference.

**Downstream (this playbook is consumed by):**

- [Control 3.2 — Usage Analytics and Activity Monitoring](../../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) — reads the canonical register on AgentID.
- [Control 3.4 — Incident Reporting and Root-Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — joins incidents to register on AgentID.
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — receives orphan handoffs from §11.
- [Control 3.8 — Copilot Hub and Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) — surfaces register data to executive dashboards.
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — register-deviation alerts.
- [Control 3.11 — Centralized Agent Inventory Enforcement](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) — publish-time gating on register completeness.
- [Control 3.3 — Compliance and Regulatory Reporting](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) — examiner-pull packaging shares the §13 procedure.

**Sibling playbooks for this control:**

- [PowerShell Setup](powershell-setup.md) — bulk export, scheduled reconciliation, hashing, idempotent diffing.
- [Verification & Testing](verification-testing.md) — pre-attestation readiness validation; evidence-pack completeness check.
- [Troubleshooting](troubleshooting.md) — symptom-driven diagnosis for portal, surface, stitching, and evidence problems.

---

## §20. Closing reminders

- **No single surface is the inventory.** The register of record is the stitched export, signed by the AI Governance Lead, bound to retention.
- **Owners are humans, not groups.** Every Owner and Backup Owner is a named individual; group ownership is a finding at any zone.
- **Three signatures, three humans.** Owner, AI Governance Lead, and (Zone 3) Compliance Officer; same human cannot occupy two attestor roles for the same row.
- **Preview surfaces are additive.** Plane 4 Agent 365 and the Plane 3 Agent Registry blade are cross-check evidence until GA in your sovereign cloud and re-signed in the §1.5 memo.
- **Hash everything.** Every exported artifact carries SHA-256 in the cycle manifest; the manifest is the first artifact in any examiner package.
- **Hedge the language.** "Helps support compliance with" — never "ensures compliance" or "guarantees" or "complete inventory" or "single pane of glass" or "real-time discoverability".

---

*Updated: April 2026 | Version: v1.4 | Maintained by: AI Governance Team*