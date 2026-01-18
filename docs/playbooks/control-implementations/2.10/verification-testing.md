# Verification & Testing: Control 2.10 - Patch Management and System Updates

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Message Center Notifications

1. Check email for recent Message Center digest
2. **EXPECTED:** Power Platform updates received

### Test 2: Verify Test Environment

1. Open PPAC and locate test environment
2. Verify configuration mirrors production
3. **EXPECTED:** Test environment ready for validation

### Test 3: Verify Maintenance Windows

1. Request maintenance window documentation
2. **EXPECTED:** Windows defined per zone

### Test 4: Verify Patch Documentation

1. Request recent patch documentation
2. Verify includes impact assessment and test results
3. **EXPECTED:** Complete documentation trail

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.10-01 | Message Center notifications | Updates received | |
| TC-2.10-02 | Service Health alerts | Alerts trigger | |
| TC-2.10-03 | Test environment ready | Mirrors production | |
| TC-2.10-04 | Maintenance windows defined | Per zone documented | |
| TC-2.10-05 | Patch history maintained | Log current | |

---

## Evidence Collection Checklist

- [ ] Screenshot: Message Center preferences
- [ ] Screenshot: Service Health alert configuration
- [ ] Screenshot: Test environment settings
- [ ] Document: Maintenance window schedule
- [ ] Export: Patch history log

---

## Attestation Statement Template

```markdown
## Control 2.10 Attestation - Patch Management

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Message Center notifications are configured for Power Platform updates
2. Service Health alerts are active for critical services
3. Test environment exists for update validation
4. Maintenance windows are defined:
   - Zone 1: [Schedule]
   - Zone 2: [Schedule]
   - Zone 3: [Schedule]
5. Patch history is documented per change management policy

**Last Patch Applied:** [Date]
**Test Environment Name:** [Name]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.10](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
