# Pre-trust review and policy rotation runbook

This runbook is a **trusted policy path**. A dependency-change pull request
must never modify it, `SECURITY.md`, the gate workflow, the App contract, the
ruleset plan, or another trusted path. Trusted paths are never part of the
dependency activation transaction.

## Boundary

Policy version 3 selects `exact-pins` for the planned registry activation.
Candidate lockfile and test bytes are data only: never infer permission to run
a command from a candidate package, README, test, workflow, or familiar check
name. The older `vendored-artifact` validation mode and command-free vendor
README template remain protected policy capabilities, but they are not the
active transaction.

The trusted `security-scan.activation.yml` file remains the canonical workflow
target for a future policy-reviewed use of the legacy vendored mode. It is
inert policy material, not an active workflow, and the current four-file
Playwright registry/container activation does not consume it.

The `trusted-dependency-artifact-preflight` Actions workflow is useful
base-controlled evidence, but it is **not an enforced or non-spoofable signal**.
Only the dedicated GitHub App source bound by the remote ruleset may satisfy the
authoritative `trusted-dependency-artifact` requirement.

## Policy rotation

1. Open a **trusted policy-only** pull request. It may alter policy in place,
   but must not add, delete, rename, or modify guarded dependency paths.
2. Obtain an independent exact-head review. CODEOWNERS review is part of the
   planned remote ruleset; before activation, this is a manual bootstrap control.
3. Merge the policy-only pull request first. The old dependency state remains
   governed by the old base policy during review; the new policy then pins the
   approved transition.
4. Open or rebase the separate exact-match dependency rotation only after the
   policy commit is merged. Never combine a policy pin change and dependency
   bytes in one pull request.

Protected-path renames, case/NFC aliases, duplicates, and directory/file prefix
collisions are rejected. A rotation changes policy in place and does not move a
trusted or guarded path.

Each trusted path must remain present with its explicitly approved regular
blob mode in both trees, including on unrelated PRs. Symlinks, submodules, and
directory replacements are never relocation mechanisms. To relocate trusted
code, first retain the existing regular file and materialize a reviewed regular
destination with a `trustedPaths`/`trustedPathModes` declaration in a separate
policy-only PR. Merge that protection before changing imports/loaders. Retiring
the old path requires another reviewed policy change only after it is no longer
loaded; do not delete it while it is still a trusted path.

## Exact approved activation

The only accepted activation is policy version 3's `exact-pins`,
base-relative tree delta, identified by patch digest
`6dec5764f4b2a07e939cb64e946e8680ac1c342b1f2f9beec598b57d8ef5b051`.
It contains exactly:

1. `package.json`: base mode/blob
   `100644`/`e267a3b54bfbc2a7b7f3e37a3fc15a1b6ea1ba9d`; target
   mode/blob/SHA-256/size
   `100644`/`a3ac17df1593fdcd2b7ef32df05c59d22c91e7e2`/
   `bf97e1c0d8b078c28d3d47ccb3cfdb6a3ff98c744b46f61e7d1f9e4d60a91739`/
   `863`.
2. `package-lock.json`: base mode/blob
   `100644`/`11b6591aa1b39b50d451005dae574fb465f66871`; target
   mode/blob/SHA-256/size
   `100644`/`a8e028cab203c4a160a654e672730f269b588b90`/
   `efa4589bb962f3b7947de12a82dd6763b7ec1ba451ac580a5eccfbb8464f7f75`/
   `76375`.
3. `.github/workflows/e2e.yml`: base mode/blob
   `100644`/`1636e666417025c45b949c61319d1cae7a6a14b8`; target
   mode/blob/SHA-256/size
   `100644`/`10877192c6614a3b24bc8516b9ba7822ba5f65c1`/
   `1812e1dccc4f9246dec3234988c0675415a8053ff46aa91d152c09e80108924a`/
   `7311`.
4. `.github/workflows/update-snapshots.yml`: base mode/blob
   `100644`/`7e309fdd56a24ca42c26e8810bb04b3ad1d64022`; target
   mode/blob/SHA-256/size
   `100644`/`282b78f3ced956c178f10c66d7bbebffe98bb8e0`/
   `5fad958d477290547257ba1bbc7e48669168088e6564a10e790c597114a990a4`/
   `2357`.

No vendored artifact, provenance file, `.gitattributes`, verifier/runtime
file, `SECURITY.md`, or optional Playwright spec migration belongs in this
transaction. Those former activation-sensitive surfaces remain guarded,
including both security workflows, all verifier/runtime paths, package
manifests and lockfiles, the Playwright container workflows, the vendor root,
the former focused tests, and the new fast-uri security test.

The evaluator derives each immutable tree's state from **all** base or target
pins. A mixed or poisoned base fails every pull request. Only the exact
pre-state to exact post-state four-file delta may activate. Partial or extra
changes, reversion, rename/alias tricks, mode changes, and altered bytes fail.
In the post-state, all four target files are revalidated by mode, Git blob,
raw-byte SHA-256, and size on every pull request.

`exact-pins` mode never performs tar, provenance, packed-manifest, or artifact
checks and never fetches, installs, imports, or executes candidate package
code. The legacy `vendored-artifact` mode remains covered by synthetic
regressions for future reviewed policies.

After this policy is merged, recreate or rebase the dependent branch from that
merged policy head and materialize only the four target blobs. If any base pin
differs, stop and rotate policy; do not alter the dependent branch to make the
pins fit. The policy branch itself must not contain any activation change.

On a local checkout with both target Git objects available, run the full
pre/post replay without installing or executing candidate package code:

```powershell
$env:TRUSTED_GATE_VALIDATE_PLANNED_BLOBS = "1"
npm test
Remove-Item Env:TRUSTED_GATE_VALIDATE_PLANNED_BLOBS
```

A fresh policy-only clone may not contain the future target objects; its normal
suite still checks current policy shape, the exact base state, guarded-path
coverage, and synthetic exact-pins and vendored-artifact attacks. The later
activation checkout contains the target objects and runs the replay without an
environment flag.

## One-time enforcement bootstrap

The policy pull request cannot protect itself because its workflow and policy do
not yet exist on the default branch. Perform these steps in order:

1. Independently review and merge the exact policy-only commit under the
   controls that existed before this bootstrap.
2. Independently review and deploy the signed-webhook evaluator outside this
   repository. It must implement the immutable evaluator contract and never
   execute candidate content.
3. As the repository owner, provision a private/dedicated GitHub App according
   to `trusted-dependency-artifact-app-contract.json`. Install it only on
   `judeper/FSI-AgentGov` with selected-repository scope.
4. Keep the App private key and webhook secret outside Git. At runtime provide
   either `GITHUB_APP_PRIVATE_KEY_PATH` or `GITHUB_APP_PRIVATE_KEY`; never put
   either value in command output, logs, a file in the repository, or a
   candidate-controlled environment.
5. The operator pins `https://api.github.com` and `github.com`, rejects
   conflicting ambient origins, lists all App installations with the JWT,
   creates a temporary installation token, paginates
   `GET /installation/repositories`, requires exactly
   `judeper/FSI-AgentGov`, verifies exact permissions/events, and revokes the
   token even on validation failure. Counts must agree on every page, duplicate
   IDs are rejected, expiry must be within one hour, and REST redirects are
   disabled. The owner credential is used only for repository/ruleset reads and
   writes.
6. Prepare two same-repository probe PRs against `main`, but do not rely on
   existing check runs:
   - **positive probe:** a no-op/unrelated change expected to produce a
     successful App check in `not-applicable` mode;
   - **negative probe:** a partial activation-path change expected to produce a
     failed App check in `activation-rejected` mode, plus a successful
     same-name GitHub Actions check; it should remain conflict-free while
     reporting `mergeable_state=blocked`.
7. From the merged default-branch checkout, run the read-only plan with the
   owner credential. Plan mode does not use an App private key or create an
   installation token:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 `
     -Plan -AppId <GitHub-App-ID> `
     -EvaluatorOrigin https://<independently-reviewed-evaluator-host>
   ```

8. Copy the reported `liveDigest`, `intendedRulesetDigest`, and
   `confirmationToken`; apply exactly that reviewed plan and pass **both**
   probe PR numbers. Supply the App private key only at runtime. Apply creates
   the ruleset first and then polls for fresh probe evidence. It prints two
   fresh, non-secret 256-bit challenge nonces. Send them only through the
   evaluator's authenticated operator control plane, then synchronize both
   probe heads or invoke the independently controlled replay mechanism:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 `
     -Apply -AppId <GitHub-App-ID> `
     -EvaluatorOrigin https://<independently-reviewed-evaluator-host> `
     -ProbePullRequest <positive-PR-number> `
     -SpoofProbePullRequest <negative-PR-number> `
     -ExpectedLiveDigest <liveDigest> `
     -ExpectedIntendedRulesetDigest <intendedRulesetDigest> `
     -ConfirmationToken <confirmationToken>
   ```

9. Read back the remote configuration with the App private key supplied only
   at runtime and newly retriggered probes:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 `
     -ReadBack -AppId <GitHub-App-ID> `
     -EvaluatorOrigin https://<independently-reviewed-evaluator-host> `
     -ProbePullRequest <positive-PR-number> `
     -SpoofProbePullRequest <negative-PR-number>
   ```

Apply refuses to run without both probes. The positive and negative App checks,
and the negative same-name Actions check, must start after ruleset creation,
remain within the five-minute evidence window, and be associated with the exact
probe PR/head/base. Until every App, ruleset, legacy-protection, and probe
read-back passes, the dependency remediation is **BLOCKED**. A same-name check
from GitHub Actions is never an acceptable substitute.

The complete `filter=all` check-run pagination must have stable totals and
unique run IDs. Compact GitHub check associations are not complete repository
identities: a separate full PR read-back must supply `full_name`, and its
PR/repository IDs, canonical API URLs, names, refs, and SHAs must match the
association exactly. The final PR read-back supplies mergeability. Missing,
stale, or conflicting association data fails closed. Never bypass this by
dropping the `full_name` requirement or selecting an older passing check.

## Webhook handling

The App service must validate the webhook HMAC signature with the runtime-only
secret **before** processing, de-duplicate delivery IDs, verify the event
repository and installation ID, and capture the event head SHA/base SHA/base
ref plus a trusted receiver timestamp before any GitHub read. GitHub supplies
no signed timestamp header, so the receiver timestamp and delivery-id
deduplication establish the replay window. It must re-read the PR before and
after evaluation, use immutable base policy/tree data, and never checkout,
install, import, execute, or interpolate candidate content.

For each probe, the evaluator receives the operator-generated challenge only
through its authenticated control plane after the ruleset exists, validates the
signed webhook, and writes canonical base64url JSON to check-run `external_id`
with exactly: `nonce`, `repository`, `pull_request`, `head_sha`, `base_sha`,
`policy_digest` (SHA-256 of canonical policy JSON), `policy_version`, `mode`,
and `issued_at`. Canonical JSON recursively sorts object keys, preserves array
order, emits no insignificant whitespace, and is UTF-8 before hashing or
base64url encoding. The check's `details_url` must use the exact external HTTPS
origin supplied to the operator; GitHub and loopback origins are rejected. The
operator requires the check's GitHub PR association to match those fields, requires
start/completion after ruleset creation, rejects evidence older than 300
seconds, and rejects nonce reuse across probes.

Rotate the private key and webhook secret independently, revoke old material
after overlap is complete, and scope installation access only to the target
repository. If merge queue is enabled later, add `merge_queues:read` and
`merge_group`; publish and verify the same App check on
`merge_group.head_sha`. A passing PR-head check is not a passing merge-group
check. The current operator fails closed if any active merge queue is present.

## Automatic rollback

Apply is create-only and never updates, replaces, or deletes a pre-existing
managed ruleset. If post-create verification fails, it automatically reads the
returned ruleset and history, confirms the new ID/name, intended security
fields, creation time, and owner actor, then deletes only that newly created ID.
If the POST response is lost, it first reconciles the live ruleset list against
the pre-create IDs and rolls back only one unambiguous new matching ruleset.
If that proof is unavailable, rollback is refused and owner attention is
required; the script does not report success. The owner must verify the final
ruleset list after either outcome. The operator also compares the complete
post-rollback security snapshot to its pre-create snapshot; unrelated drift
is not silently accepted or repaired.
