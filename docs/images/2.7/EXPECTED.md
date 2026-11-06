# Control 2.7: Vendor and Third-Party Risk Management

## Expected Screenshots

**Last Verified:** 2026-11-06 — checklist text checked against official documentation only; no tenant UI or screenshots tested. Store actual screenshots/evidence locally under `maintainers-local\tenant-evidence\2.7\`; never commit binaries. Document tenant-specific variations.

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-ppac-connectors-list.png` | PPAC | Manage → Inventory | Resource type/filter scope and Connectors column; distinguish available catalog from configured usage |
| `02-ppac-connector-details.png` | PPAC | Inventory → resource → Details → Connectors | Actual connector identifiers/operations; reconcile publisher/service owner separately |
| `03-ppac-analytics-connectors.png` | PPAC | Manage → Products → Power Automate / Power Apps | At most 28-day supplemental analytics; record refresh/coverage limits; Power Apps Connectors report has no download |
| `04-ppac-dlp-connectors.png` | PPAC | Security → Data and privacy → Data policy | Connector classification |
| `05-sharepoint-vendor-inventory.png` | SharePoint | Organization-defined vendor risk register | Third-party vendor list; not a native SharePoint vendor-risk feature |
| `06-sharepoint-vendor-assessment.png` | SharePoint | Organization-defined vendor assessment record | Risk assessment form implemented by the firm |
| `07-ppac-custom-connector-policy.png` | PPAC | Data policy → Connectors (environment) / Custom connectors (tenant) | By-name classification or ordered Host URL rules, final wildcard Blocked, actual scope |
| `08-agent-tools-model.png` | Copilot Studio | Agent → Tools; Overview → Model | MCP Allow all off/approved tools, actual model/release tag; provider access and PPAC controls captured separately |
| `09-maker-permissions.png` | PPAC / Dataverse | Actual environment Users + permissions / security role assignments | Maker creation rights and exceptions; not an invented sharing-limit creation switch |

## Verification Focus

- For registered Microsoft 365/Agent 365 tools, capture **Agents → Settings → Agent and plugin access**, individual plugin user availability, registered MCP server block state and any supported rolling-out individual-tool controls; distinguish them from ACP and agent maker toggles ([current guidance](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-plugins-skills-mcp-servers)).

- Third-party connectors are inventoried
- Vendor risk assessments are current
- DLP policies classify third-party connectors appropriately
- Connector usage is monitored

Use [the portal walkthrough](../../playbooks/control-implementations/2.7/portal-walkthrough.md) and [verification tests](../../playbooks/control-implementations/2.7/verification-testing.md) for source links, coverage gaps and separate policy/runtime evidence. No universal request/response Purview log or tenant marketplace switch is assumed.
