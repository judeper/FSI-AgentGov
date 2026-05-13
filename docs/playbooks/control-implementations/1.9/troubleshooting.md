# Control 1.9 — Troubleshooting: Data Retention and Deletion Policies

**Control:** 1.9 — Data Retention and Deletion Policies
**Pillar:** Pillar 1 — Security
**Audience:** Purview Records Manager, Purview Compliance Admin, Purview eDiscovery Roles, Compliance Officer, Power Platform Admin, Legal / General Counsel
**Companion playbooks:** [Portal walkthrough](./portal-walkthrough.md) · [PowerShell setup](./powershell-setup.md) · [Verification & testing](./verification-testing.md)

> **Scope.** This playbook covers operational, evidentiary, and regulatory failure modes for Microsoft Purview retention labels, retention policies, AI-experience retention, Records Management, Preservation Lock, eDiscovery / Litigation hold, disposition review, and Dataverse long-term retention as configured per [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
>
> Each issue follows **Symptom → Likely cause → Diagnostic → Resolution → What good looks like**. Read [§1 FSI incident handling](#1-fsi-incident-handling-read-first) before remediating production retention issues — for record-keeping controls the order of operations is *preserve evidence first, remediate second*.
>
> **Hedging note.** This playbook helps meet, and is recommended to support compliance with, SEC 17 CFR 240.17a-4, FINRA 4511, SOX §404 / §802, GLBA 501(b), CFTC 1.31, and IRS recordkeeping rules. It does not by itself satisfy any of those rules. Implementation requires legal review and verification against the firm's Written Supervisory Procedures.

---

## 1. FSI incident handling — read first

When a retention or disposition issue is detected in a Zone 3 tenant, the order of operations is:

1. **Triage severity** (§1.1)
2. **Determine reportability** (§1.2)
3. **Preserve evidence BEFORE remediation** (§1.3)
4. **Stand up compensating controls** (§1.4)
5. **Remediate**, then verify with [Verification & Testing](./verification-testing.md)

Skipping evidence preservation can convert a recoverable operational issue into a regulatory record-integrity finding.

### 1.1 Severity matrix

| Severity | Examples | Response window |
|---|---|---|
| **SEV-1 — record-keeping integrity at risk** | Retention silently disabled or unscoped from production tenant; Preservation Lock missing on Zone 3 policy that should be locked; in-scope agent transcripts disposed before retention end; eDiscovery hold inactive while litigation pending; Dataverse long-term retention silently failing on Copilot Studio environment | Immediate (page on-call); preserve evidence within 1 hour |
| **SEV-2 — retention gap with bounded blast radius** | Single Zone 2 location dropped from a label policy; disposition queue stuck >7 days; one AI-experience policy distribution status `Pending` >72h; locked policy permits a permitted-but-unintended extension | Within business day |
| **SEV-3 — operational only** | `Get-ComplianceTag` cmdlet throttling; portal label-publish UI lag <24h; reviewer email notification delivery delay | Routine queue |

### 1.2 Reportability decision tree

For SEV-1 and confirmed SEV-2, walk this tree before remediating. Do **not** rely on this list for legal advice — escalate to General Counsel / CCO immediately.

| Trigger | Likely reportable to | Notice clock |
|---|---|---|
| Disposed records that should have been retained under 17a-4 | SEC; FINRA Rule 4530 | Escalate to CCO immediately; FINRA notice per Rule 4530 categories |
| Cybersecurity incident affecting customer NPI in NY DFS-regulated entity | NY DFS Part 500.17(a) | **72 hours** from determination |
| Material cybersecurity incident at SEC registrant | SEC 8-K Item 1.05 (issuers); Form ADV-C (advisers) | "Material" thresholds — escalate to GC/CCO |
| Spoliation of records subject to active litigation hold | Court (FRCP 37(e) sanctions exposure) | Notify outside counsel immediately |
| FCM / swap dealer / CPO record loss | CFTC under 17 CFR 1.31 | Per CFTC guidance |
| Bank examiner-relevant model documentation loss | OCC 2011-12 / Federal Reserve SR 11-7 examiner notification | Per supervisory guidance |

### 1.3 Evidence preservation BEFORE remediation

For every SEV-1 (and SEV-2 where reportability is plausible):

1. Run the PowerShell evidence export from [PowerShell §7 — Evidence export](./powershell-setup.md) and save to the legal-hold evidence vault.
2. Run a Purview Audit search covering at least the prior 90 days for the affected policies, labels, and event types in [PowerShell §5 — Audit-log retention for deletion events](./powershell-setup.md). Export and SHA-256 stamp.
3. **Do not delete** the affected policies, labels, or rules. If a misconfigured policy is causing harm, prefer scoping it down or extending retention rather than deleting (deletion destroys evidence of the original configuration).
4. For affected content, place an eDiscovery hold scoped to the mailboxes/sites/Copilot locations involved before further remediation.

### 1.4 Compensating controls

| Underlying gap | Compensating control until fixed |
|---|---|
| Retention policy unscoped from a location | eDiscovery hold scoped to the affected location |
| Preservation Lock missing | Manual change-control freeze on the policy + daily PowerShell snapshot of policy state to evidence vault |
| Dataverse long-term retention failing | Scheduled bulk export of `conversationtranscript` to immutable Azure Blob (versioning + legal hold) |
| Audit log retention insufficient | Sentinel ingestion of unified audit log with extended retention |

---

## 2. Issue catalog

### 2.1 Retention policy not applying to expected content

**Symptom:** Files / messages / Copilot interactions are not being retained or labeled as expected.

**Likely cause:** Distribution still in progress; location scope omits the target; adaptive scope query excludes the target user; conflicting policy with higher precedence applied.

**Diagnostic:**

```powershell
$p = Get-RetentionCompliancePolicy -Identity 'FSI-Copilot-AIExperiences-Retention' -DistributionDetail
$p | Select-Object Name, Mode, Enabled, DistributionStatus, RetentionComplianceLockType, *Location*
Get-RetentionComplianceRule -Policy $p.Name |
    Select-Object Name, RetentionDuration, RetentionComplianceAction, ContentMatchQuery
```

For per-user diagnosis (Copilot/AI experiences), check the user's effective policy in Purview > Data lifecycle management > Policies > policy detail > **Status** > **Locations**.

**Resolution:**

1. Wait the documented distribution window: 1 day for most locations, up to 7 days for fully populated mailboxes.
2. Confirm the location switch matches the workload (`ExchangeLocation`, `SharePointLocation`, `OneDriveLocation`, `ModernGroupLocation`, the AI-experience locations).
3. If using adaptive scopes, run the scope's underlying Entra query manually to confirm the user/site is included.
4. Check the [Microsoft Learn precedence rules](https://learn.microsoft.com/en-us/purview/retention#the-principles-of-retention-or-what-takes-precedence) — the **longest** retention wins; explicit deletion never overrides retention.
5. Verify there is no policy-level **exclusion** masking the target.

**What good looks like:** `DistributionStatus = Success` for every targeted location, content shows the expected effective label/retention, and `Get-PnPListItem` (SharePoint) or audit search confirms `_ComplianceTag` is populated.

---

### 2.2 Lock-state confusion — what does "locked" actually prevent?

**Symptom:** Admin attempts a change on a Preservation-Locked policy and receives an unexpected success or unexpected failure.

**Likely cause:** Misunderstanding of what Preservation Lock permits.

**Diagnostic:**

```powershell
Get-RetentionCompliancePolicy | Where-Object RetentionComplianceLockType -eq 'Lock' |
    Select-Object Name, Mode, Enabled, RetentionComplianceLockType, WhenChanged
```

**The matrix of permitted vs. denied actions on a locked policy:**

| Action | Permitted on locked policy? |
|---|---|
| Disable policy (`-Enabled:$false`) | ❌ Denied |
| Delete policy | ❌ Denied |
| Reduce retention duration | ❌ Denied |
| Change retention action from `KeepAndDelete` to `Delete` (shortens effect) | ❌ Denied |
| Remove a location | ❌ Denied |
| Remove a label from a publish-policy | ❌ Denied |
| **Add** a new location | ✅ Permitted |
| **Extend** retention duration | ✅ Permitted (and itself irreversible) |
| Add a new rule to the policy | ✅ Permitted (the new rule is also locked) |
| Modify `ContentMatchQuery` to *broaden* | ⚠️ Microsoft behavior has varied — verify in test before production change |

**Resolution:**

1. Document the intended change against the matrix above.
2. If the change is in the "permitted" column, run it as a SEV-2 CAB change with second-person review (extending retention is itself irreversible).
3. If the change is in the "denied" column, the answer is **no** — the policy cannot be weakened. Stand up a *new* policy alongside the locked one if a separate (broader or different) retention need exists. Never attempt workarounds.

**What good looks like:** The change request explicitly cites the matrix row it falls under and includes pre/post PowerShell evidence in the change ticket.

---

### 2.3 Conflicting retention policies — which one wins?

**Symptom:** Multiple retention policies / labels apply to the same item and behavior is unexpected.

**Likely cause:** Misunderstanding of the Microsoft Purview precedence model.

**Diagnostic:**

```powershell
# Identify all policies + rules that could touch a given location
$loc = 'ExchangeLocation'
Get-RetentionCompliancePolicy | Where-Object { $_.$loc -contains 'All' -or $_.$loc.Count -gt 0 } |
    Select-Object Name, Mode, Enabled, RetentionComplianceLockType, $loc
```

**Precedence model (in order):**

1. **Retention wins over deletion.** If any policy says "retain," the item is retained regardless of any policy that says "delete."
2. **Longest retention wins.** If multiple policies apply, the longest period applies.
3. **Explicit (label) wins over implicit (policy)** for the same length.
4. **Holds beat retention.** An eDiscovery hold preserves regardless of any retention setting.
5. **Locked policy effectively wins** because it cannot be weakened to resolve a conflict.

**Resolution:**

1. Map every policy / label that targets the affected workload using the diagnostic above.
2. Apply the precedence model to predict the outcome; reconcile with observed behavior.
3. If the predicted outcome is wrong, retire the policy that should not apply (only possible if it is not locked) or scope it down via adaptive scope.
4. If the predicted outcome is right but business stakeholders want a different result, the answer is to redesign — not to break the precedence model.

**What good looks like:** A documented per-workload retention map showing the winning policy, signed by Records Management, kept with the WSPs.

---

### 2.4 Disposition review queue stuck or empty

**Symptom:** Items at retention end never appear in the **Disposition** queue, or appear and never move.

**Likely cause:** Label action is not "Start a disposition review"; reviewers are unconfigured / disabled mailboxes; reviewer notification address is wrong; underlying location does not support disposition review (Copilot interactions and Dataverse do **not** support reviewer-driven disposition).

**Diagnostic:**

```powershell
Get-ComplianceTag | Where-Object { $_.Name -like 'FSI-Agent-*' } |
    Select-Object Name, RetentionAction, ReviewerEmail, IsRecordLabel, Regulatory
```

Check the **Disposition** > **Reviewers** screen for unresolved or external reviewers.

**Resolution:**

1. For disposition-supported workloads (Exchange, SharePoint, OneDrive on labeled items): confirm `RetentionAction = KeepAndDelete` and `ReviewerEmail` is a valid mail-enabled security group.
2. For Copilot interactions and Dataverse transcripts: disposition review **is not supported**. Defensible deletion evidence comes from the audit log (`FileDeleted`/equivalent events) and the policy configuration itself.
3. Replace any individual reviewer mailboxes with mail-enabled security groups so reviewer turnover does not silently break the workflow.
4. For SharePoint / OneDrive items, enable **Disposition for items in SharePoint and OneDrive** under Records Management settings if not already on.

**What good looks like:** Disposition queue is non-empty, items move within the firm's documented review SLA (e.g., 30 days), and the **Disposed items** view shows reviewer + justification per disposition.

---

### 2.5 Content disposed before retention end

**Symptom:** Items missing from a labeled location before the retention period expired.

**Likely cause:** Hard delete of underlying mailbox/site (which removes the Preservation Hold Library); legal hold release that triggered queued disposition; misapplied `Delete` action on the label; race condition with Dataverse environment deletion.

**Diagnostic:**

```powershell
# Was the mailbox / site soft-deleted?
Get-Mailbox -SoftDeletedMailbox | Where-Object { $_.UserPrincipalName -like '*affected*' }
Get-SPODeletedSite | Where-Object { $_.Url -like '*affected*' }
```

Run an audit search for `HardDelete`, `Remove-Mailbox`, `Remove-SPOSite`, `Remove-AdminPowerAppEnvironment` covering the period.

**Resolution:**

1. **Preserve first.** Place an eDiscovery hold on remaining surfaces immediately. Do not attempt to "fix" via deletion or policy changes.
2. **Recover what is recoverable.** Soft-deleted mailboxes / sites have recovery windows (typically 30 days for sites, 30 days for mailboxes — verify against current Microsoft documentation). Restore in place if within window.
3. **Investigate root cause.** Was a Power Platform environment deleted? An admin-initiated mailbox removal? An automation that bypassed the records process?
4. **Notify CCO / GC** per §1.2.
5. **Capture lessons learned** in a post-incident review; treat as a control change request to add an additional gate (e.g., environment-deletion approval workflow).

**What good looks like:** Recoverable content recovered; non-recoverable content documented in an incident report; root-cause control change implemented and tested.

---

### 2.6 Cannot delete content after retention end (item appears stuck)

**Symptom:** Disposition is approved but the item persists; or label action is `Delete` and the item is still there past retention.

**Likely cause:** Active eDiscovery hold; regulatory-record flag preventing label removal; another retention policy with a longer period; Preservation Hold Library waiting on its own retention.

**Diagnostic:**

```powershell
# Holds touching the item's location
Get-ComplianceCase | ForEach-Object {
    Get-CaseHoldPolicy -Case $_.Identity | Select-Object Name, Enabled, ExchangeLocation, SharePointLocation
}

# Is the label a regulatory record?
Get-ComplianceTag -Identity '<label-name>' | Select-Object Name, IsRecordLabel, Regulatory
```

**Resolution:**

1. Check for an active hold; if a hold is the cause, that is **expected** behavior. Do not release the hold without legal sign-off.
2. If `Regulatory = True`, the label cannot be removed and the item cannot be deleted while the regulatory clock is running. Verify retention duration; extend if necessary.
3. Identify and reconcile longer-retention policies that may also touch the item (use §2.3 precedence diagnostic).
4. For SharePoint Preservation Hold Library, allow the documented service-side cleanup window (typically a few days after disposition).

**What good looks like:** Either the item is correctly disposed, or there is a documented lawful reason it persists (active hold, regulatory record, longer concurrent retention).

---

### 2.7 Label policy distribution shows `Pending` or `Error`

**Symptom:** Label policy or retention policy stuck in `Pending`, `Error`, or `Off (Pending)` state.

**Likely cause:** Service-side processing delay; invalid location reference (deleted site / mailbox); insufficient authoring permissions at create time; policy conflict with a tenant-level setting.

**Diagnostic:**

```powershell
Get-RetentionCompliancePolicy -Identity 'FSI-Agent-Labels-Publish-Zone3' -DistributionDetail |
    Format-List Name, DistributionStatus, *Distribution*
```

**Resolution:**

1. Allow the documented distribution window before declaring failure (24 h typical; up to 7 days for fully populated mailboxes).
2. If `Error`, inspect the `DistributionDetail` payload for invalid GUIDs / removed sites; remove or replace the offending location.
3. Confirm authoring account had Records Manager + Compliance Admin at create time; if not, recreate from a properly-roled session.
4. Check Microsoft 365 Service Health for active retention-service incidents.
5. As a last resort, recreate the policy from a known-good template; **do not** delete the original until the replacement is `Success` and verified.

**What good looks like:** `DistributionStatus = Success` across all targeted locations within the documented SLA.

---

### 2.8 eDiscovery hold not preventing deletion

**Symptom:** Content under hold is still being disposed.

**Likely cause:** Hold scope omits the affected location; hold query is too narrow; mailbox / site was hard-deleted before the hold attached; case is closed or hold was released.

**Diagnostic:**

```powershell
$case = Get-ComplianceCase -Identity 'Matter-...'
Get-CaseHoldPolicy -Case $case.Identity | Select-Object Name, Enabled, ExchangeLocation, SharePointLocation
Get-CaseHoldRule  -Policy '<hold-policy-name>' | Select-Object Name, ContentMatchQuery, Disabled
```

**Resolution:**

1. Confirm the hold is **Enabled** and **not** disabled by an admin or by case closure.
2. Confirm scope includes the actual mailbox / site / Copilot location of the affected content.
3. If the hold has a query, confirm the disputed content matches it (test with eDiscovery search).
4. If the underlying mailbox / site was hard-deleted before the hold was applied, recover from soft-delete immediately if within the recovery window.
5. Add a redundant Preservation Lock-style retention policy for ongoing matters where hold reliability is critical.

**What good looks like:** Hold inventory shows the affected items, eDiscovery search returns them, and downstream retention/disposition does not act on them.

---

### 2.9 Dataverse long-term retention not archiving

**Symptom:** Copilot Studio agent transcripts past the archive trigger remain in the operational table; **Job history** shows failures or no jobs.

**Likely cause:** Long-term retention policy not enabled on the table; environment lacks the required capacity; per-table retention disabled; environment is in a soft-delete state.

**Diagnostic:** PPAC > **Environments** > the environment > **Settings** > **Data management** > **Long-term retention** > policy detail > **Job history**.

**Resolution:**

1. Confirm long-term retention is enabled at environment level and at table level for `conversationtranscript`, `botcomponent`, `botsession`/`botinteraction` as applicable.
2. Confirm capacity is available; archival writes to long-term storage and consumes capacity per the Power Platform licensing rules.
3. Re-run the archive job manually if the UI offers that option for the failed table.
4. If the environment is mid-recovery from a soft-delete, wait for service-side reconciliation before forcing changes.
5. Add a Sentinel-watched scheduled query that alerts when the **Job history** count for in-scope tables is zero over a 7-day window.

**What good looks like:** **Job history** shows successful jobs on the documented cadence; archived rows are queryable via the Long-Term Retention pane and absent from the operational table.

---

### 2.10 SEC 17a-4(f) WORM claim cannot be substantiated

**Symptom:** Examiner asks for the firm's WORM / audit-trail-alternative attestation under 17a-4(f) and the firm cannot produce it.

**Likely cause:** The firm relied on Microsoft Purview Preservation Lock alone, without the third-party assessment and **Designated Third Party (D3P) undertaking** required by 17a-4(f)(3)(vii).

**Diagnostic:** Ask three questions of the records program:

1. Has the firm obtained a third-party assessment of the Microsoft 365 Purview retention configuration as supporting 17a-4(f)?
2. Does the firm have a signed **D3P undertaking** on file from a qualified vendor (Microsoft does **not** act as D3P)?
3. Are the Preservation-Locked policies aligned with the assessment scope and unchanged since assessment?

**Resolution:**

1. **Stop making the WORM claim** in compliance materials and examiner correspondence until the gap is closed.
2. Engage a qualified compliance consultant to perform the 17a-4(f) assessment for the in-scope tenant configuration.
3. Engage a qualified D3P vendor and execute the undertaking under 17a-4(f)(3)(vii); file with the firm's compliance records.
4. Re-baseline the locked policies against the assessment scope and document the change-management process to keep them aligned.
5. Update WSPs to reference the assessment and the D3P arrangement; train staff on the change-control gates.

**What good looks like:** A current third-party assessment, a signed D3P undertaking, and a documented change-control process exist together; examiner request can be answered with a single binder.

---

## 3. Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Treating Preservation Lock as a 17a-4(f) WORM claim by itself | The rule requires a third-party assessment and D3P undertaking; lock alone is not the rule's universe |
| Single-mailbox reviewer for disposition | Personnel turnover silently breaks disposition without alerting |
| `RetentionAction = Delete` on books-and-records | A misclassification can dispose records before regulatory minimums |
| Static scopes on Zone 3 retention policies | Population drift silently exempts new in-scope users |
| Deleting a misconfigured retention policy to "start over" | Destroys the evidence of the original misconfiguration; complicates examiner response |
| Relying on Dataverse environment-level retention only for Copilot Studio | Environment-level changes can drop retention silently; pair with Purview retention on the Copilot/AI experiences location |
| Using the same retention period across all agent surfaces because "longer is safer" | Over-retention of customer NPI creates GLBA / Reg S-P disposal exposure; calibrate by record type |
| Holding "everything" via eDiscovery to compensate for missing retention design | Holds are matter-scoped, not a substitute for a records program; over-broad holds invite spoliation arguments at release |

---

## 4. Cross-references

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md): the audit trail this control depends on.
- [Control 4.3 — Site and Document Retention Management](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md): SharePoint-specific retention guidance.
- [Microsoft Learn: Use Preservation Lock](https://learn.microsoft.com/en-us/purview/retention-preservation-lock)
- [Microsoft Learn: Regulatory requirements for information governance](https://learn.microsoft.com/en-us/purview/retention-regulatory-requirements)
- [SEC Final Rule 34-96034 (Oct 2022, electronic recordkeeping)](https://www.sec.gov/rules/final/2022/34-96034.pdf)

---

[Back to Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) · [Portal walkthrough](./portal-walkthrough.md) · [PowerShell setup](./powershell-setup.md) · [Verification & testing](./verification-testing.md)

---

*Updated: April 2026 | Version: v1.6.2*
