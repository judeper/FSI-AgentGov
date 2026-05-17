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


def _read_framework_version() -> str:
    """Read FSI-AgentGov framework version from repo-root VERSION file.

    Single source of truth for the framework release the engine was built
    against (e.g., "1.6.2"). Returns "unknown" if VERSION is missing.
    """
    version_file = Path(__file__).resolve().parents[2] / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "unknown"


FRAMEWORK_VERSION = _read_framework_version()


def normalize_manifest_controls(raw: object) -> list[dict]:
    """Return the controls list regardless of manifest top-level shape.

    The on-disk ``assessment/manifest/controls.json`` is a bare JSON list
    of 78 control objects. Earlier engine code assumed a dict-wrapped
    form ``{"controls": [...]}`` and crashed against the real file with
    ``AttributeError: 'list' object has no attribute 'get'``. This helper
    accepts either shape so the engine runs end-to-end against the
    production manifest. Closes F-MANIFEST-FORMAT-MISMATCH-01.
    """
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get("controls", [])
    raise TypeError(
        f"Manifest must be list or dict; got {type(raw).__name__}"
    )


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
    1: "Personal Productivity",
    2: "Team Collaboration",
    3: "Enterprise Managed",
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
    # Use utf-8-sig to defensively tolerate BOM written by Windows PowerShell 5.x
    # collectors. Newer collectors emit BOM-less UTF-8 but legacy installs may
    # still produce BOM-prefixed JSON. F-RUN-ASSESSMENT-ORCH-BOM-01.
    with open(path, "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def load_collected_data(
    collected_dir: Path,
) -> tuple[dict[str, dict | None], dict[str, list[str]]]:
    """Load all collected JSON files into a dict keyed by source name.

    Returns ``(collected, load_warnings)``. ``load_warnings`` maps
    source key -> list of human-readable diagnostic strings produced
    while loading (file missing, parse failure, non-dict root, empty
    payload). The collected mapping always contains every source key
    in :data:`SOURCE_FILENAMES`, with ``None`` for any source that
    could not be loaded as a usable dict.

    Closes part of F-ENGINE-API-FAILURE-MODE-UNTESTED-01: previously
    a non-dict JSON root (e.g., a bare list from PowerShell's
    single-element ``ConvertTo-Json`` footgun) crashed downstream
    evaluators with ``AttributeError: 'list' object has no attribute
    'get'``. Now it is normalized to ``None`` and a load_warning is
    surfaced so the customer sees that the collector emitted an
    unparseable payload shape.
    """
    collected: dict[str, dict | None] = {}
    load_warnings: dict[str, list[str]] = {}
    for key, filename in SOURCE_FILENAMES.items():
        path = collected_dir / filename
        if not path.is_file():
            log.info("Source file not found: %s", path)
            collected[key] = None
            load_warnings.setdefault(key, []).append(
                f"{key} data file not found at {path.name}"
            )
            continue
        try:
            parsed = load_json(path)
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("Failed to load %s: %s", path, exc)
            collected[key] = None
            load_warnings.setdefault(key, []).append(
                f"{key} data file failed to parse: {exc}"
            )
            continue
        if not isinstance(parsed, dict):
            log.warning(
                "Source %s root is %s, expected dict; treating as no data",
                path,
                type(parsed).__name__,
            )
            collected[key] = None
            load_warnings.setdefault(key, []).append(
                f"{key} data file root is {type(parsed).__name__}, "
                f"expected JSON object"
            )
            continue
        # Empty `{}` is valid JSON but means the collector wrote no
        # usable data - synthesize a warning so the customer sees
        # that the collector returned an empty payload (per S-3 in
        # AS15c rubber-duck: "the strongest possible partial-data
        # signal").
        if not parsed:
            log.warning("Source %s is empty {}; no data to evaluate", path)
            collected[key] = None
            load_warnings.setdefault(key, []).append(
                f"{key} data file is empty - collector produced no data"
            )
            continue
        collected[key] = parsed
        log.info("Loaded %s from %s", key, path)
    return collected, load_warnings


def _first_present(mapping: dict, *keys: str) -> object:
    """Return the first present non-None value from *mapping* for *keys*."""
    for key in keys:
        if key in mapping and mapping.get(key) is not None:
            return mapping.get(key)
    return None


def _normalize_ppac_data(ppac: dict) -> dict:
    """Backfill legacy evaluator keys from collector-real PPAC payloads."""
    normalized = dict(ppac)

    if normalized.get("role_assignments") is None:
        role_assignments = _first_present(ppac, "roleAssignments")
        if isinstance(role_assignments, list):
            assignment_map: dict[str, list[dict]] = {}
            for entry in role_assignments:
                if not isinstance(entry, dict):
                    continue
                env_name = _first_present(
                    entry,
                    "EnvironmentName",
                    "environmentName",
                    "DisplayName",
                    "displayName",
                )
                if not env_name:
                    continue
                assignments = _first_present(entry, "Assignments", "assignments")
                normalized_roles: list[dict] = []
                if isinstance(assignments, list):
                    for role in assignments:
                        if not isinstance(role, dict):
                            continue
                        normalized_roles.append(
                            {
                                "PrincipalType": _first_present(
                                    role, "PrincipalType", "principalType"
                                ),
                                "PrincipalObjectId": _first_present(
                                    role, "PrincipalObjectId", "principalObjectId"
                                ),
                                "PrincipalDisplayName": _first_present(
                                    role,
                                    "PrincipalDisplayName",
                                    "principalDisplayName",
                                ),
                                "RoleDefinition": _first_present(
                                    role, "RoleDefinition", "roleDefinition"
                                ),
                            }
                        )
                assignment_map[str(env_name)] = normalized_roles
            normalized["role_assignments"] = assignment_map

    return normalized


def _normalize_graph_policy(policy: dict) -> dict:
    """Normalize current Graph collector policy fields to evaluator shape."""
    conditions = policy.get("conditions") or {}
    applications = conditions.get("applications") or {}
    users = conditions.get("users") or {}
    grant_controls = policy.get("grantControls") or {}
    session_controls = policy.get("sessionControls") or {}

    state = _first_present(policy, "state", "State")
    if isinstance(state, str):
        state = state.lower()

    include_applications = _first_present(policy, "IncludeApplications")
    if include_applications is None:
        include_applications = applications.get("includeApplications", [])
    exclude_applications = _first_present(policy, "ExcludeApplications")
    if exclude_applications is None:
        exclude_applications = applications.get("excludeApplications", [])
    include_users = _first_present(policy, "IncludeUsers")
    if include_users is None:
        include_users = users.get("includeUsers", [])
    exclude_users = _first_present(policy, "ExcludeUsers")
    if exclude_users is None:
        exclude_users = users.get("excludeUsers", [])
    include_groups = _first_present(policy, "IncludeGroups")
    if include_groups is None:
        include_groups = users.get("includeGroups", [])
    exclude_groups = _first_present(policy, "ExcludeGroups")
    if exclude_groups is None:
        exclude_groups = users.get("excludeGroups", [])
    built_in_controls = _first_present(policy, "BuiltInControls")
    if built_in_controls is None:
        built_in_controls = grant_controls.get("builtInControls", [])
    operator = _first_present(policy, "Operator")
    if operator is None:
        operator = grant_controls.get("operator")
    sign_in_frequency = _first_present(policy, "SignInFrequency")
    if sign_in_frequency is None:
        sign_in_frequency = session_controls.get("signInFrequency")
    persistent_browser = _first_present(policy, "PersistentBrowser")
    if persistent_browser is None:
        persistent_browser = session_controls.get("persistentBrowser")

    return {
        "id": _first_present(policy, "id", "Id"),
        "displayName": _first_present(policy, "displayName", "DisplayName"),
        "state": state,
        "conditions": {
            "applications": {
                "includeApplications": include_applications or [],
                "excludeApplications": exclude_applications or [],
            },
            "users": {
                "includeUsers": include_users or [],
                "excludeUsers": exclude_users or [],
                "includeGroups": include_groups or [],
                "excludeGroups": exclude_groups or [],
            },
        },
        "grantControls": {
            "builtInControls": built_in_controls or [],
            "operator": operator,
        },
        "sessionControls": {
            "signInFrequency": sign_in_frequency,
            "persistentBrowser": persistent_browser,
        },
    }


def _normalize_graph_data(graph: dict) -> dict:
    """Backfill legacy evaluator keys from collector-real Graph payloads."""
    normalized = dict(graph)

    if normalized.get("conditional_access_policies") is None:
        policies = _first_present(graph, "conditionalAccessPolicies")
        if isinstance(policies, list):
            normalized["conditional_access_policies"] = [
                _normalize_graph_policy(policy)
                for policy in policies
                if isinstance(policy, dict)
            ]

    if normalized.get("fsi_security_groups") is None:
        groups = _first_present(graph, "fsiSecurityGroups")
        if isinstance(groups, list):
            normalized["fsi_security_groups"] = [
                {
                    "id": _first_present(group, "id", "Id"),
                    "displayName": _first_present(
                        group, "displayName", "DisplayName"
                    ),
                    "securityEnabled": _first_present(
                        group, "securityEnabled", "SecurityEnabled"
                    ),
                    "groupTypes": _first_present(group, "groupTypes", "GroupTypes"),
                    "membershipRule": _first_present(
                        group, "membershipRule", "MembershipRule"
                    ),
                    "memberCount": _first_present(group, "memberCount", "MemberCount"),
                }
                for group in groups
                if isinstance(group, dict)
            ]

    return normalized


def _normalize_purview_data(purview: dict) -> dict:
    """Backfill legacy evaluator keys from collector-real Purview payloads."""
    normalized = dict(purview)

    if normalized.get("audit_config") is None:
        audit_config = _first_present(purview, "auditConfig")
        if isinstance(audit_config, dict):
            normalized["audit_config"] = audit_config

    if normalized.get("retention_policies") is None:
        retention_policies = _first_present(purview, "retentionPolicies")
        if isinstance(retention_policies, list):
            normalized["retention_policies"] = retention_policies

    return normalized


def _normalize_sharepoint_data(sharepoint: dict) -> dict:
    """Backfill legacy evaluator keys from collector-real SharePoint payloads."""
    normalized = dict(sharepoint)

    if normalized.get("external_sharing") is None:
        external_sharing = _first_present(sharepoint, "externalSharing")
        if isinstance(external_sharing, list):
            normalized["external_sharing"] = {
                str(site_id): capability
                for site_id, capability in (
                    (
                        _first_present(record, "SiteId", "siteId"),
                        _first_present(
                            record, "SharingCapability", "sharingCapability"
                        ),
                    )
                    for record in external_sharing
                    if isinstance(record, dict)
                )
                if site_id is not None
            }

    if normalized.get("sites") is None:
        site_inventory = _first_present(sharepoint, "siteInventory")
        sharing_lookup = normalized.get("external_sharing") or {}
        if isinstance(site_inventory, list):
            normalized["sites"] = [
                {
                    "id": _first_present(site, "id", "Id"),
                    "displayName": _first_present(
                        site, "displayName", "DisplayName"
                    ),
                    "webUrl": _first_present(site, "webUrl", "WebUrl"),
                    "sharingCapability": (
                        sharing_lookup.get(str(site_id))
                        if site_id is not None and isinstance(sharing_lookup, dict)
                        else _first_present(
                            site, "sharingCapability", "SharingCapability"
                        )
                    ),
                }
                for site in site_inventory
                if isinstance(site, dict)
                for site_id in [_first_present(site, "id", "Id")]
            ]

    if normalized.get("grounding_scope") is None:
        grounding_cross_ref = _first_present(sharepoint, "groundingCrossRef")
        if isinstance(grounding_cross_ref, dict):
            approved = _first_present(
                grounding_cross_ref,
                "ApprovedSites",
                "approved",
            )
            unapproved = _first_present(
                grounding_cross_ref,
                "UnapprovedSites",
                "unapproved",
            )
            normalized["grounding_scope"] = {
                "approved": approved if isinstance(approved, list) else [],
                "unapproved": unapproved if isinstance(unapproved, list) else [],
            }

    return normalized


def normalize_collected_data(
    collected: dict[str, dict | None],
) -> dict[str, dict | None]:
    """Normalize live collector payloads to evaluator-expected compatibility keys."""
    normalized: dict[str, dict | None] = {}
    for source_key, payload in collected.items():
        if payload is None:
            normalized[source_key] = None
        elif source_key == "ppac":
            normalized[source_key] = _normalize_ppac_data(payload)
        elif source_key == "graph":
            normalized[source_key] = _normalize_graph_data(payload)
        elif source_key == "purview":
            normalized[source_key] = _normalize_purview_data(payload)
        elif source_key == "sharepoint":
            normalized[source_key] = _normalize_sharepoint_data(payload)
        else:
            normalized[source_key] = payload
    return normalized


def _coerce_diagnostic_list(raw: object) -> list[str]:
    """Coerce a ``_metadata.warnings`` / ``_metadata.errors`` field to
    a clean list of strings.

    PowerShell's ``ConvertTo-Json`` collapses single-element arrays to
    bare scalars - so a collector that recorded one warning may write
    ``"warnings": "Section 7 failed"`` instead of
    ``"warnings": ["Section 7 failed"]``. Normalize both shapes.
    Non-string entries are coerced via ``str()`` to keep the engine
    crash-resistant; falsy entries are dropped.
    """
    if isinstance(raw, str):
        items = [raw]
    elif isinstance(raw, list):
        items = raw
    else:
        return []
    return [str(item) for item in items if item]


def extract_collector_warnings(
    collected: dict[str, dict | None],
    load_warnings: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Build the customer-facing collector_warnings rollup.

    For each source key, merges (a) load-time diagnostics emitted by
    :func:`load_collected_data` (file missing / malformed / non-dict /
    empty) with (b) the collector-recorded ``_metadata.warnings`` and
    ``_metadata.errors`` lists from the loaded payload. Errors are
    prefixed with ``"[error] "`` so the customer sees their higher
    severity in the same flat list (per AS15c rubber-duck N-2).

    Insertion order is preserved within each source (load-warnings
    first, then collector warnings, then collector errors) for
    deterministic snapshot diffs.

    Returns a dict of source-key -> list-of-strings. Sources with no
    diagnostics at all are omitted entirely so a clean assessment
    produces ``collector_warnings = {}``.
    """
    rollup: dict[str, list[str]] = {}
    for key in SOURCE_FILENAMES:
        items: list[str] = []
        items.extend(load_warnings.get(key, []))
        payload = collected.get(key)
        if isinstance(payload, dict):
            metadata = payload.get("_metadata")
            if isinstance(metadata, dict):
                items.extend(_coerce_diagnostic_list(metadata.get("warnings")))
                items.extend(
                    f"[error] {e}"
                    for e in _coerce_diagnostic_list(metadata.get("errors"))
                )
        if items:
            rollup[key] = items
    return rollup


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
                ptype = (role.get("PrincipalType") or "").lower()
                if principal in ("everyone", "all users") or ptype == "tenant":
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
    controls: list[dict] = normalize_manifest_controls(manifest)
    manifest_version = (
        manifest.get("version", "unknown")
        if isinstance(manifest, dict)
        else "unknown"
    )

    log.info("Loading collected data from %s", collected_p)
    collected, load_warnings = load_collected_data(collected_p)
    collected = normalize_collected_data(collected)
    collector_warnings = extract_collector_warnings(collected, load_warnings)

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
            "framework_version": FRAMEWORK_VERSION,
            "timestamp": timestamp,
            "zone": zone,
            "manifest_version": manifest_version,
            "total_controls": len(scored),
            "auto_scored": summary["auto_scored"],
            "needs_manual": summary["needs_manual"],
            "collector_warnings": collector_warnings,
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
        print(f"\nAssessment complete - zone {args.zone}")
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
