# Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-purview-sits-list.png` | Purview | Data classification → Classifiers → Sensitive info types | SITs list |
| `02-purview-sits-financial.png` | Purview | SITs → Filter: Financial | Financial SITs (SSN, account numbers) |
| `03-purview-sits-create.png` | Purview | SITs → Create | Custom SIT creation |
| `04-purview-sits-patterns.png` | Purview | SIT → Patterns | Pattern configuration |
| `05-purview-edm-classifiers.png` | Purview | EDM classifiers | Exact Data Match classifiers |
| `06-purview-trainable-classifiers.png` | Purview | Trainable classifiers | Trainable classifier list |
| `07-purview-content-explorer.png` | Purview | Data classification → Content explorer | Content with SIT detections |
| `08-purview-activity-explorer.png` | Purview | Activity explorer | SIT-related activities |

## Verification Focus

- FSI-relevant SITs are enabled (account numbers, SSN, etc.)
- Custom SITs for organization-specific patterns
- Content explorer shows SIT coverage
- EDM configured for customer data matching
