# Versioned Releases

This directory contains versioned PDF releases of the FSI Agent Governance Framework for examiner handoff and offline use.

## Release Structure

```
releases/
├── README.md           # This file
└── v1.1/
    ├── CHANGELOG.md    # Release-specific changelog
    └── [PDFs]          # Generated PDFs (when available)
```

## Available Releases

| Version | Date | Status |
|---------|------|--------|
| v1.1 | January 2026 | Current |
| v1.0 | January 2026 | Superseded |

## PDF Generation

PDFs are generated from the MkDocs documentation using GitHub Actions on tagged releases.

**Planned PDFs:**
- `FSI-AgentGov-v{version}-FrameworkBook.pdf` — Framework layer only
- `FSI-AgentGov-v{version}-ControlCatalog.pdf` — All 61 controls
- `FSI-AgentGov-v{version}-QuickReference.pdf` — Reference materials

## For Examiners

If you received a PDF version of this framework, note:

1. **Check for updates:** Visit the [GitHub repository](https://github.com/judeper/FSI-AgentGov) for the latest version
2. **Live documentation:** The [GitHub Pages site](https://judeper.github.io/FSI-AgentGov/) always has current content
3. **Portal paths may change:** Microsoft updates admin portals frequently; online documentation is updated to reflect changes

## Creating a Release

1. Update version in `mkdocs.yml` and `docs/index.md`
2. Update `CHANGELOG.md` with release notes
3. Tag the release: `git tag v1.1`
4. Push the tag: `git push origin v1.1`
5. GitHub Actions will generate PDFs and create a release

---

*FSI Agent Governance Framework v1.2 - January 2026*
