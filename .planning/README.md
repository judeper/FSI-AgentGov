# .planning/ — GSD Planning State

This directory contains working state for the **GSD (Get Stuff Done) planning framework**, used by AI coding agents to coordinate documentation and governance work on the FSI Agent Governance Framework.

## Purpose

The GSD framework tracks project phases, research, execution plans, and verification results. It provides structured workflow management so that autonomous agents can plan, execute, and verify changes systematically.

## Multi-Agent Coordination

This directory supports coordination between three AI tools:

- **GitHub Copilot** — Documentation writing and GSD workflows
- **Claude Code** — Verification, QA, and GSD workflows
- **Codex CLI** — Documentation generation

Session ownership is managed through `STATE.md` to prevent write conflicts. See [`AGENTS.md`](../AGENTS.md) in the repository root for the full multi-agent protocol.

## Key Files

| File | Purpose |
|------|---------|
| `PROJECT.md` | Project identity, scope, and key decisions |
| `ROADMAP.md` | Phase breakdown with success criteria |
| `STATE.md` | Current position and session continuity |
| `REQUIREMENTS.md` | Requirements with traceability matrix |
| `config.json` | Workflow configuration (mode, depth, toggles) |
| `phases/` | Phase execution artifacts (plans, summaries, research, verification) |

## Why These Files Are Committed

These files are committed intentionally to enable session continuity across agent sessions. When an agent resumes work, it reads `STATE.md` and the relevant phase artifacts to restore context from prior sessions.

## Further Reading

- [`AGENTS.md`](../AGENTS.md) — Multi-agent coordination protocol and GSD structure
- [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) — Full repository context
