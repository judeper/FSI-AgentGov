# Implementation Checklist

Step-by-step checklist for implementing the FSI Agent Governance Framework.

---

## Phase 1: Assessment & Planning (Weeks 1-2)

### Week 1: Current State Analysis

- [ ] **Conduct Framework Orientation (Day 1)**
  - [ ] Review README.md overview
  - [ ] Understand 4 pillars and 3 zones
  - [ ] Identify project lead and team

- [ ] **Identify Existing Agents (Day 2-3)**
  - [ ] Export current agent inventory from M365 Admin Center
  - [ ] List all agents with owner and description
  - [ ] Identify data sources for each agent
  - [ ] Document current governance procedures (if any)

- [ ] **Regulatory Assessment (Day 4-5)**
  - [ ] Identify primary regulations (FINRA, SEC, SOX, GLBA, OCC, Fed)
  - [ ] Review [Regulatory Framework](../framework/regulatory-framework.md) for your regulations
  - [ ] Determine which controls apply
  - [ ] Check regulatory filing requirements

- [ ] **Compliance Baseline (Day 5)**
  - [ ] Current DLP coverage
  - [ ] Current audit retention policies
  - [ ] Current MFA implementation
  - [ ] Current change control procedures

### Week 2: Planning & Governance Setup

- [ ] **Establish Governance Structure**
  - [ ] Assign AI Governance Lead
  - [ ] Assign Compliance Officer sponsor
  - [ ] Define Governance Committee (Zone 3)
  - [ ] Schedule governance meetings

- [ ] **Classify Existing Agents (Day 1-3)**
  - [ ] Use the [Zone Decision Matrix](../framework/zones-and-tiers.md#zone-decision-matrix)
  - [ ] Assign each agent to Zone 1, 2, or 3
  - [ ] Document classification rationale
  - [ ] Identify Zone 3 agents for priority handling

- [ ] **Create Implementation Roadmap (Day 4-5)**
  - [ ] Map controls to implementation phases
  - [ ] Prioritize by regulatory requirement
  - [ ] Assign ownership per [Operating Model](../framework/operating-model.md)
  - [ ] Create timeline and milestones

- [ ] **Project Kickoff (Day 5)**
  - [ ] Present framework to leadership
  - [ ] Get executive sponsorship
  - [ ] Assign project team
  - [ ] Schedule regular steering committee meetings

---

## Phase 2: Foundation Implementation (Weeks 3-4)

### Week 3: Environment Governance

- [ ] **Environment Routing (Control 2.15)** ⭐ NEW
  - [ ] Navigate to PPAC → Manage → Environment groups
  - [ ] Enable default environment routing
  - [ ] Configure routing rules for security groups
  - [ ] Enable developer environment auto-provisioning
  - [ ] Test maker routing with new app creation
  - [ ] Document routing configuration

- [ ] **Environment Groups (Control 2.2)**
  - [ ] Create environment groups for Zone 1, Zone 2, Zone 3
  - [ ] Apply connector policies per zone
  - [ ] Configure sharing limits per zone
  - [ ] Enable AI model rules if applicable
  - [ ] Document group-to-zone mapping

- [ ] **Managed Environments (Control 2.1)**
  - [ ] Enable Managed Environment for Zone 2+ environments
  - [ ] Configure governance policies
  - [ ] Test policy enforcement
  - [ ] Document Managed Environment settings

### Week 3: Security Baseline

- [ ] **Authentication & Access (Pillar 1)**
  - [ ] **Control 1.11: Conditional Access**
    - [ ] Enable MFA for all agent creators/admins
    - [ ] Require MFA from outside corporate network
    - [ ] Test MFA enforcement
    - [ ] Document MFA policy

  - [ ] **Control 1.18: RBAC**
    - [ ] Define security roles (Creator, Editor, Admin, Viewer)
    - [ ] Assign least-privilege access
    - [ ] Document role definitions
    - [ ] Test access controls

- [ ] **Data Protection (Pillar 1)**
  - [ ] **Control 1.5: DLP and Sensitivity Labels**
    - [ ] Review baseline sensitive data types (PII, financial, etc.)
    - [ ] Create test DLP policy
    - [ ] Test DLP with sample files
    - [ ] Enable sensitivity labels for SharePoint
    - [ ] Document DLP rules

  - [ ] **Control 1.15: Encryption**
    - [ ] Verify default encryption (TLS 1.2+ in transit)
    - [ ] Verify Microsoft 365 encryption at rest
    - [ ] Document encryption standards
    - [ ] For Zone 3: Plan for customer-managed keys

- [ ] **Audit & Monitoring (Pillar 1)**
  - [ ] **Control 1.7: Audit Logging**
    - [ ] Access Purview Audit logs
    - [ ] Configure audit retention policy
    - [ ] Set retention period per regulation:
      - [ ] Zone 2: 1 year
      - [ ] Zone 3: 6+ years (see control for options)
    - [ ] Test audit log search
    - [ ] Document retention policy

### Week 4: Governance Foundation

- [ ] **Registry & Inventory (Pillar 3)**
  - [ ] **Control 3.1: Agent Inventory**
    - [ ] Create agent registry (spreadsheet or database)
    - [ ] Fields: ID, Name, Owner, Zone, Data Sources, Status, Approval Date
    - [ ] Import all existing agents
    - [ ] Assign owners
    - [ ] Document metadata for each agent

- [ ] **Approval Workflow (Pillar 2)**
  - [ ] **Control 2.12: Supervision & Oversight**
    - [ ] Document approval procedures
    - [ ] Define approval authority by zone:
      - [ ] Zone 1: Self-service
      - [ ] Zone 2: Manager approval
      - [ ] Zone 3: Governance committee
    - [ ] Create approval template/form
    - [ ] Identify approvers

- [ ] **Change Management (Pillar 2)**
  - [ ] **Control 2.3: Change Management**
    - [ ] Define change control process
    - [ ] Document change procedures
    - [ ] Test change workflow
    - [ ] Identify change approvers
    - [ ] Create change log template

- [ ] **Documentation (Pillar 2)**
  - [ ] **Control 2.13: Documentation & Record Keeping**
    - [ ] Establish document repository (SharePoint site)
    - [ ] Create governance documentation index
    - [ ] Store policies and procedures
    - [ ] Ensure version control
    - [ ] Document access controls

---

## Phase 3: Advanced Governance (Weeks 5-6)

### Week 5: Risk Management & Testing

- [ ] **Model Risk (Pillar 2)**
  - [ ] **Control 2.6: Model Risk Management**
    - [ ] For agents using AI/ML:
      - [ ] Document model purpose and use case
      - [ ] Identify model inputs and outputs
      - [ ] Define performance baseline
      - [ ] For Zone 3: Plan model validation
    - [ ] If OCC/SR 11-7 applicable:
      - [ ] Perform model risk assessment
      - [ ] Plan annual validation

- [ ] **Testing & Validation (Pillar 2)**
  - [ ] **Control 2.5: Testing & Validation**
    - [ ] Define testing requirements per agent type
    - [ ] Create test plans for critical agents
    - [ ] Perform functionality testing
    - [ ] For Zone 3: Perform security testing
    - [ ] Document test results
    - [ ] Archive test evidence

- [ ] **Bias Testing (Pillar 2)**
  - [ ] **Control 2.11: Bias Testing**
    - [ ] For credit/employment agents:
      - [ ] Define fairness metrics
      - [ ] Plan quarterly bias testing
      - [ ] Document expected outcomes
      - [ ] Establish remediation procedures
    - [ ] For customer-facing agents:
      - [ ] Plan fairness assessment
      - [ ] Document results

### Week 6: Advanced Security & Compliance

- [ ] **Advanced Data Protection (Pillar 1)**
  - [ ] **Control 1.4: Advanced Connector Policies**
    - [ ] Review high-risk connectors
    - [ ] Create allowlist of approved connectors
    - [ ] Block unauthorized connectors
    - [ ] Document connector policy
    - [ ] Test with sample agent

  - [ ] **Control 1.6: DSPM for AI**
    - [ ] Navigate to purview.microsoft.com → DSPM for AI
    - [ ] Complete Get Started setup steps
    - [ ] Review recommendations and enable policies
    - [ ] Configure activity monitoring
    - [ ] Run oversharing assessments for agent knowledge sources
    - [ ] Document DSPM setup

  - [ ] **Control 1.19: eDiscovery for Agent Interactions** ⭐ NEW
    - [ ] Assign eDiscovery administrator role
    - [ ] Document agent content locations (Teams, SharePoint)
    - [ ] Create case templates for regulatory inquiries
    - [ ] Test search for agent content
    - [ ] Document legal hold procedures

- [ ] **Compliance Reporting (Pillar 3)**
  - [ ] **Control 3.3: Compliance & Regulatory Reporting**
    - [ ] Design compliance dashboard
    - [ ] Define key compliance metrics
    - [ ] Create monthly compliance report template
    - [ ] For Zone 3: Create quarterly regulatory report
    - [ ] Identify report recipients

- [ ] **Incident Management (Pillar 3)**
  - [ ] **Control 3.4: Incident Reporting**
    - [ ] Define incident categories
    - [ ] Create incident tracking process
    - [ ] Document incident investigation procedures
    - [ ] Create RCA template
    - [ ] Define escalation procedures

- [ ] **PPAC Reporting** ⭐ NEW
  - [ ] **Control 3.7: PPAC Security Posture Assessment**
    - [ ] Access PPAC → Security → Overview
    - [ ] Review security score (Low/Medium/High)
    - [ ] Document baseline security posture
    - [ ] Create plan to address recommendations
    - [ ] Schedule weekly security score reviews

  - [ ] **Control 3.8: Copilot Hub**
    - [ ] Access PPAC → Copilot hub
    - [ ] Review agent counts and usage metrics
    - [ ] Monitor capacity/consumption status
    - [ ] Configure governance controls
    - [ ] Schedule weekly metrics review

  - [ ] **Control 3.9: Microsoft Sentinel Integration** (Zone 3)
    - [ ] Assess Sentinel integration requirements
    - [ ] Configure Sentinel workspace (if applicable)
    - [ ] Enable Power Platform data connector
    - [ ] Create analytics rules for agent threats
    - [ ] Document SOC integration procedures

---

## Phase 4: Finalization & Operations (Weeks 7-8)

### Week 7: Completion & Hardening

- [ ] **Remaining Security Controls (Pillar 1)**
  - [ ] **Control 1.1: Restrict Agent Publishing**
    - [ ] Configure publishing security groups
    - [ ] Require approval for shared agents
    - [ ] Test publishing restrictions

  - [ ] **Control 1.3: SharePoint Governance**
    - [ ] Restrict agent access to approved SharePoint sites
    - [ ] Apply sensitivity labels
    - [ ] Limit external sharing
    - [ ] Document permissions

  - [ ] **Control 1.2: Integrated Apps Management**
    - [ ] Review all integrated apps in M365 Admin Center
    - [ ] Audit connector permissions
    - [ ] Remove unnecessary integrations

- [ ] **Monitoring & Performance (Pillar 3)**
  - [ ] **Control 3.2: Usage Analytics**
    - [ ] Enable analytics in Power Platform Admin Center
    - [ ] Create usage dashboard
    - [ ] Set baseline metrics
    - [ ] Configure performance alerts

  - [ ] **Control 3.5: Cost Allocation**
    - [ ] Review agent-related costs
    - [ ] Create cost allocation model
    - [ ] Assign costs to business units
    - [ ] Create cost tracking dashboard

### Week 8: Training, Documentation & Operationalization

- [ ] **Training Program (Pillar 2)**
  - [ ] **Control 2.14: Training & Awareness**
    - [ ] Create training curriculum:
      - [ ] Zone 1 users: Basic governance overview
      - [ ] Zone 2 users: Governance, approval, best practices
      - [ ] Zone 3 operators: Complete framework
      - [ ] Compliance team: Regulatory requirements
    - [ ] Conduct training sessions
    - [ ] Track training completion
    - [ ] Obtain attestation of understanding

- [ ] **Operationalization (All Pillars)**
  - [ ] **Establish Recurring Reviews**
    - [ ] Schedule quarterly control assessments
    - [ ] Schedule quarterly compliance reviews (Zone 2+)
    - [ ] Schedule monthly monitoring (Zone 3)
    - [ ] Schedule annual framework review

  - [ ] **Create Operating Procedures**
    - [ ] Daily monitoring procedures
    - [ ] Weekly compliance reviews
    - [ ] Monthly reporting
    - [ ] Quarterly assessments
    - [ ] Annual updates

  - [ ] **Stakeholder Communication**
    - [ ] Communicate framework rollout
    - [ ] Share governance policies
    - [ ] Provide quick reference guides
    - [ ] Establish help/support channels

- [ ] **Final Verification (All Controls)**
  - [ ] **Go/No-Go Assessment**
    - [ ] Verify all Phase 1-3 items complete
    - [ ] Test critical controls
    - [ ] Verify monitoring active
    - [ ] Confirm training complete
    - [ ] Obtain executive sign-off

- [ ] **Launch** 🚀
  - [ ] Communicate framework is live
  - [ ] Activate monitoring and alerts
  - [ ] Begin operational reviews
  - [ ] Establish support procedures

---

## Ongoing Operations (After Week 8)

- [ ] **Daily**
  - [ ] Monitor alerts and incidents
  - [ ] Review security warnings

- [ ] **Weekly**
  - [ ] Review compliance status
  - [ ] Check for new agents
  - [ ] Monitor performance

- [ ] **Monthly**
  - [ ] Compliance review meeting
  - [ ] Dashboard reporting
  - [ ] Zone 3: Deep compliance review

- [ ] **Quarterly**
  - [ ] Control effectiveness assessment
  - [ ] Compliance maturity review
  - [ ] Governance committee meeting (Zone 3)
  - [ ] Update controls as needed

- [ ] **Annually**
  - [ ] Framework review and update
  - [ ] Training refresher
  - [ ] Model validation (Zone 3, if applicable)
  - [ ] Audit and SOX testing
  - [ ] Regulatory updates assessment

---

## Success Criteria

- [ ] All 60 controls implemented at appropriate maturity levels
- [ ] Agent inventory complete and maintained
- [ ] Compliance dashboard active and monitored
- [ ] Training completed for all users
- [ ] Incident management procedures operational
- [ ] Audit logging and retention in place
- [ ] Regulatory requirements met
- [ ] Governance team trained and operational
- [ ] Executive leadership informed and supportive

---

## Quick Reference: Controls by Pillar

**Pillar 1 (Security): 23 Controls**
1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19 ⭐, 1.20 ⭐, 1.21 ⭐, 1.22 ⭐, 1.23 ⭐

**Pillar 2 (Management): 20 Controls**
2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14, 2.15 ⭐, 2.16 ⭐, 2.17 ⭐, 2.18 ⭐, 2.19 ⭐, 2.20 ⭐

**Pillar 3 (Reporting): 10 Controls**
3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7 ⭐, 3.8 ⭐, 3.9 ⭐, 3.10 ⭐

**Pillar 4 (SharePoint): 7 Controls**
4.1, 4.2, 4.3, 4.4, 4.5, 4.6 ⭐, 4.7 ⭐

⭐ = New controls

---

*FSI Agent Governance Framework v1.1 - January 2026*
