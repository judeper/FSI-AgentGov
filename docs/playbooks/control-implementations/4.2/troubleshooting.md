# Control 4.2: Site Access Reviews and Certification — Troubleshooting

> Common issues, diagnostics, and resolutions for [Control 4.2 — Site Access Reviews and Certification](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md).

---

## Quick reference

| Issue | Likely Cause | Resolution |
|---|---|---|
| DAG reports unavailable or "Get started" never completes | SharePoint Advanced Management not licensed; first-run still generating | Confirm SAM license assignment in M365 Admin Center; allow up to 24 hours for first-run pipeline |
| Oversharing baseline / Agent Insights reports missing | SAM tenant not yet receiving the GA roll-out, or report data still ingesting | Confirm tenant region rollout status on the [Microsoft 365 admin center service health page](https://admin.microsoft.com); wait 7 days after enabling SAM |
| Site Access Reviews fail to start with "limit reached" | Tenant has hit the 1,000-review-per-month SAM limit | Wait until next calendar month, or de-prioritize lower-risk reviews; document deferred sites in the exception register |
| Attestation notifications not delivered | Site has no owner, custom template malformed, or Exchange transport rule blocking | Run §Diagnostics check 1 below; validate custom email template renders in test mode; check Exchange message trace |
| Custom email template content not appearing | Template was saved but policy not republished | Re-open the policy and click **Save** to force template binding; then trigger a test notification |
| Site Access Review decisions not auto-applied | `autoApplyDecisionsEnabled` is false, or service consent missing | Update the review definition; reconsent `AccessReview.ReadWrite.All` |
| Entra Access Review never starts | Start date in the future, or no in-scope members | Inspect `recurrence.range.startDate`; confirm scope query returns groups |
| Agent service principal review missing reviewers | Sites.Selected SPs not in a reviewable group | Place agent app SPs into a security group and target the access review at that group; assign AI Governance Lead as reviewer |
| Evidence retention gap flagged in audit | No Purview retention policy / label covers the evidence library | Apply a label with the firm's records retention schedule (≥ 6 years for SEC 17a-4 / FINRA 4511); enable Preservation Lock for Zone 3 |
| `New-MgIdentityGovernanceAccessReviewDefinition` returns 403 | Insufficient Graph scopes consented | Reconnect: `Connect-MgGraph -Scopes 'AccessReview.ReadWrite.All','Directory.Read.All'` |

---

## Detailed scenarios

### Scenario 1 — DAG report set incomplete

**Symptoms:** Site permissions and EEEU reports render, but Oversharing baseline / Agent Insights / Agent Access Insights are missing or empty.

**Diagnostics:**

```powershell
# Confirm SAM is enabled at tenant level
Get-SPOTenant | Select-Object DisableAddToOneDrive, DisableSpacesActivation, ConditionalAccessPolicy, AdvancedManagementEnabled
```

**Resolution:**

1. Confirm SAM Plan 1 (or M365 E5) license assignment at tenant scope.
2. Verify tenant region has received the GA wave for the affected report (Oversharing baseline GA, Agent Insights / Agent Access Insights GA per Microsoft's roadmap).
3. Allow 7 days from initial SAM enablement for ingestion to populate.
4. If still empty after 7 days, open a Microsoft support case and reference the report name and tenant id.

---

### Scenario 2 — Attestation notifications not delivered

**Symptoms:** Site attestation policy is active, but site owners report no email.

**Diagnostics:**

```powershell
# 1. Owners assigned?
Get-SPOSite -Identity 'https://contoso.sharepoint.com/sites/MarketRisk' |
    Select-Object Url, Owner, SecondaryContact

# 2. Bulk orphan scan
Get-SPOSite -Limit All -IncludePersonalSite:$false |
    Where-Object { [string]::IsNullOrWhiteSpace($_.Owner) } |
    Select-Object Url, Title, Template
```

**Resolution:**

1. Assign owners to orphaned sites: `Set-SPOSite -Identity $url -Owner 'newowner@contoso.com'`.
2. In the Site Attestation Policy, click **Customize email template** → **Send test** to verify rendering.
3. Run an Exchange Online message trace from the SAM service mail-from address to the owner; check transport rules for blocks on automated mail.
4. Confirm the owner mailbox is licensed and not in litigation hold-only state (which can suppress some notifications).

---

### Scenario 3 — Decisions not auto-applied

**Symptoms:** Reviewers complete the access review but denied users still hold membership.

**Diagnostics:**

```powershell
$reviewId = '<your-review-id>'
$def = Get-MgIdentityGovernanceAccessReviewDefinition -AccessReviewScheduleDefinitionId $reviewId
$def.Settings | Select-Object AutoApplyDecisionsEnabled, DefaultDecision, DefaultDecisionEnabled

Get-MgIdentityGovernanceAccessReviewDefinitionInstance -AccessReviewScheduleDefinitionId $reviewId |
    Select-Object Id, Status, ReviewersTotal, ReviewersCompleted
```

**Resolution:**

1. If `AutoApplyDecisionsEnabled` is false, update the definition body and `PATCH` it back via Graph.
2. Confirm the running service principal (yours, or the automation identity) has `AccessReview.ReadWrite.All` consented at admin level.
3. For groups synced from on-premises Active Directory, auto-apply is **not supported** — write-back must occur through your AD provisioning system. Document this as a residual control gap and resolve via the on-premises change ticket.
4. Re-run the cycle; verify the `AccessReviewDecisionApplied` event appears in the unified audit log.

---

### Scenario 4 — Sites.Selected agent permissions not reviewed

**Symptoms:** AI agent app registrations holding Sites.Selected do not appear in any quarterly review.

**Diagnostics:**

```powershell
$graph = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
$role  = ($graph.AppRoles | Where-Object Value -eq 'Sites.Selected').Id
Get-MgServicePrincipal -All |
    Where-Object {
        Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $_.Id -ErrorAction SilentlyContinue |
            Where-Object { $_.AppRoleId -eq $role -and $_.ResourceId -eq $graph.Id }
    } |
    Select-Object DisplayName, AppId, Id
```

**Resolution:**

1. Create a security group named e.g. `sg-fsi-ai-agents-sites-selected`.
2. Add each enumerated agent service principal to the group (service principals can be members of security groups via Graph).
3. Schedule a quarterly Entra Access Review against that group with the **AI Governance Lead** as reviewer and **Auto-apply** + **Deny on no response** turned on.
4. Document the group membership process in the Agent Inventory ([Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)).

---

### Scenario 5 — Tenant 1,000-review monthly limit reached

**Symptoms:** Attempt to start a new Site Access Review fails with a quota / limit error.

**Resolution:**

1. Run the trailing-30-day count of initiated reviews from the SAM portal.
2. Re-prioritize: complete reviews on EEEU-shared and high-Copilot-traffic sites first.
3. Defer lower-priority reviews to the next calendar month and record deferral with named approver in the exception register.
4. For sites that cannot wait, apply [Control 4.1 (Restricted Content Discovery)](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) as a compensating control to remove the site from Microsoft 365 Copilot grounding while waiting.

---

## Diagnostic commands

```powershell
# One-shot 4.2 health summary
Connect-MgGraph -Scopes 'AccessReview.Read.All','Sites.Read.All','Application.Read.All' | Out-Null
Connect-SPOService -Url 'https://contoso-admin.sharepoint.com'

Write-Host "=== Control 4.2 Diagnostic ===" -ForegroundColor Cyan

# Reviews
$reviews = Get-MgIdentityGovernanceAccessReviewDefinition -All
"Reviews defined : $($reviews.Count)"
$reviews | Group-Object Status | Format-Table Name, Count

# Orphan sites
$orphans = Get-SPOSite -Limit All -IncludePersonalSite:$false |
    Where-Object Template -notlike 'SPSPERS*' |
    Where-Object { [string]::IsNullOrWhiteSpace($_.Owner) }
"Orphan sites    : $($orphans.Count)"

# Recent attestation activity in audit log (manual lookup recommended)
"Audit operations to spot-check in Purview:"
@('AccessReviewCreate','AccessReviewInstanceComplete','AccessReviewDecisionApplied','SiteAttestationCompleted') |
    ForEach-Object { "  - $_" }
```

---

## Escalation path

1. **Level 1 — SharePoint Admin:** DAG report generation, Site Attestation Policy configuration, custom email templates, Site Access Review initiation
2. **Level 2 — Entra Identity Governance Admin:** Entra Access Review schedule definitions, auto-apply behavior, Sites.Selected service principal reviews
3. **Level 3 — Purview Records Manager:** Retention label / policy assignment to evidence repository, Preservation Lock
4. **Level 4 — Microsoft Support:** Tenant rollout status for SAM features, audit log latency, product defects
5. **Level 5 — AI Governance Committee + Compliance Officer:** Policy exceptions, scope decisions, exception register approvals

---

## How to confirm configuration is active

### Via SharePoint Admin Center

1. **Reports → Data access governance** — every report shows a refresh timestamp within 30 days
2. **Policies → Site lifecycle management → Site attestation policies** — at least one policy in **Active** state, scoped by sensitivity label

### Via Microsoft Entra Admin Center

1. **Identity governance → Access reviews** — quarterly review on M365 Groups visible with **Auto-apply** = On
2. Separate review covers Sites.Selected service principals with the AI Governance Lead listed as reviewer

### Via Microsoft Purview portal

1. **Data lifecycle management → Retention policies / labels** — coverage on the evidence library, retention ≥ 6 years, Preservation Lock on for Zone 3
2. **Audit** — `AccessReview*` and `SiteAttestationCompleted` operations present for the last cycle

### Via PowerShell

```powershell
# 60-second active-config check
Connect-MgGraph -Scopes 'AccessReview.Read.All' | Out-Null
Connect-SPOService -Url 'https://contoso-admin.sharepoint.com'

$reviews = Get-MgIdentityGovernanceAccessReviewDefinition -All |
    Where-Object Status -in @('Initialized','InProgress')
$sites   = Get-SPOSite -Limit All -IncludePersonalSite:$false |
    Where-Object Template -notlike 'SPSPERS*'
$orphan  = ($sites | Where-Object { [string]::IsNullOrWhiteSpace($_.Owner) }).Count

"Active reviews  : $($reviews.Count)"
"Sites total     : $($sites.Count)"
"Orphan sites    : $orphan  (must be 0 for full attestation coverage)"
```

---

[Back to Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.6.2*
