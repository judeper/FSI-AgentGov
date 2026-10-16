# Issue 821 — Communication Compliance documentation re-verification

**Documentation checked:** 2026-10-16. **Execution:** local-only on `ocean/issue-821`.

## Authority and verification boundary

The exact constraints were **“Re-verify ALL technical/product claims”**, **“Preserve all regulatory/compliance wording and mappings”**, **“no live tenant/UI execution (none performed)”**, **“Do not edit assessment code, scripts, workflows, or mkdocs.yml”**, and **“Never run gh, any GitHub API operations, git push/send-pack, remote mutation, PR/issue operations, or inspect/request/recover/set GitHub credentials/auth state.”**

No prohibited remote/identity operations, browser sessions, tenant commands, nested agents, screenshots, or policy mutations were performed. Microsoft Learn search and fetch tools supplied live official documentation. Large fetched articles were additionally read through unauthenticated HTTPS from the same official Learn URLs into disposable repository-local text extracts, because tool responses were truncated. No source extract or customer evidence is committed.

The target's **Last Verified** now distinguishes the 2026-10-16 documentation check from its historical April 2026 UI date. Changed companion pages have targeted clarifications, not assertions that every statement or UI on those pages was re-tested. Regulatory text, citations, mappings, and records schedules were not substantively revised. The PR template was inspected locally; no PR body or PR was created.

## Findings and disposition

| Discrepancy | Correction and affected evidence |
|---|---|
| Copilot had an invented 30-minute audit floor and universal 24-hour queue ceiling; source detection, processing, and audit visibility were conflated | Distinguish 1-hour body detection, Teams processing up to 48 hours, Exchange processing about 24 hours, connector import-dependent 24–48 hours, OCR detection/availability, and separate CC audit visibility up to 48 hours. These are not end-to-end SLAs. Corrected the 1.21 timing table's incorrect **Compliance Manager** queue attribution too. |
| PAYG was treated as an Enterprise/Other AI apps requirement only | Non-M365 AI data requires PAYG even under **Microsoft Copilot experiences**, including Copilot Studio, Security Copilot, and Fabric. Microsoft 365 Copilot data is exempt for this detection. Location selection alone does not prove onboarding/billing/ingestion. |
| Entitlement script accepted guessed/legacy SKU aliases and equated SKU presence with rights | Export complete license details and require signed source-specific entitlement/service-plan reconciliation against the live service-description matrix. Base CC and Copilot-for-M365 prompt/response analysis are distinct rows. Unknowns fail closed; signals do not prove licensing. |
| Classifier bodies were called deterministic or Microsoft-certified; an MNPI prompt was expected to trigger Prompt Shields/protected material | Preserve reproducible inputs but distinguish probabilistic classifier evaluation from an independent 100% keyword/no-condition transport control. Remove the unsupported Microsoft validation-set assertion. Expand coverage to every enabled classifier, not just the eight example rows. |
| One Copilot Chat test purported to validate all three AI categories | Require separate approved positive-control observations for each required onboarded source; unused locations need explicit not-applicable rationale. Matching prompt/response entries are separate, not automatically both present. |
| Policy inventory assumed undocumented portable `ConditionTemplate`, `Direction`, `PolicyMatchPreservation`, and status properties | Preserve raw reads, reconcile **Policy settings and status** exports and actual portal configuration, and recognize custom/system policies as valid alongside the seven template areas. Missing projected properties are not configuration failures. |
| Global privacy changes were asserted to emit `SupervisionPolicyUpdated` with `Pseudonym*` fields | No such operation/payload contract was established in the official references. Require attributable settings/change-register evidence, retain actual events where available, and do not interpret an empty field search as absence of change. Correct the documented privacy-control label/navigation. |
| IPPS-only audit claims contradicted Exchange-only troubleshooting guidance; the activity cmdlet was treated as a match feed | Policy/rule management reads explicitly require IPPS. Audit search is not documented as CC-exclusive to one endpoint. `Get-SupervisoryReviewActivity` returns reviewer actions, not detections. Verify tenant, permissions, commands, and positive controls instead of inventing silent-zero endpoint behavior. |
| Fixed-size queries, actor assumptions, and empty exports could manufacture negative evidence | Bounded snippets are diagnostic only. Final evidence requires completed paged queries, cap handling, deduplication, raw payload correlation, separate actor/message identities, and explicit zero-row CSV headers. The companion collector now handles zero rows and deduplication, fails on query errors/missing identities, and rejects a 50,000-result session. |
| A non-existent policy identity can return all policies; display name was compared directly to a UPN | Use an exact-one inventory selection or the recorded portal policy GUID. Resolve reviewer identities and inspect actual reviewer assignments instead of assuming `.Name` or an output identity string is a UPN. |
| Audit lifecycle evidence was required annually even without a change, with an assumed 365-day history | Only demand lifecycle events for actions actually performed within available retention. Tag actor is the reviewer; policy-change actor is the administrator. Preserve the documented `AeD`/`Discovery` distinctions and exact operations. |
| Global preservation inheritance was treated as missing configuration, and changing preservation implied retrospective extension | `Global Setting` is legitimate; record both selection and effective period. Preserve options/default, per-policy precedence, prospective changes, and inability to recover expired copies. Distinguish message copies from “metadata only.” |
| OME decryption/matching was asserted universally without supporting CC documentation | Convert to a conditional capability test using supported-configuration evidence and an identical unencrypted positive control. Do not generalize by encryption product name, issuer, direction, label, or successful delivery. |
| Every remediation action was assumed to produce a tag event, escalation could target an arbitrary contact, and exactly three activity rows were expected | Tags have tag evidence; notification, resolution, and escalation need their own actual history. Escalation recipients come from policy reviewers; action counts/actor representation are observed, not guessed. |
| eDiscovery Manager membership and a particular legacy UI sequence were mandatory for CC case escalation; subject was the join key | Learn states no extra permissions are needed to manage the CC-created case for the authorized investigator. Use documented **Escalate for investigation**, case/message identifiers, and `CaseAdded`; creation does not itself tag, resolve, or apply a hold. |
| Unrestricted CC Admin was assumed to see messages in the AU comparison | Use an unrestricted authorized investigator assigned to the policies. AUs do not scope reports/audit exports; overlapping unrestricted assignments and adaptive-scope incompatibility must be considered. Correct the Graph AU member cmdlet and require all pages. |
| Unscoped-sender and paused-policy tests lacked meaningful positive oracles | Inbound channel/recipient scope can legitimately include an unscoped sender. Prove effective scope and keyword transport independently. Allow up to 24 hours for pause propagation; existing matches and reviewer activity remain available and are not new detections. |
| CONT-03 in control 1.7 could manufacture PASS from a hard-coded queue depth and boolean | Replace fabricated observations with actual policy/message/action/query evidence and link the 1.10 transport/review tests. Clarify the investigator role in 1.12 TC-16 and SOC guidance. |
| Hash/UNC examples could be mistaken for immutable storage; evidence version was v1.3.4 | Correct the example to v1.6.2, exclude older manifests, identify example verdicts as illustrative, and require actual archival policy/object verification. Generic shares, hashes, and unlocked test policies do not establish immutable archival; 2555 days is not calendar-aware. |
| OCR and generic feature references were stale | Replace one-hour OCR claims with the live policy reference's detection/availability guidance. The old `communication-compliance-feature-reference` path returned 404. |

## Sources and coverage

The following exact official URLs were fetched during the check. Search queries included Communication Compliance policies/templates/processing, policy match preservation, audit activities, encrypted messages, licensing, reviewer activity, AU membership, Preservation Lock, and immutable storage. Microsoft code-sample search also corroborated the read/audit-query examples.

| Source | Claims checked / catalog coverage |
|---|---|
| https://learn.microsoft.com/en-us/purview/communication-compliance-policies | Seven template areas, defaults/classifiers/directions, custom/system policies, no PowerShell policy administration, hourly detection table, pause/resume propagation, built-in OCR and image availability. POL, CLS, SAM, NEG-02. |
| https://learn.microsoft.com/en-us/purview/communication-compliance-channels | Teams inbound/shared-channel semantics, Exchange/Viva/connector timing and scope, source onboarding, non-M365 AI billing, original-vs-copy distinction. COP, CLS, OME boundaries, NEG-01. |
| https://learn.microsoft.com/en-us/purview/communication-compliance-configure | Auditing prerequisite, reviewer mailboxes, current privacy-control label/path, source selection, custom AU-scoped policies. AUD, PSE, POL, NEG-03. |
| https://learn.microsoft.com/en-us/purview/communication-compliance-copilot | Actual AI location labels, non-M365 AI PAYG including Microsoft experiences, per-policy reviewer prerequisite, matching prompts/responses as separate entries, optional 100% no-condition transport policy. LIC, COP, CLS. |
| https://learn.microsoft.com/en-us/purview/communication-compliance-permissions | Role matrix, Admins versus Investigators/Analysts, 30-minute propagation, AU access limits and incompatibility with adaptive scopes. INV, EDC, AU, NEG-03. |
| https://learn.microsoft.com/en-us/purview/communication-compliance-investigate-remediate | Preservation default/options/override/inheritance/prospective effect; tags, notification, assigned-reviewer escalation, case creation, 100-message limit, automatic custodian and no additional case-management permissions. PSE, INV, EDC, PMP, NEG-02. |
| https://learn.microsoft.com/en-us/purview/communication-compliance-reports-audits | Actual policy/status/message/review exports and fields, audit visibility up to 48 hours, documented operations/RecordTypes, policy mailbox storage boundary. AUD, POL, CLS, INV, EDC evidence. |
| https://learn.microsoft.com/en-us/purview/audit-log-activities | `SupervisionRuleMatch`, lifecycle operations, `SupervisoryReviewTag`, and `CaseAdded`/`HoldCreated` distinction. AUD, EDC. |
| https://learn.microsoft.com/en-us/purview/communication-compliance | General product purpose and privacy-by-design boundary; not a new licensing or decryption contract. |
| https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description | Base CC versus Microsoft Copilot-for-M365 analysis entitlement matrix. LIC; licensing reference propagation. |
| https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-supervisoryreviewpolicyv2?view=exchange-ps | IPPS requirement, identity syntax and null/non-existent-identity returns-all warning. POL/COP lookup safety. |
| https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-supervisoryreviewrule?view=exchange-ps | IPPS requirement and policy-filter syntax; no guaranteed modern template/output schema. POL/COP. |
| https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-supervisoryreviewactivity?view=exchange-ps | Reviewer activities, required policy/date arguments, and documented example output fields, not a match-detection feed. CLS/INV/NEG-02. |
| https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/search-unifiedauditlog?view=exchange-ps | Cloud audit query syntax, per-call limits, session paging and 50,000-result cap. All evidence queries and negative-test completeness. |
| https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.users/get-mguserlicensedetail?view=graph-powershell-1.0 | Read-only license detail, `ServicePlans`/SKU data, and `-All`. LIC. |
| https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.directorymanagement/get-mgdirectoryadministrativeunitmember?view=graph-powershell-1.0 | Correct AU-member cmdlet, required AU identifier, `-All`, and read permissions. AU. |
| https://learn.microsoft.com/en-us/purview/retention-preservation-lock | Supported retention-policy locking and irreversible restriction boundary, not generic file-share protection. Evidence archival caveat. |
| https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview | Blob/container/version scope, locked versus unlocked policies, creation-time-based retention, and hash/path limitations. Evidence archival caveat. |

### Assumptions, unknowns, and adverse outcomes

- **Strong:** official pages establish the documented capabilities above. **Failure mode:** sources conflict or change; retain check date and resolve tenant-specific behavior rather than treating guidance as an SLA.
- **Moderate:** the tenant exposes the documented location/control names. **Missing test:** actual tenant/UI execution, effective licenses, source onboarding and command output reconciliation. Not performed; UI dates were not renewed.
- **Weak / rejected:** a plausible phrase must trigger a classifier, an empty query proves no event, a selected location proves all app coverage, or a projected field is a stable API contract. The revised tests explicitly reject these assumptions.
- **Unresolved product details:** exact audit operation/payload for global privacy/preservation changes, universal encrypted-content support, and every modern policy output field were not established. Inventing these would make the test more binary but less truthful; leaving them unknown requires manual corroboration and may prevent a PASS.
- The live preservation article contains inconsistent historical rollout dates (April/June/September 2025). Current options/default/precedence are clear; this review does not independently establish the historical rollout timeline or retrofit match timestamps.
- **Regulatory boundary:** pre-existing retention periods and legal wording were preserved as instructed, not legally revalidated. For example, the cadence and retention paragraphs contain differing records-schedule examples; Compliance/Legal owns reconciliation. The technical archival caveat must not be read as a legal opinion.
- **Trade-off:** independent transport and source-specific tests cost more than one sample/one queue count. Not doing them risks reporting untested sources or probabilistic classifier misses as control health.
- **Screenshot checklist gap closed (authorized local follow-up):** `docs\images\1.10\EXPECTED.md` now follows the corrected per-policy Pending/review, privacy, global/per-policy preservation and source-specific evidence instructions. It separates probabilistic classifier results from transport controls and directs binaries/evidence to local `maintainers-local\tenant-evidence\1.10\` storage. This is a checklist-text correction only: no tenant/UI execution, screenshots or renewed UI-verification date. `docs\images\2.12\EXPECTED.md` remains unchanged; its generic CC policy capture does not impose a corrected technical contract.

## Downstream enumeration and classification

Method: enumerate tracked text, classify every hit, then search again for the corrected symptoms. The initial broad scan matched **152 tracked files / 853 lines** (including unchanged historical monitor payloads); matches were recorded before the evidence report was added. Search dimensions were the identifier/path/title, generic Communication Compliance references, preservation, audit/activity names, and the stale feature-reference path. Regulatory/historical matches were KEEP, not rewritten. Changed statements were checked against the sources above; the table below is a relevance review of dependent excerpts, not certification of every unrelated claim in those documents.

### Changed artifacts

| Concrete path | Reason |
|---|---|
| `docs\playbooks\control-implementations\1.10\verification-testing.md` | Full target technical/product claim review, honest date, corrected test/evidence contracts. |
| `docs\playbooks\control-implementations\1.10\portal-walkthrough.md` | Matching setup, privacy, billing, OCR, preservation, transport and audit instructions. |
| `docs\playbooks\control-implementations\1.10\powershell-setup.md` | Matching session/role/output caveats and complete-query collector handling; legacy sections not certified as modern CC authoring. |
| `docs\playbooks\control-implementations\1.10\troubleshooting.md` | Matching diagnostic, pause, encryption, export, preservation and timing corrections. |
| `docs\images\1.10\EXPECTED.md` | Explicitly authorized follow-up: align screenshot checklist with corrected navigation, privacy/preservation/source evidence and local-only storage; no binary captures or tenant/UI verification. |
| `docs\controls\pillar-1-security\1.10-communication-compliance-monitoring.md` | Repeated product claims; retained required control structure and regulatory sections. |
| `docs\playbooks\control-implementations\1.7\verification-testing.md` | CONT-03 fabricated-pass removal and actual evidence handoff. |
| `docs\playbooks\control-implementations\1.12\verification-testing.md` | TC-16 CC investigator/reviewer authorization only. |
| `docs\playbooks\control-implementations\1.21\verification-testing.md` | Repeated CC timing/queue attribution only. |
| `docs\reference\fsi-configuration-examples.md` | Clarify the 1.10 design sketch's PAYG, real detector configuration, separate retention and organizational SLA. |
| `docs\reference\license-requirements.md` | Base CC versus source-specific Copilot rights and PAYG distinction. |
| `docs\reference\purview-soc-analyst-roles.md` | Actual Analysts role group plus per-policy reviewer/AU authorization. |
| `CHANGELOG.md` | Outcome and documentation-only verification boundary. |

### Unchanged dependent groups — each named member reviewed for relevant statements

Brace lists below explicitly enumerate members under the concrete path prefix; they are not sampling instructions.

| Concrete paths / enumerated group | KEEP reason |
|---|---|
| `docs\controls\CONTROL-INDEX.md`; `docs\controls\index.md`; `docs\controls\pillar-1-security\index.md`; `docs\playbooks\control-implementations\index.md` | Identity/title/navigation links unchanged. |
| `docs\controls\pillar-1-security\{1.2-agent-registry-and-integrated-apps-management,1.6-microsoft-purview-dspm-for-ai,1.7-comprehensive-audit-logging-and-compliance,1.12-insider-risk-detection-and-response,1.13-sensitive-information-types-sits-and-pattern-recognition,1.14-data-minimization-and-agent-scope-control,1.19-ediscovery-for-agent-interactions,1.21-adversarial-input-logging,1.25-mime-type-restrictions}.md` | Related-control integration/purpose references; no repeated corrected timing/property/decryption contract requiring alteration. Preserve regulatory mappings and their dates. |
| `docs\controls\pillar-2-management\{2.6-model-risk-management-sr-26-2,2.7-vendor-and-third-party-risk-management,2.23-user-consent-and-ai-disclosure-enforcement,2.24-agent-feature-enablement-and-restriction-governance}.md`; `docs\controls\pillar-3-reporting\3.4-incident-reporting-and-root-cause-analysis.md` | Supervisory, vendor, disclosure, feature-cascade and incident relationships, not a new CC implementation contract. |
| `docs\playbooks\control-implementations\1.12\{portal-walkthrough,powershell-setup,troubleshooting}.md` | IRM/CC separation and cross-links retained; distinct IRM privacy settings are not CC privacy settings. |
| `docs\playbooks\control-implementations\1.13\{portal-walkthrough,troubleshooting}.md`; `docs\playbooks\control-implementations\1.14\{portal-walkthrough,troubleshooting}.md` | SIT consumer and minimization/compensating-control references, not classifier-trigger guarantees. |
| `docs\playbooks\control-implementations\1.19\{portal-walkthrough,troubleshooting,verification-testing}.md` | CC case handoff references retained; eDiscovery operational authorization/hold procedures are not the same as CC's create-case permission. Regulatory separation-of-duties wording left intact. |
| `docs\playbooks\control-implementations\1.2\{portal-walkthrough,sponsorship-lifecycle-workflows}.md` | Registry identity/supervision handoff only. |
| `docs\playbooks\control-implementations\1.21\{portal-walkthrough,powershell-setup,troubleshooting}.md` | Prompt Shields/telemetry plane separation and control links; no universal corrected queue deadline outside the changed verification row. |
| `docs\playbooks\control-implementations\1.22\troubleshooting.md`; `docs\playbooks\control-implementations\1.5\{powershell-setup,troubleshooting,verification-testing}.md`; `docs\playbooks\control-implementations\1.6\{portal-walkthrough,troubleshooting}.md` | Adjacent DLP/DSPM/risk references, not CC detection evidence substitutes. |
| `docs\playbooks\control-implementations\1.7\{portal-walkthrough,powershell-setup,troubleshooting}.md` | Audit/content-plane separation and existing evidence paths; only CONT-03 in the verification file required correction. |
| `docs\playbooks\control-implementations\1.8\{portal-walkthrough,powershell-setup,troubleshooting,verification-testing}.md` | Runtime protection and supervisory-plane cross-references; no repeated corrected CC technical assertion. |
| `docs\playbooks\control-implementations\2.20\portal-walkthrough.md`; `docs\playbooks\control-implementations\2.24\{portal-walkthrough,powershell-setup,troubleshooting,verification-testing}.md`; `docs\playbooks\control-implementations\2.6\verification-testing.md` | General enablement/governance notifications and model-risk correlation; these do not prove CC source ingestion and were not redated. |
| `docs\playbooks\control-implementations\3.1\powershell-setup.md`; `docs\playbooks\control-implementations\3.4\{portal-walkthrough,powershell-setup}.md`; `docs\playbooks\control-implementations\3.9\troubleshooting.md`; `docs\playbooks\control-implementations\4.6\troubleshooting.md`; `docs\playbooks\control-implementations\4.7\powershell-setup.md` | Inventory, incident, SIEM and SharePoint-related CC integration mentions; no corrected 1.10 API/timing contract to propagate. |
| `docs\playbooks\advanced-implementations\dspm-for-ai-policy-pack.md`; `docs\playbooks\governance-operations\governance-operating-calendar.md` | DSPM policy-pack inventory and calendar linkage, not test verdicts or CC template-output enums. |
| `docs\framework\{agentic-capability-drivers,solutions-integration}.md` | Maturity and solution integration references only. |
| `docs\reference\{assessment-coverage,cco-quick-reference,microsoft-learn-urls,pattern-coverage,portal-paths-quick-reference,power-platform-sspm-control-mapping,regulatory-mappings,role-catalog}.md` | Coverage counts, watchlist URL, catalog/role aliases, navigation and regulatory maps unchanged; none asserts the corrected specialized test contract. Generated coverage checked rather than hand-edited. |
| `docs\downloads\index.md`; `docs\llms.txt`; `docs\start-here.md` | Download/discovery/entry-point references unchanged. |
| `docs\images\2.12\EXPECTED.md` | Inspected; generic CC policy capture unchanged. No screenshots or unsupported UI verification date. The 1.10 checklist is now in the changed-artifact inventory. |
| `assessment\manifest\{controls.json,generate_manifest.py,frontier-readiness.json}`; `assessment\data\solutions-lock.json` | Control IDs, manual evidence/routing metadata and solution mapping remain valid; no scoring/manifest implementation changes authorized or required. |
| `scripts\{test_control_110_playbook_guards.py,generate_excel_templates.py,update_excel_templates.py}`; `scripts\config\monitoring-config.yaml` | Guard tests and catalog/watch mappings unchanged; regression tests run. No script edits. |
| `mkdocs.yml`; `tests\e2e\fixtures\render-expectations.json` | Existing navigation and diagram expectations are unaffected; no new diagram/asset or nav destination. |
| `data\monitor-state.json`; the 33 concrete pending payloads listed below | Historical monitor state/payload text, not editable implementation source; unchanged. |
| `reports\audit\02-inventory.md`; `reports\learn-changes\learn-changes-2026-02-01.md`; `reports\monitoring\learn-changes-{2026-03-11,2026-04-28,2026-05-29,2026-05-30,2026-05-31,2026-06-01,2026-06-02,2026-06-03,2026-06-04,2026-06-18,2026-06-23,2026-06-24,2026-07-12,2026-07-22,2026-08-06,2026-08-22,2026-09-22}.md`; `releases\CHANGELOG-archive\CHANGELOG-v1.3.md` | Immutable historical reports/archive; preserve original observations rather than making old records look newly verified. |

All entries in this explicit KEEP group are relative to `data\monitor-pending\learn\`:

```text
learn.microsoft.com-en-us-microsoft-365-copilot-agent-essentials-m365-agents-checklist-c07fd10b938a0a03f8cbc2af.json
learn.microsoft.com-en-us-microsoft-365-copilot-agent-essentials-m365-agents-checklist-dabc6234f2ee09bcd51e9b6c.json
learn.microsoft.com-en-us-microsoft-365-copilot-agent-essentials-m365-agents-checklist-e73fd87758cbe3681a075b2a.json
learn.microsoft.com-en-us-microsoft-365-copilot-copilot-control-system-security-governance-11e4feb41794d89660235f72.json
learn.microsoft.com-en-us-microsoft-365-copilot-copilot-control-system-security-governance-811e1344ce2074f1e55de5e4.json
learn.microsoft.com-en-us-microsoft-365-copilot-copilot-control-system-security-governance-e59b49792dcba5ae8f97c16a.json
learn.microsoft.com-en-us-office365-servicedescriptions-microsoft-365-service-descriptions-micro-024d7e6d76d1c846aafee684.json
learn.microsoft.com-en-us-office365-servicedescriptions-microsoft-365-service-descriptions-micro-3ec06adcb0c36f8e78af08f8.json
learn.microsoft.com-en-us-office365-servicedescriptions-microsoft-365-service-descriptions-micro-6c19414a88b9de61f46c2bdc.json
learn.microsoft.com-en-us-office365-servicedescriptions-microsoft-365-service-descriptions-micro-90fea4bb6df5a3ce2c4100c0.json
learn.microsoft.com-en-us-office365-servicedescriptions-microsoft-365-service-descriptions-micro-9da726fd5cc40c043d1256b3.json
learn.microsoft.com-en-us-office365-servicedescriptions-microsoft-365-service-descriptions-micro-feee88c00c695955788f7ff0.json
learn.microsoft.com-en-us-purview-ai-microsoft-purview-c61a19d4061688e16451bb2d.json
learn.microsoft.com-en-us-purview-communication-compliance-660b52502437259cf38cb42f.json
learn.microsoft.com-en-us-purview-communication-compliance-investigate-remediate-c376ad53157282b7841c5392.json
learn.microsoft.com-en-us-purview-communication-compliance-investigate-remediate-f83156efc69e4d2f02acd6d4.json
learn.microsoft.com-en-us-purview-communication-compliance-policies-62029d067cd2517ccd9a41f7.json
learn.microsoft.com-en-us-purview-communication-compliance-policies-dbf2e88693fabc9ebd22dd78.json
learn.microsoft.com-en-us-purview-dspm-for-ai-considerations-a5e17c8820676e8b33f061c6.json
learn.microsoft.com-en-us-purview-insider-risk-management-22c32debd14da427f50ce54e.json
learn.microsoft.com-en-us-purview-insider-risk-management-activities-3821db57a0212f9e0722ff37.json
learn.microsoft.com-en-us-purview-insider-risk-management-activities-999fae4fbb82f1522c868b43.json
learn.microsoft.com-en-us-purview-insider-risk-management-activities-cfe52191da740b4893db90bf.json
learn.microsoft.com-en-us-purview-insider-risk-management-activities-e446e4541ff65fcb7dddfe9b.json
learn.microsoft.com-en-us-purview-insider-risk-management-settings-policy-indicators-5421a3b6bf650e5555defe02.json
learn.microsoft.com-en-us-purview-insider-risk-management-settings-policy-indicators-9c675f2e142ff5ff07fdde58.json
learn.microsoft.com-en-us-purview-insider-risk-management-settings-policy-indicators-ecc648dd5f9db4726cc2a884.json
learn.microsoft.com-en-us-purview-sit-sensitive-information-type-learn-about-c23c2f58945bf738b88602f0.json
learn.microsoft.com-en-us-purview-sit-sensitive-information-type-learn-about-d552835ddc501354da67b5de.json
learn.microsoft.com-en-us-purview-trainable-classifiers-learn-about-634dc0af6004b9bd2c4c1557.json
learn.microsoft.com-en-us-purview-whats-new-48f27e6aad46ac56a2f01dd0.json
learn.microsoft.com-en-us-purview-whats-new-dae09b18d1f0584cc778c98a.json
learn.microsoft.com-en-us-security-security-for-ai-agent-365-security-76c9437eaeff23cd8833a48f.json
```

### Generators and generated artifacts

- `scripts\build_content_graph.py` does **not** exist; no tracked content-graph generator/output was found. `scripts\verify_xref_graph.py` computes and verifies references without writing a graph. It passed.
- `python scripts\gen_explorer_data.py` — **passed**; regenerated `docs\javascripts\control-explorer-data.json`. Comparison excluding `generatedAt` showed semantic equality to HEAD. Timestamp-only churn was discarded with local `git restore`, not hand-edited.
- `python scripts\compile_researcher_package.py` — **passed**; refreshed the four ignored artifacts using the existing generator: `maintainers-local\researcher-package\01-Pillar-1-Security-Controls.md`, `maintainers-local\researcher-package\02-Pillar-2-Management-Controls.md`, `maintainers-local\researcher-package\03-Pillar-3-Reporting-Controls.md`, and `maintainers-local\researcher-package\04-Pillar-4-SharePoint-Controls.md`. They remain local, not published/committed.
- MkDocs regenerated site HTML/search assets and normal build-hook outputs. The tracked `docs\version.json` timestamp/build-identity side effect was discarded after validation; the framework version did not change.
- Manifest, coverage, explorer, FAQ, change-radar, prose, version, solution and Learn URL-count checks below passed. No affected catalog required a semantic generated-data change, and none was hand-edited.

## Validation evidence

Before content edits, the four mandatory commands ran in the required order and all **passed** (697 built pages; no broken internal links). They were repeated after the final documentation edits in the same order:

| Exact command | Result |
|---|---|
| `mkdocs build --strict` | Passed, exit 0; no warnings/errors. |
| `python scripts\verify_build_output.py site` | Passed, exit 0. |
| `python scripts\verify_meta_tags.py site` | Passed, exit 0. |
| `python scripts\verify_doc_links.py site --json _broken-links.json` | Passed, exit 0; 697 pages, no broken internal links. |
| `python scripts\verify_controls.py` | Passed. |
| `python scripts\verify_xref_graph.py` | Passed. |
| `python scripts\check_manifest_doc_drift.py --check` | Passed. |
| `python scripts\check_explorer_data_drift.py --check` | Passed. |
| `python scripts\check_change_radar_data_drift.py --check` | Passed. |
| `python scripts\check_faq_jsonld_drift.py --check` | Passed. |
| `python scripts\generate_coverage_matrix.py --check` | Passed. |
| `python scripts\verify_language_rules.py` | Passed. |
| `python scripts\verify_commercial_scope.py` | Passed. |
| `python scripts\verify_learn_urls_count.py --check` | Passed. |
| `python scripts\verify_version_stamps.py --check` | Passed. |
| `python scripts\verify_prose_counts.py --check` | Passed. |
| `python scripts\verify_solutions_docs.py --check` | Passed. |
| `python scripts\verify_regulatory_naming.py --check` | Passed. |
| `python assessment\manifest\generate_manifest.py --check` | Passed. |
| `python scripts\check_automation_honesty.py --check` | Passed. |
| `python -m pytest scripts\test_control_110_playbook_guards.py -q` | Passed, 42 tests. |
| `pwsh -NoProfile -File .\_821_validate_snippets.ps1` | Passed: 19 PowerShell documentation blocks parsed; local mocked collector tests covered empty/header-only CSV and `[]` JSON, deduplication, query errors, and 50,000-result fail-closed behavior. No tenant connection. Disposable harness removed afterward. |
| `git diff --check` | Passed. |

No full CI, browser/e2e suite, live message/classifier drill, license check, billing provisioning, or tenant UI check is claimed. There are no validation blockers from the original implementation; tenant-dependent unknowns remain explicit rather than hidden behind a PASS. The previously out-of-charter screenshot checklist gap is closed by the authorized text-only follow-up described above.

**Local harness rerun caveat:** the first final mock rerun failed its empty-CSV assertion because the disposable fixture directory retained outputs from the earlier successful run, so its wildcard selected two header-only files. After removing only that task-created fixture directory, all four scenarios and 42 regression tests passed. This was fixture isolation, not a tenant run or a hidden product-test failure.

## Authorized checklist completion follow-up — 2026-10-16

Boundary: **“ONLY local operations”**, **“update this checklist text (no binary images)”**, **“do not re-audit the whole objective”**, and **“no tenant/UI verification claims.”** This follow-up changes only `docs\images\1.10\EXPECTED.md` and this report, after local commit `3ec87da3814a71df039747adc72016ca39991ce4`. The initial working tree was clean. No remote, identity, credential, browser, tenant or nested-agent operations were performed.

The existing corrected 1.10 portal and verification guides supplied the exact navigation/control labels; the PowerShell and troubleshooting guides supplied export/query boundaries. No uncertain new portal label was introduced or separately asserted as live-verified. The checklist now uses one filename convention, policy-specific Pending/review paths, privacy and global/per-policy preservation captures, per-source locations and interaction evidence, and local-only evidence storage. Regulatory wording/mappings in the implementation documents remain untouched.

**Adversarial checks and assumptions:**

- **Strong:** the checklist matches the authorized corrected guides, not the obsolete generic Alerts/Review sequence. **Failure if left unchanged:** administrators collect the wrong evidence or infer coverage from a dashboard.
- **Moderate, still untested:** a particular tenant exposes those documented controls and each source actually ingests. The checklist requires observed labels, source-specific positive controls and unresolved-gap recording; it does not turn documentation alignment into a tenant PASS.
- **Rejected:** classifier samples are deterministic, selected locations prove onboarding, screenshots replace complete audit exports, or local hashes establish immutable storage. Extra captures cost effort and can expose sensitive content; approved test populations, anonymization and authorization remain necessary.
- **Coverage blind spot:** site/link checks do not establish tenant correctness or complete checklist coverage. A separate local relative-link check resolved all four checklist links successfully; actual screenshots, licensing, PAYG, preservation settings and message/classifier tests remain unexecuted.

The mandatory site validations ran in the exact order below after the checklist edits. All commands exited 0:

| Exact command | Actual result |
|---|---|
| `mkdocs build --strict` | Passed; documentation built in 206.73 seconds. Material emitted its upstream MkDocs 2.0 advisory banner; no MkDocs build warning/error was reported. |
| `python scripts\verify_build_output.py site` | Passed; index, reference/control HTML and search asset verified. |
| `python scripts\verify_meta_tags.py site` | Passed; all 8 required tags on 3 sampled pages. |
| `python scripts\verify_doc_links.py site --json _broken-links.json` | Passed; 697 pages, no broken internal links. |
| `python scripts\verify_language_rules.py` | Passed; 780 Markdown files scanned, no prohibited language. Existing Tier 2 exceptions were reported, not new violations. |
| `python scripts\verify_commercial_scope.py` | Passed; 674 forward-facing files scanned, no scope violations. |
| `python scripts\verify_xref_graph.py` | Passed; 538 files / 6,184 references, no broken IDs or mislabeled references. |
| `python scripts\verify_controls.py` | Passed; 79 controls, required structure/footer, four standard playbooks per control and documentation anchors. |
| `python -m pytest scripts\test_control_110_playbook_guards.py -q` | Passed; 42 tests. |
| `git diff --check` | Passed. |

Only the task-created `_broken-links.json` is removed. The build-generated `docs\version.json` SHA/timestamp-only change is restored to its initially clean tracked state; no unrelated edits or existing local evidence are discarded. Generated site assets remain local. This follow-up does not rerun or newly claim the original full technical re-verification, snippet harness or tenant tests.
