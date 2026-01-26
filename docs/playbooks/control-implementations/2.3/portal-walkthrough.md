# Control 2.3: Change Management and Release Planning - Portal Walkthrough

> This playbook provides portal-based configuration guidance for [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

---

## Prerequisites

Before starting, ensure you have:

- Power Platform Admin role or Environment Admin role for target environments
- Managed Environments enabled for Zone 2 and Zone 3 environments
- Solution publisher configured in development environment
- Access to all pipeline stage environments (dev, test, prod)
- Approval workflow recipients identified

---

## Overview

This walkthrough guides you through configuring ALM pipelines and change management workflows in the Power Platform Admin Center and Power Apps maker portal.

---

## Part 1: Access PPAC Deployment Section

The Power Platform Admin Center provides a dedicated **Deployment** section for pipeline administration.

### Steps

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Deployment** in left navigation
3. Select sub-section: Overview, Pipelines, Settings, or Catalogs

### Deployment Overview Dashboard

The dashboard displays:
- Pipelines activity
- Pending approvals count
- Failed deployments count
- Quick access to setup guides

---

## Part 2: Configure Deployment Settings

| Setting | Description | FSI Recommendation |
|---------|-------------|-------------------|
| **Enable Auto-Conversion of Target Environments to Managed** | Automatically converts target environments to Managed | Enable for enterprise managed |
| **Solution deployments across regions** | Allow cross-region deployments | Configure per policy |
| **Allow makers to import shared solution deployments** | Makers can import shared solutions | Enable for team/enterprise |

> **Warning:** Target environments in pipelines must be enabled as Managed Environments. This ensures every environment used in pipelines meets Microsoft Enterprise compliance standards.

---

## Part 3: Set Up ALM Pipelines

Power Platform pipelines enable automated, governed deployments.

### Pipeline Configuration by Governance Zone

| Zone | Pipeline Required | Stages | Approval Gates |
|------|-------------------|--------|----------------|
| Zone 1 | No | N/A | N/A |
| Zone 2 | Recommended | Dev > Test | Manager |
| Zone 3 | **Required** | Dev > Test > Prod | Multiple |

### Setting Up Pipelines

1. **Create pipeline environment** (host for pipeline configuration)
2. **Define stages** (development, test, production)
3. **Configure deployment settings** per stage
4. **Add approval gates** as required
5. **Test pipeline** with non-production solution

See [Set up pipelines](https://learn.microsoft.com/en-us/power-platform/alm/set-up-pipelines) for configuration details.

---

## Part 4: Access Pipelines from Power Apps

Makers access pipelines from Power Apps:

1. Open [Power Apps](https://make.powerapps.com)
2. Navigate to **Solutions**
3. Select **Pipelines** from toolbar
4. Create pipeline, add stages, manage deployments

**Toolbar options:** Create pipeline, Edit pipeline, Add stage, Delete pipeline, Refresh, Manage pipelines, View deployments

See [Admin deployment hub](https://learn.microsoft.com/en-us/power-platform/alm/admin-deployment-hub) for details.

---

## Part 5: Run Pipeline Deployments

### Running Pipelines

1. Open agent solution in source environment
2. Select **Deploy** from solution menu
3. Choose target stage
4. Wait for approvals (if configured)
5. Monitor deployment progress
6. Validate in target environment

See [Run pipelines](https://learn.microsoft.com/en-us/power-platform/alm/run-pipeline) for detailed steps.

---

## Part 6: Governance Zone Promotion Process

### Promotion Requirements

| Promotion | Requirements | Approvers | Documentation |
|-----------|--------------|-----------|---------------|
| **Zone 1 > Zone 2** | Business justification, basic testing | Manager, Environment owner | Request form, test results |
| **Zone 2 > Zone 3** | Full assessment, security review | Governance committee, Compliance, Security | Full package |
| **Within zone** | Change documentation | Environment owner | Change record |

### Zone 1 to Zone 2 Checklist

- [ ] Business justification documented
- [ ] Manager approval obtained
- [ ] Basic security review completed
- [ ] Target environment identified
- [ ] Solution exported from Zone 1
- [ ] Deployment plan created
- [ ] Rollback plan defined

### Zone 2 to Zone 3 Checklist

- [ ] All Zone 1 > Zone 2 requirements
- [ ] Governance committee approval
- [ ] Full security assessment
- [ ] Compliance review completed
- [ ] Performance testing passed
- [ ] User acceptance testing completed
- [ ] Production readiness checklist
- [ ] Monitoring plan defined
- [ ] Support procedures documented

---

## Part 7: Change Classification and Approval Matrix

### Change Classification

| Change Type | Examples | Risk Level | Approval |
|-------------|----------|------------|----------|
| **Emergency** | Security fix, critical bug | High | Expedited |
| **Major** | New functionality, architecture change | High | CAB |
| **Standard** | Enhancements, non-critical fixes | Medium | Manager |
| **Minor** | Documentation, cosmetic changes | Low | Self-service |

### Approval Matrix by Governance Zone

| Change Type | Zone 1 | Zone 2 | Zone 3 |
|-------------|--------|--------|--------|
| Emergency | Self-service | Manager + Security | CAB + CISO |
| Major | Self-service | Manager + Security | CAB |
| Standard | Self-service | Manager | Manager + Security |
| Minor | Self-service | Self-service | Manager |

---

## Validation

After completing the configuration, verify:

1. [ ] Pipeline environments created and accessible
2. [ ] Pipeline stages defined (Dev > Test > Prod for Zone 3)
3. [ ] Approval gates configured for each stage requiring review
4. [ ] Target environments enabled as Managed Environments
5. [ ] Test deployment completes successfully through all stages
6. [ ] Approval notifications delivered to designated approvers
7. [ ] Deployment history visible in PPAC

**Expected Result:** Solutions deploy through governed pipelines with appropriate approval gates, and all deployment activity is logged for audit purposes.

---

---

[Back to Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
