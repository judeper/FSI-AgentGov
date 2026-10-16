---
description: "Quick navigation paths for all admin portals used in the FSI Agent Governance Framework."
---
# Admin Portal Navigation Quick Reference

Quick navigation paths for all admin portals used in the FSI Agent Governance Framework.

**Last Verified:** 2026-10-16

**Verification scope:** Documentation review of every row and common-task shortcut against live official Microsoft documentation. This is **not tenant UI testing**: no portal sign-in, configuration change, screenshot capture, or entitlement test was performed. The source links identify the documented experience; entries explicitly marked **unconfirmed** are not verified navigation paths. Permissions, subscriptions, rollout, and the selected experience can change what appears. Follow the linked procedure and verify the intended tenant and environment before making changes.

---

## Power Platform Admin Center

**URL:** https://admin.powerplatform.microsoft.com

| Task | Navigation Path | Documentation |
|------|----------------|---------------|
| **View All Environments** | **Manage** > **Environments** | [P1] |
| Enable Managed Environments | **Manage** > **Environments** > Ellipsis next to environment > **Enable Managed Environments** | [P1] |
| View Environment Settings | **Manage** > **Environments** > Select environment > **Settings** | [P2] |
| **Environment Groups** | **Manage** > **Environment groups** | [P3] |
| Create Environment Group | **Manage** > **Environment groups** > **New group** | [P3] |
| Configure Group Rules | **Manage** > **Environment groups** > Select group > **Rules**; save changes and **Publish rules** to apply | [P3] |
| **Advanced Connector Policies** | **Manage** > **Environment groups** > Select group > **Rules** > **Advanced connector policies**; save and **Publish rules** | [P4] |
| **DLP Policies** | **Security** > **Data and privacy** > **Data policy** | [P5] |
| Create DLP Policy | **Security** > **Data and privacy** > **Data policy** > **+ New Policy** | [P5] |
| **Connectors** | For the connection connector picker, use **Power Apps maker portal** (`https://make.powerapps.com`) > **Data** > **Connections** > **New connection**, not a PPAC **Data > Connectors** menu | [P6] |
| **Connections** | **Power Apps maker portal** (`https://make.powerapps.com`) > **Data** > **Connections**; select the intended environment | [P6] |
| Agent Inventory | **Manage** > **Inventory** for unified inventory, or **Manage** > **Copilot Studio** for agents/agent flows/workflows. **Download** exports the entire inventory, not just displayed rows; agent **Modified on** / **Last modified by** columns do not work | [P16] |
| **Security Roles** | **Manage** > **Environments** > Select environment > **Settings** > **Users + permissions** > **Security roles** | [P7] |
| **Governance Insights** | **Actions** for governance recommendations. An environment-level **Governance Insights** blade is **unconfirmed** in the reviewed documentation; do not use the former shortcut as a verified path | [P8], [P9] |
| Runtime Protection | For external threat detection (preview): **Security** > **Threat detection** > Select environment. This is not a generic environment **Features > Runtime Protection** switch | [P10] |
| **Analytics** | Product usage reports: **Manage** > **Products**. Operational health: **Monitor** > **Products**; these are different reporting surfaces | [P11], [P12], [P13] |
| Power Automate Analytics | **Manage** > **Products** > **Power Automate** | [P11] |
| Power Apps Analytics | **Manage** > **Products** > **Power Apps** | [P12] |
| Microsoft Copilot Studio Metrics | **Monitor** > **Products** > **Copilot Studio** (documented metrics are preview) | [P14] |
| Copilot Studio Usage and Cost | **Copilot** > **Copilot Studio** for message consumption and agent usage; follow **Licensing** for additional consumption details. This is separate from the preview operational metrics page | [P15] |

---

## Microsoft Purview Portal

**URL:** https://purview.microsoft.com

If a solution card is not displayed, use **View all solutions**. Solution visibility depends on permissions and subscription, not only navigation labels. [U1]

| Task | Navigation Path | Documentation |
|------|----------------|---------------|
| **Data Loss Prevention** | **Solutions** > **Data loss prevention** | [U1], [U2] |
| Create DLP Policy | **Solutions** > **Data loss prevention** > **Policies** > **+ Create policy** | [U2] |
| View DLP Alerts | **Solutions** > **Data loss prevention** > **Alerts** | [U3] |
| **Sensitivity Labels** | **Solutions** > **Information Protection** > **Sensitivity labels** | [U4] |
| Create Sensitivity Label | **Solutions** > **Information Protection** > **Sensitivity labels** > **+ Create a label** (classic label scheme); for the modern scheme, select the label group and its create-label action | [U4] |
| Label Policies | **Solutions** > **Information Protection** > **Publishing policies** (the destination is also described as the **Label policies** page) | [U4] |
| **Audit** | **Solutions** > **Audit** | [U5] |
| Search Audit Log | **Solutions** > **Audit** > **Search**. Standard/Premium are capability tiers, not the documented search-page menu choices | [U5] |
| Audit Retention Policies | **Solutions** > **Audit** > **Audit retention policies** | [U6] |
| **DSPM for AI (classic)** | **Solutions** > **DSPM for AI (classic)**; use this only for the classic experience, not the newer DSPM solution | [U7], [U8] |
| AI Activity Dashboard | Classic: **Solutions** > **DSPM for AI (classic)** > **Overview**; use **Reports** for AI activity reports | [U7] |
| **Communication Compliance** | **Solutions** > **Communication compliance** | [U1], [U9] |
| Create CC Policy | **Solutions** > **Communication compliance** > **Policies** > **Create policy**; choose a template or custom policy | [U9] |
| **Insider Risk Management** | **Solutions** > **Insider risk management** | [U1], [U10] |
| Create IRM Policy | **Solutions** > **Insider risk management** > **Policies** > **Create policy** | [U10] |
| View IRM Alerts | **Solutions** > **Insider risk management** > **Alerts** | [U11] |
| **Sensitive Information Types** | **Solutions** > **Information Protection** > **Classifiers** > **Sensitive info types** | [U12] |
| Create Custom SIT | **Solutions** > **Information Protection** > **Classifiers** > **Sensitive info types** > **Create sensitive info type** | [U12] |
| **Data Retention** | **Solutions** > **Data Lifecycle Management** > **Policies** > **Retention policies** | [U13] |
| Create Retention Policy | **Solutions** > **Data Lifecycle Management** > **Policies** > **Retention policies** > **New retention policy** | [U13] |
| Retention Labels | **Solutions** > **Data Lifecycle Management** > **Retention labels**; use **Records management** for records-management capabilities | [U14] |
| **Endpoint DLP** | **Solutions** > **Data loss prevention** > **Overview** > **Data loss prevention settings** > **Endpoint settings**. Some procedures in the same article still call these **Endpoint DLP settings** | [U15] |
| **Records Management** | **Solutions** > **Records management** | [U1], [U14] |
| **eDiscovery** | **Solutions** > **eDiscovery** | [U1], [U8] |

---

## Microsoft Entra Admin Center

**URL:** https://entra.microsoft.com

| Task | Navigation Path | Documentation |
|------|----------------|---------------|
| **Conditional Access** | **Entra ID** > **Conditional Access** | [E1] |
| Create CA Policy | **Entra ID** > **Conditional Access** > **Policies** > **New policy** | [E1] |
| Named Locations | **Entra ID** > **Conditional Access** > **Named locations** | [E2] |
| Authentication Strengths | **Entra ID** > **Authentication methods** > **Authentication strengths** | [E3] |
| **MFA Settings** | **Entra ID** > **Multifactor authentication**; specific options are documented separately, for example **Phone call settings**. MFA enforcement is configured through Conditional Access | [E4], [E1] |
| FIDO2 Security Keys | **Entra ID** > **Security** > **Authentication methods** > **Policies** > **Passkey (FIDO2)** | [E3] |
| **Users** | **Entra ID** > **Users** | [E5] |
| **Groups** | **Entra ID** > **Groups** > **All groups** | [E6] |
| Create Security Group | **Entra ID** > **Groups** > **All groups** > **New group** > Group type **Security** | [E6] |
| **Roles and Administrators** | **Identity** > **Roles & admins** (the current role-assignment article still uses **Identity**) | [E7] |
| Assign Admin Role | **Identity** > **Roles & admins** > Select role > **Add assignments** | [E7] |
| **Access Reviews** | **ID Governance** > **Access Reviews** | [E8] |
| Create Access Review | **ID Governance** > **Access Reviews** > **New access review** | [E8] |
| **Privileged Identity Management** | **ID Governance** > **Privileged Identity Management** | [E9] |
| **Applications** | **Entra ID** > **Enterprise apps** > **All applications** | [E10] |
| App Registrations | **Entra ID** > **App registrations** | [E7] |
| **Sign-in Logs** | **Entra ID** > **Monitoring & health** > **Sign-in logs** | [E11] |
| **Audit Logs** | **Entra ID** > **Monitoring & health** > **Audit logs** | [E11] |
| **Agent Identities** | **Entra ID** > **Agents** > **Agent identities** | [E12] |

---

## Microsoft 365 Admin Center

**URL:** https://admin.microsoft.com

Expand **Show all** if a menu is hidden. Do not confuse an agent's availability in the store, installation for users, activation, and pinning: they are separate operations, and supported actions vary by agent. [M1], [M5]

| Task | Navigation Path | Documentation |
|------|----------------|---------------|
| **Users** | **Users** > **Active users** | [M1] |
| **Groups** | **Teams & groups** > **Active teams & groups** | [M2] |
| **Integrated Apps** | **Settings** > **Integrated apps** | [M3] |
| Deploy App | **Settings** > **Integrated apps**; use the linked deployment procedure for the app type rather than assume a universal button | [M3] |
| **Service Health** | **Health** > **Service health** | [M1] |
| Message Center | **Health** > **Message center** | [M1] |
| **Billing** | **Billing** > **Your products** | [M1], [M2] |
| Licenses | **Billing** > **Licenses** | [M2] |
| **Reports** | **Reports** > **Usage** | [M4] |
| **Agents > Settings** | **Agents** > **Settings** | [M6] |
| **Agents > Agent Registry** | **Agents** > **All agents** > **Registry** | [M7] |
| **Agent Inventory** | **Agents** > **All agents** > **Registry**, replacing the historical **Copilot > Agents & connectors > Agents** shortcut | [M7] |
| Approve/Publish Agent | **Agents** > **All agents** > **Requests** > Select request > **Publish to store** > Complete wizard > **Publish** | [M8] |
| Activate Agent | **Agents** > **All agents** > **Requests** > Select pending activation request > Complete activation wizard; admin-initiated activation is also available through **Registry** | [M5], [M8] |
| Deploy/Install Agent | **Agents** > **All agents** > **Registry** > Select available agent > **Install** > Complete deployment wizard | [M5] |
| Pin Agent | **Agents** > **All agents** > Ellipsis > **Manage pinned agents** > **Pin agent**; select an already-deployed agent | [M7] |
| Block/Unblock Agent | **Agents** > **All agents** > Select agent > **Block** / **Unblock** > Confirm and **Save** | [M5] |
| **Settings** | **Settings** > **Org settings** | [M1] |
| Security & Privacy | **Settings** > **Org settings** > **Security & privacy** | [M9] |
| **Microsoft Entra admin center** | Open `https://entra.microsoft.com` directly; available **Admin centers** links vary | [M1], [E1] |
| **Microsoft Purview Portal** | Open `https://purview.microsoft.com` directly rather than depend on a legacy **Compliance** shortcut | [U1] |
| **SharePoint Admin Center** | **Admin centers** > **SharePoint**, or use Microsoft's [SharePoint admin center link](https://go.microsoft.com/fwlink/?linkid=2185219) | [S1] |
| **Power Platform Admin** | Open `https://admin.powerplatform.microsoft.com` directly | [P8] |

---

## SharePoint Admin Center

**URL:** [SharePoint admin center](https://go.microsoft.com/fwlink/?linkid=2185219) (Microsoft's tenant-routing link), or **Microsoft 365 admin center** > **Admin centers** > **SharePoint**. [S1]

| Task | Navigation Path | Documentation |
|------|----------------|---------------|
| **Active Sites** | **Sites** > **Active sites** | [S2] |
| Create Site | **Sites** > **Active sites** > **Create** | [S3] |
| Site Settings | **Sites** > **Active sites** > Select site name or site row to open its details panel; this is not the site's own **Site settings** page | [S2] |
| **Deleted Sites** | **Sites** > **Deleted sites**, or the linked article's direct **Deleted sites** link | [S4] |
| **Policies** | **Policies** (left nav) | [S5], [S6] |
| **Sharing** | **Policies** > **Sharing** | [S5] |
| External Sharing Settings | **Policies** > **Sharing** > Organization-level sharing settings | [S5] |
| **Access Control** | **Policies** > **Access control** | [S6] |
| Unmanaged Devices | **Policies** > **Access control** > **Unmanaged devices** | [S6] |
| Idle Session Sign-out | **Policies** > **Access control** > **Idle session sign-out** | [S7] |
| Network Location | **Policies** > **Access control** > **Network location** | [S8] |
| Apps That Don't Use Modern Auth | **Policies** > **Access control** > **Apps that don't use modern authentication** | [S6] |
| **Term Store** | **Content services** > **Term store** | [S9] |
| **Migration** | Open Migration Manager in the SharePoint admin center; use the linked setup procedure | [S10] |
| **Settings** | **Settings** (left nav) | [S11] |
| Default Admin Center | **Unconfirmed:** a current **Settings > Default admin center** selector was not found in the reviewed documentation. Open the current admin center directly; do not rely on this legacy shortcut | [S1], [S11] |
| Site Creation | **Settings** > **Site creation** | [S11] |
| **More Features** | **More features** | [S12] |
| User Profiles | **More features** > **User profiles** > **Open** | [S12] |
| Search | **More features** > **Search** > **Open** (classic search administration) | [S13] |
| **Reports** | For SharePoint usage reports: **Microsoft 365 admin center** > **Reports** > **Usage** > SharePoint report. A generic SharePoint **Reports** landing-page shortcut is **unconfirmed** in the reviewed sources | [M4] |

---

## Copilot Studio

**URL:** https://copilotstudio.microsoft.com

These shortcuts describe agents in the **standard harness** experience documented by Microsoft, not every Copilot Studio authoring experience. The current creation article instructs users to turn off **New experience** for that workflow. [C1]

**Source-label variation:** The analytics overview calls the top-menu destination **Monitor**, while the sharing article still calls it the **Analytics** page and names the sharing role **Analytics Viewer**. Keep that role name; an Analytics reference in a sharing procedure is not evidence of a separate legacy navigation tab. [C2], [C7]

| Task | Navigation Path | Documentation |
|------|----------------|---------------|
| **All Agents** | **Agents** page | [C1] |
| Create New Agent | Standard experience: **Agents** > **Create blank agent**, or describe the agent on **Home** / **Agents** | [C1] |
| Agent Settings | Open agent > **Settings** on the top menu bar | [C1] |
| **Topics** | Open agent > **Topics** | [C1], [C2] |
| **Tools** | Open agent > **Tools** | [C1], [C5] |
| **Channels** | Open agent > **Channels** | [C3] |
| Publish Agent | Open agent > **Publish** > **Publish** and confirm | [C3] |
| **Analytics** | Open agent > **Monitor** on the top menu bar (the current name in the analytics overview) | [C2] |
| **Knowledge** | Open agent > **Knowledge** | [C1], [C6] |
| **Environment Selector** | Environment switcher on the top menu bar | [C4] |

---

## Common Admin Tasks - Quick Paths

### Enable Managed Environments (Control 2.1)
1. https://admin.powerplatform.microsoft.com
2. **Manage** > **Environments** > Ellipsis next to [Environment] > **Enable Managed Environments**. [P1]

### Create DLP Policy (Control 1.5)
1. https://purview.microsoft.com
2. **Solutions** > **Data loss prevention** > **Policies** > **+ Create policy**. [U2]

### Configure Audit Logging (Control 1.7)
1. https://purview.microsoft.com
2. **Solutions** > **Audit** > **Search**. Searching is not the same as enabling audit ingestion; follow Microsoft's [audit setup procedure](https://learn.microsoft.com/en-us/purview/audit-get-started) to verify collection is enabled. [U5]

### Set Up Conditional Access (Control 1.11)
1. https://entra.microsoft.com
2. **Entra ID** > **Conditional Access** > **Policies** > **New policy**. [E1]

### Configure Advanced Connector Policies (Control 1.4)
1. https://admin.powerplatform.microsoft.com
2. **Manage** > **Environment groups** > [Group] > **Rules** > **Advanced connector policies**; save and **Publish rules**. [P4]

### Create Sensitivity Labels (Control 1.5)
1. https://purview.microsoft.com
2. **Solutions** > **Information Protection** > **Sensitivity labels**; choose the create-label action for the tenant's classic or modern label scheme. [U4]

### Enable DSPM for AI (Control 1.6)
1. https://purview.microsoft.com
2. **Solutions** > **DSPM for AI (classic)** > **Overview**. This is the classic experience; follow its prerequisite/setup recommendations, not a universal enable switch. The newer DSPM experience is separate. [U7], [U8]

### Configure Communication Compliance (Control 1.10)
1. https://purview.microsoft.com
2. **Solutions** > **Communication compliance** > **Policies** > **Create policy**; choose the relevant template or custom policy. [U9]

---

## Microsoft Documentation Sources

[P16]: https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
[C7]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots

Each table row links to the procedure or overview reviewed on 2026-10-16. An **unconfirmed** entry records a documentation gap, not proof that a feature is absent from every tenant. Where Microsoft uses different labels within an article (for example Endpoint DLP settings), check the linked procedure before acting. No licensing entitlement is established by this navigation reference.

[P1]: https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-enable
[P2]: https://learn.microsoft.com/en-us/power-platform/admin/admin-settings
[P3]: https://learn.microsoft.com/en-us/power-platform/admin/environment-groups
[P4]: https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
[P5]: https://learn.microsoft.com/en-us/power-platform/admin/create-dlp-policy
[P6]: https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/add-manage-connections
[P7]: https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges
[P8]: https://learn.microsoft.com/en-us/power-platform/admin/new-admin-center
[P9]: https://learn.microsoft.com/en-us/power-platform/guidance/coe/starter-kit
[P10]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider
[P11]: https://learn.microsoft.com/en-us/power-platform/admin/analytics-flow
[P12]: https://learn.microsoft.com/en-us/power-platform/admin/analytics-powerapps
[P13]: https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitoring-overview
[P14]: https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitor-copilot-studio
[P15]: https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub
[U1]: https://learn.microsoft.com/en-us/purview/purview-portal
[U2]: https://learn.microsoft.com/en-us/purview/dlp-create-policy-cc-email
[U3]: https://learn.microsoft.com/en-us/purview/dlp-alerts-dashboard-get-started
[U4]: https://learn.microsoft.com/en-us/purview/create-sensitivity-labels
[U5]: https://learn.microsoft.com/en-us/purview/audit-search
[U6]: https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
[U7]: https://learn.microsoft.com/en-us/purview/dspm-for-ai
[U8]: https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
[U9]: https://learn.microsoft.com/en-us/purview/communication-compliance-policies
[U10]: https://learn.microsoft.com/en-us/purview/insider-risk-management-policies
[U11]: https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
[U12]: https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type
[U13]: https://learn.microsoft.com/en-us/purview/create-retention-policies
[U14]: https://learn.microsoft.com/en-us/purview/create-retention-labels-data-lifecycle-management
[U15]: https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
[E1]: https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-policy-all-users-mfa
[E2]: https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-assignment-network
[E3]: https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-enable-passkey-fido2
[E4]: https://learn.microsoft.com/en-us/entra/identity/authentication/howto-mfa-mfasettings
[E5]: https://learn.microsoft.com/en-us/entra/fundamentals/how-to-create-delete-users
[E6]: https://learn.microsoft.com/en-us/entra/fundamentals/how-to-manage-groups
[E7]: https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/manage-roles-portal
[E8]: https://learn.microsoft.com/en-us/entra/id-governance/create-access-review
[E9]: https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-activate-role
[E10]: https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/view-applications-portal
[E11]: https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-access-activity-logs
[E12]: https://learn.microsoft.com/en-us/entra/agent-id/agent-lists
[M1]: https://learn.microsoft.com/en-us/microsoft-365/admin/admin-overview/admin-center-overview
[M2]: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/assign-licenses-to-users
[M3]: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/test-and-deploy-microsoft-365-apps
[M4]: https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/activity-reports
[M5]: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-actions
[M6]: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-settings
[M7]: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry
[M8]: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-requests
[M9]: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/idle-session-timeout-web-apps
[S1]: https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role
[S2]: https://learn.microsoft.com/en-us/sharepoint/get-started-new-admin-center
[S3]: https://learn.microsoft.com/en-us/sharepoint/create-site-collection
[S4]: https://learn.microsoft.com/en-us/sharepoint/restore-deleted-site-collection
[S5]: https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off
[S6]: https://learn.microsoft.com/en-us/sharepoint/control-access-from-unmanaged-devices
[S7]: https://learn.microsoft.com/en-us/sharepoint/sign-out-inactive-users
[S8]: https://learn.microsoft.com/en-us/sharepoint/control-access-based-on-network-location
[S9]: https://learn.microsoft.com/en-us/sharepoint/create-and-manage-terms
[S10]: https://learn.microsoft.com/en-us/sharepointmigration/mm-get-started
[S11]: https://learn.microsoft.com/en-us/sharepoint/manage-site-creation
[S12]: https://learn.microsoft.com/en-us/sharepoint/manage-user-profiles
[S13]: https://learn.microsoft.com/en-us/sharepoint/manage-search-schema
[C1]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-first-bot
[C2]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
[C3]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
[C4]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/environments-first-run-experience
[C5]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
[C6]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio

*Last Updated: October 2026*
*Documentation verified: 2026-10-16. Tenant UI verification: not performed.*
