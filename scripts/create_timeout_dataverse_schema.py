"""Create the Dataverse schema for Inactivity Timeout Enforcement.

Tables
------
1. fsi_EnvironmentPolicy              — Per-environment timeout policy settings
2. fsi_InactivityTimeoutCompliance    — Immutable compliance scan records

Solution option sets (``fsi_ITE_compliancestatus``, ``fsi_ITE_environmenttype``)
are created by this script.  The ``fsi_acv_zone`` option set is a prerequisite
created by the CAA schema script — it is referenced but NOT created here.

Usage::

    python scripts/create_timeout_dataverse_schema.py --dry-run
    python scripts/create_timeout_dataverse_schema.py --verbose
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, Dict, List

from caa_client import CAAClient

logger = logging.getLogger(__name__)

# =========================================================================
# Prerequisite note
# =========================================================================
# The global option set ``fsi_acv_zone`` is created by create_dataverse_schema.py
# (CAA solution).  It is referenced by picklist columns in this script but is
# NOT re-created here.  Deploy the CAA schema first if ``fsi_acv_zone`` does
# not yet exist in the target environment.
# =========================================================================

# =========================================================================
# Solution option sets
# =========================================================================

SOLUTION_OPTIONSETS: Dict[str, Dict[str, Any]] = {
    "fsi_ITE_compliancestatus": {
        "Name": "fsi_ITE_compliancestatus",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "ITE Compliance Status", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {
                "Value": 0,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Compliant", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 1,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Non-Compliant", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 2,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Unknown", "LanguageCode": 1033}
                    ]
                },
            },
        ],
    },
    "fsi_ITE_environmenttype": {
        "Name": "fsi_ITE_environmenttype",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "ITE Environment Type", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {
                "Value": 0,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Default", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 1,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Sandbox", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 2,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Production", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 3,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Developer", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 4,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Trial", "LanguageCode": 1033}
                    ]
                },
            },
        ],
    },
}

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


def _integer_col(
    schema_name: str, display: str, *, required: bool = False
) -> Dict[str, Any]:
    """IntegerAttributeMetadata definition."""
    return {
        "@odata.type": "#Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
        "SchemaName": schema_name,
        "DisplayName": _label(display),
        "RequiredLevel": {"Value": "ApplicationRequired" if required else "None"},
        "MinValue": 0,
        "MaxValue": 2147483647,
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


def _environment_policy_table_definition() -> Dict[str, Any]:
    """fsi_EnvironmentPolicy table definition (OrganizationOwned)."""
    return {
        "SchemaName": "fsi_EnvironmentPolicy",
        "DisplayName": _label("Environment Policy"),
        "DisplayCollectionName": _label("Environment Policies"),
        "Description": _label(
            "Per-environment inactivity timeout policy settings"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_environmentpolicies",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_environmentid",
        "Attributes": [
            _string_col(
                "fsi_environmentid", "Environment ID",
                max_length=100, required=True,
            ),
        ],
    }


def _environment_policy_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_EnvironmentPolicy (added after table creation)."""
    return [
        _string_col(
            "fsi_environmentdisplayname", "Environment Display Name",
            max_length=200,
        ),
        # fsi_acv_zone is created by CAA schema — reference only, do not create
        _picklist_col("fsi_zone", "Zone", "fsi_acv_zone", required=True),
        _integer_col("fsi_requiredmaxduration", "Required Max Duration", required=True),
        _memo_col("fsi_notes", "Notes"),
    ]


def _compliance_table_definition() -> Dict[str, Any]:
    """fsi_InactivityTimeoutCompliance table definition (OrganizationOwned — immutable).

    Post-deployment: remove Write/Delete from security roles to enforce
    immutability.  Recommended index on ``(fsi_environmentid, fsi_lastscandate)``
    — create manually in Dataverse admin center.
    """
    return {
        "SchemaName": "fsi_InactivityTimeoutCompliance",
        "DisplayName": _label("Inactivity Timeout Compliance"),
        "DisplayCollectionName": _label("Inactivity Timeout Compliance Records"),
        "Description": _label(
            "Immutable compliance scan records for inactivity timeout enforcement"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_inactivitytimeoutcompliances",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_name",
        "Attributes": [
            _string_col(
                "fsi_name", "Name",
                max_length=200, required=True,
            ),
        ],
    }


def _compliance_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_InactivityTimeoutCompliance."""
    return [
        _string_col("fsi_environmentid", "Environment ID", max_length=100, required=True),
        _string_col("fsi_environmentname", "Environment Name", max_length=200),
        _picklist_col(
            "fsi_environmenttype", "Environment Type",
            "fsi_ITE_environmenttype",
        ),
        _boolean_col(
            "fsi_inactivitytimeoutenabled", "Inactivity Timeout Enabled",
            required=True,
        ),
        _integer_col("fsi_timeoutduration", "Timeout Duration"),
        _integer_col("fsi_requiredmaxduration", "Required Max Duration"),
        _picklist_col(
            "fsi_compliancestatus", "Compliance Status",
            "fsi_ITE_compliancestatus", required=True,
        ),
        _datetime_col("fsi_lastscandate", "Last Scan Date", required=True),
        _memo_col("fsi_notes", "Notes"),
    ]


# =========================================================================
# Schema creation functions
# =========================================================================


def create_solution_optionsets(client: CAAClient, dry_run: bool = False) -> None:
    """Create ITE solution option sets (idempotent)."""
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


def create_environment_policy_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_EnvironmentPolicy table and columns."""
    print("\n--- fsi_EnvironmentPolicy ---")
    _create_table_with_columns(
        client,
        _environment_policy_table_definition(),
        _environment_policy_columns(),
        dry_run,
    )


def create_compliance_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_InactivityTimeoutCompliance table and columns."""
    print("\n--- fsi_InactivityTimeoutCompliance ---")
    _create_table_with_columns(
        client,
        _compliance_table_definition(),
        _compliance_columns(),
        dry_run,
    )


def create_schema(client: CAAClient, dry_run: bool = False) -> None:
    """Orchestrate creation of all option sets and tables.

    This function is idempotent — safe to re-run against an existing
    environment.
    """
    print("=" * 60)
    print("ITE Dataverse Schema Deployment")
    print("=" * 60)

    if dry_run:
        print("\n*** DRY-RUN MODE — no changes will be made ***\n")

    # 1. Solution-specific option sets (must precede table columns that reference them)
    print("\n[1/3] Creating solution-specific option sets ...")
    create_solution_optionsets(client, dry_run)

    # 2. Environment Policy table
    print("\n[2/3] Creating Environment Policy table ...")
    create_environment_policy_table(client, dry_run)

    # 3. Inactivity Timeout Compliance table
    print("\n[3/3] Creating Inactivity Timeout Compliance table ...")
    create_compliance_table(client, dry_run)

    print("\n" + "=" * 60)
    print("Schema deployment complete")
    print("=" * 60)


# =========================================================================
# CLI entry point
# =========================================================================


def main() -> None:
    """CLI entry point for schema deployment."""
    parser = argparse.ArgumentParser(
        description="Deploy ITE Dataverse schema (2 tables + 2 solution option sets)"
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
