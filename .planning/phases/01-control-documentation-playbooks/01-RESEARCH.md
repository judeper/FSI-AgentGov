# Phase 1 Research: Control Documentation & Playbooks

## Phase Goal

Create Control 1.25 (MIME Type Restrictions for File Uploads) documentation following the 10-section template, 4 implementation playbooks, and screenshot specification.

## Requirements Covered

- **CTL-01:** Control 1.25 documentation (10-section template)
- **CTL-02:** 4 playbooks (portal-walkthrough, powershell-setup, verification-testing, troubleshooting)
- **CTL-03:** Screenshot specification (EXPECTED.md)

## Technical Analysis

### Control Template Structure (from `docs/templates/control-setup-template.md`)

**Header metadata (5 fields):**
- Control ID, Pillar, Regulatory Reference, Last UI Verified, Governance Levels

**10 mandatory sections:**

| # | Section | Content Pattern |
|---|---------|-----------------|
| 1 | Objective | Single paragraph, concise purpose |
| 2 | Why This Matters for FSI | Bulleted list: `**[Regulation]:** [Hedged description]` |
| 3 | Control Description | Multi-paragraph technical; may include tables, sub-headings |
| 4 | Key Configuration Points | Bulleted list of specific settings |
| 5 | Zone-Specific Requirements | 3-row table: Zone 1/2/3 with Requirement and Rationale |
| 6 | Roles & Responsibilities | 2-column table: Role / Responsibility |
| 7 | Related Controls | 2-column table: Control (relative link) / Relationship |
| 8 | Implementation Playbooks | Info admonition with 4 playbook links |
| 9 | Verification Criteria | Numbered checklist (5-6 items) |
| 10 | Additional Resources | Bulleted Microsoft Learn links |

**Footer metadata:**
```
*Updated: [Month Year] | Version: v[X.X] | UI Verification Status: [Current/Needs Review]*
```

**Exemplar enrichments (from Control 1.24):**
- Extra `**Last Verified:**` field after Governance Levels
- `!!! note "Agent 365 Architecture Update"` admonition after header
- `!!! tip` admonition referencing complementary controls
- Rich control description with comparison tables

### Playbook Structure Patterns

**Portal Walkthrough:**
- Title: `# Portal Walkthrough: Control X.X - [Name]`
- Metadata: Last Updated, Portal, Estimated Time
- Prerequisites: Checkbox list
- Body: Numbered `### Step N:` sections with portal paths
- Governance table by zone; validation checklist; footer nav

**PowerShell Setup:**
- Title: `# PowerShell Setup: Control X.X - [Name]`
- Metadata: Last Updated, Modules Required
- Prerequisites: Install-Module commands
- Scripts with comment-based help (.SYNOPSIS, .EXAMPLE)
- Validation script with [PASS]/[FAIL]/[INFO] pattern
- Complete configuration script with param() and try/catch/finally
- Footer nav

**Verification & Testing:**
- Title: `# Verification & Testing: Control X.X - [Name]`
- Manual verification: `### Test N:` with `**EXPECTED:**`
- Test cases table (TC-X.X-NN format)
- Evidence collection checklist, attestation template
- Zone-specific testing requirements table
- KQL queries for automated evidence
- Footer nav

**Troubleshooting:**
- Title: `# Troubleshooting: Control X.X - [Name]`
- Common issues summary table (Issue / Cause / Resolution)
- Detailed `### Issue:` sections with Symptoms, Resolution, Portal Path
- Escalation path, known limitations table
- Diagnostic commands, related documentation links
- Footer nav

### EXPECTED.md Format

```markdown
# Control X.X: [Name] - Screenshot Specifications

## Required Screenshots

### Screenshot N: [Descriptive Title]
**Portal Path:** [Portal] → [Menu] → [Submenu] → [Page]
**What to capture:**
- [Specific UI element 1]
- [Specific UI element 2]
```

### Cross-Reference Link Conventions

- Same-pillar: `[1.5 - DLP](1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)`
- Cross-pillar: `[3.7 - PPAC Security](../pillar-3-reporting/3.7-ppac-security-posture-assessment.md)`

### mkdocs.yml Insertion Points

- **Controls nav:** After 1.24 entry, before "Pillar 2 - Management:"
- **Playbooks nav:** After 1.24 playbook block, before "Pillar 2 - Management:"

(Note: mkdocs.yml updates are Phase 5, not Phase 1)

## Architecture Decisions

1. **Control filename:** `1.25-mime-type-restrictions.md` (per ROADMAP.md file manifest)
2. **Zone model:** Zone 1 = baseline (blocked extensions only), Zone 2 = recommended (extensions + MIME types + allowlist), Zone 3 = regulated (comprehensive + server-side validation + DLP + Sentinel)
3. **Complementary controls:** Related to 1.5 (DLP), 1.10, 1.11, 1.13, 1.14 (data scope), 3.3, 3.7, 4.3
4. **File Upload Security (v8):** Per-agent toggle solution — 1.25 is environment-wide MIME policy, complementary not redundant
5. **Hardening Baseline items 28-29:** Basic MIME check items — 1.25 provides comprehensive governance framework around those checks
6. **Extra header field:** Include `**Last Verified:**` for consistency with recent controls (1.24 pattern)
7. **Portal paths:** PPAC Privacy + Security settings; mark as needing verification since UI may have changed

## Risk Assessment

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | No existing "File Upload Security" control to pattern from — 1.25 is net-new capability | Medium | Pattern from 1.24 exemplar; use spec PDF content for technical substance |
| 2 | Portal path uncertainty — MIME type settings may have moved in PPAC | Medium | Mark `Last UI Verified: February 2026 (Needs Verification)` and define EXPECTED.md screenshots for future verification |
| 3 | Spec language violations ("ensures compliance") | Low | Apply FSI language rules strictly; use hedged language throughout |
| 4 | Regulatory mapping precision — need specific rule/section citations | Low | Use FINRA 4511(a), SEC 17a-4(f), GLBA 501(b), OCC 2011-12 §III per existing patterns |

## Recommended Approach

### Plan A: Control Document (01-01-PLAN.md)
- Create `docs/controls/pillar-1-security/1.25-mime-type-restrictions.md`
- Follow 10-section template exactly with exemplar enrichments
- Zone-specific requirements: Zone 1 baseline / Zone 2 recommended / Zone 3 regulated
- Regulatory references per REQUIREMENTS.md traceability
- Related controls table: 1.5, 1.10, 1.11, 1.13, 1.14, 3.3, 3.7, 4.3
- Implementation playbook links (point to Phase 1 Plan B deliverables)
- FSI-safe language throughout

### Plan B: Playbooks + EXPECTED.md (01-02-PLAN.md)
- Create 4 playbooks in `docs/playbooks/control-implementations/1.25/`
- Create `docs/images/1.25/EXPECTED.md`
- Follow exemplar patterns from Control 1.24 playbooks exactly
- Portal walkthrough: PPAC configuration steps for MIME settings
- PowerShell setup: FsiMimeControl module (references Phase 2 module)
- Verification testing: Zone-by-zone compliance test procedures
- Troubleshooting: Common MIME configuration pitfalls
- EXPECTED.md: 4 screenshots (PPAC blocked extensions, blocked MIME types, allowed MIME types, compliance test output)

### Wave Assignment
Both plans target non-overlapping file sets → **Wave 1** (parallel-eligible).

---
*Research completed: 2026-02-12*
*Phase: 01 — Control Documentation & Playbooks*
*Milestone: v18 — MIME Type Restrictions for File Uploads*
