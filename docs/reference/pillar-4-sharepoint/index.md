# Pillar 4: SharePoint Controls

Govern content access, site lifecycle, and external sharing within SharePoint as a knowledge source for AI agents.

## Overview

Pillar 4 addresses SharePoint-specific governance requirements when SharePoint serves as a knowledge source for **Microsoft 365 Copilot** and **Copilot Studio agents**. These 6 controls ensure that agents only access authorized content, site permissions are regularly reviewed, retention policies are enforced, external sharing is appropriately restricted, and grounding scope is properly governed—critical for preventing unauthorized disclosure of sensitive financial information.

**Primary Regulatory Alignment:** GLBA 501(b) (safeguards), SEC 17a-4 (records retention), FINRA 4511 (recordkeeping)

**Key Considerations:**

- **Information Access Governance (IAG):** Control which SharePoint sites and content agents can access
- **Oversharing Prevention:** Prevent agents from surfacing content users shouldn't see
- **External Sharing:** Restrict agent access to externally shared content
- **Retention Compliance:** Ensure SharePoint content meets regulatory retention requirements
- **Grounding Scope:** Control which content is included in the Semantic Index for AI agents

## Controls
- [4.1 SharePoint Information Access Governance (IAG)](4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md)
- [4.2 Site Access Reviews and Certification](4.2-site-access-reviews-and-certification.md)
- [4.3 Site and Document Retention Management](4.3-site-and-document-retention-management.md)
- [4.4 Guest and External User Access Controls](4.4-guest-and-external-user-access-controls.md)
- [4.5 SharePoint Security and Compliance Monitoring](4.5-sharepoint-security-and-compliance-monitoring.md)
- [4.6 Grounding Scope Governance](4.6-grounding-scope-governance.md)
