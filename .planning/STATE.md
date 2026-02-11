# Project State: FSI-AgentGov

**Last Updated:** 2026-02-11
**Milestone:** v15 — Agent Usage & Performance Workbook
**Status:** IN PROGRESS — Phase 3 complete (6/8 plans complete), 1 phase remaining

## Session Ownership

**Active Tool:** copilot
**Session Started:** 2026-02-11 21:00
**Handoff Summary:** Phase 3 (Deployment & Customization) COMPLETE — deployment-guide.md and customization-guide.md created, mkdocs.yml nav updated, index.md updated, build passes. Next: `/gsd-execute-phase 4` to execute Framework Integration & Validation.

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-11)

**Core value:** Documentation and solutions that US FSI customers trust.
**Current focus:** v15 — Deployable Azure Monitor Workbook for Copilot Studio agent usage, performance, and error visibility (ALM separation-of-duties gap).

## Milestone Series Plan

```
v4: Audit Configuration Validator — SHIPPED
v5: Session Security Configurator — SHIPPED
v6: Agent Access Governance Monitor — SHIPPED
v7: Content Moderation Governance Monitor — SHIPPED
v7.1: Framework Currency Reviews — COMPLETE
v8: File Upload Security Configurator — SHIPPED
v9: Integration (ELM + Dashboard + cross-solution) — SHIPPED
v10: Conditional Access Automation — SHIPPED
v11: Technical Remediation — COMPLETE
v12: Quality & Consistency Polish — COMPLETE
v13: Agent Usage & Performance Workbook — DEFERRED (superseded by v15)
v14: SSPM Control Coverage Remediation — COMPLETE
v15: Agent Usage & Performance Workbook — IN PROGRESS (Phase 2 complete)
```

## Current Position

**Phase:** 4 — Framework Integration & Validation (NOT STARTED)
**Plan:** 04-01 and 04-02 ready after planning
**Status:** Phase 3 complete — deployment guide and customization guide delivered, verified, committed. Phase 4 planning needed.
**Last activity:** 2026-02-11 — Phase 3 executed and verified

**Progress:**
```
v1-v14: [=========================] COMPLETE (see MILESTONES.md)
v15:    [==================>      ] IN PROGRESS — Phase 3/4 complete, 6/8 plans complete
```

## Performance Metrics

**Cumulative (v1-v14):**
- Phases: 64 complete
- Plans: 201 complete
- Requirements: 336 delivered

**v15 Target:**
- Requirements: 12 (7 High, 4 Medium, 1 validation)

## Accumulated Context

### Decisions Made

See PROJECT.md Key Decisions table for full history.

**v15 decisions:**
- v15 picks up deferred v13 scope (Agent Usage & Performance Workbook) — renumbered to maintain series continuity
- Solution targets Application Insights as data source (not Dataverse or direct API)
- Azure Monitor Workbook format chosen over Power BI for RBAC-scoped access without additional licensing

**v11 decisions:**
- Zone 1/2/3 chosen as canonical governance terminology (replacing Tier/Level variants across all playbooks)
- DEC deployment guide: full v2.0 rewrite (not patch of v1.x CSV/Blob content)
- CAA policy naming: align validation scripts to FSI-* playbook convention (not CA-* pattern)
- Version footers: per-doc edit tracking (not uniform framework stamp)
- Two-worktree parallelism: A/B tracks target non-overlapping files per phase

### Key Constraints

- **No real-time:** Batch/daily feeds sufficient — no Dataverse webhook infrastructure
- **FSI language rules:** All documentation must use regulatory-safe language
- **Build validation:** mkdocs build --strict + verify_controls.py must pass
- **Two worktrees:** A and B tracks within each phase must not touch overlapping files
- **DEC staging:** Files in maintainers-local/solutions-staging/ are gitignored — changes there don't affect builds but must be consistent

### Blockers

None.

## Pending Todos

| Date | Todo | Priority |
|------|------|----------|
| 2026-02-11 | [Agent Usage & Performance Workbook for Enterprise ALM](todos/pending/2026-02-11-agent-usage-workbook-for-enterprise-alm.md) | High — **picked up as v15** |

## Session Continuity

**Active Tool:** copilot
**Session Started:** 2026-02-11 21:00
**Handoff Summary:** Plan 02-02 complete — `src/agent-usage-workbook.json` updated (46.7KB, 795 lines). All 3 tabs populated (Q01-Q23, 25 query items), zone-aware thresholds on 6 KPI items, enhanced header with v1.0.0/framework ref/prerequisites. JSON validated. Plan 02-03 next.

---

*State initialized: 2026-02-05*
*v11 milestone started: 2026-02-10*
*v12 completed: 2026-02-11*
*v13 defined then deferred: 2026-02-11*
*v14 milestone completed: 2026-02-11*
