# Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-purview-sits-list.png` | Purview | Solutions → Information protection → Classifiers → Sensitive info types | Available SIT definitions; availability alone is not consuming-policy configuration |
| `02-purview-sits-financial.png` | Purview | SITs → Filter: Financial | Financial SITs (SSN, account numbers) |
| `03-purview-sits-create.png` | Purview | SITs → Create | Custom SIT creation |
| `04-purview-sits-patterns.png` | Purview | SIT → Patterns | Pattern configuration |
| `05-purview-edm-classifiers.png` | Purview | EDM classifiers | Exact Data Match classifiers |
| `06-purview-trainable-classifiers.png` | Purview | Trainable classifiers | Trainable classifier list |
| `07-purview-content-explorer.png` | Purview | Solutions → Data Lifecycle Management → Explorers → Content explorer | Content with SIT detections, including selected SIT and location scope |
| `08-purview-activity-explorer.png` | Purview | Activity explorer | SIT-related activities |

## Verification Focus

- FSI-relevant SIT definitions are available (account numbers, SSN, etc.); separately capture their selection, confidence/count criteria, and scope in each applicable consuming policy
- Custom SITs for organization-specific patterns
- Content explorer shows observed SIT detections for the captured scope; this is not proof of complete coverage or Copilot runtime enforcement. Pair with the separate classifier and supported-path runtime tests in the 1.13 verification playbook
- EDM configured for customer data matching
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
- Record the actual tenant breadcrumb and explorer experience if different from these documented paths; this checklist update is documentation-only, not UI verification

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.13-01-purview-sits-list.png` — SITs list
- `1.13-02-purview-sits-financial.png` — Financial SITs (SSN, account numbers)
- `1.13-03-purview-sits-create.png` — Custom SIT creation
- `1.13-04-purview-sits-patterns.png` — Pattern configuration
- `1.13-05-purview-edm-classifiers.png` — Exact Data Match classifiers
- `1.13-06-purview-trainable-classifiers.png` — Trainable classifier list
- `1.13-07-purview-content-explorer.png` — Content with SIT detections
- `1.13-08-purview-activity-explorer.png` — SIT-related activities
