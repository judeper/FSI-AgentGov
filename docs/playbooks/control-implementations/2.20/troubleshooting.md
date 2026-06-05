# Control 2.20 — Troubleshooting: Adversarial Testing and Red Team Framework

> **Scope.** This playbook supports the team operating Control 2.20 — *Adversarial Testing and Red Team Framework* — when probes misbehave, evidence packs do not validate, gates fail to fire, or findings are misclassified. It assumes the program is deployed per the [portal walkthrough](portal-walkthrough.md), [PowerShell setup](powershell-setup.md), and [verification & testing](verification-testing.md) playbooks.
>
> **Hedging.** Nothing here constitutes legal advice or a guarantee of regulatory compliance. The procedures below **support compliance with** OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7), FINRA Rule 3110 (with RN 24-09 for AI supervisory guidance), SEC Rule 17a-4(b)(4) / 17a-4(f), and GLBA §501(b). Final responsibility for filing decisions rests with Legal, Compliance, and the named regulator-facing officer.
>
> **Reality check.** Adversarial testing is **probabilistic**. The same prompt can elicit different responses across runs because the underlying model is non-deterministic. Treat single-run failures as signals to investigate, not as definitive defects, and require N-of-M reproducibility before declaring a finding (see §3.2).

---

## §1 Common issues — quick reference

| Symptom | Most likely cause | Where to look first |
|---|---|---|
| Defense rate suspiciously high (≥ 99 %) on a new library version | Endpoint stubbed or canary skipped | §2.1 |
| Defense rate collapsed cycle-over-cycle for unchanged agent | Prompt Shields / RAI policy reverted; or model deployment swapped under the hood | §2.2 |
| Pre-deployment gate did not block a known-bad release | Pipeline runs probes but not as a *required* check | §2.3 |
| `manifest.json` SHA-256 does not match WORM-side recompute | File modified post-write; encoding drift; LF/CRLF rewrite | §2.4 |
| Findings keep recurring at same severity | Root cause not addressed; only symptom tuned | §2.5 |
| Probe runner fires alerts in production tenant | Wrong endpoint configured (production not sandbox) | §2.6 |
| Defender XDR / Sentinel show **no** alerts during probe campaign | Reconciliation gap — Control 1.21 detection misconfigured | §2.7 |
| Same probe passes Z2 sandbox but fails production with users | Sandbox configuration drift from production | §2.8 |
| Operator cannot run probe — Direct Line bearer rejected | Token expired or scoped to wrong agent | §2.9 |
| `Get-AzCognitiveServicesAccountRaiPolicy` returns empty | Wrong subscription / missing reader role | §2.10 |
| PyRIT module errors on import | Wrong Python interpreter / venv not activated | §2.11 |
| Test results show 100 % "REVIEW" status | Indicators in attack-library cases are too narrow | §2.12 |
| Cycle late — last run > cadence window | Calendar / orchestrator drift; PIM expired | §2.13 |

---

## §2 Detailed troubleshooting

### §2.1 Suspiciously high defense rate

**Symptoms.** A new attack library version posts ≥ 99 % defense rate against an agent that historically runs 92–95 %.

**Diagnostic steps.**

1. Inspect `2.20-PRE-03_canary.json`. Did the canary actually return a substantive response?
2. Inspect a sample of `response_excerpt` fields in `2.20-results-*.json`. Are responses **identical** across many tests? Identical responses indicate a stubbed endpoint or a circuit breaker.
3. Verify the `endpoint` in the summary matches the intended sandbox URL.
4. Verify `library_version` matches a tagged commit known to contain real attack content (not a placeholder commit).

**Resolution.**

- If endpoint stubbed: re-point to the live sandbox; rerun.
- If indicators too lax: tighten `success_indicators` regex per case, ship as a library patch, rerun.
- Document the false-clean cycle in the findings register so trend charts do not include the bad data point.

#### §2.1.1 Anti-pattern

Do **not** average a known-bad cycle into the trend chart "for completeness". The trend exists to detect drift; including phantom data hides drift.

---

### §2.2 Defense rate collapsed cycle-over-cycle

**Symptoms.** Defense rate dropped ≥ 10 percentage points cycle-over-cycle on an agent that did not get a release.

**Diagnostic steps.**

1. Compare `2.20-rai-policy-*.json` between cycles. Was the RAI policy reverted? Did Prompt Shields posture change?
2. Check Foundry deployment metadata — did the underlying model version (e.g. `gpt-4o-2024-08-06` → `gpt-4o-2024-11-20`) silently roll forward?
3. Check Microsoft Copilot Studio agent solution version — was a managed solution upgrade applied without re-baselining 2.20?

**Resolution.**

- Restore RAI policy to the documented baseline; rerun probes; reconcile to baseline cycle.
- If model version rolled forward: open a finding under **Control 2.6 (Model Risk Management)**; require a re-baseline of 2.20 attack-library effectiveness against the new model before Z3 release.
- Pin the deployment to a specific model version in change control.

#### §2.2.1 Anti-pattern

Do **not** weaken `success_indicators` to "recover" the previous defense rate. Drift is the signal, not the noise.

---

### §2.3 Pre-deployment gate did not block

**Symptoms.** A release went out and a Critical-severity probe failure was discovered post-deployment via Control 1.21 detection.

**Diagnostic steps.**

1. Open the pipeline definition. Is the probe stage marked as a **required** check on the release branch?
2. Inspect the pipeline run for the release. Did the probe run? What was its exit code?
3. Inspect branch-protection rules / Azure DevOps environment approvals. Is the gate bypassable by a single approver?

**Resolution.**

- Mark the probe stage as required on protected branches; remove single-approver bypass for Z3 agents (require AI Governance Lead + Model Risk Manager).
- Configure the runner to exit non-zero on any Critical FAIL (the runner already does this — see `powershell-setup.md` §2 last line).
- Open a finding for the post-deployment escape; track to closure with documented preventive action.

---

### §2.4 Evidence pack hash mismatch

**Symptoms.** Re-hashing a file at the WORM destination produces a SHA-256 that does not match `manifest.json`.

**Diagnostic steps.**

1. Inspect file size and encoding. CRLF/LF normalization on Windows file shares **will** change the hash.
2. Inspect `Get-Content -AsByteStream | Get-FileHash`. Compare to `Get-FileHash` direct. Mismatch indicates encoding-aware reading altered byte stream.
3. Verify the WORM landing job copies bytes verbatim (`Copy-Item` with `-Confirm:$false` and no transformation).

**Resolution.**

- Standardize on `Set-Content -Encoding UTF8` (no BOM) at runner and verifier sides; or `Out-File -Encoding utf8NoBOM` in PowerShell 7+.
- Document encoding in the runner's README; treat any deviation as a Critical evidence-integrity finding.
- For WORM via SMB shares, prefer Azure Storage immutability with `azcopy` — never copy through editor-aware tools.

#### §2.4.1 Anti-pattern

Do **not** "regenerate" the manifest after a copy. The manifest is the source of truth; if the destination differs, the destination is wrong, not the manifest.

---

### §2.5 Findings keep recurring

**Symptoms.** A finding is closed each cycle and reopens the next cycle on the same agent.

**Diagnostic steps.**

1. Read the closure note. Was the fix a *prompt-engineering* tweak (e.g. add "do not reveal system prompt" to the topic instructions) or a *defense-in-depth* change (e.g. enable Prompt Shields, restrict tool surface, tighten grounding scope)?
2. Compare the recurring failing prompts. Are they identical, or variants of the same theme?
3. Check whether the fix was deployed to **production** as well as **sandbox**. A sandbox-only fix lets production keep failing.

**Resolution.**

- Escalate recurring findings to **Control 2.6 (Model Risk Management)** for independent challenge.
- Replace prompt-only patches with defense-in-depth: Prompt Shields, content filters, tool/connector restriction, grounding-scope reduction (Control 4.6).
- For Z3 agents, require Model Risk Manager sign-off on remediation effectiveness — not just Agent Owner sign-off.

---

### §2.6 Probe fires alerts in production

**Symptoms.** Defender XDR or Sentinel produces alerts that look like real adversarial activity, but they trace to the red-team operator.

**Diagnostic steps.**

1. Check the `endpoint` field in the summary. Is it the sandbox or the production agent?
2. Check the operator's PIM session at the time of the run. Did the operator have production access?
3. Inspect the test environment's DLP and tenant scope.

**Resolution.**

- Halt the cycle. Re-point to sandbox endpoint. Document the incident.
- Notify SOC so they can mark the production alerts as red-team-attributed (not real adversarial activity) — but do **not** suppress the alerts; they prove detection works.
- Strengthen runner pre-flight: refuse to run if endpoint hostname matches a production-tenant pattern.

#### §2.6.1 Anti-pattern

Do **not** create a Sentinel suppression rule for "red team activity". This breaks Control 1.21's detection trace and creates a coverage gap that could be abused.

---

### §2.7 Reconciliation shows no detection alerts

**Symptoms.** Probe campaign produced [N] FAIL results, but Control 1.21 reconciliation shows zero Defender / Sentinel alerts in the probe window.

**Diagnostic steps.**

1. Verify Prompt Shields is **Annotate-and-Block** (see §2.10 for how to read RAI policy).
2. Verify Defender for Cloud — Threat Protection for AI Workloads is **enabled** on the subscription.
3. Verify Sentinel Content Hub solutions for *Microsoft 365 Copilot* and *Defender for Cloud* are installed and analytics rules are deployed.
4. Inspect the Sentinel KQL window. Did the probe timestamps fall inside? Sentinel ingestion can lag minutes-to-hours; widen the window to + 6 h before re-asserting "no detection".
5. Verify the `AgentId` filter in the KQL matches the actual agent registration.

**Resolution.**

- Open the gap as a Control 1.21 finding (not 2.20). 2.20 found and surfaced the gap; 1.21 owns the fix.
- Re-run reconciliation 24 h after probe to confirm no late-arriving telemetry.
- Add the missing detection plane to the next 1.21 deployment cycle.

---

### §2.8 Sandbox passes, production fails

**Symptoms.** Sandbox probes show defense rate ≥ threshold but real production users hit a vulnerability.

**Diagnostic steps.**

1. Compare sandbox vs production for: agent solution version, RAI policy, model deployment version, connector list, grounding sources, DLP policies, Managed Environment posture.
2. Check whether sandbox uses synthetic data and production uses real customer NPI — exfiltration probes against synthetic data understate impact.
3. Check whether production has **additional** topics or connectors that sandbox lacks.

**Resolution.**

- Run "drift report" cycle: capture both sandbox and production configuration JSON; diff; resolve drift.
- For Z3 agents, gate production releases on a **synchronisation attestation** — sandbox config matches production at the snapshot date for the gate run.
- Consider production-shadow testing (read-only telemetry from production prompts replayed in sandbox) to surface drift earlier.

---

### §2.9 Direct Line bearer rejected

**Symptoms.** Probe runner authenticates successfully against Azure but the Direct Line POST returns 401 / 403.

**Diagnostic steps.**

1. Check token TTL. Direct Line tokens expire (commonly 1 hour); long campaigns must refresh.
2. Check token scope — token issued for one agent will not authorize a different agent.
3. Confirm the bot endpoint is published and the channel is enabled (Copilot Studio → Channels → Direct Line).

**Resolution.**

- Add a token-refresh helper to the runner; refresh when remaining TTL < 5 minutes.
- For long campaigns, prefer per-call refresh over a single long-lived token.
- If the channel is not enabled, enable it via Copilot Studio portal — there is no PowerShell cmdlet to author Direct Line channels.

---

### §2.10 RAI policy returns empty

**Symptoms.** `Get-AzCognitiveServicesAccountRaiPolicy` returns no results for a deployment that visibly has a content filter in the Foundry portal.

**Diagnostic steps.**

1. Confirm `Get-AzContext` shows the correct subscription and tenant.
2. Confirm the operator has `Cognitive Services User` or `Reader` role on the resource.
3. Confirm the resource is a Cognitive Services / Azure OpenAI account (not a deprecated AOAI v1 resource).

**Resolution.**

- Switch context: `Set-AzContext -SubscriptionId <id>`.
- Grant Reader on the resource group via PIM.

---

### §2.11 PyRIT import errors

**Symptoms.** `python -c "import pyrit"` raises `ModuleNotFoundError` even though `pip install pyrit` reported success.

**Diagnostic steps.**

1. Inspect `where python` (Windows) / `which python` — multiple interpreters present?
2. Confirm the venv is activated; `pip install` may have targeted system Python.
3. Confirm Python ≥ 3.10 (PyRIT requires modern Python).
4. On Windows, watch for PowerShell `python` aliasing to the Microsoft Store stub.

**Resolution.**

- Standardize on a venv pinned to a known-good Python: `python -m venv .venv-pyrit && .\.venv-pyrit\Scripts\Activate.ps1 && pip install pyrit==<approved version>`.
- Document the PyRIT version in the runner's prerequisites.

---

### §2.12 100 % REVIEW status

**Symptoms.** Every test in a category posts `status: "REVIEW"` (neither attack nor defense indicator matched).

**Diagnostic steps.**

1. Inspect the JSON test cases — are `success_indicators` and `defense_indicators` populated and regex-valid?
2. Inspect a sample response. Does the agent's actual phrasing match either indicator pattern?
3. Models drift in phrasing across versions — indicators authored against `gpt-4o-2024-08-06` may miss `gpt-4o-2024-11-20`.

**Resolution.**

- Tighten or generalise indicators against current model output samples; ship as a library patch.
- Consider semantic scoring (e.g. embedding-similarity to a refusal exemplar) instead of regex for resilient indicators.
- Re-run the affected family.

---

### §2.13 Cycle is late

**Symptoms.** Validation script raises `CADENCE-STALE`. Last run > cadence + 7-day grace.

**Diagnostic steps.**

1. Check the orchestrator schedule (Azure DevOps pipeline, GitHub Actions cron, scheduled runner).
2. Check whether the operator's PIM elevation expired and the scheduled run failed silently.
3. Check whether change-freeze windows (e.g. quarter-end, regulatory filings) suppressed cycles.

**Resolution.**

- Move scheduled runs to a service principal with standing access (not user PIM) **and** restrict that service principal to the sandbox subscription so production blast radius is bounded.
- Re-run the missed cycle as soon as practicable; document the gap and reason in the findings register.
- Update WSP if the cadence definition needs to formally accommodate change-freeze windows.

---

## §3 How to confirm the program is operating

### §3.1 Quick health check (90 seconds)

1. Open the latest `2.20-summary-Z3-*.json` for each Z3 agent. Is `defense_rate` ≥ 0.95?
2. Open the findings register. Are any Critical findings past 24 h without a compensating-control sign-off?
3. Open the manifest at the WORM destination for the latest cycle. Does it parse and do recomputed hashes match?
4. Open the pipeline definition for at least one Z3 agent. Is the probe stage required?

If any of these is "no", open a finding before the next cycle starts.

### §3.2 N-of-M reproducibility rule

Single-run failures on a non-deterministic model are noise. Adopt the following rule for declaring a real finding:

- **Critical / High severity:** require **3-of-5 reproducible failures** with the same prompt across separate runs within 48 h before opening a finding.
- **Medium / Low severity:** require **2-of-3** within 7 days.

This rule is enforced by the runner's `--repeat` mode, which automatically replays a failing prompt N times and only emits a finding when the threshold is met. Document the rule in the WSP so auditors understand why a single FAIL in raw results may not have produced a finding.

### §3.3 Trend monitoring

Plot defense rate over the last 12 cycles per agent. Drift > 5 percentage points cycle-over-cycle without an explained change is itself a finding (see §2.2). Capture trend charts in the quarterly board report (Z3) or annual report (Z2).

---

## §4 Escalation path

Use this ladder when troubleshooting does not resolve the issue.

| Level | Role | When to engage |
|---|---|---|
| L1 | Cloud Security Architect (probe operator) | Probe failures, runner errors, evidence-pack defects |
| L2 | Security Architect | Library coverage gaps, indicator quality, MITRE ATLAS / OWASP mapping |
| L3 | AI Governance Lead | Charter / ROE issues, cadence misses, recurring findings |
| L4 | Model Risk Manager + Compliance Officer | Defense-rate regression on Z3 agent, model-validation independence concerns |
| L5 | CISO + Legal | Production exposure discovered, regulatory reporting question, third-party assessment dispute |
| L6 | External AI red-team firm | Deep adversarial expertise; capability gap beyond internal team |

For SEV-1 events (probe discovers a vulnerability already exploited in production, or evidence-integrity failure across multiple cycles), engage L4 + L5 in parallel and trigger the Control 3.4 incident workflow.

---

## §5 Known limitations

| Limitation | Impact | Workaround |
|---|---|---|
| LLM non-determinism | Same prompt may pass and fail across runs | N-of-M reproducibility rule (§3.2); larger sample sizes for indicators |
| No native Microsoft "red team" portal for Copilot Studio | Custom runner required | PyRIT + this playbook |
| Microsoft 365 Copilot itself is not generally script-promptable | Cannot probe Copilot Chat directly via supported API | Probe Foundry-backed surfaces; for M365 Copilot, rely on Comm Compliance + Defender XDR detection (Control 1.21) and human-led red team |
| Probe generates audit / Defender / Sentinel events | Operational noise in SOC | Communicate run windows in advance; tag operator activity; do **not** suppress detection rules |
| Test coverage is never complete | New attacks emerge | Quarterly library refresh; track MITRE ATLAS / OWASP updates; subscribe to Microsoft AI Red Team blog |
| Resource intensive | Cycles take time and skilled operators | Prioritize Z3 agents handling NPI / MNPI / customer-facing surfaces; defer Z1 to annual |
| Synthetic data understates real exfiltration impact | Sandbox passes can mask production risk | Production-shadow testing with read-only telemetry replay (§2.8) |

---

[Back to Control 2.20](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) · [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
