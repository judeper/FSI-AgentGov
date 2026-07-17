# Assessment Engine Coverage Matrix

This page is **generated** by `scripts/generate_coverage_matrix.py` from `assessment/manifest/controls.json` and the `EVALUATORS` registry in `assessment/engine/score.py`. Do not edit by hand.

It is the honest answer to *what does the assessment engine actually automate today?* and is intended to prevent confusion between **manual by design** and **evaluator not yet implemented**.

## Evaluator states

| State | Icon | Meaning |
|-------|------|---------|
| `auto_evaluable` | ✅ | A bespoke evaluator is registered for the check's `pass_condition` and the engine can score it from collected telemetry. |
| `unimplemented_evaluator` | ⚠️ | The manifest declares a `pass_condition`, but no evaluator function is registered yet. The generic fallback returns `unknown`. |
| `manual_only` | 📝 | The control is manual by design — either `automation: manual` in the manifest or all collection methods are non-automatable. Reviewer must answer the manual question. |

## Summary

### By control

| State | Count | Share |
|-------|-------|-------|
| ✅ Auto | 7 | 8.9% |
| 📝 Manual | 26 | 32.9% |
| ⚠️ Unimplemented | 46 | 58.2% |
| **Total** | **79** | 100% |

### By check

| State | Count | Share |
|-------|-------|-------|
| ✅ Auto | 10 | 10.3% |
| 📝 Manual | 0 | 0.0% |
| ⚠️ Unimplemented | 87 | 89.7% |
| **Total** | **97** | 100% |

### Registered evaluators

`assessment/engine/score.py` registers **12** bespoke evaluator functions:

- `audit_log_enabled`
- `audit_plan_tier_adequate`
- `ca_policy_requires_mfa`
- `ca_policy_targets_copilot_studio`
- `copilot_retention_policy_exists`
- `fsi_publisher_group_exists`
- `grounding_sources_approved`
- `no_everyone_assignment`
- `no_external_sharing_on_grounding`
- `prod_env_has_security_group`
- `prod_env_is_managed`
- `share_everyone_disabled`

**Drift warning** — the following evaluators are registered but no manifest check uses them as a `pass_condition`. This usually means the manifest condition string drifted from the evaluator key:

- `ca_policy_targets_copilot_studio`
- `prod_env_has_security_group`

## Per-pillar matrix

### Pillar 1 – Security

| Control | Title | State | Auto | Unimpl | Manual | Collection | Caveats |
|---------|-------|-------|------|--------|--------|------------|---------|
| 1.1 | Control 1.1: Restrict Agent Publishing by Authorization | ✅ Auto | 3 | 0 | 0 | Graph_API, PPAC_PowerShell |  |
| 1.10 | Control 1.10: Communication Compliance Monitoring | ⚠️ Unimplemented | 0 | 1 | 0 | Purview_PowerShell | `pass_condition: comm_compliance_policy_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 1.11 | Control 1.11: Conditional Access and Phishing-Resistant MFA | ✅ Auto | 1 | 2 | 0 | Graph_API | `pass_condition: signin_frequency_set` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: phishing_resistant_mfa` declared in manifest but no bespoke evaluator registered in s… |
| 1.12 | Control 1.12: Insider Risk Detection and Response | 📝 Manual | 0 | 0 | 0 | — |  |
| 1.13 | Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell, Purview_PowerShell | `pass_condition: sit_count_adequate` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: dlp_references_sits` declared in manifest but no bespoke evaluator registered in score.… |
| 1.14 | Control 1.14: Data Minimization and Agent Scope Control | 📝 Manual | 0 | 0 | 0 | — |  |
| 1.15 | Control 1.15: Encryption: Data in Transit and at Rest | ⚠️ Unimplemented | 0 | 2 | 0 | Graph_API | `pass_condition: tls_12_enforced` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: at_rest_encryption_verified` declared in manifest but no bespoke evaluator registered in s… |
| 1.16 | Control 1.16: Information Rights Management (IRM) for Documents | 📝 Manual | 0 | 0 | 0 | — |  |
| 1.17 | Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP) | ⚠️ Unimplemented | 0 | 1 | 0 | Purview_PowerShell | `pass_condition: endpoint_dlp_policy_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 1.18 | Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC) | ⚠️ Unimplemented | 0 | 2 | 0 | Graph_API | `pass_condition: rbac_least_privilege` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: no_excessive_admin` declared in manifest but no bespoke evaluator registered in score… |
| 1.19 | Control 1.19: eDiscovery for Agent Interactions | ⚠️ Unimplemented | 0 | 2 | 0 | Purview_PowerShell | `pass_condition: ediscovery_agent_scope` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: ediscovery_copilot_content` declared in manifest but no bespoke evaluator registere… |
| 1.2 | Control 1.2: Agent Registry and Integrated Apps Management | ⚠️ Unimplemented | 0 | 3 | 0 | Graph_API | `pass_condition: agent_inventory_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: auth_mode_configured` declared in manifest but no bespoke evaluator registered in s… |
| 1.20 | Control 1.20: Network Isolation and Private Connectivity | ⚠️ Unimplemented | 0 | 2 | 0 | Azure_API | `pass_condition: private_endpoint_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: network_isolation_enforced` declared in manifest but no bespoke evaluator register… |
| 1.21 | Control 1.21: Adversarial Input Logging | ⚠️ Unimplemented | 0 | 1 | 0 | Purview_PowerShell | `pass_condition: prompt_response_logging` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 1.22 | Control 1.22: Information Barriers for AI Agents | ⚠️ Unimplemented | 0 | 2 | 0 | Purview_PowerShell | `pass_condition: ib_policy_active` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: ib_segments_configured` declared in manifest but no bespoke evaluator registered in score… |
| 1.23 | Control 1.23: Step-Up Authentication for AI Agent Operations | ⚠️ Unimplemented | 0 | 1 | 0 | Graph_API | `pass_condition: stepup_auth_deployed` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 1.24 | Control 1.24: Defender AI Security Posture Management (AI-SPM) | 📝 Manual | 0 | 0 | 0 | Azure_API |  |
| 1.25 | Control 1.25: MIME Type Restrictions for File Uploads | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell | `pass_condition: mime_zone_compliant` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: blocked_extensions_enforced` declared in manifest but no bespoke evaluator registered … |
| 1.26 | Control 1.26: Agent File Upload and File Analysis Restrictions | ⚠️ Unimplemented | 0 | 2 | 0 | Graph_API, PPAC_REST | `pass_condition: file_upload_zone_appropriate` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: label_inheritance_configured` declared in manifest but no bespoke evaluator r… |
| 1.27 | Control 1.27: AI Agent Content Moderation Enforcement | ⚠️ Unimplemented | 0 | 3 | 0 | Graph_API, PPAC_REST | `pass_condition: moderation_level_set` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: moderation_zone_compliant` declared in manifest but no bespoke evaluator registered i… |
| 1.28 | Control 1.28: Policy-Based Agent Publishing Restrictions | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell | `pass_condition: dlp_publishing_restrictions` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: security_scan_enabled` declared in manifest but no bespoke evaluator registere… |
| 1.29 | Control 1.29: Global Secure Access: Network Controls for Copilot Studio Agents | ⚠️ Unimplemented | 0 | 2 | 0 | Graph_API | `pass_condition: gsa_profile_linked` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: wcf_policy_configured` declared in manifest but no bespoke evaluator registered in scor… |
| 1.3 | Control 1.3: SharePoint Content Governance and Permissions | ⚠️ Unimplemented | 0 | 2 | 0 | SharePoint_Graph | `pass_condition: permission_inheritance_intact` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: no_oversharing` declared in manifest but no bespoke evaluator registered in … |
| 1.4 | Control 1.4: Advanced Connector Policies (ACP) | ⚠️ Unimplemented | 0 | 3 | 0 | PPAC_PowerShell | `pass_condition: dlp_policy_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: acp_allowlist_configured` declared in manifest but no bespoke evaluator registered in sc… |
| 1.5 | Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell, Purview_PowerShell | `pass_condition: dlp_scope_covers_agents` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: sensitivity_labels_enabled` declared in manifest but no bespoke evaluator register… |
| 1.6 | Control 1.6: Microsoft Purview DSPM for AI | ⚠️ Unimplemented | 0 | 1 | 0 | Purview_PowerShell | `pass_condition: dspm_policy_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 1.7 | Control 1.7: Comprehensive Audit Logging and Compliance | ✅ Auto | 2 | 0 | 0 | Graph_API, Purview_PowerShell |  |
| 1.8 | Control 1.8: Runtime Protection and External Threat Detection | ⚠️ Unimplemented | 0 | 1 | 0 | Sentinel_KQL | `pass_condition: sentinel_agent_alerts_exist` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 1.9 | Control 1.9: Data Retention and Deletion Policies | ✅ Auto | 1 | 1 | 0 | Purview_PowerShell | `pass_condition: retention_duration_adequate` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |

### Pillar 2 – Management

| Control | Title | State | Auto | Unimpl | Manual | Collection | Caveats |
|---------|-------|-------|------|--------|--------|------------|---------|
| 2.1 | Control 2.1: Managed Environments | ✅ Auto | 1 | 1 | 0 | PPAC_PowerShell | `pass_condition: managed_policies_enforced` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 2.10 | Control 2.10: Patch Management and System Updates | ⚠️ Unimplemented | 0 | 1 | 0 | PPAC_PowerShell | `pass_condition: version_info_available` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 2.11 | Control 2.11: Bias Testing and Fairness Assessment | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.12 | Control 2.12: Supervision and Oversight (FINRA Rule 3110) | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.13 | Control 2.13: Documentation and Record Keeping | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.14 | Control 2.14: Training and Awareness Program | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.15 | Control 2.15: Environment Routing and Auto-Provisioning | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell | `pass_condition: routing_rules_configured` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: routing_zone_enforced` declared in manifest but no bespoke evaluator registered i… |
| 2.16 | Control 2.16: RAG Source Integrity Validation | ⚠️ Unimplemented | 0 | 1 | 0 | SharePoint_Graph | `pass_condition: rag_validation_deployed` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 2.17 | Control 2.17: Multi-Agent Orchestration Limits | ⚠️ Unimplemented | 0 | 1 | 0 | PPAC_PowerShell | `pass_condition: orchestration_limits_set` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 2.18 | Control 2.18: Automated Conflict of Interest Testing | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.19 | Control 2.19: Customer AI Disclosure and Transparency | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.2 | Control 2.2: Environment Groups and Tier Classification | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell | `pass_condition: env_groups_exist` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: tier_classification_present` declared in manifest but no bespoke evaluator registered in … |
| 2.20 | Control 2.20: Adversarial Testing and Red Team Framework | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.21 | Control 2.21: AI Marketing Claims and Substantiation | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.22 | Control 2.22: Inactivity Timeout Enforcement | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_REST | `pass_condition: timeout_configured` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: timeout_value_adequate` declared in manifest but no bespoke evaluator registered in sco… |
| 2.23 | Control 2.23: User Consent and AI Disclosure Enforcement | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.24 | Control 2.24: Agent Feature Enablement and Restriction Governance | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell | `pass_condition: genai_flags_reviewed` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: external_plugins_controlled` declared in manifest but no bespoke evaluator registered… |
| 2.25 | Control 2.25: Microsoft Agent 365 — Admin Center Governance Console | ⚠️ Unimplemented | 0 | 2 | 0 | Graph_API | `pass_condition: agent365_console_accessible` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: agent365_inventory_visible` declared in manifest but no bespoke evaluator regi… |
| 2.26 | Control 2.26: Entra Agent ID — Identity Governance for Agents | ⚠️ Unimplemented | 0 | 2 | 0 | Graph_API | `pass_condition: agent_ids_registered` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: access_packages_configured` declared in manifest but no bespoke evaluator registered … |
| 2.27 | Control 2.27: Consumption-Entitlement Governance | ⚠️ Unimplemented | 0 | 4 | 0 | Graph_API, PPAC_PowerShell | `pass_condition: entitlement_contract_evaluated` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: per_agent_caps_configured` declared in manifest but no bespoke evaluator re… |
| 2.3 | Control 2.3: Change Management and Release Planning | ⚠️ Unimplemented | 0 | 1 | 0 | PPAC_PowerShell | `pass_condition: approval_workflow_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 2.4 | Control 2.4: Business Continuity and Disaster Recovery | ⚠️ Unimplemented | 0 | 1 | 0 | SharePoint_Graph | `pass_condition: dr_documentation_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 2.5 | Control 2.5: Testing, Validation, and Quality Assurance | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.6 | Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / Fed SR 26-2) | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.7 | Control 2.7: Vendor and Third-Party Risk Management | 📝 Manual | 0 | 0 | 0 | — |  |
| 2.8 | Control 2.8: Access Control and Segregation of Duties | ⚠️ Unimplemented | 0 | 2 | 0 | Graph_API | `pass_condition: sod_matrix_match` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: no_dev_prod_overlap` declared in manifest but no bespoke evaluator registered in score.py… |
| 2.9 | Control 2.9: Agent Performance Monitoring and Optimization | ⚠️ Unimplemented | 0 | 1 | 0 | PPAC_PowerShell | `pass_condition: usage_metrics_available` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |

### Pillar 3 – Reporting

| Control | Title | State | Auto | Unimpl | Manual | Collection | Caveats |
|---------|-------|-------|------|--------|--------|------------|---------|
| 3.1 | Control 3.1: Agent Inventory and Metadata Management | ⚠️ Unimplemented | 0 | 2 | 0 | Graph_API | `pass_condition: agent_inventory_exportable` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: all_agents_classified` declared in manifest but no bespoke evaluator registered… |
| 3.10 | Control 3.10: Hallucination Feedback Loop | 📝 Manual | 0 | 0 | 0 | — |  |
| 3.11 | Control 3.11: Centralized Agent Inventory Enforcement | 📝 Manual | 0 | 0 | 0 | — |  |
| 3.12 | Control 3.12: Agent Governance Exception and Override Management | 📝 Manual | 0 | 0 | 0 | — |  |
| 3.13 | Control 3.13: Agent 365 Admin Center Analytics and Reporting | 📝 Manual | 0 | 0 | 0 | — |  |
| 3.14 | Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry | 📝 Manual | 0 | 0 | 0 | — |  |
| 3.2 | Control 3.2: Usage Analytics and Activity Monitoring | 📝 Manual | 0 | 0 | 0 | — |  |
| 3.3 | Control 3.3: Compliance and Regulatory Reporting | ⚠️ Unimplemented | 0 | 1 | 0 | SharePoint_Graph | `pass_condition: incident_log_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 3.4 | Control 3.4: Incident Reporting and Root Cause Analysis | ⚠️ Unimplemented | 0 | 1 | 0 | SharePoint_Graph | `pass_condition: exception_doc_exists` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 3.5 | Control 3.5: Cost Allocation and Budget Tracking | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell | `pass_condition: usage_dashboard_enabled` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: data_export_configured` declared in manifest but no bespoke evaluator registered i… |
| 3.6 | Control 3.6: Orphaned Agent Detection and Remediation | 📝 Manual | 0 | 0 | 0 | — |  |
| 3.7 | Control 3.7: PPAC Security Posture Assessment | ⚠️ Unimplemented | 0 | 2 | 0 | PPAC_PowerShell | `pass_condition: security_posture_retrievable` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: posture_score_adequate` declared in manifest but no bespoke evaluator registe… |
| 3.8 | Control 3.8: Copilot Hub and Governance Dashboard | 📝 Manual | 0 | 0 | 0 | — |  |
| 3.9 | Control 3.9: Microsoft Sentinel Integration | ⚠️ Unimplemented | 0 | 2 | 0 | Sentinel_KQL | `pass_condition: sentinel_workspace_linked` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: audit_logs_ingested` declared in manifest but no bespoke evaluator registered in… |

### Pillar 4 – SharePoint

| Control | Title | State | Auto | Unimpl | Manual | Collection | Caveats |
|---------|-------|-------|------|--------|--------|------------|---------|
| 4.1 | Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery | ⚠️ Unimplemented | 0 | 2 | 0 | SharePoint_Graph | `pass_condition: site_permissions_readable` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: iag_rcd_enabled` declared in manifest but no bespoke evaluator registered in sco… |
| 4.2 | Control 4.2: Site Access Reviews and Certification | ⚠️ Unimplemented | 0 | 1 | 0 | SharePoint_Graph | `pass_condition: retention_labels_applied` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 4.3 | Control 4.3: Site and Document Retention Management | ⚠️ Unimplemented | 0 | 2 | 0 | SharePoint_Graph | `pass_condition: sp_retention_applied` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: sp_retention_duration_ok` declared in manifest but no bespoke evaluator registered in… |
| 4.4 | Control 4.4: Guest and External User Access Controls | ✅ Auto | 1 | 1 | 0 | SharePoint_Graph | `pass_condition: guest_access_disabled` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 4.5 | Control 4.5: SharePoint Security and Compliance Monitoring | ⚠️ Unimplemented | 0 | 1 | 0 | SharePoint_Graph | `pass_condition: knowledge_scan_present` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 4.6 | Control 4.6: Grounding Scope Governance | ✅ Auto | 1 | 1 | 0 | PPAC_PowerShell, SharePoint_Graph | `pass_condition: grounding_scope_restricted` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. |
| 4.7 | Control 4.7: Microsoft 365 Copilot Data Governance | 📝 Manual | 0 | 0 | 0 | — |  |
| 4.8 | Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources | ⚠️ Unimplemented | 0 | 2 | 0 | SharePoint_Graph | `pass_condition: item_permissions_scanned` declared in manifest but no bespoke evaluator registered in score.py. Result will be `unknown`. `pass_condition: no_item_oversharing` declared in manifest but no bespoke evaluator registered in … |
| 4.9 | Control 4.9: Embedded File Content Governance | 📝 Manual | 0 | 0 | 0 | — |  |

## How to add a new evaluator

1. Add a `_eval_<name>(collected, source_key)` function to `assessment/engine/score.py` returning `(passed: bool | None, evidence: str)`.
2. Register it in the `EVALUATORS` dict using the same string as the manifest's `pass_condition`.
3. Add a fixture and a unit test in `assessment/tests/`.
4. Re-run `python scripts/generate_coverage_matrix.py` and commit the regenerated `docs/reference/assessment-coverage.md`.

<!-- This page is generated by scripts/generate_coverage_matrix.py. Do not edit by hand. -->

*FSI Agent Governance Framework v1.6.2 - May 2026*