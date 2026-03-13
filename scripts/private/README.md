# scripts/private/

Internal PowerShell module functions for the **Conditional Access Automation (CAA)** solution.

These files are private helper functions consumed by the `conditional-access-automation.psd1` module manifest in the parent directory. They are not intended to be called directly.

| File | Purpose |
|------|---------|
| `CAAClient.psm1` | Dataverse Web API client for CAA policy data |
| `Connect-GraphSession.ps1` | Microsoft Graph authentication with required scopes |
| `Get-PolicyBaseline.ps1` | Captures current CA policy state as baseline snapshots |
| `Compare-PolicyBaseline.ps1` | Compares current CA policies against baseline snapshots |
| `Get-ZoneClassification.ps1` | Determines governance zone (1/2/3) from CA policy display names |
| `Test-ParameterValidation.ps1` | Validates CAA configuration file structure |
