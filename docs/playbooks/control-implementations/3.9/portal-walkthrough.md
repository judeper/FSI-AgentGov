# Portal Walkthrough — Control 3.9: Microsoft Sentinel Integration for AI Agent Monitoring

!!! danger "READ FIRST — Scope and Sibling Routing"
    This walkthrough covers **portal-first deployment of Microsoft Sentinel for AI agent monitoring** across Microsoft 365 Copilot, Microsoft Copilot Studio, Power Platform agents, and Entra workload identities. It is the primary operational procedure for Control 3.9 and is intended to be executed by the **Sentinel Admin** with input from the **SOC Analyst**, **AI Governance Lead**, **Entra Security Admin**, and **Power Platform Admin**.

    **In scope**

    | Topic | Where it lives |
    |-------|----------------|
    | Pre-flight roles, licensing, workspace decisions | §0 |
    | Sovereign cloud variant and compensating controls | §1 |
    | Workspace deployment via the **Defender portal** (security.microsoft.com) | §2 |
    | Data connectors (M365 / Entra human + workload SP / Defender / Defender for Cloud Apps / Copilot / Power Platform / optional App Insights) | §3 |
    | Agent-specific analytics rules (7 rules) | §4 |
    | Workbooks (AI Agent Security Posture, CA Insights, Agent Usage & Performance) | §5 |
    | Logic Apps automation playbooks (suspend agent, notify Owner + SOC, ITSM + NYDFS 500.17 timer) | §6 |
    | Per-table retention configuration with the books-and-records boundary | §7 |
    | Defender portal unified incident UX with agent enrichment | §8 |
    | Sentinel MCP Server **as optional analyst augmentation** | §9 |
    | Evidence capture, zone cadence, and examiner packet | §10 |

    **Out of scope — routed to siblings**

    | Topic | Route to |
    |-------|----------|
    | Bicep / ARM / az-cli / Graph automation of Sentinel artifacts | [powershell-setup.md](./powershell-setup.md) |
    | KQL detection-rule unit tests, dry-run alerts, and KPI verification | [verification-testing.md](./verification-testing.md) |
    | Connector ingestion lag, Logic App run failures, MCP authorization errors | [troubleshooting.md](./troubleshooting.md) |
    | Books-and-records retention (FINRA 4511 / SEC 17a-4(f)) — **NOT Sentinel** | [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |
    | Comprehensive Purview audit-log configuration (upstream of OfficeActivity) | [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
    | Runtime XPIA / jailbreak / external-threat detection at the Defender / Prompt Shields layer | [Control 1.8 — Runtime Protection and External Threat Detection](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) |
    | Conditional Access policy authorship for the CA Insights workbook | [Control 1.11 — Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) |
    | Defender AI-SPM posture scoring (the Defender feed Sentinel ingests) | [Control 1.24 — Defender AI Security Posture Management](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) |
    | Model risk re-validation triggered by Sentinel monitoring findings | [Control 2.6 — Model Risk Management Alignment with OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) |
    | Supervisory review (FINRA 3110) of Sentinel alert evidence | [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
    | Agent registry metadata used to enrich Sentinel incidents | [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
    | Incident reporting and root-cause analysis after Sentinel triages an incident | [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) |
    | Cascade of orphan-agent signals into the orphan remediation workflow | [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
    | Long-window analytics SDK that complements (not replaces) Sentinel | [Control 3.14 — Agent 365 Observability SDK](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) |

    If the task at hand is **not** a portal-driven Sentinel deployment, configuration, or operational tuning action, stop and follow the routing above before continuing.

!!! warning "Scope Limit — Operational monitoring, not books-and-records"
    Microsoft Sentinel **supports** detection, investigation, alerting evidence, and the audit-trail expectations of **NYDFS 23 NYCRR 500.06**, the incident-response-plan expectations of **NYDFS 500.16**, and the 72-hour notification timer of **NYDFS 500.17**. It also **supports** the ongoing-monitoring expectations on AI/ML models in **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** and **Federal Reserve SR 26-2 (formerly SR 11-7)** by feeding monitoring findings into MRM re-validation under [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md).

    Sentinel does **not** substitute for any of the following, and this walkthrough is not a books-and-records retention design:

    | Obligation | Owning control / surface |
    |------------|--------------------------|
    | Books-and-records retention under **FINRA Rule 4511** and **SEC Rules 17a-3 / 17a-4** (including 17a-4(f) WORM and audit-trail integrity) | [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — Purview retention labels + 17a-4(f) vendor archive |
    | Supervisory review of communications and agent outputs under **FINRA Rule 3110** | [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
    | Model risk management re-validation triggered by monitoring drift | [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) |
    | Incident reporting and RCA workflow after Sentinel raises an incident | [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) |
    | Orphaned-agent identification and remediation cascade | [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |

    **FINRA Notice 25-07** is cited in this walkthrough as **contextual industry consultation only**. It is an RFC and does **not** create binding obligations; sections that reference it are for forward-looking program planning, not compliance attestation.

    **CISA BOD 22-09** is cited as an **informative event-logging benchmark**. It is a Binding Operational Directive that applies to **federal civilian agencies**, not to private-sector financial-services firms; its EL1 / EL2 / EL3 maturity tiers are useful as a maturity yardstick for FSI logging programs but are not regulatory requirements for FSI.

!!! warning "Hedged-Language Reminder"
    This walkthrough uses **hedged compliance language** intentionally. Phrases like *"supports compliance with"*, *"helps meet"*, *"aids in"*, *"required for"*, and *"recommended to"* appear throughout. They are not stylistic — they reflect the legal reality that no Microsoft product feature, no Sentinel deployment, and no individual control can by itself satisfy a regulatory obligation. Implementation requires the firm's legal, compliance, and risk functions to interpret the regulation against the firm's facts. Organizations should verify each compliance assertion in this document with their compliance counsel before relying on it for any examination, attestation, or filing.

    If you are tempted to rewrite a sentence to say *"ensures compliance with"*, *"guarantees"*, *"will prevent"*, or *"eliminates risk"* — **stop**. Those phrases create legal liability and overstate what software can do. Use the hedged forms.

!!! warning "Sovereign Cloud Availability (GCC / GCC High / DoD)"

    | Capability | Commercial | GCC | GCC High | DoD | Compensating control if unavailable |
    |------------|------------|-----|----------|-----|-------------------------------------|
    | Sentinel workspace via Defender portal | GA | GA | GA (rollout) | GA (rollout) | Use Azure portal path until Defender portal parity confirmed |
    | Microsoft 365 (OfficeActivity / CopilotInteraction) connector | GA | GA | GA | Limited | §1 manual-export worksheet; ingest via custom collector if necessary |
    | Entra `SigninLogs` connector | GA | GA | GA | GA | n/a |
    | Entra `AADServicePrincipalSignInLogs` connector | GA | GA | GA | GA | n/a |
    | Microsoft 365 Defender (XDR) connector | GA | GA | GA | Limited | §1 manual-export worksheet |
    | Defender for Cloud Apps connector | GA | GA | Limited | Not available | §1 manual-export worksheet; reduce shadow-agent detection coverage and document gap |
    | Microsoft Copilot connector (Defender portal) | GA | GA (parity may lag commercial 30–90 days) | Preview / Limited | Not available at time of writing | Document feature unavailability as a product-availability gap; rely on OfficeActivity CopilotInteraction stream for partial coverage |
    | Power Platform Admin Activity connector | GA | GA | GA | Limited | Pull `PowerPlatformAdminActivity` via Purview Audit export if connector unavailable |
    | Application Insights link (custom Copilot Studio telemetry) | GA | GA | GA | GA | n/a (but verify regional App Insights availability) |
    | Sentinel MCP Server | Preview / GA (commercial) | Limited | Not available at time of writing | Not available | **Skip §9 entirely** — MCP is optional augmentation; document unavailability as a product-availability gap, not a control gap |
    | Logic Apps for SOAR playbooks | GA | GA | GA | GA (regional) | n/a |

    Verify rollout status against the Microsoft 365 roadmap, the Microsoft Sentinel sovereign-cloud release notes, and the **Microsoft Learn product-availability matrix** before each control execution. Sovereign tenants must record any unavailable capability on the §1 compensating-control worksheet as the primary evidence artifact until parity is confirmed. Unavailability of a Microsoft product feature in a sovereign cloud is a **product-availability gap**, not a Control 3.9 deficiency.

!!! info "Entra schema gotcha — `AADServicePrincipalSignInLogs` is a distinct table"
    The Entra ID connector exposes **multiple sign-in tables**. The default mental model — "all sign-ins are in `SigninLogs`" — is **wrong** for AI agent monitoring, and this is the single most common configuration error in Control 3.9 deployments.

    | Table | What it contains | What it does NOT contain |
    |-------|------------------|---------------------------|
    | `SigninLogs` | Interactive and non-interactive **human user** sign-ins | Service principal / managed-identity / workload-identity sign-ins (incl. agent identities created via Entra Agent ID) |
    | `AADNonInteractiveUserSignInLogs` | Non-interactive **human user** sign-ins (e.g., refresh tokens) | Service principal / managed-identity sign-ins |
    | `AADServicePrincipalSignInLogs` | Service-principal sign-ins (incl. **AI agents**, app registrations, MCP tools acting as confidential clients) | Human user sign-ins |
    | `AADManagedIdentitySignInLogs` | Sign-ins from system / user-assigned managed identities | Human user sign-ins |
    | `AuditLogs` | Directory changes (consent grants, role assignments, app registrations) | Sign-in events |

    **If your detection rule queries only `SigninLogs`, you will not see agent activity.** Every analytics rule in §4 that targets agent / workload identity behavior must query `AADServicePrincipalSignInLogs` (and where applicable `AADManagedIdentitySignInLogs`). The ingestion of these tables is **not** enabled by default with the Entra connector — you must explicitly select them at §3.2.

!!! info "License and Program Requirements"

    | Capability | License / SKU |
    |------------|---------------|
    | Microsoft Sentinel workspace (analytics + automation + workbooks) | Per-GB or commitment-tier ingestion + Sentinel surcharge; M365 E5 customers receive a per-user benefit toward eligible M365 data sources |
    | Microsoft Sentinel via the Defender portal (unified XDR experience) | Microsoft 365 Defender (E5 or E5 Security) entitlement plus Sentinel workspace |
    | Defender for Cloud Apps connector | Defender for Cloud Apps standalone or E5 / E5 Security |
    | Microsoft Copilot connector (Defender portal) | M365 Copilot tenant license + Defender for Cloud Apps entitlement |
    | Application Insights (Copilot Studio custom telemetry path) | Azure Monitor Application Insights — pay-as-you-go ingestion |
    | Sentinel MCP Server (optional augmentation) | Sentinel data-lake tier + MCP server license — **verify current pricing on the Microsoft Sentinel pricing page before enabling** |
    | Logic Apps (SOAR playbooks) | Consumption-tier or Standard-tier Logic Apps |
    | Entra `AADServicePrincipalSignInLogs` ingestion | Entra ID P1 minimum; P2 recommended for full sign-in risk telemetry |

!!! tip "Portal Navigation May Shift"
    Microsoft updates portal blade names and navigation regularly — particularly during the migration of Sentinel from the Azure portal into the Defender portal. Where this walkthrough cites a path such as **Defender portal → Microsoft Sentinel → Configuration → Data connectors**, treat the path as descriptive, not authoritative. If the blade has moved, anchor on the **page title** rather than the breadcrumb. Capture the new path in [troubleshooting.md](./troubleshooting.md) so it can be promoted into the next revision.

    The **Sentinel Azure portal experience deprecation date is March 31, 2027** at the time of writing. New deployments executed after early 2026 should use the **Defender portal** (`security.microsoft.com`) as the default surface. The Azure portal path (`portal.azure.com → Microsoft Sentinel`) remains supported until the deprecation date for backward compatibility and for blades that have not yet reached Defender-portal parity, but should not be the default for greenfield deployments.

## Document Map

| § | Section | Primary surface | Verification criterion |
|---|---------|-----------------|------------------------|
| 0 | Pre-flight prerequisites, roles, workspace decisions | Entra PIM + Azure portal | VC-1 |
| 1 | Sovereign-cloud variant and compensating controls | Manual worksheet | VC-2 |
| 2 | Workspace deployment via Defender portal | security.microsoft.com → Microsoft Sentinel | VC-3 |
| 3 | Data connectors (M365, Entra, Defender, Cloud Apps, Copilot, Power Platform, App Insights) | Defender portal → Configuration → Data connectors | VC-4 |
| 4 | Analytics rules — 7 AI-specific detections | Defender portal → Configuration → Analytics | VC-5 |
| 5 | Workbooks — Security Posture, CA Insights, Agent Usage | Defender portal → Threat management → Workbooks | VC-6 |
| 6 | Logic Apps automation playbooks (3 examples) | Defender portal → Configuration → Automation | VC-7 |
| 7 | Per-table retention with the books-and-records boundary | Log Analytics workspace → Tables | VC-8 |
| 8 | Incident investigation UX in the Defender portal | Defender portal → Incidents | VC-9 |
| 9 | Sentinel MCP Server (optional analyst augmentation) | Defender portal → Sentinel MCP | VC-10 |
| 10 | Evidence capture, zone cadence, examiner packet | All portals + Purview evidence library | VC-11 |

The numbering of analytics rules in §4 (R1–R7) and Logic Apps playbooks in §6 (P1–P3) is referenced from [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) and from [verification-testing.md](./verification-testing.md). Do not renumber locally — the numbering is the audit handle.

---

## §0. Pre-flight — Roles, Licensing, Workspace Decisions

Treat this section as a checklist that must be completed before opening the Defender portal. Skipping it is the most common cause of mid-deployment rework.

### 0.1 Confirm canonical roles and PIM activation

Use the canonical role names from the [role catalog](../../../reference/role-catalog.md). Map them to the operators executing this walkthrough.

| Canonical role | Used for | Where assigned | Activation expectation |
|----------------|----------|----------------|------------------------|
| **Sentinel Admin** (Microsoft Sentinel Contributor + Log Analytics Contributor on the workspace resource group) | Workspace creation, connector enablement, analytics-rule authoring, workbook publishing, Logic App linkage | Azure RBAC on the Sentinel resource group | PIM-eligible, max 8h activation, justification + ticket required |
| **SOC Analyst** (Microsoft Sentinel Responder) | Incident triage, comments, status updates, playbook on-demand triggers | Azure RBAC on the Sentinel resource group | PIM-eligible, max 8h |
| **Entra Security Admin** | Enabling diagnostic settings on Entra ID, including the workload-identity sign-in tables | Entra ID role | PIM-eligible, max 4h |
| **Purview Compliance Admin** | Verifying upstream Purview audit-log enablement (feeds OfficeActivity / CopilotInteraction) | Purview role group | PIM-eligible, max 8h |
| **AI Governance Lead** | Approves analytics-rule thresholds; signs off on §10 evidence packet | Azure AD group + RACI documented in [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Standing assignment; sign-off via change ticket |
| **Power Platform Admin** | Enables Power Platform admin-activity logging and Copilot Studio diagnostics export | Power Platform admin role | PIM-eligible, max 8h |
| **Compliance Officer** | Reviews retention configuration in §7; co-signs the §10 evidence packet quarterly | Standing role | Standing |
| **CISO** | Final approver of §6 automation playbooks that suspend agents (compensating-control authority) | Standing role | Standing |
| **Agent Owner** | Receives Logic App playbook P2 notification (Teams adaptive card) and acknowledges within the §10 SLA | Per-agent metadata in agent registry ([Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)) | Per-agent assignment |

!!! tip "PIM tip"
    Configure all five Sentinel-related Azure roles as **eligible**, not active. Permanent active assignments to Sentinel Contributor are an audit finding under NYDFS 500.07 (least-privilege) review.

[Screenshot anchor: ]

### 0.2 Confirm licensing and ingestion budget

Open the **Microsoft 365 admin center → Billing → Licenses** view and verify the following before proceeding:

1. M365 E5 (or E5 Security) is assigned to the SOC user population that will operate the Defender portal.
2. Defender for Cloud Apps is licensed.
3. Microsoft 365 Copilot license count matches the population that will be monitored via the Copilot connector.
4. Open **Azure portal → Cost Management → Budgets** in the Sentinel subscription and confirm an ingestion budget exists with an alert at 80% of the monthly cap. Sentinel ingestion costs scale with `OfficeActivity` and `CloudAppEvents` volume in particular; uncapped ingestion is a common audit finding.

[Screenshot anchor: ]

### 0.3 Workspace decisions — single vs. multi, region, retention default

Document the following decisions in the change-management ticket **before** §2:

| Decision | Recommended default | Rationale |
|----------|---------------------|-----------|
| Workspace count | One Sentinel workspace per **regulated business unit** (broker-dealer, bank, RIA), not one per environment | Aligns with FINRA Rule 3110 supervisory-system delineation; simplifies books-and-records segregation under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |
| Region | Same region as the M365 tenant's primary data residency (e.g., East US 2 for US commercial; USGov Virginia for GCC High) | Avoids cross-region egress fees and simplifies NYDFS 500.11 third-party data-flow diagrams |
| Default interactive retention | **180 days** | Operational triage window; aligns with NYDFS 500.06 audit-trail expectations without overspending |
| Long-term archive in Sentinel | **Up to 12 years** for select tables | NYDFS 500.06 audit-trail floor + matches FINRA / SEC books-and-records statutory floor — but see §7 books-and-records boundary admonition |
| Customer-managed keys (CMK) | Enabled for FSI tenants holding NPI under GLBA | Simplifies §501(b) Safeguards Rule attestations |
| Lock level | `CanNotDelete` on the workspace resource group | Prevents accidental deletion of audit-trail data; required by SEC 17a-4(f) integrity expectations |

!!! example "Examiner Evidence Box — §0 Pre-flight"
    Capture the following for the §10 evidence packet:

    - PIM role-assignment screenshot (eligible, not active) for Sentinel Admin, SOC Analyst, Entra Security Admin
    - Cost budget screenshot showing 80% alert threshold
    - Change-management ticket containing the workspace-decisions table above, signed by the AI Governance Lead and the Sentinel Admin
    - Confirmation that resource-group lock `CanNotDelete` is in place (Azure portal → Resource group → Locks)

!!! tip "Cross-Reference"
    The role-to-control mapping in §0.1 originates in [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md). The Agent Owner field used by Logic App playbook P2 (§6.2) is sourced from the Agent 365 registry; if that registry is not populated for an agent, the playbook degrades to a SOC-only notification — see [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

---

## §1. Sovereign-Cloud Variant and Compensating-Control Worksheet

This walkthrough was authored against **Microsoft 365 commercial cloud**. If the deployment target is **GCC**, **GCC High**, or **DoD**, complete this section before §2 and use the worksheet output as the authoritative scope statement for the deployment.

### 1.1 Determine cloud surface

Open the M365 admin center → **Settings → Org settings → Organization profile → Data location**. Capture the value (`US`, `GCC`, `GCCH`, `DoD`). The data-location string drives every subsequent connector availability decision.

[Screenshot anchor: ]

### 1.2 Compensating-control worksheet

For each capability listed in the **Sovereign Cloud Availability** table at the top of this document, fill in this worksheet row in the change-management ticket:

| Capability | Available in this cloud? | If no, compensating control | Owning role | Re-check date |
|------------|--------------------------|-----------------------------|-------------|---------------|
| Microsoft Copilot connector | Yes / No / Limited | If No: ingest CopilotInteraction subset via OfficeActivity; flag detection-coverage gap on the §10 examiner packet | Sentinel Admin | Quarterly |
| Defender for Cloud Apps connector | Yes / No / Limited | If No: replace shadow-agent detection (R6) with Power Platform admin-activity-only detection; reduce coverage rating from "Full" to "Partial" | Sentinel Admin + AI Governance Lead | Quarterly |
| Sentinel MCP Server | Yes / No | If No: skip §9 entirely; SOC analysts use the standard Defender portal incident UX | Sentinel Admin | Quarterly |
| `AADServicePrincipalSignInLogs` | Yes (all clouds at time of writing) | n/a | Entra Security Admin | Annual |

The completed worksheet is the **primary evidence artifact** that an unavailable Microsoft product feature in a sovereign cloud is documented as a **product-availability gap**, not a Control 3.9 deficiency. Examiners will accept a documented product-availability gap with a quarterly re-check cadence; they will not accept silent omission.

!!! example "Examiner Evidence Box — §1 Sovereign Cloud"
    - Data-location screenshot
    - Completed compensating-control worksheet stored in the Purview evidence library tagged `Control-3.9 / Sovereign-Variant`
    - Quarterly re-check ticket history (last four quarters minimum)

---

## §2. Workspace Deployment via the Defender Portal

This section deploys the Sentinel workspace and onboards it into the Defender portal unified experience.

!!! info "Surface choice"
    The Defender portal (`security.microsoft.com`) is the **default** surface for new Sentinel deployments at the time of writing. The Azure portal experience for Microsoft Sentinel is scheduled for **deprecation on March 31, 2027**. Existing deployments executing before early 2026 may continue to use the Azure portal path; new deployments should adopt the Defender portal as the primary surface to avoid a re-platforming task in 2026–2027.

### 2.1 Create the Log Analytics workspace

1. Open the **Azure portal** → **Log Analytics workspaces** → **+ Create**.
2. Subscription: the Sentinel subscription identified in §0.3.
3. Resource group: a dedicated RG (e.g., `rg-sentinel-prod-eus2`). Apply the `CanNotDelete` lock from §0.3 after creation.
4. Workspace name: follow the firm's naming convention (e.g., `law-sentinel-bd-prod-eus2` for the broker-dealer business unit).
5. Region: the value selected in §0.3.
6. Tags: at minimum `BusinessUnit`, `DataClassification=Confidential-NPI`, `Control=3.9`, `Owner=<Sentinel-Admin-DL>`, `CostCenter`.
7. Click **Review + create**, then **Create**.

[Screenshot anchor: ]

### 2.2 Enable Microsoft Sentinel on the workspace

1. In the Azure portal, search for **Microsoft Sentinel** and open the service.
2. Click **+ Create** → select the workspace from §2.1 → **Add**.
3. Wait for the Sentinel onboarding to complete (typically 1–3 minutes).

[Screenshot anchor: ]

### 2.3 Onboard Sentinel into the Defender portal

1. Navigate to **`security.microsoft.com`** in a private browser session as the Sentinel Admin.
2. In the left navigation, expand **Microsoft Sentinel**. If Sentinel is not yet visible, the Defender portal will offer an **onboarding card** — click **Connect a workspace**.
3. Select the workspace from §2.1 and click **Next → Connect**.
4. Wait for the unified-portal onboarding banner to switch from "Onboarding" to "Connected".

[Screenshot anchor: ]

!!! tip "Multi-workspace tenants"
    The Defender portal supports a **primary workspace** plus secondary workspace views. Set the regulated business-unit workspace selected in §0.3 as the primary. Cross-workspace KQL is supported via the `workspace()` operator but adds latency and cost; design analytics rules to live in the workspace whose data they query.

### 2.4 Apply the resource-group delete lock and tag governance

1. Azure portal → resource group from §2.1 → **Locks** → **+ Add** → Lock type: **Delete** → Lock name: `lock-sentinel-prod-no-delete` → Notes: "Control 3.9 / SEC 17a-4(f) audit-trail integrity / NYDFS 500.06" → **OK**.
2. Confirm tags from §2.1 propagated to the workspace, the Sentinel solution, and any auto-created Logic Apps resource group.

!!! example "Examiner Evidence Box — §2 Workspace Deployment"
    - Workspace properties blade (showing region, retention default, CMK if applicable)
    - Resource-group lock blade showing `CanNotDelete`
    - Defender portal banner showing the workspace as **Connected**
    - Tag inheritance screenshot

!!! tip "Cross-Reference"
    The CMK decision in §0.3 / §2.1 is owned by the broader key-management program, not by Control 3.9. If the tenant is using customer-managed keys for log data, document the Key Vault and key reference here and cross-link to the firm's key-management runbook. If the firm has not yet deployed CMK, that is a separate program decision and not a Control 3.9 blocker.

---

## §3. Data Connectors — The Ingestion Backbone

This section enables the seven data connectors that feed every analytics rule, workbook, and Logic App in this walkthrough. Each subsection follows the same pattern: portal navigation, connector enablement, table verification, and ingestion sanity check.

!!! warning "Order matters"
    Enable connectors **in the order presented** (3.1 → 3.7). The Entra connector (3.2) must precede the analytics rules in §4 because the agent-identity tables it produces are queried by every workload-identity rule. The Microsoft 365 connector (3.1) must precede the Copilot connector (3.5) because CopilotInteraction enrichment depends on OfficeActivity user-context resolution.

### 3.1 Microsoft 365 connector (OfficeActivity, including CopilotInteraction)

The M365 connector ingests the unified Purview audit log into the `OfficeActivity` table, which includes the `CopilotInteraction` record type for Microsoft 365 Copilot interactions across Word, Excel, PowerPoint, Outlook, Teams, and the BizChat surface.

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Data connectors**.
2. Search for **Microsoft 365** (formerly Office 365). Select the connector and click **Open connector page**.
3. In the **Configuration** section, enable telemetry for **Exchange**, **SharePoint**, **Teams**, and **General** (the General record type carries CopilotInteraction).
4. Click **Apply Changes**.
5. Wait 15–30 minutes, then run the following KQL in **Logs**:

    ```kql
    OfficeActivity
    | where TimeGenerated > ago(1h)
    | summarize Count = count() by RecordType
    | order by Count desc
    ```

    Expected: a non-zero count for `CopilotInteraction` if the tenant has active Copilot users. If the count is zero after 24 hours, route to [troubleshooting.md](./troubleshooting.md#tc-03-microsoft-copilot-connector-unavailable-in-gcc-high).

[Screenshot anchor: ]

!!! info "Upstream dependency"
    The M365 connector reads from the **Purview unified audit log**. If audit logging is not enabled at the Purview level, the connector will succeed at the portal layer but produce no data. Verify upstream audit-logging configuration in [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) before treating an empty `OfficeActivity` table as a Sentinel issue.

### 3.2 Microsoft Entra ID connector (human + workload identities)

This is the most error-prone connector in the entire walkthrough. Read the schema gotcha admonition at the top of this document before proceeding.

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Data connectors** → search **Microsoft Entra ID** → **Open connector page**.
2. In the **Configuration** pane, you will see a list of log types. **Select all of the following** — do not accept the default of `SigninLogs` only:
    - `SigninLogs` (interactive human sign-ins)
    - `AuditLogs` (directory changes — feeds R5 unusual consent grants)
    - `NonInteractiveUserSignInLogs`
    - `ServicePrincipalSignInLogs` ← **CRITICAL FOR AGENT MONITORING** (writes to `AADServicePrincipalSignInLogs`)
    - `ManagedIdentitySignInLogs` (writes to `AADManagedIdentitySignInLogs`)
    - `ProvisioningLogs`
    - `ADFSSignInLogs` (only if hybrid AD FS is in scope)
    - `RiskyUsers`, `UserRiskEvents`, `RiskyServicePrincipals`, `ServicePrincipalRiskEvents` (Entra ID P2)
3. Click **Apply Changes**.
4. Wait 15–30 minutes, then verify each table:

    ```kql
    union withsource = T *
    | where T in ("SigninLogs", "AADServicePrincipalSignInLogs", "AADManagedIdentitySignInLogs", "AuditLogs")
    | where TimeGenerated > ago(1h)
    | summarize Count = count() by T
    ```

    Expected: non-zero rows for each table. `AADServicePrincipalSignInLogs` should be non-zero in any tenant with active service principals; if zero, the most likely cause is that the checkbox in step 2 was not selected — return to step 2 and verify.

[Screenshot anchor: ]

!!! info "Diagnostic settings vs. data connector"
    The Defender-portal Entra connector is implemented under the hood as a **diagnostic setting** on the Entra tenant pointing at the Sentinel workspace. Some FSI tenants pre-create this diagnostic setting via Azure Policy. If the Entra connector page shows **"This connector is already configured"** but the table list is incomplete, open **Entra portal → Diagnostic settings** and edit the existing setting to add the missing log types. The Defender portal will reflect the change within a few minutes.

### 3.3 Microsoft Defender XDR connector

The Microsoft Defender XDR (M365D) connector ingests Defender alerts and raw device telemetry into Sentinel. For Control 3.9, the alert stream is the primary use; the device telemetry is optional and increases ingestion cost.

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Data connectors** → search **Microsoft Defender XDR** → **Open connector page**.
2. Enable **Connect incidents and alerts**. This streams the unified Defender incident queue into Sentinel.
3. Under **Connect events**, enable at minimum:
    - `AlertInfo`, `AlertEvidence` (alert metadata, required)
    - `DeviceEvents` (optional; high volume — gate on cost-budget headroom from §0.2)
    - `EmailEvents`, `EmailUrlInfo`, `EmailAttachmentInfo` (recommended for Copilot phishing-related detections)
    - `CloudAppEvents` (covered in §3.4 — disable here if §3.4 is enabled)
4. Disable **bi-directional sync** of incidents until §8 has been validated; bi-directional sync without a tested investigation runbook can cause incident-status thrash.
5. Click **Apply Changes**.
6. Verify:

    ```kql
    AlertInfo
    | where TimeGenerated > ago(24h)
    | summarize Count = count() by ServiceSource
    ```

    Expected: non-zero rows for Defender for Endpoint, Defender for Office 365, and (if licensed) Defender for Cloud Apps.

[Screenshot anchor: ]

!!! tip "Cross-Reference"
    The Defender AI-SPM posture findings ingested via this connector originate in [Control 1.24 — Defender AI Security Posture Management](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md). If AI-SPM is not yet enabled in the Defender portal, the connector will succeed but the AI-posture rows in the §5 workbook will be empty.

### 3.4 Defender for Cloud Apps connector

The Defender for Cloud Apps (MDA) connector writes to `CloudAppEvents` and is the primary feed for shadow-agent detection (R6) and SaaS-app risk for AI tools.

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Data connectors** → search **Microsoft Defender for Cloud Apps** → **Open connector page**.
2. Enable **CloudAppEvents** stream.
3. Click **Apply Changes**.
4. Verify:

    ```kql
    CloudAppEvents
    | where TimeGenerated > ago(1h)
    | summarize Count = count() by Application
    | order by Count desc
    | take 25
    ```

    Expected: a populated list of cloud apps. If `Microsoft Copilot` or known third-party AI applications (e.g., ChatGPT, Claude, Gemini) appear, the shadow-AI detection (R6) will function.

[Screenshot anchor: ]

!!! warning "Sovereign clouds"
    Defender for Cloud Apps connector is **not** available in DoD and is **limited** in GCC High at the time of writing. If unavailable, document the gap on the §1 worksheet and switch R6 (shadow-agent detection) to the Power Platform admin-activity-only variant.

### 3.5 Microsoft Copilot connector (Defender portal)

The Microsoft Copilot connector (GA in commercial cloud at the time of writing) provides richer Copilot signals than what is available via OfficeActivity alone — including XPIA flags, prompt-shield outcomes, and sensitivity-label propagation.

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Data connectors** → search **Microsoft Copilot** → **Open connector page**.
2. Click **Connect**. Authorize the connector with the Sentinel Admin credentials.
3. Click **Apply Changes**.
4. Verify (table name and schema may evolve — check the connector page for current table reference):

    ```kql
    OfficeActivity
    | where RecordType == "CopilotInteraction"
    | where TimeGenerated > ago(1h)
    | extend XPIAFlag = tostring(parse_json(CopilotEventData).XPIAFlag)
    | summarize Total = count(), XPIAFlagged = countif(isnotempty(XPIAFlag)) by bin(TimeGenerated, 15m)
    ```

    Expected: non-zero `Total` for an active tenant; `XPIAFlagged` may be zero in normal operation and is expected to be rare.

[Screenshot anchor: ]

!!! info "Connector evolution"
    The Microsoft Copilot connector schema is evolving as Microsoft adds prompt-injection telemetry, plugin/connector telemetry, and agent-identity attribution. Re-verify the schema each quarter against Microsoft Learn before committing analytics-rule KQL to production.

### 3.6 Power Platform admin activity connector

The Power Platform connector writes to `PowerPlatformAdminActivity` and is the primary feed for DLP-policy-change detection (R4) and Copilot Studio agent lifecycle events.

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Data connectors** → search **Power Platform** → **Open connector page**.
2. Authorize with the **Power Platform Admin** account.
3. Enable the following streams:
    - `PowerPlatformAdminActivity` (admin-center actions, DLP policy changes, environment changes)
    - `PowerPlatformDlpActivity` (DLP policy violations / blocks)
    - `CopilotStudioActivity` (where available — Copilot Studio agent publish, share, deletion events)
4. Click **Apply Changes**.
5. Verify:

    ```kql
    PowerPlatformAdminActivity
    | where TimeGenerated > ago(24h)
    | summarize Count = count() by EventOriginalType
    | order by Count desc
    ```

    Expected: rows including `CreateDlpPolicy`, `UpdateDlpPolicy`, `DeleteDlpPolicy`, `CreateEnvironment`, etc.

[Screenshot anchor: ]

!!! tip "Cross-Reference"
    The DLP-policy-change detection (R4) depends on this connector. The DLP policies themselves are authored under the Power Platform DLP control surface; if Sentinel detects a DLP-policy change, the change-management ticket associated with that DLP edit should be retrievable from the Power Platform admin center audit log as well.

### 3.7 Application Insights — Copilot Studio custom telemetry (optional)

Copilot Studio supports an **Application Insights** export for richer per-conversation telemetry than what flows into OfficeActivity. This is optional and best-suited to high-value enterprise agents in Zone 3.

1. Open **Copilot Studio** (`copilotstudio.microsoft.com`) as the agent maker.
2. Open the agent → **Settings** → **Advanced** → **Application Insights**.
3. Paste the Application Insights connection string for the App Insights resource that the firm has provisioned for agent telemetry. (Provisioning the App Insights resource itself is outside the scope of this walkthrough.)
4. Toggle **Log activities** = **On**.
5. Toggle **Log sensitive activity properties** = **On** for Zone 2 / Zone 3 agents only after a privacy review by the Compliance Officer; in Zone 1 leave this **Off**.
6. Click **Save**.
7. In the **Power Platform admin center** (`admin.powerplatform.microsoft.com`), open the environment containing the agent → **Settings** → **Product** → **Features** → set **Allow conversation transcripts** = **On** if the firm has approved transcript capture under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
8. In the **Defender portal** → **Microsoft Sentinel** → **Configuration** → **Data connectors** → search **Azure Monitor / Application Insights** → connect the App Insights resource to the Sentinel workspace via the diagnostic-settings path.

[Screenshot anchor: ]

!!! warning "Records-retention boundary"
    Application Insights is an **operational telemetry store**. It is **not** an SEC 17a-4(f) compliant records archive. Conversation transcripts captured through this path must be evaluated against the firm's books-and-records policy under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). If the transcripts qualify as books-and-records (e.g., communications with customers about securities), the firm must route a copy to the 17a-4(f) WORM vendor archive — App Insights alone does **not** meet the records-integrity requirement of SEC Rule 17a-4(f). Organizations should verify this routing with their compliance counsel before enabling **Allow conversation transcripts** on customer-facing agents.

!!! example "Examiner Evidence Box — §3 Data Connectors"
    For each of the seven connectors above, capture:

    - The **Open connector page** view showing **Connected** / **Last data received** timestamps
    - The verification KQL output showing non-zero rows in each expected table
    - For the Entra connector specifically, a screenshot of the diagnostic-settings page showing **all** sign-in log types selected (this is the single most-asked screenshot in NYDFS audit-trail reviews)
    - For the Application Insights connector, the privacy-review sign-off ticket from §3.7

!!! tip "Cross-Reference"
    Connector ingestion lag, "0 rows" verification failures, and authorization errors are routed to [troubleshooting.md](./troubleshooting.md). Bicep / Terraform automation of the connector enablement is in [powershell-setup.md](./powershell-setup.md) — note that several connectors (Microsoft Copilot, Power Platform) currently have **no** ARM/Bicep API and must be enabled via the portal even in IaC-first shops.

---

## §4. Analytics Rules — Seven AI-Specific Detections

This section creates the seven analytics rules that constitute the operational detection floor for Control 3.9. Each rule follows the same authoring pattern in the Defender portal.

!!! info "Rule numbering is the audit handle"
    Rule numbers R1–R7 are referenced from [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md), from [verification-testing.md](./verification-testing.md) (which contains the dry-run / unit-test cases for each rule), and from the §10 evidence packet. Do not renumber locally.

### 4.0 Common authoring pattern

For each rule below, use this navigation:

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Analytics** → **+ Create** → **Scheduled query rule**.
2. **General** tab: paste the rule name, description, and tactics from the rule subsection. Severity per the table.
3. **Set rule logic** tab: paste the KQL into the **Rule query** box. Configure the **Query scheduling** and **Alert threshold** per the rule.
4. **Entity mapping**: map at minimum `Account` (UPN), `IP` (IPAddress), and where present `CloudApplication` and a custom `Agent` entity.
5. **Incident settings**: enable incident creation and **alert grouping** as specified per rule (e.g., group by `Account` over 1h).
6. **Automated response** tab: where indicated, attach the Logic App playbook from §6.
7. **Review and create**.

[Screenshot anchor: ]

### 4.1 R1 — Prompt-injection / jailbreak indicator (XPIA)

| Field | Value |
|-------|-------|
| Severity | High |
| MITRE tactic | Initial Access, Defense Evasion |
| Frequency | Every 5 minutes |
| Lookback | 30 minutes |
| Threshold | ≥ 1 event |
| Auto-response | Logic App **P1 Suspend Agent** (gated — only triggers on confirmed Defender alert; see §6.1) |

```kql
let lookback = 30m;
OfficeActivity
| where TimeGenerated > ago(lookback)
| where RecordType == "CopilotInteraction"
| extend EventData = parse_json(CopilotEventData)
| extend XPIAFlag = tostring(EventData.XPIAFlag)
| extend PromptShieldOutcome = tostring(EventData.PromptShieldOutcome)
| where isnotempty(XPIAFlag) or PromptShieldOutcome in ("Blocked", "Flagged")
| extend AgentId = tostring(EventData.AgentId), 
         ConversationId = tostring(EventData.ConversationId),
         Account = UserId
| project TimeGenerated, Account, AgentId, ConversationId, XPIAFlag, PromptShieldOutcome, ClientIP
```

!!! info "Detection caveat"
    This rule **detects an XPIA / prompt-shield signal raised by the Microsoft Copilot runtime**. It does not detect prompt injection at agents that bypass the Copilot prompt-shield layer (e.g., custom Copilot Studio agents that use external LLMs without shield integration). Runtime-layer protection across all agent surfaces is owned by [Control 1.8 — Runtime Protection and External Threat Detection](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md). Sentinel R1 is the **monitoring** layer; it aids in detection but does not by itself prevent prompt injection.

### 4.2 R2 — Anomalous connector / MCP tool use by an agent

Detects an agent invoking a connector or MCP tool that is outside its normal baseline (sudden new connector, sharp volume spike, or use of a connector flagged as high-risk in Power Platform DLP).

| Field | Value |
|-------|-------|
| Severity | Medium |
| MITRE tactic | Discovery, Collection |
| Frequency | Every 30 minutes |
| Lookback | 24 hours, baseline 14 days |
| Threshold | ≥ 3 anomalous invocations within lookback |
| Auto-response | Logic App **P2 Notify Owner + SOC** |

```kql
let baselineWindow = 14d;
let lookback = 24h;
let baseline = PowerPlatformAdminActivity
    | where TimeGenerated between (ago(baselineWindow) .. ago(lookback))
    | where EventOriginalType in ("InvokeConnector", "InvokeMcpTool")
    | summarize BaselineCount = count() by AgentId = tostring(parse_json(EventData).AgentId), 
                                            ConnectorName = tostring(parse_json(EventData).ConnectorName);
PowerPlatformAdminActivity
| where TimeGenerated > ago(lookback)
| where EventOriginalType in ("InvokeConnector", "InvokeMcpTool")
| extend AgentId = tostring(parse_json(EventData).AgentId),
         ConnectorName = tostring(parse_json(EventData).ConnectorName),
         Account = UserId
| summarize RecentCount = count() by AgentId, ConnectorName, Account
| join kind=leftouter (baseline) on AgentId, ConnectorName
| where isnull(BaselineCount) or RecentCount > BaselineCount * 5
| where RecentCount >= 3
| project AgentId, ConnectorName, Account, RecentCount, BaselineCount
```

[Screenshot anchor: ]

### 4.3 R3 — After-hours privileged agent activity

Detects a service-principal sign-in by an agent flagged as **privileged** (membership in an Entra group such as `sg-agents-privileged`) outside of business hours.

| Field | Value |
|-------|-------|
| Severity | Medium |
| MITRE tactic | Persistence, Privilege Escalation |
| Frequency | Every 15 minutes |
| Lookback | 1 hour |
| Threshold | ≥ 1 event |
| Auto-response | Logic App **P2 Notify Owner + SOC** |

```kql
let businessStart = 7;
let businessEnd = 19;
let timezoneOffset = -5h; // adjust to firm primary timezone
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(1h)
| extend LocalHour = datetime_part("hour", TimeGenerated + timezoneOffset)
| where LocalHour < businessStart or LocalHour >= businessEnd
| where ServicePrincipalName has_any (dynamic(["agent-", "copilot-", "mcp-"]))
   or ServicePrincipalId in (
       // populate from Entra group membership of sg-agents-privileged via watchlist
       _GetWatchlist("PrivilegedAgents") | project ServicePrincipalId
   )
| project TimeGenerated, ServicePrincipalName, ServicePrincipalId, IPAddress, ResourceDisplayName, ConditionalAccessStatus
```

!!! tip "Watchlist pattern"
    Maintain the privileged-agent list as a Sentinel **Watchlist** (Defender portal → Microsoft Sentinel → Configuration → Watchlists). The watchlist is sourced from the Agent 365 registry ([Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)) on a daily refresh. Embedding the list inline in the rule KQL is an anti-pattern that breaks change management.

### 4.4 R4 — DLP-policy change or bypass on Power Platform

Detects creation, modification, or deletion of a Power Platform DLP policy, and detects DLP-policy bypass attempts.

| Field | Value |
|-------|-------|
| Severity | High (delete / bypass) / Medium (create / update) |
| MITRE tactic | Defense Evasion, Impact |
| Frequency | Every 15 minutes |
| Lookback | 1 hour |
| Threshold | ≥ 1 event |
| Auto-response | Logic App **P3 ITSM + NYDFS 500.17 timer** (delete / bypass only) |

```kql
union 
(
    PowerPlatformAdminActivity
    | where TimeGenerated > ago(1h)
    | where EventOriginalType in ("DeleteDlpPolicy", "UpdateDlpPolicy", "CreateDlpPolicy")
    | extend PolicyName = tostring(parse_json(EventData).PolicyName),
             ChangeType = EventOriginalType,
             Account = UserId
    | project TimeGenerated, ChangeType, PolicyName, Account, ClientIP
),
(
    PowerPlatformDlpActivity
    | where TimeGenerated > ago(1h)
    | where ActionType == "PolicyBypassAttempt"
    | extend PolicyName = tostring(parse_json(AdditionalFields).PolicyName),
             ChangeType = "BypassAttempt",
             Account = UserId
    | project TimeGenerated, ChangeType, PolicyName, Account, ClientIP
)
```

!!! warning "Sensitive change"
    DLP policy deletes are a **Tier-0 administrative action** for any Power Platform tenant in scope of GLBA Safeguards Rule §314.4(c)(8) (audit trails for security events). The change-management process must require dual approval for DLP-policy deletes; if Sentinel detects a deletion **without** a corresponding approved change ticket, treat it as a potential insider threat and escalate per the firm's incident-response plan ([Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)).

### 4.5 R5 — Unusual consent grants or service-principal role assignments

Detects OAuth consent grants to high-privilege Microsoft Graph scopes by a service principal, and detects directory-role assignments to service principals.

| Field | Value |
|-------|-------|
| Severity | High |
| MITRE tactic | Persistence, Privilege Escalation |
| Frequency | Every 15 minutes |
| Lookback | 1 hour |
| Threshold | ≥ 1 event |
| Auto-response | Logic App **P2 Notify Owner + SOC** |

```kql
let highRiskScopes = dynamic([
    "Mail.ReadWrite.All", "Mail.Send", "Files.ReadWrite.All", 
    "Directory.ReadWrite.All", "Application.ReadWrite.All",
    "RoleManagement.ReadWrite.Directory", "Sites.FullControl.All"
]);
union
(
    AuditLogs
    | where TimeGenerated > ago(1h)
    | where OperationName == "Consent to application"
    | extend ConsentScope = tostring(parse_json(tostring(TargetResources[0].modifiedProperties[4].newValue)))
    | where ConsentScope has_any (highRiskScopes)
    | extend Account = tostring(InitiatedBy.user.userPrincipalName),
             AppName = tostring(TargetResources[0].displayName)
    | project TimeGenerated, Operation = OperationName, AppName, ConsentScope, Account
),
(
    AuditLogs
    | where TimeGenerated > ago(1h)
    | where OperationName in ("Add member to role", "Add eligible member to role")
    | where TargetResources[0].type == "ServicePrincipal"
    | extend Account = tostring(InitiatedBy.user.userPrincipalName),
             RoleName = tostring(parse_json(tostring(TargetResources[0].modifiedProperties[1].newValue))),
             ServicePrincipalName = tostring(TargetResources[0].displayName)
    | project TimeGenerated, Operation = OperationName, ServicePrincipalName, RoleName, Account
)
```

### 4.6 R6 — Orphan / shadow agent indicator

Detects two distinct cases:

- **Orphan**: An agent (service principal) with sign-in activity but whose registered owner is disabled, deleted, or no longer in the Agent 365 registry.
- **Shadow**: A connection to a non-sanctioned third-party AI service (ChatGPT, Claude, Gemini, etc.) by a user account with significant data-access privileges.

| Field | Value |
|-------|-------|
| Severity | Medium |
| MITRE tactic | Discovery, Collection |
| Frequency | Every 1 hour |
| Lookback | 24 hours |
| Threshold | ≥ 1 event |
| Auto-response | None — cascades to Control 3.6 remediation workflow |

```kql
// Orphan branch
let orphanAgents = AADServicePrincipalSignInLogs
    | where TimeGenerated > ago(24h)
    | distinct ServicePrincipalId, ServicePrincipalName
    | join kind=leftouter (
        _GetWatchlist("AgentRegistry") | project ServicePrincipalId, OwnerUPN, OwnerStatus
    ) on ServicePrincipalId
    | where isnull(OwnerUPN) or OwnerStatus == "Disabled" or OwnerStatus == "Deleted"
    | extend FindingType = "OrphanAgent";
// Shadow branch
let shadowAI = CloudAppEvents
    | where TimeGenerated > ago(24h)
    | where Application has_any (dynamic(["ChatGPT", "Claude", "Gemini", "Perplexity", "Anthropic", "OpenAI"]))
    | summarize Events = count(), DistinctUsers = dcount(AccountObjectId) by Application
    | extend FindingType = "ShadowAI";
union orphanAgents, shadowAI
```

!!! tip "Cross-Reference"
    The orphan branch of R6 is the **upstream signal** for [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). The R6 detection alone does not remediate; remediation is a 3.6 workflow. Sentinel's role here is to surface the signal and route it.

### 4.7 R7 — Mass data download by an agent identity

Detects volumetric data egress by a service principal (e.g., agent reads thousands of SharePoint items in a short window — a hallmark of a compromised or misconfigured agent).

| Field | Value |
|-------|-------|
| Severity | High |
| MITRE tactic | Collection, Exfiltration |
| Frequency | Every 15 minutes |
| Lookback | 1 hour, baseline 14 days |
| Threshold | Configurable per agent class — see thresholds table below |
| Auto-response | Logic App **P1 Suspend Agent** (gated; high severity only) |

```kql
let lookback = 1h;
let baselineWindow = 14d;
let baseline = OfficeActivity
    | where TimeGenerated between (ago(baselineWindow) .. ago(lookback))
    | where Operation in ("FileDownloaded", "FileAccessed", "FileSyncDownloadedFull")
    | where UserType == "ServicePrincipal" or UserId has "@" == false
    | summarize BaselineHourly = avg(todouble(1)) * 60 by UserId;
OfficeActivity
| where TimeGenerated > ago(lookback)
| where Operation in ("FileDownloaded", "FileAccessed", "FileSyncDownloadedFull")
| where UserType == "ServicePrincipal" or UserId has "@" == false
| summarize RecentCount = count(), DistinctSites = dcount(Site_Url) by UserId
| join kind=leftouter (baseline) on UserId
| where RecentCount > coalesce(BaselineHourly, 50.0) * 10
| where RecentCount >= 500
| project UserId, RecentCount, DistinctSites, BaselineHourly
```

| Agent class | Recommended absolute threshold | Recommended baseline-multiplier |
|-------------|-------------------------------|---------------------------------|
| Zone 1 personal Copilot | 100 file events / hour | 5× |
| Zone 2 team agent | 500 file events / hour | 10× |
| Zone 3 enterprise agent | 2,500 file events / hour | 10× |

Adjust thresholds per business unit; the table is a starting point, not a mandate.

[Screenshot anchor: ]

!!! example "Examiner Evidence Box — §4 Analytics Rules"
    For each rule R1–R7 capture:

    - The **Analytics rule** detail page (rule name, description, severity, tactics, schedule, auto-response binding)
    - A screenshot of the **Set rule logic** tab showing the KQL committed in this walkthrough (or the firm's tuned variant) **with the change-management ticket referenced in the rule description**
    - A 30-day rolling alert summary screenshot from the Defender portal Incidents view filtered to each rule

!!! tip "Cross-Reference"
    Rule unit tests (synthetic event injection, dry-run KQL, false-positive baseline) are in [verification-testing.md](./verification-testing.md). Rule-tuning thresholds and false-positive triage are owned by the SOC under FFIEC IT Examination Handbook (Information Security) operations expectations; tuning history is part of the §10 evidence packet.

---

## §5. Workbooks — Visualization and Examiner Reporting

This section deploys three workbooks that consolidate the §3 ingestion and §4 detections into views suitable for SOC operations, AI governance reviews, and examiner walkthroughs.

### 5.1 AI Agent Security Posture workbook

This is the **primary examiner-facing workbook**. It consolidates Defender AI-SPM posture findings, R1–R7 alert volume trends, top affected agents, and the orphan-agent backlog from R6.

1. Defender portal → **Microsoft Sentinel** → **Threat management** → **Workbooks**.
2. Click **Templates** → search **AI Agent** or **Copilot**. If a Microsoft-published template (e.g., **Microsoft Copilot for Microsoft 365 Activity** or **Defender AI Posture**) exists, click **Save** to add it to the workspace, then click **View saved workbook** → **Edit**.
3. If no template fits, click **+ Workbook** → **Edit** → start with an empty workbook and add the panels described below.
4. Add the following panels (each as a **Query** part):

    | Panel | KQL summary |
    |-------|-------------|
    | Alerts by rule (R1–R7), 30 days | `SecurityAlert \| where TimeGenerated > ago(30d) \| where AlertName startswith "Agent " \| summarize Count = count() by AlertName, bin(TimeGenerated, 1d) \| render timechart` |
    | Top 10 agents by alert volume | `SecurityAlert \| where TimeGenerated > ago(30d) \| extend AgentId = tostring(parse_json(Entities)[0].AgentId) \| where isnotempty(AgentId) \| summarize Alerts = count() by AgentId \| top 10 by Alerts` |
    | Orphan agent backlog (R6) | `SecurityAlert \| where AlertName == "R6 Orphan or Shadow Agent" \| where Status != "Closed"` |
    | Defender AI-SPM posture summary | `AlertInfo \| where ServiceSource == "Microsoft Defender for Cloud" \| where Category has "AI" \| summarize Count = count() by Severity` |
    | XPIA / Prompt-shield trend (R1) | Query from R1 KQL with `bin(TimeGenerated, 1h)` and `render columnchart` |
    | DLP-policy change ledger (R4) | Query from R4 KQL with `project TimeGenerated, ChangeType, PolicyName, Account` rendered as a table |

5. Save the workbook with name `AI-Agent-Security-Posture` and pin to the SOC dashboard.

[Screenshot anchor: ]

### 5.2 Conditional Access Insights workbook

A Microsoft-published workbook that visualizes Conditional Access policy effectiveness — including for service-principal sign-ins, which is the primary value for Control 3.9.

1. Defender portal → **Microsoft Sentinel** → **Workbooks** → **Templates** → search **Conditional Access Insights**.
2. Click **Save** → **View saved workbook**.
3. In the workbook parameters bar, set **Scope** = `Service Principals` to filter the view to workload identities.
4. Save and pin.

!!! tip "Cross-Reference"
    Conditional Access policy authorship is owned by [Control 1.11 — Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md). The workbook **visualizes** policy effectiveness; it does not author or modify policy. If the workbook shows agent sign-ins not subject to a Conditional Access policy, the remediation is in 1.11, not in Sentinel.

### 5.3 Agent Usage and Performance workbook

Consumes the Application Insights stream from §3.7 (where enabled). Provides per-agent latency, error rate, conversation volume, and top intents — useful for **operational** observability and for input to MRM re-validation under [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md).

1. Defender portal → **Microsoft Sentinel** → **Workbooks** → **+ Workbook**.
2. Add Query parts targeting the Application Insights tables (`AppRequests`, `AppDependencies`, `AppExceptions`, `customEvents`):

    | Panel | KQL summary |
    |-------|-------------|
    | Conversations per agent per day | `customEvents \| where name == "ConversationStart" \| summarize Count = count() by tostring(customDimensions.AgentId), bin(timestamp, 1d)` |
    | P95 response latency | `AppRequests \| summarize percentile(duration, 95) by tostring(customDimensions.AgentId), bin(timestamp, 1h)` |
    | Top failed intents | `customEvents \| where name == "IntentResolution" and tobool(customDimensions.Failed) \| summarize Count = count() by tostring(customDimensions.IntentName) \| top 20 by Count` |
    | Knowledge-source usage | `customEvents \| where name == "KnowledgeSourceQuery" \| summarize Count = count() by tostring(customDimensions.SourceName)` |

3. Save as `AI-Agent-Usage-Performance`.

!!! warning "Performance metrics ≠ model risk evidence"
    Performance metrics from this workbook are **operational telemetry**. They aid in detecting model drift and quality degradation, but they do **not** constitute model-risk-management evidence under OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7). MRM evidence requires the structured re-validation workflow in [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md). Workbook outputs are inputs to that workflow, not substitutes for it.

!!! example "Examiner Evidence Box — §5 Workbooks"
    - PNG export of each of the three workbooks at the most recent quarter-end (Defender portal → Workbook → ⋯ → Print to PDF or use the workbook export endpoint)
    - The pinned-dashboard view in the SOC operations room
    - The list of workbook owners and review cadence (quarterly minimum)

---

## §6. Logic Apps Automation Playbooks

This section deploys three SOAR playbooks. All three are authored as **Logic Apps (Consumption)** in the Sentinel resource group and bound to the analytics rules from §4.

!!! warning "Automation policy gate"
    Any playbook that takes **suspending action** on an agent (P1) requires CISO sign-off as a documented compensating-control authority. Notify-only playbooks (P2) and ITSM-routing playbooks (P3) do not require CISO sign-off but do require AI Governance Lead sign-off. The sign-off ticket reference must appear in the Logic App tag `ApprovalTicket=<id>`.

### 6.1 P1 — Suspend Agent on High-Severity Alert

**Trigger**: Sentinel incident created with severity **High** and alert rule in (R1, R7).

**Action sequence**:

1. **Trigger**: `Microsoft Sentinel incident` (alert rule = R1 or R7, severity = High).
2. **Get incident entities** → extract `AgentId` from the alert entity mapping.
3. **HTTP action** → call Microsoft Graph: `POST https://graph.microsoft.com/v1.0/servicePrincipals/{AgentId}` with body `{ "accountEnabled": false }`. Authentication: managed identity of the Logic App, granted `Application.ReadWrite.All` (consent gated under the firm's high-privilege-app review process).
4. **Post adaptive card to Teams** → channel `#soc-agent-suspensions` with the incident ID, agent ID, agent owner UPN (from the Agent 365 watchlist), and a "Confirm suspension" button that, when clicked, posts a comment back to the Sentinel incident.
5. **Add comment to Sentinel incident** → `"Agent {AgentId} suspended automatically by playbook P1 at {utcNow()}. Owner notified. Awaiting SOC confirmation."`
6. **Tag incident** → `auto-suspension-applied`.

#### Portal authoring

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Automation** → **+ Create** → **Playbook with incident trigger**.
2. Subscription / RG: the Sentinel RG. Name: `pb-3.9-P1-suspend-agent`. Authentication: **System-assigned managed identity**.
3. Click **Create playbook**, then in the Logic App designer add the steps above.
4. Return to Sentinel → **Automation** → **+ Create automation rule** → bind P1 to incidents matching `Analytics rule name in (R1 Prompt Injection Indicator, R7 Mass Download by Agent)` AND `Severity = High`.

[Screenshot anchor: ]

!!! warning "Suspension is a reversible operational action, not a discipline action"
    Disabling an agent service principal stops it from authenticating but does **not** delete it, does **not** revoke its assigned permissions, and does **not** constitute a finding under any supervisory framework. The SOC must follow up by:

    1. Contacting the Agent Owner (P2 fires automatically in parallel).
    2. Triaging the underlying alert per [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).
    3. Re-enabling or formally retiring the agent within the SLA on the §10 cadence table.

### 6.2 P2 — Notify Agent Owner and SOC

**Trigger**: Sentinel incident created (any severity) for any rule in §4.

**Action sequence**:

1. **Trigger**: `Microsoft Sentinel incident`.
2. **Get incident entities** → extract `AgentId`.
3. **Lookup Agent Owner** → query the Agent 365 watchlist for `OwnerUPN`. If not found, fall back to the SOC distribution list and tag the incident `agent-owner-unknown` (cascades to [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)).
4. **Post adaptive card in Teams** → DM the Agent Owner with the incident ID, severity, alert summary, agent ID, and an "Acknowledge" button.
5. **Send email** (Office 365 Outlook connector) → CC the SOC distribution list.
6. **Add comment to Sentinel incident** → `"Owner {OwnerUPN} notified at {utcNow()}; acknowledgement SLA per §10 cadence."`

#### Portal authoring

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Automation** → **+ Create** → **Playbook with incident trigger**. Name: `pb-3.9-P2-notify-owner`.
2. In the designer, the **Lookup** step is a `Run query and list results (Sentinel)` action that queries the watchlist KQL: `_GetWatchlist("AgentRegistry") | where ServicePrincipalId == "{AgentId}" | project OwnerUPN`.
3. Bind via automation rule to **all** §4 rules.

[Screenshot anchor: ]

### 6.3 P3 — ITSM Routing and NYDFS 500.17 Notification Timer

**Trigger**: Sentinel incident created with severity **High** for rules R1, R4 (delete / bypass branch), R5, or R7.

**Action sequence**:

1. **Trigger**: `Microsoft Sentinel incident`.
2. **Create ITSM ticket** → ServiceNow / Jira / generic ITSM connector. Set the ticket priority to map to the Sentinel severity, populate the description from the incident summary, and tag the ticket category `Cybersecurity / AI Agent`.
3. **Set NYDFS 500.17 72-hour notification clock** → write a record to a custom log table `NYDFS500_17_Timer_CL` with fields `IncidentId, OpenedUtc, NotificationDueUtc = OpenedUtc + 72h, Status = "Open"`. Sentinel does **not** make the notification decision — that decision is made by the Compliance Officer per the firm's incident-response plan ([Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)). The timer table is **decision support**, not the decision.
4. **Post adaptive card** to `#nydfs-500-17-watchlist` Teams channel notifying the Compliance Officer that the timer has been started.
5. **Add comment to Sentinel incident** → `"P3 fired at {utcNow()}. ITSM ticket {TicketId}. NYDFS 500.17 72h decision-support timer started; compliance review required by {NotificationDueUtc}."`

!!! warning "The timer is decision-support, not a decision"
    NYDFS 23 NYCRR 500.17(a) requires notification to the Department of Financial Services within 72 hours of a determination that a cybersecurity event has occurred meeting the criteria in the regulation. The **determination** is a human judgment by the Compliance Officer / CISO informed by counsel, not an automated Sentinel output. P3 starts a **decision-support timer** that surfaces the deadline; it does not file with NYDFS, does not classify the event, and does not satisfy the 500.17 obligation by itself.

#### Portal authoring

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Automation** → **+ Create** → name `pb-3.9-P3-itsm-nydfs-timer`.
2. Authorize the ITSM connector (out-of-band approval from the firm's ITSM admin).
3. Bind via automation rule with the rule and severity filters above.

[Screenshot anchor: ]

!!! example "Examiner Evidence Box — §6 Automation"
    - Each Logic App's run history (last 90 days) showing successful triggers and any failed runs with remediation comments
    - The CISO sign-off ticket for P1
    - The AI Governance Lead sign-off tickets for P2 and P3
    - For each P3 run in the last quarter, the entry in `NYDFS500_17_Timer_CL` and the corresponding Compliance Officer disposition (notified / no-notification with reason)

!!! tip "Cross-Reference"
    Logic App run failures, ITSM connector authentication errors, and managed-identity permission issues are routed to [troubleshooting.md](./troubleshooting.md). Automation rule binding (which rule fires which playbook with which severity gate) is a key audit artifact — capture the **Automation rules** list view in the §10 packet.

---

## §7. Per-Table Retention with the Books-and-Records Boundary

Sentinel's retention model has three tiers:

| Tier | Period | Use |
|------|--------|-----|
| **Interactive** | Default 30 days, configurable up to 730 days (and recently up to 4 years for some tables) | KQL queries, analytics rules, workbooks |
| **Auxiliary / Basic logs** | Up to 2 years | Cost-optimized retention for high-volume, low-query tables |
| **Archive** | Up to 12 years (Sentinel) | Long-term audit-trail retention with restore capability |

This section configures retention per table to support the audit-trail expectations of NYDFS 500.06, FFIEC IT Examination Handbook (Audit), and SOX §404 (where AI agent activity is in scope of financial-reporting controls).

### 7.1 Recommended retention by table

| Table | Interactive | Archive | Total | Rationale |
|-------|-------------|---------|-------|-----------|
| `OfficeActivity` (incl. CopilotInteraction) | 180 days | up to 12 years | up to ~12 years | NYDFS 500.06 + audit-trail floor; **but see books-and-records boundary below** |
| `AADServicePrincipalSignInLogs` | 180 days | 7 years | 7 years | Agent identity audit trail; aligns with FINRA recordkeeping floor for related access logs |
| `SigninLogs`, `AADNonInteractiveUserSignInLogs` | 90 days | 2 years | 2 years | Operational; books-and-records authority routes to Purview |
| `AuditLogs` (Entra) | 180 days | 7 years | 7 years | Directory-change audit trail; high regulatory value |
| `CloudAppEvents` | 90 days | 2 years | 2 years | Operational; high volume |
| `PowerPlatformAdminActivity`, `PowerPlatformDlpActivity` | 180 days | 7 years | 7 years | DLP-policy change ledger; GLBA Safeguards Rule §314.4(c)(8) |
| `AlertInfo`, `SecurityAlert` | 180 days | up to 12 years | up to ~12 years | Incident audit trail (NYDFS 500.16 IRP evidence) |
| `AppRequests`, `AppDependencies` (App Insights) | 30 days | None | 30 days | Operational telemetry only |

### 7.2 Configuring per-table retention

1. Azure portal → **Log Analytics workspaces** → the workspace from §2.1 → **Tables** (preview).
2. For each table in the table above, click the row → **Manage table** → set **Total retention period** and **Archive period** per the table.
3. Save and verify the next day via:

    ```kql
    .show table OfficeActivity policy retention
    ```

[Screenshot anchor: ]

### 7.3 The books-and-records boundary — read this carefully

!!! danger "Sentinel is NOT an SEC 17a-4(f) records archive"
    The retention values in §7.1 support **operational audit trail** expectations. They do **NOT** by themselves satisfy:

    - **FINRA Rule 4511** books-and-records preservation requirements
    - **SEC Rule 17a-3** record creation requirements
    - **SEC Rule 17a-4** record preservation requirements, including **17a-4(f)** WORM / non-rewriteable, non-erasable storage and audit-trail integrity requirements

    Books-and-records data — including customer communications produced by or assisted by an AI agent that meet the definition of broker-dealer records — must be:

    1. **Captured** by Purview retention labels under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
    2. **Preserved** in a compliant 17a-4(f) WORM vendor archive (e.g., Smarsh, Global Relay, Microsoft 365 Archive with a third-party 17a-4(f) attestation, or an equivalent solution that the firm's compliance counsel has reviewed against the rule's text).
    3. **Reviewed** under the firm's supervisory system per [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

    Sentinel **complements** the books-and-records program by retaining **security telemetry** (sign-ins, alerts, audit events) that demonstrate the integrity of the records system. Sentinel **does not replace** the records program. Implementation of records preservation requires architecture decisions, vendor procurement, and sign-off by compliance counsel that are outside the scope of Control 3.9. Organizations should verify their records-preservation architecture with their compliance counsel before relying on Sentinel retention for any records obligation.

!!! example "Examiner Evidence Box — §7 Retention"
    - Per-table retention configuration screenshot for each table in §7.1
    - The cross-reference document (one page) stating which tables Sentinel owns vs. which records flow to Purview / 17a-4(f) archive — signed by the Sentinel Admin and the Compliance Officer
    - The 17a-4(f) vendor attestation reference (vendor name, attestation date, scope) — even though the vendor is owned by Control 1.9, the cross-reference is captured here so an examiner reviewing Control 3.9 can immediately see the boundary

!!! tip "Cross-Reference"
    See [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) for the books-and-records architecture. See [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the upstream Purview audit-log retention configuration that feeds OfficeActivity.

---

## §8. Incident Investigation UX in the Defender Portal

This section walks through the SOC analyst experience for triaging an AI-agent incident in the Defender portal unified view.

### 8.1 Open the incident

1. `security.microsoft.com` → **Incidents & alerts** → **Incidents**.
2. Filter: **Service source = Microsoft Sentinel** AND **Tags contains "agent"** (apply the `agent` tag via automation rule on the §4 detections to make this filter cheap).
3. Click an incident.

### 8.2 Read the unified incident page

The Defender portal unified incident page shows:

- **Attack story** graph — entities (User, Service Principal, IP, Cloud App, Agent), nodes, and lateral movement.
- **Alerts** tab — all Sentinel and Defender alerts grouped into the incident.
- **Assets** tab — affected users, devices, mailboxes, and **AI applications** (when surfaced by the Microsoft Copilot connector).
- **Investigation** tab — automated investigation results, where applicable.
- **Evidence and response** tab — files, processes, IPs, and actions taken (including P1 suspension if it fired).

[Screenshot anchor: ]

### 8.3 Enrich with Agent 365 registry

The custom entity `AgentId` is mapped at rule authoring (§4.0). In the incident page, click the **AgentId** entity → **Side panel** → the panel includes a **Custom enrichment** section pulling from the Agent 365 watchlist (configured as a custom-details entity in §4):

- Owner UPN, owner business unit, owner manager
- Agent zone (1, 2, or 3)
- Sensitivity classification
- Approved connectors / allowed MCP tools
- MRM tier and last MRM re-validation date

This enrichment is the **single most-used artifact** in SOC triage and significantly compresses the first-response window.

!!! tip "Cross-Reference"
    The Agent 365 watchlist is sourced from [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md). If the registry is sparse or stale, incident enrichment degrades and SOC mean-time-to-respond increases — this is a cross-cutting program risk, not a Sentinel deficiency.

### 8.4 Cascade to Control 3.4 incident reporting

For any incident that the SOC determines is a reportable event:

1. In the incident page → **Manage incident** → set **Status = Active**, **Classification = True positive**, **Determination** per the firm's taxonomy.
2. Click **Tasks** → assign the incident-reporting and RCA tasks defined in [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).
3. If P3 fired (NYDFS 500.17 timer), confirm the entry in `NYDFS500_17_Timer_CL` and notify the Compliance Officer.
4. Export the incident to PDF from the incident page **⋯ menu → Print** for the post-incident report.

!!! example "Examiner Evidence Box — §8 Investigation"
    - For a representative quarter, the **Incidents** filtered view (Sentinel + tag `agent`) showing volume and disposition
    - One worked example from triage to closure with timestamps, status changes, and evidence references
    - The link from a closed Sentinel incident to its Control 3.4 RCA artifact

---

## §9. Sentinel MCP Server — Optional Analyst Augmentation

The Sentinel MCP Server exposes Sentinel data and operations as tools to MCP-compatible AI assistants (e.g., a SOC analyst's GPT-based copilot). At the time of writing it is in Preview / GA in commercial cloud and **not available** in GCC High or DoD.

!!! info "Optional capability with cost and license implications"
    Sentinel MCP is **optional augmentation**, not a Control 3.9 baseline requirement. It can accelerate analyst triage but it adds licensing cost (Sentinel data-lake tier + MCP server license) and a new attack surface (an LLM with read access to Sentinel data). Verify the current licensing and pricing on the Microsoft Sentinel pricing page and run the firm's third-party-AI risk review **before** enabling.

### 9.1 Preconditions

1. Sentinel data-lake tier enabled on the workspace (Azure portal → workspace → **Sentinel data lake** → **Enable**).
2. MCP server license verified.
3. Firm's third-party-AI risk review completed for the analyst-facing MCP client (whatever client the SOC will use).
4. CISO sign-off on the read-scope granted to MCP and the user population permitted to use it.

### 9.2 Enable the MCP server

1. Defender portal → **Microsoft Sentinel** → **Configuration** → **Sentinel MCP** (or equivalent blade — confirm current path).
2. Click **Enable**. Authorize with the Sentinel Admin account.
3. Configure the **Authorization scope** — restrict to `read` operations on a defined set of tables (do not grant write/edit).
4. Configure the **User scope** — restrict to the SOC distribution group.
5. Save.

[Screenshot anchor: ]

### 9.3 Connect an MCP client

1. In the analyst's MCP-compatible client (e.g., the SOC's Copilot Studio agent or a sanctioned external assistant), add the Sentinel MCP server endpoint.
2. The analyst authenticates with their Entra credentials; the MCP server uses on-behalf-of token flow to ensure the analyst's own RBAC is enforced.
3. Test with a simple query (e.g., `"summarize Sentinel incidents tagged agent in the last 24 hours by severity"`).

### 9.4 Operating constraints

- **Read-only.** Do **not** grant write scope to the MCP server. Any analyst-driven action (close incident, run playbook, edit rule) must be performed in the Defender portal so the action is captured in the standard audit trail.
- **PII / NPI in queries.** Analyst prompts and MCP responses may contain customer NPI under GLBA. Treat MCP transcripts as Confidential-NPI; capture them in the firm's analyst-tooling DLP scope.
- **Hallucination risk.** MCP returns **summaries**, not authoritative records. Any artifact that goes into an examiner packet, an RCA, or a regulatory filing must be sourced from a **direct KQL query** in the Defender portal, not from an MCP response. The MCP response is an analyst aid; the KQL output is the record.

!!! warning "MCP responses are not records"
    The output of a Sentinel MCP conversation is **not** an SEC 17a-4(f) record, is **not** examiner evidence, and **must not** be relied upon as the source-of-truth for any compliance disposition. MCP aids analyst speed; the Defender portal and the underlying Log Analytics workspace remain the authoritative record.

!!! example "Examiner Evidence Box — §9 MCP (if enabled)"
    - The CISO sign-off ticket
    - The third-party-AI risk-review artifact
    - The MCP authorization-scope screenshot showing read-only and the user-scope restriction
    - The DLP scope coverage for analyst MCP transcripts

!!! tip "Cross-Reference"
    If the firm chooses **not** to enable Sentinel MCP, document the decision in the §1 worksheet (sovereign clouds) or in a standalone control-decision artifact (commercial). Non-adoption of an optional capability is not a control gap.

---

## §10. Evidence Capture, Zone Cadence, and Examiner Packet

This section defines the operating cadence and evidence packet for Control 3.9.

### 10.1 Cadence by zone

| Zone | Activity | Frequency | Owner |
|------|----------|-----------|-------|
| Zone 1 (Personal) | R1–R5 enabled; P2 notification on incidents | Continuous | SOC Analyst |
| Zone 1 | Workbook 5.1 review | Monthly | AI Governance Lead |
| Zone 2 (Team) | All seven rules R1–R7 enabled; P1 + P2 + P3 enabled | Continuous | SOC Analyst |
| Zone 2 | Rule tuning review (false-positive rate, threshold drift) | Monthly | SOC Analyst + Sentinel Admin |
| Zone 2 | Workbook 5.1 review | Bi-weekly | AI Governance Lead |
| Zone 3 (Enterprise) | All rules enabled; App Insights workbook 5.3 enabled | Continuous | SOC Analyst |
| Zone 3 | Rule tuning review | Weekly | SOC Analyst + Sentinel Admin |
| Zone 3 | Workbook 5.1 + 5.3 review | Weekly | AI Governance Lead |
| All zones | §1 sovereign-cloud worksheet re-check | Quarterly | Sentinel Admin |
| All zones | §10 evidence packet assembly | Quarterly | Sentinel Admin + Compliance Officer |
| All zones | Full §0–§7 walkthrough re-execution (greenfield rebuild test) | Annual | Sentinel Admin |

### 10.2 The §10 evidence packet

Assemble quarterly. Store in the Purview evidence library tagged `Control-3.9 / <YYYY>-Q<N>`. The packet is the primary examiner deliverable for Control 3.9.

| # | Artifact | Source section |
|---|----------|----------------|
| 1 | Roles + PIM eligible-assignment screenshots | §0 |
| 2 | Cost budget screenshot | §0 |
| 3 | Workspace decisions ticket | §0 |
| 4 | Sovereign-cloud compensating-control worksheet | §1 |
| 5 | Workspace properties + lock screenshots | §2 |
| 6 | Defender portal **Connected** banner | §2 |
| 7 | Per-connector status + verification KQL output (×7 connectors) | §3 |
| 8 | Entra diagnostic-settings screenshot showing all sign-in tables enabled | §3.2 |
| 9 | Per-rule detail page + KQL screenshot + 30-day alert summary (×7 rules) | §4 |
| 10 | Three workbook PDF exports | §5 |
| 11 | Three Logic App run-history exports + sign-off tickets | §6 |
| 12 | Per-table retention configuration screenshots + records-boundary cross-reference | §7 |
| 13 | One worked incident (triage to closure) demonstrating §8 enrichment + §3.4 cascade | §8 |
| 14 | MCP enablement evidence OR documented non-adoption decision | §9 |
| 15 | Cadence-table compliance log (last quarter) | §10.1 |
| 16 | Rule-tuning ledger (changes, dates, approvers) | §10 |
| 17 | Quarterly sign-off cover sheet — Sentinel Admin + AI Governance Lead + Compliance Officer | §10 |

### 10.3 Verification criteria summary

| VC | Description | Source section |
|----|-------------|----------------|
| VC-1 | Roles assigned PIM-eligible; cost budget exists | §0 |
| VC-2 | Sovereign-cloud worksheet completed (sovereign tenants) | §1 |
| VC-3 | Workspace deployed + onboarded to Defender portal + RG locked | §2 |
| VC-4 | All seven connectors connected with non-zero ingestion verified | §3 |
| VC-5 | Seven analytics rules deployed and producing alerts | §4 |
| VC-6 | Three workbooks deployed and pinned | §5 |
| VC-7 | Three Logic Apps deployed with sign-off and successful run history | §6 |
| VC-8 | Per-table retention configured per §7.1 with records-boundary cross-reference | §7 |
| VC-9 | One worked incident in last quarter demonstrating §8 enrichment | §8 |
| VC-10 | MCP enabled with constraints OR documented non-adoption | §9 |
| VC-11 | Quarterly evidence packet assembled and signed off | §10 |

Detailed verification procedures (KQL probes, dry-run injection tests, evidence-collection commands) are in [verification-testing.md](./verification-testing.md).

!!! example "Examiner Evidence Box — §10 Cadence"
    - The §10 evidence packet itself for the most recent four quarters
    - The quarterly sign-off cover sheets
    - The annual greenfield-rebuild test result (proves the runbook is current and reproducible)

!!! tip "Cross-Reference — supervisory program"
    Sentinel evidence is one input to the firm's supervisory program under [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). The §10 packet should be referenced from the firm's annual 3110 written supervisory procedures testing.

!!! tip "Cross-Reference — long-window observability"
    For long-window analytics that exceed Sentinel's interactive retention (e.g., year-over-year agent behavior trends, multi-quarter MRM input), see [Control 3.14 — Agent 365 Observability SDK](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md). The SDK **complements** Sentinel; it does not replace any of the detection, alerting, or incident workflows defined in this walkthrough.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
