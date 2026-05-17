# Verification & Testing: Control 1.24 — Defender AI Security Posture Management (AI-SPM)

**Last Updated:** April 2026
**Audience:** M365 administrators in US financial services
**Test cadence:** Monthly (Z1) / Weekly (Z2) / Daily (Z3)

> **Hedging note:** The procedures below help support evidence collection for OCC Bulletin 2026-13 (formerly OCC 2011-12), FINRA 25-07, and NIST AI RMF MEASURE function. They do not by themselves attest to control effectiveness — supervisory review and Model Risk Committee sign-off are also required.

---

## Test Plan Overview

| Test ID | Scenario | Expected Result | Zone Applicability |
|---------|----------|-----------------|---------------------|
| TC-1.24-01 | Defender CSPM Standard enabled | Tier shows `Standard` per subscription | Z1, Z2, Z3 |
| TC-1.24-02 | AI-SPM extension enabled | Extension `AIThreatProtection` reads enabled | Z1, Z2, Z3 |
| TC-1.24-03 | AI workloads discovered | All known AI resources appear in inventory | Z1, Z2, Z3 |
| TC-1.24-04 | AI BOM populated | BOM tab lists models, data sources, dependencies | Z2, Z3 |
| TC-1.24-05 | AI-specific attack paths surface | At least one path appears or zero with documented justification | Z2, Z3 |
| TC-1.24-06 | AI security recommendations generated | AI-related recommendations visible in Recommendations blade | Z1, Z2, Z3 |
| TC-1.24-07 | Defender for AI Services runtime alerts | Synthetic jailbreak prompt produces alert in Defender XDR | Z2, Z3 |
| TC-1.24-08 | Multi-cloud connector health | AWS/GCP connector status `Healthy` | Z2, Z3 if applicable |
| TC-1.24-09 | Sentinel data connector connected | Data connector status `Connected` | Z3 |
| TC-1.24-10 | Risk factor scoring populated | At least one agent has prompt-injection / data-exposure risk score | Z2, Z3 |
| TC-1.24-11 | Remediation SLA tracking | Open AI recommendations have owner + due date per zone SLA | Z1, Z2, Z3 |
| TC-1.24-12 | AI BOM reconciles to architecture-of-record | No orphan or undocumented AI resources | Z2, Z3 |

---

## Manual Verification Procedures

### TC-1.24-01 / 02 — Defender CSPM + AI-SPM extension

1. Azure Portal → **Defender for Cloud → Environment settings → [subscription] → Defender plans**.
2. Confirm **Defender CSPM** = **On** at **Standard** tier.
3. Click **Settings** on the CSPM row → confirm **AI security posture management** toggle is **On**.
4. Capture screenshot for evidence.

### TC-1.24-03 / 04 — AI workload discovery + AI BOM

1. **Defender for Cloud → Inventory**.
2. Filter Resource type → AI/ML services.
3. For each known agent / Azure OpenAI account / AI Foundry project, click in and review the **AI BOM** tab.
4. Reconcile against the architecture-of-record (firm's authoritative AI system catalog).
5. Document any orphan resources (in BOM but not in catalog) or shadow AI (not in BOM but discovered elsewhere) for remediation.

### TC-1.24-05 — AI attack paths

1. **Defender for Cloud → Cloud Security → Attack path analysis**.
2. Filter by AI resource types.
3. If zero attack paths, document the rationale (e.g., all AI endpoints private, no exposed entry points). Zero with justification is acceptable; zero without review is not.

### TC-1.24-07 — Synthetic jailbreak validation (Z2 / Z3)

> **Test in non-production only.** Coordinate with SOC before running. Document as a controlled test in the security event log.

1. Open a Copilot Studio agent in a non-production environment connected to Azure AI / Azure OpenAI.
2. Issue a known-benign jailbreak test prompt from the [Microsoft Defender XDR public test suite](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-threat-protection) (e.g., the documented `ignore previous instructions` test pattern).
3. Within ~5 minutes, confirm an alert appears in **Microsoft Defender XDR → Incidents & alerts** with title containing `jailbreak`.
4. Document the alert ID and route through the SOC runbook.
5. Close the test alert with the `Test/Validation` classification.

### TC-1.24-09 — Sentinel data connector (Z3)

1. **Microsoft Sentinel → Configuration → Data connectors → Microsoft Defender for Cloud**.
2. Confirm status = **Connected**.
3. Run KQL: `SecurityAlert | where ProductName == "Microsoft Defender for Cloud" and AlertName has_any ("AI", "OpenAI", "jailbreak", "prompt") | take 10`
4. Confirm rows return (after the synthetic test in TC-1.24-07).

---

## Automated Verification

Run [`Validate-Control-1.24.ps1`](powershell-setup.md#script-5-validate-control-124ps1-composite-validator) and capture:

- JSON output in evidence repository
- SHA-256 hash file (`*.sha256`) for integrity
- Exit code (0 = pass; 2 = failure on at least one subscription)

---

## Evidence Collection Checklist

Per quarterly attestation cycle, capture and file:

- [ ] Screenshot — Defender plans page (CSPM Standard + AI-SPM enabled) — per subscription
- [ ] Screenshot — Defender for AI Services plan (Z2/Z3)
- [ ] Screenshot — AI inventory list
- [ ] Screenshot — AI BOM tab for at least one in-scope agent
- [ ] Screenshot — Attack path analysis filtered to AI
- [ ] Screenshot — Recommendations filtered to AI resources with owner / due date
- [ ] Screenshot — Sentinel data connector status (Z3)
- [ ] CSV — `AISPM-Status-yyyymmdd.csv`
- [ ] CSV — `AI-BOM-yyyymmdd.csv`
- [ ] CSV — `AttackPaths-yyyymmdd.csv`
- [ ] JSON — `Control-1.24-Validation-yyyymmdd.json`
- [ ] SHA-256 hash files for each export
- [ ] Synthetic jailbreak test record (TC-1.24-07) — alert ID, timestamp, tester
- [ ] AI BOM reconciliation memo signed by AI Governance Lead
- [ ] Remediation tracker — open recommendations with owner, due date, current status

Retain per the longer of: FINRA Rule 4511 (6 years), SOX (7 years), or firm policy.

---

## KQL Evidence Queries

Run in Microsoft Sentinel (or Defender XDR Advanced Hunting).

```kql
// AI-related Defender alerts in last 30 days
SecurityAlert
| where TimeGenerated > ago(30d)
| where ProductName in ("Microsoft Defender for Cloud", "Microsoft Defender XDR")
| where AlertName has_any ("AI", "OpenAI", "jailbreak", "prompt", "ASCII smuggling", "Copilot")
| summarize Count = count(), FirstSeen = min(TimeGenerated), LastSeen = max(TimeGenerated)
    by AlertName, AlertSeverity
| order by Count desc
```

```kql
// AI resource inventory snapshot (Resource Graph Explorer)
Resources
| where type in~ (
    'microsoft.cognitiveservices/accounts',
    'microsoft.machinelearningservices/workspaces',
    'microsoft.search/searchservices'
)
| summarize ResourceCount = count() by Type = type, Region = location
| order by ResourceCount desc
```

```kql
// Open AI-related security recommendations
SecurityRecommendation
| where TimeGenerated > ago(7d)
| where AssessedResourceType has_any ("CognitiveServices", "MachineLearning", "OpenAI", "AIFoundry")
| where RecommendationState == "Active"
| summarize OpenCount = count() by RecommendationName, RecommendationSeverity
| order by RecommendationSeverity asc, OpenCount desc
```

---

## Attestation Statement Template

```markdown
## Control 1.24 Attestation — Defender AI Security Posture Management

**Organization:** _____________________
**Control Owner:** _____________________ (Role)
**Attestation Period:** Q_ YYYY  ([start date] – [end date])
**Date of Attestation:** _____________________

I attest that for the attestation period:

1. Defender for Cloud CSPM (Standard tier) was enabled on all in-scope Azure subscriptions
   that hosted AI workloads. Subscriptions in scope: ____ ; subscriptions enabled: ____.
2. The AI security posture management extension was enabled on each in-scope subscription.
3. AI workload discovery was active. AI Bill of Materials counts:
   - Azure OpenAI accounts: ____
   - Azure AI Services / Cognitive Services: ____
   - Azure ML workspaces: ____
   - Azure AI Foundry projects: ____
   - Multi-cloud (AWS/GCP) AI resources: ____
4. Attack paths targeting AI were reviewed at the cadence required for Zone ____:
   - Critical attack paths open at period start: ____
   - Remediated within SLA: ____ ; Accepted with documented compensating control: ____
5. AI security recommendations were triaged and remediated per zone SLA:
   - Critical: ____ open / ____ closed (SLA: 30 days Z1 / 7 days Z2 / 72 hours Z3)
   - High:     ____ open / ____ closed
   - Medium:   ____ open / ____ closed
6. Defender for AI Services runtime alerts (Zone 2/3) were investigated per SOC runbook.
   Total alerts: ____ ; True positives: ____ ; False positives: ____
7. Synthetic jailbreak test (TC-1.24-07) was executed on ____________ (date). Alert ID: ________.
8. Sentinel data connector (Zone 3) was connected for the full period.
9. AI BOM was reconciled against architecture-of-record on ____________. Discrepancies: ____.

Evidence files (with SHA-256 integrity hashes) are filed in: _____________________

**Signature:** _______________________   **Date:** _______________________
```

---

## Zone-Specific Test Frequency

| Zone | Inventory Verification | Attack Path Review | Recommendation Review | Synthetic Test |
|------|------------------------|--------------------|------------------------|----------------|
| Zone 1 | Monthly | Monthly | Monthly | Annual |
| Zone 2 | Weekly | Weekly | Weekly | Quarterly |
| Zone 3 | Daily | Daily | Daily | Monthly |

---

[Back to Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
