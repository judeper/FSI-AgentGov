# FSI-AgentGov Assessment Engine

Automated governance assessment for Microsoft 365 Copilot Studio deployments in
Financial Services. Collects tenant configuration via APIs, scores controls
against zone-specific thresholds, and generates a pre-filled assessment with a
focused manual questionnaire.

## Architecture

```
run-assessment.ps1          ← Orchestrator (PowerShell)
├── collectors/             ← Data collection scripts (one per API surface)
│   ├── Collect-PPAC.ps1
│   ├── Collect-Graph.ps1
│   ├── Collect-Purview.ps1
│   ├── Collect-SharePoint.ps1
│   └── Collect-Sentinel.ps1
├── engine/                 ← Scoring & report generation (Python)
│   ├── score.py
│   └── report.py
├── manifest/
│   └── controls.json       ← 78-control definition manifest
├── tests/                  ← Automated tests
│   ├── fixtures/           ← Synthetic test data
│   ├── test_score.py
│   └── test_report.py
└── output/                 ← Generated assessment artifacts
    ├── collected/          ← Raw collector JSON
    ├── scores.json
    ├── assessment-prefilled.md
    ├── manual-questionnaire.md
    └── assessment-summary.json
```

## Prerequisites

### PowerShell Modules

| Module | Collector | Purpose |
|--------|-----------|---------|
| `Microsoft.PowerApps.Administration.PowerShell` | PPAC | Environment, DLP, role assignment data |
| `Microsoft.Graph.Authentication` | Graph | Entra ID authentication |
| `Microsoft.Graph.Identity.SignIns` | Graph | Conditional Access policies |
| `Microsoft.Graph.Groups` | Graph | Security group enumeration |
| `ExchangeOnlineManagement` | Purview | Audit log, retention, compliance policies |
| `PnP.PowerShell` | SharePoint | Site permissions, sharing, grounding validation |
| `Az.OperationalInsights` | Sentinel | Log Analytics workspace & connector status |

### Python

- **Python 3.10+** required
- Install dependencies:

```bash
cd assessment
pip install -r requirements.txt
```

### Entra ID Permissions

#### Interactive Mode

Sign in as a Global Admin or a user with **all** of the following roles:

| Role | Scope |
|------|-------|
| Power Platform Administrator | PPAC collector |
| Compliance Administrator | Purview collector |
| Security Reader | Graph collector |
| SharePoint Administrator | SharePoint collector |
| Log Analytics Reader | Sentinel collector |

#### Service Principal Mode

Register an Entra ID application with the following **application** permissions:

| Permission | API | Collectors |
|-----------|-----|------------|
| `Policy.Read.All` | Microsoft Graph | Graph |
| `Group.Read.All` | Microsoft Graph | Graph |
| `Directory.Read.All` | Microsoft Graph | Graph |
| `AuditLog.Read.All` | Microsoft Graph | Graph |
| `Sites.Read.All` | Microsoft Graph | SharePoint |
| `Files.Read.All` | Microsoft Graph | SharePoint |
| Power Platform Admin API consent | Power Platform | PPAC |

> **Note:** Some collectors (Purview, Sentinel) may still require interactive
> authentication even in ServicePrincipal mode, depending on tenant
> configuration. Use `-SkipCollectors` for those if needed.

## Quick Start

### Interactive Mode (Recommended)

```powershell
.\run-assessment.ps1 `
    -TenantId "00000000-0000-0000-0000-000000000000" `
    -Zone 2 `
    -AuthMode Interactive `
    -CustomerName "Contoso Financial" `
    -SubscriptionId "00000000-0000-0000-0000-000000000001" `
    -ResourceGroup "rg-sentinel" `
    -WorkspaceName "sentinel-workspace"
```

### Service Principal Mode

```powershell
$secret = Read-Host -AsSecureString "Client Secret"

.\run-assessment.ps1 `
    -TenantId "00000000-0000-0000-0000-000000000000" `
    -Zone 3 `
    -AuthMode ServicePrincipal `
    -ClientId "00000000-0000-0000-0000-000000000002" `
    -ClientSecret $secret `
    -CustomerName "Contoso Financial" `
    -ApprovedSitesCsv ".\approved-sites.csv" `
    -SubscriptionId "00000000-0000-0000-0000-000000000001" `
    -ResourceGroup "rg-sentinel" `
    -WorkspaceName "sentinel-workspace"
```

### Skipping Collectors

Skip one or more collectors when their prerequisites aren't available:

```powershell
.\run-assessment.ps1 `
    -TenantId "..." `
    -Zone 2 `
    -AuthMode Interactive `
    -CustomerName "Contoso Financial" `
    -SkipCollectors @("Sentinel", "Purview")
```

> When a collector is skipped, controls that depend on its data are scored with
> **confidence: low** and flagged for manual review.

### Custom Output Directory

```powershell
.\run-assessment.ps1 ... -OutputDir "C:\Assessments\contoso-2026-03"
```

## Zones

The FSI-AgentGov framework defines three deployment zones with increasing
governance requirements:

| Zone | Name | Description |
|------|------|-------------|
| 1 | **Standard** | Internal agents, low-risk data, minimal regulatory overlap |
| 2 | **Sensitive** | Customer-facing or PII-handling agents, moderate compliance |
| 3 | **Regulated** | Agents in regulated workloads (banking, insurance, capital markets) |

Higher zones require more checks to pass per control, resulting in higher
maturity thresholds. A zone-3 assessment is the most stringent.

## Output Files

| File | Format | Description |
|------|--------|-------------|
| `output/collected/*.json` | JSON | Raw data snapshots from each collector |
| `output/scores.json` | JSON | Per-control scores, check results, confidence, and evidence |
| `output/assessment-prefilled.md` | Markdown | Pre-filled assessment report organized by pillar and control |
| `output/manual-questionnaire.md` | Markdown | Interview questions for controls requiring manual validation |
| `output/assessment-summary.json` | JSON | Machine-readable summary for dashboards and CI integration |

## Maturity Scale

Each control receives a maturity score from 0–4:

| Score | Level | Description |
|-------|-------|-------------|
| 0 | **Not Implemented** | Control is absent or all checks failed |
| 1 | **Baseline** (25%) | Minimal implementation — meets zone-1 threshold |
| 2 | **Recommended** (50%) | Standard compliance — meets zone-2 threshold |
| 3 | **Advanced** (75%) | Strong implementation with enhanced protections |
| 4 | **Fully Regulated** (100%) | Complete implementation — meets zone-3 threshold |

A control's maturity score is determined by comparing the number of passing
checks against the zone-specific threshold in the controls manifest. If the
passing count is below the minimum, the score is 0 (Not Implemented).

## Confidence Levels

Each control score includes a confidence indicator:

| Level | Meaning |
|-------|---------|
| **High** | All required API calls returned valid data |
| **Medium** | Some data sources returned partial results or warnings |
| **Low** | Required data sources were unavailable, null, or errored |

Low-confidence scores are highlighted in the assessment report and
automatically added to the manual questionnaire for validation.

## Collector Exit Codes

| Code | Meaning | Orchestrator Behavior |
|------|---------|----------------------|
| 0 | **Success** | All data collected cleanly |
| 1 | **Partial** | Some API calls failed; partial data saved | Logged as warning; run continues |
| 2 | **Failure** | Collector could not produce usable data | Logged as error; run continues |

The orchestrator never halts on collector failures. Downstream scoring handles
missing data by lowering confidence.

## Running Tests

```bash
cd assessment
pip install -r requirements.txt
pytest tests/ -v
```

### Test Coverage

| File | Tests | Focus |
|------|-------|-------|
| `tests/test_score.py` | 7 | Zone thresholds, maturity scoring, confidence, summaries |
| `tests/test_report.py` | 4 | Output file generation, Markdown structure, JSON schema |

### Test Fixtures

Test fixtures in `tests/fixtures/` provide synthetic tenant data for
deterministic, offline testing:

| Fixture | Contents |
|---------|----------|
| `controls_subset.json` | 5-control manifest (controls 1.1, 1.3, 2.1, 3.1, 4.4) |
| `ppac.json` | Power Platform environment, DLP, and role assignment data |
| `graph.json` | Conditional Access policies and Entra ID configuration |
| `purview.json` | Audit log config, retention policies |
| `sharepoint.json` | Site inventory, sharing settings, grounding scope |
| `sentinel.json` | Log Analytics workspace and connector status |
| `expected_scores.json` | Expected zone-2 scoring output for validation |

## Idempotency

Running the orchestrator multiple times with the same parameters cleanly
overwrites the output directory. No append-only files or cumulative state is
maintained between runs.

## Troubleshooting

### "Python 3 is required but was not found"

Ensure Python 3.10+ is installed and available as `python3`, `python`, or `py`
on your PATH.

### Collector authentication errors

- **Interactive mode:** Ensure you have the required admin roles and that your
  browser session isn't blocked by Conditional Access.
- **ServicePrincipal mode:** Verify the app registration has the correct API
  permissions and that admin consent has been granted.

### Missing Sentinel parameters

If you don't use Microsoft Sentinel, skip its collector:

```powershell
.\run-assessment.ps1 ... -SkipCollectors @("Sentinel")
```

### Partial collector results

When a collector returns exit code 1, check the `_metadata.warnings` array in
its output JSON for details on which API calls failed.
