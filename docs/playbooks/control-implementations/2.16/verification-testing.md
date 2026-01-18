# Verification & Testing: Control 2.16 - RAG Source Integrity Validation

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Knowledge Source Inventory

1. Open each agent in Copilot Studio
2. Navigate to **Knowledge** settings
3. Document all configured knowledge sources
4. **EXPECTED:** All sources match approved inventory

### Test 2: Verify Content Approval Workflow

1. Upload a new document to a knowledge source library
2. Check that document requires approval before indexing
3. Approve the document
4. Verify agent can now access the content
5. **EXPECTED:** Unapproved content is not available to agent

### Test 3: Verify Version Control

1. Check document library versioning settings
2. Create a minor version of a document
3. Query agent about the content
4. **EXPECTED:** Agent uses major (approved) version, not draft

### Test 4: Verify Staleness Detection

1. Identify a document older than staleness threshold
2. Run staleness report
3. **EXPECTED:** Stale document appears in report

### Test 5: Verify Citation Display

1. Ask agent a question that requires knowledge source
2. Review agent response
3. **EXPECTED:** Response includes citation to source document

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.16-01 | All knowledge sources documented | Inventory complete | |
| TC-2.16-02 | Unapproved content not indexed | Content blocked | |
| TC-2.16-03 | Only major versions used | Draft ignored | |
| TC-2.16-04 | Stale content detected | Alert generated | |
| TC-2.16-05 | Citations displayed | Source shown | |
| TC-2.16-06 | Unauthorized source blocked | Connection rejected | |
| TC-2.16-07 | Knowledge source audit logged | Logs available | |

---

## Evidence Collection Checklist

### Knowledge Source Inventory

- [ ] Document: Complete inventory of all knowledge sources
- [ ] Screenshot: Copilot Studio knowledge configuration for each agent
- [ ] Export: SharePoint site/library list used as sources

### Approval Workflow

- [ ] Screenshot: Content approval workflow configuration
- [ ] Screenshot: Example document in pending approval state
- [ ] Document: Approval workflow process description

### Version Control

- [ ] Screenshot: Library versioning settings
- [ ] Screenshot: Document version history example
- [ ] Document: Version control policy

### Staleness Monitoring

- [ ] Export: Staleness report (CSV)
- [ ] Screenshot: Alert configuration for stale content
- [ ] Document: Staleness threshold policy

### Citations

- [ ] Screenshot: Agent response with citation displayed
- [ ] Document: Citation format specification

---

## Evidence Artifact Naming Convention

```
Control-2.16_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-2.16_KnowledgeInventory_20260115.xlsx
- Control-2.16_ApprovalWorkflow_20260115.png
- Control-2.16_StalenessReport_20260115.csv
- Control-2.16_CitationExample_20260115.png
```

---

## Attestation Statement Template

```markdown
## Control 2.16 Attestation - RAG Source Integrity Validation

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. All knowledge sources are inventoried and approved
2. Content approval workflow is enabled for knowledge sources
3. Document versioning is configured per policy
4. Staleness monitoring is active with [X] day threshold
5. Agent responses include source citations
6. Audit logging captures knowledge source queries
7. No unauthorized knowledge sources are configured

**Knowledge Sources Configured:** [Number]
**Last Inventory Review:** [Date]
**Stale Content Count:** [Number]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
