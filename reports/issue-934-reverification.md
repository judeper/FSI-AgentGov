# Issue #934 - Model-risk verification technical re-check

**Last Verified:** 2026-11-09

**Target:** `docs\playbooks\control-implementations\2.6\verification-testing.md`

## Scope and evidence boundary

Live Microsoft Learn search/fetch, repository-wide reference discovery, linked-document review, local generators, offline PowerShell checks, and documentation validation were used. This is a technical-accuracy review, not a regulatory determination. Regulatory mappings, retention periods, governance approval requirements, and regulatory interpretations were not reassessed.

No tenant authentication, administrative API call, UI session, screenshot capture, policy mutation, or live collector execution occurred. Historical April/May UI-verification dates are preserved; the new date explicitly identifies a documentation review. UI verification remains **Needs Review**. No GitHub/authentication operation, remote write, push, pull request, issue update, or delegation was performed. The trusted parent owns publication and remote handoff.

The supplied PowerShell remains an illustrative, incomplete implementation: unsupported inventory and Foundry adapters fail explicitly with `Error` / `ManualEvidenceRequired`. This change does not implement a production inventory collector, signed evidence assembler, approval system, or archival pipeline.

## Discrepancies corrected

| Finding | Technical correction and propagation | Primary sources |
|---|---|---|
| Purview, CoE, Agent 365, and sample scripts implied an exhaustive tenant model inventory | Require bounded exports and reconciliation with the firm's authoritative register. Purview is supported activity evidence; CoE has coverage/maintenance limitations; Agent 365 coverage and fields vary. Unknown model snapshots remain explicit unknowns. | S1-S5, S12-S13 |
| `Get-AdminBot`, a generic Graph inventory route, and `Get-AzMLWorkspaceJob -ResourceId` were treated as implemented collectors | Remove unsupported adapter bodies rather than normalize invented responses. Azure ML job listing is not a Foundry evaluation-result contract. Persist explicit collection failures in diagnostic packages; prevent missing model names from matching every change notice. | S12-S14, S24 |
| Native Agent 365 security templates were described as a model-risk schema/approval/retention system | Separate supported security-policy bundles and request handling from firm-defined model fields, evidence approval, manifests, signatures, retention binding, and channel-specific release controls. No universal cross-channel deployment block is claimed. | S3-S7 |
| Blanket Microsoft 365 Copilot/E5 prerequisites were attached to unrelated capabilities | Use Agent 365 per-user/feature entitlements, distinguish Entra Agent ID base from extended security, and distinguish Audit Standard search/export from Premium capabilities. Provider and environment controls remain separately scoped. | S3, S15, S23, S25 |
| Monitoring navigation, feedback ownership, retention windows, and coverage were conflated | Use the Copilot Studio **Monitor** page; distinguish up-to-360-day analytics, 28-day session details/transcript UI, and separately configured Dataverse retention. Exclude test-panel traffic and failed triggers that never create a session. Customer-comments summary is a Copilot Studio preview, not a Purview feature. | S1-S2 |
| Foundry evaluation names implied uniform GA availability and numeric outputs | Task Completion, Intent Resolution, and Task Adherence are identified as preview; Tool Call Accuracy is not labeled preview on the cited evaluator page. Preserve native numeric/binary/categorical results and evaluator input applicability; skipped is not passed. Monitoring requires configured instrumentation/evaluation collection. | S8-S10 |
| Evidence tests relied on a fictional per-item `deletionLocked` property | Verify the actual applied label, record/lock state, retention start/duration, and observed operation. Ordinary retention may preserve a copy without blocking working-item deletion. Distinguish item protection from policy-level Preservation Lock. Propagate to 1.11, 1.12, 3.4, 3.6, and the examiner-response guide. | S16-S19 |
| The shared Control 1.9 instructions used `RetentionComplianceLockType` | Correct the documented setter to `-RestrictiveRetention $true` and read-back property to `RestrictiveRetention`. Reconcile every expected policy rather than filtering missing/unlocked policies away. Preserve approval/confirmation gates, add failed-read-back errors, and document adaptive-scope and regulatory-record-label eligibility limits. | S17 |
| Shared retention tests treated metadata timestamps as expiration clocks and irreversible extension as revertible | Identify label-written time accurately; do not manipulate it as a supported test clock. Preserve the dedicated-test-policy restriction and explicitly state that an increased locked-policy retention period cannot be reverted. | S16-S17 |
| A local folder/hash manifest and an assessment-engine report were treated as finalized MRM evidence | Mark local packages diagnostic/incomplete; label application, item-level evidence, approval/signing, migration-integrity checks, retention handoff, and completeness reconciliation remain separate. Control 2.6 is manual in the engine; its report is not an automatically collected model inventory/validation package. | S16-S19; reproducible manifest |

### Assumptions and unresolved boundaries

Official documentation establishes the supported contract, not execution in this tenant. Preview, rollout, region, licensing, channel coverage, exposed model identifiers, and actual policy distribution must still be checked in the implementation tenant. The live model-selection page contains changing model status/date information; this change deliberately does not freeze a model catalog or promise an unexposed snapshot.

The source's firm-defined thresholds, approval chains, six-year evidence minimum, and attestation periods remain governance requirements, not newly attributed native Microsoft features. Unsupported capabilities must produce a recorded gap, not an empty success.

Related Control 2.25 is an **upstream** dependency, not a reverified deliverable: it still contains older broader licensing, registry-completeness, and native-template assumptions. Its four companion guides were inspected for that boundary; their complete product contracts were not recertified here. The corrected 2.6 guides explicitly scope inventory, licensing, templates, and approvals rather than inheriting those assumptions. A separate targeted 2.25 re-verification is warranted; this report must not be used to certify that control.

## Sources

All Microsoft product findings above were grounded in live official Learn search/fetch. No third-party product summaries were used as authority.

| ID | Microsoft Learn URL |
|---|---|
| S1 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview |
| S2 | https://learn.microsoft.com/en-us/purview/ai-copilot-studio |
| S3 | https://learn.microsoft.com/en-us/microsoft-agent-365/overview |
| S4 | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-registry-overview |
| S5 | https://learn.microsoft.com/en-us/power-platform/guidance/coe/power-bi-monitor |
| S6 | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/policy-template |
| S7 | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-requests |
| S8 | https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/built-in-evaluators |
| S9 | https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/observability |
| S10 | https://learn.microsoft.com/en-us/azure/ai-foundry/observability/how-to/how-to-monitor-agents-dashboard |
| S11 | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-settings |
| S12 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle |
| S13 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model |
| S14 | https://learn.microsoft.com/en-us/powershell/module/az.machinelearningservices/get-azmlworkspacejob |
| S15 | https://learn.microsoft.com/en-us/entra/agent-id/what-is-agent-id-platform |
| S16 | https://learn.microsoft.com/en-us/purview/records-management |
| S17 | https://learn.microsoft.com/en-us/purview/retention-preservation-lock |
| S18 | https://learn.microsoft.com/en-us/purview/create-apply-retention-labels |
| S19 | https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-compliancetag?view=exchange-ps |
| S20 | https://learn.microsoft.com/en-us/purview/ai-microsoft-purview |
| S21 | https://learn.microsoft.com/en-us/purview/ai-microsoft-purview-permissions |
| S22 | https://learn.microsoft.com/en-us/copilot/implement/connect-to-ai-subprocessor |
| S23 | https://learn.microsoft.com/en-us/power-platform/admin/allow-llm-generative-responses |
| S24 | https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/interaction-export/aiinteractionhistory-getallenterpriseinteractions |
| S25 | https://learn.microsoft.com/en-us/purview/audit-solutions-overview |

S24 documents a user-scoped application-permission interaction export, not a tenant model inventory; Copilot Studio is excluded. S22 distinguishes the covered Claude subprocessor route from the separately opted-in Anthropic data-retention/independent-processor route. Existing provider-routing caveats were retained after verification. Release-communications lookup was not needed: the current feature-specific Learn pages supplied the relevant availability contracts.

## Downstream artifacts reviewed

Discovery searched control identifier/title, source links, and repeated product claims, not only the stale marker. The direct Markdown reference sweep found **94 documentation paths**; their matching contexts were reviewed. Additional linked dependencies and repeated retention claims were reviewed separately below. A further 39 tracked Markdown hits were historical/procedural provenance, not current implementation guidance.

In the following tables, filenames are relative to the stated prefix. **Changed** means the targeted correction is included in this commit. Reasons for unchanged entries:

- **Reference:** only the control relationship, firm workflow/requirement, or link is relevant; no corrected product behavior is duplicated.
- **Mapping:** governance/regulatory/standards mapping or terminology is unchanged; no regulatory reinterpretation was performed.
- **Catalog:** names, IDs, URLs, navigation, and control counts did not change.
- **Evidence:** evidence-format or review responsibilities remain compatible; no fictional deletion-lock/native-MRM assertion occurs in the relevant passage.
- **Manual:** existing evaluator coverage accurately describes the manual control.

### Direct references: `docs\controls\`

| Artifact | Disposition |
|---|---|
| `CONTROL-INDEX.md` | Unchanged - Catalog |
| `index.md` | Unchanged - Catalog |
| `pillar-1-security\1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` | Unchanged - Reference |
| `pillar-1-security\1.11-conditional-access-and-phishing-resistant-mfa.md` | Unchanged - Reference |
| `pillar-1-security\1.12-insider-risk-detection-and-response.md` | Unchanged - Reference |
| `pillar-2-management\2.1-managed-environments.md` | Unchanged - Reference |
| `pillar-2-management\2.6-model-risk-management-sr-26-2.md` | Changed - monitoring, inventory/version boundaries, verification criterion |
| `pillar-2-management\2.7-vendor-and-third-party-risk-management.md` | Unchanged - Reference |
| `pillar-2-management\2.9-agent-performance-monitoring-and-optimization.md` | Unchanged - Reference |
| `pillar-2-management\2.11-bias-testing-and-fairness-assessment.md` | Unchanged - Reference |
| `pillar-2-management\2.12-supervision-and-oversight-finra-rule-3110.md` | Unchanged - Reference |
| `pillar-2-management\2.16-rag-source-integrity-validation.md` | Unchanged - Reference |
| `pillar-2-management\2.17-multi-agent-orchestration-limits.md` | Unchanged - Reference |
| `pillar-2-management\2.18-automated-conflict-of-interest-testing.md` | Unchanged - Reference |
| `pillar-2-management\2.20-adversarial-testing-and-red-team-framework.md` | Unchanged - Reference |
| `pillar-2-management\2.21-ai-marketing-claims-and-substantiation.md` | Unchanged - Reference |
| `pillar-2-management\2.24-agent-feature-enablement-and-restriction-governance.md` | Unchanged - Reference |
| `pillar-2-management\index.md` | Unchanged - Catalog |
| `pillar-3-reporting\3.4-incident-reporting-and-root-cause-analysis.md` | Unchanged - Reference |
| `pillar-3-reporting\3.5-cost-allocation-and-budget-tracking.md` | Unchanged - Reference |
| `pillar-3-reporting\3.9-microsoft-sentinel-integration.md` | Unchanged - Reference |
| `pillar-3-reporting\3.12-agent-governance-exception-and-override-management.md` | Unchanged - Reference |

### Direct references: `docs\playbooks\`

| Artifact | Disposition |
|---|---|
| `advanced-implementations\human-in-the-loop-triggers.md` | Unchanged - Reference |
| `agent-lifecycle\agent-promotion-checklist.md` | Unchanged - Evidence |
| `compliance-and-audit\audit-readiness-checklist.md` | Unchanged - Evidence |
| `control-implementations\1.5\troubleshooting.md` | Unchanged - Reference |
| `control-implementations\1.7\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\1.7\powershell-setup.md` | Unchanged - Reference |
| `control-implementations\1.7\verification-testing.md` | Unchanged - Evidence |
| `control-implementations\1.11\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\1.11\powershell-setup.md` | Unchanged - Reference |
| `control-implementations\1.11\troubleshooting.md` | Unchanged - Reference |
| `control-implementations\1.11\verification-testing.md` | Changed - actual retention/record-state evidence |
| `control-implementations\1.12\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\1.12\powershell-setup.md` | Unchanged - Reference |
| `control-implementations\1.12\troubleshooting.md` | Unchanged - Reference |
| `control-implementations\1.12\verification-testing.md` | Changed - retention evidence convention, reminder, glossary |
| `control-implementations\2.1\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\2.1\verification-testing.md` | Unchanged - Reference |
| `control-implementations\2.6\portal-walkthrough.md` | Changed - licensed/scoped product operations and manual MRM boundaries |
| `control-implementations\2.6\powershell-setup.md` | Changed - explicit unsupported-adapter failures, guards, diagnostic-package limitations |
| `control-implementations\2.6\troubleshooting.md` | Changed - diagnostics consistent with actual inventory/templates/evaluators/retention |
| `control-implementations\2.6\verification-testing.md` | Changed - source re-verification and tests/evidence aligned with documented products |
| `control-implementations\2.7\portal-walkthrough.md` | Unchanged - existing scoped inventory/provider boundaries remain consistent |
| `control-implementations\2.7\troubleshooting.md` | Unchanged - Reference |
| `control-implementations\2.12\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\2.12\powershell-setup.md` | Unchanged - Reference |
| `control-implementations\2.17\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\2.17\verification-testing.md` | Unchanged - Reference |
| `control-implementations\2.20\troubleshooting.md` | Unchanged - Reference |
| `control-implementations\2.21\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\2.24\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\2.24\powershell-setup.md` | Unchanged - Reference |
| `control-implementations\2.24\troubleshooting.md` | Unchanged - Reference |
| `control-implementations\2.24\verification-testing.md` | Unchanged - Reference |
| `control-implementations\3.4\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\3.4\powershell-setup.md` | Unchanged - Reference |
| `control-implementations\3.4\verification-testing.md` | Changed - SharePoint retention evidence and shared procedure |
| `control-implementations\3.5\troubleshooting.md` | Unchanged - Reference |
| `control-implementations\3.5\verification-testing.md` | Unchanged - Reference |
| `control-implementations\3.9\portal-walkthrough.md` | Unchanged - Reference |
| `control-implementations\3.9\powershell-setup.md` | Unchanged - Reference |
| `control-implementations\3.9\verification-testing.md` | Unchanged - Reference |
| `control-implementations\4.7\verification-testing.md` | Unchanged - Reference |
| `control-implementations\index.md` | Unchanged - Catalog |
| `getting-started\phase-1-minimal-viable-controls.md` | Unchanged - Reference |
| `governance-operations\governance-operating-calendar.md` | Unchanged - Evidence |
| `incident-and-risk\ai-risk-assessment-template.md` | Unchanged - Reference |
| `regulatory-modules\colorado-ai-act-readiness.md` | Unchanged - Mapping |

### Direct references: `docs\reference\`

| Artifact | Disposition |
|---|---|
| `assessment-coverage.md` | Unchanged - Manual |
| `cco-quick-reference.md` | Unchanged - Mapping |
| `compliance-manager-templates.md` | Unchanged - Mapping; firm assessment templates are not native Agent 365 MRM templates |
| `csa-positioning-guide.md` | Unchanged - Reference |
| `csa-quick-reference.md` | Unchanged - Reference |
| `evidence-standards.md` | Unchanged - Evidence |
| `examiner-first-day-letter-response.md` | Changed - manual model-register/validation evidence, not an automated engine artifact |
| `fsi-configuration-examples.md` | Unchanged - Reference |
| `glossary.md` | Unchanged - Mapping |
| `iso-42001-mapping.md` | Unchanged - Mapping |
| `microsoft-cape-crosswalk.md` | Unchanged - Mapping |
| `microsoft-rai-v2-mapping.md` | Unchanged - Mapping |
| `nist-ai-rmf-crosswalk.md` | Unchanged - Mapping |
| `pattern-coverage.md` | Unchanged - Mapping |
| `regulatory-mappings.md` | Unchanged - Mapping |
| `role-catalog.md` | Unchanged - Reference; canonical roles remain valid |
| `service-trust-portal-attestation-guide.md` | Unchanged - Evidence |

### Remaining direct references

| Artifact | Disposition |
|---|---|
| `docs\framework\adoption-roadmap.md` | Unchanged - Reference |
| `docs\framework\agent-lifecycle.md` | Unchanged - Reference |
| `docs\framework\agentic-capability-drivers.md` | Unchanged - Reference |
| `docs\framework\agentic-coe.md` | Unchanged - Reference |
| `docs\framework\executive-summary.md` | Unchanged - Reference |
| `docs\framework\regulatory-framework.md` | Unchanged - Mapping |
| `docs\getting-started\checklist.md` | Unchanged - Reference |
| `docs\images\2.6\EXPECTED.md` | Changed - registry/request, Monitor, item-retention evidence requirements; no screenshots created |

### Additional linked/repeated-claim artifacts

| Artifact | Disposition |
|---|---|
| `docs\controls\pillar-1-security\1.9-data-retention-and-deletion-policies.md` | Changed - actual lock command/property, eligibility, item-vs-policy protection |
| `docs\playbooks\control-implementations\1.9\portal-walkthrough.md` | Changed - unfiltered expected-policy lock proof |
| `docs\playbooks\control-implementations\1.9\powershell-setup.md` | Changed - documented parameter/property, eligibility caveat and checked read-back |
| `docs\playbooks\control-implementations\1.9\verification-testing.md` | Changed - item-state test, policy proof, supported clock, irreversible test extension |
| `docs\playbooks\control-implementations\1.9\troubleshooting.md` | Changed - actual policy-state diagnostics and scope limits |
| `docs\images\1.9\EXPECTED.md` | Unchanged - generic label/settings/policy screenshots do not name the removed parameter/property |
| `docs\playbooks\control-implementations\3.6\verification-testing.md` | Changed - PRE-07 separates retained SharePoint item proof from Dataverse exports |
| `docs\controls\pillar-1-security\1.6-microsoft-purview-dspm-for-ai.md` | Unchanged - upstream supported activity evidence; not the authoritative MRM register |
| `docs\controls\pillar-1-security\1.7-comprehensive-audit-logging-and-compliance.md` | Unchanged - upstream audit/retention requirements not reassessed |
| `docs\controls\pillar-1-security\1.10-communication-compliance-monitoring.md` | Unchanged - supervisory workflow relationship, not native MRM implementation |
| `docs\controls\pillar-2-management\2.3-change-management-and-release-planning.md` | Unchanged - existing change-ticket workflow remains required |
| `docs\controls\pillar-2-management\2.5-testing-validation-and-quality-assurance.md` | Unchanged - firm testing/validation requirement |
| `docs\controls\pillar-2-management\2.8-access-control-and-segregation-of-duties.md` | Unchanged - validation independence/role boundary |
| `docs\controls\pillar-2-management\2.14-training-and-awareness-program.md` | Unchanged - validator competence relationship |
| `docs\controls\pillar-2-management\2.25-agent-365-admin-center-governance-console.md` | Unchanged - upstream limitation noted above; not recertified |
| `docs\playbooks\control-implementations\2.25\portal-walkthrough.md` | Unchanged - upstream limitation noted above; 2.6 no longer inherits the broad native-template/licensing assumptions |
| `docs\playbooks\control-implementations\2.25\powershell-setup.md` | Unchanged - existing generic adapters already explicitly unimplemented; not a new working API |
| `docs\playbooks\control-implementations\2.25\verification-testing.md` | Unchanged - upstream template/licensing assumptions require separate re-verification; not 2.6's acceptance evidence |
| `docs\playbooks\control-implementations\2.25\troubleshooting.md` | Unchanged - upstream native-template assumptions require separate re-verification |
| `docs\controls\pillar-2-management\2.26-entra-agent-id-identity-governance.md` | Unchanged - identity attribution relationship, not full inventory/MRM evidence |
| `docs\controls\pillar-3-reporting\3.1-agent-inventory-and-metadata-management.md` | Unchanged - authoritative firm register remains a reconciliation input |
| `docs\controls\pillar-3-reporting\3.2-usage-analytics-and-activity-monitoring.md` | Unchanged - usage data relationship, not the corrected collection contract |
| `docs\controls\pillar-3-reporting\3.3-compliance-and-regulatory-reporting.md` | Unchanged - reporting relationship and mappings |
| `docs\controls\pillar-3-reporting\3.6-orphaned-agent-detection-and-remediation.md` | Unchanged - accountability relationship; specific PRE-07 proof corrected in its verification guide |
| `docs\controls\pillar-4-sharepoint\4.3-site-and-document-retention-management.md` | Unchanged - upstream SharePoint retention relationship; no removed lock property |
| `docs\playbooks\_shared\powershell-baseline.md` | Unchanged - PowerShell baseline is independent of the removed adapters |

### Machine-readable catalogs, generators, and build outputs

| Artifact | Disposition |
|---|---|
| `assessment\manifest\generate_manifest.py` | Unchanged - Control 2.6 is manual, no evaluator implemented by this documentation change |
| `assessment\manifest\controls.json` | Unchanged - generator reproducibility check passed |
| `docs\javascripts\control-explorer-data.json` | Regenerated, content unchanged apart from `generatedAt`; timestamp-only noise discarded |
| `docs\javascripts\search-aliases.json` | Unchanged - same title/URL/aliases |
| `mkdocs.yml` | Unchanged - no path, title, count, or navigation changes |
| `scripts\canonicalize_regulatory_naming.py` | Unchanged - historical naming transformation, not product behavior |
| `scripts\generate_excel_templates.py` | Unchanged - control ID/title catalog only |
| `scripts\update_excel_templates.py` | Unchanged - historical title mapping, not current product guidance |
| `scripts\harvest_manifest_extension.py` | Unchanged - title-alias extraction, not product behavior |
| `scripts\test_verify_regulatory_naming.py` | Unchanged - naming fixture, no changed regulatory naming |
| `scripts\verify_regulatory_naming.py` | Unchanged - naming validation, no changed regulatory naming |
| `docs\downloads\` Excel catalog outputs | Unchanged - no IDs, titles, count, roles, or manifest content changed; no Excel regeneration needed |
| `scripts\verify_xref_graph.py` graph | Recomputed and passed; this checker has no persistent graph output |
| `docs\version.json` | Build regenerated local SHA/time; unrelated build-only changes discarded |
| `site\` | Regenerated by final strict build, including search/navigation and changed pages; ignored deployment output |
| `_broken-links.json` | Generated as `[]`, inspected, then removed as a check artifact |

There is no `scripts\build_content_graph.py` or affected persistent documentation graph generator in this checkout. The assessment code-only Graphify output is not affected by Markdown edits; it was not rebuilt.

Generator commands: `python assessment\manifest\generate_manifest.py --check` (passed); `python scripts\gen_explorer_data.py` (passed: 79 controls, 318 playbook links); `python scripts\compile_researcher_package.py` (passed); `mkdocs build --strict` (passed). No generated file was hand-edited.

The researcher compiler regenerated these ignored outputs: `maintainers-local\researcher-package\01-Pillar-1-Security-Controls.md`, `02-Pillar-2-Management-Controls.md`, `03-Pillar-3-Reporting-Controls.md`, `04-Pillar-4-SharePoint-Controls.md`. Existing limitation: the compiler covers Pillar 2 only through 2.26, so it is not evidence that the whole package has the current 79-control count. The changed 1.9 and 2.6 content is included.

The MkDocs hook regenerated 147 ignored role-homework pages. The eight Control 2.6 outputs are `docs\assessment\pre-session\ai-administrator\index.md`, `agent-owner-copilot-studio-agent-author\index.md`, `compliance-officer\index.md`, `governance-lead\index.md`, `internal-audit\index.md`, `model-risk-committee-governance-body\index.md`, `model-risk-manager-independent-validation-function\index.md`, and `power-platform-admin\index.md` (all suffixes after the first are relative to `docs\assessment\pre-session\`). Their manifest-derived control listing/questions are unchanged.

### Historical/procedural reference hits

These are **unchanged** because they record historical changes or direct readers to the current source, not a current executable product contract: `.github\prompts\review-learn-changes.prompt.md`, `.squad\agents\linus\history.md`, `CHANGELOG.md`, `reports\issue-821-reverification.md`, `reports\issue-910-reverification.md`, and `reports\learn-changes\learn-changes-2026-02-01.md`.

The following filenames under `reports\monitoring\` are also **unchanged historical snapshots**, not rewritten retroactively: `learn-changes-2026-04-07.md`, `learn-changes-2026-04-28.md`, `learn-changes-2026-04-29.md`, `learn-changes-2026-05-03.md`, `learn-changes-2026-05-10.md`, `learn-changes-2026-05-13.md`, `learn-changes-2026-05-14.md`, `learn-changes-2026-05-15.md`, `learn-changes-2026-05-16.md`, `learn-changes-2026-05-28.md`, `learn-changes-2026-05-29.md`, `learn-changes-2026-05-30.md`, `learn-changes-2026-05-31.md`, `learn-changes-2026-06-01.md`, `learn-changes-2026-06-02.md`, `learn-changes-2026-06-03.md`, `learn-changes-2026-06-04.md`, `learn-changes-2026-06-05.md`, `learn-changes-2026-06-18.md`, `learn-changes-2026-06-20.md`, `learn-changes-2026-07-09.md`, `learn-changes-2026-07-12.md`, `learn-changes-2026-07-31.md`, `learn-changes-2026-08-06.md`, `learn-changes-2026-08-20.md`, `learn-changes-2026-08-26.md`, `learn-changes-2026-08-28.md`, `learn-changes-2026-09-22.md`, `learn-changes-2026-10-02.md`, `learn-changes-2026-10-15.md`, `learn-changes-2026-10-23.md`, `learn-changes-2026-10-29.md`, `learn-changes-2026-11-07.md`.

## Local validation

The mandatory site checks ran in the required order, after the final documentation corrections:

| Exact command | Result |
|---|---|
| `mkdocs build --strict` | Passed |
| `python scripts\verify_build_output.py site` | Passed |
| `python scripts\verify_meta_tags.py site` | Passed |
| `python scripts\verify_doc_links.py site --json _broken-links.json` | Passed - zero broken links |
| `python scripts\verify_controls.py` | Passed |
| `python scripts\verify_xref_graph.py` | Passed |
| `python scripts\check_manifest_doc_drift.py --check` | Passed |
| `python scripts\check_explorer_data_drift.py --check` | Passed |
| `python scripts\check_change_radar_data_drift.py --check` | Passed |
| `python scripts\check_faq_jsonld_drift.py --check` | Passed |
| `python scripts\generate_coverage_matrix.py --check` | Passed |
| `python scripts\verify_language_rules.py` | Passed |
| `python scripts\verify_commercial_scope.py` | Passed |
| `python scripts\verify_learn_urls_count.py --check` | Passed |
| `python scripts\verify_version_stamps.py --check` | Passed |
| `python scripts\verify_prose_counts.py --check` | Passed |
| `python scripts\verify_solutions_docs.py --check` | Passed |
| `python scripts\verify_regulatory_naming.py --check` | Passed |
| `git diff --check` | Passed |

All eleven PowerShell fences in the 2.6 helper guide parsed successfully. Offline function-level execution, with Graph/network calls mocked, confirmed three explicit inventory errors, no affected-agent matches from missing model names, and persisted `Error` / `ManualEvidenceRequired` status in the package and optional Foundry output. Retention snippets were syntax-parsed separately; the lock helper was exercised only with local mocks to check failed/successful read-back handling. No policy was changed.

The first final-validation attempt caught a malformed Control 1.9 footer introduced by this change. The targeted verification date was moved to a separate canonical marker, preserving the repository's required update-footer shape, before rerunning validation.

No Python/JavaScript/assessment implementation, dependency, workflow, scoring, or site-navigation source changed, so their unrelated unit/E2E suites were not run. These are local results, not a claim that remote CI executed.

## Trusted-parent publication handoff

Use the repository PR template; include this report's **Sources**, **Discrepancies corrected**, and **Downstream artifacts reviewed** sections in or by reference from the PR summary. State explicitly that tenant/UI verification and production adapters remain outstanding, and do not describe the separate Control 2.25 limitations as resolved. Publish only after the parent revalidates the exact local commit and its durable worker claim under the issue lease.
