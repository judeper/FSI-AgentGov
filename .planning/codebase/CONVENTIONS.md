# Coding Conventions

**Analysis Date:** 2026-02-02

## Naming Patterns

**Files:**
- Lowercase with hyphens: `learn_monitor.py`, `verify_controls.py`, `compile_researcher_package.py`
- Hook files in `scripts/hooks/`: `boundary-check.py`, `researcher-package-reminder.py`
- Control files: `{pillar}-{number}-{control-name}.md` (e.g., `1.1-restrict-agent-publishing-by-authorization.md`)
- Markdown playbooks: `portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md`

**Functions:**
- Snake case throughout: `setup_logging()`, `parse_watchlist()`, `fetch_page()`, `validate_control_file()`
- Private functions prefixed with underscore: `_debug_single_url()`, `_format_change()`, `_slugify_heading()`
- Descriptive names with action verbs: `extract_main_content()`, `classify_change()`, `determine_priority()`

**Variables:**
- Snake case for all variables: `url_entries`, `control_files`, `content_hash`, `state_file_path`
- Constants in UPPERCASE: `REQUEST_TIMEOUT`, `MAX_RETRIES`, `DOCS_DIR`, `STATE_FILE_PATH`
- Private/internal constants use underscore prefix: `_LEGACY_MARKER_PATTERNS`, `_REQUIRED_METADATA_FIELDS`

**Types:**
- Type hints used throughout: `def fetch_page(url: str, session: requests.Session) -> FetchResult`
- Dataclasses for structured data: `@dataclass URLEntry`, `@dataclass ChangeRecord`, `@dataclass FetchResult`
- Optional types: `Optional[str]`, `Optional[Path]`, `Optional[dict]`

## Code Style

**Formatting:**
- Black-compatible style (implicit, no formatter configured)
- 4-space indentation
- Line length typically under 100 characters
- Docstring format: Module-level docstrings at top with triple quotes

**Linting:**
- No explicit linting configuration found
- Code follows PEP 8 conventions implicitly
- Windows encoding safety: `if sys.platform == 'win32': sys.stdout.reconfigure(encoding='utf-8')`

## Import Organization

**Order:**
1. Standard library imports (os, sys, re, pathlib, etc.)
2. Third-party imports (requests, beautifulsoup4)
3. Relative imports (none in current codebase)

**Path Aliases:**
- Absolute paths constructed with `Path(__file__).parent` for cross-platform safety
- Dynamic project root detection: `SCRIPT_DIR = Path(__file__).parent` and `PROJECT_ROOT = SCRIPT_DIR.parent`
- Example from `learn_monitor.py` (lines 78-84):
```python
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DOCS_DIR = PROJECT_ROOT / "docs"
WATCHLIST_PATH = DOCS_DIR / "reference" / "microsoft-learn-urls.md"
STATE_FILE_PATH = PROJECT_ROOT / "data" / "learn-monitor-state.json"
```

**No relative imports** - All paths use `Path` objects for platform independence.

## Error Handling

**Patterns:**
- Try/except for expected exceptions with specific error handling
- File I/O wrapped in try/except: `try: json.loads(...) except json.JSONDecodeError`
- Exception chaining with `logger.debug(traceback.format_exc())` for full stack traces
- Fail-safe defaults: Corrupt JSON state files restart fresh rather than crash
- Network errors caught with retry logic: `except requests.RequestException as e` with exponential backoff

**Example from `learn_monitor.py` (lines 172-211) - Retry pattern:**
```python
for attempt in range(MAX_RETRIES):
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", 60))
            time.sleep(wait_time)
            continue
        return FetchResult(...)
    except requests.RequestException as e:
        if attempt == MAX_RETRIES - 1:
            return FetchResult(error=str(e))
        time.sleep(2 ** attempt)
```

**Exit codes:** Scripts use meaningful exit codes (0=success, 1=meaningful changes/failures, 2=errors)

## Logging

**Framework:** Python's built-in `logging` module

**Patterns:**
- Configuration at module start with `setup_logging(verbose, debug)`
- Log level controlled by flags: `--verbose` (INFO), `--debug` (DEBUG), default WARNING
- Environment variable override: `LEARN_MONITOR_DEBUG=1`
- Log format: `"%(asctime)s [%(levelname)s] %(message)s"`
- Logger instance: `logger = logging.getLogger(__name__)` after setup

**Example from `learn_monitor.py` (lines 45-59):**
```python
def setup_logging(verbose: bool = False, debug: bool = False) -> logging.Logger:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    if os.environ.get("LEARN_MONITOR_DEBUG", "").lower() in ("1", "true", "yes"):
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)
```

## Comments

**When to Comment:**
- Complex regex patterns documented inline
- Algorithm explanations before major logic blocks
- Workaround notes for platform-specific issues (Windows encoding)
- References to external standards or design patterns

**JSDoc/TSDoc:**
- Not used (Python codebase)
- Docstrings use triple quotes for module and class documentation
- Function signatures have type hints instead of docstrings

**Example - Complex algorithm comment from `learn_monitor.py` (lines 250-254):**
```python
def classify_change(old_text: str, new_text: str) -> tuple[str, str, str]:
    """
    Classify change and generate diff.
    Returns (classification, reason, diff_text)
    """
```

## Function Design

**Size:**
- Small, focused functions: 10-40 lines typical
- Single responsibility: `fetch_page()` fetches only, `extract_main_content()` extracts only
- Long workflows broken into steps: `_run_monitor()` orchestrates smaller functions

**Parameters:**
- Explicit parameters over magic numbers
- Type hints required for all parameters
- Reasonable limits: max 4-5 parameters, use dataclasses for complex inputs
- Examples: `fetch_page(url: str, session: requests.Session) -> FetchResult`

**Return Values:**
- Explicit return types with type hints
- Dataclasses used for structured returns: `ChangeRecord`, `FetchResult`, `URLEntry`
- Functions return meaningful values, not side-effect dependent
- Tuples for multiple returns when appropriate: `tuple[str, str, str]`

**Example from `validate_docs_anchors.py` (lines 78-94) - Clear parameters and returns:**
```python
def _split_link_target(raw: str) -> tuple[str, Optional[str]]:
    """Return (path_part, fragment) where fragment excludes the leading '#'."""
    raw = raw.strip()
    if "\"" in raw:
        raw = raw.split("\"")[0].strip()
    if "#" not in raw:
        return raw, None
    path_part, fragment = raw.split("#", 1)
    fragment = fragment.strip()
    if fragment == "":
        return path_part, None
    return path_part.strip(), fragment
```

## Module Design

**Exports:**
- Main entry point: `if __name__ == "__main__": main()`
- Top-level constants defined at module scope: `SCRIPT_DIR`, `PROJECT_ROOT`, `DOCS_DIR`
- Configuration organized at top before functions

**Barrel Files:**
- Not applicable (no JavaScript/TypeScript)
- Markdown files use navigation structure defined in `mkdocs.yml`

## Standards Applied

**Python Version:**
- Python 3 (shebang: `#!/usr/bin/env python3`)
- Type hints (3.10+ style: `list[str]` instead of `List[str]`)
- f-strings throughout

**Cross-Platform Safety:**
- Windows encoding check on all scripts
- Path handling with `pathlib.Path` for Windows/Unix compatibility
- No hardcoded forward or backslashes

**Dataclass Usage:**
- Used for all structured data: `URLEntry`, `ChangeRecord`, `FetchResult`, `LinkIssue`
- Frozen dataclasses where immutability desired
- Default factories for mutable defaults: `field(default_factory=list)`

---

*Convention analysis: 2026-02-02*
