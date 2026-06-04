# Squad Memory: Known State Tracker

**Last updated:** 2026-06-04  
**Scope:** Active and recently closed issues in FSI-AgentGov review squad

---

## Issue Tracker (3 Total, 2 Closed / 1 Open)

### #364 — FINRA RN 25-07 Mischaracterization

**Status:** 🟢 **CLOSED**  
**PR:** #393 (squash-merged `4ba5f3801`, 2026-06-04)  
**Finding:** Framework mischaracterized RN 25-07 as binding target regulation when it is an RFC; also overstated it as not AI-related (actually covers AI recordkeeping + fraud).  
**Disposition:** Option 1 — reframe as monitored RFC; downgrade from target regulation.  
**Remediation:** 15 files, 2 Class A fixes + 13 Class B fixes, ~70 Class C citations left as-is.  
**Owner:** Danny (author/opener), judep (approver)  
**Verified by:** Saul (SME, 2026-06-04)  
**Decision record:** `.squad/decisions/archive/364-finra-25-07-rfc-reframing.md`

---

### #380 — Purview UAL Audit-Event Taxonomy Rewrite

**Status:** 🟢 **CLOSED**  
**PR:** #395 (squash-merged `d77a70a05`, 2026-06-04)  
**Finding:** `docs/reference/agent-audit-event-taxonomy.md` contained ~28 fabricated audit Operation/RecordType names returning zero-row KQL queries (FINRA 3110 / SOX 404 monitoring risk).  
**Disposition:** Option 1 (full authoritative rewrite) — Chosen by maintainer judep.  
**Process:** Researcher (opus-4.6, read-only) compiled Learn-cited catalog → Linus (opus-4.6) rewrote file into "Published & Searchable" (49 real cited events: 42 Purview UAL ops + 7 Entra agentType-filtered ops) vs "Conceptual Governance Categories" (15 non-published categories, each mapped to real adjacent evidence) → Saul (opus-4.7-high, owl-mode) verified: PARTIALLY VERIFIED, 0 fabrications leaked, required fixes D1-D4 → Linus applied D1-D4 → merged.  
**Remediation:** PR #395 (`d77a70a05`). Net diff 277+/291- in 1 file.  
**Decision record:** `.squad/decisions/archive/380-audit-taxonomy-rewrite.md`

---

### #381 — NIST Mapping + Coverage Rollup

**Status:** 🟡 **OPEN**  
**Last action:** PR #392 (labels fixed for consistency)  
**Scope:** Complete NIST SP 800-53 Rev 5 AI control mappings; regenerate honest assessment-coverage matrix.  
**Notes:** Labels normalization completed; mapping and coverage work pending detailed design.

---

## Durable Learnings

### FINRA RN 25-07 RFC Governance

**Principle:** RN 25-07 is a monitored Request for Comment (not adopted). Classification rules:

- **Do NOT re-flag:** Neutral citations, contextual mentions, structural tags
- **DO flag:** Binding assertions, overstatements that 25-07 is unrelated to AI
- **AI scope in RN 25-07:** Section E.3 (AI-generated communications recordkeeping), Section G (AI fraud detection)

**Source:** Decision record `364-finra-25-07-rfc-reframing.md` (verified by Saul, 2026-06-04)

---

### Purview UAL Agent Operations (Authoritative Catalog)

**Principle:** Purview Unified Audit Log publishes only 3 Agent 365 operations; fabricated operation names do not appear in KQL. Compliance auditing requires admin-controlled ops, not end-user telemetry.

**Authoritative operations:**
- **Agent 365:** AIExecuteTool, AIInvokeAgent, AIInferenceCall (3 operations)
- **Copilot Studio authoring:** 21 PowerPlatformAdministratorActivity sub-activities
- **M365 Copilot admin governance:** 5–7 operations (admin settings/policy)
- **Agent usage:** CopilotInteraction (end-user generated; NOT compliance audit suitable)
- **Entra:** NO native agent ops; filter existing app/service-principal audit by agentType

**Do NOT invent operation names.** Source: https://learn.microsoft.com/purview/audit-log-activities

**Governance caveat:** FINRA 3110 / SOX 404 compliance requires **admin-controlled operations** (AIExecuteTool, PowerPlatformAdministratorActivity, M365 Copilot admin), not user-generated CopilotInteraction logs.

**Source:** Decision record `380-audit-taxonomy-rewrite.md` (verified by Saul, 2026-06-04)

## Inbox Archive Status

**Moved to archive during #364 closeout:**
- `danny-364-reconciliation.md` → Sourced for decision record

**Still in inbox (other issues):**
- `saul-classB-reverify.md` (contains #380 + #381 sections; keep open)
- `linus-classB-remediation.md`
- `linus-learn-monitor-cleanup.md`
- `rusty-dependabot-cleanup.md`
