# Troubleshooting: Control 1.16 - Information Rights Management (IRM)

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Azure RMS not activated | Tenant configuration | Activate via admin center or PowerShell |
| Agent cannot read IRM content | Missing permissions | Add service account to label permissions |
| IRM not applying on download | Library setting not enabled | Enable IRM on document library |
| Content expiration too soon | Policy misconfiguration | Adjust expiration in label settings |
| Watermark not appearing | Content marking disabled | Enable watermark in label |

---

## Detailed Troubleshooting

### Issue: Azure RMS Not Activated

**Symptoms:** Protection options not available, IRM features missing

**Diagnostic Steps:**

1. Check RMS status:
   ```powershell
   Connect-AipService
   Get-AipService
   ```

2. Verify license includes RMS (E3/E5, AIP P1/P2)

**Resolution:**

```powershell
# Activate Azure RMS
Connect-AipService
Enable-AipService
```

Wait 15-30 minutes for propagation.

---

### Issue: Agent Cannot Read IRM-Protected Content

**Symptoms:** Agent returns error when accessing protected documents

**Diagnostic Steps:**

1. Verify agent service account identity
2. Check sensitivity label permissions
3. Review agent authentication method

**Resolution:**

- Add agent service account to sensitivity label permissions
- Grant "Viewer" permission level minimum
- Verify service account can authenticate to Azure AD
- Check for any Conditional Access policies blocking access

---

### Issue: IRM Not Applying to Downloaded Documents

**Symptoms:** Documents download without protection

**Diagnostic Steps:**

1. Verify library IRM is enabled:
   ```
   Library Settings > Information Rights Management
   ```

2. Check if user has full control (bypasses IRM)
3. Verify document is in library (not just uploaded)

**Resolution:**

- Enable IRM on the specific library
- Remove full control if not needed
- Ensure document is checked in
- Wait for sync if recently enabled

---

### Issue: Content Expires Too Soon

**Symptoms:** Users lose access before expected

**Diagnostic Steps:**

1. Review sensitivity label expiration settings
2. Check library IRM expiration
3. Verify offline access period

**Resolution:**

- Adjust label encryption expiration period
- Update library IRM settings
- Extend offline access days
- Communicate expiration policies to users

---

### Issue: Super User Access Not Working

**Symptoms:** Compliance team cannot access protected content for review

**Diagnostic Steps:**

1. Verify super user feature is enabled
2. Check super user group membership
3. Confirm no conflicting policies

**Resolution:**

```powershell
# Enable super user feature
Connect-AipService
Enable-AipServiceSuperUserFeature

# Add super user group
Add-AipServiceSuperUser -Group "SG-Compliance-SuperUsers"
```

---

## How to Confirm Configuration is Active

### Azure RMS

1. Run `Get-AipService` - should return "Enabled"
2. Check admin center shows "Protection is activated"

### Sensitivity Labels

1. Create test document
2. Apply IRM-enabled label
3. Share with non-privileged user
4. Verify restrictions are enforced

### SharePoint Library IRM

1. Upload document to IRM library
2. Download from different account
3. Verify protection is applied

---

## Escalation Path

If issues persist after troubleshooting:

1. **Purview Info Protection Admin** - Label configuration
2. **SharePoint Admin** - Library settings
3. **Security Admin** - RMS activation
4. **Microsoft Support** - Platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| IRM requires supported apps | Some apps cannot open protected files | Use supported Office versions |
| Mac/mobile limited support | Some features unavailable | Test on target platforms |
| SharePoint IRM is library-level | Cannot protect individual files differently | Use multiple libraries or labels |
| Offline access required | No offline = no access when disconnected | Set appropriate offline period |
| Super user can bypass all | Security consideration | Limit super user membership |

---

[Back to Control 1.16](../../../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
