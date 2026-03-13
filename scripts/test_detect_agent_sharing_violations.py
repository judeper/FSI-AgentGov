"""Unit tests for detect_agent_sharing_violations.py — Output & persistence functionality.

This test suite covers:
- Dataverse upsert operations (create, update, failure, mappings)
- Batch write operations (dry-run, batch processing, error tracking)
- CSV export (file creation, headers, empty results, status labels)
- Teams notifications (success, failure, template population, top violations)
- End-to-end integration smoke test

Run tests::

    pytest scripts/test_detect_agent_sharing_violations.py -v
"""

from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest
import requests

# Import functions under test
from detect_agent_sharing_violations import (
    _map_compliance_status_to_optionset,
    _map_violation_type_to_optionset,
    export_to_csv,
    send_teams_notification,
    upsert_compliance_record,
    write_compliance_results_to_dataverse,
)


# =========================================================================
# Test: Violation type mapping
# =========================================================================


def test_violation_type_mapping():
    """Test violation type string to option set integer mapping."""
    assert _map_violation_type_to_optionset("Everyone") == 0
    assert _map_violation_type_to_optionset("Public") == 1
    assert _map_violation_type_to_optionset("UnapprovedGroup") == 2
    assert _map_violation_type_to_optionset("ExcessiveIndividual") == 3
    assert _map_violation_type_to_optionset("CrossTenant") == 4
    assert _map_violation_type_to_optionset(None) is None
    assert _map_violation_type_to_optionset("Unknown") is None


def test_compliance_status_mapping():
    """Test compliance status string to option set integer mapping."""
    assert _map_compliance_status_to_optionset("Compliant") == 0
    assert _map_compliance_status_to_optionset("NonCompliant") == 1
    assert _map_compliance_status_to_optionset("Exception") == 2
    assert _map_compliance_status_to_optionset("Error") == 3
    assert _map_compliance_status_to_optionset("Unknown") == 3  # Default to Error


# =========================================================================
# Test: Dataverse upsert operations
# =========================================================================


def test_upsert_compliance_record_create():
    """Test upsert creates new record (HTTP 201)."""
    # Mock CAAClient
    mock_client = mock.MagicMock()
    mock_client.api_url = "https://org.crm.dynamics.com/api/data/v9.2"
    mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
    
    # Mock HTTP 201 (created)
    mock_response = mock.MagicMock()
    mock_response.status_code = 201
    mock_client._session.patch.return_value = mock_response
    
    # Sample record
    record = {
        "scan_run_id": "scan-123",
        "agent_id": "agent-456",
        "agent_name": "Test Agent",
        "environment_id": "env-789",
        "environment_name": "Test Environment",
        "zone": 2,
        "zone_name": "Team Collaboration",
        "sharing_principals_json": '[]',
        "evidence_hash": "abc123",
        "compliance_status": "Compliant",
        "violation_type": None,
        "details": "",
        "last_checked": "2024-01-01T00:00:00Z",
    }
    
    # Execute upsert
    result = upsert_compliance_record(mock_client, record)
    
    # Verify HTTP 201 returned as first element, no exception preserved
    assert result == ("201", False)
    
    # Verify PATCH called with alternate key
    mock_client._session.patch.assert_called_once()
    call_args = mock_client._session.patch.call_args
    assert "fsi_agent_id='agent-456'" in call_args[0][0]
    assert "fsi_environment_id='env-789'" in call_args[0][0]
    
    # Verify payload contains mapped values
    payload = call_args[1]["json"]
    assert payload["fsi_compliance_status"] == 0  # Compliant
    assert payload["fsi_violation_type"] is None


def test_upsert_compliance_record_update():
    """Test upsert updates existing record (HTTP 204)."""
    mock_client = mock.MagicMock()
    mock_client.api_url = "https://org.crm.dynamics.com/api/data/v9.2"
    mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
    
    # Mock HTTP 204 (no content, updated)
    mock_response = mock.MagicMock()
    mock_response.status_code = 204
    mock_client._session.patch.return_value = mock_response
    
    record = {
        "scan_run_id": "scan-123",
        "agent_id": "agent-456",
        "agent_name": "Test Agent",
        "environment_id": "env-789",
        "environment_name": "Test Environment",
        "zone": 3,
        "zone_name": "Enterprise Managed",
        "sharing_principals_json": '[]',
        "evidence_hash": "abc123",
        "compliance_status": "NonCompliant",
        "violation_type": "UnapprovedGroup",
        "details": "Group XYZ not in approved list",
        "last_checked": "2024-01-01T00:00:00Z",
    }
    
    result = upsert_compliance_record(mock_client, record)
    
    # Verify HTTP 204 returned as first element
    assert result == ("204", False)
    payload = mock_client._session.patch.call_args[1]["json"]
    assert payload["fsi_compliance_status"] == 1  # NonCompliant
    assert payload["fsi_violation_type"] == 2  # UnapprovedGroup


def test_upsert_compliance_record_failure():
    """Test upsert handles HTTP 500 gracefully."""
    mock_client = mock.MagicMock()
    mock_client.api_url = "https://org.crm.dynamics.com/api/data/v9.2"
    mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
    
    # Mock HTTP 500 (server error)
    mock_response = mock.MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    mock_client._session.patch.return_value = mock_response
    
    record = {
        "scan_run_id": "scan-123",
        "agent_id": "agent-456",
        "agent_name": "Test Agent",
        "environment_id": "env-789",
        "environment_name": "Test Environment",
        "zone": 0,
        "zone_name": "Unclassified",
        "sharing_principals_json": '[]',
        "evidence_hash": "abc123",
        "compliance_status": "Error",
        "violation_type": None,
        "details": "API failure",
        "last_checked": "2024-01-01T00:00:00Z",
    }
    
    result = upsert_compliance_record(mock_client, record)
    
    # Verify (None, False) returned on failure
    assert result == (None, False)


# =========================================================================
# Test: Batch Dataverse writes
# =========================================================================


def test_write_compliance_results_dry_run():
    """Test batch write skips API calls in dry-run mode."""
    mock_client = mock.MagicMock()
    
    results = [
        {
            "scan_run_id": "scan-123",
            "agent_id": "agent-1",
            "agent_name": "Agent 1",
            "environment_id": "env-1",
            "environment_name": "Env 1",
            "zone": 0,
            "compliance_status": "Compliant",
            "violation_type": None,
            "last_checked": "2024-01-01T00:00:00Z",
        },
        {
            "scan_run_id": "scan-123",
            "agent_id": "agent-2",
            "agent_name": "Agent 2",
            "environment_id": "env-2",
            "environment_name": "Env 2",
            "zone": 1,
            "compliance_status": "NonCompliant",
            "violation_type": "Everyone",
            "last_checked": "2024-01-01T00:00:00Z",
        },
    ]
    
    summary = write_compliance_results_to_dataverse(mock_client, results, dry_run=True)
    
    # Verify no API calls made
    mock_client._session.patch.assert_not_called()
    
    # Verify summary returns zero counts
    assert summary["upserted"] == 0
    assert summary["failed"] == 0


def test_write_compliance_results_batch():
    """Test batch write upserts N records."""
    mock_client = mock.MagicMock()
    mock_client.api_url = "https://org.crm.dynamics.com/api/data/v9.2"
    mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
    
    # Mock successful upserts (HTTP 204)
    mock_response = mock.MagicMock()
    mock_response.status_code = 204
    mock_client._session.patch.return_value = mock_response
    
    results = [
        {
            "scan_run_id": "scan-123",
            "agent_id": f"agent-{i}",
            "agent_name": f"Agent {i}",
            "environment_id": f"env-{i}",
            "environment_name": f"Env {i}",
            "zone": 0,
            "compliance_status": "Compliant",
            "violation_type": None,
            "last_checked": "2024-01-01T00:00:00Z",
        }
        for i in range(5)
    ]
    
    summary = write_compliance_results_to_dataverse(mock_client, results, dry_run=False)
    
    # Verify 5 PATCH calls made
    assert mock_client._session.patch.call_count == 5
    
    # Verify summary
    assert summary["upserted"] == 5
    assert summary["failed"] == 0


# =========================================================================
# Test: CSV export
# =========================================================================


def test_csv_export_creates_file():
    """Test CSV export creates file in output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = [
            {
                "scan_run_id": "scan-123",
                "agent_id": "agent-1",
                "agent_name": "Agent 1",
                "environment_id": "env-1",
                "environment_name": "Env 1",
                "zone": 2,
                "zone_name": "Team Collaboration",
                "compliance_status": "Compliant",
                "violation_type": None,
                "details": "",
                "sharing_principals_json": "[]",
                "evidence_hash": "abc123",
                "last_checked": "2024-01-01T00:00:00Z",
            }
        ]
        
        summary = {"scan_run_id": "scan-123"}
        
        csv_path = export_to_csv(results, summary, tmpdir)
        
        # Verify file exists
        assert Path(csv_path).exists()
        
        # Verify filename pattern
        assert "asard-scan-" in csv_path
        assert csv_path.endswith(".csv")


def test_csv_export_headers():
    """Test CSV export has correct column headers in order."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = [
            {
                "scan_run_id": "scan-123",
                "agent_id": "agent-1",
                "agent_name": "Agent 1",
                "environment_id": "env-1",
                "environment_name": "Env 1",
                "zone": 0,
                "zone_name": "Unclassified",
                "compliance_status": "Compliant",
                "violation_type": None,
                "details": "",
                "sharing_principals_json": "[]",
                "evidence_hash": "abc123",
                "last_checked": "2024-01-01T00:00:00Z",
            }
        ]
        
        summary = {"scan_run_id": "scan-123"}
        
        csv_path = export_to_csv(results, summary, tmpdir)
        
        # Read CSV and verify headers
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
        
        expected_headers = [
            "scan_run_id",
            "agent_id",
            "agent_name",
            "environment_id",
            "environment_name",
            "zone",
            "zone_name",
            "compliance_status",
            "violation_type",
            "details",
            "sharing_principals_json",
            "evidence_hash",
            "last_checked",
        ]
        
        assert headers == expected_headers


def test_csv_export_empty_results():
    """Test CSV export writes header-only if results empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = []
        summary = {"scan_run_id": "scan-123"}
        
        csv_path = export_to_csv(results, summary, tmpdir)
        
        # Verify file exists
        assert Path(csv_path).exists()
        
        # Verify only header row present
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == 1  # Header only


def test_csv_export_compliance_status_labels():
    """Test CSV export uses human-readable compliance status labels."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = [
            {
                "scan_run_id": "scan-123",
                "agent_id": "agent-1",
                "agent_name": "Agent 1",
                "environment_id": "env-1",
                "environment_name": "Env 1",
                "zone": 0,
                "zone_name": "Unclassified",
                "compliance_status": "Compliant",
                "violation_type": None,
                "details": "",
                "sharing_principals_json": "[]",
                "evidence_hash": "abc123",
                "last_checked": "2024-01-01T00:00:00Z",
            },
            {
                "scan_run_id": "scan-123",
                "agent_id": "agent-2",
                "agent_name": "Agent 2",
                "environment_id": "env-2",
                "environment_name": "Env 2",
                "zone": 1,
                "zone_name": "Personal Productivity",
                "compliance_status": "NonCompliant",
                "violation_type": "Everyone",
                "details": "Organization-wide sharing detected",
                "sharing_principals_json": "[]",
                "evidence_hash": "def456",
                "last_checked": "2024-01-01T00:00:00Z",
            },
        ]
        
        summary = {"scan_run_id": "scan-123"}
        
        csv_path = export_to_csv(results, summary, tmpdir)
        
        # Read CSV and verify status labels
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert rows[0]["compliance_status"] == "Compliant"
        assert rows[0]["violation_type"] == ""
        assert rows[1]["compliance_status"] == "NonCompliant"
        assert rows[1]["violation_type"] == "Everyone"


# =========================================================================
# Test: Teams notifications
# =========================================================================


def test_send_teams_notification_success():
    """Test Teams notification sends successfully (HTTP 200)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock adaptive card template
        card_template = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "{{non_compliant_count}} violations detected",
                }
            ],
        }
        
        template_path = Path(tmpdir) / "card-template.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(card_template, f)
        
        results = [
            {
                "agent_id": "agent-1",
                "agent_name": "Agent 1",
                "environment_name": "Env 1",
                "zone_name": "Team Collaboration",
                "compliance_status": "NonCompliant",
                "violation_type": "Everyone",
                "details": "Org-wide sharing",
                "last_checked": "2024-01-01T00:00:00Z",
            }
        ]
        
        summary = {
            "scan_run_id": "scan-123",
            "scan_started": "2024-01-01T00:00:00Z",
            "scan_completed": "2024-01-01T00:01:00Z",
            "total_agents": 1,
            "total_environments": 1,
            "compliant": 0,
            "non_compliant": 1,
            "exceptions": 0,
            "errors": 0,
        }
        
        # Mock requests.post (HTTP 200)
        with mock.patch("detect_agent_sharing_violations.requests.post") as mock_post:
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            result = send_teams_notification(
                "https://outlook.office.com/webhook/...",
                results,
                summary,
                str(template_path),
            )
            
            # Verify success
            assert result is True
            
            # Verify POST called once
            mock_post.assert_called_once()
            
            # Verify payload contains populated values
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            card_content = json.dumps(payload)
            assert "1 violations detected" in card_content  # Placeholder replaced


def test_send_teams_notification_failure():
    """Test Teams notification logs failure (HTTP 500) but doesn't raise."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_template = {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [],
        }
        
        template_path = Path(tmpdir) / "card-template.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(card_template, f)
        
        results = []
        summary = {
            "scan_run_id": "scan-123",
            "scan_started": "2024-01-01T00:00:00Z",
            "scan_completed": "2024-01-01T00:01:00Z",
            "total_agents": 0,
            "total_environments": 0,
            "compliant": 0,
            "non_compliant": 0,
            "exceptions": 0,
            "errors": 0,
        }
        
        # Mock requests.post (HTTP 500)
        with mock.patch("detect_agent_sharing_violations.requests.post") as mock_post:
            mock_response = mock.MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.return_value = mock_response
            
            result = send_teams_notification(
                "https://outlook.office.com/webhook/...",
                results,
                summary,
                str(template_path),
            )
            
            # Verify failure returned but no exception raised
            assert result is False


def test_teams_card_template_population():
    """Test adaptive card template placeholders replaced with actual values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_template = {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "Scan ID: {{scan_run_id}}",
                },
                {
                    "type": "TextBlock",
                    "text": "Total: {{total_agents}}, Non-compliant: {{non_compliant_count}}",
                },
            ],
        }
        
        template_path = Path(tmpdir) / "card-template.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(card_template, f)
        
        results = []
        summary = {
            "scan_run_id": "abc-123-def",
            "scan_started": "2024-01-01T00:00:00Z",
            "scan_completed": "2024-01-01T00:01:00Z",
            "total_agents": 42,
            "total_environments": 5,
            "compliant": 40,
            "non_compliant": 2,
            "exceptions": 0,
            "errors": 0,
        }
        
        with mock.patch("detect_agent_sharing_violations.requests.post") as mock_post:
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            send_teams_notification(
                "https://outlook.office.com/webhook/...",
                results,
                summary,
                str(template_path),
            )
            
            # Verify placeholders replaced
            payload = mock_post.call_args[1]["json"]
            card_json = json.dumps(payload)
            
            assert "abc-123-def" in card_json
            assert "42" in card_json
            assert "2" in card_json


def test_teams_notification_top_5_violations():
    """Test Teams notification includes only top 5 violations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_template = {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "{{violation_list}}",
                }
            ],
        }
        
        template_path = Path(tmpdir) / "card-template.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(card_template, f)
        
        # Create 10 violations (should only show top 5)
        results = [
            {
                "agent_id": f"agent-{i}",
                "agent_name": f"Agent {i}",
                "environment_name": f"Env {i}",
                "zone_name": "Team Collaboration",
                "compliance_status": "NonCompliant",
                "violation_type": "Everyone",
                "details": f"Violation {i}",
                "last_checked": "2024-01-01T00:00:00Z",
            }
            for i in range(10)
        ]
        
        summary = {
            "scan_run_id": "scan-123",
            "scan_started": "2024-01-01T00:00:00Z",
            "scan_completed": "2024-01-01T00:01:00Z",
            "total_agents": 10,
            "total_environments": 1,
            "compliant": 0,
            "non_compliant": 10,
            "exceptions": 0,
            "errors": 0,
        }
        
        with mock.patch("detect_agent_sharing_violations.requests.post") as mock_post:
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            send_teams_notification(
                "https://outlook.office.com/webhook/...",
                results,
                summary,
                str(template_path),
            )
            
            # Verify only 5 violations in list
            payload = mock_post.call_args[1]["json"]
            card_json = json.dumps(payload)
            
            # Should contain Agent 0-4, not Agent 5-9
            assert "Agent 0" in card_json
            assert "Agent 4" in card_json
            assert "Agent 9" not in card_json


# =========================================================================
# Test: End-to-end integration
# =========================================================================


def test_e2e_detection_dry_run():
    """Test end-to-end detection scan in dry-run mode."""
    # This is a smoke test to verify all components integrate correctly
    # Uses mocks for external dependencies (BAP API, Dataverse, file I/O)
    
    # Mock BAP client responses
    mock_bap_client = mock.MagicMock()
    mock_bap_client.list_environments.return_value = [
        {
            "name": "env-123",
            "properties": {"displayName": "Test Environment"},
        }
    ]
    mock_bap_client.list_agents.return_value = [
        {
            "name": "agent-456",
            "properties": {"displayName": "Test Agent"},
        }
    ]
    mock_bap_client.get_agent_permissions.return_value = [
        {"type": "user", "id": "user-789"}
    ]
    
    # Mock CAA client responses
    mock_caa_client = mock.MagicMock()
    mock_caa_client.query.return_value = [
        {"fsi_zone": 2}  # Zone 2: Team Collaboration
    ]
    
    # Mock check_agent_compliance response
    with mock.patch("detect_agent_sharing_violations.check_agent_compliance") as mock_check:
        mock_check.return_value = {
            "agent_id": "agent-456",
            "environment_id": "env-123",
            "zone": 2,
            "zone_name": "Team Collaboration",
            "compliant": True,
            "violation_type": None,
            "details": "",
        }
        
        # Import and run detection workflow
        from detect_agent_sharing_violations import run_detection_scan
        
        results, summary = run_detection_scan(
            mock_bap_client,
            mock_caa_client,
            environment_filter=None,
        )
        
        # Verify results structure
        assert len(results) == 1
        assert results[0]["agent_id"] == "agent-456"
        assert results[0]["compliance_status"] == "Compliant"
        
        # Verify summary statistics
        assert summary["total_environments"] == 1
        assert summary["total_agents"] == 1
        assert summary["compliant"] == 1
        assert summary["non_compliant"] == 0
        assert summary["errors"] == 0
        
        # Verify scan_run_id is UUID format
        assert len(summary["scan_run_id"]) == 36  # UUID format
        assert "-" in summary["scan_run_id"]


# =========================================================================
# Test: Exception handling (Phase 4)
# =========================================================================


def test_upsert_compliance_record_with_active_exception():
    """Test that upsert preserves active exceptions and sets compliance_status=2."""
    mock_caa_client = mock.MagicMock()
    
    # Mock existing record with active exception
    existing_record = {
        "fsi_compliance_status": 2,  # Exception
        "fsi_exception_expires_at": "2026-12-31T00:00:00Z",  # Future date
        "fsi_exception_justification": "Test justification",
        "fsi_exception_approved_by": "Test Approver",
        "fsi_exception_approved_at": "2026-01-01T00:00:00Z",
        "fsi_exception_review_date": "2026-06-01T00:00:00Z",
    }
    
    # Mock GET request to return existing record
    mock_get_response = mock.MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = existing_record
    
    # Mock PATCH request for upsert
    mock_patch_response = mock.MagicMock()
    mock_patch_response.status_code = 204
    
    mock_caa_client._session.get.return_value = mock_get_response
    mock_caa_client._session.patch.return_value = mock_patch_response
    mock_caa_client._get_headers.return_value = {"Authorization": "Bearer test"}
    mock_caa_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    
    # Record that would normally be NonCompliant
    record = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Test Environment",
        "compliance_status": "NonCompliant",  # Would be non-compliant without exception
        "violation_type": "Everyone",
        "zone": 2,
        "last_checked": "2026-02-13T10:00:00Z",
        "scan_run_id": "scan-789",
        "evidence_hash": "abc123",
        "sharing_principals_json": "[]",
    }
    
    # Call upsert
    result = upsert_compliance_record(mock_caa_client, record)
    
    # Verify PATCH was called
    assert result == ("204", True)
    patch_call = mock_caa_client._session.patch.call_args
    payload = patch_call[1]["json"]
    
    assert payload["fsi_compliance_status"] == 2  # Exception, not NonCompliant
    assert payload["fsi_exception_expires_at"] == "2026-12-31T00:00:00Z"
    assert payload["fsi_exception_justification"] == "Test justification"
    assert payload["fsi_exception_approved_by"] == "Test Approver"


def test_upsert_compliance_record_with_expired_exception():
    """Test that upsert does NOT preserve expired exceptions."""
    mock_caa_client = mock.MagicMock()
    
    # Mock existing record with EXPIRED exception
    existing_record = {
        "fsi_compliance_status": 2,  # Exception
        "fsi_exception_expires_at": "2020-01-01T00:00:00Z",  # Past date
        "fsi_exception_justification": "Test justification",
        "fsi_exception_approved_by": "Test Approver",
    }
    
    # Mock GET request to return existing record
    mock_get_response = mock.MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = existing_record
    
    # Mock PATCH request for upsert
    mock_patch_response = mock.MagicMock()
    mock_patch_response.status_code = 204
    
    mock_caa_client._session.get.return_value = mock_get_response
    mock_caa_client._session.patch.return_value = mock_patch_response
    mock_caa_client._get_headers.return_value = {"Authorization": "Bearer test"}
    mock_caa_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    
    # Record that would be NonCompliant
    record = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Test Environment",
        "compliance_status": "NonCompliant",
        "violation_type": "Everyone",
        "zone": 2,
        "last_checked": "2026-02-13T10:00:00Z",
        "scan_run_id": "scan-789",
        "evidence_hash": "abc123",
        "sharing_principals_json": "[]",
    }
    
    # Call upsert
    result = upsert_compliance_record(mock_caa_client, record)
    
    # Verify PATCH was called
    assert result == ("204", False)
    patch_call = mock_caa_client._session.patch.call_args
    payload = patch_call[1]["json"]
    
    assert payload["fsi_compliance_status"] == 1  # NonCompliant, not Exception
    assert "fsi_exception_expires_at" not in payload or payload.get("fsi_exception_expires_at") is None


def test_upsert_compliance_record_no_existing_exception():
    """Test that upsert works normally when no existing exception."""
    mock_caa_client = mock.MagicMock()
    
    # Mock GET request returns 404 (no existing record)
    mock_get_response = mock.MagicMock()
    mock_get_response.status_code = 404
    
    # Mock PATCH request for upsert (creates new record)
    mock_patch_response = mock.MagicMock()
    mock_patch_response.status_code = 201
    
    mock_caa_client._session.get.return_value = mock_get_response
    mock_caa_client._session.patch.return_value = mock_patch_response
    mock_caa_client._get_headers.return_value = {"Authorization": "Bearer test"}
    mock_caa_client.api_url = "https://test.crm.dynamics.com/api/data/v9.2"
    
    # Record that is NonCompliant
    record = {
        "agent_id": "agent-123",
        "agent_name": "Test Agent",
        "environment_id": "env-456",
        "environment_name": "Test Environment",
        "compliance_status": "NonCompliant",
        "violation_type": "Everyone",
        "zone": 2,
        "last_checked": "2026-02-13T10:00:00Z",
        "scan_run_id": "scan-789",
        "evidence_hash": "abc123",
        "sharing_principals_json": "[]",
    }
    
    # Call upsert
    result = upsert_compliance_record(mock_caa_client, record)
    
    # Verify PATCH was called
    assert result == ("201", False)
    patch_call = mock_caa_client._session.patch.call_args
    payload = patch_call[1]["json"]
    
    assert payload["fsi_compliance_status"] == 1  # NonCompliant
    assert "fsi_exception_expires_at" not in payload or payload.get("fsi_exception_expires_at") is None

