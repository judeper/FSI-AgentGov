# Control 3.8: Copilot Hub and Governance Dashboard - Verification & Testing

> This playbook provides verification and testing procedures for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md).

---

## Verification Steps

### 1. M365 Admin Center Access

- Navigate to Copilot section
- Verify all five navigation items accessible
- Confirm Settings tabs load correctly

### 2. Agents Section Access

- Navigate to Agents section
- Verify Overview metrics display
- Confirm Registry shows all agents

### 3. PPAC Copilot Access

- Navigate to PPAC Copilot section
- Verify Settings page loads
- Confirm Copilot Studio dashboard accessible

### 4. Settings Configuration

- Verify FSI-recommended settings applied
- Confirm web search disabled
- Check external AI providers blocked

---

## Compliance Checklist

| Item | Required For | Status |
|------|--------------|--------|
| Copilot settings documented | Audit evidence | |
| Web search disabled | FINRA 4511 compliance | |
| External AI providers blocked | Data governance | |
| Agent approval workflow configured | Risk management | |
| Usage reports exported monthly | FINRA 4511 | |
| MCP Servers reviewed | Security | |

---

## Test Cases

### Test Case 1: Settings Application

**Objective:** Verify settings changes take effect

**Steps:**

1. Disable web search in Copilot Settings
2. Test Copilot chat prompt requiring web
3. Verify web search not used

**Expected Result:** Copilot respects disabled web search

### Test Case 2: Agent Approval Workflow

**Objective:** Verify agents require approval

**Steps:**

1. Configure agent approval requirement
2. Publish test agent
3. Verify agent appears in Requests tab
4. Approve agent
5. Verify agent available

**Expected Result:** Agents require approval before availability

### Test Case 3: MCP Server Blocking

**Objective:** Verify blocked servers are inaccessible

**Steps:**

1. Block a test MCP Server
2. Attempt to use blocked capability
3. Verify capability unavailable

**Expected Result:** Blocked servers cannot be used

---

## Evidence Collection

For audits, collect:

- Copilot settings configuration export
- Agent registry export
- Usage reports (monthly)
- Audit log of configuration changes
- MCP Server availability list

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
