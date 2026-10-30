# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-30
**Run Time:** 2026-10-30T12:18:13.325731+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 3 |
| MEDIUM Changes | 2 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | knowledge-copilot-studio | MEDIUM | 4.8, 2.16, 1.14 | Update portal-walkthrough |
| 2 | microsoft-365-copilot-privacy | HIGH | 4.7, 4.6, 2.23 | Update portal-walkthrough |
| 3 | encryption-sensitivity-labels | MEDIUM | 1.16 | Review optional |
| 4 | microsoft-purview-service-description | HIGH | None | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:16c12f557f8b09832eb783a3d9750c0a3ad822eb1b6b0d88dd0ef3cfb0035901

**Affected Controls:**
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -202,7 +202,7 @@ If you customize the generative answer response, citations aren't added automatically. For example, if you clear a
 Message
 node and render the answer yourself through a variable or an Adaptive Card, you need to include citation rendering yourself. In Teams, citation links are returned automatically only for answers that aren't customized. Learn more in
-Citations aren't rendered for customized answers
+Citations don't render for customized answers
 .
 Use information from the web
 You can find the

```

---

### 2. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:7108bbd57b08cb567370196ed7c212bcf55b3f8663262d3e899f780a1cc2a8af

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -21,8 +21,6 @@ Data, Privacy, and Security for Microsoft Copilot
 Feedback
 Summarize this article for me
-Note
-Microsoft 365 Copilot is now named Microsoft Copilot, and Microsoft 365 Copilot Chat is now named Microsoft Copilot Chat. Some experiences, licenses, and capabilities might continue to reference Microsoft 365 Copilot and Microsoft 365 Copilot Chat during the transition period. There are no changes to security, compliance, and privacy for organizations.
 Microsoft Copilot is a sophisticated processing and orchestration engine that provides AI-powered productivity capabilities by coordinating the following components:
 Large language models (LLMs)
 Content in Microsoft Graph, such as emails, chats, and documents that you have permission to access.

```

---

### 3. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:7764363ecb851354d3294b3779cc736e8da5e41bf71b6892a07d96ada1a80c7f

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.10/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -230,7 +230,8 @@ Licensing for retention policies
 For organization-wide, location-wide, or include/exclude retention policies, the following licenses provide user rights:
 Microsoft 365 E5/A5/G5/E3/A3/G3, Business Premium
-Microsoft Purview Suite/EDU/GOV/FLW and Microsoft Defender + Purview Suite FLW
+Microsoft Purview Suite/EDU/GOV/FLW
+Microsoft Defender + Purview Suite FLW
 Microsoft 365 E5/A5/F5/G5 Information Protection and Governance
 Office 365 E5/A5/G5/E3/A3/G3
 If the retention policy location is an Exchange mailbox, then the following licenses also provide user rights:
@@ -251,10 +252,12 @@ Business Premium
 Office 365 E5/G5/A5/E3/G3/A3/
 F3/E1/G1
-Microsoft Purview Suite FLW and Microsoft Defender + Purview Suite FLW add-on plans
+Microsoft Purview Suite FLW add-on plans
+Microsoft Defender + Purview Suite FLW add-on plans
 If the retention policy uses an adaptive policy scope, then one of the following licenses is required to provide user rights:
 Microsoft 365 E5/A5/G5
-Microsoft Purview Suite/EDU/GOV/FLW and Microsoft Defender + Purview Suite FLW
+Microsoft Purview Suite/EDU/GOV/FLW
+Microsoft Defender + Purview Suite FLW
 Office 365 E5/A5/G5
 Microsoft 365 E5/A5/F5/G5 Information Protection and Governance
 If the retention policy applies to Microsoft Copilot interactions, the following licenses provide user rights:
@@ -264,7 +267,8 @@ Licensing for retention labels
 For retention label creation, the following licenses provide user rights:
 Microsoft 365 E5/A5/G5/E3/A3/G3/F3/F1/Business Premium
-Microsoft Purview Suite/EDU/GOV/FLW and Microsoft Defender + Purview Suite FLW
+Microsoft Purview Suite/EDU/GOV/FLW
+Microsoft Defender + Purview Suite FLW
 Microsoft 365 E5/A5/F5/G5 Information Protection and Governance
 Office 365 E5/A5/G5/E3/A3/G3/F3/E1/A1/G1
 The following retention label creation settings:
@@ -274,7 +278,8 @@ After the retention period, automatically change the retention label,
 Require these specific licenses to provide users 
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Knowledge Sources
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:16c12f557f8b09832eb783a3d9750c0a3ad822eb1b6b0d88dd0ef3cfb0035901

---

### 2. Information Rights Management
**URL:** https://learn.microsoft.com/en-us/purview/encryption-sensitivity-labels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:24beafb1fe0256e7eb21a1e0f3a9b67fd7406c9aac2f518b8142800e3663aa4c

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*