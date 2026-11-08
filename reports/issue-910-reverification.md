# Issue #910 — Vendor governance technical re-verification

**Last Verified:** 2026-11-06

**Target:** `docs\playbooks\control-implementations\2.7\portal-walkthrough.md`

**Method:** Live official Microsoft documentation search/fetch and release-communications read tools; local document review, generators, offline syntax parsing and repository validation. No delegated agents.

## Boundary and adversarial conclusions

The governing constraints were: “NEVER run gh, GitHub APIs, inspect/recover/request/set authentication or credentials, git push/send-pack, or any remote mutation”; “Do not switch branches or create worktrees”; “Do not delegate further”; and “Do not modify unrelated team state, histories, workflows, scripts, assessment code, or regulatory wording.”

Only documentation and this evidence report are committed locally. No tenant UI, screenshots, browser sessions, protected STP downloads, administrative API calls, authentication, policy changes or remote operations were performed. Historical **Last UI Verified** dates remain historical; targeted November documentation checks do not certify UI currency. Regulatory wording/mappings, approval criteria and contractual minimums were not reassessed.

The original walkthrough could generate false assurance in three ways: treating partial inventory as complete, treating a protocol/publisher as a vendor/contract identity, and treating configured policy or empty telemetry as demonstrated enforcement. The correction deliberately requires separate completeness and execution evidence.

| Assumption | Strength | Failure mode / treatment |
|---|---|---|
| Official documentation establishes the supported product contract | Strong for documented scope; not tenant behavior | Cite primary pages; distinguish source statements from executed tests |
| Documented controls are deployed in every tenant/server/workload | Moderate to weak | Rollout, role, region, preview and server-type differences remain; require tenant verification |
| Connector publisher identifies the service operator/model contract | Rejected | Microsoft-published connectors can reach third-party services; record destination and route separately |
| A single connector CSV or successful empty response proves inventory completeness | Rejected | HTTP, classic chatbot, flow/app-type and visibility gaps require reconciliation |
| Purview Audit captures all MCP calls, custom events and request/response payloads | Rejected | Validate configured agent/server logging, identity, redaction and retention; no log is not no call |
| Native model selection means GA and identical Microsoft terms/residency | Rejected | Model-specific tags/retirement and Anthropic retention-route exception require separate evidence |
| Default-deny classifications alone exclude every unapproved downstream host | Weak | Dynamic hosts and shared servers require trusted producers, access review and execution evidence |

**Trade-offs:** Raw JSON is less convenient than fabricated normalized inventory but preserves the actual evidence contract. Mixed-mode DLP prevents loss of classic coverage but increases policy reconciliation work. Turning MCP **Allow all** off reduces unsolicited new-tool exposure but can require explicit approval when vendors add useful tools. Failing to make these changes preserves convenient dashboards while hiding unsupported coverage.

## Discrepancies and original line evidence

Line numbers below refer to the pre-change local `HEAD` version inspected with `git show HEAD:<path>`, not the corrected file.

| Severity | Original artifact / lines | Defect and disposition | Primary basis |
|---|---|---|---|
| High | `docs\playbooks\control-implementations\2.7\portal-walkthrough.md:13,17` | Universal connector/plugin telemetry and “read-only or policy-additive” safety were unsupported. Separate configured execution evidence and change-control policy mutations. | S5, S15 |
| High | Same file `:23–38` | Resources/Analytics rails, Custom/Independent tabs and three-workload connector export implied complete inventory. Correct Manage inventory/products routes, 28-day limits, no-download Power Apps connector report and explicit inventory gaps. | S1–S4 |
| High | Same file `:63–70` | Conflated environment by-name custom rules with tenant Host URL rules, ignored final wildcard default and invented security-group DLP/Policy effects. Correct policy scope, precedence, visibility and dynamic-host caveats. | S5–S7 |
| High | Same file `:76,84–88` | Wrong primary-model navigation; blanket April GA/uniform provider terms and combined tenant GenAI/CMK/crossgeo controls. Correct Overview → Model and separate route/control planes. | S10–S14, S18 |
| High | `docs\playbooks\control-implementations\2.7\powershell-setup.md:18,43,86–97` | Wrong Graph module, silent failed inventory, reversed Business codes and assumed embedded URL rules. Correct read commands; retain raw responses and separate Host URL reads. | S6, S16, S17 |
| High | `docs\playbooks\control-implementations\2.7\troubleshooting.md:15,30,62,83–84` | Less-restrictive-policy explanation, fabricated operation/automatic-alert contract and Policy effects route. Replace with actual scope/classification, supported telemetry and tested delta process. | S5–S9 |
| High | `docs\controls\pillar-2-management\2.7-vendor-and-third-party-risk-management.md:84–89` | Anthropic “first-party,” blanket ChatGPT-5/Claude GA, and nonnative MCP assertion. Correct route-specific subprocessor/independent-processor terms and native Microsoft MCP support. | S8, S10–S12 |
| High | `docs\controls\pillar-1-security\1.4-advanced-connector-policies-acp.md:100,167,197` | Repeated false MCP distinction, universal custom-server March/April dates and security-group scope premise. Propagate supported scope and capability-specific availability. | S5–S9, R1–R2 |
| Medium | `docs\reference\service-trust-portal-attestation-guide.md:25,55–60,76` | Any-signed-in access, stale menu/filter labels and first ISO 42001 cycle “in progress.” Correct eligible-account/NDA/restricted roles and current report availability/scope. | S19–S20 |
| High | Downstream 1.5 / 2.17 MCP criteria and telemetry | Individual-tool ACP/DLP and automatic custom-event/UAL capture conflated separate planes. Distinguish supporting connector DLP, ACP server block, maker toggles and rolling-out Agent 365 tooling controls. | S7–S9, S15, S21–S22 |
| High | Downstream 2.24 MCP/custom connector instructions | Every MCP assumed non-Microsoft; generic allowlist/Custom plugins toggle and universal ACP coverage were unsupported. Correct actual registered-server/connector/agent controls and evidence checklist. | S6–S9, S21–S22 |

## Live primary-source ledger

All sources below were searched/fetched during this task on 2026-11-06; availability statements were not inferred from memory.

| ID | Live URL | Relevant facts used |
|---|---|---|
| S1 | https://learn.microsoft.com/en-us/power-platform/admin/analytics-powerapps | Manage → Products → Power Apps; canvas apps, max 28 days, about 24-hour refresh; Connectors report ownership limitation/no download |
| S2 | https://learn.microsoft.com/en-us/power-platform/admin/analytics-flow | Manage → Products → Power Automate; max 28 days, refresh, solution-aware/desktop exclusions, visual export |
| S3 | https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory | Manage → Inventory, resource Details/Connectors, Download, roles and classic chatbot boundary |
| S4 | https://learn.microsoft.com/en-us/power-platform/admin/inventory-schema | GA connector reference fields; built-in HTTP/tabular/app-type gaps; catalog attributes differ from resource ownership |
| S5 | https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention | Microsoft MCP connectors; ACP excludes virtual connectors; mutations can suspend/quarantine/disable; full enforcement up to 24 hours |
| S6 | https://learn.microsoft.com/en-us/power-platform/admin/dlp-custom-connector-parity | Environment names versus ordered tenant Host URLs; final Ignore wildcard; name precedence/visibility/dynamic hosts; Confidential=Business, General=Non-business; separate GUID-based URL pattern reads |
| S7 | https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss | Tenant/environment policy scope and precedence; publisher versus service owner |
| S8 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent | Native Microsoft/custom MCP; Tools → Add a tool → MCP; Allow all starts on, newly added tools default off after it is off |
| S9 | https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies | Certified/action allowlist; MCP server-level only; custom/HTTP/virtual exclusions; mixed/ACP-only; workload rollout and nonblockable connector Managed Environment requirement |
| S10 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model | Primary Overview → Model; per-model GA/preview/experimental, region, retirement/fallback |
| S11 | https://learn.microsoft.com/en-us/copilot/implement/connect-to-ai-subprocessor | Covered Anthropic subprocessor routes versus separately opted-in Anthropic models with Data Retention/independent processor/Anthropic terms |
| S12 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-external-response-model | Separate externally hosted providers, access and terms; not identical native/provider treatment |
| S13 | https://learn.microsoft.com/en-us/power-platform/admin/allow-llm-generative-responses | Microsoft 365 provider access plus separate PPAC environment/group external/preview controls |
| S14 | https://learn.microsoft.com/en-us/power-platform/admin/geographical-availability-copilot | Environment Generative AI features; US checkbox absence and model-specific movement limitations |
| S15 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry | Settings → Advanced/Application Insights; configurable conversation/sensitive-content logging, not universal Purview payloads |
| S16 | https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminpowerappconnector?view=pa-ps-latest | Authorized custom connector enumeration, not complete prebuilt catalog/usage |
| S17 | https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.devices.serviceannouncement/get-mgserviceannouncementmessage?view=graph-powershell-1.0 | Microsoft.Graph.Devices.ServiceAnnouncement, ServiceMessage.Read.All, -All |
| S18 | https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key | CMK is a separate enterprise policy/configuration |
| S19 | https://learn.microsoft.com/en-us/compliance/assurance/stp-get-started | Eligible organizational account/NDA/license, restricted document permissions, current menu/search and report access |
| S20 | https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-42001 | Current Microsoft certificates/audits and service scope including Copilot Studio; not universal external-provider coverage |
| S21 | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-tools-overview | Agents → Tools → Registry; block/unblock; connector usage preview visibility, not connector management |
| S22 | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-plugins-skills-mcp-servers | Publisher categories, plugin user availability, MCP request approval + consent; separate server block; supported server-type tool controls rolling out through Tooling Gateway |
| S23 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention | Connected MCP restrictions and actual maker/publish violations; no guaranteed universal Purview runtime operation |
| S24 | https://learn.microsoft.com/en-us/power-platform/admin/environments-overview | Environment Maker includes custom connector creation; default environment broad maker access |
| S25 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agent-tools | Microsoft/third-party MCP and upstream changes without agent republish |
| S26 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server | SDK server creation is distinct from connecting an existing server; no universal March/April date inferred |
| S27 | https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering | Separate classic connector configuration evidence |
| S28 | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-byo-mcp-server | BYO registered-server experience carries its own preview boundary |

Release-communications full-item read-back:

- **R1:** https://www.microsoft.com/en-us/microsoft-365/roadmap?id=562221 — “Use MCP-compliant tools in agent workflows,” **Launched**, Preview May 2026 / GA June 2026.
- **R2:** https://www.microsoft.com/en-us/microsoft-365/roadmap?id=570433 — interactive **MCP Apps**, **In development**, Preview October / planned GA November 2026. A planned month is not proof of launch on November 6.
- These are distinct capabilities; neither establishes universal custom-server March/April GA.

**Source uncertainties:** The live model matrix contained GPT-5 Chat's November 12 retirement and a GPT-5.5 GA/October 31-retirement inconsistency. No static model list/date was copied. The flow analytics article has inconsistent desktop wording; the published exclusion is used and completeness is not claimed. Large CMK/BYO fetches were truncated by the tool; only corroborated high-level separate-policy/preview facts were used. Failed old STP/Graph URLs were replaced by searched current pages, not repeatedly retried. No protected content or third-party service was used for research.

## Downstream disposition ledger

Brace lists below enumerate each concrete path (not wildcard sampling). Review is limited to the corrected dependency/claim, not certification of unrelated sections.

### Changed

| Paths | Reason |
|---|---|
| `docs\controls\pillar-2-management\2.7-vendor-and-third-party-risk-management.md` | Parent source: provider/MCP identity, supported controls, targeted metadata/citations |
| `docs\playbooks\control-implementations\2.7\{portal-walkthrough,powershell-setup,verification-testing,troubleshooting}.md` | Full target/implementation/test/evidence propagation |
| `docs\images\2.7\EXPECTED.md` | Actual inventory, policy, maker, model and tool evidence; local-only screenshots |
| `docs\controls\pillar-1-security\{1.4-advanced-connector-policies-acp,1.5-data-loss-prevention-dlp-and-sensitivity-labels,1.29-global-secure-access-network-controls}.md` | Repeated scope/MCP tool-plane claims; 1.29 only clarifies MCP dependency, not GSA feature verification |
| `docs\playbooks\control-implementations\1.4\{portal-walkthrough,verification-testing,troubleshooting}.md` | Security-group/service-principal misconception, MCP status and fabricated runtime evidence |
| `docs\controls\pillar-2-management\2.6-model-risk-management-sr-26-2.md` | Model selection source/route and exposed-version boundary |
| `docs\playbooks\control-implementations\2.6\{portal-walkthrough,troubleshooting}.md` | Primary model path, terms and supported provider restrictions; organizational approval register, not invented model-name gate |
| `docs\images\2.6\EXPECTED.md` | Actual model evidence, not invented Model activities audit filter |
| `docs\controls\pillar-2-management\2.17-multi-agent-orchestration-limits.md` | Repeated MCP dates, per-tool DLP/ACP and universal UAL expectations |
| `docs\playbooks\control-implementations\2.17\{portal-walkthrough,powershell-setup,verification-testing,troubleshooting}.md` | Connector/server/tool-plane propagation; custom telemetry distinguished from native audit schema |
| `docs\images\2.17\EXPECTED.md` | Current MCP/telemetry evidence boundary |
| `docs\playbooks\control-implementations\2.24\portal-walkthrough.md`, `docs\images\2.24\EXPECTED.md` | Universal non-Microsoft MCP and generic connector/plugin switches; supported registered-server/connector/agent evidence |
| `docs\playbooks\advanced-implementations\mcp-server-governance\index.md` | Native/custom/registered routes, policy gaps, no fabricated mutation IDs; actual telemetry/network applicability |
| `docs\reference\service-trust-portal-attestation-guide.md` | Access/menu/report availability and current primary link |
| `CHANGELOG.md`, `reports\issue-910-reverification.md` | Outcome/review evidence; no unrelated release-history rewrite |

### Reviewed, unchanged implementation and evidence dependencies

- `docs\controls\pillar-2-management\2.1-managed-environments.md` and `docs\playbooks\control-implementations\2.1\{portal-walkthrough,powershell-setup,verification-testing,troubleshooting}.md`: related Managed Environment, role/sharing, CMK and vendor-review references; no generic custom connector creation switch relied on by the corrected 2.7 guidance. Broader isolation/Lockbox claims are outside this targeted review.
- `docs\playbooks\control-implementations\1.4\powershell-setup.md`: existing supported API/read-back distinction; not the false custom-connector collector. No executed API verification.
- `docs\playbooks\control-implementations\1.5\{portal-walkthrough,powershell-setup,verification-testing,troubleshooting}.md`: actual DLP/evidence procedures and vendor escalation references, not the repeated MCP server/tool equivalence corrected in the control.
- `docs\playbooks\control-implementations\2.6\{powershell-setup,verification-testing}.md`: underlying-model/advisory/manual evidence contracts do not certify uniform provider terms; retained. No execution or broad API certification.
- `docs\images\{1.4,1.5,2.1}\EXPECTED.md`: inspected relevant policy/role/evidence entries; no repeated erroneous 2.7 creation-switch/model path needing correction. Existing UI dates not renewed.
- `docs\playbooks\control-implementations\2.24\{powershell-setup,verification-testing,troubleshooting}.md`: reviewed MCP reader/test/containment sections. Their `Get-Feat224*`/`Get-Agt*` wrappers and beta endpoint assumptions are legacy/custom illustrative contracts, not verified native Microsoft collectors. No new platform API artifacts were authored to make them runnable. Current supported MCP procedure is the corrected portal guide; these helpers must not be taken as complete native inventory/enforcement evidence. Broader helper verification remains a separate limitation.
- `docs\playbooks\regulatory-modules\supply-chain-risk-register-entry.md`: reviewed full template; already asks actual provider, subprocessors, residency and logging unknown/configurable status. Organizational requirements retained.
- `docs\reference\evidence-standards.md`: vendor questionnaire/contract evidence is organizational and consistent; no universal tool telemetry claim in the 2.7 row.
- `docs\playbooks\_shared\powershell-baseline.md`: module/mutation/evidence baseline reviewed; existing Power Apps 2.0.198 pin retained, not newly tenant-certified. Graph version is explicitly CAB-selected.

### Reviewed, unchanged links/catalogs/mappings

These carry links, mappings or organizational vendor approvals rather than the corrected product assertions:

- `docs\controls\{CONTROL-INDEX,index}.md`; `docs\controls\pillar-2-management\index.md`
- `docs\controls\pillar-1-security\{1.22-information-barriers,1.8-runtime-protection-and-external-threat-detection}.md`
- `docs\controls\pillar-2-management\2.27-consumption-entitlement-governance.md`
- `docs\framework\{agentic-capability-drivers,executive-summary,regulatory-framework}.md`
- `docs\playbooks\control-implementations\index.md`
- `docs\playbooks\governance-operations\governance-operating-calendar.md`
- `docs\playbooks\control-implementations\1.8\powershell-setup.md`
- `docs\playbooks\control-implementations\1.7\powershell-setup.md`
- `docs\playbooks\control-implementations\2.5\powershell-setup.md`
- `docs\playbooks\control-implementations\2.25\{troubleshooting,verification-testing}.md`
- `docs\playbooks\control-implementations\2.27\{portal-walkthrough,powershell-setup}.md`
- `docs\playbooks\control-implementations\2.9\troubleshooting.md`
- `docs\playbooks\control-implementations\3.1\portal-walkthrough.md`
- `docs\playbooks\control-implementations\4.7\powershell-setup.md`
- `docs\reference\{assessment-coverage,cco-quick-reference,compliance-manager-templates,examiner-first-day-letter-response,iso-42001-mapping,license-requirements,microsoft-cape-crosswalk,microsoft-rai-v2-mapping,nist-ai-rmf-crosswalk,owasp-llm-top10-crosswalk,pattern-coverage,regulatory-mappings,solutions-coverage-gaps}.md`

Some existing inline “2.7” references mean change-management/ALM, or a document subsection, rather than vendor Control 2.7. They were classified, not silently repaired as a regulatory/cross-reference audit. Numeric subsection/version hits in advanced labs and 1.11/1.14/1.19/1.21/1.9/2.12/2.20/2.24/2.25/2.26/2.27/2.5/3.1/3.4/3.6/3.9/4.7 playbooks are not independent vendor dependencies. Mermaid vendor numeric coordinates and package/version references were excluded.

Claim searches additionally reviewed `docs\reference\work-iq-governance.md`, `docs\playbooks\control-implementations\3.8\portal-walkthrough.md`, and `docs\playbooks\control-implementations\3.9\{portal-walkthrough,troubleshooting}.md`: specific Work IQ/Sentinel/server-authoring previews are not the universal MCP GA assertion and were not re-dated. No broad preview/license audit is claimed.

### Machine-readable and historical artifacts

- `assessment\manifest\generate_manifest.py`, `assessment\manifest\controls.json`: 2.7 is manual-only, no checks/collection methods/evidence automation. Its organizational vendor question and links remain correct; no manifest or generator source edits.
- `scripts\extract_assessment_data.py`, `scripts\generate_excel_templates.py`, `scripts\update_excel_templates.py`: reviewed control-ID/title references; catalog/questionnaire paths and control count unaffected. No functional code or downloads changed.
- `scripts\gen_explorer_data.py`, `docs\javascripts\control-explorer-data.json`: regenerated; only `generatedAt` differed, restored timestamp-only noise.
- `scripts\gen_change_radar_data.py`, `data\change-radar\items.json`, `docs\javascripts\change-radar-data.json`: vendor-review rationale still correct; regenerated, only `generatedAt` differed, restored timestamp-only noise.
- `mkdocs.yml`, `scripts\verify_xref_graph.py`: reviewed nav/validation contract; unchanged paths/control count, validation passes.
- `docs\version.json`: the build rewrites its commit SHA/build timestamp; restored this unrelated build-only change before staging.
- No tracked `build_content_graph.py` exists; no substitute tooling created.
- `releases\CHANGELOG-archive\CHANGELOG-v1.3.md`, `reports\issue-821-reverification.md`, and `reports\monitoring\learn-changes-{2026-03-11,2026-04-28,2026-06-23,2026-07-12,2026-08-28,2026-09-22,2026-10-16,2026-10-17}.md`: historical provenance/link hits, deliberately unchanged.
- `data\monitor-state.json` and `data\monitor-pending\learn\learn.microsoft.com-en-us-microsoft-365-copilot-microsoft-365-copilot-privacy-{5b5180a9faa3df5c35c850da,6901fb9b97edbbf91f157c17,8685fd30a74366b95b13a929}.json`: historical source snapshots, not authored guidance; preserved.

## Independent revision (2026-11-07) — coverage-limit and response-envelope corrections

An independent reviewer rejected the original head `6037a934d32f833ac77fe9a6b92bcec4912dcdbb` because the 2.7 PowerShell guidance omitted documented cmdlet limits and assumed an unwrapped `Get-DlpPolicy` list. The revision (markdown only; no module install/import/execution, tenant, Graph or admin API call) corrects:

- **`Get-AdminPowerAppConnector`** does not list custom connectors that are in a solution ([Power Platform PowerShell support](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell)). The export is labelled partial, and reconciliation with solution contents and portal inventory is required.
- **`Get-DlpPolicy`** shows connector display names as of policy creation or last move within the policy, and omits **new** default-group connectors that were never moved (same source). The default group is not necessarily Non-business; counts are labelled "Returned". No connector-moving workaround is added to the read-only collector.
- **List envelope.** Static review of `Microsoft.PowerApps.Administration.PowerShell` 2.0.198 (list route returns the REST helper's aggregated object with a `value` collection) and Microsoft's administration sample (`.Value`) shows the list form is an envelope. The example now enumerates `.Value` and throws on a missing/null `Value` or a policy without `connectorGroups`; an empty `Value` warns and is not treated as proof of no policies. `Get-AdminDlpPolicy` (different endpoint and projection) is not substituted.
- **Unverified fields.** `environmentType`, `createdTime` and `lastModifiedTime` support exists only for policy-creation responses in the official sample; they are kept as columns with an explicit not-established qualification and no invented replacements.

Limits: evidence is documentation plus a downloaded, inert 2.0.198 package/sample read; the limitations and the envelope were not reproduced in a tenant, the scripts were not run against the real module, and paging, scope-specific URL-pattern behavior and field presence remain unverified. The "Last Verified" dates and Needs Review UI status of the pages are not renewed. The proposed PR body below is the original and is superseded by the revised PR description.

## Generators and validation

Commands executed from repository root with `PYTHONIOENCODING=utf-8`. Existing installed tools were available; no dependencies installed or restored.

| Exact command | Result / output |
|---|---|
| `python scripts\gen_explorer_data.py` | Passed, exit 0; 79 controls, 318 playbook links; `docs\javascripts\control-explorer-data.json` semantically unchanged |
| `python scripts\gen_change_radar_data.py` | Passed, exit 0; 31 feed items; `docs\javascripts\change-radar-data.json` semantically unchanged |
| `python scripts\compile_researcher_package.py` | Passed, exit 0; four ignored `maintainers-local\researcher-package\0{1,2,3,4}-Pillar-*-Controls.md` outputs. Existing compiler log stops Pillar 2 at 2.26; no completeness certification or functional-script repair |
| PowerShell AST `Parser::ParseInput` on each target setup fence | Passed; 5 fenced blocks, 0 syntax errors; no imports/authentication/API execution |
| `mkdocs build --strict` | Passed, exit 0 |
| `python scripts\verify_build_output.py site` | Passed; expected site artifacts present |
| `python scripts\verify_meta_tags.py site` | Passed; 8 required tags on sampled pages |
| `python scripts\verify_doc_links.py site --json _broken-links.json` | Passed; 697 pages, no broken internal links |
| `python scripts\verify_controls.py` | Passed, exit 0 |
| `python scripts\verify_xref_graph.py` | Passed; 538 files, no broken IDs/mislabels |
| `python scripts\check_manifest_doc_drift.py --check` | Passed; 79 IDs across all three sources |
| `python scripts\check_explorer_data_drift.py --check` | Passed |
| `python scripts\check_change_radar_data_drift.py --check` | Passed |
| `python scripts\check_faq_jsonld_drift.py --check` | Passed; 63 questions |
| `python scripts\generate_coverage_matrix.py --check` | Passed |
| `python scripts\verify_language_rules.py` | Passed |
| `python scripts\verify_commercial_scope.py` | Passed |
| `python scripts\verify_learn_urls_count.py --check` | Passed; existing table count within tolerance |
| `python scripts\verify_version_stamps.py --check` | Passed |
| `python scripts\verify_prose_counts.py --check` | Passed |
| `python scripts\verify_solutions_docs.py --check` | Passed |
| `python scripts\verify_regulatory_naming.py --check` | Passed |
| `git diff --check` | Passed |

The four mandatory build commands were rerun successfully on the final documentation in their prescribed order, followed by all fourteen requested documentation/drift gates (all exit 0). The final internal-link scan covered 697 pages without broken links. A local comparison of all six modified controls confirmed unchanged regulatory rationale, zone requirements, roles, Regulatory Reference and historical Last UI Verified metadata. `git diff --check` passed. `_broken-links.json` is a named local check output and is removed before handoff. Ignored site/homework/package outputs and existing dependencies/customer data are not staged. Python/SPA suites and tenant enforcement tests were not run for this documentation-only change.

## Proposed PR body (parent-owned; no PR created)

```markdown
## Description

Resolve #910 vendor-governance technical drift against live Microsoft documentation checked on 2026-11-06. Correct inventory/navigation, DLP/custom connectors, MCP control planes, model/provider terms and STP/evidence guidance; propagate to linked implementations and checklists. Documentation-only verification, not UI or compliance certification.

## Type of Change

- [x] Documentation update (controls, playbooks, framework)
- [ ] New control or playbook
- [x] Bug fix (broken links, incorrect content)
- [x] Version/metadata update
- [ ] Infrastructure (CI/CD, templates, scripts)

## Checklist

- [x] `mkdocs build --strict` passes with zero errors
- [x] `python scripts/verify_controls.py` passes (if controls were modified)
- [x] No prohibited language ("ensures compliance", "guarantees", etc.)
- [x] Canonical role names used (per `docs/reference/role-catalog.md`)
- [x] Version footer updated if applicable (Month-Year)
- [x] CHANGELOG.md updated for notable changes

## Related Issues

Closes #910

## Additional Context

<!-- Any additional context, screenshots, or notes for reviewers -->

Evidence: reports/issue-910-reverification.md. `mkdocs build --strict`, `python scripts/verify_controls.py`, `python scripts/verify_build_output.py site`, `python scripts/verify_meta_tags.py site`, and `python scripts/verify_doc_links.py site --json _broken-links.json` passed; all requested documentation/drift gates passed. Both data generators passed with timestamp-only differences restored; researcher package regenerated locally. No tenant/UI/API execution. Agent 365 granular tool controls remain rollout/server-type-specific; legacy custom helper contracts outside the corrected MCP procedure are not newly certified. Regulatory wording and mappings unchanged.
```
