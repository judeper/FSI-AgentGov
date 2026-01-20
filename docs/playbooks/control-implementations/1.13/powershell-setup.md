# Control 1.13: Sensitive Information Types (SITs) - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md).

---

## Connect to Security & Compliance

```powershell
Connect-IPPSSession -UserPrincipalName admin@contoso.com
```

---

## Get All Sensitive Information Types

```powershell
$AllSITs = Get-DlpSensitiveInformationType
Write-Host "Total SITs available: $($AllSITs.Count)"

# Filter for financial SITs
$FinancialSITs = $AllSITs | Where-Object {
   $_.Name -match "credit card|bank account|SSN|social security|ABA|tax"
}
$FinancialSITs | Select-Object Name, Description | Format-Table
```

---

## Get Details of a Specific SIT

```powershell
Get-DlpSensitiveInformationType -Identity "U.S. Social Security Number (SSN)" |
    Select-Object Name, Description, RulePackageId
```

---

## Create Custom SIT via XML

```powershell
$RuleXML = @"
<?xml version="1.0" encoding="utf-8"?>
<RulePackage xmlns="http://schemas.microsoft.com/office/2011/mce">
  <RulePack id="$(New-Guid)">
    <Version build="0" major="1" minor="0" revision="0"/>
    <Publisher id="$(New-Guid)"/>
    <Details defaultLangCode="en">
      <LocalizedDetails langcode="en">
        <PublisherName>Contoso Financial</PublisherName>
        <Name>FSI Custom Rule Pack</Name>
        <Description>Custom SITs for financial services</Description>
      </LocalizedDetails>
    </Details>
  </RulePack>
  <Rules>
    <Entity id="$(New-Guid)" patternsProximity="300" recommendedConfidence="75">
      <Pattern confidenceLevel="85">
        <IdMatch idRef="Regex_InternalAccountNumber"/>
        <Match idRef="Keyword_AccountContext"/>
      </Pattern>
      <Pattern confidenceLevel="75">
        <IdMatch idRef="Regex_InternalAccountNumber"/>
      </Pattern>
    </Entity>
  </Rules>
  <Regex id="Regex_InternalAccountNumber">\b[A-Z]{3}-\d{6}-[A-Z0-9]{2}\b</Regex>
  <Keyword id="Keyword_AccountContext">
    <Group matchStyle="word">
      <Term>account</Term>
      <Term>customer number</Term>
      <Term>acct</Term>
      <Term>client id</Term>
    </Group>
  </Keyword>
</RulePackage>
"@

# Save XML and upload
$RuleXML | Out-File "FSI-Custom-SIT.xml" -Encoding UTF8

# Create the rule package
New-DlpSensitiveInformationTypeRulePackage -FileData ([System.IO.File]::ReadAllBytes("FSI-Custom-SIT.xml"))
```

---

## Create Keyword Dictionary

```powershell
$Keywords = @"
Goldman Sachs
Morgan Stanley
JP Morgan
Citigroup
Bank of America
Wells Fargo
"@

New-DlpKeywordDictionary -Name "FSI-Competitor-Names" `
    -Description "Major financial institution names" `
    -FileData ([System.Text.Encoding]::UTF8.GetBytes($Keywords))

# Get all keyword dictionaries
Get-DlpKeywordDictionary | Select-Object Name, Description
```

---

## Test SIT Detection

```powershell
$TestContent = "Customer account ABC-123456-XY with SSN 123-45-6789"
$TestResult = Test-DataClassification -TextToClassify $TestContent
$TestResult.SensitiveInformation | Format-Table SensitiveInformationType, Count, Confidence
```

---

## Get Custom SITs

```powershell
Get-DlpSensitiveInformationType | Where-Object { $_.Publisher -ne "Microsoft Corporation" }
```

---

## Export Custom SIT Inventory

```powershell
$CustomSITs = Get-DlpSensitiveInformationType | Where-Object { $_.Publisher -ne "Microsoft Corporation" }
$CustomSITs | Select-Object Name, Description, Publisher, RulePackageId |
    Export-Csv "Custom-SIT-Inventory-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

## EDM Schema Creation

```powershell
$SchemaXML = @"
<?xml version="1.0" encoding="utf-8"?>
<EdmSchema xmlns="http://schemas.microsoft.com/office/2018/edm">
  <DataStore name="FSICustomerData" description="Customer account data for exact matching">
    <Field name="CustomerAccountNumber" searchable="true"/>
    <Field name="SSN" searchable="true"/>
    <Field name="CustomerName" searchable="false"/>
    <Field name="DateOfBirth" searchable="false"/>
  </DataStore>
</EdmSchema>
"@
$SchemaXML | Out-File "FSICustomerDataSchema.xml" -Encoding UTF8

# Upload schema using EDM Upload Agent
# .\EdmUploadAgent.exe /UploadSchema /DataStoreName FSICustomerData /HashFile FSICustomerDataSchema.xml
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.13 - Sensitive Information Types (SITs) and Pattern Recognition

.DESCRIPTION
    This script inventories existing SITs, creates custom SITs for FSI use cases,
    and validates detection capabilities.

.PARAMETER CreateCustomSIT
    Whether to create custom FSI SIT rule package (default: false)

.PARAMETER TestDetection
    Whether to run detection tests (default: true)

.PARAMETER ExportPath
    Path for exports (default: current directory)

.EXAMPLE
    .\Configure-Control-1.13.ps1 -CreateCustomSIT $true -TestDetection $true

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.13 - Sensitive Information Types (SITs) and Pattern Recognition
#>

param(
    [bool]$CreateCustomSIT = $false,
    [bool]$TestDetection = $true,
    [string]$ExportPath = "."
)

try {
    # Connect to Security & Compliance
    Write-Host "Connecting to Security & Compliance Center..." -ForegroundColor Cyan
    Connect-IPPSSession

    Write-Host "Configuring Control 1.13: Sensitive Information Types (SITs)" -ForegroundColor Cyan

    # Step 1: Inventory existing SITs
    Write-Host "`n[Step 1] Inventorying Sensitive Information Types..." -ForegroundColor Yellow
    $AllSITs = Get-DlpSensitiveInformationType
    Write-Host "  Total SITs available: $($AllSITs.Count)" -ForegroundColor Green

    # Step 2: Identify financial SITs
    Write-Host "`n[Step 2] Identifying financial-relevant SITs..." -ForegroundColor Yellow
    $FinancialSITs = $AllSITs | Where-Object {
        $_.Name -match "credit card|bank account|SSN|social security|ABA|tax|SWIFT|IBAN"
    }
    Write-Host "  Financial SITs found: $($FinancialSITs.Count)" -ForegroundColor Green
    $FinancialSITs | ForEach-Object { Write-Host "    - $($_.Name)" }

    # Step 3: Check custom SITs
    Write-Host "`n[Step 3] Checking custom SITs..." -ForegroundColor Yellow
    $CustomSITs = $AllSITs | Where-Object { $_.Publisher -ne "Microsoft Corporation" }
    Write-Host "  Custom SITs: $($CustomSITs.Count)" -ForegroundColor Green
    $CustomSITs | ForEach-Object { Write-Host "    - $($_.Name)" }

    # Step 4: Create custom SIT (if requested)
    if ($CreateCustomSIT) {
        Write-Host "`n[Step 4] Creating custom FSI SIT rule package..." -ForegroundColor Yellow
        $RuleXML = @"
<?xml version="1.0" encoding="utf-8"?>
<RulePackage xmlns="http://schemas.microsoft.com/office/2011/mce">
  <RulePack id="$(New-Guid)">
    <Version build="0" major="1" minor="0" revision="0"/>
    <Publisher id="$(New-Guid)"/>
    <Details defaultLangCode="en">
      <LocalizedDetails langcode="en">
        <PublisherName>FSI Governance</PublisherName>
        <Name>FSI Custom Rule Pack</Name>
        <Description>Custom SITs for financial services compliance</Description>
      </LocalizedDetails>
    </Details>
  </RulePack>
</RulePackage>
"@
        $xmlPath = Join-Path $ExportPath "FSI-Custom-SIT.xml"
        $RuleXML | Out-File $xmlPath -Encoding UTF8
        Write-Host "  Custom SIT XML saved to: $xmlPath" -ForegroundColor Green
        Write-Host "  [INFO] Upload via New-DlpSensitiveInformationTypeRulePackage" -ForegroundColor Gray
    } else {
        Write-Host "`n[Step 4] Skipping custom SIT creation (CreateCustomSIT=false)" -ForegroundColor Gray
    }

    # Step 5: Test detection (if requested)
    if ($TestDetection) {
        Write-Host "`n[Step 5] Testing SIT detection..." -ForegroundColor Yellow
        $TestContent = "Test SSN: 123-45-6789 and Credit Card: 4111-1111-1111-1111"
        $TestResult = Test-DataClassification -TextToClassify $TestContent
        if ($TestResult.SensitiveInformation) {
            Write-Host "  Detection test passed:" -ForegroundColor Green
            $TestResult.SensitiveInformation | ForEach-Object {
                Write-Host "    - $($_.SensitiveInformationType): Confidence $($_.Confidence)%"
            }
        } else {
            Write-Host "  WARNING: Detection test returned no results" -ForegroundColor Yellow
        }
    }

    # Step 6: Export inventory
    Write-Host "`n[Step 6] Exporting SIT inventory..." -ForegroundColor Yellow
    $inventoryFile = Join-Path $ExportPath "SIT-Inventory-$(Get-Date -Format 'yyyyMMdd').csv"
    $AllSITs | Select-Object Name, Description, Publisher |
        Export-Csv -Path $inventoryFile -NoTypeInformation
    Write-Host "  Inventory exported to: $inventoryFile" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.13 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "`nDisconnected from Security & Compliance Center" -ForegroundColor Gray
}
```

---

*Updated: January 2026 | Version: v1.1*
