# Technology Stack - Session Security Configurator

**Project:** FSI Agent Governance Framework - Session Security Configurator Solution
**Research Date:** 2026-02-06
**Scope:** Stack additions for automated session security enforcement via Conditional Access policies
**Builds On:** Existing Conditional Access Automation solution (v1.0.0)

---

## Executive Summary

The Session Security Configurator extends the existing Conditional Access Automation solution to add session-specific configuration enforcement, drift detection, authentication context management, and authentication strength policy integration. The core finding is that **no new PowerShell modules are required** -- the existing `Microsoft.Graph.Identity.SignIns` module (part of Microsoft.Graph SDK) already contains all necessary cmdlets for session control management, authentication context CRUD, and authentication strength policy operations.

**Key Finding:** The existing Conditional Access Automation solution already uses `Microsoft.Graph.Identity.SignIns` for CA policy CRUD. Session controls (`signInFrequency`, `persistentBrowser`) are properties of the `conditionalAccessPolicy` resource type, not separate APIs. Authentication contexts (`c1-c99`) and authentication strength policies are also managed through the same module.

**Critical Caveat:** The `frequencyInterval: "everyTime"` setting (needed for Zone 3 risky user re-authentication) does NOT work in the Graph v1.0 API despite being documented. This is a known, unresolved issue (GitHub #647, filed June 2024, still open). The beta API must be used for this specific feature.

**Recommendation:** Extend the existing Conditional Access Automation solution rather than building a new solution. Add session validation, drift detection, authentication context configuration, and authentication strength enforcement to the existing scripts.

---

## Recommended Stack

### Primary Module: Microsoft.Graph.Identity.SignIns

| Component | Version | Purpose | Why |
|-----------|---------|---------|-----|
| **Microsoft.Graph** (meta-package) | 2.35.1 | Parent package for all Graph modules | Latest GA, published 2026-02-05 |
| **Microsoft.Graph.Identity.SignIns** | 2.35.1 | CA policy CRUD, auth contexts, auth strengths | Already used by existing CA Automation solution |
| **Microsoft.Graph.Authentication** | 2.35.1 | `Connect-MgGraph` for authentication | Required dependency |
| **Microsoft.Graph.Applications** | 2.35.1 | Service principal registration | Used by existing `Register-ServicePrincipal.ps1` |

**Installation:**
```powershell
# Install specific sub-modules (avoid full Microsoft.Graph meta-package for performance)
Install-Module Microsoft.Graph.Identity.SignIns -MinimumVersion 2.35.0 -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Authentication -MinimumVersion 2.35.0 -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Applications -MinimumVersion 2.35.0 -Scope CurrentUser -Force
```

**Rationale:**
- Version 2.35.1 is the current latest release (published 2026-02-05 per PowerShell Gallery)
- The existing CA Automation solution specifies minimum version 2.0.0 -- update to 2.35.0+ for current session control properties
- Sub-module installation is preferred over full `Microsoft.Graph` meta-package (43 sub-modules, many unneeded)
- PowerShell 5.1+ compatible (both Core and Desktop editions supported)

**Important Warning:** Microsoft.Graph SDK versions 2.26.x had significant regressions that broke Azure Automation runbook compatibility. Version 2.35.1 resolves these issues. If using Azure Automation, test thoroughly before deploying.

**Sources:**
- [PowerShell Gallery - Microsoft.Graph 2.35.1](https://www.powershellgallery.com/packages/Microsoft.Graph/2.35.1) (published 2026-02-05, verified)
- [PowerShell Gallery - Microsoft.Graph.Identity.SignIns 2.34.0](https://www.powershellgallery.com/packages/Microsoft.Graph.Identity.signins/2.34.0)
- [GitHub - Microsoft Graph PowerShell SDK Releases](https://github.com/microsoftgraph/msgraph-sdk-powershell/releases)

---

### Beta Module: Microsoft.Graph.Beta.Identity.SignIns

| Component | Version | Purpose | Why |
|-----------|---------|---------|-----|
| **Microsoft.Graph.Beta.Identity.SignIns** | 2.x | `frequencyInterval: "everyTime"` support, CAE session controls, secureSignInSession | v1.0 API does not support `everyTime` frequency interval |

**Installation:**
```powershell
Install-Module Microsoft.Graph.Beta.Identity.SignIns -Scope CurrentUser -Force
```

**When to Use Beta vs v1.0:**

| Capability | v1.0 API | Beta API | Which to Use |
|------------|----------|----------|--------------|
| CA policy CRUD | Yes | Yes | **v1.0** |
| signInFrequency (hours/days) | Yes | Yes | **v1.0** |
| signInFrequency (everyTime) | Documented but BROKEN | Yes | **Beta** (required) |
| persistentBrowser | Yes | Yes | **v1.0** |
| Authentication contexts | Yes | Yes | **v1.0** |
| Authentication strengths | Yes | Yes | **v1.0** |
| continuousAccessEvaluation session control | No | Yes | **Beta** (if needed) |
| secureSignInSession | No | Yes | **Beta** (if needed) |
| globalSecureAccessFilteringProfile | No | Yes | **Beta** (not needed) |
| What-If evaluation (`Test-MgBetaIdentityConditionalAccess`) | No | Yes | **Beta** (validation) |

**Strategy:** Use v1.0 API for everything except `frequencyInterval: "everyTime"` and What-If evaluation. This minimizes beta API dependency while getting features that are not yet in v1.0.

**Known Issue -- `everyTime` in v1.0:**
- GitHub Issue: [microsoftgraph/msgraph-metadata#647](https://github.com/microsoftgraph/msgraph-metadata/issues/647)
- Status: Open, filed June 2024, last updated May 2025, label "ToTriage"
- Error: `400 Bad Request` with message "The policy you are trying to create or update contains preview features. Use the Beta endpoint."
- Impact: Policies created via Beta API become "beta-locked" and cannot be managed via v1.0 API
- Mitigation: Create Zone 3 "everyTime" policies via Beta API, manage all other policies via v1.0

**Sources:**
- [GitHub Issue #647 - everyTime not supported in v1.0](https://github.com/microsoftgraph/msgraph-metadata/issues/647) (verified, still open)
- [Microsoft Learn - signInFrequencySessionControl](https://learn.microsoft.com/en-us/graph/api/resources/signinfrequencysessioncontrol?view=graph-rest-1.0)

---

### Supporting Libraries (Existing, No Changes Needed)

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| **Az.KeyVault** | 5.0.0+ | Credential storage for service principal | Already in existing solution prerequisites |
| **Az.Accounts** | 3.0.0+ | Azure authentication for Key Vault access | Already in existing solution prerequisites |
| **MSAL.PS** | 4.x | OAuth token acquisition (if direct REST calls needed) | Already validated in framework stack |

**No new supporting libraries are required.** The Session Security Configurator operates entirely within the Microsoft Graph API surface, which the existing Microsoft.Graph SDK handles natively.

---

## Graph API Endpoints

### Conditional Access Policy Management (Existing)

These endpoints are already used by the existing CA Automation solution. Listing for completeness.

| Operation | Endpoint | Method | Used By |
|-----------|----------|--------|---------|
| List policies | `/v1.0/identity/conditionalAccess/policies` | GET | `Test-PolicyCompliance.ps1` |
| Get policy | `/v1.0/identity/conditionalAccess/policies/{id}` | GET | `Test-PolicyCompliance.ps1` |
| Create policy | `/v1.0/identity/conditionalAccess/policies` | POST | `Deploy-CAPolicies.ps1` |
| Update policy | `/v1.0/identity/conditionalAccess/policies/{id}` | PATCH | `Deploy-CAPolicies.ps1` |
| Delete policy | `/v1.0/identity/conditionalAccess/policies/{id}` | DELETE | Not currently used |

### Session Control Properties (NEW -- Core of This Solution)

The `sessionControls` object within a CA policy contains these properties:

**v1.0 API (`conditionalAccessSessionControls`):**

| Property | Type | Description |
|----------|------|-------------|
| `signInFrequency` | signInFrequencySessionControl | Sign-in frequency enforcement |
| `persistentBrowser` | persistentBrowserSessionControl | Browser session persistence |
| `applicationEnforcedRestrictions` | applicationEnforcedRestrictionsSessionControl | App-level restrictions (Exchange/SharePoint only) |
| `cloudAppSecurity` | cloudAppSecuritySessionControl | Defender for Cloud Apps session proxy |
| `disableResilienceDefaults` | Boolean | Disable Microsoft Entra ID session extension during outages |

**signInFrequencySessionControl Properties:**

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `isEnabled` | Boolean | true/false | Enable this session control |
| `type` | signinFrequencyType | `days`, `hours` | Unit for frequency value |
| `value` | Int32 | numeric | Number of days/hours |
| `authenticationType` | signInFrequencyAuthenticationType | `primaryAndSecondaryAuthentication`, `secondaryAuthentication`, `unknownFutureValue` | What auth is re-required |
| `frequencyInterval` | signInFrequencyInterval | `timeBased`, `everyTime`, `unknownFutureValue` | Interval mode (`everyTime` requires Beta API) |

**persistentBrowserSessionControl Properties:**

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `isEnabled` | Boolean | true/false | Enable this session control |
| `mode` | persistentBrowserSessionMode | `always`, `never` | Whether browser sessions persist |

**Beta-Only Session Controls:**

| Property | Type | Description |
|----------|------|-------------|
| `continuousAccessEvaluation` | continuousAccessEvaluationSessionControl | CAE configuration per policy |
| `secureSignInSession` | secureSignInSessionControl | Bind sessions to device |
| `globalSecureAccessFilteringProfile` | globalSecureAccessFilteringProfileSessionControl | GSA profile linkage |

**Zone-to-Session-Control Mapping:**

| Zone | signInFrequency | persistentBrowser | authenticationType | API Version |
|------|----------------|-------------------|-------------------|-------------|
| Zone 1 | value: 8, type: hours | Not configured | primaryAndSecondaryAuthentication | v1.0 |
| Zone 2 | value: 4, type: hours | Not configured | primaryAndSecondaryAuthentication | v1.0 |
| Zone 3 | value: 1, type: hours | mode: never | primaryAndSecondaryAuthentication | v1.0 |
| Zone 3 (risky users) | frequencyInterval: everyTime | mode: never | primaryAndSecondaryAuthentication | **Beta required** |

**Sources:**
- [Microsoft Learn - conditionalAccessSessionControls](https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesssessioncontrols?view=graph-rest-1.0) (verified)
- [Microsoft Learn - signInFrequencySessionControl](https://learn.microsoft.com/en-us/graph/api/resources/signinfrequencysessioncontrol?view=graph-rest-1.0) (verified)
- [Microsoft Learn - Session Lifetime Policies](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime) (verified)

---

### Authentication Context Management (NEW)

Authentication contexts enable step-up authentication for sensitive operations (Control 1.23).

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List contexts | `/v1.0/identity/conditionalAccess/authenticationContextClassReferences` | GET |
| Get context | `/v1.0/identity/conditionalAccess/authenticationContextClassReferences/{id}` | GET |
| Create/Update context | `/v1.0/identity/conditionalAccess/authenticationContextClassReferences/{id}` | PATCH |
| Delete context | `/v1.0/identity/conditionalAccess/authenticationContextClassReferences/{id}` | DELETE |

**Available Context IDs:** `c1` through `c99` (tenant-scoped, NOT globally consistent)

**authenticationContextClassReference Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `id` | String | Context ID (e.g., "c1") |
| `displayName` | String | Friendly name shown in admin UX |
| `description` | String | Policy description (secondary text in UX) |
| `isAvailable` | Boolean | Whether published and ready for app use |

**Recommended Authentication Context Mapping (from Control 1.23):**

| Context ID | Display Name | Step-Up Requirement | Sign-In Frequency |
|------------|-------------|---------------------|-------------------|
| `c1` | Financial Transaction | Phishing-resistant MFA | 15 minutes |
| `c2` | Data Export | Phishing-resistant MFA | 30 minutes |
| `c3` | External API Call | Phishing-resistant MFA | 30 minutes |
| `c4` | Config Change | Phishing-resistant MFA | 30 minutes |
| `c5` | Sensitive Query | Standard MFA | 1 hour |

**PowerShell Cmdlets:**

| Cmdlet | Module | Purpose |
|--------|--------|---------|
| `Get-MgIdentityConditionalAccessAuthenticationContextClassReference` | Microsoft.Graph.Identity.SignIns | List/get auth contexts |
| `New-MgIdentityConditionalAccessAuthenticationContextClassReference` | Microsoft.Graph.Identity.SignIns | Create auth context |
| `Update-MgIdentityConditionalAccessAuthenticationContextClassReference` | Microsoft.Graph.Identity.SignIns | Update auth context |

**Required Permissions:**

| Permission | Type | Least Privileged | Higher Privileged |
|------------|------|-----------------|-------------------|
| AuthenticationContext.Read.All | Application | Read contexts | -- |
| AuthenticationContext.ReadWrite.All | Application | Create/update contexts | Policy.ReadWrite.ConditionalAccess |
| Policy.ReadWrite.ConditionalAccess | Application | Full CA management | Covers auth context operations too |

**Important:** `Policy.ReadWrite.ConditionalAccess` is a superset that covers authentication context operations. Since the existing CA Automation service principal already has this permission, no additional permissions are needed for auth context management.

**Licensing:** Entra ID P1 required. Auth contexts are NOT available in Entra ID Free.

**Sources:**
- [Microsoft Learn - Create/Update authenticationContextClassReference](https://learn.microsoft.com/en-us/graph/api/authenticationcontextclassreference-update?view=graph-rest-1.0) (verified)
- [Microsoft Learn - Authentication Context Developer Guide](https://learn.microsoft.com/en-us/entra/identity-platform/developer-guide-conditional-access-authentication-context) (verified)
- [Microsoft Learn - Get-MgIdentityConditionalAccessAuthenticationContextClassReference](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.signins/get-mgidentityconditionalaccessauthenticationcontextclassreference?view=graph-powershell-1.0) (verified)

---

### Authentication Strength Policies (NEW)

Authentication strength policies enforce phishing-resistant MFA for Zone 3 step-up scenarios.

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List policies | `/v1.0/policies/authenticationStrengthPolicies` | GET |
| Get policy | `/v1.0/policies/authenticationStrengthPolicies/{id}` | GET |
| Create custom policy | `/v1.0/policies/authenticationStrengthPolicies` | POST |
| List auth method modes | `/v1.0/identity/conditionalAccess/authenticationStrength/authenticationMethodModes` | GET |

**Built-In Authentication Strengths:**

| Policy | ID | Allowed Methods |
|--------|----|-----------------|
| Multifactor authentication | (system) | All MFA methods |
| Passwordless MFA | (system) | FIDO2, Windows Hello, certificate-based |
| Phishing-resistant MFA | (system) | FIDO2, Windows Hello, certificate-based (hardware-bound only) |

**Integration with CA Policies:**

Authentication strength is set in `grantControls.authenticationStrength` (NOT in `grantControls.builtInControls`):

```json
{
  "grantControls": {
    "authenticationStrength": {
      "id": "<authentication-strength-policy-id>"
    }
  }
}
```

**Constraint:** You CANNOT use both `builtInControls: ["mfa"]` and `authenticationStrength` in the same CA policy. They are mutually exclusive. The existing Zone 3 templates use `builtInControls: ["mfa"]` -- these must be migrated to `authenticationStrength` for phishing-resistant enforcement.

**Zone-to-Authentication-Strength Mapping:**

| Zone | Current (builtInControls) | Target (authenticationStrength) | Migration Required |
|------|--------------------------|--------------------------------|-------------------|
| Zone 1 | `["mfa"]` (risk-based) | MFA strength (built-in) | Optional |
| Zone 2 | `["mfa"]` | MFA strength (built-in) | Optional |
| Zone 3 | `["mfa", "compliantDevice"]` | Phishing-resistant MFA strength + `["compliantDevice"]` | **Yes** |

**Custom Authentication Strength (if needed):**

Organizations can create up to 15 custom authentication strength policies. A custom policy combining FIDO2 + compliant device could be useful for Zone 3.

**Required Permissions:** Same `Policy.ReadWrite.ConditionalAccess` already granted to existing service principal.

**Sources:**
- [Microsoft Learn - Authentication Strengths API Overview](https://learn.microsoft.com/en-us/graph/api/resources/authenticationstrengths-overview?view=graph-rest-1.0) (verified)
- [Microsoft Learn - Authentication Strengths Concept](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths) (verified)
- [Microsoft Learn - Require Phishing-Resistant MFA for Admins](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-admin-phish-resistant-mfa)

---

## Graph API Permissions (Consolidated)

### Existing Service Principal Permissions (from CA Automation)

| Permission | Type | Purpose | Already Granted |
|------------|------|---------|-----------------|
| `Policy.Read.All` | Application | Read CA policies | Yes |
| `Policy.ReadWrite.ConditionalAccess` | Application | Create/update CA policies | Yes |
| `Application.Read.All` | Application | Read app registrations | Yes |
| `Directory.Read.All` | Application | Read directory objects | Yes |
| `AuditLog.Read.All` | Application | Read audit logs (evidence) | Yes |

### Additional Permissions Needed for Session Security Configurator

| Permission | Type | Purpose | Already Covered By |
|------------|------|---------|-------------------|
| Auth context read/write | Application | Manage authentication contexts | `Policy.ReadWrite.ConditionalAccess` (superset) |
| Auth strength read/write | Application | Manage authentication strength policies | `Policy.ReadWrite.ConditionalAccess` (superset) |

**No additional permissions required.** The existing `Policy.ReadWrite.ConditionalAccess` application permission covers all session control, authentication context, and authentication strength operations.

### Delegated Permissions (For Interactive Operations)

For human-in-the-loop scenarios (e.g., initial deployment verification):

| Permission | Purpose | Role Required |
|------------|---------|---------------|
| `Policy.ReadWrite.ConditionalAccess` | Interactive CA management | Conditional Access Administrator |
| `Policy.Read.All` | Read-only audit | Security Reader |

**Sources:**
- [Graph Permissions - Policy.ReadWrite.ConditionalAccess](https://graphpermissions.merill.net/permission/Policy.ReadWrite.ConditionalAccess) (verified -- covers auth contexts and auth strengths)

---

## Continuous Access Evaluation (CAE)

**Status:** Auto-enabled by default for most tenants. No additional configuration needed for session security enforcement.

**Configuration via CA policy session controls:** CAE can be customized (enabled/disabled) per Conditional Access policy via the `continuousAccessEvaluation` session control -- but this property is **Beta-only** in the Graph API.

**Recommendation:** Do NOT manage CAE via Graph API in this solution. CAE is enabled by default and should remain so. If an organization needs to customize CAE behavior, do it manually via Entra portal or defer to a future phase using the Beta API.

**Key CAE behaviors relevant to session security:**
- Exchange Online, SharePoint Online, Teams, and Microsoft Graph synchronize CA policies for real-time evaluation
- Token revocation is near-instant (not dependent on token lifetime)
- CAE for workload identities (service principals) supported for Microsoft Graph as resource provider
- Starting January 2026, self-service authentication method changes require MFA if last auth was >10 minutes ago

**Sources:**
- [Microsoft Learn - Continuous Access Evaluation](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation) (verified, updated July 2025)
- [Microsoft Learn - CAE for Workload Identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation-workload)

---

## What NOT to Add

| Technology | Why Excluded |
|------------|--------------|
| **AzureAD PowerShell module** | Deprecated since March 2024. Microsoft.Graph SDK is the replacement. |
| **MSOnline PowerShell module** | Deprecated. Does not support CA policies. |
| **Microsoft365DSC** | Desired State Configuration framework is overkill for targeted session validation. Introduces unnecessary complexity and slower execution. |
| **ExchangeOnlineManagement** | Not needed for CA session controls. Session controls are Graph API operations, not Exchange operations. |
| **PnP.PowerShell** | SharePoint-focused. No CA or session control capabilities. |
| **Separate REST client library** | Microsoft.Graph SDK handles all REST calls. No need for raw `Invoke-RestMethod` for Graph API. |
| **Terraform/Bicep** | Infrastructure-as-code for CA policies is emerging but immature. Graph API via PowerShell matches existing solution patterns. |
| **Custom PowerShell binary module** | Unnecessary complexity. Script modules with existing cmdlets are sufficient. |

**Anti-Patterns to Avoid:**

- **Do NOT** use the full `Microsoft.Graph` meta-package (43 modules). Install only the 3 sub-modules needed.
- **Do NOT** mix v1.0 and Beta cmdlets in the same script without clear separation. Use Beta only for `everyTime` frequency and What-If.
- **Do NOT** create authentication contexts with hardcoded IDs across tenants. Context IDs (c1-c99) are tenant-scoped and may already be in use.
- **Do NOT** use `builtInControls: ["mfa"]` and `authenticationStrength` in the same CA policy -- they are mutually exclusive and will return a 400 error.
- **Do NOT** rely on `disableResilienceDefaults: true` in FSI environments unless explicitly required by security policy. Disabling resiliency defaults means users cannot access resources during Entra ID outages.

---

## Integration with Existing CA Automation Solution

### What Already Exists (Do NOT Rebuild)

The existing `conditional-access-automation/` solution provides:

| Script | Capability | Reuse Strategy |
|--------|-----------|----------------|
| `Deploy-CAPolicies.ps1` | Template-based CA policy deployment | **Extend** with session validation checks |
| `Test-PolicyCompliance.ps1` | Policy existence and state checking | **Extend** with session control validation |
| `Register-ServicePrincipal.ps1` | Service principal with correct permissions | **Reuse as-is** (permissions already sufficient) |
| `templates/CA-*.json` | Zone-specific policy templates | **Update** with authentication strength settings |

### What to Add (New Capabilities)

| New Script | Purpose | Integration Point |
|------------|---------|-------------------|
| `Set-SessionBaseline.ps1` | Define expected session controls per zone | New -- references template JSON |
| `Test-SessionCompliance.ps1` | Validate session controls match baseline | Extends `Test-PolicyCompliance.ps1` pattern |
| `Watch-SessionDrift.ps1` | Detect session control changes | Extends `Watch-PolicyDrift.ps1` pattern |
| `Deploy-AuthContexts.ps1` | Create authentication contexts (c1-c5) | New -- uses `New-MgIdentityConditionalAccessAuthenticationContextClassReference` |
| `Export-SessionEvidence.ps1` | Export session config for compliance | Extends `Export-PolicyEvidence.ps1` pattern |

### Template Updates Needed

Existing templates need updates for authentication strength (replacing `builtInControls: ["mfa"]`):

**Zone 3 Template Change:**
```json
// BEFORE (current)
{
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["mfa", "compliantDevice"]
  }
}

// AFTER (with authentication strength)
{
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["compliantDevice"],
    "authenticationStrength": {
      "id": "<phishing-resistant-mfa-policy-id>"
    }
  }
}
```

---

## Licensing Requirements

| License | Required For | Already Required |
|---------|-------------|-----------------|
| **Entra ID P1** | Conditional Access, authentication contexts | Yes (existing prereq) |
| **Entra ID P2** | Risk-based policies, sign-in risk | Yes (existing prereq for Zone 1) |
| **M365 E5 Security** (optional) | Advanced threat protection, enhanced risk signals | Optional (existing prereq) |

No new licensing requirements. The Session Security Configurator operates within the same license tier as the existing CA Automation solution.

---

## Version Pinning Recommendations

| Package | Minimum Version | Maximum Version | Rationale |
|---------|-----------------|-----------------|-----------|
| Microsoft.Graph.Identity.SignIns | 2.35.0 | 2.x | Current stable, all session control properties available |
| Microsoft.Graph.Authentication | 2.35.0 | 2.x | Match Identity.SignIns version |
| Microsoft.Graph.Applications | 2.35.0 | 2.x | Match Identity.SignIns version |
| Microsoft.Graph.Beta.Identity.SignIns | 2.35.0 | 2.x | Required only for `everyTime` and What-If |
| Az.KeyVault | 5.0.0 | 5.x | Existing solution compatibility |
| Az.Accounts | 3.0.0 | 3.x | Existing solution compatibility |
| PowerShell | 7.0 | 7.x | Match existing `#Requires -Version 7.0` pattern |

**Pin Strategy:**
- Pin Microsoft.Graph sub-modules to same version (avoid version skew across sub-modules)
- Use `#Requires -Modules @{ ModuleName="Microsoft.Graph.Identity.SignIns"; ModuleVersion="2.35.0" }` for fail-fast
- Allow minor version updates (2.35.0 to 2.35.x) for security patches
- Test before upgrading major version (future 3.x release)

---

## PowerShell Cmdlet Reference (Session Security)

### CA Policy Session Controls

| Cmdlet | Purpose | API Version |
|--------|---------|-------------|
| `New-MgIdentityConditionalAccessPolicy` | Create policy with session controls | v1.0 |
| `Update-MgIdentityConditionalAccessPolicy` | Modify session controls on existing policy | v1.0 |
| `Get-MgIdentityConditionalAccessPolicy` | Read policy including session controls | v1.0 |

### Authentication Contexts

| Cmdlet | Purpose | API Version |
|--------|---------|-------------|
| `Get-MgIdentityConditionalAccessAuthenticationContextClassReference` | List/get auth contexts | v1.0 |
| `New-MgIdentityConditionalAccessAuthenticationContextClassReference` | Create auth context | v1.0 |
| `Update-MgIdentityConditionalAccessAuthenticationContextClassReference` | Update auth context | v1.0 |

### Authentication Strengths

| Cmdlet | Purpose | API Version |
|--------|---------|-------------|
| `Get-MgPolicyAuthenticationStrengthPolicy` | List auth strength policies | v1.0 |
| `New-MgPolicyAuthenticationStrengthPolicy` | Create custom auth strength | v1.0 |
| `Update-MgPolicyAuthenticationStrengthPolicy` | Update auth strength | v1.0 |

### Beta-Only Cmdlets

| Cmdlet | Purpose | Why Beta |
|--------|---------|---------|
| `New-MgBetaIdentityConditionalAccessPolicy` | Create policy with `everyTime` frequency | v1.0 bug #647 |
| `Update-MgBetaIdentityConditionalAccessPolicy` | Update policy with `everyTime` frequency | v1.0 bug #647 |
| `Test-MgBetaIdentityConditionalAccess` | What-If policy evaluation | Not yet in v1.0 |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Graph SDK | Microsoft.Graph PowerShell SDK 2.35.x | Direct REST API via `Invoke-RestMethod` | SDK handles auth, pagination, error handling; REST is more verbose with no benefit |
| Auth strength | Built-in "Phishing-resistant MFA" policy | Custom auth strength policy | Built-in is sufficient for Zone 3; custom adds management overhead |
| Drift detection | PowerShell scheduled task / Azure Automation | Power Automate cloud flow | PowerShell matches existing solution pattern; Power Automate adds platform dependency |
| State management | JSON baseline files + SHA-256 hashing | Dataverse table for state | JSON baseline matches existing `Watch-PolicyDrift.ps1` pattern; simpler, no Dataverse dependency |
| Template format | JSON templates (existing pattern) | Bicep/ARM templates | JSON templates already exist and work; Bicep adds toolchain dependency |

---

## Security Considerations

### Service Principal Authentication

The existing CA Automation service principal supports both certificate and client secret authentication. For session security enforcement:

- **Production:** Use certificate-based authentication via `Connect-MgGraph -ClientId $appId -TenantId $tenantId -CertificateThumbprint $thumbprint`
- **Key Vault:** Store certificate in Azure Key Vault; rotate every 90 days maximum
- **Least privilege:** `Policy.ReadWrite.ConditionalAccess` is required (cannot be scoped further)

### Audit Trail

All CA policy modifications via Graph API are automatically logged in:
- Entra ID Audit Logs (`/auditLogs/directoryAudits`)
- Activity: "Update conditional access policy", "Add conditional access policy"
- Actor: Service principal application ID
- Details: Before/after values for changed properties

### Break-Glass Protection

Session security policies MUST exclude break-glass accounts. The existing template pattern handles this, but the Session Security Configurator must validate exclusions are present during compliance checks.

---

## Confidence Assessment

| Area | Confidence | Source Quality | Notes |
|------|------------|----------------|-------|
| Microsoft.Graph SDK 2.35.1 | **HIGH** | PowerShell Gallery (verified 2026-02-05) | Version confirmed, publication date verified |
| Session control properties (v1.0) | **HIGH** | Microsoft Learn official docs | All property types, enums, and structures verified |
| `everyTime` bug in v1.0 | **HIGH** | GitHub Issue #647 (verified open) | Confirmed still unresolved as of May 2025 |
| Authentication context API | **HIGH** | Microsoft Learn official docs | CRUD endpoints and permissions verified |
| Authentication strength API | **HIGH** | Microsoft Learn official docs | Built-in policies and integration pattern verified |
| Beta session controls (CAE, secureSignIn) | **MEDIUM** | Microsoft Learn Beta docs | Beta API subject to change without notice |
| `Policy.ReadWrite.ConditionalAccess` scope | **HIGH** | graphpermissions.merill.net (verified) | Confirmed to cover auth contexts and strengths |
| No new permissions needed | **HIGH** | Cross-referenced existing SP permissions with new requirements | All operations covered by existing permission set |

**Overall Confidence: HIGH** -- All core components verified with official Microsoft documentation and PowerShell Gallery. The only MEDIUM confidence item is Beta-only session controls (CAE, secureSignInSession), which are not critical-path features.

**Key Uncertainty:**
- When will `frequencyInterval: "everyTime"` be fixed in v1.0 API? No ETA from Microsoft. Plan for Beta dependency.
- Microsoft.Graph SDK v3.x timeline? No announcement. Current 2.x line is stable.

---

## Open Questions / Validation Needed

1. **`everyTime` beta lock-in:** After creating a Zone 3 policy via Beta API with `frequencyInterval: "everyTime"`, can it still be READ via v1.0 API? Or is it completely invisible to v1.0 operations? TEST in non-production tenant.

2. **Authentication strength + compliantDevice:** Can `authenticationStrength` and `builtInControls: ["compliantDevice"]` coexist in the same `grantControls` object? The documentation says you cannot combine `builtInControls: ["mfa"]` with `authenticationStrength`, but `compliantDevice` is not `mfa`. VERIFY via test deployment.

3. **Auth context pre-existing usage:** If a tenant already uses `c1` for a non-FSI purpose, the Session Security Configurator must detect this before overwriting. Add discovery check in `Deploy-AuthContexts.ps1`.

4. **Zone 3 template migration:** Updating Zone 3 templates from `builtInControls: ["mfa"]` to `authenticationStrength` is a breaking change for existing deployments. Define migration path (create new policy, validate, delete old policy).

5. **What-If validation:** Can `Test-MgBetaIdentityConditionalAccess` simulate session control enforcement for a specific user/application combination? TEST to determine if it returns session control details in the evaluation result.

---

## Sources (Consolidated)

**Microsoft Graph API:**
- [conditionalAccessPolicy resource (v1.0)](https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy?view=graph-rest-1.0)
- [conditionalAccessSessionControls resource (v1.0)](https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesssessioncontrols?view=graph-rest-1.0)
- [conditionalAccessSessionControls resource (Beta)](https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesssessioncontrols?view=graph-rest-beta)
- [signInFrequencySessionControl resource (v1.0)](https://learn.microsoft.com/en-us/graph/api/resources/signinfrequencysessioncontrol?view=graph-rest-1.0)
- [Create conditionalAccessPolicy (v1.0)](https://learn.microsoft.com/en-us/graph/api/conditionalaccessroot-post-policies?view=graph-rest-1.0)

**Authentication Contexts:**
- [Create/Update authenticationContextClassReference](https://learn.microsoft.com/en-us/graph/api/authenticationcontextclassreference-update?view=graph-rest-1.0)
- [Authentication Context Developer Guide](https://learn.microsoft.com/en-us/entra/identity-platform/developer-guide-conditional-access-authentication-context)
- [Get-MgIdentityConditionalAccessAuthenticationContextClassReference](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.signins/get-mgidentityconditionalaccessauthenticationcontextclassreference?view=graph-powershell-1.0)
- [New-MgIdentityConditionalAccessAuthenticationContextClassReference](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.signins/new-mgidentityconditionalaccessauthenticationcontextclassreference?view=graph-powershell-1.0)

**Authentication Strengths:**
- [Authentication Strengths API Overview](https://learn.microsoft.com/en-us/graph/api/resources/authenticationstrengths-overview?view=graph-rest-1.0)
- [Authentication Strengths Concept](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths)
- [Require Phishing-Resistant MFA](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-admin-phish-resistant-mfa)

**Session Lifetime:**
- [Session Lifetime Policies](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime)
- [Session Lifetime Concepts](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-session-lifetime)

**Continuous Access Evaluation:**
- [CAE Overview](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation)
- [CAE for Workload Identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation-workload)

**PowerShell SDK:**
- [PowerShell Gallery - Microsoft.Graph 2.35.1](https://www.powershellgallery.com/packages/Microsoft.Graph/2.35.1)
- [GitHub - Microsoft Graph PowerShell SDK](https://github.com/microsoftgraph/msgraph-sdk-powershell)
- [Managing CA Policies with PowerShell (Practical365)](https://practical365.com/conditional-access-policies-powershell/)

**Permissions:**
- [Policy.ReadWrite.ConditionalAccess scope](https://graphpermissions.merill.net/permission/Policy.ReadWrite.ConditionalAccess)
- [Microsoft Graph Permissions Reference](https://learn.microsoft.com/en-us/graph/permissions-reference)

**Known Issues:**
- [GitHub Issue #647 - everyTime not supported in v1.0](https://github.com/microsoftgraph/msgraph-metadata/issues/647)
- [Graph SDK v2.26 Issues (Practical365)](https://office365itpros.com/2025/02/25/graph-sdk-v2-26-issues/)

**Existing Solution:**
- [Conditional Access Automation README](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-06 | Initial research for Session Security Configurator solution |
