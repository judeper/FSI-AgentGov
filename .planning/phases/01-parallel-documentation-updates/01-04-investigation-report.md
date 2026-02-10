---
phase: 1
plan: 4
type: investigation
created: 2026-02-10
title: "Multi-Source Governance Agent Investigation Report"
---

# Multi-Source Governance Agent Investigation Report

## 1. Executive Summary

This investigation evaluates three architectural approaches for a conversational governance agent that answers FSI control questions grounded in framework documentation, Microsoft Learn docs, and regulatory sources. **The recommendation is DEFER (Option B — Copilot Studio Agent)** to the v10+ timeframe, after the current solution milestone series (v8–v9) completes. The framework's current MkDocs site with 62 controls, 248 playbooks, and cross-linked regulatory mappings already provides strong coverage for the target audience; a conversational layer would add incremental value but is not critical path, and the MCP ecosystem is still maturing for the hybrid scenario.

---

## 2. Options Analysis

### 2.1 Option A: Custom MCP Server + External MCP Servers

**Description:** Build a custom MCP server that exposes FSI-AgentGov content (controls, playbooks, regulatory mappings) as structured resources and tools. Integrate the Microsoft Learn MCP server (GA since November 2025) for official documentation. Add regulatory site access (FINRA.org, SEC.gov) via web scraping or structured extraction for citation grounding.

| Criterion | Assessment |
|-----------|-----------|
| **Build effort** | 12–18 person-days |
| **Maintenance burden** | 6–10 hours/month |
| **Citation quality** | HIGH — structured tool responses enable precise control-level citations with section references |
| **Audience coverage** | Developers and AI tool users (VS Code, Claude Code, Codex CLI); does NOT cover end-user M365 admins without additional client work |
| **Technical feasibility** | MEDIUM — MCP spec is stable (2025-11-05 revision), TypeScript/Python SDKs available, but client ecosystem is still concentrated in developer tools |
| **Regulatory site access** | LOW — FINRA/SEC sites are not structured for machine consumption; scraping is brittle and raises terms-of-service concerns |

**Pros:**
- Machine-readable interface enables composability with any MCP-compatible client
- Precise citation control — each tool/resource maps to a specific control or playbook
- Content stays in the repo; MCP server reads from source of truth (no content duplication)
- Learn MCP server integration is straightforward (existing GA service)
- Aligns with the framework's existing multi-agent architecture (`.github/agents/`, `.claude/skills/`)

**Cons:**
- Audience mismatch: M365 administrators (primary audience) typically use portal-based tools, not MCP clients
- Build and maintain a server component (hosting, versioning, testing)
- Regulatory site access is the weakest link — FINRA/SEC content is not available via MCP or structured API
- Client compatibility is narrow today (VS Code Copilot, Claude Code, Cursor); Copilot Studio does not consume MCP servers as knowledge sources natively
- Monthly maintenance to keep resource schemas aligned with framework updates (new controls, renamed playbooks)

---

### 2.2 Option B: Copilot Studio Agent with Knowledge Sources

**Description:** Create a Copilot Studio agent using the published GitHub Pages site as a website knowledge source. Supplement with uploaded structured data files (CONTROL-INDEX.md, regulatory-mappings.md, solutions-index.md). Configure a system prompt with FSI language guardrails (from CONTRIBUTING.md) and regulatory reference patterns.

| Criterion | Assessment |
|-----------|-----------|
| **Build effort** | 3–5 person-days |
| **Maintenance burden** | 2–4 hours/month |
| **Citation quality** | MEDIUM — website knowledge source provides page-level citations but not section-level; uploaded files improve structured lookups |
| **Audience coverage** | HIGH — M365 admins and compliance officers access via Teams, M365 Copilot, or standalone web chat; matches primary audience |
| **Technical feasibility** | HIGH — Copilot Studio website knowledge sources, file uploads, and system prompts are all GA features |
| **Regulatory site access** | LOW-MEDIUM — can add FINRA.org and SEC.gov as website knowledge sources, but citation quality from external regulation sites is unpredictable |

**Pros:**
- Lowest build cost — 3–5 days to configure and test
- Native M365 integration — deployed to Teams, accessible to target audience without new tooling
- Dogfooding value — demonstrates Copilot Studio agent governance using the framework itself
- Website knowledge source auto-indexes GitHub Pages content; no extraction pipeline needed
- System prompt can enforce FSI language rules (no "ensures compliance", etc.)
- Supplements the framework's existing solutions portfolio (13 deployed solutions)

**Cons:**
- Citation granularity is page-level, not section-level (e.g., cites "Control 1.7" page, not the specific "Dataverse Environment-Level Audit Configuration" subsection)
- No programmatic/machine-readable access — single-client (Copilot Studio runtime)
- Website knowledge source has crawl depth and freshness limitations
- Uploaded files have size limits and require manual refresh when framework content changes
- Cannot serve developer tool integration use case (no MCP compatibility)

---

### 2.3 Option C: Hybrid — MCP Server + Copilot Studio Agent

**Description:** Build both an MCP server (for developer/tool integration) and a Copilot Studio agent (for end-user Q&A). Both consume the same verified source content from the FSI-AgentGov repositories.

| Criterion | Assessment |
|-----------|-----------|
| **Build effort** | 15–22 person-days |
| **Maintenance burden** | 8–14 hours/month |
| **Citation quality** | HIGH — MCP server provides structured citations; Copilot Studio provides conversational access |
| **Audience coverage** | FULL — developers via MCP clients, admins via Teams/M365 |
| **Technical feasibility** | MEDIUM — technically feasible but doubles the surface area |
| **Regulatory site access** | LOW — same FINRA/SEC limitations apply to both channels |

**Pros:**
- Covers all target audiences (admins, compliance officers, developers, AI agent authors)
- Single source of truth consumed by both interfaces
- MCP server could eventually feed Copilot Studio via custom connectors (future convergence)

**Cons:**
- Highest build and maintenance cost — two systems to build, test, host, and update
- Marginal incremental value of MCP server over Option B alone — the primary audience (M365 admins) is fully served by Copilot Studio
- Developer audience is small relative to admin audience for this framework
- Doubles the maintenance burden without doubling the value
- Risk of content drift between MCP server schema and Copilot Studio knowledge sources

---

### 2.4 Comparison Summary

| Criterion | Option A (MCP) | Option B (Copilot Studio) | Option C (Hybrid) |
|-----------|---------------|--------------------------|-------------------|
| Build effort | 12–18 days | **3–5 days** | 15–22 days |
| Monthly maintenance | 6–10 hrs | **2–4 hrs** | 8–14 hrs |
| Citation quality | **HIGH** | MEDIUM | **HIGH** |
| Primary audience fit | LOW | **HIGH** | HIGH |
| Technical risk | MEDIUM | **LOW** | MEDIUM |
| Regulatory access | LOW | LOW-MEDIUM | LOW |
| Dogfooding value | LOW | **HIGH** | MEDIUM |
| Time to first value | 3–4 weeks | **1 week** | 4–6 weeks |

---

## 3. Key Questions Analysis

### Q1: Is it overkill?

**Answer:** Partially — for most use cases, yes. The existing MkDocs site with its three-layer navigation (Framework → Controls → Playbooks), cross-linked regulatory mappings, and control index already provides comprehensive coverage. A conversational agent adds incremental value for two specific scenarios: (a) cross-cutting queries that span multiple controls and regulations (e.g., "What controls address FINRA 4511 for Zone 3 agents?"), and (b) onboarding new administrators who don't yet know the framework's structure. For experienced users who know where to look, the static site is faster and more reliable than a conversational interface.

**Confidence:** HIGH

**Nuance:** The framework's 62 controls × 4 playbooks each = 248 playbooks, plus 7+ regulatory bodies, creates a combinatorial space where cross-referencing is genuinely complex. A well-configured agent could surface connections that static navigation makes harder to discover. But the existing regulatory-mappings.md (1,386 lines) and CONTROL-INDEX.md already address much of this.

---

### Q2: GitHub repos as knowledge source — effective for reasoning, or structured extraction needed?

**Answer:** Directly pointing at the repos is partially effective but not optimal.

- **What works:** The Markdown files are well-structured with consistent 10-section format, YAML-style metadata, and cross-references. An LLM can reason over this structure reasonably.
- **What doesn't:** Raw repo access includes non-user-facing files (scripts, planning, templates, CHANGELOG) that pollute the context. The `.github/`, `.claude/`, `.planning/` directories contain agent configuration that would confuse a governance Q&A agent.
- **Better approach:** Use the published GitHub Pages site as the knowledge source (already filtered to user-facing content) or create a curated content extraction that includes only `docs/controls/`, `docs/playbooks/`, `docs/framework/`, and `docs/reference/`.

**Confidence:** HIGH

---

### Q3: Learn MCP server value — does it justify integration?

**Answer:** Yes, but only for Option A or C. The Microsoft Learn MCP server (GA since November 2025, already documented in Control 3.9 for Sentinel integration) provides authoritative Microsoft documentation that complements the framework's FSI-specific guidance. Common user questions like "How do I configure Purview Communication Compliance?" require both framework guidance (what to configure for FSI governance) and Learn docs (how to configure it in the portal). However, for Option B (Copilot Studio), adding learn.microsoft.com as a website knowledge source achieves a similar (though less structured) result without MCP integration.

**Confidence:** MEDIUM — The quality delta between Learn MCP server structured responses and Learn website crawling in Copilot Studio has not been empirically tested for this use case.

---

### Q4: Regulatory site access — can we reliably extract and cite FINRA/SEC content?

**Answer:** Not reliably. FINRA.org and SEC.gov content is published as HTML pages and PDFs without structured APIs. Key challenges:

- **FINRA Rules:** Available at finra.org/rules-guidance but not in machine-readable format. Rule text changes infrequently but site structure changes could break scraping.
- **SEC Rules:** Available at sec.gov/rules but spread across multiple document formats (HTML, PDF, Federal Register entries). 17a-3 and 17a-4 are codified in 17 CFR, which is available via eCFR.gov (more structured, but still HTML).
- **FINRA Notices:** Notice 25-07 and similar are PDFs with no API access.
- **Terms of service:** Both sites have terms that may restrict automated scraping.

**Better alternative:** The framework's `regulatory-mappings.md` (1,386 lines) already contains curated regulatory citations with specific section references. Using this file as a knowledge source provides more reliable regulatory grounding than attempting to scrape source sites.

**Confidence:** HIGH

---

### Q5: Build vs. buy — existing tools or services?

**Answer:** Several existing capabilities reduce the build scope:

| Capability | Existing Solution | Gap |
|-----------|------------------|-----|
| Website Q&A | Copilot Studio website knowledge source | Page-level citations only |
| Microsoft Learn access | Learn MCP server (GA) | Requires MCP client |
| Repo content access | GitHub Copilot (already in use) | Not a standalone Q&A agent |
| Regulatory text | Framework's regulatory-mappings.md | Static, not conversational |
| Custom MCP server | TypeScript/Python SDKs available | Requires custom build |
| Sentinel integration | Sentinel MCP server (GA, documented in Control 3.9) | Narrow scope (security events only) |

**Key finding:** Copilot Studio's website knowledge source feature is essentially "buy" for Option B — the agent platform is already licensed (M365), the content is already published (GitHub Pages), and the configuration is declarative. The remaining "build" is system prompt engineering and testing, not infrastructure.

**Confidence:** HIGH

---

### Q6: Maintenance burden — who keeps it in sync?

**Answer:** The framework already has an established update cadence:

- Controls are updated on a monthly or per-milestone basis (currently v7.1)
- GitHub Pages site rebuilds automatically on merge to main
- The `scripts/verify_controls.py` and `mkdocs build --strict` validation pipeline catches structural issues

**For Option B (Copilot Studio):** Maintenance is minimal because the website knowledge source auto-crawls the published site. When controls are updated, the agent's knowledge refreshes on the next crawl cycle. Uploaded supplementary files (control index, regulatory mappings) require manual refresh — estimated 1–2 hours per milestone release.

**For Option A (MCP Server):** Maintenance is higher because the MCP server's resource/tool schema must be kept in sync with the framework's control structure. Adding a new control (rare — last addition was v1) requires updating the MCP server. Changing a control's structure or renaming playbooks requires schema updates.

**Owner:** The framework maintainer (currently single-maintainer repo) would own both the framework content and any agent/MCP server. This is the key risk — adding maintenance burden to a single maintainer.

**Confidence:** HIGH

---

## 4. Recommendation

### DEFER — Option B (Copilot Studio Agent)

**Recommendation:** Defer implementation to v10+ milestone, after the current solution series (v8: File Upload Security Configurator, v9: Integration) completes.

### Justification

1. **Value is incremental, not transformative.** The existing MkDocs site with 62 controls, 248 playbooks, and comprehensive cross-references already serves the primary audience well. A conversational agent improves discovery for cross-cutting queries and onboarding, but does not unlock capabilities that are currently impossible.

2. **Option B is the right approach.** Copilot Studio with website knowledge source has the best fit for the primary audience (M365 admins), the lowest build cost (3–5 days), the lowest maintenance burden (2–4 hrs/month), and provides dogfooding value by demonstrating the very governance framework it serves. Option A (MCP) serves a developer audience that is secondary for this framework. Option C (Hybrid) doubles cost without doubling value.

3. **Defer, not don't-build.** The value is real but the timing is wrong. The framework is in a maintenance milestone (v7.1) with three remaining solution milestones (v8, v9) ahead. The single maintainer should focus on shipping solutions before adding a new maintenance surface. Deferring to v10+ allows:
   - The MCP ecosystem to mature further (potentially enabling Copilot Studio → MCP integration, which would make Option B upgradeable to Option C without a rebuild)
   - The solution series to complete, freeing maintenance capacity
   - Copilot Studio's knowledge source capabilities to improve (better citation granularity, deeper crawling)

4. **Regulatory site access is not viable today.** The weakest link across all three options is reliable FINRA/SEC content extraction. The framework's curated regulatory-mappings.md is a better source than scraping. This limitation doesn't change with any of the three architectural options.

5. **Single-maintainer risk.** Adding a new system (agent or MCP server) to a single-maintainer repository increases bus factor risk. Completing the solution series first and then evaluating capacity is more prudent.

---

## 5. Deferred Implementation Details

### Recommended Approach

**Option B: Copilot Studio Agent with Knowledge Sources**

### Estimated Effort

| Activity | Effort |
|----------|--------|
| Copilot Studio agent creation and system prompt | 1 day |
| Website knowledge source configuration (GitHub Pages) | 0.5 days |
| Supplementary file uploads (control index, regulatory mappings, solutions index) | 0.5 days |
| FSI language guardrail testing (no "ensures compliance", etc.) | 1 day |
| Cross-cutting query testing (multi-control, multi-regulation) | 1 day |
| Documentation and deployment guide | 0.5 days |
| **Total** | **4.5 person-days** |

### Estimated Monthly Maintenance

| Activity | Monthly Hours |
|----------|---------------|
| Refresh uploaded files after milestone releases | 1–2 hrs |
| System prompt tuning based on user feedback | 1 hr |
| Monitor citation quality and knowledge source freshness | 0.5 hrs |
| **Total** | **2.5–3.5 hrs/month** |

### Recommended Milestone

**v10** — First milestone after the solution series (v8, v9) completes. By that point:
- All 13+ solutions will be deployed, providing the full solution catalog as knowledge context
- The MCP ecosystem may support Copilot Studio → MCP integration, enabling a future upgrade path
- Maintenance capacity will be freed from active solution development

### Prerequisites

1. GitHub Pages site remains published and accessible for website knowledge source crawling
2. Copilot Studio license available in the target tenant (included with M365 E3/E5 or Power Platform per-user)
3. FSI language rules documented in CONTRIBUTING.md (already exists)
4. Control index and regulatory mappings in stable format (already exists)

### Future Upgrade Path (v10+ → v11+)

If Copilot Studio adds native MCP server consumption (currently not available), the Option B agent could be upgraded to Option C (Hybrid) by:
1. Building the MCP server as a separate component
2. Connecting Copilot Studio to the MCP server via custom connector or native MCP integration
3. This preserves the Option B investment while extending to developer audiences

---

## 6. Alternative Improvements (Low-Effort, No Build Required)

While deferring the agent build, these low-effort improvements to the existing documentation could address some of the same user needs:

| Improvement | Effort | Impact |
|-------------|--------|--------|
| Add a "Controls by Regulation" cross-reference table to the getting-started guide | 2 hours | Helps users find controls by regulatory requirement without needing cross-cutting search |
| Add FAQ section to getting-started with common multi-control questions | 3 hours | Addresses the "onboarding discovery" use case directly |
| Enhance CONTROL-INDEX.md with regulation tags per control | 2 hours | Enables browser Ctrl+F to find controls by regulation name |
| Add MkDocs search plugins for better full-text search | 1 hour | Improves static site discoverability without building a conversational layer |

These improvements are out of scope for v7.1 but could be included in v8 or v9 as documentation enhancements.

---

## Appendix A: MCP Ecosystem Maturity Assessment (February 2026)

| Factor | Status |
|--------|--------|
| MCP specification | Stable (2025-11-05 revision) |
| TypeScript SDK | GA, well-supported |
| Python SDK | GA, well-supported |
| VS Code Copilot MCP support | GA |
| Claude Code MCP support | GA |
| Copilot Studio MCP consumption | Not available |
| Microsoft Learn MCP server | GA (November 2025) |
| Sentinel MCP server | GA (November 2025, documented in Control 3.9) |
| MCP server hosting options | Local (stdio), Remote (SSE/HTTP) |
| Enterprise auth for MCP | Limited — OAuth support in spec but adoption varies |

## Appendix B: Framework Content Inventory

| Content Type | Count | Format |
|-------------|-------|--------|
| Controls | 62 | Markdown (10-section template) |
| Playbooks (per-control) | 248 | Markdown (4 per control) |
| Advanced implementation playbooks | 27+ | Markdown |
| Deployed solutions | 13 | Power Platform + documentation |
| Regulatory bodies covered | 7+ | FINRA, SEC, SOX, GLBA, OCC, Fed, CFTC |
| Specific regulations mapped | 15+ | In regulatory-mappings.md (1,386 lines) |
| Framework documents | 11 | Markdown |
| Reference documents | 10+ | Markdown |
| Total published pages | 400+ | MkDocs static HTML |

## Appendix C: Requirements Traceability

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **FCR-13:** Investigation report with build/don't-build/defer recommendation | ✅ Complete | This document — recommendation is DEFER |
| **FCR-14:** Estimated effort and approach if build/defer | ✅ Complete | Section 5 — Option B, 4.5 person-days, 2.5–3.5 hrs/month maintenance, target v10 |

---

*Investigation completed: 2026-02-10*
*Investigator: GitHub Copilot*
*Recommendation: DEFER Option B (Copilot Studio Agent) to v10+*
