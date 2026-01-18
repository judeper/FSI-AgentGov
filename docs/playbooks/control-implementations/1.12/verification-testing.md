# Control 1.12: Insider Risk Detection and Response - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Confirm policies active | All FSI policies enabled |
| 2 | Verify analytics | Analytics showing risk patterns |
| 3 | Test alert generation | Alert generated in queue |
| 4 | Validate workflow | Case created and assignable |
| 5 | Check connectors | Connector status healthy |
| 6 | Review priority groups | Groups configured with members |

---

## Test Cases

### Test 1: Data Leak Detection

1. Simulate bulk file download (test user)
2. Download multiple files from monitored site
3. **Expected:** Alert generated for bulk download activity
4. Review alert in Insider risk management > Alerts

### Test 2: External Sharing Detection

1. Share file externally with test account
2. Create anonymous link for test file
3. **Expected:** Alert generated for risky sharing
4. Verify external user identified in alert

### Test 3: Departing User Workflow

1. Set resignation date for test user in HR connector
2. Trigger download activity
3. **Expected:** Enhanced monitoring alerts triggered
4. Verify departing user policy activation

### Test 4: Investigation Workflow

1. Confirm test alert
2. Create case from alert
3. Assign investigator
4. **Expected:** Case workflow functional
5. Complete investigation with documented resolution

### Test 5: Priority User Monitoring

1. Add test user to priority user group
2. Trigger monitored activity
3. **Expected:** Alert with priority user flag
4. Verify enhanced visibility in dashboard

---

## Evidence Artifacts

- [ ] Screenshot: Policy configurations
- [ ] Export: Alert summary by policy
- [ ] Documentation: Priority user groups
- [ ] Screenshot: Connector status
- [ ] Audit log: Investigation workflow
- [ ] Report: Risk analytics insights
- [ ] Documentation: Escalation procedures

---

## Zone-Specific Testing

### Zone 1 (Personal Productivity)

- Policies: Data leaks (basic)
- Alert threshold: High only
- Investigation: As-needed

### Zone 2 (Team Collaboration)

- Policies: Data leaks + Security violations
- Alert threshold: Medium and above
- Investigation: 48-hour SLA

### Zone 3 (Enterprise Managed)

- Policies: All policies including custom
- Alert threshold: All severities
- Investigation: 4-hour SLA for critical
- Automated response: Access suspension capability

---

## Insider Risk Indicators Testing

| Indicator | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Bulk download | Download 50+ files | Alert generated |
| External email | Email with attachment to external | Alert generated |
| USB copy | Copy file to removable media | Alert generated |
| Print activity | Print sensitive document | Alert generated |
| After-hours access | Access at unusual time | Alert generated |

---

## Confirmation Checklist

- [ ] All insider risk policies created and enabled
- [ ] Analytics enabled and showing insights
- [ ] Priority user groups configured
- [ ] HR connector functional (if used)
- [ ] Investigation settings configured
- [ ] Alert workflow documented
- [ ] Escalation procedures defined
- [ ] Test alerts generated and processed
- [ ] Evidence artifacts collected

---

*Updated: January 2026 | Version: v1.1*
