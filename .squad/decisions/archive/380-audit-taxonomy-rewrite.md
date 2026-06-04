# Decision Record: #380 Purview UAL Audit-Event Taxonomy Rewrite

**Status:** CLOSED (Resolved via PR #395, squash-merged `d77a70a05`, 2026-06-04)  
**Issue:** #380  
**PR:** #395  
**Owner:** Linus (author), judep (maintainer approval)  
**Verified by:** Saul (owl-mode QA, 2026-06-04)  

---

## Finding

Reference document **`docs/reference/agent-audit-event-taxonomy.md`** contained ~28 fabricated audit operation/record-type names that returned **zero-row KQL queries** against Purview Unified Audit Log.

**Regulatory risk:** FINRA 3110 (surveillance/detection of market manipulation involving AI) and SOX 404 (internal control auditing for compliance with Exchange Act) require audit trails. Fabricated taxonomy entries create false confidence that audit detection is possible when it is not.

**Interim mitigation:** PR #379 deployed warning banner (2026-06-03).

---

## Verified Facts (Saul, 2026-06-04)

**Primary sources:** 
- Microsoft Learn: https://learn.microsoft.com/purview/audit-log-activities
- Test KQL queries run against production Purview UAL

### Authoritative Purview UAL Agent-Related Operations

| Operation Source | Operations | Count | Notes |
|---|---|---|---|
| **Purview Unified Audit Log** | AIExecuteTool, AIInvokeAgent, AIInferenceCall | 3 | Agent 365 operations only |
| **Purview Unified Audit Log** | PowerPlatformAdministratorActivity (Copilot Studio authoring ops) | 21 | Sub-activities within this operation |
| **Purview Unified Audit Log** | CopilotInteraction (agent usage logging) | 1 | Agent usage telemetry; **not compliance audit suitable** (end-user generated) |
| **Purview Unified Audit Log** | M365 Copilot admin operations | 5–7 | Settings, policy, governance operations |
| **Entra ID Audit Log** | (no dedicated agent operations) | — | Filter existing app/service-principal ops by agentType attribute |

**Non-published/Fabricated (removed):** ~28 entries, including:
- AIAuditTrail, AIComplianceLog, AIDataClassification (no such published ops)
- CopilotStudioControlFlow, CopilotStudioIntegration (not actual operation names)
- EntraAgentAuditEvent (no Entra-native agent ops exist; filter app audit instead)

---

## Disposition

**Accepted:** Option 1 (Maintainer-selected; judep)

**Rewrite strategy:** 
- **"Published & Searchable" section:** 49 real, learn.microsoft.com-cited events across:
  - 42 Purview UAL operations (Agent 365, M365 Copilot admin, Copilot Studio authoring, agent usage)
  - 7 Entra agentType-filtered operations (app/service-principal audit)
- **"Conceptual Governance Categories" section:** 15 non-published categories (each mapped to nearest real adjacent evidence)

---

## Remediation Process

### Researcher Pass (opus-4.6, read-only)
- Compiled Microsoft Learn-cited catalog of published Purview UAL operations
- Cross-referenced with Graph Audit Log schema
- Identified ~28 fabricated entries

### Linus Pass 1 (opus-4.6, authoring)
- Rewrote file: "Published & Searchable" + "Conceptual Governance Categories" sections
- Cited learn.microsoft.com/purview/audit-log-activities as source of truth
- 49 real operations (42 Purview UAL + 7 Entra filtered)
- 15 governance categories mapped to supporting evidence

### Saul Pass (opus-4.7-high, owl-mode verification)
- **Verdict:** PARTIALLY VERIFIED
- **Critical findings:** 0 fabrications leaked; all 49 published operations verified; correct citation
- **Required fixes (D1–D4):**
  - D1: Clarify that Entra lacks native agent ops; reframe as filter-based approach
  - D2: Add caveat that CopilotInteraction is end-user-generated (not compliance-audit suitable)
  - D3: Tighten governance category mappings to adjacent real operations (not aspirational)
  - D4: Add note on Purview UAL schema versioning (audit-log-activities page as single source of truth)

### Linus Pass 2 (remediation)
- Applied D1–D4 fixes to rewritten draft
- Regenerated sections with corrected framing

### Merge & Validation
- **PR #395 squash-merged:** `d77a70a05` (2026-06-04)
- **File diff:** 277+/291- in 1 file (full rewrite with citation overhead)
- **Validation:** `mkdocs build --strict` ✅, `verify_controls.py` ✅, `verify_language_rules.py` ✅

---

## PR #395 Details

| Field | Value |
|-------|-------|
| **Title** | "chore(reference): rewrite purview-ual audit-event taxonomy from authorized source" |
| **Merge SHA** | `d77a70a05` |
| **Squash merged** | 2026-06-04 |
| **Files changed** | 1 |
| **Lines added** | 277 |
| **Lines removed** | 291 |
| **CI gates** | All 11 required checks green |

---

## Durable Learning: Purview UAL Agent Operations

**Core rule:** Purview Unified Audit Log publishes **only 3 Agent 365 operations** (AIExecuteTool, AIInvokeAgent, AIInferenceCall). For admin governance, add:
- 21 PowerPlatformAdministratorActivity sub-activities (Copilot Studio authoring)
- 5–7 M365 Copilot admin operations
- 1 CopilotInteraction (end-user usage, not compliance suitable)
- Entra: filter existing app/service-principal audit by agentType (no native agent ops)

**Do NOT invent operation names.** Cite https://learn.microsoft.com/purview/audit-log-activities as single source of truth. Verify at edit time — schema may evolve.

**Governance caveat:** CopilotInteraction is user-generated telemetry, not compliance audit trail. FINRA 3110 / SOX 404 compliance requires admin-controlled operations (AIExecuteTool, PowerPlatformAdministratorActivity, M365 Copilot admin).

---

## Related Issues

- **#364** (CLOSED): FINRA RN 25-07 RFC reframing
- **#381** (OPEN): NIST mapping + coverage rollup
