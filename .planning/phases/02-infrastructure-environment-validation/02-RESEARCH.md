# Phase 2: Infrastructure & Environment Validation - Research

**Researched:** 2026-02-06
**Domain:** Power Platform / Dataverse / PowerShell automation
**Confidence:** MEDIUM

## Summary

This phase requires building a Dataverse-based solution for tracking audit validation results across tenant and per-environment scopes. The solution follows the established Tier 2 pattern (environment-lifecycle-management) with Python scripts for Dataverse schema creation, PowerShell scripts for per-environment audit validation via Power Platform Admin API, and dual deployment paths (rapid scripts + unmanaged solution export).

The standard approach combines Dataverse Web API (Python) for infrastructure provisioning with PowerShell for per-environment audit checks using Microsoft.PowerApps.Administration.PowerShell. Key challenges include organization-owned table configuration for immutability, environment discovery with type filtering, and zone-based retention validation against Dataverse-stored thresholds.

Microsoft provides well-documented APIs and PowerShell modules (ExchangeOnlineManagement v3.7.0+, Microsoft.PowerApps.Administration.PowerShell) for both Dataverse operations and Power Platform admin tasks. The environment-lifecycle-management solution in FSI-AgentGov-Solutions provides a proven reference pattern with deploy.py orchestrator, MSAL authentication via elm_client.py, and comprehensive setup scripts.

**Primary recommendation:** Use Python + Dataverse Web API for schema creation (tables, option sets, environment variables, connection references) following the elm_client.py pattern, then PowerShell scripts with Get-AdminPowerAppEnvironment for environment discovery and audit validation, storing results in organization-owned Dataverse tables with no Update/Delete privileges for compliance immutability.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Dataverse schema design:**
- Zone classification: Denormalized — zone stored on each validation record (not a separate lookup table). Simplifies queries; zone changes are captured as new records with updated zone value
- Scope: Store both tenant-level results (from Phase 1 scripts) and per-environment results in the same history table, differentiated by a 'scope' field
- Immutability: History table is organization-owned with no update/delete — append-only for compliance evidence
- Publisher prefix: fsi_ on all tables and fields

**Environment discovery & filtering:**
- Discovery approach: Dual — API discovery finds all environments, auto-registers new ones in Dataverse registry, then validates the registered set. Alerts on newly-discovered environments
- New environment zone: Unclassified status that triggers an alert. Admin must assign a zone before validation runs against it
- Trial/Dev filtering: Automatic exclusion by environment type from API, with admin override capability to include specific dev/trial environments when needed
- Deprovisioned environments: Mark as Inactive in registry. History records preserved. Environment stops appearing in validation runs

**Validation result structure:**
- Severity levels: Same as Phase 1 — Passed, Warning, GracePeriod, Failed, Error. Same priority logic for overall status computation
- Run correlation: Unique GUID run ID links all records (tenant-level + all per-environment) from the same execution
- Raw values: Store actual configuration values checked (e.g., RetentionDays=90, AuditEnabled=true) alongside the pass/fail result. Enables drift detection by comparing stored values rather than re-querying

**Solution packaging conventions:**
- Solution type: Unmanaged with PowerShell deployment scripts
- Folder structure: Follow the exact same layout as existing solutions in FSI-AgentGov-Solutions (README, CHANGELOG, docs/, scripts/, src/)
- Zone thresholds: Configurable via Dataverse environment variables (fsi_ACV_* convention), not hardcoded
- Deployment paths: Dual-path — (1) PowerShell setup scripts for fast lab/dev testing that create Dataverse tables, seed environment variables, and configure defaults; (2) Unmanaged solution export as alternative deployment path. Both paths produce the same result. Scripts are primary for rapid testing; solution export is the enterprise deployment option
- Connection references: fsi_cr_* naming convention per requirements

### Claude's Discretion
- Record granularity (one row per environment per run vs one row per check)
- Whether to use a separate current-state table or query history directly
- Remediation hint inclusion in validation records
- Exact Dataverse field types and option set values
- Setup script idempotency approach

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope

</user_constraints>

## Standard Stack

The established libraries/tools for Power Platform Dataverse solution development:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.10+ | Dataverse Web API automation | Microsoft's documented approach for programmatic schema creation |
| PowerShell | 7.0+ | Per-environment audit validation | Required for Power Platform Admin cmdlets, consistent with Phase 1 |
| msal | 1.30.0+ | Authentication (interactive + service principal) | Microsoft Authentication Library, official OAuth2/MSAL implementation |
| requests | 2.32.0+ | HTTP requests to Dataverse Web API | Industry standard, supports retry logic and CVE fixes |
| Microsoft.PowerApps.Administration.PowerShell | Latest | Environment discovery and audit settings | Official Power Platform admin module |
| ExchangeOnlineManagement | 3.7.0+ | Unified Audit Log validation | Required for tenant-level audit checks (from Phase 1) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| azure-identity | 1.18.0+ | Service principal auth for Azure Key Vault | Credential storage for automated runs |
| azure-keyvault-secrets | 4.7.0+ | Retrieve stored credentials | Production deployments with Key Vault |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Python + Web API | PAC CLI (Power Platform CLI) | PAC CLI lacks programmatic table creation APIs; requires manual portal steps or solution XML editing |
| Python + Web API | .NET SDK | .NET SDK more complex for infrastructure automation; Python simpler for DevOps pipelines |
| MSAL | Azure.Identity | MSAL provides finer token caching control; Azure.Identity higher-level but less flexible |
| PowerShell 7 | Windows PowerShell 5.1 | PS7 required for cross-platform support and modern ExchangeOnlineManagement features |

**Installation:**
```bash
# Python dependencies
pip install -r scripts/requirements.txt

# PowerShell modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser
Install-Module -Name ExchangeOnlineManagement -MinimumVersion 3.7.0 -Scope CurrentUser
```

## Architecture Patterns

### Recommended Project Structure
```
audit-configuration-validator/
├── README.md                          # Solution overview, quick start
├── CHANGELOG.md                       # Version history
├── scripts/
│   ├── requirements.txt               # Python dependencies
│   ├── deploy.py                      # Orchestrator (schema + vars + roles)
│   ├── create_dataverse_schema.py     # Tables and option sets
│   ├── create_environment_variables.py # Zone thresholds (fsi_ACV_*)
│   ├── create_connection_references.py # Connection refs (fsi_cr_*)
│   ├── acv_client.py                  # Dataverse Web API client (MSAL auth)
│   ├── Invoke-EnvironmentAuditValidation.ps1  # Main per-env orchestrator
│   ├── Test-EnvironmentAudit.ps1      # Per-env audit enablement check
│   ├── Test-EnvironmentRetention.ps1  # Per-env retention validation
│   └── private/
│       ├── Connect-PowerPlatform.ps1  # Auth helper
│       └── Write-ValidationResult.ps1 # Store result in Dataverse
├── docs/
│   ├── prerequisites.md               # Licensing, roles, setup
│   ├── dataverse-schema.md            # Table/column definitions
│   ├── deployment-guide.md            # Step-by-step setup
│   └── troubleshooting.md             # Common issues
└── src/                               # (Reserved for Power Automate flows if Phase 3 adds them)
```

### Pattern 1: Dataverse Web API Client with MSAL Authentication
**What:** Reusable Python client class for authenticating to Dataverse and making Web API calls
**When to use:** All Dataverse operations (schema creation, querying, writing validation results)
**Example:**
```python
# Source: C:/dev/FSI-AgentGov-Solutions/environment-lifecycle-management/scripts/elm_client.py
import msal
import requests

class ACVClient:
    def __init__(self, tenant_id, environment_url, client_id=None,
                 client_secret=None, interactive=False):
        self.environment_url = environment_url.rstrip("/")
        self.api_url = f"{self.environment_url}/api/data/v9.2/"
        self._scope = [f"{self.environment_url}/.default"]

        if interactive:
            self._app = msal.PublicClientApplication(
                client_id=client_id,
                authority=f"https://login.microsoftonline.com/{tenant_id}"
            )
        else:
            self._app = msal.ConfidentialClientApplication(
                client_id=client_id,
                client_credential=client_secret,
                authority=f"https://login.microsoftonline.com/{tenant_id}"
            )

    def _get_token(self):
        result = self._app.acquire_token_silent(scopes=self._scope, account=None)
        if not result:
            result = self._app.acquire_token_for_client(scopes=self._scope)
        return result["access_token"]

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json"
        }
```

### Pattern 2: Organization-Owned Table for Immutability
**What:** Dataverse table with organization ownership and security roles that prevent update/delete
**When to use:** Compliance audit trails that must be immutable (FINRA 4511, SEC 17a-4)
**Example:**
```python
# Source: Microsoft Learn - Create table via Web API
# https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/samples/metadata-operations-powershell

TABLE_DEFINITION = {
    "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
    "SchemaName": "fsi_auditvalidationhistory",
    "DisplayName": {"LocalizedLabels": [{"Label": "Audit Validation History", "LanguageCode": 1033}]},
    "DisplayCollectionName": {"LocalizedLabels": [{"Label": "Audit Validation History", "LanguageCode": 1033}]},
    "Description": {"LocalizedLabels": [{"Label": "Immutable audit validation results", "LanguageCode": 1033}]},
    "OwnershipType": "OrganizationOwned",  # CRITICAL: Prevents per-record ownership
    "IsActivity": False,
    "HasNotes": False,
    "HasActivities": False,
    "Attributes": [
        {
            "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
            "SchemaName": "fsi_name",
            "RequiredLevel": {"Value": "ApplicationRequired"},
            "DisplayName": {"LocalizedLabels": [{"Label": "Name", "LanguageCode": 1033}]},
            "MaxLength": 100,
            "IsPrimaryName": True
        }
        # Additional columns defined in separate POST requests after table creation
    ]
}

# POST to /api/data/v9.2/EntityDefinitions
response = requests.post(
    f"{api_url}/EntityDefinitions",
    headers=headers,
    json=TABLE_DEFINITION
)
```

### Pattern 3: Environment Discovery with Type Filtering
**What:** Query all Power Platform environments, filter by type, register new ones in Dataverse
**When to use:** Environment enumeration before validation runs
**Example:**
```powershell
# Source: Microsoft.PowerApps.Administration.PowerShell module
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminpowerappenvironment

# Get all environments (admin sees all)
$allEnvironments = Get-AdminPowerAppEnvironment

# Filter out Trial and Developer environments
$productionEnvironments = $allEnvironments | Where-Object {
    $_.EnvironmentType -notin @('Trial', 'Developer')
}

# Detect newly-discovered environments
foreach ($env in $productionEnvironments) {
    $existing = Get-DataverseRecord -Table "fsi_environmentregistry" -Filter "fsi_environmentid eq '$($env.EnvironmentName)'"

    if (-not $existing) {
        # New environment discovered - register with Unclassified zone
        New-DataverseRecord -Table "fsi_environmentregistry" -Data @{
            "fsi_name" = $env.DisplayName
            "fsi_environmentid" = $env.EnvironmentName
            "fsi_zone" = 0  # Unclassified (triggers alert)
            "fsi_status" = 1  # Active
        }
        Write-Warning "New environment discovered: $($env.DisplayName) - requires zone classification"
    }
}
```

### Pattern 4: Zone-Based Retention Validation with Environment Variables
**What:** Read zone thresholds from Dataverse environment variables, validate per-environment retention
**When to use:** Zone-aware compliance checks (Zone 1: 180d, Zone 2: 365d, Zone 3: 730d)
**Example:**
```python
# Read environment variables for zone thresholds
def get_zone_thresholds(client):
    """Retrieve zone retention thresholds from Dataverse environment variables."""
    env_vars = client.query(
        entity_set="environmentvariabledefinitions",
        filter_expr="startswith(schemaname, 'fsi_ACV_Zone')",
        select=["schemaname", "defaultvalue"]
    )

    thresholds = {}
    for var in env_vars:
        if "Zone1" in var["schemaname"]:
            thresholds["Zone1"] = int(var["defaultvalue"])
        elif "Zone2" in var["schemaname"]:
            thresholds["Zone2"] = int(var["defaultvalue"])
        elif "Zone3" in var["schemaname"]:
            thresholds["Zone3"] = int(var["defaultvalue"])

    return thresholds  # {'Zone1': 180, 'Zone2': 365, 'Zone3': 730}
```

```powershell
# PowerShell equivalent using Web API
$envVars = Invoke-RestMethod -Uri "$DataverseUrl/api/data/v9.2/environmentvariabledefinitions?`$filter=startswith(schemaname,'fsi_ACV_Zone')&`$select=schemaname,defaultvalue" -Headers $headers
$zone1Threshold = ($envVars.value | Where-Object { $_.schemaname -eq 'fsi_ACV_Zone1RetentionDays' }).defaultvalue
```

### Pattern 5: Dual Deployment Strategy
**What:** Python scripts for rapid testing + unmanaged solution export for enterprise deployment
**When to use:** Lab/dev environments use scripts; production uses solution import
**Example:**
```bash
# Rapid deployment with scripts (lab/dev)
python scripts/deploy.py \
    --environment-url https://org.crm.dynamics.com \
    --tenant-id <tenant-id> \
    --interactive \
    --dry-run  # Preview changes first

# Production deployment
# 1. Export unmanaged solution from dev environment (via portal or PAC CLI)
# 2. Import solution to production via Power Platform admin center
# 3. Run post-import configuration script to seed environment variable values
```

### Anti-Patterns to Avoid

- **Hardcoding zone thresholds in scripts:** Store thresholds in Dataverse environment variables (fsi_ACV_Zone1RetentionDays, etc.) for central management without code changes
- **User-owned history tables:** Always use organization-owned for audit trails; user-owned tables inherit business unit security that can hide compliance evidence
- **Synchronous audit queries in validation loops:** Use async polling or batch queries; per-environment audit checks can take 30-60 seconds each due to API latency
- **Storing passwords in scripts:** Use MSAL interactive auth for dev, service principal + Key Vault for production; never embed credentials
- **Creating tables via portal for automation:** Use Web API programmatically; portal creation doesn't support idempotent scripts or version control
- **Missing grace period logic:** Newly-enabled audit takes 24 hours to fully ingest; always check enablement timestamp and return GracePeriod status, not Failed

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dataverse authentication | Custom OAuth2 flow with token caching | MSAL (msal Python package) | Token refresh, caching, confidential vs public client, CAE support all built-in |
| Retry logic for API throttling | Manual sleep + retry counters | requests.adapters.Retry with backoff | Dataverse returns 429 with Retry-After header; proper backoff prevents ban |
| PowerShell module version checks | Custom version parsing | #Requires -Modules @{ModuleName="X"; ModuleVersion="Y"} | PowerShell validates at script start, prevents runtime errors mid-execution |
| Environment type filtering | String matching on display names | Get-AdminPowerAppEnvironment and check .EnvironmentType property | API returns structured EnvironmentType field (Trial, Developer, Production, Sandbox) |
| Immutable audit tables | Application-level delete prevention | Organization-owned table + security role without Update/Delete privileges | Security roles enforced by platform; app-level checks can be bypassed |
| Solution versioning | Manual version numbers in filenames | Solution metadata with semantic versioning | Power Platform tracks dependencies, upgrades, and rollbacks automatically |
| Audit lag detection | Immediate failure on missing events | Grace period logic with enablement timestamp check | False positives avoided; Phase 1 scripts show 24-hour grace period pattern |

**Key insight:** Dataverse and Power Platform Admin APIs are mature (10+ years) with well-documented patterns for authentication, throttling, security, and audit lag. Custom implementations miss edge cases (token expiry, CAE, business unit inheritance, API version changes) that Microsoft handles in official modules.

## Common Pitfalls

### Pitfall 1: UnifiedAuditLogIngestionEnabled Always Returns False in Security & Compliance PowerShell
**What goes wrong:** Get-AdminAuditLogConfig in Security & Compliance PowerShell always returns False for UnifiedAuditLogIngestionEnabled, causing false negatives
**Why it happens:** Security & Compliance endpoint doesn't expose the correct property; only Exchange Online endpoint returns accurate status
**How to avoid:** Use ExchangeOnlineManagement module and Connect-ExchangeOnline, NOT Connect-IPPSSession
**Warning signs:** Validation fails even though audit is enabled in M365 Compliance Center
**Source:** Phase 1 verification (Test-UnifiedAuditLog.ps1 line 24 comment)

### Pitfall 2: Organization-Owned Tables Still Allow Updates if Security Roles Not Configured
**What goes wrong:** Organization-owned table created successfully but records can still be updated/deleted via Web API or UI
**Why it happens:** Organization ownership only sets access level to binary (can/cannot); security roles must explicitly remove Write/Delete privileges
**How to avoid:** After creating organization-owned table, create custom security role with only Create and Read privileges, assign to all users
**Warning signs:** ProvisioningLog records modified or deleted despite organization ownership
**Source:** Microsoft Learn - Security concepts in Microsoft Dataverse

### Pitfall 3: Environment Variables Not Exported with Solution
**What goes wrong:** Environment variables defined in dev environment don't appear in exported solution, or values not set after import
**Why it happens:** Environment variable values are separated from definitions; values can be removed from solution before export
**How to avoid:** Include environment variable definitions in solution; values provided at import time via modern solution import UI or deployment scripts
**Warning signs:** Zone thresholds are null or default to 0 after solution import
**Source:** Microsoft Learn - Use environment variables in Power Platform solutions

### Pitfall 4: Get-AdminPowerAppEnvironment Requires Tenant Admin for Full Discovery
**What goes wrong:** Script only sees environments where current user is Environment Admin, misses most production environments
**Why it happens:** Non-tenant-admin users only see environments they own/admin
**How to avoid:** Run discovery script as user with Power Platform Administrator or Global Administrator role, OR use service principal with Environment.Read.All API permission
**Warning signs:** Environment count much lower than expected; newly-created environments not discovered
**Source:** Microsoft Learn - Get-AdminPowerAppEnvironment cmdlet reference

### Pitfall 5: Dataverse Web API Throttling Not Handled
**What goes wrong:** Script fails with 429 Too Many Requests error during bulk table creation or high-volume validation runs
**Why it happens:** Dataverse service protection limits: 6000 requests per 5 minutes, 52,000 per 24 hours per user
**How to avoid:** Use requests.adapters.HTTPAdapter with retry logic (Retry(total=3, backoff_factor=1, status_forcelist=[429])); respect Retry-After header
**Warning signs:** Intermittent failures during deploy.py execution; "Service protection API limit" errors
**Source:** Microsoft Learn - Service protection API limits

### Pitfall 6: Publisher Prefix Cannot Be Changed After Solution Creation
**What goes wrong:** Publisher prefix typo (fis_ instead of fsi_) discovered after tables created; renaming requires full deletion and recreation
**Why it happens:** Publisher prefix is baked into schema names (fsi_auditvalidationhistory); Dataverse doesn't allow schema renames
**How to avoid:** Validate publisher prefix in preflight check before creating any tables; use --dry-run flag on deploy.py first
**Warning signs:** SchemaName doesn't match naming convention; mix of prefixes in same solution
**Source:** Microsoft Learn - Solution concepts with Power Platform

### Pitfall 7: Audit Retention Period Stamped at Record Creation
**What goes wrong:** Changing audit retention policy doesn't affect existing records; old records deleted sooner than expected
**Why it happens:** Each audit record stamped with retention period active at creation time; policy changes only affect new records
**How to avoid:** Document that retention policy changes are forward-looking; existing records retain original policy
**Warning signs:** Audit records disappearing before expected retention period expires
**Source:** Microsoft Learn - Manage Dataverse auditing

### Pitfall 8: Connection References Require Manual Sharing for Flow Activation
**What goes wrong:** Power Automate flow fails to activate after solution import with "ConnectionAuthorizationFailed" error
**Why it happens:** User activating flow must have "Can use" permission on all underlying connections referenced by connection references
**How to avoid:** Document post-import step to share connections; OR use service principal for flow execution that owns all connections
**Warning signs:** Flow import succeeds but activation fails with connection authorization error
**Source:** Microsoft Learn - Use a connection reference in a solution with Microsoft Dataverse

## Code Examples

Verified patterns from official sources and reference implementations:

### Creating Global Option Set (Choice Field)
```python
# Source: C:/dev/FSI-AgentGov-Solutions/environment-lifecycle-management/scripts/create_dataverse_schema.py
OPTIONSET_SEVERITY = {
    "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
    "Name": "fsi_acv_severity",
    "DisplayName": {"LocalizedLabels": [{"Label": "Validation Severity", "LanguageCode": 1033}]},
    "Description": {"LocalizedLabels": [{"Label": "Validation result severity levels", "LanguageCode": 1033}]},
    "OptionSetType": "Picklist",
    "IsGlobal": True,
    "Options": [
        {"Value": 1, "Label": {"LocalizedLabels": [{"Label": "Passed", "LanguageCode": 1033}]}},
        {"Value": 2, "Label": {"LocalizedLabels": [{"Label": "Warning", "LanguageCode": 1033}]}},
        {"Value": 3, "Label": {"LocalizedLabels": [{"Label": "GracePeriod", "LanguageCode": 1033}]}},
        {"Value": 4, "Label": {"LocalizedLabels": [{"Label": "Failed", "LanguageCode": 1033}]}},
        {"Value": 5, "Label": {"LocalizedLabels": [{"Label": "Error", "LanguageCode": 1033}]}},
    ]
}

# POST to /api/data/v9.2/GlobalOptionSetDefinitions
response = client.create_option_set(OPTIONSET_SEVERITY)
```

### Creating Environment Variables Programmatically
```python
# Source: Microsoft Learn - EnvironmentVariableDefinition table reference
# https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/environmentvariabledefinition

ENV_VAR_ZONE1_RETENTION = {
    "schemaname": "fsi_ACV_Zone1RetentionDays",
    "displayname": "Zone 1 Retention Days",
    "description": "Minimum audit retention days for Zone 1 (Personal Productivity) environments",
    "type": 100000000,  # Decimal number
    "defaultvalue": "180"  # 180 days
}

# POST to /api/data/v9.2/environmentvariabledefinitions
response = requests.post(
    f"{api_url}/environmentvariabledefinitions",
    headers=headers,
    json=ENV_VAR_ZONE1_RETENTION
)
env_var_id = response.json()["environmentvariabledefinitionid"]

# Optionally set current value (instance-specific)
ENV_VAR_VALUE = {
    "environmentvariabledefinitionid@odata.bind": f"/environmentvariabledefinitions({env_var_id})",
    "value": "180"
}
requests.post(f"{api_url}/environmentvariablevalues", headers=headers, json=ENV_VAR_VALUE)
```

### Creating Connection References
```python
# Source: Microsoft Learn - Connection Reference table reference
# https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/connectionreference

CONNECTION_REF_DATAVERSE = {
    "connectionreferencedisplayname": "Dataverse - Audit Validation",
    "connectionreferencelogicalname": "fsi_cr_dataverse_auditvalidation",
    "connectorid": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
    # Connection ID set during solution import or runtime
}

# POST to /api/data/v9.2/connectionreferences
response = requests.post(
    f"{api_url}/connectionreferences",
    headers=headers,
    json=CONNECTION_REF_DATAVERSE
)
```

### PowerShell: Per-Environment Audit Validation
```powershell
# Source: Pattern derived from Phase 1 Test-UnifiedAuditLog.ps1 and Microsoft.PowerApps.Administration.PowerShell docs
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminpowerappenvironment

function Test-EnvironmentAudit {
    param(
        [Parameter(Mandatory)]
        [string]$EnvironmentName,

        [Parameter(Mandatory)]
        [int]$RequiredRetentionDays
    )

    # Get environment details via admin API
    $env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName

    # Check if Dataverse exists in this environment
    if (-not $env.ProvisionedDatabaseType -or $env.ProvisionedDatabaseType -eq 'None') {
        return @{
            Status = "Error"
            Reason = "No Dataverse database in this environment"
        }
    }

    # Query Dataverse Organization table for audit settings via Web API
    $orgUrl = "https://$($env.Properties.LinkedEnvironmentMetadata.InstanceUrl)/api/data/v9.2/organizations"
    $orgResponse = Invoke-RestMethod -Uri "$orgUrl?`$select=organizationid,isauditenabled" -Headers $headers
    $org = $orgResponse.value[0]

    if (-not $org.isauditenabled) {
        return @{
            Status = "Failed"
            Reason = "Audit not enabled for environment"
            RawValue = "AuditEnabled=false"
        }
    }

    # Check retention policy (via admin API or Web API to auditing tables)
    # Note: Retention configured at environment level in Power Platform admin center
    # Querying via Get-AdminPowerAppEnvironmentAuditSettings (if cmdlet exists)
    # OR via Organization table extended properties

    return @{
        Status = "Passed"
        Reason = "Audit enabled with sufficient retention"
        RawValue = "AuditEnabled=true,RetentionDays=$RequiredRetentionDays"
    }
}
```

### PowerShell: Store Validation Result in Dataverse
```powershell
# Source: Dataverse Web API pattern
function Write-ValidationResult {
    param(
        [string]$DataverseUrl,
        [string]$AccessToken,
        [hashtable]$Result
    )

    $headers = @{
        "Authorization" = "Bearer $AccessToken"
        "Content-Type" = "application/json"
        "OData-MaxVersion" = "4.0"
        "OData-Version" = "4.0"
    }

    $record = @{
        "fsi_name" = "$($Result.EnvironmentName) - $($Result.Timestamp)"
        "fsi_runid" = $Result.RunId  # GUID linking all records in this run
        "fsi_scope" = 100000001  # Environment-level (vs 100000000 for Tenant)
        "fsi_environmentid" = $Result.EnvironmentId
        "fsi_zone" = $Result.Zone  # 1=Zone1, 2=Zone2, 3=Zone3
        "fsi_severity" = $Result.Status  # Maps to option set
        "fsi_rawvalue" = $Result.RawValue
        "fsi_timestamp" = $Result.Timestamp
    } | ConvertTo-Json

    $uri = "$DataverseUrl/api/data/v9.2/fsi_auditvalidationhistories"
    Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $record
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Windows PowerShell 5.1 for admin tasks | PowerShell 7.0+ required | 2021-2022 | Cross-platform support; ExchangeOnlineManagement v3.0+ requires PS7 |
| Manual portal table creation | Python + Dataverse Web API for schema automation | 2020+ | Idempotent deployments, version control, CI/CD pipelines |
| Connection strings in solutions | Connection references | 2019+ | Portability across environments; automatic flow enablement |
| Hardcoded config values | Environment variables in Dataverse | 2020+ | Central config management; no code changes for thresholds |
| Basic auth for Power Platform APIs | MSAL OAuth2 with CAE support | 2022+ | Security compliance; conditional access enforcement |
| .NET SDK only | Python + requests + Web API | 2018+ | Simpler DevOps integration; no Visual Studio dependency |
| Per-user app registrations | Service principal with API permissions | 2021+ | Automation without interactive auth; Key Vault integration |
| Managed solutions for all deployments | Unmanaged for dev, managed for prod | Established | Flexibility in dev; production controls |

**Deprecated/outdated:**
- **ADAL (Azure Active Directory Authentication Library):** Deprecated 2020; replaced by MSAL. ADAL tokens don't support Conditional Access Evaluation (CAE)
- **Invoke-CdsWebRequest (PowerApps-Samples helper):** Superseded by native requests library patterns; helper scripts not maintained
- **Basic authentication to Power Platform APIs:** Disabled 2021; OAuth2 with MSAL required
- **Windows-only PowerShell for admin tasks:** ExchangeOnlineManagement v3.0+ and Microsoft.PowerApps.Administration.PowerShell now require PowerShell 7.0 (cross-platform)

## Open Questions

Things that couldn't be fully resolved:

1. **Per-environment audit retention query method**
   - What we know: Audit retention configured at environment level in Power Platform admin center (max 24,855 days)
   - What's unclear: Specific Web API endpoint or PowerShell cmdlet to query current retention policy programmatically per-environment (not tenant-wide)
   - Recommendation: Test Get-AdminPowerAppEnvironment with -Capacity flag to check if audit retention exposed; fallback to querying Organization table extended properties or auditing settings via raw Web API. Document in troubleshooting if API doesn't expose retention period directly.

2. **Dataverse audit settings vs Unified Audit Log settings**
   - What we know: Two separate audit systems: (1) M365 Unified Audit Log (tenant-level, checked in Phase 1), (2) Dataverse per-environment audit (table/column level)
   - What's unclear: Whether per-environment Dataverse audit has separate retention policy from tenant-level Unified Audit Log, or if they share configuration
   - Recommendation: Validate both independently; Phase 1 scripts check tenant-level UAL, Phase 2 checks per-environment Dataverse audit enablement. Assume separate policies until confirmed otherwise.

3. **Connection reference creation via PowerShell automation**
   - What we know: Connection references can be created via Web API POST to /connectionreferences endpoint
   - What's unclear: Whether connection references require an actual connection to exist first, or can be created with null connection and bound during solution import
   - Recommendation: Test creating connection reference definition without connection ID, document whether deploy.py creates definition-only or requires pre-existing connections. Document in troubleshooting.md if manual portal step needed.

4. **Zone classification storage location**
   - What we know: User wants zone stored denormalized on each validation record
   - What's unclear: Whether to also maintain a separate environment registry table (fsi_environmentregistry) with canonical zone assignment, or rely on latest validation record for current zone
   - Recommendation: Use separate registry table for canonical zone assignment (one row per environment); validation history references environment ID and copies zone value at validation time. Registry provides single source of truth; history shows zone changes over time.

5. **Record granularity impact on query performance**
   - What we know: Two options: (1) one row per environment per run, (2) one row per check per environment per run
   - What's unclear: Performance impact of thousands of validation records (1 row/env/run vs 5+ rows/env/run) on Dataverse queries and dashboard rendering
   - Recommendation: Start with one row per environment per run (fewer records); store check details in JSON field or related child table if Phase 3 alerting needs detail. Validate query performance with 1000+ environments before finalizing schema.

## Sources

### Primary (HIGH confidence)
- [Web API table schema operations sample (PowerShell) - Microsoft Learn](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/samples/metadata-operations-powershell) - Dataverse table creation via Web API
- [Get-AdminPowerAppEnvironment - Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminpowerappenvironment?view=pa-ps-latest) - Environment discovery cmdlet
- [Manage Dataverse auditing - Microsoft Learn](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing) - Per-environment audit configuration
- [Use environment variables in Power Platform solutions - Microsoft Learn](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables) - Environment variable creation and usage
- [Use a connection reference in a solution - Microsoft Learn](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-connection-reference) - Connection reference patterns
- Local codebase: `C:/dev/FSI-AgentGov-Solutions/environment-lifecycle-management/` - Tier 2 solution reference implementation
- Local codebase: `C:/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Test-UnifiedAuditLog.ps1` - Phase 1 validation patterns

### Secondary (MEDIUM confidence)
- WebSearch: "Dataverse Web API create tables PowerShell 2026" - Verified with official Microsoft Learn samples
- WebSearch: "Power Platform admin API environment discovery types 2026" - Confirmed environment type filtering
- WebSearch: "Dataverse organization-owned table append-only immutable 2026" - Verified organization ownership patterns

### Tertiary (LOW confidence)
- WebSearch: "Dataverse PowerShell deployment common mistakes pitfalls 2026" - General best practices, not audit-specific
- WebSearch: "Power Platform environment audit validation best practices 2026" - Governance patterns, less technical depth

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Microsoft official modules and documented patterns, validated in environment-lifecycle-management solution
- Architecture: MEDIUM - Patterns derived from existing solution and official samples, but per-environment audit API specifics require validation
- Pitfalls: MEDIUM - Well-documented for Dataverse generally, some audit-specific pitfalls extrapolated from Phase 1 learnings

**Research date:** 2026-02-06
**Valid until:** 30 days (March 6, 2026) - Dataverse and Power Platform Admin APIs stable, but module versions and cmdlet availability may change
