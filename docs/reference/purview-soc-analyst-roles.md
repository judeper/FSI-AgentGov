# SOC Analyst — Purview RBAC Role Matrix

Least-privilege Microsoft Purview role assignments for Security Operations Center (SOC) analysts performing AI agent monitoring, DLP triage, and compliance investigation in FSI environments.

---

## Purpose

SOC analysts in financial services organizations require read-only and investigative access to multiple Microsoft Purview workloads to monitor AI agent activity, triage DLP alerts, review Copilot interactions, and support regulatory evidence collection. This document maps the specific Purview built-in roles needed for each SOC capability and provides a least-privilege role bundle suitable for FINRA, SEC, and OCC compliance environments.

For canonical role naming conventions, see the [Administrator Role Catalog](role-catalog.md).

---

## SOC Analyst Purview Role Matrix

| Capability | Required Purview Role(s) | Assignment Location | Notes |
|------------|--------------------------|---------------------|-------|
| View DLP rule match content (matched file/email body) | DLP Compliance Management + Content Explorer Content Viewer | Purview portal → Role groups | Content Explorer Content Viewer is required to see actual matched content — see [gating note](#content-explorer-content-viewer-gating-role) below |
| View DLP alerts and policy matches (metadata only) | DLP Compliance Management | Purview portal → Role groups | Without Content Explorer Content Viewer, analysts see match metadata only (policy name, count, location) — not the sensitive data itself |
| Review Copilot prompts via DSPM for AI (AI Hub) | Purview Data Security AI Viewer + Purview Data Security AI Content Viewer | Entra ID → Built-in roles | Both roles required: Viewer for dashboard access, Content Viewer for prompt/response inspection |
| Review auto-label simulation contextual matches | Information Protection Reader + Content Explorer Content Viewer | Purview portal → Role groups | Information Protection Reader provides label policy visibility; Content Viewer enables match-level inspection |
| View sensitivity labels and label analytics | Information Protection Reader | Purview portal → Role groups | Read-only access to label definitions, policies, and analytics dashboards |
| Search audit logs (Copilot usage, DLP events, agent activity) | Purview Audit Reader | Purview portal → Role groups | Provides search access to Unified Audit Log; does not grant audit configuration rights |
| View Insider Risk alerts (SOC triage) | Insider Risk Management Analyst | Purview portal → Role groups | Optional — assign only if SOC is responsible for Insider Risk alert triage |
| View Communication Compliance policy violations | Communication Compliance Analyst | Purview portal → Role groups | Optional — assign only if SOC is responsible for communication supervision triage |

---

## Least-Privilege SOC Analyst Role Bundle

The following bundle provides the minimum roles for an FSI SOC analyst performing AI agent monitoring and DLP investigation:

### Entra ID Built-in Roles

Assign via **Entra ID → Roles and administrators**:

| Role | Purpose |
|------|---------|
| Purview Data Security AI Viewer | Read-only access to DSPM for AI dashboards and reports |
| Purview Data Security AI Content Viewer | View sensitive content flagged by DSPM for AI policies |
| Purview Compliance Reader | Read-only portal access to Purview compliance features |

### Purview Portal Role Group Assignments

Assign via **Purview portal → Settings → Permissions → Role groups**:

| Role Group | Purpose |
|------------|---------|
| DLP Compliance Management | View DLP policies, alerts, and match metadata |
| Content Explorer Content Viewer | View actual matched sensitive content (the gating role — see below) |
| Information Protection Reader | View sensitivity labels, policies, and analytics |
| Purview Audit Reader | Search Unified Audit Log entries |

### Optional Additions (Scope-Dependent)

Assign only when the SOC team is responsible for these workloads:

| Role Group | When to Assign |
|------------|----------------|
| Insider Risk Management Analyst | SOC performs Insider Risk alert triage |
| Communication Compliance Analyst | SOC performs communication supervision triage |

---

## Content Explorer Content Viewer — Gating Role

!!! warning "Frequently Missed: Content Viewing Requires an Explicit Role"
    **Content Explorer Content Viewer** is the gating role that controls whether an analyst can see the actual sensitive data body (the matched text, document, or email content) — or only the policy match metadata (policy name, match count, content location).

    Without this role, a SOC analyst assigned to DLP Compliance Management can see *that* a DLP rule matched and *where*, but cannot see *what* was matched. This distinction is critical in FSI environments where:

    - Investigators need to verify whether a match is a true positive before escalating
    - Regulatory examiners may ask for evidence of review depth
    - Separation of duties may require restricting content access to a subset of SOC staff

    **Recommendation:** Assign Content Explorer Content Viewer to SOC analysts who perform DLP investigation and triage. For organizations requiring additional separation of duties, consider restricting this role to senior SOC analysts while providing metadata-only access to Tier 1 analysts.

    This role is referenced in the framework as **Purview DLP Content Viewer** — see the [Administrator Role Catalog](role-catalog.md) for canonical naming.

---

## Regulatory Alignment

| Regulation | How This Role Bundle Supports Compliance |
|------------|------------------------------------------|
| FINRA 4511 | Audit Reader access supports record-keeping supervision and evidence collection |
| FINRA 3110 | Least-privilege role assignments support supervisory procedure requirements |
| SEC 17a-3/4 | DLP and audit access aids in electronic record preservation oversight |
| GLBA 501(b) | Information Protection Reader supports data protection monitoring |
| OCC Bulletin 2026-13 (formerly OCC 2011-12) | DSPM for AI roles aid in model risk monitoring for AI agent workloads |

!!! note "Implementation Caveat"
    Role assignments alone do not satisfy regulatory requirements. Organizations should document SOC role assignments in their Written Supervisory Procedures (WSPs), implement Entra Privileged Identity Management (PIM) for time-bound access where appropriate, and verify role effectiveness through periodic access reviews.

---

## Related Controls

| Control | Relationship |
|---------|--------------|
| [1.24 - Defender AI Security Posture Management](../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | SOC Analyst monitors AI security alerts and investigates incidents |
| [1.25 - MIME Type Restrictions](../controls/pillar-1-security/1.25-mime-type-restrictions.md) | SOC Analyst monitors Sentinel analytics rules for file upload anomalies |
| [1.5 - DLP and Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP policy management requiring SOC investigation access |
| [1.6 - DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI monitoring requiring AI Viewer/Content Viewer roles |
| [1.10 - Communication Compliance](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Communication supervision triage (optional SOC scope) |

---

## External References

- [Microsoft Learn: Permissions in Microsoft Purview](https://learn.microsoft.com/en-us/purview/microsoft-365-compliance-center-permissions) — authoritative Purview permissions documentation
- [Microsoft Learn: Content Explorer](https://learn.microsoft.com/en-us/purview/data-classification-content-explorer) — Content Explorer access requirements and role prerequisites

---

*Updated: April 2026 | Version: v1.3 | Framework: FSI Agent Governance*
