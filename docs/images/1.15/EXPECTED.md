# Control 1.15: Encryption (Data in Transit and at Rest)

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-m365-security-settings.png` | M365 | Settings → Org settings → Security & privacy | Security settings overview |
| `02-purview-encryption-settings.png` | Purview | Information protection → Encryption | Encryption configuration |
| `03-purview-customer-key.png` | Purview | Encryption → Customer Key | Customer-managed keys setup |
| `04-purview-label-encryption.png` | Purview | Labels → [label] → Encryption | Label encryption settings |
| `05-ppac-environment-encryption.png` | PPAC | Environments → [env] → Settings → Encryption | Environment encryption settings |
| `06-ppac-cmk-settings.png` | PPAC | Encryption → Customer-managed key | CMK configuration |
| `07-spac-encryption-settings.png` | SPAC | Settings → Encryption | SharePoint encryption settings |
| `08-azure-keyvault.png` | Azure | Key Vaults → [vault] | Key vault for CMK |

## Verification Focus

- TLS 1.2+ enforced for all connections
- Customer-managed keys configured for Zone 3
- Sensitivity labels enforce encryption
- Key vault access policies are restrictive
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.15-01-m365-security-settings.png` — Security settings overview
- `1.15-02-purview-encryption-settings.png` — Encryption configuration
- `1.15-03-purview-customer-key.png` — Customer-managed keys setup
- `1.15-04-purview-label-encryption.png` — Label encryption settings
- `1.15-05-ppac-environment-encryption.png` — Environment encryption settings
- `1.15-06-ppac-cmk-settings.png` — CMK configuration
- `1.15-07-spac-encryption-settings.png` — SharePoint encryption settings
- `1.15-08-azure-keyvault.png` — Key vault for CMK
