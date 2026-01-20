# Microsoft Audit Reporting Tools for Copilot/AI Analytics

**Purpose:** Leverage Microsoft's official open-source tools to address M365 Admin Center reporting limitations and enable enterprise-scale Copilot/AI audit data extraction.
**Applies to:** Organizations needing detailed Copilot adoption analytics or large-scale audit log exports beyond native portal capabilities.
**Target audience:** AI Governance Leads, Compliance Officers, Power BI Analysts, Security Operations.

---

## Background: M365 Admin Center Reporting Limitations

Organizations deploying Microsoft 365 Copilot and Copilot Studio agents face a common challenge: **native M365 Admin Center reporting provides limited granularity**, and Viva Insights data is de-identified for privacy. For FSI compliance needs, detailed per-user and per-agent analytics often require direct access to the Unified Audit Log.

Microsoft Engineering has released two open-source tools that address these gaps:

| Tool | GitHub Repository | Purpose |
|------|-------------------|---------|
| **AI-in-One Dashboard** | [microsoft/AI-in-One-Dashboard](https://github.com/microsoft/AI-in-One-Dashboard) | Power BI template for Copilot/AI adoption analytics |
| **PAX (Portable Audit eXporter)** | [microsoft/PAX](https://github.com/microsoft/PAX) | PowerShell scripts to export audit log data at enterprise scale |

---

## 1) AI-in-One Dashboard

### Overview

The AI-in-One Dashboard is a Power BI template that consolidates Copilot usage data from multiple sources:

- Microsoft Purview Unified Audit Logs
- Licensed user data from Entra ID
- Organizational hierarchy from Entra

### Key Features

| Feature | Description | FSI Relevance |
|---------|-------------|---------------|
| **Department Segmentation** | Usage by department/role | Compliance scope tracking |
| **Licensed vs. Unlicensed** | Track Copilot license utilization | Cost allocation support |
| **Adoption Trends** | Time-series usage analysis | Executive reporting |
| **Customizable Periods** | Daily, weekly, monthly views | Audit examination evidence |

### Prerequisites

- Power BI Desktop (free) or Power BI Pro license
- Purview Audit Admin or Global Reader permissions
- Access to Entra ID for organizational data
- Microsoft 365 Copilot deployment

### FSI Implementation Considerations

1. **Regulatory Evidence:** Export dashboard snapshots monthly for compliance archives
2. **Department Mapping:** Configure organizational hierarchy to align with compliance scopes (Zone 2/3 boundaries)
3. **Retention:** Archive Power BI datasets per your FINRA 4511 / SEC 17a-4 retention schedule
4. **Access Control:** Limit dashboard access to authorized governance personnel

### Deployment

Refer to the official repository for deployment instructions:
- [AI-in-One Dashboard GitHub](https://github.com/microsoft/AI-in-One-Dashboard)

The repository includes setup guides, Power BI template files, and data connection instructions.

---

## 2) PAX (Portable Audit eXporter)

### Overview

PAX is an enterprise-grade PowerShell toolkit for exporting Copilot and AI audit data at scale. It addresses the M365 Admin Center UI limitation of 50,000 records per export.

### Three Processors

PAX includes three specialized processors for different data sources:

| Processor | Data Source | Key Capabilities |
|-----------|-------------|------------------|
| **Purview Audit Log Processor** | Unified Audit Log | Copilot interactions, custom AI apps, third-party AI |
| **Copilot Interactions Content Processor** | Microsoft Graph API | Full prompts and responses (requires appropriate permissions) |
| **Graph Audit Log Processor** | Microsoft Graph API | Copilot usage enriched with Entra user data |

### Key Features

| Feature | Description | FSI Relevance |
|---------|-------------|---------------|
| **Incremental Exports** | Watermarking for continuous extraction | Efficient compliance monitoring |
| **Parallel Processing** | Enterprise scale (millions of records) | Large organization support |
| **Bypass 50K Limit** | Export full audit history | Complete regulatory evidence |
| **CSV/Excel Output** | Import to Power BI or SIEM | Flexible analytics integration |

### Prerequisites

- PowerShell 7.x or later
- Microsoft Graph API permissions (varies by processor):
  - AuditLog.Read.All (minimum)
  - User.Read.All (for Entra enrichment)
  - CopilotInteraction.Read.All (for content capture)
- Appropriate Azure AD app registration

### FSI Use Cases

#### FINRA 25-07: Prompt/Response Capture

For firms requiring complete AI interaction records per FINRA Notice 25-07:

1. Use the **Copilot Interactions Content Processor** to capture full prompts and responses
2. Export to WORM-compliant storage (Control 1.7)
3. Tag records with AI origin metadata for examination readiness

#### SEC 17a-4: Long-Term Retention

For broker-dealers requiring WORM storage:

1. Use the **Purview Audit Log Processor** for comprehensive activity logs
2. Export to Azure Immutable Blob Storage
3. Configure retention policies per SEC 17a-4(f) requirements

#### Compliance Dashboard Integration

For executive reporting per Control 3.3:

1. Schedule PAX exports to run daily/weekly
2. Import CSV output into Power BI
3. Build custom dashboards aligned with governance zones

### Deployment

Refer to the official repository for deployment instructions:
- [PAX GitHub](https://github.com/microsoft/PAX)

The repository includes detailed documentation for each processor, permission requirements, and example scripts.

---

## 3) Compliance Considerations

### Data Handling Responsibilities

When using these tools, organizations remain responsible for:

| Area | Consideration |
|------|---------------|
| **PII Handling** | Exported data may contain user identifiable information |
| **Storage Security** | Secure export destinations with appropriate access controls |
| **Retention Compliance** | Apply FINRA 4511 / SEC 17a-4 retention to exported data |
| **Access Audit** | Log who accesses exported audit data |

### Permissions Governance

- Register tool service principals with least-privilege permissions
- Document permissions in your AI governance inventory
- Review and recertify access quarterly (Control 4.2)

### Data Classification

- Treat exported audit data as Confidential or higher
- Apply sensitivity labels if exporting to SharePoint/OneDrive
- Restrict sharing to authorized compliance and security personnel

---

## 4) Integration with Framework Controls

These tools enhance the following FSI Agent Governance Framework controls:

| Control | Integration |
|---------|-------------|
| **[1.7 - Audit Logging](../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)** | PAX enables export beyond native portal limits; supports WORM storage workflows |
| **[3.2 - Usage Analytics](../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md)** | AI-in-One Dashboard provides executive-ready adoption analytics |
| **[3.3 - Compliance Reporting](../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md)** | Both tools support examination evidence generation |
| **[3.8 - Copilot Hub](../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)** | Supplements native Copilot Hub reporting with detailed analytics |

---

## 5) Known Limitations

| Tool | Limitation | Workaround |
|------|-----------|------------|
| AI-in-One Dashboard | Requires Power BI refresh for current data | Schedule automatic refresh |
| PAX | Content capture requires elevated Graph permissions | Use audit-only processor if content not required |
| PAX | Large exports may take significant time | Use incremental watermarking; run overnight |
| Both | Tools maintained by Microsoft Engineering, not official support | Monitor GitHub for updates; test in non-production first |

---

## 6) Additional Resources

### Microsoft Official Repositories

- [AI-in-One Dashboard GitHub](https://github.com/microsoft/AI-in-One-Dashboard)
- [PAX (Portable Audit eXporter) GitHub](https://github.com/microsoft/PAX)

### Related Microsoft Learn Documentation

- [Microsoft Purview Audit Solutions](https://learn.microsoft.com/en-us/purview/audit-solutions-overview)
- [Search the Audit Log](https://learn.microsoft.com/en-us/purview/audit-log-search)
- [Audit Log Retention Policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies)
- [Copilot Usage Reports](https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage)
- [Office 365 Management Activity API](https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference)

---

*Last Updated: January 2026 | Version: v1.1*
