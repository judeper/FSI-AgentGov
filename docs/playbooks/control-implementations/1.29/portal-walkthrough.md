# Control 1.29 — Portal Walkthrough: Global Secure Access Network Controls

**Playbook Type:** Portal Walkthrough
**Control:** 1.29 — Global Secure Access: Network Controls for Microsoft Copilot Studio Agents
**Audience:** Power Platform Admins, Entra Security Admins
**Estimated Duration:** 60–90 minutes for full configuration across a single environment
**Prerequisites:** Global Secure Access license, Power Platform Admin role, Entra Security Admin role

!!! warning "Preview Feature"
    This is a preview feature. Preview features aren't meant for production use and may have restricted functionality. Features may change before becoming generally available. Subject to the [Microsoft Azure Preview Supplemental Terms of Use](https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/). Screenshots and navigation paths reflect the March 2026 UI state and may change. Validate each step against current UI before executing in production.

!!! note "Complete Control 1.20 First"
    This playbook configures **outbound** network controls for agent traffic. Ensure Control 1.20 (Network Isolation and Private Connectivity) inbound controls have been configured for the same environments before applying outbound GSA controls. A complete Zero Trust network posture requires both inbound restriction and outbound filtering.

---

## Overview

This walkthrough configures Global Secure Access network controls for Copilot Studio agents across three areas:

1. **Power Platform admin center** — Enable GSA agent traffic forwarding per environment
2. **Microsoft Entra admin center — Policy creation** — Create web content filtering, threat intelligence, and network file filtering policies
3. **Microsoft Entra admin center — Baseline profile** — Link all policies to the GSA baseline profile
4. **Microsoft Entra admin center — Monitoring** — Validate traffic logs and confirm agent metadata capture

---

## Phase 1: Enable GSA Agent Traffic Forwarding in Power Platform Admin Center

### Step 1.1 — Open the target environment settings

1. Navigate to [https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com).
2. In the left navigation, select **Environments**.
3. Locate the Copilot Studio environment you are configuring. Use the search bar to filter by environment name if needed.
4. Click the environment name to open the environment detail page.
5. In the top command bar, click **Settings**.

!!! info "Zone Classification Check"
    Before enabling, confirm the environment's Zone classification (Zone 1 / Zone 2 / Zone 3) per your organization's AI governance classification record. Zone 2 and Zone 3 environments require GSA forwarding. Zone 1 is optional but recommended. Document your classification decision in the change record.

### Step 1.2 — Enable Global Secure Access

1. In the Settings panel, expand the **Features** section (you may need to scroll down or select a Features category depending on current UI layout).
2. Locate the **Global Secure Access** toggle.
3. Toggle the setting to **On**.
4. Click **Save** to apply the change.

!!! warning "Propagation Time"
    After enabling, allow up to 15–30 minutes for the change to propagate to all agent execution nodes. Do not perform traffic validation tests immediately after saving. Proceed with policy creation in Phase 2 while waiting for propagation.

### Step 1.3 — Document and repeat for all in-scope environments

1. Record the environment name, environment ID, and the date/time GSA forwarding was enabled in your change management record.
2. Repeat Steps 1.1–1.2 for every Copilot Studio environment in scope.
3. For Zone 3 organizations with many environments, use the PowerShell playbook to enable GSA across multiple environments in bulk (see [PowerShell Setup](powershell-setup.md)).

---

## Phase 2: Create Web Content Filtering Policy in Entra Admin Center

### Step 2.1 — Navigate to web content filtering

1. Navigate to [https://entra.microsoft.com](https://entra.microsoft.com).
2. In the left navigation, expand **Global Secure Access** (under the Security section).
3. Select **Secure** from the submenu.
4. Click **Web content filtering profiles**.
5. Click **+ New policy** to create a new filtering policy.

### Step 2.2 — Define the policy name and description

1. In the **Policy name** field, enter a descriptive name following your naming convention. Recommended format: `AgentTraffic-WebFilter-[Zone]-[Date]` (e.g., `AgentTraffic-WebFilter-Zone3-2026Q1`).
2. In the **Description** field, enter: `Web content filtering policy for Copilot Studio agent outbound traffic. Created per FSI-AgentGov Control 1.29. Reviewed and approved [date] by [approver name].`
3. Set the **Policy state** to **Enabled**.

### Step 2.3 — Configure category-based blocking rules

1. In the policy editor, navigate to the **Category** rules section.
2. Add category-based block rules for the following categories at minimum for Zone 2 and Zone 3 environments. Select **Block** as the action for each:

| Category | Rationale for FSI |
|---|---|
| Illegal software and piracy | Prevent agent download of unauthorized software |
| Social media | Prevent data exfiltration to social platforms |
| Gambling | Regulatory acceptability — not a legitimate agent destination |
| Unapproved generative AI / AI tools | Block unauthorized third-party AI API calls by agents unless specifically approved |
| Hacking and exploits | Block access to attacker tooling and exploit repositories |
| Anonymizers and proxies | Block circumvention of network controls |
| Malware and botnets | Belt-and-suspenders block alongside threat intelligence filtering |
| Peer-to-peer networks | Block unauthorized file transfer channels |
| Data repository / file sharing services | Block upload to non-approved file hosts (Box, Dropbox, consumer Google Drive, etc.) unless on the organizational allowlist |

!!! note "Category Availability"
    Category availability depends on your GSA license tier. Some categories listed above may be grouped differently in the current UI. Map to available categories that best reflect the intent. Document any gaps where a desired category is not available as a control gap with compensating control reference.

### Step 2.4 — Configure URL-based rules

1. Navigate to the **URL** rules section of the policy editor.
2. For each explicitly blocked destination identified in your AI governance policy (e.g., specific unapproved AI API endpoints), add a **Block** rule with the specific FQDN or URL pattern.
3. For each approved external destination that would otherwise be categorically blocked, add an **Allow** rule to the exceptions/allowlist section. Record the business justification for each allowlist entry.

!!! warning "Default Deny for Uncategorized Destinations (Zone 3)"
    Zone 3 environments should consider setting the default action for uncategorized destinations to **Block**. This enforces an explicit-allowlist model and prevents agents from accessing destinations that have not been assessed. Review this setting with your Security team as it may require a more extensive initial allowlist build before rollout.

### Step 2.5 — Save the policy

1. Review the complete policy configuration.
2. Click **Save** (or **Create**) to save the policy. Note: Do not link to the baseline profile yet — complete all three policy types first (Phases 2, 3, and 4), then link in Phase 5.

---

## Phase 3: Configure Threat Intelligence Filtering Policy

### Step 3.1 — Navigate to threat intelligence settings

1. In Entra admin center, navigate to **Global Secure Access** > **Secure**.
2. Select **Threat intelligence**.
3. The threat intelligence filtering configuration screen appears.

### Step 3.2 — Enable and configure threat intelligence filtering

1. Confirm that **Threat intelligence filtering** is **Enabled** for your tenant.
2. Review the current threat intelligence feed configuration. Microsoft-managed threat feeds are included by default and updated in near-real time. No additional feed subscription is required for baseline coverage.
3. Set the action to **Block** (not Audit). For FSI Zone 2 and Zone 3 environments, audit-only mode is insufficient — requests to known malicious infrastructure must be actively blocked, not merely logged.
4. Review the **Exclusions** list. Add exclusions only for destinations you have independently verified are safe but are triggering false positives. Document each exclusion with date, approver, and justification.
5. Click **Save** to apply the configuration.

!!! info "Threat Intelligence Feed Currency"
    Microsoft's threat intelligence feeds are updated continuously based on global telemetry. No manual feed update is required. However, note that newly observed C2 infrastructure may have a latency of hours to days before appearing in the feed. Complement threat intelligence filtering with behavioral anomaly detection (see Control 1.8) for detection of zero-day attacker infrastructure.

---

## Phase 4: Create Network File Filtering Policy

### Step 4.1 — Navigate to network file filtering

1. In Entra admin center, navigate to **Global Secure Access** > **Secure**.
2. Click **Network file filtering**.
3. Click **+ New policy** to create a new file filtering policy.

### Step 4.2 — Define the policy

1. In the **Policy name** field, enter a name following your naming convention. Recommended format: `AgentTraffic-FileFilter-[Zone]-[Date]`.
2. In the **Description** field, enter: `Network file filtering policy for Copilot Studio agent traffic. Created per FSI-AgentGov Control 1.29. Restricts agent file upload and download per organizational data protection standards.`
3. Set the **Policy state** to **Enabled**.

### Step 4.3 — Configure file transfer rules

Configure the following rules based on your zone and data protection requirements:

**Upload rules (data leaving the organization):**

1. Add a rule to **Block** file uploads to uncategorized or non-approved file hosting services.
2. Add a rule to **Block** upload of files matching sensitive data type patterns if file content inspection is available in your GSA configuration tier.
3. For each approved file destination (e.g., approved cloud storage used in an agent workflow), add an **Allow** rule with the specific destination domain and documented business justification.

**Download rules (files entering the agent execution environment):**

1. Add a rule to **Block** download of executable file types (`.exe`, `.msi`, `.bat`, `.ps1`, `.sh`, `.dll`) from external web sources. Agents should not be downloading executable content from arbitrary URLs.
2. Add a rule to **Block** download of compressed archives (`.zip`, `.tar`, `.7z`) from uncategorized destinations unless specifically approved.
3. Add **Allow** rules for specific approved content download sources (e.g., approved vendor document repositories used by the agent for knowledge retrieval).

!!! warning "Scope with Agent Developers"
    Before finalizing file filtering rules, review agent design documentation with agent developers to identify all legitimate file transfer operations. Overly restrictive rules without allowlist exceptions can break agent functionality silently — the agent will fail to complete a task and may surface a generic error rather than a clear permission denial. Test thoroughly in a non-production environment first.

### Step 4.4 — Save the policy

1. Review the complete policy configuration.
2. Click **Save** (or **Create**) to save the policy.

---

## Phase 5: Link Policies to the Global Secure Access Baseline Profile

!!! warning "Baseline Profile Only (Preview Limitation)"
    In the current preview, only the **baseline profile** is supported for agent traffic. Conditional Access-linked profiles are not yet available for Copilot Studio agent traffic. All policy linking must be done through the baseline profile as described below.

### Step 5.1 — Open the baseline profile

1. In Entra admin center, navigate to **Global Secure Access** > **Connect**.
2. Select **Traffic forwarding**.
3. In the Traffic forwarding page, locate and click the **Baseline profile**.

### Step 5.2 — Link the web content filtering policy

1. In the baseline profile configuration, locate the **Web content filtering** section.
2. Click **Link a policy** (or the equivalent control shown in current UI).
3. Select the web content filtering policy created in Phase 2.
4. Click **Save** or **Apply** to confirm the link.

### Step 5.3 — Link the threat intelligence filtering policy

1. In the baseline profile configuration, locate the **Threat intelligence** section.
2. Confirm the threat intelligence filtering is set to the policy configured in Phase 3.
3. Verify the action is **Block** and that the policy is enabled.

### Step 5.4 — Link the network file filtering policy

1. In the baseline profile configuration, locate the **Network file filtering** section.
2. Click **Link a policy**.
3. Select the network file filtering policy created in Phase 4.
4. Click **Save** or **Apply** to confirm the link.

### Step 5.5 — Save the baseline profile

1. Review the complete baseline profile configuration showing all three linked policy types.
2. Click **Save** to commit the baseline profile changes.
3. Allow 15–30 minutes for policy changes to propagate globally.

---

## Phase 6: Validate Traffic Logs and Agent Metadata Capture

### Step 6.1 — Navigate to GSA traffic logs

1. In Entra admin center, navigate to **Global Secure Access** > **Monitor**.
2. Select **Traffic logs**.
3. The traffic logs view appears with a filterable log stream.

### Step 6.2 — Filter for agent traffic

1. Use the filter controls to filter by **Source** or **Traffic type** if agent-specific filter options are available in current UI.
2. Alternatively, filter by the IP range or identity context associated with your Copilot Studio environment.
3. Trigger a test request from a Copilot Studio agent in one of the configured environments (the agent should make a call to an external HTTP endpoint as part of its normal operation or a test flow).
4. Wait 2–5 minutes and refresh the log view.

### Step 6.3 — Verify agent metadata fields

Confirm the following fields are present in log entries for agent-originated traffic:

| Field | Expected Value |
|---|---|
| Traffic type | Agent / Copilot Studio (exact label varies by UI version) |
| Source | Agent environment identifier |
| Destination FQDN | The external hostname the agent attempted to contact |
| Action | Allow or Block |
| Policy matched | Name of the web content filtering / threat intelligence / file filtering policy that evaluated the request (for blocked requests) |
| Timestamp | UTC timestamp of the request |

!!! warning "Missing Agent Metadata"
    If log entries appear but do not include agent-specific metadata fields, the traffic may be routing through a path that bypasses GSA forwarding. Common causes: GSA forwarding toggle not saved correctly, propagation delay not yet complete, or custom connector using a non-HTTP protocol. See the [Troubleshooting](troubleshooting.md) playbook.

### Step 6.4 — Test a blocked request

1. Configure a test agent to attempt a connection to a destination that falls within a blocked web content category (use a test URL appropriate to your organization — do not use malware or C2 infrastructure for testing).
2. Trigger the agent request.
3. Confirm in GSA traffic logs that the request appears with action = **Block** and the correct policy name referenced.
4. Confirm the agent flow received an appropriate error response (not a silent timeout).

### Step 6.5 — Document completion

1. Capture screenshots of:
    - GSA forwarding toggle enabled in Power Platform admin center for each in-scope environment
    - Web content filtering policy configuration and baseline profile link
    - Threat intelligence filtering enabled with Block action
    - Network file filtering policy configuration and baseline profile link
    - Sample GSA traffic log entries showing agent metadata
2. Store screenshots in your change management or ITGC evidence repository.
3. Update the control compliance record for Control 1.29 to reflect configuration date, configuring administrator, and evidence reference.

---

## Ongoing Operational Steps

### Weekly Log Review (Zone 2)

1. Navigate to **Global Secure Access** > **Monitor** > **Traffic logs**.
2. Filter to the past 7 days; filter for agent traffic.
3. Review blocked requests: are any legitimate? If yes, open an allowlist change request.
4. Review allow requests: any unusual volume or unexpected destinations? If yes, investigate.
5. Document review date, reviewer name, and findings (or "no anomalies found") in the log review record.

### Daily Log Review (Zone 3)

1. Follow the same steps as the weekly review but scoped to the past 24 hours.
2. Any anomalous blocked requests (unexpected volume, new destination types) must be escalated to Security Operations as a potential incident within the same business day.
3. Export daily log summaries to Sentinel per Control 3.9 configuration.

### Allowlist Change Management

1. Any request to add a destination to the web content filtering allowlist must be submitted as a formal change request.
2. Change request must include: destination FQDN or URL pattern, business justification, agent name(s) requiring access, data classification of information transmitted, approver (AI Governance team and Security team sign-off required for Zone 3).
3. Quarterly review: audit all allowlist entries and remove entries no longer required.

---

[Back to Control 1.29](../../../controls/pillar-1-security/1.29-global-secure-access-network-controls.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
