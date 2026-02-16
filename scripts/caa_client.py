"""CAAClient — Dataverse Web API client for Conditional Access Automation.

Provides authenticated access to Microsoft Dataverse via the Web API,
supporting both interactive (delegated) and service-principal (client-
credentials) authentication flows through MSAL.

Environment variables
---------------------
CAA_TENANT_ID        Entra ID tenant GUID
CAA_ENVIRONMENT_URL  Dataverse environment URL (e.g. https://org.crm.dynamics.com)
CAA_CLIENT_ID        App registration client ID
CAA_CLIENT_SECRET    App registration client secret (omit for interactive)
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from typing import Any, Dict, List, Optional

import msal
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATAVERSE_API_VERSION = "v9.2"
DATAVERSE_SCOPE_SUFFIX = "/.default"

# Retry strategy: 3 retries with exponential back-off on throttle / server errors
_RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST", "PATCH", "DELETE"],
    raise_on_status=False,
)


class CAAClient:
    """Dataverse Web API client for Conditional Access Automation.

    Parameters
    ----------
    tenant_id : str | None
        Entra ID tenant GUID.  Falls back to ``CAA_TENANT_ID``.
    environment_url : str | None
        Dataverse environment URL.  Falls back to ``CAA_ENVIRONMENT_URL``.
    client_id : str | None
        App registration client ID.  Falls back to ``CAA_CLIENT_ID``.
    client_secret : str | None
        App registration client secret.  Falls back to ``CAA_CLIENT_SECRET``.
    interactive : bool
        If *True*, use interactive (delegated) auth when no secret is
        available.
    dry_run : bool
        If *True*, all mutating operations (POST / PATCH / DELETE) print
        what *would* happen and return early without making API calls.
    """

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        environment_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        interactive: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.tenant_id = tenant_id or os.environ.get("CAA_TENANT_ID", "")
        self.environment_url = (
            environment_url or os.environ.get("CAA_ENVIRONMENT_URL", "")
        ).rstrip("/")
        self.client_id = client_id or os.environ.get("CAA_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("CAA_CLIENT_SECRET")
        self.interactive = interactive
        self.dry_run = dry_run

        if not self.tenant_id:
            raise ValueError(
                "tenant_id is required (set CAA_TENANT_ID or pass explicitly)"
            )
        if not self.environment_url:
            raise ValueError(
                "environment_url is required (set CAA_ENVIRONMENT_URL or pass explicitly)"
            )
        if not self.client_id:
            raise ValueError(
                "client_id is required (set CAA_CLIENT_ID or pass explicitly)"
            )

        self.api_url = f"{self.environment_url}/api/data/{DATAVERSE_API_VERSION}"
        self._scope = [f"{self.environment_url}{DATAVERSE_SCOPE_SUFFIX}"]
        self._token_cache = msal.SerializableTokenCache()

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        if self.client_secret:
            self._app: msal.ClientApplication = (
                msal.ConfidentialClientApplication(
                    self.client_id,
                    authority=authority,
                    client_credential=self.client_secret,
                    token_cache=self._token_cache,
                )
            )
        else:
            self._app = msal.PublicClientApplication(
                self.client_id,
                authority=authority,
                token_cache=self._token_cache,
            )

        # Requests session with retry strategy
        self._session = requests.Session()
        adapter = HTTPAdapter(max_retries=_RETRY_STRATEGY)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

        logger.info(
            "CAAClient initialised (env=%s, dry_run=%s)", self.environment_url, self.dry_run
        )

    # ------------------------------------------------------------------
    # Authentication helpers
    # ------------------------------------------------------------------

    def _get_token(self) -> str:
        """Acquire an access token via MSAL (silent cache → fallback).

        Returns
        -------
        str
            Bearer access token.
        """
        # 1. Try silent token from cache
        if self.client_secret:
            result = self._app.acquire_token_silent(self._scope, account=None)
            if result and "access_token" in result:
                return result["access_token"]
            # 2a. Client-credentials flow
            result = self._app.acquire_token_for_client(scopes=self._scope)
        else:
            accounts = self._app.get_accounts()
            if accounts:
                result = self._app.acquire_token_silent(self._scope, account=accounts[0])
                if result and "access_token" in result:
                    return result["access_token"]
            if not self.interactive:
                raise RuntimeError(
                    "No client_secret and interactive=False — cannot acquire token"
                )
            # 2b. Interactive / device-code flow
            result = self._app.acquire_token_interactive(scopes=self._scope)

        if not result or "access_token" not in result:
            error_desc = result.get("error_description", "Unknown error") if result else "No result"
            raise RuntimeError(f"Failed to acquire token: {error_desc}")
        return result["access_token"]

    def _get_headers(self) -> Dict[str, str]:
        """Build HTTP headers with bearer token and OData preferences."""
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": 'odata.include-annotations="*"',
        }

    # ------------------------------------------------------------------
    # Core HTTP helpers
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Validate connectivity to the Dataverse environment.

        Returns
        -------
        bool
            *True* if the environment responds successfully.
        """
        url = f"{self.api_url}/organizations"
        try:
            resp = self._session.get(url, headers=self._get_headers(), timeout=30)
            resp.raise_for_status()
            logger.info("Connection test succeeded")
            return True
        except requests.RequestException as exc:
            logger.error("Connection test failed: %s", exc)
            return False

    def query(
        self,
        entity_set: str,
        *,
        select: Optional[List[str]] = None,
        filter: Optional[str] = None,  # noqa: A002 — OData keyword
        orderby: Optional[str] = None,
        top: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Execute an OData query against *entity_set*.

        Returns
        -------
        list[dict]
            The ``value`` array from the OData response.
        """
        url = f"{self.api_url}/{entity_set}"
        params: Dict[str, str] = {}
        if select:
            params["$select"] = ",".join(select)
        if filter:
            params["$filter"] = filter
        if orderby:
            params["$orderby"] = orderby
        if top is not None:
            params["$top"] = str(top)

        headers = self._get_headers()
        all_results: List[Dict[str, Any]] = []
        next_url: Optional[str] = None
        first_page = True
        while first_page or next_url:
            first_page = False
            if next_url:
                resp = self._session.get(next_url, headers=headers, timeout=60)
            else:
                resp = self._session.get(url, headers=headers, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            all_results.extend(data.get("value", []))
            next_url = data.get("@odata.nextLink")
        return all_results

    def create_record(self, entity_set: str, data: Dict[str, Any]) -> Optional[str]:
        """Create a record in *entity_set*.

        Returns
        -------
        str | None
            The record ID extracted from the ``OData-EntityId`` header, or
            *None* in dry-run mode.
        """
        if self.dry_run:
            print(f"[DRY-RUN] Would create record in {entity_set}")
            logger.info("[DRY-RUN] Would create record in %s", entity_set)
            return None

        url = f"{self.api_url}/{entity_set}"
        resp = self._session.post(
            url, headers=self._get_headers(), json=data, timeout=60
        )
        resp.raise_for_status()

        # Extract record ID from OData-EntityId header
        entity_id_header = resp.headers.get("OData-EntityId", "")
        match = re.search(r"\(([0-9a-fA-F-]+)\)", entity_id_header)
        record_id = match.group(1) if match else None
        logger.info("Created record in %s: %s", entity_set, record_id)
        return record_id

    def update_record(
        self, entity_set: str, record_id: str, data: Dict[str, Any]
    ) -> None:
        """Update an existing record via PATCH."""
        if self.dry_run:
            print(f"[DRY-RUN] Would update record {record_id} in {entity_set}")
            logger.info(
                "[DRY-RUN] Would update record %s in %s", record_id, entity_set
            )
            return

        url = f"{self.api_url}/{entity_set}({record_id})"
        resp = self._session.patch(
            url, headers=self._get_headers(), json=data, timeout=60
        )
        resp.raise_for_status()
        logger.info("Updated record %s in %s", record_id, entity_set)

    def execute_query(
        self, query: str
    ) -> List[Dict[str, Any]]:
        """Execute a raw OData query URL against the Dataverse API.

        Parameters
        ----------
        query
            Relative OData query string (e.g.
            ``fsi_approvedsecuritygrouppolicies?$filter=...``).

        Returns
        -------
        list[dict]
            The ``value`` array from the OData response, or an empty list.
        """
        url = f"{self.api_url}/{query}"
        resp = self._session.get(url, headers=self._get_headers(), timeout=60)
        resp.raise_for_status()
        return resp.json().get("value", [])

    def upsert_record(
        self,
        entity_set: str,
        alternate_key: str,
        data: Dict[str, Any],
    ) -> str:
        """Upsert (insert-or-update) a record using an alternate key.

        Parameters
        ----------
        entity_set
            Dataverse entity set name (e.g. ``fsi_agentsharingcompliances``).
        alternate_key
            OData alternate-key expression, e.g.
            ``fsi_agent_id='abc',fsi_environment_id='env1'``.
        data
            Record payload.

        Returns
        -------
        str
            ``'created'`` or ``'updated'`` indicating the operation performed.
        """
        if self.dry_run:
            print(f"[DRY-RUN] Would upsert record in {entity_set}({alternate_key})")
            logger.info(
                "[DRY-RUN] Would upsert record in %s(%s)",
                entity_set,
                alternate_key,
            )
            return "dry-run"

        url = f"{self.api_url}/{entity_set}({alternate_key})"
        headers = self._get_headers()
        headers["If-Match"] = "*"  # upsert semantics
        resp = self._session.patch(url, headers=headers, json=data, timeout=60)
        # 204 = updated, if header wasn't matched Dataverse creates
        resp.raise_for_status()
        action = "updated" if resp.status_code == 204 else "created"
        logger.info("Upsert %s in %s(%s)", action, entity_set, alternate_key)
        return action

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------

    def get_entity_metadata(self, logical_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity metadata by logical name.

        Returns
        -------
        dict | None
            Entity metadata dict, or *None* if the entity does not exist.
        """
        url = f"{self.api_url}/EntityDefinitions(LogicalName='{logical_name}')"
        resp = self._session.get(url, headers=self._get_headers(), timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def create_entity(self, definition: Dict[str, Any]) -> None:
        """Create an entity (table) from a metadata definition."""
        if self.dry_run:
            name = definition.get("SchemaName", definition.get("LogicalName", "unknown"))
            print(f"[DRY-RUN] Would create entity {name}")
            logger.info("[DRY-RUN] Would create entity %s", name)
            return

        url = f"{self.api_url}/EntityDefinitions"
        resp = self._session.post(
            url, headers=self._get_headers(), json=definition, timeout=60
        )
        resp.raise_for_status()
        logger.info(
            "Created entity %s",
            definition.get("SchemaName", definition.get("LogicalName")),
        )

    def create_attribute(
        self, entity_name: str, attribute: Dict[str, Any]
    ) -> None:
        """Create a column (attribute) on an existing entity."""
        if self.dry_run:
            attr_name = attribute.get("SchemaName", attribute.get("LogicalName", "unknown"))
            print(
                f"[DRY-RUN] Would create attribute {attr_name} on {entity_name}"
            )
            logger.info(
                "[DRY-RUN] Would create attribute %s on %s",
                attr_name,
                entity_name,
            )
            return

        url = (
            f"{self.api_url}/EntityDefinitions(LogicalName='{entity_name}')"
            f"/Attributes"
        )
        resp = self._session.post(
            url, headers=self._get_headers(), json=attribute, timeout=60
        )
        resp.raise_for_status()
        logger.info(
            "Created attribute %s on %s",
            attribute.get("SchemaName", attribute.get("LogicalName")),
            entity_name,
        )

    def get_attribute_metadata(
        self, entity_name: str, attribute_name: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve attribute metadata by entity and attribute logical name.

        Returns
        -------
        dict | None
            Attribute metadata dict, or *None* if it does not exist.
        """
        url = (
            f"{self.api_url}/EntityDefinitions(LogicalName='{entity_name}')"
            f"/Attributes(LogicalName='{attribute_name}')"
        )
        resp = self._session.get(url, headers=self._get_headers(), timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Global option set helpers
    # ------------------------------------------------------------------

    def create_global_optionset(self, definition: Dict[str, Any]) -> None:
        """Create a global option set definition."""
        if self.dry_run:
            name = definition.get("Name", "unknown")
            print(f"[DRY-RUN] Would create global option set {name}")
            logger.info("[DRY-RUN] Would create global option set %s", name)
            return

        url = f"{self.api_url}/GlobalOptionSetDefinitions"
        resp = self._session.post(
            url, headers=self._get_headers(), json=definition, timeout=60
        )
        resp.raise_for_status()
        logger.info("Created global option set %s", definition.get("Name"))

    def get_global_optionset(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a global option set by name.

        Returns
        -------
        dict | None
            Option set metadata, or *None* if it does not exist.
        """
        url = f"{self.api_url}/GlobalOptionSetDefinitions(Name='{name}')"
        resp = self._session.get(url, headers=self._get_headers(), timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # High-level idempotent helpers
    # ------------------------------------------------------------------

    def check_table_exists(self, logical_name: str) -> bool:
        """Check whether a table (entity) exists.

        Returns
        -------
        bool
            *True* if the entity exists in the environment.
        """
        return self.get_entity_metadata(logical_name) is not None

    def create_table(self, definition: Dict[str, Any]) -> bool:
        """Idempotent table creation — check existence first.

        Returns
        -------
        bool
            *True* if the table was created, *False* if it already existed.
        """
        logical_name = definition.get(
            "LogicalName",
            definition.get("SchemaName", "").lower(),
        )
        if self.check_table_exists(logical_name):
            logger.info("Table %s already exists — skipping", logical_name)
            print(f"Table {logical_name} already exists — skipping")
            return False

        self.create_entity(definition)
        return True

    def create_column(
        self, entity_name: str, column: Dict[str, Any]
    ) -> bool:
        """Idempotent column creation — check existence first.

        Returns
        -------
        bool
            *True* if the column was created, *False* if it already existed.
        """
        attr_logical = column.get(
            "LogicalName",
            column.get("SchemaName", "").lower(),
        )
        existing = self.get_attribute_metadata(entity_name, attr_logical)
        if existing is not None:
            logger.info(
                "Column %s on %s already exists — skipping",
                attr_logical,
                entity_name,
            )
            print(f"Column {attr_logical} on {entity_name} already exists — skipping")
            return False

        self.create_attribute(entity_name, column)
        return True
