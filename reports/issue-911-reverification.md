# judeper/OceanSquad#911 — Linus documentation verification handoff

**Date:** 2026-11-06  
**Worktree:** `C:\dev\FSI-AgentGov-wt-911`  
**Branch:** `ocean/issue-911`  
**Capability:** Linus, documentation implementation specialist, delegated by Saul  
**Status:** Source editing and affected generator work complete; parent owns final build, site consumers, smoke runtime, review and local commit.

## 1. Outcome and non-negotiable boundaries

The April UI marker was stale, but the problem was not merely a date. The walkthrough overstated isolation, export/cloning, programmatic coverage, guardrail behavior and telemetry guarantees. Correcting the date without correcting those claims would have renewed misleading assurance.

The walkthrough now records:

> **Last Verified:** 2026-11-06 (Microsoft Learn documentation review; not tenant UI verification)

Its historical **Last UI Verified: April 2026** remains historical. No tenant UI actions, screenshots, probes, API authentication, license assignments, model deployments or runtime release gates were verified.

The user's exact controlling constraints were:

- “Never run gh, GitHub API writes, git push/send-pack, remote branch mutations, or any issue/PR actions.”
- “Do NOT commit; parent reviews/validates and creates local commit.”
- “Do not change branches. Do not launch other agents.”
- “DO NOT rely on memory or mark UI screenshot verified without actual tenant evidence.”
- “preserve ALL regulatory/compliance language/mappings without rejudging it.”
- “Never hand-edit generated outputs.”
- “do not run full build/suite in parallel with parent.”

All those boundaries were maintained. Microsoft Learn tools were discovered with `api_tool.list_resources` before live `microsoft_docs_search` and `microsoft_docs_fetch` use. Primary-source checks included new/classic experience differences. No release-comms lookup was needed: current Microsoft Learn sources directly resolved the relevant technical questions. Two initially guessed Learn paths failed retrieval; they were replaced by documented paths, not treated as evidence. No email, credentials or customer evidence was accessed.

**Final Linus tracked footprint after authorized completion follow-ups:** 19 Markdown files, 411 insertions / 298 deletions. This includes both text-only screenshot specifications and surgical Agent 365/audit-schema propagation through Control 1.21 and its four playbooks. No script, assessment engine, workflow, manifest, navigation or binary changes by Linus. Initial worktree was clean; parent subsequently regenerated build-derived version/render artifacts, which Linus preserved.

The source issue is **judeper/OceanSquad#911**, not an issue in the target repository **judeper/FSI-AgentGov**. CHANGELOG and the local PR draft use the qualified source reference; the draft says **Related**, leaving closure to the trusted parent. No remote lookup/action was used to establish that distinction.

## 2. Adversarial assessment: assumptions, blind spots and trade-offs

| Assumption being rejected or qualified | Strength | Failure mode if accepted | Failure mode of the correction |
|---|---|---|---|
| Documentation matches the actual tenant UI today | Weak; no tenant evidence | False UI verification stamp and unusable navigation | Explicit Needs Review can delay sign-off; that delay is justified |
| A solution import reproduces the production agent exactly | False | Production connectors/grounding survive transport; omitted components invalidate comparison | Transport-difference evidence adds work and may make comparisons inconclusive |
| A sandbox/security group proves synthetic-only isolation | False | Application users, privileged users, flows and external knowledge can bypass the assumed boundary | More thorough review costs time; a sampled scan alone remains insufficient |
| A testing OU does not need product licenses | False | Unauthorized/unavailable testing experience and unexpected metering | Entitlement checks can block setup; no exemption was invented |
| Copilot has no programmable interface | False | Useful supported tests are unnecessarily excluded | Preview Chat API is narrower than interactive Copilot and must not become a substitute for unsupported skills |
| A Foundry evaluator supports any uploaded output or agent | False | Misleading scoring or unsupported target/region | Coverage gaps must be reported instead of converted to a pass |
| Missing Prompt Shields means almost every attack succeeds | Unsupported | Fixed success claims obscure model/application defenses and measurement quality | Observed outcomes require properly designed tests rather than a convenient constant |
| A Direct Line activity acknowledgement is the bot answer | False | Empty/echo/acknowledgement responses produce false-clean runs | Withdrawing the broken adapter leaves firm implementation work rather than a ready-made runner |
| Every probe creates an audit/Defender/Communication Compliance event | False | No alert is misclassified as safe; wrong workload schemas joined | Actual telemetry can be partial or delayed; release evidence may remain inconclusive |
| Identical manifests prove destination bytes or complete evidence | False | Hash lists can match while bytes/files are absent or altered | Full destination recomputation adds cost, but manifest-only assurance is inadequate |
| Documentary examples constitute a delivered, fail-closed release gate | False | Empty, skipped, REVIEW, WhatIf or incomplete runs advance a release | These docs now expose implementation debt; no replacement implementation is claimed |
| Historical model/package/example versions remain deployable | Weak | Availability/compatibility failures | Versions remain illustrative and require CAB/current-region validation |
| Every referenced sibling was fully reverified | False | A targeted correction is misread as a full sibling certification | Sibling footers explicitly limit review; unrelated defects remain out of scope |

**Policy boundary:** Zone 1 advisory behavior, Zone 2 ≥90% with regression blocking, Zone 3 ≥95% overall and ≥98% Critical/High families, ≥100 Zone 3 Q&A pairs, pre-deployment testing and monthly Zone 3 cadence already existed in the original walkthrough. Downstream threshold/advisory corrections align to that **unchanged original policy**; they are not new firm policy or an interpretation of any regulation. The separate, broader quarterly exercise in Control 1.21 remains unchanged.

## 3. Technical discrepancy ledger

Source identifiers below resolve to exact Microsoft URLs in §5.

| Original statement/pattern | Corrected statement or limitation | Evidence |
|---|---|---|
| April UI date presented without current verification boundary | Added documentation-only Last Verified 2026-11-06; retained historical UI date; Needs Review footer | No tenant evidence exists; live-source review only |
| PPAC Environments/New legacy path | **Manage → Environments → New** | S01 |
| Dataverse optional for agent transport | Dataverse required for Copilot Studio environment/solution workflow | S01, S03 |
| DLP and audit grouped under environment Privacy + Security | Separate **Security → Data and privacy → Data policy** and **Manage → Environments → environment → Settings → Audit and logs → Audit settings** | S05, S06 |
| Security group prevents every unauthorized environment access | Licenses, Dataverse roles, sharing/channel authentication and documented privileged/application-user exceptions must be reviewed separately | S04 |
| Synthetic-data status can be established by a Data Map scan | Review every source/destination; scan supported sources only as supplementary sampled classification evidence | S09 |
| Nonlicensed test OU / generic isolation presumed adequate | Assign surface-specific licenses; Microsoft 365 Copilot needs isolated Microsoft 365 content/test tenant, not a Power Platform sandbox | S04, S07, S10, S11 |
| Managed Environment/PIM/Foundry prerequisites implicit | Qualifying standalone licenses/meters; Entra P2 or ID Governance for PIM; Foundry role, region, quota/billing prerequisites | S07, S08, S12 |
| Agent → Settings → Solutions → Export/Import treated as complete clone | Use solution explorer **… → Solutions**, approved unmanaged source release, required objects, dependencies and import ordering | S02, S03 |
| Production managed solution can be exported | Installed managed solutions cannot be exported; do not mutate production to manufacture an export | S03 |
| Import/publish considered sufficient | Reconfigure authentication, replace production connections/tools/grounding, review nontransported components and record differences before publication | S03 |
| Foundry Deployments → Export | No assumed portal export; capture documented deployment metadata and applicable RAI policy, recreate through firm's authorized deployment process | S17, S18 |
| Policy export proves deployment protection | Capture assignment, actual configuration surface and representative outcomes; resource RAI policy is not a complete agent guardrail export | S16, S17, S18 |
| Fixed old guardrail path | New experience **Build** (top right) → **Guardrails** (left); distinguish classic content filters | S16 |
| Prompt Shields universally blocks all tested attacks | User prompt detection default on; document detection default off; separate detected/filtered; standalone API only detects; supported intervention points and preview tool-response coverage matter | S15, S16 |
| No Shields implies near-100% attack success / enabled Shields implies near-zero success | Removed unsupported constants; model, application, attack design and scoring determine observed outcomes | S15; no source supports those constants |
| No portal adversarial runner | Foundry offers AI Red Teaming Agent for supported targets; no universal three-surface runner and no shipped repository runner | S14, S23 |
| PyRIT = Python Risk Identification Toolkit | **Python Risk Identification Tool**; same correction in directly linked 1.21/2.5 mentions and 2.20 resource label | S14, S23 |
| Microsoft 365 Copilot not script-promptable | Preview Chat API supports multi-turn text with Copilot add-on license and all listed delegated permissions; no application permissions or action/content-generation skills | S10, S11 |
| Risk + Safety evaluations treated as unrestricted generic portal scoring | **Evaluation → Create**, supported targets, mappings, roles and evaluator/region restrictions; Partial/Failed are not passing results | S12, S13 |
| Sensitive-data/prohibited-action evaluators assumed generic dataset/model scoring | Preview agent-target-only restrictions preserved; score/label/defect rate is not the firm's defense-rate metric | S13 |
| Old local/cloud SDK examples interchangeable | Newer cloud workflow uses `azure-ai-projects`; classic/local `azure-ai-evaluation` differs; pin compatible approved version/adapter | S23, S24 |
| Direct Line POST activity response `.text` is bot answer | Withdrew incorrect helper. POST returns activity ID; receive messages through GET/WebSocket, watermarks, correlation and timeout | S20, S21 |
| Direct Line token expiry fixed/refresh behavior and UI path wrong | Use **Settings → Security → Web channel security → Require secured access**; retain returned expiry; refresh before expiry; expired token cannot refresh; single-conversation token; channel security is not end-user authentication | S22 |
| Unverified `$policy.ContentFilters` validation loop/categorical assumptions | Withdrew loop; retain documented RAI-policy/deployment capture with explicit schema/assignment limitations | S17, S18 |
| Universal ConversationId/AgentId joins and audit for every probe | Workload-specific operation/record type and available metadata; record correlation confidence and unavailable planes | S25 |
| Universal detection/queue timing and per-probe alert expectation | Applicable policy scope, review percentage, billing, onboarding, observed delay; no clean inference from missing alerts | S25, S26, S27 |
| Agent security treated entirely as legacy Defender plan | Copilot Studio/Foundry agent security transition requires Agent 365 from July 1, 2026 and appropriate onboarding/registry; model protection remains distinct | S27 |
| Illustrative YAML model IDs, versions, latency and join key presented as current behavior | Historical specimen explicitly illustrative; actual availability/configuration/telemetry identifiers required | S12–S18, S25–S27 |
| Runner described as read-only/idempotent and fully automated | Probes consume resources and may invoke tools; repository does not ship the named scripts; document incomplete firm-owned patterns | Source inspection; S03, S10–S14 |
| Five-character response heuristic establishes reachability | Require actual bot/agent response to canary with correlation; legitimate short responses and acknowledgements are not proof either way | S20, S21 |
| Missing baseline merely recorded while unqualified release continues | Fail preflight for a missing required baseline; separately authorized diagnostic runs cannot count as release pass | Unchanged original preflight policy |
| Verification used inconsistent zone/family gates and treated all zones identically | Align to unchanged walkthrough policy; require errors/empty/skipped/REVIEW/missing-evidence negative-path tests | Source-to-source consistency |
| Hashing a subset / comparing two manifests establishes evidence integrity | Require all applicable artifacts and recompute destination hashes from bytes, with runtime/role/cadence attestations | Source-to-source requirements; not runtime certification |
| Troubleshooting advertises `--repeat` support | No delivered repeat mode; implement validated repetitions/first-run evidence through firm process | Repository contains no such runner |
| KQL produces reliable red-team alert count | Preserve example but warn it assumes tables/fields/time windows and can count unrelated alerts, especially absent AgentId | Source inspection; S25, S27 |
| 2.5 labels 2.20 Incident Response / agent disable | Correct title; containment references point to existing **3.4 — Incident Reporting and Root Cause Analysis** workflow | Canonical control catalog; no regulation changed |
| 2.25 says 2.20 starts a Foundry-only control range | Clarify 2.20 cross-surface applicability | Corrected 2.20 specification |
| License table says N/A process for 2.20 | Surface-specific entitlements/metering; link to verified walkthrough prerequisites | S04, S07, S08, S10–S13, S26, S27 |

## 4. Walkthrough claim coverage, section by section

This covers the full walkthrough, not a sample of navigation steps. Firm controls are distinguished from Microsoft product capabilities.

| Walkthrough location | Claims reviewed | Disposition |
|---|---|---|
| Header/time/governance metadata | Verification date, UI evidence, effort estimate, governance labels | Date updated with documentation boundary; time is a variable planning estimate, not Microsoft SLA |
| READ FIRST / surfaces / §0 scope | Copilot Studio, Microsoft 365 Copilot, Foundry, PyRIT, sibling routing, sandbox/API boundary | Corrected surface-specific applicability; regulatory and standards wording retained |
| §0 portal/script matrix | Environment cmdlet, solution transport, endpoint runners, Foundry evaluations, evidence helper | Documented platform routes and unsupported universal/shipped-runner assumptions corrected |
| §1.1 authorization | Charter/ROE, segregation, signatures, CFAA/vendor terms, production exclusions | Firm/legal requirements retained verbatim; no legal rejudgment |
| §1.2 environment | Sandbox naming/type/region, DLP/Managed Environment comparison, synthetic-only content, scan evidence | Product prerequisites and scan/access limits corrected; isolation not asserted achieved |
| §1.3 identity | Licensed test identities, least privilege, PIM, audit | Entitlement/PIM prerequisites added; separate audit scopes explained |
| §1.4 tooling | PyRIT identity/version/adapter; tagged attack/golden data; evidence destination | Tool name corrected; versions are CAB-selected, not certified installed |
| Step 1 charter | Scope, approvals, cadence, severity SLAs, records-retention mapping | Existing firm/regulatory language unchanged |
| Step 2 environment | PPAC navigation, database, access group, policy/audit settings, Managed licensing | S01, S04–S09; documentation verified only |
| Step 3 Copilot Studio | Solution explorer, export type, dependency/import order, authentication, publication, missing components | S02/S03; exact-clone assertion withdrawn |
| Step 3 Foundry | Portal experience, deployment/RAI cmdlets, authorized recreation, model/quota, assignment | S16–S18; current tenant/model availability unresolved |
| Step 4 safety baseline | Build → Guardrails, user/document defaults, intervention points, detection/blocking, screenshots | S15/S16; no new screenshot evidence, no fixed success constants |
| Step 5 attack/golden library | Internal Git checkout specimen, OWASP/ATLAS mappings, FSI families, ≥100 Q&A | Firm repository/example/coverage requirements retained; no Git command executed |
| Step 6 gate | Zone thresholds, overrides, fail-closed release, runner availability | Original policy retained; implementation incompleteness prominently exposed |
| Step 7 cycle | Actual target invocation, preview Copilot API, PyRIT, Foundry scoring/mappings/results, findings/evidence | Supported interfaces and evaluator scope distinguished; no run certified |
| Step 8 evidence | Prompt/response/results/configuration/manifest artifacts, immutability destination, metadata correlation | Requirements retained; manifests/holds do not substitute for runtime or full-byte checks |
| Step 9 reconciliation | Prompt Shields, Defender, XDR, Communication Compliance, audit schema/latency | S15/S25–S27; applicability/onboarding/billing/metadata qualified |
| Zone matrix | Advisory/blocking/cadence/library/sign-off thresholds and severity | Unchanged original program policy; downstream instructions aligned |
| Illustrative YAML | Deployment versions, tools/data, cadence/thresholds, evidence/telemetry names and delays | Historical illustrative specimen, not tested tenant inventory or current availability |
| Final checklist | Configuration, gate, artifacts, GRC findings, telemetry | Added explicit unknown/unsupported/incomplete evidence criterion; not a completion attestation |
| Microsoft sources | Names, navigation, availability, licensing, transport, cmdlets, behavior | Primary URLs listed below with claim mapping |
| Footer | Updated month/version/UI status | November 2026, unchanged v1.6.2, Needs Review |

## 5. Official Microsoft source register

Live Microsoft Learn search/fetch review date: **2026-11-06**. These documents support product statements; they are not tenant evidence or independent proof of firm compliance.

| ID | Exact URL | Supported claim |
|---|---|---|
| S01 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/environments-first-run-experience | PPAC Manage → Environments → New, database/environment requirements and supported region |
| S02 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-overview | Solutions explorer **… → Solutions**, alternatives from agent settings/overview |
| S03 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export | System Customizer minimum, source solution, managed export restriction, required objects/dependencies, connectors/import order, omitted properties, authentication/publication |
| S04 | https://learn.microsoft.com/en-us/power-platform/admin/control-user-access | Security groups, licenses, Dataverse security roles and privileged/application-user exceptions |
| S05 | https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss | Data policy navigation and effective policy scope |
| S06 | https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing | Audit settings navigation, table/column scope, separation from other audit streams |
| S07 | https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-licensing | Qualifying standalone license/pay-as-you-go coverage for active Managed Environment usage |
| S08 | https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-getting-started | Entra P2/ID Governance licensing and PIM role/elevation boundaries |
| S09 | https://learn.microsoft.com/en-us/purview/data-map-data-sources | Supported Data Map sources and sampled classification; scan cannot prove every object is synthetic |
| S10 | https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/overview | Chat API preview, Copilot add-on license, multi-turn text, unsupported action/content-generation/graphic/code tools |
| S11 | https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/copilotconversation-chat | `/beta/copilot/conversations/{id}/chat`, all documented delegated permissions, no application permissions |
| S12 | https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app | Evaluation → Create, Foundry User role, target/dataset mapping, Partial/Failed status and experience limits |
| S13 | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators | Target-specific safety evaluators, preview agent-only sensitive-data/prohibited-actions scopes, score interpretation |
| S14 | https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent | PyRIT expansion/integration; supported models/agents/risks/regions, nondeterminism, mock-tool/coverage limitations |
| S15 | https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection | User/document defaults, detected versus filtered, standalone detection, supported input/tool-response intervention points |
| S16 | https://learn.microsoft.com/en-us/azure/foundry/guardrails/how-to-create-guardrails | **Build → Guardrails**, configuration/assignment and new experience |
| S17 | https://learn.microsoft.com/en-us/powershell/module/az.cognitiveservices/get-azcognitiveservicesaccountdeployment | Read-only Azure deployment metadata capture and cmdlet parameters |
| S18 | https://learn.microsoft.com/en-us/powershell/module/az.cognitiveservices/get-azcognitiveservicesaccountraipolicy | Applicable RAI-policy capture; not proof of assignment or universal guardrail export |
| S19 | https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/new-adminpowerappenvironment | Sandbox provisioning, ProvisionDatabase/LanguageName/CurrencyName/SecurityGroupId parameters |
| S20 | https://learn.microsoft.com/en-us/azure/bot-service/rest-api/bot-framework-rest-direct-line-3-0-send-activity | POST activity returns an ID, not bot answer text |
| S21 | https://learn.microsoft.com/en-us/azure/bot-service/rest-api/bot-framework-rest-direct-line-3-0-receive-activities | Receive bot messages via GET/WebSocket, watermark handling and correlation |
| S22 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/configure-web-security | Web channel security navigation, up-to-two-hour propagation, no republish requirement, single-conversation token and expiry/refresh boundary |
| S23 | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-ai-red-teaming-cloud | Cloud red-team workflow/SDK and supported target/role requirements |
| S24 | https://learn.microsoft.com/en-us/azure/foundry-classic/how-to/develop/run-scans-ai-red-teaming-agent | Classic/local red-team workflow differs from newer cloud SDK |
| S25 | https://learn.microsoft.com/en-us/purview/audit-copilot | Separate Operation/RecordType/Workload/AppIdentity, available agent/message/resource metadata, no universal conversation join; Microsoft applications including Studio custom applications in Audit Standard versus documented non-Microsoft pay-as-you-go auditing |
| S26 | https://learn.microsoft.com/en-us/purview/communication-compliance-copilot | Scoped AI policies/conditions/review percentage/reviewers; Copilot Studio/non-M365 detection metering versus M365 Copilot |
| S27 | https://learn.microsoft.com/en-us/defender-xdr/security-for-ai/transition-agent-security-to-agent-365 | Agent 365 transition, agent onboarding/observability/registry, changing alerts/BehaviorInfo versus continuing model protection |

Parent independently crosschecked Direct Line acknowledgements, Chat API restrictions, Build → Guardrails, evaluations/navigation/role/targets/mappings/Partial/Failed, and Managed Environment license/meter prerequisites against live Learn.

## 6. Complete downstream classification

Discovery covered tracked repository text plus relevant generated/ignored artifacts, without reading secrets or `.env` files. Searches used the control ID, exact title and repeated claims; numeric `2.20.0` hits were separated from true Control 2.20 references. A final broader `2\.20|adversarial|pyrit` path enumeration found **153 distinct tracked paths** and also classified keyword-only matches below. A separate report read-back assertion confirmed every one of those paths appears in this inventory. This is a complete dependency classification, **not** an assertion that every unrelated page received independent technical/UI re-verification.

### 6.1 Changed authorable files — all 19

| Path | Individual reason |
|---|---|
| `CHANGELOG.md` | Added notable judeper/OceanSquad#911 technical verification/correction entry under Unreleased/Fixed; qualified the source issue to avoid target-repository misreference |
| `docs\controls\pillar-2-management\2.20-adversarial-testing-and-red-team-framework.md` | Documentation date/boundary; PyRIT name; supported targets/licensing/isolation; workload-specific evidence correlation; incomplete evidence criterion; all ten sections retained |
| `docs\playbooks\control-implementations\2.20\portal-walkthrough.md` | Entire product walkthrough corrected and sourced; actual UI date not renewed |
| `docs\playbooks\control-implementations\2.20\powershell-setup.md` | Firm-owned/incomplete-pattern boundary, corrected API/protocol/capture assumptions; bad adapter and RAI validation loop withdrawn; KQL explicitly unverified |
| `docs\playbooks\control-implementations\2.20\verification-testing.md` | Negative-path/completeness/actual-response/bytes checks and unchanged-policy zone thresholds aligned |
| `docs\playbooks\control-implementations\2.20\troubleshooting.md` | Token/telemetry/target/baseline/gate/repetition caveats agree with corrected implementation boundaries |
| `docs\reference\license-requirements.md` | Removed blanket N/A-process entitlement impression; surface-specific prerequisites |
| `docs\playbooks\control-implementations\2.5\powershell-setup.md` | Cross-link no longer promises delivered 2.20 automation; repeated PyRIT name corrected |
| `docs\playbooks\control-implementations\2.5\verification-testing.md` | Corrected incorrect 2.20 Incident Response title only |
| `docs\playbooks\control-implementations\2.5\troubleshooting.md` | Incorrect 2.20 disable/containment routing corrected to existing 3.4; 2.20 label corrected; no compliance interpretation |
| `docs\playbooks\control-implementations\2.25\portal-walkthrough.md` | 2.20 applicability corrected; not Foundry-only |
| `docs\controls\pillar-1-security\1.21-adversarial-input-logging.md` | PyRIT expansion plus source-cited Agent 365 agent/model/onboarding/inventory/alert-behavior applicability; S25 qualifiers remove every-Studio-thread CopilotInteraction and universal conversation assumptions. Quarterly program and regulatory prose retained |
| `docs\playbooks\control-implementations\1.21\portal-walkthrough.md` | Source-cited transition and audit scope; obsolete positive handshake claims/audit-pack row10 replaced, row12 accepts applicable raw alert/behavior identifiers; audit payload fields/filters/correlation distinguish workloads; native Copilot search remains explicitly scoped |
| `docs\playbooks\control-implementations\2.5\portal-walkthrough.md` | Directly linked PyRIT expansion corrected only |
| `docs\playbooks\control-implementations\1.21\powershell-setup.md` | Agent/model/onboarding boundary and alert-only BehaviorInfo limitation; native-only fixed CopilotInteraction collector explicitly not all-Studio coverage, requiring actual workload filters and schema-aware correlation; no executable implementation added |
| `docs\playbooks\control-implementations\1.21\verification-testing.md` | Agent 365 and DXR requirements plus S25 UAL/DET/ZONE/NEG scope, supported operation/record-type and correlation assertions, no every-prompt rule; native M365 examples retained and Studio auditing not universally pay-as-you-go |
| `docs\playbooks\control-implementations\1.21\troubleshooting.md` | Agent/behavior applicability plus S25 audit-category check before diagnosing lag; wrong-category empty queries cannot prove safety or ingestion delay |
| `docs\images\2.20\EXPECTED.md` | Authorized text-only completion: monthly Z3/per-release predeployment/minimum100 Z3/isolated synthetic requirements; precise role/license/transport/guardrail/reply/evaluation/telemetry/integrity evidence and documentation-versus-UI boundary. Original literal 7+ years retention line preserved and legal-owner conflict flagged |
| `docs\images\1.21\EXPECTED.md` | Authorized text-only completion: current Agent 365 eligibility/settings/registry-observability/inventory, applicable alerts/behaviors and blocking policy; workload-specific audit payload/correlation rather than generic DCA policy or universal CopilotInteraction. Existing verification-focus/retention/regulatory wording preserved; no screenshots acquired |

Sibling 1.21/2.5/2.25 November footers explicitly say **targeted 2.20 dependency correction only; no new tenant UI evidence**. They do not claim whole-page re-verification.

### 6.2 Exact control-ID/title references unchanged

| Path | Individual reason |
|---|---|
| `docs\controls\CONTROL-INDEX.md` | ID/title/pillar/zone/automation listing unchanged |
| `docs\controls\index.md` | Catalog/name link, not corrected procedures |
| `docs\controls\pillar-2-management\index.md` | Pillar listing/title unchanged |
| `docs\controls\pillar-1-security\1.27-ai-agent-content-moderation-enforcement.md` | Related-control link retains correct adversarial purpose |
| `docs\controls\pillar-2-management\2.18-automated-conflict-of-interest-testing.md` | Related-control relationship unchanged |
| `docs\controls\pillar-2-management\2.5-testing-validation-and-quality-assurance.md` | Specification's related-control relationship remains correct; incorrect labels were in its playbooks |
| `docs\framework\adoption-roadmap.md` | Adoption dependency/timing, not disputed interface mechanics |
| `docs\framework\agentic-capability-drivers.md` | Control applicability mapping unchanged |
| `docs\framework\executive-summary.md` | Strategic control applicability, not runner/evaluator promise |
| `docs\framework\transformation-patterns.md` | Pattern/control mapping unchanged |
| `docs\playbooks\control-implementations\1.27\verification-testing.md` | Corpus/retest dependency still correct; no universal interface guarantee |
| `docs\playbooks\control-implementations\2.24\verification-testing.md` | Feature-change retest dependency remains appropriate |
| `docs\playbooks\control-implementations\index.md` | Four playbook links/title unchanged |
| `docs\playbooks\getting-started\phase-2-hardening.md` | Adoption link remains correct |
| `docs\playbooks\governance-operations\governance-operating-calendar.md` | Existing governance schedule; no correction to original 2.20 policy |
| `docs\reference\assessment-coverage.md` | 2.20 remains manual; no evaluator wired |
| `docs\reference\cco-quick-reference.md` | CCO-facing testing relationship, not technical export/API instructions |
| `docs\reference\csa-positioning-guide.md` | Positioning/control mapping unchanged |
| `docs\reference\csa-quick-reference.md` | Engagement/control relationship unchanged |
| `docs\reference\glossary.md` | Terminology/control reference, not stale walkthrough feature assertions |
| `docs\reference\iso-42001-mapping.md` | Standards mapping intentionally preserved |
| `docs\reference\microsoft-cape-crosswalk.md` | Crosswalk relationship unchanged |
| `docs\reference\microsoft-rai-v2-mapping.md` | Standards relationship unchanged |
| `docs\reference\nist-ai-rmf-crosswalk.md` | NIST labels/mappings intentionally unchanged |
| `docs\reference\owasp-llm-top10-crosswalk.md` | OWASP mapping/coverage unchanged |
| `docs\reference\pattern-coverage.md` | Control coverage mapping unchanged |
| `docs\reference\power-platform-sspm-control-mapping.md` | Control mapping, not endpoint/guardrail execution claim |
| `docs\reference\regulatory-mappings.md` | Explicitly preserved regulatory mapping |
| `docs\reference\solutions-coverage-gaps.md` | 2.20 solution-gap classification unchanged; no runner implementation added |
| `assessment\manifest\controls.json` | 2.20 manual with empty automated checks; manual questions/threshold source unchanged |
| `assessment\manifest\generate_manifest.py` | Same manual definition; prohibited code mutation unnecessary |
| `tests\e2e\fixtures\personas\all-zone3-production.json` | Manual-answer fixture unaffected by prose-only technical corrections |
| `tests\e2e\fixtures\personas\full-cco.json` | Persona/manual-answer fixture unchanged |
| `tests\e2e\fixtures\personas\unicode-i18n.json` | Unicode/manual-answer contract unchanged |
| `mkdocs.yml` | All page paths/IDs/titles unchanged; no new navigation node |
| `docs\llms.txt` | Tracked listing uses unchanged title/objective/URL, not full corrected body |
| `docs\javascripts\control-explorer-data.json` | Regenerated data semantically identical; only generatedAt changed and was restored |
| `tests\e2e\fixtures\render-expectations.json` | All five 2.20 entries unchanged; parent must regenerate after build for temporary role-page context |
| `scripts\extract_assessment_data.py` | Existing generator used, not edited; changed verification criteria propagate to ignored JSON |
| `scripts\generate_excel_templates.py` | Hard-coded catalog/workbook construction, not corrected technical procedure; no workbook field changed |
| `scripts\update_excel_templates.py` | Hard-coded workbook catalog updates not needed; no version/ID/title change |

### 6.3 Screenshot/evidence checklist — authorized text correction completed

| Path | Disposition/reason |
|---|---|
| `docs\images\2.20\EXPECTED.md` | Updated following explicit same-task authorization. Replaced quarterly Zone 3, ≥100 “recommended” and pre-production “when possible” with unchanged source-policy requirements. Added five precise evidence categories and fail/incomplete distinctions. No screenshot/tenant actions. The exact original line `- Test evidence must be preserved per retention requirements (7+ years)` remains unchanged; legal/records owner review remains open. |

The checklist disagreement concerned the **existing original walkthrough policy**, not newly invented cadence or thresholds. Its text-only alignment is complete; tenant evidence and the pre-existing retention inconsistency remain separate unresolved items.

### 6.4 Broad keyword/version matches and recursive sibling context — unchanged

Each row is classified individually. “Own control” means no dependency on the specific corrected 2.20 statement; it is not a certificate that the page has no other defects.

| Path | Individual reason |
|---|---|
| `README.md` | Broad framework/adversarial summary; no changed ID/count/version or technical walkthrough procedure |
| `assessment\manifest\frontier-readiness.json` | Separate readiness metadata, no affected evaluator/2.20 implementation |
| `assessment\tests\test_manifest_validation.py` | General adversarial/schema test terminology, no changed manual manifest contract |
| `assessment\tests\test_score.py` | General scoring tests, no evaluator/code added |
| `docs\controls\pillar-1-security\1.11-conditional-access-and-phishing-resistant-mfa.md` | Own identity-control context, not changed 2.20 interface claim |
| `docs\controls\pillar-1-security\1.19-ediscovery-for-agent-interactions.md` | Evidence/hold relationship reviewed; no retention-law reinterpretation permitted |
| `docs\controls\pillar-1-security\1.2-agent-registry-and-integrated-apps-management.md` | Risk/register dependency, not changed agent runner |
| `docs\controls\pillar-1-security\1.25-mime-type-restrictions.md` | Own file-type defense terminology |
| `docs\controls\pillar-1-security\1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` | Correct destination for DLP configuration; own policy not rewritten |
| `docs\controls\pillar-1-security\1.7-comprehensive-audit-logging-and-compliance.md` | Audit dependency reviewed; no broad audit-control rewrite |
| `docs\controls\pillar-1-security\1.8-runtime-protection-and-external-threat-detection.md` | Own runtime-detection surface; no targeted 2.20 procedure reproduced |
| `docs\controls\pillar-1-security\index.md` | Pillar catalog unchanged |
| `docs\controls\pillar-3-reporting\3.1-agent-inventory-and-metadata-management.md` | Identity confirmed: inventory, not DLP; only incorrect walkthrough routing changed |
| `docs\controls\pillar-3-reporting\3.2-usage-analytics-and-activity-monitoring.md` | Own usage analytics/adversarial context |
| `docs\controls\pillar-3-reporting\3.4-incident-reporting-and-root-cause-analysis.md` | Correct existing containment/RCA relationship confirmed |
| `docs\controls\pillar-4-sharepoint\4.7-microsoft-365-copilot-data-governance.md` | Own SharePoint/Copilot governance context |
| `docs\framework\regulatory-framework.md` | Regulatory language intentionally untouched |
| `docs\images\diagrams\3-1-agent-inventory-and-metadata-management-unified-agent-vi.svg` | Broad numeric/vector match; unrelated rendering artifact |
| `docs\images\diagrams\agent-identity-architecture-m365-admin-center-agent-settings.svg` | Numeric/vector match; unrelated architecture diagram |
| `docs\images\diagrams\deployment-guide-deployment-architecture.svg` | Numeric/vector match; no changed diagram source |
| `docs\images\diagrams\evidence-and-audit-evidence-architecture.svg` | Numeric/vector match; evidence architecture not regenerated by prose edit |
| `docs\images\diagrams\implementation-provisioning-provisioning-architecture.svg` | Numeric/vector match; unrelated provisioning diagram |
| `docs\images\diagrams\index-architecture-overview.svg` | Numeric/vector match; unchanged overall architecture |
| `docs\images\diagrams\power-bi-correlation-dataverse-tables.svg` | Numeric/vector match; unrelated Power BI diagram |
| `docs\images\diagrams\solutions-integration-integration-architecture.svg` | Numeric/vector match; solution catalog diagram unchanged |
| `docs\playbooks\advanced-implementations\deny-event-correlation-report\purview-audit-extraction.md` | Separate audit-extraction scenario/module version; no universal red-team correlation correction needed here |
| `docs\playbooks\control-implementations\1.11\powershell-setup.md` | Graph module version `2.20.0`, not Control 2.20 |
| `docs\playbooks\control-implementations\1.11\troubleshooting.md` | Version/sibling identity context, not changed red-team behavior |
| `docs\playbooks\control-implementations\1.12\powershell-setup.md` | Graph module version, separate insider-risk setup |
| `docs\playbooks\control-implementations\1.13\powershell-setup.md` | Shared SIT prerequisite/module version, no changed SIT implementation |
| `docs\playbooks\control-implementations\1.14\verification-testing.md` | Own permission-verification scenario |
| `docs\playbooks\control-implementations\1.19\portal-walkthrough.md` | Hold/preservation dependency reviewed; legal/retention statements preserved |
| `docs\playbooks\control-implementations\1.19\troubleshooting.md` | Own preservation troubleshooting, not new 2.20 runtime pattern |
| `docs\playbooks\control-implementations\1.19\verification-testing.md` | Own hold verification; not substituted for complete destination-byte/runtime evidence |
| `docs\playbooks\control-implementations\1.2\powershell-setup.md` | Registry/module-version context |
| `docs\playbooks\control-implementations\1.2\troubleshooting.md` | Own registry troubleshooting |
| `docs\playbooks\control-implementations\1.2\verification-testing.md` | Own registry tests |
| `docs\playbooks\control-implementations\1.27\portal-walkthrough.md` | Own moderation baseline; no corrected 2.20 workflow copied |
| `docs\playbooks\control-implementations\1.27\troubleshooting.md` | Own moderation diagnostics |
| `docs\playbooks\control-implementations\1.5\portal-walkthrough.md` | DLP prerequisite context; no policy redesign |
| `docs\playbooks\control-implementations\1.5\powershell-setup.md` | DLP/module-version context, not red-team runner |
| `docs\playbooks\control-implementations\1.6\powershell-setup.md` | Own DSPM/module-version context |
| `docs\playbooks\control-implementations\1.8\portal-walkthrough.md` | Separate runtime-defense feature guide |
| `docs\playbooks\control-implementations\1.8\troubleshooting.md` | Separate runtime-defense diagnostics |
| `docs\playbooks\control-implementations\2.12\verification-testing.md` | Supervision/approval context, regulation preserved |
| `docs\playbooks\control-implementations\2.26\verification-testing.md` | Own agent-identity test; no changed red-team interface contract |
| `docs\playbooks\control-implementations\2.6\troubleshooting.md` | MRM program relationship; no regulatory rejudgment |
| `docs\playbooks\control-implementations\2.6\verification-testing.md` | Independent validation program context; 2.20 remains an input |
| `docs\playbooks\control-implementations\3.1\portal-walkthrough.md` | Inventory guide confirms corrected DLP misrouting; own content unchanged |
| `docs\playbooks\control-implementations\3.1\verification-testing.md` | Own inventory checks |
| `docs\playbooks\control-implementations\3.4\portal-walkthrough.md` | Existing incident/RCA destination; 2.5 routing correction does not revise it |
| `docs\playbooks\control-implementations\4.7\portal-walkthrough.md` | Own SharePoint/Copilot governance |
| `docs\playbooks\control-implementations\4.7\verification-testing.md` | Own SharePoint/Copilot test |
| `docs\playbooks\incident-and-risk\ai-incident-response-playbook.md` | Existing response process, not 2.20's proactive program |
| `docs\playbooks\regulatory-modules\colorado-ai-impact-assessment.md` | Own regulatory/adversarial vocabulary; untouched |
| `docs\reference\compliance-manager-templates.md` | Broad assurance terminology, no corrected interface dependency |
| `docs\reference\examiner-first-day-letter-response.md` | Examiner/evidence context, not technical runner contract |
| `docs\playbooks\_shared\powershell-baseline.md` | Explicitly linked helper/pinning/ShouldProcess/hash baseline reviewed; it cannot turn missing firm scripts into shipped automation |
| `scripts\test_control_110_playbook_guards.py` | Separate 1.10 test terminology, not affected 2.20 behavior |
| `docs\javascripts\vendor\mermaid.min.js` | Vendored library/numeric matches; no governance-product claim; excluded from source edits |
| `package-lock.json` | Dependency version/numeric matches, not control metadata; Linus did not edit dependencies |

### 6.5 Historical/governance/monitoring artifacts — individually unchanged

These are evidence of earlier states or separate monitoring pipelines, not current implementation instructions. They were not rewritten to falsify history.

| Path | Individual reason |
|---|---|
| `.squad\decisions\archive\381-nist-crosswalk-mapping.md` | Historical NIST mapping decision |
| `.squad\decisions\archive\398-nist-measure-2x-label-drift.md` | Historical mapping-label decision |
| `.squad\decisions\archive\saul-360-graph-reverify.md` | Historical unrelated graph-verification record |
| `.squad\decisions\archive\saul-classA-reverify.md` | Historical unrelated verification record |
| `data\learn-monitor-state.json.migrated` | Historical monitor migration state, not authority for current docs |
| `data\monitor-pending\learn\learn.microsoft.com-en-us-purview-communication-compliance-policies-62029d067cd2517ccd9a41f7.json` | Existing pending monitoring payload; no pipeline/state mutation |
| `data\monitor-pending\learn\learn.microsoft.com-en-us-purview-communication-compliance-policies-dbf2e88693fabc9ebd22dd78.json` | Separate pending source payload; not regenerated by authoring docs |
| `data\monitor-state.json` | Monitor source history, not a derived control catalog |
| `data\monitor-state.json.backup` | Historical backup, intentionally retained |
| `releases\CHANGELOG-archive\CHANGELOG-v1.3.md` | Released historical changelog |
| `reports\audit\02-inventory.md` | Historical audit inventory |
| `reports\audit\03-learn-validation-matrix.md` | Historical validation matrix, not new verification evidence |
| `reports\audit\06-remediation-backlog.md` | Historical backlog |
| `reports\issue-821-reverification.md` | Another issue's verification record |
| `reports\learn-changes\learn-changes-2026-02-01.md` | Historical February source-drift report |
| `reports\monitoring\learn-changes-2026-04-28.md` | Historical April drift report containing 2.20 |
| `reports\monitoring\learn-changes-2026-05-12.md` | Historical May drift output |
| `reports\monitoring\learn-changes-2026-05-28.md` | Historical May drift output |
| `reports\monitoring\learn-changes-2026-05-29.md` | Historical May drift output |
| `reports\monitoring\learn-changes-2026-05-30.md` | Historical May drift output |
| `reports\monitoring\learn-changes-2026-05-31.md` | Historical May drift output |
| `reports\monitoring\learn-changes-2026-06-01.md` | Historical June drift output |
| `reports\monitoring\learn-changes-2026-06-02.md` | Historical June drift output |
| `reports\monitoring\learn-changes-2026-06-03.md` | Historical June drift output |
| `reports\monitoring\learn-changes-2026-06-04.md` | Historical June drift output |
| `reports\monitoring\learn-changes-2026-07-12.md` | Historical July drift output |
| `reports\monitoring\learn-changes-2026-07-18.md` | Historical July drift output |
| `reports\monitoring\learn-changes-2026-07-20.md` | Historical July drift output |
| `reports\monitoring\learn-changes-2026-07-21.md` | Historical July drift output |
| `reports\monitoring\learn-changes-2026-07-22.md` | Historical July drift output |
| `reports\monitoring\learn-changes-2026-08-22.md` | Historical August drift output |
| `reports\monitoring\learn-changes-2026-08-27.md` | Historical August drift output |
| `reports\monitoring\learn-changes-2026-09-22.md` | Historical September drift output |
| `reports\monitoring\learn-changes-2026-11-04.md` | Historical November monitoring run |
| `reports\regulatory-language-violations-20260214-154451.md` | Historical language-linter output, not current policy |

The local Linus charter, `.squad\skills\repo-context.md`, `.squad\decisions.md`, repository instructions, applicable path instructions, CONTRIBUTING, canonical control template and PR template were read as required. No Squad charter/decision/memory/governance file was created or edited.

## 7. Generators, derived outputs and binary inventory

### 7.1 Exact commands and results

| Command | Result and precise impact |
|---|---|
| `python scripts\extract_assessment_data.py` | **PASS**, 79 controls / 21 regulations, 26 adoption-phase mappings / 31 solution mappings; refreshed ignored `docs\javascripts\assessment-data.json` from source |
| `python scripts\gen_explorer_data.py` | **PASS**, 79 controls; title/objective-based extraction semantically unchanged, only generatedAt changed; Linus restored timestamp-only tracked churn |
| `python scripts\check_explorer_data_drift.py --check` | **PASS** after restoration |
| `node scripts\generate-render-expectations.mjs --out tests\e2e\fixtures\render-expectations.json --check` | **FAIL before build**, 147 absent build-generated pre-session role pages; 697→550 page set. Not a 2.20 asset change |
| `node scripts\generate-render-expectations.mjs --out tests\e2e\fixtures\render-expectations.json` | **PASS pre-build**, 550 pages / 39 Mermaid blocks / 63 diagram links / 6 asset links; inspected all five 2.20 entries, identical to baseline; restored unrelated generated fixture differences |
| `python scripts\compile_researcher_package.py` | **PASS**, ignored four pillar packages refreshed; existing hard-coded Pillar 2 range ends at 2.26, so legacy compiler emits 78 controls; no script edit |
| `python scripts\build_review_package.py` | **PASS**, default local-only successor package refreshed, dynamically discovers current controls; no `--site`, `--pdf` or external bundle publication |

Extractor and both reviewer-package commands were rerun after final directly dependent PyRIT label edits, after the authorized Control 1.21 transition follow-up, and after the final audit-schema/evidence completion. Explorer generation was repeated after the transition follow-up: semantic data still identical, own timestamp-only output restored; final audit-schema changes affect configuration/verification text, not its unchanged title/objective/role/catalog fields. Final Explorer drift check passed. No tracked generated artifact remains modified by Linus. Parent-owned build-derived changes were preserved.

### 7.2 Individual generated artifact classification

| Artifact / source | Classification and reason |
|---|---|
| `docs\javascripts\assessment-data.json` | Ignored output refreshed; changed 2.20 verification criteria include workload-specific correlation and unsupported/incomplete evidence. Read-back confirmed eight criteria. Authorized 1.21 follow-up also propagates model-versus-agent and applicable alert/behavior verification criteria. Existing extractor appends separator `---` to final criterion; flagged, not hand-corrected |
| `scripts\hooks\copy_assessment_data.py` | Existing build copy hook; generator output is build input, not an assessment-engine modification |
| `docs\javascripts\control-explorer-data.json` | Tracked output semantically unaffected: same name/objective/roles/zone/automation/regulatory fields, no extraction of corrected full-body text |
| `tests\e2e\fixtures\render-expectations.json` | Tracked render oracle: 2.20 control + four playbook entries have unchanged/no Mermaid/diagram/download assets; pre-session pages depend on preceding build |
| `scripts\generate-render-expectations.mjs` | Existing generator inspected, unmodified; parent/globalSetup owns post-build refresh/check |
| `scripts\gen_explorer_data.py` | Existing generator inspected/run, unmodified |
| `scripts\build_content_graph.py` | Does not exist in repository; cannot regenerate a nonexistent generator |
| Tracked content graph | No tracked derived content graph discovered; no manual graph output invented |
| `scripts\verify_xref_graph.py` | Validator, not persistent graph generator; parent ran cross-reference verification |
| `docs\llms.txt` | Tracked title/objective/URL listing unaffected; no full-text copied walkthrough |
| `mkdocs.yml` | Authoritative nav unchanged; build derives site navigation from unchanged nodes |
| `docs\reference\assessment-coverage.md` | Evaluator-generated coverage unaffected: 2.20 still manual, engine/manifest unchanged |
| `maintainers-local\researcher-package\01-Pillar-1-Security-Controls.md` | Refreshed ignored legacy compilation; 7,599 lines after authorized 1.21 naming/Agent 365 transition corrections |
| `maintainers-local\researcher-package\02-Pillar-2-Management-Controls.md` | Refreshed ignored legacy compilation; 5,864 lines, incorporates 2.20 corrections; pre-existing omission of 2.27 remains |
| `maintainers-local\researcher-package\03-Pillar-3-Reporting-Controls.md` | Generator emitted unchanged-scope local compilation; 4,280 lines |
| `maintainers-local\researcher-package\04-Pillar-4-SharePoint-Controls.md` | Generator emitted unchanged-scope local compilation; 2,028 lines |
| `maintainers-local\researcher-package\FSI-AgentGov-Review-Package\00-SITE-MAP.md` | Successor-generated local site map refreshed, approximately 58 KB |
| `maintainers-local\researcher-package\FSI-AgentGov-Review-Package\area-1-controls.md` | Successor-generated local full control corpus refreshed, approximately 1,771 KB after the transition follow-up |
| `maintainers-local\researcher-package\FSI-AgentGov-Review-Package\area-2-playbooks.md` | Existing generator's selected-playbook corpus refreshed; not asserted to reproduce every full playbook |
| `maintainers-local\researcher-package\FSI-AgentGov-Review-Package\area-3-assessment.md` | Local assessment review area refreshed; no engine code change |
| `maintainers-local\researcher-package\FSI-AgentGov-Review-Package\area-4-getting-started.md` | Local unchanged-scope onboarding corpus emitted |
| `maintainers-local\researcher-package\FSI-AgentGov-Review-Package\area-5-framework-and-ia.md` | Local unchanged-scope framework corpus emitted |
| `maintainers-local\researcher-package\FSI-AgentGov-Review-Package\area-6-reference-and-downloads.md` | Local reference corpus refreshed, including corrected licensing prose |
| Successor `00-START-HERE.md` | Generated local review-package entry point; not a hand-authored task governance file |
| Successor `MANIFEST.json` | Generated local package metadata |
| Successor `README.md` | Generated local package instructions |
| Successor `briefs\brief-1-controls.md` | Existing generator's control-review brief emitted locally |
| Successor `briefs\brief-2-playbooks.md` | Existing generator's playbook-review brief emitted locally |
| Successor `briefs\brief-3-assessment.md` | Existing generator's assessment-review brief emitted locally |
| Successor `briefs\brief-4-getting-started.md` | Existing generator's onboarding-review brief emitted locally |
| Successor `briefs\brief-5-framework-ia.md` | Existing generator's framework-review brief emitted locally |
| Successor `briefs\brief-6-reference-downloads.md` | Existing generator's reference-review brief emitted locally |
| Successor `briefs\brief-7-ux-and-adoption.md` | Existing generator's UX/adoption-review brief emitted locally |
| Successor `briefs\RESPONSE-TEMPLATE.md` | Existing generator's local reviewer-response template |
| Successor `briefs\REVIEWER-RUBRIC.md` | Existing generator's local reviewer rubric |
| `site\` output | Parent must build from settled sources before running any site consumer; no stale pre-build site result represented as current |
| `docs\version.json` | Parent-owned tracked build/version output changed during its validation; Linus did not edit or restore it |
| Parent's post-build `tests\e2e\fixtures\render-expectations.json` update | Parent/globalSetup-owned tracked render output; preserved, not confused with Linus's earlier restored pre-build churn |

### 7.3 All six tracked Excel downloads reviewed

Workbook ZIP/XML row inspection used standard-library parsing, not a new dependency.

| Path | Individual disposition |
|---|---|
| `docs\downloads\governance-maturity-dashboard.xlsx` | Unchanged: sheet3 row24 contains only `2.20`, unchanged title, `Not Started`, blank status fields; no corrected technical/licensing procedure embedded |
| `docs\downloads\compliance-officer-checklist.xlsx` | Unchanged: no 2.20 row; role subset unaffected |
| `docs\downloads\entra-administrator-checklist.xlsx` | Unchanged: no 2.20 row; role subset unaffected |
| `docs\downloads\power-platform-administrator-checklist.xlsx` | Unchanged: no 2.20 row; role subset unaffected |
| `docs\downloads\purview-administrator-checklist.xlsx` | Unchanged: no 2.20 row; role subset unaffected |
| `docs\downloads\sharepoint-administrator-checklist.xlsx` | Unchanged: no 2.20 row; role subset unaffected |

No Excel generator was run merely to churn unchanged titles/status rows or unrelated existing catalog/version debt.

## 8. Unimplemented patterns versus actual shipped defects

**No shipped `*Adversarial*.ps1` implementation was found.** The named runner, endpoint adapter, evidence helper and validator are documentary patterns. Their limitations are exposed in authorable docs instead of pretending to fix an executable package.

Still-required firm implementation/runtime work:

1. Load a real helper and implement supported target adapters; Direct Line ACK/echo must not become answer text.
2. Use `GoldenDatasetPath`, implement required suite/family completeness, threshold calculations, zone advisory rules and regression checks.
3. Fail closed on empty/skipped/error/REVIEW/WhatIf/missing-evidence and unsupported required families.
4. Replace superficial response-length canary with correlated agent response verification.
5. Produce all applicable artifacts, complete hashes and destination-byte validation; add provenance/UTC/role/cadence/runtime attestations.
6. Implement guardrail assignment/schema capture for the actual portal/API surface.
7. Validate Sentinel KQL against real tables/schemas/time windows; absent AgentId can include unrelated alerts. No query execution or clean detection result was asserted.
8. Validate repetitions and retain initial failures; no delivered `--repeat` support exists.

**Actual existing generator implementation limitations, flagged without unauthorized code mutation:**

- `scripts\compile_researcher_package.py` hard-codes Pillar 2 through 2.26 and omits 2.27. Successor local review package discovers current controls. Legacy omission is not caused by this issue.
- `scripts\extract_assessment_data.py` leaves a trailing Markdown separator in the last extracted verification criterion. Read-back exposed this existing parser behavior; no generated JSON hand-edit or script edit performed.
- Pre-build render-oracle mismatch is a build-order/context issue, not a demonstrated script defect. Parent must evaluate after mandatory build/globalSetup.

The shipped assessment engine/collectors and automation manifests were not changed. No evidence currently justifies calling their implementation defective because an illustrative documentation runner is incomplete.

## 9. Validation evidence and parent handoff

### 9.1 Executed by Linus

| Exact command/check | Outcome |
|---|---|
| `python scripts\verify_controls.py` | **PASS**, rerun after final edits: 79 controls/index/files; required structure/footers; four standard playbooks per control; documentation anchors valid |
| `python scripts\check_explorer_data_drift.py --check` | **PASS** |
| `python scripts\verify_xref_graph.py` | **PASS** after authorized follow-ups: 538 files / 6180 refs, no broken IDs or mislabeled references |
| `python scripts\verify_language_rules.py` | **PASS** after authorized follow-ups: 780 Markdown files scanned; existing declared quotation exceptions reported |
| `python scripts\verify_commercial_scope.py` | **PASS** after authorized follow-ups: 674 forward-facing files scanned |
| `git --no-pager diff --check` | **PASS**, final read-back |
| Existing generators listed in §7.1 | Outcomes recorded individually; failed pre-build render check not concealed |
| Generated assessment JSON read-back with `json.dumps(..., ensure_ascii=True)` | **PASS**, confirmed changed 2.20 criteria. Initial console read-back failed Windows cp1252 encoding on ≥; corrected ASCII-escaped output. Generator itself had passed |
| Workbook ZIP/XML inspection | **PASS**, all six workbook dispositions above |
| Persistent handoff inventory read-back | **PASS**, every one of 153 broad discovered tracked paths classified; no unclassified paths |
| Original retention-line comparison against local HEAD | **PASS**, literal `- Test evidence must be preserved per retention requirements (7+ years)` exists unchanged in both versions |
| Tenant/UI/API/Direct Line/Sentinel/runtime tests | **NOT RUN**, no authorized tenant access or shipped runner |
| Full build/test suites | **NOT RUN by Linus**, parent-owned to avoid concurrent build/suite execution |

### 9.2 Parent-reported independent evidence

These are parent reports, not Linus executions, and some preceded final name-only propagation.

| Exact reported command / gate | Reported outcome |
|---|---|
| `ruff check .` | PASS |
| `python -m pytest assessment\tests -q` | 492 passed |
| `npm test` | Initial missing Vitest failure; parent restored dependencies with `npm ci --no-audit --no-fund` (PASS); rerun 590 passed / 1 skipped |
| `python -m pytest scripts -q` | 1306 passed / 1 skipped |
| `python scripts\check_manifest_doc_drift.py --check` | PASS |
| `python scripts\generate_coverage_matrix.py --check` | PASS |
| `python assessment\manifest\generate_manifest.py --check` | PASS |
| `python scripts\check_automation_honesty.py --check` | PASS |
| `python scripts\verify_controls.py` | PASS on then-current source |
| `python scripts\verify_xref_graph.py` | PASS, 538 files / 6180 refs on then-current source |
| Language/commercial-scope/version-stamps/prose-counts gates | Parent reported PASS; exact invocations not supplied in messages, so not invented here |
| `npx --no-install playwright test --project=smoke --list` | FAIL: obsolete charter selector, repository only defines project `chromium`; do not modify configuration to satisfy stale selector |
| `mkdocs build --strict` | Parent reported **PASS** before final authorized evidence/1.21 follow-ups; final settled-source repetition remains parent-owned |
| `python scripts\verify_build_output.py site` | Parent reported mandatory site consumers **PASS** before final follow-ups; final repetition pending |
| `python scripts\verify_meta_tags.py site` | Parent reported mandatory site consumers **PASS** before final follow-ups; final repetition pending |
| `python scripts\verify_doc_links.py site --json _broken-links.json` | Parent reported mandatory site consumers **PASS** before final follow-ups; final repetition pending |
| `npm run test:e2e:smoke` | Parent reported **15/15 PASS**, after restoring missing Chromium in a session-only cache; no global browser installation or tenant evidence inferred |
| `python scripts\verify_excel_templates.py` | Parent reported **PASS**, all six downloads |
| `python scripts\verify_templates.py` | Parent reported **FAIL**, unrelated unchanged baseline: script line87 requires literal `Updated: April 2026`, while unchanged HEAD template line122 uses `Updated: [Month Year]`. Neither file modified; no out-of-scope fix |

### 9.3 Exact mandatory parent execution order

Source editing and generators are settled. Parent should now run:

1. `mkdocs build --strict`
2. `python scripts\verify_build_output.py site`
3. `python scripts\verify_meta_tags.py site`
4. `python scripts\verify_doc_links.py site --json _broken-links.json`

**No site consumer before the build.** Parent reported the mandatory build/consumers and documented smoke (15/15) passed before the authorized completion follow-ups, and will repeat the final build against the settled evidence/1.21 text. Inspect post-build render-oracle/globalSetup output. If the oracle changes, use its generator, never a hand-edit. Final evidence and the completed screenshot-specification correction belong in the parent's committed verification record.

## 10. Remaining unknowns and explicit scope limitations

- No tenant UI/screenshot evidence, licenses, permissions, model availability, API behavior, real safety results, real telemetry delay, immutable destination or runtime release gate was verified.
- Chat API and target-specific safety/red-team coverage are preview/restricted where stated; public availability was not inflated.
- Screenshot specification text alignment is completed under explicit same-task authorization. No screenshots were acquired; the literal “7+ years” retention conflict remains for the legal/records owner, not rewritten.
- Named automation remains unimplemented firm-owned work, not a shipped-script fix.
- Sentinel/KQL and abbreviated validators are not success-shaped runtime evidence.
- Full-byte integrity and runtime attestations cannot be established from an example hash manifest.
- Exact Agent 365 licensing/onboarding/agent-versus-model/alert-versus-BehaviorInfo and S25 audit-operation/record-type/correlation dependencies were checked and corrected in Control 1.21, its four artifacts and authorized text-only evidence checklist. Other sibling product/retention details were not independently certified; no full Control 1.8 or broad 1.21 rewrite was performed.
- Legacy compiler omission and extractor separator residue remain existing out-of-charter script limitations.
- Supplementary template validation has an unrelated unchanged baseline defect: hardcoded April 2026 versus the canonical template's Month Year placeholder. Neither template nor validator was changed.
- Parent's pre-follow-up build/site-consumer and 15/15 smoke results passed. Final settled-source build repetition remains parent-owned; earlier results do not certify that repetition.
- No persistent content graph exists to regenerate; indexes/catalog IDs/names/navigation/automation/manual manifest fields are unchanged. Only affected ignored assessment/reviewer outputs were refreshed.

## 11. PR-ready summary preserving repository template

The exact `.github\pull_request_template.md` was read. `Test-Path .github\PULL_REQUEST_TEMPLATE` returned False. This is a local draft, not a PR action. Headings, checklist items, ordering and HTML comment are preserved. The parent should check remaining boxes only after final validation and insert its exact final command outcomes.

---

## Description

Reverify Control 2.20's adversarial-testing walkthrough against live Microsoft Learn on 2026-11-06. Correct environment/solution transport, licensing, Copilot Chat API, Foundry evaluations/guardrails and telemetry claims; expose incomplete firm-owned automation. Propagate directly dependent implementation/testing/troubleshooting/reference corrections while preserving regulatory language. Historical tenant UI dates are not renewed.

## Type of Change

- [x] Documentation update (controls, playbooks, framework)
- [ ] New control or playbook
- [x] Bug fix (broken links, incorrect content)
- [x] Version/metadata update
- [ ] Infrastructure (CI/CD, templates, scripts)

## Checklist

- [ ] `mkdocs build --strict` passes with zero errors
- [x] `python scripts/verify_controls.py` passes (if controls were modified)
- [x] No prohibited language ("ensures compliance", "guarantees", etc.)
- [ ] Canonical role names used (per `docs/reference/role-catalog.md`)
- [x] Version footer updated if applicable (Month-Year)
- [x] CHANGELOG.md updated for notable changes

## Related Issues

Related: judeper/OceanSquad#911

## Additional Context

<!-- Any additional context, screenshots, or notes for reviewers -->

Documentation-based verification only; no tenant UI screenshots/runtime certification. Final source has 19 authorable Markdown changes including both authorized text-only evidence checklists and exact 1.21 Agent 365/audit-schema propagation; no engine/script/workflow/nav/binary edits by Linus. Downstream zone thresholds align to unchanged original walkthrough policy.

Validation:

- `python scripts\verify_controls.py` — passed after final edits.
- `python scripts\check_explorer_data_drift.py --check` — passed.
- `git --no-pager diff --check` — passed.
- `python scripts\extract_assessment_data.py` — passed, 79 controls, ignored output refreshed.
- `python scripts\compile_researcher_package.py` — passed; existing legacy omission of 2.27 flagged.
- `python scripts\build_review_package.py` — passed, local-only current-control package refreshed.
- Pre-build render-oracle check — failed for 147 absent generated role pages; all five 2.20 entries unchanged, unrelated churn restored; parent must verify after build.
- `python scripts\verify_xref_graph.py`, `python scripts\verify_language_rules.py`, `python scripts\verify_commercial_scope.py` — passed after authorized follow-ups.
- `mkdocs build --strict` and build-output/meta-tag/doc-link consumers — parent reported passed before final authorized follow-ups; final settled-source repetition pending in mandatory order.
- `npm run test:e2e:smoke` — parent reported 15/15 passed after session-only Chromium restoration.
- `python scripts\verify_excel_templates.py` — parent reported all six downloads passed.
- `python scripts\verify_templates.py` — parent reported unrelated unchanged baseline failure (hardcoded April 2026 versus Month Year placeholder); neither source changed.
- Parent independently reported Python/SPA/lint/data gates passed; final execution details belong in committed verification evidence.

Open boundaries: tenant UI evidence, unsupported/preview target coverage, firm-owned runtime patterns, Sentinel schema validation, legal-owner review of unchanged literal 7+ years retention, legacy compiler omission, existing extractor separator residue and unrelated baseline template-validator failure.

Full claim/source/downstream/generator evidence: this handoff, to be incorporated into the parent's committed verification record. No customer screenshots, secrets or remote actions.

## 12. Authorized completion follow-ups — precise discrepancy evidence

The same-task follow-up expressly authorized the text-only `EXPECTED.md` amendment and exact transition propagation through **Control 1.21 and its four implementation artifacts**. It did not authorize a broader Control 1.8 audit, regulatory revision, tenant work or executable implementation.

S27 was searched and fetched again through Microsoft Learn on 2026-11-06. It confirms:

- Copilot Studio / Foundry agent security requires Agent 365 eligibility from July 1, 2026; legacy Defender for Cloud Apps / Defender for Cloud licenses no longer cover those capabilities.
- Agent registry and observability underpin current agent inventory/security; the consolidated Security for AI Agents toggle must be checked.
- Defender for AI Services continues to support Foundry Models such as Azure OpenAI; this is not the agent entitlement.
- The transition names inventory tables `AIAgentsInfo` and `AgentsInfo`; actual schema must be validated.
- Agent 365 real-time protection audit/block rule alerts migrate to `BehaviorInfo`; threat-detection alerts are distinct. Existing Agent 365 Block rules require redefinition under the new policy experience.
- Copilot Studio real-time protection through Defender for Cloud Apps is separately described as unchanged; no blanket claim that every Defender alert becomes a behavior was made.

| Exact artifact | Contradiction found in targeted check | Surgical correction / retained boundary |
|---|---|---|
| Control 1.21 | Existing Agent 365 warning partly covered entitlement but used wrong table names, omitted BehaviorInfo and coexisted with universal synthetic-event model alert/incident expectations | Added source-cited onboarding/table/alert/behavior/model applicability and qualified those criteria; preserved regulatory sections and quarterly program |
| 1.21 portal walkthrough | Legacy preview Power Platform handshake treated as current prerequisite; wrong `AIAgentInfo` specimen, future “until July 1” text, fixed 30-minute diagnosis, universal 5–15-minute probe alerts and legacy evidence rows | Replaced exact obsolete onboarding/inventory instructions and repeated references, removed unvalidated specimen, separated actual supported model/M365/agent signal routes and unavailable evidence |
| 1.21 PowerShell setup | Subscription-plan and alert-only examples could imply complete agent security and migrated event capture | Source-cited model-only/Agent 365 boundary; explicitly no BehaviorInfo query/migration implementation, no empty-alert pass; executable snippets not rewritten |
| 1.21 verification/testing | Legacy DCA inventory prerequisite/DXR-02, alert-only DXR-01 and compensating preview Skip example implied satisfactory agent coverage | Require eligible Agent 365 onboarding/inventory and applicable alert/behavior evidence; adapt firm validator; unsupported/errored/missing-required evidence cannot pass |
| 1.21 troubleshooting | Silent-rule queries only covered legacy audit/alert tables; validation expected every red-team scenario to produce an incident | Added licensing/onboarding/BehaviorInfo diagnosis and applicability-qualified validation; historical March incident and regulatory/reportability prose retained |
| 2.20 EXPECTED.md | Quarterly Z3, 100+ recommended, pre-production when possible; missing precise technical evidence categories | Monthly Z3 and per-release predeployment/minimum100 isolated synthetic requirements aligned to unchanged walkthrough policy; licensed roles, transport/auth/connections, assigned guardrails/detected-versus-filtered, correlated bot replies, supported evaluations/telemetry and incomplete/failure evidence specified |

Original retention line was compared to local HEAD and remains byte-for-byte unchanged: `- Test evidence must be preserved per retention requirements (7+ years)`. Added an unresolved-conflict note without asserting any replacement period.

Post-follow-up commands: `python scripts\extract_assessment_data.py`, `python scripts\compile_researcher_package.py`, `python scripts\build_review_package.py`, `python scripts\gen_explorer_data.py`, `python scripts\verify_controls.py`, `python scripts\verify_xref_graph.py`, `python scripts\verify_language_rules.py`, `python scripts\verify_commercial_scope.py`, `python scripts\check_explorer_data_drift.py --check`, and `git --no-pager diff --check` all passed. Explorer semantic identity was asserted before restoring only its own generatedAt-only output; parent-owned generated version/render changes were not touched.

## 13. Final narrowly scoped audit/evidence completion

At the parent's local diff review, portal audit-pack row10 still required a withdrawn Power Platform handshake, and row12 still universally required legacy incident IDs. Both are now current: Agent 365 licensing/settings/registry-observability evidence, and applicable raw alert/behavior identifiers plus configured incident correlation. The same positive handshake assumptions in that portal's scope/matrix/final summary were corrected; explicit warnings that legacy handshakes are insufficient remain.

Authorized `docs\images\1.21\EXPECTED.md` now mirrors current Agent 365 licensing/onboarding/inventory and alert-versus-behavior/blocking-policy applicability. It specifies workload-appropriate audit payloads rather than a universal CopilotInteraction search. This remains a text-only specification; no tenant or screenshot verification occurred. Existing verification-focus/retention/regulatory wording was retained.

S25 was searched and fetched again live, with a bounded read of the same official Microsoft page's Operation/RecordType/Workload/AppIdentity/Messages/AgentId/AccessedResources table and auditing-billing section. The technical correction is **not** “replace all CopilotInteraction mentions.” Instead:

- Native Microsoft 365 Copilot examples remain scoped and unchanged where legitimate.
- Operation, record type, workload and AppIdentity are captured separately for the actual deployed experience.
- Custom/connected and other AI categories are not collapsed into CopilotInteraction for every Studio thread.
- Available message/agent/resource identifiers and documented confidence are used; ConversationId/ThreadId and field population are not universal requirements.
- Audit metadata is separate from prompt/response and detection evidence.
- Microsoft applications, including Studio custom applications, are included in Audit Standard; non-Microsoft auditing requirements are determined by the actual scenario, not every Studio agent or the record-category name alone.

| Artifact | Exact final correction |
|---|---|
| 1.21 control | Audit-plane/configuration/verification qualifiers remove the explicit EVERY Copilot Studio thread record assertion without changing regulatory clauses |
| 1.21 portal | Audit-pack rows10/12/16 and repeated handshake claims corrected; actual schema fields replace invented universal ThreadId/ContextResources population; native PowerShell search explicitly scoped |
| 1.21 PowerShell | Existing fixed CopilotInteraction example documented as native-only, incomplete multi-workload capture; missing/wrong-category output cannot prove clean evidence |
| 1.21 verification | UAL/DET/ZONE/NEG scoping, generic/illustrative audit assertions and correlation requirements qualified; supported workload metadata replaces every-prompt and universal ConversationId assumptions |
| 1.21 troubleshooting | Native filter example retained, with workload/category check before attributing empty results to ingestion delay |
| 1.21 EXPECTED | Current licensing/settings/registry-observability/inventory/alert-or-behavior and audit-schema evidence; no new tenant verification |

No executable code, architecture, unrelated controls or regulatory/retention policy was changed. A multi-file patch initially stopped at an exact-text mismatch; applied files were inspected, and only failed/remaining hunks were retried using the actual assertion text. Final guards passed.

After these final changes, `python scripts\extract_assessment_data.py`, `python scripts\compile_researcher_package.py` and `python scripts\build_review_package.py` passed and refreshed existing ignored copies. `python scripts\verify_controls.py`, `python scripts\verify_xref_graph.py` (538 files/6180 refs), `python scripts\verify_language_rules.py`, `python scripts\verify_commercial_scope.py`, `python scripts\check_explorer_data_drift.py --check` and `git --no-pager diff --check` passed. No full build/suite was run by Linus; parent was notified that sources/generators are settled for its final build.

Parent's supplementary `python scripts\verify_templates.py` failed because unchanged script line87 hardcodes `Updated: April 2026`, while unchanged HEAD `docs\templates\control-setup-template.md:122` uses `Updated: [Month Year]`. This is explicitly out of scope; neither file was changed. Parent's `python scripts\verify_excel_templates.py` passed all six tracked downloads.
