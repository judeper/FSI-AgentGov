# Verification & Testing: Control 2.14 - Training and Awareness Program

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Training Content Availability

1. Sign in to LMS/Viva Learning as a test user
2. Search for "AI Governance" training
3. **EXPECTED:** Training modules are discoverable and accessible

### Test 2: Verify Role-Based Assignment

1. Assign a test user to a role requiring training (e.g., maker role)
2. Check that training is assigned automatically
3. **EXPECTED:** Training appears in user's required learning queue

### Test 3: Verify Completion Tracking

1. Have a test user complete a training module
2. Check completion records in LMS/admin portal
3. **EXPECTED:** Completion is recorded with date/time and user ID

### Test 4: Verify Reminder Notifications

1. Create a test user with overdue training
2. Wait for reminder cycle or trigger manually
3. **EXPECTED:** Reminder email/notification sent to user

### Test 5: Verify Publishing Gate (Zone 3)

1. Attempt to publish an agent as a user without completed training
2. **EXPECTED:** Publishing blocked with message about required training

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.14-01 | Training content accessible in LMS | Content available | |
| TC-2.14-02 | Role assignment triggers training | Training auto-assigned | |
| TC-2.14-03 | Training completion recorded | Completion logged | |
| TC-2.14-04 | Overdue training triggers reminder | Reminder sent | |
| TC-2.14-05 | Untrained user blocked from publishing (Zone 3) | Publishing blocked | |
| TC-2.14-06 | Compliance report shows accurate data | Report matches records | |
| TC-2.14-07 | Training evidence exportable | Evidence can be exported | |

---

## Evidence Collection Checklist

### Training Configuration

- [ ] Screenshot: LMS showing AI Governance training modules
- [ ] Screenshot: Role-to-training mapping configuration
- [ ] Screenshot: Reminder schedule configuration
- [ ] Export: Training module list with descriptions

### Compliance Records

- [ ] Export: Training completion report (CSV/Excel)
- [ ] Screenshot: Compliance dashboard showing completion rates
- [ ] Export: Non-compliant users list with follow-up dates
- [ ] Screenshot: Evidence retention settings

### Process Documentation

- [ ] Document: Training requirements by role
- [ ] Document: Training refresh schedule
- [ ] Document: Exception handling process
- [ ] Document: Escalation path for non-compliance

---

## Evidence Artifact Naming Convention

```
Control-2.14_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-2.14_TrainingModules_20260115.png
- Control-2.14_ComplianceReport_20260115.csv
- Control-2.14_RoleMapping_20260115.xlsx
- Control-2.14_ReminderConfig_20260115.png
```

---

## Attestation Statement Template

```markdown
## Control 2.14 Attestation - Training and Awareness Program

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. AI governance training content is available and current
2. Training is assigned based on role and governance tier
3. Completion tracking is enabled and accurate
4. Reminder notifications are configured and functioning
5. Compliance reports are generated [frequency]
6. Training evidence is retained per policy
7. [Zone 3 only] Publishing gates enforce training completion

**Current Compliance Rate:** [X]%
**Target Compliance Rate:** [X]%

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
