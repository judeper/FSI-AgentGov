# Control 1.10: Communication Compliance Monitoring

**Checklist documentation aligned:** 2026-10-16. No tenant/UI execution or screenshot capture was performed; this is not a renewed UI-verification date.

Use the [Portal Walkthrough](../../playbooks/control-implementations/1.10/portal-walkthrough.md) for setup and the [Verification & Testing catalog](../../playbooks/control-implementations/1.10/verification-testing.md) for test IDs, processing windows, and evidence requirements. Paths below start in the Microsoft Purview portal (`https://purview.microsoft.com`); confirm the actual tenant labels at capture time and record any divergence rather than asserting an unobserved path.

## Expected Screenshots

Filenames are capture stems; append the UTC timestamp before `.png` as described below. Repeat policy/source-specific captures with distinct policy and source identifiers.

| Capture stem | Navigation Path | What to Capture |
|--------------|-----------------|-----------------|
| `1.10-01-purview-comm-compliance-home` | Communication Compliance | Solution landing page and capture context; not proof of source coverage |
| `1.10-02-purview-comm-policies` | Communication Compliance → Policies | Actual policy names, IDs and status; reconcile to policy inventory |
| `1.10-03-purview-comm-create-policy` | Communication Compliance → Policies → Create policy | Approved template/custom-policy choice, scoped users/groups and assigned reviewers; do not create or change a policy solely to take a screenshot |
| `1.10-04-purview-comm-conditions` | Communication Compliance → Policies → select policy → Edit policy → Choose conditions and review percentage | Actual conditions, direction where exposed, review percentage and OCR state; use Customize policy in template creation flows where needed |
| `1.10-05-purview-comm-classifiers` | Same policy conditions page as capture 04 | Every enabled classifier/SIT/keyword condition; identify the policy, not a generic Classifiers page |
| `1.10-06-purview-comm-pending` | Communication Compliance → Policies → select policy → Pending | Observed test item, matched condition, policy/message identifiers and UTC window, separately for each required onboarded source |
| `1.10-07-purview-comm-review` | Same policy → Pending → open observed item | Authorized review view and actual tag/notify/escalate outcomes per 1.10-INV-01; use separate action captures rather than assuming all actions produce tag events |
| `1.10-08-purview-comm-reports` | Communication Compliance → Reports → Policy settings and status | Configuration/status evidence; retain the actual report export separately |
| `1.10-09-purview-comm-privacy` | Settings (upper-right) → Communication Compliance → Privacy | Show anonymized versions of usernames state; retain approved change-register evidence for any opt-out (1.10-PSE-01) |
| `1.10-10-purview-comm-preservation-global` | Settings (upper-right) → Communication Compliance → Policy Match Preservation | Current global preservation period (1.10-PMP-01) |
| `1.10-11-purview-comm-preservation-policy` | Communication Compliance → Policies → select policy → Edit policy → Name and describe your policy → Preserve policy matches | Global Setting inheritance or explicit override; record both the selected choice and effective period |
| `1.10-12-purview-comm-ai-locations` | Communication Compliance → Policies → select policy → Edit policy → Choose locations to detect communications | Required selections under Microsoft Copilot experiences, Enterprise AI apps and Other AI apps; document unused categories as not applicable with rationale (1.10-COP-01) |
| `1.10-13-source-interaction` | Each approved source application's actual interaction surface | Synthetic prompt/interaction with source identity and UTC context; capture each required onboarded source independently and pair with capture 06 and audit evidence |

## Verification Focus

- Confirm actual policy scope, assigned reviewers and effective permissions. Role-group membership alone does not establish per-policy reviewer access; retain scoped/unrestricted and assigned/unassigned comparisons where required by the verification catalog.
- Separate reproducible classifier samples from a separately identified 100% keyword/no-condition transport control. Record expected versus observed classifier results for every enabled classifier; an FSI-themed phrase is not a deterministic violation trigger.
- Capture each required AI source's onboarding, entitlement and PAYG evidence references. A selected location or one Copilot Chat match does not validate other sources; non-M365 AI data requires PAYG even under Microsoft Copilot experiences.
- Keep send, detection, review-action and audit-observation UTCs separate. Apply the source-specific processing guidance in the verification catalog; an empty Pending queue or an incomplete/early query is not a PASS.
- Retain complete paged audit-query exports and completion/count metadata, correlating actual policy/message identifiers and raw payloads. `SupervisionRuleMatch` is match evidence; `SupervisoryReviewTag` is tag evidence. Reviewer activity is not a detection feed. See the [PowerShell Setup](../../playbooks/control-implementations/1.10/powershell-setup.md) and [Troubleshooting](../../playbooks/control-implementations/1.10/troubleshooting.md) guides.
- Preserve privacy settings and attributable before/after change-register evidence where changes occur. Do not invent a global privacy/preservation audit operation or infer no change from an empty field search.
- Record preservation inheritance/override and effective period. Changes are prospective and do not recover expired copies. Policy Match Preservation is not the records-retention control under SEC 17a-4; retain the separate Control 1.9 evidence reference.
- Keep **Policy settings and status**, **Export policy updates**, and the policy Overview's **Export review activities** as distinct exports. Screenshots supplement, not replace, configuration, lifecycle and reviewer-action evidence.
- Use an approved pre-production/test population when possible. Protect identities and message content according to firm policy; preserve anonymized views and capture resolved identities only with authorization. Capture additional encryption, eDiscovery and negative-test views only as required by the corresponding verification test.
- Include UTC timestamps and observed tenant/UI context; record missing captures and unresolved tenant behavior as gaps, not successful verification. No portal changes, tests or privileged actions are authorized by this checklist alone.

---

## Screenshot Organization

Store screenshots and tenant evidence **locally only** under `maintainers-local\tenant-evidence\1.10\`, not in this checklist directory and never in GitHub. Only this checklist text is tracked.

Use `{capture-stem}_{policy-id}_{source-id}_{YYYYMMDD-HHmmss-UTC}.png`, omitting policy/source components only for global settings. For example: `1.10-06-purview-comm-pending_{policy-id}_{source-id}_{YYYYMMDD-HHmmss-UTC}.png`. This replaces the older unprefixed filename list and generic Alerts/Review filenames.

Keep a local manifest mapping each capture to the verification test ID, policy/source/message identifiers, authorized observer, UTC observation, related exports/change ticket and any limitations. Retain SHA-256 sidecars per the verification catalog. Hashes and a local folder do not establish immutable archival; apply the firm's approved evidence-storage and retention procedures separately.
