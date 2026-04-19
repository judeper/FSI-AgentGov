# Portal Walkthrough: Control 1.3 - SharePoint Content Governance and Permissions

**Last Updated:** April 2026
**Portals:** SharePoint Admin Center, Microsoft Purview, Microsoft Entra Admin Center, Microsoft 365 admin center
**Estimated Time:** 3–5 hours for initial Zone 3 configuration; 30–60 minutes per additional agent grounding site

---

## Prerequisites

- [ ] **SharePoint Admin** role (configures tenant sharing, RAC, RCD, Restricted SharePoint Search, DAG)
- [ ] **Purview Info Protection Admin** role (publishes container and file sensitivity labels)
- [ ] **Purview Compliance Admin** role (publishes DLP policies for SharePoint/OneDrive)
- [ ] **Entra Identity Governance Admin** role (creates access reviews on M365 groups)
- [ ] **Microsoft 365 Copilot** licenses **or** standalone **SharePoint Advanced Management** SKU assigned (required for RAC, RCD, DAG, Restricted SharePoint Search)
- [ ] [Control 1.5 — DLP & Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) labels published to the in-scope user audience
- [ ] An approved inventory of **agent grounding sites** (which SharePoint sites Copilot Studio agents and Microsoft 365 Copilot are sanctioned to consume) — this is the working list referenced throughout

> **April 2026 UI note:** SharePoint admin center now exposes "Restricted access control" and "Restrict content discovery" directly under each site's **Settings** flyout. The legacy "Information access" tile that some 2024–2025 documentation references has been retired. The flyout is the only supported UI surface — all other paths route here.

---

## Step 1 — Configure tenant-level sharing (SharePoint admin center)

**Path:** [SharePoint admin center](https://admin.microsoft.com/sharepoint) → **Policies** → **Sharing**

1. Set **External sharing** sliders:
    - **SharePoint:** `Only people in your organization` (Zone 3 default) or `Existing guests` (Zone 2 with sanctioned partners).
    - **OneDrive:** match SharePoint or set more restrictive.
2. Under **More external sharing settings**:
    - ✅ Limit external sharing by domain → add a **block list** with `gmail.com`, `yahoo.com`, `outlook.com`, `hotmail.com`, `icloud.com`, `aol.com`, `proton.me`. For Zone 3, switch to an **allow list** of vetted partner domains only.
    - ✅ People who use a verification code must reauthenticate after **15 days**.
    - ✅ Allow only users in specific security groups to share externally → bind to `FSI-Approved-External-Sharers`.
    - ❌ Allow guests to share items they don't own (off).
    - ✅ Guests must sign in using the same account to which sharing invitations are sent.
3. Under **File and folder links**:
    - **Default link type:** `Specific people (only the people the user specifies)`.
    - **Default link permission:** `View`.
    - **Anonymous link expiration:** `30` days (or set anonymous links to off entirely for Zone 3).
4. Click **Save**. Tenant changes take effect within minutes; M365 Copilot and Copilot Studio honor the new defaults on the next user request.

**FSI recommended values:**

| Setting | Zone 1 | Zone 2 | Zone 3 |
|---|---|---|---|
| Tenant `SharingCapability` | `ExternalUserSharingOnly` (tenant default) | `ExistingExternalUserSharingOnly` | `Disabled` |
| `DefaultSharingLinkType` | `Internal` | `Internal` | `Internal` |
| `DefaultLinkPermission` | `View` | `View` | `View` |
| Anonymous link lifetime | 30 days | 7 days | Off |
| Domain restriction | Block consumer domains | Block list | Allow list (partner only) |

---

## Step 2 — Inventory and triage agent grounding sites

**Path:** SharePoint admin center → **Sites** → **Active sites** → filter and export

1. Click **Export** to download the active-sites CSV. Filter to sites that are sanctioned agent grounding sources.
2. For every site in the inventory, capture:
    - URL, primary admin, M365 group ID, current `SharingCapability`, current sensitivity label, RAC status, RCD status.
3. For sites **not** sanctioned but reachable by Microsoft 365 Copilot today (because users have permission), flag for either RCD application or Restricted SharePoint Search exclusion.
4. Save the inventory to your evidence store (`/evidence/1.3/site-inventory-YYYY-MM.csv`).

---

## Step 3 — Apply container sensitivity labels (Microsoft Purview)

**Path:** [Microsoft Purview](https://purview.microsoft.com) → **Information Protection** → **Labels** → select label → **Edit label**

1. Confirm at least one container-scoped label exists per zone tier — for example `Internal`, `Confidential-FSI`, `Highly Confidential — MNPI`.
2. For each label, on the **Define protection settings for groups and sites** step, configure:
    - **Privacy:** `Private` (Zone 2/3) or organization default (Zone 1).
    - **External user access:** `Block` (Zone 3) or `Allow with restrictions` (Zone 2 partner sites only).
    - **External sharing from labeled SharePoint sites:** restrict to match the zone (Zone 3 = `Only people in your organization`).
    - **Access from unmanaged devices:** `Block` (Zone 3); `Allow limited, web-only access` (Zone 2); tenant default (Zone 1).
    - **Default sharing link type:** `Specific people` / `View`.
4. Publish the label policy to the audience that owns agent grounding sites.

**Apply container label to a site:**

- SharePoint admin center → **Active sites** → select site → **Settings** flyout → **Sensitivity** → choose label → **Save**.
- Or, from the site itself: site header → **Settings (gear)** → **Site information** → **Sensitivity**.

**Apply default library label:**

1. From the document library used by the agent → **Settings (gear)** → **Library settings** → **More library settings**.
2. Under **Permissions and Management** → **Apply label to items in this list or library** → choose the file label → **Save**.
3. For backfill, run a Purview **auto-labeling** policy in simulation, then publish.

---

## Step 4 — Remove broad permission claims

**Path:** SharePoint site → **Settings (gear)** → **Site permissions** → **Advanced permissions settings**

1. Open each site group (`<Site> Members`, `<Site> Visitors`).
2. If any of these claims appear, remove them:
    - `Everyone`
    - `Everyone except external users`
    - `All Users (Windows)` / `All Users (Membership)`
3. Replace with named M365 groups or Entra security groups whose membership is itself reviewed (Step 7).
4. **Document** the remaining grants in the evidence store with a one-line business justification per grant.

> **Why this matters for Copilot:** Microsoft 365 Copilot grounds against any content the calling user has permission to read. A single `Everyone except external users` grant on a sensitive site can surface that content into Copilot answers across the entire workforce.

---

## Step 5 — Restricted Access Control (Zone 3 sites)

**Path:** SharePoint admin center → **Active sites** → select site → **Settings** flyout → **Restricted access control** → **Manage**

1. Toggle **Restricted access control** to **On**.
2. Add the **single** Microsoft 365 group or Entra security group that should be allowed to access the site.
3. Click **Save**. SharePoint will:
    - Block all users not in the group from opening the site, even if they have direct permissions.
    - Strip the site's content from Microsoft 365 Copilot grounding for users outside the group.
4. Allow up to **24 hours** for the policy to fully propagate (cache TTLs, search index).
5. Repeat for every Zone 3 agent grounding site. Track applied sites in the inventory.

> **Caveat:** RAC requires the site to be backed by a Microsoft 365 group or Entra security group with a stable membership. RAC is incompatible with sites that grant access via direct user permissions only.

---

## Step 6 — Restricted Content Discovery (suppress from search and Copilot)

**Path:** SharePoint admin center → **Active sites** → select site → **Settings** flyout → **Restrict content discovery** → toggle **On** → **Save**

Use RCD when a site should remain accessible to its members but should **not** be discoverable by:

- Organization-wide SharePoint search.
- Microsoft 365 Copilot grounding (Business Chat).
- Suggested files / personalized search surfaces.

RCD does not change site permissions — users with direct permission to the site can still open it. RCD is the correct lever for "this site has legitimate users but it should not surface in Copilot answers" scenarios such as HR investigations, M&A, or executive working folders.

> **April 2026:** RCD is configurable per-site in the SharePoint admin UI and exposed via PowerShell as `Set-SPOSite -RestrictContentOrgWideSearch`. There is also a tenant-wide variant accessed via **Policies** → **Restrict content discovery** that lets admins flag sites in bulk.

---

## Step 7 — (Temporary) Restricted SharePoint Search allow-list

**Path:** SharePoint admin center → **Settings** → **Search** → **Restricted SharePoint Search**

Use this only as a temporary safeguard while remediation of broader oversharing is in flight. It limits Microsoft 365 Copilot grounding to a curated allow-list of up to 100 sites tenant-wide, plus the user's own OneDrive content.

1. Toggle **Restricted SharePoint Search** to **On**.
2. Add up to 100 site URLs that are sanctioned for Copilot grounding.
3. Click **Save**. Effect is tenant-wide and applies on the next Copilot request per user.
4. Set a calendar reminder to revisit and disable once Steps 4–6 are fully applied — Restricted SharePoint Search is not intended as a permanent control.

---

## Step 8 — Data Access Governance reports (oversharing visibility)

**Path:** SharePoint admin center → **Reports** → **Data access governance**

1. Open each of the following reports for the most recent run:
    - **Sites shared with "Everyone except external users"**
    - **Sites shared with people in the org**
    - **Sites with sensitive content**
    - **Permissions state for sites**
2. For every Zone 3 agent grounding site that appears, open a remediation ticket and apply Steps 4–6.
3. Schedule a monthly review meeting with the AI Governance Lead and Compliance Officer to walk these reports.
4. Export the reports to your evidence store at month-end.

---

## Step 9 — Publish DLP policies for SharePoint and OneDrive

**Path:** [Microsoft Purview](https://purview.microsoft.com) → **Data Loss Prevention** → **Policies** → **+ Create policy**

1. Choose **Custom** → name `FSI-DLP-SharePoint-AgentGrounding`.
2. **Locations:** SharePoint sites, OneDrive accounts. Scope to the agent-grounding site inventory (or all, then exclude).
3. **Conditions:** add sensitive information types — US SSN, US Bank Account Number, US ITIN, ABA Routing Number, plus any **custom keyword classifiers** for MNPI tickers and project codenames.
4. **Actions:**
    - Restrict access or encrypt content (Block external sharing for Zone 3; warn-on-share for Zone 2).
    - Notify the user with a customized policy tip referencing the FSI policy ID.
    - Generate an incident report to the Compliance Officer mailbox.
5. Start in **Test mode with policy tips** for 7–14 days, review incidents, then move to **Enforce**.

---

## Step 10 — Access reviews on owning M365 groups (Entra)

**Path:** [Microsoft Entra admin center](https://entra.microsoft.com) → **Identity Governance** → **Access reviews** → **+ New access review**

1. **Resource type:** `Teams + Groups` → select **specific groups** → add the M365 groups backing the agent grounding sites in scope.
2. **Reviewers:**
    - Zone 3: **Multiple reviewers** — site owner **plus** the AI Governance Lead.
    - Zone 2: Group owners.
    - Zone 1: Self-review acceptable.
3. **Frequency:** Quarterly (Zone 3), Semi-annually (Zone 2), Annually (Zone 1). **Duration:** 14 days.
4. **Upon completion settings:**
    - **Auto apply results:** On.
    - **If reviewers don't respond:** `Remove access` for Zone 3; `Take recommendations` for Zone 2; `No change` for Zone 1.
    - **Action to apply on denied users:** `Remove user's membership from the resource`.
    - **Justification required:** On.
5. **Advanced:** turn on reviewer-decision helpers (sign-in inactivity recommendations) and reviewer recommendations.
6. Click **Create**.

---

## Configuration by governance level

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---|---|---|---|
| Tenant `SharingCapability` | tenant default | `ExistingExternalUserSharingOnly` | `Disabled` |
| Container label | recommended | required (`Internal`+) | required (`Confidential`+) |
| `Everyone except external users` removed | recommended | required | required |
| Restricted Access Control | not required | optional | required |
| Restricted Content Discovery | not required | as needed | required unless site is sanctioned for Copilot |
| DLP policy | tenant default | `Test with notifications` | `Enforce` |
| Access review cadence | annual | semi-annual | quarterly w/ auto-remove |
| DAG report review | annual | quarterly | monthly |

---

## Validation

After completing the steps above, verify:

- [ ] `Get-SPOTenant` shows the expected tenant sharing values (Step 1)
- [ ] All sites in the agent grounding inventory show the expected `SensitivityLabel` and zero broad claims (Steps 3–4)
- [ ] All Zone 3 sites have RAC enabled (Step 5) and, where applicable, RCD enabled (Step 6)
- [ ] DAG reports show no unexpected Zone 3 site shared with `Everyone except external users` (Step 8)
- [ ] DLP policy is in Enforce mode for Zone 3 (Step 9)
- [ ] Access reviews are scheduled and the most recent cycle completed with documented outcomes (Step 10)

See [Verification & Testing](verification-testing.md) for the full test matrix and evidence list.

---

[Back to Control 1.3](../../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0*
