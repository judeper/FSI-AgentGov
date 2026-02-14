# Codebase Analysis: Architecture

**Generated:** 2026-02-11
**Scope:** Full repository architecture analysis

## Summary

FSI-AgentGov is a documentation-centric governance framework (v1.2.41) for Microsoft 365 AI agents in US financial services, built with MkDocs Material and published to GitHub Pages. The repository implements a rigorous three-layer documentation model (Framework -> Controls -> Playbooks) spanning 71 controls across 4 pillars, with 284 playbook files providing step-by-step implementation guidance. A companion repository (FSI-AgentGov-Solutions) houses 25 deployable Power Platform solutions.

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| docs/ | All publishable documentation content (MkDocs source) |
| scripts/ | Validation, monitoring, and maintenance scripts (Python/PowerShell) |
| src/ | Adaptive card and Power Automate flow JSON definitions |
| data/ | Runtime state (learn-monitor-state.json) |
| releases/ | Release artifacts by version |
| reports/ | Generated documentation review and learn-changes reports |
| site/ | MkDocs build output (generated) |
| maintainers-local/ | Local-only maintainer artifacts (gitignored) |
| .planning/ | GSD project management workflow state |
| .github/ | Copilot agents, prompts, instructions, CI workflows |

## Three-Layer Documentation Model

- **Layer 1 (Framework):** 12 files in docs/framework/ - governance principles, strategy, organizational context (WHY)
- **Layer 2 (Controls):** 62 files across 4 pillar directories - technical specifications with 10-section format (WHAT)
- **Layer 3 (Playbooks):** 251 files in docs/playbooks/ - step-by-step implementation procedures (HOW)

**Linkage:** Controls link to playbooks via Section 8. Playbooks link back to parent controls. Framework docs provide conceptual context.

## Control Organization

| Pillar | Count | Focus |
|--------|-------|-------|
| Pillar 1 - Security | 24 | DLP, encryption, access control, audit logging |
| Pillar 2 - Management | 21 | Environments, change management, testing, risk |
| Pillar 3 - Reporting | 10 | Inventory, analytics, compliance reporting |
| Pillar 4 - SharePoint | 7 | Content governance, access reviews, grounding |

## Navigation (mkdocs.yml - 598 lines)

Home > Disclaimer > Getting Started (2) > Framework (12) > Control Catalog (62) > Playbooks (251) > Reference (19) > Downloads (6)

## Multi-Agent Architecture

- 13 custom Copilot agents in .github/agents/
- 28 prompt files in .github/prompts/
- 12 instruction files in .github/instructions/
- 5 Claude Code skills in .claude/skills/
- Session ownership protocol via .planning/STATE.md

## Planning Infrastructure

47 phase directories under .planning/phases/ from v1-v11 development history. 18 milestone archives in .planning/milestones/.

## Recommendations

1. Archive completed phase directories to reduce 47-directory sprawl
2. Playbook count (251) exceeds documented 248 - update references
3. Confirm excluded docs (CONTROL-INDEX.md, regulatory-mappings.md, raci-matrix.md) don't create dead links
4. Solutions integration bidirectional linking is well-implemented
