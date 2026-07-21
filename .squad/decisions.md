# Squad Decisions

## Active Decisions

### Issue #248: Control 1.3 Label Lookup Property (Linus, 2026-07-21)

**Decision:** Do not add `DisplayName` fallback in label filter; use `Name` only with null-guard.

**Rationale:** `MicrosoftGraphInformationProtectionLabel` has never exposed `DisplayName` in any documented version. Adding fallback would mislead future maintainers and recreate the original silent-failure bug. Applied deterministic filter `@($allLabels | Where-Object { $_.Name })` to guard against atypical objects instead.

**Owners:** Linus (implementation), Saul (review), judeper (team alignment).

**Team action:** Consider adding `.Name` vs `.DisplayName` distinction note to PowerShell baseline (`docs/playbooks/_shared/powershell-baseline.md`).

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
