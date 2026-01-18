# Control 1.6: Microsoft Purview DSPM for AI - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to purview.microsoft.com > DSPM for AI | Dashboard displayed |
| 2 | Check Get Started completion | All steps show completed |
| 3 | Review Recommendations | Actions tracked with status |
| 4 | Access Reports | Interaction data visible |
| 5 | Check Policies | Required policies enabled |
| 6 | Open Activity explorer | AI interactions logged |
| 7 | Review Data risk assessments | Assessment capability available |

---

## Get Started Verification

### Step 1: Audit Activation

- [ ] DSPM Get started shows Step 1 completed
- [ ] Purview Audit page indicates logging is enabled
- [ ] Recent audit events are present

### Steps 2-4: Extended Visibility

- [ ] Browser extension deployed (if applicable)
- [ ] Devices onboarded (if applicable)
- [ ] Extended insights enabled (if applicable)

---

## Reports Verification

1. Navigate to **DSPM for AI > Reports**
2. Verify data is populating:
   - Total interactions trend chart shows data
   - Sensitive interactions per AI app shows breakdown
   - User interaction metrics are visible

---

## Activity Explorer Verification

1. Navigate to **DSPM for AI > Activity explorer**
2. Apply filters:
   - Date range: Last 7 days
   - AI app category: Copilot experiences & agents
3. Verify:
   - AI interaction events are logged
   - User information is captured
   - Sensitive info types are detected (if applicable)
4. Test export function

---

## Data Risk Assessment Verification

1. Navigate to **DSPM for AI > Data risk assessments**
2. Verify default assessment runs successfully
3. Review results for:
   - Overshared items count
   - Severity levels
   - Affected sites/users

---

## Evidence Artifacts to Retain

### DSPM Setup Evidence

- [ ] Screenshot: DSPM Get started with all steps completed
- [ ] Screenshot: Purview Audit enabled
- [ ] Export: Sample audit results

### Reports Evidence

- [ ] Screenshot: Reports page with filters visible
- [ ] Screenshot: Total interactions trend
- [ ] Screenshot: Sensitive interactions summary

### Activity Explorer Evidence

- [ ] Export: Activity explorer CSV
- [ ] Screenshot: Filters showing scoping

### Oversharing Assessment Evidence

- [ ] Screenshot: Assessment list with status and completion time
- [ ] Screenshot: Results summary showing overshared items count
- [ ] Change evidence: Remediation tickets

### Policy Evidence

- [ ] Screenshot: DLP policies as displayed in DSPM Policies
- [ ] Screenshot: Policy details showing scope and mode

---

## Confirmation Checklist

- [ ] DSPM for AI is accessible
- [ ] All Get Started steps completed
- [ ] Recommendations are tracked
- [ ] Reports show AI interaction data
- [ ] Policies are configured and enabled
- [ ] Activity explorer logs AI interactions
- [ ] Data risk assessments can run
- [ ] Evidence artifacts collected and stored

---

*Updated: January 2026 | Version: v1.1*
