"""Deploy connection references for Inactivity Timeout Enforcement.

Creates 2 connection references with the ``fsi_cr_*`` naming convention
in the target Dataverse environment.  All operations are idempotent —
re-running against an environment that already contains the references
is safe.

Usage::

    python scripts/create_timeout_connection_references.py --dry-run
    python scripts/create_timeout_connection_references.py --verbose
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, Dict, List

import requests

from caa_client import CAAClient

logger = logging.getLogger(__name__)

# =========================================================================
# Connection reference definitions
# =========================================================================

CONNECTION_REFERENCES: List[Dict[str, Any]] = [
    {
        "logical_name": "fsi_cr_dataverse_inactivitytimeout",
        "display_name": "Dataverse - Inactivity Timeout Enforcement",
        "connector_id": "shared_commondataserviceforapps",
        "description": (
            "Policy, compliance, and error-log table CRUD"
        ),
    },
    {
        "logical_name": "fsi_cr_powerplatformforadmins_inactivitytimeout",
        "display_name": "Power Platform for Admins - Inactivity Timeout Enforcement",
        "connector_id": "shared_powerplatformforadmins",
        "description": (
            "Environment enumeration for compliance scanning"
        ),
    },
]


# =========================================================================
# Deployment functions
# =========================================================================


def create_connection_reference(
    client: CAAClient,
    ref_def: Dict[str, Any],
    dry_run: bool = False,
) -> bool:
    """Create a single connection reference (idempotent).

    Returns
    -------
    bool
        *True* if the reference was created, *False* if it already existed.
    """
    logical_name = ref_def["logical_name"]

    # Check existence by logical name
    existing = client.query(
        "connectionreferences",
        filter=f"connectionreferencelogicalname eq '{logical_name}'",
    )
    if existing:
        print(f"  {logical_name}: already exists, skipping")
        logger.info(
            "Connection reference %s already exists — skipping", logical_name
        )
        return False

    # Build definition payload
    definition: Dict[str, Any] = {
        "connectionreferencelogicalname": logical_name,
        "connectionreferencedisplayname": ref_def["display_name"],
        "connectorid": ref_def["connector_id"],
        "description": ref_def["description"],
    }

    if dry_run:
        print(
            f"  [DRY-RUN] Would create {logical_name} "
            f"(connector={ref_def['connector_id']})"
        )
        logger.info(
            "[DRY-RUN] Would create connection reference %s", logical_name
        )
        return True

    print(f"  Creating {logical_name} ...")
    try:
        client.create_record("connectionreferences", definition)
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        if status in (400, 404):
            print(
                f"  ERROR: Failed to create {logical_name} (HTTP {status}).\n"
                f"         Connector ID '{ref_def['connector_id']}' may be invalid.\n"
                f"         Verify the connector ID in Power Automate → Connections."
            )
            logger.error(
                "Failed to create connection reference %s — HTTP %s. "
                "Connector ID '%s' may be invalid.",
                logical_name,
                status,
                ref_def["connector_id"],
            )
            raise
        raise

    print(f"  Created {logical_name}")
    logger.info("Created connection reference %s", logical_name)
    return True


def create_connection_references(
    client: CAAClient,
    dry_run: bool = False,
) -> Dict[str, int]:
    """Create all 2 connection references.

    Returns
    -------
    dict
        Counts: ``{"created": n, "skipped": n}``.
    """
    print("=" * 60)
    print("ITE Connection References Deployment")
    print("=" * 60)

    if dry_run:
        print("\n*** DRY-RUN MODE — no changes will be made ***\n")

    counts = {"created": 0, "skipped": 0}

    for ref_def in CONNECTION_REFERENCES:
        created = create_connection_reference(client, ref_def, dry_run)
        if created:
            counts["created"] += 1
        else:
            counts["skipped"] += 1

    print(f"\nConnection references — created: {counts['created']}, "
          f"skipped: {counts['skipped']}")
    return counts


# =========================================================================
# CLI entry point
# =========================================================================


def main() -> None:
    """CLI entry point for connection reference deployment."""
    parser = argparse.ArgumentParser(
        description="Deploy ITE connection references (2 fsi_cr_* definitions)"
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

        create_connection_references(client, dry_run=args.dry_run)

    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Connection reference deployment failed")
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
