# Troubleshooting: Control 1.17 - Endpoint Data Loss Prevention

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Device not appearing in Purview | Onboarding incomplete | Complete Defender onboarding |
| Policy not enforcing | Policy in test mode | Enable enforcement mode |
| USB not blocked | Device not in policy scope | Add device group to policy |
| No activity logged | Audit not enabled | Enable activity logging |
| False positives | SIT too broad | Tune confidence levels |

---

## Detailed Troubleshooting

### Issue: Device Not Appearing in Purview

**Symptoms:** Device is onboarded to Defender but not showing in Endpoint DLP

**Diagnostic Steps:**

1. Verify device in Defender portal:
   ```
   security.microsoft.com > Assets > Devices
   Check health status
   ```

2. Check device meets requirements:
   - Windows 10 1809+ or Windows 11
   - macOS Catalina 10.15+
   - Correct licensing

3. Verify DLP sensor is running on device

**Resolution:**

- Re-onboard device if status is unhealthy
- Verify E5 license is assigned
- Check for conflicting endpoint protection
- Wait 24-48 hours for initial sync

---

### Issue: Policy Not Enforcing

**Symptoms:** Actions that should be blocked are allowed

**Diagnostic Steps:**

1. Check policy mode:
   ```
   Purview > DLP > Policies > [Policy]
   Check if mode is "Enable" vs "Test"
   ```

2. Verify policy locations include "Devices"
3. Check if device is in policy scope

**Resolution:**

- Change policy mode from Test to Enable
- Verify device group is in policy scope
- Check for policy priority conflicts
- Review rule conditions

---

### Issue: USB Transfer Not Blocked

**Symptoms:** Sensitive files copy to USB without restriction

**Diagnostic Steps:**

1. Verify USB restriction settings:
   ```
   Purview > Endpoint DLP settings > Device properties
   ```

2. Check if USB device is on allowed list
3. Verify file contains sensitive data matching SITs

**Resolution:**

- Remove USB from allowed devices list
- Verify SIT definitions match test content
- Check USB restriction is set to Block (not Audit)
- Verify device receives policy updates

---

### Issue: No Activity Being Logged

**Symptoms:** No events appear in Activity Explorer for endpoint actions

**Diagnostic Steps:**

1. Verify audit logging is enabled
2. Check device connectivity to cloud
3. Review time range in Activity Explorer

**Resolution:**

- Enable "Always audit file activities for devices"
- Verify device has internet connectivity
- Wait 15-30 minutes for events to appear
- Check for service health issues

---

### Issue: High False Positive Rate

**Symptoms:** Legitimate actions blocked incorrectly

**Diagnostic Steps:**

1. Review blocked events in Activity Explorer
2. Identify patterns in false positives
3. Review SIT confidence levels

**Resolution:**

- Increase confidence threshold (65 → 75 → 85)
- Add exceptions for specific files/folders
- Create user override workflow
- Tune SIT patterns

---

## How to Confirm Configuration is Active

### Device Status

1. Open Defender portal > Assets > Devices
2. Verify device shows "Active" and healthy
3. Check last activity time is recent

### Policy Status

1. Open Purview > DLP > Policies
2. Verify policy shows "On" status
3. Check policy locations include "Devices"

### Test Enforcement

1. Create test file with sensitive pattern (e.g., fake SSN)
2. Attempt blocked action (USB copy, cloud upload)
3. Verify block notification appears
4. Check event in Activity Explorer

---

## Escalation Path

If issues persist after troubleshooting:

1. **Purview Compliance Admin** - Policy configuration
2. **Defender Admin** - Device onboarding
3. **Intune Admin** - Device deployment
4. **Microsoft Support** - Platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| macOS limited features | Fewer restrictions available | Focus on Windows for Zone 3 |
| Browser restrictions browser-specific | Not all browsers supported | Use managed Edge browser |
| Offline enforcement delayed | May take time to sync | Use always-on VPN |
| No native mobile support | Mobile devices not covered | Use MAM policies instead |
| VM detection limited | Some VMs not fully supported | Test on target platforms |

---

[Back to Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
