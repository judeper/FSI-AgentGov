# Troubleshooting: Control 2.16 - RAG Source Integrity Validation

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Agent can't find content | Content not indexed or not approved | Verify approval status; wait for index refresh |
| Citations not appearing | Feature not enabled or content type issue | Check citation settings; verify content has metadata |
| Stale content in responses | No staleness policy or monitoring gap | Implement staleness checks; update content |
| Unauthorized source added | Maker added source without approval | Remove source; implement approval workflow |
| Version mismatch | Agent using cached/old version | Force refresh; verify version settings |

---

## Detailed Troubleshooting

### Issue: Agent Can't Find Expected Content

**Symptoms:** Agent responds "I don't have information about that" when content exists

**Diagnostic Steps:**

1. Verify content is in an approved knowledge source:
   ```
   Copilot Studio > Agent > Knowledge > Verify source is listed
   ```

2. Check content approval status:
   ```
   SharePoint > Library > Document > Check "Approval Status"
   ```

3. Verify content has been indexed:
   - Knowledge sources index periodically
   - New content may take up to 24 hours

4. Test with exact content terms to verify indexing

**Resolution:**

- Approve content if in pending state
- Wait for index refresh (up to 24 hours)
- Verify content is in correct library/folder
- Check knowledge source scope isn't too narrow

---

### Issue: Citations Not Appearing in Responses

**Symptoms:** Agent provides answers but doesn't cite sources

**Diagnostic Steps:**

1. Verify citation setting is enabled:
   ```
   Copilot Studio > Agent > Settings > Check citation options
   ```

2. Check if response type supports citations:
   - Some response types may not include citations
   - Verify agent is using knowledge-grounded responses

3. Test with a question that clearly requires document reference

**Resolution:**

- Enable citations in agent settings
- Ensure content has proper metadata for citation
- Verify agent is configured to use knowledge sources for the topic

---

### Issue: Agent Using Outdated Content

**Symptoms:** Agent provides information from old document versions

**Diagnostic Steps:**

1. Check document version history:
   ```
   SharePoint > Document > Version history
   ```

2. Verify agent knowledge source refresh:
   - Knowledge sources sync periodically
   - Check when last sync occurred

3. Verify versioning configuration:
   - Major vs. minor versions
   - Which version is "current"

**Resolution:**

- Publish new major version of document
- Wait for knowledge source refresh
- Manually trigger refresh if available
- Verify versioning policy is correctly configured

---

### Issue: Unauthorized Knowledge Source Added

**Symptoms:** Agent is using content from non-approved sources

**Diagnostic Steps:**

1. Review all knowledge sources:
   ```
   Copilot Studio > Agent > Knowledge
   ```

2. Compare to approved source inventory

3. Check audit logs for who added the source

**Resolution:**

- Remove unauthorized knowledge source immediately
- Document incident per incident response procedures
- Review maker permissions
- Implement approval workflow for knowledge source changes

---

## How to Confirm Configuration is Active

### Via Copilot Studio

1. Open the agent
2. Navigate to **Knowledge**
3. Verify all listed sources are approved
4. Test agent with knowledge-dependent question

### Via SharePoint

1. Navigate to knowledge source library
2. Check **Settings** > **Versioning settings**
3. Verify content approval is enabled
4. Check version history on sample documents

### Via Testing

1. Upload new unapproved document
2. Query agent about new content
3. Verify agent does NOT use unapproved content
4. Approve document and re-test

---

## Escalation Path

If issues persist after troubleshooting:

1. **SharePoint Admin** - Library configuration issues
2. **Copilot Studio Admin** - Knowledge source configuration
3. **Content Owner** - Content accuracy and staleness
4. **AI Governance Lead** - Policy questions
5. **Microsoft Support** - Platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Index refresh delay | New content not immediately available | Plan content updates ahead of need |
| No real-time staleness alerts | Manual monitoring required | Implement scheduled Power Automate flows |
| Citation format limited | May not match regulatory requirements | Document citation mapping procedure |
| Cannot restrict knowledge scope per user | All users see same knowledge | Use separate agents for different access levels |
| No built-in approval workflow | Requires SharePoint or Power Automate setup | Implement custom workflow |

---

[Back to Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
