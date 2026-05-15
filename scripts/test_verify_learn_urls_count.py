"""Tests for verify_learn_urls_count.py."""

from __future__ import annotations

import textwrap
from pathlib import Path

import verify_learn_urls_count as vluc

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_file(tmp_path: Path, actual_count: int, header_n: int, footer_n: int) -> Path:
    """Write a minimal urls-file fixture with the requested counts."""
    urls = "\n".join(
        f"https://learn.microsoft.com/en-us/example/{i}" for i in range(actual_count)
    )
    content = textwrap.dedent(f"""\
        # Microsoft Learn Documentation URLs

        - **Total URLs Tracked:** ~{header_n} (Learn URLs only)

        ---

        {urls}

        ---

        *Last Updated: May 2026*
        *Total URLs Tracked: ~{footer_n}*
        *Note: Microsoft documentation URLs may change.*
    """)
    p = tmp_path / "microsoft-learn-urls.md"
    p.write_text(content, encoding="utf-8")
    return p


def _run(monkeypatch, tmp_path, actual: int, header: int, footer: int) -> int:
    """Patch URLS_FILE and run vluc.main()."""

    p = _make_file(tmp_path, actual, header, footer)
    monkeypatch.setattr(vluc, "URLS_FILE", p)
    return vluc.main(["--check"])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSyncedState:
    """header == footer == actual ± vluc.TOLERANCE → PASS."""

    def test_exact_match(self, monkeypatch, tmp_path):
        assert _run(monkeypatch, tmp_path, actual=229, header=229, footer=229) == 0

    def test_within_tolerance(self, monkeypatch, tmp_path):
        assert _run(monkeypatch, tmp_path, actual=229, header=229 + vluc.TOLERANCE, footer=229 + vluc.TOLERANCE) == 0

    def test_at_tolerance_boundary(self, monkeypatch, tmp_path):
        assert _run(monkeypatch, tmp_path, actual=229, header=229 - vluc.TOLERANCE, footer=229 - vluc.TOLERANCE) == 0


class TestHeaderDrift:
    """Header prose number drifts > vluc.TOLERANCE from actual → FAIL."""

    def test_header_too_high(self, monkeypatch, tmp_path):
        assert _run(monkeypatch, tmp_path, actual=229, header=229 + vluc.TOLERANCE + 1, footer=229 + vluc.TOLERANCE + 1) == 1

    def test_header_too_low(self, monkeypatch, tmp_path):
        assert _run(monkeypatch, tmp_path, actual=229, header=209, footer=209) == 1


class TestFooterDrift:
    """Footer prose number drifts > vluc.TOLERANCE from actual → FAIL."""

    def test_footer_too_high(self, monkeypatch, tmp_path):
        assert _run(monkeypatch, tmp_path, actual=100, header=100, footer=150) == 1

    def test_footer_too_low(self, monkeypatch, tmp_path):
        assert _run(monkeypatch, tmp_path, actual=100, header=100, footer=50) == 1


class TestHeaderFooterDisagreement:
    """Header and footer disagree → FAIL, even if both are plausible."""

    def test_header_footer_mismatch(self, monkeypatch, tmp_path):
        # Both within tolerance of actual but differ from each other
        assert _run(monkeypatch, tmp_path, actual=229, header=229, footer=222) == 1

    def test_original_stale_values(self, monkeypatch, tmp_path):
        # Reproduces the exact pre-fix state: header=222, footer=209, actual=229
        assert _run(monkeypatch, tmp_path, actual=229, header=222, footer=209) == 1


class TestFileMissing:
    """File missing → FAIL with a clear message (exit 1)."""

    def test_missing_file(self, monkeypatch, tmp_path):

        monkeypatch.setattr(vluc, "URLS_FILE", tmp_path / "nonexistent.md")
        assert vluc.main(["--check"]) == 1
