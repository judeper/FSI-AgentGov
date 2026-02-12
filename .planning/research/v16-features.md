# v16 Research: Features & Capabilities — Unrestricted Agent Sharing Detector

**Dimension:** Features
**Created:** 2026-02-12

## Related Controls

| Control | Relevance |
|---------|-----------|
| **1.1** — Restrict Agent Publishing by Authorization | Primary. Agent auth mode, sharing scope, publishing restrictions — UASD automates 6 SSPM checks (01-06) currently manual-only |
| **3.8** — Copilot Hub and Governance Dashboard | Primary. Agent Access Control settings, zone-based allowed agent types |
| **2.8** — Access Control and Segregation of Duties | Secondary. SoD enforcement for remediation approvals |
| **3.7** — PPAC Security Posture | Secondary. Connected agent access settings |

## Existing Solutions (Complementary)

| Solution | What It Covers | UASD Adds |
|----------|---------------|-----------|
| **Agent Access Governance Monitor (AAM)** | Environment-level agent access settings (`bot-limitSharingMode`, etc.) | Per-agent sharing principal validation |
| **Configuration Hardening Baseline** | 32-item checklist, items 1-6 are Control 1.1 (manual attestation) | Automated detection of items 1-4 (auth mode, sign-in, sharing scope) |
| **Content Moderation Monitor (CMM)** | Per-agent moderation level validation | Different concern — complements UASD |

## Feature Gaps Addressed

### Gap 1: Per-Agent Sharing Principal Detection
**Current state:** No solution scans individual agents for their sharing configuration (who they're shared with).
**UASD delivers:** Continuous scanning of all agents' principal lists via BAP API, with 5 violation types.

### Gap 2: Org-Wide Sharing Detection
**Current state:** Manual portal review only.
**UASD delivers:** Automatic detection of `type = Organization` principals, violation creation, remediation workflow.

### Gap 3: Unapproved Security Group Enforcement
**Current state:** No approved group registry exists.
**UASD delivers:** `fsi_ApprovedSecurityGroup` table with zone-scoped group allowlist, automated validation against it.

### Gap 4: Cross-Tenant Access Detection
**Current state:** No automation detects agents shared with external tenant principals.
**UASD delivers:** Home tenant comparison, `CROSS_TENANT_ACCESS` violation type.

### Gap 5: Exception Lifecycle Management
**Current state:** Exceptions tracked manually (if at all).
**UASD delivers:** Dual-approval exception workflow with 90-day default expiration, automatic re-evaluation on expiry.

### Gap 6: Phantom Script
**Current state:** `restrict-agent-publishing.ps1` listed in `scripts/governance/README.md` but never created.
**UASD delivers:** `Invoke-SharingAudit.ps1` covers the detection portion; publishing restriction enforcement covered by detection rules.

## User Workflows Supported

1. **Daily automated scan** — Detector flow runs on schedule, populates Dataverse, sends Teams alerts
2. **On-demand audit** — `Invoke-SharingAudit.ps1` for ad-hoc investigations
3. **Exception request** — Exception Manager app → dual approval → time-bound suppression
4. **Remediation** — Approval-based principal overwrite; auto only for PUBLIC_INTERNET_LINK
5. **Evidence export** — `Export-ViolationReport.ps1` with SHA-256 for regulatory examination

## Confidence: High

All features directly map to spec Sections 1-9. No feature gaps beyond what's specified.
