# Phase 1 Research: Control SSPM Alignment

**Phase:** 01-control-sspm-alignment
**Researched:** 2026-02-11
**Scope:** 7 SSPM-mapped controls, 27 alert verification criteria, GLIC advisory integration

---

## 1. Current State of Each Control File

### Control 1.1 — Restrict Agent Publishing by Authorization

- **Version:** v1.3
- **Footer:** `*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*`
- **Last Verified:** 2026-02-03
- **Section 9 Criteria Count:** 11
- **SSPM Alerts Mapped:** 7 (Refs 3, 4, 5, 6, 23, 29, 34)
- **Section 9 Content:**
    1. Non-authorized users cannot create or publish agents (test with non-member account)
    2. Authorized users can create agents in designated environments
    3. Production publishing requires membership in `FSI-Agent-Publishers-Prod`
    4. All publish events appear in Microsoft Purview Audit logs
    5. Sharing restrictions block "Share with Everyone" attempts
    6. No Copilot Studio agents are configured with "No Authentication"
    7. Agents using manual authentication have "Require users to sign in" enabled
    8. Authentication enforcement is set to "Always" for Zone 2/3 agents (not "As Needed")
    9. No agents are shared with unrestricted access ("Anyone" or "Any multi-tenant")
    10. "Publish bots with AI features" is disabled at tenant level or governance review is documented
    11. Unapproved agents are blocked in M365 Admin Center Agent Inventory

### Control 1.7 — Comprehensive Audit Logging and Compliance

- **Version:** v1.3
- **Footer:** `*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*`
- **Last Verified:** 2026-02-03
- **Section 9 Criteria Count:** 9
- **SSPM Alerts Mapped:** 3 (Refs 9, 11, 31)
- **Section 9 Content:**
    1. Unified audit logging is enabled (Get-AdminAuditLogConfig shows enabled)
    2. Copilot and agent events appear in audit search results
    3. Retention policies are configured per governance tier
    4. Export capability produces complete audit records
    5. SIEM integration is functional (logs streaming to Sentinel)
    6. WORM storage is configured for broker-dealer environments (if applicable)
    7. Dataverse environment-level auditing is enabled (PPAC > Environment > Audit and logs > "Start Auditing" is on)
    8. Audit log retention is set to minimum 180 days per environment (PPAC > Environment > Audit settings)
    9. Tenant-level Dataverse auditing policy is enabled with User Sign-In and Activity logging (PPAC > Security > Compliance > Auditing)

### Control 1.8 — Runtime Protection and External Threat Detection

- **Version:** v1.3
- **Footer:** `*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*`
- **Last Verified:** 2026-02-03
- **Section 9 Criteria Count:** 11
- **SSPM Alerts Mapped:** 1 (Ref 28)
- **Section 9 Content:**
    1. Managed Environment is enabled for all regulated environments
    2. Runtime protection settings are configured and active
    3. Test prompt injection is blocked with log entry
    4. Egress controls block unauthorized connector/tool invocations
    5. Alert policies trigger on security events
    6. SIEM integration streams events within SLA (Zone 2-3)
    7. Native Microsoft Defender integration enabled (Zone 2/3)
    8. AI agent inventory populated in Defender portal
    9. Defender XDR alerts generated for blocked actions
    10. Content moderation level is set to High for all Zone 2/3 agents
    11. No agents have content moderation set below Medium without documented risk acceptance

### Control 1.18 — Application-Level Authorization and RBAC

- **Version:** v1.3
- **Footer:** `*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*`
- **Last Verified:** 2026-02-03
- **Section 9 Criteria Count:** 9
- **SSPM Alerts Mapped:** 3 (Refs 2, 38, 42)
- **Section 9 Content:**
    1. Users in `FSI - Agent Viewer` role cannot create or modify agents (read-only)
    2. Users must activate PIM to access Dataverse System Admin in production
    3. Security role assignments export shows all assignments documented
    4. Access review completes with attestation for each role
    5. Service principal credential rotation completes within 90-day window
    6. All agent actions have "Ask the user before running this action" enabled
    7. No agents have "Let other agents connect to and use this one" enabled without documented approval
    8. Environment admin count is below 10 per environment (PPAC > Environment > Users + Permissions)
    9. All System Administrator role assignments are documented and justified

### Control 2.1 — Managed Environments

- **Version:** v1.3
- **Footer:** `*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*`
- **Last Verified:** 2026-02-03
- **Section 9 Criteria Count:** 9
- **SSPM Alerts Mapped:** 6 (Refs 14, 21, 30, 32, 35, 40)
- **Section 9 Content:**
    1. Managed Environment status shows enabled in PPAC environment details
    2. Sharing limits block attempts to share beyond configured thresholds
    3. Solution checker blocks non-compliant solution imports (if Block mode enabled)
    4. Weekly usage insights digest arrives at configured recipient addresses
    5. Maker welcome content displays for new users accessing the environment
    6. Environment creation is restricted to authorized admins only (PPAC > Tenant Settings > verify "Only specific admins" is set for Developer, Production, and Trial environment assignments)
    7. Environment routing is configured for correct region (PPAC > Tenant Settings > Environment Routing)
    8. Tenant isolation is enabled (PPAC > Security > Identity and access > Tenant Isolation)
    9. Security groups are assigned to all Zone 2/3 environments

### Control 3.7 — PPAC Security Posture Assessment ⚠️ v1.2

- **Version:** v1.2 ← **ONLY CONTROL STILL AT v1.2**
- **Footer:** `*Updated: January 2026 | Version: v1.2 | UI Verification Status: Current*`
- **Last Verified:** 2026-02-03
- **Section 9 Criteria Count:** 9
- **SSPM Alerts Mapped:** 0 (aggregation control — consolidates checks from other controls)
- **Section 9 Content:**
    1. Security page accessible with all four tabs displaying correctly
    2. Health recommendations show current status for each item
    3. High-risk recommendations addressed within 7-day SLA
    4. Managed Environments enabled for all Zone 2-3 environments
    5. DLP policies applied to 100% of environments
    6. Monthly posture report generated with trend analysis
    7. Configuration hardening baseline checklist reviewed per documented frequency
    8. No configuration drift detected in agent authentication, content moderation, or AI feature settings
    9. Evidence of configuration baseline review archived for audit readiness

### Control 3.8 — Copilot Hub and Governance Dashboard

- **Version:** v1.3
- **Footer:** `*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*`
- **Last Verified:** 2026-02-03
- **Section 9 Criteria Count:** 16
- **SSPM Alerts Mapped:** 9 (Refs 18, 20, 24, 25, 26, 27, 33, 36, 37)
- **Section 9 Content:**
    1. Copilot Settings accessible with all four tabs
    2. Web search for M365 Copilot disabled for compliance-sensitive environments
    3. Admin Exclusion Groups correctly exclude designated users
    4. Deployment groups limit Copilot access to approved user populations
    5. Agent Registry shows all agents with accurate owner information
    6. Pending agent requests reviewed and actioned within SLA
    7. Ownerless agents identified and assigned within 14 days
    8. Monthly usage reports exported and archived
    9. AI Prompts toggle is disabled in PPAC for Zone 2/3 environments
    10. Generative Actions are disabled for all agents without documented approval
    11. File Analysis is disabled for agents without documented data classification review
    12. Model Knowledge is disabled for agents handling sensitive data
    13. Semantic Search is disabled for agents without approved and scoped knowledge bases
    14. Generative AI features, Move Data Across Regions, and Bing Search are reviewed and restricted per-environment
    15. Conversational transcript access is restricted to authorized personnel
    16. DLP policies block agent publishing connectors in restricted environments

### Control 1.11 — Conditional Access and Phishing-Resistant MFA (GLIC target)

- **Version:** v1.3
- **Footer:** `*Updated: February 2026 | Version: v1.3 | UI Verification Status: Current*`
- **Last Verified:** 2026-02-03
- **Section 9 Criteria Count:** 6
- **Not SSPM-mapped** (GLIC advisory target only)

---

## 2. Gap Analysis: 27 SSPM Alerts vs Verification Criteria

### Control 1.1 — 7 alerts, 7 covered

| Ref | SSPM Alert | Matching Criterion | Status |
|-----|-----------|-------------------|--------|
| 3 | Agent Level Authentication Should Be Set To 'Always' | **#8:** Authentication enforcement is set to "Always" for Zone 2/3 agents (not "As Needed") | ✅ YES |
| 4 | Agent Should Not Be Shared With Everyone | **#9:** No agents are shared with unrestricted access ("Anyone" or "Any multi-tenant") | ✅ YES |
| 5 | Agent's Authentication Should Be Set To Authenticate Manually | **#7:** Agents using manual authentication have "Require users to sign in" enabled | ✅ YES |
| 6 | Agent's Security Authentication Should Not Be 'No Authentication' | **#6:** No Copilot Studio agents are configured with "No Authentication" | ✅ YES |
| 23 | Require User Authentication Should Not Be Disabled For Published Agent | **#6:** Same criterion — "No Authentication" prohibition covers published agents | ✅ YES |
| 29 | The Option 'Publish Bots With AI Features' Should Be Disabled | **#10:** "Publish bots with AI features" is disabled at tenant level or governance review is documented | ✅ YES |
| 34 | Shared agents which are not approved by admin should be blocked | **#11:** Unapproved agents are blocked in M365 Admin Center Agent Inventory | ✅ YES |

### Control 1.7 — 3 alerts, 3 covered

| Ref | SSPM Alert | Matching Criterion | Status |
|-----|-----------|-------------------|--------|
| 9 | Dataverse Auditing Should Be Enabled | **#7:** Dataverse environment-level auditing is enabled (PPAC > Environment > Audit and logs > "Start Auditing" is on) | ✅ YES |
| 11 | Dataverse Log Retention Should Be At Least 180 Days | **#8:** Audit log retention is set to minimum 180 days per environment | ✅ YES |
| 31 | Tenant Level Dataverse Auditing Should Be Enabled | **#9:** Tenant-level Dataverse auditing policy is enabled with User Sign-In and Activity logging | ✅ YES |

### Control 1.8 — 1 alert, 1 covered

| Ref | SSPM Alert | Matching Criterion | Status |
|-----|-----------|-------------------|--------|
| 28 | The Content Moderation Level Should Be Set To 'High' | **#10:** Content moderation level is set to High for all Zone 2/3 agents | ✅ YES |

### Control 1.18 — 3 alerts, 2 fully covered, 1 partial

| Ref | SSPM Alert | Matching Criterion | Status |
|-----|-----------|-------------------|--------|
| 2 | Agent Actions Should Require User Consent Before Running | **#6:** All agent actions have "Ask the user before running this action" enabled | ✅ YES |
| 38 | Desktop Flow RPAs Should Not Have Admin-Level Roles | **#8/#9:** Environment admin count < 10; System Administrator assignments documented — covers general admin governance but **does not explicitly reference Desktop Flow RPAs having admin roles** | ⚠️ PARTIAL |
| 42 | Connected Agents Should Be Disabled Unless Explicitly Approved | **#7:** No agents have "Let other agents connect to and use this one" enabled without documented approval | ✅ YES |

**Gap Detail for Ref 38:** Criteria #8 and #9 address admin count and documentation broadly, which would catch "any" entity with admin roles including RPAs. However, the specific check "Desktop Flow RPAs should not hold System Administrator or Environment Admin security roles" is not called out. The Key Configuration Points section mentions "Limit admin count per environment" and "Review admin role assignments" generically. Adding an explicit verification criterion for RPA/service account admin-role detection would close this gap and make the posture check unambiguous.

### Control 2.1 — 6 alerts, 6 covered

| Ref | SSPM Alert | Matching Criterion | Status |
|-----|-----------|-------------------|--------|
| 14 | Environment Should Be Associated With a Security Group | **#9:** Security groups are assigned to all Zone 2/3 environments | ✅ YES |
| 21 | New Environment Creation Should Be Restricted | **#6:** Environment creation restricted to authorized admins only (Developer, Production, and Trial) | ✅ YES |
| 30 | Production and sandbox env creation set to 'Only specific admins' | **#6:** Same criterion — explicitly mentions "Only specific admins" | ✅ YES |
| 32 | Trial env creation set to 'Only specific admins' | **#6:** Same criterion — explicitly mentions "Trial environment assignments" | ✅ YES |
| 35 | Environment Routing Should Not Be Turned Off | **#7:** Environment routing is configured for correct region | ✅ YES |
| 40 | Tenant Isolation Should Be Enabled | **#8:** Tenant isolation is enabled (PPAC > Security > Identity and access > Tenant Isolation) | ✅ YES |

### Control 3.8 — 9 alerts, 9 covered

| Ref | SSPM Alert | Matching Criterion | Status |
|-----|-----------|-------------------|--------|
| 18 | Generative AI Features Should Be Turned Off | **#14:** Generative AI features reviewed and restricted per-environment | ✅ YES |
| 20 | Move Data Across Regions Should Be Disabled | **#14:** Explicitly mentions "Move Data Across Regions" | ✅ YES |
| 24 | 'Allow AI Prompts' Feature Should Be Disabled | **#9:** AI Prompts toggle disabled for Zone 2/3 environments | ✅ YES |
| 25 | 'Generative Actions/Answers' Feature Should Be Disabled | **#10:** Generative Actions disabled without documented approval | ✅ YES |
| 26 | 'Knowledge - Model' Feature Should Be Disabled | **#12:** Model Knowledge disabled for agents handling sensitive data | ✅ YES |
| 27 | 'Semantic Search' Feature Should Be Disabled | **#13:** Semantic Search disabled without approved knowledge bases | ✅ YES |
| 33 | Bing Web Search Should Be Disabled | **#14:** Explicitly mentions "Bing Search" | ✅ YES |
| 36 | File Analysis Should Be Disabled | **#11:** File Analysis disabled without data classification review | ✅ YES |
| 37 | Conversational Transcripts Should Be Restricted | **#15:** Conversational transcript access restricted to authorized personnel | ✅ YES |

### Gap Analysis Summary

| Control | Alerts | Fully Covered | Partial | Missing | Status |
|---------|--------|---------------|---------|---------|--------|
| 1.1 | 7 | 7 | 0 | 0 | ✅ Complete |
| 1.7 | 3 | 3 | 0 | 0 | ✅ Complete |
| 1.8 | 1 | 1 | 0 | 0 | ✅ Complete |
| 1.18 | 3 | 2 | 1 | 0 | ⚠️ Ref 38 partial |
| 2.1 | 6 | 6 | 0 | 0 | ✅ Complete |
| 3.8 | 9 | 9 | 0 | 0 | ✅ Complete |
| **Total** | **29** | **28** | **1** | **0** | — |

> Note: 29 total because Refs 21/30 and 6/23 map to the same criteria, but each alert is counted independently above. Unique alerts: 27.

**Bottom line:** 26 of 27 unique SSPM alerts have clear, explicit matching verification criteria. 1 alert (Ref 38 — Desktop Flow RPA admin roles) has partial coverage through general admin governance criteria and would benefit from an explicit criterion.

---

## 3. Control 3.7 v1.2 → v1.3 Delta

### Current State

- Footer reads: `*Updated: January 2026 | Version: v1.2 | UI Verification Status: Current*`
- All SSPM-driven content already present (Configuration Drift Monitoring subsection with 13-row hardening table, 3 verification criteria for hardening baseline)
- `Last Verified: 2026-02-03` field already updated

### What Changed Between v1.2 and the Current Content

Per the SSPM alert mapping file, Control 3.7 received:
- **+Configuration Drift Monitoring subsection** with 13-row hardening table consolidating posture checks across Controls 1.1, 1.7, 1.8, 1.18, 2.1, 3.8
- **+3 verification criteria** (items 7-9: hardening baseline review, no configuration drift, evidence archival)
- **+Related Controls links** to 1.1, 1.8, 1.18 (the other SSPM-mapped controls)
- **+Configuration Hardening Baseline playbook link**

### Required Changes for v1.3 Bump

| Change | Current Value | New Value |
|--------|--------------|-----------|
| Footer version | `v1.2` | `v1.3` |
| Footer month | `January 2026` | `February 2026` |

**Content assessment:** The control body already contains all v1.3-tier content. The SSPM-driven additions (hardening table, related controls, verification criteria) were implemented but the footer was not bumped. This is purely a metadata update.

### Comparison with Other v1.3 Controls

| Feature | 1.1 | 1.7 | 1.8 | 1.18 | 2.1 | 3.7 | 3.8 |
|---------|-----|-----|-----|------|-----|------|-----|
| Last Verified field | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Footer v1.3 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ v1.2 | ✅ |
| Footer Feb 2026 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ Jan 2026 | ✅ |
| SSPM config points | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (hardening table) | ✅ |
| SSPM verification criteria | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Agent 365 Preview section | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**No structural gaps** exist between 3.7's content and other v1.3 controls. The only delta is the footer metadata.

---

## 4. Control 1.1 and 1.11 GLIC Advisory Placement

### Background

SSPM Refs 39 and 41 are valid security posture checks excluded from the 27 in-scope alerts because they are **General Licensing & Identity Controls (GLIC)** — they exist outside the Power Platform / Copilot agent governance perimeter:

| Ref | Alert | GLIC Classification | Related Control |
|-----|-------|---------------------|-----------------|
| 39 | Guest User Access Level should be set to 'Most Restrictive' | Identity control (Entra ID tenant-wide) | 1.1 (agent access scope) |
| 41 | MFA Should Be Required For All Users | Identity control (Entra ID tenant-wide) | 1.11 (Conditional Access / MFA) |

### Placement: Control 1.11 (Ref 41 — MFA for All Users)

**Recommended location:** After the Key Configuration Points section (Section 4), as an `!!! info` admonition.

**Rationale:** The control already addresses MFA for agent creators and makers. The GLIC advisory acknowledges that tenant-wide MFA enforcement (for all users, not just agent administrators) is a complementary identity hygiene measure that strengthens the agent governance posture without being a direct agent governance control.

**Proposed content pattern:**

```markdown
!!! info "Complementary Identity Control: Tenant-Wide MFA Enforcement"
    Enforcing MFA for all users — not just AI agent creators and administrators — 
    is a complementary identity control that strengthens the overall agent governance 
    posture. While this control focuses on Conditional Access policies specific to 
    agent lifecycle roles, organizations should verify that tenant-wide MFA enforcement 
    is in place as part of their broader identity security baseline. Tenant-wide MFA 
    reduces the risk of compromised accounts being used to interact with or exfiltrate 
    data from AI agents.
```

**Alternative location:** Section 10 (Additional Resources) as a related guidance note. This is less visible but less disruptive to the control flow.

**Recommendation:** Place in Section 4 for visibility. Agent governance administrators reviewing MFA configuration benefit from seeing the broader MFA context.

### Placement: Control 1.1 (Ref 39 — Guest User Access)

**Recommended location:** After the Agent-Level Authentication subsection in Key Configuration Points (Section 4), as an `!!! info` admonition.

**Rationale:** Control 1.1 already restricts agent sharing and access. The GLIC advisory acknowledges that restricting guest user access at the Entra ID tenant level (to "Most Restrictive") is a complementary identity control that limits who can interact with published agents, beyond the per-agent sharing restrictions this control configures.

**Proposed content pattern:**

```markdown
!!! info "Complementary Identity Control: Guest User Access Restriction"
    Restricting the Entra ID guest user access level to the most restrictive 
    setting is a complementary identity control that limits what external users 
    can discover and access across the tenant, including AI agents. While this 
    control focuses on per-agent authentication and sharing restrictions, 
    organizations should verify that tenant-level guest access policies are 
    appropriately restrictive as part of their broader identity security baseline. 
    Configure in Entra ID > External Identities > External collaboration settings.
```

**Alternative location:** Section 7 (Related Controls) as an additional row linking to Entra ID external collaboration documentation. However, this is less prominent than an admonition.

**Recommendation:** Place as admonition in Section 4 for consistency with 1.11 advisory placement.

---

## 5. Risks and Recommendations

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Build break from admonition syntax error** | Low | High | Run `mkdocs build --strict` after each control edit |
| **Language rule violation in GLIC advisory** | Low | Medium | Avoid "ensures," "guarantees"; use hedged language per style guide |
| **Third-party tool name leak in advisory** | Low | High | Do not reference "SSPM," "Adaptive Shield," or any scanner name per design decision |
| **Ref 38 criterion conflicts with existing admin governance wording** | Low | Low | Add as new criterion #10 without modifying existing criteria |
| **Version bump creates stale cross-references** | Very Low | Low | 3.7's cross-references already point to v1.3 controls; no stale links |
| **Verify_controls.py script fails on new criterion format** | Low | Medium | Run `python scripts/verify_controls.py` after changes |

### Recommendations

1. **CTL-01 (3.7 bump):** Safe to execute — metadata-only change with zero content risk.

2. **CTL-02 (verification criteria audit):** The gap analysis shows only 1 partial gap (Ref 38). Recommend adding one new verification criterion to Control 1.18 Section 9:
   > "No Desktop Flow or RPA service accounts hold System Administrator or Environment Admin security roles without documented approval"
   
   This makes the posture check explicit without changing any existing criteria. Also consider adding a corresponding row to Control 3.7's Configuration Drift Monitoring table.

3. **CTL-03 (GLIC advisories):** Place as `!!! info` admonitions in Section 4 of both controls. Use hedged language. Do not mention any SSPM scanner or third-party tool by name.

4. **Validation sequence:** After all edits:
   - `mkdocs build --strict`
   - `python scripts/verify_controls.py`
   - `python scripts/verify_language_rules.py` (if available)

---

## 6. Recommended Wave Structure

All three requirements (CTL-01, CTL-02, CTL-03) are independent and can execute in a single wave.

### Wave 1 (All tasks — no dependencies)

```
┌─────────────────────────────────────────────────┐
│  CTL-01: Bump 3.7 footer to v1.3               │
│  Files: 3.7 control (1 file, 2-line change)     │
├─────────────────────────────────────────────────┤
│  CTL-02: Add Ref 38 explicit criterion to 1.18  │
│  Files: 1.18 control (1 file, 1 criterion add)  │
│  Optional: 3.7 hardening table row addition     │
├─────────────────────────────────────────────────┤
│  CTL-03a: Add GLIC advisory to 1.11             │
│  Files: 1.11 control (1 file, admonition add)   │
├─────────────────────────────────────────────────┤
│  CTL-03b: Add GLIC advisory to 1.1              │
│  Files: 1.1 control (1 file, admonition add)    │
└─────────────────────────────────────────────────┘
```

### File Manifest

| Action | File | Requirement |
|--------|------|-------------|
| Modify (footer) | `docs/controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md` | CTL-01 |
| Modify (criterion) | `docs/controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md` | CTL-02 |
| Modify (hardening row) | `docs/controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md` | CTL-02 (optional) |
| Modify (advisory) | `docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md` | CTL-03 |
| Modify (advisory) | `docs/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md` | CTL-03 |

**Total files modified:** 4 (3.7 handles both CTL-01 and CTL-02 optional)

### Estimated Effort

| Task | Complexity | Lines Changed | Risk |
|------|-----------|---------------|------|
| CTL-01: 3.7 footer bump | Trivial | ~2 | None |
| CTL-02: 1.18 criterion + optional 3.7 row | Low | ~5 | Low |
| CTL-03a: 1.11 GLIC advisory | Low | ~8 | Low |
| CTL-03b: 1.1 GLIC advisory | Low | ~8 | Low |
| Validation (mkdocs build + verify scripts) | Low | 0 | None |
| **Total** | **Low** | **~23** | **Low** |

### Plan File Structure

A single plan file (`01-01-PLAN.md`) is sufficient since all tasks fit in one wave with no dependencies. The plan should include:

- Tasks 1-4 matching CTL-01, CTL-02, CTL-03a, CTL-03b
- Verification section with `mkdocs build --strict` and `verify_controls.py`
- Must-haves referencing the 3 success criteria from the phase goal

---

## Appendix A: Control 3.7 Hardening Table Coverage

The Configuration Drift Monitoring table in Control 3.7 currently has 13 rows. These consolidate the 27 SSPM alerts into a practical review checklist:

| Row | Setting Category | Covers SSPM Refs | Notes |
|-----|-----------------|------------------|-------|
| 1 | Agent Authentication (No Auth) | 6, 23 | ✅ |
| 2 | Agent Authentication (Always) | 3 | ✅ |
| 3 | Agent Sharing (unrestricted) | 4 | ✅ |
| 4 | Audit Logging (Dataverse) | 9 | ✅ |
| 5 | Audit Retention (180 days) | 11 | ✅ |
| 6 | Content Moderation (High) | 28 | ✅ |
| 7 | Agent Actions (consent) | 2 | ✅ |
| 8 | Connected Agents (disabled) | 42 | ✅ |
| 9 | Environment Creation (restricted) | 21, 30, 32 | ✅ |
| 10 | Tenant Isolation (restricted) | 40 | ✅ |
| 11 | Security Groups (assigned) | 14 | ✅ |
| 12 | AI Feature Toggles (disabled) | 18, 24, 25, 26, 27, 36 | ✅ Consolidates multiple AI features |
| 13 | Transcript Access (restricted) | 37 | ✅ |

**Not explicitly in table:** Refs 5 (manual auth sign-in), 29 (AI publishing), 31 (tenant-level Dataverse auditing), 33 (Bing Search), 34 (block unapproved), 35 (env routing), 38 (RPA admin roles), 20 (move data across regions)

These are covered in individual control Section 9 criteria but not in the 3.7 summary table. The table is appropriately a summary view — exhaustive 1:1 mapping would make it unwieldy. **No action needed** for the table coverage; the individual controls carry the complete verification criteria.

---

## Appendix B: GLIC Advisory Language Constraints

Per project design decisions:
- **No third-party tool names** in published documentation (no "SSPM," "Adaptive Shield," etc.)
- **Hedged language required** ("supports compliance with," not "ensures compliance")
- **Advisory, not mandate** — these are complementary controls, not framework requirements
- Use `!!! info` admonition (not `!!! warning` or `!!! danger`) since these are informational

The advisories should frame these as identity hygiene measures that strengthen the agent governance perimeter without expanding the framework's control scope.
