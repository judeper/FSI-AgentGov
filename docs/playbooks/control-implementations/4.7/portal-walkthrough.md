# Control 4.7 — Portal Walkthrough: Microsoft 365 Copilot Data Governance

**Control ID:** 4.7
**Pillar:** SharePoint and OneDrive Governance
**Playbook Type:** Portal Walkthrough (Admin Center UI)
**Last UI Verified:** April 2026
**Estimated Time:** 8–12 hours across the three-stage rollout (Report-only → Pilot → Broad)
**Prerequisites:** Pre-rollout gates PRE-01 through PRE-07 (see §3) completed and evidenced

---

!!! danger "READ FIRST — Scope and routing"
    This walkthrough covers the **portal-driven configuration** of Microsoft 365 Copilot data governance using the Microsoft 365 admin center, the Microsoft Purview portal, and the SharePoint admin center. It is the single source of truth for click-paths, screenshot anchors, and the staged rollout sequence.

    Use the sibling playbooks for adjacent work:

    | If you need… | Use this sibling playbook |
    |---|---|
    | Bulk configuration, idempotent baselines, evidence export | [PowerShell Setup](powershell-setup.md) |
    | Pre-flight readiness, post-change validation, failure pattern triage | [Verification & Testing](verification-testing.md) |
    | Symptom-to-fix decision tree, license/permission gotchas | [Troubleshooting](troubleshooting.md) |
    | Live-incident response (oversharing, leaked secret, prompt injection) | [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) |
    | The "why" — regulatory mapping, zone tiering, related controls | [Control 4.7 specification](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) |

!!! warning "Hedged-language reminder"
    Configuring these settings **supports compliance with** FINRA 4511, SEC 17a-4, GLBA 501(b), and Federal Reserve SR 26-2 (formerly SR 11-7). It does **not** by itself guarantee compliance. Effectiveness depends on label coverage, DLP policy quality, identity hygiene, training, and your firm's interpretation of the rules. Engage Compliance, Legal, and Information Security before broad rollout.

---

## §0. Coverage boundary and portal-vs-PowerShell decision matrix

This section sets the boundary of what this walkthrough covers and where to switch to the sibling automation playbook.

### 0.1 What this playbook covers

- Microsoft 365 Copilot tenant settings (admin center → Settings → Copilot)
- Microsoft Purview Sensitivity Labels for Copilot interactions and generated content
- Data Loss Prevention (DLP) for Microsoft 365 Copilot — both prompt-side and response-side rules
- Restricted SharePoint Search (RSS) and Restricted Content Discoverability (RCD) configuration
- Endpoint DLP rules that govern Copilot in Microsoft Edge
- Pages (in OneDrive) and Notebooks (in Loop containers) protection scope
- Data residency confirmation, EU Data Boundary verification, and the Anthropic exception
- Multi-Geo behavior for tenants spanning multiple data regions
- Sovereign cloud parity (Commercial / GCC / GCC High / DoD) — current state and gaps

### 0.2 What this playbook does NOT cover

- M365 Copilot license assignment (covered in Control 2.1 and Control 2.4)
- SharePoint and OneDrive sharing defaults (Controls 4.1, 4.2)
- Conditional Access policies gating Copilot access (Control 1.7)
- Audit log retention and search (Controls 3.4, 3.8)
- Connector governance for non-Microsoft data sources (Control 1.21)
- Agent and Copilot Studio governance (Control 2.10 and the Copilot Studio playbook set)

### 0.3 Portal-vs-PowerShell decision matrix

Use this table to decide whether to stay in this portal walkthrough or switch to [PowerShell Setup](powershell-setup.md). The criterion is **scale, repeatability, and evidence**.

| Task | Portal (this playbook) | PowerShell (sibling) | Reason for split |
|---|:---:|:---:|---|
| Initial pilot config (≤ 50 users) | ✅ Primary | Optional | Faster click-through; screenshot evidence |
| Tenant-wide rollout (> 50 users) | ⚠️ Reference only | ✅ Primary | Idempotency + change-record evidence |
| Restricted SharePoint Search (RSS) initial enablement | ✅ Primary | ✅ Either | Tenant-wide toggle; evidenced via either path |
| Restricted Content Discoverability (RCD) site list | ⚠️ ≤ 25 sites | ✅ > 25 sites | Portal is per-site; PS handles bulk |
| Sensitivity Labels for Copilot — label scope edits | ✅ Primary | ⚠️ Partial | Label authoring is portal-only; scope toggles via PS |
| DLP for Microsoft 365 Copilot — initial policy | ✅ Primary | ✅ Either | Prompt-side rules require portal builder; export via PS |
| DLP — bulk rule clone across pillars | ❌ | ✅ Primary | Portal does not support clone-across-policy |
| Endpoint DLP rules touching Copilot in Edge | ✅ Primary | ⚠️ Partial | Endpoint DLP UI is mature; PS for export only |
| Evidence pack generation (the 19 artifacts in §12) | ❌ | ✅ Primary | Hash + timestamp requirements need scripted capture |
| Multi-Geo data residency verification | ⚠️ Read-only view | ✅ Primary | Geo binding requires Graph + EXO calls |
| Audit log query for Copilot activities | ❌ | ✅ Primary | Beyond the 30-day portal cap; needs unified audit log |
| Periodic re-attestation (quarterly) | ❌ | ✅ Primary | Schedule + diff + sign-off requires automation |

**Rule of thumb:** Portal for initial **set-up and review**. PowerShell for **scale, evidence, and recurrence**. If you find yourself clicking the same blade more than three times, switch to the sibling.

---

## §1. Surface inventory, propagation latency, and the Everyone-Except-External-Users (EEEU) callout

Microsoft 365 Copilot grounds its responses in tenant data accessible to the prompting user. Governance must therefore consider **every Copilot surface**, the **propagation latency** of each governance change, and the historical **EEEU oversharing pattern** that is the most common root cause of Copilot data exposure incidents in financial services.

### 1.1 Copilot surface inventory (April 2026)

| Surface | Hosting | Governance scope | Notes |
|---|---|---|---|
| Microsoft 365 Copilot Chat (work) | Service-side, Substrate | Tenant-bounded; honors RSS/RCD/DLP for M365 Copilot | Default conversational surface |
| Copilot in Word / Excel / PowerPoint / Outlook / OneNote | Client + service | Honors sensitivity labels at file level; DLP on response generation | Per-app behavior varies |
| Copilot in Teams (chat / meeting recap) | Service-side | Inherits Teams/SharePoint permissions | Recap honors meeting policy |
| Copilot in Loop | Loop containers | Container-scoped permissions | Notebooks created here |
| Copilot in OneDrive | OneDrive | Per-user scope; Pages live here | Pages have separate retention |
| Copilot in Edge (web grounding) | Edge browser | Endpoint DLP applies | **Edge-only** for Copilot Endpoint DLP |
| Copilot Pages | OneDrive | Pages are stored as `.fluid` artifacts in OneDrive | Treat as OneDrive content |
| Copilot Notebooks | Loop containers | Notebook = Loop container with Copilot grounding | Container permissions = grounding scope |
| Microsoft 365 Copilot Search (org search) | Substrate | Honors RSS, RCD, item-level permissions | RSS gates the entire surface when enabled |

### 1.2 Propagation latency table (April 2026 — verify in your tenant during pilot)

| Change | Typical propagation | Worst case observed | Validation step |
|---|---|---|---|
| Tenant Copilot toggle (on/off) | < 15 minutes | 1 hour | Test prompt as a freshly-licensed user |
| Sensitivity label policy publish | 1–24 hours | 48 hours | New session in Word; label picker shows new labels |
| Sensitivity label scope change (file/email vs. groups+sites) | 2–24 hours | 48 hours | Re-attempt blocked operation as test user |
| DLP for M365 Copilot policy publish | 1 hour | 24 hours | Issue a prompt designed to trigger the rule |
| RSS enablement | < 1 hour | 4 hours | Run an org-wide search as a non-admin |
| RCD per-site flag | < 1 hour | 4 hours | Confirm site no longer appears in tenant search |
| Endpoint DLP policy update | 1 hour | 24 hours | Edge restart on endpoint; trigger test rule |
| Conditional Access policy targeting Copilot | < 5 minutes | 30 minutes | Sign-out / sign-in cycle |
| Multi-Geo geo binding change | 24 hours | 7 days | Confirm via Graph user `preferredDataLocation` |

!!! warning "Pilot soak time"
    Plan for **at least 72 hours of soak time** between policy publish and pilot validation. Do not declare a pilot stage successful on a same-day test — sensitivity-label propagation in particular has been observed to take 48 hours in heavily federated tenants.

### 1.3 The Everyone-Except-External-Users (EEEU) callout

The single most common root cause of Microsoft 365 Copilot oversharing in US financial services tenants is the historical **Everyone Except External Users (EEEU)** group being applied to SharePoint sites, OneDrive folders, and Microsoft 365 Groups that were never intended to be tenant-readable.

**Why it matters for Copilot:** EEEU effectively grants every internal user read access to the resource. Copilot grounding respects ACLs. Therefore, **any document an internal user could open with EEEU permission is grounding-eligible for that user's Copilot prompts**. A 2,000-person FSI firm with a poorly-permissioned site containing draft Suitability/KYC working papers can have those documents surface in a junior advisor's Copilot prompt.

**Pre-rollout requirement:** Run the Microsoft 365 Copilot **Data Access Governance (DAG) report** before enabling Copilot for any new pilot wave. The DAG report (Microsoft 365 admin center → Reports → Copilot → Data access governance) flags sites with EEEU permissions and high item counts. Treat any flagged site as a **PRE-ROLLOUT BLOCKER** until remediated by the site owner or moved to RCD.

**Hedged-language note:** Running the DAG report **supports compliance with** FINRA 4511 (record-keeping integrity) and GLBA 501(b) (safeguards against unauthorized access). It does not by itself remediate the underlying permissions — that remains the site owner's responsibility under your data-ownership operating model (Control 2.1).

---

## §2. Sovereign cloud parity matrix (April 2026)

Microsoft 365 Copilot availability and feature parity differs across Microsoft sovereign cloud offerings. This matrix reflects the state as of April 2026. **Verify against the Microsoft 365 roadmap and your contracted service descriptions before relying on this for procurement decisions.**

| Capability | Commercial | GCC | GCC High | DoD |
|---|:---:|:---:|:---:|:---:|
| Microsoft 365 Copilot Chat (work) | ✅ GA | ✅ GA | ⚠️ Limited preview | ❌ Not available |
| Copilot in Word/Excel/PowerPoint/Outlook | ✅ GA | ✅ GA | ⚠️ Limited preview | ❌ Not available |
| Copilot in Teams | ✅ GA | ✅ GA | ⚠️ Limited preview | ❌ Not available |
| Sensitivity Labels for Copilot | ✅ GA | ✅ GA | ⚠️ Preview | ❌ |
| DLP for Microsoft 365 Copilot | ✅ GA | ✅ GA | ⚠️ Preview | ❌ |
| Restricted SharePoint Search (RSS) | ✅ GA | ✅ GA | ✅ GA | N/A |
| Restricted Content Discoverability (RCD) | ✅ GA | ✅ GA | ⚠️ Preview | N/A |
| Endpoint DLP for Copilot in Edge | ✅ GA | ✅ GA | ⚠️ Preview | ❌ |
| Pages (OneDrive-backed) | ✅ GA | ✅ GA | ❌ | ❌ |
| Notebooks (Loop containers) | ✅ GA | ⚠️ Preview | ❌ | ❌ |
| EU Data Boundary (EUDB) | ✅ GA (EU tenants) | N/A | N/A | N/A |
| Anthropic models in Copilot | ✅ Opt-in (Commercial only) | ❌ | ❌ | ❌ |

### 2.1 Anthropic in Copilot — sovereign cloud reality

As of January 7, 2026, Microsoft enabled Anthropic models (Claude family) as an **opt-in** option for Microsoft 365 Copilot in Commercial cloud only. Key facts for FSI governance:

- **Not available in GCC, GCC High, or DoD** — sovereign cloud customers cannot opt in.
- **Not in the EU Data Boundary** — Anthropic processing occurs outside EUDB. EU tenants that opt in lose EUDB protection for Anthropic-routed prompts.
- **Tenant-level opt-in, not user-level** — once enabled, eligible users can route prompts to Anthropic. There is no per-user gating in the admin UI as of April 2026.
- **No additional DPA terms beyond the Microsoft Online Services DPA** — Microsoft's processing terms govern; verify with Legal whether your firm requires a supplemental Anthropic-specific risk assessment.
- **Audit-log enrichment is partial** — model selection appears in audit events but downstream telemetry parity with Azure OpenAI Service is limited as of April 2026.

**FSI recommendation:** Default to **opt-out** for regulated personas (RIAs, broker-dealers, fund accounting, treasury). Permit Anthropic opt-in only for narrowly-scoped personas with explicit Compliance sign-off. Document the decision in the Risk Acceptance log.

### 2.2 Operational implication for multi-cloud firms

Firms operating across Commercial and GCC High (a common pattern for broker-dealer subsidiaries with US Government clients):

- **Cannot achieve identical Copilot capability across both tenants** — feature parity is not on the GCC High roadmap with parity timing as of April 2026.
- **Should design two distinct governance baselines** — one for Commercial, one for GCC High — rather than seeking a "lowest common denominator" that throttles Commercial productivity.
- **Should track GCC High feature releases monthly** via the Microsoft 365 admin center Message Center and the Microsoft 365 government roadmap.

---

## §3. Pre-rollout gates PRE-01 through PRE-07

These seven gates must be evidenced as **Met** before stage 1 (Report-only) of the rollout in §4. Each gate has a **Why**, a **Portal click-path or check**, and an **Evidence artifact**. The evidence artifacts feed the §12 evidence pack.

### PRE-01: Tenant license posture confirmed

- **Why:** Microsoft 365 Copilot requires per-user licensing. Misconfigured assignment is the #1 cause of "Copilot not appearing for some users" tickets and undermines audit completeness.
- **Check:** Microsoft 365 admin center → Billing → Licenses → confirm Microsoft 365 Copilot SKU count matches procurement record. Cross-reference against Active Users report.
- **Evidence artifact:** `pre-01-license-posture.json` — output of `Get-MgSubscribedSku` filtered to Copilot SKUs, with assignment count.
- **Pass criterion:** License count ≥ planned pilot population, with ≥ 5% headroom for incremental adds.

### PRE-02: AI Administrator and Purview Data Security AI Admin roles assigned

- **Why:** Operational governance requires Role-Based Access Control. Avoid using Global Admin for routine Copilot policy changes — it leaves an inappropriate audit trail and violates least-privilege under Fed SR 26-2 (formerly SR 11-7) model risk principles.
- **Check:** Microsoft Entra admin center → Roles & admins → search "AI Administrator" and "Purview Data Security AI Admin" → confirm at least two assignees per role (primary + backup).
- **Evidence artifact:** `pre-02-role-assignments.json` — Graph PIM/Roles export for both roles.
- **Pass criterion:** ≥ 2 active assignees per role; no permanent Global Admin assignments for routine Copilot operations.

### PRE-03: Sensitivity label taxonomy published and adopted

- **Why:** DLP for Microsoft 365 Copilot, Sensitivity Labels for Copilot, and label-based grounding restrictions all assume a published, adopted label taxonomy. Without it, you cannot enforce label-based controls.
- **Check:** Microsoft Purview portal → Information Protection → Labels → confirm at least one label is published in a label policy with scope including the pilot user group. Confirm adoption rate ≥ 80% of recently-modified documents in pilot users' OneDrive (use Activity Explorer).
- **Evidence artifact:** `pre-03-label-taxonomy.json` — labels, label policies, and pilot adoption rate.
- **Pass criterion:** Taxonomy includes at minimum: Public, Internal, Confidential, Highly Confidential. ≥ 80% adoption in pilot population's recent activity.

### PRE-04: Audit log ingestion and retention verified

- **Why:** SEC 17a-4 and FINRA 4511 require record retention. Copilot audit events must flow to your audit log retention pipeline (Sentinel, third-party SIEM, or M365 long-term retention) before you enable Copilot for production users — otherwise activity from the gap period is unrecoverable.
- **Check:** Microsoft Purview portal → Audit → Search → run a query for `RecordType = CopilotInteraction` over the past 7 days. Confirm results return. Confirm your audit log retention policy (Audit Premium or third-party export) covers the WORM-equivalent period required by your firm's record retention schedule.
- **Evidence artifact:** `pre-04-audit-ingestion.json` — sample of 10 CopilotInteraction events plus retention policy export.
- **Pass criterion:** Retention ≥ 7 years for Copilot interaction events (FINRA 4511 baseline) or your firm's longer schedule.

### PRE-05: Restricted Content Discoverability prerequisite — at least one Copilot license assigned

- **Why:** Restricted Content Discoverability (RCD) is a tenant feature that **only activates** once at least one Microsoft 365 Copilot license is assigned in the tenant. Attempting to flag a site for RCD before a Copilot license exists silently fails — the flag appears set but is not enforced.
- **Check:** Microsoft 365 admin center → Active users → filter "Microsoft 365 Copilot" → confirm ≥ 1 user holds the license. If not, assign to the first pilot user **before** attempting any RCD work.
- **Evidence artifact:** `pre-05-copilot-license-floor.json` — Graph user assignment record for the first Copilot-licensed user.
- **Pass criterion:** ≥ 1 Copilot license assigned and active.

### PRE-06: Data Access Governance (DAG) baseline captured

- **Why:** §1.3 (EEEU). The DAG report identifies oversharing risks before Copilot grounding amplifies them. Capture a baseline now so you can demonstrate remediation progress over time.
- **Check:** Microsoft 365 admin center → Reports → Copilot → Data access governance → run "Sites with shared content" and "Sites with sensitive content" reports.
- **Evidence artifact:** `pre-06-dag-baseline.csv` — both DAG report exports, timestamped.
- **Pass criterion:** Baseline captured. Sites flagged with EEEU + high item count have either (a) been remediated, (b) been moved to RCD, or (c) been formally accepted on the Risk Acceptance log with a remediation deadline.

### PRE-07: Communication and training plan signed off

- **Why:** Fed SR 26-2 (formerly SR 11-7) model risk management requires user training proportionate to the model's intended use. FINRA Notice 24-09 and the FINRA 25-07 series specifically reference workforce competence with AI tools as a supervisory expectation.
- **Check:** Compliance and HR have signed off on the training curriculum, the acceptable-use policy delta, and the user communication plan (announcement, FAQ, support channel).
- **Evidence artifact:** `pre-07-training-signoff.pdf` — signed sign-off cover sheet plus curriculum table of contents.
- **Pass criterion:** Sign-offs from Compliance and HR on file. Training delivered to pilot population before Stage 2.

---

## §4. Three-stage rollout — Report-only → Pilot → Broad

This rollout sequence is mandatory for Zone 2 and Zone 3 deployments under Control 4.7. Zone 1 (personal productivity) may compress Stages 1 and 2 with documented Compliance acknowledgment.

### Stage 1 — Report-only (Weeks 1–2)

**Goal:** Generate signal without enforcement. Surface what *would* be blocked without disrupting users.

**Steps:**

1. Microsoft Purview portal → Data Loss Prevention → Policies → **+ Create policy** → Custom → name `FSI-Copilot-DLP-ReportOnly`.
2. Locations → toggle **Microsoft 365 Copilot** ON. Toggle all other locations OFF for now (we are isolating the Copilot signal).
3. Create at least three rules covering your firm's top-three sensitive data classes (e.g., MNPI, SSN, PCI). For each rule:
    - Conditions: Sensitive Information Type matches (use your firm's SITs from Control 1.13) **OR** sensitivity label is "Confidential" or above.
    - Actions: **Audit only**. Do NOT enable block, restrict, or notify actions in Stage 1.
4. Policy mode → **Run the policy in test mode without notifications**. Confirm. Save.
5. Wait 72 hours for soak. Then export Activity Explorer events for the policy and review with Compliance.

**Stage 1 exit criteria:**

- ≥ 72 hours of telemetry collected.
- At least 10 distinct policy hits reviewed by Compliance (or formal "no hits — population too small" sign-off).
- False-positive rate < 30% (otherwise rule tuning required before Stage 2).

### Stage 2 — Pilot (Weeks 3–6)

**Goal:** Move pilot population to enforcement. Validate user experience and operational runbooks.

**Steps:**

1. Identify pilot population — typically 25–100 users spanning ≥ 2 business functions and ≥ 1 regulated function (e.g., one trading desk + one back-office team).
2. Microsoft Purview portal → DLP → Policies → open `FSI-Copilot-DLP-ReportOnly` → **Edit policy**.
3. Rename to `FSI-Copilot-DLP-Pilot`.
4. Scope → Restrict to pilot user group (must be a security group or M365 group, not a distribution list).
5. For each rule, change Action from Audit-only to **Block with override** for sensitivity-label rules and **Block** (no override) for SSN/PCI rules.
6. User notifications → ON. Use the firm-approved notification text (see [Troubleshooting](troubleshooting.md) §3 for template).
7. Save. Wait 24 hours. Validate with three test prompts using a pilot user account.
8. Stand up the operational runbook: ticket queue, on-call rotation, daily false-positive triage meeting (15 min/day for first two weeks).

**Stage 2 exit criteria:**

- ≥ 21 days of pilot enforcement.
- Net Promoter Score or equivalent user-satisfaction signal collected and reviewed.
- False-positive rate < 10%.
- All P1/P2 incidents from pilot resolved or formally accepted.
- Sign-off from Compliance, IT Security, and pilot business leads.

### Stage 3 — Broad (Weeks 7+)

**Goal:** Tenant-wide enforcement.

**Steps:**

1. Open `FSI-Copilot-DLP-Pilot` → **Save as** → name `FSI-Copilot-DLP-Production`.
2. Scope → All users (or all licensed Copilot users — depends on whether you have unlicensed users requiring policy coverage).
3. Confirm rules are enforcement-mode (Block / Block-with-override).
4. Save. **Do not delete the Pilot policy yet** — keep it for 30 days as a rollback point.
5. Send tenant-wide announcement (24 hours before activation).
6. Activate the policy. Monitor the on-call queue intensively for the first 5 business days.

**Stage 3 exit criteria:**

- Policy active for ≥ 30 days without P1 incident.
- Helpdesk ticket volume returned to baseline.
- Pilot policy deactivated; Production policy is sole enforcement source.
- Quarterly attestation cycle scheduled (Control 3.4 cadence).

---

## §5. Sensitivity Labels for Copilot

Sensitivity Labels for Copilot govern (a) **whether Copilot can ground on a labeled file or email**, and (b) **what label is applied to Copilot-generated content** (Pages, summaries, drafts).

### 5.1 Conceptual model

The decision is driven by **encryption and usage rights**, not the label name. A file labeled "Highly Confidential" with no encryption is freely groundable. A file labeled "Internal" with encryption that omits the EXTRACT or VIEW usage right is **not** groundable for the prompting user.

**Critical caveat:** A sensitivity label alone does NOT block Copilot grounding. Only **encryption + missing EXTRACT or VIEW usage right** blocks it. Many firms incorrectly assume that labeling a file "Confidential" prevents Copilot grounding — it does not.

### 5.2 Click-path: configure a label to restrict Copilot grounding

1. Microsoft Purview portal → Information Protection → Labels.
2. Open the relevant label (e.g., "Highly Confidential — Restricted").
3. Scope: confirm "Files & emails" is checked (Copilot grounding follows the file/email scope, not the groups+sites scope).
4. Encryption: **Enabled**.
5. Assign permissions → Add users/groups → For each authorized group, **uncheck EXTRACT and VIEW** if you intend to block Copilot grounding for that group while preserving the ability to open the file via the native app.
6. Save → Publish via a label policy that includes the user population.

**Validation:** After 24-hour propagation, sign in as a test user in the affected group, open a file with this label in Word, and ask Copilot to summarize. Expect a "this content can't be summarized" response or a graceful skip in the citations.

### 5.3 Click-path: apply a label to Copilot-generated content

1. Microsoft Purview portal → Information Protection → Label policies.
2. Open the policy targeting your Copilot population → **Edit policy**.
3. **Default label for documents** → set to your "Internal" or "Confidential" baseline (per your firm's labeling strategy).
4. **Default label for Pages** → set to the same or stricter baseline. (Pages are stored in OneDrive; default labels propagate.)
5. Save and republish.

### 5.4 Auto-labeling for Copilot-generated content

For Copilot-generated content destined for SharePoint or OneDrive, configure auto-labeling rules:

1. Microsoft Purview portal → Information Protection → Auto-labeling.
2. **+ Create auto-labeling policy** → name `FSI-Copilot-Output-Auto-Label`.
3. Locations → SharePoint sites + OneDrive accounts in scope.
4. Conditions → "Content contains" → Sensitive Info Types matching your firm's SITs. Optionally add trainable classifiers for FSI-specific content (e.g., investment recommendation, customer non-public info).
5. Apply the appropriate label (typically one tier above the org default — e.g., default Internal → auto-apply Confidential when SIT match).
6. **Test in simulation mode first** (this is non-negotiable — auto-label simulation reveals false positives before user-visible relabeling).
7. After ≥ 7 days of clean simulation, turn on the policy.

**Hedged language:** Auto-labeling **supports** consistent label application. It does not eliminate the need for user training on manual labeling — auto-labeling typically catches 60–80% of correctly-classified content; the remainder requires user judgment.

---

## §6. Data Loss Prevention for Microsoft 365 Copilot

DLP for Microsoft 365 Copilot is a **distinct DLP location** in the Purview portal. It is not the same as Endpoint DLP, Exchange DLP, or SharePoint DLP. It evaluates **both prompt content and response content**.

### 6.1 What DLP for M365 Copilot can do

- **Prompt-side:** Block or warn when a user submits a prompt containing sensitive content (e.g., a prompt that pastes an SSN).
- **Response-side:** Block or modify a response when Copilot would surface content from a flagged source (e.g., grounding hits a labeled file the policy excludes from Copilot).
- **Audit:** Generate Activity Explorer events for prompts and responses meeting policy criteria.

### 6.2 Click-path: create a DLP for M365 Copilot policy (production-grade)

1. Microsoft Purview portal → Data Loss Prevention → Policies → **+ Create policy**.
2. Choose **Custom** → name `FSI-Copilot-DLP-Production`.
3. Locations → toggle **Microsoft 365 Copilot** ON. Leave other locations OFF unless you specifically want this policy to span (most firms keep Copilot policies isolated for clarity of telemetry).
4. **Advanced DLP rules** → **+ Create rule** → for each protected data class:
    - Name the rule descriptively (e.g., `Block-Prompt-MNPI`).
    - **Conditions** — pick from:
        - Content contains sensitive info type (e.g., Material Non-Public Information SIT)
        - Content has sensitivity label (e.g., "Highly Confidential")
        - Content matches trainable classifier
    - **Actions** — Block, Block with override, or Audit only. Combine with **User notifications** (custom text per Compliance).
5. Set **Policy mode** to test-mode for the report-only stage; switch to active mode for pilot/production.
6. Save.

### 6.3 Prompt-side vs response-side rules

**Prompt-side example:** A user types "Please draft an email to [client] referencing the planned acquisition of [target] before the press release." The prompt itself contains MNPI. A prompt-side rule keyed to your MNPI SIT blocks the prompt before submission and notifies the user.

**Response-side example:** A user asks "Summarize my recent meetings about Project Atlas." Copilot grounds on a meeting recap that contains MNPI. A response-side rule keyed to the MNPI SIT or label modifies the response to omit the MNPI content and surfaces a notification.

**Operational reality:** Response-side enforcement has been observed to have a **higher false-positive rate** than prompt-side. Plan to spend the first two weeks of pilot tuning response-side rules. Maintain a lower SIT confidence threshold (e.g., 75%) for prompt-side and a higher threshold (e.g., 85%) for response-side to balance signal and noise.

### 6.4 Combining DLP with Sensitivity Labels — order of evaluation

When a Copilot interaction touches both label-encrypted content and DLP rules, the order is:

1. **Sensitivity label encryption check** — if the user lacks EXTRACT/VIEW, the content is excluded from grounding entirely. DLP never sees it.
2. **Prompt-side DLP** — evaluated against the prompt text.
3. **Grounding** — Copilot pulls eligible content.
4. **Response-side DLP** — evaluated against the response candidate.
5. **Response delivery or block** — based on rule actions.

This means a permissive label posture cannot be "rescued" by aggressive DLP — DLP cannot evaluate content it never sees. Get the label posture right first.

---

## §7. Restricted SharePoint Search (RSS)

Restricted SharePoint Search (RSS) is a tenant-wide setting that limits Copilot's organizational search to a curated allow-list of SharePoint sites. It is a coarse-but-effective tool for tenants that have not yet completed broad permissions remediation.

### 7.1 When to use RSS

- Tenant has a **known oversharing problem** (DAG report flags many sites with EEEU + high item counts).
- Tenant is in **early Copilot rollout** and wants to constrain blast radius while permissions remediation proceeds.
- A specific business unit needs guaranteed exclusion from Copilot grounding pending its own readiness review.

### 7.2 When NOT to use RSS

- Tenant has mature permissions hygiene and the productivity loss from RSS would be significant.
- The desired outcome is per-site exclusion only — use RCD instead (see §7.4).

### 7.3 Click-path: enable RSS

1. SharePoint admin center → Settings → Search → **Restricted SharePoint Search**.
2. Enable the toggle.
3. Add allow-listed sites — paste site URLs (one per line) up to the documented limit (currently 100 sites).
4. Save.

**Effect:** Once enabled, Copilot's organizational search is limited to the allow-listed sites plus the user's own OneDrive and the user's frequently-accessed sites. All other sites are excluded from grounding through the search surface.

**Caveat:** RSS does not block direct grounding when a user explicitly references a file (e.g., "Summarize the file at this URL"). It only constrains **search-driven** grounding.

### 7.4 Restricted Content Discoverability (RCD) — per-site exclusion

RCD is the per-site complement to RSS. Use RCD when you need to exclude specific sites from Copilot grounding without enabling tenant-wide RSS.

**Click-path:**

1. SharePoint admin center → Active sites → select the site → Policies → **Restricted Content Discoverability**.
2. Toggle ON.
3. Save.

**Effect:** The site no longer appears in Copilot's organizational search results. Direct URL access still works for users with permission.

**Critical prerequisite (PRE-05):** RCD requires at least one Microsoft 365 Copilot license assigned in the tenant. Without it, the toggle appears successful but is not enforced.

**Bulk RCD:** Portal supports per-site only. For > 25 sites, use the [PowerShell Setup](powershell-setup.md) sibling.

---

## §8. Endpoint DLP for Copilot in Edge

Endpoint DLP rules can govern Copilot interactions in **Microsoft Edge**. As of April 2026, Endpoint DLP for Copilot is **Edge-only** — Chrome, Firefox, and Safari are documented gaps.

### 8.1 Browser scope reality

| Browser | Endpoint DLP for Copilot | Notes |
|---|:---:|---|
| Microsoft Edge | ✅ Supported | Full Endpoint DLP rule coverage |
| Google Chrome | ❌ Not supported | Endpoint DLP can monitor file uploads in Chrome but cannot intercept Copilot prompts/responses |
| Mozilla Firefox | ❌ Not supported | Same as Chrome |
| Apple Safari | ❌ Not supported | macOS Endpoint DLP exists but lacks Copilot-specific hooks |

**Operational implication:** Firms that allow non-Edge browsers for Copilot access have an enforcement gap. Options:

- **Restrict Copilot web access to Edge** via Conditional Access browser-restriction policy or endpoint configuration.
- **Accept the gap** and document on the Risk Acceptance log with quarterly review (Control 3.4).
- **Deploy compensating controls** — e.g., DLP for M365 Copilot service-side policies (which apply regardless of browser) handle the bulk of enforcement; Endpoint DLP is a defense-in-depth layer.

### 8.2 Click-path: create an Endpoint DLP rule for Copilot in Edge

1. Microsoft Purview portal → Data Loss Prevention → Endpoint DLP settings — confirm Edge is in scope and onboarded devices report status Healthy.
2. Microsoft Purview portal → DLP → Policies → **+ Create policy** → Custom → name `FSI-Copilot-Endpoint-Edge`.
3. Locations → toggle **Devices** ON. Optionally toggle **Microsoft 365 Copilot** ON if you want a unified policy (most firms keep them split for clarity).
4. Rules → **+ Create rule**:
    - Conditions: include Browser = Edge, App = Microsoft 365 Copilot Chat, Activity = Paste to browser / Upload to cloud.
    - Sensitive content: SIT match or label match.
    - Actions: Block / Block with override / Audit.
5. Save and publish.

**Validation:** On a test endpoint with Edge + Copilot, attempt to paste sample sensitive content (e.g., test SSN string) into a Copilot prompt. Expect block + Endpoint DLP toast notification.

---

## §9. Pages and Notebooks — protection scope

Copilot Pages and Copilot Notebooks are governance edge cases because they live in **non-obvious storage**.

### 9.1 Pages

- **Storage:** OneDrive, as `.fluid` artifact files.
- **Permission model:** OneDrive sharing model — initially private to the creator, shareable via link or direct invite.
- **Sensitivity label:** Inherits the OneDrive default label (set in §5.3); auto-labeling rules with OneDrive scope apply.
- **DLP:** OneDrive DLP location applies. DLP for M365 Copilot **does not** evaluate Page content directly — it evaluates the prompt that generated the Page.
- **Audit:** Page creation, edit, share appear as OneDrive activities in the unified audit log with Copilot correlation IDs.
- **Retention:** Inherits OneDrive retention. If OneDrive retention is 7 years, Pages are retained 7 years.

**FSI implication:** A user can create a Page summarizing MNPI grounded from authorized sources, then share the Page via link with a wider audience. The DLP for M365 Copilot policy does not retroactively re-evaluate the Page's sharing event — that is OneDrive sharing DLP. Ensure your OneDrive sharing policies cover the gap.

### 9.2 Notebooks

- **Storage:** Loop containers (separate from OneDrive, separate from SharePoint).
- **Permission model:** Loop container permission model — owner-managed, with explicit add for collaborators.
- **Sensitivity label:** Loop containers as of April 2026 have **partial** sensitivity label coverage. Verify in your tenant — some firms find labels apply to the Notebook artifact but not to embedded components.
- **DLP:** Loop containers are emerging in DLP scope. Test thoroughly before relying on DLP for Notebooks.
- **Audit:** Notebook activities appear in the audit log under Loop workload events.
- **Retention:** Loop retention policies apply (Microsoft Purview → Data Lifecycle Management → Microsoft Loop).

**FSI implication:** Notebooks can become a "shadow workspace" for Copilot interactions. Apply Loop retention policies aligned to your OneDrive/SharePoint retention before enabling Notebooks broadly. Consider restricting Notebook creation to specific user groups during pilot.

---

## §10. Data residency, Multi-Geo, and the Anthropic exception

### 10.1 Default data residency

Microsoft 365 Copilot processes prompts and responses within the tenant's primary geography by default. Substrate (the service backbone) operates regionally, and grounding stays within the tenant's data residency unless an explicit cross-geo source is referenced.

**Click-path to confirm tenant geography:**

1. Microsoft 365 admin center → Settings → Org settings → Organization profile → **Data location**.
2. Confirm the listed geography matches your contracted data residency.

### 10.2 Multi-Geo behavior

For Multi-Geo tenants:

- Each user has a `preferredDataLocation` (PDL) attribute. Copilot routes the user's interactions through the PDL geo where supported.
- Grounding sources hosted in a geo other than the user's PDL may still be groundable (subject to permissions); the response is generated in the user's PDL.
- **Cross-geo grounding does not violate data residency** in the contractual sense, but it may have implications under specific regulator interpretations (e.g., a Singapore MAS-regulated user grounding on EU-resident data).
- Verify PDL via Graph: `GET /users/{id}?$select=preferredDataLocation`.

**Validation:** During pilot, run cross-geo test prompts and confirm the response generation path matches expectations. Document the path in your firm's data flow diagrams (relevant under GLBA 501(b) safeguards documentation).

### 10.3 EU Data Boundary (EUDB)

For EU tenants, Microsoft's EU Data Boundary commitment applies to Copilot **with the explicit exception of Anthropic-routed prompts**. If you opt in to Anthropic models in an EU tenant, prompts routed to Anthropic exit EUDB.

**Recommendation for EU FSI tenants:** Default to Anthropic opt-OUT. If business demand for Anthropic exists, document the EUDB exception, obtain Compliance and Data Protection sign-off, and apply DLP rules that prevent EUDB-sensitive content from reaching Anthropic-routed prompts.

### 10.4 The Anthropic exception (April 2026)

Anthropic models opted-in for Copilot:

- Are **not in EUDB**.
- Are **not in any sovereign cloud** (Commercial only).
- Are subject to the standard Microsoft Online Services DPA — verify with your Legal team whether your firm requires a supplemental Anthropic-specific risk assessment.
- Have **partial audit-event parity** with Azure-hosted models — model selection appears in audit events; downstream telemetry is incomplete.

---

## §11. FSI incident response clocks

Copilot-related incidents in US financial services tenants are subject to multiple regulatory clocks. The following are the clocks most commonly cited as relevant to AI governance incidents (verify with Legal for your specific obligations).

| Regulation | Trigger | Clock |
|---|---|---|
| SEC Reg S-P (amended 2024) | Breach of customer NPI | 30 days to notify customers |
| NYDFS Part 500 (23 NYCRR 500) | Cybersecurity event | 72 hours to notify NYDFS |
| SEC Form 8-K Item 1.05 | Material cybersecurity incident | 4 business days from materiality determination |
| FINRA Rule 4530 | Specified events including litigation, customer complaints | Variable; many within 30 calendar days |
| GLBA Safeguards Rule (FTC) | Notification of unauthorized access to customer information | 30 days for notification of certain events affecting ≥ 500 customers |
| Federal Reserve / OCC computer-security incident notification | "Notification incident" affecting bank operations | 36 hours |
| SEC Rule 17a-4 | Records preservation | Continuous; not an incident clock but compounds responses |

**Operational requirement:** Your AI Incident Response Playbook (cross-referenced in §13) must map each Copilot-relevant incident pattern (oversharing, leaked secret in prompt, prompt-injection-driven exfiltration, model-output defamation, hallucinated investment advice surfaced to a customer) to the applicable clocks.

**Why this section is in a portal walkthrough:** because the portal configurations you make in §§5–9 directly affect your ability to **detect** and **evidence** these incidents within the clock. A misconfigured audit log retention (PRE-04 unmet) can transform a 30-day notification clock into a non-recoverable evidence gap.

---

## §12. Evidence pack — 19 artifacts with SHA-256 hashes

The following 19 artifacts constitute the evidence pack for a Control 4.7 attestation. Generate them at the close of each rollout stage and at each quarterly attestation cycle. Compute SHA-256 hashes for tamper evidence and store them with the artifacts. Use the [PowerShell Setup](powershell-setup.md) sibling to script generation.

| # | Artifact | Source | Cadence |
|---|---|---|---|
| 1 | `pre-01-license-posture.json` | Graph `Get-MgSubscribedSku` | Per stage + quarterly |
| 2 | `pre-02-role-assignments.json` | Graph PIM/Roles export | Per stage + quarterly |
| 3 | `pre-03-label-taxonomy.json` | Purview labels + label policies + Activity Explorer adoption | Per stage + quarterly |
| 4 | `pre-04-audit-ingestion.json` | Purview Audit search + retention policy export | Per stage + quarterly |
| 5 | `pre-05-copilot-license-floor.json` | Graph user assignments | Per stage + quarterly |
| 6 | `pre-06-dag-baseline.csv` | M365 admin center DAG export | Per stage + quarterly (compare deltas) |
| 7 | `pre-07-training-signoff.pdf` | Document of record | Per stage |
| 8 | `dlp-copilot-policy-export.json` | Purview DLP policy export | Per stage + on policy change |
| 9 | `dlp-copilot-rule-coverage-matrix.csv` | Mapping of SITs to rules to regulations | Per stage + quarterly |
| 10 | `sensitivity-label-policy-export.json` | Purview labels + label policies | Per stage + on policy change |
| 11 | `auto-label-simulation-results.csv` | Purview auto-label simulation export | Quarterly |
| 12 | `rss-allow-list.csv` | SharePoint admin center export | Per stage + on change |
| 13 | `rcd-site-list.csv` | SharePoint Get-SPOSite filtered to RCD-flagged | Per stage + monthly |
| 14 | `endpoint-dlp-policy-export.json` | Purview Endpoint DLP policy export | Per stage + on change |
| 15 | `pages-and-notebooks-coverage.json` | OneDrive + Loop retention + label coverage report | Quarterly |
| 16 | `data-residency-confirmation.json` | M365 admin center org settings export + Multi-Geo PDL audit | Quarterly |
| 17 | `anthropic-opt-in-decision.pdf` | Document of record (opt-in / opt-out + signed approvals) | Annually + on change |
| 18 | `quarterly-attestation.pdf` | Cover sheet with sign-offs from Compliance, IT Security, AI Administrator | Quarterly |
| 19 | `evidence-pack-manifest.json` | Index of all 19 artifacts with SHA-256 hashes and timestamps | Per generation |

**SHA-256 generation snippet** (run from the evidence pack folder):

```powershell
$stamp = Get-Date -Format 'yyyyMM'
Get-ChildItem -File | ForEach-Object {
    $hash = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
    [pscustomobject]@{
        Artifact  = $_.Name
        SizeBytes = $_.Length
        SHA256    = $hash
        Captured  = (Get-Date).ToString('o')
        Pack      = $stamp
    }
} | ConvertTo-Json -Depth 3 | Set-Content -Path 'evidence-pack-manifest.json' -Encoding utf8
```

**Storage:** Store the evidence pack in a WORM-equivalent location aligned to your firm's record retention (typically the same store used for SEC 17a-4 obligations). Index by attestation date.

---

## §13. Cross-references and companion playbook handoff

### 13.1 Related controls

| Control | Relationship |
|---|---|
| [1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Underlying DLP/labels foundation that Copilot policies extend |
| [1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Audit pipeline used to evidence Copilot interactions |
| [1.13 — Sensitive Information Types and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | Source of SITs used in §6 DLP rules |
| [1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | Discovery and hold posture for Copilot interactions |
| [1.21 — Adversarial Input Logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Prompt-injection telemetry that complements §6 |
| [3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Reporting cadence for §11 incident clocks |
| [3.8 — Copilot Hub and Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | Dashboard surface for the §12 evidence pack |
| [4.2 — Site Access Reviews and Certification](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | Foundation for permissions hygiene |
| [4.5 — SharePoint Security and Compliance Monitoring](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | RCD candidates emerge from 4.5 monitoring |
| [4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Direct upstream for RSS/RCD scoping decisions |
| [4.8 — Item-Level Permission Scanning](../../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md) | Identifies the EEEU oversharing patterns called out in §1.3 |
| [4.9 — Embedded File Content Governance](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md) | Governs Pages and Notebook embedded content per §9 |

### 13.2 Companion playbook handoff

This portal walkthrough hands off to its siblings as follows:

**To [PowerShell Setup](powershell-setup.md):**

- Use when planning the §12 evidence pack — all 19 artifacts have scripted generation paths in PowerShell Setup §3.
- Use when scaling RCD beyond 25 sites — PowerShell Setup §4 covers `Set-SPOSite -RestrictContentOrgWideSearch` bulk patterns.
- Use when standing up the quarterly attestation automation (Control 3.4 cadence).
- Use when integrating with your CI/CD-style configuration pipeline (e.g., M365 DSC, Microsoft Graph PowerShell-based GitOps).

**To [Verification & Testing](verification-testing.md):**

- Use after Stage 1 (Report-only) to validate signal quality — Verification & Testing §2 has the false-positive triage procedure.
- Use after Stage 2 (Pilot) to validate user experience — Verification & Testing §3 has the pilot-user survey template.
- Use after Stage 3 (Broad) to validate enforcement at scale — Verification & Testing §4 has the production health-check script.
- Use at each quarterly attestation — Verification & Testing §6 has the attestation pre-flight checklist.

**To [Troubleshooting](troubleshooting.md):**

- Use when a user reports "Copilot can't find a file I have access to" — Troubleshooting §2 covers grounding gaps (RSS scope, RCD, encryption).
- Use when a DLP rule is flagging false positives at > 30% rate — Troubleshooting §3 covers SIT confidence tuning.
- Use when sensitivity labels appear to be ignored by Copilot — Troubleshooting §4 covers the EXTRACT/VIEW evaluation path.
- Use when Endpoint DLP rules aren't firing — Troubleshooting §5 covers Edge-only scope and onboarding state checks.

**To [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md):**

- Use immediately on any P1/P2 oversharing event, leaked-secret-in-prompt event, or model-output incident with potential customer impact.
- The AI IR Playbook references this walkthrough for **post-incident remediation** — specifically RCD enablement for affected sites and DLP rule tuning to prevent recurrence.

### 13.3 External references

- Microsoft Learn — [Microsoft 365 Copilot data, privacy, and security](https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-privacy)
- Microsoft Learn — [Sensitivity labels for Copilot](https://learn.microsoft.com/purview/sensitivity-labels-coauthoring)
- Microsoft Learn — [DLP for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)
- Microsoft Learn — [Restricted SharePoint Search](https://learn.microsoft.com/sharepoint/restricted-sharepoint-search)
- Microsoft Learn — [Restricted Content Discoverability](https://learn.microsoft.com/sharepoint/restricted-content-discovery)
- Microsoft Learn — [Endpoint DLP](https://learn.microsoft.com/purview/endpoint-dlp-learn-about)
- Microsoft Learn — [Multi-Geo capabilities in OneDrive and SharePoint](https://learn.microsoft.com/microsoft-365/enterprise/multi-geo-capabilities-in-onedrive-and-sharepoint-online-in-microsoft-365)
- FINRA Notice 24-09 — Use of artificial intelligence
- FINRA Regulatory Notice 25-07 series — AI supervisory expectations
- SEC Rule 17a-4 — Records preservation
- NYDFS 23 NYCRR 500 — Cybersecurity requirements
- Federal Reserve SR 26-2 (formerly SR 11-7) — Model risk management

---

## §14. Anti-patterns — at least 15 things NOT to do

These anti-patterns are derived from observed FSI Copilot rollouts. Each carries a specific harm and the section that addresses it.

| # | Anti-pattern | Harm | Addressed in |
|---|---|---|---|
| AP-01 | Enabling Copilot for all users on Day 1 without DAG report review | Mass oversharing; potential GLBA 501(b) and FINRA 4511 implications | §1.3, §3 PRE-06 |
| AP-02 | Assuming a "Confidential" sensitivity label blocks Copilot grounding | False sense of security; grounding occurs anyway | §5.1 |
| AP-03 | Skipping Stage 1 (Report-only) and going straight to enforcement | High false-positive rate; user revolt; helpdesk overwhelm | §4 Stage 1 |
| AP-04 | Configuring DLP only on the prompt side ("if we block the input we're done") | Grounding-driven exfiltration uncaught | §6.3 |
| AP-05 | Using Global Admin for routine Copilot policy changes | Audit-trail mess; least-privilege violation; Fed SR 26-2 (formerly SR 11-7) finding | §3 PRE-02 |
| AP-06 | Enabling Restricted Content Discoverability before assigning any Copilot license | Toggle silently fails; perceived control is absent | §3 PRE-05, §7.4 |
| AP-07 | Enabling Anthropic opt-in tenant-wide without persona analysis | EUDB exit; sovereign cloud confusion; opaque audit trail | §2.1, §10.4 |
| AP-08 | Allowing Chrome/Firefox/Safari for Copilot and assuming Endpoint DLP applies | Endpoint DLP for Copilot is Edge-only; gap unmitigated | §8.1 |
| AP-09 | Treating Pages as ephemeral / out-of-scope for governance | Pages live in OneDrive; full retention and label scope applies | §9.1 |
| AP-10 | Treating Notebooks the same as Pages | Notebooks live in Loop containers — different permission and DLP coverage | §9.2 |
| AP-11 | Setting RSS allow-list and forgetting to maintain it | Drift; productivity loss; users route around RSS via direct URLs | §7.3 |
| AP-12 | Auto-labeling production rollout without simulation | Mass relabeling event; user confusion; potential disclosure incidents | §5.4 |
| AP-13 | Audit log retention configured for default 90 days | Cannot meet FINRA 4511 / SEC 17a-4 evidence requirements | §3 PRE-04 |
| AP-14 | Same DLP policy spans Exchange, SharePoint, Devices, and Copilot | Telemetry impossible to interpret; tuning impossible | §6.2 |
| AP-15 | No quarterly attestation cycle scheduled at rollout | Drift goes undetected; audit findings at next exam | §12, §13.1 (3.4 link) |
| AP-16 | Pilot population chosen from a single business function | Misses cross-functional failure modes; pilot signal is unrepresentative | §4 Stage 2 |
| AP-17 | Compliance not part of false-positive triage during pilot | Rule tuning drifts away from supervisory intent | §4 Stage 1 exit, §4 Stage 2 |
| AP-18 | Treating the §12 evidence pack as a one-time generation | Drift between attestations is invisible; quarterly cycle becomes a fire drill | §12 |

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
