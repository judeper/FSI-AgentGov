# Control 2.7: Vendor and Third-Party Risk Management - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md).

---

## Common Issues and Solutions

| Issue | Symptoms | Root Cause | Solution |
|-------|----------|------------|----------|
| Incomplete connector inventory | Unknown connectors discovered during audits | Limited visibility | Run PowerShell enumeration scripts |
| Missing SOC 2 report | Vendor cannot provide documentation | Vendor maturity | Accept alternatives or conduct independent assessment |
| Custom connector security | Connectors created without review | No approval process | Implement Managed Environments |
| Delayed incident notification | Vendor security incident not reported | Contract gaps | Review and update contract terms |
| DLP policy not blocking | Users can use blocked connectors | Policy misconfiguration | Verify policy scope and propagation |

---

## Detailed Troubleshooting

### Issue 1: Unable to Identify All Third-Party Connectors

**Symptoms:** Incomplete connector inventory, unknown connectors discovered during audits

**Solutions:**

1. Run PowerShell scripts to enumerate connectors across all environments
2. Review Power Platform analytics for connector usage
3. Check audit logs in Microsoft Purview for connection activity
4. Enable connector activity alerts for new deployments
5. Survey environment admins for custom connector usage

---

### Issue 2: Vendor Fails to Provide SOC 2 Report

**Symptoms:** Vendor cannot provide required security documentation

**Solutions:**

1. Accept alternative certifications (ISO 27001, FedRAMP)
2. Request bridge letter if report is pending
3. Conduct independent security assessment
4. Implement compensating controls (enhanced monitoring)
5. Escalate to vendor risk committee for risk acceptance or termination

---

### Issue 3: Custom Connector Security Concerns

**Symptoms:** Custom connectors created without security review

**Solutions:**

1. Implement pre-deployment security review process
2. Enable Managed Environments to control solution deployment
3. Use solution checker to identify security issues
4. Require code review for custom connector APIs
5. Block custom connector creation except in designated environments

---

### Issue 4: Vendor Incident Notification Delayed

**Symptoms:** Vendor security incident not reported timely

**Solutions:**

1. Review contract for notification requirements
2. Assess impact to organization and report internally
3. Document timeline of vendor notification
4. Update vendor risk score based on incident handling
5. Consider contract remediation or termination

---

### Issue 5: DLP Policies Not Blocking Connectors as Expected

**Symptoms:** Users able to use connectors that should be blocked

**Solutions:**

1. Verify DLP policy is applied to correct environments
2. Check for conflicting policies (least restrictive wins)
3. Confirm connector is correctly classified in policy
4. Wait for policy propagation (up to 1 hour)
5. Verify environment is marked as Managed

---

### Issue 6: Community Plugin Installed Without Review

**Symptoms:** Unvetted community connector discovered in environment

**Solutions:**

1. Disable connector immediately
2. Review usage and data exposure
3. Assess impact of any data that flowed through connector
4. Document incident and root cause
5. Strengthen preventive controls (DLP, marketplace blocking)

---

### Issue 7: AI Vendor Model Change Without Notice

**Symptoms:** Agent behavior changed unexpectedly due to underlying model update

**Solutions:**

1. Document behavioral changes observed
2. Contact vendor for model change information
3. Compare performance against baseline
4. Revalidate agent per MRM requirements if material
5. Update contract to strengthen notification requirements

---

## Escalation Path

If issues cannot be resolved using this guide:

1. **Level 1:** Power Platform Admin - Technical configuration
2. **Level 2:** AI Governance Lead - Policy and process
3. **Level 3:** Compliance Officer - Regulatory requirements
4. **Level 4:** Vendor Risk Committee - Risk acceptance decisions

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Assessment procedures

---

*Updated: January 2026 | Version: v1.1*
