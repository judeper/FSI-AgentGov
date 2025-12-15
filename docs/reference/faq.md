# Frequently Asked Questions (FAQ)

Common questions and answers about the FSI Agent Governance Framework.

---

## Getting Started

### Q: Where do I start?

A: Read in this order:
1. README.md (5 min overview)
2. Zones-Overview.md (understand your zone)
3. Quick-Start-Guide.md (30 min hands-on)
4. Regulatory-Mappings.md (if regulated)

### Q: What if I don't know which zone my agent should be in?

A: Use the Zone Decision Matrix in Zones-Overview.md:
- Zone 1: Personal only, M365 data only
- Zone 2: Team/dept, internal data only
- Zone 3: Org-wide, customer data, regulated data

Ask your manager or compliance officer if unsure.

### Q: How long does implementation take?

A: Depends on current state:
- **Zone 1:** 1-2 days (minimal)
- **Zone 2:** 1-2 weeks (moderate)
- **Zone 3:** 3-6 weeks (comprehensive)

Full framework: 8-week phased approach (see Implementation-Checklist.md)

---

## Framework Questions

### Q: Why are there 43 controls?

A: The framework covers:
- **Pillar 1:** 18 security controls
- **Pillar 2:** 14 management/lifecycle controls
- **Pillar 3:** 6 reporting/monitoring controls
- **Pillar 4:** 5 SharePoint-specific controls

Total = 43 controls covering all governance areas.

### Q: Do I need to implement all 43 controls?

A: No. Implement based on:
1. **Your zone:** Zone 1 needs fewer, Zone 3 needs all
2. **Your regulations:** Implement applicable controls
3. **Your risk tolerance:** Higher risk = more controls

Start with baseline for your zone, add recommended/regulated as you mature.

### Q: What's a "governance level"?

A: Each control has 3 levels:
- **Baseline (Level 1):** Minimum implementation
- **Recommended (Level 2-3):** Best practices
- **Regulated/High-Risk (Level 4):** Comprehensive

Implement baseline for Zone 1, baseline+recommended for Zone 2, all levels for Zone 3.

### Q: Can I modify the framework?

A: Yes! The framework is a starting point. You can:
- Add controls specific to your organization
- Combine controls if makes sense
- Adjust governance levels based on risk
- Customize for your regulations

Maintain version control and document changes.

---

## Zones & Classification

### Q: Can an agent be in multiple zones?

A: No. Each agent is in one zone. It may progress through zones:
- Zone 1 (personal) → Zone 2 (team) → Zone 3 (production)

### Q: What if an agent starts in Zone 1 but needs Zone 2 features?

A: Promote it through formal process:
1. Request promotion to next zone
2. Get appropriate approvals
3. Implement required controls for new zone
4. Move to new environment
5. Document promotion

### Q: Can I move an agent from Zone 3 to Zone 2?

A: Yes, through demotion if:
- Agent is no longer production-critical
- Compliance requirements reduced
- Risk profile decreased

Requires governance committee approval and documentation.

### Q: What defines "customer-facing"?

A: If the agent is used by:
- Customers
- Clients
- External parties
- Regulatory subjects

→ Must be Zone 3

---

## Governance & Approvals

### Q: Who approves each zone?

A: 
- **Zone 1:** Self-service (no approval)
- **Zone 2:** Manager/Department Head
- **Zone 3:** Governance Committee (Compliance Officer, CISO, General Counsel, CRO)

### Q: How long does approval take?

A:
- **Zone 1:** Immediate (self)
- **Zone 2:** 3-5 business days (manager review)
- **Zone 3:** 10-14 business days (governance committee)

### Q: What if my approval is denied?

A: Get feedback and revise:
1. Address concerns raised
2. Provide additional information
3. Re-submit
4. Escalate if needed per RACI-Matrix.md

### Q: Who is the Governance Committee?

A: Typically:
- AI Governance Lead (Chair)
- Compliance Officer
- CISO
- General Counsel
- Chief Risk Officer (if applicable)
- Business owner (agent requester)

See RACI-Matrix.md for detailed roles.

---

## Regulations

### Q: Which regulations apply to my organization?

A:
- **FINRA?** If you're a securities broker/dealer
- **SEC?** If you're a registered investment adviser or public company
- **SOX?** If you're a public company
- **GLBA?** If you're a financial institution
- **OCC?** If you're a national bank
- **Federal Reserve?** If you're a bank holding company

Check with your Compliance Officer.

### Q: What if multiple regulations apply?

A: Implement controls that satisfy all:
1. Check Regulatory-Mappings.md for each regulation
2. Take strictest requirement
3. Document compliance with each
4. Implement control at highest level needed

Example: If both FINRA (1yr) and SEC (6yr) apply, implement 6-year retention.

### Q: Are there controls I don't need to implement?

A: Possibly. Review Regulatory-Mappings.md:
1. Find your regulations
2. See applicable controls
3. Implement those controls
4. Others are optional but recommended

### Q: We're not regulated. Do we still need governance?

A: Yes, best practices recommend:
- Basic security (MFA, DLP, audit)
- Change management
- Testing before production
- Incident response

Even without regulations, governance protects:
- Data
- Operations
- Reputation
- Business continuity

---

## Implementation

### Q: Should we do all phases at once?

A: No. The 8-week phased approach recommended:
- **Phase 1 (Weeks 1-2):** Assessment
- **Phase 2 (Weeks 3-4):** Security baseline
- **Phase 3 (Weeks 5-6):** Advanced governance
- **Phase 4 (Weeks 7-8):** Finalization

See Implementation-Checklist.md for details.

### Q: Can we start before full governance is ready?

A: Yes, by zone:
- **Zone 1:** Deploy immediately (no approval needed)
- **Zone 2:** Can deploy after basic approval workflow
- **Zone 3:** Must have full governance before production

Recommend completing Phase 1-2 before Zone 3 deployment.

### Q: What if we can't implement all controls by deadline?

A: Prioritize:
1. Security controls (Pillar 1) - highest priority
2. Regulatory requirements - next priority
3. Management controls (Pillar 2)
4. Reporting controls (Pillar 3)

Implement basic version for urgent items, mature over time.

### Q: Who leads implementation?

A: Typically:
- **Project Lead:** AI Governance Lead
- **Executive Sponsor:** Compliance Officer or CISO
- **Implementation Team:** 
  - Power Platform Admin (technical)
  - Compliance Officer (regulatory)
  - CISO or Security Admin (security)
  - Internal Audit (independent testing)

See RACI-Matrix.md for detailed roles.

---

## Operations & Monitoring

### Q: How often should we review controls?

A:
- **Zone 1:** Annual (if tracked)
- **Zone 2:** Quarterly
- **Zone 3:** Monthly + annual comprehensive

### Q: What's the difference between monitoring and assessment?

A:
- **Monitoring:** Continuous (daily/weekly) tracking of activity
- **Assessment:** Periodic (quarterly/annual) evaluation of control effectiveness

Both are needed.

### Q: How do we measure compliance?

A: Use maturity scorecard:
- Level 0 (0%): Not implemented
- Level 1 (25%): Baseline implemented
- Level 2 (50%): Developing toward recommended
- Level 3 (75%): Recommended implemented
- Level 4 (100%): Regulated/high-risk implemented

Track progress over time.

### Q: What if we find a compliance gap?

A: Follow incident management:
1. Document the gap
2. Assess severity and impact
3. Create remediation plan
4. Assign owner and deadline
5. Verify remediation
6. Document closure

See Control 3.4: Incident Reporting for details.

---

## Technology & Platforms

### Q: What platforms does this framework support?

A: All Microsoft 365 agents:
- Copilot Studio
- Agent Builder
- SharePoint agents
- Teams agents
- M365 Copilot agents

### Q: Do we need specific licenses?

A: Depends on controls:
- **Basic governance:** Standard M365 licenses
- **Advanced governance:** Premium licenses recommended for:
  - Purview Audit Premium (longer retention)
  - Managed Environments (governance enforcement)
  - DSPM for AI (data governance)

Check with your Microsoft account team.

### Q: Can we use other governance platforms?

A: Yes. Framework is platform-agnostic. You can:
- Use ServiceNow for change management
- Use Jira for incident tracking
- Use custom compliance tools
- Mix and match tools

Important: Ensure integration and audit trail.

---

## Audit & Compliance

### Q: How long do we keep records?

A: Depends on regulation:
- **FINRA 4511:** 6 years + 1 year accessible
- **SEC 17a-3/4:** 6 years + 3 years accessible
- **SOX 404:** 7 years minimum
- **GLBA:** 5-7 years
- **OCC/SR 11-7:** Per model (typically 3+ years)

See Regulatory-Mappings.md for your regulations.

### Q: What evidence do auditors want to see?

A: For each control:
1. **Policy documentation** (what should happen)
2. **Configuration proof** (technical setup screenshots)
3. **Activity logs** (evidence it's working)
4. **Test results** (verification that it works)
5. **Remediation records** (how issues were fixed)

### Q: How do we prepare for an audit?

A: Complete preparation process:
1. **Inventory all agents** (Control 3.1)
2. **Document policies and procedures** (Control 2.13)
3. **Compile audit evidence** (activity logs, approvals, tests)
4. **Perform control testing** (internal audit)
5. **Remediate any gaps** (document remediation)
6. **Create compliance summary** (executive overview)

### Q: What if auditors find a violation?

A: Remediation process:
1. **Root cause analysis:** Why did it happen?
2. **Corrective action:** Fix the issue
3. **Preventive action:** Stop recurrence
4. **Documentation:** Record everything
5. **Evidence:** Verify remediation worked
6. **Reporting:** Report to audit committee

---

## Troubleshooting

### Q: Our DLP policy isn't working.

A: Check:
1. Is the policy enabled?
2. Is it scoped to the right locations?
3. Is the rule correctly configured?
4. Are there any exceptions?
5. Have you tested with sample data?

See Control 1.5 for troubleshooting steps.

### Q: We're seeing too many false positives on DLP.

A: Tune your DLP:
1. Review rule sensitivity
2. Add exceptions for legitimate uses
3. Adjust thresholds
4. Test with realistic data
5. Document exceptions

### Q: Audit logs seem incomplete.

A: Verify:
1. Is audit logging enabled?
2. Is retention policy set?
3. Are all locations being logged?
4. Check for export/archival jobs
5. Verify access permissions to audit logs

### Q: We missed a control deadline.

A: Reassess:
1. What's the current state?
2. What's required by your zone/regulation?
3. Can you implement a baseline version quickly?
4. Create revised timeline
5. Document re-plan and approval

---

## Best Practices

### Q: What's the #1 governance mistake?

A: Not starting with **clear policies.**
- Define governance objectives
- Document approval procedures
- Communicate expectations
- Technology is secondary to process

### Q: How do we get buy-in?

A: Key stakeholders:
- **Business:** Show governance enables innovation (Zone 1 is fast)
- **Compliance:** Show you're meeting requirements
- **IT:** Show you're supporting their platform
- **Executives:** Show you're reducing risk

### Q: How do we scale governance?

A: As agents grow:
1. **Automate where possible** (DLP, audit)
2. **Delegate approvals** (managers for Zone 2)
3. **Create templates** (agent request forms)
4. **Use dashboards** (real-time monitoring)
5. **Document procedures** (make it repeatable)

---

## Getting Help

### Q: Where do I find details on a specific control?

A: Reference the control file:
- Example: "1.5-data-loss-prevention-dlp-and-sensitivity-labels.md"
- Each control has implementation guidance and verification steps

### Q: Who can I contact with questions?

A:
- **Governance:** Contact AI Governance Lead
- **Regulatory:** Contact Compliance Officer
- **Technical:** Contact Power Platform Admin
- **Security:** Contact CISO or Security Admin

### Q: Is there a glossary?

A: Yes! See Glossary.md for all terms and definitions.

### Q: Where can I get training?

A: See Control 2.14: Training & Awareness Program
- Role-specific training available
- Annual refresher required
- Compliance certification recommended

---

*FSI Agent Governance Framework Beta - December 2025*
