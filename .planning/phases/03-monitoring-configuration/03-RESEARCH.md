# Phase 3: Monitoring Configuration Externalization - Research

**Researched:** 2026-02-04
**Domain:** Python YAML configuration management, pattern externalization, validation frameworks
**Confidence:** HIGH

## Summary

This phase externalizes hardcoded classification patterns from `monitoring_shared.py` and `regulatory_monitor.py` into YAML configuration files. The research confirms that Python's standard library `re` module combined with PyYAML 6.0.3 provides everything needed. No additional schema validation libraries are required for this phase given the user's decision for raw regex patterns without template expansion.

The established approach is:
- Use PyYAML 6.0.3 with `yaml.safe_load()` for security
- Validate regex patterns at startup using `re.compile()` to catch syntax errors early
- Use rich inline YAML comments for self-documentation
- Fail hard on missing/invalid config files to prevent runtime surprises
- Store config in `scripts/config/` with version control

**Primary recommendation:** Use Python stdlib (`yaml.safe_load()` + `re.compile()`) for config loading and regex validation. Skip third-party schema libraries (Yamale, Pydantic) since user wants raw regex only and explicit validation at load time.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyYAML | 6.0.3 | YAML parsing and serialization | Official Python YAML library, 6.0.3 released Sept 2025, supports Python 3.8+ |
| Python `re` | stdlib | Regex compilation and validation | Built-in, no dependencies, validates patterns at load time |
| Python `pathlib` | stdlib | File path handling | Already used throughout codebase |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `typing` | stdlib | Type hints for config structures | Document expected config shape |
| `dataclasses` | stdlib | Config data structures | Represent loaded config as Python objects |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyYAML | ruamel.yaml | ruamel preserves comments/formatting for round-tripping; not needed here (read-only) |
| Manual validation | Yamale, Pydantic | User wants raw regex validation at load time, not schema frameworks |
| JSON | YAML | YAML supports comments, more human-readable for non-developers |

**Installation:**
```bash
# PyYAML likely already installed for mkdocs
pip install pyyaml>=6.0
```

**Current status:** PyYAML is listed as optional in `scripts/requirements.txt` (line 12: `# pyyaml>=6.0`). Make it required.

## Architecture Patterns

### Recommended Project Structure
```
scripts/
├── config/
│   ├── monitoring-config.yaml      # Single unified config file
│   └── README.md                   # Config documentation
├── monitoring_shared.py            # Remove hardcoded patterns
├── regulatory_monitor.py           # Remove hardcoded patterns
└── learn_monitor.py                # Uses shared classification
```

**Config file decision (Claude's discretion):** Single unified config file (`monitoring-config.yaml`) because:
- Both monitors share the same classification framework (CRITICAL/HIGH/MEDIUM/NOISE)
- User specified "externalize **both monitors**" in decisions
- Avoids duplication of shared patterns
- Easier to maintain consistency across monitors
- Can still have monitor-specific sections within one file

### Pattern 1: Config Loading with Validation
**What:** Load YAML config at module initialization, validate all patterns immediately, fail fast if invalid
**When to use:** For any configuration that affects runtime behavior
**Example:**
```python
# Source: Python stdlib + PyYAML 6.0.3 documentation
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
import yaml

def load_monitoring_config(config_path: Path) -> Dict[str, Any]:
    """
    Load monitoring configuration with fail-fast validation.

    Raises:
        FileNotFoundError: Config file missing
        yaml.YAMLError: Invalid YAML syntax
        ValueError: Invalid regex pattern with specific path
    """
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        print("Expected location: scripts/config/monitoring-config.yaml")
        sys.exit(2)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML syntax in {config_path}")
        print(f"Details: {e}")
        sys.exit(2)

    # Validate regex patterns
    _validate_patterns(config, config_path)

    return config

def _validate_patterns(config: Dict[str, Any], config_path: Path) -> None:
    """Validate all regex patterns in config, exit with specific error on failure."""
    for source_key in ['learn', 'regulatory']:
        for severity in ['critical_patterns', 'high_patterns', 'medium_patterns', 'noise_patterns']:
            yaml_path = f"{source_key}.{severity}"
            patterns = config.get(source_key, {}).get(severity, [])

            for i, entry in enumerate(patterns):
                pattern_str = entry.get('pattern', '')
                try:
                    re.compile(pattern_str)
                except re.error as e:
                    print(f"ERROR: Invalid regex in config")
                    print(f"  File: {config_path}")
                    print(f"  Path: {yaml_path}[{i}].pattern")
                    print(f"  Pattern: {pattern_str}")
                    print(f"  Error: {e}")
                    sys.exit(2)
```

### Pattern 2: YAML Config Structure
**What:** Self-documenting YAML with sections mirroring classification waterfall
**When to use:** For the monitoring config file
**Example:**
```yaml
# FSI-AgentGov Monitoring Configuration
# Version: 1.0
# Last Updated: 2026-02-04
#
# This file controls classification patterns for Learn Monitor and Regulatory Monitor.
# Both monitors use the same 4-tier classification system:
#   - CRITICAL: Requires immediate action (portal-walkthrough playbook updates)
#   - HIGH: Requires review (control documentation may need updates)
#   - MEDIUM: General content updates (review optional)
#   - NOISE: Metadata/formatting only (safe to ignore)
#
# Pattern matching order (classification waterfall):
#   1. CRITICAL patterns checked first
#   2. HIGH patterns checked second
#   3. NOISE patterns checked third
#   4. Everything else defaults to MEDIUM
#
# Each pattern entry has two fields:
#   - pattern: Raw Python regex (use \b for word boundaries, escape special chars)
#   - reason: Human-readable explanation (shown in reports)

# === Learn Monitor Configuration ===
learn:
  # CRITICAL: Changes requiring immediate playbook updates
  critical_patterns:
    - pattern: '\d+\.\s+(click|select|go to|navigate)'
      reason: 'UI navigation steps changed'

    - pattern: '(deprecated|removed|no longer|retired)'
      reason: 'Deprecation notice'

    - pattern: '(breaking change|migration required)'
      reason: 'Breaking changes'

  # HIGH: Changes requiring control review
  high_patterns:
    - pattern: '(Admin center|portal|Power Platform|Purview)'
      reason: 'Portal references'

    - pattern: '(button|menu|tab|panel|dialog|blade)'
      reason: 'UI element names'

  # NOISE: Safe to ignore (metadata/formatting)
  noise_patterns:
    - pattern: '^\s*$'
      reason: 'Empty lines'

    - pattern: 'ms\.(date|author|reviewer|topic)'
      reason: 'Metadata fields'

  # Operational settings
  settings:
    request_delay: 1.0          # Seconds between requests
    request_timeout: 30         # HTTP timeout in seconds
    max_retries: 3              # Retry attempts for failed requests
    diff_line_limit: 100        # Max diff lines in reports

# === Regulatory Monitor Configuration ===
regulatory:
  # CRITICAL: AI agents/copilot mentioned in regulatory context
  critical_patterns:
    - pattern: '\bai\s+agent'
      reason: 'Directly mentions AI agents'

  # HIGH: AI/ML/automation in FSI context
  high_patterns:
    - pattern: '\bartificial\s+intelligence'
      reason: 'References artificial intelligence'

  # Federal Register API configuration
  agencies:
    - slug: 'securities-and-exchange-commission'
      name: 'SEC'
    - slug: 'commodity-futures-trading-commission'
      name: 'CFTC'

  # Keyword-to-control mapping
  # Maps regulatory keywords to affected framework controls
  # Provides actionable suggestions in reports
  keyword_control_map:
    - keyword: supervision
      controls:
        - id: "2.12"
          name: "Supervision and Oversight (FINRA Rule 3110)"
        - id: "2.18"
          name: "Automated Conflict of Interest Testing"

    - keyword: recordkeeping
      controls:
        - id: "1.7"
          name: "Audit Trail and Logging"
```

### Pattern 3: Config Override via CLI Flag
**What:** Allow alternate config file location for testing
**When to use:** Both monitors need `--config <path>` flag
**Example:**
```python
parser.add_argument(
    '--config',
    type=Path,
    default=SCRIPT_DIR / 'config' / 'monitoring-config.yaml',
    help='Path to monitoring configuration file'
)

# Then in main():
config = load_monitoring_config(args.config)
```

### Pattern 4: Validate Flag (Dry-Run Validation)
**What:** Check config validity without running monitor
**When to use:** Both monitors need `--validate` flag
**Example:**
```python
parser.add_argument(
    '--validate',
    action='store_true',
    help='Validate configuration file and exit'
)

# Then in main():
if args.validate:
    print(f"Validating config: {args.config}")
    config = load_monitoring_config(args.config)
    print("✓ Config is valid")
    print(f"  Learn patterns: {len(config['learn']['critical_patterns'])} critical, ...")
    print(f"  Regulatory patterns: ...")
    sys.exit(0)
```

### Anti-Patterns to Avoid
- **Ignoring config errors and using defaults:** User specified fail-hard behavior; never fall back to hardcoded patterns
- **Loading config on every function call:** Load once at module initialization, cache in module-level variable
- **Allowing invalid regex to reach runtime:** All patterns must be validated at load time with `re.compile()`
- **Template expansion or pattern aliases:** User explicitly wants raw regex only
- **Mixing config formats:** Stick with YAML, don't split into JSON/TOML/INI

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML schema validation | Custom validator | PyYAML `safe_load()` + `re.compile()` | Schema libraries (Yamale, Pydantic) are overkill for this use case; user wants raw regex validation |
| Config file comments | JSON with external docs | YAML with inline comments | YAML natively supports `#` comments for self-documentation |
| Regex pattern libraries | Pattern template system | Raw regex strings | User explicitly rejected template expansion; regex experts edit these |
| Config reloading on change | File watcher | Load once at startup | Monitors are batch scripts, not long-running services |

**Key insight:** This is a straightforward externalization task. Resist the temptation to add schema frameworks, config management layers, or pattern DSLs. The simplest solution (YAML + stdlib) is the right solution.

## Common Pitfalls

### Pitfall 1: PyYAML `yaml.load()` Without Loader
**What goes wrong:** Using `yaml.load()` without specifying `Loader` triggers security warning and may execute arbitrary code
**Why it happens:** Old PyYAML tutorials showed `yaml.load()` without warnings; behavior changed in PyYAML 5.1+
**How to avoid:** Always use `yaml.safe_load()` or specify `Loader=yaml.FullLoader` explicitly
**Warning signs:** DeprecationWarning about unsafe loading

### Pitfall 2: Regex Validation After First Use
**What goes wrong:** Invalid regex pattern causes crash during classification, not at startup
**Why it happens:** Patterns aren't compiled until first use in `re.search()`
**How to avoid:** Validate all patterns with `re.compile()` immediately after loading YAML
**Warning signs:** Script runs fine until first URL with change triggers pattern matching

### Pitfall 3: Unclear Error Messages
**What goes wrong:** "Invalid regex in config" without showing which pattern failed
**Why it happens:** Validation loop doesn't track YAML path context
**How to avoid:** Error messages must include: config file path, YAML path (e.g., `learn.critical_patterns[2].pattern`), pattern string, and regex error
**Warning signs:** Developer has to add debug prints to find bad pattern

### Pitfall 4: Missing Config File Assumed Empty
**What goes wrong:** Script continues with no patterns loaded, classifies everything as MEDIUM
**Why it happens:** Developer treats missing file as "use defaults"
**How to avoid:** User specified "fail hard if config file is missing" — exit with error code 2
**Warning signs:** Monitor runs but reports zero CRITICAL/HIGH changes when it should

### Pitfall 5: YAML Anchors/Aliases in Patterns
**What goes wrong:** User tries to use YAML anchors (`&anchor`, `*alias`) to reduce duplication; patterns become references not strings
**Why it happens:** YAML anchors are powerful but complex; pattern strings need to be literal
**How to avoid:** Document in config comments that patterns must be raw strings, no YAML anchors
**Warning signs:** TypeError when trying to use pattern value as string

### Pitfall 6: Content Normalization Rules Externalized Without Testing
**What goes wrong:** If HTML tag/CSS selector removal is externalized, changes to normalization affect existing state hashes
**Why it happens:** Content normalization happens before hashing; changing it invalidates all stored hashes
**How to avoid:** If externalizing normalization rules (Claude's discretion), version the state file schema and rehash on format change
**Warning signs:** Every URL reports "CHANGED" after config update when nothing actually changed

### Pitfall 7: Keyword Map Without Control Descriptions
**What goes wrong:** YAML has keyword-to-control ID mappings but no context about what each control is
**Why it happens:** Developer treats it as pure data structure, forgets human maintainability
**How to avoid:** User specified "control IDs + short descriptions as structured fields" — include control names in YAML
**Warning signs:** Maintainer has to look up what control "2.12" is every time they edit keyword map

## Code Examples

Verified patterns from official sources:

### Loading Config at Module Level
```python
# Source: Python stdlib documentation, PyYAML 6.0.3 docs
# Place at top of monitoring_shared.py after imports

from pathlib import Path
import yaml
import sys

# Module-level config
_CONFIG = None

def get_monitoring_config() -> dict:
    """Get monitoring configuration (loads once, caches)."""
    global _CONFIG
    if _CONFIG is None:
        config_path = Path(__file__).parent / 'config' / 'monitoring-config.yaml'
        _CONFIG = load_monitoring_config(config_path)
    return _CONFIG
```

### Pattern Matching with Config
```python
# Source: FSI-AgentGov codebase (monitoring_shared.py lines 188-198)
# Replace hardcoded patterns with config-driven approach

def classify_change(old_text: str, new_text: str, url: str = "") -> tuple[str, str, str]:
    """Classify change severity using patterns from config."""
    config = get_monitoring_config()
    patterns = config['learn']  # or 'regulatory' depending on source

    # ... generate diff ...

    # Check CRITICAL patterns first (classification waterfall)
    for entry in patterns['critical_patterns']:
        pattern = entry['pattern']
        reason = entry['reason']
        for line in diff_lines:
            if line.startswith('+') or line.startswith('-'):
                if re.search(pattern, line, re.IGNORECASE):
                    return (CLASSIFICATION_CRITICAL, reason, diff_text)

    # Continue with HIGH, NOISE, then default to MEDIUM...
```

### Control Mapping from Config
```python
# Source: FSI-AgentGov codebase (regulatory_monitor.py lines 229-248)
# Replace KEYWORD_CONTROL_MAP dict with config-driven approach

def find_affected_controls_by_keywords(title: str, abstract: str, config: dict) -> list[dict]:
    """Find affected controls from config keyword map."""
    combined = f"{title.lower()} {abstract.lower()}"
    affected = {}

    for entry in config['regulatory']['keyword_control_map']:
        keyword = entry['keyword']
        pattern = rf'\b{re.escape(keyword)}\b'
        if re.search(pattern, combined, re.IGNORECASE):
            for control in entry['controls']:
                control_id = control['id']
                if control_id not in affected:
                    affected[control_id] = control

    return sorted(affected.values(), key=lambda x: x['id'])
```

### HTML Normalization Rules (if externalized)
```python
# Source: Claude's discretion area - BeautifulSoup 4 patterns
# Only if user decides to externalize normalization rules

# In monitoring-config.yaml:
# learn:
#   normalization:
#     remove_tags:
#       - script
#       - style
#       - nav
#     remove_selectors:
#       - .feedback-section
#       - .metadata

# In monitoring_shared.py:
def normalize_content(html: str, config: dict) -> str:
    """Normalize HTML using config-driven rules."""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove tags from config
    for tag_name in config['learn']['normalization']['remove_tags']:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove by CSS selector from config
    for selector in config['learn']['normalization']['remove_selectors']:
        for elem in soup.select(selector):
            elem.decompose()

    # ... rest of normalization ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded patterns in Python | YAML config files with validation | 2020s+ | Non-developers can tune classification without code changes |
| `yaml.load()` without Loader | `yaml.safe_load()` always | PyYAML 5.1 (2019) | Security: prevents arbitrary code execution |
| JSON for config | YAML for human-editable config | 2015+ | Better comments, readability |
| Schema libraries for simple validation | stdlib validation for raw regex | Ongoing | Avoid dependency bloat when stdlib suffices |

**Deprecated/outdated:**
- `yaml.load()` without Loader: Unsafe, use `yaml.safe_load()` instead
- Python 2 `unicode` strings in YAML: PyYAML 6.0.3 requires Python 3.8+, always uses UTF-8

## Open Questions

Things that couldn't be fully resolved:

1. **Should content normalization rules be externalized?**
   - What we know: User marked this as "Claude's discretion"; current normalization is hardcoded in `monitoring_shared.py` lines 104-141
   - What's unclear: Benefit vs. complexity tradeoff — externalizing adds flexibility but risks breaking existing state hashes
   - Recommendation: **Start without externalizing normalization rules**. They're stable and technical (BeautifulSoup selectors). Add in later phase if needed. Focus on classification patterns first.

2. **Single config file or split per monitor?**
   - What we know: User said "Claude's discretion"; both monitors share classification framework
   - What's unclear: Whether monitor-specific sections justify separate files
   - Recommendation: **Single unified config file** (`monitoring-config.yaml`) with sections for `learn:` and `regulatory:`. Easier to maintain consistency, less duplication. Can split later if file grows unwieldy.

3. **Config file name?**
   - What we know: User said "Claude's discretion" — examples given were `monitoring-config.yaml` vs `classification-patterns.yaml`
   - What's unclear: Which name better reflects purpose
   - Recommendation: **`monitoring-config.yaml`** — broader scope allows adding operational settings (timeouts, delays) not just patterns

4. **Should operational settings (timeouts, rate limits) be in config or remain constants?**
   - What we know: User specified "patterns AND thresholds — operational settings (timeouts, rate limits, retry counts, diff limits)"
   - What's unclear: None — user explicitly included these in scope
   - Recommendation: **Include operational settings in YAML config**. Example: `learn.settings.request_delay: 1.0`, `learn.settings.diff_line_limit: 100`

## Sources

### Primary (HIGH confidence)
- PyYAML 6.0.3 PyPI page: https://pypi.org/project/PyYAML/ (verified current version Sept 2025, Python 3.8+ requirement)
- Python `re` module documentation: https://docs.python.org/3/library/re.html (stdlib, standard for regex validation)
- Python `yaml.safe_load()` security: https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation (safe loading best practices)

### Secondary (MEDIUM confidence)
- [YAML Tutorial: Everything You Need to Get Started in Minutes](https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started) - Best practices for YAML structure
- [Python YAML Configuration Guide](https://mertcobanov.medium.com/python-yaml-configuration-guide-add326d712c5) - Configuration patterns
- [YAML: The Missing Battery in Python – Real Python](https://realpython.com/python-yaml/) - PyYAML usage patterns
- [Validate YAML in Python with Schema](https://www.andrewvillazon.com/validate-yaml-python-schema/) - Validation approaches
- [GitHub - 23andMe/Yamale: A schema and validator for YAML](https://github.com/23andMe/Yamale) - Alternative validation library (not needed for this phase)
- [YAML Comments: Inline, Block & Multi-Line Examples](https://testkube.io/blog/yaml-commenting-best-practices-kubernetes-testing) - Comment best practices
- [YAML Style Guide | Home Assistant Developer Docs](https://developers.home-assistant.io/docs/documenting/yaml-style-guide/) - Self-documenting YAML practices

### Tertiary (LOW confidence)
- Various Medium/blog posts about YAML configuration - general patterns, not verified against official docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - PyYAML 6.0.3 verified from official PyPI, stdlib `re` module is standard
- Architecture: HIGH - Patterns researched from official Python docs and PyYAML documentation
- Pitfalls: HIGH - Based on verified PyYAML security warnings and common regex validation errors

**Research date:** 2026-02-04
**Valid until:** 30 days (PyYAML and Python stdlib are stable; classification patterns are project-specific)
