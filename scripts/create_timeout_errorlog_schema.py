"""Create the Dataverse schema for Inactivity Timeout Enforcement error logging.

Tables
------
1. fsi_InactivityTimeoutErrorLog — Error logging for compliance scan failures

No new option sets are required — ``fsi_errortype`` uses free-text to
accommodate unanticipated error categories.

Usage::

    python scripts/create_timeout_errorlog_schema.py --dry-run
    python scripts/create_timeout_errorlog_schema.py --verbose
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, Dict, List

from caa_client import CAAClient

logger = logging.getLogger(__name__)

# =========================================================================
# Column definition helpers
# =========================================================================


def _label(text: str) -> Dict[str, Any]:
    """Build a localised label structure."""
    return {"LocalizedLabels": [{"Label": text, "LanguageCode": 1033}]}


def _string_col(
    schema_name: str, display: str, *, max_length: int = 100, required: bool = False
) -> Dict[str, Any]:
    """StringAttributeMetadata definition."""
    col: Dict[str, Any] = {
        "@odata.type": "#Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "SchemaName": schema_name,
        "DisplayName": _label(display),
        "RequiredLevel": {"Value": "ApplicationRequired" if required else "None"},
        "MaxLength": max_length,
    }
    return col


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


# =========================================================================
# Table definition
# =========================================================================


def _errorlog_table_definition() -> Dict[str, Any]:
    """fsi_InactivityTimeoutErrorLog table definition (OrganizationOwned — append-only)."""
    return {
        "SchemaName": "fsi_InactivityTimeoutErrorLog",
        "DisplayName": _label("Inactivity Timeout Error Log"),
        "DisplayCollectionName": _label("Inactivity Timeout Error Logs"),
        "Description": _label(
            "Error logging for inactivity timeout compliance scan failures"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_inactivitytimeouterrorlogs",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_name",
        "Attributes": [
            _string_col("fsi_name", "Name", max_length=256, required=True),
        ],
    }


def _errorlog_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_InactivityTimeoutErrorLog."""
    return [
        _string_col("fsi_environmentid", "Environment ID", max_length=100, required=True),
        _string_col("fsi_errortype", "Error Type", max_length=50, required=True),
        _memo_col("fsi_errorraw", "Error Raw"),
        _datetime_col("fsi_timestamp", "Timestamp", required=True),
    ]


# =========================================================================
# Schema creation functions
# =========================================================================


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


def create_errorlog_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_InactivityTimeoutErrorLog table and columns."""
    print("\n--- fsi_InactivityTimeoutErrorLog ---")
    _create_table_with_columns(
        client, _errorlog_table_definition(), _errorlog_columns(), dry_run
    )


def create_schema(client: CAAClient, dry_run: bool = False) -> None:
    """Orchestrate creation of the error log table.

    This function is idempotent — safe to re-run against an existing
    environment.
    """
    print("=" * 60)
    print("ITE Error Log Dataverse Schema Deployment")
    print("=" * 60)

    if dry_run:
        print("\n*** DRY-RUN MODE — no changes will be made ***\n")

    print("\n[1/1] Creating Inactivity Timeout Error Log table ...")
    create_errorlog_table(client, dry_run)

    print("\n" + "=" * 60)
    print("Schema deployment complete")
    print("=" * 60)


# =========================================================================
# CLI entry point
# =========================================================================


def main() -> None:
    """CLI entry point for schema deployment."""
    parser = argparse.ArgumentParser(
        description="Deploy ITE error log Dataverse schema (1 table)"
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

# =========================================================================
# Post-deployment steps
# =========================================================================
# 1. Security roles: Remove Delete privilege from
#    fsi_InactivityTimeoutErrorLog table (append-only).
#
# 2. Recommended index: Create a composite index on
#    (fsi_environmentid, fsi_timestamp) via Dataverse admin UI.
#    The Web API does not support programmatic index creation.
#
# 3. Seed data: Populate fsi_environmentpolicy rows with
#    tenant-specific EnvironmentNames.  Example:
#
#    EXAMPLE_POLICIES = [
#        {
#            "fsi_environmentid": "<EnvironmentName>",
#            "fsi_environmentdisplayname": "Production",
#            "fsi_zone": 2,          # Zone 2
#            "fsi_requiredmaxduration": 120,
#            "fsi_notes": "Zone 2 — max 120 min",
#        },
#        {
#            "fsi_environmentid": "<EnvironmentName>",
#            "fsi_environmentdisplayname": "Finance Prod",
#            "fsi_zone": 3,          # Zone 3
#            "fsi_requiredmaxduration": 60,
#            "fsi_notes": "Zone 3 — max 60 min",
#        },
#    ]
# =========================================================================
