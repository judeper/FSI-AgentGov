# External Integrations

**Analysis Date:** 2026-02-02

## APIs & External Services

**Microsoft Learn Documentation:**
- Service: Microsoft Learn content platform
- What it's used for: Monitoring documentation changes for FSI-AgentGov controls (209 URLs tracked)
- SDK/Client: requests library + BeautifulSoup4 for parsing
- Authentication: Public (no auth required for content fetch)
- Script: `scripts/learn_monitor.py` runs daily via GitHub Actions
- Change Detection: Hashes content, detects UI steps, dates, deprecations, status changes
- Output: `reports/learn-changes/learn-changes-YYYY-MM-DD.md` with AI-assisted review support

**Microsoft Graph API:**
- Service: Microsoft 365 API endpoints
- What it's used for: Message Center polling, admin activity, reporting data
- Client: requests library (HTTP client)
- Authentication: Entra ID app registration (OAuth2 Client Credentials)
- Used by: FSI-AgentGov-Solutions (message-center-monitor, compliance-dashboard)
- Endpoints: `/admin/serviceAnnouncement/messages`, admin activity, Power Platform APIs

**GitHub API:**
- Service: GitHub.com
- What it's used for: PR automation, workflow dispatch, repository management
- Client: GitHub CLI (gh), GitHub Actions APIs
- Authentication: GitHub token (GITHUB_TOKEN)
- Used by: `.github/workflows/` for PR creation, labeling, status reporting
- Scripts: `learn_monitor.py` creates/updates PRs with change reports

**GitHub Pages:**
- Service: Static site hosting (https://judeper.github.io/FSI-AgentGov/)
- What it's used for: Publishing rendered documentation site
- Deployment: Automated via `publish_docs.yml` on main branch push
- Build: mkdocs gh-deploy converts Markdown to HTML

## Data Storage

**Databases:**
- None in primary repository (documentation-only project)
- State tracking: `data/learn-monitor-state.json` - JSON file with content hashes for Learn URLs
  - Location: Repository root under `data/` directory
  - Purpose: Baseline for change detection between runs
  - Updated: Daily by learn-monitor workflow

**File Storage:**
- Local filesystem only - all artifacts stored in repository
- Reports: `reports/learn-changes/` - Generated change detection reports (Markdown)
- Scripts: `scripts/` - Python validation and monitoring scripts
- Documentation: `docs/` - Markdown documentation (284 playbooks + 71 controls + 10 framework docs)
- Downloads: `docs/downloads/` - Excel templates for administrators

**Remote Storage (via FSI-AgentGov-Solutions):**
- Dataverse (Power Platform) - Primary data store for operational solutions
- Azure Storage Blob - Optional for DEC solution compliance storage
- Application Insights - RAI telemetry and agent tracing data

**Caching:**
- GitHub Actions cache: `.cache/` - MkDocs Material theme cache (weekly rotation)
- No persistent caching layer

## Authentication & Identity

**Auth Provider:**
- GitHub (for Actions workflows)
- Entra ID (for Microsoft API access in downstream solutions)

**Implementation:**
- `GITHUB_TOKEN` - GitHub Actions default token for PR creation and workflow dispatch
- App registrations - Created per solution for Microsoft Graph access
  - Message Center Monitor: ServiceMessage.Read.All permission
  - Compliance Dashboard: Organization.Read.All permission
  - DEC Solution: ServicePrincipal Graph permissions for audit access

**Secrets Location:**
- GitHub Secrets: Configured in repository settings
- Azure Key Vault: Referenced in FSI-AgentGov-Solutions (not in primary repo)
- Environment variables: Used in GitHub Actions workflows

## Monitoring & Observability

**Error Tracking:**
- None (documentation-only project)
- FSI-AgentGov-Solutions use Application Insights for agent telemetry

**Logs:**
- GitHub Actions logs: Visible in Actions tab
- Learn Monitor output: Captured to stdout, available in workflow logs
- State file: `data/learn-monitor-state.json` contains execution metadata (timestamps, URLs checked)

**Alerts:**
- GitHub workflow notifications: Email on PR creation when changes detected
- Learn Monitor PR labels: `needs-review` label added when changes detected
- Manual review: Maintainer reviews change reports before merging

## CI/CD & Deployment

**Hosting:**
- GitHub Pages (static hosting, published from gh-pages branch)
- Uses mkdocs gh-deploy for automated deployment

**CI Pipeline:**
- **publish_docs.yml** (on push to main)
  - Validates docs: `mkdocs build --strict`
  - Blocks forbidden artifacts (PDFs, JSONs, internal docs)
  - Deploys to GitHub Pages

- **link-check.yml** (weekly + PR trigger + push)
  - Validates markdown links (internal and external)
  - Runs control consistency checks
  - Uses gaurav-nelson/github-action-markdown-link-check

- **learn-monitor.yml** (daily @ 6 AM UTC + manual trigger)
  - Monitors 209 Microsoft Learn URLs
  - Detects content changes and deprecations
  - Creates PRs with detailed change reports
  - Enables AI-assisted review workflow

**Build Process:**
1. Git push to main
2. GitHub Actions triggers publish_docs.yml
3. Python 3.11 environment loads mkdocs-material
4. `mkdocs build --strict` validates all markdown
5. `mkdocs gh-deploy --force` publishes to GitHub Pages
6. Site live at https://judeper.github.io/FSI-AgentGov/

## Environment Configuration

**Required env vars (GitHub Actions):**
- `GITHUB_TOKEN` - Provided by GitHub Actions, used for PR creation
- `LEARN_MONITOR_DEBUG` - Optional (set to 1 for debug output)

**Optional env vars (local development):**
- `LEARN_MONITOR_DEBUG=1` - Enable verbose logging for monitoring script
- None required for local mkdocs serve

**Secrets location:**
- GitHub Settings → Secrets and variables → Actions
- No hardcoded credentials in repository
- FSI-AgentGov-Solutions uses Azure Key Vault for production secrets

## Webhooks & Callbacks

**Incoming:**
- GitHub webhook (automated): Pushes to main trigger publish_docs.yml
- GitHub webhook (automated): PRs trigger link-check.yml
- Scheduled triggers (cron): Daily learn-monitor, weekly link-check

**Outgoing:**
- Learn Monitor creates PRs: peter-evans/create-pull-request action
- Learn Monitor adds PR comments: peter-evans/create-or-update-comment action
- AI-assisted review: Manual invocation of `/review-learn-changes` skill in Claude Code

## Integration Points with FSI-AgentGov-Solutions

This repository provides framework and playbooks that solutions implement:

**Message Center Monitor:**
- Consumes: Control 2.3 (Change Management) and Control 3.2 (Usage Analytics)
- APIs used: Microsoft Graph `/admin/serviceAnnouncement/messages`
- Data sink: Dataverse MessageCenterLog table

**Deny Event Correlation Report:**
- Consumes: Control 1.8 (Runtime Protection), Control 1.7 (Audit Logging)
- APIs used: Purview Audit API, Application Insights REST API
- Data sources: CopilotInteraction events, DLP events, RAI telemetry

**Compliance Dashboard:**
- Consumes: All 71 controls (compliance evidence aggregation)
- Data sink: Dataverse ComplianceMetric table
- Visualization: Power BI connected to Dataverse

**Environment Lifecycle Management:**
- Consumes: Control 2.1 (Managed Environments), Control 2.2 (Environment Groups)
- APIs used: Power Platform admin APIs, Dataverse APIs
- Automation: Power Automate flows + Python provisioning scripts

**Conditional Access Automation:**
- Consumes: Control 1.11 (Conditional Access), Control 1.23 (Step-Up Authentication)
- APIs used: Microsoft Graph `/policies/conditionalAccessPolicies`
- Deployment: Azure CLI, PowerShell

**Platform Change Governance:**
- Consumes: Control 2.3 (Change Management)
- Primary data source: Microsoft Message Center (via Graph API)
- Integration: learn_monitor.py framework guidance applies

## Data Flow

```
FSI-AgentGov (Documentation)
    ↓
Scripts validate controls and references
    ↓
learn_monitor.py monitors 209 Microsoft Learn URLs daily
    ↓
Changes detected → GitHub PR with report
    ↓
Manual review + optional /review-learn-changes AI assist
    ↓
Merged to update baseline
    ↓

FSI-AgentGov-Solutions (Implementations)
    ↓
Solutions implement controls via:
  - Power Automate flows → Dataverse
  - PowerShell scripts → M365 APIs
  - Python automation → Azure services
  - Power BI dashboards → reporting
    ↓
Data flows to: Graph API, Sentinel, App Insights, Dataverse
```

---

*Integration audit: 2026-02-02*
