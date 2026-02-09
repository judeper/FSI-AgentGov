---
phase: 04-evidence-export-framework-integration
plan: SSC-03
type: execute
wave: 2
depends_on: ["04-SSC-01"]
files_modified:
  - FSI-AgentGov-Solutions/session-security-configurator/README.md
  - FSI-AgentGov-Solutions/session-security-configurator/CHANGELOG.md
  - FSI-AgentGov-Solutions/session-security-configurator/docs/EVIDENCE-EXPORT-GUIDE.md
  - FSI-AgentGov-Solutions/session-security-configurator/docs/PREREQUISITES.md
  - FSI-AgentGov-Solutions/session-security-configurator/docs/DATAVERSE-SCHEMA.md
  - FSI-AgentGov-Solutions/session-security-configurator/docs/TROUBLESHOOTING.md
autonomous: true

must_haves:
  truths:
    - "README.md reflects v1.0.0 complete status with all phases documented"
    - "README.md includes prerequisites section with licensing, roles, and module requirements"
    - "Documentation covers Dataverse schema (3 tables, option sets)"
    - "Evidence export guide provides step-by-step instructions for export and verification"
    - "Troubleshooting guide covers common issues with error codes and remediation"
    - "CHANGELOG includes Phase 4 entries for evidence export scripts"
  artifacts:
    - path: "FSI-AgentGov-Solutions/session-security-configurator/README.md"
      provides: "Complete solution README with Phase 4 content"
      contains: "Export-SessionSecurityEvidence"
    - path: "FSI-AgentGov-Solutions/session-security-configurator/docs/PREREQUISITES.md"
      provides: "Prerequisites documentation"
      contains: "Microsoft 365 E5"
    - path: "FSI-AgentGov-Solutions/session-security-configurator/docs/DATAVERSE-SCHEMA.md"
      provides: "Dataverse schema documentation"
      contains: "fsi_ValidationHistory"
    - path: "FSI-AgentGov-Solutions/session-security-configurator/docs/EVIDENCE-EXPORT-GUIDE.md"
      provides: "Evidence export instructions"
      contains: "Export-SessionSecurityEvidence"
    - path: "FSI-AgentGov-Solutions/session-security-configurator/docs/TROUBLESHOOTING.md"
      provides: "Troubleshooting guide"
      contains: "Common Issues"
    - path: "FSI-AgentGov-Solutions/session-security-configurator/CHANGELOG.md"
      provides: "Phase 4 release notes"
      contains: "Evidence Export"
  key_links:
    - from: "README.md Quick Start"
      to: "Export-SessionSecurityEvidence.ps1"
      via: "Step 5 evidence export"
      pattern: "Export-SessionSecurityEvidence"
    - from: "README.md Documentation section"
      to: "docs/EVIDENCE-EXPORT-GUIDE.md"
      via: "documentation link"
      pattern: "EVIDENCE-EXPORT-GUIDE"
    - from: "EVIDENCE-EXPORT-GUIDE.md"
      to: "Test-EvidenceIntegrity.ps1"
      via: "verification instructions"
      pattern: "Test-EvidenceIntegrity"
---

<objective>
Create comprehensive documentation suite for Session Security Configurator covering prerequisites, Dataverse schema, deployment, evidence export, and troubleshooting.

Purpose: Administrators need complete documentation to deploy and operate the SSC solution. The README serves as the entry point, and detailed guides in docs/ cover specific operational areas (CEV-03).
Output: Updated README + CHANGELOG, 4 documentation files (prerequisites, schema, evidence export, troubleshooting).
</objective>

<context>
SSC solution structure after Phases 1-3:
- 11 scripts + 4 private helpers (~5,559 lines)
- 3 Dataverse tables (SessionBaseline, ValidationHistory, DriftViolation)
- Power Automate flow for daily validation
- Teams adaptive card alerting

Phase 4 adds:
- Export-SessionSecurityEvidence.ps1
- Get-SSCValidationResults.ps1 (private)
- Test-EvidenceIntegrity.ps1

Reference ACV documentation pattern for consistency.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create PREREQUISITES.md</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/docs/PREREQUISITES.md
  </files>
  <action>
    Create comprehensive prerequisites documentation covering all requirements for SSC deployment.

    Structure:
    ```markdown
    # Session Security Configurator Prerequisites

    ## Licensing Requirements

    | Requirement | Purpose |
    |------------|---------|
    | Microsoft 365 E5 or E5 Security | Conditional Access, authentication contexts, authentication strength policies |
    | Power Platform per-user or per-app license | Dataverse storage, Power Automate flows |
    | Azure Automation (optional) | Scheduled runbook execution |

    ## Role Requirements

    | Role | Purpose |
    |------|---------|
    | Entra ID Security Administrator | Deploy authentication contexts, CA policies |
    | Entra ID Privileged Role Administrator | Configure PIM settings for AI admin roles |
    | Power Platform Administrator | Deploy Dataverse schema, connection references |
    | (Optional) Automation Operator | Execute Azure Automation runbooks |

    ## PowerShell Module Requirements

    - `Microsoft.Graph.Authentication` (v2.0+)
    - `Microsoft.Graph.Identity.SignIns`
    - `Microsoft.Graph.Identity.DirectoryManagement`
    - `MSAL.PS` (for evidence export with service principal)

    Install:
    ```powershell
    Install-Module Microsoft.Graph.Authentication, Microsoft.Graph.Identity.SignIns, Microsoft.Graph.Identity.DirectoryManagement, MSAL.PS -Scope CurrentUser
    ```

    ## Python Requirements

    For Dataverse deployment scripts:
    - Python 3.8+
    - `msal` package
    - `requests` package

    Install:
    ```bash
    pip install -r scripts/requirements.txt
    ```

    ## Dataverse Requirements

    - Dataverse environment with capacity
    - System Customizer or System Administrator role for schema deployment
    - Connection references for Dataverse, Office 365 Outlook, Microsoft Teams

    ## Network Requirements

    - Access to `https://login.microsoftonline.com` (authentication)
    - Access to `https://graph.microsoft.com` (Graph API)
    - Access to `https://*.crm.dynamics.com` (Dataverse API)

    ## Governance Zone Alignment

    SSC enforces zone-specific session controls:

    | Zone | Sign-In Frequency | Auth Strength | Compliant Device |
    |------|------------------|---------------|------------------|
    | Zone 1 | 8 hours | Standard MFA | Not required |
    | Zone 2 | 4 hours | Passwordless | Recommended |
    | Zone 3 | 1 hour | Phishing-resistant | Required |
    ```

    Target: ~100 lines
  </action>
  <verify>
    1. File exists at docs/PREREQUISITES.md
    2. Contains licensing, roles, modules, Python requirements
    3. Contains zone alignment table
  </verify>
  <done>
    PREREQUISITES.md created with comprehensive requirements documentation.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create DATAVERSE-SCHEMA.md</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/docs/DATAVERSE-SCHEMA.md
  </files>
  <action>
    Create Dataverse schema documentation covering all tables, option sets, and relationships.

    Structure:
    ```markdown
    # Session Security Configurator Dataverse Schema

    ## Overview

    SSC uses three Dataverse tables to store session security baselines, validation history, and drift violations.

    ## Tables

    ### fsi_SessionBaseline

    Stores zone-specific session security baseline configurations.

    **Ownership:** User-owned
    **Purpose:** Configuration storage for expected session controls per zone

    | Column | Type | Description |
    |--------|------|-------------|
    | fsi_sessionbaselineid | GUID | Primary key |
    | fsi_name | String | Baseline display name |
    | fsi_zone | Option Set | Zone classification (fsi_acv_zone) |
    | fsi_signinfrequencyminutes | Integer | Expected sign-in frequency in minutes |
    | fsi_authstrength | String | Expected authentication strength policy name |
    | fsi_requirecompliantdevice | Boolean | Whether compliant device is required |
    | fsi_pimintegration | String | PIM configuration (activation window, approval) |
    | fsi_isactive | Boolean | Whether this baseline is the current active baseline |
    | fsi_capturedat | DateTime | Timestamp when baseline was captured |

    ### fsi_ValidationHistory

    Immutable audit log of all validation runs.

    **Ownership:** Organization-owned (immutable after deployment)
    **Purpose:** Regulatory audit trail — SecurityRole removes Write/Delete post-deployment

    | Column | Type | Description |
    |--------|------|-------------|
    | fsi_validationhistoryid | GUID | Primary key |
    | fsi_name | String | Validation display name |
    | fsi_runid | String | Unique identifier for the validation run |
    | fsi_zone | Option Set | Zone validated (fsi_acv_zone) |
    | fsi_severity | Option Set | Result severity (fsi_acv_severity) |
    | fsi_validationtype | Option Set | Validation dimension (fsi_ssc_validationtype) |
    | fsi_signinfrequencyminutes | Integer | Observed sign-in frequency |
    | fsi_authstrength | String | Observed authentication strength |
    | fsi_requirecompliantdevice | Boolean | Observed compliant device requirement |
    | fsi_pimintegration | String | Observed PIM configuration |
    | fsi_breakglassstatus | String | Break-glass exclusion status |
    | fsi_conflictauditstatus | String | CA policy conflict status |
    | fsi_reason | String | Detailed result explanation |
    | fsi_timestamp | DateTime | Validation execution timestamp |

    ### fsi_DriftViolation

    Threshold violations requiring operator attention.

    **Ownership:** User-owned
    **Purpose:** Alert management with acknowledgment workflow

    | Column | Type | Description |
    |--------|------|-------------|
    | fsi_driftviolationid | GUID | Primary key |
    | fsi_name | String | Violation display name |
    | fsi_zone | Option Set | Affected zone (fsi_acv_zone) |
    | fsi_severity | Option Set | Violation severity (fsi_acv_severity) |
    | fsi_validationtype | Option Set | Dimension with drift (fsi_ssc_validationtype) |
    | fsi_expectedvalue | String | Baseline expected value |
    | fsi_observedvalue | String | Actual observed value |
    | fsi_detectedat | DateTime | When drift was detected |
    | fsi_acknowledgedat | DateTime | When operator acknowledged |
    | fsi_acknowledgedby | String | Operator who acknowledged |
    | fsi_remediatedat | DateTime | When drift was remediated |

    ## Option Sets

    ### fsi_acv_zone (Shared with ACV)

    | Value | Label |
    |-------|-------|
    | 0 | Unclassified |
    | 100000001 | Zone 1 |
    | 100000002 | Zone 2 |
    | 100000003 | Zone 3 |

    ### fsi_acv_severity (Shared with ACV)

    | Value | Label |
    |-------|-------|
    | 1 | Passed |
    | 2 | Warning |
    | 3 | GracePeriod |
    | 4 | Failed |
    | 5 | Error |

    ### fsi_ssc_validationtype (SSC-specific)

    | Value | Label |
    |-------|-------|
    | 100000001 | SessionControls |
    | 100000002 | AuthStrength |
    | 100000003 | PIMSettings |
    | 100000004 | BreakGlass |
    | 100000005 | ConflictAudit |
    | 100000006 | Orchestrator |

    ## Environment Variables

    | Variable | Type | Default | Purpose |
    |----------|------|---------|---------|
    | fsi_SSC_Zone1_SignInFrequencyMinutes | Decimal | 480 | Zone 1 session limit (8h) |
    | fsi_SSC_Zone2_SignInFrequencyMinutes | Decimal | 240 | Zone 2 session limit (4h) |
    | fsi_SSC_Zone3_SignInFrequencyMinutes | Decimal | 60 | Zone 3 session limit (1h) |
    | fsi_SSC_Zone1_AuthStrength | String | Standard MFA | Zone 1 auth strength |
    | fsi_SSC_Zone2_AuthStrength | String | Passwordless | Zone 2 auth strength |
    | fsi_SSC_Zone3_AuthStrength | String | Phishing-resistant | Zone 3 auth strength |

    ## Deployment

    Deploy schema using:

    ```bash
    cd scripts
    python deploy.py --dataverse-url https://org.crm.dynamics.com --tables-only
    python deploy.py --dataverse-url https://org.crm.dynamics.com --vars-only
    ```

    ## Security Notes

    After deployment, modify the Security Role for `fsi_ValidationHistory` to remove Write and Delete privileges for all roles except System Administrator. This ensures immutability for regulatory compliance.
    ```

    Target: ~200 lines
  </action>
  <verify>
    1. File exists at docs/DATAVERSE-SCHEMA.md
    2. Contains 3 table definitions with columns
    3. Contains option set definitions
    4. Contains environment variables table
  </verify>
  <done>
    DATAVERSE-SCHEMA.md created with complete schema documentation.
  </done>
</task>

<task type="auto">
  <name>Task 3: Create EVIDENCE-EXPORT-GUIDE.md</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/docs/EVIDENCE-EXPORT-GUIDE.md
  </files>
  <action>
    Create step-by-step evidence export guide for administrators.

    Structure:
    ```markdown
    # Evidence Export Guide

    ## Overview

    Export-SessionSecurityEvidence.ps1 produces JSON files containing session security validation history with SHA-256 integrity hashes for FINRA/SEC examination support.

    ## Prerequisites

    - PowerShell 7.0+
    - MSAL.PS module (for service principal authentication)
    - Dataverse deployed with validation history data
    - Read access to fsi_ValidationHistory table

    ## Interactive Mode

    For ad-hoc exports during audits:

    ```powershell
    # Export last 30 days for all zones
    .\scripts\Export-SessionSecurityEvidence.ps1 `
        -DataverseUrl https://org.crm.dynamics.com `
        -TenantId "your-tenant-id" `
        -OutputDirectory .\exports `
        -Interactive

    # Export specific zone
    .\scripts\Export-SessionSecurityEvidence.ps1 `
        -DataverseUrl https://org.crm.dynamics.com `
        -TenantId "your-tenant-id" `
        -Zone 3 `
        -OutputDirectory .\exports `
        -Interactive

    # Export specific date range
    .\scripts\Export-SessionSecurityEvidence.ps1 `
        -DataverseUrl https://org.crm.dynamics.com `
        -TenantId "your-tenant-id" `
        -FromDate "2026-01-01" `
        -ToDate "2026-01-31" `
        -OutputDirectory .\exports `
        -Interactive
    ```

    ## Service Principal Mode

    For scheduled/automated exports:

    ```powershell
    $clientSecret = ConvertTo-SecureString "your-secret" -AsPlainText -Force

    .\scripts\Export-SessionSecurityEvidence.ps1 `
        -DataverseUrl https://org.crm.dynamics.com `
        -TenantId "your-tenant-id" `
        -ClientId "app-registration-id" `
        -ClientSecret $clientSecret `
        -OutputDirectory .\exports
    ```

    ## Export Parameters

    | Parameter | Required | Default | Description |
    |-----------|----------|---------|-------------|
    | DataverseUrl | Yes | — | Dataverse organization URL |
    | TenantId | Yes | — | Azure AD tenant ID |
    | Zone | No | All | Filter by zone (1, 2, 3, or All) |
    | OutputDirectory | Yes | — | Export destination folder |
    | FromDate | No | 30 days ago | Date range start |
    | ToDate | No | Now | Date range end |
    | RunId | No | — | Specific validation run ID |
    | Interactive | No | False | Use interactive authentication |
    | ClientId | No | — | Service principal app ID |
    | ClientSecret | No | — | Service principal secret |

    ## Output Files

    Each export produces two files:

    ```
    session-security-evidence-Zone3-20260209-143022.json
    session-security-evidence-Zone3-20260209-143022.json.sha256
    ```

    ## Evidence JSON Schema

    ```json
    {
      "metadata": {
        "exportedAt": "2026-02-09T14:30:22Z",
        "scope": "SessionSecurity",
        "zone": "Zone 3",
        "fromDate": "2026-01-10T00:00:00Z",
        "toDate": "2026-02-09T23:59:59Z",
        "exportVersion": "1.0.0",
        "recordCount": 42,
        "organizationUrl": "https://org.crm.dynamics.com"
      },
      "summary": {
        "overallStatus": "Passed",
        "validationsRun": 42,
        "validationsPassed": 40,
        "validationsFailed": 2,
        "validationsWarning": 0
      },
      "validations": [
        {
          "name": "Zone 3 Session Controls",
          "runId": "abc123",
          "zone": "Zone 3",
          "severity": "Passed",
          "validationType": "SessionControls",
          "signInFrequencyMinutes": 60,
          "authStrength": "Phishing-resistant MFA",
          "reason": "Session controls match baseline",
          "timestamp": "2026-02-09T06:00:00Z"
        }
      ]
    }
    ```

    ## Verifying Evidence Integrity

    Use Test-EvidenceIntegrity.ps1 to verify SHA-256 hash:

    ```powershell
    # Verify single file
    .\scripts\Test-EvidenceIntegrity.ps1 -EvidenceFile .\exports\session-security-evidence-Zone3-20260209-143022.json

    # Batch verification
    Get-ChildItem .\exports\*.json | ForEach-Object {
        $result = .\scripts\Test-EvidenceIntegrity.ps1 -EvidenceFile $_.FullName -Quiet
        [PSCustomObject]@{ File = $_.Name; Valid = $result }
    }
    ```

    ## Recommended Export Schedule

    | Use Case | Schedule | Zone Filter | Retention |
    |----------|----------|-------------|-----------|
    | Weekly compliance check | Weekly (Sunday) | All | 90 days |
    | Monthly examination prep | Monthly (1st) | All | 2 years |
    | Zone 3 audit trail | Daily | Zone 3 only | 730 days |
    | On-demand examination | Ad-hoc | As requested | Permanent |

    ## Troubleshooting

    | Error | Cause | Resolution |
    |-------|-------|------------|
    | 401 Unauthorized | Token expired or invalid | Re-authenticate with -Interactive |
    | 404 Not Found | Table doesn't exist | Verify Dataverse deployment completed |
    | No records returned | Date range has no data | Expand date range or verify validation runs |
    | Hash mismatch | File modified after export | Re-export; do not modify evidence files |
    ```

    Target: ~180 lines
  </action>
  <verify>
    1. File exists at docs/EVIDENCE-EXPORT-GUIDE.md
    2. Contains interactive and service principal examples
    3. Contains parameter table
    4. Contains JSON schema example
    5. Contains verification instructions
  </verify>
  <done>
    EVIDENCE-EXPORT-GUIDE.md created with complete export instructions.
  </done>
</task>

<task type="auto">
  <name>Task 4: Create TROUBLESHOOTING.md</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/docs/TROUBLESHOOTING.md
  </files>
  <action>
    Create troubleshooting guide covering common deployment and operational issues.

    Structure:
    ```markdown
    # Session Security Configurator Troubleshooting

    ## Common Deployment Issues

    ### Authentication Context Deployment

    | Error | Cause | Resolution |
    |-------|-------|------------|
    | "Context already exists" | Authentication context c1-c5 already defined | Use -Force to overwrite, or manually update in Entra portal |
    | "Insufficient permissions" | Missing Security Administrator role | Assign Security Administrator or Global Administrator |
    | Graph API timeout | Large tenant with many CA policies | Retry with -Verbose; consider off-hours deployment |

    ### CA Policy Deployment

    | Error | Cause | Resolution |
    |-------|-------|------------|
    | "Bake period not met" | Policy created < 72 hours ago | Wait for report-only period to complete |
    | "Conflicting policy detected" | Overlapping CA policy targeting same users | Review conflict audit output; merge or disable conflicting policy |
    | "Authentication strength not found" | Named policy doesn't exist | Create auth strength policy before deploying CA policy |

    ### Dataverse Schema Deployment

    | Error | Cause | Resolution |
    |-------|-------|------------|
    | "Table already exists" | Schema previously deployed | Re-run with --force flag |
    | "Insufficient privileges" | Missing System Customizer role | Assign System Administrator or System Customizer |
    | Connection refused | Firewall blocking Dataverse API | Verify network access to *.crm.dynamics.com |

    ## Common Validation Issues

    ### Test-SessionCompliance Failures

    | Validation | Common Failure | Resolution |
    |------------|----------------|------------|
    | SessionControls | Sign-in frequency not enforced | Verify CA policy is in Enforce mode (not report-only) |
    | AuthStrength | Wrong strength applied | Check auth strength assignment in target CA policy |
    | PIMSettings | Activation window too long | Configure PIM role settings to match zone requirements |
    | BreakGlass | Account not excluded | Add break-glass accounts to exclusion group |
    | ConflictAudit | Multiple policies detected | Use pre-deployment conflict audit to identify overlaps |

    ### Break-Glass Validation Errors

    Break-glass failures are CRITICAL and force overall validation to Failed.

    | Scenario | Cause | Resolution |
    |----------|-------|------------|
    | "Break-glass not excluded" | Accounts not in exclusion group | Add to CA policy exclusion group |
    | "Group membership check failed" | Graph API error querying group | Verify group exists and accessible |
    | "Multiple break-glass accounts missing" | Partial exclusion | Add ALL break-glass accounts to exclusion |

    ## Common Flow Issues

    ### Daily Validation Flow

    | Issue | Cause | Resolution |
    |-------|-------|------------|
    | Flow not triggering | Recurrence misconfigured | Verify daily schedule in Power Automate |
    | Teams alert not sent | Connection reference not bound | Bind Teams connection reference |
    | Dataverse write fails | ValidationHistory security role issue | Check security role has Create privilege |
    | Timeout on validation | Large number of CA policies | Increase flow timeout; consider zone-by-zone execution |

    ## Evidence Export Issues

    | Issue | Cause | Resolution |
    |-------|-------|------------|
    | No records returned | No validations in date range | Expand date range; verify validation flow ran |
    | JSON truncated | Object too deep | Verify -Depth 10 in ConvertTo-Json |
    | Hash verification fails | File modified after export | Re-export evidence; never edit exported files |
    | Access token expired | Long-running export | Re-authenticate before export |

    ## Error Reference

    | Error Code | Message | Resolution |
    |------------|---------|------------|
    | SSC-001 | Authentication context conflict | Review context IDs; use -Force to overwrite |
    | SSC-002 | Policy bake period violation | Wait 72 hours before enabling enforcement |
    | SSC-003 | Break-glass exclusion missing | Add break-glass accounts to exclusion group |
    | SSC-004 | PIM configuration mismatch | Update PIM role settings to match zone |
    | SSC-005 | Conflict audit warning | Review overlapping CA policies |
    | SSC-006 | Dataverse connection failed | Verify URL and authentication |
    | SSC-007 | Evidence export failed | Check date range and table access |

    ## Getting Support

    1. **Check logs:** Review PowerShell output with -Verbose flag
    2. **Verify prerequisites:** Re-run prerequisite checks
    3. **Review documentation:** Check FLOW_SETUP.md for flow issues
    4. **Check FSI-AgentGov issues:** [GitHub Issues](https://github.com/judeper/FSI-AgentGov-Solutions/issues)
    ```

    Target: ~150 lines
  </action>
  <verify>
    1. File exists at docs/TROUBLESHOOTING.md
    2. Contains deployment, validation, and flow issue tables
    3. Contains error reference table
  </verify>
  <done>
    TROUBLESHOOTING.md created with comprehensive issue resolution guidance.
  </done>
</task>

<task type="auto">
  <name>Task 5: Update README.md with Phase 4 content and completed status</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/README.md
  </files>
  <action>
    Read current README.md and update with:

    1. **Status line**: Change to `v1.0.0 — Complete`

    2. **What This Solution Does section**: Add evidence export capability bullets:
       - **Exports** compliance evidence to JSON with SHA-256 integrity hashing
       - **Verifies** evidence file integrity for audit examination submissions

    3. **Quick Start section**: Add Step 5 for evidence export:
       ```markdown
       ### Step 5: Export Compliance Evidence

       ```powershell
       # Export session security validation evidence
       .\scripts\Export-SessionSecurityEvidence.ps1 `
           -DataverseUrl https://org.crm.dynamics.com `
           -TenantId <your-tenant-id> `
           -OutputDirectory .\exports `
           -Interactive

       # Verify evidence integrity
       .\scripts\Test-EvidenceIntegrity.ps1 `
           -EvidenceFile .\exports\session-security-evidence-All-20260209-143022.json
       ```
       ```

    4. **Documentation section**: Add link to new docs:
       - [Prerequisites](docs/PREREQUISITES.md)
       - [Dataverse Schema](docs/DATAVERSE-SCHEMA.md)
       - [Evidence Export Guide](docs/EVIDENCE-EXPORT-GUIDE.md)
       - [Troubleshooting](docs/TROUBLESHOOTING.md)

    5. **Architecture section**: Note evidence export layer

    Maintain existing content format and style.
  </action>
  <verify>
    1. README contains "v1.0.0 — Complete" status
    2. README contains Export-SessionSecurityEvidence in Quick Start
    3. README contains links to all 4 documentation files
  </verify>
  <done>
    README.md updated with Phase 4 content and completed status.
  </done>
</task>

<task type="auto">
  <name>Task 6: Update CHANGELOG.md with Phase 4 entries</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/CHANGELOG.md
  </files>
  <action>
    Add Phase 4 release entry to CHANGELOG.md:

    ```markdown
    ## [1.0.0] - 2026-02-09

    ### Added
    - Phase 4: Evidence Export and Framework Integration
      - Export-SessionSecurityEvidence.ps1 — compliance evidence export with SHA-256 integrity hashing
      - Get-SSCValidationResults.ps1 — Dataverse validation history query helper
      - Test-EvidenceIntegrity.ps1 — SHA-256 hash verification utility
      - PREREQUISITES.md — comprehensive prerequisites documentation
      - DATAVERSE-SCHEMA.md — Dataverse table and option set reference
      - EVIDENCE-EXPORT-GUIDE.md — step-by-step export instructions
      - TROUBLESHOOTING.md — common issues and resolutions
      - Control 1.23 framework integration (tip admonition)
      - solutions-index.md catalog entry

    ### Status
    - Solution complete with all 4 phases delivered
    - Validated against FSI-AgentGov governance framework
    ```

    Add after existing Phase 3 entries.
  </action>
  <verify>
    1. CHANGELOG contains "Evidence Export" section
    2. CHANGELOG lists all Phase 4 deliverables
  </verify>
  <done>
    CHANGELOG.md updated with Phase 4 release notes.
  </done>
</task>

</tasks>

<validation>
Run after all tasks complete:

```bash
# Verify documentation files exist
ls FSI-AgentGov-Solutions/session-security-configurator/docs/

# Verify README updates
grep "v1.0.0" FSI-AgentGov-Solutions/session-security-configurator/README.md
grep "Export-SessionSecurityEvidence" FSI-AgentGov-Solutions/session-security-configurator/README.md

# Verify CHANGELOG
grep "Evidence Export" FSI-AgentGov-Solutions/session-security-configurator/CHANGELOG.md
```
</validation>

<summary_template>
## Summary

- **Plan:** 04-SSC-03 Documentation Suite
- **Phase:** 04-evidence-export-framework-integration
- **Wave:** 2

### Deliverables

| Artifact | Lines | Status |
|----------|-------|--------|
| PREREQUISITES.md | ~100 | Created |
| DATAVERSE-SCHEMA.md | ~200 | Created |
| EVIDENCE-EXPORT-GUIDE.md | ~180 | Created |
| TROUBLESHOOTING.md | ~150 | Created |
| README.md | — | Updated with Phase 4 |
| CHANGELOG.md | — | Updated with Phase 4 |

### Must-Haves Covered

- [x] Documentation covers prerequisites, Dataverse schema, configuration
- [x] Documentation covers deployment and troubleshooting
</summary_template>
