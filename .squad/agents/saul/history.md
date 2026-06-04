# Saul — verifier history

## 2026-06-04 — Issue #360 Graph CA re-verification

Re-verified the Microsoft Graph beta Conditional Access JSON schema against MS Learn (live) for `docs/framework/agent-identity-architecture.md` Policy Examples 1 & 2. Verdict written to `.squad/decisions/inbox/saul-360-graph-reverify.md`.

Net outcome: prior verifier (Livingston) was directionally right that the existing JSON is fabricated, but **one of Livingston's specific replacement claims was itself incorrect** and the conclusion "no Graph schema exists for All agent identities" is now refuted by the published beta schema. Corrected, author-ready JSON delivered for both examples — disclaimer can come off.

## Learnings

1. **`agentIdRiskLevels` is a single-string flag-enum, not a JSON array.** Wire format is `"agentIdRiskLevels": "high"` (or `"medium,high"` for multi-select). The MS Learn JSON-representation block at `conditionalaccessconditionset?view=graph-rest-beta` shows `"agentIdRiskLevels": "String"` (singular), and the official POST example response in `conditionalaccessroot-post-policies?view=graph-rest-beta` returns `"agentIdRiskLevels": "high"`. The pattern matches the sibling `insiderRiskLevels` (also a named flag-enum, also serialized as a single string), and contrasts with `signInRiskLevels` / `userRiskLevels` / `servicePrincipalRiskLevels` which are typed as `riskLevel collection` and serialize as `["String"]` arrays. **For future Graph reviews: when the property type is a named enum (e.g., `conditionalAccessFooLevels`) it is almost always a single-string flag-enum; when typed as `xxxLevel collection` it is a JSON array. Don't trust property descriptions saying "multivalued" — check the JSON-rep block AND a working POST example.**

2. **Agent identity policy targeting lives on `clientApplications`, never on `users`.** The `conditionalAccessUsers` resource only has user/group/role properties — there are no `includeAgents`/`excludeAgents` fields and never were. Agent identities are targeted via `conditionalAccessClientApplications.includeAgentIdServicePrincipals` / `excludeAgentIdServicePrincipals` / `agentIdServicePrincipalFilter`. The `"All"` literal sentinel is supported in `includeAgentIdServicePrincipals` (demonstrated by official POST examples 5 and 6 in `conditionalaccessroot-post-policies?view=graph-rest-beta`) but is NOT enumerated in the property-description text of the schema reference. **For future Graph reviews: when a UI option appears in Entra portal but isn't listed in a property's text description, check the official POST examples on the Create-{resource} page — Microsoft frequently documents sentinel values by example only.**

3. **Filter-by-attribute is a sibling field with `mode` inside the filter, not a per-side sub-object.** `excludeApplications.attributeFilter` is fabricated; the correct shape is `applicationFilter` as a single sibling of `includeApplications`/`excludeApplications`, with the include-vs-exclude semantics set via `mode` inside the `conditionalAccessFilter` object itself. Same pattern applies to `agentIdServicePrincipalFilter` (sibling of include/exclude agent ID lists) and `servicePrincipalFilter` (sibling of include/exclude SP lists). The MS-documented "allow only approved" pattern uses `builtInControls: ["block"]` + `mode: "exclude"` (negative allowlist) — counterintuitive but canonical, documented in `policy-autonomous-agents`. **For future Graph reviews: when a filter looks like it belongs nested on the include or exclude side, check whether it's actually a peer field on the parent — and read the `mode` field carefully because the negative-allowlist pattern is the MS-recommended idiom for several agent scenarios.**

4. **MS Learn is the authoritative source AND it has copy/paste typos.** Example 6 response body on `conditionalaccessroot-post-policies?view=graph-rest-beta` has a missing comma after `"agentIdRiskLevels": "high"` before `"clientAppTypes": ["all"]`. Cosmetic, doesn't change the schema, but worth noting: blindly copy-pasting MS Learn JSON into production can produce parse errors. Always validate as JSON before shipping. **For future Graph reviews: always JSON-parse-validate any payload before recommending it to FSI admins.**

5. **`/beta` vs `/v1.0` matters and must always be called out.** `agentIdRiskLevels` does not exist in v1.0. `conditionalAccessUsers` in v1.0 likewise lacks agent fields. Any FSI doc using these schemas must explicitly note `POST https://graph.microsoft.com/beta/identity/conditionalAccess/policies` and stamp "beta — subject to change" with a verification date. The lighter `!!! note "Beta Graph API — subject to change"` admonition is appropriate; the heavier "not Graph-API-ready" warning is misleading once the JSON is verified.

6. **My verifier role does NOT include applying the fix.** Per charter: produce verdict + evidence, hand off to a separate author. Resisted the urge to also edit the doc, even though I had ready-to-paste JSON. Future Saul: do not be helpful in the wrong direction — that's how rubber-stamping starts.

---

## 2026-06-04 — Class-A re-verification batch (#370, #372, #373, #365)

**Charter applied:** read-only verifier; no doc edits, no PRs. Output written to .squad/decisions/inbox/saul-classA-reverify.md.

**Verdicts:**
- **#370 Sentinel MCP "GA November 2025"** → REFUTED. Sep 2025 What's New explicitly labels "(Preview)"; Nov 2025 section has zero MCP mention; overview page never says GA; Azure Updates feed has zero matching items.
- **#372 PPAC Actions under Security node** → REFUTED. `power-platform-advisor` doc shows top-level "Select Actions" navigation; Security page is a *peer* that surfaces contextual recommendations.
- **#373 Computer Use "GA October 2025 (no longer Frontier-gated)"** → REFUTED. Live MS Support article last updated Feb 2026 still titled "(Frontier)" and states verbatim: "This feature is currently available through the Frontier program." Frontier ≡ preview by Microsoft's own definition. M365 Roadmap 511796 forecast GA Nov 2025 but status is still "In development" — roadmap is forward-looking, not authoritative for live status.
- **#365 Customer Key Standard+Premium SKU** → VERIFIED. `customer-key-set-up` page verbatim supports both SKUs and strongly recommends Premium for production; Standard for test/validation only.

**Key learnings to bank:**

1. **M365 Roadmap GA dates are forward-looking, not authoritative for live status.** Roadmap 511796 (Computer Use) forecasts GA Nov 2025 but status is "In development" and the live MS Support article (Feb 2026) still labels Frontier. Never cite a roadmap date as proof of GA — fetch the live MS Learn / Support doc.

2. **"GA … with Frontier access" is internally contradictory.** Third-party blogs (handsontek, supersimple365) make this claim for Computer Use. Frontier is Microsoft's pre-GA preview channel by explicit definition (`get-started-frontier`). Treat any blog assertion of GA-via-Frontier as evidence the blogger conflated "released to Frontier tenants" with "GA". Authoritative trumps blog.

3. **"What's new" page negative-evidence pattern is reliable for Sentinel.** Programmatic monthly-section scan confirmed Nov 2025 section has zero MCP mentions. A six-month-rolling "What's new" page that does not announce GA for a feature it previously called Preview is strong refutation of an unverified GA claim.

4. **PPAC navigation: top-level vs nested.** The Actions/Advisor doc uses unambiguous breadcrumb language ("Select Actions" from the admin center home). The "Contextual recommendations are also available in: Security page, Copilot page, Monitor page" bullet is the trap — it confirms surfaces consume Actions data but does not nest Actions under them.

5. **Customer Key SKU dispute (Linus vs Livingston) resolved.** MS Learn is unambiguous: both SKUs supported; Premium strongly recommended for production; Standard only for testing/validation. Livingston's hedged draft wording is the correct interpretation; Linus's "Premium required" overstates and would substitute one defect for another.
