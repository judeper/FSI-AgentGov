# Troubleshooting: Control 2.12 - Supervision and Oversight

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| HITL not triggering | Topic not configured | Add review requirement to topic |
| Review queue backed up | Insufficient reviewers | Add more designated principals |
| Evidence not captured | Logging flow broken | Verify Power Automate flow |
| Principal not available | Scheduling conflict | Ensure backup supervisors |

---

## Detailed Troubleshooting

### Issue: HITL Not Triggering

**Symptoms:** Agent sends responses without supervisor review

**Resolution:**

1. Verify generative answers review is enabled
2. Check topic configuration for review requirement
3. Verify user is accessing Zone 3 agent
4. Test with explicit high-risk prompt

---

### Issue: Review Queue Backed Up

**Symptoms:** Reviews pending longer than SLA

**Resolution:**

1. Add additional designated principals
2. Implement escalation for SLA breach
3. Review sampling rates (may be too aggressive)
4. Automate low-risk approvals where appropriate

---

## Escalation Path

1. **Compliance Officer** - WSP requirements
2. **Designated Principal** - Review decisions
3. **AI Governance Lead** - Configuration issues
4. **CISO** - SLA breaches

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No native HITL analytics | Manual reporting | Build Power BI dashboard |
| Real-time review challenging | May slow responses | Balance sampling vs. risk |
| FINRA-specific requirements | Must customize | Document WSP thoroughly |
| Multiple agent channels | Complex supervision | Standardize review process |

---

[Back to Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
