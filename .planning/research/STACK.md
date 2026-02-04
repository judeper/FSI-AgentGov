# Technology Stack - v2 Improvements

**Project:** FSI Agent Governance Framework
**Research Date:** 2026-02-04
**Scope:** Stack additions/changes for v2 milestone improvements

---

## Executive Summary

This research focuses on stack additions needed for v2 improvements to the existing FSI-AgentGov framework. The v2 milestone emphasizes **incremental improvements** to existing infrastructure rather than wholesale replacement. Key areas: MkDocs navigation enhancements, PowerShell security hardening, monitoring configuration externalization, and solution completion patterns.

**Recommendation:** Add selective plugins and modules to existing stack. **Do NOT** replace working foundation (MkDocs Material, Python validation scripts, PowerShell solutions).

---

## Stack Additions for v2

### 1. MkDocs Navigation Improvements

**Requirement:** Breadcrumb navigation, auto-generated navigation, playbook discovery

#### Recommended: Native MkDocs Material Features

| Feature | Version | Status | Why |
|---------|---------|--------|-----|
| `navigation.path` (breadcrumbs) | mkdocs-material 9.7.0+ | Built-in | Native feature, zero dependencies, now free (was Insiders) |
| mkdocs-material | 9.7.1 (latest) | Stable | Already in use, includes all former Insiders features |

**Configuration (breadcrumbs):**
```yaml
theme:
  name: material
  features:
    - navigation.path  # Breadcrumb navigation above page title
```

**Rationale:**
- MkDocs Material 9.7.0 (released Nov 11, 2025) made `navigation.path` free for everyone
- Zero additional dependencies
- Native integration with existing theme
- Lightweight, no plugin conflicts

**Source:** [MkDocs Material - Setting up navigation](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)

#### Alternative Considered: mkdocs-awesome-pages-plugin

| Library | Version | Purpose | Why NOT Using |
|---------|---------|---------|---------------|
| mkdocs-awesome-pages-plugin | 2.10.1 | Auto-generate navigation from directory structure | Requires manual `.pages` files, conflicts with existing mkdocs.yml nav structure |

**Reason to defer:**
- Current project has 62 controls with established manual nav structure in `mkdocs.yml` (lines 79-591)
- Plugin requires removing existing `nav:` entry or adding `...` placeholders
- Risk: Breaking existing navigation structure that's working
- Current manual nav provides explicit control over presentation order
- **v2 recommendation:** Use native `navigation.path` only, defer auto-generation to v3 if needed

**Source:** [mkdocs-awesome-pages-plugin on PyPI](https://pypi.org/project/mkdocs-awesome-pages-plugin/)

#### Playbook Discovery via Admonitions

**Requirement:** Help users discover playbooks from parent control pages

**Recommended Pattern:** Use existing MkDocs Material admonition syntax

```markdown
!!! info "Implementation Playbooks"
    See [Portal Walkthrough](../../playbooks/control-implementations/1.1/portal-walkthrough.md) for step-by-step portal configuration.
```

**No additional plugins needed.** MkDocs Material supports admonitions natively via `markdown_extensions: [admonition]` (already configured line 62 in mkdocs.yml).

**Rationale:**
- Zero dependencies (already configured)
- Existing project uses admonitions extensively
- Simple markdown syntax
- Integration: Add admonition blocks to control files pointing to their 4 playbooks

**Source:** [MkDocs Material - Admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)

---

### 2. PowerShell Security Best Practices (FSI)

**Requirement:** Secret management, error handling, #Requires statements for FSI PowerShell scripts

#### Recommended: PowerShell SecretManagement + Az.KeyVault

| Module | Version | Purpose | Why |
|--------|---------|---------|-----|
| Microsoft.PowerShell.SecretManagement | 1.1.2 | Unified secret management interface | Cross-platform, extensible, Microsoft-supported |
| Az.KeyVault | 3.3.0+ | Azure Key Vault integration | Includes SecretManagement extension, FSI-standard secret store |

**Installation:**
```powershell
# Core SecretManagement module
Install-Module Microsoft.PowerShell.SecretManagement -Scope CurrentUser

# Azure Key Vault module (3.3.0+ includes SecretManagement support)
Install-Module Az.KeyVault -Scope CurrentUser
```

**Registration Pattern (for FSI scripts):**
```powershell
# Register Azure Key Vault as secret vault
Register-SecretVault -Name "FSIAgentGov" -ModuleName Az.KeyVault -VaultParameters @{
    AZKVaultName = "your-keyvault-name"
    SubscriptionId = "your-subscription-id"
}

# Retrieve secrets in scripts
$credential = Get-Secret -Name "PowerPlatformServicePrincipal" -Vault "FSIAgentGov" -AsPlainText
```

**Rationale:**
- **FSI requirement:** Secrets must not be in scripts, environment variables insufficient for audit trails
- Azure Key Vault provides audit logging required for SOX 302/404, FINRA 4511
- SecretManagement abstraction allows swapping vault providers without script changes
- Az.KeyVault 3.3.0+ natively includes SecretManagement extension (no separate extension module)
- Cross-platform support for Windows/Linux/macOS

**Sources:**
- [PowerShell Gallery - SecretManagement 1.1.2](https://www.powershellgallery.com/packages/Microsoft.PowerShell.SecretManagement/1.1.2)
- [Microsoft Learn - Azure Key Vault automation](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/how-to/using-azure-keyvault)
- [Microsoft Learn - SecretManagement Overview](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/overview)

#### #Requires Statement Best Practices

**Pattern for FSI scripts:**
```powershell
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="Microsoft.PowerShell.SecretManagement"; ModuleVersion="1.1.2" }
#Requires -Modules @{ ModuleName="Az.KeyVault"; ModuleVersion="3.3.0" }
```

**Rationale:**
- Fail-fast validation prevents runtime errors in production
- PowerShell 7.0+ required for cross-platform support
- Module version enforcement prevents API compatibility issues
- #Requires statements are global scope, enforced before script execution

**Source:** [Microsoft Learn - about_Requires](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires)

#### Error Handling Pattern

**Recommended:**
```powershell
[CmdletBinding()]
param()

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
    # Script logic
}
catch {
    Write-Error "Operation failed: $_"
    throw  # Propagate for CI/CD detection
}
```

**Rationale:**
- `Set-StrictMode -Version Latest` catches uninitialized variables, undefined properties
- `$ErrorActionPreference = "Stop"` converts non-terminating errors to terminating (enables try/catch)
- Explicit error messages aid troubleshooting
- `throw` propagates errors for CI/CD pipeline failure detection

**Source:** [PowerShell Scripting Best Practices](https://dstreefkerk.github.io/2025-06-powershell-scripting-best-practices/)

---

### 3. Monitoring Configuration Externalization

**Requirement:** YAML externalization for monitoring adapter patterns

#### Recommended: YAML Configuration Files with PyYAML

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| PyYAML | 6.0+ | YAML parsing in Python | Industry standard, already suggested in requirements.txt |

**Pattern:**
```yaml
# config/monitoring-sources.yaml
sources:
  learn:
    enabled: true
    check_interval_hours: 24
    classification_patterns:
      critical:
        - "deprecated"
        - "breaking change"
      high:
        - "Admin center"
        - "compliance"

  regulatory-federal-register:
    enabled: true
    check_interval_hours: 168  # weekly
    agencies:
      - FINRA
      - SEC
      - OCC
```

**Integration with existing monitoring_shared.py:**
```python
import yaml
from pathlib import Path

def load_monitoring_config():
    """Load monitoring configuration from YAML."""
    config_path = Path(__file__).parent.parent / "config" / "monitoring-sources.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)
```

**Rationale:**
- Existing `monitoring_shared.py` (591 lines) uses hardcoded patterns for classification
- YAML externalization enables non-developers to adjust monitoring sensitivity
- Supports multiple source adapters (Learn, regulatory) with per-source configuration
- PyYAML already listed as optional dependency in `scripts/requirements.txt` line 12
- Maintains existing unified state management (data/monitor-state.json)

**What NOT to change:**
- Keep JSON for state files (`data/monitor-state.json`) - optimized for programmatic read/write
- YAML only for human-editable configuration, NOT state persistence

**Source:** [YAML Configuration Externalization](https://medium.com/@vinciabhinav7/configuration-externalization-design-pattern-an-overview-25a05680ca73)

---

### 4. State Management: SQLite vs JSON

**Requirement:** State persistence for ~200 monitored URLs

#### Recommended: KEEP JSON

**Decision:** Continue using JSON files for state management.

**Current implementation:**
- `data/monitor-state.json` - Unified state with source-keyed sections
- `monitoring_shared.py` provides atomic write with temp file + rename pattern (lines 415-450)

**Rationale:**
| Factor | JSON | SQLite | Winner |
|--------|------|--------|--------|
| **Scale** | 200 URLs, ~50KB file | Overkill for this size | JSON |
| **Performance** | Entire file read at startup (microseconds for 50KB) | Connection overhead | JSON |
| **Queries** | Linear scan sufficient | Indexed queries unnecessary | JSON |
| **Atomicity** | Temp file + rename (existing) | WAL mode, BEGIN/COMMIT | Equivalent |
| **Complexity** | Zero dependencies | sqlite3 module (stdlib) | JSON simpler |
| **Portability** | Human-readable, git-diffable | Binary format | JSON |

**When SQLite becomes necessary:**
- State file exceeds 1MB (~4000 URLs)
- Require historical change tracking (not current requirement)
- Need concurrent read/write from multiple processes

**Current v2 scope does NOT require SQLite.**

**Sources:**
- [SQLite vs JSON Forum Discussion](https://sqlite.org/forum/forumpost/3d7be1ad3d)
- [JSON vs SQLite Performance](https://news.ycombinator.com/item?id=2685131)

---

### 5. Power Platform Solution Completion Patterns

**Requirement:** Guidance for Compliance Dashboard and Scope Drift Monitor completion

#### Compliance Dashboard (Control 3.3)

**Recommended Stack:**

| Component | Technology | Why |
|-----------|------------|-----|
| Data Source | Power Platform CoE Starter Kit | Industry-standard governance data model |
| Dashboard | Power BI Desktop | Native integration with Dataverse |
| Deployment | Power BI Service | FSI tenant deployment model |

**Integration Pattern:**
```powershell
# Data extraction from CoE Starter Kit
Connect-PowerAppsAccount
$environments = Get-AdminPowerAppEnvironment
$apps = Get-AdminPowerApp

# Export to Dataverse table for Power BI
# Use CoE Starter Kit tables: admin_Environment, admin_App, admin_Flow
```

**Rationale:**
- CoE Starter Kit provides pre-built Dataverse schema for governance data
- Power BI desktop files (.pbix) deployable via Power BI Service
- FSI audit requirement: Power BI workspaces with AAD group-based access control
- Data refresh: Scheduled refresh via Power Platform connector (no secrets in .pbix)

**Source:** [Microsoft Learn - CoE Power BI Compliance Dashboard](https://learn.microsoft.com/en-us/power-platform/guidance/coe/power-bi-compliance)

#### Scope Drift Monitor (Control 1.14)

**Recommended Pattern:**

| Component | Technology | Why |
|-----------|------------|-----|
| Baseline Storage | Dataverse custom table | Audit trail, RBAC, versioning |
| Agent Metadata | Power Platform API via PowerShell | Runtime data access scope |
| Comparison Logic | Power Automate flow | Scheduled monitoring (daily) |

**Dataverse Table Schema:**
```
AgentBaseline {
    AgentId: string (primary key)
    BaselineDeclaredScope: string (JSON array of SharePoint sites)
    BaselineCreatedDate: datetime
    LastValidationDate: datetime
}

AgentScopeDriftEvent {
    AgentId: string (lookup to AgentBaseline)
    DetectedScope: string (JSON array)
    DriftType: OptionSet (Expansion, Reduction, Unauthorized)
    DetectedDate: datetime
    Severity: OptionSet (High, Medium, Low)
}
```

**Rationale:**
- Dataverse native audit logging meets FINRA 4511 requirements
- Agent identity (Agent 365 Entra ID) enables Microsoft Graph API queries for actual access
- Power Automate flow orchestrates daily validation without custom hosting
- Integration with existing Control 3.1 (Agent Inventory) via AgentId foreign key

**Source:** [Microsoft Power Platform Blog - Agent 365 Dataverse](https://www.microsoft.com/en-us/power-platform/blog/2025/06/16/data-agent-architecture-powered-by-microsoft-dataverse/)

---

## What NOT to Add

### Deferred to Future Versions

| Technology | Why Deferring |
|------------|---------------|
| mkdocs-awesome-pages-plugin | Conflicts with existing manual nav (62 controls), risky for v2 |
| SQLite | JSON sufficient for current scale (200 URLs) |
| Alternative Python validation frameworks | Existing verify_controls.py works, no need to replace |
| Container orchestration (Docker/K8s) | GitHub Pages deployment works, over-engineering |
| Alternative monitoring frameworks (Prometheus) | Unified monitoring system via monitoring_shared.py is appropriate for scope |

---

## Integration Points with Existing Stack

### MkDocs Material (Current: Base theme)

**Changes:**
- Add `navigation.path` feature flag to mkdocs.yml
- No version upgrade required (9.7.1 already latest)
- Zero plugin additions

**Integration:**
```yaml
# mkdocs.yml additions
theme:
  features:
    - navigation.path  # NEW: Breadcrumb navigation
    # Existing features preserved
    - navigation.instant
    - navigation.tracking
    - navigation.sections
```

### Python Scripts (Current: Standard library only)

**Changes:**
- Add PyYAML to requirements.txt (uncomment line 12)
- Add monitoring configuration loader to monitoring_shared.py
- No breaking changes to existing scripts

**Integration:**
```python
# monitoring_shared.py additions
import yaml

def load_classification_config():
    """Load classification patterns from YAML config."""
    # New function, existing classification logic remains backward compatible
```

### PowerShell Solutions (Current: Basic patterns)

**Changes:**
- Add #Requires statements to all scripts
- Add SecretManagement integration for credential management
- Add error handling template

**Integration:**
```powershell
# Template for FSI-AgentGov-Solutions scripts
#Requires -Version 7.0
#Requires -Modules Microsoft.PowerShell.SecretManagement

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Existing script logic wraps in try/catch
```

### GitHub Actions (Current: CI/CD for docs, Learn monitor)

**Changes:**
- Add PowerShell module installation step
- Add YAML validation step for monitoring configs
- No workflow restructuring

**Integration:**
```yaml
# .github/workflows/learn-monitor.yml additions
- name: Install Python Dependencies
  run: pip install -r scripts/requirements.txt  # Now includes PyYAML

- name: Validate Monitoring Config
  run: python scripts/validate_monitoring_config.py  # New validation script
```

---

## Installation Instructions

### For Documentation (MkDocs)

```bash
# No new packages required
# Just update mkdocs.yml configuration

# Verify current version
pip show mkdocs-material
# Expected: 9.7.1 or higher
```

### For Python Scripts

```bash
cd /Users/admin/dev/FSI-AgentGov

# Uncomment PyYAML in scripts/requirements.txt (line 12)
# Then install
pip install -r scripts/requirements.txt
```

### For PowerShell Solutions

```powershell
# Install SecretManagement
Install-Module Microsoft.PowerShell.SecretManagement -Scope CurrentUser -Force

# Install Azure Key Vault module (includes SecretManagement extension)
Install-Module Az.KeyVault -MinimumVersion 3.3.0 -Scope CurrentUser -Force

# Verify installation
Get-Module -ListAvailable Microsoft.PowerShell.SecretManagement
Get-Module -ListAvailable Az.KeyVault
```

---

## Version Pinning Recommendations

| Package | Minimum Version | Maximum Version | Rationale |
|---------|-----------------|-----------------|-----------|
| mkdocs-material | 9.7.0 | 9.7.x | Last feature release, includes navigation.path |
| PyYAML | 6.0 | 6.x | Stable API, semantic versioning |
| Microsoft.PowerShell.SecretManagement | 1.1.2 | 1.x | Current stable, minor updates safe |
| Az.KeyVault | 3.3.0 | 4.x | Includes SecretManagement extension |

**Pin strategy:**
- MkDocs Material: Pin to 9.7.x (team shifting to Zensical, no new features)
- Python packages: Allow minor updates (6.0 → 6.x) for security patches
- PowerShell modules: Allow major updates (1.x, 4.x) - Microsoft backward compatibility guarantee

---

## Security Considerations

### Secret Management (PowerShell)

**FSI Requirements:**
- Secrets stored in Azure Key Vault (not local SecretStore)
- Key Vault access logged via Azure Monitor
- Service principal authentication with certificate (not password)
- Key rotation every 90 days (automated via Key Vault)

**Implementation:**
```powershell
# Register vault with service principal auth
$tenantId = "your-tenant-id"
$appId = "your-app-id"
$certThumbprint = "your-cert-thumbprint"

Connect-AzAccount -ServicePrincipal -TenantId $tenantId -ApplicationId $appId -CertificateThumbprint $certThumbprint

Register-SecretVault -Name "FSIAgentGovProd" -ModuleName Az.KeyVault -VaultParameters @{
    AZKVaultName = "fsi-agentgov-prod-kv"
    SubscriptionId = "your-subscription-id"
}
```

**Audit Trail:**
- Key Vault logs all secret access via Diagnostic Settings → Log Analytics
- Meets FINRA 4511 / SEC 17a-4 requirements for audit trails

### Configuration Files (YAML)

**Security:**
- YAML files contain classification patterns ONLY (no secrets)
- Store in repository (version controlled)
- No encryption required

**Anti-pattern:**
- DO NOT store secrets in YAML (use Key Vault instead)

---

## Confidence Assessment

| Area | Confidence | Source Quality | Notes |
|------|------------|----------------|-------|
| MkDocs Material navigation | **HIGH** | Official docs, PyPI | navigation.path verified in official docs, version 9.7.1 confirmed on PyPI |
| PowerShell SecretManagement | **HIGH** | Microsoft Learn, PowerShell Gallery | Version 1.1.2 verified on PowerShell Gallery, Az.KeyVault 3.3.0+ confirmed |
| YAML externalization | **MEDIUM** | WebSearch + existing code review | Pattern well-established, PyYAML already in requirements.txt |
| JSON vs SQLite | **HIGH** | SQLite forum, technical analysis | Scale analysis clear: 200 URLs = JSON sufficient |
| Power Platform patterns | **MEDIUM** | Microsoft Learn, recent blogs | CoE Starter Kit patterns verified, Agent 365 Dataverse architecture recent (2025-2026) |

**Overall Confidence: HIGH** - Core recommendations (MkDocs, PowerShell, JSON) verified with official sources. Power Platform patterns at MEDIUM confidence due to rapidly evolving Agent 365 capabilities.

---

## Open Questions / Validation Needed

1. **MkDocs navigation.path UX:** Test breadcrumbs on mobile/tablet to confirm usability improvement
2. **PyYAML performance:** Benchmark YAML load time vs hardcoded patterns (expect negligible difference)
3. **SecretManagement in GitHub Actions:** Verify service principal authentication pattern for CI/CD pipelines
4. **Agent 365 Entra ID availability:** Confirm Agent 365 Entra ID feature GA (currently rolling out per Jan 2026 blog post)

---

## Sources

**MkDocs Material:**
- [Setting up navigation](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- [Admonitions reference](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)
- [mkdocs-material on PyPI](https://pypi.org/project/mkdocs-material/)
- [Insiders now free announcement](https://squidfunk.github.io/mkdocs-material/blog/2025/11/11/insiders-now-free-for-everyone/)

**MkDocs Plugins:**
- [mkdocs-awesome-pages-plugin on PyPI](https://pypi.org/project/mkdocs-awesome-pages-plugin/)

**PowerShell SecretManagement:**
- [SecretManagement overview](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/overview)
- [Azure Key Vault automation](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/how-to/using-azure-keyvault)
- [PowerShell Gallery - SecretManagement 1.1.2](https://www.powershellgallery.com/packages/Microsoft.PowerShell.SecretManagement/1.1.2)
- [PowerShell Scripting Best Practices](https://dstreefkerk.github.io/2025-06-powershell-scripting-best-practices/)
- [about_Requires](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires)

**Configuration Externalization:**
- [Configuration Externalization Pattern](https://medium.com/@vinciabhinav7/configuration-externalization-design-pattern-an-overview-25a05680ca73)
- [YAML Best Practices](https://medium.com/@lingeshcbz/yaml-the-ultimate-guide-with-examples-and-best-practices-7040f9e389ed)

**State Management:**
- [SQLite vs JSON Discussion](https://sqlite.org/forum/forumpost/3d7be1ad3d)
- [When JSON Sucks article](https://pl-rants.net/posts/when-not-json/)

**Power Platform:**
- [CoE Power BI Compliance Dashboard](https://learn.microsoft.com/en-us/power-platform/guidance/coe/power-bi-compliance)
- [Data Agent Architecture with Dataverse](https://www.microsoft.com/en-us/power-platform/blog/2025/06/16/data-agent-architecture-powered-by-microsoft-dataverse/)
- [Agent 365 and Work IQ](https://www.microsoft.com/en-us/power-platform/blog/2026/01/27/build-adaptive-intelligence/)

---

## Appendix: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-04 | Initial research for v2 milestone improvements |
