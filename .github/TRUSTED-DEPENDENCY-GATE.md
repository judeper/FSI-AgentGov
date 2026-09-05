# Trusted dependency-artifact gate — **BLOCKED pending owner provisioning**

This policy branch supplies a base-controlled evaluator, an exact remote
ruleset plan, a least-privilege GitHub App contract, and a read-only/apply/
read-back operator script. It does **not** create an App, change repository
settings, or make the artifact gate enforced.

## Remote state read-back — September 5, 2026

An owner-authenticated read-only REST read-back on **September 5, 2026**
(GitHub response `Date: Sat, 05 Sep 2026 02:08:29 GMT`)
resolved `gh api user` to `judeper` and confirmed:

- `judeper/FSI-AgentGov` is public, owned by a `User`, and defaults to `main`;
- `GET /repos/judeper/FSI-AgentGov/rulesets?includes_parents=true` returned
  `200 []`, so the managed ruleset is not active;
- `GET /repos/judeper/FSI-AgentGov/branches/main/protection` returned an
  active strict legacy branch-protection document with `enforce_admins=true`,
  force-pushes blocked, deletions blocked, `required_signatures=false`,
  `required_linear_history=false`, `required_conversation_resolution=false`,
  and all three merge methods enabled. It contains these **13 App-bound
  checks** (`app_id=15368`): `e2e-smoke`, `gitleaks`, `dependency-review`,
  `Analyze (python)`, `Analyze (javascript)`, `mkdocs-strict`,
  `verify_version_stamps`, `ruff`, `pytest (assessment + scripts)`,
  `manifest / index / nav drift`, `FSI language rules`,
  `autodoc-redirect-verify`, and `autodoc-verify`.

An earlier non-admin read using `judep_microsoft` returned `404` for branch
protection because GitHub masks that resource without permission; it was **not
evidence that protection was absent**. The planned ruleset is additive and
must preserve this complete legacy state. No enforcement-active claim is made
until App provisioning and the full read-back succeed.

The owner-token probe of `GET /repos/judeper/FSI-AgentGov/installation` returned
HTTP `401` (`A JSON web token could not be decoded`) on the same date. The
operator therefore does not treat that endpoint as user-token evidence: App
identity and installation verification use the documented App JWT path.

## Chosen non-spoofable mechanism

The planned mechanism is a repository branch ruleset requiring the check named
`trusted-dependency-artifact` from one explicit dedicated GitHub App
`integration_id`. The intended payload is
`.github/trusted-policy/trusted-dependency-artifact-ruleset.plan.json`.

The GitHub REST ruleset schema supports a required status check with an
`integration_id`; a familiar check name alone is not evidence of its
publisher. A candidate workflow or same-name GitHub Actions run cannot satisfy
the planned requirement unless it is published by the dedicated App.

Required-workflow binding is not selected. GitHub documents that required
workflows are an organization/enterprise ruleset capability, while this
repository is personal-user owned. This branch therefore does not claim that
feature is available here.

## Base-controlled evaluator

`.github/workflows/trusted-dependency-artifact.yml` is a **non-enforcing
preflight**, not the required check. It uses `pull_request_target`, checks out
the immutable event base SHA only, grants `contents: read` only, and never
checks out, installs, imports, executes, or interpolates candidate content.
The dedicated App service is the only component permitted to publish the
authoritative check.

The evaluator uses one canonical repository-path identity:

1. reject non-strings, empty/overlong paths, NUL/control characters,
   backslashes, absolute paths, empty segments, and `.`/`..` segments;
2. normalize Unicode to NFC while retaining the canonical spelling;
3. ASCII-case-fold the canonical spelling for Git/Windows collision safety.

It precomputes folded identities for every trusted/guarded exact path,
prefix/suffix, forbidden basename, vendor root, package/lock/provenance/
artifact/documentation/config path, and activation pin. The collision map
contains every base/head tree path plus base protected identities. It rejects
duplicates, NFC/case collisions, directory/file prefix collisions, and any
case/NFC alias of a protected or forbidden identity even when the canonical
spelling is absent. The same identity is used for PR records,
`previous_filename`, immutable tree diffs, vendor scans, forbidden names,
artifact presence, and the final not-applicable decision.

The evaluator retains exact rename and race checks, immutable base/head tree
comparison, base-owned policy material, and command-free-document handling.
Candidate README bytes are data and are never shell-scanned, executed, or
trusted because they contain a familiar command.

## Exact activation and rotation model

The policy branch contains no package, lockfile, or vendored artifact bytes.
Activation is an all-or-nothing exact-byte transaction for approved commit
`8acd5d7907d9ef01e2875855fdd83b307a1e2edd` (parent
`0326a993c09f7f370d38bdb51a3818570867872d`). The complete allowed activation
set is enumerated in `dependency-artifact-policy.json` and includes the
package/lock/gitattributes files, the vendor tarball/provenance/README,
required verifier/runtime files, security workflows, `SECURITY.md`, and the
four focused tests. Every allowed path has an exact Git blob ID, raw-byte
SHA-256, and size. Any extra path or byte change fails closed.

After activation, the effective exact pins continue to apply. Ordinary PRs
cannot change the artifact, package manifests, lockfiles, `.gitattributes`,
verifier/runtime bytes, or activation files. A rotation is policy-first:
trusted policy owners land a standalone pin/policy PR, the new policy
intentionally blocks the old artifact, and only then does a separate
exact-match artifact PR land. There is no unguarded interval and no policy
plus artifact PR.

## Owner/App credential and apply contract

The operator keeps two credentials separate:

- **Owner credential:** `GH_TOKEN` or `gh auth` authenticated as `judeper`;
  it performs owner-only plan/create/read/delete ruleset operations.
- **App credential:** a short-lived JWT generated at runtime from the App ID
  and a private key supplied through `GITHUB_APP_PRIVATE_KEY_PATH` or
  `GITHUB_APP_PRIVATE_KEY`. The helper reads the key only in memory, never
  commits, persists, logs, echoes, or passes it to candidate code.

The App must be installed only on `judeper/FSI-AgentGov` with exactly
`metadata:read`, `contents:read`, `pull_requests:read`, and `checks:write`.
The App contract includes the `pull_request`, `check_suite`, and `check_run`
webhooks; if merge queue is enabled later, it additionally requires
`merge_queues:read` and `merge_group`. Extra permissions/events fail closed.
The webhook secret is runtime-only and must be rotated, timestamp/replay
bounded, and HMAC-signature validated before processing a payload. The App
must scope installations to this repository and must never execute candidate
content.

Before create, Apply verifies owner identity/admin access/repository/branch,
App JWT identity, exact installation, permissions/events, ruleset API
capability, expected `integration_id`, and **two nominated probes**:

1. a positive no-op PR whose exact head has a successful dedicated-App check
   and unambiguous `mergeable=true`, `mergeable_state=clean`;
2. a separate negative PR with only a successful same-name
   `github-actions` check whose exact head is `mergeable=false`,
   `mergeable_state=blocked`.

If either probe is absent, ambiguous, or unexpectedly passes, Apply refuses.
Read-back reports `verified=true` only after the same positive and negative
probes pass, the managed ruleset matches every security-relevant field, and
the complete legacy branch-protection state is unchanged. If an API cannot
directly report required-check satisfaction, these exact mergeability probes
are the required fallback; ambiguous states fail closed.

Apply is create-only: it refuses to update or replace an existing managed
ruleset. If post-create verification fails, the documented automatic rollback
reads the returned ruleset and history, confirms the returned ID/name,
intended security digest, creation time, and owner actor, then deletes **only
that newly created ID**. If the POST response is lost, it first reconciles one
unambiguous new managed ID against the pre-create snapshot. It never deletes a
pre-existing ruleset. If identity or creator/time proof is unavailable, rollback
is refused and owner attention is required; the operation is not reported as
success.

The exact commands and sequencing are in
`.github/trusted-policy/PRETRUST-REVIEW-RUNBOOK.md`. Until provisioning and
read-back complete, the artifact gate remains **BLOCKED and non-enforced**.
