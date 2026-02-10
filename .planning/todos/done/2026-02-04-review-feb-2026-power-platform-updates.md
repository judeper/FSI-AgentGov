---
created: 2026-02-04T19:03
title: Review February 2026 Power Platform and Copilot Studio updates
area: docs
files:
  - docs/controls/pillar-1-security/control-1.7.md
  - docs/controls/pillar-1-security/control-1.10.md
  - docs/controls/pillar-2-management/control-2.1.md
  - docs/reference/regulatory-mappings.md
  - scripts/config/monitoring-config.yaml
---

## Problem

Microsoft published multiple new and updated articles for Power Platform and Copilot Studio in February 2026. Need to review whether these updates affect the FSI-AgentGov framework, particularly a CRITICAL deprecation announcement for Dataverse audit events.

### CRITICAL - Dataverse Purview Audit Deprecation (May 2026)

**Starting May 2026:** Dataverse will no longer include before-and-after field change values in audit events sent to Microsoft Purview.

**Impact on framework:**
- Control 1.7 (Audit Trail Requirements) - May need update for how to retrieve detailed audit data
- Control 1.10 (Records Retention) - Audit trail completeness may be affected
- Regulatory-mappings.md - SEC 17a-4 / FINRA 4511 recordkeeping implications
- Solutions using Purview audit integration may need alternative approach

**Required action:** Customers must retrieve detailed audit data from Dataverse APIs instead of Purview.

### New Solution Ideas (Reference Architectures)

1. **Customer Support Agent** - Dynamics 365/Dataverse/SharePoint integration
   - Architecture diagram, workflows, escalation strategies
   - Reliability, operational excellence, performance, responsible AI

2. **Onboarding Agent** - New hire experience
   - Candidate data retrieval, Q&A, personalized learning plans
   - Progress monitoring workflows

3. **Anomaly Detection Agent** - New entry in solution ideas table

4. **Travel Concierge** - Updated with agent instructions section

5. **Ticket Management System** - Updated with agent instructions

### Updated Platform Guidance

1. **Opt in to early access updates** - Rewrote for release channels
   - Environment setup, navigation, validation checklist
   - FAQ on ALM strategies and rollback options

2. **Deleted records (preview)** - Renamed from "Recycle Bin"
   - 1-30 day retention clarification
   - Storage management guidance

### Framework touchpoints to verify:

- **Control 1.7** (Audit Trail) - Dataverse audit event deprecation is CRITICAL
- **Control 2.1** (Environment Management) - Release channels may affect guidance
- **Learn Monitor URLs** - May need new URLs added for:
  - Customer support agent reference architecture
  - Onboarding agent solution idea
  - Updated early access/release channel docs
- **Solutions index** - Reference architectures may inspire new FSI solutions

## Solution

1. **Immediate (before May 2026):** Add warning to Control 1.7 about Dataverse audit deprecation and alternative approach using Dataverse APIs
2. **Near-term:** Review reference architectures for FSI applicability
3. **Ongoing:** Add new Learn URLs to monitoring config if relevant to framework
4. **Consider:** Whether "Deleted records" rename affects any framework references
