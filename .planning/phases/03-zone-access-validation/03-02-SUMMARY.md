# Summary: Plan 03-02 — Drift Detection + Teams Notification Support

## Status: Complete

## Deliverables

| Deliverable | Status | File |
|-------------|--------|------|
| Adaptive card template | Complete | `src/adaptive-card-zone-access-alert.json` |
| README update | Complete | `scripts/governance/README.md` |
| Drift detection | Complete | Pre-integrated in Plan 03-01 (scripts/governance/Test-ZoneAgentAccess.ps1) |

## Tasks Completed

1. **Baseline Loading and Comparison Logic** — Import-AccessBaseline and Compare-AccessBaseline functions implemented in Plan 03-01 script. Composite key: CheckId|Context|Zone. Drift types: PolicyChanged, StatusChanged, GroupMembershipChanged, NewCheck. Auto-save baseline after each scan.
2. **SHA-256 Evidence Hashing** — Per-check evidence hash via Get-EvidenceHash, overall IntegrityHash computed when -IncludeEvidence specified. Uppercase hex without dashes format.
3. **Teams Adaptive Card Template** — Created `src/adaptive-card-zone-access-alert.json` following UASD alert card pattern. Schema 1.4, severity mapping (Critical/High/Medium/Low), sections for header, scan summary, findings, and drift detection. Template variables documented in _metadata for Power Automate flow integration.
4. **Drift Summary Console Output** — Drift detection section in console output mirrors Test-AgentAuthConfiguration.ps1 pattern. Shows baseline path, previous scan time, drift breakdown by type (policy changed, status changed, group membership, new checks).
5. **Update Governance README** — Added Test-ZoneAgentAccess.ps1 to scripts table with Control 3.8 reference. Added integration note about adaptive card template for Teams notification.

## Decisions Made

- **Drift detection pre-integrated in Plan 01:** Since the script architecture required drift detection wiring in the main flow, both Import-AccessBaseline and Compare-AccessBaseline were implemented during Plan 01. Plan 02 focused on the adaptive card template and README update.
- **Adaptive card follows UASD pattern:** Used identical structure (header, summary, findings, actions) and metadata pattern (_metadata with mappings) as adaptive-card-uasd-alert.json for consistency across the governance solution set.
- **Added drift section to card:** Beyond the UASD pattern, added a dedicated driftSection with visibility toggle (${HasDrifts}) since drift detection is a key differentiator for this script.

## Commits

1. `feat(governance): add zone access alert adaptive card + README update` — adaptive card template (281 lines), README update (2 additions)

## File Manifest

| Action | File |
|--------|------|
| Created | `src/adaptive-card-zone-access-alert.json` |
| Modified | `scripts/governance/README.md` |

## Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| ZAV-03 | Delivered | Drift detection with baseline comparison, adaptive card template for Teams notification, JSON output for Dataverse ingestion |
