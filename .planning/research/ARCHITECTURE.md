# Architecture Patterns

**Domain:** Session Security Configurator for FSI-AgentGov-Solutions
**Researched:** 2026-02-06
**Overall Confidence:** HIGH (derived from direct examination of existing codebase)

---

## Executive Summary

The Session Security Configurator (SSC) enforces and monitors session-level Conditional Access controls (sign-in frequency, persistent browser, MCAS session control) per governance zone. It occupies a specific niche between the existing Conditional Access Automation (CAA) solution and the Audit Configuration Validator (ACV) -- focusing exclusively on session control properties of CA policies rather than the broader policy lifecycle that CAA handles.

The architecture follows the established Tier 2 pattern (PowerShell validation + Python Dataverse infrastructure + Power Automate orchestration) and integrates with three existing solutions: Environment Lifecycle Management (zone classification source), Conditional Access Automation (policy deployment -- no duplication), and Compliance Dashboard (evidence sink for Control 1.23 scoring).

---

## Boundary Definition: Session Security Configurator vs Conditional Access Automation

This is the most critical architectural decision. The boundary must be clean to avoid duplication.

### What Conditional Access Automation (CAA) Already Does

Based on examination of `conditional-access-automation/`:

| Capability | CAA Script | Status |
|------------|-----------|--------|
| Deploy CA policy templates | `Deploy-CAPolicies.ps1` | Done |
| Register service principal | `Register-ServicePrincipal.ps1` | Done |
| Policy compliance/coverage check | `Test-PolicyCompliance.ps1` | Done |
| Policy drift detection (any property) | `Watch-PolicyDrift.ps1` | Done (planned) |
| Evidence export | `Export-PolicyEvidence.ps1` | Done (planned) |
| ELM integration (auto-deploy on provision) | Config-based | Done |

CAA session controls today are statically defined in templates (e.g., `CA-CopilotStudio-Zone3.json` sets `signInFrequency: 1 hour` and `persistentBrowser: never`). CAA deploys these but does not deeply validate, remediate, or report on session control compliance as a specialized concern.

### What Session Security Configurator (SSC) Adds

| Capability | SSC Scope | Why Not in CAA |
|------------|-----------|----------------|
| **Session control baseline per zone** | Define expected session settings (sign-in frequency, persistent browser, MCAS controls) per zone, per application | CAA templates embed these but don't treat them as a separately validatable concern |
| **Session-specific drift detection** | Detect when session controls specifically weaken (e.g., timeout increased from 1hr to 8hr) | CAA `Watch-PolicyDrift.ps1` detects any change -- SSC provides session-specific severity and remediation context |
| **Session control remediation** | Auto-remediate session control drift back to zone baseline | CAA reports drift but does not auto-fix |
| **Authentication context validation** | Validate that authentication contexts (c1-c5) are configured per Control 1.23 | Not in CAA scope at all |
| **Step-up authentication monitoring** | Track step-up failures, bypass attempts | Control 1.23 specific |
| **Session evidence for Compliance Dashboard** | Export session-specific evidence (distinct from CAA's full-policy evidence) | CAA exports entire policy state; SSC exports session-specific compliance |

### The Clean Boundary

```
CAA owns:                          SSC owns:
- Policy lifecycle (CRUD)          - Session control baselines (definition)
- Template management              - Session control validation (pass/fail)
- Full policy drift                - Session drift detection + remediation
- Policy coverage gaps             - Authentication context validation
- Policy evidence (full state)     - Step-up monitoring
                                   - Session-specific evidence export
```

**Integration point:** SSC reads CA policies via Graph API (same as CAA) but never creates, modifies, or deletes policies. If SSC detects session drift, it can either:
1. Auto-remediate via Graph API `PATCH` on session controls only, OR
2. Alert and defer to CAA for remediation (safer, recommended for Zone 3)

**Recommendation:** SSC should NOT modify CA policies directly in Zone 3 (too risky for automated remediation of enterprise controls). For Zone 1/2, auto-remediation is acceptable. For Zone 3, SSC alerts and creates a remediation ticket.

---

## Recommended Architecture

```
                    +-------------------------------------------------+
                    |       Session Security Configurator (SSC)        |
                    |       (session-security-config/)                 |
                    +-------------------------------------------------+
                    |                                                   |
                    |  +-------------+  +--------------------+         |
                    |  |  Baseline   |  |   Session Drift    |         |
                    |  |  Manager    |  |   Detector         |         |
                    |  +------+------+  +--------+-----------+         |
                    |         |                   |                     |
                    |  +------+------+  +--------+-----------+         |
                    |  |  AuthContext |  |   Evidence          |        |
                    |  |  Validator  |  |   Exporter          |        |
                    |  +-------------+  +--------------------+         |
                    +-------------------------+------------------------+
                                              |
              +-------------------------------+------------------------------+
              |                               |                              |
              v                               v                              v
    +------------------+         +-------------------+         +-------------------+
    |  Microsoft        |         |  Dataverse         |         |  Power Automate    |
    |  Graph API        |         |  (SSC tables)      |         |  (SSC flows)       |
    |  (read CA/auth)   |         |                    |         |                    |
    +------------------+         +-------------------+         +-------------------+
              |                               |                              |
              v                               v                              v
    +------------------+         +-------------------+         +-------------------+
    |  Entra ID         |         |  ELM zone data     |         |  Teams / Email     |
    |  CA Policies      |         |  (fsi_er_zone)     |         |  (alerts)          |
    |  Auth Contexts    |         |  ACV environment   |         |                    |
    |  Sign-in Logs     |         |  registry          |         |                    |
    +------------------+         +-------------------+         +-------------------+
```

### Component Boundaries

| Component | Responsibility | Communicates With | New or Existing |
|-----------|---------------|-------------------|-----------------|
| **Baseline Manager** | Define expected session settings per zone per application | Dataverse (write baselines), Graph API (read current CA policies) | **New** |
| **Session Drift Detector** | Compare live CA session controls against stored baselines | Graph API (read), Dataverse (read baselines, write violations), Power Automate (trigger alerts) | **New** |
| **AuthContext Validator** | Validate authentication contexts (c1-c5) exist and are bound to CA policies | Graph API (read auth contexts, read CA policies) | **New** |
| **Evidence Exporter** | Export session compliance evidence with SHA-256 hashing | Dataverse (read history), File system (write JSON) | **New** (follows ACV `Export-AuditValidationEvidence.ps1` pattern) |
| **ELM EnvironmentRegistry** | Provides zone classification for each environment | Read only -- no changes | **Existing** (`fsi_EnvironmentRegistry` or `fsi_EnvironmentRequest`) |
| **ACV EnvironmentRegistry** | Provides environment catalog with zone + last validated timestamp | Read only -- no changes | **Existing** (`fsi_EnvironmentRegistry`) |
| **Compliance Dashboard** | Receives session evidence for Control 1.23 scoring | Write to `fsi_complianceevidence` table | **Existing** |

---

## Data Flow

### Flow 1: Session Baseline Definition

```
Admin defines zone session requirements
    |
    v
PowerShell: New-SessionBaseline.ps1
    |  Reads: Zone definition (which apps, which zones)
    |  Reads: Current CA policies from Graph API (to pre-populate)
    |  Writes: fsi_SessionBaseline rows to Dataverse
    v
Dataverse: fsi_SessionBaseline table
    (Zone 1: signInFrequency=8h, persistentBrowser=allowed)
    (Zone 2: signInFrequency=4h, persistentBrowser=never)
    (Zone 3: signInFrequency=1h, persistentBrowser=never, mcasProxy=required)
```

### Flow 2: Session Drift Detection (Scheduled)

```
Power Automate: SSC-SessionDriftDetector (daily)
    |
    v Trigger: Recurrence (daily 6 AM UTC)
    |
    v Calls PowerShell (Azure Automation runbook)
PowerShell: Invoke-SessionDriftScan.ps1
    |  Reads: fsi_SessionBaseline from Dataverse (expected state)
    |  Reads: CA policies from Graph API (actual state)
    |  Reads: fsi_EnvironmentRegistry from Dataverse (zone mapping)
    |  Compares: session controls per zone per application
    |  Writes: fsi_SessionValidationHistory (pass/fail per check)
    |
    +-- No drift -> Log Passed result
    |
    +-- Drift detected ->
            |  Writes: fsi_SessionDriftViolation to Dataverse
            |  Returns: violation details to Power Automate
            v
        Power Automate: Route alert
            |
            +-- Zone 1/2: Auto-remediate via Graph API PATCH
            |       |  Writes: remediation record to history
            |       |  Sends: informational Teams notification
            |
            +-- Zone 3: Alert only (no auto-remediation)
                    |  Sends: critical Teams adaptive card
                    |  Creates: fsi_complianceexception in Dashboard
```

### Flow 3: Authentication Context Validation

```
PowerShell: Test-AuthenticationContexts.ps1
    |  Reads: Expected auth contexts from fsi_SessionBaseline
    |         (c1=Financial Transaction, c2=Data Export, etc.)
    |  Reads: Actual auth contexts from Graph API
    |         (GET /identity/conditionalAccess/authenticationContextClassReferences)
    |  Reads: CA policies referencing auth contexts
    |  Validates: Each context exists, is bound to appropriate CA policy
    |  Writes: fsi_SessionValidationHistory
    v
Results: Pass/Fail per auth context
```

### Flow 4: Evidence Export

```
PowerShell: Export-SessionSecurityEvidence.ps1
    |  Reads: fsi_SessionValidationHistory (date range)
    |  Reads: fsi_SessionDriftViolation (date range)
    |  Reads: fsi_SessionBaseline (current baselines)
    |  Generates: JSON evidence package
    |  Calculates: SHA-256 hash
    |  Writes: evidence.json + evidence.json.sha256
    |
    v Optionally pushes to Compliance Dashboard
    |  Writes: fsi_complianceevidence row
    |          (controlassessmentid = Control 1.23 assessment)
    |          (evidencetype = 5: Test Result)
    |          (hash = SHA-256 of evidence file)
```

---

## Dataverse Schema (New Tables)

All tables follow the established `fsi_` publisher prefix convention with solution-specific prefix `SSC`.

### Table: fsi_SessionBaseline

Defines expected session control configuration per zone per application.

| Column | Type | Description |
|--------|------|-------------|
| `fsi_sessionbaselineid` | GUID | Primary key |
| `fsi_name` | Text | Descriptive name (e.g., "Zone 3 - Copilot Studio") |
| `fsi_zone` | Choice (fsi_acv_zone) | Zone 1/2/3 (reuse existing global option set) |
| `fsi_applicationid` | Text | Entra app ID targeted |
| `fsi_applicationname` | Text | Display name (Copilot Studio, Agent Builder, etc.) |
| `fsi_signinfrequencyvalue` | Integer | Expected sign-in frequency value |
| `fsi_signinfrequencyunit` | Choice | hours / days |
| `fsi_persistentbrowser` | Choice | always / never / conditional |
| `fsi_mcasproxyenabled` | Boolean | Whether MCAS session proxy required |
| `fsi_mcaspolicyid` | Text | MCAS session policy ID (if applicable) |
| `fsi_authcontextrequired` | Boolean | Whether auth context binding expected |
| `fsi_authcontextids` | Text | Comma-separated auth context IDs (c1,c2,etc.) |
| `fsi_isactive` | Boolean | Whether this baseline is enforced |
| `createdon` | DateTime | Auto |
| `modifiedon` | DateTime | Auto |

**Ownership:** Organization-owned (admin-managed, not user-scoped)

### Table: fsi_SessionValidationHistory

Immutable validation results (same pattern as ACV's `fsi_AuditValidationHistory`).

| Column | Type | Description |
|--------|------|-------------|
| `fsi_sessionvalidationhistoryid` | GUID | Primary key |
| `fsi_name` | Text | SESSION-{zone}-{app}-{timestamp} |
| `fsi_runid` | GUID | Correlates records in one scan execution |
| `fsi_zone` | Choice (fsi_acv_zone) | Zone at time of validation (reuse existing) |
| `fsi_applicationid` | Text | Entra app ID |
| `fsi_validationtype` | Text | SignInFrequency, PersistentBrowser, MCASProxy, AuthContext |
| `fsi_severity` | Choice (fsi_acv_severity) | Passed/Warning/Failed/Error (reuse existing) |
| `fsi_expectedvalue` | Text | Expected configuration (e.g., "signInFrequency=1h") |
| `fsi_actualvalue` | Text | Actual configuration found |
| `fsi_reason` | Text | Human-readable explanation |
| `fsi_driftdetected` | Boolean | Whether this represents a regression from last Passed |
| `fsi_remediationaction` | Choice (fsi_ssc_remediationaction) | None/AutoRemediated/AlertSent/TicketCreated |
| `fsi_timestamp` | DateTime | When validation ran |

**Ownership:** Organization-owned, immutable (remove Write/Delete post-deployment)

### Table: fsi_SessionDriftViolation

Active drift violations tracking (same pattern as Scope Drift Monitor's violation table).

| Column | Type | Description |
|--------|------|-------------|
| `fsi_sessiondriftviolationid` | GUID | Primary key |
| `fsi_name` | Text | DRIFT-{zone}-{app}-{change type} |
| `fsi_zone` | Choice (fsi_acv_zone) | Affected zone (reuse existing) |
| `fsi_applicationid` | Text | Affected application |
| `fsi_changetype` | Choice (fsi_ssc_changetype) | SignInFrequencyWeakened, PersistentBrowserEnabled, MCASDisabled, AuthContextRemoved, PolicyDisabled |
| `fsi_previousvalue` | Text | Before change |
| `fsi_currentvalue` | Text | After change |
| `fsi_changedby` | Text | UPN of actor (from audit log if available) |
| `fsi_detectedat` | DateTime | When drift was detected |
| `fsi_status` | Choice (fsi_ssc_violationstatus) | Open/Remediated/Accepted/Escalated |
| `fsi_remediatedat` | DateTime | When remediated (null if open) |
| `fsi_remediatedby` | Text | Who/what remediated |

**Ownership:** Organization-owned

### Global Option Sets

| Option Set | Values | Notes |
|------------|--------|-------|
| `fsi_acv_zone` | Unclassified(0), Zone 1(1), Zone 2(2), Zone 3(3) | **Reuse existing** -- already global from ACV deployment |
| `fsi_acv_severity` | Passed(1), Warning(2), GracePeriod(3), Failed(4), Error(5) | **Reuse existing** -- already global from ACV deployment |
| `fsi_ssc_changetype` | SignInFrequencyWeakened(1), PersistentBrowserEnabled(2), MCASDisabled(3), AuthContextRemoved(4), PolicyDisabled(5), ExclusionAdded(6) | **New** |
| `fsi_ssc_violationstatus` | Open(1), Remediated(2), Accepted(3), Escalated(4) | **New** |
| `fsi_ssc_remediationaction` | None(0), AutoRemediated(1), AlertSent(2), TicketCreated(3) | **New** |

**Critical note on option set reuse:** The ACV already defines `fsi_acv_zone` and `fsi_acv_severity` as global option sets. The SSC deployment script must check for existing global option sets and reference them rather than creating duplicates. If ACV has not been deployed to the target environment, SSC must create these option sets itself.

---

## Environment Variables (New)

Following the ACV pattern (`fsi_{SOLUTION}_{Variable}`):

| Variable | Default | Description |
|----------|---------|-------------|
| `fsi_SSC_Zone1SignInFrequencyHours` | 8 | Zone 1 sign-in frequency |
| `fsi_SSC_Zone2SignInFrequencyHours` | 4 | Zone 2 sign-in frequency |
| `fsi_SSC_Zone3SignInFrequencyHours` | 1 | Zone 3 sign-in frequency |
| `fsi_SSC_Zone3MCASRequired` | true | Whether Zone 3 requires MCAS proxy |
| `fsi_SSC_AutoRemediateZone1` | true | Auto-remediate Zone 1 drift |
| `fsi_SSC_AutoRemediateZone2` | true | Auto-remediate Zone 2 drift |
| `fsi_SSC_AutoRemediateZone3` | false | Auto-remediate Zone 3 drift (default OFF) |
| `fsi_SSC_TeamsGroupId` | (blank) | Teams group for alerts |
| `fsi_SSC_TeamsChannelId` | (blank) | Teams channel for alerts |
| `fsi_SSC_SecurityTeamEmail` | (blank) | Email for Zone 3 escalations |

---

## Connection References (New)

| Logical Name | Display Name | Connector |
|-------------|-------------|-----------|
| `fsi_cr_dataverse_sessionsecurity` | Dataverse - Session Security Config | `shared_commondataserviceforapps` |
| `fsi_cr_office365_sessionsecurity` | Office 365 - Session Security Config | `shared_office365` |
| `fsi_cr_teams_sessionsecurity` | Teams - Session Security Config | `shared_teams` |

---

## Integration Points with Existing Solutions

### 1. Environment Lifecycle Management (ELM) -- Zone Source

**Direction:** SSC reads from ELM

**Integration pattern:** When SSC runs a drift scan, it queries the ELM `fsi_EnvironmentRegistry` (or ACV's copy) to determine which zone each environment belongs to. This zone drives which session baseline applies.

**Query:** `GET /api/data/v9.2/fsi_environmentregistries?$filter=fsi_status eq 1` (active environments with zone classification)

**Fallback:** If an environment is not in the registry (Unclassified), SSC applies Zone 1 (least restrictive) defaults and logs a Warning.

### 2. Conditional Access Automation (CAA) -- Policy Source

**Direction:** SSC reads from same Graph API as CAA, but never writes policies

**Integration pattern:** SSC reads CA policies from `GET /identity/conditionalAccess/policies` and extracts only the `sessionControls` block plus grant control context. SSC does NOT deploy, create, modify, or delete CA policies -- that is CAA's exclusive domain.

**Exception:** Auto-remediation in Zone 1/2 uses `PATCH /identity/conditionalAccess/policies/{id}` to update ONLY the `sessionControls` block. This is the one area where SSC writes to the same resource CAA manages. To avoid conflicts:
- SSC only patches `sessionControls` (never `grantControls`, `conditions`, or `state`)
- SSC logs the remediation to Dataverse with before/after values
- CAA's `Watch-PolicyDrift.ps1` will detect SSC's remediation as a "change" -- the SSC remediation record in Dataverse serves as the audit trail explaining why

### 3. Compliance Dashboard -- Evidence Sink

**Direction:** SSC writes to Compliance Dashboard tables

**Integration pattern:** SSC exports session compliance evidence and writes a `fsi_complianceevidence` row linking to the Control 1.23 assessment:

```json
{
  "fsi_name": "Session Security Validation - Q1 2026",
  "fsi_controlassessmentid": "<Control 1.23 assessment GUID>",
  "fsi_evidencetype": 5,
  "fsi_sourceurl": "https://storage.blob.core.windows.net/evidence/session-validation-2026-Q1.json",
  "fsi_description": "Automated session control validation: 24 checks passed, 0 failed",
  "fsi_collecteddate": "2026-03-31T23:59:00Z",
  "fsi_hash": "<SHA-256 of evidence JSON>"
}
```

### 4. Audit Configuration Validator (ACV) -- Pattern Reference

**Direction:** No runtime integration, but SSC follows ACV patterns

SSC reuses these ACV architectural patterns:
- **Immutable history table** (organization-owned, remove Write/Delete post-deploy)
- **Run ID correlation** (GUID linking all records in one execution)
- **Drift detection via baseline comparison** (`Compare-ValidationBaseline.ps1` pattern)
- **Evidence export with SHA-256** (`Export-AuditValidationEvidence.ps1` pattern)
- **Python deployment scripts** (`deploy.py`, `create_dataverse_schema.py`, `create_environment_variables.py`, `create_connection_references.py`)
- **Azure Automation runbook wrapper** (`Start-*Runbook.ps1` pattern)
- **Adaptive card alert templates** (JSON templates in `src/`)

---

## Directory Structure

Following the established solution directory pattern:

```
session-security-config/
+-- CHANGELOG.md
+-- README.md
+-- docs/
|   +-- prerequisites.md
|   +-- dataverse-schema.md
|   +-- baseline-configuration.md
|   +-- flow-configuration.md
|   +-- evidence-export-guide.md
|   +-- troubleshooting.md
+-- scripts/
|   +-- ssc_client.py                      # Dataverse Web API client (based on acv_client.py)
|   +-- create_dataverse_schema.py         # Table creation
|   +-- create_environment_variables.py    # Zone threshold variables
|   +-- create_connection_references.py    # Dataverse, Office 365, Teams
|   +-- deploy.py                          # Orchestrator (dry-run, idempotent)
|   +-- requirements.txt                   # Python dependencies
|   +-- New-SessionBaseline.ps1            # Define zone baselines
|   +-- Invoke-SessionDriftScan.ps1        # Core drift detection
|   +-- Test-AuthenticationContexts.ps1    # Auth context validation
|   +-- Export-SessionSecurityEvidence.ps1 # Evidence export (SHA-256)
|   +-- Test-EvidenceIntegrity.ps1         # Hash verification
|   +-- Start-SessionValidationRunbook.ps1 # Azure Automation wrapper
|   +-- private/
|       +-- Compare-SessionBaseline.ps1    # Baseline comparison helper
|       +-- Connect-GraphSession.ps1       # Graph API auth helper
|       +-- Write-ValidationResult.ps1     # Dataverse write helper
+-- src/
|   +-- session-drift-flow.json            # Power Automate flow definition
|   +-- adaptive-card-session-alert.json   # Teams alert template
|   +-- adaptive-card-zone3-escalation.json # Zone 3 critical alert
+-- templates/
    +-- session-baselines/
        +-- zone1-defaults.json            # Default Zone 1 session settings
        +-- zone2-defaults.json            # Default Zone 2 session settings
        +-- zone3-defaults.json            # Default Zone 3 session settings
```

---

## Patterns to Follow

### Pattern 1: Immutable Validation History (from ACV)

**What:** All validation results are written once and never modified. The history table uses organization ownership and security roles strip Write/Delete post-deployment.

**When:** Every validation scan produces rows in `fsi_SessionValidationHistory`.

**Why:** Regulatory examination requires tamper-evident audit trail. FINRA 4511 and SEC 17a-4 mandate immutable record retention.

### Pattern 2: Run ID Correlation (from ACV)

**What:** Each scan execution generates a GUID `RunId`. All Dataverse records from that scan share the RunId.

**When:** `Invoke-SessionDriftScan.ps1` generates a RunId at start and passes it to all write operations.

**Why:** Enables querying "show me everything from the scan that ran at 6 AM on Feb 3" -- critical for troubleshooting and evidence export.

### Pattern 3: Zone-Parameterized Validation (from ACV)

**What:** Validation thresholds are driven by zone classification, not hardcoded.

**When:** SSC reads the environment's zone from the registry, then looks up the baseline for that zone.

**Why:** Zone 1/2/3 have different session requirements (8h/4h/1h sign-in frequency). Hardcoding would prevent customer customization.

### Pattern 4: Dry-Run Deployment (from ACV, ELM)

**What:** All deployment scripts support `--dry-run` flag that previews changes without executing.

**When:** `deploy.py --dry-run` shows what tables, variables, and connection references would be created.

**Why:** Production Dataverse environments require change control. Preview-before-commit is table stakes.

### Pattern 5: Idempotent Schema Creation (from ACV, ELM)

**What:** Schema creation scripts check for existing resources before creating. Running twice produces the same result.

**When:** `create_dataverse_schema.py` checks `EntityDefinitions` for existing tables before attempting creation.

**Why:** Re-running deployment after a partial failure must succeed without errors.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Duplicating CA Policy Lifecycle

**What:** SSC must NOT deploy, create, or delete CA policies.

**Why bad:** CAA already handles policy lifecycle. Two solutions managing the same Graph API resources creates conflicting writes, race conditions, and audit confusion.

**Instead:** SSC reads CA policies and validates session controls only. If session settings need changing, SSC either auto-remediates a narrow `sessionControls` PATCH (Zone 1/2) or alerts for manual remediation via CAA (Zone 3).

### Anti-Pattern 2: Hardcoded Session Thresholds

**What:** Embedding session timeout values directly in PowerShell scripts.

**Why bad:** Different organizations may have different requirements. NIST 800-63B suggests timeouts but doesn't mandate specific values.

**Instead:** Store thresholds in Dataverse environment variables (`fsi_SSC_Zone*`) and baseline table. Scripts read at runtime.

### Anti-Pattern 3: Creating Duplicate Zone Option Sets

**What:** Creating `fsi_ssc_zone` when `fsi_acv_zone` already exists as a global option set.

**Why bad:** Multiple zone option sets with identical values create mapping confusion and make cross-solution queries harder.

**Instead:** Deployment script checks for existing global option sets (`fsi_acv_zone`, `fsi_acv_severity`) and reuses them. Only create new option sets for SSC-specific choices (`fsi_ssc_changetype`, `fsi_ssc_violationstatus`).

### Anti-Pattern 4: Polling Graph API Too Frequently

**What:** Running session drift detection every 15 minutes.

**Why bad:** Graph API has throttling limits. Daily detection is sufficient for session controls which change infrequently.

**Instead:** Default to daily scans. For Zone 3, optionally support an Entra ID audit log trigger (policy change event) for near-real-time detection via a separate flow.

---

## Power Automate Flows

### Flow 1: SSC-SessionDriftDetector

**Trigger:** Recurrence (daily, 6:00 AM UTC -- same time as ACV flows for operational consistency)

**Actions:**
1. Initialize variables (DataverseUrl, TenantId, RunId)
2. Call Azure Automation to run `Start-SessionValidationRunbook.ps1`
3. Wait for completion
4. Query `fsi_SessionValidationHistory` for this RunId where `driftdetected = true`
5. If drift found:
   - For Zone 1/2 with auto-remediation enabled: Call remediation child flow
   - For Zone 3 or auto-remediation disabled: Send adaptive card alert
   - For all: Write summary to `fsi_SessionDriftViolation`
6. Send completion summary (Teams informational)

### Flow 2: SSC-Zone3Escalation (Optional)

**Trigger:** Dataverse row created in `fsi_SessionDriftViolation` where zone = 3

**Actions:**
1. Send critical adaptive card to security team
2. Create approval request for remediation decision
3. If approved: Flag for CAA manual remediation
4. If rejected (accepted risk): Update violation status, create `fsi_complianceexception`

---

## Suggested Build Order

Based on dependencies and the established ACV phased approach:

### Phase 1: PowerShell Core (No Dataverse dependency)

Build the core validation logic first, testable standalone:

1. `New-SessionBaseline.ps1` -- Define baselines (outputs JSON locally)
2. `Invoke-SessionDriftScan.ps1` -- Core drift scan (reads Graph API, compares to JSON baseline, outputs JSON results)
3. `Test-AuthenticationContexts.ps1` -- Auth context validation
4. `private/Compare-SessionBaseline.ps1` -- Baseline comparison helper
5. `private/Connect-GraphSession.ps1` -- Graph API authentication

**Deliverable:** Scripts that can validate session controls against a local JSON baseline file, outputting results to console/file.

### Phase 2: Dataverse Infrastructure

Deploy Dataverse schema and migrate from local JSON to Dataverse storage:

1. `ssc_client.py` -- Dataverse Web API client (based on `acv_client.py`)
2. `create_dataverse_schema.py` -- Tables and option sets (with reuse detection)
3. `create_environment_variables.py` -- Zone threshold variables
4. `create_connection_references.py` -- Connectors
5. `deploy.py` -- Orchestrator with dry-run
6. Update `Invoke-SessionDriftScan.ps1` to read/write Dataverse
7. Update `New-SessionBaseline.ps1` to write to Dataverse

**Deliverable:** Full Dataverse schema deployed, scripts reading baselines from Dataverse and writing validation history.

### Phase 3: Automation and Alerting

Add scheduled execution and alert routing:

1. `Start-SessionValidationRunbook.ps1` -- Azure Automation wrapper
2. `src/session-drift-flow.json` -- Power Automate flow definition
3. `src/adaptive-card-session-alert.json` -- Alert template
4. `src/adaptive-card-zone3-escalation.json` -- Zone 3 critical alert
5. Auto-remediation logic for Zone 1/2

**Deliverable:** Daily automated scans with Teams alerts and optional auto-remediation.

### Phase 4: Evidence Export and Dashboard Integration

Complete the compliance integration:

1. `Export-SessionSecurityEvidence.ps1` -- Evidence export with SHA-256
2. `Test-EvidenceIntegrity.ps1` -- Hash verification
3. Compliance Dashboard integration (write to `fsi_complianceevidence`)
4. Documentation suite

**Deliverable:** Evidence export supporting FINRA/SEC examinations, integrated with Compliance Dashboard for Control 1.23 scoring.

---

## Graph API Permissions Required

| Permission | Type | Purpose |
|-----------|------|---------|
| `Policy.Read.All` | Application | Read CA policies and session controls |
| `Policy.ReadWrite.ConditionalAccess` | Application | Auto-remediate session controls (Zone 1/2 only) |
| `AuthenticationContext.Read.All` | Application | Read authentication context definitions |
| `AuditLog.Read.All` | Application | Read sign-in logs for step-up monitoring |
| `Directory.Read.All` | Application | Read group memberships for policy target resolution |

**Note:** If auto-remediation is disabled for all zones, `Policy.ReadWrite.ConditionalAccess` can be downgraded to `Policy.Read.All`, reducing the attack surface of the service principal.

---

## Scalability Considerations

| Concern | At 10 environments | At 100 environments | At 500+ environments |
|---------|---------------------|----------------------|----------------------|
| Graph API calls | ~20 calls/scan | ~200 calls/scan | Batch requests, throttle handling |
| Dataverse writes | ~40 rows/scan | ~400 rows/scan | Bulk create API |
| Scan duration | <2 minutes | ~10 minutes | Parallel batches (Azure Automation) |
| Alert volume | Individual alerts | Digest summaries | Exception-only alerting |

---

## Security Considerations

1. **Service Principal scope:** SSC service principal should have minimal permissions. If auto-remediation is disabled, read-only Graph API permissions suffice.
2. **Immutable history:** Remove Write/Delete from security roles post-deployment (same as ACV pattern).
3. **Zone 3 remediation:** Default to alert-only for Zone 3. Auto-remediation of enterprise CA policies is high-risk and should require explicit opt-in with documented approval.
4. **Credential storage:** Use Azure Key Vault for service principal credentials (same as CAA pattern with `Register-ServicePrincipal.ps1`).
5. **Break-glass exclusion:** SSC must recognize and not flag break-glass account exclusions as violations.

---

## Verification Points

Before marking architecture complete:

- [ ] All components follow established solution patterns (PowerShell + Power Automate + Dataverse)
- [ ] Connection references use `fsi_cr_*` naming convention
- [ ] Environment variables use `fsi_SSC_*` naming convention
- [ ] Dataverse tables use `fsi_` publisher prefix
- [ ] Immutable audit log table follows ACV pattern (org-owned, append-only)
- [ ] Teams notifications use native connector (not deprecated webhooks)
- [ ] Evidence export includes SHA-256 integrity hashing
- [ ] Build order accounts for component dependencies
- [ ] Integration points with existing solutions documented
- [ ] Boundary with Conditional Access Automation explicitly defined
- [ ] Dataverse table naming follows `fsi_` convention throughout
- [ ] Global option set reuse strategy documented (fsi_acv_zone, fsi_acv_severity)

---

## Sources

**HIGH Confidence (Read directly from solution code):**

- `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/README.md` -- v1.0.0 architecture, phased build pattern
- `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/create_dataverse_schema.py` -- Option set definitions, table structure, publisher prefix pattern
- `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/create_environment_variables.py` -- Environment variable naming convention
- `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/create_connection_references.py` -- Connection reference naming
- `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/private/Compare-ValidationBaseline.ps1` -- Drift detection pattern
- `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Export-AuditValidationEvidence.ps1` -- Evidence export with SHA-256
- `/Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/src/tenant-validation-flow.json` -- Power Automate flow structure
- `/Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/README.md` -- CAA scope, zone requirements, session controls in templates
- `/Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Deploy-CAPolicies.ps1` -- Policy deployment scope
- `/Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Test-PolicyCompliance.ps1` -- Compliance check scope
- `/Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/docs/compliance-monitoring.md` -- Drift detection and evidence export scope
- `/Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/templates/CA-CopilotStudio-Zone3.json` -- Session controls in templates (signInFrequency, persistentBrowser)
- `/Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/templates/CA-CopilotStudio-Zone1.json` -- Zone 1 session controls
- `/Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/CHANGELOG.md` -- WIP status, no session-specific features
- `/Users/admin/dev/FSI-AgentGov-Solutions/scope-drift-monitor/README.md` -- Drift detection pattern, violation tracking
- `/Users/admin/dev/FSI-AgentGov-Solutions/environment-lifecycle-management/scripts/create_dataverse_schema.py` -- Zone option sets, ELM data model
- `/Users/admin/dev/FSI-AgentGov-Solutions/compliance-dashboard/README.md` -- Dashboard architecture, evidence integration
- `/Users/admin/dev/FSI-AgentGov-Solutions/compliance-dashboard/docs/dataverse-schema.md` -- `fsi_complianceevidence` table structure
- `/Users/admin/dev/FSI-AgentGov/docs/controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md` -- Control 1.23 requirements, auth contexts (c1-c5), zone requirements

**MEDIUM Confidence (Training data, verify with official docs):**

- Microsoft Graph API endpoint `GET /identity/conditionalAccess/policies` -- CA policy read
- Microsoft Graph API endpoint `PATCH /identity/conditionalAccess/policies/{id}` -- Session control remediation
- Microsoft Graph API endpoint `GET /identity/conditionalAccess/authenticationContextClassReferences` -- Auth context read
- Graph API permissions model for Conditional Access

**LOW Confidence (Needs verification):**

- MCAS session proxy integration via CA session controls -- exact configuration path needs verification with current Defender for Cloud Apps documentation
- Whether `AuthenticationContext.Read.All` is the correct permission scope name (may have been renamed in recent Graph API updates)

---

*Session Security Configurator Architecture Research - February 2026*
