# Technology Stack

**Analysis Date:** 2026-02-02

## Languages

**Primary:**
- Python 3.9+ - Validation scripts, monitoring, documentation processing
- Markdown - Framework, controls, playbooks, reference documentation (primary format)
- YAML - MkDocs configuration, GitHub Actions workflows, metadata

**Secondary:**
- PowerShell - Playbook automation scripts for Power Platform and M365 administration
- KQL (Kusto Query Language) - Microsoft Sentinel analysis queries
- SQL/T-SQL - Dataverse queries (advanced implementations only)
- JSON - Configuration, metadata, API payloads, state files

## Runtime

**Environment:**
- Python 3.11 (GitHub Actions workflows)
- Python 3.9+ (local development)

**Package Manager:**
- pip - Python dependency management
- No lockfile requirement (minimal, standard library-first approach)

## Frameworks

**Core:**
- MkDocs Material - Static documentation site generation and publishing
  - Version: Latest (installed via pip install mkdocs-material)
  - Purpose: Renders Markdown docs to HTML, serves GitHub Pages site

**Validation & Automation:**
- Dataclasses (Python stdlib) - Data modeling for validation scripts
- Pathlib (Python stdlib) - Cross-platform file operations
- Logging (Python stdlib) - Structured logging for monitoring scripts

**CI/CD:**
- GitHub Actions - Workflow automation (daily monitor, link checks, docs publishing)
- GitHub Pages - Static site hosting (https://judeper.github.io/FSI-AgentGov/)

## Key Dependencies

**Critical:**
- requests 2.28+ - HTTP requests for Learn Monitor and external integrations
- beautifulsoup4 4.12+ - HTML parsing for Learn documentation content analysis
- mkdocs-material - MkDocs Material theme for documentation site

**Development/Optional:**
- pyyaml 6.0+ - YAML parsing for mkdocs.yml validation
- markdown 3.4+ - Markdown parsing for content validation
- openpyxl 3.1+ - Excel template management for admin checklists
- pytest 7.0+ - Test framework for script validation
- black 23.0+ - Code formatting for Python scripts
- flake8 6.0+ - Linting for Python scripts

**External Services (via API/SDK, not local dependencies):**
- Microsoft Graph API - Message Center, Defender, reporting data
- Microsoft Sentinel API - SIEM query execution
- Application Insights REST API - RAI telemetry extraction
- Purview Audit API - CopilotInteraction events, XPIA detection
- Exchange Online Management (PowerShell) - Audit log extraction

## Configuration

**Environment:**
- `.github/copilot-instructions.md` - Central Claude Code instructions (v1.2.37)
- `.claude/CLAUDE.md` - Comprehensive project documentation and rules
- `.claude/settings.json` - Team-shared Claude Code settings (hooks, permissions)
- `.claude/settings.local.json` - Local Claude Code overrides (not committed)

**Build:**
- `mkdocs.yml` - Site navigation, theme, markdown extensions, validation rules
- `.github/workflows/mlc-config.json` - Markdown link checker configuration
- `.github/workflows/*.yml` - Three CI/CD workflows (link-check, publish_docs, learn-monitor)

**Documentation Build:**
- `mkdocs build --strict` - Validates all docs before publishing; zero warnings required
- MkDocs 1.6+ validation: nav links, anchors, absolute links

## Platform Requirements

**Development:**
- macOS, Linux, or Windows with Python 3.9+
- Git for version control
- Text editor or IDE (any)
- pip for dependency installation
- Optional: mkdocs-material for local preview (`mkdocs serve`)

**Production:**
- Deployment target: GitHub Pages (static hosting)
- HTTPS only
- Published from main branch after successful CI checks

**CI/CD Environment:**
- Ubuntu latest (GitHub Actions)
- Python 3.11 environment with pip
- Network access to: github.com, learn.microsoft.com, graph.microsoft.com

## External APIs & Services

**Microsoft Learn Monitoring:**
- Monitors 209 Microsoft Learn URLs daily via `learn_monitor.py`
- Uses requests library to fetch page content
- Detects: UI changes, deprecations, dates, feature status
- Generates change reports to `reports/learn-changes/`

**GitHub Actions Integration:**
- Scheduled workflows: Daily (Learn Monitor @ 6 AM UTC), Weekly (Link check @ 2 AM UTC Sunday)
- Workflows store state in `data/learn-monitor-state.json`
- Creates PRs with change reports for human review

**Optional: Local Secret Management:**
- Azure Key Vault (used in FSI-AgentGov-Solutions for webhook secrets)
- Entra ID app registrations (for API authentication)

## Build & Validation Commands

```bash
# Build documentation (must pass with zero errors)
mkdocs build --strict

# Preview locally
mkdocs serve

# Validate control structure
python scripts/verify_controls.py

# Validate Excel templates
python scripts/verify_excel_templates.py

# Check Microsoft Learn URLs for changes
python scripts/learn_monitor.py --dry-run --limit 5

# Run all validation
python scripts/validate_before_push.py
```

## Cross-Repository Integration

This repository (`FSI-AgentGov`) integrates with `FSI-AgentGov-Solutions` for deployable implementations:

**Solution Dependencies (separate repo):**
- Power Automate flows (cloud-native, no dependencies)
- PowerShell scripts (requires ExchangeOnlineManagement, Az modules)
- Python scripts (requires msal, requests, azure-identity)
- Dataverse schemas (Power Platform native)
- Power BI dashboards (Power BI service)

**Technology Stack in FSI-AgentGov-Solutions:**
- Python 3.10+ (automation scripts)
- PowerShell 7+ (deployment and configuration)
- YAML (flow definitions)
- DAX (Power BI measures)
- Dataverse (primary data store)
- Power Automate (workflow automation)
- Power BI (reporting and visualization)

---

*Stack analysis: 2026-02-02*
