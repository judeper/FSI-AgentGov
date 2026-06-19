# Autodoc Pipeline Runbook (maintainer-only)

> Operations + provisioning for the **autonomous Learn Monitor documentation pipeline**
> (Stage 1). This is internal tooling documentation; it is **not** part of the published
> docs site. Customer-facing description lives in
> [`docs/reference/learn-monitor-ai-enhancement.md`](../docs/reference/learn-monitor-ai-enhancement.md).

## What it does

When enabled, the pipeline turns Microsoft Learn documentation changes into drafted doc
edits, **independently verified** before a human merges them. It is **fail-closed** and
**off by default** (`AUTODOC_ENABLED` repo variable).

```
learn-monitor.yml (daily)
  └─ detect changes → reports/monitoring/learn-changes-*.md + state PR (auto-merges, state-only)
        │
        ▼  [W1] learn-autodoc-route.yml   (gated by AUTODOC_ENABLED)
   classify each change (scripts/autodoc_classifier.py, fail-closed) → open issues:
     • route=autodraft → labels autodoc + squad:copilot  ─┐
     • route=human     → labels autodoc + escalate         │ (human analyses; no agent)
        │                                                   │
        ▼ (existing squad-issue-assign.yml assigns the     │
           Copilot coding agent on the squad:copilot label)│
   Copilot coding agent → copilot/* PR with the doc edit   │
        │                                                   │
        ▼  [W2] autodoc-verify.yml  (required check "autodoc-verify", shim-aware)
   deterministic verifier (scripts/autodoc_verify.py) AND cross-vendor LLM verifier
   (scripts/autodoc_llm_verify.py, Anthropic Claude) — BOTH must pass; fail-closed
        │ pass → HUMAN merges (CODEOWNERS)        │ fail / needs_human
        ▼                                          ▼  [W4] autodoc-fix-retry.yml
   (Stage 2, deferred: content auto-merge)    bounded retry (≤ AUTODOC_MAX_FIX_CYCLES)
                                              then escalate to a human (fail-closed)
```

## Components (all merged to `main`, inert until `AUTODOC_ENABLED=true`)

| Component | File | Role |
|-----------|------|------|
| Classifier | `scripts/autodoc_classifier.py` | Deterministic, fail-closed routing (autodraft vs human); `automerge_eligible` is **redirect-only** |
| Canary | `scripts/autodoc_canary.py` | Poison-pill guard; asserts known-bad samples are **never auto-merge-eligible** (most also route to human) and halts routing if one is mis-promoted |
| Router | `scripts/autodoc_route.py` + `.github/workflows/learn-autodoc-route.yml` | Opens autodraft / human issues with the authoring contract; fingerprint-idempotent via `data/autodoc-ledger.json` |
| Deterministic verifier | `scripts/autodoc_verify.py` | Path/section allowlist, diff-minimality, claim-support, FSI language; CommonMark heading parsing (markdown-it-py) |
| LLM verifier | `scripts/autodoc_llm_verify.py` | Anthropic Claude faithfulness check (cross-vendor from the GPT-based author); fail-closed |
| Verify gate | `scripts/autodoc_verify_gate.py` + `.github/workflows/autodoc-verify.yml` | Required check `autodoc-verify`; shim-aware; hardened `pull_request_target` |
| Fix-retry/escalation | `scripts/autodoc_retry.py` + `.github/workflows/autodoc-fix-retry.yml` | Bounded retry, then human escalation |

## Safety model (do not weaken without review)

- **Fail-closed everywhere.** Classifier defaults to `human`; verifiers default to fail /
  `needs_human`; missing `ANTHROPIC_API_KEY` → `needs_human` (never a silent pass).
- **Humans merge content.** Stage 1 is "agent drafts → verify → **human merges**" (CODEOWNERS).
  `automerge_eligible` is **redirect-only**; no content change auto-merges.
- **Regulatory/compliance is triage-only** and never auto-authored.
- **Master kill-switch:** set `AUTODOC_ENABLED=false` (or unset) → the whole pipeline is inert.
  Stage-0 state-PR auto-merge has its own switch (`LEARN_STATE_AUTOMERGE`).

## Provisioning (run as `judeper`, repo admin). Pipeline stays OFF until the last step.

1. **Enable the Copilot coding agent** for `judeper/FSI-AgentGov` (repo Settings → Copilot →
   Coding agent, or the org Copilot settings). Confirm your plan includes the coding agent.
2. **Grant the existing GitHub App** (`APP_CLIENT_ID`) these repo permissions if missing:
   Contents R/W, Pull requests R/W, **Issues R/W**, **Actions R/W**; re-accept on the installation.
3. **Anthropic key:**
   ```bash
   gh secret set ANTHROPIC_API_KEY --repo judeper/FSI-AgentGov --body "<anthropic-key>"
   ```
4. **One fine-grained PAT** (judeper-owned, scoped to this repo; Issues/PRs/Contents/Actions
   R/W + Copilot coding-agent permission) → covers agent assignment, the agent-tasks retry
   API, and workflow approval:
   ```bash
   gh secret set COPILOT_ASSIGN_TOKEN --repo judeper/FSI-AgentGov --body "<fine-grained-PAT>"
   ```
5. **After `autodoc-verify.yml` has run once**, add `autodoc-verify` to `main` branch
   protection → Require status checks. (Shim-aware: it reports success on normal PRs.)
6. **Optional:** set `AUTODOC_MAX_FIX_CYCLES` (default 2).
7. **GO LIVE / for a verification run:**
   ```bash
   gh variable set AUTODOC_ENABLED --repo judeper/FSI-AgentGov --body "true"
   # kill-switch:
   gh variable set AUTODOC_ENABLED --repo judeper/FSI-AgentGov --body "false"
   ```

**Minimum for a first end-to-end test:** steps 1 + 3 + 4 + 7. The LLM verifier fails closed
without the key, so nothing auto-proceeds unsafely.

## Operations

- **Disable immediately:** `gh variable set AUTODOC_ENABLED ... --body "false"`.
- **A draft escalated to you:** look for issues/PRs labeled `escalate` + `needs-review`
  (the agent has been un-assigned; `squad:copilot` removed). Review/fix/merge manually.
- **Canary failed:** routing halts and opens an `escalate` issue — the classifier mis-promoted
  a poison sample; do not enable until investigated.
- **Audit trail:** every change has a stable `AUTODOC-FINGERPRINT`; `data/autodoc-ledger.json`
  records routed changes; verifier verdicts appear on the PR.

## Deferred: F5 idempotency baseline-deferral

The "don't advance the monitor baseline until the downstream doc task is terminal" change
(F5) was **deliberately deferred**: the silent-drop risk it guards is already mitigated
because every detected change opens a tracking **issue** that persists regardless of the
state baseline, and the F5 change would modify `learn_monitor.py` which runs **daily
regardless of the kill-switch** (risk to the live monitor for low marginal benefit).
Revisit only if real operation shows changes being lost despite the issue ledger.
