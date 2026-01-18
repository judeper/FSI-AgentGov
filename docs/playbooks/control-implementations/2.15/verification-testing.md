# Verification & Testing: Control 2.15 - Environment Routing and Auto-Provisioning

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Environment Group Configuration

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments** > **Environment groups**
3. Open each group and verify membership
4. **EXPECTED:** Groups contain correct environments per governance design

### Test 2: Verify Routing Rules

1. In each environment group, select **Rules**
2. Review each rule's conditions and target
3. Verify rule priorities are correct
4. **EXPECTED:** Rules target appropriate environments with correct conditions

### Test 3: Test Routing - Security Group Rule

1. Sign in as a user in a security group with a routing rule
2. Navigate to [Power Apps](https://make.powerapps.com)
3. Click **+ Create** to start a new app
4. Check which environment is selected by default
5. **EXPECTED:** User is routed to environment specified in rule

### Test 4: Test Routing - No Rule Match

1. Sign in as a user NOT matching any routing rules
2. Navigate to Power Apps or Copilot Studio
3. Check which environment is selected by default
4. **EXPECTED:** User is routed to default/fallback environment

### Test 5: Verify Routing Documentation

1. Review routing rule documentation
2. Compare documented rules to configured rules
3. **EXPECTED:** Documentation matches actual configuration

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.15-01 | Environment groups contain correct environments | Membership correct | |
| TC-2.15-02 | Security group rule routes correctly | User sees target env | |
| TC-2.15-03 | Domain rule routes correctly | User sees target env | |
| TC-2.15-04 | Rule priority respected | Higher priority wins | |
| TC-2.15-05 | No-match user gets default env | Default env selected | |
| TC-2.15-06 | Documentation matches config | All rules documented | |
| TC-2.15-07 | Rule change requires approval (Zone 3) | Change blocked without approval | |

---

## Evidence Collection Checklist

### Environment Group Configuration

- [ ] Screenshot: PPAC > Environment groups list
- [ ] Screenshot: Each group's environment membership
- [ ] Screenshot: Each group's routing rules
- [ ] Export: Environment configuration JSON

### Routing Rules

- [ ] Screenshot: Routing rules with conditions and priorities
- [ ] Document: Rule-to-target mapping table
- [ ] Screenshot: Default environment configuration

### Testing Evidence

- [ ] Screenshot: Test user routed to correct environment
- [ ] Screenshot: No-match user routed to default
- [ ] Document: Test case results table

---

## Evidence Artifact Naming Convention

```
Control-2.15_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-2.15_EnvGroups_20260115.png
- Control-2.15_RoutingRules_20260115.png
- Control-2.15_TestResults_20260115.xlsx
- Control-2.15_EnvConfig_20260115.json
```

---

## Attestation Statement Template

```markdown
## Control 2.15 Attestation - Environment Routing

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Environment groups are configured per governance design
2. Routing rules direct users to appropriate environments
3. Rule priorities are correctly ordered
4. Default environment fallback is appropriately governed
5. Routing changes follow change control process
6. Configuration documentation is current and accurate

**Environment Groups Configured:** [Number]
**Routing Rules Active:** [Number]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
