# Portal Walkthrough: Control 1.22 - Information Barriers for AI Agents

**Last Updated:** January 2026
**Portal:** Microsoft Purview
**Estimated Time:** 4-6 hours

## Prerequisites

- [ ] Purview Compliance Admin role
- [ ] User attributes populated in Entra ID (Department)
- [ ] Information Barriers license (E5 or add-on)

---

## Step-by-Step Configuration

### Step 1: Define Organization Segments

1. Open [Microsoft Purview](https://compliance.microsoft.com)
2. Navigate to **Information barriers** > **Segments**
3. Create segments for each business unit:

```powershell
# Example segment definitions
New-OrganizationSegment -Name "IB-Research" -UserGroupFilter "Department -eq 'Research'"
New-OrganizationSegment -Name "IB-Trading" -UserGroupFilter "Department -eq 'Trading'"
New-OrganizationSegment -Name "IB-InvestmentBanking" -UserGroupFilter "Department -eq 'Investment Banking'"
New-OrganizationSegment -Name "IB-Sales" -UserGroupFilter "Department -eq 'Sales'"
```

### Step 2: Create Barrier Policies

1. Navigate to **Policies** > **Information barriers**
2. Create policies blocking cross-segment access:

**Research-Trading Barrier:**
- Segment 1: IB-Research
- Segment 2: IB-Trading
- Action: Block

**IB-Sales Barrier:**
- Segment 1: IB-InvestmentBanking
- Segment 2: IB-Sales
- Action: Block

### Step 3: Apply Barrier Policies

1. After creating all policies, apply them:
   ```powershell
   Start-InformationBarrierPoliciesApplication
   ```
2. Wait for application to complete (can take hours)

### Step 4: Validate SharePoint Alignment

1. Verify SharePoint sites align with barriers
2. Research content not accessible to Trading
3. IB content not accessible to Sales

### Step 5: Configure Wall-Crossing Workflow

1. Create approval workflow for exceptions:
   - Compliance Officer approval
   - Legal approval
   - Business Unit head approval
2. Document wall-crossing in compliance system
3. Set expiration for temporary access

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Barriers** | User-inherited | Validated weekly | Mandatory enforcement |
| **Wall-Crossing** | Documented | Approval required | Formal process |
| **Monitoring** | Periodic audit | Weekly audit | Real-time |
| **Retention** | 1 year | 6 years | 6+ years |

---

## Validation

After completing these steps, verify:

- [ ] Segments defined for all business units
- [ ] Barrier policies show Active status
- [ ] Research user cannot access Trading content
- [ ] Wall-crossing workflow functional

---

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
