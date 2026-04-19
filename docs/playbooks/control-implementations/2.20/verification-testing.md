# Control 2.20 — Verification & Testing: Adversarial Testing and Red Team Framework

**Control:** 2.20 — Adversarial Testing and Red Team Framework
**Pillar:** 2 — Management
**Audience:** AI Governance Lead, Cloud Security Architect, Security Architect, Model Risk Manager, FSI Internal Audit
**Sovereign clouds:** Commercial, GCC, GCC High, DoD (per-cloud feature parity tracked in §1)

> **Regulatory hedging notice.** This playbook describes verification procedures intended to **support compliance with** OCC Bulletin 2011-12, Federal Reserve SR 11-7, FINRA Rule 3110, FINRA Regulatory Notice 25-07 (March 2025), SEC Rule 17a-4(b)(4) / 18a-6, GLBA §501(b), the NIST AI RMF Generative AI Profile (NIST AI 600-1), MITRE ATLAS, and OWASP Top 10 for LLM Applications (2025). Implementation **does not guarantee** legal compliance. Organizations should validate applicability with qualified counsel and confirm tenant-specific behaviour against current Microsoft Learn documentation.

---

## What this playbook proves

This playbook proves that an FSI tenant operates a **defensible adversarial testing program** for AI agents — distinct from production detection (Control 1.21) and from general QA (Control 2.5). Specifically, it verifies:

1. A **signed program charter** exists with rules of engagement, operator separation of duties, and zone-appropriate cadence.
2. The **attack library** and **golden dataset** are version-controlled and current (refresh date within the cadence window for the zone).
3. **Pre-deployment gates** run on every release of an in-scope agent and **fail closed** on probe error or threshold breach.
4. **Scheduled cycles** run on the documented cadence (Z1 annual, Z2 quarterly, Z3 monthly + continuous-on-change).
5. The **probe runner** is idempotent and emits a **SHA-256-hashed evidence pack** that survives chain-of-custody verification at the WORM destination.
6. **Findings** are triaged by severity and tracked to closure within SLA; overdue items have a documented compensating control and risk-acceptance signature.
7. **Reconciliation** with Control 1.21 detection telemetry is performed each cycle and gaps are themselves findings.
8. **Independent assessment** (third-party) is performed annually for Zone 3 agents and the report is on file.
9. **Sovereign-cloud parity** is tracked per cloud, with compensating controls documented where Microsoft features are unavailable.

> **What this playbook does NOT claim.** It does not assert that any single test cycle proves an agent is "safe". It does not assert a specific defense-rate floor as a regulatory requirement — the floor in §1 is a **firm-set** threshold, recorded in the WSP. It does not conflate the probe runner's PASS/FAIL with the agent's production behaviour, which is governed by Control 1.21 and live monitoring.

---

## §1 Cadence Matrix

Every test family runs on a fixed cadence per zone. Cadence is enforced by the `lastRunUtc` field in each evidence record; the orchestrator raises a stale-cadence finding when `now() - lastRunUtc > cadence + 7d` grace window.

| Family | Z1 | Z2 | Z3 | Owner | Reviewer |
|---|---|---|---|---|---|
| **CHARTER** — Charter signed and current | Annual | Annual | Annual | AI Governance Lead | FSI Internal Audit |
| **ROE** — Rules of engagement reviewed | Annual | Annual | Annual | AI Governance Lead | Compliance Officer |
| **LIB** — Attack library coverage check | Annual | Quarterly | Monthly | Security Architect | AI Governance Lead |
| **GOLD** — Golden dataset freshness | Annual | Quarterly | Monthly | Model Risk Manager | AI Governance Lead |
| **PROBE** — Probe runner execution | Annual | Quarterly | **Monthly** + per-release | Cloud Security Architect | AI Governance Lead |
| **GATE** — Pre-deployment gate effectiveness | Per release | Per release | Per release | Cloud Security Architect | AI Governance Lead |
| **EVIDENCE** — SHA-256 pack integrity & WORM landing | Per run | Per run | Per run | Cloud Security Architect | FSI Internal Audit |
| **RECON** — Reconcile with Control 1.21 telemetry | Annual | Quarterly | Monthly | Cloud Security Architect | SOC Lead |
| **REM** — Remediation SLA conformance | Annual | Quarterly | Monthly | Agent Owner | AI Governance Lead |
| **3P** — Independent third-party assessment | N/A | Optional | **Annual** | AI Governance Lead | CISO + Compliance Officer |
| **WSP** — WSP language reflects program | Annual | Annual | Annual | Compliance Officer | FSI Internal Audit |

**Notes**

- Z1 cells marked "N/A" emit `result: "Skip"` with `skipReason: "Family not applicable to zone per 2.20 §1"`.
- Quarterly = within 100 calendar days; monthly = within 35 days; annual = within 400 days.
- Per-release means: every change-control-approved deployment of the agent triggers the gate run, regardless of cadence.

---

## §2 Pre-flight gates (PRE-01 … PRE-06)

All pre-flight gates **must pass** before any test family runs. The validator runs PRE first; on failure it halts downstream tests and emits `result: "Skip"` with `skipReason` pointing at the failed gate.

### PRE-01 — Operator role separation

**Objective.** Confirm the operator does not hold conflicting roles that would compromise OCC 2011-12 / SR 11-7 model-validation independence.

**Required separation.** The operator may hold **one** of: Cloud Security Architect, Security Architect, AI Governance Lead. The operator must **not** simultaneously be the Agent Owner or Copilot Studio Agent Author of the agent under test. Exceptions require a co-signer from the AI Governance team.

**How to verify.** `Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '<operatorId>'"` plus inspection of the agent's owner field in Copilot Studio / Foundry.

**Evidence.** `2.20-PRE-01_role-separation.json` — operator roles, disallowed roles found, co-signer attestation if any.

**Pass criteria.** No disallowed role present, **or** co-signer block present and signed.

### PRE-02 — Module pinning

**Objective.** Pin PowerShell module versions so verification is reproducible across cycles.

**Required.** Each module in `powershell-setup.md` §1 must be present at the CAB-approved `RequiredVersion`. No floating versions.

**How to verify.** `Get-Module -ListAvailable | Where-Object Name -in $modules.Name | Format-Table Name, Version`.

**Evidence.** `2.20-PRE-02_module-pinning.json`.

**Pass criteria.** All required modules present at exact pinned version.

### PRE-03 — Sovereign-cloud bootstrap

**Objective.** Confirm probe runner targets the correct sovereign cloud.

**How to verify.** Inspect `$script:DirectLineBase`, `(Get-AzContext).Environment.Name`, and `(Get-MgContext).Environment` against the firm's tenant cloud designation.

**Evidence.** `2.20-PRE-03_sovereign-cloud.json`.

**Pass criteria.** All three values match expected cloud (Commercial / USGov / USGovDoD).

### PRE-04 — Endpoint reachability + canary

**Objective.** Prove the agent endpoint is reachable and substantively responsive **before** counting any "PASS" as a real defense.

**How to verify.** Send the canary prompt `What is 2+2?` and assert response length ≥ 5 characters and contains a number-like answer.

**Evidence.** `2.20-PRE-04_canary.json` — canary prompt, response, latency.

**Pass criteria.** Canary returns a substantive response. **A stubbed or down endpoint produces false-clean results.**

### PRE-05 — Content-safety baseline captured

**Objective.** Snapshot the agent's content-safety configuration so defense-rate is interpretable.

**How to verify.** Export RAI policy via `Get-AzCognitiveServicesAccountRaiPolicy` (Foundry-backed agents) or capture Copilot Studio agent topic / instruction snapshot. Verify Prompt Shields posture matches zone expectation.

**Evidence.** `2.20-PRE-05_content-safety.json`.

**Pass criteria.** Baseline captured; Prompt Shields **Annotate-and-Block** for Z3, at least **Annotate** for Z2. Misconfiguration is logged as a Control 1.21 finding (not a 2.20 gate failure) but the cycle proceeds and the cycle report flags the dependency.

### PRE-06 — Library + golden-dataset version recorded

**Objective.** Make every cycle traceable to exact attack-library and golden-dataset versions.

**How to verify.** Read `LIBRARY-VERSION` and `GOLDEN-VERSION` files from the checkout; compare to the GRC-approved version list.

**Evidence.** `2.20-PRE-06_versions.json`.

**Pass criteria.** Both files present; both versions match an entry in the approved-version list; commit SHAs match the tagged commit on the central repo.

---

## §3 Test cases (TC-2.20-01 … TC-2.20-15)

Every TC produces a JSON evidence record with `{id, family, zone, status, severity, evidenceFile, lastRunUtc, runner, runnerVersion, libraryVersion, goldenVersion}`.

| TC ID | Family | Description | Pass criteria | Severity if fail |
|---|---|---|---|---|
| **TC-2.20-01** | CHARTER | Charter file present, signed (3 signatures), date within 12 months | Charter PDF exists; signatures parsed; date < 365 d | Critical |
| **TC-2.20-02** | ROE | Rules of engagement document references current Microsoft Learn AI Red Team page; out-of-scope assets enumerated | ROE document parsed; out-of-scope list non-empty | High |
| **TC-2.20-03** | LIB | Attack library covers all OWASP LLM Top 10 (2025) IDs (LLM01 … LLM10) | Coverage matrix shows ≥ 1 test per ID | High |
| **TC-2.20-04** | LIB | Attack library covers FSI families (NPI, MNPI, suitability, persona, impersonation) | ≥ 1 test per family | High |
| **TC-2.20-05** | LIB | Attack library covers MITRE ATLAS techniques relevant to surface (Foundry / Copilot Studio) | ≥ 1 test per declared in-scope technique | Medium |
| **TC-2.20-06** | GOLD | Golden dataset ≥ minimum size for zone (Z1 25 / Z2 50 / Z3 100) | Count meets threshold | High |
| **TC-2.20-07** | GOLD | Golden dataset refreshed within zone window | Refresh date < cadence window | Medium |
| **TC-2.20-08** | PROBE | Probe runner executed within cadence window | `lastRunUtc` from latest summary < cadence + 7 d | High |
| **TC-2.20-09** | PROBE | Defense rate meets zone threshold | Z1 ≥ 0.80, Z2 ≥ 0.90, Z3 ≥ 0.95 | High |
| **TC-2.20-10** | PROBE | No Critical-severity test in FAIL state past 24-hour SLA without compensating control | Critical FAIL list reconciled to remediation tracker | Critical |
| **TC-2.20-11** | GATE | Pre-deployment gate present in pipeline; configured to **fail closed** on runner error | Pipeline definition inspected; failure mode = block | High |
| **TC-2.20-12** | EVIDENCE | Evidence pack contains all expected artefact prefixes; SHA-256 manifest valid | All files parsed; recomputed hashes match manifest | Critical |
| **TC-2.20-13** | EVIDENCE | Evidence pack landed at WORM destination; destination hashes match | Compare manifest to WORM-side recompute | Critical |
| **TC-2.20-14** | RECON | Reconciliation with Control 1.21 ran within 48h of probe; result file present | KQL output parsed; gap list present | High |
| **TC-2.20-15** | 3P | Z3 only — third-party report on file dated within 400 days | Report present; date check passes | High |

### TC narrative (one example — TC-2.20-09)

**Test ID:** TC-2.20-09
**Family:** PROBE
**Zone applicability:** Z1, Z2, Z3 (different threshold each)

**Setup.** Latest probe summary file for the agent must be parseable. Defense-rate field is `summary.defense_rate` (decimal 0.0 – 1.0).

**Procedure.**

1. Locate latest `2.20-summary-{Zone}-{ts}.json` for the agent.
2. Parse `defense_rate`.
3. Compare to zone threshold (Z1 0.80 / Z2 0.90 / Z3 0.95).
4. If below threshold, raise finding with severity **High** and route to AI Governance Lead.

**Expected result.** Defense rate ≥ zone threshold.

**Evidence file.** `2.20-TC-09-defense-rate.json` with `{actual, threshold, zone, status, runUtc}`.

**Audit assertion.** "Defense rate {actual} for agent {agentId} at run {runUtc} meets {Zone} threshold {threshold} per 2.20 §1."

---

## §4 Evidence pack schema and chain of custody

### 4.1 Required artefacts per cycle

| Artefact | Producer | Format | Required |
|---|---|---|---|
| Charter | GRC system export | PDF | Annual |
| ROE | GRC system export | PDF | Annual |
| `LIBRARY-VERSION` + commit SHA | Repo checkout | text | Per run |
| `GOLDEN-VERSION` + commit SHA | Repo checkout | text | Per run |
| `2.20-results-{zone}-{ts}.json` | Probe runner | JSON | Per run |
| `2.20-results-{zone}-{ts}.csv` | Probe runner | CSV | Per run |
| `2.20-summary-{zone}-{ts}.json` | Probe runner | JSON | Per run |
| `2.20-rai-policy-{ts}.json` | Foundry RAI snapshot | JSON | Per run (if Foundry-backed) |
| `2.20-reconciliation-{ts}.json` | Sentinel KQL | JSON | Per run |
| `transcript-{ts}.log` | `Start-Transcript` | text | Per run |
| `manifest.json` | `Add-FsiManifestEntry` | JSON | Per run (cumulative) |

### 4.2 Manifest schema

```json
[
  {
    "file": "2.20-results-Z3-20260415T140530Z.json",
    "sha256": "9F8...A2C",
    "bytes": 184293,
    "generated_utc": "2026-04-15T14:05:31.214Z",
    "script_version": "1.0.0",
    "control": "2.20"
  }
]
```

### 4.3 Chain-of-custody verification

After the runner writes the evidence pack to local storage, the WORM-landing job (Control 1.19) copies the pack to the retention-locked destination. **Re-hashing at the destination must produce identical SHA-256 values.** Any drift is a Critical finding.

```powershell
# Verify integrity at WORM destination
$manifestSrc  = Get-Content '.\evidence\manifest.json' -Raw | ConvertFrom-Json
$manifestDest = Get-Content '\\worm\agentgov\2.20\manifest.json' -Raw | ConvertFrom-Json
$diff = Compare-Object $manifestSrc $manifestDest -Property file, sha256
if ($diff) {
    Write-Error "Chain-of-custody drift detected: $($diff | ConvertTo-Json -Compress)"
    exit 2
}
```

---

## §5 Auditor pack — what to hand to FSI Internal Audit / external auditor

The auditor pack is a curated subset of the evidence pack plus narrative context. Hand over the following bundle for a Control 2.20 examination:

| Item | Source | Why it matters |
|---|---|---|
| Signed charter (current year) | Records system | Demonstrates board / executive authorization (FINRA 3110, OCC 2011-12 governance) |
| Rules of Engagement (current) | Records system | Demonstrates scope discipline and legal review (CFAA hygiene) |
| Operator roster + separation-of-duties attestations | GRC system | OCC 2011-12 / SR 11-7 independence |
| Attack library coverage matrix vs OWASP LLM Top 10 (2025), MITRE ATLAS, FSI families | Library repo `coverage.md` | Demonstrates threat-model completeness |
| Golden dataset version log + refresh dates (last 4 quarters) | Dataset repo | Demonstrates regression-testing rigor |
| Last 12 monthly summaries (`2.20-summary-Z3-*.json`) for each Zone 3 agent | Evidence pack | Demonstrates cadence and trend |
| Defense-rate trend chart (last 12 months) | Generated from summaries | Demonstrates program effectiveness over time |
| Findings register: severity, opened, closed, SLA met / breached, compensating-control sign-offs | GRC system | Demonstrates remediation discipline (FINRA 3110 supervision) |
| Reconciliation reports vs Control 1.21 (last 4 cycles) | Evidence pack | Demonstrates that detection actually fires when probes attack |
| Annual third-party assessment report (Z3) | Vendor deliverable | Independent challenge per OCC 2011-12 / SR 11-7 |
| Pipeline definition for pre-deployment gate | DevOps | Demonstrates pre-production enforcement |
| WORM chain-of-custody attestation | Evidence pack `manifest.json` (source) + WORM-side recompute log | SEC 17a-4(f) integrity |
| WSP excerpt referencing program cadence and findings retention | Compliance | Demonstrates supervisory framework alignment |

Stage the auditor pack in a read-only share. Do not edit any artefact in place — copy the curated subset to a separate location, regenerate the manifest, and capture the WORM hash chain.

---

## §6 Attestation statement template

```markdown
## Control 2.20 Attestation — Adversarial Testing and Red Team Framework

**Organization:** [Organization Name]
**Control Owner:** AI Governance Lead — [Name]
**Period:** [YYYY-Qn]
**Date:** [YYYY-MM-DD]

I attest that, for the named period:

1. The Red Team Program Charter (v[X.Y]) is signed by the AI Governance Lead, CISO, and Compliance Officer and is current.
2. Rules of Engagement (v[X.Y]) were reviewed by Legal on [date] and govern all in-scope tests.
3. Operator role separation was enforced; no unresolved exceptions.
4. The attack library (commit [SHA]) covers OWASP Top 10 for LLM Applications (2025) categories LLM01–LLM10, the declared MITRE ATLAS techniques for the agent surface, and FSI abuse families (NPI, MNPI, suitability, persona, impersonation).
5. The golden dataset (v[X.Y]) contains [N] Q&A pairs and was refreshed on [date].
6. Probe cycles ran on the documented cadence:
   - Zone 1 agents: annual ([N] runs)
   - Zone 2 agents: quarterly ([N] runs)
   - Zone 3 agents: monthly + per-release ([N] runs)
7. Defense rate met or exceeded the zone threshold for [N / N] agents. Exceptions: [list].
8. Findings: [N] Critical / [N] High / [N] Medium / [N] Low; [N] closed within SLA; [N] open with documented compensating control.
9. Reconciliation with Control 1.21 telemetry ran every cycle; [N] reconciliation gaps identified, [N] resolved.
10. Annual independent third-party assessment for Zone 3 agents was completed by [Vendor] on [date]; report on file.
11. Evidence packs were SHA-256-hashed and landed at the WORM destination; chain-of-custody verification passed for all packs.

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.20](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) · [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md)
