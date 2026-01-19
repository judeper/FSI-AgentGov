# Frequently Asked Questions (FAQ)

Common questions and answers about the FSI Agent Governance Framework.

---

## Getting Started

### Q: Where do I start?

A: Read in this order:

1. README.md (5 min overview)
2. [Zones Guide](../framework/zones-and-tiers.md) (understand your zone)
3. [Quick Start](../getting-started/quick-start.md) (30 min hands-on)
4. [Regulatory Mappings](../framework/regulatory-framework.md) (if regulated)

### Q: What if I don't know which zone my agent should be in?

A: Use the [Zone Decision Matrix](../framework/zones-and-tiers.md#zone-decision-matrix):

- Zone 1: Personal only, M365 data only
- Zone 2: Team/dept, internal data only
- Zone 3: Org-wide, customer data, regulated data

Ask your manager or compliance officer if unsure.

### Q: How long does implementation take?

A: Depends on current state:

- **Zone 1:** 1-2 days (minimal)
- **Zone 2:** 1-2 weeks (moderate)
- **Zone 3:** 3-6 weeks (comprehensive)

Full framework: 8-week phased approach (see the [Implementation Checklist](../getting-started/checklist.md))

---

## Framework Questions

### Q: Why are there 61 controls?

A: The framework covers:

- **Pillar 1:** 23 security controls
- **Pillar 2:** 21 management/lifecycle controls
- **Pillar 3:** 10 reporting/monitoring controls
- **Pillar 4:** 7 SharePoint-specific controls

Total = 61 controls covering all governance areas.

### Q: Do I need to implement all 61 controls?

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

## Environment Governance

### Q: How do I prevent users from creating agents in the default environment?

A: Enable **environment routing** in Power Platform Admin Center:

1. Navigate to PPAC → Manage → Environment groups
2. Enable **Default environment routing**
3. Configure routing rules to direct makers to appropriate environments
4. Optionally enable **Developer environment auto-provisioning**

This prevents shadow AI by automatically routing makers to governed environments. See [Control 2.15: Environment Routing](../controls/pillar-2-management/2.15-environment-routing.md).

### Q: Where can I see all agents across my tenant?

A: Use the **PPAC Inventory experience** (Preview):

1. Power Platform Admin Center → Resources → Agents
2. View tenant-wide agent list with metadata
3. Filter by environment, owner, or status
4. Note: Data refreshes every 24 hours; 500 agent display limit

Also check M365 Admin Center → Settings → Integrated Apps for published agents.

See [Control 3.1: Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).

### Q: How do I promote an agent from Zone 2 to Zone 3?

A: Follow the **zone promotion process**:

1. Complete all Zone 3 governance requirements
2. Submit formal promotion request to Governance Committee
3. Undergo security and compliance review
4. Configure production environment with Managed Environment enabled
5. Use ALM pipelines to deploy from test to production
6. Document promotion and retain evidence

See [Lifecycle Governance Guide](../framework/agent-lifecycle.md) and [Control 2.3: Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

### Q: What are Environment Groups and how do they help governance?

A: **Environment Groups** allow you to:

- Group environments by zone (Zone 1, Zone 2, Zone 3)
- Apply consistent governance rules across all environments in a group
- Enforce connector policies, sharing limits, and AI model restrictions
- Prevent configuration drift with centralized rule management

Navigate to PPAC → Manage → Environment groups to configure. See [Control 2.2: Environment Groups](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md).

### Q: What is the Copilot Hub?

A: The **Copilot Hub** (in Power Platform Admin Center) provides:

- Centralized dashboard for agent governance
- Usage and adoption metrics
- ROI tracking and business value insights
- Capacity/consumption monitoring
- Quick access to governance controls

Access via PPAC → Copilot. See [Control 3.8: Copilot Hub](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md).

### Q: How do I monitor AI data security risks?

A: Use **Microsoft Purview DSPM for AI**:

1. Navigate to purview.microsoft.com → DSPM for AI
2. Review recommendations for AI security
3. Enable activity monitoring for AI interactions
4. Configure DLP policies targeting AI applications
5. Run oversharing assessments for agent knowledge sources

See [Control 1.6: DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

### Q: How many controls are in the framework?

A: The framework includes 61 controls across four pillars:

- **Pillar 1 - Security:** 23 controls (1.1-1.23) covering DLP, encryption, audit logging, eDiscovery
- **Pillar 2 - Management:** 21 controls (2.1-2.21) covering lifecycle, change control, environment routing
- **Pillar 3 - Reporting:** 10 controls (3.1-3.10) covering inventory, monitoring, incidents, Sentinel
- **Pillar 4 - SharePoint:** 7 controls (4.1-4.7) covering SharePoint-specific governance

See [Control Index](../controls/CONTROL-INDEX.md) for the complete list.

### Q: How do I monitor my Power Platform security posture?

A: Use the **PPAC Security Posture Assessment**:

1. Navigate to Power Platform Admin Center → Security → Overview
2. Review your security score (Low/Medium/High)
3. View security recommendations
4. Click recommendations to see remediation steps
5. Track improvements over time

This provides a centralized view of tenant security configuration. See [Control 3.7: PPAC Security Posture Assessment](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md).

### Q: How do I integrate with Microsoft Sentinel for agent monitoring?

A: For Zone 3 agents requiring SOC integration:

1. Configure Microsoft Sentinel workspace in Azure
2. Enable Power Platform data connector in Sentinel
3. Create analytics rules for agent-related security events:
   - Unusual agent data access patterns
   - Connector policy violations
   - Environment configuration changes
4. Configure incident response playbooks
5. Integrate with your SOC procedures

This enables real-time threat detection and automated response for production agents. See [Control 3.9: Microsoft Sentinel Integration](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

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
4. Escalate if needed per the [RACI Matrix](../framework/operating-model.md)

### Q: Who is the Governance Committee?

A: Typically:

- AI Governance Lead (Chair)
- Compliance Officer
- CISO
- General Counsel
- Chief Risk Officer (if applicable)
- Business owner (agent requester)

See the [RACI Matrix](../framework/operating-model.md) for detailed roles.

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

1. Check [Regulatory Mappings](../framework/regulatory-framework.md) for each regulation
2. Take strictest requirement
3. Document compliance with each
4. Implement control at highest level needed

Example: If both FINRA (1yr) and SEC (6yr) apply, implement 6-year retention.

### Q: Are there controls I don't need to implement?

A: Possibly. Review [Regulatory Mappings](../framework/regulatory-framework.md):

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

See the [Implementation Checklist](../getting-started/checklist.md) for details.

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

See the [RACI Matrix](../framework/operating-model.md) for detailed roles.

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

A: Microsoft 365 agents and related in-suite Copilot experiences, including:

- Copilot Studio agents
- Agent Builder agents
- SharePoint agents
- Teams agents
- Microsoft 365 Copilot

### Q: Do we need specific licenses?

A: Depends on controls:

- **Basic governance:** Standard M365 licenses
- **Advanced governance:** Premium licenses recommended for:
  - Purview Audit Premium (longer retention)
  - Managed Environments (governance enforcement)
  - DSPM for AI (data governance)

Check with your Microsoft account team.

### Q: What about Agent 365 and Entra Agent ID?

A: Some controls reference Microsoft features that are currently in preview:

| Feature | Status (Jan 2026) | Access |
|---------|-------------------|--------|
| **Agent 365** | Frontier Preview | Requires Frontier program enrollment |
| **Entra Agent ID** | Public Preview | Available in Entra Admin Center |
| **Advanced Connector Policies (ACP)** | Preview | Available in PPAC |
| **Environment Groups** | Preview | Available in PPAC |

**To access preview features:**

1. **Frontier program:** Sign up at the Microsoft 365 Admin Center → Settings → Org settings → Frontier
2. **Agent ID:** Navigate to Entra Admin Center → Enterprise applications → Filter by "Agent ID (Preview)"

Controls that reference preview features include appropriate disclaimers. Check [Microsoft Learn](https://learn.microsoft.com/en-us/entra/agent-id/) for current availability.

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

See [Regulatory Mappings](../framework/regulatory-framework.md) for your regulations.

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

## Exceptions & Risk Acceptance

### Q: What if we cannot implement a required control?

A: Document an exception with risk acceptance:

1. **Document the gap:** Identify the control and what cannot be implemented
2. **Explain the reason:** Technical limitation, business constraint, or cost prohibition
3. **Assess the risk:** What is the potential impact of non-implementation?
4. **Identify compensating controls:** What alternative measures reduce the risk?
5. **Obtain approval:** Get sign-off from appropriate authority (see below)
6. **Set review date:** Schedule periodic re-evaluation

### Q: Who must approve a control exception?

A: Approval authority depends on the zone and control criticality:

| Zone | Non-Critical Controls | Critical Controls |
|------|----------------------|-------------------|
| Zone 1 | Manager | AI Governance Lead |
| Zone 2 | AI Governance Lead | Governance Committee |
| Zone 3 | Governance Committee | Governance Committee + Executive Sponsor |

Critical controls include: DLP (1.5), Audit Logging (1.7), MFA (1.11), Access Control (2.8).

### Q: What are compensating controls?

A: Alternative measures that reduce risk when the primary control cannot be implemented:

| Primary Control Gap | Possible Compensating Controls |
|--------------------|-------------------------------|
| Automated DLP not available | Manual review process, restricted data access |
| Environment routing not enabled | Weekly audit of default environment, cleanup procedures |
| Sentinel integration not licensed | Enhanced manual log review, third-party SIEM |
| Managed Environments not licensed | More frequent manual audits, stricter approval process |

Document compensating controls with evidence of their effectiveness.

### Q: How long can an exception remain open?

A: Exception durations:

- **Temporary exceptions:** Maximum 90 days, then re-evaluate
- **Long-term exceptions:** Maximum 12 months, requires annual renewal
- **Permanent exceptions:** Rare, requires Governance Committee approval and annual attestation

All exceptions should include a remediation target date when feasible.

### Q: How do we document exceptions for auditors?

A: Maintain an **Exception Register** with:

1. **Control ID and name**
2. **Exception description** (what is not implemented)
3. **Business justification**
4. **Risk assessment** (likelihood × impact)
5. **Compensating controls** (with evidence)
6. **Approval record** (who approved, when)
7. **Review schedule** (next review date)
8. **Remediation plan** (if applicable)

Auditors expect documented risk acceptance decisions, not undocumented gaps.

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

*FSI Agent Governance Framework v1.1 - January 2026*
