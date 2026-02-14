# Remediation Backlog

**Generated:** 2026-02-14
**Source:** Learn Validation Matrix + Technical Findings + Documentation Findings

## Priority Definitions

| Priority | Criteria | SLA Suggestion |
|----------|----------|----------------|
| **P0** | Runtime crash, data loss, security exposure, fabricated claims | Fix before any customer deployment |
| **P1** | Incorrect Learn claims, broken features, stale data, misleading info | Fix within next release |
| **P2** | Role naming, formatting, minor doc quality, consistency | Batch into maintenance sprint |

---

## P0 — Critical (12 items)

| # | Owner | Difficulty | Type | Description | Acceptance Criteria | File(s) |
|---|-------|-----------|------|-------------|-------------------|---------|
| 1 | Eng | M | Script fix | ALCA: Remove `#Requires -Version 7.2`; add PS 5.1 requirement. Fix `Add-PowerAppsAccount` to pass `-AccessToken`. Change PUT to PATCH for EntityDefinitions. Remove invalid RecordType values. | Scripts run successfully in PS 5.1; PATCH used for metadata; only valid RecordTypes queried | Enable-AuditLogging.ps1 |
| 2 | Eng | M | Script fix | SSC: Add `return` statement to `create_schema()`. Align option set values to Dataverse convention (100000000-range) in both Python and PowerShell. | `deploy.py` completes without crash; zone queries return data | create_dataverse_schema.py, PS scripts |
| 3 | Eng | S | Script fix | DR Testing: Move recovery logic from `if ($DryRun)` to production branch. | Production mode executes recovery steps; DryRun only simulates | Invoke-DRTest.ps1 |
| 4 | Eng | S | Script fix | CAA: Remove `Write-Host` of client secret in catch block; `throw` on failure. Add `CA-CopilotStudio-*` to policy filter patterns. | No secret in output; compliance check matches template policies | Register-ServicePrincipal.ps1, Test-PolicyCompliance.ps1 |
| 5 | Eng | S | Script fix | DECR: Remove `-ApiKey` parameter from orchestrator call; align with Entra auth. | RAI extraction runs successfully with Entra ID auth | Invoke-DailyDenyReport.ps1 |
| 6 | Eng | M | Script fix | FUS: Expose access token from module; fix dot-source to call operator `&`. | Evidence export authenticates; baseline capture starts without crash | Export-FileUploadEvidence.ps1, Invoke-FileUploadBaselineCapture.ps1 |
| 7 | Eng | M | Script fix | MIME: Validate `EnforcementMode` against known set; throw on unrecognized. Change DLP template default from `TestWithNotifications` to `Enable`. | Config typos caught; fresh deployments block by default | ValidateMimeTypePlugin.cs, dlp-policy-template.json |
| 8 | Eng | S | Script fix | RAG: Write baseline hash to `fsi_baselinehash` on initial capture. | Drift detection triggers on subsequent changed scans | Invoke-SourceValidation.ps1 |
| 9 | Eng | M | Script fix | SEG: Add Power Platform role queries (PAC CLI or admin connector). | SoD scan detects PP roles; Maker/Checker rules match | Invoke-SoDScan.ps1 |
| 10 | Eng | M | Script fix | ELM: Add Dataverse pagination loop. Add HTTPAdapter with retry. Fix hash computation. | Queries return >5000 records; retries on 429; hash verification passes | elm_client.py, export_quarterly_evidence.py |
| 11 | Docs | S | Doc edit | Control 2.12: Change "GA" to "Preview" for Entra Agent ID and CA for agents. Add preview caveats. | Control states "(Preview)" with operational cautions | 2.12-agent-identity-and-lifecycle.md |
| 12 | Docs | S | Doc edit | Control 3.11: Remove fabricated "AB-900" certification reference; replace with PL-900 or remove. | No non-existent certification codes in docs | 3.11-centralized-agent-inventory-enforcement.md |

## P1 — High (18 items)

| # | Owner | Difficulty | Type | Description | Acceptance Criteria | File(s) |
|---|-------|-----------|------|-------------|-------------------|---------|
| 13 | Eng | S | Script fix | COI Testing: Replace hardcoded PASS with actual agent interaction via Direct Line API. | Tests call agent and validate responses | run_coi_tests.py |
| 14 | Eng | S | Script fix | Dashboard: Change OAuth scope to env-specific `{env}.crm.dynamics.com`. Update control count from 62 to 71. | Least-privilege scope; correct control count | load_sample_data.py |
| 15 | Eng | S | Script fix | HT: Change `SEVERITY_WEIGHTS` dict keys from string to integer matching Dataverse. | Score calculations return correct weighted values | analyze_patterns.py |
| 16 | Docs | S | Doc edit | Control 2.23: Fix portal path from "Settings > Org settings > Copilot > AI Disclaimer" to correct path. | Portal path matches Microsoft Learn | 2.23-copilot-actions-and-connectors.md |
| 17 | Docs | S | Doc edit | Control 3.8: Clarify CopilotForM365AdminExclude scope — excludes admin center only, not end-user Copilot. | Scope correctly described | 3.8-copilot-hub-and-governance-dashboard.md |
| 18 | Docs | S | Doc edit | Control 4.6: Correct sync frequency — 4-6h is Salesforce/ServiceNow only; SharePoint requires manual sync. | Sync behavior accurately documented per source type | 4.6-knowledge-source-security.md |
| 19 | Docs | S | Doc edit | license-requirements.md: Update Dataverse default from 5 GB to 15 GB. Add license rows for controls 1.25-1.28, 2.22-2.24, 3.11-3.12. Rename "Copilot for Enterprise" to "Microsoft 365 Copilot". | Correct capacity, all 71 controls mapped, correct product name | docs/reference/license-requirements.md |
| 20 | Docs | S | Doc edit | executive-summary.md: Update pillar control counts to 28/24/12/7=71. | Total matches actual control count | docs/framework/executive-summary.md |
| 21 | Docs | S | Doc edit | governance-fundamentals.md: Update pillar table to 28/24/12/7=71 to match header. | Table and header consistent | docs/framework/governance-fundamentals.md |
| 22 | Docs | S | Doc edit | glossary.md: Fix FINRA 4512 from "Continuing Education" to "Customer Account Information". | Regulatory reference factually correct | docs/reference/glossary.md |
| 23 | Docs | S | Doc edit | solutions-index.md: Update Dashboard control count from 62 to 71. Remove stale "before February 2026" deadline or update. Replace "Ensures" with "Supports". | Correct counts, current timeline, compliant language | docs/reference/solutions-index.md |
| 24 | Docs | S | Doc edit | solutions-architecture-guide.md: Correct UAL limit from 50,000 to 5,000 per query. | Correct limit stated | docs/reference/solutions-architecture-guide.md |
| 25 | Docs | S | Doc edit | Control 1.17: Correct GSA terminology — Internet Access is a component, not former name. | Accurate product lineage | 1.17-global-secure-access.md |
| 26 | Docs | S | Doc edit | Control 2.20: Update MITRE ATLAS counts (12 tactics, 100+ techniques). | Current ATLAS figures | 2.20-ai-risk-assessment.md |
| 27 | Eng | S | Script fix | ELM: Fix PrivilegeDepth values from 1,2,4,8 to 0,1,2,3. Remove "included in M365 E3/E5" licensing claim. | Correct enum values; accurate licensing | ELM README + scripts |
| 28 | Eng | S | Script fix | MCM: Clarify Premium license requirement. Fix Graph severity enum (no "critical" in serviceUpdateMessage). | Correct licensing; correct enum | MCM README + flow |
| 29 | Eng | S | Script fix | SDM: Replace deprecated `Send-MailMessage` with `Send-MgUserMail`. | No PS7 obsolete warnings | SDM scripts |
| 30 | Eng | S | Script fix | FUS: Handle `Get-AzAccessToken` SecureString return in Az.Accounts 5.0+. | Compatible with current Az.Accounts | FUS scripts |

## P2 — Maintenance (57 items)

### Role Naming Standardization (14 items)

| # | Control | Current | Canonical | File |
|---|---------|---------|-----------|------|
| 31 | 1.5 | Entra AI Admin | AI Administrator | 1.5-data-loss-prevention-dlp-and-sensitivity-labels.md |
| 32 | 1.8 | Power Platform Administrator | Power Platform Admin | 1.8-runtime-protection-and-external-threat-detection.md |
| 33 | 1.11 | Copilot Studio Environment Admin | Environment Admin | 1.11-conditional-access-and-phishing-resistant-mfa.md |
| 34 | 1.19 | Purview eDiscovery Admin | Purview eDiscovery Roles | 1.19-ediscovery-for-agent-interactions.md |
| 35 | 3.4 | Platform Admin | Power Platform Admin | 3.4-incident-reporting-and-root-cause-analysis.md |
| 36 | 3.8 | M365 Administrator | (Add to catalog or use canonical) | 3.8-copilot-hub-and-governance-dashboard.md |
| 37 | 3.9 | Platform Admin | Power Platform Admin | 3.9-microsoft-sentinel-integration.md |
| 38 | 4.2 | Site Collection Admin | SharePoint Site Collection Admin | 4.2-site-access-reviews-and-certification.md |
| 39 | 4.3 | Records Management | Purview Records Manager | 4.3-site-and-document-retention-management.md |
| 40 | 4.4 | Security Admin | Entra Security Admin | 4.4-guest-and-external-user-access-controls.md |
| 41 | 4.7 | Microsoft 365 Admin | (Add to catalog or use canonical) | 4.7-microsoft-365-copilot-data-governance.md |
| 42 | Multiple | Purview Data Security AI Admin | (Add to role catalog) | 1.5, role-catalog.md |
| 43 | Multiple | Authentication Administrator | (Add to role catalog) | 1.11, role-catalog.md |
| 44 | Multiple | Microsoft Purview Admin | (Add to role catalog) | 1.19, role-catalog.md |

### Structural / Formatting (9 items)

| # | Type | Description | File |
|---|------|-------------|------|
| 45 | Gap | Missing `---` separator before Implementation Playbooks | 1.11 |
| 46 | Gap | Missing `---` separator before Implementation Playbooks | 3.8 |
| 47 | Gap | Missing `---` separator before Implementation Playbooks | 3.11 |
| 48 | Gap | Missing `---` separator before Implementation Playbooks | 3.12 |
| 49 | Missing | Missing "Last Verified" header field | 3.11 |
| 50 | Missing | Missing "Last Verified" header field | 3.12 |
| 51 | Ambiguity | Instructions say "Implementation Guides" vs template "Implementation Playbooks" | .github/copilot-instructions.md |
| 52 | Ambiguity | Footer versions inconsistent (v1.2 Jan vs v1.2.41 Feb) | Multiple files |
| 53 | Incorrect | Related Controls table uses external URL not internal cross-ref | 4.7 |

### Content Quality (8 items)

| # | Type | Description | File |
|---|------|-------------|------|
| 54 | Ambiguity | Add functional/operational roles section to role catalog | role-catalog.md |
| 55 | Gap | Add CFTC Rule 1.31 dedicated section | regulatory-framework.md |
| 56 | Ambiguity | Dual Accountable in RACI for Zone 3 approval | executive-summary.md |
| 57 | Missing | Add regulatory citations for retention periods | executive-summary.md |
| 58 | Ambiguity | Zone 1 "Compliance: None" should be hedged | quick-start.md |
| 59 | Docs | SAM feature count (11 of 12) is stale; now 13+ | sam-licensing.md |
| 60 | Docs | Rename "M365 E5 Compliance" to "Microsoft Purview Suite" | FINRA supervision, solutions docs |
| 61 | Docs | Control 3.6 uses `AgenticUser` userType — not standard | 3.6-agent-inventory.md |

### Systemic Engineering (26 items)

| # | Type | Description | Solutions Affected |
|---|------|-------------|-------------------|
| 62 | Script fix | Add Dataverse pagination loop | ELM, ALCA, FUS, SSC, AAM, HT, RAG, Dashboard |
| 63 | Script fix | Move secrets to Key Vault; remove `--client-secret` CLI args | CAA, DECR, FUS, SSC, SEG, MIME |
| 64 | Script fix | Add Graph API retry/backoff with exponential delay | CAA, DECR, FUS, SSC |
| 65 | Script fix | Replace wildcard `Cert:\*\` with specific store path | AAM, CMM, FUS, SSC |
| 66 | Script fix | Add structured logging with timestamps and correlation IDs | All 25 solutions |
| 67 | Script fix | Add WhatIf/DryRun mode for destructive operations | Solutions with write operations |
| 68 | Script fix | Add input validation for all parameters | All solutions |
| 69 | Script fix | Add troubleshooting section to READMEs | Solutions missing it |
| 70 | Script fix | Add rollback/undo guidance | Solutions with schema or policy changes |
| 71–87 | Various | Individual Medium/Low findings per solution | Various |

---

## Implementation Sequence

1. **Sprint 0 (P0):** Items 1–12 — all Critical runtime/data/security issues
2. **Sprint 1 (P1 Eng):** Items 13–15, 27–30 — script correctness fixes
3. **Sprint 1 (P1 Docs):** Items 16–26 — Learn-contradicted doc updates
4. **Sprint 2 (P2):** Items 31–70 — role naming, formatting, systemic improvements
5. **Ongoing:** Items 71–87 — individual solution hardening
