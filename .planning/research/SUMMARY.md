# Project Research Summary

**Project:** Session Security Configurator (v5 Milestone)
**Domain:** Automated Conditional Access session control enforcement for Microsoft 365 AI agent governance in US financial services
**Researched:** 2026-02-06
**Confidence:** HIGH

## Executive Summary

The Session Security Configurator (SSC) automates zone-specific Conditional Access session control enforcement -- sign-in frequency, persistent browser, authentication contexts, and authentication strengths -- for Control 1.23 (Step-Up Authentication for Agent Operations). The dominant finding across all four research dimensions is that **this solution should be built as an extension of the existing Conditional Access Automation (CAA) solution, not as a standalone solution**. The existing CAA already handles CA policy CRUD, deployment, drift detection, and evidence export. SSC fills a specific gap: authentication context lifecycle management (c1-c5), step-up CA policy templates with authentication strength enforcement, session-specific validation, and step-up monitoring. No new PowerShell modules or Graph API permissions are needed -- the existing `Microsoft.Graph.Identity.SignIns` module and `Policy.ReadWrite.ConditionalAccess` permission cover all required operations.

The recommended approach is a 4-phase build following the established Tier 2 pattern (PowerShell + Dataverse + Power Automate). Phase 1 builds standalone PowerShell scripts for authentication context management and session validation against local JSON baselines. Phase 2 adds Dataverse infrastructure for persistent state. Phase 3 layers on Power Automate automation with Teams alerting and zone-tiered remediation. Phase 4 completes evidence export with Compliance Dashboard integration. This phasing allows each layer to be tested independently before adding the next, matching the proven ACV (Audit Configuration Validator) build pattern.

The critical risks are: (1) overlapping CA policies creating unpredictable session timeouts because Entra evaluates ALL matching policies with AND logic, (2) break-glass account exclusion failures causing tenant lockout, (3) premature transition from report-only to enforced mode disrupting trading operations, and (4) automated drift remediation bypassing SOX/FINRA change control requirements. A mandatory pre-deployment CA policy audit, break-glass validation on every write, 72-hour minimum report-only bake time, and detect-only default for drift detection are non-negotiable safeguards. Additionally, the March 2026 "All resources" enforcement change from Microsoft must be accounted for in deployment timing -- it may affect persistent browser session policies that target "All resources."

## Key Findings

### Recommended Stack

The stack story is simple: no new dependencies. The existing Microsoft Graph PowerShell SDK (`Microsoft.Graph.Identity.SignIns` v2.35.1) contains all cmdlets needed for session controls, authentication contexts, and authentication strength policies. Session controls are properties within the `conditionalAccessPolicy` resource, not separate APIs.

**Core technologies:**
- **Microsoft.Graph.Identity.SignIns v2.35.1**: CA policy session controls, authentication context CRUD, authentication strength management -- already used by existing CAA solution
- **Microsoft.Graph.Beta.Identity.SignIns v2.35.1**: Required ONLY for `frequencyInterval: "everyTime"` (Zone 3 risky users) and What-If evaluation -- v1.0 has a confirmed open bug (GitHub #647, filed June 2024, still unresolved)
- **Microsoft.Graph.Authentication v2.35.1**: Graph connection management -- existing dependency
- **Dataverse Web API**: Session baselines, validation history, drift violations -- follows ACV pattern
- **Power Automate**: Scheduled drift scans, Teams alerting, zone-tiered remediation routing -- follows ACV pattern

**Critical version note:** Microsoft.Graph SDK v2.26.x had regressions breaking Azure Automation runbook compatibility. Pin to v2.35.0+ minimum. The `builtInControls: ["mfa"]` and `authenticationStrength` grant controls are mutually exclusive -- Zone 3 templates must be migrated from the former to the latter for phishing-resistant MFA enforcement.

**No new permissions required.** The existing service principal's `Policy.ReadWrite.ConditionalAccess` permission covers authentication context and authentication strength operations.

### Expected Features

**Must have (table stakes):**
- **TS-1: Authentication Context Lifecycle Management** -- Create/validate c1-c5 contexts (foundation for everything else)
- **TS-2: Step-Up CA Policy Deployment** -- Deploy 5 step-up policies with correct auth strengths per context
- **TS-3: Zone-Specific Session Control Validation** -- Validate deployed policies match zone requirements (8h/4h/1h)
- **TS-4: Session Control Drift Detection** -- Extend CAA's `Watch-PolicyDrift.ps1` with step-up-specific drift types
- **TS-5: Compliance Evidence Export** -- Extend CAA's `Export-PolicyEvidence.ps1` with auth context and step-up data
- **TS-6: Dry-Run Mode** -- Non-negotiable for FSI; preview all changes before applying

**Should have (differentiators):**
- **D-2: Authentication Strength Policy Management** -- Custom FSI-specific auth strength policies, user readiness reporting
- **D-4: CAE Configuration Validation** -- Verify CAE enabled for step-up policies, strict enforcement for Zone 3
- **D-1: Context-to-Operation Mapping Validation** -- Verify auth contexts are actually triggered in sign-in logs

**Defer (v2+):**
- **D-3: PIM Integration Validation** -- Requires P2 licensing, complex cross-referencing
- **D-5: Step-Up Dashboard Data** -- Needs Compliance Dashboard Dataverse schema extension
- **D-6: Token Protection Validation** -- Verify GA status for Power Platform before investing

**Anti-features (do NOT build):**
- General CA policy deployment engine (CAA already has this)
- Independent drift detection system (extend CAA's)
- Separate evidence export pipeline (extend CAA's)
- Real-time policy enforcement agent (Microsoft's responsibility)
- MFA method registration management (IAM concern, out of scope)

### Architecture Approach

SSC follows the Tier 2 solution pattern with four internal components: Baseline Manager (defines expected session settings per zone), Session Drift Detector (compares live state to baselines), AuthContext Validator (validates c1-c5 exist and are correctly bound), and Evidence Exporter (SHA-256 integrity hashing for compliance). It integrates with three existing solutions -- ELM for zone classification, CAA for policy deployment (no duplication), and Compliance Dashboard for evidence delivery. The clean boundary is: CAA owns policy lifecycle, SSC owns session control validation and authentication context management. SSC reads CA policies but never creates or deletes them. Auto-remediation (PATCH on sessionControls only) is permitted for Zone 1/2 but defaults to alert-only for Zone 3.

**Major components:**
1. **Baseline Manager** -- Defines expected session controls per zone per application, stored in `fsi_SessionBaseline` Dataverse table
2. **Session Drift Detector** -- Daily Graph API scan comparing live CA session controls against baselines, writes to `fsi_SessionValidationHistory` (immutable)
3. **AuthContext Validator** -- Validates authentication contexts c1-c5 exist and are bound to correct step-up CA policies
4. **Evidence Exporter** -- Exports session compliance evidence with SHA-256 hashing for FINRA/SEC examinations

**New Dataverse tables:** `fsi_SessionBaseline`, `fsi_SessionValidationHistory` (immutable), `fsi_SessionDriftViolation`. Reuses existing global option sets `fsi_acv_zone` and `fsi_acv_severity` from ACV deployment.

### Critical Pitfalls

1. **Conflicting CA policies with overlapping session controls** -- Entra evaluates ALL matching policies with AND logic; most restrictive wins. A tenant-wide "12-hour SIF for all apps" policy will override Zone 1's intended 8-hour setting. **Prevention:** Pre-deployment audit of ALL existing CA policies with What-If testing for representative users in each zone. This is a Phase 1 hard prerequisite.

2. **Break-glass account exclusion failure** -- Template substitution failure or stale object IDs in config causes break-glass accounts to be included in session policies, leading to potential tenant lockout. **Prevention:** Programmatic break-glass validation before every policy write; abort entire deployment if validation fails. Post-deployment read-back verification.

3. **Premature report-only to enforced transition** -- Deploying directly in enforced mode or insufficient bake time causes production disruption during trading hours. **Prevention:** 72-hour minimum bake period (non-negotiable for FSI), human approval gate for enforced mode, phased zone-by-zone enablement (Zone 1 first).

4. **Automated remediation bypassing change control** -- Auto-fixing drift without CAB approval violates SOX 302/404 and FINRA 3110 requirements. **Prevention:** Detect-only mode as default; use `Policy.Read.All` for drift detection principal; human-in-the-loop for all Zone 3 writes.

5. **Persistent browser session requires "All cloud apps" targeting** -- Microsoft states this control only works correctly when targeting all apps. Existing Zone 3 template targets specific apps, which may silently fail. **Prevention:** Either create a separate "All cloud apps" persistent browser policy or use shorter sign-in frequency as compensating control.

## Implications for Roadmap

Based on combined research, the solution naturally decomposes into 4 phases matching the ACV proven build pattern.

### Phase 1: PowerShell Core -- Authentication Context and Session Validation

**Rationale:** All other phases depend on the core PowerShell validation logic. Building standalone scripts first (no Dataverse dependency) allows rapid iteration and testing against real Graph API responses. The pre-deployment CA policy audit (Pitfall 1 prevention) must happen before any policy deployment.

**Delivers:** Working PowerShell scripts that create authentication contexts, deploy step-up policies (report-only), validate session controls against JSON baselines, and export results to console/file.

**Features addressed:** TS-1 (Auth Context Management), TS-2 (Step-Up Policy Deployment), TS-3 (Zone Validation), TS-6 (Dry-Run Mode), D-2 (Auth Strength Management)

**Pitfalls to avoid:** Pitfall 1 (pre-deployment CA audit), Pitfall 2 (break-glass validation), Pitfall 5 (persistent browser scoping), Pitfall 9 (v1.0 vs beta API), Pitfall 10 (legacy MFA setting conflict), Pitfall 13 (zone membership overlap)

**Scripts to build:**
- `Deploy-AuthContexts.ps1` -- Create c1-c5 with idempotent execution
- `Deploy-StepUpPolicies.ps1` -- Step-up CA policy templates with authentication strength
- `Test-SessionCompliance.ps1` -- Validate session controls match zone baselines
- `private/Compare-SessionBaseline.ps1` -- Baseline comparison helper
- `private/Connect-GraphSession.ps1` -- Graph API auth helper
- Step-up policy templates in `templates/step-up/`
- Zone baseline defaults in `templates/session-baselines/`

### Phase 2: Dataverse Infrastructure -- Persistent State and Schema

**Rationale:** Once PowerShell core is proven against real APIs, migrate from local JSON baselines to Dataverse for persistent, queryable state. This is the standard Tier 2 pattern progression (same as ACV Phase 2). Dataverse enables cross-solution integration with ELM zone data and Compliance Dashboard evidence.

**Delivers:** Deployed Dataverse schema (3 tables, 3 new option sets, reuse of 2 existing option sets), environment variables for zone thresholds, connection references. Scripts updated to read/write Dataverse instead of local JSON.

**Features addressed:** TS-4 (Drift Detection -- baseline storage), TS-5 (Evidence Export -- history storage)

**Pitfalls to avoid:** Pitfall 6 (document session control scope honestly -- interactive only), Pitfall 7 (document CAE/SIF interaction for evidence), Pitfall 8 (March 2026 enforcement change timing), Pitfall 12 (device-type SIF behavior documentation)

**Scripts to build:**
- `ssc_client.py` -- Dataverse Web API client (based on `acv_client.py`)
- `create_dataverse_schema.py` -- Tables, option sets (with existing option set reuse detection)
- `create_environment_variables.py` -- Zone threshold variables
- `create_connection_references.py` -- Dataverse, Office 365, Teams connectors
- `deploy.py` -- Orchestrator with dry-run support
- Updates to Phase 1 scripts for Dataverse read/write

### Phase 3: Automation and Alerting -- Scheduled Drift Detection

**Rationale:** With validated scripts and Dataverse infrastructure, add scheduled execution via Power Automate and zone-tiered alerting. Drift detection is the ongoing operational value -- it catches unauthorized session control weakening. This phase must implement detect-only as the default (Pitfall 4).

**Delivers:** Daily automated drift scans via Power Automate + Azure Automation, Teams adaptive card alerts with severity classification, optional auto-remediation for Zone 1/2 only (with explicit opt-in), Zone 3 escalation flow.

**Features addressed:** TS-4 (Drift Detection -- automation), D-4 (CAE Configuration Validation)

**Pitfalls to avoid:** Pitfall 4 (detect-only default, no auto-remediation for Zone 3), Pitfall 11 (include named locations in drift baseline), Pitfall 14 (baseline staleness -- approved change feedback loop), Pitfall 17 (Graph API rate limiting)

**Artifacts to build:**
- `Start-SessionValidationRunbook.ps1` -- Azure Automation wrapper
- `src/session-drift-flow.json` -- Power Automate flow definition
- `src/adaptive-card-session-alert.json` -- Teams alert template
- `src/adaptive-card-zone3-escalation.json` -- Zone 3 critical alert
- Auto-remediation logic (Zone 1/2 only, opt-in)

### Phase 4: Evidence Export and Dashboard Integration

**Rationale:** Complete the compliance loop by exporting session security evidence with SHA-256 integrity hashing and feeding it into the Compliance Dashboard for Control 1.23 scoring. This is the phase that makes the solution examinable by FINRA/SEC/OCC auditors.

**Delivers:** Evidence export with SHA-256 manifest, Compliance Dashboard `fsi_complianceevidence` integration, documentation suite (prerequisites, schema, configuration, troubleshooting).

**Features addressed:** TS-5 (Evidence Export), framework documentation updates

**Pitfalls to avoid:** Pitfall 6 (separate interactive vs workload identity evidence), Pitfall 7 (explain CAE/SIF interaction in compliance narrative)

**Artifacts to build:**
- `Export-SessionSecurityEvidence.ps1` -- Evidence export with SHA-256
- `Test-EvidenceIntegrity.ps1` -- Hash verification
- Compliance Dashboard integration (write to `fsi_complianceevidence`)
- Full documentation suite (6 docs)
- Framework documentation updates (solutions-index, solutions-integration, Control 1.23 cross-references)

### Phase Ordering Rationale

- **Phase 1 before Phase 2:** PowerShell scripts must work standalone before adding Dataverse dependency. This matches the ACV pattern where core validation logic was proven first, then migrated to Dataverse storage.
- **Phase 2 before Phase 3:** Dataverse schema must exist before Power Automate flows can read/write to it. Environment variables must be deployed before scheduled flows reference them.
- **Phase 3 before Phase 4:** Validation history must be accumulating in Dataverse before evidence export can query it. Drift detection must be running to generate the violation data that evidence export aggregates.
- **Dependencies drive grouping:** TS-1 (auth contexts) is the absolute foundation -- everything depends on contexts existing. TS-2 (step-up policies) depends on TS-1. TS-3/TS-4/TS-5 depend on TS-2. D-2 (auth strength) is naturally paired with TS-2 (policies reference strengths).
- **Pitfall timing:** The pre-deployment CA audit (Pitfall 1) must happen in Phase 1 before any policy deployment. The March 2026 enforcement change (Pitfall 8) means Phase 2 deployment timing should either complete before March 27 or begin after the rollout stabilizes in June 2026.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** Verify `authenticationStrength` + `builtInControls: ["compliantDevice"]` coexistence in same `grantControls` object (Stack research Open Question #2). Also verify persistent browser behavior with app-specific targeting (Pitfall 5 needs testing).
- **Phase 3:** Determine exact behavior of policies created via Beta API (`everyTime` frequency) -- can they be read via v1.0? Or are they "beta-locked"? (Stack research Open Question #1)
- **Phase 4:** Validate What-If evaluation (`Test-MgBetaIdentityConditionalAccess`) returns session control details in evaluation results (Stack research Open Question #5)

Phases with standard patterns (skip research-phase):
- **Phase 2:** Dataverse schema creation follows exact ACV pattern -- `create_dataverse_schema.py`, `create_environment_variables.py`, `create_connection_references.py`, `deploy.py`. Well-documented, established pattern.
- **Phase 4:** Evidence export follows exact ACV `Export-AuditValidationEvidence.ps1` pattern. SHA-256 hashing, JSON output, Compliance Dashboard integration all established.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | All components verified against PowerShell Gallery and Microsoft Learn docs. No new dependencies. Only uncertainty: when will Graph v1.0 fix `everyTime` (GitHub #647) |
| Features | **HIGH** | Table stakes grounded in Control 1.23 specs and existing CAA solution examination. Differentiators have clear Graph API support. Feature boundary with CAA is well-defined |
| Architecture | **HIGH** | Derived from direct examination of 7 existing solutions in FSI-AgentGov-Solutions repo. Tier 2 pattern, Dataverse schema, Power Automate flows all follow proven ACV pattern |
| Pitfalls | **HIGH** | 17 pitfalls identified from Microsoft official docs, community sources, and existing codebase examination. Critical pitfalls (1-4) are well-documented with clear prevention strategies |

**Overall confidence: HIGH** -- This is an extension of an existing solution following established patterns, not greenfield development. The Graph API surface is GA and documented. The Dataverse/Power Automate architecture is proven across 4+ existing solutions.

### Gaps to Address

- **`everyTime` beta lock-in behavior:** After creating a Zone 3 policy via Beta API, can it be read via v1.0? Test in non-production tenant before architecture is finalized (Phase 1 research task)
- **`authenticationStrength` + `compliantDevice` coexistence:** Documentation says `mfa` and `authenticationStrength` are mutually exclusive, but `compliantDevice` is not `mfa`. Verify via test deployment (Phase 1 research task)
- **Persistent browser with app-specific targeting:** Does it actually enforce, or silently fail? Existing Zone 3 template may have this issue. Test actual browser behavior, not just policy configuration (Phase 1 testing task)
- **March 2026 enforcement change impact:** Track Microsoft rollout timeline. If SSC deploys "All resources" policies for persistent browser, the OIDC-only scope enforcement change may cause unexpected blocks (Phase 2 timing decision)
- **Authentication context pre-existing usage:** Tenants may already use c1-c5 for non-FSI purposes. `Deploy-AuthContexts.ps1` must discover and warn before overwriting (Phase 1 design requirement)
- **MCAS session proxy configuration path:** The exact integration path between CA session controls and Defender for Cloud Apps needs verification with current documentation (Phase 3 if MCAS proxy is needed for Zone 3)

## Sources

### Primary (HIGH confidence -- official documentation, verified)

**Microsoft Graph API:**
- [conditionalAccessSessionControls (v1.0)](https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesssessioncontrols?view=graph-rest-1.0)
- [signInFrequencySessionControl (v1.0)](https://learn.microsoft.com/en-us/graph/api/resources/signinfrequencysessioncontrol?view=graph-rest-1.0)
- [authenticationContextClassReference API](https://learn.microsoft.com/en-us/graph/api/resources/authenticationcontextclassreference)
- [Authentication Strengths API Overview](https://learn.microsoft.com/en-us/graph/api/resources/authenticationstrengths-overview?view=graph-rest-1.0)

**Microsoft Entra / Conditional Access:**
- [Session Lifetime Policies](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime)
- [Session Controls Concept](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-session)
- [Continuous Access Evaluation](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation)
- [CA for Workload Identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)
- [Persistent Browser Session Policy](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-all-users-persistent-browser)
- [Authentication Strengths Concept](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths)
- [Phishing-Resistant MFA for Admins](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-admin-phish-resistant-mfa)
- [Developer Guide -- Authentication Context](https://learn.microsoft.com/en-us/entra/identity-platform/developer-guide-conditional-access-authentication-context)

**PowerShell SDK:**
- [PowerShell Gallery -- Microsoft.Graph 2.35.1](https://www.powershellgallery.com/packages/Microsoft.Graph/2.35.1)
- [Graph Permissions -- Policy.ReadWrite.ConditionalAccess](https://graphpermissions.merill.net/permission/Policy.ReadWrite.ConditionalAccess)

**Known Issues:**
- [GitHub #647 -- everyTime not supported in v1.0](https://github.com/microsoftgraph/msgraph-metadata/issues/647) (open, filed June 2024)

**Upcoming Changes:**
- [Microsoft Entra Blog -- March 2026 CA enforcement change](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/upcoming-conditional-access-change-improved-enforcement-for-policies-with-resour/4488925)

### Secondary (MEDIUM confidence -- community sources, verified with multiple)

- [MSEndpointMgr: CA Implementation Mistakes](https://msendpointmgr.com/2025/10/14/microsoft-conditional-access-implementation-considerations-and-common-mistakes/)
- [Practical365: Managing CA Policies with PowerShell](https://practical365.com/conditional-access-policies-powershell/)
- [Report-Only to Enforced Transition Guide](https://www.welkasworld.com/post/conditional-access-essentials-how-to-safely-transition-policies-from-report-only-to-enforced-mode)
- [4sysops: March 2026 Enforcement Analysis](https://4sysops.com/archives/microsoft-entra-id-fixes-conditional-access-policy-bypass-will-enforce-mfa-sign-in-for-oidc-only-requests/)

### Project-Internal (HIGH confidence -- existing codebase)

- `FSI-AgentGov-Solutions/conditional-access-automation/` -- Existing solution (scripts, templates, docs)
- `FSI-AgentGov-Solutions/audit-configuration-validator/` -- ACV pattern reference (Dataverse schema, deployment scripts, evidence export)
- `FSI-AgentGov-Solutions/scope-drift-monitor/` -- Drift detection pattern reference
- `FSI-AgentGov-Solutions/compliance-dashboard/` -- Evidence integration target
- `docs/controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md` -- Control 1.23 requirements
- `docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md` -- Control 1.11 baseline
- `docs/framework/zones-and-tiers.md` -- Zone governance model

---
*Research completed: 2026-02-06*
*Ready for roadmap: yes*
