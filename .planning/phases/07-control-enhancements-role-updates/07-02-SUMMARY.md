---
phase: 07
plan: 02
subsystem: pillar-1-security
tags:
  - dspm-ai-observability
  - unified-dspm
  - control-enhancement
  - microsoft-purview
  - preview-feature
dependency-graph:
  requires:
    - 06-01-agent-365-documentation
  provides:
    - enhanced-dspm-ai-observability-documentation
    - unified-dspm-experience-guidance
    - agent-risk-observability-configuration
  affects:
    - future-dspm-unified-ga-updates
tech-stack:
  added: []
  patterns:
    - unified-dspm-experience-preview-documentation
    - prepare-now-migration-readiness
key-files:
  created: []
  modified:
    - docs/controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md
    - docs/playbooks/control-implementations/1.6/portal-walkthrough.md
    - docs/playbooks/control-implementations/1.6/powershell-setup.md
    - docs/playbooks/control-implementations/1.6/verification-testing.md
    - docs/playbooks/control-implementations/1.6/troubleshooting.md
decisions:
  - id: unified-dspm-preview-documentation
    choice: Document unified DSPM experience as preview with June 2026 GA timeline
    rationale: MC1191257 Message Center announcement confirms rollout; users need preparation guidance now
  - id: prepare-now-checklist-pattern
    choice: Provide pre-GA preparation steps following Phase 6 Agent 365 migration pattern
    rationale: Organizations can prepare baseline before unified experience migration
  - id: agent-risk-observability-framing
    choice: Frame as enhanced capabilities within unified DSPM, not standalone feature
    rationale: Research shows agent risk observability is dashboard/reporting enhancement within unified experience
  - id: powershell-api-manual-export
    choice: Document manual portal export for agent risk data until PowerShell API available at GA
    rationale: Preview unified DSPM lacks PowerShell cmdlets for agent risk; avoid setting false expectations
metrics:
  duration: 342 seconds (5.7 minutes)
  completed: 2026-02-06
---

# Phase 7 Plan 02: Enhanced DSPM AI Observability Documentation Summary

**One-liner:** Added comprehensive unified DSPM experience documentation with agent risk observability, enhanced Activity Explorer, and prepare-now migration guidance for June 2026 GA

## What Was Delivered

Enhanced Control 1.6 (Microsoft Purview DSPM for AI) with comprehensive documentation of the unified DSPM experience (preview) and updated all four playbooks with configuration, automation, verification, and troubleshooting content for enhanced DSPM AI Observability capabilities.

### Enhanced Control 1.6 - DSPM AI Observability

**New "Enhanced DSPM AI Observability" subsection added:**

- **Preview status clearly marked:** MC1191257 Message Center reference for June 2026 GA timeline
- **Capabilities comparison table:** Classic DSPM for AI vs. Unified DSPM Experience across 5 dimensions (Agent Risk Dashboards, Activity Explorer, Data Classification Visibility, Dashboard Experience, Remediation Workflows)
- **FSI benefit mapping:** Each capability mapped to regulatory requirement (FINRA 3110, SEC AI priorities, OCC 2011-12, GLBA 501(b), SOX 302)
- **Prepare Now checklist:** 6 pre-GA preparation steps organizations can take today (verify DSPM for AI configuration, remediate current findings, document Activity Explorer filters, enable extended insights, prepare for unified dashboard migration, review reporting cadence)
- **Regulatory mapping:** Enhanced capabilities help support FINRA 3110 supervision, SEC AI priorities transparency, OCC 2011-12 model risk management
- **Roles updated:** Added AI Administrator (delegated DSPM settings management) and Entra Security Admin (Defender XDR integration with DSPM observability data)
- **Key Configuration Points updated:** Added unified DSPM experience GA migration monitoring

**Cross-references added:**
- Weekly Risk Assessments table updated to reference Enhanced DSPM AI Observability subsection

### Playbook Updates

**Portal Walkthrough (portal-walkthrough.md):**

- **New "Enhanced DSPM AI Observability (Preview)" section** with preview UI warning
- **Unified DSPM access:** Portal navigation for preview-enabled vs. classic tenants
- **Agent Risk Observability Dashboard:** Configuration steps for per-agent risk scoring (High/Medium/Low), contributing factors review, export procedures
- **Enhanced Activity Explorer:** Multi-agent selection, data classification filters, access pattern filtering, policy violation filtering, advanced search with operators (AND, OR, NOT), enhanced CSV export with additional metadata
- **Unified Dashboard Configuration:** Integrated dashboard widgets, email notifications (daily for Zone 3, weekly for Zone 2, monthly for Zone 1)
- **Data Classification Insights:** Real-time labeled vs. unlabeled data access monitoring, label mismatch alerts, classification reporting
- **Zone-specific guidance:** Zone 1 (monthly review), Zone 2 (weekly dashboard + agent risk digest), Zone 3 (daily review + real-time alerts + daily exports)

**PowerShell Setup (powershell-setup.md):**

- **Enhanced Activity Explorer data export script:** RecordType filtering for AI events, enhanced metadata parsing (RiskScore, AccessPattern - preview fields)
- **Weekly DSPM summary report generator:** Automated HTML report combining Activity Explorer summary, policy violations, event counts
- **Agent risk data export guidance:** Manual portal export documented (PowerShell API not yet available in preview), import and processing script for high-risk agent notifications
- **Preview cmdlet warning admonition:** Clear notice that PowerShell syntax may change at GA

**Verification Testing (verification-testing.md):**

- **DSPM-01: Unified DSPM experience accessibility test**
  - Objective: Confirm preview ring access or classic DSPM availability
  - Expected outcomes for both preview-enabled and non-preview tenants
  - Evidence: Navigation screenshots, tenant preview ring status documentation
- **DSPM-02: Agent risk observability data verification test**
  - Objective: Verify agent risk dashboards populating with risk scores
  - Test steps: Review contributing factors, export agent risk summary CSV
  - Expected outcomes: Risk scores with baseline data, "Insufficient Data" handling for new agents
  - Evidence: Agent risk dashboard screenshots, contributing factors screenshots, CSV export
- **DSPM-03: Activity Explorer enhanced filters test**
  - Objective: Confirm multi-agent selection, data classification filters, advanced search functionality
  - Test steps: Multi-agent filter, sensitivity label filter, advanced search with operators, enhanced CSV export comparison
  - Expected outcomes: Enhanced filters functional, additional metadata columns in CSV export
  - Evidence: Filter screenshots, advanced search screenshots, enhanced vs classic CSV comparison

**Troubleshooting (troubleshooting.md):**

- **"Unified DSPM experience not visible" entry:**
  - Solutions: Verify tenant preview ring enrollment, check MC1191257 Message Center, complete Get Started wizard, verify licensing, clear browser cache
  - Workaround: Use classic DSPM for AI until unified experience available
- **"Agent risk data not populating" entry:**
  - Solutions: Verify Application Insights integration, check Observability SDK configuration (Agent 365 SDK agents), verify 7-14 day activity baseline, check data latency (weekly updates), verify DSPM Get Started completion
  - Workaround: Use Activity Explorer enhanced filters for manual high-risk pattern identification
- **"Activity Explorer missing AI events" entry:**
  - Solutions: Verify audit logging enabled, check Activity Explorer filters, verify audit retention policy, check agent activity type, verify user/agent in scope
  - Workaround: Export audit log via PowerShell `Search-UnifiedAuditLog` for manual filtering

## Task Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | 96a4ded | feat(07-02): add Enhanced DSPM AI Observability to Control 1.6 |
| 2 | 49554bb | feat(07-02): update Control 1.6 playbooks for DSPM AI Observability |

## Decisions Made

### 1. Unified DSPM Preview Documentation Strategy

**Decision:** Document unified DSPM experience as preview with explicit June 2026 GA timeline and prepare-now guidance

**Rationale:**
- MC1191257 Message Center announcement confirms unified DSPM rollout (April-May 2026 staged rollout, June 2026 GA expected)
- Organizations need preparation guidance NOW to establish baselines before migration
- Preview admonitions clearly mark feature status and set expectations for GA changes

**Impact:** Users understand what's coming, can prepare today, won't be surprised by unified experience migration at GA

### 2. Prepare Now Checklist Pattern

**Decision:** Provide 6 pre-GA preparation steps following Phase 6 Agent 365 "prepare now, migrate later" pattern

**Rationale:**
- Phase 6 Agent 365 migration roadmap pattern was well-received (actionable pre-GA steps)
- FSI organizations prefer proactive preparation over reactive scrambling
- Baseline establishment (remediating current findings, documenting filters) reduces migration disruption

**Impact:** Organizations can establish clean DSPM baseline, document current workflows, and prepare for seamless unified experience migration

### 3. Agent Risk Observability Framing

**Decision:** Frame Enhanced DSPM AI Observability as collection of capabilities within unified DSPM, not standalone feature

**Rationale:**
- Research confirmed "AI Observability" is marketing term for dashboards/reporting within unified DSPM
- Framing as "Enhanced DSPM AI Observability capabilities" sets accurate expectations
- Capabilities comparison table (Classic vs Unified) shows incremental enhancement, not net-new feature

**Impact:** Users understand unified DSPM as evolution of current DSPM for AI, not separate product/licensing requirement

### 4. PowerShell API Manual Export Documentation

**Decision:** Document manual portal export for agent risk data; PowerShell cmdlet support deferred until GA

**Rationale:**
- Preview unified DSPM lacks PowerShell API for agent risk observability
- Setting expectation that automation comes at GA prevents user frustration
- Manual export workflow documented as interim approach

**Impact:** Users have working process today (manual export + PowerShell processing), know to watch for GA PowerShell API release

### 5. Zone-Specific Configuration Depth

**Decision:** Provide granular zone-specific guidance (Zone 1: monthly, Zone 2: weekly, Zone 3: daily + real-time)

**Rationale:**
- Enhanced observability creates monitoring overhead; zone-specific cadence balances risk vs. burden
- Zone 3 enterprises need real-time alerting; Zone 1 personal agents don't justify daily review
- Aligns with existing framework zone pattern (escalating rigor for escalating risk)

**Impact:** Organizations can right-size monitoring effort; Zone 3 gets enterprise-grade alerting without burdening Zone 1/2

## Deviations from Plan

None — plan executed exactly as written.

## Challenges Encountered

### Challenge 1: Unified DSPM Preview Ring Availability Uncertainty

**Issue:** Research could not confirm which tenants have preview access; gradual rollout means test cases may not be applicable for all users

**Resolution:**
- Added "Preview Ring Enrollment Required" admonition in portal walkthrough
- Test case DSPM-01 explicitly verifies preview vs. classic access
- Expected outcomes documented for both preview-enabled and non-preview tenants
- Troubleshooting entry for "unified DSPM not visible" guides users on checking preview status

**Outcome:** Documentation works for both preview and non-preview tenants without confusion

### Challenge 2: PowerShell Cmdlets Not Yet Available in Preview

**Issue:** Unified DSPM preview lacks PowerShell API for agent risk observability, limiting automation capabilities

**Resolution:**
- Documented manual portal export workflow as interim approach
- Added PowerShell import/processing script for manual exports
- Preview cmdlet warning admonition set expectation that automation comes at GA
- Weekly summary report script includes placeholder comment for future PowerShell API

**Outcome:** Users have working process today, clear expectation that full automation arrives at GA

### Challenge 3: Agent Risk Scoring Baseline Requirements

**Issue:** Agent risk observability requires 7-14 days of activity to establish baseline; new agents show "Insufficient Data"

**Resolution:**
- Test case DSPM-02 expected outcomes include "Insufficient Data" handling
- Troubleshooting entry documents 7-14 day baseline requirement
- Portal walkthrough notes new agents may not have risk scores immediately
- Verification testing evidence collection allows for "baseline pending" status

**Outcome:** Users understand why new agents lack risk scores, know to wait 1-2 weeks for baseline establishment

## Next Phase Readiness

**Phase 7 Plan 03 (Control 3.8 AI Feature Access Control):**
- Ready to proceed — no blockers
- Control 3.8 enhancement independent of DSPM unified experience
- AI Feature Access Control is GA (M365 Admin Center Copilot settings), no preview dependencies

**FSI-AgentGov-Solutions Repository:**
- No impact — Phase 7 is documentation-only (no solution deployments)

**Learn Monitor Impact:**
- New Microsoft Learn URLs to add:
  - Unified DSPM experience documentation (when published)
  - Agent risk observability guidance (when published)
  - Enhanced Activity Explorer documentation (when published)
- Monitor MC1191257 for GA announcement and updated Learn documentation links

**Outstanding Items:**
- None for this plan

## Self-Check: PASSED

All files created and all commits verified:

**Files Modified:**
- ✅ docs/controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md (exists)
- ✅ docs/playbooks/control-implementations/1.6/portal-walkthrough.md (exists)
- ✅ docs/playbooks/control-implementations/1.6/powershell-setup.md (exists)
- ✅ docs/playbooks/control-implementations/1.6/verification-testing.md (exists)
- ✅ docs/playbooks/control-implementations/1.6/troubleshooting.md (exists)

**Commits:**
- ✅ 96a4ded: feat(07-02): add Enhanced DSPM AI Observability to Control 1.6
- ✅ 49554bb: feat(07-02): update Control 1.6 playbooks for DSPM AI Observability

**Build Validation:**
- ✅ mkdocs build --strict passes with zero errors
