# Control 2.3: Change Management and Release Planning — Troubleshooting

> Troubleshooting guidance for [Control 2.3: Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
>
> **Audience:** Power Platform Admins, Pipeline Admins, AI Governance Lead.

---

## Quick Reference

| Symptom | Likely Cause | First Action |
|---------|--------------|--------------|
| Pipeline deployment fails with "Access denied" | Missing role on target | Verify user / service principal has `System Administrator` (Dataverse) on target |
| Solution import conflicts ("Component already exists") | Unmanaged customizations in target | Enable **Overwrite Unmanaged Customizations** on import |
| Approval stuck in pending | Approver did not receive notification | Check Power Automate flow runs and approver mailbox / Teams |
| Version mismatch after deploy | Multiple solutions with same uniquename | Use unique publisher prefix; verify `uniquename` matches |
| Rollback fails — previous version missing | No backup retained | Implement export-on-deploy and verify retention policy |
| Delegated deployment fails | Service principal lacks roles or consent | See "Delegated Deployment Issues" below |
| Pipeline not visible to maker | Not assigned to the pipeline | Add user to pipeline in host environment |
| Message Center delta query returns 401 | Missing Graph permission | Grant `ServiceMessage.Read.All` and consent |

---

## Detailed Troubleshooting

### Pipeline not visible in Power Apps

**Symptoms:** Makers cannot see or access configured pipelines from the Power Apps maker portal.

**Steps to resolve:**

1. Verify the user is assigned to the pipeline in the host environment (PPAC > Pipelines > select pipeline > Users)
2. Confirm the source environment is added to a pipeline stage as a valid source
3. Confirm the user has at least the **Basic User** Dataverse security role in the source environment
4. Refresh the Power Apps browser session (sign out and back in if needed)
5. Confirm the pipelines host environment is reachable from the user's region (data-residency restrictions can block visibility)

---

### Solution export fails with missing dependencies

**Symptoms:** Export fails with a dependency error referencing components not in the solution.

**Steps to resolve:**

1. Run **Solution Checker** in the maker portal before export
2. Identify missing dependencies in the error detail
3. Add the dependent components to the solution, or ensure the dependent solution is present in the target
4. Use the **Export including required components** option if dependencies should travel with the solution
5. Review the dependency graph in the maker portal (Solution > Dependencies)

---

### Managed solution cannot be modified in target

**Symptoms:** Components cannot be edited after importing a managed solution.

**Explanation:** This is the intended behavior — managed solutions enforce that changes flow from the development environment through the pipeline. This protection supports SOX 302/404 segregation of duties.

**Resolution:**

1. Make all changes in the unmanaged source environment
2. Re-export and re-import the updated managed solution through the pipeline
3. Avoid "holding solutions" or unmanaged overrides in production; they create unmanaged customizations that future imports must overwrite, undermining the audit trail

---

### Environment routing conflicts with pipeline targets

**Symptoms:** Agents or solutions deploy to unexpected environments.

**Steps to resolve:**

1. Verify Environment Routing rules (Control 2.15) do not redirect pipeline targets
2. Confirm the pipeline target matches the agent's assigned governance zone
3. Review environment group membership and routing priorities
4. Coordinate with the Power Platform Admin to align routing rules and pipeline configuration

---

### Approval workflow not triggering

**Symptoms:** A pipeline deployment proceeds without waiting at the expected approval gate.

**Steps to resolve:**

1. Confirm the Power Automate flow uses the **`OnApprovalStarted`** trigger (not a generic approval action)
2. Verify the flow is **On** in the pipelines host environment
3. Confirm the connection used by the flow is valid (Power Automate > Connections); re-authenticate if expired
4. Check the flow run history for trigger receipts; if none, the pipeline event is not reaching Power Automate
5. Confirm the approver(s) have the licensing required to receive Approvals
6. Inspect the pipeline stage configuration — approval gates are stage-scoped and must be enabled per stage

---

### Solution Checker errors blocking deployment

**Symptoms:** Pipeline fails at the Solution Checker stage.

**Steps to resolve:**

1. Open Solution Checker results in the maker portal
2. Address **Critical** and **High** severity findings (these block deployment by default)
3. For **Medium** / **Low** findings that are accepted, document the rationale in the change record and an exception register
4. Re-run Solution Checker to confirm fixes
5. If a rule is consistently inappropriate for your context, work with the AI Governance Lead before excluding it; record the justification

---

### Cross-region deployment failures

**Symptoms:** Deployment fails when source and target environments are in different Azure regions.

**Steps to resolve:**

1. Verify **Solution deployments across regions** is enabled in PPAC > Deployment > Settings
2. Confirm data-residency policy permits the cross-region deployment (US FSI tenants typically restrict to US regions)
3. Test connectivity between regions
4. As a workaround, perform an export / import outside the pipeline if cross-region pipelines are restricted

---

### Version number not incrementing

**Symptoms:** Multiple deployments show the same solution version.

**Steps to resolve:**

1. Confirm the version is updated **in the source environment** before export
2. Check that your version-management script (see PowerShell Setup) is running and authenticated
3. If automation failed, manually update the version using `Set-FsiSolutionVersion`
4. Audit recent pipeline runs for build-version drift and reconcile

---

## Delegated Deployment Issues

### Symptom: "The principal does not have permission to perform this action" on Prod stage

**Likely causes and fixes:**

1. The service principal lacks the `System Administrator` Dataverse role on the **target** environment.
   - Fix: PPAC > Environments > target > Settings > Users + permissions > Application users; add the service principal and assign `System Administrator`.
2. The service principal lacks the `Deployment Pipeline Administrator` role on the **host** environment.
   - Fix: assign the role on the pipelines host environment.
3. Admin consent for the Entra app registration was not granted at the tenant level.
   - Fix: Entra admin center > App registrations > select app > API permissions > **Grant admin consent**.

### Symptom: Approval flow approves but delegated import never starts

**Steps to resolve:**

1. Check the pipeline run state in PPAC > Deployment > Overview
2. If the run is "Awaiting deployment" with the delegated identity, confirm the service principal's secret has not expired (Entra > App registrations > Certificates & secrets)
3. Rotate the secret if expired and update the secrets vault entry referenced by your automation
4. Re-trigger the deployment

### Symptom: Audit logs do not show the service principal as the deploying identity

**Steps to resolve:**

1. Confirm **Is Delegated Deployment** is **On** for the stage (PPAC > Pipelines > Stage)
2. Confirm the delegate type and ID are correct
3. If the stage shows "Off", the deployment ran under the requesting maker — this **breaks** the SOX 302/404 segregation-of-duties control and must be remediated before the next change

---

## Rollback-Specific Issues

### Cannot find the previous solution version

**Symptoms:** Rollback is needed but no backup exists.

**Steps to resolve:**

1. Check the artifact storage location defined in your retention policy
2. Search for solution exports with timestamps and matching uniquename
3. Check whether the target environment retained the prior solution layer (PPAC > Environment > Solutions > select solution > **Layers**)
4. If only the active layer remains, you cannot roll back via re-import; you must replay the change in reverse via the standard pipeline
5. Open a remediation item: implement export-on-deploy and verify retention before the next change

### Rollback causes data conflicts

**Symptoms:** Importing the prior managed solution conflicts with data created by the newer version.

**Steps to resolve:**

1. Inventory data changes made since the original deployment
2. Export affected data before rollback
3. Plan a data migration strategy post-rollback
4. If data impact is high, evaluate a forward-fix instead of rollback (deploy a hotfix that resolves the issue without reverting)

---

## Message Center / Service Communications API Issues

### Symptom: `401 Unauthorized` on `/admin/serviceAnnouncement/messages`

**Steps to resolve:**

1. Confirm the application or delegated permission `ServiceMessage.Read.All` is granted
2. Confirm tenant admin consent has been granted for the permission
3. For app-only contexts, confirm the Graph access token includes the permission as an `roles` claim (delegated tokens use `scp`)

### Symptom: `429 Too Many Requests`

**Steps to resolve:**

1. Implement exponential back-off and respect the `Retry-After` header
2. Use **delta queries** instead of full pulls — store the `@odata.deltaLink` between runs
3. Reduce poll frequency; Message Center messages are not real-time and a 1-hour cadence is typically sufficient

### Symptom: Delta query returns the same set repeatedly

**Steps to resolve:**

1. Confirm the `@odata.deltaLink` is being persisted and re-used on the next run
2. If the state file is empty or invalid, the query falls back to a full pull
3. Validate the state file is written with `ascii` encoding (some systems add a BOM that breaks the URL)

---

## Pre-Existing Personal Pipelines

**Symptom:** The organization has personal pipelines created outside centrally governed hosts that need cleanup before enforcing pipeline governance policies.

**Background:** When Power Platform pipelines were first enabled, makers may have created personal pipelines in various environments. Enforcing a centralized pipelines-host policy requires identifying and cleaning up these legacy pipelines.

**Resolution:**

1. **Assess scope** — query the `DeploymentPipeline` Dataverse table across environments
2. **Notify owners** — give pipeline owners 30-60 days before deactivation
3. **Execute cleanup** — deactivate non-compliant pipelines after the deadline
4. **Enforce policy** — link environments to the designated pipelines host

For a production-ready implementation, see the [Pipeline Governance Cleanup Solution](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup) in the FSI-AgentGov-Solutions repository.

---

## Out-of-Solution Components

**Symptom:** After importing a Copilot Studio agent solution, the agent behaves differently than in source.

**Likely cause:** Components stored outside the solution boundary were not included in export.

**Steps to resolve:**

1. Inventory components that are commonly out-of-solution:
   - Externally hosted knowledge sources (URLs, file shares)
   - Tenant-level connector configurations and connection references
   - Files referenced by URL rather than uploaded
   - Some preview features not yet integrated with the solution framework
2. For each, document the configuration in a parallel inventory tied to the change record
3. Re-create or re-link the configuration in the target environment as part of the change
4. Add post-deployment validation steps that confirm out-of-solution components are present and correctly configured

---

## Escalation Path

If issues cannot be resolved using this guide:

1. **Level 1 — Power Platform Admin** — technical configuration, pipeline behavior
2. **Level 2 — Pipeline Admin / AI Governance Lead** — process and approval workflow issues
3. **Level 3 — Compliance Officer** — regulatory impact, evidence gaps
4. **Level 4 — Microsoft Support** — product-level issues, with a support ticket from a tenant admin

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md) — PPAC and Copilot Studio configuration
- [PowerShell Setup](powershell-setup.md) — Automation scripts
- [Verification & Testing](verification-testing.md) — Evidence collection and rollback drills

---

*Updated: April 2026 | Version: v1.6.2*
