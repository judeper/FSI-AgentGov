# Control 1.4: Advanced Connector Policies (ACP)

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-ppac-environment-groups.png` | PPAC | Manage → Environment groups | Environment groups list |
| `02-ppac-create-env-group.png` | PPAC | Environment groups → New | Environment group creation dialog |
| `03-ppac-env-group-members.png` | PPAC | Environment groups → [group] | Environments in group |
| `04-ppac-managed-env-enable.png` | PPAC | Environments → [env] → Enable Managed | Managed environment enablement dialog |
| `05-ppac-managed-env-settings.png` | PPAC | Environments → [env] → Edit Managed | Managed environment settings panel |
| `06-ppac-acp-navigation.png` | PPAC | Environment groups → [group] → Rules → Advanced connector policies | ACP pane navigation |
| `07-ppac-acp-status.png` | PPAC | Environment groups → [group] → Rules → Advanced connector policies | Applied/not-applied portal status |
| `08-ppac-acp-add-connectors.png` | PPAC | Advanced connector policies → Add connectors | Certified connector selection |
| `09-ppac-acp-actions.png` | PPAC | Advanced connector policies → [connector] | Action restrictions configuration |
| `10-ppac-dlp-endpoints.png` | PPAC | Policies → Data policies → [policy] → Configure connector | Classic DLP endpoint filtering for HTTP coverage |

## Verification Focus

- Environment groups properly categorize by zone
- Managed Environments enabled for production
- ACP policies restrict connectors appropriately
- Classic DLP endpoint filtering restricts approved HTTP connections; endpoint filtering is not an ACP capability
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.4-01-ppac-environment-groups.png` — Environment groups list
- `1.4-02-ppac-create-env-group.png` — Environment group creation dialog
- `1.4-03-ppac-env-group-members.png` — Environments in group
- `1.4-04-ppac-managed-env-enable.png` — Managed environment enablement dialog
- `1.4-05-ppac-managed-env-settings.png` — Managed environment settings panel
- `1.4-06-ppac-acp-navigation.png` — ACP section navigation
- `1.4-07-ppac-acp-status.png` — Applied/not-applied portal status
- `1.4-08-ppac-acp-add-connectors.png` — Certified connector selection
- `1.4-09-ppac-acp-actions.png` — Action restrictions configuration
- `1.4-10-ppac-dlp-endpoints.png` — Classic DLP endpoint filtering for HTTP coverage
