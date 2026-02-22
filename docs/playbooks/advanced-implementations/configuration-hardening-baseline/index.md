# Configuration Hardening Baseline

**Status:** February 2026 - FSI-AgentGov v1.2
**Related Controls:** 1.1, 1.7, 1.8, 1.18, 1.27, 2.1, 2.22, 3.7, 3.8

---

## Purpose

This playbook consolidates security-critical configuration settings across Power Platform, Copilot Studio, and M365 Admin Center into a single reviewable hardening baseline. It enables FSI organizations to proactively verify their configuration posture across agent authentication, audit logging, content moderation, RBAC, environment governance, and AI feature access — addressing the settings most commonly flagged by security posture assessments.

**Applies to:** All zones; baseline settings apply organization-wide, with stricter requirements for Zone 2/3 environments.

---

## Problem Statement

Financial services organizations face continuous configuration drift risk across dozens of inter-related settings spanning multiple admin portals. Native PPAC security recommendations cover a subset of these settings, but critical agent-level configurations (authentication mode, content moderation level, AI feature toggles, connected agent access) are not surfaced in native posture scoring and require manual verification.

**Key challenges:**

1. **Settings span multiple portals** — PPAC, Copilot Studio, M365 Admin Center, Entra ID
2. **No native aggregated view** — each setting must be checked individually
3. **Configuration drift between reviews** — settings may change between weekly/monthly review cycles
4. **Audit evidence collection** — manual screenshots and attestation forms for each setting

---

## Master Configuration Hardening Checklist

!!! info "Automation Feasibility"
    - **Automated** — Fully queryable via Power Platform Admin Connector or Dataverse API; validated by `Invoke-HardeningBaselineCheck.ps1`
    - **Semi-Automated** — Queryable via Copilot Studio Management API or PPAC REST API (limited GA availability); may require emerging API access
    - **Manual Attestation** — No API access currently; requires portal screenshot and attestation record

### Agent Authentication and Access (Control 1.1)

| # | Setting | Portal Path | Expected Value (Zone 2/3) | Severity | Automation |
|---|---------|-------------|---------------------------|----------|------------|
| 1 | Agent authentication mode | Copilot Studio > Agent > Settings > Security | Not "No Authentication" | High | Semi-Automated |
| 2 | Require users to sign in (manual auth) | Copilot Studio > Agent > Settings > Security | Enabled | High | Semi-Automated |
| 3 | Authentication enforcement timing | Copilot Studio > Agent > Settings > Security | "Always" (not "As Needed") | High | Semi-Automated |
| 4 | Agent sharing scope | Copilot Studio > Agent > Channels > Share Settings | Copilot Readers or Security Groups (not "Anyone") | High | Semi-Automated |
| 5 | Publish bots with AI features | PPAC > Tenant Settings | Disabled (until governance review) | High | Automated |
| 6 | Unapproved shared agents blocked | M365 Admin > Copilot > Agents & connectors > Agent Inventory | Blocked | High | Semi-Automated |

!!! tip "Automated Validation Available"
    Items 1–6 can now be validated using `Test-AgentAuthConfiguration.ps1`, which reads per-agent authentication configuration via BAP/PPAC REST endpoints and validates all 6 SSPM items with zone-based logic, drift detection, and SHA-256 evidence export.

    **Script Location:** `scripts/governance/Test-AgentAuthConfiguration.ps1`

### Audit Logging (Control 1.7)

| # | Setting | Portal Path | Expected Value | Severity | Automation |
|---|---------|-------------|----------------|----------|------------|
| 7 | Environment-level auditing | PPAC > Environment > Settings > Audit and logs | "Start Auditing" enabled | High | Automated |
| 8 | Audit log retention period | PPAC > Environment > Audit settings > "Retain these logs for" | ≥ 180 days (Zone 1), ≥ 365 days (Zone 2), ≥ 730 days (Zone 3) | High | Automated |
| 9 | Tenant-level Dataverse auditing | PPAC > Security > Compliance > Auditing | "Turn on Auditing" enabled with User Sign-In and Activity | Medium | Automated |

### Content Moderation (Control 1.27)

| # | Setting | Portal Path | Expected Value (Zone 2/3) | Severity | Automation |
|---|---------|-------------|---------------------------|----------|------------|
| 10 | Content moderation level | Copilot Studio > Agent > Topics > System > Generative AI topic > Content moderation | High | High | Manual Attestation |

### RBAC and Agent Governance (Control 1.18)

| # | Setting | Portal Path | Expected Value | Severity | Automation |
|---|---------|-------------|----------------|----------|------------|
| 11 | Agent action user consent | Copilot Studio > Agent > Actions | "Ask the user before running this action" enabled for all actions | High | Manual Attestation |
| 12 | Connected agent access | Copilot Studio > Agent > Settings > Connected Agents | Disabled unless explicitly approved | High | Manual Attestation |
| 13 | Environment admin count | PPAC > Environment > Users + Permissions | < 10 System Administrators per environment | Medium | Semi-Automated |

### Environment Provisioning (Control 2.1)

| # | Setting | Portal Path | Expected Value | Severity | Automation |
|---|---------|-------------|----------------|----------|------------|
| 14 | Environment creation restriction | PPAC > Tenant Settings > Dev/Prod/Trial environment assignments | "Only specific admins" | High | Automated |
| 15 | Environment routing | PPAC > Tenant Settings > Environment Routing | Configured for correct region | Medium | Automated |
| 16 | Tenant isolation | PPAC > Security > Identity and access > Tenant Isolation | "Restrict Cross-Tenant Connections" enabled | High | Automated |
| 17 | Environment security groups | PPAC > Environment details > Security group | Assigned for all Zone 2/3 environments | High | Automated |

### AI Feature Access (Control 3.8)

| # | Setting | Portal Path | Expected Value (Zone 2/3) | Severity | Automation |
|---|---------|-------------|---------------------------|----------|------------|
| 18 | AI Prompts | PPAC > Environment > Settings > Features | Off (unless approved) | Medium | Semi-Automated |
| 19 | Generative Actions | Copilot Studio > Agent > Overview > Orchestration | Off (unless approved) | High | Manual Attestation |
| 20 | File Analysis | Copilot Studio > Agent > Settings > Generative AI > File processing | Off (unless approved) | Medium | Manual Attestation |
| 21 | Model Knowledge | Copilot Studio > Agent > Settings > Generative AI | Off for sensitive data agents | Medium | Manual Attestation |
| 22 | Semantic Search | Copilot Studio > Agent > Settings > Generative AI | Off (unless approved) | High | Manual Attestation |
| 23 | Generative AI features (per-env) | PPAC > Environment > Generative AI features | Restrict by default | Medium | Semi-Automated |
| 24 | Move Data Across Regions | PPAC > Environment > Generative AI features | Off | High | Semi-Automated |
| 25 | Bing Search | PPAC > Environment > Generative AI features | Off | Medium | Semi-Automated |
| 26 | Conversational transcript access | PPAC > Environment > Features > Copilot Studio Agents | Restricted to authorized personnel | Medium | Semi-Automated |
| 27 | DLP for agent publishing connectors | PPAC > Data policies | Block Copilot Studio for Teams and M365 Copilot channel in restricted environments | High | Semi-Automated |

### Environment Security Settings (Controls 2.22, 3.7)

| # | Setting | Portal Path | Expected Value | Severity | Automation |
|---|---------|-------------|----------------|----------|------------|
| 28 | Blocked attachment extensions | PPAC > Environment > Settings > Privacy + Security | Dangerous extensions blocked (ade, adp, app, asa, asp, bat, cmd, com, dll, exe, hta, jar, js, jse, msi, pst, reg, scr, vb, vbe, vbs, ws, wsc, wsf, wsh, etc.) | Medium | Automated |
| 29 | Blocked MIME types | PPAC > Environment > Settings > Privacy + Security | High-risk MIME types blocked (application/javascript, application/hta, text/javascript, application/x-javascript, text/scriplet, application/xml, application/msaccess, application/prg) | Medium | Automated |
| 30 | Inactivity timeout | PPAC > Environment > Settings > Privacy + Security | Enabled; ≤ 120 minutes (Zone 3: ≤ 60 minutes) | Medium | Automated |
| 31 | Session expiration | PPAC > Environment > Settings > Privacy + Security | Custom session timeout enabled; ≤ 1440 minutes | Medium | Automated |
| 32 | Content Security Policy (CSP) | PPAC > Environment > Settings > Privacy + Security > Content security policy > Model Driven | "Enforce content security policy" enabled | Medium | Automated |

---

## Review Frequency

| Zone | Review Cadence | Reviewer | Evidence Requirement |
|------|---------------|----------|---------------------|
| **Zone 1** | Monthly | Power Platform Admin | Checklist completion record |
| **Zone 2** | Bi-weekly | Power Platform Admin + AI Governance Lead | Checklist + screenshot evidence |
| **Zone 3** | Weekly | Power Platform Admin + Compliance Officer | Checklist + screenshot evidence + attestation statement |

### Escalation Triggers

The following conditions require an immediate out-of-cycle baseline review regardless of the scheduled cadence:

- **Configuration drift detected** — Automated checks report a previously passing item now failing
- **Regulatory examination notification** — Receipt of examination letter or regulatory inquiry
- **Security incident** — Any incident involving agent or Power Platform components
- **SSPM posture score degradation** — PPAC security recommendations score drops below threshold
- **New SSPM alert type** — Vendor adds new alert category requiring baseline coverage assessment

### Review Scope Matrix

| Cadence | Items Reviewed | Evidence Type |
|---------|---------------|---------------|
| Weekly (Zone 3) | All 32 items | Script + attestation |
| Bi-weekly (Zone 2) | All 32 items | Script + attestation |
| Monthly (Zone 1) | High-severity items (items 1–9, 14, 16–17, 28–32) | Script report |
| Quarterly | Full baseline + evidence package export | Complete package |
| Annual | Baseline review + classification update | Assessment report |

### Compliance Calendar Integration

Align baseline reviews with quarterly regulatory examination preparation cycles:

1. **Week 1 of quarter** — Run full automated baseline check and compile evidence package
2. **Week 2 of quarter** — Complete manual attestation for non-automated items
3. **Week 3 of quarter** — Review gaps and remediate findings
4. **Week 4 of quarter** — Archive evidence package with SHA-256 integrity hash for examination readiness

---

## Manual Attestation Procedures

For settings that cannot be validated through automated means (tenant-level toggles, approval-based configurations), collect evidence using the following procedures:

### Evidence Collection Template

For each setting in the checklist:

1. **Navigate** to the portal path listed in the checklist
2. **Capture** a screenshot showing the current setting value
3. **Document** in the attestation record:
   - Setting name and portal path
   - Current value observed
   - Expected value per checklist
   - Pass/Fail determination
   - Reviewer name and date
   - Exception documentation (if applicable)
4. **Archive** screenshots and attestation records per your organization's evidence retention policy

### Attestation Record Format

```
Setting: [Name from checklist]
Portal Path: [Path from checklist]
Expected: [Expected value]
Observed: [Actual value]
Status: [Pass / Fail / Exception]
Reviewer: [Name]
Date: [YYYY-MM-DD]
Exception Justification: [If applicable]
Next Review: [Date]
```

---

## Integration with Existing Solutions

This hardening baseline complements existing FSI-AgentGov solutions:

| Solution | Integration Point |
|----------|-------------------|
| **Audit Compliance Manager** | Validates items 7-9 (audit logging settings) automatically |
| **Environment Lifecycle Management** | Validates items 14-17 (environment provisioning) at creation time |
| **Compliance Dashboard** | Aggregate hardening baseline results into compliance posture scoring |
| **Hardening Baseline Verification Script** | Validates items 7–9 (audit logging), 14–17 (environment provisioning), and 28–32 (environment security settings) with automated pass/fail and evidence export |

### Planned Solution: Agent Security Configuration Validator

A new solution is planned to automate validation of Copilot Studio agent-level settings (items 1-6, 10-12, 18-22):

- Validates authentication mode, content moderation, connected agent access, and AI feature toggles across all agents in a tenant
- Uses Power Platform Admin Connector + Copilot Studio management API
- Provides daily drift detection with compliance scoring
- Maps to Controls 1.1, 1.8, 1.18, 3.8

---

## Evidence Export for Regulatory Examination

### Evidence Package Overview

The hardening baseline supports two evidence collection modes:

- **Automated evidence** — Generated by `Invoke-HardeningBaselineCheck.ps1` for items 7–9 (audit logging), 14–17 (environment provisioning), and 28–32 (environment security settings). The script produces a timestamped JSON report with pass/fail status per item. Items 1–6 (agent authentication and access) can also be validated via `Test-AgentAuthConfiguration.ps1` with zone-based logic and drift detection.
- **Manual attestation evidence** — Compiled by reviewers for items without full API access (items 10–12, 18–27). Follows the attestation record format in the Manual Attestation Procedures section above.

Both modes produce evidence packages suitable for regulatory examination preparation under FINRA 4511 and SEC 17a-4 requirements.

### Automated Evidence Collection

Run the hardening baseline verification script with evidence export:

```powershell
.\scripts\governance\Invoke-HardeningBaselineCheck.ps1 `
    -OutputFormat JSON `
    -OutputPath .\evidence\hardening-baseline-$(Get-Date -Format 'yyyy-MM-dd').json `
    -IncludeEvidence
```

### SHA-256 Integrity Hash

Each evidence export includes a SHA-256 integrity hash for tamper detection. The hash is computed over the results JSON before the hash field is populated:

```powershell
# Hash computation pattern (performed automatically by the script)
$resultsJson = $baselineResults | ConvertTo-Json -Depth 10 -Compress
$hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
    [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
)
$integrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
```

Examiners can verify evidence integrity by recomputing the hash against the exported JSON (excluding the `IntegrityHash` field).

### Evidence Package JSON Structure

```json
{
  "Metadata": {
    "CheckedAt": "2026-02-11T14:30:00Z",
    "ScriptVersion": "1.0.0",
    "EnvironmentsScanned": 3,
    "IntegrityHash": "A1B2C3..."
  },
  "Summary": {
    "TotalChecks": 7,
    "Passed": 5,
    "Failed": 2,
    "Skipped": 0,
    "OverallStatus": "GapsFound"
  },
  "Checks": [ ... ],
  "Gaps": [ ... ]
}
```

### Manual Attestation Evidence

For items requiring manual attestation, compile evidence packages using the attestation record format documented in the Manual Attestation Procedures section. Each attestation record should include:

1. **Screenshot** of the portal setting at the documented path
2. **Attestation record** with reviewer name, date, observed value, and pass/fail determination
3. **Exception documentation** for any approved deviations from expected values

Store manual attestation records alongside automated evidence exports for a complete evidence package.

### Storage Recommendations

| Storage Option | Use Case | Retention Feature |
|----------------|----------|-------------------|
| **SharePoint compliance library** | Organizations with M365 E5 | Retention labels with regulatory record classification |
| **Azure Blob with immutable storage** | Organizations requiring WORM compliance | Time-based immutability policies for SEC 17a-4 |
| **On-premises file share** | Air-gapped environments | File system ACLs with audit logging |

### Retention Guidance

Evidence retention periods should align with applicable regulatory requirements:

| Regulation | Minimum Retention | Applies To |
|------------|-------------------|------------|
| **FINRA 4511** | 6 years | Broker-dealer communications and records |
| **SEC 17a-3/4** | 3–6 years (varies by record type) | Books and records of securities firms |
| **SOX 302/404** | 7 years | Internal control documentation |
| **OCC 2011-12** | Per institution policy (typically 5+ years) | Model risk management records |

!!! warning "Retention Advisory"
    Organizations should consult with their compliance and legal teams to determine the appropriate retention period based on their specific regulatory obligations. The periods listed above represent minimum requirements and may not cover all applicable regulations.

---

## Related Resources

- [Control 2.22: Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md) — Zone-based inactivity timeout validation and enforcement
- [Control 3.7: PPAC Security Posture Assessment](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) — Native PPAC posture scoring
- [Control 1.24: Defender AI Security Posture Management](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) — Multi-cloud AI infrastructure posture
- [PPAC Security Best Practices](https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview)

---

*Updated: February 2026 | Version: v1.2*
