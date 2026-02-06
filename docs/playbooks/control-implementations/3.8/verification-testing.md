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

### Test Case FAC-01: Admin Exclusion Group Correctly Removes Copilot Access

**Objective:** Verify Admin Exclusion Group correctly removes Microsoft 365 Copilot access for excluded users

**Prerequisites:**
- Admin Exclusion Group created with name `CopilotForM365AdminExclude`
- Test user has M365 Copilot license assigned
- Test user is NOT currently in Admin Exclusion Group

**Steps:**

1. **Baseline verification:**
   - Sign in as test user
   - Navigate to Microsoft Teams or Outlook
   - Verify Copilot Chat is accessible and functional
   - Document current access state

2. **Add user to Admin Exclusion Group:**
   - As administrator, navigate to Microsoft Entra admin center > Groups
   - Open `CopilotForM365AdminExclude` group
   - Add test user to group membership
   - Document timestamp of addition

3. **Wait for propagation:**
   - Wait 24 hours for group membership change to propagate
   - Note: Propagation can take up to 24 hours per Microsoft documentation

4. **Verify exclusion:**
   - Sign in as test user (force new authentication session)
   - Navigate to Microsoft Teams > Copilot Chat
   - Attempt to access Copilot features
   - Document behavior (access denied, features not visible, error message)

5. **Verify license assignment unchanged:**
   - As administrator, verify test user still has M365 Copilot license assigned
   - Confirm exclusion is behavioral (group-based), not license-based

6. **Remove from exclusion group and verify restoration:**
   - Remove test user from Admin Exclusion Group
   - Wait 24 hours for propagation
   - Sign in as test user and verify Copilot access restored

**Expected Result:**
- User in Admin Exclusion Group cannot access Copilot features despite having valid license
- Copilot Chat not visible in Teams/Outlook, or displays "not available" message
- After removal from group (and propagation), access is restored

**Evidence to Collect:**
- Screenshot of test user with Copilot access before exclusion
- Screenshot of Admin Exclusion Group membership showing test user
- Screenshot of test user without Copilot access after exclusion
- Entra ID audit log entry showing group membership change
- Timestamp documentation for 24-hour propagation verification

**Regulatory Mapping:** FINRA 3110 (supervisory restrictions), SOX 404 (IT access controls)

---

### Test Case FAC-02: Deployment Group Limits Copilot Availability to Specified User Population

**Objective:** Verify Deployment Group correctly limits Copilot availability to users in approved deployment phase

**Prerequisites:**
- Deployment group created (e.g., `Copilot-Pilot-IT-Compliance`)
- Two test users with M365 Copilot licenses:
  - Test User A: Member of deployment group
  - Test User B: NOT member of deployment group (but has license)

**Steps:**

1. **Create deployment group:**
   - As administrator, create deployment group in M365 Admin Center > Copilot > Settings
   - Add Test User A to deployment group
   - Verify Test User B is NOT in deployment group
   - Document group configuration

2. **Configure Copilot for deployment group only:**
   - In M365 Admin Center, configure Copilot to be available only to deployment group members
   - Save settings and document timestamp

3. **Wait for propagation:**
   - Wait 8 hours for settings to propagate across tenant

4. **Test User A (in deployment group):**
   - Sign in as Test User A
   - Navigate to Teams > Copilot Chat
   - Verify Copilot features are accessible and functional
   - Document successful access

5. **Test User B (NOT in deployment group):**
   - Sign in as Test User B
   - Navigate to Teams > Copilot Chat
   - Verify Copilot features are NOT accessible
   - Document denial behavior (features hidden, error message, etc.)

6. **Verify license assignments:**
   - Confirm both Test User A and Test User B have identical M365 Copilot license assignments
   - Verify difference in access is deployment group membership, not licensing

**Expected Result:**
- Test User A (in deployment group): Copilot access granted
- Test User B (not in deployment group): Copilot access denied despite valid license
- Deployment group configuration enforces phased rollout control

**Evidence to Collect:**
- Deployment group membership list showing Test User A included, Test User B excluded
- Screenshot of Test User A successfully accessing Copilot
- Screenshot of Test User B denied access to Copilot
- License assignment report showing both users have M365 Copilot licenses
- M365 Admin Center settings showing deployment group configuration

**Regulatory Mapping:** SEC (controlled change management), SOX 404 (documented IT controls)

---

### Test Case FAC-03: Web Search Disabled Users Cannot Access Web-Grounded Copilot Responses

**Objective:** Verify web search control prevents Copilot from accessing external web data when disabled

**Prerequisites:**
- M365 Admin Center access to Copilot > Settings > Data access
- Test user with M365 Copilot access
- Web search control set to "Enabled" initially (baseline)

**Steps:**

1. **Baseline test with web search enabled:**
   - As administrator, verify web search is enabled (M365 Admin > Copilot > Settings > Data access)
   - Sign in as test user
   - In Copilot Chat, ask a question that requires external web data (e.g., "What are the latest news headlines today?")
   - Document Copilot response — should include web-grounded content or indicate web search used
   - Sign out

2. **Disable web search:**
   - As administrator, navigate to M365 Admin Center > Copilot > Settings > Data access
   - Set "Web search for M365 Copilot" to "Disabled"
   - Save settings and document timestamp

3. **Wait for propagation:**
   - Wait 8 hours for setting to propagate across tenant
   - Note: Microsoft documentation indicates up to 8 hours for Copilot settings propagation

4. **Test with web search disabled:**
   - Sign in as test user (force new session)
   - In Copilot Chat, ask the same question requiring external web data
   - Document Copilot response — should indicate web search not available, or limit response to organizational data only
   - Verify no web-grounded content in response

5. **Verify organizational data still accessible:**
   - Ask Copilot a question that can be answered from organizational data (e.g., "Summarize my recent emails")
   - Verify Copilot can still access and respond using organizational Microsoft 365 data
   - Confirm only web search is disabled, not all Copilot functionality

**Expected Result:**
- With web search enabled: Copilot provides web-grounded responses
- With web search disabled: Copilot does NOT access external web data, limits responses to organizational data
- Organizational data access remains functional when web search disabled

**Evidence to Collect:**
- Screenshot of M365 Admin Center showing web search enabled (baseline)
- Screenshot of Copilot response with web-grounded content (baseline)
- Screenshot of M365 Admin Center showing web search disabled
- Screenshot of Copilot response WITHOUT web content (web search disabled)
- Screenshot of Copilot successfully using organizational data (web search disabled)
- Timestamp documentation for 8-hour propagation verification

**Regulatory Mapping:** GLBA 501(b) (prevent external data leakage), FINRA (MNPI protection)

---

### Test Case 1: Admin Exclusion Group Access Control (Legacy)

**Objective:** Verify users in Admin Exclusion Group cannot access Copilot

**Steps:**

1. Create Admin Exclusion Group in M365 Admin
2. Add test user to Admin Exclusion Group
3. Wait for propagation (up to 8 hours)
4. Sign in as test user
5. Attempt to access Copilot Chat in Teams/Outlook

**Expected Result:** Access denied or Copilot features not visible

### Test Case 2: Deployment Group Restrictions

**Objective:** Verify users outside deployment group cannot access Copilot

**Steps:**

1. Create deployment group with specific users
2. Assign Copilot to deployment group only
3. Wait for propagation (up to 8 hours)
4. Test with user inside deployment group
5. Test with user outside deployment group

**Expected Result:** Feature available only to users in deployment group

### Test Case 3: Web Search Control Disabled

**Objective:** Verify Copilot responses use only organizational data when web search disabled

**Steps:**

1. Disable web search in Copilot Settings (Data Access tab)
2. Wait for propagation (up to 8 hours)
3. Test Copilot chat prompt requiring web search
4. Verify web search not used in response

**Expected Result:** Copilot respects disabled web search setting

### Test Case 4: Agent Access Restrictions

**Objective:** Verify restricted agent access prevents third-party agent discovery

**Steps:**

1. Configure agent access to organizational agents only
2. Wait for propagation
3. Attempt to discover third-party agents
4. Verify only organizational agents available

**Expected Result:** Third-party agents not discoverable

### Test Case 5: AI Administrator Role Permissions

**Objective:** Verify AI Administrator can configure Copilot settings without Global Admin

**Steps:**

1. Assign AI Administrator role to test user
2. Sign in as AI Administrator
3. Navigate to M365 Admin > Copilot > Settings
4. Modify Copilot settings (User Access, Data Access, Actions)
5. Verify settings changes applied successfully

**Expected Result:** Settings changes applied successfully without Global Admin

### Test Case 6: Settings Application (Legacy)

**Objective:** Verify settings changes take effect

**Steps:**

1. Disable web search in Copilot Settings
2. Test Copilot chat prompt requiring web
3. Verify web search not used

**Expected Result:** Copilot respects disabled web search

### Test Case 7: Agent Approval Workflow

**Objective:** Verify agents require approval

**Steps:**

1. Configure agent approval requirement
2. Publish test agent
3. Verify agent appears in Requests tab
4. Approve agent
5. Verify agent available

**Expected Result:** Agents require approval before availability

### Test Case 8: MCP Server Blocking

**Objective:** Verify blocked servers are inaccessible

**Steps:**

1. Block a test MCP Server
2. Attempt to use blocked capability
3. Verify capability unavailable

**Expected Result:** Blocked servers cannot be used

---

## Evidence Collection

For audits, collect:

**AI Feature Access Control Evidence:**
- Admin Exclusion Group membership list (export monthly)
- Deployment group configuration and user assignments per phase
- Web search control settings documentation (enabled/disabled per zone)
- Agent access control settings (allowed agent types per zone)
- Copilot Chat pinning configuration per department/role
- Evidence of 24-hour propagation validation for exclusion groups
- Evidence of 8-hour propagation validation for settings changes

**General Copilot Governance Evidence:**
- Copilot settings configuration export (M365 Admin Center > Copilot > Settings)
- Feature access control settings documentation (all four tabs: User access, Data access, Actions, Other)
- Agent registry export (M365 Admin Center > Agents > All agents)
- Usage reports (monthly) — Copilot Chat Active Users, Assisted Hours, Satisfaction Rate
- Audit log of configuration changes (Entra ID > Audit logs, filter for Copilot-related events)
- MCP Server availability list (M365 Admin Center > Agents > Tools)
- AI Administrator role assignment documentation
- Compliance Officer approval records for Admin Exclusion Group membership changes

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
