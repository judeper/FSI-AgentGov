"""Tests for autodoc retry/escalation decisions."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_retry as retry  # noqa: E402


@pytest.mark.parametrize(
    ("attempts", "max_cycles", "conclusion", "expected_action", "expected_next", "reason_fragment"),
    [
        (0, 2, "needs_human", "escalate", 1, "human judgment"),
        (0, 2, "fail", "retry", 1, "retry limit not reached"),
        (2, 2, "fail", "escalate", 3, "retry limit reached"),
        (0, 2, "cancelled", "escalate", 1, "not auto-retryable"),
        (0, 2, "", "escalate", 1, "unknown"),
    ],
)
def test_decide_matrix(
    attempts: int,
    max_cycles: int,
    conclusion: str,
    expected_action: str,
    expected_next: int,
    reason_fragment: str,
) -> None:
    decision = retry.decide(attempts, max_cycles, conclusion)

    assert decision["action"] == expected_action
    assert decision["next_attempt"] == expected_next
    assert reason_fragment in str(decision["reason"])


def test_count_attempts_from_sample_comments() -> None:
    comments = [
        "First human comment with no marker.",
        "### Autodoc fix retry requested\n\nAUTODOC-RETRY: 1/2\n\nPlease fix.",
        "not a marker: AUTODOC-RETRY 2/2",
        "AUTODOC-RETRY: 2 / 2\nTrailing body.",
        "Indented marker is still a marker.\n  autodoc-retry: 3/3",
    ]

    assert retry.count_attempts(comments) == 3


def test_built_retry_comment_has_marker_summary_and_constraints() -> None:
    comment = retry.build_retry_comment(1, 2, "path_allowlist failed")

    assert "AUTODOC-RETRY: 1/2" in comment
    assert "path_allowlist failed" in comment
    assert "AUTODOC-FINGERPRINT" in comment
    assert "allowed_files" in comment
    assert "Do not advance any baseline" in comment


def test_built_escalation_comment_explains_reason() -> None:
    comment = retry.build_escalation_comment(2, "retry limit reached (2/2)")

    assert "Autodoc escalated to human review" in comment
    assert "Prior retry attempts: 2" in comment
    assert "retry limit reached (2/2)" in comment
    assert "No baseline was advanced" in comment
