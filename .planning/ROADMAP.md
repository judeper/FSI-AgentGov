# Roadmap: Technical Remediation (v11)

## Overview

Comprehensive remediation of 107 findings and 42 gaps identified by full technical audit of all solutions (CAA, DEC, ELM, PCG), framework docs, reference docs, operational playbooks, and control implementation playbooks. Organized by risk: runtime failures first, then regulatory accuracy, then consistency, then backfill.

**Audit scope:** 19 solutions, 62 controls, ~250 playbooks, 12 framework docs, 21 reference docs, 30 operational playbooks, ~25 scripts/artifacts.

**Execution model:** Each phase has two plans (A/B) targeting non-overlapping file sets for parallel worktree execution. An operator can run two VS Code sessions simultaneously, one per worktree/branch.

## Phases

- [x] **Phase 1: Critical Runtime Fixes** — Fix bugs that cause actual deployment/runtime failures in CAA and DEC solutions
- [x] **Phase 2: Regulatory & Technical Accuracy** — Fix regulatory citation errors, control count mismatches, and solution technical contradictions
- [x] **Phase 3: Terminology & Version Normalization** — Standardize Zone/Tier/Level language, role names, and version footers across all docs
- [x] **Phase 4: Cross-Reference & Link Integrity** — Fix broken cross-references, missing solution mappings, path errors
- [x] **Phase 5: Script & Code Fixes** — Fix PowerShell bugs, non-existent cmdlets, parameter mismatches in scripts and playbooks
- [ ] **Phase 6: Gap Backfill & Design Improvements** — Create missing deployment guides, operational playbooks, and inter-document linking

## Phase Details

### Phase 1: Critical Runtime Fixes
**Goal:** Eliminate bugs that would cause runtime failures if CAA or DEC solutions are deployed as documented
**Depends on:** Nothing (first phase, highest priority)
**Requirements:** RTF-01 through RTF-10
**Success Criteria:**
  1. CAA Dataverse column names match between flow JSON and schema Python script
  2. CAA flows reference correct documentation URL slugs
  3. CAA private helper scripts exist (or Test-PolicyCompliance.ps1 works standalone)
  4. CAA policy naming convention is consistent between validation scripts and playbook templates
  5. DEC severity and zone option set values match between correlation engine and schema
  6. DEC deployment guide describes v2.0 Dataverse architecture (not v1.x CSV/Blob)
  7. DEC Power BI playbook uses Dataverse connector (not CSV file sources)
  8. DEC extraction scripts derive zone from agent metadata (not hardcoded '1')
**Plans:** 2 (A = CAA, B = DEC — no file overlap)

Plans:
- [ ] 01-01-PLAN.md — CAA Runtime Fixes (RTF-01 through RTF-05) — Worktree A
- [ ] 01-02-PLAN.md — DEC Runtime Fixes (RTF-06 through RTF-10) — Worktree B

### Phase 2: Regulatory & Technical Accuracy
**Goal:** Fix regulatory citation errors and solution technical contradictions that affect compliance accuracy
**Depends on:** Nothing (independent of Phase 1)
**Requirements:** RTA-01 through RTA-10
**Success Criteria:**
  1. Pillar 1 control count reads "24" everywhere (not "23"), total reads "62" (not "61")
  2. FINRA 25-07 references are corrected or clarified across all files
  3. SEC 17a-3/4 retention periods distinguish 3-year communications from 6-year records
  4. Zone 3 retention period is consistent (7 or 10 years) across all docs
  5. ELM Lab 3 does not instruct users to pass SecurityGroupId at creation time
  6. ELM zone rationale collected for Zone 2 (not just Zone 3)
  7. PCG Lab ingestion uses upsert (not "Add a new row")
  8. "Azure AD" replaced with "Microsoft Entra ID" across PCG playbooks
**Plans:** 2 (A = Framework/Reference, B = Solution Playbooks — no file overlap)

Plans:
- [ ] 02-01-PLAN.md — Framework & Reference Accuracy (RTA-01 through RTA-05) — Worktree A
- [ ] 02-02-PLAN.md — Solution Playbook Accuracy (RTA-06 through RTA-10) — Worktree B

### Phase 3: Terminology & Version Normalization
**Goal:** Standardize governance terminology (Zone/Tier/Level), role names, and version footers across all docs
**Depends on:** Nothing (independent, but best after Phase 2)
**Requirements:** TVN-01 through TVN-06
**Success Criteria:**
  1. All playbooks use "Zone 1/2/3" (no "Tier" or "Level" variants without mapping note)
  2. Role names match role-catalog.md canonical names across all playbooks
  3. All footer version strings updated to current framework version
  4. Framework document count accurate in index.md
  5. Glossary includes Agent 365, Entra Agent ID, Blueprint, Sponsor terms
**Plans:** 2 (A = Terminology, B = Version/Metadata — minimal file overlap)

Plans:
- [ ] 03-01-PLAN.md — Governance Terminology Standardization (TVN-01 through TVN-03) — Worktree A
- [ ] 03-02-PLAN.md — Version & Metadata Normalization (TVN-04 through TVN-06) — Worktree B

### Phase 4: Cross-Reference & Link Integrity
**Goal:** Fix broken cross-references, missing solution mappings, and path errors across controls, playbooks, and reference docs
**Depends on:** Phase 2 (uses corrected control counts/names)
**Requirements:** XRL-01 through XRL-06
**Success Criteria:**
  1. CAA solution referenced in Controls 1.23 and 1.18
  2. DEC coverage includes Control 1.8 in solutions-coverage-gaps.md
  3. Evidence-pack-assembly.md paths point to actual file locations
  4. Legacy "Gap N" references replaced with actual playbook/control names
  5. ELM environment group names consistent between provisioning and Control 2.2
  6. Solutions-index version numbers match actual solution versions
**Plans:** 2 (A = Solution cross-refs, B = Navigation & naming — minimal overlap)

Plans:
- [ ] 04-01-PLAN.md — Solution Cross-Reference Fixes (XRL-01 through XRL-03) — Worktree A
- [ ] 04-02-PLAN.md — Navigation & Naming Fixes (XRL-04 through XRL-06) — Worktree B

### Phase 5: Script & Code Fixes
**Goal:** Fix PowerShell bugs, non-existent cmdlets, and parameter mismatches in scripts and playbooks
**Depends on:** Phase 1 (CAA/DEC scripts already fixed)
**Requirements:** SCF-01 through SCF-06
**Success Criteria:**
  1. Test-PolicyCompliance.ps1 $isBlock variable scoped correctly
  2. CAA module manifest exports only existing functions
  3. 4.7 PowerShell SKU filter uses SkuPartNumber (not SkuId regex)
  4. Non-existent cmdlets in promotion gates marked as pseudocode or replaced
  5. Cross-solution integration parameter names aligned (SolutionId vs Solution)
  6. Search-UnifiedAuditLog pagination warnings added to audit query playbooks
**Plans:** 2 (A = PowerShell/Script bugs, B = Config & Schema gaps)

Plans:
- [ ] 05-01-PLAN.md — PowerShell & Script Bugs (SCF-01 through SCF-04) — Worktree A
- [ ] 05-02-PLAN.md — Config, Schema & Documentation (SCF-05 through SCF-06) — Worktree B

### Phase 6: Gap Backfill & Design Improvements
**Goal:** Create missing deployment guides, operational playbooks, and design improvements identified during audit
**Depends on:** Phases 1-5 (build on corrected foundation)
**Requirements:** GBD-01 through GBD-08 (advisory — scope to be refined)
**Success Criteria:**
  1. CAA end-to-end deployment guide exists
  2. ELM approval flow implementation documented
  3. Pillar 4 portal walkthroughs include parent control caveats (reindexing, EEEU, discovery amplification)
  4. DSPM policy pack has portal deployment steps
  5. Spec-level playbooks interlinked (confidence <-> HITL <-> explainability)
**Plans:** 2 (A = Gap backfill, B = Design improvements)

Plans:
- [ ] 06-01-PLAN.md — Gap Backfill (GBD-01 through GBD-04) — Worktree A
- [ ] 06-02-PLAN.md — Design Improvements (GBD-05 through GBD-08) — Worktree B

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Critical Runtime Fixes | 0/2 | Not started |
| 2. Regulatory & Technical Accuracy | 0/2 | Not started |
| 3. Terminology & Version Normalization | 0/2 | Not started |
| 4. Cross-Reference & Link Integrity | 2/2 | Complete |
| 5. Script & Code Fixes | 2/2 | Complete |
| 6. Gap Backfill & Design Improvements | 0/2 | Not started |

## Parallel Execution Guide

Each phase's two plans target **non-overlapping files** and can run in parallel worktrees:

| Phase | Plan A (Worktree A) | Plan B (Worktree B) |
|-------|---------------------|---------------------|
| 1 | CAA: src/*.json, scripts/*.py, scripts/*.ps1, scripts/private/ | DEC: docs/playbooks/advanced-implementations/deny-event-*, maintainers-local/solutions-staging/deny-event-* |
| 2 | Framework: docs/framework/*, docs/reference/*, docs/getting-started/* | Solutions: docs/playbooks/advanced-implementations/environment-*, platform-change-*, docs/controls/pillar-2-management/* |
| 3 | Playbooks: docs/playbooks/control-implementations/*, docs/reference/role-catalog.md | Metadata: all file footers (version strings), docs/framework/index.md, docs/reference/glossary.md |
| 4 | References: docs/controls/pillar-1-security/1.23*, 1.18*, docs/reference/solutions-coverage-gaps.md | Navigation: docs/playbooks/compliance-and-audit/*, docs/playbooks/advanced-implementations/platform-change-governance/*, docs/reference/solutions-index.md |
| 5 | Scripts: scripts/Test-PolicyCompliance.ps1, scripts/conditional-access-automation.psd1, docs/playbooks/control-implementations/4.7/* | Config: maintainers-local/solutions-staging/cross-solution-integration/*, docs/playbooks/monitoring-and-validation/* |
| 6 | Guides: docs/playbooks/advanced-implementations/ (new files), docs/playbooks/control-implementations/4.1-4.7/* | Design: docs/playbooks/advanced-implementations/ (linking), docs/getting-started/quick-start.md, docs/playbooks/governance-operations/* |

**Worktree setup:**
```bash
git worktree add ../FSI-AgentGov-WTA -b v11/phase-N-track-a
git worktree add ../FSI-AgentGov-WTB -b v11/phase-N-track-b
```

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| RTF-01 | 1 | 01-01 | Fix fsi_result_json column name in flow JSON |
| RTF-02 | 1 | 01-01 | Add 6 missing Dataverse columns to schema |
| RTF-03 | 1 | 01-01 | Fix documentation URL slug in 3 CAA artifacts |
| RTF-04 | 1 | 01-01 | Create 3 missing private helper scripts |
| RTF-05 | 1 | 01-01 | Align CA policy naming (FSI-* convention) |
| RTF-06 | 1 | 01-02 | Fix DEC severity option set mismatch |
| RTF-07 | 1 | 01-02 | Fix DEC zone option set value mismatch |
| RTF-08 | 1 | 01-02 | Rewrite DEC deployment guide for v2.0 |
| RTF-09 | 1 | 01-02 | Update DEC Power BI playbook to Dataverse |
| RTF-10 | 1 | 01-02 | Fix hardcoded zone in DEC extraction scripts |
| RTA-01 | 2 | 02-01 | Fix Pillar 1 count (23->24) and total (61->62) |
| RTA-02 | 2 | 02-01 | Audit/fix FINRA 25-07 references |
| RTA-03 | 2 | 02-01 | Fix SEC 17a-3/4 retention period |
| RTA-04 | 2 | 02-01 | Resolve Zone 3 retention conflict (7 vs 10 yr) |
| RTA-05 | 2 | 02-01 | Fix solution count inconsistencies, CFTC 1.31 |
| RTA-06 | 2 | 02-02 | Fix ELM Lab 3 SecurityGroup + Zone Rationale |
| RTA-07 | 2 | 02-02 | Fix ELM non-existent Get-CrmRolePrivilege |
| RTA-08 | 2 | 02-02 | Fix PCG upsert + state-setting + pagination |
| RTA-09 | 2 | 02-02 | Replace Azure AD with Microsoft Entra ID in PCG |
| RTA-10 | 2 | 02-02 | Fix DEC column names, table count, module name |
| TVN-01 | 3 | 03-01 | Standardize Zone 1/2/3 in all playbooks |
| TVN-02 | 3 | 03-01 | Normalize role names to role-catalog canonical |
| TVN-03 | 3 | 03-01 | Add Zone/Tier/Level mapping note |
| TVN-04 | 3 | 03-02 | Align all version footers to v1.2.38 |
| TVN-05 | 3 | 03-02 | Add glossary entries for Agent 365 terms |
| TVN-06 | 3 | 03-02 | Fix framework doc count, ELM footer versions |
| XRL-01 | 4 | 04-01 | Add CAA ref to Controls 1.23, 1.18 |
| XRL-02 | 4 | 04-01 | Add Control 1.8 to DEC coverage gaps |
| XRL-03 | 4 | 04-01 | Add AAM, FUS to solutions-coverage-gaps.md |
| XRL-04 | 4 | 04-02 | Fix evidence-pack-assembly.md paths |
| XRL-05 | 4 | 04-02 | Replace "Gap N" with actual references |
| XRL-06 | 4 | 04-02 | Fix ELM env group names, PCG version, etc. |
| SCF-01 | 5 | 05-01 | Fix $isBlock scope in Test-PolicyCompliance.ps1 |
| SCF-02 | 5 | 05-01 | Fix CAA module manifest export list |
| SCF-03 | 5 | 05-01 | Fix 4.7 PowerShell SKU filter |
| SCF-04 | 5 | 05-01 | Mark pseudocode cmdlets in promotion gates |
| SCF-05 | 5 | 05-02 | Fix cross-solution integration parameter names |
| SCF-06 | 5 | 05-02 | Add audit log pagination warnings |
| GBD-01 | 6 | 06-01 | Create CAA end-to-end deployment guide |
| GBD-02 | 6 | 06-01 | Document ELM approval flow implementation |
| GBD-03 | 6 | 06-01 | Backfill P4 portal walkthrough caveats |
| GBD-04 | 6 | 06-01 | Add DSPM portal deployment steps |
| GBD-05 | 6 | 06-02 | Interlink spec-level playbooks |
| GBD-06 | 6 | 06-02 | FAQ timeline reconciliation note |
| GBD-07 | 6 | 06-02 | Fix footnote markers in governance-ops |
| GBD-08 | 6 | 06-02 | Remove quick-start emojis (optional) |

**Total: 38/38 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-10*
*Depth: comprehensive*
*Phases: 6 (runtime -> regulatory -> terminology -> xrefs -> scripts -> gaps)*
