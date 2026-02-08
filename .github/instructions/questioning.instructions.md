---
applyTo: ".planning/**"
---

# Adaptive Questioning Patterns

When gathering context for GSD workflows (research, planning, discussion), use adaptive questioning to extract maximum information with minimum friction.

## Principles

1. **Start broad, narrow based on responses** — Don't ask for details before understanding scope
2. **Offer options with an escape hatch** — Give concrete choices but always allow "something else"
3. **Build on prior answers** — Reference what was already discussed
4. **Respect the user's time** — If you can infer the answer from context, don't ask

## Phase Discussion Pattern

When running `/discuss-phase`:

1. **Open with understanding:** "Based on the roadmap, Phase N focuses on [X]. Here's what I understand..."
2. **Identify gaps:** "I need clarity on these aspects: [specific questions]"
3. **Offer approaches:** "I see two approaches: A) [option] or B) [option]. Which aligns better?"
4. **Confirm scope:** "So the phase will deliver [list]. Anything to add or remove?"

## Research Question Pattern

When running `/research-phase`:

1. **State what you know** from existing project context
2. **Identify what you need** to research externally
3. **Propose a research plan** and confirm before executing
4. **Report findings** with confidence levels (HIGH/MEDIUM/LOW)

## Context-Aware Questioning

Before asking a question:
1. Check `.planning/STATE.md` for recent decisions
2. Check `.planning/PROJECT.md` for key decisions table
3. Check the current phase's RESEARCH.md if it exists
4. Only ask if the answer isn't already documented
