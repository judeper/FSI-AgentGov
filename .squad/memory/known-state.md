# Squad Memory: Known State Tracker

**Last updated:** 2026-06-04  
**Scope:** Active and recently closed issues in FSI-AgentGov review squad

---

## Issue Tracker (4 Total, 3 Closed / 1 Open)

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

**Status:** 🟢 **CLOSED**  
**PR:** #397 (squash-merged `edba6f09c`, 2026-06-04)  
**Finding:** NIST AI RMF crosswalk (PR #392) label fixes left control mappings misaligned; SME-gated reconciliation required.  
**Disposition:** Option 1 — apply SME-derived mapping (Linus author → Saul verification → Linus remediation).  
**Remediation:** MEASURE 2.6/2.11/2.2 mappings corrected; Control 2.7 orphan status verified; coverage rollup recalculated (UNCHANGED: 93%/94%/97%).  
**Owner:** Linus (author), Saul (verifier, owl-mode), judep (approver)  
**Decision record:** `.squad/decisions/archive/381-nist-crosswalk-mapping.md`

---

### #398 — NIST AI RMF 1.0 Label Drift in MEASURE 2.x

**Status:** 🔴 **OPEN**  
**Opened:** 2026-06-04 (uncovered during #381 verification)  
**Finding:** Saul (owl-mode) identified ~7 of 11 MEASURE 2.x rows (2.1, 2.3, 2.4, 2.5, 2.7, 2.9, 2.10) carry labels that don't match NIST AI 100-1 §5.3 subcategory text; also an "Effective Coverage" wording quirk (line ~230).  
**Scope:** Systemic label drift (out of scope for #381).  
**Status:** SME-gated, tracked for future NIST-SME pass.  
**Decision record:** `.squad/decisions/archive/381-nist-crosswalk-mapping.md` (documented as follow-up finding)

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

---

### NIST AI RMF Crosswalk Historical Label Drift

**Principle:** `docs/reference/nist-ai-rmf-crosswalk.md` historically used in-house summary labels that DON'T match NIST AI 100-1 §5.3 subcategory numbering.

**Procedure:**
- When touching any MEASURE/MAP/GOVERN row, verify the label against the official NIST PDF (https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)
- Re-decide the entangled control mapping after label verification
- Recompute the bottom-of-file coverage rollup after any change

**Source:** Decision record `381-nist-crosswalk-mapping.md` (verified by Saul, owl-mode, 2026-06-04); systemic findings tracked in #398

---

## Escalation Backlog Status

**CLEARED:** #364, #380, #381 all closed (PRs #393, #395, #397 merged, 2026-06-04)

**New tracked item:** #398 OPEN (SME-gated, documented in decision records)

---

## Inbox Archive Status

**Moved to archive during closeout cycle:**
- `danny-364-reconciliation.md` → Sourced for #364 decision record
- `saul-classB-reverify.md` → Sourced for #380/#381/#398 decision records + durable learnings

**Still in inbox (completed items moved to decision records):**
- `linus-classB-remediation.md` (completed; source for #381/#380)
- `linus-learn-monitor-cleanup.md`
- `rusty-dependabot-cleanup.md`
