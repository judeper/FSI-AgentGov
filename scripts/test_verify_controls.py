"""Focused tests for the documented control footer contract."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_controls  # noqa: E402


def _control_with_footer(footer: str) -> str:
    headings = "\n\n".join(verify_controls.REQUIRED_HEADINGS)
    return f"""# Control 1.1: Test Control

**Control ID:** 1.1
**Pillar:** Security
**Regulatory Reference:** Test

{headings}

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
