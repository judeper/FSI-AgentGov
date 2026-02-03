# Phase 2: Documentation Audit Foundation - Research

**Researched:** 2026-02-03
**Domain:** Documentation accuracy verification and consistency enforcement
**Confidence:** HIGH

## Summary

Phase 2 requires auditing all 62 controls and their 248 playbooks to verify accuracy against current Microsoft capabilities with consistent formatting and reliable citations. This is a two-pass accuracy and consistency audit where the first pass identifies all discrepancies in per-pillar audit reports, and the second pass applies corrections after review.

The framework has strong existing infrastructure for this work: a 10-section control template enforced by `verify_controls.py`, 209 Microsoft Learn URLs monitored by `learn_monitor.py` with daily change detection, and comprehensive playbook coverage (4 per control). The challenge is systematic verification of factual accuracy against fast-moving Microsoft documentation while enforcing formatting consistency across controls that evolved organically.

Key findings: Controls use inconsistent formatting patterns (32 of 67 use MkDocs admonitions, varying blockquote vs admonition usage), the Learn Monitor provides real-time change detection with severity classification, and regulatory citation patterns are well-established but need verification against actual regulation text rather than just the existing regulatory-mappings.md.

**Primary recommendation:** Use per-pillar batched audits with structural validation first (template compliance, formatting standardization) followed by content accuracy verification (Microsoft Learn alignment, regulatory citation accuracy), producing detailed audit reports with evidence before applying corrections.

## Standard Stack

The established tooling and patterns for documentation verification:

### Core

| Tool/Pattern | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| MkDocs Material | Current | Static site generation with nav validation | Framework's existing build system, --strict mode catches structural errors |
| Python verify_controls.py | v1.2.37 | Template compliance validation | Existing validation script enforcing 10-section structure |
| Python learn_monitor.py | v1.2.37 | Microsoft Learn URL change detection | Active monitoring of 209 URLs with daily runs and severity classification |
| BeautifulSoup4 | Current | HTML parsing for URL verification | Already used by learn_monitor.py for content extraction |
| SHA-256 hashing | Standard | Content change detection | learn_monitor.py uses for reliable change tracking |

### Supporting

| Tool/Pattern | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| difflib | Python stdlib | Line-by-line content comparison | Change identification between versions |
| grep/ripgrep | System | Pattern matching across controls | Finding formatting inconsistencies |
| git diff | Git | Version comparison | Tracking corrections between audit and fix passes |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual audit | Automated content scraping | Manual catches context issues automation misses; use hybrid approach |
| Single-pass fix | Two-pass audit-then-fix | Two-pass allows review of findings before committing changes |
| Full-framework audit | Per-pillar batching | Batching enables incremental review and faster feedback cycles |

**Installation:**

Already installed. Verify with:

```bash
python3 scripts/verify_controls.py
python3 scripts/learn_monitor.py --dry-run --limit 5
mkdocs build --strict
```

## Architecture Patterns

### Recommended Audit Structure

```
.planning/phases/02-documentation-audit-foundation/
├── 02-RESEARCH.md              # This file
├── plans/
│   ├── 03-PLAN-pillar-1.md     # Audit Pillar 1 (24 controls)
│   ├── 04-PLAN-pillar-2.md     # Audit Pillar 2 (21 controls)
│   ├── 05-PLAN-pillar-3.md     # Audit Pillar 3 (10 controls)
│   └── 06-PLAN-pillar-4.md     # Audit Pillar 4 (7 controls)
└── outputs/
    ├── AUDIT-PILLAR-1.md       # Pillar 1 audit findings
    ├── AUDIT-PILLAR-2.md       # Pillar 2 audit findings
    ├── AUDIT-PILLAR-3.md       # Pillar 3 audit findings
    └── AUDIT-PILLAR-4.md       # Pillar 4 audit findings
```

### Pattern 1: Two-Pass Audit Methodology

**What:** First pass produces audit reports with detailed findings and evidence. Second pass applies corrections after review.

**When to use:** When batch accuracy verification requires human review before committing changes.

**Audit Report Structure:**

```markdown
# Pillar N Audit Report

**Audited:** [date]
**Controls Checked:** [count]
**Total Findings:** [count]

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | N | Factually wrong / could mislead |
| Moderate | N | Outdated but not harmful |
| Minor | N | Formatting / naming inconsistency |

## Critical Findings

### Control X.X: [Name]

**Issue:** [What's wrong]
**Evidence:** [Microsoft Learn URL / regulation text]
**Current Doc Says:** [Excerpt]
**Should Say:** [Correction with source]
**Affected Files:**
- controls/pillar-X/X.X-name.md (lines XX-YY)
- playbooks/control-implementations/X.X/portal-walkthrough.md (lines XX-YY)

## Moderate Findings
[Same structure]

## Minor Findings
[Same structure]

## Verification Notes

**Microsoft Learn URLs Checked:** [count]
**Last Learn Monitor Run:** [date from learn-monitor-state.json]
**Template Compliance:** [Pass/Fail from verify_controls.py]
**Regulatory Citations Verified:** [count]
```

### Pattern 2: Structural vs Content Validation

**What:** Separate validation of template compliance (structural) from factual accuracy (content).

**Structure First:**
1. Run `verify_controls.py` to identify template violations
2. Check 10-section ordering and completeness
3. Verify formatting consistency (admonitions, tables, code blocks)
4. Ensure footer metadata present and canonical

**Content Second:**
1. Cross-reference Microsoft Learn URLs against current documentation
2. Verify regulatory citations against actual regulation text
3. Check that configuration steps match current portal UI
4. Validate that PowerShell examples use current cmdlets

**Example - Structural Check:**

```python
# Verify all controls have required sections in correct order
REQUIRED_HEADINGS = [
    "## Objective",
    "## Why This Matters for FSI",
    "## Control Description",
    "## Key Configuration Points",
    "## Zone-Specific Requirements",
    "## Roles & Responsibilities",
    "## Related Controls",
    "## Implementation Guides",
    "## Verification Criteria",
    "## Additional Resources",
]

# Check footer format
CANON_UPDATED = "Updated: January 2026"
CANON_VERSION = "Version: v1.2"
CANON_UI_STATUS_PREFIX = "UI Verification Status:"
```

**Example - Content Check:**

```python
# Extract Microsoft Learn URLs from control
learn_urls = re.findall(r'https://learn\.microsoft\.com[^\s\)]+', content)

# Compare against learn-monitor-state.json
for url in learn_urls:
    if url in state['urls']:
        current_hash = state['urls'][url]['content_hash']
        # Flag if content changed since last doc update
```

### Pattern 3: Formatting Standard Derivation

**What:** Rather than creating a separate formatting standards document, derive the standard from best-formatted existing controls.

**Identification Criteria:**

Controls that exemplify good formatting:
- Control 2.1 (Managed Environments) - Extensive admonitions for licensing, deadlines, prerequisites
- Control 3.1 (Agent Inventory) - Code blocks with proper syntax highlighting, inline tables
- Control 1.1 (Restrict Publishing) - Clean blockquote usage for playbook links

**Standard Elements to Extract:**

1. **Admonition Usage:**
   - `!!! warning` for licensing requirements, deadlines, breaking changes
   - `!!! info` for preview features, context clarifications
   - `!!! tip` for advanced implementations, deployable solutions
   - `!!! danger` for critical action-required items
   - `!!! note` for verification scope, terminology clarifications

2. **Table Formatting:**
   - Zone-specific requirements: 3-column (Zone, Requirement, Rationale)
   - Roles & Responsibilities: 2-column (Role, Responsibility)
   - Related Controls: 2-column (Control with link, Relationship)

3. **Code Block Standards:**
   - PowerShell: Use `powershell` language identifier
   - Kusto/KQL: Use `kusto` language identifier
   - Bash: Use `bash` language identifier
   - Include `# Comment` lines for context

4. **Link Patterns:**
   - Internal control links: `[X.X - Name](../pillar-N/file.md)`
   - Playbook links: `[Portal Walkthrough](../../playbooks/control-implementations/X.X/portal-walkthrough.md)`
   - External: `[Microsoft Learn: Topic](https://learn.microsoft.com/...)`

### Pattern 4: Citation Verification Protocol

**What:** Systematic verification of regulatory citations against source regulation text, not just regulatory-mappings.md.

**Verification Steps:**

1. **Extract all regulatory citations from control:**
   ```bash
   grep -E "(FINRA|SEC|SOX|GLBA|OCC|Fed SR|CFTC|NYDFS)" control.md
   ```

2. **Verify specific section citations:**
   - FINRA 4511(a)(1) - Check actual rule text at finra.org
   - SEC 17a-4(b)(4) - Verify retention period matches regulation
   - SOX 302/404 - Confirm internal control requirements align

3. **Flag imprecise citations:**
   - "Required for FINRA 4511" ✗ (too vague)
   - "Supports FINRA 4511(a) books and records retention" ✓ (specific)

4. **Verify regulatory-mappings.md accuracy:**
   - Cross-check control-to-regulation mappings
   - Verify retention periods match actual regulation
   - Ensure zone requirements align with regulatory risk

**Common Citation Errors:**

- Using outdated rule numbers (FINRA Notice 25-07 is workplace modernization, not AI supervision)
- Imprecise section references ("SEC requirements" vs "SEC 17a-4(b)(4)")
- Confusing guidance documents with binding rules
- Missing effective dates for recent regulation changes

### Anti-Patterns to Avoid

- **Fixing as you audit:** Document first, fix after review prevents premature commits
- **Assuming Learn Monitor caught everything:** Monitor detects changes, not initial inaccuracies
- **Template-only validation:** Structure compliance doesn't guarantee factual accuracy
- **Batch commits without review:** Per-pillar audit reports enable incremental review

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Microsoft Learn content change detection | Custom scraper with cron | learn_monitor.py with GitHub Actions workflow | Already monitors 209 URLs daily with severity classification and diff generation |
| Template compliance checking | Manual review | verify_controls.py | Enforces 10-section structure, footer metadata, and heading consistency |
| URL availability checking | Custom HTTP checker | MkDocs link checker in CI | GitHub Actions workflow runs weekly, catches broken internal/external links |
| Regulatory text retrieval | Manual lookup | Regulatory agency websites + existing regulatory-mappings.md as starting point | Official sources are authoritative; mappings document provides framework context |

**Key insight:** The framework has mature infrastructure for documentation verification. The audit focuses on applying existing tools systematically rather than building new validation mechanisms.

## Common Pitfalls

### Pitfall 1: Treating Learn Monitor as Ground Truth

**What goes wrong:** Learn Monitor detects changes but doesn't verify initial accuracy. Controls may have been inaccurate from creation.

**Why it happens:** Assumption that monitored URLs guarantee current accuracy.

**How to avoid:**
1. Use Learn Monitor state as starting verification point
2. Manually verify each control's Microsoft Learn references against current documentation
3. Check publication dates on Learn articles (controls updated Jan 2026, but Learn articles may be older)
4. Flag controls referencing Learn URLs not in microsoft-learn-urls.md (unmonitored)

**Warning signs:**
- Control says "Last UI Verified: January 2026" but Learn URL shows "Last updated: 2025"
- Control references features as "current" that are marked "preview" in Learn
- Configuration steps don't match current portal screenshots

### Pitfall 2: Inconsistent Admonition Application

**What goes wrong:** Controls use varying patterns for similar information (blockquotes vs admonitions, inconsistent severity levels).

**Why it happens:** Organic growth across 62 controls without enforced formatting standards.

**How to avoid:**
1. Identify "best formatted" controls as exemplars (2.1, 3.1, 1.1)
2. Create admonition decision tree:
   - Preview features → `!!! warning "Preview Notice"`
   - Licensing requirements → `!!! warning "Licensing Requirements"`
   - Critical deadlines → `!!! danger "Action Required"`
   - Advanced solutions → `!!! tip "Advanced Implementation"`
   - Clarifications → `!!! info` or `!!! note`
3. Convert blockquotes to appropriate admonition types
4. Standardize across all controls in audit phase

**Warning signs:**
- Same information type formatted differently across controls
- Important warnings buried in paragraph text instead of admonitions
- Overuse of blockquotes for content that should be admonitions

### Pitfall 3: Regulatory Citation Without Verification

**What goes wrong:** Citing "FINRA 4511" or "SEC 17a-4" without verifying specific section applies.

**Why it happens:** Copying citations from regulatory-mappings.md without checking source regulation text.

**How to avoid:**
1. Access actual regulation text (finra.org, sec.gov, pcaobus.org)
2. Verify specific subsections cited (e.g., SEC 17a-4(b)(4) vs 17a-4(a))
3. Check retention periods match exactly (3 years vs 6 years)
4. Verify rule interpretation matches FINRA/SEC guidance documents
5. Flag citations that are guidance (FINRA Notice 24-09) vs binding rules (FINRA 3110)

**Warning signs:**
- Generic citations without specific subsections
- Retention periods that don't match official requirements
- Citing notices/guidance as if they're binding rules
- Missing effective dates for recent regulatory changes

### Pitfall 4: Scope Creep into Feature Work

**What goes wrong:** Audit uncovers missing capabilities, temptation to add new controls/playbooks.

**Why it happens:** Discovering gaps naturally leads to wanting to fill them.

**How to avoid:**
1. Document findings as "Out of Scope" section in audit report
2. Create separate tracking for future enhancement work
3. Strictly limit audit to: accuracy verification, formatting standardization, citation validation
4. New controls, new playbooks, and feature additions belong in later phases

**Warning signs:**
- Audit report includes "should add control for X" recommendations
- Spending time researching new Microsoft features not currently documented
- Planning new playbook structures instead of auditing existing ones

### Pitfall 5: Assuming Playbook Accuracy from Control Accuracy

**What goes wrong:** Verifying control document doesn't guarantee linked playbooks are accurate.

**Why it happens:** Playbooks are separate files; controls link to them but don't contain their content.

**How to avoid:**
1. Audit scope includes ALL 248 playbooks (4 per control)
2. Verify portal-walkthrough steps match current UI
3. Check PowerShell cmdlets in powershell-setup are current
4. Validate verification-testing procedures are executable
5. Ensure troubleshooting reflects current error patterns

**Warning signs:**
- Control references current features but playbook uses deprecated steps
- Portal-walkthrough has navigation paths that don't match current admin centers
- PowerShell examples use cmdlets removed in recent updates

## Code Examples

Verified patterns from existing framework:

### Extracting Microsoft Learn URLs from Control

```python
# Source: scripts/learn_monitor.py pattern
import re

def extract_learn_urls(control_content: str) -> list[str]:
    """Extract all Microsoft Learn URLs from control markdown."""
    pattern = r'https://learn\.microsoft\.com/[^\s\)\]<>\"\']*'
    urls = re.findall(pattern, control_content)
    # Remove trailing punctuation
    cleaned = [url.rstrip('.,;:)') for url in urls]
    return list(set(cleaned))  # Deduplicate
```

### Checking URL Against Learn Monitor State

```python
# Source: Adapted from learn_monitor.py
import json
from pathlib import Path

def check_url_freshness(url: str, control_updated: str) -> dict:
    """
    Compare control update date against Learn Monitor last check.

    Returns dict with status and recommendation.
    """
    state_file = Path("data/learn-monitor-state.json")
    state = json.loads(state_file.read_text())

    if url not in state['urls']:
        return {
            'status': 'UNMONITORED',
            'recommendation': 'Add to microsoft-learn-urls.md for monitoring'
        }

    url_data = state['urls'][url]
    last_check = state['last_run']

    # Parse control_updated: "January 2026" -> datetime comparison
    # If Learn URL changed after control update, flag for review

    return {
        'status': 'MONITORED',
        'last_check': last_check,
        'content_hash': url_data['content_hash']
    }
```

### Template Compliance Validation

```python
# Source: scripts/verify_controls.py (existing implementation)
import re
from pathlib import Path

REQUIRED_HEADINGS = [
    "## Objective",
    "## Why This Matters for FSI",
    "## Control Description",
    "## Key Configuration Points",
    "## Zone-Specific Requirements",
    "## Roles & Responsibilities",
    "## Related Controls",
    "## Implementation Guides",
    "## Verification Criteria",
    "## Additional Resources",
]

def validate_control_structure(control_path: Path) -> list[str]:
    """Validate control has all required sections."""
    content = control_path.read_text(encoding="utf-8")
    failures = []

    # Check for control title format
    if not re.search(r"^#\s+Control\s+\d+\.\d+[:\-]\s+.+$", content, flags=re.MULTILINE):
        failures.append("missing or malformed control title")

    # Check required headings
    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            failures.append(f"missing required section: {heading}")

    # Check footer metadata
    if "Updated: January 2026" not in content:
        failures.append("missing canonical 'Updated: January 2026' in footer")

    return failures
```

### Regulatory Citation Extraction

```bash
# Extract all regulatory citations from a control
grep -E "(FINRA [0-9]{4}|SEC [0-9]{2}a-[0-9]|SOX [0-9]{3}|GLBA [0-9]{3}|OCC [0-9]{4}-[0-9]{2}|SR [0-9]{2}-[0-9]|CFTC [0-9]\.[0-9]{2}|NYDFS Part [0-9]{3})" \
  docs/controls/pillar-N/X.X-control-name.md
```

### Formatting Consistency Check

```bash
# Find controls using blockquotes for playbook links (should standardize)
grep -l "> For step-by-step" docs/controls/pillar-*/*.md

# Find controls using admonitions (newer pattern)
grep -l "^!!!" docs/controls/pillar-*/*.md

# Identify admonition types in use
grep -h "^!!!" docs/controls/pillar-*/*.md | cut -d' ' -f2 | sort | uniq -c | sort -nr
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual Microsoft Learn checking | learn_monitor.py automated daily monitoring | v1.2.35 (Jan 2026) | 209 URLs tracked with change detection and severity classification |
| Single formatting standard across all controls | Organic growth with inconsistent patterns | Ongoing | 32 of 67 controls use admonitions; others use blockquotes or inline text |
| Generic regulatory citations | Specific subsection references with verification | v1.2.32 (remediation) | Improved audit defensibility but requires ongoing verification |
| Monthly template checks | verify_controls.py in CI/CD | v1.1+ | Catches structural violations automatically |

**Deprecated/outdated:**
- Manual link checking: Replaced by GitHub Actions link-check.yml workflow (weekly)
- Single-pass documentation updates: Two-pass methodology (audit-then-fix) adopted for Phase 2

## Open Questions

Things that couldn't be fully resolved:

1. **Admonition vs Blockquote Decision Criteria**
   - What we know: 32 of 67 controls use admonitions; blockquotes common for playbook links
   - What's unclear: Exact decision tree for when to use admonition types vs blockquotes
   - Recommendation: Derive standard from controls 2.1, 3.1, 1.1 (best-formatted); use admonitions for warnings/tips/notes, blockquotes only for extended quotations

2. **"Last Verified" Metadata Field Placement**
   - What we know: User wants this added to track freshness
   - What's unclear: Footer metadata vs header metadata vs inline section
   - Recommendation: Add to header metadata block (with Control ID, Pillar, Regulatory Reference, Last UI Verified) as "Last Content Verified: 2026-02-XX"

3. **Regulatory Citation Verification Depth**
   - What we know: Citations should be verified against actual regulation text
   - What's unclear: How deep to verify (exact subsection wording vs general applicability)
   - Recommendation: Verify specific subsection applies and retention periods match exactly; flag for legal review if interpretation ambiguous

4. **Microsoft Learn URL Programmatic Access**
   - What we know: Microsoft Learn Catalog API is deprecated mid-2026; MCP Server exists but doesn't provide full docs access
   - What's unclear: Best programmatic approach for content verification beyond existing learn_monitor.py scraping
   - Recommendation: Continue using learn_monitor.py BeautifulSoup approach; monitor for Microsoft Learn API v2 release

## Sources

### Primary (HIGH confidence)

- **FSI-AgentGov Repository** - Live codebase analysis
  - `/Users/admin/dev/FSI-AgentGov/docs/controls/` - 62 controls across 4 pillars
  - `/Users/admin/dev/FSI-AgentGov/docs/playbooks/control-implementations/` - 248 playbooks
  - `/Users/admin/dev/FSI-AgentGov/scripts/verify_controls.py` - Template validation logic
  - `/Users/admin/dev/FSI-AgentGov/scripts/learn_monitor.py` - URL monitoring implementation
  - `/Users/admin/dev/FSI-AgentGov/data/learn-monitor-state.json` - 209 monitored URLs with hashes
  - `/Users/admin/dev/FSI-AgentGov/reports/learn-changes/learn-changes-2026-02-01.md` - Recent change detection

- **Project Documentation**
  - `.github/copilot-instructions.md` - Repository structure and design decisions
  - `CONTRIBUTING.md` - Language guidelines and style rules
  - `docs/templates/control-setup-template.md` - 10-section control template
  - `docs/controls/CONTROL-INDEX.md` - Master control list (62 controls)
  - `docs/reference/regulatory-mappings.md` - Regulation-to-control mappings

### Secondary (MEDIUM confidence)

- [Glitter AI - How to Audit Documentation (2026)](https://www.glitter.io/blog/process-documentation/how-to-audit-documentation) - Contemporary documentation audit methodology
- [Fluid Topics - Technical Documentation Trends 2026](https://www.fluidtopics.com/blog/industry-insights/technical-documentation-trends-2026/) - AI-driven documentation verification trends
- [Microsoft Learn Catalog API Documentation](https://learn.microsoft.com/en-us/training/support/catalog-api) - Official API for Learn content (deprecated mid-2026)
- [Microsoft Learn MCP Server](https://github.com/MicrosoftDocs/mcp) - New approach for programmatic documentation access

### Tertiary (LOW confidence)

- WebSearch results on audit documentation best practices - General guidance requiring framework-specific adaptation
- PCAOB AS 1215 Audit Documentation Standard - Applies to financial audits but principles transferable to documentation audits

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools are existing, proven framework components
- Architecture: HIGH - Patterns derived from live codebase analysis and established framework practices
- Pitfalls: HIGH - Based on actual framework implementation challenges and organic evolution patterns

**Research date:** 2026-02-03
**Valid until:** 60 days (framework-specific research less volatile than fast-moving libraries)

**Key Constraints from CONTEXT.md:**
- Two-pass audit-then-fix approach (locked decision)
- Per-pillar batching: 4 separate plans, one per pillar (locked decision)
- Full structural + content check including all 248 playbooks (locked decision)
- Three-tier severity: Critical/Moderate/Minor (locked decision)
- Formatting standard derived from best-formatted controls (locked decision)
- "Last Verified" date metadata field (locked decision)
- Regulatory citations verified against actual regulation text (locked decision)

**Out of Scope (per CONTEXT.md deferred ideas):**
- None identified; discussion stayed within phase scope
