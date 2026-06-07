"""Create the two-table Dataverse schema for Agent Sharing Access Restriction Detector.

Tables
------
1. fsi_AgentSharingCompliance       — Agent sharing compliance tracking per zone
2. fsi_ApprovedSecurityGroupPolicy  — Approved security groups per governance zone

Two solution-specific global option sets (``fsi_ASARD_*``) are created by
this script.  The shared option sets ``fsi_acv_zone`` and
``fsi_acv_severity`` are referenced but **not** created here — they are
provisioned by the CAA schema script (``create_dataverse_schema.py``).

Usage::

    python scripts/create_asard_dataverse_schema.py --dry-run
    python scripts/create_asard_dataverse_schema.py --verbose
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, Dict, List

from caa_client import CAAClient

logger = logging.getLogger(__name__)

# =========================================================================
# Shared option sets — referenced but NOT created by this script
# =========================================================================
# fsi_acv_zone and fsi_acv_severity are created by the CAA schema script
# (create_dataverse_schema.py).  ASARD tables bind picklist columns to
# these shared option sets but do not recreate them.

# =========================================================================
# Solution-specific option sets (ASARD)
# =========================================================================


def _label(text: str) -> Dict[str, Any]:
    """Build a localised label structure."""
    return {"LocalizedLabels": [{"Label": text, "LanguageCode": 1033}]}


SOLUTION_OPTIONSETS: Dict[str, Dict[str, Any]] = {
    "fsi_ASARD_compliancestatus": {
        "Name": "fsi_ASARD_compliancestatus",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "ASARD Compliance Status", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {"Value": 0, "Label": _label("Compliant")},
            {"Value": 1, "Label": _label("NonCompliant")},
            {"Value": 2, "Label": _label("Exception")},
            {"Value": 3, "Label": _label("Error")},
        ],
    },
    "fsi_ASARD_violationtype": {
        "Name": "fsi_ASARD_violationtype",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "ASARD Violation Type", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {"Value": 0, "Label": _label("Everyone")},
            {"Value": 1, "Label": _label("Public")},
            {"Value": 2, "Label": _label("UnapprovedGroup")},
            {"Value": 3, "Label": _label("ExcessiveIndividual")},
            {"Value": 4, "Label": _label("CrossTenant")},
        ],
    },
}

# =========================================================================
# Column definition helpers
# =========================================================================


def _string_col(
    schema_name: str, display: str, *, max_length: int = 100, required: bool = False
) -> Dict[str, Any]:
    """StringAttributeMetadata definition."""
    return {
        "@odata.type": "#Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "SchemaName": schema_name,
        "DisplayName": _label(display),
        "RequiredLevel": {"Value": "ApplicationRequired" if required else "None"},
        "MaxLength": max_length,
    }


def _memo_col(
    schema_name: str, display: str, *, required: bool = False
) -> Dict[str, Any]:
    """MemoAttributeMetadata definition."""
    return {
        "@odata.type": "#Microsoft.Dynamics.CRM.MemoAttributeMetadata",
        "SchemaName": schema_name,
        "DisplayName": _label(display),
        "RequiredLevel": {"Value": "ApplicationRequired" if required else "None"},
        "MaxLength": 1048576,
        "Format": "TextArea",
    }


def _boolean_col(
    schema_name: str, display: str, *, default: bool = False, required: bool = False
) -> Dict[str, Any]:
    """BooleanAttributeMetadata definition."""
    return {
        "@odata.type": "#Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
        "SchemaName": schema_name,
        "DisplayName": _label(display),
        "RequiredLevel": {"Value": "ApplicationRequired" if required else "None"},
        "DefaultValue": default,
        "OptionSet": {
            "TrueOption": {"Value": 1, "Label": _label("Yes")},
            "FalseOption": {"Value": 0, "Label": _label("No")},
        },
    }


def _datetime_col(
    schema_name: str, display: str, *, required: bool = False
) -> Dict[str, Any]:
    """DateTimeAttributeMetadata definition."""
    return {
        "@odata.type": "#Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
        "SchemaName": schema_name,
        "DisplayName": _label(display),
        "RequiredLevel": {"Value": "ApplicationRequired" if required else "None"},
        "Format": "DateAndTime",
        "DateTimeBehavior": {"Value": "UserLocal"},
    }


def _picklist_col(
    schema_name: str, display: str, global_optionset_name: str, *, required: bool = False
) -> Dict[str, Any]:
    """PicklistAttributeMetadata bound to a global option set."""
    return {
        "@odata.type": "#Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
        "SchemaName": schema_name,
        "DisplayName": _label(display),
        "RequiredLevel": {"Value": "ApplicationRequired" if required else "None"},
        "GlobalOptionSet@odata.bind": (
            f"/GlobalOptionSetDefinitions(Name='{global_optionset_name}')"
        ),
    }


# =========================================================================
# Table definitions
# =========================================================================


def _agent_sharing_compliance_table_definition() -> Dict[str, Any]:
    """fsi_AgentSharingCompliance table definition (OrganizationOwned)."""
    return {
        "SchemaName": "fsi_AgentSharingCompliance",
        "DisplayName": _label("Agent Sharing Compliance"),
        "DisplayCollectionName": _label("Agent Sharing Compliance Records"),
        "Description": _label(
            "Agent sharing compliance tracking per governance zone"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_agentsharingcompliances",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_agent_name",
        "Attributes": [
            _string_col("fsi_agent_name", "Agent Name", max_length=200, required=True),
        ],
    }


def _agent_sharing_compliance_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_AgentSharingCompliance (added after table creation)."""
    return [
        _string_col("fsi_agent_id", "Agent ID", max_length=100, required=True),
        _string_col("fsi_environment_id", "Environment ID", max_length=100, required=True),
        _string_col("fsi_environment_name", "Environment Name", max_length=200),
        _memo_col("fsi_sharing_principals_json", "Sharing Principals JSON"),
        _picklist_col("fsi_violation_type", "Violation Type", "fsi_ASARD_violationtype"),
        _picklist_col("fsi_zone", "Zone", "fsi_acv_zone"),
        _picklist_col("fsi_compliance_status", "Compliance Status", "fsi_ASARD_compliancestatus", required=True),
        _datetime_col("fsi_last_checked", "Last Checked", required=True),
        _datetime_col("fsi_remediation_date", "Remediation Date"),
        _string_col("fsi_scan_run_id", "Scan Run ID", max_length=100),
        _string_col("fsi_evidence_hash", "Evidence Hash", max_length=64),
        # Exception tracking columns (Phase 4)
        _datetime_col("fsi_exception_expires_at", "Exception Expires At"),
        _memo_col("fsi_exception_justification", "Exception Justification"),
        _string_col("fsi_exception_approved_by", "Exception Approved By", max_length=256),
        _datetime_col("fsi_exception_approved_at", "Exception Approved At"),
        _datetime_col("fsi_exception_review_date", "Exception Review Date"),
    ]


def _approved_security_group_policy_table_definition() -> Dict[str, Any]:
    """fsi_ApprovedSecurityGroupPolicy table definition (OrganizationOwned)."""
    return {
        "SchemaName": "fsi_ApprovedSecurityGroupPolicy",
        "DisplayName": _label("Approved Security Group Policy"),
        "DisplayCollectionName": _label("Approved Security Group Policies"),
        "Description": _label(
            "Approved security groups per governance zone for agent sharing"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_approvedsecuritygrouppolicies",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_group_name",
        "Attributes": [
            _string_col("fsi_group_name", "Group Name", max_length=200, required=True),
        ],
    }


def _approved_security_group_policy_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_ApprovedSecurityGroupPolicy (added after table creation)."""
    return [
        _picklist_col("fsi_zone", "Zone", "fsi_acv_zone", required=True),
        _string_col("fsi_group_id", "Group ID", max_length=100, required=True),
        _memo_col("fsi_purpose", "Purpose"),
        _boolean_col("fsi_is_active", "Is Active", default=True),
        _string_col("fsi_added_by", "Added By", max_length=256),
        _datetime_col("fsi_added_at", "Added At"),
    ]


# =========================================================================
# Schema creation functions
# =========================================================================


def create_solution_optionsets(client: CAAClient, dry_run: bool = False) -> None:
    """Create ASARD solution-specific global option sets (idempotent)."""
    for name, definition in SOLUTION_OPTIONSETS.items():
        existing = client.get_global_optionset(name)
        if existing is not None:
            logger.info("Global option set %s already exists — skipping", name)
            print(f"Global option set {name} already exists — skipping")
            continue
        logger.info("Creating global option set %s", name)
        print(f"Creating global option set {name} ...")
        client.create_global_optionset(definition)
        print(f"  Created {name}")


def _create_table_with_columns(
    client: CAAClient,
    table_def: Dict[str, Any],
    columns: List[Dict[str, Any]],
    dry_run: bool = False,
) -> None:
    """Create a table and then add its columns (idempotent)."""
    logical_name = table_def["SchemaName"].lower()
    schema_name = table_def["SchemaName"]

    created = client.create_table(table_def)
    if created:
        print(f"  Created table {schema_name}")
    else:
        print(f"  Table {schema_name} already exists")

    # Add columns (idempotent — each is checked individually)
    for col in columns:
        col_name = col.get("SchemaName", "unknown")
        added = client.create_column(logical_name, col)
        if added:
            print(f"    Added column {col_name}")
        else:
            print(f"    Column {col_name} already exists")


def create_agent_sharing_compliance_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_AgentSharingCompliance table, columns, and alternate key."""
    print("\n--- fsi_AgentSharingCompliance ---")
    _create_table_with_columns(
        client,
        _agent_sharing_compliance_table_definition(),
        _agent_sharing_compliance_columns(),
        dry_run,
    )

    # Alternate key for upsert on (fsi_agent_id, fsi_environment_id)
    key_name = "fsi_agentsharingcompliance_agentkey"
    logical_name = "fsi_agentsharingcompliance"
    print(f"  Creating alternate key {key_name} ...")

    if dry_run or client.dry_run:
        print(f"  [DRY-RUN] Would create alternate key {key_name}")
        return

    # Check if key already exists
    url = (
        f"{client.api_url}/EntityDefinitions(LogicalName='{logical_name}')"
        f"/Keys"
    )
    try:
        resp = client._session.get(url, headers=client._get_headers(), timeout=30)
        resp.raise_for_status()
        existing_keys = resp.json().get("value", [])
        for key in existing_keys:
            if key.get("SchemaName", "").lower() == key_name.lower():
                print(f"  Alternate key {key_name} already exists — skipping")
                return
    except Exception:
        logger.warning("Could not check existing keys — attempting creation")

    key_def = {
        "SchemaName": key_name,
        "DisplayName": _label("Agent + Environment Key"),
        "KeyAttributes": ["fsi_agent_id", "fsi_environment_id"],
    }

    try:
        resp = client._session.post(
            url, headers=client._get_headers(), json=key_def, timeout=60
        )
        resp.raise_for_status()
        print(f"  Created alternate key {key_name}")
    except Exception as exc:
        logger.error("Failed to create alternate key: %s", exc)
        print(f"  WARNING: Could not create alternate key — {exc}")


def create_approved_security_group_policy_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_ApprovedSecurityGroupPolicy table and columns."""
    print("\n--- fsi_ApprovedSecurityGroupPolicy ---")
    _create_table_with_columns(
        client,
        _approved_security_group_policy_table_definition(),
        _approved_security_group_policy_columns(),
        dry_run,
    )


def seed_default_policy(client: CAAClient, dry_run: bool = False) -> None:
    """Insert template approved group policy records for each zone.

    These are documentation placeholders — admins must populate with
    actual Microsoft Entra ID security group IDs for their organization.
    """
    entity_set = "fsi_approvedsecuritygrouppolicies"

    seeds = [
        {
            "fsi_group_name": "Zone 1 — Personal Productivity (No Group Sharing)",
            "fsi_zone": 1,
            "fsi_group_id": "00000000-0000-0000-0000-000000000000",
            "fsi_purpose": "Documentation placeholder. Zone 1 does not permit group sharing. "
                           "No approved groups needed.",
            "fsi_is_active": False,
            "fsi_added_by": "ASARD Schema Deployment",
        },
        {
            "fsi_group_name": "Zone 2 — Team Collaboration (Named Groups)",
            "fsi_zone": 2,
            "fsi_group_id": "00000000-0000-0000-0000-000000000000",
            "fsi_purpose": "Template record. Replace with actual Azure AD security group IDs "
                           "approved by team managers for Zone 2 collaboration.",
            "fsi_is_active": False,
            "fsi_added_by": "ASARD Schema Deployment",
        },
        {
            "fsi_group_name": "Zone 3 — Enterprise Approved Security Group",
            "fsi_zone": 3,
            "fsi_group_id": "00000000-0000-0000-0000-000000000000",
            "fsi_purpose": "Template record. Replace with actual Azure AD security group IDs "
                           "pre-approved by enterprise security for Zone 3 managed agents.",
            "fsi_is_active": False,
            "fsi_added_by": "ASARD Schema Deployment",
        },
    ]

    for seed in seeds:
        name = seed["fsi_group_name"]
        existing = client.query(
            entity_set,
            filter=f"fsi_group_name eq '{name}'",
        )
        if existing:
            print(f"  Seed record '{name}' already exists — skipping")
            continue
        if dry_run or client.dry_run:
            print(f"  [DRY-RUN] Would create seed record '{name}'")
            continue
        client.create_record(entity_set, seed)
        print(f"  Created seed record '{name}'")


def create_schema(client: CAAClient, dry_run: bool = False) -> None:
    """Orchestrate creation of all option sets, tables, and seed data.

    This function is idempotent — safe to re-run against an existing
    environment.  Shared option sets (fsi_acv_zone, fsi_acv_severity)
    are NOT created here; they must already exist from the CAA schema
    deployment.
    """
    print("=" * 60)
    print("ASARD Dataverse Schema Deployment")
    print("=" * 60)

    if dry_run:
        print("\n*** DRY-RUN MODE — no changes will be made ***\n")

    # 1. Solution-specific option sets (fsi_ASARD_*)
    #    NOTE: fsi_acv_zone and fsi_acv_severity are shared and created
    #    by the CAA schema script — not recreated here.
    print("\n[1/4] Creating ASARD solution-specific option sets ...")
    create_solution_optionsets(client, dry_run)

    # 2. Agent Sharing Compliance table + alternate key
    print("\n[2/4] Creating Agent Sharing Compliance table ...")
    create_agent_sharing_compliance_table(client, dry_run)

    # 3. Approved Security Group Policy table
    print("\n[3/4] Creating Approved Security Group Policy table ...")
    create_approved_security_group_policy_table(client, dry_run)

    # 4. Seed default approved group policy records
    print("\n[4/4] Seeding default approved group policy records ...")
    seed_default_policy(client, dry_run)

    print("\n" + "=" * 60)
    print("Schema deployment complete")
    print("=" * 60)


# =========================================================================
# CLI entry point
# =========================================================================


def main() -> None:
    """CLI entry point for schema deployment."""
    parser = argparse.ArgumentParser(
        description="Deploy ASARD Dataverse schema (2 tables + 2 option sets + seed data)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without making API calls",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )
    parser.add_argument(
        "--tenant-id",
        default=None,
        help="Entra ID tenant GUID (or set CAA_TENANT_ID)",
    )
    parser.add_argument(
        "--environment-url",
        default=None,
        help="Dataverse environment URL (or set CAA_ENVIRONMENT_URL)",
    )
    parser.add_argument(
        "--client-id",
        default=None,
        help="App registration client ID (or set CAA_CLIENT_ID)",
    )
    parser.add_argument(
        "--client-secret",
        default=None,
        help="App registration client secret (or set CAA_CLIENT_SECRET)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Use interactive (delegated) authentication",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        client = CAAClient(
            tenant_id=args.tenant_id,
            environment_url=args.environment_url,
            client_id=args.client_id,
            client_secret=args.client_secret,
            interactive=args.interactive,
            dry_run=args.dry_run,
        )

        if not args.dry_run:
            print("Testing connection ...")
            if not client.test_connection():
                print("ERROR: Cannot connect to Dataverse environment", file=sys.stderr)
                sys.exit(1)
            print("Connection OK\n")

        create_schema(client, dry_run=args.dry_run)

    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Schema deployment failed")
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
