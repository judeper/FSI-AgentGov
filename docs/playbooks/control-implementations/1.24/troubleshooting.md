# Troubleshooting: Control 1.24 — Defender AI Security Posture Management (AI-SPM)

**Last Updated:** April 2026
**Audience:** M365 administrators in US financial services

> **Hedging note:** Resolutions below address common operational issues. They do not absolve the firm of independent verification or model risk assessment obligations under OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7).

---

## Quick-Reference Issue Matrix

| # | Symptom | Most Likely Cause | First Action |
|---|---------|-------------------|--------------|
| 1 | AI-SPM extension toggle missing | Defender CSPM is on **Foundational** (free) tier, not Standard | Upgrade CSPM to Standard |
| 2 | AI workloads not in inventory | Recently created (<24 h) or subscription excluded | Wait 24 h; verify exemptions |
| 3 | No attack paths visible | No internet exposure or compensating controls in place | Validate via test scenario |
| 4 | AI BOM tab shows partial data | Discovery still warming up; agent not yet registered | Wait 24–48 h after first traffic |
| 5 | Multi-cloud connector unhealthy | IAM/service-account permission drift | Re-run onboarding wizard |
| 6 | Recommendations missing | Feature still rolling out to region; no AI assets present | Confirm regional availability |
| 7 | Sentinel not receiving AI alerts | Data connector disconnected; rule template disabled | Re-enable connector + rules |
| 8 | Defender for AI Services alerts not firing | Plan not enabled; agent not connected to Azure AI | Verify plan + integration |
| 9 | Synthetic jailbreak test produces no alert | Defender for AI Services not enabled, or alert routing rule blocks XDR | Confirm runtime plan + XDR routing |
| 10 | `Set-AzSecurityPricing` errors with Forbidden | Caller missing Security Admin or Contributor at subscription scope | Re-elevate via PIM |

---

## Detailed Troubleshooting

### Issue 1 — AI-SPM extension toggle is missing

**Symptoms:** Under **Defender CSPM → Settings**, no `AI security posture management` toggle appears.

**Resolution:**

1. Verify Defender CSPM pricing tier is **Standard**:
   ```powershell
   Get-AzSecurityPricing -Name CloudPosture | Select PricingTier
   ```
2. If `Free`, upgrade:
   ```powershell
   Set-AzSecurityPricing -Name CloudPosture -PricingTier Standard -WhatIf
   ```
3. Confirm the caller has **Security Admin** at the subscription scope.
4. Confirm the subscription region supports AI-SPM (rolling out; check the Azure status page).

---

### Issue 2 — AI workloads not appearing in Inventory

**Symptoms:** Known Azure OpenAI account exists but does not appear under Defender for Cloud Inventory.

**Resolution:**

1. Confirm the resource is in a subscription that has **Defender CSPM Standard** enabled.
2. Confirm the resource was created more than **4–24 hours** ago (initial discovery).
3. Verify Resource Graph can see it:
   ```powershell
   Search-AzGraph -Query "Resources | where type =~ 'microsoft.cognitiveservices/accounts' | where name == '<resource-name>'"
   ```
4. Check **Environment settings → [subscription] → Exclusions** for explicit exclusions of resource type or resource group.
5. Confirm the subscription is not in a parental management group with conflicting policy.

---

### Issue 3 — Attack paths empty for AI resources

**Symptoms:** Attack path analysis returns zero results when filtered to AI workloads.

**Resolution:**

1. Allow **24–48 hours** after AI-SPM enablement for first analysis.
2. Validate that at least one AI resource has a meaningful exposure (public network, identity-based access to data, etc.). Resources that are network-isolated and identity-locked may legitimately produce no attack paths.
3. Confirm **Microsoft Threat Intelligence** extension is enabled on Defender CSPM (required for many AI scenarios).
4. Run a controlled test: temporarily expose a non-production AI endpoint with public network access, wait 24 h, and confirm an attack path appears. **Revert the exposure immediately after the test.**
5. Document zero-result outcomes in the model risk register with justification.

---

### Issue 4 — AI BOM tab shows partial data

**Symptoms:** Models or data dependencies are missing from the AI BOM tab for an inventoried AI resource.

**Resolution:**

1. Confirm the agent has had at least one inference call after AI-SPM enablement (BOM discovery is partly traffic-driven).
2. For Copilot Studio agents, ensure the agent is **published** in the environment, not just in draft.
3. For Azure AI Foundry projects, confirm models are deployed to an endpoint (deployments populate the BOM; registered-only models may not).
4. Refresh the inventory page after 4 hours.
5. Where BOM is incomplete after 48 hours, file an Azure support ticket with severity matched to the workload sensitivity.

---

### Issue 5 — Multi-cloud connector unhealthy

**Symptoms:** AWS or GCP connector status reads `Unhealthy` or `Authorization error`.

**Resolution (AWS):**

1. **Environment settings → [AWS connector] → Health**.
2. Verify CloudFormation stack is intact and current:
   ```bash
   aws cloudformation describe-stacks --stack-name <defender-stack-name>
   ```
3. Confirm IAM role trust policy allows the Defender for Cloud principal.
4. Re-download and re-deploy the CloudFormation template if Microsoft has revised role permissions (commonly happens when new AI services are added).

**Resolution (GCP):**

1. **Environment settings → [GCP connector] → Health**.
2. Re-run the provided `gcloud` script to refresh workload identity federation bindings.
3. Confirm the service account has at minimum: `roles/aiplatform.viewer`, `roles/cloudasset.viewer`, `roles/iam.securityReviewer`.

---

### Issue 7 — Sentinel not receiving AI alerts

**Symptoms:** Defender for Cloud generates AI alerts in the Defender portal but they do not appear in Sentinel.

**Resolution:**

1. **Sentinel → Configuration → Data connectors → Microsoft Defender for Cloud**: verify status `Connected`.
2. Under the connector, confirm **bi-directional sync** is enabled if your SOC closes alerts in Sentinel.
3. Verify analytics rule templates are enabled (filter rule templates by `AI`).
4. Run KQL to confirm raw ingestion: `SecurityAlert | where ProductName == "Microsoft Defender for Cloud" | take 5`
5. If raw rows arrive but rules don't trigger, review rule logic for threshold mismatches.

---

### Issue 8 — Defender for AI Services not generating runtime alerts

**Symptoms:** Defender for AI Services plan is enabled but no jailbreak / prompt-leak alerts appear despite test prompts.

**Resolution:**

1. Confirm the **AI workloads** plan reads `Standard`:
   ```powershell
   Get-AzSecurityPricing -Name AI | Select PricingTier
   ```
2. Confirm the agent is connected to a supported Azure AI / Azure OpenAI deployment in an in-scope subscription.
3. For Copilot Studio agents, confirm Defender for Cloud Apps **real-time agent protection** is enabled at the tenant level (separate licensing — typically Microsoft 365 E5 Compliance / Security).
4. Confirm the alert routing rule in Defender XDR has not suppressed AI alert types.
5. Re-run the synthetic test and watch the **Defender for Cloud → Security alerts** blade in real time.

---

## Diagnostic Commands

```powershell
# All Defender plans for current subscription
Get-AzSecurityPricing | Format-Table Name, PricingTier, @{N='Extensions';E={($_.Extensions | Where-Object IsEnabled -EQ 'True' | Select-Object -ExpandProperty Name) -join ';'}}

# Resource Graph reachability
Search-AzGraph -Query "Resources | take 1"

# AI resource enumeration
Get-AzResource | Where-Object ResourceType -match 'cognitiveservices|machinelearning|openai|aifoundry' |
  Format-Table Name, ResourceType, ResourceGroupName, Location

# Confirm caller has Security Admin at subscription scope
Get-AzRoleAssignment -SignInName (Get-AzContext).Account.Id |
  Where-Object RoleDefinitionName -match 'Security|Owner|Contributor'
```

---

## Known Limitations (April 2026)

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Discovery latency 4–24 hours | New AI resources delayed | Use Resource Graph + `Get-AIWorkloadInventory.ps1` for immediate evidence |
| Regional availability variance | AI-SPM not in all Azure regions | Track via Azure roadmap; deploy in supported region for centralized governance |
| AWS/GCP coverage gaps | Some niche AI services unsupported | Manual inventory for unsupported services; document in AI BOM addendum |
| Attack path scope | Cannot model every prompt-injection chain | Supplement with red-team threat modeling and runtime protection (Defender for AI Services) |
| Copilot Studio shadow agents | Discovery preview; not all agents tracked | Combine with Power Platform Admin Center inventory (Control 3.1) and Defender for Cloud Apps |
| Defender for AI Services billing | Per-token pricing can be material at scale | Forecast via test environment before broad rollout; budget per zone |
| Sovereign cloud (DoD) feature parity | AI-SPM may lag commercial GA | Confirm parity with Microsoft FedRAMP team before Zone 3 commitment |

---

## Escalation Path

1. **Control Owner / Security Admin** — configuration, permissions, basic discovery issues
2. **Cloud Security Architect** — attack path interpretation, AI BOM reconciliation
3. **AI Governance Lead** — model risk register alignment, BOM discrepancy disposition
4. **Microsoft Azure Support** — platform issues; open with severity matching workload (Severity A for Zone 3 customer-facing impact)
5. **Microsoft FastTrack / Account Team** — feature availability, regional rollout, sovereign cloud parity
6. **Model Risk Committee** — material AI BOM discrepancies; control failures impacting attestation

---

## Related Documentation

- [Microsoft Learn: Defender for Cloud troubleshooting](https://learn.microsoft.com/en-us/azure/defender-for-cloud/troubleshooting-guide)
- [Microsoft Learn: AI security posture management](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-security-posture)
- [Microsoft Learn: Attack path analysis](https://learn.microsoft.com/en-us/azure/defender-for-cloud/concept-attack-path)
- [Microsoft Learn: Multi-cloud connectors](https://learn.microsoft.com/en-us/azure/defender-for-cloud/multicloud)
- [Microsoft Learn: Real-time agent protection (Defender for Cloud Apps)](https://learn.microsoft.com/en-us/defender-cloud-apps/real-time-agent-protection-during-runtime)

---

[Back to Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
