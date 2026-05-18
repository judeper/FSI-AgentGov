# Control 2.15: Environment Routing

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-ppac-env-groups-list.png` | PPAC | Manage → Environment groups | List of FSI environment groups |
| `02-ppac-env-group-rules-published.png` | PPAC | Manage → Environment groups → \[group\] → Rules | Each rule in **Published** state (not Draft) |
| `03-ppac-tenant-settings-routing.png` | PPAC | Manage → Tenant settings → Environment routing | Routing toggle On + product portal selections |
| `04-ppac-routing-rule-list.png` | PPAC | Manage → Tenant settings → Environment routing | Ordered list of routing rules (audience → target group) |
| `05-ppac-routing-rule-detail.png` | PPAC | Manage → Tenant settings → Environment routing → \[rule\] | Single rule detail showing audience scope and target group |
| `06-test-maker-routed-env.png` | Microsoft Copilot Studio / PPAC | New maker session, then PPAC env detail | Auto-provisioned dev env appears in expected target group |

## Verification Focus

- Routing toggle is On at tenant level for the documented set of product portals
- Routing rules list ordered correctly (LOB groups above the Everyone catch-all)
- Each target environment group has its policy rules **Published**, not Draft
- A test maker is auto-provisioned into the expected environment group on first portal visit
- Inherited group rules appear locked in the routed environment's settings
