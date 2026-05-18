# Portal Walkthrough: Control 2.14 — Training and Awareness Program

**Last Updated:** April 2026
**Portals:** Microsoft Teams admin center, Microsoft Entra admin center, SharePoint admin center, Microsoft 365 admin center
**Estimated Time:** 4–6 hours initial setup; ongoing curriculum maintenance

!!! warning "Implementation requires policy decisions outside the portals"
    Portal configuration alone does not satisfy FINRA Rule 3110(a)(7) or FINRA Regulatory Notice 25-07. Before configuring tooling, your firm should have approved: (1) the AI governance curriculum, (2) the role-to-training matrix, (3) the passing threshold and its rationale, (4) the retention period for training evidence, and (5) the escalation path for non-completion. This walkthrough covers the platform configuration; the program substance is the firm's responsibility.

---

## Prerequisites

- [ ] **Entra Global Admin** or **Teams Admin** for initial Viva Learning setup
- [ ] **Knowledge Admin** (Entra role) for ongoing content source management — see [docs/reference/role-catalog.md](../../../reference/role-catalog.md)
- [ ] **SharePoint Admin** if SharePoint will host custom training content
- [ ] **AI Administrator** for alignment with M365 Copilot and agent governance settings
- [ ] **Purview Compliance Admin** for retention policy on training records (see Control 2.13)
- [ ] Approved AI governance curriculum and role-to-training matrix
- [ ] Microsoft 365 E3/E5 (basic Viva Learning) or Viva Suite / Viva Learning premium license (LMS connectors, advanced reporting)

---

## Step 1 — Define Roles and Training Matrix (Off-Portal)

Document the role-to-training mapping before touching the portals. The matrix below is illustrative — your firm should adapt it.

| Audience | Required Training | Frequency | Owner |
|---|---|---|---|
| Agent Maker (Microsoft Copilot Studio / Agent Builder) | AI agent fundamentals, data governance, prompt safety, firm policy | Initial + annual + on major feature change | AI Administrator |
| Agent Approver / Reviewer | Approval criteria, supervision evidence, FINRA 3110 obligations | Initial + annual | Purview Compliance Admin |
| Agent Supervisor (FINRA-registered) | Supervision of AI-assisted activity, escalation, recordkeeping | Initial + annual + after Reg Notice updates | Compliance / Supervisor's principal |
| Platform Admin (PPAC / Tenant) | Environment governance, DLP, monitoring, incident response | Initial + quarterly delta | Power Platform Admin |
| End User | Acceptable use, data classification, confidentiality | Initial + annual | Business Manager |

Record the matrix in your governance documentation (Control 2.13) and version it.

---

## Step 2 — Assign the Knowledge Admin Role

The **Knowledge Admin** Entra role grants the minimum permissions needed to manage Viva Learning content sources without granting tenant-wide admin rights.

1. Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com) as an **Entra Privileged Role Admin** or **Entra Global Admin**.
2. Navigate to **Identity > Roles & admins > Roles & admins**.
3. Search for **Knowledge Admin** and select the role.
4. Choose **Add assignments** and assign the role to the staff who will manage Viva Learning content sources.
5. For regulated tenants, prefer **eligible** assignments via Entra PIM with a documented activation justification (Control 1.x — privileged access governance).

---

## Step 3 — Set Up Viva Learning in the Teams Admin Center

Viva Learning is administered from the Teams admin center as of 2026; the legacy path under Microsoft 365 admin center > Org settings has been deprecated.

1. Sign in to the [Microsoft Teams admin center](https://admin.teams.microsoft.com) as **Teams Admin** or **Entra Global Admin**.
2. Navigate to **Teams apps > Manage apps**, search for **Viva Learning**, and confirm the app is **Allowed**.
3. Open **Viva > Viva Learning** in the left navigation.
4. Review the **Default content sources** — Microsoft Learn, Microsoft 365 Training, and (if licensed) LinkedIn Learning. Disable any sources not approved by your firm.
5. Pin Viva Learning to the Teams app bar via a **Teams app setup policy** so the population in scope sees the app on first use.

> **Reference:** [Microsoft Learn — Set up Microsoft Viva Learning](https://learn.microsoft.com/en-us/viva/learning/set-up-viva-learning)

---

## Step 4 — Add SharePoint as a Content Source (Custom Curriculum)

Use SharePoint when your firm authors its own AI governance content (slide decks, policy PDFs, recorded walkthroughs).

1. As **SharePoint Admin**, create a SharePoint **communication site** named (for example) `AI Governance Learning`. Communication sites are recommended over team sites for read-mostly content.
2. Upload approved content. Supported types: `.docx`, `.pptx`, `.xlsx`, `.pdf`, `.mp3`, `.m4a`, `.mp4`, `.mov`, `.avi`, plus URL-linked items. The Viva Learning ingestion ceiling is approximately **1,000 files per source** on basic licensing (higher with premium).
3. Set permissions using **Microsoft 365 Groups** or **Security Groups** only — Viva Learning does not honor user-direct permissions on the source library.
4. As **Knowledge Admin**, return to **Teams admin center > Viva > Viva Learning > Content sources > SharePoint**.
5. Choose **Add SharePoint URL**, paste the site or library URL, and save.
6. Wait up to **24 hours** for the initial ingestion. Permission and content changes thereafter respect the same 24-hour refresh.

> **Reference:** [Microsoft Learn — Add SharePoint as a content source](https://learn.microsoft.com/en-us/viva/learning/configure-sharepoint-content-source)

---

## Step 5 — (Optional) Connect a Third-Party LMS

If your firm already operates an LMS, surface it in Viva Learning so completion data and content live in one experience. Premium licensing typically required.

Supported native connectors (verify against current Microsoft Learn at the time of change):

- Cornerstone OnDemand
- Saba
- SAP SuccessFactors
- Workday Learning

1. As **Knowledge Admin**, open **Teams admin center > Viva > Viva Learning > Content sources > LMS**.
2. Select **Add LMS** and choose the connector. Provide the tenant URL and the service-account credentials your LMS team supplies.
3. Allow **24–48 hours** for the initial assignment and content sync.
4. Confirm with the LMS owner that the service account is provisioned with the **least-privilege read scope** the connector requires.

> **Reference:** [Microsoft Learn — Add learning management systems for Viva Learning](https://learn.microsoft.com/en-us/viva/learning/configure-lms)

---

## Step 6 — Wire Training into Agent Lifecycle (Process, Not a Native Toggle)

There is **no native Copilot Studio or PPAC toggle** that gates agent publishing on training completion. The control is delivered through process and supporting integrations:

- **Maker enablement (Control 2.1):** Reference the required training curriculum in the maker welcome content and pre-publish checklists.
- **Approval workflow (Control 2.4 / 2.12):** In the approval Power Automate flow, add a step that looks up the requester in the LMS export (or via the LMS API) and blocks the approval task if training is incomplete or expired.
- **Periodic attestation:** Run a scheduled flow that produces an attestation list for FINRA-supervised roles and routes it to the supervising principal.

Document this process in the firm's WSPs and reference it from Control 2.12 (Supervision) and Control 2.13 (Documentation).

---

## Step 7 — Configure Retention for Training Evidence

Training completion records may be subject to FINRA 4511 / SEC 17a-4(f) recordkeeping if they evidence supervisory qualifications.

1. As **Purview Compliance Admin**, sign in to the [Microsoft Purview portal](https://purview.microsoft.com).
2. Navigate to **Solutions > Data Lifecycle Management > Policies > Retention policies**.
3. Create or extend a retention policy covering the SharePoint site and any Exchange mailbox (e.g., LMS notification mailbox) that holds training records.
4. Apply a retention period aligned to the firm's record schedule (commonly **6+ years** for FINRA-impacting records). Where SEC 17a-4(f) applies, configure **Records Management** with a label that **marks records as regulatory** to enable WORM lock.
5. Document the label, scope, and disposition review cadence in Control 2.13 evidence.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---|---|---|---|
| Training assignment | Recommended | Required for makers and approvers | Required for all roles in scope |
| Completion tracking | Optional | Enabled in LMS / Viva Learning | Enabled with periodic export to evidence store |
| Refresh cadence | Annual | Annual + on major policy change | Annual + after FINRA / SEC notice impacting AI |
| Approval-flow check | Not required | Recommended (warning) | Required (block on incomplete/expired) |
| Evidence retention | Per firm policy | 3+ years | Per firm record schedule (typically 6+ years); WORM where SEC 17a-4(f) applies |

The values above are framework defaults. Your firm's WSPs and record-retention schedule are authoritative.

---

## Validation Checklist

- [ ] Knowledge Admin role assigned (preferably PIM-eligible) to named individuals
- [ ] Viva Learning visible to the in-scope population in Teams
- [ ] SharePoint content source ingested (file count matches what was uploaded, allowing for the 1,000-file ceiling)
- [ ] LMS connector (if used) showing assignments and completions for at least one pilot user
- [ ] Approval workflow looks up training status before allowing agent publishing in Zone 3
- [ ] Retention policy or records label applied to the training evidence locations
- [ ] Role-to-training matrix and threshold rationale committed to governance documentation (Control 2.13)

---

[Back to Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
