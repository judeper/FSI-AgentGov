# Phase 2: Documentation Audit Foundation - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Verify all 62 controls and their 248 playbooks reflect current Microsoft capabilities with accurate citations and consistent formatting. This is an accuracy and consistency audit — not feature work. Output is per-pillar audit reports followed by corrections. New controls, new playbooks, and feature additions belong in other phases.

</domain>

<decisions>
## Implementation Decisions

### Discrepancy handling
- Two-pass approach: first pass flags all discrepancies in audit reports, second pass fixes them after review
- Audit report findings include detailed evidence: specific Microsoft Learn URL, what our doc says vs what's current, and suggested correction
- Three-tier severity classification: Critical (factually wrong / could mislead), Moderate (outdated but not harmful), Minor (formatting / naming inconsistency)
- When Microsoft has removed or renamed a capability, update to current but add a transition note (e.g., "Previously known as X" or "Replaced by Y in [date]")

### Audit scope & batching
- Batch by pillar: 4 batches matching the 4 pillars (Pillar 1: 24 controls, Pillar 2: 21, Pillar 3: 10, Pillar 4: 7)
- Each plan covers one pillar — one plan per pillar for the audit pass
- Full structural + content check per control: verify content accuracy against Microsoft Learn AND verify 10-section template compliance, formatting, and link resolution
- Scope includes all 248 control playbooks (portal-walkthrough, powershell-setup, verification-testing, troubleshooting) — not just the 62 control documents
- Each pillar produces its own audit report (e.g., AUDIT-PILLAR-1.md)

### Formatting standards
- Core sections (Purpose, Requirements, Implementation, Verification) are mandatory and must follow template ordering. Optional sections (Related Controls, References) can vary
- Standardize MkDocs formatting elements across all controls: define one pattern for admonitions, tables, code blocks, and enforce consistently
- Derive the formatting standard from the best-formatted existing controls rather than creating a separate standards document
- Controls that work but use non-standard formatting get rewritten to match the standard — full consistency enforced

### Citation & reference style
- Broken or redirected Microsoft Learn URLs: replace with current equivalent URL (remove if no equivalent exists), no change notes needed
- Add a "Last Verified" date metadata field to each control (e.g., "Last Verified: 2026-02-XX") to track freshness
- Regulatory citations formatted inline with specific section numbers (e.g., "Required for FINRA 4511(a)(1)") where relevant in the control text
- Verify regulatory citations against actual regulation text, not just the existing regulatory-mappings.md — flag any citations that don't accurately reflect the requirement

### Claude's Discretion
- Exact format of the "Last Verified" metadata field placement within controls
- How to identify the "best-formatted" controls to derive the standard from
- Ordering of pillar audits (which pillar first)
- Internal structure of per-pillar audit reports

</decisions>

<specifics>
## Specific Ideas

- Two-pass methodology: audit-then-fix allows reviewing all findings before committing changes
- Per-pillar audit reports enable incremental review — don't need to wait for all 62 controls before reviewing Pillar 1 findings
- Transition notes for renamed/removed Microsoft capabilities serve FSI admins who may recognize old names
- "Last Verified" date creates ongoing maintenance value beyond this audit

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-documentation-audit-foundation*
*Context gathered: 2026-02-03*
