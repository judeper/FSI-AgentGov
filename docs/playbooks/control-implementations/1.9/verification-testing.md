# Control 1.9: Data Retention and Deletion Policies - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Confirm labels created | All FSI agent labels listed in Purview |
| 2 | Verify policy distribution | Policies show "Success" status |
| 3 | Test label application | Label appears in document properties |
| 4 | Test retention hold | Deletion blocked during retention |
| 5 | Validate disposition workflow | Items appear in disposition review |
| 6 | Verify legal hold | Content protected from deletion |

---

## Test Cases

### Test 1: Retention Label Application

1. Navigate to a SharePoint document library
2. Select a test document
3. Apply the FSI-AgentConversations-7Year label
4. **Expected:** Label appears in document properties with retention info

### Test 2: Retention Hold Verification

1. Apply retention label to test content
2. Attempt to delete the labeled content
3. **Expected:** Deletion blocked with retention message

### Test 3: Disposition Review Workflow

1. Create test item with short retention (use test label)
2. Wait for retention period to expire
3. **Expected:** Item appears in disposition review queue
4. Complete disposition review
5. **Expected:** Item deleted or extended per review decision

### Test 4: Legal Hold Override

1. Place legal hold on test content
2. Apply retention label that would delete content
3. **Expected:** Content retained due to legal hold
4. Release legal hold
5. **Expected:** Normal retention behavior resumes

### Test 5: Policy Distribution

1. Create new retention policy
2. Monitor distribution status
3. **Expected:** Policy shows "Success" within 24-48 hours

---

## Evidence Artifacts

- [ ] Screenshot: Retention labels with settings
- [ ] Screenshot: Retention policies with locations
- [ ] Export: Policy distribution status
- [ ] Documentation: Retention schedule mapping to regulations
- [ ] Screenshot: Disposition review configuration
- [ ] Audit log: Deletion prevention test
- [ ] Documentation: Legal hold procedures
- [ ] Export: Compliance summary report

---

## Zone-Specific Testing

### Zone 1 (Personal Productivity)

- Conversation retention: 1 year minimum
- Configuration retention: 6 months
- Disposition: Automatic deletion

### Zone 2 (Team Collaboration)

- Conversation retention: 3 years
- Configuration retention: 3 years
- Disposition: Manager review required

### Zone 3 (Enterprise Managed)

- Conversation retention: 7 years
- Configuration retention: 6 years
- Audit logs: 10 years
- Disposition: Compliance review required
- SEC 17a-4: WORM or audit-trail alternative for broker-dealer records

---

## Regulatory Retention Requirements

| Regulation | Minimum Retention | Applies To |
|------------|-------------------|------------|
| FINRA 4511 | 6 years | Books and records, communications |
| SEC 17a-3/4 | 6-7 years | Trade records, communications |
| SOX 404 | 7 years | Financial audit documentation |
| GLBA 501(b) | Per company policy | Customer financial information |

---

## Confirmation Checklist

- [ ] All FSI retention labels created
- [ ] Labels published to required locations
- [ ] Retention policies active and distributed
- [ ] Disposition reviewers configured
- [ ] Legal hold procedures documented
- [ ] Audit log retention extended
- [ ] Zone-specific retention applied
- [ ] Evidence artifacts collected

---

*Updated: January 2026 | Version: v1.2*
