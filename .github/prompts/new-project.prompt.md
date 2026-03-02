---
name: "gsd-new-project"
description: "Initialize a new project with deep context gathering and PROJECT.md"
tools: ["read", "edit", "search", "execute", "agent", "web"]
---

<objective>
Initialize a new GSD project by gathering deep context through adaptive questioning and parallel research, then creating PROJECT.md with project identity, scope, and key decisions.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (project description or empty for interactive)

@.planning/PROJECT.md (if exists — extending existing project)
</context>

<process>

<step name="gather_context">
Use adaptive questioning to understand the project scope. Ask focused questions in batches of 2-3, not all at once.

**Round 1 — Identity:**
- What is being built? (feature, solution, documentation, integration)
- Who is the target user? (M365 admin, compliance officer, developer)
- What problem does this solve?

**Round 2 — Scope:**
- What are the must-have deliverables?
- What is explicitly out of scope?
- Are there regulatory requirements? (FINRA, SEC, SOX, GLBA, OCC)

**Round 3 — Constraints:**
- Technology constraints? (PowerShell, Dataverse, Power Automate, Graph API)
- Cross-repository? (FSI-AgentGov docs + FSI-AgentGov-Solutions artifacts)
- Timeline or milestone context? (which milestone in the v1-v9 series)

For FSI-AgentGov: much context is already established in PROJECT.md. When extending an existing project, focus questions on what's new or changed.
</step>

<step name="run_research">
Spawn 4 parallel researchers to investigate the domain ecosystem. Each researcher writes to `.planning/research/`.

**Dimension 1 — Technology Stack:**
```
Task(
  prompt="Research the technology stack for: {project_description}

    Focus on:
    - Microsoft 365 APIs and SDKs relevant to this project
    - PowerShell modules needed (Microsoft.Graph, ExchangeOnlineManagement, etc.)
    - Dataverse schema patterns from existing solutions
    - Power Automate connector availability
    - Authentication requirements (app-only vs delegated, required permissions)

    Write findings to: .planning/research/tech-stack.md",
  subagent_type="gsd-project-researcher",
  description="Research tech stack"
)
```

**Dimension 2 — Features and Capabilities:**
```
Task(
  prompt="Research feature requirements for: {project_description}

    Focus on:
    - What existing FSI-AgentGov controls relate to this project
    - What existing solutions in FSI-AgentGov-Solutions can be reused
    - Feature gaps that need new development
    - User workflows that must be supported
    - Reporting and alerting requirements

    Write findings to: .planning/research/features.md",
  subagent_type="gsd-project-researcher",
  description="Research features"
)
```

**Dimension 3 — Architecture Patterns:**
```
Task(
  prompt="Research architecture patterns for: {project_description}

    Focus on:
    - Existing solution patterns (Tier 2: PowerShell + Dataverse + Power Automate)
    - ACV v4 pattern as reference architecture
    - Cross-repository integration (docs in FSI-AgentGov, code in FSI-AgentGov-Solutions)
    - Dataverse table design patterns (org-owned vs user-owned, option set reuse)
    - Power Automate flow patterns (Scope_Try/Scope_Catch, adaptive cards)
    - Deployment orchestration patterns (deploy.py with selective flags)

    Write findings to: .planning/research/architecture.md",
  subagent_type="gsd-project-researcher",
  description="Research architecture"
)
```

**Dimension 4 — Pitfalls and Risks:**
```
Task(
  prompt="Research pitfalls and risks for: {project_description}

    Focus on:
    - Common failure modes in similar Microsoft 365 governance projects
    - Regulatory compliance risks (FINRA record retention, SOX change control)
    - API limitations, throttling, deprecation timelines
    - Cross-solution dependency risks (shared option sets, connection references)
    - Deployment risks (report-only bake periods, break-glass exclusions)
    - Lessons learned from previous milestones (check .planning/research/SUMMARY.md)

    Write findings to: .planning/research/pitfalls.md",
  subagent_type="gsd-project-researcher",
  description="Research pitfalls"
)
```

**Wait for all 4 researchers to complete**, then synthesize:

```
Task(
  prompt="Synthesize research outputs from 4 parallel researchers.

    Read these files:
    - .planning/research/tech-stack.md
    - .planning/research/features.md
    - .planning/research/architecture.md
    - .planning/research/pitfalls.md

    Create a unified summary with:
    - Key findings across all dimensions
    - Architecture recommendations
    - Pitfalls to avoid with specific prevention mechanisms
    - Confidence assessment per topic
    - Recommended phase sequencing

    Write to: .planning/research/SUMMARY.md",
  subagent_type="gsd-research-synthesizer",
  description="Synthesize research"
)
```
</step>

<step name="create_project">
Create or update `.planning/PROJECT.md` using this template:

```markdown
# Project: {Name}

**Created:** YYYY-MM-DD
**Milestone:** v{N} — {Name}
**Status:** Initialized

## Project Identity

**What:** {One-sentence description}
**Who:** {Target audience}
**Why:** {Problem being solved}

## Scope

### In Scope
- {Deliverable 1}
- {Deliverable 2}

### Out of Scope
- {Explicitly excluded item 1}

## Key Decisions

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | {decision} | {why} | YYYY-MM-DD |

## Technology Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Scripts | PowerShell 7+ | Microsoft.Graph module |
| Data | Dataverse | {table design notes} |
| Automation | Power Automate | {flow patterns} |
| Documentation | MkDocs Material | Strict build validation |

## Regulatory Context

| Regulation | Relevance | Controls |
|-----------|-----------|----------|
| {FINRA 4511} | {how it applies} | {control IDs} |

## Cross-Repository

| Repository | Contains | Path |
|-----------|----------|------|
| FSI-AgentGov | Documentation, framework | C:/dev/FSI-AgentGov |
| FSI-AgentGov-Solutions | Deployable artifacts | C:/dev/FSI-AgentGov-Solutions |

## Research Summary

{Key findings from synthesized research — link to .planning/research/SUMMARY.md}
```

Initialize `.planning/config.json` if it doesn't exist:
```json
{
  "project_name": "{name}",
  "mode": "careful",
  "depth": "standard",
  "parallelization": true,
  "model_profile": "balanced",
  "workflow": {
    "research": true,
    "plan_check": true,
    "verifier": true
  },
  "commit_docs": true
}
```
</step>

<step name="initialize_state">
Create or update `.planning/STATE.md` with initial project state:
- Set milestone name and status
- Initialize progress tracker
- Record session start
</step>

<step name="offer_next">
```
## Project Initialized

**{Project Name}** — ready for milestone planning

Research completed: {topic_count} topics, {confidence} overall confidence
Key risk: {top_risk_from_pitfalls}

`/gsd-new-milestone` — Define the first milestone and create ROADMAP.md
```
</step>

</process>

<success_criteria>
- [ ] User context gathered through adaptive questioning
- [ ] 4 parallel research dimensions completed
- [ ] Research synthesized into SUMMARY.md
- [ ] PROJECT.md created with full project identity
- [ ] config.json initialized with workflow settings
- [ ] STATE.md updated with project state
</success_criteria>
