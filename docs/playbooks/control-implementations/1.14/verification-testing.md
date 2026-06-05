# Verification & Testing — Control 1.14: Data Minimization and Agent Scope Control

> **Scope.** This playbook verifies that every Microsoft 365, Power Platform, and Microsoft Copilot Studio agent registered against Control 1.14 is grounded only in the data sources, connectors, and OAuth scopes documented in the per-agent inventory, and that any change to that scope is detected, approved, and recorded in the Unified Audit Log (UAL) within published processing windows.
>
> **Audience.** AI Governance Lead (Responsible), Power Platform Admin and Purview Compliance Admin (Accountable for primary tooling), CISO and Compliance Officer (Approver), Audit Manager (Consulted on evidence retention), Information Protection Admin and Purview Data Security AI Admin (Consulted on DSPM for AI signals), Entra Identity Governance Admin (Consulted on access reviews), SharePoint Admin (Consulted on grounding scope).
>
>
> **Cross-links.** Controls [1.2 Agent Registry](../1.2/portal-walkthrough.md) · [1.4 Connector Governance](../1.4/portal-walkthrough.md) · [1.10 Conditional Access for Agents](../1.10/portal-walkthrough.md) · [1.13 SIT-Aware DLP for Copilot](../1.13/verification-testing.md) · [1.17 Agent Identity Lifecycle](../1.17/portal-walkthrough.md) · [1.18 OAuth Consent Governance](../1.18/portal-walkthrough.md) · [1.19 Service Principal Hygiene](../1.19/portal-walkthrough.md) · [4.6 Grounding Scope Governance](../4.6/portal-walkthrough.md) · [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) · [PowerShell Baseline](../../_shared/powershell-baseline.md).
>
> **Last UI verified.** May 2026 against Power Platform Admin Center, Copilot Studio, Microsoft Purview portal (DSPM for AI / unified DSPM AI activities), Microsoft Entra admin center, and SharePoint admin center.

---

## What this verification catches

This playbook is designed to detect the following failure modes, each of which has been observed in FSI Microsoft 365 deployments and each of which carries a regulatory exposure under FINRA 4511, FINRA 3110, FINRA RN 24-09, SEC Reg S-P (2024 amendments), SEC 17a-3 / 17a-4, GLBA 501(b), SOX 404, OCC Bulletin 2026-13 (formerly OCC 2011-12), and CCPA §1798.100:

1. **Silent NPI grounding via site-rooted scope.** A Z3 customer-facing agent is pointed at a SharePoint site root (rather than a specific document library or folder), so newly added libraries containing NPI become groundable without any change-management event.
2. **OAuth scope creep.** A connector authorization initially granted with a narrow scope (e.g., `Files.Read`) is silently broadened on re-consent (e.g., to `Files.ReadWrite.All` or `Sites.Read.All`) without re-approval and without a UAL `Consent to application` event being reviewed.
3. **Blocked-connector bypass.** A connector classified `Blocked` in tenant DLP is reachable in a non-default Power Platform environment that the DLP policy does not cover.
4. **Knowledge-source drift undetected.** A new knowledge source is added to a Z2 or Z3 agent and is accepted at runtime before any drift signal is reviewed by the AI Governance Lead, because the alert is routed only to the Power Platform Admin distribution group.
5. **Orphan justifications.** An `(agent, datasource)` row in the inventory loses its business justification (because the requester left the firm) but the data source remains attached, leaving the agent technically grounded with no documented basis.
6. **RCD / RSS misalignment with Control 4.6.** A Copilot Studio knowledge source resolves to a SharePoint site that the 4.6 Restricted Content Discovery (RCD) decision excluded from agent grounding, exposing a contradictory governance posture.
7. **Custom and HTTP connectors outside Advanced Connector Policy (ACP) scope.** Custom connectors and HTTP connectors are assumed to be ACP-governed and therefore action-restricted; in fact ACP applies only to certified connectors, so these channels remain governed only by classic DLP endpoint filtering and require explicit verification.
8. **Decommission silently purges evidence.** An agent is decommissioned and its evidence is deleted with the workspace, contrary to FINRA 4511 / SEC 17a-4(f) six-year retention.
9. **Single-identity build-approve-review.** The same identity that built the agent also approved the connector grant and signed off on the access review, defeating segregation of duties under SOX 404 and FINRA 3110.
10. **Restricted SharePoint Search treated as a long-term Z3 boundary.** RSS is positioned by Microsoft as a short-term remediation step while a tenant deploys SharePoint Advanced Management; treating it as a permanent Z3 control masks the absence of folder-scoped grounding.

---

## §1 Verification cadence

The cadence below is the minimum re-verification frequency per zone and per test family. Z3 agents (enterprise / customer-facing / regulated) require monthly re-verification of all families because changes to grounding, connector scope, or OAuth consent on a Z3 agent carry the highest NPI-exposure and SEC Reg S-P notification risk. Z1 agents (personal productivity) are re-verified annually as a control sample; the NEG family includes a Z1 control-arm test (NEG-02) so that drift detection is demonstrated to be tuned and not firing globally.

| Test family | Z1 (Personal) | Z2 (Team) | Z3 (Enterprise) | Owner | Reviewer | Regulatory driver |

| LIC (license and role separation) | Annual | Quarterly | Monthly | Power Platform Admin | AI Governance Lead | FINRA 4511, SOX 404 |
| UAL (audit log enablement and event flow) | Annual | Quarterly | Monthly | Purview Compliance Admin | Audit Manager | FINRA 4511, SEC 17a-4 |
| INV (per-agent data-access inventory) | Annual | Quarterly | Monthly | AI Governance Lead | Compliance Officer | GLBA 501(b), FINRA 4511 |
| DLP (connector data loss prevention) | Annual | Quarterly | Monthly | Power Platform Admin | Information Protection Admin | FINRA 3110, GLBA 501(b) |
| OAUTH (minimum scope, re-consent) | Annual | Quarterly | Monthly | Entra Identity Governance Admin | AI Governance Lead | GLBA 501(b), SEC Reg S-P |
| SCOPE (knowledge source, SP groups, Dataverse roles) | Annual | Quarterly | Monthly | SharePoint Admin | AI Governance Lead | FINRA 4511, FINRA RN 24-09, FINRA 3110 |
| DRIFT (provoke and detect scope drift) | n/a | Quarterly | Monthly | AI Governance Lead | CISO | FINRA 3110, FINRA RN 24-09 |
| APR (zone approval workflow, access review) | Annual | Quarterly | Monthly | Entra Identity Governance Admin | Compliance Officer | SOX 404, GLBA 501(b) |
| AUDIT (UAL reconciliation) | Annual | Quarterly | Monthly | Audit Manager | Compliance Officer | FINRA 4511, SEC 17a-4 |
| NEG (negative tests) | Annual | Semi-annual | Quarterly | AI Governance Lead | Audit Manager | Control validation |
| IR (incident-response tabletop) | n/a | Annual | Annual | CISO | CRO | SEC Reg S-P 2024, GLBA 501(b) |

**Cadence enforcement.** The PowerShell validator in §6.2 emits a `lastRunUtc` field per test family. The companion solution `scope-drift-monitor` in `FSI-AgentGov-Solutions` raises an alert when a family's `lastRunUtc` exceeds the cadence shown above by more than 7 days. Cadence drift is itself a finding under SOX 404 (control operating effectiveness) and should be tracked in the issues register, not silently re-baselined.

---

## §2 Pre-flight

Pre-flight tests confirm that the verification harness can run reliably and that the tenant satisfies the minimum platform conditions for a meaningful test. A failure in any PRE test halts the run and is logged as `Status=Skip` with `Detail` describing the missing precondition; downstream tests are not attempted. This fail-closed posture is consistent with the 1.13 verification harness.

### 1.14-PRE-01 — License entitlement attested

**Objective.** Confirm that the tenant has the licenses required for Power Platform DLP, Copilot Studio agent governance, Purview DSPM for AI, and Microsoft Entra Identity Governance access reviews.

**Preconditions.** Power Platform Admin role; Purview Compliance Admin role; Entra Global Reader; tenant ID.

**Steps.**

1. From Power Platform Admin Center, capture the Managed Environment licensing status: **Manage > Tenant settings > Managed Environment**.
2. From the Microsoft 365 admin center > Billing > Licenses, export the SKU assignments to CSV.
3. From the Microsoft Purview portal, navigate to **DSPM for AI > Get started** and confirm that signal collection is enabled and reporting.
4. From the Microsoft Entra admin center, navigate to **Identity Governance > Access reviews** and confirm the feature is licensed (P2 or Microsoft Entra ID Governance SKU).

**Expected.** All four feature areas show entitled status and the SKU export shows at least one assignment of the required SKU(s) per zone test user.

**Pass criteria.** All four screenshots captured, SKU CSV present, no licensing gap noted.

**Audit assertion.** "Tenant `{tenantId}` is entitled to Power Platform Managed Environments, Copilot Studio governance, Purview DSPM for AI, and Microsoft Entra Identity Governance as of `{utcDate}`."

**Evidence collected.** `1.14-PRE-01_licensing.csv`, `1.14-PRE-01_dspm-for-ai.png`, `1.14-PRE-01_managed-env.png`, `1.14-PRE-01_access-reviews.png`.

### 1.14-PRE-02 — Role separation (segregation of duties)

**Objective.** Demonstrate that the Power Platform Admin, SharePoint Admin, Purview Compliance Admin, and AI Governance Lead are held by distinct identities (not the same person, and not the same service principal). This is required to support SOX 404 segregation-of-duties review.

**Preconditions.** Microsoft Graph PowerShell with `RoleManagement.Read.Directory`; the canonical role-to-identity mapping from `docs/reference/role-catalog.md`.

**Steps.**

1. Run `Get-MgRoleManagementDirectoryRoleAssignment -All` and export to JSON.
2. Filter for the four canonical role definitions: Power Platform Administrator, SharePoint Administrator, Compliance Administrator, and the custom AI Governance Lead role (or its tenant-specific equivalent).
3. Compare principal IDs across the four sets; any overlap is a finding.

**Expected.** No principal ID appears in more than one of the four role sets. Service principals (if any) are documented in Control 1.19 hygiene records.

**Pass criteria.** Distinct-principal report shows zero overlap; any documented exception is approved by the CISO and recorded in the issues register.

**Audit assertion.** "Role separation verified for tenant `{tenantId}` on `{utcDate}`. No identity holds two of the four canonical roles."

**Evidence collected.** `1.14-PRE-02_role-assignments.json`, `1.14-PRE-02_distinct-principal-report.csv`.


### 1.14-PRE-04 — Unified Audit Log enabled and ingesting

**Objective.** Confirm that UAL is enabled on the tenant and that the workloads required by Control 1.14 (`MicrosoftCopilotStudio`, `PowerPlatformConnector` / `MicrosoftFlow`, `PowerAppsPlan`, `SharePoint`, `AzureActiveDirectory`) are ingesting events.

**Preconditions.** Exchange Online PowerShell connected with `Connect-ExchangeOnline`; Purview Compliance Admin or equivalent.

**Steps.**

1. Run `Get-AdminAuditLogConfig | Select UnifiedAuditLogIngestionEnabled` and confirm `True`.
2. For each workload above, run `Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) -RecordType {workload} -ResultSize 1` and confirm at least one row is returned.
3. Page the search using `-SessionId` and `-SessionCommand ReturnLargeSet` to confirm the harness avoids the basic 10,000-row cap (this is the same trap class documented in 1.13 anti-pattern §8.13).

**Expected.** UAL enabled; each workload returns at least one event in the last 7 days; paged search completes without exceeding the cap.

**Pass criteria.** All five workloads return events; paged-search test demonstrates `ResultIndex > 10000` capability.

**Audit assertion.** "UAL ingestion verified across the five workloads required by Control 1.14 on `{utcDate}` in tenant `{tenantId}`."

**Evidence collected.** `1.14-PRE-04_ual-config.json`, `1.14-PRE-04_workload-flow.csv`.

### 1.14-PRE-05 — PowerShell module pinning

**Objective.** Confirm that the verification harness runs against pinned versions of every PowerShell module it depends on, so that a future cmdlet behavior change cannot silently invalidate prior evidence.

**Preconditions.** PowerShell 7.4 or later.

**Steps.**

1. Run the module-pinning block from `_shared/powershell-baseline.md` (also reproduced in §6.2 of this playbook).
2. Capture `Get-Module -ListAvailable | Where-Object Name -in @('Microsoft.PowerApps.Administration.PowerShell','Microsoft.Online.SharePoint.PowerShell','PnP.PowerShell','ExchangeOnlineManagement','Microsoft.Graph.Authentication','Microsoft.Graph.Identity.SignIns','Microsoft.Graph.Applications')` and export to JSON.
3. Confirm the tenant-approved `Microsoft.Online.SharePoint.PowerShell` build is current enough to expose the Restricted Content Discovery / Restricted SharePoint Search cmdlets used by Control 4.6 validation; if not, record a fail or skip rather than asserting clean SharePoint scope evidence.

**Expected.** Each module present at the minimum pinned version; the harness throws if any module is below the pin.

**Pass criteria.** Module-version report present; no missing or under-versioned module.

**Audit assertion.** "PowerShell module versions pinned and verified on `{utcDate}`."

**Evidence collected.** `1.14-PRE-05_module-versions.json`.

### 1.14-PRE-06 — Two-portal precondition (PPAC DLP + Purview DSPM for AI)

**Objective.** Confirm that the two governance surfaces relied on by Control 1.14 — Power Platform Admin Center DLP and Microsoft Purview DSPM for AI — are both reachable by the verifier and both reflect the same tenant. This is the same trap class flagged in 1.8 §2.5: a tenant may have one surface configured by one team and the other surface left in default, producing contradictory evidence.

**Preconditions.** Power Platform Admin and Purview Compliance Admin roles.

**Steps.**

1. From Power Platform Admin Center, capture the DLP policies list and confirm at least one policy is present.
2. From **Purview > DSPM for AI > Activity explorer** or, in the unified experience, **DSPM > Discover > Activity explorer > AI activities**, capture a 24-hour activity export and confirm events from at least one Copilot Studio agent are present.
3. Confirm both portals show the same tenant ID in the tenant switcher.

**Expected.** Both portals reachable, same tenant, both showing recent activity.

**Pass criteria.** Two-portal screenshot pair captured; tenant ID matches.

**Audit assertion.** "Two-portal precondition satisfied for tenant `{tenantId}` on `{utcDate}`."

**Evidence collected.** `1.14-PRE-06_ppac-dlp.png`, `1.14-PRE-06_dspm-activity.csv`.

### 1.14-PRE-07 — Named test users, named test agents, controlled corpus

**Objective.** Confirm that the verification harness uses named test identities (one per zone), named test agents (one per zone), and a controlled test corpus, so that observed UAL events can be unambiguously attributed to the test run.

**Preconditions.** Three test users (`testuser-z1@`, `testuser-z2@`, `testuser-z3@`); three test agents (`agent-fsi-test-Z1`, `agent-fsi-test-Z2`, `agent-fsi-test-Z3`) registered in Control 1.2; controlled SharePoint site `https://{tenant}.sharepoint.com/sites/fsi-test-1.14` with the test corpus published under `tests/1.14/corpus/` (folders: `in-scope`, `out-of-scope-finance`, `out-of-scope-hr`).

**Steps.**

1. Confirm each test user exists in Entra and is licensed (LIC-01).
2. Confirm each test agent is registered in the Control 1.2 agent registry with a stable agent ID.
3. Confirm the SharePoint test site exists and the three corpus folders are populated with at least 5 seed documents each (one document per folder must contain a synthetic SIT match per Control 1.13 to support cross-test verification).
4. Capture the test inventory at `tests/1.14/manifest.json` so the harness can resolve test IDs to live agent IDs.

**Expected.** All three test users, three test agents, and one test site present; corpus seeded.

**Pass criteria.** Test manifest validates against `evidence-manifest-v1.json` schema (see §6.1).

**Audit assertion.** "Test fixtures present for tenant `{tenantId}` on `{utcDate}`: 3 users, 3 agents, 1 site, 15 corpus documents."

**Evidence collected.** `1.14-PRE-07_test-manifest.json`, `1.14-PRE-07_corpus-listing.csv`.

---

## §3 Documented processing windows

Each test in §4 has an "Expected" clause that depends on a Microsoft-published or Microsoft-documented processing window between an action being taken and a signal becoming visible to the verifier. These windows are reproduced below; if a test fails because a signal is not yet visible, the verifier should re-run after the window has elapsed before raising a finding.

| Signal source | Action → signal visibility window | Source | Used by |

| Power Platform DLP policy propagation (tenant-wide) | Up to 24 hours after policy change | Microsoft Learn — *Data loss prevention policies* | DLP-01..05 |
| Power Platform DLP policy propagation (single environment) | Up to 1 hour after policy change | Microsoft Learn — *Data loss prevention policies* | DLP-01..05 |
| DSPM for AI activity collection | Up to 24 hours after agent interaction | Microsoft Learn — *Microsoft Purview DSPM for AI* | DRIFT-01, DRIFT-03, AUDIT-01, NEG-01 |
| Unified Audit Log ingestion (most workloads) | Up to 60 minutes; up to 24 hours for some workloads | Microsoft Learn — *Search the audit log in the Purview portal* | UAL-01..04, AUDIT-01, NEG-01..04 |
| Microsoft Entra Access Reviews completion | Configurable (default 1 day, 1 week, 2 weeks, 1 month) | Microsoft Learn — *Create an access review* | APR-04 |
| SharePoint Restricted Search / RCD index latency | Up to 72 hours after configuration change | Microsoft Learn — *Restricted SharePoint Search* | SCOPE-02, SCOPE-03 |
| Copilot Studio knowledge source re-index | Up to 60 minutes for incremental, 24 hours for full | Microsoft Learn — *Add knowledge to your agent* | SCOPE-01, SCOPE-03, DRIFT-01 |
| Microsoft Graph `oauth2PermissionGrants` reflection of consent | Near-real-time (under 5 minutes) | Microsoft Learn — *oauth2PermissionGrants resource* | OAUTH-01, OAUTH-02 |
| Defender for Cloud Apps alert generation | Up to 60 minutes from signal | Microsoft Learn — *Investigate alerts in Defender for Cloud Apps* | DRIFT-04 |

**Window-aware retry policy.** The validator (§6.2) supports a `-WaitForWindow` switch that re-runs each test after its documented window has elapsed if the first attempt returns `Skip` due to "signal not yet visible." This avoids false-fail findings on tests that simply ran too quickly after the provoking action.

---

## §4 Test catalog

The 37 tests below form the auditable core of Control 1.14. Each test follows the canonical 7-field structure (Objective · Preconditions · Steps · Expected · Pass criteria · Audit assertion · Evidence collected) and is named `1.14-{FAMILY}-{NN}` to support paged search and cross-control reuse. Test IDs are stable; if a test is retired, its ID is not reused.

### LIC — License and role separation

#### 1.14-LIC-01 — Power Platform + Copilot Studio + Purview DSPM for AI entitlement attested per tenant

**Objective.** Establish the regulatory baseline that the tenant is licensed to operate the controls Control 1.14 depends on.

**Preconditions.** PRE-01 passed; access to billing portal and Purview portal.

**Steps.**

1. Export `Get-AdminPowerAppEnvironment | Where-Object {$_.EnvironmentType -eq 'Managed'}` and confirm at least one Managed Environment per zone.
2. Capture the Microsoft 365 license assignments for the three test users (PRE-07).
3. Capture the DSPM for AI entitlement screen (Purview portal > DSPM for AI > Settings).

**Expected.** Each test user is licensed for the SKU required by its zone; at least one Managed Environment is present per zone in scope; DSPM for AI shows entitled.

**Pass criteria.** Three license rows present; ≥1 Managed Environment per zone; DSPM for AI screenshot captured.

**Audit assertion.** "Tenant entitlement to Power Platform Managed Environments, Copilot Studio agent governance, and Purview DSPM for AI was confirmed on `{utcDate}`."

**Evidence collected.** `1.14-LIC-01_managed-envs.json`, `1.14-LIC-01_user-licenses.csv`, `1.14-LIC-01_dspm-entitlement.png`.

#### 1.14-LIC-02 — Role separation: Power Platform Admin ≠ SharePoint Admin ≠ Purview Compliance Admin ≠ AI Governance Lead

**Objective.** Confirm SoD for the four roles whose combined privilege would defeat Control 1.14.

**Preconditions.** PRE-02 passed.

**Steps.**

1. Pull `Get-MgRoleManagementDirectoryRoleAssignment` for the four canonical role definitions.
2. For each principal in the union, list which of the four roles it holds.
3. Any principal in ≥2 roles is a finding; document any approved exception with CISO sign-off and link to the issues register.

**Expected.** No principal in ≥2 of the four canonical roles, except documented exceptions.

**Pass criteria.** Distinct-principal report present; exceptions table empty or fully signed.

**Audit assertion.** "Segregation of duties verified across the four canonical Control 1.14 roles on `{utcDate}` for tenant `{tenantId}`."

**Evidence collected.** `1.14-LIC-02_distinct-principals.csv`, `1.14-LIC-02_exceptions.json`.


### UAL — Unified Audit Log enablement and event flow

#### 1.14-UAL-01 — UAL enabled and required workloads flowing

**Objective.** Confirm UAL is enabled and the four workloads required by Control 1.14 (`MicrosoftCopilotStudio`, `PowerPlatformConnector` / `MicrosoftFlow`, `PowerAppsPlan`, `SharePoint`) are returning events in the last 7 days.

**Preconditions.** PRE-04 passed; Exchange Online PowerShell connected.

**Steps.**

1. Run `Search-UnifiedAuditLog` per workload as in PRE-04 §4 with `-ResultSize 100` and a 7-day window.
2. Persist each result set to CSV.
3. Confirm at least one row per workload.

**Expected.** Every required workload returns ≥1 row.

**Pass criteria.** Four CSVs present; row counts logged.

**Audit assertion.** "UAL is enabled and ingesting events from the four workloads required by Control 1.14 on `{utcDate}`."

**Evidence collected.** `1.14-UAL-01_workload-{name}.csv` (4 files).

#### 1.14-UAL-02 — UAL emits `Consent to application` for each new connector authorization

**Objective.** Confirm UAL captures OAuth consent grants so OAUTH-01/02 have an audit trail.

**Preconditions.** UAL-01 passed; an unconsented test connector available.

**Steps.**

1. From the test Z2 agent, attach a new connector that requires user consent (e.g., a tenant-internal Microsoft Graph connector).
2. Wait up to 60 minutes (UAL ingestion window per §3).
3. Run `Search-UnifiedAuditLog -Operations 'Consent to application' -StartDate (Get-Date).AddHours(-2) -EndDate (Get-Date)`.

**Expected.** At least one `Consent to application` row referencing the test app and test user.

**Pass criteria.** Row present; row export persisted; test user matches PRE-07 identity.

**Audit assertion.** "UAL emits `Consent to application` for new connector authorizations on `{utcDate}`."

**Evidence collected.** `1.14-UAL-02_consent.csv`.

#### 1.14-UAL-03 — UAL emits `ConnectorAdded` (Power Platform) for connector attached to an agent

**Objective.** Confirm UAL captures the Power Platform side of the connector-attachment event.

**Preconditions.** UAL-01 passed.

**Steps.**

1. From Copilot Studio, attach a connector to the test Z2 agent (re-use UAL-02 if convenient).
2. Wait per §3.
3. Run `Search-UnifiedAuditLog -RecordType PowerPlatformConnector -Operations 'ConnectorAdded' -StartDate (Get-Date).AddHours(-2) -EndDate (Get-Date)`.

**Expected.** At least one `ConnectorAdded` row referencing the test agent and connector.

**Pass criteria.** Row present and references the agent ID from the Control 1.2 registry.

**Audit assertion.** "UAL captures `ConnectorAdded` for Copilot Studio agents on `{utcDate}`."

**Evidence collected.** `1.14-UAL-03_connector-added.csv`.

#### 1.14-UAL-04 — UAL emits `AgentKnowledgeUpdated` / `AgentKnowledgeAdded` when knowledge source changes

**Objective.** Confirm UAL captures the grounding-scope side of the change-management event.

**Preconditions.** UAL-01 passed.

**Steps.**

1. From Copilot Studio, add a new SharePoint document library knowledge source to the test Z3 agent.
2. Wait per §3.
3. Run `Search-UnifiedAuditLog -RecordType MicrosoftCopilotStudio -Operations 'AgentKnowledgeAdded','AgentKnowledgeUpdated' -StartDate (Get-Date).AddHours(-2) -EndDate (Get-Date)`.

**Expected.** At least one row referencing the test agent and the new knowledge source URL.

**Pass criteria.** Row present; URL matches the seeded change.

**Audit assertion.** "UAL captures grounding-scope changes via `AgentKnowledgeAdded` / `AgentKnowledgeUpdated` on `{utcDate}`."

**Evidence collected.** `1.14-UAL-04_knowledge-updated.csv`.

### INV — Per-agent data-access inventory

#### 1.14-INV-01 — Machine-readable per-agent data-access inventory exists for 100% of registered agents

**Objective.** Confirm that the per-agent data-access inventory (`agent-inventory.json` or `.csv`) exists, is machine-readable, and covers every agent in the Control 1.2 registry.

**Preconditions.** Control 1.2 agent registry export (`agents-registry.json`); inventory artifact location agreed in Control 1.2.

**Steps.**

1. Pull the Control 1.2 agent registry as `agents-registry.json`.
2. Pull the inventory as `agent-inventory.json`.
3. Run a left-join: every agent ID in the registry must appear in the inventory; the inventory must list at least one `(datasource, justification)` row per agent.

**Expected.** Set difference `registry \ inventory` is empty.

**Pass criteria.** Diff report empty.

**Audit assertion.** "Per-agent data-access inventory exists for 100% of agents in the Control 1.2 registry on `{utcDate}`."

**Evidence collected.** `1.14-INV-01_diff-report.csv`, `1.14-INV-01_inventory.json`.

#### 1.14-INV-02 — Each `(agent, datasource)` row has documented business justification, data classification, and zone

**Objective.** Confirm minimum required metadata per inventory row.

**Preconditions.** INV-01 passed.

**Steps.**

1. Validate each inventory row against the schema in §6.1 `agent-inventory-row-v1.json` (required: `agentId`, `dataSourceId`, `dataSourceType`, `businessJustification`, `dataClassification`, `zone`, `requestedBy`, `approvedBy`, `lastReviewedUtc`).
2. List rows missing any required field.

**Expected.** Zero rows fail validation.

**Pass criteria.** Validation report empty.

**Audit assertion.** "All inventory rows include the required minimum metadata on `{utcDate}`."

**Evidence collected.** `1.14-INV-02_schema-validation.json`.

#### 1.14-INV-03 — Inventory references a data classification compatible with Control 1.13 SITs (NPI / MNPI / public)

**Objective.** Cross-reference inventory `dataClassification` values against the Control 1.13 SIT catalog so that a "public" classification cannot be applied to a data source that 1.13 has labelled as containing NPI.

**Preconditions.** INV-02 passed; Control 1.13 SIT inventory export.

**Steps.**

1. Pull the 1.13 SIT-to-data-source map.
2. For each inventory row, look up the data source in the 1.13 map.
3. If the 1.13 map indicates an NPI/MNPI SIT match for the data source and the inventory classification is "public," raise a finding.

**Expected.** Zero classification mismatches.

**Pass criteria.** Cross-reference report empty.

**Audit assertion.** "Inventory data classifications are consistent with Control 1.13 SIT detections on `{utcDate}`."

**Evidence collected.** `1.14-INV-03_cross-ref.csv`.

#### 1.14-INV-04 — Orphaned data sources (in registry but no justification) = 0

**Objective.** Detect data sources attached to agents but without a current `(agent, datasource)` justification row.

**Preconditions.** INV-01 passed.

**Steps.**

1. For each agent, pull the live data-source list from Copilot Studio (knowledge sources) and Power Platform (connector references).
2. For each `(agent, datasource)` pair found live, look up the inventory.
3. Pairs found live but absent from inventory are orphans.

**Expected.** Zero orphans.

**Pass criteria.** Orphan list empty; any pre-existing orphan has an open ticket (NEG-03 will exercise this path).

**Audit assertion.** "Zero orphan `(agent, datasource)` pairs on `{utcDate}`."

**Evidence collected.** `1.14-INV-04_orphan-report.csv`.

### DLP — Connector data loss prevention

#### 1.14-DLP-01 — Tenant DLP policy classifies connectors and covers every Z2/Z3 environment

**Objective.** Confirm a non-default DLP policy exists and is scoped to every Z2/Z3 environment in the tenant.

**Preconditions.** PRE-06 passed.

**Steps.**

1. `Get-DlpPolicy | ConvertTo-Json -Depth 8` and persist.
2. Pull the environment list with `Get-AdminPowerAppEnvironment`.
3. For each Z2/Z3 environment (per Control 1.2 zone tagging), confirm a DLP policy includes it (either by explicit inclusion or by tenant-default scope).

**Expected.** Every Z2/Z3 environment is covered by ≥1 DLP policy that classifies connectors into Business / Non-Business / Blocked.

**Pass criteria.** Coverage report shows 100% of Z2/Z3 environments covered.

**Audit assertion.** "Tenant DLP policy coverage of Z2/Z3 environments is 100% on `{utcDate}`."

**Evidence collected.** `1.14-DLP-01_policies.json`, `1.14-DLP-01_coverage.csv`.

#### 1.14-DLP-02 — Adding a Blocked connector to a Z3 agent is rejected at design time

**Objective.** Demonstrate runtime enforcement of the Blocked classification.

**Preconditions.** DLP-01 passed; a connector currently classified Blocked in the policy applicable to the Z3 environment.

**Steps.**

1. As the Z3 maker, attempt to attach the Blocked connector to `agent-fsi-test-Z3` from Copilot Studio.
2. Capture the rejection screen and any error code.
3. Wait per §3 and search UAL for `DlpPolicyEvaluated` / `PolicyEvaluation` events referencing the attempt.

**Expected.** Design-time rejection; UAL row recording the evaluation.

**Pass criteria.** Rejection screen and UAL evidence both present.

**Audit assertion.** "Blocked connectors are rejected at design time on Z3 agents on `{utcDate}`."

**Evidence collected.** `1.14-DLP-02_rejection.png`, `1.14-DLP-02_dlp-evaluation.csv`.

#### 1.14-DLP-03 — Cross-group data flow at runtime is blocked (Business + Non-Business)

**Objective.** Confirm runtime enforcement of cross-group data flow restrictions.

**Preconditions.** DLP-01 passed; one Business and one Non-Business connector attached to a test Z2 flow.

**Steps.**

1. Trigger the test flow that attempts to read from Business and write to Non-Business.
2. Capture the runtime error (DLP block).
3. Search UAL for the corresponding policy evaluation row.

**Expected.** Runtime block; UAL evidence.

**Pass criteria.** Both pieces of evidence present.

**Audit assertion.** "Cross-group connector data flow is blocked at runtime on `{utcDate}`."

**Evidence collected.** `1.14-DLP-03_runtime-block.png`, `1.14-DLP-03_ual.csv`.

#### 1.14-DLP-04 — Advanced Connector Policies action-level read-only enforced for high-risk certified connectors

**Objective.** Confirm ACP action-level restrictions apply to a high-risk certified connector (e.g., a finance system connector restricted to read-only actions only).

**Preconditions.** DLP-01 passed; one ACP-controlled connector and a defined read-only action set.

**Steps.**

1. Export the ACP via `Get-PowerAppDlpPolicy -PolicyName {acp}` (or the equivalent in the current PowerApps Administration module).
2. Attempt a write action with the test Z2 agent against the ACP-restricted connector.
3. Capture the action-level rejection.

**Expected.** Write rejected; read still permitted.

**Pass criteria.** Both screens captured.

**Audit assertion.** "ACP action-level restrictions enforce read-only on the in-scope connector on `{utcDate}`."

**Evidence collected.** `1.14-DLP-04_acp.json`, `1.14-DLP-04_action-block.png`.

#### 1.14-DLP-05 — Custom connectors and HTTP connectors governed by classic DLP endpoint filtering

**Objective.** Confirm custom and HTTP connectors (which are out of ACP scope) are governed by classic DLP endpoint filtering.

**Preconditions.** DLP-01 passed; a custom connector and an HTTP connector configured.

**Steps.**

1. Inspect the DLP policy for endpoint-filter rules applicable to the custom and HTTP connectors.
2. Attempt a call from the test Z2 agent to a non-allowed endpoint via the HTTP connector.
3. Capture the endpoint-filter block.

**Expected.** Block at the endpoint-filter layer; UAL row recording the evaluation.

**Pass criteria.** Both pieces of evidence present.

**Audit assertion.** "Custom and HTTP connectors are governed by classic DLP endpoint filtering on `{utcDate}`."

**Evidence collected.** `1.14-DLP-05_endpoint-filter.png`, `1.14-DLP-05_ual.csv`.

### OAUTH — Minimum scope, re-consent

#### 1.14-OAUTH-01 — Each agent's connector authorization grants only the minimum OAuth scope set documented in inventory

**Objective.** Confirm OAuth scope minimization at the Microsoft Graph layer.

**Preconditions.** INV-02 passed; Microsoft Graph PowerShell with `DelegatedPermissionGrant.Read.All`.

**Steps.**

1. For each agent, look up the app registration in inventory.
2. Run `Get-MgOauth2PermissionGrant -Filter "clientId eq '{appId}'"` and persist the granted scopes.
3. Diff the granted scopes against the documented minimum scope set.

**Expected.** Granted set ⊆ documented minimum set; any over-grant is a finding.

**Pass criteria.** Diff report empty.

**Audit assertion.** "OAuth scope grants conform to documented minimum sets on `{utcDate}`."

**Evidence collected.** `1.14-OAUTH-01_scope-diff.csv`.

#### 1.14-OAUTH-02 — Re-consent required when an agent requests a broader OAuth scope (no silent expansion)

**Objective.** Confirm that scope expansion triggers a fresh consent flow rather than silently widening the existing grant.

**Preconditions.** OAUTH-01 passed; an app registration permitted to request additional scopes for testing.

**Steps.**

1. From the test Z2 agent, programmatically request a broader scope than initially granted.
2. Observe whether the user is prompted for re-consent (expected) or whether the broader scope is silently accepted.
3. Search UAL for the corresponding `Consent to application` row.

**Expected.** Re-consent prompt fires; UAL row recorded.

**Pass criteria.** Both screen capture and UAL row present.

**Audit assertion.** "OAuth scope expansion requires fresh consent on `{utcDate}`."

**Evidence collected.** `1.14-OAUTH-02_reconsent.png`, `1.14-OAUTH-02_ual.csv`.

### SCOPE — Knowledge source, SharePoint groups, Dataverse roles

#### 1.14-SCOPE-01 — All Z3 agent knowledge sources scoped to a specific document library or folder, not site root

**Objective.** Confirm that no Z3 agent has a knowledge source pointing at a SharePoint site root URL.

**Preconditions.** INV-02 passed.

**Steps.**

1. For each Z3 agent, pull the knowledge sources from Copilot Studio.
2. Parse each URL; if the URL is a site root (path ends at `/sites/{name}` or `/teams/{name}` with no subpath beyond `Shared Documents`), raise a finding.

**Expected.** Zero site-rooted knowledge sources on Z3 agents.

**Pass criteria.** Site-root report empty.

**Audit assertion.** "All Z3 knowledge sources are folder-scoped on `{utcDate}`."

**Evidence collected.** `1.14-SCOPE-01_knowledge-sources.csv`.

#### 1.14-SCOPE-02 — Knowledge sources resolve only to sites included in 4.6 RSS allow-list or RCD decision

**Objective.** Confirm that grounding scope is consistent with the Control 4.6 site-level decision (allow via RSS, exclude via RCD, or document the variance).

**Preconditions.** Control 4.6 RSS allow-list and RCD exclude-list exports.

**Steps.**

1. Pull the 4.6 RSS / RCD lists.
2. For each knowledge source URL on every agent, check that the host site is consistent with the 4.6 decision.

**Expected.** Zero contradictions.

**Pass criteria.** Cross-reference report empty.

**Audit assertion.** "Knowledge source host sites are consistent with Control 4.6 RSS/RCD decisions on `{utcDate}`."

**Evidence collected.** `1.14-SCOPE-02_rss-rcd-cross-ref.csv`.

#### 1.14-SCOPE-03 — Test Z3 agent grounded only on declared folders — query against an out-of-scope folder returns no citation

**Objective.** Demonstrate runtime enforcement of folder-scoped grounding on a test agent.

**Preconditions.** PRE-07 corpus seeded; SCOPE-01 passed for `agent-fsi-test-Z3`.

**Steps.**

1. Issue to `agent-fsi-test-Z3` a query that can only be answered from the `out-of-scope-finance` folder (use a unique seed string).
2. Capture the response and citation list.
3. Confirm no citation references the out-of-scope folder.

**Expected.** Either no citation or citations limited to the in-scope folder.

**Pass criteria.** Citation list contains zero out-of-scope references; response acknowledges lack of source.

**Audit assertion.** "Folder-scoped grounding enforced at runtime on Z3 test agent on `{utcDate}`."

**Evidence collected.** `1.14-SCOPE-03_chat-transcript.json`, `1.14-SCOPE-03_citations.csv`.

#### 1.14-SCOPE-04 — "Agent Access" SharePoint groups exist with minimum-permission templates

**Objective.** Confirm minimum-permission SharePoint group templates are in use for agent access.

**Preconditions.** SharePoint Admin role; PnP.PowerShell connected.

**Steps.**

1. For each Z3 SharePoint site referenced in inventory, run `Get-PnPGroup` and confirm an "Agent Access" group exists with a Read or Restricted-View permission template.
2. Confirm the agent's app registration or user principal is a member.

**Expected.** Group exists; permission template ≤ Read; agent membership recorded.

**Pass criteria.** Group inventory present; templates conform.

**Audit assertion.** "Agent SharePoint access uses minimum-permission group templates on `{utcDate}`."

**Evidence collected.** `1.14-SCOPE-04_groups.json`.

#### 1.14-SCOPE-05 — Dataverse table-level security roles for agent service principals grant only required tables/columns

**Objective.** Confirm Dataverse role minimization for agents that read or write Dataverse data.

**Preconditions.** Power Platform Admin role; Dataverse environments inventoried.

**Steps.**

1. For each agent with a Dataverse data source, export the assigned security role(s).
2. Confirm the role grants only the tables and columns documented in inventory.

**Expected.** Granted ⊆ documented.

**Pass criteria.** Diff empty.

**Audit assertion.** "Dataverse role grants conform to documented minimum on `{utcDate}`."

**Evidence collected.** `1.14-SCOPE-05_dataverse-roles.json`.

### DRIFT — Provoke and detect scope drift

#### 1.14-DRIFT-01 — Provoke scope drift: add new knowledge source to test Z3 agent → alert fires within published latency

**Objective.** Demonstrate that a scope change on a Z3 agent is detected by Purview / Defender within the §3 window.

**Preconditions.** PRE-07 fixtures present; alert rule configured per Control 1.14 portal walkthrough.

**Steps.**

1. As the test Z3 maker, add a new (out-of-scope-for-the-test) document library to `agent-fsi-test-Z3`.
2. Wait per §3 (UAL ingestion + DSPM activity collection windows).
3. Confirm the corresponding alert fires in Defender for Cloud Apps or Microsoft Sentinel.
4. Capture the alert ID, the firing UAL row, and the alert routing.

**Expected.** Alert fires within window; alert ID recorded.

**Pass criteria.** Alert evidence present; firing UAL row matches the provoking change.

**Audit assertion.** "Scope-drift alert fires within published latency on Z3 test agent on `{utcDate}`."

**Evidence collected.** `1.14-DRIFT-01_alert.png`, `1.14-DRIFT-01_alert-id.txt`, `1.14-DRIFT-01_ual.csv`.

#### 1.14-DRIFT-02 — Provoke scope drift: attach new connector to test Z2 agent → manager-approval workflow blocks publish

**Objective.** Confirm Z2 manager-approval gate functions for connector additions.

**Preconditions.** Approval workflow configured per Control 1.14 portal walkthrough.

**Steps.**

1. As the test Z2 maker, attach a new connector to `agent-fsi-test-Z2` and attempt to publish.
2. Confirm publish is blocked pending manager approval; capture the workflow state.
3. As the manager, deny the request; confirm the agent is not published.

**Expected.** Publish blocked; deny recorded.

**Pass criteria.** Workflow run present; deny captured.

**Audit assertion.** "Z2 manager-approval gate blocked an unapproved connector attachment on `{utcDate}`."

**Evidence collected.** `1.14-DRIFT-02_workflow.json`.

#### 1.14-DRIFT-03 — Scope-Drift-Monitor solution ingests last 7-day delta and flags 100% of seeded drifts

**Objective.** Confirm the companion solution `scope-drift-monitor` (FSI-AgentGov-Solutions) detects all seeded drifts in a 7-day window.

**Preconditions.** Solution deployed; seeds for DRIFT-01 and DRIFT-02 present in last 7 days.

**Steps.**

1. Run the solution's reconciliation job manually.
2. Confirm the run report lists all seeded drifts.

**Expected.** 100% of seeded drifts flagged; zero false negatives.

**Pass criteria.** Run report present and complete.

**Audit assertion.** "Scope-Drift-Monitor solution flagged 100% of seeded drifts on `{utcDate}`."

**Evidence collected.** `1.14-DRIFT-03_run-report.json`.

#### 1.14-DRIFT-04 — Scope-creep alert routes to AI Governance Lead distribution group (not just Power Platform Admin)

**Objective.** Confirm alert routing reaches the AI Governance Lead, not only the Power Platform Admin.

**Preconditions.** Alert rule from DRIFT-01.

**Steps.**

1. Inspect the alert configuration; confirm the AI Governance Lead distribution group is in the recipient list.
2. Confirm the firing alert from DRIFT-01 produced an entry in the distribution group's mailbox.

**Expected.** Recipient list includes AI Governance Lead group; mailbox entry present.

**Pass criteria.** Both pieces of evidence present.

**Audit assertion.** "Scope-creep alerts route to the AI Governance Lead group on `{utcDate}`."

**Evidence collected.** `1.14-DRIFT-04_recipients.json`, `1.14-DRIFT-04_mailbox.png`.

### APR — Zone approval workflow, access review

#### 1.14-APR-01 — Z1 self-service scope change recorded in audit trail with user attestation

**Objective.** Confirm Z1 self-service path produces an auditable attestation.

**Preconditions.** Z1 maker workspace; self-service attestation form configured.

**Steps.**

1. As the Z1 maker, change the data source on `agent-fsi-test-Z1` and complete the attestation.
2. Confirm an audit row is written referencing the attestation text and user.

**Expected.** Audit row present with attestation reference.

**Pass criteria.** Row captured; attestation text matches the form.

**Audit assertion.** "Z1 self-service scope changes are audited with user attestation on `{utcDate}`."

**Evidence collected.** `1.14-APR-01_attestation.json`.

#### 1.14-APR-02 — Z2 scope change cannot be published without manager approval

**Objective.** Re-confirm DRIFT-02 from the approval-workflow angle (positive: approve path also works).

**Preconditions.** DRIFT-02 fixtures.

**Steps.**

1. Submit a Z2 scope change.
2. As the manager, approve the request; confirm publish proceeds.
3. Capture the approval record and the resulting publish event.

**Expected.** Approve path completes; UAL records the change.

**Pass criteria.** Approval and UAL evidence present.

**Audit assertion.** "Z2 scope changes require and complete with manager approval on `{utcDate}`."

**Evidence collected.** `1.14-APR-02_approval.json`, `1.14-APR-02_publish.csv`.

#### 1.14-APR-03 — Z3 scope change requires CISO (or designated AI Governance approver) approval and records justification

**Objective.** Confirm Z3 elevated-approval path.

**Preconditions.** Z3 approval workflow configured with CISO or designated approver.

**Steps.**

1. Submit a Z3 scope change with a documented justification.
2. As the approver, approve with comments.
3. Confirm the approval record includes the justification and approver identity.

**Expected.** Approval recorded with justification.

**Pass criteria.** Approval record present and complete.

**Audit assertion.** "Z3 scope changes require CISO-tier approval with documented justification on `{utcDate}`."

**Evidence collected.** `1.14-APR-03_approval.json`.

#### 1.14-APR-04 — Quarterly (Z2) / monthly (Z3) access review completed within window, with documented decisions and revocations

**Objective.** Confirm Microsoft Entra Access Review cadence and outcome capture.

**Preconditions.** Access reviews configured per Control 1.14 portal walkthrough.

**Steps.**

1. Pull the most recent completed access review for each Z2 and Z3 agent group.
2. Confirm review completed within its configured window.
3. Confirm decisions and revocations are recorded.

**Expected.** All in-window reviews completed; decisions captured.

**Pass criteria.** Review export present; revocations executed where decided.

**Audit assertion.** "Access reviews completed within window with documented decisions on `{utcDate}`."

**Evidence collected.** `1.14-APR-04_reviews.json`.

### AUDIT — UAL reconciliation

#### 1.14-AUDIT-01 — End-to-end reconciliation: every test in §2 / §4 produces ≥1 UAL row, paged search for 90-day window

**Objective.** Confirm that the verification harness itself is auditable: every provoking action in §2 / §4 produces at least one UAL row that can be paged retrieved over a 90-day window without exceeding the 50,000-row paged cap.

**Preconditions.** All §2 and §4 tests run within the last 90 days.

**Steps.**

1. Run `Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-90) -EndDate (Get-Date) -SessionId "1.14-AUDIT-01" -SessionCommand ReturnLargeSet -ResultSize 5000` and continue until empty.
2. For each test ID, look up the expected UAL row using the test's documented operation/recordtype filter.
3. Build a reconciliation report: test ID × found-or-not × UAL row reference.

**Expected.** 100% of tests have ≥1 UAL row.

**Pass criteria.** Reconciliation report has zero "not found."

**Audit assertion.** "Verification harness produces auditable UAL evidence for 100% of tests on `{utcDate}`."

**Evidence collected.** `1.14-AUDIT-01_reconciliation.csv`, `1.14-AUDIT-01_paged-results.csv`.

### NEG — Negative tests

#### 1.14-NEG-01 — Out-of-scope user with no agent role does NOT appear in agent UAL events

**Objective.** Confirm UAL noise is not falsely attributing events to uninvolved users.

**Preconditions.** A user with no agent role; UAL-01 passed.

**Steps.**

1. From the test agents' UAL, filter for the out-of-scope user identity over a 7-day window.
2. Confirm zero rows returned.

**Expected.** Zero rows.

**Pass criteria.** Empty result.

**Audit assertion.** "UAL does not attribute agent events to out-of-scope users on `{utcDate}`."

**Evidence collected.** `1.14-NEG-01_empty-result.txt`.

#### 1.14-NEG-02 — Z1 control-arm agent does NOT trigger Z3 scope-drift alert

**Objective.** Confirm scope-drift alerts are tuned to zone and not firing globally.

**Preconditions.** DRIFT-01 alert rule.

**Steps.**

1. Provoke a scope change on `agent-fsi-test-Z1` analogous to DRIFT-01.
2. Confirm the Z3-scoped alert does not fire (Z1 cadence may produce a different, lower-severity alert; capture either outcome).

**Expected.** Z3 alert does not fire on Z1 change.

**Pass criteria.** Alert dashboard shows no Z3 alert from the Z1 change.

**Audit assertion.** "Scope-drift alerts are tuned by zone and do not fire globally on `{utcDate}`."

**Evidence collected.** `1.14-NEG-02_alert-dashboard.png`.

#### 1.14-NEG-03 — Removing the only justification row for `(agent, datasource)` triggers ticket / alert (orphan detection)

**Objective.** Confirm orphan detection (INV-04) triggers a workflow.

**Preconditions.** INV-04 passed; orphan-detection workflow configured.

**Steps.**

1. In a test inventory branch, delete the only justification row for a test `(agent, datasource)` pair.
2. Run the orphan detection job.
3. Confirm a ticket or alert is generated.

**Expected.** Ticket created; orphan reported.

**Pass criteria.** Ticket reference captured.

**Audit assertion.** "Orphan detection triggers a tracked workflow on `{utcDate}`."

**Evidence collected.** `1.14-NEG-03_ticket.json`.

#### 1.14-NEG-04 — Disabled / decommissioned agent retains evidence (no silent purge) per FINRA 4511 / SEC 17a-4

**Objective.** Confirm decommissioning preserves the evidence pack for the retention period.

**Preconditions.** A decommissioned test agent; evidence storage in WORM-compliant location.

**Steps.**

1. Decommission a test Z2 agent per Control 1.17 lifecycle steps.
2. Confirm the evidence pack still exists in WORM storage.
3. Confirm retention metadata indicates the 6-year hold per FINRA 4511 / SEC 17a-4(f).

**Expected.** Evidence intact; retention metadata correct.

**Pass criteria.** Evidence present; retention attribute confirmed.

**Audit assertion.** "Decommissioning preserves Control 1.14 evidence under FINRA 4511 / SEC 17a-4(f) retention on `{utcDate}`."

**Evidence collected.** `1.14-NEG-04_evidence-listing.csv`, `1.14-NEG-04_retention-metadata.json`.

### IR — Incident response

#### 1.14-IR-01 — Tabletop: scope-creep finding on Z3 customer-facing agent → containment, root cause, customer-notification gate

**Objective.** Exercise the AI Incident Response playbook for a Z3 scope-creep finding and confirm the SEC Reg S-P 30-day customer-notification clock is correctly evaluated.

**Preconditions.** AI Incident Response playbook published; tabletop participants identified (CISO, CRO, AI Governance Lead, Compliance Officer, General Counsel observer).

**Steps.**

1. Convene the tabletop using a synthetic finding from DRIFT-01 (assume real customer NPI was groundable for 36 hours before detection).
2. Walk through containment, root cause analysis, and the SEC Reg S-P notification gate (the 30-day clock under the 2024 amendments runs from determination of unauthorized access; document the determination point).
3. Capture the after-action report including: timeline, decisions, and notification determination.

**Expected.** After-action report produced; notification determination point documented; gaps logged into the issues register.

**Pass criteria.** After-action report signed by CISO and CRO.

**Audit assertion.** "Scope-creep tabletop on a Z3 customer-facing agent was conducted on `{utcDate}` with `{n}` gaps logged."

**Evidence collected.** `1.14-IR-01_after-action-report.pdf`, `1.14-IR-01_timeline.csv`.

---


## §6 Evidence pack

### §6.1 Evidence manifest schema

The evidence manifest is a JSON document conforming to `evidence-manifest-v1.json`. Each verification run produces exactly one manifest, hashed with SHA-256 and stored alongside the evidence files. Manifests are immutable; a re-run produces a new manifest with a new `generatedUtc`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fsi-agentgov/schemas/evidence-manifest-v1.json",
  "type": "object",
  "required": ["controlId", "tenantId", "zone", "cloud", "generatedUtc", "files"],
  "properties": {
    "controlId":    { "const": "1.14" },
    "tenantId":     { "type": "string", "format": "uuid" },
    "zone":         { "enum": ["Z1", "Z2", "Z3"] },
    "cloud": { "const": "Commercial" },
    "generatedUtc": { "type": "string", "format": "date-time" },
    "files": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "sizeBytes", "sha256", "capturedUtc", "testId"],
        "properties": {
          "path":        { "type": "string" },
          "sizeBytes":   { "type": "integer", "minimum": 0 },
          "sha256":      { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
          "capturedUtc": { "type": "string", "format": "date-time" },
          "testId":      { "type": "string", "pattern": "^1\\.14-(LIC|UAL|INV|DLP|OAUTH|SCOPE|DRIFT|APR|AUDIT|NEG|IR|PRE)-\\d{2}$" }
        }
      }
    }
  }
}
```

A companion schema `agent-inventory-row-v1.json` validates the per-row inventory shape used by INV-02:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fsi-agentgov/schemas/agent-inventory-row-v1.json",
  "type": "object",
  "required": [
    "agentId", "dataSourceId", "dataSourceType",
    "businessJustification", "dataClassification", "zone",
    "requestedBy", "approvedBy", "lastReviewedUtc"
  ],
  "properties": {
    "agentId":               { "type": "string" },
    "dataSourceId":          { "type": "string" },
    "dataSourceType":        { "enum": ["SharePoint", "OneDrive", "Dataverse", "Connector", "HTTP", "Custom"] },
    "businessJustification": { "type": "string", "minLength": 32 },
    "dataClassification":    { "enum": ["Public", "Internal", "Confidential", "NPI", "MNPI"] },
    "zone":                  { "enum": ["Z1", "Z2", "Z3"] },
    "requestedBy":           { "type": "string", "format": "email" },
    "approvedBy":            { "type": "string", "format": "email" },
    "lastReviewedUtc":       { "type": "string", "format": "date-time" }
  }
}
```

### §6.2 Validator (PowerShell)

The validator below is the canonical harness for Control 1.14. Drop into `assessment/collectors/Verify-Control-1.14.ps1`. The skeleton enforces module pinning, runs each test family, emits one JSON line per test, and writes a SHA-256 manifest of evidence files. Real implementations of each `Test-*` function should be added incrementally; the skeleton fails-closed on `Skip` so missing implementations cannot be silently passed when invoked with `-Strict`.

> **Note.** The function names below use periods (e.g., `Test-1.14-LIC-01`). PowerShell tolerates this in function names and the form is preserved here for documentation traceability against the test ID. If your style guide forbids periods in identifiers, rename to `Test-1_14_LIC_01` and adjust the runner regex.

```powershell
#Requires -Version 7.4
<#
.SYNOPSIS
  Control 1.14 — Data Minimization and Agent Scope Control verification harness.
.DESCRIPTION
  Runs the 37-test catalog against a target tenant + zone, emits NDJSON results
  and a SHA-256 evidence manifest conformant with evidence-manifest-v1.json.
  Fail-closed: any Skip or unhandled exception with -Strict produces exit code 2.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $TenantId,
    [Parameter(Mandatory)] [ValidateSet('Z1','Z2','Z3')] [string] $Zone,
    [Parameter(Mandatory)] [string] $EnvironmentId,
    [Parameter(Mandatory)] [string] $EvidencePath,
    [string] $Cloud = 'Commercial',
    [string[]] $TestFilter,
    [switch] $Strict,
    [switch] $WaitForWindow
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# --- Module pinning (1.14-PRE-05) -----------------------------------------
$RequiredModules = @{
    'Microsoft.PowerApps.Administration.PowerShell' = '2.0.200'
    'Microsoft.Online.SharePoint.PowerShell'        = '16.0.25513.12000'
    'PnP.PowerShell'                                = '2.12.0'
    'ExchangeOnlineManagement'                      = '3.5.0'
    'Microsoft.Graph.Authentication'                = '2.20.0'
    'Microsoft.Graph.Identity.SignIns'              = '2.20.0'
    'Microsoft.Graph.Applications'                  = '2.20.0'
}
foreach ($m in $RequiredModules.Keys) {
    $have = Get-Module -ListAvailable -Name $m |
            Where-Object { $_.Version -ge [Version]$RequiredModules[$m] } |
            Select-Object -First 1
    if (-not $have) { throw "Module $m >= $($RequiredModules[$m]) required (1.14-PRE-05)." }
}

# --- Result emitter --------------------------------------------------------
$Results = New-Object System.Collections.Generic.List[object]
function Emit-Result {
    param(
        [Parameter(Mandatory)] [string] $TestId,
        [Parameter(Mandatory)] [ValidateSet('Pass','Fail','Skip','Error')] [string] $Status,
        [string] $Detail = '',
        [string[]] $EvidenceFiles = @()
    )
    $Results.Add([pscustomobject]@{
        testId        = $TestId
        zone          = $Zone
        cloud         = $Cloud
        tenantId      = $TenantId
        environmentId = $EnvironmentId
        status        = $Status
        detail        = $Detail
        evidenceFiles = $EvidenceFiles
        timestampUtc  = (Get-Date).ToUniversalTime().ToString('o')
    }) | Out-Null
}

# --- Test family stubs (implement per §4 of the playbook) -----------------
function Test-1.14-PRE-01 { Emit-Result -TestId '1.14-PRE-01' -Status 'Skip' -Detail 'TODO: license entitlement attested' }
function Test-1.14-PRE-02 { Emit-Result -TestId '1.14-PRE-02' -Status 'Skip' -Detail 'TODO: role separation' }
function Test-1.14-PRE-04 { Emit-Result -TestId '1.14-PRE-04' -Status 'Skip' -Detail 'TODO: UAL enabled and ingesting' }
function Test-1.14-PRE-05 { Emit-Result -TestId '1.14-PRE-05' -Status 'Skip' -Detail 'TODO: module pinning verified' }
function Test-1.14-PRE-06 { Emit-Result -TestId '1.14-PRE-06' -Status 'Skip' -Detail 'TODO: two-portal precondition' }
function Test-1.14-PRE-07 { Emit-Result -TestId '1.14-PRE-07' -Status 'Skip' -Detail 'TODO: named test fixtures' }

function Test-1.14-LIC-01 { Emit-Result -TestId '1.14-LIC-01' -Status 'Skip' -Detail 'TODO: PPAC + Purview DSPM-for-AI entitlement' }
function Test-1.14-LIC-02 { Emit-Result -TestId '1.14-LIC-02' -Status 'Skip' -Detail 'TODO: Graph role-assignment SoD export' }

function Test-1.14-UAL-01 { Emit-Result -TestId '1.14-UAL-01' -Status 'Skip' -Detail 'TODO: Search-UnifiedAuditLog -RecordType MicrosoftCopilotStudio,PowerPlatformConnector,SharePoint last 7d' }
function Test-1.14-UAL-02 { Emit-Result -TestId '1.14-UAL-02' -Status 'Skip' -Detail 'TODO: filter Operations -eq "Consent to application"' }
function Test-1.14-UAL-03 { Emit-Result -TestId '1.14-UAL-03' -Status 'Skip' -Detail 'TODO: filter Operations -eq ConnectorAdded' }
function Test-1.14-UAL-04 { Emit-Result -TestId '1.14-UAL-04' -Status 'Skip' -Detail 'TODO: filter Operations -in AgentKnowledgeUpdated,AgentKnowledgeAdded' }

function Test-1.14-INV-01 { Emit-Result -TestId '1.14-INV-01' -Status 'Skip' -Detail 'TODO: diff inventory.json vs 1.2 agent registry' }
function Test-1.14-INV-02 { Emit-Result -TestId '1.14-INV-02' -Status 'Skip' -Detail 'TODO: JSON Schema validate inventory rows' }
function Test-1.14-INV-03 { Emit-Result -TestId '1.14-INV-03' -Status 'Skip' -Detail 'TODO: cross-ref 1.13 SIT mapping' }
function Test-1.14-INV-04 { Emit-Result -TestId '1.14-INV-04' -Status 'Skip' -Detail 'TODO: detect orphan data sources' }

function Test-1.14-DLP-01 { Emit-Result -TestId '1.14-DLP-01' -Status 'Skip' -Detail 'TODO: Get-DlpPolicy + environment coverage' }
function Test-1.14-DLP-02 { Emit-Result -TestId '1.14-DLP-02' -Status 'Skip' -Detail 'TODO: blocked-connector design-time rejection' }
function Test-1.14-DLP-03 { Emit-Result -TestId '1.14-DLP-03' -Status 'Skip' -Detail 'TODO: cross-group runtime block' }
function Test-1.14-DLP-04 { Emit-Result -TestId '1.14-DLP-04' -Status 'Skip' -Detail 'TODO: ACP action-level read-only' }
function Test-1.14-DLP-05 { Emit-Result -TestId '1.14-DLP-05' -Status 'Skip' -Detail 'TODO: custom/HTTP connector endpoint filter' }

function Test-1.14-OAUTH-01 { Emit-Result -TestId '1.14-OAUTH-01' -Status 'Skip' -Detail 'TODO: oauth2PermissionGrants diff' }
function Test-1.14-OAUTH-02 { Emit-Result -TestId '1.14-OAUTH-02' -Status 'Skip' -Detail 'TODO: re-consent on broader scope' }

function Test-1.14-SCOPE-01 { Emit-Result -TestId '1.14-SCOPE-01' -Status 'Skip' -Detail 'TODO: assert folder-scoped knowledge sources' }
function Test-1.14-SCOPE-02 { Emit-Result -TestId '1.14-SCOPE-02' -Status 'Skip' -Detail 'TODO: cross-ref 4.6 RSS/RCD decision' }
function Test-1.14-SCOPE-03 { Emit-Result -TestId '1.14-SCOPE-03' -Status 'Skip' -Detail 'TODO: out-of-scope query returns no citation' }
function Test-1.14-SCOPE-04 { Emit-Result -TestId '1.14-SCOPE-04' -Status 'Skip' -Detail 'TODO: Get-PnPGroup minimum-permission template' }
function Test-1.14-SCOPE-05 { Emit-Result -TestId '1.14-SCOPE-05' -Status 'Skip' -Detail 'TODO: Dataverse role table/column scope' }

function Test-1.14-DRIFT-01 { Emit-Result -TestId '1.14-DRIFT-01' -Status 'Skip' -Detail 'TODO: provoke + assert alert' }
function Test-1.14-DRIFT-02 { Emit-Result -TestId '1.14-DRIFT-02' -Status 'Skip' -Detail 'TODO: manager-approval gate' }
function Test-1.14-DRIFT-03 { Emit-Result -TestId '1.14-DRIFT-03' -Status 'Skip' -Detail 'TODO: scope-drift-monitor delta ingest' }
function Test-1.14-DRIFT-04 { Emit-Result -TestId '1.14-DRIFT-04' -Status 'Skip' -Detail 'TODO: alert recipient = AI Gov Lead group' }

function Test-1.14-APR-01 { Emit-Result -TestId '1.14-APR-01' -Status 'Skip' -Detail 'TODO: Z1 self-service audit row' }
function Test-1.14-APR-02 { Emit-Result -TestId '1.14-APR-02' -Status 'Skip' -Detail 'TODO: Z2 manager-approval enforced' }
function Test-1.14-APR-03 { Emit-Result -TestId '1.14-APR-03' -Status 'Skip' -Detail 'TODO: Z3 CISO approval + justification' }
function Test-1.14-APR-04 { Emit-Result -TestId '1.14-APR-04' -Status 'Skip' -Detail 'TODO: cadence access-review completion' }

function Test-1.14-AUDIT-01 { Emit-Result -TestId '1.14-AUDIT-01' -Status 'Skip' -Detail 'TODO: paged UAL reconciliation' }

function Test-1.14-NEG-01 { Emit-Result -TestId '1.14-NEG-01' -Status 'Skip' -Detail 'TODO: out-of-scope user no events' }
function Test-1.14-NEG-02 { Emit-Result -TestId '1.14-NEG-02' -Status 'Skip' -Detail 'TODO: Z1 control-arm no Z3 alert' }
function Test-1.14-NEG-03 { Emit-Result -TestId '1.14-NEG-03' -Status 'Skip' -Detail 'TODO: orphan justification triggers ticket' }
function Test-1.14-NEG-04 { Emit-Result -TestId '1.14-NEG-04' -Status 'Skip' -Detail 'TODO: decommission preserves evidence' }

function Test-1.14-IR-01 { Emit-Result -TestId '1.14-IR-01' -Status 'Skip' -Detail 'TODO: tabletop after-action report' }

# --- Runner ----------------------------------------------------------------
$AllTests = Get-Command -Name 'Test-1.14-*' -CommandType Function
foreach ($t in $AllTests) {
    $id = $t.Name -replace '^Test-',''
    if ($TestFilter -and ($TestFilter -notcontains $id)) { continue }
    try { & $t.Name } catch { Emit-Result -TestId $id -Status 'Error' -Detail $_.Exception.Message }
}

# --- Persist NDJSON --------------------------------------------------------
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ndjson = Join-Path $EvidencePath ("Control-1.14_Results_{0:yyyyMMddHHmmss}.ndjson" -f (Get-Date))
$Results | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 6 } | Set-Content -Path $ndjson -Encoding utf8

# --- SHA-256 manifest (§6.1) ----------------------------------------------
$manifest = Get-ChildItem -Path $EvidencePath -File -Recurse | ForEach-Object {
    [pscustomobject]@{
        path        = (Resolve-Path -LiteralPath $_.FullName -Relative)
        sizeBytes   = $_.Length
        sha256      = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        capturedUtc = (Get-Date).ToUniversalTime().ToString('o')
        testId      = ($_.Name -replace '^(1\.14-[A-Z]+-\d{2}).*','$1')
    }
}
$manifestPath = Join-Path $EvidencePath ("Control-1.14_Manifest_{0:yyyyMMdd}.json" -f (Get-Date))
[pscustomobject]@{
    controlId    = '1.14'
    tenantId     = $TenantId
    zone         = $Zone
    cloud        = $Cloud
    schema       = 'https://fsi-agentgov/schemas/evidence-manifest-v1.json'
    generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
    files        = $manifest
} | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding utf8

# --- Exit code -------------------------------------------------------------
$fail = $Results | Where-Object Status -in @('Fail','Error')
$skip = $Results | Where-Object Status -eq 'Skip'
if ($fail) { exit 1 }
if ($Strict -and $skip) { exit 2 }
exit 0
```

### §6.3 Manifest builder & validator

Validate any existing manifest with the following one-liner (requires `Test-Json` from PowerShell 7.4+):

```powershell
$schema   = Get-Content '.\schemas\evidence-manifest-v1.json' -Raw
$manifest = Get-Content '.\evidence\Control-1.14_Manifest_20260415.json' -Raw
if (-not (Test-Json -Json $manifest -Schema $schema)) {
    throw "Manifest fails schema validation."
}
# Re-hash every file and confirm the recorded SHA-256 matches.
($manifest | ConvertFrom-Json).files | ForEach-Object {
    $live = (Get-FileHash -LiteralPath $_.path -Algorithm SHA256).Hash
    if ($live -ne $_.sha256) {
        throw "Hash mismatch on $($_.path) — recorded $($_.sha256), live $live"
    }
}
```

### §6.4 Artifacts table

| Test ID prefix | Filename pattern | Format | Producer |

| `1.14-PRE-*` | `1.14-PRE-NN_{descriptor}.{json,csv,png}` | JSON / CSV / PNG | Verifier |
| `1.14-LIC-*` | `1.14-LIC-NN_{descriptor}.{json,csv,png}` | JSON / CSV / PNG | Verifier |
| `1.14-UAL-*` | `1.14-UAL-NN_{descriptor}.csv` | CSV | `Search-UnifiedAuditLog` |
| `1.14-INV-*` | `1.14-INV-NN_{descriptor}.{csv,json}` | CSV / JSON | Inventory job |
| `1.14-DLP-*` | `1.14-DLP-NN_{descriptor}.{json,csv,png}` | JSON / CSV / PNG | `Get-DlpPolicy` + screenshot |
| `1.14-OAUTH-*` | `1.14-OAUTH-NN_{descriptor}.{csv,png}` | CSV / PNG | Microsoft Graph |
| `1.14-SCOPE-*` | `1.14-SCOPE-NN_{descriptor}.{csv,json}` | CSV / JSON | Copilot Studio export, PnP |
| `1.14-DRIFT-*` | `1.14-DRIFT-NN_{descriptor}.{json,png,txt}` | JSON / PNG / TXT | Defender / Sentinel |
| `1.14-APR-*` | `1.14-APR-NN_{descriptor}.json` | JSON | Approval workflow |
| `1.14-AUDIT-*` | `1.14-AUDIT-NN_{descriptor}.csv` | CSV | UAL paged |
| `1.14-NEG-*` | `1.14-NEG-NN_{descriptor}.{txt,csv,json,png}` | mixed | mixed |
| `1.14-IR-*` | `1.14-IR-NN_{descriptor}.{pdf,csv}` | PDF / CSV | Tabletop facilitator |
| Manifest | `Control-1.14_Manifest_{yyyyMMdd}.json` | JSON | Validator |
| NDJSON results | `Control-1.14_Results_{yyyyMMddHHmmss}.ndjson` | NDJSON | Validator |

### §6.5 Retention and WORM storage

Evidence supports compliance with the following retention obligations and should be preserved for the longest applicable period. Implementation requires the storage tier to enforce immutability (WORM); organizations should verify their storage configuration meets the regulator's expectations.

| Regulation | Minimum retention | Notes |

| FINRA Rule 4511 (general books and records) | 6 years | Applies to broker-dealer in-scope evidence. |
| SEC 17 CFR 240.17a-4(f) (electronic records) | 6 years (first 2 in easily accessible place) | WORM or audit-trail-equivalent storage required. |
| SEC Reg S-P (2024 amendments) | 6 years | Customer-notification artifacts and incident records. |
| SOX 404 (audit work papers) | 7 years | Where Control 1.14 evidence supports SOX testing. |
| GLBA 501(b) | Per institution policy | Typically 6 years. |
| CCPA §1798.100 | Per institution policy | 24 months minimum for consumer requests. |

Recommended storage: Microsoft 365 Records Management with a retention label `1.14-Evidence-WORM-6yr`, or Azure Blob Storage with immutability policy (legal hold or time-based) configured per FINRA / SEC guidance.

---

## §7 Attestation block

Each verification run produces a signed attestation. The attestation is itself an evidence artifact and is hashed into the manifest. Multi-role sign-off supports compliance with SOX 404 segregation-of-duties expectations and with FINRA 3110 supervisory review.

```text
CONTROL 1.14 — DATA MINIMIZATION AND AGENT SCOPE CONTROL
Verification attestation

Tenant ID:        {tenantId}
Cloud: Commercial
Zone(s) covered:  {Z1  All}
Run window:       {startUtc} → {endUtc}
Manifest SHA-256: {hash}
NDJSON results:   {filename}

Test summary:
  Pass:  {n}
  Fail:  {n}
  Skip:  {n}
  Error: {n}

Findings opened in issues register: {ticket-ids}
Cadence drift since prior run:      {none | family list}

Sign-off (RACI):
  Responsible (Tester)        — AI Governance Lead
    Name:                     ____________________
    Signature / Date (UTC):   ____________________

  Accountable (Reviewer)      — Power Platform Admin OR Purview Compliance Admin
    Name:                     ____________________
    Signature / Date (UTC):   ____________________

  Consulted (Approver)        — CISO (Z3) | Compliance Officer (Z2) | self (Z1)
    Name:                     ____________________
    Signature / Date (UTC):   ____________________

  Informed (Audit)            — Audit Manager
    Name:                     ____________________
    Signature / Date (UTC):   ____________________

I attest that the verification was conducted as described in the playbook
verification-testing.md (v1.4, April 2026), that the evidence pack at the
manifest SHA-256 above is complete, and that any Skip/Fail/Error rows have
been triaged into the issues register with owner and target close date.
```

The attestation block is filed as `Control-1.14_Attestation_{yyyyMMdd}.txt` in the evidence pack and its SHA-256 is included in the manifest. A re-issued attestation creates a new dated file; prior attestations are not modified.

---

## §8 Anti-patterns and known traps

The following anti-patterns have been observed in FSI deployments. Each is paired with the test that detects it, so a verifier can confirm the anti-pattern is not present.

1. **Site-rooted knowledge source on a Z3 agent ("just point it at the team site").** Detected by SCOPE-01.
2. **Wildcard `Sites.Read.All` Graph permission granted to an agent app registration.** Detected by OAUTH-01.
3. **Manual Excel inventory with no schema and no diff-against-registry job.** Detected by INV-01 / INV-02 (will fail schema validation).
4. **DLP policy scoped to default environment only (Z2/Z3 environments uncovered).** Detected by DLP-01 coverage report.
5. **ACP enabled in ACP-only mode without confirming dual-enforcement requirement.** Detected by DLP-04 paired with DLP-05.
6. **Custom connectors assumed to be ACP-governed (they are not — endpoint filter required).** Detected by DLP-05.
7. **Knowledge source pointing at a site governed by 4.6 RSS allow-list mismatch.** Detected by SCOPE-02.
8. **Scope-drift alert routed only to Power Platform Admin (no AI Governance Lead).** Detected by DRIFT-04.
9. **Test-mode policy left on after go-live, suppressing alerts.** Detected by DRIFT-01 (alert will not fire).
10. **Approval workflow bypassed by service principal making changes via Microsoft Graph.** Detected by APR-02 / APR-03 (UAL row will reference the service principal, not the documented approver).
11. **Same identity used for build, approval, and review (no separation of duties).** Detected by LIC-02.
12. **Quarterly review documented but no evidence of revocations.** Detected by APR-04.
13. **UAL search using basic search (10,000-row cap) instead of paged `Search-UnifiedAuditLog -SessionCommand ReturnLargeSet`.** Detected by AUDIT-01 (paged retrieval mandatory).
14. **Evidence stored in a non-WORM location violating SEC 17a-4(f).** Detected by NEG-04 (decommission-preserves-evidence test will surface the storage gap).
15. **SHA-256 manifest generated once at write time and never re-validated.** Detected by §6.3 validator one-liner.
17. **Removing a connector from DLP without first revoking existing agent grants ("zombie OAuth").** Detected by OAUTH-01 diff against documented minimum.
18. **Treating Restricted SharePoint Search as a long-term Z3 boundary** (Microsoft positions RSS as a short-term remediation step pending SharePoint Advanced Management deployment — see Control 4.6). Detected by SCOPE-01 (RSS does not eliminate the requirement to scope knowledge sources to a folder).

---

## §9 Cross-links

- Control [1.2 Agent Registry](../1.2/portal-walkthrough.md) — source of truth for the registered agent set used by INV-01.
- Control [1.4 Connector Governance](../1.4/portal-walkthrough.md) — DLP and ACP configuration tested by DLP-01..05.
- Control [1.10 Conditional Access for Agents](../1.10/portal-walkthrough.md) — identity-side enforcement complementing OAUTH-01.
- Control [1.13 SIT-Aware DLP for Copilot](../1.13/verification-testing.md) — SIT catalog cross-referenced by INV-03.
- Control [1.17 Agent Identity Lifecycle](../1.17/portal-walkthrough.md) — decommissioning steps verified by NEG-04.
- Control [1.18 OAuth Consent Governance](../1.18/portal-walkthrough.md) — consent policy tested by OAUTH-01 / OAUTH-02.
- Control [1.19 Service Principal Hygiene](../1.19/portal-walkthrough.md) — service principal documentation referenced by LIC-02.
- Control [4.6 Grounding Scope Governance](../4.6/portal-walkthrough.md) — RSS / RCD decisions cross-referenced by SCOPE-02.
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) — exercised by IR-01.
- [Shared PowerShell Baseline](../../_shared/powershell-baseline.md) — module pinning and connection patterns used by §6.2 validator.
- Microsoft Learn — *Data loss prevention policies* — <https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention>
- Microsoft Learn — *Connector classification* — <https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification>
- Microsoft Learn — *Advanced Connector Policies* — <https://learn.microsoft.com/en-us/power-platform/admin/connector-action-control>
- Microsoft Learn — *Add knowledge to your agent (SharePoint / OneDrive)* — <https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint>
- Microsoft Learn — *Restricted SharePoint Search* — <https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search>
- Microsoft Learn — *Restricted Content Discovery* — <https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery>
- Microsoft Learn — *Microsoft Purview DSPM for AI* — <https://learn.microsoft.com/en-us/purview/ai-microsoft-purview>
- Microsoft Learn — *Search-UnifiedAuditLog* — <https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog>
- Microsoft Learn — *Audited activities reference* — <https://learn.microsoft.com/en-us/purview/audit-log-activities>
- Microsoft Learn — *Microsoft Graph oauth2PermissionGrants resource* — <https://learn.microsoft.com/en-us/graph/api/resources/oauth2permissiongrant>
- Microsoft Learn — *Power Platform Managed Environments* — <https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview>



---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
