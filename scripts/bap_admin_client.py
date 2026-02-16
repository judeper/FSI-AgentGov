"""BAPAdminClient — Business Application Platform Admin API client.

Provides authenticated access to the BAP Admin API for enumerating Power
Platform environments, Copilot Studio agents (bots), and agent sharing
permissions.  Supports both interactive (delegated) and service-principal
(client-credentials) authentication flows through MSAL.

Environment variables
---------------------
BAP_TENANT_ID        Entra ID tenant GUID
BAP_CLIENT_ID        App registration client ID
BAP_CLIENT_SECRET    App registration client secret (omit for interactive)

Example usage
-------------
::

    from bap_admin_client import BAPAdminClient

    # Service principal auth
    client = BAPAdminClient(
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        client_secret="your-client-secret"
    )

    # Interactive auth (device code flow)
    client = BAPAdminClient(
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        interactive=True
    )

    # Test connection
    if client.test_connection():
        # Enumerate environments
        environments = client.list_environments()
        for env in environments:
            print(f"Environment: {env['name']}")
            
            # Get agents in environment
            agents = client.list_agents(env['name'])
            for agent in agents:
                # Get agent permissions
                permissions = client.get_agent_permissions(
                    env['name'], 
                    agent['name']
                )
                print(f"  Agent: {agent['properties']['displayName']}")
                print(f"    Shared with {len(permissions)} principal(s)")
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import msal
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BAP_ADMIN_BASE_URL = "https://api.bap.microsoft.com"
BAP_ADMIN_SCOPE = "https://api.bap.microsoft.com/.default"

# Retry strategy: 3 retries with exponential back-off on throttle / server errors
_RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "PATCH"],  # Read and write operations
    raise_on_status=False,
)


class BAPAdminClient:
    """Business Application Platform Admin API client.

    Parameters
    ----------
    tenant_id : str | None
        Entra ID tenant GUID.  Falls back to ``BAP_TENANT_ID``.
    client_id : str | None
        App registration client ID.  Falls back to ``BAP_CLIENT_ID``.
    client_secret : str | None
        App registration client secret.  Falls back to ``BAP_CLIENT_SECRET``.
        If not provided, interactive auth is required.
    interactive : bool
        If *True*, use interactive (delegated) auth when no secret is
        available.
    """

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        interactive: bool = False,
    ) -> None:
        self.tenant_id = tenant_id or os.environ.get("BAP_TENANT_ID", "")
        self.client_id = client_id or os.environ.get("BAP_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("BAP_CLIENT_SECRET")
        self.interactive = interactive

        if not self.tenant_id:
            raise ValueError(
                "tenant_id is required (set BAP_TENANT_ID or pass explicitly)"
            )
        if not self.client_id:
            raise ValueError(
                "client_id is required (set BAP_CLIENT_ID or pass explicitly)"
            )

        self.base_url = BAP_ADMIN_BASE_URL
        self._scope = [BAP_ADMIN_SCOPE]
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

        logger.info("BAPAdminClient initialised (tenant=%s)", self.tenant_id)

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
        """Build HTTP headers with bearer token."""
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Core API methods
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Validate connectivity to the BAP Admin API.

        Returns
        -------
        bool
            *True* if the API responds successfully.
        """
        url = f"{self.base_url}/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments"
        params = {"api-version": "2016-11-01", "$top": "1"}
        
        try:
            resp = self._session.get(
                url, headers=self._get_headers(), params=params, timeout=30
            )
            resp.raise_for_status()
            logger.info("Connection test succeeded")
            return True
        except requests.RequestException as exc:
            logger.error("Connection test failed: %s", exc)
            return False

    def list_environments(self) -> List[Dict[str, Any]]:
        """List all Power Platform environments visible to the authenticated principal.

        Returns
        -------
        list[dict]
            Environment objects with structure::

                [
                    {
                        "id": "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/...",
                        "type": "Microsoft.BusinessAppPlatform/scopes/environments",
                        "location": "unitedstates",
                        "name": "environment-guid",
                        "properties": {
                            "displayName": "Production - Finance",
                            "environmentSku": "Production",
                            "isDefault": false,
                            "azureRegionHint": "eastus",
                            ...
                        }
                    },
                    ...
                ]

        Notes
        -----
        Returns empty list on API failure (graceful degradation).
        """
        url = f"{self.base_url}/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments"
        params = {"api-version": "2016-11-01"}

        try:
            headers = self._get_headers()
            all_environments: List[Dict[str, Any]] = []
            next_url: Optional[str] = None
            first_page = True
            while first_page or next_url:
                first_page = False
                if next_url:
                    resp = self._session.get(
                        next_url, headers=headers, timeout=60
                    )
                else:
                    resp = self._session.get(
                        url, headers=headers, params=params, timeout=60
                    )
                resp.raise_for_status()
                data = resp.json()
                all_environments.extend(data.get("value", []))
                next_url = data.get("@odata.nextLink")
            logger.info("Retrieved %d environment(s)", len(all_environments))
            return all_environments
        except requests.RequestException as exc:
            logger.error("Failed to list environments: %s", exc)
            return []

    def list_agents(self, environment_id: str) -> List[Dict[str, Any]]:
        """List Copilot Studio agents (bots) in the specified environment.

        Parameters
        ----------
        environment_id : str
            Environment GUID (from the ``name`` field of ``list_environments()``).

        Returns
        -------
        list[dict]
            Agent (bot) objects with structure::

                [
                    {
                        "name": "bot-guid",
                        "id": "/providers/.../environments/.../bots/bot-guid",
                        "type": "Microsoft.BusinessAppPlatform/scopes/environments/bots",
                        "properties": {
                            "displayName": "HR Assistant",
                            "description": "...",
                            "isCustomizable": true,
                            ...
                        }
                    },
                    ...
                ]

        Notes
        -----
        Returns empty list on API failure (graceful degradation per environment).
        """
        url = (
            f"{self.base_url}/providers/Microsoft.BusinessAppPlatform/"
            f"scopes/admin/environments/{environment_id}/bots"
        )
        params = {"api-version": "2021-04-01"}

        try:
            headers = self._get_headers()
            all_agents: List[Dict[str, Any]] = []
            next_url: Optional[str] = None
            first_page = True
            while first_page or next_url:
                first_page = False
                if next_url:
                    resp = self._session.get(
                        next_url, headers=headers, timeout=60
                    )
                else:
                    resp = self._session.get(
                        url, headers=headers, params=params, timeout=60
                    )
                resp.raise_for_status()
                data = resp.json()
                all_agents.extend(data.get("value", []))
                next_url = data.get("@odata.nextLink")
            logger.debug(
                "Retrieved %d agent(s) from environment %s", len(all_agents), environment_id
            )
            return all_agents
        except requests.RequestException as exc:
            logger.warning(
                "Failed to list agents for environment %s: %s", environment_id, exc
            )
            return []

    def get_agent_permissions(
        self, environment_id: str, agent_id: str
    ) -> List[Dict[str, Any]]:
        """Get sharing permissions for a specific Copilot Studio agent.

        Parameters
        ----------
        environment_id : str
            Environment GUID.
        agent_id : str
            Agent (bot) GUID (from the ``name`` field of ``list_agents()``).

        Returns
        -------
        list[dict]
            Permission (principal) objects with structure::

                [
                    {
                        "type": "user",
                        "id": "user-guid",
                        "displayName": "John Doe",
                        "userPrincipalName": "john.doe@contoso.com",
                    },
                    {
                        "type": "group",
                        "id": "group-guid",
                        "displayName": "Finance Team",
                    },
                    ...
                ]

        Notes
        -----
        Returns empty list on API failure (graceful degradation per agent).
        """
        url = (
            f"{self.base_url}/providers/Microsoft.BusinessAppPlatform/"
            f"scopes/admin/environments/{environment_id}/bots/{agent_id}/permissions"
        )
        params = {"api-version": "2021-04-01"}

        try:
            resp = self._session.get(
                url, headers=self._get_headers(), params=params, timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            permissions = data.get("value", [])
            logger.debug(
                "Retrieved %d permission(s) for agent %s", len(permissions), agent_id
            )
            return permissions
        except requests.RequestException as exc:
            logger.warning(
                "Failed to get permissions for agent %s in environment %s: %s",
                agent_id,
                environment_id,
                exc,
            )
            return []

    def modify_agent_permissions(
        self, environment_id: str, agent_id: str, principals: List[Dict[str, Any]]
    ) -> bool:
        """Modify sharing permissions for a Copilot Studio agent.

        This method uses PATCH to **replace all** existing permissions with the
        provided principals list. This is a destructive operation — all existing
        permissions not in the principals list will be removed.

        Parameters
        ----------
        environment_id : str
            Environment GUID.
        agent_id : str
            Agent (bot) GUID.
        principals : list[dict]
            List of permission objects with structure::

                [
                    {
                        "properties": {
                            "roleName": "CanView",
                            "principal": {
                                "id": "group-guid",
                                "type": "Group",
                                "displayName": "Finance Team"
                            }
                        }
                    },
                    ...
                ]

        Returns
        -------
        bool
            True if PATCH succeeded (200/204), False if error occurred.

        Notes
        -----
        The BAP Admin API PATCH endpoint uses a ``{"put": [...]}`` body structure
        that replaces all existing permissions. No incremental add/delete operations.

        Retries on 429 (rate limit) and 500+ (server errors) per _RETRY_STRATEGY.

        All PATCH attempts are logged with agent_id, environment_id, HTTP status,
        and response body for audit trail.
        """
        url = (
            f"{self.base_url}/providers/Microsoft.BusinessAppPlatform/"
            f"scopes/admin/environments/{environment_id}/bots/{agent_id}/permissions"
        )
        params = {"api-version": "2021-04-01"}
        body = {"put": principals}

        logger.info(
            "Modifying permissions for agent %s in environment %s (%d principal(s))",
            agent_id,
            environment_id,
            len(principals),
        )

        try:
            resp = self._session.patch(
                url, headers=self._get_headers(), params=params, json=body, timeout=60
            )
            resp.raise_for_status()
            
            logger.info(
                "Successfully modified permissions for agent %s (HTTP %d)",
                agent_id,
                resp.status_code,
            )
            return True

        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response else "unknown"
            response_text = exc.response.text if exc.response else ""
            
            logger.error(
                "Failed to modify permissions for agent %s in environment %s: "
                "HTTP %s — %s",
                agent_id,
                environment_id,
                status,
                response_text[:500],  # Truncate response for logging
            )
            return False

        except requests.RequestException as exc:
            logger.error(
                "Request error modifying permissions for agent %s in environment %s: %s",
                agent_id,
                environment_id,
                exc,
            )
            return False
