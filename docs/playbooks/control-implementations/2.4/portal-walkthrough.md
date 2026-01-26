# Control 2.4: Business Continuity and Disaster Recovery - Portal Walkthrough

> This playbook provides portal-based configuration guidance for [Control 2.4](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md).

---

## Overview

This walkthrough guides you through configuring BC/DR capabilities in the Power Platform Admin Center, including creating DR environments, configuring backups, and setting up monitoring.

---

## Part 1: Classify Agents by Criticality

Before configuring BC/DR infrastructure, classify agents by business criticality.

### Criticality Tiers

| Tier | Description | RTO | RPO | Examples |
|------|-------------|-----|-----|----------|
| **Tier 1 - Critical** | Business cannot operate | <1 hour | <15 min | Trading assistant, Payment processor |
| **Tier 2 - High** | Significant impact | <4 hours | <1 hour | Customer service, Compliance agent |
| **Tier 3 - Medium** | Moderate impact | <24 hours | <4 hours | Internal HR bot, IT help desk |
| **Tier 4 - Low** | Minimal impact | <72 hours | <24 hours | Personal productivity agents |

### Document in BC/DR Plan

For each agent, capture:
- Agent ID and name
- Business owner
- Criticality tier
- Dependencies (data sources, connectors, integrations)
- Recovery priority order

---

## Part 2: Create Secondary Region Environments

**Portal Path:** Power Platform Admin Center > Environments > + New

### Steps

1. Navigate to **Power Platform Admin Center** (admin.powerplatform.microsoft.com)
2. Select **Environments** > Click **+ New**
3. **Create DR Environment:**
   - **Name:** "[Primary Env Name]-DR"
   - **Region:** Select different geographic region
   - **Type:** Production
   - **Purpose:** Disaster recovery for [Primary Env]
4. **Configure Environment:**
   - Enable Managed Environment
   - Apply same DLP policies as primary
   - Configure same security roles
5. **Document Region Mapping:**

| Primary Region | DR Region |
|----------------|-----------|
| East US | West US |

Select two regions that meet your organization's data residency and operational resilience requirements.

---

## Part 3: Configure Dataverse Backup Settings

**Portal Path:** Power Platform Admin Center > Environments > [Environment] > Backups

### Steps

1. Navigate to **Power Platform Admin Center**
2. Select **Environments** > Choose production environment
3. Click **Backups** in the left navigation
4. **Review System Backups:**
   - Microsoft provides automatic daily backups (retained 28 days)
   - System backups occur automatically
5. **Configure Additional Protection:**
   - Click **Schedule backup** for on-demand backups before major changes
   - Document backup schedule in BC/DR plan
6. **Note Limitations:**
   - System backups restore entire environment
   - For granular agent restore, use solution-based backup

---

## Part 4: Deploy Agents to DR Environment

**Portal Path:** Power Platform Admin Center > Solutions > Import

### Initial DR Deployment

1. Import latest solution backup to DR environment
2. Configure environment variables for DR region
3. Test agent functionality in DR environment

### Configure Connection References

1. Update connection references to use DR-region resources
2. Create service accounts for DR environment
3. Document connection mapping

---

## Part 5: Configure Service Health Monitoring

**Portal Path:** Microsoft 365 Admin Center > Health > Service health

### Steps

1. Navigate to **Microsoft 365 Admin Center**
2. Select **Health** > **Service health**
3. Click **Preferences** > **Email**
4. Enable alerts for:
   - Power Platform
   - Dataverse
   - SharePoint Online (if used for knowledge)
   - Azure Active Directory

### Communication Plan

| Severity | Response Time | Notification |
|----------|---------------|--------------|
| Critical | Immediate | Phone + SMS + Email |
| High | 15 minutes | Email + Teams |
| Medium | 1 hour | Email |
| Low | Next business day | Email |

---

## Part 6: Create DR Runbook

### DR Declaration Process

```
Trigger Criteria:
- Primary region unavailable >30 minutes
- Microsoft declares regional outage
- Security incident requiring failover

Declaration Authority:
- CIO or delegate
- IT Operations Director
- On-call manager (after hours)

Notification List:
- Executive leadership
- Business unit heads
- IT operations team
- Customer communications team
```

### Recovery Runbook - Tier 1 Agents

```
Step 1: Verify DR Environment Status (5 min)
[ ] Login to DR environment
[ ] Verify agent solutions are deployed
[ ] Confirm connectivity to data sources

Step 2: Activate DR Agents (15 min)
[ ] Update DNS/traffic routing to DR
[ ] Enable agent endpoints
[ ] Verify OAuth connections

Step 3: Test Agent Functionality (15 min)
[ ] Execute test conversations
[ ] Verify data source connectivity
[ ] Confirm critical functions working

Step 4: Communicate Status (5 min)
[ ] Notify stakeholders of DR activation
[ ] Update status page
[ ] Log DR event for regulatory purposes

Total Estimated Time: 40 minutes
```

### Failback Procedure

```
Pre-Failback Checklist:
[ ] Primary region confirmed stable
[ ] Microsoft all-clear received
[ ] Data sync verification complete

Failback Steps:
[ ] Synchronize any DR changes to primary
[ ] Update routing to primary region
[ ] Test primary agent functionality
[ ] Deactivate DR agents (standby mode)
[ ] Document failback completion
```

---

## Part 7: Schedule and Conduct DR Testing

### Annual DR Test Process

**Pre-Test Planning (2 weeks before):**
- Schedule test window with stakeholders
- Notify affected business units
- Prepare test scenarios
- Brief DR team

**DR Test Execution:**

```
Test Scenario: Regional Outage Simulation

Phase 1: Failover (Target: <1 hour for Tier 1)
- Simulate primary region unavailability
- Execute DR declaration process
- Activate DR environment
- Route traffic to DR

Phase 2: Operation (2-4 hours)
- Execute business-critical transactions
- Test all Tier 1 agent functions
- Verify data integrity
- Monitor performance

Phase 3: Failback (Target: <2 hours)
- Confirm primary region available
- Synchronize data changes
- Execute failback procedure
- Verify primary operation
```

**Post-Test Documentation:**
- Test results summary
- RTO/RPO achievement status
- Issues encountered
- Corrective actions
- Lessons learned
- Sign-off from business owners

---

---

[Back to Control 2.4](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
