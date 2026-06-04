# Decision Record: #364 FINRA RN 25-07 RFC Reframing

**Status:** CLOSED (Resolved via PR #393, squash-merged `4ba5f3801`, 2026-06-04)  
**Issue:** #364  
**PR:** #393  
**Owner:** Danny (author/opener), judep (maintainer approval)  
**Verified by:** Saul (SME reverification, 2026-06-04)  

---

## Finding

Framework documentation **mischaracterized FINRA RN 25-07** in two ways:

1. **Binding assertion error (Class A):** `.github/copilot-instructions.md` and `AGENTS.md` listed RN 25-07 as a binding "target regulation" when it is actually a Request for Comment (RFC) with no adopted status.

2. **Not AI governance overstatement (Class B):** 13 control files contained assertions or hedged language suggesting RN 25-07 is "not AI governance" or tangentially related to AI, when it actually **is in scope for AI** via:
   - **Section E.3:** Recordkeeping obligations for AI-generated communications under Exchange Act Rule 17a-4(b)(4)
   - **Section G:** AI-driven fraud detection and mitigation requirements

---

## Verified Facts (Saul, 2026-06-04)

**Primary source:** FINRA Notice to Members 25-07 (workplace modernization RFC)

- **Type:** Request for Comment (RFC); not adopted as binding rule
- **Comment window:** Closed July 2025
- **AI scope:** YES
  - E.3 explicitly addresses recordkeeping for AI-generated communications
  - G covers AI-driven fraud detection
- **Status:** Monitored proposal (can evolve; currently guidance-only, not binding)

---

## Disposition

**Accepted:** Option 1 (maintainer-selected, judep)

**Reframe as:** Monitored RFC touching AI recordkeeping; downgrade from "target regulation" to "monitored proposal" category

---

## Remediation (PR #393)

**Squash merged:** `4ba5f3801` (2026-06-04)  
**Files changed:** 15  
**Total enumeration:** ~85 RN 25-07 occurrences across repo

### Classification Breakdown

| Class | Count | Action |
|-------|-------|--------|
| **(a) Binding assertion** | 2 | Fixed (moved to "monitored proposals") |
| **(b) Contradiction/overstatement** | 13 | Fixed (rewritten risk statements, reframed AI scope) |
| **(c) Neutral citations** | ~70 | Left as-is (already correct RFC framing or structural/programmatic) |

### Files Modified

**Repo-wide metadata (2 files):**
- `.github/copilot-instructions.md` — moved RN 25-07 to "monitored proposals"
- `AGENTS.md` — moved RN 25-07 to "monitored proposals"

**Framework & reference (4 files):**
- `docs/framework/regulatory-framework.md` — rewritten risk callout (E.3 + G scope)
- `docs/reference/cco-quick-reference.md` — bibliography + warning rewrite
- `docs/reference/regulatory-mappings.md` — warning rewrite
- `docs/reference/microsoft-cape-crosswalk.md` — FAQ rewrite

**Controls (8 files):**
- `docs/controls/pillar-1-security/1.7-...md` — aligned parenthetical
- `docs/controls/pillar-2-management/2.12-...md` — link description update
- `docs/controls/pillar-4-sharepoint/4.1–4.7.md` — replaced overstatements (7 controls)

**Not modified (~70 neutral citations + ~25 playbooks):** Already correct RFC framing or structural/programmatic.

---

## Learning Captured

**Durable principle:** FINRA RN 25-07 is an RFC (not an adopted rule). Do not re-flag:
- Neutral citations that simply reference RN 25-07 as a proposal
- Contextual mentions in playbooks or procedural guides
- Structural/programmatic tags in manifest or assessment code

**Do flag:**
- Assertions that RN 25-07 is binding/adopted
- Overstatements that RN 25-07 is unrelated to AI (it covers AI recordkeeping + fraud detection)

---

## Validation

- `mkdocs build --strict` ✅
- `python scripts/verify_controls.py` ✅
- `python scripts/verify_language_rules.py` ✅

---

## Related Issues

- **#380** (OPEN): SME taxonomy rewrite + interim banner PR #379
- **#381** (OPEN): NIST mapping + coverage rollup; labels fixed PR #392
