# Control 1.7: Comprehensive Audit Logging and Compliance

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-purview-audit-search.png` | Purview | Audit → Search | Audit log search interface |
| `02-purview-audit-results.png` | Purview | Audit → Results | Sample audit log results |
| `03-purview-audit-retention.png` | Purview | Audit → Retention policies | Audit retention configuration |
| `04-purview-audit-export.png` | Purview | Audit → Export | Export options for compliance |
| `05-ppac-activity-logs.png` | PPAC | Manage → Environments → selected environment → Settings → Audit and logs → Audit settings | Environment audit settings, retention, and applicable activity logging; selected table/column audit inventory captured separately |
| `06-m365-audit-settings.png` | Purview | Solutions → Audit | Unified audit configuration; keep the Exchange Online ingestion-status export alongside the screenshot |
| `07-sentinel-copilot-ingestion.png` | Sentinel | Data connectors → Microsoft Copilot; Logs → CopilotActivity | Connector state and the controlled event's `RecordId`, `ActorName`, event time, and first-observed UTC time |

## Verification Focus

- Audit logging is enabled for all workloads
- Retention meets regulatory requirements (7 years for FSI)
- Power Platform activities are captured
- Export functionality works for examinations
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
- Verify Dataverse row-change history separately from default Copilot Studio SDK administrative activity; do not require an invented six-table set
- Match the source Purview audit ID to `CopilotActivity.RecordId`; an `OfficeActivity` count or a prompt-text marker is not native Copilot ingestion proof

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.7-01-purview-audit-search.png` — Audit log search interface
- `1.7-02-purview-audit-results.png` — Sample audit log results
- `1.7-03-purview-audit-retention.png` — Audit retention configuration
- `1.7-04-purview-audit-export.png` — Export options for compliance
- `1.7-05-ppac-activity-logs.png` — Power Platform activity logs
- `1.7-06-m365-audit-settings.png` — M365 audit configuration
- `1.7-07-sentinel-copilot-ingestion.png` — Copilot connector and exact source-event correlation
