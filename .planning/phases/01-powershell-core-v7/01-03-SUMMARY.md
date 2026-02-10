# Plan 01-03 Summary: Test-ContentModerationCompliance.ps1 validation orchestrator

**Status:** Complete
**Wave:** 3
**Started:** 2026-02-10T12:00:00Z
**Completed:** 2026-02-10T12:30:00Z

## Commits

- `4ac90fd` — feat(cmm): implement Test-ContentModerationCompliance validation orchestrator

## Files Created/Modified

- `content-moderation-monitor/scripts/Test-ContentModerationCompliance.ps1` — Full implementation replacing stub (524 lines)

## Implementation Details

### Test-ContentModerationCompliance.ps1

Function-based orchestrator that chains Get-AgentModerationSettings and Compare-ModerationCompliance into a single validation workflow:

- **Parameters (12):** OutputFormat (Table/Json/Object), IncludeEnvironments, ExcludeEnvironments, ExcludeSandbox, ExcludeTrial, ExcludeDefault, GracePeriodHours (48), IncludeDrafts, IncludeCompliant, DataverseUrl, BaselinePath, Top
- **SupportsShouldProcess:** Enables `-WhatIf` dry-run mode (CMV-04)
- **Flow:** Import dependencies → Validate parameters → Build query/compare params → Get-AgentModerationSettings → Compare-ModerationCompliance → Calculate statistics → Summary banner → Format output
- **Summary banner:** Displays environments scanned, agents scanned, compliant/violation counts, severity breakdown (Critical/High/Medium/Warning) with color coding
- **Table output:** Per-agent detail with severity color coding (Critical=DarkRed, High=Red, Medium=Yellow, Warning=DarkYellow), including agent name, environment, zone, moderation levels, status, and regulatory context
- **JSON output:** Structured metadata + results array for evidence export pipeline consumption
- **Object output:** Raw PSCustomObject[] for PowerShell pipeline composition
- **Overall status:** Critical (any critical) → Failed (any high) → Review (medium/warning) → Passed
- **Empty results handling:** Graceful handling when no agents found, with appropriate banner and empty result structures per output format
- **WhatIf indicator:** DRY RUN note in banner and metadata when -WhatIf is active

### Usage Patterns Documented

```powershell
# Pattern 1: Quick dry-run (most common Phase 1 usage)
Test-ContentModerationCompliance -WhatIf

# Pattern 2: Targeted scan with JSON for automation
Test-ContentModerationCompliance -IncludeEnvironments @("env-1") -OutputFormat Json

# Pattern 3: Pipeline composition
Get-AgentModerationSettings -ExcludeSandbox | Compare-ModerationCompliance | Where-Object { $_.Severity -eq 'Critical' }

# Pattern 4: Production scan with ELM zone lookup
Test-ContentModerationCompliance -ExcludeSandbox -ExcludeTrial -DataverseUrl "https://fsi-gov.crm.dynamics.com"
```

All four patterns documented in script comment-based help with `.EXAMPLE` blocks.

## Decisions Made

- **Function-based design:** Used function wrapper (not script-level params) to match Get-AgentModerationSettings and Compare-ModerationCompliance patterns, enabling both dot-source and module import consumption
- **Dot-source dependencies:** Script imports companion scripts via dot-sourcing to load their functions into the same scope, following the established pattern
- **Data collection in WhatIf mode:** Get-AgentModerationSettings runs in both normal and WhatIf modes since it's a read-only operation — WhatIf only suppresses persistence operations (Phase 2+)
- **IncludeCompliant logic:** When IncludeCompliant is false, Compare-ModerationCompliance returns only violations; compliant count is calculated as total agents minus violations
- **Overall status classification:** Added 'Critical' status distinct from 'Failed' to match severity classification in the moderation baseline (Zone 3 Low = Critical vs Zone 2 Low = High)
- **JSON output structure:** Used explicit hashtable construction (not direct ConvertTo-Json on PSCustomObject) to produce clean, predictable JSON keys for evidence export pipeline consumers

## Self-Check

- [x] No PowerShell parse errors (Parser::ParseFile validation)
- [x] SupportsShouldProcess present on CmdletBinding
- [x] #Requires -Modules statement present
- [x] Function definition Test-ContentModerationCompliance present
- [x] All three output formats (Table, Json, Object) implemented
- [x] WhatIf/DryRun handling with banner indicator
- [x] Color-coded severity (DarkRed, Red, Yellow, DarkYellow)
- [x] Summary banner with environment/agent/violation counts
- [x] 12 parameters matching plan specification
- [x] FSI language rules — no forbidden phrases
- [x] All four usage patterns documented in comment-based help
- [x] Pipeline composition (Pattern 3) supported via raw script calls
- [x] JSON output produces valid JSON structure (ConvertTo-Json -Depth 5)
