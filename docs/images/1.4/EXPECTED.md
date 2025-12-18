# Control 1.4: Advanced Connector Policies (ACP)

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-ppac-environment-groups.png` | PPAC | Manage → Environment groups | Environment groups list |
| `02-ppac-create-env-group.png` | PPAC | Environment groups → New | Environment group creation dialog |
| `03-ppac-env-group-members.png` | PPAC | Environment groups → [group] | Environments in group |
| `04-ppac-managed-env-enable.png` | PPAC | Environments → [env] → Enable Managed | Managed environment enablement dialog |
| `05-ppac-managed-env-settings.png` | PPAC | Environments → [env] → Edit Managed | Managed environment settings panel |
| `06-ppac-acp-navigation.png` | PPAC | Policies → Advanced connector policies | ACP section navigation |
| `07-ppac-acp-list.png` | PPAC | Advanced connector policies | List of connector policies |
| `08-ppac-acp-create.png` | PPAC | ACP → New policy | Policy creation wizard |
| `09-ppac-acp-connectors.png` | PPAC | ACP → [policy] → Connectors | Connector restrictions configuration |
| `10-ppac-acp-endpoints.png` | PPAC | ACP → [policy] → Endpoints | Endpoint filtering rules |

## Verification Focus

- Environment groups properly categorize by zone
- Managed Environments enabled for production
- ACP policies restrict connectors appropriately
- Endpoint filtering blocks unauthorized external connections
