# Playbook Authoring Guide

Conventions and canonical skeleton for FSI Agent Governance Framework playbooks.

!!! info "Scope of this guide"
    This guide defines the canonical playbook structure for all new playbooks under `docs/playbooks/`. It also establishes the structural standard for the full 316-playbook rollout (79 controls × 4 types). The long-tail remediation of all 316 existing files to this standard is tracked as **PLAYBOOKS-01** and is flagged for a follow-up sprint — see [Follow-up Flag](#follow-up-flag-playbooks-01) at the bottom of this page.

---

## Canonical Playbook Skeleton

Every playbook under `docs/playbooks/control-implementations/{id}/` must follow this section order. Sections may be adapted for content, but **must not be omitted** (use a brief "N/A — not applicable for this control" if the section has no content).

### Portal Walkthrough (`portal-walkthrough.md`)

```markdown
# Control {X.Y} — Portal Walkthrough: {Control Name}

!!! abstract "Mission brief"
    | | |
    |---|---|
    | **What you'll accomplish** | ... |
    | **Estimated time** | ... |
    | **Required roles** | ... |
    | **Prerequisites** | ... |
    | **Rollback** | Brief rollback summary; link to Rollback section below |

??? note "Scope & regulatory context — expand for sibling routing and non-substitution reminders"
    ... (scope, sibling routing, non-substitution reminders)

!!! warning "Hedged-language reminder"
    This playbook helps support compliance with ... It does not by itself satisfy any obligation.

---

## Step 1: ...
## Step N: ...

---

## Rollback / Back-out

### Pre-change snapshot (required before configuration changes)
1. ...

### Rollback procedures by component
| Component | Rollback action | Time to effect |
|---|---|---|
| ... | ... | ... |

---

## Validation

- [ ] ...

---

[Back to Control {X.Y}](...) | [PowerShell Setup](...) | [Verification Testing](...) | [Troubleshooting](...)

---

*Updated: {Month Year} | Version: v1.6.2 | UI Verification Status: Current*
```

### PowerShell Setup (`powershell-setup.md`)

```markdown
# Control {X.Y} — PowerShell Setup: {Control Name}

!!! warning "Read the FSI PowerShell baseline first"
    ...

**Last Updated:** {Month Year}
**Modules Required:** ...

---

## Prerequisites
...

## Configuration Script
...

## Validation Script
...

## Rollback / Back-out

### Pre-change snapshot
...

### Rollback procedures
...

---

[Back to Control {X.Y}](...) | [Portal Walkthrough](...) | [Verification Testing](...) | [Troubleshooting](...)

---

*Updated: {Month Year} | Version: v1.6.2*
```

### Verification & Testing (`verification-testing.md`)

```markdown
# Control {X.Y} — Verification & Testing: {Control Name}

**Last Updated:** {Month Year}
**Estimated Time:** ...

---

## Manual Verification Steps
...

## Test Case Table

| Test | Expected Result | Evidence |
|---|---|---|
| ... | ... | ... |

## Evidence Collection Checklist
- [ ] ...

## Automated Validation
...

---

[Back to Control {X.Y}](...) | [Portal Walkthrough](...) | [PowerShell Setup](...) | [Troubleshooting](...)

---

*Updated: {Month Year} | Version: v1.6.2*
```

### Troubleshooting (`troubleshooting.md`)

```markdown
# Control {X.Y} — Troubleshooting: {Control Name}

**Last Updated:** {Month Year}

---

## Common Issues

| Symptom | Likely Cause | Resolution |
|---|---|---|
| ... | ... | ... |

## Detailed Diagnostic Steps
...

## Escalation Path
...

---

[Back to Control {X.Y}](...) | [Portal Walkthrough](...) | [PowerShell Setup](...) | [Verification Testing](...)

---

*Updated: {Month Year} | Version: v1.6.2*
```

---

## Length Budgets (Soft Guidance)

| Playbook type | Typical controls | "Advanced/Foundation" exceptions |
|---|---|---|
| Portal Walkthrough | 400–800 lines | Controls 2.1, 3.1, 3.4 are signalled exceptions (~800–1200 lines); they should carry a document map at the top |
| PowerShell Setup | 200–500 lines | Controls 2.1, 3.1 are signalled exceptions (~2000 lines); they carry a section map |
| Verification & Testing | 150–400 lines | |
| Troubleshooting | 100–300 lines | |

Playbooks substantially over the "Advanced/Foundation" exception thresholds should be reviewed for splitting or moving content to an Advanced Implementation guide.

---

## H1 Naming Convention

Use this exact form:

```
# Control {X.Y} — {Playbook Type}: {Control Name}
```

Where `{Playbook Type}` is one of:
- `Portal Walkthrough`
- `PowerShell Setup`
- `Verification & Testing`
- `Troubleshooting`

Examples:
- `# Control 1.1 — Portal Walkthrough: Restrict Agent Publishing by Authorization`
- `# Control 2.1 — PowerShell Setup: Managed Environments`
- `# Control 3.1 — Verification & Testing: Agent Inventory and Metadata Management`
- `# Control 4.7 — Troubleshooting: M365 Copilot Data Governance`

---

## Metadata Frontmatter (Optional but Recommended)

For leaf playbook pages, consider adding a search boost frontmatter to de-prioritize leaf pages in search (they should rank below the canonical control docs):

```yaml
---
search:
  boost: 0.5
---
```

Apply this to control-implementation leaf pages (individual playbooks for each control) but NOT to category index pages or the Playbooks overview.

---

## Language Rules

All playbooks must comply with the FSI Language Rules (see `CONTRIBUTING.md` and the CI language linter):

- **Never:** "ensures compliance", "guarantees", "will prevent", "eliminates risk"
- **Always use:** "supports compliance with", "helps meet", "required for", "aids in"
- Include implementation caveats: "Organizations should verify...", "Implementation requires..."

The CI language linter (`python scripts/verify_language_rules.py`) enforces these rules on every PR.

---

## Rollback / Back-out (Required in Portal and PowerShell Playbooks)

Every Portal Walkthrough and PowerShell Setup playbook must include a **Rollback / Back-out** section that:

1. **Requires a pre-change snapshot** — instructions to capture and hash the current state before any configuration change.
2. **Provides component-level rollback procedures** — a table mapping each configurable component to its rollback action and expected time to effect.
3. **Warns about irreversible operations** — explicit `!!! warning` callouts for any operations that cannot be easily undone.

See the [Control 1.1 Portal Walkthrough](../control-implementations/1.1/portal-walkthrough.md), [Control 2.1 Portal Walkthrough](../control-implementations/2.1/portal-walkthrough.md), and [Control 3.1 Portal Walkthrough](../control-implementations/3.1/portal-walkthrough.md) for reference implementations.

---

## Scope Collapsible (Required for Complex Playbooks)

Complex playbooks (those with substantial scope/sibling-routing/non-substitution content) should move that framing block into a collapsible admonition rather than a top-level `!!! danger "READ FIRST"`:

```markdown
??? note "Scope & regulatory context — expand for sibling routing and non-substitution reminders"
    ... content ...
```

The `???` syntax creates a closed-by-default collapsible block. Simple playbooks may omit this block if scope can be summarized in the mission brief row.

---

## PowerShell Helper Namespace Convention

Each control's four-playbook set must use **one canonical PowerShell function prefix** for helpers referenced across siblings. Helper functions called from one sibling playbook that are defined in another sibling must use the same prefix — mixed namespaces cause "command not found" errors when an admin copies a cmdlet name from one sibling into the workflow of another.

### Rule: One prefix per control

| Control | Canonical prefix | Defined in |
|---|---|---|
| 1.1 | *(none — uses bare module cmdlets)* | `powershell-setup.md` inline |
| 2.1 | `Fsi-` (e.g., `Invoke-Fsi-Control21Setup`, `Set-Fsi-SharingLimits`) | `powershell-setup.md` |
| 3.1 | `Agt31` (e.g., `Initialize-Agt31Session`, `Export-Agt31EvidencePack`) | `powershell-setup.md` |

For new controls, choose the prefix at authoring time and apply it consistently across all four playbooks. The `powershell-setup.md` playbook is the **canonical definition source**; troubleshooting and verification playbooks that need their own diagnostic helpers must:
- Use the **same prefix** if a helper is referenced from the PowerShell Setup playbook, OR
- Clearly scope any playbook-local helpers (e.g., with a comment or a distinct local-only prefix) and **never claim a local helper is "in the sister PowerShell Setup playbook"** unless it actually appears in that file.

### What "playbook-local helper" means

Some troubleshooting and verification playbooks define read-only diagnostic helpers that are not exported from the PowerShell Setup playbook:
- `2.1/troubleshooting.md` defines `Agt21`-prefixed read-only helpers inline. These are **not** the same as the `Fsi-*` helpers in `powershell-setup.md`.
- `2.1/verification-testing.md` defines `Me21`-prefixed evidence-infrastructure helpers inline (e.g., `New-Me21RunId`, `New-Me21EvidencePack`, `Test-Me21EvidenceSchema`). These are self-contained and not defined in `powershell-setup.md`.

To prevent broken cross-refs: if a code block calls a function by name, that function must either be defined in the **same file**, or the text must include a verified link to the exact section in the sibling file where the definition lives.

### Cross-reference hygiene checklist

Before committing any playbook update that adds a helper call:

- [ ] Is the function defined in this file? If not, which sibling file and which section?
- [ ] Does the referenced function name **exactly** match what appears in the sibling file? (Search the sibling file to confirm.)
- [ ] Does the cross-reference include a link to the correct section (`§N`), not just a link to the playbook?
- [ ] Is the prefix consistent with the control's canonical prefix?

---

## Follow-up Flag: PLAYBOOKS-02 (long-tail)

**Status:** Exemplar controls fixed (June 2026 sprint — 1.1, 2.1, 3.1) | Scope: 76 remaining controls

The cross-ref and namespace issues fixed in the exemplar controls (1.1, 2.1, 3.1) likely appear across the full 316-file set. Fixes applied:
- `2.1/verification-testing.md`: removed broken claim that `Invoke-Me21PreFlight.ps1` is in PowerShell Setup; fixed broken `§10`/`Invoke-Me21Tests.ps1` Pester reference (§19.1 is the correct location); fixed wrong `§6` cross-ref for maker enumeration helper
- `2.1/troubleshooting.md`: removed broken `scripts/control-2.1/Agt21-Helpers.ps1` external-script reference; helpers are inline in this file
- `1.1/powershell-setup.md`: removed misleading "PSEUDOCODE" labels from rollback snapshot block (cmdlets are real and used in the same file)

**Remaining rollout (not in this sprint):**
- Audit all 316 files for "see sister playbook" cross-refs that don't resolve to an existing function or section
- Standardize function prefixes across all 79 controls' four-playbook sets
- Add a CI lint that greps cross-referenced function names against their claimed definition location

**CI enforcement (proposed):** A `scripts/verify_playbook_xrefs.py` script should verify that any text matching "in the sister \[PowerShell Setup\]" is followed by a function name that actually appears in the referenced sibling. **This CI gate does not exist yet — flagged for the follow-up sprint.**

---

## Follow-up Flag: PLAYBOOKS-01

**Status:** Flagged for follow-up sprint | Scope: 316 files across 79 controls × 4 playbook types

The canonical structure above is established as of June 2026. The full rollout to all 316 files is bounded as a follow-up item:

**What has been applied (June 2026 sprint):**
- Mission brief box + collapsible scope/regulatory block: Control 2.1 and 3.1 portal walkthroughs (exemplars)
- Rollback / Back-out section: Control 1.1, 2.1, 3.1 portal walkthroughs + Control 1.1 and 2.1 PowerShell setups
- BOM removed from 10 files
- H1 standardized for 4.7 PowerShell and Verification & Testing
- This authoring guide established as the canonical standard

**Remaining rollout:**
- Apply mission brief box to remaining 311 portal-walkthrough files
- Add Rollback / Back-out section to remaining portal-walkthrough and PowerShell-setup files
- Standardize H1 format across all 316 files
- Optionally: add `search: boost: 0.5` frontmatter to all 316 leaf files (PLAYBOOKS-IA-11)

**CI enforcement (proposed):** A template-conformance lint script (`scripts/verify_playbook_structure.py`) should be added as a CI gate that checks for: H1 presence + naming convention, presence of required sections (Rollback, Validation), and absence of banned phrases. **This CI gate does not exist yet — flagged for implementation in the follow-up sprint.**

---

*Updated: June 2026 | Version: v1.6.2*
