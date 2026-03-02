# Verification & Testing: Control 1.18 - Application-Level Authorization and RBAC

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Viewer Role Restrictions

1. Log in as user with FSI - Agent Viewer role
2. Navigate to Copilot Studio
3. Attempt to create new agent
4. **EXPECTED:** Create option disabled or error on attempt

### Test 2: Verify PIM Activation Required

1. Log in as Power Platform Admin (without PIM activation)
2. Attempt admin action (e.g., modify environment)
3. **EXPECTED:** Access denied until PIM role activated

### Test 3: Verify Column-Level Security

1. Log in as user without sensitive field access
2. Open record with sensitive fields (SSN, Account Balance)
3. **EXPECTED:** Sensitive fields hidden or show asterisks

### Test 4: Verify Access Review Process

1. Navigate to Entra > Access Reviews
2. Locate review for security group
3. **EXPECTED:** Review scheduled and reviewers assigned

### Test 5: Export Role Assignments

1. Run Export-SecurityRoles.ps1 script
2. Review exported data
3. **EXPECTED:** All assignments documented with no orphaned accounts

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.18-01 | Viewer cannot create agent | Action blocked | |
| TC-1.18-02 | Admin requires PIM | Must activate role | |
| TC-1.18-03 | Sensitive fields hidden | Field security enforced | |
| TC-1.18-04 | Service principal rotation | Credentials rotated | |
| TC-1.18-05 | Access review scheduled | Review active | |
| TC-1.18-06 | Role assignment export | Complete export | |

---

## Evidence Collection Checklist

- [ ] Export: Security role assignments (CSV)
- [ ] Screenshot: Custom security role configuration
- [ ] Screenshot: PIM settings for admin roles
- [ ] Screenshot: Access review configuration
- [ ] Document: Role-to-group mapping

---

## Attestation Statement Template

```markdown
## Control 1.18 Attestation - RBAC

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Custom security roles are implemented with least-privilege access
2. Role assignments are made to security groups (not individuals)
3. PIM is configured for privileged roles:
   - Max activation: [Duration]
   - Approval required: [Yes/No]
4. Access reviews are scheduled:
   - Zone 1: [Annual]
   - Zone 2: [Semi-annual]
   - Zone 3: [Quarterly]
5. Column-level security protects sensitive fields

**Last Access Review:** [Date]
**Next Access Review:** [Date]

**Signature:** _______________________
**Date:** _______________________
```

---

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|-------------------|-----------------|-------------|----------|
| SSPM-1.18-01 | Agent action consent | Enabled for all published agents | PPAC > Environments > Settings > Features | Screenshot |
| SSPM-1.18-02 | Connected agents | Disabled or restricted to approved list | PPAC > Environments > Settings > Features | Screenshot |
| SSPM-1.18-03 | Admin count | < 10 environment-level admins per environment | PPAC > Environments > Settings > Users + permissions > Security roles | Screenshot |
| SSPM-1.18-04 | RPA admin roles | RPA/service accounts not assigned admin roles | PPAC > Environments > Settings > Users + permissions > Security roles | Screenshot |

### Test Procedures

**SSPM-1.18-01: Agent Action Consent**

1. Navigate to **PPAC** > **Environments** > select environment > **Settings** > **Features**
2. Locate "Agent action consent" setting
3. Verify the setting is **Enabled** for all published agents
4. **Pass criteria:** Agent action consent is enabled, requiring user consent before agent actions execute
5. **Evidence:** Screenshot showing Features page with agent action consent toggle

**SSPM-1.18-02: Connected Agents**

1. Navigate to **PPAC** > **Environments** > select environment > **Settings** > **Features**
2. Locate "Connected agents" setting
3. Verify the setting is **Disabled** or restricted to an approved list of agents
4. **Pass criteria:** Connected agents are disabled or limited to organization-approved agents only
5. **Evidence:** Screenshot showing Features page with connected agents configuration

**SSPM-1.18-03: Admin Count**

1. Navigate to **PPAC** > **Environments** > select environment > **Settings** > **Users + permissions** > **Security roles**
2. Open the "System Administrator" role
3. Count the number of users assigned to the role
4. **Pass criteria:** Fewer than 10 environment-level admins per environment
5. **Evidence:** Screenshot showing security role membership with user count

**SSPM-1.18-04: RPA Admin Roles**

1. Navigate to **PPAC** > **Environments** > select environment > **Settings** > **Users + permissions** > **Security roles**
2. Review the "System Administrator" and "Environment Admin" roles
3. Verify no RPA or service accounts are assigned admin-level roles
4. **Pass criteria:** All admin role members are named individuals — no service principals or RPA accounts
5. **Evidence:** Screenshot showing admin role assignments with account types identified

---

*Updated: February 2026 | Version: v1.2 | Classification: Verification Testing*

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
