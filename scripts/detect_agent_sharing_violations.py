"""Agent Sharing Access Restriction Detector (ASARD) — Detection Script.

This script enumerates all Copilot Studio agents across Power Platform
environments via the BAP Admin API, retrieves sharing configurations,
and evaluates compliance against zone-based sharing rules.

Purpose
-------
- Enumerate all environments accessible to the authenticated principal
- Enumerate all Copilot Studio agents in each environment
- Retrieve sharing principals (permissions) for each agent
- Classify each environment into a governance zone (0–3)
- Evaluate agent sharing configuration against zone-specific rules
- Track scan run metadata and evidence hashes for audit trail

Requirements
------------
- Python 3.9+
- msal>=1.30.0
- requests>=2.32.0
- Environment variables (BAP Admin API):
  - BAP_TENANT_ID
  - BAP_CLIENT_ID
  - BAP_CLIENT_SECRET (or use --interactive flag)
- Environment variables (Dataverse — for zone classification):
  - CAA_TENANT_ID
  - CAA_ENVIRONMENT_URL
  - CAA_CLIENT_ID
  - CAA_CLIENT_SECRET

Usage
-----
Service principal auth::

    python detect_agent_sharing_violations.py --dry-run --verbose

Interactive auth::

    python detect_agent_sharing_violations.py --interactive --dry-run

Filter environments::

    python detect_agent_sharing_violations.py --environment-filter "Prod.*" --dry-run
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# Import Phase 1 modules
from asard_zone_rules import check_agent_compliance
from bap_admin_client import BAPAdminClient
from caa_client import CAAClient

logger = logging.getLogger(__name__)


# =========================================================================
# Environment enumeration
# =========================================================================


def enumerate_environments(
    bap_client: BAPAdminClient, environment_filter: Optional[str]
) -> List[Dict[str, Any]]:
    """Enumerate Power Platform environments, optionally filtered by name.

    Parameters
    ----------
    bap_client : BAPAdminClient
        Authenticated BAP Admin API client.
    environment_filter : str | None
        Optional regex pattern to filter environments by display name.

    Returns
    -------
    list[dict]
        List of environment objects from BAP Admin API.
    """
    logger.info("Enumerating environments...")
    environments = bap_client.list_environments()

    if not environments:
        logger.warning("No environments found (API may have failed or tenant is empty)")
        return []

    logger.info("Found %d environment(s)", len(environments))

    # Apply filter if provided
    if environment_filter:
        try:
            pattern = re.compile(environment_filter, re.IGNORECASE)
            filtered = [
                env
                for env in environments
                if pattern.search(env.get("properties", {}).get("displayName", ""))
            ]
            logger.info(
                "Environment filter '%s' matched %d of %d environment(s)",
                environment_filter,
                len(filtered),
                len(environments),
            )
            return filtered
        except re.error as exc:
            logger.error("Invalid environment filter regex '%s': %s", environment_filter, exc)
            return environments

    return environments


# =========================================================================
# Agent enumeration per environment
# =========================================================================


def enumerate_agents_in_environment(
    bap_client: BAPAdminClient, environment: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Enumerate Copilot Studio agents in a single environment.

    Parameters
    ----------
    bap_client : BAPAdminClient
        Authenticated BAP Admin API client.
    environment : dict
        Environment object from ``enumerate_environments()``.

    Returns
    -------
    list[dict]
        List of agent (bot) objects from BAP Admin API.
        Empty list on API failure (graceful degradation).
    """
    environment_id = environment.get("name", "")
    environment_name = environment.get("properties", {}).get("displayName", environment_id)

    if not environment_id:
        logger.warning("Environment object missing 'name' field — skipping")
        return []

    agents = bap_client.list_agents(environment_id)
    return agents


# =========================================================================
# Permissions retrieval per agent
# =========================================================================


def get_agent_permissions_json(
    bap_client: BAPAdminClient, environment_id: str, agent_id: str
) -> Optional[str]:
    """Retrieve agent sharing permissions as JSON string.

    Parameters
    ----------
    bap_client : BAPAdminClient
        Authenticated BAP Admin API client.
    environment_id : str
        Environment GUID.
    agent_id : str
        Agent (bot) GUID.

    Returns
    -------
    str | None
        JSON array of sharing principals, or *None* if retrieval fails.
    """
    permissions = bap_client.get_agent_permissions(environment_id, agent_id)
    if permissions is None:
        return None
    return json.dumps(permissions)


# =========================================================================
# Pre-flight validation
# =========================================================================


def validate_approved_groups_policy(caa_client: CAAClient) -> bool:
    """Validate that Zone 3 approved group policy table is not empty.

    Parameters
    ----------
    caa_client : CAAClient
        Dataverse client for policy queries.

    Returns
    -------
    bool
        *True* if approved groups found or query fails (non-blocking warning),
        *False* if table is confirmed empty (logs warning).
    """
    logger.info("Validating Zone 3 approved group policy table...")
    try:
        records = caa_client.query(
            "fsi_approvedsecuritygrouppolicies",
            filter="fsi_zone eq 3 and fsi_is_active eq true",
            select=["fsi_group_id"],
        )
        if not records:
            logger.warning(
                "Zone 3 approved group policy table is empty. "
                "Zone 3 agents may false-positive as non-compliant."
            )
            return False
        logger.info("Found %d approved group(s) for Zone 3", len(records))
        return True
    except Exception as exc:
        logger.warning(
            "Failed to validate approved groups policy (scan will proceed): %s", exc
        )
        # Non-blocking: return True to allow scan to continue
        return True


# =========================================================================
# Dataverse persistence
# =========================================================================


def _map_violation_type_to_optionset(violation_type: Optional[str]) -> Optional[int]:
    """Map violation type string to Dataverse option set integer.
    
    Parameters
    ----------
    violation_type : str | None
        Violation type from zone rules ('Everyone', 'Public', etc.)
    
    Returns
    -------
    int | None
        Option set value (0-4) or None if compliant/error.
    """
    if violation_type is None:
        return None
    
    mapping = {
        "Everyone": 0,
        "Public": 1,
        "UnapprovedGroup": 2,
        "ExcessiveIndividual": 3,
        "CrossTenant": 4,
    }
    return mapping.get(violation_type)


def _map_compliance_status_to_optionset(compliance_status: str) -> int:
    """Map compliance status string to Dataverse option set integer.
    
    Parameters
    ----------
    compliance_status : str
        Compliance status ('Compliant', 'NonCompliant', 'Exception', 'Error')
    
    Returns
    -------
    int
        Option set value (0-3).
    """
    mapping = {
        "Compliant": 0,
        "NonCompliant": 1,
        "Exception": 2,
        "Error": 3,
    }
    return mapping.get(compliance_status, 3)  # Default to Error


def upsert_compliance_record(
    caa_client: CAAClient, record: Dict[str, Any]
) -> Optional[str]:
    """Upsert a compliance record to Dataverse via alternate key.
    
    Parameters
    ----------
    caa_client : CAAClient
        Dataverse Web API client.
    record : dict
        Compliance result from detection scan.
    
    Returns
    -------
    str | None
        HTTP status code (201=created, 204=updated) or None on failure.
    """
    # Build Dataverse record payload
    agent_id = record["agent_id"]
    environment_id = record["environment_id"]
    
    # Phase 4: Check for existing active exception
    # If agent has active exception (compliance_status=2, expires_at >= now),
    # preserve exception fields and set compliance_status=Exception
    existing_record = None
    has_active_exception = False
    
    try:
        # Query for existing record using alternate key
        alternate_key = f"fsi_agent_id='{agent_id}',fsi_environment_id='{environment_id}'"
        url = f"{caa_client.api_url}/fsi_agentsharingcompliances({alternate_key})"
        headers = caa_client._get_headers()
        response = caa_client._session.get(url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            existing_record = response.json()
            
            # Check if exception is active (status=2 AND expires_at >= now)
            compliance_status = existing_record.get("fsi_compliance_status")
            expires_at_str = existing_record.get("fsi_exception_expires_at")
            
            if compliance_status == 2 and expires_at_str:
                # Parse expiration date
                from dateutil import parser as dateparser
                expires_at = dateparser.parse(expires_at_str)
                now = datetime.now(timezone.utc)
                
                if expires_at >= now:
                    has_active_exception = True
                    logger.debug(
                        "Agent %s has active exception (expires %s) — preserving exception fields",
                        record["agent_name"],
                        expires_at.strftime("%Y-%m-%d"),
                    )
    except Exception as exc:
        # If query fails, proceed with normal upsert (no exception preservation)
        logger.debug("Exception check query failed for %s: %s", record["agent_name"], exc)
    
    # Map string values to option set integers
    violation_type_int = _map_violation_type_to_optionset(record.get("violation_type"))
    
    # If active exception exists, override compliance_status to Exception (2)
    if has_active_exception:
        compliance_status_int = 2  # Exception
    else:
        compliance_status_int = _map_compliance_status_to_optionset(record["compliance_status"])
    
    payload = {
        "fsi_agent_id": agent_id,
        "fsi_agent_name": record["agent_name"],
        "fsi_environment_id": environment_id,
        "fsi_environment_name": record["environment_name"],
        "fsi_sharing_principals_json": record.get("sharing_principals_json"),
        "fsi_violation_type": violation_type_int,
        "fsi_zone": record.get("zone", 0),
        "fsi_compliance_status": compliance_status_int,
        "fsi_last_checked": record["last_checked"],
        "fsi_remediation_date": None,  # Phase 3 will populate this
        "fsi_scan_run_id": record["scan_run_id"],
        "fsi_evidence_hash": record.get("evidence_hash"),
    }
    
    # If active exception, preserve exception fields from existing record
    if has_active_exception and existing_record:
        payload["fsi_exception_expires_at"] = existing_record.get("fsi_exception_expires_at")
        payload["fsi_exception_justification"] = existing_record.get("fsi_exception_justification")
        payload["fsi_exception_approved_by"] = existing_record.get("fsi_exception_approved_by")
        payload["fsi_exception_approved_at"] = existing_record.get("fsi_exception_approved_at")
        payload["fsi_exception_review_date"] = existing_record.get("fsi_exception_review_date")
    
    # Use alternate key for upsert: (fsi_agent_id, fsi_environment_id)
    alternate_key = f"fsi_agent_id='{agent_id}',fsi_environment_id='{environment_id}'"
    url = f"{caa_client.api_url}/fsi_agentsharingcompliances({alternate_key})"
    
    try:
        headers = caa_client._get_headers()
        response = caa_client._session.patch(
            url, headers=headers, json=payload, timeout=60
        )
        
        if response.status_code in (201, 204):
            status_label = "created" if response.status_code == 201 else "updated"
            logger.debug(
                "Dataverse upsert %s: %s (%s)",
                status_label,
                record["agent_name"],
                agent_id,
            )
            return str(response.status_code)
        else:
            logger.error(
                "Dataverse upsert failed for %s (%s): HTTP %d — %s",
                record["agent_name"],
                agent_id,
                response.status_code,
                response.text[:200],
            )
            return None
    except Exception as exc:
        logger.error(
            "Dataverse upsert exception for %s (%s): %s",
            record["agent_name"],
            agent_id,
            exc,
        )
        return None


def write_compliance_results_to_dataverse(
    caa_client: CAAClient, results: List[Dict[str, Any]], dry_run: bool
) -> Dict[str, int]:
    """Write compliance results to Dataverse in batch.
    
    Parameters
    ----------
    caa_client : CAAClient
        Dataverse Web API client.
    results : list[dict]
        Compliance results from detection scan.
    dry_run : bool
        If True, skip actual writes and return zero counts.
    
    Returns
    -------
    dict
        Summary with 'upserted', 'failed', and 'exceptions' counts.
    """
    if dry_run:
        logger.info("DRY RUN: Would upsert %d record(s) to Dataverse", len(results))
        return {"upserted": 0, "failed": 0, "exceptions": 0}
    
    logger.info("Writing %d compliance record(s) to Dataverse...", len(results))
    
    upserted = 0
    failed = 0
    exceptions = 0
    
    for idx, record in enumerate(results, start=1):
        # Progress logging (every 10 records or all in DEBUG)
        if idx % 10 == 0 or logger.isEnabledFor(logging.DEBUG):
            logger.info(
                "Dataverse upsert [%d/%d]: %s",
                idx,
                len(results),
                record["agent_name"],
            )
        
        # Check if this record will be treated as an exception
        agent_id = record["agent_id"]
        environment_id = record["environment_id"]
        
        try:
            # Query for existing active exception
            alternate_key = f"fsi_agent_id='{agent_id}',fsi_environment_id='{environment_id}'"
            url = f"{caa_client.api_url}/fsi_agentsharingcompliances({alternate_key})"
            headers = caa_client._get_headers()
            response = caa_client._session.get(url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                existing_record = response.json()
                compliance_status = existing_record.get("fsi_compliance_status")
                expires_at_str = existing_record.get("fsi_exception_expires_at")
                
                if compliance_status == 2 and expires_at_str:
                    from dateutil import parser as dateparser
                    expires_at = dateparser.parse(expires_at_str)
                    now = datetime.now(timezone.utc)
                    
                    if expires_at >= now:
                        exceptions += 1
        except Exception:
            pass  # If check fails, proceed normally
        
        status = upsert_compliance_record(caa_client, record)
        if status:
            upserted += 1
        else:
            failed += 1
    
    logger.info(
        "Dataverse writes complete: %d upserted, %d failed, %d exceptions preserved",
        upserted,
        failed,
        exceptions,
    )
    
    return {"upserted": upserted, "failed": failed, "exceptions": exceptions}


# =========================================================================
# Console output formatting
# =========================================================================


def print_console_output(
    results: List[Dict[str, Any]],
    summary: Dict[str, Any],
    csv_path: Optional[str],
    dataverse_summary: Optional[Dict[str, int]],
) -> None:
    """Print formatted console output with scan results.
    
    Parameters
    ----------
    results : list[dict]
        Compliance results from detection scan.
    summary : dict
        Summary statistics from scan.
    csv_path : str | None
        Path to CSV export file, if exported.
    dataverse_summary : dict | None
        Dataverse write summary, if performed.
    """
    print("\n" + "=" * 70)
    print("Agent Sharing Compliance Scan")
    print("=" * 70)
    print(f"Scan Run ID: {summary['scan_run_id']}")
    print(f"Started:     {summary['scan_started']}")
    print(f"Completed:   {summary['scan_completed']}")
    print()
    
    # Group results by environment
    results_by_env: Dict[str, List[Dict[str, Any]]] = {}
    for result in results:
        env_id = result["environment_id"]
        if env_id not in results_by_env:
            results_by_env[env_id] = []
        results_by_env[env_id].append(result)
    
    # Print per-environment results
    for env_id, env_results in results_by_env.items():
        # Use first result for environment metadata
        first_result = env_results[0]
        env_name = first_result["environment_name"]
        zone = first_result.get("zone", 0)
        zone_name = first_result.get("zone_name", "Unclassified")
        
        print(f"Environment: {env_name} (Zone {zone}: {zone_name})")
        
        for result in env_results:
            agent_name = result["agent_name"]
            compliance_status = result["compliance_status"]
            
            if compliance_status == "Compliant":
                # Green checkmark for compliant
                principals_count = len(json.loads(result.get("sharing_principals_json", "[]")))
                print(f"  [\u2713] Agent: {agent_name} — Compliant ({principals_count} principals)")
            elif compliance_status == "NonCompliant":
                # Red X for violations
                violation_type = result.get("violation_type", "Unknown")
                details = result.get("details", "")
                print(f"  [\u2717] Agent: {agent_name} — VIOLATION: {violation_type} ({details})")
            elif compliance_status == "Error":
                # Yellow ! for errors
                details = result.get("details", "Unknown error")
                print(f"  [!] Agent: {agent_name} — ERROR: {details}")
        
        print()
    
    # Print summary statistics
    print("-" * 70)
    print("Summary")
    print("-" * 70)
    print(f"Total Environments: {summary['total_environments']}")
    print(f"Total Agents:       {summary['total_agents']}")
    
    total = summary['total_agents']
    if total > 0:
        compliant_pct = (summary['compliant'] / total) * 100
        non_compliant_pct = (summary['non_compliant'] / total) * 100
    else:
        compliant_pct = 0.0
        non_compliant_pct = 0.0
    
    print(f"Compliant:          {summary['compliant']} ({compliant_pct:.1f}%)")
    print(f"Non-Compliant:      {summary['non_compliant']} ({non_compliant_pct:.1f}%)")
    print(f"Exceptions:         {summary['exceptions']}")
    print(f"Errors:             {summary['errors']}")
    print()
    
    if csv_path:
        print(f"CSV Export:         {csv_path}")
    
    if dataverse_summary:
        print(
            f"Dataverse Records:  {dataverse_summary['upserted']} upserted, "
            f"{dataverse_summary['failed']} failed"
        )
    
    print("=" * 70)
    print()


# =========================================================================
# CSV export
# =========================================================================


def export_to_csv(
    results: List[Dict[str, Any]], summary: Dict[str, Any], output_dir: str
) -> str:
    """Export compliance results to CSV file.
    
    Parameters
    ----------
    results : list[dict]
        Compliance results from detection scan.
    summary : dict
        Summary statistics (used for scan_run_id).
    output_dir : str
        Output directory for CSV file.
    
    Returns
    -------
    str
        Path to CSV file.
    """
    # Create output directory if missing
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate CSV filename with timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    csv_filename = f"asard-scan-{timestamp}.csv"
    csv_path = output_path / csv_filename
    
    logger.info("Exporting results to CSV: %s", csv_path)
    
    # Define CSV columns
    fieldnames = [
        "scan_run_id",
        "agent_id",
        "agent_name",
        "environment_id",
        "environment_name",
        "zone",
        "zone_name",
        "compliance_status",
        "violation_type",
        "details",
        "sharing_principals_json",
        "evidence_hash",
        "last_checked",
    ]
    
    # Map compliance status and violation type to human-readable strings
    def format_compliance_status(status: str) -> str:
        """Map internal status to human-readable label."""
        return status  # Already human-readable from detection script
    
    def format_violation_type(vtype: Optional[str]) -> str:
        """Map violation type to human-readable label."""
        if vtype is None:
            return ""
        return vtype  # Already human-readable from zone rules
    
    # Write CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        if not results:
            logger.warning("No results to export — CSV contains header only")
        
        for result in results:
            row = {
                "scan_run_id": result["scan_run_id"],
                "agent_id": result["agent_id"],
                "agent_name": result["agent_name"],
                "environment_id": result["environment_id"],
                "environment_name": result["environment_name"],
                "zone": result.get("zone", 0),
                "zone_name": result.get("zone_name", "Unclassified"),
                "compliance_status": format_compliance_status(result["compliance_status"]),
                "violation_type": format_violation_type(result.get("violation_type")),
                "details": result.get("details", ""),
                "sharing_principals_json": result.get("sharing_principals_json", ""),
                "evidence_hash": result.get("evidence_hash", ""),
                "last_checked": result["last_checked"],
            }
            writer.writerow(row)
    
    logger.info("CSV export complete: %d row(s) written", len(results))
    return str(csv_path)


# =========================================================================
# Teams notification
# =========================================================================


def send_teams_notification(
    webhook_url: str,
    results: List[Dict[str, Any]],
    summary: Dict[str, Any],
    card_template_path: str = "src/adaptive-card-asard-alert.json",
) -> bool:
    """Send Teams adaptive card notification via webhook.
    
    Parameters
    ----------
    webhook_url : str
        Teams incoming webhook URL.
    results : list[dict]
        Compliance results from detection scan.
    summary : dict
        Summary statistics.
    card_template_path : str
        Path to adaptive card template JSON file.
    
    Returns
    -------
    bool
        True if notification sent successfully, False otherwise.
    """
    try:
        # Load adaptive card template
        template_path = Path(card_template_path)
        if not template_path.exists():
            logger.error("Adaptive card template not found: %s", card_template_path)
            return False
        
        with open(template_path, "r", encoding="utf-8") as f:
            card_template = json.load(f)
        
        # Build violation list (top 5 non-compliant agents)
        non_compliant = [r for r in results if r["compliance_status"] == "NonCompliant"]
        non_compliant_sorted = sorted(
            non_compliant,
            key=lambda r: (r.get("violation_type", ""), r["agent_name"]),
        )
        top_violations = non_compliant_sorted[:5]
        
        # Format violation list as text
        violation_lines = []
        for result in top_violations:
            agent_name = result["agent_name"]
            env_name = result["environment_name"]
            zone_name = result.get("zone_name", "Unknown")
            violation_type = result.get("violation_type", "Unknown")
            details = result.get("details", "")
            
            violation_lines.append(
                f"• **{agent_name}** ({env_name})\n"
                f"  Zone: {zone_name} | Violation: {violation_type} — {details}"
            )
        
        violation_list = "\n\n".join(violation_lines) if violation_lines else "No violations to display"
        
        # Escape violation_list for JSON embedding (escape newlines, quotes, backslashes)
        violation_list_escaped = (
            violation_list
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )
        
        # Populate template placeholders
        card_json = json.dumps(card_template)
        card_json = card_json.replace("{{scan_run_id}}", summary["scan_run_id"])
        card_json = card_json.replace("{{scan_started}}", summary["scan_started"])
        card_json = card_json.replace("{{scan_completed}}", summary["scan_completed"])
        card_json = card_json.replace("{{total_agents}}", str(summary["total_agents"]))
        card_json = card_json.replace("{{total_environments}}", str(summary["total_environments"]))
        card_json = card_json.replace("{{compliant_count}}", str(summary["compliant"]))
        card_json = card_json.replace("{{non_compliant_count}}", str(summary["non_compliant"]))
        card_json = card_json.replace("{{exception_count}}", str(summary["exceptions"]))
        card_json = card_json.replace("{{error_count}}", str(summary["errors"]))
        card_json = card_json.replace("{{violation_list}}", violation_list_escaped)
        
        # Placeholder URLs (can be customized in future)
        card_json = card_json.replace("{{report_url}}", "https://admin.powerplatform.microsoft.com/")
        card_json = card_json.replace("{{exceptions_url}}", "https://admin.powerplatform.microsoft.com/")
        
        card = json.loads(card_json)
        
        # Send POST to Teams webhook
        logger.info("Sending Teams notification to webhook...")
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            json={"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]},
            timeout=30,
        )
        
        if response.status_code == 200:
            logger.info("Teams notification sent successfully")
            return True
        else:
            logger.error(
                "Teams notification failed: HTTP %d — %s",
                response.status_code,
                response.text[:200],
            )
            return False
    
    except Exception as exc:
        logger.warning("Teams notification exception (non-fatal): %s", exc)
        return False


# =========================================================================
# Main detection workflow
# =========================================================================


def run_detection_scan(
    bap_client: BAPAdminClient,
    caa_client: CAAClient,
    environment_filter: Optional[str],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Execute the full detection scan workflow.

    Parameters
    ----------
    bap_client : BAPAdminClient
        Authenticated BAP Admin API client.
    caa_client : CAAClient
        Dataverse client for zone classification and policy lookups.
    environment_filter : str | None
        Optional regex pattern to filter environments by name.

    Returns
    -------
    tuple[list[dict], dict]
        - Compliance results (list of dicts)
        - Summary statistics (dict)
    """
    # Generate scan run ID
    scan_run_id = str(uuid.uuid4())
    scan_start_time = datetime.now(timezone.utc).isoformat()
    logger.info("Starting scan run: %s", scan_run_id)

    # Pre-flight validation
    validate_approved_groups_policy(caa_client)

    # Initialize counters
    total_agents = 0
    compliant_count = 0
    non_compliant_count = 0
    exception_count = 0  # Phase 4 support (0 for now)
    error_count = 0

    compliance_results: List[Dict[str, Any]] = []

    # Step 1: Enumerate environments
    environments = enumerate_environments(bap_client, environment_filter)
    total_environments = len(environments)

    if not environments:
        logger.warning("No environments to scan — exiting early")
        scan_end_time = datetime.now(timezone.utc).isoformat()
        summary = {
            "scan_run_id": scan_run_id,
            "scan_started": scan_start_time,
            "scan_completed": scan_end_time,
            "total_environments": 0,
            "total_agents": 0,
            "compliant": 0,
            "non_compliant": 0,
            "exceptions": 0,
            "errors": 0,
        }
        return (compliance_results, summary)

    # Step 2: For each environment → enumerate agents → evaluate sharing
    for env_idx, environment in enumerate(environments, start=1):
        environment_id = environment.get("name", "")
        environment_name = environment.get("properties", {}).get(
            "displayName", environment_id
        )

        logger.info(
            "Environment [%d/%d]: %s", env_idx, total_environments, environment_name
        )

        # Enumerate agents in environment
        agents = enumerate_agents_in_environment(bap_client, environment)
        agent_count = len(agents)
        logger.info("  Found %d agent(s)", agent_count)

        if not agents:
            continue

        # Process each agent
        for agent_idx, agent in enumerate(agents, start=1):
            agent_id = agent.get("name", "")
            agent_name = agent.get("properties", {}).get("displayName", agent_id)

            logger.info("  Agent [%d/%d]: %s", agent_idx, agent_count, agent_name)
            total_agents += 1

            # Retrieve permissions
            logger.debug("    Retrieving permissions...")
            permissions_json = get_agent_permissions_json(
                bap_client, environment_id, agent_id
            )

            if permissions_json is None:
                # API failure — record error
                logger.error("    Failed to retrieve permissions — recording as Error")
                error_count += 1
                compliance_results.append(
                    {
                        "scan_run_id": scan_run_id,
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                        "environment_id": environment_id,
                        "environment_name": environment_name,
                        "zone": 0,
                        "zone_name": "Unclassified",
                        "sharing_principals_json": None,
                        "evidence_hash": None,
                        "compliant": False,
                        "violation_type": None,
                        "compliance_status": "Error",
                        "details": "Failed to retrieve agent permissions from BAP API",
                        "last_checked": datetime.now(timezone.utc).isoformat(),
                    }
                )
                continue

            # Generate evidence hash
            evidence_hash = hashlib.sha256(
                permissions_json.encode("utf-8")
            ).hexdigest()

            # Evaluate compliance
            try:
                result = check_agent_compliance(
                    agent_id=agent_id,
                    environment_id=environment_id,
                    environment_name=environment_name,
                    sharing_principals_json=permissions_json,
                    client=caa_client,
                )

                # Augment result with scan metadata
                result["scan_run_id"] = scan_run_id
                result["agent_name"] = agent_name
                result["environment_name"] = environment_name
                result["sharing_principals_json"] = permissions_json
                result["evidence_hash"] = evidence_hash
                result["last_checked"] = datetime.now(timezone.utc).isoformat()

                # Determine compliance_status
                if result.get("violation_type") == "Error":
                    result["compliance_status"] = "Error"
                    error_count += 1
                elif result["compliant"]:
                    result["compliance_status"] = "Compliant"
                    compliant_count += 1
                else:
                    result["compliance_status"] = "NonCompliant"
                    non_compliant_count += 1

                compliance_results.append(result)

                # Progress logging
                if result["compliant"]:
                    logger.info("    ✓ Compliant")
                else:
                    violation = result.get("violation_type", "Unknown")
                    logger.warning("    ✗ Violation: %s", violation)

            except Exception as exc:
                logger.exception("    Compliance check failed: %s", exc)
                error_count += 1
                compliance_results.append(
                    {
                        "scan_run_id": scan_run_id,
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                        "environment_id": environment_id,
                        "environment_name": environment_name,
                        "zone": 0,
                        "zone_name": "Unclassified",
                        "sharing_principals_json": permissions_json,
                        "evidence_hash": evidence_hash,
                        "compliant": False,
                        "violation_type": "Error",
                        "compliance_status": "Error",
                        "details": f"Compliance check exception: {exc}",
                        "last_checked": datetime.now(timezone.utc).isoformat(),
                    }
                )

    # Step 3: Compile summary
    scan_end_time = datetime.now(timezone.utc).isoformat()
    summary = {
        "scan_run_id": scan_run_id,
        "scan_started": scan_start_time,
        "scan_completed": scan_end_time,
        "total_environments": total_environments,
        "total_agents": total_agents,
        "compliant": compliant_count,
        "non_compliant": non_compliant_count,
        "exceptions": exception_count,
        "errors": error_count,
    }

    logger.info("Scan completed: %s", scan_run_id)
    logger.info("Summary: %d agents scanned", total_agents)
    logger.info("  Compliant: %d", compliant_count)
    logger.info("  Non-compliant: %d", non_compliant_count)
    logger.info("  Errors: %d", error_count)

    return (compliance_results, summary)


# =========================================================================
# CLI and main entrypoint
# =========================================================================


def configure_logging(verbose: bool, log_file: Optional[str]) -> None:
    """Configure logging handlers and format.

    Parameters
    ----------
    verbose : bool
        If *True*, set log level to DEBUG; otherwise INFO.
    log_file : str | None
        Optional path to log file.
    """
    level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format))

    # File handler (optional)
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=level, format=log_format, handlers=handlers)


def main() -> int:
    """Main entrypoint for the detection script.

    Returns
    -------
    int
        Exit code (0 = success, 1 = error).
    """
    parser = argparse.ArgumentParser(
        description="Detect agent sharing violations across Power Platform environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Authentication arguments
    parser.add_argument(
        "--tenant-id",
        help="Entra ID tenant GUID (fallback: BAP_TENANT_ID)",
    )
    parser.add_argument(
        "--client-id",
        help="App registration client ID (fallback: BAP_CLIENT_ID)",
    )
    parser.add_argument(
        "--client-secret",
        help="App registration client secret (fallback: BAP_CLIENT_SECRET)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Use interactive login (device code flow)",
    )

    # Scan options
    parser.add_argument(
        "--environment-filter",
        help="Regex pattern to filter environments by name (e.g., 'Prod.*')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enumerate and evaluate but skip Dataverse writes",
    )

    # Output options
    parser.add_argument(
        "--output-dir",
        default="./reports/",
        help="Output directory for CSV export (default: ./reports/)",
    )
    parser.add_argument(
        "--teams-webhook-url",
        help="Teams incoming webhook URL for notifications (optional)",
    )

    # Logging options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging",
    )
    parser.add_argument(
        "--log-file",
        help="Path to log file (optional)",
    )

    args = parser.parse_args()

    # Configure logging
    configure_logging(args.verbose, args.log_file)

    logger.info("=== Agent Sharing Access Restriction Detector (ASARD) ===")
    logger.info("Dry-run mode: %s", args.dry_run)

    try:
        # Step 1: Initialize BAP Admin API client
        logger.info("Initializing BAP Admin API client...")
        bap_client = BAPAdminClient(
            tenant_id=args.tenant_id,
            client_id=args.client_id,
            client_secret=args.client_secret,
            interactive=args.interactive,
        )

        # Step 2: Test connection
        logger.info("Testing BAP Admin API connection...")
        if not bap_client.test_connection():
            logger.error("BAP Admin API connection test failed — cannot proceed")
            return 1

        # Step 3: Initialize Dataverse client (for zone classification)
        logger.info("Initializing Dataverse client...")
        caa_client = CAAClient()

        logger.info("Testing Dataverse connection...")
        if not caa_client.test_connection():
            logger.error("Dataverse connection test failed — cannot proceed")
            return 1

        # Step 4: Run detection scan
        logger.info("Starting detection scan...")
        compliance_results, summary = run_detection_scan(
            bap_client, caa_client, args.environment_filter
        )

        # Step 5: Write to Dataverse (unless dry-run)
        logger.info("Writing compliance results to Dataverse...")
        dataverse_summary = write_compliance_results_to_dataverse(
            caa_client, compliance_results, args.dry_run
        )

        # Step 6: Export to CSV
        logger.info("Exporting results to CSV...")
        csv_path = export_to_csv(compliance_results, summary, args.output_dir)

        # Step 7: Print console output
        print_console_output(
            compliance_results, summary, csv_path, dataverse_summary
        )

        # Step 8: Send Teams notification (if webhook URL provided)
        if args.teams_webhook_url:
            logger.info("Sending Teams notification...")
            send_teams_notification(
                args.teams_webhook_url,
                compliance_results,
                summary,
            )
        else:
            logger.debug("Teams webhook URL not provided — skipping notification")

        return 0

    except KeyboardInterrupt:
        logger.warning("Scan interrupted by user")
        return 1
    except Exception as exc:
        logger.exception("Scan failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
