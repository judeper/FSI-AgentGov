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

!!! warning "Deprecated Legacy Test Cases"
    The following legacy test cases are superseded by the detailed FAC-prefixed test procedures above (FAC-01 through FAC-03). Use the FAC-prefixed tests for current verification workflows. These legacy cases are retained for historical reference only.

### Test Case 1: Admin Exclusion Group Access Control (Legacy — see FAC-01)

**Objective:** Verify users in Admin Exclusion Group cannot access Copilot

**Steps:**

1. Create Admin Exclusion Group in M365 Admin
2. Add test user to Admin Exclusion Group
3. Wait for propagation (up to 24 hours)
4. Sign in as test user
5. Attempt to access Copilot Chat in Teams/Outlook

**Expected Result:** Access denied or Copilot features not visible

### Test Case 2: Deployment Group Restrictions (Legacy — see FAC-02)

**Objective:** Verify users outside deployment group cannot access Copilot

**Steps:**

1. Create deployment group with specific users
2. Assign Copilot to deployment group only
3. Wait for propagation (up to 24 hours)
4. Test with user inside deployment group
5. Test with user outside deployment group

**Expected Result:** Feature available only to users in deployment group

### Test Case 3: Web Search Control Disabled (Legacy — see FAC-03)

**Objective:** Verify Copilot responses use only organizational data when web search disabled

**Steps:**

1. Disable web search in Copilot Settings (Data Access tab)
2. Wait for propagation (up to 8 hours)
3. Test Copilot chat prompt requiring web search
4. Verify web search not used in response

**Expected Result:** Copilot respects disabled web search setting

### Test Case 4: Agent Access Restrictions (Legacy)

**Objective:** Verify restricted agent access prevents third-party agent discovery

**Steps:**

1. Configure agent access to organizational agents only
2. Wait for propagation
3. Attempt to discover third-party agents
4. Verify only organizational agents available

**Expected Result:** Third-party agents not discoverable

### Test Case 5: AI Administrator Role Permissions (Legacy)

**Objective:** Verify AI Administrator can configure Copilot settings without Global Admin

**Steps:**

1. Assign AI Administrator role to test user
2. Sign in as AI Administrator
3. Navigate to M365 Admin > Copilot > Settings
4. Modify Copilot settings (User Access, Data Access, Actions)
5. Verify settings changes applied successfully

**Expected Result:** Settings changes applied successfully without Global Admin

### Test Case 6: Settings Application (Legacy — see FAC-03)

**Objective:** Verify settings changes take effect

**Steps:**

1. Disable web search in Copilot Settings
2. Test Copilot chat prompt requiring web
3. Verify web search not used

**Expected Result:** Copilot respects disabled web search

### Test Case 7: Agent Approval Workflow (Legacy)

**Objective:** Verify agents require approval

**Steps:**

1. Configure agent approval requirement
2. Publish test agent
3. Verify agent appears in Requests tab
4. Approve agent
5. Verify agent available

**Expected Result:** Agents require approval before availability

### Test Case 8: MCP Server Blocking (Legacy)

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

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|-------------------|-----------------|-------------|----------|
| SSPM-3.8-01 | AI Prompts toggle | Disabled at tenant level | PPAC > Settings > Power Platform Settings | Screenshot |
| SSPM-3.8-02 | Generative Actions toggle | Disabled at tenant level | PPAC > Settings > Power Platform Settings | Screenshot |
| SSPM-3.8-03 | File Analysis Models | Disabled | PPAC > Settings > Power Platform Settings | Screenshot |
| SSPM-3.8-04 | Model Knowledge | Disabled | PPAC > Settings > Power Platform Settings | Screenshot |
| SSPM-3.8-05 | Semantic Search with AI | Disabled | PPAC > Settings > Power Platform Settings | Screenshot |
| SSPM-3.8-06 | Move Data Across Regions | Disabled | PPAC > Settings > Power Platform Settings | Screenshot |
| SSPM-3.8-07 | Bing Search | Disabled | PPAC > Settings > Power Platform Settings | Screenshot |
| SSPM-3.8-08 | Transcript access | Restricted to compliance roles | M365 Admin > Copilot > Settings | Screenshot |
| SSPM-3.8-09 | DLP for publishing | DLP policy enforcement active | PPAC > Policies > Data policies | Screenshot |

### Test Procedures

**SSPM-3.8-01: AI Prompts Toggle**

1. Navigate to **PPAC** > **Settings** > **Power Platform Settings**
2. Locate "AI Prompts" toggle
3. Verify toggle is set to **Disabled** at the tenant level
4. **Pass criteria:** AI Prompts toggle is off — makers cannot create AI prompt actions
5. **Evidence:** Screenshot showing Power Platform Settings page with AI Prompts toggle state

**SSPM-3.8-02: Generative Actions Toggle**

1. Navigate to **PPAC** > **Settings** > **Power Platform Settings**
2. Locate "Generative Actions" toggle
3. Verify toggle is set to **Disabled** at the tenant level
4. **Pass criteria:** Generative Actions toggle is off — generative AI actions are not available to makers
5. **Evidence:** Screenshot showing Power Platform Settings page with Generative Actions toggle state

**SSPM-3.8-03: File Analysis Models**

1. Navigate to **PPAC** > **Settings** > **Power Platform Settings**
2. Locate "File Analysis Models" toggle
3. Verify toggle is set to **Disabled**
4. **Pass criteria:** File Analysis Models is disabled — no automated file analysis via AI
5. **Evidence:** Screenshot showing toggle state

**SSPM-3.8-04: Model Knowledge**

1. Navigate to **PPAC** > **Settings** > **Power Platform Settings**
2. Locate "Model Knowledge" toggle
3. Verify toggle is set to **Disabled**
4. **Pass criteria:** Model Knowledge is disabled — agents cannot access general model knowledge
5. **Evidence:** Screenshot showing toggle state

**SSPM-3.8-05: Semantic Search with AI**

1. Navigate to **PPAC** > **Settings** > **Power Platform Settings**
2. Locate "Semantic Search with AI" toggle
3. Verify toggle is set to **Disabled**
4. **Pass criteria:** Semantic Search with AI is disabled — AI-powered search is not active
5. **Evidence:** Screenshot showing toggle state

**SSPM-3.8-06: Move Data Across Regions**

1. Navigate to **PPAC** > **Settings** > **Power Platform Settings**
2. Locate "Move Data Across Regions" toggle
3. Verify toggle is set to **Disabled**
4. **Pass criteria:** Cross-region data movement is disabled — data stays within the configured region
5. **Evidence:** Screenshot showing toggle state

**SSPM-3.8-07: Bing Search**

1. Navigate to **PPAC** > **Settings** > **Power Platform Settings**
2. Locate "Bing Search" toggle
3. Verify toggle is set to **Disabled**
4. **Pass criteria:** Bing Search is disabled — agents cannot query external web data via Bing
5. **Evidence:** Screenshot showing toggle state

**SSPM-3.8-08: Transcript Access**

1. Navigate to **M365 Admin Center** > **Copilot** > **Settings**
2. Review transcript access configuration
3. Verify transcript access is restricted to compliance roles only (not all users or all admins)
4. **Pass criteria:** Only designated compliance roles can access agent interaction transcripts
5. **Evidence:** Screenshot showing transcript access control settings with role assignments

**SSPM-3.8-09: DLP for Publishing**

1. Navigate to **PPAC** > **Policies** > **Data policies**
2. Verify at least one DLP policy is active and applies to the target environments
3. Verify the policy blocks or restricts high-risk connectors
4. Confirm DLP enforcement is active for agent publishing (agents cannot publish if they violate DLP)
5. **Pass criteria:** DLP policy enforcement is active and applies to all governed environments
6. **Evidence:** Screenshot showing DLP policy list with environment assignments and connector classifications

---

*Updated: February 2026 | Version: v1.3 | Classification: Verification Testing*
