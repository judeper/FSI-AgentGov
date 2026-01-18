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

*Updated: January 2026 | Version: v1.1*
