# Control 2.10: Patch Management and System Updates — Portal Walkthrough

> Portal-based configuration guidance for [Control 2.10: Patch Management and System Updates](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md).
>
> **Audience:** Power Platform Admins, AI Administrators, and AI Governance Leads in US financial services organizations.

---

## Prerequisites

Before starting, confirm:

- **Roles:**
    - **Power Platform Admin** — required to set release channels and create environments in PPAC
    - **AI Administrator** — required to track Microsoft 365 Copilot and Copilot Studio service updates and manage Copilot feature settings
    - **Entra Global Reader** *or* **Microsoft 365 Service Support Admin** — required to read Message Center; an Entra Global Admin or AI Administrator can also delegate read access via the Service Communications API
    - **Reader** on the target Azure subscription(s) — required to view Service Health; **Monitoring Contributor** required to create alert rules and Azure Monitor action groups
- **Licensing:** Managed Environments enabled on every Zone 2 / Zone 3 environment (release channel selection requires Managed Environments for full enforcement)
- **Identity:** A change-intake distribution list (or Teams channel) routed to the AI Governance Lead and the Power Platform Admin
- **Source-control / evidence store:** A SharePoint document library or Dataverse table designated for patch evidence, ideally with retention lock per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- **Sovereign cloud:** If the tenant is GCC, GCC High, or DoD, identify the correct admin endpoints up front (commercial admin URLs will not work) — see the [PowerShell Setup](powershell-setup.md) playbook for the canonical endpoint table

> **Implementation caveat:** Microsoft owns the platform release cadence. The configuration below governs **awareness, validation, and response** — not suppression of vendor-driven changes.

---

## Overview

This walkthrough configures, in order:

1. Microsoft 365 Message Center subscriptions and routing
2. Azure Service Health alert rules with Azure Monitor action groups
3. Power Platform release channels per environment (Monthly vs. Semi-annual)
4. A validation environment that mirrors production
5. Maintenance windows aligned to the two annual release waves
6. The patch evidence library and templates

---

## Part 1: Configure Microsoft 365 Message Center

The Message Center is the authoritative source for Microsoft 365 platform changes that affect AI agents. Posts are tagged by service and may carry an **Action required by** date.

### Subscribe to email digests

1. Open the [Microsoft 365 Admin Center](https://admin.microsoft.com).
2. Select **Health > Message center**.
3. Select **Preferences** (gear icon, top right of the Message Center page).
4. On the **Email** tab:
    - Add the change-intake distribution list (recommended) and individual recipients (Power Platform Admin, AI Administrator, AI Governance Lead).
    - Check **Send me a weekly digest** and **Send me emails for major updates and Message center posts that I am tagged in**.
    - Under **Choose services**, restrict to the relevant services for your AI estate. Typical FSI selection:
        - Microsoft Copilot
        - Microsoft Copilot Studio
        - Power Platform
        - Power Automate
        - Power Apps
        - Microsoft Dataverse
        - SharePoint Online (if used as a knowledge source)
        - Microsoft Purview
5. **Save**.

### Apply the FSI tag taxonomy

Tags drive routing and evidence retention. Apply at minimum:

| Tag | Purpose | Owner |
|-----|---------|-------|
| `FSI-Agent-Impact` | Post may affect agent behavior or runtime | AI Administrator |
| `FSI-Connector-Change` | Connector deprecation, new connector, auth change | Power Platform Admin |
| `FSI-Action-Required` | Post has an "Action required by" date | AI Governance Lead |
| `FSI-Awaiting-Assessment` | Triaged but not yet impact-assessed | AI Governance Lead |
| `FSI-Closed` | Assessment complete; outcome recorded in change log | AI Governance Lead |

To apply: open a Message Center post → **Tag** → add tags → **Save**.

> **Note (April 2026):** Tag taxonomy is per-tenant and per-user. To enforce a tenant-wide taxonomy, automate tagging with the [Message Center Monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor) solution and treat the manual tag set as a fallback only.

---

## Part 2: Configure Azure Service Health Alerts

Service Health surfaces live service incidents and planned maintenance. Use it to detect **runtime** disruption (not feature changes — those come through Message Center).

1. Open the [Azure Portal](https://portal.azure.com).
2. Search for **Service Health** and open it.
3. Select **Health alerts** > **+ Add service health alert**.
4. Configure:
    - **Subscription:** select the subscription(s) hosting your Power Platform / Azure dependencies.
    - **Services:** add at minimum:
        - Power Platform (resource provider `Microsoft.PowerPlatform`)
        - Power Apps (`Microsoft.PowerApps`)
        - Power Automate (`Microsoft.Flow`)
        - Microsoft 365 Apps (if applicable)
        - Azure Key Vault (if any agent retrieves secrets from a Key Vault)
        - Application Insights / Log Analytics (if used for agent telemetry)
    - **Regions:** the regions hosting your environments (US East/Central/West for most US FSI tenants; sovereign-cloud customers select GCC/GCC High regions).
    - **Event type:** Service issue, Planned maintenance, Health advisory, Security advisory.
5. Under **Actions**, attach an **Azure Monitor action group**:
    - If none exists, select **Create action group**.
    - Name it (e.g., `ag-fsi-platform-ops`).
    - Add an **Email** action for the operations distribution list.
    - For Zone 3, add a **Webhook** or **Logic App** action that opens an incident ticket in your ITSM.
    - Avoid relying on **SMS** as the sole notification channel — carrier delivery is best-effort and not audit-defensible. Use email or webhook to a logged channel.
6. Name the alert (e.g., `alert-fsi-pp-service-health`) and save.

> **FSI Note:** Document the action group composition in your incident-response runbook. Per FFIEC IT Handbook expectations, alerting paths must be testable and have a documented owner.

See [Microsoft Learn: Configure Service Health alerts](https://learn.microsoft.com/en-us/azure/service-health/alerts-activity-log-service-notifications-portal) for current screens.

---

## Part 3: Set Release Channels per Environment

Power Platform offers two release channels at the environment level. The "Early Access" opt-in concept used in earlier waves has been replaced by the **Monthly channel**.

| Channel | Cadence | FSI Use |
|---------|---------|---------|
| **Monthly channel** | Features ship monthly; closer to Microsoft's internal release cadence | Validation environments, Zone 1 sandboxes, breaking-change rehearsal |
| **Semi-annual channel** (default) | Aligned to the two annual release waves (April / October) | Zone 2 / Zone 3 production environments |

### Set the channel

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com).
2. Select **Environments** and pick the target environment.
3. Select **Settings** (top toolbar) > **Product** > **Behavior**.
4. Under **Release channel**, select the appropriate channel:
    - **Monthly channel** for the validation environment.
    - **Semi-annual channel** for production.
5. Select **Save**.

> **Note (April 2026):** The Behavior page also exposes feature toggles that may be channel-gated. Review the page after each wave update to confirm new toggles are set per your governance policy.

### Apply by zone

| Zone | Validation environment channel | Production environment channel |
|------|--------------------------------|--------------------------------|
| Zone 1 | Not required (use a personal sandbox if desired) | Monthly *or* Semi-annual at owner discretion |
| Zone 2 | **Monthly** (mirrors prod config) | **Semi-annual** |
| Zone 3 | **Monthly** (mirrors prod config; mandatory) | **Semi-annual** (mandatory; no exceptions without CAB approval) |

See [Microsoft Learn: Power Platform release channels](https://learn.microsoft.com/en-us/power-platform/admin/early-release).

---

## Part 4: Establish a Validation Environment

The validation environment exists to surface platform-driven regressions before production users see them.

1. In PPAC, select **Environments > + New**.
2. Configure:
    - **Name:** `FSI-Update-Validation` (or your tenant convention).
    - **Type:** **Sandbox** (sandboxes can be reset; production cannot).
    - **Region:** the same region as your production agents.
    - **Add Dataverse:** **Yes** if production agents use Dataverse-backed knowledge sources or topics; otherwise No.
    - **Managed Environment:** **Enable**.
3. After creation, open the environment and apply Part 3 to set the channel to **Monthly**.
4. Deploy a **managed solution copy** of each Zone 2/3 production agent into the validation environment using your pipeline (see [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)).
5. Document any **out-of-solution dependencies** (knowledge sources by URL, tenant-level connectors, custom connectors) — these must be reproduced manually because they are not part of the solution boundary.
6. Author a **baseline regression test suite** for each agent (covered in the [Verification & Testing](verification-testing.md) playbook).

---

## Part 5: Define Maintenance Windows by Wave

The Power Platform release cadence centers on two annual waves:

- **Wave 1** — preview from January, general availability rolling from April through September
- **Wave 2** — preview from July, general availability rolling from October through March

### Recommended FSI window pattern

| Zone | Window pattern | Notes |
|------|---------------|-------|
| Zone 1 | Anytime, with notification 24h before known wave dates | Owners self-manage; document on a SharePoint calendar |
| Zone 2 | Monthly maintenance window aligned to Patch Tuesday week, off-hours | Document approver and rollback path per change |
| Zone 3 | Two annual major windows aligned to wave GA, plus monthly micro-windows for Message Center "Action required" items; CAB approval required | Communicate windows 30 days in advance to business stakeholders; align with [Control 2.4](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) |

### Document and publish the calendar

1. Create a SharePoint calendar list named `FSI Platform Maintenance`.
2. For each window, capture:
    - Window start / end (with time zone)
    - In-scope environments and agents
    - Change ticket reference
    - Rollback decision time
    - Approver
3. Restrict edit access to Power Platform Admin and AI Governance Lead; grant read to all agent owners and business stakeholders.

---

## Part 6: Set Up the Patch Evidence Library

The evidence library is what an examiner will request under SEC 17a-4 / FINRA 4511 record-retention rules.

1. Create a SharePoint document library named `FSI-Patch-Evidence`.
2. Add columns:

    | Column | Type | Notes |
    |--------|------|-------|
    | Message ID | Single line | e.g., `MC123456` from Message Center |
    | Service | Choice | Power Platform, Copilot Studio, M365 Copilot, etc. |
    | Category | Choice | Plan for change, Prevent or fix issues, Stay informed |
    | Action Required By | Date | Microsoft-set deadline (if any) |
    | Impact Assessment | Multi-line | Owner: AI Governance Lead |
    | Validation Result | Choice | Pass / Fail / N/A |
    | Validation Evidence Link | Hyperlink | Link to test run output |
    | Deployment Date | Date | Production deployment timestamp |
    | Rollback Plan | Multi-line | Required for Zone 3 |
    | Approver | Person | Required for Zone 2/3 |
    | SHA-256 (evidence) | Single line | Required for Zone 3 |
    | Status | Choice | Open / Validated / Deployed / Rolled back / Closed |

3. Apply a **retention label** with retention duration per your firm's record policy (typically 6 years for FSI under FINRA 4511 / SEC 17a-4(b)(4); consult your records-retention schedule).
4. Enable **versioning** and disallow item deletion via library permissions.
5. Optional (Zone 3): mirror entries to Microsoft Sentinel via a Logic App for cross-control SIEM correlation.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|--------------------|
| Message Center subscription | Personal | Distribution list | Distribution list + automated polling |
| Service Health alerts | Optional | Required, email | Required, email + ITSM webhook |
| Release channel — validation env | N/A | Monthly | Monthly |
| Release channel — production env | Default | Semi-annual | Semi-annual |
| Validation environment | Optional | Required | Required, mirrors prod managed solutions |
| Maintenance window cadence | Ad hoc | Monthly | Two wave windows + monthly micro-windows |
| Evidence retention | Best-effort | CSV export per change | SHA-256-hashed JSON + manifest, retention-locked |
| CAB approval | N/A | For breaking changes | For all production deployments |

---

## Validation

After completing the configuration, confirm:

- [ ] Message Center email digest received by the change-intake distribution list within 7 days
- [ ] At least one Message Center post tagged with the FSI taxonomy
- [ ] Test Service Health alert fires (use a Microsoft-published service health drill, or a test alert via PowerShell — see [Verification & Testing](verification-testing.md))
- [ ] Validation environment shows **Monthly** under Settings > Product > Behavior; production shows **Semi-annual**
- [ ] Validation environment has a managed solution copy of at least one production agent
- [ ] `FSI Platform Maintenance` calendar contains the next two upcoming windows
- [ ] `FSI-Patch-Evidence` library exists with all required columns and a retention label applied
- [ ] One end-to-end dry run executed (Message Center post → impact assessment → validation environment test → evidence captured → ticket closed)

**Expected Result:** Platform changes are received, triaged, validated in a Monthly-channel sandbox, deployed under approval to Semi-annual production, and recorded in a retention-locked evidence library with hash-integrity proofs.

---

## Related Playbooks

- [PowerShell Setup](powershell-setup.md) — Pinned-module, sovereign-aware automation for Message Center polling, evidence emission, and validation runs
- [Verification & Testing](verification-testing.md) — Test cases, rollback drill, evidence collection
- [Troubleshooting](troubleshooting.md) — Common issues with Message Center, release channels, and Service Health alerts

[Back to Control 2.10](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md)

---

*Updated: April 2026 | Version: v1.6.2*
