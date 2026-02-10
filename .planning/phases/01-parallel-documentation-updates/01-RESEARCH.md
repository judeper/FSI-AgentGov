---
phase: 1
type: research
created: 2026-02-10
title: Phase 1 Research — Parallel Documentation Updates
---

# Phase 1 Research: Parallel Documentation Updates

## Summary

This research document analyzes all target files for the 4 parallel plans in Phase 1. Each plan operates on non-overlapping file sets, confirming zero file conflicts and full parallel execution safety.

**Files analyzed:** 18 existing files + 2 reference files (template, CONTRIBUTING.md)
**Plans covered:** 01-01 (Dataverse deprecation), 01-02 (Agent 365 GA), 01-03 (Evaluation framework), 01-04 (Multi-source investigation)

---

## Plan 01-01: Dataverse Purview Audit Deprecation

### Requirements: FCR-01, FCR-02, FCR-03

### File Analysis

#### 1. `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- **Lines:** 261
- **Version footer:** `v1.3 | February 2026`
- **Current structure:** Header metadata → Agent 365 info admonition → 10 sections + extra reference sections at end (Agent 365 Audit Events, Observability by Agent Type)
- **Existing admonitions:** `!!! info "Agent 365 Architecture Update"`, `!!! info "Updated February 2026"`, `!!! warning "Agent Logs Are Typically Communications"`, `!!! info "FINRA Notice 25-07 Status"`, `!!! warning "Audit Schema Captures Metadata, Not Full Content"`, `!!! note "Querying AI Audit Events"`
- **Dataverse section (lines 138-143):** "Dataverse Environment-Level Audit Configuration" under Key Configuration Points — documents enabling environment-level auditing, configuring retention, and tenant-level Dataverse auditing policy
- **Verification Criteria (items 7-9):** Explicitly reference Dataverse environment-level auditing checks

**What needs to change (FCR-01):**
- Add a `!!! warning "Dataverse Purview Audit Event Changes — May 2026"` admonition near the Dataverse Environment-Level Audit Configuration subsection (around line 138)
- Warning content: Starting May 2026, Dataverse will no longer include before-and-after field change values in audit events sent to Microsoft Purview. Customers requiring detailed field-level change data must retrieve it directly from Dataverse APIs
- Add guidance to use Dataverse APIs as the alternative data source for field-level changes
- No structural changes needed — this is an additive warning

**Patterns to follow:**
- Admonition format: `!!! warning "Title"` with 4-space indented content
- Hedged language: "organizations should", "may need to"
- Regulatory references: cite specific sections (SEC 17a-4, FINRA 4511)

**Complexity:** Simple edit (add admonition + 1-2 paragraphs)

---

#### 2. `docs/controls/pillar-1-security/1.10-communication-compliance-monitoring.md`
- **Lines:** ~175
- **Version footer:** `v1.2 | January 2026`
- **Current structure:** Standard 10-section format + extra Regulatory Requirements section after Verification Criteria
- **Existing admonitions:** `!!! info "Updated February 2026"` in Regulatory Requirements section
- **Dataverse relevance:** None — this control focuses on Microsoft Purview Communication Compliance, not Dataverse audit events
- **Audit events mentioned:** `CopilotInteraction`, `CopilotForM365Interaction`, `AgentInteraction`, `CopilotChat`, `TeamsAIInteraction` — all M365 audit events, not Dataverse

**What needs to change (FCR-03):**
- Review confirms **no changes needed** — Control 1.10 monitors M365 Copilot communication compliance through Purview, not Dataverse audit events. The Dataverse deprecation does not affect this control's guidance.
- Document this finding in the plan as "reviewed, no changes required"

**Complexity:** No edit needed (review-only)

---

#### 3. `docs/controls/pillar-2-management/2.1-managed-environments.md`
- **Lines:** ~230
- **Version footer:** `v1.3 | February 2026`
- **Current structure:** Standard 10-section format + extra sections (Agent 365 Blueprint Lifecycle preview)
- **Existing admonitions:** `!!! info "Agent 365 Architecture Update"`, `!!! warning "Licensing Requirements"`, `!!! danger "Pay-As-You-Go..."`, `!!! danger "Action Required: February 2026..."`, `!!! warning "Preview Notice"`
- **Dataverse relevance:** This control covers Power Platform Managed Environments. Environment-level auditing is referenced in Control 1.7, not 2.1. The release channel updates mentioned in the todo relate to "Opt in to early access updates" guidance.
- **Release channel impact:** The todo mentions updated platform guidance for release channels. However, Control 2.1 does not currently reference early access or release channel configuration.

**What needs to change (FCR-03):**
- Review confirms **minimal or no changes needed** — Control 2.1 focuses on Managed Environment activation, sharing limits, solution checker, and usage insights. It does not reference Dataverse audit event configuration (that's in 1.7). The release channel update from the todo is not directly related to the Dataverse deprecation.
- If any cross-reference to audit completeness is found, add a brief note pointing to Control 1.7's deprecation warning. Otherwise, no changes required.

**Complexity:** No edit or trivial cross-reference addition

---

#### 4. `docs/reference/regulatory-mappings.md`
- **Lines:** 1,386
- **Version footer:** None visible (reference document)
- **Current structure:** Major sections for each regulation (FINRA 4511, FINRA 3110, FINRA AI Supervision, SEC 17a-3/4, SEC 10b-5/Reg BI, SEC Marketing Rule, SOX 302/404, GLBA 501-505, OCC 2011-12/SR 11-7)
- **Control 1.7 references:** Appears in FINRA 4511 (line 33), FINRA AI Supervision (line 163), SEC 17a-3/4 (line 219), OCC 2011-12 (line ~700+)
- **SEC 17a-4 section (lines 208-268):** Contains "Record Categories" including Agent Communications, Transaction Records, Governance Records, with retention periods. Zone 2/3 alignment subsection.

**What needs to change (FCR-02):**
- In the SEC 17a-3/4 section, add a note about the Dataverse audit event deprecation's impact on recordkeeping completeness
- Add guidance that organizations relying on Purview audit events for Dataverse field-level change records (supporting SEC 17a-4 retention) must transition to Dataverse APIs before May 2026
- Similarly, in FINRA 4511 section where Control 1.7 is referenced, add a brief note about the Dataverse API alternative
- Format: Use `!!! warning` admonition consistent with existing admonitions in this file (e.g., `!!! warning "Agent Logs as Communications"` at line 27)

**Patterns to follow:**
- Existing admonition style: `!!! warning "Title"` and `!!! note "Title"` with content
- Control cross-references: `[1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)`
- Hedged language throughout

**Complexity:** Moderate edit (add admonitions in 2 sections)

---

### Plan 01-01 Risk Assessment
- **Dependencies:** None — first plan
- **Cross-file conflicts:** None — these 4 files are exclusive to Plan 01-01
- **Risk:** Low — changes are additive warnings, not structural modifications
- **Regulatory language risk:** Medium — deprecation warnings near regulatory citations require careful hedging

---

## Plan 01-02: Agent 365 GA Readiness Review

### Requirements: FCR-04, FCR-05, FCR-06, FCR-07, FCR-08

### File Analysis

#### 1. `docs/framework/agent-365-architecture.md`
- **Lines:** 16 (redirect stub)
- **Current content:** A consolidation redirect notice pointing to `agent-identity-architecture.md`
- **Message:** "This document has been consolidated into the Unified Agent Governance document"

**What needs to change (FCR-04):**
- The architecture content now lives in `docs/framework/agent-identity-architecture.md` (1,010 lines). The meeting notes should be applied there, not to the redirect stub.
- Target file: `agent-identity-architecture.md`
- Additions needed:
  - GA readiness status: Entra Agent ID, Conditional Access for agents, M365 Admin Center Agent Settings are GA. Agent 365 Unified Control Plane and Observability remain preview (Frontier program).
  - Declarative agent deployment limitations: Export/import required for org-wide deployment; direct publish under consideration; admins can block/delete but cannot deploy org-wide from registry
  - Shadow AI discovery roadmap: Plan for post-GA includes discovering agents hosted on GCP/AWS using Entra and Defender capabilities
  - Licensing caveats: Feature-to-license mappings not finalized; current preview access doesn't reflect final licensing
  - Multi-tenant API support NOT committed; single-tenant focus
  - Agent onboarding bugs affecting activation (fixes rolling out)

- Best location: Add a new subsection under the existing architecture sections, or add meeting findings as admonitions at key points. The document already has clear GA/preview delineation in its "Additional Resources" section and preview warnings.
- The Migration Roadmap section (lines ~573-870) could receive updates about deployment limitations.
- The Overview section's `!!! warning "Preview Features"` (line 7) already distinguishes GA vs preview and should be verified for accuracy against meeting notes.

**Patterns to follow:**
- Warning admonitions for preview features: `!!! warning "Preview Features - Verify Before Implementing"`
- Info admonitions for GA features: `!!! success "Generally Available"` or `!!! info`
- Tables for feature status tracking (existing pattern in 3.8)

**Complexity:** Moderate — multiple insertions across a 1,010-line document

---

#### 2. `docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- **Lines:** ~210
- **Version footer:** `v1.2 | January 2026`
- **Current structure:** Standard 10-section format + extra sections (Agent Identity Governance, Decision Matrix, Unified Control Plane Visibility)
- **Existing admonitions:** `!!! tip "Agent 365 Architecture Update"`, `!!! warning "Service Principal Security Group Bypass"`
- **Agent 365 references:** Points to `agent-identity-architecture.md` for detailed guidance. Contains Decision Matrix for Agent ID vs. Blueprint. Cross-references `agent-365-architecture.md` (the redirect stub).

**What needs to change (FCR-05, FCR-08):**
- Update the existing `!!! tip` Agent 365 admonition to reflect current GA/preview status more precisely
- Note agent registry visibility findings: agents from Copilot Studio visible, Foundry agents at GA, declarative agents appear but lack org-wide deployment
- Add note about admin deployment constraints (cannot deploy declarative agents org-wide from registry)
- Update preview admonition to reflect GA timeline for Agent 365 features
- Fix cross-reference to `agent-365-architecture.md` — this is now a redirect; consider pointing directly to `agent-identity-architecture.md`

**Complexity:** Simple-moderate (update admonitions, fix cross-reference)

---

#### 3. `docs/controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- **Lines:** 278
- **Version footer:** `v1.2 | January 2026`
- **Current structure:** Standard 10-section format + extra sections (AI Agent Autonomy Levels, FINRA Rule 2210, Rule 3120 Testing, Entra Agent ID Sponsorship Alignment with `!!! info "Preview Feature - Frontier Program"`)
- **Existing Agent 365 admonition:** `!!! tip "Agent 365 Architecture Update"` about Entra Agent ID sponsorship model
- **Sponsorship section:** Has `!!! info "Preview Feature - Frontier Program"` — needs check against GA status

**What needs to change (FCR-05, FCR-08):**
- Verify Entra Agent ID sponsorship preview admonition — meeting notes confirm sponsorship model. Need to check if sponsorship has moved to GA or remains preview.
- Per the architecture document, Entra Agent ID is listed as GA. Sponsorship model may be GA. If so, update `!!! info "Preview Feature - Frontier Program"` to GA status.
- Add note about observability integration status for supervision evidence collection
- Cross-reference to `agent-365-architecture.md` should point to `agent-identity-architecture.md`

**Complexity:** Simple (update preview admonition, fix cross-reference)

---

#### 4. `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- **Lines:** 393
- **Version footer:** `v1.3 | February 2026`
- **Current structure:** Standard 10-section format + extensive extra sections (Preview Status, Terminology, January 2026 Enhancements, AI Feature Access Control zones/exclusion groups/deployment groups, PPAC AI Feature Controls, Conversational Transcript, DLP for Publishing, Agent Essentials Preview)
- **Preview status table (lines 14-22):** Shows Copilot Hub, Agent Registry, MCP Server Governance all as "Preview" with "Expected GA: TBA"

**What needs to change (FCR-05, FCR-08):**
- Update Preview Feature Status Tracking table with GA timeline signals from meeting notes
- Note Agent Registry visibility findings (Copilot Studio visible, Foundry at GA, declarative agents limited)
- Add note about admin deployment constraints
- Update "Microsoft Agent 365 Strategic Context (Preview)" section near bottom with GA status findings
- Update preview admonitions if GA timeline is clearer

**Complexity:** Moderate (multiple admonition updates across long document)

---

#### 5. `docs/reference/role-catalog.md`
- **Lines:** ~200
- **Version footer:** `v1.2 | February 2026`
- **Current structure:** Canonical Roles tables (Entra, Purview, Power Platform, Scenario-Based), AI Governance Permission Matrix, Role Selection Guidance, Governance Roles
- **AI Administrator entry:** Listed under Entra (Identity) roles with description "Manage M365 Copilot settings, AI services, connector delegation, Copilot feature access controls, and agent governance settings"
- **Permission Matrix:** Shows AI Administrator permissions vs Global Admin, Security Admin, Power Platform Admin

**What needs to change (FCR-06):**
- Add note that Agent 365 access is currently limited to Global Administrators and AI Administrators only — no additional roles at GA
- Note that no fine-grained or read-only roles are planned for GA; Microsoft is collecting feedback
- Add this limitation to the AI Governance Permission Matrix or as an admonition
- This is additive — no existing content needs restructuring

**Patterns to follow:**
- Use `!!! note` admonition for role limitation callout
- Use table format consistent with existing Permission Matrix

**Complexity:** Simple edit (add admonition + table row or note)

---

#### 6. `docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- **Lines:** 352
- **Version footer:** Not visible in read range (likely at end)
- **Current structure:** Standard 10-section format + extensive extra sections (Virtual Governance Connectors, HTTP Endpoint Filtering, DLP for Copilot Prompts preview)
- **Existing Agent 365 admonition:** `!!! info "Agent 365 Architecture Update"` about cross-platform DLP enforcement via Purview
- **Defender references:** None directly — this control covers DLP, not Defender

**What needs to change (FCR-07):**
- Review against meeting notes on security event gaps. DLP deny events may be affected by blocked prompt visibility issues in Defender.
- If the meeting notes indicate DLP enforcement events are not consistently visible in Defender advanced hunting, add a note in the cross-platform DLP enforcement context.
- Likely a brief `!!! note` admonition about DLP deny event visibility limitations in Defender

**Complexity:** Simple edit (add brief admonition if applicable)

---

#### 7. `docs/controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- **Lines:** 308
- **Version footer:** Not visible in read range
- **Current structure:** Standard 10-section format + extra sections (Supported AI Workloads, Weekly Risk Assessments, Enhanced DSPM AI Observability preview)
- **Existing Agent 365 admonition:** `!!! note "Agent 365 Architecture Update"` about Purview DSPM integration
- **Defender references:** Line in Roles table: "Entra Security Admin | View reports and policies; Defender XDR integration with DSPM for AI observability data"

**What needs to change (FCR-07):**
- Add note about observability integration between DSPM for AI and Defender — meeting notes indicate blocked prompt visibility in Defender is inconsistent
- DSPM Activity Explorer ingests Defender agent activity events (per Related Controls reference to 1.8). If these events are inconsistent, DSPM visibility is also affected.
- Add `!!! warning` or `!!! note` about security event inconsistencies affecting DSPM Activity Explorer completeness

**Complexity:** Simple edit (add admonition)

---

#### 8. `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- **Lines:** 378
- **Version footer:** Not visible in read range
- **Current structure:** Standard 10-section format + extensive extra sections (Native Defender Integration with `!!! success "Generally Available - February 2026"`, Additional Threat Detection, Security Webhooks API, AI-Enabled Threat Patterns)
- **Existing Agent 365 admonition:** `!!! info "Agent 365 Architecture Update"` about centralized security posture dashboard
- **Defender integration:** Most detailed Defender integration of any control — covers Defender for Cloud Apps, real-time protection, advanced hunting

**What needs to change (FCR-07):**
- This is the primary control for noting security event inconsistencies
- Meeting notes: "Blocked prompt visibility in Defender is inconsistent and under review"
- Add `!!! warning` admonition in the Native Defender Integration section noting that blocked prompt events may not consistently appear in Defender advanced hunting
- Note that this is acknowledged by Microsoft and under review
- This directly affects the "Advanced Hunting" subsection's promise that "Agent data available in Defender advanced hunting queries"

**Patterns to follow:**
- `!!! warning "Known Limitation"` or `!!! warning "Security Event Visibility Gap"` style
- Hedged language: "may not consistently appear", "under review by Microsoft"

**Complexity:** Moderate edit (add warning with specific context about which events are affected)

---

### Plan 01-02 Risk Assessment
- **Dependencies:** None — files don't overlap with other plans
- **Cross-file conflicts:** None — 8 files exclusive to Plan 01-02
- **Risk:** Medium — 8 files to edit, some with complex existing structures
- **Key risk:** The redirect at `agent-365-architecture.md` means FCR-04 changes go to `agent-identity-architecture.md` instead (1,010 lines). Need careful insertion points.
- **Preview → GA transitions:** Must verify each preview admonition against confirmed GA status from meeting notes. Incorrect GA claims would be harmful.
- **Cross-reference consistency:** Multiple controls reference `agent-365-architecture.md` (the redirect). Consider whether to update those references to point to `agent-identity-architecture.md` directly, or leave the redirect in place.

**Recommendation for cross-references:** Leave the redirect in place. MkDocs will follow it. Updating all cross-references creates unnecessary churn and risk.

---

## Plan 01-03: Evaluation Framework Enhancements

### Requirements: FCR-09, FCR-10, FCR-11, FCR-12

### File Analysis

#### 1. `docs/controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md`
- **Lines:** ~210
- **Version footer:** `v1.2 | January 2026`
- **Current structure:** Standard 10-section format + extra Regulatory Requirements section
- **Test methodology:** Section 3 (Control Description) lists 6 testing approaches. Section 4 (Key Configuration Points) lists configuration items including automated testing in pre-deployment pipeline.
- **No existing evaluation framework references**

**What needs to change (FCR-09):**
- Add reference to Copilot Studio's built-in 8-step evaluation framework in the Control Description or Key Configuration Points section
- The evaluation framework's grader types (quality assessment, classification grading, capability verification) directly apply to conflict of interest testing
- Add subsection or admonition referencing the evaluation methodology as a complementary tool for automated testing
- Note that the evaluation framework supports "evidence-based confidence" and "observable, repeatable, and explainable" testing — language that aligns with FSI regulatory requirements

**Best insertion point:** After the existing Key Configuration Points, or as a new subsection within Control Description after the 6 testing approaches

**Patterns to follow:**
- `!!! tip` for tool/capability references
- Microsoft Learn link for the evaluation blog/docs
- Hedged language: "can complement", "supports", "helps validate"

**Complexity:** Simple-moderate (add subsection or admonition with evaluation framework reference)

---

#### 2. `docs/controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- **Lines:** ~190
- **Version footer:** `v1.2 | January 2026`
- **Current structure:** Standard 10-section format
- **Change management context:** Related Controls table links to 2.3 (Change Management). The control focuses on SoD, access reviews, PIM — not directly on testing or regression detection.

**What needs to change (FCR-10):**
- The todo mentions "regression detection via sequential evaluation comparisons" for Control 2.8, framing it as a change management enhancement
- However, upon analysis, Control 2.8 is about **Access Control and Segregation of Duties**, not Change Management. The todo's reference to "Control 2.8 (Change Management)" appears to be a mislabeling — Change Management is actually Control 2.3.
- The evaluation framework's regression detection concept better fits **Control 2.5 (Testing, Validation, and Quality Assurance)** or **Control 2.3 (Change Management)**
- For 2.8 specifically: could add a reference to using evaluation framework comparisons to validate that access control changes don't introduce regressions in agent behavior

**Recommended approach:** Add a brief note in the Verification Criteria or Key Configuration Points about using sequential evaluations to validate that SoD or access changes don't degrade agent behavior. Keep it minimal since the primary evaluation framework references belong in 2.18 and potentially 2.5.

**Complexity:** Simple edit (brief addition)

---

#### 3. `docs/controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- **Lines:** ~230
- **Version footer:** `v1.2 | January 2026`
- **Current structure:** Standard 10-section format + extra sections (Programmatic Inventory Access, Agent Essentials preview, Environment Provisioning Registration)
- **Monitoring context:** Zone-Specific Requirements define review cadences (monthly/weekly/daily). No existing evaluation or quality monitoring references.

**What needs to change (FCR-11):**
- Add reference to comparative monitoring pattern — using sequential evaluations to track agent quality metrics over time as part of inventory metadata
- The evaluation framework's "Comparative Monitoring" step (step 8) aligns with the control's ongoing monitoring requirements
- Best insertion: Add quality monitoring metadata fields to the inventory recommendations, or add a subsection about tracking agent quality trends
- Could add an evaluation score or quality metric as recommended inventory metadata

**Patterns to follow:**
- Table format for metadata fields
- `!!! tip` for recommended practices

**Complexity:** Simple edit (add recommended metadata field or brief subsection)

---

#### 4. `docs/playbooks/control-implementations/2.18/verification-testing.md`
- **Lines:** ~110
- **Version footer:** `January 2026`
- **Current structure:** Manual Verification Steps (5 tests), Test Cases table (7 test cases), Evidence Collection Checklist, Evidence Artifact Naming, Attestation Statement Template
- **No evaluation framework references**

**What needs to change (FCR-12):**
- Add an evaluation methodology guidance section — this is the most significant addition in Plan 01-03
- Include guidance on using Copilot Studio's evaluation framework for COI testing:
  - Step-by-step methodology aligned with the 8-step framework
  - Scenario definition for COI-specific evaluation
  - Grader configuration for proprietary bias, commission bias, suitability
  - Using real user data vs. synthetic test cases
  - Comparative monitoring for regression detection across agent updates
- Add new test cases to the Test Cases table for evaluation-based testing
- Add evidence collection items for evaluation results

**Best insertion point:** After the existing Test Cases section, before Evidence Collection

**Patterns to follow:**
- Manual Verification Steps format: numbered steps with **EXPECTED** results
- Test Cases table format: `| Test ID | Scenario | Expected Result | Pass/Fail |`
- Evidence naming: `Control-2.18_[ArtifactType]_[YYYYMMDD].[ext]`

**Complexity:** Significant new content (new section with methodology guidance)

---

### Plan 01-03 Risk Assessment
- **Dependencies:** None — files don't overlap with other plans
- **Cross-file conflicts:** None — 4 files exclusive to Plan 01-03
- **Risk:** Low-Medium — mostly additive content
- **Key risk:** The todo references "Control 2.8 (Change Management)" which is actually "Access Control and SoD." The evaluation framework's regression detection is a loose fit for 2.8; changes should be minimal and focused.
- **Evaluation feature GA status:** Must verify whether Copilot Studio evaluation framework is GA or preview before referencing. If preview, use appropriate admonition.

---

## Plan 01-04: Multi-Source Governance Agent Investigation

### Requirements: FCR-13, FCR-14

### File Analysis

No existing files to modify. This plan produces a new investigation document.

**Output location:** `.planning/phases/01-parallel-documentation-updates/` or `.planning/research/`

**Source material to analyze:**
- Todo file describes 3 options (A: MCP Server, B: Copilot Studio Agent, C: Hybrid)
- Key questions: overkill assessment, GitHub repos as knowledge source, Learn MCP server value, regulatory site access, build vs. buy, maintenance burden
- Target users: M365 admins, compliance officers, security teams

**What needs to be produced (FCR-13, FCR-14):**
- Investigation report with:
  - Options A/B/C analysis with pros/cons
  - Clear build/don't-build/defer recommendation
  - If build or defer: estimated effort, maintenance cost, recommended approach
  - Prototype feasibility assessment
  - Citation quality analysis

**Patterns to follow:**
- Use `.planning/` artifact format with YAML frontmatter
- Markdown document with clear recommendation section

**Complexity:** Significant new content (investigation report), but no existing files to modify

---

### Plan 01-04 Risk Assessment
- **Dependencies:** None
- **Cross-file conflicts:** None — creates new artifact only
- **Risk:** Low — no framework changes, pure investigation output
- **Key risk:** Recommendation quality depends on current MCP server ecosystem maturity assessment

---

## Cross-Cutting Patterns

### Admonition Styles Used in Framework

| Type | MkDocs Syntax | Usage Pattern |
|------|---------------|---------------|
| Info | `!!! info "Title"` | GA features, updates, clarifications |
| Warning | `!!! warning "Title"` | Preview features, known limitations, deprecations |
| Danger | `!!! danger "Title"` | Critical deadlines, breaking changes |
| Tip | `!!! tip "Title"` | Solutions, automation, best practices |
| Note | `!!! note "Title"` | Terminology, minor clarifications |
| Success | `!!! success "Title"` | GA announcements (used in 1.8 for Defender GA) |

**For deprecation warnings:** Use `!!! warning` (consistent with existing "Agent Logs as Communications" warning in 1.7 and "Licensing Consideration" in 1.8)

**For critical deadlines:** Use `!!! danger` (consistent with "Action Required: February 2026" in 2.1)

### Cross-Reference Formats

- **Inter-pillar:** `[X.X - Control Name](../pillar-N-name/X.X-control-name.md)`
- **Same-pillar:** `[X.X - Control Name](X.X-control-name.md)`
- **Framework docs:** `[Document Name](../../framework/document-name.md)`
- **Playbooks:** `[Playbook Name](../../playbooks/control-implementations/X.X/playbook-name.md)`

### Role Naming Conventions (Canonical)

| Canonical Name | Do NOT Use |
|----------------|-----------|
| Entra Global Admin | Global Administrator |
| AI Administrator | Microsoft 365 AI Administrator |
| Entra Security Admin | Security Administrator, Defender XDR Admin |
| Power Platform Admin | Power Apps Admin |
| Purview Compliance Admin | Compliance Administrator |

### Version Footer Format

```markdown
*Updated: February 2026 | Version: v1.X | UI Verification Status: Current*
```

Update month to "February 2026" for all modified files. Increment minor version (e.g., v1.2 → v1.3) if substantive content added.

### Language Rules (Mandatory)

| Prohibited | Use Instead |
|-----------|-------------|
| "ensures compliance" | "supports compliance with" |
| "guarantees" | "helps meet" |
| "will prevent" | "helps prevent" |
| "eliminates risk" | "helps reduce risk" |

---

## File Inventory Summary

### Plan 01-01 (Dataverse Deprecation) — 4 files

| File | Lines | Action | Complexity |
|------|-------|--------|------------|
| `1.7-comprehensive-audit-logging-and-compliance.md` | 261 | Add deprecation warning admonition | Simple |
| `1.10-communication-compliance-monitoring.md` | ~175 | Review only — no changes needed | None |
| `2.1-managed-environments.md` | ~230 | Review only — no/minimal changes | None-Trivial |
| `regulatory-mappings.md` | 1,386 | Add deprecation notes in SEC 17a-4 and FINRA 4511 sections | Moderate |

### Plan 01-02 (Agent 365 GA) — 8 files

| File | Lines | Action | Complexity |
|------|-------|--------|------------|
| `agent-identity-architecture.md` | 1,010 | Add meeting findings (GA status, limitations, roadmap) | Moderate |
| `1.11-conditional-access-and-phishing-resistant-mfa.md` | ~210 | Update admonitions, fix cross-reference | Simple-Moderate |
| `2.12-supervision-and-oversight-finra-rule-3110.md` | 278 | Update preview admonition if GA confirmed | Simple |
| `3.8-copilot-hub-and-governance-dashboard.md` | 393 | Update preview status table, add deployment constraints | Moderate |
| `role-catalog.md` | ~200 | Add AI Admin role limitation note | Simple |
| `1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` | 352 | Add DLP event visibility note if applicable | Simple |
| `1.6-microsoft-purview-dspm-for-ai.md` | 308 | Add security event consistency note | Simple |
| `1.8-runtime-protection-and-external-threat-detection.md` | 378 | Add blocked prompt visibility warning | Moderate |

### Plan 01-03 (Evaluation Framework) — 4 files

| File | Lines | Action | Complexity |
|------|-------|--------|------------|
| `2.18-automated-conflict-of-interest-testing.md` | ~210 | Add evaluation framework reference | Simple-Moderate |
| `2.8-access-control-and-segregation-of-duties.md` | ~190 | Add brief regression detection note | Simple |
| `3.1-agent-inventory-and-metadata-management.md` | ~230 | Add quality monitoring metadata reference | Simple |
| `verification-testing.md` (playbook 2.18) | ~110 | Add evaluation methodology section | Significant |

### Plan 01-04 (Multi-Source Investigation) — 0 existing files

| File | Lines | Action | Complexity |
|------|-------|--------|------------|
| (new investigation report) | N/A | Create investigation document | Significant |

**Total: 16 files to edit/review, 1 new file to create**
**True edits required: 12 files** (4 files review-only or no changes)

---

## Dependency Graph

```
Plan 01-01 ──┐
Plan 01-02 ──┤── All parallel (Wave 1) ──→ Phase 2: Validation
Plan 01-03 ──┤
Plan 01-04 ──┘
```

No inter-plan dependencies. No file overlaps. All plans can execute simultaneously.

---

## Key Findings and Recommendations

### Finding 1: agent-365-architecture.md Is a Redirect
The FCR-04 target file `agent-365-architecture.md` is a 16-line redirect stub pointing to `agent-identity-architecture.md` (1,010 lines). **All FCR-04 changes must target `agent-identity-architecture.md`.**

### Finding 2: Control 1.10 and 2.1 Likely Need No Changes
FCR-03 requires review of Controls 1.10 and 2.1 for Dataverse deprecation impact. Analysis shows:
- **Control 1.10** monitors M365 Communication Compliance — uses Purview audit events for M365 Copilot, not Dataverse. No Dataverse dependency found.
- **Control 2.1** manages Power Platform Managed Environments — covers sharing, solution checker, usage insights. Audit configuration is documented in Control 1.7. No direct Dataverse audit event dependency.

**Recommendation:** Document "reviewed, no changes required" for both in the execution plan.

### Finding 3: Todo Mislabels Control 2.8 as "Change Management"
The evaluation framework todo references "Control 2.8 (Change Management)" but Control 2.8 is actually "Access Control and Segregation of Duties." Change Management is Control 2.3. The regression detection concept is a loose fit for 2.8. Keep the 2.8 edit minimal and focused on how sequential evaluations can validate that access control changes don't regress agent behavior.

### Finding 4: Entra Agent ID GA Status Needs Verification
The architecture document states Entra Agent ID is GA, and the 2.12 control has a "Preview Feature - Frontier Program" admonition for sponsorship. The meeting notes should clarify whether sponsorship specifically has reached GA. If so, the admonition in 2.12 should be updated from preview to GA.

### Finding 5: Cross-References to Redirect Should Be Left Alone
Multiple controls reference `agent-365-architecture.md`. Since this file contains a valid redirect to `agent-identity-architecture.md`, MkDocs handles navigation correctly. Updating all cross-references creates unnecessary churn. **Leave redirect cross-references as-is.**

### Finding 6: Evaluation Framework GA Status Unknown
The todo asks to reference Copilot Studio's evaluation framework but doesn't confirm whether it's GA or preview. The blog post describes it, but GA status should be verified. If preview, all references must include appropriate preview admonitions.

---

*Research completed: 2026-02-10*
*Researcher: GitHub Copilot*
*Ready for plan creation*
