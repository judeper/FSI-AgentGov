# Pre-trust review and policy rotation runbook

This runbook is a **trusted policy path**. A dependency-artifact pull request
must never modify it, `SECURITY.md`, the gate workflow, the App contract, the
ruleset plan, or another trusted path in the same pull request unless it is the
separately approved exact activation transaction.

## Boundary

The vendored README is an exact byte-pinned artifact file. It is data only:
never infer permission to run a command from a candidate artifact, README, test,
workflow, or familiar check name. The command-free template remains protected
policy material for future documentation rotations.

The `trusted-dependency-artifact-preflight` Actions workflow is useful
base-controlled evidence, but it is **not an enforced or non-spoofable signal**.
Only the dedicated GitHub App source bound by the remote ruleset may satisfy the
authoritative `trusted-dependency-artifact` requirement.

## Policy rotation

1. Open a **trusted policy-only** pull request. It may alter policy in place,
   but must not add, delete, rename, or modify guarded artifact paths.
2. Obtain an independent exact-head review. CODEOWNERS review is part of the
   planned remote ruleset; before activation, this is a manual bootstrap control.
3. Merge the policy-only pull request first. The old artifact remains governed
   by the old base policy during review; the new policy then blocks old bytes.
4. Open or rebase the separate exact-match artifact rotation only after the
   policy commit is merged. Never combine a policy pin change and artifact
   bytes in one pull request.

Protected-path renames, case/NFC aliases, duplicates, and directory/file prefix
collisions are rejected. A rotation changes policy in place and does not move a
trusted or guarded path.

## Exact approved activation

When the artifact is absent from the immutable base tree, the only accepted
activation is the complete file set and exact bytes recorded in
`dependency-artifact-policy.json` for approved commit
`8acd5d7907d9ef01e2875855fdd83b307a1e2edd`. That set includes package metadata,
`.gitattributes`, the artifact/provenance/README, verifier/runtime files,
security workflows, `SECURITY.md`, and the focused tests. Any extra file,
dependency, lock node, script, URL, registry, workflow, test, or documentation
byte fails closed. The policy branch itself contains none of those package,
lockfile, or artifact bytes.

## One-time enforcement bootstrap

The policy pull request cannot protect itself because its workflow and policy do
not yet exist on the default branch. Perform these steps in order:

1. Independently review and merge the exact policy-only commit under the
   controls that existed before this bootstrap.
2. As the repository owner, provision a private/dedicated GitHub App according
   to `trusted-dependency-artifact-app-contract.json`. Install it only on
   `judeper/FSI-AgentGov` with selected-repository scope.
3. Keep the App private key and webhook secret outside Git. At runtime provide
   either `GITHUB_APP_PRIVATE_KEY_PATH` or `GITHUB_APP_PRIVATE_KEY`; never put
   either value in command output, logs, a file in the repository, or a
   candidate-controlled environment.
4. Verify the App's exact identity, installation, permissions, and webhook
   events with the App JWT. The owner credential and App credential are
   separate: owner `GH_TOKEN`/`gh auth` performs ruleset operations; the App
   JWT proves the publisher identity. An owner-token probe of the documented
   App-installation endpoint returned HTTP 401 on September 5, 2026, so there
   is no user-token fallback in this operator.
5. Create two disposable or nominated no-op probes:
   - **positive probe:** the dedicated App publishes a successful
     `trusted-dependency-artifact` check on the exact PR head and the PR is
     `mergeable=true`, `mergeable_state=clean`;
   - **negative probe:** a different PR has only a successful same-name
     `github-actions` check on its exact head and is
     `mergeable=false`, `mergeable_state=blocked`.
6. From the merged default-branch checkout, run the read-only plan with the
   App private key supplied only at runtime:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 `
     -Plan -AppId <GitHub-App-ID>
   ```

7. Copy the reported `liveDigest`, `intendedRulesetDigest`, and
   `confirmationToken`; apply exactly that reviewed plan and pass **both**
   probe PR numbers:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 `
     -Apply -AppId <GitHub-App-ID> `
     -ProbePullRequest <positive-PR-number> `
     -SpoofProbePullRequest <negative-PR-number> `
     -ExpectedLiveDigest <liveDigest> `
     -ExpectedIntendedRulesetDigest <intendedRulesetDigest> `
     -ConfirmationToken <confirmationToken>
   ```

8. Read back the remote configuration with the same two probes:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 `
     -ReadBack -AppId <GitHub-App-ID> `
     -ProbePullRequest <positive-PR-number> `
     -SpoofProbePullRequest <negative-PR-number>
   ```

Apply refuses to run without both probes. Until every App, ruleset, legacy
protection, and probe read-back passes, the artifact remediation is **BLOCKED**.
A same-name check from GitHub Actions is never an acceptable substitute.

## Webhook handling

The App service must validate the webhook HMAC signature with the runtime-only
secret, reject missing/invalid timestamps outside the replay window, de-duplicate
delivery IDs, verify the event repository and installation ID, and capture the
event head SHA/base SHA/base ref before any GitHub read. It must re-read the PR
before and after evaluation, use immutable base policy/tree data, and never
checkout, install, import, execute, or interpolate candidate content.

Rotate the private key and webhook secret independently, revoke old material
after overlap is complete, and scope installation access only to the target
repository. If merge queue is enabled later, add `merge_queues:read` and
`merge_group`; publish and verify the same App check on
`merge_group.head_sha`. A passing PR-head check is not a passing merge-group
check.

## Automatic rollback

Apply is create-only and never updates, replaces, or deletes a pre-existing
managed ruleset. If post-create verification fails, it automatically reads the
returned ruleset and history, confirms the new ID/name, intended security
fields, creation time, and owner actor, then deletes only that newly created ID.
If the POST response is lost, it first reconciles the live ruleset list against
the pre-create IDs and rolls back only one unambiguous new matching ruleset.
If that proof is unavailable, rollback is refused and owner attention is
required; the script does not report success. The owner must verify the final
ruleset list after either outcome.
