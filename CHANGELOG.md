# Changelog

All notable changes to the FSI Agent Governance Framework are documented here, organized by major version.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

---

## [1.4.0] — April 2026 (Assessment Tool Unification & Solutions Bridge)

### Added
- **Unified manifest schema**: Single source of truth (`assessment/manifest/controls.json`) for Python scoring engine and assessment SPA with 11 additive fields per control
- **Solutions bridge**: Cross-repository integration with FSI-AgentGov-Solutions v1.4.0 via committed `solutions-lock.json` (35 solutions indexed)
- **10 SPA enhancements**: How-to-verify drawer (E1), zone auto-exclusion (E2), collector evidence import (E3), role filter (E4), sector calibration for 8 institution types (E5), priority starter set of 5 foundation controls (E6), Next Session Agenda export (E7), inline evidence/notes capture (E8), facilitator mode with hints and time budgets (E9), 7 per-role pre-session homework pages (E10)
- **Harvest script**: `scripts/harvest_manifest_extension.py` scaffolds v1.4 fields from existing control docs with TODO placeholders for author-judgment content
- **3 validators**: Manifest schema validator, solutions lock validator, and lock refresh script with tag pinning
- **Portal export envelope (v1.4.1-prep, additive)**: SPA `exportJSON` and `exportRoleSection` now emit a `_metadata` block (framework version, export schema version, manifest commit hint, pillar names, schema type) plus `_computedScores` (pillar/overall percentages and counts) and a derived `assessmentStatus` enum (`draft`/`in-progress`/`final`). Existing top-level state keys are preserved, so v1.3.x consumers continue to work unchanged. Importer silently drops snapshot fields and recomputes on next export. See [CHANGELOG-v1.4.md](CHANGELOG-v1.4.md) and [`assessment/data/README.md`](assessment/data/README.md#portal-export-schema).

### Changed
- **Control count normalization**: Fixed stale "71 controls" / "72 controls" references to "78 controls" across all documentation
- **Version bump**: 1.3.3 → 1.4.0 across README, mkdocs.yml, CITATION.cff, and meta references

### Breaking Changes
- **Assessment SPA export schema**: JSON export format incompatible with v1.3.x—no migration tool provided; recommend completing in-progress v1.3 assessments before upgrading or re-running from scratch with v1.4 collector import

---

| Version | Period | File |
|---------|--------|------|
| **v1.4.x** (current) | April 2026 | [CHANGELOG-v1.4.md](CHANGELOG-v1.4.md) |
| **v1.3.x** | March–April 2026 | [CHANGELOG-v1.3.md](CHANGELOG-v1.3.md) |
| **v1.2.x** | January–March 2026 | [CHANGELOG-v1.2.md](CHANGELOG-v1.2.md) |
| **v1.1.x** | January 2026 | [CHANGELOG-v1.1.md](CHANGELOG-v1.1.md) |
| **v1.0.x and earlier** | October–December 2025 | [CHANGELOG-v1.0.md](CHANGELOG-v1.0.md) |
