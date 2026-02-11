# Requirements: Technical Remediation (v11)

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| RTF | Runtime Fixes | 10 |
| RTA | Regulatory & Technical Accuracy | 10 |
| TVN | Terminology & Version Normalization | 6 |
| XRL | Cross-Reference & Link Integrity | 6 |
| SCF | Script & Code Fixes | 6 |
| GBD | Gap Backfill & Design Improvements | 8 |
| **Total** | | **38** (+ 8 advisory) |

> Advisory requirements (GBD) are subject to scope refinement during Phase 6 planning.

## RTF — Runtime Fixes

- [ ] **RTF-01:** Fix `fsi_result_json` column name mismatch between CAA flow JSON and Dataverse schema script
- [ ] **RTF-02:** Add 6 missing Dataverse columns (`fsi_policy_display_name`, `fsi_evaluation_id`, `fsi_grant_controls`, `fsi_session_controls`, `fsi_conditions_summary`, `fsi_last_modified_date`) to create_dataverse_schema.py
- [ ] **RTF-03:** Fix documentation URL slug from `conditional-access-automation` to `conditional-access-assessment` in 3 CAA artifacts (2 flows + deploy.py)
- [ ] **RTF-04:** Create 3 missing private helper scripts referenced by CAA module manifest: `Get-CAPolicyRiskScore.ps1`, `Format-ComplianceReport.ps1`, `Test-CAAPrerequisites.ps1`
- [ ] **RTF-05:** Align Conditional Access policy naming convention to `FSI-*` prefix across validation scripts and playbook templates
- [ ] **RTF-06:** Fix DEC severity option set mismatch — correlation engine outputs must match Dataverse schema option set values
- [ ] **RTF-07:** Fix DEC zone option set values — extraction scripts must use schema-defined values (not string labels)
- [ ] **RTF-08:** Rewrite DEC deployment guide to describe v2.0 Dataverse architecture (remove references to CSV/Blob storage from v1.x)
- [ ] **RTF-09:** Update DEC Power BI playbook to use Dataverse connector (remove CSV file source instructions)
- [ ] **RTF-10:** Fix hardcoded zone value (`'1'`) in DEC extraction scripts — derive from agent metadata dynamically

## RTA — Regulatory & Technical Accuracy

- [ ] **RTA-01:** Fix Pillar 1 control count from "23" to "24" and total from "61" to "62" in executive-summary.md, governance-fundamentals.md, and index pages
- [ ] **RTA-02:** Audit all FINRA 25-07 references — verify citation accuracy (Notice vs Rule), update effective dates, confirm applicability statements
- [ ] **RTA-03:** Fix SEC 17a-3/4 retention period language — distinguish 3-year communications preservation from 6-year books/records retention
- [ ] **RTA-04:** Resolve Zone 3 retention period conflict — standardize on 7 years or 10 years across all framework, control, and playbook references
- [ ] **RTA-05:** Fix solution count inconsistencies (13 vs 19), correct CFTC 1.31 applicability scope in regulatory-framework.md
- [ ] **RTA-06:** Fix ELM Lab 3: remove SecurityGroupId at creation time instruction; collect zone rationale for Zone 2 (not just Zone 3)
- [ ] **RTA-07:** Fix ELM Lab 5: replace non-existent `Get-CrmRolePrivilege` cmdlet with working alternative or pseudocode annotation
- [ ] **RTA-08:** Fix PCG Lab 3: change "Add a new row" to upsert pattern; fix state-setting to use option set value; add pagination for >100 items
- [ ] **RTA-09:** Replace all "Azure AD" references with "Microsoft Entra ID" in PCG playbooks and related docs
- [ ] **RTA-10:** Fix DEC documentation: correct Dataverse column name prefixes (`fsi_` consistency), fix table count, correct module name references

## TVN — Terminology & Version Normalization

- [ ] **TVN-01:** Standardize governance zone terminology — all playbooks use "Zone 1/2/3" (replace "Tier" or "Level" variants, or add explicit mapping note)
- [ ] **TVN-02:** Normalize admin role names to role-catalog.md canonical forms across all playbooks (e.g., "Global Administrator" → "Entra Global Admin")
- [ ] **TVN-03:** Add Zone/Tier/Level equivalence mapping note to zones-and-tiers.md for backward compatibility
- [ ] **TVN-04:** Align all document footer version strings to current framework version (v1.2.38)
- [ ] **TVN-05:** Add missing glossary entries: Agent 365 Architecture, Entra Agent ID, Blueprint, Sponsor, DSPM
- [ ] **TVN-06:** Fix framework document count in index.md; correct ELM footer version discrepancies

## XRL — Cross-Reference & Link Integrity

- [ ] **XRL-01:** Add CAA solution reference to Controls 1.23 (Conditional Access Policies) and 1.18 (Security Baseline) Implementation Guides sections
- [ ] **XRL-02:** Add Control 1.8 (Agent Threat Protection) to DEC coverage in solutions-coverage-gaps.md
- [ ] **XRL-03:** Add Agent Activity Monitor (AAM) and Federated User Sync (FUS) solutions to solutions-coverage-gaps.md
- [ ] **XRL-04:** Fix evidence-pack-assembly.md file paths — update to match actual repository locations
- [ ] **XRL-05:** Replace legacy "Gap N" placeholder references with actual playbook or control document names
- [ ] **XRL-06:** Fix ELM environment group naming inconsistency between provisioning playbook and Control 2.2; fix solutions-index.md version numbers

## SCF — Script & Code Fixes

- [ ] **SCF-01:** Fix `$isBlock` variable scoping bug in `scripts/Test-PolicyCompliance.ps1` — ensure value persists across pipeline stages
- [ ] **SCF-02:** Fix CAA module manifest (`conditional-access-automation.psd1`) — remove exports for non-existent functions, or create the functions
- [ ] **SCF-03:** Fix Control 4.7 PowerShell playbook SKU filter — use `SkuPartNumber` string match instead of `SkuId` regex
- [ ] **SCF-04:** Mark non-existent cmdlets in ELM promotion gate scripts as pseudocode (with `# PSEUDOCODE` annotation) or replace with working alternatives
- [ ] **SCF-05:** Align cross-solution integration parameter names — standardize on `SolutionId` vs `Solution` across all integration scripts
- [ ] **SCF-06:** Add `Search-UnifiedAuditLog` pagination warnings to audit query playbooks (5000-result limit, session-based paging)

## GBD — Gap Backfill & Design Improvements (Advisory)

- [ ] **GBD-01:** Create CAA end-to-end deployment guide (prerequisites → Dataverse setup → flow import → validation → monitoring)
- [ ] **GBD-02:** Document ELM approval flow implementation (Power Automate approval workflow for environment requests)
- [ ] **GBD-03:** Add parent control caveats to Pillar 4 portal walkthroughs (reindexing delays, EEEU impact, discovery amplification risks)
- [ ] **GBD-04:** Add DSPM policy pack portal deployment steps to security playbooks
- [ ] **GBD-05:** Interlink spec-level playbooks (confidence thresholds ↔ human-in-the-loop ↔ explainability) with cross-references
- [ ] **GBD-06:** Add FAQ timeline reconciliation note explaining 30/60/90 day variations across framework documents
- [ ] **GBD-07:** Fix footnote markers in governance-operations playbooks (broken `[^1]` references)
- [ ] **GBD-08:** Remove emoji characters from quick-start.md per FSI documentation style guidelines (optional/low priority)

## Out of Scope

| Item | Reason |
|------|--------|
| New solution development | Companion repo (FSI-AgentGov-Solutions) |
| Companion repo code fixes | Separate repository, separate milestone |
| Excel template updates | Covered by verify_excel_templates.py, no audit findings |
| MkDocs theme/plugin changes | No audit findings related to theme |
| New control authoring | v11 is remediation-only, no new controls |
| Screenshot verification | Local-only workflow, no doc changes needed |

---
*Requirements defined: 2026-02-10*
*Audit source: 8-subagent parallel technical review (107 findings, 42 gaps)*
*Traceability: All 38 requirements map to ROADMAP.md phases — see Coverage table*
