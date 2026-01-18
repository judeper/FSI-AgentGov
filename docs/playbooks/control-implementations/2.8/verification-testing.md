# Verification & Testing: Control 2.8 - Access Control and Segregation of Duties

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Security Groups

1. Open Entra Admin Center > Groups
2. Search for "SG-Agent-"
3. Verify all 5 governance groups exist
4. **EXPECTED:** All groups present with appropriate membership

### Test 2: Verify SoD Enforcement

1. Attempt to add same user to SG-Agent-Developers AND SG-Agent-Approvers
2. Submit an agent for approval as that user
3. Attempt to approve as the same user
4. **EXPECTED:** Approval should be blocked (SoD violation)

### Test 3: Verify PIM Activation

1. Sign in as user eligible for Platform Admin role
2. Navigate to PIM > My roles
3. Activate the Platform Admin role
4. **EXPECTED:** Requires justification and/or approval

### Test 4: Verify Access Review

1. Navigate to Identity Governance > Access reviews
2. Confirm quarterly review is scheduled
3. Check last review completion rate
4. **EXPECTED:** Reviews scheduled, >95% completion

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.8-01 | All security groups exist | 5 groups present | |
| TC-2.8-02 | Groups have correct membership | Roles properly assigned | |
| TC-2.8-03 | SoD blocks creator self-approval | Approval rejected | |
| TC-2.8-04 | PIM requires justification | Activation requires reason | |
| TC-2.8-05 | Access review scheduled | Quarterly cadence set | |
| TC-2.8-06 | No user in conflicting roles | SoD check passes | |

---

## Evidence Collection Checklist

- [ ] Screenshot: Security groups list
- [ ] Screenshot: Group membership for each role
- [ ] Screenshot: PIM eligible assignments
- [ ] Screenshot: Access review schedule
- [ ] Export: SoD validation report (CSV)
- [ ] Screenshot: Approval workflow blocking self-approval

---

## Attestation Statement Template

```markdown
## Control 2.8 Attestation - Access Control and Segregation of Duties

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Security groups are established for agent governance roles:
   - Developers: [Count] members
   - Reviewers: [Count] members
   - Approvers: [Count] members
   - Release Managers: [Count] members
   - Platform Admins: [Count] members

2. Segregation of duties is enforced:
   - Creators cannot approve own work
   - Approvers cannot deploy
   - No single person can complete end-to-end deployment

3. Privileged Identity Management is configured:
   - Admin roles require activation
   - Activation requires justification
   - [Approval required for Zone 3: Yes/No]

4. Access reviews are scheduled:
   - Frequency: [Quarterly/Monthly]
   - Last review: [Date]
   - Completion rate: [Percentage]

**Last SoD Audit:** [Date]
**Violations Found:** [Count or None]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
