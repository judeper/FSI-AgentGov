# Control 2.13: Documentation and Record-Keeping

## Expected Screenshots

Documentation targets re-verified 2026-11-09; tenant screenshots remain pending. Store captures under `maintainers-local/tenant-evidence/`, never in Git.

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-sharepoint-doc-library.png` | SharePoint | Governance document library | Document structure |
| `02-sharepoint-version-history.png` | SharePoint | Document → Version history | Version tracking |
| `03-sharepoint-metadata.png` | SharePoint | Document → Properties | Metadata and classification |
| `04-purview-retention-labels.png` | Purview | Solutions > Records Management > File plan | Label duration, record type, and disposition settings |
| `05-purview-retention-applied.png` | SharePoint | Test document > Properties | Actual retention label and standard-record lock status |
| `06-purview-legal-hold.png` | Purview | eDiscovery → Holds | Legal hold configuration |
| `07-sharepoint-templates.png` | SharePoint | Templates library | Document templates |
| `08-purview-label-policy.png` | Purview | Solutions > Records Management > Policies > Label policies | Publication distribution and governance group under Microsoft 365 Group mailboxes & sites |
| `09-purview-auto-apply.png` | Purview | Records Management > Policies > Label policies > Auto-apply a label | Actual library ParentLink query, location, simulation, and deployed status |
| `10-agent-release.png` | Copilot Studio | Agent > Publish; Settings > Agent details | Publication status and environment context; pair with release record |
| `11-solution-history.png` | Power Apps | Solutions > select solution > See history | Version, operation, timestamps, result; capture before 180-day cleanup |
| `12-solution-layers.png` | Solution explorer | Agents > agent > Advanced > See solution layers | Deployed layers; pair with source solution ZIP and dependency inventory |
| `13-container-immutability.png` | Azure | Container > More > Access policy | Container-scoped locked retention and disposable-test results |
| `14-dataverse-auditing.png` | Power Platform Admin Center | Manage > Environments > environment > Settings > Audit and logs > Audit settings | Environment auditing; pair with table/column auditing settings |

## Verification Focus

- Document library structure follows standard
- Version control is enabled
- Retention labels are applied
- Standard and regulatory record behavior are distinguished; no regulatory-record auto-apply test
- Publication evidence and source export are not replaced with a Power Apps inventory
- Templates ensure consistency
