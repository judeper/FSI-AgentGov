# Control 1.9: Data Retention and Deletion Policies

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-purview-retention-labels.png` | Purview | Data lifecycle management → Labels | Retention labels list |
| `02-purview-retention-create.png` | Purview | Labels → Create label | Retention label creation |
| `03-purview-retention-settings.png` | Purview | Label → Settings | Retention period and action settings |
| `04-purview-retention-policies.png` | Purview | Policies | Retention policies list |
| `05-purview-policy-locations.png` | Purview | Policy → Locations | Policy scope (SharePoint, Exchange, etc.) |
| `06-purview-disposition.png` | Purview | Disposition | Disposition review queue |
| `07-purview-records-management.png` | Purview | Records management | Records management dashboard |
| `08-ppac-data-policies.png` | PPAC | Environments → Data management | Environment data settings |

## Verification Focus

- Retention labels match FSI requirements (6-7 years)
- Policies cover all locations with agent data
- Disposition review is configured for regulated content
- Records management supports immutable retention
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.9-01-purview-retention-labels.png` — Retention labels list
- `1.9-02-purview-retention-create.png` — Retention label creation
- `1.9-03-purview-retention-settings.png` — Retention period and action settings
- `1.9-04-purview-retention-policies.png` — Retention policies list
- `1.9-05-purview-policy-locations.png` — Policy scope (SharePoint, Exchange, etc.)
- `1.9-06-purview-disposition.png` — Disposition review queue
- `1.9-07-purview-records-management.png` — Records management dashboard
- `1.9-08-ppac-data-policies.png` — Environment data settings
