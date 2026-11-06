# Issue 912 - blocked technical verification handoff

**Reviewer:** Saul (OceanSquad). **Documentation review date:** 2026-11-06.
**Disposition:** BLOCKED; not a completed re-verification or implementation.

## Authority and scope

The repository charter at `.squad\agents\saul\charter.md` explicitly prohibits Saul from fixing content or modifying CI workflows. It routes content drift to linus and build/workflow problems to linus or rusty. The local-only worker contract also prohibits remote writes and credential inspection. Accordingly, this commit contains a verification report only. The trusted parent must route corrective implementation; no sub-issue, PR, remote write, authentication operation, or nested-agent dispatch was performed.

The source page remains unchanged, including its historical UI marker and footer. Advancing a verification stamp would misrepresent the unresolved findings. No tenant execution, portal verification, licensing reconciliation, screenshots, or regulatory/compliance judgement was performed.

This is a blocking technical triage, not certification of every claim in the source or every repository dependency. Full claim-by-claim review and downstream propagation remain outstanding.

## Findings

Line numbers refer to the unchanged files on the worker's starting commit.

| Severity | File and lines | Finding and primary evidence | Required disposition |
|---|---|---|---|
| P1 | `docs\playbooks\control-implementations\2.12\verification-testing.md:422-435,525` | The HITL test sleeps 60 seconds and requires a `Search-UnifiedAuditLog` hit, with an audit-hit-under-60-seconds PASS band. Microsoft states there is no committed audit availability time; core-service records typically take 60-90 minutes and other services can take longer [S1]. This is not a reliable negative oracle for handoff failure. | linus: separate application/engagement-hub evidence from delayed audit reconciliation; require known positive controls, actual operation/schema matching and complete queries before interpreting missing records. Preserve firm policy SLAs as policy, not Microsoft commitments. |
| P1 | `docs\playbooks\control-implementations\2.12\portal-walkthrough.md:461-495`; `powershell-setup.md:1180-1212`; `verification-testing.md:1622-1661` | The Python example imports `RequestPort` and calls `self.request_port.submit`; the PowerShell verifier mandates a `RequestPort` node for every workflow. The live HITL article uses `RequestPort` for C#/Go, but Python uses `Executor`, `WorkflowContext.request_info()` and `@response_handler`. Python events are `WorkflowEvent` with `type == "request_info"` and responses are supplied to `workflow.run(...)` [S3]. Checkpoint storage must be configured; an example call is not proof of durable persistence [S4]. | linus: distinguish language-specific SDK contracts from firm-owned manifest/export schemas; test actual request/response correlation and restored pending requests. An illustrative-snippet caveat does not make these names a verified Python API. |
| P1 | `docs\playbooks\control-implementations\2.12\verification-testing.md:1820-1825,1839-1840,1869-1871` | The retention test reads workspace `ArchiveRetentionInDays`, although total/long-term retention is configured per table, separately from workspace-default analytics retention [S5]. It also presents a "Sentinel immutable archive policy export" as an artifact without establishing an immutable storage configuration. Analytics/long-term retention and storage immutability are distinct technical properties [S5,S6]. | linus: inspect actual per-table effective analytics/total retention and separately verify the configured immutable evidence destination. Do not change the firm's records schedule or reinterpret its regulatory wording. |
| P1 | `docs\playbooks\control-implementations\2.12\portal-walkthrough.md:294-324`; `verification-testing.md:1900-1904`; `troubleshooting.md:352` | Handoff setup assumes node-level queue configuration, a "Require handoff" switch and a publishing block/backlog outcome. Live Learn documents an engagement-hub connection and `Topics > System > Escalate`, with `Add node > Topic Management > Transfer conversation`; a demo canvas can report "No renderer for this activity" [S2]. These instructions do not establish a built-in supervisory publication gate or direct M365-group routing. | linus: name the engagement-hub/firm-built routing and publication controls and their prerequisites; reconcile actual evidence with the channel used. Do not treat a transfer node or test-canvas event alone as proof that a qualified reviewer received the conversation. |
| P1 | `docs\playbooks\control-implementations\2.12\troubleshooting.md:173-224`; `verification-testing.md:11,1767-1781` | The troubleshooting catalog presents Graph paths such as `/beta/admin/agentFramework/pendingRequests`, `/beta/copilotStudio/agents/{agentId}/hitlConfiguration` and `/beta/admin/agentGov/supervisionTesting`. Live searches did not establish official contracts for these paths; the Agent Framework references describe application-hosted workflow request/response and checkpoint storage [S3,S4]. Likewise, no default Purview forwarding contract was established for the listed Agent Framework checkpoint tables. **Unverified**, not independently proven nonexistent. | linus: resolve each endpoint/table against an official API/connector reference or identify it explicitly as a firm-owned adapter and supply its implementation/schema. The PowerShell sibling already identifies the AGF evidence endpoint as firm-specific; reconcile the troubleshooting/source claims with that boundary. |
| P1 | `docs\playbooks\control-implementations\2.12\verification-testing.md:68,943,1640,1796,2269` | The target requires `Invoke-Agt212PreFlight.ps1` and `_helpers/Agt212.Common.ps1`, and says the PowerShell sibling bootstraps the helper modules. Searches under `scripts`, `assessment` and the 2.12 playbook directory found references but no definitions for the preflight and several `Agt212`/Copilot Studio verification helpers. | linus: classify the suites as design templates requiring firm implementation, or provide the missing implementation through the proper specialist. Do not describe them as an executable out-of-box evidence pipeline. |
| P1 | `.squad\agents\saul\charter.md` validation command; `playwright.config.mjs:57-61` | The prescribed `--project=smoke` selector fails because the repository defines only `chromium`; the supported smoke command uses `--grep @smoke --workers=1`. This is a charter/configuration mismatch, not a source-document change. | Trusted parent/rusty: reconcile the charter's command separately; no workflow or charter correction is included here. |

## Sources

Live Microsoft Learn search and fetch tools were used. These references support the specific findings above, not a complete claim inventory.

| ID | Official URL | Reviewed boundary |
|---|---|---|
| S1 | https://learn.microsoft.com/en-us/purview/audit-log-search | Audit timing, required audit roles, Exchange Online audit-search cmdlet, indexed-content limitations. |
| S2 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off | Engagement-hub prerequisite, Escalate topic, Transfer conversation navigation, context variables, test-canvas limitations. |
| S3 | https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop | C#/Go RequestPort versus Python request/response handlers, external event handling and resumption. |
| S4 | https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints | Explicit checkpoint storage, Python storage providers and persistence configuration. |
| S5 | https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure | Workspace-default analytics retention versus table analytics/total retention; long-term retention is not a separate workspace archive property. |
| S6 | https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview | Separate time-based retention/legal-hold configuration for immutable blob storage. |

An attempted fetch of `https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/microsoftcopilotstudio` could not be retrieved; it is not supporting evidence. Searches for the proposed Graph paths and Sentinel table names did not establish an official contract, so those findings remain explicitly unverified.

## Downstream artifacts reviewed

All artifacts below are **unchanged**. Where a correction is required, unchanged means blocked by reviewer authority, not that propagation is unnecessary.

| Artifact | Review result / reason unchanged |
|---|---|
| `docs\playbooks\control-implementations\2.12\verification-testing.md` | Blocking findings above; no renewal of UI or verification stamps. |
| `docs\playbooks\control-implementations\2.12\portal-walkthrough.md` | Repeats the language-confused SDK example and unsupported handoff/publication assumptions; implementation propagation required. |
| `docs\playbooks\control-implementations\2.12\powershell-setup.md` | AGF verifier requires a RequestPort node regardless of language; Copilot Studio helper projects an unverified API/schema. Its audit-delay caveat at line 90 is already consistent with S1, and its firm-specific AGF evidence endpoint is useful prior art. |
| `docs\playbooks\control-implementations\2.12\troubleshooting.md` | Unverified Graph catalog and "Require handoff" diagnosis require propagation. Checkpoint restoration concept is supported by S3 when checkpoint storage is configured. |
| `docs\controls\pillar-2-management\2.12-supervision-and-oversight-finra-rule-3110.md` | Objective/workflow table use combined RequestPort/request_info terminology; clarify language distinctions if changed. Verification criteria specify evidence goals, not the source page's 60-second audit oracle. Regulatory text not evaluated. |
| `docs\images\2.12\EXPECTED.md` | Generic six-screenshot checklist lacks the detailed anchors claimed by the portal sibling; reconcile evidence instructions during corrective implementation. No screenshots captured. |
| `docs\playbooks\control-implementations\2.17\portal-walkthrough.md` | Repeated combined SDK terminology at line 129 deserves language/availability re-check during implementation. Its opening warning correctly distinguishes firm-authored enforcement from native portal controls. |
| `docs\controls\pillar-2-management\2.17-multi-agent-orchestration-limits.md` | SDK primitive table at line 164 repeats combined terminology; needs language-specific reconciliation if that terminology is corrected. |
| `docs\playbooks\advanced-implementations\human-in-the-loop-triggers.md` | Relevant matches describe firm-owned triggers and supervisory policy, not the specific timing/SDK/property contracts above; no correction established by this triage. |
| `docs\playbooks\control-implementations\3.9\verification-testing.md` | Existing audit-delay caveat at line 303 matches S1; TC-12 already exports per-table retention. Preserve these as prior art rather than propagating the erroneous workspace archive check. |
| `docs\reference\agent-audit-event-taxonomy.md` | Control-identifier reference does not establish the source page's invented checkpoint-table forwarding contract; no targeted change established. |
| `docs\javascripts\control-explorer-data.json` | Generated control 2.12 objective mirrors combined SDK terminology. Regenerate from the source after corrective implementation, not by hand. |
| `scripts\gen_explorer_data.py`; `scripts\check_explorer_data_drift.py` | Read generator ownership: control objectives come from control Markdown; playbooks supply names/links. No verified-date field was found in this generator. Existing drift check passes; no generator logic change established. |
| `mkdocs.yml`; `docs\controls\CONTROL-INDEX.md` | Identifier/title/navigation matches do not require edits for the established technical discrepancies; no path or title change proposed. |
| `assessment\manifest\generate_manifest.py`; `assessment\manifest\controls.json` | Discovered as control-ID matches, not exhaustively reviewed. Any implementation affecting manifest text must use its generator and re-run downstream guards. |
| `reports\issue-821-reverification.md` | Historical evidence of the existing audit-delay correction in the PowerShell sibling and 3.9 guidance; preserve, do not rewrite. |

Initial broad search for control identifier/title/helper names matched 188 paths, including vendor/package-version false positives and historical monitoring/release records. A second symptom search identified additional dependency excerpts. This report lists reviewed relevant excerpts, **not** all 188 paths as fully reviewed. The remaining linked controls, lifecycle/checklist/evidence pages, licensing/role requirements and derived surfaces require completion by the implementation owner before issue closure.

## Generators and validation

No content source was corrected, so there is no accepted semantic change to propagate into a graph, manifest or catalog. No `scripts\build_content_graph.py` was found. `mkdocs build --strict` ran the repository's registered site/assessment generation hooks. The generated site passed completeness, metadata and internal-link checks; checked-in build timestamps/test-fixture timestamps were restored rather than included as unrelated changes.

| Command | Result |
|---|---|
| `mkdocs build --strict` | PASS, exit 0; build completed in 102 seconds. MkDocs Material printed its upstream MkDocs 2.0 advisory, not a strict-build failure. |
| `python scripts\verify_build_output.py site` | PASS, exit 0. |
| `python scripts\verify_meta_tags.py site` | PASS, exit 0. |
| `python scripts\verify_doc_links.py site --json _broken-links.json` | PASS, exit 0; 697 pages, zero broken internal links. Temporary JSON removed. |
| `python scripts\verify_controls.py` | PASS, exit 0; 79 controls, required sections and standard playbooks. |
| `python scripts\verify_version_stamps.py --check` | PASS, exit 0. |
| `python scripts\verify_prose_counts.py --check` | PASS, exit 0. |
| `ruff check .` | PASS, exit 0. |
| `python scripts\verify_xref_graph.py` | PASS, exit 0; no broken IDs or mislabeled cross-references. |
| `python scripts\check_manifest_doc_drift.py --check` | PASS, exit 0. |
| `python scripts\check_explorer_data_drift.py --check` | PASS, exit 0. |
| `python scripts\verify_language_rules.py` | PASS, exit 0; existing declared quotation exceptions remain. |
| `python scripts\verify_commercial_scope.py` | PASS, exit 0. |
| `npx --no-install playwright test --project=smoke` | FAIL, exit 1: no project named smoke after restoring locked dependencies. Initial attempt also exposed missing local packages. |
| `npm ci --ignore-scripts --no-audit --no-fund` | PASS, exit 0; locked worktree-local test dependencies restored after missing-package failure. No dependency manifest/lock change. |
| `npm run test:e2e:smoke` (initial supported-selector run) | FAIL, exit 1: Chromium headless-shell executable missing; 13 failed launches, one test passed and one did not run. |
| `npx --no-install playwright install chromium --only-shell` | PASS, exit 0 with `PLAYWRIGHT_BROWSERS_PATH` set to ignored worktree-local `maintainers-local\tmp\ocean-912-playwright`; no shared browser-cache mutation. |
| `npm run test:e2e:smoke` (browser-restored run, same local browser path) | FAIL, exit 1: six passed, nine failed in 4.8 minutes. Failures include waiting for the SPA's "Start New Assessment" button; the local server also returned 404 for `javascripts/assessment-data.json`. Root cause not diagnosed or attributed to this report-only change. |

The local smoke server served HTTP requests and shut down after the runner completed; no listener remained on port 8765. Browser traces, screenshots and videos remain local in ignored test-output directories. No Windows snapshots are committed. The full repository CI suite was not run and is not claimed green.

## Trusted-parent handoff

Do not publish this report as a completed fix or close issue 912. Route content correction and complete re-verification to linus, with rusty for any real implementation/workflow surface reached during discovery. Preserve the regulatory/compliance boundary. Only the trusted parent may create remote follow-up artifacts after its lease/commit verification.
