# Linus — Class-A Remediation Outcome

**Author:** Linus (documentation author)
**Date:** 2026-06-04
**Directive:** judep — "merge and close out all pending ones"
**Source verification:** Saul (read-only QA), `saul-classA-reverify.md`, 2026-06-04

---

## Summary

All four verified corrections applied in a single branch and PR. Validations green. PR opened as ready-for-review; Danny merges separately.

---

## Issue Dispositions

### #370 — 3.9 Sentinel MCP Server (REFUTED → FIXED)

- **Was:** `(GA November 2025)`
- **Now:** `(Preview as of September 2025 — verify current status against [Microsoft Sentinel — What's new](...) at edit time)`
- **MS Learn citation:** https://learn.microsoft.com/en-us/azure/sentinel/whats-new (Sep 2025 section labels MCP Server as Preview; November 2025 section: zero MCP entries)

### #372 — 3.7 PPAC Actions page placement (REFUTED → FIXED)

- **Was:** "The **Security** node in PPAC navigation contains four pages, plus a related **Actions** page…"
- **Now:** "PPAC navigation includes a top-level **Actions** page… alongside the **Security** node's four pages. The Security pages surface contextual recommendations drawn from Actions; Actions is a peer top-level area, not a child of Security:"
- **MS Learn citation:** https://learn.microsoft.com/power-platform/admin/power-platform-advisor — Actions is top-level ("Select Actions"); Security is a peer that surfaces contextual recommendations from Actions
- **Scan result:** No other line in 3.7 asserts Actions lives under Security. Lines 83 and 222 correctly treat Actions and Security as peers.

### #373 — 3.13 Computer Use / Frontier status (REFUTED → FIXED)

- **Was:** "Computer Use has been generally available since October 2025 for tenants with Microsoft 365 Copilot licensing (no longer Frontier-gated)."
- **Now:** "Researcher with Computer Use is available via the Microsoft Frontier program (preview) as of February 2026 for tenants with Microsoft 365 Copilot licensing — verify current status against the [Microsoft Frontier program page](...) at edit time."
- **MS Learn citation:** https://support.microsoft.com/topic/get-started-using-researcher-with-computer-use-in-microsoft-365-copilot-frontier-1f274537-6648-46e8-8264-052a49b92af4 (last updated February 2026 — explicitly states "This feature is currently available through the Frontier program")
- **Footer note:** 3.13 footer was already `June 2026` — no change required.

### #365 — 1.15 Customer Key SKU guidance (VERIFIED → CORRECTED TO MATCH MS LEARN VERBATIM)

- **Line ~51 was:** `(Standard SKU minimum; Premium HSM-backed recommended; Managed HSM available for the highest assurance)`
- **Line ~51 now:** `(Customer Key supports either the Standard or Premium SKU; Microsoft strongly recommends the Premium HSM-backed SKU for production data and Standard only for testing and validation; Managed HSM available for the highest assurance)`
- **Line ~65 was:** `Premium SKU with HSM-backed RSA keys for Zone 3.`
- **Line ~65 now:** `Premium SKU with HSM-backed RSA keys recommended for all production data (Standard SKU only for testing and validation; Premium required for Zone 3).`
- **Zone 3 table row (~line 88):** Unchanged — already correct ("Premium Key Vault SKU … required").
- **MS Learn citation:** https://learn.microsoft.com/en-us/purview/customer-key-set-up — "Customer Key supports key vaults with either of the two SKUs, but Microsoft strongly recommends using the Premium SKU." / "Use Standard SKU key vaults and keys only for testing and validation."

---

## Validation Results

| Check | Result |
|-------|--------|
| `mkdocs build --strict` | ✅ Zero errors, zero warnings (71.97s) |
| `python scripts/verify_controls.py` | ✅ All 78 controls valid |
| `python scripts/verify_language_rules.py` | ✅ No prohibited language found |

---

## PR Details

- **Branch:** `fix/escalation-reverify-batch-365-370-372-373`
- **Commit:** `1b8324657`
- **PR:** [#390](https://github.com/judeper/FSI-AgentGov/pull/390) — ready-for-review, not draft
- **Closes:** #365, #370, #372, #373
- **EMU account:** Restored to `judep_microsoft` ✅

---

*Linus · 2026-06-04 · Documentation author — read/write `docs/**` only*
