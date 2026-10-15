# Control 1.28: Policy-Based Agent Publishing Restrictions

**Last Verified:** 2026-10-14
**Verification method:** Live Microsoft Learn documentation review; no tenant UI session or screenshots were captured. Actual tenant UI and configured approval workflows still require local verification.

## Expected Screenshots

Capture evidence in a non-production environment with non-sensitive names. Labels and icons can vary; record the actual UI rather than reproducing sample messages. Zone classifications are framework requirements, not Microsoft product settings.

### Screenshot 1: Zone-Specific Data Policy
**Portal Path:** Power Platform Admin Center -> Security -> Data and privacy -> Data policy -> [Policy]
**What to capture:**
- Policy name, ID, assigned environments, and connector classifications.
- Business, Non-business, and Blocked groups, including the default group for new connectors.
- Exact Copilot Studio connector names, such as **HTTP**, **Facebook channel in Copilot Studio**, **Direct Line channels in Copilot Studio**, and **Chat without Microsoft Entra ID authentication in Copilot Studio**.
- Keep an approved channel allowed. Do not confuse the Facebook service connector with the Copilot Studio Facebook channel connector.
- Record unblockable connectors; a literal "everything else Blocked" or empty Non-business group is not always possible.

### Screenshot 2: Connector Classification
**Portal Path:** Power Platform Admin Center -> Security -> Data and privacy -> Data policy -> [Policy] -> Edit Policy -> Assign connectors
**What to capture:**
- Connector list, search, Blockable attribute, and Business/Non-business/Blocked group views.
- A selected blockable connector and its Move to Business or Block action (toolbar or ellipsis menu).
- Do not require a three-column drag-and-drop interface.

### Screenshot 3: Environment Scope
**Portal Path:** Power Platform Admin Center -> Security -> Data and privacy -> Data policy -> [Policy] -> Edit Policy
**What to capture:**
- Scope and environment selection, including Available and Added to policy views where shown.
- For tenant policies, record Add multiple environments, Add all environments, or Exclude certain environments as applicable.
- Environment IDs and the saved policy's Applied to summary. Environment-level policies have no tenant-wide scope selection.

### Screenshot 4: DLP Violation Prevents Publishing
**Portal Path:** Copilot Studio -> [Agent] -> Publish / Channels
**What to capture:**
- Error banner and Details, publish failure or unavailable Publish button, and actual connector/policy information.
- Channels -> error details -> Download: the exported workbook's **DLP violations** and **Blocked channels** worksheets.
- If Show raw is available, capture the violation type without sensitive data.
- This is DLP evidence, not a generic "Security scan failed" panel.

### Screenshot 5: Successful Publish
**Portal Path:** Copilot Studio -> [Agent] -> Publish
**What to capture:**
- Successful publication of an agent whose connectors and channels comply with the assigned policy.
- Agent identity and publication time; supporting approval evidence is collected separately.
- Do not require invented "DLP compliance / Channel restrictions / Configuration security: Passed" scan categories.

### Screenshot 6: Automatic Security Scan Warning
**Portal Path:** Copilot Studio -> [Agent] -> Publish
**What to capture:**
- In a test agent, a documented risk condition: **No authentication**, **Maker-provided credentials** for a connector/flow, or sharing with everyone in the organization.
- The actual warning and remediation guidance shown before publishing.
- Do not expect HTTP certificate-validation warnings, zone-specific risk ratings, fixed colors, or an acknowledgment checkbox unless observed in the tenant.
- Security scan warnings and mandatory DLP blocks are separate signals; a warning cannot override a DLP violation.

### Screenshot 7: Restricted Channels
**Portal Path:** Copilot Studio -> [Agent] -> Channels (top menu)
**What to capture:**
- Disabled/unavailable channels and the information icon explaining policy or authentication restrictions.
- The approved Teams and Microsoft Copilot channel, where permitted.
- DLP uses **Direct Line channels in Copilot Studio** for demo/custom websites and other Direct Line channels; **Facebook channel in Copilot Studio** controls Facebook.
- Telegram is reached through Azure Bot Service channels, not a documented standalone Copilot Studio Telegram DLP connector. Record the actual channel path and policy coverage; do not infer a Telegram-specific block from a service connector.

### Screenshot 8: Configured Approval Process
**Portal Path:** Power Automate -> [Organization's approval flow], or Power Apps -> [Pipelines host] -> Deployment Pipeline Configuration
**What to capture:**
- The actual intake trigger, approvers, decision branches, and evidence sink.
- For pipeline gates, **Pre-deployment Step Required** and its custom approval/status-update flow.
- Do not expect PPAC Features toggles called "Require approval for new chatbots" or "Require approval for chatbot updates."

### Screenshots 9-12: Submission, Pending, Approved, and Rejected Records
**Location:** Organization's intake form/change ticket, Power Automate Approvals, or configured pipeline workflow
**What to capture:**
- Request ID, agent/environment, submitter, justification, testing evidence reference, and decision history.
- Approver, timestamp, comments, and notification for approved and rejected requests.
- For a preventive pipeline gate, evidence that rejection stops deployment.
- These are configured process records, not built-in Copilot Studio Submit for approval forms or PPAC Pending/Completed approvals pages. A flow triggered after an agent change is detective, not a pre-publish gate.

### Screenshot 13: Published Agent Affected by a Policy Change
**Portal Path:** Copilot Studio -> [Agent] -> Channels / Publish
**What to capture:**
- In a test environment, tighten a policy for a **blockable** connector such as HTTP, then capture published and draft error details.
- Blocked republish and, if reproduced, the runtime **DataLossPreventionViolation** error with timestamp.
- Do not move the SharePoint service connector to Blocked; it is unblockable. Copilot Studio knowledge-source connectors are distinct policy surfaces.
- Do not claim the previous published version continues serving normally; policy violations can disrupt runtime.

### Screenshot 14: Solution Promotion Pipeline
**Portal Path:** PPAC -> Deployments -> [Custom host]; Power Apps -> [Host environment] -> Deployment Pipeline Configuration
**What to capture:**
- Linked development environment and Test/Production deployment stages, including Previous Deployment Stage.
- Target Managed Environments, stage gate settings, and deployment run history.
- Environment groups organize governance rules; they are not a promotion pipeline diagram.

### Screenshot 15: Copilot Studio Publishing Audit
**Portal Path:** Microsoft Purview -> Solutions -> Audit
**What to capture:**
- Copilot Studio authoring activity **BotUpdateOperation-BotPublish**; **BotCreate** is a separate creation event.
- Actual Operation, CreationTime, user, ResultStatus, and BotId/BotSchemaName fields where present.
- Exported record correlated with the agent and test window.
- Do not require DLP status, connector usage, scan results, or approval comments in the publishing event; Microsoft does not document those fields as a combined record.

### Screenshot 16: DLP Enforcement Evidence
**Location:** Copilot Studio Channels error details and downloaded workbook
**What to capture:**
- Connector, policy name/ID, agent/environment, blocked channels, and failed publish evidence.
- Do not require a Purview activity named "DLP policy violation detected" for a blocked Copilot Studio publish.
- Capture policy-change audit evidence separately if available; it is not proof of the blocked attempt itself.

### Screenshot 17: Approval Evidence
**Location:** Configured Power Automate approval record, pipeline run, or change-ticket system
**What to capture:**
- Request ID, approver, decision, timestamp, comments, and deployment correlation.
- Do not require a Purview activity named "Approve chatbot publishing request"; preserve the supporting workflow record.

### Screenshot 18: Inventory and Evidence Hash
**Location:** Dataverse inventory export and PowerShell evidence output
**What to capture:**
- Inventory obtained from the documented Dataverse Bots table / List rows from selected environment approach, plus environment identifiers.
- CSV path and SHA-256 hash from the PowerShell playbook.
- Separate DLP violation workbook reconciliation. Inventory alone does not produce per-agent DLP-compliant/non-compliant totals.

### Screenshot 19: DLP Policy Automation
**Location:** Windows PowerShell 5.1 and PPAC policy read-back
**What to capture:**
- Pinned module version, approved policy definition, mutation confirmation, and Get-DlpPolicy read-back.
- New-DlpPolicy supports -NewPolicy; Set-DlpPolicy uses -PolicyName and -UpdatedPolicy, not -ConnectorGroups.
- Use the portal for connector classification/environment selection if an approved, version-tested automation definition is unavailable.

### Screenshot 20: Custom Connector Host URL Patterns
**Portal Path:** Power Platform Admin Center -> Security -> Data and privacy -> Data policy -> [Tenant policy] -> Custom connectors
**What to capture:**
- Ordered host URL patterns classified Business/Non-business/Blocked.
- Explicit approved host patterns and the final `*` rule classified Blocked; the initial default is Ignore, not Blocked.
- Rule ordering and saved policy. Environment policies classify individual custom connectors instead.
- HTTP endpoint filtering is a separate configuration, not an effect of custom connector host patterns.

## Verification Focus and Availability

- Microsoft documents tenant-wide DLP enforcement since early 2025 and removal of agent exemptions **since March 2025** (MC973179).
- Existing published agents can experience runtime errors as well as blocked publishing. Do not describe an old Soft-Enabled exemption as a supported tenant rollout option.
- Automatic security scans warn about the three documented risk conditions above. The retrieved Learn page does not establish a January 31, 2026 GA date or MC1217615; those release claims are not verified here.
- Approval, pipeline, and evidence collection require organization-specific configuration. Validate actual access restrictions using a non-admin author.
- No additional licensing SKU is established by this screenshot checklist. Confirm Copilot Studio, pipeline/Managed Environment, Power Automate, and Purview entitlements for the chosen implementation.
- Store all screenshots, downloaded workbooks, exports, and tenant evidence under `maintainers-local/tenant-evidence/1.28/` (gitignored), never in tracked documentation.
- Use filenames `1.28-01-*` through `1.28-20-*` matching the numbered evidence categories above; mark configured-process evidence not applicable with a reason when the implementation uses another approval path.

## Sources

Live documentation reviewed on 2026-10-14:

- [Configure data policies for agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention)
- [Troubleshoot data policy enforcement](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-dlp-troubleshooting)
- [Automatic security scan](https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-scan)
- [Publish and deploy your agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels)
- [Manage data policies](https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss)
- [Data policies for custom connectors](https://learn.microsoft.com/en-us/power-platform/admin/dlp-custom-connector-parity)
- [Audit Copilot Studio activities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio)
- [Custom pipelines host](https://learn.microsoft.com/en-us/power-platform/alm/custom-host-pipelines)
- [Extend pipelines](https://learn.microsoft.com/en-us/power-platform/alm/extend-pipelines)
- [PowerShell support](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell)
- [New-DlpPolicy](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/new-dlppolicy)
- [Set-DlpPolicy](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/set-dlppolicy)
- [Agent (bot) table](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/bot)
- [Secure Copilot Studio projects](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/sec-gov-phase3)
