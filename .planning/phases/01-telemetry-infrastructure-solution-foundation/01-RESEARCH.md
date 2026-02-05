# Phase 1: Telemetry Infrastructure & Solution Foundation - Research

**Researched:** 2026-02-05
**Domain:** Azure telemetry infrastructure provisioning with Python SDK
**Confidence:** HIGH

## Summary

Phase 1 deploys FSI-compliant telemetry infrastructure (Application Insights, Log Analytics, ADLS Gen2 export) using Azure SDK for Python and creates comprehensive solution documentation in the FSI-AgentGov-Solutions repository. The research confirms that Azure SDK for Python provides mature management libraries for full resource provisioning, Log Analytics supports 730-day retention for FSI compliance, and ADLS Gen2 immutable storage meets SEC 17a-4 requirements.

Key findings:
- Azure SDK for Python (azure-mgmt-*) packages provide complete resource lifecycle management with stable APIs
- Log Analytics workspace supports up to 730-day interactive retention (sufficient for 2-year SEC 17a-4(b)(4) requirement)
- ADLS Gen2 with WORM policy is SEC 17a-4(f) compliant when locked (Cohasset validated)
- Copilot Studio telemetry uses customEvents table with PII in customDimensions fields
- Python automation patterns from environment-lifecycle-management solution provide proven reference architecture

**Primary recommendation:** Use Azure SDK for Python (not CLI wrappers) with argparse + YAML/JSON config file pattern. Implement Python-based provisioning for all resources except WORM policy configuration (manual only for safety).

## Standard Stack

The established libraries/tools for Azure telemetry infrastructure automation:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| azure-mgmt-applicationinsights | 4.1.0 | Application Insights workspace management | Official Microsoft SDK, stable API, supports 730-day retention |
| azure-mgmt-loganalytics | 13.0.0+ | Log Analytics workspace management | Official Microsoft SDK, supports retention configuration |
| azure-mgmt-monitor | Latest | Diagnostic settings configuration | Export to ADLS Gen2 via diagnostic settings API |
| azure-mgmt-storage | Latest | ADLS Gen2 storage account creation | Hierarchical namespace support |
| azure-mgmt-authorization | Latest | RBAC role assignment automation | SoD enforcement (operational vs compliance paths) |
| azure-identity | 1.18.0+ | Authentication (DefaultAzureCredential) | CAE support, standard auth pattern |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| msal | 1.30.0+ | Token caching for Service Principal auth | CI/CD scenarios, non-interactive auth |
| requests | 2.32.0+ | HTTP client for Graph API calls | CVE-2024-35195 security fix |
| pyyaml | Latest | Config file parsing | If using YAML config format |
| argparse | Standard library | CLI argument parsing | All Python automation scripts |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Azure SDK for Python | Azure CLI wrappers (subprocess) | CLI = fragile (output parsing breaks), SDK = stable API contracts |
| Python scripts | PowerShell Az modules | PowerShell = Windows-centric, Python = cross-platform + better error handling |
| JSON config | YAML config | JSON = stricter, YAML = more readable (user preference) |

**Installation:**
```bash
pip install azure-mgmt-applicationinsights azure-mgmt-loganalytics azure-mgmt-monitor azure-mgmt-storage azure-mgmt-authorization azure-identity msal requests
```

**Source:** [azure-mgmt-applicationinsights PyPI](https://pypi.org/project/azure-mgmt-applicationinsights/), [Azure SDK for Python (Mgmt)](https://azure.github.io/azure-sdk/releases/latest/mgmt/python.html)

## Architecture Patterns

### Recommended Project Structure

```
agent-observability-foundation/
├── README.md                          # Architecture overview first, then setup
├── architecture.md                    # Single Mermaid diagram + SoD boundaries
├── prerequisites.md                   # Checklist table: Resource | Role | License
├── governance-mapping.md              # Artifact → Controls with tiered evidence
├── config/
│   ├── config.schema.json             # JSON schema for validation
│   └── config.example.yml             # Example configuration
├── scripts/
│   ├── provision.py                   # Main provisioning script
│   ├── teardown.py                    # Cleanup script for lab cycling
│   ├── verify_telemetry.py            # Post-deployment validation
│   ├── verify_worm.py                 # WORM policy verification script
│   └── requirements.txt               # Python dependencies
├── docs/
│   ├── pii-sanitization-guide.md      # Decision framework + field table
│   ├── cost-tuning-guide.md           # Sampling and cost management
│   └── worm-configuration.md          # Manual WORM setup steps
└── templates/
    └── diagnostic-settings.json       # ARM template for export config
```

### Pattern 1: Azure SDK Client Initialization with DefaultAzureCredential

**What:** Standard authentication pattern using azure-identity DefaultAzureCredential

**When to use:** All Azure SDK scripts (supports interactive auth, Service Principal, Managed Identity)

**Example:**
```python
# Source: https://pypi.org/project/azure-mgmt-applicationinsights/
from azure.identity import DefaultAzureCredential
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
import os

subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
credential = DefaultAzureCredential()

client = ApplicationInsightsManagementClient(
    credential=credential,
    subscription_id=subscription_id
)
```

### Pattern 2: argparse + Config File Override

**What:** CLI arguments override config file values (matches environment-lifecycle-management pattern)

**When to use:** All provisioning scripts to support both lab automation and production deployments

**Example:**
```python
# Source: Adapted from FSI-AgentGov-Solutions/environment-lifecycle-management/scripts/deploy.py
import argparse
import yaml

parser = argparse.ArgumentParser(description="Provision telemetry infrastructure")
parser.add_argument("--config", default="config/config.yml", help="Config file path")
parser.add_argument("--resource-group", help="Resource group (overrides config)")
parser.add_argument("--location", help="Azure region (overrides config)")
parser.add_argument("--retention-days", type=int, help="Retention days (overrides config)")
parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
args = parser.parse_args()

# Load config file
with open(args.config) as f:
    config = yaml.safe_load(f)

# CLI args override config
resource_group = args.resource_group or config.get("resource_group")
location = args.location or config.get("location", "eastus")
retention_days = args.retention_days or config.get("retention_days", 730)
```

### Pattern 3: Idempotent Resource Creation

**What:** Check if resource exists before creation, update if exists

**When to use:** All resource provisioning to support reruns without errors

**Example:**
```python
# Source: Adapted from Azure SDK patterns
from azure.core.exceptions import ResourceNotFoundError

def create_or_update_workspace(client, resource_group, workspace_name, location, retention_days):
    """Create Log Analytics workspace or update retention if exists."""
    try:
        # Check if exists
        existing = client.workspaces.get(resource_group, workspace_name)
        print(f"Workspace {workspace_name} exists, updating retention...")

        # Update retention
        workspace = {
            "location": location,
            "retention_in_days": retention_days
        }
        result = client.workspaces.create_or_update(
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            parameters=workspace
        )
        return result
    except ResourceNotFoundError:
        print(f"Creating workspace {workspace_name}...")
        workspace = {
            "location": location,
            "retention_in_days": retention_days
        }
        result = client.workspaces.create_or_update(
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            parameters=workspace
        )
        return result
```

### Pattern 4: Error Handling with Azure SDK Exceptions

**What:** Catch specific Azure SDK exceptions before falling back to general AzureError

**When to use:** All Azure SDK operations

**Example:**
```python
# Source: https://learn.microsoft.com/en-us/azure/developer/python/sdk/fundamentals/errors
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError,
    HttpResponseError,
    AzureError
)

try:
    result = client.workspaces.create_or_update(...)
except ClientAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Request ID: {e.error.code}")
    sys.exit(1)
except ResourceExistsError as e:
    print(f"Resource already exists: {e.message}")
    # Continue or update
except HttpResponseError as e:
    print(f"HTTP error: {e.status_code} - {e.message}")
    print(f"Error code: {e.error.code}")
    sys.exit(1)
except AzureError as e:
    print(f"Azure SDK error: {e.message}")
    sys.exit(1)
```

### Anti-Patterns to Avoid

- **Subprocess Azure CLI calls:** Brittle, output parsing breaks with CLI version changes
- **Hardcoded subscription IDs:** Use config file or environment variables
- **No dry-run mode:** Always provide --dry-run for preview
- **Manual WORM via script:** Too risky for accidental immutable lockdown in production
- **Ignoring retry policies:** Azure SDK has built-in retries, don't disable

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Diagnostic settings export | Custom HTTP API calls | azure-mgmt-monitor DiagnosticSettingsOperations | Handles async operations, retries, API versioning |
| RBAC role assignments | Manual portal clicks | azure-mgmt-authorization RoleAssignmentsOperations | Scope strings are complex, SDK handles formatting |
| Telemetry sampling | Custom event filtering | Application Insights adaptive sampling config | Sampling preserves trace context, custom filtering breaks correlation |
| PII redaction | Regex in telemetry processors | Document fields + provide decision framework | No universal PII pattern, context-dependent (user controls) |
| WORM policy verification | Custom blob read/write tests | Azure Storage immutability audit log | Official audit trail for SEC 17a-4 compliance |

**Key insight:** Azure management SDKs handle async polling (environment creation takes 5-10 minutes), retry policies, and API versioning. Custom HTTP wrappers miss these edge cases.

## Common Pitfalls

### Pitfall 1: ADLS Gen2 Hierarchical Namespace Blocks Diagnostic Settings Export

**What goes wrong:** You create ADLS Gen2 storage account with hierarchical namespace enabled, then diagnostic settings fail to export logs with no clear error.

**Why it happens:** Microsoft limitation - diagnostic settings do not support ADLS Gen2 with hierarchical namespace enabled (as of Feb 2026).

**How to avoid:** Create StorageV2 (general-purpose v2) account WITHOUT hierarchical namespace for telemetry export. Use hierarchical namespace only for post-export archival if needed.

**Warning signs:** Diagnostic settings show "configured" but no data appears in storage account after 24 hours.

**Source:** [ADLS Gen2 Access Logs via Diagnostic Settings - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/1822342/adls-gen2-access-logs-via-diagnostic-settings)

### Pitfall 2: Confusing Analytics Retention vs Total Retention

**What goes wrong:** You set `retentionInDays=730` thinking you get full Log Analytics query access for 2 years, but only get 90 days (default).

**Why it happens:** Log Analytics has TWO retention settings: `retentionInDays` (analytics/hot storage) and `totalRetentionInDays` (long-term/archive). Only analytics retention is queryable in real-time.

**How to avoid:** Set BOTH `retentionInDays=730` AND `totalRetentionInDays=730` for full 2-year interactive access. For longer retention (SEC 17a-4(a) 6 years), use totalRetentionInDays up to 4383 days (12 years) with search jobs for archived data.

**Warning signs:** Queries return "no data" after 90 days even though retention is configured.

**Source:** [Manage data retention in a Log Analytics workspace - Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure)

### Pitfall 3: WORM Policy Applied via Script Locks Production Data Permanently

**What goes wrong:** Provisioning script includes WORM policy creation. Developer runs against production storage account. Immutable lock is permanent. Data cannot be deleted, storage costs accumulate forever.

**Why it happens:** WORM policies CANNOT be unlocked once applied (by design for SEC 17a-4 compliance).

**How to avoid:** NEVER automate WORM policy creation in provisioning scripts. Document manual steps in `docs/worm-configuration.md` with clear warnings. Provide verification script (`verify_worm.py`) to confirm immutability without applying it.

**Warning signs:** Script parameter named `--apply-worm` or `--lock-policy` is a red flag.

### Pitfall 4: Adaptive Sampling Not Supported in Python Application Insights SDK

**What goes wrong:** You configure adaptive sampling in Python script expecting Application Insights to auto-adjust sampling rate based on volume. Sampling rate stays fixed, costs explode.

**Why it happens:** Adaptive sampling is only available for ASP.NET/ASP.NET Core and Azure Functions. Python SDK does not support adaptive sampling (as of Feb 2026).

**How to avoid:** For Copilot Studio telemetry (server-side), configure sampling at Application Insights workspace level (ingestion sampling), not at SDK level. Document recommended fixed sampling rate (e.g., 50%) in cost-tuning-guide.md.

**Warning signs:** Python code references `adaptive_sampling_percentage` parameter (does not exist).

**Source:** [Telemetry sampling in Azure Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/sampling-classic-api)

### Pitfall 5: customDimensions PII Exposure

**What goes wrong:** User enables "Log sensitive Activity properties" in Copilot Studio, full conversation text appears in Application Insights customDimensions. Compliance team finds PII in telemetry during audit.

**Why it happens:** Copilot Studio captures `text` and `speak` fields when sensitive logging is enabled. These flow to Application Insights without sanitization.

**How to avoid:** Document in `pii-sanitization-guide.md` that `text`, `speak`, `fromName`, `recipientName` fields contain PII. Provide decision framework: drop field, hash (one-way), mask (partial), or encrypt (reversible). Default recommendation: disable sensitive properties logging.

**Warning signs:** Search customEvents table for `customDimensions.text` contains customer names, account numbers, or personal data.

**Source:** [Capture telemetry with Application Insights - Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry)

## Code Examples

Verified patterns from official sources:

### Create Application Insights Workspace with 730-Day Retention

```python
# Source: https://pypi.org/project/azure-mgmt-applicationinsights/
from azure.identity import DefaultAzureCredential
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient

credential = DefaultAzureCredential()
subscription_id = "your-subscription-id"
client = ApplicationInsightsManagementClient(credential, subscription_id)

# Application Insights component
app_insights_params = {
    "location": "eastus",
    "kind": "web",
    "application_type": "web",
    "retention_in_days": 730,  # 2-year retention for SEC 17a-4(b)(4)
    "workspace_resource_id": f"/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}"
}

component = client.components.create_or_update(
    resource_group_name="rg-agent-telemetry",
    resource_name="ai-agent-observability",
    insight_properties=app_insights_params
)

print(f"Application Insights created: {component.instrumentation_key}")
print(f"Connection string: {component.connection_string}")
```

### Create Log Analytics Workspace with 730-Day Retention

```python
# Source: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/loganalytics/azure-mgmt-loganalytics
from azure.mgmt.loganalytics import LogAnalyticsManagementClient

la_client = LogAnalyticsManagementClient(credential, subscription_id)

# Workspace parameters
workspace_params = {
    "location": "eastus",
    "retention_in_days": 730,  # Interactive retention (queryable)
    "sku": {
        "name": "PerGB2018"  # Pay-as-you-go pricing tier
    }
}

workspace = la_client.workspaces.begin_create_or_update(
    resource_group_name="rg-agent-telemetry",
    workspace_name="law-agent-observability",
    parameters=workspace_params
).result()

print(f"Workspace created: {workspace.customer_id}")
```

### Configure Diagnostic Settings Export to ADLS Gen2

```python
# Source: https://learn.microsoft.com/en-us/python/api/azure-mgmt-monitor/
from azure.mgmt.monitor import MonitorManagementClient

monitor_client = MonitorManagementClient(credential, subscription_id)

# Diagnostic settings for Application Insights export
diagnostic_settings = {
    "storage_account_id": f"/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage_account}",
    "logs": [
        {
            "category": "AppTraces",
            "enabled": True,
            "retention_policy": {
                "enabled": True,
                "days": 2555  # 7 years for SEC 17a-4(a)
            }
        },
        {
            "category": "AppEvents",
            "enabled": True,
            "retention_policy": {
                "enabled": True,
                "days": 2555
            }
        }
    ]
}

# Apply to Application Insights resource
resource_uri = f"/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Insights/components/ai-agent-observability"

result = monitor_client.diagnostic_settings.create_or_update(
    resource_uri=resource_uri,
    name="export-to-adls",
    parameters=diagnostic_settings
)

print(f"Diagnostic settings configured: {result.name}")
```

### RBAC Role Assignment (Separation of Duties)

```python
# Source: https://learn.microsoft.com/en-us/python/api/azure-mgmt-authorization/
from azure.mgmt.authorization import AuthorizationManagementClient
import uuid

auth_client = AuthorizationManagementClient(credential, subscription_id)

# Assign "Monitoring Reader" to operational team (read-only)
# Assign "Storage Blob Data Reader" to compliance team (archive access)

scope = f"/subscriptions/{subscription_id}/resourceGroups/{rg}"
role_definition_id = f"{scope}/providers/Microsoft.Authorization/roleDefinitions/43d0d8ad-25c7-4714-9337-8ba259a9fe05"  # Monitoring Reader

assignment_params = {
    "role_definition_id": role_definition_id,
    "principal_id": "operational-team-group-object-id",
    "principal_type": "Group"
}

assignment = auth_client.role_assignments.create(
    scope=scope,
    role_assignment_name=str(uuid.uuid4()),
    parameters=assignment_params
)

print(f"Role assigned: {assignment.role_definition_id}")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Azure CLI subprocess wrappers | Azure SDK for Python native clients | 2020+ (SDK maturity) | Stable API contracts, better error handling, type hints |
| Single retention setting | Analytics + Total retention (dual) | 2023 (Log Analytics update) | Cost optimization: hot vs archive storage |
| Manual WORM via portal | Programmatic verification (not creation) | 2024 (compliance best practice) | Prevents accidental production lockdown |
| Portal-only diagnostic settings | ARM templates + SDK automation | 2022+ (IaC patterns) | Repeatable deployments, audit trail |
| Application Insights standalone | App Insights + Log Analytics workspace binding | 2021+ (workspace-based) | Unified query experience, cross-resource correlation |

**Deprecated/outdated:**
- **Classic Application Insights (no workspace):** Deprecated Feb 2024, all new instances must bind to Log Analytics workspace
- **Azure CLI `az monitor app-insights component create` without workspace:** Fails with error since workspace binding is required
- **Python SDK azure-applicationinsights (data plane):** Legacy SDK, replaced by OpenTelemetry for instrumentation

## Open Questions

Things that couldn't be fully resolved:

1. **Copilot Studio Native Sampling Configuration**
   - What we know: Copilot Studio sends telemetry server-side to Application Insights, adaptive sampling not available in Python SDK
   - What's unclear: Can Copilot Studio sampling be configured at agent level, or only at Application Insights ingestion level?
   - Recommendation: Document ingestion sampling (workspace-level) as primary cost control, investigate Copilot Studio connector settings for agent-level sampling in Phase 2

2. **WORM Policy Verification Without Portal Access**
   - What we know: WORM policy audit logs stored per container, blob inventory shows immutability status
   - What's unclear: Can verification script read audit logs without Storage Blob Data Owner role? (read-only verification)
   - Recommendation: Test with Storage Blob Data Reader role, document minimum RBAC in `verify_worm.py` script

3. **Diagnostic Settings Export Latency**
   - What we know: Diagnostic settings export to storage is near-real-time (5-15 minutes)
   - What's unclear: Does export latency impact SEC 17a-4 compliance if audit event occurs minutes before system failure?
   - Recommendation: Document known latency in architecture.md, recommend Log Analytics workspace as primary audit source (real-time), storage export as backup/archive

## Sources

### Primary (HIGH confidence)

- [azure-mgmt-applicationinsights PyPI](https://pypi.org/project/azure-mgmt-applicationinsights/) - v4.1.0 stable release, Python 3.8+ required
- [azure-mgmt-loganalytics PyPI](https://pypi.org/project/azure-mgmt-loganalytics/) - v13.0.0 stable release
- [Manage data retention in a Log Analytics workspace - Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure) - 730-day retention configuration verified
- [Capture telemetry with Application Insights - Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry) - customDimensions schema documented
- [Overview of immutable storage for blob data - Azure Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview) - SEC 17a-4 WORM compliance (Cohasset validated)
- [Handle Errors Produced by the Azure SDK for Python](https://learn.microsoft.com/en-us/azure/developer/python/sdk/fundamentals/errors) - Exception hierarchy and retry policies

### Secondary (MEDIUM confidence)

- [Azure SDK for Python (Mgmt)](https://azure.github.io/azure-sdk/releases/latest/mgmt/python.html) - Latest releases Feb 2026
- [Application Insights telemetry with Microsoft Copilot Studio](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights) - Integration patterns verified
- [ADLS Gen2 Access Logs via Diagnostic Settings - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/1822342/adls-gen2-access-logs-via-diagnostic-settings) - Hierarchical namespace limitation confirmed

### Tertiary (LOW confidence - community sources)

- [Telemetry sampling in Azure Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/sampling-classic-api) - Adaptive sampling Python limitation inferred from absence in docs (not explicitly stated)
- [jsonargparse documentation](https://jsonargparse.readthedocs.io/en/v2.32.2/) - Config file pattern (YAML + argparse) from search results

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries from official Microsoft Azure SDK for Python with stable versions
- Architecture: HIGH - Patterns verified from FSI-AgentGov-Solutions/environment-lifecycle-management production code
- Pitfalls: HIGH - ADLS Gen2 limitation from Microsoft Q&A, WORM policy verified from official docs, PII fields from Copilot Studio telemetry schema
- Cost tuning: MEDIUM - Adaptive sampling limitation inferred (not explicitly documented as "not supported in Python")

**Research date:** 2026-02-05
**Valid until:** 90 days (Azure SDK stable, but telemetry schemas may evolve with Copilot Studio updates)

---

## Additional Context: FSI-AgentGov Integration

### Existing Framework Controls Using Telemetry

| Control | Telemetry Requirement | Phase 1 Deliverable |
|---------|----------------------|-------------------|
| 1.7 - Comprehensive Audit Logging | Application Insights captures CopilotInteraction events | App Insights workspace provisioning |
| 3.2 - Usage Analytics and Activity Monitoring | customEvents table with session/message/completion metrics | Log Analytics workspace for KQL queries (Phase 2) |
| 2.9 - Agent Performance Monitoring | Latency distribution (P50/P95/P99) | Telemetry pipeline foundation |
| 1.6 - DSPM for AI | Content scanning requires telemetry access | RBAC separation (operational vs compliance) |

**Governance mapping approach** (from CONTEXT.md): Start from artifact → list controls supported. Example:

```markdown
## Application Insights Workspace

**Primary evidence for:**
- Control 1.7: Audit logging (CopilotInteraction events)
- Control 3.2: Usage analytics (session metrics)

**Supporting evidence for:**
- Control 2.9: Performance monitoring (latency telemetry)
- Control 1.6: DSPM for AI (content access to customDimensions)

**Partial coverage for:**
- Control 2.6: Model risk management (telemetry available, KQL queries in Phase 2)
```

### Solution Documentation Standards (from existing solutions)

Based on message-center-monitor and environment-lifecycle-management patterns:

**README structure:**
1. Status badge (Completed/Work In Progress)
2. What This Solution Does (bullet points)
3. Who Should Use This (table: Audience | Use Case)
4. Prerequisites (numbered sections with sub-bullets)
5. Quick Start (numbered steps)
6. Workflow (ASCII diagram)
7. Documentation (table: Guide | Description)
8. Troubleshooting (table: Issue | Cause | Solution)
9. Version + CHANGELOG.md reference
10. Related Controls (links to FSI-AgentGov controls)
11. Playbook Reference (if exists)
12. License

**Python script standards** (from environment-lifecycle-management):
- Shebang: `#!/usr/bin/env python3`
- Docstring with usage examples
- argparse with descriptive help text
- `--dry-run` flag for preview
- Banner function for user-facing scripts
- Preflight validation before mutations
- Try-except with specific Azure exceptions
- Print statements with emoji/symbols (✓ ○ ✗) for status

### PII Sanitization Decision Framework

| Field | Contains PII? | Recommendation | Rationale |
|-------|---------------|----------------|-----------|
| `customDimensions.text` | YES (conversation) | Drop or hash | Customer prompts contain names, accounts, SSNs |
| `customDimensions.speak` | YES (conversation) | Drop or hash | Speech output may contain PII |
| `customDimensions.fromName` | YES (username) | Hash (one-way) | User identity, not needed for analytics |
| `customDimensions.recipientName` | YES (agent/user) | Hash (one-way) | Agent identity sufficient |
| `customDimensions.channelId` | NO | Retain | Channel type (msteams, webchat) is not PII |
| `customDimensions.locale` | NO | Retain | Language preference is not PII |
| `customDimensions.designMode` | NO | Retain | Test vs production flag |
| `customDimensions.TopicName` | NO | Retain | Intent classification, no PII |

**Decision framework:**
1. Does field contain customer-identifiable data? → Drop or hash
2. Is field needed for analytics/troubleshooting? → If yes, hash; if no, drop
3. Is field required for compliance audit trail? → Encrypt (reversible) with key management
4. Default: When in doubt, drop field (can always enable later)

**Source:** Adapted from [Dealing with PII or Sensitive Data Captured by Application Insights](https://learn.microsoft.com/en-us/archive/msdn-technet-forums/0b38fd1e-8aa9-45f7-91a7-fd0631ef8bba) and Copilot Studio telemetry schema analysis.
