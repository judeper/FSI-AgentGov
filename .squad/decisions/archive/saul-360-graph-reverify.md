# Saul — Verification Verdict for Issue #360

**Subject:** Re-verify Microsoft Graph beta Conditional Access JSON schema for the two agent-identity policy examples in `docs/framework/agent-identity-architecture.md` (Policy Examples 1 & 2, ~lines 219–276).
**Verifier:** Saul (FSI-AgentGov review squad)
**Date verified:** 2026-06-04
**Verification scope:** Read-only confirmation of beta Graph schema as published on Microsoft Learn today. **All findings stamped "beta — subject to change."**
**Charter discipline:** This file contains evidence + a corrected payload spec only. A separate author applies the fix.

---

## TL;DR for the author

The prior verifier (Livingston) was directionally correct that the two policy JSON blocks in the doc do not match the published Graph beta schema — but **one of Livingston's specific replacement claims is itself wrong, and another claim ("UI-only, no Graph schema for All agent identities") is now refuted by the published beta schema**. Live evidence from Microsoft Learn:

1. `agentIdRiskLevels` is published in beta as a **single-string flag-enum on `conditions`**, not as a JSON array. The canonical wire form is `"agentIdRiskLevels": "high"` (and `"high,medium"` for multi-select), NOT `["high"]`.
2. Agent-identity targeting **IS** publicly schematized in beta — it lives on `conditionalAccessClientApplications` (not on `conditionalAccessUsers`). Fields: `includeAgentIdServicePrincipals` / `excludeAgentIdServicePrincipals` (with `"All"` sentinel supported, demonstrated by MS Learn POST examples) and `agentIdServicePrincipalFilter` (custom-security-attribute rule).
3. `excludeApplications.attributeFilter` is fabricated. Filtering by attribute is a sibling `applicationFilter` (single field on `applications`) — not a per-side sub-object.

Both Policy Examples can therefore be **replaced with verified Graph-API-ready JSON** rather than kept behind the disclaimer. See "Corrected JSON" section at the bottom.

---

## Q1 — Risk-based blocking: `agentIdRiskLevels`

**Verdict: VERIFIED (with one correction to Livingston's claim).**

### Sub-claims evaluated

| Sub-claim | Verdict |
|---|---|
| `agentIdRiskLevels` exists on `conditionalAccessConditionSet` in **beta**. | ✅ Verified |
| `agentIdRiskLevels` is the canonical way to express "block high-risk agent identities" in policy JSON. | ✅ Verified |
| Nested `agentRisk: { riskLevels: [...] }` shape does NOT exist. | ✅ Verified |
| Wire format is array `"agentIdRiskLevels": ["high"]` (Livingston's claim). | ❌ **REFUTED** — wire format is single string `"agentIdRiskLevels": "high"` (flag-enum), not an array. |
| `agentIdRiskLevels` exists in v1.0. | ❌ **REFUTED** — beta only. |

### Evidence

**Source 1 — `conditionalAccessConditionSet` (beta) schema reference.**
URL: `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessconditionset?view=graph-rest-beta`

Property table, exact quote:
> | `agentIdRiskLevels` | `conditionalAccessAgentIdRiskLevels` | Agent identity risk levels included in the policy. The possible values are: `low`, `medium`, `high`, `unknownFutureValue`. This enumeration is multivalued. |

Note the type: `conditionalAccessAgentIdRiskLevels` is a **named flag-enum type**, NOT a `riskLevel collection`. Compare to peer properties on the same resource — `signInRiskLevels`, `userRiskLevels`, `servicePrincipalRiskLevels` are typed as **`riskLevel collection`** (string-array on the wire), whereas `agentIdRiskLevels` and `insiderRiskLevels` are typed as named flag-enums. The JSON representation block in the same page confirms this — note `"String"` (singular) for the flag-enums vs. `["String"]` (array) for the collections:

```json
{
  "@odata.type": "#microsoft.graph.conditionalAccessConditionSet",
  ...
  "servicePrincipalRiskLevels": ["String"],
  "signInRiskLevels": ["String"],
  "userRiskLevels": ["String"],
  ...
  "insiderRiskLevels": "String",
  "agentIdRiskLevels": "String"
}
```

**Source 2 — `conditionalAccessConditionSet` (v1.0) schema reference.**
URL: `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessconditionset` (v1.0)

The v1.0 property table contains no `agentIdRiskLevels` row. Confirmed beta-only.

**Source 3 — `Create conditionalAccessPolicy` (beta), Example 6 (working POST body).**
URL: `https://learn.microsoft.com/en-us/graph/api/conditionalaccessroot-post-policies?view=graph-rest-beta` (Example 6: "Create a Conditional Access policy to block all agent identities from accessing all resources"). Exact quote of the relevant `conditions` fragment:

```json
{
    "displayName": "Block all agent identities from accessing resources",
    "conditions": {
        "clientApplications": {
            "includeAgentIdServicePrincipals": ["All"],
            "excludeAgentIdServicePrincipals": [],
            "agentIdServicePrincipalFilter": null
        },
        "applications": {
            "includeApplications": ["All"],
            "excludeApplications": []
        }
    },
    ...
}
```

The corresponding **response** body (same example) returns the canonical wire form for the risk levels:

```json
"agentIdRiskLevels": "high"
```

Confirming the wire format is a **single string**, not an array. (Multi-select is expressed as a comma-separated string per Graph's flag-enum convention, e.g., `"medium,high"`.)

**Doc bug spotted (cosmetic, not a schema issue):** Example 6 in the MS Learn response body has a missing comma after `"agentIdRiskLevels": "high"` before `"clientAppTypes": ["all"]`. Pure typo in the docs; the schema is sound.

---

## Q2 — "All agent identities" UI-targeting JSON

**Verdict: REFUTED (Livingston was wrong — the schema IS published in beta).**

### Sub-claims evaluated

| Sub-claim | Verdict |
|---|---|
| `users.includeAgents` / `users.excludeAgents` exist on `conditionalAccessUsers`. | ❌ **REFUTED** (these do NOT exist — Livingston correct on this point). |
| "All agent identities" UI option has **no** published Graph JSON schema. | ❌ **REFUTED** — schema IS published in beta, just not on `users`. It's on `clientApplications`. |
| Agent identity targeting in JSON lives on `conditionalAccessClientApplications` via `includeAgentIdServicePrincipals` / `excludeAgentIdServicePrincipals` / `agentIdServicePrincipalFilter`. | ✅ Verified. |
| The literal `"All"` sentinel is accepted in `includeAgentIdServicePrincipals` to mean "all agent identities". | ✅ Verified by official POST example (see below). |

### Evidence

**Source 1 — `conditionalAccessUsers` (beta) schema reference.**
URL: `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessusers?view=graph-rest-beta`

Full property list: `excludeGroups`, `excludeGuestsOrExternalUsers`, `excludeRoles`, `excludeUsers`, `includeGroups`, `includeGuestsOrExternalUsers`, `includeRoles`, `includeUsers`. **No `includeAgents` / `excludeAgents` properties exist.** Confirms the doc's current `"users": { "includeAgents": "all" }` shape is fabricated.

**Source 2 — `conditionalAccessClientApplications` (beta) schema reference.**
URL: `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessclientapplications?view=graph-rest-beta`

Property table, exact quotes:
> | `agentIdServicePrincipalFilter` | `conditionalAccessFilter` | Filter that defines rules based on custom security attribute tags to include/exclude agent identities in the policy. |
> | `excludeAgentIdServicePrincipals` | `String collection` | Agent identity object IDs excluded from the policy. |
> | `includeAgentIdServicePrincipals` | `String collection` | Agent identity object IDs included in the policy. |

JSON representation block on the same page:

```json
{
    "@odata.type": "#microsoft.graph.conditionalAccessClientApplications",
    "includeServicePrincipals": ["String"],
    "excludeServicePrincipals": ["String"],
    "servicePrincipalFilter": {"@odata.type": "microsoft.graph.conditionalAccessFilter"},
    "includeAgentIdServicePrincipals": ["String"],
    "excludeAgentIdServicePrincipals": ["String"],
    "agentIdServicePrincipalFilter": {"@odata.type": "microsoft.graph.conditionalAccessFilter"}
}
```

**Source 3 — "All" sentinel demonstrated by official POST examples.**
URL: `https://learn.microsoft.com/en-us/graph/api/conditionalaccessroot-post-policies?view=graph-rest-beta`

Examples 5 and 6 both use:

```json
"clientApplications": {
    "includeAgentIdServicePrincipals": ["All"],
    "excludeAgentIdServicePrincipals": [],
    "agentIdServicePrincipalFilter": ...
}
```

The string `"All"` is the documented sentinel (analogous to `"ServicePrincipalsInMyTenant"` used on the peer property `includeServicePrincipals`).

**Caveat:** The `"All"` sentinel is documented **by example, not by an enumeration line in the property-description text**. The schema reference page itself describes the field only as "Agent identity object IDs included in the policy." The two POST examples on the `Create conditionalAccessPolicy` page are the authoritative source for the `"All"` literal. If MS Learn later normalizes the property description to also list the sentinel explicitly, the example remains valid.

**Source 4 — `Conditional Access for agents` overview page.**
URL: `https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id`

Exact quote confirming the design point: agent identities are scoped on the client-applications side, not users:
> "the agent requests an access token using its own agent identity and credentials … the token is issued to the agent identity (not the user). Therefore, Conditional Access policies are scoped to the agent identity rather than the user. You can target agents acting as applications in Conditional Access using the following options: **All agent identities** … **Select agent identities** …"

---

## Q3 — `excludeApplications.attributeFilter`

**Verdict: REFUTED (fabricated; delete and use sibling `applicationFilter`).**

### Sub-claims evaluated

| Sub-claim | Verdict |
|---|---|
| `excludeApplications` is an object that accepts a nested `attributeFilter` sub-object. | ❌ **REFUTED** — `excludeApplications` is a plain `String collection`. |
| There is a valid beta way to filter EXCLUDED applications by attribute. | ✅ Yes, but as a sibling `applicationFilter` (whole-condition filter with `mode: include` / `mode: exclude`), not a per-side property. |

### Evidence

**Source — `conditionalAccessApplications` (beta) schema reference.**
URL: `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessapplications?view=graph-rest-beta`

Property table, exact quotes:
> | `applicationFilter` | `conditionalAccessFilter` | Filter that defines the dynamic-application-syntax rule to include/exclude cloud applications. A filter can use custom security attributes to include/exclude applications. |
> | `excludeApplications` | `String collection` | … The list of client IDs (`appId`) explicitly excluded from the policy. |
> | `includeApplications` | `String collection` | … The list of client IDs (`appId`) the policy applies to … |

JSON representation:

```json
{
  "includeApplications": ["String"],
  "excludeApplications": ["String"],
  "applicationFilter": {"@odata.type": "microsoft.graph.conditionalAccessFilter"},
  "includeUserActions": ["String"],
  ...
}
```

`applicationFilter` is a **single sibling field**, with `mode` of `include` or `exclude` set inside the filter itself (per `conditionalAccessFilter`). The current doc's `"excludeApplications": { "attributeFilter": { ... } }` shape is fabricated and should be deleted.

The MS Learn `Create conditionalAccessPolicy` Example 5 demonstrates the correct pattern of using `applicationFilter` once, with `mode: exclude` set inside it:

```json
"applications": {
    "includeApplications": ["All"],
    "excludeApplications": [],
    "applicationFilter": {
        "mode": "exclude",
        "rule": "CustomSecurityAttribute.AgenticResources_ResourceType -eq \"HR\""
    }
}
```

(Semantics of `mode: exclude` in this MS Learn pattern: tag the in-scope resources, set the policy to BLOCK in `grantControls`, then use `applicationFilter.mode = exclude` so the BLOCK policy applies to everything **except** the tagged-approved set — i.e., the negative-allowlist pattern. This is the pattern documented in the `policy-autonomous-agents` "Use custom security attributes" walkthrough at `https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-autonomous-agents`.)

---

## Q4 — Corrected JSON (author-ready spec)

The disclaimer block can be **removed** from both policy examples once the JSON below is in place. The shapes are now fully verified against the published beta schema and official Microsoft Learn POST examples.

### Required boilerplate near both examples (replace the existing warning admonition)

```
!!! note "Beta Graph API — subject to change"
    The JSON below targets the **`/beta` Microsoft Graph endpoint**: `POST https://graph.microsoft.com/beta/identity/conditionalAccess/policies`. Beta APIs are not supported for production and the schema may change. Validated against MS Learn on 2026-06-04. See [Conditional Access for agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) and [Create conditionalAccessPolicy (beta)](https://learn.microsoft.com/en-us/graph/api/conditionalaccessroot-post-policies?view=graph-rest-beta) for the authoritative reference.
```

### Policy Example 1 — Block high-risk agent identities (replace the current JSON block)

```json
{
  "displayName": "Block high-risk agent identities",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "clientApplications": {
      "includeAgentIdServicePrincipals": ["All"],
      "excludeAgentIdServicePrincipals": [],
      "agentIdServicePrincipalFilter": null
    },
    "applications": {
      "includeApplications": ["All"],
      "excludeApplications": []
    },
    "agentIdRiskLevels": "high"
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["block"]
  }
}
```

Key wire-format points the author MUST preserve:

- `agentIdRiskLevels` is a **single string** (flag-enum), not a JSON array. Multi-select form: `"medium,high"`. Do NOT write `["high"]`.
- Agent identity targeting goes on `clientApplications`, NOT on `users`. Do not include a `users` block in an agent-only policy (or set `users` to its empty defaults).
- `"All"` is the literal sentinel for `includeAgentIdServicePrincipals`.
- Start in `enabledForReportingButNotEnforced` (report-only) per MS Learn's standard pattern; flip to `"enabled"` after impact review.

### Policy Example 2 — Allow only approved agents using custom security attributes (replace the current JSON block)

```json
{
  "displayName": "Allow only HR-approved agents to access HR resources",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "clientApplications": {
      "includeAgentIdServicePrincipals": ["All"],
      "excludeAgentIdServicePrincipals": [],
      "agentIdServicePrincipalFilter": {
        "mode": "exclude",
        "rule": "CustomSecurityAttribute.AgentAttributes_AgentApprovalStatus -eq \"HR_Approved\""
      }
    },
    "applications": {
      "includeApplications": ["All"],
      "excludeApplications": [],
      "applicationFilter": {
        "mode": "exclude",
        "rule": "CustomSecurityAttribute.ResourceAttributes_Department -eq \"HR\""
      }
    }
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["block"]
  }
}
```

Key wire-format points the author MUST preserve:

- The negative-allowlist semantics are intentional and match the MS Learn walkthrough in `policy-autonomous-agents`: the policy **blocks**, the filters use `mode: "exclude"`, and the net effect is "block everything except HR-tagged agents targeting HR-tagged resources." Do not flip `mode` to `include` without re-reading the MS Learn pattern.
- Custom-security-attribute rule syntax: `CustomSecurityAttribute.{AttributeSetName}_{AttributeName} -eq "Value"`. The doc's prior `AgentApprovalStatus` / `Department` shape (no attribute set prefix) was non-canonical — the author should use `AgentAttributes_AgentApprovalStatus` and `ResourceAttributes_Department` (or whatever attribute set names the FSI walkthrough actually creates) to match the MS Learn `policy-autonomous-agents` worked example. If the FSI doc later prescribes different attribute-set names, keep the `{Set}_{Name}` shape.
- `applicationFilter` is a single field on `applications` — not nested inside `excludeApplications`. There is no `excludeApplications.attributeFilter` shape.
- The `agentIdServicePrincipalFilter` and `applicationFilter` are independent — agents filtered on the LHS, resources filtered on the RHS.

### What to do with the prior verifier's "Recommended FSI Policies" callouts

The four bullet recommendations that follow Example 2 in the doc ("Block high-risk agents", "Require approval for sensitive data access", "Enforce geographic restrictions", "Time-based access") do not contain JSON and are not affected by this verdict. Leave them as-is. Note that for "Enforce geographic restrictions" and "Time-based access," there is no specific agent-only JSON beyond standard `locations` / `clientAppTypes` conditions — admins should use the standard `conditionalAccessConditionSet` properties.

---

## Sources cited (all MS Learn, fetched 2026-06-04)

1. `conditionalAccessConditionSet` (beta) — `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessconditionset?view=graph-rest-beta`
2. `conditionalAccessConditionSet` (v1.0) — `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessconditionset`
3. `conditionalAccessUsers` (beta) — `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessusers?view=graph-rest-beta`
4. `conditionalAccessClientApplications` (beta) — `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessclientapplications?view=graph-rest-beta`
5. `conditionalAccessApplications` (beta) — `https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessapplications?view=graph-rest-beta`
6. `Create conditionalAccessPolicy` (beta) — `https://learn.microsoft.com/en-us/graph/api/conditionalaccessroot-post-policies?view=graph-rest-beta` (Examples 5 & 6 are the smoking guns)
7. `Conditional Access for agents` — `https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id`
8. `Recommended policies for autonomous agents` — `https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-autonomous-agents`

---

## Adversarial pushback I considered before approving the corrected JSON

- **"Maybe the `String` in the JSON-rep block is a docs typo and `agentIdRiskLevels` really is an array."** Refuted by Example 6's actual response body returning `"agentIdRiskLevels": "high"` (single string). The flag-enum interpretation is consistent with sibling `insiderRiskLevels` (same `"String"` form in the JSON rep).
- **"Maybe `[\"All\"]` for `includeAgentIdServicePrincipals` is implied but not actually accepted by the API."** Both Example 5 and Example 6 POST bodies on `Create conditionalAccessPolicy` use exactly this shape with HTTP `201 Created` responses shown immediately below them. Authoritative.
- **"Maybe `agentIdServicePrincipalFilter` requires a different rule syntax than `applicationFilter`."** Both are typed as `conditionalAccessFilter` (same resource type), so `{ "mode": ..., "rule": ... }` applies to both. Example 5 demonstrates both filters in the same POST body.
- **"Maybe the corrected payload should NOT use `mode: exclude`."** Cross-checked against the `policy-autonomous-agents` walkthrough; the negative-allowlist pattern is the MS-recommended approach for "allow only approved agents" when paired with `builtInControls: ["block"]`. The semantics are non-obvious but documented.

---

## What the author should do next (recommended sequence)

1. Replace the two JSON blocks in `docs/framework/agent-identity-architecture.md` (Policy Examples 1 & 2) with the corrected JSON above.
2. Replace the existing `!!! warning "Illustrative example — not Graph-API-ready"` admonitions with the lighter `!!! note "Beta Graph API — subject to change"` block shown above.
3. Run `mkdocs build --strict` and `python scripts/verify_language_rules.py`.
4. Close issue #360 referencing this verdict file.

**Verifier sign-off (Saul):** All four acceptance questions resolved with verified/refuted verdicts backed by quoted MS Learn schema text and official POST examples. No "cannot-confirm" remaining. Disclaimer can come off the doc once the JSON is replaced. Beta caveat must remain.
