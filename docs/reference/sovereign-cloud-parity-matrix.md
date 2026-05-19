# Sovereign Cloud Parity Matrix — v1 (May 2026)

This matrix aggregates the per-control sovereign-cloud caveats already authored across the FSI-AgentGov control catalog into a single, scannable view. It is intended for FSI architects, CSAs, and partner field teams who need a one-page answer to *"will this work in my Government cloud tenant?"* before committing to a target architecture.

---

## How to read this matrix

- **Rows** are FSI-AgentGov controls with a material sovereign-cloud caveat already documented in the control body.
- **Columns** are the four sovereign deployment surfaces FSI tenants typically ask about:
    - **GCC** — Microsoft 365 Government Community Cloud (commercial-equivalent compliance baseline; FedRAMP Moderate, IRS 1075, CJIS).
    - **GCC High** — Microsoft 365 Government Community Cloud High (DoD IL4 / FedRAMP High baseline; ITAR-aware).
    - **DoD IL5** — Microsoft 365 DoD cloud (Impact Level 5 baseline).
    - **China cloud (21Vianet)** — Microsoft 365 operated by 21Vianet in China; isolated from Microsoft commercial and US Government clouds.
- **Cell values** use a small status vocabulary:
    - **GA** — Generally available with feature parity to commercial.
    - **GA / verify** — Service is GA but specific feature parity should be re-verified at deploy time.
    - **Lagging** — Service is GA but a referenced sub-capability lags commercial; document the gap.
    - **Limited** — Material capability gap (size limit, missing connector, missing classifier) that affects the control's evidence pipeline.
    - **Not announced** — Microsoft has not published a parity roadmap item; treat as unavailable until disclosed.
    - **Verify with MS** — No first-party content exists in this control today; FSI tenants should validate directly with the Microsoft account team before assuming a posture.
    - **N/A** — Capability is inherently inapplicable to that cloud (e.g., 21Vianet exclusions in commercial-only roadmap items).
- The **Compensating control** column points at the documented fallback (manual register, named-owner attestation, alternate Microsoft surface) authored elsewhere in the framework.
- Each row's **Source** link jumps to the sovereign-cloud admonition in the underlying control file, where the caveat language and verification cadence live.

!!! warning "v1 starting point — not a substitute for current Microsoft attestation"
    This matrix is a v1.7 starting point that crystallises caveats already in the control catalog; **gaps will be filled as customer evidence accumulates**. Per FSI examiner feedback, the framework's GCC parity story has been a known gap; this matrix is the first pass at quantifying it. Customers and partners must **validate current GA status with Microsoft before finalising architecture decisions** — the [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap), the [Microsoft 365 US Government service descriptions](https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/), and the tenant's own Message Center are the authoritative sources at any point in time.

---

## Pillar 1 — Security

| Control | GCC | GCC High | DoD IL5 | China (21Vianet) | Compensating control / workaround |
|---------|-----|----------|---------|------------------|-----------------------------------|
| [1.1 Restrict Agent Publishing](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) — PowerShell automation must target sovereign endpoints (`-Endpoint usgov\|usgovhigh\|dod`) | GA / verify | GA / verify | GA / verify | Verify with MS | PowerShell Setup playbook (Control 1.1) — sovereign-cloud-aware automation patterns |
| [1.5 DLP & Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — DLP for M365 Copilot rolling; IRM-driven Adaptive Protection **not available in any US Government cloud** | GA / verify | Lagging | Lagging | Verify with MS | Static role-based DLP without risk tiering; document Adaptive Protection gap as compensating-control note |
| [1.6 DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — Classic DSPM for AI GA in Commercial & GCC; GCC High & DoD GA at `purview.microsoft.us` with partial parity; unified DSPM (May 2026) **not yet announced for sovereign clouds** | GA | GA / verify (partial parity) | GA / verify (partial parity) | Verify with MS | Use classic DSPM for AI surface only; do not promise unified DSPM benefits in sovereign clouds; record gap on Zone 3 evidence binder |
| [1.8 Runtime Protection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) — Defender for Cloud Apps **AI Agent Protection** preview in commercial; Security Webhooks API prerelease; Microsoft Copilot Studio is GA in GCC and GCC High but generative-AI dependencies are independently gated | Lagging | Not announced (DCAS AI Agent Protection) | Not announced | Verify with MS | Use Copilot Studio Prompt Shields + content moderation as alternative; record any gap in Zone 3 exception register |
| [1.10 Communication Compliance](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — Core CC GA all clouds; **Detect Microsoft Copilot interactions** template availability is staged | GA / verify (Detect Copilot template) | GA / verify (Detect Copilot template) | GA / verify (Detect Copilot template) | Verify with MS | Use generic CC policies on Exchange / Teams / Viva Engage until Copilot template lands; portal endpoint differs per cloud |
| [1.11 Conditional Access](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) — User CA GA all clouds; CA Workload Identities Premium SKU and **Entra Agent ID** parity differs | GA / verify | Lagging (Entra Agent ID not announced) | Lagging (Entra Agent ID not announced) | Verify with MS | Govern agent identities via SP-targeted CA Workload Identity policies until Entra Agent ID lands |
| [1.12 Insider Risk Management](../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) — IRM core verify per cloud; **Adaptive Protection not available in any US Government cloud** per Microsoft Learn | Limited | Not announced (Adaptive Protection) | Not announced (Adaptive Protection) | Verify with MS | Compensating: Communication Compliance, Audit (Premium), DLP, Defender for Cloud Apps, Sentinel UEBA, manual supervisory review, exception register |
| [1.13 Sensitive Information Types](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) — Built-in & custom pattern SITs GA all clouds; **EDM, NER, trainable classifiers, DLP-for-Copilot, DSPM-for-AI** require per-cloud verification | GA (SITs); verify (EDM/NER/TC) | GA (SITs); verify (EDM/NER/TC) | GA (SITs); verify (EDM/NER/TC) | Verify with MS | Use built-in SITs as baseline; document EDM/NER/trainable-classifier gaps as compensating-control conversation |
| [1.14 Data Minimization](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) — Power Platform DLP parity all clouds; **DSPM for AI lags** in GCC High / DoD; SharePoint Advanced Management RCD/RSS/DAG limited; Copilot Studio limited preview in GCC High as of early 2026 | GA / verify | Lagging (DSPM for AI, SAM, Copilot Studio) | Lagging (DSPM for AI, SAM, Copilot Studio) | Verify with MS | Pillar-4 grounding controls (RCD/RSS), manual scope reviews; document DSPM gap |
| [1.15 Encryption (Transit & Rest)](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) — Service encryption + TLS GA all clouds; **Customer Key (CMK) workload coverage differs between Commercial and GCC High** (e.g., Power Automate, several D365 apps not yet on GCC High CMK list) | GA / verify per workload | Limited (CMK workload coverage) | Limited (CMK workload coverage) | Verify with MS | Verify per-service CMK coverage in [Microsoft Learn — Customer-managed key](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key) before asserting CMK in narrative |
| [1.19 eDiscovery for Agent Interactions](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) — Unified eDiscovery (Purview portal) GA all clouds; **classic eDiscovery retired August 2025 except 21Vianet** | GA | GA | GA | Classic-only (per Microsoft) | Re-verify Copilot interactions location parity; treat any GCC High/DoD gap on Copilot interactions location as a compensating-control conversation |
| [1.20 Network Isolation & Private Connectivity](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) — IP firewall, IP cookie binding, VNet integration, Private Endpoints all available across Commercial / GCC / GCC High / DoD | GA | GA | GA | Verify with MS | None required for primary capabilities; verify Azure Government region pairing for VNet support |
| [1.21 Adversarial Input Logging](../controls/pillar-1-security/1.21-adversarial-input-logging.md) — Azure AI Content Safety **Prompt Shields**, Defender for Cloud AI workload protection, Defender XDR for Copilot, Comm Compliance Prompt Shield classifier — verify per release | Verify per release | Lagging — verify per release | Lagging — verify per release | Verify with MS | Treat any cross-cloud parity gap as compensating-control conversation; do not over-promise real-time blocking in sovereign clouds without per-feature verification |

---

## Pillar 2 — Management

| Control | GCC | GCC High | DoD IL5 | China (21Vianet) | Compensating control / workaround |
|---------|-----|----------|---------|------------------|-----------------------------------|
| [2.1 Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md) — Managed Environments available with **material gaps**: weekly digest / **Usage insights not available in GCC, GCC High, DoD, or 21Vianet**; CMK service coverage differs; Agent 365 governance console no parity | Limited (Usage insights) | Limited (Usage insights, CMK) | Limited (Usage insights, CMK) | Limited (Usage insights) | Substitute Microsoft Graph activity exports, Purview audit (1.7 / 3.1), or Sentinel ingestion (3.9) for the weekly digest; do **not** rely on the digest as books-and-records evidence |
| [2.5 Testing, Validation & QA](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) — Copilot Studio broadly available; **Azure AI Foundry evaluation, advanced evaluator families, third-party model availability lag** | Verify per evaluator | Lagging (Foundry evaluators) | Lagging (Foundry evaluators) | Verify with MS | Document compensating evaluator (manual SME review, alternative evaluator family) when target evaluator missing in cloud |
| [2.6 Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — DSPM for AI, Foundry evaluation harness, Agent 365 console, Entra Agent ID, Anthropic Claude — all require per-cloud verification | Verify per surface | Lagging across surfaces | Lagging across surfaces | Verify with MS | Maintain manual model inventory (SharePoint list backed by Purview retention); MRM validation by firm's existing MRM function under firm policy; retain evidence under 17a-4(f) |
| [2.9 Agent Performance Monitoring](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) — Copilot Studio analytics, Application Insights integration, **Power Platform analytics export to Azure Data Lake** reduced or staggered availability in US Gov clouds | Lagging | Limited (analytics export) | Limited (analytics export) | Verify with MS | Verify telemetry completeness — a configuration that produces complete telemetry in commercial may produce partial / empty data in GCC High / DoD, creating false-clean evidence |
| [2.12 Supervision (FINRA Rule 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — Supervisory obligations apply equally; **Copilot Studio human-agent handoff, Agent Framework HITL evidence-export, Entra Agent ID sponsorship, Agent 365 admin center** have parity gaps | Verify per surface | Not announced (sponsorship & Agent 365) | Not announced (sponsorship & Agent 365) | Verify with MS | Documented compensating supervisory control: principal-led manual review at zone-appropriate sampling rate, evidenced in supervision register; reconcile against 1.2 / 3.1 registry; disclose absence of native HITL enforcement in WSPs |
| [2.24 Feature Enablement Governance](../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) — M365 Copilot, Copilot Studio, declarative agents, MCP connectors, Agent Framework tools — sovereign typically lags commercial **6–18 months**; some preview capabilities may never reach sovereign | Lagging 6–18 mo | Lagging 6–18 mo | Lagging 6–18 mo | Verify with MS | Maintain separate feature catalog per cloud; treat any "allow in Zone 2/3" decision in commercial as **not inherited** into sovereign; record unavailable items as **product unavailability** in examination briefing |
| [2.25 Agent 365 Admin Center](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — As of GA (May 1, 2026) **no announced parity for Agent 365 Admin Center, governance templates, or admin-gated publish/activate workflows in GCC, GCC High, or DoD** | Not announced | Not announced | Not announced | Verify with MS | Named human owner in Control 1.2 registry; manual quarterly attestation; change-management approval per Control 2.3; SoD per Control 2.8; disclose absence in WSPs |
| [2.26 Entra Agent ID Identity Governance](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — Entra Agent ID **GA in commercial** (April 2026; Agent 365 / M365 E7 licensing bundle GA May 1, 2026); **no GCC, GCC High, or DoD availability announced** for agent-identity object types or "All agents (preview)" assignment-policy option | Not announced | Not announced | Not announced | Verify with MS | Do not implement as technical configuration in sovereign; named human owner in Control 1.2 registry; manual quarterly attestation; service-principal-based access governance; disclose in WSPs |

---

## Pillar 3 — Reporting

| Control | GCC | GCC High | DoD IL5 | China (21Vianet) | Compensating control / workaround |
|---------|-----|----------|---------|------------------|-----------------------------------|
| [3.1 Agent Inventory & Metadata](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — M365 admin center Agents / Agent Registry surface availability staged across clouds | GA / verify rollout | Verify | Verify | Verify with MS | Sovereign Cloud Boundary is a required metadata field on every agent record; reconcile via Graph activity exports + manual attestation where admin-center surface lags |
| [3.4 Incident Reporting & RCA](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — Defender XDR unified incidents, Sentinel connectors, IRM templates verify; **Sentinel MCP Server no announced sovereign-cloud GA** | Verify per connector | Lagging (some connectors, MCP server) | Lagging (some connectors, MCP server) | Verify with MS | Manual incident register (SharePoint list backed by Purview retention); documented runbook with regulator-notification matrix; quarterly exercise of compensating controls |
| [3.5 Cost Allocation & Budget Tracking](../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) — **M365 Copilot PAYG, Cost Management exports** parity verify | Verify | Lagging — verify | Lagging — verify | Verify with MS | Document which surfaces are not at parity and what manual compensating controls bridge the gap (CFO-approved rate card, manual chargeback ledger) |
| [3.6 Orphaned Agent Detection](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — depends on **Agent 365 Ownerless Agents card (2.25)** and **Entra Agent ID lifecycle workflows (2.26)** — neither parity-announced for GCC / GCC High / DoD | Not announced (transitively) | Not announced (transitively) | Not announced (transitively) | Verify with MS | **Quarterly manual reconciliation** of Control 1.2 registry against HR leaver list (90d), Entra disabled-user list, Power Platform maker / environment-owner exports; dual-signed worksheet retained 6 yr |
| [3.9 Microsoft Sentinel Integration](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — Sentinel exists across commercial and government clouds; **connector and preview-feature parity varies**: Microsoft Copilot connector, certain Defender data types, Sentinel MCP Server lag in GCC High / DoD | GA / verify connectors | Lagging (Copilot connector, MCP) | Lagging (Copilot connector, MCP) | Verify with MS | Document unavailable capabilities as **product unavailability**, not as policy exceptions; use parallel patterns from 2.25 / 3.6 for sovereign-cloud evidence discipline |

---

## Pillar 4 — SharePoint

| Control | GCC | GCC High | DoD IL5 | China (21Vianet) | Compensating control / workaround |
|---------|-----|----------|---------|------------------|-----------------------------------|
| [4.6 Grounding Scope Governance](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) — RCD, Restricted SharePoint Search, SharePoint Advanced Management roll out to gov clouds on a delayed cadence; **Copilot Studio connector payload limit is 450 KB in GCC vs. 5 MB commercial** | Limited (450 KB connector payload; SAM/RCD/RSS rollout lag) | Lagging | Lagging | Verify with MS | Verify availability via Microsoft 365 Roadmap & tenant Message Center before committing posture; design connector flows to the lower payload ceiling |
| [4.7 Microsoft 365 Copilot Data Governance](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) — M365 Copilot GA all clouds with feature gaps in higher-isolation environments; **Anthropic Claude not available in GCC, GCC High, or DoD**; flex routing scoped to EU/EFTA tenants | GA / verify (no Anthropic) | GA / verify (no Anthropic, feature gaps) | GA / verify (no Anthropic, feature gaps) | Verify with MS | Document Anthropic availability per cloud; CISO risk acceptance for sovereign-cloud parity gaps; record subprocessor / flex-routing posture in governance evidence |

---

## Coverage and gaps in this v1 matrix

| Pillar | Controls in pillar | Controls in matrix | Sovereign signal coverage |
|--------|-------------------:|-------------------:|---------------------------|
| Pillar 1 — Security | 29 | 13 | 13 of 29 controls have sovereign-cloud caveats authored; remaining 16 have not yet been called out and should be reviewed in v1.8. |
| Pillar 2 — Management | 26 | 8 | 8 of 26 controls; the 18 remaining management controls (lifecycle, change-control, vendor management, training, etc.) are mostly process controls where sovereign parity rarely changes the requirement. |
| Pillar 3 — Reporting | 14 | 5 | 5 of 14; reporting controls 3.2/3.3/3.7/3.8/3.10–3.14 have not yet been examined for sovereign-cloud caveats. |
| Pillar 4 — SharePoint | 9 | 2 | 2 of 9; the 7 remaining SharePoint controls warrant a focused sovereign-cloud pass in v1.8. |
| **Total** | **78** | **28** | **~36% of the 78-control catalog has a documented sovereign-cloud caveat in v1.7.** |

**China cloud (21Vianet) coverage is weak by design.** First-party authored content covers only a single explicit case (Control 1.19 — classic eDiscovery retained for 21Vianet) and one acknowledgement (Control 2.1 — Usage insights not available). Most cells in that column read "Verify with MS" rather than inventing facts. China-cloud parity is a **v1.8 backlog item**; FSI tenants operating in 21Vianet should engage Microsoft directly until this column is filled.

**DoD IL4 vs IL5 nuance.** Microsoft Learn frequently treats GCC High as the "DoD IL4 / L4 baseline" and DoD as the IL5 baseline. This matrix uses **GCC High** for the L4 row and **DoD IL5** for the L5 row, mirroring the column headings used in Microsoft's own service descriptions. Where Microsoft documents a single "GCC High & DoD" status, both columns carry the same value.

---

## Backlog (v1.8)

The following controls have GCC / GCC-H / DoD content in their bodies but are not yet aggregated into this matrix because the authored content is comparatively shallow (single-line acknowledgement, footer reference, or RACI mention rather than a substantive parity statement). They will be promoted into v1.8:

- Pillar 1: 1.2 (Agent Registry — sovereign endpoint patterns), 1.7 (Audit Logging — IPPS endpoints), 1.9 (Retention — sovereign endpoint patterns), 1.16 (IRM for Documents — DKE / sovereign), 1.17 / 1.18 / 1.22 (mentioned via playbooks but not control-body)
- Pillar 2: 2.7 (Vendor Management — subprocessor location), 2.10 (Lifecycle), 2.11 (Bias / Fairness), 2.13 (Records), 2.16 (RAG validation), 2.17–2.20 (testing / red-team patterns), 2.21–2.23 (operations)
- Pillar 3: 3.2, 3.3, 3.7, 3.8, 3.10, 3.11, 3.12, 3.13, 3.14
- Pillar 4: 4.1, 4.2, 4.3, 4.4, 4.5, 4.8, 4.9
- Cross-cutting reference docs: `docs/playbooks/_shared/powershell-baseline.md` (canonical sovereign endpoint flags) is referenced from many controls but is not represented as a row here.

Adding any of the above is **mostly extraction**, not net-new authorship — the parity facts are typically already in the underlying control body, the playbook, or in the [`work-iq-governance.md`](work-iq-governance.md) reference doc.

---

## Re-verification cadence

- **Quarterly** — Re-verify against the [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap) and the [Microsoft 365 US Government service descriptions](https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/). Any cell whose status moved from "Not announced" to "GA" should be promoted in the underlying control's sovereign admonition first, then surfaced into this matrix.
- **At deploy time** — Re-verify any "Verify per release" or "Lagging — verify" cell against the tenant's Message Center and the live Learn page linked from the underlying control. A configuration that produces complete telemetry in commercial may produce partial or empty data in GCC High / DoD; treat that as a false-clean risk on the evidence binder.
- **At Microsoft model-swap announcements** — Anthropic, third-party model providers, and Foundry evaluator families have independent sovereign-cloud rollouts that lag the M365 / Power Platform release wave. Re-verify Pillar 2 rows (2.5, 2.6, 4.7) on every announced model addition.

---

## Related material

- [Control 1.20 — Network Isolation & Private Connectivity](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) — primary network-layer control referenced from many of the rows above.
- [CSA Positioning Guide](csa-positioning-guide.md) — partner / CSA conversation patterns; this matrix is the reference data behind the "sovereign cloud" objection-handling pattern in Section 9.
- [Solutions Index](solutions-index.md) — companion solution implementations whose sovereign-cloud applicability is governed by the underlying control rows.
- [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap)
- [Microsoft 365 US Government service descriptions](https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/)
- [Microsoft Cloud for US Government overview](https://learn.microsoft.com/en-us/azure/azure-government/documentation-government-welcome)

---

*Updated: May 2026 | Version: v1.6.2 | Source: Aggregated from per-control sovereign-cloud admonitions across the v1.6.2 control catalog.*
