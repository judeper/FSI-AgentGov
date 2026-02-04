# Monitoring Configuration Guide

This guide explains how to modify the FSI-AgentGov monitoring configuration file (`monitoring-config.yaml`). The configuration controls how the Learn Monitor and Regulatory Monitor classify and prioritize detected changes.

**Target Audience:** FSI compliance staff and administrators who need to adjust monitoring sensitivity without modifying Python code.

---

## Purpose

The monitoring system watches for changes in:

1. **Microsoft Learn Documentation** - Detects when Microsoft updates documentation that may require changes to FSI-AgentGov playbooks
2. **Regulatory Sources** - Detects new rules and notices from SEC, CFTC, OCC, Federal Reserve, and FINRA that may affect AI agent governance

The configuration file lets you:
- Adjust which changes are flagged as critical vs. routine
- Add new keywords that map to specific controls
- Configure which regulatory agencies to monitor
- Tune operational parameters like request timeouts

---

## File Structure

| Section | Purpose |
|---------|---------|
| `learn` | Classification patterns for Microsoft Learn documentation changes |
| `regulatory` | Classification patterns for regulatory items from Federal Register and FINRA |
| `keyword_control_map` | Maps keywords in regulatory items to FSI-AgentGov controls that may need updates |
| `federal_register` | Federal Register API configuration (agencies, document types) |
| `operational` | HTTP request settings and output formatting |

---

## Classification Order

Changes and regulatory items are classified using a waterfall approach:

1. **CRITICAL** - Checked first. Requires immediate action.
2. **HIGH** - Checked second. Requires review within 1-2 days.
3. **NOISE** - Checked third. Metadata or formatting changes; can be ignored.
4. **MEDIUM** - Default if no other patterns match. Review optional.

The first matching pattern determines the classification. If no patterns match, the item defaults to MEDIUM.

### What Each Classification Means

| Classification | Learn Monitor | Regulatory Monitor |
|---------------|---------------|-------------------|
| CRITICAL | UI navigation steps changed; deprecation notices; breaking changes | Directly mentions AI agents, copilot, or automated advice |
| HIGH | Portal references; UI element names; policy language; compliance features | References AI, ML, automation, or FSI-specific requirements |
| MEDIUM | General content updates | General FSI regulations with indirect relevance |
| NOISE | Metadata, article contributors, formatting only | No FSI AI agent governance relevance |

---

## Pattern Syntax

Patterns use Python regular expression (regex) syntax. Here are the most common elements you'll need:

### Essential Syntax

| Syntax | Meaning | Example |
|--------|---------|---------|
| `\b` | Word boundary (start or end of word) | `\bai\b` matches "ai" but not "mail" |
| `\s` | Any whitespace (space, tab, newline) | `ai\s+agent` matches "ai agent" with any spaces |
| `+` | One or more of the previous element | `\s+` matches one or more spaces |
| `*` | Zero or more of the previous element | `\s*` matches zero or more spaces |
| `(a\|b)` | Either a or b | `(click\|select)` matches "click" or "select" |
| `[34]` | Any single character in brackets | `17a-[34]` matches "17a-3" or "17a-4" |
| `(?:...)` | Group without capturing | `(?:electronic\|automated)` groups the OR |
| `^` | Start of line | `^[-+]` matches lines starting with - or + |
| `\.` | Literal period (escape special character) | `ms\.date` matches "ms.date" |

### Pattern Examples

**Match "AI agent" or "AI agents" (case-insensitive):**
```yaml
pattern: '\bai\s+agents?'
```

**Match SEC 17a-3 or SEC 17a-4:**
```yaml
pattern: '\bsec\s+17a-[34]'
```

**Match deprecation-related words:**
```yaml
pattern: '(deprecated|removed|no longer|retired)'
```

**Match "recordkeeping" followed by "electronic" or "automated":**
```yaml
pattern: '\brecordkeeping.*(?:electronic|automated)'
```

---

## How to Modify Patterns

### Adding a New Pattern

1. Open `monitoring-config.yaml`
2. Find the appropriate section (`learn` or `regulatory`) and classification tier
3. Add a new entry following this format:

```yaml
    - pattern: 'your-regex-pattern-here'
      reason: "Human-readable reason for flagging"
```

**Example - Add a CRITICAL pattern for "AI model":**

```yaml
learn:
  critical_patterns:
    # ... existing patterns ...
    - pattern: '\bai\s+model'
      reason: "AI model terminology changed"
```

### Modifying an Existing Pattern

1. Find the pattern you want to change
2. Update the `pattern` value or `reason` text
3. Save and validate (see Validation section below)

### Removing a Pattern

1. Delete the entire entry (both `pattern` and `reason` lines)
2. Ensure YAML indentation remains correct

---

## How to Add Keyword Mappings

Keyword mappings connect regulatory terms to FSI-AgentGov controls. When a regulatory item contains a keyword, the mapped controls may need review.

### Format

```yaml
keyword_control_map:
  - keyword: your keyword phrase
    controls:
      - id: "X.Y"
        name: "Control Name"
```

### Adding a New Keyword

1. Find the `keyword_control_map` section
2. Add a new entry:

```yaml
  - keyword: sanctions
    controls:
      - id: "1.3"
        name: "Data Loss Prevention Policies"
      - id: "2.6"
        name: "Risk Assessment Framework"
```

**Notes:**
- Keywords are matched case-insensitively
- Use lowercase for the keyword value
- Control IDs must match those in `docs/controls/CONTROL-INDEX.md`

---

## How to Add Agencies

To monitor additional regulatory agencies from the Federal Register:

1. Find the agency slug on [federalregister.gov](https://www.federalregister.gov/agencies)
2. Add an entry to `federal_register.agencies`:

```yaml
federal_register:
  agencies:
    # ... existing agencies ...
    - slug: consumer-financial-protection-bureau
      short_name: CFPB
```

---

## Validation

**Before deploying changes**, validate the configuration file:

### Quick Syntax Check

```bash
python3 -c "import yaml; yaml.safe_load(open('scripts/config/monitoring-config.yaml')); print('Valid')"
```

### Full Validation (checks regex patterns)

```bash
cd /path/to/FSI-AgentGov
python3 -c "from scripts.monitoring_shared import load_monitoring_config; load_monitoring_config()"
```

If validation passes, no output is shown. If validation fails, you'll see an error message indicating:
- The location of the error (e.g., `learn.critical_patterns[2].pattern`)
- The invalid pattern value
- The specific error (e.g., "unterminated character set")

---

## Common Mistakes

### YAML Syntax Errors

| Mistake | Problem | Fix |
|---------|---------|-----|
| Missing quotes around pattern | YAML interprets backslashes incorrectly | Always quote patterns: `pattern: '\bword'` |
| Inconsistent indentation | YAML requires consistent spacing | Use 2 spaces per indent level |
| Tab characters | YAML doesn't allow tabs | Replace tabs with spaces |

### Regex Errors

| Mistake | Problem | Fix |
|---------|---------|-----|
| Unescaped special characters | `.`, `(`, `)`, `[`, `]` have special meaning | Escape with backslash: `\.` |
| Unclosed brackets | `[abc` without closing `]` | Add closing bracket: `[abc]` |
| Unclosed parentheses | `(a|b` without closing `)` | Add closing paren: `(a|b)` |
| Invalid escape sequence | `\z` is not valid | Use valid escapes: `\b`, `\s`, `\d` |

### Testing Your Patterns

Before adding a pattern, test it:

```bash
python3 -c "import re; re.compile(r'your-pattern-here'); print('Valid')"
```

---

## Operational Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `request_timeout` | 30 | Seconds to wait for HTTP responses |
| `max_retries` | 3 | Number of retry attempts for failed requests |
| `request_delay` | 1.0 | Seconds between requests (prevents rate limiting) |
| `max_diff_lines` | 100 | Truncate diffs longer than this |

**When to adjust:**
- Increase `request_timeout` if you see timeout errors
- Increase `request_delay` if you see rate limiting (429) errors
- Decrease `max_diff_lines` if reports are too large

---

## Related Documentation

- [Learn Monitor Guide](../../docs/reference/learn-monitor-guide.md) - How the Learn Monitor works
- [Control Index](../../docs/controls/CONTROL-INDEX.md) - Complete list of FSI-AgentGov controls
- [Regulatory Mappings](../../docs/reference/regulatory-mappings.md) - Framework regulatory coverage

---

## Support

If you need help modifying the configuration:

1. Test changes in a development environment first
2. Use the validation commands above before deploying
3. Check the error message carefully - it indicates the exact location of the problem
4. Refer to the pattern examples in this guide
