# Playbook: Portal Walkthrough — Control 2.26

**Control:** 2.26 — Entra Agent ID: Identity Governance for Agents
**Playbook Type:** Portal Walkthrough
**Estimated Time:** 2–4 hours (initial setup); 30 minutes per subsequent agent onboarding
**Prerequisites:** Microsoft 365 Global Administrator or Identity Governance Administrator; Frontier program enrollment completed or in progress

---

!!! info "Preview Feature — Microsoft Entra Agent ID"
    The Entra Agent ID capabilities configured in this playbook are available in **PREVIEW** via the Microsoft 365 Frontier program only. Steps that reference the "Agent identities" blade, access packages for agent identities, and agent-specific lifecycle workflows all require an active Frontier enrollment. Steps that use general Entra Identity Governance features (entitlement management, access reviews, lifecycle workflows) are generally available but may require Entra ID Governance P2 licensing.

    Verify Frontier enrollment is active before beginning. If the Agent identities blade is not visible after enrollment, allow up to one hour for propagation.

!!! warning "Licensing Requirements"
    The following licenses are required for full Control 2.26 implementation:
    - **Microsoft Entra ID Governance** (P2 or Governance add-on) — required for entitlement management, access packages, and lifecycle workflows
    - **Microsoft 365 Frontier enrollment** — required for Entra Agent ID, agent identity management, and agent-specific access package support
    - **Microsoft Entra ID P2** — required for access reviews and Privileged Identity Management integration

---

## Section 1: Enable Frontier and Verify Entra Agent ID Availability

### Step 1.1: Enroll in the Microsoft 365 Frontier Program

1. Navigate to the **Microsoft 365 Admin Center**: [https://admin.microsoft.com](https://admin.microsoft.com)
2. In the left navigation, select **Copilot**.
3. Select **Settings**.
4. Locate the **Frontier** section and select **Manage Frontier enrollment**.
5. Review the Frontier program terms.
6. Select **Enroll** and confirm.
7. Record the enrollment confirmation and date in the governance log.

!!! note "Propagation Time"
    After enrolling in Frontier, allow **up to one hour** before the Agent identities blade appears in the Entra admin center. Do not proceed to Step 1.2 until the blade is visible.

### Step 1.2: Verify Entra Agent ID Blade Availability

1. Navigate to the **Microsoft Entra admin center**: [https://entra.microsoft.com](https://entra.microsoft.com)
2. In the left navigation, expand **Applications**.
3. Confirm the presence of **Agent identities** in the Applications submenu.
4. Select **Agent identities** to open the agent inventory.
5. Verify that existing Copilot Studio agents deployed in the tenant are visible.

!!! danger "If Agent Identities Blade Is Missing"
    If the Agent identities blade is not visible after one hour, see the [Troubleshooting playbook](troubleshooting.md) — Section 1: Agent Identities Not Visible. Common causes include incomplete Frontier enrollment or browser cache issues.

### Step 1.3: Document Baseline Inventory

1. Within the Agent identities blade, select **Export** to download the current agent inventory.
2. Record the total count of agent identities in the governance log.
3. Note which agents have null or empty Sponsor fields — these represent immediate governance gaps requiring remediation in Section 2.

---

## Section 2: Assign Agent Sponsors

Sponsor assignment is the foundational accountability step of this control. Every Zone 2 and Zone 3 agent must have a named, individual human sponsor before the agent is considered compliant.

### Step 2.1: Assign a Sponsor to an Individual Agent

1. In the Entra admin center, navigate to **Applications > Agent identities**.
2. Select the agent requiring a sponsor assignment.
3. Select **Properties** in the agent detail panel.
4. Locate the **Sponsor** field.
5. Select **Edit** or the assignment icon next to the Sponsor field.
6. Search for and select the named individual who is accountable for this agent.

!!! warning "Sponsor Must Be a Named Individual"
    The sponsor field must be assigned to a named individual user account. Shared mailboxes, distribution groups, service accounts, and role groups are not acceptable sponsors for governance compliance. The sponsor must be a person who can be held accountable and who will receive lifecycle workflow notifications.

7. Select **Save**.
8. Verify the sponsor name appears in the Properties panel.
9. Notify the newly assigned sponsor via email, including a link to their sponsor responsibilities documentation.

### Step 2.2: Zone-Specific Sponsor Requirements

| Zone | Sponsor Requirement | Secondary Approver |
|---|---|---|
| Zone 1 — Personal | Creator documented in agent description field; no formal Entra sponsor required | None |
| Zone 2 — Team | Formal sponsor assigned in Entra Agent ID Properties; department head notified | Department Head (for departure workflow) |
| Zone 3 — Enterprise | Formal sponsor assigned in Entra Agent ID Properties at deployment time | Compliance Officer designated as secondary approver in access package policy |

### Step 2.3: Bulk Sponsor Assignment for Pre-Existing Agents

For organizations with a large number of agents deployed before this control was implemented, use the [PowerShell Setup playbook](powershell-setup.md) — Section 3 (Bulk Sponsor Assignment) to assign sponsors programmatically via Microsoft Graph API. After bulk assignment, return to this section to verify the assignments are reflected in the Entra portal.

---

## Section 3: Create the Agent Resources Entitlement Management Catalog

The entitlement management catalog is the container for all resources that agents are authorized to access. Access packages within this catalog define the specific bundles of resources assigned to agents.

### Step 3.1: Create the Catalog

1. In the Entra admin center, navigate to **Identity Governance > Entitlement management**.
2. Select **Catalogs** in the left panel.
3. Select **New catalog**.
4. Configure the following settings:

    | Field | Value |
    |---|---|
    | Name | AI Agent Resources |
    | Description | Contains all SharePoint, Graph API, and data resources available for governed assignment to AI agent identities |
    | Enabled | Yes |
    | Enabled for external users | No |

5. Select **Create**.

### Step 3.2: Add Resources to the Catalog

1. Select the newly created **AI Agent Resources** catalog.
2. Select **Resources** in the catalog detail panel.
3. Select **Add resources**.
4. Add each resource that agents are permitted to access. Common examples for FSI environments:

    | Resource Type | Examples |
    |---|---|
    | SharePoint sites | Compliance document library, Reporting SharePoint site, Research data site |
    | Microsoft Graph API permissions | Sites.Read.All, Files.Read.All, Mail.Read (restricted), Calendars.Read |
    | Azure resource groups | If agents interact with Azure-hosted data services |
    | Applications | Other M365 or line-of-business applications accessible to agents |

5. Select **Add** after selecting each resource.
6. Verify all required resources appear in the catalog resources list.

!!! note "Resource Scoping"
    Add only the resources that agents actually require. The principle of least privilege applies to access packages: an access package should grant the minimum set of permissions necessary for the agent's documented function. Broad or catch-all permissions defeat the purpose of entitlement management.

---

## Section 4: Create Access Packages for Agent Resource Bundles

Access packages represent the standard configurations of resource access appropriate for different agent types and zones. Every Zone 3 agent must access resources exclusively through access packages; no direct permission assignments outside entitlement management are permitted for Zone 3.

### Step 4.1: Create a Zone 2 Standard Access Package

1. Navigate to **Identity Governance > Entitlement management > Catalogs > AI Agent Resources**.
2. Select **Access packages**.
3. Select **New access package**.
4. On the **Basics** tab, configure:

    | Field | Value |
    |---|---|
    | Name | SharePoint Read + Graph Read — Zone 2 Agent |
    | Description | Standard read-only access to team SharePoint and Graph API for Zone 2 team agents |
    | Catalog | AI Agent Resources |

5. Select **Next: Resource roles**.
6. Select **Add resources** and choose the SharePoint sites and Graph API permissions appropriate for Zone 2 agents.
7. Assign the appropriate role for each resource (e.g., Read, Visitor).
8. Select **Next: Requests**.
9. Configure request policy:
    - Who can request: **Specific users and groups** (restrict to users who have been approved to deploy Zone 2 agents)
    - Require approval: **Yes**
    - First approver: Agent Sponsor
10. Select **Next: Lifecycle**.
11. Configure lifecycle settings:

    | Field | Value |
    |---|---|
    | Access package assignments expire | On a specified date — or — After a number of days |
    | Maximum duration | 365 days |
    | Allow users to extend | Yes (requires sponsor re-approval) |
    | Require access reviews | No (Zone 2 uses annual lifecycle review, not quarterly certification) |

12. Select **Next: Review + Create** and select **Create**.

### Step 4.2: Create a Zone 3 Standard Access Package

Repeat the steps in 4.1 with the following differences:

| Field | Zone 3 Configuration |
|---|---|
| Name | SharePoint Read/Write + Graph Full — Zone 3 Agent |
| Description | Governed access to enterprise SharePoint and Graph API for Zone 3 regulated agents |
| First approver (Requests) | AI Governance Lead |
| Second approver (Requests) | Compliance Officer |
| Maximum duration (Lifecycle) | 365 days |
| Allow extensions | Yes — requires AI Governance Lead + Compliance Officer co-approval |
| Require access reviews | Yes — quarterly |
| Reviewers | Current sponsor + Compliance Officer |
| On failure to review | Remove access |

!!! danger "Zone 3 — No Direct Permissions Outside Access Packages"
    For Zone 3 agents, all resource access must be assigned through entitlement management access packages. Information Security must verify periodically that Zone 3 agent identities have no direct SharePoint site permissions, no direct Graph API delegated permissions, and no Azure RBAC assignments outside the entitlement management framework. Exceptions require AI Governance Lead sign-off and must be documented with a compensating control.

### Step 4.3: Assign an Access Package to an Agent Identity

1. Navigate to the access package created in Step 4.1 or 4.2.
2. Select **Assignments**.
3. Select **Add assignment**.
4. In the **User** field, search for the agent identity. (Agent identities appear as non-human principals in the assignment workflow when Frontier is enabled.)
5. Set the assignment expiration date in accordance with the zone's maximum duration policy.
6. Select the approver flow is satisfied (for Zone 3, ensure both approvers have approved).
7. Select **Add**.
8. Verify the assignment appears in the Assignments list with the correct expiration date.

---

## Section 5: Configure Lifecycle Workflows for Sponsor Departure

Lifecycle workflows automate the governance response when an agent's sponsor departs the organization. This is the primary mechanism preventing orphaned agent identities in Zone 2 and Zone 3.

### Step 5.1: Create the Sponsor Departure Workflow

1. Navigate to **Identity Governance > Lifecycle workflows**.
2. Select **New workflow**.
3. Select the **Leaver** category (sponsor departure is a leaver event from the agent's perspective).
4. Configure the workflow:

    | Field | Value |
    |---|---|
    | Name | Agent Identity Sponsor Departure — Suspension and Reassignment |
    | Description | Triggers when an agent's assigned sponsor account is deactivated or marked as a leaver. Suspends the agent identity and creates a reassignment task for the AI Governance Lead. |
    | Trigger | Leaver — sponsor user account deactivated or marked inactive |

5. Select **Add task** and add the following tasks in order:

    | Task Order | Task | Target | Configuration |
    |---|---|---|---|
    | 1 | Send email notification | AI Governance Lead | Template: "Agent [AgentName] sponsor [SponsorName] has departed. Agent suspended pending reassignment. SLA: 5 business days." |
    | 2 | Disable agent identity | Agent identity | Immediately disable the agent account to prevent unapproved activity |
    | 3 | Create access review task | Compliance Officer | Initiate an ad-hoc access review for the affected agent |
    | 4 | Escalation notification (conditional — if no reassignment within 5 business days) | CISO / AI Governance Lead | Template: "Agent [AgentName] sponsor reassignment SLA breached. Immediate review required." |

6. Select **Save and enable**.

!!! warning "HR Connector Integration Required"
    For the leaver trigger to fire accurately and in a timely manner, the Entra lifecycle workflows must be connected to your organization's HR system (Workday, SAP SuccessFactors, or similar) via the Entra HR connector. Without this integration, the trigger relies on manual account deactivation in Entra, which may introduce delays. See the [Troubleshooting playbook](troubleshooting.md) — Section 2 for HR connector configuration guidance.

### Step 5.2: Test the Workflow (Dry Run)

Before relying on this workflow in production, perform a test using a non-production agent identity:

1. Navigate to **Identity Governance > Lifecycle workflows**.
2. Select the workflow created in Step 5.1.
3. Select **Run on demand**.
4. Select a test agent identity.
5. Select **Run**.
6. Navigate to **Workflow history** and verify:
    - The notification task completed successfully.
    - The agent identity was disabled.
    - The access review task was created.
7. Document the test execution in the governance log as evidence for examination readiness.

---

## Section 6: Configure Quarterly Access Certification Campaigns (Zone 3)

Access certification campaigns require named certifiers to actively attest that each Zone 3 agent's resource assignments remain appropriate. This is the primary ongoing certification evidence for SOX 404 and FINRA 3110 attestation.

### Step 6.1: Create the Zone 3 Quarterly Access Review

1. Navigate to **Identity Governance > Access reviews**.
2. Select **New access review**.
3. Configure the review:

    | Field | Value |
    |---|---|
    | Review name | Zone 3 Agent Access Certification — Quarterly |
    | Description | Quarterly certification that all Zone 3 AI agent resource assignments are appropriate, necessary, and compliant with least-privilege policy |
    | Scope | Access package assignments — Zone 3 agent access packages |
    | Reviewers | Agent sponsor (primary) + Compliance Officer (secondary) |
    | Duration | 14 days |
    | Recurrence | Quarterly |
    | If reviewers don't respond | Remove access |
    | Apply results | Automatically |

4. Select **Start**.

### Step 6.2: Export Certification Results for Examination Evidence

After each quarterly certification cycle completes:

1. Navigate to the completed access review.
2. Select **Download results**.
3. Export the CSV file containing: agent name, resource, certifier name, decision (approve/deny), decision date, and justification.
4. Archive this evidence file per the organization's six-year retention policy.
5. Note any denied or removed assignments in the quarterly AI Governance report.

---

## Section 7: Configure SIEM Log Forwarding for Lifecycle Events

### Step 7.1: Configure Entra Diagnostic Settings

1. Navigate to the **Microsoft Entra admin center**.
2. Select **Monitoring & health > Diagnostic settings**.
3. Select **Add diagnostic setting**.
4. Configure the following:

    | Field | Value |
    |---|---|
    | Diagnostic setting name | Agent Identity Lifecycle Events — SIEM |
    | Log categories to forward | AuditLogs, SignInLogs (filter to agent identity sign-ins) |
    | Destination | Log Analytics workspace (or Event Hub for SIEM ingestion) |

5. Select **Save**.

### Step 7.2: Apply Retention Policy

1. In the Log Analytics workspace (or SIEM), apply a data retention policy of **minimum 6 years** to the agent identity log stream.
2. Verify the retention policy is active by checking the workspace retention settings.
3. Document the retention policy configuration as examination evidence.

!!! note "Retention Cross-Reference"
    FINRA 4511 requires a minimum of six years for most books and records, with the first two years in an accessible (not offline-only) format. Ensure your SIEM retention architecture meets both the total duration and the accessibility requirements.

---

## Completion Checklist

Upon completing this playbook, verify the following:

- [ ] Frontier enrollment confirmed active; Agent identities blade visible in Entra admin center
- [ ] All Zone 2 and Zone 3 agents have a named individual sponsor assigned in Entra Agent ID Properties
- [ ] AI Agent Resources catalog created with all required resources added
- [ ] Zone 2 standard access package created with 365-day maximum duration
- [ ] Zone 3 standard access package created with dual-approver policy and quarterly access review
- [ ] All Zone 3 agents assigned to access packages (no direct permissions outside entitlement management)
- [ ] Sponsor departure lifecycle workflow created, enabled, and test-executed
- [ ] Quarterly access certification campaign created and scheduled for Zone 3
- [ ] SIEM log forwarding configured with six-year retention
- [ ] All configuration screenshots and evidence archived to governance file

---

[Back to Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: March 2026 | Version: v1.3*
