# Verification & Testing: Control 2.15 — Environment Routing and Auto-Provisioning

**Last Updated:** April 2026

This playbook produces audit-defensible evidence that environment routing is on, the rule order matches the documented policy, and routed makers actually land in the expected environment group.

---

## Manual Verification Steps

### Test 1 — Routing is Enabled at the Tenant Setting

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com) as a Power Platform Admin.
2. **Manage → Tenant settings → Environment routing**.
3. **EXPECTED:** Routing toggle is **On**; the configured product portals (Copilot Studio, Power Apps, Power Automate cloud, Power Automate for desktop) match the documented scope.

Programmatic equivalent:

```powershell
(Get-TenantSettings).powerPlatform.governance.enableDefaultEnvironmentRouting   # → True
(Get-TenantSettings).powerPlatform.governance.environmentRoutingAllMakers       # → True or False per policy
```

### Test 2 — Rule Order Matches Documented Policy

1. PPAC → Tenant settings → Environment routing.
2. Capture the rule list in order, including audience (Everyone / security group GUID) and target environment group.
3. Compare to the rule-order document attached to the change ticket.
4. **EXPECTED:** Rule names, audiences, target groups, and order match the approved policy.

### Test 3 — LOB Maker Lands in the Correct Environment Group

For each LOB security group rule:

1. Sign in as a test user who is a member of `<sg-fsi-lob-makers>` and has **no** existing developer environment.
2. Open [Copilot Studio](https://copilotstudio.microsoft.com) (and repeat for Power Apps).
3. **EXPECTED:** A new developer environment is auto-provisioned and is assigned to the LOB target environment group.
4. In PPAC, open the new environment → **Settings** → confirm Type = Developer, Managed = On, parent group = expected.

### Test 4 — Catch-All "Everyone" Rule Routes Unaffiliated Makers

1. Sign in as a test user **not** in any LOB routing security group.
2. Open Copilot Studio (no existing dev env).
3. **EXPECTED:** Maker is provisioned into the catch-all group (e.g., `FSI-Personal-Dev-Default`). If the only outcome is the default environment, the catch-all rule is missing — flag as gap.

### Test 5 — Existing Developer Environment Wins

1. Sign in as a maker who already owns a developer environment.
2. **EXPECTED:** Maker is routed into their **existing** developer environment, not a new one. (If multiple, alphabetically first.) This is documented Microsoft behavior, not a defect.

### Test 6 — Group-Published Rules Are Inherited

1. Open a routed personal dev env in PPAC.
2. **Settings → Sharing limits / AI features / Solution checker** — confirm the values match the parent group's published rules and are **locked** (read-only at the env level).
3. **EXPECTED:** All values inherited; local environment admin cannot modify them.

### Test 7 — Default Environment Still Reachable (Documented Limitation)

1. As any routed maker, in the maker portal use the environment switcher to navigate to the default environment.
2. **EXPECTED:** Access is **not** blocked by routing alone. This is a known limitation; default-environment hygiene depends on Control 2.16 + DLP (Control 1.4).

### Test 8 — Sovereign Cloud Confirmation (GCC / GCC High / DoD only)

1. Run `Get-TenantSettings` after `Add-PowerAppsAccount -Endpoint <cloud>`.
2. **EXPECTED:** Returned tenant ID matches your sovereign tenant. If commercial values appear, the script connected to the wrong cloud — re-run with the correct `-Endpoint`.

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.15-01 | Routing enabled in tenant settings | `enableDefaultEnvironmentRouting = True` | |
| TC-2.15-02 | Routing enabled for documented portals | Matches policy scope | |
| TC-2.15-03 | Rule order matches change ticket | Same names, order, target groups | |
| TC-2.15-04 | LOB user (no existing dev env) routes to LOB group | New env in LOB group | |
| TC-2.15-05 | Unaffiliated user routes via catch-all | New env in default catch-all group | |
| TC-2.15-06 | Maker with existing dev env keeps it | Routed to existing env | |
| TC-2.15-07 | Group-published rules inherited and locked | Locked values match group | |
| TC-2.15-08 | Default env still reachable | Reachable (documented limitation) | |
| TC-2.15-09 | Sovereign-cloud script binds to correct tenant | Tenant ID matches | |
| TC-2.15-10 | Routing change requires CAB approval (Zone 3) | No undocumented changes in audit log | |

---

## Evidence Collection Checklist

### Configuration

- [ ] `tenant-settings-after-*.json` (output of `Get-TenantSettings` post-change) — captured by the PowerShell setup script
- [ ] `manifest-*.json` listing each evidence file with SHA-256, bytes, generated_utc, control = 2.15
- [ ] PPAC screenshot of **Tenant settings → Environment routing** showing the rule list and order (file: `Control-2.15_RoutingRules_<YYYYMMDD>.png`)
- [ ] PPAC screenshot of each target **Environment group → Rules** tab showing rules **Published** (file: `Control-2.15_GroupRules_<group>_<YYYYMMDD>.png`)
- [ ] CSV inventory of routed developer environments (`dev-env-inventory-<YYYYMMDD>.csv`)

### Test Execution

- [ ] Screenshot of LOB test maker landing in expected group (one per LOB)
- [ ] Screenshot of catch-all test maker landing in default catch-all group
- [ ] Screenshot of routed env Settings showing inherited, locked values
- [ ] Document: Test results table with date, user, observed env, expected env, pass/fail

### Supervisory Review (Zone 3 / FINRA-regulated)

- [ ] Change ticket reference linking to CAB approval
- [ ] Attestation (template below), signed by control owner
- [ ] Confirmation that all evidence files have been transferred to WORM-locked storage

---

## Evidence Artifact Naming Convention

```
Control-2.15_<ArtifactType>_<YYYYMMDD>.<ext>

Examples:
  Control-2.15_RoutingRules_20260418.png
  Control-2.15_TenantSettingsAfter_20260418.json
  Control-2.15_GroupRules_FSI-Personal-Dev-Wealth_20260418.png
  Control-2.15_TestResults_20260418.xlsx
  Control-2.15_Manifest_20260418.json
```

---

## Attestation Statement Template

```markdown
## Control 2.15 Attestation — Environment Routing

**Organization:** [Organization Name]
**Control Owner:** [Name / Role]
**Reviewer:** [Compliance Officer]
**Date:** [YYYY-MM-DD]

I attest that as of the date above:

1. Environment routing is enabled in the tenant for the documented set of maker portals.
2. Routing rules in PPAC match the rule-order document attached to change ticket [CHG-####].
3. Each target environment group is populated with Managed Environments and has its policy rules **Published**.
4. Sample testing for each LOB security group and the catch-all rule produced the expected routing outcome.
5. Evidence files (PPAC screenshots, `Get-TenantSettings` JSON, SHA-256 manifest) have been transferred to WORM-locked storage in compliance with SEC 17a-4(f) and FINRA 4511.
6. Any deviation between the configured state and the documented policy has been logged and remediated or explicitly accepted.

**Routing Rules Active:** [Number]
**Target Environment Groups:** [Comma-separated names]
**Maker Scope:** [All makers / New makers only]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
