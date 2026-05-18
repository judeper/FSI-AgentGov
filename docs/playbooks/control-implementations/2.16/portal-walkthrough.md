# Control 2.16: RAG Source Integrity Validation — Portal Walkthrough

> Portal-based configuration guidance for [Control 2.16: RAG Source Integrity Validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md).
>
> **Audience:** SharePoint Admins, Power Platform Admins, AI Administrators, and AI Governance Leads in US financial services organizations.

---

## Prerequisites

Before starting, confirm:

- **Roles:**
    - **AI Administrator** — required to add or remove Microsoft Copilot Studio knowledge sources and to manage citation settings on tenant-wide agents
    - **Power Platform Admin** — required to govern environments hosting agents and to deploy Power Automate approval flows
    - **SharePoint Admin** *or* **SharePoint Site Collection Admin** — required to enable versioning, content approval, and metadata schemas on knowledge libraries
    - **Copilot Studio Agent Author** — required to bind approved knowledge sources to a specific agent
    - **Compliance Officer** *or* **Purview Compliance Admin** — required to validate retention alignment with SEC 17a-4 / FINRA 4511 on knowledge source libraries
- **Licensing:** Copilot Studio capacity allocated to the target environment; SharePoint Online plan that supports versioning and content approval
- **Sovereign cloud:** If the tenant is GCC, GCC High, or DoD, confirm correct admin URLs (`admin.microsoft.us`, `gcchigh.copilotstudio.microsoft.us`, etc.); commercial URLs will not work — see the [PowerShell Setup](powershell-setup.md) playbook for the canonical endpoint table
- **Evidence store:** A SharePoint document library or Dataverse table designated for source-approval evidence, ideally with retention lock per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- **Source inventory baseline:** A current list of every Copilot Studio agent in scope and its declared knowledge sources

> **Implementation caveat:** Copilot Studio knowledge index refreshes are platform-driven and asynchronous. The configuration below governs **what is eligible** for indexing and **how integrity is evidenced** — not the moment of index propagation. Allow up to 24 hours after a content change for results to surface in agent responses.

---

## Overview

This walkthrough configures, in order:

1. The knowledge source inventory and approval baseline
2. SharePoint library hardening (versioning, content approval, metadata)
3. Copilot Studio knowledge source binding (per agent)
4. Citation enablement and verification
5. The Power Automate approval workflow for new sources
6. The staleness monitoring loop
7. The source-approval evidence library

---

## Part 1: Establish the Knowledge Source Inventory

The inventory is the authoritative list of every source any agent in scope is permitted to use. Without it, source approval, staleness review, and audit response are not defensible.

1. Open [Copilot Studio](https://copilotstudio.microsoft.com) (or the appropriate sovereign URL).
2. Select the in-scope environment from the environment picker.
3. For each agent, open **Knowledge** and record:
    - Source type (SharePoint, Dataverse, OneDrive, uploaded file, public website, Bing Custom Search)
    - Source URL or table name
    - Indexing scope (specific library, folder, view, or row filter)
    - Date added and the maker who added it
4. Cross-check against the **AI Administrator's** approved-sources list in your governance evidence library.
5. For every source not on the approved list, open a removal change ticket and route to the AI Governance Lead.

> **Note (April 2026):** Bing Custom Search was added as a supported Copilot Studio knowledge source type in March 2026. Treat any internet-sourced grounding as **prohibited by default** in Zone 2 / Zone 3 until Compliance Officer review confirms it meets data accuracy and provenance requirements.

---

## Part 2: Harden SharePoint Knowledge Libraries

Apply these settings to **every** SharePoint library that grounds an agent in scope.

### Enable major and minor versioning with approval gating

1. Open the library in SharePoint.
2. Select **Settings (gear)** > **Library settings** > **More library settings** > **Versioning settings**.
3. Configure:
    - **Content Approval:** *Require content approval for submitted items* → **Yes**
    - **Document Version History:** *Create major and minor (draft) versions*
    - **Major version limit:** 50 (adjust per retention policy)
    - **Minor version limit:** 10
    - **Draft Item Security:** *Only users who can approve items (and the author of the item)*
4. **OK**.

The effect: only approved **major** versions are visible to the Copilot Studio indexer. Drafts and pending-approval content cannot ground agent responses.

### Apply the FSI metadata schema

Add these site columns to each library and mark them required:

| Column | Type | Purpose |
|--------|------|---------|
| `Source Owner` | Person or Group | Accountable content owner |
| `Approval Date` | Date and Time | When the source was approved by the AI Governance Lead |
| `Next Review Date` | Date and Time | Drives staleness alerts |
| `Classification` | Choice (Public / Internal / Confidential / Restricted) | Sensitivity tier |
| `Regulatory Scope` | Choice (None / FINRA / SEC / SOX / GLBA / Multi) | Used to gate Zone 3 retention |
| `Approved For Agents` | Multi-line text | Comma-separated agent IDs eligible to use this content |

> **Filter caveat:** Copilot Studio's per-source filter conditions evaluate against SharePoint columns at index time. If `Approved For Agents` is left blank, the document is **not** eligible — fail-closed.

### Configure indexing filter conditions

1. Re-open the agent in Copilot Studio.
2. Open the SharePoint knowledge source and select **Edit**.
3. Under **Filter conditions**, add:
    - `Modified` ≥ today − *Staleness Threshold* (90 days for Zone 3, 180 days for Zone 2, 365 days for Zone 1)
    - `Approved For Agents` *contains* the current agent's identifier
4. **Save**.

---

## Part 3: Bind and Verify Citation Settings (per Agent)

For each agent in scope:

1. In Copilot Studio, open the agent → **Settings** → **Generative AI** (or **AI tab**, depending on UI version).
2. Confirm **Include source citations in responses** is **enabled**.
3. Set **Response refusal** to *Refuse if no grounded source is available* for Zone 3 agents.
4. Open **Knowledge** and confirm only sources from the approved inventory are listed.
5. Save and publish the agent.
6. Test: ask the agent a knowledge-bound question and confirm a citation appears in the response with a working link to the source document.

> **Citation behavior:** Citation surfaces vary by channel. Microsoft Teams renders citations as inline footnotes; the Microsoft 365 Copilot Chat surface renders citations as a "References" block. Embedded SDK channels may suppress citations entirely — re-test on every channel before approving for production.

---

## Part 4: Deploy the Source-Approval Power Automate Flow

Goal: a new file added to a knowledge library cannot become a major version (and therefore cannot ground an agent) without explicit AI Governance Lead approval.

1. Open [Power Automate](https://make.powerautomate.com) in the **same environment** that hosts the agent.
2. Create a new automated cloud flow.
3. Trigger: **SharePoint — When a file is created (properties only)**, scoped to the knowledge library.
4. Action: **Approvals — Start and wait for an approval** with type *Approve / Reject — Everyone must approve*; assign to the AI Governance Lead group.
5. Condition: if `Outcome` = `Approve`, run **SharePoint — Set content approval status** = *Approved*; else = *Rejected*.
6. Action: **SharePoint — Update file properties** to stamp `Approval Date`, `Source Owner`, and `Next Review Date`.
7. Save and run a test.

> **Mutation safety note:** Approval flows are tenant-state mutations. Test in a non-production environment first; capture the run history JSON as evidence of design effectiveness.

---

## Part 5: Configure the Staleness Monitoring Loop

1. Create a second flow, scheduled daily.
2. Action: **SharePoint — Get items** with filter `Next Review Date lt @{utcNow()}`.
3. For each result, send a Teams message to the `Source Owner` and a digest to the AI Governance Lead.
4. Optional: write each stale item to a Dataverse table for trending and for examiner-ready evidence.

| Zone | Staleness threshold | Alert cadence |
|------|---------------------|---------------|
| Zone 1 (Personal) | 365 days | Owner only, monthly |
| Zone 2 (Team) | 180 days | Owner + AI Governance Lead, weekly |
| Zone 3 (Enterprise) | 90 days; 30 days for regulatory content | Owner + AI Governance Lead + Compliance Officer, daily |

---

## Part 6: Stand Up the Source-Approval Evidence Library

Create a SharePoint library named `FSI-RAG-Source-Approvals` with retention lock per Control 1.7. For every approved source, store:

- The signed source-approval form (PDF)
- The owning agent inventory entry (CSV)
- The library hardening evidence (JSON from the [PowerShell Setup](powershell-setup.md) read-only audit script, with SHA-256 manifest)
- The Power Automate flow run history export covering the most recent 12 months

> **Automation companion:** The [RAG Source Validator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/rag-source-validator) in FSI-AgentGov-Solutions automates SHA-256 hashing, schema-drift detection, and freshness monitoring across SharePoint, Dataverse, and Azure Blob sources, and writes its output to this library.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|--------------------|
| Knowledge source approval | Informal, owner-attested | Documented approval per source | Power Automate approval flow + signed form |
| Content versioning | Optional | Major + minor enabled | Required, content approval enforced |
| Staleness threshold | 365 days | 180 days | 90 days; 30 days for regulatory content |
| Citation display | Optional | Enabled | Required; refusal-if-ungrounded enabled |
| Source inventory review | Annual, owner-attested | Quarterly, AI Governance Lead | Quarterly + on-demand for examiner requests |
| External / internet sources | Allowed with disclosure | Restricted, case-by-case | Prohibited unless Compliance Officer signs off |
| Bing Custom Search | Allowed with disclosure | Restricted | Prohibited |
| Evidence retention | None required | 12 months | 7 years (SEC 17a-4 / FINRA 4511 alignment) |

---

## FSI Example Configuration

```yaml
Agent: Client Portfolio Advisor
Environment: FSI-Wealth-Prod (Managed)
Zone: 3 (Enterprise Managed)

Knowledge Sources (approved):
  - Source: SharePoint - Investment Research Library
    URL: https://contoso.sharepoint.com/sites/research/PublishedResearch
    Scope: Approved Documents library, major versions only
    Filter: Approved For Agents contains "client-portfolio-advisor"
    Owner: Research Team Lead
    Approval Flow: AI-Governance-Lead-Approval
    Review Frequency: 90 days; 30 days for regulatory commentary

  - Source: Dataverse - Client FAQs
    Table: fsi_clientfaqs
    Scope: statuscode eq Published AND approved_by_compliance eq true
    Owner: Client Services Lead
    Review Frequency: 90 days

Prohibited Sources:
  - Public websites (general)
  - Bing Custom Search
  - Personal OneDrive
  - Any SharePoint site not in the approved-sources register
  - Third-party knowledge bases without an executed data-processing agreement

Citation Policy:
  - Citations: Required, displayed inline
  - Refusal: Refuse if no grounded source is available
```

---

## Validation

After completing these steps, verify:

- [ ] Knowledge source inventory exists and matches what is bound in every agent
- [ ] Versioning + content approval enabled on every source library
- [ ] FSI metadata schema applied; `Approved For Agents` populated for every grounded document
- [ ] Filter conditions configured per agent
- [ ] Power Automate approval flow runs end-to-end on a test upload
- [ ] Staleness flow sends a test alert
- [ ] Citations render correctly on every channel the agent is published to
- [ ] Source-approval evidence library populated and retention-locked

---

[Back to Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
