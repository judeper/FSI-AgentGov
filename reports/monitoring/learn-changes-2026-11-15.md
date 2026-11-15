# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-15
**Run Time:** 2026-11-15T13:35:50.470375+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 2 |
| Redirects | 8 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | agent-365-security | HIGH | 3.7, 2.25 | Review and update |
| 2 | ...cipline-security-operations-incidents | HIGH | 3.4 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Agent 365 Security Overview

**URL:** https://learn.microsoft.com/en-us/security/security-for-ai/agent-365-security
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:e2b8f5ab038a44277ee5764932b4f848fcef3551686fd55937e2f600325f1ae1

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -85,9 +85,20 @@ AI agent inventory in Microsoft Defender XDR
 AI agent detection and protection in Microsoft Defender XDR
 Next steps
-Learn more about Microsoft Agent 365:
+Continue with product implementation:
 Microsoft Agent 365 documentation
 Microsoft Agent 365 blog post: The control plane for AI agents
+Connect Agent 365 deployment to organizational security adoption:
+Secure your agentic insider with SAF
+.
+Defend with agents using SAF
+.
+Secure AI with Zero Trust
+.
+Govern agent identities and privileges
+.
+Operationalize agent monitoring with SecOps implementation patterns
+.
 Feedback
 Was this page helpful?
 Yes

```

---

### 2. Incident Response Planning

**URL:** https://learn.microsoft.com/en-us/security/zero-trust/security-adoption-discipline-security-operations-incidents
**Section:** Security Operations
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:fbb3248846e6168507952b068695c3b22e1b270fc477053d4e9ba100cace06d0

**Affected Controls:**
- Control 3.4: Control 3.4: Incident Reporting and Root Cause Analysis
  - File: `controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md`

**What Changed:**
```diff
--- +++ @@ -19,176 +19,116 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Plan incident response
+Plan and run SecOps incident operations
 Feedback
 Summarize this article for me
-This article is part of the Security Operations (SecOps) discipline in the
+This article helps security and technology teams plan and run incident operations that investigate, contain, and support recovery from active cyberattacks while limiting business, operational, legal, and reputational impact.
+This guidance is part of the
+Security Operations (SecOps) discipline
+in the
 Microsoft Security Adoption Framework (SAF)
-. It helps SecOps leaders, architects, IT leaders, and business stakeholders design incident response capabilities that investigate, contain, and recover from active cyberattacks while minimizing business, operational, legal, and reputational impact.
-Use this article for incident response strategy and process guidance. For readiness activities, use
+.
+Use this article for durable incident operating principles. Use
 Prepare for incident response
-. For scenario-specific execution guidance, use
-Incident response playbooks overview
-. For control-specific and product-level implementation guidance, use
-SecOps technology
-.
-Incident response overview
-Incident response is the practice of investigating and remediating active attack campaigns against your organization.
-Incident response has the largest direct influence on critical SecOps metrics, particularly:
-Mean Time to Acknowledge (MTTA)
-. The time it takes your team to acknowledge an alert or incident after generation.
-Mean Time to Remediate (MTTR)
-. The time it takes to fix a security incident after acknowledgement.
-Reducing these metrics lowers organizational risk and limits attacker impact.
-Successful incident response depends on close collaboration between incident responders, threat hunting, threat intelligence, IT operations, legal, communications, and leadership teams
```

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*