# Verification & Testing — Control 3.9: Microsoft Sentinel Integration

> **Examiner-defensible evidence package** for Control 3.9. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, SEC, NYDFS, FFIEC, OCC, and internal audit that AI-agent telemetry is centrally ingested into Microsoft Sentinel, that AI-specific analytics rules detect prompt-injection / jailbreak / anomalous workload-identity behavior, that Logic Apps response playbooks fire end-to-end, that incidents cascade correctly into Controls 2.6, 2.12, 3.4, and 3.6, and that NYDFS 23 NYCRR 500.17 72-hour timers start, escalate, and produce a signed quarterly evidence bundle.
>
> **Scope:** Microsoft Sentinel workspaces operating in the Microsoft 365 commercial (Global) cloud.
>
> **Last UI verified:** April 2026 against the post-2026.04.x Defender / Microsoft Sentinel unified portal build, the Microsoft Entra portal build of the same wave, and the Logic Apps Standard runtime release of the same wave.
>
> **Companion controls:** [1.7 Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.8 Runtime Protection & External Threat Detection](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md), [1.9 Data Retention & Deletion](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), [1.11 Conditional Access & Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md), [1.24 Defender AI-SPM](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md), [2.6 Model Risk Management — OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.8 Access Control & Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md), [2.12 Supervision & Oversight — FINRA Rule 3110](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.25 Microsoft Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [3.4 Incident Reporting & Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [3.6 Orphaned Agent Detection & Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md), [3.14 Agent 365 Observability SDK](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md).

---

!!! warning "Scope Limit — operational monitoring evidence, not books-and-records"
    Microsoft Sentinel and the Log Analytics workspace backing it produce **operational monitoring evidence** — alert artifacts, KQL query results, incident records, automation-run logs, and workbook snapshots. They are **not** the system of record for **books-and-records retention** under **FINRA Rule 4511**, **SEC Rule 17a-3 / 17a-4**, or **NYDFS 23 NYCRR 500.06** content-level retention obligations. The firm's books-and-records evidence for Copilot prompts, agent transcripts, supervisory annotations, and recordkeeping content **must be retained through Microsoft Purview retention policies, eDiscovery exports, or an SEC 17a-4(f)-compliant archive** under [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). This playbook **supports compliance with** FINRA 3110 (Supervision), FINRA 4511 (Books and Records), FINRA RN 24-09 / Rule 3110, SEC 17a-3/17a-4, NYDFS 500.06/500.16/500.17, FFIEC IT Examination Handbook, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), and Federal Reserve SR 26-2 (formerly SR 11-7). It **does not guarantee** compliance and **does not replace** registered-principal supervisory review under FINRA Rule 3110 or written supervisory procedures.

!!! info "Entra schema gotcha — `AADServicePrincipalSignInLogs` is distinct from `SigninLogs`"
    Workload-identity (service principal, managed identity, agent identity) sign-ins are emitted to **`AADServicePrincipalSignInLogs`**, **not** to `SigninLogs`. `SigninLogs` covers human (member and guest) interactive and non-interactive sign-ins. Several TCs below explicitly cross-check both tables; an analytics rule that filters only `SigninLogs` will silently miss every agent sign-in event and produce a false-clean evidence record. Verify the `_BilledSize` and `Count()` of both tables in TC-1.

---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.4+ Core; `#Requires -Version 7.4` at the top of every executable script. See [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md). |
| Test framework | Pester 5.5+. All assertions use `Should` with `-Because` clauses for examiner traceability. |
| Output discipline | No `Write-Host` in evidence-emitting code paths. All evidence is structured `[pscustomobject]` via `Write-Output`, then serialized with `ConvertTo-Json -Depth 8`. |
| KQL discipline | Every KQL snippet in this playbook is labelled with a stable **query-hash** (SHA-256 of the canonical query text, lowercased, whitespace-normalised). The hash is embedded in every evidence record so any examiner can reproduce the query exactly as executed at run time. |
| Evidence retention | **Operational evidence:** 1 year hot in the Sentinel workspace, 7 years in Azure Storage archive tier (firm's choice up to 12 years for Fed-supervised entities). **Books-and-records evidence** is **not** stored in Sentinel; see [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). |
| Hashing | SHA-256 over canonical JSON; chained leaf hashes plus a Merkle root in `attestation.json` (TC-16). |
| Run identifier | Every test run is tagged `AGT39-yyyyMMdd-HHmmss-<8charGuid>` and embedded in every evidence record and artifact filename. |
| Canonical role names | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). No title substitution (e.g., "Global Administrator" is not a substitute for "Entra Global Admin"). |

> This playbook **helps meet** continuous-monitoring, audit-trail, incident-response, supervisory-cascade, and 72-hour-notification expectations under the regulations enumerated above. It is one component of a defensible AI-agent governance program; it does not replace the firm's written supervisory procedures, model risk management practices required by Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12), or legal review.

---

## §0 Pre-Test Prerequisites

### 0.1 Operator role prerequisites

The verification cycle is read-mostly: §1–§17 read connector state, KQL tables, analytics-rule definitions, automation rules, Logic Apps run histories, and incident records. Test fixtures (TC-3 prompt-injection sandbox prompt, TC-4 simulated MCP connector call, TC-6 non-prod DLP toggle, TC-9 mass-download fixture) execute under **dedicated sandbox identities** scoped to a non-production environment; they never touch production Zone 2 / Zone 3 data. Any remediation cited from a TC FAIL routes to the sister [PowerShell Setup](./powershell-setup.md), [Portal Walkthrough](./portal-walkthrough.md), or [Troubleshooting](./troubleshooting.md) playbook under its own change ticket and write scopes.

| Role (canonical) | Required for | PIM activation window |
|---|---|---|
| Sentinel Admin (Microsoft Sentinel Contributor on the workspace RG) | Reads workspace, data-connector state, analytics-rule definitions, automation rules, Logic Apps run histories, incident records; signs DETECT and AUTOMATE evidence | 4 hours, just-in-time |
| SOC Analyst (Microsoft Sentinel Responder) | Reads incidents and entities, runs hunting queries, witnesses the cascade-cross-reference assertions in TC-14 | 4 hours, just-in-time |
| Log Analytics Reader (subscription scope) | Read-only KQL execution against the Sentinel workspace; supports the dual-control witness pattern in TC-16 | 4 hours, standing permissible |
| Entra Global Reader | Reads `SigninLogs`, `AADServicePrincipalSignInLogs`, `AuditLogs`; verifies workload-identity coverage in TC-1 / TC-5 | 4 hours, standing permissible |
| Purview Compliance Admin | Reads Purview retention-label state to cross-check that books-and-records retention is **not** delegated to Sentinel (TC-12); reads UAL `OfficeActivity` ingestion path | 4 hours |
| Power Platform Admin | Reads `PowerPlatformAdminActivity` ingestion (DLP changes consumed in TC-6) and Power Platform DLP policy state for revert verification | 2 hours |
| AI Governance Lead | Counter-signs incident-cascade evidence (TC-14), quarterly evidence bundle (TC-16) | Standing with quarterly recertification per Control 2.8 |
| Compliance Officer | Counter-signs the NYDFS 500.17 72-hour-timer evidence (TC-11), Zone 3 supervisory-cascade evidence (TC-14), the quarterly bundle (TC-16) | Standing |
| Information Security Officer / CISO designee | Reviews Logic Apps runaway-suspension thresholds (TC-9, TC-10); counter-signs TC-16 quarterly bundle | Standing |
| Logic Apps Contributor (workflow RG) | Reads Logic Apps run history for TC-9, TC-10, TC-11; never holds standing write privilege on production playbooks | 2 hours, just-in-time |

> **Least privilege.** No operator should hold **Entra Global Admin** persistently for this playbook. Day-to-day verification work is performed under the read roles above with **Entra Global Reader** as the witness. If the tenant requires Global Admin to read a transient feature surface, activate via **Entra PIM** time-bound, never standing. Standing privileged-role overlap between Preparer / Validator / Compliance signatories is a cycle-stopping FAIL (see TC-16).

### 0.2 Module baseline

Pin to specific module versions so evidence packs are reproducible across machines and across time. Re-validate against newer module versions before promoting them to the standing schedule.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Az.Accounts';                                ModuleVersion='2.19.0' }
#Requires -Modules @{ ModuleName='Az.SecurityInsights';                        ModuleVersion='3.1.1'  }
#Requires -Modules @{ ModuleName='Az.OperationalInsights';                     ModuleVersion='3.2.0'  }
#Requires -Modules @{ ModuleName='Az.LogicApp';                                ModuleVersion='1.7.1'  }
#Requires -Modules @{ ModuleName='Az.Monitor';                                 ModuleVersion='5.2.1'  }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication';             ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.SignIns';           ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.DirectoryManagement'; ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.Reports';               ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion='2.0.200' }
#Requires -Modules @{ ModuleName='Pester';                                     ModuleVersion='5.5.0'  }

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
```

> **Note on Sentinel API surface.** `Az.SecurityInsights` 3.x covers analytics rules, automation rules, incidents, and data-connector state for the commercial cloud. Some preview features (Microsoft Copilot data connector, Sentinel MCP Server, certain UEBA models) surface only via the `2024-09-01-preview` REST API and the unified Defender portal at `security.microsoft.com`; this playbook abstracts those calls behind wrapper functions in [PowerShell Setup](./powershell-setup.md). Re-verify API versions and module noun availability after each Microsoft release wave.

### 0.3 PRE gates (must all pass before TC-1 through TC-16 execute)

`Invoke-Agt39PreFlight.ps1` runs nine pre-flight gates. Any `FAIL` halts the suite and emits a single `preflight-FAILED-<runId>.json`.

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | Confirms modules loaded at the pinned versions in §0.2 | HALT |
| Az context | PRE-02 | Confirms `Connect-AzAccount` against the correct subscription holding the Sentinel workspace | HALT |
| Graph context | PRE-03 | Confirms `Connect-MgGraph` with scopes `AuditLog.Read.All`, `Directory.Read.All`, `Reports.Read.All`, `SecurityEvents.Read.All`, `SecurityIncident.Read.All` | HALT |
| Tenant identification | PRE-04 | Captures `tenantId`, `displayName`, Sentinel `workspaceId`, `workspaceResourceId`, and `verifiedDomains[0].name` for every evidence record | HALT |
| Workspace reachability | PRE-05 | Probes `Invoke-AzOperationalInsightsQuery -Query 'print 1'` for HTTP 200 within 30s | HALT — without workspace reachability, no KQL evidence can be produced |
| Clock skew gate | PRE-06 | Compares local UTC to the workspace `TimeGenerated` of `print now()`; aborts on > 60s drift | HALT — skew invalidates timestamp evidence under FINRA 4511 / SEC 17a-4 |
| Microsoft Copilot connector reachability | PRE-07 | Probes the Microsoft Copilot data connector status via `Get-AzSentinelDataConnector`; `NotFound` halts the suite | HALT |
| Logic Apps runtime reachability | PRE-08 | Probes the Logic Apps Standard runtime hosting suspend-agent / notify / NYDFS-72h playbooks (`Get-AzLogicApp` enumeration and a `GET` against the Workflow Management API `/health` endpoint) | HALT |
| Evidence root writeable | PRE-09 | Confirms `$env:AGT39_EVIDENCE_ROOT` exists, is writeable, resolves to WORM-eligible storage (Azure Blob immutability policy in `Locked` state on the parent container) | HALT |

### 0.4 Run identifier and evidence root

```powershell
function New-Agt39RunId {
    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $guid = ([guid]::NewGuid().ToString('N')).Substring(0,8)
    "AGT39-$ts-$guid"
}

$script:RunId        = New-Agt39RunId
$script:RunTimestamp = (Get-Date).ToUniversalTime().ToString('o')
$script:EvidenceRoot = Join-Path $env:AGT39_EVIDENCE_ROOT $script:RunId
New-Item -Path $script:EvidenceRoot -ItemType Directory -Force | Out-Null
```

Every evidence record produced in TC-1 through TC-16 is written under `$script:EvidenceRoot`, and the `runId` is embedded in the filename of every artifact assembled into the TC-16 quarterly evidence bundle.

### 0.5 KQL query-hash convention

```powershell
function Get-Agt39QueryHash {
    [CmdletBinding()]
    [OutputType([string])]
    param([Parameter(Mandatory=$true)][string]$Query)

    # Canonicalise: trim, collapse internal whitespace, lowercase
    $canonical = ($Query -replace '\s+',' ').Trim().ToLowerInvariant()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($canonical)
    $sha   = [System.Security.Cryptography.SHA256]::Create()
    ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
}
```

Every KQL snippet in this playbook is presented with its canonical form and a `query_hash` field stamped into the corresponding evidence record. Examiners can recompute the hash from the snippet text in the playbook to confirm that the query executed at run time matches the published query. Drift in the hash without a corresponding change-ticket reference is itself a TC-16 FAIL.

### 0.7 Evidence record schema (canonical)

Every evidence record MUST conform to this schema. `Test-Agt39EvidenceSchema` (defined in [PowerShell Setup](./powershell-setup.md)) enforces it; the TC-16 bundle assembler refuses to publish a bundle containing any record that fails validation.

```json
{
  "control_id": "3.9",
  "tc_id": "TC-3",
  "run_id": "AGT39-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "sentinel_workspace_id": "/subscriptions/.../resourceGroups/rg-sec-prod/providers/Microsoft.OperationalInsights/workspaces/law-sec-prod",
  "cloud": "Commercial",
  "namespace": "DETECT",
  "criterion": "TC-3 prompt-injection / jailbreak detection",
  "subject_id": "incident-2026-04-15-7841",
  "subject_type": "sentinel_incident",
  "status": "PASS",
  "assertion": "Prompt-injection sandbox prompt produced a Sentinel incident within 5 minutes; incident is tagged 'ai-prompt-injection' and an automation rule cascaded a comment to the Control 2.12 supervisory queue.",
  "observed_value": {
    "incident_id": "7841",
    "incident_severity": "High",
    "alert_rule_id": "rule-ai-prompt-injection-v3",
    "time_to_alert_seconds": 187,
    "cascade_target_2_12_ticket": "SUP-2026-04-1129",
    "query_hash": "f3a1b9..."
  },
  "expected_value": {
    "time_to_alert_seconds_max": 600,
    "cascade_target_2_12_ticket": "<non-null>"
  },
  "evidence_artifacts": ["tc3-incident-7841.json","tc3-cascade-SUP-2026-04-1129.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-RN-24-09","NYDFS-500.06","NYDFS-500.16","FFIEC-IS"],
  "remediation_ref": null,
  "operator_upn": "soc.analyst@contoso.com",
  "witness_upn": "ai.governance.lead@contoso.com",
  "schema_version": "1.0"
}
```

---

## §1 Test Case Catalog

The 17 test cases below are grouped into six namespaces. Each namespace produces independent evidence records that combine into the single signed quarterly bundle in TC-16.

| Namespace | Test cases | Cadence | Owner |
|---|---|---|---|
| `INGEST`   | TC-1, TC-12, TC-13          | Daily (TC-1); Quarterly (TC-12, TC-13) | Sentinel Admin |
| `DETECT`   | TC-2, TC-3, TC-4, TC-5, TC-6, TC-7, TC-9, TC-15 | Weekly (most); Per-cycle (TC-3, TC-6) | SOC Analyst |
| `CASCADE`  | TC-8, TC-14                  | Per cycle | AI Governance Lead |
| `AUTOMATE` | TC-9, TC-10, TC-11           | Per cycle (TC-10); on-demand (TC-9); per-incident (TC-11) | Sentinel Admin + Compliance Officer |
| `WORKBOOK` | TC-13                        | Weekly | SOC Analyst |
| `ATTEST`   | TC-16                        | Quarterly | Compliance Officer |

---

## §2 TC-1 — Connector Health Matrix (24-Hour Ingestion Confirmation)

**Namespace:** `INGEST` | **Owner:** Sentinel Admin | **Cadence:** Daily

### Setup

- PRE-01 through PRE-10 have all returned `PASS` for the run.
- The firm's Sentinel architecture document (Control 3.9 §Key Configuration Points) lists the **required-tables matrix** the run will assert against. The reference matrix below is the framework default; the firm's deployment may extend it but must not contract it without an approved exception.
- Operator role: **Sentinel Admin** + **Log Analytics Reader**. Witness: **Entra Global Reader** for the workload-identity tables.

| Required table | Source connector | Why required |
|---|---|---|
| `SigninLogs` | Microsoft Entra ID | Human sign-ins relevant to agent orchestration / supervisory access |
| `AADServicePrincipalSignInLogs` | Microsoft Entra ID | **Workload-identity (agent / service principal / managed identity) sign-ins** — distinct from `SigninLogs` |
| `AADNonInteractiveUserSignInLogs` | Microsoft Entra ID | Refresh-token and silent reauth flows, including Copilot session refresh |
| `AuditLogs` | Microsoft Entra ID | Directory changes, consent grants, role assignments (consumed by TC-7) |
| `OfficeActivity` (CopilotInteraction) | Microsoft 365 / Purview UAL | Copilot prompt/response metadata, XPIA / jailbreak signals |
| `PowerPlatformAdminActivity` | Power Platform Admin Activity | DLP-policy events, environment changes, agent metadata changes (consumed by TC-6) |
| `CloudAppEvents` | Defender for Cloud Apps | Runtime threat detections, shadow-app, mass-download (consumed by TC-9) |
| `AlertInfo`, `AlertEvidence` | Microsoft 365 Defender | XDR alerts, including Defender AI-SPM (Control 1.24) |
| `DeviceEvents` | Microsoft 365 Defender | Endpoint behavior correlated to agent activity |
| `SecurityIncident` | Microsoft Sentinel | Native incident table — used by TC-14 cascade assertions |

### Steps

1. Resolve the workspace and the connector list:

    ```powershell
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $env:AGT39_WORKSPACE_RG -Name $env:AGT39_WORKSPACE_NAME
    $connectors = Get-AzSentinelDataConnector -ResourceGroupName $ws.ResourceGroupName -WorkspaceName $ws.Name
    ```

2. Execute the ingestion-matrix KQL probe. **Note both human and workload-identity tables are checked explicitly:**

    ```kql
    // query_hash anchor: tc1-ingest-matrix-v2
    let required = datatable(TableName:string, MaxLatencyMin:int)
    [
        "SigninLogs",                         60,
        "AADServicePrincipalSignInLogs",      60,
        "AADNonInteractiveUserSignInLogs",    60,
        "AuditLogs",                          60,
        "OfficeActivity",                     90,
        "PowerPlatformAdminActivity",         120,
        "CloudAppEvents",                     90,
        "AlertInfo",                          60,
        "AlertEvidence",                      60,
        "DeviceEvents",                       60,
        "SecurityIncident",                   60
    ];
    union withsource=TableName
        SigninLogs, AADServicePrincipalSignInLogs, AADNonInteractiveUserSignInLogs,
        AuditLogs, OfficeActivity, PowerPlatformAdminActivity, CloudAppEvents,
        AlertInfo, AlertEvidence, DeviceEvents, SecurityIncident
    | where TimeGenerated > ago(24h)
    | summarize
        RowCount      = count(),
        LastIngested  = max(TimeGenerated),
        FirstIngested = min(TimeGenerated)
        by TableName
    | join kind=rightouter required on TableName
    | extend
        LatencyMin = iif(isnull(LastIngested), real(99999),
                         datetime_diff('minute', now(), LastIngested)),
        Status     = case(
            isnull(RowCount),                                "FAIL-NoData",
            datetime_diff('minute', now(), LastIngested) > MaxLatencyMin,
                                                             "FAIL-Stale",
            "PASS")
    | project TableName, RowCount, LastIngested, LatencyMin, MaxLatencyMin, Status
    | order by Status asc, TableName asc
    ```

3. Emit the per-table evidence record and stamp the canonical `query_hash` produced by `Get-Agt39QueryHash`.

4. **Workload-identity cross-check.** Execute a second targeted query to confirm that `AADServicePrincipalSignInLogs` is not merely present but actually contains rows that look like agent sign-ins:

    ```kql
    // query_hash anchor: tc1-spnsi-agent-presence-v1
    AADServicePrincipalSignInLogs
    | where TimeGenerated > ago(24h)
    | extend appKind = case(
        ServicePrincipalName has_any ("copilot","agent","bot","powerapp","studio"), "agent_likely",
        AppDisplayName       has_any ("Copilot","Agent","Bot","Power Apps","Copilot Studio"), "agent_likely",
        "other")
    | summarize
        TotalSpSignIns = count(),
        AgentLikely    = countif(appKind == "agent_likely"),
        DistinctSpns   = dcount(ServicePrincipalId)
    ```

### Expected

- All 11 required tables show `Status == "PASS"`.
- `AADServicePrincipalSignInLogs` shows `AgentLikely > 0` for any tenant that has at least one provisioned agent or Copilot workload identity.
- Latency for security-critical tables (`SigninLogs`, `AADServicePrincipalSignInLogs`, `AlertInfo`) is < 60 minutes.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Per-table ingestion matrix JSON | `tc1-ingest-matrix-<runId>.json` | Operational — 1y hot, 7y archive |
| SPN sign-in agent-presence summary | `tc1-spnsi-presence-<runId>.json` | Operational — 1y hot, 7y archive |
| Connector status export | `tc1-connector-state-<runId>.json` | Operational — 1y hot, 7y archive |
| Signed run record | `tc1-attest-<runId>.json` (Sentinel Admin signature; Entra Global Reader witness) | Operational — 1y hot, 7y archive |

### Remediation

- **`FAIL-NoData` on `AADServicePrincipalSignInLogs`:** the workspace is missing the Entra ID diagnostic-setting category `ServicePrincipalSignInLogs`. Open a change ticket; remediate via [Portal Walkthrough §Step 2](./portal-walkthrough.md) and [Troubleshooting](./troubleshooting.md). **Do not** treat as a Sentinel rule problem — this is an Entra diagnostic-routing problem.
- **`FAIL-Stale` on `OfficeActivity`:** check Microsoft 365 connector ingestion delay; common causes are deferred backfill after a connector restart and tenant-level audit ingestion lag (cap typically ~30 min, occasional 60–90 min).
- **`FAIL-Stale` on `PowerPlatformAdminActivity`:** verify the Power Platform Admin Activity connector is still in `Connected` state and the diagnostic-setting on the Power Platform tenant points to this workspace; remediation in [PowerShell Setup](./powershell-setup.md).
- **`FAIL-NoData` on `AlertInfo` / `AlertEvidence`:** Defender XDR connector likely disconnected; cross-check Control 1.24 verification evidence for AI-SPM signal presence before concluding root cause.
- A FAIL on TC-1 is a **cycle-stopping** result for the daily run; downstream TC-2 through TC-15 emit `BLOCKED — TC-1 not green` until TC-1 returns to PASS.

---

## §3 TC-2 — Analytics Rule Coverage (7 AI-Specific Rules Enabled and Tagged)

**Namespace:** `DETECT` | **Owner:** SOC Analyst | **Cadence:** Weekly

### Setup

- TC-1 returned `PASS` within the last 24 hours.
- The firm's analytics-rule catalog enumerates the seven AI-specific rules below; the catalog is version-controlled in the same repository as this playbook and the rule template hashes are pinned in the firm's `analytics-rules-catalog.json`.

| Rule ID (firm naming) | Detects | Severity | Cascade target |
|---|---|---|---|
| `AI-RULE-01` | Prompt-injection / jailbreak signal in `OfficeActivity` (CopilotInteraction) and `CloudAppEvents` | High | Control 2.12 supervisory queue |
| `AI-RULE-02` | Anomalous connector / MCP server invocation by a workload identity | Medium | Control 2.25 governance console + Control 1.2 registry |
| `AI-RULE-03` | After-hours privileged-agent sign-in via `AADServicePrincipalSignInLogs` | Medium | SOC Tier-2 + Control 2.12 (if supervisory-relevant) |
| `AI-RULE-04` | Unexpected DLP policy state change in `PowerPlatformAdminActivity` | High | Power Platform Admin + revert automation (TC-6) |
| `AI-RULE-05` | Unusual app-role / consent grant in `AuditLogs` | High | Control 2.8 access-review queue |
| `AI-RULE-06` | Mass data download by an agent identity in `CloudAppEvents` / `OfficeActivity` | High | Suspend-agent Logic App (TC-9) |
| `AI-RULE-07` | Defender AI-SPM alert ingestion (`AlertInfo` `Category == "AI security"`) | High | Control 1.24 + Control 3.4 |

### Steps

1. Enumerate enabled analytics rules and reduce to AI-tagged rules:

    ```powershell
    $rules = Get-AzSentinelAlertRule -ResourceGroupName $ws.ResourceGroupName -WorkspaceName $ws.Name
    $aiRules = $rules | Where-Object {
        $_.Tag -contains 'ai-agent' -or $_.DisplayName -match '(?i)agent|copilot|prompt[- ]?injection|jailbreak|ai-spm|mcp'
    }
    ```

2. Reconcile against the firm catalog:

    ```powershell
    $expected = (Get-Content $env:AGT39_RULE_CATALOG_PATH -Raw | ConvertFrom-Json).rules
    $missing  = $expected | Where-Object { $_.id -notin $aiRules.Tag }
    $disabled = $aiRules | Where-Object { -not $_.Enabled }
    ```

3. For each present rule, emit the rule's `query` text, `query_hash`, `enabled` state, `severity`, `tactics`, `tag` set, `lastModifiedUtc`, and `lastTriggeredUtc`.

### Expected

- All 7 catalog rules are present, enabled, tagged `ai-agent`, and have a recorded `lastModifiedUtc` consistent with the firm's change-ticket log.
- No rule has been silently modified out-of-cycle (last-modified timestamp matches a change ticket in the firm's CMDB).
- `query_hash` of each deployed rule matches the `query_hash` recorded in the firm catalog.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Rule-presence reconciliation | `tc2-rule-presence-<runId>.json` | Operational — 1y hot, 7y archive |
| Per-rule definition export | `tc2-rule-<RULE-ID>-<runId>.json` | Operational — 1y hot, 7y archive |
| Drift-vs-catalog report | `tc2-drift-<runId>.json` (FAIL records only) | Operational — 1y hot, 7y archive |

### Remediation

- **Missing rule:** deploy from the firm's ARM/Bicep template under a change ticket; do not edit in-portal.
- **Disabled rule:** confirm whether the disable was authorised (change ticket required); if unauthorised, re-enable and open a security-event ticket against the operator who disabled it (Control 2.8 segregation-of-duties review).
- **Drifted rule (`query_hash` mismatch):** treat as a high-severity change-management incident under Control 3.4. The rule's `lastModifiedBy` UPN is captured in the evidence record for the access-review queue (Control 2.8).

---

## §4 TC-3 — Prompt Injection / Jailbreak Detection (Sandbox Red-Team Probe)

**Namespace:** `DETECT` | **Owner:** SOC Analyst (with AI Governance Lead witness) | **Cadence:** Per cycle

### Setup

- A **dedicated red-team sandbox tenant or sandbox environment** is used. **Never** execute this TC against a production user, agent, or environment.
- A **benign canary prompt-injection payload** is maintained in the firm's red-team library; the payload is constructed to trigger the firm's prompt-shield / Defender AI-SPM detector without exfiltrating any data and without referencing customer or NPI content.
- The sandbox agent identity is enrolled in the same analytics-rule scope as production (otherwise the test proves nothing about production rule coverage) and is tagged `purpose=red-team-canary` in the Agent Registry (Control 1.2 / 2.25).
- TC-2 has confirmed `AI-RULE-01` is present, enabled, and at the catalog `query_hash`.

### Steps

1. **Pre-record baseline.** Capture the `lastTriggeredUtc` for `AI-RULE-01` and the current `SecurityIncident` row count for the sandbox agent.

2. **Inject the canary.** From a sandboxed Microsoft Copilot Studio agent or an MCP test harness, submit the canary prompt-injection payload as a single user turn.

3. **Wait for the analytics-rule cycle** (rule frequency typically 5 min; tolerance 15 min for end-to-end).

4. **Confirm alert and incident creation.** Run:

    ```kql
    // query_hash anchor: tc3-prompt-injection-detection-v2
    let sandboxAgent = "<sandbox-agent-spn-id>";
    let windowStart  = ago(30m);
    SecurityAlert
    | where TimeGenerated > windowStart
    | where AlertName has_any ("Prompt injection","Jailbreak","XPIA","Prompt shield")
       or  ProductName == "Microsoft Defender for Cloud Apps"
       or  AlertName has "AI-RULE-01"
    | extend entities = parse_json(Entities)
    | mv-expand entities
    | where tostring(entities.AadUserId) == sandboxAgent
       or  tostring(entities.Name)      contains sandboxAgent
       or  tostring(entities.Aux)       contains sandboxAgent
    | project TimeGenerated, AlertName, AlertSeverity, SystemAlertId, ProductName, Entities
    ```

5. **Confirm cascade to Control 2.12 supervisory queue.** Verify that the automation rule attached to `AI-RULE-01` posted a comment / ticket reference into the supervisory queue identified by Control 2.12. The supervisory queue ticket ID is captured in the incident's `Comments` array:

    ```kql
    // query_hash anchor: tc3-cascade-2-12-v1
    SecurityIncident
    | where TimeGenerated > ago(30m)
    | where Title has "AI-RULE-01" or Labels has "ai-prompt-injection"
    | mv-expand Comments
    | extend commentText = tostring(Comments.Message)
    | where commentText has "SUP-"
    | project IncidentNumber, Severity, Status, Owner, Labels, commentText
    ```

### Expected

- A new `SecurityAlert` row appears for the sandbox agent within 15 minutes of injection, with `AlertSeverity == "High"`.
- A `SecurityIncident` row is created with `Labels` containing `ai-prompt-injection` and `purpose-red-team-canary`.
- The incident `Comments` include a reference to a Control 2.12 supervisory-queue ticket of the form `SUP-YYYY-MM-NNNN`.
- The Defender AI-SPM signal (Control 1.24) is present in `AlertEvidence` if the firm has AI-SPM enabled.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Canary injection request log (sanitised) | `tc3-canary-request-<runId>.json` | Operational — 1y hot, 7y archive |
| Alert export | `tc3-alert-<systemAlertId>.json` | Operational — 1y hot, 7y archive |
| Incident export | `tc3-incident-<incidentNumber>.json` | Operational — 1y hot, 7y archive |
| Cascade ticket reference | `tc3-cascade-SUP-<ticketId>.json` | Operational — 1y hot, 7y archive |
| Signed dual-control attestation (SOC + AI Governance Lead) | `tc3-attest-<runId>.json` | Operational — 1y hot, 7y archive |

### Remediation

- **No alert raised within 15 min:** verify (a) sandbox agent is in scope of `AI-RULE-01` (`extend agentInScope = ...` in the rule), (b) the canary payload still matches the rule heuristics (Microsoft signature updates may neutralise older canaries), (c) the Microsoft Copilot data connector is healthy in TC-1 — if the connector shows `NotFound`, remediate per the troubleshooting playbook.
- **Alert raised but no incident:** check Sentinel incident-creation setting on the rule (`createIncident: true`).
- **Incident created but no cascade comment:** the automation rule is broken or disabled; cross-reference TC-10 Logic Apps run history for the failure.
- **Cascade comment present but no Control 2.12 ticket exists:** Control 2.12 supervisory queue intake is broken; raise a Control 3.4 incident. **Do not close TC-3 with `PASS` if the downstream ticket cannot be retrieved.**

---

## §5 TC-4 — Anomalous Connector / MCP Server Use (Agent Registry Cross-Reference)

**Namespace:** `DETECT` | **Owner:** SOC Analyst | **Cadence:** Per cycle

### Setup

- The sandbox agent from TC-3 is also used here, with a separate canary action: invoking a connector / MCP server endpoint **not previously seen** for that agent identity.
- The Agent Registry (Control 1.2 / 2.25) baseline of seen-connectors per agent is exported into a watchlist `AgentConnectorBaseline` in Sentinel (refreshed by a daily Logic App).
- `AI-RULE-02` is present, enabled, and at the catalog `query_hash`.

### Steps

1. From the sandbox agent, invoke a benign MCP server / custom-connector endpoint that the registry does not list for that agent.

2. Run the detection query:

    ```kql
    // query_hash anchor: tc4-anomalous-connector-mcp-v2
    let baseline = _GetWatchlist('AgentConnectorBaseline')
        | project AgentSpnId, KnownConnector = ConnectorName;
    PowerPlatformAdminActivity
    | where TimeGenerated > ago(1h)
    | where OperationName has_any ("ConnectorInvoked","McpServerInvoked","CustomConnectorCall")
    | extend AgentSpnId = tostring(parse_json(AdditionalProperties).agentSpnId),
             ConnectorName = tostring(parse_json(AdditionalProperties).connectorName)
    | join kind=leftouter baseline on AgentSpnId, $left.ConnectorName == $right.KnownConnector
    | where isnull(KnownConnector)
    | project TimeGenerated, AgentSpnId, ConnectorName, OperationName, CallerIpAddress, CorrelationId
    ```

3. Confirm the alert raised by `AI-RULE-02` enriches the incident with the Agent Registry record (Control 1.2 / 2.25) by inspecting the incident `CustomDetails`:

    ```kql
    // query_hash anchor: tc4-registry-enrichment-v1
    SecurityIncident
    | where TimeGenerated > ago(1h)
    | where Title has "AI-RULE-02"
    | extend agentRegistryRef = tostring(parse_json(AdditionalData).agentRegistryRef),
             ownerUpn         = tostring(parse_json(AdditionalData).ownerUpn),
             zone             = tostring(parse_json(AdditionalData).zone)
    | project IncidentNumber, agentRegistryRef, ownerUpn, zone, Severity
    ```

### Expected

- `AI-RULE-02` raises an alert within one rule-cycle.
- The incident's `CustomDetails` contains `agentRegistryRef` pointing back to the agent's record in Control 2.25 / Control 1.2 and `ownerUpn` populated for non-orphan agents.
- For an **orphan / ownerless agent** detected by this path, the cascade flows to TC-8 (Control 3.6 remediation register) rather than to a named owner.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Anomalous-connector hit | `tc4-anomaly-<correlationId>.json` | Operational — 1y hot, 7y archive |
| Registry-enrichment incident export | `tc4-incident-<incidentNumber>.json` | Operational — 1y hot, 7y archive |

### Remediation

- **Detection misses the canary connector:** confirm the watchlist `AgentConnectorBaseline` refresh job ran (Logic App `wf-baseline-refresh`); a stale baseline causes false negatives.
- **Enrichment missing `agentRegistryRef`:** the Agent Registry sync into Sentinel watchlists is broken; cross-reference Control 2.25 verification evidence for the watchlist export job.


---

## §6 TC-5 — After-Hours Privileged Agent Sign-In (Workload-Identity Evidence)

**Namespace:** `DETECT` | **Owner:** SOC Analyst | **Cadence:** Per cycle (time-boxed)

### Setup

- A **time-boxed** privileged sandbox agent (held under an Entra PIM time-bound assignment) is used; the assignment window is opened deliberately outside the firm's documented business hours (per Control 2.12 supervisory schedule).
- `AI-RULE-03` is present, enabled, and at the catalog `query_hash`.
- The firm's business-hours definition is encoded in a Sentinel watchlist `BusinessHoursByLocale` (so detection logic does not hardcode 7-19 UTC).

### Steps

1. Open the PIM activation outside business hours; cause the sandbox agent to perform a single privileged operation (e.g., reading a Zone 3 SharePoint library catalogued in the test fixture).

2. Run the detection query against `AADServicePrincipalSignInLogs` (**not** `SigninLogs` — this is the workload-identity table):

    ```kql
    // query_hash anchor: tc5-after-hours-spnsi-v3
    let bh = _GetWatchlist('BusinessHoursByLocale')
        | project Locale, StartHour = toint(StartHour), EndHour = toint(EndHour);
    AADServicePrincipalSignInLogs
    | where TimeGenerated > ago(24h)
    | where ResultType == 0
    | extend ServicePrincipalKind = case(
        AppDisplayName has_any ("Copilot","Agent","Bot","Power Apps","Copilot Studio"), "agent",
        "other")
    | where ServicePrincipalKind == "agent"
    | extend HourUtc = datetime_part('hour', TimeGenerated),
             Locale  = tostring(parse_json(LocationDetails).countryOrRegion)
    | join kind=leftouter bh on Locale
    | where isnull(StartHour) or HourUtc < StartHour or HourUtc > EndHour
    | project TimeGenerated, ServicePrincipalName, ServicePrincipalId, AppDisplayName, IPAddress, Locale, HourUtc
    ```

3. Confirm the alert and capture the privileged-role context from the corresponding `AuditLogs` row (the PIM activation event).

### Expected

- A `SecurityAlert` from `AI-RULE-03` references the sandbox agent's `ServicePrincipalId`.
- The alert is correlated to the `AuditLogs` PIM-activation event by `correlationId`.
- The incident `CustomDetails` includes the activation justification and the activator's UPN, supporting Control 2.8 segregation-of-duties review.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| `AADServicePrincipalSignInLogs` excerpt for the sandbox agent | `tc5-spnsi-<runId>.json` | Operational — 1y hot, 7y archive |
| PIM activation audit row | `tc5-pim-<correlationId>.json` | Operational — 1y hot, 7y archive |
| Alert + incident export | `tc5-alert-<systemAlertId>.json`, `tc5-incident-<incidentNumber>.json` | Operational — 1y hot, 7y archive |

### Remediation

- **Detection silently empty:** the most common cause is filtering on `SigninLogs` instead of `AADServicePrincipalSignInLogs` (see the schema gotcha admonition). Re-verify the rule body.
- **Detection fires for production agents in normal operation:** the business-hours watchlist is wrong for the agent's locale; correct the watchlist row. **Do not** widen the rule's window without a TC-2 catalog change ticket.

---

## §7 TC-6 — DLP Policy Change Detection and Revert Automation

**Namespace:** `DETECT` | **Owner:** Power Platform Admin (witness: SOC Analyst) | **Cadence:** Per cycle

### Setup

- A **non-production Power Platform tenant or non-prod environment policy** is used. **Never** toggle a production DLP policy as part of this test.
- `AI-RULE-04` is present, enabled, at the catalog `query_hash`, and wired to the `wf-revert-dlp` Logic App (TC-10).
- The non-prod DLP policy is registered with the firm's CMDB as `NONPROD-DLP-CANARY-A` and the canary toggle is documented as a planned change.

### Steps

1. Toggle a single connector group on `NONPROD-DLP-CANARY-A` from Business to Non-business (or remove a connector classification).

2. Within 15 minutes, query:

    ```kql
    // query_hash anchor: tc6-dlp-policy-change-v2
    PowerPlatformAdminActivity
    | where TimeGenerated > ago(30m)
    | where OperationName in ("UpdateDlpPolicy","UpdatePolicyConnectorConfigurations","DeleteDlpPolicy")
    | extend policyName    = tostring(parse_json(AdditionalProperties).policyName),
             actorUpn      = tostring(parse_json(AdditionalProperties).actorUpn),
             connectorList = tostring(parse_json(AdditionalProperties).changedConnectors)
    | project TimeGenerated, OperationName, policyName, actorUpn, connectorList, CorrelationId
    ```

3. Confirm `wf-revert-dlp` Logic App execution by querying the Logic Apps run history (TC-10 reuses this evidence):

    ```powershell
    Get-AzLogicAppRunHistory -ResourceGroupName $env:AGT39_AUTOMATION_RG -Name 'wf-revert-dlp' `
      | Where-Object { $_.StartTime -gt (Get-Date).AddMinutes(-30) } `
      | Select-Object Name, Status, StartTime, EndTime, TriggerName
    ```

4. Verify the policy state is restored to its pre-test definition (compare the post-revert policy export against the firm's policy baseline JSON).

### Expected

- The `UpdateDlpPolicy` row appears in `PowerPlatformAdminActivity` within 5 minutes (allow up to 15 min for connector ingestion).
- `AI-RULE-04` raises a High-severity alert.
- `wf-revert-dlp` runs, status `Succeeded`, within 10 minutes of the alert.
- Post-revert policy diff against baseline is empty.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Pre-test policy baseline | `tc6-policy-baseline-<runId>.json` | Operational — 1y hot, 7y archive |
| Detection KQL excerpt | `tc6-detect-<correlationId>.json` | Operational — 1y hot, 7y archive |
| Logic App run record | `tc6-revert-run-<runName>.json` | Operational — 1y hot, 7y archive |
| Post-revert policy diff | `tc6-diff-<runId>.json` | Operational — 1y hot, 7y archive |
| Witness sign-off | `tc6-attest-<runId>.json` (Power Platform Admin signature; SOC Analyst witness) | Operational — 1y hot, 7y archive |

### Remediation

- **No `UpdateDlpPolicy` row:** Power Platform Admin Activity connector latency exceeds the rule window; verify TC-1 and increase rule lookback to 30 min if needed (under change ticket).
- **Revert Logic App did not fire:** automation rule trigger condition not matching; inspect rule's `triggers[0].condition` JSON.
- **Revert Logic App fired but policy still drifted:** the Logic App's managed identity lacks `Power Platform Administrator` rights; remediate per [Troubleshooting](./troubleshooting.md) and [PowerShell Setup](./powershell-setup.md) — **do not** add Entra Global Admin to the workflow identity; use scoped PIM-eligible assignment.

---



## §8 TC-7 — Unusual App-Role / Consent Grant Detection (AuditLogs Cascade to Access Reviews)

**Namespace:** `DETECT` | **Owner:** SOC Analyst (witness: Entra Global Reader) | **Cadence:** Per cycle

### Setup

- A **sandbox enterprise application** is registered in the test tenant or in a non-prod app-registration scoped to the canary OU. **Never** issue a real consent grant against a production application as part of this test.
- `AI-RULE-05` is present, enabled, at the catalog `query_hash`, and configured to enrich incidents with the consenting user's UPN, the resource app's display name, and the granted permission scopes.
- The cascade target is the Control 2.8 access-review queue identified by queue name `ARQ-AGENT-CONSENTS`.

### Steps

1. From the sandbox tenant, grant a benign delegated permission scope (e.g., `User.Read.All`) to a sandbox application via admin consent.

2. Within 15 minutes, query:

    ```kql
    // query_hash anchor: tc7-consent-grant-v2
    AuditLogs
    | where TimeGenerated > ago(30m)
    | where OperationName in ("Consent to application","Add app role assignment to service principal","Add delegated permission grant")
    | extend actorUpn      = tostring(InitiatedBy.user.userPrincipalName),
             resourceApp   = tostring(TargetResources[0].displayName),
             scopesGranted = tostring(parse_json(TargetResources[0].modifiedProperties)[0].newValue)
    | where resourceApp != "" and scopesGranted != ""
    | project TimeGenerated, actorUpn, resourceApp, scopesGranted, CorrelationId
    ```

3. Confirm the alert fires and the automation rule pushes the consent record into queue `ARQ-AGENT-CONSENTS` (Control 2.8). The queue ticket reference is captured in the incident's `Comments` array as `ARQ-YYYY-MM-NNNN`.

### Expected

- The consent event is captured in `AuditLogs` within 5 min.
- `AI-RULE-05` raises a High-severity alert; incident is created.
- The Control 2.8 access-review queue contains a new pending review item with the actor UPN, resource app, and scope list.
- The reviewer assignment is **not** the consenter (segregation-of-duties).

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| `AuditLogs` consent excerpt | `tc7-consent-<correlationId>.json` | Operational — 1y hot, 7y archive |
| Alert + incident export | `tc7-alert-<systemAlertId>.json`, `tc7-incident-<incidentNumber>.json` | Operational — 1y hot, 7y archive |
| Cascade reference | `tc7-cascade-ARQ-<ticketId>.json` | Operational — 1y hot, 7y archive |

### Remediation

- **No alert raised:** confirm the consent operation generated an `AuditLogs` row (some legacy admin-consent paths emit only application-level audit, not directory-level audit); verify the Entra ID diagnostic-setting category `AuditLogs` is enabled.
- **Cascade did not create an access-review item:** Logic App `wf-create-access-review` failed; cross-reference TC-10 run history.
- **Reviewer is the consenter:** segregation-of-duties violation in the Logic App's reviewer-resolution logic; this is itself a Control 2.8 finding and must be opened as a Control 3.4 incident.

---

## §9 TC-8 — Orphan / Shadow Agent Cascade to Remediation Register

**Namespace:** `CASCADE` | **Owner:** AI Governance Lead (witness: SOC Analyst) | **Cadence:** Per cycle

### Setup

- A **test orphan** is provisioned in the sandbox by creating an agent identity, then deleting its registry record (Control 1.2 / 2.25) so that subsequent activity by that identity registers as ownerless. The test orphan is tagged `purpose=orphan-canary`.
- The cascade target is the Control 3.6 remediation register, queue name `RR-ORPHAN-AGENTS`.
- Sentinel watchlist `AgentRegistryActiveOwners` contains the tenant's agent → owner mapping refreshed daily.

### Steps

1. Cause the test orphan to perform a benign operation (e.g., a single Copilot query or an MCP server call).

2. Run the orphan-detection query:

    ```kql
    // query_hash anchor: tc8-orphan-detect-v2
    let owners = _GetWatchlist('AgentRegistryActiveOwners')
        | project AgentSpnId, OwnerUpn;
    AADServicePrincipalSignInLogs
    | where TimeGenerated > ago(1h)
    | summarize lastSeen = max(TimeGenerated), signIns = count() by ServicePrincipalId, ServicePrincipalName, AppDisplayName
    | join kind=leftouter owners on $left.ServicePrincipalId == $right.AgentSpnId
    | where isnull(OwnerUpn) or OwnerUpn == ""
    | project lastSeen, ServicePrincipalId, ServicePrincipalName, AppDisplayName, signIns
    ```

3. Confirm the cascade Logic App `wf-orphan-to-remediation` posted a row to the remediation register with the orphan's SPN ID, last-seen timestamp, sign-in count, and a tag of `cascade-source=tc8`.

### Expected

- The test orphan appears in the detection result with `OwnerUpn` null.
- A row exists in `RR-ORPHAN-AGENTS` referencing the orphan's SPN ID and tagged `cascade-source=tc8`.
- The remediation register's SLA clock starts (Control 3.6 register convention).

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Orphan detection result | `tc8-orphan-<runId>.json` | Operational — 1y hot, 7y archive |
| Remediation register row | `tc8-rr-<rrId>.json` | Operational — 1y hot, 7y archive |
| Logic App run record | `tc8-logicapp-<runName>.json` | Operational — 1y hot, 7y archive |

### Remediation

- **Detection misses the test orphan:** watchlist `AgentRegistryActiveOwners` may include the test SPN incorrectly; verify the registry-export job filtered out tagged canaries.
- **Cascade did not write to register:** Logic App permissions on the register backend (Dataverse / SharePoint list / Cosmos DB) are missing; remediate per [Troubleshooting](./troubleshooting.md).

---

## §10 TC-9 — Mass Data Download by Agent Identity (Suspend-Agent Playbook Trigger)

**Namespace:** `AUTOMATE` | **Owner:** SOC Analyst (witness: AI Governance Lead) | **Cadence:** Per cycle (red-team window)

### Setup

- The sandbox agent from TC-3 is granted temporary read access to a **synthetic dataset** of dummy records (no NPI, no customer data, no PII). The dataset is sized so that the test can exceed the firm's mass-download threshold (default 5,000 records / 100 MB in 5 min).
- `AI-RULE-06` is present, enabled, at the catalog `query_hash`, and wired to the `wf-suspend-agent` Logic App.
- The suspend-agent Logic App's managed identity has the **scoped** permission to disable the sandbox SPN only; it is **not** Entra Global Admin.

### Steps

1. From the sandbox agent, perform a controlled bulk read of the synthetic dataset that exceeds the threshold within a single 5-min window.

2. Within 15 minutes, query:

    ```kql
    // query_hash anchor: tc9-mass-download-v2
    union
        (CloudAppEvents
            | where TimeGenerated > ago(30m)
            | where ActionType in ("FileDownloaded","FilePreviewed","FileSyncDownloadedFull")
            | extend agentId = tostring(parse_json(RawEventData).ApplicationId),
                     bytes   = tolong(parse_json(RawEventData).ObjectSize)),
        (OfficeActivity
            | where TimeGenerated > ago(30m)
            | where Operation in ("FileDownloaded","FileSyncDownloadedFull")
            | extend agentId = tostring(parse_json(ExtendedProperties).ApplicationId),
                     bytes   = tolong(SourceFileExtension))
    | where agentId != ""
    | summarize fileCount = count(), totalBytes = sum(bytes), windowStart = min(TimeGenerated), windowEnd = max(TimeGenerated) by agentId
    | where fileCount > 5000 or totalBytes > 100*1024*1024
    ```

3. Confirm the suspend-agent Logic App fired and disabled the sandbox SPN:

    ```powershell
    Get-AzADServicePrincipal -ObjectId $env:AGT39_SANDBOX_SPN_ID `
      | Select-Object DisplayName, AccountEnabled
    ```

4. Confirm the SOC Analyst received the Teams adaptive-card notification (out-of-band evidence: screenshot or Graph API audit).

### Expected

- Detection returns a row for the sandbox agent.
- `AI-RULE-06` raises a High-severity alert; incident is created.
- Sandbox SPN `AccountEnabled == False` within 5 minutes of the alert.
- SOC Analyst notification posted to the configured Teams channel.
- A revert work item is automatically opened against the AI Governance Lead to re-enable the sandbox SPN at end-of-test (Control 3.6 remediation register).

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Mass-download detection result | `tc9-detect-<runId>.json` | Operational — 1y hot, 7y archive |
| Pre-suspend SPN state | `tc9-spn-pre-<runId>.json` | Operational — 1y hot, 7y archive |
| Post-suspend SPN state | `tc9-spn-post-<runId>.json` | Operational — 1y hot, 7y archive |
| Logic App run record | `tc9-suspend-run-<runName>.json` | Operational — 1y hot, 7y archive |
| Teams notification audit | `tc9-teams-<messageId>.json` | Operational — 1y hot, 7y archive |
| Re-enable work-item record | `tc9-rr-<rrId>.json` | Operational — 1y hot, 7y archive |

### Remediation

- **Threshold not crossed:** the synthetic dataset was too small or the time window too narrow; re-run with a larger fixture.
- **Logic App fails to disable SPN:** managed identity scope insufficient; remediate per [PowerShell Setup](./powershell-setup.md) **without** elevating to Global Admin.
- **SPN remains disabled past test window:** the re-enable work-item is the formal closure path; **do not** bypass it manually.

---

## §11 TC-10 — Logic Apps Playbook Execution (End-to-End Run-History Audit)

**Namespace:** `AUTOMATE` | **Owner:** Logic Apps Contributor (witness: SOC Analyst + Compliance Officer) | **Cadence:** Per cycle

### Setup

- The four canonical Sentinel-attached Logic Apps under audit:
    - `wf-suspend-agent` (TC-9 trigger)
    - `wf-notify-owner-soc` (general notification)
    - `wf-revert-dlp` (TC-6 trigger)
    - `wf-nydfs-72h-timer` (TC-11 trigger)
- Each Logic App's managed identity, role assignments, and `actions` block JSON has been exported into the firm's CMDB at the change-ticket associated with the deployed version. The exported JSON `query_hash` (SHA-256 of canonicalised content) is pinned in the firm's `automation-catalog.json`.

### Steps

1. Enumerate run history for the past 30 days for each of the four Logic Apps:

    ```powershell
    foreach ($la in @('wf-suspend-agent','wf-notify-owner-soc','wf-revert-dlp','wf-nydfs-72h-timer')) {
        Get-AzLogicAppRunHistory -ResourceGroupName $env:AGT39_AUTOMATION_RG -Name $la `
            | Where-Object { $_.StartTime -gt (Get-Date).AddDays(-30) } `
            | Select-Object @{n='LogicApp';e={$la}}, Name, Status, StartTime, EndTime, TriggerName, Error
    }
    ```

2. For each run, capture: run ID, trigger source (incident ID for Sentinel-triggered runs), start/end timestamps, status, action-level success counts, and any error payloads.

3. Confirm the deployed `actions` block JSON `query_hash` matches the catalog pin (no out-of-band edits):

    ```powershell
    foreach ($la in @('wf-suspend-agent','wf-notify-owner-soc','wf-revert-dlp','wf-nydfs-72h-timer')) {
        $def = (Get-AzLogicApp -ResourceGroupName $env:AGT39_AUTOMATION_RG -Name $la).Definition
        $hash = Get-Agt39QueryHash -Text ($def | ConvertTo-Json -Depth 50 -Compress)
        [pscustomobject]@{ LogicApp = $la; DefinitionHash = $hash }
    }
    ```

4. Sample one run per Logic App for **deep evidence** (full action-by-action input/output trace), redacting secrets per the firm's evidence-redaction policy.

### Expected

- All four Logic Apps have at least one `Succeeded` run in the cycle (TC-6, TC-9, TC-11 produce a run; TC-14 produces a notification run).
- No `Failed` runs without a corresponding Control 3.4 incident.
- Definition hashes match the catalog (no drift).
- Sampled deep-evidence run shows expected action sequence end-to-end.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| 30-day run-history summary | `tc10-runs-summary-<runId>.json` | Operational — 1y hot, 7y archive |
| Per-Logic-App definition hash | `tc10-defhash-<la>-<runId>.json` | **Books-and-records scope where Logic App enforces a regulatory control** — 6y/7y per FINRA 4511 / SEC 17a-4 |
| Deep-evidence sampled run | `tc10-deep-<la>-<runName>.json` | Operational — 1y hot, 7y archive |
| Tri-signature attestation | `tc10-attest-<runId>.json` (Logic Apps Contributor + SOC Analyst + Compliance Officer) | **Books-and-records scope** — 6y/7y per FINRA 4511 / SEC 17a-4 |

### Remediation

- **Definition hash drift:** treat as a high-severity change-management incident under Control 3.4; the Logic App must be redeployed from the pinned template, not patched in-portal.
- **Repeated `Failed` runs without an open incident:** the failure-handling automation is broken; remediate per [Troubleshooting](./troubleshooting.md).


---

## §12 TC-11 — NYDFS 500.17(a) 72-Hour Notification Timer (Escalation and Drafting Kit)

**Namespace:** `AUTOMATE` | **Owner:** Compliance Officer (witness: CISO + AI Governance Lead) | **Cadence:** Per cycle (table-top + at least one live trigger per quarter)

!!! warning "Regulatory framing"
    This TC verifies the **technical timer mechanism** that supports the firm's NYDFS 23 NYCRR 500.17(a) 72-hour cybersecurity-event notification obligation. It does **not** itself satisfy the obligation. The decision to notify, the notification content, and the determination of whether the event meets the §500.17(a) threshold remain with the Compliance Officer and CISO under the firm's incident-response plan. Implementation requires that the firm's incident-response plan documents this timer as one input, not as the legal trigger.

### Setup

- The `wf-nydfs-72h-timer` Logic App is wired to fire on incidents tagged `regulatory-relevance=NYDFS-500.17` (the tag is applied by automation rules attached to high-severity AI-incidents and by manual SOC Analyst tag).
- The drafting kit content (templates, contact list, attestation form) lives in the documents identified by Control 3.4. The Logic App attaches the latest version of the kit to the escalation ticket.
- The escalation chain is: SOC Analyst → SOC Lead (T+0) → Compliance Officer (T+1h) → CISO (T+24h) → Board notification preparation (T+48h) → 72h decision point.

### Steps

1. **Live trigger leg.** Tag a sandbox incident (created via TC-3) with `regulatory-relevance=NYDFS-500.17`. Confirm the timer Logic App fires and creates an escalation ticket with:
    - T+0 timestamp recorded
    - 72-hour decision deadline computed in firm's home timezone (America/New_York for NYDFS)
    - Compliance Officer added as ticket assignee
    - Drafting kit version attached (kit `query_hash` pinned)
    - Initial Teams adaptive-card posted to the Compliance Officer's incident channel

2. **Escalation step verification.** Allow the timer Logic App to advance through its first escalation step (T+1h notification to Compliance Officer). Capture the notification record.

3. **Table-top decision point.** With the Compliance Officer, perform a **table-top** dry-run of the 72-hour decision (no real notification is filed). Capture the decision rationale (notify / not notify / threshold not met) into the ticket.

4. **Close-out.** Mark the sandbox incident as test-closed; the timer Logic App must record a `closed-test` outcome and write a closure record.

### Expected

- Escalation ticket exists with all metadata fields populated.
- Compliance Officer received notification within 5 min of the T+1h escalation step.
- Drafting kit version attached and `query_hash` matches the catalog.
- Table-top decision recorded with Compliance Officer signature and CISO co-signature.
- Closure record written; the timer is not left running past test close-out.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Timer-fire record | `tc11-timer-fire-<incidentNumber>.json` | **Books-and-records scope** — 6y/7y per NYDFS 500.06/500.16/500.17 |
| Escalation-step notification record | `tc11-escalation-<step>-<runId>.json` | **Books-and-records scope** — 6y/7y |
| Drafting kit attachment manifest (with `query_hash`) | `tc11-kit-manifest-<runId>.json` | **Books-and-records scope** — 6y/7y |
| Table-top decision record | `tc11-decision-<runId>.json` (Compliance Officer + CISO signatures) | **Books-and-records scope** — 6y/7y |
| Closure record | `tc11-closure-<runId>.json` | **Books-and-records scope** — 6y/7y |

### Remediation

- **Timer did not fire on tag:** automation rule trigger condition mis-scoped (e.g., filtering on `Labels` instead of `Tag`); remediate under change ticket.
- **Drafting kit version drift:** the kit attached is older than the catalog pin; re-run the kit-publication pipeline (Control 3.4).
- **Compliance Officer not notified:** distribution group membership stale; the firm's joiner-mover-leaver process for the Compliance Officer role is the upstream root cause and must be raised as a Control 2.8 finding.
- **Timer left running after test:** manual closure required; record a Control 3.4 finding on the operator who failed to close the test cleanly.

---

## §13 TC-12 — Sentinel Retention vs Purview Books-and-Records Boundary

**Namespace:** `ATTEST` | **Owner:** Sentinel Admin (witness: Compliance Officer + Information Security Officer / CISO) | **Cadence:** Quarterly

!!! warning "Boundary clarification"
    Sentinel retention is operational telemetry retention. It is **not** the firm's books-and-records system for FINRA 4511 / SEC 17a-4 / NYDFS 500.06 evidence. Books-and-records artifacts are retained in Microsoft Purview under the retention labels and policies verified by Controls 1.7 and 1.9. This TC verifies the **boundary** between the two: that Sentinel's retention is configured for operational sufficiency and that books-and-records artifacts produced by this playbook are written to Purview-controlled stores at capture time, not relied on Sentinel for legal retention.

### Setup

- Firm's Sentinel retention configuration: default ~180 days hot in Log Analytics, archive tier extended to firm-elected duration up to 12 years (Microsoft maximum). The firm's elected archive duration is recorded in the firm's `sentinel-retention-config.json` and signed off by the CISO.
- Firm's Purview retention policies for AI-related books-and-records (Control 1.7 / 1.9) are verified independently in those controls' verification-testing playbooks; this TC consumes those verification artifacts as inputs.

### Steps

1. Capture Sentinel workspace and per-table retention:

    ```powershell
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $env:AGT39_WORKSPACE_RG -Name $env:AGT39_WORKSPACE_NAME
    Get-AzOperationalInsightsTable -ResourceGroupName $ws.ResourceGroupName -WorkspaceName $ws.Name `
        | Select-Object Name, RetentionInDays, TotalRetentionInDays, ArchiveRetentionInDays
    ```

2. Reconcile against the firm's elected configuration. Any drift is a **change-control** finding.

3. Inventory books-and-records artifacts produced by THIS playbook (the `tc10-defhash-*`, `tc11-*`, `tc15-*`, `tc17-*` artifacts marked **Books-and-records scope** in their evidence-capture tables) and confirm each was written to a Purview-labelled location at capture time. Capture the Purview label name and the policy ID applied.

4. Confirm that **no** evidence record relies on Sentinel as its sole retention store for a books-and-records artifact.

### Expected

- Per-table retention matches the firm's elected configuration (no drift).
- Every books-and-records artifact has a Purview retention label applied at capture time.
- The Purview label's locked retention period meets or exceeds the artifact's regulatory retention floor (6y for FINRA 4511 / NYDFS / SEC 17a-4 with 2y immediately accessible; 7y for SOX 404).

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Sentinel retention configuration export | `tc12-retention-<runId>.json` | Operational — 1y hot, 7y archive |
| Books-and-records artifact-to-Purview-label map | `tc12-bnr-map-<runId>.json` | **Books-and-records scope** — 6y/7y |
| CISO sign-off | `tc12-attest-<runId>.json` | **Books-and-records scope** — 6y/7y |

### Remediation

- **Sentinel retention drifted from elected configuration:** open a Control 3.4 change-control incident; remediate via [PowerShell Setup](./powershell-setup.md). **Do not** silently re-align — the prior period must be explained.
- **Books-and-records artifact missing Purview label:** the capture pipeline is broken for that TC; remediate the Logic App or Pester evidence-writer to apply the label at capture time. The unlabelled artifact must be re-labelled retroactively and the gap window logged as a Control 1.7 / 1.9 finding.

---

## §14 TC-13 — Workbook Health (AI Agent Security Posture + Conditional Access Insights)

**Namespace:** `WORKBOOK` | **Owner:** Sentinel Admin (witness: AI Governance Lead) | **Cadence:** Per cycle

### Setup

- Two workbooks in scope:
    - **`AI Agent Security Posture`** — owned by Sentinel Admin, content authored against AI-specific KQL.
    - **`Conditional Access Insights`** — Microsoft-published workbook; Control 1.11 verifies the underlying Conditional Access policies and this TC verifies the workbook surfaces those policies' health.
- Each workbook's JSON template is pinned in the firm's CMDB by `query_hash`.

### Steps

1. Enumerate workbook templates and confirm presence:

    ```powershell
    Get-AzApplicationInsightsWorkbook -ResourceGroupName $env:AGT39_WORKSPACE_RG `
        | Where-Object { $_.DisplayName -in @('AI Agent Security Posture','Conditional Access Insights') } `
        | Select-Object DisplayName, Name, Category, ResourceId
    ```

2. For each workbook, export the serialised JSON, compute `query_hash`, and reconcile to the catalog pin.

3. Render each workbook's signature panels (programmatically via Azure portal API or manual screenshot per the firm's evidence policy) for the cycle window:
    - `AI Agent Security Posture`: incident counts, top alerting rules, top alerting agents, mass-download trend, prompt-injection trend.
    - `Conditional Access Insights`: policy-coverage gaps, sign-ins blocked vs allowed, MFA challenge counts, policy-change recency.

4. Confirm each panel returns data (no empty widgets) and that the time-window is the documented cycle window.

### Expected

- Both workbooks exist; no drift in `query_hash`.
- All signature panels return data for the cycle window.
- Cross-reference: the Conditional Access Insights policy-coverage panel reflects the policies enumerated in the latest Control 1.11 verification evidence.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Workbook JSON exports | `tc14-workbook-<DisplayName>-<runId>.json` | Operational — 1y hot, 7y archive |
| Panel screenshots / API renders | `tc14-panel-<DisplayName>-<panel>-<runId>.png` | Operational — 1y hot, 7y archive |
| Catalog reconciliation | `tc14-recon-<runId>.json` | Operational — 1y hot, 7y archive |

### Remediation

- **Workbook missing:** redeploy from the pinned template (do not author in-portal).
- **Panel empty:** underlying KQL query returns no rows — most often a TC-1 ingestion failure or a watchlist refresh failure; cross-reference TC-1 evidence first.
- **Drift in `query_hash`:** treat as Control 3.4 change-management incident.

---

## §15 TC-14 — Cross-Control Cascade Evidence (Tagging into 3.4, 2.12, 2.6, 3.6)

**Namespace:** `CASCADE` | **Owner:** AI Governance Lead (witness: SOC Analyst + Compliance Officer) | **Cadence:** Per cycle

### Setup

- All cascades emitted by automation rules in this control set carry a structured `cascade-source` tag of the form `cascade-source=<targetControlId>:<eventId>`. The ingest of these tags into downstream registers/queues is what TC-14 audits.
- Downstream targets:
    - Control 3.4 incident management
    - Control 2.12 supervisory queue
    - Control 2.6 model risk management register (where the incident has model-risk relevance)
    - Control 3.6 remediation register

### Steps

1. Reconcile cascade-out events from Sentinel against cascade-in receipts in each downstream register for the cycle window:

    ```kql
    // query_hash anchor: tc15-cascade-out-v2
    SecurityIncident
    | where TimeGenerated > ago(7d)
    | mv-expand Labels
    | extend tag = tostring(Labels)
    | where tag startswith "cascade-source="
    | extend targetControl = extract(@"cascade-source=([0-9.]+):", 1, tag),
             eventId       = extract(@"cascade-source=[0-9.]+:(.+)", 1, tag)
    | project IncidentNumber, targetControl, eventId, Severity, Status
    ```

2. For each `(targetControl, eventId)` pair, query the downstream register's API (Dataverse, SharePoint list, ServiceNow, or the firm's chosen system) to confirm the receipt row exists and matches the source incident.

3. Compute the **cascade-loss rate** = (cascade-out count − cascade-in count) / cascade-out count. Target: 0%.

4. Sample three cascades per downstream control for **deep evidence** (full request/response payloads from the cascade Logic App, redacted per the firm's evidence-redaction policy).

### Expected

- Cascade-loss rate == 0% for the cycle.
- All sampled deep-evidence runs show successful end-to-end propagation.
- Tri-signature attestation captured (AI Governance Lead + SOC Analyst + Compliance Officer).

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Cascade-out enumeration | `tc15-out-<runId>.json` | Operational — 1y hot, 7y archive |
| Per-target cascade-in reconciliation | `tc15-in-<targetControl>-<runId>.json` | Operational — 1y hot, 7y archive |
| Cascade-loss-rate report | `tc15-loss-<runId>.json` | **Books-and-records scope** — 6y/7y per FINRA 4511 |
| Deep-evidence sampled cascades | `tc15-deep-<targetControl>-<eventId>.json` | Operational — 1y hot, 7y archive |
| Tri-signature attestation | `tc15-attest-<runId>.json` | **Books-and-records scope** — 6y/7y |

### Remediation

- **Cascade-loss rate > 0%:** open a Control 3.4 incident per missing cascade; the upstream Logic App is the most likely root cause but the downstream register's intake API may also be at fault.
- **Deep-evidence sample shows malformed payload:** the cascade Logic App's payload schema has drifted from the receiver's contract; the firm's contract-test pipeline (if present) should have caught this earlier — raise a finding against that pipeline.

---

## §16 TC-15 — Break-Glass Account Sign-In Alert Wiring (Control 1.11 Cross-Reference)

**Namespace:** `DETECT` | **Owner:** SOC Analyst (witness: CISO) | **Cadence:** Per cycle (live trigger annually with CISO authorisation)

!!! warning "Break-glass discipline"
    Live break-glass account sign-in tests are performed under **explicit CISO authorisation**, with the test event recorded in the firm's break-glass log (Control 1.11). Implementation requires that the firm's break-glass procedure documents the test cadence and the witness requirements. **Never** sign in to a break-glass account outside the documented test or the documented break-glass scenario.

### Setup

- The firm maintains exactly two break-glass accounts per Control 1.11 verification evidence.
- A dedicated Sentinel analytics rule `BG-RULE-01` (P1 severity) is wired to fire on **any** sign-in by either break-glass account, regardless of result code.
- The rule is exempt from suppression and from incident-grouping (each sign-in produces its own incident).

### Steps

1. **Tag-only verification leg (every cycle).** Confirm rule presence, enabled state, P1 severity, no suppression, no grouping:

    ```powershell
    $r = Get-AzSentinelAlertRule -ResourceGroupName $ws.ResourceGroupName -WorkspaceName $ws.Name `
        | Where-Object DisplayName -eq 'BG-RULE-01'
    [pscustomobject]@{
        Enabled         = $r.Enabled
        Severity        = $r.Severity
        SuppressionDuration = $r.SuppressionDuration
        IncidentConfiguration = $r.IncidentConfiguration
    }
    ```

2. **Wiring verification.** Confirm the rule's KQL targets both break-glass UPNs (cross-reference Control 1.11's evidence for the canonical UPN list):

    ```kql
    // query_hash anchor: tc16-bg-rule-body-anchor-v1
    // expected substring in rule.query (compared by query_hash anchor, not by literal match)
    // SigninLogs | where UserPrincipalName in~ ("<bg-1-upn>", "<bg-2-upn>")
    ```

3. **Live trigger leg (annual, CISO-authorised).** Sign in to one break-glass account under the documented break-glass test procedure. Confirm:
    - `BG-RULE-01` raises a P1 alert within one rule-cycle.
    - Incident is created (no grouping with prior incidents).
    - `wf-notify-owner-soc` Logic App posts a P1 adaptive-card to the SOC channel and the CISO's incident channel.
    - The break-glass log (Control 1.11) is updated with the test event.

### Expected

- Tag-only verification: rule enabled, P1, no suppression, no grouping.
- Live trigger leg (annual): alert + incident + Teams notification all observed; Control 1.11 break-glass log updated.

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Rule definition export | `tc16-rule-<runId>.json` | **Books-and-records scope** — 6y/7y per FINRA 4511 / SEC 17a-4 |
| Live-trigger alert + incident export | `tc16-alert-<systemAlertId>.json`, `tc16-incident-<incidentNumber>.json` | **Books-and-records scope** — 6y/7y |
| Teams notification record | `tc16-teams-<messageId>.json` | Operational — 1y hot, 7y archive |
| Break-glass log update reference | `tc16-bglog-<entryId>.json` | **Books-and-records scope** — 6y/7y |
| CISO authorisation for live trigger | `tc16-ciso-auth-<runId>.json` | **Books-and-records scope** — 6y/7y |

### Remediation

- **Rule disabled:** P1 finding; re-enable immediately and open a Control 3.4 incident against the operator who disabled it (segregation-of-duties review under Control 2.8).
- **Rule modified to remove a break-glass UPN:** P1 finding; treat as potential insider-risk indicator and escalate to CISO + insider-threat program.
- **Live trigger did not produce alert:** the rule is silently broken; this is an existential finding for Control 1.11 and TC-15 returns `FAIL` regardless of all other passes.

---

## §17 TC-16 — Quarterly Evidence Bundle (Signed JSON Manifest with Five Attestations)

**Namespace:** `ATTEST` | **Owner:** AI Governance Lead (signers: Sentinel Admin + SOC Lead + AI Governance Lead + Compliance Officer + CISO) | **Cadence:** Quarterly

### Setup

- The cycle's TC-1 through TC-15 evidence records are collected from the operational evidence store.
- The firm's evidence-bundle signing key is held in Azure Key Vault under the `ai-governance-bundle-signer` key, with key-access policy restricted to the AI Governance Lead's HSM-backed identity. Implementation requires that the firm's Key Vault access reviews (Control 2.8) include this key.

### Steps

1. **Collection.** Aggregate all `tc1-*` through `tc16-*` artifacts from the cycle into a single working directory.

2. **Manifest generation.** For each artifact, capture: filename, SHA-256 hash, capture timestamp, owning operator UPN, regulatory-relevance tags (FINRA-4511, SEC-17a-4, NYDFS-500.06 / 500.16 / 500.17, FFIEC-IS, OCC-2011-12, FED-SR-11-7, SOX-404 as applicable). Emit a single `manifest.json`.

3. **KQL query-hash manifest.** Aggregate every `query_hash anchor` referenced by the cycle's TC executions into `query-hash-manifest.json`, mapping anchor → SHA-256 of canonicalised KQL → first-seen timestamp → catalog-version reference.

4. **Five signatures.** Sign the bundle in the documented order, capturing each signer's UPN, signature timestamp, signing-key identifier, and signed digest:
    1. Sentinel Admin (data-integrity attestation)
    2. SOC Lead (operational-completeness attestation)
    3. AI Governance Lead (governance-completeness attestation)
    4. Compliance Officer (regulatory-mapping attestation)
    5. CISO (final accept attestation)

5. **Lodgement.** Lodge the signed bundle into the Purview-labelled books-and-records store. Confirm the Purview label is applied and the lodgement receipt is captured.

### Expected

- `manifest.json` enumerates every cycle artifact; SHA-256 of every artifact verifies.
- `query-hash-manifest.json` enumerates every KQL anchor exercised; every hash matches the canonicalised text.
- Five signatures are captured in the documented order, with no gaps and no out-of-order signatures.
- Bundle lodged in Purview-labelled store with a 6y minimum locked retention (extending to 7y where SOX-404 applies, 12y if firm has elected the longer Sentinel archive period for cross-reference).

### Evidence Capture

| Artifact | Filename pattern | Retention tier |
|---|---|---|
| Cycle manifest | `tc17-manifest-<cycleId>.json` | **Books-and-records scope** — 6y/7y |
| KQL query-hash manifest | `tc17-query-hash-manifest-<cycleId>.json` | **Books-and-records scope** — 6y/7y |
| Signature bundle | `tc17-signed-bundle-<cycleId>.json.sig` | **Books-and-records scope** — 6y/7y |
| Lodgement receipt | `tc17-lodgement-<cycleId>.json` | **Books-and-records scope** — 6y/7y |

### Remediation

- **Hash mismatch on any artifact:** evidence integrity compromised; this is an existential finding for the cycle. Open a Control 3.4 incident, perform a root-cause investigation (operator error vs storage corruption vs tampering), and re-collect the impacted artifact under fresh signature. **Do not** lodge a bundle with an unexplained hash mismatch.
- **Signature out of order:** the bundle must be re-signed in the documented order. The out-of-order signature event is itself logged in the bundle metadata.
- **Lodgement receipt missing:** Purview label not applied at lodgement; remediate immediately and log the gap window.
- **Signer unavailable:** the firm's documented delegate-signer chain (Control 2.8) is invoked; the delegation event is captured in the bundle.

---

## §19 Canonical Evidence Capture Table (TC × Artifact × Retention × Regulation)

The following table is the canonical mapping for the cycle. It is the artifact inventory to be referenced by Control 3.4 incident evidence requests, by examiner inquiries, and by the Control 3.14 audit trail.

| TC | Artifact (filename pattern) | Retention tier | Regulation tie |
|---|---|---|---|
| TC-1 | `tc1-ingest-matrix-<runId>.json` | Operational — 1y hot / 7y archive | FFIEC-IS, OCC-2011-12 |
| TC-1 | `tc1-spnsi-presence-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-1 | `tc1-connector-state-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-1 | `tc1-attest-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-2 | `tc2-rule-presence-<runId>.json` | Operational — 1y / 7y | FFIEC-IS, FED-SR-11-7 |
| TC-2 | `tc2-rule-<RULE-ID>-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-2 | `tc2-drift-<runId>.json` | Operational — 1y / 7y | FFIEC-IS, OCC-2011-12 |
| TC-3 | `tc3-canary-request-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-3 | `tc3-alert-<systemAlertId>.json` | Operational — 1y / 7y | FFIEC-IS, NYDFS-500.16 |
| TC-3 | `tc3-incident-<incidentNumber>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-3 | `tc3-cascade-SUP-<ticketId>.json` | Operational — 1y / 7y | FINRA-3110 |
| TC-3 | `tc3-attest-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-4 | `tc4-anomaly-<correlationId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-4 | `tc4-incident-<incidentNumber>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-5 | `tc5-spnsi-<runId>.json` | Operational — 1y / 7y | FFIEC-IS, FINRA-3110 |
| TC-5 | `tc5-pim-<correlationId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-5 | `tc5-alert-<systemAlertId>.json`, `tc5-incident-<incidentNumber>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-6 | `tc6-policy-baseline-<runId>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-6 | `tc6-detect-<correlationId>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-6 | `tc6-revert-run-<runName>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-6 | `tc6-diff-<runId>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-6 | `tc6-attest-<runId>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-7 | `tc7-consent-<correlationId>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-7 | `tc7-alert-<systemAlertId>.json`, `tc7-incident-<incidentNumber>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-7 | `tc7-cascade-ARQ-<ticketId>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-8 | `tc8-orphan-<runId>.json` | Operational — 1y / 7y | OCC-2011-12, FED-SR-11-7 |
| TC-8 | `tc8-rr-<rrId>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-8 | `tc8-logicapp-<runName>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-9 | `tc9-detect-<runId>.json` | Operational — 1y / 7y | NYDFS-500.16, FFIEC-IS |
| TC-9 | `tc9-spn-pre-<runId>.json`, `tc9-spn-post-<runId>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-9 | `tc9-suspend-run-<runName>.json` | Operational — 1y / 7y | NYDFS-500.16 |
| TC-9 | `tc9-teams-<messageId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-9 | `tc9-rr-<rrId>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-10 | `tc10-runs-summary-<runId>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-10 | `tc10-defhash-<la>-<runId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, SEC-17a-3, SEC-17a-4 |
| TC-10 | `tc10-deep-<la>-<runName>.json` | Operational — 1y / 7y | OCC-2011-12 |
| TC-10 | `tc10-attest-<runId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, SEC-17a-4 |
| TC-11 | `tc11-timer-fire-<incidentNumber>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.06, NYDFS-500.16, NYDFS-500.17 |
| TC-11 | `tc11-escalation-<step>-<runId>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.17 |
| TC-11 | `tc11-kit-manifest-<runId>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.17 |
| TC-11 | `tc11-decision-<runId>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.17 |
| TC-11 | `tc11-closure-<runId>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.17 |
| TC-12 | `tc12-retention-<runId>.json` | Operational — 1y / 7y | FINRA-4511, SEC-17a-4 |
| TC-12 | `tc12-bnr-map-<runId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, SEC-17a-4, NYDFS-500.06 |
| TC-12 | `tc12-attest-<runId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, SEC-17a-4 |
| TC-13 | `tc13-matrix-<runId>.json` | Operational — 1y / 7y | NYDFS-500.06 |
| TC-13 | `tc13-classifications-<runId>.json` | Operational — 1y / 7y | NYDFS-500.06 |
| TC-13 | `tc13-watchlist-<runId>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.06 |
| TC-13 | `tc13-exception-<exceptionId>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.06 |
| TC-13 | `tc14-workbook-<DisplayName>-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-13 | `tc14-panel-<DisplayName>-<panel>-<runId>.png` | Operational — 1y / 7y | FFIEC-IS |
| TC-13 | `tc14-recon-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-14 | `tc15-out-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-14 | `tc15-in-<targetControl>-<runId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-14 | `tc15-loss-<runId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511 |
| TC-14 | `tc15-deep-<targetControl>-<eventId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-14 | `tc15-attest-<runId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511 |
| TC-15 | `tc16-rule-<runId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, SEC-17a-4 |
| TC-15 | `tc16-alert-<systemAlertId>.json`, `tc16-incident-<incidentNumber>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.16 |
| TC-15 | `tc16-teams-<messageId>.json` | Operational — 1y / 7y | FFIEC-IS |
| TC-15 | `tc16-bglog-<entryId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, NYDFS-500.06 |
| TC-15 | `tc16-ciso-auth-<runId>.json` | **Books-and-records — 6y / 7y** | NYDFS-500.06 |
| TC-16 | `tc17-manifest-<cycleId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, SEC-17a-4, SOX-404 |
| TC-16 | `tc17-query-hash-manifest-<cycleId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, SOX-404 |
| TC-16 | `tc17-signed-bundle-<cycleId>.json.sig` | **Books-and-records — 6y / 7y** | FINRA-4511, SEC-17a-4, SOX-404, NYDFS-500.06 |
| TC-16 | `tc17-lodgement-<cycleId>.json` | **Books-and-records — 6y / 7y** | FINRA-4511, SEC-17a-4 |

---

## §20 Document Footer

The verification cycle owner closes the cycle by producing the TC-16 signed bundle. Operational evidence is retained in the firm's evidence store; books-and-records-scope evidence is lodged in the Purview-labelled books-and-records store under the locked-retention policies verified by Controls 1.7 and 1.9.

For implementation context, see [Portal Walkthrough](./portal-walkthrough.md), [PowerShell Setup](./powershell-setup.md), and [Troubleshooting](./troubleshooting.md). For the upstream control specification, see [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
