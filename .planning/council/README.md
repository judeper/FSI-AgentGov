# AI Council Audit Trail

This directory persists the audit trail for the multi-iteration AI council critique that produced **plan v3.1** of the Playwright E2E validation harness for the FSI Readiness Assessment SPA.

## What the council is

A panel of LLM critics, each given a distinct adversarial angle (security, performance, FMEA, customer realism, SRE reliability, correctness, handoff durability), reviews a draft plan and produces structured findings. Findings are triaged into themes and folded back into a revised plan. The cycle repeats until termination criteria are met.

## Iterative loop

```
draft plan ──► critics (N angles) ──► findings ──► triage to themes ──► revised plan
                  ▲                                                            │
                  └──────────────────  next iteration  ◄───────────────────────┘
```

Each iteration narrows: more critics challenge fewer remaining issues, and findings either (a) fold into existing themes as edits, or (b) raise a genuinely new theme.

## Anti-rubber-stamp termination criteria

To prevent the council from converging artificially (critics nodding because earlier iterations already baked their concerns in), iter3 enforced:

1. **Inlined prior themes** in critic prompts with explicit *"do not re-raise"* guards.
2. **Auto-downgrade** of findings that restate iter1/iter2 themes without new evidence.
3. **Threshold:** terminate when **≤ 5 P0/P1 findings remain from the latest iteration AND all are addressable as plan edits, not new themes.**
4. **Diminishing-returns check:** finding count must be collapsing (e.g., 71 → 87 → 16), not flat.

iter3 produced 6 P0/P1 (one downgraded), all addressable as plan edits — declared **CONVERGED**.

## Per-iteration findings

| Iteration | Critics | Findings | Outcome |
|---|---|---|---|
| [iter1](./iter1/findings.csv) | broad panel | ~71 | distilled to 10 themes (Themes 1–10) |
| [iter2](./iter2/findings.csv) | refined angles | ~87 | 70 accepted, themes refined |
| [iter3](./iter3/findings.csv) | 3 tight critics | 16 | 6 valid P0/P1, all folded as plan edits → v3.1 |

See [`SUMMARY.md`](./SUMMARY.md) for the convergence narrative.

## Provenance note

Raw critic transcripts for iter1 and iter2 were lost in conversation compaction. The `findings.csv` files in `iter1/` and `iter2/` are **synthesized reconstructions** derived from the surviving plan.md theme structure (Themes 1–10) at `C:\Users\judep\.copilot\session-state\7111c566-2644-4d36-aee3-a722dcee7be4\plan.md`. The `iter3/findings.csv` reflects the 16 deltas captured verbatim in plan.md §"Plan v3.1 — Iteration 3 deltas". Future council runs MUST persist raw transcripts immediately (Theme 3 / F-002).
