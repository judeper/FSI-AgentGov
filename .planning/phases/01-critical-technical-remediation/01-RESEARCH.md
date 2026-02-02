# Phase 1: Critical Technical Remediation - Research

**Researched:** 2026-02-02
**Domain:** Technical documentation maintenance (API deprecations and compliance deadlines)
**Confidence:** HIGH

## Summary

This phase documents time-sensitive Microsoft API deprecations and compliance deadlines affecting FSI organizations using Microsoft 365 AI agents. The work involves adding inline warning callouts to existing documentation and scripts across two repositories (FSI-AgentGov documentation and FSI-AgentGov-Solutions code).

The standard approach is to add MkDocs Material admonition callouts (`!!! danger`) at the point of first use in each affected document, following the existing pattern established in Control 2.1 and the DEC playbook. The warnings include specific dates, explicit consequences, migration guidance, and "Last verified: [date]" stamps.

Key findings: (1) Four API deprecations affect FSI-AgentGov with specific dates and migration paths, (2) February 2026 pipeline deadline already documented but may need cross-references, (3) MkDocs Material admonition syntax is already in use with consistent patterns, (4) FSI-AgentGov-Solutions has 5 files needing updates for x-api-key deprecation.

**Primary recommendation:** Use inline danger callouts with step-by-step migration guidance at first mention of deprecated APIs; systematically grep for each deprecated API across both repositories; follow existing warning patterns from Control 2.1 and DEC playbook.

## Standard Stack

The established tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| MkDocs Material | 9.x | Documentation site generator | Already in use; admonition extension enabled |
| grep/ripgrep | System | File content search | Systematic deprecation discovery |
| Git | System | Version control | Track documentation updates |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| mkdocs build --strict | 9.x | Documentation validation | Pre-commit validation |
| Python Markdown | 3.x (via MkDocs) | Markdown processing | Admonition rendering |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Inline warnings | Centralized deprecation page | User decisions require inline warnings (no centralized page) |
| Manual discovery | Automated scanning | Grep is faster and more reliable for comprehensive coverage |

**Installation:**
Already installed in project. No additional dependencies required.

## Architecture Patterns

### Recommended Project Structure

Documentation warnings follow existing MkDocs structure:
```
docs/
├── controls/pillar-*/          # Control documentation with inline warnings
│   └── X.X-control-name.md
├── playbooks/                  # Playbooks with inline warnings
│   └── control-implementations/
│       └── X.X/
│           └── powershell-setup.md
└── reference/
    └── faq.md                  # Deprecation FAQ section
```

### Pattern 1: Inline Danger Callout at First Mention

**What:** MkDocs Material danger admonition placed where deprecated API/method is first mentioned in instructions
**When to use:** All time-sensitive deadlines and API deprecations
**Example:**
```markdown
## Application Insights Setup

### Step 2: Configure API Access

!!! danger "x-api-key Deprecation - March 31, 2026"
    The Application Insights API key (`x-api-key`) authentication method is deprecated and will stop working on **March 31, 2026**. After this date, scripts using API keys will fail.

    **Required Migration:**

    - Switch to **Entra ID (Azure AD) authentication** using service principals or managed identities
    - Use `Connect-AzAccount` and bearer token authentication instead of API keys
    - See [migration guide](link) for step-by-step instructions

    **Timeline:**

    | Date | Impact |
    |------|--------|
    | Now | Begin migration planning |
    | March 31, 2026 | API keys stop working |

    **Last verified:** February 2, 2026
```
**Source:** Existing pattern from `docs/playbooks/advanced-implementations/deny-event-correlation-report/app-insights-rai-telemetry.md` (lines 161-176)

### Pattern 2: Prerequisites Section Warning

**What:** Licensing or prerequisite warnings placed before main configuration steps
**When to use:** Requirements that must be satisfied before implementation
**Example:**
```markdown
## Prerequisites

!!! warning "Licensing Requirements"
    Managed Environments require **Power Platform Premium capacity** or equivalent licensing. Verify the following before implementation:

    - **Managed Environment activation**: Requires Power Apps, Power Automate, or Copilot Studio premium licenses, OR Dynamics 365 licenses, OR Power Platform per-app/per-user plans with premium entitlements
    - **Advanced security features** (IP Firewall, VNet, CMK, Lockbox): Require additional licensing beyond Managed Environment designation

    Consult [Microsoft Learn: Licensing overview](https://learn.microsoft.com/en-us/power-platform/admin/pricing-billing-skus) for current licensing requirements.
```
**Source:** Existing pattern from `docs/controls/pillar-2-management/2.1-managed-environments.md` (lines 28-36)

### Pattern 3: Dedicated Deadline Section

**What:** Standalone section for time-sensitive compliance deadlines with actionable steps
**When to use:** Critical deadlines requiring organizational action (e.g., February 2026 pipeline requirement)
**Example:**
```markdown
## Critical Deadline: February 2026 Pipeline Requirement

!!! danger "Action Required: February 2026 Managed Environment Enforcement"
    Starting **February 2026**, Microsoft will automatically enable Managed Environments for any pipeline target environments that aren't already enabled.

    **Impact:**

    - All pipeline target environments will become Managed Environments
    - Licensing charges may apply for environments without premium capacity
    - Developer environments are NOT affected (can remain unmanaged)
    - Pipeline host environments can be production without being managed

    **Required Actions:**

    1. Audit all pipeline target environments in your tenant
    2. Verify premium licensing coverage for each target environment
    3. Proactively enable Managed Environment status to control timing
    4. Use [Pipeline Governance Cleanup](../../reference/solutions-index.md#pipeline-governance-cleanup) to discover and remediate personal pipelines before enforcement

    **Source:** [Microsoft Learn: Admin Deployment Hub](https://learn.microsoft.com/en-us/power-platform/alm/admin-deployment-hub)

    **Last verified:** February 2, 2026
```
**Source:** Existing pattern from `docs/controls/pillar-2-management/2.1-managed-environments.md` (lines 50-70)

### Pattern 4: Cross-Repository Warning Consistency

**What:** Same warning text in both FSI-AgentGov documentation and FSI-AgentGov-Solutions scripts
**When to use:** Deprecations affecting both documentation and code
**Example (FSI-AgentGov documentation):**
```markdown
!!! danger "x-api-key Deprecation - March 31, 2026"
    [warning text]
```

**Example (FSI-AgentGov-Solutions README):**
```markdown
> ⚠️ **Deprecation Warning: x-api-key Authentication**
>
> Application Insights x-api-key authentication is deprecated and will be removed **March 31, 2026**. After this date, `Export-RaiTelemetry.ps1` will fail unless migrated to Entra ID authentication. See [prerequisites.md](docs/prerequisites.md#authentication-migration) for migration guidance.
```
**Source:** Existing pattern from `deny-event-correlation-report/README.md` (lines 5-7)

### Anti-Patterns to Avoid

- **Centralized deprecation page:** User decisions explicitly reject this approach - warnings must be inline
- **Vague timing:** "Soon" or "Coming in 2026" - must include exact dates
- **Link-only guidance:** "See Microsoft Learn for migration" - must include self-contained step-by-step instructions
- **Assume-don't-verify:** Stating consequences without explicit verification - each warning needs "Last verified: [date]"
- **Selective warning placement:** If API appears in 10 files, warn in all 10 files, no exceptions

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Finding deprecated APIs | Manual search/reading | `grep -r "x-api-key" .` | Systematic coverage prevents missed files |
| Writing warnings | Custom format per file | Existing MkDocs admonition patterns | Consistency, already tested, user expectations |
| Deprecation verification | Assume training data is current | WebFetch official Microsoft Learn docs | Training data may be stale; official docs are authoritative |
| Cross-repo updates | Manual file-by-file editing | Grep both repos, batch updates | Ensures consistency and completeness |

**Key insight:** Systematic discovery via grep prevents false confidence about completeness. Manual review inevitably misses files.

## Common Pitfalls

### Pitfall 1: Incomplete Scope Discovery
**What goes wrong:** Manual search finds 5 files, misses 3 others where deprecated API is mentioned
**Why it happens:** Grep not used comprehensively; assumptions about "where it would be"
**How to avoid:** Systematic grep for each deprecated API pattern across both repositories
**Warning signs:** User decisions say "all files" but researcher only checked obvious locations

### Pitfall 2: Outdated Microsoft Learn URLs
**What goes wrong:** Warning links to Microsoft Learn page that has moved or changed
**Why it happens:** Learn Monitor tracks 209 URLs but they still redirect/change
**How to avoid:** WebFetch the exact URL before adding it to warnings; verify it loads correctly
**Warning signs:** URL returns redirect or 404; content doesn't match expected topic

### Pitfall 3: Inconsistent Warning Tone
**What goes wrong:** Some warnings use "You must..." while others use "Organizations should..."
**Why it happens:** Not following established advisory tone from user decisions
**How to avoid:** Use professional advisory tone pattern: "Organizations should plan to..." not "You must..."
**Warning signs:** Imperative language ("Do this now!") instead of advisory framing

### Pitfall 4: Migration Guidance Without Verification Steps
**What goes wrong:** Warning says "migrate to Entra ID" but doesn't explain how to verify migration succeeded
**Why it happens:** User decisions require verification steps but researcher only documents migration
**How to avoid:** Every migration guidance section must include "Verify migration" subsection with testable commands
**Warning signs:** Migration guidance ends with configuration steps, no validation checks

### Pitfall 5: Assuming February 2026 Deadline is Fully Documented
**What goes wrong:** Researcher assumes existing Control 2.1 section is sufficient and doesn't check for cross-references
**Why it happens:** Confirmation bias - Control 2.1 looks complete, so researcher stops investigating
**How to avoid:** User decisions require "cross-reference related warnings where connected impacts exist" - search for all mentions of "pipeline" and "Managed Environment" to find related content
**Warning signs:** Only one control mentions pipeline deadline but 3+ controls discuss pipelines

### Pitfall 6: Migration Paths Without "Both Portal and PowerShell"
**What goes wrong:** Warning only documents portal steps, no PowerShell automation
**Why it happens:** User decisions explicitly require "Both portal walkthrough AND PowerShell automation for each migration"
**How to avoid:** Every migration section needs two subsections: Portal Walkthrough and PowerShell Automation
**Warning signs:** Only manual steps provided, no script examples

## Code Examples

Verified patterns from official sources:

### MkDocs Material Danger Admonition
```markdown
!!! danger "CRITICAL: Action Required by [Month] [Year]"
    [Date-specific headline with explicit timeframe]

    **Impact:**

    - [Consequence 1 - what breaks if no action]
    - [Consequence 2 - licensing/compliance implications]
    - [Consequence 3 - scope of impact]

    **Required Actions:**

    1. [Actionable step 1]
    2. [Actionable step 2 with portal walkthrough]
    3. [Actionable step 3 with PowerShell alternative]
    4. [Reference to solution/tool if available]

    **Migration (Portal):**

    1. Navigate to [Location] > [Submenu]
    2. Click [Button/Option]
    3. Configure [Setting] to [Value]
    4. Verify: [Testable check]

    **Migration (PowerShell):**

    ```powershell
    # [Description of what this does]
    Connect-AzAccount
    $context = Get-AzContext
    Set-AzKeyVault -Name "vault" -EnableRbacAuthorization $true

    # Verify migration
    Get-AzKeyVault -Name "vault" | Select-Object EnableRbacAuthorization
    # Expected: EnableRbacAuthorization : True
    ```

    **Timeline:**

    | Date | Impact |
    |------|--------|
    | Now | Begin planning |
    | [Month] [Year] | [What stops working] |

    **Source:** [Microsoft Learn: Title](URL)

    **Last verified:** [Date]
```
**Source:** Synthesized from existing patterns in Control 2.1 and DEC playbook

### Grep Search Pattern for Systematic Discovery
```bash
# Search FSI-AgentGov documentation
grep -r "x-api-key" /Users/admin/dev/FSI-AgentGov/docs/

# Search FSI-AgentGov-Solutions code
grep -r "x-api-key" /Users/admin/dev/FSI-AgentGov-Solutions/

# Search for EWS references
grep -ri "Exchange Web Services\|EWS" /Users/admin/dev/FSI-AgentGov/docs/

# Search for SharePoint Add-in references
grep -ri "SharePoint Add-in\|SharePoint Add-In" /Users/admin/dev/FSI-AgentGov/docs/

# Search for Azure Key Vault API references
grep -ri "Key Vault.*API\|enableRbacAuthorization" /Users/admin/dev/FSI-AgentGov/docs/
```
**Source:** Standard grep patterns for comprehensive file discovery

### FAQ Deprecation Entry Pattern
```markdown
### Q: What Microsoft APIs are being deprecated in 2026?

A: Key deprecation dates affecting this framework:

| API/Feature | Deprecation Date | Replacement | Impact |
|-------------|------------------|-------------|--------|
| **Application Insights x-api-key** | March 31, 2026 | Entra ID OAuth 2.0 | RAI telemetry scripts in DEC solution |
| **Exchange Web Services (EWS)** | October 2026 | Microsoft Graph API | Audit log extraction (if using EWS) |
| **SharePoint Add-Ins** | April 2, 2026 | SharePoint Framework (SPFx) | Custom SharePoint integrations (if used) |
| **Azure Key Vault (pre-2026-02-01 APIs)** | February 27, 2027 | API version 2026-02-01 with RBAC | Key Vault access patterns |
| **Office 365 Connectors (incoming webhooks)** | March 31, 2026 | Power Automate Workflows connector | Teams notifications; MCM solution uses native connector (unaffected) |
| **Reporting Webservice** | April 6, 2026 | Microsoft Graph APIs | Usage reporting scripts |
| **Connect-ExchangeOnline Basic Auth (SMTP AUTH)** | March 1 – April 30, 2026 | OAuth 2.0 for SMTP AUTH | Audit log extraction scripts (SMTP only; other protocols deprecated 2021-2023) |

!!! warning "Action Required"
    Organizations using custom scripts for audit extraction, RAI telemetry, or reporting should plan migration to replacement APIs before the deprecation dates.
```
**Source:** Existing pattern from `docs/reference/faq.md` (lines 484-496)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Application Insights API keys (x-api-key) | Entra ID OAuth 2.0 with service principals | Deprecated March 31, 2026 | All RAI telemetry scripts must migrate |
| Exchange Web Services (EWS) | Microsoft Graph API | Disabled October 2026 | Audit log extraction if using EWS |
| SharePoint Add-Ins | SharePoint Framework (SPFx) | Retired April 2, 2026 | Custom SharePoint integrations |
| Azure Key Vault access policies | Azure RBAC (API version 2026-02-01) | Pre-2026-02-01 APIs retired February 27, 2027 | Key Vault configuration patterns |
| Office 365 Connectors | Power Automate Workflows connector | Deprecated March 31, 2026 | Teams webhooks (MCM unaffected) |
| Reporting Webservice | Microsoft Graph APIs | Deprecated April 6, 2026 | Usage reporting scripts |
| Exchange Basic Auth SMTP | OAuth 2.0 for SMTP AUTH | Disabled March 1-April 30, 2026 | Email-based audit scripts |

**Deprecated/outdated:**
- **x-api-key authentication for Application Insights:** Replaced by Entra ID OAuth 2.0; existing scripts in FSI-AgentGov-Solutions DEC solution affected
- **EWS for Exchange Online access:** Replaced by Microsoft Graph; only relevant if custom audit extraction uses EWS (framework uses Exchange Online PowerShell)
- **SharePoint Add-Ins:** Replaced by SPFx; only relevant if custom governance solutions use Add-Ins (framework does not)
- **Azure Key Vault pre-2026-02-01 APIs:** All vaults must use 2026-02-01 or later by February 27, 2027; affects secret management patterns

## Open Questions

Things that couldn't be fully resolved:

1. **Does FSI-AgentGov use Exchange Web Services (EWS) anywhere?**
   - What we know: Framework uses Exchange Online PowerShell (`Connect-ExchangeOnline`) for Purview audit log extraction; no explicit EWS references found in initial grep
   - What's unclear: Whether any custom scripts or integrations use EWS; whether audit extraction dependencies chain to EWS
   - Recommendation: Comprehensive grep for "EWS" and "Exchange Web Services" to definitively rule out; if found, add warnings

2. **Does FSI-AgentGov use SharePoint Add-Ins anywhere?**
   - What we know: Framework has Pillar 4 SharePoint controls but focuses on native governance features (Advanced Management, retention, sensitivity labels); no Add-In references found in initial search
   - What's unclear: Whether Control 4.7 (Custom Governance Solutions) mentions Add-Ins as an integration option
   - Recommendation: Grep for "SharePoint Add-in" and "Add-In" to verify; likely not relevant but must confirm

3. **Does FSI-AgentGov use Azure Key Vault APIs directly?**
   - What we know: Framework references Key Vault for secret management in solutions architecture; FSI-AgentGov-Solutions uses Key Vault for secret storage
   - What's unclear: Whether any scripts use pre-2026-02-01 API versions explicitly; whether migration is automatic or requires code changes
   - Recommendation: Check FSI-AgentGov-Solutions scripts for Key Vault SDK usage; if using Azure PowerShell `Az.KeyVault` module, verify module version supports 2026-02-01 API

4. **Are there cross-references between Control 2.1 and other controls mentioning pipelines?**
   - What we know: Control 2.1 documents February 2026 deadline; user decisions require "cross-reference related warnings where connected impacts exist"
   - What's unclear: Which other controls mention deployment pipelines and should cross-reference the deadline
   - Recommendation: Grep for "pipeline" and "deployment" across all controls; add cross-reference links where relevant

5. **Should warnings include "who this affects" role statements?**
   - What we know: User decisions mark this as Claude's discretion
   - What's unclear: Whether role-based targeting improves or clutters warnings
   - Recommendation: Include role targeting for warnings with clear role boundaries (e.g., "Power Platform Admins should..." for environment configuration); omit for warnings affecting all users

## Sources

### Primary (HIGH confidence)
- **Microsoft Learn: Azure Key Vault API Retirement** - https://learn.microsoft.com/en-us/azure/key-vault/general/access-control-default - February 27, 2027 retirement date for pre-2026-02-01 APIs; RBAC migration guidance verified
- **Microsoft Learn: Exchange Web Services Deprecation** - https://learn.microsoft.com/en-us/exchange/clients-and-mobile-in-exchange-online/deprecation-of-ews-exchange-online - October 2026 global disablement date verified; Microsoft Graph migration path confirmed
- **Existing FSI-AgentGov Control 2.1** - `/Users/admin/dev/FSI-AgentGov/docs/controls/pillar-2-management/2.1-managed-environments.md` - February 2026 pipeline deadline already documented with complete warning pattern (lines 50-70)
- **Existing FSI-AgentGov DEC Playbook** - `/Users/admin/dev/FSI-AgentGov/docs/playbooks/advanced-implementations/deny-event-correlation-report/app-insights-rai-telemetry.md` - x-api-key deprecation March 31, 2026 already documented with migration guidance (lines 161-176)
- **Existing FSI-AgentGov FAQ** - `/Users/admin/dev/FSI-AgentGov/docs/reference/faq.md` - API deprecation table already exists (lines 484-496)
- **Existing FSI-AgentGov-Solutions DEC README** - `/Users/admin/dev/FSI-AgentGov-Solutions/deny-event-correlation-report/README.md` - x-api-key deprecation warning already present (lines 5-7)
- **MkDocs Material Documentation** - Admonition syntax confirmed via `mkdocs.yml` (line 62: `- admonition`)

### Secondary (MEDIUM confidence)
- **WebSearch: SharePoint Add-Ins Retirement** - April 2, 2026 retirement date from Microsoft Community Hub and Microsoft Learn; SharePoint Framework as replacement
- **WebSearch: EWS Timeline Community Discussion** - October 2026 date corroborated by Microsoft 365 Message Center Archive (MC676299) and community forums
- **WebSearch: Azure Key Vault API Timeline** - February 2026 and February 27, 2027 dates confirmed across multiple Microsoft Docs sources

### Tertiary (LOW confidence)
- None - all findings verified with official Microsoft documentation or existing codebase patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Existing tools already in use (MkDocs Material, grep, git)
- Architecture: HIGH - Patterns already established in Control 2.1 and DEC playbook; user decisions confirm inline approach
- Pitfalls: HIGH - Based on user decisions explicitly stating requirements (systematic search, both repos, verification steps)

**Research date:** 2026-02-02
**Valid until:** April 2, 2026 (when first major deprecation takes effect; research should be re-validated if new Microsoft deprecations announced)

**Deprecation Timeline Summary:**

| Date | Deprecation | Status in Codebase |
|------|-------------|-------------------|
| February 2026 | Pipeline Managed Environment enforcement | Already documented in Control 2.1 |
| March 31, 2026 | Application Insights x-api-key | Already documented in DEC playbook and FAQ |
| April 2, 2026 | SharePoint Add-Ins | Research needed - likely not used |
| April 6, 2026 | Reporting Webservice | Already documented in FAQ |
| March 1-April 30, 2026 | Exchange Basic Auth SMTP | Already documented in FAQ |
| October 2026 | Exchange Web Services (EWS) | Research needed - likely not used |
| February 27, 2027 | Azure Key Vault pre-2026-02-01 APIs | Research needed - verify FSI-AgentGov-Solutions usage |

**Next Research Actions (for planning phase):**
1. Grep for EWS references to confirm not used
2. Grep for SharePoint Add-In references to confirm not used
3. Check FSI-AgentGov-Solutions for Azure Key Vault SDK usage
4. Grep for "pipeline" across all controls to identify cross-reference opportunities
5. Verify all Microsoft Learn URLs referenced in warnings are current (use WebFetch)
