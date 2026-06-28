# Pillar 3: Reporting Controls

Provide visibility, accountability, and metrics for agent governance.

## Overview

Pillar 3 establishes the reporting and monitoring capabilities required to maintain oversight of AI agents across the organization. These 14 controls ensure that governance teams, compliance officers, and regulators have visibility into agent inventory, usage patterns, security posture, incident response, analytics, observability telemetry, and hallucination feedback—essential for demonstrating effective supervision to examiners.

**Primary Regulatory Alignment:** FINRA 3110 (supervision), FINRA 4511 (recordkeeping), SEC 17a-3/4 (records)

!!! danger "⚠️ Action Required by July 1, 2026 — Agent 365 Required for AI Agent Inventory"
    After **2026-07-01**, Defender for Cloud Apps alone no longer provides AI Agent Inventory. **Agent 365** (or Microsoft 365 E7 / Frontier Suite) is required to retain AI Agent Inventory visibility. Third-party cloud agent discovery via Defender for Cloud connectors also ends on this date; transition to Registry sync (Preview) before the deadline. See [Control 3.7](3.7-ppac-security-posture-assessment.md) and [Control 3.6](3.6-orphaned-agent-detection-and-remediation.md) for full details.

!!! note "Retention Period Guidance for Pillar 3 Controls"
    Retention periods cited across Pillar 3 controls reflect the **regulatory minimum floors**, not firm policy maxima. FINRA Rule 4511 and SEC Rule 17a-4 set a **6-year minimum** for most broker-dealer books-and-records (with the first 3 years readily accessible). Periods vary by record class — some classes carry shorter requirements (e.g., 3 years under SEC 17a-3) and some firms configure 7 years as an internal buffer. Where a control states a specific period, treat it as the floor for that record class. **Always verify record-class-specific requirements with qualified counsel** before finalizing retention policy configuration.

**Control Categories:**

| Category | Controls | Focus |
|----------|----------|-------|
| Inventory & Tracking | 3.1, 3.5-3.6 | Agent registry, cost tracking, orphan detection |
| Activity Monitoring | 3.2, 3.8 | Usage analytics, Copilot Hub |
| Compliance Reporting | 3.3-3.4 | Regulatory reporting, incident response |
| Security Operations | 3.7, 3.9 | PPAC security posture, Sentinel integration |
| Quality Feedback | 3.10 | Hallucination feedback loop |
| Governance Analytics & Enforcement | 3.11-3.14 | Centralized inventory enforcement, exception management, admin center analytics, observability telemetry |

## Controls
- [3.1 Agent Inventory and Metadata Management](3.1-agent-inventory-and-metadata-management.md)
- [3.2 Usage Analytics and Activity Monitoring](3.2-usage-analytics-and-activity-monitoring.md)
- [3.3 Compliance and Regulatory Reporting](3.3-compliance-and-regulatory-reporting.md)
- [3.4 Incident Reporting and Root Cause Analysis](3.4-incident-reporting-and-root-cause-analysis.md)
- [3.5 Cost Allocation and Budget Tracking](3.5-cost-allocation-and-budget-tracking.md)
- [3.6 Orphaned Agent Detection and Remediation](3.6-orphaned-agent-detection-and-remediation.md)
- [3.7 PPAC Security Posture Assessment](3.7-ppac-security-posture-assessment.md)
- [3.8 Copilot Hub](3.8-copilot-hub-and-governance-dashboard.md)
- [3.9 Microsoft Sentinel Integration](3.9-microsoft-sentinel-integration.md)
- [3.10 Hallucination Feedback Loop](3.10-hallucination-feedback-loop.md)
- [3.11 Centralized Agent Inventory Enforcement](3.11-centralized-agent-inventory-enforcement.md)
- [3.12 Agent Governance Exception and Override Management](3.12-agent-governance-exception-and-override-management.md)
- [3.13 Agent 365 Admin Center Analytics and Reporting](3.13-agent-365-admin-center-analytics.md)
- [3.14 Agent 365 Observability SDK and Custom Agent Telemetry](3.14-agent-365-observability-sdk.md)

---

*FSI Agent Governance Framework v1.6.2 - May 2026*
