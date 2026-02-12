# Phase 3 Research: Cloud Flow & Validation Logic

## Phase Goal

Create the `Detect-InactivityTimeout-NonCompliance` flow template with BAP Admin API integration, policy-driven compliance evaluation, and guarded notification.

## Requirements Covered

- **FLW-01:** Flow template enumerates environments via BAP Admin API, loads `fsi_environmentpolicy` rows, builds lookup keyed by EnvironmentName
- **FLW-02:** Per-environment evaluation with configurable concurrency (default 5) — policy resolution, BAP API privacy settings retrieval, compliance determination, immutable Dataverse persistence
- **FLW-03:** Guarded notification — email only when Non-Compliant > 0 OR Unknown > 0; includes environment, zone, actual duration, required max, and status

## 1. Existing Flow Template Pattern Analysis

### 1.1 JSON Envelope Structure

All 6 flow templates in `src/` share a common JSON envelope:

```json
{
  "properties": {
    "connectionReferences": { ... },
    "definition": {
      "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
        "$connections": { "defaultValue": {}, "type": "Object" },
        "$authentication": { "defaultValue": {}, "type": "SecureObject" }
      },
      "triggers": { ... },
      "actions": { ... }
    },
    "displayName": "...",
    "description": "...",
    "state": "Started"
  },
  "schemaVersion": "1.0.0.0"
}
```

### 1.2 Connection References

Projects use a naming convention for connection reference logical names:

| Solution | Dataverse | Office 365 | Teams | Approvals |
|----------|-----------|------------|-------|-----------|
| CAA (v10) | `fsi_cr_dataverse_conditionalaccessautomation` | `fsi_cr_office365_conditionalaccessautomation` | `fsi_cr_teams_conditionalaccessautomation` | — |
| UASD (v16) | `fsi_cr_dataverse_sharingdetector` | — | `fsi_cr_teams_sharingdetector` | `fsi_cr_approvals_sharingdetector` |

**Pattern:** `fsi_cr_{connector}_{solutionname}`

**For v19 (Inactivity Timeout):**
- `fsi_cr_dataverse_inactivitytimeout`
- `fsi_cr_office365_inactivitytimeout` (for email notifications)

**Note:** No `shared_teams` connector needed — requirements specify email-only notification (not Teams adaptive card). This simplifies the connection reference set vs UASD/CAA which used both Teams and email.

### 1.3 Trigger Patterns

**Daily Scheduled (reuse for v19):**
```json
"Recurrence_Daily_0600_UTC": {
  "type": "Recurrence",
  "recurrence": {
    "frequency": "Day",
    "interval": 1,
    "startTime": "2026-01-01T06:00:00Z",
    "timeZone": "UTC",
    "schedule": { "hours": ["6"], "minutes": ["0"] }
  },
  "metadata": { "operationMetadataId": "recurrence-daily-0600" }
}
```

Used identically by: `caa-daily-compliance-flow.json`, `uasd-detector-scan-agents.json`. The v19 flow uses the same daily 06:00 UTC trigger.

### 1.4 Variable Initialization Pattern

All flows initialize variables in a sequential chain (each `runAfter` the previous):

1. `Initialize_DataverseUrl` → `runAfter: {}`
2. `Initialize_TenantId` → `runAfter: Initialize_DataverseUrl`
3. ... chained sequentially

Each variable has:
- `description` field referencing the environment variable name: `"Set via environment variable fsi_{SOLUTION}_{VarName}."`
- Empty default `value: ""`  (populated by solution environment variables at deployment)

### 1.5 Scope_Try / Scope_Catch Pattern

Every flow uses the same error-handling scaffold:

```
Scope_Try:
  type: Scope
  actions: { ... main logic ... }
  runAfter: { last_variable_init: ["Succeeded"] }

Scope_Catch:
  type: Scope
  actions: { error notification email/Teams }
  runAfter: { Scope_Try: ["Failed", "TimedOut"] }
```

The Scope_Catch in CAA sends a CRITICAL email. UASD sends a Teams adaptive card error notification. **For v19, we should use email (matching FLW-03's email-only notification requirement).**

### 1.6 BAP Admin API Usage Patterns

**UASD flow** is the primary precedent for BAP Admin API calls (HTTP action with MSI auth):

```json
"List_Environments": {
  "type": "Http",
  "inputs": {
    "method": "GET",
    "uri": "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2016-11-01",
    "headers": { "Content-Type": "application/json" },
    "authentication": {
      "type": "ManagedServiceIdentity",
      "audience": "https://api.bap.microsoft.com"
    }
  }
}
```

**Key observations:**
- Auth: `ManagedServiceIdentity` with `audience: "https://api.bap.microsoft.com"`
- The `name` property in the response is the canonical EnvironmentName (not display name)
- The `displayName` is at `properties.displayName`
- API version for environment listing: `2016-11-01`
- API version for settings/privacy: `2021-04-01` (from requirements spec)

**For v19, the privacy endpoint is:**
```
GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01
```

### 1.7 Dataverse Operations

All flows use the `shared_commondataserviceforapps` connector with `OpenApiConnection` type:

**Create Record:**
```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "parameters": {
      "entityName": "fsi_tablename",
      "item/fsi_column1": "@value1",
      "item/fsi_column2": "@value2"
    },
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
      "connectionName": "shared_commondataserviceforapps",
      "operationId": "CreateRecord"
    }
  }
}
```

**List Records (with filter):**
```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "parameters": {
      "entityName": "fsi_tablename",
      "$filter": "fsi_column eq 'value'",
      "$select": "fsi_col1,fsi_col2"
    },
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
      "connectionName": "shared_commondataserviceforapps",
      "operationId": "ListRecords"
    }
  }
}
```

### 1.8 Concurrency Control

**Current patterns use `operationOptions: "Sequential"` only** — no configurable concurrency is used in existing flows. Both UASD and CAA iterate environments and agents sequentially.

The v19 requirement specifies `configurable concurrency (default 5)`. This is a **new pattern** for this project. In Cloud Flows, the `Apply_to_Each` action supports `runtimeConfiguration.concurrency.repetitions` to set parallel degree:

```json
"Apply_to_Each_Environment": {
  "type": "Foreach",
  "foreach": "@body('List_Environments')?['value']",
  "actions": { ... },
  "runtimeConfiguration": {
    "concurrency": {
      "repetitions": 5
    }
  }
}
```

**Note:** When using concurrency > 1, you cannot use `IncrementVariable` or `AppendToArrayVariable` inside the loop (they are not thread-safe). Instead, counters must be computed after the loop using `length()` on the resulting Dataverse records, or use a Compose → Select → Length pattern.

### 1.9 Guarded Notification Pattern

**UASD pattern:**
```json
"Check_Violations_Found": {
  "type": "If",
  "expression": { "greater": ["@variables('ViolationCount')", 0] },
  "actions": { /* build card + send */ },
  "else": { "actions": {} }
}
```

**CAA pattern:**
```json
"Check_Alert_Required": {
  "type": "If",
  "expression": { "equals": ["@body('Parse_Results')?['AlertRequired']", true] },
  "actions": { /* adaptive card + Teams + email */ },
  "else": { "actions": {} }
}
```

**For v19:** Guard on `NonCompliantCount > 0 OR UnknownCount > 0`. Since we're using concurrency, we cannot rely on variable accumulators. The guard should query the Dataverse compliance table for records from the current scan run with non-compliant or unknown status.

### 1.10 Email Notification Pattern (Office 365 Connector)

From CAA:
```json
"Send_Alert_Email": {
  "type": "OpenApiConnection",
  "inputs": {
    "parameters": {
      "emailMessage/To": "@variables('ComplianceDistributionList')",
      "emailMessage/Subject": "[SEVERITY] Subject — Status",
      "emailMessage/Body": "<html><body>...</body></html>",
      "emailMessage/Importance": "High"
    },
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365",
      "connectionName": "shared_office365",
      "operationId": "SendEmailV2"
    }
  }
}
```

### 1.11 Flow Display Name and Description

**Pattern:** `"{solution-abbreviation} - {Flow Purpose}"`
- CAA: `"CAA - Daily Compliance Scan"`
- UASD: `"fsi-UASD-Detector-ScanAgents"`

**For v19:** `"ITE - Detect Inactivity Timeout Non-Compliance"` or consistent with the file name: `"fsi-ITE-Detect-InactivityTimeout-NonCompliance"`

**Description pattern:** Includes purpose, regulatory references, and solution affiliation:
```
"Detects non-compliant inactivity timeout settings across Power Platform environments using zone-based policy evaluation. Supports compliance with GLBA 501(b), SOX 302, FINRA 4511, NIST 800-53 AC-11/AC-12. Part of the FSI Agent Governance — Inactivity Timeout Enforcement solution."
```

## 2. BAP Admin API — Privacy Settings Endpoint

### 2.1 Endpoint Details

**GET (read current settings):**
```
GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01
```

**Expected response structure (from spec):**
```json
{
  "properties": {
    "inactivityTimeoutEnabled": true,
    "inactivityTimeoutDuration": "PT60M",
    "inactivityWarningDuration": "PT5M"
  }
}
```

**Key parsing rules:**
- `inactivityTimeoutEnabled`: boolean — if `false`, timeout is disabled → **Non-Compliant**
- `inactivityTimeoutDuration`: ISO 8601 duration string (e.g., `"PT60M"` = 60 minutes, `"PT120M"` = 120 minutes)
- Must parse the duration into minutes for numeric comparison against `fsi_requiredmaxduration`

### 2.2 Authentication

Per spec: Service principal auth with scope `https://api.bap.microsoft.com/.default`.

**Existing flows use:**
```json
"authentication": {
  "type": "ManagedServiceIdentity",
  "audience": "https://api.bap.microsoft.com"
}
```

This is the lab-grade pattern consistent with v4-v18. The MSI must have Power Platform Administrator role or appropriate API permissions.

### 2.3 Error Scenarios

Per requirements, the flow must handle:
- **401 Unauthorized** — Invalid or expired token → Unknown + error log
- **403 Forbidden** — Insufficient permissions → Unknown + error log
- **404 Not Found** — Environment doesn't exist or privacy settings not available → Unknown + error log
- **429 Too Many Requests** — Rate limited → Unknown + error log
- **ParseError** — Unexpected response format → Unknown + error log
- **MissingPolicy** — No `fsi_environmentpolicy` row for this EnvironmentName → Unknown + error log

## 3. Recommended Flow Structure

### 3.1 Action Sequence (Plan A: Core Logic)

```
1. Trigger: Recurrence_Daily_0600_UTC

2. Variables (sequential chain):
   - Initialize_DataverseUrl
   - Initialize_ComplianceDistributionList
   - Initialize_ScanRunId (guid())
   - Initialize_ConcurrencyLimit (integer, default 5 — env var fsi_ITE_ConcurrencyLimit)
   - Initialize_NonCompliantCount (integer, 0)
   - Initialize_UnknownCount (integer, 0)
   - Initialize_CompliantCount (integer, 0)
   - Initialize_ResultCards (array, [])

3. Scope_Try:
   a. Load_Environment_Policies (ListRecords from fsi_environmentpolicies)
   b. Build_Policy_Lookup (Compose: create lookup object from policy rows)
   c. List_Environments (HTTP GET to BAP Admin API)
   d. Apply_to_Each_Environment (Foreach with sequential execution):
      i.   Set_EnvironmentName (Compose: items()?['name'])
      ii.  Set_EnvironmentDisplayName (Compose: items()?['properties']?['displayName'])
      iii. Set_EnvironmentType (Compose: items()?['properties']?['environmentSku'])
      iv.  Resolve_Policy (Compose: lookup policy by EnvironmentName)
      v.   Check_Policy_Exists:
           - NO → Create Unknown compliance row + MissingPolicy error log + Increment UnknownCount
           - YES → Continue to BAP API call
      vi.  Scope_API_Call:
           - Get_Privacy_Settings (HTTP GET privacy endpoint)
           - Parse_Privacy_Response
           - Evaluate_Compliance:
             - timeout disabled → Non-Compliant
             - parse duration → compare to required max
             - duration > required max → Non-Compliant
             - otherwise → Compliant
           - Create_Compliance_Record (immutable row)
           - Increment appropriate counter
           - If Non-Compliant or Unknown: Append result card
      vii. Scope_API_Error:
           - runAfter Scope_API_Call: [Failed, TimedOut]
           - Create Unknown compliance row + error log entry
           - Increment UnknownCount

   e. Check_Notification_Required:
      - If NonCompliantCount > 0 OR UnknownCount > 0:
        - Build HTML email body with results table
        - Send_Alert_Email (Office365 SendEmailV2)
      - Else: no action

4. Scope_Catch:
   - runAfter Scope_Try: [Failed, TimedOut]
   - Send_Flow_Error_Email (CRITICAL notification)
```

### 3.2 Concurrency Design Decision

**Option A: Sequential with variable accumulators** (simpler, matches existing pattern)
- `operationOptions: "Sequential"` on `Apply_to_Each_Environment`
- Can use `IncrementVariable` for counters and `AppendToArrayVariable` for result cards
- Simpler error handling
- **Downside:** Slower for large environment counts

**Option B: Parallel with post-loop queries** (matches spec's "configurable concurrency default 5")
- `runtimeConfiguration.concurrency.repetitions: 5`
- Cannot use variable accumulators inside loop
- After loop, query Dataverse: count compliance rows from this ScanRunId grouped by status
- **Downside:** More complex, requires post-loop aggregation queries

**Recommendation: Option A (Sequential)** — for the initial implementation, this matches all existing flow patterns and avoids the complexity of thread-safe accumulation. The `configurable concurrency` requirement can be noted as "configurable via flow designer" with the default being sequential, and a comment in the description noting the `runtimeConfiguration` setting. This is consistent with how UASD handles its environment loop.

**Rationale:** The UASD detector scans potentially hundreds of agents across environments and still uses Sequential. Environment-level timeout scanning is simpler (one API call per environment, no nested agent loop). Sequential processing is adequate for typical tenant sizes (10-50 environments). The roadmap can note "concurrency tunable in flow designer" for production optimization.

**However**, if the requirement strictly mandates `configurable concurrency (default 5)` as a must-have, use Option B with:
1. No `IncrementVariable` inside the loop
2. Each iteration writes its compliance row to Dataverse (CreateRecord is inherently thread-safe)
3. After the loop, query Dataverse for counts: `$filter=fsi_scan_run_id eq '{ScanRunId}' and fsi_compliancestatus eq N`
4. Environment variable `fsi_ITE_ConcurrencyLimit` stores the repetitions value (but note: the flow template JSON hardcodes the default, the environment variable is conceptual — actual change requires editing the flow definition or using a child flow pattern)

**Update:** Given the requirement explicitly states "configurable concurrency (default 5)", the plan should implement **Option B** to satisfy FLW-02. The approach:
1. Set `runtimeConfiguration.concurrency.repetitions: 5` on the environment forEach
2. Write compliance rows and error logs inside the loop (Dataverse CreateRecord is thread-safe)
3. After the loop, run 3 List_Records queries to count Compliant/Non-Compliant/Unknown by ScanRunId
4. Build notification from the queried results rather than accumulated variables
5. Note in flow description that concurrency is configurable via flow designer settings

### 3.3 Duration Parsing

The BAP API returns ISO 8601 durations like `PT60M` or `PT2H`. In Power Automate expressions:

```
@int(replace(replace(body('Parse_Privacy_Response')?['properties']?['inactivityTimeoutDuration'], 'PT', ''), 'M', ''))
```

This handles `PTnM` format. For `PTnH` format, additional parsing is needed:
```
@if(contains(body('Parse_Privacy_Response')?['properties']?['inactivityTimeoutDuration'], 'H'),
  mul(int(first(split(replace(body('Parse_Privacy_Response')?['properties']?['inactivityTimeoutDuration'], 'PT', ''), 'H'))), 60),
  int(replace(replace(body('Parse_Privacy_Response')?['properties']?['inactivityTimeoutDuration'], 'PT', ''), 'M', ''))
)
```

**Simpler approach:** Use a Compose action to extract the numeric minutes value and handle both `PTnM` and `PTnHnM` formats.

### 3.4 Policy Lookup Pattern

The flow loads all `fsi_environmentpolicy` rows upfront and needs to find the matching row for each environment by `fsi_environmentid` (which holds the EnvironmentName).

In Power Automate, there's no native dictionary/hashmap. **Options:**

**Option A: Filter array per iteration**
```json
"Resolve_Policy": {
  "type": "Query",
  "inputs": {
    "from": "@body('Load_Environment_Policies')?['value']",
    "where": "@equals(item()?['fsi_environmentid'], outputs('Set_EnvironmentName'))"
  }
}
```
Then `first(body('Resolve_Policy'))` gets the matching policy or null.

**Option B: Dataverse query per iteration**
Query `fsi_environmentpolicies` with `$filter=fsi_environmentid eq '{name}'` each time. More API calls but avoids in-memory filtering.

**Recommendation: Option A** — matches existing patterns (UASD loads approved groups upfront then filters in-memory). Single Dataverse read for all policies, then in-memory `Query` filter per environment. This is the exact pattern used by UASD's `Initialize_Approved_Group_Ids` + in-loop `contains()` check.

## 4. Key Patterns to Reuse from Existing Flows

| Pattern | Source Flow | Adaptation for v19 |
|---------|-------------|---------------------|
| Daily 06:00 UTC recurrence trigger | UASD, CAA | Direct reuse |
| Variable initialization chain | All flows | Adapt variable names to `fsi_ITE_*` |
| BAP Admin API + MSI auth | UASD | Same auth pattern, different endpoint (privacy settings) |
| Environment enumeration via HTTP | UASD | Reuse `List_Environments` exactly |
| Scope_Try / Scope_Catch | All flows | Direct reuse with email error notification |
| Dataverse CreateRecord for immutable rows | UASD, CAA | Same pattern for compliance + error log tables |
| Guarded notification check | UASD (`Check_Violations_Found`) | Adapt to `NonCompliantCount > 0 OR UnknownCount > 0` |
| Email notification via Office 365 | CAA (`Send_Alert_Email`) | Adapt HTML body for timeout compliance |
| In-memory policy lookup | UASD (`Load_Approved_Groups`) | Same pattern: load all, filter per iteration |
| ScanRunId for audit grouping | UASD | Direct reuse for correlating scan results |

## 5. Patterns That Differ from Existing Templates

| Difference | Existing Pattern | v19 Requirement | Approach |
|-----------|-----------------|-----------------|----------|
| Concurrency | Sequential (`operationOptions: "Sequential"`) | Configurable concurrency (default 5) | Use `runtimeConfiguration.concurrency.repetitions: 5`; avoid variable accumulators inside loop |
| Counter accumulation | `IncrementVariable` inside loop | Cannot use with concurrency > 1 | Post-loop Dataverse queries to count by `fsi_compliancestatus` |
| Result card accumulation | `AppendToArrayVariable` inside loop | Cannot use with concurrency > 1 | Post-loop: query Non-Compliant/Unknown records, build HTML table directly |
| Notification channel | Teams adaptive card + email (CAA); Teams only (UASD) | Email only | Simpler — only `shared_office365` connector needed |
| No agents/bots enumeration | UASD lists bots per environment | v19 evaluates environment-level setting | One API call per environment (not nested) |
| ISO 8601 duration parsing | Not present in existing flows | Parse `PTnM`/`PTnH` duration strings | Compose action with string manipulation expressions |
| Error log table | Not present in UASD/CAA flows | Separate `fsi_inactivitytimeout_errorlog` table | Additional CreateRecord for each error scenario |
| Per-environment error scope | UASD has no per-API error handling | Each API call needs individual error capture | Nested `Scope_API_Try` / `Scope_API_Catch` inside the forEach |

## 6. Risks and Dependencies

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| BAP Admin API privacy endpoint may not return expected JSON structure | Medium | High | Wrap in try/catch scope; ParseError handling; validate against actual API response in testing |
| ISO 8601 duration format variations (`PT2H`, `PT2H30M`, `PT120M`) | Medium | Medium | Implement robust parsing with multiple format handlers |
| Concurrency with variable accumulators | High (if using parallel) | High | Use Option B: post-loop Dataverse queries for counts |
| Large environment count (>100) causing throttling | Low | Medium | Sequential processing or moderate concurrency (5); BAP API should handle well |
| MSI audience for privacy settings endpoint may differ from environment listing | Low | High | Both use `https://api.bap.microsoft.com` audience — consistent with UASD |
| `fsi_environmentpolicy` table empty on first run | High (expected) | Medium | All environments → Unknown + MissingPolicy — expected behavior per spec |

### Dependencies

| Dependency | Type | Status | Impact |
|-----------|------|--------|--------|
| `fsi_environmentpolicy` Dataverse table | Phase 2 (DVM-01) | Not started | Flow references table but works without it (all results = Unknown) |
| `fsi_inactivitytimeout_compliance` table | Phase 2 (DVM-02) | Not started | Flow writes to this table — schema must match |
| `fsi_inactivitytimeout_errorlog` table | Phase 2 (DVM-03) | Not started | Flow writes error entries — schema must match |
| Environment variables (fsi_ITE_*) | Phase 2 | Not started | Flow template uses empty defaults — variables populated at deployment |
| BAP Admin API access | Infrastructure | Assumed available | MSI must have Power Platform Admin role |

**Key:** The flow template JSON can be created independently of Phase 2. It references Dataverse table names and column names by string — no compile-time dependency. The template is validated by importing into a Power Platform solution.

## 7. Technical Approach Per Must-Have

### FLW-01: Environment Enumeration + Policy Lookup

**Approach:**
1. `Load_Environment_Policies`: Dataverse ListRecords on `fsi_environmentpolicies`, `$select=fsi_environmentid,fsi_environmentdisplayname,fsi_zone,fsi_requiredmaxduration`
2. `List_Environments`: HTTP GET to BAP Admin API (reuse UASD pattern exactly)
3. Inside `Apply_to_Each_Environment`:
   - Extract `EnvironmentName` from `items()?['name']` (canonical identifier)
   - Extract `DisplayName` from `items()?['properties']?['displayName']`
   - Extract `EnvironmentType` from `items()?['properties']?['environmentSku']`
   - `Resolve_Policy`: Query filter on loaded policies array: `equals(item()?['fsi_environmentid'], outputs('Set_EnvironmentName'))`
   - Check policy exists: `greater(length(body('Resolve_Policy')), 0)`

### FLW-02: Per-Environment Compliance Evaluation

**Approach for each environment:**

```
1. Check_Policy_Exists:
   YES:
     a. Set_RequiredMaxDuration = first(body('Resolve_Policy'))?['fsi_requiredmaxduration']
     b. Set_Zone = first(body('Resolve_Policy'))?['fsi_zone']
     c. Scope_BAP_API_Try:
        - Get_Privacy_Settings: HTTP GET /settings/privacy
        - Parse_Privacy_Response
        - Set_TimeoutEnabled = body('Parse')?['properties']?['inactivityTimeoutEnabled']
        - Set_TimeoutDuration = parse ISO 8601 to minutes
        - Evaluate:
          - NOT TimeoutEnabled → Status = "Non-Compliant", Note = "Inactivity timeout is disabled"
          - TimeoutDuration > RequiredMaxDuration → Status = "Non-Compliant", Note = "Duration {actual}m exceeds maximum {required}m"
          - Otherwise → Status = "Compliant"
        - Create_Compliance_Record: CreateRecord in fsi_inactivitytimeout_compliance
     d. Scope_BAP_API_Catch:
        - runAfter Scope_BAP_API_Try: [Failed, TimedOut]
        - Create Unknown compliance row
        - Create error log entry (fsi_errortype from HTTP status or exception)

   NO:
     a. Create compliance row: Status = Unknown, Note = "No explicit policy found for environment"
     b. Create error log: fsi_errortype = "MissingPolicy"
```

### FLW-03: Guarded Notification

**Approach:**
1. After the environment loop completes, query compliance records for this scan run:
   - `Count_NonCompliant`: ListRecords where `fsi_scan_run_id eq '{ScanRunId}' and fsi_compliancestatus eq 1` (Non-Compliant)
   - `Count_Unknown`: ListRecords where `fsi_scan_run_id eq '{ScanRunId}' and fsi_compliancestatus eq 2` (Unknown)
2. Guard condition: `length(Count_NonCompliant/value) > 0 OR length(Count_Unknown/value) > 0`
3. If true, build HTML email:
   - Subject: `[NON-COMPLIANT] Inactivity Timeout Compliance Scan — {count} issue(s) found`
   - Body includes:
     - Scan summary (date, total environments, compliant/non-compliant/unknown counts)
     - Results table with columns: Environment, Zone, Timeout Enabled, Actual Duration, Required Max, Status
     - Each Non-Compliant/Unknown row highlighted
   - Send via Office 365 `SendEmailV2` to `ComplianceDistributionList`
4. If false (all compliant): no email sent

## 8. File Manifest

### Files to Create (Phase 3)

| File | Purpose |
|------|---------|
| `src/detect-inactivity-timeout-noncompliance.json` | Cloud Flow template — daily detection scan with BAP Admin API, policy evaluation, Dataverse persistence, guarded email notification |

### Files NOT Created by Phase 3

| File | Phase | Purpose |
|------|-------|---------|
| Adaptive card template | — | Not needed — v19 uses email-only notification (no Teams adaptive card) |
| Dataverse schema scripts | Phase 2 | Table schemas referenced but not created here |
| PowerShell scripts | Phase 4 | Remediation scripts are independent |

### Single File Rationale

Unlike UASD (which has 4 flow files: detector, exception-approval, remediation, exception-manager-app) or CAA (which has 2 flows: daily-compliance, provisioning-hook), v19 has a **single detection flow**. The remediation is PowerShell-based (Phase 4), and there is no exception/approval workflow in scope. This matches the spec requirements which define only one flow (FLW-01/02/03).

## 9. Estimated Flow Template Size

Based on existing templates:
- `caa-daily-compliance-flow.json`: 1,332 lines (Azure Automation + parse + dual Teams/email)
- `uasd-detector-scan-agents.json`: 1,951 lines (5 violation rules, nested agent loop, Teams card)
- `caa-provisioning-hook-flow.json`: 1,381 lines (Azure Automation + single-environment)

**v19 estimate:** ~800–1,000 lines. Simpler than UASD (no nested agent loop, no 5-rule evaluation, no exception checking) and CAA (no Azure Automation job orchestration). The primary actions are: enumerate environments → load policies → per-env API call → evaluate → write record → post-loop notification guard → email.

## 10. Naming Conventions Summary

| Element | Convention | v19 Value |
|---------|-----------|-----------|
| Flow file | `{verb}-{noun}-{purpose}.json` | `detect-inactivity-timeout-noncompliance.json` |
| Display name | `{abbrev} - {Purpose}` | `ITE - Detect Inactivity Timeout Non-Compliance` |
| Connection refs | `fsi_cr_{connector}_{solution}` | `fsi_cr_dataverse_inactivitytimeout`, `fsi_cr_office365_inactivitytimeout` |
| Environment vars | `fsi_ITE_{VarName}` | `fsi_ITE_DataverseUrl`, `fsi_ITE_ComplianceDistributionList`, `fsi_ITE_ConcurrencyLimit` |
| Dataverse tables | `fsi_{tablename}` | `fsi_environmentpolicies`, `fsi_inactivitytimeout_compliances`, `fsi_inactivitytimeout_errorlogs` |
| Scan correlation | `ScanRunId` (GUID) | `@{guid()}` initialized at flow start |
| Action names | PascalCase descriptive | `Load_Environment_Policies`, `Get_Privacy_Settings`, `Evaluate_Compliance` |
| Compliance status | Choice values | 0 = Compliant, 1 = Non-Compliant, 2 = Unknown |

## 11. Plan Split

Per the roadmap, Phase 3 has 2 plans:

**Plan A (03-01): Flow template core** — enumeration + policy lookup + evaluation logic
- Variables, trigger, Scope_Try structure
- Load policies, list environments, forEach loop
- Per-environment: policy resolution, BAP API call, compliance evaluation, Dataverse writes
- Error handling scopes (per-environment and flow-level)

**Plan B (03-02): Notification logic + error handling + concurrency configuration
- Post-loop aggregation queries (count by status)
- Guarded notification check
- HTML email composition
- Send email action
- Scope_Catch (flow-level error notification)
- Concurrency runtime configuration

**Note:** Since the output is a single JSON file, both plans contribute to the same file. Plan A creates the file with core logic; Plan B extends it with notification and finalization. This is manageable because:
1. Plan A writes the main action structure
2. Plan B adds the post-loop actions and Scope_Catch
3. Both are sequential (Plan B depends on Plan A)

---
*Research completed: 2026-02-12*
*Phase: 3 — Cloud Flow & Validation Logic*
*Requirements: FLW-01, FLW-02, FLW-03*
*Depth: comprehensive*
