# Troubleshooting: Control 1.22 — Information Barriers for AI Agents

**Last Updated:** April 2026
**Audience:** M365 administrators and SOC / compliance engineering teams responding to IB issues

---

## Quick-Reference Symptom Matrix

| Symptom | Most Likely Cause | First Step |
|---|---|---|
| User can chat across what should be a barrier | User has no segment, or last application has not completed | Check `Get-InformationBarrierRecipientStatus -Identity <upn>` and `Get-InformationBarrierPoliciesApplicationStatus` |
| `Get-InformationBarrierPoliciesApplicationStatus` stuck `InProgress` > 72h | Filter targeting an empty/invalid attribute, conflicting policy, or transient service issue | Inspect failed segments; open Microsoft support case with `Identity` GUID |
| M365 Copilot returns content from a blocked segment | User is in unintended segment, knowledge source is unsegmented, or Channel Agent surface used | Reproduce as test user; check segment membership; review knowledge-source segments |
| Copilot Studio Channel Agent does not trim cross-segment | **Expected platform behavior** — Channel Agents do not consistently inherit IB | Apply compensating controls or republish as per-user Teams app |
| Cannot create a Microsoft 365 Group containing two users | Working as designed; users are in segments with no allow-list overlap | Use wall-crossing workflow if business-justified |
| SharePoint site allows cross-segment members | Site has no segment assigned, or site IB mode is permissive | Assign site segment; set IB mode to `Explicit` |
| `New-InformationBarrierPolicy` fails with `SegmentsBlocked` parameter error | Tenant is in `MultiSegment` mode (allow-list pattern) | Use `-SegmentsAllowed` instead |
| `New-InformationBarrierPolicy` fails with `SegmentsAllowed` parameter error | Tenant is in `Legacy` or `SingleSegment` mode (block-list pattern) | Use `-SegmentsBlocked` instead |
| Exchange mail still flows between segments after applying | In `MultiSegment` mode, mail-flow IB enforcement differs from `Legacy`; review supplemental compensating transport rules | Validate workload coverage and configure compensating Exchange transport rules if required |

---

## Detailed Troubleshooting Scenarios

### Scenario A — User in Wrong (or No) Segment

**Symptoms:**
- User can access content they should not, or cannot access content they should.
- `Get-InformationBarrierRecipientStatus -Identity <upn>` returns no segment or an unexpected segment.

**Resolution:**

1. Confirm the user's `Department`, `CompanyName`, and other attributes in Entra ID match the segment filter (`Get-MgUser -UserId <upn> -Property Department,CompanyName,JobTitle`).
2. If attributes are wrong, fix in the **HR-of-record** system and let the provisioning sync update Entra ID. Do not hand-edit — manual changes will be overwritten and break audit lineage.
3. After attributes correct, re-run `Start-InformationBarrierPoliciesApplication` and wait for `Completed`.
4. Re-test with `Get-InformationBarrierRecipientStatus`.

> **FINRA 3110 note:** Each manual override of an HR-of-record attribute should be ticketed and approved by Compliance. Hand-edited attributes that drive segment membership are a supervisory finding.

---

### Scenario B — Policy Application Stuck `InProgress`

**Symptoms:**
- `Get-InformationBarrierPoliciesApplicationStatus` shows `InProgress` for >72 hours.

**Resolution:**

1. Capture all in-progress entries:
    ```powershell
    Get-InformationBarrierPoliciesApplicationStatus | Where-Object Status -eq 'InProgress'
    ```
2. Inspect any `FailedTaskDetails` or per-segment errors.
3. Common causes:
    - A segment filter references an attribute populated for very few users (e.g., 0).
    - Conflicting overlapping segments after a recent migration.
    - Tenant-side service throttling (rare; usually self-clears in 24h).
4. If the issue persists past 72 hours, open a **Microsoft support case** under "Microsoft 365 → Microsoft Purview → Information Barriers", citing the affected `Identity` GUIDs. Attach the baseline export (Script 1) and the policy export (Script 3 output).

---

### Scenario C — M365 Copilot or Per-User Agent Returns Cross-Segment Content

**Symptoms:**
- A research-segmented user issues a Copilot prompt and the response includes trading content (or vice-versa).

**Resolution:**

1. Reproduce as the same test user; record the prompt and response.
2. Verify the user's segment with `Get-InformationBarrierRecipientStatus`.
3. Verify the source content's container (SharePoint site, OneDrive, Loop workspace) has the **expected segment** assignment. Sites without segments are not IB-trimmed.
4. Verify whether the response originated from a **Graph connector** index — Graph connector content is not IB-segmented by default. If it is, treat as a knowledge-source curation gap (Control 1.4 / 1.7) and remove the cross-segment content from the connector index.
5. Confirm the agent surface is **per-user invocation**, not a Channel Agent (see Scenario D).
6. If all of the above are correct and the response still leaks, open a Microsoft support case and freeze the agent until resolved (FINRA 3110 supervisory expectation).

---

### Scenario D — Channel Agent Cross-Segment Behavior

**Symptoms:**
- A Copilot Studio agent posted as a Channel Agent in a Teams channel returns content from a segment the invoker should not see.

**This is documented platform behavior.** Channel Agents do not consistently inherit per-invoker IB context.

**Resolution:**

1. Inventory all Channel Agents in PPAC.
2. For each Channel Agent that is in a channel spanning barrier-protected segments:
    - **Zone 3:** Republish as a per-user Teams app and unpublish the Channel Agent. Until then, suspend the agent.
    - **Zone 2:** Apply compensating controls — restrict the channel membership to a single segment, prune knowledge sources to non-barrier-protected content, and apply Power Platform DLP (Control 1.4) and Purview DLP for Copilot/Agents (Control 1.7).
    - **Zone 1:** Document risk acceptance signed by Compliance.
3. Update agent inventory and risk register.

---

### Scenario E — Wall-Crossing Approved but User Still Blocked

**Symptoms:**
- A wall-crossing has been approved and provisioned, but the user still cannot access the target content.

**Resolution:**

1. Confirm the GRC provisioning step actually changed the segment assignment or temporary group membership.
2. **Run `Start-InformationBarrierPoliciesApplication`** — segment changes are not enforced until policies are re-applied.
3. Wait for `Completed` status; expect 1–24 hours typical, longer in large tenants.
4. Communicate the realistic activation timeline to the requesting BU; do not over-promise immediate access.

---

### Scenario F — `Get-InformationBarrierMode` Returns `Legacy`

**Symptoms:**
- The tenant is on IB v1; multi-segment features and the modern (post-August 2023) lifecycle are not available.

**Resolution:**

1. Migration is one-way and must be planned with Compliance + IT change-board approval.
2. Pre-migration prerequisites:
    - Remove all Exchange Online Address Book Policies (ABPs) created for IB v1 use (only those — keep unrelated ABPs).
    - Re-validate every existing segment filter against current directory attributes.
3. Follow [Microsoft Learn — Use multi-segment support in Information Barriers](https://learn.microsoft.com/en-us/purview/information-barriers-multi-segment) for the migration cmdlet sequence.
4. After migration, re-run all of [Verification & Testing](verification-testing.md) end-to-end, including behavioral tests.

---

### Scenario G — Mail Flow Behavior Differs from Expected

**Symptoms:**
- In `MultiSegment` mode, mail between segmented users is permitted in some flows where it would have been blocked in `Legacy`.

**Resolution:**

1. Multi-Segment IB is **not** enforced via Exchange Address Book Policies. Mail-flow blocking semantics differ from Legacy.
2. If the firm requires hard mail-flow blocking between segments (e.g., research → trading), supplement IB with **Exchange transport rules** that reject messages when sender and recipient have specific group memberships or attributes.
3. Document the supplement as a compensating control under Control 1.7 (DLP) or Control 2.13 (Communication Compliance) and reference it in the Control 1.22 attestation.

---

### Scenario H — Microsoft Loop / Whiteboard / Planner Sharing Across Segments

**Symptoms:**
- Loop components or Whiteboards appear shareable across segments; Planner plans are visible cross-segment.

**Resolution:**

1. Loop, Whiteboard, and modern Planner inherit the host SharePoint/OneDrive container's IB segment. If the host container is unsegmented, the artifact is unsegmented.
2. Move the artifact to a properly segmented site or assign a segment to the existing site.
3. Re-test access as the cross-segment test user.

---

## Escalation Path

1. **Tier 1 — M365 Admin / Help Desk:** triage symptom; capture `Get-InformationBarrierRecipientStatus`, `Get-InformationBarrierPoliciesApplicationStatus`, and reproduce screenshots.
2. **Tier 2 — Purview Compliance Admin:** validate segment filters, policy matrix, and SharePoint site segments; re-run application.
3. **Tier 3 — AI Administrator:** verify agent knowledge-source inventory and Channel Agent posture.
4. **Tier 4 — Compliance Officer + Legal:** wall-crossing decisions, residual-risk acceptance, and FINRA 3110 supervisory finding triage.
5. **Tier 5 — Microsoft Support:** open a Premier / Unified Support case under Microsoft Purview → Information Barriers with baseline + status exports attached. Engage the FastTrack or CSU team for systemic regressions.

---

## Known Limitations

| Limitation | Impact | Workaround / Mitigation |
|---|---|---|
| Application is asynchronous and slow (24–72h in large tenants) | Policy changes do not take effect immediately | Schedule changes during low-impact windows; communicate timelines |
| Users without segment bypass IB | Highest-impact residual risk | 100% segment coverage attestation; HR-of-record-driven attribute sync |
| Channel Agents do not consistently inherit per-invoker IB | Cross-segment leakage in shared channels | Compensating controls, channel-membership restriction, Zone 3 prohibition |
| Graph-connector indexes are not IB-segmented by default | M365 Copilot can surface cross-segment connector content | Curate connector indexes per segment; Control 1.4 and 1.7 compensations |
| External / DirectLine surfaces have no IB context | Cross-segment leakage if exposed externally | Do not expose IB-protected agents externally; use compensating data-scope restrictions |
| `MultiSegment` mode mail-flow semantics differ from `Legacy` | Mail-flow assumptions from Legacy may no longer hold | Supplement with Exchange transport rules where hard mail-flow blocking is required |
| Migration `Legacy` → modern is one-way | Cannot revert in tenant | Plan migration carefully; Compliance + change-board approval |
| Up to 5,000 segments and 10 segments-per-user | Hard ceiling for very complex firms | Consolidate segments by regulatory boundary, not org-chart granularity |

---

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
