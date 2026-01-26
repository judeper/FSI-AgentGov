# Control 1.4: Advanced Connector Policies (ACP) - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md).

---

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| "Advanced Connector Policies option not visible" | Environment is not a Managed Environment | Enable Managed Environments first (see Control 2.1) |
| "Environment not in a group" | Must create environment group first | Create environment group and add environment |
| "Policy not applying to existing connections" | Existing connections may persist even after policy changes | Perform an immediate connection inventory; remove non-compliant connections via **Data** > **Connections** and require re-creation under policy; document remediation |
| "Users report legitimate connectors are blocked" | Connector not in allowlist | Submit connector request through change management; security team approval required |
| "Cannot publish rules" | Insufficient permissions | Verify Power Platform Administrator role in Entra ID |
| "Connector is allowed but flow fails with policy error" | DLP boundary blocks cross-connector data movement | Review DLP grouping (Business/Non-Business/Blocked) and ensure the intended connector combination is permitted; prefer redesign over loosening policy |
| "Third-party connector cannot meet US-only requirements" | Service processes/stores data outside US | Block connector for regulated environments; document vendor decision and use an approved internal integration instead |

---

## How to Confirm Configuration is Active

### Via Portal

1. Power Platform Admin Center > **Manage** > **Environment Groups**
2. Select your FSI group > **Rules** tab
3. Confirm "Advanced connector policies" shows green checkmark
4. Confirm "Published" status appears

### Via User Testing

1. As a maker in the environment, create a new cloud flow
2. Attempt to add a blocked connector
3. **Expected result**: "This connector is blocked by your administrator" message

### Via DLP Validation

1. Create a cloud flow that attempts to move data between a Business connector and a Non-Business/Blocked connector
2. **Expected result**: DLP policy violation message and prevention of save/run

### Via Audit Log

1. Microsoft Purview portal > **Audit** > **Search**
2. Filter: Activity = "Blocked connector usage attempt"
3. Confirm blocked attempts are logged (tests your monitoring)

---

## Escalation Path

If issues persist after troubleshooting:

1. **First tier**: Power Platform Admin - verify environment configuration
2. **Second tier**: AI Governance Lead - review policy design
3. **Third tier**: Microsoft Support - platform-level issues

---

## Preventive Measures

To avoid common issues:

- Maintain documented connector catalog with owner, review cadence, and change control
- Perform quarterly connector usage reviews via Power Platform audit logs
- Annual recertification of approved connectors by security team
- Incident response plan for unauthorized connector usage detection

---

*Updated: January 2026 | Version: v1.2*
