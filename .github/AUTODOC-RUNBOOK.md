# Autodoc Pipeline Runbook (maintainer-only)

> Operations + provisioning for the **autonomous Learn Monitor documentation pipeline**
> (Stage 1). This is internal tooling documentation; it is **not** part of the published
> docs site. Customer-facing description lives in
> [`docs/reference/learn-monitor-ai-enhancement.md`](../docs/reference/learn-monitor-ai-enhancement.md).

> **Status — mid-pivot.** The pipeline is being moved off GitHub's cloud coding agent
> (which cannot run here: the enterprise Copilot license is on an EMU account barred from
> this public personal repo, and GitHub disallows cloud-agent **automations on public
> repositories**) and onto a **local, unattended GitHub Copilot CLI drafter**. This runbook
> documents the **current** (Phase 1) state. Sections marked **(forthcoming)** describe
> components that are not built yet — do not provision them.

## What it does

When enabled, the pipeline turns Microsoft Learn documentation changes into drafted doc
edits, **independently verified** before a human merges them. It is **fail-closed** and
**off by default** (`AUTODOC_ENABLED` repo variable).

```
learn-monitor.yml (daily)
  └─ detect changes → reports/monitoring/learn-changes-*.md + state PR (auto-merges, state-only)
        │
        ▼  local Copilot CLI runner  (forthcoming — Phase 2; gated by AUTODOC_ENABLED)
   classify each change (scripts/autodoc_classifier.py via scripts/autodoc_route.py, fail-closed):
     • route=autodraft → draft the edit with Copilot CLI (headless), then verify  ─┐
     • route=human     → open a human escalation issue (no agent)                  │
        │                                                                          │
        ▼  deterministic verifier (scripts/autodoc_verify.py) + bounded fix loop   │
        ▼  independent cross-model review (forthcoming — a DIFFERENT Copilot model │
           family via scripts/autodoc_cli_review.py); both must pass, fail-closed  │
        │ pass → open PR → HUMAN merges (CODEOWNERS)   │ repeated fail → escalate ──┘
        ▼
   [backstop] autodoc-verify.yml — deterministic-only required check on autodoc PRs,
              shim-aware (reports success on normal PRs), hardened pull_request_target
```

## Components

### Implemented (merged to `main`, inert until `AUTODOC_ENABLED=true`)

| Component | File | Role |
|-----------|------|------|
| Classifier | `scripts/autodoc_classifier.py` | Deterministic, fail-closed routing (autodraft vs human); `automerge_eligible` is **redirect-only** |
| Canary | `scripts/autodoc_canary.py` | Poison-pill guard; asserts known-bad samples are **never auto-merge-eligible** (most also route to human) and halts routing if one is mis-promoted |
| Router / contract builder | `scripts/autodoc_route.py` | Builds the per-change authoring contract (allowed files/headings, fingerprint); fingerprint-idempotent via `data/autodoc-ledger.json` |
| Deterministic verifier | `scripts/autodoc_verify.py` | Path/section allowlist, diff-minimality, claim-support, FSI language; CommonMark heading parsing (markdown-it-py) |
| Verify gate (CI backstop) | `scripts/autodoc_verify_gate.py` + `.github/workflows/autodoc-verify.yml` | **Deterministic-only** required check `autodoc-verify`; shim-aware; hardened `pull_request_target` |
| Retry/escalation decision | `scripts/autodoc_retry.py` | Offline, fail-closed decision logic (bounded retry vs escalate) reused by the runner |
| Baseline-deferral ledger (F5) | `scripts/autodoc_defer.py` + `scripts/autodoc_advance.py` + `.github/workflows/learn-monitor-advance.yml` | Advances the monitor baseline only when the downstream doc task is terminal; **byte-identical no-op** unless `AUTODOC_ENABLED=true` |

### Forthcoming (the local drafter — Phases 2–3, not built yet)

| Component | File | Role |
|-----------|------|------|
| Cross-model reviewer | `scripts/autodoc_cli_review.py` | Independent review by a **different** GitHub Copilot model family (replaces the retired third-party LLM verifier) |
| Unattended runner | `scripts/autodoc_local_runner.ps1` | Reads pending changes → drafts via Copilot CLI headless → deterministic verify + fix loop → cross-model review → opens PR via the `judeper` token |
| Scheduler | `scripts/Register-AutodocTask.ps1` | Registers a Windows Scheduled Task that runs the runner after the daily monitor |

## Safety model (do not weaken without review)

- **Fail-closed everywhere.** Classifier defaults to `human`; the deterministic verifier and
  the (forthcoming) cross-model review default to fail / `needs_human` — never a silent pass.
- **Humans merge content.** Stage 1 is "agent drafts → verify → **human merges**" (CODEOWNERS).
  `automerge_eligible` is **redirect-only**; no content change auto-merges.
- **Regulatory/compliance is triage-only** and never auto-authored.
- **Master kill-switch:** set `AUTODOC_ENABLED=false` (or unset) → the whole pipeline is inert.
  Stage-0 state-PR auto-merge has its own switch (`LEARN_STATE_AUTOMERGE`).
- **Account model:** the Copilot CLI reasons on the **EMU license** (`judep_microsoft`); all
  git/PR writes go through the **`judeper`** token — independent auths, no mid-run switching.

## Provisioning (run as `judeper`, repo admin). Pipeline stays OFF until the last step.

Phase 1 leaves almost nothing to provision — the drafter that would consume secrets is not
built yet. **Autodoc no longer uses `ANTHROPIC_API_KEY` or `COPILOT_ASSIGN_TOKEN`** (both were
tied to the retired cloud-agent design). Note: `COPILOT_ASSIGN_TOKEN` is **still used by the
separate Squad workflows** (`squad-issue-assign.yml`, `squad-heartbeat.yml`) — do **not**
remove that repo secret.

1. **(Optional, backstop) Require the deterministic gate.** After `autodoc-verify.yml` has run
   once, add `autodoc-verify` to `main` branch protection → Require status checks. It is
   shim-aware and reports success on normal PRs, so it will not block them.
2. **Keep it off.** Leave `AUTODOC_ENABLED` unset/`false` until the local runner lands and you
   are ready for a verification run.

**Forthcoming (Phase 3) — runner provisioning** will be: ensure the Copilot CLI is logged in
as `judep_microsoft` (the active license); ensure `gh`/git `judeper` credentials are available
to the scheduled task; register the task (`Register-AutodocTask.ps1`); then flip the switch:

```bash
gh variable set AUTODOC_ENABLED --repo judeper/FSI-AgentGov --body "true"
# kill-switch:
gh variable set AUTODOC_ENABLED --repo judeper/FSI-AgentGov --body "false"
```

## Operations

- **Disable immediately:** `gh variable set AUTODOC_ENABLED ... --body "false"` (and/or disable
  the scheduled task once it exists).
- **A draft escalated to you:** look for issues/PRs labeled `escalate` + `needs-review`. Review
  / fix / merge manually.
- **Canary failed:** routing halts and opens an `escalate` issue — the classifier mis-promoted
  a poison sample; do not enable until investigated.
- **Audit trail:** every change has a stable `AUTODOC-FINGERPRINT`; `data/autodoc-ledger.json`
  records routed changes; verifier verdicts appear on the PR.
