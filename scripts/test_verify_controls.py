"""Focused tests for the documented control footer contract."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_controls  # noqa: E402


def _control_with_footer(
    footer: str,
    last_ui_verified: str | None = "**Last UI Verified:** May 2026",
    body: str = "",
) -> str:
    headings = "\n\n".join(verify_controls.REQUIRED_HEADINGS)
    verification_metadata = (
        f"{last_ui_verified}\n" if last_ui_verified is not None else ""
    )
    body_content = f"\n\n{body}" if body else ""
    return f"""# Control 1.1: Test Control

**Control ID:** 1.1
**Pillar:** Security
**Regulatory Reference:** Test
{verification_metadata}

{headings}{body_content}

---

{footer}
"""


def test_historical_update_date_remains_valid_footer_metadata(tmp_path: Path) -> None:
    """May footers must not expire merely because the calendar reached August."""
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*"
        ),
        encoding="utf-8",
    )

    assert verify_controls.validate_control_file(control) == []


def test_missing_last_ui_verified_metadata_is_rejected(tmp_path: Path) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*",
            last_ui_verified=None,
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("Last UI Verified metadata" in failure for failure in failures)


def test_body_decoy_does_not_replace_missing_header_verification_metadata(
    tmp_path: Path,
) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*",
            last_ui_verified=None,
            body="Example only:\n\n**Last UI Verified:** May 2026",
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("Last UI Verified metadata" in failure for failure in failures)


def test_body_decoy_does_not_replace_invalid_header_verification_metadata(
    tmp_path: Path,
) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*",
            last_ui_verified="**Last UI Verified:** 2026-05",
            body="Example only:\n\n**Last UI Verified:** May 2026",
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("Last UI Verified metadata" in failure for failure in failures)


def test_malformed_last_ui_verified_date_is_rejected(tmp_path: Path) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*",
            last_ui_verified="**Last UI Verified:** 2026-05",
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("Last UI Verified metadata" in failure for failure in failures)


def test_invalid_ui_verification_status_is_rejected(tmp_path: Path) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Verified*"
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("invalid UI Verification Status" in failure for failure in failures)


def test_body_decoy_does_not_replace_missing_end_of_document_footer(
    tmp_path: Path,
) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "Footer intentionally missing.",
            body=(
                "Example only:\n\n"
                "*Updated: May 2026 | Version: v1.6.2 | "
                "UI Verification Status: Current*"
            ),
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("canonical update date footer" in failure for failure in failures)


def test_body_decoy_does_not_mask_invalid_actual_footer(tmp_path: Path) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Verified*",
            body=(
                "Example only:\n\n"
                "*Updated: May 2026 | Version: v1.6.2 | "
                "UI Verification Status: Current*"
            ),
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("invalid UI Verification Status" in failure for failure in failures)


def test_body_version_decoy_does_not_mask_invalid_footer_version(
    tmp_path: Path,
) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v9.9.9 | UI Verification Status: Current*",
            body="Example narrative containing Version: v1.6.2.",
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("invalid canonical version in footer" in failure for failure in failures)


def test_later_body_title_and_metadata_cannot_masquerade_as_header(
    tmp_path: Path,
) -> None:
    control = tmp_path / "1.1-test-control.md"
    decoy_control = _control_with_footer(
        "*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*"
    )
    control.write_text(
        "---\ndescription: Not a control page\n---\n"
        "# Overview\n\nIntroductory body prose.\n\n"
        f"{decoy_control}",
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("control title" in failure for failure in failures)
    assert any("Last UI Verified metadata" in failure for failure in failures)


def test_documented_ui_verification_status_detail_is_allowed(tmp_path: Path) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: May 2026 | Version: v1.6.2 | "
            "UI Verification Status: Needs Review — portal labels require re-check*"
        ),
        encoding="utf-8",
    )

    assert verify_controls.validate_control_file(control) == []


def test_update_date_text_outside_canonical_footer_does_not_satisfy_contract(
    tmp_path: Path,
) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Version: v1.6.2 | UI Verification Status: Current*\n\n"
            "Updated: May 2026"
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("canonical update date footer" in failure for failure in failures)


def test_invalid_month_name_is_rejected_in_footer(tmp_path: Path) -> None:
    control = tmp_path / "1.1-test-control.md"
    control.write_text(
        _control_with_footer(
            "*Updated: Smarch 2026 | Version: v1.6.2 | UI Verification Status: Current*"
        ),
        encoding="utf-8",
    )

    failures = verify_controls.validate_control_file(control)

    assert any("canonical update date footer" in failure for failure in failures)
