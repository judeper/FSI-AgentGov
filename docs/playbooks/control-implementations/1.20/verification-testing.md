# Verification & Testing: Control 1.20 — Network Isolation and Private Connectivity

**Last Updated:** April 2026
**Audience:** M365 administrators, security engineers, internal audit, and compliance reviewers in US financial services.

This playbook defines the test cases, evidence artifacts, and attestation template used to demonstrate that Control 1.20 is operating as designed for a given Power Platform environment. Use it after the [Portal Walkthrough](portal-walkthrough.md) and [PowerShell Setup](powershell-setup.md) playbooks have been executed.

---

## Test Environment Hygiene

- Run **destructive or "block expected" tests** in a non-production environment that mirrors the in-scope environment's network configuration. Do not run cookie-replay or deny tests against a production environment hosting customer data.
- Tests assume access to:
    - A workstation **inside** the corporate egress (allowlisted IP).
    - A workstation **outside** that allowlist (e.g., a tethered mobile network or an isolated cloud VM with a public egress).
    - A small **utility VM** inside the Power Platform VNet (in `snet-private-endpoints` or a separate jump subnet) for DNS and HTTP probes.
- Capture the **timestamp (UTC)**, **operator**, and **expected vs. actual result** for each test. Save artifacts to the change ticket and the supervisory file.

---

## Test Cases

| Test ID | Scenario | Expected Result | Evidence |
|---|---|---|---|
| TC-1.20-01 | From a non-allowlisted IP, attempt sign-in to the make.powerapps.com / model-driven app of the in-scope environment. | HTTP 403 with `IPFirewallBlockedRequest` (or equivalent platform error). User cannot reach Dataverse data. | Browser screenshot + Dataverse audit entry |
| TC-1.20-02 | From an allowlisted corporate IP, sign in and load a record. | Success. Audit entry shows allowed IP. | Screenshot + audit entry |
| TC-1.20-03 | Cookie replay (controlled, non-production): capture an authenticated cookie from one client IP, replay from a second client IP. | Replayed request rejected. User from second IP is forced to re-authenticate. | Network capture summary + auth log |
| TC-1.20-04 | From the utility VM **inside** the VNet, run `Resolve-DnsName myvault.vault.azure.net`. | Returns a private IP (e.g., `10.100.2.5`). | `Resolve-DnsName` output |
| TC-1.20-05 | From a workstation **outside** the VNet, run `Resolve-DnsName myvault.vault.azure.net`. | Returns a public IP. | `Resolve-DnsName` output (negative test) |
| TC-1.20-06 | From the utility VM, attempt `Get-AzKeyVaultSecret` against the in-scope Key Vault. | Success. Key Vault diagnostic logs show the request `callerIpAddress` matching the private endpoint NIC IP. | Key Vault diagnostic log row |
| TC-1.20-07 | From outside the VNet (no allowlist), attempt `Get-AzKeyVaultSecret`. | Failure: `Public network access is disabled` (or 403 forbidden by network rules). | PowerShell error transcript |
| TC-1.20-08 | Run a Microsoft Copilot Studio agent test conversation that triggers a Power Automate flow calling Azure SQL via the private endpoint. | Conversation returns expected data. SQL audit shows the connection from the delegated subnet IP range. | Agent transcript + SQL audit row |
| TC-1.20-09 | Inspect Application Insights ingestion: send a custom event from the agent's host. | Event appears in App Insights within standard ingestion latency. AMPLS access mode = `PrivateOnly` and ingestion succeeds via private endpoint. | App Insights query result + AMPLS config |
| TC-1.20-10 | `Get-PowerAppEnvironmentEnterprisePolicy -EnvironmentName <env>` (Windows PowerShell 5.1). | Returns the linked policy with primary + failover subnet IDs matching the change ticket. | PowerShell output |
| TC-1.20-11 | `Get-AzVirtualNetworkSubnetConfig` against the delegated subnet. | `Delegations[0].ServiceName = 'Microsoft.PowerPlatform/enterprisePolicies'`. | PowerShell output |
| TC-1.20-12 | NSG flow logs / Traffic Analytics show egress traffic from the delegated subnet to the private endpoint subnet, and **no** outbound traffic from the delegated subnet to public IPs of in-scope dependencies. | Confirmed via Traffic Analytics view. | Screenshot of flow path |

---

## Evidence Collection Checklist

Capture the following artifacts and attach them to the change record and the next quarterly attestation:

- [ ] PPAC screenshot: **IP firewall = Enforce**, with allowlisted CIDRs visible (redact non-public CIDRs per firm standard).
- [ ] PPAC screenshot: **IP-address-based cookie binding = On**.
- [ ] Azure Portal screenshot: subnet detail showing **Subnet delegation = Microsoft.PowerPlatform/enterprisePolicies** for both regions.
- [ ] Azure Portal screenshot: at least one Private Endpoint in **Approved** state per dependency type (Key Vault, SQL, Storage, AMPLS).
- [ ] `Resolve-DnsName` output from the in-VNet utility VM showing private IPs for each in-scope dependency FQDN.
- [ ] Output of `Script 6 — Validation` from the [PowerShell Setup](powershell-setup.md) playbook (JSON + `.sha256`).
- [ ] Test transcripts for TC-1.20-01, TC-1.20-03, and TC-1.20-07 (the "block expected" tests).
- [ ] Updated network architecture diagram, dated and signed by the **Compliance Officer** and **Entra Security Admin**.

---

## Self-Service Validation Script

The [PowerShell Setup playbook](powershell-setup.md) `Script 6 — Validation` produces a machine-readable evidence record. A green run requires:

```text
IsManagedEnvironment      : True
EnterprisePolicyLinked    : True
PrimarySubnetMatches      : True
FailoverSubnetMatches     : True
DelegationOn_<subnet>     : True (for both primary and failover)
PublicAccessDisabled_<r>  : True (for every in-scope dependency)
```

Any `False` in the above is a finding that should be opened in your governance tracker before signing the attestation.

---

## Failure Modes and What They Indicate

| Observation | Likely cause | Next step |
|---|---|---|
| TC-1.20-04 returns a public IP from inside the VNet | Private DNS zone not linked to the VNet, or zone-group not created on the PE | Re-run private DNS zone linking; verify `Get-AzPrivateDnsZoneGroup` |
| TC-1.20-06 fails with timeout but DNS resolves to private IP | NSG denies outbound from delegated subnet to PE subnet | Inspect NSG rules; allow `VirtualNetwork → VirtualNetwork` per Microsoft requirement |
| TC-1.20-08 fails with `Login failed for user 'NT AUTHORITY\ANONYMOUS LOGON'` from a flow | Managed identity not granted on the SQL server, or Azure SQL public access still enabled and IP firewall mismatched | Reconcile managed identity grants and confirm SQL public access is `Disabled` |
| TC-1.20-09 ingestion delayed > 30 minutes after enabling `PrivateOnly` | Some agent hosts do not have a network path to the AMPLS PE | Re-open AMPLS in `Open` mode, fix host networking, then re-tighten |
| TC-1.20-10 returns no policy | Enterprise policy creation succeeded but the link step failed silently | Re-run `New-AdminPowerAppEnvironmentEnterprisePolicy` link step in Windows PowerShell 5.1 |

See [Troubleshooting](troubleshooting.md) for the full failure-mode catalog.

---

## Attestation Statement Template

```markdown
## Control 1.20 Attestation — Network Isolation and Private Connectivity

**Organization:** [Legal entity]
**Environment ID:** [Power Platform GUID]
**Environment Name:** [Display name]
**Zone:** [1 / 2 / 3]
**Quarter:** [QYYYY]
**Control Owner:** [Name, role]
**Reviewers:** [Entra Security Admin name], [Compliance Officer name]

I attest that, as of the date below, the following are in effect for this environment:

1. The environment is a Managed Environment.
2. IP firewall is configured in **Enforce** mode with the allowlisted ranges listed in Appendix A.
3. IP-address-based cookie binding is **On**, with reverse-proxy headers configured as documented in Appendix B (if applicable).
4. The environment is linked to enterprise (network) policy `<policy GUID>` with delegated subnets in `<primary region>` and `<failover region>`.
5. Public network access is **Disabled** on the Key Vault(s), Azure SQL server(s), Storage account(s), and AMPLS-scoped Application Insights / Log Analytics workspace(s) listed in Appendix C.
6. Test cases TC-1.20-01 through TC-1.20-12 from the Verification & Testing playbook were executed on `<date>` with results recorded in the change ticket.
7. The current network architecture diagram (Appendix D) accurately reflects the deployed configuration.

**Signed:** _____________________________   **Date (UTC):** _________________
```

---

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
