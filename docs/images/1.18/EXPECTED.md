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
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.18-01-ppac-security-groups.png` — Security group assignment
- `1.18-02-ppac-security-roles.png` — Security roles list
- `1.18-03-ppac-role-details.png` — Role privileges configuration
- `1.18-04-ppac-custom-role.png` — Custom role creation
- `1.18-05-ppac-users-permissions.png` — User permission assignments
- `1.18-06-ppac-column-security.png` — Column-level security
- `1.18-07-entra-pim-roles.png` — Privileged roles list
- `1.18-08-entra-pim-assignments.png` — Role assignments (eligible/active)
- `1.18-09-entra-pim-settings.png` — Activation requirements
- `1.18-10-entra-access-reviews.png` — Access review configuration
