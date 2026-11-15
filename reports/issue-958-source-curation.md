# Issue 958: Sensitivity-label citation reconciliation blocked

**Checked:** 2026-11-15
**Worker:** Linus
**Repository:** judeper/FSI-AgentGov
**Disposition:** Stopped before implementation because current official sources conflict on encrypted SharePoint grounding. No documentation correction or publication is claimed.

## Baseline and overlap

An unauthenticated, read-only public GitHub REST check returned current `main`
as `9016ee9ceb0e53470ef424b4d4c5de4cf45b6c28`, matching the starting local HEAD.
The accepted sensitivity reference is present in
`docs/reference/microsoft-learn-urls.md`. No historical reset was performed.

All six open target-repository PR file inventories were inspected: #1961,
#1960, #1958, #1957, #1906, and #1887. None touches the four scoped 1.26
documents. The open-issue response contained 93 entries, including PRs, and
did not require another page. Relevant source-review alerts are:

- #1982: the old Copilot Studio sensitivity-label URL; human-review escalation,
  no draft attempted.
- #1891: the general Purview sensitivity-label page; human-review escalation,
  no draft attempted.
- #1881: the Purview encryption/sensitivity-label page; human-review escalation,
  no draft attempted.

These alerts are not evidence of an executable overlapping implementation.
They remain untouched; this report does not resolve their source lineage.

## Blocking official-source ambiguity

Both pages below were retrieved successfully from Microsoft Learn during this
run. Their encryption statements cannot safely be combined into an affirmative
support claim for the scoped instructions.

| Official source | Retrieved statement | Consequence |
|---|---|---|
| [Purview: Sensitivity labels and AI interactions](https://learn.microsoft.com/en-us/purview/ai-copilot-studio#sensitivity-labels-and-ai-interactions) | Users need EXTRACT as well as VIEW when a label applies encryption. Its Copilot Studio-specific guidance says: "Encryption is supported only with sensitivity labels, and only for the SharePoint knowledge source." | Describes conditional support for label-encrypted SharePoint content. |
| [SharePoint knowledge sources do not return results: protected content](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/knowledge/sharepoint-no-response#content-is-protected-by-sensitivity-labels-dke-or-a-password) | The agent-level SharePoint source respects label permission trimming, but "the agent can't extract or ground on content whose protection encrypts the file." It explicitly includes encrypting labels, DKE, and password protection, even where an item is Ready and openable by the user. | Describes a grounding limitation for label-encrypted SharePoint files without stating that VIEW/EXTRACT rights remove it. |

The Purview page identifies source commit
`d97e409d50022299b253e6de9060f0641ba23d37` and an `updated_at` value of
`2026-06-25T22:34:00Z`. The troubleshooting page identifies source commit
`f385ca239370a18977c829042821b500ef8d8232` and an `updated_at` value of
`2026-08-06T18:07:00Z`. A later timestamp alone does not establish that one
statement supersedes the other or define a reliable path-specific exception.

The Purview section also documents SharePoint (including OneDrive) and
Dataverse with Data Map auto-labeling, response/citation label display using
label priority, and separate inheritance for newly created Word and PowerPoint
content. Those statements do not resolve the encrypted-grounding conflict,
establish universal runtime-upload coverage, or independently recertify the
historical preview/shield UI assertions in the scoped documents.

## Scope and impact

The four requested files were read completely. Their seven stale citations
remain unchanged:

| File | Old citations |
|---|---:|
| `docs/controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md` | 3 |
| `docs/playbooks/control-implementations/1.26/verification-testing.md` | 1 |
| `docs/playbooks/control-implementations/1.26/troubleshooting.md` | 2 |
| `docs/playbooks/control-implementations/1.26/portal-walkthrough.md` | 1 |

The task explicitly makes source ambiguity a stop condition. Accordingly, no
replacement wording was authored, no preview/GA or licensing/billing conclusion
was finalized, and no UI or tenant behavior was tested. No metadata, frozen
report, monitor state, redirect policy, validator, infrastructure, or dependency
was changed. This new report is the only worker change.

## Validation and handoff

Strict MkDocs, built-site/internal-link, language, and control validators were
not run: implementation stopped before any of the four documentation files
was edited. This report is not evidence that those gates pass or that the
requested reconciliation is complete.

The trusted parent must resolve or obtain authoritative clarification of the
encrypted-grounding discrepancy before authorizing implementation. Independent
review and publication have not occurred. The worker performed no remote writes,
used no `gh` commands, and did not inspect credentials or authentication state.
Any remote status update or publication remains the trusted parent's responsibility.
