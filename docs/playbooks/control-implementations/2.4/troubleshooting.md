# Control 2.4: Business Continuity and Disaster Recovery — Troubleshooting

> Common BC/DR issues and resolutions for [Control 2.4: Business Continuity and Disaster Recovery](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md).

---

## Audience

M365 administrators in US financial services responding to BC/DR issues during a live event, an exercise, or an examination response. Steps below assume the [Portal Walkthrough](portal-walkthrough.md) and [PowerShell Setup](powershell-setup.md) have been completed previously.

---

## Issue Index

| # | Symptom | Likely cause | Severity in event |
|---|---------|--------------|-------------------|
| 1 | DR environment out of sync with production | Sync pipeline failure or stale copy-environment job | Blocks failover |
| 2 | Connection failures in DR after failover | DR connection references not bound or service-account permissions missing in DR region | Blocks Tier 1 traffic |
| 3 | Customer-managed export pipeline failing | Service principal credential expired, Dataverse permissions changed, or Azure Storage RBAC drift | Blocks RPO compliance |
| 4 | Measured RTO exceeds target | Manual steps in runbook, slow approval chain, or under-provisioned DR environment | Examiner finding |
| 5 | Data integrity issues after restore | Solution export missing components (knowledge sources, custom topics) or hash mismatch | SEC 17a-4 reconstruction risk |
| 6 | Failback data conflicts | Concurrent writes in DR and primary during failover/failback overlap | Records integrity risk |
| 7 | Microsoft system backup not visible in PPAC | Environment recently migrated, region change, or temporary service issue | Operational only |
| 8 | Cross-region restore not offered | Microsoft does not provide native cross-region Dataverse restore | Architectural — confirms need for customer-managed exports |
| 9 | Entra Agent ID / service principal cannot authenticate to DR | Application user not registered in DR environment, or federated credential expired | Blocks Tier 1 traffic |
| 10 | Service Health alerts missed | Subscription routed to single mailbox, on-call rotation not on the DL, or Graph rate-limit on polling job | Detection delay |

---

## Issue 1 — DR Environment Out of Sync

**Symptoms:** DR agent version, environment variables, or solution components do not match production.

**Diagnosis:**

1. PPAC → DR environment → **Solutions** → compare solution **Version** and **Last installed** with production
2. Review the most recent ALM pipeline run or `Copy-PowerAppEnvironment` job log
3. Confirm service principal used by the sync job still has Dataverse System Administrator role in both environments

**Resolution:**

1. Run a fresh export from production using the [PowerShell Setup §4](powershell-setup.md#4-customer-managed-solution-export-to-immutable-storage) script (or `pac solution export ... --managed true`)
2. Import to DR using `pac solution import` or PPAC → **Import solution**
3. Re-apply DR-specific environment variable values (regional API endpoints, storage account names)
4. Re-bind connection references using DR-region service accounts
5. Add monitoring on the sync pipeline so failures alert the DR distribution list, not a single mailbox
6. If sync drift recurs, increase sync frequency (for Zone 3, the staleness budget is typically ≤ 24 hours)

---

## Issue 2 — Connection Failures in DR After Failover

**Symptoms:** Agents in the DR environment return errors when calling APIs, Dataverse tables, or premium connectors.

**Diagnosis:**

- Power Apps maker portal in DR → **Connections** → check connection status
- DR environment → **Connection references** → verify each reference is bound to a working connection
- Test the underlying connector with a one-step Power Automate flow

**Resolution:**

1. **Re-bind connection references**:
   - DR environment → **Solutions** → open solution → **Connection references** → for each, **Edit** and select the DR-region connection
2. **Verify service-account presence in the DR region**:
   - PPAC → DR environment → **Settings** → **Users + permissions** → **Application users** → confirm each agent identity is present and assigned the same Dataverse security role
3. **Validate network reachability**:
   - For VNet-integrated connectors, confirm the DR-region VNet integration gateway is provisioned
   - For ExpressRoute / private endpoint dependencies, verify routing to the DR region
4. **Refresh OAuth tokens**:
   - Some connectors require interactive re-consent in the DR region; capture this in the runbook so it does not block the next failover
5. **Smoke-test each connector** with a flow before declaring the failover complete

---

## Issue 3 — Customer-Managed Export Pipeline Failing

**Symptoms:** Scheduled solution or data export jobs are not landing in the immutable Azure Blob container; RPO at risk.

**Diagnosis:**

- Azure DevOps / GitHub Actions / Azure Automation run history — identify the failing step
- Confirm the service principal still has:
  - Dataverse System Administrator (or equivalent) on the source environment
  - Storage Blob Data Contributor on the target Storage Account / container
- Check Azure Blob immutability policy — once locked, version-level immutability cannot be reduced; ensure the policy hasn't drifted from the documented baseline

**Resolution:**

1. **Renew or rotate service principal credentials**; prefer **federated credentials** (workload identity federation) to avoid manual secret rotation
2. **Reapply RBAC** on both Dataverse (application user role) and Storage (Storage Blob Data Contributor on the container)
3. **Validate immutability policy** is `enabled` and the retention period meets the documented requirement (typically ≥ 6 years for SEC 17a-4)
4. **Test manual export** via [PowerShell Setup §4](powershell-setup.md#4-customer-managed-solution-export-to-immutable-storage); compare SHA-256 against a prior known-good export
5. **Open a CAB ticket** documenting the failure window, the gap against RPO, and remediation; this becomes part of the next exercise evidence

---

## Issue 4 — Measured RTO Exceeds Target

**Symptoms:** Exercise documentation shows tier RTO not met; examiner finding likely.

**Diagnosis:**

- Review exercise timestamps phase-by-phase
- Identify steps that took longer than the runbook target
- Check whether delays were process (waiting for approval), technical (slow re-binding), or organizational (on-call manager unavailable)

**Resolution:**

1. **Streamline the runbook**: pre-authorize tier-specific declaration so the on-call manager does not wait for executive approval inside the RTO window
2. **Pre-stage in DR**: keep the DR environment within the staleness budget so import time at failover is zero
3. **Automate the cutover**: script DNS / Front Door / channel publish changes; manual portal clicks are the most common time sink
4. **Pre-bind DR connection references** during steady-state with a "shadow" identity that is dormant until failover; activate at failover rather than re-bind
5. **Up-tier DR capacity** (capacity add-ons) if cold start of the DR environment causes user-visible latency
6. **Increase exercise frequency** so the team is practiced; FFIEC examiners view this favorably
7. **Document the RTO miss in the BIA** as a known constraint and adjust either the RTO target (with BCP committee approval) or the architecture

---

## Issue 5 — Data Integrity Issues After Restore

**Symptoms:** Restored agent has missing knowledge sources, missing topics, or returns "configuration not found" errors.

**Diagnosis:**

- Compare the restored solution component count with the source export manifest
- Verify the SHA-256 hash of the restored `.zip` against the hash sidecar from immutable storage
- Confirm whether the missing component is a **solution-aware** component (covered by export) or a **non-solution-aware** component (knowledge source, certain custom topics)

**Resolution:**

1. **Hash mismatch** → restore from a different known-good export and re-verify; investigate the storage account integrity
2. **Solution component missing** → the source export was incomplete; review the export script and its solution component selection
3. **Knowledge source missing** → invoke the documented secondary export procedure for non-solution-aware components; this is a known limitation of solution export and must be addressed by separate backup procedure
4. **Environment variable values missing** → restore environment variable values from the documented DR variable set, not from the production export (the values typically differ per region)
5. **Document any reconstruction effort** for the regulatory record — this matters for SEC 17a-4 reconstruction obligations

---

## Issue 6 — Failback Data Conflicts

**Symptoms:** After failback to primary, conflicting records exist in primary and DR; users see stale or duplicate data.

**Diagnosis:**

- Identify the DR operating window (failover declaration → failback declaration)
- Inventory tables that received writes during the window
- For each conflicting row, determine source-of-truth (DR is typically authoritative for the operating window)

**Resolution:**

1. **Document the DR operating window** with start and end timestamps
2. **Export DR state** before failback (managed solution + relevant Dataverse table snapshots)
3. **Reconcile in primary**:
   - For low-volume tables, manual merge by Dataverse System Admin
   - For high-volume tables, use a Power Automate or Azure Synapse Link reverse-sync flow
4. **Consider "DR becomes primary"** if the operating window was long or the merge cost exceeds the value of returning to the original primary; in this case, update DNS / endpoint configuration permanently and rebuild the old primary as the new DR
5. **Capture the reconciliation in the post-event report** under [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) for examiner traceability

---

## Issue 7 — Microsoft System Backup Not Visible in PPAC

**Symptoms:** PPAC → Environment → **Backups** shows no system backups for the past 24 hours.

**Diagnosis:**

- Check Microsoft 365 Service Health for active Dataverse advisories
- Confirm the environment was not recently migrated, restored, or had its region changed (these can briefly suppress visible system backups)

**Resolution:**

1. Wait 24 hours and re-check; system backups are continuous and gaps usually self-heal
2. Trigger a **manual backup** in the interim ([PowerShell Setup §2](powershell-setup.md#2-trigger-and-verify-a-manual-dataverse-backup)) so the change window is not blocked
3. If the gap persists more than 48 hours, open a Microsoft support case (severity B for production)
4. Document the gap in the BIA risk log so the next exercise references it

---

## Issue 8 — Cross-Region Restore Not Offered

**Symptoms:** PPAC restore dialog only offers in-region restore; DR-region restore is not an option.

**Cause:** This is the documented Microsoft platform behavior — Microsoft does **not** provide native cross-region Dataverse restore. System backups are tied to the source region.

**Resolution (architectural, not a defect):**

1. Confirm the customer-managed export-to-Blob pipeline is the recovery path for cross-region scenarios
2. Confirm a secondary-region environment is pre-provisioned per [Portal Walkthrough §2](portal-walkthrough.md#part-2-provision-and-harden-the-secondary-region-environment)
3. Confirm solution import to the DR environment is part of the runbook, not a system-backup restore
4. Document this Microsoft platform behavior in the BIA so examiners understand the customer-side controls that compensate

---

## Issue 9 — Entra Agent ID / Service Principal Cannot Authenticate to DR

**Symptoms:** Token acquisition succeeds against Entra, but Dataverse calls in the DR environment return `401` or `Forbidden`.

**Diagnosis:**

- Use [PowerShell Setup §6](powershell-setup.md#6-smoke-test-the-dr-environment) `WhoAmI` smoke test
- PPAC → DR environment → **Settings** → **Users + permissions** → **Application users** → search for the app's `appId`
- Microsoft Entra admin center → confirm federated credential or client secret is valid

**Resolution:**

1. **App user missing in DR** → register the application user in the DR environment with the same Dataverse security role assigned in production
2. **Credential expired** → rotate credential per the documented rotation procedure; prefer federated credentials for unattended workloads
3. **API permission scope mismatch** → confirm the application has the same Graph / Dataverse delegated and application permissions; admin-consent in DR if a tenant-scoped consent record is required
4. **Conditional Access blocking** → confirm the DR environment URL is included in the Conditional Access named-locations and policies that target the agent's identity

---

## Issue 10 — Service Health Alerts Missed

**Symptoms:** A Microsoft Power Platform / Dataverse advisory was published but the DR team did not receive it in time.

**Diagnosis:**

- Microsoft 365 admin center → **Service health** → confirm the advisory was published
- Verify the alert subscription audience (must be a distribution list, not a single mailbox)
- Confirm the on-call rotation includes membership in the DL

**Resolution:**

1. **Re-subscribe to a distribution list** that the on-call rotation belongs to
2. **Add Teams channel notifications** by routing the Graph `Get-MgServiceAnnouncementMessage` output ([PowerShell Setup §7](powershell-setup.md#7-subscribe-to-service-health-alerts-via-graph)) to a Teams DR channel
3. **Add a daily digest job** so missed real-time notifications are caught within 24 hours
4. **Document detection time** as a separate SLA in the BIA — detection delay is part of the total RTO

---

## Escalation Path

If issues cannot be resolved using this guide:

| Level | Role | When to engage |
|-------|------|----------------|
| 1 | IT Operations | Pipeline failures, automation errors, runbook execution support |
| 2 | Power Platform Admin | Environment configuration, Managed Environment policy, capacity issues |
| 3 | Entra Agent ID Admin | Identity / federated credential issues affecting DR authentication |
| 4 | AI Governance Lead | Process, scope, runbook accuracy, exercise findings |
| 5 | Compliance Officer | Examiner inquiries, regulatory recordkeeping concerns |
| 6 | Microsoft Support | Confirmed platform-level incidents (open Sev B for production) |

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md) — Step-by-step portal configuration
- [PowerShell Setup](powershell-setup.md) — Automation scripts
- [Verification & Testing](verification-testing.md) — Test procedures and exercise scenarios

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
