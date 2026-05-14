# Changelog Archive

This directory holds **historical, version-frozen changelog files** for releases prior to the current major version. They are no longer in the active rotation but are kept for git-history continuity, audit trail, and inbound-link preservation.

## Convention

The canonical, ever-current changelog lives at the **repo root**:

- [`CHANGELOG.md`](../../CHANGELOG.md) — current major version (v1.5.x onward)

Mirrored on the documentation site at:

- [`/changelog/`](https://judeper.github.io/FSI-AgentGov/changelog/) — same content, included via `mkdocs-include-markdown-plugin`

When a major version is closed out (i.e., the next major begins), its per-version changelog is moved here under the name `CHANGELOG-vX.Y.md`. Inbound links from the root `README.md`, the canonical `CHANGELOG.md`, and any cross-referencing docs are updated in the same change.

## Current contents

| File | Era | Original path |
|------|-----|---------------|
| [`CHANGELOG-v1.4.md`](CHANGELOG-v1.4.md) | April 2026 — assessment unification, solutions bridge, SPA hardening | `CHANGELOG-v1.4.md` (root) |
| [`CHANGELOG-v1.3.md`](CHANGELOG-v1.3.md) | March–April 2026 — six new controls, 24 playbooks, dual-model council review | `CHANGELOG-v1.3.md` (root) |
| [`CHANGELOG-v1.1.md`](CHANGELOG-v1.1.md) | December 2025 — three-layer documentation architecture | `releases/v1.1/CHANGELOG.md` |

Pre-v1.1 history is preserved in git history only — see [commits prior to December 2025](https://github.com/judeper/FSI-AgentGov/commits/main/) for archaeology.

---

*Updated: May-2026 | Version: v1.6.2 | Audience: maintainers, audit reviewers*
