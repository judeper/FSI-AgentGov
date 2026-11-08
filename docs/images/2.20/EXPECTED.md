# Control 2.20: Adversarial Testing and Red Team Framework - Screenshot Specifications

**Specification reviewed:** 2026-11-06 (documentation alignment only; no tenant UI or screenshot verification)

This checklist specifies evidence to collect during authorized testing. It does not attest that testing, configuration, licensing, screenshots, or a release gate have been verified. Follow the [portal walkthrough](../../playbooks/control-implementations/2.20/portal-walkthrough.md) and [verification criteria](../../playbooks/control-implementations/2.20/verification-testing.md); the [PowerShell examples](../../playbooks/control-implementations/2.20/powershell-setup.md) are incomplete firm-owned patterns, not shipped automation.

## Required Screenshots

### Screenshot 1: Red Team Program Documentation
**What to capture:**
- Red team rules of engagement document
- Designated team members and roles
- Scope definition and testing schedule (monthly for Zone 3, with pre-deployment testing for each release)
- Authorization, prohibited production-data targeting, and approved isolated synthetic test surfaces

### Screenshot 2: Attack Library Coverage
**What to capture:**
- Curated test case library covering OWASP LLM Top 10 (2025) categories
- MITRE ATLAS technique mapping
- Test case categorization (prompt injection, jailbreaking, manipulation)

### Screenshot 3: Golden Dataset Validation Results
**What to capture:**
- Golden dataset with domain-specific Q&A pairs (minimum 100 per Zone 3 agent)
- Approved dataset version, tagged commit, refresh date, and synthetic-data review
- Validation results showing agent accuracy metrics
- Comparison against baseline accuracy thresholds

### Screenshot 4: CI/CD Pipeline Adversarial Testing
**What to capture:**
- Automated adversarial testing stage in deployment pipeline
- Test execution results with pass/fail indicators per attack category
- Recorded zone policy: Zone 1 at least 80% defense rate (the repository's owner-approved documented acceptance gate, not a Microsoft or regulatory value; record the firm's actual adopted value); Zone 2 at least 90% defense rate with regression blocking; Zone 3 at least 95% overall and 98% for Critical/High families
- Negative-path results showing that empty/skipped suites, adapter/probe errors, unscored/`REVIEW` results, missing required evidence, and enforced threshold/family breaches cannot produce a passing release
- Actual firm implementation and run identifiers; an illustrative script or pipeline screenshot alone is not evidence that the gate works

### Screenshot 5: Remediation Tracking Dashboard
**What to capture:**
- Vulnerability remediation tracking with SLA compliance (Critical: 24h, High: 7d, Medium: 30d)
- Open vs. resolved vulnerability counts
- SLA breach indicators and escalation status

### Screenshot 6: Test Identity, Licensing, and Isolation
**What to capture:**
- Authorized test identities, assigned licenses/meters, and least-privileged roles for the tested experience; redact personal identifiers and never capture credentials
- Power Platform Admin provisioning evidence and applicable Dataverse solution privileges (at least System Customizer); applicable Foundry User role and PIM eligibility/activation evidence
- Sandbox type, region, Dataverse, access group, effective DLP/audit scope, and production-configuration comparison; record privileged/application-user exceptions and other isolation limits
- Synthetic grounding data and tool/flow destinations; a sampled Data Map scan alone does not establish synthetic-only content
- For Microsoft 365 Copilot, the separately isolated test tenant/content boundary rather than an assumed Power Platform sandbox boundary; record Chat API preview, license, delegated-permission, and unsupported-skill limitations where used

### Screenshot 7: Solution Transport and Configuration Differences
**What to capture:**
- Approved unmanaged source solution, transported package type/version, required components, and import results; do not export an installed managed production solution
- Authentication reconfiguration, connection references, environment variables, tools/flows, grounding sources, and channel/audience restrictions reviewed before publication or invocation
- Replacement of production destinations with synthetic sandbox equivalents; omitted/nontransported components and remaining differences from the approved production snapshot
- For Foundry-backed agents, deployment/model/version and applicable policy/configuration identifiers, test-resource recreation, and recorded differences; do not assume a portal export or exact clone

### Screenshot 8: Assigned Guardrails and Actual Outcomes
**What to capture:**
- Applicable Foundry **Build → Guardrails** configuration or classic content-filter/RAI-policy surface, with deployment/agent assignment identifiers
- User prompt/document attack settings and supported intervention points; distinguish configured detection from blocking
- Representative benign/attack outcomes with raw `detected` and `filtered` annotations; standalone Content Safety detection is not proof of application blocking
- For surfaces without that Foundry policy, the applicable agent instructions/tools/authentication/grounding baseline and explicitly unsupported controls

### Screenshot 9: Correlated Agent Replies
**What to capture:**
- Benign canary prompt, actual bot/model reply, expected answer, run/activity identifiers, timestamps, and latency
- For Direct Line, the bot reply received through GET/WebSocket and watermark/correlation evidence, not the POST activity acknowledgement or user echo
- Missing, timed-out, stubbed, or uncorrelated replies recorded as incomplete/failed evidence, not a defense pass

### Screenshot 10: Evaluation, Telemetry, and Evidence Completeness
**What to capture:**
- Supported evaluation target/region, evaluator names/versions, input/output mappings, raw results, and run status; preview/unsupported families and Partial/Failed evaluations are not passing cross-validation
- Applicable Prompt Shields, Defender/Agent 365, Communication Compliance, and audit onboarding/policy/billing scope, with supported workload records and raw available identifiers
- Workload-specific correlation confidence, event/ingestion times, and measured processing windows; no universal ConversationId/AgentId join or per-probe alert is assumed
- Explicit unsupported/not-applicable, pending-ingestion, collection-error, and detection-gap classifications with reasons/owners; absent telemetry is not a clean pass
- Required artifact inventory and SHA-256 manifest with recomputed source/destination file hashes; missing artifacts or matching manifests without destination-byte verification are not complete evidence

---

## Notes for Verification
- This control is primarily process-based; screenshots demonstrate testing program and results
- Capture pre-deployment and scheduled test evidence from authorized isolated synthetic test surfaces; do not use production customer data
- Store screenshots and raw exports locally under `maintainers-local\tenant-evidence\`; do not commit screenshots, customer data, or credentials
- Pair screenshots with the applicable machine-readable configuration, response, evaluation, telemetry, and hash records; screenshots alone do not establish runtime success
- Record unavailable screenshots and unsupported/incomplete evidence explicitly; a documentation review must not renew the historical tenant UI verification date
- Ensure test results and vulnerability details are representative but not exploitable
- Include timestamps to demonstrate currency
- Test evidence must be preserved per retention requirements (7+ years)

**Unresolved retention inconsistency:** The existing retention wording above is preserved unchanged. It differs from other control guidance and requires the firm's legal/records-retention owner to review; this specification does not establish a replacement retention period.
