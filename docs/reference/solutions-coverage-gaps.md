# Solutions Coverage Gap Analysis

Current-state analysis of the live companion solutions in FSI-AgentGov-Solutions against the 78-control FSI Agent Governance Framework baseline.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total controls | 78 |
| Live top-level solution folders | 33 |
| Controls with live solutions | 39 |
| Controls without live solutions | 39 |
| Overall solution coverage | 50.0% |

!!! info "Important context"
    This page tracks deployable companion solutions only. A control without a live solution may still be addressed through native Microsoft 365 and Power Platform configuration, framework playbooks, or documented process controls.

---

## Coverage by Pillar

| Pillar | Total Controls | Covered | Gaps | Coverage |
|--------|----------------|---------|------|----------|
| **Pillar 1 - Security** | 29 | 14 | 15 | 48.3% |
| **Pillar 2 - Management** | 26 | 17 | 9 | 65.4% |
| **Pillar 3 - Reporting** | 14 | 7 | 7 | 50.0% |
| **Pillar 4 - SharePoint** | 9 | 1 | 8 | 11.1% |
| **Total** | 78 | 39 | 39 | 50.0% |

---

## Current Coverage Register

| Pillar | Controls with live solutions |
|--------|------------------------------|
| **Pillar 1 - Security** | 1.1, 1.2, 1.4, 1.5, 1.7, 1.8, 1.9, 1.10, 1.11, 1.13, 1.14, 1.18, 1.23, 1.25 |
| **Pillar 2 - Management** | 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.16, 2.17, 2.18, 2.22, 2.24 |
| **Pillar 3 - Reporting** | 3.1, 3.2, 3.3, 3.4, 3.7, 3.8, 3.10 |
| **Pillar 4 - SharePoint** | 4.3 |

See [Solutions Index](solutions-index.md) for the live 33-solution catalog and the published [Solutions Control Mapping](https://judeper.github.io/FSI-AgentGov-Solutions/reference/control-mapping/) for per-control solution references.

---

## Current Gap Register

| Pillar | Controls without live solutions | Notes |
|--------|---------------------------------|-------|
| **Pillar 1 - Security** | 1.3, 1.6, 1.12, 1.15, 1.16, 1.17, 1.19, 1.20, 1.21, 1.22, 1.24, 1.26, 1.27, 1.28, 1.29 | Mix of native Microsoft configuration, SharePoint governance, and targeted automation opportunities. |
| **Pillar 2 - Management** | 2.7, 2.14, 2.15, 2.19, 2.20, 2.21, 2.23, 2.25, 2.26 | Includes process-first controls, native Agent 365 admin-center capabilities, and future automation candidates. |
| **Pillar 3 - Reporting** | 3.5, 3.6, 3.9, 3.11, 3.12, 3.13, 3.14 | Includes native analytics/admin-center reporting surfaces plus future observability and cost-management work. |
| **Pillar 4 - SharePoint** | 4.1, 4.2, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9 | SharePoint controls remain primarily framework/playbook driven; Control 4.3 is the only live solution-backed control today. |

---

## Current Architecture Notes

- The live inventory is folder-driven: if a top-level solution folder is added or removed, update [Solutions Index](solutions-index.md) and the companion Solutions control mapping in the same change set.
- There is no separate live `agent-365-governance-monitor` solution. Native Agent 365 admin-center surfaces remain the primary implementation path for Controls 2.25 and 3.13, while `agent-365-lifecycle-governance` complements them with workflow automation and evidence capture.
- `agent-observability-foundation` is intentionally foundational and does not carry a standalone primary-control mapping, even though it supports multiple monitoring and reporting scenarios.
- Solution coverage should be interpreted together with each control's playbooks. A solution gap does not mean the control is unsupported; it means the current implementation path is documentation-led rather than packaged as a live companion solution.

---

## Follow-up Priorities

1. Preserve the **33-solution / 78-control** baseline across summary pages before updating detailed solution narratives.
2. Treat native Agent 365 governance surfaces as native capabilities unless a new live top-level solution folder is intentionally introduced.
3. Prioritize SharePoint-governance and reporting gaps only when the framework team decides they require packaged automation beyond portal guidance and playbooks.
