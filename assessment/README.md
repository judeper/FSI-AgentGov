# FSI-AgentGov Assessment Engine

Automated governance assessment for Microsoft 365 Copilot Studio deployments in
Financial Services. Two complementary assessments share the same orchestrator:

- **Controls assessment** — Collects tenant configuration via APIs, scores 78
  controls against zone-specific thresholds, and generates a pre-filled
  assessment with a focused manual questionnaire. Audience: M365
  administrators, compliance officers preparing for audit.
- **Frontier Readiness assessment** — A 25-question facilitator-led
  self-diagnostic across the 5 capability drivers (Microsoft CAPE alignment).
  Identifies the scale-breaker driver and pattern readiness for the 6
  Frontier Transformation Patterns. Audience: CIO, CDAO, AI Governance Lead,
  AI Program Sponsor.

> **Assessment surface note:** The browser-based assessment SPA is a
> self-assessment questionnaire that scores answers entered by the assessor
> against the manifest's zone requirements. The Python assessment engine is a
> telemetry-driven scorer that evaluates collected tenant data (PPAC, Graph,
> Purview, SharePoint, Sentinel) against manifest `pass_condition` values. The
> two surfaces serve different audiences and operate on different inputs by
> design — the SPA is for facilitated self-assessment, the engine is for
> automated tenant verification. They share `assessment/manifest/controls.json`
> as a common source of truth but apply it differently.

## When to Run Which Assessment

| Run **Controls** if... | Run **Frontier Readiness** if... | Run **Both** if... |
|---|---|---|
| You are an M365 admin conducting a technical compliance baseline | You are a CIO/CDAO/AI Program Sponsor evaluating agent program maturity | You want a comprehensive program assessment with both strategic (Frontier) and tactical (Controls) outputs |
| Preparing for an audit or examiner readiness review | Deciding which Frontier Transformation Pattern to prioritize next | Onboarding a customer at the start of a transformation engagement |
| Remediating specific control gaps already known | Identifying the **scale-breaker** capability driver before investing in deeper controls work | Producing a board-level or examiner-facing maturity narrative that pairs strategic posture with control evidence |
| Time available: 2–4 hours collector runtime + manual questionnaire | Time available: 15–30 minute facilitator interview | Time available: both windows above |

**Recommended sequencing:** Run **Frontier Readiness FIRST** to identify the scale-breaker driver (the weakest of the five drivers — the ceiling on agent program scale), then run **Controls** to remediate the specific control gaps that move the scale-breaker driver forward. Re-run the Controls assessment after remediation to confirm uplift.

> **Note on outputs:** A Controls assessment surfaces "Control 1.5 DLP scored 2/4 because you have DLP policies but no sensitivity label auto-application" — actionable for an admin. A Frontier Readiness assessment surfaces "Your Organization & Culture driver scored 200 (Repeatable) — until you build a maker community and assign supervisor accountability per FINRA 3110, Pattern 1 Employee AI Enablement will not scale beyond pilot." Each assessment answers a different question. Don't expect one to substitute for the other.

## Architecture

```
run-assessment.ps1                           ← Orchestrator (PowerShell, -AssessmentType param)
├── collectors/
│   ├── Collect-PPAC.ps1                     ← Controls assessment
│   ├── Collect-Graph.ps1                    ← Controls assessment
│   ├── Collect-Purview.ps1                  ← Controls assessment
│   ├── Collect-SharePoint.ps1               ← Controls assessment
│   ├── Collect-Sentinel.ps1                 ← Controls assessment
│   └── Collect-Frontier.ps1                 ← Frontier Readiness assessment
├── engine/
│   ├── score.py                             ← 78-control scoring (0–4 maturity)
│   ├── score_frontier.py                    ← 5-driver scoring (100–500)
│   └── report.py                            ← --type controls | frontier | both
├── manifest/
│   ├── controls.json                        ← authoritative source 78-control manifest
│   └── frontier-readiness.json             ← 25-question Frontier manifest
├── tests/
│   ├── fixtures/
│   ├── test_score.py
│   ├── test_score_frontier.py               ← Frontier scoring tests
│   └── test_report.py
└── output/
    ├── collected/
    │   ├── ppac.json, graph.json, ...       ← Controls collectors
    │   └── frontier.json                    ← Frontier collector
    ├── scores.json                          ← Controls assessment
    ├── assessment-prefilled.md              ← Controls assessment
    ├── manual-questionnaire.md              ← Controls assessment
    ├── assessment-summary.json             ← Controls assessment
    ├── frontier-summary.json               ← Frontier assessment
    ├── frontier-prefilled.md               ← Frontier assessment
    └── capability-driver-rollup.json       ← Generated only when -AssessmentType Both
```

`assessment/manifest/controls.json` is the authored source manifest for both
assessment surfaces. The documentation build copies it to the SPA's runtime
asset path (`docs/assessment/data/controls.json` / `/assessment/data/controls.json`),
but contributor edits should always start in `assessment/manifest/controls.json`.

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

### Frontier Readiness Mode (interactive)

```powershell
.\run-assessment.ps1 `
    -TenantId "00000000-0000-0000-0000-000000000000" `
    -Zone 2 `
    -AuthMode Interactive `
    -CustomerName "Contoso Financial" `
    -AssessmentType Frontier
```

Sentinel parameters are not required when `-AssessmentType Frontier`. The orchestrator will run `Collect-Frontier.ps1` interactively, prompting you for each of the 25 questions.

### Frontier Readiness Mode (batch — pre-recorded answers)

```powershell
.\run-assessment.ps1 `
    -TenantId "00000000-0000-0000-0000-000000000000" `
    -Zone 2 `
    -AuthMode Interactive `
    -CustomerName "Contoso Financial" `
    -AssessmentType Frontier `
    -FrontierAnswersFile ".\contoso-frontier-answers.json"
```

The answers JSON shape is documented in `assessment/collectors/Collect-Frontier.ps1` (see `-InputFile`).

### Both Assessments in One Run

```powershell
.\run-assessment.ps1 `
    -TenantId "00000000-0000-0000-0000-000000000000" `
    -Zone 2 `
    -AuthMode Interactive `
    -CustomerName "Contoso Financial" `
    -AssessmentType Both `
    -SubscriptionId "..." -ResourceGroup "..." -WorkspaceName "..." `
    -FrontierAnswersFile ".\frontier-answers.json"
```

Produces both report sets PLUS `output/capability-driver-rollup.json` (cross-referencing controls scored maturity by capability driver tag).

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
| `output/collected/frontier.json` | JSON | Facilitator answers from the Frontier Readiness questionnaire |
| `output/frontier-summary.json` | JSON | 5-driver scores (100–500), scale-breaker, pattern readiness |
| `output/frontier-prefilled.md` | Markdown | Frontier readiness narrative with executive summary, scale-breaker analysis, pattern readiness, question-level detail |
| `output/capability-driver-rollup.json` | JSON | Per-driver rollup of Controls maturity scores (only when `-AssessmentType Both`) |

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

## Frontier Readiness Maturity Levels

The Frontier Readiness assessment scores each of the 5 capability drivers on the Microsoft 100–500 scale (NOT the 0–4 controls scale — these are different instruments answering different questions, see [docs/framework/agentic-capability-drivers.md](../docs/framework/agentic-capability-drivers.md) §"Why FSI does NOT mathematically merge maturity scales").

| Score | Level | Description |
|-------|-------|-------------|
| 100 | **Initial** | Ad-hoc; no documented processes; isolated practitioners |
| 200 | **Repeatable** | Patterns within a single business unit; informal coordination |
| 300 | **Defined** | Enterprise-wide documentation; named owners; reviewed cadence |
| 400 | **Capable** | Measured outcomes; refresh cadences; integrated reporting |
| 500 | **Optimized** | Continuous improvement; board-level integration; quarterly attestation |

The five drivers are: AI Strategy & Experience, Business Strategy, AI Governance & Security, Technology & Data, Organization & Culture.

The **scale-breaker** is the lowest-scored driver — the ceiling on how far any Frontier Transformation Pattern can scale, regardless of how strong the other drivers are.

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
| `tests/test_score_frontier.py` | ≥6 | Driver scoring (100–500), scale-breaker identification, pattern readiness |
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
