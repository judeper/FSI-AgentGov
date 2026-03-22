# Control 2.25: Microsoft Agent 365 — Admin Center Governance Console - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Agent 365 overview page
**Portal Path:** M365 admin center -> Agents -> Overview
**What to capture:**
- Hero metrics visible
- Pending Requests governance card
- Ownerless Agents governance card

### Screenshot 2: Publishing approval workflow
**Portal Path:** M365 admin center -> Agents -> Requests or publish wizard
**What to capture:**
- Approval queue entry
- Approver context
- Governance template selection step

### Screenshot 3: Governance template configuration
**Portal Path:** M365 admin center -> Agents -> Governance templates
**What to capture:**
- Default and custom templates
- Bundled controls/policies
- Template assignment options

### Screenshot 4: Researcher Computer Use settings
**Portal Path:** M365 admin center -> Agents -> Researcher -> Computer Use
**What to capture:**
- Access scope setting
- Work data toggle
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

Store screenshots in the `docs/images/2.25/` directory for local maintainer verification.

---

[Back to Control 2.25](../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
