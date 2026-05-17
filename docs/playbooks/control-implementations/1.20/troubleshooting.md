# Troubleshooting: Control 1.20 — Network Isolation and Private Connectivity

**Last Updated:** April 2026
**Audience:** M365 administrators, Power Platform admins, and Azure platform engineers responding to network-isolation incidents in US financial services tenants.

This playbook is the failure-mode catalog for Control 1.20. Pair it with the [Portal Walkthrough](portal-walkthrough.md), [PowerShell Setup](powershell-setup.md), and [Verification & Testing](verification-testing.md) playbooks.

---

## Quick Reference

| Symptom | Most likely cause | First-step fix |
|---|---|---|
| Users on the corporate network suddenly can't sign in to the environment | IP firewall switched to Enforce while a corporate egress IP changed | Re-add the new egress CIDR; revert to Audit if widespread |
| Users on VPN see intermittent re-prompts | Cookie binding rejecting cookies after VPN reconnect/IP change | Confirm reverse-proxy header config; expected behavior on IP change |
| Agent fails to call Key Vault from a Managed Environment | Enterprise policy not linked OR public access disabled with no PE in place | Verify `Get-PowerAppEnvironmentEnterprisePolicy` and PE state |
| `nslookup` returns a public IP for a dependency from inside the VNet | Private DNS zone not linked to the VNet, or PE missing zone group | Add VNet link; create DNS zone group on the PE |
| Power Automate flow times out reaching Azure SQL via private endpoint | NSG denying intra-VNet traffic or SQL public access still on with mismatched firewall | Inspect NSG flow logs; reconcile SQL networking blade |
| Application Insights ingestion drops after switching AMPLS to `PrivateOnly` | Agent hosts (App Service, hybrid worker) lack PE path | Revert to `Open`, fix host networking, re-tighten |
| `New-AdminPowerAppEnvironmentEnterprisePolicy` errors with parameter not found | Module version drift | Re-pin module; re-check current cmdlet help |

---

## Detailed Troubleshooting

### Issue 1 — IP firewall blocking legitimate corporate traffic

**Symptoms.** A wave of users from the corporate network suddenly receive 403 errors when opening model-driven apps or the Maker Portal scoped to the in-scope environment. Dataverse audit shows `IPFirewallBlockedRequest` events with a source IP not in the allowlist.

**Likely causes.**

1. The firm's egress NAT pool changed (cloud proxy provider rotation, ZTNA migration, ISP change) and the new IPs are not in the allowlist.
2. The firewall was switched from **Audit** to **Enforce** while a temporary egress path (test proxy, secondary office circuit) was in use during audit-mode capture, so its CIDR was never added.
3. A user on a guest Wi-Fi or split-tunnel VPN is reaching the service from an unexpected egress, not from the corporate proxy.

**Resolution.**

1. Confirm the actual source IPs from `IPFirewallBlockedRequest` in Dataverse audit.
2. Reconcile against the network team's egress IP authoritative source.
3. If the gap is genuine, add the missing CIDRs in PPAC → Privacy + Security → IP firewall and **Save**.
4. If the cause is unclear or the impact is broad, **revert to Audit mode** until the egress map is corrected, then re-Enforce after a clean audit window.
5. Reconcile with [Conditional Access named locations](../1.11/portal-walkthrough.md) so allowlists are aligned across both controls.

> **Do not** broadly widen the allowlist (e.g., `0.0.0.0/0`) as a workaround. That defeats the control and creates an audit finding.

---

### Issue 2 — Cookie binding causing user re-prompts

**Symptoms.** Users on flaky or roaming networks (cellular, hotel Wi-Fi, VPN reconnects) are re-prompted to sign in more often than expected.

**Likely cause.** This is **expected behavior**: cookie binding rejects a session cookie when the source IP changes. The platform asks for a fresh sign-in.

**Resolution.**

1. Confirm reverse-proxy header configuration is correct in PPAC (so users behind the proxy show the *original* client IP, not the proxy IP, as the binding key).
2. For genuinely impacted user populations (mobile-heavy field roles), discuss compensating controls with Security: continued cookie binding plus an SSO session that bridges quickly is usually preferable to disabling binding.
3. Disable cookie binding **only** with documented Compliance approval and a compensating control noted in the change record.

---

### Issue 3 — Agent cannot call Key Vault / SQL / Storage after enabling private endpoints

**Symptoms.** Agent flows fail with timeouts or `Forbidden` after the Azure team disables public network access on a dependency.

**Likely causes.**

1. Enterprise policy was not actually linked to the environment (or the link silently failed).
2. The PE is in `Pending` state (manual approval was required for cross-tenant or cross-subscription scenarios).
3. NSG on the PE subnet denies inbound from the delegated subnet.
4. Private DNS zone is not linked to the VNet, so the agent resolves the public FQDN and is rejected at the firewall.

**Resolution.**

1. Run (Windows PowerShell 5.1):
    ```powershell
    Get-PowerAppEnvironmentEnterprisePolicy -EnvironmentName <env-id>
    ```
    Confirm the policy is present and lists both primary and failover subnet IDs.
2. In Azure Portal → the dependency → **Networking** → **Private endpoint connections**: confirm state is **Approved**, not **Pending**.
3. Inspect NSG flow logs for denies between the delegated subnet and PE subnet. Expected NSG rule: allow `VirtualNetwork` → `VirtualNetwork` on the relevant ports (443 for most PaaS, 1433 for Azure SQL).
4. From the in-VNet utility VM:
    ```powershell
    Resolve-DnsName <dependency-fqdn>
    ```
    Confirm the response is a private IP. If not, add the VNet link to the relevant `privatelink.*.azure.net` Private DNS zone and create the zone-group on the PE.

---

### Issue 4 — Application Insights / Log Analytics ingestion stops after switching AMPLS to `PrivateOnly`

**Symptoms.** Telemetry from agent hosts, Power Automate flows, or supporting Azure Functions stops appearing in Application Insights / Log Analytics shortly after the AMPLS access mode is set to `PrivateOnly`.

**Likely cause.** Some telemetry sources do not have a network path to the AMPLS private endpoint (e.g., a hybrid worker on an on-prem network without ExpressRoute / VPN to the VNet, or an App Service plan not VNet-integrated).

**Resolution.**

1. Revert AMPLS to `Open` ingestion mode immediately to restore telemetry.
2. Use the Microsoft Learn guidance on [AMPLS planning](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/private-link-security) to enumerate every source.
3. Add VNet integration / ExpressRoute connectivity for missing sources, or move the workspace out of AMPLS scope if the source cannot reach the PE and is genuinely intended for public ingestion.
4. Re-tighten to `PrivateOnly` only after every source is confirmed.

---

### Issue 5 — `New-AdminPowerAppEnvironmentEnterprisePolicy` errors with "parameter cannot be found"

**Symptoms.** Scripts that previously worked now fail with errors such as `A parameter cannot be found that matches parameter name 'PrimaryVirtualNetworkSubnetId'`.

**Likely cause.** Module drift. `Microsoft.PowerApps.Administration.PowerShell` cmdlets in the enterprise-policy / network area have changed parameter names and aliases between minor versions.

**Resolution.**

1. `Get-Module Microsoft.PowerApps.Administration.PowerShell -ListAvailable` — note the version installed.
2. `Get-Help New-AdminPowerAppEnvironmentEnterprisePolicy -Full` — reconcile the current parameter set against your script.
3. Cross-check against the current [Microsoft Learn page for VNet setup](https://learn.microsoft.com/en-us/power-platform/admin/vnet-support-setup-configure).
4. Re-pin the working version per the [PowerShell baseline](../../_shared/powershell-baseline.md) §1 and update CAB documentation.
5. Avoid `-Force` upgrades on `Microsoft.PowerApps.Administration.PowerShell` in regulated tenants without re-validating scripts in a non-production environment first.

---

### Issue 6 — Cmdlet returns empty results in a sovereign-cloud tenant

**Symptoms.** `Get-AdminPowerAppEnvironment` returns no environments, or the validation script shows `EnterprisePolicyLinked: False` for an environment that is clearly linked in the GCC / GCC High / DoD portal.

**Likely cause.** `Add-PowerAppsAccount` was called without `-Endpoint`, so the cmdlet authenticated against commercial endpoints and silently returned an empty result set ("false-clean").

**Resolution.**

1. Stop. **Do not** trust the empty result.
2. Re-authenticate using the sovereign-cloud helper from the [PowerShell Setup playbook](powershell-setup.md):
    ```powershell
    Connect-FsiClouds -Cloud GCCHigh -TenantId <tenant>
    ```
3. Re-run the validation. Confirm against the matching sovereign PPAC URL.
4. Add a guard to your scripts that asserts a non-empty environment list and throws if zero results are returned in production.

See the [PowerShell baseline](../../_shared/powershell-baseline.md) §3 for the canonical sovereign-aware authentication pattern.

---

### Issue 7 — Subnet too small / cannot expand later

**Symptoms.** New environments cannot be added to the enterprise policy; Microsoft documentation indicates IP exhaustion in the delegated subnet.

**Likely cause.** Subnet was sized as `/27` or `/28` for "test"; production traffic outgrew the available IP pool.

**Resolution.**

1. The delegated subnet **cannot be resized in place** once Power Platform has injected resources.
2. Plan a migration: provision a new larger subnet (Microsoft recommends `/24` for production), create a new enterprise policy referencing the new subnet, and re-link the environment during a change window.
3. Update CAB and supervisory records with the new subnet IDs.

---

## Escalation Path

1. **Power Platform Admin** — IP firewall, cookie binding, enterprise policy link.
2. **Azure platform team (Network Contributor)** — VNet, subnet delegation, private endpoints, Private DNS, NSG, AMPLS.
3. **Entra Security Admin** — reconciliation with Conditional Access named locations and broader identity boundary.
4. **Compliance Officer** — sign-off on any deviation from the documented Zone 2 / Zone 3 requirements.
5. **Microsoft Support** — open a Power Platform admin support case (specify *Network Isolation / Subnet Delegation*) for platform-side issues; open an Azure support case for Private Link / DNS issues.

---

## Known Limitations (April 2026)

| Limitation | Impact | Workaround / Note |
|---|---|---|
| VNet support requires Managed Environments | Standard environments cannot use subnet delegation | Upgrade to Managed Environment (Control 2.1) |
| Failover subnet is mandatory for the enterprise policy | Higher Azure consumption (two subnets, two regions) | Plan IP space and budget for both regions during landing-zone design |
| Delegated subnet cannot be resized in place | Sizing mistakes are expensive to fix | Use `/24` for production from day one |
| Some legacy connectors do not honor VNet integration | Specific connector calls may continue to traverse the public path | Audit connectors used per environment; replace or wrap legacy connectors where the residual risk is unacceptable |
| Not all Azure regions are supported for Power Platform VNet integration | Region selection constraints | Verify on the [Microsoft Learn region list](https://learn.microsoft.com/en-us/power-platform/admin/vnet-support-overview) |
| AMPLS access mode applies workspace-wide | Tightening to `PrivateOnly` affects every source, not just agent telemetry | Stage rollout and re-verify ingestion after every change |
| IP firewall limit | Up to 200 ranges and 4,000 characters per environment | Aggregate to CIDR; consolidate egress proxies |

---

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
