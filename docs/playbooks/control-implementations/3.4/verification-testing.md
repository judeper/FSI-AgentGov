# Control 3.4: Incident Reporting and Root Cause Analysis - Verification & Testing

> This playbook provides verification and testing procedures for [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

---

## Verification Steps

### 1. Incident Reporting Flow

- Submit test incident through intake form
- Verify notifications trigger correctly
- Confirm assignment to investigator

### 2. SLA Monitoring

- Create test incidents at each severity level
- Verify SLA timers activate
- Confirm escalation triggers at breach

### 3. RCA Process

- Complete sample RCA document
- Verify approval workflow
- Confirm archive to permanent storage

### 4. Metrics Dashboard

- Review incident metrics
- Verify calculations are accurate
- Test drill-down to individual incidents

---

## Compliance Checklist

| Item | Required For | Status |
|------|--------------|--------|
| Incident tracking system operational | All regulations | |
| SLA monitoring configured | FFIEC, SOX 404 | |
| RCA template approved | Internal governance | |
| Escalation matrix documented | All regulations | |
| Regulatory notification thresholds defined | GLBA, State laws | |
| Incident records retained 6+ years | SEC 17a-4 | |
| Weekly incident review meetings | Best practice | |

---

## Test Cases

### Test Case 1: Critical Incident Escalation

**Objective:** Verify critical incidents escalate immediately

**Steps:**

1. Report incident with Severity = Critical
2. Verify CISO/CCO notification within 15 minutes
3. Confirm Teams notification to Security-Ops channel
4. Check Sentinel incident creation (if integrated)

**Expected Result:** All notifications sent within SLA

### Test Case 2: SLA Breach Alert

**Objective:** Verify overdue incidents trigger alerts

**Steps:**

1. Create High severity incident
2. Leave unresolved for >1 hour
3. Verify escalation email sent
4. Confirm status updated to "Escalated"

**Expected Result:** Automatic escalation at SLA breach

### Test Case 3: Incident Closure Validation

**Objective:** Verify closure requires RCA completion

**Steps:**

1. Attempt to close incident without Root Cause
2. Verify validation error
3. Complete Root Cause and Corrective Actions
4. Successfully close incident

**Expected Result:** Closure blocked until required fields complete

### Test Case 4: SEC Regulation S-P Notification

**Objective:** Verify 30-day customer notification workflow

**Steps:**

1. Report incident with customer data exposure
2. Mark Regulatory Impact = Yes
3. Verify incident queued for compliance review
4. Confirm notification countdown started

**Expected Result:** Workflow tracks 30-day notification deadline

---

## Evidence Collection

For regulatory examinations, collect:

- Incident log export (last 12 months)
- SLA compliance report
- Sample RCA documents
- Escalation matrix documentation
- Regulatory notification records

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
