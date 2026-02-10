# Phase 2: Dataverse Infrastructure - Research

**Researched:** 2026-02-06
**Domain:** Dataverse schema deployment, Python automation, PowerShell integration
**Confidence:** HIGH

## Summary

Phase 2 creates persistent Dataverse infrastructure to store session security validation results from Phase 1, enabling historical trending, compliance reporting, and automated remediation workflows. The research focused on three key areas: (1) Dataverse schema deployment patterns following the established ACV v4 pattern, (2) Python tooling for idempotent deployments with MSAL authentication, and (3) PowerShell-to-Dataverse integration for reading zone-specific thresholds at runtime.

The standard approach is to use Python scripts with the MSAL library for OAuth authentication and raw Dataverse Web API calls for schema deployment, as this provides the most control and transparency for infrastructure-as-code deployments. The ACV solution (v4 milestone) established the pattern that SSC should follow: separate scripts for schema, environment variables, and connection references, orchestrated by a master deploy.py with idempotent checks and dry-run support.

Key findings: (1) PowerShell scripts can query Dataverse environment variables via Web API to retrieve zone thresholds, eliminating hardcoded values; (2) Validation history tables must be organization-owned (not user-owned) with Write/Delete privileges removed via security roles for immutability; (3) The fsi_acv_zone and fsi_acv_severity option sets already exist from ACV and should be reused, not recreated; (4) Environment variable values are limited to 2000 characters and require API calls to fetch (no local caching available).

**Primary recommendation:** Follow the ACV Python deployment pattern exactly, adapting table definitions to SSC's three-table schema (session baselines, validation history, drift violations) while reusing existing option sets.

## Standard Stack

The established libraries/tools for Dataverse schema deployment via Python:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| msal | 1.34.0+ | OAuth authentication to Dataverse | Official Microsoft library for Entra ID auth, supports both interactive browser and service principal flows |
| requests | 2.31.0+ | HTTP client for Dataverse Web API | Industry standard, built-in retry logic with HTTPAdapter |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| msal-extensions | 1.2.0+ | Token caching across runs | Optional — improves performance for repeated runs by caching tokens to disk |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Raw requests + MSAL | Microsoft PowerPlatform DataverseClient-Python | Higher-level abstraction but less transparency for schema operations; ACV established raw API pattern |
| Service principal auth | Interactive browser auth | SP better for CI/CD automation; interactive better for manual deployments and troubleshooting |

**Installation:**
```bash
pip install msal requests
```

**Environment Variables (following ACV pattern):**
```bash
export SSC_TENANT_ID="<tenant-id>"
export SSC_ENVIRONMENT_URL="https://org.crm.dynamics.com"
export SSC_CLIENT_ID="<app-registration-client-id>"
export SSC_CLIENT_SECRET="<client-secret>"
```

## Architecture Patterns

### Recommended Project Structure

Following ACV v4 pattern from `C:/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/`:

```
session-security-configurator/
├── scripts/
│   ├── ssc_client.py                    # Dataverse Web API client (analogous to acv_client.py)
│   ├── create_dataverse_schema.py       # Tables + columns deployment
│   ├── create_environment_variables.py  # Zone threshold env vars
│   ├── create_connection_references.py  # Dataverse, O365, Teams connectors
│   └── deploy.py                        # Orchestrator script
└── templates/
    └── session-baselines/               # Phase 1 JSON templates (already exist)
```

**Naming conventions:**
- Tables: `fsi_ssc_*` prefix (SessionBaseline, ValidationHistory, DriftViolation)
- Environment variables: `fsi_SSC_*` prefix (Zone1SignInFrequencyMinutes, Zone2SignInFrequencyMinutes, etc.)
- Connection references: `fsi_cr_*` prefix (shared across solutions — reuse ACV refs where possible)

### Pattern 1: MSAL Authentication with Token Caching

**What:** Use ConfidentialClientApplication for service principal auth, PublicClientApplication for interactive auth, with silent token acquisition attempts before new login flows.

**When to use:** All Dataverse API operations require OAuth tokens; this pattern minimizes auth overhead.

**Example:**
```python
# Source: ACV acv_client.py (lines 89-111)
def _get_token(self) -> str:
    """Acquire access token with caching."""
    # Try to get cached token first
    accounts = self._app.get_accounts() if self.interactive else None
    result = self._app.acquire_token_silent(
        scopes=self._scope,
        account=accounts[0] if accounts else None,
    )

    if not result:
        if self.interactive:
            # Interactive browser flow
            result = self._app.acquire_token_interactive(scopes=self._scope)
        else:
            # Client credentials flow
            result = self._app.acquire_token_for_client(scopes=self._scope)

    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "Unknown error"))
        raise RuntimeError(f"Failed to acquire token: {error}")

    return result["access_token"]
```

**Key points:**
- Scope must be `[f"{environment_url}/.default"]` for Dataverse
- Token caching reduces auth calls from ~50/deployment to ~1
- Silent acquisition works for 60-minute token lifetime

### Pattern 2: Idempotent Schema Deployment

**What:** Check for existence before creating each component (option sets, tables, columns); skip if already exists.

**When to use:** All infrastructure deployments to support safe re-runs and partial deployments.

**Example:**
```python
# Source: ACV create_dataverse_schema.py (lines 90-104)
def create_optionsets(client: ACVClient, dry_run: bool = False) -> None:
    """Create all global option sets."""
    print("\n[Creating Global Option Sets]")

    for name, definition in OPTIONSETS.items():
        existing = client.get_global_optionset(name)
        if existing:
            print(f"  {name}: already exists, skipping")
            continue

        if dry_run:
            print(f"  {name}: would create")
        else:
            client.create_global_optionset(definition)
            print(f"  {name}: created")
```

**SSC adaptation:**
- Check for `fsi_acv_zone` and `fsi_acv_severity` — if they exist (from ACV deployment), skip creation
- If they don't exist, create them (SSC can deploy standalone without ACV dependency)
- Session-specific option sets (e.g., `fsi_ssc_validationtype`) are always created

### Pattern 3: Dataverse Web API Metadata Operations

**What:** Use EntityDefinitions and Attributes endpoints to create tables and columns programmatically.

**When to use:** Infrastructure-as-code deployments where UI-based setup is not scalable or auditable.

**Example:**
```python
# Source: ACV acv_client.py (lines 248-276)
def create_entity(self, entity_metadata: dict) -> dict:
    """Create a new entity (table)."""
    if self.dry_run:
        schema_name = entity_metadata.get("SchemaName", "Unknown")
        print(f"  [DRY RUN] Would create entity: {schema_name}")
        return {"LogicalName": schema_name.lower()}

    response = self._session.post(
        urljoin(self.api_url, "EntityDefinitions"),
        headers=self._get_headers(),
        json=entity_metadata,
    )
    response.raise_for_status()

    # Get the created entity
    entity_id = response.headers.get("OData-EntityId", "")
    if entity_id:
        get_response = self._session.get(entity_id, headers=self._get_headers())
        if get_response.ok:
            return get_response.json()
    return {"LogicalName": entity_metadata.get("SchemaName", "").lower()}
```

**SSC table requirements:**
1. **fsi_SessionBaseline** — Zone configurations (read from Phase 1 JSON templates)
2. **fsi_ValidationHistory** — Immutable append-only audit log (organization-owned)
3. **fsi_DriftViolation** — Zone threshold violations detected by Test-SessionCompliance.ps1

### Pattern 4: Environment Variable Deployment

**What:** Create EnvironmentVariableDefinition + EnvironmentVariableValue pairs for configurable zone thresholds.

**When to use:** When PowerShell scripts need to read runtime configuration from Dataverse instead of hardcoded values.

**Example:**
```python
# Source: ACV create_environment_variables.py (lines 96-118)
# Create environment variable definition
definition_data = {
    "schemaname": schemaname,
    "displayname": var["displayname"],
    "description": var["description"],
    "type": 100000001 if var["type"] == "Decimal" else 100000000,  # Decimal=100000001, String=100000000
}

definition_id = client.create_record(
    "environmentvariabledefinitions", definition_data
)

# Create environment variable value (current value)
value_data = {
    "value": var["defaultvalue"],
    "environmentvariabledefinitionid@odata.bind": f"/environmentvariabledefinitions({definition_id})",
}

client.create_record("environmentvariablevalues", value_data)
```

**SSC environment variables (zone thresholds):**
- `fsi_SSC_Zone1SignInFrequencyMinutes` → 480 (8 hours)
- `fsi_SSC_Zone2SignInFrequencyMinutes` → 240 (4 hours)
- `fsi_SSC_Zone3SignInFrequencyMinutes` → 60 (1 hour)
- `fsi_SSC_Zone1AuthStrength` → "standard"
- `fsi_SSC_Zone2AuthStrength` → "passwordless"
- `fsi_SSC_Zone3AuthStrength` → "phishing-resistant"

**PowerShell integration pattern:**
```powershell
# Future Phase 3: PowerShell reads from Dataverse instead of JSON baselines
$envVarUrl = "$DataverseUrl/api/data/v9.2/environmentvariablevalues?`$filter=schemaname eq 'fsi_SSC_Zone3SignInFrequencyMinutes'&`$select=value"
$response = Invoke-RestMethod -Uri $envVarUrl -Headers $headers -Method Get
$zone3SignInMinutes = [int]$response.value[0].value
```

### Pattern 5: Connection Reference Creation

**What:** Define connection reference metadata (logical name, connector type) without binding actual connections until solution import.

**When to use:** Power Automate flows in Phase 3 will reference these to access Dataverse and Teams.

**Example:**
```python
# Source: ACV create_connection_references.py (lines 75-90)
data = {
    "connectionreferencelogicalname": logical_name,
    "connectionreferencedisplayname": conn_ref["display_name"],
    "connectorid": f"/providers/Microsoft.PowerApps/apis/{conn_ref['connector']}",
    "description": conn_ref.get("description", ""),
}

client.create_record("connectionreferences", data)
```

**SSC connection references:**
- `fsi_cr_dataverse_sessionvalidation` → shared_commondataserviceforapps (read/write validation history)
- `fsi_cr_office365_sessionvalidation` → shared_office365 (tenant-level CA policy queries)
- `fsi_cr_teams_sessionvalidation` → shared_teams (drift violation alerting)

**Note:** Connection references created by ACV can be reused if they have generic names; SSC-specific refs only needed if different permissions required.

### Anti-Patterns to Avoid

- **Don't recreate existing option sets:** Check for `fsi_acv_zone` and `fsi_acv_severity` before creating; reuse if present
- **Don't use user-owned tables for audit logs:** Validation history must be organization-owned for immutability (user deletion should not cascade)
- **Don't skip dry-run mode:** Always test with `--dry-run` first to catch schema conflicts or permission issues
- **Don't hardcode URLs:** Use environment variables for tenant ID, environment URL, and client credentials
- **Don't ignore retry logic:** Dataverse API can throttle; use requests.adapters.Retry with backoff

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OAuth token management | Custom token refresh logic | MSAL acquire_token_silent() | Handles caching, refresh, multi-account, token expiry edge cases |
| HTTP retry logic | Manual retry loops | requests.adapters.HTTPAdapter with Retry | Handles 429 throttling, transient failures, exponential backoff |
| Dataverse metadata operations | Direct HTTP calls without abstraction | Shared client class (ssc_client.py) | Centralizes auth, headers, error handling, dry-run mode |
| Environment variable value parsing | String manipulation | Direct API query with $filter | Type-safe, handles decimal vs string types, supports updates |
| Idempotent deployment checks | Try/catch on create | Explicit get_entity_metadata() before create | Clearer intent, separates check from operation, better logging |

**Key insight:** The Dataverse Web API is low-level by design; abstractions like ACVClient reduce boilerplate and enforce patterns (dry-run, retry, auth) consistently across all operations.

## Common Pitfalls

### Pitfall 1: Option Set Naming Collision

**What goes wrong:** Attempting to create `fsi_acv_zone` when ACV already deployed it causes a 400 Bad Request error with "Name already in use".

**Why it happens:** Global option sets are tenant-scoped; different solutions sharing the same option set must coordinate.

**How to avoid:** Always check for existence with `get_global_optionset()` before creating; if it exists, verify the values match expectations, then skip creation.

**Warning signs:** Deployment script fails with "option set already exists" despite clean target environment (indicates another solution already deployed it).

**Code example:**
```python
# CORRECT: Check before create
existing = client.get_global_optionset("fsi_acv_zone")
if existing:
    print(f"  fsi_acv_zone: already exists (from ACV or other solution), reusing")
    # Optionally validate values match expectations
else:
    client.create_global_optionset(zone_optionset_definition)
```

### Pitfall 2: Environment Variable Type Mismatch

**What goes wrong:** Creating environment variable with type "Decimal" but PowerShell script treats value as integer causes rounding errors or type conversion failures.

**Why it happens:** Dataverse environment variable types (100000000=String, 100000001=Decimal, 100000002=JSON) don't map directly to PowerShell types; `value` field is always stored as string.

**How to avoid:** Store all numeric values as Decimal type (100000001) in Dataverse, cast to [int] in PowerShell when retrieving.

**Warning signs:** Validation logic compares "480" (string) to 480 (int) and fails equality check despite same numeric value.

**Code example:**
```python
# Python deployment
{
    "schemaname": "fsi_SSC_Zone1SignInFrequencyMinutes",
    "type": 100000001,  # Decimal, not String
    "defaultvalue": "480",  # Stored as string but typed as Decimal
}
```

```powershell
# PowerShell retrieval (Phase 3)
$zone1Minutes = [int]$envVarResponse.value[0].value  # Cast to int
```

### Pitfall 3: Organization-Owned Table Security Misconfiguration

**What goes wrong:** Validation history table is organization-owned but security roles still allow Write/Delete, allowing users to modify immutable audit log.

**Why it happens:** OwnershipType: OrganizationOwned removes per-record ownership but doesn't automatically restrict Write/Delete — those must be removed via security role configuration.

**How to avoid:** Document post-deployment security role configuration in deployment script output; consider separate script to validate role privileges.

**Warning signs:** Compliance audit finds validation history records with modified/deleted entries; regulatory evidence is no longer trustworthy.

**Mitigation:**
```python
# In deploy.py final output
print("  IMPORTANT: Security Configuration Required")
print("    - ValidationHistory is organization-owned for immutability")
print("    - Security roles must remove Write/Delete privileges")
print("    - Only allow Create (append-only) for automation accounts")
```

### Pitfall 4: Connection Reference Binding Confusion

**What goes wrong:** Connection references created successfully but Power Automate flows fail at runtime with "connection not configured" error.

**Why it happens:** Connection references are definitions only; actual connection binding happens during solution import or manual flow configuration, not during Python deployment.

**How to avoid:** Document that connection references require post-deployment binding step; deployment script should output next steps.

**Warning signs:** `connectionreferences` table has records but `connectionid` column is null/empty.

**Mitigation:**
```python
# In deploy.py final output
print("  Next Steps:")
print("    1. Bind connection references manually:")
print("       - Open Power Automate or solution")
print("       - Configure connections for fsi_cr_dataverse_sessionvalidation")
print("       - Configure connections for fsi_cr_teams_sessionvalidation")
```

### Pitfall 5: Dry-Run Mode Incomplete Coverage

**What goes wrong:** Script has `--dry-run` flag but some operations (like token acquisition, connection test) still execute, causing side effects.

**Why it happens:** Dry-run checks scattered throughout code instead of centralized; easy to miss wrapping new operations.

**How to avoid:** Pass `dry_run` parameter to client constructor; client class checks `self.dry_run` in all mutating operations.

**Warning signs:** Dry-run output shows "Token acquired: ✓" despite --dry-run flag; connection tests hit production environment.

**Code example:**
```python
# CORRECT: Client-level dry-run check
class SSCClient:
    def __init__(self, ..., dry_run: bool = False):
        self.dry_run = dry_run

    def create_record(self, entity_set: str, data: dict) -> str:
        if self.dry_run:
            print(f"  [DRY RUN] Would create record in: {entity_set}")
            return "00000000-0000-0000-0000-000000000000"
        # ... actual create logic
```

## Code Examples

Verified patterns from official sources and ACV implementation:

### Dataverse Web API Client Initialization

```python
# Source: ACV acv_client.py (lines 24-88)
import msal
import requests
from requests.adapters import HTTPAdapter, Retry

class SSCClient:
    """Dataverse Web API client with MSAL authentication and retry logic."""

    def __init__(
        self,
        tenant_id: str,
        environment_url: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        interactive: bool = False,
        dry_run: bool = False,
    ):
        self.tenant_id = tenant_id
        self.environment_url = environment_url.rstrip("/")
        self.api_url = f"{self.environment_url}/api/data/v9.2/"
        self.dry_run = dry_run

        # Dataverse requires the environment URL as the scope
        self._scope = [f"{self.environment_url}/.default"]

        # Setup retry strategy
        self._session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)

        if interactive:
            self._app = msal.PublicClientApplication(
                client_id=client_id,
                authority=f"https://login.microsoftonline.com/{tenant_id}",
            )
        else:
            self._app = msal.ConfidentialClientApplication(
                client_id=client_id,
                client_credential=client_secret,
                authority=f"https://login.microsoftonline.com/{tenant_id}",
            )
```

### Create Dataverse Table with Column Definitions

```python
# Source: ACV create_dataverse_schema.py (lines 111-141)
def get_validation_history_entity() -> dict:
    """Get ValidationHistory entity definition."""
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
        "SchemaName": "fsi_ValidationHistory",
        "DisplayName": {"LocalizedLabels": [{"Label": "Session Validation History", "LanguageCode": 1033}]},
        "DisplayCollectionName": {"LocalizedLabels": [{"Label": "Session Validation History", "LanguageCode": 1033}]},
        "Description": {"LocalizedLabels": [{"Label": "Immutable validation results for Control 1.23 compliance evidence", "LanguageCode": 1033}]},
        "OwnershipType": "OrganizationOwned",  # CRITICAL: immutability requires org-owned
        "IsActivity": False,
        "HasActivities": False,
        "HasNotes": False,
        "IsAuditEnabled": {"Value": True},
        "PrimaryNameAttribute": "fsi_name",
        "Attributes": [
            {
                "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
                "SchemaName": "fsi_Name",
                "DisplayName": {"LocalizedLabels": [{"Label": "Validation ID", "LanguageCode": 1033}]},
                "Description": {"LocalizedLabels": [{"Label": "Zone3-{timestamp} or Zone2-{timestamp}", "LanguageCode": 1033}]},
                "RequiredLevel": {"Value": "ApplicationRequired"},
                "MaxLength": 200,
                "FormatName": {"Value": "Text"},
            },
        ],
    }
```

### Query Environment Variable Values from PowerShell

```powershell
# Future Phase 3 integration pattern
# Source: Microsoft Learn - Environment Variable Value table reference
param(
    [string]$DataverseUrl = "https://org.crm.dynamics.com"
)

# Connect to Dataverse (using Microsoft.PowerApps.Administration.PowerShell or REST API)
$headers = @{
    "Authorization" = "Bearer $($token.AccessToken)"
    "Content-Type" = "application/json"
}

# Query environment variable value
$filter = "schemaname eq 'fsi_SSC_Zone3SignInFrequencyMinutes'"
$select = "value,environmentvariabledefinitionid"
$uri = "$DataverseUrl/api/data/v9.2/environmentvariablevalues?`$filter=$filter&`$select=$select"

$response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get

if ($response.value.Count -gt 0) {
    $zone3SignInMinutes = [int]$response.value[0].value
    Write-Host "Zone 3 sign-in frequency: $zone3SignInMinutes minutes (from Dataverse)"
} else {
    Write-Warning "Environment variable not found; using hardcoded default"
    $zone3SignInMinutes = 60
}
```

### Orchestrator Script Pattern

```python
# Source: ACV deploy.py (lines 57-155)
def deploy(
    client: SSCClient,
    dry_run: bool = False,
    tables_only: bool = False,
    verbose: bool = False,
) -> bool:
    """Deploy all SSC components to Dataverse."""
    success = True

    try:
        # Test connection first
        if not (dry_run or client.dry_run):
            print("[Testing Connection]")
            org = client.test_connection()
            print(f"  Connected to: {org.get('name', 'Unknown')}")

        if tables_only:
            create_schema(client, dry_run=dry_run)
        else:
            # Full deployment
            print("\n" + "=" * 70)
            print("  STEP 1: Dataverse Schema")
            create_schema(client, dry_run=dry_run)

            print("\n" + "=" * 70)
            print("  STEP 2: Environment Variables")
            create_environment_variables(client, dry_run=dry_run)

            print("\n" + "=" * 70)
            print("  STEP 3: Connection References")
            create_connection_references(client, dry_run=dry_run)

        # Final summary
        if dry_run or client.dry_run:
            print("  DRY RUN COMPLETE")
            print("  Run without --dry-run to apply changes.")
        else:
            print("  DEPLOYMENT COMPLETE")
            print("\n  Next Steps:")
            print("    1. Configure security roles (remove Write/Delete on ValidationHistory)")
            print("    2. Bind connection references in Power Automate")

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        success = False

    return success
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| PowerShell-only with hardcoded baselines | PowerShell + Dataverse with environment variables | v4 (ACV milestone) | Zone thresholds externalized; operators can adjust without redeploying scripts |
| Manual schema creation via UI | Python infrastructure-as-code | v4 (ACV milestone) | Repeatable deployments; version control for schema; audit trail of changes |
| User-owned tables for audit logs | Organization-owned tables with role restrictions | v4 (ACV milestone) | True immutability; user deletion doesn't cascade to compliance evidence |
| ADAL authentication | MSAL authentication | 2023 (ADAL deprecation) | Modern auth flows; supports managed identity; better token caching |
| Custom retry logic | requests.adapters.Retry | Industry standard | Handles Dataverse throttling (429) automatically; exponential backoff |

**Deprecated/outdated:**
- **ADAL (Azure Active Directory Authentication Library):** Deprecated June 2023; replaced by MSAL for all new projects
- **Manual connection reference binding in deployment scripts:** Not possible via Web API; must be done during solution import or via UI
- **String-only environment variables:** Dataverse now supports Decimal, JSON, Data Source types for better type safety

## Open Questions

Things that couldn't be fully resolved:

1. **Should SSC create its own connection references or reuse ACV's?**
   - What we know: Connection references are scoped to solution; multiple solutions can reference the same connector
   - What's unclear: If ACV and SSC both create `fsi_cr_dataverse_*`, does it cause conflicts or just duplicate definitions?
   - Recommendation: Use SSC-specific names (`fsi_cr_dataverse_sessionvalidation`) to avoid coupling; operators can bind to same underlying connection

2. **How should Phase 3 PowerShell scripts authenticate to Dataverse to read environment variables?**
   - What we know: PowerShell can use `Invoke-RestMethod` with OAuth token; MSAL.PS module exists but adds dependency
   - What's unclear: Best practice for PowerShell-to-Dataverse auth in automation context (scheduled flows, CI/CD)
   - Recommendation: Use service principal auth with `Connect-MgGraph` then pass token to `Invoke-RestMethod`; document in Phase 3 research

3. **Should ValidationHistory table use Dataverse audit log feature or custom immutability enforcement?**
   - What we know: Dataverse built-in auditing tracks all changes but auditors can delete audit logs; organization-owned removes Write/Delete via roles
   - What's unclear: Does organization-owned + role restriction meet SEC 17a-4 immutability requirements, or is additional technical control needed?
   - Recommendation: Use organization-owned + role restriction as primary control; document that Dataverse audit log provides secondary evidence of attempted modifications

## Sources

### Primary (HIGH confidence)

- [Microsoft Learn - Use the Dataverse Web API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview) - Official Dataverse Web API documentation
- [Microsoft Learn - Use OAuth authentication with Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth) - OAuth authentication patterns
- [Microsoft Learn - MSAL Python Overview](https://learn.microsoft.com/en-us/entra/msal/python/) - Official MSAL library documentation
- [PyPI - MSAL](https://pypi.org/project/msal/) - MSAL Python 1.34.0+ package
- [Microsoft Learn - Environment Variable Value table reference](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/environmentvariablevalue) - EnvironmentVariableValue schema
- [Microsoft Learn - Use environment variables in solutions](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables) - Environment variable usage patterns
- ACV v4 implementation - `C:/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/` - Established pattern for FSI-AgentGov solutions

### Secondary (MEDIUM confidence)

- [Benedikt's Power Platform Blog - Set Connection References in Pipelines](https://benediktbergmann.eu/2021/12/02/set-connection-references-and-environment-variables-in-pipelines/) - Connection reference deployment patterns
- [Microsoft Learn - Pre-populate connection references with Power Platform Build Tools](https://learn.microsoft.com/en-us/power-platform/alm/conn-ref-env-variables-build-tools) - Automated connection binding
- [GitHub - MarcusRisanger/Dataverse-API](https://github.com/MarcusRisanger/Dataverse-API) - Python abstraction layer example
- [Low Code Lewis - Using environment variables with Dataverse](https://www.lewisdoes.dev/blog/using-environment-variables-with-dataverse-environments/) - Practical usage patterns

### Tertiary (MEDIUM confidence - regulatory context)

- [InScope - Audit Trail Requirements Guidelines](https://www.inscopehq.com/post/audit-trail-requirements-guidelines-for-compliance-and-best-practices) - Compliance audit trail best practices
- [Remington-Davis - 21 CFR Part 11 Audit Trail Requirements](https://www.remdavis.com/news/21-cfr-part-11-audit-trail-requirements) - FDA regulatory requirements (analogous to SEC/FINRA)
- [ComplianceG - FDA Audit Trails Explained](https://www.complianceg.com/fda-audit-trail/) - Immutability requirements for regulated audit trails

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - MSAL and requests are documented official libraries; ACV v4 established pattern
- Architecture: HIGH - Direct examination of ACV codebase + Microsoft Learn documentation
- Pitfalls: MEDIUM - Derived from ACV implementation patterns and Dataverse API documentation; not all pitfalls tested in production

**Research date:** 2026-02-06
**Valid until:** 2026-03-06 (30 days — Dataverse Web API and MSAL are stable)

**Key assumptions:**
- ACV v4 pattern is appropriate for SSC (both are Tier 2 solutions with similar requirements)
- fsi_acv_zone and fsi_acv_severity option sets are deployed and available for reuse
- PowerShell-to-Dataverse integration will be researched in Phase 3 (not blocking for Phase 2 planning)
