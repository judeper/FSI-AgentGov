# Versioning and Support

This page is the canonical statement of how the FSI Agent Governance
Framework is versioned, what we consider a breaking change, and how long a
given release is supported. It complements the [Solutions Contract](solutions-contract.md),
which describes how downstream repositories should pin to framework releases.

## Source of Truth

The framework version is the value of `framework_version` referenced by the
[Solutions Contract](solutions-contract.md) and the latest entry in
[`CHANGELOG.md`](https://github.com/judeper/FSI-AgentGov/blob/main/CHANGELOG.md).
The MkDocs site footer reflects the same value.

## Versioning Scheme

We follow [Semantic Versioning 2.0.0](https://semver.org/) adapted to a
governance-content project:

| Component | Bumped when… |
|-----------|--------------|
| **Major** (`X`.0.0) | A control ID is removed, an existing `pass_condition` string is renamed, the manifest schema removes a field, a zone definition changes, or a regulatory mapping is removed |
| **Minor** (`X.Y`.0) | A new control is added, a new `pass_condition` is added, a new evaluator is wired, a manifest field is added, or a new playbook section is introduced |
| **Patch** (`X.Y.Z`) | Documentation fixes, evidence-link refreshes, typos, bug fixes that do not change the public schema, dependency updates |

The 78-control baseline is itself a major-version commitment. Adding the 79th
control would be a minor change, but renumbering existing controls would be
a major change.

## Stability Commitments by Version

For any release `vX.Y.Z`, the following hold within the same **major**
version:

1. The set of control IDs present at the time of `vX.0.0` will continue to
   exist (additions allowed; removals require a major bump).
2. The pillar assignment of every control is stable.
3. The shape of `controls.json` is additive — fields may be added but not
   removed or repurposed.
4. The zone tier model (Personal / Team / Enterprise) is stable.

Within the same **minor** version:

1. `pass_condition` strings used by registered evaluators are stable.
2. `evaluator_state` rollups are stable for any control whose underlying
   manifest entry has not changed.
3. Output schemas of `assessment-prefilled.md`,
   `manual-questionnaire.md`, and `assessment-summary.json` are stable.

Patch releases never change any of the above.

## Support Window

| Version | Status |
|---------|--------|
| Latest minor on `main` | Fully supported |
| Previous minor | Security fixes only |
| Older versions | Unsupported after **60 days** from a new minor release |

Security fixes follow the process in [`SECURITY.md`](https://github.com/judeper/FSI-AgentGov/blob/main/SECURITY.md).

## Release Artifacts

Each tagged release publishes:

- A GitHub Release with auto-generated notes
- A CycloneDX SBOM for the Python dependency tree
- A CycloneDX SBOM for the npm dependency tree
- Sigstore (cosign keyless) build-provenance attestations
- Sigstore SBOM attestations

All artifacts are produced by `.github/workflows/release-artifacts.yml`
using GitHub Actions OIDC; there are no long-lived signing keys.

## Deprecation Process

If a public-surface element will be removed in the next major:

1. The element is annotated `Deprecated` in its source location and in the
   relevant docs page during a minor release.
2. The deprecation is summarised in `CHANGELOG.md` under
   **Deprecations** for that minor.
3. The element remains functional for the entire remaining major version.
4. Removal happens only at the next major release, with a migration note in
   `CHANGELOG.md`.

## How Downstream Consumers Should Pin

See the [Solutions Contract](solutions-contract.md) for the recommended
pinning patterns. In short: pin to a release tag (e.g., `v1.6.2`), not
`main`, and bump the pin deliberately as part of your own release process.

## Pre-Release Versions

Release candidates use the `vX.Y.Z-rcN` suffix. RCs are signed and produce
SBOMs but are not considered supported releases. The Solutions repo should
not pin to an RC tag in production guidance.
