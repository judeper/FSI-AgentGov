# Conditional Access Agent Identity Templates

> Sample Conditional Access (CA) policy templates for [Control 1.11 — Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).
>
> These templates are **starting points**, not turnkey deployments. Every application ID, group object ID, named-location ID, and service-principal target **must be verified in the deploying tenant** before policies are promoted out of report-only mode. The cost of a fail-open CA policy in a US financial-services tenant is severe: silent non-enforcement creates audit findings under FINRA, SEC 17a-4, NYDFS Part 500, and the GLBA Safeguards Rule.

---

## 1. Overview

This playbook provides Microsoft Graph–schema CA policy templates that govern:

- **Agent makers** (humans authoring agents in Copilot Studio, Power Apps, Power Automate, and Microsoft 365 Copilot Studio)
- **Agent administrators** (Power Platform Admins, Copilot Studio Admins, AI governance leads)
- **Workload identities** that publish, run, or manage agents (CI/CD service principals, agent runtime SPs, agent identities surfaced under the Entra Agent ID preview)

All templates align to the three-zone agent governance model documented in Control 1.11.

### Zone-to-template mapping

| Zone | Persona | Required templates | Optional |
|------|---------|--------------------|----------|
| **Zone 1 — Personal** | Individual makers building personal-productivity agents | CA-001 (maker MFA), CA-005 (BG exclusion), CA-006 (user-risk) | CA-007 (CAE) |
| **Zone 2 — Team** | Departmental publishers | CA-002 (Zone 2 phishing-resistant MFA), CA-003 (12h sign-in frequency), CA-004 (no persistent browser), CA-005, CA-006, CA-007 | CA-WI-001 (CI/CD SP) |
| **Zone 3 — Enterprise** | Enterprise admins, regulated-data agents | CA-002 (Zone 3 variant), CA-003 (≤4h sign-in frequency), CA-004, CA-005, CA-006, CA-007, CA-WI-001, CA-WI-002 (agent-identity), CA-WI-003 (Microsoft-managed baseline) | — |

!!! danger "Hedged scope"
    These templates help support — they do not guarantee — compliance with FINRA WSP, SEC 17a-4, NYDFS §500.12, GLBA Safeguards Rule §314.4(c)(5), OCC Heightened Standards, and Federal Reserve SR 11-7 expectations for AI-system access controls. Organizations should verify each policy against their own regulatory interpretations and obtain CISO sign-off before enforcement.

---

## 2. Prerequisites

### License matrix

| Capability | Required SKU | Used by templates |
|------------|--------------|--------------------|
| Conditional Access (user identity) | Microsoft Entra ID P1 | CA-001 through CA-005, CA-007 |
| Risk-based CA (user risk, sign-in risk) | Microsoft Entra ID P2 | CA-006 |
| Authentication strengths (Phishing-resistant MFA) | Entra ID P1 | CA-002, CA-003 |
| **Conditional Access for Workload Identities (CA-WID)** | **Microsoft Entra Workload Identities Premium** (per service principal, per month) | CA-WI-001, CA-WI-002 |
| Custom security attributes for SP filtering | Entra ID P1 + RBAC role `Attribute Definition Administrator` | CA-WI-002 |
| Continuous Access Evaluation (CAE) | Entra ID P1 + supported clients | CA-007 |
| Token Protection (sign-in token) | Entra ID P2 | CA-003 (Zone 3) |
| Microsoft-managed agent baseline | Entra Agent ID preview entitlement | CA-WI-003 |

!!! warning "Workload Identities Premium is licensed per service principal"
    Conditional Access for Workload Identities (CA-WID) requires **Microsoft Entra Workload Identities Premium**, billed per-SP per-month. Without this SKU, `New-MgIdentityConditionalAccessPolicy` calls that target service principals will be **rejected at deployment** (not silently fail). Confirm the SKU is assigned and the count of agent SPs is budgeted before deploying CA-WI-001 / CA-WI-002. As of April 2026, Workload Identities Premium availability **lags in GCC High and DoD sovereign clouds** — verify cloud parity before production rollout.

### RBAC roles needed

| Action | Required role |
|--------|---------------|
| Create / modify CA policies | Entra Conditional Access Admin **or** Entra Security Admin |
| Read CA policies (review) | Entra Security Reader |
| Manage authentication strengths | Entra Authentication Policy Admin |
| Define / assign custom security attributes | Attribute Definition Administrator + Attribute Assignment Administrator |
| Manage break-glass accounts | Entra Global Admin (constrained to BG account scope) |
| Promote a report-only policy to enabled | Entra Conditional Access Admin (with PIM activation recommended) |

### Pre-existing artifacts

- **Two cloud-only break-glass accounts** already provisioned, password-vaulted, and FIDO2-key-vaulted (per Section 5, CA-005 / Anti-pattern table). The break-glass security group `sg-breakglass-accounts` already exists and contains both accounts.
- Authentication strength **Phishing-resistant MFA** (built-in `00000000-0000-0000-0000-000000000004`) verified present in tenant.
- Security groups for makers and admins per zone (`sg-agent-makers-zone1/2/3`, `sg-agent-admins-zone3`).
- Agent inventory complete (see [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)).
- Diagnostic settings forwarding `SignInLogs`, `AADServicePrincipalSignInLogs`, and `AuditLogs` to Log Analytics or Sentinel (required for CA-006 evidence and CA-WID monitoring).

---

## 3. Critical pre-deployment step: verify application IDs in your tenant

!!! danger "First-party application IDs MUST be verified per tenant before deployment"
    The application IDs reproduced in Section 5 are Microsoft's **commercial-cloud, well-known** app IDs as of April 2026 publication. They are **not stable across sovereign clouds** (GCC, GCC High, DoD), and Microsoft has historically renamed and re-issued IDs across the Bing Chat → Microsoft 365 Chat → Microsoft 365 Copilot rebranding sequence. A CA policy that pins an application ID **the tenant does not actually expose** is accepted by Microsoft Graph and **matches zero sign-ins** — i.e., it fails open silently. Always run the discovery snippet below, compare results to the templates, and substitute the IDs returned by your tenant.

### App ID discovery script (run before every deployment)

```powershell
# Resolve current first-party application IDs in YOUR tenant before deploying CA policies.
# Run from a session with Directory.Read.All consent.
Connect-MgGraph -Scopes "Application.Read.All","Directory.Read.All" -NoWelcome

$expectedSurfaces = @(
    'Microsoft Power Apps',
    'Microsoft Power Platform',
    'Power Virtual Agents Service',
    'Power Virtual Agents Web',
    'Microsoft 365 Chat',
    'Microsoft 365 Copilot',
    'Microsoft Copilot Studio',
    'Common Data Service',
    'Microsoft Graph PowerShell',
    'Power Automate'
)

$resolved = foreach ($name in $expectedSurfaces) {
    Get-MgServicePrincipal -Filter "displayName eq '$name'" -ConsistencyLevel eventual -All |
        Select-Object @{n='Surface';e={$name}}, DisplayName, AppId, Id
}

$resolved | Format-Table -AutoSize
$resolved | Export-Csv -Path "tenant-firstparty-appids-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
```

### Reference IDs used in this playbook (commercial cloud, verify before use)

| Surface | App ID (commercial cloud) | Notes |
|---------|---------------------------|-------|
| Microsoft Power Apps (PowerApps Web / Service) | `475226c6-020e-4fb2-8a90-7a972cbfc1d4` | Verify via discovery script |
| Microsoft Power Platform / PPAC | `7df0a125-d3be-4c96-aa54-591f83ff541c` | Verify via discovery script |
| Power Virtual Agents Service (Copilot Studio runtime) | `38e15ad7-bb74-4ac3-9aef-f4b720b51c20` | Verify; preview-cloud variants exist |
| Power Virtual Agents Web (Copilot Studio Maker) | `96ff4394-9197-43aa-b393-6a41652e21f8` | Verify |
| Microsoft 365 Chat / M365 Copilot (chat surface) | `fb8d773d-7ef8-4ec0-a117-179f88add510` | Confirm against `Microsoft 365 Chat` SP — historical rebrand churn |
| Common Data Service / Dataverse | `00000007-0000-0000-c000-000000000000` | Stable across clouds |
| Microsoft Graph PowerShell | `14d82eec-204b-4c2f-b7e8-296a70dab67e` | Used by deployment automation; consider excluding from CA-002/003 in narrow break-glass scenarios |

### Common authentication-strength IDs

| Strength | ID |
|----------|-----|
| Multifactor authentication (built-in) | `00000000-0000-0000-0000-000000000002` |
| Passwordless MFA | `00000000-0000-0000-0000-000000000003` |
| **Phishing-resistant MFA** (FIDO2 / Windows Hello for Business / Certificate-based) | `00000000-0000-0000-0000-000000000004` |

!!! note "Synced passkeys are not AAL3-equivalent"
    The Phishing-resistant MFA built-in strength accepts FIDO2 passkeys, but **synced (cloud-backed) passkeys** do not meet NIST SP 800-63B AAL3. For Zone 3 admins and any scenario requiring AAL3-equivalent assurance, configure a **custom authentication strength** that allows only **device-bound FIDO2** authenticators and Windows Hello for Business (cloud Kerberos trust). Windows Hello for Business **key trust is deprecating**; use cloud Kerberos trust for new deployments.

---

## 4. Deployment ring discipline

Every template in Section 5 ships with `state = "enabledForReportingButNotEnforced"`. This is intentional. The recommended promotion path is:

1. **Deploy** to report-only.
2. **Validate** for ≥7 days against `SigninLogs` to confirm the policy matches the intended user/app/condition set with no unexpected `notApplied` results.
3. **Run What-If** (Section 7) for representative pilot users including a break-glass simulated principal.
4. **Promote** to `state = "enabled"` only after CISO or designate sign-off.

To promote:

```powershell
$policy = Get-MgIdentityConditionalAccessPolicy -Filter "displayName eq 'CA-002-Zone2-Maker-PhishingResistant'"
Update-MgIdentityConditionalAccessPolicy -ConditionalAccessPolicyId $policy.Id -State "enabled"
```

---

## 5. Policy templates (Microsoft Graph JSON)

Each template is presented as a Graph-schema JSON body suitable for `New-MgIdentityConditionalAccessPolicy -BodyParameter` or a direct `POST /identity/conditionalAccess/policies` call. Replace `<...>` placeholders with tenant-specific object IDs.

---

### CA-001 — Zone 3 maker MFA via Phishing-resistant Authentication Strength

**Purpose:** Require phishing-resistant MFA for Zone 3 makers when authoring agents.
**Control mapping:** Control 1.11 → Zone 3 maker authentication baseline. Helps support NYDFS §500.12 and FINRA WSP authentication expectations for privileged AI authoring.

```json
{
  "displayName": "CA-001-Zone3-Maker-PhishingResistantMFA",
  "description": "CA-001 | Zone 3 | Control 1.11 | Phishing-resistant MFA for Zone 3 agent makers in Copilot Studio, Power Apps, and Power Automate authoring surfaces.",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeGroups": ["<object-id-of-sg-agent-makers-zone3>"],
      "excludeGroups": ["<object-id-of-sg-breakglass-accounts>"]
    },
    "applications": {
      "includeApplications": [
        "475226c6-020e-4fb2-8a90-7a972cbfc1d4",
        "96ff4394-9197-43aa-b393-6a41652e21f8",
        "7df0a125-d3be-4c96-aa54-591f83ff541c"
      ]
    },
    "clientAppTypes": ["all"]
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["compliantDevice"],
    "authenticationStrength": {
      "id": "00000000-0000-0000-0000-000000000004"
    }
  }
}
```

!!! note "Grant operator semantics"
    `operator = "AND"` requires **all** listed controls to be satisfied. `authenticationStrength` is treated as an additional control — do **not** also list `"mfa"` in `builtInControls` when `authenticationStrength` is present (B7 anti-pattern). When using `operator = "OR"` with multiple `builtInControls`, any one satisfies the grant.

---

### CA-002 — Zone 2 maker MFA

**Purpose:** Require MFA (with phishing-resistant strength preferred) for Zone 2 makers.
**Control mapping:** Control 1.11 → Zone 2 maker baseline. Helps support GLBA Safeguards Rule §314.4(c)(5).

```json
{
  "displayName": "CA-002-Zone2-Maker-MFA",
  "description": "CA-002 | Zone 2 | Control 1.11 | MFA for Zone 2 agent makers in Copilot Studio Maker and Power Apps.",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeGroups": ["<object-id-of-sg-agent-makers-zone2>"],
      "excludeGroups": ["<object-id-of-sg-breakglass-accounts>"]
    },
    "applications": {
      "includeApplications": [
        "475226c6-020e-4fb2-8a90-7a972cbfc1d4",
        "96ff4394-9197-43aa-b393-6a41652e21f8"
      ]
    },
    "clientAppTypes": ["browser", "mobileAppsAndDesktopClients"]
  },
  "grantControls": {
    "operator": "OR",
    "authenticationStrength": {
      "id": "00000000-0000-0000-0000-000000000004"
    }
  }
}
```

---

### CA-003 — Sign-in frequency for Copilot Studio author portal (Zone 3 ≤ 4h, Zone 2 ≤ 12h)

**Purpose:** Force re-authentication on a fixed interval for maker portals to limit token-theft blast radius.
**Control mapping:** Control 1.11 → session controls. Helps support FFIEC IT Examination Handbook session-management expectations.

**Zone 3 variant (4 hours):**

```json
{
  "displayName": "CA-003-Zone3-Maker-SignInFrequency-4h",
  "description": "CA-003 | Zone 3 | Control 1.11 | 4-hour sign-in frequency + token protection for Zone 3 maker portals.",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeGroups": ["<object-id-of-sg-agent-makers-zone3>"],
      "excludeGroups": ["<object-id-of-sg-breakglass-accounts>"]
    },
    "applications": {
      "includeApplications": [
        "475226c6-020e-4fb2-8a90-7a972cbfc1d4",
        "96ff4394-9197-43aa-b393-6a41652e21f8",
        "7df0a125-d3be-4c96-aa54-591f83ff541c"
      ]
    },
    "clientAppTypes": ["all"]
  },
  "sessionControls": {
    "signInFrequency": {
      "frequencyInterval": "timeBased",
      "value": 4,
      "type": "hours",
      "isEnabled": true
    },
    "tokenProtection": {
      "isEnabled": true
    }
  }
}
```

**Zone 2 variant (12 hours):** identical body with `value = 12` and the Zone 2 group.

!!! warning "FrequencyInterval is mandatory"
    The `signInFrequency` session control **requires** `frequencyInterval` (`timeBased` or `everyTime`). Omitting it causes the request to be rejected — or, in some Graph beta builds, silently coerced to `everyTime`, which **ignores `value` and `type` entirely**. Either failure mode results in your intended frequency not being enforced.

---

### CA-004 — Persistent browser session = Never persistent (Zone 3 maker portals)

**Purpose:** Block "Stay signed in" for maker portals to limit cookie-theft persistence.
**Control mapping:** Control 1.11 → Zone 3 session hardening.

```json
{
  "displayName": "CA-004-Zone3-Maker-NoPersistentBrowser",
  "description": "CA-004 | Zone 3 | Control 1.11 | Disallow persistent browser sessions for Zone 3 maker portals.",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeGroups": ["<object-id-of-sg-agent-makers-zone3>"],
      "excludeGroups": ["<object-id-of-sg-breakglass-accounts>"]
    },
    "applications": {
      "includeApplications": [
        "475226c6-020e-4fb2-8a90-7a972cbfc1d4",
        "96ff4394-9197-43aa-b393-6a41652e21f8",
        "7df0a125-d3be-4c96-aa54-591f83ff541c"
      ]
    },
    "clientAppTypes": ["browser"]
  },
  "sessionControls": {
    "persistentBrowser": {
      "mode": "never",
      "isEnabled": true
    }
  }
}
```

---

### CA-005 — Break-glass exclusion pattern (apply to All users, **Exclude** break-glass)

!!! danger "Never apply a Block grant directly to break-glass accounts"
    A CA policy with `users.includeGroups = sg-breakglass-accounts` and `grantControls.builtInControls = ["block"]` **locks out emergency access**. Block always wins among grant controls — no other policy can "invert" it. The correct pattern is to apply restrictive policies to **All users with the BG group excluded**, plus a separate high-severity Sentinel/KQL alert on any sign-in by either BG account.

**Purpose:** Demonstrate the canonical exclusion shape that every restrictive policy in CA-001 through CA-007 must follow.
**Control mapping:** Control 1.11 → emergency access. Helps support NYDFS §500.7 access governance and FFIEC business-continuity expectations.

**Two-account pattern (operational requirements):**

| Requirement | Configuration |
|-------------|---------------|
| Account count | **Two** cloud-only accounts (`breakglass1@<tenant>.onmicrosoft.com`, `breakglass2@<tenant>.onmicrosoft.com`) |
| Federation | None — accounts must not depend on on-prem AD or external IdP |
| Authenticator | FIDO2 hardware key per account, **stored in physically separate safes** |
| Password | 128+ character random, sealed dual-control envelope |
| MFA registration | FIDO2 only (no SMS, no Authenticator app) |
| Testing cadence | Quarterly alternating — test BG1 in Q1/Q3, BG2 in Q2/Q4 |
| Monitoring | Sentinel alert (Critical) on every sign-in attempt (success or failure) |
| Excluded from | Every restrictive CA policy (every template in Section 5 except CA-WI-* which target SPs) |

**Reference exclusion shape (apply on every restrictive policy):**

```json
"users": {
  "includeUsers": ["All"],
  "excludeGroups": ["<object-id-of-sg-breakglass-accounts>"]
}
```

**BG monitoring KQL (Sentinel scheduled rule, run every 5 minutes):**

```kql
SigninLogs
| where TimeGenerated > ago(10m)
| where UserPrincipalName in~ (
    "breakglass1@<tenant>.onmicrosoft.com",
    "breakglass2@<tenant>.onmicrosoft.com"
  )
| project TimeGenerated, UserPrincipalName, IPAddress, Location,
          AppDisplayName, ResultType, ResultDescription, DeviceDetail
| extend AlertSeverity = "Critical",
         AlertMessage  = strcat("Break-glass account sign-in: ", UserPrincipalName)
```

---

### CA-006 — Token-theft / user-risk response (User risk = High → password change + reauth)

**Purpose:** Force credential reset and reauthentication when Entra ID Protection raises a High user-risk signal (token theft, leaked credentials, anomalous sign-ins).
**Control mapping:** Control 1.11 → risk-based response. Requires Entra ID P2.

```json
{
  "displayName": "CA-006-AllUsers-UserRiskHigh-PasswordChange",
  "description": "CA-006 | All zones | Control 1.11 | High user risk requires secure password change + phishing-resistant reauth.",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": ["All"],
      "excludeGroups": ["<object-id-of-sg-breakglass-accounts>"]
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "userRiskLevels": ["high"],
    "clientAppTypes": ["all"]
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["passwordChange"],
    "authenticationStrength": {
      "id": "00000000-0000-0000-0000-000000000004"
    }
  },
  "sessionControls": {
    "signInFrequency": {
      "frequencyInterval": "everyTime",
      "isEnabled": true
    }
  }
}
```

!!! note "`everyTime` does not require `value` / `type`"
    When `frequencyInterval = "everyTime"`, the `value` and `type` properties are not used. This is the schema-correct way to force reauthentication on every request — do not set `value = 0`.

---

### CA-007 — CAE strict-enforcement verification policy

**Purpose:** Enforce Continuous Access Evaluation in strict mode so revoked tokens, disabled accounts, and password resets propagate to live sessions in near-real-time.
**Control mapping:** Control 1.11 → session integrity. Helps support FFIEC session-revocation expectations.

```json
{
  "displayName": "CA-007-AllUsers-CAE-StrictEnforcement",
  "description": "CA-007 | All zones | Control 1.11 | Strict CAE enforcement on all interactive sign-ins.",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": ["All"],
      "excludeGroups": ["<object-id-of-sg-breakglass-accounts>"]
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "clientAppTypes": ["browser", "mobileAppsAndDesktopClients"]
  },
  "sessionControls": {
    "continuousAccessEvaluation": {
      "mode": "strictEnforcement"
    }
  }
}
```

!!! note "CAE client support"
    Strict-enforcement CAE requires CAE-aware client applications. Older clients fall back to long-lived tokens. Validate against `SigninLogs` `TokenIssuerType` and `IsTokenProtectionEnabled` columns before promoting from report-only.

---

### CA-WI-001 — SP-targeted CA WID for Power Automate publishing pipelines

**Purpose:** Restrict CI/CD service principals that publish Power Automate flows or Copilot Studio agents to known network locations and require client-certificate authentication.
**Control mapping:** Control 1.11 → CI/CD identity governance. Helps support SEC 17a-4 evidentiary integrity for automated change pipelines.

!!! warning "Workload Identities Premium SKU required"
    CA-WI-001 will **fail at deployment** without Microsoft Entra Workload Identities Premium assigned. Verify SKU before applying. Each targeted SP consumes one license-month.

```json
{
  "displayName": "CA-WI-001-CICD-SP-CompliantNetworkOnly",
  "description": "CA-WI-001 | All zones | Control 1.11 | Block CI/CD service principals signing in from outside compliant named locations.",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "clientApplications": {
      "includeServicePrincipals": [
        "<service-principal-object-id-1>",
        "<service-principal-object-id-2>"
      ],
      "excludeServicePrincipals": []
    },
    "applications": {
      "includeApplications": [
        "7df0a125-d3be-4c96-aa54-591f83ff541c",
        "00000007-0000-0000-c000-000000000000"
      ]
    },
    "locations": {
      "includeLocations": ["All"],
      "excludeLocations": ["<object-id-of-named-location-AzureDevOpsHosted>"]
    },
    "clientAppTypes": ["all"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

!!! note "Compliant network is location-based, not a grant control"
    There is **no** `compliantNetworkLocation` member in the `conditionalAccessGrantControl` enum (the valid members are `block`, `mfa`, `compliantDevice`, `domainJoinedDevice`, `approvedApplication`, `compliantApplication`, `passwordChange`, `unknownFutureValue`). Compliant-network enforcement is implemented by **excluding** the compliant named location from `includeLocations` and applying a `block` grant — exactly the shape above.

---

### CA-WI-002 — Agent identity scoped via `AgentZone` custom security attribute

**Purpose:** Apply Block when an agent service principal is rated `servicePrincipalRiskLevel = high`, scoped to Zone 2/Zone 3 agents via a custom security attribute filter so per-SP enumeration is not required.
**Control mapping:** Control 1.11 → agent-identity risk response. Helps support Federal Reserve SR 11-7 model risk management for agent-as-actor authorization decisions.

**Prerequisite:** Define a custom security attribute set (e.g., `AgentGov`) with attribute `AgentZone` (string, allowed values `1` / `2` / `3`) and assign it to in-scope agent service principals.

```json
{
  "displayName": "CA-WI-002-AgentSP-Zone2or3-HighRisk-Block",
  "description": "CA-WI-002 | Zone 2 + Zone 3 | Control 1.11 | Block high-risk agent service principals filtered by AgentZone custom security attribute.",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "clientApplications": {
      "includeServicePrincipals": ["ServicePrincipalsInMyTenant"],
      "servicePrincipalFilter": {
        "mode": "include",
        "rule": "CustomSecurityAttribute.AgentGov.AgentZone -in [\"2\", \"3\"]"
      }
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "servicePrincipalRiskLevels": ["high"],
    "clientAppTypes": ["all"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

!!! note "There is no `userType eq 'AgenticUser'` filter"
    The `conditionalAccessUsers` schema has no `userType` filter, and there is no `AgenticUser` value. Agents are targeted via `clientApplications.includeServicePrincipals` and (recommended for scale) `servicePrincipalFilter` with a custom security attribute rule, **not** through the `users` block. `servicePrincipalRiskLevels` requires Workload Identities Premium and Entra ID Protection coverage of workload identities.

---

### CA-WI-003 — Microsoft-managed agent baseline (read-only — surface via `Source = Microsoft` filter)

**Purpose:** Inventory and verify the Microsoft-managed Conditional Access baseline policies that ship with Entra Agent ID. These are **not authored by the tenant** — they are surfaced read-only and should be reviewed quarterly to confirm the baseline still aligns with FSI policy.
**Control mapping:** Control 1.11 → Microsoft-managed baseline reconciliation.

!!! note "Surfacing Microsoft-managed policies"
    Microsoft-managed CA policies do not appear in a separate menu. In the Entra portal, open **Protection → Conditional Access → Policies** and filter **Source = Microsoft**. Programmatically:

```powershell
# List all Microsoft-managed CA policies (templated baselines)
Get-MgIdentityConditionalAccessPolicy -All |
    Where-Object { $_.TemplateId -ne $null -or $_.AdditionalProperties.source -eq 'microsoft' } |
    Select-Object DisplayName, State, ModifiedDateTime, TemplateId |
    Format-Table -AutoSize
```

These baselines must not be edited by tenant admins. If a baseline is too restrictive for a documented FSI scenario, file a Microsoft support exception rather than disabling the policy — disabling a Microsoft-managed baseline must be documented in the agent registry with CISO sign-off and quarterly review.

---

## 6. JSON deployment via `New-MgIdentityConditionalAccessPolicy`

### Apply a single template

```powershell
Connect-MgGraph -Scopes "Policy.ReadWrite.ConditionalAccess","Policy.Read.All","Application.Read.All" -NoWelcome

$body = Get-Content -Raw -Path ".\ca-002-zone2-maker-mfa.json" | ConvertFrom-Json -AsHashtable
New-MgIdentityConditionalAccessPolicy -BodyParameter $body
```

### Apply all templates in a directory (report-only)

```powershell
Get-ChildItem -Path ".\templates" -Filter "ca-*.json" | ForEach-Object {
    Write-Host "Deploying $($_.Name)..." -ForegroundColor Cyan
    $body = Get-Content -Raw -Path $_.FullName | ConvertFrom-Json -AsHashtable
    # Force report-only on first deploy regardless of file content
    $body.state = "enabledForReportingButNotEnforced"
    try {
        New-MgIdentityConditionalAccessPolicy -BodyParameter $body
        Write-Host "  OK" -ForegroundColor Green
    } catch {
        Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}
```

### Idempotent re-deploy (update if displayName exists)

```powershell
function Set-CaPolicy {
    param($Body)
    $existing = Get-MgIdentityConditionalAccessPolicy -Filter "displayName eq '$($Body.displayName)'"
    if ($existing) {
        Update-MgIdentityConditionalAccessPolicy -ConditionalAccessPolicyId $existing.Id -BodyParameter $Body
        Write-Host "Updated: $($Body.displayName)" -ForegroundColor Yellow
    } else {
        New-MgIdentityConditionalAccessPolicy -BodyParameter $Body
        Write-Host "Created: $($Body.displayName)" -ForegroundColor Green
    }
}
```

---

## 7. Validation: What-If test cases per policy

Run each test through the Entra **What If** tool (Protection → Conditional Access → What If) **and** programmatically via the beta `evaluate` endpoint. Document outcomes in the agent registry change ticket before promoting to `enabled`.

| Policy | Test principal | Test app | Expected matched policies | Expected outcome |
|--------|----------------|----------|--------------------------|------------------|
| CA-001 | Zone 3 maker | Power Apps Maker | CA-001, CA-003, CA-004, CA-007 | Phishing-resistant MFA + compliant device required; 4h sign-in frequency; no persistent browser |
| CA-002 | Zone 2 maker | Copilot Studio Maker | CA-002, CA-003 (12h variant), CA-007 | Phishing-resistant MFA; 12h sign-in frequency |
| CA-003 (Z3) | Zone 3 maker | Copilot Studio Maker | CA-001, CA-003, CA-004 | 4h reauth enforced |
| CA-004 | Zone 3 maker via browser | Power Apps | CA-001, CA-003, CA-004 | "Stay signed in" suppressed |
| **CA-005** | **`breakglass1` account** | **Any app** | **No restrictive policy matches** | **Sign-in succeeds with no MFA prompt; Sentinel critical alert fires** |
| CA-006 | Standard user with simulated High user risk | Any app | CA-006, CA-007 | Password change + phishing-resistant reauth required |
| CA-007 | Any user, CAE-aware client | Any app | CA-007 | Strict CAE active in token claims |
| CA-WI-001 | CI/CD SP from non-compliant IP | Power Platform | CA-WI-001 | Block |
| CA-WI-001 | CI/CD SP from compliant named location | Power Platform | CA-WI-001 | Allow (excluded location) |
| CA-WI-002 | Agent SP with `AgentZone = 3` and risk = High | Any app | CA-WI-002 | Block |
| CA-WI-002 | Agent SP with `AgentZone = 1` and risk = High | Any app | No match | Allow (out of scope) |

### Programmatic What-If

```powershell
$payload = @{
    signInIdentity = @{ "@odata.type" = "#microsoft.graph.userSignIn"; userId = "<test-user-object-id>" }
    appId          = "475226c6-020e-4fb2-8a90-7a972cbfc1d4"
    clientAppType  = "browser"
    ipAddress      = "203.0.113.10"
    deviceInfo     = @{ isCompliant = $true; trustType = "azureAD" }
} | ConvertTo-Json -Depth 8

Invoke-MgGraphRequest -Method POST `
    -Uri 'https://graph.microsoft.com/beta/identity/conditionalAccess/evaluate' `
    -Body $payload -ContentType 'application/json'
```

---

## 8. Anti-patterns reference (CA policies that fail open or lock out)

| # | Anti-pattern | Why it fails | Correct pattern |
|---|--------------|--------------|-----------------|
| 1 | **B1.** `users.includeGroups = sg-breakglass-accounts` + `builtInControls = ["block"]` | Locks out emergency access; Block always wins | Apply restrictive policies to All users with `excludeGroups` on the BG group; alert via Sentinel |
| 2 | **B2.** Pinning unverified or copied app GUIDs | Graph accepts unknown GUIDs silently → policy matches no sign-ins → **fails open** | Run the discovery script in Section 3; pin only IDs returned in your tenant |
| 3 | **B3.** `builtInControls = ["compliantNetworkLocation"]` | Not a member of the grant-control enum → 400 / silent reject | Use `locations.excludeLocations` + `builtInControls = ["block"]` |
| 4 | **B4.** `signInFrequency` without `frequencyInterval` | Rejected or coerced to `everyTime` (your value/type ignored) | Always set `frequencyInterval = "timeBased"` (with `value` + `type`) or `"everyTime"` |
| 5 | **B5a.** Group display name in `includeServicePrincipals` | Schema expects SP object IDs or `"ServicePrincipalsInMyTenant"`; string returns 400 | Enumerate SP `id` values or use `servicePrincipalFilter` with custom security attribute |
| 6 | **B5b.** Deploying CA-WID without Workload Identities Premium | Deployment fails (or, in some preview windows, policy is created but never evaluated) | Verify SKU before deployment; document per-SP license cost |
| 7 | **B6.** `userType eq 'AgenticUser'` filter | No such filter exists in the CA users schema | Use `clientApplications.servicePrincipalFilter` with a custom security attribute (e.g., `AgentZone`) |
| 8 | **B7.** Mixing `authenticationStrength` and `builtInControls = ["mfa"]` | Double-MFA semantics; unpredictable when combined with other controls | When `authenticationStrength` is set, do **not** also list `"mfa"` in `builtInControls` |
| 9 | Promoting a policy from report-only to enabled without ≥7 days of sign-in log validation | Unforeseen `notApplied` patterns lock out legitimate users | Validate against `SigninLogs` for ≥7 days; run What-If for pilot principals + BG simulation |
| 10 | Pinning `applications.includeApplications = ["Office365"]` and assuming Power Platform is covered | The Office 365 app group does not include Power Platform / Copilot Studio surfaces | Enumerate first-party app IDs explicitly per the tenant discovery script |
| 11 | Using synced (cloud-backed) FIDO2 passkeys for AAL3-equivalent assurance | Synced passkeys are not device-bound and do not meet NIST AAL3 | Define a custom authentication strength restricted to device-bound FIDO2 + WHfB cloud Kerberos trust |
| 12 | Targeting WHfB **key trust** in new deployments | Key trust is deprecating | Use **cloud Kerberos trust** for new WHfB deployments |
| 13 | Editing a Microsoft-managed CA baseline policy | Tenant edits to Microsoft-managed policies are rejected or overwritten | File a Microsoft support exception; document override decisions in the agent registry with CISO sign-off |
| 14 | Skipping the `clientAppTypes` condition | Default behaviour omits legacy auth coverage in some scenarios; explicit is safer | Always set `clientAppTypes` explicitly (`["all"]` or the specific subset) |
| 15 | Using a single break-glass account | No redundancy if the account / FIDO2 key is compromised or lost | Always provision **two** BG accounts in physically separate safes; alternate quarterly testing |
| 16 | Pinning commercial-cloud app IDs in GCC High / DoD tenants | Sovereign-cloud app IDs differ; policy matches nothing in the wrong cloud | Run discovery script in the **target sovereign cloud**; never copy IDs across clouds |

---

## 9. Cross-references

- [Control 1.11 — Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) — parent control
- [Portal Walkthrough](portal-walkthrough.md) — step-by-step Entra portal configuration for the templates above
- [PowerShell Setup](powershell-setup.md) — automation scripts (group creation, attribute definition, BG provisioning)
- [Verification Testing](verification-testing.md) — test cases, evidence collection, sign-in log validation queries
- [Troubleshooting](troubleshooting.md) — common deployment errors and resolutions
- [Agent Identity Architecture](../../../framework/agent-identity-architecture.md) — agent identity model and zone definitions
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — prerequisite agent inventory

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
