# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-15
**Run Time:** 2026-09-15T11:17:43.094506+00:00
**Total URLs Checked:** 231

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| Redirects | 5 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | sec-gov-intro | HIGH | 3.8 | Review and update |
| 2 | whats-new | HIGH | None | Review and update |
| 3 | kit-agent-review-tool | HIGH | 2.3 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Governance Guidance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/sec-gov-intro
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:53a3b679ed781283707777d8b61eb63570fc615c0886123cb91f7d44c3a697dc

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -39,6 +39,10 @@ : Implement a disciplined ALM approach for your Copilot Studio agents by moving agents through environments and using automated pipelines to ensure controlled deployments, consistent quality, and reliable promotion from development to production.
 Monitor operations, compliance, and capacity
 : Use Copilot Studio's built-in analytics, transcript reviews, and feedback tools to monitor agent effectiveness, spot regressions, and drive iterative improvements across quality, safety, and user satisfaction.
+Manage the AI model lifecycle for Copilot Studio agents
+: Establish a model lifecycle management strategy to ensure your agents use the most appropriate AI models for their tasks.
+Govern Copilot Credit consumption
+: Find agents powered by the GitHub Copilot harness, classify the environments that hold them, and apply controls that keep Copilot Credit consumption within approved boundaries.
 Review the manage checklist
 : Validate security, governance, compliance, and deployment requirements.
 Feedback

```

---

### 2. Copilot Studio guidance hub — What's new

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:d0660a3f92cd9234f23d8fdd6049ef2808436f126730357d0ea34afd08a035a7

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -23,10 +23,52 @@ Feedback
 Summarize this article for me
 Get the latest information about what's new and what changed in the Copilot Studio guidance hub.
+September 2026
+New articles
+Govern Copilot Credit consumption for agents powered by the GitHub Copilot
+Other updates
+New real-world case studies showing how
+Coca-Cola Andina uses Copilot Studio to improve HR support for frontline workers
+and how
+COSMO CONSULT uses Copilot Studio agents to improve sales operations and data quality
+New
+Reference architectures
+in the Power Platform and Copilot Studio Architecture Center:
+Migrate legacy meetings to Microsoft Teams with a conversational agent
+Automate procurement order acknowledgment matching with Copilot Studio and SAP
+August 2026
+New articles
+Prevent duplicate messages with context-aware design in the standard harness
+Manage the AI model lifecycle for Copilot Studio agents
+July 2026
+New articles
+New Copilot Agent Kit capabilities, including
+Agent Debugger
+,
+Agent Library
+,
+Agent Insights Hub
+,
+Power Shield
+, and
+Agent Review Pipeline
+, with significant updates to
+Agent Review Tool
+to describe its expanded scope. This update marks the first phase of the rename from
+Copilot Studio Kit
+to
+Copilot Agent Kit
+.
 June 2026
 New articles
 Measure the return on investment (ROI) and business value of AI agents
 Plan Copilot Studio agent deployments for throughput and rate limits
+Other updates
+New real-world case studies, on how
+Grupo Bimbo standardizes global audit processes with Copilot Studio
+and on how
+Copilot Agent Kit helps organizations improve visibility, monitor performance, and refine their agents
+.
 May 2026
 Architecting agent solutions
 moved to the
@@ -52,7 +94,7 @@ Dunaway, a Texas-based, multidiscipline design, planning, and engineering firm, streamlines city code research with Copilot Studio
 and on 
```

---

### 3. Copilot Agent Kit — Agent Review Tool

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/kit-agent-review-tool
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:3db7d78d15abd2bea3fae0e7dfd74200e4bc113721c2b04caa5f2efde18bca61

**Affected Controls:**
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`

**What Changed:**
```diff
--- +++ @@ -173,7 +173,7 @@ : A second AI model reads the agent's system instructions and checks them against 15 best-practice criteria from Microsoft's generative-mode guidanceâcovering scope, safety, response quality, and user experience. For each criterion the instructions don't satisfy, it surfaces a specific finding and a concrete recommendation.
 After all three steps complete, a PDF report is automatically generated and the results open in the review panel.
 Important
-Each review consumes Copilot credits. The AI-powered steps (pattern evaluation, instruction compliance check, and PDF generation) each invoke an AI model through Dataverse. Plan accordingly if you're reviewing a large number of agents.
+Each review consumes Copilot Credits. The AI-powered steps (pattern evaluation, instruction compliance check, and PDF generation) each invoke an AI model through Dataverse. Plan accordingly if you're reviewing a large number of agents.
 Patterns detected
 Patterns identify specific anti-patterns or missing best practices in an agent's configuration. The tool checks 18 patterns across 7 categories.
 All 18 patterns
@@ -793,8 +793,8 @@ Yes. The tool only shows agents that have generative AI enabled, so every agent in the grid is expected to have instructions. If the compliance check reports no instructions, the agent's generative orchestration is active but no system instructions are written yet. Adding instructions is strongly recommended.
 Why is "Persona and Tone" Low severity?
 Microsoft's guidance notes that a professional, polite tone is already the default behavior for Copilot Studio agents. Instructions for tone are only necessary if you want a non-default tone. This criterion is Low because failing it rarely causes user-facing problems.
-Does running a review consume Copilot credits?
-Yes. Each review invokes AI models three timesâfor pattern evaluation, instruction compliance, and PDF generation. Each invocation consumes Copilot credits from your ten
```

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/overview | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/security-governance | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/security-governance |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/management-controls | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/management-controls |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*