# Trusted dependency-artifact gate — **BLOCKED pending owner provisioning**

This policy branch supplies a base-controlled evaluator, an exact remote
ruleset plan, a least-privilege GitHub App contract, and a read-only/apply/
read-back operator script. It does **not** create an App, change repository
settings, or make the artifact gate enforced.

## Remote state read-back — September 5, 2026

An owner-authenticated read-only REST read-back on **September 5, 2026**
(GitHub response `Date: Sat, 05 Sep 2026 03:47:06 GMT`)
resolved `gh api user` to `judeper` and confirmed:

- `judeper/FSI-AgentGov` is public, owned by a `User`, and defaults to `main`;
- `GET /repos/judeper/FSI-AgentGov/rulesets?includes_parents=true` returned
  `200 []`, so the managed ruleset is not active;
- `GET /repos/judeper/FSI-AgentGov/branches/main/protection` returned an
  active strict legacy branch-protection document with `enforce_admins=true`,
  force-pushes blocked, deletions blocked, `required_signatures=false`,
  `required_linear_history=false`, `required_conversation_resolution=false`,
  no legacy pull-request-review rule, no actor restrictions, and all three
  merge methods enabled. It contains these **13 App-bound checks**
  (`app_id=15368`): `e2e-smoke`, `gitleaks`, `dependency-review`,
  `Analyze (python)`, `Analyze (javascript)`, `mkdocs-strict`,
  `verify_version_stamps`, `ruff`, `pytest (assessment + scripts)`,
  `manifest / index / nav drift`, `FSI language rules`,
  `autodoc-redirect-verify`, and `autodoc-verify`.

An earlier non-admin read using `judep_microsoft` returned `404` for branch
protection because GitHub masks that resource without permission; it was **not
evidence that protection was absent**. The planned ruleset is additive and
must preserve this complete legacy state. No enforcement-active claim is made
until App provisioning and the full read-back succeed.

An owner token is deliberately not used with App-authenticated endpoints.
App identity and installation discovery use a runtime App JWT; repository
enumeration uses a temporary installation access token.

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

1. reject non-strings, empty/overlong paths, C0/C1 controls, bidirectional
   controls, backslashes, absolute paths, colon/ADS syntax, empty segments,
   `.`/`..` segments, trailing dots/spaces, Windows device names (including
   extension variants), Windows-invalid filename characters, `.git`, and DOS
   short-name aliases;
2. normalize Unicode to NFC while retaining the canonical spelling;
3. conservatively fold ASCII and Unicode case aliases (including long-s and
   dotless-i) for case-insensitive checkout collision safety.

It precomputes folded identities for every trusted/guarded exact path,
prefix/suffix, forbidden basename, vendor root, package/lock/provenance/
artifact/documentation/config path, and activation pin. The collision map
contains every base/head tree path plus base protected identities. It rejects
duplicates, NFC/case collisions, directory/file prefix collisions, and any
case/NFC alias of a protected or forbidden identity even when the canonical
spelling is absent. The same identity is used for PR records,
`previous_filename`, immutable tree diffs, vendor scans, forbidden names,
artifact presence, and the final not-applicable decision. GitHub recursive
trees include `040000` directory entries; `git ls-tree -r -z` omits them unless
`-t` is also supplied. Explicit and implied directories participate in alias
detection but are not files or leaf changes. A directory's changed tree ID does
not expand the exact activation delta. Malformed modes/types/object IDs, missing
tree response fields, truncation, and oversized trees fail closed.

Every `trustedPaths` entry must exist as a regular Git blob in **both** the
immutable base and candidate, with its exact `trustedPathModes` mode (currently
`100644`). This applies even to unrelated PRs: a poisoned base is not a bypass.
Symlinks (`120000`), submodules (`160000`), directories, missing files, and
unapproved executable-bit changes are rejected before any authorization.
Guarded activation files likewise retain their explicitly approved regular
blob modes on both sides. A helper cannot redirect trust to an unguarded
destination by becoming a symlink. A relocation requires protecting and
materializing the destination in a separate reviewed policy step **before**
trusted code can load it; existing trusted paths are not silently retired.

The evaluator retains exact rename and race checks, immutable base/head tree
comparison, base-owned policy material, and command-free-document handling.
Candidate README bytes are data and are never shell-scanned, executed, or
trusted because they contain a familiar command.

## Exact activation and rotation model

The policy branch contains no vendored artifact bytes and does not activate the
package change. Activation is an all-or-nothing, base-relative exact tree delta
defined by policy version 2 and patch digest
`a9cc1b76042703c570dcd4a95575fbf54880e58f4ae8a26d35e2d9ea0c482425`.
The 16-path set includes package/lock/gitattributes files, the vendor
tarball/provenance/README, verifier/runtime files, two security workflows, and
five focused tests. `SECURITY.md` and every trusted policy, runbook, gate
workflow, and operator path are excluded; `activation.allowedFiles` has an
empty intersection with `trustedPaths`.

Each activation path has an exact immutable-base state (blob+mode or required
absence) and an exact target mode, Git blob ID, raw-byte SHA-256, and size.
Before the artifact exists, **any** guarded or activation-path change is
rejected unless the immutable base/head delta equals all 16 paths exactly and
every base and target pin matches. There is no `guard-only` success for a
manifest, lockfile, attributes file, verifier, workflow, test, or artifact
documentation change.

The former artifact commit/parent pair is not an approved lineage. The future
artifact branch must be recreated from the merged policy head. Its only
permitted delta is the pinned 16-path patch. The new `security-scan.yml` target
retains the policy branch's `permissions: {}` hardening while adding the
reviewed artifact steps; all other target blobs are identified individually by
the new pin set. If any base pin has moved, policy owners must review and issue
a new base-relative patch instead of reusing the old branch.

The acceptance-test target is the exact blob tracked at
`.github/trusted-policy/trusted-gate-artifact-acceptance.template.mjs`; copy its
raw Git blob, not a CRLF-converted working-tree rendering. The template checks
the current schema and both immutable trees instead of the removed
`artifactRequiredByBase`/caller-supplied activation override contract.
The already-approved security workflow target is also stored, unchanged, at
`.github/trusted-policy/security-scan.activation.yml` so its exact Git blob
survives independently of an unreferenced local reconstruction.
Policy-stage tests verify the schema, templates, and synthetic exact-activation
attack cases. With the reviewed artifact objects available locally, set
`TRUSTED_GATE_VALIDATE_PLANNED_BLOBS=1` to additionally replay every real target
pin without activating packages or executing candidate code; missing objects
then fail, rather than skipping tests. The actual artifact branch always runs
that acceptance suite. The older acceptance-test blob is no longer approved.

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

Both code paths are pinned to `https://api.github.com` and `github.com`.
Production rejects ambient `GITHUB_API_URL`, `GITHUB_SERVER_URL`, or `GH_HOST`
values that point elsewhere. The operator lists every App installation with the
JWT, obtains the target installation, creates a short-lived installation
token, paginates the documented `GET /installation/repositories` endpoint,
requires exactly `judeper/FSI-AgentGov` and the approved permissions, and
rejects an invalid or overlong expiry (at most one hour), and revokes the
temporary token on success and validation failure. Installation and repository
pages are explicitly enumerated into scalar records; duplicate IDs, changing
totals, incomplete pages, and nested/malformed repository payloads fail closed.
REST redirects are disabled so an otherwise pinned request cannot forward an
App credential to another origin.

The App must be installed only on `judeper/FSI-AgentGov` with exactly
`metadata:read`, `contents:read`, `pull_requests:read`, and `checks:write`.
The App contract includes the `pull_request`, `check_suite`, and `check_run`
webhooks; if merge queue is enabled later, it additionally requires
`merge_queues:read` and `merge_group`. Extra permissions/events fail closed.
The current operator refuses any active merge queue until a later reviewed
policy adds equally fresh, signed merge-group evidence.
The webhook secret is runtime-only. The independently reviewed evaluator must
be deployed outside this repository, validate `X-Hub-Signature-256` before
processing, de-duplicate delivery IDs, capture a trusted receiver timestamp,
scope the installation to this repository, and never execute candidate
content. GitHub does not provide a signed timestamp header, so freshness is
anchored to the receiver clock and the resulting check-run timestamps.

Before create, Apply verifies owner identity/admin access/repository/branch,
App JWT identity, the App's only installation, exact repository enumeration,
permissions/events, ruleset API capability, expected `integration_id`, and the
reviewed evaluator origin (also bound into the confirmation token).
It then creates the additive ruleset. Only **post-creation** evidence from two
nominated probes can complete the transaction:

1. a positive no-op PR whose exact head has a successful dedicated-App check
   in `not-applicable` mode and unambiguous `mergeable=true`,
   `mergeable_state=clean`;
2. a separate negative partial-activation PR with a failed dedicated-App check
   in `activation-rejected` mode plus a successful same-name `github-actions`
   check, whose exact head remains conflict-free (`mergeable=true`) but
   `mergeable_state=blocked`.

After ruleset read-back, the operator emits two fresh 256-bit, non-secret
challenge nonces through its local console. The evaluator accepts them only
through its authenticated out-of-band control plane. The operator also
requires each check's `details_url` origin to equal the independently reviewed
external evaluator origin supplied at runtime. Each evaluator check's
canonical base64url `external_id` binds the exact challenge nonce, repository,
PR number, head SHA, base SHA, immutable-base policy version and canonical-JSON
SHA-256, evaluator verdict mode, and trusted receiver timestamp. The
operator rejects stale/pre-ruleset timestamps, wrong or reused nonces, missing or
mismatched PR associations, wrong policy coordinates, and stale same-name
Actions runs. Apply polls only for this fresh evidence; pre-existing checks
cannot authorize creation. Read-back reports `verified=true` only after the
same causal probes pass, the managed ruleset matches every security-relevant
field, and the complete legacy branch-protection state is unchanged.

Checks are fetched with `filter=all` and complete, count-checked pagination.
The newest run from each required source must satisfy the proof; an older
success cannot mask a newer failed, pending, malformed, or stale run. GitHub's
compact check association omits repository `full_name`. The operator requires
that field from a separately read-back full PR, verifies the compact
association's exact PR ID/number/URL, repository ID/name/API URL, ref, and head/base
SHA against it, and only then supplies `full_name` to the strict check validator.
Missing or conflicting fields are not inferred from requested coordinates.
The PR is re-read after pagination and its final mergeability is used.

Apply is create-only: it refuses to update or replace an existing managed
ruleset. If post-create verification fails, the documented automatic rollback
reads the returned ruleset and history, confirms the returned ID/name,
intended security digest, creation time, and owner actor, then deletes **only
that newly created ID**. If the POST response is lost, it first reconciles one
unambiguous new managed ID against the pre-create snapshot. It never deletes a
pre-existing ruleset. If identity or creator/time proof is unavailable, rollback
is refused and owner attention is required; the operation is not reported as
success.
Before creation the complete live security snapshot is checked again. After
rollback, the snapshot must equal the pre-create snapshot; concurrent drift
requires owner attention rather than a success claim.

The exact commands and sequencing are in
`.github/trusted-policy/PRETRUST-REVIEW-RUNBOOK.md`. Until provisioning and
read-back complete, the artifact gate remains **BLOCKED and non-enforced**.
