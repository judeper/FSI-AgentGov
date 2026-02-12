# v16 Research: Pitfalls & Risks — Unrestricted Agent Sharing Detector

**Dimension:** Pitfalls & Risks
**Created:** 2026-02-12

## Risk Register

### Risk 1: BAP API Documentation Gap (Medium)

**Description:** The spec references BAP API endpoints for per-agent sharing principals (GET and PATCH) that are not publicly documented on Microsoft Learn. Environment-level BAP APIs are well-documented; per-agent sharing APIs are not.

**Impact:** If endpoints change or are removed, detection and remediation break.

**Mitigation:**
- Spec mandates using these endpoints as-is — follow literally
- Document API endpoints and version in deployment guide
- Lab-grade implementation allows for rapid iteration if APIs change
- Fallback: Dataverse OData `chatbots` entity for enumeration; sharing principals may require UI-based workaround

**Severity:** Medium — lab-grade reduces production impact

### Risk 2: Severity Option Set Mapping (Low)

**Description:** Spec uses Critical/High/Medium/Low severity but framework uses `fsi_acv_severity` with Passed/Warning/GracePeriod/Failed/Error values. Mapping is:
- Critical → Failed (4)
- High → Error (5)
- Medium → Warning (2)
- Low → GracePeriod (3)

**Impact:** Reporting may be confusing if labels don't map intuitively (e.g., "Error" meaning "High severity" rather than "system error").

**Mitigation:**
- Document mapping explicitly in deployment guide
- Solution documentation uses spec terminology (Critical/High/Medium/Low) with stored values in parentheses
- Expandable: can create `fsi_UASD_severity` later if mapping causes confusion

### Risk 3: AAM Status Discrepancy (Low)

**Description:** Agent Access Governance Monitor listed as "Work In Progress" in solutions-index.md but "Shipped" in milestones, STATE, and PROJECT.

**Impact:** Confusion about UASD's relationship to AAM.

**Mitigation:** Reconcile status in Phase 5. Decision: complementary solutions (AAM = environment-level, UASD = per-agent).

### Risk 4: No Agent Inventory Table (Low)

**Description:** Spec references `jd_agentvault_id` lookup, but Control 3.1 agent inventory is CSV/SharePoint-based, not Dataverse.

**Impact:** No foreign key integrity for agent references.

**Mitigation:** Use inline agent identity fields (`fsi_agent_id`, `fsi_agent_name`, `fsi_environment_id`). Expandable to Dataverse agent registry later.

### Risk 5: Remediation Overwrites All Principals (Medium)

**Description:** BAP PATCH endpoint replaces ALL existing principals (spec Section 3.3). This is destructive — a remediation error could lock out legitimate users.

**Impact:** Incorrect remediation could break agent access for authorized users.

**Mitigation:**
- Default mode is Approval for ALL zones (Non-Negotiable Rule #5)
- Automatic remediation only for PUBLIC_INTERNET_LINK
- Remediation builds principal array from approved security groups only
- Empty array = owner-only access (used only when explicitly approved)
- Deployment guide must warn about destructive nature of PATCH

### Risk 6: Cross-Tenant Detection False Positives (Low)

**Description:** Multi-tenant organizations (e.g., post-merger) may legitimately have cross-tenant principals.

**Impact:** False positive `CROSS_TENANT_ACCESS` violations.

**Mitigation:** Exception Manager app provides business justification and dual approval for legitimate cross-tenant sharing. `fsi_UASD_HomeTenantId` environment variable defines "home" tenant.

### Risk 7: Canvas App Complexity (Medium)

**Description:** Exception Manager app requires dual approval workflow, expiration enforcement, agent lookup — non-trivial for a Canvas App.

**Impact:** Development time may exceed estimates.

**Mitigation:** Lab-grade implementation. Start with minimal viable app (exception submission + status view). Dual approval handled by Power Automate flow, not app logic.

## Lessons Learned from Prior Milestones

| Milestone | Lesson | Application to v16 |
|-----------|--------|-------------------|
| v4 (ACV) | Dual validation strategy prevents false positives from audit lag | UASD should log raw principals JSON for audit trail (`fsi_sharedwith_json`) |
| v6 (AAM) | Environment-level vs per-agent distinction is critical | UASD explicitly scoped to per-agent; AAM remains for environment-level |
| v9 (Integration) | Option set reuse across solutions requires explicit check-and-reference logic | Schema script must check for existing `fsi_acv_zone` / `fsi_acv_severity` before creating |
| v10 (CAA) | Idempotent deployment scripts save debugging time | All 5 UASD scripts designed for safe re-run |
| v14 (SSPM) | Manual attestation items create audit gaps | UASD automates what was manual attestation for Control 1.1 SSPM items |

## Overall Risk Assessment: Low-Medium

Lab-grade implementation reduces all risks. BAP API documentation gap is the primary concern but mitigated by spec-mandated endpoint usage. All other risks have proven mitigation patterns from prior milestones.
