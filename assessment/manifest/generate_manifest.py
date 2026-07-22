#!/usr/bin/env python3
"""Generate controls.json manifest from control file metadata and markdown sources."""
import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASE = REPO_ROOT / "docs" / "controls"
OUTPUT = REPO_ROOT / "assessment" / "manifest" / "controls.json"

PILLAR_DIRS = {
    1: ("pillar-1-security", "Security"),
    2: ("pillar-2-management", "Management"),
    3: ("pillar-3-reporting", "Reporting"),
    4: ("pillar-4-sharepoint", "SharePoint"),
}

# (id, filename, pillar, automation, collection_methods, manual_question)
CONTROLS = [
    # Pillar 1 - Security (29)
    ("1.1","1.1-restrict-agent-publishing-by-authorization.md",1,"full",["PPAC_PowerShell","Graph_API"],None),
    ("1.2","1.2-agent-registry-and-integrated-apps-management.md",1,"full",["Graph_API"],None),
    ("1.3","1.3-sharepoint-content-governance-and-permissions.md",1,"partial",["SharePoint_Graph"],"Have site permission reviews been completed in the last 90 days for all agent knowledge sources?"),
    ("1.4","1.4-advanced-connector-policies-acp.md",1,"full",["PPAC_PowerShell"],None),
    ("1.5","1.5-data-loss-prevention-dlp-and-sensitivity-labels.md",1,"full",["PPAC_PowerShell","Purview_PowerShell"],None),
    ("1.6","1.6-microsoft-purview-dspm-for-ai.md",1,"partial",["Purview_PowerShell"],"Has a DSPM for AI scan been reviewed with findings actioned in the last 30 days?"),
    ("1.7","1.7-comprehensive-audit-logging-and-compliance.md",1,"full",["Purview_PowerShell","Graph_API"],None),
    ("1.8","1.8-runtime-protection-and-external-threat-detection.md",1,"partial",["Sentinel_KQL"],"Have runtime protection alerts been reviewed and tuned in the last 30 days?"),
    ("1.9","1.9-data-retention-and-deletion-policies.md",1,"full",["Purview_PowerShell"],None),
    ("1.10","1.10-communication-compliance-monitoring.md",1,"partial",["Purview_PowerShell"],"Has the supervision review queue been reviewed by a compliance officer in the last 30 days?"),
    ("1.11","1.11-conditional-access-and-phishing-resistant-mfa.md",1,"partial",["Graph_API"],"Provide evidence that sign-in frequency and persistent-browser session controls are set per governance zone (Zone 2 at most 12 hours, Zone 3 at most 4 hours) and that phishing-resistant MFA (for example FIDO2, device-bound passkeys, Windows Hello for Business, or CBA) is enforced for maker/admin identities."),
    ("1.12","1.12-insider-risk-detection-and-response.md",1,"manual",[],"Provide quarterly Purview portal evidence that Insider Risk policies covering agent use are enabled and alerts were reviewed and dispositioned."),
    ("1.13","1.13-sensitive-information-types-sits-and-pattern-recognition.md",1,"partial",["Purview_PowerShell","PPAC_PowerShell"],"Are custom SITs for your institution's regulated data types (account numbers, CRD numbers) configured and validated?"),
    ("1.14","1.14-data-minimization-and-agent-scope-control.md",1,"manual",[],"Has data minimization been applied to restrict agent context to only the data necessary for each agent's specific function?"),
    ("1.15","1.15-encryption-data-in-transit-and-at-rest.md",1,"manual",[],"Provide manual evidence that TLS 1.2+ (or stronger) is enforced for agent data in transit and that at-rest encryption is enabled for Microsoft 365 and any connected customer-managed data stores."),
    ("1.16","1.16-information-rights-management-irm-for-documents.md",1,"manual",[],"Are IRM protections applied to sensitive documents accessible to agents, and has IRM labeling been validated end-to-end?"),
    ("1.17","1.17-endpoint-data-loss-prevention-endpoint-dlp.md",1,"partial",["Purview_PowerShell"],"Is endpoint DLP enforced on all endpoints from which agents are accessed, including unmanaged devices?"),
    ("1.18","1.18-application-level-authorization-and-role-based-access-control-rbac.md",1,"partial",["Graph_API"],"Has a least-privilege access review for all agent administrative roles been completed in the last 90 days?"),
    ("1.19","1.19-ediscovery-for-agent-interactions.md",1,"full",["Purview_PowerShell"],None),
    ("1.20","1.20-network-isolation-private-connectivity.md",1,"full",["Azure_API"],None),
    ("1.21","1.21-adversarial-input-logging.md",1,"partial",["Purview_PowerShell"],"Is adversarial input logging reviewed on a scheduled basis, and are prompt injection attempts being tracked?"),
    ("1.22","1.22-information-barriers.md",1,"full",["Purview_PowerShell"],None),
    ("1.23","1.23-step-up-authentication-for-agent-operations.md",1,"partial",["Graph_API"],"Has step-up authentication been tested end-to-end for all Zone 3 operations in the last 60 days?"),
    ("1.24","1.24-defender-ai-security-posture-management.md",1,"manual",["Azure_API"],"Provide evidence of weekly (Zone 2) or daily (Zone 3) security recommendation reviews, including reviewer names, dates, and actions taken on identified AI security gaps."),
    ("1.25","1.25-mime-type-restrictions.md",1,"full",["PPAC_PowerShell"],None),
    ("1.26","1.26-agent-file-upload-and-file-analysis-restrictions.md",1,"partial",["PPAC_REST","Graph_API"],"Provide the approval documentation for each agent with file upload enabled, demonstrating that approval is appropriate to the agent's governance zone."),
    ("1.27","1.27-ai-agent-content-moderation-enforcement.md",1,"full",["PPAC_REST","Graph_API"],None),
    ("1.28","1.28-policy-based-agent-publishing-restrictions.md",1,"full",["PPAC_PowerShell"],None),
    ("1.29","1.29-global-secure-access-network-controls.md",1,"partial",["Graph_API"],"Provide evidence of weekly (Zone 2) or daily (Zone 3) GSA traffic log review, including reviewer names, dates, false positive assessments, and escalation decisions for anomalous blocked requests."),
    # Pillar 2 - Management (26)
    ("2.1","2.1-managed-environments.md",2,"full",["PPAC_PowerShell"],None),
    ("2.2","2.2-environment-groups-and-tier-classification.md",2,"full",["PPAC_PowerShell"],None),
    ("2.3","2.3-change-management-and-release-planning.md",2,"partial",["PPAC_PowerShell"],"Is the change management workflow enforced for all Zone 3 agent promotions, with evidence stored in your ITSM system?"),
    ("2.4","2.4-business-continuity-and-disaster-recovery.md",2,"partial",["SharePoint_Graph"],"Has a business continuity failover test been executed and documented for agent-dependent processes in the last 12 months?"),
    ("2.5","2.5-testing-validation-and-quality-assurance.md",2,"manual",[],"Is there a documented QA process requiring test coverage for agent responses before Zone 2 or Zone 3 promotion?"),
    ("2.6","2.6-model-risk-management-sr-26-2.md",2,"manual",[],"Has a model risk management review (aligned to OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Fed SR 26-2 (formerly Fed SR 11-7)) been completed for any agents serving regulated functions?"),
    ("2.7","2.7-vendor-and-third-party-risk-management.md",2,"manual",[],"Has a vendor risk assessment been completed for all third-party connectors and plugins used by production agents?"),
    ("2.8","2.8-access-control-and-segregation-of-duties.md",2,"partial",["Graph_API"],"Has a segregation of duties review confirmed that no individual has both agent development and production publishing rights?"),
    ("2.9","2.9-agent-performance-monitoring-and-optimization.md",2,"partial",["PPAC_PowerShell"],"Are agent performance metrics (latency, fallback rate, escalation rate) reviewed on a scheduled cadence?"),
    ("2.10","2.10-patch-management-and-system-updates.md",2,"partial",["PPAC_PowerShell"],"Is there a documented patch management process for reviewing and applying Copilot Studio platform updates?"),
    ("2.11","2.11-bias-testing-and-fairness-assessment.md",2,"manual",[],"Has bias testing been performed for agents that make recommendations affecting customers, with results documented and reviewed?"),
    ("2.12","2.12-supervision-and-oversight-finra-rule-3110.md",2,"manual",[],"Is there a designated supervisory principal for each production agent per FINRA Rule 3110, with a documented review cadence?"),
    ("2.13","2.13-documentation-and-record-keeping.md",2,"manual",[],"Is a complete governance record maintained per agent (owner, purpose, data sources, approval chain, test results)?"),
    ("2.14","2.14-training-and-awareness-program.md",2,"manual",[],"Have all agent developers, publishers, and administrators completed AI governance training in the last 12 months?"),
    ("2.15","2.15-environment-routing.md",2,"full",["PPAC_PowerShell"],None),
    ("2.16","2.16-rag-source-integrity-validation.md",2,"partial",["SharePoint_Graph"],"Are all SharePoint knowledge sources scanned for accuracy and currency on a documented schedule?"),
    ("2.17","2.17-multi-agent-orchestration-limits.md",2,"partial",["PPAC_PowerShell"],"Have multi-agent orchestration workflows been reviewed for circular delegation and privilege escalation risks?"),
    ("2.18","2.18-automated-conflict-of-interest-testing.md",2,"manual",[],"Has automated conflict-of-interest testing been performed for agents that surface investment recommendations or research?"),
    ("2.19","2.19-customer-ai-disclosure-and-transparency.md",2,"manual",[],"Is there clear AI disclosure language presented to customers before they interact with any customer-facing agent?"),
    ("2.20","2.20-adversarial-testing-and-red-team-framework.md",2,"manual",[],"Has a red team or adversarial testing exercise been conducted for Zone 3 agents, with findings tracked to resolution?"),
    ("2.21","2.21-ai-marketing-claims-and-substantiation.md",2,"manual",[],"Have all AI marketing claims referencing agent capabilities been reviewed for substantiation and regulatory accuracy?"),
    ("2.22","2.22-inactivity-timeout-enforcement.md",2,"full",["PPAC_REST"],None),
    ("2.23","2.23-user-consent-and-ai-disclosure-enforcement.md",2,"manual",[],"Is user consent captured and logged before any agent accesses personal data, with consent records retained per policy?"),
    ("2.24","2.24-agent-feature-enablement-and-restriction-governance.md",2,"full",["PPAC_PowerShell"],None),
    ("2.25","2.25-agent-365-admin-center-governance-console.md",2,"full",["Graph_API"],None),
    ("2.26","2.26-entra-agent-id-identity-governance.md",2,"full",["Graph_API"],None),
    # Pillar 3 - Reporting (14)
    ("3.1","3.1-agent-inventory-and-metadata-management.md",3,"full",["Graph_API"],None),
    ("3.2","3.2-usage-analytics-and-activity-monitoring.md",3,"manual",[],"Is agent usage reported to compliance and risk leadership on a regular schedule, with anomalies flagged?"),
    ("3.3","3.3-compliance-and-regulatory-reporting.md",3,"partial",["SharePoint_Graph"],"Are AI-specific incidents (hallucinations, data leakage, unexpected outputs) logged separately from general IT incidents?"),
    ("3.4","3.4-incident-reporting-and-root-cause-analysis.md",3,"partial",["SharePoint_Graph"],"Is there an active exception register for controls not yet implemented, with risk acceptance signatures?"),
    ("3.5","3.5-cost-allocation-and-budget-tracking.md",3,"full",["PPAC_PowerShell"],None),
    ("3.6","3.6-orphaned-agent-detection-and-remediation.md",3,"manual",[],"Are orphaned agents (no active owner) reviewed at least quarterly and decommissioned or reassigned?"),
    ("3.7","3.7-ppac-security-posture-assessment.md",3,"full",["PPAC_PowerShell"],None),
    ("3.8","3.8-copilot-hub-and-governance-dashboard.md",3,"manual",[],"Is there a hallucination feedback loop \u2014 a mechanism for users to flag incorrect agent outputs \u2014 with review and remediation?"),
    ("3.9","3.9-microsoft-sentinel-integration.md",3,"full",["Sentinel_KQL"],None),
    ("3.10","3.10-hallucination-feedback-loop.md",3,"manual",[],"Are Sentinel alerts for agent-related security signals reviewed by the SOC on a documented cadence?"),
    ("3.11","3.11-centralized-agent-inventory-enforcement.md",3,"manual",[],"Is there a defined exception management process with documented risk acceptance for controls not yet at target maturity?"),
    ("3.12","3.12-agent-governance-exception-and-override-management.md",3,"manual",[],"Are regulatory reporting obligations (SAR, FINRA CAT, exam readiness) specifically addressed in your agent governance program?"),
    ("3.13","3.13-agent-365-admin-center-analytics.md",3,"manual",[],"Has the governance program been reviewed by Internal Audit or an independent risk function in the last 12 months?"),
    ("3.14","3.14-agent-365-observability-sdk.md",3,"manual",[],"Is there a process to track and action changes to applicable regulations (FINRA, SEC, OCC, Fed, FDIC, NCUA) as they affect agents?"),
    # Pillar 4 - SharePoint (9)
    ("4.1","4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md",4,"partial",["SharePoint_Graph"],"Have access reviews been completed for all SharePoint sites used as agent knowledge sources in the last 90 days?"),
    ("4.2","4.2-site-access-reviews-and-certification.md",4,"partial",["SharePoint_Graph"],"Are retention labels consistently applied to all documents in agent knowledge sources, not just at the site level?"),
    ("4.3","4.3-site-and-document-retention-management.md",4,"full",["SharePoint_Graph"],None),
    ("4.4","4.4-guest-and-external-user-access-controls.md",4,"full",["SharePoint_Graph"],None),
    ("4.5","4.5-sharepoint-security-and-compliance-monitoring.md",4,"partial",["SharePoint_Graph"],"Has a knowledge source scan been run in the last 30 days and findings reviewed by a content owner?"),
    ("4.6","4.6-grounding-scope-governance.md",4,"full",["PPAC_PowerShell","SharePoint_Graph"],None),
    ("4.7","4.7-microsoft-365-copilot-data-governance.md",4,"manual",[],"Are embedded files within SharePoint (PDFs, attachments) included in the grounding scope review, not just top-level documents?"),
    ("4.8","4.8-item-level-permission-scanning-agent-knowledge-sources.md",4,"full",["SharePoint_Graph"],None),
    ("4.9","4.9-embedded-file-content-governance.md",4,"manual",[],"Are embedded files within SharePoint (PDFs, attachments) included in the grounding scope review, not just top-level documents?"),
]

# Pre-defined checks per control (derived from spec API surface hints + control verification criteria)
CHECKS_DB = {
    "1.1": [
        ("1.1.a","Environment Maker role not assigned to All Users","Get-AdminPowerAppEnvironmentRoleAssignment","no_everyone_assignment",[1,2,3]),
        ("1.1.b","Agent publisher security group exists (FSI-Agent-Publishers-Prod)","Get-MgGroup","fsi_publisher_group_exists",[2,3]),
        ("1.1.c","Share with Everyone disabled across environments","Get-TenantSettings","share_everyone_disabled",[3]),
    ],
    "1.2": [
        ("1.2.a","Agent inventory maintained with all agents registered","Get-MgServicePrincipal","agent_inventory_exists",[1,2,3]),
        ("1.2.b","Authentication mode configured per agent","Get-MgServicePrincipal","auth_mode_configured",[2,3]),
        ("1.2.c","No orphaned agents (all have active owner)","Get-MgServicePrincipal","no_orphaned_agents",[3]),
    ],
    "1.3": [
        ("1.3.a","SharePoint permission inheritance not broken on grounding sites","Get-MgSitePermission","permission_inheritance_intact",[1,2,3]),
        ("1.3.b","No oversharing detected on knowledge source sites","Get-MgSitePermission","no_oversharing",[2,3]),
    ],
    "1.4": [
        ("1.4.a","DLP policy exists covering agent environments","Get-DlpPolicy","dlp_policy_exists",[1,2,3]),
        ("1.4.b","ACP allowlist configured for approved connectors","Get-DlpPolicy","acp_allowlist_configured",[2,3]),
        ("1.4.c","Blocked connector list enforced","Get-DlpPolicy","blocked_connectors_enforced",[3]),
    ],
    "1.5": [
        ("1.5.a","DLP policy scoped to agent environments","Get-DlpPolicy","dlp_scope_covers_agents",[1,2,3]),
        ("1.5.b","Sensitivity label policies enabled","Get-LabelPolicy","sensitivity_labels_enabled",[2,3]),
    ],
    "1.6": [
        ("1.6.a","DSPM for AI policy exists in Purview","Get-DlpCompliancePolicy","dspm_policy_exists",[2,3]),
    ],
    "1.7": [
        ("1.7.a","Unified audit logging enabled","Get-AdminAuditLogConfig","audit_log_enabled",[1,2,3]),
        ("1.7.b","M365 Audit plan tier is E5 or equivalent","Get-MgSubscribedSku","audit_plan_tier_adequate",[2,3]),
    ],
    "1.8": [
        ("1.8.a","Sentinel alerts configured for agent anomalies","Invoke-AzOperationalInsightsQuery","sentinel_agent_alerts_exist",[2,3]),
    ],
    "1.9": [
        ("1.9.a","Retention policy scoped to Copilot interactions exists","Get-RetentionCompliancePolicy","copilot_retention_policy_exists",[1,2,3]),
        ("1.9.b","Retention duration meets zone requirements","Get-RetentionCompliancePolicy","retention_duration_adequate",[2,3]),
    ],
    "1.10": [
        ("1.10.a","Communication compliance policy targeting agents exists","Get-SupervisoryReviewPolicyV2","comm_compliance_policy_exists",[2,3]),
    ],
    "1.11": [
        ("1.11.a","CA policy targeting Copilot Studio app enforces MFA","Get-MgIdentityConditionalAccessPolicy","ca_policy_requires_mfa",[1,2,3]),
        ("1.11.b","Sign-in frequency policy set for agent sessions (manual evidence required)","Get-MgIdentityConditionalAccessPolicy","",[2,3],["Manual"]),
        ("1.11.c","Phishing-resistant MFA required for Zone 3 (manual evidence required)","Get-MgIdentityConditionalAccessPolicy","",[3],["Manual"]),
    ],
    "1.12": [],  # manual only (portal evidence required)
    "1.13": [
        ("1.13.a","SIT inventory in Purview covers regulated data types (manual evidence required)","Get-DlpSensitiveInformationType","",[2,3],["Manual"]),
        ("1.13.b","Enforced DLP policy rules reference SIT conditions","Get-DlpCompliancePolicy","dlp_references_sits",[2,3]),
    ],
    "1.14": [],  # manual only
    "1.15": [],  # manual only (tenant/org surface does not expose TLS/at-rest proof)
    "1.16": [],  # manual only
    "1.17": [
        ("1.17.a","Endpoint DLP policy exists in Purview","Get-DlpCompliancePolicy","endpoint_dlp_policy_exists",[2,3]),
    ],
    "1.18": [
        ("1.18.a","RBAC role assignments readable and least-privilege enforced","Get-MgRoleManagementDirectoryRoleAssignment","rbac_least_privilege",[1,2,3]),
        ("1.18.b","No excessive admin role assignments for agent operations","Get-MgRoleManagementDirectoryRoleAssignment","no_excessive_admin",[2,3]),
    ],
    "1.19": [
        ("1.19.a","eDiscovery case includes agent interaction data source","Get-ComplianceCase","ediscovery_agent_scope",[2,3]),
        ("1.19.b","eDiscovery search covers Copilot interaction content types","Get-ComplianceCase","ediscovery_copilot_content",[3]),
    ],
    "1.20": [
        ("1.20.a","Private endpoint or VNet integration configured for PPAC","Get-AzPrivateEndpointConnection","private_endpoint_exists",[3]),
        ("1.20.b","Network isolation enforced for production environments","Get-AzPrivateEndpointConnection","network_isolation_enforced",[3]),
    ],
    "1.21": [
        ("1.21.a","Audit log captures prompt/response pairs","Get-AdminAuditLogConfig","prompt_response_logging",[2,3]),
    ],
    "1.22": [
        ("1.22.a","Information barrier policy exists and is active","Get-InformationBarrierPolicy","ib_policy_active",[2,3]),
        ("1.22.b","IB segments cover agent-accessible data boundaries","Get-InformationBarrierPolicy","ib_segments_configured",[3]),
    ],
    "1.23": [
        ("1.23.a","Step-up authentication companion solution deployed","Get-MgIdentityConditionalAccessPolicy","stepup_auth_deployed",[3]),
    ],
    "1.24": [],  # manual only
    "1.25": [
        ("1.25.a","MIME type restrictions configured per zone template","Test-FsiMimeCompliance","mime_zone_compliant",[1,2,3]),
        ("1.25.b","Blocked file extensions enforced","Get-FsiMimeConfig","blocked_extensions_enforced",[2,3]),
    ],
    "1.26": [
        ("1.26.a","File upload toggle state per agent is zone-appropriate","Get-CopilotStudioAgentConfig","file_upload_zone_appropriate",[2,3]),
        ("1.26.b","Sensitivity label inheritance configured for uploaded files","Get-MgSiteDriveItem","label_inheritance_configured",[3]),
    ],
    "1.27": [
        ("1.27.a","Content moderation level set per agent","Get-CopilotStudioAgentConfig","moderation_level_set",[1,2,3]),
        ("1.27.b","Per-prompt moderation level meets zone minimum (Moderate for Z2, High for Z3)","Get-CopilotStudioAgentConfig","moderation_zone_compliant",[2,3]),
        ("1.27.c","Custom safety messages configured for Zone 3 agents","Get-CopilotStudioAgentConfig","safety_messages_configured",[3]),
    ],
    "1.28": [
        ("1.28.a","DLP publishing restrictions enforced in agent environments","Get-DlpPolicy","dlp_publishing_restrictions",[2,3]),
        ("1.28.b","Security scan gate enabled for production publishing","Get-DlpPolicy","security_scan_enabled",[3]),
    ],
    "1.29": [
        ("1.29.a","GSA baseline profile linked to Copilot Studio CA policy","Get-MgIdentityConditionalAccessPolicy","gsa_profile_linked",[2,3]),
        ("1.29.b","Web content filtering policy blocks unapproved categories","Get-MgIdentityConditionalAccessPolicy","wcf_policy_configured",[3]),
    ],
    # Pillar 2
    "2.1": [
        ("2.1.a","All production environments have IsManaged: true","Get-AdminPowerAppEnvironment","prod_env_is_managed",[1,2,3]),
        ("2.1.b","Managed environment policies enforced","Get-AdminPowerAppEnvironment","managed_policies_enforced",[2,3]),
    ],
    "2.2": [
        ("2.2.a","Environment groups exist with zone mapping","Get-AdminPowerAppEnvironment","env_groups_exist",[1,2,3]),
        ("2.2.b","Zone 1/2/3 tier classification present for all environments","Get-AdminPowerAppEnvironment","tier_classification_present",[2,3]),
    ],
    "2.3": [
        ("2.3.a","Approval workflow present for agent promotions","Get-AdminFlow","approval_workflow_exists",[2,3]),
    ],
    "2.4": [
        ("2.4.a","DR documentation present in SharePoint governance site","Get-MgSiteDriveItem","dr_documentation_exists",[2,3]),
    ],
    "2.5": [],  # manual only
    "2.6": [],  # manual only
    "2.7": [],  # manual only
    "2.8": [
        ("2.8.a","Role assignments match SoD matrix","Get-MgRoleManagementDirectoryRoleAssignment","sod_matrix_match",[2,3]),
        ("2.8.b","No individual holds both dev and prod publishing rights","Get-MgRoleManagementDirectoryRoleAssignment","no_dev_prod_overlap",[3]),
    ],
    "2.9": [
        ("2.9.a","Usage metrics available in PPAC for agent environments","Get-AdminPowerAppEnvironment","usage_metrics_available",[2,3]),
    ],
    "2.10": [
        ("2.10.a","Copilot Studio version and connector versions retrievable","Get-AdminPowerAppEnvironment","version_info_available",[2,3]),
    ],
    "2.11": [],  # manual only
    "2.12": [],  # manual only
    "2.13": [],  # manual only
    "2.14": [],  # manual only
    "2.15": [
        ("2.15.a","Environment routing rules configured","Get-AdminPowerAppEnvironment","routing_rules_configured",[2,3]),
        ("2.15.b","Routing enforces zone boundaries","Get-AdminPowerAppEnvironment","routing_zone_enforced",[3]),
    ],
    "2.16": [
        ("2.16.a","RAG source validation companion solution deployed","Get-MgSiteDriveItem","rag_validation_deployed",[2,3]),
    ],
    "2.17": [
        ("2.17.a","Multi-agent orchestration limits set in PPAC","Get-AdminPowerAppEnvironment","orchestration_limits_set",[2,3]),
    ],
    "2.18": [],  # manual only
    "2.19": [],  # manual only
    "2.20": [],  # manual only
    "2.21": [],  # manual only
    "2.22": [
        ("2.22.a","Inactivity timeout configured per environment","Get-AdminPowerAppEnvironmentSetting","timeout_configured",[2,3]),
        ("2.22.b","Timeout value meets zone requirements (8h Zone2, 4h Zone3)","Get-AdminPowerAppEnvironmentSetting","timeout_value_adequate",[2,3]),
    ],
    "2.23": [],  # manual only
    "2.24": [
        ("2.24.a","Generative AI feature flags reviewed per environment","Get-AdminPowerAppEnvironment","genai_flags_reviewed",[1,2,3]),
        ("2.24.b","External plugin toggles set per zone policy","Get-AdminPowerAppEnvironment","external_plugins_controlled",[2,3]),
    ],
    "2.25": [
        ("2.25.a","Agent 365 Admin Center governance console accessible","Get-MgServicePrincipal","agent365_console_accessible",[2,3]),
        ("2.25.b","Agent inventory visible in governance console","Get-MgServicePrincipal","agent365_inventory_visible",[2,3]),
    ],
    "2.26": [
        ("2.26.a","Entra Agent ID identities registered with sponsors","Get-MgIdentityGovernanceLifecycleWorkflow","agent_ids_registered",[2,3]),
        ("2.26.b","Access packages configured for agent resource bundles","Get-MgEntitlementManagementAccessPackage","access_packages_configured",[3]),
    ],
    # Pillar 3
    "3.1": [
        ("3.1.a","Agent inventory exportable with owner and classification","Get-MgServicePrincipal","agent_inventory_exportable",[1,2,3]),
        ("3.1.b","All agents have classification tag assigned","Get-MgServicePrincipal","all_agents_classified",[2,3]),
    ],
    "3.2": [],  # manual only
    "3.3": [
        ("3.3.a","Incident log location detectable in SharePoint or ticketing system","Get-MgSiteDriveItem","incident_log_exists",[2,3]),
    ],
    "3.4": [
        ("3.4.a","Exception management process document present in governance site","Get-MgSiteDriveItem","exception_doc_exists",[2,3]),
    ],
    "3.5": [
        ("3.5.a","Usage reporting dashboard enabled in PPAC","Get-AdminPowerAppEnvironment","usage_dashboard_enabled",[1,2,3]),
        ("3.5.b","Data export configured for cost tracking","Get-AdminPowerAppEnvironment","data_export_configured",[2,3]),
    ],
    "3.6": [],  # manual only
    "3.7": [
        ("3.7.a","PPAC Security Posture score retrievable","Get-AdminPowerAppEnvironment","security_posture_retrievable",[1,2,3]),
        ("3.7.b","Security posture score meets minimum threshold","Get-AdminPowerAppEnvironment","posture_score_adequate",[2,3]),
    ],
    "3.8": [],  # manual only
    "3.9": [
        ("3.9.a","Sentinel workspace linked to PPAC tenant","Get-AzOperationalInsightsWorkspace","sentinel_workspace_linked",[2,3]),
        ("3.9.b","Audit logs ingested into Sentinel workspace","Invoke-AzOperationalInsightsQuery","audit_logs_ingested",[2,3]),
    ],
    "3.10": [],  # manual only
    "3.11": [],  # manual only
    "3.12": [],  # manual only
    "3.13": [],  # manual only
    "3.14": [],  # manual only
    # Pillar 4
    "4.1": [
        ("4.1.a","SharePoint site permissions readable for grounding sites","Get-MgSitePermission","site_permissions_readable",[1,2,3]),
        ("4.1.b","IAG restricted content discovery enabled","Get-MgSitePermission","iag_rcd_enabled",[2,3]),
    ],
    "4.2": [
        ("4.2.a","Retention labels applied to SharePoint grounding sites","Get-MgSiteList","retention_labels_applied",[1,2,3]),
    ],
    "4.3": [
        ("4.3.a","Retention policies applied to SharePoint sites used for agent grounding","Get-RetentionCompliancePolicy","sp_retention_applied",[1,2,3]),
        ("4.3.b","Retention duration meets regulatory minimums","Get-RetentionCompliancePolicy","sp_retention_duration_ok",[2,3]),
    ],
    "4.4": [
        ("4.4.a","External sharing disabled on grounding sites","Get-MgSite","no_external_sharing_on_grounding",[1,2,3]),
        ("4.4.b","Guest access disabled on knowledge source sites","Get-MgSite","guest_access_disabled",[2,3]),
    ],
    "4.5": [
        ("4.5.a","Knowledge source scanning companion solution present","Get-MgSiteDriveItem","knowledge_scan_present",[2,3]),
    ],
    "4.6": [
        ("4.6.a","Grounding scope restricted to approved sites only","Get-AdminPowerAppEnvironment","grounding_scope_restricted",[1,2,3]),
        ("4.6.b","No unapproved sites in agent knowledge source configuration","Get-MgSite","grounding_sources_approved",[2,3]),
    ],
    "4.7": [],  # manual only
    "4.8": [
        ("4.8.a","Item-level permissions scanned on knowledge source files","Get-MgSiteDriveItemPermission","item_permissions_scanned",[1,2,3]),
        ("4.8.b","No oversharing detected (no Everyone or Everyone-except-external)","Get-MgSiteDriveItemPermission","no_item_oversharing",[2,3]),
    ],
    "4.9": [],  # manual only
}

ZONE_THRESHOLD_OVERRIDES = {
    "1.13": {
        "zone1": {"min_checks_passed": 0, "maturity_score": 0},
        "zone2": {"min_checks_passed": 1, "maturity_score": 2},
        "zone3": {"min_checks_passed": 1, "maturity_score": 4},
    },
}

AUTHORITATIVE_CONTROL_IDS = {"1.11", "1.13"}


def extract_title(filepath):
    """Extract control title from the first H1 or metadata line."""
    try:
        with filepath.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    # Remove markdown heading and any control ID prefix
                    title = line.lstrip("# ").strip()
                    # Remove "Control X.Y – " or "X.Y " prefix if present
                    title = re.sub(r"^Control\s+\d+\.\d+\s*[\u2013\u2014–—-]\s*", "", title)
                    title = re.sub(r"^\d+\.\d+\s*[\u2013\u2014–—-]\s*", "", title)
                    return title
                # Check metadata header for title
                m = re.match(r"title:\s*(.+)", line, re.IGNORECASE)
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    except Exception:
        pass
    return None


def build_control(cid, filename, pillar, automation, methods, manual_q):
    pillar_dir, pillar_name = PILLAR_DIRS[pillar]
    source_file = f"docs/controls/{pillar_dir}/{filename}"
    filepath = BASE / pillar_dir / filename

    # Extract title from file
    title = extract_title(filepath)
    if not title:
        # Derive from filename
        title = filename.replace(".md", "").split("-", 1)[-1].replace("-", " ").title()

    # Get checks
    checks_raw = CHECKS_DB.get(cid, [])
    checks = []
    auto_evaluable_checks = []
    for check_data in checks_raw:
        check_id, desc, api_call, pass_cond, zones, *metadata = check_data
        check = {
            "check_id": check_id,
            "description": desc,
            "api_call": api_call,
            "pass_condition": pass_cond,
        }
        if metadata:
            check["collection_methods"] = metadata[0]
        check["zone_required"] = zones
        checks.append(check)
        if pass_cond and check.get("collection_methods") != ["Manual"]:
            auto_evaluable_checks.append(check)

    # Manual-only checks must never inflate automated pass thresholds.
    total = len(auto_evaluable_checks)
    if total == 0:
        # Manual-only controls
        zone_thresholds = {
            "zone1": {"min_checks_passed": 0, "maturity_score": 0},
            "zone2": {"min_checks_passed": 0, "maturity_score": 0},
            "zone3": {"min_checks_passed": 0, "maturity_score": 0},
        }
    elif total == 1:
        zone_thresholds = {
            "zone1": {"min_checks_passed": 1, "maturity_score": 1},
            "zone2": {"min_checks_passed": 1, "maturity_score": 2},
            "zone3": {"min_checks_passed": 1, "maturity_score": 4},
        }
    elif total == 2:
        zone_thresholds = {
            "zone1": {"min_checks_passed": 1, "maturity_score": 1},
            "zone2": {"min_checks_passed": 2, "maturity_score": 2},
            "zone3": {"min_checks_passed": 2, "maturity_score": 4},
        }
    else:
        z2_min = max(1, int(total * 0.65))
        zone_thresholds = {
            "zone1": {"min_checks_passed": 1, "maturity_score": 1},
            "zone2": {"min_checks_passed": z2_min, "maturity_score": 2},
            "zone3": {"min_checks_passed": total, "maturity_score": 4},
        }
    zone_thresholds = ZONE_THRESHOLD_OVERRIDES.get(cid, zone_thresholds)

    return {
        "id": cid,
        "title": title,
        "pillar": pillar,
        "pillar_name": pillar_name,
        "source_file": source_file,
        "automation": automation,
        "collection_methods": methods,
        "checks": checks,
        "zone_thresholds": zone_thresholds,
        "manual_question": manual_q,
    }


def render_manifest(existing_controls=None):
    generated_by_id = {}
    for cid, filename, pillar, automation, methods, manual_q in CONTROLS:
        generated_by_id[cid] = build_control(
            cid, filename, pillar, automation, methods, manual_q
        )

    if not existing_controls:
        return list(generated_by_id.values())

    controls = []
    for existing in existing_controls:
        entry = existing.copy()
        if existing["id"] in AUTHORITATIVE_CONTROL_IDS:
            entry.update(generated_by_id[existing["id"]])
        controls.append(entry)
    return controls


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if generated content differs from controls.json.",
    )
    args = parser.parse_args(argv)

    existing_controls = []
    if OUTPUT.exists():
        existing_controls = json.loads(OUTPUT.read_text(encoding="utf-8"))
    controls = render_manifest(existing_controls)
    rendered = json.dumps(controls, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != rendered:
            print(f"Manifest drift detected: run {Path(__file__).name}")
            return 1
        print("Manifest is reproducible.")
        return 0

    print(f"Generated {len(controls)} controls")
    print(f"  Pillar 1: {sum(1 for c in controls if c['pillar']==1)}")
    print(f"  Pillar 2: {sum(1 for c in controls if c['pillar']==2)}")
    print(f"  Pillar 3: {sum(1 for c in controls if c['pillar']==3)}")
    print(f"  Pillar 4: {sum(1 for c in controls if c['pillar']==4)}")
    print(f"  Full: {sum(1 for c in controls if c['automation']=='full')}")
    print(f"  Partial: {sum(1 for c in controls if c['automation']=='partial')}")
    print(f"  Manual: {sum(1 for c in controls if c['automation']=='manual')}")

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"\nWritten to {OUTPUT}")
    print(f"File size: {OUTPUT.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
