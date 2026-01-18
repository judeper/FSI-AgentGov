# Verification & Testing: Control 1.22 - Information Barriers

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Segment Membership

1. Select test user from Research department
2. Verify user is in IB-Research segment
3. **EXPECTED:** User correctly assigned to segment

### Test 2: Test Barrier Enforcement

1. Log in as Research user
2. Attempt to access Trading content via agent
3. **EXPECTED:** Access blocked by Information Barrier

### Test 3: Test Wall-Crossing Workflow

1. Submit wall-crossing request
2. Verify approval routing to Compliance
3. **EXPECTED:** Request routes correctly

### Test 4: Verify SharePoint Alignment

1. Check Research SharePoint site permissions
2. Verify Trading users cannot access
3. **EXPECTED:** Permissions align with barriers

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.22-01 | Segments defined | All units covered | |
| TC-1.22-02 | Barrier blocks Research-Trading | Access denied | |
| TC-1.22-03 | Barrier blocks IB-Sales | Access denied | |
| TC-1.22-04 | Wall-crossing workflow | Approval required | |
| TC-1.22-05 | SharePoint aligned | Permissions match | |

---

## Evidence Collection Checklist

- [ ] Export: Organization segments (CSV)
- [ ] Export: Barrier policies (CSV)
- [ ] Screenshot: Policy application status
- [ ] Document: Wall-crossing procedure

---

## Attestation Statement Template

```markdown
## Control 1.22 Attestation - Information Barriers

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Organization segments are defined for:
   - Research, Trading, Investment Banking, Sales, Compliance
2. Barrier policies are active between designated segments
3. Wall-crossing workflow requires multi-level approval
4. SharePoint permissions align with barrier policies
5. Barrier events are logged and retained 6+ years

**Segments:** [Count]
**Active Policies:** [Count]
**Last Review:** [Date]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
