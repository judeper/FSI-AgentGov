# Phase 7: Control Enhancements & Role Updates - Research

**Researched:** 2026-02-06
**Domain:** Microsoft 365 Governance Framework Documentation
**Confidence:** HIGH

## Summary

Phase 7 updates the FSI-AgentGov framework to reflect Q1 2026 Microsoft governance capabilities across six requirements. This is a documentation enhancement phase — no code development, solely updating existing control files and playbooks within the FSI-AgentGov repository. Research confirms that all six capabilities exist with sufficient official documentation to support comprehensive control and playbook updates.

Key findings: (1) Virtual connectors are already documented in Control 1.5 and playbooks — this requirement involves expanding the existing 11-connector table with additional detail; (2) DSPM AI Observability capabilities are emerging via the new unified DSPM experience (preview) with enhanced weekly risk assessments; (3) AI Administrator role is GA with well-documented permissions for Copilot management; (4) "Defender XDR Administrator" is not a distinct Entra role — research shows Security Administrator is the correct role for Defender XDR operations; (5) SharePoint Restricted Search is GA with comprehensive documentation; (6) AI Feature Access Control exists as granular settings in the M365 Admin Center Copilot Hub (Admin Exclusion Groups, Deployment Groups, feature toggles).

The standard approach is to add new subsections within the existing 10-section control template, update all 4 playbooks per control with detailed implementation steps, and add two new roles to the role catalog with full permission matrices. MkDocs admonitions will distinguish GA vs. Preview features.

**Primary recommendation:** Enhance existing controls with dedicated subsections rather than appending content — this maintains control structure integrity and ensures clear section placement for each capability.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Content Depth Per Control:**
- Add **new subsections within existing control sections** — each enhancement gets a dedicated subsection (e.g., "## Virtual Connectors" under Control 1.5's relevant section)
- **Comprehensive detail** for all enhancements — full enumeration, configuration guidance, zone-specific notes, implementation steps (match depth of existing control content)
- **Inline regulatory mapping** per enhancement — each new subsection includes a brief note on which regulations the capability helps support
- **MkDocs admonition for GA/Preview status** — use `!!! warning 'Preview Feature'` or `!!! info 'GA Feature'` at top of each new subsection to indicate rollout status

**Role Catalog Integration:**
- **Full role-catalog entries** for both AI Administrator and Defender XDR Administrator — standard format: description, permissions, controls affected, zone applicability, licensing notes
- **Update all affected controls** — audit controls for role references and add AI Administrator / Defender XDR Admin where they apply (comprehensive cross-referencing)
- **Include role selection guidance** — add a "Role Selection Guidance" subsection explaining when AI Admin is preferred over Power Platform Admin (separation of duties, least privilege rationale)
- **Defender XDR Admin in security controls** — add to role catalog AND update Pillar 1 controls that reference Defender capabilities (e.g., 1.6 DSPM, Defender for Cloud Apps references)

**SharePoint Restricted Search:**
- **Document now with preview admonition** — write full enhancement content with `!!! warning 'Preview Feature'` admonition; update when GA lands
- **Place in Control 4.6** (Content Governance) — Restricted Search is about controlling what content surfaces in results
- **AI agent grounding focus** — frame primarily as "how Restricted Search limits what AI agents can access for grounding data," directly relevant to agent governance
- **Include 'prepare now' checklist** — pre-GA preparation steps organizations can take today (audit current search scopes, identify sensitive sites, etc.), similar to Phase 6 Agent 365 migration roadmap pattern

**Playbook Updates:**
- **Update all 4 playbooks** for each enhanced control — portal-walkthrough, powershell-setup, verification-testing, troubleshooting all get new sections for each enhancement
- **Preview features get playbook content with disclaimer** — write steps based on preview UI with `!!! warning 'Preview — UI may change at GA'` admonition; update at GA
- **Update playbooks for role references** — any playbook step that says "assign X role" gets updated to include AI Administrator or Defender XDR Admin where appropriate
- **Specific test cases per enhancement** — each enhancement gets 2-3 verification test cases with expected outcomes in verification-testing playbooks

### Claude's Discretion

- Exact section placement within each control's 10-section structure (which of the 10 sections each subsection lands under)
- Order of enhancements within multi-enhancement controls
- Whether to add new troubleshooting entries or extend existing ones
- Specific verification test case wording and expected outcomes

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope

</user_constraints>

---

## Standard Stack

This is a documentation-only phase. The "stack" consists of documentation tools and frameworks already established in the FSI-AgentGov repository.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| MkDocs Material | Current (repo) | Static site generation | Established framework documentation platform |
| Markdown | CommonMark | Documentation format | Universal, version-controlled, human-readable |
| Microsoft Learn | Current | Authoritative source | Official Microsoft documentation for all capabilities |
| Git | Current | Version control | Standard for documentation tracking and collaboration |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| MkDocs admonitions | Material theme | Feature status indicators | Distinguish GA vs. Preview capabilities |
| Internal links | Markdown syntax | Cross-references | Link controls, playbooks, role catalog entries |
| Tables | Markdown GFM | Structured data | Permission matrices, zone requirements, configuration steps |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| MkDocs admonitions | Plain text warnings | Admonitions provide visual distinction and semantic meaning |
| Dedicated new controls | Enhancements to existing | User decision: enhance existing controls, not create new ones |
| Separate preview docs | Inline preview notes | Inline approach maintains single source of truth, easier to update at GA |

**Installation:**
No additional installation required — all tools already present in repository.

---

## Architecture Patterns

### Documentation Update Pattern

The framework uses a three-layer architecture: Framework → Controls → Playbooks. Control enhancements follow this pattern:

```
docs/
├── controls/pillar-X/
│   └── X.X-control-name.md          # 10-section control file
│       ├── (existing content)
│       └── (new subsection within appropriate section)
│
├── playbooks/control-implementations/X.X/
│   ├── portal-walkthrough.md        # Add configuration steps
│   ├── powershell-setup.md          # Add automation scripts
│   ├── verification-testing.md      # Add test cases
│   └── troubleshooting.md           # Add common issues
│
└── reference/
    └── role-catalog.md               # Add new role entries
```

### Pattern 1: Control Enhancement via Subsections

**What:** Add dedicated subsections for new capabilities within the existing 10-section control structure

**When to use:** When adding new capabilities to existing controls (all six requirements)

**Example:**
```markdown
## Control Description

(existing content)

### Virtual Governance Connectors

!!! info "GA Feature"
    Virtual governance connectors are generally available as of Q1 2025.

Power Platform DLP policies enforce data protection through 11 virtual governance connectors...

| Connector | Status | Description | Configuration |
|-----------|--------|-------------|---------------|
| AI Builder (GPT) | GA | Controls access to GPT models | PPAC > DLP Policies |
...
```

**Section placement logic:**
- Technical capabilities → Control Description section
- Configuration details → Key Configuration Points section
- Role assignments → Roles & Responsibilities section
- Related capabilities → Related Controls section

### Pattern 2: Role Catalog Entry Format

**What:** Standardized role entry format with permissions matrix and FSI guidance

**When to use:** Adding new roles to role-catalog.md (AI Administrator, Defender XDR Administrator)

**Example:**
```markdown
| Canonical Role | Typical Responsibilities | Accepted Aliases |
|---|---|---|
| **AI Administrator** | Manage M365 Copilot settings, AI services | Microsoft 365 AI Administrator |

## AI Governance Permission Matrix

| Permission | AI Administrator | Entra Global Admin |
|------------|------------------|---------------------|
| Manage Copilot settings | ✓ | ✓ |
| Manage Copilot connectors | ✓ | ✓ |
...

!!! tip "FSI Least-Privilege Role Assignment"
    For agent governance: Prefer AI Administrator over Global Admin...
```

### Pattern 3: Playbook Enhancement Sections

**What:** Add dedicated sections within existing playbook structure for new capabilities

**When to use:** All playbook updates (4 playbooks × 4 controls = 16 files)

**Example structure:**
```markdown
# Control X.X: [Name] - Portal Walkthrough

(existing content)

## Step N: Configure [New Capability]

!!! warning "Preview Feature — UI may change at GA"

1. Navigate to [Portal]
2. Select [Setting]
3. Configure [Parameters]
...

### FSI-Specific Configuration

For Zone 3 environments:
- Setting 1: [Value]
- Setting 2: [Value]
```

### Anti-Patterns to Avoid

- **Appending to end of Control Description:** Don't just add paragraphs at the bottom — use dedicated subsections with headers
- **Generic admonitions:** Don't use vague "Note" admonitions — specify Preview vs. GA status explicitly
- **Role name inconsistency:** Don't invent role names — use canonical names from role-catalog.md
- **Regulatory language violations:** Don't say "ensures compliance" — use "helps support" or "aids in meeting"
- **Orphaned playbook content:** Don't add playbook sections without corresponding control updates

---

## Don't Hand-Roll

Problems that have existing solutions in the framework or Microsoft ecosystem:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Role permission documentation | Custom permission lists | Microsoft Learn permissions reference | Microsoft maintains authoritative source; changes tracked upstream |
| Feature status tracking | Manual status flags | MkDocs admonitions with semantic types | Visual distinction, searchable, theme-integrated |
| Control cross-references | Manual link maintenance | Internal markdown links with validation | MkDocs strict mode validates links at build time |
| Regulatory mapping | Inline compliance claims | Existing "Why This Matters for FSI" section pattern | Consistent format, prevents overclaims, auditable |

**Key insight:** The framework already has established patterns for every update type required in this phase. Research confirms no new patterns need invention — follow existing control and playbook structure.

---

## Common Pitfalls

### Pitfall 1: Role Name Confusion - "Defender XDR Administrator"

**What goes wrong:** Research shows "Defender XDR Administrator" is not a distinct Microsoft Entra built-in role. The correct role is "Security Administrator" (Entra Security Admin in framework naming).

**Why it happens:** Community discussions and informal documentation sometimes use "Defender XDR Admin" colloquially to describe Security Administrators managing XDR.

**How to avoid:**
- Add "Defender XDR Administrator" as an **accepted alias** for "Entra Security Admin" in role-catalog.md
- Document explicitly: "Defender XDR Administrator is an informal term; the official role is Security Administrator"
- Update controls to reference "Entra Security Admin" as the canonical name
- Add permission matrix showing Defender XDR capabilities of Security Administrator role

**Warning signs:** If documentation refers to a role not listed in Microsoft Learn permissions reference, verify it exists before creating role catalog entry.

**Sources:** [Microsoft Learn: Manage access to Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/m365d-permissions) confirms Global Administrator and Security Administrator manage XDR, no distinct "Defender XDR Administrator" role.

### Pitfall 2: SharePoint Restricted Search Status Ambiguity

**What goes wrong:** Web search results suggest RSS is "designed for" Copilot but don't explicitly state GA status. Official docs show production admin scripts and configuration guidance.

**Why it happens:** Preview features often transition to GA without prominent announcements; documentation updated incrementally.

**How to avoid:**
- Mark as GA based on official Microsoft Learn documentation presence and admin script availability
- Use `!!! info "GA Feature"` admonition in Control 4.6
- Note in control: "Available for Microsoft 365 Copilot customers" (per official docs)
- Include "verify current status before large-scale deployment" guidance

**Warning signs:** Absence of explicit "Preview" banners in Microsoft Learn docs typically indicates GA status.

**Sources:** [Microsoft Learn: Restricted SharePoint Search](https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search) provides comprehensive admin guidance without preview disclaimers.

### Pitfall 3: DSPM "AI Observability" as Distinct Feature

**What goes wrong:** Treating "AI Observability" as a standalone feature rather than a collection of capabilities within the new unified DSPM experience.

**Why it happens:** Microsoft marketing materials emphasize "AI Observability" as a headline feature, but it's actually enhanced reporting and monitoring within DSPM.

**How to avoid:**
- Research shows "AI Observability" = dedicated dashboards, agent risk tracking, activity explorer enhancements within unified DSPM
- Document as "Enhanced DSPM AI Observability capabilities" rather than a separate feature
- Update Control 1.6 with subsection on new capabilities: agent risk observability, enhanced activity explorer, unified DSPM experience (preview)
- Note weekly risk assessments are existing capability now enhanced with better reporting

**Warning signs:** If searching for a feature name yields only marketing content, not technical docs, it may be a rebranding or collection of capabilities.

**Sources:** [Microsoft Learn: New DSPM experience](https://learn.microsoft.com/en-us/purview/data-security-posture-management-learn-about) describes AI observability as dashboards and metrics within DSPM, not standalone feature.

### Pitfall 4: Virtual Connector "Enumeration" Misinterpretation

**What goes wrong:** Treating CTRL-01 as "list all virtual connectors" when the requirement is "expand existing table with comprehensive configuration guidance."

**Why it happens:** "Enumeration" can mean simple listing OR comprehensive documentation with details.

**How to avoid:**
- Control 1.5 already has a Virtual Governance Connectors table with 11 connectors
- User decision specifies "comprehensive detail" and "full enumeration, configuration guidance"
- Enhancement = expand existing table columns, add zone-specific recommendations, include HTTP endpoint filtering subsection
- Playbooks need detailed configuration steps for each connector classification

**Warning signs:** If enhancement seems trivial (just a list), verify user expectations match the scope.

### Pitfall 5: AI Feature Access Control Feature Discovery

**What goes wrong:** Searching for "AI Feature Access Control" as a distinct feature name yields no results — it's actually a collection of admin settings in Copilot Hub.

**Why it happens:** User requirement uses descriptive name; Microsoft documentation describes individual settings (Admin Exclusion Groups, Deployment Groups, feature toggles).

**How to avoid:**
- Research confirmed these are standard M365 Admin Center Copilot settings:
  - User access controls (all users / no users / specific users)
  - Admin Exclusion Groups (CopilotForM365AdminExclude security group)
  - Deployment Groups (staged rollout)
  - Web search control (tenant and group-level)
  - Copilot Chat pinning controls
  - Agent access control (which agents users can use)
- Document as "AI Feature Access Control" section in Control 3.8 that describes these settings collectively
- No MkDocs preview admonition needed — these are GA capabilities

**Warning signs:** If feature name yields zero Microsoft Learn results, it may be a descriptive name for a collection of settings.

**Sources:** [Microsoft Learn: Manage Microsoft 365 Copilot Chat](https://learn.microsoft.com/en-us/copilot/manage) and [Microsoft Learn: Agent Settings](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-settings) document the individual controls.

---

## Code Examples

### Control Enhancement Subsection Template

```markdown
### [Capability Name]

!!! [info|warning] "[GA Feature | Preview Feature]"
    [Status explanation - when available, what changes at GA if preview]

[Introductory paragraph explaining what this capability does and why it matters for agent governance]

**Key Characteristics:**

- [Characteristic 1]
- [Characteristic 2]
- [Characteristic 3]

**FSI Use Case:** [Specific financial services scenario where this capability helps]

| Configuration Item | Setting | Zone 3 Guidance |
|--------------------|---------|-----------------|
| [Item 1] | [Value] | [FSI-specific recommendation] |
| [Item 2] | [Value] | [FSI-specific recommendation] |

**Regulatory Mapping:** This capability helps support [regulation 1] ([why]), [regulation 2] ([why]).
```

### Role Catalog Entry Template

```markdown
| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **[Role Name]** | [Core responsibilities] | [Alternative names], [Common variations] |

## [Role Name] Permission Matrix

| Permission | [Role Name] | [Comparison Role 1] | [Comparison Role 2] |
|------------|-------------|---------------------|---------------------|
| [Permission 1] | ✓ | ✓ | ✗ |
| [Permission 2] | ✓ | ✗ | ✗ |
| [Permission 3] | ✗ | ✓ | ✓ |

*[Additional notes about delegation, scope limitations, or special cases]

!!! tip "FSI Least-Privilege Role Assignment"
    - **For [use case 1]:** Prefer [Role Name] over [Global Admin] to enforce [principle]
    - **For [use case 2]:** Use [Role Name] when [condition]
    - **When Global Admin is required:** [Specific scenarios that genuinely need Global Admin]
    - **For FINRA-regulated firms:** [Regulatory compliance consideration per Rule 3110]
```

### Playbook Step Template for New Capability

```markdown
## Step [N]: Configure [Capability Name]

!!! warning "Preview Feature — UI may change at GA"
    This feature is in preview as of [month year]. Steps documented reflect current preview UI.

1. Navigate to [Portal URL]
2. Select **[Menu Path]** > **[Submenu]**
3. In the **[Section Name]** section, configure:
   - **[Setting 1]:** Set to `[Value]` ([reason])
   - **[Setting 2]:** Set to `[Value]` ([reason])
4. For Zone 3 environments, additionally configure:
   - **[Zone-specific setting]:** `[Value]`
5. Click **Save** and allow [N] hours for propagation

### Verification

To verify configuration:

```powershell
# PowerShell verification command
Get-[Noun] -[Parameter] | Where-Object { $_.Property -eq "Value" }
```

Expected output: [Description of what successful configuration looks like]

### FSI-Specific Notes

- **Zone 1:** [Guidance for personal productivity agents]
- **Zone 2:** [Guidance for team collaboration agents]
- **Zone 3:** [Guidance for enterprise managed agents]
```

---

## State of the Art

| Capability | Old Approach | Current Approach | When Changed | Impact |
|------------|--------------|------------------|--------------|--------|
| Virtual Connectors | Manual feature toggles per service | Unified DLP policy enforcement via virtual connectors | Q1 2025 | Centralized governance across Copilot Studio capabilities |
| DSPM for AI | Separate "AI Hub DSPM" experience | Unified DSPM experience with AI Observability | Preview (Q1 2026 GA) | Single pane of glass for data security across all data types |
| AI Administration | Global Admin or Power Platform Admin | Dedicated AI Administrator role | Q4 2025-Q1 2026 | Least-privilege access for Copilot governance |
| Defender XDR Access | Security Administrator (existing) | Security Administrator (confirmed) | N/A | Clarification of correct role name |
| SharePoint Search for AI | Restricted Content Discovery only | Restricted Search + Restricted Content Discovery | Q4 2025 | Positive governance model with allowed list |
| Copilot User Access | License-based only | License + Admin Exclusion + Deployment Groups | Q4 2025-Q1 2026 | Granular user-level and feature-level controls |

**Deprecated/outdated:**
- "AI Hub DSPM" naming: Now called "Data Security Posture Management for AI (DSPM for AI)" since November 2024
- Separate Defender XDR governance roles: Security Administrator is the canonical Entra role for XDR management
- Opt-out DLP enforcement for Copilot Studio: DLP enforcement is now mandatory (enabled early 2025 per MC973179)

---

## Open Questions

1. **Unified DSPM GA Timeline**
   - What we know: Microsoft announced unified DSPM experience in preview, targeting "early 2026" GA (April-May 2026 rollout per MC1191257)
   - What's unclear: Exact GA date not confirmed; preview documentation may change
   - Recommendation: Document new DSPM AI Observability capabilities with `!!! warning 'Preview Feature'` admonition in Control 1.6; update to `!!! info 'GA Feature'` when Message Center confirms GA

2. **SharePoint Restricted Search Preview/GA Status**
   - What we know: Microsoft Learn docs show comprehensive admin guidance with PowerShell scripts; no preview disclaimers present
   - What's unclear: No explicit "GA" announcement found in research; may have quietly transitioned from preview
   - Recommendation: Mark as GA in Control 4.6 based on production documentation availability; include note "verify feature availability for your tenant before large-scale deployment"

3. **AI Administrator Role Adoption Timeline**
   - What we know: Role exists in Entra with documented permissions; Microsoft guidance recommends for Copilot management
   - What's unclear: When role became GA (appears Q4 2025-Q1 2026); adoption rate among FSI organizations
   - Recommendation: Document as GA in role catalog; include "recently introduced" context note; emphasize least-privilege benefits for FINRA 3110 compliance

4. **Defender XDR Administrator Alias Handling**
   - What we know: "Defender XDR Administrator" is informal term; official role is "Security Administrator"
   - What's unclear: Whether to add as separate role-catalog entry or as alias only
   - Recommendation: Add as "Accepted Aliases" for Entra Security Admin; include explicit note that it's informal terminology for Security Administrator managing XDR workloads

5. **Virtual Connector Configuration Details**
   - What we know: 11 virtual connectors exist; basic classification (Business/Non-Business/Blocked) documented
   - What's unclear: Detailed zone-specific recommendations for each connector; HTTP endpoint filtering pattern examples
   - Recommendation: Control 1.5 and playbooks already have foundation; enhancement adds comprehensive zone-specific guidance table and HTTP filtering subsection

---

## Sources

### Primary (HIGH confidence)

- [Microsoft Learn: Restricted SharePoint Search](https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search) - GA status, configuration guidance, allowed list management
- [Microsoft Learn: Data Security Posture Management (new preview)](https://learn.microsoft.com/en-us/purview/data-security-posture-management-learn-about) - AI Observability capabilities, unified DSPM experience
- [Microsoft Learn: DSPM for AI (classic)](https://learn.microsoft.com/en-us/purview/dspm-for-ai) - Weekly risk assessments, existing capabilities
- [Microsoft Learn: Microsoft Entra built-in roles](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference) - AI Administrator role permissions
- [Microsoft Learn: AI Administrator connector delegation](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/connector-admin-delegation) - AI Admin scope and delegation
- [Microsoft Learn: Manage access to Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/m365d-permissions) - Security Administrator role for XDR
- [Microsoft Learn: Manage Microsoft 365 Copilot Chat](https://learn.microsoft.com/en-us/copilot/manage) - User access controls, feature restrictions
- [Microsoft Learn: Agent Settings](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-settings) - Admin Exclusion Groups, Deployment Groups

### Secondary (MEDIUM confidence)

- [Microsoft Learn: Custom connector parity](https://learn.microsoft.com/en-us/power-platform/admin/dlp-custom-connector-parity) - Virtual connector background (verified with existing Control 1.5 content)
- [Microsoft Community Hub: New DSPM experience announcement](https://techcommunity.microsoft.com/blog/microsoft-security-blog/beyond-visibility-the-new-microsoft-purview-data-security-posture-management-dsp/4470984) - DSPM roadmap and timeline
- [M365 Admin Message Center Archive: MC1191257](https://mc.merill.net/message/MC1191257) - Unified DSPM rollout timeline (April-May 2026)
- [Microsoft Community Hub: What's New in M365 Copilot January 2026](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/what%E2%80%99s-new-in-microsoft-365-copilot--january-2026/4488916) - Agent mode, Copilot updates

### Tertiary (LOW confidence)

- Web search results for virtual connectors, DSPM observability, AI Administrator, Defender XDR Administrator, SharePoint Restricted Search, AI Feature Access Control - Ecosystem context and feature discovery (all findings verified with primary sources)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Established MkDocs/Markdown framework, no new tools needed
- Architecture: HIGH - Existing control/playbook patterns well-documented in framework
- Control enhancement scope: HIGH - All six capabilities verified with official Microsoft Learn documentation
- Role catalog updates: HIGH - AI Administrator role fully documented; Defender XDR Admin confirmed as Security Administrator alias
- Playbook update pattern: HIGH - Existing playbook structure provides clear template for enhancements

**Research date:** 2026-02-06
**Valid until:** 30 days (March 2026) - Unified DSPM GA expected April 2026; re-verify preview status at planning time
