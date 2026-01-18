# Control 1.4: Advanced Connector Policies (ACP) - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md).

---

## Verification Steps

Use the steps below to generate audit-ready evidence that ACP + DLP boundaries are active and effective.

### 1. Confirm Prerequisites (Dependencies 2.1 and 2.2)

- Power Platform Admin Center > **Manage** > **Environments**: verify environment shows **Managed Environment** enabled
- Power Platform Admin Center > **Manage** > **Environment Groups**: verify environment is in the intended group

### 2. Test Blocked Connector (Denylist Enforcement)

1. In Copilot Studio, create or open an agent in a regulated environment
2. Attempt to add a tool/flow that uses a blocked connector (e.g., social media)
3. **Expected**: Connector is unavailable or connection creation is blocked with an administrator policy message

### 3. Test Action-Level Restriction

1. Pick an allowed connector with restricted actions (e.g., SharePoint or Dataverse)
2. Attempt to use a disallowed action (e.g., delete/update)
3. **Expected**: Action is blocked or prevented, depending on the ACP feature behavior for that connector

### 4. Validate DLP Boundaries (Data Crossing Prevention)

1. Attempt to build a flow that combines a Business connector with a Non-Business/Blocked connector
2. **Expected**: The platform prevents cross-group data movement and displays a DLP policy error

### 5. Review Connector/Connection Inventory

1. Power Platform Admin Center > **Data** > **Connections**
2. Verify connections in regulated environments align with the allowlist and do not include prohibited connectors

### 6. Audit Policy and Configuration Changes

1. Microsoft Purview portal > **Audit** > **Search**
2. Search for Power Platform administration activities related to environment groups, DLP policies, and connector policy changes
3. **Expected**: Changes are attributable to named admin identities and include timestamps

---

## Expected Results Summary

| Test | Expected Outcome |
|------|------------------|
| Blocked connector test | Connector unavailable; admin policy message displayed |
| Action-level restriction test | Disallowed action blocked at runtime |
| DLP boundary test | Cross-group data flow prevented with policy error |
| Connection inventory review | Only allowlisted connectors present in regulated environments |
| Audit log review | All policy changes logged with admin identity and timestamp |

---

## Evidence Artifacts

Capture the following evidence artifacts for each regulated environment group:

### 1. Environment Group Evidence

- Screenshot: Environment group details showing the environment list and tier/classification
- Screenshot: **Rules** tab showing **Advanced connector policies** with **Published** status

### 2. ACP Allow/Deny Configuration Evidence

- Screenshot: Connector list in ACP (allowlist/denylist state)
- Screenshot(s): Connector action restrictions (where available) for at least one high-risk connector scenario

### 3. DLP Boundary Evidence

- Screenshot: DLP policy connector grouping (Business/Non-Business/Blocked)
- Screenshot: DLP policy scope (environments included)

### 4. Enforcement Evidence

- Screenshot: Blocked connector attempt in a regulated environment (error banner/message)
- Screenshot: Blocked cross-boundary (DLP) flow build attempt (policy violation message)

### 5. Audit Evidence

- Export: Purview audit results for the policy change window (include query parameters and time range)

### 6. Change Control Evidence

- Ticket/record: Connector approval request, vendor review decision, and implementation date

---

## Confirmation Checklist

Use this checklist to confirm control effectiveness:

- [ ] Environment is enabled as Managed Environment
- [ ] Environment is member of appropriate Environment Group
- [ ] ACP is configured with FSI-approved allowlist
- [ ] Blocked connectors are inaccessible to makers
- [ ] Action-level restrictions are enforced
- [ ] DLP boundaries prevent cross-group data flow
- [ ] All connector/policy changes appear in audit logs
- [ ] Evidence artifacts collected and stored

---

*Updated: January 2026 | Version: v1.1*
