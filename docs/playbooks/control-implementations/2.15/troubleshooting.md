# Troubleshooting: Control 2.15 — Environment Routing and Auto-Provisioning

**Last Updated:** April 2026

This playbook addresses the most common failure modes admins encounter when enabling and operating environment routing. Most issues stem from confusing **routing rules** (Tenant settings → Environment routing) with **environment-group policy rules** (Environment groups → Rules). They are different surfaces.

---

## Common Issues — Quick Reference

| Issue | Likely Cause | First Action |
|-------|--------------|--------------|
| No routing happens at all | `enableDefaultEnvironmentRouting` is False, or no rules saved | `Get-TenantSettings` and check the flag |
| Maker lands in default env instead of expected group | No matching rule, or higher-priority "Everyone" rule shadows LOB rules | Inspect rule order in PPAC |
| Maker lands in their old dev env, not the routed group | Documented behavior — existing dev env wins | Decommission the old env or accept |
| Group rules not applied to routed env | Group rules in **Draft**, not **Published** | Open group → Rules → publish |
| Maker can still open the default environment | Documented behavior — routing sets landing env, does not restrict | Layer DLP / access reviews (Controls 1.4, 2.16) |
| `Get-TenantSettings` returns empty / errors | Wrong PowerShell edition or sovereign endpoint | Check Desktop edition + `-Endpoint` value |
| Rules won't save in PPAC | Insufficient role, or referenced security group missing | Verify Power Platform Admin + group existence |

---

## Detailed Troubleshooting

### Issue: No routing happens at all

**Symptoms:** Every maker (test or real) lands in the default environment regardless of group membership.

**Diagnostic Steps:**

```powershell
$g = (Get-TenantSettings).powerPlatform.governance
$g | Select-Object enableDefaultEnvironmentRouting,
                   environmentRoutingAllMakers,
                   environmentRoutingTargetEnvironmentGroupId
```

1. If `enableDefaultEnvironmentRouting` is **False**, routing is off — re-run `Enable-EnvironmentRouting.ps1` (PowerShell Setup playbook).
2. If `environmentRoutingAllMakers` is **False** and your test users already had accounts before routing was enabled, they are excluded by design — set to `True` or test with a never-before-seen account.
3. In PPAC → Tenant settings → Environment routing, confirm at least one rule is listed and that **Save** was clicked at the pane level (rule-level Save alone is not enough).

**Resolution:** Re-enable routing with the documented PowerShell or PPAC procedure; confirm the AllMakers scope; confirm the rule list is non-empty and saved.

---

### Issue: Maker lands in the default env instead of the expected target group

**Symptoms:** A user who is a member of an LOB security group is still landing in the default environment.

**Diagnostic Steps:**

1. **Group membership:** Microsoft Entra Admin Center → Users → \[user\] → Groups. Confirm transitive membership in the security group named in the rule.
2. **Rule order:** PPAC → Tenant settings → Environment routing. Read top-down. The first matching rule wins. If an "Everyone" rule sits above the LOB rule, every maker hits "Everyone" first.
3. **Existing dev env:** PPAC → Environments, filter Type = Developer, Owner = the test user. If they already own one, routing sends them to it (alphabetically first if multiple).
4. **Provisioning failure:** If new-env creation fails for any reason, the maker silently falls back to the default environment. Check Power Platform admin activity logs for `EnvironmentProvisioningFailed` events.
5. **Sync delay:** New security-group memberships can take up to 24 hours to propagate into routing decisions.

**Resolution:**

- Move the LOB rule above the "Everyone" rule.
- Decommission the old developer environment, or accept the existing-env-wins behavior.
- Re-test 24 hours after a new group membership is added.
- If provisioning failures recur, open a Microsoft support ticket — these are platform-side.

---

### Issue: Group rules are not being inherited by routed environments

**Symptoms:** A routed dev env shows local sharing limits or AI flags that don't match the parent group's policy.

**Diagnostic Steps:**

1. PPAC → Environment groups → \[target group\] → **Rules** tab.
2. For each rule (Sharing limits, AI features, Solution checker, Backup retention, etc.), confirm status is **Published**, not **Draft**.
3. In the routed env's Settings, the inherited values should appear with a lock icon. If they're editable, the rule is unpublished or the env is not actually in the group.
4. Confirm the env is in the expected group: PPAC → Environments → \[env\] → property "Environment group".

**Resolution:** Publish any draft rules. If the env is in the wrong group, move it via Environments → \[env\] → Edit → Environment group.

---

### Issue: Routed maker can still access and create in the default environment

**Symptoms:** Even after routing is on, makers continue creating apps and agents in the default environment.

**Cause:** This is **documented behavior**. Environment routing sets the maker's landing/default environment in the maker portals — it does not restrict access to other environments the maker has rights to. The default environment is accessible to everyone in the tenant by default.

**Resolution (defense in depth):**

- Apply tight DLP policies to the default environment (Control 1.4).
- Restrict Maker / Environment Maker role assignment in the default environment (Control 2.16).
- Configure publisher-restriction policies (Control 1.1) to block agent publishing in the default env.
- Track and decommission default-env resources on a documented cadence (Control 2.16, 3.x reporting).

There is no built-in "deny" or "block" routing rule type.

---

### Issue: `Get-TenantSettings` returns empty, errors, or wrong tenant data

**Symptoms:** Script returns `$null`, throws "command not found", or returns settings for a tenant other than the intended one.

**Diagnostic Steps:**

1. Confirm PowerShell edition: `$PSVersionTable.PSEdition` must be **Desktop** (Windows PowerShell 5.1). The Power Apps Administration module silently fails on PowerShell 7.
2. Confirm the module is installed and at the CAB-approved version: `Get-Module Microsoft.PowerApps.Administration.PowerShell -ListAvailable`.
3. Confirm the sovereign cloud endpoint matches the tenant: `Add-PowerAppsAccount -Endpoint <prod|usgov|usgovhigh|dod> -TenantID <id>`. Wrong endpoint binds to the wrong cloud and returns commercial data (or zero environments) — produces **false-clean evidence**.
4. Confirm the executing identity has the **Power Platform Admin** role (Entra) or a Dataverse System Admin role on the tenant.

**Resolution:** Switch to Windows PowerShell 5.1; install the pinned module version; supply the correct `-Endpoint`; assign the Power Platform Admin role (use PIM for just-in-time elevation).

---

### Issue: Rules won't save in PPAC

**Symptoms:** Clicking **Save** in the routing rule pane returns an error or silently reverts.

**Diagnostic Steps:**

1. Confirm Power Platform Admin role on the executing identity (Environment Admin is **not** sufficient for tenant-level routing rules).
2. Confirm the referenced Microsoft Entra security group exists and the executing identity can read it.
3. Confirm the target environment group exists, contains at least one Managed Environment, and is in a state other than "Provisioning".
4. Check browser console / network tab for HTTP 403 / 404 responses identifying the failing dependency.

**Resolution:** Add Power Platform Admin role; create or repair the missing security or environment group; retry.

---

## How to Confirm Configuration Is Active

### Via PowerShell (machine-readable, audit-friendly)

```powershell
$g = (Get-TenantSettings).powerPlatform.governance
[PSCustomObject]@{
    Enabled       = $g.enableDefaultEnvironmentRouting
    AllMakers     = $g.environmentRoutingAllMakers
    PrimaryGroup  = $g.environmentRoutingTargetEnvironmentGroupId
} | Format-List
```

### Via Portal

1. PPAC → Manage → Tenant settings → Environment routing.
2. Confirm the toggle is On, the product portals match policy, and rules appear in the documented order.
3. Cross-check each target group via Manage → Environment groups → \[group\] → **Rules** showing **Published**.

### Via Maker Experience

1. Sign in as a test maker matching a specific rule. Open Copilot Studio.
2. Confirm a new dev env is auto-provisioned in the expected group, OR (if the maker already owns a dev env) confirm routing landed them in their existing one.

---

## Escalation Path

1. **Power Platform Admin team** — routing configuration, environment-group rules, provisioning failures.
2. **Identity / Entra team** — security-group membership, group sync delays.
3. **Microsoft Support** — recurring provisioning failures, multi-rule rendering bugs in PPAC, sovereign-cloud endpoint regressions.
4. **AI Governance Lead / Compliance Officer** — policy questions, exceptions, change approval.

---

## Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Routing only sets the maker's landing env | Default env remains accessible | Combine with DLP (Control 1.4) and default-env hygiene (Control 2.16) |
| Existing developer environment wins over a new routing target | Maker not placed in the expected group on first visit | Decommission legacy dev envs or accept |
| Rule audiences limited to "Everyone" or one Entra security group | Cannot natively route by domain, attribute, or geography | Model these via security group membership upstream |
| Routing fails closed → fallback to default env | Provisioning failures look like compliance gaps | Monitor `EnvironmentProvisioningFailed` events |
| Power Apps Administration module is **Desktop only** | PS 7 hosts return empty results silently | Edition guard in every script (see PowerShell Setup) |
| Multi-rule routing managed primarily via PPAC, not PowerShell | Cannot fully automate rule ordering through tenant settings cmdlets | Capture PPAC export as supplementary evidence |
| Power Pages not in scope for routing | Pages makers still default to the default env | Govern Pages separately |
| Rule changes evaluated at session start | Active maker sessions don't re-route until next sign-in | Communicate planned changes; rotate test sessions |

---

[Back to Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
