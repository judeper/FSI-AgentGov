# Troubleshooting: Control 1.15 — Encryption: Data in Transit and at Rest

**Last Updated:** April 2026

---

## Quick Issue Index

| Issue | Section |
|---|---|
| Customer Key DEP stuck in `PendingActivation` | [Customer Key activation failures](#customer-key-activation-failures) |
| `Register-SPODataEncryptionPolicy` returns access-denied | [SPO Customer Key registration errors](#spo-customer-key-registration-errors) |
| TLS handshake errors on hybrid / custom endpoint | [TLS handshake failures](#tls-handshake-failures) |
| DKE-labelled file fails to open for an authorized user | [DKE service unreachable or misconfigured](#dke-service-unreachable-or-misconfigured) |
| PPAC CMK option missing on environment | [Power Platform CMK not available](#power-platform-cmk-not-available) |
| Need to revoke Customer Key safely | [Customer Key revocation and data-purge safety](#customer-key-revocation-and-data-purge-safety) |
| Key Vault deletes / disables not alerting | [Key Vault diagnostic + alerting gaps](#key-vault-diagnostic-alerting-gaps) |

---

## Customer Key Activation Failures

### Symptom: DEP stays in `PendingActivation`

Microsoft initiates an asynchronous wrap operation when a DEP is created/assigned. If the wrap fails, the policy lingers in `PendingActivation`.

#### Likely cause 1 — Missing key permissions on the workload service principal

The DEP uses one of two Microsoft service principals:

- Exchange Online DEP → **Office 365 Exchange Online**
- SharePoint / OneDrive DEP → **Office 365 SharePoint Online**

Required permissions on **each** key (primary + secondary): `Get`, `WrapKey`, `UnwrapKey`. Anything broader is over-privileged; anything narrower fails wrap.

**Fix:** Re-grant via vault access policy or RBAC role `Key Vault Crypto Service Encryption User` scoped at the **key** (not the vault).

#### Likely cause 2 — Key Vault firewall blocking trusted Microsoft services

If the vault has the firewall enabled, "Allow trusted Microsoft services to bypass this firewall" must be checked, **and** the M365 workload SP must still be listed in access policy / RBAC.

#### Likely cause 3 — Key not enabled, or expiry / activation date set

Customer Key requires the key to be enabled with no activation/expiration window set.

**Fix:** `Update-AzKeyVaultKey -Enable $true` and verify `NotBefore` / `Expires` are unset.

#### Likely cause 4 — Soft-delete retention < 90 days, or purge protection disabled

Customer Key requires soft-delete retention ≥ 90 days **and** purge protection enabled.

**Fix:** Soft-delete retention can only be **increased**, not reduced. Purge protection can be enabled at any time and is irreversible. Enable both before re-activating.

#### Likely cause 5 — Wrong tenant

The Azure subscription hosting the Key Vault must be in the **same Microsoft Entra tenant** as the Microsoft 365 tenant. Cross-tenant Customer Key is not supported.

---

## SPO Customer Key Registration Errors

### Symptom: `Register-SPODataEncryptionPolicy` returns 403 / access-denied

#### Likely cause — Run from PowerShell 7

`Microsoft.Online.SharePoint.PowerShell` is **Windows PowerShell 5.1 only**. Running the cmdlet from PowerShell 7 produces inconsistent failures (silent missing cmdlets, partial connections, or 403). The PowerShell setup script includes a `$PSVersionTable.PSEdition` guard for this reason.

### Symptom: "Already registered" or "operation in progress"

SPO Customer Key registration is **tenant-wide and one-shot**. The cmdlet cannot be re-run while activation is pending. Wait for `Get-SPODataEncryptionPolicy` to settle before any further action; treat ongoing changes as rotation, not registration.

---

## TLS Handshake Failures

### Symptom: SSL Labs reports legacy TLS or weak ciphers

Microsoft 365 service endpoints have not accepted TLS 1.0/1.1 since the Microsoft-wide deprecation (2020 for general availability, fully enforced thereafter). If SSL Labs reports legacy TLS:

#### Likely cause 1 — On-premises hybrid component (Exchange hybrid, AD FS, hybrid SharePoint)

The legacy protocol is being negotiated by **your** hybrid endpoint, not by Microsoft 365. Disable TLS 1.0 / 1.1 on the hybrid server (registry: `HKLM\System\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server\Enabled = 0`) and rotate the listener. Test SChannel, .NET, and any per-app TLS settings.

#### Likely cause 2 — Custom domain pointing to a third-party reverse proxy

A WAF or reverse proxy in front of your custom domain is doing the TLS termination. Audit and harden the proxy.

#### Likely cause 3 — Direct-line / connector endpoint for a Copilot Studio agent

Custom HTTP connectors and direct-line endpoints can run on customer-supplied infrastructure. Audit each connector's TLS settings.

### Symptom: `Connect-ExchangeOnline` fails with `Could not create SSL/TLS secure channel`

The client (Windows PowerShell 5.1 in particular) is defaulting to a TLS version Microsoft no longer accepts.

**Fix:** `[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13`. For permanent fix, set `SchUseStrongCrypto` registry values on .NET Framework.

---

## DKE Service Unreachable or Misconfigured

### Symptom: Authorized user gets "Access required from the customer key service" on a DKE-labelled file

#### Likely cause 1 — DKE service endpoint not reachable from the client

The DKE key service URL must be reachable over HTTPS from the Office client at the moment of open. Validate from the client: `Invoke-WebRequest https://dke.fsi-corp.example/<keyname>` (placeholder — replace with your tenant) should return a JSON metadata response.

**Fix:** Restore network connectivity. Loss of the DKE service makes **all** DKE-labelled content unreadable globally — DR posture for the service is critical.

#### Likely cause 2 — Certificate not publicly trusted

DKE clients require a publicly trusted TLS certificate on the key service endpoint. Self-signed and private-CA certificates fail.

#### Likely cause 3 — Microsoft Entra app-registration consent missing for the user

The DKE key service authenticates callers via an Entra app registration. The user (or their group) must be assigned to that app registration **and** consent must be granted.

#### Likely cause 4 — Key service returning the wrong key for the named key endpoint

Each DKE label binds to a specific key endpoint (e.g., `/Confidential-MNPI`). If the service is not configured for that endpoint, callers get a generic 404 → Office presents it as access-required.

### Symptom: DKE-protected file appears to open with no challenge

**This is a control failure.** Either the file is not actually DKE-encrypted (label misapplied / encryption setting wrong), or the client has cached credentials that mask the test. Re-validate with TC-1.15-04 from a clean session and a control account that has never authorized to the DKE service.

---

## Power Platform CMK Not Available

### Symptom: "Manage encryption key" option missing in PPAC for an environment

#### Likely cause 1 — Environment is not a Managed Environment

CMK requires the environment to be enabled as a Managed Environment first.

#### Likely cause 2 — Environment is Default or a personal environment

Default and personal Dataverse environments do not support CMK.

#### Likely cause 3 — License does not cover CMK

CMK requires Power Apps / Power Automate Premium licensing in the environment, plus the appropriate Managed Environment licensing.

#### Likely cause 4 — Key Vault and environment in different Azure regions

CMK requires the Key Vault to be in the **same Azure region** as the Dataverse environment. Cross-region is not supported.

### Symptom: CMK enable kicks off but Dataverse re-encryption fails

#### Likely cause — Key Vault permission scope wrong

Dataverse needs `Get/WrapKey/UnwrapKey` on the **specific key** (not the vault). Re-grant at the key scope and retry.

---

## Customer Key Revocation and Data-Purge Safety

!!! danger "Revocation is irreversible — by design"
    Microsoft Customer Key supports **revocation** so that you can perform a cryptographic erase of your tenant's customer-encrypted data (e.g., GDPR Article 17, regulator-mandated tenant exit, end-of-engagement deletion). Once revoked, the data-purge path runs to completion and the affected data **cannot be recovered by anyone** — not by your administrators, not by Microsoft Support, not by a forensics vendor.

### Before you revoke

- [ ] Written CISO + Records Officer + Legal sign-off (in your change-management system)
- [ ] Confirmed there is no business-continuity expectation for the affected data
- [ ] Confirmed any preservation / litigation hold has been satisfied via separate export
- [ ] Microsoft Support case open (Microsoft gates the destructive sequence)
- [ ] Communications plan executed for affected user populations
- [ ] Rehearsal completed in a non-production tenant within the last 12 months

### What to do **instead** for non-destructive scenarios

| You actually want… | Do this — not revocation |
|---|---|
| Rotate to a new key version | New version of the same key — see [PowerShell § 5](powershell-setup.md#5-key-rotation-routine-non-destructive) |
| Move from Standard to Premium HSM | Add new HSM key to existing DEP, then rotate; do not revoke |
| Investigate a suspected key compromise | Disable the suspect key version (reversible within soft-delete window) and rotate; engage Microsoft Support before any delete |
| Retire an unused environment | Delete the workload (mailbox, site) — not the DEP key |

### Recovery window

- Soft-deleted keys can be recovered for the configured retention period (≥ 90 days for Customer Key vaults).
- Once purge protection has held the soft-delete window and the revocation operation has progressed past Microsoft's purge gate, **recovery is not possible**.

---

## Key Vault Diagnostic + Alerting Gaps

### Symptom: A `KeyDelete` or `KeyDisable` event fires but no alert reaches the SOC

#### Likely cause 1 — Diagnostic setting not configured

Each Key Vault must have a Diagnostic Setting routing the `AuditEvent` category to a Log Analytics workspace, Event Hub, or Storage Account. Default = no logging.

**Fix:** Azure portal → Key Vault → **Diagnostic settings** → add a setting that ships `AuditEvent` (and optionally `AllMetrics`) to your Sentinel workspace.

#### Likely cause 2 — Sentinel analytic rule missing

Even with logs flowing, there is no out-of-box alert. Author a custom analytic rule, e.g.:

```kusto
AzureDiagnostics
| where ResourceType == "VAULTS"
| where OperationName in ("KeyDelete", "KeyDisable", "VaultDelete", "VaultPurge")
| project TimeGenerated, ResourceId, OperationName, identity_claim_upn_s, CallerIPAddress, ResultType
```

Bind to an Incident with severity High and notify the Encryption Custodian + SOC distribution.

---

## Known Limitations

| Limitation | Impact | Workaround |
|---|---|---|
| Customer Key requires E5 / Customer Key add-on | Lower-tier tenants cannot configure Customer Key | Stay on Microsoft-managed keys (Zone 1 baseline) until license uplift |
| Customer Key DEP activation is asynchronous (minutes to ~24h) | Cannot be batched into short change windows | Plan activation in a separate change ticket from the dependent workload changes |
| SPO Customer Key registration is tenant-wide, not per-site | All sites encrypted with same DEP | Create separate tenants for jurisdictionally separate data — Customer Key cannot partition within a tenant |
| DKE service availability is fully on the customer | Loss of the DKE service = global loss of DKE-protected file access | Deploy HA pair; geo-redundant; backup key material into HSM |
| CMK requires same-region Key Vault | No cross-region key escrow | Maintain key backup process to satisfy DR requirements |
| HSM-backed keys require Premium vault | Higher Azure cost | Premium for Zone 2/3 only; Standard for Zone 1 audit needs |
| Customer Key revocation is irreversible | Data destruction risk if mis-used | Restrict, document, rehearse — see revocation safety section |
| `Register-SPODataEncryptionPolicy` is one-shot per tenant | Cannot iterate cleanly | Test in a non-production tenant first |

---

## Escalation Path

1. **Encryption Custodian** (Entra Security Admin) — Customer Key activation, Key Vault hardening
2. **Purview Info Protection Admin** — DEP and DKE label issues
3. **Power Platform Admin** — PPAC CMK
4. **CISO + Records Officer** — Any consideration of revocation
5. **Microsoft Support** — Required for revocation execution and any platform-level Customer Key incident; open a Sev A ticket with the DEP name and Key Vault key URIs

---

[Back to Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
