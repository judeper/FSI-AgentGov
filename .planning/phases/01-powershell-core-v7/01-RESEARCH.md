# Phase 1 Research: Content Moderation Governance Monitor (v7)

**Researched:** 2026-02-09
**Phase:** 1 — PowerShell Core
**Requirements covered:** CMV-01, CMV-02, CMV-03, CMV-04, CMV-05, CMV-06

## 1. Technical Analysis

### 1.1 The Per-Agent Problem

The fundamental architectural difference between v7 and all prior milestones (v4 ACV, v5 SSC, v6 AAM) is that **content moderation is configured per-agent, not per-environment**.

Prior solutions queried environment-level settings via `Get-AdminPowerAppEnvironment`, extracting `governanceConfiguration.settings.extendedSettings` properties like `bot-limitSharingMode`. Content moderation has no equivalent environment-level property — it is configured at **Copilot Studio > Agent > Settings > Generative AI > Content moderation** and stored in the agent's Dataverse metadata.

This means v7 requires a **two-tier query pattern**:
1. **Environment tier**: Enumerate Power Platform environments (reuse existing pattern)
2. **Agent tier**: For each environment with a Dataverse instance, query the `bot` table to enumerate Copilot Studio agents and retrieve their generative AI configuration

### 1.2 Dataverse Bot Table Schema

Copilot Studio agents are stored in each environment's Dataverse instance as records in the `bot` table. Key columns:

| Column | Type | Description |
|--------|------|-------------|
| `botid` | Uniqueidentifier | Primary key |
| `name` | String | Agent display name |
| `schemaname` | String | Internal schema name |
| `publishedon` | DateTime | Last publish timestamp |
| `statecode` | OptionSet | Active/Inactive |
| `statuscode` | OptionSet | Published/Draft/etc. |
| `configuration` | Memo/JSON | Agent configuration blob |
| `botcomponentids` | Related | Navigation to bot components |

Agent configuration — including generative AI settings like content moderation level — is stored in **`botcomponent`** records associated with the bot. Each `botcomponent` has a `componenttype` that categorizes what the component represents (topic, dialog, generative settings, etc.).

### 1.3 Content Moderation Level Extraction

The content moderation level is part of the agent's generative AI configuration. Two approaches to extract it:

**Approach A — Dataverse Web API direct query:**
```
GET https://{env}.crm.dynamics.com/api/data/v9.2/bots?$select=botid,name,configuration,statecode,statuscode
```
Then parse the `configuration` JSON blob for moderation settings, or follow up with:
```
GET https://{env}.crm.dynamics.com/api/data/v9.2/botcomponents?$filter=_botid_value eq '{botid}'&$select=componenttype,content
```
Filter for the component type that holds generative AI settings and parse the `content` JSON for the `ContentModeration` property.

**Approach B — Power Platform PowerShell + Dataverse invoke:**
Use `Invoke-RestMethod` with an access token obtained via `Connect-AzAccount` or the Power Platform Admin module's authentication context to query each environment's Dataverse endpoint.

**Recommended: Approach B** — Aligns with existing PowerShell patterns, avoids new module dependencies.

### 1.4 Content Moderation Values

From the Copilot Studio documentation and Control 1.8:

| Portal Display | Internal Value | Filtering Behavior |
|---------------|---------------|---------------------|
| Low | `Low` or `Lowest` | Minimal filtering; broader responses |
| Medium | `Medium` | Balanced filtering; blocks clearly harmful content |
| High | `High` or `Highest` | Strict filtering; blocks potentially sensitive content |

The internal representation in Dataverse may use enumeration values or string labels. The script must normalize these to the three canonical levels (Low/Medium/High) for comparison.

### 1.5 Environment Enumeration (Reused Pattern)

Environment enumeration follows the proven v6 AAM pattern:
```powershell
#Requires -Modules Microsoft.PowerApps.Administration.PowerShell
$environments = Get-AdminPowerAppEnvironment
```

**Critical filter**: Only environments with a Dataverse instance can contain Copilot Studio agents. Environments without Dataverse (canvas-app-only environments) should be skipped. Check for the presence of `$env.Internal.properties.linkedEnvironmentMetadata` or similar property indicating Dataverse provisioning.

### 1.6 Authentication Model

Querying per-environment Dataverse instances requires authentication to each environment's endpoint. Options:

1. **Service principal with Dataverse application user** in each environment — Enterprise pattern, best for automation but complex setup
2. **Interactive user with admin role** across environments — Simpler for operator script, matches Phase 1 standalone posture
3. **Power Platform Admin module token reuse** — The `Microsoft.PowerApps.Administration.PowerShell` module's auth context may provide tokens that can be used for Dataverse Web API calls

For Phase 1 (standalone PowerShell scripts), **Option 2 is recommended** with a helper that obtains a Dataverse token per environment. Phase 3 (Power Automate) will shift to connection references.

### 1.7 Zone Compliance Rules

From REQUIREMENTS.md severity matrix and Control 1.8:

| Zone | Agent Moderation Level | Severity | Regulatory Context |
|------|----------------------|----------|-------------------|
| Zone 3 | Low | CRITICAL | FINRA 3110 — Unmoderated customer-facing AI agent |
| Zone 3 | Medium | HIGH | GLBA 501(b) — Insufficient content protection for enterprise agent |
| Zone 2 | Low | HIGH | SOX 404 — Inadequate content controls for shared agent |
| Zone 2 | Medium | MEDIUM | Best practice uplift recommended for team agents |
| Zone 1 | Low | HIGH | Governance gap — Below minimum threshold |
| Zone 1 | Medium | Compliant | Meets Zone 1 minimum requirement |
| Any Zone | High | Compliant | Meets all zone requirements |

## 2. Architecture Decisions

### 2.1 Reuse from v6 AAM

The following components can be directly adapted from the v6 AAM scaffold:

| v6 AAM Component | v7 CMM Adaptation | Change Scope |
|-------------------|-------------------|--------------|
| Folder structure | Same Tier 2 layout | Rename `agent-access-monitor/` → `content-moderation-monitor/` |
| `AAMClient.psm1` | `CMMClient.psm1` | New Dataverse queries for `bot` table; CMM_ env var prefix |
| `Get-ZoneClassification.ps1` | Reuse as-is | No changes needed |
| `Test-ParameterValidation.ps1` | Adapt validators | Validate moderation levels instead of sharing modes |
| `Get-ExpectedSettings.ps1` | `Get-ExpectedModerationLevel.ps1` | Zone → expected moderation level lookup |
| `zone-settings-baseline.json` | `moderation-baseline.json` | Map zones to expected moderation levels + severity matrix |
| `Compare-ZoneCompliance.ps1` | `Compare-ModerationCompliance.ps1` | Compare actual agent moderation vs. zone expected |
| `Test-AgentAccessCompliance.ps1` | `Test-ContentModerationCompliance.ps1` | Orchestrate: envs → agents → compare → report |

### 2.2 New Components (v7-Specific)

| Component | Purpose |
|-----------|---------|
| `Get-AgentModerationSettings.ps1` | For each environment, query Dataverse `bot`/`botcomponent` tables to retrieve agent moderation levels |
| `Connect-EnvironmentDataverse.ps1` (private) | Obtain Dataverse access token for a specific environment's endpoint |
| `moderation-baseline.json` | Zone-specific moderation requirements + severity matrix + regulatory context |

### 2.3 Solution Folder Structure

```
content-moderation-monitor/
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── PREREQUISITES.md
│   ├── SCHEMA.md
│   ├── EVIDENCE_EXPORT.md
│   └── TROUBLESHOOTING.md
├── scripts/
│   ├── private/
│   │   ├── CMMClient.psm1
│   │   ├── Get-ZoneClassification.ps1          # Reused from v6
│   │   ├── Test-ParameterValidation.ps1
│   │   ├── Get-ExpectedModerationLevel.ps1
│   │   └── Connect-EnvironmentDataverse.ps1    # NEW
│   ├── Get-AgentModerationSettings.ps1          # NEW (core query)
│   ├── Compare-ModerationCompliance.ps1
│   └── Test-ContentModerationCompliance.ps1
├── src/
│   └── dataverse/
│       ├── tables/
│       ├── environment-variables/
│       └── connection-references/
├── templates/
│   └── moderation-baseline.json
└── flows/
```

### 2.4 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Query layer | Dataverse Web API per environment | Only reliable programmatic path to per-agent settings |
| Auth helper | Separate `Connect-EnvironmentDataverse.ps1` | Isolates auth complexity; testable independently |
| Agent filtering | By `statecode`/`statuscode` | CMV-05 requires filter by published vs. draft |
| Env var prefix | `CMM_` | Follows ACV_/SSC_/AAM_ pattern |
| Output grain | Per-agent (not per-environment) | v7 validates individual agents, unlike v6 which validated environments |
| Baseline format | `moderation-baseline.json` | Matches v6 pattern but maps zones → moderation levels instead of sharing modes |

### 2.5 Plan Decomposition

Following the v6 three-plan pattern:

| Plan | Scope | Wave |
|------|-------|------|
| **01-01-PLAN** | Scaffold, private helpers (`CMMClient.psm1`, `Get-ZoneClassification.ps1`, `Connect-EnvironmentDataverse.ps1`, `Get-ExpectedModerationLevel.ps1`), `moderation-baseline.json` | Wave 1 |
| **01-02-PLAN** | `Get-AgentModerationSettings.ps1` (env enumeration + per-env bot query), `Compare-ModerationCompliance.ps1` (agent-level compliance check with severity) | Wave 2 |
| **01-03-PLAN** | `Test-ContentModerationCompliance.ps1` orchestrator (query → compare → report, WhatIf, OutputFormat, filters) | Wave 2 |

## 3. Risk Assessment

### 3.1 API Availability Risk — HIGH

**Risk:** The exact Dataverse schema for content moderation level in `bot`/`botcomponent` tables is not documented in public Microsoft Learn references. The internal representation (column name, value format) may vary between Copilot Studio versions.

**Mitigation:**
- Phase 1 Plan 1 should include a **discovery task** — run an exploratory query against a test environment's `bot` and `botcomponent` tables to determine the exact schema
- Build the extraction logic to be tolerant of missing properties (graceful degradation)
- Log raw data at `-Verbose` level for debugging unexpected schemas

### 3.2 Cross-Environment Authentication — MEDIUM

**Risk:** Querying Dataverse in each environment requires separate authentication. In large tenants with 50+ environments, this could be slow and may hit token request rate limits.

**Mitigation:**
- Implement token caching per environment in `Connect-EnvironmentDataverse.ps1`
- Use `-IncludeEnvironments` filter for targeted scanning
- Default `GracePeriodHours` to 48 to reduce environment count
- Add `-MaxEnvironments` safety parameter (Phase 1 nice-to-have)

### 3.3 Copilot Studio Premium Licensing — LOW

**Risk:** Querying Copilot Studio bot metadata via Dataverse may require specific licensing for the querying user/service principal.

**Mitigation:**
- Document licensing prerequisites in `PREREQUISITES.md`
- The Power Platform Admin role can typically read Dataverse system tables including `bot`
- Validate during scaffold plan (01-01) discovery task

### 3.4 Output Volume — MEDIUM

**Risk:** Unlike v6 (one result per environment), v7 produces one result per agent. A tenant with 50 environments averaging 10 agents each yields 500 results, which is significantly higher output volume.

**Mitigation:**
- Default to violations-only output (no `-IncludeCompliant`)
- `-OutputFormat Table` should use compact per-agent table format
- Add `-Top N` parameter for capped output during exploration
- Summary statistics (total agents, compliant count, violation count by severity) in all output formats

### 3.5 Bot Table Query Performance — LOW

**Risk:** Large environments may contain hundreds of bots. Unbounded queries could be slow.

**Mitigation:**
- Use OData `$select` to retrieve only needed columns
- Use `$filter` to limit to active bots (`statecode eq 0`) by default
- Page results if Dataverse returns partial pages (standard OData paging)

## 4. Recommended Approach

### 4.1 Implementation Order

```
01-01-PLAN (Wave 1 — scaffold)
├── Solution folder structure
├── CMMClient.psm1 (Dataverse client with CMM_ prefix)
├── Connect-EnvironmentDataverse.ps1 (per-env auth helper)
├── Get-ZoneClassification.ps1 (reuse from v6)
├── Get-ExpectedModerationLevel.ps1 (zone → level lookup)
├── Test-ParameterValidation.ps1 (moderation level validators)
├── moderation-baseline.json (zone → level → severity → regulatory)
├── README.md, CHANGELOG.md, docs/PREREQUISITES.md
└── ** DISCOVERY: Query test env bot/botcomponent tables to confirm schema **

01-02-PLAN (Wave 2 — core scripts)
├── Get-AgentModerationSettings.ps1
│   ├── Enumerate environments (Get-AdminPowerAppEnvironment + filters)
│   ├── For each env: Connect-EnvironmentDataverse → query bot table
│   ├── Extract content moderation level from bot/botcomponent
│   ├── Apply agent filters (published/draft, status)
│   └── Return PSCustomObject[] with agent-grain results
└── Compare-ModerationCompliance.ps1
    ├── Load moderation-baseline.json
    ├── Compare each agent's moderation level vs. zone expected
    ├── Classify violations by severity matrix
    ├── Include regulatory context strings
    └── Support -IncludeCompliant and pipeline input

01-03-PLAN (Wave 2 — orchestrator)
└── Test-ContentModerationCompliance.ps1
    ├── SupportsShouldProcess (WhatIf / dry-run)
    ├── Query → Compare → Report pipeline
    ├── OutputFormat (Table/JSON/Object)
    ├── Filter params (ExcludeSandbox, ExcludeTrial, ExcludeDefault)
    ├── GracePeriodHours, DataverseUrl
    ├── Summary statistics banner
    └── Agent-level detail table
```

### 4.2 moderation-baseline.json Structure

```json
{
  "version": "1.0.0",
  "description": "Expected content moderation levels per governance zone",
  "zones": {
    "Zone1": {
      "description": "Personal Productivity - Medium minimum",
      "minimumModerationLevel": "Medium",
      "violations": {
        "Low": { "severity": "High", "regulatory": "Governance gap — Below minimum threshold" }
      }
    },
    "Zone2": {
      "description": "Team Collaboration - High required",
      "minimumModerationLevel": "High",
      "violations": {
        "Low": { "severity": "High", "regulatory": "SOX 404 — Inadequate content controls for shared agent" },
        "Medium": { "severity": "Medium", "regulatory": "Best practice uplift recommended for team agents" }
      }
    },
    "Zone3": {
      "description": "Enterprise Managed - High required",
      "minimumModerationLevel": "High",
      "violations": {
        "Low": { "severity": "Critical", "regulatory": "FINRA 3110 — Unmoderated customer-facing AI agent" },
        "Medium": { "severity": "High", "regulatory": "GLBA 501(b) — Insufficient content protection for enterprise agent" }
      }
    },
    "Unknown": {
      "description": "Unclassified environment",
      "minimumModerationLevel": "High",
      "violations": {
        "unclassified": { "severity": "Warning", "regulatory": "Governance gap — Environment not assigned to zone" }
      }
    }
  }
}
```

### 4.3 Get-AgentModerationSettings.ps1 Output Schema

Each result object represents a single agent:

```powershell
[PSCustomObject]@{
    AgentId                 = [string]   # bot.botid
    AgentName               = [string]   # bot.name
    AgentStatus             = [string]   # Published/Draft/Inactive
    ContentModerationLevel  = [string]   # Low/Medium/High
    EnvironmentId           = [string]   # Power Platform environment ID
    EnvironmentDisplayName  = [string]   # Environment display name
    EnvironmentType         = [string]   # Production/Sandbox/Default/etc.
    Zone                    = [string]   # Zone1/Zone2/Zone3/Unknown
    DataverseUrl            = [string]   # Environment's Dataverse endpoint
    LastPublished           = [datetime] # bot.publishedon
    RetrievedAt             = [datetime] # Query timestamp
}
```

### 4.4 Compare-ModerationCompliance.ps1 Output Schema

Each result object represents a compliance assessment per agent:

```powershell
[PSCustomObject]@{
    AgentId                 = [string]
    AgentName               = [string]
    EnvironmentDisplayName  = [string]
    Zone                    = [string]
    CurrentModerationLevel  = [string]   # Actual: Low/Medium/High
    ExpectedModerationLevel = [string]   # From baseline
    IsCompliant             = [bool]
    Severity                = [string]   # Critical/High/Medium/Warning/null
    RegulatoryContext       = [string]   # From baseline
    AgentStatus             = [string]
}
```

## 5. Dependencies

### 5.1 PowerShell Module Dependencies

| Module | Purpose | Install |
|--------|---------|---------|
| `Microsoft.PowerApps.Administration.PowerShell` | Environment enumeration | `Install-Module` from PSGallery |
| `Az.Accounts` (optional) | Token acquisition for Dataverse Web API | `Install-Module` from PSGallery |

No Graph SDK dependency (unlike v5 SSC). Dataverse access is via REST (`Invoke-RestMethod`).

### 5.2 Infrastructure Dependencies

| Dependency | Required By | Notes |
|------------|-------------|-------|
| Power Platform Admin role | Environment enumeration | Same as v6 |
| Dataverse instance per environment | Agent query | Environments without Dataverse are skipped |
| Network access to `*.crm.dynamics.com` | Dataverse Web API calls | May require proxy configuration |

### 5.3 Upstream Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| v6 AAM `Get-ZoneClassification.ps1` | Complete (shipped) | Reuse directly |
| ELM Dataverse table (`fsi_environment`) | Optional (naming convention fallback exists) | No risk — fallback covers |
| Copilot Studio bot Dataverse schema | Needs discovery | Mitigated by 01-01 discovery task |

### 5.4 Key Unknowns Requiring Discovery (01-01 Task)

1. **Exact column name** for content moderation level in `bot` or `botcomponent` table
2. **Value representation** — string ("High"/"Medium"/"Low") vs. integer enum vs. JSON blob property
3. **Component type filter** — which `botcomponent.componenttype` value corresponds to generative AI settings
4. **Availability of moderation setting on draft/unpublished agents** — may only be present after first publish

### 5.5 Downstream Consumers

| Phase | What It Needs from Phase 1 |
|-------|----------------------------|
| Phase 2 | `CMMClient.psm1` interface for writing to Dataverse tables |
| Phase 3 | `Get-AgentModerationSettings.ps1` output for drift comparison |
| Phase 4 | `Test-ContentModerationCompliance.ps1` JSON output for evidence hashing |

---

*Research completed: 2026-02-09 | Researcher: Copilot (Claude Opus 4.6)*
