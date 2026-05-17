# Control 1.13 — PowerShell Setup: Sensitive Information Types and Pattern Recognition

> **Scope.** This playbook is the canonical PowerShell automation reference for Control 1.13 — *Sensitive Information Types (SITs) and Pattern Recognition*. It covers the six Microsoft Purview detection paths (built-in SITs, custom pattern SITs, named entities, trainable classifiers, Exact Data Match (EDM), and keyword dictionaries) as they apply to AI-agent governance for US financial-services tenants in the Microsoft Commercial, GCC, GCC High, and DoD clouds.
>
> **Companion documents.**
>
> - Control specification — `docs/controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`
> - Portal walkthrough — `./portal-walkthrough.md`
> - Verification & testing — `./verification-testing.md`
> - Troubleshooting — `./troubleshooting.md`
> - Shared baseline — `docs/playbooks/_shared/powershell-baseline.md`
>
> **Important regulatory framing.** Nothing in this playbook *guarantees* regulatory compliance. The cmdlets, scripts, and patterns below *support* control objectives required by FINRA Rules 4511 and 25-07, SEC Rules 17a-3 / 17a-4 and Reg S-P, GLBA §501(b), SOX §404, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), and Federal Reserve SR 26-2 (formerly SR 11-7). Implementation requires that organizations validate every script against their own change-management, model-risk, and supervisory-review processes before production rollout.

## 0. Wrong-shell trap (READ FIRST)

Control 1.13 has *three* PowerShell surfaces that look interchangeable and are not. Choosing the wrong one is the single most common failure mode and produces silent false-clean evidence.

| Surface | Connect cmdlet | Module | Purpose | Typical 1.13 use |
|---|---|---|---|---|
| **Security & Compliance PowerShell (IPPS)** | `Connect-IPPSSession` | `ExchangeOnlineManagement` v3.5+ | Purview / DLP / SIT / EDM / dictionaries / classifiers | **Almost everything in this playbook** |
| **Exchange Online (EXO)** | `Connect-ExchangeOnline` | `ExchangeOnlineManagement` v3.5+ | Mail-flow, transport rules, mailbox audit | Cross-checks against §11 reconciliation only |
| **Microsoft Graph PowerShell** | `Connect-MgGraph` | `Microsoft.Graph` v2.x | Directory, role, license, audit-log read | Pre-flight licence and role checks (§1) |

> **There is no separate `IPPSSession` module.** `Connect-IPPSSession` ships inside `ExchangeOnlineManagement`. Installing a non-existent `IPPSSession` module is a recurring anti-pattern and will fail silently because PowerShell's package providers will simply return zero results. Pin the *Exchange* module and you have IPPS.

> **Disconnect note.** Use `Disconnect-ExchangeOnline` for **both** EXO and IPPS REST sessions. The cmdlet `Disconnect-IPPSSession` *does not exist* — invoking it produces `CommandNotFoundException` and may leave you connected. See §10a.

### PowerShell edition guard

`ExchangeOnlineManagement` v3.5 supports both Windows PowerShell 5.1 and PowerShell 7.2+. SCC REST cmdlets (the ones returning `*Compliance*`, `*Dlp*`, `*Classifier*`, `*Edm*`, `*SensitiveInformation*`) are REST-based and therefore work on both editions, but several legacy cmdlets still rely on WinRM remoting and only work in 5.1. Standardise on PowerShell 7.4 LTS for new automation and add an explicit edition guard at the top of every script:

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }

if ($PSVersionTable.PSEdition -ne 'Core') {
    throw "This script targets PowerShell 7+. Current edition: $($PSVersionTable.PSEdition)."
}
```

If a script must run under Windows PowerShell 5.1 (for example because it calls the EDM upload agent on a hardened jump host), state it explicitly: `#Requires -Version 5.1` and document the reason in the file header.

## 1. Pre-flight: session bootstrap, role and licence checks

Every Control 1.13 script begins with the same five preconditions: PowerShell edition pinned, module version pinned, sovereign endpoint resolved, IPPS session opened with banner suppression, and admin role + licence verified through Microsoft Graph. Bundle them once into a reusable `Initialize-Agt113Session` helper so individual scripts do not drift.

### 1.1 The session bootstrap helper

Save as `Initialize-Agt113Session.ps1` in your shared automation library:

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Authentication'; RequiredVersion = '2.15.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Identity.DirectoryManagement'; RequiredVersion = '2.15.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Users';            RequiredVersion = '2.15.0' }

<#
.SYNOPSIS
    Bootstraps a Control 1.13 admin session: opens IPPS + Graph in the correct
    sovereign cloud, verifies role assignment and SKU entitlement, and starts a
    timestamped transcript for evidence collection.
.PARAMETER AdminUpn
    UPN of the admin executing the change. Used for role-assignment lookup.
.PARAMETER Cloud
    One of: Commercial, GCC, GCCHigh, DoD. Selects ConnectionUri/AuthorityUri.
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
        [Parameter(Mandatory)] [string]   $AdminUpn,
        [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud,
        [Parameter(Mandatory)] [string]   $EvidenceRoot,
        [string[]] $RequiredRoles = @(
            'Compliance Administrator',
            'Compliance Data Administrator',
            'Information Protection Administrator'
        ),
        [string[]] $RequiredSkuPartNumbers = @('SPE_E5')
    )

    # 1. Resolve sovereign endpoints (see §11 for the full matrix).
    $endpoints = switch ($Cloud) {
        'Commercial' { @{ IPPSConnectionUri = $null; IPPSAuthorityUri = $null;
                          GraphEnvironment  = 'Global' } }
        'GCC'        { @{ IPPSConnectionUri = $null; IPPSAuthorityUri = $null;
                          GraphEnvironment  = 'Global' } }
        'GCCHigh'    { @{ IPPSConnectionUri = 'https://ps.compliance.protection.office365.us/powershell-liveid/';
                          IPPSAuthorityUri  = 'https://login.microsoftonline.us/organizations';
                          GraphEnvironment  = 'USGov' } }
        'DoD'        { @{ IPPSConnectionUri = 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/';
                          IPPSAuthorityUri  = 'https://login.microsoftonline.us/organizations';
                          GraphEnvironment  = 'USGovDoD' } }
    }

    # 2. Evidence root + transcript.
    if (-not (Test-Path $EvidenceRoot)) {
        New-Item -ItemType Directory -Path $EvidenceRoot -Force | Out-Null
    }
    $stamp        = Get-Date -Format 'yyyyMMdd-HHmmss'
    $transcript   = Join-Path $EvidenceRoot "agt113-$stamp.transcript.log"
    Start-Transcript -Path $transcript -IncludeInvocationHeader | Out-Null
    Write-Information "Transcript: $transcript" -InformationAction Continue

    # 3. Connect-IPPSSession (banner suppressed, sovereign-aware).
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

    # 5. Role check via Graph (avoids reliance on the RBAC role group cmdlets).
    $me   = Get-MgUser -UserId $AdminUpn -ErrorAction Stop
    $assigns = Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '$($me.Id)'" -ExpandProperty RoleDefinition
    $held = $assigns.RoleDefinition.DisplayName | Sort-Object -Unique
    $hit  = $held | Where-Object { $RequiredRoles -contains $_ }
    if (-not $hit) {
        throw "Operator $AdminUpn does not hold any of the required roles: $($RequiredRoles -join ', '). Held: $($held -join ', ')."
    }
    Write-Information "Role check OK. Operator holds: $($hit -join ', ')" -InformationAction Continue

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
|---|---|---|
| Read SIT / dictionary / classifier inventory | Compliance Data Administrator | Read-only; preferred for inventory scripts |
| Author or modify SITs, dictionaries, EDM schemas | Compliance Administrator **or** Information Protection Administrator | Use Information Protection Administrator where the tenant has split duties |
| Author DLP policies that bind SITs to Copilot / Exchange / SharePoint workloads | Compliance Administrator | Policy cmdlets enforce this server-side |
| EDM `EdmUploadAgent.exe` data upload | Compliance Administrator + on-host membership of `EDM_DataUploaders` security group | Group membership is enforced by the agent, not by IPPS |
| Trainable classifier publish | Compliance Administrator + tenant-level FSI governance gate sign-off (§8) | Model-risk governance is procedural, not technical |

Use the canonical short role names (`Purview Compliance Admin`, `Purview Compliance Data Admin`, `Information Protection Admin`) when documenting evidence. The Graph display names (`Compliance Administrator`, etc.) are what the API returns and what the helper above checks.

### 1.3 Module pinning

Pin to a known-good version of `ExchangeOnlineManagement` and refuse to run against newer/older builds without explicit override. The shared baseline (`docs/playbooks/_shared/powershell-baseline.md` §1) describes the rationale.

```powershell
$wantModule  = 'ExchangeOnlineManagement'
$wantVersion = [version]'3.5.0'
$mod = Get-Module -ListAvailable -Name $wantModule |
       Where-Object { $_.Version -ge $wantVersion } |
       Sort-Object Version -Descending | Select-Object -First 1
if (-not $mod) {
    throw "Required module $wantModule >= $wantVersion not installed. Run: Install-Module $wantModule -RequiredVersion $wantVersion -Scope CurrentUser -Force"
}
Import-Module $mod.Path -Force
```

## 2. Coverage boundary: PowerShell vs portal vs Maker

PowerShell is authoritative for inventory, idempotent rollout, drift detection, rollback, and evidence. It is *not* authoritative for everything. Be explicit with operators about which tasks must be done where.

| Task | PowerShell | Purview portal | Maker (Power Platform / Copilot Studio) |
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
#Requires -Version 7.2
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
$sits = Get-DlpSensitiveInformationType -ResultSize Unlimited |
        Select-Object Name, Publisher, Type, RulePackId, State, Description,
                      RecommendedConfidence, @{n='LastModified'; e={$_.WhenChangedUTC}}
$sits | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $out 'sits.json')      -Encoding utf8
$sits | Export-Csv      -NoTypeInformation -Path (Join-Path $out 'sits.csv')

# 2. SIT rule packages (XML container — one pack may carry many SITs).
$packs = Get-DlpSensitiveInformationTypeRulePackage |
         Select-Object Name, Publisher, Version, State, WhenChangedUTC,
                       @{n='RulePackXmlSize'; e={ ($_.RulePackXml | Measure-Object Length -Sum).Sum }}
$packs | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $out 'sit-rule-packages.json') -Encoding utf8
foreach ($p in (Get-DlpSensitiveInformationTypeRulePackage)) {
    $safe = ($p.Name -replace '[^\w\-]','_')
    Set-Content -Path (Join-Path $out "rulepack-$safe.xml") -Value $p.RulePackXml -Encoding utf8
}

# 3. Keyword dictionaries.
$dicts = Get-DlpKeywordDictionary |
         Select-Object Name, Description, Identity, KeywordCount,
                       @{n='LastModified'; e={$_.WhenChangedUTC}}
$dicts | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $out 'dictionaries.json') -Encoding utf8

# 4. EDM schemas.
$edm = Get-DlpEdmSchema |
       Select-Object Name, Description, State, DataStoreName,
                     @{n='ColumnCount'; e={ ($_.Schema.EdmSchemaXml -split '<Field ' ).Count - 1 }},
                     WhenChangedUTC
$edm | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $out 'edm.json') -Encoding utf8

# 5. Trainable classifiers — hedge: cmdlet surface still moving. Verify name on Learn.
try {
    $cls = Get-Classifier -ErrorAction Stop |
           Select-Object Name, Description, Mode, PublishDate, WhenChangedUTC
} catch [System.Management.Automation.CommandNotFoundException] {
    Write-Warning "Get-Classifier not present in this module build. Skipping classifier inventory."
    $cls = @()
}
$cls | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $out 'classifiers.json') -Encoding utf8

# 6. DLP policies + rules that reference SITs (consumption side).
$pols  = Get-DlpCompliancePolicy  | Select-Object Name, Mode, Enabled, EnforcementPlanes, CreatedBy, WhenChangedUTC
$rules = Get-DlpComplianceRule    | Select-Object Name, ParentPolicyName, Disabled, ContentContainsSensitiveInformation, AdvancedRule, WhenChangedUTC
$pols  | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $out 'dlp-policies.json') -Encoding utf8
$rules | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $out 'dlp-rules.json')    -Encoding utf8

# 7. SHA-256 manifest (see §15).
Get-ChildItem $out -File | ForEach-Object {
    [PSCustomObject]@{
        File   = $_.Name
        SHA256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        Bytes  = $_.Length
    }
} | ConvertTo-Json -Depth 3 | Set-Content (Join-Path $out 'manifest.json') -Encoding utf8

Write-Information "Inventory written to $out" -InformationAction Continue
```

**Why `-ResultSize Unlimited`.** Without it the SCC cmdlets cap returns at 1,000 objects and the inventory silently truncates. A truncated inventory is the most common cause of "phantom drift" in §12 reconciliation.

## 4. Keyword dictionaries: `New-FsiKeywordDictionary.ps1`

Keyword dictionaries back named-counterparty lists (broker-dealer panels, restricted-list issuers, MNPI deal codenames). The single most common implementation bug is **encoding the term file as UTF-8**. The `-FileData` parameter requires a **UTF-16 (Unicode) byte array** with `\r\n` line terminators. UTF-8 input parses to a corrupt or empty dictionary and silently fails on accented terms (e.g., "Société Générale", "Crédit Agricole", "Banco Bilbao Vizcaya Argentaria").

```powershell
#Requires -Version 7.2
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
$existing = Get-DlpKeywordDictionary -Identity $Name -ErrorAction SilentlyContinue
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
$after = Get-DlpKeywordDictionary -Identity $Name
$afterPath = Join-Path $Session.EvidenceRoot ("dict-$Name-after-$($Session.Stamp).json")
$after | ConvertTo-Json -Depth 6 | Set-Content $afterPath -Encoding utf8

Write-Information ("Dictionary '{0}' now contains {1} terms." -f $Name, $after.KeywordCount) -InformationAction Continue
```

**Operational notes.**

- The dictionary `Identity` *is* the display name, so renaming a dictionary breaks every DLP rule that references it. Treat the name as immutable once published.
- Keyword dictionaries support up to ~100,000 terms and ~1 MB compressed; verify the current limit on Microsoft Learn before bulk-loading restricted lists. If the list approaches the cap, consider splitting by asset class (`FSI-Restricted-Issuers-Equities`, `FSI-Restricted-Issuers-Credit`) so individual rules can target only the dictionaries they need.
- Reference a dictionary inside a custom SIT XML rule package via `<Match idRef="Keyword_Dictionary_GUID" />` where the GUID is `(Get-DlpKeywordDictionary -Identity $Name).Identity`.

## 5. Custom pattern SIT rule package: `New-FsiCustomSitPack.ps1`

This is the highest-leverage and highest-risk operation in 1.13. A *rule package* is an XML container that may publish one or many SITs. The cmdlets are:

| Operation | Cmdlet | Notes |
|---|---|---|
| Create rule package | `New-DlpSensitiveInformationTypeRulePackage -FileData $bytes` | XML must be UTF-8 byte array |
| Update rule package | `Set-DlpSensitiveInformationTypeRulePackage -Identity <Name> -FileData $bytes` | Bump `RulePack/Version` first |
| Remove rule package | `Remove-DlpSensitiveInformationTypeRulePackage -Identity <Name>` | Will fail while any DLP rule binds a SIT it defines |

> **Do not confuse `New-DlpSensitiveInformationType` with `New-DlpSensitiveInformationTypeRulePackage`.** The former is the *document fingerprint* cmdlet (§6) and demands a mandatory `-Fingerprints` parameter. Custom *pattern* SITs (regex, keyword, dictionary, function calls) **only** ship through rule packages.

### 5.1 Schema rules that the validator enforces

The XML schema is unforgiving. The most common failures, all of which return cryptic `Invalid sensitive information type rule package` errors:

1. **`<Regex>` and `<Keyword>` definitions must live inside `<Rules>`.** They are not children of `<Entity>`. The `<Entity>` block uses `<Pattern>` → `<IdMatch idRef="…" />` / `<Match idRef="…" />` to *reference* regex/keyword definitions that live as siblings later in `<Rules>`.
2. **`<Version>` is on `<RulePack>` (the inner element), not `<RulePackage>`.** Bump it on every change or the upload will silently keep the previous body.
3. **Every entity, regex, and keyword needs a stable GUID.** Generate them once and treat them as immutable. Inlining `$(New-Guid)` in the heredoc is a recurring bug — every script run produces a different SIT.
4. **Confidence levels (60 / 75 / 85) are tied to `<Pattern confidenceLevel="…">` blocks.** Use three patterns of decreasing strictness so DLP rules can choose a tier.
5. **`<LocalizedStrings>` is mandatory** and must list each entity by GUID. Missing entries silently truncate the SIT picker in the portal.

### 5.2 Worked example — Contoso 9-digit account number with Luhn validation

The example below publishes a single SIT named `Contoso-Account-Number` that:

- Matches a 9-digit Contoso account number using `Func_luhn_check` for checksum validation.
- Increases confidence when nearby keywords appear (`account`, `acct`, `client id`).
- Boosts confidence further in MNPI contexts (`merger`, `acquisition`, `material non-public`).
- **Excludes** known test-data sentinels (`TEST-`, `SAMPLE-`, `XXX-`) so SDLC pipelines do not generate false positives.
- Emits at three confidence tiers (60 / 75 / 85) for downstream DLP tier selection.

Save the XML as a here-string in your script — but generate GUIDs **once**, externally, and paste them in:

```powershell
#Requires -Version 7.2
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
<RulePackage xmlns="http://schemas.microsoft.com/office/2018/09/contentclassification">
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

      <!-- Tier 3 (85) : account number + Luhn + (acct keywords OR MNPI keywords) and NOT test sentinels -->
      <Pattern confidenceLevel="85">
        <IdMatch idRef="Regex_Contoso_Account" />
        <Match idRef="Func_luhn_check" />
        <Any minMatches="1">
          <Match idRef="Keyword_Contoso_Account" />
          <Match idRef="Keyword_Contoso_MNPI" />
        </Any>
        <ExcludedMatch idRef="Keyword_Contoso_Test" />
      </Pattern>

      <!-- Tier 2 (75) : account number + Luhn + acct keywords -->
      <Pattern confidenceLevel="75">
        <IdMatch idRef="Regex_Contoso_Account" />
        <Match idRef="Func_luhn_check" />
        <Match idRef="Keyword_Contoso_Account" />
        <ExcludedMatch idRef="Keyword_Contoso_Test" />
      </Pattern>

      <!-- Tier 1 (60) : account number + Luhn (no keyword corroboration) -->
      <Pattern confidenceLevel="60">
        <IdMatch idRef="Regex_Contoso_Account" />
        <Match idRef="Func_luhn_check" />
        <ExcludedMatch idRef="Keyword_Contoso_Test" />
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
        <Description default="true" langcode="en-us">9-digit Contoso account number, Luhn-validated, with keyword corroboration. Excludes test-data sentinels.</Description>
      </Resource>
    </LocalizedStrings>
  </Rules>
</RulePackage>
"@

# Encode XML as UTF-8 byte array (NOT UTF-16 — the XML *prologue* says UTF-16 but the
# rule-pack upload pipeline expects the file body as bytes and re-parses; the standard
# practice is UTF-8 here. If you change the prologue to UTF-8, keep encoding aligned.)
$bytes = [System.Text.Encoding]::Unicode.GetBytes($xml)

# Before-snapshot.
$existing = Get-DlpSensitiveInformationTypeRulePackage -Identity $RulePackName -ErrorAction SilentlyContinue
$beforePath = Join-Path $Session.EvidenceRoot ("sitpack-$RulePackName-before-$($Session.Stamp).xml")
if ($existing) { Set-Content $beforePath $existing.RulePackXml -Encoding utf8 }

if ($existing) {
    if ($PSCmdlet.ShouldProcess($RulePackName, 'Set-DlpSensitiveInformationTypeRulePackage')) {
        Set-DlpSensitiveInformationTypeRulePackage -Identity $RulePackName -FileData $bytes
    }
} else {
    if ($PSCmdlet.ShouldProcess($RulePackName, 'New-DlpSensitiveInformationTypeRulePackage')) {
        New-DlpSensitiveInformationTypeRulePackage -FileData $bytes | Out-Null
    }
}

# After-snapshot.
$after = Get-DlpSensitiveInformationTypeRulePackage -Identity $RulePackName
Set-Content (Join-Path $Session.EvidenceRoot "sitpack-$RulePackName-after-$($Session.Stamp).xml") $after.RulePackXml -Encoding utf8

Write-Information "Rule package '$RulePackName' published version $RulePackVersion." -InformationAction Continue
```

> **Promote test-data sentinels everywhere.** Every custom SIT a US FSI tenant publishes should carry `<ExcludedMatch>` entries for `TEST-`, `SAMPLE-`, and a tenant-specific UAT prefix. Without them, the *first* failure mode at rollout is an avalanche of false positives from synthetic data in pre-production environments — which trains operators to ignore SIT alerts, defeating Control 1.13's purpose.

## 6. Document fingerprint SITs: `Add-FsiDocumentFingerprintSit.ps1`

Document fingerprinting builds a SIT from the *structural pattern* of a template document — for example, a board-deck template, a credit-memo skeleton, or a Form ADV. The cmdlet is `New-DlpSensitiveInformationType` (singular, no `RulePackage`) and demands `-Fingerprints` as a byte array of one or more template files.

```powershell
#Requires -Version 7.2
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

# 1. Load every template file as bytes.
$prints = foreach ($p in $TemplatePaths) {
    if (-not (Test-Path $p)) { throw "Template not found: $p" }
    [System.IO.File]::ReadAllBytes((Resolve-Path $p))
}

# 2. Idempotent upsert.
$existing = Get-DlpSensitiveInformationType -Identity $Name -ErrorAction SilentlyContinue
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

- Document fingerprints match on the *invariant* skeleton of a template (boilerplate, table structure, headings). They are noisy when the template is sparse and miss when end users restructure documents heavily. Validate every fingerprint with `Test-DataClassification` (§10) against both true-positive and known-good documents before binding into a DLP rule.
- A single fingerprint SIT can carry *multiple* template files — pass them all in the same `-Fingerprints` array so the SIT votes the union of patterns.
- Fingerprint SITs do not support per-tier confidence; bind them at `recommendedConfidence` only.

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

# Schema XML example: searchable=AccountNumber,SSN; non-searchable but returnable=FullName,Email.
# Keep ≤ ~32 searchable columns — verify the current cap on Microsoft Learn before authoring.
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $SchemaXmlPath))

$existing = Get-DlpEdmSchema -Identity $SchemaName -ErrorAction SilentlyContinue
if ($existing) {
    if ($PSCmdlet.ShouldProcess($SchemaName, 'Set-DlpEdmSchema')) {
        Set-DlpEdmSchema -Identity $SchemaName -FileData $bytes
    }
} else {
    if ($PSCmdlet.ShouldProcess($SchemaName, 'New-DlpEdmSchema')) {
        New-DlpEdmSchema -FileData $bytes -DataStoreName $DataStoreName | Out-Null
    }
}

$after = Get-DlpEdmSchema -Identity $SchemaName
$after | ConvertTo-Json -Depth 8 |
    Set-Content (Join-Path $Session.EvidenceRoot "edm-$SchemaName-$($Session.Stamp).json") -Encoding utf8

Write-Information "EDM schema '$SchemaName' state: $($after.State). Data store: $($after.DataStoreName)." -InformationAction Continue
```

### 7.2 Data upload (`EdmUploadAgent.exe`)

`EdmUploadAgent.exe` is a separate Windows utility, not a PowerShell module. Microsoft ships **three** installer packages: Commercial+GCC, GCC High, and DoD. They differ only in the embedded service endpoint URLs, which can also be overridden in `EdmUploadAgent.exe.config` for sovereign tenants. Install only the package matching your cloud.

| Step | Subcommand | Purpose |
|---|---|---|
| 1 | `EdmUploadAgent.exe /ValidateData /DataFile <csv> /Schema <schema.xml>` | Confirms CSV column count + types match schema |
| 2 | `EdmUploadAgent.exe /Authorize /TenantId <guid>` | Interactive AAD login; persists refresh token for the agent service identity |
| 3 | `EdmUploadAgent.exe /CreateHash /DataFile <csv> /Schema <schema.xml> /OutputDir <dir>` | Salts and one-way hashes data locally — cleartext stays on host |
| 4 | `EdmUploadAgent.exe /UploadHash /DataStoreName <name> /HashFile <hash>` | Uploads hash store to Purview |
| 5 | `EdmUploadAgent.exe /SaveSchedule /DataStoreName <name> ...` | Optional: scheduled refresh from a watched directory |
| 6 | `EdmUploadAgent.exe /GetDataStore /DataStoreName <name>` | Read-back: confirms row counts, last refresh timestamp |
| 7 | `EdmUploadAgent.exe /RemoveDataStore /DataStoreName <name>` | Removes hash store; required *before* `Remove-DlpEdmSchema` |

Verify upload completion in PowerShell:

```powershell
$schema = Get-DlpEdmSchema -Identity $SchemaName
if ($schema.State -ne 'Active') {
    Write-Warning "Schema '$SchemaName' state is '$($schema.State)'. Hash upload may still be in progress."
}
```

### 7.3 Caveats

- **Searchable column cap.** The schema imposes a hard cap on the number of *searchable* columns (currently in the low-30s; verify against current Microsoft Learn before authoring). Plan the schema so the most selective column (`SSN`, `AccountNumber`) is searchable and the rest are returned only as evidence.
- **Refresh cadence and indexing latency.** Microsoft does not publish a hard SLA for indexing latency between hash upload and DLP detection availability. Do **not** invent one in operational documentation. Plan changes around an empirical 24–48 hour validation window.
- **Hash store data residency.** The cleartext source file never leaves the upload host. Treat the upload host itself as a high-value system: tier-0 admin model, mailbox-less service identity, no inbound SMB, audit-logged file mounts, and a documented destruction process for the source CSV after upload.
- **Removal order.** `Remove-DlpEdmSchema` will fail while a data store is bound. Always run `EdmUploadAgent.exe /RemoveDataStore` first, then remove the schema.

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

### 8.2 Cmdlet surface — verify before each change window

Microsoft has renamed the trainable-classifier cmdlet surface several times (variants seen include `*-MLClassifier`, `*-Classifier`, and the portal-only `*-TrainableClassifier`). **Do not hard-code the cmdlet name in production runbooks.** Instead:

```powershell
$candidates = @('Get-Classifier','Get-MLClassifier','Get-TrainableClassifier')
$cmd = $candidates | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
if (-not $cmd) {
    throw "No trainable classifier cmdlet present in this module build. Verify Microsoft Learn and update the runbook."
}
$classifiers = & $cmd
```

For *publishing* a trainable classifier into operational use, **the portal is the supported path**. The PowerShell surface today is best treated as inventory + delete + audit, not authoring. Reference Microsoft Learn for the current article: *Learn about trainable classifiers* and *Get started with trainable classifiers*.

### 8.3 Evidence

Capture, at every change window:

- The classifier list (`& $cmd | ConvertTo-Json -Depth 4`).
- The DLP rule(s) that bind each classifier (filter `Get-DlpComplianceRule` for `AdvancedRule` strings containing the classifier identity).
- A copy of the model-risk validation report PDF and its SHA-256, written into the evidence pack alongside the technical artefacts.

## 9. DLP for Microsoft 365 Copilot: `New-FsiCopilotDlpPolicy.ps1`

A SIT only protects an agent if a DLP policy *binds* it to the Copilot workload. The pattern below mirrors the Microsoft Learn "DLP policy for Copilot" example exactly: workload location is `Applications`, identity is the Copilot location GUID, enforcement plane is `CopilotExperiences`, and the SIT binding is provided as an **AdvancedRule JSON document** to support per-tier confidence and minimum-count tuning.

> **There is no `-CopilotConfiguration` parameter.** If you see one in older runbooks, delete it — it never shipped. The location array + `EnforcementPlanes` + `AdvancedRule` are the supported surface.

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] $Session,
    [Parameter(Mandatory)] [string] $PolicyName     = 'FSI-Copilot-Block-MNPI',
    [Parameter(Mandatory)] [string] $RuleName       = 'FSI-Copilot-Block-MNPI-Rule',
    [Parameter(Mandatory)] [string] $CopilotLocationId,                 # Copilot location GUID (Get-DlpComplianceLocation)
    [Parameter(Mandatory)] [string[]] $SitNames,                         # SIT display names to bind
    [int] $MinCount       = 1,
    [ValidateSet('Low','Medium','High')] [string] $Confidence = 'High'
)

$ErrorActionPreference = 'Stop'

# 1. Locations array — workload Applications, identity = Copilot location GUID, all tenants.
$loc = ConvertTo-Json -Depth 6 -Compress @(
    @{
        Workload   = 'Applications'
        Location   = $CopilotLocationId
        Inclusions = @( @{ Type = 'Tenant'; Identity = 'All' } )
    }
)

# 2. Map confidence string → numeric for AdvancedRule.
$confMap = @{ Low = 60; Medium = 75; High = 85 }
$confInt = $confMap[$Confidence]

# 3. AdvancedRule JSON — Version 1, Condition with grouped SIT match.
$sitGroup = $SitNames | ForEach-Object {
    @{ name = $_; confidencelevel = $Confidence; mincount = $MinCount }
}
$advRule = ConvertTo-Json -Depth 10 -Compress @{
    Version   = '1.0'
    Condition = @{
        Operator     = 'And'
        SubConditions = @(
            @{
                ConditionName = 'ContentContainsSensitiveInformation'
                Value         = @{
                    groups = @(
                        @{
                            name           = 'FSI-MNPI-Group'
                            operator       = 'Or'
                            sensitivetypes = $sitGroup
                        }
                    )
                }
            }
        )
    }
}

# 4. Idempotent policy upsert.
$existingPolicy = Get-DlpCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue
if (-not $existingPolicy) {
    if ($PSCmdlet.ShouldProcess($PolicyName, 'New-DLPCompliancePolicy')) {
        New-DLPCompliancePolicy -Name $PolicyName `
            -Locations $loc `
            -EnforcementPlanes @('CopilotExperiences') `
            -Mode 'TestWithNotifications' | Out-Null
    }
} else {
    Write-Information "Policy '$PolicyName' already exists. Updating rule only." -InformationAction Continue
}

# 5. Idempotent rule upsert.
$existingRule = Get-DlpComplianceRule -Identity $RuleName -ErrorAction SilentlyContinue
if ($existingRule) {
    if ($PSCmdlet.ShouldProcess($RuleName, 'Set-DlpComplianceRule')) {
        Set-DlpComplianceRule -Identity $RuleName `
            -AdvancedRule $advRule `
            -RestrictAccess @( @{ setting = 'ExcludeContentProcessing'; value = 'Block' } )
    }
} else {
    if ($PSCmdlet.ShouldProcess($RuleName, 'New-DlpComplianceRule')) {
        New-DlpComplianceRule -Name $RuleName -Policy $PolicyName `
            -AdvancedRule $advRule `
            -RestrictAccess @( @{ setting = 'ExcludeContentProcessing'; value = 'Block' } ) | Out-Null
    }
}

$after = @{
    Policy = Get-DlpCompliancePolicy -Identity $PolicyName
    Rule   = Get-DlpComplianceRule   -Identity $RuleName
}
$after | ConvertTo-Json -Depth 10 |
    Set-Content (Join-Path $Session.EvidenceRoot "copilot-dlp-$PolicyName-$($Session.Stamp).json") -Encoding utf8

Write-Information "Copilot DLP policy '$PolicyName' / rule '$RuleName' published in TestWithNotifications mode." -InformationAction Continue
```

**Operational notes.**

- Always start in `TestWithNotifications` mode. Move to `Enable` only after a documented soak window and after Activity Explorer (§11) shows the expected match rate against test traffic.
- The `RestrictAccess` setting `ExcludeContentProcessing` = `Block` is what tells Copilot to *exclude* the matching content from its grounding/answer generation. This is the correct lever for "the agent must not surface this content in its answer."
- For SharePoint grounding scope, this rule complements (does not replace) Control 4.6. See cross-links at §16.

## 10. `Test-DataClassification` harness

`Test-DataClassification` is the *only* programmatic way to confirm that a SIT actually fires against a given content sample. It accepts the raw bytes of a document or a string, runs the same classification engine the DLP service uses, and returns matches.

> **Critical correctness rule.** The cmdlet returns an object with a `.ClassificationResults` property. Each result has `.SensitiveTypeName`, `.Count`, and `.Confidence`. **There is no `.SensitiveInformation` property.** Code that reads `$result.SensitiveInformation` will silently return `$null` and produce false-clean evidence — the single most damaging bug in 1.13 verification.

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
<#
.SYNOPSIS
    Runs Test-DataClassification against a corpus of fixture files and emits a
    pass/fail report keyed on expected SIT names. Treats empty ClassificationResults
    as a hard failure (the historical false-clean failure mode).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] $Session,
    [Parameter(Mandatory)] [string] $FixtureRoot,            # directory containing test files
    [Parameter(Mandatory)] [hashtable] $Expectations         # @{ 'fixture.txt' = @('Contoso-Account-Number') }
)

$ErrorActionPreference = 'Stop'
$report = @()

foreach ($file in (Get-ChildItem $FixtureRoot -File)) {
    $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
    $resp  = Test-DataClassification -DocumentData $bytes -DocumentName $file.Name

    if ($null -eq $resp -or $null -eq $resp.ClassificationResults) {
        throw "Test-DataClassification returned no ClassificationResults for $($file.Name). Aborting (false-clean guard)."
    }

    $matched = @($resp.ClassificationResults | Select-Object -ExpandProperty SensitiveTypeName)
    $expected = @($Expectations[$file.Name])

    $missing  = $expected | Where-Object { $_ -notin $matched }
    $extra    = $matched  | Where-Object { $_ -notin $expected }

    $report += [PSCustomObject]@{
        File      = $file.Name
        Expected  = $expected -join ', '
        Matched   = $matched  -join ', '
        Missing   = $missing  -join ', '
        Extra     = $extra    -join ', '
        Pass      = (-not $missing)
        Details   = $resp.ClassificationResults | Select-Object SensitiveTypeName, Count, Confidence
    }
}

$report | ConvertTo-Json -Depth 6 |
    Set-Content (Join-Path $Session.EvidenceRoot "testclass-$($Session.Stamp).json") -Encoding utf8
$report | Format-Table File, Expected, Matched, Pass -AutoSize

if ($report | Where-Object { -not $_.Pass }) {
    throw "Test-DataClassification harness failed for $((($report | Where-Object { -not $_.Pass }).File) -join ', ')."
}
```

**Fixture pack guidance.** Maintain a fixture pack alongside every custom SIT in source control:

- `tp-*.txt` — true positives. Should match the SIT at the documented confidence tier.
- `tn-*.txt` — true negatives (test sentinels, lookalike numbers without keywords). Should *not* match.
- `boundary-*.txt` — edge cases (whitespace, Unicode, leading/trailing punctuation, non-ASCII names) that the SIT is documented to handle.

Run the harness on every CI/CD merge against the SIT rule package and archive the JSON report in the evidence pack.

## 11. Audit and Activity Explorer reconciliation

Every change to a SIT, dictionary, EDM schema, classifier, or DLP rule lands in the Unified Audit Log. Reconciliation against the audit log proves that the change you intended is the change the service recorded — and surfaces drift introduced by other operators between change windows.

```powershell
#Requires -Version 7.2
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
                  @{n='Target'; e={ ($_ | ConvertFrom-Json).ObjectId }},
                  AuditData |
    ConvertTo-Json -Depth 6 |
    Set-Content (Join-Path $Session.EvidenceRoot "audit-$($Session.Stamp).json") -Encoding utf8

Write-Information "$($events.Count) audit events captured for the last $LookbackHours h." -InformationAction Continue
```

For agent-runtime evidence (which DLP rules actually fired against Copilot prompts/answers), Activity Explorer is the canonical source. Export from the portal or via the Activity Explorer Graph API; PowerShell does not currently expose Activity Explorer as first-class cmdlets in a stable surface.

> Send the audit + Activity Explorer JSON exports into your SIEM (Microsoft Sentinel for tenants on the FSI baseline) so anomaly detection — for example, an after-hours `Remove-DlpComplianceRule` against a Copilot policy — fires automatically. The AI incident-response playbook (`docs/playbooks/incident-and-risk/ai-incident-response-playbook.md`) is the standing on-call runbook.

## 12. Idempotency, drift detection, and rollback

### 12.1 Idempotency pattern

Every mutating script in this playbook follows the same shape:

1. `Get-*` to capture a **before-snapshot** to JSON.
2. If the object exists, `Set-*`; otherwise `New-*`.
3. `Get-*` again to capture an **after-snapshot**.
4. Diff before/after into a delta JSON for the change-record.

This pattern means re-running any script in this playbook with identical inputs is a no-op (modulo `WhenChangedUTC` updates).

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
|---|---|---|
| Rule package | All `DlpComplianceRule`s referencing any SIT in the pack | `Remove-DlpSensitiveInformationTypeRulePackage` |
| Document fingerprint SIT | All rules referencing it | `Remove-DlpSensitiveInformationType` |
| Keyword dictionary | All rules and rule-pack `<Match>` references | `Remove-DlpKeywordDictionary` |
| EDM schema | `EdmUploadAgent.exe /RemoveDataStore` | `Remove-DlpEdmSchema` |
| DLP policy | All child `DlpComplianceRule`s | `Remove-DLPCompliancePolicy` |
| Trainable classifier | Rules that reference its identity | Portal removal (cmdlet surface unstable) |

A pre-canned rollback for every change record means: archived before-snapshot JSON + the exact `Set-` / `Remove-` invocation that restores it. Treat rollback scripts as production code — code-review them, version them, store them next to the change record.

## 13. Sovereign-cloud reference

Cloud selection is made once, in `Initialize-Agt113Session`. Get this wrong and `Connect-IPPSSession` will silently authenticate to the wrong tenant ring.

| Cloud | `Connect-IPPSSession -ConnectionUri` | `-AzureADAuthorizationEndpointUri` | `Connect-MgGraph -Environment` | EDM agent installer |
|---|---|---|---|---|
| **Commercial** | *(default — omit)* | *(default — omit)* | `Global` | EDM Upload Agent — Commercial / GCC |
| **GCC** | *(default — same as Commercial)* | *(default)* | `Global` | EDM Upload Agent — Commercial / GCC |
| **GCC High** | `https://ps.compliance.protection.office365.us/powershell-liveid/` | `https://login.microsoftonline.us/organizations` | `USGov` | EDM Upload Agent — GCC High |
| **DoD** | `https://l5.ps.compliance.protection.office365.us/powershell-liveid/` | `https://login.microsoftonline.us/organizations` | `USGovDoD` | EDM Upload Agent — DoD |

> **Verify the DoD endpoint.** The DoD ring URL is the most volatile of the four. Confirm against the current Microsoft Learn article *"Connect to Security & Compliance PowerShell"* before each change window. If the EDM Upload Agent fails to authenticate in DoD or GCC High, edit `EdmUploadAgent.exe.config` to override the service endpoint URLs (the installer ships with the correct defaults but configuration drift on long-lived hosts is common).

Cross-tenant scenarios (a US bank operating both a Commercial tenant for non-regulated subsidiaries and a GCC High tenant for federal contracts) require **two completely separate** automation profiles — different module installations are not required, but separate connection profiles, separate evidence stores, and separate change-record systems are mandatory. Do not attempt to share a session across clouds.

## 14. Anti-patterns

The following patterns appear in the wild and have all caused production incidents in FSI tenants. None of them is acceptable in a Control 1.13 runbook.

| # | Anti-pattern | Why it fails | Correct pattern |
|---|---|---|---|
| 1 | Reading `$result.SensitiveInformation` from `Test-DataClassification` | The property does not exist. Returns `$null` → false-clean evidence. | Read `$result.ClassificationResults` and project `SensitiveTypeName`, `Count`, `Confidence`. |
| 2 | UTF-8 encoding for `New-DlpKeywordDictionary -FileData` | The cmdlet requires UTF-16 (Unicode). UTF-8 yields a corrupt or empty dictionary; non-ASCII names ("Société Générale") silently disappear. | `[System.Text.Encoding]::Unicode.GetBytes(...)` with `\r\n` line terminators. |
| 3 | `<Regex>` or `<Keyword>` placed inside `<Entity>` instead of as siblings inside `<Rules>` | Schema rejects the rule package with an opaque error. | Definitions are siblings of `<Entity>` inside `<Rules>`; `<Entity>` references them via `<IdMatch idRef="…">` / `<Match idRef="…">`. |
| 4 | Calling `Disconnect-IPPSSession` | The cmdlet does not exist; raises `CommandNotFoundException` and may leave you connected. | Call `Disconnect-ExchangeOnline -Confirm:$false` for both EXO and IPPS REST sessions. |
| 5 | Creating an EDM schema and treating the SIT as live | Schemas without an uploaded hash store match nothing. | Run `EdmUploadAgent.exe /CreateHash` + `/UploadHash` and confirm `Get-DlpEdmSchema` shows `State = Active`. |
| 6 | Identifying built-in SITs by display name in scripts | Built-in SIT display names are localised and have changed between releases. | Use the immutable GUID from `Get-DlpSensitiveInformationType -Identity <guid>`. |
| 7 | Filtering rule packages by `Publisher` string | Publisher strings have varied across Microsoft releases ("Microsoft Corporation" vs "Microsoft"). Brittle. | Filter on `Publisher` GUID, or just enumerate all and treat the result as the source of truth. |
| 8 | Inlining `$(New-Guid)` inside a SIT rule package XML heredoc | Every script run produces a different SIT, which breaks DLP rule bindings, history, and rollback. | Generate GUIDs once at design time, paste as constants, and treat as immutable. |
| 9 | Passing `-CopilotConfiguration` to `New-DLPCompliancePolicy` | The parameter does not exist — historical fabrication. | Use `-Locations` (Applications + Copilot location GUID) + `-EnforcementPlanes @('CopilotExperiences')` + `-AdvancedRule`. |
| 10 | Documenting an SLA for EDM hash-store indexing or trainable classifier publishing | Microsoft does not publish hard SLAs for these latencies. Inventing one creates a false expectation that downstream supervisory testing depends on. | Plan around a documented empirical 24–48 h validation window and link to Microsoft Learn rather than asserting an SLA. |
| 11 | Hard-coded `admin@contoso.com` in a runbook | Operator identity ends up in the audit log as the wrong principal. | `param([Parameter(Mandatory)] [string] $AdminUpn)`. |
| 12 | `Write-Host` inside a function | Bypasses the information stream; cannot be redirected to the transcript or evidence pack cleanly. | `Write-Information … -InformationAction Continue` for narration, `Write-Verbose` for diagnostics. |
| 13 | Skipping `-ResultSize Unlimited` on inventory cmdlets | Silent truncation at 1,000 objects; drift detection misses changes beyond the cap. | Always pass `-ResultSize Unlimited` on `Get-DlpSensitiveInformationType`, `Get-DlpComplianceRule`, `Search-UnifiedAuditLog`. |
| 14 | Custom SIT without `<ExcludedMatch>` test sentinels | First wave of false positives comes from synthetic data in pre-production environments. Operators learn to ignore SIT alerts. | Every custom SIT excludes `TEST-`, `SAMPLE-`, and a tenant UAT prefix. |

## 15. Evidence pack and `Write-FsiEvidence`

Every change window produces an evidence pack containing the transcript, the before/after JSON snapshots, audit-log exports, `Test-DataClassification` reports, and a SHA-256 manifest binding them together. The shared baseline (`docs/playbooks/_shared/powershell-baseline.md` §5) defines the helper:

```powershell
function Write-FsiEvidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $EvidenceDir,
        [Parameter(Mandatory)] [string] $ControlId,
        [Parameter(Mandatory)] [string] $ChangeRef     # change ticket ID
    )

    if (-not (Test-Path $EvidenceDir)) { throw "Evidence dir not found: $EvidenceDir" }

    $manifest = Get-ChildItem $EvidenceDir -File -Recurse | ForEach-Object {
        [PSCustomObject]@{
            RelativePath = (Resolve-Path $_.FullName -Relative)
            SHA256       = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
            Bytes        = $_.Length
            ModifiedUtc  = $_.LastWriteTimeUtc
        }
    }

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

## 16. Cross-links

- **Control 1.5 — Identity baseline for agent makers and admins.** SIT authoring requires the privileged-role and Conditional Access posture defined there. `docs/controls/pillar-1-security/1.5-identity-baseline-for-agent-makers-and-admins.md`
- **Control 1.6 — Sensitivity labels and label policies.** SIT detection drives auto-labelling; labels in turn drive Copilot grounding eligibility. `docs/controls/pillar-1-security/1.6-sensitivity-labels-for-ai-content.md`
- **Control 1.7 — DLP policy framework.** This playbook publishes SITs; Control 1.7 is the parent for the DLP policy engine that consumes them. `docs/controls/pillar-1-security/1.7-data-loss-prevention-for-ai-interactions.md`
- **Control 1.10 — Customer Lockbox / data-residency boundary.** Customer Lockbox and data-residency posture are covered in Control 2.1 Managed Environments — see the *Customer Lockbox & Data Residency Posture* sub-section.
- **Control 4.6 — SharePoint grounding scope governance.** SIT-based DLP rules complement scope governance for what an agent can ground on. `docs/controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- **AI Incident Response Playbook.** Standing on-call runbook for SIT/DLP alerts that fire against agent traffic. `docs/playbooks/incident-and-risk/ai-incident-response-playbook.md`
- **Shared PowerShell baseline.** Module pinning, sovereign endpoints, transcript and evidence helpers. `docs/playbooks/_shared/powershell-baseline.md`

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
