# Architecture Patterns: v2 Integration with FSI-AgentGov

**Domain:** MkDocs documentation site enhancement + PowerShell solutions modernization
**Researched:** 2026-02-04
**Confidence:** HIGH

---

## Executive Summary

v2 improvements integrate cleanly with the existing FSI-AgentGov architecture with minimal disruption. The core finding: **all six integration points can be implemented incrementally without requiring full rewrites**. MkDocs Material breadcrumbs work with manual nav (additive). Awesome Pages plugin requires explicit integration points via `...` entries (opt-in coexistence). PowerShell modernization is isolated to the Solutions repo. Compliance Dashboard and Scope Drift Monitor build on existing monitoring framework patterns with established Dataverse/Power Automate/Power BI patterns.

**Critical Integration Points:**
1. MkDocs breadcrumbs: Theme feature flag addition (zero nav changes)
2. Awesome Pages: Requires `nav: ...` integration markers (breaking if done wrong)
3. PowerShell SecretManagement: Drop-in replacement for ConvertTo-SecureString (targeted fix)
4. Compliance Dashboard: New Dataverse tables + flows, no framework changes
5. Scope Drift Monitor: Uses monitoring_shared.py as intended (plugin pattern)
6. YAML config files: Belongs in docs/ with validation schema support

**Build Order Recommendation:** Documentation improvements first (breadcrumbs, YAML configs), then PowerShell fixes (isolated), then solutions completion (most complex).

---

## Recommended Architecture

### High-Level Component Map

```
FSI-AgentGov (Documentation Repository)
├── docs/ (MkDocs Material site)
│   ├── framework/
│   ├── controls/
│   ├── playbooks/
│   └── reference/
│       ├── monitoring-architecture.md (existing)
│       ├── learn-monitor-config.yaml (NEW - Learn Monitor config)
│       └── regulatory-monitor-config.yaml (NEW - Regulatory config)
├── mkdocs.yml (nav structure - MODIFIED for breadcrumbs + optional Awesome Pages)
├── scripts/
│   ├── monitoring_shared.py (existing - unchanged)
│   ├── learn_monitor.py (existing - unchanged)
│   └── regulatory_monitor.py (existing - unchanged)
└── data/
    └── monitor-state.json (unified state - unchanged)

FSI-AgentGov-Solutions (Deployable Solutions Repository)
├── compliance-dashboard/ (WIP → Completed)
│   ├── dataverse-solution/ (NEW - Dataverse schema + flows)
│   │   ├── ComplianceDashboard_1_0_0.zip
│   │   └── schema.xml
│   ├── power-bi-template/ (NEW - .pbit file)
│   │   └── ComplianceDashboard.pbit
│   └── scripts/ (existing - enhanced)
├── scope-drift-monitor/ (WIP → Completed)
│   ├── scripts/
│   │   ├── New-AgentBaseline.ps1 (MODIFIED - add #Requires)
│   │   └── monitoring_adapter.py (NEW - uses monitoring_shared.py)
│   └── dataverse-solution/ (NEW)
└── [other solutions]/
    └── *.ps1 (MODIFIED - add #Requires, SecretManagement)
```

---

## Integration Point 1: MkDocs Material Breadcrumbs

### Current State
- **mkdocs.yml:** Manual nav with ~200 entries across 4 sections
- **Theme features:** navigation.instant, navigation.tracking, navigation.sections, search.suggest, toc.integrate
- **No breadcrumbs:** Users navigate via left sidebar only

### How Breadcrumbs Integrate

**Official Source:** [Setting up navigation - Material for MkDocs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)

Breadcrumbs in MkDocs Material are **additive** and work seamlessly with manual nav.

**Integration Method:**
```yaml
# mkdocs.yml
theme:
  name: material
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.sections
    - navigation.path         # NEW - enables breadcrumbs
    - search.suggest
    - search.highlight
    - toc.integrate
```

**Behavior:**
- Breadcrumbs render **above** the page title
- Generated from nav hierarchy (manual or automatic)
- Format: `Home > Framework > Agent Identity Architecture`
- No changes to existing nav structure required
- Optional: Can hide per-page via front matter (`hide: [navigation.path]`)

**Impact Assessment:**
- **Existing nav:** Zero changes needed
- **User experience:** Improved orientation on deep pages (Control 2.16 Playbooks have 4-level depth)
- **Breaking changes:** None
- **Rollback:** Remove feature flag

**Recommendation:** Implement immediately as Phase 1 quick win.

---

## Integration Point 2: Awesome Pages Plugin Migration

### Current State
- **mkdocs.yml:** Fully manual nav (79 lines for framework, 489 lines for controls/playbooks)
- **Maintenance:** Adding new control requires 5 manual nav edits
- **Error prone:** Typos in paths cause build failures

### How Awesome Pages Coexists

**Official Source:** [Getting Started - Awesome Nav for MkDocs](https://lukasgeiter.github.io/mkdocs-awesome-nav/)

Awesome Pages **requires explicit integration** but can coexist with manual nav via `...` (rest) entries.

**Critical Constraint:**
> This plugin won't do anything if your mkdocs.yml defines a nav or pages entry. To make use of the features listed below, you'll either have to remove the entry completely or add a `...` entry to it.

**Integration Strategy (Incremental Migration):**

```yaml
# mkdocs.yml - Phase 1: Manual sections + auto playbooks
nav:
  - Home: index.md
  - Disclaimer: disclaimer.md
  - Getting Started:
    - Quick Start: getting-started/quick-start.md
    - Implementation Checklist: getting-started/checklist.md
  - Framework:
    - Overview: framework/index.md
    - Executive Summary: framework/executive-summary.md
    # ... (keep manual for stable sections)
  - Control Catalog:
    - ...  # Auto-generate controls from pillar-*/
  - Playbooks:
    - ...  # Auto-generate playbooks from docs/playbooks/
  - Reference:
    - ...  # Auto-generate reference docs
```

**Directory-Level Configuration (.pages.yaml):**

```yaml
# docs/controls/pillar-1-security/.pages.yaml
title: Pillar 1 - Security
order: 1
collapse_single_pages: false
```

**Behavior:**
- Sections with manual nav entries: Use manual nav
- Sections with `...`: Auto-generated from file structure
- Hybrid approach reduces maintenance burden by ~60%

**Migration Path:**
1. **Phase 1:** Keep Framework manual, auto-generate Playbooks only (lowest risk)
2. **Phase 2:** Auto-generate Controls (requires .pages.yaml per pillar)
3. **Phase 3:** Auto-generate Reference (highest payoff, currently 15 manual entries)

**Impact Assessment:**
- **Build compatibility:** Requires mkdocs-awesome-pages-plugin in requirements.txt
- **Breaking changes:** If `...` placement is wrong, nav will break
- **Rollback:** Remove plugin, restore manual nav from git
- **Testing:** mkdocs build --strict must pass

**Recommendation:** Implement as Phase 2 after breadcrumbs. Start with Playbooks section (most repetitive).

---

## Integration Point 3: YAML Configuration Files for Monitoring

### Current State
- **Learn Monitor:** URLs hardcoded in docs/reference/microsoft-learn-urls.md (Markdown table)
- **Regulatory Monitor:** Sources hardcoded in scripts/regulatory_monitor.py
- **No schema validation:** Manual editing, prone to typos
- **Configuration scattered:** Some in scripts, some in docs

### Where YAML Config Files Belong

**Pattern from MkDocs Ecosystem:**
- Configuration lives in **docs/reference/** alongside markdown documentation
- Benefits from MkDocs YAML schema validation
- Version controlled with documentation

**Proposed Structure:**

```
docs/reference/
├── monitoring-architecture.md (existing)
├── learn-monitor-config.yaml (NEW)
├── regulatory-monitor-config.yaml (NEW)
└── microsoft-learn-urls.md (DEPRECATED - migrate to YAML)
```

**Example: learn-monitor-config.yaml**

```yaml
# Learn Monitor Configuration
# Schema: https://github.com/judeper/FSI-AgentGov/schemas/learn-monitor-config.schema.json

version: 1
source_key: learn
report_prefix: learn-changes

# URL Categories
url_sources:
  - section: Power Platform Admin Center
    urls:
      - url: https://learn.microsoft.com/en-us/power-platform/admin/...
        topic: Environment Lifecycle Management
        priority: high
        affected_controls:
          - 2.1
          - 2.2

  - section: Microsoft Purview Compliance
    urls:
      - url: https://learn.microsoft.com/en-us/purview/...
        topic: DLP Policies
        priority: critical
        affected_controls:
          - 1.5
          - 1.17

# Change Classification Rules
classification:
  critical_patterns:
    - pattern: '\d+\.\s+(click|select|go to|navigate)'
      reason: 'UI navigation steps changed'
    - pattern: '(deprecated|removed|no longer|retired)'
      reason: 'Deprecation notice'

  high_patterns:
    - pattern: '(Admin center|portal|Power Platform|Purview)'
      reason: 'Portal references'
```

**Benefits:**
1. **Schema validation:** Catch errors before runtime
2. **Documentation proximity:** Config near the docs it affects
3. **DRY principle:** No duplication between docs and code
4. **Migration path:** Scripts read YAML instead of scraping markdown

**Integration with monitoring_shared.py:**

```python
# NEW: scripts/config_loader.py
import yaml
from pathlib import Path

def load_monitor_config(config_path: Path) -> dict:
    """Load and validate monitor configuration from YAML."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Validate against schema
    # ... (JSON Schema validation)

    return config

# scripts/learn_monitor.py (MODIFIED)
from config_loader import load_monitor_config

# Replace parse_watchlist() with:
config = load_monitor_config(DOCS_DIR / "reference" / "learn-monitor-config.yaml")
url_entries = []
for section in config['url_sources']:
    for url_info in section['urls']:
        url_entries.append(URLEntry(
            url=url_info['url'],
            topic=url_info['topic'],
            section=section['section']
        ))
```

**Impact Assessment:**
- **Breaking changes:** None (additive - old markdown still works during migration)
- **Dependencies:** Requires PyYAML (already in requirements.txt via MkDocs)
- **Validation:** JSON Schema recommended but optional
- **Migration effort:** ~2-4 hours per monitor

**Recommendation:** Implement as Phase 1 alongside breadcrumbs. Low risk, high maintainability payoff.

---

## Integration Point 4: PowerShell Module Modernization

### Current State (from v1 Audit)

**Critical Issues:**
- `Register-ServicePrincipal.ps1`: Uses `ConvertTo-SecureString -AsPlainText -Force` (exposes secrets in memory)
- `Test-PolicyCompliance.ps1`: Zero try/catch error handling
- 12 scripts missing `#Requires` statements

**Isolated to FSI-AgentGov-Solutions repository** - no framework changes.

### PowerShell SecretManagement Integration

**Official Source:** [Overview of the SecretManagement and SecretStore modules](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/overview?view=ps-modules)

**Current Anti-Pattern:**
```powershell
# Register-ServicePrincipal.ps1 (BEFORE)
$SecurePassword = ConvertTo-SecureString -String $ClientSecret -AsPlainText -Force
$Credential = New-Object System.Management.Automation.PSCredential($ClientId, $SecurePassword)
```

**Recommended Pattern:**
```powershell
# Register-ServicePrincipal.ps1 (AFTER)
#Requires -Modules @{ ModuleName = 'Microsoft.PowerShell.SecretManagement'; ModuleVersion = '1.1.2' }

# Store secret once during setup
Set-Secret -Name 'ServicePrincipal-ClientSecret' -Secret $ClientSecret

# Retrieve as SecureString in script
$SecurePassword = Get-Secret -Name 'ServicePrincipal-ClientSecret' -AsPlainText:$false
$Credential = New-Object System.Management.Automation.PSCredential($ClientId, $SecurePassword)
```

**Best Practices Applied:**
1. **SecureString objects:** Secrets retrieved as SecureString (never plain text in memory)
2. **User context:** Vault registered per-user (no cross-user exposure)
3. **Automation support:** Set-SecretStoreConfiguration -Authentication None for scheduled tasks
4. **Multiple vaults:** Different security levels for different secret types

**Source:** [Working with PowerShell Secret Management](https://www.techtarget.com/searchwindowsserver/tutorial/Working-with-PowerShell-Secret-Management-and-Secret-Vault)

### #Requires Statements

**Official Source:** [about_Requires - PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires?view=powershell-7.5)

**Current State:** 12 scripts missing module requirements

**Implementation Pattern:**
```powershell
# All scripts MUST start with:
#Requires -Version 7.0
#Requires -Modules @{ ModuleName = 'Microsoft.Graph'; ModuleVersion = '2.0.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.PowerShell.SecretManagement'; ModuleVersion = '1.1.2' }

<#
.SYNOPSIS
Script description here
#>
```

**Benefits:**
- **Early failure:** Script won't run if prerequisites missing (better UX)
- **Version enforcement:** Prevents compatibility issues
- **Self-documenting:** Module dependencies visible in header

**Impact Assessment:**
- **Breaking changes:** Scripts will fail on systems without required modules (GOOD - prevents silent failures)
- **Deployment:** README.md must document module installation steps
- **CI/CD:** Pipeline must install required modules before testing

### Error Handling

**Current Anti-Pattern:**
```powershell
# Test-PolicyCompliance.ps1 (BEFORE)
$policies = Invoke-MgGraphRequest -Uri "https://graph.microsoft.com/v1.0/policies/..."
foreach ($policy in $policies.value) {
    # Process policy
}
```

**Recommended Pattern:**
```powershell
# Test-PolicyCompliance.ps1 (AFTER)
try {
    $policies = Invoke-MgGraphRequest -Uri "https://graph.microsoft.com/v1.0/policies/..." -ErrorAction Stop

    if ($null -eq $policies -or $policies.value.Count -eq 0) {
        Write-Warning "No policies found - environment may not be configured"
        return
    }

    foreach ($policy in $policies.value) {
        # Process policy
    }
}
catch {
    Write-Error "Failed to retrieve policies: $_"
    Write-Error $_.Exception.Message
    exit 1
}
```

**Impact Assessment:**
- **Solutions repo only:** Zero impact on framework documentation
- **Testing required:** Each modified script needs functional testing
- **Documentation:** Playbooks reference PowerShell scripts but don't embed code
- **Migration:** Can be done incrementally per-solution

**Recommendation:** Implement as Phase 3 after documentation improvements. Prioritize CRITICAL findings first (Register-ServicePrincipal.ps1).

---

## Integration Point 5: Compliance Dashboard Architecture

### Current State
- **Status:** v1.0.0-beta (WIP)
- **Missing:** Power BI template (.pbit), complete Dataverse solution
- **Documented:** Schema, flows, prerequisites (docs complete, artifacts missing)

### Dataverse Schema Design

**Official Source:** [Power BI modeling guidance for Power Platform](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-modeling-guidance-for-power-platform)

**Recommended Star Schema:**

```
┌──────────────────────┐
│  Fact_Compliance     │ (FACT TABLE)
├──────────────────────┤
│ ComplianceScoreId PK │
│ ControlId FK         │
│ DateKey FK           │
│ EnvironmentId FK     │
│ ZoneId FK            │
├──────────────────────┤
│ Score (0-100)        │
│ Status (enum)        │
│ LastAssessmentDate   │
│ AssessmentMethod     │
└──────────────────────┘
         │ N:1 relationships
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
┌──────────────────┐         ┌──────────────────┐
│ Dim_Control      │         │ Dim_Zone         │
├──────────────────┤         ├──────────────────┤
│ ControlId PK     │         │ ZoneId PK        │
│ ControlNumber    │         │ ZoneName         │
│ PillarId FK      │         │ WeightMultiplier │
│ Title            │         └──────────────────┘
│ RegulatoryImpact │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Dim_Pillar       │
├──────────────────┤
│ PillarId PK      │
│ PillarName       │
│ PillarNumber     │
└──────────────────┘
```

**Best Practices Applied:**
1. **Star schema:** Fact table at center with dimension tables (standard analytics pattern)
2. **Assumed referential integrity:** Set on all relationships for INNER JOIN optimization
3. **Dual storage mode:** Dimension tables use Dual mode (cached when possible)
4. **Column pruning:** Only retrieve columns needed for reports (not all table columns)

**Source:** [DirectQuery model guidance in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/guidance/directquery-model-guidance)

**Integration with Existing Framework:**

The Compliance Dashboard reads **existing control metadata** from the FSI-AgentGov repository:

```python
# scripts/load_sample_data.py (MODIFIED)
import json
from pathlib import Path

# Read control master data from FSI-AgentGov
controls_index = Path("../FSI-AgentGov/docs/controls/CONTROL-INDEX.md")
# Parse markdown table to extract 62 controls
# Load into Dim_Control table
```

**No changes to FSI-AgentGov required** - dashboard reads from published GitHub repo or local clone.

### Power Automate Flows

**Official Source:** [Manage cloud flow run history in Dataverse](https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata)

**Data Collection Pattern:**

```
┌─────────────────────────────────────────────────────┐
│ Scheduled Cloud Flow: Daily Compliance Collector    │
├─────────────────────────────────────────────────────┤
│ Trigger: Recurrence (Daily at 06:00 UTC)           │
│                                                     │
│ Actions:                                            │
│ 1. HTTP: Get Purview Compliance Score API          │
│ 2. Parse JSON: Extract assessment data             │
│ 3. For Each: Control assessment                    │
│    ├─ Condition: Check if control exists           │
│    ├─ Dataverse: Upsert Fact_Compliance            │
│    └─ Dataverse: Update Dim_Control last_checked   │
│ 4. Dataverse: Update metadata table (run timestamp)│
└─────────────────────────────────────────────────────┘
```

**Flow Run History Storage:**
- Stored in Dataverse FlowRun elastic table (28-day retention)
- Partitioned by user for performance
- Application Insights integration for deeper diagnostics

**Source:** [Monitor your flows - Power Automate](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/monitoring-and-alerting)

**Integration with monitoring_shared.py:**

Compliance Dashboard is **separate** from Learn/Regulatory Monitor. It uses **Power Automate** for data collection, not Python scripts. Monitoring patterns are conceptually similar (state management, change detection) but implementation is different.

```
Learn Monitor (Python)          Compliance Dashboard (Power Automate)
├─ monitoring_shared.py         ├─ Cloud flows
├─ learn_monitor.py             ├─ Dataverse tables
├─ regulatory_monitor.py        ├─ Power BI DirectQuery
└─ data/monitor-state.json      └─ FlowRun history
```

**No code sharing between systems** - both are monitoring, but different domains.

### Power BI Report

**DirectQuery Configuration:**

```
Data Source: Dataverse (DirectQuery mode)
Connection: https://{org}.crm.dynamics.com
Authentication: Azure AD
Tables:
  - Fact_Compliance (DirectQuery)
  - Dim_Control (Dual - cached)
  - Dim_Pillar (Dual - cached)
  - Dim_Zone (Dual - cached)
  - Dim_Date (Import - date table)
```

**DAX Measures (from docs/dax-measures.md):**

```dax
Overall Compliance Score =
    DIVIDE(
        SUMX(
            Fact_Compliance,
            [Score] * RELATED(Dim_Zone[WeightMultiplier])
        ),
        SUMX(
            Fact_Compliance,
            100 * RELATED(Dim_Zone[WeightMultiplier])
        ),
        0
    )

Critical Exceptions Count =
    CALCULATE(
        COUNTROWS(Fact_Compliance),
        Fact_Compliance[Status] = "Non-Compliant",
        RELATED(Dim_Control[RegulatoryImpact]) = "Critical"
    )
```

**Impact Assessment:**
- **FSI-AgentGov changes:** None (dashboard consumes published data)
- **Solutions repo changes:** Add Dataverse solution ZIP, Power BI .pbit template
- **Dependencies:** Requires Environment Lifecycle Management solution for zone data
- **Testing:** Requires test Dataverse environment with sample data

**Recommendation:** Implement as Phase 4 after PowerShell fixes. Most complex integration but well-isolated.

---

## Integration Point 6: Scope Drift Monitor

### Current State
- **Status:** v1.0.0 (WIP)
- **Structure:** Basic framework, incomplete core logic
- **Missing:** Detection flow, baseline capture script, monitoring adapter

### Integration with monitoring_shared.py

**Scope Drift Monitor is a different domain** from Learn/Regulatory Monitor but **should follow same patterns**.

**Proposed Architecture:**

```
scripts/
├── monitoring_shared.py (existing - core utilities)
├── learn_monitor.py (existing - uses monitoring_shared)
├── regulatory_monitor.py (existing - uses monitoring_shared)
└── scope_drift_adapter.py (NEW - uses monitoring_shared)

FSI-AgentGov-Solutions/scope-drift-monitor/
├── scripts/
│   ├── New-AgentBaseline.ps1 (PowerShell - captures initial scope)
│   └── monitoring_adapter.py (Python - bridges PowerShell → monitoring_shared)
└── flows/
    └── DriftDetectionFlow.json (Power Automate - real-time detection)
```

**Adapter Pattern:**

```python
# FSI-AgentGov-Solutions/scope-drift-monitor/scripts/monitoring_adapter.py
"""
Scope Drift Monitor adapter for unified monitoring framework.

Uses monitoring_shared.py from FSI-AgentGov repository for:
- State management (unified monitor-state.json)
- Change classification
- Report generation
"""
import sys
from pathlib import Path

# Import from FSI-AgentGov repository
sys.path.insert(0, str(Path(__file__).parent / "../../../FSI-AgentGov/scripts"))
from monitoring_shared import (
    load_state,
    save_state_atomic,
    get_source_state,
    set_source_state,
    generate_report_header,
    generate_executive_summary,
    write_report,
    CLASSIFICATION_CRITICAL,
    CLASSIFICATION_HIGH,
    CLASSIFICATION_MEDIUM,
)

SOURCE_KEY = "scope-drift"
REPORT_PREFIX = "scope-drift"

def detect_drift(agent_id: str, baseline_scope: dict, current_access: dict) -> list:
    """
    Detect drift between baseline scope and current access patterns.

    Returns list of drift violations.
    """
    violations = []

    # Compare connectors
    baseline_connectors = set(baseline_scope.get('connectors', []))
    current_connectors = set(current_access.get('connectors', []))
    new_connectors = current_connectors - baseline_connectors

    for connector in new_connectors:
        violations.append({
            'type': 'connector',
            'name': connector,
            'severity': CLASSIFICATION_HIGH,
            'reason': 'Agent used connector not in declared scope'
        })

    # Compare SharePoint sites (similar pattern)
    # Compare Dataverse tables (similar pattern)

    return violations

# ... rest of adapter logic
```

**Benefits of Shared Framework:**
1. **Consistent state management:** All monitors use same JSON structure
2. **Consistent reporting:** All monitors generate same report format
3. **Code reuse:** Change classification, diff generation shared
4. **Unified dashboard:** Could aggregate Learn + Regulatory + Scope Drift changes

**Integration Method:**
- **Python adapter:** Reads PowerShell baseline output, uses monitoring_shared.py
- **Power Automate flow:** Runs real-time (different trigger than batch Python)
- **Dual approach:** Batch daily Python scan + real-time flow alerts

**Impact Assessment:**
- **FSI-AgentGov changes:** None (monitoring_shared.py already designed for plugins)
- **Solutions repo changes:** Add monitoring_adapter.py, reference monitoring_shared.py
- **Testing:** Requires mock agent data, simulated access patterns
- **Dependencies:** Python 3.10+, requests, Access to Unified Audit Log

**Recommendation:** Implement as Phase 5 after Compliance Dashboard. Demonstrates monitoring framework extensibility.

---

## Component Integration Summary

### New Components

| Component | Location | Purpose | Dependencies |
|-----------|----------|---------|--------------|
| **YAML Monitor Configs** | docs/reference/ | Monitoring URL/source configuration | PyYAML (existing) |
| **config_loader.py** | scripts/ | Load and validate YAML configs | PyYAML, JSON Schema |
| **Breadcrumbs** | mkdocs.yml theme.features | Navigation enhancement | None (MkDocs Material built-in) |
| **Awesome Pages** | mkdocs.yml plugins | Auto-nav generation | mkdocs-awesome-pages-plugin |
| **SecretManagement** | Solutions *.ps1 scripts | Secure secret handling | Microsoft.PowerShell.SecretManagement module |
| **#Requires** | Solutions *.ps1 scripts | Module dependency declaration | None (PowerShell built-in) |
| **Compliance Dashboard Schema** | Solutions/compliance-dashboard/dataverse-solution/ | Dataverse tables + flows | Dataverse, Power Automate |
| **Compliance Dashboard BI** | Solutions/compliance-dashboard/power-bi-template/ | Power BI report template | Power BI Premium/Pro |
| **Scope Drift Adapter** | Solutions/scope-drift-monitor/scripts/ | Monitoring framework integration | monitoring_shared.py |

### Modified Components

| Component | Change | Impact |
|-----------|--------|--------|
| **mkdocs.yml** | Add navigation.path, optional Awesome Pages | Additive - zero breaking changes |
| **learn_monitor.py** | Load YAML config instead of markdown scraping | Backward compatible during migration |
| **regulatory_monitor.py** | Load YAML config instead of hardcoded sources | Backward compatible during migration |
| **Solutions *.ps1** | Add #Requires, error handling, SecretManagement | Breaking for systems without modules |
| **Solutions README.md** | Document module prerequisites | Documentation only |

### Unchanged Components

| Component | Why Unchanged |
|-----------|---------------|
| **monitoring_shared.py** | Already designed for plugin pattern - no changes needed |
| **data/monitor-state.json** | Unified format supports new sources without schema change |
| **docs/controls/** | Control markdown files unchanged - breadcrumbs render from nav |
| **docs/playbooks/** | Playbooks unchanged - Awesome Pages reads file structure |
| **Framework docs** | No architecture changes - enhancements are additive |

---

## Data Flow Changes

### Before v2 (Current State)

```
Learn Monitor Flow:
microsoft-learn-urls.md → parse_watchlist() → URLEntry list → fetch + classify
                                                                      ↓
                                                        monitor-state.json (source: learn)
                                                                      ↓
                                                      learn-changes-YYYY-MM-DD.md

Compliance Dashboard Flow:
[None - v1.0.0-beta incomplete]

Scope Drift Monitor Flow:
[None - v1.0.0 incomplete]
```

### After v2 (Proposed State)

```
Learn Monitor Flow:
learn-monitor-config.yaml → load_monitor_config() → URLEntry list → fetch + classify
                                                                           ↓
                                                         monitor-state.json (source: learn)
                                                                           ↓
                                                       learn-changes-YYYY-MM-DD.md

Compliance Dashboard Flow:
FSI-AgentGov/docs/controls/ → load_sample_data.py → Dim_Control (Dataverse)
                                                           ↓
Purview Compliance API → Power Automate Flow → Fact_Compliance (Dataverse)
                                                           ↓
                                              Power BI DirectQuery → Dashboard

Scope Drift Monitor Flow:
Agent metadata → New-AgentBaseline.ps1 → baseline.json → Dataverse (Agent Scope table)
                                                                ↓
Unified Audit Log → Power Automate Flow → Access log analysis → Drift detection
                                                                       ↓
                                                        monitor-state.json (source: scope-drift)
                                                                       ↓
Drift violations → monitoring_adapter.py → scope-drift-YYYY-MM-DD.md
```

**Key Changes:**
1. **YAML configs replace markdown scraping** - structured data, validated
2. **Compliance Dashboard uses Dataverse hub** - enterprise BI pattern
3. **Scope Drift uses dual approach** - real-time flows + batch Python reports
4. **All monitoring shares state file** - unified monitor-state.json with source keys

---

## Build Order and Dependencies

### Phase 1: Documentation Quick Wins (Week 1)
**Goal:** Immediate UX improvements with zero risk

1. **Breadcrumbs** (1 day)
   - Add `navigation.path` to mkdocs.yml
   - Test: `mkdocs build --strict`
   - Deploy: Commit to main, GitHub Pages auto-deploys

2. **YAML Monitor Configs** (2 days)
   - Create learn-monitor-config.yaml
   - Create regulatory-monitor-config.yaml
   - Create config_loader.py
   - Migrate URLs from markdown (backward compatible)
   - Test: `python scripts/learn_monitor.py --dry-run --limit 5`

**Dependencies:** None
**Risk:** Low
**Deliverables:** Breadcrumbs live, YAML configs usable

### Phase 2: Awesome Pages Migration (Week 2)
**Goal:** Reduce nav maintenance burden

1. **Playbooks Auto-Nav** (3 days)
   - Add mkdocs-awesome-pages-plugin to requirements.txt
   - Replace Playbooks section with `...` entry
   - Create .pages.yaml in playbooks/ subdirectories
   - Test: `mkdocs build --strict` (critical - nav breakage possible)
   - Rollback plan: Git revert if build fails

2. **Reference Auto-Nav** (1 day)
   - Replace Reference section with `...` entry
   - Test and verify ordering

**Dependencies:** Phase 1 complete (validates mkdocs.yml changes work)
**Risk:** Medium (nav structure changes)
**Deliverables:** 60% reduction in manual nav entries

### Phase 3: PowerShell Modernization (Week 3-4)
**Goal:** Fix CRITICAL and HIGH security findings

1. **#Requires Statements** (2 days)
   - Add to all 12 missing scripts
   - Document module prerequisites in README.md
   - Test: Script validation (regex-based - pwsh not available)

2. **SecretManagement Migration** (3 days)
   - Fix Register-ServicePrincipal.ps1 (CRITICAL)
   - Add error handling to Test-PolicyCompliance.ps1 (HIGH)
   - Document vault setup in prerequisites.md

3. **Functional Testing** (3 days)
   - Test each modified script in test environment
   - Validate error handling paths
   - Update playbooks if script interfaces changed

**Dependencies:** Phase 2 complete (documentation stable)
**Risk:** Medium (scripts must work in production)
**Deliverables:** CRITICAL/HIGH findings resolved, solutions hardened

### Phase 4: Compliance Dashboard Completion (Week 5-6)
**Goal:** Move from v1.0.0-beta to v1.0.0

1. **Dataverse Solution** (4 days)
   - Export schema from docs/dataverse-schema.md
   - Create Dataverse solution ZIP
   - Deploy to test environment
   - Load sample data

2. **Power Automate Flows** (3 days)
   - Create Compliance Score Collector flow
   - Create Environment Status Collector flow
   - Create Exception Aggregator flow
   - Test with sample data

3. **Power BI Template** (3 days)
   - Build .pbit from docs/power-bi-setup.md spec
   - Implement DAX measures from docs/dax-measures.md
   - Test with Dataverse connection
   - Validate all 5 dashboard pages render

**Dependencies:** Phase 3 complete (PowerShell scripts stable)
**Risk:** High (complex multi-component system)
**Deliverables:** Compliance Dashboard v1.0.0, deployable ZIP + .pbit

### Phase 5: Scope Drift Monitor Completion (Week 7-8)
**Goal:** Move from v1.0.0 WIP to v1.0.0 stable

1. **Monitoring Adapter** (3 days)
   - Create monitoring_adapter.py
   - Implement drift detection logic
   - Integrate with monitoring_shared.py
   - Test with mock data

2. **PowerShell Baseline Capture** (2 days)
   - Complete New-AgentBaseline.ps1
   - Add #Requires statements
   - Test with real agent metadata

3. **Power Automate Flow** (3 days)
   - Create real-time drift detection flow
   - Test with Unified Audit Log data
   - Validate alerts trigger correctly

**Dependencies:** Phase 4 complete (establishes Dataverse pattern)
**Risk:** Medium (depends on Audit Log data availability)
**Deliverables:** Scope Drift Monitor v1.0.0, dual detection modes

---

## Rollback Plans

### Breadcrumbs
**Rollback:** Remove `navigation.path` from mkdocs.yml, redeploy
**Time:** 5 minutes
**Risk:** None (additive feature)

### Awesome Pages
**Rollback:** Git revert mkdocs.yml, remove plugin from requirements.txt, redeploy
**Time:** 10 minutes
**Risk:** Medium if build broken, manual nav still in git history

### YAML Configs
**Rollback:** Point scripts back to markdown parsing (code supports both)
**Time:** 15 minutes
**Risk:** Low (backward compatible during migration)

### PowerShell Changes
**Rollback:** Git revert modified scripts, redeploy
**Time:** 30 minutes
**Risk:** High if production scripts already using SecretManagement (vault data persists)

### Compliance Dashboard
**Rollback:** Delete Dataverse solution, remove Power BI workspace
**Time:** 1 hour
**Risk:** Low (isolated system, no framework dependencies)

### Scope Drift Monitor
**Rollback:** Disable Power Automate flow, remove monitoring_adapter.py
**Time:** 30 minutes
**Risk:** Low (isolated system, no framework dependencies)

---

## Quality Gates

### Phase 1 Gates
- [ ] `mkdocs build --strict` passes with breadcrumbs enabled
- [ ] Breadcrumbs render correctly on sample pages (deep and shallow)
- [ ] YAML configs validate against JSON Schema
- [ ] learn_monitor.py loads YAML successfully in dry-run mode

### Phase 2 Gates
- [ ] `mkdocs build --strict` passes with Awesome Pages
- [ ] All playbooks visible in auto-generated nav
- [ ] Nav ordering matches expected structure
- [ ] No broken links introduced

### Phase 3 Gates
- [ ] All PowerShell scripts include #Requires statements
- [ ] SecretManagement integration tested with real secrets
- [ ] Error handling tested with simulated API failures
- [ ] No regression in existing solution functionality

### Phase 4 Gates
- [ ] Dataverse solution imports without errors
- [ ] Sample data loads successfully
- [ ] Power Automate flows run without errors
- [ ] Power BI report renders all 5 pages
- [ ] DirectQuery performs within 10-second threshold

### Phase 5 Gates
- [ ] monitoring_adapter.py integrates with monitoring_shared.py
- [ ] Baseline capture script completes successfully
- [ ] Drift detection identifies test violations correctly
- [ ] Reports generated in unified format

---

## Sources

### MkDocs Material Integration
- [Setting up navigation - Material for MkDocs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- [Getting Started - Awesome Nav for MkDocs](https://lukasgeiter.github.io/mkdocs-awesome-nav/)
- [Configuration - MkDocs](https://www.mkdocs.org/user-guide/configuration/)

### PowerShell Best Practices
- [about_Requires - PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires?view=powershell-7.5)
- [Overview of the SecretManagement and SecretStore modules](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/overview?view=ps-modules)
- [Working with PowerShell Secret Management](https://www.techtarget.com/searchwindowsserver/tutorial/Working-with-PowerShell-Secret-Management-and-Secret-Vault)

### Power Platform Integration
- [Power BI modeling guidance for Power Platform](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-modeling-guidance-for-power-platform)
- [DirectQuery model guidance in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/guidance/directquery-model-guidance)
- [Manage cloud flow run history in Dataverse](https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata)
- [Monitor your flows - Power Automate](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/monitoring-and-alerting)

---

## Confidence Assessment

| Area | Confidence | Source Quality | Notes |
|------|------------|----------------|-------|
| MkDocs Breadcrumbs | HIGH | Official MkDocs Material docs | Feature well-documented, widely used |
| Awesome Pages | HIGH | Official plugin docs + examples | Coexistence pattern validated |
| YAML Configs | MEDIUM | MkDocs ecosystem patterns | No official schema yet, custom implementation |
| PowerShell #Requires | HIGH | Microsoft Learn official docs | Language feature, stable |
| SecretManagement | HIGH | Microsoft Learn + community guides | Module stable since v1.1.2 |
| Dataverse Schema | HIGH | Microsoft Learn guidance | Star schema is standard BI pattern |
| Power BI DirectQuery | HIGH | Microsoft Learn official guidance | DirectQuery best practices well-established |
| Power Automate Flows | MEDIUM | Microsoft Learn + community patterns | Flow patterns validated, specific flows need testing |
| Scope Drift Adapter | MEDIUM | Architectural pattern (not implemented) | Based on proven monitoring_shared.py design |

**Overall Confidence: HIGH** for documentation improvements, **MEDIUM-HIGH** for solutions completion.

---

*Research completed: 2026-02-04*
*Researcher: GSD Project Researcher (Claude Agent)*
*Review status: Ready for roadmap creation*
