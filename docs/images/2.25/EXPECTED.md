# Control 2.25: Microsoft Agent 365 — Admin Center Governance Console - Screenshot Specifications

**Last Verified:** 2026-11-09 (documentation review only; screenshots not captured).

## Required Screenshots

### Screenshot 1: Agent 365 overview page
**Portal Path:** M365 admin center -> Agents -> Overview
**What to capture:**
- Agent registry, Active users, Agent run-time, and Registry sync visible
- Agents with exceptions count/view (not an Exception Rate hero card)
- Pending Requests governance card
- Ownerless Agents governance card

### Screenshot 2: Publishing approval workflow
**Portal Path:** M365 admin center -> Agents -> All agents -> Requests -> Pending review -> Publish to store
**What to capture:**
- Approval queue entry
- Approver context
- Governance template selection step

### Screenshot 3: Governance template configuration
**Portal Path:** M365 admin center -> Agents -> Settings -> Security templates
**What to capture:**
- Default and custom templates
- Bundled controls/policies
- Template assignment options

### Screenshot 4: Researcher Computer Use settings
**Portal Path:** M365 admin center -> Agents -> Researcher -> Computer Use
**What to capture:**
- Access scope setting
- Admin work-data setting and user Work control (admin-enabled still requires user opt-in)
- Allowed/excluded website list

---

## Notes for Verification
- Capture from a pre-production or demo tenant when possible
- Include timestamps to demonstrate currency
- Redact tenant-specific sensitive values before retaining screenshots
- Re-verify after major Microsoft portal changes

---

## Screenshot Naming Convention

Save screenshots with the following naming format:
```
2.25_Screenshot-[Number]_[Description]_[YYYYMMDD].png
```

Store screenshots under `maintainers-local/tenant-evidence/2.25/` for local verification only; do not commit tenant screenshots. Record actual UI labels, scope, timestamp, and unresolved evidence gaps.

---

[Back to Control 2.25](../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
