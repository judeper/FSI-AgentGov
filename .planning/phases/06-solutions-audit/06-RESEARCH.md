# Phase 6: Solutions Audit - Research

**Researched:** 2026-02-03
**Domain:** Solution maturity assessment, cross-repository documentation audit, technical debt resolution
**Confidence:** HIGH

## Summary

This research examines the current state of 13 deployable solutions in the FSI-AgentGov-Solutions companion repository, the 5 TECH debt items to resolve, and the framework documentation (solutions-index.md, solutions-integration.md) that must be updated. The research identifies what each solution contains, assesses preliminary maturity indicators, catalogs regulatory alignment claims requiring verification, and maps TECH items to specific files.

The 13 solutions divide into two clear maturity tiers: 4 "older" solutions (ELM v1.1.2, MCM v2.1.1, PGC v1.0.8, DEC v1.1.0) with multiple version iterations and richer file structures, and 9 "newer" solutions (all v1.0.0, February 2026) with varying levels of documentation and script completeness. The solutions-integration.md only covers the 4 older solutions in depth -- the 9 newer solutions need equal coverage added.

**Primary recommendation:** Structure the audit as solution-by-solution review with a standardized checklist, followed by TECH debt resolution, then framework documentation updates. Solutions should be batched into 3-4 plans to keep each plan manageable.

## Current State Assessment

### Solution File Inventory

Each solution was examined for file structure depth. This is a key maturity indicator since the CONTEXT.md establishes that solutions are documentation artifacts.

#### Tier A: Multi-Version Solutions (older, more mature)

| Solution | Version | Script Files | Doc Files | Other Files | Total |
|----------|---------|-------------|-----------|-------------|-------|
| Environment Lifecycle Management | v1.1.2 | 9 Python scripts | 7 docs | 3 templates, checklist | ~20 |
| Message Center Monitor | v2.1.1 | 0 (src/README placeholder) | 5 guides | 1 JSON template | ~8 |
| Pipeline Governance Cleanup | v1.0.8 | 2 PowerShell | 7 guides | 3 samples | ~14 |
| Deny Event Correlation Report | v1.1.0 | 4 PowerShell | 3 docs | 4 KQL queries | ~12 |

#### Tier B: v1.0.0 Solutions (newer, February 2026)

| Solution | Script Files | Doc Files | Other Files | Total |
|----------|-------------|-----------|-------------|-------|
| FINRA Supervision Workflow | 2 Python (deploy.py, export) | 7 docs | 1 requirements.txt | ~11 |
| Conditional Access Automation | 3 PowerShell | 5 docs | 8 JSON templates | ~17 |
| Compliance Dashboard | 1 Python (load_sample) | 6 docs | 1 JSON sample data | ~9 |
| Segregation Detector | 2 PowerShell | 4 docs | - | ~7 |
| Scope Drift Monitor | 1 PowerShell | 2 docs | - | ~4 |
| RAG Source Validator | 1 PowerShell | 1 doc (schema) | - | ~3 |
| COI Testing | 1 Python | 0 referenced docs | 1 requirements.txt | ~4 |
| Hallucination Tracker | 1 Python | 0 referenced docs | - | ~3 |
| DR Testing Framework | 1 PowerShell | 0 referenced docs | - | ~3 |

**Key Observation:** Several newer solutions reference docs/ folders in their READMEs (e.g., `docs/prerequisites.md`, `docs/troubleshooting.md`) but these files may not exist on disk. The READMEs list documentation guides in tables but the actual files may be missing. This is a critical audit finding -- documentation references that lead to 404s.

### Solutions-Integration.md Gap

The current `docs/framework/solutions-integration.md` covers only 4 solutions (ELM, MCM, PGC, DEC) with detailed control mappings, zone applicability matrix, deployment sequence, and CoE alignment. The CONTEXT.md decision requires expanding this to cover all 13 solutions at equal depth.

**Current coverage:** 4/13 solutions (31%)
**Required coverage:** 13/13 solutions (100%)

The Mermaid diagram only shows 4 solutions and needs expansion.

### Solutions-Index.md State

The `docs/reference/solutions-index.md` already lists all 13 solutions with descriptions, version info, regulatory alignment, and related controls. However:

- No status/maturity column exists (must be added per CONTEXT.md decision)
- Version history table at bottom has correct versions
- Some version numbers in the "Repository Structure" code block are outdated (shows v1.0.1 for ELM, v2.0.0 for MCM, v1.0.0 for DEC)

## TECH Debt Item Analysis

### TECH-03: PAYG vs Premium Licensing in Control 2.1

**Status:** PARTIALLY ADDRESSED
**Confidence:** HIGH

Control 2.1 already contains a `!!! danger` admonition titled "Pay-As-You-Go Does NOT Satisfy Managed Environment Licensing" (lines 39-48) that clearly states PAYG meters do NOT satisfy Managed Environment licensing for active users. This appears to have been added previously (possibly Phase 2 or Phase 4).

**Remaining work:** Verify this warning is complete and accurate. Check if any solution docs (especially ELM) reference PAYG as valid for Managed Environments. Cross-reference with current Microsoft Learn documentation.

**Files to check:**
- `/Users/admin/dev/FSI-AgentGov/docs/controls/pillar-2-management/2.1-managed-environments.md` (already has warning)
- `/Users/admin/dev/FSI-AgentGov-Solutions/environment-lifecycle-management/README.md` (references licensing)
- `/Users/admin/dev/FSI-AgentGov/docs/playbooks/control-implementations/2.1/portal-walkthrough.md`
- `/Users/admin/dev/FSI-AgentGov/docs/playbooks/control-implementations/2.1/troubleshooting.md`

### TECH-04: Service Principal Security Group Bypass Risk

**Status:** NOT DOCUMENTED
**Confidence:** HIGH

No controls or solution docs currently document the risk that Service Principals may bypass security group-based access controls. A grep across all control files found zero matches for "Service Principal.*security group.*bypass" or similar patterns.

**What needs documenting:** When Conditional Access policies or DLP policies use security group assignments, Service Principals (used by Power Automate flows, automation scripts) may not be members of those groups and therefore bypass the controls. This is a known Microsoft platform behavior.

**Files to update (decision: use `!!! warning` admonition):**
- Controls that reference security group-based enforcement:
  - `1.11-conditional-access-and-phishing-resistant-mfa.md`
  - `1.4-advanced-connector-policies-acp.md` (DLP policies)
  - `2.8-access-control-and-segregation-of-duties.md`
- Solution docs:
  - `conditional-access-automation/README.md` (directly relevant)
  - `environment-lifecycle-management/README.md` (uses Service Principal)

### TECH-05: DLP Enforcement Mode Confusion (Soft-Enabled vs Enabled)

**Status:** PARTIALLY ADDRESSED
**Confidence:** HIGH

Control 1.5 already contains an enforcement timeline table (lines 36-43) showing Soft-Enabled (January 2025, audit-only) vs Enabled (February 2025, full enforcement) vs Complete (March 2025, all tenants). The distinction is clearly documented.

**Remaining work:** Verify the language in all related playbooks and solutions is consistent. Check if any docs still reference the old opt-out capability or suggest DLP enforcement is optional.

**Files to check:**
- `/Users/admin/dev/FSI-AgentGov/docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` (already has timeline)
- `/Users/admin/dev/FSI-AgentGov/docs/playbooks/control-implementations/1.5/` (all 4 playbooks)
- `/Users/admin/dev/FSI-AgentGov-Solutions/deny-event-correlation-report/` (correlates DLP events)

### TECH-06: Defender Two-Portal Configuration

**Status:** PARTIALLY ADDRESSED IN PHASE 4
**Confidence:** HIGH

Control 1.8 already has a "Two-Portal Configuration Required" section explaining both the Defender Portal and PPAC steps. Phase 4 Plan 04-04 addressed verification and cross-control consistency for Defender.

**Remaining work:** Verify the two-portal configuration guidance is complete and consistent across:
- Control 1.8 (primary, already detailed)
- Any solutions that reference Defender integration
- Check if deny-event-correlation-report references Defender CloudAppEvents

**Files to check:**
- `/Users/admin/dev/FSI-AgentGov/docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- `/Users/admin/dev/FSI-AgentGov-Solutions/deny-event-correlation-report/README.md` (lists Defender CloudAppEvents as optional data source)
- `/Users/admin/dev/FSI-AgentGov/docs/playbooks/control-implementations/1.8/`

### TECH-07: Information Barriers Channel Agent Limitation

**Status:** ALREADY DOCUMENTED
**Confidence:** HIGH

Control 1.22 already has a comprehensive `!!! warning "Channel Agent vs. Copilot Studio Agent IB Support"` admonition (lines 38-58) that clearly:
- Shows a table of agent types with IB support status
- Explains that Channel Agents do NOT inherit barrier policies
- Lists compensating controls
- Includes testing guidance

**Remaining work:** Verify this is sufficient. May already be complete from a previous phase. Check if any solution docs need to reference this limitation.

## Regulatory Alignment Verification Issues Found

### Deny Event Correlation Report - FINRA 25-07 Citation Error

**Confidence:** HIGH

The deny-event-correlation-report README.md (line 24) lists "FINRA 25-07 - AI governance evidence" in its regulatory alignment section. However, per the framework's own `regulatory-mappings.md`, FINRA Regulatory Notice 25-07 addresses **workplace modernization rules**, not AI governance. The correct references for AI governance are:
- FINRA Regulatory Notice **24-09** (Gen AI guidance)
- FINRA **2026 Annual Regulatory Oversight Report** (GenAI examination priorities)

This is an inaccuracy that needs correction as part of the regulatory alignment verification.

### Other Regulatory Claims to Verify

Each of the 9 newer solutions claims regulatory alignment that needs cross-referencing against `regulatory-mappings.md`:

| Solution | Claims | Verification Needed |
|----------|--------|---------------------|
| FINRA Supervision | FINRA 3110, 3120, 24-09, SEC 17a-3, 17a-4 | Cross-check control mappings |
| Conditional Access | NIST 800-53, SOX 404, GLBA 501(b) | Verify CA maps to these regs |
| Compliance Dashboard | SOX 404, FINRA 3120, OCC 2011-12 | Verify reporting control mappings |
| Segregation Detector | SOX 404, COSO, OCC Heightened Standards | Verify SoD control mappings |
| Scope Drift Monitor | GDPR 5(1)(c), GLBA 501(b), CCPA | Verify data minimization mappings |
| RAG Source Validator | SEC 17a-4, FINRA 4511, SOX 404 | Verify integrity control mappings |
| COI Testing | FINRA 2111, 2010, 2210, SEC Reg BI | Verify COI control mappings |
| Hallucination Tracker | FINRA 2210, SEC Marketing Rule, CFPB | Verify accuracy control mappings |
| DR Testing | OCC Heightened Standards, FFIEC BCP, SEC 17a-4, FINRA 4370 | Verify BC/DR mappings |

## Architecture Patterns

### Audit Checklist Pattern (Recommended)

Each solution should be audited against a consistent checklist:

```
1. README.md Review
   - [ ] Version number accurate
   - [ ] Description matches actual functionality
   - [ ] Prerequisites complete and accurate
   - [ ] Quick Start steps testable (documentation review only)
   - [ ] Regulatory alignment claims verified against regulatory-mappings.md
   - [ ] Related Controls links valid
   - [ ] Status badge present (to be added)

2. Script/Code Review
   - [ ] All referenced scripts exist on disk
   - [ ] Scripts have appropriate headers/documentation
   - [ ] No deprecated API usage (or properly warned)
   - [ ] Authentication methods current (Entra ID, not x-api-key)
   - [ ] Error handling present

3. Documentation Review
   - [ ] All docs/ referenced files exist
   - [ ] Internal links valid
   - [ ] Dataverse schema documented (if applicable)
   - [ ] Flow configuration documented (if applicable)
   - [ ] Troubleshooting guide exists

4. Framework Alignment
   - [ ] Control mappings accurate (solution -> controls)
   - [ ] Solution referenced in mapped control documents
   - [ ] Zone applicability documented
   - [ ] Regulatory claims match framework regulatory-mappings.md

5. Status Classification
   - [ ] Status proposed with evidence rationale
   - [ ] Status consistent with actual maturity
```

### Status Classification Methodology (Recommended)

Based on the CONTEXT.md status labels:

| Status | Evidence Required |
|--------|-------------------|
| **Planned** | README exists; scripts may be stubs or minimal; docs may be incomplete; solution describes what WILL be built |
| **Work In Progress** | README complete; some scripts functional; core documentation present; not all features implemented |
| **Validated** | README complete; scripts functional (documentation review confirms); all docs present; regulatory claims verified |
| **Completed** | All of Validated + CHANGELOG shows iterative versions; comprehensive documentation; production-tested patterns |

**Preliminary Status Estimates (subject to audit confirmation):**

| Solution | Estimated Status | Rationale |
|----------|-----------------|-----------|
| Environment Lifecycle Management | Completed | v1.1.2, 9 scripts, 7 docs, iterative versions |
| Message Center Monitor | Completed | v2.1.1, extensive docs, iterative versions |
| Pipeline Governance Cleanup | Completed | v1.0.8, 2 scripts, 7 docs, samples |
| Deny Event Correlation Report | Validated* | v1.1.0, 4 scripts, but x-api-key deprecation pending |
| FINRA Supervision Workflow | Validated | v1.0.0, 2 scripts, 7 docs, comprehensive README |
| Conditional Access Automation | Validated | v1.0.0, 3 scripts, 8 templates, 5 docs |
| Compliance Dashboard | Work In Progress | v1.0.0-beta explicitly, Power BI manual |
| Segregation Detector | Validated | v1.0.0, 2 scripts, 4 docs |
| Scope Drift Monitor | Work In Progress | v1.0.0, 1 script, 2 docs, missing referenced docs |
| RAG Source Validator | Work In Progress | v1.0.0, 1 script, 1 doc, missing referenced docs |
| COI Testing | Planned | v1.0.0, 1 script, 0 detailed docs on disk |
| Hallucination Tracker | Planned | v1.0.0, 1 script, 0 detailed docs on disk |
| DR Testing Framework | Planned | v1.0.0, 1 script, 0 detailed docs on disk |

*Note: These are estimates based on file counts. The actual audit must read file contents to confirm quality and accuracy.

### Badge Format for README Status (Recommended)

```markdown
<!-- At top of each README.md, after title -->
![Status: Completed](https://img.shields.io/badge/Status-Completed-brightgreen)
![Status: Validated](https://img.shields.io/badge/Status-Validated-green)
![Status: Work%20In%20Progress](https://img.shields.io/badge/Status-Work%20In%20Progress-yellow)
![Status: Planned](https://img.shields.io/badge/Status-Planned-lightgrey)
```

Alternative (simpler, no external dependency):
```markdown
> **Status:** Completed | Validated | Work In Progress | Planned
```

**Recommendation:** Use the simpler text-based badge (no external image service dependency). This keeps the solutions repo self-contained and avoids broken images in air-gapped environments (common in FSI).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Status badge rendering | Custom HTML/CSS | Simple markdown `> **Status:** X` format | Avoids external dependencies, works offline |
| Regulatory mapping verification | Manual cross-reference | Systematic comparison against regulatory-mappings.md | The framework already has canonical mappings |
| Control link generation | Manual URL construction | Copy patterns from existing control references | Consistency with established link format |

## Common Pitfalls

### Pitfall 1: Referenced Documentation That Does Not Exist

**What goes wrong:** Solution READMEs reference docs/ files in tables and links that may not actually exist on disk. This creates misleading documentation.
**Why it happens:** READMEs were written with planned documentation in mind, but the docs were not all created.
**How to avoid:** For each solution, verify every referenced file path exists. If it does not, either create it or remove the reference.
**Warning signs:** README lists `[docs/troubleshooting.md](docs/troubleshooting.md)` but file is missing.

### Pitfall 2: Outdated Version Numbers in Framework Docs

**What goes wrong:** The solutions-integration.md "Repository Structure" code block shows old version numbers (ELM v1.0.1, MCM v2.0.0, DEC v1.0.0) that don't match current versions.
**Why it happens:** The integration doc was written when fewer solutions existed and versions were lower.
**How to avoid:** Update all version references when touching these files.

### Pitfall 3: Inconsistent Control Number References

**What goes wrong:** Solution READMEs link to controls using slightly different URL paths than the actual filenames.
**Why it happens:** Control filenames include descriptive slugs that may not be consistently referenced.
**How to avoid:** Verify every control link resolves. Use the `CONTROL-INDEX.md` as the source of truth for filenames.

### Pitfall 4: Confusing "FINRA 25-07" with AI Governance

**What goes wrong:** The deny-event-correlation-report cites "FINRA 25-07" as AI governance evidence, but 25-07 is about workplace modernization.
**Why it happens:** Easy to confuse FINRA notice numbers; 24-09 is the AI-relevant notice.
**How to avoid:** Cross-check every FINRA notice number against the regulatory-mappings.md.

### Pitfall 5: Updating One Repository but Not the Other

**What goes wrong:** A fix is applied in FSI-AgentGov-Solutions but the corresponding framework doc in FSI-AgentGov is not updated (or vice versa).
**Why it happens:** Two separate git repositories with separate commit histories.
**How to avoid:** Per CONTEXT.md decision, TECH fixes must be applied in BOTH repositories. Each plan should explicitly list files in both repos.

## Recommended Plan Structure

Based on the scope (13 solutions + 5 TECH items + 2 framework docs), recommend splitting into 4-5 plans:

### Option A: By Solution Maturity Tier (Recommended)

| Plan | Scope | Estimated Size |
|------|-------|---------------|
| **Plan 1** | Audit 4 Tier-A solutions (ELM, MCM, PGC, DEC) + TECH-03 (PAYG in 2.1, relates to ELM) | Medium |
| **Plan 2** | Audit 5 Tier-B solutions with deeper docs (FINRA, CAA, Compliance, SoD, Scope Drift) | Large |
| **Plan 3** | Audit 4 Tier-B solutions with minimal docs (RAG, COI, Hallucination, DR) + keep/cut recommendations | Medium |
| **Plan 4** | TECH-04, TECH-05, TECH-06, TECH-07 resolution across both repos | Medium |
| **Plan 5** | Framework doc updates: solutions-integration.md expansion + solutions-index.md status column + control cross-references | Large |

### Option B: By Work Type

| Plan | Scope |
|------|-------|
| **Plan 1** | Audit all 13 solutions (findings report) |
| **Plan 2** | Apply fixes from audit findings (solution docs) |
| **Plan 3** | TECH debt resolution (both repos) |
| **Plan 4** | Framework documentation updates |

**Recommendation:** Option A is better because it produces actionable fixes alongside audit findings, reducing back-and-forth. Each plan both audits AND fixes within its scope.

## Cross-Repository File Map

### Files in FSI-AgentGov to Update

| File | Update Type |
|------|-------------|
| `docs/framework/solutions-integration.md` | Expand from 4 to 13 solutions |
| `docs/reference/solutions-index.md` | Add status column, fix version numbers |
| Control docs where solutions map (17+ controls) | Add solution references |
| TECH-03 related files (2.1 and playbooks) | Verify PAYG warning completeness |
| TECH-04 related controls (1.11, 1.4, 2.8) | Add Service Principal warning |
| TECH-05 related files (1.5 and playbooks) | Verify DLP enforcement clarity |
| TECH-06 related files (1.8 and playbooks) | Verify Defender two-portal completeness |
| TECH-07 related files (1.22) | Verify IB limitation completeness |

### Files in FSI-AgentGov-Solutions to Update

| File | Update Type |
|------|-------------|
| All 13 `README.md` files | Add status badge |
| `deny-event-correlation-report/README.md` | Fix FINRA 25-07 -> 24-09 |
| `deny-event-correlation-report/scripts/Export-RaiTelemetry.ps1` | Migrate from x-api-key to Entra ID auth |
| Solutions with TECH-04 relevance | Add SP bypass warning |
| Solutions referencing Defender | Verify two-portal guidance |
| Root `README.md` | Consider adding status column |

## Solution-to-Control Mapping (Complete)

This maps all 13 solutions to their declared controls, for use in adding cross-references:

| Solution | Primary Control | Secondary Controls |
|----------|----------------|-------------------|
| Environment Lifecycle Management | 2.1 | 2.2, 2.15 |
| Message Center Monitor | 2.3 | 2.10 |
| Pipeline Governance Cleanup | 2.3 | 2.1 |
| Deny Event Correlation Report | 1.5 | 1.7, 3.4 |
| FINRA Supervision Workflow | 2.12 | 1.10, 1.7 |
| Conditional Access Automation | 1.11 | 1.23, 1.18 |
| Compliance Dashboard | 3.3 | 3.1, 3.2 |
| Segregation Detector | 2.8 | 2.1, 2.3 |
| Scope Drift Monitor | 1.14 | 1.4, 1.5 |
| RAG Source Validator | 2.16 | 1.7, 2.13 |
| COI Testing | 2.18 | 2.11, 2.5 |
| Hallucination Tracker | 3.10 | 2.9, 2.12 |
| DR Testing Framework | 2.4 | 2.1, 1.9 |

**Unique controls touched:** 17 controls across all 4 pillars (1.4, 1.5, 1.7, 1.9, 1.10, 1.11, 1.14, 1.18, 1.23, 2.1, 2.2, 2.3, 2.4, 2.5, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.15, 2.16, 2.18, 3.1, 3.2, 3.3, 3.4, 3.10)

**Controls to add solution references to:** Each of these ~27 controls should receive a reference to its mapped solution(s). Format per CONTEXT.md: "See [Solution Name] for automated implementation."

## Open Questions

1. **Missing docs verification:** Several newer solutions reference doc files that may not exist on disk. The audit must verify each referenced file. This research identified the risk from file listings but did not read every referenced doc to confirm existence.

2. **Script functionality depth:** The CONTEXT.md says "treat solutions as documentation artifacts, not code" but also says "update scripts that reference deprecated APIs." The audit should read script contents for deprecated API patterns beyond just the known x-api-key issue in DEC.

3. **Keep/cut recommendations:** The CONTEXT.md asks Claude to produce keep/cut recommendations for Planned solutions. The research identified COI Testing, Hallucination Tracker, and DR Testing Framework as potentially "Planned" status. The actual audit must examine whether these provide unique value or overlap with other solutions.

4. **TECH-03 completeness:** Control 2.1 already has the PAYG warning. Need to confirm whether this TECH item is already resolved or if there are other files still propagating the misconception.

5. **TECH-06 completeness:** Phase 4 already addressed Defender two-portal configuration. Need to confirm whether this TECH item was fully resolved in Phase 4 or if gaps remain.

## Sources

### Primary (HIGH confidence)
- Direct file reads of all 13 solution READMEs in FSI-AgentGov-Solutions
- Direct file reads of solutions-index.md and solutions-integration.md in FSI-AgentGov
- Direct file reads of Control 2.1 (TECH-03), Control 1.5 (TECH-05), Control 1.22 (TECH-07), Control 1.8 (TECH-06)
- Grep searches across both repositories for TECH item patterns
- File listing of all solution directories (complete file inventory)
- FSI-AgentGov-Solutions CHANGELOG.md (release history)
- FSI-AgentGov regulatory-mappings.md (canonical regulatory references)

### Secondary (MEDIUM confidence)
- Planning documents: REQUIREMENTS.md, STATE.md, ROADMAP.md for TECH item context
- PITFALLS.md for Defender integration context

### Tertiary (LOW confidence)
- Preliminary status estimates based on file counts (need content review to confirm)

## Metadata

**Confidence breakdown:**
- Current state assessment: HIGH - based on direct file reads of all solution READMEs and file listings
- TECH item mapping: HIGH - based on grep searches and file reads of affected controls
- Regulatory alignment issues: HIGH - identified by cross-referencing solution claims against regulatory-mappings.md
- Status estimates: MEDIUM - based on file counts, not content quality review
- Plan structure recommendation: MEDIUM - reasonable but depends on user preference

**Research date:** 2026-02-03
**Valid until:** 2026-03-03 (30 days - stable domain, no external dependencies)
