# Decision Record: #381 — NIST AI RMF Crosswalk Mapping + Coverage Rollup

**Issue:** #381  
**Decision Date:** 2026-06-04  
**Status:** ✅ **CLOSED** (PR #397 merged)  
**Owner:** judep (maintainer)  

---

## Finding Summary

**Ref:** REFB-001/002

The NIST AI RMF crosswalk document (`docs/reference/nist-ai-rmf-crosswalk.md`) had misaligned CONTROL mappings despite earlier label normalization (PR #392). Root cause: MEASURE 2.6, 2.11, and 2.2 labels were fixed but their entangled FSI-AgentGov control mappings were left stale and inconsistent with current framework controls.

**Specific issues:**
- MEASURE 2.6 (Safety) → incorrectly mapped
- MEASURE 2.11 (Fairness & bias) → incorrectly mapped
- MEASURE 2.2 label corrected to match NIST AI 100-1 §5.3 but mapping stale
- Control 2.7 coverage determination unclear (GOVERN/MAP coverage not documented)
- TODO(NIST-SME) markers left in-place for future reconciliation

---

## Disposition

**Option Chosen:** Option 1 (apply SME-derived mapping)  
**Approved By:** judep (maintainer, 2026-06-04)

---

## Resolution Process

### Stage 1: Initial Author Pass
- **Agent:** Linus (Opus-4.6)
- **Task:** Generate NIST AI RMF mappings reconciled against NIST AI 100-1 §5.3 per framework controls
- **Output:** Proposed mapping corrections with control cross-references

### Stage 2: Verification (Owl-Mode)
- **Agent:** Saul (Opus-4.7-high, owl-mode enabled)
- **Task:** Verify Linus mappings against authoritative NIST AI 100-1 §5.3
- **Verification Method:** Cross-referenced subcategory numbering against https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
- **Findings:**
  - ✅ MEASURE 2.6 mapping validated
  - ✅ MEASURE 2.11 mapping validated
  - ✅ MEASURE 2.2 label + mapping validated
  - ✅ Control 2.7 coverage confirmed under GOVERN 6.1/6.2 + MAP 4.1/4.2 (no orphan)
  - ⚠️ **Blocker Found:** Control 2.5 cross-reference incomplete (discovered during review)
  - ⚠️ **Systemic Finding:** ~7 of 11 MEASURE 2.x rows (2.1, 2.3, 2.4, 2.5, 2.7, 2.9, 2.10) carry labels that don't match NIST AI 100-1 §5.3 subcategory text (out of scope for this PR; tracked as #398)

### Stage 3: Remediation
- **Agent:** Linus (Opus-4.6)
- **Task:** Fix blocker (Control 2.5 cross-reference) and apply Saul-verified mappings
- **Result:** All Saul findings addressed; coverage rollup recalculated

### Stage 4: Merge
- **PR:** #397 (squash-merged `edba6f09c` → main, 2026-06-04)

---

## Final Mappings & Fixes Applied

| MEASURE | Label | FSI Control Mapping | Status |
|---------|-------|-------------------|--------|
| 2.6 | Safety | [1.8, 2.20] | ✅ Corrected |
| 2.11 | Fairness & bias | [2.11 Bias Testing & Fairness] | ✅ Corrected |
| 2.2 | (label corrected to NIST text) | [2.5, 2.14] | ✅ Corrected |
| 2.7 | (coverage determination) | Covered under GOVERN 6.1/6.2 + MAP 4.1/4.2 | ✅ Verified (no orphan) |

---

## Coverage Rollup Impact

**Before:** 67 addressed / 63 full / 2 partial / 2 N/A (93% / 94% / 97%)  
**After:** 67 addressed / 63 full / 2 partial / 2 N/A (93% / 94% / 97%)  
**Delta:** UNCHANGED — corrections were mapping-only; no new controls addressed

---

## Cleanup

- ✅ TODO(NIST-SME) markers removed from PR #397
- ✅ Control 2.5 cross-reference completed

---

## Related & Follow-Up

**New Issue Opened:** #398 "NIST AI RMF 1.0 label drift in MEASURE 2.x"  
**Status:** OPEN (SME-gated, out of scope for #381)  
**Scope:** Systemic MEASURE 2.x label drift (see Saul's owl-mode findings above)

---

## Durable Learning

**Principle:** NIST AI RMF crosswalk (`docs/reference/nist-ai-rmf-crosswalk.md`) historically used in-house summary labels that DON'T match NIST AI 100-1 §5.3 subcategory numbering.

**Procedure:**
- When touching any MEASURE/MAP/GOVERN row, verify the label against the official NIST PDF (https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)
- Re-decide the entangled control mapping after label verification
- Recompute the bottom-of-file coverage rollup after any change

**Source:** Verified by Saul (owl-mode, 2026-06-04) against NIST AI 100-1 §5.3

---

*Archived: 2026-06-04*
