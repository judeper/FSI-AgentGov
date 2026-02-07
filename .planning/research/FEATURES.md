# Feature Landscape: Session Security Configurator

**Domain:** Automated session security enforcement for Microsoft 365 AI agent workloads in US financial services
**Researched:** 2026-02-06
**Overall Confidence:** HIGH (grounded in existing Control 1.23/1.11 specs, existing Conditional Access Automation solution, and verified Microsoft Graph API capabilities)

---

## Relationship to Existing Conditional Access Automation Solution

**Critical scoping decision:** The existing Conditional Access Automation solution (v1.0.0, WIP) already covers broad CA policy deployment, compliance testing, drift detection, and evidence export for Controls 1.11, 1.23, and 1.18. The Session Security Configurator must be scoped to avoid duplicating that work.

### What Conditional Access Automation Already Covers

| Capability | Status | Scripts |
|------------|--------|---------|
| 8 CA policy templates (zone-aligned) | Built | `templates/*.json` |
| Policy deployment (dry-run + live) | Built | `Deploy-CAPolicies.ps1` |
| Compliance testing (coverage, gaps, session values) | Built | `Test-PolicyCompliance.ps1` |
| Drift detection with Teams alerting | Built | `Watch-PolicyDrift.ps1` |
| Evidence export with SHA-256 integrity | Built | `Export-PolicyEvidence.ps1` |
| Service principal registration | Built | `Register-ServicePrincipal.ps1` |
| ELM integration for new environments | Documented | Config mapping |
| Break-glass account exclusion enforcement | Built | All templates |

### What the Session Security Configurator Should NOT Duplicate

The existing CA Automation solution handles general CA policy CRUD, deployment, and monitoring. The Session Security Configurator should focus specifically on the **authentication context and step-up session control layer** that the CA Automation solution does not address. This means:

- Do NOT build another policy deployment engine (use or extend CA Automation's)
- Do NOT build another drift detection framework (extend CA Automation's)
- Do NOT build another evidence export system (extend CA Automation's)
- DO build the authentication context lifecycle management
- DO build session control validation specific to step-up requirements
- DO build the mapping between agent operations and authentication contexts

### Recommended Scope Boundary

| Concern | Owned By | Rationale |
|---------|----------|-----------|
| CA policy templates and deployment | Conditional Access Automation | Already built, well-tested |
| Zone-based session timeout enforcement | Conditional Access Automation | Already in Zone1/2/3 templates |
| Authentication context creation (c1-c5) | Session Security Configurator | Not in CA Automation |
| Step-up CA policies per auth context | Session Security Configurator | Not in CA Automation |
| Authentication strength configuration | Session Security Configurator | Context-specific strengths |
| Session control validation per context | Session Security Configurator | Step-up specific validation |
| Context-to-operation mapping validation | Session Security Configurator | Domain-specific logic |
| Consolidated compliance reporting | Both (integration) | SSC feeds into CA Automation evidence |

---

## Table Stakes

Features users expect from a session security configurator. Missing any of these means the solution feels incomplete or cannot serve its stated purpose.

### TS-1: Authentication Context Lifecycle Management

**Why Expected:** Control 1.23 defines five authentication contexts (c1-c5) that must exist in Entra ID before any step-up policies work. Without automated context management, administrators must manually create and maintain these in the portal -- error-prone and unauditable.

**What It Does:**
- Creates authentication contexts c1 through c5 via Microsoft Graph API (`New-MgIdentityConditionalAccessAuthenticationContextClassReference`)
- Validates existing contexts match expected configuration (displayName, description, isAvailable)
- Reports on context status (created, missing, misconfigured)
- Supports idempotent execution (safe to re-run)

**Complexity:** Low
**Confidence:** HIGH -- Graph API for authentication context CRUD is GA and documented in Microsoft.Graph.Identity.SignIns module. Allowed values are c1 through c25.
**Dependencies:** Microsoft.Graph PowerShell module, `Policy.ReadWrite.ConditionalAccess` permission
**Source:** [Microsoft Learn: authenticationContextClassReference](https://learn.microsoft.com/en-us/graph/api/resources/authenticationcontextclassreference)

---

### TS-2: Step-Up Conditional Access Policy Deployment

**Why Expected:** Authentication contexts are useless without CA policies that enforce them. Each context needs a policy specifying MFA strength, sign-in frequency, and grant controls. This is the core function.

**What It Does:**
- Deploys CA policies for each authentication context with correct settings:
  - c1 (Financial Transaction): Phishing-resistant MFA, 15-minute sign-in frequency
  - c2 (Data Export): Phishing-resistant MFA, 30-minute sign-in frequency
  - c3 (External API): Phishing-resistant MFA, 30-minute sign-in frequency
  - c4 (Config Change): Phishing-resistant MFA, 30-minute sign-in frequency
  - c5 (Sensitive Query): Standard MFA, 60-minute sign-in frequency
- Deploys in report-only mode by default with explicit enable step
- Excludes break-glass accounts from all policies
- Uses authentication strength grant control (not just builtInControls mfa)

**Complexity:** Medium
**Confidence:** HIGH -- Existing CA Automation templates demonstrate the JSON structure. Step-up policies follow the same pattern but target authentication contexts instead of applications.
**Dependencies:** TS-1 (contexts must exist first), Break-glass account configuration
**Notes:** Template structure should follow CA Automation naming convention: `CA-StepUp-[ContextName]-[Requirement]`

---

### TS-3: Zone-Specific Session Control Validation

**Why Expected:** Different zones have different session requirements per Control 1.23. Administrators need to verify that deployed policies match zone requirements, not just that policies exist.

**What It Does:**
- Validates session lifetime matches zone requirements:
  - Zone 1: 8-hour session, standard MFA, step-up not required
  - Zone 2: 4-hour session, 30-minute fresh auth for data exports/external API
  - Zone 3: 1-hour session, 15-minute fresh auth for all sensitive actions, phishing-resistant MFA
- Validates authentication strength matches zone:
  - Zone 1: Multifactor authentication strength (built-in)
  - Zone 2: Passwordless MFA strength for step-up
  - Zone 3: Phishing-resistant MFA strength (FIDO2/WHfB/CBA only)
- Reports compliance per zone with pass/fail/warning status
- Generates zone compliance matrix output

**Complexity:** Medium
**Confidence:** HIGH -- Zone requirements are explicitly defined in Control 1.23 and the zones-and-tiers framework document. Validation logic is straightforward comparison against known-good values.
**Dependencies:** TS-2 (policies must be deployed to validate)

---

### TS-4: Session Control Drift Detection

**Why Expected:** Session security configuration can be weakened by unauthorized changes (sign-in frequency increased, authentication strength downgraded, policies disabled). This is the same pattern as CA Automation's drift detection but specific to step-up policies.

**What It Does:**
- Captures baseline of step-up CA policies (authentication context, sign-in frequency, authentication strength, persistent browser, grant controls)
- Compares current state against baseline on scheduled runs
- Detects specific drift types:
  - Sign-in frequency weakened (15 min changed to 60 min)
  - Authentication strength downgraded (phishing-resistant to standard MFA)
  - Policy disabled or deleted
  - Authentication context removed from policy conditions
  - New exclusions added
  - Persistent browser mode changed from "never"
- Alerts via Teams webhook with severity classification

**Complexity:** Medium
**Confidence:** HIGH -- Pattern is identical to CA Automation's `Watch-PolicyDrift.ps1`, just with different baseline properties. Can potentially extend that script rather than building new.
**Dependencies:** TS-2, Teams webhook configuration
**Notes:** Should be implemented as an extension of CA Automation's `Watch-PolicyDrift.ps1` to avoid maintaining two drift detection systems.

---

### TS-5: Compliance Evidence Export

**Why Expected:** Financial services organizations must produce evidence for regulatory examinations (FINRA, SEC, OCC). Step-up authentication configuration must be exportable with integrity verification.

**What It Does:**
- Exports authentication context definitions
- Exports step-up CA policy configurations
- Exports authentication strength policy configurations
- Exports sign-in logs filtered for step-up events (where authentication context is populated)
- Generates SHA-256 manifest for integrity verification
- Exports in quarterly periods (matching examination cycles)

**Complexity:** Low
**Confidence:** HIGH -- Pattern established in both CA Automation (`Export-PolicyEvidence.ps1`) and Audit Configuration Validator (`Export-AuditValidationEvidence.ps1`). Same approach, different data scope.
**Dependencies:** TS-1, TS-2
**Notes:** Should integrate with CA Automation's evidence export rather than creating a separate export pipeline. A single `Export-PolicyEvidence.ps1` that covers both general CA and step-up session controls is preferable to two separate exporters.

---

### TS-6: Dry-Run Mode for All Operations

**Why Expected:** CA policy misconfiguration can lock out entire organizations. Every deployment and modification operation must support previewing changes before applying them. This is non-negotiable for FSI environments.

**What It Does:**
- All deployment scripts support `-DryRun` parameter
- Dry run outputs exactly what would be created/modified/deleted
- Dry run validates prerequisites (permissions, dependencies, conflicts)
- Dry run checks for policy conflicts (overlapping conditions that could cause MFA loops)

**Complexity:** Low (built into script design pattern)
**Confidence:** HIGH -- CA Automation already implements this pattern in `Deploy-CAPolicies.ps1`.
**Dependencies:** None (architectural requirement for all scripts)

---

## Differentiators

Features that set this solution apart from basic CA policy management. Not strictly required for function, but highly valued in FSI contexts.

### D-1: Authentication Context-to-Operation Mapping Validation

**Value Proposition:** Goes beyond "are the policies configured correctly?" to ask "are the right operations triggering the right authentication contexts?" This is the gap between infrastructure configuration and application-level integration.

**What It Does:**
- Defines expected mapping: which agent operations should trigger which authentication context
- Queries sign-in logs to verify that authentication contexts are actually being triggered
- Reports on operations that should trigger step-up but have no authentication context in logs
- Reports on unexpected authentication context usage patterns
- Provides coverage analysis: "context c1 was triggered 0 times in 30 days -- is Financial Transaction step-up actually integrated?"

**Complexity:** High
**Confidence:** MEDIUM -- Sign-in logs include `authenticationContextClassReferences` field. The analysis logic is custom but feasible. The challenge is defining the "expected" mapping, which depends on how Copilot Studio/Agent Builder implement authentication context challenges.
**Dependencies:** TS-1, TS-2, Copilot Studio/Agent Builder integration with authentication contexts
**Notes:** This may need to start as a reporting feature and mature into a validation feature as organizations learn what "normal" step-up patterns look like.

---

### D-2: Authentication Strength Policy Management

**Value Proposition:** Control 1.23 requires specific authentication strengths per context severity (phishing-resistant for c1-c4, standard for c5). Custom authentication strength policies enforce exactly the right MFA methods.

**What It Does:**
- Creates custom authentication strength policies:
  - `FSI-Critical-Operations`: FIDO2, Windows Hello for Business, Certificate-based authentication only
  - `FSI-High-Operations`: Passwordless MFA (adds passkeys)
  - `FSI-Medium-Operations`: Standard MFA (all methods)
- Validates that step-up CA policies reference correct authentication strengths
- Reports on users who lack registered methods for required authentication strength
- Identifies users in Zone 3 groups without phishing-resistant MFA methods registered

**Complexity:** Medium
**Confidence:** HIGH -- Authentication strength policies are GA. The `Get-MgPolicyAuthenticationStrengthPolicy` cmdlet lists built-in and custom strengths. Custom creation uses `New-MgPolicyAuthenticationStrengthPolicy`.
**Dependencies:** TS-2 (policies reference these strengths)
**Source:** [Microsoft Learn: Authentication Strengths](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths)

---

### D-3: PIM Integration Validation for Zone 3 Step-Up

**Value Proposition:** Control 1.23 defines PIM + step-up as a combined control for Zone 3 administrative operations. This validates the integration is correctly configured.

**What It Does:**
- Validates PIM settings for AI administration roles match Control 1.23 requirements:
  - Power Platform Admin: 4-hour max activation, approval required
  - Purview Admin: 8-hour max activation, approval required
  - Agent Sponsor (Zone 3): 8-hour max activation, approval required
- Validates PIM activation requires authentication context (c4 for config changes)
- Cross-references PIM activation logs with step-up authentication logs
- Reports on Zone 3 admin actions that occurred without PIM activation

**Complexity:** High
**Confidence:** MEDIUM -- PIM settings are accessible via Graph API (`unifiedRoleManagementPolicyAuthenticationContextRule`). The cross-referencing logic between PIM and sign-in logs is custom but the data sources are well-documented. The agent-identity-templates playbook already demonstrates this pattern in KQL queries.
**Dependencies:** TS-1, TS-2, PIM configured for AI admin roles
**Notes:** PIM is an Entra ID P2 feature. Not all organizations will have this. Should gracefully skip PIM validation when P2 is not licensed.

---

### D-4: Continuous Access Evaluation (CAE) Configuration

**Value Proposition:** CAE provides near-real-time revocation of sessions when security events occur (user disabled, IP changes, risk detected). For FSI, this means compromised sessions are terminated in minutes rather than waiting for token expiry. CAE sessions can remain valid for up to 28 hours with critical events managing revocations instead of fixed time periods.

**What It Does:**
- Validates CAE is enabled for step-up policies (auto-enabled as part of CA but can be explicitly disabled)
- Validates CAE strict enforcement mode for Zone 3 policies
- Reports on CAE effectiveness (token lifetimes, revocation events)
- Validates that resilience defaults are configured appropriately (should be disabled for Zone 3 to prioritize security over availability)

**Complexity:** Low
**Confidence:** HIGH -- CAE is GA and auto-enabled. Configuration is a session control in CA policies. Strict enforcement mode is a configurable option.
**Dependencies:** TS-2
**Source:** [Microsoft Learn: Continuous Access Evaluation](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation)

---

### D-5: Step-Up Session Activity Dashboard Data

**Value Proposition:** Provides operational visibility into how step-up authentication is working in practice -- how often users are challenged, success/failure rates, which contexts trigger most, and latency impact on user experience.

**What It Does:**
- Queries sign-in logs for step-up authentication events
- Aggregates metrics:
  - Step-up challenges per context (c1-c5) per day
  - Success/failure rates per context
  - Average time to complete step-up
  - Users most frequently challenged
  - Step-up bypass attempts (if any)
- Outputs data suitable for Power BI or Compliance Dashboard integration
- Generates weekly summary for governance review

**Complexity:** Medium
**Confidence:** MEDIUM -- Sign-in logs contain the data needed. The aggregation logic is custom. Integration with the existing Compliance Dashboard solution would need a Dataverse table for step-up metrics.
**Dependencies:** TS-2, Sign-in logs enabled, Optionally: Compliance Dashboard for visualization

---

### D-6: Token Protection Validation for Zone 3

**Value Proposition:** Token protection (token binding) prevents stolen tokens from being replayed on different devices. For Zone 3 agents handling regulated data, this is an additional defense against session hijacking. Microsoft has increasingly relied on device-bound sign-in tokens since 2025.

**What It Does:**
- Validates token protection is enabled in Zone 3 step-up policies
- Reports on token protection enforcement status
- Identifies sessions where token protection was not enforced (fallback to unbound tokens)

**Complexity:** Low
**Confidence:** MEDIUM -- Token protection is available as a session control. However, it may have limited applicability for some Power Platform workloads. Need to verify current support scope for Copilot Studio and Agent Builder applications specifically.
**Dependencies:** TS-2, Entra ID P2

---

## Anti-Features

Features to explicitly NOT build. These are common mistakes in this domain or capabilities that would duplicate existing work.

### AF-1: General CA Policy Deployment Engine

**Why Avoid:** The Conditional Access Automation solution already has `Deploy-CAPolicies.ps1` with template-based deployment, dry-run mode, zone filtering, and ELM integration. Building another deployment engine creates maintenance burden and inconsistency.
**What to Do Instead:** Create step-up policy templates in the CA Automation `templates/` directory structure. Use or extend `Deploy-CAPolicies.ps1` to support a `StepUp` template set alongside existing Zone1/Zone2/Zone3 sets.

---

### AF-2: Independent Drift Detection System

**Why Avoid:** CA Automation has `Watch-PolicyDrift.ps1` with baseline capture, Teams alerting, severity classification, and Azure Automation support. A second drift detection system would be confusing to operate.
**What to Do Instead:** Extend `Watch-PolicyDrift.ps1` baseline schema to include authentication context and step-up-specific properties. Add step-up drift types to existing severity classification.

---

### AF-3: Separate Evidence Export Pipeline

**Why Avoid:** Both CA Automation (`Export-PolicyEvidence.ps1`) and Audit Configuration Validator (`Export-AuditValidationEvidence.ps1`) already have evidence export with SHA-256 manifests. A third exporter adds operational complexity.
**What to Do Instead:** Extend `Export-PolicyEvidence.ps1` to include authentication context definitions and step-up policy details in its export scope. Or create a lightweight wrapper that calls the existing exporter with step-up-specific filters.

---

### AF-4: Real-Time Policy Enforcement Agent

**Why Avoid:** Attempting to build an agent that sits in the authentication flow and makes real-time decisions crosses from configuration management into identity infrastructure. This is Microsoft's responsibility (Entra ID enforces CA policies). Building middleware in this path creates security risk and latency.
**What to Do Instead:** Configure policies correctly and monitor their enforcement through sign-in logs. The solution validates configuration, not enforcement.

---

### AF-5: MFA Method Registration Management

**Why Avoid:** Managing which MFA methods users have registered is an IAM operational concern, not a session security configuration concern. It touches user provisioning, helpdesk workflows, and hardware token logistics that are far outside scope.
**What to Do Instead:** Report on authentication method readiness (D-2 identifies users without required methods) but do not manage registration. Link to Microsoft's MFA registration campaign feature for remediation.

---

### AF-6: Application-Level Authentication Context Integration

**Why Avoid:** Making Copilot Studio or Agent Builder agents actually trigger authentication contexts requires application-level development in those platforms, not PowerShell configuration. The configurator manages the Entra ID side, not the application side.
**What to Do Instead:** Document the integration requirements and provide D-1 (mapping validation) to detect when application-level integration is missing. Leave application integration to the agent development team.

---

## Feature Dependencies

```
TS-1: Auth Context Management
  |
  +---> TS-2: Step-Up CA Policy Deployment
  |       |
  |       +---> TS-3: Zone Validation
  |       |
  |       +---> TS-4: Drift Detection
  |       |
  |       +---> TS-5: Evidence Export
  |       |
  |       +---> D-1: Context-to-Operation Mapping
  |       |
  |       +---> D-2: Auth Strength Management
  |       |
  |       +---> D-3: PIM Integration Validation
  |       |
  |       +---> D-4: CAE Configuration
  |       |
  |       +---> D-5: Dashboard Data
  |       |
  |       +---> D-6: Token Protection Validation
  |
  TS-6: Dry-Run Mode (architectural, applies to all)
```

**External Dependencies:**

| Feature | External Dependency | Risk |
|---------|---------------------|------|
| All | Microsoft.Graph PowerShell module | Low -- well-established |
| All | Entra ID P1 licensing | Low -- baseline for CA |
| D-3 | Entra ID P2 licensing (PIM) | Medium -- not all orgs |
| D-6 | Token protection support for Power Platform apps | Medium -- verify current status |
| D-1 | Application integration with auth contexts | High -- depends on Copilot Studio capabilities |
| TS-4, AF-2 | Conditional Access Automation solution | Medium -- must coordinate changes |

**Integration Dependencies with Existing Solutions:**

| Solution | Integration Point | Type |
|----------|-------------------|------|
| Conditional Access Automation | Template directory, drift detection extension, evidence export | Extension |
| Compliance Dashboard | Step-up metrics Dataverse table for D-5 | Data feed |
| Audit Configuration Validator | Pattern for evidence export, SHA-256 manifest | Pattern reuse |
| Environment Lifecycle Management | Zone classification determines which step-up policies apply | Read-only |

---

## MVP Recommendation

For MVP, prioritize the table stakes features that establish the authentication context and step-up policy layer that the existing Conditional Access Automation solution does not cover.

### MVP Phase

**Build (new scripts):**
1. **TS-1: Authentication Context Lifecycle Management** -- Foundation, everything depends on this
2. **TS-2: Step-Up CA Policy Deployment** -- Core value, deploys the 5 step-up policies
3. **TS-3: Zone-Specific Session Control Validation** -- Proves policies match requirements
4. **TS-6: Dry-Run Mode** -- Safety requirement for FSI (architectural, not separate work)
5. **D-2: Authentication Strength Policy Management** -- Ensures correct MFA methods enforced

**Extend (modify existing CA Automation scripts):**
6. **TS-4: Drift Detection** -- Extend CA Automation's `Watch-PolicyDrift.ps1`
7. **TS-5: Evidence Export** -- Extend CA Automation's `Export-PolicyEvidence.ps1`

### Defer to Post-MVP

- **D-1: Context-to-Operation Mapping** -- Requires real usage data; cannot validate without deployed agents triggering step-up. Build after organizations have running agents.
- **D-3: PIM Integration Validation** -- Requires P2 licensing; optional for organizations without PIM.
- **D-4: CAE Configuration** -- Valuable but low effort; can be added in a patch release.
- **D-5: Dashboard Data** -- Needs Compliance Dashboard Dataverse schema extension; coordinate with Compliance Dashboard v2.
- **D-6: Token Protection** -- Verify GA status for Power Platform before investing.

### Implementation Approach

The Session Security Configurator should be implemented as an **extension module within the Conditional Access Automation solution**, not as a separate solution in the repository. This means:

1. New scripts in `conditional-access-automation/scripts/` prefixed with `SessionSecurity-` or in a `session-security/` subdirectory
2. New templates in `conditional-access-automation/templates/step-up/` directory
3. Extended baseline schema in existing drift detection
4. Extended export scope in existing evidence export
5. Documentation in `conditional-access-automation/docs/session-security.md`

This approach avoids solution sprawl and leverages the existing infrastructure while adding the step-up authentication layer that Control 1.23 requires.

---

## Sources

### Official Documentation (HIGH confidence)
- [Microsoft Learn: Session Controls](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-session) -- Complete session control reference including sign-in frequency, persistent browser, CAE, token protection, application enforced restrictions, Conditional Access App Control, Global Secure Access security profile, and resilience defaults
- [Microsoft Learn: authenticationContextClassReference API](https://learn.microsoft.com/en-us/graph/api/resources/authenticationcontextclassreference) -- Graph API for auth context CRUD (c1-c25 allowed values)
- [Microsoft Learn: New-MgIdentityConditionalAccessAuthenticationContextClassReference](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.signins/new-mgidentityconditionalaccessauthenticationcontextclassreference) -- PowerShell cmdlet for context creation
- [Microsoft Learn: Authentication Strengths](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths) -- Built-in and custom auth strength policies
- [Microsoft Learn: Continuous Access Evaluation](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation) -- CAE reference (28-hour token lifetime with critical event revocation)
- [Microsoft Learn: Session Lifetime Policies](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime) -- Sign-in frequency configuration
- [Microsoft Learn: Conditional Access APIs and PowerShell](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-apis) -- Graph API automation patterns
- [Microsoft Learn: Phishing-Resistant MFA for Admin Roles](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-admin-phish-resistant-mfa) -- Phishing-resistant MFA enforcement patterns
- [Microsoft Learn: Developer Guide for Authentication Context](https://learn.microsoft.com/en-us/entra/identity-platform/developer-guide-conditional-access-authentication-context) -- Application integration guidance

### Internal Sources (HIGH confidence -- existing codebase)
- Control 1.23: Step-Up Authentication for Agent Operations (`docs/controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md`)
- Control 1.11: Conditional Access and Phishing-Resistant MFA (`docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`)
- Conditional Access Automation solution (`FSI-AgentGov-Solutions/conditional-access-automation/`) -- README, templates, scripts, docs
- Conditional Access Agent Identity Templates playbook (`docs/playbooks/control-implementations/1.11/conditional-access-agent-templates.md`)
- Control 1.23 PowerShell Setup playbook (`docs/playbooks/control-implementations/1.23/powershell-setup.md`)
- Control 1.23 Portal Walkthrough playbook (`docs/playbooks/control-implementations/1.23/portal-walkthrough.md`)
- Zones and Tiers framework (`docs/framework/zones-and-tiers.md`)
- Solutions Integration mapping (`docs/framework/solutions-integration.md`)
- Solutions Index (`docs/reference/solutions-index.md`)

### Community Sources (MEDIUM confidence)
- [Paradigm Security: Top 10 CA Policies 2026](https://paradigmsecurity.nl/blog/conditional-access-policies-for-enhanced-security/) -- Best practices for session security
- [Practical365: Managing CA Policies with PowerShell](https://practical365.com/conditional-access-policies-powershell/) -- PowerShell automation patterns
- [CIPP GitHub: CA Template Drift Detection Feature Request](https://github.com/KelvinTegelaar/CIPP/issues/4772) -- Community drift detection patterns for CA templates
- [ConditionalAccessDocumentation on GitHub](https://github.com/nicolonsky/ConditionalAccessDocumentation) -- Community tool for CA documentation with PowerShell

---

*Research completed: 2026-02-06 | Confidence: HIGH for table stakes (Graph API verified, Control 1.23 specifications clear), MEDIUM for differentiators (PIM cross-referencing, operation mapping depend on preview features and usage data)*
