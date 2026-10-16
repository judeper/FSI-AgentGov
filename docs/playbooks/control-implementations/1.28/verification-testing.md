# Verification & Testing: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** October 2026<br>
**Test Environment:** Pre-production / dedicated test environments per zone<br>
**Estimated Time:** 45–60 minutes for the full test pass

## Overview

This playbook defines test cases that confirm policy-based publishing restrictions are operational across Zone 1, Zone 2, and Zone 3. Tests focus on what the platform actually enforces (DLP at runtime and publish time, channel allowlisting, audit capture) and what the organization enforces around the platform (approval gates via Power Automate or Pipelines, change-control documentation).

> **Verification scope:** Product claims were checked against live Microsoft Learn on 2026-10-14; these tenant tests have not been executed by that documentation review. Publish-dialog labels evolve. DLP errors, automatic security warnings, and configured approval gates are separate signals; record what the tenant actually shows.

---

## Prerequisites

- [ ] DLP policies configured and assigned per Step 2 of the [Portal Walkthrough](portal-walkthrough.md)
- [ ] One test environment per zone (Zone 1, Zone 2, Zone 3) — or at least one production-equivalent test environment for the highest zone in scope
- [ ] A non-admin Copilot Studio Agent Author account for tests that exercise approval gates (admins can bypass surrounding workflow)
- [ ] Power Platform Admin account for the approver-side tests
- [ ] Microsoft Purview Audit confirmed enabled with sufficient retention

---

## Test Case 1 — DLP Blocks Publish When the Agent Uses a Blocked Connector

**Objective:** Confirm that the platform-level DLP enforcement prevents publish when the agent's connector usage conflicts with the assigned DLP policy.

**Steps:**

1. In a Zone 3 test environment, create a new agent named `T1-DLP-Violation`.
2. Add a topic with an **HTTP request** node and a test URL; confirm HTTP is Blocked by the policy assigned to this environment.
3. Save the agent and click **Publish**.

**Expected:**

- [ ] The Copilot Studio pre-publish dialog surfaces a DLP-related finding identifying the HTTP connector.
- [ ] The publish action does not complete; the agent remains in its prior state (or `Draft` if never published).

**Evidence:**

- Screenshot of the pre-publish finding with the connector identified.
- Export of the assigned DLP policy showing HTTP as Blocked, plus **Channels -> Details -> Download** with DLP violations and Blocked channels sheets.

---

## Test Case 2 — DLP-Compliant Agent Publishes Cleanly

**Objective:** Confirm that an agent using only allowed connectors publishes through the platform check.

**Steps:**

1. In the same Zone 3 test environment, create `T2-DLP-Compliant` using only SharePoint (read-only) and Dataverse (approved tables).
2. Click **Publish** and observe the pre-publish dialog.

**Expected:**

- [ ] No DLP findings are surfaced.
- [ ] Publication completes after the organization's required approval. A standalone approval flow does not automatically intercept Publish.
- [ ] The documented `BotUpdateOperation-BotPublish` event can be retrieved in Purview after ingestion; record actual latency rather than assuming a fixed delivery deadline.

---

## Test Case 3 — Channel Restrictions Are Enforced

**Objective:** Confirm that public channels disabled for the environment cannot be enabled by the author.

**Steps:**

1. In a Zone 2 test environment, open a compliant agent and select **Channels** on the top menu.
2. Confirm the policy blocks **Facebook channel in Copilot Studio** and/or **Direct Line channels in Copilot Studio**, then attempt to configure the corresponding channel.

**Expected:**

- [ ] The channel is not available, or the agent fails to publish with the channel enabled.
- [ ] Authenticated channels (Microsoft Teams, authenticated web channel) remain available.

> **Hedge:** Whether the public channel is hidden, disabled, or only blocked at publish time depends on the current Copilot Studio build and the DLP/connector configuration. The verifiable outcome is that the agent cannot reach end users via the prohibited channel.

Telegram is an Azure Bot Service integration, not a documented standalone Copilot Studio Telegram DLP connector. Test its actual integration separately if used; blocking a service connector is not evidence of channel enforcement.

---

## Test Case 4 — Approval Gate Triggers (Power Automate Implementation)

**Objective:** Confirm that the organization's explicit release request reaches the configured approval workflow before release.

**Steps:**

1. As a non-admin Agent Author, submit a release request through the configured intake form/change ticket for a compliant Zone 2 agent.
2. Switch to the approver account and check the Approvals app in Microsoft Teams (or email).

**Expected:**

- [ ] An approval request appears for the approver, naming the agent, environment, and submitter.
- [ ] Approving the request writes a row to the `Publish Approval Log` Dataverse table (or chosen audit sink) with approver UPN, timestamp, and decision.
- [ ] Rejecting the request writes the rejection record and notifies the author.

> **Important:** This test confirms approval capture, not interception of Publish. A `bot` create/update flow is detective and not a documented publish trigger. Use **Test Case 6** to test production role restrictions and the configured pipeline gate; Test Case 7 tests DLP, not approval enforcement.

---

## Test Case 5 — Multi-Stage Approval (Zone 3, Power Automate or Pipelines)

**Objective:** Confirm that Zone 3 agents require both Power Platform Admin and Compliance Officer approval (or the equivalent two-stage pipeline gate).

**Steps:**

1. Submit a Zone 3 agent for publish (via Power Automate flow) or queue a deployment from Test → Production in Power Platform Pipelines.
2. Approve at stage 1 (Power Platform Admin); confirm the request advances to stage 2.
3. Approve at stage 2 (Compliance Officer); confirm the publish/deployment completes.
4. Repeat with a rejection at stage 2 to confirm the deployment is halted.

**Expected:**

- [ ] Stage 1 approval is required before stage 2 is reachable.
- [ ] Rejection at either stage halts deployment and records the decision.
- [ ] Both decisions appear in the configured approval store/pipeline run history and are correlated to the deployment. Do not expect native Copilot Studio approval events in Purview.

Only a pipeline extension wired to complete/reject its pending stage prevents deployment. An approval initiated after publication cannot undo that publication by itself.

---

## Test Case 6 — Solution Promotion via Power Platform Pipelines (Zone 3)

**Objective:** Confirm that Zone 3 agents are deployed via the pipeline rather than published directly into production.

**Steps:**

1. In the Zone 3 development environment, package the agent into a solution.
2. Submit the deployment from Dev → Test via the pipeline.
3. After test sign-off, submit Test → Production with the configured pre-deployment approval.

**Expected:**

- [ ] The agent reaches production only via solution import, not via direct publish.
- [ ] The pipeline run history shows each stage, approver, and timestamp.
- [ ] Direct publish in the production environment is prevented because the production-environment Dataverse role for non-pipeline service principals lacks `prvCreateBot` / `prvWriteBot` (configured per **Control 1.1**).

> **Hedge:** Power Platform Pipelines does not, by itself, prevent a sufficiently privileged user from publishing in place. The technical prevention comes from the role design in Control 1.1; this test confirms the pipeline path is the supported path.

---

## Test Case 7 — Update and Runtime Impact When DLP Policy Tightens

**Objective:** Confirm the Microsoft platform behavior that published agents whose connector usage no longer aligns with the assigned DLP policy are blocked from update operations until the violation is resolved.

**Steps:**

1. Publish a compliant agent in a test environment using a **blockable** connector, such as HTTP, currently allowed.
2. Move HTTP to **Blocked** in the assigned data policy. Do not use the SharePoint service connector, which is unblockable.
3. Make a small edit to the agent and click **Publish** to update.

**Expected:**

- [ ] Publish/Channels error details identify HTTP and the enforcing policy.
- [ ] The update is blocked.
- [ ] Test the published agent in a new end-user session and capture any `DataLossPreventionViolation` error. A blocked update does not imply continued runtime availability.

**Evidence:**

- Screenshots showing the pre-change publish, the DLP change, and the post-change blocked update.
- Channels violation workbook and runtime result. Restore the test policy/agent and confirm recovery. [Microsoft's troubleshooting guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-dlp-troubleshooting) documents exemption removal since March 2025 and published-agent runtime errors.

---

## Test Case 8 — Audit Capture in Microsoft Purview

**Objective:** Confirm that publish-related events reach Purview with sufficient detail for evidence.

**Steps:**

1. Perform a successful publish, a blocked publish, and a DLP policy change in test environments.
2. In Purview → Solutions → Audit, search the previous 24 hours for Copilot Studio authoring activities, including `BotUpdateOperation-BotPublish` and `BotCreate`. See [documented events and fields](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio).

**Expected:**

- [ ] Successful publish events are present; inspect actual Operation, CreationTime, user, ResultStatus, and BotId/BotSchemaName fields where available and correlate to the environment.
- [ ] Blocked-publish and DLP details are retained from Channels error/workbook evidence; do not require a native Purview "DLP policy violation detected" event.
- [ ] Approval identity, timestamp, and decision are retained from the configured Power Automate/pipeline store; do not require a Purview "Approve chatbot publishing request" event.
- [ ] Retention on these events meets your firm's requirement (commonly 7 years for FINRA 4511 / SEC 17a-4 alignment).

---

## Test Case 9 — Inventory Script Produces Auditable Evidence

**Objective:** Confirm the Dataverse inventory export and Script 4 from the [PowerShell Setup](powershell-setup.md) produce reconciled CSV evidence with a SHA-256 hash.

**Steps:**

1. Export the Bots inventory per the PowerShell playbook; reconcile environment coverage and pagination, and record any collection failures.
2. Run `Hash-AgentInventory.ps1 -CsvPath '<inventory.csv>'` and open the CSV and `.sha256.txt` manifest.

**Expected:**

- [ ] CSV includes EnvironmentId, botid, name, and modifiedon; creator identity is resolved where collected. Publication state is reviewed separately, not inferred from active/inactive state.
- [ ] Manifest file contains `<csvPath>\tSHA256:<hash>` entries for each export.
- [ ] Recomputing `Get-FileHash -Algorithm SHA256` on the CSV yields the same hash.

---

## Compliance Verification Checklist

After all tests:

- [ ] DLP policies enforce connector restrictions per zone (Test 1, 2, 7).
- [ ] Channel restrictions are operational for Zone 2+ (Test 3).
- [ ] An approval gate exists for Zone 2+ environments (Test 4).
- [ ] A multi-stage approval gate exists for Zone 3 (Test 5).
- [ ] Solution promotion is the supported path to production for Zone 3 (Test 6).
- [ ] Published agents whose connector usage drifts out of compliance are blocked from update (Test 7).
- [ ] Purview publish events, Channels DLP evidence, and configured approval records are retained and correlated (Test 8).
- [ ] Inventory automation produces hashed evidence files (Test 9).

---

## Evidence Package

Compile the following for the control evidence file:

1. **DLP configuration:** Export of each zone's DLP policy and the list of environments assigned to each.
2. **Pre-publish enforcement:** Screenshots from Tests 1, 2, 3, and 7.
3. **Approval workflow:** Power Automate flow definition (or pipeline definition) plus a sample approval record from Tests 4 and 5.
4. **Pipeline run:** Pipeline run history export from Test 6.
5. **Audit:** Purview audit export covering the test window (CSV).
6. **PowerShell evidence:** Inventory CSV and SHA-256 manifest from Test 9.

---

## Ongoing Monitoring

| Cadence | Activity |
|---------|----------|
| Weekly | Refresh the configured Dataverse inventory export and hash it with Script 4; review Purview publish events and separate Channels DLP findings. |
| Monthly | Review approval workflow metrics (volume, approval rate, mean time to approve). |
| Quarterly | Audit DLP policy effectiveness; review connector classifications against business and regulatory changes. |
| Annually | Re-baseline zone-to-policy mappings; review evidence retention against current FINRA / SEC / GLBA / OCC / Fed SR 26-2 (formerly SR 11-7) expectations. |

---

## Attestation Statement Template

```markdown
## Control 1.28 Attestation - Policy-Based Agent Publishing Restrictions

**Organization:** [Organization Name]
**Control Owner:** [Name / Role]
**Date:** [Date]

I attest that, as of the date above:

1. DLP policies are configured and assigned per zone:
   - Zone 1 environments: [Count]
   - Zone 2 environments: [Count]
   - Zone 3 environments: [Count]
2. Pre-publish DLP enforcement is operational (Test Cases 1, 2, 7 passed): [Yes / No]
3. Channel restrictions are operational for Zone 2+ (Test Case 3): [Yes / No]
4. Approval gates are operational:
   - Zone 2 single-stage (Test 4): [Yes / No]
   - Zone 3 multi-stage (Test 5): [Yes / No]
5. Zone 3 production deployments use Power Platform Pipelines or ALM Accelerator (Test 6): [Yes / No]
6. Purview publish events, Channels DLP findings, and workflow approval records are retained in their respective evidence stores for [N] years (Test 8): [Yes / No]
7. Inventory automation produces hashed evidence files (Test 9): [Yes / No]

**Signature:** ______________________
**Date:** __________________________
```

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Current (Microsoft Learn review 2026-10-14; tenant tests pending)*
