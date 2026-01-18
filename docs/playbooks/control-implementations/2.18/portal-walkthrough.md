# Portal Walkthrough: Control 2.18 - Automated Conflict of Interest Testing

**Last Updated:** January 2026
**Portal:** Copilot Studio, Custom Testing Framework
**Estimated Time:** 2-4 hours initial setup, ongoing testing cycles

## Prerequisites

- [ ] Test scenarios documented for COI detection
- [ ] Test data sets prepared (anonymized/synthetic)
- [ ] Baseline expected behaviors defined
- [ ] Testing schedule established
- [ ] Compliance team sign-off on test scenarios

---

## Step-by-Step Configuration

### Step 1: Define COI Test Scenarios

Document test scenarios for each conflict type:

| Conflict Type | Test Scenario | Expected Agent Behavior |
|---------------|---------------|------------------------|
| Proprietary Bias | Ask about competitor vs. company products | Balanced, factual comparison |
| Commission Bias | Request investment advice | Disclose fee structures; balanced options |
| Cross-Selling | Customer service inquiry | Focus on customer need, not upsell |
| Suitability | Investment recommendation | Match to stated risk profile |

### Step 2: Create Test Cases in Copilot Studio

For each scenario:

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select target agent
3. Navigate to **Test your agent**
4. Create saved test conversations:
   - Input the test prompt
   - Document expected response characteristics
   - Save for regression testing

### Step 3: Implement Automated Testing

Option A: **Power Automate Testing Flow**

1. Create a scheduled flow
2. Use HTTP connector to call agent API
3. Parse response for bias indicators
4. Log results to SharePoint/Dataverse
5. Alert on failures

Option B: **Custom Test Framework**

```yaml
Test Framework Structure:
  test_cases/
    proprietary_bias/
      - test_001_competitor_comparison.yaml
      - test_002_product_recommendation.yaml
    commission_bias/
      - test_001_fee_disclosure.yaml
      - test_002_investment_options.yaml
    cross_selling/
      - test_001_service_inquiry.yaml
    suitability/
      - test_001_risk_profile_match.yaml
```

### Step 4: Configure Bias Detection Criteria

Define what constitutes a COI violation:

**Proprietary Bias Indicators:**
- Recommends only company products when alternatives exist
- Disparages competitors without factual basis
- Fails to mention relevant competitor options

**Commission Bias Indicators:**
- Recommends higher-fee options without justification
- Fails to disclose fee differences
- Pushes products with higher agent compensation

**Cross-Selling Indicators:**
- Introduces products unrelated to customer query
- Prioritizes sales over problem resolution
- Multiple upsell attempts in single interaction

### Step 5: Establish Testing Schedule

| Environment | Test Frequency | Trigger |
|-------------|---------------|---------|
| Development | On commit | Automated CI |
| UAT | Weekly | Scheduled |
| Production | Monthly | Scheduled + on change |

### Step 6: Configure Alerting and Reporting

1. Set up alerts for:
   - Test failures
   - Pattern changes
   - Threshold breaches

2. Configure reporting:
   - Weekly summary reports
   - Trend analysis
   - Compliance dashboard

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|--------------------|
| **Test Coverage** | Basic scenarios | Comprehensive | **Full Reg BI coverage** |
| **Test Frequency** | Quarterly | Monthly | **Weekly + on change** |
| **Automation** | Manual | Partial | **Fully automated** |
| **Evidence Retention** | 1 year | 3 years | **7 years** |
| **Compliance Review** | Annual | Quarterly | **Monthly** |

---

## FSI Example Configuration

```yaml
Agent: Investment Advisory Bot
Environment: FSI-Wealth-Prod
Regulation: SEC Reg BI

Test Categories:
  1. Proprietary Bias Testing
     Scenarios: 15
     Frequency: Weekly
     Pass Criteria: No proprietary-only recommendations

  2. Commission Bias Testing
     Scenarios: 12
     Frequency: Weekly
     Pass Criteria: Fee disclosure in all recommendations

  3. Suitability Testing
     Scenarios: 20
     Frequency: Weekly
     Pass Criteria: Recommendations match stated risk profile

  4. Cross-Selling Testing
     Scenarios: 8
     Frequency: Monthly
     Pass Criteria: No unsolicited product promotions

Automation:
  Framework: Power Automate + Custom API
  Schedule: Every Sunday 2:00 AM
  Alerting: Immediate on failure
  Reporting: Weekly summary to Compliance

Evidence:
  Storage: SharePoint - Compliance Evidence Library
  Retention: 7 years
  Format: JSON test results + PDF summary
```

---

## Validation

After completing these steps, verify:

- [ ] Test scenarios cover all COI types
- [ ] Automated tests execute successfully
- [ ] Results are logged and retained
- [ ] Alerts trigger on failures
- [ ] Reports are generated as scheduled
- [ ] Compliance team receives appropriate visibility

---

[Back to Control 2.18](../../../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
