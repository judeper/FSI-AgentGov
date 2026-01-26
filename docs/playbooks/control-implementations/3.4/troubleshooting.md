# Control 3.4: Incident Reporting and Root Cause Analysis - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

---

## Common Issues and Resolutions

### Issue: Incidents Not Auto-Assigning

**Symptoms:** New incidents remain unassigned

**Resolution:**

1. Check Power Automate flow is enabled
2. Verify on-call assignment logic
3. Confirm user accounts exist in lookup
4. Check flow run history for errors

---

### Issue: SLA Alerts Not Triggering

**Symptoms:** Overdue incidents not generating alerts

**Resolution:**

1. Verify scheduled flow is running
2. Check SLA threshold configuration
3. Confirm email delivery settings
4. Test with shorter SLA for validation

---

### Issue: RCA Template Not Saving

**Symptoms:** Root cause analysis forms fail to save

**Resolution:**

1. Check required field validation
2. Verify user has Contribute permissions
3. Ensure document library is not locked
4. Check for character limit issues

---

### Issue: Regulatory Notification Workflow Not Triggering

**Symptoms:** Incidents with regulatory impact not flagged

**Resolution:**

1. Verify RegulatoryImpact field is set correctly
2. Check notification workflow conditions
3. Confirm compliance team distribution list
4. Test workflow with manual trigger

---

## Diagnostic Commands

```powershell
# Check for open incidents past SLA
$openIncidents = Get-PnPListItem -List "AI Agent Incidents" -Query "<View><Query><Where><Neq><FieldRef Name='Status'/><Value Type='Text'>Closed</Value></Neq></Where></Query></View>"

foreach ($incident in $openIncidents) {
    $hoursOpen = ((Get-Date) - [DateTime]$incident["ReportedDate"]).TotalHours
    Write-Host "$($incident['IncidentID']): $([math]::Round($hoursOpen, 1)) hours open - $($incident['Severity'])"
}

# Check Power Automate flow status
Get-AdminFlow -EnvironmentName "Default" | Where-Object { $_.DisplayName -like "*Incident*" }
```

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| Critical incident stuck | CISO | Immediate |
| SLA system failure | IT Operations | 1 hour |
| Notification failures | Platform Admin | 4 hours |
| Reporting inaccuracies | AI Governance Lead | 24 hours |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.2*
