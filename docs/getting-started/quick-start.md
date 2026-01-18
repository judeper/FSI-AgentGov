# Quick Start Guide

Get up and running with the FSI Agent Governance Framework in 30 minutes.

---

## Getting Started: 3-Phase Approach

The framework recommends a structured 3-phase adoption approach:

### Phase I: Form a Governance Team (Week 1-2)

| Activity | Owner | Output |
|----------|-------|--------|
| Identify stakeholders | Executive Sponsor | Stakeholder list |
| Assign roles per RACI | AI Governance Lead | Role assignments |
| Establish communication channels | Project Lead | Teams channel/meetings |
| Create initial policies | Compliance Officer | Draft governance policy |

### Phase II: Train Employees (Week 2-4)

| Training | Audience | Duration |
|----------|----------|----------|
| Zone overview and classification | All makers | 1 hour |
| PPAC administration | Platform admins | 2 hours |
| Compliance monitoring | Compliance team | 2 hours |
| Security controls | Security team | 2 hours |

### Phase III: Deploy and Engage (Week 4+)

| Activity | Priority | Control Reference |
|----------|----------|-------------------|
| Enable environment routing | Critical | [2.15](../controls/pillar-2-management/2.15-environment-routing.md) |
| Configure environment groups | Critical | [2.2](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) |
| Deploy security controls | High | Pillar 1 controls |
| Set up monitoring | High | [3.7](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md), [3.8](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) |
| Iterate based on feedback | Ongoing | All controls |

---

## 🚀 For New Users (10 minutes)

### Step 1: Understand the Framework Structure (3 min)

The framework has **4 pillars** and **3 zones**:

**4 Pillars (types of governance):**

1. Security (19 controls) - Protect data
2. Management (15 controls) - Govern lifecycle
3. Reporting (9 controls) - Monitor activities
4. SharePoint (5 controls) - Govern SharePoint

**3 Zones (risk levels):**

1. Zone 1 - Personal development (low risk)
2. Zone 2 - Team collaboration (medium risk)
3. Zone 3 - Enterprise production (high risk)

### Step 2: Classify Your Agents (5 min)

Ask these questions:

**Q: Who uses this agent?**
- Just me? → Zone 1
- My team/department? → Zone 2
- Organization-wide or customers? → Zone 3

**Q: What data does it access?**
- Only my personal data? → Zone 1
- Departmental data? → Zone 2
- Regulated/customer data? → Zone 3

**Result:** You've classified your agent to a zone.

### Step 3: Find Applicable Regulations (2 min)

Check which regulations apply to your organization:

- ✅ FINRA? (broker-dealers)
- ✅ SEC? (investment advisers, public companies)
- ✅ SOX? (public companies)
- ✅ GLBA? (all financial institutions)
- ✅ OCC? (national banks)
- ✅ Federal Reserve? (bank holding companies, state member banks)
- ✅ FDIC? (state non-member banks, savings associations)
- ✅ NCUA? (credit unions)
- ✅ State insurance regulator? (insurers)
- ✅ NYDFS Part 500? (NY-licensed institutions)

Result: You've identified your primary US regulators. Consult your Compliance Officer to confirm.

---

## 📋 For Implementation (20 minutes)

### Quick Implementation Checklist

**Week 1: Assessment**
- [ ] Classify all existing agents to zones
- [ ] Create agent inventory
- [ ] Identify primary regulations
- [ ] Assign governance roles

**Week 2: Security Baseline**
- [ ] Enable MFA for all agent creators
- [ ] Implement basic DLP policy
- [ ] Configure audit logging (1-year)
- [ ] Document security procedures

**Week 3: Governance**
- [ ] Establish approval workflow for Zone 2+
- [ ] Create agent registry
- [ ] Document change control process
- [ ] Assign Compliance Officer oversight

**Week 4: Monitoring**
- [ ] Set up compliance dashboard
- [ ] Configure incident alerts
- [ ] Schedule quarterly reviews
- [ ] Document governance procedures

**Week 5+: Continuous**
- [ ] Monthly compliance reviews
- [ ] Quarterly control assessments
- [ ] Annual regulatory updates
- [ ] Continuous improvement

---

## 🎯 Common Scenarios

### Scenario 1: Single Zone 1 Agent (Personal)

**Time Required:** 1 day

**Steps:**

1. Create agent in personal environment
2. Document agent purpose
3. Keep basic audit logs (30 days)
4. No approval needed

**Controls Required:**

- Basic documentation
- Minimal governance

**Compliance:** None (Zone 1 not examined)

---

### Scenario 2: Zone 2 Team Agent (Department)

**Time Required:** 1 week

**Steps:**

1. Get manager approval
2. Classify agent to Zone 2
3. Identify data sources
4. Configure DLP and audit
5. Document approval
6. Train team members

**Controls Required (minimum):**

- 1.2 Agent Registry
- 1.5 DLP and Labels
- 1.7 Audit Logging (1 year)
- 1.11 Conditional Access
- 2.3 Change Management
- 2.12 Supervision

**Compliance:** FINRA 3110 supervision

---

### Scenario 3: Zone 3 Production Agent (Customer-Facing)

**Time Required:** 3-6 weeks

**Steps:**

1. Establish governance committee
2. Risk assessment and business case
3. Security testing
4. Bias testing (if applicable)
5. Model risk assessment
6. Legal and compliance review
7. Change control process
8. Incident response procedures
9. Governance committee approval
10. Production deployment

**Controls Required (comprehensive):**

- All 48 controls apply
- Enhanced versions per regulation

**Compliance:** 

- FINRA comprehensive
- SEC Rule 17a-3/4
- SOX 302/404
- GLBA 501(b)
- OCC/SR 11-7 (if applicable)

---

## 📚 Where to Find Things

| Question | Answer |
|----------|--------|
| "How do I get started?" | You're reading it! |
| "What are the zones?" | [Zones Guide](../framework/zones-and-tiers.md) |
| "Which regulations apply?" | [Regulatory Framework](../framework/regulatory-framework.md) |
| "What's the full framework?" | [Overview](../index.md) |
| "Who does what?" | [Operating Model](../framework/operating-model.md) |
| "How do I implement?" | [Implementation Checklist](checklist.md) |
| "What does this term mean?" | [Glossary](../reference/glossary.md) |
| "Common questions?" | [FAQ](../reference/faq.md) |
| "Tell me about control 1.5" | [1.5 Data Loss Prevention](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) |
| "I need a policy" | Check control files for policy guidance |

---

## 🔑 Key Terms (Quick Version)

- **Zone:** Risk level (1=low, 2=medium, 3=high)
- **Control:** Governance requirement (48 total)
- **Pillar:** Control category (Security, Management, Reporting, SharePoint)
- **DLP:** Data Loss Prevention (prevent unauthorized data sharing)
- **MFA:** Multi-Factor Authentication (login security)
- **Audit:** Activity logging and monitoring
- **Model Risk:** Risk of AI/algorithm failures
- **Bias Testing:** Check for unfair treatment across demographics

---

## ✅ Next Steps

1. **Read [Zones Guide](../framework/zones-and-tiers.md)** (understand zones)
2. **Review [Regulatory Framework](../framework/regulatory-framework.md)** (find your regulations)
3. **Check [Implementation Checklist](checklist.md)** (get step-by-step tasks)
4. **Reference individual controls** (implement details)
5. **Document evidence** (compliance proof)

---

## 💬 Still Questions?

- Check **[FAQ](../reference/faq.md)** for common questions
- Review **[Glossary](../reference/glossary.md)** for terms
- Contact your **Compliance Officer** for regulatory questions
- Ask your **Power Platform Admin** for technical setup

---

*FSI Agent Governance Framework v1.0 - January 2026*
