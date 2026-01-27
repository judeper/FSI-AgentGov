# Blueprint Promotion Gate Definitions

> Part of [Agent Blueprint Promotion Gates](index.md)

---

## Gate 1: Design → Build

**Purpose:** Validate business justification and technical feasibility before development begins.

### Approval Requirements

| Zone | Approvers | SLA |
|------|-----------|-----|
| Zone 2 | Technical Lead | 2 business days |
| Zone 3 | Technical Lead + Architecture Review Board | 5 business days |

### Criteria Checklist

| Criterion | Zone 2 | Zone 3 | Validation Method |
|-----------|--------|--------|-------------------|
| Business justification documented | ✓ | ✓ | Document review |
| Use case aligned with governance zone | ✓ | ✓ | Zone classification matrix |
| Data sources identified and classified | ✓ | ✓ | Data source inventory |
| Data sensitivity assessment complete | - | ✓ | Sensitivity label review |
| Connectors within approved catalog | ✓ | ✓ | DLP policy check |
| Customer-facing determination | ✓ | ✓ | Business owner attestation |
| Human sponsor assigned | ✓ | ✓ | Entra Agent ID check |
| Regulatory impact assessed | - | ✓ | Impact assessment template |

### Evidence Artifacts

| Artifact | Template | Storage Location |
|----------|----------|------------------|
| Requirements Document | `REQ-{AgentId}-v{Version}.docx` | SharePoint: `/AgentGovernance/Design/` |
| Data Source Declaration | `DSD-{AgentId}.xlsx` | SharePoint: `/AgentGovernance/Design/` |
| Zone Classification Form | `ZCF-{AgentId}.pdf` | SharePoint: `/AgentGovernance/Design/` |
| Sponsor Assignment Record | Entra ID audit log | Automatic |

### Gate 1 Approval Template

```json
{
  "gateId": "G1-{BlueprintId}",
  "gateName": "Design Review",
  "agentId": "{AgentId}",
  "agentName": "{AgentName}",
  "zone": "Zone2|Zone3",
  "submittedBy": "{DeveloperUPN}",
  "submittedDate": "{ISO8601}",
  "criteria": {
    "businessJustification": { "met": true, "evidenceUrl": "{url}" },
    "dataSourcesClassified": { "met": true, "evidenceUrl": "{url}" },
    "connectorsApproved": { "met": true, "evidenceUrl": "{url}" },
    "sponsorAssigned": { "met": true, "sponsorId": "{guid}" }
  },
  "approvals": [
    {
      "approverRole": "TechnicalLead",
      "approverUPN": "{email}",
      "decision": "Approved|Rejected|ConditionalApproval",
      "decisionDate": "{ISO8601}",
      "comments": "{text}",
      "conditions": []
    }
  ],
  "result": "Passed|Failed|Conditional"
}
```

---

## Gate 2: Build → Test

**Purpose:** Confirm development is complete and agent is ready for quality assurance.

### Approval Requirements

| Zone | Approvers | SLA |
|------|-----------|-----|
| Zone 2 | QA Lead | 2 business days |
| Zone 3 | QA Lead + Security scan (automated) | 3 business days |

### Criteria Checklist

| Criterion | Zone 2 | Zone 3 | Validation Method |
|-----------|--------|--------|-------------------|
| All topics implemented | ✓ | ✓ | Topic inventory check |
| Connectors configured and tested | ✓ | ✓ | Connector test results |
| Fallback topics defined | ✓ | ✓ | Topic review |
| Error handling implemented | ✓ | ✓ | Error scenario review |
| Security scan passed | - | ✓ | Automated scan report |
| Test plan documented | ✓ | ✓ | Test plan review |
| Test environment provisioned | ✓ | ✓ | Environment validation |
| DLP policy compliance verified | ✓ | ✓ | Policy check script |

### Automated Security Scan Requirements (Zone 3)

| Check | Tool | Pass Criteria |
|-------|------|---------------|
| Credential exposure | Defender for Cloud Apps | No hardcoded secrets |
| Prompt injection vectors | Custom scanning tool | No vulnerable patterns |
| Data exfiltration paths | DLP policy test | All paths blocked |
| Connector permissions | Graph API audit | Least privilege verified |

### Evidence Artifacts

| Artifact | Template | Storage Location |
|----------|----------|------------------|
| Technical Design Document | `TDD-{AgentId}-v{Version}.docx` | SharePoint: `/AgentGovernance/Build/` |
| Test Plan | `TP-{AgentId}-v{Version}.xlsx` | SharePoint: `/AgentGovernance/Test/` |
| Security Scan Report | `SSR-{AgentId}-{Date}.pdf` | SharePoint: `/AgentGovernance/Security/` |
| DLP Compliance Report | `DLP-{AgentId}-{Date}.pdf` | SharePoint: `/AgentGovernance/Compliance/` |

### Gate 2 Approval Template

```json
{
  "gateId": "G2-{BlueprintId}",
  "gateName": "Build Complete",
  "agentId": "{AgentId}",
  "automatedChecks": {
    "securityScan": {
      "passed": true,
      "scanDate": "{ISO8601}",
      "reportUrl": "{url}",
      "findings": {
        "critical": 0,
        "high": 0,
        "medium": 2,
        "low": 5
      }
    },
    "dlpCompliance": {
      "passed": true,
      "policiesEvaluated": ["FSI-Baseline", "FSI-Financial-Data"],
      "violations": 0
    }
  },
  "approvals": [
    {
      "approverRole": "QALead",
      "approverUPN": "{email}",
      "decision": "Approved",
      "decisionDate": "{ISO8601}",
      "comments": "Test plan reviewed and approved"
    }
  ],
  "result": "Passed"
}
```

---

## Gate 3: Test → Stage

**Purpose:** Validate testing is complete and agent meets quality standards.

### Approval Requirements

| Zone | Approvers | SLA |
|------|-----------|-----|
| Zone 2 | Manager + QA sign-off | 3 business days |
| Zone 3 | Manager + QA sign-off + Compliance review | 5 business days |

### Criteria Checklist

| Criterion | Zone 2 | Zone 3 | Validation Method |
|-----------|--------|--------|-------------------|
| All test cases executed | ✓ | ✓ | Test execution report |
| Pass rate ≥ 95% | ✓ | ✓ | Test metrics |
| No critical/high defects open | ✓ | ✓ | Defect tracking system |
| Performance baseline met | - | ✓ | Performance test results |
| Bias testing completed | - | ✓ | Bias test report |
| Compliance review approved | - | ✓ | Compliance attestation |
| UAT plan documented | ✓ | ✓ | UAT plan review |

### Test Coverage Requirements

| Test Type | Zone 2 Minimum | Zone 3 Minimum |
|-----------|----------------|----------------|
| Functional tests | 80% topic coverage | 95% topic coverage |
| Integration tests | All connectors | All connectors + edge cases |
| Security tests | Basic scan | Full penetration test |
| Performance tests | Optional | Required (baseline) |
| Bias tests | Optional | Required (per Control 2.11) |
| Regression tests | Optional | Required |

### Evidence Artifacts

| Artifact | Template | Storage Location |
|----------|----------|------------------|
| Test Execution Report | `TER-{AgentId}-{Date}.xlsx` | SharePoint: `/AgentGovernance/Test/` |
| Defect Summary | `DEF-{AgentId}-{Date}.xlsx` | SharePoint: `/AgentGovernance/Test/` |
| Performance Test Results | `PTR-{AgentId}-{Date}.pdf` | SharePoint: `/AgentGovernance/Test/` |
| Bias Test Report | `BTR-{AgentId}-{Date}.pdf` | SharePoint: `/AgentGovernance/Compliance/` |
| Compliance Review Attestation | `CRA-{AgentId}-{Date}.pdf` | SharePoint: `/AgentGovernance/Compliance/` |

### Gate 3 Approval Template

```json
{
  "gateId": "G3-{BlueprintId}",
  "gateName": "Test Complete",
  "agentId": "{AgentId}",
  "testMetrics": {
    "totalTestCases": 150,
    "passed": 147,
    "failed": 2,
    "blocked": 1,
    "passRate": 98.0,
    "criticalDefects": 0,
    "highDefects": 0,
    "mediumDefects": 2
  },
  "performanceBaseline": {
    "avgResponseTime": 1.2,
    "p95ResponseTime": 2.8,
    "threshold": 3.0,
    "passed": true
  },
  "biasTestResults": {
    "tested": true,
    "protectedClasses": ["age", "gender", "race", "disability"],
    "disparateImpact": false,
    "reportUrl": "{url}"
  },
  "approvals": [
    {
      "approverRole": "QALead",
      "decision": "Approved",
      "decisionDate": "{ISO8601}"
    },
    {
      "approverRole": "Manager",
      "decision": "Approved",
      "decisionDate": "{ISO8601}"
    },
    {
      "approverRole": "ComplianceOfficer",
      "decision": "Approved",
      "decisionDate": "{ISO8601}",
      "attestationUrl": "{url}"
    }
  ],
  "result": "Passed"
}
```

---

## Gate 4: Stage → Production

**Purpose:** Final approval before production deployment with all governance requirements met.

### Approval Requirements

| Zone | Approvers | SLA |
|------|-----------|-----|
| Zone 2 | Business Owner + Manager | 3 business days |
| Zone 3 | Business Owner + CAB + Compliance + Legal (if customer-facing) | 5-10 business days |

### Criteria Checklist

| Criterion | Zone 2 | Zone 3 | Validation Method |
|-----------|--------|--------|-------------------|
| UAT completed and signed off | ✓ | ✓ | UAT sign-off form |
| Production configuration documented | ✓ | ✓ | Production config doc |
| Rollback plan tested | ✓ | ✓ | Rollback test results |
| Monitoring configured | ✓ | ✓ | Monitoring dashboard |
| Support procedures documented | ✓ | ✓ | Support runbook |
| CAB approval obtained | - | ✓ | CAB meeting minutes |
| Legal review complete (if customer-facing) | - | ✓ | Legal sign-off |
| Regulatory notification filed (if required) | - | ✓ | Filing confirmation |
| Agent inventory updated | ✓ | ✓ | Registry check |

### Rollback Verification Requirements

| Check | Description | Pass Criteria |
|-------|-------------|---------------|
| Previous version availability | Confirm prior solution version exists | Version in solution history |
| Rollback procedure documented | Step-by-step rollback instructions | Runbook exists |
| Rollback test executed | Successfully restored previous version | Test log shows success |
| Data integrity verified | No data loss during rollback | Verification checksum |
| Communication plan | Stakeholder notification ready | Template approved |

### Evidence Artifacts

| Artifact | Template | Storage Location |
|----------|----------|------------------|
| UAT Sign-off Form | `UAT-{AgentId}-{Date}.pdf` | SharePoint: `/AgentGovernance/UAT/` |
| Production Configuration | `PROD-{AgentId}-{Version}.json` | SharePoint: `/AgentGovernance/Production/` |
| Rollback Plan | `RBP-{AgentId}-{Version}.docx` | SharePoint: `/AgentGovernance/Production/` |
| Rollback Test Results | `RBT-{AgentId}-{Date}.pdf` | SharePoint: `/AgentGovernance/Production/` |
| CAB Meeting Minutes | `CAB-{Date}.pdf` | SharePoint: `/ChangeManagement/CAB/` |
| Legal Review (if applicable) | `LR-{AgentId}-{Date}.pdf` | SharePoint: `/AgentGovernance/Legal/` |
| Support Runbook | `SRB-{AgentId}.docx` | SharePoint: `/AgentGovernance/Support/` |

### Gate 4 Approval Template

```json
{
  "gateId": "G4-{BlueprintId}",
  "gateName": "Production Deployment",
  "agentId": "{AgentId}",
  "deploymentDetails": {
    "targetEnvironment": "PROD-{EnvironmentId}",
    "deploymentWindow": "{ISO8601}",
    "rollbackDeadline": "{ISO8601}",
    "previousVersion": "{Version}",
    "newVersion": "{Version}"
  },
  "rollbackVerification": {
    "planDocumented": true,
    "testExecuted": true,
    "testDate": "{ISO8601}",
    "testResult": "Success",
    "restorationTime": "15 minutes"
  },
  "approvals": [
    {
      "approverRole": "BusinessOwner",
      "decision": "Approved",
      "decisionDate": "{ISO8601}"
    },
    {
      "approverRole": "CAB",
      "decision": "Approved",
      "decisionDate": "{ISO8601}",
      "meetingRef": "CAB-2026-0127"
    },
    {
      "approverRole": "ComplianceOfficer",
      "decision": "Approved",
      "decisionDate": "{ISO8601}",
      "attestationUrl": "{url}"
    },
    {
      "approverRole": "Legal",
      "decision": "Approved",
      "decisionDate": "{ISO8601}",
      "reviewUrl": "{url}",
      "conditions": ["Customer disclosure updated"]
    }
  ],
  "result": "Passed",
  "deploymentAuthorized": true
}
```

---

## Gate Failure Handling

### Rejection Workflow

When a gate fails:

1. **Document rejection reason** in gate record
2. **Notify submitter** with specific remediation requirements
3. **Create remediation task** in tracking system
4. **Reset to previous phase** if partial progress
5. **Re-submit** when remediation complete

### Conditional Approval

Gates may be conditionally approved with documented conditions:

| Condition Type | Example | Tracking |
|----------------|---------|----------|
| Time-bound | "Complete bias testing within 7 days" | Task with deadline |
| Risk-accepted | "Medium vulnerability accepted with compensating control" | Risk register entry |
| Documentation | "Update support runbook before go-live" | Document checklist |

### Escalation Path

| Level | Trigger | Escalate To | SLA |
|-------|---------|-------------|-----|
| 1 | Rejection disputed | Next-level approver | 2 days |
| 2 | SLA exceeded (2x) | AI Governance Lead | 1 day |
| 3 | Critical business need | CIO/CISO | Same day |

---

## Audit Trail Requirements

Each gate must capture:

| Field | Description | Retention |
|-------|-------------|-----------|
| Gate ID | Unique identifier | Permanent |
| Timestamps | Submit, each approval, completion | Permanent |
| Approver identity | UPN of each approver | Permanent |
| Decision | Approved/Rejected/Conditional | Permanent |
| Comments | Approver rationale | Permanent |
| Evidence URLs | Links to all artifacts | Permanent |
| Conditions | Any conditional requirements | Permanent |
| Remediation | Actions taken for failures | Permanent |

---

## Related Resources

- [Overview](index.md) - Gate model summary
- [Implementation Guide](implementation-guide.md) - Setup procedures
- [Control 2.3 - Change Management](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)
- [Control 2.5 - Testing and Validation](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md)

---

*FSI Agent Governance Framework v1.2.6 - January 2026*
