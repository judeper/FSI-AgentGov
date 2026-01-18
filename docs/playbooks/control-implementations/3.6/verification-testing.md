# Control 3.6: Orphaned Agent Detection and Remediation - Verification & Testing

> This playbook provides verification and testing procedures for [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

---

## Verification Steps

### 1. Detection Accuracy

- Run orphan detection script
- Manually verify flagged agents are truly orphaned
- Confirm no false positives in results

### 2. Remediation Workflow

- Test reassignment process
- Verify archive functionality
- Confirm approval routing works

### 3. SLA Monitoring

- Create test orphan entry
- Verify SLA timers activate
- Confirm escalation at breach

---

## Compliance Checklist

| Item | Required For | Status |
|------|--------------|--------|
| Weekly orphan detection | Governance hygiene | |
| Remediation SLAs defined | Operational efficiency | |
| Approval workflow for deletion | Risk management | |
| Orphan report archiving | Audit evidence | |
| Owner succession planning | Business continuity | |

---

## Test Cases

### Test Case 1: Departed Owner Detection

**Objective:** Verify detection when owner leaves organization

**Steps:**

1. Identify agent owned by disabled user
2. Run orphan detection
3. Verify agent flagged with "Owner Departed"

**Expected Result:** Agent correctly identified as orphan

### Test Case 2: Reassignment Process

**Objective:** Verify ownership transfer works

**Steps:**

1. Select orphaned agent
2. Execute reassignment to new owner
3. Verify new owner has full access
4. Confirm metadata updated

**Expected Result:** Ownership successfully transferred

### Test Case 3: Archive and Delete

**Objective:** Verify secure agent removal

**Steps:**

1. Archive an orphaned agent
2. Verify agent is disabled
3. After retention period, execute deletion
4. Confirm complete removal

**Expected Result:** Agent properly archived then deleted

---

## Evidence Collection

For audits, collect:

- Weekly orphan detection reports
- Remediation action logs
- Approval records for deletions
- SLA compliance metrics

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
