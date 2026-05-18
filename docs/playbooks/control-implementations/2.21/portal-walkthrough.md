# Portal Walkthrough: Control 2.21 — AI Marketing Claims and Substantiation

**Last Updated:** April 2026
**Portals:** SharePoint admin center, SharePoint site, Power Automate, Microsoft Purview portal
**Estimated Time:** 2–3 hours initial setup
**Audience:** SharePoint Admin and Power Platform Admin partnering with the Compliance Officer

---

## Overview

This playbook walks through configuration of general-purpose Microsoft 365 surfaces (SharePoint, Power Automate, and optionally Purview retention) to support the AI marketing claims governance process. Microsoft does not ship a SEC- or FINRA-specific marketing-review product; the configuration below is a documented pattern that helps support compliance with SEC Marketing Rule 206(4)-1, FINRA Rule 2210, and FINRA Regulatory Notice 24-09 when combined with firm policy and human supervisory review.

!!! warning "Process control, not a compliance product"
    The portal steps in this playbook do not, by themselves, satisfy any regulatory obligation. They configure the system of record and workflow that the firm's compliance and legal teams use to review and substantiate AI claims. Pairing this configuration with documented Written Supervisory Procedures (WSPs) is required.

---

## Prerequisites

| Item | Details |
|---|---|
| Roles | **SharePoint Admin** (or Site Collection Admin on the target site) for list/library/retention setup; **Power Platform Admin** or maker rights in a managed Power Platform environment for the Power Automate flows |
| Approvers identified | Named **Compliance Officer**, **AI Governance Lead**, and Legal reviewer (functional roles) |
| Site target | A governed SharePoint communication or team site (recommend a dedicated "AI Governance" site) |
| Retention policy decision | Decide whether claims and substantiation evidence will be governed by an existing FINRA 4511 / SEC 17a-4 retention label or by a label created in this playbook |
| WSP coverage | Marketing-claims procedure exists or is in draft and references this workflow |

---

## Step 1 — Provision the AI Governance site (if it does not exist)

1. Sign in to the **SharePoint admin center** (`https://<tenant>-admin.sharepoint.com`) as **SharePoint Admin**.
2. Select **Sites** → **Active sites** → **+ Create**.
3. Choose **Communication site** (or use an existing governed team site if one exists).
4. Set:
    - **Site name:** `AI Governance`
    - **Primary admin:** Compliance Officer (or governance shared mailbox)
    - **Sensitivity label:** Apply the firm's "Internal — Compliance" or equivalent label
5. After creation, open **Site permissions** and grant the Compliance and AI Governance teams **Edit**, marketing submitters **Contribute**, and all other users **Read** (or remove default broad access if your tenant uses that pattern).

!!! tip "Use an existing site if you already have one"
    Many firms already operate a centralized "Compliance" or "Governance" site. Reusing it avoids fragmenting evidence and simplifies retention. If you reuse an existing site, skip site creation and start at Step 2.

---

## Step 2 — Create the AI Marketing Claims Inventory list

1. Open the AI Governance site → **+ New** → **List** → **Blank list**.
2. Name: **AI Marketing Claims Inventory**. Description: "System of record for AI-related marketing claim submissions, reviews, approvals, and quarterly re-reviews per Control 2.21."
3. Add the following columns (use **+ Add column** in list view):

| Display Name | Internal Name | Type | Notes |
|---|---|---|---|
| Claim Text | `ClaimText` | Multiple lines (plain text) | Required; the exact wording proposed for publication |
| Claim Category | `ClaimCategory` | Choice | Performance, Capability, Comparative, Predictive, Efficiency |
| Agent / Product | `AgentProduct` | Single line | Name of agent or product being marketed |
| Target Channel | `TargetChannel` | Choice | Website, Email, Social Media, Sales Collateral, Press Release, Conference Material, Multiple |
| Governance Zone | `GovernanceZone` | Choice | Zone 1 — Personal, Zone 2 — Team, Zone 3 — Enterprise |
| FINRA 2210 Communication Type | `FinraCommType` | Choice | Correspondence, Retail Communication, Institutional Communication, N/A |
| Substantiation File | `SubstantiationFile` | Hyperlink | URL to the evidence document (in the substantiation library) |
| Status | `ClaimStatus` | Choice | Draft, Under Review, Approved, Rejected, Withdrawn, Retired |
| Submitted By | `SubmittedBy` | Person | Defaults to current user on submission |
| Submission Date | `SubmissionDate` | Date and time | |
| Compliance Reviewer | `ComplianceReviewer` | Person | Compliance Officer who approved |
| Review Date | `ReviewDate` | Date and time | |
| Approval Date | `ApprovalDate` | Date and time | |
| Next Review Date | `NextReviewDate` | Date and time | Calculated by the Power Automate flow as Approval Date + 90 days |
| Review Comments | `ReviewComments` | Multiple lines | Reviewer notes, including basis for approval or rejection |

4. Open **List settings** → **Versioning settings** and set:
    - **Item version history:** Create a version each time you edit an item — **Yes**
    - **Major versions to retain:** 50 (or per firm policy)
    - **Require content approval:** No (workflow handles approval)
5. Under **Advanced settings**, set **Read access** to "Read all items" and **Create and edit access** to "Create items and edit items that were created by the user" so submitters cannot edit each other's claims.

---

## Step 3 — Create the AI Claims Substantiation document library

1. From the same site, **+ New** → **Document library** → name **AI Claims Substantiation**.
2. Open **Library settings**:
    - **Versioning:** Create major versions; require check-out.
    - **Require documents to be checked out:** Yes (preserves a clean audit trail).
3. Create top-level folders matching the claim categories:
    - `Performance Claims`
    - `Capability Claims`
    - `Comparative Claims`
    - `Predictive Claims`
    - `Efficiency Claims`
4. Add metadata columns: **Linked Claim ID** (Number), **Evidence Type** (Choice: Test Report, Backtest, Vendor Documentation, Internal Analysis, Customer Study, Other), and **Source Owner** (Person).

---

## Step 4 — Apply a retention label (Purview)

The firm's retention obligations under FINRA Rule 4511 and SEC Rule 17a-4 may require that marketing materials and supporting books and records be retained for a defined period (commonly three to six years for member firms; longer for some advisers). Apply a retention label appropriate to your obligations.

1. Sign in to the **Microsoft Purview portal** (`https://purview.microsoft.com`) as **Purview Compliance Admin** or **Purview Records Manager**.
2. Navigate to **Solutions** → **Records management** → **File plan** → **+ Create label**.
3. Configure:
    - **Name:** `AI Marketing Claim — Books and Records`
    - **Mark items as a record:** Yes (recommended for FINRA / SEC books-and-records scope)
    - **Retention period:** Set to the firm's documented retention period for marketing communications (verify with Compliance — do not assume a specific number of years)
    - **Trigger:** Based on when items were created
    - **At end of retention:** Trigger a disposition review
4. Publish a **Retention label policy** that targets the **AI Claims Substantiation** library and the **AI Marketing Claims Inventory** list.
5. Optionally, in **Library settings** of the substantiation library, set a **default retention label** so new uploads inherit the label automatically.

!!! warning "Confirm retention period with Compliance"
    Retention periods are firm- and registration-specific. SEC-registered investment advisers, FINRA member broker-dealers, dual-registrants, and futures-side firms (CFTC 1.31) may have different obligations. Do not hard-code a number of years without explicit Compliance confirmation. The previous version of this playbook used "7 years" as an example — treat that as illustrative only.

---

## Step 5 — Build the pre-publication review flow (Power Automate)

1. Open **Power Automate** (`https://make.powerautomate.com`) and select the managed environment that hosts your governance flows (created under Control 2.1 / 2.2).
2. **+ Create** → **Automated cloud flow**.
3. Trigger: **SharePoint — When an item is created or modified**, pointing to the AI Governance site and the **AI Marketing Claims Inventory** list.
4. Add a **Condition** at the top: continue only when `Status` equals `Under Review` (this prevents the flow from running on Draft saves or post-approval edits).
5. Add **Start and wait for an approval**:
    - Approval type: **Approve / Reject — First to respond**
    - Assigned to: dynamic value of `Compliance Reviewer` if set, otherwise the Compliance Officer group mailbox
    - Title: `[AI Claim Review] {Title} — {ClaimCategory}`
    - Details: include the dynamic `ClaimText`, `AgentProduct`, `Target Channel`, `Governance Zone`, and a link to the substantiation file
6. Branch on the approval **Outcome**:
    - **Reject** → update the item: `Status = Rejected`, set `Review Date`, write the reject comments to `Review Comments`, send rejection email to submitter, terminate.
    - **Approve** → continue to step 7.
7. Add a second **Start and wait for an approval** assigned to the **AI Governance Lead** for technical accuracy validation. Same reject/approve branching.
8. Add a **Condition**: if `Governance Zone` equals `Zone 3 — Enterprise`, add a third approval assigned to **Legal Counsel**.
9. After all required approvals succeed, update the list item:
    - `Status = Approved`
    - `Approval Date = utcNow()`
    - `Next Review Date = addDays(utcNow(), 90)` (use the Power Automate expression `addDays(utcNow(),90)`)
    - `Review Comments = `concatenated approval notes
10. Send a confirmation email to the submitter and the reviewers.
11. Save and **Turn on** the flow. Test with a Draft item moved to Under Review.

---

## Step 6 — Build the quarterly review reminder flow

1. **+ Create** → **Scheduled cloud flow**.
2. Recurrence: **Weekly**, Monday, 09:00 in the firm's primary business time zone.
3. **SharePoint — Get items**:
    - Site Address: AI Governance site
    - List: AI Marketing Claims Inventory
    - Filter Query (OData): `ClaimStatus eq 'Approved' and NextReviewDate le '@{addDays(utcNow(),14)}'`
4. **Apply to each** returned item:
    - **Send an email (V2)** to `Compliance Reviewer` with the claim text, original approval date, substantiation link, and a deep link to the list item.
    - Optionally, post a card to a Compliance Microsoft Teams channel using **Post adaptive card in a chat or channel**.
5. Save and **Turn on**. Trigger a manual run to confirm filter and recipients.

---

## Step 7 — Restrict who can approve

In **List settings** → **Permissions for this list**:

1. **Stop inheriting permissions** (only if necessary; usually inherited site permissions are sufficient).
2. Add a SharePoint group `AI Claims Approvers` containing only the named Compliance Officer(s), AI Governance Lead, and Legal reviewer(s). Grant **Edit**.
3. Confirm marketing submitters have **Contribute** but cannot edit other users' items (set in Step 2).
4. Document the group membership in the WSP and in Control 2.8 (Access Control and Segregation of Duties) scope, if applicable.

---

## Configuration by Governance Level

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---|---|---|---|
| Claims Inventory | Not required | Recommended | **Required** |
| Pre-Publication Review | Not required | Compliance review | Compliance + AI Governance + Legal |
| Substantiation File | Not required | Recommended | **Required** |
| Quarterly Re-Review | Not required | Optional | **Required** |
| FINRA 2210 classification recorded | Not required | Recommended | **Required** |
| Retention label applied | N/A | Per firm policy | **Per firm policy (records label)** |

---

## Validation Checklist

- [ ] AI Governance site exists with appropriate permissions
- [ ] AI Marketing Claims Inventory list created with all 15 columns
- [ ] AI Claims Substantiation library created with category folders and metadata
- [ ] Retention label applied to both list and library (or in-scope of an existing label policy)
- [ ] Pre-publication approval flow turned on and successfully tested end-to-end with a sample claim
- [ ] Quarterly review reminder flow turned on and produced a test reminder
- [ ] AI Claims Approvers SharePoint group created and populated
- [ ] WSP / governance procedure references the workflow and identifies named approvers

---

## Related Controls

- [2.19 — Customer AI Disclosure and Transparency](../../../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md)
- [2.5 — Testing, Validation, and Quality Assurance](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md)
- [2.6 — Model Risk Management Alignment with OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md)

---

[Back to Control 2.21](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
