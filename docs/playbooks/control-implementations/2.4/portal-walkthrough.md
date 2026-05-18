# Control 2.4: Business Continuity and Disaster Recovery — Portal Walkthrough

> Portal-based configuration guidance for [Control 2.4: Business Continuity and Disaster Recovery](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md).

---

## Audience and Scope

This walkthrough is for **M365 administrators** in US financial services who configure Power Platform business continuity and disaster recovery (BC/DR) for Microsoft Copilot Studio agents. It covers customer-managed steps in the Power Platform Admin Center (PPAC), Power Apps maker portal, Microsoft 365 admin center, and Microsoft Entra admin center as of **April 2026**. It does **not** cover Microsoft-side platform recovery, which is governed by the Online Services Terms and SLA.

!!! warning "Microsoft does not auto-failover Dataverse cross-region"
    Microsoft maintains in-region high availability for Dataverse and Copilot Studio. **Cross-region recovery is the customer's responsibility** and requires a pre-provisioned secondary-region environment, customer-managed solution and data exports, and a documented runbook. The steps below operationalize that responsibility.

---

## Prerequisites

Before starting, confirm you have:

- **Power Platform Admin** role (canonical role from `docs/reference/role-catalog.md`) — required for environment provisioning, manual backup, copy-environment operations, and tenant deployment settings
- **Environment Admin** on the source production environment and the target DR environment — required to manage DLP exemptions, security roles, environment variables, and connection references
- **Microsoft 365 Service Health Reader** (or Global Reader) for at least one named admin account, plus an admin distribution list — required for Service Health and Message Center subscriptions
- **Entra Agent ID Admin** (where Entra Agent ID is enabled) — required to confirm agent identity continuity in the DR environment
- An approved Business Impact Analysis (BIA) listing the agents in scope, their criticality tier, and board-ratified RTO / RPO targets — see [Control 2.4 §Zone-Specific Requirements](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md#zone-specific-requirements)
- An identified secondary Azure region in the same regulatory geography as your primary region (for example: East US ↔ West US, or North Europe ↔ West Europe). Confirm the secondary region against [Azure regions for Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/regions-overview)

---

## Overview

This walkthrough follows the customer-side BC/DR lifecycle for Copilot Studio agents:

| Part | Activity | Owner |
|------|----------|-------|
| 1 | Classify agents and ratify RTO / RPO in the BIA | AI Governance Lead |
| 2 | Provision and harden the secondary-region environment | Power Platform Admin |
| 3 | Confirm Microsoft system backups and configure manual backups | Power Platform Admin |
| 4 | Configure customer-managed solution and data exports | Power Platform Admin |
| 5 | Validate agent identity continuity in the DR environment | Entra Agent ID Admin |
| 6 | Subscribe to Service Health and Message Center alerts | Power Platform Admin |
| 7 | Author the DR runbook (declaration, failover, failback) | AI Governance Lead |
| 8 | Schedule and document recovery exercises | Compliance Officer |

---

## Part 1 — Classify Agents and Ratify RTO / RPO

The BIA is the source of truth for which agents enter scope, what their tier is, and what their RTO / RPO targets are. The portal does not store this — it is a governance artifact maintained alongside the firm's BCP.

For each agent, capture in the BIA:

- Agent display name and Copilot Studio bot ID
- Hosting environment (production environment ID + region)
- Business owner and recovery owner
- Criticality tier (1 / 2 / 3 / 4) per [Control 2.4 §Agent Criticality Classification](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md#agent-criticality-classification)
- RTO and RPO ratified by the BCP committee
- Dependencies: knowledge sources, custom connectors, environment variables, downstream APIs, identity (service principal / Entra Agent ID), Power Automate flows
- Recovery priority order within the tier

Cross-reference the agent inventory maintained under [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).

---

## Part 2 — Provision and Harden the Secondary-Region Environment

**Portal path (April 2026):** Power Platform Admin Center → **Resources** → **Environments** → **+ New**

### 2.1 Create the DR environment

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com) and sign in with a Power Platform Admin account
2. Select **Resources** → **Environments** → **+ New**
3. Configure:
   - **Name:** `<PrimaryEnvName>-DR`
   - **Region:** the pre-approved secondary region for the primary's geography
   - **Type:** **Production** (Tier 1 / Tier 2) or **Sandbox** (Tier 3 internal-only agents — note that sandbox and non-Managed production environments both default to 7-day backup retention; enable Managed Environments on production to access 28-day extended retention)
   - **Add a Dataverse data store:** **Yes**
   - **Currency / Language:** match the primary environment
   - **Security group:** apply the same restricted security group used in production
4. Select **Save** and wait for provisioning to complete

### 2.2 Enable Managed Environments and apply parity policies

1. Select the new DR environment → **Settings** → **Product** → **Features**
2. Enable **Managed Environment** (required for any environment hosting Zone 2 or Zone 3 agents — see [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md))
3. Apply the same DLP policies that govern the primary environment: **Policies** → **Data policies** → assign the DR environment to the same policy scopes
4. Reproduce in the DR environment:
   - Security roles and team memberships
   - Environment variables (values appropriate for the DR region — for example, regional API endpoints)
   - Connection references (placeholder; will be re-bound during failover)
   - Conditional Access targeting the DR environment URL

!!! tip "Document the region pairing in your BCP"
    Record the primary ↔ DR mapping in the BIA, not just inside PPAC. Examiners look for documented region pairing decisions, including the data-residency rationale.

---

## Part 3 — Confirm Microsoft System Backups and Configure Manual Backups

**Portal path (April 2026):** Power Platform Admin Center → **Resources** → **Environments** → `<env>` → **Settings** → **Updates** → **Backup & restore** (or the **Backups** action on the environment command bar)

### 3.1 Verify system backups

1. Open the production environment in PPAC
2. From the command bar, select **Backups**
3. Confirm:
   - **System backups** are present and current — by default backups are retained for **7 days for all environment types**; production Managed Environments with extended retention enabled show backups spanning up to **28 days**. Confirm which applies to this environment before setting RPO targets that rely on system-backup recovery.

   - The most recent system backup timestamp is current

System backups support Microsoft-side recovery for in-region events. Within a region, the platform targets approximately near-zero RPO and recovery in under five minutes (per the [Power Platform BCDR FAQ](https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery), May 2026). System backups restore the **entire environment**, not individual agents or solutions, and are not portable cross-region.

### 3.2 Create a manual backup before any high-risk change

1. From the **Backups** view select **Create**
2. Enter a **Label** describing the change (for example, `Pre-deploy TradingAssistant 4.2.0`)
3. Select **Create**
4. Manual backups of production Managed Environments with extended retention enabled are kept up to **28 days**; all other environments retain manual backups for **7 days** by default. Verify current retention for this environment against [Backup and restore environments](https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments) before relying on a specific window.

### 3.3 Restore drill (sandbox only — never on production without a change ticket)

1. Open a non-production environment in PPAC
2. Select **Backups** → choose a system or manual backup → **Restore**
3. Choose **Restore over an existing environment** (sandbox target) or **Restore to a new environment**
4. Record the start and finish times in the exercise log — this measures Microsoft-side restore time as one input to RTO

---

## Part 4 — Configure Customer-Managed Solution and Data Exports

System backups alone do not satisfy SEC 17a-4 reconstruction obligations and do not support cross-region recovery. Customer-managed exports are mandatory for Zone 2 and Zone 3.

### 4.1 Solution exports (managed)

**Portal path:** Power Apps maker portal → **Solutions** → select solution → **Export solution**

1. Open [Power Apps](https://make.powerapps.com) in the production environment
2. Select **Solutions** → choose the solution containing the agent
3. Select **Export solution** → **Publish** all customizations → **Next**
4. Choose **Managed** → set **Version** following the [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) versioning convention
5. **Export** and save the `.zip` to immutable / WORM-capable storage (Azure Blob with immutability policy, or equivalent)
6. Repeat per the cadence required by the agent's RPO target

!!! warning "Solution export does not capture every Copilot Studio component"
    Knowledge sources, certain custom topics, and external data referenced by the agent may not be inside the solution package. Verify component coverage before relying on the export for full recovery. Maintain separate export procedures for excluded components and document them in the runbook.

### 4.2 Dataverse data exports

For agents that read or write Dataverse tables containing records subject to retention:

1. Use **Azure Synapse Link for Dataverse** (PPAC → Environment → **Azure Synapse Link**) for continuous near-real-time replication to ADLS Gen2, **or**
2. Use the Dataverse Web API / Dataflows for scheduled batch exports

Store outputs in immutable storage with a retention period meeting the longest of: SEC 17a-4 (six years for most records), FINRA 4511, and any applicable state regulation.

### 4.3 Pre-stage solutions in the DR environment

1. In the DR environment, **Solutions** → **Import solution**
2. Import the latest managed solution
3. Bind connection references to DR-region connections (will be re-validated at failover)
4. Verify environment variables resolve to DR-appropriate values

Refresh the DR environment on a schedule that keeps it within the RPO window — for Zone 3, this typically means daily at minimum and ideally automated via Power Platform pipelines (see [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)).

---

## Part 5 — Validate Agent Identity Continuity

Entra app registrations, service principals, federated credentials, and Entra Agent IDs are **tenant-global** — they are not bound to a Power Platform region and survive a single-region outage without re-registration. Validation focuses on confirming that the DR environment can authenticate **using** them.

**Portal path:** Microsoft Entra admin center → **Identity** → **Applications** → **App registrations**

1. For each app registration or Agent ID used by an in-scope agent, confirm:
   - The application is **multi-tenant or single-tenant** consistent with the primary
   - **Federated credentials** (workload identity federation) are present and not expired
   - **Client secrets** are stored in a Key Vault that is itself replicated cross-region (Azure Key Vault is region-paired by default)
   - **API permissions** include any Graph or Dataverse scopes the agent uses
2. In the DR Power Platform environment, register the application user (Power Platform Admin Center → DR environment → **Settings** → **Users + permissions** → **Application users** → **+ New app user**)
3. Assign the same Dataverse security role used in production
4. Document the credential rotation owner and cadence in the BIA

---

## Part 6 — Subscribe to Service Health and Message Center Alerts

**Portal path:** Microsoft 365 admin center → **Health** → **Service health** → **Customize alerts**

1. Open [Microsoft 365 admin center](https://admin.microsoft.com) → **Health** → **Service health**
2. Select **Customize alerts** → **Add a new rule**
3. Subscribe a **DR distribution list** (not a single inbox) to alerts for:
   - Power Platform
   - Dynamics 365 (covers Dataverse advisories)
   - Copilot Studio
   - Microsoft Entra
   - Power Automate
4. Repeat for **Message Center** under **Health** → **Message center** → **Preferences** → enable email digest for the same audiences
5. Document the notification matrix in the runbook:

| Severity | Initial response | Escalation channel |
|----------|------------------|--------------------|
| Critical (active outage affecting Tier 1) | Immediate | DR bridge call + executive notification |
| High (degraded service for Tier 1 / Tier 2) | ≤ 15 minutes | Teams DR channel + email |
| Medium (advisory affecting future operations) | ≤ 1 hour | Email |
| Informational | Next business day | Digest |

---

## Part 7 — Author the DR Runbook

The runbook is a controlled document maintained alongside the BCP. It should be version-controlled, reviewed at least annually, and approved by Compliance.

### 7.1 Declaration criteria

Document the conditions that authorize a DR declaration. Examples:

- Microsoft confirms a regional service incident affecting the primary Power Platform region with no ETA, **or** the incident exceeds the agent's RTO
- Tier 1 agent is unavailable for more than 30 minutes with no in-region resolution path
- Security incident requires isolation of the primary environment

### 7.2 Declaration authority

| Role | Authority |
|------|-----------|
| CIO or delegate | Tier 1 declaration |
| IT Operations Director | Tier 2 declaration |
| On-call IT Manager | After-hours declaration with mandatory CIO notification |

### 7.3 Tier 1 failover sequence (target ≤ 60 minutes)

1. **Declare** (≤ 5 min): On-call manager confirms criteria, opens incident ticket, notifies leadership distribution list
2. **Validate DR readiness** (≤ 10 min): Confirm DR environment status, latest solution version present, application users active
3. **Re-bind connections** (≤ 15 min): Update connection references in DR to live credentials; refresh OAuth tokens for premium connectors
4. **Cut over traffic** (≤ 10 min): Update Azure Front Door / Traffic Manager / Teams app endpoint / channel publish targets to point at the DR agent
5. **Smoke test** (≤ 15 min): Execute the agent test script (see [Verification & Testing](verification-testing.md)) and validate critical flows
6. **Communicate** (≤ 5 min): Notify business owners and users; update status page; log declaration time and recovery time

### 7.4 Failback sequence

1. Confirm primary region is stable (Microsoft all-clear posted; no further service health advisories)
2. Inventory data and configuration changes made in the DR environment during the outage
3. Export modified solutions and any Dataverse data changes from DR
4. Import to the primary environment and reconcile conflicts
5. Cut traffic back to primary; place DR back into warm-standby state
6. File post-event report (see [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md))

---

## Part 8 — Schedule and Document Recovery Exercises

**Cadence:** Annual for Zone 2; quarterly for Zone 3 (mix of tabletop and live failover).

### 8.1 Pre-exercise (≥ 2 weeks ahead)

- Schedule the exercise window with all participants and notify business owners
- Define the scenario (regional outage, tenant-wide auth failure, malicious deletion of an agent, etc.)
- Confirm the success criteria (RTO / RPO met, runbook accurate, no undocumented dependencies)
- Brief the DR team and assign an exercise observer

### 8.2 Exercise execution

- Follow the runbook exactly — observers note any deviation, ambiguity, or undocumented step
- Capture timestamps for each phase
- Document any data integrity issues found post-failover

### 8.3 Post-exercise documentation (retain ≥ 6 years)

- Exercise summary (scenario, scope, participants, observer)
- Measured RTO and RPO vs. target
- Gaps and corrective actions tracked to closure with owners and dates
- Compliance Officer sign-off

This evidence supports FFIEC examination, FINRA 4370 review, and OCC Heightened Standards (Appendix D) independent assurance.

---

## Validation

After completing all parts, confirm:

1. The BIA lists every Zone 2 and Zone 3 agent with tier, RTO, RPO, dependencies, and recovery owner
2. A secondary-region environment exists for each Zone 3 production environment with parity policies and current solutions
3. Manual and system backups are visible in PPAC for all in-scope production environments
4. Customer-managed solution exports are landing in immutable storage on the cadence required by RPO
5. Application users for agent identities are registered in the DR environment with the same Dataverse roles
6. Service Health and Message Center alerts route to the DR distribution list, not a single mailbox
7. The DR runbook is published, version-controlled, and approved by Compliance
8. The most recent exercise has documented results and corrective actions

---

[Back to Control 2.4](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
