# Control 2.7: Vendor and Third-Party Risk Management — Troubleshooting

> Companion to [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md). Common failure modes and resolutions for vendor and connector risk management in M365 / Power Platform / Copilot Studio.

---

## Quick Reference

| # | Issue | Likely Root Cause | First Action |
|---|-------|-------------------|--------------|
| 1 | Inventory misses connectors actually in use | Producer environments outside scope; service principals creating apps | Enumerate **all** environments via PowerShell; cross-check Purview audit |
| 2 | Vendor cannot supply SOC 2 Type II | Smaller vendor, pre-attestation maturity | Accept ISO 27001 + bridge letter + independent assessment; document risk acceptance |
| 3 | Custom connector created without review | Producer environment lacks creation restriction | Restrict in Managed Environments; route producers to designated environments |
| 4 | Vendor incident notice arrived late | Contract notification window not enforced | Re-paper contract; raise vendor risk score; escalate to vendor risk committee |
| 5 | DLP policy fails to block expected connector | Less-restrictive policy wins; classification missing | Validate effective policy; ensure target connector classified and policy scoped |
| 6 | Community / independent-publisher plugin appeared in Copilot Studio agent | Tenant allows non-allowlisted plugins; admin not scoped | Disable plugin; tighten Copilot Studio plugin governance; notify agent owner |
| 7 | LLM vendor changed model behavior with no notice | Contract clause weak or absent | Trigger Control 2.6 re-validation; re-paper contract; consider vendor change |
| 8 | MCP tool server reachable from agent without inventory entry | Egress not gated; intake bypassed | Block egress to MCP server; require Tier T5 onboarding before re-enabling |

---

## Detailed Troubleshooting

### Issue 1 — Connector inventory is incomplete

**Symptoms:** Audit discovers connectors in production not present in the inventory; new connectors appear without intake.

**Diagnostics:**
1. Run the inventory snapshot from the [PowerShell Setup](powershell-setup.md) playbook against **every** environment, including default and personal productivity.
2. Cross-reference Purview audit (operations: `CreateConnection`, `RegisterCustomConnector`, `UpdateApp` with new connection IDs) for the prior 90 days.
3. Confirm no service principals are creating connections outside the inventory pipeline.

**Resolution:**
- Add an automated weekly snapshot to the evidence pipeline.
- Enable Power Platform admin alerts for new connector creation in Zone 2/3.
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
1. Disable the connector immediately if it carries customer NPI, MNPI, or supervisory data.
2. Run the custom connector enumeration script and assess data exposure.
3. In the affected environment, restrict custom connector creation via Managed Environments → **Sharing limits** and **Maker controls** (see [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)).
4. Establish designated producer environments for custom connector development; block production environments from creation rights.
5. Add a Power Platform admin alert for `RegisterCustomConnector` events.

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
1. Open Power Platform admin center → **Policies → Data policies** → select policy → **Policy effects**. Confirm the connector is in the **Blocked** group and the policy is scoped to the user's environment.
2. If multiple policies apply, the **most restrictive wins**, but only across overlapping environments. Validate environment-to-policy mapping.
3. Check propagation: changes can take up to **one hour** to take effect.
4. Confirm the environment is **Managed** — some advanced DLP controls require Managed Environments.

**Resolution:**
- Reclassify the connector and republish the policy.
- Verify Conditional Access does not bypass policy via service-principal flows.
- For Copilot Studio plugins, confirm the plugin is also restricted at the Copilot Studio agent layer (DLP alone does not govern all plugin types).

---

### Issue 6 — Independent / community plugin appeared in a Copilot Studio agent

**Symptoms:** Unvetted plugin discovered in agent **Tools / Plugins** tab.

**Resolution:**
1. Disable the plugin immediately and remove it from the agent.
2. Review tool-call audit logs for data sent to the plugin endpoint.
3. Assess whether NPI, MNPI, or supervisory content was transmitted. If yes, follow Control 3.x incident response and consider notification obligations.
4. Strengthen prevention: tenant-level Copilot Studio plugin allowlist, restrict agent-author roles, and require AI Administrator approval for new plugin enablement.

---

### Issue 7 — AI/LLM vendor changed model behavior without notice

**Symptoms:** Agent accuracy, latency, or output character changes unexpectedly; no contract-required notification was received.

**Resolution:**
1. Capture before/after evidence (sampled prompt/response pairs, evaluation metrics).
2. Treat as a **model change** under Control 2.6 — re-validate the agent before continued production use if the change is material.
3. Open a contract dispute citing the missing notification; require the vendor to publish a change log with retroactive notice.
4. Re-paper the contract to tighten the change-notice clause (e.g., 60 days for material changes, with right to suspend without penalty).
5. For OCC- or Federal Reserve-supervised institutions, document the event in the model risk inventory per OCC 2011-12 / SR 11-7.

---

### Issue 8 — MCP tool server reachable without inventory entry

**Symptoms:** Network telemetry or agent execution log shows traffic to an MCP server that is not in the Tier T5 inventory.

**Resolution:**
1. Block egress to the unknown MCP endpoint at the network layer.
2. Identify the agent and owner that introduced the MCP reference.
3. Require formal Tier T5 onboarding (vendor diligence pack, contract, AI-clauses) before any re-enablement.
4. Add network egress allowlisting as a control for Zone 3 agents reaching external services.

---

## Microsoft Platform Update Monitoring

For Copilot Studio and Microsoft 365 Copilot, the underlying models are managed by Microsoft. Treat Microsoft as your highest-volume Tier T1 / T5 vendor and monitor for change.

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

Open a re-validation per [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) when:

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

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
