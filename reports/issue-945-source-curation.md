# Issue #945 - Copilot Studio sensitivity-label reference curation

**Observed:** 2026-11-11

**Author:** Linus. Research assistance checked official sources; this is not an independent reviewer verdict.

## Immutable base and scope

Base: `b37ac79e5e27b91922a9a55029fdbe17c4f50b47` on local branch
`ocean/issue-945`. Local HEAD, `origin/main`, and a public read-only
`git ls-remote` of `refs/heads/main` agreed before editing. The trusted parent
must revalidate the candidate and then-current main before publication.

The original row at `docs/reference/microsoft-learn-urls.md:88` was:

```text
| **Sensitivity Labels in Copilot Studio** | https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio | Oct 2026 |
```

Only its URL and row-specific verification month change. The caption, other
rows, aggregate counts, and page footer remain unchanged. This report is the
directly coupled provenance/impact record, not another published reference page.

This is a new bounded technical-curation candidate related to
[original PR #1926](https://github.com/judeper/FSI-AgentGov/pull/1926), not a
revision of its supplied head `c80248d5036c33c3e3b98e0b5bb6ec8ae15e05dd`.
Its gate failures and run IDs are issue-supplied context, not independently
verified run results. The redirect gate correctly restricts automated swaps;
this manually curated change also updates the verification month and must not
be represented as a redirect-only candidate.

Read rules: `CONTRIBUTING.md`, `.github/copilot-instructions.md`, Linus's local
charter, `.squad/skills/repo-context.md`, the applicable build/language/scope/git
instruction files, `.github/prompts/review-learn-changes.prompt.md`, and the
source-support, isolation, fail-closed and independent-review rules in
`.github/AUTODOC-RUNBOOK.md`. No validator, policy, workflow, executable,
monitor baseline, or review requirement changes.

## Official source evidence

Live Microsoft Learn fetch/search research was followed by a direct full-page
fetch of the selected source. Routing was separately measured with public
unauthenticated `curl.exe --location` requests on the observation date.
HTTP success is routing evidence only, not the basis for topic equivalence.

| Source | Observed title and routing | Precise relevance |
|---|---|---|
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio | "Configure data policies for agents"; one redirect to `https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention`, final HTTP 200 | Connector data policies, authentication and channel restrictions are not a replacement for sensitivity-label response display. Do not rename the reference to DLP. |
| https://learn.microsoft.com/en-us/purview/ai-copilot-studio#sensitivity-labels-and-ai-interactions | "Use Microsoft Purview to manage data security & compliance for Microsoft Copilot Studio"; base page returns HTTP 200 without redirects; fetched heading is "Sensitivity labels and AI interactions" | The capability table explicitly supports sensitivity labels. The section says agents built in Copilot Studio "display the sensitivity label for items listed in the response and citations" and that the latest response displays the "highest priority sensitivity label" from the data used. This is the original reference's response-label purpose, not keyword-only equivalence. |
| https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/knowledge/sharepoint-no-response | "SharePoint knowledge sources don't return results in Copilot Studio"; content fetched by research assistance; redirect chain not measured | Its "Content is protected by sensitivity labels, DKE, or a password" section says agent-level SharePoint knowledge respects labels for permission trimming, but cannot extract or ground on encrypted content. This limits any broader implementation claim. |

The selected Purview source explicitly scopes support to SharePoint (including
OneDrive) and Dataverse with Data Map auto-labeling policies. It says encryption
support is limited to labeled SharePoint content and that EXTRACT and VIEW
rights are required. The troubleshooting source describes encrypted-content
grounding failures. These sources leave an implementation-specific tension:
this change does not resolve it or certify encrypted-file processing.

The selected source also conditions Purview management of agents on non-Microsoft
channels on pay-as-you-go billing. No universal source/channel coverage, preview
graduation, licensing entitlement, agent-level label inheritance, regulatory
interpretation, or tenant-tested behavior is asserted. The section link is
topic-equivalent evidence, not proof that all historical claims remain current.

Historical context only: `reports/monitoring/learn-changes-2026-10-04.md`
records the old article's title, "View sensitivity labels in agent responses
(preview)", and highest-label response/citation display. The November 6 report
records replacement by DLP content. These reports help identify the original
purpose; they are not current Microsoft authority.

## Changed/unchanged impact ledger

Exact old-URL/topic discovery across `docs`, `data`, and `reports` found 37
matches in 16 files before this report was added. The following ledger covers
every matched file. Source references were searched, not all sensitivity-label
behavior across the framework; other source lineages are not recertified.

| Artifact | Disposition and remaining limit |
|---|---|
| `docs/reference/microsoft-learn-urls.md` | Changed: one reference row, same sensitivity-label caption; URL targets the official topic section and verification month becomes November 2026. |
| `reports/issue-945-source-curation.md` | Added: bounded provenance, impact and validation record. |
| `docs/controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md` | Unchanged: three old-URL citations remain; existing preview, response-display and auto-labeling claims are not recertified. Separate follow-up is needed for those citations and claims. |
| `docs/playbooks/control-implementations/1.26/verification-testing.md` | Unchanged: one response-label documentation citation still routes to DLP; no testing procedure was recertified. |
| `docs/playbooks/control-implementations/1.26/troubleshooting.md` | Unchanged: two old-URL citations remain, including a preview/response-shield claim; implementation review is outside this row-only correction. |
| `docs/playbooks/control-implementations/1.26/portal-walkthrough.md` | Unchanged: one old-URL preview citation remains; no UI or availability verification is claimed. |
| `data/monitor-state.json` | Unchanged: historical monitor key/topic is not advanced or migrated by this curation. |
| `data/monitor-pending/learn/learn.microsoft.com-en-us-microsoft-copilot-studio-sensitivity-label-copilot-studio-96e8c869375efdbca29c037c.json` | Unchanged: pending source lineage remains for the trusted workflow to reconcile. |
| `reports/monitoring/learn-changes-2026-03-11.md`, `learn-changes-2026-04-28.md`, `learn-changes-2026-07-12.md`, `learn-changes-2026-09-22.md`, `learn-changes-2026-10-04.md`, `learn-changes-2026-11-06.md`, `learn-changes-2026-11-07.md`, `learn-changes-2026-11-10.md`, `learn-changes-2026-11-11.md` (all under the same directory) | Unchanged: nine historical observation records, not current instructions to rewrite. |

The daily monitor reads the watchlist (`scripts/learn_monitor.py`); the new
section URL can create a different monitored identity. Existing state/pending
records are deliberately preserved, not certified resolved or silently reset.
Consumers linking to the watchlist page retain the same page path and headings.
The Learn URL occurrence count remains 228; existing approximate header/footer
counts of 231 remain within the validator's tolerance.

## Validation and handoff

| Command/check | Actual outcome |
|---|---|
| `mkdocs build --strict` | Passed, exit 0; final candidate built in 83.58 seconds, with no MkDocs warning/error log entries. Material emitted its existing startup notice about MkDocs 2.0; this is not a source-validation result. |
| `python scripts\verify_build_output.py site` | Passed, exit 0; 43 reference and 86 control HTML pages, populated search index. |
| `python scripts\verify_meta_tags.py site` | Passed, exit 0; eight required tags on three sampled pages. This is the validator's sampling scope, not an all-page metadata certification. |
| `python scripts\verify_doc_links.py site --json <session-files>\issue-945-broken-links.json` | Passed, exit 0; final stable site scanned 697 pages with no broken internal links. External URLs are not covered by this check. |
| `python scripts\verify_language_rules.py` | Passed, exit 0; no prohibited language, four existing review exceptions reported. |
| `python scripts\verify_commercial_scope.py` | Passed, exit 0; 674 forward-facing files scanned. |
| `python scripts\verify_learn_urls_count.py --check` | Passed, exit 0; actual 228, both approximate counts 231, within existing tolerance. |
| `python scripts\verify_controls.py` | Passed, exit 0 on the unchanged control/playbook surfaces; 79 controls, required structure, four standard playbooks and documentation anchors. |
| `python scripts\verify_xref_graph.py` | Passed, exit 0 on unchanged cross-reference surfaces; 538 files, 6,163 references, no broken IDs or mislabeled references. |
| Exact row comparison against immutable base and generated reference HTML assertion | Passed: the reference file equals the base with exactly the specified row replacement, and the selected URL occurs in built HTML. |
| `git diff --check` | Passed, exit 0. |

An initial shell wrapper split `--check` into characters and the count validator
rejected that invocation (exit 2). The explicit command above then passed; this
was not a validator defect. An earlier link scan overlapped the final rebuild
and reported only one page; it was discarded as incomplete evidence. The final
ordered built-site checks ran after the rebuild without another concurrent
build and scanned all 697 HTML pages. Build-generated changes to tracked
`docs/version.json` were removed; that file is byte-identical to the base.

The final build log and machine-readable link result are local session
artifacts, not committed tenant evidence. No tenant access, regulatory review,
remote CI execution, immutable-base gate execution against a remote PR, or
independent approval occurred. Existing CI and immutable-base gates remain
unchanged and must run through the trusted-parent publication path.

Publication and independent review remain pending. Only the trusted parent may
push or create a replacement PR, revalidate the lease/base/candidate and required
checks, or update issue #945. No original-PR closure, approval transfer, manual
CI retry, merge, or post-rejection author cycle is authorized.
