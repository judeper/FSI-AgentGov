# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-06
**Run Time:** 2026-10-06T12:55:36.275922+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | whats-new | HIGH | 2.25, 2.5, 2.10 | Review and update |
| 2 | dlp-policy-reference | HIGH | 1.5 | Review and update |

---

## HIGH: Control Review Recommended

### 1. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:b746055b6e7b06626684d356b6e4d9f83345e38bb1dae0b946c424eb51e39324

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -24,13 +24,52 @@ Summarize this article for me
 This article provides resources to learn about new features in Copilot Studio.
 Released versions
-For information about the new features, fixes, and improvements released in the past few weeks, see
-Released versions of Microsoft Copilot Studio
-.
+Get an overview of new capabilities in the
+Roadmap
+. You can filter for products and specific areas and learn what's coming when.
 Note
 Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+September 2026
+Add an
+extract node
+to a workflow to pull named values and tables out of documents, such as invoices, contracts, and financial statements, so later steps can use the extracted data.
+(Preview) Add a
+Copilot node
+to a workflow to run Copilot Chat or a Cowork task, grounded in the connected user's mail, files, calendar, and chats, and to call agents like Researcher and Analyst or your own Agent Builder agents.
+Choose a
+model
+for your agent powered by the GitHub Copilot harness from a simple dropdown menu, and try out experimental models early to evaluate them before they're production-ready.
+Configure a
+content safety test method
+to evaluate your agent's responses for potentially harmful content, such as hateful, sexual, violent, or self-harm content, with configurable severity thresholds.
+(General availability)
+Attach files
+to a conversation so your agent can read, summarize, or otherwise reason over them, now expanded to support Excel, PowerPoint, and Word files.
+Add
+Dataverse tables
+as a knowledge source to ground your agent in your organization's Dataverse data, including (preview) unstructured reasoning over Multiline Text and File columns so your agent can find answers in notes, descriptions, and attached documents, not just structured fields.
+August 2026
+Learn about
+usage-bas
```

---

### 2. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:cb1f231a85ab9a4c2a70d5a32fe8504a7a99ec024391161f3211a3b85f8bb114

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**What Changed:**
```diff
--- +++ @@ -2835,17 +2835,21 @@ Block everyone
 to block internal users.
 Learn more URL
-Users may want to learn why their activity is being blocked. You can configure a site or a page that explains more about your policies. When you select
-Provide a compliance URL for the end user to learn more about your organization's policies (only available for Exchange)
-, and the user receives a policy tip notification in Outlook Win32, the
+Users may want to learn why their activity is being blocked. You can configure a site or a page that explains more about your policies. In the rule's user notification settings, select
+Provide a compliance URL for the end user to learn more about your organization's policies
+, and then enter the URL.
+For Outlook Win32, the
 Learn more
-link points to the site URL that you provide. This URL has priority over the global compliance URL configured with
-Set-PolicyConfig -ComplainceURL
+link in the policy tip points to the site URL that you provide. This URL has priority over the global compliance URL configured with
+Set-PolicyConfig -ComplianceURL
+.
+For Microsoft Copilot and Copilot Chat, the
+Learn about access restrictions
+link in the standard block message points to the URL that you provide. Only the link destination changes; the message text and enforcement action remain unchanged. For more information, see
+Customize the link in Copilot policy tips
 .
 Important
-You must configure the site or page that
-Learn more
-points to from scratch. Microsoft Purview doesn't provide this functionality out of the box.
+You must configure the site or page that the link points to from scratch. Microsoft Purview doesn't provide this functionality out of the box.
 User overrides
 The intent of
 User overrides

```

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*