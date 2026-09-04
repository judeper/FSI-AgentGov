# Security Policy

This document covers the security posture of the **FSI Agent Governance
Framework** repository (`judeper/FSI-AgentGov`). The framework is a
documentation-first governance reference; it ships scripts, CI workflows, a
documentation site (MkDocs), an assessment engine (Python), and machine-readable
control manifests. It does **not** ship runtime services, hosted endpoints,
secrets, or production tenants.

## Supported Versions

We support the latest minor release on the `main` branch and the immediately
prior minor release. Older releases receive only critical security fixes for
60 days after a new minor is published.

| Version | Status |
|---------|--------|
| `v1.6.x` (current) | Supported |
| `v1.5.x` | Security fixes only |
| `< v1.5` | Unsupported |

The canonical version source is the `framework_version` field referenced by
the [Solutions Contract](docs/reference/solutions-contract.md).

## Reporting a Vulnerability

**Do not** open a public GitHub issue for security reports.

Use GitHub's private vulnerability reporting:

> Repository → **Security** tab → **Report a vulnerability**

Please include:

- A description of the issue and the affected component (script, workflow,
  manifest entry, documentation guidance, generated artifact)
- Steps to reproduce
- Impact assessment from your perspective
- Any suggested mitigation

### Response targets

- Acknowledgement within **2 business days**
- Initial triage within **5 business days**
- Coordinated disclosure once a fix or mitigation is available

## Scope of This Repository

In scope:

- Repository contents: scripts, workflows, manifests, documentation, the
  assessment engine, and the published MkDocs site
- Generated release artifacts: SBOMs, CycloneDX manifests, Sigstore
  attestations
- Guidance documents that, if followed literally, would lead to an insecure
  Microsoft 365 / Power Platform configuration

Out of scope:

- Vulnerabilities in Microsoft 365, Copilot Studio, Power Platform, or any
  third-party Microsoft service — report those to Microsoft via
  [MSRC](https://msrc.microsoft.com/)
- Implementation defects in tenants that have applied this guidance — these
  are the adopting organisation's responsibility
- The companion repository `judeper/FSI-AgentGov-Solutions` — that repository
  has its own security policy

## Threat Model (Summary)

The framework's adversary model assumes:

| Asset | Threat | Mitigation |
|-------|--------|------------|
| This repository's source code | Malicious dependency, supply-chain compromise | Dependabot, dependency review, CodeQL, secret scanning, signed releases |
| Generated SBOMs and release artifacts | Tampering | Sigstore keyless signing, build provenance attestations, GitHub Actions OIDC |
| Assessment manifests (`controls.json`) | Drift between framework and downstream consumers (e.g., Solutions repo) | Pinned release tags per the Solutions Contract; manifest/index/nav drift CI check |
| Assessment engine outputs | False sense of automation coverage | Explicit `evaluator_state` field surfaced in all outputs; `assessment-coverage.md` is generated and CI-checked |
| PowerShell collectors run in customer tenants | Excessive privilege, plaintext credentials | PSScriptAnalyzer ruleset, no plaintext secret parameters, documented least-privilege roles |
| Test fixtures and example IDs | Exposure of real customer data | Allowlist enforced by gitleaks; canonical zero/one tenant IDs only |

The framework is **not** designed to defend against:

- Compromise of the customer's M365 tenant
- Misuse of evidence collected by the assessment engine after it leaves the
  tenant
- Modifications made by a fork or a downstream consumer

## Security Controls Enforced in CI

| Control | Workflow |
|---------|----------|
| Static analysis (Python) | `python-quality.yml` (ruff: F, B, I) |
| Code-quality (Python + JS) | `codeql.yml` (security-and-quality queries) |
| Static analysis (PowerShell) | `powershell-quality.yml` (PSScriptAnalyzer) |
| Secret scanning | `secret-scanning.yml` (gitleaks) |
| Dependency review on PRs | `dependency-review.yml` |
| Dependency updates | `dependabot.yml` |
| Manifest / docs drift | `python-quality.yml` → `check_manifest_doc_drift.py` |
| Assessment coverage transparency | `python-quality.yml` → `generate_coverage_matrix.py --check` |
| FSI language rules | `python-quality.yml` → `verify_language_rules.py` |
| SBOMs + signed release artifacts | `release-artifacts.yml` (CycloneDX + Sigstore) |
| Link health on docs | `link-check.yml` |

### Exceptional fast-uri dependency artifact

Ajv 8.20.0 depends on `fast-uri` `^3.0.1`. The npm registry did not contain the
patched compatible release, 3.1.7, as of September 4, 2026. The published 4.0.0
package is not a safe substitute: it is outside Ajv's declared major-version
range and remains in multiple HIGH advisory ranges. The required 3.1.7 fixes
cover GHSA-jqff-g426-hqxp, GHSA-fph4-wmhf-6fwf, GHSA-f65p-4m7j-42xc,
GHSA-5jgf-p345-68v8, GHSA-qw65-cvwx-89v3, and GHSA-58mr-gqgx-xq4g.

GitHub-generated source archives are not treated as immutable package
artifacts because their compression bytes can be regenerated. As a narrow
supply-chain exception, `package.json` declares the reviewed repo-relative
tarball under `vendor/npm/fast-uri/3.1.7/` as a development-dependency anchor
and binds only Ajv's transitive edge to that exact spec with npm's `$fast-uri`
override reference. The lock and verification gate retain Ajv's declared
dependency edge and reject any production dependency or duplicate package
copy. The tarball was deterministically reconstructed from verified upstream
commit `412e40abd4eb8beabfb952d80abf949a2baf27a3` (tree
`a1ec2b29b5d2493a9ba4d2de480a062b08f72558`); its exact packlist, license,
SHA-256, SHA-512, and regeneration procedure are committed beside it.
`package-lock.json` retains the package identity `fast-uri@3.1.7`, a local
`file:` source, and SHA-512 integrity.

This does not establish a general vendoring channel. Remove the exception once
an official byte-stable npm registry artifact supplies a patched version
compatible with Ajv, after verifying registry integrity/provenance, Ajv
compatibility, all six exploit regressions, and the full repository suite.

## Evidence and Data Handling

The assessment engine writes outputs to `assessment/output/`, which is
git-ignored. Customer tenant data **must not** be committed. Test fixtures
under `assessment/tests/fixtures/` use canonical example tenant IDs only and
are explicitly allowlisted by the secret scanner.

## Best Practice for Adopters

When implementing this framework in your tenant:

- Run all changes through your organisation's change-management process
- Pilot in a non-production environment before broad rollout
- Map controls to your existing audit and evidence workflows
- Keep an issue / risk register for any control you cannot fully implement
- Follow the pinning model in the [Solutions Contract](docs/reference/solutions-contract.md)
  rather than tracking `main`

## Coordinated Disclosure Credit

If you would like public credit for a valid report, indicate this in your
submission. We will publish your name (or pseudonym) in the release notes
of the patched version. We do not currently offer monetary rewards.

---

*FSI Agent Governance Framework — Security Policy*
