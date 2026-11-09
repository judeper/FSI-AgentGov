# Control 3.6: Orphaned Agent Detection and Remediation - Screenshot Specifications

## Required Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-entra-user-status.png` | Entra | Users → User settings | User account status |
| `02-ppac-agent-owner.png` | PPAC | Agent → Owner | Owner information |
| `03-sharepoint-orphan-list.png` | SharePoint | Orphaned agent tracking | Orphan tracking list |
| `04-pauto-detection-flow.png` | Power Automate | Orphan detection flow | Automated detection |
| `05-pauto-notification-flow.png` | Power Automate | Notification flow | Owner departure alerts |
| `06-ppac-usage-analytics.png` | PPAC | Analytics → Usage | Inactive agent detection |
| `07-sharepoint-remediation-log.png` | SharePoint | Remediation log | Remediation records |
| `08-agent365-without-owners.png` | Microsoft 365 admin center | Agents > Overview > Agents without owners | Actual assigned-owner gap view, selected scope, timestamp, and supporting rows; not a disabled/departed-owner detector or an inferred Graph response |

## Notes for Verification

- Detection flow runs on schedule
- Orphaned agents are identified
- Notification triggers on owner departure
- Remediation is tracked
- Reconcile the captured Agent 365 ownerless view manually with the firm register; no generic governance API or supplied `Get-Agt36OwnerlessCard` adapter is established. Documentation cross-check: 2026-11-09; tenant/UI execution remains pending.
- Keep screenshots local under `maintainers-local/tenant-evidence/`; do not commit tenant evidence.

---

[Back to Control 3.6](../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
