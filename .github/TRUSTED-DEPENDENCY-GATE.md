# Trusted dependency-artifact gate

The `trusted-dependency-artifact` check is the **authoritative** supply-chain
gate for reviewed dependency artifacts. This document states exactly what it
does, what it deliberately does not do, and what a repository administrator must
configure for it to be enforced.

## The problem it exists to solve

`sri-check` and `security-scan` run on the `pull_request` event. Their workflow
files, the verifier scripts they invoke, the hashes they compare against, and
the tests they run are **all supplied by the pull request under review**. A
sufficiently coherent malicious change can update every one of them together and
still go green. Adding more hashes inside a pull-request-controlled workflow does
not fix this; it only makes the self-attestation longer.

`sri-check` remains useful, fast, cross-platform feedback. It is **supplemental**
and must never be described as authoritative.

## The trust boundary

| Element | Source | Candidate can influence it? |
|---|---|---|
| Workflow file | protected default branch | no |
| Expected pins and allowlists | `.github/trusted-policy/dependency-artifact-policy.json` on the default branch | no |
| Verifier code that decides pass/fail | `scripts/trusted/verify-dependency-artifact-gate.mjs` on the default branch | no |
| Candidate tree (tarball, lock, manifest, provenance, verifier source, docs) | pull request head, read through the REST API | yes — it is **data**, never code |

The gate uses `pull_request_target`, which runs the workflow from the default
branch. It **never** checks out, fetches into the workspace, merges, or executes
the pull request head or its merge commit. There is no `npm`, no `npm ci`, no
package script, no lifecycle hook, no `node_modules` directory, and no dependency
cache in either job.

Candidate content reaches the gate only as bytes:

1. `GET /pulls/{n}/files` — the changed-path list, bounded and rejected if truncated.
2. `GET /git/trees/{head_sha}?recursive=1` — the head tree, with file modes.
3. `GET /git/blobs/{blob_sha}` — only the specific blobs the policy names.

Every blob is re-hashed to its own Git object id before it is believed, so the
API cannot hand back different bytes than the tree advertised.

## How a change is classified

| Changed paths | Mode | Result |
|---|---|---|
| none of the guarded paths | `not-applicable` | pass — the check still reports, so a required check is never missing |
| trusted policy paths only | `policy-only` | pass, explicitly stating no artifact was validated; CODEOWNERS review governs it |
| trusted policy paths **and** guarded paths | `mixed-trusted-and-guarded` | **fail closed** — you may not move the pins in the same pull request that supplies the bytes |
| guarded paths, artifact present in base | `artifact` | full validation against base pins |
| guarded paths, artifact not yet in base | `guard-only` | guard invariants only; referencing the artifact spec without shipping its bytes fails |

Whether the artifact is *required* is derived from the **base checkout on disk**,
not from policy text and never from the candidate. That keeps the gate honest in
both directions: it cannot demand bytes that do not exist yet, and a candidate
cannot escape validation by deleting the artifact.

## What full validation asserts

- Pinned raw-byte SHA-256 and size for the tarball, the provenance manifest, and
  the two fast-uri verifier scripts.
- Tarball structure parsed as data: canonical gzip header, header checksums,
  regular files only (no symlink, hardlink, device or directory entries), no path
  escaping `package/`, no absolute or `..` path, non-executable modes, canonical
  ownership and mtime, entry-count / entry-size / unpacked-size bounds, and no
  data after the zero-block terminator.
- `provenance.json` file count, per-file digests against the packed bytes, no
  unsafe paths, no executable entries.
- Packed `package.json`: exact identity and license, no lifecycle scripts, no `bin`.
- Root `package.json`: pinned local spec in `devDependencies`, never in
  `dependencies`, the exact `ajv` → `$fast-uri` override, and no lifecycle or
  hook (`pre*`/`post*`) script.
- `package-lock.json`: exact version, `resolved`, SRI, `dev: true`, exactly one
  copy of the package, Ajv's declared `^3.0.1` edge intact, and no dependency
  declaring a `node`, `npm` or `npx` bin that could shadow the trusted toolchain.
- Tree hygiene: no `.npmrc` anywhere, no `npm-shrinkwrap.json`, no submodule, and
  nothing under `vendor/` outside the reviewed allowlist or with a symlink /
  executable mode.
- `.gitattributes`: required binary marking present, and no `filter=`, `merge=`
  or `diff=` driver aimed at a guarded path.
- The candidate verifier's own `FAST_URI_POLICY` constants and its six advisory
  identifiers must equal the base-controlled values.
- Reviewer-facing documents (`vendor/npm/fast-uri/3.1.7/README.md`,
  `SECURITY.md`) must not instruct anyone to run `npm`, `npx`, `yarn`, `pnpm`,
  `bun` or a `node_modules/.bin` shim before trust is established.

## Why the check run is published explicitly

A `pull_request_target` workflow runs from the default branch, and its
automatically created check run attaches to that branch's commit — not to the
pull request head. Branch rulesets evaluate required status checks on the pull
request **head SHA**, so a `pull_request_target` job's own check can never
satisfy a required status check.

The `publish` job therefore creates the check run itself, against
`github.event.pull_request.head.sha`, with the stable name
`trusted-dependency-artifact`. That is the name a ruleset must require.

`publish` is the only job holding a write scope (`checks: write`). It never reads
candidate content. The verdict travels from `validate` to `publish` base64-encoded
and is re-parsed against a strict schema; a missing, malformed, cancelled or
failed verdict publishes `failure`. There is no path that reports success on
incomplete evidence.

## Force-push and race behaviour

The tree is addressed by the event's head SHA and every blob is verified against
its own Git object id, so a force-push cannot substitute content mid-run. The
gate additionally reads the pull request back at the end and fails closed if the
head moved. Because the published check run is bound to the SHA that was
actually validated, a new head simply has no passing check.

## Required repository configuration — NOT YET APPLIED

Enforcement is a **repository setting**, not a file in this repository. Nothing
in this change set can enable it, and no one should describe the gate as enforced
until the setting has been read back.

`.github/branch-protection.json` already declares the desired state and
`.github/branch-protection.meta.json` records that this context is published
through the Checks API. To apply it, a maintainer with push access to
`judeper/FSI-AgentGov` must run, from the repository root:

```powershell
pwsh -NoProfile -File scripts/apply-branch-protection.ps1 -Branch main
```

then read the live state back and confirm the context is present:

```powershell
gh api repos/judeper/FSI-AgentGov/branches/main/protection --jq '.required_status_checks.contexts'
```

The context must appear exactly as `trusted-dependency-artifact`. Until that
read-back succeeds, the gate reports its verdict but does **not** block a merge.

### CODEOWNERS review is not currently enforced

`.github/branch-protection.json` sets `"required_pull_request_reviews": null`.
CODEOWNERS therefore assigns reviewers but **nothing requires their approval**.
That directly weakens one link in this design: a `policy-only` pull request
passes the gate on the explicit understanding that human review governs it, and
today that review is advisory.

Until a maintainer sets `required_pull_request_reviews` with
`require_code_owner_reviews: true` on `main` and reads the live protection back,
describe the policy path as *reviewed by convention*, not *reviewed by
enforcement*. The artifact path is unaffected — it is enforced by byte pins, not
by review.

Also confirm, in repository settings, that the default `GITHUB_TOKEN` permission
is read-only and that Actions is not configured to grant write scopes by default;
the workflow declares `permissions: {}` at file level, but a permissive default
would still widen other workflows.

## Changing the policy

Changing an expected pin, an allowlist entry, or the gate itself requires a
pull request that touches **only** trusted paths. The gate reports `policy-only`
for such a change and does not validate an artifact, because there is none in
scope; CODEOWNERS review is what governs it. A pull request that mixes a policy
change with a guarded dependency change fails closed by design.

Removing the fast-uri exception therefore has a required order: first a
policy pull request that drops the pins, then the pull request that deletes the
artifact, lock entry, override and gate wiring.

## Known limits

- Actions are referenced by major tag (`actions/checkout@v7`), matching existing
  repository convention. Commit-SHA pinning would be stronger.
- The gate validates structure, identity and policy conformance. It does not
  execute the packaged code; behavioural regression evidence still comes from the
  isolated child harness in `scripts/verify-fast-uri-artifact.mjs`, which the gate
  binds by byte digest rather than by trusting its output.
- A `policy-only` pass is exactly that: an assertion that no artifact was in
  scope. It is not a statement that the new policy is correct. Only human review
  can make that statement — and see the note above: code-owner review is not
  currently required by branch protection.
- The REST reader path runs for the first time only after this workflow reaches
  the default branch, because `pull_request_target` executes the workflow from
  there. Until then it is exercised by offline fixtures only.
