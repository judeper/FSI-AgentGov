"""Deploy environment variables for Inactivity Timeout Enforcement.

Creates 3 environment variables with the ``fsi_ITE_*`` prefix in the
target Dataverse environment.  All operations are idempotent — re-running
against an environment that already contains the variables is safe.

Usage::

    python scripts/create_timeout_environment_variables.py --dry-run
    python scripts/create_timeout_environment_variables.py --verbose
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, Dict, List

from caa_client import CAAClient

logger = logging.getLogger(__name__)

# =========================================================================
# Environment variable definitions
# =========================================================================

ENVIRONMENT_VARIABLES: List[Dict[str, Any]] = [
    {
        "schema_name": "fsi_ITE_ConcurrencyLimit",
        "display_name": "ITE - Concurrency Limit",
        "type": 100000002,  # Whole Number
        "default_value": "5",
        "description": (
            "Max parallel environment evaluations"
        ),
    },
    {
        "schema_name": "fsi_ITE_NotificationRecipients",
        "display_name": "ITE - Notification Recipients",
        "type": 100000000,  # String
        "default_value": "",
        "description": (
            "Email addresses for compliance alerts"
        ),
    },
    {
        "schema_name": "fsi_ITE_ScanFrequencyHours",
        "display_name": "ITE - Scan Frequency (Hours)",
        "type": 100000002,  # Whole Number
        "default_value": "24",
        "description": (
            "Scan interval in hours"
        ),
    },
]


# =========================================================================
# Deployment functions
# =========================================================================


def create_environment_variable(
    client: CAAClient,
    var_def: Dict[str, Any],
    dry_run: bool = False,
) -> bool:
    """Create a single environment variable (idempotent).

    Returns
    -------
    bool
        *True* if the variable was created, *False* if it already existed.
    """
    schema_name = var_def["schema_name"]

    # Check existence by schema name
    existing = client.query(
        "environmentvariabledefinitions",
        filter=f"schemaname eq '{schema_name}'",
    )
    if existing:
        print(f"  {schema_name}: already exists, skipping")
        logger.info("Environment variable %s already exists — skipping", schema_name)
        return False

    # Build definition payload
    definition: Dict[str, Any] = {
        "SchemaName": schema_name,
        "DisplayName": schema_name,
        "EnvironmentVariableDisplayName": var_def["display_name"],
        "Description": var_def["description"],
        "Type": var_def["type"],
        "DefaultValue": var_def["default_value"],
    }

    if dry_run:
        default_display = var_def["default_value"] or "(empty)"
        print(
            f"  [DRY-RUN] Would create {schema_name} "
            f"(type={var_def['type']}, default={default_display})"
        )
        logger.info("[DRY-RUN] Would create environment variable %s", schema_name)
        return True

    print(f"  Creating {schema_name} ...")
    client.create_record("environmentvariabledefinitions", definition)
    print(f"  Created {schema_name}")
    logger.info("Created environment variable %s", schema_name)
    return True


def create_environment_variables(
    client: CAAClient,
    dry_run: bool = False,
) -> Dict[str, int]:
    """Create all 3 environment variables.

    Returns
    -------
    dict
        Counts: ``{"created": n, "skipped": n}``.
    """
    print("=" * 60)
    print("ITE Environment Variables Deployment")
    print("=" * 60)

    if dry_run:
        print("\n*** DRY-RUN MODE — no changes will be made ***\n")

    counts = {"created": 0, "skipped": 0}

    for var_def in ENVIRONMENT_VARIABLES:
        created = create_environment_variable(client, var_def, dry_run)
        if created:
            counts["created"] += 1
        else:
            counts["skipped"] += 1

    print(f"\nEnvironment variables — created: {counts['created']}, "
          f"skipped: {counts['skipped']}")
    return counts


# =========================================================================
# CLI entry point
# =========================================================================


def main() -> None:
    """CLI entry point for environment variable deployment."""
    parser = argparse.ArgumentParser(
        description="Deploy ITE environment variables (3 fsi_ITE_* definitions)"
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

        create_environment_variables(client, dry_run=args.dry_run)

    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Environment variable deployment failed")
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
