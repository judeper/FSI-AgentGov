"""Unit tests for remediate_agent_sharing.py."""

from unittest import mock

import pytest
from remediate_agent_sharing import (
    build_permission_object,
    get_zone_remediation_principals,
    update_compliance_record,
    validate_remediation,
)

# =========================================================================
# Test fixtures
# =========================================================================


@pytest.fixture
def mock_dataverse_client():
    """Mock CAAClient for Dataverse operations."""
    client = mock.Mock()
    client.execute_query.return_value = {"value": []}
    client.upsert_record.return_value = True
    return client


@pytest.fixture
def mock_bap_client():
    """Mock BAPAdminClient for BAP API operations."""
    client = mock.Mock()
    client.get_agent_permissions.return_value = []
    client.modify_agent_permissions.return_value = True
    client.test_connection.return_value = True
    return client


# =========================================================================
# Helper function tests
# =========================================================================


def test_build_permission_object():
    """Test build_permission_object creates correct structure."""
    result = build_permission_object(
        group_id="group-guid-1",
        group_name="Finance Team",
        role_name="CanView",
    )

    assert result == {
        "properties": {
            "roleName": "CanView",
            "principal": {
                "id": "group-guid-1",
                "type": "Group",
                "displayName": "Finance Team",
            },
        }
    }


def test_build_permission_object_default_role():
    """Test build_permission_object uses default role CanView."""
    result = build_permission_object(
        group_id="group-guid-1",
        group_name="Finance Team",
    )

    assert result["properties"]["roleName"] == "CanView"


# =========================================================================
# Zone remediation logic tests
# =========================================================================


def test_zone_1_remediation_removes_all_groups(mock_dataverse_client):
    """Test Zone 1 remediation removes all group sharing, preserves users."""
    current_principals = [
        {"type": "user", "id": "user-1", "displayName": "John Doe"},
        {"type": "user", "id": "user-2", "displayName": "Jane Smith"},
        {"type": "group", "id": "group-1", "displayName": "Finance Team"},
        {"type": "group", "id": "group-2", "displayName": "IT Team"},
    ]

    result = get_zone_remediation_principals(
        zone=1,
        current_principals=current_principals,
        approved_groups=[],
        dataverse_client=mock_dataverse_client,
    )

    # Should preserve 2 users, remove 2 groups
    assert len(result) == 2
    assert all(
        p["properties"]["principal"]["type"] == "User" for p in result
    )
    assert result[0]["properties"]["principal"]["displayName"] == "John Doe"
    assert result[1]["properties"]["principal"]["displayName"] == "Jane Smith"


def test_zone_1_remediation_no_users_returns_empty(mock_dataverse_client):
    """Test Zone 1 remediation with no users returns empty list (logs warning)."""
    current_principals = [
        {"type": "group", "id": "group-1", "displayName": "Finance Team"},
        {"type": "group", "id": "group-2", "displayName": "IT Team"},
    ]

    result = get_zone_remediation_principals(
        zone=1,
        current_principals=current_principals,
        approved_groups=[],
        dataverse_client=mock_dataverse_client,
    )

    # Should return empty list (all groups removed, no users)
    assert len(result) == 0


def test_zone_2_remediation_removes_everyone_public(mock_dataverse_client):
    """Test Zone 2 remediation removes Everyone/Public, preserves named groups."""
    current_principals = [
        {"type": "group", "id": "everyone", "displayName": "Everyone"},
        {"type": "group", "id": "public", "displayName": "Public"},
        {"type": "group", "id": "group-1", "displayName": "Finance Team"},
        {"type": "user", "id": "user-1", "displayName": "John Doe"},
    ]

    result = get_zone_remediation_principals(
        zone=2,
        current_principals=current_principals,
        approved_groups=[],
        dataverse_client=mock_dataverse_client,
    )

    # Should preserve Finance Team group and John Doe user (2 principals)
    assert len(result) == 2
    
    # Check that Everyone and Public are removed
    display_names = [p["properties"]["principal"]["displayName"] for p in result]
    assert "Everyone" not in display_names
    assert "Public" not in display_names
    assert "Finance Team" in display_names
    assert "John Doe" in display_names


def test_zone_2_remediation_case_insensitive_everyone(mock_dataverse_client):
    """Test Zone 2 remediation handles case-insensitive Everyone/Public matching."""
    current_principals = [
        {"type": "group", "id": "group-1", "displayName": "EVERYONE"},
        {"type": "group", "id": "group-2", "displayName": "public users"},
        {"type": "group", "id": "group-3", "displayName": "Finance Team"},
    ]

    result = get_zone_remediation_principals(
        zone=2,
        current_principals=current_principals,
        approved_groups=[],
        dataverse_client=mock_dataverse_client,
    )

    # Should preserve only Finance Team (EVERYONE and "public users" removed)
    assert len(result) == 1
    assert result[0]["properties"]["principal"]["displayName"] == "Finance Team"


def test_zone_3_remediation_replaces_with_approved_groups(mock_dataverse_client):
    """Test Zone 3 remediation replaces all principals with approved groups."""
    current_principals = [
        {"type": "user", "id": "user-1", "displayName": "John Doe"},
        {"type": "group", "id": "group-1", "displayName": "Old Group"},
    ]

    approved_groups = ["approved-group-1", "approved-group-2"]

    # Mock group name lookup from policy table
    mock_dataverse_client.execute_query.side_effect = [
        {"value": [{"fsi_group_name": "Approved Finance Team"}]},
        {"value": [{"fsi_group_name": "Approved IT Team"}]},
    ]

    result = get_zone_remediation_principals(
        zone=3,
        current_principals=current_principals,
        approved_groups=approved_groups,
        dataverse_client=mock_dataverse_client,
    )

    # Should replace all with 2 approved groups
    assert len(result) == 2
    assert all(
        p["properties"]["principal"]["type"] == "Group" for p in result
    )
    assert result[0]["properties"]["principal"]["displayName"] == "Approved Finance Team"
    assert result[1]["properties"]["principal"]["displayName"] == "Approved IT Team"


def test_zone_3_remediation_no_approved_groups_raises_error(mock_dataverse_client):
    """Test Zone 3 remediation raises ValueError if no approved groups."""
    current_principals = [
        {"type": "user", "id": "user-1", "displayName": "John Doe"},
    ]

    with pytest.raises(ValueError, match="Zone 3 has no approved groups"):
        get_zone_remediation_principals(
            zone=3,
            current_principals=current_principals,
            approved_groups=[],  # Empty list
            dataverse_client=mock_dataverse_client,
        )


def test_zone_3_remediation_fallback_to_group_id_if_name_missing(mock_dataverse_client):
    """Test Zone 3 remediation uses group ID as fallback if name not found."""
    approved_groups = ["approved-group-1"]

    # Mock group name lookup returns empty result (name not found)
    mock_dataverse_client.execute_query.return_value = {"value": []}

    result = get_zone_remediation_principals(
        zone=3,
        current_principals=[],
        approved_groups=approved_groups,
        dataverse_client=mock_dataverse_client,
    )

    # Should use group ID as display name fallback
    assert len(result) == 1
    assert result[0]["properties"]["principal"]["displayName"] == "approved-group-1"


def test_unknown_zone_falls_back_to_zone_2(mock_dataverse_client):
    """Test unknown zone (0 or invalid) falls back to Zone 2 remediation."""
    current_principals = [
        {"type": "group", "id": "everyone", "displayName": "Everyone"},
        {"type": "group", "id": "group-1", "displayName": "Finance Team"},
    ]

    result = get_zone_remediation_principals(
        zone=0,  # Unknown zone
        current_principals=current_principals,
        approved_groups=[],
        dataverse_client=mock_dataverse_client,
    )

    # Should apply Zone 2 logic (remove Everyone, preserve Finance Team)
    assert len(result) == 1
    assert result[0]["properties"]["principal"]["displayName"] == "Finance Team"


# =========================================================================
# Post-remediation validation tests
# =========================================================================


def test_validate_remediation_success_first_attempt(mock_bap_client, mock_dataverse_client):
    """Test validate_remediation succeeds on first attempt."""
    # Mock successful compliance check
    with mock.patch("remediate_agent_sharing.check_agent_compliance") as mock_check:
        mock_check.return_value = {"compliant": True}

        # Mock BAP API returns approved groups
        mock_bap_client.get_agent_permissions.return_value = [
            {"type": "group", "id": "approved-1", "displayName": "Approved Team"}
        ]

        result = validate_remediation(
            agent_id="agent-1",
            environment_id="env-1",
            environment_name="Production",
            bap_client=mock_bap_client,
            dataverse_client=mock_dataverse_client,
            max_retries=3,
        )

        assert result["validated"] is True
        assert result["compliant"] is True
        assert result["attempts"] == 1
        assert result["error"] is None


def test_validate_remediation_success_after_retry(mock_bap_client, mock_dataverse_client):
    """Test validate_remediation succeeds after one retry (eventual consistency)."""
    # Mock compliance check fails first, then succeeds
    with mock.patch("remediate_agent_sharing.check_agent_compliance") as mock_check:
        mock_check.side_effect = [
            {"compliant": False, "violation_type": "UnauthorizedGroupSharing"},
            {"compliant": True},
        ]

        # Mock BAP API returns approved groups
        mock_bap_client.get_agent_permissions.return_value = [
            {"type": "group", "id": "approved-1", "displayName": "Approved Team"}
        ]

        result = validate_remediation(
            agent_id="agent-1",
            environment_id="env-1",
            environment_name="Production",
            bap_client=mock_bap_client,
            dataverse_client=mock_dataverse_client,
            max_retries=3,
        )

        assert result["validated"] is True
        assert result["compliant"] is True
        assert result["attempts"] == 2  # First attempt failed, second succeeded


def test_validate_remediation_failure_after_max_retries(mock_bap_client, mock_dataverse_client):
    """Test validate_remediation fails after exhausting max retries."""
    # Mock compliance check always returns non-compliant
    with mock.patch("remediate_agent_sharing.check_agent_compliance") as mock_check:
        mock_check.return_value = {
            "compliant": False,
            "violation_type": "UnauthorizedGroupSharing",
            "details": "Agent still has Everyone group",
        }

        # Mock BAP API returns old principals (not updated)
        mock_bap_client.get_agent_permissions.return_value = [
            {"type": "group", "id": "everyone", "displayName": "Everyone"}
        ]

        result = validate_remediation(
            agent_id="agent-1",
            environment_id="env-1",
            environment_name="Production",
            bap_client=mock_bap_client,
            dataverse_client=mock_dataverse_client,
            max_retries=3,
        )

        assert result["validated"] is True  # Validation ran, but result is non-compliant
        assert result["compliant"] is False
        assert result["attempts"] == 3
        assert "Agent still has Everyone group" in result["error"]


def test_validate_remediation_exception_handling(mock_bap_client, mock_dataverse_client):
    """Test validate_remediation handles exceptions gracefully."""
    # Mock BAP API raises exception
    mock_bap_client.get_agent_permissions.side_effect = Exception("Network error")

    result = validate_remediation(
        agent_id="agent-1",
        environment_id="env-1",
        environment_name="Production",
        bap_client=mock_bap_client,
        dataverse_client=mock_dataverse_client,
        max_retries=3,
    )

    assert result["validated"] is False
    assert result["compliant"] is False
    assert result["attempts"] == 3
    assert "Network error" in result["error"]


# =========================================================================
# Dataverse update tests
# =========================================================================


def test_update_compliance_record_success(mock_dataverse_client):
    """Test update_compliance_record successfully upserts to Dataverse."""
    result = update_compliance_record(
        agent_id="agent-1",
        environment_id="env-1",
        status=0,  # Compliant
        remediation_date="2026-02-13T18:00:00Z",
        dataverse_client=mock_dataverse_client,
    )

    assert result is True
    mock_dataverse_client.upsert_record.assert_called_once()

    # Verify payload structure
    call_args = mock_dataverse_client.upsert_record.call_args
    payload = call_args[1]["data"]
    assert payload["fsi_agent_id"] == "agent-1"
    assert payload["fsi_environment_id"] == "env-1"
    assert payload["fsi_compliance_status"] == 0
    assert payload["fsi_remediation_date"] == "2026-02-13T18:00:00Z"


def test_update_compliance_record_with_error_details(mock_dataverse_client):
    """Test update_compliance_record includes error details when provided."""
    error_message = "Validation failed: Agent still has Everyone group after remediation"

    result = update_compliance_record(
        agent_id="agent-1",
        environment_id="env-1",
        status=3,  # Error
        remediation_date="2026-02-13T18:00:00Z",
        dataverse_client=mock_dataverse_client,
        error_details=error_message,
    )

    assert result is True

    # Verify error details in payload
    call_args = mock_dataverse_client.upsert_record.call_args
    payload = call_args[1]["data"]
    assert payload["fsi_validation_error"] == error_message


def test_update_compliance_record_truncates_long_error(mock_dataverse_client):
    """Test update_compliance_record truncates error details to 4000 chars."""
    long_error = "Error: " + "x" * 5000  # 5000+ characters

    result = update_compliance_record(
        agent_id="agent-1",
        environment_id="env-1",
        status=3,
        remediation_date="2026-02-13T18:00:00Z",
        dataverse_client=mock_dataverse_client,
        error_details=long_error,
    )

    assert result is True

    # Verify error details truncated to 4000 chars
    call_args = mock_dataverse_client.upsert_record.call_args
    payload = call_args[1]["data"]
    assert len(payload["fsi_validation_error"]) == 4000


def test_update_compliance_record_failure(mock_dataverse_client):
    """Test update_compliance_record handles Dataverse upsert failure."""
    # Mock Dataverse upsert raises exception
    mock_dataverse_client.upsert_record.side_effect = Exception("Dataverse connection failed")

    result = update_compliance_record(
        agent_id="agent-1",
        environment_id="env-1",
        status=0,
        remediation_date="2026-02-13T18:00:00Z",
        dataverse_client=mock_dataverse_client,
    )

    assert result is False


# =========================================================================
# Integration workflow tests (optional, requires mocked clients)
# =========================================================================


def test_remediate_agent_whatif_mode():
    """Test remediate_agent in WhatIf mode (no PATCH executed)."""
    # This test would require mocking argparse.Namespace and full workflow
    # Deferred to integration testing (Phase 5)
    pass


def test_remediate_agent_single_agent_mode():
    """Test remediate_agent processes single agent successfully."""
    # This test would require mocking BAP + Dataverse clients and full workflow
    # Deferred to integration testing (Phase 5)
    pass


# =========================================================================
# Exception handling tests (Phase 4)
# =========================================================================


def test_remediate_agent_skips_active_exception():
    """Test that remediate_agent skips agents with active exceptions."""
    import argparse
    from unittest import mock
    
    # Mock clients
    mock_bap_client = mock.MagicMock()
    mock_dataverse_client = mock.MagicMock()
    
    # Mock Dataverse GET request to return active exception
    mock_get_response = mock.MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {
        "fsi_compliance_status": 2,  # Exception
        "fsi_exception_expires_at": "2026-12-31T00:00:00Z",  # Future date
        "fsi_exception_justification": "Test exception",
        "fsi_exception_approved_by": "Test Approver",
    }
    
    mock_dataverse_client._session.get.return_value = mock_get_response
    mock_dataverse_client._get_headers.return_value = {"Authorization": "Bearer test"}
    mock_dataverse_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    
    # Mock argparse.Namespace
    args = argparse.Namespace(
        whatif=False,
        verbose=True,
        zone_override=None,
    )
    
    # Agent data
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Test Environment",
        "sharing_principals_json": "[]",
    }
    
    # Import function
    from remediate_agent_sharing import remediate_agent
    
    # Call remediate_agent
    result = remediate_agent(agent_data, mock_bap_client, mock_dataverse_client, args)
    
    # Verify agent was skipped
    assert result["success"] is True
    assert result.get("skipped") is True
    assert result.get("skip_reason") == "active_exception"
    
    # Verify no PATCH was attempted
    mock_bap_client.modify_agent_permissions.assert_not_called()


def test_remediate_agent_proceeds_with_expired_exception():
    """Test that remediate_agent proceeds when exception is expired."""
    import argparse
    from unittest import mock
    
    # Mock clients
    mock_bap_client = mock.MagicMock()
    mock_dataverse_client = mock.MagicMock()
    
    # Mock Dataverse GET request to return EXPIRED exception
    mock_get_response = mock.MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {
        "fsi_compliance_status": 2,  # Exception
        "fsi_exception_expires_at": "2020-01-01T00:00:00Z",  # Past date (expired)
        "fsi_exception_justification": "Test exception",
        "fsi_exception_approved_by": "Test Approver",
    }
    
    mock_dataverse_client._session.get.return_value = mock_get_response
    mock_dataverse_client._get_headers.return_value = {"Authorization": "Bearer test"}
    mock_dataverse_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    
    # Mock classify_environment_zone
    with mock.patch("remediate_agent_sharing.classify_environment_zone") as mock_classify:
        mock_classify.return_value = 2  # Zone 2
        
        # Mock parse_sharing_principals
        with mock.patch("remediate_agent_sharing.parse_sharing_principals") as mock_parse:
            mock_parse.return_value = {"principals": [{"type": "user", "id": "user-1"}]}
            
            # Mock get_zone_remediation_principals
            with mock.patch("remediate_agent_sharing.get_zone_remediation_principals") as mock_remediate:
                mock_remediate.return_value = [{"properties": {"roleName": "CanView"}}]
                
                # Mock BAP client modify_agent_permissions (success)
                mock_bap_client.modify_agent_permissions.return_value = True
                
                # Mock validate_remediation
                with mock.patch("remediate_agent_sharing.validate_remediation") as mock_validate:
                    mock_validate.return_value = {"compliant": True, "attempts": 1}
                    
                    # Mock update_compliance_record
                    with mock.patch("remediate_agent_sharing.update_compliance_record") as mock_update:
                        mock_update.return_value = True
                        
                        # Mock argparse.Namespace
                        args = argparse.Namespace(
                            whatif=False,
                            verbose=False,
                            zone_override=None,
                        )
                        
                        # Agent data
                        agent_data = {
                            "agent_id": "agent-123",
                            "agent_name": "Test Agent",
                            "environment_id": "env-456",
                            "environment_name": "Test Environment",
                            "sharing_principals_json": '[{"type":"user","id":"user-1"}]',
                        }
                        
                        # Import function
                        from remediate_agent_sharing import remediate_agent
                        
                        # Call remediate_agent
                        result = remediate_agent(agent_data, mock_bap_client, mock_dataverse_client, args)
                        
                        # Verify agent was NOT skipped (expired exception ignored)
                        assert result.get("skipped") is not True
                        
                        # Verify PATCH was attempted
                        mock_bap_client.modify_agent_permissions.assert_called_once()


def test_remediate_agent_proceeds_with_no_exception():
    """Test that remediate_agent proceeds normally when no exception exists."""
    import argparse
    from unittest import mock
    
    # Mock clients
    mock_bap_client = mock.MagicMock()
    mock_dataverse_client = mock.MagicMock()
    
    # Mock Dataverse GET request to return 404 (no record)
    mock_get_response = mock.MagicMock()
    mock_get_response.status_code = 404
    
    mock_dataverse_client._session.get.return_value = mock_get_response
    mock_dataverse_client._get_headers.return_value = {"Authorization": "Bearer test"}
    mock_dataverse_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    
    # Mock classify_environment_zone
    with mock.patch("remediate_agent_sharing.classify_environment_zone") as mock_classify:
        mock_classify.return_value = 2  # Zone 2
        
        # Mock parse_sharing_principals
        with mock.patch("remediate_agent_sharing.parse_sharing_principals") as mock_parse:
            mock_parse.return_value = {"principals": [{"type": "user", "id": "user-1"}]}
            
            # Mock get_zone_remediation_principals
            with mock.patch("remediate_agent_sharing.get_zone_remediation_principals") as mock_remediate:
                mock_remediate.return_value = [{"properties": {"roleName": "CanView"}}]
                
                # Mock BAP client modify_agent_permissions (success)
                mock_bap_client.modify_agent_permissions.return_value = True
                
                # Mock validate_remediation
                with mock.patch("remediate_agent_sharing.validate_remediation") as mock_validate:
                    mock_validate.return_value = {"compliant": True, "attempts": 1}
                    
                    # Mock update_compliance_record
                    with mock.patch("remediate_agent_sharing.update_compliance_record") as mock_update:
                        mock_update.return_value = True
                        
                        # Mock argparse.Namespace
                        args = argparse.Namespace(
                            whatif=False,
                            verbose=False,
                            zone_override=None,
                        )
                        
                        # Agent data
                        agent_data = {
                            "agent_id": "agent-123",
                            "agent_name": "Test Agent",
                            "environment_id": "env-456",
                            "environment_name": "Test Environment",
                            "sharing_principals_json": '[{"type":"user","id":"user-1"}]',
                        }
                        
                        # Import function
                        from remediate_agent_sharing import remediate_agent
                        
                        # Call remediate_agent
                        result = remediate_agent(agent_data, mock_bap_client, mock_dataverse_client, args)
                        
                        # Verify agent was NOT skipped
                        assert result.get("skipped") is not True
                        
                        # Verify PATCH was attempted
                        mock_bap_client.modify_agent_permissions.assert_called_once()

