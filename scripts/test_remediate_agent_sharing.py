"""Unit tests for remediate_agent_sharing.py."""

import argparse
import json
import sys
from unittest import mock

import pytest
from asard_zone_rules import check_agent_compliance as real_check_agent_compliance
from remediate_agent_sharing import (
    build_permission_object,
    get_zone_remediation_principals,
    main,
    parse_remediation_principals,
    remediate_agent,
    summarize_result_bucket,
    update_compliance_record,
    validate_remediation,
)

# =========================================================================
# Test fixtures
# =========================================================================


def _make_dataverse_client(approved_group_ids=None):
    """Build a Dataverse mock with no policy record and no active exception.

    ``fsi_environmentpolicies`` returns no rows, so any zone classification
    falls through to naming convention — the condition that lets validation
    drift to Zone 0 when the resolved zone is not threaded through.
    """
    client = mock.MagicMock()
    client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    client._session.get.return_value.status_code = 404
    client.execute_query.return_value = {"value": []}

    def _query(entity_set, **_kwargs):
        if entity_set == "fsi_approvedsecuritygrouppolicies":
            return [{"fsi_group_id": gid} for gid in (approved_group_ids or [])]
        return []

    client.query.side_effect = _query
    return client


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


@pytest.mark.parametrize(
    "payload",
    [
        "{bad json}",
        json.dumps({"type": "user", "id": "user-1"}),
        json.dumps([42]),
        json.dumps([{"id": "user-1"}]),
        json.dumps([{"type": "user"}]),
        json.dumps([{"type": "mystery", "id": "principal-1"}]),
        json.dumps(
            [
                {
                    "properties": {
                        "principal": {"type": "User", "id": "user-1"}
                    }
                }
            ]
        ),
    ],
)
def test_parse_remediation_principals_rejects_malformed_or_unknown_flat_items(
    payload,
):
    """Mutation input rejects malformed, nested, and unknown principal shapes."""
    with pytest.raises(ValueError):
        parse_remediation_principals(payload)


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


def test_zone_remediation_helper_rejects_unknown_flat_principal(
    mock_dataverse_client,
):
    """The mutation helper itself cannot silently discard an unknown type."""
    with pytest.raises(ValueError, match="unsupported type"):
        get_zone_remediation_principals(
            zone=2,
            current_principals=[
                {"type": "mystery", "id": "principal-1", "displayName": "Unknown"}
            ],
            approved_groups=[],
            dataverse_client=mock_dataverse_client,
        )


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
    """Test Zone 2 remediation handles case-insensitive Everyone/Public matching.

    The production code (``get_zone_remediation_principals`` in
    ``remediate_agent_sharing.py``) uses **exact** (set-membership) matching
    against ``_system_names`` so a legitimate group with a name that contains
    ``"public"`` or ``"all"`` as a substring (e.g. "Republic Team", "Mall
    Operations") is preserved. The case-insensitivity comes from lowercasing
    the inputs before the set lookup, not from substring matching.

    This test exercises the case-insensitivity path with ``"EVERYONE"`` (mixed
    upper) and ``"Public"`` (initial-cap). Both lowercase exactly to entries in
    the system-name set and must be filtered. ``"Finance Team"`` is preserved
    because it's a real named group.
    """
    current_principals = [
        {"type": "group", "id": "group-1", "displayName": "EVERYONE"},
        {"type": "group", "id": "group-2", "displayName": "Public"},
        {"type": "group", "id": "group-3", "displayName": "Finance Team"},
    ]

    result = get_zone_remediation_principals(
        zone=2,
        current_principals=current_principals,
        approved_groups=[],
        dataverse_client=mock_dataverse_client,
    )

    # Should preserve only Finance Team (EVERYONE and Public removed)
    assert len(result) == 1
    assert result[0]["properties"]["principal"]["displayName"] == "Finance Team"


def test_zone_2_remediation_preserves_substring_named_groups(mock_dataverse_client):
    """Companion to the case-insensitive test: documents that the production
    code intentionally does NOT substring-match against ``_system_names``.

    Without this test, a future maintainer could "fix" the case-insensitive
    test by changing the production set-membership check to a substring
    contains-check, which would silently break customers whose group names
    contain words like "public" or "all" as roots ("Republic Team",
    "Public Sector Solutions", "Falls Church Office", "All-Stars").
    """
    current_principals = [
        {"type": "group", "id": "group-1", "displayName": "Republic Team"},
        {"type": "group", "id": "group-2", "displayName": "Public Sector Solutions"},
        {"type": "group", "id": "group-3", "displayName": "All-Stars"},
        {"type": "group", "id": "group-4", "displayName": "Everyone"},
    ]

    result = get_zone_remediation_principals(
        zone=2,
        current_principals=current_principals,
        approved_groups=[],
        dataverse_client=mock_dataverse_client,
    )

    # Should preserve the 3 substring-named groups; remove only "Everyone".
    assert len(result) == 3
    display_names = [p["properties"]["principal"]["displayName"] for p in result]
    assert "Republic Team" in display_names
    assert "Public Sector Solutions" in display_names
    assert "All-Stars" in display_names
    assert "Everyone" not in display_names


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
        mock_check.return_value = {"compliant": True, "zone": 3}

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
            zone=3,
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
            {"compliant": False, "violation_type": "UnauthorizedGroupSharing", "zone": 3},
            {"compliant": True, "zone": 3},
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
            zone=3,
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
            "zone": 3,
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
            zone=3,
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
        zone=3,
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


def test_remediate_agent_calls_classifier_with_supported_arguments():
    """Test non-override remediation uses the classifier's supported contract."""
    import argparse

    from remediate_agent_sharing import remediate_agent

    mock_bap_client = mock.MagicMock()
    mock_dataverse_client = mock.MagicMock()
    mock_dataverse_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    mock_dataverse_client._session.get.return_value.status_code = 404
    args = argparse.Namespace(whatif=True, verbose=False, zone_override=None)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Production-Finance",
        "sharing_principals_json": "[]",
    }

    with (
        mock.patch(
            "remediate_agent_sharing.classify_environment_zone",
            autospec=True,
            return_value=3,
        ) as mock_classify,
        mock.patch(
            "remediate_agent_sharing.parse_remediation_principals",
            wraps=parse_remediation_principals,
        ),
        mock.patch(
            "remediate_agent_sharing.get_zone_remediation_principals",
            return_value=[],
        ),
    ):
        result = remediate_agent(
            agent_data,
            mock_bap_client,
            mock_dataverse_client,
            args,
        )

    assert result == {"success": True, "whatif": True, "error": None}
    mock_classify.assert_called_once_with(
        environment_id="env-456",
        environment_name="Production-Finance",
        client=mock_dataverse_client,
    )


def test_remediate_agent_fails_closed_for_unclassified_single_agent_context():
    """Test GUID-only single-agent context cannot remediate as Zone 0."""
    import argparse

    from remediate_agent_sharing import remediate_agent

    environment_id = "11111111-2222-3333-4444-555555555555"
    mock_bap_client = mock.MagicMock()
    mock_dataverse_client = mock.MagicMock()
    mock_dataverse_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    mock_dataverse_client._session.get.return_value.status_code = 404
    mock_dataverse_client.query.return_value = []
    args = argparse.Namespace(whatif=False, verbose=False, zone_override=None)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "agent-123",
        "environment_id": environment_id,
        "environment_name": environment_id,
        "sharing_principals_json": "[]",
    }

    with (
        mock.patch(
            "remediate_agent_sharing.parse_remediation_principals",
            wraps=parse_remediation_principals,
        ) as mock_parse,
        mock.patch(
            "remediate_agent_sharing.get_zone_remediation_principals"
        ) as mock_remediation,
        mock.patch(
            "remediate_agent_sharing.update_compliance_record"
        ) as mock_update,
    ):
        result = remediate_agent(
            agent_data,
            mock_bap_client,
            mock_dataverse_client,
            args,
        )

    assert result["success"] is False
    assert result["whatif"] is False
    assert "usable environment policy" in result["error"]
    assert "recognizable environment name" in result["error"]
    assert "--zone-override" in result["error"]
    mock_parse.assert_not_called()
    mock_remediation.assert_not_called()
    mock_bap_client.modify_agent_permissions.assert_not_called()
    mock_update.assert_not_called()


@pytest.mark.parametrize("zone", [1, 2, 3])
def test_remediate_agent_classified_zones_still_proceed(zone):
    """Test classified zones still mutate permissions and write compliance."""
    import argparse

    from remediate_agent_sharing import remediate_agent

    mock_bap_client = mock.MagicMock()
    mock_bap_client.modify_agent_permissions.return_value = True
    mock_dataverse_client = mock.MagicMock()
    mock_dataverse_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    mock_dataverse_client._session.get.return_value.status_code = 404
    args = argparse.Namespace(whatif=False, verbose=False, zone_override=None)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Recognized Environment",
        "sharing_principals_json": "[]",
    }

    with (
        mock.patch(
            "remediate_agent_sharing.classify_environment_zone",
            autospec=True,
            return_value=zone,
        ),
        mock.patch(
            "remediate_agent_sharing.parse_remediation_principals",
            wraps=parse_remediation_principals,
        ),
        mock.patch(
            "remediate_agent_sharing.get_approved_groups_for_zone",
            return_value=[],
        ),
        mock.patch(
            "remediate_agent_sharing.get_zone_remediation_principals",
            return_value=[],
        ),
        mock.patch(
            "remediate_agent_sharing.validate_remediation",
            return_value={"compliant": True, "attempts": 1},
        ),
        mock.patch(
            "remediate_agent_sharing.update_compliance_record",
            return_value=True,
        ) as mock_update,
    ):
        result = remediate_agent(
            agent_data,
            mock_bap_client,
            mock_dataverse_client,
            args,
        )

    assert result == {"success": True, "whatif": False, "error": None}
    mock_bap_client.modify_agent_permissions.assert_called_once()
    mock_update.assert_called_once()


def test_zone_1_flat_payload_preserves_user_in_exact_replace_body():
    """Zone 1 keeps the raw-payload user and removes the raw-payload group."""
    current_principals = [
        {"type": "user", "id": "user-1", "displayName": "Alex User"},
        {"type": "group", "id": "group-1", "displayName": "Finance Team"},
    ]
    mock_bap_client = mock.MagicMock()
    mock_bap_client.modify_agent_permissions.return_value = True
    mock_dataverse_client = _make_dataverse_client()
    args = argparse.Namespace(whatif=False, verbose=False, zone_override=1)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Test Environment",
        "sharing_principals_json": json.dumps(current_principals),
    }

    with (
        mock.patch(
            "remediate_agent_sharing.validate_remediation",
            return_value={"compliant": True, "attempts": 1},
        ),
        mock.patch(
            "remediate_agent_sharing.update_compliance_record", return_value=True
        ),
    ):
        result = remediate_agent(
            agent_data, mock_bap_client, mock_dataverse_client, args
        )

    expected_body = {
        "put": [
            {
                "properties": {
                    "roleName": "CanView",
                    "principal": {
                        "id": "user-1",
                        "type": "User",
                        "displayName": "Alex User",
                    },
                }
            }
        ]
    }
    call = mock_bap_client.modify_agent_permissions.call_args.kwargs
    assert result == {"success": True, "whatif": False, "error": None}
    assert call["environment_id"] == "env-456"
    assert call["agent_id"] == "agent-123"
    assert {"put": call["principals"]} == expected_body


def test_zone_2_flat_payload_removes_everyone_in_exact_replace_body():
    """Zone 2 keeps raw users/groups and removes Everyone from the replace body."""
    current_principals = [
        {"type": "user", "id": "user-1", "displayName": "Alex User"},
        {"type": "group", "id": "group-1", "displayName": "Finance Team"},
        {"type": "Everyone", "id": "everyone", "displayName": "Everyone"},
    ]
    mock_bap_client = mock.MagicMock()
    mock_bap_client.modify_agent_permissions.return_value = True
    mock_dataverse_client = _make_dataverse_client()
    args = argparse.Namespace(whatif=False, verbose=False, zone_override=2)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Test Environment",
        "sharing_principals_json": json.dumps(current_principals),
    }

    with (
        mock.patch(
            "remediate_agent_sharing.validate_remediation",
            return_value={"compliant": True, "attempts": 1},
        ),
        mock.patch(
            "remediate_agent_sharing.update_compliance_record", return_value=True
        ),
    ):
        result = remediate_agent(
            agent_data, mock_bap_client, mock_dataverse_client, args
        )

    expected_body = {
        "put": [
            {
                "properties": {
                    "roleName": "CanView",
                    "principal": {
                        "id": "user-1",
                        "type": "User",
                        "displayName": "Alex User",
                    },
                }
            },
            {
                "properties": {
                    "roleName": "CanView",
                    "principal": {
                        "id": "group-1",
                        "type": "Group",
                        "displayName": "Finance Team",
                    },
                }
            },
        ]
    }
    call = mock_bap_client.modify_agent_permissions.call_args.kwargs
    assert result == {"success": True, "whatif": False, "error": None}
    assert call["environment_id"] == "env-456"
    assert call["agent_id"] == "agent-123"
    assert {"put": call["principals"]} == expected_body


@pytest.mark.parametrize(
    "payload",
    [
        "{bad json}",
        json.dumps({"type": "user", "id": "user-1"}),
        json.dumps([{"type": "unknown", "id": "principal-1"}]),
        json.dumps(
            [
                {
                    "properties": {
                        "principal": {"type": "User", "id": "user-1"}
                    }
                }
            ]
        ),
    ],
)
def test_remediate_agent_invalid_flat_payload_fails_before_mutation(payload):
    """Invalid raw payloads cannot reach replace-all PATCH or compliance writes."""
    mock_bap_client = mock.MagicMock()
    mock_dataverse_client = _make_dataverse_client()
    args = argparse.Namespace(whatif=False, verbose=False, zone_override=2)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Test Environment",
        "sharing_principals_json": payload,
    }

    with mock.patch(
        "remediate_agent_sharing.update_compliance_record"
    ) as mock_update:
        result = remediate_agent(
            agent_data, mock_bap_client, mock_dataverse_client, args
        )

    assert result["success"] is False
    assert result["whatif"] is False
    assert result["error"]
    mock_bap_client.modify_agent_permissions.assert_not_called()
    mock_update.assert_not_called()


def test_remediate_agent_whatif_uses_true_flat_payload_counts(capsys):
    """WhatIf previews the real current/proposed counts and never mutates."""
    current_principals = [
        {"type": "user", "id": "user-1", "displayName": "Alex User"},
        {"type": "group", "id": "group-1", "displayName": "Finance Team"},
        {"type": "Everyone", "id": "everyone", "displayName": "Everyone"},
    ]
    mock_bap_client = mock.MagicMock()
    mock_dataverse_client = _make_dataverse_client()
    args = argparse.Namespace(whatif=True, verbose=False, zone_override=2)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Test Environment",
        "sharing_principals_json": json.dumps(current_principals),
    }

    with (
        mock.patch(
            "remediate_agent_sharing.validate_remediation"
        ) as mock_validate,
        mock.patch(
            "remediate_agent_sharing.update_compliance_record"
        ) as mock_update,
    ):
        result = remediate_agent(
            agent_data, mock_bap_client, mock_dataverse_client, args
        )

    output = capsys.readouterr().out
    assert result == {"success": True, "whatif": True, "error": None}
    assert "Current sharing: 3 principal(s)" in output
    assert "Proposed sharing: 2 principal(s)" in output
    assert "Alex User (user)" in output
    assert "Finance Team (group)" in output
    assert "[WHATIF] No changes applied" in output
    mock_bap_client.modify_agent_permissions.assert_not_called()
    mock_validate.assert_not_called()
    mock_update.assert_not_called()


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

        # Exercise the real raw flat-payload parser contract.
        with mock.patch(
            "remediate_agent_sharing.parse_remediation_principals",
            wraps=parse_remediation_principals,
        ):
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

        # Exercise the real raw flat-payload parser contract.
        with mock.patch(
            "remediate_agent_sharing.parse_remediation_principals",
            wraps=parse_remediation_principals,
        ):
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


# =========================================================================
# WhatIf accounting regression tests
# =========================================================================


def test_summarize_result_bucket_never_reports_failure_as_simulated():
    """Test a failed result is bucketed as failed even when WhatIf was set."""
    assert (
        summarize_result_bucket({"success": False, "whatif": True, "error": "boom"})
        == "failed"
    )
    assert (
        summarize_result_bucket({"success": False, "whatif": False, "error": "boom"})
        == "failed"
    )
    assert (
        summarize_result_bucket({"success": True, "whatif": True, "error": None})
        == "whatif"
    )
    assert (
        summarize_result_bucket({"success": True, "whatif": False, "error": None})
        == "succeeded"
    )
    assert (
        summarize_result_bucket(
            {"success": True, "whatif": False, "error": None, "skipped": True}
        )
        == "skipped"
    )


def test_remediate_agent_zone_zero_guard_is_a_failure_under_whatif():
    """Test the Zone 0 refusal counts as a failure, not a simulated run."""
    environment_id = "11111111-2222-3333-4444-555555555555"
    mock_bap_client = mock.MagicMock()
    mock_dataverse_client = _make_dataverse_client()
    args = argparse.Namespace(whatif=True, verbose=False, zone_override=None)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "agent-123",
        "environment_id": environment_id,
        "environment_name": environment_id,
        "sharing_principals_json": "[]",
    }

    with mock.patch("remediate_agent_sharing.update_compliance_record") as mock_update:
        result = remediate_agent(
            agent_data, mock_bap_client, mock_dataverse_client, args
        )

    assert result["success"] is False
    assert result["whatif"] is False
    assert summarize_result_bucket(result) == "failed"
    mock_bap_client.modify_agent_permissions.assert_not_called()
    mock_update.assert_not_called()


# =========================================================================
# Validation zone-contract regression tests
# =========================================================================


@pytest.mark.parametrize("zone", [0, None, 4, "1"])
def test_validate_remediation_refuses_unenforceable_zone(
    mock_bap_client, mock_dataverse_client, zone
):
    """Test validation never runs without an enforceable Zone 1/2/3."""
    with mock.patch("remediate_agent_sharing.check_agent_compliance") as mock_check:
        result = validate_remediation(
            agent_id="agent-1",
            environment_id="env-1",
            environment_name="MyCustomEnv",
            bap_client=mock_bap_client,
            dataverse_client=mock_dataverse_client,
            zone=zone,
            max_retries=3,
        )

    assert result["validated"] is False
    assert result["compliant"] is False
    assert result["attempts"] == 0
    assert "not enforceable" in result["error"]
    mock_check.assert_not_called()
    mock_bap_client.get_agent_permissions.assert_not_called()


@pytest.mark.parametrize("zone", [1, 2, 3])
def test_validate_remediation_evaluates_the_resolved_zone(
    mock_bap_client, mock_dataverse_client, zone
):
    """Test the resolved remediation zone is what validation evaluates."""
    mock_bap_client.get_agent_permissions.return_value = [
        {"type": "group", "id": "group-1", "displayName": "Finance Team"}
    ]

    with (
        mock.patch("remediate_agent_sharing.time.sleep"),
        mock.patch("remediate_agent_sharing.check_agent_compliance") as mock_check,
    ):
        mock_check.return_value = {"compliant": True, "zone": zone}

        result = validate_remediation(
            agent_id="agent-1",
            environment_id="env-1",
            environment_name="MyCustomEnv",
            bap_client=mock_bap_client,
            dataverse_client=mock_dataverse_client,
            zone=zone,
            max_retries=3,
        )

    assert result["compliant"] is True
    assert mock_check.call_args.kwargs["zone"] == zone


def test_validate_remediation_fails_closed_when_evaluated_zone_disagrees(
    mock_bap_client, mock_dataverse_client
):
    """Test a Zone 0 verdict can never validate a Zone 1 remediation."""
    mock_bap_client.get_agent_permissions.return_value = [
        {"type": "group", "id": "group-1", "displayName": "Finance Team"}
    ]

    with (
        mock.patch("remediate_agent_sharing.time.sleep"),
        mock.patch("remediate_agent_sharing.check_agent_compliance") as mock_check,
    ):
        mock_check.return_value = {"compliant": True, "zone": 0}

        result = validate_remediation(
            agent_id="agent-1",
            environment_id="env-1",
            environment_name="MyCustomEnv",
            bap_client=mock_bap_client,
            dataverse_client=mock_dataverse_client,
            zone=1,
            max_retries=3,
        )

    assert result["validated"] is False
    assert result["compliant"] is False
    assert result["attempts"] == 3
    assert "Zone 1" in result["error"]
    assert mock_check.call_count == 3


def test_remediate_agent_override_zone_1_persisting_group_never_writes_compliant():
    """Test --zone-override 1 with a surviving group fails closed end-to-end.

    Without the resolved zone threaded into validation, the unclassifiable
    environment re-classifies to Zone 0, whose permissive rules accept the
    surviving group and write Compliant.
    """
    environment_id = "11111111-2222-3333-4444-555555555555"
    surviving_group = {
        "type": "group",
        "id": "group-still-shared",
        "displayName": "Finance Team",
    }

    mock_bap_client = mock.MagicMock()
    mock_bap_client.modify_agent_permissions.return_value = True
    mock_bap_client.get_agent_permissions.return_value = [surviving_group]
    mock_dataverse_client = _make_dataverse_client()
    args = argparse.Namespace(whatif=False, verbose=False, zone_override=1)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "agent-123",
        "environment_id": environment_id,
        "environment_name": environment_id,
        "sharing_principals_json": json.dumps([surviving_group]),
    }

    with (
        mock.patch("remediate_agent_sharing.time.sleep"),
        mock.patch(
            "remediate_agent_sharing.check_agent_compliance",
            wraps=real_check_agent_compliance,
        ) as spy_check,
        mock.patch(
            "remediate_agent_sharing.update_compliance_record", return_value=True
        ) as mock_update,
    ):
        result = remediate_agent(
            agent_data, mock_bap_client, mock_dataverse_client, args
        )

    assert result["success"] is False
    assert result["whatif"] is False
    assert summarize_result_bucket(result) == "failed"

    # The surviving group was judged by the Zone 1 rules the remediation applied
    assert {call.kwargs["zone"] for call in spy_check.call_args_list} == {1}
    assert "Zone 1" in result["error"]
    assert "does not allow group sharing" in result["error"]

    # Retried per existing convention before failing
    assert mock_bap_client.get_agent_permissions.call_count == 3

    # Wrote Error (3) and never Compliant (0)
    statuses = [call.kwargs["status"] for call in mock_update.call_args_list]
    assert statuses == [3]


@pytest.mark.parametrize(
    ("environment_name", "expected_zone"),
    [("QA-Testing", 2), ("Production-Finance", 3)],
)
def test_remediate_agent_classified_zone_validation_matches_remediation_zone(
    environment_name, expected_zone
):
    """Test classified Zone 2/3 remediations are validated under the same zone."""
    surviving_everyone = {"type": "Everyone", "id": "all", "displayName": "Everyone"}

    mock_bap_client = mock.MagicMock()
    mock_bap_client.modify_agent_permissions.return_value = True
    mock_bap_client.get_agent_permissions.return_value = [surviving_everyone]
    mock_dataverse_client = _make_dataverse_client(approved_group_ids=["approved-1"])
    args = argparse.Namespace(whatif=False, verbose=False, zone_override=None)
    agent_data = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": environment_name,
        "sharing_principals_json": json.dumps([surviving_everyone]),
    }

    with (
        mock.patch("remediate_agent_sharing.time.sleep"),
        mock.patch(
            "remediate_agent_sharing.check_agent_compliance",
            wraps=real_check_agent_compliance,
        ) as spy_check,
        mock.patch(
            "remediate_agent_sharing.update_compliance_record", return_value=True
        ) as mock_update,
    ):
        result = remediate_agent(
            agent_data, mock_bap_client, mock_dataverse_client, args
        )

    assert spy_check.call_count == 3
    assert {call.kwargs["zone"] for call in spy_check.call_args_list} == {expected_zone}
    assert result["success"] is False
    assert result["whatif"] is False
    assert f"Zone {expected_zone}" in result["error"]

    statuses = [call.kwargs["status"] for call in mock_update.call_args_list]
    assert statuses == [3]


# =========================================================================
# CLI exit-code regression tests
# =========================================================================


@pytest.mark.parametrize(
    ("cli_args", "remediation_result", "expected_exit"),
    [
        (
            [],
            {"success": False, "whatif": False, "error": "mutation refused"},
            1,
        ),
        (
            [],
            {"success": True, "whatif": False, "error": None},
            0,
        ),
        (
            ["--whatif"],
            {"success": True, "whatif": True, "error": None},
            0,
        ),
    ],
)
def test_main_returns_failure_only_when_processing_has_failures(
    cli_args, remediation_result, expected_exit
):
    """CLI exits nonzero for failed agents and zero for success/WhatIf-only."""
    bap_client = mock.MagicMock()
    bap_client.test_connection.return_value = True
    dataverse_client = mock.MagicMock()
    agents = [
        {
            "agent_id": "agent-123",
            "agent_name": "Test Agent",
            "environment_id": "env-456",
            "environment_name": "Test Environment",
            "sharing_principals_json": "[]",
        }
    ]

    with (
        mock.patch.object(
            sys, "argv", ["remediate_agent_sharing.py", *cli_args]
        ),
        mock.patch(
            "remediate_agent_sharing.BAPAdminClient", return_value=bap_client
        ),
        mock.patch(
            "remediate_agent_sharing.CAAClient", return_value=dataverse_client
        ),
        mock.patch(
            "remediate_agent_sharing.load_agents_from_dataverse",
            return_value=agents,
        ),
        mock.patch(
            "remediate_agent_sharing.remediate_agent",
            return_value=remediation_result,
        ),
    ):
        exit_code = main()

    assert exit_code == expected_exit
