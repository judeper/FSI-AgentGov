# Control 3.8: Copilot Hub and Governance Dashboard — Troubleshooting

> Troubleshooting guidance for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md). Each issue follows the same structure: **Symptoms → Likely cause → Diagnostic steps → Resolution → Evidence to capture**. Always wait the documented propagation window (24 h for exclusion groups, 8 h for tenant settings) before escalating — premature escalation is the most common false-positive in FSI Copilot deployments.

---

## 1. AI Feature Access Control issues

### 1.1 Excluded user still has Copilot access

**Symptoms:** A user added to `CopilotForM365AdminExclude` continues to see admin-center Copilot features.

**Likely causes:**

- Less than 24 hours since group membership change.
- Group name typo (case-sensitive — must be exactly `CopilotForM365AdminExclude`).
- User has cached tokens.
- User holds multiple Copilot license assignments and one bypasses the exclusion path.

**Diagnostic steps:**

```powershell
$grp = Get-MgGroup -Filter "displayName eq 'CopilotForM365AdminExclude'"
$usr = Get-MgUser  -Filter "userPrincipalName eq 'user@contoso.com'"
Get-MgGroupMember -GroupId $grp.Id | Where-Object Id -eq $usr.Id  # confirm membership
$usr.AssignedLicenses | Format-Table  # confirm only one Copilot SKU
```

**Resolution:**

1. Wait the full 24-hour propagation window.
2. Verify the group name exactly (no whitespace, correct casing).
3. Have the user sign out of all M365 sessions, clear browser cache, and sign in again.
4. If still failing, check for Conditional Access policies or admin role overrides (Global Admins may bypass certain restrictions).
5. Note the scope: the exclusion governs **admin-center** Copilot features; end-user Copilot in Word/Excel/Teams requires separate license/policy controls.

**Evidence:** PowerShell membership confirmation, before/after screenshots, timestamp records.

---

### 1.2 Deployment group not limiting access

**Symptoms:** Users outside the deployment group can access Copilot, or users inside cannot.

**Likely causes:**

- Group is Microsoft 365 instead of Security.
- Deployment group setting points at the wrong group ID.
- Less than 8 hours since the change.
- User is in both deployment group and Admin Exclusion Group (exclusion wins).

**Diagnostic steps:**

```powershell
$dep = Get-MgGroup -Filter "displayName eq 'Copilot-Pilot-IT-Compliance'"
$exc = Get-MgGroup -Filter "displayName eq 'CopilotForM365AdminExclude'"
$usr = Get-MgUser  -Filter "userPrincipalName eq 'user@contoso.com'"
Get-MgGroupMember -GroupId $dep.Id | Where-Object Id -eq $usr.Id
Get-MgGroupMember -GroupId $exc.Id | Where-Object Id -eq $usr.Id
$dep.SecurityEnabled; $dep.MailEnabled  # must be True; False
```

**Resolution:**

1. Confirm group type is Security (`SecurityEnabled = True`, `MailEnabled = False`).
2. Reconcile the configured group ID against the intended group.
3. Wait the 8-hour window.
4. Remove the user from the exclusion group if conflict detected.

---

### 1.3 Web search still returning results after disabling

**Symptoms:** Copilot continues to ground responses in external web data after the setting is Disabled.

**Likely causes:**

- Less than 8 hours since the change.
- Setting was applied at a sub-scope (group/user) but not tenant-wide.
- Browser/session cache.
- Response is internal data that **looks** web-like.

**Resolution:**

1. Wait the 8-hour window.
2. Re-test with a query that demonstrably requires web access ("today's news headlines"); the expected response is "I don't have access to web search" or equivalent.
3. Confirm the tenant-level setting is Disabled (not just a per-group override).
4. Have the user sign out and clear cache before retesting.

**Evidence:** before/after settings screenshot, before/after response screenshot with citation list.

---

### 1.4 Admin Exclusion Group propagation appears stuck

**Symptoms:** 24-hour window has elapsed, exclusion still not effective.

**Resolution:**

1. Confirm the group name exactly matches `CopilotForM365AdminExclude`.
2. Verify the user is a direct member, not nested through an unsupported group type.
3. Open a Microsoft Support ticket — include the group object ID, the affected user UPN, the timestamp of group membership change, and the exact Copilot feature you are testing. Reference KB documentation for `CopilotForM365AdminExclude`.
4. Track Sev B; targeted SLA 4 hours.

---

## 2. Copilot Hub portal issues

### 2.1 Copilot section missing from M365 Admin Center

**Symptoms:** No Copilot navigation entry in admin.microsoft.com.

**Resolution:**

1. Confirm M365 Copilot licenses are assigned in the tenant (not just purchased).
2. Confirm the signed-in user has AI Administrator or Entra Global Admin.
3. Clear browser cache, sign in again.
4. Check the Service Health Dashboard for tenant-level Copilot incidents.

---

### 2.2 Settings changes not propagating

**Symptoms:** Saved configuration is not reflected in user behavior after the documented window.

**Resolution:**

1. Allow up to **8 hours** for tenant settings; up to **24 hours** for Admin Exclusion Group; up to **48 hours** in extreme cases.
2. Confirm users sign out and back in.
3. Check Conditional Access for policies that re-enable controls (e.g., session controls forcing web grounding).
4. Check group policy overrides for browser-side controls (Edge Copilot, etc.).
5. If still failing, capture timestamps and submit a Microsoft Support ticket.

---

### 2.3 Agent registry incomplete or inaccurate

**Symptoms:** Known agents missing; counts disagree with Copilot Studio inventory.

**Resolution:**

1. Confirm Entra ID directory sync is current (no pending sync errors).
2. Use the Refresh control on the Registry page.
3. Cross-check via the PPAC Copilot Studio environment inventory (`Export-PpacCopilotStudioInventory`).
4. For Frontier agents (App Builder, Workflows) and SharePoint agents, hero metrics depend on Agent 365 / M365 E7 licensing and the Agent 365 Observability SDK — coverage gaps are expected and should be documented per the control's "Verification Criteria" item 23.

---

### 2.4 Usage reports show no data

**Symptoms:** Chat Active Users / Assisted Hours / Satisfaction Rate panels empty.

**Resolution:**

1. Confirm Copilot has been actively used for ≥ 72 hours.
2. Confirm Purview Audit (Standard or Premium) is enabled tenant-wide.
3. Confirm the executing identity has the **Reports Reader** role (or higher).
4. Verify the report date range covers active usage.

---

## 3. PowerShell automation issues

### 3.1 `Get-MgAuditLogDirectoryAudit` returns no Copilot events

**Likely causes:**

- Purview Audit not enabled.
- Identity lacks `AuditLog.Read.All`.
- Filter window predates audit retention (default 180 days for Standard).

**Resolution:**

```powershell
Get-MgContext | Select-Object Account, Scopes
# Confirm AuditLog.Read.All present; if not, reconnect with the scope
Connect-MgGraph -Scopes 'AuditLog.Read.All' -Environment $env
```

Confirm Purview Audit is enabled in the Microsoft Purview portal.

---

### 3.2 `Add-PowerAppsAccount` returns zero environments

**Almost always a sovereign-cloud endpoint mismatch** — see [PowerShell baseline §3](../../_shared/powershell-baseline.md). Pass `-Endpoint usgov` / `usgovhigh` / `dod` / `china` for the appropriate cloud. Commercial-endpoint authentication against a sovereign tenant returns false-clean (zero) results.

---

### 3.3 PPAC cmdlets fail with empty results in PowerShell 7

**Cause:** `Microsoft.PowerApps.Administration.PowerShell` is **Desktop-only** (Windows PowerShell 5.1).

**Resolution:** Run PPAC governance scripts in Windows PowerShell 5.1 only. The PowerShell baseline includes a guard:

```powershell
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw 'PPAC governance cmdlets require Windows PowerShell 5.1.'
}
```

---

### 3.4 Module-version mismatch breaks evidence reproducibility

**Symptoms:** Same script returns different shapes between runs; SHA-256 manifests disagree.

**Resolution:** Pin every module via `-RequiredVersion <approved-version>` — see [baseline §1](../../_shared/powershell-baseline.md). Document the pinned versions in your change ticket.

---

## 4. Supervision and transcript issues

### 4.1 Agent creator can still access their own transcripts

**Likely causes:** Conditional Access or RBAC policy not enforced; user is in both `Copilot-Studio-Publishers` and `Copilot-Compliance-Supervisors`.

**Resolution:**

1. Audit group membership — a user must not be in both groups.
2. Confirm the Conditional Access policy denying transcript URLs to `Copilot-Studio-Publishers` is in **Enabled** state (not Report-only).
3. Sign the user out, clear cached tokens, retest.
4. Capture the failure for your separation-of-duties evidence pack.

---

### 4.2 Transcript retention shorter than 7 years

**Resolution:** Configure a Purview retention policy on the Copilot Studio transcript location with minimum 7-year retention. For SEC 17a-4(f) WORM expectations, pair with Azure Immutable Blob Storage (legal hold or time-based retention) for the exported archives.

---

### 4.3 No audit events for transcript access

**Resolution:**

1. Confirm Purview Audit is enabled.
2. Confirm Copilot Studio audit events are within the retention window (Standard: 180 days; Premium: up to 10 years).
3. Verify the executing identity holds **AuditLog.Read.All**.
4. For SIEM forwarding, confirm the connector is healthy and not back-pressured.

---

## 5. DLP and publishing issues

### 5.1 Agents continue to publish through restricted connectors

**Resolution:**

1. Confirm a tenant DLP policy includes the target environment.
2. Confirm `Copilot Studio for Microsoft Teams` and `M365 Copilot channel` are in the **Blocked** classification.
3. Confirm the policy is in **Enforced** mode (not Audit).
4. See [Control 1.5 — DLP](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) for full DLP authoring.

---

## Diagnostic command quick reference

```powershell
# Copilot license assignment
$copilotSkus = Get-MgSubscribedSku | Where-Object SkuPartNumber -match 'Copilot'
Get-MgUser -Filter 'assignedLicenses/any()' -All |
    Where-Object { ($_.AssignedLicenses.SkuId | Where-Object { $_ -in $copilotSkus.SkuId }).Count -gt 0 } |
    Select-Object DisplayName, UserPrincipalName

# Confirm Graph context and scopes
Get-MgContext | Select-Object Account, TenantId, Scopes

# List Copilot-relevant directory roles
Get-MgDirectoryRole | Where-Object DisplayName -match 'AI Administrator|Global Administrator|Power Platform Administrator'
```

---

## Escalation path

| Severity | Symptom | Escalate to | Target response |
|---|---|---|---|
| Sev A | Copilot Hub unavailable tenant-wide | Microsoft Support (Severity A) | 1 hour |
| Sev B | Settings not propagating after documented window | Microsoft Support (Sev B) + IT Operations | 4 hours |
| Sev B | Admin Exclusion Group failing to enforce | Microsoft Support + Compliance Officer | 4 hours |
| Sev C | Agent registry inaccurate | Power Platform Admin | 1 business day |
| Immediate | Suspected unauthorized transcript access | Compliance Officer + Security Team | Immediate |
| Immediate | DLP bypass observed | Compliance Officer + Security Team | Immediate |

> Hedged language reminder: this control **supports** FINRA / SEC / GLBA / SOX evidence requirements; troubleshooting issues do not by themselves trigger regulatory non-compliance, but undocumented gaps in supervision often do. Capture every diagnostic step in your change/incident ticket.

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — manual configuration
- [PowerShell Setup](powershell-setup.md) — automation scripts
- [Verification & Testing](verification-testing.md) — test cases and evidence collection

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
