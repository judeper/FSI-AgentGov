# Release v1.1 — January 2026

## Overview

Version 1.1 restructures the FSI Agent Governance Framework into three clearly separated layers for improved usability and maintenance.

## Key Changes

### Architecture

- **Three-layer structure:** Framework (stable) → Control Catalog (quarterly) → Playbooks (continuous)
- **Role-based navigation:** Quick-start guides for Compliance Officers, Platform Admins, Examiners
- **Implementation extraction:** Portal paths and scripts moved to playbooks for easier updates

### New Content

- Executive Summary for board/C-suite audiences
- Adoption Roadmap with phased implementation guidance
- 10 new playbooks for getting started, compliance, and lifecycle management
- Enhanced HITL pattern definitions

### Language Updates

- Zone 1 regulatory language softened to conditional phrasing
- Pillar 4 explicitly positioned as SharePoint specialization
- Customer-facing conduct notes added to Controls 2.12 and 2.19

## Migration Notes

If upgrading from v1.0:

1. **Updated paths:** Control files moved from `reference/pillar-*/` to `controls/pillar-*/`
2. **Playbook reorganization:** Operational templates moved to `playbooks/` with new categories
3. **Framework layer:** New `framework/` directory contains governance content

## Verification

- `mkdocs build --strict` passes with zero errors
- All 60 controls validated
- All internal links verified

---

*FSI Agent Governance Framework v1.1 - January 2026*
