# Control 1.13 — PowerShell Setup: Sensitive Information Types and Pattern Recognition

**Last Verified:** 2026-10-16 — documentation-only review against Microsoft Learn; no tenant sessions, commands, or UI tests performed.

> **Scope.** This playbook is the canonical PowerShell automation reference for Control 1.13 — *Sensitive Information Types (SITs) and Pattern Recognition*. It covers the six Microsoft Purview detection paths (built-in SITs, custom pattern SITs, named entities, trainable classifiers, Exact Data Match (EDM), and keyword dictionaries) as they apply to AI-agent governance for US financial-services tenants in the Microsoft the Microsoft commercial cloud.
>
> **Companion documents.**
>
> - Control specification — `docs/controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`
> - Portal walkthrough — `./portal-walkthrough.md`
> - Verification & testing — `./verification-testing.md`
> - Troubleshooting — `./troubleshooting.md`
> - Shared baseline — `docs/playbooks/_shared/powershell-baseline.md`
>
> **Important regulatory framing.** Nothing in this playbook *guarantees* regulatory compliance. The cmdlets, scripts, and patterns below *support* control objectives required by FINRA Rules 3110 and 4511 (with FINRA RN 24-09 as AI supervisory guidance), SEC Rules 17a-3 / 17a-4 and Reg S-P, GLBA §501(b), SOX §404, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), and Federal Reserve SR 26-2 (formerly SR 11-7). Implementation requires that organizations validate every script against their own change-management, model-risk, and supervisory-review processes before production rollout.

## 0. Wrong-shell trap (READ FIRST)

Control 1.13 has *three* PowerShell surfaces that look interchangeable and are not. Choosing the wrong one is the single most common failure mode and produces silent false-clean evidence.

| Surface | Connect cmdlet | Module | Purpose | Typical 1.13 use |

| **Security & Compliance PowerShell (IPPS)** | `Connect-IPPSSession` | `ExchangeOnlineManagement` v3.5+ | Purview / DLP / SIT / EDM / dictionaries / classifiers | **Almost everything in this playbook** |
| **Exchange Online (EXO)** | `Connect-ExchangeOnline` | `ExchangeOnlineManagement` v3.5+ | Mail-flow, transport rules, mailbox audit | Cross-checks against §11 reconciliation only |
| **Microsoft Graph PowerShell** | `Connect-MgGraph` | `Microsoft.Graph` v2.x | Directory, role, license, audit-log read | Pre-flight licence and role checks (§1) |

> **There is no separate `IPPSSession` module.** `Connect-IPPSSession` ships inside `ExchangeOnlineManagement`. Installing a non-existent `IPPSSession` module is a recurring anti-pattern and will fail silently because PowerShell's package providers will simply return zero results. Pin the *Exchange* module and you have IPPS.

> **Disconnect note.** Use `Disconnect-ExchangeOnline` for **both** EXO and IPPS REST sessions. The cmdlet `Disconnect-IPPSSession` *does not exist* — invoking it produces `CommandNotFoundException` and may leave you connected. See §10a.

### PowerShell edition guard

For the pinned `ExchangeOnlineManagement` 3.5.0 examples below, use PowerShell **7.4+** on a supported Windows host, not 7.2. The [current compatibility matrix](https://learn.microsoft.com/en-us/powershell/exchange/exchange-online-powershell-v2) requires 7.4+ for module 3.5.0–3.9.2 and 7.6+ for 3.10.0+. Windows PowerShell 5.1 is separately supported. IPPS is not currently supported on PowerShell 7 Linux/macOS. Validate the approved module/runtime pair; these illustrative pins do not supersede patch review.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }

if ($PSVersionTable.PSEdition -ne 'Core') {
    throw "This script targets PowerShell 7+. Current edition: $($PSVersionTable.PSEdition)."
}
```

If a script must run under Windows PowerShell 5.1 (for example because it calls the EDM upload agent on a hardened jump host), state it explicitly: `#Requires -Version 5.1` and document the reason in the file header.

## 1. Pre-flight: session bootstrap, role and licence checks

Every Control 1.13 script begins with the same five preconditions: PowerShell edition pinned, module version pinned, IPPS session opened with banner suppression, and admin role + licence verified through Microsoft Graph. Bundle them once into a reusable `Initialize-Agt113Session` helper so individual scripts do not drift.

### 1.1 The session bootstrap helper

Save as `Initialize-Agt113Session.ps1` in your shared automation library:

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Authentication'; RequiredVersion = '2.15.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Identity.DirectoryManagement'; RequiredVersion = '2.15.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Users';            RequiredVersion = '2.15.0' }

<#
.SYNOPSIS
    Bootstraps a Control 1.13 admin session: opens IPPS + Graph in the correct
    verifies role assignment and SKU entitlement, and starts a
    timestamped transcript for evidence collection.
.PARAMETER AdminUpn
    UPN of the admin executing the change. Used for role-assignment lookup.
.PARAMETER Cloud
    Commercial (the target cloud for this framework).
.PARAMETER EvidenceRoot
    Absolute path to the evidence directory (transcript + JSON + manifest land here).
.PARAMETER RequiredRoles
    Role display names that the operator must hold in at least one. Defaults to the
    minimum-privilege set for SIT/DLP work.
.PARAMETER RequiredSkuPartNumbers
    Tenant SKUs that must be present for the planned change (E5 / Compliance E5 /
    Copilot for M365). Verified against Get-MgSubscribedSku.
#>
function Initialize-Agt113Session {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        [Parameter(Mandatory)] [string]   $AdminUpn,    [Parameter(Mandatory)] [string] $Cloud = 'Commercial',
        [Parameter(Mandatory)] [string]   $EvidenceRoot,
        [string[]] $RequiredRoles = @(
            'Compliance Administrator',
            'Compliance Data Administrator',
            'Information Protection Administrator'
        ),
        [string[]] $RequiredSkuPartNumbers = @('SPE_E5')
    )

    $endpoints = @{ IPPSConnectionUri = $null; IPPSAuthorityUri = $null;
                    GraphEnvironment  = 'Global' }

    # 2. Evidence root + transcript.
    if (-not (Test-Path $EvidenceRoot)) {
        New-Item -ItemType Directory -Path $EvidenceRoot -Force | Out-Null
    }
    $stamp        = Get-Date -Format 'yyyyMMdd-HHmmss'
    $transcript   = Join-Path $EvidenceRoot "agt113-$stamp.transcript.log"
    Start-Transcript -Path $transcript -IncludeInvocationHeader | Out-Null
    Write-Information "Transcript: $transcript" -InformationAction Continue

    $ippsParams = @{ UserPrincipalName = $AdminUpn; ShowBanner = $false }
    if ($endpoints.IPPSConnectionUri) { $ippsParams.ConnectionUri = $endpoints.IPPSConnectionUri }
    if ($endpoints.IPPSAuthorityUri)  { $ippsParams.AzureADAuthorizationEndpointUri = $endpoints.IPPSAuthorityUri }
    if ($PSCmdlet.ShouldProcess("IPPS ($Cloud)", 'Connect-IPPSSession')) {
        Connect-IPPSSession @ippsParams
    }

    # 4. Connect-MgGraph for role + SKU verification.
    $graphScopes = @('Directory.Read.All','RoleManagement.Read.Directory','Organization.Read.All')
    if ($PSCmdlet.ShouldProcess("Graph ($Cloud)", 'Connect-MgGraph')) {
        Connect-MgGraph -Environment $endpoints.GraphEnvironment -Scopes $graphScopes -NoWelcome
    }

    # 5. Direct directory-role inventory only; Purview RBAC is a separate check.
    $me   = Get-MgUser -UserId $AdminUpn -ErrorAction Stop
    $assigns = Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '$($me.Id)'" -ExpandProperty RoleDefinition
    $held = $assigns.RoleDefinition.DisplayName | Sort-Object -Unique
    $hit  = $held | Where-Object { $RequiredRoles -contains $_ }
    Write-Information "Direct directory-role inventory: $($held -join ', ')" -InformationAction Continue
    Write-Warning 'This does not evaluate Purview role groups, group-based grants, PIM activation, or assigned-user feature entitlement. Complete PRE-01 and PRE-04 separately.'

    # 6. Tenant SKU check.
    $skus = Get-MgSubscribedSku
    foreach ($want in $RequiredSkuPartNumbers) {
        if (-not ($skus | Where-Object { $_.SkuPartNumber -eq $want })) {
            throw "Tenant lacks required SKU '$want'. Aborting."
        }
    }
    Write-Information "SKU check OK: $($RequiredSkuPartNumbers -join ', ')" -InformationAction Continue

    # 7. Return a session context object that downstream scripts consume.
    [PSCustomObject]@{
        Cloud         = $Cloud
        AdminUpn      = $AdminUpn
        Endpoints     = $endpoints
        EvidenceRoot  = $EvidenceRoot
        Transcript    = $transcript
        Stamp         = $stamp
    }
}
```

### 1.2 Minimum-privilege role expectations

| Task | Minimum role (Purview) | Notes |

| Read SIT / dictionary / classifier inventory | Compliance Data Administrator | Read-only; preferred for inventory scripts |
| Author or modify SITs, dictionaries, EDM schemas | Compliance Administrator **or** Information Protection Administrator | Use Information Protection Administrator where the tenant has split duties |
| Author DLP policies that bind SITs to Copilot / Exchange / SharePoint workloads | Compliance Administrator | Policy cmdlets enforce this server-side |
| EDM `EdmUploadAgent.exe` data upload | Authorized work/school account in the tenant's `EDM_DataUploaders` security group | Not a local host group; schema administration requires separate Purview permissions |
| Trainable classifier publish | Compliance Administrator + tenant-level FSI governance gate sign-off (§8) | Model-risk governance is procedural, not technical |

Use canonical short role names when documenting evidence. The bootstrap's direct Graph inventory is supplementary, not an authorization oracle for Purview role groups. Tenant SKU presence also does not prove a user is licensed; complete feature-specific PRE-01/PRE-04 before mutation.

### 1.3 Module pinning

Pin to a known-good version of `ExchangeOnlineManagement` and refuse to run against newer/older builds without explicit override. The shared baseline (`docs/playbooks/_shared/powershell-baseline.md` §1) describes the rationale.

```powershell
$wantModule  = 'ExchangeOnlineManagement'
$wantVersion = [version]'3.5.0'
$mod = Get-Module -ListAvailable -Name $wantModule |
       Where-Object { $_.Version -eq $wantVersion } |
       Sort-Object Version -Descending | Select-Object -First 1
if (-not $mod) {
    throw "Required module $wantModule $wantVersion not installed. Install the approved exact version before proceeding."
}
Import-Module $mod.Path -Force
```

## 2. Coverage boundary: PowerShell vs portal vs Maker

PowerShell is authoritative for inventory, idempotent rollout, drift detection, rollback, and evidence. It is *not* authoritative for everything. Be explicit with operators about which tasks must be done where.

| Task | PowerShell | Purview portal | Maker (Power Platform / Microsoft Copilot Studio) |
|---|:-:|:-:|:-:|
| Inventory all SITs / dictionaries / classifiers / EDM schemas | ✅ Required | Read-only | n/a |
| Create / update / remove a *custom pattern* SIT (regex + keyword + Luhn) | ✅ Authoritative (XML rule package) | ⚠ Convenient for first draft, but no version control | n/a |
| Create / update / remove a *document fingerprint* SIT | ✅ Authoritative | Limited UI | n/a |
| Create / update / remove a *keyword dictionary* | ✅ Authoritative (UTF-16 binary) | ⚠ UI accepts up to 100 KB; PowerShell required for larger or non-ASCII terms | n/a |
| Create / upload an EDM schema | Schema only via PS; data via `EdmUploadAgent.exe` | Schema editor available | n/a |
| Train and publish a *trainable classifier* | ⚠ Cmdlet surface still moving; **portal is the supported path today** | ✅ Authoritative for publish | n/a |
| Bind SITs into a DLP policy *for Copilot* | ✅ Authoritative | ✅ Available | Maker cannot configure DLP |
| Choose which SITs the agent *consumes* | n/a | n/a (Maker decides scope, admin decides DLP) | ✅ Maker selects knowledge sources; DLP enforces what may leave |
| View Activity Explorer / Purview Audit evidence | Read via `Search-UnifiedAuditLog` | ✅ Authoritative dashboard | n/a |

> **Trainable classifiers — read this carefully.** Microsoft has renamed the cmdlet surface multiple times between `*-MLClassifier` and `*-Classifier`. As of this playbook's last UI-verification window, only the portal path is consistently shippable. Treat any PowerShell automation against trainable classifiers as a candidate for breakage and **verify the exact cmdlet name against current Microsoft Learn before each change window**. See §8 for the FSI governance gate that gates this control entirely.

## 3. Inventory (read-only): `Get-FsiSitInventory.ps1`

A clean inventory is the foundation of every subsequent operation. Run it before *any* mutation, after *any* mutation, and on a daily schedule into the evidence store. The script is read-only and safe to run with `Compliance Data Administrator`.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
<#
.SYNOPSIS
    Read-only inventory of every SIT, dictionary, EDM schema, classifier, and DLP
    policy/rule that references a SIT. Emits NDJSON + CSV per object class plus a
    SHA-256 evidence manifest.
.PARAMETER Session
    Output of Initialize-Agt113Session.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] $Session
)

$ErrorActionPreference = 'Stop'
$out = Join-Path $Session.EvidenceRoot ("inventory-" + $Session.Stamp)
New-Item -ItemType Directory -Path $out -Force | Out-Null

# 1. Built-in + custom SITs (single-entity definitions).
$sits = Get-DlpSensitiveInformationType |
        Select-Object Name, Publisher, Type, RulePackId, State, Description,
                      RecommendedConfidence, @{n='LastModified'; e={$_.WhenChangedUTC}}
$sits | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $out 'sits.json')      -Encoding utf8
$sits | Export-Csv      -NoTypeInformation -Path (Join-Path $out 'sits.csv')

# 2. SIT rule packages (XML container — one pack may carry many SITs).
$packs = Get-DlpSensitiveInformationTypeRulePackage |
         Select-Object Name, Publisher, Version, State, WhenChangedUTC,
                       @{n='RulePackXmlSize'; e={ $_.SerializedClassificationRuleCollection.Length }}
$packs | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $out 'sit-rule-packages.json') -Encoding utf8
foreach ($p in (Get-DlpSensitiveInformationTypeRulePackage)) {
    $safe = ($p.Name -replace '[^\w\-]','_')
    [System.IO.File]::WriteAllBytes(
        (Join-Path $out "rulepack-$safe.xml"), $p.SerializedClassificationRuleCollection
    )
}

# 3. Keyword dictionaries.
$dicts = Get-DlpKeywordDictionary |
         Select-Object Name, Description, Identity, KeywordCount,
                       @{n='LastModified'; e={$_.WhenChangedUTC}}
$dicts | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $out 'dictionaries.json') -Encoding utf8

# 4. EDM schemas.
$edm = Get-DlpEdmSchema |
       Select-Object Name, Description, State, DataStoreName,
                     @{n='ColumnCount'; e={ ($_.EdmSchemaXML -split '<Field ' ).Count - 1 }},
                     WhenChangedUTC
$edm | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $out 'edm.json') -Encoding utf8

# 5. Capture classifier inventory in the supported portal workflow (§8).
# Do not write an empty inventory that could be mistaken for a verified absence.

# 6. DLP policies + rules that reference SITs (consumption side).
$pols  = Get-DlpCompliancePolicy  | Select-Object Name, Mode, Enabled, EnforcementPlanes, CreatedBy, WhenChangedUTC
$rules = Get-DlpComplianceRule    | Select-Object Name, ParentPolicyName, Disabled, ContentContainsSensitiveInformation, AdvancedRule, WhenChangedUTC
$pols  | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $out 'dlp-policies.json') -Encoding utf8
$rules | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $out 'dlp-rules.json')    -Encoding utf8

# 7. SHA-256 manifest (see §14).
Get-ChildItem $out -File | ForEach-Object {
    [PSCustomObject]@{
        File   = $_.Name
        SHA256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        Bytes  = $_.Length
    }
} | ConvertTo-Json -Depth 3 | Set-Content (Join-Path $out 'manifest.json') -Encoding utf8

Write-Information "Inventory written to $out" -InformationAction Continue
```

**Parameter and output checks.** `Get-DlpSensitiveInformationType` does not document `-ResultSize`; do not add it generically to every inventory cmdlet. Save raw returned objects before selecting fields, and inspect actual properties rather than interpreting null projected fields as proof of state. Package XML is in `SerializedClassificationRuleCollection`; schema XML is in `EdmSchemaXML`. See [SIT cmdlet](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-dlpsensitiveinformationtype) and [custom SIT export](https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type-in-scc-powershell).

## 4. Keyword dictionaries: `New-FsiKeywordDictionary.ps1`

Keyword dictionaries back named-counterparty lists (broker-dealer panels, restricted-list issuers, MNPI deal codenames). The single most common implementation bug is **encoding the term file as UTF-8**. The `-FileData` parameter requires a **UTF-16 (Unicode) byte array** with `\r\n` line terminators. UTF-8 input parses to a corrupt or empty dictionary and silently fails on accented terms (e.g., "Société Générale", "Crédit Agricole", "Banco Bilbao Vizcaya Argentaria").

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
<#
.SYNOPSIS
    Idempotently create or update a Purview keyword dictionary from a list of terms.
    Encodes the term file as UTF-16 LE (Unicode) with CRLF line endings — the only
    encoding accepted by New-DlpKeywordDictionary -FileData.
.PARAMETER Session
    Output of Initialize-Agt113Session.
.PARAMETER Name
    Dictionary display name. Used as the natural key for idempotency.
.PARAMETER Description
    Free-form description, included in evidence.
.PARAMETER Terms
    String array of dictionary terms. Deduplicated and sorted; blanks removed.
.EXAMPLE
    .\New-FsiKeywordDictionary.ps1 -Session $s -Name 'FSI-Restricted-Issuers' `
        -Description 'Restricted list — research blackout' `
        -Terms (Get-Content .\restricted-list.txt)
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] $Session,
    [Parameter(Mandatory)] [string]   $Name,
    [Parameter(Mandatory)] [string]   $Description,
    [Parameter(Mandatory)] [string[]] $Terms
)

$ErrorActionPreference = 'Stop'

# 1. Normalise terms.
$clean = $Terms |
         Where-Object { $_ -and $_.Trim() } |
         ForEach-Object { $_.Trim() } |
         Sort-Object -Unique
if ($clean.Count -eq 0) { throw "No usable terms supplied." }

# 2. Build a UTF-16 LE byte array with CRLF terminators. THIS IS NOT OPTIONAL.
$sb = [System.Text.StringBuilder]::new()
foreach ($t in $clean) { [void]$sb.Append($t); [void]$sb.Append("`r`n") }
$bytes = [System.Text.Encoding]::Unicode.GetBytes($sb.ToString())

# 3. Before-snapshot for rollback evidence.
$existing = Get-DlpKeywordDictionary -Name $Name -ErrorAction SilentlyContinue
$beforePath = Join-Path $Session.EvidenceRoot ("dict-$Name-before-$($Session.Stamp).json")
$existing | ConvertTo-Json -Depth 6 | Set-Content $beforePath -Encoding utf8

# 4. Idempotent upsert.
if ($existing) {
    if ($PSCmdlet.ShouldProcess($Name, 'Set-DlpKeywordDictionary (update)')) {
        Set-DlpKeywordDictionary -Identity $Name -FileData $bytes -Description $Description
    }
} else {
    if ($PSCmdlet.ShouldProcess($Name, 'New-DlpKeywordDictionary (create)')) {
        New-DlpKeywordDictionary -Name $Name -Description $Description -FileData $bytes | Out-Null
    }
}

# 5. After-snapshot.
$after = Get-DlpKeywordDictionary -Name $Name
$afterPath = Join-Path $Session.EvidenceRoot ("dict-$Name-after-$($Session.Stamp).json")
$after | ConvertTo-Json -Depth 6 | Set-Content $afterPath -Encoding utf8

Write-Information ("Dictionary '{0}' now contains {1} terms." -f $Name, $after.KeywordCount) -InformationAction Continue
```

**Operational notes.**

- Dictionary `Identity` is a GUID, distinct from `Name`. Preserve the GUID used by SIT XML references.
- Keyword dictionaries share a **1 MB post-compression tenant limit**, not 1 MB per dictionary. Splitting dictionaries does not evade the combined limit. See [keyword dictionaries](https://learn.microsoft.com/en-us/purview/sit-create-a-keyword-dictionary).
- Reference a dictionary using its actual GUID as the XML `idRef`, obtained from `(Get-DlpKeywordDictionary -Name $Name).Identity`; do not use the display name or a `Keyword_Dictionary_` prefix as the identifier.

## 5. Custom pattern SIT rule package: `New-FsiCustomSitPack.ps1`

This is the highest-leverage and highest-risk operation in 1.13. A *rule package* is an XML container that may publish one or many SITs. The cmdlets are:

| Operation | Cmdlet | Notes |

| Create rule package | `New-DlpSensitiveInformationTypeRulePackage -FileData $bytes` | Keep XML declaration and actual byte encoding aligned |
| Update rule package | `Set-DlpSensitiveInformationTypeRulePackage -FileData $bytes` | XML identifies the package; bump `RulePack/Version` first |
| Remove rule package | `Remove-DlpSensitiveInformationTypeRulePackage -Identity <Name>` | Will fail while any DLP rule binds a SIT it defines |

> **Do not confuse `New-DlpSensitiveInformationType` with `New-DlpSensitiveInformationTypeRulePackage`.** The former is the document-fingerprint workflow (§6), documented with fingerprint objects or template `-FileData`; custom regex patterns use the rule-package XML workflow.

### 5.1 Schema rules that the validator enforces

The XML schema is unforgiving. The most common failures, all of which return cryptic `Invalid sensitive information type rule package` errors:

1. **`<Regex>` and `<Keyword>` definitions must live inside `<Rules>`.** They are not children of `<Entity>`. The `<Entity>` block uses `<Pattern>` → `<IdMatch idRef="…" />` / `<Match idRef="…" />` to *reference* regex/keyword definitions that live as siblings later in `<Rules>`.
2. **`<Version>` is on `<RulePack>` (the inner element), not `<RulePackage>`.** Bump it on every change or the upload will silently keep the previous body.
3. **Every entity, regex, and keyword needs a stable GUID.** Generate them once and treat them as immutable. Inlining `$(New-Guid)` in the heredoc is a recurring bug — every script run produces a different SIT.
4. **Confidence levels (60 / 75 / 85) are tied to `<Pattern confidenceLevel="…">` blocks.** Use three patterns of decreasing strictness so DLP rules can choose a tier.
5. **`<LocalizedStrings>` is mandatory** and must list each entity by GUID. Missing entries silently truncate the SIT picker in the portal.

### 5.2 Worked example — Contoso 9-digit account number with contextual evidence

The example below publishes a single SIT named `Contoso-Account-Number` that:

- Matches a nine-digit firm-defined account pattern with contextual evidence; it does not claim an undocumented `Func_luhn_check` validates arbitrary numbers. Microsoft does not support uploading custom functions.
- Increases confidence when nearby keywords appear (`account`, `acct`, `client id`).
- Boosts confidence further in MNPI contexts (`merger`, `acquisition`, `material non-public`).
- **Excludes** known test-data sentinels (`TEST-`, `SAMPLE-`, `XXX-`) so SDLC pipelines do not generate false positives.
- Emits at three confidence tiers (60 / 75 / 85) for downstream DLP tier selection.

Save the XML as a here-string in your script — but generate GUIDs **once**, externally, and paste them in:

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] $Session,
    [Parameter(Mandatory)] [string] $RulePackName     = 'FSI-Contoso-Custom-SITs',
    [Parameter(Mandatory)] [string] $RulePackVersion  = '1.0.0.0'
)

$ErrorActionPreference = 'Stop'

# GUIDs frozen at design time. DO NOT regenerate on each run.
$pkgGuid    = '0d6e9b51-6e5e-4f6e-95a6-1e66a0e6b001'
$entityGuid = '7b2e0e6e-9b8f-4e6c-8c2a-2c7e0a1f0001'
$regexGuid  = 'bb1e91b8-2d4a-44c2-9b5d-2f0a8e0a0001'
$kwAcctGuid = 'f1f2f3f4-1111-2222-3333-444455556601'
$kwMnpiGuid = 'f1f2f3f4-1111-2222-3333-444455556602'
$kwTestGuid = 'f1f2f3f4-1111-2222-3333-444455556603'

$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<RulePackage xmlns="http://schemas.microsoft.com/office/2011/mce">
  <RulePack id="$pkgGuid">
    <Version major="1" minor="0" build="0" revision="0" />
    <Publisher id="11111111-2222-3333-4444-555555555555" />
    <Details defaultLangCode="en-us">
      <LocalizedDetails langcode="en-us">
        <PublisherName>Contoso FSI Governance</PublisherName>
        <Name>FSI Contoso Custom SITs</Name>
        <Description>Contoso financial-services custom sensitive information types. Author: GRC. Change ticket required.</Description>
      </LocalizedDetails>
    </Details>
  </RulePack>

  <Rules>
    <!-- ENTITY (consumer of regex + keyword definitions below) -->
    <Entity id="$entityGuid" patternsProximity="300" recommendedConfidence="75">

      <!-- High (85): account pattern plus contextual evidence, excluding approved sentinels -->
      <Pattern confidenceLevel="85">
        <IdMatch idRef="Regex_Contoso_Account" />
        <Any minMatches="1">
          <Match idRef="Keyword_Contoso_Account" />
          <Match idRef="Keyword_Contoso_MNPI" />
        </Any>
        <Any minMatches="0" maxMatches="0">
          <Match idRef="Keyword_Contoso_Test" />
        </Any>
      </Pattern>

      <!-- Medium (75): account pattern plus account keywords -->
      <Pattern confidenceLevel="75">
        <IdMatch idRef="Regex_Contoso_Account" />
        <Match idRef="Keyword_Contoso_Account" />
        <Any minMatches="0" maxMatches="0">
          <Match idRef="Keyword_Contoso_Test" />
        </Any>
      </Pattern>

      <!-- Low (60): account pattern without corroborating keywords -->
      <Pattern confidenceLevel="60">
        <IdMatch idRef="Regex_Contoso_Account" />
        <Any minMatches="0" maxMatches="0">
          <Match idRef="Keyword_Contoso_Test" />
        </Any>
      </Pattern>
    </Entity>

    <!-- REGEX DEFINITIONS (siblings of Entity, INSIDE <Rules>) -->
    <Regex id="Regex_Contoso_Account">(?&lt;![\d-])\d{9}(?![\d-])</Regex>

    <!-- KEYWORD DEFINITIONS (siblings of Entity, INSIDE <Rules>) -->
    <Keyword id="Keyword_Contoso_Account">
      <Group matchStyle="word">
        <Term>account</Term>
        <Term>acct</Term>
        <Term>client id</Term>
        <Term>customer number</Term>
      </Group>
    </Keyword>

    <Keyword id="Keyword_Contoso_MNPI">
      <Group matchStyle="word">
        <Term>merger</Term>
        <Term>acquisition</Term>
        <Term>material non-public</Term>
        <Term>MNPI</Term>
        <Term>deal code</Term>
      </Group>
    </Keyword>

    <Keyword id="Keyword_Contoso_Test">
      <Group matchStyle="string">
        <Term>TEST-</Term>
        <Term>SAMPLE-</Term>
        <Term>XXX-</Term>
        <Term>do not use</Term>
      </Group>
    </Keyword>

    <LocalizedStrings>
      <Resource idRef="$entityGuid">
        <Name default="true" langcode="en-us">Contoso Account Number</Name>
        <Description default="true" langcode="en-us">Nine-digit firm-defined account pattern with confidence-specific contextual evidence. Test sentinel exclusions require adversarial validation.</Description>
      </Resource>
    </LocalizedStrings>
  </Rules>
</RulePackage>
"@

# Encode consistently with the XML UTF-16 declaration.
$bytes = [System.Text.Encoding]::Unicode.GetBytes($xml)

# Before-snapshot.
$existing = @(Get-DlpSensitiveInformationTypeRulePackage | Where-Object {
    $_.Name -eq $RulePackName -or $_.Identity -eq $RulePackName
})
if ($existing.Count -gt 1) { throw 'Ambiguous rule-package identity.' }
$beforePath = Join-Path $Session.EvidenceRoot ("sitpack-$RulePackName-before-$($Session.Stamp).xml")
if ($existing) {
    [System.IO.File]::WriteAllBytes($beforePath, $existing.SerializedClassificationRuleCollection)
}

if ($existing) {
    if ($PSCmdlet.ShouldProcess($RulePackName, 'Set-DlpSensitiveInformationTypeRulePackage')) {
        Set-DlpSensitiveInformationTypeRulePackage -FileData $bytes
    }
} else {
    if ($PSCmdlet.ShouldProcess($RulePackName, 'New-DlpSensitiveInformationTypeRulePackage')) {
        New-DlpSensitiveInformationTypeRulePackage -FileData $bytes | Out-Null
    }
}

# After-snapshot.
$after = Get-DlpSensitiveInformationTypeRulePackage -Identity $RulePackName
[System.IO.File]::WriteAllBytes(
    (Join-Path $Session.EvidenceRoot "sitpack-$RulePackName-after-$($Session.Stamp).xml"),
    $after.SerializedClassificationRuleCollection
)

Write-Information "Rule package '$RulePackName' published version $RulePackVersion." -InformationAction Continue
```

> **Test exclusions adversarially.** The documented rule-package exclusion uses `<Any minMatches="0" maxMatches="0">`, not `<ExcludedMatch>`. Any sentinel-based exclusion can be copied into real content to suppress detection; use only an explicitly approved, validated exception design and retain non-excluded positives. The example is a design sketch, not a tenant-tested deployment.

## 6. Document fingerprint SITs: `Add-FsiDocumentFingerprintSit.ps1`

Document fingerprinting matches a template's **text**, not visual layout. The [documented multi-template example](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpsensitiveinformationtype) creates fingerprint objects with `New-DlpFingerprint` before passing them to `-Fingerprints`; raw template bytes belong to `-FileData`, not that array.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] $Session,
    [Parameter(Mandatory)] [string]   $Name,
    [Parameter(Mandatory)] [string]   $Description,
    [Parameter(Mandatory)] [string[]] $TemplatePaths,
    [ValidateSet('Low','Medium','High')] [string] $RecommendedConfidence = 'High'
)

$ErrorActionPreference = 'Stop'

# 1. Create fingerprint objects from each template.
$prints = foreach ($p in $TemplatePaths) {
    if (-not (Test-Path $p)) { throw "Template not found: $p" }
    $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $p).Path)
    $fingerprint = New-DlpFingerprint -FileData $bytes -Description $Description
    $fingerprint[0]
}

# 2. Idempotent upsert.
$existing = @(Get-DlpSensitiveInformationType | Where-Object { $_.Name -eq $Name })
if ($existing.Count -gt 1) { throw 'Ambiguous SIT name.' }
if ($existing -and $existing.Type -ne 'DocumentFingerprint') {
    throw "SIT '$Name' already exists with type '$($existing.Type)'. Pick a different name."
}

if ($existing) {
    if ($PSCmdlet.ShouldProcess($Name, 'Set-DlpSensitiveInformationType')) {
        Set-DlpSensitiveInformationType -Identity $Name -Fingerprints $prints -Description $Description
    }
} else {
    if ($PSCmdlet.ShouldProcess($Name, 'New-DlpSensitiveInformationType')) {
        New-DlpSensitiveInformationType -Name $Name -Description $Description `
            -Fingerprints $prints -IsExact:$false | Out-Null
    }
}

$after = Get-DlpSensitiveInformationType -Identity $Name
$after | ConvertTo-Json -Depth 4 |
    Set-Content (Join-Path $Session.EvidenceRoot "fp-$Name-$($Session.Stamp).json") -Encoding utf8

Write-Information "Document-fingerprint SIT '$Name' updated. Type: $($after.Type)." -InformationAction Continue
```

**Operational caveats.**

- Document fingerprints match template text with configured partial/exact thresholds. Use the portal file-upload test for documents; §10's text collector is not a binary-document upload API. Validate positives/negatives and limitations in the [fingerprinting guide](https://learn.microsoft.com/en-us/purview/document-fingerprinting).
- A single fingerprint SIT can carry *multiple* template files — pass them all in the same `-Fingerprints` array so the SIT votes the union of patterns.
- Current fingerprint creation supports per-level partial-match percentages (`ThresholdConfig`) and exact matching (`IsExact`); inspect actual configuration rather than assuming one recommended-confidence property defines every threshold.

## 7. Exact Data Match (EDM): `Initialize-FsiEdm.ps1` + `EdmUploadAgent.exe`

EDM is the only Purview detection path that matches against *the actual customer/account list*, not a regex approximation of it. The architecture has two halves:

1. **Schema** (PowerShell, IPPS) — declares the column layout and which columns are searchable / case-sensitive / ignore-punctuation.
2. **Hashed data store** (Windows utility, `EdmUploadAgent.exe`) — runs on a hardened on-prem or Azure VM jump host, salts and one-way hashes the source CSV, and uploads the hash store to the Purview service. The cleartext data **never** leaves the upload host.

### 7.1 Schema (PowerShell)

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] $Session,
    [Parameter(Mandatory)] [string] $SchemaName        = 'FSI-Customer-Master',
    [Parameter(Mandatory)] [string] $DataStoreName     = 'FSICustomerMasterDS',
    [Parameter(Mandatory)] [string] $SchemaXmlPath
)

$ErrorActionPreference = 'Stop'

# Schema fields identify searchable primary and supporting values, not cleartext return columns.
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $SchemaXmlPath))

$existing = @(Get-DlpEdmSchema | Where-Object {
    $_.Name -eq $SchemaName -or $_.Identity -eq $SchemaName
})
if ($existing.Count -gt 1) { throw 'Ambiguous EDM schema identity.' }
if ($existing) {
    if ($PSCmdlet.ShouldProcess($SchemaName, 'Set-DlpEdmSchema')) {
        Set-DlpEdmSchema -FileData $bytes
    }
} else {
    if ($PSCmdlet.ShouldProcess($SchemaName, 'New-DlpEdmSchema')) {
        New-DlpEdmSchema -FileData $bytes | Out-Null
    }
}

$after = Get-DlpEdmSchema -Identity $SchemaName
$after | ConvertTo-Json -Depth 8 |
    Set-Content (Join-Path $Session.EvidenceRoot "edm-$SchemaName-$($Session.Stamp).json") -Encoding utf8

Write-Information "EDM schema '$SchemaName' state: $($after.State). Data store: $($after.DataStoreName)." -InformationAction Continue
```

### 7.2 Data upload (`EdmUploadAgent.exe`)

`EdmUploadAgent.exe` is a separate Windows utility, not a PowerShell module. Download the installer package matching your cloud from Microsoft Learn.

| Step | Subcommand | Purpose |

| 1 | `EdmUploadAgent.exe /ValidateData /DataFile <csv> /Schema <schema.xml>` | Confirms CSV column count + types match schema |
| 2 | `EdmUploadAgent.exe /Authorize` | Sign in with the work/school user in the EDM_DataUploaders security group |
| 3 | `EdmUploadAgent.exe /CreateHash /DataFile <csv> /Schema <schema.xml> /HashLocation <dir>` | Creates salted hash output locally |
| 4 | `EdmUploadAgent.exe /UploadHash /DataStoreName <name> /HashFile <hash>` | Uploads hash store to Purview |
| 5 | Scheduled task following the documented EDM refresh workflow | Firm-defined refresh cadence; no documented `/SaveSchedule` subcommand |
| 6 | `EdmUploadAgent.exe /GetDataStore` and `/GetSession /DataStoreName <name>` | Read-back data-store update times and upload sessions |
| 7 | Remove dependent EDM SIT, then remove schema through the supported workflow | Schema deletion also deletes its data store within 24 hours |

Verify schema export separately from upload completion:

```powershell
$schema = Get-DlpEdmSchema -Identity $SchemaName
Set-Content -Path '.\edm-schema-export.xml' -Value $schema.EdmSchemaXML
# Capture /GetDataStore and /GetSession on the Upload Agent host, then test detection.
```

### 7.3 Caveats

- **Searchable column cap.** The current schema wizard guide says one to ten searchable fields; the same guide's manual XML steps still say five. Verify the chosen workflow; neither supports the previous 32-searchable-column claim. Supporting fields are not cleartext "return columns".
- **Refresh and test readiness.** Capture upload/indexing completion; test an hour later, and wait at least an hour after EDM SIT changes. Existing files can require reclassification even when direct tests pass. These are documented expectations, not a guaranteed end-to-end SLA.
- **Hash store data residency.** The cleartext source file never leaves the upload host. Treat the upload host itself as a high-value system: tier-0 admin model, mailbox-less service identity, no inbound SMB, audit-logged file mounts, and a documented destruction process for the source CSV after upload.
- **Removal order.** Remove dependent EDM SITs before deleting a schema. Schema deletion also removes the associated data store within 24 hours. See [schema lifecycle](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-create-schema), [hash/upload commands](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-hash-upload), and [EDM tests](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-test).

## 8. Trainable classifiers — FSI governance gate

Trainable classifiers are machine-learning models that classify content (research, complaint mail, MNPI narratives) by *style* rather than pattern. They are powerful and they are **model-risk artefacts**. In a US FSI tenant, a trainable classifier published into a DLP rule that gates Copilot output is in scope for **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** and **Federal Reserve SR 26-2 (formerly SR 11-7)** model-risk-management expectations.

### 8.1 Mandatory governance gate

The framework requires the following sign-offs *before* a trainable classifier is published into any production DLP rule that affects agent grounding or output:

1. **Model inventory entry** — the classifier appears in the firm's model inventory with owner, intended use, and limitations.
2. **Independent validation** — a documented validation pass against a held-out labelled dataset, including precision/recall by class.
3. **Bias and language-coverage statement** — explicit acknowledgement that the model is **English-only at general availability** and a documented assessment of whether non-English content in scope creates a control gap.
4. **Periodic revalidation cadence** — at least annually, and after any retraining.
5. **Rollback plan** — pre-authored DLP rule that disables the classifier-bound condition without deleting the classifier itself.

The control specification (`1.13-sensitive-information-types-sits-and-pattern-recognition.md` §"FSI Governance Gate for Trainable Classifiers") is the authoritative source for sign-off owners.

### 8.2 Supported classifier workflow

Use the [documented portal workflow](https://learn.microsoft.com/en-us/purview/classifier-get-started-with), not guessed `Get-Classifier`, `Get-MLClassifier`, or `Get-TrainableClassifier` alternatives. Capture the actual classifier inventory/status in the portal. Custom training uses 50–500 positive and 150–1,500 negative text-based samples in separate SharePoint folders; the author must have access. Custom classifiers support English only; pretrained language coverage varies. Published custom classifiers cannot be retrained: replacement requires a new classifier and revalidated consumer bindings.

### 8.3 Evidence

Capture, at every change window:

- The actual portal classifier inventory, lifecycle status, supported languages, and validation results.
- The DLP rule(s) that bind each classifier (filter `Get-DlpComplianceRule` for `AdvancedRule` strings containing the classifier identity).
- A copy of the model-risk validation report PDF and its SHA-256, written into the evidence pack alongside the technical artefacts.

## 9. DLP for Microsoft 365 Copilot: author and verify the supported policy

Use [portal walkthrough Step 9](portal-walkthrough.md#step-9-dlp-for-microsoft-365-copilot-consumer-policy-that-uses-the-sits) and the [current Microsoft Learn procedure](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about). The former provisioning example's location GUID lookup, `CopilotExperiences` payload, and generic `ExcludeContentProcessing` action were not verified against that procedure and are withdrawn rather than represented as a working script.

Create a **Custom** policy with the **Microsoft 365 Copilot and Copilot Chat** location (all other locations are disabled). Verify initiating-user scope and exclusions. Use separate rules for supported built-in/custom SITs in typed prompts and sensitivity labels on grounding files/emails. Prompt processing restriction is preview and tenant-rollout dependent; it does not scan file uploads or grounding files. Label exclusion does not automatically follow from a SIT match or label assignment. Simulation, alerts, and notifications are supported; test the configured behavior rather than assuming a generic educate-only action or automatic agent-identity targeting. Policy updates can take up to four hours.

Capture read-back without a guessed workload filter:

```powershell
Get-DlpCompliancePolicy | ConvertTo-Json -Depth 30 |
    Set-Content (Join-Path $Session.EvidenceRoot 'dlp-policies.json') -Encoding utf8
Get-DlpComplianceRule | ConvertTo-Json -Depth 30 |
    Set-Content (Join-Path $Session.EvidenceRoot 'dlp-rules.json') -Encoding utf8
```

Reconcile these exports with the actual portal location, scope, mode, and separate rule conditions/actions, then execute `1.13-DLP-01..03` in the [verification playbook](verification-testing.md). Exported configuration alone is not enforcement proof. Copilot Studio connectors require separate coverage testing.

## 10. `Test-DataClassification` harness

[`Test-DataClassification`](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/test-dataclassification) tests text with `-TextToClassify` (or documented text-extraction input), not raw document bytes through `-DocumentData`/`-DocumentName`. Use the portal upload test for binary documents and test each production workload separately.

> **Result contract.** Microsoft documents `.ClassificationResults` but does not establish the former harness's `.SensitiveTypeName` projection as a universal schema. Preserve raw results and review the actual sensitive type/count/confidence fields. An empty successful result can be an expected negative; an error or missing envelope is not. The following collector deliberately does not manufacture an automated pass/fail oracle from undocumented fields.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
<#
.SYNOPSIS
    Captures raw classification results and expectations for synthetic text fixtures.
    Human review reconciles identity, count, confidence, positives, and negatives.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] $Session,
    [Parameter(Mandatory)] [string] $FixtureRoot,            # directory containing test files
    [Parameter(Mandatory)] [hashtable] $Expectations         # @{ 'fixture.txt' = @('Contoso-Account-Number') }
)

$ErrorActionPreference = 'Stop'
$report = @()

foreach ($file in (Get-ChildItem $FixtureRoot -File -Filter '*.txt')) {
    if (-not $Expectations.ContainsKey($file.Name)) {
        throw "Missing expectation for $($file.Name)."
    }
    $resp = Test-DataClassification -TextToClassify (Get-Content $file.FullName -Raw) -ErrorAction Stop

    if ($null -eq $resp -or $null -eq $resp.ClassificationResults) {
        throw "Test-DataClassification returned no ClassificationResults for $($file.Name). Aborting (false-clean guard)."
    }

    $expected = @($Expectations[$file.Name])

    $report += [PSCustomObject]@{
        File      = $file.Name
        Expected  = $expected -join ', '
        Outcome   = 'review-required'
        Details   = $resp.ClassificationResults
    }
}

$report | ConvertTo-Json -Depth 6 |
    Set-Content (Join-Path $Session.EvidenceRoot "testclass-$($Session.Stamp).json") -Encoding utf8
$report | Format-Table File, Expected, Outcome -AutoSize
if (-not $report.Count) { throw 'No text fixtures were evaluated.' }
```

**Fixture pack guidance.** Maintain a fixture pack alongside every custom SIT in source control:

- `tp-*.txt` — true positives. Should match the SIT at the documented confidence tier.
- `tn-*.txt` — true negatives (test sentinels, lookalike numbers without keywords). Should *not* match.
- `boundary-*.txt` — edge cases (whitespace, Unicode, leading/trailing punctuation, non-ASCII names) that the SIT is documented to handle.

Run the harness on every CI/CD merge against the SIT rule package and archive the JSON report in the evidence pack.

## 11. Audit and Activity Explorer reconciliation

Capture supported, observed administrative audit activity alongside before/after configuration; do not assume every classifier or EDM operation emits a particular UAL event. The command below is a bounded first page, not a completeness proof. For complete windows, use a fixed session ID with `ReturnLargeSet`, preserve raw records, and split windows at the documented 50,000-result session cap.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
[CmdletBinding()]
param(
    [Parameter(Mandatory)] $Session,
    [int] $LookbackHours = 24
)

$end   = Get-Date
$start = $end.AddHours(-$LookbackHours)

$ops = @(
    'New-DlpSensitiveInformationTypeRulePackage',
    'Set-DlpSensitiveInformationTypeRulePackage',
    'Remove-DlpSensitiveInformationTypeRulePackage',
    'New-DlpSensitiveInformationType',
    'Set-DlpSensitiveInformationType',
    'Remove-DlpSensitiveInformationType',
    'New-DlpKeywordDictionary','Set-DlpKeywordDictionary','Remove-DlpKeywordDictionary',
    'New-DlpEdmSchema','Set-DlpEdmSchema','Remove-DlpEdmSchema',
    'New-DLPCompliancePolicy','Set-DLPCompliancePolicy','Remove-DLPCompliancePolicy',
    'New-DlpComplianceRule','Set-DlpComplianceRule','Remove-DlpComplianceRule'
)

$events = Search-UnifiedAuditLog -StartDate $start -EndDate $end -Operations $ops -ResultSize 5000

$events |
    Select-Object CreationDate, UserIds, Operations,
                  @{n='Target'; e={ ($_.AuditData | ConvertFrom-Json).ObjectId }},
                  AuditData |
    ConvertTo-Json -Depth 6 |
    Set-Content (Join-Path $Session.EvidenceRoot "audit-$($Session.Stamp).json") -Encoding utf8

Write-Information "$($events.Count) audit events captured for the last $LookbackHours h." -InformationAction Continue
```

For supported runtime activities, use the portal or [`Export-ActivityExplorerData`](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/export-activityexplorerdata). It covers up to 30 days and uses `LastPage`, `Watermark`, and `PageCookie` paging (maximum page size 5,000; cookie valid 120 seconds). Preserve each page; fields differ by activity. Do not assume a generic Graph Activity Explorer API or a one-to-one join with CopilotInteraction.

> Send the audit + Activity Explorer JSON exports into your SIEM (Microsoft Sentinel for tenants on the FSI baseline) so anomaly detection — for example, an after-hours `Remove-DlpComplianceRule` against a Copilot policy — fires automatically. The AI incident-response playbook (`docs/playbooks/incident-and-risk/ai-incident-response-playbook.md`) is the standing on-call runbook.

## 12. Idempotency, drift detection, and rollback

### 12.1 Idempotency pattern

Every mutating script in this playbook follows the same shape:

1. `Get-*` to capture a **before-snapshot** to JSON.
2. If the object exists, `Set-*`; otherwise `New-*`.
3. `Get-*` again to capture an **after-snapshot**.
4. Diff before/after into a delta JSON for the change-record.

This is an upsert pattern, not a guaranteed no-op: compare actual definitions before calling setters and verify read-back. Some setters still mutate timestamps/state with identical inputs.

### 12.2 Drift detection

```powershell
# Daily drift detection: compare today's inventory to yesterday's baseline.
$today    = Get-Content (Join-Path $Session.EvidenceRoot "inventory-$($Session.Stamp)\sits.json") | ConvertFrom-Json
$yesterday= Get-Content $LastKnownGoodPath | ConvertFrom-Json

$diff = Compare-Object $yesterday $today -Property Name, RulePackId, State -PassThru
if ($diff) {
    $diff | ConvertTo-Json -Depth 6 |
        Set-Content (Join-Path $Session.EvidenceRoot "drift-$($Session.Stamp).json") -Encoding utf8
    Write-Warning "Drift detected: $($diff.Count) SIT objects changed since last known good."
}
```

### 12.3 Rollback dependency graph

Removal order matters. Attempting to remove an object while a dependent still references it returns an opaque `…is in use…` error.

```
DLP rule  ──binds──▶  SIT  ──packaged in──▶  Rule package
                       ▲
                       └──binds──▶  EDM schema  ──holds──▶  Hash data store
                       └──binds──▶  Keyword dictionary
```

To remove cleanly:

| Object class | Remove first | Then |

| Rule package | All `DlpComplianceRule`s referencing any SIT in the pack | `Remove-DlpSensitiveInformationTypeRulePackage` |
| Document fingerprint SIT | All rules referencing it | `Remove-DlpSensitiveInformationType` |
| Keyword dictionary | All rules and rule-pack `<Match>` references | `Remove-DlpKeywordDictionary` |
| EDM schema | Remove dependent EDM SITs through the supported workflow | `Remove-DlpEdmSchema`; associated data store is deleted within 24 hours |
| DLP policy | All child `DlpComplianceRule`s | `Remove-DLPCompliancePolicy` |
| Trainable classifier | Rules that reference its identity | Portal removal (cmdlet surface unstable) |

A pre-canned rollback for every change record means: archived before-snapshot JSON + the exact `Set-` / `Remove-` invocation that restores it. Treat rollback scripts as production code — code-review them, version them, store them next to the change record.


## 13. Anti-patterns

The following patterns appear in the wild and have all caused production incidents in FSI tenants. None of them is acceptable in a Control 1.13 runbook.

| # | Anti-pattern | Why it fails | Correct pattern |

| 1 | Guessing a flat classification result schema | Null projections can create false-clean evidence. | Preserve `$result.ClassificationResults`, inspect actual fields, and review positives and negatives. |
| 2 | UTF-8 encoding for `New-DlpKeywordDictionary -FileData` | The cmdlet requires UTF-16 (Unicode). UTF-8 yields a corrupt or empty dictionary; non-ASCII names ("Société Générale") silently disappear. | `[System.Text.Encoding]::Unicode.GetBytes(...)` with `\r\n` line terminators. |
| 3 | `<Regex>` or `<Keyword>` placed inside `<Entity>` instead of as siblings inside `<Rules>` | Schema rejects the rule package with an opaque error. | Definitions are siblings of `<Entity>` inside `<Rules>`; `<Entity>` references them via `<IdMatch idRef="…">` / `<Match idRef="…">`. |
| 4 | Calling `Disconnect-IPPSSession` | The cmdlet does not exist; raises `CommandNotFoundException` and may leave you connected. | Call `Disconnect-ExchangeOnline -Confirm:$false` for both EXO and IPPS REST sessions. |
| 5 | Creating an EDM schema and treating the SIT as live | Schema existence is not upload/indexing proof. | Capture `/GetDataStore`, `/GetSession`, then direct EDM detection after the documented readiness window. |
| 6 | Identifying built-in SITs by display name in scripts | Built-in SIT display names are localised and have changed between releases. | Use the immutable GUID from `Get-DlpSensitiveInformationType -Identity <guid>`. |
| 7 | Filtering rule packages by `Publisher` string | Publisher strings have varied across Microsoft releases ("Microsoft Corporation" vs "Microsoft"). Brittle. | Filter on `Publisher` GUID, or just enumerate all and treat the result as the source of truth. |
| 8 | Inlining `$(New-Guid)` inside a SIT rule package XML heredoc | Every script run produces a different SIT, which breaks DLP rule bindings, history, and rollback. | Generate GUIDs once at design time, paste as constants, and treat as immutable. |
| 9 | Using unverified Copilot DLP provisioning payloads | A plausible parameter/payload is not a supported procedure. | Use §9's documented portal authoring and separate prompt/label tests. |
| 10 | Turning processing guidance into an SLA | Readiness differs by service and existing-file classification. | Use the documented EDM test-readiness and classifier lifecycle guidance, recording actual observations. |
| 11 | Hard-coded `admin@contoso.com` in a runbook | Operator identity ends up in the audit log as the wrong principal. | `param([Parameter(Mandatory)] [string] $AdminUpn)`. |
| 12 | `Write-Host` inside a function | Bypasses the information stream; cannot be redirected to the transcript or evidence pack cleanly. | `Write-Information … -InformationAction Continue` for narration, `Write-Verbose` for diagnostics. |
| 13 | Copying `-ResultSize Unlimited` across unrelated cmdlets | SIT inventory does not document it; UAL accepts an integer maximum of 5,000 per call. | Verify each cmdlet's syntax and paging, then prove completeness. |
| 14 | Untested sentinel exclusions | Attackers can copy sentinels to suppress real detection; `<ExcludedMatch>` is not the documented syntax. | Validate an approved negative-evidence design with adversarial positives and negatives. |

## 14. Evidence pack and `Write-FsiEvidence`

Every change window produces an evidence pack containing the transcript, the before/after JSON snapshots, audit-log exports, `Test-DataClassification` reports, and a SHA-256 manifest binding them together. The shared baseline (`docs/playbooks/_shared/powershell-baseline.md` §4) defines the helper:

```powershell
function Write-FsiEvidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $EvidenceDir,
        [Parameter(Mandatory)] [string] $ControlId,
        [Parameter(Mandatory)] [string] $ChangeRef     # change ticket ID
    )

    if (-not (Test-Path $EvidenceDir)) { throw "Evidence dir not found: $EvidenceDir" }

    $manifestPath = Join-Path (Resolve-Path $EvidenceDir).Path 'manifest.json'
    $manifest = @(Get-ChildItem $EvidenceDir -File -Recurse |
        Where-Object FullName -ne $manifestPath | ForEach-Object {
        [PSCustomObject]@{
            RelativePath = (Resolve-Path $_.FullName -Relative)
            SHA256       = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
            Bytes        = $_.Length
            ModifiedUtc  = $_.LastWriteTimeUtc
        }
    })

    $envelope = [PSCustomObject]@{
        ControlId     = $ControlId
        ChangeRef     = $ChangeRef
        GeneratedUtc  = (Get-Date).ToUniversalTime()
        TenantId      = (Get-MgContext).TenantId
        Operator      = (Get-MgContext).Account
        FileCount     = $manifest.Count
        Files         = $manifest
    }

    $envelope | ConvertTo-Json -Depth 6 |
        Set-Content (Join-Path $EvidenceDir 'manifest.json') -Encoding utf8

    Write-Information "Evidence manifest written: $EvidenceDir\manifest.json (Control $ControlId / change $ChangeRef)" -InformationAction Continue
}
```

Call `Write-FsiEvidence` as the **last** step of every mutating runbook, after `Stop-Transcript`. The `manifest.json` is what supervisory testing and external audit reviewers consume; everything else in the evidence pack is the supporting record.

**Retention.** Evidence packs supporting Control 1.13 changes are subject to FINRA Rule 4511 / SEC Rule 17a-4 books-and-records retention (six years, first two readily accessible) and SOX §404 audit-trail expectations. Store them in a WORM-enabled location (Purview Records Management with a regulatory record label, or an Azure Storage immutability policy) and replicate to the firm's evidence vault.

## 10a. Disconnect

```powershell
# Correct disconnect — works for both EXO and IPPS REST sessions established
# through ExchangeOnlineManagement v3.x.
Disconnect-ExchangeOnline -Confirm:$false
Disconnect-MgGraph -ErrorAction SilentlyContinue
Stop-Transcript
```

`Disconnect-IPPSSession` is a frequently-imagined cmdlet that does not exist. Calling it raises `CommandNotFoundException` and — because `Disconnect-ExchangeOnline` was never called — leaves the IPPS REST session live until token expiry. In a shared jump-host environment this can leak credentials between operators.

## 15. Cross-links

- [Control 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — consuming policies and label bindings.
- [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — posture and activity evidence.
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — audit collection and retention.
- [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) — Customer Lockbox and data-residency posture.
- **Control 4.6 — SharePoint grounding scope governance.** SIT-based DLP rules complement scope governance for what an agent can ground on. `docs/controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- **AI Incident Response Playbook.** Standing on-call runbook for SIT/DLP alerts that fire against agent traffic. `docs/playbooks/incident-and-risk/ai-incident-response-playbook.md`
- **Shared PowerShell baseline.** Module pinning, transcript and evidence helpers. `docs/playbooks/_shared/powershell-baseline.md`

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review — documentation verified; tenant UI not tested*
