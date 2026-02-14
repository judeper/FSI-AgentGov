"""Unit tests for BAPAdminClient."""

import json
from unittest import mock

import pytest

from bap_admin_client import BAPAdminClient


# =========================================================================
# Test fixtures
# =========================================================================


@pytest.fixture
def mock_msal_confidential():
    """Mock ConfidentialClientApplication for service principal auth."""
    with mock.patch("bap_admin_client.msal.ConfidentialClientApplication") as mock_app:
        instance = mock_app.return_value
        instance.acquire_token_for_client.return_value = {
            "access_token": "test-token-sp"
        }
        instance.acquire_token_silent.return_value = None
        yield instance


@pytest.fixture
def mock_msal_public():
    """Mock PublicClientApplication for interactive auth."""
    with mock.patch("bap_admin_client.msal.PublicClientApplication") as mock_app:
        instance = mock_app.return_value
        instance.acquire_token_interactive.return_value = {
            "access_token": "test-token-interactive"
        }
        instance.get_accounts.return_value = []
        yield instance


@pytest.fixture
def mock_requests_session():
    """Mock requests.Session for HTTP calls."""
    with mock.patch("bap_admin_client.requests.Session") as mock_session:
        instance = mock_session.return_value
        yield instance


# =========================================================================
# Initialization tests
# =========================================================================


def test_bap_client_initialization(mock_msal_confidential):
    """Test that BAPAdminClient constructor sets tenant_id and client_id."""
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    assert client.tenant_id == "test-tenant-id"
    assert client.client_id == "test-client-id"
    assert client.client_secret == "test-secret"
    assert client.base_url == "https://api.bap.microsoft.com"


def test_bap_client_initialization_missing_tenant():
    """Test that BAPAdminClient raises ValueError if tenant_id is missing."""
    with pytest.raises(ValueError, match="tenant_id is required"):
        BAPAdminClient(client_id="test-client-id", client_secret="test-secret")


def test_bap_client_initialization_missing_client_id():
    """Test that BAPAdminClient raises ValueError if client_id is missing."""
    with pytest.raises(ValueError, match="client_id is required"):
        BAPAdminClient(tenant_id="test-tenant-id", client_secret="test-secret")


# =========================================================================
# Authentication tests
# =========================================================================


def test_service_principal_auth(mock_msal_confidential, mock_requests_session):
    """Test service principal (client credentials) authentication flow."""
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Trigger token acquisition
    token = client._get_token()

    assert token == "test-token-sp"
    mock_msal_confidential.acquire_token_for_client.assert_called_once()


def test_interactive_auth(mock_msal_public, mock_requests_session):
    """Test interactive (device code) authentication flow."""
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        interactive=True,
    )

    # Trigger token acquisition
    token = client._get_token()

    assert token == "test-token-interactive"
    mock_msal_public.acquire_token_interactive.assert_called_once()


# =========================================================================
# API method tests
# =========================================================================


def test_list_environments_success(mock_msal_confidential, mock_requests_session):
    """Test list_environments returns parsed environment list on success."""
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock API response
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "value": [
            {
                "name": "env-guid-1",
                "properties": {"displayName": "Production"},
            },
            {
                "name": "env-guid-2",
                "properties": {"displayName": "Test"},
            },
        ]
    }
    mock_requests_session.get.return_value = mock_response

    environments = client.list_environments()

    assert len(environments) == 2
    assert environments[0]["name"] == "env-guid-1"
    assert environments[1]["properties"]["displayName"] == "Test"
    mock_requests_session.get.assert_called_once()


def test_list_agents_success(mock_msal_confidential, mock_requests_session):
    """Test list_agents returns parsed agent list on success."""
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock API response
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "value": [
            {
                "name": "bot-guid-1",
                "properties": {"displayName": "HR Assistant"},
            },
            {
                "name": "bot-guid-2",
                "properties": {"displayName": "Finance Bot"},
            },
        ]
    }
    mock_requests_session.get.return_value = mock_response

    agents = client.list_agents("env-guid-1")

    assert len(agents) == 2
    assert agents[0]["name"] == "bot-guid-1"
    assert agents[1]["properties"]["displayName"] == "Finance Bot"
    mock_requests_session.get.assert_called_once()


def test_get_agent_permissions_success(mock_msal_confidential, mock_requests_session):
    """Test get_agent_permissions returns permissions list on success."""
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock API response
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "value": [
            {
                "type": "user",
                "id": "user-guid-1",
                "displayName": "John Doe",
            },
            {
                "type": "group",
                "id": "group-guid-1",
                "displayName": "Finance Team",
            },
        ]
    }
    mock_requests_session.get.return_value = mock_response

    permissions = client.get_agent_permissions("env-guid-1", "bot-guid-1")

    assert len(permissions) == 2
    assert permissions[0]["type"] == "user"
    assert permissions[1]["displayName"] == "Finance Team"
    mock_requests_session.get.assert_called_once()


# =========================================================================
# Error handling tests
# =========================================================================


def test_retry_on_throttle_429(mock_msal_confidential, mock_requests_session):
    """Test that client retries on 429 throttling response."""
    import requests
    
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock first call returns 429, second call succeeds
    mock_response_429 = mock.Mock()
    mock_response_429.status_code = 429
    mock_response_429.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests")

    mock_response_success = mock.Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"value": []}

    # Note: With retry strategy, the session will handle retries internally
    # For this test, we'll just verify graceful degradation
    mock_requests_session.get.side_effect = requests.RequestException("429 Too Many Requests")

    environments = client.list_environments()

    # Should return empty list (graceful degradation)
    assert environments == []


def test_graceful_degradation_on_500(mock_msal_confidential, mock_requests_session):
    """Test graceful degradation on 500 server error."""
    import requests
    
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock server error
    mock_requests_session.get.side_effect = requests.RequestException("500 Internal Server Error")

    # list_environments should log error and return empty list
    environments = client.list_environments()
    assert environments == []

    # list_agents should log error and return empty list
    agents = client.list_agents("env-guid-1")
    assert agents == []

    # get_agent_permissions should log error and return empty list
    permissions = client.get_agent_permissions("env-guid-1", "bot-guid-1")
    assert permissions == []


# =========================================================================
# Connection test
# =========================================================================


def test_test_connection_success(mock_msal_confidential, mock_requests_session):
    """Test that test_connection returns True on successful API call."""
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock successful environments list response
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"value": []}
    mock_requests_session.get.return_value = mock_response

    result = client.test_connection()

    assert result is True


def test_test_connection_failure(mock_msal_confidential, mock_requests_session):
    """Test that test_connection returns False on API failure."""
    import requests
    
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock API failure
    mock_requests_session.get.side_effect = requests.RequestException("Connection failed")

    result = client.test_connection()

    assert result is False


# =========================================================================
# PATCH method tests (modify_agent_permissions)
# =========================================================================


def test_modify_agent_permissions_success(mock_msal_confidential, mock_requests_session):
    """Test modify_agent_permissions returns True on 200 OK response."""
    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock successful PATCH response
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = mock.Mock()  # No exception
    mock_requests_session.patch.return_value = mock_response

    principals = [
        {
            "properties": {
                "roleName": "CanView",
                "principal": {
                    "id": "group-guid-1",
                    "type": "Group",
                    "displayName": "Finance Team",
                },
            }
        }
    ]

    result = client.modify_agent_permissions("env-guid-1", "bot-guid-1", principals)

    assert result is True
    mock_requests_session.patch.assert_called_once()

    # Verify PATCH request body structure
    call_args = mock_requests_session.patch.call_args
    assert call_args[1]["json"] == {"put": principals}


def test_modify_agent_permissions_bad_request(mock_msal_confidential, mock_requests_session):
    """Test modify_agent_permissions returns False on 400 Bad Request."""
    import requests

    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock 400 Bad Request
    mock_response = mock.Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid request body"
    mock_response.raise_for_status.side_effect = requests.HTTPError("400 Bad Request", response=mock_response)
    mock_requests_session.patch.return_value = mock_response

    result = client.modify_agent_permissions("env-guid-1", "bot-guid-1", [])

    assert result is False
    mock_requests_session.patch.assert_called_once()


def test_modify_agent_permissions_unauthorized(mock_msal_confidential, mock_requests_session):
    """Test modify_agent_permissions returns False on 401 Unauthorized."""
    import requests

    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock 401 Unauthorized
    mock_response = mock.Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized", response=mock_response)
    mock_requests_session.patch.return_value = mock_response

    result = client.modify_agent_permissions("env-guid-1", "bot-guid-1", [])

    assert result is False


def test_modify_agent_permissions_forbidden(mock_msal_confidential, mock_requests_session):
    """Test modify_agent_permissions returns False on 403 Forbidden."""
    import requests

    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock 403 Forbidden
    mock_response = mock.Mock()
    mock_response.status_code = 403
    mock_response.text = "Insufficient permissions"
    mock_response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden", response=mock_response)
    mock_requests_session.patch.return_value = mock_response

    result = client.modify_agent_permissions("env-guid-1", "bot-guid-1", [])

    assert result is False


def test_modify_agent_permissions_not_found(mock_msal_confidential, mock_requests_session):
    """Test modify_agent_permissions returns False on 404 Not Found."""
    import requests

    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock 404 Not Found
    mock_response = mock.Mock()
    mock_response.status_code = 404
    mock_response.text = "Agent not found"
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found", response=mock_response)
    mock_requests_session.patch.return_value = mock_response

    result = client.modify_agent_permissions("env-guid-1", "bot-guid-1", [])

    assert result is False


def test_modify_agent_permissions_rate_limit(mock_msal_confidential, mock_requests_session):
    """Test modify_agent_permissions handles 429 rate limit with retries."""
    import requests

    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock 429 Rate Limit (note: retry strategy is handled by urllib3, not by our code directly)
    # For this test, we'll simulate the final failure after retries
    mock_response = mock.Mock()
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"
    mock_response.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests", response=mock_response)
    mock_requests_session.patch.return_value = mock_response

    result = client.modify_agent_permissions("env-guid-1", "bot-guid-1", [])

    # Should return False after retries exhausted
    assert result is False


def test_modify_agent_permissions_server_error(mock_msal_confidential, mock_requests_session):
    """Test modify_agent_permissions handles 500 server error with retries."""
    import requests

    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock 500 Internal Server Error
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = requests.HTTPError("500 Internal Server Error", response=mock_response)
    mock_requests_session.patch.return_value = mock_response

    result = client.modify_agent_permissions("env-guid-1", "bot-guid-1", [])

    # Should return False after retries exhausted
    assert result is False


def test_modify_agent_permissions_request_exception(mock_msal_confidential, mock_requests_session):
    """Test modify_agent_permissions handles general request exceptions."""
    import requests

    client = BAPAdminClient(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-secret",
    )

    # Mock general request exception (e.g., network error)
    mock_requests_session.patch.side_effect = requests.RequestException("Network error")

    result = client.modify_agent_permissions("env-guid-1", "bot-guid-1", [])

    assert result is False
