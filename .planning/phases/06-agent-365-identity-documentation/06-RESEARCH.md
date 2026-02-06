# Phase 6: Agent 365 & Identity Documentation - Research

**Researched:** 2026-02-05
**Domain:** Microsoft Agent 365 unified control plane, Entra Agent ID identity architecture, M365 Admin Center Agent Settings
**Confidence:** HIGH

## Summary

Phase 6 requires creating comprehensive documentation for Microsoft's Agent 365 unified control plane, Entra Agent ID identity architecture, and M365 Admin Center Agent Settings—all framed for FSI governance practitioners. This is a documentation-only phase targeting the FSI-AgentGov repository.

Research confirms that Agent 365 and Entra Agent ID represent a fundamental architectural shift from per-platform governance to unified control plane governance. The distinction is critical: **Entra Agent ID** is the identity service (like Entra ID for users), while **Agent 365** is the control plane (like M365 Admin Center). Agent 365 uses Entra Agent ID as its identity foundation.

Both capabilities are currently in preview through Microsoft's Frontier program, with GA expected Q1-Q2 2026. The framework already has two related documents (`agent-identity-architecture.md` and `agent-365-architecture.md`), and this phase will create a unified replacement that consolidates and expands this content.

**Primary recommendation:** Create a single comprehensive document that progresses from identity foundation (Entra Agent ID) → control plane architecture (Agent 365) → admin settings (M365 Admin Center), with detailed Mermaid diagrams, side-by-side comparison tables, migration readiness checklists, and expanded control mapping. The document should adopt a "prepare now, migrate later" tone with pre-GA and post-GA action items clearly separated.

---

## User Constraints

### Locked Decisions

**From CONTEXT.md - These MUST be followed:**

1. **Single unified document** combining all 3 requirements (A365-01, A365-02, A365-03) — Entra Agent ID → Agent 365 control plane → M365 Admin Center settings
2. **Replaces** existing `docs/framework/agent-identity-architecture.md` — fold existing content into the unified doc as single source of truth
3. **Detailed Mermaid diagrams** included: identity flow (Entra Agent ID → sponsorship model), control plane architecture, and admin settings hierarchy — not just one overview diagram
4. **Tone: "Prepare now, migrate later"** — actionable prep steps readers can take before GA, with current-state fallbacks
5. **Side-by-side comparison tables** for current governance vs. Agent 365 governance — "Today (per-platform)" vs "Agent 365 (unified)" columns
6. **Migration readiness checklist with phases** — pre-GA checklist (identity audit, sponsorship model planning, CA policy review) + post-GA migration steps
7. **Single top-level disclaimer** about preview status: "Based on preview features as of [date]. Verify GA status before implementing." — no inline per-feature status badges
8. **Expanded mapping table** covering all controls that Agent 365 changes (likely 10-15 controls across identity, DLP, registry, access)
9. **Current vs. Agent 365 columns** format: Control | Current Approach | Agent 365 Approach — consistent with existing `agent-365-architecture.md` pattern
10. **Phase 6 also updates affected control files** (pillar-1/, pillar-2/ etc.) with Agent 365 forward-reference notes — not deferred to Phase 7
11. **Dual audience:** M365 administrators (tactical, admin settings) AND security architects (strategic, architecture decisions)
12. **Assumes framework knowledge** — readers know the 62 controls and 3 zones. Links to framework docs for newcomers rather than explaining inline
13. **Only document confirmed features** — stick to officially documented Microsoft guidance. Skip speculative areas entirely to minimize outdated content risk
14. **Link to Microsoft Learn sources** as references — readers can verify and track updates. Consistent with existing framework docs
15. **Add new Learn URLs to monitoring list** — any Microsoft Learn URLs referenced in this doc must be added to `scripts/learn_monitor.py` tracking (currently 209 URLs)

### Claude's Discretion

- Exact file placement within docs/ tree (framework/ or reference/)
- Document section ordering and heading hierarchy
- Which specific controls are affected (determined during research)
- Level of detail in Mermaid diagrams
- Exact wording of preview disclaimer banner

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

---

## Standard Stack

This is a documentation phase, not a code/script phase. The "stack" consists of documentation tooling and Microsoft Learn sources.

### Core Documentation Tools

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| MkDocs Material | 9.5+ | Static site generator | Already used for FSI-AgentGov framework |
| Mermaid.js | 10.6+ | Diagram rendering | Embedded in MkDocs Material, supports architecture diagrams |
| Markdown | CommonMark | Content format | Universal documentation format |

### Microsoft Learn Sources (PRIMARY AUTHORITY)

| Source | Coverage | Confidence |
|--------|----------|------------|
| [Microsoft Entra Agent ID Overview](https://learn.microsoft.com/en-us/entra/agent-id/) | Identity architecture | HIGH - GA |
| [Agent Owners, Sponsors, Managers](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-owners-sponsors-managers) | Sponsorship model | HIGH - GA |
| [Governing Agent Identities](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview) | Lifecycle workflows | HIGH - GA |
| [Conditional Access for Agent Identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) | CA policies | HIGH - GA |
| [Agent Settings in M365 Admin Center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-settings) | Admin controls | HIGH - GA |
| [Agent Registry in M365 Admin Center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry) | Registry metadata | HIGH - GA |
| [Agent 365 Blueprint (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-blueprint) | Blueprint architecture | MEDIUM - Preview |
| [Agent 365 Identity (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/identity) | Identity integration | MEDIUM - Preview |
| [Agent 365 Observability (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/observability) | Telemetry/monitoring | MEDIUM - Preview |

### Supporting Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| Python 3.11+ | Learn Monitor script updates | Adding new URLs to monitoring |
| VS Code | Markdown editing | Local development |
| Git | Version control | Committing changes |

**Installation:**

None required — documentation editing uses existing FSI-AgentGov tooling.

---

## Architecture Patterns

### Unified Document Structure

The research confirms that the unified document should follow this progression:

```
unified-agent-governance.md (or similar name)
├── 1. Introduction & Preview Disclaimer
├── 2. Entra Agent ID: Identity Foundation
│   ├── What is an Agent Identity?
│   ├── Agentic Users vs. Service Principals
│   ├── Sponsorship Model (Owners, Sponsors, Managers)
│   ├── Lifecycle Workflows
│   └── Conditional Access Policies
├── 3. Agent 365: Unified Control Plane
│   ├── Control Plane Architecture
│   ├── Unified Registry
│   ├── Security Posture Management
│   ├── Observability (Application Insights)
│   └── Cross-Platform Governance
├── 4. M365 Admin Center: Agent Settings
│   ├── Allowed Agent Types
│   ├── Sharing Controls
│   ├── Templates (Default & Custom)
│   └── User Access
├── 5. Migration Roadmap
│   ├── Phase 1: Foundation (Entra Agent ID - available now)
│   ├── Phase 2: Evaluation (Agent 365 Preview - Frontier)
│   └── Phase 3: Adoption (Agent 365 GA - future)
├── 6. Control Impact Analysis
│   └── Control | Current Approach | Agent 365 Approach
├── 7. FSI Regulatory Alignment
└── 8. Related Framework Components & Sources
```

### Pattern 1: Sponsorship Model Documentation

**What:** Document the three administrative roles (Owners, Sponsors, Managers) with separation of concerns

**When to use:** Explaining human accountability for agent lifecycle

**Example structure:**

```markdown
## Sponsorship Model: Human Accountability for Agents

### Three Administrative Roles

| Role | Access Level | Responsibilities | Typical Persona |
|------|--------------|------------------|----------------|
| **Owners** | Technical admin | Modify settings, credentials, re-enable agents | Developers, IT admins |
| **Sponsors** | Business oversight | Lifecycle decisions, access requests, incident response | Business owners, team leads |
| **Managers** | Hierarchical view | Request access packages, view reporting agents | Same as organizational managers |

### Separation of Concerns

- **Owners** = Technical control WITHOUT business decision-making
- **Sponsors** = Business accountability WITHOUT technical modification rights
- **Managers** = Organizational visibility WITHOUT administrative control

This separation aligns with FINRA 3110's supervision requirements: sponsors provide business oversight (supervision), while owners handle technical operations (execution).

### Sponsorship Succession

When a sponsor leaves the organization:
1. Entra ID Lifecycle Workflows detect sponsor termination
2. Automatic reassignment to sponsor's manager (if configured)
3. Notification sent to backup sponsor (if designated)
4. Agent suspended if no action within 14 days (configurable)
5. Compliance team notified for Zone 3 agents

[Mermaid diagram showing sponsor lifecycle workflow]
```

### Pattern 2: Side-by-Side Comparison Tables

**What:** Compare current per-platform governance with Agent 365 unified governance

**When to use:** Throughout the document to show migration value

**Example:**

```markdown
## Agent Registry: Current vs. Agent 365

| Aspect | Current (Per-Platform) | Agent 365 (Unified) |
|--------|------------------------|---------------------|
| **Discovery** | Manual scripts across PPAC, M365 Admin Center, Azure Portal, SharePoint Admin Center | Automatic aggregation in unified registry |
| **Metadata** | Basic (name, owner, environment) | Rich (usage analytics, risk scores, compliance status) |
| **Audit Trail** | Separate logs per platform; manual consolidation for examinations | Unified activity log in Application Insights; single export |
| **Policy Enforcement** | DLP policies in Power Platform don't apply to Agent Builder agents | Cross-platform DLP enforcement via Purview |
| **Compliance Reporting** | Custom PowerShell scripts to aggregate data | Pre-built dashboards; Graph API export |

**FSI Value:** Examination response time reduced from days (manual consolidation) to minutes (single registry export).
```

### Pattern 3: Migration Readiness Checklist

**What:** Pre-GA and post-GA action items with clear status

**When to use:** Helping readers prepare for Agent 365 adoption

**Example:**

```markdown
## Migration Readiness Checklist

### Pre-GA Actions (Available Now)

- [ ] **Enable Entra Agent ID** in your tenant (Entra admin center > Identity Governance > Agent ID)
- [ ] **Assign sponsors to existing agents**
  - Zone 1: Agents sponsor themselves
  - Zone 2: Require manager approval
  - Zone 3: Require director + compliance approval
- [ ] **Configure Entra ID Lifecycle Workflows**
  - Periodic sponsor reviews (monthly for Zone 3, quarterly for Zone 2)
  - Automatic sponsor reassignment when sponsor departs
  - Agent suspension if sponsor review not completed within 14 days
- [ ] **Implement Conditional Access policies** for agent authentication
  - Policy 1: Block high-risk agent identities (Agent risk = High)
  - Policy 2: Allow only approved agents to access sensitive resources (using custom security attributes)
- [ ] **Enroll in Microsoft 365 Frontier program** to access Agent 365 preview

### Post-GA Actions (After Agent 365 GA Announcement)

- [ ] **Validate GA feature set** against Phase 2 gap analysis
- [ ] **Pilot production migration** with Zone 1 agents (low risk)
- [ ] **Run parallel governance** for 30 days (Agent 365 + per-platform)
- [ ] **Phased rollout by zone** (Zone 1 → Zone 2 → Zone 3)
- [ ] **Sunset per-platform processes** once Agent 365 coverage complete
```

### Pattern 4: Detailed Mermaid Diagrams

**What:** Architecture diagrams showing identity flow, control plane, and admin settings hierarchy

**When to use:** Visual explanation of complex concepts

**Example topics for diagrams:**

1. **Entra Agent ID Sponsorship Flow**
   - Shows: User creates agent → Entra Agent ID created → Sponsor assignment workflow → Manager approval (Zone 2+) → Agent activated
   - Includes: Decision points, approval gates, automatic succession path

2. **Agent 365 Control Plane Architecture**
   - Shows: Copilot Studio, Agent Builder, Azure AI Foundry, SharePoint agents → Agent 365 Unified Registry → Security Posture Dashboard, Observability (App Insights), Lifecycle Management, Cross-Platform Policies
   - Includes: Identity layer (Entra Agent ID) as foundation

3. **M365 Admin Center Agent Settings Hierarchy**
   - Shows: Agent Settings (root) → Allowed Agent Types, Sharing Controls, Templates, User Access
   - Includes: Template types (Default vs. Custom), sharing options (All/None/Specific Groups)

### Anti-Patterns to Avoid

- **DON'T assume Agent 365 is GA yet** — Preview status must be clear in the disclaimer
- **DON'T explain basic framework concepts inline** — Link to existing framework docs (zones, controls) rather than re-explaining
- **DON'T use speculative features** — Stick to officially documented capabilities only
- **DON'T use regulatory guarantee language** — "helps support" not "ensures compliance"
- **DON'T create inline per-feature status badges** — Single top-level disclaimer only

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Custom agent registry | SharePoint list with manual updates | Agent 365 Unified Registry (post-GA) | Microsoft's registry includes automatic discovery, rich metadata, security integration, and Graph API export |
| Agent identity management | Service principals with custom governance | Entra Agent ID with sponsorship model | Purpose-built for agents; includes lifecycle workflows, Conditional Access, and sponsorship succession |
| Agent activity monitoring | Custom PowerShell scripts aggregating logs | Agent 365 Observability (Application Insights) | Unified telemetry across all agent types; pre-built dashboards; OpenTelemetry standard |
| Sponsorship tracking | Manual spreadsheets | Entra ID Lifecycle Workflows | Automated sponsor reviews, succession handling, compliance notifications |
| Conditional Access for agents | Per-app policies | Entra Agent ID Conditional Access | Agent-specific risk signals; custom security attributes; unified policy enforcement |

**Key insight:** Agent 365 and Entra Agent ID are designed to replace fragmented per-platform governance. Custom solutions will become technical debt as Microsoft's unified control plane matures.

---

## Common Pitfalls

### Pitfall 1: Confusing Agent 365 with Entra Agent ID

**What goes wrong:** Documentation conflates the control plane (Agent 365) with the identity service (Entra Agent ID), leading to misunderstanding of when to use each

**Why it happens:** Similar naming, both announced at Ignite 2025, both related to agent governance

**How to avoid:**
- Use the analogy: "Agent 365 is like M365 Admin Center (management portal), Entra Agent ID is like Entra ID (identity directory)"
- Clearly state: "Agent 365 uses Entra Agent ID as its identity foundation"
- Document separately, then show integration

**Warning signs:**
- Readers ask "Do I need both?"
- Confusion about where to configure sponsorship (Entra) vs. where to view registry (Agent 365)

### Pitfall 2: Documenting Preview Features as Production-Ready

**What goes wrong:** Readers implement preview features in production, then face breaking changes or unsupported scenarios

**Why it happens:** Excitement about new capabilities; unclear preview status; mixing GA and preview features

**How to avoid:**
- Single top-level disclaimer about preview status (with date)
- Migration roadmap clearly separates "Phase 1: Foundation (available now with GA features)" from "Phase 2: Evaluation (preview only)" from "Phase 3: Adoption (post-GA)"
- Side-by-side tables show current-state fallbacks when Agent 365 isn't GA yet
- Explicitly state: "Continue using per-platform governance for production until Agent 365 reaches GA"

**Warning signs:**
- Readers report Agent 365 features aren't available in their tenant (not enrolled in Frontier)
- Compliance teams concerned about using preview features for regulatory requirements

### Pitfall 3: Insufficient Control Impact Analysis

**What goes wrong:** Documentation updates the unified doc but doesn't identify which of the 62 controls are affected by Agent 365, leading to outdated control files

**Why it happens:** Control impact analysis requires reading all 62 controls to find Agent 365 references

**How to avoid:**
- Research identified 17+ controls currently referencing Agent 365, Entra Agent ID, or sponsorship
- Expanded mapping table must cover: 1.2 (Registry), 1.5 (DLP), 1.7 (Audit), 1.8 (Runtime Protection), 1.11 (Conditional Access), 2.1 (Managed Environments), 2.3 (Change Management), 2.12 (FINRA 3110 Supervision), 3.1 (Inventory), 3.6 (Orphaned Agent Detection), and others
- Phase 6 tasks must include updating control files with forward-reference notes

**Warning signs:**
- Control files still reference per-platform governance only
- No clear path from control to Agent 365 guidance
- Readers confused about how Agent 365 affects their control implementation

### Pitfall 4: Forgetting to Update Learn Monitor

**What goes wrong:** New Agent 365 documentation links to Microsoft Learn URLs that aren't monitored, so the team doesn't get notified when Microsoft updates those pages

**Why it happens:** Learn Monitor script requires manual URL addition

**How to avoid:**
- User constraint explicitly requires: "Add new Learn URLs to monitoring list"
- All Microsoft Learn URLs referenced in the unified doc must be added to `scripts/learn_monitor.py`
- Currently 209 URLs monitored; expect to add 10-15 new URLs for Agent 365

**Warning signs:**
- Microsoft updates Agent 365 Learn docs but no PR is created
- Framework documentation becomes outdated without notification

### Pitfall 5: Over-Explaining Basic Framework Concepts

**What goes wrong:** Document becomes bloated with explanations of zones, controls, and governance principles that readers already know

**Why it happens:** Trying to make the document self-contained for newcomers

**How to avoid:**
- User constraint: "Assumes framework knowledge — readers know the 62 controls and 3 zones"
- Link to framework docs rather than re-explaining: "See [Zones and Tiers](zones-and-tiers.md) for governance zone definitions"
- Keep focus on Agent 365 architecture, not framework fundamentals

**Warning signs:**
- Document exceeds 500 lines with inline explanations
- Redundancy with existing framework documents

---

## Code Examples

This is a documentation phase, but the document will reference configuration examples from Microsoft Learn.

### Entra Agent ID Conditional Access Policy

Source: [Microsoft Learn - Conditional Access for Agent Identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id)

**Scenario: Block High-Risk Agent Identities**

```json
{
  "displayName": "Block high-risk agent identities",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeAgents": "all"
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "agentRisk": {
      "riskLevels": ["high"]
    }
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["block"]
  }
}
```

**Scenario: Allow Only Approved Agents Using Custom Security Attributes**

```json
{
  "displayName": "Allow only HR-approved agents to access HR resources",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeAgents": "all",
      "excludeAgents": {
        "attributeFilter": {
          "attribute": "AgentApprovalStatus",
          "operator": "Contains",
          "value": "HR_Approved"
        }
      }
    },
    "applications": {
      "includeApplications": ["All"],
      "excludeApplications": {
        "attributeFilter": {
          "attribute": "Department",
          "operator": "Contains",
          "value": "HR"
        }
      }
    }
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["block"]
  }
}
```

### Entra ID Lifecycle Workflow: Sponsor Departure Handling

Source: [Microsoft Learn - Agent Sponsor Tasks in Lifecycle Workflows](https://learn.microsoft.com/en-us/entra/id-governance/agent-sponsor-tasks)

**Workflow configuration:**

```json
{
  "displayName": "Agent sponsor departure handling",
  "isEnabled": true,
  "executionConditions": {
    "trigger": {
      "type": "userDeparture"
    },
    "scope": {
      "subjectType": "agentic_user_sponsor"
    }
  },
  "tasks": [
    {
      "taskDefinitionId": "sendNotificationToBackupSponsor",
      "arguments": [
        {
          "name": "messageTemplate",
          "value": "AgentSponsorDepartureNotification"
        }
      ]
    },
    {
      "taskDefinitionId": "suspendAgentIfNoAction",
      "arguments": [
        {
          "name": "delayInDays",
          "value": "14"
        }
      ]
    }
  ]
}
```

### M365 Admin Center Agent Settings: Custom Template

Source: [Microsoft Learn - Agent Settings in Microsoft 365 Admin Center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-settings)

**Custom template for Zone 3 agents:**

```markdown
1. Open Microsoft 365 admin center
2. Navigate to Agents > Settings > Template > Add New Template
3. Select agent type: "Copilot Studio agents"
4. Provide:
   - Template name: "Zone 3 Enterprise Managed Agents"
   - Description: "Template for customer-facing agents with full governance"
5. Add custom policies (Microsoft's default policies are preselected and locked):
   - Require sensitivity label: "Highly Confidential"
   - Require DLP policy: "FSI Data Protection"
   - Require approval workflow: "AI Governance Committee"
6. Review and save
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Service principals for agent identity | Entra Agent ID (Agentic Users) | Nov 2025 (Ignite announcement) | Agents now have first-class identities with Conditional Access, sponsorship, and lifecycle workflows |
| Per-platform agent registries (PPAC, M365 Admin Center, Azure Portal) | Agent 365 Unified Registry | Nov 2025 (preview) | Single source of truth for all agent types; eliminates manual consolidation |
| Manual agent ownership tracking in spreadsheets | Entra ID Lifecycle Workflows with automatic sponsor succession | Oct 2025 (GA for ownership reassignment) | Automated sponsor reviews, departure handling, compliance notifications |
| Custom PowerShell scripts for agent activity monitoring | Agent 365 Observability with Application Insights | Nov 2025 (preview) | Unified telemetry across all agent types using OpenTelemetry standard |
| Per-app Conditional Access policies for agents | Entra Agent ID Conditional Access with agent-specific risk signals | Nov 2025 (GA for agent CA) | Risk-based policies for agents; custom security attributes; agent risk detection |

**Deprecated/outdated:**

- **Service principals as primary agent identity** — Agentic Users are now the recommended identity type for agents (supports sponsorship, licensing, Conditional Access)
- **Per-platform governance approaches** — Agent 365 unified control plane replaces fragmented per-platform administration (still in preview; continue per-platform until GA)
- **Manual agent registry in SharePoint** — Agent 365 Unified Registry provides richer metadata and automatic discovery (preview; SharePoint registry still valid until GA)

**Current state (February 2026):**

- **Entra Agent ID:** Generally available (GA)
- **Entra Agent ID Conditional Access:** Generally available (GA)
- **Entra ID Lifecycle Workflows for agents:** Generally available (GA)
- **Agent 365 Unified Control Plane:** Preview (requires Frontier program enrollment)
- **M365 Admin Center Agent Settings:** Generally available (GA)
- **M365 Admin Center Agent Registry:** Generally available (GA)
- **Agent 365 Observability:** Preview (requires Frontier program enrollment)

**Expected GA timeline:**

- Agent 365 Unified Control Plane: Q1-Q2 2026 (estimated)

---

## Open Questions

### 1. Agent 365 Licensing Model Post-GA

**What we know:**
- Preview access included with Frontier program enrollment
- Default template automatically assigns Agent 365 license to instances (preview feature)
- Microsoft's licensing model for GA not yet announced

**What's unclear:**
- Per-agent licensing fees post-GA?
- Included in existing M365 E5/Power Platform Premium licenses?
- Separate SKU required?

**Recommendation:**
- Document preview status in migration roadmap
- Note: "Agent 365 licensing model for GA not yet announced; preview access included with Frontier enrollment"
- Recommend budgeting for potential per-agent licensing fees (similar to Power Platform Premium model)
- Update documentation when Microsoft announces GA licensing

### 2. Agent 365 Coverage for Third-Party Agents

**What we know:**
- Agent 365 registry intended to track "all agents" including third-party and open-source agents
- Microsoft Learn documentation mentions "third-party agents" in registry capabilities

**What's unclear:**
- How are third-party agents registered in Agent 365?
- Does Agent 365 apply DLP policies to third-party agents?
- What observability is available for non-Microsoft agents?

**Recommendation:**
- Document in "Open Questions" section of unified doc
- Note: "Agent 365 third-party agent coverage details not yet fully documented; expect clarification at GA"
- Recommend testing third-party agent registration in Phase 2 (Evaluation) with Frontier program

### 3. Agent 365 Integration with Existing FSI-AgentGov-Solutions

**What we know:**
- FSI-AgentGov-Solutions repository has 13 deployable solutions covering 17 controls
- Solutions include agent registry automation, environment lifecycle management, and deny event correlation

**What's unclear:**
- Will FSI-AgentGov-Solutions be updated to integrate with Agent 365 APIs?
- Should solutions use Agent 365 registry as data source instead of custom SharePoint lists?
- When should migration from custom solutions to Agent 365 native capabilities occur?

**Recommendation:**
- Phase 6 documentation should note: "Future FSI-AgentGov-Solutions updates may integrate with Agent 365 APIs post-GA"
- Control mapping table should show both current approach (custom solutions) and Agent 365 approach (native capabilities)
- Leave actual solution migration to future phases (post-Agent 365 GA)

### 4. Entra Agent ID Sponsorship Limits

**What we know:**
- Sponsorship model requires one or more sponsors per agent
- Sponsors can be users or groups
- Best practice: maximum of 10 agents per sponsor (configurable)

**What's unclear:**
- Is the 10 agent limit enforced by Entra Agent ID or just a recommendation?
- What happens if a sponsor exceeds the limit?
- Can policy enforce sponsor limits automatically?

**Recommendation:**
- Document as best practice: "Recommended maximum of 10 agents per sponsor"
- Note in unified doc: "Limit is configurable by organizational policy; no hard technical limit in Entra Agent ID"
- Recommend monitoring sponsor workload in periodic reviews

---

## Control Impact Analysis

Research identified **17 controls** currently referencing Agent 365, Entra Agent ID, or sponsorship. Based on the unified documentation, the following controls will need Agent 365 forward-reference notes:

### High Impact (Major Changes)

| Control | Current Approach | Agent 365 Approach | Forward Reference Note |
|---------|------------------|--------------------|-----------------------|
| **1.2 Agent Registry** | Custom SharePoint list + per-platform inventories (PPAC, M365 Admin Center) | Agent 365 Unified Registry with automatic discovery, rich metadata, Graph API export | "Agent 365 Unified Registry (preview) offers a future architecture that consolidates all agent types. See [unified doc] for migration guidance." |
| **1.11 Conditional Access** | Per-app policies; service principals; inconsistent coverage | Entra Agent ID Conditional Access with agent-specific risk signals, custom security attributes | "Entra Agent ID extends Conditional Access to agents. See [unified doc] for agent CA policies and risk detection." |
| **2.12 FINRA 3110 Supervision** | Manual supervisor assignment in documentation | Entra Agent ID sponsorship model with enforced human accountability, lifecycle workflows | "Entra Agent ID sponsorship model aligns with FINRA 3110 supervision requirements. See [unified doc] for sponsorship configuration." |
| **3.6 Orphaned Agent Detection** | PowerShell scripts querying multiple platforms; manual correlation | Agent 365 lifecycle governance with automatic orphan flagging; Entra ID Lifecycle Workflows trigger reassignment | "Agent 365 lifecycle governance automates orphan detection. See [unified doc] for lifecycle workflow configuration." |

### Medium Impact (Enhanced Capabilities)

| Control | Current Approach | Agent 365 Approach | Forward Reference Note |
|---------|------------------|--------------------|-----------------------|
| **1.5 DLP and Sensitivity Labels** | Per-platform DLP policies (PPAC for Copilot Studio, M365 for Agent Builder) | Cross-platform DLP enforcement via Purview integration with Agent 365 | "Agent 365 enables cross-platform DLP enforcement. See [unified doc] for unified DLP configuration." |
| **1.7 Comprehensive Audit Logging** | Separate logs per platform; manual consolidation for examinations | Unified activity logs in Application Insights via Agent 365 Observability | "Agent 365 Observability consolidates audit logs. See [unified doc] for Application Insights integration." |
| **1.8 Runtime Protection** | Per-platform threat detection (Defender for Cloud Apps for PPAC) | Centralized security posture dashboard in Agent 365 with real-time policy violation visibility | "Agent 365 security posture dashboard provides unified threat visibility. See [unified doc] for security integration." |
| **2.1 Managed Environments** | Power Platform Managed Environments (PPAC) | Agent 365 lifecycle management with promotion gates and approval workflows | "Agent 365 lifecycle management complements Managed Environments. See [unified doc] for promotion gate configuration." |
| **2.3 Change Management** | Per-platform approval workflows | Agent 365 promotion gates enforce consistent approval workflows across agent types | "Agent 365 standardizes change management across platforms. See [unified doc] for approval workflow configuration." |
| **3.1 Agent Inventory** | Manual inventory consolidation from multiple platforms | Agent 365 unified registry eliminates manual consolidation; single source of truth | "Agent 365 unified registry provides single source of truth. See [unified doc] for registry capabilities." |

### Low Impact (Minor References)

| Control | Forward Reference Note |
|---------|------------------------|
| **1.6 DSPM for AI** | "Agent 365 integrates with Purview DSPM. See [unified doc] for security posture integration." |
| **1.18 RBAC** | "Entra Agent ID supports role assignments for agent identities. See [unified doc] for agent RBAC configuration." |
| **1.24 Defender AI-SPM** | "Agent 365 security posture dashboard integrates with Defender. See [unified doc] for threat detection." |
| **2.4 Business Continuity** | "Agent 365 observability supports DR testing. See [unified doc] for observability configuration." |
| **2.5 Testing & Validation** | "Agent 365 lifecycle management supports promotion gates. See [unified doc] for testing workflows." |
| **2.13 Documentation** | "Agent 365 unified registry provides comprehensive agent documentation. See [unified doc] for registry metadata." |
| **3.2 Usage Analytics** | "Agent 365 observability provides rich usage analytics. See [unified doc] for Application Insights dashboards." |

**Total controls affected:** 17 (27% of 62 controls)

---

## FSI Regulatory Alignment

### FINRA 3110 (Supervision and Oversight)

**How Agent 365 Helps:**

- **Sponsorship Model:** Entra Agent ID sponsorship creates clear human accountability for agent behavior, aligning with FINRA 3110's requirement for designated supervisors
- **Separation of Duties:** Sponsors provide business oversight (supervision), while owners handle technical operations (execution)
- **Lifecycle Workflows:** Automated sponsor reviews ensure continuous supervision; monthly reviews for Zone 3 align with FINRA's supervision requirements
- **Audit Trail:** Unified activity logs in Application Insights support supervision evidence collection

**Documentation Approach:**
- Map Entra Agent ID "sponsors" to FINRA 3110 "designated supervisors"
- Note: "Sponsorship model enforces FINRA 3110 supervision requirements through mandatory human accountability"
- Recommend: Monthly sponsor reviews for customer-facing agents (Zone 3)

**Source:** [FINRA Rule 3110: Supervision](https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110)

### SEC 17a-3/4 (Recordkeeping)

**How Agent 365 Helps:**

- **Unified Audit Trail:** Agent 365 Observability consolidates activity logs across all agent types into Application Insights
- **Time-Stamped Records:** OpenTelemetry standard captures timestamp, identity, action, and result for all agent invocations
- **Identity Attribution:** Entra Agent ID ensures all agent actions are attributable to a specific agent identity (not shared service principal)
- **Retention Integration:** Application Insights retention policies can be configured to meet SEC 17a-4's 3-6 year retention requirements

**Documentation Approach:**
- Note: "Agent 365 Observability supports SEC 17a-3/4 recordkeeping requirements through unified audit trail"
- Recommend: Configure Application Insights retention to meet regulatory retention periods (3-6 years)
- Map agent activity logs to SEC 17a-4's "communications" definition

**Source:** [SEC Rule 17a-4: Electronic Recordkeeping](https://www.sec.gov/investment/amendments-electronic-recordkeeping-requirements-broker-dealers)

### OCC 2011-12 / Fed SR 11-7 (Model Risk Management)

**How Agent 365 Helps:**

- **Comprehensive Inventory:** Agent 365 unified registry provides single source of truth for all agents (supports OCC 2011-12's model inventory mandate)
- **Rich Metadata:** Registry captures business purpose, data sources, risk ratings, and approval status (supports model governance)
- **Lifecycle Management:** Promotion gates enforce formal approval workflows before agents move to production (supports model validation requirements)
- **Ongoing Monitoring:** Observability and security posture dashboard enable continuous monitoring (supports OCC 2011-12's ongoing monitoring requirement)

**Documentation Approach:**
- Map Agent 365 unified registry to OCC 2011-12's "model inventory" requirement
- Note: "Agent 365 lifecycle management supports OCC 2011-12's three-line defense: development (owners), validation (sponsors + AI Governance Committee), ongoing monitoring (observability)"
- Recommend: Tag agents with OCC risk ratings (low/medium/high) using custom metadata

**Source:** [OCC Bulletin 2011-12: Model Risk Management](https://www.occ.treas.gov/news-issuances/bulletins/2011/bulletin-2011-12.html)

### SOX 302/404 (Internal Controls)

**How Agent 365 Helps:**

- **Change Management:** Agent 365 promotion gates enforce approval workflows and separation of duties
- **Access Control:** Entra Agent ID Conditional Access policies enforce risk-based access control for agents
- **Audit Trail:** Unified activity logs support SOX audit evidence collection
- **Configuration Baselines:** Agent 365 templates (default and custom) enforce security baselines

**Documentation Approach:**
- Map Agent 365 promotion gates to SOX 302's change management controls
- Note: "Agent 365 lifecycle management supports SOX 302 internal controls through enforced approval workflows"
- Recommend: Custom templates for Zone 3 agents with full governance policies

**Source:** Sarbanes-Oxley Act Sections 302 and 404

### GLBA 501(b) (Safeguards Rule)

**How Agent 365 Helps:**

- **Access Control:** Entra Agent ID Conditional Access policies enforce authentication requirements
- **Monitoring:** Agent 365 Observability enables continuous monitoring of agent activity
- **Encryption:** Agent 365 integrates with Microsoft's encryption-at-rest and encryption-in-transit
- **Risk Assessment:** Security posture dashboard identifies misconfigurations and policy violations

**Documentation Approach:**
- Map Entra Agent ID Conditional Access to GLBA 501(b)'s access control requirements
- Note: "Agent 365 security posture management supports GLBA 501(b) safeguards through continuous monitoring and risk assessment"
- Recommend: Phishing-resistant MFA for Zone 3 agent creators and sponsors

**Source:** Gramm-Leach-Bliley Act Section 501(b)

---

## Sources

### Primary (HIGH confidence - GA Features)

**Microsoft Learn - Entra Agent ID:**
- [Microsoft Entra Agent ID Overview](https://learn.microsoft.com/en-us/entra/agent-id/)
- [What is Microsoft Entra Agent ID?](https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents)
- [Overview of Agent Identities in Microsoft Entra](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-identities)
- [Administrative Relationships in Microsoft Entra Agent ID (Owners, Sponsors, Managers)](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-owners-sponsors-managers)
- [Governing Agent Identities (Preview)](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview)
- [Agent Identity Sponsor Tasks in Lifecycle Workflows (Preview)](https://learn.microsoft.com/en-us/entra/id-governance/agent-sponsor-tasks)
- [Conditional Access for Agent Identities in Microsoft Entra](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id)
- [Conditional Access for High-Risk Agent Identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-agent-block-high-risk)

**Microsoft Learn - M365 Admin Center:**
- [Agent Settings in Microsoft 365 Admin Center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-settings)
- [Agent Registry in Microsoft 365 Admin Center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry)
- [Agent 365 Overview Page in Microsoft 365 Admin Center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview)
- [Manage Copilot Agents in Microsoft 365 Admin Center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps)
- [Share and Manage Agents Built with Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-builder-share-manage-agents)

### Secondary (MEDIUM confidence - Preview Features)

**Microsoft Learn - Agent 365 (Preview):**
- [Agent 365 Blueprint (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-blueprint)
- [Agent 365 Deployment Checklist (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-checklist)
- [Agent 365 Identity (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/identity)
- [Agent 365 Observability (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/observability)
- [Agent Observability Schema Reference](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/reference/observability-schema/)
- [Microsoft 365 Copilot Agents Admin Guide](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-admin-guide)

**Microsoft Official Blogs:**
- [Microsoft Agent 365: The Control Plane for AI Agents](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-agent-365-the-control-plane-for-ai-agents/)
- [New Capabilities for AI Admins from Ignite 2025](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/new-capabilities-for-ai-admins-from-ignite-2025/4478906)
- [Four Priorities for AI-Powered Identity and Network Access Security in 2026](https://www.microsoft.com/en-us/security/blog/2026/01/20/four-priorities-for-ai-powered-identity-and-network-access-security-in-2026/)
- [A New Era of Agents, a New Era of Posture](https://www.microsoft.com/en-us/security/blog/2026/01/21/new-era-of-agents-new-era-of-posture/)

### Regulatory Sources

- [FINRA Rule 3110: Supervision](https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110)
- [SEC Rule 17a-4: Electronic Recordkeeping Requirements](https://www.sec.gov/investment/amendments-electronic-recordkeeping-requirements-broker-dealers)
- [OCC Bulletin 2011-12: Model Risk Management](https://www.occ.treas.gov/news-issuances/bulletins/2011/bulletin-2011-12.html)
- [Federal Reserve SR 11-7: Model Risk Management](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm)

### Community Sources (Supporting Context)

- [Secure AI Agents with Microsoft Entra Agent ID (Dave R - Microsoft Azure MVP)](https://itnext.io/secure-ai-agents-with-microsoft-entra-agent-id-identity-governance-and-conditional-access-at-c1c23cd4ac8a)
- [Microsoft Agent 365: Unified Control Plane to Manage Agents (AdminDroid)](https://blog.admindroid.com/microsoft-agent-365-unified-control-plane-to-manage-ai-agents/)

---

## Metadata

**Confidence breakdown:**

- **Entra Agent ID architecture:** HIGH - GA features, official Microsoft Learn documentation
- **Agent 365 unified control plane:** MEDIUM - Preview features, subject to change before GA
- **M365 Admin Center Agent Settings:** HIGH - GA features, official Microsoft Learn documentation
- **Control impact analysis:** HIGH - Based on existing FSI-AgentGov control files and grep analysis
- **FSI regulatory alignment:** HIGH - Based on official regulatory sources (FINRA, SEC, OCC)
- **Migration roadmap:** MEDIUM - Preview features require Frontier enrollment; GA timeline estimated

**Research date:** 2026-02-05

**Valid until:** 30 days for GA features (stable), 7 days for preview features (fast-moving)

**Next review:** After Agent 365 GA announcement (expected Q1-Q2 2026)
