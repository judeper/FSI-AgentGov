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

The preflight CLI emits one JSON verdict on stdout and exits with status 0
(success) or 1 (failure). It exports no step outputs and does not write
network-derived verdicts to `GITHUB_OUTPUT` or other runner files.

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
Activation behavior is selected only by the immutable-base policy through a
closed validation mode. Policy version 3 uses `exact-pins`: the evaluator
classifies both immutable trees from every `activation.basePins` and
`activation.pins` entry. The older `vendored-artifact` mode remains supported
for reviewed policies that intentionally use tarball presence and its complete
companion-file set as activation state. A candidate cannot select or alter the
mode used to judge itself.

Guarded activation files likewise retain their explicitly approved regular
blob modes on both sides. In `exact-pins` mode, the selected pre-state or
post-state determines which mode pin applies. A helper cannot redirect trust
to an unguarded destination by becoming a symlink. A relocation requires
protecting and materializing the destination in a separate reviewed policy
step **before** trusted code can load it; existing trusted paths are not
silently retired.

The evaluator retains exact rename and race checks, immutable base/head tree
comparison, base-owned policy material, and command-free-document handling.
Candidate README bytes are data and are never shell-scanned, executed, or
trusted because they contain a familiar command.

## Exact activation and rotation model

This policy-only branch does not activate the package change. Policy version 3
selects the closed `exact-pins` mode and authorizes one all-or-nothing,
base-relative two-file registry transaction with patch digest
`ce866287d558a90428d4656e8e0f7456263bc72e52426488c09d29dc9dcbff43`:

| Path | Immutable base | Exact target |
|---|---|---|
| `package-lock.json` | mode `100644`, blob `08aafb595607f78f0a0998b022a2cebe920bb257` | mode `100644`, blob `11b6591aa1b39b50d451005dae574fb465f66871`, SHA-256 `4eeef37fa3ff1b558fbb40829786791591807f400aa5907b6388f9ebe5c3e3d1`, 76,919 bytes |
| `tests/spa/fast-uri-security.test.mjs` | absent | mode `100644`, blob `a43678648562f3b13a40ca672ce81953b89c1b2a`, SHA-256 `0b23c08eb971f8f787a284a966a014e4fbd70acad01bba121cb614a5a96245bd`, 2,573 bytes |

No `package.json` override, vendored tarball/provenance/README, workflow,
`.gitattributes`, verifier/runtime file, or `SECURITY.md` is an activation
target. The security workflows, verifier/runtime paths, `.gitattributes`,
package manifests and lockfile, vendor root, former focused tests, and the new
fast-uri security test remain guarded after removal from the old activation
set.

For each immutable tree, all base pins must match (pre-state) or all target
pins must match (post-state); every mixed or poisoned state is invalid. An
invalid base fails every pull request. The only accepted transition is the
exact pre-state to the exact post-state with no extra changed path. Partial
updates, extra files, reversion, rename or alias tricks, changed modes, and
altered bytes fail closed. Once activated, every pull request revalidates both
target files by mode, Git blob ID, raw-byte SHA-256, and size, even when the
reported pull-file list is unrelated.

`exact-pins` mode does not run tar, provenance, packed-manifest, or vendored
artifact checks and never fetches, installs, imports, or executes candidate
package code. The evaluator reads only repository blobs needed for structural
checks and exact pin validation. The `vendored-artifact` mode and its synthetic
regressions remain available as a backward-compatible evaluator capability,
but it is not selected by policy version 3.

The trusted
`.github/trusted-policy/security-scan.activation.yml` file is retained only as
the canonical workflow target for that legacy vendored mode. It is inert
policy material, not an active workflow, and the policy v3 `exact-pins`
transaction does not consume it.

The future activation branch must be recreated or rebased from the merged
policy-v3 head. Its only permitted delta is the two pinned files above. If
either base pin has moved, policy owners must stop and issue another standalone
policy review instead of adapting the activation branch. The tracked
`trusted-gate-artifact-acceptance.template.mjs` can replay the exact pre/post
trees when the target Git objects are locally available; setting
`TRUSTED_GATE_VALIDATE_PLANNED_BLOBS=1` makes missing target objects fail rather
than skip that replay.

Further changes remain policy-first: trusted policy owners merge a standalone
pin/policy pull request, then a separate exact-match dependency pull request.
There is no unguarded interval and no combined policy-plus-dependency pull
request.

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

Both received GitHub timestamps and generated decision clocks use the same
strict UTC normalizer: invariant Gregorian dates, colon-separated time, and an
uppercase `Z`. Probe observation times and the apply/rollback transaction
boundaries never use the host's culture or calendar. Offset, local, ambiguous,
malformed, stale, future, and non-causal evidence is still rejected; the
five-minute probe window and rollback identity/chronology checks are unchanged.
The executed operator regressions cover Invariant, `fi-FI`, `ar-SA`, and `fr-FR`
cultures through real plan/apply, probe polling, serialized model evidence,
lost-create reconciliation, rollback and token cleanup, with all network
transports mocked.

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
