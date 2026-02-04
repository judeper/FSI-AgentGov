# Phase 3: Monitoring Configuration Externalization - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Extract hardcoded classification patterns from `monitoring_shared.py` and `regulatory_monitor.py` into external YAML configuration so non-developers can adjust monitoring sensitivity without code changes. Covers Learn Monitor, Regulatory Monitor, and shared settings.

</domain>

<decisions>
## Implementation Decisions

### Config scope
- Externalize **both monitors** (Learn and Regulatory) — they share the same classification framework
- Include **patterns AND thresholds** — classification patterns, keyword-to-control maps, agency lists, operational settings (timeouts, rate limits, retry counts, diff limits)
- Content normalization rules (HTML tags/selectors to strip) — Claude's discretion

### YAML structure
- **Group patterns by severity** — sections for `critical_patterns`, `high_patterns`, `medium_patterns`, `noise_patterns`; severity is implicit from section name
- Each pattern entry has `pattern` (regex) and `reason` (human-readable) fields
- **Raw regex only** — no named pattern aliases or template expansion; users who edit patterns know regex
- Keyword-to-control mappings include **control IDs + short descriptions** as structured fields for readability
- **Heavily documented** — rich inline YAML comments explaining every section, how to modify patterns, and examples

### Validation & errors
- **Fail hard** if config file is missing or has invalid YAML syntax — no run without valid config
- **Fail on load** if any regex pattern is invalid — validate all patterns at startup, exit with specific error pointing to the bad pattern
- Add **`--validate` flag** to `learn_monitor.py` and `regulatory_monitor.py` to check config and exit without running
- Error messages report **YAML path + value** (e.g., `learn.critical_patterns[2].pattern`) for debugging

### Migration path
- **Clean break** — remove hardcoded patterns entirely; config file is required
- Config location: **`scripts/config/`** subdirectory alongside Python files
- Add **`--config <path>` flag** to specify alternate config file location
- Config file **committed to repo** — version-controlled, all users start with same baseline

### Claude's Discretion
- Single config file vs split per monitor (decide based on code structure)
- Whether to externalize content normalization rules (HTML tags, CSS selectors)
- Config file name (e.g., `monitoring-config.yaml` vs `classification-patterns.yaml`)

</decisions>

<specifics>
## Specific Ideas

- Config should be self-documenting — a non-developer should be able to read the YAML and understand what each section does
- Pattern organization should mirror the code's classification waterfall: CRITICAL patterns checked first, then HIGH, then NOISE, then MEDIUM (default)
- Keyword-to-control mapping example structure:
  ```yaml
  keyword_control_map:
    - keyword: supervision
      controls:
        - id: "2.12"
          name: "Human-in-the-Loop Approval"
        - id: "2.18"
          name: "Supervision Queue Integration"
  ```

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-monitoring-configuration*
*Context gathered: 2026-02-04*
