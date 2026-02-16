# ACM Deep Audit — Security Assessment

**Audit Date:** 2026-02-16
**Solution:** Audit Compliance Manager (ACM) v1.0.0
**Auth Surface:** Managed Identity + Exchange Online + Microsoft Graph + Dataverse Web API + Power Platform Admin API

---

## Auth Surface Analysis

The ACM solution connects to 5 Microsoft services with different auth flows:

| Service | Auth Method | Script(s) | Risk Level |
|---------|------------|-----------|------------|
| Dataverse Web API | Managed Identity (MI) via IMDS | AuditComplianceHelpers.psm1 | Medium |
| Exchange Online | Interactive / Certificate / MI* | Connect-AuditServices.ps1 | High |
| Microsoft Graph | MI token | AuditComplianceHelpers.psm1 | Medium |
| Power Platform Admin | MI token via BAP endpoint | Check/Enable-AuditLogging.ps1 | Medium |
| Azure Automation | MSAL.PS (Certificate/Secret) | Start-*Runbook.ps1 | Medium |

*MI for EXO is documented as a requirement but **not implemented** (see SEC-1).

---

## Security Findings

### SEC-1: Missing Managed Identity Path for Exchange Online (P1)

- **File:** `Connect-AuditServices.ps1`
- **Impact:** Azure Automation runbooks using MI for Dataverse/Graph must fall back to certificate auth for EXO, creating a split auth model. Certificate management is a security surface that MI eliminates.
- **Fix:** Add `Connect-ExchangeOnline -ManagedIdentity -Organization $TenantId` parameter set.

### SEC-2: SecureString Reconverted to Plaintext (P0)

- **File:** `Connect-PowerPlatform.ps1`
- **Impact:** Client secret is converted from SecureString → BSTR → plaintext for `Add-PowerAppsAccount`, then converted **again** for `Get-MsalToken`. Two plaintext copies exist in managed memory simultaneously. `$plainSecret = $null` does NOT clear the string from .NET heap.
- **Fix:** Pass SecureString directly to `Get-MsalToken -ClientSecret` (supports SecureString natively). Minimize plaintext copies.

### SEC-3: OData Filter Injection (P2)

- **File:** `AuditComplianceHelpers.psm1` — `Write-DataverseComplianceRecord`
- **Impact:** `$EnvironmentId` interpolated directly into OData `$filter` query without encoding. Environment IDs are GUIDs in practice (low exploitation risk), but violates defense-in-depth.
- **Fix:** Validate GUID format: `if ($EnvironmentId -notmatch '^[0-9a-fA-F-]{36}$') { throw }`.

### SEC-4: Graph API Email URI Not Validated (P2)

- **File:** `AuditComplianceHelpers.psm1` — `Send-ComplianceNotification`
- **Impact:** `$FromAddress` interpolated into Graph API URL without encoding. Path traversal theoretically possible but Graph API would reject.
- **Fix:** Validate email format or use `[Uri]::EscapeDataString()`.

### SEC-5: Certificate Store Wildcard (P1)

- **File:** `Connect-PowerPlatform.ps1`
- **Impact:** `Get-Item "Cert:\*\$Thumbprint"` searches all stores. If cert exists in multiple stores, returns array → type mismatch. In shared hosting, could match a different user's certificate.
- **Fix:** Use explicit store path `Cert:\LocalMachine\My\` or `Cert:\CurrentUser\My\`.

### SEC-6: Token in Return Object (P2)

- **File:** `Connect-PowerPlatform.ps1`
- **Impact:** Dataverse access token returned as plain string in result hashtable. Accidental logging of the result would expose bearer token.
- **Fix:** Consider `SecureString` return or `ToString()` override that redacts token.

### SEC-7: Vulnerable Python Dependency (P1)

- **File:** `requirements.txt`
- **Impact:** `requests>=2.32.0` allows installing versions 2.32.0–2.32.3, all affected by CVE-2024-47081 (`.netrc` credential leak).
- **Fix:** Pin `requests>=2.32.4`.

### SEC-8: POST Retry Creates Duplicates (P0)

- **File:** `alca_client.py`
- **Impact:** `allowed_methods` includes POST. On transient 500 errors, POST requests are retried, potentially creating duplicate Dataverse records. This is a data integrity issue for compliance tracking.
- **Fix:** Remove POST from retry methods (only retry idempotent operations).

### SEC-9: Canary Value Persistence (P1)

- **File:** `New-CanaryEvent.ps1`
- **Impact:** If the canary cleanup fails (`Set-Mailbox $null` throws for originally-empty attributes, or script is interrupted), the canary value persists on the mailbox indefinitely. An auditor would see unexplained `CustomAttribute15` modifications.
- **Fix:** Use empty string `""` instead of `$null`. Move revert to `finally` block.

### SEC-10: Mutable Module State (P1)

- **File:** `AuditComplianceHelpers.psm1`
- **Impact:** Exported `$ComplianceStatusMap` hashtable is mutable. Any consumer can add/modify/remove entries, corrupting the compliance status mapping for all scripts in the session.
- **Fix:** Use `ReadOnlyDictionary` wrapper.

---

## Risk Matrix

| Risk | Likelihood | Impact | Severity | Finding |
|------|-----------|--------|----------|---------|
| Duplicate compliance records | Medium | High | **P0** | SEC-8 |
| Secret in memory | Low | High | **P0** | SEC-2 |
| Credential leak via CVE | Low | High | **P1** | SEC-7 |
| Canary persistence | Medium | Medium | **P1** | SEC-9 |
| Split auth model | Medium | Medium | **P1** | SEC-1 |
| Wrong cert selected | Low | High | **P1** | SEC-5 |
| Module state corruption | Low | Medium | **P1** | SEC-10 |
| OData injection | Very Low | Medium | **P2** | SEC-3 |
| Token exposure in logs | Low | Medium | **P2** | SEC-6 |
| Graph URI manipulation | Very Low | Low | **P2** | SEC-4 |

---

## Recommendations

1. **Immediate:** Remove POST from retry `allowed_methods` in both Python clients
2. **Immediate:** Pin `requests>=2.32.4` to close CVE-2024-47081
3. **Next release:** Add MI support to `Connect-AuditServices.ps1` for a unified auth model
4. **Next release:** Fix SecureString handling in `Connect-PowerPlatform.ps1`
5. **Planned:** Add input validation for all values interpolated into API URIs

---

*Report: acm-audit-security-assessment.md | Generated: 2026-02-16*
