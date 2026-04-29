#!/usr/bin/env python3
"""FSI-AgentGov Assessment Scoring Engine.

Evaluates collected telemetry against the control manifest to produce
maturity scores, evidence records, and a per-control + summary output.

Usage::

    python score.py --manifest <controls.json> --collected <dir> \
                    --zone <1|2|3> --output <scores.json>
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

ENGINE_VERSION = "1.0.0"

log = logging.getLogger("fsi-agentgov-score")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COPILOT_STUDIO_APP_ID = "96ff4394-9197-43aa-b393-6a41652e21f8"

MATURITY_LABELS: dict[int, str] = {
    0: "Not Implemented",
    1: "Aware",
    2: "Recommended",
    3: "Optimized",
    4: "Fully Governed",
}

ZONE_DESCRIPTIONS: dict[int, str] = {
    1: "Personal / Low Risk",
    2: "Team / Medium Risk",
    3: "Enterprise / Production",
}

# Map api_call values from controls.json → collected-data source key.
API_SOURCE_MAP: dict[str, str] = {
    # Power Platform Admin Center
    "Get-AdminPowerAppEnvironmentRoleAssignment": "ppac",
    "Get-AdminPowerAppEnvironment": "ppac",
    "Get-AdminPowerAppDlpPolicy": "ppac",
    "Get-AdminPowerAppTenantSetting": "ppac",
    "Get-AdminPowerAppConnector": "ppac",
    # Microsoft Graph
    "Get-MgGroup": "graph",
    "Get-MgIdentityConditionalAccessPolicy": "graph",
    "Get-MgDirectoryRole": "graph",
    "Get-MgDirectoryRoleMember": "graph",
    "Get-MgApplication": "graph",
    "Get-MgServicePrincipal": "graph",
    # Purview / Compliance Center
    "Get-AdminAuditLogConfig": "purview",
    "Get-RetentionCompliancePolicy": "purview",
    "Get-DlpCompliancePolicy": "purview",
    "Get-Label": "purview",
    "Get-InsiderRiskPolicy": "purview",
    "Get-ComplianceCase": "purview",
    # SharePoint
    "Get-PnPSiteSearchQueryResults": "sharepoint",
    "Get-PnPTenantSite": "sharepoint",
    "Get-PnPSite": "sharepoint",
    "Get-PnPSiteCollectionAdmin": "sharepoint",
    "Get-PnPListItem": "sharepoint",
    # Sentinel
    "Get-AzSentinelWorkspace": "sentinel",
    "Get-AzSentinelDataConnector": "sentinel",
    "Get-AzSentinelAlertRule": "sentinel",
}

# Map collection_methods from controls.json → source key.
COLLECTION_METHOD_SOURCE: dict[str, str | None] = {
    "PPAC_PowerShell": "ppac",
    "PPAC_REST": "ppac",
    "Graph_API": "graph",
    "Purview_PowerShell": "purview",
    "SharePoint_PnP": "sharepoint",
    "Sentinel": "sentinel",
    "Manual": None,
}

# Source key → expected filename in the collected directory.
SOURCE_FILENAMES: dict[str, str] = {
    "ppac": "ppac.json",
    "graph": "graph.json",
    "purview": "purview.json",
    "sharepoint": "sharepoint.json",
    "sentinel": "sentinel.json",
}

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict:
    """Load and parse a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_collected_data(collected_dir: Path) -> dict[str, dict | None]:
    """Load all collected JSON files into a dict keyed by source name."""
    collected: dict[str, dict | None] = {}
    for key, filename in SOURCE_FILENAMES.items():
        path = collected_dir / filename
        if path.is_file():
            try:
                collected[key] = load_json(path)
                log.info("Loaded %s from %s", key, path)
            except (json.JSONDecodeError, OSError) as exc:
                log.warning("Failed to load %s: %s", path, exc)
                collected[key] = None
        else:
            log.info("Source file not found: %s", path)
            collected[key] = None
    return collected


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_production_env(env: dict) -> bool:
    """Heuristic: treat an environment as production when its SKU or display
    name indicates production usage."""
    sku = env.get("Properties", {}).get("environmentSku", "").lower()
    name = (env.get("DisplayName") or "").lower()
    return sku == "production" or "prod" in name


def _resolve_source_key(
    api_call: str, collection_methods: list[str] | None
) -> str | None:
    """Determine the collected-data source key for a given API call."""
    source = API_SOURCE_MAP.get(api_call)
    if source:
        return source
    for method in collection_methods or []:
        source = COLLECTION_METHOD_SOURCE.get(method)
        if source:
            return source
    return None


def _source_has_data(collected: dict, source_key: str | None) -> bool:
    return source_key is not None and collected.get(source_key) is not None


# ---------------------------------------------------------------------------
# Pass-condition evaluators
# ---------------------------------------------------------------------------
# Signature: (collected, source_key) -> (passed: bool | None, evidence: str)
# ``None`` for *passed* means the check could not be evaluated ("unknown").


def _eval_no_everyone_assignment(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    ppac = collected.get("ppac")
    if not ppac:
        return None, "PPAC data not available"
    assignments = ppac.get("role_assignments")
    if assignments is None:
        return None, "role_assignments not collected"
    everyone_found: list[str] = []
    env_count = 0
    if isinstance(assignments, dict):
        for env_id, roles in assignments.items():
            env_count += 1
            for role in roles:
                principal = (role.get("PrincipalDisplayName") or "").lower()
                ptype = (role.get("PrincipalType") or "").lower()
                if principal in ("everyone", "all users") or ptype == "tenant":
                    everyone_found.append(env_id)
    if everyone_found:
        return (
            False,
            f"'Everyone' assignment found in {len(everyone_found)} environment(s)",
        )
    label = (
        "production environments"
        if any(_is_production_env(e) for e in ppac.get("environments", []))
        else f"{env_count} environment(s)"
    )
    return True, f"No 'All Users' assignment found in role_assignments for {label}"


def _eval_fsi_publisher_group_exists(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    graph = collected.get("graph")
    if not graph:
        return None, "Graph data not available"
    groups = graph.get("fsi_security_groups")
    if groups is None:
        return None, "fsi_security_groups not collected"
    if isinstance(groups, list) and len(groups) > 0:
        names = [g.get("displayName", "unknown") for g in groups]
        return True, f"FSI publisher security group(s) found: {', '.join(names)}"
    return False, "No FSI publisher security group found in fsi_security_groups"


def _eval_share_everyone_disabled(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    ppac = collected.get("ppac")
    if not ppac:
        return None, "PPAC data not available"
    assignments = ppac.get("role_assignments")
    if assignments is None:
        return None, "role_assignments not collected"
    if isinstance(assignments, dict):
        for env_id, roles in assignments.items():
            for role in roles:
                principal = (role.get("PrincipalDisplayName") or "").lower()
                if principal in ("everyone", "all users"):
                    return (
                        False,
                        f"Share with Everyone found in environment {env_id}",
                    )
    settings = ppac.get("environment_settings") or {}
    if settings.get("shareWithEveryone") is True:
        return False, "shareWithEveryone is enabled in environment settings"
    return True, "Share with Everyone is disabled"


def _eval_ca_policy_targets_copilot_studio(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    graph = collected.get("graph")
    if not graph:
        return None, "Graph data not available"
    policies = graph.get("conditional_access_policies")
    if policies is None:
        return None, "conditional_access_policies not collected"
    for policy in policies:
        if policy.get("state") != "enabled":
            continue
        apps = (
            policy.get("conditions", {})
            .get("applications", {})
            .get("includeApplications", [])
        )
        if COPILOT_STUDIO_APP_ID in apps:
            name = policy.get("displayName", "unnamed")
            return (
                True,
                f"CA policy '{name}' targets app ID {COPILOT_STUDIO_APP_ID}",
            )
    return False, "No enabled CA policy targets Copilot Studio app ID"


def _eval_ca_policy_requires_mfa(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    graph = collected.get("graph")
    if not graph:
        return None, "Graph data not available"
    policies = graph.get("conditional_access_policies")
    if policies is None:
        return None, "conditional_access_policies not collected"
    for policy in policies:
        if policy.get("state") != "enabled":
            continue
        apps = (
            policy.get("conditions", {})
            .get("applications", {})
            .get("includeApplications", [])
        )
        if COPILOT_STUDIO_APP_ID not in apps:
            continue
        controls = policy.get("grantControls", {}).get("builtInControls", [])
        if "mfa" in controls:
            return True, "CA policy includes 'mfa' in builtInControls"
    return False, "No CA policy targeting Copilot Studio requires MFA"


def _eval_prod_env_has_security_group(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    ppac = collected.get("ppac")
    if not ppac:
        return None, "PPAC data not available"
    envs = ppac.get("environments")
    if envs is None:
        return None, "environments not collected"
    prod_envs = [e for e in envs if _is_production_env(e)]
    if not prod_envs:
        return None, "No production environments found"
    ungrouped: list[str] = []
    for env in prod_envs:
        sg = (
            env.get("Properties", {})
            .get("linkedEnvironmentMetadata", {})
            .get("securityGroupId")
        )
        if not sg:
            ungrouped.append(env.get("DisplayName", "unknown"))
    if ungrouped:
        return (
            False,
            f"Production environment(s) without security group: "
            f"{', '.join(ungrouped)}",
        )
    sg_sample = (
        prod_envs[0]
        .get("Properties", {})
        .get("linkedEnvironmentMetadata", {})
        .get("securityGroupId", "")
    )
    name = prod_envs[0].get("DisplayName", "unknown")
    return (
        True,
        f"Environment '{name}' has securityGroupId '{sg_sample}'",
    )


def _eval_prod_env_is_managed(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    ppac = collected.get("ppac")
    if not ppac:
        return None, "PPAC data not available"
    envs = ppac.get("environments")
    if envs is None:
        return None, "environments not collected"
    prod_envs = [e for e in envs if _is_production_env(e)]
    if not prod_envs:
        return None, "No production environments found"
    unmanaged: list[str] = []
    for env in prod_envs:
        state = env.get("States", {}).get("management", {}).get("id", "")
        if state != "Managed":
            unmanaged.append(env.get("DisplayName", "unknown"))
    if unmanaged:
        return (
            False,
            f"Unmanaged production environment(s): {', '.join(unmanaged)}",
        )
    name = prod_envs[0].get("DisplayName", "unknown")
    state = (
        prod_envs[0].get("States", {}).get("management", {}).get("id", "")
    )
    return True, f"Environment '{name}' management state is '{state}'"


def _eval_audit_log_enabled(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    purview = collected.get("purview")
    if not purview:
        return None, "Purview data not available"
    config = purview.get("audit_config")
    if config is None:
        return None, "audit_config not collected"
    enabled = config.get("UnifiedAuditLogIngestionEnabled")
    if enabled is True:
        return True, "UnifiedAuditLogIngestionEnabled is true"
    return False, f"UnifiedAuditLogIngestionEnabled is {enabled}"


def _eval_copilot_retention_policy_exists(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    purview = collected.get("purview")
    if not purview:
        return None, "Purview data not available"
    policies = purview.get("retention_policies")
    if policies is None:
        return None, "retention_policies not collected"
    for policy in policies:
        workload = policy.get("Workload", "")
        if "copilot" in workload.lower() and policy.get("Enabled") is True:
            return (
                True,
                f"Retention policy '{policy.get('Name', 'unknown')}' "
                f"covers {workload} workload",
            )
    return False, "No enabled retention policy covering Copilot workload found"


def _eval_grounding_sources_approved(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    sp = collected.get("sharepoint")
    if not sp:
        return None, "SharePoint data not available"
    scope = sp.get("grounding_scope")
    if scope is None:
        return None, "grounding_scope not collected"
    unapproved = scope.get("unapproved", [])
    if unapproved:
        return (
            False,
            f"{len(unapproved)} unapproved grounding source(s) found",
        )
    return (
        True,
        "All grounding sources in approved list; no unapproved sources found",
    )


def _eval_no_external_sharing_on_grounding(
    collected: dict, _source_key: str | None
) -> tuple[bool | None, str]:
    sp = collected.get("sharepoint")
    if not sp:
        return None, "SharePoint data not available"
    sharing = sp.get("external_sharing")
    if sharing is None:
        return None, "external_sharing not collected"
    sites = sp.get("sites", [])
    enabled_sites: list[str] = []
    for site in sites:
        sid = site.get("id", "")
        cap = sharing.get(sid, site.get("sharingCapability", ""))
        if cap and str(cap).lower() != "disabled":
            enabled_sites.append(site.get("displayName", sid))
    if enabled_sites:
        return (
            False,
            f"External sharing enabled on: {', '.join(enabled_sites)}",
        )
    return True, "External sharing is 'Disabled' on all grounding sites"


# --- Evaluator registry ---------------------------------------------------

EVALUATORS: dict[str, object] = {
    "no_everyone_assignment": _eval_no_everyone_assignment,
    "fsi_publisher_group_exists": _eval_fsi_publisher_group_exists,
    "share_everyone_disabled": _eval_share_everyone_disabled,
    "ca_policy_targets_copilot_studio": _eval_ca_policy_targets_copilot_studio,
    "ca_policy_requires_mfa": _eval_ca_policy_requires_mfa,
    "prod_env_has_security_group": _eval_prod_env_has_security_group,
    "prod_env_is_managed": _eval_prod_env_is_managed,
    "audit_log_enabled": _eval_audit_log_enabled,
    "copilot_retention_policy_exists": _eval_copilot_retention_policy_exists,
    "grounding_sources_approved": _eval_grounding_sources_approved,
    "no_external_sharing_on_grounding": _eval_no_external_sharing_on_grounding,
}


def _generic_evaluate(
    condition: str, collected: dict, source_key: str | None
) -> tuple[bool | None, str]:
    """Best-effort evaluation for unrecognized pass_condition strings."""
    if not _source_has_data(collected, source_key):
        src_label = SOURCE_FILENAMES.get(source_key or "", source_key or "unknown")
        return None, f"Source data not available ({src_label})"
    return (
        None,
        f"Automated evaluation not available for condition '{condition}'",
    )


# ---------------------------------------------------------------------------
# Evaluator-state classification (transparency)
# ---------------------------------------------------------------------------
#
# Every check is classified into one of three explicit states so the
# assessment output cannot silently conflate "manual by design" with
# "we haven't written the evaluator yet".
#
# * ``auto_evaluable`` — pass_condition has a registered bespoke evaluator
#   in EVALUATORS and can be scored from collected telemetry.
# * ``manual_only`` — the check (or its parent control) is intentionally
#   manual: collection_methods is ``["Manual"]`` only, OR the parent
#   control's automation is "manual", OR no pass_condition is defined.
# * ``unimplemented_evaluator`` — a pass_condition is specified and the
#   collection method is automatable, but no bespoke evaluator is
#   registered for it. The generic evaluator will return "unknown".

EVALUATOR_STATES = ("auto_evaluable", "manual_only", "unimplemented_evaluator")


def classify_check_evaluator_state(
    check: dict,
    control_automation: str,
    control_collection_methods: list[str] | None,
) -> str:
    """Classify a single check into one of EVALUATOR_STATES.

    Pure function — depends only on the manifest, not on collected data.
    Used for both runtime output enrichment and the static coverage matrix.
    """
    condition = (check.get("pass_condition") or "").strip()
    if condition and condition in EVALUATORS:
        return "auto_evaluable"

    methods = check.get("collection_methods") or control_collection_methods or []
    automatable_method_present = any(
        COLLECTION_METHOD_SOURCE.get(m) is not None for m in methods
    )

    if (
        control_automation == "manual"
        or not condition
        or (methods and not automatable_method_present)
    ):
        return "manual_only"

    return "unimplemented_evaluator"


def rollup_control_evaluator_state(
    control_automation: str, check_states: list[str]
) -> str:
    """Roll a control's per-check evaluator states into a single state.

    Precedence:
      1. ``auto_evaluable`` — at least one check is auto-evaluable.
      2. ``unimplemented_evaluator`` — has automatable checks but no
         bespoke evaluator implementation (most common gap today).
      3. ``manual_only`` — purely manual control or has no checks.
    """
    if "auto_evaluable" in check_states:
        return "auto_evaluable"
    if "unimplemented_evaluator" in check_states:
        return "unimplemented_evaluator"
    if not check_states and control_automation != "manual":
        # Defensive fallback: no checks defined and not flagged manual.
        return "unimplemented_evaluator"
    return "manual_only"


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------


def evaluate_check(
    check: dict,
    collected: dict,
    zone: int,
    collection_methods: list[str] | None,
    timestamp: str,
    control_automation: str = "full",
) -> dict:
    """Evaluate a single check and return a result dict."""
    check_id: str = check["check_id"]
    zone_required: list[int] = check.get("zone_required", [])
    api_call: str = check.get("api_call", "")
    condition: str = check.get("pass_condition", "")
    description: str = check.get("description", "")

    evaluator_state = classify_check_evaluator_state(
        check, control_automation, collection_methods
    )
    applicable = zone in zone_required

    if not applicable:
        return {
            "check_id": check_id,
            "description": description,
            "zone_required": zone_required,
            "applicable": False,
            "result": "not_applicable",
            "passed": None,
            "value": f"Check not required for zone {zone}",
            "evidence": f"Check not required for zone {zone}",
            "source": None,
            "timestamp": timestamp,
            "data_available": True,
            "evaluator_state": evaluator_state,
        }

    source_key = _resolve_source_key(api_call, collection_methods)
    source_file = SOURCE_FILENAMES.get(source_key or "") if source_key else None
    data_available = _source_has_data(collected, source_key)

    evaluator = EVALUATORS.get(condition)
    if evaluator:
        passed, evidence = evaluator(collected, source_key)
    else:
        passed, evidence = _generic_evaluate(condition, collected, source_key)

    if passed is None:
        result = "unknown"
    elif passed:
        result = "pass"
    else:
        result = "fail"

    return {
        "check_id": check_id,
        "description": description,
        "zone_required": zone_required,
        "applicable": True,
        "result": result,
        "passed": passed,
        "value": evidence,
        "evidence": evidence,
        "source": source_file,
        "timestamp": timestamp,
        "data_available": data_available,
        "evaluator_state": evaluator_state,
    }


def compute_maturity(
    checks_passed: int, zone: int, zone_thresholds: dict
) -> tuple[int, str, int]:
    """Compute maturity score for the assessed zone.

    Only the target zone's threshold is evaluated — lower or higher zones
    are not consulted.

    Returns ``(maturity_score, maturity_label, min_checks_required)``.
    """
    zone_key = f"zone{zone}"
    threshold = zone_thresholds.get(zone_key, {})
    min_required: int = threshold.get("min_checks_passed", 0)
    target_maturity: int = threshold.get("maturity_score", 0)

    if min_required > 0 and checks_passed >= min_required:
        score = target_maturity
    elif min_required == 0:
        # Threshold of zero means no checks needed — award the maturity.
        score = target_maturity
    else:
        score = 0

    label = MATURITY_LABELS.get(score, "Unknown")
    return score, label, min_required


def compute_confidence(check_results: list[dict]) -> str:
    """Derive confidence from data availability across applicable checks.

    * **high** — all applicable checks had data available
    * **medium** — some lacked data
    * **low** — most / all lacked data
    """
    applicable = [c for c in check_results if c["applicable"]]
    if not applicable:
        return "low"
    # A check has usable data only if its source loaded AND the evaluator
    # could actually read the needed fields (result != "unknown").
    available_count = sum(
        1 for c in applicable if c["data_available"] and c["result"] != "unknown"
    )
    total = len(applicable)
    if available_count == total:
        return "high"
    if available_count >= total / 2:
        return "medium"
    return "low"


def score_control(
    control: dict, collected: dict, zone: int, timestamp: str
) -> dict:
    """Score a single control against the collected data."""
    control_id: str = control["id"]
    checks_def: list[dict] = control.get("checks", [])
    collection_methods: list[str] = control.get("collection_methods", [])
    zone_thresholds: dict = control.get("zone_thresholds", {})
    automation: str = control.get("automation", "full")

    check_results: list[dict] = [
        evaluate_check(
            chk, collected, zone, collection_methods, timestamp, automation
        )
        for chk in checks_def
    ]

    applicable = [c for c in check_results if c["applicable"]]
    checks_total = len(applicable)
    passed_list = [c for c in applicable if c["passed"] is True]
    failed_list = [c for c in applicable if c["passed"] is False]
    checks_passed = len(passed_list)

    maturity_score, maturity_label, min_required = compute_maturity(
        checks_passed, zone, zone_thresholds
    )
    confidence = compute_confidence(check_results)

    # Roll up evaluator coverage so consumers can distinguish auto from
    # manual-by-design from unimplemented evaluators.
    check_states = [c["evaluator_state"] for c in check_results]
    evaluator_state = rollup_control_evaluator_state(automation, check_states)
    from collections import Counter as _Counter

    state_breakdown = dict(_Counter(check_states))
    for s in EVALUATOR_STATES:
        state_breakdown.setdefault(s, 0)

    # Build evidence dict (keyed by check_id, applicable checks only)
    evidence_dict: dict[str, dict] = {}
    for cr in check_results:
        if cr["applicable"]:
            evidence_dict[cr["check_id"]] = {
                "result": cr["result"],
                "value": cr["value"],
                "source": cr["source"],
                "timestamp": cr["timestamp"],
            }

    needs_manual = (
        automation in ("partial", "manual")
        and control.get("manual_question") is not None
    )

    return {
        # Primary output fields (task spec)
        "control_id": control_id,
        "title": control["title"],
        "pillar": control["pillar"],
        "pillar_name": control["pillar_name"],
        "checks_total": checks_total,
        "checks_passed": checks_passed,
        "checks_failed": [c["check_id"] for c in failed_list],
        "maturity_score": maturity_score,
        "zone_assessed": zone,
        "confidence": confidence,
        "evidence": evidence_dict,
        "needs_manual": needs_manual,
        "manual_question": control.get("manual_question"),
        "evaluator_state": evaluator_state,
        "evaluator_state_breakdown": state_breakdown,
        # Compatibility fields (align with expected_scores fixture)
        "id": control_id,
        "automation": automation,
        "zone": zone,
        "checks": [
            {
                "check_id": cr["check_id"],
                "description": cr["description"],
                "zone_required": cr["zone_required"],
                "applicable": cr["applicable"],
                "passed": cr["passed"],
                "evidence": cr["evidence"],
                "evaluator_state": cr["evaluator_state"],
            }
            for cr in check_results
        ],
        "checks_applicable": checks_total,
        "min_checks_required": min_required,
        "maturity_label": maturity_label,
    }


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def compute_summary(
    scored_controls: list[dict], zone: int, timestamp: str
) -> dict:
    """Compute aggregate summary statistics across all scored controls."""
    total = len(scored_controls)
    auto_scored = sum(1 for c in scored_controls if not c["needs_manual"])
    needs_manual = total - auto_scored

    # Maturity distribution — all controls (including manual/partial) are
    # counted so the distribution sums to total_controls.
    maturity_dist: dict[str, int] = {str(i): 0 for i in range(5)}
    for c in scored_controls:
        key = str(c["maturity_score"])
        maturity_dist[key] = maturity_dist.get(key, 0) + 1

    avg_maturity = (
        round(sum(c["maturity_score"] for c in scored_controls) / total, 1)
        if total
        else 0.0
    )

    # Confidence distribution
    conf_dist: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    for c in scored_controls:
        conf_dist[c["confidence"]] = conf_dist.get(c["confidence"], 0) + 1

    # By pillar
    pillar_agg: dict[str, dict] = {}
    for c in scored_controls:
        p = str(c["pillar"])
        if p not in pillar_agg:
            pillar_agg[p] = {
                "name": c["pillar_name"],
                "pillar_name": c["pillar_name"],
                "total": 0,
                "controls": 0,
                "maturity_sum": 0,
            }
        pillar_agg[p]["total"] += 1
        pillar_agg[p]["controls"] += 1
        pillar_agg[p]["maturity_sum"] += c["maturity_score"]

    by_pillar: dict[str, dict] = {}
    for p in sorted(pillar_agg):
        data = pillar_agg[p]
        avg = (
            round(data["maturity_sum"] / data["controls"], 1)
            if data["controls"]
            else 0.0
        )
        by_pillar[p] = {
            "name": data["name"],
            "pillar_name": data["pillar_name"],
            "total": data["total"],
            "controls": data["controls"],
            "average_maturity": avg,
        }

    return {
        "total_controls": total,
        "auto_scored": auto_scored,
        "needs_manual": needs_manual,
        "maturity_distribution": maturity_dist,
        "by_maturity": maturity_dist,
        "average_maturity": avg_maturity,
        "confidence_distribution": conf_dist,
        "by_pillar": by_pillar,
        "evaluator_coverage": _compute_evaluator_coverage(scored_controls),
        "zone_assessed": zone,
        "assessment_timestamp": timestamp,
    }


def _compute_evaluator_coverage(scored_controls: list[dict]) -> dict:
    """Aggregate evaluator-state coverage across controls and checks.

    Surfaces honest automation coverage so consumers can distinguish
    "manual by design" from "evaluator not yet implemented".
    """
    from collections import Counter as _Counter

    control_states = _Counter(
        c.get("evaluator_state", "manual_only") for c in scored_controls
    )
    check_states: _Counter = _Counter()
    for c in scored_controls:
        for k, v in (c.get("evaluator_state_breakdown") or {}).items():
            check_states[k] += v

    out_controls = {s: control_states.get(s, 0) for s in EVALUATOR_STATES}
    out_checks = {s: check_states.get(s, 0) for s in EVALUATOR_STATES}
    total_controls = sum(out_controls.values())
    total_checks = sum(out_checks.values())
    return {
        "controls": out_controls,
        "checks": out_checks,
        "total_controls": total_controls,
        "total_checks": total_checks,
    }


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FSI-AgentGov Assessment Scoring Engine",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to controls.json manifest",
    )
    parser.add_argument(
        "--collected",
        required=True,
        help="Path to directory containing collected JSON files",
    )
    parser.add_argument(
        "--zone",
        required=True,
        type=int,
        choices=[1, 2, 3],
        help="Governance zone to assess (1, 2, or 3)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write scores.json output",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args(argv)


def run(
    manifest_path: str,
    collected_dir: str,
    zone: int,
    output_path: str,
) -> dict:
    """Execute the scoring engine and return the results dict.

    Can be called programmatically (e.g. from tests) or via the CLI.
    """
    manifest_p = Path(manifest_path)
    collected_p = Path(collected_dir)
    output_p = Path(output_path)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    log.info("Loading manifest from %s", manifest_p)
    manifest = load_json(manifest_p)
    controls: list[dict] = manifest.get("controls", [])

    log.info("Loading collected data from %s", collected_p)
    collected = load_collected_data(collected_p)

    log.info("Scoring %d controls for zone %d", len(controls), zone)
    scored: list[dict] = []
    for control in controls:
        result = score_control(control, collected, zone, timestamp)
        scored.append(result)
        log.debug(
            "  %s — maturity %d (%s), confidence %s",
            result["control_id"],
            result["maturity_score"],
            result["maturity_label"],
            result["confidence"],
        )

    summary = compute_summary(scored, zone, timestamp)

    output = {
        "_metadata": {
            "engine_version": ENGINE_VERSION,
            "timestamp": timestamp,
            "zone": zone,
            "manifest_version": manifest.get("version", "unknown"),
            "total_controls": len(scored),
            "auto_scored": summary["auto_scored"],
            "needs_manual": summary["needs_manual"],
        },
        "controls": scored,
        "summary": summary,
    }

    output_p.parent.mkdir(parents=True, exist_ok=True)
    with open(output_p, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
    log.info("Scores written to %s", output_p)

    return output


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    try:
        result = run(args.manifest, args.collected, args.zone, args.output)
        summary = result["summary"]
        print(f"\nAssessment complete — zone {args.zone}")
        print(f"  Controls scored:  {summary['total_controls']}")
        print(f"  Auto-scored:      {summary['auto_scored']}")
        print(f"  Needs manual:     {summary['needs_manual']}")
        print(f"  Average maturity: {summary['average_maturity']}")
        print(f"  Output: {args.output}")
    except Exception as exc:
        log.error("Scoring failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
