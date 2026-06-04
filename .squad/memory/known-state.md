# Squad Memory: Known State Tracker

**Last updated:** 2026-06-04  
**Scope:** Active and recently closed issues in FSI-AgentGov review squad

---

## Issue Tracker (3 Total)

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

### #380 — SME Taxonomy Rewrite (Interim Mitigation)

**Status:** 🟡 **OPEN**  
**Last action:** PR #379 (interim banner deployed)  
**Scope:** Rewrite SME-facing taxonomy in control role descriptions and governance operating model to clarify role boundaries.  
**Notes:** #379 provides interim visual warning until full rewrite; no decision record yet (pending SME review + design phase).

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

## Inbox Archive Status

**Moved to archive during #364 closeout:**
- `danny-364-reconciliation.md` → Sourced for decision record

**Still in inbox (other issues):**
- `saul-classB-reverify.md` (contains #380 + #381 sections; keep open)
- `linus-classB-remediation.md`
- `linus-learn-monitor-cleanup.md`
- `rusty-dependabot-cleanup.md`
