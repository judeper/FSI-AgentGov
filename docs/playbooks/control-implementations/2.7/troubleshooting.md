# Control 2.7: Vendor and Third-Party Risk Management — Troubleshooting

> Companion to [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md). Common failure modes and resolutions for vendor and connector risk management in M365 / Power Platform / Microsoft Copilot Studio.

---

**Last Verified:** 2026-11-06

**Verification scope:** Official documentation only; no tenant UI, API execution, screenshots, or enforcement tests. Remediation changes require impact assessment and approved change control.

## Quick Reference

| # | Issue | Likely Root Cause | First Action |
|---|-------|-------------------|--------------|
| 1 | Inventory misses connectors actually in use | Resource/analytics coverage gaps; missing visibility | Reconcile resource inventory, custom connectors, agent tools and actual runtime evidence |
| 2 | Vendor cannot supply SOC 2 Type II | Smaller vendor, pre-attestation maturity | Accept ISO 27001 + bridge letter + independent assessment; document risk acceptance |
| 3 | Custom connector created without review | Maker permissions or intake process not governed | Review actual maker-role assignments and DLP usage controls; sharing limits do not restrict creation |
| 4 | Vendor incident notice arrived late | Contract notification window not enforced | Re-paper contract; raise vendor risk score; escalate to vendor risk committee |
| 5 | DLP policy fails to block expected connector | Wrong environment/classification, enforcement delay, ACP-only mode or unsupported connector type | Reconcile all applicable DLP/ACP policies and test the actual operation |
| 6 | Community / independent-publisher tool appeared in Copilot Studio agent | Unapproved maker change or upstream tool change | Remove tool; review maker permissions and supported connector/server restrictions |
| 7 | LLM vendor changed model behavior with no notice | Contract clause weak or absent | Trigger Control 2.6 re-validation; re-paper contract; consider vendor change |
| 8 | MCP tool server reachable from agent without inventory entry | Unapproved server binding or intake bypass | Remove binding/block supported connector or server; identify actual operator and risk tier |

---

## Detailed Troubleshooting

### Issue 1 — Connector inventory is incomplete

**Symptoms:** Audit discovers connectors in production not present in the inventory; new connectors appear without intake.

**Diagnostics:**
1. Run the inventory snapshot from the [PowerShell Setup](powershell-setup.md) playbook against **every** environment, including default and personal productivity.
2. Compare **Manage → Inventory** resource connector references with raw custom connector reads and agent **Tools**. Analytics has at most 28 days and incomplete workload coverage; it does not provide a universal three-workload connector CSV. Built-in HTTP actions are not captured as connectors ([inventory limitations](https://learn.microsoft.com/en-us/power-platform/admin/inventory-schema)).
3. Inspect actual available administrative audit activities and configured execution logs within their retention periods. Do not assume literal operation IDs or complete request/response evidence. Review service-principal-owned resources and any visibility gaps separately.

**Resolution:**
- Add an automated weekly snapshot to the evidence pipeline.
- Configure and test an inventory-delta/approval notification process; do not assume native automatic alerts for every new connector.
- Require intake-ticket reference in any change-management approval before publishing a new connector to a Managed Environment.

---

### Issue 2 — Vendor cannot provide SOC 2 Type II

**Symptoms:** Tier T2–T5 vendor lacks current SOC 2 Type II report.

**Resolution paths (in priority order):**
1. **Accept alternative attestation** — ISO 27001 + recent surveillance audit, FedRAMP Moderate/High, HITRUST. Document acceptance and rationale.
2. **Bridge letter** — Acceptable to span the period between the prior SOC 2 and the next, provided issuance date is within 90 days.
3. **Independent assessment** — Commission a qualified third-party security assessment. Risk-accept gaps with executive sign-off.
4. **Compensating controls** — Tighten DLP, require additional logging, restrict to non-NPI workloads, set risk-acceptance expiry (≤ 12 months).
5. **Vendor exit** — Escalate to the vendor risk committee for offboarding when no acceptable path exists.

---

### Issue 3 — Custom connector created without security review

**Symptoms:** New custom connector found in a production environment with no record in the intake system.

**Resolution:**
1. Contain unauthorized usage through an approved agent removal or supported DLP/ACP restriction; assess impacted existing resources before changing policy.
2. Run the custom connector enumeration script and assess data exposure.
3. Review actual **Environment Maker** and Dataverse role assignments: Environment Maker includes custom connector creation ([environment roles](https://learn.microsoft.com/en-us/power-platform/admin/environments-overview#environment-roles)). Managed Environment sharing limits are not a creation restriction.
4. Establish designated producer environments and least-privilege maker permissions where supported; document the default environment's broad maker access. Use DLP to restrict **usage**, not as evidence that creation is impossible.
5. Add tested inventory-delta notifications and intake review; use documented audit activities actually observed, not a fabricated `RegisterCustomConnector` alert contract.

---

### Issue 4 — Vendor incident notification delayed

**Symptoms:** Public disclosure or third-party intelligence reaches the firm before the vendor's own notification.

**Resolution:**
1. Document the timeline (vendor incident time → vendor notice → firm awareness) and impact assessment.
2. Update the vendor's risk score and trigger a contract review.
3. For FINRA-regulated firms, evaluate whether the delay implicates the firm's Rule 4530 reporting obligation.
4. Consider remediation paths: contract amendment, financial penalties, escalation to vendor risk committee, or vendor exit.

---

### Issue 5 — DLP policy not blocking as expected

**Symptoms:** Users continue to add connectors that should be blocked.

**Diagnostics:**
1. Open Power Platform admin center → **Security → Data and privacy → Data policy**. Review **Scope / Applied to**, connector classifications and all applicable policies; no **Policy effects** view is assumed ([manage data policies](https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss)).
2. If multiple policies apply, the **most restrictive wins**, but only across overlapping environments. Validate environment-to-policy mapping.
3. Check propagation: policy enforcement is usually within an hour but can take **24 hours** for full enforcement; changes can disable connections and suspend/quarantine existing resources ([policy process](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)).
4. Review ACP **Status**, scope and mode separately. ACP-only mode ignores classic DLP; ACP does not support custom, HTTP or virtual connectors. Managed Environments are required to block otherwise nonblockable connectors, not to apply every classic DLP policy ([ACP](https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies)).
5. For custom connectors, reconcile environment by-name classification against ordered tenant Host URL patterns; final `*` defaults to Ignore unless explicitly changed. Existing name assignments supersede patterns; dynamic host changes occur after policy evaluation ([custom connector limitations](https://learn.microsoft.com/en-us/power-platform/admin/dlp-custom-connector-parity)).

**Resolution:**
- Reclassify the connector and republish the policy.
- Test with the actual delegated/service-principal connection. Conditional Access is an identity control, not a mechanism that overrides DLP; DLP scope is the hosting environment, not user security-group membership.
- For Copilot Studio plugins, confirm the plugin is also restricted at the Copilot Studio agent layer (DLP alone does not govern all plugin types).

---

### Issue 6 — Independent / community plugin appeared in a Copilot Studio agent

**Symptoms:** Unvetted tool discovered on the agent's **Tools** page.

**Resolution:**
1. Disable the plugin immediately and remove it from the agent.
2. Review configured agent/server telemetry for the actual call and destination. Record missing payload/identity evidence rather than interpreting no log as no transmission.
3. Assess whether NPI, MNPI, or supervisory content was transmitted. If yes, follow Control 3.x incident response and consider notification obligations.
4. Restrict maker/edit permissions, apply supported connector/ACP server restrictions and require approval for additions. For MCP, turn **Allow all** off and enable only approved tools; new tools then default off ([MCP selection](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent)). Do not assume a universal tenant plugin allowlist or auto-update switch.

---

### Issue 7 — AI/LLM vendor changed model behavior without notice

**Symptoms:** Agent accuracy, latency, or output character changes unexpectedly; no contract-required notification was received.

**Resolution:**
1. Capture before/after evidence (sampled prompt/response pairs, evaluation metrics).
2. Treat as a **model change** under Control 2.6 — re-validate the agent before continued production use if the change is material.
3. Open a contract dispute citing the missing notification; require the vendor to publish a change log with retroactive notice.
4. Re-paper the contract to tighten the change-notice clause (e.g., 60 days for material changes, with right to suspend without penalty).
5. For OCC- or Federal Reserve-supervised institutions, document the event in the model risk inventory per OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7).

---

### Issue 8 — MCP tool server reachable without inventory entry

**Symptoms:** Network telemetry or agent execution log shows traffic to an MCP server absent from the approved server/vendor inventory; actual operator, destination and data determine its risk tier.

**Resolution:**
1. Remove the unapproved agent binding or block the supported connector/MCP server through applicable DLP/ACP. Network containment applies only where the deployment's actual supported route traverses infrastructure you govern; corporate device egress does not automatically control SaaS agent calls.
2. Identify the agent and owner that introduced the MCP reference.
3. Identify publisher, hosting operator, downstream services and applicable terms, then perform risk-tiered onboarding before re-enablement. Microsoft also publishes MCP connectors; MCP is not non-Microsoft by definition ([MCP integration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent)).
4. Validate the applicable network, connector/server, tool-selection and telemetry controls independently; record any unavailable enforcement plane as a gap.

---

## Microsoft Platform Update Monitoring

For Copilot Studio and Microsoft 365 Copilot, the underlying models are managed by Microsoft. Treat Microsoft as your highest-volume Tier T1 / T5 vendor and monitor for change.

For external model routes, identify the actual model operator and terms instead of extending that statement to every provider. Review primary models on **Overview → Model**, the live [availability/retirement matrix](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model), provider access plus PPAC environment/group settings, and [Anthropic route-specific terms](https://learn.microsoft.com/en-us/copilot/implement/connect-to-ai-subprocessor). Native selection is not a uniform GA, residency or contract promise.

| Channel | URL | What to Monitor |
|---------|-----|-----------------|
| Microsoft 365 Message Center | <https://admin.microsoft.com> → Message center | Copilot Studio, Power Platform, M365 Copilot updates |
| Service Health Dashboard | <https://admin.microsoft.com> → Service health | Outages, degraded performance, incident reports |
| Power Platform release plans | <https://learn.microsoft.com/en-us/power-platform/release-plan/> | Upcoming features and breaking changes |
| Copilot Studio What's New | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new> | Feature updates, model provider additions |
| Microsoft Service Trust Portal | <https://servicetrust.microsoft.com> | SOC 1/2/3, ISO, FedRAMP attestations |

### Recommended cadence

**Weekly:** Review Message Center for Power Platform / Copilot Studio entries; document items affecting deployed agents.

**Monthly:** Review Power Platform release notes; assess upcoming changes against Zone 2/3 agents; plan re-validation where needed.

**Quarterly:** Refresh vendor scorecards (including Microsoft); verify SOC 2 currency on the Service Trust Portal; assess platform changes against MRM (Control 2.6) thresholds.

### Re-validation triggers (Control 2.6 linkage)

Open a re-validation per [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) when:

- Microsoft announces a model change for a model used by a Zone 2/3 agent.
- Agent behavior metrics deviate from baseline beyond the threshold defined in the agent's monitoring plan.
- Microsoft announces deprecation of a feature the agent depends on.
- A service incident affects data integrity or output accuracy.
- Customer complaints, supervisory exceptions, or near-miss events increase without configuration change.

### Sample PowerShell — Message Center for Power Platform

```powershell
Connect-MgGraph -Scopes 'ServiceMessage.Read.All' -NoWelcome

Get-MgServiceAnnouncementMessage -All |
  Where-Object {
      ($_.Services -contains 'Power Platform' -or
       $_.Services -contains 'Microsoft Copilot Studio') -and
      $_.LastModifiedDateTime -gt (Get-Date).AddDays(-7)
  } |
  Select-Object Title, Severity, ActionRequiredByDateTime, LastModifiedDateTime |
  Format-Table -AutoSize
```

---

## Escalation Path

| Level | Owner | Trigger |
|------:|-------|---------|
| 1 | Power Platform Admin | Configuration / DLP / connector issues |
| 2 | AI Governance Lead | Policy, intake, allowlist disputes |
| 3 | Compliance Officer | Regulatory or recordkeeping implication |
| 4 | Vendor Risk Committee | Risk acceptance, vendor exit, material incident |
| 5 | Board / Risk Committee | Material breach or supervisory implication |

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md)
- [PowerShell Setup](powershell-setup.md)
- [Verification & Testing](verification-testing.md)

---

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation-only; no tenant execution)*
