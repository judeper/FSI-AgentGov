# Control 1.10: Communication Compliance Monitoring - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Confirm policies active | All FSI policies listed and enabled |
| 2 | Test detection | Alert generated within SLA |
| 3 | Verify reviewer access | Pending alerts visible to analysts |
| 4 | Test escalation | Escalation notification sent |
| 5 | Validate audit evidence | Audit log returns relevant events |
| 6 | Validate retention | Communications retained per policy |

---

## Test Cases

### Test 1: Inappropriate Content Detection

1. Send test message containing harassment keywords
2. Wait for policy processing (up to 24 hours)
3. **Expected:** Alert generated for inappropriate content
4. Review alert in Communication Compliance queue

### Test 2: Regulatory Violation Detection

1. Send test message with regulatory violation keywords
2. Example: "This is a guaranteed return investment"
3. **Expected:** Alert generated for regulatory violation
4. Verify correct policy matched

### Test 3: Sensitive Information Detection

1. Send test message with sensitive data patterns
2. Example: Test credit card number format
3. **Expected:** Alert generated for sensitive data
4. Verify SIT correctly identified

### Test 4: Reviewer Workflow

1. Log in as Communication Compliance Analyst
2. Navigate to alert queue
3. **Expected:** Test alerts visible
4. Process alert through triage workflow
5. **Expected:** Disposition options available

### Test 5: Escalation Flow

1. Escalate test alert to investigator
2. **Expected:** Investigator receives notification
3. Log in as investigator
4. **Expected:** Escalated alert visible with context

---

## Evidence Artifacts

- [ ] Screenshot: Policy configurations (scope, locations, conditions)
- [ ] Export: Policy list and alert statistics
- [ ] Documentation: Reviewer assignments and SLAs
- [ ] Screenshot: Classifier enablement
- [ ] Audit log export: Policy and reviewer actions
- [ ] Sample case records: Disposition rationale and evidence
- [ ] Report: Periodic compliance summary

---

## Zone-Specific Testing

### Zone 1 (Personal Productivity)

- Monitoring: Basic (harassment, threats)
- Review frequency: Weekly sampling
- Escalation: HR only

### Zone 2 (Team Collaboration)

- Monitoring: Standard (inappropriate + regulatory)
- Review frequency: Daily
- Escalation: Compliance + HR

### Zone 3 (Enterprise Managed)

- Monitoring: Comprehensive (all scenarios)
- Review frequency: Real-time for high-risk
- Escalation: Compliance + Legal + Regulators
- AI classifiers: All enabled

---

## FSI Detection Scenario Testing

| Scenario | Test Pattern | Expected Action |
|----------|--------------|-----------------|
| Unsuitable Recommendations | "guaranteed", "risk-free" | Alert + Review |
| MNPI Indicators | "before announcement", "insider" | Alert + Immediate Review |
| Churning Indicators | "trade more", "increase activity" | Alert + Investigation |
| Conflicts of Interest | "my account", "personal trades" | Alert + Ethics Review |
| Customer Complaints | "complaint", "dispute" | Alert + Service Management |

---

## Confirmation Checklist

- [ ] Communication Compliance roles assigned
- [ ] All FSI policies created and enabled
- [ ] Detection classifiers configured
- [ ] OCR enabled for image processing
- [ ] Priority user groups configured
- [ ] Alert routing configured
- [ ] Review workflow documented
- [ ] Test alerts generated and processed
- [ ] Evidence artifacts collected

---

*Updated: January 2026 | Version: v1.1*
