# Portal Walkthrough: Control 1.20 — Network Isolation and Private Connectivity

**Last Updated:** May 2026
**Portals:** Power Platform Admin Center (PPAC), Azure Portal
**Estimated Time:** 30–45 minutes for IP firewall + cookie binding; 4–8 hours end-to-end for full VNet + Private Endpoint deployment (excluding Azure platform-team change windows)

---

## Audience and Scope

This walkthrough is for **M365 administrators** in US financial services who own Power Platform governance for Microsoft Copilot Studio agents. Azure resource provisioning steps assume coordination with your Azure platform team (Network Contributor on the target subscription/resource group). PPAC steps are owned by the **Power Platform Admin**.

Use this playbook when implementing Control 1.20 for a Zone 2 (recommended) or Zone 3 (mandatory) environment. For Zone 1, only the documentation step at the end applies.

---

## Prerequisites

- [ ] **Managed Environment** enabled on the target environment (Control 2.1). IP firewall, cookie binding, and VNet support are Managed-Environment features.
- [ ] **Power Platform Admin** role for PPAC steps.
- [ ] **Azure Network Contributor** (or equivalent) on the target Azure subscription / resource group for VNet, subnet, private endpoint, and DNS zone steps.
- [ ] **AI Administrator** awareness — the agent inventory in the affected environment should be confirmed before Enforce.
- [ ] Power Platform region of the environment confirmed, and the **Azure region paired** to it identified for both **primary** and **failover** Azure regions (subnets are required in both).
- [ ] CIDRs of the firm's egress IPs (proxy, VPN, ZTNA egress) confirmed with the network team — **not** internal RFC1918 ranges unless those actually egress directly.
- [ ] Change ticket open with reviewers from Security and Compliance assigned.


---

## Step 1 — Configure IP Firewall (PPAC)

1. Open the [Power Platform Admin Center](https://admin.powerplatform.microsoft.com).
2. **Environments** → select the in-scope environment (must be Managed).
3. **Settings** → **Privacy + Security** → **IP firewall**.
4. Toggle **IP firewall** to **On**.
5. **Mode:** select **Audit only** for the initial rollout.
6. **Allowed IP ranges:** add corporate egress CIDRs in IPv4 / IPv6 / CIDR form. Examples:
    - `203.0.113.0/24` (proxy egress)
    - `198.51.100.10/32` (single VPN exit)
7. **Apply IP-based cookie binding for non-interactive flows:** keep enabled per Microsoft guidance.
8. **Save**.

> **Limits:** Up to **200 IP ranges** per environment; the address field accepts up to **4,000 characters**. Aggregate to CIDR where possible.

> **Audit-mode duration:** Run for at least **one full business cycle** (typically 5–10 business days, longer if month-end batch jobs, off-shore handoffs, or quarterly reporting touches the environment). Review **Dataverse Audit** logs and PPAC analytics for `IPFirewallAuditMode` events before switching to Enforce.

After audit review:

9. Return to **Settings → Privacy + Security → IP firewall**.
10. Change **Mode** to **Enforce** and **Save**. Document the cutover time in the change ticket.

---

## Step 2 — Enable IP-Address-Based Cookie Binding (PPAC)

1. Same blade: **Settings → Privacy + Security → IP firewall** (cookie binding is in the same area on current UI; on some tenants it appears under **Privacy + Security → IP cookie binding**).
2. Toggle **IP-address-based cookie binding** to **On**.
3. If your tenant terminates TLS at a **reverse proxy** before traffic reaches Microsoft endpoints:
    - Add proxy egress IPs under **Reverse proxy IP addresses**.
    - Confirm the proxy is configured to forward the original client IP via the standard `X-Forwarded-For` header (Microsoft-supported header).
4. **Save**.

> **User impact.** Users on networks with significant IP churn (consumer carrier-grade NAT, sudden VPN reconnects) may be re-prompted to authenticate. Communicate this expectation to end users and the help desk before enabling in production.

---

## Step 3 — Provision VNet, Delegated Subnets, and Private DNS (Azure Portal)

> Owned by the **Azure platform team**. Run in both the **primary** Azure region paired with your Power Platform region and the **failover** region. Microsoft requires both.

### 3a. Create the VNet

1. Azure Portal → **Virtual networks** → **+ Create**.
2. Subscription / Resource group: per your landing-zone standard (e.g., `rg-pp-network-prod-eastus`).
3. **Region:** the Azure region paired with the Power Platform environment region.
4. Name: `vnet-pp-prod-eastus` (use your naming standard).
5. **IP Addresses:** address space `10.100.0.0/16` (example).
6. Subnets:
    - `snet-pp-delegated` (`10.100.1.0/24`) — for Power Platform delegation (`/24` recommended for production).
    - `snet-private-endpoints` (`10.100.2.0/24`) — for the Key Vault / Storage / SQL private endpoints.
7. **Review + create** → **Create**.

### 3b. Delegate the subnet

1. Open the new VNet → **Subnets** → **snet-pp-delegated**.
2. **Subnet delegation** → select **Microsoft.PowerPlatform/enterprisePolicies**.
3. **Save**.

### 3c. Repeat for the failover region

Create an equivalent VNet (different address space, e.g., `10.101.0.0/16`) and delegated subnet in the **paired failover** Azure region. Both subnets are referenced when you create the enterprise policy.

### 3d. Link Private DNS zones

For each PaaS dependency, create or reuse a **Private DNS zone** and link it to **both VNets**:

| Dependency | Private DNS zone |
|---|---|
| Key Vault | `privatelink.vaultcore.azure.net` |
| Azure SQL | `privatelink.database.windows.net` |
| Storage (blob) | `privatelink.blob.core.windows.net` |
| Azure Monitor (AMPLS) | `privatelink.monitor.azure.com`, `privatelink.oms.opinsights.azure.com`, `privatelink.ods.opinsights.azure.com`, `privatelink.agentsvc.azure-automation.net`, `privatelink.blob.core.windows.net` |

For each zone: **Virtual network links → + Add** → select the primary and failover VNets → enable **Auto-registration: No** (for PaaS Private Link zones).

---

## Step 4 — Create the Power Platform Enterprise (Network) Policy and Link to Environment

> Microsoft currently performs this step via PowerShell rather than the portal. The **PowerShell setup playbook** (companion file) provides the canonical scripted version. The PPAC UI shows the link result on the environment's **History** and **Settings** blades after the link is created.

In PPAC, after the PowerShell link step completes:

1. PPAC → **Security** → **Data and privacy** → **Azure Virtual Network policies**. *(The PPAC Security information architecture is still evolving — verify the exact 'Azure Virtual Network policies' label in your tenant.)*
2. The environment should appear with the linked policy name visible. Confirm the policy name matches the value from your change ticket.
3. To confirm the link succeeded: PPAC → **Manage** → **Environments** → [environment] → **History**. Status should read **Succeeded**.

> If the **Security** pane or **Data and privacy** sub-pane is not visible, confirm the environment is a Managed Environment (prerequisite). Portal labels may vary between release rings — cross-verify against the [MS Learn VNet setup guide](https://learn.microsoft.com/en-us/power-platform/admin/vnet-support-setup-configure) at deploy time.

---

## Step 5 — Create Private Endpoints for Dependencies (Azure Portal)

Repeat for each dependency the agent calls (Key Vault, Storage, Azure SQL, and AMPLS).

### Example: Key Vault Private Endpoint

1. Azure Portal → open the **Key Vault**.
2. **Networking** → **Private endpoint connections** → **+ Create**.
3. Name: `pe-kv-pp-eastus`.
4. **Region:** match the Key Vault region.
5. **Resource:** target sub-resource = `vault`.
6. **Virtual network:** the Power Platform VNet; **Subnet:** `snet-private-endpoints`.
7. **Private DNS integration:** **Yes** → select the existing `privatelink.vaultcore.azure.net` zone.
8. **Review + create** → **Create**.

After creation:

9. Key Vault → **Networking** → **Public access** → **Disable public access**, or restrict to "Allow trusted Microsoft services" only if the firm's standard requires it.
10. Confirm the **firewall** tab shows **Allow public network access from specific virtual networks and IP addresses: Disabled** (or the equivalent in the latest UI).

Repeat the pattern for **Storage**, **Azure SQL** (sub-resource `sqlServer`), and the **AMPLS** for Application Insights / Log Analytics. For AMPLS:

- Create the **Azure Monitor Private Link Scope** resource.
- Add the in-scope **Application Insights** components and **Log Analytics workspaces**.
- Create a private endpoint targeting the AMPLS scope (sub-resource `azuremonitor`).
- Set the AMPLS **Access modes** for ingestion and queries to **Private Only** for Zone 3 (use **Open** during initial migration to avoid telemetry gaps, then tighten).

---

## Step 6 — Reconcile with Conditional Access (Control 1.11)

1. Open the [Microsoft Entra admin center](https://entra.microsoft.com) → **Protection → Conditional Access → Named locations**.
2. Confirm the same egress CIDRs used in Step 1 are represented as **Trusted IPs** named locations.
3. If a Conditional Access policy gates Power Platform access by named location, ensure its IP set **matches or is a subset** of the IP firewall allowlist. Mismatches cause confusing user-facing errors that look like sign-in failures but are network rejections (or vice versa).

---

## Step 7 — Document and Attest

1. Update the environment's network architecture diagram (the firm's diagramming standard; Visio / draw.io / Mermaid). Include: agents in scope, environment, delegated subnet, VNet peering or links, private endpoints, dependency resources, AMPLS, and the egress proxy.
2. Attach the diagram to the change record and the supervisory file.
3. Capture screenshots of the IP firewall (Enforce mode), cookie binding toggle, subnet delegation, and at least one private endpoint in **Approved** state, plus an `nslookup` from a VM in the VNet showing the dependency FQDN resolving to a `10.x.x.x` address.
4. Record reviewer sign-offs from **Security** and **Compliance** in the change ticket.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---|---|---|---|
| Managed Environment | Optional | Required | Required |
| IP firewall | Off (documented) | Enforce | Enforce |
| Cookie binding | Off | On | On (with reverse-proxy headers if applicable) |
| VNet integration | Not required | Recommended when calling Azure dependencies | Mandatory (primary + failover) |
| Private Endpoints | Not required | Required for dependencies holding NPI | Required for Key Vault, Storage, SQL, AMPLS |
| Public network access on dependencies | Default | Disable for NPI-bearing resources | Disabled |
| NSG flow logs / Traffic Analytics | Not required | Recommended | Required |
| Re-attestation cadence | Annual | Semi-annual | Quarterly |

---

## Validation

After completing the steps above, the [Verification & Testing](verification-testing.md) playbook walks through the test cases. At minimum, before closing the change ticket:

- [ ] IP firewall is in **Enforce** mode and a test from a non-allowlisted IP returns 403.
- [ ] Cookie binding is on and a controlled cookie-replay test (non-production) is rejected.
- [ ] `Get-PowerAppEnvironmentEnterprisePolicy` returns the linked policy with the expected primary and failover subnet IDs.
- [ ] `nslookup` from a VM in `snet-private-endpoints` resolves Key Vault, SQL, and AMPLS FQDNs to `10.x.x.x`.
- [ ] Public network access is **Disabled** on all in-scope dependencies.
- [ ] Architecture diagram and screenshots attached to the change ticket.

---

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
