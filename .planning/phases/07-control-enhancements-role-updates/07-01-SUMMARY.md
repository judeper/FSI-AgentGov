---
phase: 07-control-enhancements-role-updates
plan: 01
subsystem: documentation-framework
tags: [dlp, virtual-connectors, http-filtering, zone-governance, control-1.5]
requires:
  - 06-03 (Agent 365 documentation complete)
provides:
  - Comprehensive virtual connector governance guidance with zone-specific configuration
  - FSI-specific HTTP endpoint filtering patterns
  - Virtual connector playbook enhancements (4 playbooks)
affects:
  - Future Control 1.5 implementations will reference enhanced virtual connector guidance
  - Zone 3 deployments benefit from detailed HTTP endpoint filtering examples
tech-stack:
  added: []
  patterns: [zone-specific-dlp-configuration, http-endpoint-filtering-fsi-patterns]
key-files:
  created: []
  modified:
    - docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md
    - docs/playbooks/control-implementations/1.5/portal-walkthrough.md
    - docs/playbooks/control-implementations/1.5/powershell-setup.md
    - docs/playbooks/control-implementations/1.5/verification-testing.md
    - docs/playbooks/control-implementations/1.5/troubleshooting.md
decisions:
  - Enhanced existing 11-connector table with zone-specific recommendation columns
  - Expanded HTTP endpoint filtering with FSI-specific patterns (banking APIs, regulatory sources, market data)
  - Added comprehensive zone-specific configuration guidance (Zone 1/2/3)
  - Updated all 4 playbooks with connector-specific implementation steps
metrics:
  duration: 6 minutes
  completed: 2026-02-06
---

# Phase 07 Plan 01: Virtual Connector Governance Enhancement Summary

**One-liner:** Enhanced Control 1.5 with comprehensive zone-specific virtual connector governance guidance, FSI HTTP endpoint filtering patterns, and updated playbooks for Zone 3 DLP enforcement.

---

## What Was Delivered

Enhanced Control 1.5 (Data Loss Prevention and Sensitivity Labels) and all 4 associated playbooks with comprehensive virtual connector governance guidance.

**Control 1.5 Enhancements:**

- Added zone-specific configuration columns to existing 11-connector table (Zone 1-2 Recommendation, Zone 3 Recommendation)
- Added comprehensive zone-specific virtual connector configuration table mapping each connector to recommended DLP classification per zone
- Expanded HTTP Endpoint Filtering section with FSI-specific patterns:
  - Internal API patterns for banking systems
  - Regulatory data source patterns (SEC EDGAR, FINRA APIs, FFIEC, Treasury)
  - Market data provider patterns (Bloomberg, Refinitiv)
  - "Common FSI Endpoint Patterns" table with Allow/Block examples
- Added inline regulatory mapping note (FINRA 4511, GLBA 501(b), SOX 404)
- Added GA admonition for virtual governance connectors (Q1 2025)
- Updated Roles & Responsibilities table to include AI Administrator role

**Playbook Enhancements:**

All 4 playbooks updated with comprehensive virtual connector content:

1. **portal-walkthrough.md:**
   - Expanded Step 2 with zone-specific connector classification substeps (Zone 1/2/3)
   - Added detailed HTTP endpoint filtering configuration steps
   - Added "Configure Zone-Specific Connector Classification" guidance
   - Included FSI-specific endpoint patterns for allow list configuration

2. **powershell-setup.md:**
   - Added PowerShell commands for virtual connector DLP classification export
   - Added audit script for Zone 3 connector configuration verification
   - Added comprehensive export script for audit evidence collection (CSV format)

3. **verification-testing.md:**
   - Added new test cases: VC-07 (Zone 3 classifications), VC-08 (HTTP filtering), VC-09 (DLP audit log)
   - Added HTTP endpoint filtering test cases (VC-13-16) for Zone 3 requirement verification
   - Added evidence collection guidance for virtual connector compliance

4. **troubleshooting.md:**
   - Added "Virtual connector classification not enforcing" troubleshooting entry
   - Added "HTTP endpoint filtering not blocking expected URLs" troubleshooting entry
   - Added "Maker sees no DLP error when using blocked connector" troubleshooting entry

---

## Task Commits

| Task | Description | Commit | Files Modified |
|------|-------------|--------|----------------|
| 1 | Expand Control 1.5 virtual connector documentation | ff8f1dd | docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md |
| 2 | Update Control 1.5 playbooks for virtual connector enhancements | 972deb5 | portal-walkthrough.md, powershell-setup.md, verification-testing.md, troubleshooting.md |

---

## Requirements Satisfied

**CTRL-01:** Virtual connector enumeration and DLP guidance expanded in Control 1.5

- ✅ Zone-specific recommendations for all 11 virtual governance connectors documented
- ✅ FSI-specific HTTP endpoint filtering patterns included (banking systems, regulatory sources, market data vendors)
- ✅ All 4 playbooks updated with connector-specific configuration, automation, testing, and troubleshooting content
- ✅ Inline regulatory mapping added (FINRA 4511, GLBA 501(b), SOX 404)
- ✅ GA admonition added for virtual governance connectors
- ✅ AI Administrator role added to Roles & Responsibilities table

---

## Decisions Made

1. **Enhanced existing table rather than replace:** Control 1.5 already had an 11-connector table at lines 77-93. Rather than replace it, we added zone-specific recommendation columns and expanded the supporting guidance below the table.

2. **Zone-specific configuration tables:** Added comprehensive zone-by-zone guidance with dedicated tables for Zone 1, Zone 2, and Zone 3 configuration approaches. This provides clear implementation paths for each governance tier.

3. **HTTP endpoint filtering expansion:** Expanded from 3-row example table to comprehensive FSI-specific patterns including:
   - Banking system API patterns (`*.internal.yourbank.com`)
   - Regulatory data sources (SEC, FINRA, FFIEC, Treasury)
   - Market data vendor patterns with BAA requirement notes
   - Social media and file-sharing block patterns

4. **Playbook depth matching control depth:** Playbooks received substantial expansion to match the depth of control enhancements. Portal walkthrough went from basic connector classification to zone-specific configuration steps with endpoint filtering details.

5. **Troubleshooting for common issues:** Added 3 new troubleshooting entries based on likely real-world issues: policy scope problems, endpoint filtering syntax errors, and maker notification issues.

---

## Deviations from Plan

None - plan executed exactly as written.

---

## Testing & Validation

- ✅ `python3 -m mkdocs build --strict` passes with zero errors (33.13 seconds)
- ✅ All internal links valid
- ✅ No hedging language violations ("ensures compliance" avoided throughout)
- ✅ All 11 virtual governance connectors enumerated with zone-specific guidance
- ✅ HTTP endpoint filtering examples use FSI-appropriate patterns
- ✅ Regulatory mapping uses hedging language ("helps support", not "ensures")

---

## What's Next

**For Phase 7:**
- Plan 02: DSPM AI Observability enhancements to Control 1.6
- Plan 03: AI Feature Access Control enhancements to Control 3.8
- Plan 04: AI Administrator and Defender XDR Administrator role catalog additions
- Plan 05: SharePoint Restricted Search enhancements to Control 4.6

**Dependencies for other work:**
- Control 1.5 virtual connector guidance now ready for FSI organizations implementing Zone 3 DLP policies
- HTTP endpoint filtering examples can be referenced by Control 2.3 (Third-Party Risk) documentation
- Virtual connector test cases available for QA teams validating DLP enforcement

---

## Self-Check: PASSED

**Files created:** None (all enhancements to existing files)

**Files modified (5 total):**
- ✅ docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md
- ✅ docs/playbooks/control-implementations/1.5/portal-walkthrough.md
- ✅ docs/playbooks/control-implementations/1.5/powershell-setup.md
- ✅ docs/playbooks/control-implementations/1.5/verification-testing.md
- ✅ docs/playbooks/control-implementations/1.5/troubleshooting.md

**Commits exist (2 total):**
- ✅ ff8f1dd (Task 1: Control 1.5 expansion)
- ✅ 972deb5 (Task 2: Playbook updates)

All files exist, all commits present in git log.

---

*Completed: 2026-02-06 | Duration: 6 minutes | Commits: 2*
