# Control 1.18: Application-Level Authorization and RBAC

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-ppac-security-groups.png` | PPAC | Environments → [env] → Settings → Security groups | Security group assignment |
| `02-ppac-security-roles.png` | PPAC | Environments → Settings → Security roles | Security roles list |
| `03-ppac-role-details.png` | PPAC | Security roles → [role] | Role privileges configuration |
| `04-ppac-custom-role.png` | PPAC | Security roles → Create | Custom role creation |
| `05-ppac-users-permissions.png` | PPAC | Environments → Users + permissions | User permission assignments |
| `06-ppac-column-security.png` | PPAC | Settings → Column security profiles | Column-level security |
| `07-entra-pim-roles.png` | Entra | Identity Governance → PIM → Roles | Privileged roles list |
| `08-entra-pim-assignments.png` | Entra | PIM → Assignments | Role assignments (eligible/active) |
| `09-entra-pim-settings.png` | Entra | PIM → Role settings | Activation requirements |
| `10-entra-access-reviews.png` | Entra | Identity Governance → Access reviews | Access review configuration |

## Verification Focus

- Security roles follow least-privilege principle
- PIM configured for privileged Power Platform roles
- Access reviews scheduled for role assignments
- Custom roles created for FSI-specific needs
