# Control 1.6: Microsoft Purview DSPM for AI - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

---

## Common Issues

### Issue: DSPM Dashboard Shows No AI Interactions

**Symptoms:** Overview displays zero interactions despite active Copilot usage

**Solutions:**

1. Verify unified audit logging is enabled (Get Started step 1)
2. Check that users have Microsoft 365 Copilot licenses assigned
3. Wait 24-48 hours for initial data population
4. Verify date range filter in reports
5. Confirm users are actually using Copilot features

---

### Issue: Browser Extension Not Capturing Third-Party AI

**Symptoms:** ChatGPT, Claude, other AI usage not appearing in reports

**Solutions:**

1. Verify extension deployment via Intune/Endpoint Manager
2. Check extension is enabled in user browsers
3. Confirm AI domains are in the monitored list
4. Verify users are signed in to browser with work account
5. Check extension version is current

---

### Issue: Recommendations Not Updating

**Symptoms:** Completed actions still show as pending in Recommendations

**Solutions:**

1. Manually mark recommendation as complete if action was taken
2. Refresh the browser/dashboard
3. Wait for sync (can take up to 24 hours)
4. Verify the action was fully completed in source system
5. Contact Microsoft support if stuck for >48 hours

---

### Issue: Activity Explorer Missing Expected Events

**Symptoms:** Known AI interactions not appearing in Activity explorer

**Solutions:**

1. Adjust date range filter to include event timeframe
2. Check filter settings (user, app, activity type)
3. Verify audit retention policy hasn't deleted events
4. Confirm user/app is in scope for monitoring
5. Export all data and search manually if needed

---

### Issue: Oversharing Assessment Returns Errors

**Symptoms:** Data risk assessment fails or shows errors

**Solutions:**

1. Verify SharePoint sites are accessible
2. Check permissions to run assessments
3. Ensure sites aren't in a locked/read-only state
4. Reduce scope and retry with smaller site set
5. Check service health for Purview/SharePoint issues

---

### Issue: DSPM for AI Not Visible in Navigation

**Symptoms:** Cannot find DSPM for AI in Purview portal

**Solutions:**

1. Verify E5 or E5 Compliance license is assigned
2. Check Purview Compliance Admin role is assigned
3. Clear browser cache and refresh
4. Try a different browser
5. Verify tenant region supports DSPM for AI

---

### Issue: Policies Not Syncing from Other Solutions

**Symptoms:** DLP or IRM policies not appearing in DSPM Policies view

**Solutions:**

1. Verify policies exist in their native solution
2. Check policy is enabled (not in test mode only)
3. Wait for sync (can take several hours)
4. Refresh the DSPM Policies page
5. Verify permissions to view policies

---

## Escalation Path

If issues persist after troubleshooting:

1. **First tier**: Purview Compliance Admin - verify configuration
2. **Second tier**: Security Operations - check integration issues
3. **Third tier**: Microsoft Support - platform-level issues

---

*Updated: January 2026 | Version: v1.2*
