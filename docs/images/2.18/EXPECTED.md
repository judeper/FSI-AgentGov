# Control 2.18: Automated Conflict of Interest Testing - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Copilot Studio Evaluation Framework
**Portal Path:** Microsoft Copilot Studio → Agents → [Agent] → Analytics → Evaluation
**What to capture:**
- Evaluation run results showing classification grading
- Test scenario categories (proprietary bias, commission bias, suitability)
- Quality assessment scores and pass/fail indicators

### Screenshot 2: COI Test Scenario Configuration
**What to capture:**
- Defined conflict-of-interest test scenarios (proprietary bias, commission bias, cross-selling)
- Test datasets with comparable proprietary vs. competitor products
- Bias threshold definitions (e.g., proprietary recommendations vs. market share)

### Screenshot 3: Pre-Deployment Pipeline Integration
**What to capture:**
- Automated conflict testing stage in CI/CD deployment pipeline
- Test execution results showing pass/fail for each COI scenario
- Gate enforcement preventing deployment with failing COI tests

### Screenshot 4: System Prompt Audit Results
**What to capture:**
- System prompt review output showing absence of prohibited bias language
- Audit checklist for prompt bias indicators
- Documentation of prompt review date and reviewer

### Screenshot 5: Conflict Testing Report
**What to capture:**
- Statistical analysis report with proprietary recommendation rates
- Comparison against expected distribution (market share baseline)
- Recommendation breakdown by product type with bias indicators

---

## Notes for Verification
- This control is primarily process-based; screenshots demonstrate testing methodology and results
- Capture from pre-production environment when possible
- Ensure product names and financial data are representative but not sensitive
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
