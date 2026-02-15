"""Create the five-table Dataverse schema for Unrestricted Agent Sharing Detector.

Tables
------
1. fsi_AgentSharingSetting       — Current agent sharing configuration state
2. fsi_SharingViolation          — Sharing violation audit trail
3. fsi_SharingException          — Exception requests and approvals
4. fsi_ApprovedSecurityGroup     — Admin-managed approved security groups
5. fsi_SharingPolicy             — Sharing policy thresholds and configuration

Six solution-specific global option sets (``fsi_UASD_*``) are created by
this script.  The shared option sets ``fsi_acv_zone`` and
``fsi_acv_severity`` are referenced but **not** created here — they are
provisioned by the CAA schema script (``create_dataverse_schema.py``).

Usage::

    python scripts/create_uasd_dataverse_schema.py --dry-run
    python scripts/create_uasd_dataverse_schema.py --verbose
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
# (create_dataverse_schema.py).  UASD tables bind picklist columns to these
# shared option sets but do not recreate them.

# =========================================================================
# Solution-specific option sets (UASD)
# =========================================================================

SOLUTION_OPTIONSETS: Dict[str, Dict[str, Any]] = {
    "fsi_UASD_sharingscope": {
        "Name": "fsi_UASD_sharingscope",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "UASD Sharing Scope", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {
                "Value": 0,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Individual", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 1,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "SecurityGroup", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 2,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Organization", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 3,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Public", "LanguageCode": 1033}
                    ]
                },
            },
        ],
    },
    "fsi_UASD_violationtype": {
        "Name": "fsi_UASD_violationtype",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "UASD Violation Type", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {
                "Value": 0,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "ORG_WIDE_SHARING", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 1,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "PUBLIC_INTERNET_LINK", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 2,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "UNAPPROVED_GROUP", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 3,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "EXCESSIVE_INDIVIDUAL", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 4,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "CROSS_TENANT_ACCESS", "LanguageCode": 1033}
                    ]
                },
            },
        ],
    },
    "fsi_UASD_violationstatus": {
        "Name": "fsi_UASD_violationstatus",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "UASD Violation Status", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {
                "Value": 0,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Open", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 1,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Remediated", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 2,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Exception_Granted", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 3,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "False_Positive", "LanguageCode": 1033}
                    ]
                },
            },
        ],
    },
    "fsi_UASD_exceptionstatus": {
        "Name": "fsi_UASD_exceptionstatus",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "UASD Exception Status", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {
                "Value": 0,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Pending", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 1,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Approved", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 2,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Denied", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 3,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Expired", "LanguageCode": 1033}
                    ]
                },
            },
        ],
    },
    "fsi_UASD_authmode": {
        "Name": "fsi_UASD_authmode",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "UASD Auth Mode", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {
                "Value": 0,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "ManualAuthentication", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 1,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "NoAuthentication", "LanguageCode": 1033}
                    ]
                },
            },
        ],
    },
    "fsi_UASD_dataclassification": {
        "Name": "fsi_UASD_dataclassification",
        "DisplayName": {
            "LocalizedLabels": [
                {"Label": "UASD Data Classification", "LanguageCode": 1033}
            ]
        },
        "IsGlobal": True,
        "OptionSetType": "Picklist",
        "Options": [
            {
                "Value": 0,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Public", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 1,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Internal", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 2,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "Confidential", "LanguageCode": 1033}
                    ]
                },
            },
            {
                "Value": 3,
                "Label": {
                    "LocalizedLabels": [
                        {"Label": "HighlyConfidential", "LanguageCode": 1033}
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


def _agent_sharing_setting_table_definition() -> Dict[str, Any]:
    """fsi_AgentSharingSetting table definition (OrganizationOwned)."""
    return {
        "SchemaName": "fsi_AgentSharingSetting",
        "DisplayName": _label("Agent Sharing Setting"),
        "DisplayCollectionName": _label("Agent Sharing Settings"),
        "Description": _label(
            "Current agent sharing configuration state"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_agentsharingsettings",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_agent_name",
        "Attributes": [
            _string_col("fsi_agent_name", "Agent Name", max_length=200, required=True),
        ],
    }


def _agent_sharing_setting_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_AgentSharingSetting (added after table creation)."""
    return [
        _string_col("fsi_agent_id", "Agent ID", max_length=100, required=True),
        _string_col("fsi_environment_id", "Environment ID", max_length=100, required=True),
        _string_col("fsi_environment_name", "Environment Name", max_length=200),
        _picklist_col("fsi_sharing_scope", "Sharing Scope", "fsi_UASD_sharingscope", required=True),
        _integer_col("fsi_principal_count", "Principal Count"),
        _memo_col("fsi_principals_json", "Principals JSON"),
        _picklist_col("fsi_auth_mode", "Auth Mode", "fsi_UASD_authmode"),
        _datetime_col("fsi_last_scanned", "Last Scanned", required=True),
        _boolean_col("fsi_break_glass_exclude", "Break Glass Exclude", default=False),
    ]


def _sharing_violation_table_definition() -> Dict[str, Any]:
    """fsi_SharingViolation table definition (OrganizationOwned)."""
    return {
        "SchemaName": "fsi_SharingViolation",
        "DisplayName": _label("Sharing Violation"),
        "DisplayCollectionName": _label("Sharing Violations"),
        "Description": _label(
            "Sharing violation audit trail"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_sharingviolations",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_violationname",
        "Attributes": [
            _string_col("fsi_violationname", "Violation Name", max_length=256, required=True),
        ],
    }


def _sharing_violation_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_SharingViolation (added after table creation)."""
    return [
        _string_col("fsi_agentid", "Agent ID", max_length=100, required=True),
        _string_col("fsi_agentname", "Agent Name", max_length=200, required=True),
        _string_col("fsi_environmentid", "Environment ID", max_length=100, required=True),
        _string_col("fsi_environmentname", "Environment Name", max_length=200),
        _picklist_col("fsi_violationtype", "Violation Type", "fsi_UASD_violationtype", required=True),
        _picklist_col("fsi_violationstatus", "Violation Status", "fsi_UASD_violationstatus", required=True),
        _picklist_col("fsi_severity", "Severity", "fsi_acv_severity", required=True),
        _picklist_col("fsi_zone", "Zone", "fsi_acv_zone"),
        _memo_col("fsi_description", "Description"),
        _memo_col("fsi_evidencejson", "Evidence JSON"),
        _string_col("fsi_evidencehash", "Evidence Hash", max_length=64),
        _datetime_col("fsi_remediatedon", "Remediated On"),
        _string_col("fsi_remediatedby", "Remediated By", max_length=256),
        _datetime_col("fsi_detectedat", "Detected At", required=True),
        _string_col("fsi_scanrunid", "Scan Run ID", max_length=100),
        _integer_col("fsi_principalcount", "Principal Count"),
        _memo_col("fsi_principaldetail", "Principal Detail"),
    ]


def _sharing_exception_table_definition() -> Dict[str, Any]:
    """fsi_SharingException table definition (OrganizationOwned)."""
    return {
        "SchemaName": "fsi_SharingException",
        "DisplayName": _label("Sharing Exception"),
        "DisplayCollectionName": _label("Sharing Exceptions"),
        "Description": _label(
            "Exception requests and approvals"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_sharingexceptions",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_exceptionname",
        "Attributes": [
            _string_col("fsi_exceptionname", "Exception Name", max_length=256, required=True),
        ],
    }


def _sharing_exception_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_SharingException (added after table creation)."""
    return [
        _string_col("fsi_violationid", "Violation ID", max_length=100, required=True),
        _string_col("fsi_agentid", "Agent ID", max_length=100, required=True),
        _string_col("fsi_agentname", "Agent Name", max_length=200, required=True),
        _string_col("fsi_environmentid", "Environment ID", max_length=100, required=True),
        _picklist_col("fsi_exceptionstatus", "Exception Status", "fsi_UASD_exceptionstatus", required=True),
        _picklist_col("fsi_violationtype", "Violation Type", "fsi_UASD_violationtype", required=True),
        _memo_col("fsi_justification", "Business Justification", required=True),
        _picklist_col("fsi_dataclassification", "Data Classification", "fsi_UASD_dataclassification", required=True),
        _string_col("fsi_requestedby", "Requested By", max_length=256, required=True),
        _string_col("fsi_approvedby", "Approved By", max_length=256),
        _string_col("fsi_approvedbysecurity", "Approved By Security", max_length=256),
        _string_col("fsi_approvedbydataowner", "Approved By Data Owner", max_length=256),
        _datetime_col("fsi_requestedat", "Requested At", required=True),
        _datetime_col("fsi_approvedon", "Approved On"),
        _datetime_col("fsi_expireson", "Expires On", required=True),
    ]


def _approved_security_group_table_definition() -> Dict[str, Any]:
    """fsi_ApprovedSecurityGroup table definition (OrganizationOwned)."""
    return {
        "SchemaName": "fsi_ApprovedSecurityGroup",
        "DisplayName": _label("Approved Security Group"),
        "DisplayCollectionName": _label("Approved Security Groups"),
        "Description": _label(
            "Admin-managed approved security groups"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_approvedsecuritygroups",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_display_name",
        "Attributes": [
            _string_col("fsi_display_name", "Display Name", max_length=200, required=True),
        ],
    }


def _approved_security_group_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_ApprovedSecurityGroup (added after table creation)."""
    return [
        _string_col("fsi_entraid_group_id", "Entra ID Group ID", max_length=100, required=True),
        _picklist_col("fsi_zone", "Zone", "fsi_acv_zone", required=True),
        _boolean_col("fsi_is_active", "Is Active", default=True),
        _string_col("fsi_added_by", "Added By", max_length=256),
        _datetime_col("fsi_added_at", "Added At"),
    ]


def _sharing_policy_table_definition() -> Dict[str, Any]:
    """fsi_SharingPolicy table definition (OrganizationOwned)."""
    return {
        "SchemaName": "fsi_SharingPolicy",
        "DisplayName": _label("Sharing Policy"),
        "DisplayCollectionName": _label("Sharing Policies"),
        "Description": _label(
            "Sharing policy thresholds and configuration"
        ),
        "OwnershipType": "OrganizationOwned",
        "IsActivity": False,
        "EntitySetName": "fsi_sharingpolicies",
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_policy_name",
        "Attributes": [
            _string_col("fsi_policy_name", "Policy Name", max_length=200, required=True),
        ],
    }


def _sharing_policy_columns() -> List[Dict[str, Any]]:
    """Additional columns for fsi_SharingPolicy (added after table creation)."""
    return [
        _integer_col("fsi_max_individual_shares", "Max Individual Shares", required=True),
        _picklist_col("fsi_governance_zone", "Governance Zone", "fsi_acv_zone", required=True),
        _boolean_col("fsi_auto_remediate_public_link", "Auto Remediate Public Link", default=False),
        _boolean_col("fsi_is_active", "Is Active", default=True),
        _string_col("fsi_updated_by", "Updated By", max_length=256),
        _datetime_col("fsi_updated_at", "Updated At"),
    ]


# =========================================================================
# Schema creation functions
# =========================================================================


def create_solution_optionsets(client: CAAClient, dry_run: bool = False) -> None:
    """Create UASD solution-specific global option sets (idempotent)."""
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


def create_agent_sharing_setting_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_AgentSharingSetting table and columns."""
    print("\n--- fsi_AgentSharingSetting ---")
    _create_table_with_columns(
        client,
        _agent_sharing_setting_table_definition(),
        _agent_sharing_setting_columns(),
        dry_run,
    )


def create_sharing_violation_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_SharingViolation table and columns."""
    print("\n--- fsi_SharingViolation ---")
    _create_table_with_columns(
        client,
        _sharing_violation_table_definition(),
        _sharing_violation_columns(),
        dry_run,
    )


def create_sharing_exception_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_SharingException table and columns."""
    print("\n--- fsi_SharingException ---")
    _create_table_with_columns(
        client,
        _sharing_exception_table_definition(),
        _sharing_exception_columns(),
        dry_run,
    )


def create_approved_security_group_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_ApprovedSecurityGroup table and columns."""
    print("\n--- fsi_ApprovedSecurityGroup ---")
    _create_table_with_columns(
        client,
        _approved_security_group_table_definition(),
        _approved_security_group_columns(),
        dry_run,
    )


def create_sharing_policy_table(client: CAAClient, dry_run: bool = False) -> None:
    """Create the fsi_SharingPolicy table and columns."""
    print("\n--- fsi_SharingPolicy ---")
    _create_table_with_columns(
        client,
        _sharing_policy_table_definition(),
        _sharing_policy_columns(),
        dry_run,
    )


def seed_default_policy(client: CAAClient, dry_run: bool = False) -> None:
    """Insert default sharing policy row (idempotent)."""
    existing = client.query(
        "fsi_sharingpolicies",
        filter="fsi_policy_name eq 'Default Sharing Policy'",
    )
    if existing:
        print("  Default sharing policy already exists — skipping")
        return
    if dry_run:
        print("  [DRY-RUN] Would create default sharing policy row")
        return
    definition = {
        "fsi_policy_name": "Default Sharing Policy",
        "fsi_max_individual_shares": 100,
        "fsi_governance_zone": 0,  # Unclassified / All
        "fsi_auto_remediate_public_link": False,
        "fsi_is_active": True,
    }
    client.create_record("fsi_sharingpolicies", definition)
    print("  Created default sharing policy (MaxIndividualShares=100, Zone=All)")


def create_schema(client: CAAClient, dry_run: bool = False) -> None:
    """Orchestrate creation of all option sets, tables, and seed data.

    This function is idempotent — safe to re-run against an existing
    environment.  Shared option sets (fsi_acv_zone, fsi_acv_severity)
    are NOT created here; they must already exist from the CAA schema
    deployment.
    """
    print("=" * 60)
    print("UASD Dataverse Schema Deployment")
    print("=" * 60)

    if dry_run:
        print("\n*** DRY-RUN MODE — no changes will be made ***\n")

    # 1. Solution-specific option sets (fsi_UASD_*)
    #    NOTE: fsi_acv_zone and fsi_acv_severity are shared and created
    #    by the CAA schema script — not recreated here.
    print("\n[1/7] Creating UASD solution-specific option sets ...")
    create_solution_optionsets(client, dry_run)

    # 2. Agent Sharing Setting table
    print("\n[2/7] Creating Agent Sharing Setting table ...")
    create_agent_sharing_setting_table(client, dry_run)

    # 3. Sharing Violation table
    print("\n[3/7] Creating Sharing Violation table ...")
    create_sharing_violation_table(client, dry_run)

    # 4. Sharing Exception table
    print("\n[4/7] Creating Sharing Exception table ...")
    create_sharing_exception_table(client, dry_run)

    # 5. Approved Security Group table
    print("\n[5/7] Creating Approved Security Group table ...")
    create_approved_security_group_table(client, dry_run)

    # 6. Sharing Policy table
    print("\n[6/7] Creating Sharing Policy table ...")
    create_sharing_policy_table(client, dry_run)

    # 7. Seed default policy row
    print("\n[7/7] Seeding default sharing policy ...")
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
        description="Deploy UASD Dataverse schema (5 tables + 6 option sets + seed data)"
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
