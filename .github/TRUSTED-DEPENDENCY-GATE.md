# Trusted dependency-artifact gate — **BLOCKED pending owner provisioning**

This policy branch supplies a base-controlled evaluator, an exact remote
ruleset plan, a GitHub App contract, and a read-only/apply/read-back operator
script. It does **not** create an App, change repository settings, or make the
artifact gate enforced.

As observed through authenticated, read-only GitHub REST requests on
**September 5, 2026**, `judeper/FSI-AgentGov` is a public repository owned by a
`User`; `GET /repos/judeper/FSI-AgentGov/rulesets` returned `200 []`, and
`GET /branches/main/protection` returned `404`. Therefore no ruleset or legacy
branch-protection gate is currently active.

## Chosen non-spoofable mechanism

The planned mechanism is a **repository branch ruleset** requiring the check
named `trusted-dependency-artifact` from one explicit **dedicated GitHub App
integration ID**. The intended payload is
`.github/trusted-policy/trusted-dependency-artifact-ruleset.plan.json`.

The GitHub REST ruleset schema supports a required status check with an
`integration_id`; unlike a name-only context, that binds the accepted result to
the publisher App. GitHub documents that any writer can set a status/check name,
so a familiar name alone is not evidence. A candidate workflow, including one
that runs on a pull-request head or a test-merge commit, cannot satisfy the
planned requirement unless it can publish as the dedicated App.

Required-workflow binding is not the selected mechanism. GitHub documents
ruleset required workflows as organization/enterprise configuration, while this
repository is personal-user owned. The REST schema alone is not proof that this
account can activate the feature, so this branch does not claim that it can.

## What the local preflight does

`.github/workflows/trusted-dependency-artifact.yml` is a **non-enforcing
preflight**, not the required check. It uses `pull_request_target`, checks out
the immutable event base SHA only, grants `contents: read` only, and never
checks out, installs, imports, executes, or interpolates candidate content.
It does not hold `checks: write` and does not publish
`trusted-dependency-artifact`.

The evaluator reads complete pull-file records (`status`, `filename`, and
`previous_filename`) and independently diffs immutable base and candidate
trees. It:

- classifies both sides of a rename; protected-path renames are forbidden;
- rejects truncated base/candidate trees, malformed rename records, unsafe
  separators/control characters/dot segments, protected Unicode-normalization
  collisions, and protected ASCII-case collisions;
- derives whether the artifact is required from the immutable base tree and
  verifies its presence, paths, pins, package/lock/provenance relationships on
  **every** verdict, including nominally not-applicable and policy-only PRs;
- captures event base/head SHA, checks both before evaluation, and rechecks
  both (plus base ref) before returning a verdict.

`/pulls/{n}/files` is evidence for rename intent, never the only classifier.
If it is incomplete while the immutable tree diff contains protected changes,
the evaluator fails closed.

## Documentation boundary

Candidate artifact documentation is not shell-parsed. Instead,
`vendor/npm/fast-uri/3.1.7/README.md` is an exact SHA-256/size pin in the
protected policy and must equal the no-command
`vendor-readme-template.md`. Any byte change, including wrappers, aliases,
backticks, subshells, or PowerShell call operators, fails the pin. All
pre-trust and rotation procedures live in the protected
`PRETRUST-REVIEW-RUNBOOK.md`; `SECURITY.md` and this document are trusted paths.
A policy rotation must be a standalone PR and cannot be combined with a guarded
artifact change.

## Remote provisioning and read-back

The exact owner procedure is in
`.github/trusted-policy/PRETRUST-REVIEW-RUNBOOK.md`. In brief:

1. Independently review and merge this **policy-only** commit under the
   controls that existed before it. This PR cannot protect itself.
2. Provision a dedicated GitHub App according to
   `trusted-dependency-artifact-app-contract.json`; install it only on this
   repository and keep all credentials outside Git.
3. From the merged default branch, run
   `Invoke-TrustedDependencyArtifactRuleset.ps1 -Plan -AppId <id>`.
4. Copy its `liveDigest`, `intendedRulesetDigest`, and `confirmationToken`;
   rerun it with explicit `-Apply` and all three values.
5. Run `-ReadBack -AppId <id> -ProbePullRequest <new-no-op-PR>`.

The script defaults to read-only planning. Apply creates a new, dedicated
ruleset only; it never PUTs the old branch-protection document. It validates the
repository/branch/App installation, aborts on live-state drift, and read-backs
the exact expected source, strictness, reviews/CODEOWNERS, conversation
resolution, force-push/deletion block, linear history, no bypass actors, and
unchanged legacy restrictions/signature state. Any mismatch is failure, not a
partial success.

This plan does not enable merge queue. If it is enabled later, the dedicated App
must publish the same expected-source check on `merge_group.head_sha`; a passing
PR-head check is not a passing test-merge check.

## Registry and advisory facts

Registry publication and advisory search results are deliberately not
enforcement inputs. Direct registry/API evidence must record its date, HTTP/TLS
result, and any mirror condition. A search result, mirror result, or transport
failure does not establish package publication or absence. This branch makes no
volatile claim about availability of `fast-uri` `3.1.7` or `4.1.4`.

On **September 5, 2026**, direct canonical-registry probes for both versions
failed at TLS negotiation (Windows Schannel curl error 35; Node `fetch` also
failed), so this review reached no publication/absence conclusion. GitHub's
advisory API returned live records for four retained regression identifiers and
`404` for two; those mixed results are not used to add, remove, or reinterpret
the historical byte pins or regression identifiers.

## Residual risk

Until the owner provisions the App and the remote ruleset read-back succeeds,
the gate remains **BLOCKED and non-enforced**. The preflight improves evidence
but cannot prevent a merge. After activation, compromise of the repository owner
or the dedicated App is still outside a repository-only control; the App must
be independently operated and credentialed.
