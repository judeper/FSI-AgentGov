# Control 2.3: Change Management and Release Planning — Portal Walkthrough

> Portal-based configuration guidance for [Control 2.3: Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
>
> **Audience:** Power Platform Admins and Pipeline Admins in US financial services organizations.

---

## Prerequisites

Before starting, confirm:

- **Roles:** Power Platform Admin (or Environment Admin on every target environment); Pipeline Admin on the pipelines host environment
- **Licensing:** Managed Environments enabled on every Zone 2 / Zone 3 environment that will participate in pipelines (target environments must be Managed)
- **Identity:** A dedicated **service principal** registered in Microsoft Entra ID for delegated deployments to Zone 3 production stages, with no interactive sign-in rights and credentials stored in a secrets vault
- **Solution publisher** configured in the development environment with a unique prefix (e.g., `fsi`) so solution components are identifiable in audit
- **Approver chain** documented per zone (Zone 2: manager or team lead; Zone 3: CAB member + Compliance Officer)
- **Source-control repository** designated to hold exported solutions and configuration snapshots

---

## Overview

This walkthrough configures, in order:

1. PPAC Deployment hub and pipeline settings
2. A pipelines host environment and pipeline stages (Dev → Test → Prod)
3. Delegated deployment under a service principal for Zone 3 Prod
4. A Power Automate approval flow on the `OnApprovalStarted` trigger
5. The Copilot Studio publishing approval workflow as a complementary native gate
6. Microsoft 365 Message Center monitoring as input to the change-management process

---

## Part 1: Open the PPAC Deployment Hub

The Power Platform Admin Center (PPAC) provides a dedicated **Deployment** section for pipeline administration, sometimes referred to as the *admin deployment hub*.

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com).
2. In the left navigation, select **Deployment**.
3. Review the sub-sections:
   - **Overview** — pipeline activity, pending approvals, failed deployments
   - **Pipelines** — list of all pipelines and their stages
   - **Settings** — tenant-level deployment settings (covered below)
   - **Catalogs** — solution catalogs (out of scope for this control)

> **Note (April 2026):** The Deployment hub layout was confirmed against the PPAC UI in April 2026. Microsoft has signaled minor reorganization through 2026 wave 1; if labels differ, search for "deployment" in PPAC.

---

## Part 2: Configure Tenant Deployment Settings

In **PPAC > Deployment > Settings**, review and configure the following:

| Setting | Description | FSI Recommendation |
|---------|-------------|--------------------|
| **Enable Auto-Conversion of Target Environments to Managed** | Automatically converts target environments to Managed when added to a pipeline stage | **Enable** for Zone 2 / Zone 3 tenants |
| **Solution deployments across regions** | Allows pipeline source and target to be in different Azure regions | Configure per data-residency policy; for US FSI, typically restrict to US regions |
| **Allow makers to import shared solution deployments** | Lets makers in target environments accept shared deployment artifacts | Enable for Team / Enterprise zones; document in change record |

> **Important:** Target environments in pipelines **must** be enabled as Managed Environments. Microsoft automatically enables Managed on environments you have already deployed to via pipelines, independent of the **Auto-Conversion** setting above. Auto-Conversion is an opt-in control that ensures *future* target environments are also converted on first use. See the [admin deployment hub guidance](https://learn.microsoft.com/en-us/power-platform/alm/admin-deployment-hub) for current behavior.

---

## Part 3: Create the Pipelines Host Environment

The pipelines host stores pipeline definitions and the deployment history. It is **not** a source or target — it is the control-plane environment.

1. In PPAC, select **Environments > New**.
2. Name: `FSI-Pipelines-Host` (or your tenant convention).
3. Type: **Production** (the host should be Production-class, even if it hosts only metadata).
4. Region: aligned with your data-residency policy.
5. **Add Dataverse:** required for pipelines.
6. Enable **Managed Environments** on the host.
7. Assign Pipeline Admins via **Settings > Users + permissions > Application users** or Dataverse security roles (`Deployment Pipeline Administrator`).

---

## Part 4: Define Pipeline Stages by Governance Zone

In PPAC, open **Deployment > Pipelines > New pipeline**, choose the host environment, then configure stages.

### Pipeline Configuration by Zone

| Zone | Pipeline Required | Stages | Approval Gates | Delegated Deployment |
|------|-------------------|--------|----------------|----------------------|
| Zone 1 | No | N/A | N/A | N/A |
| Zone 2 | Recommended | Dev → Prod (Test optional) | Manager (native or Power Automate) | Optional |
| Zone 3 | **Required** | Dev → Test → Prod | Multiple (CAB + Compliance) | **Required on Prod stage** |

### Stage Configuration Steps (Zone 3)

For each stage:

1. Select **Add stage**.
2. Provide a stage name (e.g., `Test`, `Prod`).
3. Select the **target environment** (must be Managed).
4. Configure **previous stage** so promotion order is enforced (Dev → Test → Prod).
5. Save the stage.

> **Note:** Pipelines enforce that a deployment to a later stage must originate from an earlier stage. This is a built-in promotion guardrail that supports the FFIEC IT Handbook expectation of separated Dev / Test / Prod environments.

---

## Part 5: Configure Delegated Deployment on Zone 3 Prod

Delegated deployment runs the import under a designated identity (service principal or pipeline owner) instead of the requesting maker, giving you maker/checker separation at the platform layer.

1. Open the Zone 3 pipeline in PPAC.
2. Select the **Prod** stage and choose **Edit**.
3. Toggle **Is Delegated Deployment** to **On**.
4. Choose the delegate type:
   - **Service principal** (recommended for Zone 3) — provide the Application (client) ID of the Entra app registration created for pipelines.
   - **Pipeline owner** — uses the identity that owns the pipeline; suitable for Zone 2 only.
5. Confirm the delegate has the `Deployment Pipeline Administrator` role on the host environment and the `System Administrator` Dataverse role on the target Prod environment.
6. Save the stage.

> **FSI Note:** The maker who requested the change must **not** be assigned the `System Administrator` role on the Prod environment. This is the control that enforces SOX 302/404 segregation of duties at deployment time. Document this assignment in your Written Supervisory Procedures.

See [Microsoft Learn: Deploy pipelines as a service principal or pipeline owner](https://learn.microsoft.com/en-us/power-platform/alm/delegated-deployments-setup) for current guidance.

---

## Part 6: Add a Power Automate Approval Gate

Approval gates use the pipelines extensibility events. For a Zone 3 production deployment, the typical pattern is:

| Trigger | When it fires | Use it for |
|---------|---------------|------------|
| `OnPreDeploymentStarted` | Before Solution Checker / pre-deployment validation | Block early on policy violations (e.g., wrong environment group) |
| `OnApprovalStarted` | When the deployment reaches the approval gate | Capture CAB and Compliance approvals; record approval evidence |

### Build the approval flow

1. Open [Power Automate](https://make.powerautomate.com) in the **pipelines host environment**.
2. Create a new **automated cloud flow**.
3. Trigger: **Power Platform for Admins (or "Pipelines") — When a deployment is requested (`OnApprovalStarted`)**.
4. Add an **Approvals — Start and wait for an approval** action:
   - Approval type: **Approve / Reject — Everyone must approve** (for CAB + Compliance) or **First to respond** for fast paths.
   - Assigned to: CAB distribution list and Compliance Officer (Zone 3); manager (Zone 2).
   - Title: include change ID, source environment, target environment, solution name, version.
   - Details: include change justification and link to the change record.
5. Branch on the response:
   - **Approved →** Call the pipelines connector to approve the deployment.
   - **Rejected →** Call the pipelines connector to reject and send a notification to the requestor.
6. Add a final action that writes the approval outcome (approver, timestamp, comments) to your audit store (Dataverse table, SharePoint list, or Sentinel via API).
7. Save and turn the flow **On**.

### Test the gate

1. From the Dev environment, request a deployment to Test.
2. Confirm the approval task is created in the approver's Power Automate Approvals.
3. Approve and verify the deployment proceeds.
4. Repeat with a rejection to verify the deployment is blocked and the requestor is notified.

See [Microsoft Learn: Extend pipelines with Power Automate](https://learn.microsoft.com/en-us/power-platform/alm/extend-pipelines) for trigger schemas.

---

## Part 7: Enable Copilot Studio Native Publishing Approvals (Zone 2)

For Zone 2 agents that publish directly without a pipeline, use the native approval workflow:

1. Open [Copilot Studio](https://copilotstudio.microsoft.com).
2. Select the agent and open **Settings**.
3. Navigate to **Security** > **Publish approval** (label may vary).
4. Toggle **Require approval to publish** to **On**.
5. Add designated approvers (manager or team lead).
6. Save.

> **Note:** Native publish approval is per-agent and is a complementary gate to pipeline approvals. For Zone 3 agents deployed via pipelines, pipeline approvals are authoritative; native publish approval is not required but may be enabled as a defense-in-depth control.

---

## Part 8: Configure Message Center Monitoring

Microsoft 365 Message Center surfaces platform changes that may invalidate agent behavior (deprecations, throttling changes, security updates).

### UI route (manual)

1. Open the [Microsoft 365 Admin Center](https://admin.microsoft.com).
2. Select **Health > Message center**.
3. Filter by service: **Microsoft Copilot**, **Power Platform**, **Power Automate**, **Dataverse**, **SharePoint**.
4. Tag relevant messages and assign owners.

### Programmatic route (recommended for Zone 3)

Use the Microsoft Graph **Service Communications API** to pull Message Center messages on a schedule and route relevant items into your change-intake queue. See the [PowerShell Setup](powershell-setup.md) playbook for the delta-query pattern, and the [Message Center Monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor) companion solution for a production-ready implementation.

---

## Part 9: Governance Zone Promotion Process

### Promotion Requirements

| Promotion | Requirements | Approvers | Documentation |
|-----------|--------------|-----------|---------------|
| **Zone 1 → Zone 2** | Business justification, basic testing, manager sign-off | Manager, Environment owner | Request form, test results |
| **Zone 2 → Zone 3** | Full risk assessment, security review, compliance review, performance test | CAB, Compliance Officer, Entra Security Admin | Full change package (see verification playbook) |
| **Within Zone 3 (Test → Prod)** | Pipeline run with approvals; pre-deployment Solution Checker pass | CAB + Compliance via Power Automate flow | Change record linked to deployment run |

### Zone 1 → Zone 2 Checklist

- [ ] Business justification documented
- [ ] Manager approval obtained
- [ ] Basic security review completed
- [ ] Target environment identified and Managed
- [ ] Solution exported from Zone 1 environment

> **Important:** Not all Copilot Studio agent components are captured in solution export. Custom topics packaged in the solution are exported; externally hosted knowledge sources, files referenced by URL, and tenant-level connector configurations are **not** part of the solution boundary. Verify all components are captured before promoting and maintain a parallel inventory of out-of-solution dependencies.

- [ ] Deployment plan created
- [ ] Rollback plan defined (link to prior managed solution)

### Zone 2 → Zone 3 Checklist

- [ ] All Zone 1 → Zone 2 requirements
- [ ] Risk assessment completed (model risk per OCC Bulletin 2026-13 (formerly OCC 2011-12) if applicable)
- [ ] Full security assessment by Entra Security Admin
- [ ] Compliance review (FINRA, SOX, GLBA scope confirmed)
- [ ] Performance and load testing completed
- [ ] User acceptance testing completed and signed off
- [ ] Production readiness checklist (Control 2.5 evidence)
- [ ] Monitoring plan defined (Control 3.x reporting)
- [ ] Support and incident procedures documented (Control 2.4)
- [ ] Delegated-deployment service principal configured on Prod stage

---

## Part 10: Change Classification and Approval Matrix

### Change Classification

| Change Type | Examples | Risk Level | Approval Path |
|-------------|----------|------------|---------------|
| **Emergency** | Security vulnerability (CVSS ≥ 7.0), regulatory mandate, customer-impacting outage | High | Expedited (see control doc Emergency Change Procedures) |
| **Major** | New functionality, architecture change, new connector, new knowledge source touching customer data | High | Standard CAB |
| **Standard** | Topic enhancement, prompt tuning, non-critical bug fix | Medium | Manager + Compliance review |
| **Minor** | Documentation, cosmetic updates, internal-only labels | Low | Self-service with logged change |

### Approval Matrix by Zone

| Change Type | Zone 1 | Zone 2 | Zone 3 |
|-------------|--------|--------|--------|
| Emergency | Self-service | Manager + Entra Security Admin | CAB + CISO + Compliance |
| Major | Self-service | Manager + Entra Security Admin | Full CAB |
| Standard | Self-service | Manager | Manager + Compliance |
| Minor | Self-service | Self-service (logged) | Manager (logged) |

---

## Validation

After completing the configuration, confirm:

1. [ ] Pipelines host environment created and accessible to Pipeline Admins
2. [ ] Pipeline stages defined (Dev → Test → Prod for Zone 3) with correct previous-stage chaining
3. [ ] Approval gates (native or Power Automate) configured for each stage requiring review
4. [ ] Delegated deployment configured on Zone 3 Prod stage with service principal identity
5. [ ] Target environments enabled as Managed Environments
6. [ ] Test deployment completes successfully through all stages
7. [ ] Approval notifications delivered to designated approvers and rejections block deployment
8. [ ] Deployment history visible in PPAC > Deployment > Overview
9. [ ] Message Center monitoring is in place (UI assignment or programmatic pull)
10. [ ] Configuration snapshots captured for at least one Zone 2-3 agent and committed to source control

**Expected Result:** Solutions deploy through governed pipelines with appropriate approval gates and delegated deployment for Zone 3, all deployment activity is logged in PPAC and the audit store, and Message Center change events are routed into the change-intake process.

---

## Related Playbooks

- [PowerShell Setup](powershell-setup.md) — Automation scripts for export/import, version management, snapshots, and Message Center polling
- [Verification & Testing](verification-testing.md) — Evidence collection, rollback drills, A/B testing
- [Troubleshooting](troubleshooting.md) — Common issues with pipelines, approvals, delegated deployments

[Back to Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
