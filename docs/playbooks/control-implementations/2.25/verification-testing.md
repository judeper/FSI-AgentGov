# Control 2.25: Microsoft Agent 365 — Admin Center Governance Console — Verification & Testing

This playbook provides test cases, evidence collection procedures, and attestation templates for Control 2.25. All test procedures are designed to produce examination-ready evidence supporting FINRA Rule 3110 supervisory documentation requirements, SEC 17a-4 recordkeeping obligations, SOX 404 IT general controls testing, and OCC 2011-12 technology risk management review.

!!! info "Evidence Retention"
    All test outputs documented in this playbook must be retained in your compliance repository with the same retention schedule applied to technology control evidence — minimum 3 years for general IT controls, 6 years for records tied to broker-dealer supervision or customer activity. Apply your firm's SEC Rule 17a-4(f) compliant storage policy to all exported evidence files.

## Prerequisites Before Testing

- Agent 365 Frontier enrollment completed and confirmed in Billing > Licenses
- At least one test agent available in the registry (a non-production agent created specifically for governance testing)
- Governance administrator account with M365 Admin Center access
- Test user account with Copilot license (for end-to-end workflow tests)
- Access to your firm's change management system (for cross-referencing approval records)
- Compliance officer available for Zone 3 sign-off verification steps
- Test outputs directory created: `/compliance-tests/control-2.25/YYYY-MM-DD/`

## Test Case TC-2.25-01: Frontier Enrollment Verification

**Purpose:** Confirm that Copilot Frontier is enrolled and Agent 365 Frontier licenses are provisioned.
**Regulatory Basis:** OCC 2011-12 — Technology risk management; prerequisite for all other controls in this framework.
**Frequency:** Monthly, or immediately following any tenant-level license or configuration changes.

**Procedure:**

1. Navigate to **M365 Admin Center > Billing > Licenses**.
2. Locate the **Agent 365 Frontier** SKU in the license list.
3. Record the total and assigned license counts.
4. Navigate to **M365 Admin Center > Agents** and confirm the Agents section is visible in the left navigation.
5. Navigate to **M365 Admin Center > Copilot > Settings > User Access > Copilot Frontier** and confirm the enrollment toggle shows **Enabled**.

**Evidence to Collect:**

| Evidence Item | Collection Method | File Name Convention |
|---|---|---|
| Screenshot of Billing > Licenses showing Agent 365 Frontier | Browser screenshot | `TC-01-billing-licenses-YYYY-MM-DD.png` |
| Screenshot of Copilot Frontier toggle = Enabled | Browser screenshot | `TC-01-frontier-enabled-YYYY-MM-DD.png` |
| PowerShell output of Script 1 (Frontier Enrollment Check) | Script 1 JSON output | `TC-01-frontier-check-YYYY-MM-DD.json` |

**Pass Criteria:**
- Agent 365 Frontier SKU present with at least 1 license total
- Frontier toggle shows Enabled
- Agents section visible in admin center navigation
- Script 1 `EnrollmentHealthy` field = `true`

**Fail Response:** If any criterion fails, execute the [Troubleshooting playbook](troubleshooting.md) — Frontier Not Visible section before re-testing.

---

## Test Case TC-2.25-02: Admin Approval Workflow Enforcement

**Purpose:** Confirm that agent publication and activation requests cannot bypass the admin approval workflow for Zone 2 and Zone 3 environments.
**Regulatory Basis:** FINRA Rule 3110 — Supervisory control must be established before any agent is deployed.
**Frequency:** Quarterly, or following any change to agent publishing settings.

**Procedure:**

1. Using the **test user account** (non-admin), navigate to the agent creation experience (e.g., Copilot Studio or the in-product agent builder).
2. Create a minimal test agent with the name `TC-0225-ApprovalTest-[date]` and attempt to submit it for publication.
3. Confirm that the submission triggers a **Pending Request** — the agent does not publish automatically.
4. Navigate to **M365 Admin Center > Agents > Overview** (as the governance administrator) and confirm the test agent appears in the **Pending Requests** governance card.
5. Navigate to **Agents > All Agents > Registry > Requests tab** and confirm the test agent request is listed with status = Pending, sorted correctly by submission date.
6. Record the request age and confirm it is below SLA threshold.
7. Do NOT approve the request yet — reject it with reason `TEST: TC-2.25-02 approval workflow verification` to clean up without creating a live agent.

**Evidence to Collect:**

| Evidence Item | Collection Method | File Name Convention |
|---|---|---|
| Screenshot of test agent in Pending Requests governance card | Browser screenshot | `TC-02-pending-card-YYYY-MM-DD.png` |
| Screenshot of Requests tab showing pending status | Browser screenshot | `TC-02-requests-tab-YYYY-MM-DD.png` |
| Screenshot of rejection confirmation with rejection reason | Browser screenshot | `TC-02-rejection-YYYY-MM-DD.png` |

**Pass Criteria:**
- Test agent submission did not auto-publish
- Pending Requests card reflected the request within 5 minutes of submission
- Rejection action successfully removed the request from the queue
- Rejection reason is stored and visible in request history

**Fail Response:** If the test agent published without admin approval, immediately Block the agent, open an incident ticket, and escalate to the CISO. This represents a supervisory control failure requiring urgent remediation.

---

## Test Case TC-2.25-03: Governance Template Application Verification

**Purpose:** Confirm that the Default or Custom Governance Template is applied at publish time and that the associated policies are active post-publication.
**Regulatory Basis:** OCC 2011-12 — Layered security controls; SOX 404 — IT general controls; FINRA 3110 — Supervision.
**Frequency:** For each new agent publication in Zone 2/3; quarterly spot-check of existing agents.

**Procedure:**

1. Identify a recently published Zone 2 or Zone 3 agent in **Agents > All Agents > Registry**.
2. Click on the agent to open its detail view.
3. Locate the **Governance Template** field and confirm it shows either `Default Governance Template` (Zone 2) or your firm's custom template name (Zone 3).
4. For Zone 3 agents, confirm the custom template includes Entra Access Package by navigating to the template details.
5. Verify that Purview Audit is active for the agent by navigating to **Microsoft Purview > Audit > Activities** and searching for agent-related events in the last 7 days. Confirm agent activity events are being captured.
6. Verify that SharePoint Agent Access Insights is active by navigating to **SharePoint Admin Center > Active Sites** and confirming agent access entries exist for SharePoint-connected agents.

**Evidence to Collect:**

| Evidence Item | Collection Method | File Name Convention |
|---|---|---|
| Screenshot of agent detail view showing governance template name | Browser screenshot | `TC-03-agent-template-YYYY-MM-DD.png` |
| Screenshot of custom template details showing Entra Access Package (Zone 3) | Browser screenshot | `TC-03-custom-template-details-YYYY-MM-DD.png` |
| Screenshot of Purview Audit showing agent events | Browser screenshot | `TC-03-purview-audit-YYYY-MM-DD.png` |
| Exported agent inventory CSV showing GovernanceTemplate column | Script 2 CSV output | `TC-03-inventory-YYYY-MM-DD.csv` |

**Pass Criteria:**
- All Zone 2 agents show Default or Custom Governance Template (not None)
- All Zone 3 agents show a Custom Governance Template
- No Zone 3 agents show only the Default Template
- Purview Audit is capturing agent events
- Inventory CSV `GovernanceTemplate` column has no blank values for Zone 2/3 agents

**Fail Response:** Any agent in Zone 2/3 without a governance template applied must be immediately re-published through the publishing wizard with the correct template. Document as a control deficiency in your SOX 404 testing workpapers if the gap is material.

---

## Test Case TC-2.25-04: Pending Requests SLA Compliance Check

**Purpose:** Confirm that all pending requests are being reviewed and resolved within the defined SLA.
**Regulatory Basis:** FINRA Rule 3110 — Supervisory review must be timely; SOX 302 — Management must attest to control effectiveness.
**Frequency:** Weekly for Zone 2; Daily for Zone 3 (this test validates the ongoing process).

**Procedure:**

1. Navigate to **Agents > Overview** and review the **Pending Requests** governance card.
2. Note the total count and the week-over-week delta badge.
3. Click into the Requests tab and review the oldest pending request's submission date.
4. Calculate the age in business days.
5. Compare against SLA thresholds: Zone 2 = 5 business days, Zone 3 = 1 business day.
6. Run Script 3 (Governance Queue Status) and review the JSON output for `SLABreachDetected` and `PendingRequestsSLA` fields.

**Evidence to Collect:**

| Evidence Item | Collection Method | File Name Convention |
|---|---|---|
| Screenshot of Pending Requests card with count and delta | Browser screenshot | `TC-04-pending-requests-YYYY-MM-DD.png` |
| Script 3 JSON output showing SLA status | Script 3 JSON output | `TC-04-queue-status-YYYY-MM-DD.json` |
| Governance meeting minutes or ticket log showing review cadence | Exported from ticketing system | `TC-04-governance-log-YYYY-MM.pdf` |

**Pass Criteria:**
- No Zone 3 requests older than 1 business day
- No Zone 2 requests older than 5 business days
- Script 3 `SLABreachDetected` = `false`
- Governance meeting minutes confirm weekly (Zone 2) or daily (Zone 3) review occurred

---

## Test Case TC-2.25-05: Ownerless Agents Detection and Remediation

**Purpose:** Confirm that ownerless agents are detected, surfaced, and remediated promptly.
**Regulatory Basis:** FINRA Rule 3110 — Every agent must have an accountable supervisor in the chain; SOX 404 — Control ownership must be assigned.
**Frequency:** Weekly for Zone 2; Daily for Zone 3.

**Procedure:**

1. Navigate to **Agents > Overview** and review the **Ownerless Agents** governance card.
2. Record the count of ownerless agents.
3. If count is zero, verify via Script 3 output (`OwnerlessAgentsTotal` = 0) — this constitutes the pass evidence.
4. If ownerless agents are present, verify that a remediation ticket exists in the change management system for each one, with a due date within 48 hours and an assigned governance administrator.
5. For agents showing on the card, click **Assign Owner** on a test ownerless agent (if available) to confirm the inline action functions correctly.
6. Post-assignment, confirm the agent no longer appears on the Ownerless Agents card within 5 minutes.

**Evidence to Collect:**

| Evidence Item | Collection Method | File Name Convention |
|---|---|---|
| Screenshot of Ownerless Agents card (zero count) | Browser screenshot | `TC-05-ownerless-zero-YYYY-MM-DD.png` |
| Script 3 JSON output showing `OwnerlessAgentsTotal: 0` | Script 3 JSON output | `TC-05-queue-status-YYYY-MM-DD.json` |
| If agents remediated: Script 4 audit log entries | Script 4 JSON log | `TC-05-owner-assignment-log-YYYY-MM.json` |

**Pass Criteria:**
- Ownerless Agents card count = 0, OR
- If agents present: each has an open remediation ticket with due date within 48 hours
- No ownerless agent has been in the unassigned state for more than 48 hours without a documented escalation
- Owner Assignment Log (Script 4) is up to date for all remediated agents

---

## Test Case TC-2.25-06: Exception Rate Monitoring and Threshold Alerting

**Purpose:** Confirm that the Exception Rate metric is being actively monitored and that a defined threshold with an escalation path exists.
**Regulatory Basis:** OCC 2011-12 — Ongoing monitoring of technology risk; FINRA 3110 — Supervisory system must include anomaly detection.
**Frequency:** Monthly review of monitoring configuration; ongoing daily/weekly operational monitoring.

**Procedure:**

1. Navigate to **Agents > Overview** and record the current **Exception Rate** hero metric value.
2. Confirm the Exception Rate is documented against the firm's defined threshold (e.g., >5% = escalation required).
3. Locate the documented threshold in the AI governance policy or runbook (must be a named document, not informal knowledge).
4. Confirm that an escalation path exists — a named individual or team to receive alerts when the threshold is exceeded.
5. If automated alerting is configured (e.g., Azure Monitor alert on the metric, or Script 3 email alert), provide evidence of the alert rule configuration.
6. Review governance meeting minutes from the last 30 days to confirm the metric was reviewed at each session.

**Evidence to Collect:**

| Evidence Item | Collection Method | File Name Convention |
|---|---|---|
| Screenshot of Overview dashboard showing Exception Rate metric | Browser screenshot | `TC-06-exception-rate-YYYY-MM-DD.png` |
| Copy of AI governance policy section defining exception rate threshold | Policy document extract | `TC-06-threshold-policy-YYYY-MM.pdf` |
| Alert rule configuration (Azure Monitor or equivalent) | Export from monitoring tool | `TC-06-alert-rule-YYYY-MM-DD.json` |
| Governance meeting minutes referencing exception rate review | Meeting minutes extract | `TC-06-governance-minutes-YYYY-MM.pdf` |

**Pass Criteria:**
- Exception Rate metric visible and current on Overview dashboard
- Documented threshold exists in a named policy or runbook
- Named escalation path exists (person or team)
- Metric reviewed at every governance session in the past 30 days (documented in minutes)
- No unresolved threshold breach from the prior 30 days without a documented investigation record

---

## Test Case TC-2.25-07: Monthly Inventory Export and Retention Verification

**Purpose:** Confirm that monthly inventory exports are being produced, date-stamped, and stored in a retention-compliant location.
**Regulatory Basis:** SEC Rules 17a-3/17a-4 — Books and records retention; FINRA 3110 — Examination readiness.
**Frequency:** Monthly.

**Procedure:**

1. Navigate to the compliance repository and confirm a date-stamped inventory export file exists for the current month (format: `agent-inventory-YYYY-MM-DD.csv`).
2. Open the current month's export and confirm it contains the required fields: Agent Name, Agent ID, Publisher, Platform, Owner, Status, Deployment Scope, Governance Template Applied, Last Modified Date.
3. Confirm at least 12 consecutive monthly exports exist in the repository (rolling 12-month retention minimum for active exam readiness).
4. Confirm the storage location applies an immutability or WORM policy consistent with SEC Rule 17a-4(f).
5. Review the export log file (`agent-inventory-export-log.json`) to confirm each export was performed by the authorized service principal and within 5 business days of month-end.

**Evidence to Collect:**

| Evidence Item | Collection Method | File Name Convention |
|---|---|---|
| Directory listing of compliance repository showing 12+ monthly exports | `ls` or storage browser screenshot | `TC-07-repository-listing-YYYY-MM-DD.png` |
| Sample export file (current month) | CSV file | `TC-07-inventory-sample-YYYY-MM-DD.csv` |
| Export log JSON file | JSON file | `TC-07-export-log-YYYY-MM.json` |
| Storage immutability policy configuration | Storage admin screenshot | `TC-07-storage-policy-YYYY-MM-DD.png` |

**Pass Criteria:**
- Current month's export exists within 5 business days of month-end
- All required fields present in the export
- 12 consecutive monthly exports available
- Storage immutability policy active on the repository
- Export log confirms all exports performed by authorized service principal

---

## Test Case TC-2.25-08: Researcher with Computer Use Configuration Verification

**Purpose:** Confirm that the Researcher with Computer Use capability is configured per organizational policy and not left in default state.
**Regulatory Basis:** OCC 2011-12 — Explicit control decisions for technology capabilities; FINRA 3110 — Supervision of AI-assisted research workflows.
**Frequency:** Quarterly, or following any change to Researcher configuration.

**Procedure:**

1. Navigate to **Agents > Researcher > Computer Use tab**.
2. Record the current configuration for all three settings: Who has access, Work Access toggle, Website Access policy.
3. Compare recorded configuration against the documented policy decision in your AI governance policy or the Researcher with Computer Use configuration log.
4. For Zone 3 institutions, confirm:
   a. Who has access = Specific groups (not All users)
   b. The specified group is the approved security group defined in your AI governance policy
   c. Work Access = Off (unless written CISO approval exists)
   d. Website Access = Allow specific URLs with a defined allowlist
5. Confirm the configuration decision is documented with: date configured, configured by (named administrator), approving authority, and business justification.

**Evidence to Collect:**

| Evidence Item | Collection Method | File Name Convention |
|---|---|---|
| Screenshot of Computer Use tab showing all three settings | Browser screenshot | `TC-08-computer-use-config-YYYY-MM-DD.png` |
| Extract from AI governance policy or config log showing approved configuration | Policy/log document | `TC-08-config-policy-YYYY-MM.pdf` |
| CISO approval letter (Zone 3 Work Access only, if enabled) | Signed document | `TC-08-ciso-approval-YYYY-MM.pdf` |

**Pass Criteria:**
- All three Computer Use settings reflect a documented, affirmative decision (not default/unreviewed state)
- Zone 3 access is limited to specific approved group
- Work Access = Off unless CISO written approval exists and is on file
- Website Access = specific URL allowlist for Zone 3
- Configuration is documented with named administrator and approving authority

---

## Evidence Package Assembly for Examinations

When preparing for a FINRA cycle exam, OCC examination, or SOX 404 audit, assemble the following evidence package from the test outputs above:

| Examination Topic | Test Cases | Evidence Files |
|---|---|---|
| AI governance control environment | TC-01, TC-02 | Frontier enrollment screenshots, approval workflow screenshots |
| Agent supervision documentation | TC-02, TC-03, TC-05 | Approval records, governance template screenshots, owner assignment log |
| Technology risk management | TC-01, TC-03, TC-06 | Enrollment verification, template evidence, exception rate monitoring docs |
| Books and records — agent inventory | TC-07 | 12 months of CSV exports, export log, storage policy evidence |
| Internal controls over technology | TC-03, TC-04, TC-06 | Template evidence, SLA compliance reports, monitoring configuration |
| Supervisory system documentation | TC-02, TC-04, TC-05 | Approval workflow, SLA reports, ownerless agent remediation log |

!!! warning "Examination Readiness SLA"
    Financial services regulators (FINRA, OCC, SEC) may request AI governance evidence with as little as 24–48 hours notice during an examination. Maintain your evidence package in a state where it can be produced within 24 hours. Monthly inventory exports, quarterly test execution, and daily governance queue monitoring are not aspirational — they are the minimum required to meet this production standard.

---

[Back to Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

*Updated: March 2026 | Version: v1.3*
