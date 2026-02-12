# Phase 3 Research: DLP Policy & Sentinel Monitoring

## Phase Goal

Create Purview DLP policy template and Sentinel monitoring queries/alerts for MIME-based upload blocking.

## Requirements Covered

- **MON-01:** DLP policy template (Purview)
- **MON-02:** Sentinel KQL queries (2 queries)
- **MON-03:** Sentinel analytics alert rule ARM template

## Technical Analysis

### DLP Policy Template

Standard Purview DLP unified policy template (JSON) for Power Platform locations. Key elements:
- `policyId`: GUID placeholder for customer deployment
- `rules`: Array of content restriction rules matching file extensions and MIME patterns
- `conditions`: File extension matching for executable patterns
- `actions`: Block access, generate incident reports
- `locations`: Power Platform environments (configurable filter)
- Pattern: Executable file types from zone2.json/zone3.json blocked extensions lists

**Blocked file patterns (from zone templates):**
- Extensions: exe, bat, cmd, ps1, vbs, js, jar, dll, msi, scr, hta (11 core dangerous types)
- Additional high-risk: com, cpl, inf, lnk, pif, reg, sct, wsf, wsh

### Sentinel KQL Queries

**query-mime-blocks.kql:**
- Source table: `PowerPlatformDlpActivity_CL` or `PowerPlatformAdminActivity` (depending on tenant config)
- Time range: 30 days lookback
- Aggregation: By file extension, user, environment
- Purpose: Blocked upload attempt visibility and trending

**query-exception-usage.kql:**
- Source table: `PowerPlatformAdminActivity` + custom exception register data
- Time range: 90 days lookback
- Correlation: Upload events for exception-listed MIME types
- Purpose: Exception utilization monitoring and anomaly detection

### Sentinel Analytics Alert Rule ARM Template

Standard ARM template for `Microsoft.SecurityInsights/alertRules` (scheduled type):
- `$schema`: `https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#`
- Resource type: `Microsoft.OperationalInsights/workspaces/providers/alertRules`
- Kind: `Scheduled`
- Threshold: >10 blocked upload attempts per user per hour
- MITRE ATT&CK: T1566 (Phishing), T1204 (User Execution)
- Entity mapping: Account
- Incident grouping: By user
- Frequency: 1 hour
- Lookback: 1 hour
- Severity: Medium

### Existing Project Patterns

- **Solution artifacts in `src/`:** JSON files (workbooks, flows, adaptive cards) — no Sentinel templates yet
- **Zone templates:** `scripts/governance/mime-templates/zone{1,2,3}.json` — provide the MIME type and extension lists
- **No existing KQL or ARM templates** in the repo — these are first-of-kind artifacts

## Architecture Decisions

1. **DLP template format:** Purview unified DLP policy JSON (not legacy EXO format)
2. **KQL log source:** Use `PowerPlatformDlpActivity_CL` (custom log) as primary table with fallback comment noting `PowerPlatformAdminActivity` alternative
3. **ARM template API version:** `2023-02-01` for Microsoft.SecurityInsights
4. **Alert threshold:** >10 blocks/user/hour as high-volume indicator (per roadmap spec)
5. **File target locations:** All 4 files in `src/` directory per roadmap manifest
6. **Configurable environment filter:** DLP template includes placeholder for environment scope restriction

## Risk Assessment

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | Purview DLP policy JSON schema variations across tenants | Low | Use well-documented rule structure; add deployment notes |
| 2 | KQL table names vary by tenant configuration | Low | Comment alternatives in queries |
| 3 | ARM API version changes | Low | Use stable 2023-02-01 version |

## Recommended Approach

### Plan A: DLP Policy Template + KQL Queries (03-01-PLAN.md)
- Create `src/dlp-policy-template.json` — Purview DLP unified policy
- Create `src/query-mime-blocks.kql` — blocked uploads KQL (30-day)
- Create `src/query-exception-usage.kql` — exception usage KQL (90-day)
- All files in `src/` per roadmap manifest

### Plan B: Sentinel Alert Rule ARM Template (03-02-PLAN.md)
- Create `src/high-volume-blocks.json` — ARM template for scheduled analytics rule
- >10 blocks/user/hour threshold
- MITRE ATT&CK mapping, entity mapping, incident grouping
- Complete deployable ARM template

### Wave Assignment
Both plans target non-overlapping file sets → **Wave 1** (parallel-eligible).

---
*Research completed: 2026-02-12*
*Phase: 03 — DLP Policy & Sentinel Monitoring*
*Milestone: v18 — MIME Type Restrictions for File Uploads*
