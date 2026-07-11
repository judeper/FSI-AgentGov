# Autodoc Pipeline Runbook (maintainer-only)

> Operations + provisioning for the **autonomous Learn Monitor documentation pipeline**
> (Stage 1). Internal tooling documentation — **not** part of the published docs site.
> Customer-facing description lives in
> [`docs/reference/learn-monitor-ai-enhancement.md`](../docs/reference/learn-monitor-ai-enhancement.md).

The pipeline turns Microsoft Learn documentation changes into **drafted** doc edits,
**independently verified** by a different model before **OceanSquad reviews and
SHA-pinned merges** them. The owner is involved only after final automation escalation. It is
**fail-closed** and **off by default**. The drafter is the **local GitHub Copilot CLI** run
on a schedule — not GitHub's cloud coding agent (which can't run here: the enterprise Copilot
license is on an EMU account barred from this public personal repo, and GitHub disallows
cloud-agent automations on public repositories).

```
learn-monitor.yml (daily)
  └─ detect changes → reports/monitoring/learn-changes-*.md + state PR (auto-merges, state-only)
        │
        ▼  scripts/autodoc_runner.py   (scheduled task; no-op unless AUTODOC_ENABLED=true)
   route each change (autodoc_route → autodoc_classifier, fail-closed) IN A DISPOSABLE WORKTREE:
     • route=autodraft → draft with Copilot CLI (headless, --draft-model)            ─┐
     • route=human     → open a human escalation issue (no draft)                     │
        │                                                                             │
        ▼  deterministic verify (autodoc_verify_gate) + bounded fix loop             │
        ▼  independent cross-model review (autodoc_cli_review, --review-model =       │
        │  a DIFFERENT Copilot family); BOTH must pass, fail-closed                    │
        │ pass → push (judeper) → open PR → OceanSquad review/merge    │ repeat fail → owner escalation ─┘
        ▼
   [backstop] autodoc-verify.yml — deterministic-only required check on autodoc PRs,
              shim-aware (success on normal PRs), hardened pull_request_target
```

## Components (all implemented; inert until enabled)

| Component | File | Role |
|-----------|------|------|
| Classifier | `scripts/autodoc_classifier.py` | Deterministic, fail-closed routing (autodraft vs human); `automerge_eligible` is **redirect-only** |
| Canary | `scripts/autodoc_canary.py` | Poison-pill guard; deterministic checks always run before routing. The existing cross-model review API is wired through a fail-closed adapter, but live model activation remains opt-in (`AUTODOC_CANARY_CROSS_MODEL_ENABLED=true`) so tests stay offline |
| Router / contract builder | `scripts/autodoc_route.py` | Builds the per-change authoring contract (allowed files/headings, fingerprint); fingerprint-idempotent via `data/autodoc-ledger.json` |
| Deterministic verifier | `scripts/autodoc_verify.py` | Path/section allowlist, diff-minimality, claim-support, FSI language; CommonMark heading parsing |
| Verify gate (CI backstop) | `scripts/autodoc_verify_gate.py` + `.github/workflows/autodoc-verify.yml` | **Deterministic-only** required check `autodoc-verify`; shim-aware; hardened `pull_request_target` |
| Cross-model reviewer | `scripts/autodoc_cli_review.py` | Independent faithfulness review by a **different** Copilot model family; strict fail-closed verdict parsing |
| Retry/escalation decision | `scripts/autodoc_retry.py` | Offline, fail-closed bounded-retry-vs-escalate decision logic |
| **Unattended runner** | `scripts/autodoc_runner.py` | Routes the latest report and, per autodraft change, drafts → verifies → cross-model-reviews → opens an OceanSquad-reviewed PR; runs in a **disposable git worktree**; idempotent via the ledger |
| **Scheduler** | `scripts/Register-AutodocTask.ps1` | Registers the daily Windows Scheduled Task that runs the runner |
| Baseline-deferral ledger (F5) | `scripts/autodoc_defer.py` + `scripts/autodoc_advance.py` + `.github/workflows/learn-monitor-advance.yml` | Advances the monitor baseline only when the downstream doc task is terminal; **byte-identical no-op** unless `AUTODOC_ENABLED=true` |
| Queue consolidation | `scripts/autodoc_consolidate.py` | Exact-source supersession planner/closer for stale sibling issues; **dry-run by default**, `--apply` performs `NOT_PLANNED` closes with audit comments |

## Safety model (do not weaken without review)

- **Fail-closed everywhere.** Classifier defaults to `human`; the deterministic verifier and the
  cross-model review default to fail / `needs_human` — never a silent pass. The reviewer rejects
  any non-conforming model output (extra keys, wrong types, multiple/echoed verdicts, etc.).
- **OceanSquad is the sole merge owner.** Routine verified documentation PRs are reviewed and
  SHA-pinned merged by OceanSquad after required checks. The owner reviews only final escalations.
  Target-native/agreement-ledger auto-merge remains disabled and observational.
- **Canonical redirect identity.** Known tracking parameters (`msockid`, `WT.mc_id`, `utm_*`,
  `ocid`) are stripped before matching, routing, fingerprinting, and PR generation. Functional
  query parameters and fragments are preserved. Redirect rows deduplicate by canonical source,
  while the canonical destination is part of the fingerprint so A→B and A→C remain distinct.
- **Regulatory/compliance is triage-only** and never auto-authored.
- **Isolation.** The runner drafts in a **disposable git worktree** (a fresh checkout of base with
  none of your ignored/local files), so an autonomous draft can never touch your main checkout.
- **Account model:** the Copilot CLI reasons on the **EMU license** (`judep_microsoft`); all git/PR
  writes go through the **`judeper`** token — independent auths, no mid-run switching.

## Two switches named `AUTODOC_ENABLED` (important)

| Switch | Where | Gates | Set with |
|--------|-------|-------|----------|
| **Local env var** | the machine running the scheduled task | the **runner** (`autodoc_runner.py` no-ops unless it is `true`) | `setx AUTODOC_ENABLED true` (user env; the task inherits it) |
| **Repo variable** | `judeper/FSI-AgentGov` Actions variables | the **CI verify gate** and F5 advance (`vars.AUTODOC_ENABLED`) | `gh variable set AUTODOC_ENABLED --repo judeper/FSI-AgentGov --body "true"` |

Both must be `true` to go fully live: the local env var lets the runner draft, and the repo variable
lets the resulting autodoc PRs pass the CI gate (the gate **fails** an autodoc PR while the repo
variable is not `true`). Either one set to non-`true` is a valid kill-switch.

## Provisioning (do as `judeper` where it writes to GitHub; the runner reasons on the EMU CLI login)

1. **Copilot CLI logged in** as `judep_microsoft` (the licensed account) on the machine that runs
   the task: `copilot` → `/login` if needed. This is the model entitlement; it is independent of
   the `gh` active account.
2. **`gh`/git `judeper` credentials available** to that user context. The runner pushes and opens
   PRs/issues as the **push account** (`-PushAccount`, default `judeper`); the task command resolves
   that account's token from the gh keyring at run time (via `gh auth token --user judeper`) and
   exposes it to both `git` and `gh` for the runner process only — so the machine's active EMU
   account never blocks the write. Verify `gh auth status` lists `judeper` and that
   `gh auth token --user judeper` returns a token.
3. **Create the labels the runner attaches** (one-time, idempotent). The runner labels its PRs
   `autodoc` and its escalation issues `autodoc` + `escalate`; a missing label fails the write
   (fail-closed). Create any that are absent:
   ```powershell
   gh label create autodoc --repo judeper/FSI-AgentGov --color 0E8A16 --description "Automated Learn Monitor documentation pipeline"
   gh label create escalate --repo judeper/FSI-AgentGov --color FBCA04 --description "Needs human review" 2>$null
   ```
4. **Register the scheduled task:**
   ```powershell
   ./scripts/Register-AutodocTask.ps1 -RepoPath C:\dev\FSI-AgentGov -DraftModel <draft-model> -ReviewModel <different-family-model>
   ```
   Pick a powerful draft model and a **different family** for review (e.g. an Opus/GPT/Gemini split).
   For another repo, pass `-PushAccount <owner>` if its writes use a different account.

   > **Dedicated checkout.** The task does **not** run against your working tree. The script clones a
   > dedicated checkout once (default sibling `C:\dev\FSI-AgentGov.autodoc`, override with
   > `-CheckoutPath`) and seeds its idempotency ledger from your repo. Each run the task hard-syncs
   > that checkout to `origin/main` (fetch + checkout + `reset --hard`, fail-closed) so the runner
   > always sees the latest **merged** Learn Monitor report, and never touches your branches or
   > uncommitted work. The runner's `data/autodoc-ledger.json` lives in that checkout (untracked, so it
   > survives the hard reset). Delete the checkout dir to force a fresh clone next registration.

   > The task reads the push account's token from the gh keyring at run time, so it must run in the
   > user's **interactive** context (the default — "run only when user is logged on"). If you switch
   > it to "run whether the user is logged on or not," the keyring/credential store is unreachable and
   > the task **fails closed** (it throws before the runner starts rather than writing as the wrong
   > account). For a fully headless host, supply a stored fine-grained PAT via `GH_TOKEN` instead.
5. **Required deterministic gates:** the committed `.github/branch-protection.json` preserves the
   live strict 11-check baseline and adds `autodoc-verify` plus `autodoc-redirect-verify`.
   `autodoc-verify` recognizes both `autodoc/*` and `copilot/*`; both checks self-shim on unrelated
   PRs. `mkdocs-strict` already validates internal links and anchors through MkDocs 1.6 validation,
   so no duplicate internal-link check is required. The network-dependent external-link workflow
   remains non-required.
6. **GO LIVE** — set BOTH switches (see the table above):
   ```powershell
   setx AUTODOC_ENABLED true                                                   # activates the runner
   gh variable set AUTODOC_ENABLED --repo judeper/FSI-AgentGov --body "true"   # activates the CI gate
   ```
   **Kill-switch:** `setx AUTODOC_ENABLED false` (stops new drafts) and/or
   `gh variable set AUTODOC_ENABLED --repo judeper/FSI-AgentGov --body "false"`; or
   `Unregister-ScheduledTask -TaskName 'FSI-AgentGov-Autodoc' -Confirm:$false`.

> There are **no `ANTHROPIC_API_KEY` / `COPILOT_ASSIGN_TOKEN` secrets** in this pipeline (both were
> retired with the cloud-agent design). Note `COPILOT_ASSIGN_TOKEN` is **still used by the separate
> Squad workflows** — do not remove that repo secret.

## Operations

- **Disable immediately:** flip either `AUTODOC_ENABLED` switch to non-`true`, or disable the task
  (`Disable-ScheduledTask -TaskName 'FSI-AgentGov-Autodoc'`).
- **Inspect:** `Get-ScheduledTask -TaskName 'FSI-AgentGov-Autodoc'`; run on demand with
  `Start-ScheduledTask -TaskName 'FSI-AgentGov-Autodoc'`; dry run with
  `python scripts/autodoc_runner.py --repo . --draft-model <m> --review-model <m> --dry-run` (with
  `AUTODOC_ENABLED=true` in the session).
- **Consolidate stale queue siblings (exact-source):** snapshot issues then run the
  consolidator in reviewed dry-run mode, then a guarded apply:
  `gh issue list --state all --label autodoc --json number,url,state,stateReason,body --limit 500 > autodoc-issues-all.json`
  then review the plan:
  `python scripts/autodoc_consolidate.py --issues-json autodoc-issues-all.json > autodoc-consolidate-plan.json`
  then capture reviewed guards from the plan:
  `python -c "import json; p=json.load(open('autodoc-consolidate-plan.json', encoding='utf-8')); print('count=', p['snapshot']['count']); print('sha256=', p['snapshot']['sha256']); print('closures=', p['summary']['closures_planned'])"`
  then apply with explicit guardrails:
  `python scripts/autodoc_consolidate.py --issues-json autodoc-issues-all.json --apply --expected-count <count> --expected-snapshot-sha256 <sha256> --max-closures <approved_ceiling>`
  (closes stale siblings as `NOT_PLANNED` with audit comments).
- **A draft escalated to you:** look for issues/PRs labeled `escalate` / `needs-review`; this is a
  final owner escalation after automation exhaustion. Escalation is idempotent (it reuses an
  existing issue for the same change).
- **Canary failed:** routing/CI halts on a poison sample mis-promotion — investigate before enabling.
- **Stale worktrees:** the task prunes them each run (`git worktree prune`); a crashed run may leave a
  `.autodoc-worktree-<pid>` dir next to the repo — safe to delete.
- **Audit trail:** every change carries a stable `AUTODOC-FINGERPRINT`; `data/autodoc-ledger.json`
  records routed changes; the cross-model review verdict appears in the PR body.

## Redirect agreement telemetry (observational; native auto-merge disabled)

The redirect agreement ledger records whether deterministic redirect PRs were merged as-is,
edited, closed, or later reverted. It remains useful calibration telemetry, but it cannot activate
GitHub native auto-merge: OceanSquad owns the only final merge path.

**What's built**
- **Independent CI gate** (`scripts/autodoc_redirect_ci_verify.py` + `.github/workflows/autodoc-redirect-verify.yml`):
  re-derives the clean-swap verdict from the actual PR diff on GitHub's side; runs on every PR and
  self-shims success for non-redirect PRs (so it is safe to make a required check).
- **Agreement ledger** (`scripts/autodoc_automerge.py`,
  `data/autodoc-automerge-ledger.json`): the runner records each redirect PR and reconciles its
  outcome each run (merged-as-is / edited / closed / reverted). "Merged-as-is" is re-verified with
  the independent verifier; reverts are detected via git against the stored merge SHA.

**The observational gate calculation** (`autodoc_automerge.unlock_state`) retains these calibration
inputs, but its result is never used to call `gh pr merge --auto`:

| Condition | Env var | Default |
|-----------|---------|---------|
| Master switch on | `AUTOMERGE_ENABLED` | (off) |
| Min terminal samples in window | `AUTOMERGE_MIN_SAMPLES` | 10 |
| Min weeks the samples span | `AUTOMERGE_MIN_WEEKS` | 4 |
| Min merged-exactly-as-is rate | `AUTOMERGE_MIN_AGREEMENT` | 1.0 |
| Zero post-merge reverts in window | — | (always enforced) |
| Window length (days) | `AUTOMERGE_WINDOW_DAYS` | 120 |

Defaults are conservative placeholders. The agreement ledger is repo-local runtime state, not an
anti-tamper boundary (see the `autodoc_automerge` module docstring). Do not enable or document an
activation path without a separately approved policy change; `AUTOMERGE_ENABLED` is observational
only in the runner.

Revert detection remains useful telemetry. No automated auto-revert or native auto-merge workflow
should be added while OceanSquad is the single merge owner.

## Portability to other Gov repos

The runner is repo-agnostic — the same scripts work for `FSI-CopilotGov`,
`FSI-CopilotGov-Solutions`, and similar **public** repos owned by `judeper`. To onboard one:

1. Copy the `scripts/autodoc_*.py`, `scripts/Register-AutodocTask.ps1`, the `autodoc-verify.yml`
   workflow, `.github/CODEOWNERS`, and this runbook into the target repo (they have no
   FSI-AgentGov-specific paths beyond the docs allowlist in `autodoc_route.py`, which you tune per
   repo: `ALLOWED_HEADINGS` / `FORBIDDEN_PATHS` and the `docs/` path normalisation).
2. Ensure the target repo has a Learn Monitor producing `reports/monitoring/learn-changes-*.md`
   (or adapt `reports_glob` / the report format the router parses).
3. Register a task with a **unique** `-TaskName` and the target `-RepoPath`; set
   `AUTODOC_REPO=<owner>/<repo>` in that task's environment so the runner targets the right repo
   (defaults to `judeper/FSI-AgentGov`).
4. Set both `AUTODOC_ENABLED` switches for that repo.

Build for one repo first and generalise on the next onboarding (decide late) rather than
pre-abstracting a shared package.
