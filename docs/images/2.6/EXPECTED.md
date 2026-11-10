# Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-sharepoint-model-inventory.png` | SharePoint | Model inventory list | AI model/agent inventory |
| `02-sharepoint-model-card.png` | SharePoint | Model → Details | Model documentation card |
| `03-sharepoint-validation-log.png` | SharePoint | Validation tracking | Validation records |
| `04-copilot-agent-settings.png` | Copilot Studio | Agent → Overview → Model | Primary model, release tag and displayed version; record any exact version not exposed |
| `05-copilot-knowledge-sources.png` | Copilot | Agent → Knowledge | Knowledge sources documentation |
| `06-purview-audit-model.png` | Configured audit/telemetry surfaces | Actual supported activities in the review window | Available model-change evidence; no universal Model activities filter/event is assumed |
| `07-agent-registry-review.png` | Microsoft 365 admin center | Agents → All agents → Registry / Requests | Actual source scope, visible metadata and publication/activation decision; firm's MRM approval record is separate from the security template |
| `08-copilot-monitor.png` | Copilot Studio | Agent → Monitor | Applicable conversational/event-trigger metrics and collection window; no test-panel traffic or assumed failed-trigger coverage |
| `09-purview-evidence-label.png` | Purview and SharePoint | Approved label definition and sampled finalized evidence item | Applied label, retention start/duration and record status; policy-level Preservation Lock evidence is separate, not a fictional per-item deletionLocked field |

## Verification Focus

- Model inventory is complete and current
- Validation documentation exists for each agent
- Risk ratings are assigned and reviewed
- Ongoing monitoring is documented
- Reconcile the firm's register with supported Power Platform/Agent 365 inventories and Purview activity; activity absence is not agent absence
- Capture evaluator versions, release state and unsupported/skipped results; preview evaluators are not GA production dependencies

**Last Verified:** 2026-11-09 — targeted evidence checklist correction only; no tenant UI/screenshots tested. Capture provider/retention route and separate Microsoft 365/PPAC settings per the [vendor-model procedure](../../playbooks/control-implementations/2.6/portal-walkthrough.md#41-capture-vendor-model-selection-and-provider-evidence) and [verification procedure](../../playbooks/control-implementations/2.6/verification-testing.md). Store screenshots locally under `maintainers-local/tenant-evidence/`.
