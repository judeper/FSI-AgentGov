# Pre-trust review and policy rotation runbook

This runbook is a **trusted policy path**. A dependency-artifact pull request
must never modify it, `SECURITY.md`, the gate workflow, the app contract, the
ruleset plan, or any other trusted path in the same pull request.

## Boundary

The vendored artifact README is an exact byte-pinned copy of
`vendor-readme-template.md`; it contains no executable procedure. Do not infer
permission to run a command from a candidate artifact, its README, a test, a
workflow, or a check with a familiar name.

The `trusted-dependency-artifact-preflight` Actions workflow is useful
base-controlled evidence, but it is **not an enforced or non-spoofable
signal**. Only the dedicated GitHub App source bound by the remote ruleset may
satisfy the authoritative `trusted-dependency-artifact` requirement.

## Policy rotation

1. Open a **policy-only** pull request. It may alter trusted policy in place,
   but must not add, delete, rename, or modify a guarded artifact path.
2. Obtain an independent exact-head review. Required CODEOWNERS review is part
   of the planned remote ruleset; before that ruleset is active, this review is
   a manual bootstrap control.
3. Merge the policy-only pull request first. If the ruleset's workflow/App
   binding must change, apply and read it back before any artifact pull request.
4. Open or rebase the artifact pull request only after the policy commit and
   remote read-back are complete.

The gate rejects all protected-path renames. A rotation changes policy in place;
it does not move a trusted or guarded path.

## One-time enforcement bootstrap

The policy pull request cannot protect itself because its workflow and policy
do not yet exist on the default branch. Perform these steps in order:

1. Independently review the exact policy-only commit and merge it under the
   controls that existed before this bootstrap.
2. As the repository owner, provision and install the dedicated GitHub App
   described in `trusted-dependency-artifact-app-contract.json`. Keep its
   private key and webhook secret outside this repository.
3. From the merged default-branch checkout, generate a read-only plan:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 -Plan -AppId <GitHub-App-ID>
   ```

4. Copy the reported `liveDigest`, `intendedRulesetDigest`, and
   `confirmationToken`; then apply exactly that reviewed plan:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 -Apply -AppId <GitHub-App-ID> -ExpectedLiveDigest <liveDigest> -ExpectedIntendedRulesetDigest <intendedRulesetDigest> -ConfirmationToken <confirmationToken>
   ```

5. Read back the remote configuration and a new no-op pull request's check
   source. It must show the same App ID for both the ruleset
   `integration_id` and the successful check run:

   ```powershell
   pwsh -NoProfile -File scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1 -ReadBack -AppId <GitHub-App-ID> -ProbePullRequest <new-no-op-PR-number>
   ```

Until every read-back passes, the artifact remediation is **BLOCKED**. A
same-name status or check run, including one created by GitHub Actions, is not
an acceptable substitute.

## Merge queue

This plan does not enable merge queue. If an owner enables it later, the
dedicated App must process `merge_group` events and publish the expected-source
check on the merge-group test SHA. A check run attached only to the pull request
head does not satisfy that test-merge evaluation.

## Registry and advisory evidence

This policy does not use package-registry availability or advisory-search
results as an enforcement predicate. Record direct registry/API responses with
their date and TLS/mirror conditions in the review evidence; a failed mirror,
search result, or unavailable TLS path does not prove publication or absence of
any package version.
