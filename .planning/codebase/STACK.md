# Codebase Analysis: Technology Stack

**Generated:** 2026-02-11
**Scope:** Full repository technology analysis

## Summary

FSI-AgentGov is a documentation-centric governance framework built with MkDocs Material, using Python for validation/monitoring tooling and PowerShell for Microsoft 365 tenant automation. The repository has 4 GitHub Actions CI/CD workflows, a unified monitoring framework for tracking Microsoft Learn and regulatory changes, and a Conditional Access Automation (CAA) module targeting PowerShell 7+ with Microsoft Graph SDK dependencies.

## Languages & Frameworks

| Language | Usage | File Count |
|----------|-------|------------|
| **Markdown** | Primary deliverable - 71 controls, 284 playbooks, framework docs | ~500+ files |
| **Python 3.9+** (CI targets 3.11) | Validation scripts, monitoring adapters, Dataverse client | ~15 scripts |
| **PowerShell 7.0+** (Core only) | Conditional Access Automation, compliance testing | ~8 scripts/modules |
| **YAML** | MkDocs config, CI/CD workflows, monitoring config | ~6 files |
| **JSON** | Power Automate flows, Adaptive Cards, state files | 3 solution artifacts + state |

## Build Tools

- **MkDocs Material** with light/dark mode, navigation.instant, search.suggest
- **Build:** `mkdocs build --strict` | **Deploy:** `mkdocs gh-deploy --force`
- **Excluded from build:** images/, scripts/, templates/, select reference files

## Dependencies

### Python (scripts/requirements.txt)
- pyyaml >=6.0, msal >=1.30.0, requests >=2.32.0, openpyxl >=3.1.0
- Core validation scripts use only Python stdlib

### PowerShell
- Microsoft.Graph.Identity.SignIns >=2.0.0, Microsoft.Graph.Applications >=2.0.0

## CI/CD (4 GitHub Actions Workflows)
- publish_docs.yml: Build + deploy to GitHub Pages
- learn-monitor.yml: Daily Microsoft Learn change detection
- regulatory-monitor.yml: Weekly Federal Register + FINRA monitoring
- link-check.yml: Markdown link validation + verify_controls.py

## Recommendations

1. Pin mkdocs-material version in CI
2. Consolidate dependency files (beautifulsoup4 not in requirements.txt)
3. Add unit tests for monitoring framework and CAA logic
4. Add pyproject.toml for modern Python tooling
5. PowerShell module manifest exports no functions (placeholders)
6. Node.js markdown-link-check has no package.json
7. Test Python 3.9 in CI if backward compatibility intended
