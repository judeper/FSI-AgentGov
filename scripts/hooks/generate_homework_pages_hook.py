"""MkDocs hook — generate per-role homework pages before build.

Runs during ``mkdocs build`` / ``mkdocs serve``. Calls the homework page
generator to create one page per role under ``docs/assessment/pre-session/``.

Wire-up in ``mkdocs.yml``::

    hooks:
      - scripts/hooks/generate_homework_pages_hook.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add scripts to path so we can import the generator
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from generate_homework_pages import generate_all_homework_pages

log = logging.getLogger("mkdocs.generate_homework_pages_hook")


def on_pre_build(config, **_kwargs):
    """Generate homework pages before MkDocs starts building."""
    log.info("generate_homework_pages_hook: generating per-role homework pages...")
    
    try:
        role_stats = generate_all_homework_pages()
        log.info(
            f"generate_homework_pages_hook: generated {len(role_stats)} pages "
            f"for {sum(role_stats.values())} control assignments"
        )
    except Exception as e:
        log.error(f"generate_homework_pages_hook: failed: {e}", exc_info=True)
        raise
