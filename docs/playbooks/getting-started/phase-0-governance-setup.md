# Phase 0: Governance Setup

Foundation phase for establishing governance structure and core controls (0-60 days).

---

## Overview

Phase 0 establishes the organizational foundation and minimum viable controls needed to enable secure AI agent experimentation while maintaining governance oversight.

**Timeline:** 0-60 days
**Outcome:** Governance structure in place, Zone 1 and Zone 2 environments enabled

---

## Week 1-2: Governance Structure

### Identify Key Roles

- [ ] **AI Governance Lead** — Assign individual with accountability for framework
- [ ] **Power Platform Admin** — Assign technical lead for platform configuration
- [ ] **Compliance Officer liaison** — Identify compliance point of contact
- [ ] **CISO liaison** — Identify security point of contact

### Initial Documentation

- [ ] Review FSI Agent Governance Framework documentation
- [ ] Draft governance committee charter (for Zone 3 preparation)
- [ ] Identify existing policies that apply to AI agents
- [ ] Document current state of any existing agents

### Kickoff Meeting

Conduct kickoff meeting with key stakeholders:

- [ ] Present framework overview
- [ ] Agree on implementation timeline
- [ ] Assign ownership for Phase 0 tasks
- [ ] Schedule weekly check-ins

---

## Week 3-4: Core Technical Controls

### Control 2.1: Managed Environments

**Purpose:** Enable governance features for Zone 2 environments

**Steps:**

1. Navigate to Power Platform Admin Center
2. Go to Environments > [Zone 2 Environment] > Settings
3. Enable "Managed Environment"
4. Configure baseline settings

**Verification:**

- [ ] Managed Environment shows as enabled
- [ ] Environment details show managed features available

### Control 1.1: Restrict Agent Publishing

**Purpose:** Prevent unauthorized agent deployment

**Steps:**

1. Navigate to PPAC > Manage > Environment groups
2. Create Zone 1 and Zone 2 environment groups
3. Configure sharing rules:
   - Zone 1: Disabled sharing
   - Zone 2: Controlled sharing
4. Assign environments to groups

**Verification:**

- [ ] Attempt to share agent outside policy fails
- [ ] Environment group rules active

### Control 1.5: DLP Policies

**Purpose:** Prevent sensitive data from reaching unauthorized connectors

**Steps:**

1. Navigate to PPAC > Policies > Data policies
2. Create baseline DLP policy
3. Classify connectors:
   - Business (approved)
   - Non-business (restricted)
   - Blocked
4. Apply to Zone 2 environments

**Verification:**

- [ ] Attempt to use blocked connector fails
- [ ] Policy shows as active

### Control 1.7: Audit Logging (Baseline)

**Purpose:** Ensure agent activities are recorded

**Steps:**

1. Navigate to Microsoft Purview compliance portal
2. Go to Audit
3. Verify auditing is enabled for Power Platform
4. Configure retention (30 days for Zone 1, 1 year for Zone 2)

**Verification:**

- [ ] Test action appears in audit log
- [ ] Retention settings correct

---

## Week 5-6: Environment Setup

### Environment Architecture

Create the following environment structure:

| Environment | Zone | Purpose | Managed? |
|-------------|------|---------|----------|
| Personal-[User] | 1 | Individual development | No |
| Team-[Department] | 2 | Team collaboration | Yes |
| Test | 2 | Testing and validation | Yes |

### Environment Groups

Configure environment groups in PPAC:

**Zone 1 Group:**

- Sharing: Disabled
- Channels: M365 Chat only
- AI features: All allowed (experimental)

**Zone 2 Group:**

- Sharing: Controlled (team only)
- Channels: Teams, SharePoint
- AI features: Production-ready only

### Control 2.15: Environment Routing

**Purpose:** Automatically route makers to appropriate environments

**Steps:**

1. Navigate to PPAC > Manage > Default environment routing
2. Enable routing
3. Map security groups to environments
4. Configure fallback environment

**Verification:**

- [ ] New maker lands in correct environment
- [ ] Routing rules active

---

## Week 7-8: Operational Readiness

### Control 3.1: Agent Inventory

**Purpose:** Establish central registry of all agents

**Steps:**

1. Create SharePoint list or other tracking mechanism
2. Define required metadata fields:
   - Agent ID
   - Agent Name
   - Owner
   - Zone
   - Status
   - Creation Date
3. Document inventory process
4. Inventory any existing agents

**Verification:**

- [ ] Inventory accessible to governance team
- [ ] Process documented

### Control 2.3: Change Management

**Purpose:** Establish controlled change process for Zone 2+ agents

**Steps:**

1. Document change management workflow
2. Create change request template
3. Define approval requirements by zone
4. Communicate process to makers

**Verification:**

- [ ] Process documented
- [ ] Template available

### Training

- [ ] Complete Power Platform Admin training
- [ ] Review governance framework with compliance team
- [ ] Brief department managers on Zone 2 requirements

### First Governance Meeting

Conduct first governance review meeting:

- [ ] Review Phase 0 completion status
- [ ] Discuss any issues encountered
- [ ] Plan Phase 1 priorities
- [ ] Schedule recurring meetings

---

## Phase 0 Completion Checklist

### Governance Structure

- [ ] AI Governance Lead assigned
- [ ] Key roles identified
- [ ] Governance committee charter drafted
- [ ] Weekly meetings scheduled

### Technical Controls

- [ ] Managed Environments enabled for Zone 2
- [ ] Agent publishing restrictions in place
- [ ] DLP policies configured
- [ ] Audit logging verified

### Environments

- [ ] Zone 1 environment group configured
- [ ] Zone 2 environment group configured
- [ ] Environment routing enabled
- [ ] Test environment available

### Operations

- [ ] Agent inventory process established
- [ ] Change management process documented
- [ ] Key stakeholders trained

---

## Success Criteria

Phase 0 is complete when:

1. AI Governance Lead can demonstrate publishing restrictions work
2. DLP policies prevent unauthorized data flow
3. Agent inventory process is operational
4. At least one Zone 2 environment is ready for use
5. Governance team has completed initial training

---

## Next Phase

Proceed to [Phase 1: Minimal Viable Controls](phase-1-minimal-viable-controls.md) to implement production readiness controls.

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.1*
