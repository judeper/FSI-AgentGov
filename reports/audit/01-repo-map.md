# Repo Map

## FSI-AgentGov (Documentation Repository)

**URL:** https://github.com/judeper/FSI-AgentGov
**Local:** `C:\dev\FSI-AgentGov`
**Purpose:** Governance framework documentation for Microsoft 365 AI agents in US FSI

### Directory Structure

```
FSI-AgentGov/
├── docs/                              # SOURCE OF TRUTH — all published content
│   ├── controls/                      # 71 governance controls (4 pillars)
│   │   ├── pillar-1-security/         # 28 controls (1.1–1.28)
│   │   ├── pillar-2-management/       # 24 controls (2.1–2.24)
│   │   ├── pillar-3-reporting/        # 12 controls (3.1–3.12)
│   │   └── pillar-4-sharepoint/       # 7 controls (4.1–4.7)
│   ├── playbooks/                     # Implementation guides
│   │   ├── control-implementations/   # 284 playbooks (4 per control × 71)
│   │   ├── advanced-implementations/  # 15 advanced guides + 10 subfolders
│   │   ├── governance-operations/     # Standing governance procedures
│   │   ├── compliance-and-audit/      # Audit preparation
│   │   ├── incident-and-risk/         # Incident handling
│   │   ├── agent-lifecycle/           # Lifecycle management
│   │   ├── monitoring-and-validation/ # Monitoring procedures
│   │   ├── regulatory-modules/        # Regulatory-specific guides
│   │   └── validation-testing/        # Testing procedures
│   ├── framework/                     # 12 governance principle docs
│   ├── reference/                     # 22 supporting materials
│   ├── getting-started/               # 2 onboarding docs
│   ├── downloads/                     # 6 Excel checklists + index
│   └── templates/                     # Control authoring template
├── scripts/                           # 60+ validation and automation scripts
│   ├── governance/                    # 20 PowerShell governance scripts
│   ├── reporting/                     # Reporting scripts
│   ├── hooks/                         # Git hooks
│   ├── private/                       # Private helper scripts
│   └── config/                        # Configuration files
├── mkdocs.yml                         # Site nav and build config
├── reports/                           # Generated reports
├── releases/                          # Release artifacts
└── data/                              # Data files
```

### Source of Truth Locations

| Content Type | Location | Format |
|-------------|----------|--------|
| Control definitions | `docs/controls/pillar-*/` | Markdown (10-section template) |
| Implementation playbooks | `docs/playbooks/control-implementations/` | Markdown (4 per control) |
| Framework principles | `docs/framework/` | Markdown |
| Reference materials | `docs/reference/` | Markdown |
| Excel checklists | `docs/downloads/` | .xlsx |
| Site structure | `mkdocs.yml` | YAML |
| Validation scripts | `scripts/` | Python + PowerShell |

---

## FSI-AgentGov-Solutions (Automation Repository)

**URL:** https://github.com/judeper/FSI-AgentGov-Solutions
**Local:** `C:\dev\FSI-AgentGov-Solutions`
**Purpose:** Deployable Power Platform solutions implementing governance controls

### Directory Structure

```
FSI-AgentGov-Solutions/
├── agent-access-monitor/              # Agent access governance monitoring
├── agent-observability-foundation/    # Telemetry and observability (v1.1.0)
├── agent-sharing-access-restriction-detector/  # Sharing restriction detection
├── audit-compliance-manager/             # Unified audit compliance manager (v1.0.0, consolidates former ACV + ALCA)
├── coi-testing/                       # Conflict of interest testing (planned)
├── compliance-dashboard/              # Aggregated compliance reporting (v1.0.0)
├── conditional-access-automation/     # CA policy deployment (v1.1.0)
├── content-moderation-monitor/        # Content moderation monitoring (v1.0.0)
├── cross-solution-integration/        # Cross-solution orchestration (v1.0.0)
├── deny-event-correlation-report/     # Deny event correlation
├── dr-testing-framework/             # DR testing (planned)
├── environment-lifecycle-management/  # Environment provisioning (v1.1.2)
├── file-upload-security/             # File upload security (v1.0.0)
├── finra-supervision-workflow/       # FINRA 3110 supervision (v1.0.0)
├── hallucination-tracker/            # Hallucination tracking (planned)
├── inactivity-timeout-enforcement/   # Timeout enforcement (v1.0.0)
├── message-center-monitor/           # M365 Message Center monitoring (v2.1.1)
├── mime-type-restrictions/           # MIME type restrictions (v1.0.0)
├── pipeline-governance-cleanup/      # Pipeline governance (v1.0.8)
├── rag-source-validator/             # RAG source validation (WIP)
├── scope-drift-monitor/             # Scope drift detection (v1.1.0)
├── segregation-detector/            # Segregation of duties (v1.0.0)
├── session-security-configurator/   # Session security config (v1.0.0)
├── unrestricted-agent-sharing-detector/ # Sharing detection (v1.0.0)
└── scripts/                          # Shared scripts (hooks)
```

### Solution Maturity

| Status | Count | Solutions |
|--------|-------|-----------|
| Production (v1.0+) | 19 | Most solutions |
| Planned/WIP | 4 | coi-testing, dr-testing-framework, hallucination-tracker, rag-source-validator |
| Missing README | 1 | agent-sharing-access-restriction-detector |

### Common Technology Stack

- **Languages:** PowerShell 7+, Python 3.9+, C# (one plugin)
- **Platform:** Power Platform, Dataverse, Power Automate, Power BI
- **Identity:** Microsoft Graph API, Entra ID, Azure Key Vault
- **Monitoring:** KQL, Application Insights, Log Analytics, Microsoft Sentinel
- **Licensing:** M365 E5/E5 Compliance, Power Platform Premium, Dataverse capacity

---

## Cross-Repo Dependencies

1. **Solutions → Docs:** Each solution maps to specific control IDs in the docs repo
2. **Docs → Solutions:** `docs/reference/solutions-index.md` catalogs all solutions
3. **Docs → Solutions:** Advanced implementation playbooks reference solution deployment guides
4. **Scripts:** Both repos contain `scripts/hooks/` with shared hook patterns (boundary-check, researcher-package-reminder)
