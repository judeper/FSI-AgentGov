"""Agent Sharing Remediation Script — WhatIf Mode, Zone-Specific Enforcement.

This script remediates non-compliant Copilot Studio agent sharing by applying
zone-appropriate permissions. Supports WhatIf simulation mode, multiple input
sources (Dataverse, CSV, single agent), and post-remediation validation.

Zone remediation patterns
-------------------------
- **Zone 1 (Personal Productivity):** Remove ALL group sharing, preserve individual users
- **Zone 2 (Team Collaboration):** Remove Everyone/Public/organization, preserve named groups
- **Zone 3 (Enterprise Managed):** Replace ALL with pre-approved security groups from policy table

Key features
------------
- WhatIf mode: Simulate changes without applying (--whatif)
- Post-remediation validation: Re-scan agent after PATCH, retry up to 3 times
- Dataverse integration: Update compliance records with remediation_date and compliance_status
- Flexible input: Dataverse query (default), CSV file (--from-csv), or single agent (--agent-id)

Environment variables
---------------------
BAP_TENANT_ID        Entra ID tenant GUID
BAP_CLIENT_ID        App registration client ID (Power Platform Admin API)
BAP_CLIENT_SECRET    App registration client secret
DATAVERSE_ORG_URL    Dataverse organization URL (e.g., https://contoso.crm.dynamics.com)

Example usage
-------------
::

    # WhatIf mode (simulation only, no changes applied)
    python remediate_agent_sharing.py --whatif --from-dataverse --verbose

    # Single-agent remediation
    python remediate_agent_sharing.py --agent-id "abc-123" --environment-id "env-456"

    # Remediate all non-compliant agents from Dataverse
    python remediate_agent_sharing.py --from-dataverse

    # Remediate from CSV file (detection script output)
    python remediate_agent_sharing.py --from-csv violations.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from asard_zone_rules import (
    check_agent_compliance,
    classify_environment_zone,
    get_approved_groups_for_zone,
    parse_sharing_principals,
)
from bap_admin_client import BAPAdminClient
from caa_client import CAAClient
from dateutil import parser as dateparser

# =========================================================================
# Module constants
# =========================================================================

DEFAULT_BATCH_SIZE = 10
MAX_VALIDATION_RETRIES = 3
VALIDATION_DELAYS = [2, 5, 10]  # seconds between validation attempts

logger = logging.getLogger(__name__)


# =========================================================================
# Helper functions
# =========================================================================


def build_permission_object(
    group_id: str, group_name: str, role_name: str = "CanView"
) -> Dict[str, Any]:
    """Build a BAP API permission object for a security group.

    Parameters
    ----------
    group_id : str
        Microsoft Entra ID group GUID.
    group_name : str
        Display name for the group.
    role_name : str, optional
        Permission role (default: "CanView").

    Returns
    -------
    dict
        Permission object with structure::

            {
                "properties": {
                    "roleName": "CanView",
                    "principal": {
                        "id": "group-guid",
                        "type": "Group",
                        "displayName": "Finance Team"
                    }
                }
            }
    """
    return {
        "properties": {
            "roleName": role_name,
            "principal": {
                "id": group_id,
                "type": "Group",
                "displayName": group_name,
            },
        }
    }


def get_group_name_from_policy(
    group_id: str, dataverse_client: CAAClient
) -> Optional[str]:
    """Query Dataverse policy table for group display name.

    Parameters
    ----------
    group_id : str
        Microsoft Entra ID group GUID.
    dataverse_client : CAAClient
        Dataverse client instance.

    Returns
    -------
    str or None
        Group display name from ``fsi_group_name`` field, or None if not found.
    """
    try:
        # Query the approved security group policies table
        query = (
            f"fsi_approvedsecuritygrouppolicies"
            f"?$filter=fsi_group_id eq '{group_id}'"
            f"&$select=fsi_group_name"
        )
        result = dataverse_client.execute_query(query)
        
        if result and "value" in result and len(result["value"]) > 0:
            return result["value"][0].get("fsi_group_name")
        
        return None
        
    except Exception as exc:
        logger.warning(
            "Failed to query group name for %s from policy table: %s", group_id, exc
        )
        return None


def get_zone_remediation_principals(
    zone: int,
    current_principals: List[Dict[str, Any]],
    approved_groups: List[str],
    dataverse_client: CAAClient,
) -> List[Dict[str, Any]]:
    """Build remediation principals list based on zone rules.

    Parameters
    ----------
    zone : int
        Environment zone (1, 2, or 3).
    current_principals : list[dict]
        Current agent sharing principals (parsed from BAP API).
    approved_groups : list[str]
        Approved group IDs from policy table (Zone 3 only).
    dataverse_client : CAAClient
        Dataverse client for group name lookup.

    Returns
    -------
    list[dict]
        List of permission objects for BAP API PATCH body.

    Notes
    -----
    - **Zone 1:** Remove all groups, preserve individual users
    - **Zone 2:** Remove Everyone/Public/organization, preserve named groups + users
    - **Zone 3:** Replace ALL with approved groups from policy table
    """
    remediation_principals = []

    if zone == 1:
        # Zone 1: Remove ALL group sharing, preserve individual users
        for principal in current_principals:
            if principal.get("type", "").lower() == "user":
                # Build permission object for user
                remediation_principals.append(
                    {
                        "properties": {
                            "roleName": "CanView",
                            "principal": {
                                "id": principal.get("id"),
                                "type": "User",
                                "displayName": principal.get("displayName", ""),
                            },
                        }
                    }
                )
        
        if len(remediation_principals) == 0:
            logger.warning(
                "Zone 1 remediation will remove ALL principals (potential access lockout)"
            )

    elif zone == 2:
        # Zone 2: Remove Everyone/Public/organization, preserve named groups + users
        for principal in current_principals:
            principal_type = principal.get("type", "").lower()
            principal_id = principal.get("id", "").lower()
            display_name = principal.get("displayName", "").lower()
            
            # Skip Everyone, Public, organization-wide principals
            # Use exact matching to avoid removing legitimate groups
            # whose names contain these words (e.g., "Republic Team")
            _system_names = {"everyone", "everyone except external users",
                             "public", "all users", "all"}
            if (
                display_name in _system_names
                or principal_id in ["everyone", "public", "all"]
                or principal_type in ["organization", "tenant"]
            ):
                logger.debug(
                    "Zone 2: Removing Everyone/Public principal: %s", display_name
                )
                continue
            
            # Preserve named groups and individual users
            if principal_type in ["user", "group"]:
                remediation_principals.append(
                    {
                        "properties": {
                            "roleName": "CanView",
                            "principal": {
                                "id": principal.get("id"),
                                "type": principal_type.capitalize(),
                                "displayName": principal.get("displayName", ""),
                            },
                        }
                    }
                )

    elif zone == 3:
        # Zone 3: Replace ALL with approved groups from policy table
        if len(approved_groups) == 0:
            logger.error(
                "Zone 3 remediation requires approved groups, but none found in policy table"
            )
            raise ValueError("Zone 3 has no approved groups (would remove all access)")
        
        for group_id in approved_groups:
            # Get group display name from policy table
            group_name = get_group_name_from_policy(group_id, dataverse_client)
            if not group_name:
                group_name = group_id  # Fallback to group ID if name not found
            
            remediation_principals.append(build_permission_object(group_id, group_name))

    else:
        # Zone 0 or unknown: Treat as Zone 2 (safe fallback)
        logger.warning(
            "Unknown zone %d, applying Zone 2 remediation (safe fallback)", zone
        )
        return get_zone_remediation_principals(
            2, current_principals, approved_groups, dataverse_client
        )

    return remediation_principals


def validate_remediation(
    agent_id: str,
    environment_id: str,
    environment_name: str,
    bap_client: BAPAdminClient,
    dataverse_client: CAAClient,
    max_retries: int = MAX_VALIDATION_RETRIES,
) -> Dict[str, Any]:
    """Validate that remediation succeeded by re-scanning agent permissions.

    Parameters
    ----------
    agent_id : str
        Agent GUID.
    environment_id : str
        Environment GUID.
    environment_name : str
        Environment display name.
    bap_client : BAPAdminClient
        BAP Admin API client.
    dataverse_client : CAAClient
        Dataverse client.
    max_retries : int, optional
        Maximum validation attempts (default: 3).

    Returns
    -------
    dict
        Validation result with structure::

            {
                "validated": bool,
                "compliant": bool,
                "attempts": int,
                "error": str or None
            }

    Notes
    -----
    Retries with delays [2, 5, 10] seconds to handle BAP API eventual consistency.
    """
    for attempt in range(max_retries):
        delay = VALIDATION_DELAYS[attempt] if attempt < len(VALIDATION_DELAYS) else 10
        
        logger.debug(
            "Validation attempt %d/%d for agent %s (delay: %ds)",
            attempt + 1,
            max_retries,
            agent_id,
            delay,
        )
        
        time.sleep(delay)
        
        try:
            # Re-fetch agent permissions from BAP API
            current_permissions = bap_client.get_agent_permissions(
                environment_id, agent_id
            )
            
            if not current_permissions:
                logger.warning(
                    "Validation attempt %d: No permissions returned for agent %s",
                    attempt + 1,
                    agent_id,
                )
                continue
            
            # Serialize for compliance check
            permissions_json = json.dumps(current_permissions)
            
            # Re-evaluate compliance
            compliance_result = check_agent_compliance(
                agent_id=agent_id,
                environment_id=environment_id,
                environment_name=environment_name,
                sharing_principals_json=permissions_json,
                client=dataverse_client,
            )
            
            if compliance_result["compliant"]:
                logger.info(
                    "Validation succeeded for agent %s after %d attempt(s)",
                    agent_id,
                    attempt + 1,
                )
                return {
                    "validated": True,
                    "compliant": True,
                    "attempts": attempt + 1,
                    "error": None,
                }
            else:
                logger.warning(
                    "Validation attempt %d: Agent %s still non-compliant — %s",
                    attempt + 1,
                    agent_id,
                    compliance_result.get("violation_type", "Unknown"),
                )
                
                # If last retry, return failure
                if attempt >= max_retries - 1:
                    return {
                        "validated": True,
                        "compliant": False,
                        "attempts": attempt + 1,
                        "error": compliance_result.get("details", "Unknown validation error"),
                    }
        
        except Exception as exc:
            logger.error(
                "Validation attempt %d failed with exception: %s", attempt + 1, exc
            )
            
            # If last retry, return error
            if attempt >= max_retries - 1:
                return {
                    "validated": False,
                    "compliant": False,
                    "attempts": attempt + 1,
                    "error": str(exc),
                }
    
    # Should not reach here, but return failure if loop completes
    return {
        "validated": False,
        "compliant": False,
        "attempts": max_retries,
        "error": "Max retries exhausted",
    }


def update_compliance_record(
    agent_id: str,
    environment_id: str,
    status: int,
    remediation_date: str,
    dataverse_client: CAAClient,
    error_details: Optional[str] = None,
) -> bool:
    """Update Dataverse compliance record after remediation.

    Parameters
    ----------
    agent_id : str
        Agent GUID.
    environment_id : str
        Environment GUID.
    status : int
        Compliance status option set value (0=Compliant, 3=Error).
    remediation_date : str
        ISO 8601 datetime string (e.g., "2026-02-13T18:00:00Z").
    dataverse_client : CAAClient
        Dataverse client.
    error_details : str, optional
        Validation error details (for status=3).

    Returns
    -------
    bool
        True if upsert succeeded, False if error occurred.

    Notes
    -----
    Upserts to ``fsi_agentsharingcompliances`` table by alternate key
    (fsi_agent_id, fsi_environment_id).
    """
    try:
        payload = {
            "fsi_agent_id": agent_id,
            "fsi_environment_id": environment_id,
            "fsi_compliance_status": status,
            "fsi_remediation_date": remediation_date,
        }
        
        if error_details:
            payload["fsi_validation_error"] = error_details[:4000]  # Max length 4000
        
        # Upsert by alternate key
        entity_set = "fsi_agentsharingcompliances"
        alternate_key = f"fsi_agent_id='{agent_id}',fsi_environment_id='{environment_id}'"
        
        dataverse_client.upsert_record(
            entity_set=entity_set,
            alternate_key=alternate_key,
            data=payload,
        )
        
        logger.info(
            "Updated compliance record for agent %s: status=%d, remediation_date=%s",
            agent_id,
            status,
            remediation_date,
        )
        return True
        
    except Exception as exc:
        logger.error(
            "Failed to update compliance record for agent %s: %s", agent_id, exc
        )
        return False


def print_agent_summary(
    agent_data: Dict[str, Any],
    current_principals: List[Dict[str, Any]],
    proposed_principals: List[Dict[str, Any]],
    whatif: bool = False,
) -> None:
    """Print agent remediation summary to console.

    Parameters
    ----------
    agent_data : dict
        Agent metadata (name, environment, zone).
    current_principals : list[dict]
        Current sharing principals.
    proposed_principals : list[dict]
        Proposed remediation principals.
    whatif : bool, optional
        WhatIf mode flag (default: False).
    """
    print("\n" + "=" * 80)
    print(f"Agent: {agent_data.get('agent_name', 'Unknown')}")
    print(f"Environment: {agent_data.get('environment_name', 'Unknown')}")
    print(f"Zone: {agent_data.get('zone', 'Unknown')}")
    print("-" * 80)
    print(f"Current sharing: {len(current_principals)} principal(s)")
    for principal in current_principals:
        print(f"  - {principal.get('displayName', 'Unknown')} ({principal.get('type', 'Unknown')})")
    print("-" * 80)
    print(f"Proposed sharing: {len(proposed_principals)} principal(s)")
    for principal in proposed_principals:
        principal_data = principal.get("properties", {}).get("principal", {})
        print(f"  + {principal_data.get('displayName', 'Unknown')} ({principal_data.get('type', 'Unknown')})")
    print("-" * 80)
    
    if whatif:
        print("[WHATIF] No changes applied (simulation mode)")
    else:
        print("[ACTION] Changes will be applied")
    
    print("=" * 80 + "\n")


def remediate_agent(
    agent_data: Dict[str, Any],
    bap_client: BAPAdminClient,
    dataverse_client: CAAClient,
    args: argparse.Namespace,
) -> Dict[str, Any]:
    """Remediate a single agent's sharing violations.

    Parameters
    ----------
    agent_data : dict
        Agent metadata with keys: agent_id, agent_name, environment_id,
        environment_name, zone, sharing_principals_json.
    bap_client : BAPAdminClient
        BAP Admin API client.
    dataverse_client : CAAClient
        Dataverse client.
    args : argparse.Namespace
        CLI arguments (whatif, verbose, etc.).

    Returns
    -------
    dict
        Remediation result with structure::

            {
                "success": bool,
                "whatif": bool,
                "error": str or None
            }
    """
    agent_id = agent_data["agent_id"]
    agent_name = agent_data.get("agent_name", "Unknown")
    environment_id = agent_data["environment_id"]
    environment_name = agent_data.get("environment_name", "Unknown")
    
    logger.info(
        "Remediating agent %s (%s) in environment %s",
        agent_name,
        agent_id,
        environment_name,
    )
    
    # Phase 4: Check for active exception before remediation
    try:
        alternate_key = f"fsi_agent_id='{agent_id}',fsi_environment_id='{environment_id}'"
        url = f"{dataverse_client.api_url}/fsi_agentsharingcompliances({alternate_key})"
        headers = dataverse_client._get_headers()
        response = dataverse_client._session.get(url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            compliance_record = response.json()
            compliance_status = compliance_record.get("fsi_compliance_status")
            expires_at_str = compliance_record.get("fsi_exception_expires_at")
            
            if compliance_status == 2 and expires_at_str:
                # Parse expiration date
                expires_at = dateparser.parse(expires_at_str)
                now = datetime.now(timezone.utc)
                
                if expires_at >= now:
                    # Active exception exists — skip remediation
                    expires_formatted = expires_at.strftime("%Y-%m-%d")
                    message = f"Agent {agent_name} has active exception (expires {expires_formatted}) — skipping remediation"
                    logger.info(message)
                    print(f"  [SKIP] {message}")
                    return {"success": True, "whatif": False, "error": None, "skipped": True, "skip_reason": "active_exception"}
    except Exception as exc:
        # If exception check fails, log warning and proceed with remediation
        logger.warning("Exception check failed for %s: %s — proceeding with remediation", agent_name, exc)
    
    try:
        # Classify zone (or use override)
        if args.zone_override:
            zone = args.zone_override
            logger.debug("Using zone override: %d", zone)
        else:
            zone = classify_environment_zone(
                environment_name=environment_name,
                environment_metadata={"displayName": environment_name},
            )
        
        agent_data["zone"] = zone
        
        # Parse current sharing principals
        sharing_principals_json = agent_data.get("sharing_principals_json", "[]")
        parsed = parse_sharing_principals(sharing_principals_json)
        current_principals = parsed.get("principals", [])
        
        logger.debug(
            "Agent %s has %d current principal(s) in Zone %d",
            agent_id,
            len(current_principals),
            zone,
        )
        
        # Get approved groups for Zone 3
        approved_groups = []
        if zone == 3:
            approved_groups = get_approved_groups_for_zone(zone, dataverse_client)
            logger.debug(
                "Zone 3: Retrieved %d approved group(s) from policy table",
                len(approved_groups),
            )
        
        # Build remediation principals based on zone
        proposed_principals = get_zone_remediation_principals(
            zone=zone,
            current_principals=current_principals,
            approved_groups=approved_groups,
            dataverse_client=dataverse_client,
        )
        
        logger.debug(
            "Proposed remediation: %d principal(s) for agent %s",
            len(proposed_principals),
            agent_id,
        )
        
        # Print summary (verbose mode or WhatIf)
        if args.verbose or args.whatif:
            print_agent_summary(
                agent_data, current_principals, proposed_principals, args.whatif
            )
        
        # WhatIf mode: Log proposed changes without applying
        if args.whatif:
            patch_body = {"put": proposed_principals}
            logger.info(
                "[WHATIF] Would replace %d principal(s) with %d approved principal(s) for agent %s",
                len(current_principals),
                len(proposed_principals),
                agent_id,
            )
            logger.info(
                "[WHATIF] Proposed PATCH body:\n%s", json.dumps(patch_body, indent=2)
            )
            return {"success": True, "whatif": True, "error": None}
        
        # Apply remediation via PATCH
        logger.warning(
            "Applying remediation to agent %s: %d → %d principal(s)",
            agent_id,
            len(current_principals),
            len(proposed_principals),
        )
        
        patch_success = bap_client.modify_agent_permissions(
            environment_id=environment_id,
            agent_id=agent_id,
            principals=proposed_principals,
        )
        
        if not patch_success:
            logger.error("Failed to apply remediation to agent %s", agent_id)
            return {"success": False, "whatif": False, "error": "PATCH failed"}
        
        # Post-remediation validation
        logger.info("Validating remediation for agent %s", agent_id)
        validation_result = validate_remediation(
            agent_id=agent_id,
            environment_id=environment_id,
            environment_name=environment_name,
            bap_client=bap_client,
            dataverse_client=dataverse_client,
        )
        
        # Update Dataverse compliance record
        remediation_date = datetime.now(timezone.utc).isoformat()
        
        if validation_result["compliant"]:
            # Success: Mark as Compliant (status=0)
            update_compliance_record(
                agent_id=agent_id,
                environment_id=environment_id,
                status=0,  # Compliant
                remediation_date=remediation_date,
                dataverse_client=dataverse_client,
            )
            logger.info(
                "Remediation validated successfully for agent %s after %d attempt(s)",
                agent_id,
                validation_result["attempts"],
            )
            return {"success": True, "whatif": False, "error": None}
        else:
            # Validation failed: Mark as Error (status=3)
            error_details = validation_result.get("error", "Unknown validation error")
            update_compliance_record(
                agent_id=agent_id,
                environment_id=environment_id,
                status=3,  # Error
                remediation_date=remediation_date,
                dataverse_client=dataverse_client,
                error_details=error_details,
            )
            logger.error(
                "Remediation validation failed for agent %s: %s", agent_id, error_details
            )
            return {"success": False, "whatif": False, "error": error_details}
    
    except Exception as exc:
        logger.error("Exception remediating agent %s: %s", agent_id, exc, exc_info=True)
        return {"success": False, "whatif": False, "error": str(exc)}


def load_agents_from_dataverse(
    dataverse_client: CAAClient, args: argparse.Namespace
) -> List[Dict[str, Any]]:
    """Load non-compliant agents from Dataverse.

    Parameters
    ----------
    dataverse_client : CAAClient
        Dataverse client.
    args : argparse.Namespace
        CLI arguments.

    Returns
    -------
    list[dict]
        List of agent data dictionaries.
    """
    logger.info("Loading non-compliant agents from Dataverse")
    
    try:
        # Query for compliance_status=1 (NonCompliant) within last 24 hours
        query = (
            "fsi_agentsharingcompliances"
            "?$filter=fsi_compliance_status eq 1"
            "&$select=fsi_agent_id,fsi_agent_name,fsi_environment_id,fsi_environment_name,"
            "fsi_sharing_principals_json,fsi_last_checked"
        )
        
        result = dataverse_client.execute_query(query)
        
        if not result or "value" not in result:
            logger.warning("No results from Dataverse query")
            return []
        
        agents = []
        for record in result["value"]:
            agents.append(
                {
                    "agent_id": record.get("fsi_agent_id"),
                    "agent_name": record.get("fsi_agent_name"),
                    "environment_id": record.get("fsi_environment_id"),
                    "environment_name": record.get("fsi_environment_name"),
                    "sharing_principals_json": record.get("fsi_sharing_principals_json"),
                }
            )
        
        logger.info("Loaded %d non-compliant agent(s) from Dataverse", len(agents))
        return agents
        
    except Exception as exc:
        logger.error("Failed to load agents from Dataverse: %s", exc, exc_info=True)
        return []


def load_agents_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load agents from CSV file (detection script output).

    Parameters
    ----------
    csv_path : str
        Path to CSV file.

    Returns
    -------
    list[dict]
        List of agent data dictionaries.
    """
    logger.info("Loading agents from CSV file: %s", csv_path)
    
    agents = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Filter to non-compliant agents only
                if row.get("compliance_status", "").lower() == "noncompliant":
                    agents.append(
                        {
                            "agent_id": row.get("agent_id"),
                            "agent_name": row.get("agent_name"),
                            "environment_id": row.get("environment_id"),
                            "environment_name": row.get("environment_name"),
                            "sharing_principals_json": row.get("sharing_principals_json"),
                        }
                    )
        
        logger.info("Loaded %d non-compliant agent(s) from CSV", len(agents))
        return agents
        
    except Exception as exc:
        logger.error("Failed to load agents from CSV: %s", exc, exc_info=True)
        return []


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Remediate agent sharing violations with zone-specific enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Input mode
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--from-dataverse",
        action="store_true",
        default=True,
        help="Load non-compliant agents from Dataverse (default)",
    )
    input_group.add_argument(
        "--from-csv",
        metavar="PATH",
        help="Load agents from CSV file (detection script output)",
    )
    input_group.add_argument(
        "--agent-id",
        metavar="GUID",
        help="Remediate single agent (requires --environment-id)",
    )
    
    parser.add_argument(
        "--environment-id",
        metavar="GUID",
        help="Environment GUID for single-agent remediation (requires --agent-id)",
    )
    
    # Execution mode
    parser.add_argument(
        "--whatif",
        "--dry-run",
        action="store_true",
        help="Simulate changes without applying (WhatIf mode)",
    )
    parser.add_argument(
        "--zone-override",
        type=int,
        choices=[1, 2, 3],
        help="Force zone classification (testing only)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Process N agents per batch (default: {DEFAULT_BATCH_SIZE})",
    )
    
    # Authentication
    parser.add_argument(
        "--tenant-id",
        help="Entra ID tenant GUID (or BAP_TENANT_ID env var)",
    )
    parser.add_argument(
        "--client-id",
        help="App registration client ID (or BAP_CLIENT_ID env var)",
    )
    parser.add_argument(
        "--client-secret",
        help="App registration client secret (or BAP_CLIENT_SECRET env var)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Use interactive auth (device code flow)",
    )
    
    # Logging
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )
    parser.add_argument(
        "--log-file",
        metavar="PATH",
        help="Write logs to file",
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if args.log_file:
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(args.log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
    else:
        logging.basicConfig(level=log_level, format=log_format)
    
    # Validate CLI arguments
    if args.agent_id and not args.environment_id:
        logger.error("--agent-id requires --environment-id")
        sys.exit(1)
    
    if args.environment_id and not args.agent_id:
        logger.error("--environment-id requires --agent-id")
        sys.exit(1)
    
    # Initialize clients
    logger.info("Initializing BAP Admin and Dataverse clients")
    
    try:
        bap_client = BAPAdminClient(
            tenant_id=args.tenant_id or os.environ.get("BAP_TENANT_ID"),
            client_id=args.client_id or os.environ.get("BAP_CLIENT_ID"),
            client_secret=args.client_secret or os.environ.get("BAP_CLIENT_SECRET"),
            interactive=args.interactive,
        )
        
        dataverse_client = CAAClient(
            environment_url=os.environ.get("DATAVERSE_ORG_URL") or os.environ.get("CAA_ENVIRONMENT_URL"),
            tenant_id=args.tenant_id or os.environ.get("BAP_TENANT_ID"),
            client_id=args.client_id or os.environ.get("BAP_CLIENT_ID"),
            client_secret=args.client_secret or os.environ.get("BAP_CLIENT_SECRET"),
        )
        
        # Test connections
        if not bap_client.test_connection():
            logger.error("BAP Admin API connection test failed")
            sys.exit(1)
        
        logger.info("Client initialization successful")
        
    except Exception as exc:
        logger.error("Failed to initialize clients: %s", exc, exc_info=True)
        sys.exit(1)
    
    # Load agents
    agents = []
    
    if args.agent_id and args.environment_id:
        # Single-agent mode
        logger.info("Single-agent remediation mode")
        
        # Fetch agent permissions from BAP API
        permissions = bap_client.get_agent_permissions(
            args.environment_id, args.agent_id
        )
        
        if not permissions:
            logger.error(
                "Failed to fetch permissions for agent %s in environment %s",
                args.agent_id,
                args.environment_id,
            )
            sys.exit(1)
        
        agents.append(
            {
                "agent_id": args.agent_id,
                "agent_name": args.agent_id,  # Name not available in single-agent mode
                "environment_id": args.environment_id,
                "environment_name": args.environment_id,
                "sharing_principals_json": json.dumps(permissions),
            }
        )
    
    elif args.from_csv:
        # CSV input mode
        agents = load_agents_from_csv(args.from_csv)
    
    else:
        # Dataverse input mode (default)
        agents = load_agents_from_dataverse(dataverse_client, args)
    
    if len(agents) == 0:
        logger.warning("No agents to remediate")
        sys.exit(0)
    
    logger.info("Processing %d agent(s)", len(agents))
    
    # Process agents
    stats = {
        "total": len(agents),
        "succeeded": 0,
        "failed": 0,
        "whatif": 0,
        "skipped": 0,  # Phase 4: Track agents skipped due to active exceptions
    }
    
    for i, agent_data in enumerate(agents, start=1):
        logger.info("Processing agent %d/%d", i, len(agents))
        
        result = remediate_agent(agent_data, bap_client, dataverse_client, args)
        
        if result.get("skipped"):
            stats["skipped"] += 1
        elif result["whatif"]:
            stats["whatif"] += 1
        elif result["success"]:
            stats["succeeded"] += 1
        else:
            stats["failed"] += 1
        
        # Batch pause (rate limit mitigation)
        if i % args.batch_size == 0 and i < len(agents):
            logger.info("Batch pause (processed %d agents)", i)
            time.sleep(2)
    
    # Print summary
    print("\n" + "=" * 80)
    print("REMEDIATION SUMMARY")
    print("=" * 80)
    print(f"Total agents processed: {stats['total']}")
    print(f"  Succeeded: {stats['succeeded']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  WhatIf (simulated): {stats['whatif']}")
    print(f"  Skipped (active exceptions): {stats['skipped']}")
    print("=" * 80 + "\n")
    
    logger.info("Remediation script completed")


if __name__ == "__main__":
    main()
