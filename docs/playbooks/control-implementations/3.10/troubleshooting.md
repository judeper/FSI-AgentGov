# Control 3.10: Hallucination Feedback Loop - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md).

---

## Common Issues and Resolutions

### Issue: Feedback Not Being Captured

**Symptoms:** Users report feedback but no tracking items created

**Resolution:**

1. Verify feedback is enabled in agent settings
2. Check Power Automate flow is enabled
3. Verify list permissions allow item creation
4. Review flow run history for errors
5. Test with manual feedback submission

---

### Issue: High Volume Overwhelming Team

**Symptoms:** Too many reports to process

**Resolution:**

1. Implement auto-categorization based on keywords
2. Add severity-based prioritization
3. Consider batch processing for low-severity
4. Review thresholds for escalation
5. Add automated resolution for common issues

---

### Issue: Trend Alerts Not Triggering

**Symptoms:** High rate agents not flagged

**Resolution:**

1. Verify scheduled flow is running
2. Check threshold configuration
3. Confirm agent matching logic
4. Test with lower threshold

---

### Issue: MTTR Calculation Incorrect

**Symptoms:** Average resolution time wrong

**Resolution:**

1. Verify resolution date field populated
2. Check date format consistency
3. Exclude open issues from calculation
4. Review timezone handling

---

### Issue: Remediation Not Preventing Recurrence

**Symptoms:** Same hallucination repeats

**Resolution:**

1. Verify root cause correctly identified
2. Confirm knowledge source actually updated
3. Test agent with same query
4. Check for caching issues
5. Document in repeat tracking

---

## Diagnostic Commands

```powershell
# Check recent hallucination reports
Get-PnPListItem -List "Hallucination Tracking" -Query "<View><Query><Where><Geq><FieldRef Name='Created'/><Value Type='DateTime'><Today OffsetDays='-7'/></Value></Geq></Where></Query></View>" | Select-Object Id, Title

# Check open issues count
(Get-PnPListItem -List "Hallucination Tracking" | Where-Object { $_["Status"] -ne "Closed" }).Count

# Verify flow status
Get-AdminFlow -EnvironmentName "Default" | Where-Object { $_.DisplayName -like "*Hallucination*" }
```

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| Customer harm | Compliance + Legal | Immediate |
| High volume backlog | AI Governance Lead | 24 hours |
| Tracking system failure | Platform Admin | 4 hours |
| Repeat critical | QA Lead | 24 hours |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.1*
