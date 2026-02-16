# Technical Findings — Solutions Deep Review

**Method:** Read-based static analysis of all 25 solution packages. No live execution. Reviewed authentication, robustness, correctness, and operational readiness.

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **Critical** | 17 | Runtime crashes, data loss, security exposure, completely broken features |
| **High** | 3 | False assurance, least-privilege violations, incorrect scoring |
| **Total tracked** | 20 | (156 total findings identified across all severities; 20 highest-severity tracked here) |

### Systemic Issues (Cross-Cutting)

| Issue | Solutions Affected | Risk Level |
|-------|-------------------|------------|
| No Dataverse pagination | ELM, ACM, FUS, SSC, AAM, HT, RAG, Dashboard (8) | Critical — silent data loss >5000 records |
| Client secret as CLI argument | CAA, DECR, FUS, SSC, SEG, MIME (6+) | High — secret in process listing |
| No Graph API retry/backoff | CAA, DECR, FUS, SSC (4) | High — 429 throttling crashes |
| Wildcard cert store `Cert:\*\` | AAM, CMM, FUS, SSC (4) | Medium — performance/security |
| Option set mismatch (Python 0,1,2,3 vs PS 100000000-range) | FUS, SSC (2) | Critical — zero query results |

---

## Critical Findings (17)

### ACM — Audit Compliance Manager (formerly ALCA)

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 1 | Power Platform auth token acquired but never passed to `Add-PowerAppsAccount` | PP auth fails entirely; no environments remediated | Missing `-AccessToken` parameter | Enable-AuditLogging.ps1:255-256 | Add `-ApplicationId` and `-AccessToken` parameters |
| 2 | HTTP PUT instead of PATCH for EntityDefinitions | Replaces entire entity definition; may wipe metadata | Wrong HTTP method | Enable-AuditLogging.ps1:180-182 | Change to `-Method PATCH` |

### CAA — Conditional Access Automation

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 3 | Client secret printed to console when Key Vault retrieval fails | Secret exposed in terminal history and logs | Catch block falls through to Write-Host | Register-ServicePrincipal.ps1:219 | Remove plaintext output; fail with `throw` |
| 4 | FSI policy filter hardcoded `CA-FSI-*` but templates use `CA-CopilotStudio-*` prefix | Compliance check finds zero policies; reports 100% gap | Policy name patterns don't match templates | Test-PolicyCompliance.ps1:182-184 | Add patterns for all template prefixes |

### DECR — Deny Event Correlation Report

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 5 | Orchestrator passes `-ApiKey` to child script that no longer accepts it | RAI telemetry extraction completely broken | Script migrated to Entra auth; orchestrator not updated | Invoke-DailyDenyReport.ps1:311-313 | Remove `-ApiKey`; align with Entra auth flow |

### DR — DR Testing Framework

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 6 | Recovery steps only execute inside `if ($DryRun)` blocks | Production mode performs ZERO recovery, then reports PASS | Logic is inverted — recovery guarded by DryRun flag | Invoke-DRTest.ps1:94-121 | Move recovery logic to non-DryRun branch |

### ELM — Environment Lifecycle Management

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 7 | Dataverse `query()` never follows `@odata.nextLink` pagination | Silent data loss for tenants with >5000 records | No pagination loop | elm_client.py:124-161 | Add loop following `@odata.nextLink` until null |
| 8 | Manifest hash computed before hash field populated | Integrity verification always fails | Hash includes the hash field itself | export_quarterly_evidence.py:263-268 | Hash file array only, or write to sibling `.sha256` |
| 9 | No retry logic in ELMClient | Transient 429/503 crashes deployment mid-schema | Raw requests without retry adapter | elm_client.py:115-161 | Mount `HTTPAdapter` with `Retry` |

### FUS — File Upload Security

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 10 | Evidence export uses `$null` access token | All API calls send empty Bearer token → 401 | Token not exposed by module | Export-FileUploadEvidence.ps1:148-151 | Expose token from module; pass to evidence export |
| 11 | Dot-sourcing scripts with `Mandatory` params triggers immediate binding | Script crashes at startup before main logic | Dot-source executes inline `param()` blocks | Invoke-FileUploadBaselineCapture.ps1:108-111 | Use call operator `&` with arguments instead |

### MIME — MIME Type Restrictions

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 12 | `EnforcementMode` only checks for `"Block"`; any other value silently passes | Fail-open: typo in config removes all enforcement | No config validation against known enum | ValidateMimeTypePlugin.cs:293 | Validate against known set; throw on unrecognized value |
| 13 | DLP template ships with `TestWithNotifications` mode | If deployed without edit, DLP policy never blocks uploads | Non-blocking default mode | dlp-policy-template.json:19 | Change default to `Enable` or add deployment validation |

### RAG — RAG Source Validator

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 14 | Baseline hash never written to `fsi_baselinehash` field | Every scan passes; drift detection never triggers | Missing baseline write on first run | Invoke-SourceValidation.ps1:117-133 | Set `fsi_baselinehash` on initial baseline capture |

### SEG — Segregation Detector

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 15 | Only queries Entra ID roles; rules reference Power Platform roles | Maker/Checker SoD rules NEVER match; detection non-functional | Missing Power Platform admin API calls | Invoke-SoDScan.ps1:79-97 | Add Power Platform role queries via PAC CLI or admin connector |

### SSC — Session Security Configurator

| # | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|--------|------------|-----------|-----------------|
| 16 | `create_schema()` returns `None`; `deploy.py` crashes on `result["errors"]` | Full deployment pipeline crashes every run | Missing `return` statement | create_dataverse_schema.py:503-508 | Add `return {"errors": [], "created": tables}` |
| 17 | Python schema defines zone options `0,1,2,3` but PowerShell expects `100000001-3` | Every zone-based query returns zero results | Inconsistent option set constants between languages | create_dataverse_schema.py vs PS scripts | Align to Dataverse convention (100000000-range) |

---

## High Findings (3)

| # | Solution | Symptom | Impact | Root Cause | File:Line | Recommended Fix |
|---|---------|---------|--------|------------|-----------|-----------------|
| 18 | COI Testing | All test scenarios return hardcoded `PASS` without calling agent | False assurance; 100% pass regardless of behavior | Agent interaction stubbed out | run_coi_tests.py:252-264 | Implement Direct Line API integration |
| 19 | Dashboard | OAuth scope `admin.services.crm.dynamics.com` | Admin access across ALL environments; violates least privilege | Should use env-specific URL | load_sample_data.py:33 | Use `{env}.crm.dynamics.com` scope |
| 20 | Hallucination Tracker | Severity field assumed string but Dataverse returns integer | Score lookup returns default 1 for all; scores meaningless | Type mismatch in `SEVERITY_WEIGHTS` dict | analyze_patterns.py:37-42 | Use integer keys matching Dataverse values |

---

## Additional Findings Summary (136 Medium/Low — not individually tracked)

| Category | Medium | Low | Examples |
|----------|--------|-----|---------|
| Missing error handling | 18 | 8 | No try/catch around Graph calls, no HTTP status checks |
| Missing logging | 12 | 6 | No structured logging, no correlation IDs |
| Missing WhatIf/DryRun | 8 | — | Destructive operations without preview mode |
| Missing input validation | 10 | 4 | No parameter validation, no config schema checks |
| Hardcoded values | 6 | 8 | Hardcoded tenant IDs, API versions, file paths |
| Missing rollback guidance | 8 | — | No undo procedures documented |
| Missing troubleshooting | 4 | 6 | No troubleshooting section in READMEs |
| Deprecated cmdlet usage | 4 | 2 | Send-MailMessage, old Az module patterns |
| Unsafe secret handling | 6 | — | Secrets in config files, plaintext in logs |
| Missing pagination | 8 | — | Graph API, Dataverse, UAL queries |
| Missing retry/backoff | 6 | — | No 429/throttle handling |
| Other | 10 | 10 | Various code quality, naming, documentation gaps |
