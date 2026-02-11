"""Deployment orchestrator for Conditional Access Automation infrastructure.

Sequences all Phase 2 deployment steps — Dataverse schema, environment
variables, and connection references — with selective execution modes
and post-deployment guidance.

Usage::

    python scripts/deploy.py --dry-run
    python scripts/deploy.py --tables-only
    python scripts/deploy.py --vars-only --dry-run
    python scripts/deploy.py --verbose
"""

from __future__ import annotations

import argparse
import logging
import sys

from caa_client import CAAClient
from create_dataverse_schema import create_schema
from create_environment_variables import create_environment_variables
from create_connection_references import create_connection_references

logger = logging.getLogger(__name__)

# =========================================================================
# Post-deployment guidance
# =========================================================================

POST_DEPLOYMENT_GUIDANCE = """
\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
 Post-Deployment Steps
\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

 1. SECURITY: Remove Write/Delete permissions on
    fsi_CAPolicyValidationHistory for non-system users
    (immutable audit trail)

 2. CONNECTIONS: Open Power Automate \u2192 Solutions \u2192
    Bind each connection reference to an authenticated connection:
    - fsi_cr_dataverse_conditionalaccessautomation
    - fsi_cr_office365_conditionalaccessautomation
    - fsi_cr_teams_conditionalaccessautomation
    - fsi_cr_graph_conditionalaccessautomation

 3. TEAMS: Configure fsi_CAA_TeamsGroupId and
    fsi_CAA_TeamsChannelId environment variables with
    your target Teams group/channel GUIDs

 4. VERIFY: Re-run with --dry-run to confirm all
    artifacts exist:
    python deploy.py --dry-run

\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
"""


def _run_deployment(args: argparse.Namespace) -> None:
    """Execute the deployment pipeline based on CLI arguments."""
    selective = args.tables_only or args.vars_only or args.refs_only
    run_tables = args.tables_only or not selective
    run_vars = args.vars_only or not selective
    run_refs = args.refs_only or not selective

    print("=" * 60)
    print("CAA Infrastructure Deployment Orchestrator")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY-RUN MODE — no changes will be made ***\n")

    # Step 1: Build client
    client = CAAClient(
        tenant_id=args.tenant_id,
        environment_url=args.environment_url,
        client_id=args.client_id,
        client_secret=args.client_secret,
        interactive=args.interactive,
        dry_run=args.dry_run,
    )

    # Step 2: Test connection (blocks deployment on failure)
    print("\n[Step 1/4] Testing connection ...")
    if args.dry_run:
        print("  [DRY-RUN] Skipping connection test")
    else:
        if not client.test_connection():
            print(
                "ERROR: Cannot connect to Dataverse environment. "
                "Deployment aborted.",
                file=sys.stderr,
            )
            sys.exit(1)
        print("  Connection OK")

    # Step 3: Deploy Dataverse schema
    if run_tables:
        print("\n[Step 2/4] Deploying Dataverse schema ...")
        create_schema(client, dry_run=args.dry_run)
    else:
        print("\n[Step 2/4] Dataverse schema — skipped (selective mode)")

    # Step 4: Deploy environment variables
    if run_vars:
        print("\n[Step 3/4] Deploying environment variables ...")
        create_environment_variables(client, dry_run=args.dry_run)
    else:
        print("\n[Step 3/4] Environment variables — skipped (selective mode)")

    # Step 5: Deploy connection references
    if run_refs:
        print("\n[Step 4/4] Deploying connection references ...")
        create_connection_references(client, dry_run=args.dry_run)
    else:
        print("\n[Step 4/4] Connection references — skipped (selective mode)")

    # Post-deployment guidance
    print(POST_DEPLOYMENT_GUIDANCE)


# =========================================================================
# CLI entry point
# =========================================================================


def main() -> None:
    """CLI entry point for CAA deployment orchestrator."""
    parser = argparse.ArgumentParser(
        description=(
            "Deploy CAA infrastructure — Dataverse schema, "
            "environment variables, and connection references"
        )
    )

    # Authentication arguments
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

    # Execution mode arguments
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview all changes without executing",
    )
    parser.add_argument(
        "--tables-only",
        action="store_true",
        help="Deploy only Dataverse schema (tables and option sets)",
    )
    parser.add_argument(
        "--vars-only",
        action="store_true",
        help="Deploy only environment variables",
    )
    parser.add_argument(
        "--refs-only",
        action="store_true",
        help="Deploy only connection references",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        _run_deployment(args)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:
        logger.exception("Deployment failed")
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
