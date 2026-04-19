# Control 2.16: RAG Source Integrity Validation — Troubleshooting

> Diagnostic and remediation guidance for [Control 2.16: RAG Source Integrity Validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md).
>
> **Audience:** SharePoint Admins, Power Platform Admins, AI Administrators, and SOC Analysts responding to RAG-source incidents in regulated tenants.

---

## Triage Quick Reference

| Symptom | Likely cause | First action |
|---------|--------------|--------------|
| Agent returns "I don't know" for content that exists | Document is not approved (still a draft / minor version), or filter excludes it | Verify approval status and `Approved For Agents` column |
| Citations missing from agent responses | Citation setting disabled, response not grounded, or channel suppresses citations | Re-test the same prompt in M365 Chat or Teams; check agent settings |
| Agent surfacing outdated content | Index has not refreshed since the major version was published | Wait the documented index window (up to 24h); confirm the new version is the current major |
| Unauthorized knowledge source bound to an agent | Maker added the source without approval | Remove the binding; capture evidence; review maker permissions and Power Platform DLP |
| Validation script returns zero items in GCC High | Connected to commercial endpoints (false-clean) | Re-run with `-Cloud GCCHigh` and the correct PnP `-AzureEnvironment` |
| `Get-AdminPowerAppEnvironmentRoleAssignment` returns nothing | Environment is Dataverse-backed | Use PPAC Dataverse Security Roles, not the cmdlet (baseline section 6) |
| `Test-LibraryHardening.ps1` reports `FAIL` on `Modified` field references | Field internal name differs in classic vs modern sites | Confirm via `Get-PnPField -List $lib` and update the script's field reference |
| Power Automate approval flow not firing | Trigger scoped to wrong library, or flow disabled | Open flow run history; re-confirm the SharePoint trigger scope |
| Staleness alert fires for documents that were just edited | `Modified` is metadata-touch, not content-change | Switch to RAG Source Validator solution (SHA-256-based drift) |

---

## Detailed Troubleshooting

### Issue 1 — Agent cannot find content that exists

**Symptoms:** Agent responds with a non-grounded answer or refuses, even though the source document is in the bound library.

**Diagnostic steps:**

1. Confirm the document is approved as a major version:
    - Open the library → select the document → **Version history** → confirm the current row is a major version (e.g., `2.0`, not `1.5`)
    - **Approval Status** column must read `Approved`
2. Confirm the FSI metadata is populated:
    - `Approved For Agents` must contain the agent's identifier (case-sensitive — verify exact value)
    - `Classification` must be set
3. Re-open the agent's knowledge source filter in Copilot Studio and confirm the filter expression matches the document's metadata
4. Check index propagation: Copilot Studio knowledge index refreshes are platform-driven and asynchronous; allow up to 24 hours after a content or metadata change
5. Run `Test-LibraryHardening.ps1` and confirm the library reports `Status = PASS`

**Remediation:**

- Approve the document as a major version, populate `Approved For Agents`, and re-test after the index window
- If the filter expression is too narrow, broaden it in Copilot Studio and capture the change in the source-approval evidence library

### Issue 2 — Citations not rendered

**Symptoms:** Agent provides correct content but does not show source citations.

**Diagnostic steps:**

1. Open the agent → **Settings** → **Generative AI** → confirm **Include source citations in responses** is enabled
2. Test the same prompt on a different channel (Microsoft Teams, M365 Copilot Chat, custom website)
3. Confirm the response is **grounded** — non-grounded generative answers (model-only) do not produce citations by design

**Remediation:**

- Enable citation display in agent settings and republish the agent
- For embedded SDK channels that suppress citations, document the channel as **out-of-scope for Zone 3** and route users to a channel that renders citations
- For non-grounded answers, tighten the agent's grounding settings or add the relevant content to a bound knowledge source

### Issue 3 — Agent uses outdated content

**Symptoms:** Agent returns information from a previous major version after a new major version was published.

**Diagnostic steps:**

1. Open **Version history** on the document; confirm the new major version is the most recent row and is *Approved*
2. Note the publish timestamp; compare to the index window (up to 24 hours)
3. Re-run the agent test in an InPrivate / incognito browser session to bypass any client cache

**Remediation:**

- Wait the full index window before declaring this a defect
- If the issue persists beyond 48 hours, open a Microsoft support ticket and capture the document URL, agent ID, and version timestamps
- Add a row to the source-approval evidence library noting the support ticket

### Issue 4 — Unauthorized knowledge source bound to an agent

**Symptoms:** Drift between two consecutive `agent-knowledge-bindings-*.json` snapshots reveals a source that is not in the approved-sources register.

**Diagnostic steps:**

1. Identify the agent and source from the diff CSV
2. Open the agent in Copilot Studio → **Knowledge** → confirm the source is present
3. Check Copilot Studio audit logs (via Purview Audit) for the `BotComponentCreated` event to identify the maker who added the source

**Remediation:**

- Remove the binding immediately
- Open an incident ticket per the [Incident Response playbook](../../incident-and-risk/ai-incident-response-playbook.md) (if applicable to your organization)
- Review the maker's environment permissions and the Power Platform DLP policy that should have prevented the addition
- Capture the audit event and the removal as evidence

### Issue 5 — Sovereign-cloud false-clean

**Symptoms:** `Test-LibraryHardening.ps1` returns "0 libraries found" against a tenant that you know has libraries.

**Diagnostic steps:**

1. Confirm the `-Cloud` parameter matches the tenant cloud (`Commercial`, `GCC`, `GCCHigh`, `DoD`)
2. Confirm `Connect-PnPOnline -AzureEnvironment` resolved to the right value (`Production`, `USGovernment`, `USGovernmentHigh`, `USGovernmentDoD`)
3. Try the equivalent operation in PnP interactively, e.g.:
    ```powershell
    Connect-PnPOnline -Url <site> -Interactive -AzureEnvironment USGovernmentHigh -ClientId <id>
    Get-PnPList | Select-Object Title, BaseTemplate, ItemCount
    ```

**Remediation:**

- Re-run with the correct `-Cloud` parameter
- File a finding noting that the previous "clean" run was false-clean and re-collect evidence

### Issue 6 — Dataverse compatibility on Power Apps admin cmdlets

**Symptoms:** `Get-AdminPowerAppEnvironmentRoleAssignment` returns empty silently, or `Set-` returns 403 Forbidden.

**Diagnostic steps:**

1. Confirm the environment has Dataverse:
    ```powershell
    (Get-AdminPowerAppEnvironment -EnvironmentName <id>).CommonDataServiceDatabaseProvisioningState
    ```
    A value of `Succeeded` indicates Dataverse is provisioned.

**Remediation:**

- For Dataverse environments, use **PPAC > Environment > Settings > Users + permissions > Security roles** instead of the admin cmdlets
- This is documented Microsoft behavior; it is not a defect

### Issue 7 — `Modified` date triggers spurious staleness alerts

**Symptoms:** Documents whose content has not changed appear in stale-content reports because metadata edits update `Modified`.

**Diagnostic steps:**

1. Confirm the document's `Editor` and last-edit reason — metadata-only edits are typically permission or column updates
2. Compare consecutive `stale-content-*.json` snapshots to identify whether the document churns repeatedly

**Remediation:**

- Switch the staleness signal from SharePoint `Modified` to the **content hash** maintained by the [RAG Source Validator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/rag-source-validator) solution
- Update the staleness Power Automate flow to read from the validator's Dataverse table

### Issue 8 — Approval flow not firing for new content

**Symptoms:** New uploads bypass approval and are immediately visible to the agent.

**Diagnostic steps:**

1. Open the flow in [Power Automate](https://make.powerautomate.com); inspect **28-day run history**
2. Confirm the trigger is scoped to the correct site and library
3. Confirm the flow owner / connection is still valid (look for connection-error rows in run history)
4. Confirm the library is set to **Require content approval = Yes** so that uploads land as `Pending` rather than auto-approved

**Remediation:**

- Re-scope the trigger or re-authorize the connection
- Re-enable content approval on the library
- Re-run the negative test from [Verification & Testing](verification-testing.md) Test 3

---

## Confirming the Configuration Is Active

### Via Copilot Studio

1. Open the agent → **Knowledge**
2. Confirm every listed source appears in the approved-sources register
3. Open **Settings** → **Generative AI** and confirm citation settings
4. Send a knowledge-bound test prompt and confirm the response includes a citation

### Via SharePoint

1. Open each library → **Library settings** → **Versioning settings**
2. Confirm:
    - **Require content approval** = Yes
    - **Major + minor versioning** = Enabled
    - **Draft Item Security** = Only approvers and the author
3. Open a sample document → **Version history** → confirm major / minor lifecycle is operating

### Via PowerShell

1. Run `Validate-Control-2.16.ps1` (see [PowerShell Setup](powershell-setup.md))
2. Confirm exit code 0 and that `manifest.json` includes the latest evidence files with SHA-256 hashes

### Via Power Automate

1. Open both flows (approval, staleness) and confirm **Status = On**
2. Inspect the most recent run history; both should show successful runs within the audit period

---

## Escalation Path

| Issue type | First responder | Escalate to |
|------------|-----------------|-------------|
| SharePoint library configuration | SharePoint Admin | SharePoint Site Collection Admin → Microsoft Support |
| Copilot Studio knowledge source binding | AI Administrator | Power Platform Admin → Microsoft Support |
| Power Automate flow failures | Power Platform Admin | Power Automate Admin → Microsoft Support |
| Content accuracy or staleness | Source Owner | Content Owner's manager → AI Governance Lead |
| Unauthorized binding (suspected insider risk) | AI Governance Lead | Compliance Officer → SOC Analyst |
| Sovereign-cloud connectivity / false-clean | SharePoint Admin | Microsoft Premier / Unified Support |

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Index refresh delay (up to 24 hours) | New approved content not immediately available to the agent | Plan content updates ahead of need; document the index window in service-level expectations |
| `Modified` is metadata-touch, not content-change | False-positive staleness alerts | Use the RAG Source Validator solution for content-hash drift detection |
| Citation rendering varies by channel | Embedded SDK channels may suppress citations | Restrict Zone 3 agents to channels that render citations |
| No built-in approval workflow in Copilot Studio | Requires Power Automate flow on the source library | Use the flow pattern in [Portal Walkthrough](portal-walkthrough.md) Part 4 |
| Per-user knowledge scoping not supported | All users with agent access see the same grounded knowledge | Use separate agents (and separate knowledge sources) per access tier |
| Bing Custom Search lacks per-result provenance | Internet-sourced grounding is not regulator-defensible | Prohibit Bing Custom Search in Zone 3 |
| `Get-AdminPowerAppEnvironmentRoleAssignment` silently returns empty on Dataverse environments | False-clean evidence risk | Detection guard in baseline section 6; use PPAC Dataverse Security Roles |

---

[Back to Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.3.3*
