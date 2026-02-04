# Feature Landscape: Documentation Improvements & Solution Completions

**Project:** FSI Agent Governance Framework v2 Milestone
**Domain:** Technical documentation improvements + compliance solution completions
**Researched:** 2026-02-04
**Confidence:** HIGH

---

## Executive Summary

This research covers six feature domains for the v2 milestone: MkDocs navigation improvements, playbook discoverability patterns, PowerShell security hardening for FSI, and two solution completions (Compliance Dashboard and Scope Drift Monitor). All features have clear industry patterns and expected behaviors documented in official Microsoft and MkDocs Material sources.

**Key Finding:** Documentation improvements are table stakes for usability at scale (254+ playbooks). Solution security hardening is table stakes for FSI production deployment. Compliance aggregation and scope drift monitoring are differentiators in the AI governance space.

---

## Table Stakes Features

Features users expect. Missing these makes the product feel incomplete or unprofessional.

### 1. MkDocs Breadcrumb Navigation

**Feature:** Enable `navigation.path` in Material for MkDocs to display breadcrumb trails above page titles.

**Why Expected:**
- Material for MkDocs v9.7.0+ includes this as a standard navigation feature
- Users visiting 254+ playbook pages need orientation context
- Mobile users especially need breadcrumb navigation for smaller screens
- Industry standard across all major documentation platforms (Docusaurus, ReadTheDocs, etc.)

**Complexity:** Low

**Implementation:**
```yaml
theme:
  features:
    - navigation.path  # Breadcrumb navigation
```

**Evidence:**
- [Material for MkDocs Navigation Guide](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- Currently enabled: `navigation.instant`, `navigation.tracking`, `navigation.sections`
- Missing: `navigation.path` (breadcrumbs)

**Dependencies:** None (configuration-only change)

**Notes:** Can be hidden on specific pages using frontmatter `hide` property if needed.

---

### 2. Playbook Discoverability via Admonitions

**Feature:** Add admonition boxes to control pages surfacing related playbooks.

**Why Expected:**
- 248 control playbooks are "orphaned" - only discoverable via direct navigation or search
- Technical documentation standard practice: callout boxes for related content
- Material for MkDocs, Docusaurus, MyST Markdown all implement admonitions as core features
- "Related Implementation Guides" sections are expected in governance frameworks

**Complexity:** Low

**Implementation Pattern:**
```markdown
!!! info "Implementation Guides"

    - **[Portal Walkthrough](../playbooks/control-implementations/1.1/portal-walkthrough.md)** - Step-by-step UI configuration
    - **[PowerShell Setup](../playbooks/control-implementations/1.1/powershell-setup.md)** - Automation scripts
    - **[Verification Testing](../playbooks/control-implementations/1.1/verification-testing.md)** - Test cases and evidence collection
    - **[Troubleshooting](../playbooks/control-implementations/1.1/troubleshooting.md)** - Common issues and resolutions
```

**Evidence:**
- [Material for MkDocs Admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)
- [MarkdownTools Admonitions Guide](https://blog.markdowntools.com/posts/markdown-admonitions-callouts-complete-guide)
- Current usage: DANGER admonitions for API deprecations (Phase 1), need INFO admonitions for discoverability

**Dependencies:** None (Markdown extension already enabled)

**Notes:** Avoid overuse - research shows too many callouts reduce effectiveness. Limit to 1-2 per control page.

---

### 3. Navigation Auto-Generation

**Feature:** Eliminate manual mkdocs.yml nav maintenance by using directory structure or plugin-based generation.

**Why Expected:**
- 254 playbook files require manual nav entries today
- MkDocs auto-generates nav when `nav:` section is omitted
- Sites with 100+ pages use either auto-generation or plugins (mkdocs-awesome-pages, mkdocs-gen-nav)
- Manual nav maintenance is error-prone and blocks scalability

**Complexity:** Medium

**Implementation Options:**

**Option A: Full Auto-Generation (Simplest)**
- Remove `nav:` section from mkdocs.yml
- MkDocs auto-discovers all markdown files
- **Tradeoff:** Loses custom ordering, alphabetical only

**Option B: Hybrid with Awesome Pages Plugin**
- Keep curated nav for framework/controls
- Use `.pages` files for playbook directories
- **Tradeoff:** Adds plugin dependency

**Option C: Current Manual (Status Quo)**
- Continue manual nav entries
- **Tradeoff:** Doesn't scale beyond current 254 playbooks

**Evidence:**
- [MkDocs Navigation Configuration](https://www.mkdocs.org/user-guide/configuration/)
- [mkdocs-awesome-pages-plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)
- Current state: Manual nav for all sections (framework, controls, playbooks, reference)

**Dependencies:** Plugin installation if Option B chosen

**Notes:** Phase 1 should research actual nav requirements before committing to implementation approach.

---

### 4. PowerShell Security Hardening (FSI Production)

**Feature:** Production-ready PowerShell scripts with FSI security controls.

**Why Expected:**
- Financial services environments require defense-in-depth security
- Current tech debt: `ConvertTo-SecureString -AsPlainText -Force` exposes secrets (v1 audit finding)
- Current tech debt: Zero try/catch error handling in critical scripts
- Australian Cyber Security Centre and US government guidance mandate these controls for production environments

**Complexity:** Medium-High

**Required Controls:**

| Control | Current State | Target State | Priority |
|---------|---------------|--------------|----------|
| **Secrets Management** | Plaintext ConvertTo-SecureString | Azure Key Vault or SecretManagement module | CRITICAL |
| **Error Handling** | Zero try/catch blocks | Comprehensive error handling with logging | HIGH |
| **Module Requirements** | Missing #Requires statements | All scripts declare module dependencies | MEDIUM |
| **Execution Policy** | Not enforced | Scripts signed or RemoteSigned policy | MEDIUM |
| **Logging** | Basic Write-Host | Structured logging with audit trail | MEDIUM |
| **Constrained Language Mode** | Not tested | Verify scripts work in ConstrainedLanguage mode | LOW |

**Implementation Pattern:**

```powershell
#Requires -Version 7.0
#Requires -Modules Microsoft.PowerShell.SecretManagement, Az.KeyVault

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Environment,

    [Parameter()]
    [string]$VaultName = "fsi-secrets-vault"
)

try {
    # Retrieve secrets from vault (never hardcode)
    $credential = Get-Secret -Name "ServicePrincipalSecret" -Vault $VaultName -AsPlainText

    # Business logic with error handling
    Connect-ServicePrincipal -Credential $credential -Environment $Environment

    # Structured logging
    Write-Information "Connected to environment: $Environment" -InformationAction Continue

} catch {
    Write-Error "Failed to connect: $_"
    Write-EventLog -LogName Application -Source "FSI-AgentGov" -EventId 1001 -Message "Connection failure: $_"
    exit 1
} finally {
    # Cleanup
    if ($credential) { Clear-Variable -Name credential }
}
```

**Evidence:**
- [PowerShell Security Features - Microsoft Learn](https://learn.microsoft.com/en-us/powershell/scripting/security/security-features)
- [Australian Cyber Security Centre - Securing PowerShell](https://www.cyber.gov.au/resources-business-and-government/maintaining-devices-and-systems/system-hardening-and-administration/system-administration/securing-powershell-enterprise)
- [PowerShell Security Hardening Guide - CodeLucky](https://codelucky.com/powershell-security-hardening/)
- Current v1 tech debt: 12 scripts missing #Requires, 1 CRITICAL secrets exposure, 1 HIGH error handling gap

**Dependencies:**
- Azure Key Vault (if using Azure-based secrets)
- PowerShell SecretManagement module (v1.1+)
- PowerShell 7.0+ for modern security features

**Notes:** FSI environments may require HSM-backed vaults (Azure Key Vault Premium) for FIPS 140-3 Level 3 compliance.

---

### 5. Compliance Dashboard - Core Components

**Feature:** Aggregated compliance reporting across 62 controls with Power BI + Dataverse.

**Why Expected:**
- SOX 404, FINRA 3120, OCC 2011-12 require compliance status reporting
- Current state: Beta (v1.0.0-beta) - Dataverse schema exists, Power BI template requires manual creation
- Industry standard: Compliance dashboards aggregate data from multiple sources into unified view
- Power Platform + Dataverse is Microsoft's recommended approach for M365 compliance dashboards

**Complexity:** Medium-High

**Core Architecture Components:**

| Component | Purpose | Current State | Target State |
|-----------|---------|---------------|--------------|
| **Dataverse Tables** | Store compliance data | ✓ Schema defined | Add audit log tables |
| **Power Automate Flows** | Data collection | Documented only | Deploy 3 core flows |
| **Power BI Template** | Dashboard visualization | Manual creation required | Automated .pbit template |
| **DAX Measures** | Compliance calculations | Documented | Implement in template |
| **Sample Data** | Demo/testing | ✓ JSON fixture exists | Load script validated |

**Required Data Flows:**

```
1. Purview Compliance Manager → Power Automate → Dataverse
   - Compliance scores, assessment status (Daily)

2. Power Platform Admin Center → Power Automate → Dataverse
   - Environment count, DLP policy status (Daily)

3. Environment Lifecycle Management → Dataverse
   - Zone classification, governance status (Real-time)

4. FINRA Supervision Workflow → Dataverse (if deployed)
   - Queue metrics, review completion rates (Hourly)

5. Dataverse → Power BI
   - DirectQuery or Import mode
```

**Evidence:**
- [Dataverse Auditing - Power Platform Architecture](https://learn.microsoft.com/en-us/power-platform/architecture/key-concepts/dataverse-auditing)
- [Power BI Compliance Dashboard Best Practices 2026](https://multishoring.com/blog/power-bi-compliance-dashboard-2/)
- Current FSI-AgentGov-Solutions/compliance-dashboard: 11 files, schema complete, flows documented, Power BI template gap

**Dependencies:**
- Power BI Pro or Premium (for dashboard hosting)
- Dataverse capacity (compliance data storage)
- Power Automate Premium (data collection flows)
- Microsoft 365 E5 or E5 Compliance (Purview API access)

**Notes:** Organizations using automated compliance dashboards reduce audit preparation time by 40% (industry benchmark).

---

### 6. Scope Drift Monitor - Detection Logic

**Feature:** Detect AI agent data access beyond declared scope (connectors, SharePoint sites, Dataverse tables, external APIs).

**Why Expected:**
- GDPR Article 5(1)(c) requires data minimization
- Microsoft Agent 365 governance mandate: "grant agents access only to specific data sources required"
- Current state: WIP (v1.0.0) - Baseline script exists, detection logic not implemented
- 2026 AI governance standard: scope drift detection with post-market monitoring (regulatory expectation)

**Complexity:** High

**Core Detection Architecture:**

| Component | Purpose | Current State | Target State |
|-----------|---------|---------------|--------------|
| **Agent Scope Baseline** | Define allowed access | ✓ Schema defined | Baseline capture script validated |
| **Access Log Aggregation** | Collect actual access | Not implemented | 4 data sources integrated |
| **Drift Detection Engine** | Compare baseline vs actual | Not implemented | Real-time + batch detection |
| **Alert Workflow** | Notify on violations | Not implemented | Teams/email alerts |
| **Expansion Approval** | Request scope changes | Not implemented | Approval workflow |

**Detection Data Sources:**

| Source | Events Captured | Availability |
|--------|----------------|--------------|
| **Unified Audit Log** | CopilotInteraction with connector details | M365 E5 or E5 Compliance |
| **Defender CloudAppEvents** | Shadow IT detection, external API calls | Defender for Cloud Apps |
| **SharePoint Audit** | Site/library access events | SharePoint E3+ |
| **Dataverse Audit** | Table read/write operations | Dataverse capacity |

**Drift Violation Types:**

| Violation | Severity | Example | Detection Window |
|-----------|----------|---------|------------------|
| New Connector | High | Agent uses SQL connector not in scope | 15 min (real-time) |
| New SharePoint Site | Medium | Agent accesses HR site outside scope | 1 hour (near real-time) |
| New Dataverse Table | Medium | Agent queries Contacts when only Accounts allowed | 1 hour |
| New External API | High | Agent calls undeclared third-party API | 15 min |

**Evidence:**
- [Microsoft Agent 365 Governance Guide](https://www.charterglobal.com/microsoft-agent-365-and-enterprise-ai-governance-building-control-trust-and-scale-for-autonomous-systems/)
- [AI Agent Observability 2026 - N-iX](https://www.n-ix.com/ai-agent-observability/)
- [OWASP AI Agent Security Top 10 - 2026](https://medium.com/@oracle_43885/owasps-ai-agent-security-top-10-agent-security-risks-2026-fc5c435e86eb)
- Current FSI-AgentGov-Solutions/scope-drift-monitor: Baseline script exists, detection logic gap

**Dependencies:**
- Microsoft 365 E5 or E5 Compliance (Unified Audit Log)
- Defender for Cloud Apps (CloudAppEvents)
- Power Automate Premium (detection flows)
- Dataverse capacity (violation storage)

**Notes:** Post-market monitoring of drift and emergent behavior is a regulatory expectation under EU and US AI frameworks in 2026.

---

## Differentiators

Features that set the product apart. Not expected, but valued when present.

### 1. AI-Assisted Learn Monitor Review

**Current State:** Implemented in v1.2.37 via `/review-learn-changes` skill

**Value Proposition:**
- Automated analysis of Microsoft Learn documentation changes
- AI proposes specific documentation updates based on diff analysis
- Reduces manual review time from hours to minutes for 209 tracked URLs

**Competitive Advantage:** No other M365 governance framework has automated Learn monitoring with AI-assisted remediation

**Complexity:** Already implemented (not a v2 feature)

**Notes:** This is a differentiator that already exists. Document as best practice for other projects.

---

### 2. Unified Monitoring Architecture

**Current State:** Implemented in v1.2.37 (Phase 8)

**Value Proposition:**
- Single monitoring system for both Learn documentation and regulatory changes
- Consistent reporting format across monitors
- Extensible pattern for adding new monitors (GitHub dependencies, MCP server updates, etc.)

**Competitive Advantage:** Most frameworks monitor either documentation OR regulations, not both with unified architecture

**Complexity:** Already implemented (not a v2 feature)

**Notes:** v2 could extend this pattern to monitor GitHub Actions workflow updates or Power Platform release notes.

---

### 3. Navigation Pruning for Performance

**Feature:** Enable `navigation.prune` in Material for MkDocs to reduce site size by 33%+ for 254 playbook pages.

**Value Proposition:**
- Significantly faster page loads for large documentation sites
- Only visible navigation items included in rendered HTML
- Material for MkDocs specifically recommends this for 100+ page sites

**Competitive Advantage:** Most MkDocs sites don't optimize for scale. This shows awareness of performance at enterprise scale.

**Complexity:** Low

**Implementation:**
```yaml
theme:
  features:
    - navigation.prune  # For 100+ pages, reduces site size 33%+
```

**Evidence:**
- [Material for MkDocs Navigation - Large Site Optimization](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- "especially useful for documentation sites with 100+ or even 1,000+ of pages"

**Dependencies:** None (configuration-only)

**Notes:** Pairs well with breadcrumb navigation and auto-generation.

---

### 4. Cross-Repository Git Operations from FSI-AgentGov

**Current State:** Partially implemented (hooks + boundary-check.py)

**Value Proposition:**
- Edit solution scripts while working in framework documentation context
- Single working directory for cross-repo features
- Boundary hooks prevent accidental operations outside project scope

**Competitive Advantage:** Most multi-repo projects require manual cd between repos. This provides seamless cross-repo workflow.

**Complexity:** Low (infrastructure exists, needs documentation)

**Notes:** Not a v2 feature per se, but documenting this capability improves developer experience.

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain.

### 1. Complete mkdocs.yml Auto-Generation Without Control

**Why Avoid:**
- Framework section needs specific ordering (Overview → Governance Fundamentals → Zones → Lifecycle → Agent 365 → Regulatory → Operating Model)
- Control indexes need manual curation (Pillar 1 Security, Pillar 2 Management, etc.)
- Alphabetical auto-generation breaks pedagogical flow

**What to Do Instead:**
- Hybrid approach: Manual nav for framework/controls, auto-generation for playbooks only
- Use `nav:` section for curated content, let playbooks discover themselves
- Or use awesome-pages plugin with `.pages` files for directory-level control

**Evidence:** Current mkdocs.yml has carefully curated nav structure that provides learning path

---

### 2. Overly Complex Admonition Hierarchies

**Why Avoid:**
- Research shows too many callouts cause readers to ignore them
- Nested admonitions are visually cluttered
- "Before adding one or more admonitions to a topic, consider the visual impact they have on the page"

**What to Do Instead:**
- Limit to 1-2 admonition boxes per page
- Use INFO type for implementation guides (consistent pattern)
- Reserve DANGER/WARNING for actual risks (already used for API deprecations)

**Evidence:**
- [Splunk Style Guide - Admonitions](https://docs.splunk.com/Documentation/StyleGuide/current/StyleGuide/Notesandcautions)
- [MarkdownTools Guide - Best Practices](https://blog.markdowntools.com/posts/markdown-admonitions-callouts-complete-guide)

---

### 3. Inline Secrets in PowerShell Scripts (Even Encrypted)

**Why Avoid:**
- `ConvertTo-SecureString -AsPlainText -Force` exposes secrets in process memory
- SecureString is deprecated in .NET Core / PowerShell 7+
- FSI audit requirements mandate external secrets management (not inline)

**What to Do Instead:**
- Azure Key Vault for cloud-based secrets
- PowerShell SecretManagement module for cross-platform
- Environment variables only for non-production development
- NEVER commit secrets to Git (even encrypted)

**Evidence:**
- [PowerShell Secrets Management - AttuneOps](https://attuneops.io/powershell-secrets-management/)
- [Secure Password Management - SecureIdeas](https://www.secureideas.com/blog/secure-password-management-in-powershell-best-practices)
- Current v1 tech debt: `Register-ServicePrincipal.ps1` violates this (CRITICAL finding)

---

### 4. Power BI Import Mode for Real-Time Compliance Data

**Why Avoid:**
- Import mode caches data, causing stale compliance scores
- Real-time violations (scope drift, DLP events) need fresh data
- Import mode requires scheduled refresh, adding complexity

**What to Do Instead:**
- DirectQuery mode for Dataverse connections
- Aggregated tables can use Import for historical trends
- Hybrid model: DirectQuery for current state, Import for 90-day trends

**Evidence:**
- [Power BI Governance Best Practices - TheReportingHub](https://thereportinghub.com/power-bi/power-bi-governance-best-practices)
- Compliance Dashboard architecture diagram shows DirectQuery as primary mode

---

### 5. Unified Audit Log as Single Source for Scope Drift

**Why Avoid:**
- Unified Audit Log has 30-minute to 24-hour latency
- External API calls may not appear in Unified Audit Log
- Shadow IT detection requires Defender CloudAppEvents
- SharePoint audit provides more granular site access data

**What to Do Instead:**
- Multi-source detection: Unified Audit Log + Defender + SharePoint + Dataverse
- Aggregate access logs from all sources into Dataverse
- Different detection frequencies based on severity (15 min for High, 1 hour for Medium, daily for Low)

**Evidence:**
- [AI Agent Security Guide - MintMCP](https://www.mintmcp.com/blog/ai-agent-security)
- Scope Drift Monitor architecture shows 4 data sources, not just one

---

## Feature Dependencies

Dependencies between features and existing framework capabilities.

```
Breadcrumb Navigation
  ↓
No dependencies (standalone config change)

Playbook Discoverability
  ↓
Requires: Admonition markdown extension (already enabled)
  ↓
Depends on: 62 control pages already existing

Navigation Auto-Generation
  ↓
Conflicts with: Current manual nav structure (requires research phase)
May require: awesome-pages plugin (if hybrid approach)

PowerShell Security Hardening
  ↓
Requires: Azure Key Vault OR PowerShell SecretManagement module
Requires: PowerShell 7.0+ for modern security features
Modifies: 13 solution scripts in FSI-AgentGov-Solutions repo
  ↓
Blocks: Production deployment of solutions until CRITICAL/HIGH findings resolved

Compliance Dashboard Completion
  ↓
Requires: Dataverse capacity (already documented)
Requires: Power BI Pro/Premium (already documented)
Requires: Power Automate Premium (already documented)
  ↓
Depends on: Environment Lifecycle Management solution (for zone data)
Optionally depends on: FINRA Supervision Workflow (for supervision metrics)

Scope Drift Monitor Completion
  ↓
Requires: Microsoft 365 E5 or E5 Compliance (Unified Audit Log)
Requires: Defender for Cloud Apps (CloudAppEvents)
Requires: Dataverse capacity (violation storage)
  ↓
Depends on: Agent Scope Baseline script (already exists)
Integrates with: Controls 1.4, 1.5, 1.8 (connector policies, DLP, Defender)
```

---

## MVP Feature Prioritization

For v2 milestone, prioritize based on impact and complexity.

### Phase 1: Documentation Usability (High Impact, Low Complexity)

1. **Breadcrumb Navigation** - 5 minutes (config change)
2. **Playbook Discoverability** - 2-3 hours (62 control pages, templated admonitions)
3. **Navigation Pruning** - 5 minutes (config change)

**Rationale:** These are table stakes for 254-page documentation sites. Low complexity, immediate user value.

---

### Phase 2: PowerShell Security (Critical for Production, Medium Complexity)

1. **Secrets Management** - Replace `ConvertTo-SecureString -AsPlainText` with SecretManagement module
2. **Error Handling** - Add try/catch blocks to all scripts
3. **Module Requirements** - Add #Requires statements to 12 scripts

**Rationale:** Blocks production deployment. FSI audit requirement. CRITICAL and HIGH severity from v1 audit.

---

### Phase 3: Navigation Auto-Generation Research (Deferred)

1. **Research Phase** - Evaluate impact of auto-generation on learning path
2. **Prototype** - Test with playbooks directory only
3. **Decide** - Manual, hybrid (awesome-pages), or full auto-generation

**Rationale:** Medium complexity, needs research to avoid breaking pedagogical structure. Can be deferred to post-v2.

---

### Phase 4: Compliance Dashboard Completion (High Value, Medium Complexity)

1. **Power Automate Flows** - Deploy 3 core data collection flows
2. **Power BI Template** - Create automated .pbit with DAX measures
3. **Testing** - Validate with sample data load

**Rationale:** Differentiator for framework. Supports SOX/FINRA/OCC requirements. Beta status complete.

---

### Phase 5: Scope Drift Monitor Completion (High Value, High Complexity)

1. **Access Log Aggregation** - Implement 4 data source collectors
2. **Drift Detection Engine** - Compare baseline vs actual access
3. **Alert Workflow** - Teams/email notifications
4. **Expansion Approval** - Optional approval workflow

**Rationale:** Differentiator for AI agent governance. GDPR/GLBA requirement. Most complex feature, defer if timeline tight.

---

## Defer to Post-v2

Features valuable but not critical for v2 milestone:

- **Navigation Auto-Generation** - Needs research phase, risk of breaking learning path
- **Scope Drift Expansion Approval Workflow** - Nice-to-have, core detection is sufficient for v1.0.0
- **Compliance Dashboard Forecasting** - Advanced analytics, not required for SOX/FINRA compliance
- **Constrained Language Mode Testing** - Low priority security control, most FSI environments don't use CLM

---

## Quality Gates

Before marking features complete:

### Documentation Features
- [ ] Breadcrumb navigation visible on all pages except homepage
- [ ] All 62 control pages have INFO admonition box linking to 4 playbooks
- [ ] Navigation pruning reduces site size (measure with `mkdocs build` output)
- [ ] `mkdocs build --strict` passes with zero warnings

### PowerShell Security
- [ ] Zero instances of `ConvertTo-SecureString -AsPlainText -Force`
- [ ] All scripts have try/catch with error logging
- [ ] All scripts have #Requires statements for module dependencies
- [ ] PSScriptAnalyzer runs clean (no Critical or Error findings)

### Compliance Dashboard
- [ ] 3 Power Automate flows deployed and collecting data
- [ ] Power BI template (.pbit) opens in Power BI Desktop
- [ ] Sample data loads successfully
- [ ] All 5 dashboard pages render correctly
- [ ] DAX measures calculate compliance scores correctly

### Scope Drift Monitor
- [ ] Baseline capture script validated
- [ ] 4 data sources aggregating access logs
- [ ] Drift detection runs on schedule (real-time, near-real-time, daily)
- [ ] Alerts sent to Teams/email on violation
- [ ] Test case: New connector triggers High severity alert within 15 minutes

---

## Sources

### MkDocs Material & Documentation
- [Setting up navigation - Material for MkDocs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- [Configuration - MkDocs](https://www.mkdocs.org/user-guide/configuration/)
- [Admonitions - Material for MkDocs](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)
- [Markdown Admonitions Complete Guide - MarkdownTools](https://blog.markdowntools.com/posts/markdown-admonitions-callouts-complete-guide)

### PowerShell Security
- [PowerShell Security Features - Microsoft Learn](https://learn.microsoft.com/en-us/powershell/scripting/security/security-features)
- [Securing PowerShell in the Enterprise - Australian Cyber Security Centre](https://www.cyber.gov.au/resources-business-and-government/maintaining-devices-and-systems/system-hardening-and-administration/system-administration/securing-powershell-enterprise)
- [PowerShell Security Hardening Guide - CodeLucky](https://codelucky.com/powershell-security-hardening/)
- [PowerShell Secrets Management - AttuneOps](https://attuneops.io/powershell-secrets-management/)

### Power Platform & Compliance
- [Dataverse Auditing - Power Platform Architecture](https://learn.microsoft.com/en-us/power-platform/architecture/key-concepts/dataverse-auditing)
- [Power BI Compliance Dashboard Best Practices - Multishoring](https://multishoring.com/blog/power-bi-compliance-dashboard-2/)
- [Power Platform Governance Guide - SysKit](https://www.syskit.com/blog/scalable-power-platform-governance-guide/)
- [Power BI Governance Best Practices - TheReportingHub](https://thereportinghub.com/power-bi/power-bi-governance-best-practices)

### AI Agent Governance & Security
- [Microsoft Agent 365 Governance - Charter Global](https://www.charterglobal.com/microsoft-agent-365-and-enterprise-ai-governance-building-control-trust-and-scale-for-autonomous-systems/)
- [AI Agent Observability 2026 - N-iX](https://www.n-ix.com/ai-agent-observability/)
- [AI Agent Security Guide - MintMCP](https://www.mintmcp.com/blog/ai-agent-security)
- [OWASP AI Agent Security Top 10 - 2026](https://medium.com/@oracle_43885/owasps-ai-agent-security-top-10-agent-security-risks-2026-fc5c435e86eb)
- [Data, Privacy, and Security for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-copilot-privacy)

### Technical Documentation Trends
- [Technical Documentation Trends 2026 - Fluid Topics](https://www.fluidtopics.com/blog/industry-insights/technical-documentation-trends-2026/)
- [Discoverability in 2026 - Search Engine Land](https://searchengineland.com/discoverability-in-2026-how-digital-pr-and-social-search-work-together-467559)

---

*Researched: 2026-02-04*
*Confidence: HIGH (all sources verified with official Microsoft and MkDocs documentation)*
