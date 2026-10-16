# Control 1.7: Comprehensive Audit Logging and Compliance

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-purview-audit-search.png` | Purview | Audit → Search | Audit log search interface |
| `02-purview-audit-results.png` | Purview | Audit → Search → select completed search | Sample metadata and raw `CopilotEventData`; no expectation of verbatim prompt text |
| `03-purview-audit-retention.png` | Purview | Audit → Policies | Applicable policy scope, priority, duration, and license evidence |
| `04-purview-audit-export.png` | Purview | Audit → Search → select completed search | Export options and result counts; distinguish portal from PowerShell limits |
| `05-ppac-activity-logs.png` | PPAC | Manage → Environments → select environment → Settings → Audit and logs → Audit settings | Dataverse environment auditing; capture approved table/column settings separately |
| `06-purview-payg-association.png` | Purview | Settings → Account details | Azure subscription association; verify applicable collection policy separately |
| `07-entra-agent-filters.png` | Entra | Entra ID → Monitoring & health → Sign-in logs | Is Agent / Agent type filters and a known agent sign-in |
| `08-sentinel-copilot-ingestion.png` | Sentinel | Logs → query `CopilotActivity` | Known Purview audit ID matched to `RecordId`; redact customer identifiers |

## Verification Focus

- Audit logging is enabled for all workloads
- Retention meets regulatory requirements (7 years for FSI)
- Power Platform activities are captured
- Export functionality works for examinations
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.7-01-purview-audit-search.png` — Audit log search interface
- `1.7-02-purview-audit-results.png` — Sample audit log results
- `1.7-03-purview-audit-retention.png` — Audit retention configuration
- `1.7-04-purview-audit-export.png` — Export options for compliance
- `1.7-05-ppac-activity-logs.png` — Power Platform activity logs
- `1.7-06-purview-payg-association.png` — PAYG subscription association
- `1.7-07-entra-agent-filters.png` — Documented agent sign-in filters
- `1.7-08-sentinel-copilot-ingestion.png` — Known-record ingestion evidence

**Documentation review: 2026-10-16.** These are capture requirements, not completed UI verification. See the [troubleshooting source register](../../playbooks/control-implementations/1.7/troubleshooting.md#documentation-re-verification-sources) for live Microsoft Learn references. Keep screenshots and tenant evidence local in `maintainers-local/tenant-evidence/`; do not commit images.
