# Control 1.20: Network Isolation and Private Connectivity

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-ppac-environment-settings.png` | PPAC | Environments → [env] → Settings | Environment settings overview showing Privacy + Security |
| `02-ppac-ip-firewall.png` | PPAC | Environments → [env] → Settings → Privacy + Security → IP firewall | IP Firewall configuration with IP ranges |
| `03-ppac-vnet-config.png` | PPAC | Environments → [env] → Settings → Privacy + Security → Virtual Network | VNet configuration showing subscription, VNet, subnet selection |
| `04-azure-vnet-subnet.png` | Azure | Virtual Networks → [vnet] → Subnets | Subnet configuration with Power Platform delegation |
| `05-azure-keyvault-pe.png` | Azure | Key Vaults → [vault] → Networking → Private endpoint connections | Private endpoint configuration for Key Vault |
| `06-azure-keyvault-firewall.png` | Azure | Key Vaults → [vault] → Networking | Key Vault firewall settings (public access disabled) |
| `07-azure-appinsights-network.png` | Azure | Application Insights → [resource] → Network Isolation | App Insights private link configuration |
| `08-azure-ampls.png` | Azure | Azure Monitor Private Link Scope → [scope] | AMPLS configuration with linked resources |
| `09-azure-sql-pe.png` | Azure | SQL Server → [server] → Networking → Private endpoint connections | Private endpoint for Azure SQL |
| `10-azure-private-dns-zone.png` | Azure | Private DNS zones → [zone] | Private DNS zone with A records |
| `11-ppac-ip-cookie-binding.png` | PPAC | Environments → [env] → Settings → Privacy + Security → IP cookie binding | IP cookie binding toggle |

## Verification Focus

- IP Firewall enabled and restricting access to approved ranges
- VNet support enabled with proper subnet delegation
- Private Endpoints provisioned and in "Succeeded" state
- Private DNS zones linked to VNet with correct A records
- Key Vault firewall denies public access (for strict isolation)
- Application Insights connected via Private Link Scope
- No public endpoint access for sensitive data sources
- IP cookie binding enabled for session security (Zone 3)
