# Control 2.24 — Troubleshooting Playbook

**Companion to:** [Control 2.24 — Agent Feature Enablement and Restriction Governance](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md)

**Sibling playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Verification & Testing](./verification-testing.md)

**Audience:** AI Administrator, Power Platform Admin, Purview Compliance Admin, Security Architect, AI Governance Lead, Compliance Officer, Change Management Team, Microsoft Support liaisons.

**Scope:** Diagnose, contain, and remediate failures of the agent feature catalog, three-surface enablement model (tenant Copilot hub → environment → per-agent), zone-based exposure, sovereign-cloud parity, MCP/connector approval gates, voice/image/preview controls, and the cascading dependencies into MRM (2.6) and supervision (2.12). FINRA Rule 3110 / 3120, SEC Rule 17a-4(f), SEC Reg SCI (242.1001–242.1007), SOX §404 ITGC, GLBA Safeguards Rule, OCC Heightened Standards, **Federal Reserve SR 26-2 (formerly SR 11-7) model risk management**, and CFTC Rule 1.31.

> **Regulatory framing.** Feature toggles are *technical guardrails*. They support — but do not substitute for — the model risk lifecycle (Control 2.6, Fed SR 26-2 (formerly SR 11-7)), supervisory written procedures (Control 2.12, FINRA 3110), or the AI guardrail framework (Control 1.1). Every remediation in this playbook must be paired with the corresponding governance artifact (MRM change record, supervisor attestation, AI risk acceptance) before closure.

> **Sovereign-cloud caveat.** Microsoft 365 GCC, GCC High, and DoD lag commercial Copilot / Microsoft Copilot Studio / MCP / Agent Framework features by **6–18 months**, and a non-trivial subset of capabilities never reach sovereign clouds at all. Maintain a **cloud-segregated feature catalog**, never assume admin-center parity, and document every commercial-only feature as out-of-scope for sovereign tenants in the catalog itself.

---

## §0 Triage Tree

### §0.1 Five-minute decision flow

```
Symptom reported
  │
  ├─► Toggle/setting absent in admin UI?              → §2  TOGGLE-ABSENT
  ├─► Catalog disagrees with live tenant state?       → §3  CATALOG-DRIFT
  ├─► User can do X in surface A, blocked in surface B?→ §4  SURFACE-CONFUSION
  ├─► Unapproved MCP/connector wired to an agent?     → §5  MCP-UNAPPROVED
  ├─► A preview feature went GA / was deprecated and
  │   existing agents now behave differently?         → §6  RETROACTIVE-PREVIEW
  ├─► Disable / restriction request stuck in workflow?→ §7  REVERSE-FLOW-STUCK
  ├─► Zone-2 / Zone-3 agent using a Zone-1-only flag? → §8  ZONE-ESCALATION
  ├─► Sovereign tenant asked for a commercial-only
  │   feature, or parity drift between clouds?        → §9  SOV-PARITY-GAP
  ├─► DLP policy and feature toggle disagree on the
  │   same data flow?                                 → §10 DLP-MISMATCH
  ├─► Voice / image / multimodal feature enabled
  │   without comms-compliance recording path?        → §11 VOICE-IMAGE-GAP
  ├─► Feature change made without MRM change record
  │   (Fed SR 26-2 — formerly SR 11-7) or without model re-validation?       → §12 MRM-CASCADE-BROKEN
  └─► Supervisors unaware that a feature changed,
      WSP / supervision queue not updated?            → §13 SUPERVISOR-UNAWARE
```

### §0.2 Severity matrix

| Severity | Definition | Examples | Initial response SLA |
|---|---|---|---|
| **Sev 1** | Active regulatory exposure, examiner inquiry open, or unapproved data egress in production. | Unapproved MCP server reachable in Z3; voice transcription on without CC capture; deprecated preview emitting unreviewed output to clients. | 15 min — page AI Governance Lead + Compliance Officer + on-call AI Administrator. |
| **Sev 2** | Control degraded but contained; cross-zone or cross-cloud drift; MRM/supervision cascade broken but no client impact yet. | Catalog drift on a Z2 environment; SOV-PARITY-GAP causing GCC-High request backlog; MRM change record missing for a recent toggle. | 4 hrs — AI Administrator + Security Architect; notify AI Governance Lead. |
| **Sev 3** | Single-user friction, documentation gap, low-blast-radius config error. | One Z1 user cannot enable a permitted preview; helper cmdlet returns stale data. | 2 business days — AI Administrator. |

### §0.3 Pre-escalation checklist

Before paging Microsoft Support, the AI Administrator must collect:

- [ ] Tenant ID, environment ID, agent ID(s), affected user UPN(s).
- [ ] Cloud (Commercial / GCC / GCC High / DoD) and region.
- [ ] Surface(s) involved — tenant Copilot hub, environment-level Power Platform Admin Center (PPAC), and/or per-agent Copilot Studio.
- [ ] Output of `Get-Agt224FeatureSnapshot` (see §1.2) attached as JSON.
- [ ] Last three change records from the catalog (see §1.4) covering the affected feature.
- [ ] Confirmation that the issue is reproducible **after** a fresh sign-in (clears stale RBAC/feature-flight cache).
- [ ] MRM (2.6) change record ID, if the affected feature is in scope for model risk.
- [ ] Supervision (2.12) WSP section reference, if the affected feature changes a reviewable surface.

### §0.4 Examiner-artifact preservation

> **Stop-the-press rule.** If an examiner inquiry, internal-audit hold, or legal-hold notice is open against the affected agent, environment, or feature, **do not** flip toggles, delete agents, or rotate credentials before evidence is captured per §22 and §X. SEC Rule 17a-4(f) and CFTC Rule 1.31 require WORM-grade preservation of the configuration state at the time of the inquiry; remediation that overwrites that state is itself a finding.

Capture order: (1) `Get-Agt224FeatureSnapshot -IncludeAuditTrail` to immutable storage, (2) Purview audit export for the affected actors over the inquiry window, (3) PPAC governance-console screenshots (Control 2.25), (4) only then begin remediation.

---

## §1 Diagnostic Data Collection

### §1.1 Helper cmdlet catalog (`Get-Agt224*` / `Set-Agt224*`)

These helpers wrap the underlying Microsoft Graph, Power Platform, Copilot, and Purview endpoints. Definitions live in [`./powershell-setup.md`](./powershell-setup.md); sovereign substitutions in [`../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).

| Cmdlet | Purpose | Primary surface |
|---|---|---|
| `Get-Agt224FeatureSnapshot` | Full three-surface state (tenant + environment + per-agent) for a tenant or scoped environment. | All |
| `Get-Agt224CatalogDiff` | Compares the canonical feature catalog (source of truth) against live tenant state; emits drift report. | All |
| `Get-Agt224ToggleProvenance` | Returns who/when/why for the last N changes to a named toggle, with audit-log correlation IDs. | Tenant + env |
| `Get-Agt224SurfaceMatrix` | Cross-tabulates the same logical capability across tenant Copilot hub, PPAC, and Copilot Studio per-agent. | All |
| `Get-Agt224McpInventory` | Lists every MCP server, connector, and external tool reachable from each agent, with approval status. | Per-agent |
| `Get-Agt224PreviewFeatures` | Enumerates preview / GA-pending features in tenancy, with deprecation timers and retroactive-flip risk. | Tenant + env |
| `Get-Agt224ReverseFlowQueue` | Outstanding *disable / restrict* requests, age, blocking approver, exception expiry. | Workflow |
| `Get-Agt224ZoneAssignment` | Maps environments and agents to Zone 1 / 2 / 3 per Control 2.2; flags zone-feature mismatch. | Env + per-agent |
| `Get-Agt224SovereignParity` | Side-by-side catalog Commercial vs. GCC / GCC High / DoD; flags commercial-only items. | Tenant |
| `Get-Agt224DlpAlignment` | Cross-checks feature toggles against DLP / ACP policies (Control 1.4) for the same data flow. | Tenant + env |
| `Get-Agt224MultimodalSurfaces` | Voice / image / vision / video surfaces enabled, paired against CC capture coverage (Control 1.10). | Per-agent |
| `Get-Agt224MrmCascade` | Joins feature changes against MRM change records (Control 2.6); reports orphaned changes. | Governance |
| `Get-Agt224SupervisorAttestation` | Joins feature changes against supervisor acknowledgement records (Control 2.12 WSP). | Governance |
| `Set-Agt224EmergencyDisable` | Tenant-wide kill-switch for a named feature; requires AI Governance Lead + Compliance Officer co-sign. | Tenant |

### §1.2 Baseline snapshot

```powershell
# Full snapshot, attach to every Sev 1 / Sev 2 ticket
$snap = Get-Agt224FeatureSnapshot -TenantId $TenantId -IncludeAuditTrail -IncludeMcpInventory
$snap | ConvertTo-Json -Depth 10 |
    Out-File "evidence/2.24/E-01_snapshot_$(Get-Date -Format yyyyMMddHHmm).json"
```

> **Hedged language.** A snapshot **supports** examiner response by capturing point-in-time state; it does **not** by itself satisfy the Fed SR 26-2 (formerly SR 11-7) documentation requirement, which lives in the MRM change record (Control 2.6).

### §1.3 Microsoft Graph queries (GQ-01 … GQ-08)

| ID | Endpoint | Returns | Used in pillar |
|---|---|---|---|
| **GQ-01** | `GET /copilot/admin/settings` | Tenant-level Copilot feature flags, web-grounding, plug-in policy. | §2, §3, §6 |
| **GQ-02** | `GET /copilot/admin/agents` | All registered agents with publisher, surface, sensitivity binding. | §3, §4, §8 |
| **GQ-03** | `GET /solutions/virtualAgents/bots?$expand=connectors` | Copilot Studio agents and their connector graph. | §5, §10 |
| **GQ-04** | `GET /security/secureScores/controlProfiles?$filter=startswith(controlName,'Copilot')` | Copilot-related secure-score posture; flags toggle drift. | §3 |
| **GQ-05** | `GET /admin/serviceAnnouncement/messages?$filter=contains(services,'Copilot')` | Message Center items: GA, deprecation, retroactive-flip notices. | §6 |
| **GQ-06** | `GET /identityGovernance/accessReviews/definitions` | Access reviews tied to feature exception groups (researcher / analyst). | §7 |
| **GQ-07** | `GET /informationProtection/policy/labels` | Sensitivity labels referenced by per-agent feature gates. | §10 |
| **GQ-08** | `GET /security/auditLog/queries` | Saved queries used by §22 evidence collection. | §22, §X |

For **GCC / GCC High / DoD**, swap `graph.microsoft.com` for `graph.microsoft.us` (GCC, GCC High) or `dod-graph.microsoft.us` (DoD); see `_shared/powershell-baseline.md` §3.

### §1.4 KQL queries (Microsoft 365 Defender / Sentinel / Purview Audit)

| ID | Source | Purpose |
|---|---|---|
| **KQL-01** | `CloudAppEvents` | Detect toggle changes outside the change-window (catalog drift / unauthorized change). |
| **KQL-02** | `CloudAppEvents` | Per-agent connector additions where ConnectorId not in approved list (§5). |
| **KQL-03** | `OfficeActivity` (`AuditLogs`) | Copilot admin-center setting changes, joined with actor role (AI Administrator vs. Entra Global Admin breakglass). |
| **KQL-04** | `PowerPlatformAdminActivity` | Environment-level feature flips with approver UPN. |
| **KQL-05** | `CloudAppEvents` + `IdentityInfo` | Researcher / Analyst exception-group membership joined to actual feature usage. |
| **KQL-06** | `CommunicationComplianceEvents` | Coverage gap: agents emitting voice/image without a matching CC policy (§11). |

```kusto
// KQL-01 — toggle changes outside the change window
let WindowStart = datetime(2026-04-15T00:00Z);
let WindowEnd   = datetime(2026-04-15T04:00Z);
CloudAppEvents
| where Timestamp between (ago(30d) .. now())
| where ActionType in ("Update Copilot setting", "Update agent feature", "Update environment feature")
| where not(Timestamp between (WindowStart .. WindowEnd))
| project Timestamp, AccountUpn, ActionType, RawEventData
| order by Timestamp desc
```

### §1.5 Evidence Floor (E-01 … E-10)

| Code | Artifact | Format | Retention target | Pillar / runbook |
|---|---|---|---|---|
| **E-01** | Feature snapshot JSON (`Get-Agt224FeatureSnapshot`) | JSON, immutable | 7 yrs (SEC 17a-4 / FINRA 4511) | All |
| **E-02** | Catalog diff report (`Get-Agt224CatalogDiff`) | CSV + JSON | 7 yrs | §3, §9 |
| **E-03** | Toggle provenance log | CSV | 7 yrs | §2, §3, §12 |
| **E-04** | MCP / connector inventory | JSON | 7 yrs | §5, §10 |
| **E-05** | Reverse-flow workflow ticket bundle | PDF + JSON | 7 yrs | §7 |
| **E-06** | Sovereign parity diff | CSV | 7 yrs | §9 |
| **E-07** | DLP-vs-toggle alignment report | CSV | 7 yrs | §10 |
| **E-08** | Multimodal coverage report | CSV | 7 yrs | §11 |
| **E-09** | Post-incident attestation (signed) | PDF + JSON manifest | 7 yrs | §X |
| **E-10** | Examiner / audit response bundle | PDF + manifest, WORM | Per legal-hold scope | §0.4, §14 (RB-01) |

> **Non-substitution.** Evidence in E-01 … E-10 supports examiner response and post-incident attestation. It does **not** satisfy Fed SR 26-2 (formerly SR 11-7) §V (model documentation) or FINRA 3110 supervisory-procedure documentation; those are produced under Controls 2.6 and 2.12 respectively, and must be cross-linked from E-09.

---

## §2 TOGGLE-ABSENT — Expected toggle is missing from the admin UI

### §2.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| AI Administrator cannot find a setting documented in the catalog. | M365 admin → Copilot, PPAC → Copilot governance, Copilot Studio per-agent. | UI version banner older than catalog `min_ui_version`. |
| Toggle visible to Entra Global Admin but not to AI Administrator. | M365 admin center. | RBAC propagation lag or scoped-role gap. |
| Toggle present in Commercial but absent in GCC / GCC High / DoD. | Sovereign tenant. | Cloud parity drift — see §9. |
| Toggle was present last week, missing today. | Any. | Microsoft removed/renamed in a service update — see §6. |

### §2.2 Root-cause matrix

| Cause | Evidence | Resolution path |
|---|---|---|
| Feature not yet rolled out to ring. | `Get-Agt224PreviewFeatures` shows feature in *targeted-release* only. | Wait for ring; or opt environment into targeted release per change-management policy. |
| AI Administrator role missing required permission. | `Get-Agt224ToggleProvenance -ImpersonateRole 'AI Administrator'` returns `Forbidden`. | Add scoped permission (preferred) or temporary Entra Global Admin breakglass with full §X attestation. |
| Sovereign cloud does not carry the feature. | `Get-Agt224SovereignParity` flags `CommercialOnly = $true`. | Document as out-of-scope; see §9. |
| Microsoft renamed / relocated the toggle. | Message Center notice (GQ-05) within 30 days. | Update catalog and references; reconfirm via §3 diff. |
| Tenant on legacy licence SKU. | Entra licence inventory shows missing SKU. | Engage licensing; do **not** enable via unsupported workaround. |

### §2.3 Diagnostic steps

1. Run `Get-Agt224SurfaceMatrix -Feature <FeatureName>`; confirm whether the toggle is expected on the surface in question.
2. Run `Get-Agt224SovereignParity -Feature <FeatureName>` if tenant is sovereign.
3. Pull GQ-05 for the last 60 days for any rename / deprecation message.
4. Have a second admin in a different role re-test (rule out role scoping).
5. Confirm browser locale / Edge profile is not cached on a stale tenant.

### §2.4 Resolution steps

- **If RBAC gap:** request the AI Administrator role be granted the missing scoped permission via the standing change-management ticket; **do not** keep Entra Global Admin assignments active beyond the breakglass window.
- **If ring lag:** open a tracker entry, set the symptom-owner expectation, and check daily until ring reaches the target environment.
- **If sovereign-only absence:** mark the feature in the catalog as `Scope: Commercial` and update the cloud-segregated catalog (§9). Communicate to requesters that the capability **will not be enabled** in the sovereign tenant until Microsoft ships it.
- **If Microsoft rename:** update the catalog entry, retire the old reference, and run §3 to confirm no orphan references remain.

### §2.5 Verification

- [ ] `Get-Agt224SurfaceMatrix` shows the toggle on the expected surface(s).
- [ ] `Get-Agt224ToggleProvenance` returns a non-empty history under the AI Administrator role (no breakglass).
- [ ] Catalog entry updated; E-02 diff is clean for the affected feature.

### §2.6 Cross-references

- [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — governance console as the canonical surface for tenant-level toggles.
- §6 RETROACTIVE-PREVIEW (rename can mask a deprecation).
- §9 SOV-PARITY-GAP (parity is the most common false positive here).

---

## §3 CATALOG-DRIFT — Source-of-truth catalog disagrees with live tenant state

### §3.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Quarterly attestation produces non-zero diff between catalog and live state. | Governance review. | `Get-Agt224CatalogDiff` rows > 0. |
| Toggle flipped without a corresponding catalog change-record. | Audit. | KQL-01 hit outside change window. |
| Two environments meant to be identical have diverged. | Multi-env governance. | `Get-Agt224SurfaceMatrix -Compare env-a,env-b` non-empty. |
| Catalog says "disabled" but Copilot Studio per-agent allows the feature. | Per-agent surface. | See §4 SURFACE-CONFUSION. |

### §3.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| Manual change by an admin outside the change window. | KQL-01 + actor UPN; E-03 provenance. | Roll back, raise change-management exception, re-attest. |
| Microsoft service-side default flip. | GQ-05 message; Microsoft Roadmap entry. | Update catalog to record new Microsoft default; confirm acceptance via AI Governance Lead. |
| Automation drift — IaC pipeline diverges from catalog. | Pipeline diff vs. live state. | Re-converge pipeline; introduce drift-detection job (see §3.4). |
| Per-agent override left in place from a prior incident. | `Get-Agt224FeatureSnapshot -Scope agent` flags override. | Remove override or formalise as documented exception (Control 2.6 acceptance). |

### §3.3 Diagnostic steps

1. `Get-Agt224CatalogDiff -TenantId $TenantId -OutFile evidence/2.24/E-02_diff.csv`.
2. For every row, run `Get-Agt224ToggleProvenance -Feature <name> -Last 10` to identify actor + timestamp.
3. Run KQL-01 across the same window for unauthorized changes.
4. Run KQL-04 to capture environment-level approver UPN per change.

### §3.4 Resolution steps

- For each unauthorized change: roll back, then file a retrospective change-record citing the rollback (do **not** keep an unauthorized state, even if benign — that legitimises future drift).
- For Microsoft service-side flips: update the catalog, attach the GQ-05 message ID as evidence, route through AI Governance Lead for one-line acceptance.
- For pipeline drift: schedule `Get-Agt224CatalogDiff` as a daily job; emit Sev 2 alert when diff > 0.
- For per-agent overrides: route to Control 2.6 (model risk acceptance) or remove.

### §3.5 Verification

- [ ] E-02 diff is empty for the affected scope.
- [ ] Every change in the last 30 days is paired with a change-record (E-03).
- [ ] Daily drift-detection job is green for 7 consecutive days.

### §3.6 Cross-references

- §2 TOGGLE-ABSENT (sometimes a "missing toggle" is just an undetected drift).
- [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — drift that affects model behaviour requires MRM re-validation.
- [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — console as authoritative read surface.

---

## §4 SURFACE-CONFUSION — Same capability, inconsistent state across the three surfaces

### §4.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| User can do X in Copilot chat but is blocked in Copilot Studio agent. | End user. | Tenant Copilot hub allows; per-agent denies. |
| Environment policy denies a connector but per-agent shows it as available. | Maker. | PPAC denies; Copilot Studio shows stale list. |
| Tenant disabled web grounding; agent in environment X still grounds web. | Auditor. | Per-agent override predates the tenant flip. |

### §4.2 Root-cause matrix

The three-surface model (tenant Copilot hub → environment via PPAC → per-agent in Copilot Studio) applies the **most restrictive** rule across surfaces *for new sessions*, but **existing per-agent overrides may persist** until reconciled. Most surface-confusion incidents trace to one of:

| Cause | Evidence | Resolution |
|---|---|---|
| Per-agent override persisting across a tenant disable. | `Get-Agt224SurfaceMatrix -Feature X -ShowOverrides`. | Remove override; or escalate to exception via §7 reverse-flow. |
| Stale UI cache (user has not re-authenticated). | Symptom resolves after sign-out / sign-in. | User re-auth; document as known transient. |
| Environment-level policy not propagated yet. | PPAC change made < 30 min ago. | Wait propagation window; re-test. |
| Two admins changed the same feature concurrently from different surfaces. | Provenance shows two near-simultaneous writes. | Reconcile; add change-window enforcement (Control 2.25). |

### §4.3 Diagnostic steps

1. `Get-Agt224SurfaceMatrix -Feature <name> -Scope tenant,env,agent -ShowOverrides`.
2. For per-agent override: `Get-Agt224ToggleProvenance -Scope agent -AgentId <id>`.
3. Confirm the user re-authenticated post-change.

### §4.4 Resolution steps

- Define and document the **intended winning surface** for the feature in the catalog. Default: tenant disable wins; per-agent overrides require explicit Control 2.6 / 2.12 acceptance.
- Remove or formalise per-agent overrides; if formalising, the override must be logged with the AI Administrator + agent owner + Compliance Officer signatures, and an expiry date.
- Add a daily `Get-Agt224SurfaceMatrix` drift report to the §22 evidence pipeline.

### §4.5 Cross-references

- §3 CATALOG-DRIFT.
- §8 ZONE-ESCALATION (per-agent overrides often escalate effective zone).
- [Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) — orchestration extends surface-confusion across delegating agents.

---

## §5 MCP-UNAPPROVED — Unapproved MCP server / connector wired to an agent

### §5.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Agent calls an MCP server that is not in the approved registry. | Telemetry / DLP alert. | KQL-02 hit. |
| Maker added a connector via Copilot Studio that bypasses ACP (1.4). | DLP alert. | `Get-Agt224McpInventory` flags `ApprovalStatus = Unknown`. |
| Approved MCP server credential rotated; agent continues with old endpoint. | Outage. | Endpoint mismatch in inventory. |
| MCP server reachable in Z3 environment that is meant to be air-gapped. | Audit. | Z3 environment policy violation. |

### §5.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| ACP (Control 1.4) policy not applied to the environment. | `Get-Agt224DlpAlignment` flags missing policy. | Apply ACP; rerun §10. |
| Maker bypassed approval workflow. | KQL-02 + actor UPN. | **Sev 1** — disable agent, audit data flow, raise incident under Control 3.4. |
| MCP registry stale; legitimate server appears unapproved. | Registry diff vs. control plane. | Update registry; document. |
| Connector inherited from a template / solution import. | Solution-import audit. | Strip on import; harden template-import policy (Control 1.2). |

### §5.3 Diagnostic steps

1. `Get-Agt224McpInventory -Scope tenant -Format json | Tee-Object evidence/2.24/E-04_mcp.json`.
2. KQL-02 across the last 30 days; correlate connector adds with maker UPN.
3. For each `ApprovalStatus = Unknown`, identify the data classifications the connector touches (Control 1.4 mapping).
4. Confirm whether any agent has actually invoked the connector (telemetry).

### §5.4 Resolution steps

- **If invocation occurred:** treat as Sev 1. Engage Compliance Officer and Security Architect. Capture E-01 + E-04 to immutable storage **before** disabling. Then disable the connector via `Set-Agt224EmergencyDisable -Scope connector -Id <id>`. Open a Control 3.4 incident.
- **If no invocation yet:** disable the connector binding on the agent, notify the maker, route through the formal MCP approval workflow.
- Refresh the MCP registry; introduce a daily reconciliation job.
- Cascade: ensure ACP (Control 1.4) policy denies *all* unapproved connectors at the environment boundary, not just at the per-agent surface.

### §5.5 Verification

- [ ] `Get-Agt224McpInventory` shows zero `ApprovalStatus = Unknown` rows.
- [ ] ACP policy active on every environment in scope.
- [ ] If Sev 1 was raised: Control 3.4 incident closed; E-09 attestation filed.

### §5.6 Cross-references

- [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — registry as the source of truth.
- [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) — ACP as the enforcement layer.
- [Control 1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md) — MIME boundary for MCP-returned payloads.
- [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — incident path.

---

## §6 RETROACTIVE-PREVIEW — Preview feature went GA / was deprecated; existing agents now behave differently

### §6.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Agent output suddenly different from prior week. | End user / supervisor. | GQ-05 GA-promotion or deprecation message in window. |
| Preview opt-in setting now greyed out (locked at GA default). | Admin. | Catalog `state = preview` but UI shows GA. |
| Deprecated preview feature still bound to a production agent. | Audit. | `Get-Agt224PreviewFeatures -State deprecated` non-empty. |
| Microsoft flipped preview default from off → on for all tenants. | Audit. | KQL-01 service-principal actor. |

### §6.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| GA promotion changed default behaviour. | GQ-05 message. | Re-validate per Control 2.6 (Fed SR 26-2 (formerly SR 11-7) model change). Update catalog. Communicate to supervisors (§13). |
| Preview deprecated; Microsoft removed. | GQ-05 deprecation notice. | Migrate dependent agents *before* removal date; document migration in MRM record. |
| Preview opt-in left enabled past go-live; should have been re-evaluated. | Catalog review history. | Run §X attestation; either accept (with MRM record) or disable. |
| Tenant auto-enrolled into preview without admin consent. | KQL-01 service-principal actor. | Opt out; raise with Microsoft; document. |

### §6.3 Diagnostic steps

1. `Get-Agt224PreviewFeatures -IncludeDeprecationTimers`.
2. For each entry, fetch GQ-05 messages referencing it.
3. Cross-reference with MRM (Control 2.6) for any agent whose risk tier changes as a result.
4. Pull KQL-01 for the timestamp Microsoft flipped a default.

### §6.4 Resolution steps

- For GA promotion that changes model behaviour: **trigger MRM re-validation** (Control 2.6). Until re-validation completes, either disable the GA capability for the affected agent or accept the residual risk in writing through AI Governance Lead.
- For deprecation: build a migration plan with the agent owner; track to the deprecation date; if migration cannot complete, escalate to AI Governance Lead.
- For unsolicited Microsoft default-flip: the *control* is still violated even though Microsoft is the actor — the catalog must be updated, supervisors must be notified, and the change must be explicitly accepted or reverted at the tenant.
- Cascade to §13 SUPERVISOR-UNAWARE.

### §6.5 Verification

- [ ] No deprecated preview feature is bound to a production agent.
- [ ] Every GA promotion in the last 90 days has either an MRM re-validation record or a written risk acceptance.
- [ ] Catalog `state` matches Microsoft Roadmap state for every entry.

### §6.6 Cross-references

- [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — GA-promotion = model change for Fed SR 26-2 (formerly SR 11-7).
- [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — supervisor notification.
- §13 SUPERVISOR-UNAWARE.

---

## §7 REVERSE-FLOW-STUCK — Disable / restrict request stalled in workflow

### §7.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Disable request open for > SLA, no approver action. | Workflow report. | `Get-Agt224ReverseFlowQueue -OlderThan 5d`. |
| Restriction applied at tenant but per-agent override still active. | Auditor. | See §4 SURFACE-CONFUSION. |
| Researcher / Analyst exception expired; access not removed. | Access review. | GQ-06 review overdue. |
| Compliance asked for emergency disable; toggle still on. | Compliance Officer. | Sev 1 — see §1.1 emergency cmdlet. |

### §7.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| Approver out of office, no delegate. | Workflow log. | Activate delegate; escalate to AI Governance Lead. |
| Workflow blocked on missing MRM evidence. | Workflow comments. | Produce Control 2.6 evidence; resume. |
| Exception expiry not auto-enforced. | GQ-06 review state. | Configure access-review auto-removal. |
| Emergency disable not triggered because approval gate too strict. | Workflow definition. | Add break-glass path with co-sign (AI Governance Lead + Compliance Officer); see §X. |

### §7.3 Diagnostic steps

1. `Get-Agt224ReverseFlowQueue -IncludeBlockingApprover -OutFile evidence/2.24/E-05_queue.json`.
2. For each stuck request, identify blocking approver and time-in-queue.
3. For exception-group requests, pull GQ-06 to confirm review state.

### §7.4 Resolution steps

- For SLA-breached approvals: escalate to delegate, then to AI Governance Lead. **Do not** bypass the workflow — bypassing is itself a Sev 2 finding.
- For emergency disables (Sev 1): use `Set-Agt224EmergencyDisable` with both AI Governance Lead and Compliance Officer co-sign captured in E-09. Backfill the workflow record within 24 hrs.
- Configure expiry-driven removal for researcher / analyst exception groups (Control 1.1).
- Quarterly: review the reverse-flow queue and prune.

### §7.5 Cross-references

- [Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) — exception groups governed here.
- [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — workflow surface.
- §X Recovery — emergency-disable attestation.

---

## §8 ZONE-ESCALATION — Zone-2 / Zone-3 agent using a Zone-1-only feature

### §8.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Z2 agent enabled web grounding (Z1-only per zone exposure model). | DLP / audit. | `Get-Agt224ZoneAssignment -ShowMismatch`. |
| Z3 (regulated/SOX) agent has connector to consumer-cloud SaaS. | Audit. | Connector classification < Z3 minimum. |
| Z2 agent escalated to Z3 by ownership change but feature catalog not updated. | Governance review. | Zone re-tagged; features still Z2 defaults. |

### §8.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| Per-agent override left feature on after zone change. | `Get-Agt224SurfaceMatrix -ShowOverrides`. | Remove override or formalise via §7. |
| Environment misclassified in Control 2.2. | 2.2 inventory diff. | Re-classify; cascade feature catalog. |
| Maker explicitly enabled Z1-only feature on a Z2 agent. | Provenance. | Disable; coach maker; route through Control 1.1 publishing-authorisation review. |

### §8.3 Diagnostic steps

1. `Get-Agt224ZoneAssignment -ShowMismatch -OutFile evidence/2.24/E-02_zone_diff.csv`.
2. For each mismatch row, pull `Get-Agt224ToggleProvenance` to identify the actor.
3. Correlate with Control 2.2 environment-tier records.

### §8.4 Resolution steps

- Disable any feature that exceeds the agent's zone exposure ceiling.
- If the feature is genuinely required, **promote the agent's zone** through the formal zone-change workflow (Control 2.2) — do **not** weaken the zone feature ceiling.
- Cascade: a zone change typically triggers MRM (2.6) re-tier and supervisory (2.12) re-coverage; verify both happened.

### §8.5 Cross-references

- [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) — zone definitions.
- §4 SURFACE-CONFUSION.
- §12 MRM-CASCADE-BROKEN.

---

## §9 SOV-PARITY-GAP — Sovereign tenant requesting commercial-only feature, or parity drift

### §9.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Business requests a feature in GCC High that exists only in Commercial. | Intake. | `Get-Agt224SovereignParity` flags `CommercialOnly = $true`. |
| Same agent operates differently in Commercial vs. GCC tenant. | Multi-cloud user. | Surface matrix differs across clouds. |
| Microsoft shipped a feature to GCC; sovereign catalog not updated. | Microsoft Roadmap. | Catalog drift in sovereign cloud — see §3. |
| DoD tenant shows feature as available but cannot enable. | Admin. | Roadmap "rolling out" but tenant not reached. |

### §9.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| Feature is genuinely commercial-only. | Microsoft Roadmap. | Document refusal; offer compensating control. **Do not** mirror via unsupported workaround. |
| Feature shipped to sovereign but catalog not synced. | Roadmap + GQ-05. | Update sovereign catalog; route through change-management. |
| Feature in sovereign-cloud rolling-out state. | Roadmap status. | Wait for ring; do not engage Microsoft for early enablement unless governance accepts the support implications. |
| Cross-cloud agent expectation invalid. | Architecture review. | Redesign to cloud-segregated; do **not** create cross-cloud bridges. |

### §9.3 Diagnostic steps

1. `Get-Agt224SovereignParity -Cloud GCCH -OutFile evidence/2.24/E-06_parity.csv`.
2. Cross-check Microsoft Roadmap entry for the feature; capture URL and date.
3. Confirm cloud assignment of every requesting environment (Control 2.2).

### §9.4 Resolution steps

- For genuinely commercial-only requests: produce a written refusal citing the parity gap, offer the closest sovereign-supported alternative, and capture in the catalog as `Scope: Commercial; SovereignAlternative: <…>`.
- For sync gap: update the sovereign catalog, attach the Roadmap reference as evidence, route through change-management.
- Schedule a monthly `Get-Agt224SovereignParity` report; gate any sovereign feature change on a clean parity check.

### §9.5 Verification

- [ ] Sovereign catalog reconciled to Microsoft Roadmap for sovereign clouds.
- [ ] Every commercial-only refusal has a written record and a compensating control reference.
- [ ] Monthly parity report runs and is reviewed by AI Governance Lead.

### §9.6 Cross-references

- [`../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).
- §3 CATALOG-DRIFT.
- RB-03 (§16) sovereign parity escalation.

---

## §10 DLP-MISMATCH — DLP / ACP policy and feature toggle disagree on the same data flow

### §10.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Feature toggle allows web grounding; DLP blocks the resulting URL fetch. | End user / telemetry. | `Get-Agt224DlpAlignment -Surface grounding` flags conflict. |
| Connector enabled in catalog; ACP (1.4) denies. | Maker. | Approval-status mismatch. |
| Sensitivity-labelled content reaches an agent the catalog says cannot consume it. | Purview. | GQ-07 label binding mismatch. |
| File upload feature on; MIME restriction (1.25) blocks. | End user. | MIME deny logs paired with feature on. |

### §10.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| Toggle and DLP authored by different teams without alignment. | Two change records, same date, divergent. | Reconcile; designate the DLP / ACP layer as authoritative for data-flow decisions; the feature toggle becomes a *capability ceiling*, not a *data permission*. |
| DLP policy stale relative to a renamed feature. | Catalog rename history. | Update DLP rule; re-test. |
| Sensitivity label removed but per-agent gate still references it. | Label inventory diff. | Remove gate or re-introduce label. |

### §10.3 Diagnostic steps

1. `Get-Agt224DlpAlignment -OutFile evidence/2.24/E-07_dlp.csv`.
2. For each conflict, identify the DLP policy ID and the feature toggle ID.
3. Pull GQ-07 to confirm label state; KQL-02 / KQL-06 for live denials.

### §10.4 Resolution steps

- Treat the DLP / ACP layer as the *authoritative* data-flow decision; the feature toggle must be set to the **most restrictive** of (toggle ceiling, DLP allow). Do not loosen DLP to match a permissive toggle.
- Where the conflict is from rename / drift, update the DLP rule and re-test.
- Cascade to Control 1.4 (ACP) for any connector-related conflict.
- Add `Get-Agt224DlpAlignment` to the §22 evidence pipeline.

### §10.5 Cross-references

- [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md).
- [Control 1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md).
- §11 VOICE-IMAGE-GAP.

---

## §11 VOICE-IMAGE-GAP — Multimodal feature enabled without comms-compliance recording path

### §11.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Voice-input feature on; no Communication Compliance (CC) policy captures the transcript. | Compliance. | `Get-Agt224MultimodalSurfaces -ShowCcGap`. |
| Image / vision feature on; no retention applied to attachments. | Compliance. | KQL-06 hit. |
| Real-time translation enabled in client-facing agent without supervisor review channel. | Supervisor. | Per-agent surface enabled, no 2.12 binding. |

### §11.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| CC policy authored only for text. | CC policy inventory. | Extend CC policy to voice / image surfaces (Control 1.10). |
| Supervisor (2.12) WSP not updated for multimodal review. | WSP version diff. | Update WSP; train; re-attest. |
| Multimodal surface left on by default after a Microsoft GA. | GQ-05 + provenance. | Disable until coverage proven; see §6. |

### §11.3 Diagnostic steps

1. `Get-Agt224MultimodalSurfaces -OutFile evidence/2.24/E-08_multimodal.csv`.
2. For each agent with multimodal on, confirm matching CC policy via Control 1.10.
3. Confirm supervisor coverage for the surface via Control 2.12 records.

### §11.4 Resolution steps

- **Hard gate:** if there is no matching CC capture path, the multimodal surface must be disabled. The toggle is not a substitute for the recording obligation under SEC 17a-4 / FINRA 4511.
- Cascade to Control 1.10 (CC policy update) and Control 2.12 (WSP update).
- Add multimodal coverage to the §22 evidence pipeline.

### §11.5 Cross-references

- [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md).
- [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

---

## §12 MRM-CASCADE-BROKEN — Feature change made without an MRM change record (SR 26-2)

### §12.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Toggle changed; no Control 2.6 change record exists. | Quarterly MRM review. | `Get-Agt224MrmCascade -ShowOrphans`. |
| GA promotion changed model behaviour; no re-validation triggered. | MRM. | See §6 + missing 2.6 record. |
| Feature change crossed the model-risk-tier threshold without re-tier. | Audit. | Tier mismatch in 2.6 inventory. |

### §12.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| Workflow does not require MRM evidence for in-scope features. | Workflow definition. | Add MRM evidence as a hard gate. |
| Catalog does not flag which features are MRM-in-scope. | Catalog schema. | Add `MrmInScope` flag; backfill. |
| Change made through an out-of-band path (e.g. PowerShell) without workflow. | KQL-01 / KQL-04. | Disable out-of-band path or instrument it to emit workflow ticket. |

### §12.3 Diagnostic steps

1. `Get-Agt224MrmCascade -ShowOrphans -OutFile evidence/2.24/E-03_mrm_orphans.csv`.
2. For each orphan, identify whether the change crossed an MRM threshold (consult Control 2.6 risk-tier matrix).
3. Pull provenance to identify actor and pathway.

### §12.4 Resolution steps

- For each orphan: produce a retrospective MRM change record under Control 2.6, including risk acceptance signed by AI Governance Lead. **Do not** silently close — every orphan is itself an Fed SR 26-2 (formerly SR 11-7) finding.
- Tighten workflow to make MRM evidence a hard gate for in-scope features.
- Add `MrmInScope` flag to the catalog and to `Get-Agt224FeatureSnapshot`.
- Cascade to §13 (supervisor re-notification once MRM record is closed).

> **Hedged language.** Producing a retrospective MRM record **supports** Fed SR 26-2 (formerly SR 11-7) documentation but does not erase the original gap; the audit trail must show both the gap and the retrospective remediation.

### §12.5 Cross-references

- [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md).
- §6 RETROACTIVE-PREVIEW.
- RB-04 (§17).

---

## §13 SUPERVISOR-UNAWARE — Feature changed; supervisors / WSP not updated

### §13.1 Symptom catalog

| Symptom | Where reported | First-look indicator |
|---|---|---|
| Supervisor reports unfamiliar agent behaviour. | Supervision queue. | `Get-Agt224SupervisorAttestation -ShowOrphans`. |
| WSP version older than the most recent feature change. | Compliance review. | Version drift. |
| New surface (e.g. voice) live but no supervision sampling defined. | Audit. | See §11. |

### §13.2 Root-cause matrix

| Cause | Evidence | Resolution |
|---|---|---|
| Workflow does not notify supervisors. | Workflow definition. | Add supervisor-notification step + acknowledgement gate. |
| WSP review cadence lags feature change cadence. | WSP cadence vs. change frequency. | Move WSP to event-driven review for feature-impacting changes. |
| Supervisor coverage map missing the new surface. | 2.12 inventory. | Update coverage map; train; re-attest. |

### §13.3 Diagnostic steps

1. `Get-Agt224SupervisorAttestation -ShowOrphans -OutFile evidence/2.24/E-03_super_orphans.csv`.
2. For each orphan, identify which WSP section governs the affected surface.
3. Confirm supervisor training records are current.

### §13.4 Resolution steps

- Issue a supervisor advisory describing the change and the new expected behaviour; require acknowledgement within 5 business days.
- Update the WSP; route through Control 2.12 review and approval.
- Add supervisor-acknowledgement as a hard gate to the change workflow for feature-impacting changes.
- For a missed cycle, run a back-look supervision review covering the period from change to acknowledgement.

### §13.5 Cross-references

- [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
- §11 VOICE-IMAGE-GAP.
- §12 MRM-CASCADE-BROKEN.

---

## §14 RB-01 — Examiner / Regulator Inquiry on Agent Feature State

**Trigger.** FINRA, SEC, OCC, Federal Reserve, CFTC, or state regulator opens an inquiry that includes "what features were enabled on agent X between dates A and B" or "how do you know feature Y was disabled when policy required it."

**Pre-conditions.**

- E-01 snapshot history retained per §1.5.
- E-03 toggle provenance retained per §1.5.
- Audit log exports (Purview) reachable for the inquiry window.

**Procedure.**

1. **T+0 — Stop-the-press (per §0.4).** Issue a written hold to the AI Administrator team: no toggle changes, no agent deletions, no credential rotations on the named agents until evidence is captured. Notify Compliance Officer and Legal.
2. **T+1 hr — Capture point-in-time state.** Run `Get-Agt224FeatureSnapshot -IncludeAuditTrail` against the named agent / environment / tenant; commit to immutable storage as **E-10**.
3. **T+2 hr — Reconstruct the inquiry window.** Use `Get-Agt224ToggleProvenance -Last 365` filtered to the window; cross-join with KQL-01 / KQL-03 / KQL-04 for actor and approver UPN.
4. **T+4 hr — Cross-control bundle.** Pull the matching MRM (2.6) records, supervisor (2.12) attestations, DLP (1.4) policies, and CC (1.10) coverage for the same window. Bundle as a single PDF + manifest.
5. **T+24 hr — Compliance / Legal review.** Compliance Officer reviews the bundle for completeness; Legal reviews for privilege.
6. **T+SLA — Submit.** Submit through the Compliance Officer; do **not** allow direct admin-to-regulator transmission of evidence.

**Evidence bundle (E-10).**

- E-01 snapshot for window start, end, and quarterly checkpoints inside the window.
- E-03 provenance for every flagged feature.
- Cross-references to E-02 (catalog state), E-04 (MCP inventory), E-07 (DLP), E-08 (multimodal).
- Manifest listing every artefact, hash, and capture time.

**Rollback.** None — no remediation actions are taken in this runbook beyond the stop-the-press hold. Lift the hold only after Compliance Officer signs off.

**Cross-references.** §0.4, §22, [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

---

## §15 RB-02 — Zero-Day Microsoft Service-Side Default Flip

**Trigger.** Microsoft flips a Copilot / Copilot Studio / MCP / Agent Framework default for the tenant without admin action, and the flip is detected via GQ-05 message, KQL-01 service-principal actor, or end-user behaviour change.

**Pre-conditions.** §1 diagnostic data current; AI Governance Lead reachable.

**Procedure.**

1. **T+0 — Detect & classify.** Confirm the flip via GQ-05 + KQL-01. Determine whether the flipped feature is MRM-in-scope (Control 2.6) or supervision-in-scope (Control 2.12).
2. **T+30 min — Containment decision.** AI Administrator + AI Governance Lead decide: (a) accept the new default, (b) revert at tenant, or (c) revert per-environment / per-agent. Document the decision and rationale.
3. **T+1 hr — Execute decision.** If revert: apply at the highest surface that achieves the goal (tenant > environment > per-agent). Capture E-01 before and after.
4. **T+2 hr — Cascade.** If MRM-in-scope: open a 2.6 record. If supervision-in-scope: notify supervisors per §13. If multimodal: re-check §11 coverage.
5. **T+24 hr — Post-flip attestation.** File E-09 with rationale, decision, and cascade evidence.

**Evidence bundle.** GQ-05 message, KQL-01 result, E-01 before / after, decision memo, cascade tickets.

**Rollback.** Revert toggle if the decision changes; the catalog must reflect the latest state.

**Cross-references.** §6 RETROACTIVE-PREVIEW, §12 MRM-CASCADE-BROKEN, §13 SUPERVISOR-UNAWARE.

---

## §16 RB-03 — Sovereign Parity Escalation (Commercial-Only Feature Requested in GCC / GCC High / DoD)

**Trigger.** Business sponsor requests a feature in a sovereign tenant that `Get-Agt224SovereignParity` flags as `CommercialOnly = $true` or `Status = NotPlannedForSovereign`.

**Procedure.**

1. **T+0 — Confirm parity gap.** Run `Get-Agt224SovereignParity -Cloud <cloud> -Feature <name>`; capture the Microsoft Roadmap entry URL and date.
2. **T+1 day — Compensating-control analysis.** Security Architect identifies the closest sovereign-supported alternative; AI Governance Lead reviews fitness-for-purpose.
3. **T+3 days — Written refusal + alternative.** Compliance Officer issues a written response to the requester documenting (a) the parity gap, (b) the compensating control, (c) the conditions under which the request would be re-opened (e.g. "if Microsoft ships to GCC High").
4. **T+5 days — Catalog update.** Add the feature to the sovereign catalog as `Scope: Commercial; SovereignAlternative: <…>; ReReviewTrigger: <Roadmap milestone>`.
5. **Quarterly.** Re-check Roadmap; if status changes, re-open through change-management.

**Evidence bundle.** E-06 parity report, Roadmap reference, refusal memo, catalog diff.

**Cross-references.** §9, [`../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).

---

## §17 RB-04 — Deprecated Preview Feature Bound to a Production Agent

**Trigger.** Microsoft has issued a deprecation timer for a preview feature, and `Get-Agt224PreviewFeatures -State deprecated` shows one or more production agents bound to it.

**Procedure.**

1. **T+0 — Inventory.** List every agent bound to the deprecated feature; rank by zone, business criticality, MRM tier.
2. **T+5 days — Migration plan.** Each agent owner produces a migration plan: target alternative, test plan, supervisor re-coverage, MRM re-validation if applicable.
3. **T+halfway-to-deprecation — Mid-point review.** AI Governance Lead reviews progress; escalate stalled migrations.
4. **T+deprecation - 14 days — Hard freeze.** Any remaining agent must either complete migration or receive a documented acceptance of post-deprecation breakage from AI Governance Lead + Compliance Officer.
5. **T+deprecation — Post-removal verification.** Confirm no agent retains a binding; close E-09.

**Rollback.** Microsoft deprecation cannot be rolled back — the rollback is the migration plan itself.

**Cross-references.** §6 RETROACTIVE-PREVIEW, [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

---

## §18 RB-05 — SOX §404 Quarterly Attestation Deadline

**Trigger.** Quarterly SOX §404 ITGC attestation due; financial-reporting-relevant agents (typically Z3) require evidence of feature-state stability and change-control adherence.

**Procedure.**

1. **T-30 days — Pre-attestation diff.** Run `Get-Agt224CatalogDiff` for every Z3 environment in scope. Resolve drift per §3.
2. **T-21 days — Provenance bundle.** For every change in the quarter on Z3 features, attach `Get-Agt224ToggleProvenance` output, change-record ID, and approver UPN.
3. **T-14 days — MRM and supervision reconciliation.** `Get-Agt224MrmCascade -ShowOrphans` and `Get-Agt224SupervisorAttestation -ShowOrphans` must be empty for Z3.
4. **T-7 days — Internal Audit walkthrough.** Internal Audit reviews the bundle; resolve findings.
5. **T-0 — Sign-off.** AI Governance Lead + Compliance Officer + Internal Audit sign E-09.

**Evidence bundle.** E-01 (start of quarter, end of quarter, weekly), E-02, E-03, MRM cascade report, supervisor cascade report, signed E-09.

**Cross-references.** [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md).

---

## §19 RB-06 — Non-Compliant Z3 Agent Detected in Production

**Trigger.** Audit / monitoring detects a Z3 (regulated/SOX) agent in a configuration that violates the Z3 feature ceiling (e.g. consumer-cloud connector, web grounding, multimodal without CC, MCP unapproved).

**Procedure.**

1. **T+0 — Sev 1 declared.** Page AI Governance Lead + Compliance Officer + on-call AI Administrator.
2. **T+15 min — Evidence first (per §0.4).** Capture E-01 + the relevant evidence codes (E-04 for MCP, E-07 for DLP, E-08 for multimodal) **before** any change.
3. **T+30 min — Containment.** Use the smallest-blast-radius action that ends the violation: per-agent disable preferred over environment disable preferred over tenant disable. Use `Set-Agt224EmergencyDisable` only if smaller-scope actions are insufficient.
4. **T+2 hr — Open Control 3.4 incident.** Root-cause analysis owned by AI Governance Lead; supervisor and MRM cascades initiated in parallel.
5. **T+24 hr — Customer / counterparty impact assessment.** Compliance Officer determines whether disclosure or notification is required (state notification laws, GLBA Safeguards Rule incident response).
6. **T+5 days — Post-incident review.** File E-09; update catalog, workflow, and detection to prevent recurrence.

**Cross-references.** §5, §8, §10, §11, [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

---

## §20 RB-07 — SEC Reg SCI Notification Path for Critical-System-Affecting Feature Change

**Trigger.** Tenant operates an SCI entity (national securities exchange, SCI ATS, SCI clearing agency, SCI plan processor, exempt clearing agency, registered SBSDR, or other entity within Reg SCI scope) and a Copilot / Copilot Studio / MCP feature change has, may have, or did have a material impact on an SCI system or SCI security event handling.

> **Scope caveat.** Whether a particular firm is an SCI entity, and whether a particular feature change is "SCI-relevant," is a Compliance / Legal determination, not an admin determination. This runbook governs the *operational* response *after* Compliance has classified the change as Reg SCI-in-scope.

**Procedure.**

1. **T+0 — Compliance classification confirmed.** Compliance Officer confirms in writing that the change falls within Reg SCI § 242.1002(a) or 242.1002(b) reporting scope.
2. **T+immediate — Preserve.** Apply §0.4 stop-the-press; capture E-01 + E-10 to immutable storage.
3. **T+1 hr — Internal notification.** Notify Senior Officer for Reg SCI compliance, AI Governance Lead, Internal Audit.
4. **T+24 hr — Reg SCI 24-hour update.** If Compliance determines the event is a "systems disruption," "systems compliance issue," or "systems intrusion" requiring 24-hour update under § 242.1002(b)(1)(ii), Compliance produces and files the update; AI Administrator supplies the technical narrative and evidence bundle on request.
5. **T+commitment — Quarterly / written report.** Provide evidence as Compliance directs for the quarterly Reg SCI report and any required written notice.
6. **T+post-event — Post-event analysis.** Contribute the technical RCA to the SCI post-event review.

**Evidence bundle.** E-01 + E-10 + technical narrative + every cross-control artefact relevant to the affected SCI system.

**Cross-references.** [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), §14 RB-01, §19 RB-06.

---

## §21 Escalation Matrix

| Tier | Engaged when | Owner | Engagement path |
|---|---|---|---|
| **Internal — AI Administrator on-call** | All Sev 3, initial Sev 2. | AI Administrator team. | Standing rota. |
| **Internal — AI Governance Lead** | All Sev 1, any Sev 2 with cross-control cascade, any reverse-flow SLA breach. | AI Governance Lead. | Page via incident channel. |
| **Internal — Compliance Officer** | Any Sev 1, any examiner / audit hold, any Reg SCI / Fed SR 26-2 (formerly SR 11-7) / FINRA 3110 implication, any customer-impact assessment. | Compliance Officer. | Page via incident channel. |
| **Internal — Security Architect** | MCP-UNAPPROVED, ZONE-ESCALATION, DLP-MISMATCH where data egress occurred. | Security Architect. | Page via incident channel. |
| **Internal — Legal** | Any examiner inquiry, any Reg SCI 24-hour event, any cross-border data implication, any vendor-contract trigger. | Compliance Officer engages Legal. | Compliance-mediated only. |
| **Microsoft Support — Tier 1** | Reproducible UI / functional issue, no data exposure. | AI Administrator. | M365 admin → Support, attach §0.3 bundle. |
| **Microsoft Support — Tier 2 / Premier (Unified Support)** | Service-side default flip, sovereign parity dispute, RBAC defect, Graph endpoint defect. | AI Administrator + AI Governance Lead. | Premier ticket; reference incident ID. |
| **Microsoft Support — Critical Situation (CritSit)** | Sev 1 with active service-side root cause; data egress; multi-tenant blast radius. | AI Governance Lead. | Premier CritSit; loop in Account TAM. |
| **External — Regulator** | Per Compliance / Legal direction only. | Compliance Officer. | Never direct from admin team. |

> **Role usage rule.** AI Administrator is the standing day-to-day role for all activity in this playbook. Entra Global Admin is **exceptional only** — used solely for break-glass actions where AI Administrator scope is insufficient, and every such use must appear in E-09.

---

## §22 Evidence Collection During Incident

### §22.1 Capture order

For every Sev 1 / Sev 2 incident, capture in this order **before** any remediation action:

1. **E-01** — `Get-Agt224FeatureSnapshot -IncludeAuditTrail` to immutable storage.
2. **E-03** — `Get-Agt224ToggleProvenance` for every affected feature, last 90 days.
3. **E-04** — `Get-Agt224McpInventory` for every affected agent.
4. **E-07** — `Get-Agt224DlpAlignment` for every affected data flow.
5. **E-08** — `Get-Agt224MultimodalSurfaces` for every affected agent.
6. Purview audit-log export for affected actors over the incident window.
7. Defender / Sentinel KQL exports (KQL-01 .. KQL-06 as relevant).

### §22.2 Storage and integrity

- Write to a WORM-class immutable storage tier (Azure immutable Blob, Purview retention-locked container, or equivalent).
- Compute SHA-256 over each artefact; record in the manifest.
- Apply a retention label that meets **the longer of** (a) SEC 17a-4(f) / FINRA 4511 (6 yrs accessible, then archive), (b) CFTC Rule 1.31 (5 yrs / lifetime of the swap), (c) any active legal hold.

### §22.3 Manifest schema

```json
{
  "incidentId": "INC-2026-0414-0001",
  "tenantId": "...",
  "cloud": "Commercial|GCC|GCCH|DoD",
  "captureStartUtc": "2026-04-14T13:02:11Z",
  "captureEndUtc":   "2026-04-14T13:34:42Z",
  "artefacts": [
    {
      "code": "E-01",
      "path": "evidence/2.24/E-01_snapshot_202604141302.json",
      "sha256": "…",
      "capturedBy": "ai-admin@contoso.com",
      "purviewLabel": "Records-7yr-Locked"
    }
  ],
  "crossControlRefs": ["2.6/MRM-2026-04-019", "2.12/WSP-2026-Q2-rev3"]
}
```

### §22.4 Chain of custody

Every artefact must record: capturing identity, timestamp (UTC), source tenant + cloud, hash, retention label, and the manifest entry. Movement between storage tiers must be logged. Examiner / regulator transmission goes through Compliance Officer only.

---

## §23 Cross-References (Consolidated)

**Within Pillar 1 — Security:**

- [Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) — publishing-authorization gate; researcher / analyst exception groups.
- [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — registry as source of truth; template-import hardening.
- [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) — ACP as the authoritative data-flow decision layer.
- [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — multimodal CC coverage.
- [Control 1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md) — MIME boundary for MCP / file-upload features.

**Within Pillar 2 — Management:**

- [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) — zone definitions.
- [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — MRM cascade.
- [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — supervision cascade.
- [Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) — orchestration extends surface confusion.
- [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — governance console as canonical surface.

**Within Pillar 3 — Reporting:**

- [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — incident path for Sev 1.
- [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — orphaned-agent overlap with deprecated-preview migration.

**Sibling playbooks (Control 2.24):**

- [Portal Walkthrough](./portal-walkthrough.md).
- [PowerShell Setup](./powershell-setup.md).
- [Verification & Testing](./verification-testing.md).

**Shared:**

- [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — sovereign endpoint substitution, helper-cmdlet baseline.

---

## §X Recovery and Post-Incident Attestation

### §X.1 Closure criteria

An incident under this playbook may be closed only when **all** of the following are true:

- [ ] Symptom no longer reproducible (verified by AI Administrator and the original reporter).
- [ ] All evidence in §22 captured to immutable storage with manifest.
- [ ] Catalog updated; `Get-Agt224CatalogDiff` clean for the affected scope.
- [ ] Surface matrix consistent across tenant / environment / per-agent.
- [ ] Where MRM-in-scope: Control 2.6 record opened, signed, and linked.
- [ ] Where supervision-in-scope: Control 2.12 supervisor advisory acknowledged within SLA.
- [ ] Where DLP / connector / multimodal cascades applied: Controls 1.4 / 1.10 / 1.25 confirmed re-aligned.
- [ ] Detection added or strengthened so the same root cause would surface earlier next time.
- [ ] E-09 attestation signed (template below).

### §X.2 E-09 Attestation Template

```markdown
# Control 2.24 — Post-Incident Attestation (E-09)

**Incident ID:**            INC-YYYY-MMDD-NNNN
**Pillar(s) engaged:**      §N (NAME), §N (NAME)
**Runbook(s) executed:**    RB-NN
**Severity (final):**       Sev 1 | Sev 2 | Sev 3
**Tenant / Cloud:**         <tenantId> / Commercial | GCC | GCCH | DoD
**Detection time (UTC):**   YYYY-MM-DDTHH:MM:SSZ
**Containment time (UTC):** YYYY-MM-DDTHH:MM:SSZ
**Resolution time (UTC):**  YYYY-MM-DDTHH:MM:SSZ

## 1. Summary
<one paragraph: what happened, what was the regulatory exposure, what was done>

## 2. Root cause
<which §N pillar(s); upstream contributing factors; was this a recurrence>

## 3. Cascades engaged
- [ ] Control 2.6 (MRM / Fed SR 26-2 — formerly SR 11-7) — record ID:
- [ ] Control 2.12 (Supervision / FINRA 3110) — WSP ref:
- [ ] Control 1.4 (ACP) — policy IDs touched:
- [ ] Control 1.10 (CC) — policy IDs touched:
- [ ] Control 3.4 (Incident) — incident ID:
- [ ] None of the above — explicit rationale below:

## 4. Evidence bundle
| Code | Path | SHA-256 | Retention label |
|---|---|---|---|
| E-01 | … | … | Records-7yr-Locked |
| E-03 | … | … | Records-7yr-Locked |
| …    | … | … | … |

## 5. Break-glass usage
- [ ] No Entra Global Admin or `Set-Agt224EmergencyDisable` action was required.
- [ ] Break-glass used; identity, timestamp, co-signers, scope below:

## 6. Detection improvement
<what monitoring / alert / workflow gate was added or tuned>

## 7. Hedged-language confirmation
This attestation **supports** examiner response and post-incident review. It does not substitute for:
- the Fed SR 26-2 (formerly SR 11-7) model-risk record (Control 2.6),
- the FINRA Rule 3110 written supervisory procedure update (Control 2.12),
- or the AI guardrail framework (Control 1.1).

## 8. Sign-off
| Role | Name | Date (UTC) |
|---|---|---|
| AI Administrator | | |
| AI Governance Lead | | |
| Compliance Officer | | |
| Security Architect (if §5/§8/§10) | | |
| Senior Officer for Reg SCI (if RB-07) | | |
```

### §X.3 Lessons-learned cadence

- AI Governance Lead reviews all closed E-09 records monthly; cross-cuts root causes across pillars.
- Quarterly: produce a trend report into the governance steering committee covering pillar frequency, mean-time-to-detect, mean-time-to-contain, cascade completion rates.
- Annual: feed into the catalog re-baseline and the sovereign parity re-baseline (§9).

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
