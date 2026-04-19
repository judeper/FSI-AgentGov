# Control 3.8: Copilot Hub and Governance Dashboard — Verification & Testing

> Verification and testing procedures for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md). Use this playbook to produce examination-ready evidence that the Copilot Hub and Agent governance surfaces are configured per zone, that AI feature toggles are governed, and that transcript supervision controls operate as designed. All language is hedged — these tests **support** FINRA / SEC / GLBA / SOX evidence; they do not by themselves constitute compliance.

---

## Verification Strategy

| Layer | What to test | Evidence type |
|---|---|---|
| **Portal accessibility** | Copilot Hub, Agents page, PPAC Copilot all render with required navigation | Screenshot |
| **Settings configuration** | User access, Data access, Actions, Other tabs match zone profile | Screenshot + JSON snapshot |
| **Behavioral controls** | Admin Exclusion Group, Deployment Groups, web search, agent restrictions | Test-user sign-in evidence |
| **Supervision controls** | Transcript access roles, separation of duties, retention, audit trail | Role assignment export + audit log |
| **SSPM hardening** | AI feature toggles per Configuration Hardening Baseline | Screenshot + JSON snapshot |

---

## Compliance Checklist

| # | Item | Evidence | Regulatory tie |
|---|---|---|---|
| 1 | Copilot Settings documented across all four tabs | Screenshot + JSON | FINRA 4511, SOX 404 |
| 2 | Web search disabled per zone | Screenshot + behavioral test | GLBA 501(b), MNPI |
| 3 | External AI providers and third-party LLMs blocked | Screenshot | FINRA 4511 |
| 4 | Agent approval workflow active | Pending-requests export | FINRA 3110, SEC 17a-3 |
| 5 | Monthly usage reports archived | Export + SHA-256 manifest | FINRA 4511, FINRA 25-07 |
| 6 | MCP Server allow-list reviewed | Screenshot + change ticket | SOX 404 |
| 7 | Transcript access restricted to Compliance | Role export | FINRA 3110 |
| 8 | Transcript retention ≥ 7 years | Purview retention policy | FINRA 4511, SEC 17a-4 |
| 9 | Separation of duties — agent creators excluded from own transcripts | RBAC / CA policy | FINRA 3110 |
| 10 | DLP blocks publishing connectors in restricted environments | DLP policy export | SOX 404, FINRA 4511 |

---

## Test Cases — Behavioral Controls

Each test case includes an objective, prerequisites, steps, structured pass/fail criteria, evidence to collect, and the regulatory mapping.

### FAC-01 — Admin Exclusion Group removes Copilot admin-center access

**Objective:** Verify `CopilotForM365AdminExclude` group membership removes admin-center Copilot features for excluded users.

**Prerequisites:**

- `CopilotForM365AdminExclude` security group exists (exact name).
- Test user has M365 Copilot license and is **not** currently in the group.

**Steps:**

1. Baseline: sign in as test user; capture screenshot showing Copilot admin-center features available.
2. Add test user to `CopilotForM365AdminExclude`. Record timestamp.
3. Wait the full **24-hour** propagation window.
4. Force a fresh authentication (sign out, clear cache, sign in).
5. Capture screenshot showing admin-center Copilot features unavailable.
6. Confirm M365 Copilot license is still assigned (license assignment must be unchanged — exclusion is behavioral).
7. Remove the user from the group, wait 24 hours, confirm restoration.

**Pass criteria:**

- After ≥ 24 hours, the excluded user cannot access admin-center Copilot features while still holding the license.
- Removing the user from the group restores access within 24 hours.

**Fail conditions:**

- Access remains after 24 hours → check group name spelling (case-sensitive) and conflicting policies.
- License is missing → exclusion was applied incorrectly via licensing rather than the exclusion group.

**Evidence:** before/after screenshots, group membership export, Entra audit log entry for the membership change, timestamp record.

**Regulatory mapping:** FINRA 3110 (supervisory restrictions), SOX 404 (IT access controls).

---

### FAC-02 — Deployment Group limits Copilot to approved population

**Objective:** Verify Copilot availability is limited to deployment-group members.

**Prerequisites:**

- Deployment group (e.g., `Copilot-Pilot-IT-Compliance`) created.
- Test User A (in group) and Test User B (not in group), both with M365 Copilot license.

**Steps:**

1. Configure Copilot to be available only to the deployment group; record timestamp.
2. Wait **8 hours** for tenant propagation.
3. Test User A: confirm Copilot Chat in Teams/Outlook is accessible.
4. Test User B: confirm Copilot Chat is **not** accessible.
5. Confirm both users hold identical Copilot licenses.

**Pass criteria:** A has access; B does not; license assignments are identical.

**Fail conditions:**

- B has access → confirm group type is **Security**, deployment group setting is enabled, and 8-hour propagation has elapsed.
- A has no access → confirm A is in the deployment group and not also in the Admin Exclusion Group (exclusion overrides).

**Evidence:** group membership export, before/after screenshots for both users, license assignment report.

**Regulatory mapping:** SOX 404 (documented IT controls), FINRA 3110 (supervised rollout).

---

### FAC-03 — Web search control prevents external grounding

**Objective:** Verify disabling web search removes web-grounded responses while preserving organizational data access.

**Prerequisites:** Test user with M365 Copilot access; web search initially Enabled.

**Steps:**

1. Baseline (web search Enabled): ask Copilot a query requiring external data ("latest news headlines today"). Capture web-grounded response.
2. Disable web search in M365 Admin → Copilot → Settings → Data access. Record timestamp.
3. Wait **8 hours**.
4. Repeat the same query. Capture response — should refuse external grounding.
5. Ask a query answerable from organizational data ("summarize my recent emails") — confirm Copilot still answers using M365 data only.

**Pass criteria:**

- Post-disable response contains no web grounding.
- Organizational data queries continue to function.

**Fail conditions:**

- Web grounding still present after 8 hours → see troubleshooting playbook (`Issue: Web search still returning results`).

**Evidence:** before/after screenshots of the M365 Admin setting, before/after Copilot responses with citations, organizational-data response, timestamp record.

**Regulatory mapping:** GLBA 501(b) (prevent external data leakage), FINRA (MNPI protection).

---

### FAC-04 — Agent access restriction prevents third-party discovery

**Objective:** Verify Zone 3 agent access policy hides non-organizational agents.

**Prerequisites:** Zone 3 environment configured to "Organizational agents only".

**Steps:**

1. Configure Actions → Allowed agent types → "Organizational only".
2. Wait 8 hours.
3. As a deployment-group user, open the agent gallery in Copilot Chat.
4. Confirm only organizational agents are listed.
5. Attempt to install a Microsoft-verified or third-party agent → confirm install path is unavailable.

**Pass criteria:** Only organizational agents are discoverable; install paths for other publishers are unavailable.

**Evidence:** screenshot of Settings → Actions, screenshot of agent gallery, install attempt screenshot.

**Regulatory mapping:** FINRA 4511, FINRA 25-07 (approved tools and systems).

---

### FAC-05 — AI Administrator can configure Copilot without Global Admin

**Objective:** Confirm least-privilege role model is operative.

**Steps:**

1. Assign a test user the **AI Administrator** role only.
2. Sign in as that user; navigate to M365 Admin → Copilot → Settings.
3. Modify a setting on each of User access, Data access, Actions tabs; save.
4. Confirm the change persists.

**Pass criteria:** Settings changes save successfully without Global Admin elevation.

**Evidence:** role assignment screenshot, before/after settings export, Entra audit log entry showing the AI Administrator as initiator.

**Regulatory mapping:** SOX 404 segregation of duties; OCC 2011-12 least-privilege.

---

### FAC-06 — Agent approval workflow

**Objective:** Verify newly published agents require approval before becoming available.

**Steps:**

1. Configure Agents → Settings → require approval for new agents.
2. As a maker, publish a test agent.
3. Confirm the agent appears in **Pending Requests** on the Agent overview page.
4. Approve the agent as the AI Governance Lead.
5. Confirm the agent then appears in the registry as available.

**Pass criteria:** Publishing → Pending → Approved → Available state flow is observable and audit-logged.

**Evidence:** screenshots of each state, audit log entry for the approval event.

**Regulatory mapping:** FINRA 3110 (supervisory pre-approval), SOX 404 (change control).

---

### FAC-07 — MCP Server blocking

**Objective:** Verify blocked MCP servers cannot be invoked by agents.

**Steps:**

1. Block a test MCP server in M365 Admin → Agents → Tools.
2. Attempt to use a capability backed by that server from an agent.
3. Confirm the capability fails with a clear access-denied response.

**Pass criteria:** Blocked MCP server capability is unavailable; error reason is logged.

**Evidence:** screenshot of Tools allow/block list, agent invocation log.

**Regulatory mapping:** GLBA 501(b), SOX 404.

---

### FAC-08 — Transcript separation of duties

**Objective:** Verify agent creators cannot access transcripts for agents they built.

**Prerequisites:** Test user is in `Copilot-Studio-Publishers`; not in `Copilot-Compliance-Supervisors`.

**Steps:**

1. As the test user, build and publish a test agent in a Zone 2/3 environment.
2. Have a different user interact with the agent to generate transcripts.
3. As the original creator, attempt to view transcripts for that agent.
4. Confirm access is denied (Conditional Access or RBAC).
5. As a member of `Copilot-Compliance-Supervisors`, confirm transcripts are accessible.

**Pass criteria:** Creator denied; Supervisor permitted.

**Evidence:** RBAC role export, Conditional Access policy export, denial screenshot, supervisor access screenshot.

**Regulatory mapping:** FINRA 3110 (supervision separation of duties), SOX 404.

---

## Evidence Collection Pack

For each monthly governance review, collect and store with SHA-256 manifest (see PowerShell `Write-FsiEvidence`):

**AI Feature Access Control:**

- Admin Exclusion Group membership (monthly export).
- Deployment group definitions and member rosters per wave.
- Web search and external AI settings per zone.
- Allowed agent types per zone.
- Copilot Chat pinning configuration per department.
- 24-hour and 8-hour propagation validation timestamps.

**General Copilot Governance:**

- Copilot Settings export (User access, Data access, Actions, Other tabs).
- Agent registry export (Publisher, Channel, Platform breakdown).
- Monthly usage report (Chat Active Users, Assisted Hours, Satisfaction Rate).
- Entra audit log filtered for Copilot-related changes (≥ 30 days).
- MCP server allow/block list.
- AI Administrator role assignment evidence.
- Compliance Officer approval records for Admin Exclusion Group changes.

**Supervision and Records:**

- Transcript access role matrix (Entra group → permission mapping).
- Conditional Access policy evidence enforcing creator exclusion.
- Purview Audit retention policy showing ≥ 7 years.
- Sample exported transcript with SHA-256 hash.
- Quarterly attestation from supervisors.

---

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"
    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected | Portal Path | Evidence |
|---|---|---|---|---|
| SSPM-3.8-01 | AI Prompts toggle | Disabled at tenant | PPAC → Copilot → Settings | Screenshot |
| SSPM-3.8-02 | Generative Actions toggle | Disabled at tenant | PPAC → Copilot → Settings | Screenshot |
| SSPM-3.8-03 | File Analysis Models | Disabled | PPAC → Copilot → Settings | Screenshot |
| SSPM-3.8-04 | Model Knowledge | Disabled | PPAC → Copilot → Settings | Screenshot |
| SSPM-3.8-05 | Semantic Search with AI | Disabled | PPAC → Copilot → Settings | Screenshot |
| SSPM-3.8-06 | Move Data Across Regions | Disabled | PPAC → Environments → Generative AI features | Screenshot |
| SSPM-3.8-07 | Bing Search | Disabled | PPAC → Environments → Generative AI features | Screenshot |
| SSPM-3.8-08 | Transcript access | Restricted to Compliance roles | PPAC → Copilot → Settings | Screenshot + role export |
| SSPM-3.8-09 | DLP for publishing | Active and applied | PPAC → Policies → Data policies | Screenshot |

### Test procedures

For each SSPM-3.8-NN test:

1. Navigate to the portal path.
2. Locate the toggle/setting.
3. Confirm the value matches **Expected**.
4. Capture screenshot showing the setting state, the environment context (where applicable), and the timestamp.
5. Record the change-ticket reference that authorized the current state.

**Pass criteria** (all): setting in expected state with documented change-ticket evidence.

**Common fail mode:** the setting was changed at the per-environment level but not at tenant level. Re-check both scopes — the strictest setting wins.

---

## Quarterly attestation prompt

For Compliance Officer / AI Governance Lead sign-off:

> "I have reviewed the Control 3.8 monthly evidence packs for the past quarter. Admin Exclusion Group membership matches the current restricted-persons list. Deployment groups align with the approved rollout plan. Web search controls are configured per zone. AI feature toggles in PPAC are Off unless approved with documented business justification. Transcript access is restricted to Compliance and supervisors are independent of agent creators. No unauthorized transcript access events were observed. Variances are documented in the variance log."

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — manual configuration
- [PowerShell Setup](powershell-setup.md) — automation scripts
- [Troubleshooting](troubleshooting.md) — common issues and resolutions

---

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
