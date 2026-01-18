# Verification & Testing: Control 2.12 - Supervision and Oversight

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify WSP Addendum

1. Request WSP addendum for AI agents
2. Verify coverage of supervision requirements
3. **EXPECTED:** Documented procedures with approvals

### Test 2: Test HITL Configuration

1. Trigger high-risk agent response
2. Verify review prompt appears
3. **EXPECTED:** Supervisor review required before sending

### Test 3: Test Review Queue

1. Submit flagged response
2. Check review queue in SharePoint
3. Complete review and decision
4. **EXPECTED:** End-to-end workflow functional

### Test 4: Verify Supervision Evidence

1. Request recent supervision log
2. Verify reviewer decisions are documented
3. **EXPECTED:** Complete audit trail

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.12-01 | WSP addendum exists | Documented and approved | |
| TC-2.12-02 | HITL triggers | Review required | |
| TC-2.12-03 | Review queue functions | Workflow completes | |
| TC-2.12-04 | Supervision logged | Decisions documented | |
| TC-2.12-05 | Principal qualified | Appropriate registrations | |

---

## Evidence Collection Checklist

- [ ] Document: WSP addendum
- [ ] Screenshot: HITL configuration in Copilot Studio
- [ ] Screenshot: Review queue in SharePoint
- [ ] Export: Supervision log (CSV)
- [ ] Document: Designated principal qualifications

---

## Attestation Statement Template

```markdown
## Control 2.12 Attestation - Supervision and Oversight

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. WSP addendum for AI agents is documented and approved
2. HITL is configured for Zone 3 agents:
   - Investment recommendations: [Review required]
   - Account-specific advice: [Review required]
3. Sampling protocol is implemented:
   - Zone 1: [X%]
   - Zone 2: [X%]
   - Zone 3: [X%]
4. Designated principals are qualified:
   - [Name]: Series 24
5. Supervision evidence is retained per FINRA 4511

**Reviews This Period:** [Count]
**Approval Rate:** [X%]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
