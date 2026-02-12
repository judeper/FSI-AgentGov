# v16 Research Summary — Unrestricted Agent Sharing Detector

**Created:** 2026-02-12
**Sources:** v16-tech-stack.md, v16-features.md, v16-architecture.md, v16-pitfalls.md

## Key Findings

### Technology Stack
- BAP API (`api.bap.microsoft.com`) is the sole source of truth for agent sharing principals — spec-mandated
- Dataverse OData available as fallback for agent enumeration
- Graph API excluded for sharing decisions (Non-Negotiable Rule #2)
- Lab-grade security: interactive auth initially, managed identity deferred

### Features
- UASD fills 6 automation gaps across Controls 1.1 and 3.8
- Addresses SSPM items 1-4 from Configuration Hardening Baseline (currently manual attestation)
- 5 violation types: ORG_WIDE_SHARING, PUBLIC_INTERNET_LINK, UNAPPROVED_GROUP, EXCESSIVE_INDIVIDUAL, CROSS_TENANT_ACCESS
- Exception lifecycle management with dual approval and 90-day expiration
- Complements (not replaces) Agent Access Governance Monitor (AAM = environment-level, UASD = per-agent)

### Architecture
- Tier 2 pattern: PowerShell + Dataverse + Power Automate (matches 12 shipped solutions)
- 5 Dataverse tables (extended from standard 3-table pattern for exception management)
- Inline agent identity (no dependency on non-existent agentvault table)
- Reuses `fsi_acv_zone` and `fsi_acv_severity` shared option sets
- 6 solution-specific option sets (`fsi_UASD_*`)

### Pitfalls
- BAP API per-agent sharing endpoints not publicly documented (Medium risk, mitigated by spec mandate)
- PATCH endpoint is destructive (overwrites all principals) — Approval default mitigates
- Severity mapping from spec (Critical/High/Medium/Low) to framework (Failed/Error/Warning/GracePeriod) documented explicitly
- No agent inventory Dataverse table — inline fields used instead

## Architecture Recommendation

Follow established Tier 2 solution pattern with 5 phases:
1. Infrastructure (schema, env vars, connection refs)
2. Detection (detector flow, audit script, adaptive card)
3. Remediation & Exceptions (remediation flow, exception flow, canvas app, import script)
4. Deployment & Operations (deploy scripts, export script, deployment guide)
5. Framework Integration (solutions-index, control updates, nav, validation)

## Recommended Phase Sequencing

Linear dependency chain: 1 → 2 → 3 → 4 → 5. Within phases, A/B plans target non-overlapping files.

## Confidence Assessment

| Topic | Confidence | Notes |
|-------|-----------|-------|
| Dataverse schema | High | Well-established pattern across 12 solutions |
| PowerShell scripts | High | Header pattern, #Requires, evidence export all proven |
| Power Automate flows | High | JSON structure pattern from CAA, daily compliance flow |
| BAP API endpoints | Medium | Per-agent sharing endpoints spec-mandated but not publicly documented |
| Canvas App | Medium | Lab-grade; minimal viable app sufficient |
| Framework integration | High | Standard process (solutions-index, control tips, mkdocs nav) |

**Overall Confidence: High** — Stack, patterns, and integration approach all well-proven. BAP API is the only medium-confidence area.
