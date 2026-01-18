# Troubleshooting: Control 2.14 - Training and Awareness Program

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Training not appearing for users | Role mapping incorrect or sync delay | Verify role assignments; wait 24 hours for sync |
| Completion not recording | LMS integration issue | Check LMS connection; verify SCORM compliance |
| Reminders not sending | Email configuration or schedule | Verify email settings; check reminder schedule |
| Compliance report inaccurate | Data sync lag or filter issue | Refresh data; verify report filters |
| Publishing gate not enforcing | Gate not configured or bypass | Verify gate configuration in environment settings |

---

## Detailed Troubleshooting

### Issue: Training Not Appearing for Users

**Symptoms:** Users don't see required training in their queue

**Diagnostic Steps:**

1. Verify user's role assignment:
   ```
   Microsoft Entra Admin Center > Users > [User] > Assigned roles
   ```

2. Check role-to-training mapping in LMS:
   ```
   LMS Admin > Role Mappings > Verify AI Governance training is mapped
   ```

3. Check sync status between identity provider and LMS

4. Verify user is in scope for training (correct department/location)

**Resolution:**

- Correct role assignment if missing
- Update role-to-training mapping
- Force sync if available
- Manually assign training if automation fails

---

### Issue: Completion Not Recording

**Symptoms:** Users complete training but status shows incomplete

**Diagnostic Steps:**

1. Check LMS completion logs for the specific user/course

2. Verify training module is SCORM compliant (if using external content)

3. Check browser console for JavaScript errors during training

4. Verify completion criteria are met (all modules, quiz score, etc.)

**Resolution:**

- Re-mark completion manually if logs show completion
- Fix SCORM package if non-compliant
- Have user complete in different browser
- Adjust completion criteria if too strict

---

### Issue: Publishing Gate Not Enforcing

**Symptoms:** Users without training can still publish agents

**Diagnostic Steps:**

1. Verify environment is Zone 3 (gates only required for Zone 3)

2. Check if user has admin bypass permissions

3. Verify gate is configured in environment settings:
   ```
   PPAC > Environments > [env] > Edit managed environments
   Check for training requirement configuration
   ```

4. Check if training completion data is syncing to Power Platform

**Resolution:**

- Configure publishing gate if missing
- Remove admin bypass if inappropriate
- Fix integration between LMS and Power Platform
- Implement manual approval workflow as interim

---

### Issue: Compliance Report Shows Wrong Data

**Symptoms:** Report numbers don't match actual completion status

**Diagnostic Steps:**

1. Check report generation date vs. data freshness

2. Verify report filters (date range, role, department)

3. Check for duplicate user records

4. Verify data source is correct LMS instance

**Resolution:**

- Refresh report with current data
- Correct filters to match intended scope
- De-duplicate user records
- Point report to correct data source

---

## How to Confirm Configuration is Active

### Via LMS Admin Portal

1. Navigate to LMS Admin > Training Programs
2. Verify AI Governance training is active
3. Check assignment rules are enabled
4. Verify completion tracking is on

### Via Compliance Report

1. Generate a fresh compliance report
2. Verify known-compliant users show as compliant
3. Verify known-non-compliant users show as non-compliant
4. Check totals match expected counts

---

## Escalation Path

If issues persist after troubleshooting:

1. **LMS Administrator** - Training platform configuration
2. **IT Identity Team** - Role assignment and sync issues
3. **AI Governance Lead** - Policy and requirement questions
4. **HR/Learning Team** - Training content and requirements
5. **LMS Vendor Support** - Platform bugs or limitations

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| LMS sync delay | Completion may take 24-48 hours to reflect | Manual verification for urgent cases |
| No native Power Platform training gate | Requires custom integration | Use approval workflows as alternative |
| Limited reporting granularity | May not show sub-module completion | Use LMS native reports for detail |
| External content tracking | Third-party courses may not track properly | Use only SCORM-compliant content |

---

[Back to Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
