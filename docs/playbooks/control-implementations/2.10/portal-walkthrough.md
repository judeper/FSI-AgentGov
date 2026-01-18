# Portal Walkthrough: Control 2.10 - Patch Management and System Updates

**Last Updated:** January 2026
**Portal:** Microsoft 365 Admin Center, Azure Portal
**Estimated Time:** 2-3 hours for setup

## Prerequisites

- [ ] Microsoft 365 Admin role
- [ ] Power Platform Admin role
- [ ] Azure Service Health access (if using Azure services)

---

## Step-by-Step Configuration

### Step 1: Subscribe to Message Center

1. Open [Microsoft 365 Admin Center](https://admin.microsoft.com)
2. Navigate to **Health** > **Message center**
3. Configure preferences:
   - Email notifications for Power Platform updates
   - Email notifications for Copilot Studio updates
4. Add AI Governance Lead and Power Platform Admin to recipients

### Step 2: Configure Azure Service Health Alerts

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to **Service Health** > **Health alerts**
3. Create alert:
   - Services: Power Platform, Azure Key Vault, Application Insights
   - Event types: Service issues, Planned maintenance
   - Notification: Operations team email and SMS

### Step 3: Establish Test Environment

1. Create non-production environment in PPAC:
   - Name: `FSI-Update-Testing`
   - Type: Sandbox
   - Mirror production configuration
2. Deploy production agent copy for testing
3. Create baseline test suite

### Step 4: Define Maintenance Windows

1. Document maintenance windows by zone:
   - Zone 1: Anytime with notification
   - Zone 2: Weekends preferred, 48-hour notice
   - Zone 3: Scheduled windows only, change approval required
2. Communicate windows to stakeholders

### Step 5: Create Patch Documentation Process

1. Create SharePoint library for patch documentation
2. Create template for patch assessment:
   - Update description
   - Impact assessment
   - Test results
   - Rollback plan
   - Approval

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Auto-Updates** | Enabled | Controlled | Change-controlled |
| **Testing** | Optional | Critical updates | All updates |
| **Documentation** | Basic | Tracked | Full change control |
| **Maintenance Window** | Flexible | Defined | Strict |
| **Rollback Plan** | None | Critical updates | All updates |

---

## Validation

After completing these steps, verify:

- [ ] Message Center notifications configured
- [ ] Service Health alerts trigger correctly
- [ ] Test environment mirrors production
- [ ] Maintenance windows documented
- [ ] Patch history log maintained

---

[Back to Control 2.10](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
