# Portal Walkthrough: Control 1.24 — Defender AI Security Posture Management (AI-SPM)

**Last Updated:** May 2026
**Portal:** Microsoft Defender for Cloud (Azure Portal — `portal.azure.com`)
**Estimated Time:** 2–3 hours per subscription (initial enablement); ~30 min/week ongoing review
**Audience:** M365 administrators in US financial services

> **Hedging note:** Enabling AI-SPM helps support OCC Bulletin 2026-13 (formerly OCC 2011-12), Fed SR 26-2 (formerly SR 11-7), and FINRA RN 24-09 + Rule 3110 expectations for AI inventory and model risk monitoring. It does not, by itself, satisfy those obligations — supervisory procedures, evidence retention, and Model Risk Committee review are also required.

---

## Prerequisites

- [ ] **Azure subscription(s)** that host AI workloads (Azure OpenAI, Azure AI Foundry, Azure AI Services / Cognitive Services, Azure Machine Learning)
- [ ] **Defender CSPM (Standard tier)** plan available — this is a paid plan; AI-SPM is included as an extension at no extra cost as of April 2026, but Defender CSPM itself is metered
- [ ] **Entra Security Admin** role (canonical) on the tenant — required to configure Defender plans and connectors
- [ ] **Owner** or **Contributor + Security Admin** at the Azure subscription scope to toggle Defender plans
- [ ] (Optional) AWS account with IAM admin rights for AWS Bedrock/SageMaker connector
- [ ] (Optional) GCP project with Org Admin / Project Owner for Vertex AI connector
- [ ] Microsoft Sentinel workspace identified (required for Zone 3)

---

## Step 1 — Enable Defender CSPM on each in-scope subscription

1. Sign in to the [Azure Portal](https://portal.azure.com) as Entra Security Admin.
2. Search **Microsoft Defender for Cloud** → open the service.
3. Left navigation → **Management** group → **Environment settings**.
4. Expand the management group / tenant tree and select the **Azure subscription** that hosts AI workloads.
5. On the subscription **Defender plans** page, locate **Defender CSPM** and toggle to **On** (Standard tier).
6. Click **Save** at the top of the page.

> If **Defender CSPM** is already on, confirm pricing tier reads **Standard** (not Foundational/free) — AI-SPM is unavailable on Foundational.

---

## Step 2 — Enable the AI security posture management extension

1. Same **Environment settings → [subscription] → Defender plans** page.
2. On the **Defender CSPM** row, click **Settings** (or the gear icon).
3. In the **Extensions** blade, locate **AI security posture management** and toggle **On**.
4. Also confirm **Microsoft Threat Intelligence** is **On** (required for AI-specific attack path scenarios).
5. Click **Continue** → **Save**.

> Initial discovery typically takes **4–24 hours** to populate the AI BOM. Plan validation activities accordingly.

---

## Step 3 — Enable Defender for AI Services (runtime threat protection)

AI-SPM provides posture findings (proactive). Defender for AI Services provides runtime detections (reactive). FSI Zone 2 and Zone 3 should enable both.

1. Same **Defender plans** page.
2. Locate **AI workloads** (formerly *Defender for AI Services*) and toggle **On**.
3. Confirm enablement of **Threat protection for AI workloads** in the settings blade (covers jailbreak attempts, prompt leak, ASCII smuggling, sensitive-data exposure alerts, reconnaissance).
4. Click **Save**.

---

## Step 4 — Verify AI workload discovery

1. Defender for Cloud left nav → **General** → **Inventory**.
2. Apply filter: **Resource type** = `Azure AI services`, `Azure OpenAI`, `Azure Machine Learning workspace`, or `Azure AI Foundry`.
3. Confirm each known AI resource appears.
4. Click into a resource and review the **AI BOM** tab — confirm models, data connections, and dependencies are listed.

If a known resource is missing, see [Troubleshooting](troubleshooting.md) — *AI workloads not appearing in inventory*.

---

## Step 5 — Review attack paths for AI workloads

1. Left nav → **Cloud Security** → **Attack path analysis**.
2. **Filter** → Resource type → select AI resource types.
3. Review attack paths. Common AI-specific scenarios as of April 2026:
   - Internet-exposed Azure OpenAI endpoint with access to sensitive data store
   - Microsoft Copilot Studio agent with over-permissive Dataverse role chained to a public-facing trigger
   - AI Foundry project with managed identity granting access to a Key Vault containing customer secrets
   - Indirect prompt injection chain (external content source → agent → privileged action)
4. For each path, click **Insights** to review evidence, then **Remediate** for prioritized recommendations.
5. Document remediation decisions (fix, accept risk, compensating control) in the firm's model risk register.

---

## Step 6 — Review and triage AI security recommendations

1. Left nav → **Cloud Security** → **Recommendations**.
2. **Filter** → **Resource type** = AI services / ML workspace / OpenAI / AI Foundry.
3. Sort by **Risk score** (descending). Common high-impact recommendations:
   - Azure OpenAI accounts should disable public network access
   - Cognitive Services accounts should use managed identity
   - Azure AI Services should have customer-managed keys (CMK) for at-rest encryption
   - Diagnostic logs for Azure OpenAI should be enabled
4. Assign owner and target remediation date per zone SLA (Zone 1: 30 days, Zone 2: 14 days, Zone 3: 72 hours for critical).

---

## Step 7 — Configure multi-cloud connectors (if applicable)

Skip this step for tenants exclusively using Azure-hosted AI.

### AWS (Amazon Bedrock / SageMaker)

1. **Environment settings** → **Add environment** → **Amazon Web Services**.
2. Provide AWS account ID, region, and choose **AI security posture management** in the plan list.
3. Download the CloudFormation template and deploy in the AWS account (creates the cross-account IAM role).
4. Click **Next** through the wizard → **Create**.

### GCP (Vertex AI — GA November 2025)

1. **Environment settings** → **Add environment** → **Google Cloud Platform**.
2. Provide GCP organization or project ID; select **AI security posture management**.
3. Run the provided `gcloud` script to create the workload identity federation and required IAM bindings.
4. Click **Create**.

Validate by checking **Inventory** for non-Azure AI resources after ~24 hours.

---

## Step 8 — Integrate with Microsoft Sentinel (required for Zone 3)

1. Open **Microsoft Sentinel** in Azure Portal → select the Zone 3 SOC workspace.
2. **Configuration** → **Data connectors** → search **Microsoft Defender for Cloud**.
3. Click **Open connector page** → **Connect** the in-scope subscriptions.
4. Enable **Bi-directional sync** if your SOC manages alerts from Sentinel back to Defender.
5. Under **Analytics rules**, enable Microsoft-provided rule templates filtered by `AI` (e.g., `Suspicious AI workload activity`, `Jailbreak attempt detected`).

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| Defender CSPM (Standard) | Required | Required | Required |
| AI-SPM extension | Required | Required | Required |
| Defender for AI Services (runtime) | Optional | Required | Required |
| Microsoft Threat Intelligence extension | Recommended | Required | Required |
| Multi-cloud connectors | If applicable | If applicable | Required if any non-Azure AI |
| Sentinel data connector | Optional | Recommended | Required |
| Attack path review cadence | Monthly | Weekly | Daily |
| Critical remediation SLA | 30 days | 7 days | 72 hours |
| AI BOM reconciliation | Annual | Quarterly | Quarterly + Model Risk Committee |

---

## Validation Checklist

- [ ] Defender CSPM reads **Standard** on every in-scope subscription
- [ ] AI security posture management extension shows **Enabled**
- [ ] AI workloads appear in **Inventory**
- [ ] AI BOM tab populated for at least one known agent / model
- [ ] At least one AI-related attack path or recommendation is visible (or zero with documented justification)
- [ ] Defender for AI Services runtime alerts are routed to Defender XDR (Zone 2/3)
- [ ] Sentinel data connector reads **Connected** (Zone 3)
- [ ] Multi-cloud connector status is **Healthy** (where configured)

---

## FSI Evidence to Capture

For supervisory and audit evidence retention:

- Screenshot of **Defender plans** page showing CSPM Standard + AI-SPM toggled on (per subscription)
- Export of **Inventory** filtered to AI workloads (CSV)
- Export of **Recommendations** filtered to AI resources (CSV)
- Export of **Attack paths** for AI resources (CSV via REST API — see [PowerShell Setup](powershell-setup.md))
- AI BOM extract — filed in the model risk register

Retain for the longer of: FINRA WORM retention (6 years per Rule 4511), SOX retention (7 years), or firm policy.

---

[Back to Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
