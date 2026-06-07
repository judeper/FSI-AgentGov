---
applyTo: "docs/**/*.md,**/README.md,**/AGENTS.md,assessment/**/*.json,solutions/**/*.md,site-docs/**/*.md"
---

# Commercial-Cloud Scope Rule  (COMMON — identical in all four FSI repos)

> **Scope policy.** FSI-AgentGov, FSI-CopilotGov, FSI-AgentGov-Solutions and
> FSI-CopilotGov-Solutions are scoped to **US commercial-cloud Microsoft 365 only**.
> Government and sovereign clouds — **GCC, GCC High, DoD, Azure Government, GovCloud,
> and other sovereign clouds** — are **out of scope** and must not be documented,
> evaluated, or given operational guidance in forward-facing content.

## Why
Carrying gov-cloud guidance means continuously tracking a *separate* feature-parity
and availability surface (which Microsoft changes independently of commercial cloud).
That is ongoing maintenance the project deliberately does not take on. One scope
statement + this automated gate replaces dozens of per-feature gov-cloud caveats.

## What is prohibited (in forward-facing docs + published assessment data)
Any mention that documents, evaluates, or instructs for government/sovereign clouds:

| Prohibited term | Examples that FAIL |
|---|---|
| `GCC`, `GCC High` | "For GCC tenants, verify default-off…", "GCC High parity gap…" |
| `DoD` | "…in Commercial / GCC High / DoD tenants" |
| `sovereign` (cloud) | "Sovereign-cloud parity confirmed…", "sovereign-cloud compensating control" |
| `government cloud`, `GovCloud`, `Azure Government` | "available in government cloud" |
| gov endpoints (`purview.microsoft.us`, `*.office365.us`, `*.microsoftonline.us`) | "use purview.microsoft.us for GCC High" |

## What is NOT in scope of this rule (intentionally not scanned)
- **Functional code** (`*.ps1`, `*.py`, `*.psm1`, `*.js`) — gov-endpoint handling there is
  functionality, not tracked guidance. (Terminology hygiene is a separate concern.)
- **Inert historical records** — `CHANGELOG*`, `reports/**` (monitoring logs),
  `releases/**`, `tests/**` & fixtures, `templates/**`, `.squad/**`, `research/**`,
  `*.schema.json` (residency enums), `*-lock.json`, `*.backup`, `*.migrated`,
  monitor-state files. These need no maintenance and rewriting them is pure churn.

## The required scope disclaimer (add once per repo, e.g. `docs/SCOPE.md` or in the README)
> **Cloud scope.** This content targets **US commercial-cloud Microsoft 365**.
> Government and sovereign clouds (GCC, GCC High, DoD, and other sovereign clouds)
> are **out of scope**; verify gov-cloud applicability independently with Microsoft.

The disclaimer file (`SCOPE.md` / `disclaimer.md`) and this rule file are the only
places allowed to name the terms — the linter excludes them automatically.

## Legitimate exceptions
If a single mention is genuinely required (rare), add an opt-out marker on the file:

```
<!-- commercial-scope: allow reason: "glossary definition of the GCC acronym" -->
```

## Enforcement
`scripts/verify_commercial_scope.py` runs in CI (`.github/workflows/commercial-scope.yml`)
on every PR and on push to `main`. It fails the build (exit 1) if any forward-facing
file introduces government/sovereign-cloud content. Run it locally before pushing:

```
python scripts/verify_commercial_scope.py
```
