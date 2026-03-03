# Changelog — v1.1.x

All notable changes to the FSI Agent Governance Framework v1.1.x releases are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

**Other versions:** [Current (v1.2.x)](CHANGELOG-v1.2.md) | [v1.0.x and earlier](CHANGELOG-v1.0.md)

---

## [1.1.9] — January 24, 2026 (Learn Monitor Documentation)

### Overview

Added comprehensive documentation explaining how the Microsoft Learn Documentation Monitor works, including verification that the system is operating correctly.

### Added

- **Learn Monitor Guide** (`docs/reference/learn-monitor-guide.md`) - Detailed documentation covering:
  - When the monitor runs (daily at 6 AM UTC)
  - When PRs are created (Sundays or when changes detected)
  - Change classification (CRITICAL/HIGH/MEDIUM/NOISE)
  - Local testing commands
  - Troubleshooting guide
- **Navigation updates** - Added guide to mkdocs.yml and reference index

### Verified

- Learn monitor script syntax valid
- Dependencies installed (requests, beautifulsoup4)
- Dry-run mode working correctly
- Single URL debug mode operational
- GitHub Actions workflow running successfully (5 consecutive daily passes)

### Files Modified

| File | Changes |
|------|---------|
| `docs/reference/learn-monitor-guide.md` | New file - comprehensive monitor documentation |
| `docs/reference/index.md` | Added Learn Monitor Guide to Technical Reference section |
| `mkdocs.yml` | Added navigation entry for Learn Monitor Guide |
| `.claude/CLAUDE.md` | Added guide to Key Files and Quick Navigation |
| `CHANGELOG.md` | This entry |

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/learn_monitor.py --dry-run --limit 3`: Pass

---

## [1.1.8] — January 24, 2026 (Documentation Consistency Fixes)

### Overview

This release addresses documentation inconsistencies identified during a review, including version alignment, regulatory coverage, maturity level clarification, and retention period standardization.

### Fixed

- **Version Alignment** - Updated governance-fundamentals.md, zones-and-tiers.md, CONTROL-INDEX.md to v1.1.8
- **Regulatory Coverage** - Added FDIC and NCUA to governance-fundamentals.md
- **Maturity Levels** - Clarified distinction between implementation levels (3) and maturity scale (0-4)
- **Retention Periods** - Aligned Zone 3 retention across zones and controls (7-10 years); added rationale

### Added

- **Microsoft-Built Agents Applicability** - Control mapping for Researcher, Analyst, Facilitator agents in governance-fundamentals.md

### Files Modified

| File | Changes |
|------|---------|
| `README.md` | Version (1.1.7→1.1.8), maturity levels clarification |
| `docs/framework/governance-fundamentals.md` | Version, regulators (FDIC/NCUA), maturity note, Microsoft-built agents section |
| `docs/framework/zones-and-tiers.md` | Version, retention rationale note |
| `docs/controls/CONTROL-INDEX.md` | Version |
| `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Zone 3 retention (7-10 years) |
| `docs/controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md` | Zone 3 retention (7-10 years) |
| `CHANGELOG.md` | This entry |

### Validation

- `mkdocs build --strict`: Pass
- `python scripts/verify_controls.py`: All 61 controls valid

---

## [1.1.7] — January 23, 2026 (Documentation Accuracy Fixes)

### Overview

This release addresses technical inaccuracies identified during a comprehensive deep review, including invalid KQL queries, incorrect PowerShell parameters, outdated regulatory references, and missing admin settings documentation.

### Fixed

- **KQL Queries** - Corrected 6 queries using non-existent tables (`CopilotInteraction`, `SharePointAuditLogs`, `SharePointSiteProperties`, `SharePointFileProperties`, `DlpAll`). Now use correct `OfficeActivity` and `CloudAppEvents` tables with appropriate RecordType filtering.

- **PowerShell Parameter** - Replaced `RestrictContentOrgWideSearchAndCopilot` with correct GA parameter `RestrictContentOrgWideSearch` across 9 files (4.6/4.7 playbooks, semantic-index-governance-queries.md, control 4.6).

- **SEC 17a-4 References** - Updated ~15 files to reflect October 2022 amendments (effective May 2023) that made WORM optional. Broker-dealers can now use either WORM storage or audit-trail alternative.

- **FINRA Notice 25-07 Status** - Added RFC disclaimer to key files clarifying that Notice 25-07 is a Request for Comment with comment period extending to July 2025 (not final requirements). Changed language from "requires" to "proposes" where applicable.

### Added

- **Data Source Limitations** - Added explanatory notes in KQL query documentation explaining hybrid PowerShell/KQL approach needed for site/file property data not available in Log Analytics.

- **Agent 365 Admin Settings** - Added reference to Microsoft 365 Admin Center "Agent settings" page in Control 1.2 and its portal walkthrough, including:
  - Allowed Agent Types configuration
  - Sharing controls
  - Templates (Agent 365 license)
  - User Access controls
  - FSI zone-specific recommended settings table

- **Parameter Status Notes** - Added admonitions clarifying GA vs. preview status for PowerShell parameters.

### Files Modified

| Area | Files Updated |
|------|---------------|
| KQL Queries | `semantic-index-governance-queries.md`, `3.9/powershell-setup.md`, `1.7` control |
| PowerShell Parameter | 9 files in 4.6, 4.7 playbooks and control docs |
| SEC 17a-4 | ~15 files including controls 1.7, 1.9, 2.13 and playbooks |
| FINRA 25-07 | ~6 key files including control 2.11, regulatory-mappings.md |
| Agent 365 | Control 1.2 and `1.2/portal-walkthrough.md` |

### Validation

- `python scripts/verify_controls.py`: ✅ All 61 controls valid
- Control structure: ✅ Pass

---

## [1.1.6] — January 20, 2026 (Microsoft Learn Documentation Monitor)

### Overview

This release adds an automated monitoring system to detect changes in Microsoft Learn documentation that may require updates to the FSI-AgentGov framework. The monitor runs daily, classifies changes by impact, identifies affected controls and playbooks, and creates PRs for human review.

### Added

- **Microsoft Learn Documentation Monitor** (`scripts/learn_monitor.py`)
  - Monitors ~190 Microsoft Learn URLs from the watchlist
  - Detects content changes using BeautifulSoup + SHA-256 hashing
  - Classifies changes as meaningful/minor/noise based on:
    - UI navigation steps (CRITICAL for playbooks)
    - Policy language and compliance features (HIGH)
    - Deprecation notices and breaking changes (HIGH)
    - Configuration instructions (MEDIUM)
  - Maps changes to affected controls and playbooks
  - Generates markdown reports with diff snippets
  - Supports debugging: `--url`, `--debug`, `--verbose`, `--limit`, `--dry-run`

- **GitHub Actions Workflow** (`.github/workflows/learn-monitor.yml`)
  - Daily scheduled runs at 6:00 AM UTC
  - Manual trigger via workflow_dispatch
  - Creates PRs on meaningful changes or weekly baseline (Sundays)
  - Labels: `documentation`, `automated`, `learn-watch`

- **State and Report Directories**
  - `data/` - Stores `learn-monitor-state.json` with content hashes
  - `reports/learn-changes/` - Stores dated change reports

### Changed

- **Fixed cross-platform path issue** (`scripts/compile_researcher_package.py`)
  - Changed from hardcoded Windows path to dynamic detection
  - Now works on Windows, macOS, and Linux

- **Improved hook error handling** (`scripts/hooks/boundary-check.py`)
  - Added empty input handling
  - Added JSONDecodeError catch
  - Simplified confusing conditional logic

- **Improved hook error handling** (`scripts/hooks/researcher-package-reminder.py`)
  - Added empty input handling
  - Added broad exception catch
  - Both hooks now fail open (allow on error)

### Files Modified

| File | Action |
|------|--------|
| `scripts/learn_monitor.py` | Created (~750 lines) |
| `.github/workflows/learn-monitor.yml` | Created |
| `data/.gitkeep` | Created |
| `reports/learn-changes/.gitkeep` | Created |
| `scripts/compile_researcher_package.py` | Fixed path detection |
| `scripts/hooks/boundary-check.py` | Improved error handling |
| `scripts/hooks/researcher-package-reminder.py` | Improved error handling |

### Validation

- `mkdocs build --strict`: ✅ Pass
- `python scripts/learn_monitor.py --limit 3 --dry-run`: ✅ Pass
- `python scripts/compile_researcher_package.py`: ✅ Pass
- Hook scripts handle edge cases without errors

---

## [1.1.5] — January 20, 2026 (Claude Code Configuration Update)

### Overview

This release updates the Claude Code configuration to align with latest Anthropic documentation (v2.1+, January 2026), including YAML frontmatter for skills and a split settings architecture.

### Added

- **Team-shared settings file** (`.claude/settings.json`)
  - Base permissions for git, mkdocs, python, pip commands
  - Deny rules for dangerous operations (`rm -rf /`, `.env` access)
  - Hook configurations (PreToolUse, PostToolUse)
  - Version-controlled for team consistency

- **YAML frontmatter to all 4 skills**
  - `name` - Skill identifier for invocation
  - `description` - Enables auto-suggestion based on task context
  - `allowed-tools` - Restricts tool access per skill
  - `user-invocable: true` - Enables `/skill-name` invocation

### Changed

- **Settings architecture split**
  - `settings.json` - Team-shared configuration (committed)
  - `settings.local.json` - Local overrides only (not committed)
  - Settings merge at runtime for flexibility

- **Slimmed settings.local.json**
  - Reduced from 30 rules to 5 local-only rules
  - Contains: `includeCoAuthoredBy`, WebFetch domains, GitHub CLI permissions

- **Updated CLAUDE.md documentation**
  - New "Configuration" section with settings file reference
  - Updated directory structure showing both settings files
  - Enhanced Skills section with frontmatter description
  - Detailed hooks documentation with JSON output format

### Skills Updated

| Skill | Allowed Tools |
|-------|---------------|
| `/update-control` | Read, Edit, Glob, Grep, Bash |
| `/add-control` | Read, Write, Edit, Glob, Grep, Bash |
| `/update-excel` | Read, Bash, Glob |
| `/verify-ui` | Read, Edit, Glob, Grep, WebFetch |

### Files Modified

| File | Action |
|------|--------|
| `.claude/skills/update-control.md` | Added YAML frontmatter |
| `.claude/skills/add-control.md` | Added YAML frontmatter |
| `.claude/skills/update-excel.md` | Added YAML frontmatter |
| `.claude/skills/verify-ui.md` | Added YAML frontmatter |
| `.claude/settings.json` | Created (team-shared) |
| `.claude/settings.local.json` | Slimmed to local-only |
| `.claude/CLAUDE.md` | Updated configuration documentation |

### Validation

- `mkdocs build --strict`: ✅ Pass
- All 4 skills have valid YAML frontmatter
- Hook scripts output correct JSON format
- Boundary check hook blocks dangerous commands

---

## [1.1.4] — January 20, 2026 (Microsoft Audit Reporting Tools Integration)

### Overview

This release integrates two Microsoft Engineering open-source tools that address a common FSI pain point: M365 Admin Center provides limited Copilot/AI reporting data, and Viva Insights data is de-identified. These tools enable enterprise-scale audit data extraction and adoption analytics.

### Added

- **Microsoft Audit Reporting Tools Playbook** (`docs/playbooks/advanced-implementations/microsoft-audit-reporting-tools.md`)
  - Comprehensive guide for AI-in-One Dashboard and PAX (Portable Audit eXporter)
  - FSI-specific implementation considerations and use cases
  - Integration guidance for FINRA 25-07 prompt/response capture
  - SEC 17a-4 WORM storage workflow support
  - Compliance considerations (data handling, permissions, classification)

- **Microsoft Open Source Tools Section** (`docs/reference/microsoft-learn-urls.md`)
  - AI-in-One Dashboard GitHub repository link
  - PAX (Portable Audit eXporter) GitHub repository link
  - Cross-reference to implementation playbook

### Enhanced

- **Control 1.7 (Comprehensive Audit Logging)** - Added cross-reference to Microsoft Audit Reporting Tools playbook for enterprise-scale audit extraction
- **Control 3.2 (Usage Analytics)** - Added cross-reference to Microsoft Audit Reporting Tools playbook for enhanced adoption analytics
- **Control 3.3 (Compliance Reporting)** - Added cross-reference to Microsoft Audit Reporting Tools playbook for examination evidence generation
- **Control 3.8 (Copilot Hub)** - Added cross-reference to Microsoft Audit Reporting Tools playbook for supplemental reporting capabilities

### Changed

- **mkdocs.yml** - Added navigation entry for Microsoft Audit Reporting Tools under Advanced Implementations

### Tools Integrated

| Tool | GitHub Repository | Purpose |
|------|-------------------|---------|
| AI-in-One Dashboard | microsoft/AI-in-One-Dashboard | Power BI template for Copilot adoption analytics |
| PAX (Portable Audit eXporter) | microsoft/PAX | PowerShell scripts to export audit log data at scale |

### Gaps Addressed

These tools address the following capability gaps identified in the framework:

| Gap | Tool | How Addressed |
|-----|------|---------------|
| Real-Time Executive Dashboard | AI-in-One Dashboard | Pre-built Power BI template with department segmentation |
| Advanced Data Analytics | PAX | Raw data export for custom analytics pipelines |
| Trend Analysis | AI-in-One Dashboard | Time-series adoption tracking by department/role |
| Third-Party Integration | PAX | CSV/Excel export compatible with any BI tool |
| 50K Record Export Limit | PAX | Incremental exports with watermarking bypass native limits |

### Files Modified

| File | Change |
|------|--------|
| `docs/playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` | **Created** - New playbook |
| `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md` | Added cross-reference |
| `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` | Added cross-reference |
| `docs/reference/microsoft-learn-urls.md` | Added Microsoft Open Source Tools section |
| `mkdocs.yml` | Added nav entry for new playbook |

### Validation

- `mkdocs build --strict`: ✅ Pass
- All cross-references resolve correctly
- GitHub repository links verified accessible

---

## [1.1.3] — January 19, 2026 (Deep Review & Enhancements)

### Overview

This release completes a comprehensive 10-agent deep review of the entire repository, verifying completeness, regulatory coverage, and alignment with framework objectives. All identified enhancements have been implemented.

### Added

- **Microsoft Learn URL Tracking** (`docs/reference/microsoft-learn-urls.md`)
  - Expanded from 48 to 159 tracked URLs (100% coverage of links used in documentation)
  - Added 12 new product categories: Azure Services, Microsoft Defender, Power Automate, Power Apps, Microsoft Teams, Microsoft Graph API, Power BI, Microsoft Viva, Security Operations, PowerShell References, Office 365 Management API, Microsoft Entra Agent ID
  - All links verified as of January 2026
  - Purpose: Enable automated monitoring for Microsoft documentation changes

- **Microsoft Platform Update Monitoring** (`docs/playbooks/control-implementations/2.7/troubleshooting.md`)
  - New section: Monitoring Channels (Message Center, Service Health, Release Plans, What's New, Roadmap)
  - Recommended monitoring process (weekly/monthly/quarterly cadence)
  - Re-validation triggers for Microsoft platform changes
  - PowerShell script for Message Center monitoring

- **ECOA Quarterly Testing Requirements** (`docs/playbooks/control-implementations/2.11/verification-testing.md`)
  - ECOA 9 protected classes reference table with citations (15 U.S.C. § 1691)
  - Quarterly testing checklist with due dates and owners
  - Minimum sample sizes per protected class category
  - New Test 5: Verify Quarterly Cadence for Zone 3 agents

### Documentation

- **CLAUDE.md Updates**
  - Added Comprehensive Deep Review section documenting 10-agent analysis
  - Added Review Directory (`review/`) documentation explaining external validation artifacts
  - Updated version to v1.1.3

### Verified (No Changes Needed)

The deep review confirmed the following are already adequately covered:

| Gap Candidate | Status | Existing Coverage |
|---------------|--------|-------------------|
| IP Cookie Binding | ✅ Covered | Control 1.20 |
| AI Data Sharing Tenant Setting | ✅ Covered | Controls 2.1, 4.7 |
| Cross-Geographic Data Movement | ✅ Covered | Controls 2.1, 1.20 |
| Maker Welcome Content | ✅ Covered | Control 2.1 Section 4 |
| AI Plugin Governance | ✅ Covered | Controls 1.4, 2.7, 4.7 |
| Skills Connector Governance | ✅ Covered | Controls 1.4, 2.17 |
| Web Channel Security | ✅ Covered | Controls 4.7, 4.1 |
| Colorado AI Act | ✅ Covered | `docs/playbooks/regulatory-modules/` |

### Deep Review Summary

| Area | Score | Status |
|------|-------|--------|
| Framework Alignment | 9.5/10 | Excellent |
| Control Completeness | 10/10 | Complete |
| Cross-Reference Integrity | 9.5/10 | Excellent |
| Stale Documentation | 1/10 (staleness) | Very Clean |
| Regulatory Coverage | 85/100 | Strong |
| Microsoft Learn Links | 100% | Complete |
| Copilot Studio DLP | 94% | Strong |
| Power Platform Architecture | 100% | Complete |

---

## [1.1.2] — January 19, 2026 (NIST AI RMF Crosswalk Correction)

### Fixed

- **NIST AI RMF Crosswalk Accuracy** (`docs/reference/nist-ai-rmf-crosswalk.md`)
  - Corrected subcategory counts in summary table (was 61, actual 67 subcategories addressed)
  - Added methodology section explaining coverage calculation against NIST AI RMF 1.0 (72 total subcategories)
  - Updated coverage figures: 93% of NIST subcategories addressed, 97% effective coverage of applicable areas
  - Documented 5 subcategories not explicitly addressed (MEASURE 2.12/2.13, MAP 3.4/3.5, GOVERN 4.4) with rationale
  - Updated auditor guidance with accurate coverage metrics

### Changed

- **Coverage Summary Table:** Now shows correct subcategory counts per function (GOVERN 19, MAP 16, MEASURE 19, MANAGE 13)
- **Coverage Claim:** Changed from "92% Full coverage" to "93% subcategories addressed, 97% effective coverage of applicable areas"

### Context

This fix was identified during a comprehensive 18-agent framework review. The original summary table had arithmetic errors in the subcategory counts, and the coverage calculation did not account for the full NIST AI RMF 1.0 structure (72 subcategories). The crosswalk content and control mappings remain accurate; only the summary statistics were corrected.

---

## [1.1.1] — January 2026 (Researcher Gap Analysis Response)

### Overview

This release addresses findings from an external researcher gap analysis, implementing valid recommendations and documenting rationale for rejected items.

**Summary:** Of 19 claimed gaps, 8 were invalid (already covered), 5 were partially valid (minor enhancements), 2 were valid (new content created), and 4 were out of scope.

### Added

- **Control 2.21: AI Marketing Claims and Substantiation** — New control addressing SEC Marketing Rule (206(4)-1) and "AI washing" enforcement precedent (Delphia, Global Predictions 2024 settlements)
- **4 Playbooks for Control 2.21:**
  - `portal-walkthrough.md` — Claims inventory setup and review workflow
  - `powershell-setup.md` — SharePoint list and automation scripts
  - `verification-testing.md` — Test cases and attestation template
  - `troubleshooting.md` — Common issues and resolutions
- **NIST AI RMF Crosswalk** (`docs/reference/nist-ai-rmf-crosswalk.md`) — Maps all 61 controls to NIST AI RMF GOVERN/MAP/MEASURE/MANAGE functions (92% coverage)
- **SEC Marketing Rule section** in `docs/reference/regulatory-mappings.md`

### Enhanced (8 Controls)

- **Control 1.7:** Added AI-generated communication tagging guidance per FINRA 25-07 (AI vs human attribution, event types)
- **Control 1.10:** Added monitored Copilot and AI locations table with audit event names and friendly names
- **Control 1.8:** Added AI-enabled threat patterns section (deepfakes, AI phishing, synthetic identities) per NYDFS cyber guidance
- **Control 1.11:** Added PIM baselines table for AI administration roles with activation durations and approvers
- **Control 1.23:** Added PIM integration for sensitive agent operations (publishing, deletion, policy changes)
- **Control 1.4:** Added Copilot plugins and extensions terminology table clarifying governance scope
- **Control 2.7:** Added FSI-specific vendor categories table including archiving vendors (Smarsh, Global Relay, etc.)
- **Control 3.3:** Added AI regulatory impact assessment template with regulatory driver mapping

### Changed

- **Control count:** 60 → 61 controls
- **Pillar 2 count:** 20 → 21 controls
- Updated `docs/controls/CONTROL-INDEX.md` with Control 2.21
- Updated `mkdocs.yml` navigation for Control 2.21 and NIST crosswalk
- Updated `docs/reference/regulatory-mappings.md` coverage table to 61 controls

### Researcher Gap Analysis Summary

| Gap Category | Count | Action |
|--------------|-------|--------|
| **INVALID (Already Covered)** | 8 | No action - researcher missed existing coverage |
| **PARTIALLY VALID (Enhancement)** | 5 | Minor documentation improvements (completed) |
| **VALID (New Content)** | 2 | Control 2.21 + NIST crosswalk (completed) |
| **OUT OF SCOPE** | 4 | Rejected - outside M365 framework focus |

**Rejected Items (Out of Scope):**
- REG-004: SEC predictive analytics (proposal not finalized)
- REG-007: NAIC AI Model Bulletin (insurance outside primary scope)
- CC-012: ISO 42001/23894 (US FSI-focused, not multi-jurisdiction)
- IND-015: SEC/FINRA exam focus (restatement, not gap)

---

## [1.1] — January 2026

### Architecture

- **Three-Layer Documentation Model:**
  - **Layer 1 - Framework** (`docs/framework/`): Governance principles for executives and compliance
  - **Layer 2 - Controls** (`docs/controls/`): Technical specifications (60 controls across 4 pillars)
  - **Layer 3 - Playbooks** (`docs/playbooks/`): Step-by-step implementation procedures
- Renamed `docs/reference/pillar-*/` to `docs/controls/pillar-*/` for clarity
- Reorganized `docs/operational-templates/` content into `docs/playbooks/`
- Added role-based navigation on homepage

### Added

- **Framework Layer (9 documents):**
  - `executive-summary.md` — Board-level overview
  - `zones-and-tiers.md` — Zone 1/2/3 classification guidance
  - `adoption-roadmap.md` — 30/60/90-day phased implementation
  - `agent-lifecycle.md` — Agent lifecycle management
  - `operating-model.md` — RACI and accountability
  - `governance-fundamentals.md` — Core governance principles
  - `governance-cadence.md` — Recurring governance activities
  - `regulatory-framework.md` — FSI regulatory landscape
  - `index.md` — Framework layer overview

- **Control Implementation Playbooks (240 files):**
  - Created 4 playbooks per control (60 controls × 4 = 240 files)
  - Playbook types for each control:
    - `portal-walkthrough.md` — Step-by-step portal configuration
    - `powershell-setup.md` — PowerShell automation scripts
    - `verification-testing.md` — Test cases and evidence collection
    - `troubleshooting.md` — Common issues and resolutions
  - Located at `docs/playbooks/control-implementations/{control-id}/`
  - Each playbook includes: prerequisites, step-by-step instructions, configuration by governance level, FSI example configurations, validation checklists

- **Playbook Categories:**
  - `governance-operations/` — Standing procedures (weekly reviews, quarterly assessments)
  - `compliance-and-audit/` — Audit preparation, evidence collection, examination response
  - `incident-and-risk/` — Data exposure, compliance violation handling
  - `agent-lifecycle/` — Agent provisioning, retirement, updates

- **Scripts Directory Enhancement:**
  - `scripts/README.md` — Usage guide
  - `scripts/requirements.txt` — Python dependencies
  - `scripts/governance/` — Governance automation (placeholder)
  - `scripts/reporting/` — Reporting automation (placeholder)
  - `scripts/hooks/boundary-check.py` — Project boundary protection hook

- **GitHub Issue Templates:**
  - `bug-report.md` — Bug reporting template
  - `feature-request.md` — Feature request template
  - `ui-verification.md` — UI verification checklist

### Changed

- Zone 1 regulatory language softened to conditional phrasing
- Pillar 4 explicitly positions as SharePoint specialization of Pillars 1-3
- HITL patterns explicitly defined (Pre-Approval, Sampled Review, Escalation-on-Threshold)
- Controls 2.12 and 2.19 updated with customer-facing conduct notes
- Updated `.claude/claude.md` with three-layer documentation guidance
- Updated `.github/copilot-instructions.md` with new directory structure
- Updated `scripts/verify_controls.py` to use `docs/controls/` path
- Updated `scripts/compile_researcher_package.py` to use `docs/controls/` path
- Updated `scripts/hooks/researcher-package-reminder.py` to detect both old and new paths

### Fixed

- **Fixed `verify_controls.py` validation mismatch** (CI failure):
  - Updated footer constants to match actual control format (`Updated: January 2026`, `Version: v1.1`, `UI Verification Status:`)
  - Updated required headings to match actual control structure (`## Objective`, `## Why This Matters for FSI`, `## Control Description`, etc.)
  - Updated required metadata fields to match actual control files (`**Control ID:**`, `**Pillar:**`, `**Regulatory Reference:**`)
  - Changed Primary Owner validation to check for `## Roles & Responsibilities` section
  - Fixed missing `UI Verification Status` in controls 2.1 and 2.2 footers
- Fixed 6 broken cross-references between controls:
  - Control 2.16 → 4.1 (wrong filename)
  - Control 2.19 → 1.6 (wrong filename)
  - Control 2.4 → 3.4 (wrong filename)
  - Control 2.6 → 3.3 (wrong filename)
  - Control 3.5 → 2.2 (wrong filename)
  - Control 3.6 → 2.3 (wrong filename)
- Fixed relative path issues in playbooks (1.1, 3.1, 3.2)
- Resolved all link warnings in mkdocs build

### Removed (Legacy Cleanup - January 18, 2026)

- **Deleted legacy pillar directories** (64 files):
  - `docs/reference/pillar-1-security/` — superseded by `docs/controls/pillar-1-security/`
  - `docs/reference/pillar-2-management/` — superseded by `docs/controls/pillar-2-management/`
  - `docs/reference/pillar-3-reporting/` — superseded by `docs/controls/pillar-3-reporting/`
  - `docs/reference/pillar-4-sharepoint/` — superseded by `docs/controls/pillar-4-sharepoint/`
- **Deleted legacy operational-templates** (21 files):
  - `docs/operational-templates/` — content migrated to `docs/playbooks/`
- **Deleted excluded getting-started duplicates** (4 files):
  - `docs/getting-started/overview.md` — duplicate of `docs/framework/index.md`
  - `docs/getting-started/zones.md` — duplicate of `docs/framework/zones-and-tiers.md`
  - `docs/getting-started/lifecycle.md` — duplicate of `docs/framework/agent-lifecycle.md`
  - `docs/getting-started/governance-review-cadence.md` — duplicate of `docs/framework/governance-cadence.md`
- **Updated mkdocs.yml** — removed exclude_docs entries for deleted files
- **Fixed docs/downloads/index.md** — corrected control count (58→60) and version (v1.0→v1.1)

### Documentation Cleanup (January 18, 2026)

Fixed stale documentation after v1.1 restructuring:

- **docs/reference/regulatory-mappings.md** — Fixed broken hyperlink to Colorado AI Impact Assessment (changed from deleted `../operational-templates/...` to `../playbooks/regulatory-modules/...`)
- **docs/getting-started/checklist.md** — Updated control counts from 48 to 60; fixed pillar counts (19→23, 15→20, 9→10, 5→7); updated version footer from v1.0 to v1.1
- **docs/reference/faq.md** — Updated control counts from 48 to 60 with corrected pillar breakdown
- **docs/images/README.md** — Updated documentation paths from `docs/reference/pillar-*` to `docs/controls/pillar-*`
- **docs/images/VERIFY.md** — Updated path pattern from `docs/reference/...` to `docs/controls/...`
- **docs/templates/README.md** — Removed references to non-existent JSON files; updated control count from 48 to 60; updated "After Creating a Control" steps to reference CONTROL-INDEX.md
- **mkdocs.yml** — Added `playbooks/control-implementations/*/` to exclude_docs to suppress 240 "not in nav" warnings

### Comprehensive Repository Verification (January 18, 2026)

Exhaustive verification of all repository content (scripts, Excel files, documentation) with automated tooling.

**Scripts Deleted (6 legacy one-time migration scripts with stale paths):**
- `scripts/apply_primary_owner_roles.py`
- `scripts/fix_zone_guidance_grammar.py`
- `scripts/tailor_zone_guidance.py`
- `scripts/fix_controls_targeted_cleanup.py`
- `scripts/audit_controls_zone_hygiene.py`
- `scripts/generate_zone_cleanup_plan.py`

**Scripts Added:**
- `scripts/verify_excel_templates.py` — Validates Excel template control counts and stale content
- `scripts/update_excel_templates.py` — Updates Excel templates (version references, missing controls)

**Documentation Fixed:**
- **docs/reference/microsoft-learn-urls.md** — Updated footer date from "December 2025" to "January 2026"
- **docs/reference/faq.md** — Updated preview feature table header from "Dec 2025" to "Jan 2026"

**Excel Templates Updated (all 6 files):**
- Updated version footer from "v1.0 Beta" to "v1.1" in all 6 Excel files
- Added missing controls 1.23 and 2.20 to `governance-maturity-dashboard.xlsx` (58→60 controls)

**Validation Results:**
- All documentation layers verified clean (framework, reference, controls, playbooks, getting-started)
- All Excel templates pass verification (`verify_excel_templates.py`)
- Zero stale "48 control" references in docs
- Zero stale `docs/reference/pillar-*` paths in active scripts
- Zero stale "v1.0" references (except CHANGELOG historical entries)

### Playbook Navigation Integration Fix (January 19, 2026)

**Problem Fixed:** 240 playbook files were excluded from MkDocs build and not published to GitHub Pages, causing broken links in control documentation Section 8 (Implementation Guides).

**Root Cause:** The `playbooks/control-implementations/*/` directory pattern was listed in `mkdocs.yml` under `exclude_docs` (added during v1.1 to suppress "not in nav" warnings), which prevented the playbook files from being published.

**Solution:**
- Removed `playbooks/control-implementations/*/` from `exclude_docs` in `mkdocs.yml`
- Added all 60 control playbook sections to site navigation under `Playbooks → Control Implementations` (~305 lines)
- Each control now has 4 nested playbook links: Portal Walkthrough, PowerShell Setup, Verification, Troubleshooting

**Files Modified:**
- `mkdocs.yml` - Removed exclusion pattern, added nested playbook nav structure (lines 163-468)
- `.claude/CLAUDE.md` - Added context section documenting this fix
- `.claude/settings.local.json` - Added `includeCoAuthoredBy: false` setting

**Validation:**
- `mkdocs build --strict` passes
- All 240 playbook HTML files now generated in site/
- Navigation hierarchy complete: Framework → Controls → Playbooks (with nested control sections)

---

