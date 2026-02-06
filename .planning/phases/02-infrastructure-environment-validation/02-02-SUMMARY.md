---
phase: 02-infrastructure-environment-validation
plan: 02
subsystem: infra
tags: [powershell, power-platform, dataverse, environment-discovery, auth-helper]

# Dependency graph
requires:
  - phase: 02-01
    provides: Dataverse schema (fsi_environmentregistries, fsi_auditvalidationhistories) and API client
provides:
  - Power Platform auth helper (interactive + service principal with cert/secret)
  - Dataverse validation result writer (append-only immutable records)
  - Environment discovery with registry sync and filtering
  - Foundation for environment-scoped audit validation
affects: [02-03, 03-power-automate-integration]

# Tech tracking
tech-stack:
  added:
    - Microsoft.PowerApps.Administration.PowerShell (>=2.0)
    - MSAL.PS (for Dataverse token acquisition)
  patterns:
    - Dot-source auth helpers (Connect-PowerPlatform.ps1)
    - Append-only Dataverse writes (Write-ValidationResult.ps1)
    - Environment registry sync with auto-registration
    - Three-phase discovery (enumerate, sync, filter)
    - Zone-based filtering with Trial/Developer exclusion policy

key-files:
  created:
    - /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/private/Connect-PowerPlatform.ps1
    - /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/private/Write-ValidationResult.ps1
    - /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Invoke-EnvironmentDiscovery.ps1
  modified: []

key-decisions:
  - Use MSAL.PS for Dataverse Web API token acquisition (consistent with industry standard MSAL libraries)
  - Well-known Power Apps client ID (1950a258-227b-4e31-a9cf-717495945fc2) for interactive auth
  - Append-only validation history (Write-ValidationResult supports only POST, no PUT/DELETE)
  - Auto-register new environments as Unclassified/Active (requires admin zone assignment before validation)
  - Preserve deprovisioned environment records by marking Inactive (history preservation per user decision from 02-01)
  - Trial/Developer exclusion policy (excluded by default unless -IncludeTrialDev or fsi_overrideinclude=true)
  - Unclassified zone exclusion (environments require zone classification before validation)

patterns-established:
  - Auth helper pattern: Separate authentication from business logic
  - Option set mapping pattern: String to integer conversion with validation
  - Three-phase discovery pattern: Enumerate → Sync → Filter
  - Registry as source of truth: Discovered environments must be registered before validation
  - Defensive filtering: Multiple exclusion criteria with explicit warnings

# Metrics
duration: 3min
completed: 2026-02-06
---

# Phase 2 Plan 2: Power Platform Auth, Dataverse Write Helper, and Environment Discovery

**One-liner:** Power Platform/Dataverse authentication helpers, append-only validation history writer, and environment discovery with registry sync supporting auto-registration and zone-based filtering.

## Accomplishments

### 1. Power Platform Authentication Helper (Connect-PowerPlatform.ps1)

Created authentication helper for Power Platform Admin API and Dataverse Web API with dual authentication:

**Power Platform Admin API:**
- Uses Add-PowerAppsAccount cmdlet from Microsoft.PowerApps.Administration.PowerShell module
- Supports interactive, service principal with client secret, and service principal with certificate
- Required for Get-AdminPowerAppEnvironment (environment discovery)

**Dataverse Web API:**
- Uses MSAL.PS library for token acquisition
- Constructs scope: `{DataverseUrl}/.default`
- Supports same three authentication modes (interactive, secret, cert)
- Well-known Power Apps client ID for interactive: `1950a258-227b-4e31-a9cf-717495945fc2`

**Return value:**
```powershell
@{
    PowerAppsAuthenticated = $true/$false
    DataverseAccessToken   = "Bearer token string"
    DataverseUrl           = "https://org.crm.dynamics.com"
    TenantId               = "tenant.onmicrosoft.com"
    AuthMethod             = "Interactive" | "ServicePrincipal-Secret" | "ServicePrincipal-Certificate"
}
```

**Security features:**
- SecureString handling for client secrets
- Immediate memory clearing after plaintext conversion
- Certificate store lookup for thumbprint-based auth
- Descriptive error messages for missing modules/permissions

**Lines of code:** 298 (including comprehensive comment-based help)

---

### 2. Dataverse Validation Result Writer (Write-ValidationResult.ps1)

Created append-only writer for fsi_auditvalidationhistory table:

**Immutability enforcement:**
- Only POST operations (no PUT/DELETE/PATCH methods)
- Each validation run creates new records linked by RunId GUID
- Captures point-in-time configuration state

**Option set mappings (exact match to Dataverse schema):**
```powershell
Severity: Passed=1, Warning=2, GracePeriod=3, Failed=4, Error=5
Scope: Tenant=100000000, Environment=100000001
Zone: Unclassified=0, Zone1=1, Zone2=2, Zone3=3
```

**Record naming:**
- Tenant scope: `TENANT-{timestamp}`
- Environment scope: `ENV-{EnvironmentName}-{timestamp}`

**Required parameters:**
- DataverseUrl, AccessToken, RunId, Scope, Severity, ValidationType, RawValue, Reason

**Optional parameters:**
- Zone, EnvironmentId, EnvironmentName, RemediationHint, CheckCount

**Return value:** Created record ID (GUID) on success, throws on failure with HTTP status and response body.

**Lines of code:** 314 (including detailed examples for tenant and environment scoped validations)

---

### 3. Environment Discovery with Registry Sync (Invoke-EnvironmentDiscovery.ps1)

Created EVAL-04 script implementing three-phase discovery:

**Phase A: Enumerate Environments**
- Calls `Get-AdminPowerAppEnvironment` (requires Power Platform Admin or Global Admin role)
- Extracts: EnvironmentId, DisplayName, EnvironmentType, InstanceUrl
- Maps environment types to integers: Production=1, Sandbox=2, Developer=3, Trial=4, Default=5

**Phase B: Sync to Dataverse Registry**
- Query existing fsi_environmentregistries entries
- For new environments:
  - POST new record with fsi_zone=0 (Unclassified), fsi_status=1 (Active)
  - Set fsi_discoveredon to current UTC timestamp
  - Add to $newEnvironments array
  - Emit warning: "requires zone classification before validation"
- For existing environments:
  - PATCH fsi_environmenttype if changed
  - PATCH fsi_status=1 (Active) if previously marked Inactive
- For deprovisioned environments (in registry but not discovered):
  - PATCH fsi_status=2 (Inactive)
  - Preserve record (no DELETE) for historical tracking
  - Add to $inactivatedEnvironments array
  - Emit warning: "marked Inactive"

**Phase C: Filter and Return Validation Set**
- Start with all Active registry entries (fsi_status=1)
- Exclusion filter 1: Unclassified zone
  - Skip if fsi_zone=0
  - Add to $skippedUnclassified array
  - Emit warning: "Assign zone before validation"
- Exclusion filter 2: Trial/Developer environments
  - Skip if fsi_environmenttype=3 (Developer) or 4 (Trial)
  - UNLESS -IncludeTrialDev switch is set
  - UNLESS fsi_overrideinclude=true in registry
  - Add to $skippedTrialDev array
- Return array of environment hashtables: EnvironmentId, DisplayName, Zone, EnvironmentUrl, EnvironmentType

**Return value:**
```powershell
[PSCustomObject]@{
    Timestamp                = "2026-02-06T12:34:56Z"
    TotalDiscovered          = 15
    NewEnvironments          = @("Env1", "Env2")
    InactivatedEnvironments  = @("OldEnv1")
    SkippedUnclassified      = @("NewEnv3")
    SkippedTrialDev          = @("DevEnv1", "TrialEnv2")
    ValidationSet            = @( ... )  # Array of environment hashtables
}
```

**Optional JSON export:** If -OutputPath provided, exports full result as JSON.

**Lines of code:** 436 (including comprehensive help, defensive error handling, and color-coded console output)

---

## Task Commits

| Task | Commit | Description | Files | LOC |
|------|--------|-------------|-------|-----|
| 1 | a190e85 | Add Power Platform auth helper and Dataverse write helper | Connect-PowerPlatform.ps1, Write-ValidationResult.ps1 | 612 |
| 2 | ee93ec6 | Add environment discovery with registry sync and filtering | Invoke-EnvironmentDiscovery.ps1 | 436 |

**Total lines of code:** 1,048

---

## Files Created

| File | Purpose | LOC |
|------|---------|-----|
| `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/private/Connect-PowerPlatform.ps1` | Auth helper for Power Platform Admin API and Dataverse Web API | 298 |
| `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/private/Write-ValidationResult.ps1` | Append-only Dataverse validation result writer | 314 |
| `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Invoke-EnvironmentDiscovery.ps1` | Environment discovery with registry sync (EVAL-04) | 436 |

All files follow regulatory-safe language guidelines (no "ensures", "guarantees", "will prevent", "eliminates risk").

---

## Decisions Made

### 1. MSAL.PS for Dataverse Token Acquisition
**Decision:** Use MSAL.PS library for Dataverse Web API authentication instead of custom OAuth implementations.

**Rationale:**
- Industry-standard MSAL library with active Microsoft support
- Consistent with Phase 1 pattern (ExchangeOnlineManagement uses MSAL internally)
- Handles token caching, refresh, and error handling
- Supports all three authentication modes (interactive, secret, cert)

**Impact:** Adds MSAL.PS module dependency (must be installed: `Install-Module MSAL.PS`)

---

### 2. Well-Known Power Apps Client ID for Interactive Auth
**Decision:** Use `1950a258-227b-4e31-a9cf-717495945fc2` as default client ID for interactive authentication.

**Rationale:**
- Microsoft's first-party Power Apps client ID
- Pre-consented in all tenants (no admin consent required)
- Documented in Microsoft Learn for Power Platform authentication scenarios
- Users can override with custom ClientId if needed (enterprise app registrations)

**Impact:** Simplifies interactive authentication (no app registration required for basic scenarios)

---

### 3. Append-Only Validation History
**Decision:** Write-ValidationResult.ps1 supports ONLY POST operations (no PUT/DELETE/PATCH).

**Rationale:**
- Regulatory requirement: Immutable audit trail
- Point-in-time snapshots of configuration state
- Each validation run creates new records (never modifies historical records)
- Aligns with FSI compliance requirements (SOX 302/404, SEC 17a-4)

**Implementation:** No update/delete code paths, only `Invoke-RestMethod -Method Post`

**Impact:** Validation history grows over time (retention policy required)

---

### 4. Auto-Register New Environments as Unclassified/Active
**Decision:** When discovery finds new environments, automatically register them with Zone=0 (Unclassified) and Status=1 (Active).

**Rationale:**
- Prevents "unknown environment" validation failures
- Forces explicit admin decision on zone classification
- Unclassified environments are excluded from validation (safe default)
- Discovery alerts admins: "requires zone classification before validation"

**Alternative considered:** Require manual registration before validation → rejected (too much friction, admins wouldn't discover new environments)

**Impact:** New environments require one-time zone assignment via Power Automate/manual update

---

### 5. Preserve Deprovisioned Environments (Mark Inactive)
**Decision:** When environments are deprovisioned, mark fsi_status=2 (Inactive) but do NOT delete registry record.

**Rationale:**
- Historical tracking: "What environments existed in Q4 2025?"
- Audit trail preservation: "When was this environment discovered/deprovisioned?"
- Regulatory compliance: FSI firms need historical environment inventory
- User decision from 02-01: Preserve history, don't delete

**Implementation:** PATCH fsi_status=2, no DELETE operations

**Impact:** Registry grows over time (deprovisioned environments remain as historical records)

---

### 6. Trial/Developer Exclusion Policy
**Decision:** Exclude Trial and Developer environments from validation set by default, with two override mechanisms.

**Rationale:**
- Trial environments: Temporary, not production-critical
- Developer environments: Personal sandboxes, not managed
- Reduces noise in validation results (focus on production/sandbox)
- Admins can override via:
  - `-IncludeTrialDev` switch (global override for one run)
  - `fsi_overrideinclude=true` in registry (permanent override for specific environment)

**Implementation:** Check `fsi_environmenttype` (3=Developer, 4=Trial), then check override flags

**Impact:** Default validation set focuses on managed environments (Production, Sandbox, Default)

---

### 7. Unclassified Zone Exclusion
**Decision:** Exclude environments with fsi_zone=0 (Unclassified) from validation set.

**Rationale:**
- Zone classification drives retention thresholds (Zone1=180d, Zone2=365d, Zone3=730d)
- Can't validate without knowing required retention period
- Forces admin to classify environment before validation (intentional friction)

**Alternative considered:** Default to Zone1 thresholds → rejected (could under-report for higher zones)

**Impact:** New environments require zone assignment before first validation

---

## Deviations from Plan

None. Plan executed exactly as written. All required features implemented, all verification criteria met.

---

## Next Phase Readiness

**Plan 02-03 can proceed immediately.** All prerequisites met:

1. ✓ Power Platform authentication helper available (Connect-PowerPlatform.ps1)
2. ✓ Dataverse write helper available (Write-ValidationResult.ps1)
3. ✓ Environment discovery available (Invoke-EnvironmentDiscovery.ps1)
4. ✓ Registry sync pattern established (auto-registration, filtering)

**Plan 02-03 scope:** Environment-scoped audit validation
- Use Connect-PowerPlatform for auth
- Use Invoke-EnvironmentDiscovery to get validation set
- Create environment validators (environment audit, mailbox audit)
- Use Write-ValidationResult to write per-environment findings

**Blockers:** None.

**Known limitations:**
- Requires Power Platform Administrator or Global Administrator role (for Get-AdminPowerAppEnvironment)
- MSAL.PS module must be installed (not included in PowerShell Gallery by default)
- Dataverse schema from 02-01 must be deployed first

---

## Self-Check: PASSED

### Files Created
```
✓ /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/private/Connect-PowerPlatform.ps1
✓ /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/private/Write-ValidationResult.ps1
✓ /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Invoke-EnvironmentDiscovery.ps1
```

### Commits Verified
```
✓ a190e85 — feat(02-02): add Power Platform auth helper and Dataverse write helper
✓ ee93ec6 — feat(02-02): add environment discovery with registry sync and filtering
```

### Verification Criteria
```
✓ #Requires statements present in all scripts
✓ Write-ValidationResult has no PUT/DELETE/PATCH operations (append-only)
✓ Option set mappings match Dataverse schema exactly
✓ Connect-PowerPlatform dot-sourced in Invoke-EnvironmentDiscovery
✓ Get-AdminPowerAppEnvironment called for discovery
✓ Trial/Developer filtering logic present with overrideinclude check
✓ Unclassified zone exclusion present (fsi_zone eq 0)
✓ Deprovisioned handling present (PATCH fsi_status=2)
✓ No prohibited regulatory language ("ensures", "guarantees", "will prevent", "eliminates risk")
```

All files exist. All commits present. All verification criteria met. Plan 02-02 execution complete.
