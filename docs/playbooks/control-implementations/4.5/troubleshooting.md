# Control 4.5: SharePoint Security and Compliance Monitoring - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md).

---

## Common Issues and Solutions

| Issue | Symptoms | Likely Cause | Resolution |
|---|---|---|---|
| **Agent insights page empty** | "View reports" shows no data; tenant has known agent activity | SAM not yet provisioned, or 24–48h initial population window not elapsed | Confirm SAM entitlement (bundled with M365 Copilot since Jan 2025, or standalone SAM SKU). Wait 48 hours after activation before troubleshooting further |
| **DAG reports empty** | Reports generate but show no content | First-run baseline not initialized, or tenant truly has no qualifying activity | Click **Get started** under **Reports > Data access governance**. For 10,000+ site tenants, allow several hours for snapshot completion |
| **Dashboard cards missing data** | Home dashboard shows blanks or "Data unavailable" | Insufficient role assignment, browser blocking, or temporary service issue | Verify SharePoint Admin role via deterministic Graph check (see PowerShell Setup, Step 6); check Microsoft 365 Service Health for active SharePoint incidents |
| **Audit log search returns zero** | `Search-UnifiedAuditLog` completes with no results in active tenant | Audit ingestion disabled, or search outside retention window | Confirm `UnifiedAuditLogIngestionEnabled = True`; confirm date range within active retention |
| **Audit log search silently truncated** | Result count exactly 5,000 with no error | `Search-UnifiedAuditLog` page limit; non-paginated call | Use session-based pagination (`SessionId` + `SessionCommand ReturnLargeSet`) per the FSI baseline |
| **Advanced Management features missing** | Menu items grayed out | Tenant lacks SAM entitlement | Confirm SAM via Microsoft 365 admin center "Your products"; SAM is included with every M365 Copilot license as of Jan 2025 |
| **Export failures or timeouts** | DAG / audit export hangs or errors | Result set too large; concurrent admin operations; off-hours throttling | Reduce date range; filter by site or user; rerun during business hours; for very large tenants, paginate with `-ResultSize 5000` and session IDs |
| **Real-time alerts not firing** | Expected high-severity alerts never received | Alert policy disabled, recipient mailbox not monitored, or threshold too high | Confirm policy is **Active**; verify recipient is a monitored shared mailbox (not a single admin); review threshold; remember alert latency is not contractually guaranteed and can be minutes to a few hours |
| **`Get-MgUserMemberOf` fails to confirm SharePoint Admin** | Role check returns `$false` for a user who has the role | `displayName -like '*SharePoint*'` heuristic misses the role, or role not yet activated in tenant | Use deterministic role lookup via `Get-MgDirectoryRole`; activate role from template if needed (see PowerShell Setup Step 6) |
| **Sentinel `OfficeActivity` table empty for SharePoint** | Zone 3 SOC sees no SharePoint events | Office 365 connector not enabled in Sentinel, or SharePoint stream not selected | In Sentinel data connectors, confirm Office 365 connector is connected and SharePoint is enabled. See [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |

---

## Diagnostic Steps

### 1. Confirm Licensing (SAM and Copilot)

```powershell
Get-MgSubscribedSku | Where-Object {
    $_.SkuPartNumber -match 'COPILOT|SHAREPOINT_ADVANCED|SPE_E5'
} | Select-Object SkuPartNumber, ConsumedUnits, @{n='Available';e={$_.PrepaidUnits.Enabled - $_.ConsumedUnits}}
```

SAM is included with every Microsoft 365 Copilot license (since January 2025) and is also available as a standalone SKU. If neither appears in the result, request the entitlement before troubleshooting reports further.

### 2. Confirm Audit Ingestion

```powershell
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
```

If `False`, no other monitoring evidence is reliable. Enable ingestion (Purview portal > Audit > Start recording user and admin activity) and wait up to 60 minutes before re-testing.

### 3. Confirm Audit Retention Sufficiency (FSI-Critical)

```powershell
Get-RetentionCompliancePolicy -ErrorAction SilentlyContinue |
    Where-Object { $_.Workload -match 'SharePoint' } |
    Select-Object Name, Enabled, Workload
```

If only Standard (180-day) or Premium (1-year) audit retention is in place, **this is a finding**. SEC 17a-4 / FINRA 4511 typically require 6 years; create a Purview audit retention policy sized to the regulatory window. See [Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies).

### 4. Confirm Privileged Role Assignment (Deterministic)

```powershell
$role = Get-MgDirectoryRole -Filter "displayName eq 'SharePoint Administrator'"
if (-not $role) {
    $template = Get-MgDirectoryRoleTemplate -Filter "displayName eq 'SharePoint Administrator'"
    $role = New-MgDirectoryRole -RoleTemplateId $template.Id
}
Get-MgDirectoryRoleMember -DirectoryRoleId $role.Id -All
```

Avoid `displayName -like '*SharePoint*'`; that pattern can match unrelated objects and produces false positives.

### 5. Force a New DAG Snapshot

If reports look stale: SharePoint Admin Center > **Reports** > **Data access governance** > **Get started** (or **Refresh** if previously initialized). For tenants with more than 10,000 sites, allow several hours for completion before re-checking.

---

## Escalation Path

| Issue Severity | Escalation | Target Response |
|---|---|---|
| Agent insights missing for licensed tenant > 48 hours | SharePoint Admin → Microsoft Support (SharePoint queue) | 2 business days |
| Audit ingestion disabled or returning zero in active tenant | Purview Compliance Admin → Microsoft Support (Compliance queue) | 1 business day |
| Audit retention policy missing or undersized for regulated tenant | Compliance Officer → Internal remediation; treat as **finding** in next attestation | Same day (open ticket) |
| Real-time alert pipeline silent during a known event | Entra Security Admin → SOC + Microsoft Support | Same day |

!!! note "FINRA / SEC examination context"
    If a regulator is on-site, audit-related issues should be escalated immediately to the Compliance Officer and recorded in the examination response log. Do not silently retry — preserve the original failure evidence.

---

## Prevention Best Practices

1. **Pin module versions** through Change Advisory Board approval — floating versions break SOX 404 reproducibility.
2. **Hash every evidence export** at capture time and store the hash in an `EVIDENCE-MANIFEST.csv` file.
3. **Size audit retention to the regulatory window** before relying on Search-UnifiedAuditLog for evidence.
4. **Paginate** all `Search-UnifiedAuditLog` calls — never trust a single 5,000-record fetch.
5. **Route alerts to a monitored shared mailbox**, never a single individual.
6. **Verify role assignment deterministically** via `Get-MgDirectoryRole` — not via `displayName -like` heuristics.
7. **Test the full pipeline quarterly** with a synthetic high-severity event to confirm SOC receives and triages the alert.

---

## Related Resources

- [Agent insights in SharePoint](https://learn.microsoft.com/en-us/sharepoint/insights-on-sharepoint-agents)
- [Data access governance reports](https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports)
- [SharePoint Advanced Management overview](https://learn.microsoft.com/en-us/sharepoint/advanced-management)
- [SharePoint Admin agent overview](https://learn.microsoft.com/en-us/sharepoint/content-governance-agent)
- [Microsoft Purview Audit overview](https://learn.microsoft.com/en-us/purview/audit-solutions-overview)
- [Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies)
- [Search-UnifiedAuditLog cmdlet reference](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog)

---

[Back to Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
