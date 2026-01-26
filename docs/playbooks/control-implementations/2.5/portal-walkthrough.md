# Control 2.5: Testing, Validation, and Quality Assurance - Portal Walkthrough

> This playbook provides portal-based configuration guidance for [Control 2.5](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md).

---

## Overview

This walkthrough guides you through establishing testing environments, configuring Copilot Studio testing capabilities, and implementing evaluation gates.

---

## Part 1: Create Test Environment

**Portal Path:** Power Platform Admin Center > Environments > + New

### Steps

1. Navigate to **Power Platform Admin Center**
2. Click **Environments** > **+ New**
3. **Create Test Environment:**
   - **Name:** "[Project]-Test" or "[Project]-QA"
   - **Type:** Sandbox
   - **Region:** Same as production
   - **Purpose:** Dedicated testing
4. **Configure Environment:**
   - Enable Managed Environment
   - Apply production DLP policies
   - Import production solution for testing
5. **Prepare Test Data:**
   - Create anonymized test dataset
   - Include edge cases and boundary conditions
   - Document test data catalog

---

## Part 2: Configure Copilot Studio Testing

**Portal Path:** Copilot Studio > [Agent] > Test

### Steps

1. Open **Copilot Studio** (copilotstudio.microsoft.com)
2. Select the agent to test
3. Click **Test your agent** (Test panel)
4. **Create Test Suites:**
   - Happy path tests (normal usage)
   - Edge case tests (boundary conditions)
   - Error handling tests (invalid inputs)
   - Security tests (unauthorized access attempts)
   - Performance tests (response time)

### Test Case Template

```
Test Case ID: TC-[AgentID]-[Number]
Test Name: [Descriptive name]
Priority: [Critical | High | Medium | Low]

Preconditions:
- [Required state before test]

Test Steps:
1. [User action]
2. [Expected agent response]
3. [Verification step]

Expected Result:
- [Detailed expected outcome]

Actual Result: [To be filled during testing]
Status: [Pass | Fail | Blocked]
Tester: [Name]
Date: [Date]
```

---

## Part 3: Configure Agent Evaluation

**Portal Path:** Copilot Studio > [Agent] > Analytics > Evaluation

Copilot Studio provides built-in evaluation capabilities:

| Metric | Description | FSI Application |
|--------|-------------|-----------------|
| **Groundedness** | Response is based on provided knowledge sources | Ensures regulatory accuracy |
| **Relevance** | Response addresses the user's question | Customer satisfaction |
| **Coherence** | Response is well-structured and logical | Professional communication |
| **Fluency** | Response is grammatically correct | Brand standards |
| **Similarity** | Response matches expected answer | Golden dataset validation |

### Configuration by Zone

| Setting | Zone 1 | Zone 2 | Zone 3 |
|---------|--------|--------|--------|
| **Groundedness tracking** | Optional | Enabled | Mandatory |
| **Golden dataset testing** | Not required | Recommended | Mandatory |
| **Evaluation frequency** | Monthly | Weekly | Daily |
| **Baseline thresholds** | Informal | Documented | Documented + approved |
| **Regression alerting** | No | Yes | Yes + escalation |

---

## Part 4: Agent Evaluation Gates

### Evaluation Gate Framework

| Gate | Lifecycle Stage | Required Validations | Zone Applicability |
|------|-----------------|---------------------|-------------------|
| **Gate 1: Design Review** | Design > Build | Business justification, risk classification | All zones |
| **Gate 2: Security Clearance** | Build > Evaluate | Prompt injection testing, authentication validation | Zone 2, Zone 3 |
| **Gate 3: Functional Approval** | Evaluate > Deploy | Test suite pass rate >95%, UAT sign-off | Zone 2, Zone 3 |
| **Gate 4: Production Readiness** | Deploy > Monitor | Compliance approval, rollback plan documented | Zone 3 mandatory |

### Gate 2: Security Clearance Checklist

| Validation | Pass Criteria | Evidence Required |
|------------|---------------|-------------------|
| **Prompt Injection Testing** | No successful injection in 20+ test cases | Test results log |
| **Jailbreak Resistance** | Agent refuses all bypass attempts | Test case documentation |
| **Authentication Verification** | Unauthorized access blocked 100% | Access test results |
| **Data Boundary Validation** | No cross-tenant or cross-account leakage | DLP test report |
| **Tool/Action Authorization** | Only approved connectors accessible | Connector audit |

### Gate 3: Functional Approval Requirements

1. **Test Pass Rate:** Minimum 95% of test cases passed
2. **Critical Defects:** Zero unresolved P1/Critical issues
3. **Performance Baseline:** Response time within tier thresholds
4. **UAT Completion:** Business owner sign-off obtained
5. **KPI Baseline Documentation:** Define success metrics

### Gate 4: Production Readiness (Zone 3)

| Requirement | Description | Owner |
|-------------|-------------|-------|
| **Compliance Approval** | Written approval from Compliance Officer | Compliance |
| **Rollback Plan** | Documented procedure to revert | Platform Team |
| **Monitoring Configuration** | Alerts and dashboards configured | Operations |
| **Incident Response** | Escalation procedures documented | Security/Operations |
| **Change Record** | Change ticket approved and logged | Change Management |

---

## Part 5: UAT Process

### Pre-UAT Preparation

1. Deploy agent to UAT environment
2. Prepare UAT test scenarios
3. Brief business testers
4. Provide UAT sign-off template

### UAT Sign-Off Form

```
UAT Sign-Off Document

Agent: [Agent Name]
Version: [Version Number]
UAT Period: [Start Date] to [End Date]

Test Results:
- Total scenarios tested: [Number]
- Passed: [Number]
- Failed: [Number]
- Deferred: [Number]

Known Issues:
[List any accepted defects]

Business Approval:
[ ] The agent meets business requirements
[ ] The agent is approved for production deployment

Signed: _________________ Date: _________
Business Owner

Signed: _________________ Date: _________
Compliance Representative (enterprise-managed only)
```

---

## Part 6: Security Testing Checklist

### Authentication Testing

- [ ] Test access without authentication (should fail)
- [ ] Test with valid credentials (should succeed)
- [ ] Test with expired tokens (should fail gracefully)
- [ ] Test session timeout behavior

### Authorization Testing

- [ ] Test access to restricted data (should be denied)
- [ ] Test role-based access (correct permissions)
- [ ] Test cross-tenant access (should be blocked)

### Prompt Injection Testing

- [ ] Test with injection attempts
- [ ] Verify agent doesn't execute unauthorized commands
- [ ] Test jailbreak prevention

### Data Leakage Testing

- [ ] Test for PII exposure
- [ ] Verify sensitivity labels enforced
- [ ] Test DLP policy enforcement

---

## Part 7: Performance Testing Baselines

| Metric | Zone 1 | Zone 2 | Zone 3 |
|--------|--------|--------|--------|
| Response Time (p50) | <3s | <2s | <1s |
| Response Time (p95) | <10s | <5s | <3s |
| Concurrent Users | 10 | 100 | 1000 |
| Availability | 95% | 99% | 99.9% |

---

## Part 8: Test Evidence Retention

| Evidence Type | Zone 1 | Zone 2 | Zone 3 |
|---------------|--------|--------|--------|
| Test Plans | 1 year | 3 years | 7 years |
| Test Results | 1 year | 3 years | 7 years |
| UAT Sign-off | 1 year | 3 years | 7 years |
| Security Test Reports | 1 year | 3 years | 7 years |
| Bias Test Results | N/A | 3 years | 7 years |

**Evidence Storage:**
- SharePoint document library with retention policy
- Azure DevOps test artifacts
- Automated backup to compliance archive

---

## Related Playbooks

- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.2*
