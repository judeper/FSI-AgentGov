# Phase 1 Research: Authentication & Script Modernization

**Researched:** 2026-02-10
**Domain:** App Insights Entra ID migration, shared module architecture, Key Vault credential handling
**Phase Goal:** Migrate all extraction scripts from deprecated authentication to Entra ID, create a shared client module, and modernize scripts to match v4-v8 security standards

---

## Must-Haves for Phase 1

Derived from ROADMAP.md success criteria:

| # | Must-Have | Source Criterion |
|---|----------|-----------------|
| 1 | Export-RaiTelemetry.ps1 authenticates via Connect-AzAccount + Get-AzAccessToken (no x-api-key) | SC-1 |
| 2 | DECClient.psm1 with shared auth helpers, connection management, reusable extraction functions for 3 data sources | SC-2 |
| 3 | All 4 scripts have #Requires statements | SC-3 |
| 4 | All 4 scripts use Azure Key Vault for credential retrieval (no hardcoded secrets) | SC-3 |
| 5 | KQL queries validated and updated if needed for Entra ID token-based API access | SC-4 |

---

## 1. Technical Analysis — Current State

### 1.1 Existing DEC Artifacts

**Framework playbooks** (6 files in `docs/playbooks/advanced-implementations/deny-event-correlation-report/`):

| File | Content |
|------|---------|
| `index.md` | Solution overview, architecture diagram, data source descriptions |
| `purview-audit-extraction.md` | `Export-CopilotDenyEvents.ps1` inline — `Search-UnifiedAuditLog -RecordType CopilotInteraction` |
| `dlp-event-extraction.md` | `Export-DlpCopilotEvents.ps1` inline — `Search-UnifiedAuditLog -RecordType DlpRuleMatch` |
| `app-insights-rai-telemetry.md` | `Export-RaiTelemetry.ps1` inline — REST API with **deprecated x-api-key** |
| `power-bi-correlation.md` | Power BI correlation model, DAX measures, Power Query transformations |
| `deployment-guide.md` | End-to-end deployment with `Invoke-DailyDenyReport.ps1` orchestrator inline |

**Solutions repository** (FSI-AgentGov-Solutions, companion repo — not in this workspace):
- `deny-event-correlation-report/scripts/` — 4 PowerShell scripts
- `deny-event-correlation-report/kql-queries/` — 4 KQL query files
- `deny-event-correlation-report/docs/` — architecture.md, prerequisites.md, troubleshooting.md

**Status:** v1.1.0, Work In Progress in `solutions-index.md`.

### 1.2 Current Script Authentication Methods

| Script | Auth Method | API / Service | Status |
|--------|-------------|---------------|--------|
| `Export-CopilotDenyEvents.ps1` | `Connect-ExchangeOnline` | Purview Unified Audit Log | Working but no `#Requires`, hardcoded credential handling |
| `Export-DlpCopilotEvents.ps1` | `Connect-ExchangeOnline` | Purview DLP Events | Working but no `#Requires`, hardcoded credential handling |
| `Export-RaiTelemetry.ps1` | `x-api-key` header | App Insights REST API | **DEPRECATED — fails March 31, 2026** |
| `Invoke-DailyDenyReport.ps1` | `Get-AzKeyVaultSecret` + above | Orchestrator | Uses Key Vault for some secrets, but passes `$ApiKey` directly |

### 1.3 Current Script Deficiencies

1. **No `#Requires` statements** — None of the 4 scripts declare version or module dependencies
2. **Hardcoded credential patterns** — `ConvertTo-SecureString $exoPass -AsPlainText -Force` (anti-pattern fixed in v2 DEBT-01)
3. **No shared module** — Each script manages its own connection independently
4. **No structured error handling** — Bare `try/catch` without structured error objects
5. **No dry-run/WhatIf** — Unlike v4-v8 solutions
6. **CSV output only** — No Dataverse persistence (Phase 2 scope)

### 1.4 KQL Queries

Three inline KQL queries exist in `app-insights-rai-telemetry.md`:

1. **Daily ContentFiltered Events** — Extracts all `ContentFiltered` events in 24h
2. **Summary by Agent and Category** — `summarize FilterCount = count() by agentId, filterCategory`
3. **High-Severity Events Alert** — 15-minute window for `filterSeverity == "High"`

All queries use `customEvents | where name == "MicrosoftCopilotStudio"` and `eventType == "ContentFiltered"`. **Queries are auth-agnostic** — the same KQL works regardless of whether the REST call uses x-api-key or bearer token. No query changes needed.

---

## 2. Architecture Decisions

### 2.1 Established *Client.psm1 Pattern (v4-v8)

Every v6-v8 Tier 2 solution follows the same shared module pattern:

| Solution | Client Module | Prefix |
|----------|--------------|--------|
| Agent Access Monitor (v6) | `AAMClient.psm1` | `AAM_` |
| Content Moderation Monitor (v7) | `CMMClient.psm1` | `CMM_` |
| File Upload Security (v8) | `FUSClient.psm1` | `FUS_` |

DECClient.psm1 follows this pattern with `DEC_` environment variable prefix.

### 2.2 DECClient.psm1 Structure

DEC is unique: it connects to **three distinct services** rather than Dataverse-only.

```
DECClient.psm1
├── Connect-DECServices          # Master connection (calls the three below)
├── Connect-DECExchangeOnline    # ExchangeOnline for Purview Audit + DLP
├── Connect-DECAppInsights       # Entra ID bearer token for App Insights API
├── Connect-DECDataverse         # Dataverse connection (Phase 2 adds implementation)
├── Get-DECEnvironmentVariable   # Read DEC_ env vars from Dataverse
├── Invoke-DECAppInsightsQuery   # REST wrapper with bearer token, retry, refresh
├── Write-DECDenyEvent           # Stub for Phase 2
├── Write-DECCorrelation         # Stub for Phase 2
└── Write-DECValidationHistory   # Stub for Phase 2
```

Phase 1 implements auth + extraction functions. Phase 2 fills in `Write-DEC*` stubs.

### 2.3 #Requires Patterns

```powershell
# Export-RaiTelemetry.ps1
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="Az.Accounts"; ModuleVersion="3.0.0" }

# Export-CopilotDenyEvents.ps1 / Export-DlpCopilotEvents.ps1
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.0.0" }

# Invoke-DailyDenyReport.ps1
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="Az.Accounts"; ModuleVersion="3.0.0" }, @{ ModuleName="Az.KeyVault"; ModuleVersion="5.0.0" }, @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.0.0" }
```

### 2.4 Key Vault Credential Pattern

Established pattern (v4-v8):
1. Store secrets in Azure Key Vault
2. Retrieve at runtime via `Get-AzKeyVaultSecret`
3. Use RBAC-based access (`Key Vault Secrets User` role) — new KV instances after Feb 1, 2026 enforce Azure RBAC
4. Dual credential pattern for zero-downtime rotation

### 2.5 Entra ID Bearer Token for App Insights

Already documented in `docs/reference/faq.md`:

**Current (deprecated):**
```powershell
$headers = @{ "x-api-key" = $ApiKey }
```

**Target (Entra ID):**
```powershell
$token = (Get-AzAccessToken -ResourceUrl "https://api.applicationinsights.io").Token
$headers = @{ "Authorization" = "Bearer $token" }
```

**Service principal requirements:**
1. App Registration with **Monitoring Reader** role on App Insights resource
2. `Connect-AzAccount -ServicePrincipal` with credentials from Key Vault
3. Bearer token via `Get-AzAccessToken -ResourceUrl "https://api.applicationinsights.io"`

---

## 3. Risk Assessment

### 3.1 x-api-key Deadline — CRITICAL

| Factor | Detail |
|--------|--------|
| Deprecation date | March 31, 2026 |
| Days remaining | ~49 days |
| Impact if missed | `Export-RaiTelemetry.ps1` fails completely |
| Mitigation | AUTH-01 is Plan 01 — execute immediately |
| Contingency | Manual Azure portal KQL queries as fallback |

### 3.2 Breaking Changes — MEDIUM

| Risk | Mitigation |
|------|-----------|
| `Get-AzAccessToken` API surface changes | Pin module version in `#Requires` |
| Token expiry during long extractions (1h default) | Token refresh logic in `Invoke-DECAppInsightsQuery` |
| Service principal RBAC scope misconfiguration | Document exact assignment in PREREQUISITES.md |
| Key Vault RBAC migration (Feb 2027) | Use RBAC from the start |

### 3.3 Testing Concerns — MEDIUM

| Concern | Detail |
|---------|--------|
| No automated tests | v1.1.0 DEC has zero test coverage |
| Requires live tenant | Exchange Online and App Insights queries need actual data |
| Three-service token management | More complex than v6-v8 single-service clients |
| Playbook inline code drift | Framework playbooks embed script code that must stay in sync |

---

## 4. Recommended Approach

### Plan 01-01 (Wave 1): Entra ID Auth Migration (AUTH-01)

Migrate `Export-RaiTelemetry.ps1` from x-api-key to bearer token. Add `#Requires` and Key Vault credential retrieval. Validate KQL queries work with bearer token auth. Independent — no prior plan dependencies.

### Plan 01-02 (Wave 2): DECClient.psm1 (AUTH-02)

Create shared module following `AAMClient`/`CMMClient`/`FUSClient` pattern. Depends on Plan 01-01 to inherit the proven auth pattern. Define full module interface but implement only auth + extraction functions (Phase 2 fills Write stubs).

### Plan 01-03 (Wave 3): Script Hardening (AUTH-03)

Add `#Requires`, Key Vault credentials, structured error handling to all 4 scripts. Depends on both 01-01 (auth pattern) and 01-02 (DECClient.psm1 import). Refactor all scripts to use DECClient module.

---

## 5. Dependencies and Constraints

### External Dependencies

| Dependency | Type | Required For |
|------------|------|-------------|
| `Az.Accounts` module | PowerShell | `Connect-AzAccount`, `Get-AzAccessToken` |
| `Az.KeyVault` module | PowerShell | `Get-AzKeyVaultSecret` |
| `ExchangeOnlineManagement` module | PowerShell | `Search-UnifiedAuditLog` |
| Azure App Registration | Azure resource | Service principal with Monitoring Reader |
| Azure Key Vault | Azure resource | Credential storage |

### Cross-Phase Dependencies

| Phase 1 Output | Consumed By |
|----------------|-------------|
| `DECClient.psm1` connection management | Phase 2 (Dataverse write functions) |
| `DECClient.psm1` exported function signatures | Phase 3 (Power Automate calls) |
| Updated extraction scripts | Phase 4 (Evidence export) |
| `#Requires` statements | Phase 3 (Azure Automation module imports) |

### Constraints

- **Scripts live in FSI-AgentGov-Solutions** — Phase 1 file changes target the companion repo
- **Framework playbooks need parallel updates** — Inline code in playbooks must stay in sync
- **Three-service auth** — DECClient is more complex than v6-v8 single-service clients
- **KQL queries unchanged** — Auth-agnostic; only REST call wrapper changes
- **CSV output preserved** — New Dataverse output is additive (Phase 2)
