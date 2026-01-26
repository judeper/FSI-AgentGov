# Control 1.7: Comprehensive Audit Logging - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## Prerequisites

- Unified audit logging enabled at tenant level
- E5 licenses assigned for extended retention
- Retention requirements documented per regulation
- SIEM integration requirements identified
- Azure storage account created (if WORM required)

---

## Accessing Audit

1. Open [Microsoft Purview](https://purview.microsoft.com)
2. Navigate to **Audit** in left navigation
3. Select **Search** to query audit logs

**If you don't see Audit:**

- Confirm your account has Purview Compliance Admin role
- Confirm audit logging is enabled at tenant level
- Allow for ingestion latency (30 min to 24 hours)

---

## Audit Search Interface

### Search Form Fields

| Field | Description |
|-------|-------------|
| **Date and time range (UTC)** | Start and end date for search |
| **Activities - friendly names** | Select activities by friendly name |
| **Activities - operation names** | Enter operation values (comma-separated) |
| **Record Types** | Select record types to search |
| **Users** | Users whose audit logs to search |

### Agent-Related Audit Events

**Microsoft 365 Copilot Activities:**

| Activity | Description |
|----------|-------------|
| CopilotInteraction | User interaction with Microsoft 365 Copilot |
| CopilotFeedback | User feedback on Copilot response |
| CopilotPluginUsed | Plugin invoked during interaction |

**Copilot Studio Activities:**

| Activity | Description |
|----------|-------------|
| AgentCreated | New agent created |
| AgentPublished | Agent published to channel |
| AgentModified | Agent configuration changed |
| AgentInteraction | User interaction with agent |

---

## Searching for Agent Activities

1. Navigate to **Audit > Search**
2. Set **Date and time range** for period of interest
3. In **Activities - friendly names**, select Copilot or agent activities
4. Optionally filter by **Users** or **Workloads**
5. Enter a **Search name** for reference
6. Click **Search**
7. Review results and export as needed

### Example Searches

| Scenario | Search Parameters |
|----------|-------------------|
| All Copilot interactions | Activities: CopilotInteraction, Date: Last 30 days |
| Agent creation events | Activities: AgentCreated, AgentPublished |
| Admin changes to agents | Record Types: CopilotStudio, Activities: *Modified |
| User-specific activity | Users: specific user, Activities: CopilotInteraction |

---

## Audit Retention Configuration

### Standard vs Premium

| Feature | Audit (Standard) | Audit (Premium) |
|---------|------------------|-----------------|
| Log retention | 180 days | Up to 10 years |
| Custom policies | No | Yes |
| High-value events | No | Yes |

### Creating Retention Policies

1. Navigate to **Audit > Policies**
2. Click **Create policy**
3. Configure retention period
4. Select record types to retain
5. Assign to users or entire organization
6. Save policy

### FSI Retention Requirements

| Tier | Minimum Retention | Recommended |
|------|-------------------|-------------|
| Tier 1 | 180 days (Standard) | 1 year |
| Tier 2 | 1 year | 7 years |
| Tier 3 | 7 years | 10 years |

---

## FINRA 25-07 Compliance

!!! info "FINRA Notice 25-07 Status"
    FINRA Notice 25-07 is a **Request for Comment (RFC)** with comment period extending to
    **July 2025**. Requirements described are proposed guidance, not final rules.

FINRA Notice 25-07 proposes complete AI interaction records (not summaries) for customer-facing agents.

### Required Retention Fields

| Field | Requirement |
|-------|-------------|
| Raw User Prompt | Complete, verbatim |
| Complete AI Response | Full text, no summarization |
| Timestamp | UTC timestamp |
| User ID | Authenticated identifier |
| Agent ID | Canonical AgentID |
| Citations/Sources | Required for RAG agents |

### Prohibited Practices

- Summary-only retention
- Metadata-only logging
- Partial response capture
- Prompt truncation

---

## SEC 17a-4 Compliance Options

For broker-dealers, the October 2022 SEC amendments (effective May 2023) now allow either WORM storage or an audit-trail alternative for records preservation.

### Options

| Option | Description |
|--------|-------------|
| **WORM Storage** | Traditional non-rewritable, non-erasable storage |
| **Audit-Trail Alternative** | Maintains complete audit trail of all record modifications, preventing alteration without detectable trace |
| **Azure Immutable Blob Storage** | Export to Azure with immutable policy (supports WORM) |
| **Third-party Archive** | Vendor with WORM or audit-trail compliance |
| **Microsoft 365 Audit Premium** | Extended retention (evaluate with compliance team for 17a-4 sufficiency) |

!!! info "SEC 17a-4 Amendment (October 2022)"
    The SEC's October 2022 amendments eliminated the mandatory WORM requirement, allowing
    broker-dealers to use audit-trail alternatives that achieve the same preservation goals.
    Consult with compliance and legal counsel to determine the appropriate approach.

### Azure Immutable Storage Setup (If Using WORM)

1. Create Azure Storage account
2. Enable immutable blob storage
3. Configure time-based retention (6 years minimum)
4. Set up weekly automated export from Purview Audit
5. Implement integrity verification

---

## SIEM Integration

### Export Options

| Method | Use Case |
|--------|----------|
| Manual export | Ad-hoc investigations |
| Management Activity API | Automated export |
| Azure Monitor | Real-time streaming |
| Microsoft Sentinel | Native integration |

---

[Back to Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
