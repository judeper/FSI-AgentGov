# Phase 4: Feature Enhancement Updates - Research

**Researched:** 2026-02-03
**Domain:** Microsoft 365 Copilot / Power Platform governance features (2025-2026 releases)
**Confidence:** HIGH

## Summary

Phase 4 involves updating existing framework controls with GA and preview governance features released in 2025-2026. The phase focuses on five specific requirements: virtual connectors DLP (Control 1.5), DSPM/AI observability (Control 1.6), AI Feature Access Control (Control 3.8), Defender for Power Platform verification and expansion (FEAT-06), and role catalog updates (FEAT-07).

Research confirms all five features exist and are documented in Microsoft Learn. The domain is well-established with official Microsoft documentation, though some features remain in preview status requiring appropriate flagging. The standard approach is inline documentation updates within existing control structures, maintaining the three-layer architecture (Framework → Controls → Playbooks).

**Primary recommendation:** Use inline integration with preview admonitions for all updates. Feature tables should follow a standardized format (Feature | Status | Description | Configuration) and be integrated into existing control sections rather than creating new standalone sections.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Microsoft Learn Documentation | Current (2026) | Official feature documentation | Authoritative source for all Microsoft 365/Power Platform features |
| Power Platform Admin Center (PPAC) | Cloud-based | DLP and governance configuration | Primary admin interface for virtual connectors and threat detection |
| Microsoft Purview Compliance Portal | Cloud-based | DSPM for AI, DLP policies | Central hub for data security posture management |
| Microsoft 365 Admin Center | Cloud-based | Copilot Hub, feature access control | Primary interface for M365 Copilot governance |
| Microsoft Defender Portal | Cloud-based | Defender for Cloud Apps integration | Security operations and threat detection |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PowerShell for Microsoft 365 | Current | Automation scripts | Bulk configuration, verification testing |
| Microsoft Graph API | v1.0 | Programmatic access | Custom reporting, automation scenarios |
| KQL (Kusto Query Language) | N/A | Advanced hunting, log analysis | Defender XDR queries, Application Insights |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Inline documentation | New control documents | Would violate user decision to enhance existing controls, not create new ones |
| Preview admonitions | "New" badges | Preview admonitions are established pattern from Phase 3 (Agent 365 strategic architecture) |
| Separate Defender mapping table | Inline capabilities | User decision: no separate table, merge capabilities seamlessly |

**Installation:**
Not applicable — all capabilities are cloud-based admin portal features. No local installation required.

## Architecture Patterns

### Recommended Documentation Structure

Controls → Sections → Feature Tables → Implementation Guides

```
docs/controls/pillar-X-name/
├── X.X-control-name.md         # Control document with feature tables
└── ...

docs/playbooks/control-implementations/X.X/
├── portal-walkthrough.md       # Updated with new feature steps
├── powershell-setup.md        # Updated with new automation scripts
├── verification-testing.md    # Updated with new test cases
└── troubleshooting.md         # Updated with new issue resolutions
```

### Pattern 1: Virtual Connectors Table (Control 1.5)

**What:** Inline integration into existing DLP section, not a new subsection

**When to use:** When adding feature-level capabilities that extend existing controls

**Example:**

```markdown
### Copilot Studio DLP Connector Categories

DLP policies can control the following connector categories for Copilot Studio agents:

| Category | Connectors | FSI Governance Notes |
|----------|-----------|---------------------|
| **Knowledge Sources** | SharePoint, OneDrive, Dataverse, Public websites, Uploaded documents | Zone 3: Restrict to approved SharePoint sites only |
| **Channels** | Microsoft Teams, Direct Line, Facebook, SharePoint, WhatsApp | Zone 2-3: Block social media channels (Facebook, WhatsApp) |
| **Actions** | HTTP with Microsoft Entra, HTTP webhook, Premium connectors | Zone 3: Require connector-level approval |
| **AI Services** | Azure OpenAI, AI Builder | Apply tenant-wide policies |
```

**Source:** Confirmed pattern from Control 1.5 (lines 66-73)

### Pattern 2: Preview Feature Documentation (DSPM, Defender)

**What:** Preview features wrapped in admonition blocks, full implementation detail provided

**When to use:** For all features requiring Frontier Program enrollment or in Public Preview

**Example:**

```markdown
!!! warning "Preview — Requires Frontier Program"
    [Feature name] is in preview as of [month year]. Feature availability and functionality may change before general availability.

[Full feature documentation including portal walkthroughs, PowerShell, verification]
```

**Source:** Phase 3 Agent 365 pattern (Control 1.5 lines 89-109, Control 3.8 lines 16-28)

### Pattern 3: Standardized Feature Table Format

**What:** Consistent table structure across all phase updates

**When to use:** When documenting multiple related features (virtual connectors, Defender capabilities, etc.)

**Example:**

```markdown
| Feature | Status | Description | Configuration |
|---------|--------|-------------|---------------|
| [Name] | GA/Preview | [What it does] | [Where to configure] |
```

**Source:** User decision from CONTEXT.md

### Pattern 4: Role Catalog Permission Matrix

**What:** Permission comparison table for new AI Administrator and Defender XDR Administrator roles

**When to use:** When adding roles with overlapping capabilities that need differentiation

**Example:**

```markdown
| Permission | AI Administrator | Global Admin | Security Admin |
|------------|------------------|--------------|----------------|
| Manage Copilot connectors | ✓ | ✓ | ✗ |
| Register Entra apps | ✓ (delegated) | ✓ | ✗ |
| Consent to Graph API | Limited scope | Full | ✗ |
| View usage reports | ✓ | ✓ | ✗ |
```

**FSI Guidance Example:**
"For FINRA-regulated firms, prefer AI Administrator over Global Admin for agent governance to enforce least-privilege access."

**Source:** User decision from CONTEXT.md, WebFetch results from Microsoft Learn

### Anti-Patterns to Avoid

- **Creating New Standalone Sections:** Virtual connectors should NOT get "### Virtual Connectors DLP" subsection — integrate into existing DLP section
- **Separate Defender Mapping Tables:** User explicitly rejected this — capabilities must be documented inline within each control
- **New/Enhancement Badges:** When preview features reach GA, remove admonition only — no "New" badge or transition marker
- **Treating Security Previews Differently:** User decision: same preview treatment for all features including Defender security capabilities

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Virtual connector enumeration | Manual list from portal | Microsoft Learn DLP documentation | 11 connectors officially documented, avoids missing new connectors |
| DSPM risk assessment schedules | Custom PowerShell scripts | Built-in weekly automation | Microsoft already runs weekly for top 100 SharePoint sites |
| AI Administrator permissions | Custom role definitions | Entra built-in AI Administrator role | Microsoft maintains canonical permissions, auto-updated |
| Defender XDR integration | Custom webhook API | Native Defender for Cloud Apps toggle | Microsoft provides two-portal integration (Defender + PPAC) |
| Feature status tracking | Manual documentation updates | Microsoft Learn URLs monitor | Framework already has learn_monitor.py (209 URLs) |

**Key insight:** Microsoft is rapidly iterating on AI governance features. Framework should reference authoritative sources (Microsoft Learn) rather than duplicating feature details that may change monthly. Tables should be high-level governance mappings, not comprehensive feature enumerations.

## Common Pitfalls

### Pitfall 1: Preview Feature Documentation Depth

**What goes wrong:** Documentation authors provide shallow coverage for preview features, deferring detail until GA.

**Why it happens:** Assumption that preview features will change significantly before GA, making detailed documentation "wasted effort."

**How to avoid:** User explicitly decided preview features receive full implementation detail — portal walkthroughs, PowerShell, verification — same depth as GA content. When feature reaches GA, simply remove admonition.

**Warning signs:** Playbook gaps for preview features, placeholder sections, "TBD" markers.

### Pitfall 2: Creating Visible Seams Between Old and New Content

**What goes wrong:** New Defender capabilities documented in a "New Features" section separate from existing Defender content.

**Why it happens:** Easier to add new sections than refactor existing content for seamless integration.

**How to avoid:** User decision: "New Defender content merged seamlessly into existing Defender sections — no visible seams between old and new content." Requires reading existing control content and identifying natural integration points.

**Warning signs:** Headings like "### New Capabilities" or "### 2026 Updates" that create temporal boundaries.

### Pitfall 3: Alternative Exploration for Locked Decisions

**What goes wrong:** Researcher investigates multiple approaches when user already decided on one.

**Why it happens:** Natural research instinct to explore options, not recognizing CONTEXT.md decisions are locked.

**How to avoid:** CONTEXT.md "Decisions" section = locked choices. Research THESE deeply, don't explore alternatives. Example: User decided "inline integration" for virtual connectors — don't research standalone section approaches.

**Warning signs:** Research report sections comparing multiple architecture approaches when user already chose one.

### Pitfall 4: Role Catalog Additions Without Least-Privilege Guidance

**What goes wrong:** New roles added to catalog without FSI-specific guidance on when to use them vs. existing roles.

**Why it happens:** Assumption that role descriptions from Microsoft Learn are sufficient.

**How to avoid:** User decision: "Permission matrix table format: key permissions per role with checkmarks showing what each role can/cannot do" PLUS "FSI-specific least-privilege role assignment guidance included."

**Warning signs:** Role catalog entries without comparison tables or "prefer X over Y for Z scenario" guidance.

### Pitfall 5: Assuming "Feature Access Control" is a Discrete Feature

**What goes wrong:** Searching for a specific "AI Feature Access Control" product when it's actually a collection of capabilities.

**Why it happens:** Requirement name sounds like a discrete feature rather than a governance capability area.

**How to avoid:** WebSearch results show "feature access control" refers to admin controls for Copilot deployment (license-based restrictions, admin exclusions, pinning controls). Not a single product but a governance pattern across M365 Admin Center.

**Warning signs:** Inability to find dedicated Microsoft Learn article titled "AI Feature Access Control."

## Code Examples

Verified patterns from official sources:

### Virtual Connectors DLP Classification (Control 1.5)

```markdown
### Copilot Studio DLP Connector Categories

DLP policies can control the following connector categories for Copilot Studio agents:

| Category | Connectors | FSI Governance Notes |
|----------|-----------|---------------------|
| **Knowledge Sources** | SharePoint, OneDrive, Dataverse, Public websites, Uploaded documents | Zone 3: Restrict to approved SharePoint sites only |
| **Channels** | Microsoft Teams, Direct Line, Facebook, SharePoint, WhatsApp | Zone 2-3: Block social media channels |
| **Actions** | HTTP with Microsoft Entra, HTTP webhook, Premium connectors | Zone 3: Require connector-level approval |
| **AI Services** | Azure OpenAI, AI Builder | Apply tenant-wide policies |
```

**Source:** Framework pattern established in Control 1.5, extended with 11 virtual governance connectors from [Microsoft Learn - Configure data policies for agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention)

### DSPM Weekly Risk Assessment Documentation (Control 1.6)

```markdown
### Weekly Risk Assessments

**Default Assessment:**
- Automatically runs **weekly** for the top 100 SharePoint sites based on usage
- **Initial delay**: 4 days before first results display
- **Wait time for updates**: At least 48 hours after assessment completion before results refresh

**Metrics & Dashboards Available:**

| Tab | Metrics |
|-----|---------|
| **Overview** | Summary insights per site/workspace |
| **Identify** | Data scanned vs. not scanned for sensitive information types |
| **Protect** | Oversharing remediation options |
| **Monitor** | Sharing breakdown: specific people, external, organization-wide, group-based access |
```

**Source:** [Microsoft Learn - DSPM for AI](https://learn.microsoft.com/en-us/purview/dspm-for-ai)

### AI Administrator Role Permissions (Role Catalog)

```markdown
### Entra (Identity)

| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **AI Administrator** | Manage M365 Copilot and AI-related enterprise services | Microsoft 365 AI Administrator |
| **Entra Global Admin** | Tenant-wide configuration and access | Global Administrator, Global Admin |
```

**Permission Matrix:**

| Permission | AI Administrator | Global Admin | Security Admin |
|------------|------------------|--------------|----------------|
| Manage Copilot connectors | ✓ | ✓ | ✗ |
| Register Entra apps | ✓ (delegated)* | ✓ | ✗ |
| Consent to ExternalItem.* APIs | ✓ | ✓ | ✗ |
| Consent to all Graph APIs | ✗ | ✓ | ✗ |
| View usage reports | ✓ | ✓ | ✗ |
| Create support tickets | ✓ | ✓ | ✗ |

*Requires delegation via custom role for app registration and limited API consent scope.

**FSI Least-Privilege Guidance:**
- **For agent governance:** Prefer AI Administrator over Global Admin to enforce least-privilege access
- **For Copilot connector management:** AI Administrator sufficient for most tasks
- **When Global Admin is required:** Initial tenant setup, broad Graph API consent beyond ExternalItem/ExternalConnection scope
```

**Source:** [Microsoft Learn - Microsoft Entra built-in roles](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference), [Microsoft Learn - Grant administrative rights to AI Administrators](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/connector-admin-delegation)

### Defender XDR Administrator Role Status

**Finding:** No dedicated "Defender XDR Administrator" built-in role exists in Microsoft Entra.

**Recommended Approach:**
- Use **Security Administrator** for Defender XDR access
- Use **Global Administrator** or **Security Administrator** for unified RBAC management
- Document as "Defender XDR Admin" informally refers to Security Admin with Defender permissions

**Alternative:** Create custom role via Defender XDR Unified RBAC with specific permissions.

**Role Catalog Entry:**
```markdown
| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **Entra Security Admin** | Security configuration, policy, Defender XDR access | Security Administrator, Defender XDR Admin (informal) |
```

**Source:** [Microsoft Learn - Manage access to Microsoft Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/m365d-permissions)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual DLP connector selection | Virtual governance connectors for Copilot Studio | February 2025 | 11 Copilot-specific connectors now enforceable via DLP policies |
| Manual oversharing assessments | Automatic weekly DSPM risk assessments | GA 2024 (enhanced 2025) | Top 100 SharePoint sites scanned weekly by default, no manual trigger |
| License-only Copilot access control | Admin-controlled deployment with exclusions | 2025-2026 rollout | Granular user/group controls, admin exclusion groups |
| Third-party webhook only | Native Defender for Cloud Apps integration | GA February 2026 | AI agent inventory, activity logging, real-time protection via Defender portal |
| DSPM for AI (standalone) | Unified DSPM experience | June 2026 (planned) | Consolidation of DSPM and DSPM for AI into single Purview experience |

**Deprecated/outdated:**
- **Standalone "Defender XDR Administrator" role:** Never existed as built-in Entra role; Security Administrator provides Defender XDR access
- **Manual weekly risk assessments:** Now automated via DSPM Default Assessment
- **DLP policies without virtual connectors:** Pre-2025 approach; current standard is 11 virtual governance connectors

## Open Questions

Things that couldn't be fully resolved:

1. **AI Feature Access Control as Discrete Feature**
   - What we know: M365 Admin Center provides license-based restrictions, admin exclusions, pinning controls, deployment groups
   - What's unclear: No discrete "AI Feature Access Control" product or portal section exists — it's a governance pattern across multiple admin controls
   - Recommendation: Document as enhancement to Control 3.8 (Copilot Hub) focusing on admin controls for user-level feature restrictions, not a standalone capability

2. **Defender for Power Platform Scope vs. Defender for Cloud Apps**
   - What we know: Control 1.8 documents "Defender for Cloud Apps integration" providing Copilot Studio agent protection
   - What's unclear: Whether "Defender for Power Platform" is distinct product or marketing term for Defender for Cloud Apps capabilities applied to Power Platform workloads
   - Recommendation: Verify existing Control 1.8 documentation accuracy (FEAT-06), expand with new capabilities discovered during verification, use "Defender for Cloud Apps - Copilot Studio AI Agents" as canonical term

3. **Role Catalog Updates Timeline**
   - What we know: AI Administrator is established Entra built-in role; "Defender XDR Administrator" doesn't exist as built-in role
   - What's unclear: Whether to add informal "Defender XDR Admin" term to role catalog or only document Security Administrator
   - Recommendation: Add AI Administrator as standalone entry; document "Defender XDR Admin" as accepted alias for Security Administrator in existing entry

4. **Preview Feature GA Timeline**
   - What we know: Several features remain in preview (Defender agent protection, DSPM unified experience June 2026)
   - What's unclear: Which preview features will reach GA during Phase 4 implementation period
   - Recommendation: Document all features with current status (GA/Preview), rely on learn_monitor.py to detect status changes via Microsoft Learn documentation updates

## Sources

### Primary (HIGH confidence)

- [Microsoft Learn: Configure data policies for agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention) - Virtual governance connectors enumeration
- [Microsoft Learn: DSPM for AI](https://learn.microsoft.com/en-us/purview/dspm-for-ai) - Weekly risk assessments, observability capabilities
- [Microsoft Learn: Microsoft Entra built-in roles](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference) - AI Administrator role permissions
- [Microsoft Learn: Grant administrative rights to AI Administrators](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/connector-admin-delegation) - AI Administrator delegation and limitations
- [Microsoft Learn: Manage access to Microsoft Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/m365d-permissions) - Defender XDR role clarification
- [Microsoft Learn: Protect your Microsoft Copilot Studio AI agents (Preview)](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection) - Defender for Cloud Apps agent protection
- [Microsoft Learn: Manage Microsoft 365 Copilot Chat](https://learn.microsoft.com/en-us/copilot/manage) - Feature access control capabilities

### Secondary (MEDIUM confidence)

- [Microsoft Security Blog: From runtime risk to real‑time defense: Securing AI agents](https://www.microsoft.com/en-us/security/blog/2026/01/23/runtime-risk-realtime-defense-securing-ai-agents/) - Defender agent protection architecture
- [Microsoft Community Hub: How to use DSPM for AI Data Risk Assessment](https://techcommunity.microsoft.com/blog/microsoft-security-blog/how-to-use-dspm-for-ai-data-risk-assessment-to-address-internal-oversharing/4399785) - DSPM implementation guidance
- [Microsoft Power Platform Blog: Announcing major DLP enhancements](https://www.microsoft.com/en-us/power-platform/blog/power-automate/announcing-major-dlp-enhancements-for-power-automate-and-copilot-studio/) - Virtual connectors announcement

### Tertiary (LOW confidence)

- WebSearch results for "AI Feature Access Control" - Generic access control guidance, no discrete feature product confirmed
- Community blog posts about AI Administrator role - Supplementary to official Microsoft Learn documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All capabilities are documented in official Microsoft Learn, existing framework controls confirmed
- Architecture: HIGH - Inline integration pattern established in Phase 3 (Agent 365), user decisions lock approach
- Pitfalls: MEDIUM - Based on framework patterns and user decisions, not comprehensive field testing

**Research date:** 2026-02-03
**Valid until:** 2026-03-03 (30 days for stable documentation domain; Microsoft Learn monitor provides ongoing validation)

**Key validation mechanisms:**
- Framework already monitors 209 Microsoft Learn URLs via learn_monitor.py
- Control 1.5, 1.6, 1.8, 3.8 existing documentation provides baseline for updates
- User decisions in CONTEXT.md constrain architecture choices, reducing risk of incorrect approach
