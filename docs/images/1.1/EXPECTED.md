# Control 1.1: Restrict Agent Publishing by Authorization

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-entra-create-security-group.png` | Entra | Groups → New group | Security group creation dialog with "Agent Makers" name |
| `02-entra-group-members.png` | Entra | Groups → Members | Adding members to the security group |
| `03-ppac-environment-settings.png` | PPAC | Environments → [env] → Settings | Environment settings panel |
| `04-ppac-security-roles.png` | PPAC | Environments → Security roles | Security roles list and assignment |
| `05-ppac-maker-permissions.png` | PPAC | Environments → Users + permissions | Maker permission configuration |
| `06-copilot-settings-access.png` | Copilot | Settings → Security | Access restriction settings in Copilot Studio |
| `07-copilot-verify-restricted.png` | Copilot | Copilots list | Verification that unauthorized users cannot create |

## Verification Focus

- Security group type is "Security" (not M365)
- PPAC shows security group assigned to environment
- Copilot Studio shows access is restricted to group members
