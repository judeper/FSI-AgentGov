"""Unit test stubs for asard_zone_rules module.

Expand in Phase 2 detection testing.

These tests validate zone rules configuration, zone classification,
sharing principal parsing, and compliance evaluation logic without
requiring a live Dataverse connection.
"""

from __future__ import annotations

import json
from unittest import mock

from asard_zone_rules import (
    ZONE_SHARING_RULES,
    check_agent_compliance,
    classify_environment_zone,
    evaluate_zone_compliance,
    parse_sharing_principals,
)

# =========================================================================
# Zone rules configuration tests
# =========================================================================


class TestZoneSharingRules:
    """Verify zone rule definitions are correct."""

    def test_zone_1_no_group_sharing(self):
        rules = ZONE_SHARING_RULES[1]
        assert rules["allow_individual_sharing"] is True
        assert rules["allow_group_sharing"] is False
        assert rules["allow_everyone"] is False
        assert rules["allow_public"] is False

    def test_zone_2_named_groups_allowed(self):
        rules = ZONE_SHARING_RULES[2]
        assert rules["allow_individual_sharing"] is True
        assert rules["allow_group_sharing"] is True
        assert rules["allow_everyone"] is False
        assert rules["allow_public"] is False
        assert rules["require_approved_groups"] is False

    def test_zone_3_approved_groups_only(self):
        rules = ZONE_SHARING_RULES[3]
        assert rules["allow_individual_sharing"] is False
        assert rules["allow_group_sharing"] is True
        assert rules["allow_everyone"] is False
        assert rules["require_approved_groups"] is True

    def test_zone_0_safe_fallback(self):
        rules = ZONE_SHARING_RULES[0]
        assert rules["allow_everyone"] is False
        assert rules["allow_public"] is False


# =========================================================================
# Zone classification tests
# =========================================================================


class TestClassifyEnvironmentZone:
    """Verify zone classification via naming conventions."""

    def test_production_returns_zone_3(self):
        assert classify_environment_zone("env-1", "Production-Finance") == 3

    def test_enterprise_returns_zone_3(self):
        assert classify_environment_zone("env-2", "Enterprise Main") == 3

    def test_test_returns_zone_2(self):
        assert classify_environment_zone("env-3", "QA-Testing") == 2

    def test_staging_returns_zone_2(self):
        assert classify_environment_zone("env-4", "Staging Environment") == 2

    def test_dev_returns_zone_1(self):
        assert classify_environment_zone("env-5", "Dev Sandbox") == 1

    def test_sandbox_returns_zone_1(self):
        assert classify_environment_zone("env-6", "Personal Sandbox") == 1

    def test_unknown_returns_default(self):
        assert classify_environment_zone("env-7", "MyCustomEnv") == 0

    def test_case_insensitive(self):
        assert classify_environment_zone("env-8", "PRODUCTION") == 3

    def test_no_client_skips_lookup(self):
        # Should not raise when client=None
        result = classify_environment_zone("env-9", "Production", client=None)
        assert result == 3

    def test_policy_lookup_uses_deployed_logical_names_and_overrides_name(self):
        client = mock.MagicMock()
        client.query.return_value = [{"fsi_zone": 1}]

        result = classify_environment_zone(
            "env-9",
            "Production",
            client=client,
        )

        assert result == 1
        client.query.assert_called_once_with(
            "fsi_environmentpolicies",
            filter="fsi_environmentid eq 'env-9'",
            select=["fsi_zone"],
            top=1,
        )


# =========================================================================
# Sharing principal parsing tests
# =========================================================================


class TestParseSharingPrincipals:
    """Verify sharing principal JSON parsing."""

    def test_empty_string(self):
        result = parse_sharing_principals("")
        assert result["individuals"] == []
        assert result["security_groups"] == []
        assert result["has_everyone"] is False

    def test_malformed_json(self):
        result = parse_sharing_principals("{bad json}")
        assert result["individuals"] == []

    def test_everyone_detected(self):
        principals = json.dumps([{"type": "Everyone", "id": "all"}])
        result = parse_sharing_principals(principals)
        assert result["has_everyone"] is True

    def test_public_detected(self):
        principals = json.dumps([{"type": "Public", "id": "pub"}])
        result = parse_sharing_principals(principals)
        assert result["has_public"] is True

    def test_security_group_extracted(self):
        principals = json.dumps([
            {"type": "group", "id": "group-abc-123", "displayName": "Finance Team"}
        ])
        result = parse_sharing_principals(principals)
        assert "group-abc-123" in result["security_groups"]

    def test_individual_extracted(self):
        principals = json.dumps([
            {"type": "user", "id": "user@contoso.com"}
        ])
        result = parse_sharing_principals(principals)
        assert "user@contoso.com" in result["individuals"]


# =========================================================================
# Zone compliance evaluation tests
# =========================================================================


class TestEvaluateZoneCompliance:
    """Verify compliance evaluation per zone."""

    def test_zone_1_individual_compliant(self):
        parsed = {"individuals": ["user1"], "security_groups": [], "has_everyone": False, "has_public": False, "has_organization": False}
        result = evaluate_zone_compliance(1, parsed)
        assert result["compliant"] is True

    def test_zone_1_group_noncompliant(self):
        parsed = {"individuals": [], "security_groups": ["group-1"], "has_everyone": False, "has_public": False, "has_organization": False}
        result = evaluate_zone_compliance(1, parsed)
        assert result["compliant"] is False
        assert result["violation_type"] == "UnapprovedGroup"

    def test_zone_2_named_groups_compliant(self):
        parsed = {"individuals": ["user1"], "security_groups": ["group-1"], "has_everyone": False, "has_public": False, "has_organization": False}
        result = evaluate_zone_compliance(2, parsed)
        assert result["compliant"] is True

    def test_zone_2_everyone_noncompliant(self):
        parsed = {"individuals": [], "security_groups": [], "has_everyone": True, "has_public": False, "has_organization": False}
        result = evaluate_zone_compliance(2, parsed)
        assert result["compliant"] is False
        assert result["violation_type"] == "Everyone"

    def test_zone_3_approved_groups_compliant(self):
        parsed = {"individuals": [], "security_groups": ["group-a"], "has_everyone": False, "has_public": False, "has_organization": False}
        result = evaluate_zone_compliance(3, parsed, approved_groups=["group-a"])
        assert result["compliant"] is True

    def test_zone_3_unapproved_groups_noncompliant(self):
        parsed = {"individuals": [], "security_groups": ["group-x"], "has_everyone": False, "has_public": False, "has_organization": False}
        result = evaluate_zone_compliance(3, parsed, approved_groups=["group-a"])
        assert result["compliant"] is False
        assert result["violation_type"] == "UnapprovedGroup"

    def test_zone_3_individual_noncompliant(self):
        parsed = {"individuals": ["user1"], "security_groups": [], "has_everyone": False, "has_public": False, "has_organization": False}
        result = evaluate_zone_compliance(3, parsed, approved_groups=[])
        assert result["compliant"] is False
        assert result["violation_type"] == "ExcessiveIndividual"


# =========================================================================
# End-to-end compliance check tests
# =========================================================================


class TestCheckAgentCompliance:
    """Verify end-to-end compliance orchestration."""

    def test_compliant_zone_1_individual(self):
        principals = json.dumps([{"type": "user", "id": "user@contoso.com"}])
        result = check_agent_compliance(
            agent_id="agent-1",
            environment_id="env-1",
            environment_name="Dev Sandbox",
            sharing_principals_json=principals,
        )
        assert result["compliant"] is True
        assert result["zone"] == 1

    def test_noncompliant_zone_2_everyone(self):
        principals = json.dumps([{"type": "Everyone", "id": "all"}])
        result = check_agent_compliance(
            agent_id="agent-2",
            environment_id="env-2",
            environment_name="QA Testing",
            sharing_principals_json=principals,
        )
        assert result["compliant"] is False
        assert result["violation_type"] == "Everyone"
        assert result["zone"] == 2

    def test_error_handling(self):
        # Malformed JSON should not raise — returns Error violation
        result = check_agent_compliance(
            agent_id="agent-3",
            environment_id="env-3",
            environment_name="Production",
            sharing_principals_json="",
        )
        # Empty principals = compliant (no violations detected)
        assert result["zone"] == 3
