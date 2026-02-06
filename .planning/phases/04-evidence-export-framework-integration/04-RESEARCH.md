# Phase 4: Evidence Export & Framework Integration - Research

**Researched:** 2026-02-06
**Domain:** PowerShell JSON evidence export, SHA-256 integrity hashing, MkDocs documentation integration
**Confidence:** HIGH

## Summary

Phase 4 requires implementing compliance evidence export with integrity hashing and integrating the Audit Configuration Validator solution into the FSI-AgentGov framework documentation. This involves three distinct technical domains: PowerShell JSON serialization for structured evidence export, cryptographic hashing for evidence integrity, and MkDocs Material documentation patterns for framework integration.

The standard approach combines PowerShell's native `ConvertTo-Json` cmdlet with `Get-FileHash` for SHA-256 hashing, following patterns established in existing solutions (FINRA Supervision Workflow, Scope Drift Monitor). Documentation integration follows MkDocs Material admonition patterns with solution callouts in Control 1.7 and structured solution-index.md entries.

**Primary recommendation:** Use PowerShell native cmdlets with `-Depth 10` for JSON export, `Get-FileHash -Algorithm SHA256` for integrity hashing, and follow established Control 1.7 documentation patterns with "Deployable Solution" tip admonitions.

---

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PowerShell | 5.1 / 7.x | Evidence export scripting | Native to Windows, Exchange Online, Power Platform modules |
| ConvertTo-Json | Built-in | JSON serialization | Native cmdlet, no external dependencies |
| Get-FileHash | Built-in | SHA-256 hash generation | Built-in integrity verification, cryptographically secure |
| MkDocs Material | 9.x | Documentation framework | FSI-AgentGov standard, established patterns |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Out-File | Built-in | File writing with encoding | Explicit UTF8 encoding for JSON files |
| MSAL.PS | 1.x | Authentication for API calls | If exporting to external systems (not needed for file-based evidence) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ConvertTo-Json | ConvertTo-Csv | JSON supports nested objects, CSV loses structure depth |
| Get-FileHash SHA256 | Get-FileHash MD5 | SHA-256 is cryptographically stronger, industry standard for compliance |
| PowerShell JSON | Python json module | PowerShell integrates with validation scripts, no language switch |

**Installation:**

No installation required — all core tools are built into PowerShell 5.1+.

```bash
# Verify PowerShell version
$PSVersionTable.PSVersion

# Verify cmdlets available
Get-Command ConvertTo-Json, Get-FileHash
```

---

## Architecture Patterns

### Recommended File Structure

```
audit-configuration-validator/
├── scripts/
│   ├── Export-AuditValidationEvidence.ps1    # Main evidence export script
│   └── private/
│       └── Write-ValidationResult.ps1          # (existing - write to Dataverse)
├── exports/                                    # Evidence output directory
│   ├── tenant-validation-YYYYMMDD-HHMMSS.json
│   ├── tenant-validation-YYYYMMDD-HHMMSS.json.sha256
│   ├── environment-validation-YYYYMMDD-HHMMSS.json
│   └── environment-validation-YYYYMMDD-HHMMSS.json.sha256
└── docs/
    └── evidence-export-guide.md                # Documentation for auditors
```

### Pattern 1: Evidence Export with Integrity Hash

**What:** Export validation results to JSON with accompanying SHA-256 hash file

**When to use:** Compliance evidence collection, audit examinations, external storage

**Example:**

```powershell
# Source: PowerShell ConvertTo-Json best practices
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertto-json

function Export-AuditValidationEvidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('Tenant', 'Environment')]
        [string]$Scope,

        [Parameter(Mandatory)]
        [string]$OutputDirectory,

        [Parameter()]
        [string]$RunId,

        [Parameter()]
        [datetime]$FromDate = (Get-Date).AddDays(-30)
    )

    # Generate filename with timestamp
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $fileName = "$($Scope.ToLower())-validation-$timestamp.json"
    $filePath = Join-Path $OutputDirectory $fileName

    # Retrieve validation results from Dataverse
    $results = Get-ValidationResults -Scope $Scope -RunId $RunId -FromDate $FromDate

    # Convert to JSON with sufficient depth for nested objects
    $jsonContent = $results | ConvertTo-Json -Depth 10 -Compress:$false

    # Write to file with UTF-8 encoding (explicit for cross-platform compatibility)
    $jsonContent | Out-File -FilePath $filePath -Encoding utf8 -Force

    # Generate SHA-256 hash
    $hash = Get-FileHash -Path $filePath -Algorithm SHA256

    # Write hash to companion file
    $hashFilePath = "$filePath.sha256"
    "$($hash.Hash)  $fileName" | Out-File -FilePath $hashFilePath -Encoding utf8 -Force

    # Return evidence package info
    [PSCustomObject]@{
        EvidenceFile = $filePath
        HashFile = $hashFilePath
        SHA256 = $hash.Hash
        RecordCount = ($results | Measure-Object).Count
        GeneratedAt = (Get-Date).ToString('o')
    }
}
```

### Pattern 2: JSON Evidence Schema

**What:** Structured JSON format for validation evidence with metadata

**When to use:** All evidence exports to ensure consistency

**Example:**

```json
{
  "metadata": {
    "exportedAt": "2026-02-06T14:35:00Z",
    "scope": "Tenant",
    "zone": 3,
    "runId": "12345678-1234-1234-1234-123456789012",
    "exportVersion": "1.0.0",
    "organizationId": "contoso.onmicrosoft.com"
  },
  "summary": {
    "overallStatus": "Passed",
    "validationsRun": 3,
    "validationsPassed": 3,
    "validationsFailed": 0,
    "validationsWarning": 0
  },
  "validations": [
    {
      "validationType": "UnifiedAuditLog",
      "severity": "Passed",
      "timestamp": "2026-02-06T14:30:00Z",
      "rawValue": "AuditEnabled=true,CanaryEventRetrieved=true",
      "reason": "Unified Audit Log is enabled and canary event successfully retrieved within 5 minutes",
      "details": {
        "auditEnabled": true,
        "canaryRetrieved": true,
        "canaryWaitTime": "00:03:45"
      }
    }
  ]
}
```

### Pattern 3: Control Documentation Integration

**What:** Add "Deployable Solution" tip admonition to Control 1.7

**When to use:** After solution README and solutions-index.md are complete

**Example:**

```markdown
## Related Controls

| Control | Relationship |
|---------|--------------|
| [1.6 - DSPM for AI](1.6-microsoft-purview-dspm-for-ai.md) | AI interaction visibility |

!!! tip "Deployable Solution: Audit Configuration Validator"
    For automated validation of tenant and environment audit configurations with zone-based retention requirements, see the **Audit Configuration Validator** solution.

    **Capabilities:**
    - Tenant-level audit validation (Unified Audit Log, mailbox audit)
    - Environment-level audit validation (Power Platform audit retention)
    - Zone-based retention thresholds (180d/365d/730d)
    - Daily scheduled validation with drift detection
    - Evidence export with SHA-256 integrity hashing

    **Deployable Solution:** [audit-configuration-validator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-configuration-validator) provides PowerShell validation scripts, Azure Automation runbook wrappers, and Power Automate flow definitions.

---
```

### Anti-Patterns to Avoid

- **Default JSON depth (2):** ConvertTo-Json defaults to -Depth 2, which truncates nested validation details. Always specify `-Depth 10` for evidence export.
- **Missing UTF-8 encoding:** Out-File defaults may vary by platform. Explicitly specify `-Encoding utf8` for cross-platform compatibility.
- **Hash without filename:** SHA-256 hash files should include the filename being hashed (standard format: `{hash}  {filename}`).
- **Inline documentation in control files:** Don't add solution details directly to control files. Use tip admonitions that link to solutions-index.md.

---

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON serialization | Custom formatter | ConvertTo-Json | Built-in, handles type conversion, proper escaping |
| File hashing | Manual hash computation | Get-FileHash | Cryptographically verified, standard format |
| Hash verification | String comparison | Compare with Get-FileHash | Prevents encoding issues, platform-independent |
| MkDocs admonitions | Raw HTML | Native `!!!` syntax | Material theme styling, responsive, accessible |

**Key insight:** PowerShell's native cmdlets are designed for compliance evidence workflows. Custom implementations risk encoding issues, incorrect escaping, and cross-platform incompatibility.

---

## Common Pitfalls

### Pitfall 1: Insufficient JSON Depth for Nested Objects

**What goes wrong:** Validation results contain nested objects (details, rawValue parsing). Default `-Depth 2` converts deep objects to unhelpful string representations like "System.Collections.Hashtable".

**Why it happens:** ConvertTo-Json defaults to 2 levels to prevent infinite recursion. Documentation doesn't emphasize this trap.

**How to avoid:**
- Always specify `-Depth 10` for evidence export
- Test with actual nested validation results, not simple examples
- Review exported JSON to verify all properties are serialized

**Warning signs:**
- JSON contains strings like "System.Collections.Hashtable"
- Nested properties show as "@{...}" instead of expanded objects
- Reimporting JSON loses structure

**Source:** [ConvertTo-Json documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertto-json) — "The Depth parameter specifies how many levels of contained objects are included in the JSON representation. The default value is 2."

### Pitfall 2: SHA-256 Hash Format Inconsistency

**What goes wrong:** Different hash verification tools expect different formats. Inconsistent formatting breaks verification workflows.

**Why it happens:** Get-FileHash returns an object, not a formatted string. Manual formatting may omit filename or use wrong separator.

**How to avoid:**
- Use standard format: `{hash}  {filename}` (two spaces between hash and filename)
- This format is compatible with `sha256sum -c` on Linux/macOS
- Include filename in hash file for traceability

**Warning signs:**
- Hash verification tools fail to parse hash file
- Uncertain which file a hash belongs to
- Manual hash comparison required

**Source:** [Get-FileHash documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash) — Standard practice from Linux sha256sum tools.

### Pitfall 3: Mixing Solution Details into Control Files

**What goes wrong:** Adding extensive solution documentation directly to control files bloats the control, duplicates content, and creates maintenance burden.

**Why it happens:** Easy to add "just a few lines" to control. Pattern creep leads to multi-paragraph solution descriptions.

**How to avoid:**
- Control files: Brief tip admonition with link to solutions-index.md
- Solution details: Full description, architecture, prerequisites in solutions-index.md
- Limit control file addition to 5-8 lines maximum

**Warning signs:**
- Tip admonition exceeds 10 lines
- Duplicating content from solutions-index.md
- Control file diff shows >20 lines added

### Pitfall 4: Evidence Export Without Validation History

**What goes wrong:** Exporting only the latest validation run loses historical trend data needed for compliance reporting.

**Why it happens:** Focused on "current state" without considering audit trail requirements.

**How to avoid:**
- Support `-FromDate` parameter to export date ranges
- Default to last 30 days to capture trends
- Include metadata about date range in JSON export
- Document recommended export frequency (monthly for audits)

**Warning signs:**
- Auditors request historical data not in exports
- No way to show compliance trend over time
- Re-running export doesn't reproduce previous results

---

## Code Examples

Verified patterns from official sources:

### Hash Verification Script

```powershell
# Source: Get-FileHash documentation
# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash

function Test-EvidenceIntegrity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EvidenceFilePath
    )

    $hashFilePath = "$EvidenceFilePath.sha256"

    if (-not (Test-Path $hashFilePath)) {
        throw "Hash file not found: $hashFilePath"
    }

    # Read expected hash from file
    $hashContent = Get-Content $hashFilePath -Raw
    $expectedHash = ($hashContent -split '\s+')[0]

    # Compute actual hash
    $actualHash = (Get-FileHash -Path $EvidenceFilePath -Algorithm SHA256).Hash

    # Compare (case-insensitive)
    if ($expectedHash -eq $actualHash) {
        Write-Output "✓ Integrity verified: Hashes match"
        return $true
    } else {
        Write-Warning "✗ Integrity check failed: Hashes do not match"
        Write-Warning "Expected: $expectedHash"
        Write-Warning "Actual:   $actualHash"
        return $false
    }
}
```

### Dataverse Query for Evidence Export

```powershell
# Query validation history from Dataverse for evidence export
function Get-ValidationResults {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('Tenant', 'Environment')]
        [string]$Scope,

        [Parameter()]
        [string]$RunId,

        [Parameter()]
        [datetime]$FromDate = (Get-Date).AddDays(-30)
    )

    # Build OData filter
    $filters = @()

    # Scope filter (choice field, use integer value)
    $scopeValue = if ($Scope -eq 'Tenant') { 1 } else { 2 }
    $filters += "fsi_scope eq $scopeValue"

    # Date filter
    $isoDate = $FromDate.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $filters += "fsi_timestamp ge $isoDate"

    # Optional RunId filter
    if ($RunId) {
        $filters += "fsi_runid eq $RunId"
    }

    $filterString = $filters -join ' and '

    # Query Dataverse (requires ACVClient)
    $query = "fsi_auditvalidationhistories?`$filter=$filterString&`$orderby=fsi_timestamp desc"
    $results = Invoke-DataverseQuery -Query $query

    return $results.value
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual audit exports | Automated evidence export with integrity hashing | 2026 | FINRA supervision workflow established pattern |
| Depth 2 JSON default | Explicit -Depth 10 for nested objects | PowerShell 7.0+ | Prevents truncation warnings, complete serialization |
| MD5 hashing | SHA-256 hashing | ~2015 industry shift | Cryptographically stronger, compliance standard |
| Solution docs in control files | Tip admonitions linking to solutions-index.md | FSI-AgentGov v1.2.36+ | Cleaner control files, centralized solution catalog |

**Deprecated/outdated:**
- **MD5 for evidence integrity:** Security experts now recommend SHA-256 for critical applications
- **Inline solution documentation in controls:** v1.2.36+ uses solutions-index.md as single source of truth

---

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal evidence export frequency**
   - What we know: FINRA supervision workflow exports quarterly, scope-drift-monitor exports monthly
   - What's unclear: Whether audit configuration validation should default to monthly or quarterly
   - Recommendation: Default to monthly exports, document in evidence-export-guide.md, make configurable via parameter

2. **Evidence retention policy**
   - What we know: Zone-based retention (180d/365d/730d) applies to validation history in Dataverse
   - What's unclear: Whether exported evidence files follow same retention or extended (e.g., WORM storage)
   - Recommendation: Document that evidence exports support external retention policies, reference Control 1.7 WORM guidance

3. **Evidence export scope (single run vs. date range)**
   - What we know: Single run export is simpler, date range export provides trend analysis
   - What's unclear: Default behavior preference for auditors
   - Recommendation: Support both via parameter, default to last 30 days for compliance value

---

## Solutions-Index.md Integration Pattern

Based on analysis of existing entries (FINRA Supervision Workflow, Scope Drift Monitor, Compliance Dashboard):

**Required sections:**
1. **Table entry** with solution name, version, status, description, related controls
2. **Solution details section** with heading, description, components list, regulatory alignment, related controls, repository link

**Pattern:**

```markdown
### Audit Configuration Validator

Automated validation of Microsoft 365 and Power Platform audit configurations to support compliance with US financial services regulations.

**Components:**
- PowerShell validation scripts (tenant and environment level)
- Azure Automation runbook wrappers for scheduled execution
- Power Automate flow definitions for drift detection and alerting
- Dataverse tables for validation history and environment registry
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**
- FINRA 4511 (Books and Records - Audit Configuration)
- SEC 17a-3/4 (Recordkeeping - Audit Trail Requirements)
- SOX 404 (Internal Controls - Audit Logging)
- GLBA 501(b) (Safeguards - Audit Trail)

**Related Control:** [1.7 - Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)

**Repository Link:** [audit-configuration-validator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-configuration-validator)
```

---

## Control 1.7 Update Pattern

Based on existing patterns (deny-event-correlation-report in Control 1.7):

**Location:** After "Related Controls" section, before "Implementation Playbooks" section

**Pattern:**

```markdown
## Related Controls

| Control | Relationship |
|---------|--------------|
| [1.6 - DSPM for AI](1.6-microsoft-purview-dspm-for-ai.md) | AI interaction visibility |
| [1.19 - eDiscovery](1.19-ediscovery-for-agent-interactions.md) | Legal discovery |
| [3.2 - Usage Analytics](../pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Activity monitoring |
| [3.9 - Sentinel Integration](../pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | SIEM integration |

!!! tip "Advanced Implementation: Deny Event Correlation Report"
    For daily operational reports correlating deny events across Purview Audit, DLP, and Application Insights, see [Deny Event Correlation Report](../../playbooks/advanced-implementations/deny-event-correlation-report/index.md).

    **Deployable Solution:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) provides PowerShell extraction scripts and KQL queries.

!!! tip "Automated Validation: Audit Configuration Validator"
    For automated validation of tenant and environment audit configurations with zone-based retention requirements, see the **Audit Configuration Validator** solution.

    **Capabilities:**
    - Tenant-level audit validation (Unified Audit Log, mailbox audit)
    - Environment-level audit validation (Power Platform audit retention)
    - Zone-based retention thresholds (180d/365d/730d)
    - Daily scheduled validation with drift detection
    - Evidence export with SHA-256 integrity hashing

    **Deployable Solution:** [audit-configuration-validator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-configuration-validator) provides PowerShell validation scripts, Azure Automation runbook wrappers, and Power Automate flow definitions.

---

## Implementation Playbooks
```

**Key characteristics:**
- Uses "Automated Validation" heading (not "Deployable Solution" which is used for operational tools)
- Placed after existing "Advanced Implementation" tip
- Bullet list of capabilities (5-6 items)
- Single-line deployable solution reference with artifacts list
- Consistent markdown formatting with existing entries

---

## Documentation Checklist

Before marking Phase 4 complete, verify:

- [ ] Evidence export script supports both Tenant and Environment scope
- [ ] SHA-256 hash files use standard format (`{hash}  {filename}`)
- [ ] JSON export uses `-Depth 10` to prevent nested object truncation
- [ ] Evidence export guide documents recommended frequency (monthly)
- [ ] Control 1.7 updated with "Automated Validation" tip admonition
- [ ] solutions-index.md includes Audit Configuration Validator entry
- [ ] Solution README includes Prerequisites, Quick Start, Zone Requirements sections
- [ ] Deployment guide provides step-by-step administrator instructions
- [ ] All documentation follows FSI-AgentGov language guidelines (no "ensures compliance")

---

## Sources

### Primary (HIGH confidence)

- [Microsoft Learn: ConvertTo-Json](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertto-json) - JSON serialization, depth parameter
- [Microsoft Learn: Get-FileHash](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash) - SHA-256 hashing for file integrity
- [MkDocs Material: Admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) - Tip admonition syntax and styling
- FSI-AgentGov existing solutions - Pattern analysis from FINRA Supervision Workflow, Scope Drift Monitor, Compliance Dashboard

### Secondary (MEDIUM confidence)

- [PowerShell JSON Guide](https://shellgeek.com/powershell-json-guide-with-examples/) - ConvertTo-Json best practices and depth examples
- [Verify File Integrity with Get-FileHash](https://theitbros.com/file-hash-powershell/) - SHA-256 hash verification patterns
- [Financial Services Cloud Compliance Audit Trails](https://www.fastslowmotion.com/financial-services-cloud-compliance-audit-trail-best-practices/) - FSI evidence export best practices

### Tertiary (LOW confidence)

None — all critical findings verified with official documentation.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Native PowerShell cmdlets, established FSI-AgentGov patterns
- Architecture: HIGH - Patterns verified from 3 existing solutions in FSI-AgentGov-Solutions
- Pitfalls: HIGH - ConvertTo-Json depth issue documented in Microsoft Learn, verified in GitHub issues
- Documentation integration: HIGH - Pattern extracted from Control 1.7 and solutions-index.md

**Research date:** 2026-02-06
**Valid until:** 60 days (PowerShell cmdlets stable, documentation patterns established)
