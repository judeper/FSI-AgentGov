# Control 4.6 — Verification & Testing: Grounding Scope Governance

> Verification procedures for [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md). Run each test on the cadence in §1, capture evidence per §6, and complete the attestation in §7 each cycle.
>
> **Scope of this playbook.** Control 4.6 governs *grounding scope* — which SharePoint and OneDrive content surfaces to AI agents (Microsoft 365 Copilot chat / Business Chat, Copilot Studio agents, declarative Agent Builder agents) for grounding and citation. The control under test is the **union** of seven mechanisms, not RCD alone:
>
> 1. **RCD — Restricted Content Discovery** (per-site exclusion at SharePoint Admin Center; affects tenant-wide search and Microsoft 365 Copilot chat / Business Chat).
> 2. **RSS — Restricted SharePoint Search** (tenant allowed-list of up to 100 sites; positions itself as a *short-term* containment measure, **not** a security boundary).
> 3. **DLP for Microsoft 365 Copilot** (Power Platform DLP policies that block SharePoint / OneDrive URLs from being added as Copilot Studio knowledge sources).
> 4. **DAG — Data Access Governance reports** (oversharing, sharing-links, and sensitivity-label coverage reports that establish the regulator-credible evidence trail).
> 5. **Personal OneDrive boundary** (RCD does not apply to OneDrive; organizational Copilot Studio agents must not surface a publisher''s OneDrive content to other invokers).
> 6. **In-app Copilot carve-out** (RCD does *not* block Word / Excel / PowerPoint Copilot grounding on a file the user has open — this is documented behavior and the single most common false-fail in this control).
> 7. **Unified Audit Log evidence of grounding-scope changes** (`SharePointSetTenantSettings` family operations and DLP policy edits — verify exact operation names against current Microsoft Learn at write time).
>
> **Out of scope here:** SharePoint records retention horizons (verified under [Control 1.9](../1.9/verification-testing.md)), unified-audit retention configuration (verified under [Control 1.7](../1.7/verification-testing.md)), and the broader sensitivity-label / DLP design beyond grounding-scope enforcement (verified under [Control 1.5](../1.5/verification-testing.md)).
>
> **Audience:** M365 administrator + AI Governance Lead + Compliance Officer at a US financial services organization producing audit-defensible evidence for FINRA Rule 4511 / 3110 / 25-07, SEC Rule 17a-3/4, GLBA 501(b), SOX 302/404, OCC 2011-12 / Federal Reserve SR 11-7, and NYDFS 23 NYCRR 500 examiners.
>
> **Sovereign clouds:** Commercial · GCC · GCC High · DoD — see §5 for variants. RSS, RCD, SharePoint Advanced Management (SAM), and DLP-for-Copilot have **non-parity availability** in US Government clouds; verify each capability against current Microsoft Learn before claiming PASS / FAIL on a sovereign tenant.
>
> **Cross-links:** [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md) · [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md).
>
> **Last UI Verified:** April 2026.

---

## What this verification catches

This catalog is designed to surface the carry-forward defect classes that the AI Council review identified for Grounding Scope Governance:

- **RCD-only thinking.** A tenant that has RCD enabled on a handful of sensitive sites but no RSS posture, no DLP-for-Copilot policy, no DAG reporting, and no OneDrive-boundary test has implemented roughly one-seventh of the control. The verification catalog forces evidence on every mechanism in the §1 cadence.
- **Wrong surface tested.** RCD scopes Microsoft 365 Copilot chat / Business Chat (the work-grounded surface at `microsoft365.com/chat`) and tenant-wide search. It does not scope in-app Copilot in Word, Excel, or PowerPoint when the user has the file open. A test that prompts in-app Copilot and reports "RCD failed" is reading the wrong surface.
- **In-app carve-out misread as a defect.** When `4.6-INAPP-01` shows that an RCD-restricted file *still* yields a Word Copilot summary, the operationally correct action is **document and retain** as expected behavior — not roll back the RCD policy.
- **Fabricated SLA trap.** The previous version of this playbook said "allow 24-48 hours" before testing. That is not a Microsoft-published value. The only published windows are RSS take-effect (~1 hour), RCD propagation (variable; *more than a week* on very large sites per Learn), and DAG activity-report population (~24 hours after collection enabled, with 28-day activity history). Anything else is firm-defined and must be labeled as such.
- **DLP-for-Copilot completely untested.** A SharePoint URL is blocked from Copilot Studio knowledge-source ingest by a Power Platform DLP policy; nothing in RCD or RSS produces that block. The DLP-for-Copilot test family (`4.6-DLP-NN`) is the only path to that evidence.
- **DAG reports never extracted.** The DAG snapshot and activity reports are the canonical examiner-facing oversharing evidence. A control attestation without a recent DAG report is hollow.
- **OneDrive boundary assumed, not tested.** Personal OneDrive is excluded from RCD by design; an organizational Copilot Studio agent must not bridge a publisher''s OneDrive to other invokers. `4.6-OND-NN` exercises that boundary.
- **Two-portal precondition skipped.** RCD and RSS live in the SharePoint Admin Center (SPAC). DLP-for-Copilot lives in the Power Platform Admin Center (PPAC). State captured from one portal, hours apart, is not an evidence-coherent baseline. Pre-flight §2.4 enforces a ±15-minute capture window across both portals.
- **Recent-interaction false-pass on RSS tests.** RSS is documented as *not a security boundary* — content the test user owns, recently accessed, or had directly shared still surfaces. RSS tests with a "dirty" test identity produce non-deterministic results. Pre-flight §2.7 mandates a clean, never-touched test identity.
- **UAL operation name guessed.** `SharePointSetTenantSettings` is the documented family for tenant-settings audit rows, but the *exact* operation name and current set evolve. Verify on Learn at every UI-verification cycle (`audit-log-activities`).
- **Schema drift on `Get-SPOTenant` / `Get-SPOTenantRestrictedSearchAllowedList`.** Property names and shapes have changed across SPO Management Shell versions. NEG tests assert property presence before the assertion runs; otherwise a renamed property silently passes.
- **Sovereign-cloud "passes" without verification.** RSS and DLP-for-Copilot have non-parity in US Government clouds. Sampling a "pass" without reading current Learn is an examiner-facing misstatement.

Each test below maps to the failure mode it detects, names a deterministic fixture, asserts an expected/actual JSON shape, and emits an artifact set whose SHA-256 is recorded in the §6 manifest.

---
## 1. Re-Verification Cadence

Each test below has a primary cadence (driven by the regulator who wants to see the evidence) and runs additionally on every *change* to the underlying configuration and on every grounding-scope incident. **All timestamps in artifacts and audit assertions are UTC.**

| Test ID | Frequency | Owner | Retention | Regulatory driver |
|---|---|---|---|---|
| 4.6-LIC-01 | Quarterly + on-license-change | M365 Administrator | 7 years (SOX 404) | SOX 302/404 |
| 4.6-UAL-01 | Quarterly + on-tenant-change | Compliance Officer | 7 years (SOX 404) | SEC 17a-4(b), FINRA 4511 |
| 4.6-MOD-01 | Quarterly + on-module-update | M365 Administrator | 3 years | OCC 2011-12 (model risk lineage) |
| 4.6-RCD-01 | Monthly + on-RCD-change | SharePoint Admin | 6 years (FINRA 4511) | FINRA 4511, SEC 17a-3 |
| 4.6-RCD-02 | Monthly + on-RCD-change | SharePoint Admin | 6 years (FINRA 4511) | FINRA 4511, SEC 17a-3 |
| 4.6-RCD-03 | Monthly + on-RCD-change | SharePoint Admin | 6 years (FINRA 4511) | FINRA 4511, SEC 17a-3 |
| 4.6-RCD-04 | Quarterly | SharePoint Admin | 6 years | FINRA 3110, OCC 2011-12 |
| 4.6-RCD-05 | Monthly + on-RCD-change | SharePoint Admin | 6 years | FINRA 4511 |
| 4.6-RCD-06 | Quarterly | SharePoint Admin | 6 years | FINRA 25-07 |
| 4.6-RSS-01 | Monthly + on-RSS-change | SharePoint Admin | 6 years | FINRA 4511 |
| 4.6-RSS-02 | Monthly + on-RSS-change | SharePoint Admin | 6 years | FINRA 4511 |
| 4.6-RSS-03 | Monthly + on-RSS-change | SharePoint Admin | 6 years | FINRA 4511 |
| 4.6-RSS-04 | Quarterly | SharePoint Admin | 6 years | FINRA 3110 |
| 4.6-RSS-05 | Quarterly | AI Governance Lead | 6 years | FINRA 25-07 (NOT-A-BOUNDARY attestation) |
| 4.6-DLP-01 | Monthly + on-policy-change | Purview Compliance Admin | 6 years (FINRA 4511) + 7 years (SOX 404) | FINRA 4511, SOX 404, GLBA 501(b) |
| 4.6-DLP-02 | Monthly + on-policy-change | Purview Compliance Admin | 6 years + 7 years | FINRA 4511, SOX 404 |
| 4.6-DLP-03 | Monthly + on-policy-change | Power Platform Admin | 6 years + 7 years | FINRA 4511, SOX 404 |
| 4.6-DLP-04 | Quarterly | Purview Compliance Admin | 6 years + 7 years | GLBA 501(b), NYDFS 500.11 |
| 4.6-DAG-01 | Monthly | SharePoint Admin | 6 years | FINRA 3110, FINRA 25-07, SEC 17a-3 |
| 4.6-DAG-02 | Monthly | SharePoint Admin | 6 years | FINRA 3110, GLBA 501(b) |
| 4.6-DAG-03 | Quarterly | AI Governance Lead | 6 years | FINRA 25-07 |
| 4.6-OND-01 | Quarterly | M365 Administrator | 6 years | FINRA 4511, GLBA 501(b) |
| 4.6-OND-02 | Quarterly | AI Governance Lead | 6 years | FINRA 4511, GLBA 501(b) |
| 4.6-INAPP-01 | Quarterly | AI Governance Lead | 6 years | FINRA 25-07 (false-fail prevention) |
| 4.6-INAPP-02 | Quarterly | AI Governance Lead | 6 years | FINRA 25-07 |
| 4.6-AUDIT-01 | Monthly | Compliance Officer | 7 years (SOX 404) | SEC 17a-4(b), SOX 404 |
| 4.6-AUDIT-02 | Monthly | Compliance Officer | 7 years | SOX 404 |
| 4.6-AUDIT-03 | Quarterly | Compliance Officer | 7 years | SOX 404, FINRA 4511 |
| 4.6-NEG-01 | Quarterly | SharePoint Admin | 6 years | FINRA 25-07 (negative-test discipline) |
| 4.6-NEG-02 | Quarterly | SharePoint Admin | 6 years | FINRA 25-07 |
| 4.6-NEG-03 | Quarterly | Purview Compliance Admin | 6 years | FINRA 25-07 |
| 4.6-NEG-04 | Quarterly | AI Governance Lead | 6 years | FINRA 25-07 |
| 4.6-IR-01 | Annually + on-incident | AI Governance Lead + Risk Officer | 7 years (SOX 404) | OCC 2011-12, SR 11-7, NYDFS 500.16 |

**On-change re-runs.** Any change to (a) the RCD list on a site, (b) the RSS allowed-list, (c) any DLP-for-Copilot policy in scope of `Microsoft 365 Copilot` location, (d) any in-scope SharePoint site''s sharing settings, or (e) the role assignments named in §2.6 triggers an immediate re-run of the affected test family within five business days. The on-change trigger is detected from the AUDIT-01 monthly diff or from change-management ticket metadata.

**On-incident re-runs.** Any of the following grounding-scope incidents triggers `4.6-IR-01` plus a re-run of the implicated test family within 24 hours:
- A user reports unexpected content surfaced by Microsoft 365 Copilot chat / Business Chat citing a site that should have been RCD-restricted.
- A Copilot Studio agent author successfully ingests a SharePoint URL that DLP-for-Copilot should have blocked.
- A DAG report shows a > 25% week-over-week increase in oversharing-link count on any site labeled `Confidential` or higher.
- A PPAC / SPAC role-assignment change touches one of the named roles in §2.6 outside an approved change window.

**Frequency rationale.** Monthly cadence on RCD / RSS / DLP / DAG / AUDIT mirrors the broker-dealer supervisory review pattern (FINRA 3110) and the SOX quarterly attestation cycle. Quarterly cadence on negative tests, in-app carve-out tests, and OND tests reflects that those scenarios change far less often but must be on a calendar to remain examiner-credible. Annual cadence on `4.6-IR-01` matches OCC 2011-12 / SR 11-7 model-risk validation.

**Frequencies labeled "firm-defined."** The firm sets the calendar day-of-month for the monthly cadence, the named cycle owner for each test, and any acceleration above the cadences above. Microsoft does not publish a regulator-required cadence for any of these tests; the cadences here are this framework''s recommendation, not Microsoft policy.

---
## 2. Pre-flight Gates

Every test in §4 is **gated** on the seven pre-flight assertions below. If any pre-flight fails, the entire cycle is aborted and the failure is logged in the §6 manifest with `status: BLOCKED`. Do not proceed to §4 with any pre-flight in `FAIL`.

### 2.1 License entitlement

Verify that the test tenant carries the licensing required for each mechanism under test:

- **Microsoft 365 Copilot** licenses on every named test user in §2.6 (RCD, RSS, in-app, OneDrive boundary, DAG citation tests).
- **SharePoint Advanced Management (SAM)** add-on at the tenant level (RCD configuration UI, DAG oversharing reports). RCD enablement and DAG reporting both require SAM; without SAM the tests in `4.6-RCD-NN` and `4.6-DAG-NN` cannot be authoritatively run and must be recorded as `BLOCKED`, not `PASS`.
- **Microsoft Purview** (Data Loss Prevention) license sufficient to author DLP policies with the `Microsoft 365 Copilot` location. Verify on the tenant license report; do not infer from a generic "E5" SKU label without checking the SKU detail.

Capture the license summary as `4.6-LIC-01-<TENANT>-<UTC>-licenses.json` and SHA-256 sidecar.

### 2.2 Unified Audit Log enabled

Confirm UAL is enabled tenant-wide and that retention covers the longest regulatory horizon claimed in §1 (7 years for SOX 404). UAL configuration is verified in detail under [Control 1.7](../1.7/verification-testing.md); this control re-asserts the gate. If UAL is disabled or retention is shorter than 7 years, every AUDIT-NN test will be inconclusive — do not proceed.

Capture `4.6-UAL-01-<TENANT>-<UTC>-ual-state.json`.

### 2.3 PowerShell modules pinned

Pin and record the exact module versions used for the cycle. Module-version drift is the most common cause of silently broken NEG tests. Follow the [_shared PowerShell Authoring Baseline](../../_shared/powershell-baseline.md) for connection patterns, error handling, and logging.

| Module | Minimum version | Used for |
|---|---|---|
| `Microsoft.Online.SharePoint.PowerShell` (SPO Management Shell) | latest GA at cycle start | RCD / RSS configuration read, `Get-SPOTenant`, `Get-SPOTenantRestrictedSearchAllowedList` |
| `PnP.PowerShell` | latest GA | Per-site RCD property read where SPO Management Shell does not expose the property |
| `ExchangeOnlineManagement` | latest GA | UAL search (`Search-UnifiedAuditLog`) |
| `Microsoft.Graph` | latest GA | Power Platform DLP policy enumeration via Graph beta endpoints (where available); supplemental telemetry |
| `Microsoft.PowerApps.Administration.PowerShell` | latest GA | Power Platform DLP policy enumeration (primary) |

Record actual installed versions to `4.6-MOD-01-<TENANT>-<UTC>-modules.json`. Any cycle that runs against a non-pinned module set is **non-reproducible** and must be re-run.

### 2.4 Two-portal precondition (±15 minute capture window)

RCD and RSS state lives in the **SharePoint Admin Center (SPAC)**. DLP-for-Copilot state lives in the **Power Platform Admin Center (PPAC)** and **Microsoft Purview**. A coherent baseline requires both states captured within a **±15-minute window** so that no DLP edit during the SPAC capture invalidates the DLP test.

Mechanically:

1. Start a UTC timer (record `T0` to the second).
2. Capture SPAC state (RCD list, RSS allowed-list, `Get-SPOTenant` settings) and write to `4.6-RCD-PRE-<TENANT>-<UTC>-spac.json`.
3. Within 15 minutes of `T0`, capture PPAC / Purview state (DLP-for-Copilot policy enumeration, policy bodies for in-scope policies) and write to `4.6-DLP-PRE-<TENANT>-<UTC>-ppac.json`.
4. Compute `delta_seconds = T_ppac - T_spac`. If `|delta_seconds| > 900`, abort the cycle and re-run. Record the delta in the manifest (§6).

### 2.5 Sovereign-cloud parity gate

For tenants in GCC, GCC High, or DoD, verify on current Microsoft Learn that each mechanism under test is **available** in the cloud being tested. As of the Last UI Verified date in the header:

- RSS, RCD, SAM, and DLP-for-Copilot have **non-parity availability windows** in US Government clouds.
- Connector payload limits in GCC are tighter than commercial (~450KB).

If a mechanism is unavailable in the sovereign cloud being tested, the corresponding test family is recorded as `N/A — sovereign non-parity` with a Learn citation, not `FAIL`. Do **not** silently skip; the §7 attestation must enumerate every `N/A`.

### 2.6 Named test fixtures (do not run on production identities)

The following fixtures must exist in every test tenant and must be used exclusively for this control. Running RSS or in-app tests against an identity with recent interaction with the test sites produces non-deterministic results because RSS and in-app surfaces both honor recent-interaction / share / ownership signals.

| Fixture type | Identifier | Purpose |
|---|---|---|
| Test user | `tester-rcd-01@<tenant>` | RCD positive / negative tests; clean of any recent interaction with RCD sites |
| Test user | `tester-rss-01@<tenant>` | RSS allowed-list tests; clean of any recent interaction with non-allowed sites |
| Test user | `tester-dlp-01@<tenant>` | DLP-for-Copilot agent-author identity (must hold Copilot Studio author rights) |
| Test user | `tester-other-01@<tenant>` | OneDrive boundary cross-invoker identity (different from publisher) |
| SharePoint site | `spo-rcd-test-001` | Site with RCD enabled; deterministic content set including marker GUID `RCD-MARKER-{cycle-uuid}` |
| SharePoint site | `spo-rcd-test-002` | Site with RCD enabled; second site to verify RCD does not partially apply |
| SharePoint site | `spo-rss-test-001` | Site **on** the RSS allowed-list |
| SharePoint site | `spo-rss-test-002` | Site **off** the RSS allowed-list |
| SharePoint site | `spo-dlp-test-001` | Site whose URL is in scope of the DLP-for-Copilot policy under test |
| SharePoint site | `spo-dlp-test-002` | Site whose URL is **not** in scope of the DLP-for-Copilot policy under test |
| Copilot Studio agent | `agent-z1-grounding-test` | Zone 1 (Personal Productivity) agent fixture |
| Copilot Studio agent | `agent-z2-grounding-test` | Zone 2 (Team Collaboration) agent fixture |
| Copilot Studio agent | `agent-z3-grounding-test` | Zone 3 (Enterprise Managed) agent fixture |
| DLP policy | `dlp-policy-46-test` | Power Platform DLP policy targeting `Microsoft 365 Copilot` location with `spo-dlp-test-001` URL on the blocked list |
| Marker file | `RCD-MARKER-{cycle-uuid}.docx` | Per-cycle deterministic content placed into each RCD site for grounding-citation assertion |
| Marker file | `RSS-MARKER-{cycle-uuid}.docx` | Per-cycle marker for RSS allowed-list tests |
| Marker file | `DLP-MARKER-{cycle-uuid}.docx` | Per-cycle marker for DLP-for-Copilot ingest tests |

Each cycle generates a fresh `{cycle-uuid}` to defeat result caching. Marker files contain a unique sentence ("This is grounding fixture marker `<uuid>` for control 4.6 cycle `<cycle-id>`.") so that a Copilot citation on the marker is unambiguous evidence that the test surface read the test file.

### 2.7 DAG data collection enabled and seasoned

DAG reports require **data-collection enablement** with at minimum 24 hours of activity history before any `4.6-DAG-NN` test will yield non-empty results. Seasoned data (e.g., 7-day history) gives more representative oversharing snapshots. If DAG was enabled less than 24 hours before the cycle, record `4.6-DAG-NN` as `BLOCKED — data not yet seasoned (<24h)`.

The DAG retention model is: ~24 hours from collection enablement to first report population, **28-day rolling activity history**, snapshot reports retained per the SAM tenant settings. Verify against current Learn at every UI-verification cycle.

---

## 3. Documented Processing Windows

Only the following processing windows are Microsoft-documented as of the Last UI Verified date in the header. Anything else is firm-defined and labeled as such.

| Operation | Documented window | Source-of-truth |
|---|---|---|
| RSS allowed-list change to take effect tenant-wide | ~1 hour | Microsoft Learn — Restricted SharePoint Search |
| RCD propagation on a site after enable / disable | Variable; can exceed 1 week on very large sites | Microsoft Learn — Restricted Content Discovery |
| DAG report population after collection enablement | ~24 hours | Microsoft Learn — Data Access Governance |
| DAG activity history window | 28 days rolling | Microsoft Learn — Data Access Governance |
| RBAC role-assignment propagation (Entra) | ~30 minutes typical (firm-defined upper bound) | Firm-defined; cite Microsoft Learn for current Entra propagation guidance |
| UAL ingestion latency (event to searchable) | Up to 24 hours, varies by service (firm-defined upper bound used in tests is 24h) | Microsoft Learn — Audit log search |

**Disclaimer.** Any cadence, latency tolerance, or "expect within X hours" expression in §4 that is not in the table above is **firm-defined** and labeled as such inline. The previous version of this playbook contained a fabricated "24-48 hour" RCD SLA; that value does not appear in Microsoft documentation and must not be reintroduced.

**Interpretation guidance.** A test that runs *during* a documented processing window and reports the surface as not-yet-updated is `INCONCLUSIVE — within published window`, not `FAIL`. A test that runs *after* the upper-bound window and still reports the surface as not-updated is `FAIL`. The §7 attestation must distinguish the two.

---
## 4. Test Catalog

Each test follows the format: **Objective · Preconditions · Steps · Expected · Pass criteria (binary) · Audit assertion · Evidence collected**. Every artifact filename uses the convention defined in §6 and is accompanied by a `.sha256` sidecar.

### 4.6-LIC-01 — License entitlement gate

- **Objective.** Confirm Microsoft 365 Copilot, SAM, and Purview DLP licensing is provisioned at the tenant and on every named test user before any §4 test runs.
- **Preconditions.** `tester-rcd-01`, `tester-rss-01`, `tester-dlp-01`, `tester-other-01` exist; tenant license inventory accessible.
- **Steps.** (1) Connect to Microsoft Graph as a license-reader role. (2) Enumerate `subscribedSkus` and confirm presence of the Copilot, SAM, and Purview DLP SKUs. (3) For each named test user, enumerate `assignedLicenses` and assert the Copilot SKU is present. (4) Persist the full enumeration.
- **Expected.** Tenant carries Copilot + SAM + Purview DLP. Each test user carries Copilot.
- **Pass criteria.** Every named user shows Copilot in `assignedLicenses`; tenant shows SAM and Purview DLP SKUs. Otherwise FAIL and abort cycle.
- **Audit assertion.** Not applicable (license read is not a UAL-emitting operation in itself); record the license report SHA-256 in §6.
- **Evidence.** `4.6-LIC-01-<TENANT>-<UTC>-licenses.json` + `.sha256`.

### 4.6-UAL-01 — Unified Audit Log gate

- **Objective.** Re-assert UAL is enabled and retention covers the longest claim in §1 (7 years).
- **Preconditions.** Connect to Exchange Online as a role with `View-Only Audit Logs`.
- **Steps.** (1) Run `Get-AdminAuditLogConfig | Select UnifiedAuditLogIngestionEnabled`. (2) Enumerate audit retention policies (`Get-UnifiedAuditLogRetentionPolicy`) and capture the policy bodies. (3) Confirm retention ≥ 7 years for the operations claimed in AUDIT-01/02/03.
- **Expected.** UAL ingestion enabled; retention ≥ 7 years for `SharePointSetTenantSettings` family + DLP policy edit operations.
- **Pass criteria.** Both true. Otherwise FAIL and abort cycle.
- **Audit assertion.** Not applicable.
- **Evidence.** `4.6-UAL-01-<TENANT>-<UTC>-ual-state.json` + `.sha256`.

### 4.6-MOD-01 — PowerShell module pin verification

- **Objective.** Record the exact PowerShell module versions used for the cycle so that NEG tests are reproducible against the same surface.
- **Preconditions.** Modules listed in §2.3 installed.
- **Steps.** (1) `Get-Module -ListAvailable Microsoft.Online.SharePoint.PowerShell, PnP.PowerShell, ExchangeOnlineManagement, Microsoft.Graph, Microsoft.PowerApps.Administration.PowerShell | Select Name, Version, Path`. (2) Persist as JSON. (3) Compare against the previous cycle''s pin record; flag any version drift.
- **Expected.** All modules present at GA versions ≥ pinned minimums.
- **Pass criteria.** Every module enumerates with a version meeting the §2.3 minimum.
- **Audit assertion.** Not applicable.
- **Evidence.** `4.6-MOD-01-<TENANT>-<UTC>-modules.json` + `.sha256`.

### 4.6-RCD-01 — RCD enabled-state on configured site list

- **Objective.** Confirm each site that the firm''s policy designates as RCD-restricted has RCD enabled in SPAC.
- **Preconditions.** §2 pre-flight all PASS; firm policy list of RCD-restricted sites versioned in change-control; `spo-rcd-test-001` and `spo-rcd-test-002` on that list.
- **Steps.** (1) Connect SPO Management Shell. (2) For each site on the policy list, read the RCD property (via `Get-SPOSite -Identity <url> -Detailed` or per-site PnP read where the SPO cmdlet does not surface the property). (3) Capture per-site RCD state; assert `True` on every policy-listed site. (4) Persist enumeration.
- **Expected.** Every policy-listed site reports RCD enabled.
- **Pass criteria.** Zero deviations between policy list and observed state. Any site on the policy list with RCD disabled → FAIL.
- **Audit assertion.** UAL contains a `SharePointSetTenantSettings` (or current equivalent — verify the operation name on Microsoft Learn `audit-log-activities`) row for each enable action within the change-control window of record. Operation name stated as illustrative pending verification.
- **Evidence.** `4.6-RCD-01-<TENANT>-<UTC>-rcd-state.json` + `.sha256`; UAL row export `4.6-RCD-01-<TENANT>-<UTC>-ual-rows.json` + `.sha256`.

### 4.6-RCD-02 — Business Chat does not surface RCD-restricted content

- **Objective.** Confirm Microsoft 365 Copilot chat / Business Chat does not cite content from `spo-rcd-test-001` for an identity (`tester-rcd-01`) who has no recent interaction with the site.
- **Preconditions.** `4.6-RCD-01` PASS; marker file `RCD-MARKER-{cycle-uuid}.docx` placed on `spo-rcd-test-001` at least one published RCD-propagation window before this test runs (see §3 — note that for very large sites, the upper bound is "more than a week").
- **Steps.** (1) Sign in as `tester-rcd-01` to `microsoft365.com/chat`. (2) Issue a deterministic prompt that names the marker GUID: "Find the document that contains the marker `RCD-MARKER-{cycle-uuid}` and quote the marker sentence." (3) Capture the full Copilot response including any citation chips. (4) Persist response transcript and screenshot.
- **Expected.** Copilot does not return the marker sentence or cite `spo-rcd-test-001`.
- **Pass criteria.** Marker sentence absent **and** no citation to any URL on `spo-rcd-test-001`.
- **Audit assertion.** Capture the Copilot interaction audit row (Microsoft 365 Copilot interaction event); confirm event records that grounding sources excluded the RCD site (or, equivalently, that no citation row references the RCD site).
- **Evidence.** `4.6-RCD-02-<TENANT>-<UTC>-bizchat-transcript.json` + screenshot `.png` + `.sha256` for each.

### 4.6-RCD-03 — Tenant search does not return RCD-restricted content

- **Objective.** Confirm SharePoint tenant search does not return content from `spo-rcd-test-001` for `tester-rcd-01`.
- **Preconditions.** `4.6-RCD-01` PASS; marker file present on `spo-rcd-test-001` past the RCD-propagation window.
- **Steps.** (1) Sign in as `tester-rcd-01` to `<tenant>.sharepoint.com/_layouts/15/sharepoint.aspx`. (2) Issue a search query for `RCD-MARKER-{cycle-uuid}`. (3) Capture the result page including total-results count and any per-site facets. (4) Persist screenshot and HTML snapshot.
- **Expected.** Zero results returned; no `spo-rcd-test-001` facet present.
- **Pass criteria.** Result count = 0 and no facet listing the RCD-restricted site.
- **Audit assertion.** Optionally capture `SearchQueryPerformed` UAL row (operation name illustrative) for traceability of the test query.
- **Evidence.** `4.6-RCD-03-<TENANT>-<UTC>-search-results.html` + screenshot `.png` + `.sha256`.

### 4.6-RCD-04 — RCD does not partially apply across multiple sites

- **Objective.** Confirm RCD enablement on `spo-rcd-test-001` is independent of `spo-rcd-test-002`; both must individually report enabled.
- **Preconditions.** Both sites on the firm''s RCD policy list.
- **Steps.** (1) Read RCD property on `spo-rcd-test-001` and `spo-rcd-test-002` independently. (2) Assert both are enabled. (3) Persist combined enumeration.
- **Expected.** Both sites enabled; no implicit "tenant RCD" flag substituting for per-site enable.
- **Pass criteria.** Both report `True` independently.
- **Audit assertion.** Cross-reference UAL rows from `4.6-RCD-01`.
- **Evidence.** `4.6-RCD-04-<TENANT>-<UTC>-rcd-pair-state.json` + `.sha256`.

### 4.6-RCD-05 — RCD removal evidenced through change-control

- **Objective.** Confirm any site removed from the RCD list since the previous cycle has a corresponding change-control ticket and a UAL row evidencing the removal.
- **Preconditions.** Previous-cycle RCD enumeration persisted in §6 evidence repository.
- **Steps.** (1) Diff current `4.6-RCD-01` enumeration against the previous-cycle enumeration. (2) For each site removed, capture (a) the change-control ticket reference and approver, (b) the UAL row evidencing the removal, (c) the business justification.
- **Expected.** Every removal is paired with ticket + UAL row + justification.
- **Pass criteria.** Zero unexplained removals.
- **Audit assertion.** UAL row of operation that disabled RCD; tie to ticket via `Date`/`UserId` correlation.
- **Evidence.** `4.6-RCD-05-<TENANT>-<UTC>-rcd-removals-with-evidence.json` + `.sha256`.

### 4.6-RCD-06 — RCD scope-of-applicability statement (NOT-A-TOTAL-CONTROL)

- **Objective.** Produce the regulator-facing statement that records what RCD does and does not do, so that examiners receive the same scope statement under FINRA 25-07 every cycle.
- **Preconditions.** All RCD tests above PASS or have explained gaps.
- **Steps.** Author the statement using the boilerplate in [Portal Walkthrough §RCD scope statement](portal-walkthrough.md), customized with the cycle date, the count of RCD-enabled sites, and the count of in-app carve-out tests passed (`4.6-INAPP-NN`).
- **Expected.** A signed statement that explicitly says: RCD scopes Microsoft 365 Copilot chat / Business Chat and tenant search; RCD does **not** scope in-app Word/Excel/PowerPoint Copilot when the user has the file open; RCD does **not** apply to personal OneDrive; RCD propagation can exceed 1 week on very large sites.
- **Pass criteria.** Statement signed by AI Governance Lead; SHA-256 captured.
- **Audit assertion.** None; statement is the artifact.
- **Evidence.** `4.6-RCD-06-<TENANT>-<UTC>-rcd-scope-statement.pdf` + `.sha256`.
### 4.6-RSS-01 — RSS allowed-list state

- **Objective.** Confirm the RSS allowed-list is enabled and contains exactly the sites in the firm''s RSS policy list (no more, no fewer; ≤ 100 entries per Microsoft documented limit).
- **Preconditions.** §2 pre-flight all PASS; firm RSS policy list versioned in change-control with `spo-rss-test-001` on the list.
- **Steps.** (1) `Get-SPOTenantRestrictedSearchAllowedList`. (2) Capture the full list and its size. (3) Diff against the firm policy list.
- **Expected.** Exact match between observed allowed-list and policy list; count ≤ 100.
- **Pass criteria.** Zero deviations and count within limit.
- **Audit assertion.** UAL row from `SharePointSetTenantSettings` family for the most recent RSS edit (operation name illustrative pending Learn verification).
- **Evidence.** `4.6-RSS-01-<TENANT>-<UTC>-rss-allowed-list.json` + `.sha256`.

### 4.6-RSS-02 — RSS positive case (allowed-list site is searchable by clean identity)

- **Objective.** Confirm `tester-rss-01` (clean of recent interaction with `spo-rss-test-001`) can locate the RSS marker on the allowed-list site via tenant search.
- **Preconditions.** RSS-MARKER placed on `spo-rss-test-001`; ~1 hour past RSS take-effect window (§3); tester-rss-01 has had no interaction with the site.
- **Steps.** (1) Sign in as `tester-rss-01`. (2) Search tenant for `RSS-MARKER-{cycle-uuid}`. (3) Capture results.
- **Expected.** Marker located on `spo-rss-test-001`.
- **Pass criteria.** Result count ≥ 1 and includes `spo-rss-test-001`.
- **Audit assertion.** Optional `SearchQueryPerformed` capture.
- **Evidence.** `4.6-RSS-02-<TENANT>-<UTC>-rss-positive-results.html` + screenshot + `.sha256`.

### 4.6-RSS-03 — RSS negative case (off-list site not searchable by clean identity)

- **Objective.** Confirm `tester-rss-01` cannot locate the RSS marker on `spo-rss-test-002` (which is off the allowed-list).
- **Preconditions.** RSS-MARKER placed on `spo-rss-test-002`; ~1 hour past take-effect; tester-rss-01 has had no interaction with the site, never owned it, never had the file directly shared.
- **Steps.** (1) Sign in as `tester-rss-01`. (2) Search for `RSS-MARKER-{cycle-uuid}`. (3) Capture results.
- **Expected.** Marker not surfaced from `spo-rss-test-002`.
- **Pass criteria.** Result count = 0 from `spo-rss-test-002`.
- **Audit assertion.** Optional `SearchQueryPerformed` capture.
- **Evidence.** `4.6-RSS-03-<TENANT>-<UTC>-rss-negative-results.html` + screenshot + `.sha256`.

### 4.6-RSS-04 — RSS recent-interaction carve-out is acknowledged

- **Objective.** Confirm — and **document** — that an identity with recent interaction with `spo-rss-test-002` *will* surface content from it via Copilot chat / search, because RSS is not a security boundary.
- **Preconditions.** Use a separate carve-out identity (not `tester-rss-01`) that has owned, recently accessed, or had a direct share of `spo-rss-test-002`.
- **Steps.** (1) Sign in as the carve-out identity. (2) Search for `RSS-MARKER-{cycle-uuid}`. (3) Capture results.
- **Expected.** Marker **does** surface for the carve-out identity.
- **Pass criteria.** Result count ≥ 1 from `spo-rss-test-002`. (This is an acknowledgment test: the surface is documented to behave this way.)
- **Audit assertion.** None; this test confirms documented behavior.
- **Evidence.** `4.6-RSS-04-<TENANT>-<UTC>-rss-carveout-results.html` + `.sha256`; **operational note** capturing that RSS is not a record-isolation control.

### 4.6-RSS-05 — RSS NOT-A-BOUNDARY attestation

- **Objective.** Produce the regulator-facing statement that RSS is *not* a security boundary, *not* a substitute for record retention, and is positioned by Microsoft as a short-term containment lever while site-permissions remediation proceeds.
- **Preconditions.** `4.6-RSS-01` through `4.6-RSS-04` completed.
- **Steps.** Author the statement using the boilerplate in [Portal Walkthrough §RSS not-a-boundary](portal-walkthrough.md), citing the carve-out evidence from `4.6-RSS-04`.
- **Expected.** Signed statement.
- **Pass criteria.** Statement signed by AI Governance Lead; SHA-256 captured.
- **Audit assertion.** None.
- **Evidence.** `4.6-RSS-05-<TENANT>-<UTC>-rss-boundary-statement.pdf` + `.sha256`.

### 4.6-DLP-01 — DLP-for-Copilot policy state

- **Objective.** Confirm `dlp-policy-46-test` exists, is in the **Enabled** state (not test-only), and scopes the `Microsoft 365 Copilot` location with `spo-dlp-test-001` URL on the blocked list.
- **Preconditions.** §2 pre-flight all PASS; Power Platform / Purview connection authenticated.
- **Steps.** (1) Enumerate DLP policies via `Get-AdminDlpPolicy` (Power Platform admin module) **and** via the Purview equivalent. (2) Capture the policy body for `dlp-policy-46-test`. (3) Assert state = Enabled and confirm `spo-dlp-test-001` URL on the blocked list within `Microsoft 365 Copilot` location scope.
- **Expected.** Policy enabled with the test URL blocked.
- **Pass criteria.** Both true.
- **Audit assertion.** UAL row evidencing the most recent policy edit (operation name illustrative; verify on Learn).
- **Evidence.** `4.6-DLP-01-<TENANT>-<UTC>-dlp-policy-state.json` + `.sha256`.

### 4.6-DLP-02 — DLP blocks SharePoint URL ingest as Copilot Studio knowledge source

- **Objective.** Confirm a Copilot Studio agent author (`tester-dlp-01`) attempting to add `spo-dlp-test-001` URL as a knowledge source is blocked by `dlp-policy-46-test`.
- **Preconditions.** `4.6-DLP-01` PASS; Copilot Studio author rights granted to `tester-dlp-01`.
- **Steps.** (1) Sign in as `tester-dlp-01` to Copilot Studio. (2) Open `agent-z2-grounding-test`. (3) Add a SharePoint knowledge source pointing at `spo-dlp-test-001`. (4) Capture the rejection toast / error message and any inline policy reference. (5) Persist screenshot and the network response if accessible via dev-tools capture.
- **Expected.** Ingest blocked with a policy reference message.
- **Pass criteria.** URL not added; explicit block message captured.
- **Audit assertion.** UAL row for the policy-block event in the Power Platform audit stream (operation name illustrative pending Learn verification).
- **Evidence.** `4.6-DLP-02-<TENANT>-<UTC>-dlp-block-screenshot.png` + transcript JSON + `.sha256`.

### 4.6-DLP-03 — DLP allows non-blocked URL ingest (positive case)

- **Objective.** Confirm `tester-dlp-01` can add `spo-dlp-test-002` URL (off the blocked list) as a knowledge source — i.e., the DLP policy is not over-restricting.
- **Preconditions.** `4.6-DLP-01` PASS; `spo-dlp-test-002` not in any DLP-for-Copilot block list.
- **Steps.** (1) Sign in as `tester-dlp-01`. (2) Open `agent-z2-grounding-test`. (3) Add `spo-dlp-test-002` as a knowledge source. (4) Capture success.
- **Expected.** Ingest succeeds.
- **Pass criteria.** Knowledge source added; agent able to ground on `DLP-MARKER-{cycle-uuid}` placed on the site.
- **Audit assertion.** UAL row for the knowledge-source add operation.
- **Evidence.** `4.6-DLP-03-<TENANT>-<UTC>-dlp-positive.png` + transcript + `.sha256`.

### 4.6-DLP-04 — DLP-for-Copilot is the canonical knowledge-source block mechanism

- **Objective.** Produce the regulator-facing statement that explicitly identifies DLP-for-Copilot as the **only** mechanism that blocks a SharePoint URL from being added as a Copilot Studio knowledge source — RCD and RSS do not produce that effect.
- **Preconditions.** `4.6-DLP-01..03` completed.
- **Steps.** Author the statement using the boilerplate, citing the test results.
- **Expected.** Signed statement.
- **Pass criteria.** Statement signed; SHA-256 captured.
- **Audit assertion.** None.
- **Evidence.** `4.6-DLP-04-<TENANT>-<UTC>-dlp-canonical-statement.pdf` + `.sha256`.
### 4.6-DAG-01 — DAG oversharing snapshot extracted

- **Objective.** Pull the current DAG oversharing snapshot for sites in scope of Control 4.6 and persist as evidence.
- **Preconditions.** §2.7 PASS (DAG enabled and seasoned ≥ 24h).
- **Steps.** (1) Open SPAC → Reports → Data Access Governance. (2) Run the oversharing report scoped to the in-scope sites. (3) Export to CSV / JSON. (4) Persist with SHA-256.
- **Expected.** Report generates with non-empty rows for sites that have any sharing activity.
- **Pass criteria.** Report produced; row count recorded; week-over-week delta computed.
- **Audit assertion.** Report run is recorded in DAG telemetry; capture report metadata.
- **Evidence.** `4.6-DAG-01-<TENANT>-<UTC>-oversharing-snapshot.json` + `.sha256`.

### 4.6-DAG-02 — DAG sharing-links and sensitivity-label coverage extracted

- **Objective.** Pull the DAG sharing-links and sensitivity-label coverage reports for in-scope sites.
- **Preconditions.** §2.7 PASS.
- **Steps.** (1) Open the sharing-links report; export. (2) Open the sensitivity-label coverage report; export. (3) Persist both with SHA-256.
- **Expected.** Both reports generate.
- **Pass criteria.** Both reports produced.
- **Audit assertion.** Capture report metadata.
- **Evidence.** `4.6-DAG-02-<TENANT>-<UTC>-sharing-links.json` + `.sha256`; `4.6-DAG-02-<TENANT>-<UTC>-label-coverage.json` + `.sha256`.

### 4.6-DAG-03 — DAG findings reviewed and tracked

- **Objective.** Confirm that DAG findings from `4.6-DAG-01` and `4.6-DAG-02` were reviewed by the AI Governance Lead and that any over-threshold findings have remediation tickets.
- **Preconditions.** `4.6-DAG-01` and `4.6-DAG-02` PASS; firm threshold defined (e.g., > 25% week-over-week increase in oversharing-link count for `Confidential`+ sites is firm-defined as a remediation trigger).
- **Steps.** (1) AI Governance Lead reviews the snapshots. (2) Generate an exception list of sites breaching firm thresholds. (3) For each, attach the remediation ticket reference. (4) Persist the review record.
- **Expected.** Every breach has a ticket.
- **Pass criteria.** Zero unticketed breaches.
- **Audit assertion.** None (this is a process artifact).
- **Evidence.** `4.6-DAG-03-<TENANT>-<UTC>-dag-review.json` + `.sha256`.

### 4.6-OND-01 — Personal OneDrive boundary (RCD scope statement)

- **Objective.** Produce the regulator-facing statement that RCD does **not** apply to personal OneDrive, and document the firm''s alternative controls for OneDrive content (sensitivity labels, DLP, retention).
- **Preconditions.** `4.6-RCD-06` produced.
- **Steps.** Author the statement; cite Microsoft Learn for the OneDrive carve-out.
- **Expected.** Signed statement.
- **Pass criteria.** Statement signed; SHA-256 captured.
- **Audit assertion.** None.
- **Evidence.** `4.6-OND-01-<TENANT>-<UTC>-onedrive-scope-statement.pdf` + `.sha256`.

### 4.6-OND-02 — Cross-invoker OneDrive boundary on Copilot Studio agent

- **Objective.** Confirm a Copilot Studio agent (`agent-z2-grounding-test`) configured by `tester-dlp-01` does not surface `tester-dlp-01`''s personal OneDrive content to a different invoker (`tester-other-01`).
- **Preconditions.** Marker file placed on `tester-dlp-01`''s OneDrive (not shared with `tester-other-01`); agent published with default OneDrive grounding posture per firm policy.
- **Steps.** (1) Sign in as `tester-other-01`. (2) Invoke `agent-z2-grounding-test`. (3) Issue a deterministic prompt that names the OneDrive marker. (4) Capture response.
- **Expected.** Marker not surfaced; no citation to `tester-dlp-01`''s OneDrive.
- **Pass criteria.** Marker absent; no citation.
- **Audit assertion.** Capture Copilot Studio interaction audit row evidencing the invocation.
- **Evidence.** `4.6-OND-02-<TENANT>-<UTC>-onedrive-cross-invoker.json` + screenshot + `.sha256`.

### 4.6-INAPP-01 — In-app Word Copilot carve-out (DOCUMENTED behavior)

- **Objective.** Confirm — and **document** — that opening the RCD-restricted marker file in Word and invoking Copilot summarization succeeds. RCD does **not** scope in-app Copilot when the user has the file open via direct permission.
- **Preconditions.** `RCD-MARKER-{cycle-uuid}.docx` on `spo-rcd-test-001`; `tester-rcd-01` has direct permission to the marker file (independent of search/chat scope).
- **Steps.** (1) Sign in as `tester-rcd-01`. (2) Open the marker file in Word for the web. (3) Invoke Copilot → Summarize. (4) Capture the summary text. (5) Persist transcript + screenshot.
- **Expected.** Copilot returns a meaningful summary including the marker sentence.
- **Pass criteria.** Summary returned and references marker content. **Failure to return content is the abnormal result here.**
- **Audit assertion.** Capture the Microsoft 365 Copilot interaction audit row evidencing the in-app invocation against the marker file.
- **Evidence.** `4.6-INAPP-01-<TENANT>-<UTC>-inapp-word.json` + screenshot + `.sha256`. **This artifact is the canonical evidence that in-app Copilot is the carve-out — do not interpret as an RCD failure.**

### 4.6-INAPP-02 — In-app carve-out scope statement

- **Objective.** Produce the regulator-facing statement that the in-app Copilot carve-out is documented Microsoft behavior and is **expected** to PASS in the affirmative direction. Anti-pattern note in §8 cross-references this test.
- **Preconditions.** `4.6-INAPP-01` PASS in the affirmative direction.
- **Steps.** Author the statement using the boilerplate, cite `4.6-INAPP-01` evidence.
- **Expected.** Signed statement.
- **Pass criteria.** Statement signed; SHA-256 captured.
- **Audit assertion.** None.
- **Evidence.** `4.6-INAPP-02-<TENANT>-<UTC>-inapp-carveout-statement.pdf` + `.sha256`.

### 4.6-AUDIT-01 — Tenant-settings change audit (monthly diff)

- **Objective.** Extract the rolling 30-day window of `SharePointSetTenantSettings` family rows (operation name illustrative — verify on Learn `audit-log-activities` at every UI cycle) and confirm every row maps to a change-control ticket.
- **Preconditions.** `4.6-UAL-01` PASS.
- **Steps.** (1) `Search-UnifiedAuditLog` over the prior 30 days for the operation family. (2) Persist rows. (3) Reconcile against change-control system; flag unticketed rows.
- **Expected.** Every change row has a ticket.
- **Pass criteria.** Zero unticketed changes.
- **Audit assertion.** Operations include RCD enable/disable, RSS allowed-list edits, and other tenant-settings operations relevant to grounding scope.
- **Evidence.** `4.6-AUDIT-01-<TENANT>-<UTC>-tenant-settings-rows.json` + reconciliation `.json` + `.sha256`.

### 4.6-AUDIT-02 — DLP-for-Copilot policy edit audit

- **Objective.** Extract the rolling 30-day window of DLP-for-Copilot policy edit rows (Power Platform audit stream) and confirm every row maps to a ticket.
- **Preconditions.** `4.6-UAL-01` PASS.
- **Steps.** (1) Pull Power Platform DLP audit rows for the prior 30 days. (2) Persist. (3) Reconcile against change-control.
- **Expected.** Every edit ticketed.
- **Pass criteria.** Zero unticketed edits.
- **Audit assertion.** Operation names captured against current Learn (illustrative pending verification).
- **Evidence.** `4.6-AUDIT-02-<TENANT>-<UTC>-dlp-edit-rows.json` + `.sha256`.

### 4.6-AUDIT-03 — Audit-pack assembly and review

- **Objective.** Assemble the per-cycle audit pack (everything in §6) and route to the Compliance Officer for review and sign-off.
- **Preconditions.** All §4 tests above completed.
- **Steps.** (1) Run the §6 manifest generator. (2) Verify every artifact has a SHA-256 sidecar. (3) Generate the audit-pack PDF cover-sheet. (4) Route to Compliance Officer.
- **Expected.** Audit pack assembled and signed.
- **Pass criteria.** Cover-sheet signed; manifest validates.
- **Audit assertion.** None (the artifact is the assertion).
- **Evidence.** `4.6-AUDIT-03-<TENANT>-<UTC>-audit-pack-coversheet.pdf` + manifest JSON + `.sha256`.
### 4.6-NEG-01 — `Get-SPOTenant` schema-presence assertion

- **Objective.** Defend against silent NEG passes caused by SPO Management Shell schema drift. Assert that every property the RCD/RSS tests rely on is present on the returned object before asserting its value.
- **Preconditions.** §2.3 module pin recorded.
- **Steps.** (1) Run `Get-SPOTenant`. (2) For each property name the test catalog reads (e.g., RSS-related and RCD-related properties currently exposed at the tenant level), assert `(@($obj.PSObject.Properties.Name) -contains '<name>')` is `$true` *before* reading the value. (3) Record the property-presence map.
- **Expected.** Every relied-on property present on the cycle''s pinned module version.
- **Pass criteria.** Zero missing properties; if any property is missing, the test family that depends on it is recorded as `BLOCKED — schema drift` and an upstream issue is opened.
- **Audit assertion.** None (this is a test-harness assertion).
- **Evidence.** `4.6-NEG-01-<TENANT>-<UTC>-spo-tenant-schema.json` + `.sha256`.

### 4.6-NEG-02 — `Get-SPOTenantRestrictedSearchAllowedList` schema-presence assertion

- **Objective.** As `4.6-NEG-01` for the RSS-allowed-list cmdlet output shape.
- **Preconditions.** §2.3 module pin recorded.
- **Steps.** Same property-presence pattern; assert the cmdlet returns the documented shape; assert count ≤ 100.
- **Expected.** Documented shape returned.
- **Pass criteria.** Shape matches; otherwise BLOCK and open upstream issue.
- **Audit assertion.** None.
- **Evidence.** `4.6-NEG-02-<TENANT>-<UTC>-rss-allowed-schema.json` + `.sha256`.

### 4.6-NEG-03 — DLP-for-Copilot policy enumeration shape assertion

- **Objective.** Assert that the Power Platform DLP enumeration response includes the property names the DLP tests rely on, and that policy bodies serialize with the in-scope `Microsoft 365 Copilot` location key present.
- **Preconditions.** §2.3 pin includes `Microsoft.PowerApps.Administration.PowerShell` at the recorded version.
- **Steps.** (1) Enumerate DLP policies. (2) Assert each policy body contains the location-scope key required by the tests. (3) Persist shape report.
- **Expected.** Documented shape.
- **Pass criteria.** Shape matches.
- **Audit assertion.** None.
- **Evidence.** `4.6-NEG-03-<TENANT>-<UTC>-dlp-shape.json` + `.sha256`.

### 4.6-NEG-04 — Cycle-bracket negative test (no leakage between RCD-restricted site and Business Chat for unrelated identity)

- **Objective.** Defend against test-fixture cross-contamination by running a final negative pass: a *second* clean identity (`tester-other-01`) issues the RCD marker query against Business Chat at the end of the cycle. The marker must remain absent.
- **Preconditions.** All RCD tests above completed; `tester-other-01` clean of any interaction with `spo-rcd-test-001`.
- **Steps.** (1) Sign in as `tester-other-01`. (2) Issue the marker query at `microsoft365.com/chat`. (3) Capture transcript.
- **Expected.** Marker absent and no citation to `spo-rcd-test-001`.
- **Pass criteria.** Marker absent; no citation.
- **Audit assertion.** Capture the Microsoft 365 Copilot interaction audit row.
- **Evidence.** `4.6-NEG-04-<TENANT>-<UTC>-bracket-bizchat.json` + screenshot + `.sha256`.

### 4.6-IR-01 — Grounding-scope incident response dry-run

- **Objective.** Run a tabletop dry-run of the grounding-scope incident response flow (per the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)) using a fabricated incident: "Business Chat surfaced content from `spo-rcd-test-001` to `tester-rcd-01` at `<UTC>`." Time-box to 2 hours.
- **Preconditions.** AI Incident Response Playbook current; on-call roster current; SPAC + PPAC + Purview write-access on-call established.
- **Steps.** (1) Page on-call. (2) Triage: confirm RCD enabled (re-run `4.6-RCD-01` ad-hoc). (3) If RCD not enabled, enable; if RCD enabled, capture the marker citation as evidence and escalate per playbook. (4) Capture the timeline (page → triage → containment → root-cause → close) with UTC timestamps. (5) Persist tabletop minutes.
- **Expected.** Tabletop completes within time-box; every role engaged; gaps logged.
- **Pass criteria.** Tabletop completed and minuted; AI Governance Lead + Risk Officer signed minutes.
- **Audit assertion.** None (tabletop artifact is the evidence).
- **Evidence.** `4.6-IR-01-<TENANT>-<UTC>-tabletop-minutes.pdf` + `.sha256`.

---

## 5. Sovereign-Cloud Variant Matrix

The matrix below records, for each test family, the availability and any execution variation across Commercial, GCC, GCC High, and DoD as of the Last UI Verified date in the header. **Verify each row against current Microsoft Learn at every UI-verification cycle.** Where a mechanism is unavailable in a sovereign cloud, the corresponding test rows are recorded as `N/A — sovereign non-parity` in the §7 attestation, not `FAIL`.

| Test family | Commercial | GCC | GCC High | DoD | Notes |
|---|---|---|---|---|---|
| LIC-01 | ✅ Run | ✅ Run | ✅ Run (verify SAM SKU on Learn) | ✅ Run (verify SAM SKU on Learn) | License catalogs differ across clouds |
| UAL-01 | ✅ Run | ✅ Run | ✅ Run | ✅ Run | UAL retention SKUs may differ |
| MOD-01 | ✅ Run | ✅ Run | ✅ Run | ✅ Run | Module endpoints differ; record GCC-prefixed endpoint URLs in pin record |
| RCD-01..06 | ✅ Run | ⚠ Verify availability on Learn before run | ⚠ Non-parity windows; verify on Learn | ⚠ Non-parity windows; verify on Learn | RCD availability in US Gov clouds has historically lagged Commercial |
| RSS-01..05 | ✅ Run | ⚠ Verify on Learn | ⚠ Non-parity; verify on Learn | ⚠ Non-parity; verify on Learn | RSS rollout to US Gov clouds has historically lagged Commercial |
| DLP-01..04 | ✅ Run | ⚠ Verify Power Platform DLP `Microsoft 365 Copilot` location availability | ⚠ Non-parity; verify on Learn | ⚠ Non-parity; verify on Learn | DLP-for-Copilot location-scope availability differs |
| DAG-01..03 | ✅ Run | ⚠ Verify SAM/DAG availability on Learn | ⚠ Non-parity; verify | ⚠ Non-parity; verify | DAG depends on SAM availability |
| OND-01..02 | ✅ Run | ✅ Run (verify Copilot Studio availability) | ⚠ Verify Copilot Studio sovereign availability on Learn | ⚠ Verify Copilot Studio sovereign availability on Learn | Copilot Studio sovereign availability is the gating factor |
| INAPP-01..02 | ✅ Run | ⚠ Verify in-app Copilot availability on Learn | ⚠ Verify | ⚠ Verify | In-app Copilot availability differs by app and cloud |
| AUDIT-01..03 | ✅ Run | ✅ Run | ✅ Run | ✅ Run | Verify operation names on Learn at every cycle |
| NEG-01..04 | ✅ Run | ✅ Run | ✅ Run | ✅ Run | Module endpoint URLs differ |
| IR-01 | ✅ Run | ✅ Run | ✅ Run | ✅ Run | Roster and on-call procedures may differ by cloud |

**Sovereign exception path.** A test marked `⚠ Verify on Learn` that turns out unavailable: (a) record `N/A — sovereign non-parity` with the Learn URL and access date, (b) document the firm''s compensating control in §7 attestation (e.g., manual periodic search exfiltration probe in lieu of RSS allowed-list; sensitivity-label DLP for SharePoint URL ingest in lieu of DLP-for-Copilot), (c) reassess at next UI-verification cycle.

**GCC connector payload.** GCC connector payload limit is ~450KB; if any custom telemetry pipeline pushes evidence to a GCC connector, partition payloads accordingly. This affects the §6 evidence-pack assembly path on GCC tenants.

---
## 6. Evidence Pack

### 6.1 File-naming convention

Every artifact filename uses the form:

```
4.6-<TestID>-<TENANT>-<UTC-yyyyMMddTHHmmssZ>-<descriptor>.<ext>
```

Each artifact has a paired SHA-256 sidecar with the same base name and `.sha256` extension. Sidecars contain a single line: the lowercase hex SHA-256 followed by two spaces and the artifact filename, matching the Linux `sha256sum` format (this is the format expected by the §6.3 PowerShell validator).

### 6.2 Manifest JSON schema

Every cycle emits a `manifest.json` at the cycle-output root. The manifest is itself hashed and the hash is countersigned by the Compliance Officer in §7.

```json
{
  "control_id": "4.6",
  "control_name": "Grounding Scope Governance",
  "cycle_id": "<uuid>",
  "tenant_id": "<tenant-guid>",
  "tenant_cloud": "Commercial | GCC | GCCH | DoD",
  "cycle_started_utc": "2026-04-15T13:00:00Z",
  "cycle_completed_utc": "2026-04-15T17:30:00Z",
  "two_portal_delta_seconds": 612,
  "module_versions": {
    "Microsoft.Online.SharePoint.PowerShell": "16.0.x",
    "PnP.PowerShell": "2.x",
    "ExchangeOnlineManagement": "3.x",
    "Microsoft.Graph": "2.x",
    "Microsoft.PowerApps.Administration.PowerShell": "2.x"
  },
  "tester": "alice@<tenant>",
  "reviewer": "bob@<tenant>",
  "approver": "carol@<tenant>",
  "tests": [
    {
      "test_id": "4.6-RCD-01",
      "status": "PASS | FAIL | INCONCLUSIVE | BLOCKED | N/A",
      "started_utc": "2026-04-15T13:05:12Z",
      "completed_utc": "2026-04-15T13:08:44Z",
      "evidence": [
        {
          "filename": "4.6-RCD-01-CONTOSO-20260415T130812Z-rcd-state.json",
          "sha256": "<hex>",
          "size_bytes": 12480
        }
      ],
      "notes": "All 14 policy-list sites enabled. UAL rows reconciled."
    }
  ],
  "exceptions": [
    {
      "test_id": "4.6-DLP-02",
      "status": "N/A — sovereign non-parity",
      "compensating_control": "Manual quarterly knowledge-source ingest review by Purview Compliance Admin",
      "learn_url": "https://learn.microsoft.com/...",
      "learn_access_date": "2026-04-15"
    }
  ],
  "manifest_sha256": "<hex of this file with the manifest_sha256 field zeroed during compute>",
  "compliance_officer_signature": "<DocuSign envelope id or equivalent>"
}
```

### 6.3 PowerShell validator

A reference validator MUST be run before the manifest is signed. It (a) re-computes every artifact''s SHA-256 and confirms the sidecar matches, (b) confirms every test row in the manifest references an artifact present on disk, (c) confirms `cycle_completed_utc > cycle_started_utc`, (d) confirms `two_portal_delta_seconds <= 900`, and (e) confirms required test IDs are all represented (LIC-01, UAL-01, MOD-01, RCD-01..06, RSS-01..05, DLP-01..04, DAG-01..03, OND-01..02, INAPP-01..02, AUDIT-01..03, NEG-01..04, IR-01).

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $CyclePath
)

# Follows _shared/powershell-baseline.md authoring rules:
# - Set-StrictMode, ErrorActionPreference, no [void] discards on objects we want to inspect.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$manifestPath = Join-Path $CyclePath 'manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "manifest.json not found at $manifestPath"
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

$required = @(
    '4.6-LIC-01','4.6-UAL-01','4.6-MOD-01',
    '4.6-RCD-01','4.6-RCD-02','4.6-RCD-03','4.6-RCD-04','4.6-RCD-05','4.6-RCD-06',
    '4.6-RSS-01','4.6-RSS-02','4.6-RSS-03','4.6-RSS-04','4.6-RSS-05',
    '4.6-DLP-01','4.6-DLP-02','4.6-DLP-03','4.6-DLP-04',
    '4.6-DAG-01','4.6-DAG-02','4.6-DAG-03',
    '4.6-OND-01','4.6-OND-02',
    '4.6-INAPP-01','4.6-INAPP-02',
    '4.6-AUDIT-01','4.6-AUDIT-02','4.6-AUDIT-03',
    '4.6-NEG-01','4.6-NEG-02','4.6-NEG-03','4.6-NEG-04',
    '4.6-IR-01'
)

$present = @($manifest.tests | ForEach-Object { $_.test_id })
$missing = @($required | Where-Object { $present -notcontains $_ })
if ($missing.Count -gt 0) {
    throw ("Missing required test IDs: {0}" -f ($missing -join ', '))
}

if ($manifest.two_portal_delta_seconds -gt 900) {
    throw ("Two-portal capture delta {0}s exceeds 900s" -f $manifest.two_portal_delta_seconds)
}

$started   = [datetime]::Parse($manifest.cycle_started_utc).ToUniversalTime()
$completed = [datetime]::Parse($manifest.cycle_completed_utc).ToUniversalTime()
if ($completed -le $started) {
    throw "cycle_completed_utc must be later than cycle_started_utc"
}

$mismatches = New-Object System.Collections.Generic.List[string]
foreach ($t in $manifest.tests) {
    foreach ($e in $t.evidence) {
        $artifact = Join-Path $CyclePath $e.filename
        if (-not (Test-Path -LiteralPath $artifact)) {
            $mismatches.Add("MISSING: $($e.filename)") | Out-Null
            continue
        }
        $observed = (Get-FileHash -Algorithm SHA256 -LiteralPath $artifact).Hash.ToLowerInvariant()
        if ($observed -ne $e.sha256.ToLowerInvariant()) {
            $mismatches.Add("HASH MISMATCH: $($e.filename)") | Out-Null
        }
        $sidecar = "$artifact.sha256"
        if (-not (Test-Path -LiteralPath $sidecar)) {
            $mismatches.Add("MISSING SIDECAR: $($e.filename).sha256") | Out-Null
        }
    }
}

if ($mismatches.Count -gt 0) {
    throw ("Manifest validation failed:`n - {0}" -f ($mismatches -join "`n - "))
}

Write-Host "Manifest validates: $($manifest.tests.Count) tests, $($manifest.exceptions.Count) exceptions."
```

### 6.4 Artifacts table

| Artifact | Source test | Format | Retention |
|---|---|---|---|
| `licenses.json` | 4.6-LIC-01 | JSON | 7 years (SOX 404) |
| `ual-state.json` | 4.6-UAL-01 | JSON | 7 years |
| `modules.json` | 4.6-MOD-01 | JSON | 3 years |
| `rcd-state.json` + UAL rows | 4.6-RCD-01..05 | JSON | 6 years (FINRA 4511) |
| `rcd-scope-statement.pdf` | 4.6-RCD-06 | PDF | 6 years |
| `rss-allowed-list.json` + result HTML/PNG | 4.6-RSS-01..04 | JSON / HTML / PNG | 6 years |
| `rss-boundary-statement.pdf` | 4.6-RSS-05 | PDF | 6 years |
| `dlp-policy-state.json` + block / positive screenshots | 4.6-DLP-01..03 | JSON / PNG | 6 years + 7 years |
| `dlp-canonical-statement.pdf` | 4.6-DLP-04 | PDF | 6 years + 7 years |
| `oversharing-snapshot.json`, `sharing-links.json`, `label-coverage.json`, `dag-review.json` | 4.6-DAG-01..03 | JSON | 6 years |
| `onedrive-scope-statement.pdf`, `onedrive-cross-invoker.json` | 4.6-OND-01..02 | PDF / JSON | 6 years |
| `inapp-word.json` + screenshot, `inapp-carveout-statement.pdf` | 4.6-INAPP-01..02 | JSON / PNG / PDF | 6 years |
| `tenant-settings-rows.json`, `dlp-edit-rows.json`, `audit-pack-coversheet.pdf` | 4.6-AUDIT-01..03 | JSON / PDF | 7 years |
| `*-schema.json`, `bracket-bizchat.json` | 4.6-NEG-01..04 | JSON | 6 years |
| `tabletop-minutes.pdf` | 4.6-IR-01 | PDF | 7 years |
| `manifest.json` (cycle root) | All | JSON | Longest of all artifacts (7 years) |

### 6.5 Retention guidance

Apply the **longest** applicable retention horizon to each artifact:

- **FINRA Rule 4511 / SEC 17a-4(b):** 6 years for broker-dealer books-and-records (RCD/RSS/DLP/DAG state and incident records).
- **SOX 302/404:** 7 years for control evidence supporting internal financial reporting controls (license entitlement, UAL state, audit assertions, attestation).
- **GLBA 501(b):** firm-defined retention per the firm''s privacy schedule; align to the longer of FINRA / SOX where ambiguous.
- **OCC 2011-12 / SR 11-7:** model-risk validation evidence retained per firm''s model-risk policy (typically 7 years).
- **NYDFS 23 NYCRR 500:** retain consistent with 500.6 (audit trail) and 500.16 (incident response).

### 6.6 WORM evidence storage

Persist the cycle output to the firm''s evidence repository under the WORM (write-once-read-many) path:

```
<evidence-root>/4.6-grounding-scope/<TENANT>/<UTC-yyyyMMdd>/manifest.json
<evidence-root>/4.6-grounding-scope/<TENANT>/<UTC-yyyyMMdd>/<artifacts...>
<evidence-root>/4.6-grounding-scope/<TENANT>/<UTC-yyyyMMdd>/<artifacts....sha256>
```

For SharePoint-backed evidence storage, apply a Records-Management label that meets SEC 17a-4(b) WORM expectations and align with [Control 1.9](../1.9/verification-testing.md) for the records-retention controls themselves.

---
## 7. Attestation

The attestation block below is produced once per cycle, signed by the named roles, and persisted alongside the manifest. It is the single document an examiner will read first.

```
FSI Agent Governance — Control 4.6 Verification Attestation

Tenant:           <TENANT-DISPLAY-NAME> (<TENANT-GUID>)
Cloud:            Commercial | GCC | GCC High | DoD
Cycle ID:         <UUID>
Cycle window:     <UTC start> → <UTC end>
Manifest SHA-256: <hex>

Tester:    [ ] I confirm I executed every test in §4 of the
              Control 4.6 Verification & Testing playbook on the
              named cycle window, using the named test fixtures
              in §2.6, and persisted every artifact identified
              in §6 with its SHA-256 sidecar.
              Name: ______________________  Signature: __________  Date (UTC): __________

Reviewer:  [ ] I reviewed the manifest, re-computed SHA-256 on
              a sample of artifacts, and confirmed the §6.3
              validator passed. I confirm the two-portal capture
              delta is ≤ 900 seconds.
              Name: ______________________  Signature: __________  Date (UTC): __________

Approver:  [ ] I attest that the cycle outcome is a fair and
              accurate representation of the tenant''s grounding-
              scope posture for the cycle window. Exceptions
              listed below are approved.
              Name: ______________________  Signature: __________  Date (UTC): __________

Cycle outcome (binary, by test family):
  RCD-01..06       PASS / FAIL / N/A
  RSS-01..05       PASS / FAIL / N/A
  DLP-01..04       PASS / FAIL / N/A
  DAG-01..03       PASS / FAIL / N/A
  OND-01..02       PASS / FAIL / N/A
  INAPP-01..02     PASS (affirmative) / FAIL / N/A
  AUDIT-01..03     PASS / FAIL / N/A
  NEG-01..04       PASS / FAIL / N/A
  IR-01            PASS / FAIL / N/A

Exceptions (status: N/A — sovereign non-parity, BLOCKED, INCONCLUSIVE):
  Test ID   Status    Compensating control / next step    Owner    Re-test date
  ───────   ───────   ────────────────────────────────    ─────    ────────────
  4.6-DLP-02  N/A      Manual quarterly review            ___      ___
  ...

Firm-defined cadence and SLA values used in this cycle:
  RCD on-change re-run window:    5 business days (firm-defined)
  RCD-restricted PROPAGATION upper bound used as INCONCLUSIVE/FAIL boundary:   firm-defined ___ days
  DAG remediation-ticket threshold:  > 25% week-over-week increase on Confidential+ sites (firm-defined)
  UAL ingestion latency upper bound used in tests:  24 hours (firm-defined upper bound)

Microsoft-published windows referenced (see §3):
  RSS take-effect:           ~1 hour
  RCD propagation:           variable; can exceed 1 week on very large sites
  DAG report population:     ~24 hours after collection enabled
  DAG activity history:      28-day rolling

Regulatory drivers attested against this cycle:
  - FINRA Rule 4511 (books and records)
  - FINRA Rule 3110 (supervisory review)
  - FINRA 25-07 (AI / agent supervision guidance)
  - SEC Rule 17a-3 / 17a-4 / 17a-4(b) (record retention; WORM)
  - SOX 302 / 404 (internal control over financial reporting)
  - GLBA 501(b) (safeguards)
  - OCC 2011-12 / Federal Reserve SR 11-7 (model risk management)
  - NYDFS 23 NYCRR 500 (Parts 500.6 audit trail; 500.11 third-party; 500.16 incident response)

Caveats (this attestation is bounded by):
  1. RCD does NOT scope in-app Word/Excel/PowerPoint Copilot when the user
     has the file open via direct permission. The §4.6-INAPP-01 test PASSING
     in the affirmative direction is documented Microsoft behavior, NOT a
     defect. Do not treat as an RCD failure.
  2. RSS is NOT a security boundary. Identities with recent interaction,
     ownership, or direct-share of an off-allowed-list site WILL surface
     content from it; this is documented Microsoft behavior.
  3. RCD does NOT apply to personal OneDrive. Compensating controls for
     OneDrive content are addressed under Controls 1.5 (sensitivity labels)
     and 4.7 (OneDrive sharing posture).
  4. DLP-for-Copilot is the ONLY in-product mechanism that blocks a
     SharePoint URL from being added as a Copilot Studio knowledge source.
     RCD and RSS do not produce that effect.
  5. UAL operation names referenced in §4 (e.g., SharePointSetTenantSettings)
     are illustrative and must be re-verified on Microsoft Learn at every
     UI-verification cycle. The audit assertion is satisfied if the tenant
     change is recorded under the then-current operation name family.
  6. Sovereign-cloud rows marked N/A reflect documented non-parity
     availability windows for RSS / RCD / SAM / DLP-for-Copilot in US
     Government clouds; compensating controls are listed in the exceptions
     table above.

This attestation supports compliance with the regulations listed above; it
does not, by itself, constitute a determination of compliance. Final
compliance determinations remain with the firm''s Compliance Officer and
external examiner.
```

Persist the signed attestation as `4.6-ATTEST-<TENANT>-<UTC>-attestation.pdf` and include it in the manifest as part of `4.6-AUDIT-03` evidence.

---

## 8. Anti-Patterns

The following anti-patterns are tracked because each has surfaced in production tenants, in prior versions of this playbook, or in AI Council reviews. The §4 test catalog is engineered to prevent the corresponding false-pass / false-fail.

1. **"RCD broke in-app Copilot — roll back."** False-fail. RCD does not scope in-app Word/Excel/PowerPoint Copilot when the user has the file open via direct permission. `4.6-INAPP-01` PASSING in the affirmative direction is the *expected* result. Rolling back RCD on this basis weakens Business Chat / search containment without addressing any real defect.

2. **"RCD is enabled tenant-wide; we don''t need RSS or DLP."** False-claim. RCD is per-site, not tenant-wide; RSS is independent and addresses tenant-search exposure during permissions-remediation; DLP-for-Copilot is the *only* lever that prevents Copilot Studio knowledge-source ingest of an in-scope SharePoint URL. The §4 catalog tests each independently for a reason.

3. **"RSS is our records-isolation control."** False-claim. RSS is documented as not a security boundary. `4.6-RSS-04` and `4.6-RSS-05` produce the regulator-facing statement that records this explicitly. Records isolation is addressed under Controls 1.5, 1.9, and 4.1 — not by RSS.

4. **"We ran the test on my admin account; everything looked right."** Non-deterministic. RSS and in-app surfaces honor recent-interaction / ownership / direct-share signals. Tests run on identities with prior interaction with the test sites cannot distinguish "RSS is allowing this" from "the surface is honoring the recent-interaction signal." §2.6 mandates clean test identities.

5. **"Allow 24-48 hours and re-test."** Fabricated SLA. The previous version of this playbook contained that figure; it is not a Microsoft-published window. The only documented windows are in §3. Any "X hours" expression in your runbook that does not appear in §3 is firm-defined and must be labeled so.

6. **"We tested DLP at the SharePoint admin center; it works."** Wrong portal. DLP-for-Copilot lives in the Power Platform Admin Center / Microsoft Purview, scoped to the `Microsoft 365 Copilot` location. Reading SPAC alone produces no evidence of the DLP block path.

7. **"DAG reports came back empty so the tenant is fine."** False-pass. DAG requires data-collection enablement (§2.7) and ≥ 24 hours of seasoning before producing meaningful results. An empty DAG report on a tenant with active sharing is a DAG-not-enabled signal, not a clean-tenant signal.

8. **"OneDrive content is fine because RCD is on."** False-claim. RCD does not apply to personal OneDrive. `4.6-OND-01` produces the boundary statement; `4.6-OND-02` exercises the cross-invoker boundary on Copilot Studio agents.

9. **"We''ll add the Copilot license to the test users when we need to."** Cycle-aborter. License entitlement is `4.6-LIC-01` and gates every downstream test. Discovering a missing Copilot license partway through the cycle invalidates every test that ran before it.

10. **"`Get-SPOTenant` returns the same thing every time."** Schema-drift trap. The cmdlet has changed shape across SPO Management Shell versions. `4.6-NEG-01` asserts property presence before reading values, so a renamed or removed property is recorded as `BLOCKED — schema drift` instead of silently passing.

11. **"`SharePointSetTenantSettings` is the audit operation — write the assertion against that exact string."** Future-fragile. The audit operation name family evolves; the §4 audit assertions state the operation name as illustrative pending verification on `audit-log-activities` at every UI-verification cycle. Hardcoding the string and never re-verifying produces silent audit-assertion failures.

12. **"Capture SPAC state on Monday, capture PPAC state on Wednesday."** Incoherent baseline. Any DLP edit between Monday and Wednesday invalidates the DLP test against the SPAC baseline. §2.4 enforces a ±15-minute capture window across both portals, and `manifest.two_portal_delta_seconds > 900` is a §6.3 validator failure.

13. **"We''ll skip `4.6-IR-01` this year — no incidents."** Misses the point. The annual tabletop is the only routine exercise of the grounding-scope IR flow; without it, on-call paging / triage / containment paths atrophy. NYDFS 500.16 expects evidence of IR exercise regardless of whether a real incident occurred.

14. **"The sovereign tenant ''passed'' all tests."** Unverified parity claim. RSS / RCD / SAM / DLP-for-Copilot have non-parity in US Gov clouds; passing without a current-Learn verification means the test is reading a surface that may not exist or may behave differently. The §5 sovereign matrix forces an explicit Learn re-verification per cycle.

15. **"The marker file is the same one we used last cycle."** Cache trap. Reusing the same marker GUID across cycles cannot distinguish "the surface is reading this cycle''s state" from "the surface returned a cached result from a prior cycle." `{cycle-uuid}` in §2.6 is regenerated every cycle for exactly this reason.

---

## 9. Cross-Links

### Within Control 4.6

- [Portal Walkthrough](portal-walkthrough.md) — UI-driven enable / disable procedures for RCD, RSS, and DLP-for-Copilot policies referenced from §4.
- [PowerShell Setup](powershell-setup.md) — automated enable / disable scripts and the schema-presence helper used by `4.6-NEG-01..03`.
- [Troubleshooting](troubleshooting.md) — documented failure modes for the surfaces tested in §4 (e.g., RSS take-effect lag, RCD propagation on very large sites, DLP-policy precedence).

### Other controls in this framework

- [Control 1.5 — Sensitivity Labels and Data Classification](../1.5/verification-testing.md) — labels are the substrate that DLP-for-Copilot policies reference; tests in 4.6-DLP-NN assume the label model from 1.5 is in place.
- [Control 1.7 — Audit Logging Configuration](../1.7/verification-testing.md) — UAL enablement and retention is verified there; `4.6-UAL-01` re-asserts the gate for this control.
- [Control 1.9 — SharePoint Records Retention](../1.9/verification-testing.md) — records retention horizons referenced in §6.5 are verified there.
- [Control 1.14 — Microsoft 365 Copilot Configuration](../1.14/verification-testing.md) — the Copilot license, in-app behavior, and Business Chat surface tested here are governed there.
- [Control 2.16 — Power Platform DLP for Copilot](../2.16/verification-testing.md) — the authoritative verification of the DLP-for-Copilot policy lifecycle; `4.6-DLP-01..04` here is the grounding-scope-specific subset.
- [Control 4.1 — SharePoint Permissions Architecture](../4.1/verification-testing.md) — the permissions baseline that RSS positions itself as containment for during remediation.
- [Control 4.7 — OneDrive Sharing Posture](../4.7/verification-testing.md) — the OneDrive-sharing controls referenced by `4.6-OND-NN` for the carve-out.
- [Control 4.8 — SharePoint Sensitivity-Label Enforcement](../4.8/verification-testing.md) — label enforcement on SharePoint that DAG reports on in `4.6-DAG-02`.

### Shared playbooks

- [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md) — the connection / error-handling / logging conventions all §4 PowerShell snippets follow.
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) — the IR flow that `4.6-IR-01` exercises.

### External references (verify on current Microsoft Learn at every UI-verification cycle)

- Microsoft Learn — Restricted Content Discovery (SharePoint Advanced Management).
- Microsoft Learn — Restricted SharePoint Search.
- Microsoft Learn — Data Loss Prevention policies for Microsoft 365 Copilot.
- Microsoft Learn — Data Access Governance reports.
- Microsoft Learn — Microsoft 365 Copilot interactions and audit events.
- Microsoft Learn — Audit log activities catalog (`audit-log-activities`).
- Microsoft Learn — Microsoft 365 Government plans and feature parity.

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*