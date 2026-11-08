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

## Verification Focus

- Model inventory is complete and current
- Validation documentation exists for each agent
- Risk ratings are assigned and reviewed
- Ongoing monitoring is documented

**Last Verified:** 2026-11-06 — targeted model/evidence checklist correction only; no tenant UI/screenshots tested. Capture provider/retention route and separate Microsoft 365/PPAC settings per the [vendor-model procedure](../../playbooks/control-implementations/2.6/portal-walkthrough.md#41-capture-vendor-model-selection-and-provider-evidence). Store screenshots locally under `maintainers-local/tenant-evidence/`.
