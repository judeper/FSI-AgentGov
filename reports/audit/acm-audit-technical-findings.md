# ACM Deep Audit — Technical Findings

**Audit Date:** 2026-02-16
**Solution:** Audit Compliance Manager (ACM) v1.0.0
**Scope:** 30 scripts (23 PS1 + 1 PSD1 + 7 PY) across `audit-compliance-manager/` in FSI-AgentGov-Solutions

---

## Systemic Issue #1: PowerShell Version Incoherence

Every script in the ACM solution is affected by inconsistent PS version declarations:

| File | Declared Version | Uses PS 7+ Features? | Conflict? |
|------|-----------------|----------------------|-----------|
| AuditComplianceHelpers.psm1 | 7.2 | Yes (Get-Date -AsUTC) | ❌ All callers declaring 5.1 break |
| Connect-PowerPlatform.ps1 | 7.0 | Unknown | ❌ Module dependency on 7.2 |
| Connect-AuditServices.ps1 | — | — | Missing MI path |
| Check-AuditLoggingCompliance.ps1 | 5.1 | Yes (Get-Date -AsUTC) | ❌ Will fail on 5.1 |
| Enable-AuditLogging.ps1 | 5.1 | No (via module) | ❌ Module won't load |
| Test-*.ps1 (all 5) | 7.0 | Yes | OK internally, but ecosystem conflict |
| Start-*Runbook.ps1 (both) | 7.0 | Yes | OK internally |

**Recommendation:** Standardize on `#Requires -Version 7.2` across all files. Replace any PS 5.1 claims. Document PS 7.2 as a prerequisite in README.

---

## Systemic Issue #2: Export-ModuleMember in .ps1 Files

5 files in `scripts/private/` use `Export-ModuleMember` which only works in `.psm1` files. In `.ps1` files, this either does nothing (when run directly) or throws a terminating error (when dot-sourced):

- `Connect-PowerPlatform.ps1`
- `Connect-AuditServices.ps1`
- `Invoke-EnvironmentDiscovery.ps1`
- `Get-ValidationResults.ps1`
- `Compare-ValidationBaseline.ps1`
- `Write-ValidationResult.ps1`
- `New-CanaryEvent.ps1`

**Fix:** Remove all `Export-ModuleMember` lines from `.ps1` files.

---

## Systemic Issue #3: Missing Dataverse Pagination

Only `Get-ValidationResults.ps1` implements `@odata.nextLink` pagination. These scripts silently truncate at 5,000 records:

| Script | Query | Impact |
|--------|-------|--------|
| acv_client.py `query()` | Any Dataverse query | Data loss for tables >5000 rows |
| alca_client.py `query()` | Any Dataverse query | Data loss for tables >5000 rows |
| Invoke-EnvironmentDiscovery.ps1 | `fsi_environmentregistries` (2 queries) | Incomplete env discovery |
| Invoke-EnvironmentAuditValidation.ps1 | `fsi_environmentregistries` (SkipDiscovery) | Incomplete validation |

**Fix:** Add `@odata.nextLink` follow-up loops, replicating the pattern from `Get-ValidationResults.ps1`.

---

## Batch A: Auth & Module Core (25 findings: 2 P0, 12 P1, 11 P2)

### P0

| # | File | Finding | Fix |
|---|------|---------|-----|
| A-1 | AuditComplianceHelpers.psd1 | ProjectUri/LicenseUri point to `github.com/microsoft/` — actual repo is `github.com/judeper/` | Update URIs |
| A-2 | Connect-PowerPlatform.ps1 | ClientSecret converted from SecureString to plain text, then reconverted for MSAL — unnecessary exposure | Pass SecureString directly to `Get-MsalToken -ClientSecret` |

### P1

| # | File | Finding | Fix |
|---|------|---------|-----|
| A-3 | AuditComplianceHelpers.psm1 | Exported hashtable variables are mutable — consumers can corrupt module state | Use `ReadOnlyDictionary` |
| A-4 | AuditComplianceHelpers.psm1 | Non-atomic upsert (GET-then-PATCH) race condition with concurrent runbooks | Use Dataverse native upsert with alternate key |
| A-5 | AuditComplianceHelpers.Tests.ps1 | No tests for `Invoke-DataverseRequest` — central API wrapper untested | Add tests for GET, POST, URL normalization, errors |
| A-6 | AuditComplianceHelpers.Tests.ps1 | No test for `Send-ComplianceNotification` with bad attachment path | Add test, consider `Write-Warning` instead of silent skip |
| A-7 | Connect-PowerPlatform.ps1 | Duplicate `param()` blocks — script-level and function-level with different mandatory declarations | Remove script-level param |
| A-8 | Connect-PowerPlatform.ps1 | `Get-Item Cert:\*\$Thumbprint` wildcard may return array → type mismatch | Use specific store path |
| A-9 | Connect-PowerPlatform.ps1 | `Export-ModuleMember` in .ps1 is non-functional | Remove |
| A-10 | Connect-AuditServices.ps1 | Passes all params regardless of auth method — fragile | Use splatting with relevant params only |
| A-11 | Connect-AuditServices.ps1 | `Disconnect-ExchangeOnline` called twice — second is no-op | Remove duplicate |
| A-12 | Connect-AuditServices.ps1 | `Export-ModuleMember` in .ps1 is non-functional | Remove |
| A-13 | Connect-AuditServices.ps1 | No Managed Identity auth path — cannot use MI for Exchange Online in Azure Automation | Add MI parameter set |
| A-14 | private/*.ps1 | Not referenced from PSD1 NestedModules — consumers must dot-source manually | Add to PSD1 or document requirement |

---

## Batch B: Detection Pipeline (23 findings: 1 P0, 10 P1, 12 P2)

### P0

| # | File | Finding | Fix |
|---|------|---------|-----|
| B-1 | Check-AuditLoggingCompliance.ps1 | Uses `Get-Date -AsUTC` (PS 7.1+) but declares `#Requires -Version 5.1` | Replace with `[DateTime]::UtcNow` or align to 7.2 |

### P1

| # | File | Finding | Fix |
|---|------|---------|-----|
| B-2 | Check-AuditLoggingCompliance.ps1 | `Get-AdminConfig` cmdlet does not exist — Purview audit check always returns `$false` (100% false negatives) | Use `Get-AdminPowerAppEnvironment` or BAP API |
| B-3 | Check-AuditLoggingCompliance.ps1 | `Search-UnifiedAuditLog` not filtered by environment — returns tenant-wide result applied to each env (false positives) | Add env filter via `-FreeText` or JSON parsing |
| B-4 | Invoke-EnvironmentAuditValidation.ps1 | No Dataverse pagination (SkipDiscovery path) — >5000 envs truncated | Add `@odata.nextLink` |
| B-5 | Invoke-EnvironmentAuditValidation.ps1 | GET-then-PATCH race condition on registry updates | Use Dataverse alternate key upsert |
| B-6 | Invoke-TenantAuditValidation.ps1 | Three separate EXO sessions instead of one — wasteful and fragile | Single session in orchestrator |
| B-7 | Invoke-EnvironmentDiscovery.ps1 | No pagination on 2 Dataverse registry queries | Add `@odata.nextLink` |
| B-8 | Invoke-EnvironmentDiscovery.ps1 | `Export-ModuleMember` in .ps1 throws when dot-sourced — breaks orchestrator | Remove |
| B-9 | Invoke-EnvironmentDiscovery.ps1 | `LinkedEnvironmentMetadata.InstanceUrl` null for non-Dataverse envs → downstream failures | Add null check, filter null-URL environments |
| B-10 | Invoke-EnvironmentDiscovery.ps1 | Property mismatch: outputs `DisplayName` but orchestrator reads `EnvironmentName` → blank names | Standardize property names |
| B-11 | Get-ValidationResults.ps1 | `Export-ModuleMember` in .ps1 — will throw when dot-sourced | Remove |

---

## Batch C: Remediation & Evidence (20 findings: 0 P0, 8 P1, 12 P2)

### P1

| # | File | Finding | Fix |
|---|------|---------|-----|
| C-1 | Enable-AuditLogging.ps1 | `systemuser` in CopilotStudioEntities array is a core platform entity, not Copilot Studio — generates high-volume noise | Replace with `conversationtranscript` or `chatbot` |
| C-2 | Export-AuditValidationEvidence.ps1 | `-Encoding utf8` on PS 7+ writes UTF-8 with BOM — breaks cross-platform hash verification | Use `-Encoding utf8NoBOM` |
| C-3 | Export+Test-EvidenceIntegrity | PS version mismatch: Export requires 7.0, Test requires 5.1 — encoding differs, hashes won't match | Standardize both to 7.0 |
| C-4 | Test-EvidenceIntegrity.ps1 | Hash file BOM bytes not trimmed — 64-char length check fails | Add `TrimStart([char]0xFEFF)` |
| C-5 | Write-ValidationResult.ps1 | Record ID extraction from `@odata.context` is incorrect — should use response property | Use `$response.fsi_auditvalidationhistoryid` |
| C-6 | New-CanaryEvent.ps1 | `Set-Mailbox -CustomAttribute15 $null` throws — canary value never cleaned up for empty attributes | Use empty string `""` |
| C-7 | Enable-AuditLogging.ps1 | `ShouldProcess` bypass in helper function — WhatIf protection fragile if called directly | Add `CmdletBinding(SupportsShouldProcess)` to helper |
| C-8 | AuditComplianceHelpers.psm1 | Non-atomic upsert (GET-then-PATCH) race condition with concurrent runbooks | Use Dataverse native upsert with alternate key |

---

## Batch D: Validation Test Scripts (37 findings: 6 P0, 16 P1, 15 P2)

**Key finding:** The 5 `Test-*.ps1` files are **production validation scripts**, not Pester tests. They have **zero Pester test coverage**.

### P0

All 5 validators + the test file require PS 7.0+/7.2, creating systemic version conflict.

### P1 (selected)

| # | File | Finding | Fix |
|---|------|---------|-----|
| D-1 | All 5 validators | Zero Pester test coverage — compliance-critical scripts in FSI with no automated testing | Create `.Tests.ps1` for each |
| D-2 | Test-MailboxAudit.ps1 | Calls `Connect-ExchangeOnlineSession` — function may not exist in helper | Verify function name match |
| D-3 | Test-MailboxAudit.ps1 | Hardcoded sample size of 5 mailboxes — statistically meaningless for large tenants | Make sample size a parameter |

---

## Batch E+F: Runbooks & Python (17 findings: 2 P0, 6 P1, 9 P2)

### P0

| # | File | Finding | Fix |
|---|------|---------|-----|
| EF-1 | acv_client.py | No pagination in `query()` — >5000 records silently dropped | Add `@odata.nextLink` loop |
| EF-2 | alca_client.py | `PUT` in retry `allowed_methods` + POST retries can create duplicate records | Remove POST and PUT from retry methods |

### P1 (selected)

| # | File | Finding | Fix |
|---|------|---------|-----|
| EF-3 | requirements.txt | `requests>=2.32.0` vulnerable to CVE-2024-47081 — should be >=2.32.4 | Pin `requests>=2.32.4` |
| EF-4 | create_dataverse_schema.py | OptionSet values use non-standard 1-5 range instead of 100000000+ | Renumber to publisher option range |
| EF-5 | acv_client.py + alca_client.py | Massive code duplication — diverging bug fixes | Merge into single class with inheritance |
| EF-6 | Start-TenantValidationRunbook.ps1 | Only supports cert auth for Dataverse — missing client-secret path | Add client-secret branching |

---

## Confirmed Correct (v23 Regression)

| Check | Evidence |
|-------|---------|
| ✅ PATCH not PUT | `Enable-AuditLogging.ps1` uses `-Method PATCH` on EntityDefinitions |
| ✅ AccessToken passed | `Add-PowerAppsAccount -AccessToken $ppToken` in both runbooks |
| ✅ Valid RecordTypes | Only `PowerAppsApp` (valid enum value) used |
| ❌ PS 5.1 compat | Module still requires 7.2, scripts mixed 5.1/7.0/7.2 |

---

*Report: acm-audit-technical-findings.md | Generated: 2026-02-16*
