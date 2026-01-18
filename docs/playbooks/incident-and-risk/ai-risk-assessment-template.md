# AI Risk Assessment Template

Structured risk assessment for AI agent deployment decisions.

---

## Overview

Use this template to assess risks before deploying new agents or promoting existing agents to higher governance zones. Risk assessment is required for Zone 2 and mandatory with formal documentation for Zone 3.

---

## Assessment Information

| Field | Value |
|-------|-------|
| **Agent Name** | |
| **Agent ID** | |
| **Proposed Zone** | Zone 1 / Zone 2 / Zone 3 |
| **Business Owner** | |
| **Assessment Date** | |
| **Assessor** | |

---

## Agent Description

### Purpose

*Describe what the agent does and the business problem it solves.*

### Users

*Who will use this agent? How many users?*

### Data Sources

*What data does the agent access? List all knowledge sources and connectors.*

### Outputs

*What outputs does the agent produce? How are they used?*

---

## Risk Assessment Categories

### 1. Data Risk

| Risk Factor | Rating | Justification |
|-------------|--------|---------------|
| **Data sensitivity** | Low / Medium / High | |
| **Data volume** | Low / Medium / High | |
| **External data exposure** | Yes / No | |
| **Customer PII accessed** | Yes / No | |
| **Financial data accessed** | Yes / No | |

**Overall Data Risk:** Low / Medium / High

**Mitigating Controls:**

- [ ] DLP policies applied (Control 1.5)
- [ ] Sensitivity labels enforced
- [ ] Data minimization implemented (Control 1.14)
- [ ] Other: ______________

---

### 2. Regulatory Risk

| Risk Factor | Applies? | Justification |
|-------------|----------|---------------|
| **FINRA supervision required** | Yes / No | |
| **SEC records requirements** | Yes / No | |
| **GLBA customer data** | Yes / No | |
| **SOX financial data** | Yes / No | |
| **OCC model risk guidance** | Yes / No | |
| **Fair lending implications** | Yes / No | |

**Overall Regulatory Risk:** Low / Medium / High

**Mitigating Controls:**

- [ ] Supervisory procedures documented (Control 2.12)
- [ ] Audit logging configured (Control 1.7)
- [ ] Model risk assessment completed (Control 2.6)
- [ ] Bias testing completed (Control 2.11)
- [ ] Other: ______________

---

### 3. Operational Risk

| Risk Factor | Rating | Justification |
|-------------|--------|---------------|
| **Business impact if unavailable** | Low / Medium / High | |
| **Dependency on agent for critical processes** | Low / Medium / High | |
| **Complexity of agent logic** | Low / Medium / High | |
| **Integration points** | Low / Medium / High | |

**Overall Operational Risk:** Low / Medium / High

**Mitigating Controls:**

- [ ] Business continuity plan (Control 2.4)
- [ ] Change management process (Control 2.3)
- [ ] Testing procedures (Control 2.5)
- [ ] Monitoring configured (Control 3.2)
- [ ] Other: ______________

---

### 4. Security Risk

| Risk Factor | Rating | Justification |
|-------------|--------|---------------|
| **Attack surface** | Low / Medium / High | |
| **Privilege level required** | Low / Medium / High | |
| **External exposure** | None / Internal / External | |
| **Data exfiltration potential** | Low / Medium / High | |

**Overall Security Risk:** Low / Medium / High

**Mitigating Controls:**

- [ ] Managed Environment enabled (Control 2.1)
- [ ] Conditional Access applied (Control 1.11)
- [ ] Runtime protection enabled (Control 1.8)
- [ ] Network isolation configured (Control 1.20)
- [ ] Other: ______________

---

### 5. Reputational Risk

| Risk Factor | Rating | Justification |
|-------------|--------|---------------|
| **Customer-facing** | Yes / No | |
| **Brand impact if fails** | Low / Medium / High | |
| **Public visibility** | Low / Medium / High | |
| **Hallucination risk** | Low / Medium / High | |

**Overall Reputational Risk:** Low / Medium / High

**Mitigating Controls:**

- [ ] Human-in-the-loop for high-risk decisions
- [ ] Hallucination monitoring (Control 3.10)
- [ ] AI disclosure implemented (Control 2.19)
- [ ] Escalation procedures documented
- [ ] Other: ______________

---

## Overall Risk Summary

| Category | Rating | Weight | Weighted Score |
|----------|--------|--------|----------------|
| Data Risk | Low=1 / Medium=2 / High=3 | 25% | |
| Regulatory Risk | Low=1 / Medium=2 / High=3 | 25% | |
| Operational Risk | Low=1 / Medium=2 / High=3 | 20% | |
| Security Risk | Low=1 / Medium=2 / High=3 | 20% | |
| Reputational Risk | Low=1 / Medium=2 / High=3 | 10% | |
| **Total** | | 100% | |

**Risk Classification:**

- **1.0-1.5:** Low Risk — Zone 1 appropriate
- **1.6-2.2:** Medium Risk — Zone 2 appropriate
- **2.3-3.0:** High Risk — Zone 3 required

**Calculated Risk Level:** ____________

**Recommended Zone:** ____________

---

## Residual Risk Assessment

After applying mitigating controls, assess residual risk:

| Category | Initial Risk | Mitigating Controls | Residual Risk |
|----------|--------------|---------------------|---------------|
| Data | | | |
| Regulatory | | | |
| Operational | | | |
| Security | | | |
| Reputational | | | |

**Residual Risk Acceptable:** Yes / No

**If No, additional controls required:**

---

## Approval

### Zone 2 Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Manager | | | |
| AI Governance Lead | | | |

### Zone 3 Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Owner | | | |
| AI Governance Lead | | | |
| Compliance Officer | | | |
| CISO | | | |
| General Counsel (if customer-facing) | | | |

---

## Review Schedule

| Review Type | Frequency | Next Review Date |
|-------------|-----------|------------------|
| Risk reassessment | Annual | |
| Control effectiveness | Quarterly | |
| Bias testing | Quarterly | |

---

## Attachments

- [ ] Business case documentation
- [ ] Data flow diagram
- [ ] Test results
- [ ] Security assessment
- [ ] Bias testing results (Zone 3)

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.1*
