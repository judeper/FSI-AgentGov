# Control 3.13: Agent 365 Admin Center Analytics and Reporting - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Analytics overview dashboard
**Portal Path:** M365 admin center -> Agents -> Overview
**What to capture:**
- Agent Registry, Active Users, Agent Run-time, and Registry Sync hero metrics
- Pending Requests card (three newest requests only); capture the full Requests list separately for queue and SLA evidence
- Agents without Owners card
- Agents with Exceptions actionable view

### Screenshot 2: Agents by publisher/platform analytics
**Portal Path:** M365 admin center -> Agents -> Overview
**What to capture:**
- Publisher breakdown
- Platform distribution
- Trend visual for active users

### Screenshot 3: Inventory export action
**Portal Path:** M365 admin center -> Agents -> All agents -> Registry
**What to capture:**
- Export button
- Agent list columns
- Evidence-friendly point-in-time view
- Selected All agents / Filtered agents scope, actual CSV/Excel format, and any supplemental firm-required fields absent from the native export

### Screenshot 4: Researcher with Computer Use reporting
**Portal Path:** M365 admin center -> Agents -> Researcher -> Computer Use
**What to capture:**
- Allowed websites or restrictions
- User scope
- Reporting or configuration state

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
3.13_Screenshot-[Number]_[Description]_[YYYYMMDD].png
```

Store screenshots under `maintainers-local/tenant-evidence/`; retain only this checklist in the repository. Documentation cross-check: 2026-11-09; no screenshots or tenant/UI execution were verified.

---

[Back to Control 3.13](../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md)
