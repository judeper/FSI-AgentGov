# Saul — Class-A Re-verification Batch (4 escalations)

**Verifier:** Saul (read-only QA)
**Verification date:** 2026-06-04
**Charter:** Independent factual verification against Microsoft Learn — no doc edits, no PRs.
**Source authorities used:** `microsoft-learn` MCP (`microsoft_docs_search`, `microsoft_docs_fetch`), Microsoft Release Communications MCP (M365 Roadmap, Azure Updates), `web_search` (corroboration only).

> Owl-mode discipline applied: a third-party blog post is **not** an authoritative GA announcement. M365 Roadmap forward-looking dates are **not** equivalent to "live MS Learn doc currently says GA." Where the live MS Learn surface still labels a feature Preview/Frontier, that label wins — regardless of older roadmap optimism.

---

## #370 — Pillar 3.9: Sentinel MCP Server "GA November 2025"

**Claim under review** (from `docs/controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md:41`):
> "**Sentinel MCP Server** (GA November 2025) is an optional analyst/SOC augmentation path…"

**Verdict: REFUTED.** No GA announcement for the Microsoft Sentinel MCP Server exists on Microsoft Learn. The most recent MS Learn label is **Preview** (September 2025).

### Quoted evidence

1. **What's new in Microsoft Sentinel** — `https://learn.microsoft.com/en-us/azure/sentinel/whats-new` (fetched 2026-06-04)
   - **September 2025 section, verbatim:**
     > "Microsoft Sentinel data lake is now generally available (GA)
     > Microsoft Sentinel graph (Preview)
     > **Microsoft Sentinel Model Context Protocol (MCP) server (Preview)**"
   - **November 2025 section:** contains the account-entity standardization update; **no MCP server entry and no GA milestone for MCP**. (Programmatic scan: November 2025 section contains zero "MCP" / "Model Context" mentions.)
   - **October 2025 section:** zero MCP/Model Context mentions.

2. **Sentinel MCP overview** — `https://learn.microsoft.com/azure/sentinel/datalake/sentinel-mcp-overview` (fetched 2026-06-04)
   - Title: *"What is Microsoft Sentinel's **support for** Model Context Protocol (MCP)?"*
   - Body never uses the strings "general availability" or "GA"; uses scenario language only ("Microsoft Sentinel … introduces support for Model Context Protocol").

3. **Azure Updates feed** (Microsoft Release Communications search for "Sentinel MCP server"): **zero items**. No Azure Update post announces GA.

### Recommended disposition (for a separate author)
Replace `(GA November 2025)` with `(Preview as of September 2025 — verify against the [Microsoft Sentinel What's New](https://learn.microsoft.com/en-us/azure/sentinel/whats-new) page at edit time)`, OR drop the parenthetical and link the live overview page. Do not invent a different GA month.

---

## #372 — Pillar 3.7: "Actions" page under PPAC **Security** node

**Claim under review** (from issue body summarising `docs/controls/pillar-3-reporting/3.7-*.md`): Actions page (formerly Power Platform Advisor) is located **under the Security node** in PPAC navigation.

**Verdict: REFUTED.** Microsoft Learn documents **Actions** as a top-level area of the Power Platform admin center, not a child node of Security. The Security page surfaces *contextual* recommendations from Actions, but Actions itself is a peer of Security, not a descendant.

### Quoted evidence

**Actions overview** — `https://learn.microsoft.com/power-platform/admin/power-platform-advisor` (fetched 2026-06-04)

1. Top-level placement, verbatim:
   > "**To view recommendations in the actions page:**
   > 1. Go to the [Power Platform admin center](https://admin.powerplatform.microsoft.com/).
   > 2. **Select Actions.**"

2. Security is a peer surface that consumes Actions data, not its parent:
   > "Contextual recommendations from the Power Platform actions page are also available in:
   > - Power Platform admin center
   >     - **Security page**
   >     - **Copilot page**
   >     - **Monitor page**"

3. "Power Platform Advisor" rename is confirmed by the URL slug (`power-platform-advisor`) and the Advisor card text:
   > "Power Platform admins can view the top recommendations on the **Advisor** card."

### Recommended disposition (for a separate author)
Update 3.7 navigation breadcrumb to top-level **Actions** (formerly Power Platform Advisor). Reframe the Security page reference as "the Security page in PPAC surfaces contextual recommendations from Actions" rather than asserting Actions is under Security. Update `docs/images/3.7/EXPECTED.md` accordingly on the next Last-UI-Verified pass.

---

## #373 — Pillar 3.13: "Computer Use — GA October 2025 (no longer Frontier-gated)"

**Claim under review** (from `docs/controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md:56`):
> "**Researcher with Computer Use Reporting** … Computer Use has been **generally available since October 2025** for tenants with Microsoft 365 Copilot licensing **(no longer Frontier-gated)**."

**Verdict: REFUTED.** The live MS Learn / Microsoft Support article — **last updated February 2026** — explicitly states Computer Use is **still Frontier-gated** (Frontier = pre-GA preview by Microsoft's own definition). The M365 Roadmap entry forecast GA for November 2025 but the official doc has not flipped to GA as of the verifier's fetch.

### Quoted evidence

1. **Get started using Researcher with Computer Use in Microsoft 365 Copilot (Frontier)** — `https://support.microsoft.com/topic/get-started-using-researcher-with-computer-use-in-microsoft-365-copilot-frontier-1f274537-6648-46e8-8264-052a49b92af4` (fetched 2026-06-04; page footer: *"Last updated: February 2026"*)
   - Title itself contains "**(Frontier)**".
   - Verbatim Note block:
     > "Researcher with Computer Use is available to users with a Microsoft 365 Copilot license as part of the Researcher agent. … **This feature is currently available through the Frontier program.**"

2. **Microsoft Copilot Frontier Program** — `https://learn.microsoft.com/microsoft-365/admin/manage/get-started-frontier` (fetched 2026-06-04). Frontier is Microsoft's pre-GA preview channel, verbatim:
   > "The Microsoft Frontier program gives organizations early access to innovative and emerging AI capabilities in Microsoft 365 **before those features reach general availability (GA)**."
   > "**Frontier features are preview and subject to change.**"

3. **Microsoft 365 admin center — agent details** — `https://learn.microsoft.com/microsoft-365/admin/manage/agent-details` (fetched 2026-06-04): describes Computer Use admin configuration without any "GA" or "generally available" label (programmatic scan: 0 GA mentions, 1 preview mention, 1 frontier mention).

4. **M365 Roadmap item 511796** ("Computer Use in Researcher", created 2025-10-30): forecast Preview October 2025 / GA November 2025; status still recorded as **"In development"**. A forward-looking roadmap is not an authoritative GA statement, and the live doc above contradicts the roadmap.

### Owl-mode adversarial check
A third-party blog (handsontek.net) claims "GA October 30, 2025 for tenants with Frontier access." This is internally contradictory ("GA … with Frontier access" — Frontier is by Microsoft's definition pre-GA). It is not a Microsoft authoritative source and is overridden by the live MS Learn / Support article. Do NOT use that blog as a GA citation.

### Recommended disposition (for a separate author)
Rewrite line 56 to: *"Researcher with Computer Use is available via the Microsoft Frontier program (preview) as of February 2026 — verify current status against the [Microsoft Learn Frontier program page](https://learn.microsoft.com/microsoft-365/admin/manage/get-started-frontier) at edit time."* Drop "(no longer Frontier-gated)" entirely — it is the inverse of the truth. Re-verify before each control edit, because Microsoft has telegraphed GA intent on the roadmap.

---

## #365 — Pillar 1.15: Customer Key Azure Key Vault SKU support

**Claim under review:** Does Microsoft support **both Standard and Premium** Azure Key Vault SKUs for Customer Key, and does it **recommend Premium (HSM-backed)** for production?

**Verdict: VERIFIED.** Microsoft Learn explicitly supports both SKUs and strongly recommends Premium for production; Standard is endorsed only for testing/validation.

### Quoted evidence

**Set up Customer Key** — `https://learn.microsoft.com/en-us/purview/customer-key-set-up` (fetched 2026-06-04)

Section heading: **"Create a premium Azure Key Vault in each subscription"**

Verbatim body:
> "When you create a key vault, you must choose an SKU: either Standard or Premium. The Standard SKU uses software-protected keys without a Hardware Security Module (HSM), while the premium SKU allows the use of HSMs to protect keys. **Customer Key supports key vaults with either of the two SKUs, but Microsoft strongly recommends using the Premium SKU.** The cost of operations is the same for both; so, the only price difference comes from the monthly cost of each HSM-protected key."

Follow-on guidance, verbatim:
> "**Use the Premium SKU key vaults and HSM-protected keys for production data. Use Standard SKU key vaults and keys only for testing and validation.**"

### What this means for the control text dispute
- Current control text (line 51) "Standard SKU minimum; Premium HSM-backed recommended" **understates** Microsoft's position — it suggests Standard is acceptable for production.
- Linus's proposed fix "Premium SKU required — Standard SKU is not supported" **overstates** Microsoft's position — Standard *is* supported, just only for test/validation.
- The wording in the issue body (Livingston's draft) is consistent with the MS Learn source.

### Recommended disposition (for a separate author)
The underlying fact is verified; the exact wording is a maintainer judgement. The wording proposed in #365 ("supports either SKU; Microsoft strongly recommends Premium for production; Standard for testing/validation only") is the only one of the three candidates that matches MS Learn verbatim. Also remove the "for Zone 3" qualifier from line 65, which currently implies Standard is acceptable for Zones 1/2 production.

---

## Summary table

| Issue | Claim | Verdict | Headline disposition |
|-------|-------|---------|----------------------|
| #370 | Sentinel MCP Server "GA November 2025" | **REFUTED** | Still **Preview** per Sep 2025 What's New; no GA announcement exists. Re-label as Preview or remove parenthetical. |
| #372 | PPAC "Actions" page lives under Security node | **REFUTED** | Actions is a **top-level** PPAC area; Security is a peer that surfaces contextual recommendations. Update breadcrumb. |
| #373 | "Computer Use GA October 2025 (no longer Frontier-gated)" | **REFUTED** | Live MS Support article (updated Feb 2026) explicitly says **still Frontier-program** (preview). Rewrite as Frontier/preview. |
| #365 | Customer Key supports both SKUs; Premium recommended for production | **VERIFIED** | MS Learn matches verbatim. Linus's "Premium required" fix is wrong; Livingston's drafted wording is correct. |

---

*Verifier: Saul · Run date: 2026-06-04 · Read-only; no doc edits performed.*
