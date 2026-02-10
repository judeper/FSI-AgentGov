---
phase: 4
plan: 1
wave: 1
dependencies: ["Phase 3 complete"]
---

# Plan 04-FUS-01: Evidence Export and Integrity Verification

## Objective
Create evidence export and integrity verification scripts for regulatory compliance (SEC 17a-4(f) support).

## Requirements Covered
- **CEV-01**: SHA-256 evidence export
- **INF-03**: Evidence integrity verification

## Tasks
1. Create `scripts/Export-FileUploadEvidence.ps1` following CMM evidence export pattern
2. Query Dataverse: fsi_fileupload_validationhistory, fsi_fileupload_violation, fsi_fileupload_baseline
3. Build JSON evidence package with metadata, summary, validations, violations, baselines sections
4. Generate SHA-256 companion `.sha256` file
5. Support zone filtering, date range, RunId filtering
6. Create `scripts/Test-EvidenceIntegrity.ps1` for hash verification

## Verification
- [ ] Evidence JSON has all required sections
- [ ] SHA-256 companion file generated
- [ ] Test-EvidenceIntegrity validates hash match
- [ ] Zone and date filtering works
