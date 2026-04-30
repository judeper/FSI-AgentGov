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
| `v1.4.x` (current) | Supported |
| `v1.3.x` | Security fixes only |
| `< v1.3` | Unsupported |

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
