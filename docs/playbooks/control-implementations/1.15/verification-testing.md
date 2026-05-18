# Verification & Testing: Control 1.15 — Encryption: Data in Transit and at Rest

**Last Updated:** April 2026

This playbook produces auditor-ready evidence for GLBA 501(b), SEC Reg S-P 17 CFR 248.30, NY DFS 23 NYCRR 500.15, FFIEC IT Examination Handbook, and SOX 404 testing.

---

## Verification Checklist

Run through this list once per quarter for Zone 2 / Zone 3, once per annual review for Zone 1.

1. [ ] **TLS posture** — SSL Labs Grade A/A+ on every public tenant endpoint; TLS 1.0 / 1.1 = No; no weak ciphers (RC4, 3DES, EXPORT)
2. [ ] **Service-encryption baseline** — Purview Customer Key page confirms Microsoft service encryption active for EO, SPO, OneDrive, Teams
3. [ ] **Customer Key — Exchange Online** — `Get-M365DataAtRestEncryptionPolicy` returns `PolicyState=Active`; both Primary and Secondary key URIs resolve
4. [ ] **Customer Key — SPO/OneDrive** — `Get-SPODataEncryptionPolicy` returns `State=Registered` (or equivalent active state); both vault references valid
5. [ ] **Vault hardening** — every Customer Key vault has soft delete + purge protection enabled, retention ≥ 90 days
6. [ ] **Key Vault access scope** — only the `Office 365 Exchange Online` / `Office 365 SharePoint Online` service principal has key permissions, scoped to `Get/WrapKey/UnwrapKey` only
7. [ ] **Key Vault diagnostic logs** — flowing to Sentinel/SIEM; events present in last 7 days; alert rules exist for `KeyDelete`, `KeyDisable`, `VaultDelete`
8. [ ] **DKE label (Zone 3)** — sensitivity label with encryption type "Double Key Encryption" exists, points at customer DKE service URL, published to MNPI scope
9. [ ] **DKE end-to-end (Zone 3)** — labelled test document is unreadable from a control account that has no DKE-service access (proof of cryptographic isolation)
10. [ ] **Power Platform CMK** — PPAC environment shows "Encryption key managed by customer" with linked Key Vault key URI on every Managed Environment hosting a Microsoft Copilot Studio agent
11. [ ] **Copilot grounding inventory** — every Copilot grounding source mapped to its DEP coverage; inventory dated within last quarter
12. [ ] **Key rotation evidence** — most recent rotation falls within the cadence required for the zone (Zone 2 annual / Zone 3 quarterly); rotation ticket records dual-control approval and the new key version URI
13. [ ] **Revocation runbook (Zone 3)** — runbook exists, names approval chain, and includes a dated rehearsal report from a non-prod tenant within the last 12 months
14. [ ] **Certificate inventory** — every customer-controlled certificate (custom domains, hybrid, DKE service) has expiry date tracked; alerts fire ≥ 60 days before expiry

---

## Test Scenarios

### TC-1.15-01 — TLS posture

| Field | Value |
|---|---|
| Pre-condition | Tenant operational; admin workstation with internet access |
| Action | Run [SSL Labs](https://www.ssllabs.com/ssltest/) against `<tenant>.sharepoint.com`, `<tenant>-my.sharepoint.com`, custom domains |
| Expected | Grade A/A+; TLS 1.2+ only; no weak ciphers |
| Pass criteria | Every endpoint at Grade A or better |
| Evidence | SSL Labs PDF / PNG per endpoint, dated |

### TC-1.15-02 — Customer Key DEP state (Exchange Online)

| Field | Value |
|---|---|
| Pre-condition | `Connect-ExchangeOnline` |
| Action | `Get-M365DataAtRestEncryptionPolicy \| Format-List Name, PolicyState, AzureKeyIDs` |
| Expected | `PolicyState=Active`; both key URIs present; `Enabled=True` |
| Pass criteria | All expected DEPs Active; URIs resolve to enabled keys in the vault |
| Evidence | Cmdlet output JSON with SHA-256, retained per Control 1.9 retention |

### TC-1.15-03 — Customer Key vault hardening

| Field | Value |
|---|---|
| Pre-condition | `Connect-AzAccount` to subscription hosting Customer Key vaults |
| Action | `Get-AzKeyVault -VaultName <name> -ResourceGroupName <rg> \| Format-List EnableSoftDelete, EnablePurgeProtection, SoftDeleteRetentionInDays, AccessPolicies` |
| Expected | `EnableSoftDelete=True`, `EnablePurgeProtection=True`, retention ≥ 90; access policies show only the workload service principal with `Get/WrapKey/UnwrapKey` |
| Pass criteria | All four flags correct; no human accounts retain key permissions on the vault outside change windows |
| Evidence | Cmdlet output + Azure portal screenshot of access policies |

### TC-1.15-04 — DKE cryptographic isolation (Zone 3)

| Field | Value |
|---|---|
| Pre-condition | DKE service deployed; DKE label published; one user authorized to the DKE service, one control user not |
| Action | Authorized user labels a Word doc with the DKE label, saves, closes; control user attempts to open from their own session |
| Expected | Authorized user opens the document. Control user receives an access-required prompt referencing the DKE service; cannot decrypt content |
| Pass criteria | Both behaviours observed in the same test cycle |
| Evidence | Screen recording or paired screenshots from both sessions |

### TC-1.15-05 — Power Platform CMK on Managed Environment

| Field | Value |
|---|---|
| Pre-condition | Managed Environment hosts Copilot Studio agent; CMK applied |
| Action | PPAC → Environments → select environment → review the **Encryption** panel |
| Expected | "Encryption key managed by customer"; vault key URI linked; environment status Healthy |
| Pass criteria | All three displayed; vault URI clickable and resolves |
| Evidence | PPAC screenshot |

### TC-1.15-06 — Key rotation rehearsal

| Field | Value |
|---|---|
| Pre-condition | Non-production tenant or dedicated test vault |
| Action | Run [`Invoke-FsiKeyRotation.ps1`](powershell-setup.md#5-key-rotation-routine-non-destructive) with `-WhatIf` then for real on a test vault; verify Customer Key picks up the new version |
| Expected | New key version created; previous version remains enabled; Microsoft wrap operation completes against new version (visible in Key Vault diagnostic logs as `KeyWrap` event referencing the new version) |
| Pass criteria | New `KeyWrap` events on new version observed within 24 hours |
| Evidence | Cmdlet output + Sentinel/SIEM event extract |

### TC-1.15-07 — Customer Key revocation rehearsal (Zone 3, non-prod only)

!!! danger "Non-production tenant only"
    This test must be executed in a tenant that holds **no real customer or financial data**. The data-purge path is irreversible; rehearsal in production is never appropriate.

| Field | Value |
|---|---|
| Pre-condition | Non-production tenant with disposable Customer Key DEP and labelled test data |
| Action | Execute the revocation runbook end to end with the named approval chain |
| Expected | Revocation initiated; Microsoft confirms data-purge schedule; after the purge window, attempts to access the protected mailboxes/sites fail |
| Pass criteria | Runbook executes without ambiguity; approval evidence captured at each gate |
| Evidence | Dated runbook execution log + Microsoft Support case ID + SIEM events |

### TC-1.15-08 — Key Vault audit-log alerting

| Field | Value |
|---|---|
| Pre-condition | Key Vault diagnostic settings stream `AuditEvent` to Sentinel/SIEM |
| Action | In a test vault, `Update-AzKeyVaultKey -Enable $false` on a non-DEP-bound key; verify alert |
| Expected | Sentinel/SIEM alert fires within agreed SLA (e.g., 5 min) on the `KeyDisable` event |
| Pass criteria | Alert raised, ticketed, acknowledged; mean-time-to-detect within target |
| Evidence | Alert ticket, SIEM event extract |

---

## Evidence Collection Checklist

Use this list when assembling an audit response or DFS Cybersecurity Certification of Compliance package.

### TLS

- [ ] SSL Labs PDF/PNG per public endpoint, dated
- [ ] PowerShell `Get-TlsCipherSuite` output from a representative client (if hybrid)
- [ ] Certificate inventory CSV with expiry tracking

### Customer Key (Exchange Online)

- [ ] `Get-M365DataAtRestEncryptionPolicy` output (JSON + SHA-256)
- [ ] Purview portal Customer Key page screenshot
- [ ] Most recent CAB ticket for activation / rotation

### Customer Key (SPO/OneDrive)

- [ ] `Get-SPODataEncryptionPolicy` output (JSON + SHA-256)
- [ ] Purview portal screenshot
- [ ] Activation evidence

### Azure Key Vault

- [ ] `Get-AzKeyVault` JSON for each vault
- [ ] Access-policy screenshot (showing only workload SP with `Get/WrapKey/UnwrapKey`)
- [ ] Diagnostic-settings export
- [ ] Sentinel/SIEM dashboard or event extract for last 30 days

### DKE (Zone 3)

- [ ] DKE service architecture diagram
- [ ] DKE label configuration export
- [ ] Paired-screenshot evidence for TC-1.15-04
- [ ] DKE service availability / DR runbook

### Power Platform CMK

- [ ] PPAC environment encryption panel screenshot
- [ ] CMK key reference and vault hardening evidence
- [ ] List of Managed Environments hosting agents with CMK status

### Governance

- [ ] Key rotation register (date, vault/key, version, approver, ticket)
- [ ] Customer Key revocation runbook + most recent rehearsal report
- [ ] Encryption inventory (Copilot grounding source → DEP)
- [ ] Quarterly attestation signed by Compliance Officer

---

## Evidence Artifact Naming Convention

```
Control-1.15_<ArtifactType>_<YYYYMMDD>.<ext>

Examples:
  Control-1.15_SSLLabs_sharepoint_20260415.png
  Control-1.15_GetM365DEP_20260415.json
  Control-1.15_KeyVaultHardening_eo-pri_20260415.json
  Control-1.15_DKEIsolation_20260415.mp4
  Control-1.15_PPACEnvCMK_prod-finance_20260415.png
  Control-1.15_RotationRegister_2026Q2.xlsx
  Control-1.15_RevocationRehearsal_20260118.pdf
```

Each artifact must have an entry in `manifest.jsonl` with SHA-256 hash, generated UTC timestamp, and the script/script-version that produced it.

---

## Attestation Statement Template

```markdown
## Control 1.15 Attestation — Encryption (Data in Transit and at Rest)

**Organization:** [Organization Name]
**Control Owner:** [Name / Role — e.g., Entra Security Admin]
**Reporting Period:** [QX YYYY]
**Date:** [Date]

I attest that, for the reporting period above:

1. TLS 1.2+ is enforced on all public Microsoft 365 tenant endpoints; SSL Labs evidence is on file.
2. Microsoft service encryption with Microsoft-managed keys protects all Exchange Online, SharePoint Online, OneDrive, and Teams content (Zone 1 baseline).
3. Microsoft Purview Customer Key is configured for [Zone 2 / Zone 3] workloads:
    - Exchange Online DEP: [name] — state Active — keys [primary URI] / [secondary URI]
    - SPO/OneDrive DEP: [name] — state Registered — keys [primary URI] / [secondary URI]
4. Both Customer Key vaults have soft delete enabled (90-day retention) and purge protection enabled. Access is scoped to the Microsoft 365 workload service principals with `Get/WrapKey/UnwrapKey` only.
5. Key Vault audit logs stream to [SIEM / Microsoft Sentinel]; alert rules cover `KeyDelete`, `KeyDisable`, `VaultDelete`.
6. (Zone 3) Double Key Encryption is in production for MNPI / [scope]; cryptographic isolation has been validated this period (test TC-1.15-04).
7. Power Platform CMK is applied to all Managed Environments hosting Copilot Studio agents.
8. Key rotation completed on [date] following the documented dual-control procedure; next rotation scheduled for [date].
9. (Zone 3) The Customer Key revocation runbook was rehearsed in non-production on [date]; results recorded in [ticket].

**Open items / compensating controls (DFS 500.15(b)):**
[List any encryption-at-rest gaps with CISO-approved compensating controls and review date]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
