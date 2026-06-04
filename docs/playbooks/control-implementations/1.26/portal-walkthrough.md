# Portal Walkthrough: Control 1.26 - Agent File Upload and File Analysis Restrictions

**Last Updated:** May 2026
**Portals:** Microsoft Copilot Studio, Power Platform Admin Center (PPAC), Microsoft Purview, Microsoft Defender XDR (Zone 3)
**Estimated Time:** 20–40 minutes per agent (Zone 3 includes DLP and content-scanning verification)

## Prerequisites

- [ ] **AI Administrator** (canonical role per `docs/reference/role-catalog.md`) — primary owner for the per-agent **File Upload** toggle and allowed-file-type list
- [ ] **Power Platform Admin** — required for environment feature flags, SharePoint Embedded (SPE) container review, and DLP scope
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

### Step 2: Open the Per-Agent Security Panel (Copilot Studio)

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target environment from the environment switcher (top-right)
3. Open the target agent
4. Click the agent name → **Settings** → **Security**

> **Portal path (April 2026):** *Copilot Studio → \[Environment\] → \[Agent\] → Settings → Security → File Upload*. The **Security** node is reached from the per-agent Settings panel; older guidance that lists a **Knowledge** sub-tab for the toggle is stale.

### Step 3: Set the File Upload Toggle Per Zone

| Zone | Recommended Default | Conditions to Enable |
|------|---------------------|----------------------|
| Zone 1 (Personal) | **On** acceptable for personal-productivity use | None beyond Microsoft defaults; periodic review |
| Zone 2 (Team) | **Off** until approved | Documented approval and DLP coverage in the agent's environment |
| Zone 3 (Enterprise) | **Off** (default deny) | Formal risk assessment, AI Governance Lead approval, DLP enforce mode, and Defender content scanning |

1. Toggle **File Upload** to the state determined by Step 1's approval check
2. Click **Save**
3. **Republish** the agent: Copilot Studio caches agent runtime configuration; the new toggle state may not be enforced for clients until the agent is republished

### Step 4: Configure Allowed File Types (Per-Agent Allowlist)

> **Required for every Zone 2 and Zone 3 agent with File Upload = On.** PPAC controls (Control 1.25) establish the *maximum* permitted file types for the environment; per-agent allowlists apply *additional* least-privilege restrictions.

1. In the **File Upload** section, locate **Allowed file types** (visible only when the toggle is **On**)
2. Reduce the allowlist to the minimum set required by the agent's documented purpose
   - Example: a contract-summary agent → `.pdf` only
   - Example: a financial-analysis agent → `.xlsx`, `.csv` only
3. Do not inherit the full environment allowlist by default
4. Click **Save** and republish

### Step 5: Verify File Size and Per-Conversation Limits

1. Review and document the Microsoft-defined limits applicable to your agent (per Microsoft Learn, April 2026):

    | Source | Limit |
    |---|---|
    | Maker-uploaded knowledge files | Up to **512 MB** per file |
    | Knowledge files per agent (local upload) | **500** files (GA Aug 2025) |
    | Knowledge files per agent (SharePoint/OneDrive source) | **1,000** files (GA Aug 2025) |
    | User-uploaded PDF at runtime | **<40 pages** |
    | User-uploaded TXT/CSV at runtime | **<180 KB** |
    | User-uploaded image at runtime | **15 MB** (4 MB on Direct Line) |

2. For Zone 3, document any organizational reductions to these defaults (e.g., enforced via Defender for Cloud Apps file size policies) in the risk assessment

> **Note:** Microsoft does not currently expose a per-agent setting to lower these defaults below platform values. Reductions must be enforced via complementary controls (Defender file policies, Purview DLP rules, network egress policies).

### Step 6: Verify Sensitivity Label Inheritance

1. In Copilot Studio, navigate to the agent's **Knowledge** section
2. If File Upload is **On**, upload a small test file with a sensitivity label applied at source (e.g., **Confidential**)
3. Confirm the agent surfaces the inherited label in the agent properties panel
4. Upload a second test file with a more restrictive label (e.g., **Highly Confidential**) and verify the agent inherits the **most restrictive** label
5. Capture screenshot evidence and store under `maintainers-local/tenant-evidence/1.26/` (gitignored)

> **Caveat:** Auto-labeling for SharePoint Embedded (SPE) containers used by Copilot Studio may require an explicit Purview auto-labeling policy that includes the SPE location. If labels do not flow through, see the [Troubleshooting](troubleshooting.md) playbook.

### Step 7: Verify DLP Policy Coverage (Zone 2+)

1. Open [Microsoft Purview](https://purview.microsoft.com) → **Data Loss Prevention** → **Policies**
2. Confirm a DLP policy exists that covers the **Power Platform** location and is scoped to the agent's environment
3. Confirm the policy is in **Enforce** mode (not Test or Off)
4. For Zone 3, confirm the policy includes the FSI-relevant Sensitive Information Types (US SSN, US Bank Account Number, Credit Card Number, ITIN, MNPI patterns) and configures **Block** action with override prohibited

### Step 8: Configure Defender for Cloud Apps Content Scanning (Zone 3)

> **Required for Zone 3.** PPAC and per-agent allowlists inspect declared file extensions and MIME headers; magic-byte (true content type) inspection requires Defender for Cloud Apps. See Control 1.25 portal walkthrough Step 7 for the parallel environment-level pattern; this step targets the agent's SPE container.

1. Open [Microsoft Defender XDR portal](https://security.microsoft.com) → **Cloud apps** → **Policies** → **Policy management** → **File policy**
2. Create a file policy scoped to **SharePoint Online / OneDrive for Business** that filters on the SPE container associated with the agent's environment
3. Add filter: **MIME type (true type) does not equal** the approved per-agent allowlist
4. Governance actions: **Quarantine** + Notify file owner + Notify SOC distribution list
5. Create a **High** severity alert; forward to Microsoft Sentinel
6. Save and confirm the policy is **Enabled**

### Step 9: Review SharePoint Embedded Container Configuration

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com) → **Environments** → \[Environment\]
2. Locate the **SharePoint Embedded** container details for the environment hosting the agent
3. Document the container ID and verify:
   - Access controls limit the container to authorized service principals and admins
   - A Purview retention policy is applied (Zone 2+) that meets the agent's record-retention obligations under FINRA 4511 / SEC 17a-4(f)
   - Container auditing is enabled (Zone 2+)
4. Capture the configuration as JSON evidence (see [PowerShell Setup](powershell-setup.md) for SHA-256 evidence emission)

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
| **SPE container retention policy** | Recommended | Required | Required + auditing enabled |
| **Sentinel monitoring** | Optional | Optional | Required |
| **Inventory tracking** | Recommended | Required | Required |
| **Review frequency** | Quarterly | Monthly | Weekly |
| **Exception process** | Informal | Documented | Documented with approval |

---

## Validation

After completing these steps, verify:

- [ ] Per-agent **File Upload** toggle state matches the agent's zone and approval status
- [ ] Per-agent **Allowed file types** list is reduced to the minimum required by the agent's documented purpose (Zone 2+)
- [ ] Sensitivity-label inheritance test passes (agent surfaces the most restrictive label from uploaded files)
- [ ] DLP policy in **Enforce** mode covers the agent's environment (Zone 2+)
- [ ] Defender for Cloud Apps file policy with true-MIME inspection is **Enabled** (Zone 3)
- [ ] SPE container access controls, retention policy, and auditing are configured (Zone 2+)
- [ ] Per-agent inventory updated with toggle state, approval reference, and next review date
- [ ] Screenshot evidence captured under `maintainers-local/tenant-evidence/1.26/` (gitignored — never push to the repository)

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
