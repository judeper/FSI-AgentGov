# Troubleshooting: Control 1.16 — Information Rights Management (IRM)

**Last Updated:** April 2026

---

## Quick Reference

| Symptom | Likely Cause | First Action |
|---|---|---|
| "Protection is activated" not shown / IRM options missing in Purview | Azure RMS not activated for tenant | Run `Enable-AipService` (Entra Global Admin via PIM) |
| **Information Rights Management** link absent in library settings | Tenant-level SharePoint IRM not enabled | Toggle in SharePoint Admin Center → Access control → IRM |
| Agent returns "Access denied" when grounding on a labeled doc | Agent service identity not in label permissions | Add identity at Viewer in label encryption settings |
| Downloaded files are not protected | Library IRM disabled, or user has Full Control | Enable library IRM; remove unnecessary Full Control |
| Watermark missing | Content marking not enabled or not licensed | Enable in label content marking; check user has AIP P2 / E5 |
| Content expires unexpectedly | License cache interval too low or label expiration set aggressively | Tune `LicenseCacheExpireDays` and label encryption expiration |
| `Track and revoke` shows no events | Document tracking feature disabled or telemetry latency | Verify `Get-AipServiceConfiguration` `DocumentTrackingFeatureState` is `Enabled`; allow up to 60 min |
| Super-user can no longer decrypt | Super-user feature disabled or group membership lost | Re-run `Enable-AipServiceSuperUserFeature` and `Set-AipServiceSuperUserGroup` |
| GCC High tenant: library IRM unavailable | SharePoint list/library IRM is global cloud only | Use label-only protection; document the exception |

---

## Detailed Scenarios

### Scenario A — Azure RMS is Not Activated

**Symptoms**
- Microsoft 365 Admin Center shows the activation banner.
- `Get-AipService` returns `Disabled` or the cmdlet errors with "service not provisioned".
- IRM toggles in SharePoint or label encryption settings appear greyed out.

**Diagnosis**
```powershell
Connect-AipService
Get-AipService
Get-AipServiceConfiguration | Select-Object FunctionalState, LicenseValidityDuration
```

**Resolution**
1. Confirm tenant SKU includes Azure RMS (M365/O365 E3 or higher, Business Premium, or AIP P1/P2).
2. Elevate to Entra Global Admin via Privileged Identity Management.
3. Run `Enable-AipService`. Allow 15–30 minutes for tenant propagation.
4. Re-run Test 1 in [Verification & Testing](verification-testing.md).

---

### Scenario B — Agent Cannot Read IRM-Protected Content

**Symptoms**
- Copilot Studio agent returns a generic "I couldn't find an answer" or surfaces a permission error in trace logs.
- The same content is accessible to interactive users with the same nominal permissions.

**Diagnosis**
1. Identify the agent's effective service identity (Copilot Studio app registration object ID, or the user identity for delegated grounding).
2. Inspect the sensitivity label encryption permissions: does the identity appear, and at what level?
3. Check the SharePoint library permissions for the same identity (IRM does not grant access — it constrains it).
4. Inspect Conditional Access for any policy excluding service principals or applying device compliance to API calls.

**Resolution**
- Add the agent identity to the sensitivity label permissions at **Viewer** level. Co-Author or Co-Owner is overprivileged and creates an egress path that defeats this control.
- Confirm the identity has at least Read at the SharePoint library level.
- Exempt service principals from device-bound Conditional Access where appropriate, or use workload identity policies aligned with [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).

---

### Scenario C — Downloaded Files Are Not Protected

**Symptoms**
- A user downloads a file from an IRM-enabled library and opens it locally with no banner, no restrictions.

**Diagnosis**
1. Confirm library IRM: SharePoint library settings → Information Rights Management → "Restrict permission to documents in this library on download" should be checked.
2. Confirm the downloading user does **not** hold Full Control on the library (Full Control bypasses library IRM in some scenarios).
3. Confirm the file type supports IRM (Office formats and PDF; arbitrary binary types do not protect).

**Resolution**
- Enable library IRM via [Portal Walkthrough Step 4](portal-walkthrough.md#step-4-enable-irm-on-a-sharepoint-document-library) or `Script 3` in [PowerShell Setup](powershell-setup.md).
- Tighten library permissions — Full Control should be limited to the site collection administrators and the compliance super-user group.
- For non-Office file types, layer label-based encryption (which travels with the file) in addition to library IRM, and consider the "Do not allow users to upload documents that do not support IRM" toggle.

---

### Scenario D — Document Tracking Shows No Events After a Confirmed Open

**Symptoms**
- A user opened a tracked document but the event is not visible in the Purview Track and Revoke dashboard.

**Diagnosis**
```powershell
Connect-AipService
(Get-AipServiceConfiguration).DocumentTrackingFeatureState
Disconnect-AipService
```

**Resolution**
- If `DocumentTrackingFeatureState` is `Disabled`, enable it: `Enable-AipServiceDocumentTrackingFeature`.
- Tracking telemetry can take up to 60 minutes to appear; retry after the latency window before escalating.
- Cross-check the Unified Audit Log (`Search-UnifiedAuditLog -Operations RmsAccess,FileAccessed`) — this is the authoritative record source for SOX 404 / FINRA 4511 evidence.

---

### Scenario E — Revocation Does Not Take Effect

**Symptoms**
- A document is revoked in the dashboard, but the previously authorized user can still open the locally cached copy.

**Diagnosis**
- The user's offline use license has not yet expired. Offline license validity is controlled by the **Allow offline access** label setting and the library's **Users must verify their credentials using this interval** setting.

**Resolution**
- Wait out the offline license window (Zone 3 recommended: 7 days). After that, the client must re-acquire a license and revocation is enforced.
- For incidents requiring immediate effect, also revoke at the user identity layer (disable the account, revoke refresh tokens via `Revoke-MgUserSignInSession`) and monitor for tampering.
- For Zone 3, consider reducing offline access to 1 day or 0 (online-only) for the highest-sensitivity label, accepting the user-experience tradeoff.

---

### Scenario F — Super-User Cannot Decrypt for eDiscovery

**Symptoms**
- Compliance super-user receives "You don't have permission" when opening an IRM-protected document during an eDiscovery workflow.

**Diagnosis**
```powershell
Connect-AipService
Get-AipServiceSuperUserFeature
Get-AipServiceSuperUserGroup
Disconnect-AipService
```

**Resolution**
- If feature shows `Disabled`, run `Enable-AipServiceSuperUserFeature`.
- If the group address is empty or wrong, run `Set-AipServiceSuperUserGroup -GroupEmailAddress '<group>@<tenant>'`. The group must be **mail-enabled** (security group + mail or distribution group).
- Confirm the user is a direct or transitive member of the group. Group membership changes can take up to several hours to propagate to RMS.

---

## How to Confirm Configuration is Active

| Layer | Verification command / portal |
|---|---|
| Azure RMS | `Get-AipService` returns `Enabled`; admin center shows "Protection is activated" |
| Sensitivity label encryption | Open label in Purview; confirm Encryption shows "Configure" with permissions populated |
| Tenant SharePoint IRM | SharePoint Admin Center → Access control → IRM = "Use the IRM service…" |
| Library IRM | Library settings → Information Rights Management → checkbox set; or `Get-PnPList -Includes IrmSettings` shows `IrmEnabled = $true` |
| Tracking | `Get-AipServiceConfiguration` `DocumentTrackingFeatureState = Enabled` |
| Super-user | `Get-AipServiceSuperUserFeature = Enabled`; `Get-AipServiceSuperUserGroup` returns expected group |

---

## Escalation Path

1. **Purview Info Protection Admin** — label, encryption, content marking, auto-labeling.
2. **SharePoint Admin** — tenant IRM, library IRM, library permissions.
3. **Entra Global Admin (via PIM)** — Azure RMS activation, super-user feature toggle, application identity scoping.
4. **AI Governance Lead** — agent inventory, agent identity scoping, Zone classification disputes.
5. **Microsoft Support** — platform-side issues (telemetry latency >24h, RMS service errors), open with the AIP / Purview workload tag.

---

## Known Limitations

| Limitation | Impact | Recommended handling |
|---|---|---|
| SharePoint list/library IRM is supported only in the Microsoft global cloud | GCC High and DoD tenants cannot rely on library IRM | Use label-based encryption only; document the exception in the FSI risk register |
| IRM requires IRM-aware client applications | Non-supported apps cannot open protected files | Standardize on current Microsoft 365 Apps for enterprise; restrict third-party PDF readers |
| Mac and mobile clients have reduced IRM features | Some advanced restrictions silently downgrade | Test the target user population's client mix during rollout |
| SharePoint IRM is library-scoped, not item-scoped | Cannot apply different IRM policies to individual files in the same library | Segment libraries by sensitivity, or use sensitivity labels at the file level |
| Offline license validity creates a revocation grace period | Revocation does not take effect until cache expires | Set offline access to 1–7 days for Zone 3; combine with identity-layer revocation in incidents |
| Super-user can decrypt every protected document tenant-wide | High-impact privilege | Limit group to named compliance personnel; review quarterly under [Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) |
| Auto-labeling SLA is best-effort | Newly created files may be unprotected for hours before auto-label applies | Pair with mandatory manual labeling defaults at Office app save |

---

[Back to Control 1.16](../../../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
