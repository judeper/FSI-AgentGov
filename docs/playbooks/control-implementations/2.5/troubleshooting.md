# Control 2.5 — Testing, Validation, and Quality Assurance: Troubleshooting

**Pillar:** 2 — Management & Lifecycle Governance
**Control:** 2.5 — Testing, Validation, and Quality Assurance
**Playbook Type:** Troubleshooting & Incident Response
**Audience:** AI Governance Lead, Model Risk Manager, Copilot Studio Agent Authors, Compliance Officer, Designated Supervisor / Registered Principal, Power Platform Admin, Purview Compliance Admin
**Scope:** Failures, defects, governance breaches, and incidents arising across the five evaluation planes — Test Pane (developer smoke), Copilot Studio Agent Evaluation (repeatable batch), Azure AI Foundry / Evaluation SDK (quantitative quality and safety), PyRIT (adversarial), and Copilot Studio Analytics + production telemetry (post-deployment monitoring).

> **READ FIRST — §1 establishes the FSI incident-handling spine for this playbook.** All §2 pillar remediations and §3 runbooks reference §1 severity, evidence, and reportability constructs. Do not begin remediation work without classifying severity per §1.1 and consulting the reportability decision tree in §1.2.

---

## Table of Contents

1. **FSI Incident Handling for Testing & Validation Failures**
2. **Eight Troubleshooting Pillars** (symptom → root cause → diagnostic → remediation → validation → evidence)
3. **Nine Failure-Mode Runbooks** (narrative incident-response style)
4. **Evidence Preservation Standards**
5. **Communication & Escalation Patterns**
6. **Recovery & Re-Validation**
7. **Post-Incident Review (PIR) Template**
8. **Anti-Patterns & Common Mistakes**

---

## §1 — FSI Incident Handling for Testing & Validation Failures

Testing and validation failures in Microsoft 365 AI agents are not purely engineering bugs. In a US financial services firm they may simultaneously constitute (a) a Sarbanes-Oxley internal-control deficiency over financial reporting, (b) a FINRA Rule 3110 supervisory failure, (c) a SR 11-7 / OCC 2011-12 model risk-management deficiency, (d) a GLBA 501(b) safeguards weakness, and (e) under FINRA Notice 25-07 a registered-representative-conduct concern when an AI agent is producing supervised communications. Treating a failed evaluator score, a leaked holdout dataset, or a bypassed pipeline gate as a routine ticket — without classifying severity, preserving evidence, and consulting the reportability tree — creates legal, regulatory, and reputational exposure that can be material.

This section provides the spine that all later remediations and runbooks share.

### §1.1 — Severity Classification Matrix

Severity is the first decision. It governs response time, escalation depth, communication breadth, and whether external counsel and the reportability tree must be invoked. Classify within the first 30 minutes of detection and re-classify as facts evolve.

| Severity | Definition | Examples (Testing & Validation) | Initial Response | Escalation |
|---|---|---|---|---|
| **SEV-1** | Production agent producing unsafe, materially inaccurate, or non-compliant output to customers, registered representatives, or regulators; OR validation evidence integrity is in doubt for a deployed agent; OR a control bypass is confirmed and the agent is live. | Drift breach with confirmed customer harm; holdout leakage discovered after Zone-3 deployment; pipeline gate bypass on production agent; tampered evidence pack discovered during an examination. | Immediate containment within 1 hour. War-room. Pause / disable agent per Control 2.20. | AI Governance Lead, Model Risk Manager, CISO, Chief Compliance Officer (CCO), Legal/Privacy, Designated Supervisor; consider 24-hour notification to Operational Risk Committee. |
| **SEV-2** | High-risk validation defect with no confirmed customer impact yet, OR validation gate failure on a Zone-3 candidate that was about to be promoted, OR a recurring drift signal exceeding warning thresholds. | New jailbreak class identified in PyRIT but agent still gated; safety evaluator regression in pre-prod; evaluator family withdrawn from sovereign cloud affecting an upcoming deployment; SoD violation discovered before sign-off. | Containment within 4 hours. Hold all promotions touching the affected pattern. | AI Governance Lead, Model Risk Manager, Compliance Officer, Agent Owner, Designated Supervisor (informed). |
| **SEV-3** | Defect or process gap affecting a Zone-2 (team) agent, or a recoverable evaluator/quota incident with no governance breach. | Foundry quota exhaustion mid-run; transient grader timeouts; analytics dashboard data lag; a single failed verification criterion in a Zone-2 pilot. | Triage within next business day. Document remediation plan. | Agent Owner, AI Governance Lead (informed). |
| **SEV-4** | Cosmetic, documentation, or single-developer issue with no governance, regulatory, or production impact. | Test Pane authentication hiccup affecting one developer; manifest validation warnings in M365 Agents Toolkit; mis-labeled evaluator in a non-prod report. | Standard ticket queue. | Agent author, team lead. |

**Re-classification rule.** Severity may only move *up* without additional approval; downgrades require AI Governance Lead and Compliance Officer concurrence and a written rationale appended to the incident record. This supports SR 11-7 expectations that model-risk findings cannot be silently de-escalated.

### §1.2 — Reportability Decision Tree

After severity is set, walk this tree before *any* external communication. Answer in order. A "Yes" at any branch raises the question of mandatory or advisory regulatory notification, which is a Legal and Compliance decision — not an engineering decision.

- **Q1 — Customer impact?** Did an AI agent provide materially inaccurate, misleading, biased, or unsafe output to a customer, prospective customer, or registered representative who acted on it? If Yes → Legal and CCO engaged within 4 hours; evaluate Reg S-P / GLBA notification, FINRA 4530 reporting (customer complaint, settlement, regulatory action), state breach laws.
- **Q2 — Books-and-records integrity?** Did the failure compromise the completeness, accuracy, or immutability of records subject to SEC 17a-4(b)(4) or FINRA 4511 retention? If Yes → Records Manager and Legal within 4 hours; document the gap, remediation, and whether a 17a-4(f) attestation is implicated.
- **Q3 — Supervisory failure?** Did the failure indicate that the firm's written supervisory procedures (WSPs) under FINRA 3110 did not detect, prevent, or escalate AI-generated supervised communications? If Yes → Designated Supervisor and Legal; assess WSP gap and whether a Form U4/U5 disclosure is implicated for any registered person.
- **Q4 — Model risk materiality?** Is the affected agent classified as a "model" under SR 11-7 / OCC 2011-12, and does the failure represent a material change in performance, soundness, or use? If Yes → Model Risk Manager logs an MRM finding; notify Operational Risk Committee.
- **Q5 — Privacy or NPI exposure?** Did the failure disclose, log, or expose nonpublic personal information (NPI) under GLBA, PHI under HIPAA-adjacent rules, or PII under state privacy laws (e.g., CCPA/CPRA, NYDFS Part 500)? If Yes → Privacy Officer and Legal within 2 hours; preserve evidence per §4; evaluate breach notification clocks.
- **Q6 — Anti-fraud, AML, or market-conduct nexus?** Could the failure obstruct or compromise BSA/AML monitoring, market-abuse surveillance, or trade-supervision logic? If Yes → BSA Officer or AML Compliance; consider SAR filing implications.
- **Q7 — External examination active?** Is an SEC, FINRA, OCC, Fed, CFPB, or state regulator examination, sweep, or inquiry currently open touching this agent, this product, or this evaluation evidence? If Yes → Legal *only* communicates with examiners; freeze evidence per §4 and assume all artifacts are discoverable.

If all answers are No after Legal review, the incident is internal; document the reasoning explicitly in the PIR (§7). "No reportability" is itself a finding that should be auditable.

### §1.3 — Evidence Floor

For every SEV-1 and SEV-2 incident, and recommended for SEV-3, capture at minimum the following artifacts before any remediation that would alter system state. Hash and timestamp at capture; store in immutable retention (Purview retention label aligned to Control 1.7 and Control 1.21). Failure to capture this floor is itself a SR 11-7 / FINRA 3110 finding.

| ID | Artifact | Source |
|---|---|---|
| E-01 | Incident timeline (UTC, minute-level) | Incident commander notes |
| E-02 | Agent identity: tenant ID, environment ID, agent ID, version, last published timestamp | Power Platform Admin Center / Copilot Studio |
| E-03 | Model and orchestration configuration snapshot (model name, version, system prompt hash, tool/connector list, knowledge sources) | Copilot Studio export, M365 Agents Toolkit manifest |
| E-04 | Last successful validation evidence pack (datasets used, evaluator versions, scores, sign-offs) | Control 2.5 evidence repository |
| E-05 | Failing evaluator output (per-row scores, judge rationales where applicable) | Azure AI Foundry / Evaluation SDK / PyRIT |
| E-06 | Production telemetry window covering the failure (Copilot Studio Analytics export; App Insights traces if instrumented) | Analytics export |
| E-07 | Audit logs from Purview Unified Audit Log filtered to the agent, environment, and time window | Purview |
| E-08 | DLP / Sensitivity label events touching the agent or its data sources | Purview DLP / MIP |
| E-09 | Pipeline run logs and approver identities for the last promotion | Power Platform Pipelines / ALM Accelerator |
| E-10 | Solution Checker report for the last promoted solution version | Power Platform |
| E-11 | Sovereign-cloud inventory (commercial vs GCC vs GCC-H vs DoD) for the agent and its evaluators | Tenant inventory |
| E-12 | Communications log (who was notified, when, by what channel) | Incident commander notes |
| E-13 | Containment actions taken with timestamps and operator identity | Change record |

**Hash + sign on capture.** Use a witnessed SHA-256 of each artifact and write the hash to the incident record. This is the same evidentiary hygiene used for 17a-4(b)(4) records and is the single most common gap auditors cite.

### §1.4 — Compensating Controls (When You Cannot Fully Remediate)

Some incidents cannot be fully remediated within the response window — for example, an evaluator family is unavailable in GCC-High and Microsoft has not committed a date. In these cases, document explicit *compensating controls* that the firm will rely on until full remediation is possible. Compensating controls are not an excuse to skip a gate; they are a temporary, time-boxed, board-or-MRM-approved substitute.

Examples that have been used in practice:
- Substituting an internal human review queue (4-eyes per Control 2.3) for an unavailable automated safety evaluator, with daily sampling rate and reviewer roster documented.
- Constraining agent scope (Zone-3 → Zone-2 internal only) until the missing evaluator is restored.
- Increasing monitoring frequency in Copilot Studio Analytics from weekly to daily and lowering drift alert thresholds.
- Adding a pre-publish manual sign-off by the Designated Supervisor for any prompt or knowledge-source change.

Each compensating control must have an owner, an expiration date, an exit criterion (what restores the original control), and an MRM-or-Compliance approver of record.

### §1.5 — Pre-Escalation Checklist

Before paging an executive or convening a war-room, the on-call AI Governance Lead should confirm:

1. Severity classified per §1.1 with a written rationale.
2. Evidence floor (§1.3) capture *initiated* (not necessarily complete).
3. Containment option identified — at minimum a path to disable or scope-restrict the agent per Control 2.20.
4. Reportability tree (§1.2) walked with preliminary answers; Legal awareness flag set if any Yes.
5. Customer-facing or supervised-communication impact preliminarily assessed.
6. Sovereign-cloud scope identified (which tenants / environments / clouds are affected).
7. Last-known-good validation evidence located (E-04).

Skipping this checklist is the most common reason post-incident reviews find that "the firm reacted before it understood" — a finding that itself becomes an SR 11-7 governance deficiency.

### §1.6 — Communication Ladder

| Level | Audience | Trigger | Channel | Timing |
|---|---|---|---|---|
| L1 | Agent Owner, Author, on-call AI Governance Lead | Any SEV-3 or higher | Incident channel | Immediate |
| L2 | Model Risk Manager, Compliance Officer, Designated Supervisor | SEV-2 confirmed or any reportability "Yes" | Incident channel + email of record | Within 4 hours |
| L3 | CISO, CCO, Privacy Officer, Legal | SEV-1, or SEV-2 with Q1/Q2/Q5/Q7 = Yes | Phone + secure messaging | Within 1 hour of SEV-1; within 4 hours of qualifying SEV-2 |
| L4 | CEO / President, Board Risk Committee, External Counsel, Regulator (per Legal direction) | Confirmed material customer impact, confirmed examination nexus, or counsel advice | Per crisis-comms playbook | Per Legal |

All ladder events are themselves evidence (E-12). Do not communicate outward at L4 without Legal owning the message.

### §1.7 — Worked SEV-1 Example (Illustrative)

*A Zone-3 customer-service Copilot Studio agent is reported by a relationship manager to have given a client an inaccurate cost-basis explanation for a partial-share transaction. The agent has been live for three weeks since its last validation pack was signed.*

- **T+0:00** Agent Owner pages on-call AI Governance Lead. Severity initially SEV-2.
- **T+0:15** Lead pulls last sign-off (E-04) and sees the model was swapped two weeks ago via a "minor configuration change" without re-running the quality evaluator suite. Severity raised to **SEV-1** under §1.1 (validation evidence integrity in doubt for a deployed agent).
- **T+0:25** Containment: Power Platform Admin disables the agent in Production environment per Control 2.20; replaces with a maintenance message; pipeline locked.
- **T+0:30** Reportability tree (§1.2): Q1 Yes (customer received material misinformation), Q3 Yes (supervisory procedure for change management was bypassed), Q4 Yes (model swap without re-validation is an MRM finding). Legal and CCO paged at L3.
- **T+1:00** Evidence floor capture in motion (E-01..E-13); Purview audit log frozen for the relevant window.
- **T+2:00** Customer impact assessment: how many sessions were exposed to the swapped model? Analytics export (E-06) used to enumerate.
- **T+24:00** Incident report drafted; FINRA 4530 evaluation; client remediation by relationship manager and supervisor; PIR scheduled (§7); MRM finding logged.

The lesson — and the one regulators reinforce — is that **a model swap is a re-validation trigger, not a configuration change.** This pattern recurs in §3 Runbook 6.

### §1.8 — Diagnostic Query Reference

Frequently used queries during an incident. Treat output as evidence.

**Purview Unified Audit Log (KQL via Search-UnifiedAuditLog):**
```
Search-UnifiedAuditLog -StartDate (Get-Date).AddHours(-24) -EndDate (Get-Date) `
  -RecordType CopilotInteraction -ResultSize 5000 |
  Where-Object { $_.AuditData -match "<agentId>" } |
  Export-Csv -NoTypeInformation -Path .\E07-audit-<incident>.csv
```

**Copilot Studio Analytics export (PowerShell + Power Platform CLI):**
```
pac copilot analytics export --bot <botId> --environment <envId> `
  --start "<UTC start>" --end "<UTC end>" --output .\E06-analytics-<incident>.csv
```

**Pipeline run history (last promotion):**
```
pac pipeline list --environment <envId> --output json |
  ConvertFrom-Json | Where-Object { $_.SolutionUniqueName -eq "<solution>" } |
  Sort-Object CompletedOn -Descending | Select-Object -First 5
```

**Foundry evaluation run summary (Python, AI Evaluation SDK):**
```
from azure.ai.evaluation import EvaluationClient
client = EvaluationClient.from_connection_string(<conn>)
run = client.get_run("<run_id>")
print(run.status, run.metrics, run.artifacts)
```

**Solution Checker last result:**
```
pac solution check-result --solution-unique-name <solution> --output table
```

These five queries cover roughly 80% of the artifacts needed for E-05 through E-10. Run them early; their output is timestamped, which strengthens the evidentiary chain.

---

## §2 — Eight Troubleshooting Pillars

Each pillar follows the same shape: **Symptom → Likely Root Causes → Diagnostic Steps → Remediation → Validation → Evidence & Reportability.** These are the high-frequency operational issues; if a symptom escalates beyond what is shown here (e.g., production customer impact), pivot to §3 runbooks and §1 incident handling.

### Pillar 2.1 — Test Pane / Topic Test Failures

**Symptoms:** Test Pane in Copilot Studio fails to load the agent; topic test errors immediately on send; variables evaluate to `null`; a knowledge source returns "no results" for queries that previously worked; authentication loop when the test pane attempts to call a connected action.

**Likely root causes:**
- User signed into Copilot Studio with an identity that lacks delegated permissions to a Dataverse table, SharePoint site, or Graph scope referenced by the agent.
- A connection reference points to a connector that has been deleted, expired, or moved between environments by an unrelated solution import.
- The agent was edited in a different environment and the published version in the current environment is stale.
- Knowledge source indexing has not completed (large SharePoint sites can take hours after first attach).
- The Test Pane uses a different conversation state than published Teams/M365 channels — a topic that branches on `User.Id` may behave differently when impersonated by the test pane.

**Diagnostic steps:**
1. Confirm the published version timestamp on the agent vs the version being tested. Republish if drifted.
2. In Copilot Studio → Settings → Generative AI, verify the orchestration mode (classic vs generative) and the system prompt are as expected.
3. Open the Activity Map / Trace view for the failing turn. Identify which node fails and the exact error string.
4. For knowledge sources: open the source connector and trigger "Re-index now"; check the indexing status.
5. For connections: open Power Apps → Connections under your identity and confirm each referenced connector shows "Connected" with a non-expired token.

**Remediation:**
- Refresh stale connection references; if a connector was deleted, re-add and re-bind.
- For permission errors, request the missing role through standard access management (do not grant broad Dataverse roles to silence an error).
- Re-publish the agent after fixing references; test again in an incognito session to rule out cached tokens.
- For knowledge-source latency, wait for indexing to complete and confirm via a known-positive query.

**Validation:** Re-run the failing topic test and at least one regression scenario from the agent's smoke-test set. Confirm the Activity Map shows clean execution end-to-end.

**Evidence & reportability:** Test Pane failures during development are normally SEV-4. They become SEV-3 or higher only if (a) they reveal a permissions misconfiguration that may have been exploited at runtime, or (b) they are discovered post-deployment in a Zone-3 agent. In the latter case, capture E-02, E-03, E-07.

### Pillar 2.2 — Copilot Studio Agent Evaluation Failures

**Symptoms:** Test set import rejects the file; an evaluation run hangs in "Queued" indefinitely; grader timeouts; per-row scores all return `null`; "permission denied" when starting an evaluation; results show but the comparison view is empty.

**Likely root causes:**
- Test set CSV/JSON does not match the schema expected by the agent (missing required columns, encoding issues, embedded newlines without quoting).
- The signed-in user lacks the *Copilot Studio Author* role *and* the environment-level permission to invoke evaluations.
- Tenant-level capacity for AI evaluations is exhausted; runs queue but cannot dispatch.
- The agent under test was unpublished or deleted between submission and dispatch.
- Generative orchestration is disabled on the agent — many evaluators require it.

**Diagnostic steps:**
1. Re-export the test-set template from the Evaluations UI and diff against your file.
2. Check Power Platform Admin Center → Capacity → AI capacity; confirm available units.
3. In Copilot Studio → Evaluations → Run details, expand the run and read the per-stage status messages.
4. Reproduce with a 3-row mini test set to isolate dataset vs platform causes.

**Remediation:**
- Fix dataset schema; re-encode as UTF-8 without BOM if the importer rejects.
- Request additional AI capacity allocation through the Power Platform Admin.
- If the run is stuck, cancel and resubmit; capture the original run ID for the evidence pack.
- Ensure the agent is published before kicking off an evaluation.

**Validation:** Successful run with non-null per-row scores; comparison view shows the expected baseline-vs-candidate deltas; export the run summary as a CSV/JSON artifact for the evidence pack.

**Evidence & reportability:** Capture E-04 (run summary) and E-05 (per-row scores). If the failure occurred while validating a Zone-3 candidate that was already in a release window, raise to SEV-2 and pause promotion until evaluations succeed.

### Pillar 2.3 — Azure AI Foundry / Evaluation SDK Failures

**Symptoms:** Evaluator returns HTTP 429 (throttled) repeatedly; HTTP 401/403 from the evaluator endpoint; "evaluator not available in this region/cloud"; dataset rows fail with `KeyError` or schema mismatch; per-row scores return but aggregated metrics are missing; service principal authentication works locally but fails in pipeline.

**Likely root causes:**
- Tenant or subscription quota for the underlying model deployment is exhausted; evaluators that depend on a judge model (e.g., GPT-4o-class) are most affected.
- The managed identity used by the pipeline lacks `Cognitive Services User` (or equivalent) on the Foundry resource.
- Evaluator family is not deployed in the target Azure region or sovereign cloud (see Pillar 2.8).
- Dataset rows are missing required fields (`query`, `response`, `context`, `ground_truth` — varies by evaluator).
- Network egress from the build agent is blocked by firewall to the Foundry endpoint.

**Diagnostic steps:**
1. Inspect the evaluator response payload, not just the HTTP code; Azure returns structured error reasons.
2. Run `az role assignment list --assignee <miClientId> --scope <foundryScope>` to confirm RBAC.
3. Run a single-row evaluation locally with the same identity to bisect dataset vs auth vs network.
4. Check Foundry → Quotas and Models pages for region availability and TPM (tokens-per-minute) limits.

**Remediation:**
- Request quota increase or distribute load across regions (subject to data-residency constraints — Compliance must approve).
- Add backoff and retry to your evaluation harness; the SDK supports per-evaluator concurrency tuning.
- For schema errors, run dataset validation before submission; use the SDK's `EvaluationDataset.validate()` helper if available in your SDK version.
- For sovereign-cloud unavailability, see Pillar 2.8 and §3 Runbook 7.

**Validation:** Re-run the full evaluation; confirm aggregated metrics populate; record evaluator versions in the evidence pack (versions matter — a numeric score from evaluator vN is not directly comparable to vN+1).

**Evidence & reportability:** Capture E-05 with evaluator version metadata. If the failure delays a Zone-3 release, treat as SEV-2 and use the compensating-control pattern (§1.4) before considering any waiver.

### Pillar 2.4 — PyRIT Adversarial Campaign Failures

**Symptoms:** PyRIT orchestrator crashes mid-campaign; scorer chain misconfiguration causing all attacks to be marked "successful" or all "failed"; target endpoint rate-limits; dataset of seed prompts fails to load; results CSV has duplicate or missing rows.

**Likely root causes:**
- PyRIT version mismatch between the orchestrator and the scorer plugins.
- Target endpoint (the agent under test) is the production agent rather than a dedicated red-team replica — rate limiting and audit-log noise both follow.
- Scorer chain references a judge model that is unavailable or deprecated.
- Seed dataset includes copyrighted material or sensitive PII that triggers MIP DLP en route.
- Campaign was run by an identity lacking permission to write results to the configured storage account.

**Diagnostic steps:**
1. Pin and record exact versions: `pyrit`, scorer plugins, judge model, target agent version. This is required for reproducibility (an SR 11-7 expectation).
2. Inspect orchestrator logs for the exact failure stage (seed → attack → scoring → write).
3. Re-run a 5-prompt smoke campaign against a non-prod replica of the agent.
4. Confirm storage account RBAC and that the storage account is in an approved sovereign-cloud region.

**Remediation:**
- Stand up or use an existing dedicated red-team agent replica (Zone-2 environment is appropriate); never run adversarial campaigns against a production Zone-3 agent without explicit written authorization from CISO and Compliance.
- Pin a known-good combination of PyRIT, scorers, and judge model; record the combination in the evidence pack.
- Sanitize the seed dataset; remove anything with PII or copyrighted content unless the campaign explicitly tests those defenses and Legal has approved.

**Validation:** Smoke campaign returns expected mix of successes and failures; full campaign completes; results CSV row count matches expected count; scorer rationales are present and human-readable for a sample.

**Evidence & reportability:** Capture E-05 (scorer outputs) plus campaign manifest (seeds, scorers, target version, judge version). If the campaign discovers a *new* successful jailbreak class against a deployed agent, escalate per §3 Runbook 4 — do not treat as a routine PyRIT defect.

### Pillar 2.5 — Power Platform Solution Checker / Pipelines Failures

**Symptoms:** Solution Checker flags rules the team believes are false positives; pipeline approval times out; Managed Environment policy blocks the deployment; rollback fails or partially applies; pipeline runs succeed but the deployed solution does not match source.

**Likely root causes:**
- A new Solution Checker rule has been added in the latest platform update that legitimately flags pre-existing patterns.
- Approver email/Teams notification was filtered to spam; approver was unavailable; SLA expired.
- Managed Environment policy requires a sharing limit, DLP scope, or sensitivity label that the solution does not yet meet.
- The solution being promoted contains unmanaged customizations layered on top of a managed solution; rollback semantics differ.
- A connection reference in the target environment differs from source, causing post-import re-binding to drift.

**Diagnostic steps:**
1. Open the Solution Checker report and review each high/critical finding individually; do not bulk-suppress.
2. Pull the pipeline run JSON (`pac pipeline list ... --output json`) and inspect every stage transition.
3. Check Managed Environment policies in Power Platform Admin → Environments → Policies.
4. Diff the source solution `.zip` and the deployed solution export; identify drift.

**Remediation:**
- Address Solution Checker findings at source; suppress only with documented justification approved by the Power Platform Admin and the AI Governance Lead.
- Add a backup approver to every pipeline stage; configure SLA escalation.
- Update the solution to comply with Managed Environment policy or, with documented MRM approval, request a temporary policy exception bounded by an expiration date.
- For rollback failures, restore from the last known-good solution backup; never leave a partially rolled-back state in production.

**Validation:** Pipeline completes end-to-end; Solution Checker is clean (or all suppressions are documented); the deployed solution hash matches the source artifact.

**Evidence & reportability:** Capture E-09 (pipeline run + approvers) and E-10 (Solution Checker report). A bypassed gate is an SR 11-7 / FINRA 3110 concern — see §3 Runbook 3.

### Pillar 2.6 — M365 Agents Toolkit Local Sideload Failures

**Symptoms:** `teamsapp validate` fails with manifest schema errors; tunnel does not establish; debug attach fails; sideload upload to a personal sandbox tenant returns "policy blocked"; agent runs locally but Graph calls fail.

**Likely root causes:**
- Manifest schema version is older than the toolkit version expects; required fields (e.g., new copilot extension blocks) missing.
- Local dev tunnel port already in use or blocked by enterprise firewall.
- Sideload disabled at tenant level for security reasons (correct posture for production tenants — use a dedicated dev tenant).
- Graph permissions consented in the wrong tenant; tokens issued for the dev tenant cannot reach prod resources (and should not).
- Node / .NET runtime version mismatch with toolkit requirements.

**Diagnostic steps:**
1. Run `teamsapp validate --env local` and address each schema error.
2. Confirm tunnel: `devtunnel list` and `devtunnel host` outputs.
3. Confirm tenant policy: in Teams Admin Center → Teams apps → Setup policies, check sideload allowance.
4. Inspect token issuer and audience claims when Graph calls fail.

**Remediation:**
- Use a dedicated dev/sandbox tenant for sideload; never weaken production tenant sideload policy to satisfy a developer workflow.
- Update manifest to the schema version the toolkit expects; pin toolkit version per project.
- Resolve port conflicts; if firewall blocks tunnels, use the documented enterprise relay or shift to a cloud-hosted dev container.

**Validation:** App side-loads cleanly into the dev tenant; debug attach hits a breakpoint; Graph calls succeed for the dev-tenant identity.

**Evidence & reportability:** Local sideload failures are SEV-4 unless they reveal that production sideload policy has been weakened — in which case escalate to SEV-2 and capture E-07 (audit log of policy change).

### Pillar 2.7 — Copilot Studio Analytics / Quality Dashboard Issues

**Symptoms:** Analytics dashboards are blank or stale; specific metrics (e.g., resolution rate, escalation rate) are missing; drift threshold alerts fire repeatedly without apparent reason; a metric value differs between the UI and an exported CSV.

**Likely root causes:**
- Analytics ingestion lag (typical lag is hours, can extend during platform incidents).
- The agent's telemetry collection setting is off, or a recent publish reset it.
- Drift baseline was computed on a small or unrepresentative window.
- A change in user population (e.g., rollout to a new business unit) shifts the input distribution legitimately, triggering drift alerts that are real but not defective.
- Time-zone mismatch between dashboard (tenant default) and exported CSV (UTC).

**Diagnostic steps:**
1. Check Microsoft 365 service health and Power Platform admin announcements for ingestion incidents.
2. Verify analytics is enabled on the agent: Copilot Studio → Settings → Analytics.
3. Re-baseline drift using a representative window (typically 14–30 days of post-deployment traffic).
4. Reconcile UI vs CSV by normalizing time zones.

**Remediation:**
- For lag, wait and re-check; do not alter the agent based on incomplete data.
- For mis-baselined drift, recompute and document; obtain MRM concurrence on the new baseline.
- For real distribution shifts, this is an input — schedule a re-validation cycle (§6); do not silence the alert.

**Validation:** Dashboards repopulate; drift alerts are explainable; metric reconciliation succeeds across UI and export.

**Evidence & reportability:** A confirmed sustained drift breach in a Zone-3 agent is SEV-1/SEV-2 — see §3 Runbook 5. A dashboard outage that prevents monitoring is itself a control gap (Control 2.5 + 2.20) and should be tracked even if no production harm has occurred.

### Pillar 2.8 — Sovereign Cloud Parity Issues (GCC / GCC-H / DoD)

**Symptoms:** An evaluator family available in commercial cloud is not deployable in GCC-High or DoD; a model version used in commercial validation has no DoD equivalent; PyRIT scorer's judge model is unavailable; Foundry features differ between clouds (lagging GA).

**Likely root causes:**
- Microsoft's published feature parity matrix shows the feature is not yet in the target cloud, or is in preview only.
- The tenant identity used has not been granted access to the sovereign tenant resources (sovereign clouds typically require separate identities).
- Data-residency policy (legitimately) prevents cross-cloud calls that the evaluator implicitly attempts.

**Diagnostic steps:**
1. Consult the official Microsoft Learn parity pages for the specific evaluator/model and the target cloud; record the date checked and version observed.
2. Confirm regional availability inside the sovereign cloud (e.g., USGov Virginia vs USGov Arizona for GCC-H).
3. Confirm identity and RBAC in the sovereign tenant.

**Remediation:**
- If parity is not yet available, document a compensating control (§1.4) — typically a substituted human review queue plus an enhanced manual evaluator — with an explicit expiration date and an MRM approver.
- Constrain the agent's zone or scope until parity is achieved (e.g., do not deploy to Zone-3 in DoD until the safety evaluator is generally available).
- Track Microsoft's roadmap and re-evaluate quarterly.

**Validation:** Compensating control is operating (sampling rate, reviewer roster, evidence collection); zone restriction is enforced in the relevant environment.

**Evidence & reportability:** Capture E-11 (sovereign-cloud inventory) and the compensating-control approval. A sovereign-cloud parity gap that is *not* covered by a compensating control and where an agent has been deployed anyway is an SR 11-7 deficiency — escalate per §3 Runbook 7.

---

## §3 — Nine Failure-Mode Runbooks (Incident-Response Style)

These runbooks are deliberately written in narrative form. Each represents a class of incident that recurs in FSI implementations of M365 AI agents and that does not lend itself to a terse symptom-remediation card. Each runbook follows the structure: **Scenario → Severity Classification → Immediate Actions (T+0 to T+1h) → Investigation (T+1h to T+8h) → Containment → Eradication → Recovery → Lessons Learned → Regulatory Reporting Decision Tree → Evidence References.** All references back to §1 should be honored — these runbooks assume the §1 spine has been read.

### Runbook 1 — Holdout Dataset Leakage Discovered

**Scenario.** During a quarterly attestation cycle the AI Governance Lead reviews the validation evidence pack for a Zone-3 customer-service agent and notices that several rows in the holdout dataset used to score the latest release also appear, verbatim, in the supervised fine-tuning corpus that the prompt-engineering team built when iterating on the system prompt. In other words, the holdout was not actually held out — the agent's "high" quality scores were partially memorization. The agent has been live for six weeks.

This pattern — holdout leakage — is one of the most common and most damaging defects in AI validation. It is the reason SR 11-7 emphasizes *independent* validation: a developer who creates the test set and the training data is structurally biased toward leakage even when acting in good faith. It is also why FINRA Notice 25-07 expects firms to demonstrate not just that they tested an AI tool but that the tests were *meaningful* tests.

**Severity classification.** SEV-1. The integrity of validation evidence is in doubt for a deployed Zone-3 agent. This is true even if the agent's actual production behavior has been acceptable, because the evidence on which the deployment decision rested is now unreliable. Re-classifying downward without re-validation would itself be an SR 11-7 finding.

**Immediate actions (T+0 to T+1h).**
1. Page Model Risk Manager, Compliance Officer, AI Governance Lead, Agent Owner. Open incident channel.
2. Freeze all in-flight promotions touching this agent or any sibling agent that may share the same datasets. The leakage may be a corpus-management defect that affects multiple agents, not just this one.
3. Capture E-04 (the contaminated evidence pack) and quarantine — do not delete, do not amend in place. The original is itself evidence.
4. Snapshot the current production agent (E-02, E-03) for later comparison.
5. Consider, but do not yet execute, a Control 2.20 disable. The decision to take the agent offline is a business-impact decision and requires the Agent Owner plus Compliance concurrence; see Containment.

**Investigation (T+1h to T+8h).**
- Determine the *extent* of leakage: how many holdout rows are contaminated, and by what mechanism (direct copy, paraphrase, embedding-similarity duplication)?
- Determine the *vintage* of leakage: when did the contaminated rows enter the training corpus relative to when they entered the holdout?
- Determine *who* had visibility into both corpora — this is a SoD diagnosis, not a blame exercise, but the answer matters for §3 Runbook 2.
- Determine whether the agent's *production* behavior shows signs of memorization (e.g., near-verbatim responses to holdout-style prompts in production telemetry — pull E-06).
- Re-score the agent on a *clean* holdout — built independently by the validation team, drawn from production-distribution data with PII handled per Control 1.6, never seen by the development team. This is the truth-test.

**Containment.** If the clean re-score shows the agent's true quality is materially below the deployment threshold, take the agent offline (Control 2.20) and substitute either a prior known-good version or a maintenance message. If the clean re-score is within acceptable bounds, the agent may remain live under enhanced monitoring (daily Analytics review, lowered drift thresholds, increased human sampling per Control 2.3) while remediation proceeds. Document this decision and its approver explicitly.

**Eradication.**
- Rebuild the holdout dataset from scratch under the supervision of an independent validator who did not contribute to the training corpus.
- Implement (or fix) the corpus-segregation control: separate storage accounts for training vs holdout, separate access groups, automated overlap detection on commit.
- Update Control 2.5 evidence-pack template to require an *overlap report* (cryptographic hash + embedding-similarity check) between training and holdout as a sign-off artifact.
- Re-validate the agent end-to-end against the clean holdout and refresh the evidence pack.

**Recovery.** Promote only after the clean re-validation meets thresholds and Compliance + MRM sign off. If the agent had to be taken offline, restore in stages — Zone-2 internal pilot first, then Zone-3 — with daily monitoring for the first two weeks.

**Lessons learned.** The most common root cause is convenience: developers reuse high-quality curated examples in both places because it is easier than sourcing fresh data. The fix is process, not technology. Bake the overlap report into the gate and the leak cannot reach production unnoticed.

**Regulatory reporting decision tree.** Walk §1.2. Q3 (supervisory failure) is typically Yes — the firm's WSPs did not detect the leak before deployment. Q4 (model risk materiality) is Yes by definition for a SEV-1 of this kind. Q1 depends on whether the clean re-score reveals customer-impacting inaccuracy. Legal and CCO own the final reportability call.

**Evidence references.** E-01, E-02, E-03, E-04 (quarantined), E-05 (clean re-score), E-06, E-09, E-12, E-13, plus the new overlap-report artifact going forward.

### Runbook 2 — Validator-Developer Conflation (Segregation-of-Duties Violation)

**Scenario.** During an internal audit the auditor pulls the sign-off chain for the last three Zone-3 agent releases. In all three, the validator listed in the evidence pack is the same person as either the prompt author, the knowledge-source curator, or the pipeline approver. In one case the same individual appears in all four roles. The agents were promoted; the evidence packs are signed; the audit log shows no anomalies.

This is a **segregation-of-duties (SoD) violation** with respect to Control 2.5 and Control 2.1. SR 11-7 explicitly requires independence between model development and model validation; FINRA 3110 supervisory expectations are similar in spirit (the supervisor is not the supervised). When the same human plays both roles, the validation is not independent, regardless of how technically rigorous it was.

**Severity classification.** SEV-2 if discovered before any customer-facing harm and the agent is performing acceptably. SEV-1 if combined with any other finding (drift breach, leakage, customer complaint) or if discovered during an external examination.

**Immediate actions (T+0 to T+1h).**
1. Page AI Governance Lead, Compliance Officer, Model Risk Manager, Internal Audit liaison. Notify the Agent Owners.
2. Freeze further promotions of the affected agents until independent re-validation is complete.
3. Capture E-09 (pipeline runs and approver identities) and E-04 (signed evidence packs) for the affected releases.
4. Pull the access-management history for the implicated identities — when were they granted each role, by whom, under what justification?

**Investigation (T+1h to T+8h).**
- Map the actual versus intended SoD model. Which roles should never overlap? (Author ≠ Validator. Validator ≠ Approver. Records Manager ≠ any of the above for evidence retention purposes.)
- Determine *how* the conflation happened: a thin team that legitimately had no second qualified validator? A role-assignment defect in the access-management process? A workflow that allowed self-approval?
- Determine *scope*: only the three audited releases, or a pattern across the entire portfolio? Pull the pipeline-run history across all agents and look for the same identity in author + validator columns.
- Engage Internal Audit early — this finding is likely to appear in their report regardless of how the firm responds, and pre-coordinated language is better than surprised language.

**Containment.** Do not silently re-sign the evidence packs. The original sign-offs are evidence; replacing them is itself a finding. Instead, append an *addendum* to each affected pack stating the SoD breach was discovered, the date discovered, the scope, and the remediation plan. Independent re-validation evidence is added to the pack alongside, not in place of, the original.

**Eradication.**
- Implement role-conflict detection in the pipeline: a pre-promotion check that compares the author identity against the validator identity and the approver identity against both, and blocks promotion if overlap exists, with a documented exception path requiring AI Governance Lead approval for genuine staffing constraints.
- Where the team is too thin to staff independent roles internally, source a validator from a sibling team, an internal audit function, or an approved third-party validator. Document the arrangement in the evidence pack.
- Update access-management runbooks to require a SoD-impact review when granting Copilot Studio Author + Validator + Power Platform Pipeline Approver roles to the same identity.

**Recovery.** Independently re-validate each affected agent. If re-validation fails any threshold, treat as SEV-1 and follow §3 Runbook 1 recovery pattern. If re-validation passes, the agent remains live with the addended evidence pack.

**Lessons learned.** SoD violations almost never look malicious; they look like productivity. A small team racing a deadline collapses roles to ship. The fix is platform enforcement, not policy memos: if the pipeline cannot promote when roles overlap, the team is forced to source independent validators and the control becomes self-enforcing.

**Regulatory reporting decision tree.** Q3 (supervisory failure) is Yes — the WSPs permitted the conflation. Q4 (model risk) is Yes. Q7 (active examination) elevates urgency dramatically — if Internal Audit is mid-cycle or an external exam is open, Legal must be in the loop within the same business day.

**Evidence references.** E-04, E-09, E-12, plus access-management history (out-of-band) and the SoD-detection rule artifacts going forward.

### Runbook 3 — Pipeline Gate Bypass Detected

**Scenario.** The Power Platform Admin runs a quarterly review of pipeline-run history and notices that two solution promotions to the Production environment over the last quarter completed without invoking the Solution Checker stage, and one of them also skipped the Compliance approval stage. The deployments were performed via a maintenance flow by a privileged account, not through the standard pipeline. The agents in question are still live.

A pipeline gate bypass is one of the most serious findings in any deployment-controls regime. It does not matter whether the agent is currently behaving well — the firm has no evidence that the standard quality and compliance gates were ever satisfied for these versions, and the act of bypassing the gate is itself the issue.

**Severity classification.** SEV-1 if the bypassed promotion targeted Production / Zone-3. SEV-2 for Zone-2. The default assumption should be SEV-1 until scope is fully understood.

**Immediate actions (T+0 to T+1h).**
1. Page CISO, AI Governance Lead, Model Risk Manager, Compliance Officer, Power Platform Admin, Internal Audit. Open incident channel.
2. Freeze all maintenance-flow promotions and all privileged-account promotions to Production. Standard pipeline only.
3. Capture E-09 (full pipeline history including the bypassed runs), E-07 (Purview audit log of the privileged-account activity), and E-02/E-03 for the affected agents.
4. Identify the human(s) who performed the bypass and the human(s) who could have detected it but did not.

**Investigation (T+1h to T+8h).**
- Reconstruct the timeline: when was the maintenance flow created? When was each bypassed promotion executed? What changed in each promotion?
- Determine *why*: emergency change with documented break-glass approval (which would be a different and lesser finding), or routine convenience (which is the worst case)?
- Determine the universe of in-scope promotions: any other deployments that used the same maintenance flow or privileged path? Search Purview for all uses.
- Pull the most recent validated evidence pack for each affected agent and compare its version hash against the currently deployed version. Are they the same? If not, the deployed version has *no* validation evidence on record — that is a discrete additional finding.

**Containment.**
- Rotate or constrain the privileged accounts used to perform the bypass. Move them to just-in-time elevation (PIM) with a documented approval workflow.
- Disable the maintenance flow path; any future emergency change must use a documented break-glass procedure that still emits the gate evidence.
- For each agent whose deployed version lacks current validation evidence, decide whether to (a) take the agent offline and roll back to the last validated version, or (b) keep the agent live under enhanced monitoring while emergency re-validation runs. (b) is acceptable only with explicit MRM + Compliance + CISO sign-off, time-boxed, with daily status reports.

**Eradication.**
- Implement deny-by-default at the platform level: Managed Environment policy that prohibits direct solution import to Production except via the named pipeline; Power Platform DLP that blocks the maintenance connector in Production.
- Add a daily reconciliation report that compares Production deployments against pipeline-run records and alerts on any deployment without a corresponding pipeline run.
- Update the change-management policy to define what an emergency change is, who can authorize one, and what the post-event documentation requirements are.

**Recovery.** Re-validate every affected agent through the standard pipeline. Replace the bypassed deployments with re-validated equivalents. Where re-validation discovers material defects, treat each as a sub-incident under §1.

**Lessons learned.** Gate bypass typically reflects a culture issue more than a technical issue: the maintenance flow existed because the standard pipeline was perceived as too slow. The durable fix is to make the standard pipeline fast and reliable enough that bypass offers no real benefit, *while simultaneously* making bypass technically impossible. One without the other does not work.

**Regulatory reporting decision tree.** Q3 (supervisory failure) is Yes. Q4 (model risk) is Yes. Q2 (records integrity) may be Yes if the bypassed deployments altered records-retention behavior. Q7 (examination) elevates urgency. Legal and CCO own the final call; this is the kind of finding that, if discovered by an examiner before the firm self-discovers and remediates, becomes a meaningfully worse outcome.

**Evidence references.** E-02, E-03, E-07, E-09, E-12, E-13, plus the new daily-reconciliation report artifact.

### Runbook 4 — Adversarial Campaign Reveals New Jailbreak / Prompt-Injection Post-Deployment

**Scenario.** A monthly PyRIT campaign against a deployed Zone-3 financial-services research agent surfaces a previously unknown indirect prompt-injection class: a particular pattern of footnote markup embedded in PDF research notes causes the agent to leak portions of its system prompt and, in two of fifty trials, to follow attacker-controlled instructions to produce non-compliant disclaimers. The pattern was not present in the validation safety battery used at deployment; the agent has been live for two months serving registered representatives.

This is the "the world moved" failure mode: validation was honest at deployment, but the adversarial surface evolved. SR 11-7 anticipates this — model performance and soundness must be monitored continuously, not just at release. FINRA Notice 25-07 explicitly contemplates new attack patterns emerging post-deployment as part of the AI risk landscape.

**Severity classification.** SEV-1 if the new attack class produces customer-facing or supervised-communication-facing output (as in this scenario, since registered representatives are the audience). SEV-2 if the attack succeeds only in lab conditions with no production exposure. The decision rests on whether the attack is reachable from production input channels — in this case, yes, because research PDFs are routinely uploaded by reps.

**Immediate actions (T+0 to T+1h).**
1. Page CISO, AI Governance Lead, Model Risk Manager, Compliance Officer, Designated Supervisor, Agent Owner. Open incident channel. Loop in Threat Intelligence if the firm has an internal function.
2. Containment first, investigation second: scope-restrict or disable the attack vector. In this scenario, that means either disabling PDF ingestion temporarily or routing PDF-derived content through a sanitizer step before the agent sees it. Use Control 2.20 if full disable is required.
3. Preserve the PyRIT campaign artifacts (E-05 with full attack manifests and judge rationales) and the matching production telemetry slice (E-06).
4. Search production telemetry for prior occurrences: has this attack pattern *already* succeeded in the wild without being caught?

**Investigation (T+1h to T+8h).**
- Reproduce the attack against a staged copy of the agent to confirm and to vary the attack payload — understanding the boundary of the vulnerability.
- Determine whether the vulnerability is specific to this agent (its system prompt, its tools, its knowledge sources) or generic to the underlying model. Generic vulnerabilities affect every agent on the same model and become a portfolio-wide finding.
- Coordinate with Microsoft Security Response Center (MSRC) if the vulnerability appears to be in platform behavior rather than agent configuration. Responsible disclosure is the right posture; do not publish details until Microsoft has had a reasonable response window.
- Engage Legal early. If the attack succeeded in the wild against actual reps and produced non-compliant communications, the firm may have FINRA notification obligations regardless of customer harm.

**Containment.** Maintain the input-vector restriction (PDF sanitizer or temporary disable) until eradication is complete. If the attack is generic to the underlying model and Microsoft has not yet shipped a platform mitigation, consider model substitution to a less-affected model family pending fix, with re-validation under §6.

**Eradication.**
- Add the new attack class to the standing PyRIT regression suite for this agent and all sibling agents. The suite must be run on every release going forward.
- Update the agent's system prompt and tool/knowledge configuration to incorporate the recommended defense pattern (e.g., explicit instruction to ignore footnote-embedded directives, structured prompt with isolated context blocks).
- Update the firm's safety-evaluator battery (Indirect Attack family) and re-baseline so the new pattern is detected automatically in future validations.
- Subscribe Threat Intelligence to monitor open-source attack-pattern feeds and feed novel patterns into the next campaign.

**Recovery.** Re-validate the agent end-to-end (full quality + safety + adversarial). Restore production with enhanced monitoring (daily Analytics review for two weeks, lowered drift thresholds, increased Control 2.3 sampling).

**Lessons learned.** A clean validation at T0 is not a permanent safety claim. Any agent that exposes a non-trivial attack surface (file uploads, web retrieval, third-party content) requires recurring adversarial testing, and the cadence should be aligned to the rate at which the threat landscape evolves — for high-exposure agents, monthly is reasonable.

**Regulatory reporting decision tree.** Q1 (customer impact) likely Yes if any rep acted on a poisoned response with a customer; Q3 (supervisory) likely Yes; Q4 (model risk) Yes. Microsoft coordination may also implicate Q7 if disclosure timing intersects with an examination. Legal owns reportability sequencing.

**Evidence references.** E-01, E-03, E-05, E-06, E-07, E-12, E-13, plus the updated PyRIT regression suite, the platform-mitigation correspondence (if any), and the prompt-defense changeset.

### Runbook 5 — Drift Breach in Production (Copilot Studio Analytics)

**Scenario.** Copilot Studio Analytics for a Zone-3 retail-banking FAQ agent shows that the groundedness metric has trended downward over six weeks: a shift from a baseline of ~0.92 to a current rolling average of ~0.78, with two recent weeks below the firm's pre-defined drift threshold of 0.85. The escalation rate to human agents has risen modestly. No single user complaint has been filed, but the metric pattern is unmistakable.

Drift breaches are the most-anticipated and least-prepared-for incident class in production AI agents. Anticipated, because every governance framework warns about them. Least-prepared-for, because by the time they breach, the team has often lost the muscle memory to re-validate quickly.

**Severity classification.** SEV-2 on threshold breach for a Zone-3 agent without confirmed customer harm; SEV-1 if combined with any customer complaint, regulatory inquiry, or analytics evidence of incorrect specific-customer outputs.

**Immediate actions (T+0 to T+1h).**
1. Page Agent Owner, AI Governance Lead, Model Risk Manager, Compliance Officer. Open incident channel.
2. Capture E-06 (full Analytics export over the breach window plus the prior baseline window) and E-04 (last validated evidence pack with the original baseline conditions).
3. Pull a sample of low-groundedness conversations from the breach window for human review (Control 2.3 reviewers are appropriate). The goal is not to close the incident on the basis of the sample, but to understand whether the metric is reflecting real degradation or evaluator drift.
4. Determine whether anything changed *in the agent* during the breach window: prompt edit, knowledge-source content change, tool change, model version change. Cross-check against pipeline run history (E-09).

**Investigation (T+1h to T+8h).**
- Decompose the drift: is it the input distribution that changed (more novel questions), the knowledge source that changed (content updates that the agent is now mis-grounding against), or the model that changed (a platform-side update)?
- For input-distribution shifts: this is a real signal that the agent's scope no longer matches its design. Either expand scope through a controlled re-design and re-validation, or narrow scope by routing out-of-scope questions to humans.
- For knowledge-source shifts: re-index, update the agent's retrieval configuration, and re-validate against a refreshed holdout.
- For model-side shifts: this is a hidden model swap from the firm's perspective and triggers Runbook 6.
- Engage Compliance to assess whether the drift produced any customer-facing communications that, in retrospect, would not have met disclosure or accuracy standards. Pull conversation transcripts as needed under Control 1.7 retention.

**Containment.** While investigation proceeds, lower the drift alert threshold further so any continued degradation is caught earlier; increase Control 2.3 human review sampling rate; if the drift is severe (for this scenario, sustained below 0.75 would qualify), scope-restrict or disable the agent per Control 2.20.

**Eradication.** Address the root cause identified in investigation. Re-validate against a fresh holdout that reflects the *current* input distribution, not the deployment-vintage distribution. Update the baseline for the drift metric and document the re-baseline approval (MRM concurrence required).

**Recovery.** Promote the corrected agent through the standard pipeline. Maintain enhanced monitoring for at least two weeks post-restoration. Schedule a structural review of monitoring cadence — if the breach was not caught within the firm's tolerance window, the cadence is wrong.

**Lessons learned.** Drift baselines should be recomputed on a regular cycle (typically quarterly) rather than treated as set-at-deployment forever. The goal is not to chase the metric but to keep the threshold meaningful as the world evolves. A drift breach that surprises the team months after deployment is a monitoring-cadence failure as much as an agent failure.

**Regulatory reporting decision tree.** Q1 depends on the customer-impact assessment from investigation. Q3 (supervisory) is Yes if the drift produced supervised communications that fell below standards. Q4 (model risk) is Yes by definition for a Zone-3 drift breach. Q5 (privacy) is rarely implicated by groundedness drift specifically but should be checked.

**Evidence references.** E-04, E-06, E-09, E-12, plus the re-baseline documentation and the Control 2.3 sample-review record.

### Runbook 6 — Model Swap Regression (A/B Challenger Degradation)

**Scenario.** The firm's platform team migrates a Zone-3 Copilot Studio agent from one underlying model to a successor model that Microsoft has positioned as a drop-in upgrade. The migration is treated as a configuration change. Within ten days, two business units report degraded behavior: more verbose responses, occasional refusals on previously-handled queries, and one near-miss where the agent provided generic guidance where the prior model would have escalated to a human. No formal A/B challenger evaluation was run; the prior model is no longer easy to revert to because the platform team has decommissioned the prior deployment.

Model swap is the single most under-appreciated change-management category in M365 AI agent governance. From a pure-config perspective it is one click. From an SR 11-7 perspective it is a re-validation trigger and arguably a re-approval trigger, because the model is the most material component of the agent.

**Severity classification.** SEV-1 if the swap targeted Production / Zone-3 and re-validation was not performed (this scenario). SEV-2 if the swap targeted Zone-2 or if a partial re-validation was performed but did not meet the firm's full threshold.

**Immediate actions (T+0 to T+1h).**
1. Page AI Governance Lead, Model Risk Manager, Compliance Officer, CISO, Agent Owner, Platform Engineering Lead. Open incident channel.
2. Determine whether the prior model is still deployable (in any region/cloud) for rollback. If yes, prepare the rollback artifact even before deciding to use it.
3. Capture E-02, E-03 (current and prior model identities and versions), E-04 (last validation pack — which was for the prior model), E-06 (production telemetry covering the swap window).
4. Pull the change record that authorized the swap. Identify the approver and the framing — was it labeled "configuration change" or "model change"? The framing is itself part of the finding.

**Investigation (T+1h to T+8h).**
- Quantify the regression: re-run the most recent validation evaluation against the *current* (new-model) deployment and compare scores to the validated (prior-model) baseline. Material movement on any quality, safety, or escalation evaluator is a regression signal.
- Inventory other agents that share the same underlying model. A model swap that went unannounced for one agent likely went unannounced for many — search the platform.
- Determine whether Microsoft itself swapped the model under the agent (a *silent* model update from the platform) or whether the firm performed the swap. The former is a vendor-management finding (Control 2.4) in addition to a Control 2.5 finding.

**Containment.** If rollback is still feasible, roll back to the prior validated model under enhanced monitoring while re-validating the new model properly. If rollback is not feasible (the prior model is decommissioned by the vendor), scope-restrict the agent to lower-risk use cases until re-validation is complete, or disable per Control 2.20 if the regression is severe.

**Eradication.**
- Update Control 2.5 procedures to define model identity and version explicitly as a *material change* requiring full re-validation, with no "configuration change" path available for it. Encode this as a pipeline gate: any solution promotion whose model identity differs from the prior promotion must invoke the full evaluation suite, not the delta suite.
- Subscribe to Microsoft model deprecation and update notifications and route them through Change Management with a defined SLA for re-validation.
- Update the change-record taxonomy to make "model change" a first-class category, not a sub-type of "configuration change."

**Recovery.** Complete the proper re-validation of the new model. If it passes, deploy with enhanced monitoring and an updated evidence pack. If it fails, retain the rollback (or substitute another model that does pass).

**Lessons learned.** The vendor's framing of a model upgrade is the vendor's framing. The firm's framing must be governed by SR 11-7 and the firm's own MRM policy. Conflating those framings — letting the vendor's "drop-in" language lower the firm's bar — is the recurring mistake.

**Regulatory reporting decision tree.** Q3 (supervisory) is typically Yes. Q4 (model risk) is Yes by definition. Q1 depends on whether the regression produced customer-facing harm. Q7 elevates urgency if any examination touches model-risk practices.

**Evidence references.** E-02, E-03, E-04, E-06, E-09, E-12, plus the change record, the rollback artifact (if used), and the post-swap re-validation evidence pack.

### Runbook 7 — Evaluator Family Unavailable in Target Sovereign Cloud

**Scenario.** A line of business in the firm's GCC-High tenant requests deployment of a Zone-3 agent that, in its commercial-cloud equivalent, was validated using the full Azure AI Evaluation safety battery — including Indirect Attack and Code Vulnerability evaluators. On preparing the GCC-High deployment, the platform team discovers that two of the required evaluator families are not yet generally available in GCC-High. The judge model used by the PyRIT scorer chain is similarly unavailable. The business sponsor asks whether the agent can deploy "with what evaluators are available."

This is the recurring sovereign-cloud parity dilemma. The temptation is to call the gap a vendor problem and move forward; the correct posture is to treat the gap as the firm's problem to govern, with explicit compensating controls.

**Severity classification.** Pre-deployment, this is not yet an incident — it is a control design decision. It becomes SEV-2 if the agent is deployed without compensating controls and the gap is later discovered by audit, and SEV-1 if the missing evaluators were the ones that would have caught a now-confirmed defect.

**Immediate actions (T+0 to T+1h).** (When discovered as a pending deployment decision rather than as a post-deployment finding.)
1. AI Governance Lead and Model Risk Manager convene with the Agent Owner. Compliance Officer participates.
2. Pull the Microsoft Learn parity matrix as of the date of the discussion and capture it as evidence (a screenshot with URL and timestamp). Parity matrices change.
3. Map the missing evaluators to specific risks: Indirect Attack maps to a defined adversarial risk class; Code Vulnerability maps to a defined code-execution risk class. The mapping determines which compensating controls are credible.

**Investigation (T+1h to T+8h).**
- For each missing evaluator, identify the substitute compensating control(s) from §1.4. The credible substitutes are: human review (Control 2.3) at a defined sampling rate; constrained agent capability (e.g., disable the tools that depend on Code Vulnerability assurance); zone restriction (do not promote to Zone-3 in GCC-High; keep at Zone-2); enhanced monitoring (lowered drift thresholds, daily Analytics review).
- Quantify the substitution: a human reviewer at 100% sampling is a credible substitute for an automated safety evaluator at scale only if the response volume is low. If volume is high, 100% review is infeasible and the only credible compensating control is scope/zone restriction.
- Document the *expiration* of each compensating control. The substitute is in place *until* the missing evaluator is generally available in GCC-High and has been validated in the firm's environment. There must be a date or a tracked event that triggers exit, otherwise the compensating control becomes permanent and the gap drifts into normal.

**Containment.** None — this is a pre-deployment decision. If the conversation is happening *because* an agent is already deployed without these controls, treat as a SEV-2 finding under §3 Runbook 1's posture and re-validate or scope-restrict immediately.

**Eradication.** This is the wrong word for this runbook — the gap is not a defect, it is a vendor-availability constraint. The action is to *govern* the gap.
- Establish the compensating-control package: documented substitution mapping, owner, expiration trigger, MRM and Compliance approver, evidence-collection process.
- Track Microsoft's roadmap for the missing evaluators in GCC-High (and DoD as applicable) on a quarterly cycle. Move the expiration trigger forward as roadmap dates firm up.
- When the missing evaluator becomes generally available, run the firm's own validation against it before lifting the compensating control; do not assume parity at the day of GA.

**Recovery.** If the agent was deployed with proper compensating controls, recovery is the lifecycle moment when the missing evaluator is GA and the compensating control is retired. Re-validate end-to-end with the now-available evaluator and update the evidence pack.

**Lessons learned.** Sovereign-cloud parity gaps are a permanent feature of the FSI landscape, not a transient one. Firms that build a repeatable compensating-control framework once can apply it across many controls and many gaps; firms that improvise each time accumulate undocumented exceptions that compound.

**Regulatory reporting decision tree.** Pre-deployment with proper compensating controls, no reporting is implicated. Post-deployment without compensating controls, Q3 and Q4 are typically Yes; Q7 elevates urgency materially if a sovereign-cloud customer is also a federal agency that may itself audit the firm's controls.

**Evidence references.** Parity matrix snapshot (date/URL), compensating-control approval (MRM + Compliance), evaluator-availability tracker, E-04, E-11.

### Runbook 8 — Validation Evidence Pack Tamper Detected (Hash / Signature Break)

**Scenario.** During an examination, the firm runs an integrity check across its evidence repository for Control 2.5 packs covering the prior eighteen months. Three packs return hash mismatches relative to the hashes recorded at sign-off. One pack contains a signed PDF whose signature no longer validates. None of the affected agents have been retired; all are live in Production.

Evidence integrity is the bedrock of every regulatory framework that touches the firm — SEC 17a-4(b)(4) for records, SR 11-7 for model documentation, SOX 404 for ICFR. An evidence pack whose contents do not match the recorded hash, or whose digital signature no longer validates, is *as if it did not exist* from a regulator's perspective. The firm cannot prove what was approved.

**Severity classification.** SEV-1 by default. The presumption is that integrity is broken until the firm can demonstrate either (a) a benign cause (e.g., re-encoding by a storage-tier migration that preserved logical content) or (b) a malicious or negligent cause requiring investigation.

**Immediate actions (T+0 to T+1h).**
1. Page CISO, AI Governance Lead, Model Risk Manager, Compliance Officer, Records Manager, Internal Audit, and Legal. Open incident channel. Treat as a potential records-integrity incident with regulatory implications from minute one.
2. Quarantine all three affected packs (and the signed PDF) — do not delete, do not amend. Take read-only snapshots for forensic preservation.
3. Capture the storage-account access logs for the affected objects across the entire window from sign-off to discovery (not just the recent window). Look for any write events.
4. Identify every agent and every approval that referenced the affected packs.

**Investigation (T+1h to T+8h).**
- Reconstruct the lifecycle of each affected pack: storage-account history, retention-label changes, access-control changes, any migrations, any tooling that touched the bytes.
- Differentiate cause categories:
  - *Benign re-encoding*: a storage migration changed encoding but preserved logical content. Verifiable by reconstructing the original content from logical fields and re-hashing under both encodings.
  - *Configuration drift*: the hash was computed against an early draft and the final pack was substituted without re-hashing. This is a process failure, not malice, but it is still an integrity gap.
  - *Negligent overwrite*: someone with write access edited the pack post-sign-off without preserving the original. This is a control failure.
  - *Malicious tampering*: someone deliberately altered the pack to misrepresent what was approved. This is a discrete forensic incident with potentially criminal implications. Legal owns the response.
- For the signature break: validate the certificate chain; check whether the signing certificate was revoked; check whether the document was re-saved by software that does not preserve detached signatures.
- Engage Internal Audit and Legal continuously through the investigation. Decisions about external disclosure to examiners must be Legal-led.

**Containment.**
- Lock down write access to the evidence repository. Move to write-once-read-many (WORM) storage if not already; enforce Purview retention labels with disposition review.
- Halt all evidence-pack modifications across the firm until the cause is understood and the control is re-baselined.
- For the agents whose validation evidence is in question, decide whether to maintain in production under enhanced monitoring or to take offline pending re-validation. Default toward offline if the integrity break could plausibly mask validation defects.

**Eradication.**
- Implement WORM/immutable storage for all evidence packs at sign-off. The pack hash recorded at sign-off should be against the immutable copy.
- Implement automated periodic integrity checks (weekly) across the entire evidence repository, not just at examination time. The point of the check is to surface integrity breaks within days, not months.
- For the signed-PDF case, move to a signature format and storage tier that survives platform migrations; consider blockchain-anchored timestamping for high-value packs.
- Update the evidence-pack template to include the immutable-storage URI, the hash algorithm, and the recorded hash as fields visible to the approver at sign-off.

**Recovery.** Re-validate any agent whose evidence integrity could not be re-established to a sufficient standard. For agents where logical content was demonstrably preserved (benign re-encoding), document the determination and the technical proof; this becomes part of the evidence pack going forward.

**Lessons learned.** Evidence integrity is most often broken by routine IT operations — a storage migration, a tool upgrade, a permissions cleanup — performed without awareness that the affected files are evidence. The fix is to treat the evidence repository as a regulated records system from day one, with all the controls (immutability, integrity checking, change management) that implies.

**Regulatory reporting decision tree.** Q2 (records integrity) is Yes by definition. Q3 (supervisory) is Yes — the WSPs failed to ensure evidence integrity. Q4 (model risk) is Yes for any affected model-classified agent. Q7 (examination) is the worst-case combination — if discovery happens during an examination, the path through Legal is non-negotiable and the firm's posture is materially better the more proactively it has been monitoring integrity.

**Evidence references.** E-04 (the affected packs, quarantined originals plus snapshot), storage-account access logs, integrity-check tooling output, signing-certificate validation reports, and the post-incident immutable-storage configuration.

### Runbook 9 — Examiner / External Auditor Request for Testing Evidence

**Scenario.** A FINRA examiner sends a written request to the firm asking for: (a) the inventory of AI-enabled supervised-communications tools in production, (b) the testing and validation evidence for two specific named agents, including pre-deployment evaluation results and post-deployment monitoring outputs, (c) the supervisory procedures governing those tools, and (d) any incidents involving those tools in the prior twelve months. Response is requested within ten business days.

This is not a technical incident in the conventional sense, but it is the moment when every Control 2.5 investment either pays off or fails to pay off. The runbook is included here because the patterns of *how* evidence is assembled, transmitted, and characterized to an examiner are themselves governed and themselves a source of supervisory exposure.

**Severity classification.** Treat as SEV-2 by default for resourcing and attention; escalate to SEV-1 if the request includes any indication of a specific concern (a customer complaint, a market-conduct lead, a referral from another regulator) or if the firm's preliminary self-assessment surfaces a material gap in the evidence sought.

**Immediate actions (T+0 to T+1h).** (Of receipt, not of incident detection — this is the regulatory-response mode.)
1. Legal and CCO own the response. AI Governance Lead, Model Risk Manager, Records Manager, and Internal Audit support. The examiner is the audience; Legal is the voice.
2. Acknowledge receipt within the timeframe specified by the examiner (often 24 hours).
3. Open a discrete examination response workspace with retention preserved. Every artifact gathered or generated for the response is itself a record subject to preservation.
4. Pull the Control 2.5 evidence inventory for the two named agents and for all incidents in the prior twelve months. This is the dry run — what *would* the firm produce today, before any polishing?

**Investigation (T+1h to T+8h, then continuous).** This is reverse investigation: the firm is investigating its own posture as the examiner will see it.
- For each named agent: assemble the evidence pack (E-04), the production telemetry (E-06), the audit logs (E-07), the pipeline history (E-09), the Solution Checker reports (E-10), and the incident records (E-12, E-13) for any incidents in scope.
- Verify integrity per Runbook 8 patterns. If integrity is in question, that is a discrete crisis requiring Legal decision-making about disclosure.
- Identify and document gaps. A gap acknowledged proactively is materially better than a gap discovered by the examiner. Legal owns the framing.
- Assemble the supervisory-procedure documentation (WSPs) for the AI tools and confirm the WSPs were in effect during the period in question. WSP changes mid-period must be disclosed.
- Build the inventory: every AI-enabled tool in production, the business it serves, its zone, its model, its evaluator history, its incident history. The inventory should be defensible — a registered representative receiving an answer from the firm should appear in the inventory if AI participated in producing it.

**Containment.** Within the examination response: do not produce evidence beyond what was requested unless Legal directs (over-production carries its own risks). Do not destroy or modify any record in scope; preservation hold is in effect from the moment of receipt.

**Eradication.** Not applicable — this is a regulatory response, not a defect. The closest equivalent is *gap closure*: any deficiency surfaced during preparation that is also fixable during the response window should be addressed and documented, with timing made transparent to the examiner per Legal's framing.

**Recovery.** Submit the response within the window. Post-submission, conduct a structured retrospective: what was easy to assemble, what was hard, what was missing, what would the firm change in its everyday Control 2.5 practice to make the next request faster and cleaner? The retrospective is itself feedback into the framework.

**Lessons learned.** A firm that can assemble the response to a typical examiner request in two business days from a single evidence repository, without scrambling, is operating Control 2.5 well. A firm that needs ten business days and finds gaps mid-assembly is operating Control 2.5 well-enough-to-pass-but-not-well. The gap between those two states is the maturity arc this framework supports.

**Regulatory reporting decision tree.** The examination *is* the reporting context. Q7 is Yes by definition. The remaining questions are framing for Legal: what does the firm need to disclose proactively within the examination, and what does it need to surface only if asked? Those are Legal calls, not engineering calls.

**Evidence references.** E-02, E-03, E-04, E-06, E-07, E-09, E-10, E-11, E-12, E-13 for each in-scope agent and incident, plus the WSPs, the inventory, and the response cover letter.

---

## §4 — Evidence Preservation Standards

Evidence preservation is the connective tissue between Control 2.5 (testing and validation) and Controls 1.6 (incident response), 1.7 (audit logging), and 1.21 (records retention). The standards below codify what must be preserved, how, for how long, and under what controls.

**What.** The evidence floor (§1.3 E-01..E-13) for every SEV-1 and SEV-2 incident; the evidence packs underlying every Zone-3 deployment decision; the periodic monitoring outputs that document continued conformance after deployment; the change records authorizing every promotion; the access-control records demonstrating segregation-of-duties; the parity-matrix snapshots and compensating-control approvals for sovereign-cloud gaps.

**How.** Capture artifacts in their native format (CSV, JSON, PDF, screenshots) with metadata: source system, query or export command used, timestamp in UTC, capturing identity, hash (SHA-256 or stronger). Store in immutable storage with Purview retention labels. Sign-off artifacts (evidence packs, attestations) should be digitally signed where possible and the signature itself preserved with the document.

**How long.** Align to SEC 17a-4(b)(4) and FINRA 4511 for any artifact that constitutes a books-and-records record (typically six years, with the first two years easily accessible). Align to SR 11-7 / OCC 2011-12 model-risk documentation expectations (often longer; firm-specific MRM policy governs). Align to GLBA 501(b) for any artifact containing NPI. The longest applicable retention governs.

**Under what controls.** Write-once-read-many (WORM) where supported. Periodic integrity checks (weekly minimum) per Runbook 8 lessons. Access controls scoped to the smallest necessary group, with all access logged. Disposition reviews before any retention-period-driven deletion, with sign-off recorded.

**Common failure modes.**
- Evidence stored in a developer's OneDrive instead of the governed evidence repository.
- Evidence stored without hashing, so integrity cannot later be demonstrated.
- Evidence stored with the wrong retention label, leading to premature deletion.
- Evidence stored in commercial cloud while the agent operates in GCC-High, creating data-residency exposure.
- Evidence captured at sign-off but never integrity-checked again until an examiner asks.

Each of these failure modes is itself a Control 2.5 finding when surfaced.

---

## §5 — Communication & Escalation Patterns

Section §1.6 defined the communication ladder. This section expands on the *patterns* that recur across incidents and where firms most often stumble.

**Pattern A — The reporting clock starts at detection, not at confirmation.** The most common mistake in escalation is to delay the page until "we know what we have." For SEV-1 and SEV-2 candidates the right posture is to page early on the *suspicion* and downgrade if the suspicion is not confirmed, rather than to wait for confirmation and lose the first hour. SR 11-7 and FINRA 3110 evaluators are unsympathetic to firms that delayed escalation in order to clean up the story.

**Pattern B — Engineering does not communicate outward.** Customer communications, regulatory communications, and external counsel communications are owned by Legal and Compliance, not by the engineering team that surfaced the incident. Engineers communicate inward (to Legal, Compliance, MRM) and provide factual material; the outbound voice is owned upstream. Mixing these channels creates legal exposure.

**Pattern C — One source of truth per incident.** The incident commander maintains the canonical timeline (E-01) and all updates flow through it. Side conversations in DMs, side-emails, and ad-hoc spreadsheets fragment the record and create discoverability complications. Discipline here pays off in the PIR (§7) and in any subsequent regulatory response.

**Pattern D — Regulator communication is a one-way valve.** Once a regulator is notified, the firm cannot un-notify. The decision to notify is therefore a Legal-and-CCO decision, not a CISO decision and not an AI Governance Lead decision. The decision *not* to notify, when reportability could plausibly apply, is also a Legal decision and is itself a finding documented in the PIR with the reasoning.

**Pattern E — Internal communications are also evidence.** Slack/Teams messages, emails, and tickets generated during an incident may all be discoverable in subsequent litigation or examination. Communicate factually; avoid speculation, blame language, and informal severity assertions ("this is a disaster") that may be pulled out of context later. The standard is the same as for any potentially-discoverable communication.

---

## §6 — Recovery & Re-Validation

Recovery from a Control 2.5 incident is not "the agent is back online." Recovery is the lifecycle return to a state where the firm can credibly attest, with evidence, that the agent meets its quality, safety, and supervisory thresholds. The components:

**Re-validation triggers.** Any of the following requires re-validation at the appropriate plane(s):
- Model swap (Runbook 6) — full re-validation across all five planes.
- System prompt change beyond cosmetic — at minimum quality and safety planes.
- Knowledge source addition, removal, or material content refresh — quality plane plus targeted safety re-test of the new content.
- Tool/connector change affecting agent capability — full safety plane plus targeted quality.
- New attack class identified (Runbook 4) — adversarial plane re-baseline; quality re-spot-check.
- Drift breach (Runbook 5) — re-baseline plus targeted quality re-validation.
- Sovereign-cloud expansion — full re-validation in the new cloud against any compensating controls.
- Examination-driven gap closure (Runbook 9) — targeted to the gap, with documentation visible to the examiner.

**Re-validation depth.** Match the depth to the trigger. A new attack class does not necessarily require re-running the full quality battery if the change to the agent is purely defensive prompt-hardening. Conversely, a model swap requires full re-validation — partial does not suffice.

**Re-baseline of monitoring.** After recovery, baselines for drift detection should be recomputed against the post-incident state. Pre-incident baselines no longer reflect the agent's current behavior and would generate spurious alerts (or worse, mask real ones).

**Phased restoration.** For agents that were taken fully offline, restore in stages: Zone-2 internal pilot first, then Zone-3 with enhanced monitoring for at least two weeks, then standard monitoring cadence. Sudden full restoration after a SEV-1 is a missed opportunity to catch any residual issue.

**Sign-off.** Recovery is complete only when the new evidence pack is signed off by an *independent* validator (Runbook 2 lessons) and approved per the standard pipeline (Runbook 3 lessons). Bypassing either step invalidates the recovery.

---

## §7 — Post-Incident Review (PIR) Template

Every SEV-1 and SEV-2 incident concludes with a written PIR delivered within 30 days. The template below is the minimum content; firms may extend.

1. **Incident summary.** One paragraph: what happened, when, scope of impact (customer, supervisory, records, privacy), severity, and current status.
2. **Timeline.** Minute-level UTC timeline from detection through recovery. Includes detection method (who/what surfaced the issue), each escalation event, each containment action, each communication, and the recovery milestone.
3. **Root cause analysis.** A "five whys"–depth analysis. Avoid stopping at proximate cause. The root cause of a holdout leak is rarely "a developer reused a row"; it is usually "the corpus-segregation control did not exist as a platform-enforced gate."
4. **What worked.** Genuine credit for what the response did well. The PIR is not only a critique; recognizing what worked reinforces it.
5. **What did not work.** Honest accounting of what was slow, missed, or wrong. Frame factually, not personally.
6. **Reportability outcome.** Walk §1.2 explicitly. Document each Q with Yes/No and the rationale, and identify any external notifications made or considered. "No reportability" is itself a documented determination, not an absence.
7. **Remediation actions.** Each action: owner, due date, success criterion, evidence-of-completion artifact. Tracked to closure with a defined cadence.
8. **Control changes.** Any updates to Control 2.5 procedures, evidence-pack templates, pipeline gates, monitoring cadences, or governance roles flowing from the incident. The PIR is the canonical mechanism for the framework to learn.
9. **Re-validation status.** What was re-validated, against what evidence, signed by whom, on what date.
10. **Sign-off.** AI Governance Lead, Model Risk Manager, Compliance Officer (and Designated Supervisor where applicable) sign the PIR. The signed PIR becomes part of the agent's permanent record (E-04 successor).

Distribute the PIR to the Operational Risk Committee for SEV-1; to the AI Governance Council for SEV-2; and surface remediation tracking in the standing risk-committee dashboard.

---

## §8 — Anti-Patterns & Common Mistakes

A non-exhaustive list of anti-patterns observed in Control 2.5 implementations across FSI firms. Each is paired with the failure mode it produces.

1. **"The Test Pane works, ship it."** Treating developer-plane smoke tests as evidence of validation. Skips the four other evaluation planes. Produces Runbook 1 and Runbook 6 patterns at scale.
2. **"We'll add the holdout next sprint."** Validating on the same data the agent was tuned on, with the intent to circle back later. Holdout debt is the most expensive technical debt in AI; it always comes due during the next examination.
3. **"The model swap is just a config change."** Categorical mis-labeling. Produces Runbook 6.
4. **"The validator is the same person as the author because we're a small team."** Convenience SoD violation. Produces Runbook 2. The fix is platform enforcement, not policy memos.
5. **"Solution Checker findings are mostly false positives."** Bulk-suppression mindset. Produces real defects reaching production hidden in the suppression noise.
6. **"We'll page when we know what we have."** Delayed escalation. Produces compounding regulatory exposure under SR 11-7 and FINRA 3110 and weakens the PIR record.
7. **"Engineering can update the customer."** Channel confusion. Produces Legal exposure. Reserve outbound communication to Legal/Compliance/Communications.
8. **"The evidence is in someone's OneDrive, we'll consolidate later."** Evidence-repository drift. Produces Runbook 8 conditions and examination-response chaos (Runbook 9).
9. **"GCC-High doesn't have that evaluator yet, we'll just deploy without it."** Uncovered sovereign-cloud parity gap. Produces Runbook 7 in its worst form.
10. **"Drift alerts are noisy, we lowered them."** Silencing rather than understanding the signal. Produces Runbook 5 in its delayed form.
11. **"PyRIT isn't applicable to our agent."** Adversarial-testing avoidance. Produces Runbook 4 patterns.
12. **"That incident wasn't reportable, no PIR needed."** Skipping the PIR for incidents the team determined were not externally reportable. Loses the institutional learning and weakens the firm's ability to demonstrate continuous improvement during the next examination.

---

## Cross-References

- [`../../incident-and-risk/ai-incident-response-playbook.md`](../../incident-and-risk/ai-incident-response-playbook.md) — Firm-wide AI incident response procedures
- [`../1.6/troubleshooting.md`](../1.6/troubleshooting.md) — Purview DSPM for AI troubleshooting (paired data-protection lens on incidents)
- [`../1.7/troubleshooting.md`](../1.7/troubleshooting.md) — Audit logging troubleshooting (evidence-source operational guidance)
- [`../1.19/troubleshooting.md`](../1.19/troubleshooting.md) — DLP and content-protection troubleshooting
- [`../1.21/troubleshooting.md`](../1.21/troubleshooting.md) — Records retention and disposition troubleshooting
- [`../2.1/troubleshooting.md`](../2.1/troubleshooting.md) — Agent inventory and lifecycle governance troubleshooting
- [`../2.3/troubleshooting.md`](../2.3/troubleshooting.md) — Human-in-the-loop and 4-eyes review troubleshooting
- [`../2.20/troubleshooting.md`](../2.20/troubleshooting.md) — Agent disable and decommissioning troubleshooting
- [`../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) — Control 2.5 specification

---

*Updated: April 2026 | Version: v1.4 | Maintained by: AI Governance Team*







