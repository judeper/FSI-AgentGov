# Troubleshooting: Control 2.2 — Environment Groups and Tier Classification

**Last Updated:** April 2026

---

## Common issues — quick reference

| Symptom | Most likely cause | First action |
|---|---|---|
| Rules saved but not enforced | Rules saved without **Publish** | PPAC → Group → Rules → **Publish rules** |
| Cannot add environment to a group | Environment is not Managed | Enable Managed Environment ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)) |
| Setting still editable in member environment | Rule not published or 15-min propagation delay | Verify Published timestamp; wait 15 min |
| New maker landed in ungrouped env | Routing target points to non-grouped env | Fix routing target ([Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md)) |
| External models still configurable | Wrong rule edited; or env in a different group | Verify environment's group on the env's PPAC page |
| CUA usage detected | CUA is governed by Microsoft Copilot Studio admin, not this control | Disable in Copilot Studio admin ([Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md)) |
| Group not visible in PPAC | Missing Power Platform Admin role | Confirm role in M365 admin / Entra |
| Cannot remove a rule once published | Rules cannot be unpublished — only changed | Edit rule to default value and re-publish |
| Maker complains setting is locked unexpectedly | Group inheritance is working as designed | Confirm with maker; document in maker FAQ |

---

## Detailed scenarios

### 1 — Rules not applying after configuration

**Symptoms.** Member environment's setting still matches its old value, or makers can still perform an action the rule was meant to block.

**Diagnose.**

1. PPAC → **Environment groups** → *group* → **Environments** tab — confirm the env is listed.
2. PPAC → **Environment groups** → *group* → **Rules** tab — confirm rule **Status = Published** with a recent timestamp.
3. PPAC → **Environments** → *env* → **Settings** — open the corresponding setting; it should show **Locked by environment group**.
4. Wait 15 minutes after publish for propagation; refresh PPAC.

**Resolve.**

- If env is missing from the group: add it (must be a Managed Environment first).
- If rule is **Saved** but not **Published**: click **Publish rules**.
- If still editable after 30 minutes: open a Microsoft support case (see escalation below).

---

### 2 — Cannot add an environment to a group

**Symptoms.** Environment doesn't appear in the picker, or the **Add** action returns an error.

**Diagnose.**

1. PPAC → **Environments** → *env* — check for the **Managed** badge.
2. Confirm env type is not **Default**, **Trial**, or **Developer (personal)** — these cannot join groups even when otherwise managed.
3. Confirm you have **Environment Admin** rights on the target environment (Power Platform Admin alone is sometimes insufficient at the resource level).
4. Confirm the environment is not in a pending operation (provisioning, restore, recovery).

**Resolve.**

- Promote the environment to Managed via [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md).
- For Default / Trial, plan migration to a Production-type Managed Environment.
- Acquire Environment Admin or wait for the pending operation.

---

### 3 — Group rule and per-environment setting disagree

**Symptoms.** A setting appears in two places (group and environment) with conflicting visible values.

**Behaviour.** Once a group rule is **Published**, the corresponding environment setting becomes **Locked (read-only)** and inherits the group value. There is no per-environment exception today.

**Resolve.**

- If a legitimate exception is required, move the environment to a different group with the desired value, **or** unpublish the conflicting rule (this affects all members).
- Document the resolution in the governance change log.

---

### 4 — A new Microsoft rule has appeared in PPAC

**Symptoms.** Rules tab shows a rule that is not in the FSI zone matrix.

**Diagnose.**

1. Cross-check the [Microsoft Learn rules list](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules) — note GA vs preview.
2. Determine the data / supervisory implications with AI Administrator and Purview Compliance Admin.

**Resolve.**

- Decide a Zone 1/2/3 value, update the matrix in `docs/controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`, and re-publish in PPAC.
- Record the change in the governance change log; note the source URL and decision date.
- Bring the next quarterly re-baseline forward if the new rule is high-impact.

---

### 5 — Maker routed into the wrong zone

**Symptoms.** A new maker's environment is in the wrong group, or in no group at all.

**Diagnose.**

1. PPAC → **Environments** → **Environment routing** — review the active routing rules.
2. Confirm the routing target environment is itself in an `FSI-Z1-*` group.
3. Check routing exceptions list for the maker.

**Resolve.**

- Update routing per [Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md).
- Move the misrouted environment into the correct zone group.
- Re-test with a pilot maker account.

---

### 6 — Group descriptions don't make zone intent obvious during audit

**Symptoms.** Auditor cannot determine governance zone from group names/descriptions alone.

**Resolve.**

- Update the description to include: `Zone {1|2|3}`, allowed data sensitivity, change authority, review cadence.
- Rename groups to the `FSI-Z{n}-{purpose}` convention if not already used.
- Re-capture screenshots and update the evidence pack.

---

### 7 — CUA usage detected despite "all zones disabled"

**Symptoms.** Audit shows CUA / Computer Use activity in a tenant where governance documentation states it is disabled.

**Important.** CUA is **not** an environment group rule. Disabling it in a group has no effect.

**Resolve.**

- Disable CUA tenant-wide in Copilot Studio admin per [Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md).
- Investigate the activity (audit log search; unified audit log → `MicrosoftCopilotStudio` workload).
- Document the incident per security incident procedures.
- Update Control 2.2 evidence to reference Control 2.24 status (do not claim Control 2.2 enforces CUA).

---

## How to confirm the control is active end-to-end

### Via portal

1. PPAC → **Environment groups** → *group* — Environments tab populated; Rules tab shows Published.
2. Open any member environment → Settings — at least one setting shows **Locked by environment group**.
3. Try to perform a blocked action (e.g., share an agent with Editor in a Zone 1 env) — action is blocked.

### Via PowerShell

```powershell
.\Validate-Control-2.2.ps1                  # exit code 0 = pass
.\Validate-Control-2.2.ps1 -FailOnWarning   # CI-friendly strict mode
```

### Via cross-control evidence

- Control 2.1 evidence shows all member environments are Managed.
- Control 2.24 evidence shows CUA tenant-wide disabled.
- Control 1.15 evidence shows CMK status (per environment, not via this control).

---

## Escalation path

| Step | Owner | When |
|---|---|---|
| 1 | Power Platform Admin | Initial triage and portal/PowerShell checks |
| 2 | AI Administrator | AI-related rule values (External models, Preview models, AI prompts, Generative AI settings) |
| 3 | Purview Compliance Admin | Retention or supervisory rule disputes |
| 4 | Microsoft Support | Platform bugs, propagation > 30 min, missing rules in PPAC |
| 5 | AI Governance Lead | Policy disputes that require executive sign-off |

### Microsoft Support — opening a case

1. PPAC → **Help + support** → **New support request**.
2. Category: **Environment groups**.
3. Provide: tenant ID, environment group ID, affected environment ID, rule name, expected vs observed behaviour, screenshots, and exact timestamps.

---

## Known limitations (April 2026)

| Limitation | Impact | Workaround |
|---|---|---|
| Group rule **values** cannot be set via PowerShell | No CI/CD for rule configuration | Portal-first; verify enforcement via per-environment setting reads |
| Rule propagation up to 15 minutes | Verification immediately after publish may show stale state | Plan changes during low-activity windows; re-verify after 15 min |
| No rule version history | Cannot roll back rules natively | Maintain manual change log + screenshot evidence pack |
| One group per environment | Cannot inherit from multiple groups | Use most-restrictive group; supplement with non-group controls |
| Per-environment exceptions not supported | A single non-conforming env requires a separate group | Create a narrowly scoped group for the exception with documented approval |
| Default and Trial environments cannot join | Cannot enforce rules there | Migrate workloads to Production-type Managed Environments |

---

## Security note — CUA (out of scope for this control)

Computer-Using Agents (CUA) is **not** governed by environment groups. The FSI baseline is **CUA disabled tenant-wide** via Copilot Studio admin / Microsoft 365 admin center. See [Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) for the authoritative procedure. Do not attempt to use environment groups as a CUA enforcement mechanism — it has no effect.

---

[Back to Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
