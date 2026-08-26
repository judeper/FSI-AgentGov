"""Zone-based sharing rules and compliance evaluation for ASARD.

This module defines zone-based sharing rules for the Agent Sharing Access
Restriction Detector and provides functions for zone classification, sharing
principal parsing, and compliance evaluation.

Key functions
-------------
- ``classify_environment_zone()`` — Determine governance zone from environment metadata
- ``parse_sharing_principals()`` — Parse BAP API sharing principals JSON
- ``evaluate_zone_compliance()`` — Evaluate sharing against zone rules
- ``check_agent_compliance()`` — End-to-end compliance check for a single agent

Zone rules
----------
- **Zone 1 (Personal Productivity):** Individual user sharing only. No group sharing.
- **Zone 2 (Team Collaboration):** Named security groups permitted. No Everyone or Public.
- **Zone 3 (Enterprise Managed):** Pre-approved security groups from policy table only.
- **Zone 0 (Unclassified):** Safe fallback — named groups permitted, no Everyone/Public.

Example usage (detection script integration)::

    from asard_zone_rules import check_agent_compliance

    result = check_agent_compliance(
        agent_id="abc-123",
        environment_id="env-456",
        environment_name="Production-Finance",
        sharing_principals_json='[{"type":"group","id":"..."}]',
        client=caa_client,
    )
    if not result["compliant"]:
        print(f"Violation: {result['violation_type']} — {result['details']}")
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# =========================================================================
# Zone sharing rules configuration
# =========================================================================

ZONE_SHARING_RULES: Dict[int, Dict[str, Any]] = {
    1: {
        "name": "Personal Productivity",
        "allow_individual_sharing": True,
        "allow_group_sharing": False,
        "allow_everyone": False,
        "allow_public": False,
        "require_approved_groups": False,
        "description": "Individual user sharing only. No group sharing beyond creator.",
    },
    2: {
        "name": "Team Collaboration",
        "allow_individual_sharing": True,
        "allow_group_sharing": True,
        "allow_everyone": False,
        "allow_public": False,
        "require_approved_groups": False,
        "description": "Named security groups permitted. No Everyone or Public sharing.",
    },
    3: {
        "name": "Enterprise Managed",
        "allow_individual_sharing": False,
        "allow_group_sharing": True,
        "allow_everyone": False,
        "allow_public": False,
        "require_approved_groups": True,
        "description": "Pre-approved security groups from policy table only. No individual sharing.",
    },
    0: {
        "name": "Unclassified",
        "allow_individual_sharing": True,
        "allow_group_sharing": True,
        "allow_everyone": False,
        "allow_public": False,
        "require_approved_groups": False,
        "description": "Default fallback. Named groups permitted, no Everyone/Public.",
    },
}

# Zones that carry enforceable remediation rules. Zone 0 (Unclassified) is a
# permissive detection-time fallback only — it must never be used to decide
# whether a remediation succeeded.
ENFORCEABLE_ZONES = (1, 2, 3)

# =========================================================================
# Naming convention patterns for zone classification
# =========================================================================

_ZONE_NAME_PATTERNS: Dict[int, List[str]] = {
    3: ["prod", "production", "enterprise"],
    2: ["test", "qa", "staging", "uat"],
    1: ["dev", "sandbox", "personal"],
}


# =========================================================================
# Zone classification
# =========================================================================


def classify_environment_zone(
    environment_id: str,
    environment_name: str,
    client: Any = None,
    default_zone: int = 0,
) -> int:
    """Determine the governance zone for an environment.

    Classification cascade (first match wins):

    1. **Environment policy lookup:** If ``client`` is provided, query
       ``fsi_EnvironmentPolicy`` table for environment. If a policy
       record exists with a usable ``fsi_zone`` value (1–3), return that
       zone. Zone 0 is unclassified and falls through.
    2. **Naming convention:** Check environment name against known patterns
       (case-insensitive). "prod"/"production"/"enterprise" → Zone 3;
       "test"/"qa"/"staging"/"uat" → Zone 2;
       "dev"/"sandbox"/"personal" → Zone 1.
    3. **Fallback:** Return ``default_zone`` (0 by default).

    Parameters
    ----------
    environment_id : str
        Power Platform environment ID.
    environment_name : str
        Environment display name.
    client : CAAClient | None
        Dataverse client for policy lookups. If *None*, skips Dataverse.
    default_zone : int
        Fallback zone if no classification matches (default: 0).

    Returns
    -------
    int
        Zone number (0–3).
    """
    # 1. Environment policy lookup (if client available)
    if client is not None:
        try:
            records = client.query(
                "fsi_environmentpolicies",
                filter=f"fsi_environmentid eq '{environment_id}'",
                select=["fsi_zone"],
                top=1,
            )
            if records:
                zone_value = records[0].get("fsi_zone")
                if zone_value is not None:
                    zone = int(zone_value)
                    if zone not in (1, 2, 3):
                        logger.warning(
                            "Environment %s policy returned unusable Zone %d — falling back to naming convention",
                            environment_id,
                            zone,
                        )
                    else:
                        logger.info(
                            "Environment %s classified as Zone %d via policy lookup",
                            environment_id,
                            zone,
                        )
                        return zone
        except Exception as exc:
            logger.warning(
                "Policy lookup failed for environment %s: %s — falling back to naming convention",
                environment_id,
                exc,
            )

    # 2. Naming convention (case-insensitive)
    name_lower = (environment_name or "").lower()
    for zone, patterns in _ZONE_NAME_PATTERNS.items():
        for pattern in patterns:
            if re.search(r"\b" + re.escape(pattern) + r"\b", name_lower):
                logger.info(
                    "Environment '%s' classified as Zone %d via naming convention (matched '%s')",
                    environment_name,
                    zone,
                    pattern,
                )
                return zone

    # 3. Fallback
    logger.info(
        "Environment '%s' unclassified — defaulting to Zone %d",
        environment_name,
        default_zone,
    )
    return default_zone


# =========================================================================
# Sharing principal parsing
# =========================================================================


def parse_sharing_principals(principals_json: str) -> Dict[str, Any]:
    """Parse BAP API sharing principals JSON into a structured dictionary.

    Parameters
    ----------
    principals_json : str
        JSON array from BAP Admin API containing sharing principal objects.
        Each object is expected to have at least a ``type`` field and
        optionally ``id`` / ``displayName``.

    Returns
    -------
    dict
        Structured summary::

            {
                "individuals": [],        # user principal names / IDs
                "security_groups": [],    # Microsoft Entra ID group object IDs
                "has_everyone": False,
                "has_public": False,
                "has_organization": False,
            }

    Notes
    -----
    Handles malformed JSON gracefully — returns empty structure and logs a
    warning.  Detection of special principals uses case-insensitive matching
    on ``type`` and ``displayName`` fields.
    """
    empty: Dict[str, Any] = {
        "individuals": [],
        "security_groups": [],
        "has_everyone": False,
        "has_public": False,
        "has_organization": False,
    }

    if not principals_json:
        return empty

    try:
        principals = json.loads(principals_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("Failed to parse sharing principals JSON: %s", exc)
        return empty

    if not isinstance(principals, list):
        logger.warning("Sharing principals is not a list — got %s", type(principals).__name__)
        return empty

    result: Dict[str, Any] = {
        "individuals": [],
        "security_groups": [],
        "has_everyone": False,
        "has_public": False,
        "has_organization": False,
    }

    for principal in principals:
        if not isinstance(principal, dict):
            continue

        p_type = str(principal.get("type", "")).lower()
        p_name = str(principal.get("displayName", "")).lower()
        p_id = str(principal.get("id", ""))

        # Detect special principals
        if p_type == "everyone" or p_name == "everyone":
            result["has_everyone"] = True
        elif p_type == "public" or p_name == "public":
            result["has_public"] = True
        elif p_type in ("organization", "org") or p_name in ("organization", "org", "all users"):
            result["has_organization"] = True
            result["has_everyone"] = True  # Organization-wide = effectively Everyone
        elif p_type in ("group", "securitygroup", "security_group"):
            if p_id:
                result["security_groups"].append(p_id)
        elif p_type in ("user", "individual", ""):
            if p_id:
                result["individuals"].append(p_id)

    return result


# =========================================================================
# Zone compliance evaluation
# =========================================================================


def evaluate_zone_compliance(
    zone: int,
    parsed_principals: Dict[str, Any],
    approved_groups: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Evaluate sharing principals against zone-specific sharing rules.

    Parameters
    ----------
    zone : int
        Governance zone (0–3).
    parsed_principals : dict
        Output from ``parse_sharing_principals()``.
    approved_groups : list[str] | None
        Microsoft Entra ID group IDs approved for this zone (Zone 3 only).
        If *None* for Zone 3, skip approved group check (log warning).

    Returns
    -------
    dict
        Compliance evaluation result::

            {
                "compliant": True/False,
                "violation_type": None | "Everyone" | "Public" | "UnapprovedGroup" | ...,
                "details": "Human-readable explanation",
                "violations": [{"type": str, "details": str}, ...],
            }

        ``violation_type`` and ``details`` reflect the first (highest-severity)
        violation for backward compatibility.  ``violations`` contains all
        detected violations.
    """
    rules = ZONE_SHARING_RULES.get(zone, ZONE_SHARING_RULES[0])
    violations = []

    # Check Everyone
    if parsed_principals.get("has_everyone") and not rules["allow_everyone"]:
        violations.append({
            "type": "Everyone",
            "details": (
                f"Zone {zone} ({rules['name']}) prohibits Everyone sharing. "
                f"Agent is shared with Everyone or all organization users."
            ),
        })

    # Check Public
    if parsed_principals.get("has_public") and not rules["allow_public"]:
        violations.append({
            "type": "Public",
            "details": (
                f"Zone {zone} ({rules['name']}) prohibits Public sharing. "
                f"Agent has a public internet link."
            ),
        })

    groups = parsed_principals.get("security_groups", [])

    # Zone 1: No group sharing allowed
    if not rules["allow_group_sharing"] and groups:
        violations.append({
            "type": "UnapprovedGroup",
            "details": (
                f"Zone {zone} ({rules['name']}) does not allow group sharing. "
                f"Agent is shared with {len(groups)} security group(s)."
            ),
        })

    # Zone 3: Require approved groups
    if rules["require_approved_groups"] and groups:
        if approved_groups is None:
            logger.warning(
                "Zone %d requires approved groups but no approved_groups list provided — "
                "skipping approved group check",
                zone,
            )
        else:
            approved_set = {g.lower() for g in approved_groups}
            unapproved = [g for g in groups if g.lower() not in approved_set]
            if unapproved:
                violations.append({
                    "type": "UnapprovedGroup",
                    "details": (
                        f"Zone {zone} ({rules['name']}) requires pre-approved security groups. "
                        f"{len(unapproved)} unapproved group(s) found: {', '.join(unapproved[:5])}"
                        + (" ..." if len(unapproved) > 5 else "")
                    ),
                })

    # Zone 3: No individual sharing
    individuals = parsed_principals.get("individuals", [])
    if not rules["allow_individual_sharing"] and individuals:
        violations.append({
            "type": "ExcessiveIndividual",
            "details": (
                f"Zone {zone} ({rules['name']}) does not allow individual sharing. "
                f"Agent is shared with {len(individuals)} individual user(s)."
            ),
        })

    if violations:
        return {
            "compliant": False,
            "violation_type": violations[0]["type"],
            "details": violations[0]["details"],
            "violations": violations,
        }

    return {
        "compliant": True,
        "violation_type": None,
        "details": f"Zone {zone} ({rules['name']}): Sharing configuration is compliant.",
        "violations": [],
    }


# =========================================================================
# Approved group lookup
# =========================================================================


def get_approved_groups_for_zone(zone: int, client: Any) -> List[str]:
    """Query approved security groups for a governance zone from Dataverse.

    Reads from the ``fsi_ApprovedSecurityGroupPolicy`` table (created by
    ``create_asard_dataverse_schema.py``).  Filters by zone and active
    status.

    Parameters
    ----------
    zone : int
        Governance zone (1–3).
    client : CAAClient
        Dataverse client for querying.

    Returns
    -------
    list[str]
        Microsoft Entra ID security group object IDs approved for the zone.
        Empty list if no records found or on error.
    """
    try:
        records = client.query(
            "fsi_approvedsecuritygrouppolicies",
            filter=f"fsi_zone eq {zone} and fsi_is_active eq true",
            select=["fsi_group_id"],
        )
        group_ids = [r["fsi_group_id"] for r in records if r.get("fsi_group_id")]
        if not group_ids:
            logger.info("No approved groups found for Zone %d", zone)
        else:
            logger.info("Found %d approved group(s) for Zone %d", len(group_ids), zone)
        return group_ids
    except Exception as exc:
        logger.error("Failed to query approved groups for Zone %d: %s", zone, exc)
        return []


# =========================================================================
# End-to-end compliance check
# =========================================================================


def check_agent_compliance(
    agent_id: str,
    environment_id: str,
    environment_name: str,
    sharing_principals_json: str,
    client: Any = None,
    default_zone: int = 0,
    zone: Optional[int] = None,
) -> Dict[str, Any]:
    """Orchestrate a full compliance check for a single agent.

    Workflow:

    1. Classify environment zone via ``classify_environment_zone()`` (skipped
       when the caller supplies an explicit ``zone``)
    2. Parse sharing principals via ``parse_sharing_principals()``
    3. Get approved groups for zone (Zone 3 only, if client available)
    4. Evaluate compliance via ``evaluate_zone_compliance()``
    5. Return enriched result with zone and agent context

    Parameters
    ----------
    agent_id : str
        Copilot Studio agent ID.
    environment_id : str
        Power Platform environment ID.
    environment_name : str
        Environment display name.
    sharing_principals_json : str
        JSON array of sharing principals from BAP API.
    client : CAAClient | None
        Dataverse client for policy lookups and approved group queries.
    default_zone : int
        Fallback zone if environment cannot be classified (default: 0).
    zone : int | None
        Pre-resolved governance zone. When supplied, classification is skipped
        entirely and compliance is evaluated against this exact zone — used by
        post-remediation validation so it cannot silently re-classify to a more
        permissive zone than the one the remediation applied. Must be one of
        ``ENFORCEABLE_ZONES``; any other value (including 0) fails closed with
        a non-compliant ``Error`` result. When *None* (default), the zone is
        classified as before.

    Returns
    -------
    dict
        Compliance result::

            {
                "agent_id": "...",
                "environment_id": "...",
                "zone": 1,
                "zone_name": "Personal Productivity",
                "compliant": True/False,
                "violation_type": None | "Everyone" | "Public" | ...,
                "details": "...",
            }
    """
    try:
        # 1. Resolve zone — an explicitly supplied zone wins over classification
        if zone is None:
            zone = classify_environment_zone(
                environment_id, environment_name, client=client, default_zone=default_zone
            )
        elif zone not in ENFORCEABLE_ZONES:
            # Fail closed: an explicit but unenforceable zone (notably Zone 0)
            # would otherwise be evaluated against permissive fallback rules.
            logger.error(
                "Compliance check refused for agent %s: caller supplied unenforceable zone %r",
                agent_id,
                zone,
            )
            return {
                "agent_id": agent_id,
                "environment_id": environment_id,
                "zone": zone,
                "zone_name": ZONE_SHARING_RULES.get(zone, ZONE_SHARING_RULES[0])["name"],
                "compliant": False,
                "violation_type": "Error",
                "details": (
                    f"Caller supplied unenforceable zone {zone!r}; compliance can only be "
                    f"evaluated against zones {ENFORCEABLE_ZONES}."
                ),
            }
        zone_name = ZONE_SHARING_RULES.get(zone, ZONE_SHARING_RULES[0])["name"]

        # 2. Parse principals
        parsed = parse_sharing_principals(sharing_principals_json)

        # 3. Get approved groups (Zone 3 only)
        approved_groups: Optional[List[str]] = None
        if zone == 3 and client is not None:
            approved_groups = get_approved_groups_for_zone(zone, client)

        # 4. Evaluate compliance
        result = evaluate_zone_compliance(zone, parsed, approved_groups)

        # 5. Enrich and return
        return {
            "agent_id": agent_id,
            "environment_id": environment_id,
            "zone": zone,
            "zone_name": zone_name,
            "compliant": result["compliant"],
            "violation_type": result["violation_type"],
            "details": result["details"],
        }

    except Exception as exc:
        logger.exception("Compliance check failed for agent %s", agent_id)
        return {
            "agent_id": agent_id,
            "environment_id": environment_id,
            "zone": default_zone,
            "zone_name": ZONE_SHARING_RULES.get(default_zone, ZONE_SHARING_RULES[0])["name"],
            "compliant": False,
            "violation_type": "Error",
            "details": f"Compliance check error: {exc}",
        }
