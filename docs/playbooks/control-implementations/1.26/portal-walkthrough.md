# Portal Walkthrough: Control 1.26 - Agent File Upload and File Analysis Restrictions

**Last Updated:** May 2026
**Portals:** Microsoft Copilot Studio, Power Platform Admin Center (PPAC), Microsoft Purview, Microsoft Defender XDR (Zone 3)
**Estimated Time:** 20–40 minutes per agent (Zone 3 includes DLP and content-scanning verification)

## Prerequisites

- [ ] **AI Administrator** (canonical role per `docs/reference/role-catalog.md`) — primary owner for the per-agent **File Upload** toggle and allowed-file-type list
- [ ] **Power Platform Admin** — required for environment feature flags, Dataverse environment capacity and security role review, and DLP scope
- [ ] **Purview Compliance Admin** — required for DLP and sensitivity-label policy verification (Zone 2+)
- [ ] **Copilot Studio Agent Author** (Environment Maker + agent ownership) — required to open agent Settings
- [ ] Documented governance-zone classification for each target agent (Zone 1 / Zone 2 / Zone 3)
- [ ] Approved file-upload enablement request with documented business justification (Zone 2+); formal risk assessment (Zone 3)
- [ ] Companion: Control 1.25 (MIME Type Restrictions) implemented at the environment level — this control is *per-agent* and depends on environment-level allowlists for defense-in-depth

> **Scope note:** This walkthrough governs the **per-agent** File Upload toggle in Copilot Studio. Environment-wide file-type and MIME allowlists are governed by **Control 1.25**. Apply both for layered protection.

---

## Step-by-Step Configuration

### Step 1: Confirm Agent Zone Classification and Approval State

1. Open your agent inventory and confirm the agent's governance zone (1 / 2 / 3)
2. For **Zone 2** or **Zone 3** agents, confirm an approved file-upload enablement request exists in your governance system of record (ServiceNow, SharePoint List, Dataverse, etc.)
3. For **Zone 3** agents, confirm a documented risk assessment is on file and approved by the AI Governance Lead or designate

> **Important:** Do not toggle File Upload on for a Zone 2 or Zone 3 agent without the documented approval. Toggle changes are recorded in the Power Platform admin activity log and may surface during supervisory review.

### Step 2: Open the Per-Agent File Upload Settings (Copilot Studio)

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target environment from the environment switcher (top-right)
3. Open the target agent
4. Click the agent name → **Settings** → **Generative AI**
5. Navigate to the **File processing capabilities** section

> **Portal path (June 2026):** *Copilot Studio → \[Environment\] → \[Agent\] → Settings → Generative AI → File processing capabilities → File uploads*. Older guidance referencing a "Security → File Upload" or "Knowledge" sub-tab is stale.

### Step 3: Set the File Upload Toggle Per Zone

| Zone | Recommended Default | Conditions to Enable |
|------|---------------------|----------------------|
| Zone 1 (Personal) | **On** acceptable for personal-productivity use | None beyond Microsoft defaults; periodic review |
| Zone 2 (Team) | **Off** until approved | Documented approval and DLP coverage in the agent's environment |
| Zone 3 (Enterprise) | **Off** (default deny) | Formal risk assessment, AI Governance Lead approval, DLP enforce mode, and Defender content scanning |

1. Toggle **File Upload** to the state determined by Step 1's approval check
2. Click **Save**
3. **Republish** the agent: Copilot Studio caches agent runtime configuration; the new toggle state may not be enforced for clients until the agent is republished

> **Caveats (verify before relying on the toggle as a governance control):**
> - **CMK environments:** If the agent resides in a [Customer Managed Key (CMK)-enabled environment](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-customer-managed-keys#enable-cmk-for-copilot-studio), the toggle can be set to **On** but the agent will not process uploaded files. Document this as a compensating control gap. See [Troubleshooting](troubleshooting.md) for the diagnostic symptom.
> - **SharePoint channel:** If the agent is published to a SharePoint channel, users cannot upload files regardless of the toggle state (per Microsoft Learn). Verify the channel matrix before treating the per-agent toggle as an authoritative governance control for SharePoint-published agents.

### Step 4: Configure Allowed File Types (Per-Agent Allowlist)

> **Required for every Zone 2 and Zone 3 agent with File Upload = On.** PPAC controls (Control 1.25) establish the *maximum* permitted file types for the environment; per-agent allowlists apply *additional* least-privilege restrictions.

1. In the **File processing capabilities** section, locate **Allowed file types** (visible only when File uploads is **On**)
2. Reduce the allowlist to the minimum set required by the agent's documented purpose
   - Example: a contract-summary agent → `.pdf` only
   - Example: a financial-analysis agent → `.xlsx`, `.csv` only
3. Do not inherit the full environment allowlist by default
4. Click **Save** and republish

> **Note:** The supported file types for user runtime uploads (DOCX, CSV, PDF, TXT, JPG, PNG, WebP, non-animated GIF) are narrower than maker-uploaded knowledge source types (which include XML, HTML, JSON, YAML, and additional formats). Build Zone 3 allowlists against the [current MS Learn supported types list](https://learn.microsoft.com/en-us/microsoft-copilot-studio/image-input-analysis) for runtime uploads and the [knowledge source types list](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload#supported-document-types) for maker uploads.

### Step 5: Verify File Size and Per-Conversation Limits

1. Review and document the Microsoft-defined limits applicable to your agent (per Microsoft Learn):

    | Source | Limit |
    |---|---|
    | Maker-uploaded knowledge files | Up to **512 MB** per file |
    | Knowledge files per agent (Dataverse / local upload) | **500** files (see [Copilot Studio quotas and limits](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)) |
    | User-uploaded file at runtime (individual file size) | **15 MB** (see [Allow file input from users](https://learn.microsoft.com/en-us/microsoft-copilot-studio/image-input-analysis)) |
    | User-uploaded text file at runtime (character limit, without code interpreter) | **30,000 characters** per file |

2. For Zone 3, document any organizational reductions to these defaults (e.g., enforced via Defender for Cloud Apps file size policies) in the risk assessment

> **Note:** Microsoft does not currently expose a per-agent setting to lower these defaults below platform values. Reductions must be enforced via complementary controls (Defender file policies, Purview DLP rules, network egress policies).
>
> **Multi-channel note:** The 500-file limit applies to the Copilot Studio web app (Dataverse-stored knowledge). Multi-channel Zone 2/3 tenants should verify whether the Teams app surface exposes different file quota limits and document the applicable limits per channel in the risk assessment.

### Step 6: Verify Sensitivity Label Display (Preview Feature)

> **Preview:** Sensitivity label display in Copilot Studio agent responses is a preview feature per Microsoft Learn. Verify current GA status at [View sensitivity labels in agent responses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio) before treating this as a Regulated-zone baseline control.

1. In Copilot Studio, navigate to the agent's **Knowledge** section
2. If File Upload is **On**, upload two test files with different sensitivity labels applied at source (e.g., one **Confidential** and one **Highly Confidential**)
3. Send a test query that causes the agent to cite both files in its response
4. Confirm the response displays a shield icon showing the **Highly Confidential** label (the highest label among cited content in that response)
5. Capture screenshot evidence of the response-level label shield and store under `maintainers-local/tenant-evidence/1.26/` (gitignored)

> **Caveat:** The documented behavior is per-response shield display of the highest label among content **cited in that response** — not an agent-level inherited property. If the shield does not appear, verify Purview auto-labeling policies cover the Dataverse environment (the label must be present on the source file at the time of upload). See the [Troubleshooting](troubleshooting.md) playbook.

### Step 7: Verify DLP Policy Coverage (Zone 2+)

1. Open [Microsoft Purview](https://purview.microsoft.com) → **Data Loss Prevention** → **Policies**
2. Confirm a DLP policy exists that covers the **Power Platform** location and is scoped to the agent's environment
3. Confirm the policy is in **Enforce** mode (not Test or Off)
4. For Zone 3, confirm the policy includes the FSI-relevant Sensitive Information Types (US SSN, US Bank Account Number, Credit Card Number, ITIN, MNPI patterns) and configures **Block** action with override prohibited

### Step 8: Configure Defender for Cloud Apps Content Scanning (Zone 3)

> **Required for Zone 3.** PPAC and per-agent allowlists inspect declared file extensions and MIME headers; magic-byte (true content type) inspection requires Defender for Cloud Apps. See Control 1.25 portal walkthrough Step 7 for the parallel environment-level pattern; this step targets files associated with the agent's Dataverse environment.

1. Open [Microsoft Defender XDR portal](https://security.microsoft.com) → **Cloud apps** → **Policies** → **Policy management** → **File policy**
2. Create a file policy scoped to the Dataverse / Power Platform location associated with the agent's environment
3. Add filter: **MIME type (true type) does not equal** the approved per-agent allowlist
4. Governance actions: **Quarantine** + Notify file owner + Notify SOC distribution list
5. Create a **High** severity alert; forward to Microsoft Sentinel
6. Save and confirm the policy is **Enabled**

### Step 9: Review Dataverse Environment Storage Configuration

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com) → **Environments** → \[Environment\]
2. Navigate to **Resources → Capacity** to review Dataverse storage consumption for the environment hosting the agent's knowledge files
3. Navigate to **Settings → Users + permissions → Security roles** and verify:
   - Access to the Dataverse tables storing knowledge files is restricted to authorized service principals and admin roles
   - A Purview retention policy is applied (Zone 2+) that meets the agent's record-retention obligations under FINRA 4511 / SEC 17a-4(f)
   - Dataverse auditing is enabled for the environment (Zone 2+)
4. Capture the configuration as evidence (see [PowerShell Setup](powershell-setup.md) for SHA-256 evidence emission)

### Step 10: Update the Per-Agent Inventory

1. Update the file-upload inventory with:
   - Agent name and environment
   - Zone classification
   - Toggle state and allowed-file-type list
   - Approval reference (ticket / record ID)
   - Last review date and reviewer
2. Schedule the next review at the zone-appropriate cadence (Zone 1 quarterly / Zone 2 monthly / Zone 3 weekly)

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **File Upload toggle default** | Allowed | Disabled until approved | Default deny |
| **Per-agent allowed file types** | Microsoft defaults | Reduced to documented purpose | Minimum set; documented in risk assessment |
| **Approval required** | No | Documented approval | Formal risk assessment + AI Governance Lead approval |
| **Sensitivity label inheritance** | Recommended | Required | Required with audit trail |
| **DLP policy coverage** | Not required | Required (Enforce mode) | Required + content scanning |
| **Defender for Cloud Apps content scanning** | Not required | Optional | Required (true-MIME inspection) |
| **Dataverse environment retention policy** | Recommended | Required | Required + auditing enabled |
| **Sentinel monitoring** | Optional | Optional | Required |
| **Inventory tracking** | Recommended | Required | Required |
| **Review frequency** | Quarterly | Monthly | Weekly |
| **Exception process** | Informal | Documented | Documented with approval |

---

## Validation

After completing these steps, verify:

- [ ] Per-agent **File Upload** toggle state matches the agent's zone and approval status
- [ ] Per-agent **Allowed file types** list is reduced to the minimum required by the agent's documented purpose (Zone 2+)
- [ ] Sensitivity-label response shield test passes (agent response displays the highest sensitivity label of cited content — preview feature; see Step 6)
- [ ] DLP policy in **Enforce** mode covers the agent's environment (Zone 2+)
- [ ] Defender for Cloud Apps file policy with true-MIME inspection is **Enabled** (Zone 3)
- [ ] Dataverse environment security roles, retention policy, and auditing are configured (Zone 2+)
- [ ] Per-agent inventory updated with toggle state, approval reference, and next review date
- [ ] Screenshot evidence captured under `maintainers-local/tenant-evidence/1.26/` (gitignored — never push to the repository)

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: June 2026 | Version: v1.6.2 | UI Verification Status: Current*
