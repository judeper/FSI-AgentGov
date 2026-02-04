# Phase 8: Monitoring Systems Review - Research

**Researched:** 2026-02-04
**Domain:** Documentation/regulatory content monitoring systems
**Confidence:** HIGH

## Summary

Phase 8 aims to review and improve the existing Learn Monitor system and assess the need for regulatory monitoring. The Learn Monitor (Python-based, daily GitHub Actions) is functional but shows opportunities for simplification and enhanced change visibility. The AI-assisted review skill exists but needs validation. A regulatory monitor does not exist as code — it should be designed and implemented as part of this phase.

**Current state analysis:**
- Learn Monitor: 857 lines of Python, 209 URLs tracked, daily execution, 4-tier classification working
- AI-assisted review: `.claude/skills/review-learn-changes.md` skill exists, designed but needs end-to-end testing
- Regulatory monitoring: No automation exists; manual tracking implied by state AI law references in CHANGELOG

**Primary recommendation:** Keep Learn Monitor architecture with targeted simplifications, activate and validate the AI-assisted review skill, and implement lightweight regulatory monitoring using RSS feeds and Federal Register API for FSI-specific sources.

---

## Standard Stack

### Core Libraries (Learn Monitor - Already in Use)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **requests** | 2.31+ | HTTP client | Industry standard, reliable, well-documented |
| **beautifulsoup4** | 4.12+ | HTML parsing | "Gold standard for parsing HTML" per industry consensus |
| **Python 3.11** | 3.11+ | Runtime | GitHub Actions default, stable, modern features |

### Supporting Libraries for Regulatory Monitoring

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **feedparser** | 6.0+ | RSS/Atom feed parsing | FINRA/SEC RSS feeds, standard library for feed parsing |
| **requests-html** | 0.10+ | Enhanced requests with JS support | If regulatory sites require JavaScript rendering |
| **hashlib** | stdlib | SHA-256 hashing | Already used in Learn Monitor, proven for content change detection |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| BeautifulSoup + requests | Scrapy | Scrapy adds complexity (async, selectors, middleware) unnecessary for monitoring ~200-300 URLs daily |
| BeautifulSoup + requests | requests-html | requests-html adds JS rendering support if needed, but BeautifulSoup is lighter for static content |
| Custom RSS parsing | feedparser | feedparser is battle-tested, handles RSS/Atom/RDF, better than hand-rolling XML parsing |

**Installation:**
```bash
# Already installed for Learn Monitor
pip install requests beautifulsoup4

# Add for regulatory monitoring
pip install feedparser
```

---

## Architecture Patterns

### Recommended Project Structure

```
scripts/
├── learn_monitor.py              # Existing Learn Monitor (keep)
├── regulatory_monitor.py         # NEW: Unified regulatory monitoring
├── monitoring_shared.py          # NEW: Shared utilities (hash, fetch, classify)
└── hooks/                        # Claude Code hooks
    ├── boundary-check.py
    └── researcher-package-reminder.py

data/
├── learn-monitor-state.json      # Existing Learn state
└── regulatory-monitor-state.json # NEW: Regulatory state

reports/
├── learn-changes/                # Existing Learn reports
└── regulatory-changes/           # NEW: Regulatory reports
```

### Pattern 1: Unified Monitoring Architecture

**What:** Single conceptual monitoring system with two specialized monitors (Learn, Regulatory) sharing common utilities

**When to use:** When monitoring multiple content sources with similar change detection needs

**Example:**
```python
# Source: FSI-AgentGov Learn Monitor architecture (lines 172-211, 243-247)
# Common pattern: fetch → normalize → hash → compare → classify

class ContentMonitor:
    """Base class for content monitoring."""

    def fetch_content(self, url: str) -> str:
        """Fetch and normalize content."""
        response = self.session.get(url, timeout=30)
        return self._normalize(response.text)

    def _normalize(self, html: str) -> str:
        """Extract main content, remove noise."""
        soup = BeautifulSoup(html, 'html.parser')
        # Remove non-content elements
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        text = soup.get_text(separator='\n', strip=True)
        # Normalize whitespace and dates
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{4}', '[DATE]', text)
        return text.strip()

    def compute_hash(self, content: str) -> str:
        """SHA-256 content hash."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def detect_change(self, url: str, new_content: str, state: dict) -> bool:
        """Compare hash against state."""
        new_hash = self.compute_hash(new_content)
        old_hash = state.get("urls", {}).get(url, {}).get("content_hash")
        return new_hash != old_hash

class LearnMonitor(ContentMonitor):
    """Microsoft Learn documentation monitor."""
    pass

class RegulatoryMonitor(ContentMonitor):
    """FINRA/SEC/Federal Register monitor."""

    def fetch_rss_feed(self, feed_url: str) -> list:
        """Fetch and parse RSS feed for new entries."""
        import feedparser
        feed = feedparser.parse(feed_url)
        return [entry for entry in feed.entries]
```

### Pattern 2: Four-Tier Change Classification

**What:** Consistent classification (CRITICAL/HIGH/MEDIUM/NOISE) across all monitors

**When to use:** All change detection to maintain uniform prioritization

**Example:**
```python
# Source: FSI-AgentGov Learn Monitor (lines 250-313)
def classify_change(old_text: str, new_text: str) -> tuple[str, str, str]:
    """
    Classify change as CRITICAL/HIGH/MEDIUM/NOISE.
    Returns (classification, reason, diff_text)
    """
    diff_lines = list(difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True)
    ))

    if not diff_lines:
        return ('noise', 'No text changes detected', '')

    # CRITICAL patterns (for Learn Monitor)
    critical_patterns = [
        (r'\d+\.\s+(click|select|go to)', 'UI navigation steps'),
        (r'portal-walkthrough', 'Playbook step reference'),
    ]

    # HIGH patterns
    high_patterns = [
        (r'(deprecated|removed|retired)', 'Deprecation notice'),
        (r'(Important|Warning|Note):', 'Policy callout'),
        (r'(required|must|prohibited)', 'Requirement language'),
    ]

    # MEDIUM patterns
    medium_patterns = [
        (r'(enable|disable|configure)', 'Configuration change'),
    ]

    # NOISE patterns
    noise_patterns = [
        (r'ms\.(date|author|reviewer)', 'Metadata update'),
        (r'(Article|Contributor|Feedback)', 'Page chrome'),
    ]

    # Check patterns in order: CRITICAL → HIGH → MEDIUM → NOISE
    for line in diff_lines:
        if line.startswith(('+', '-')):
            for pattern, reason in critical_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return ('critical', reason, '\n'.join(diff_lines[:100]))
            for pattern, reason in high_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return ('high', reason, '\n'.join(diff_lines[:100]))

    # Default to MEDIUM if not noise
    return ('medium', 'Content update', '\n'.join(diff_lines[:100]))
```

### Pattern 3: Control-to-URL Impact Mapping

**What:** Map monitored URLs back to affected framework controls for targeted updates

**When to use:** When generating change reports to show which documentation needs review

**Example:**
```python
# Source: FSI-AgentGov Learn Monitor (lines 316-372)
def find_affected_files(url: str, docs_dir: Path) -> dict:
    """
    Find controls and playbooks that reference this URL.
    Returns: {'controls': [...], 'playbooks': [...]}
    """
    affected = {'controls': [], 'playbooks': []}

    # Scan controls
    for pillar_dir in (docs_dir / 'controls').glob('pillar-*'):
        for control_file in pillar_dir.glob('*.md'):
            content = control_file.read_text(encoding='utf-8')
            if url in content:
                control_id = control_file.stem.split('-')[0]
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                affected['controls'].append({
                    'control_id': control_id,
                    'title': title_match.group(1) if title_match else control_file.stem,
                    'file_path': str(control_file.relative_to(docs_dir)),
                })

    # Scan playbooks (similar pattern)
    for playbook_file in (docs_dir / 'playbooks').rglob('*.md'):
        content = playbook_file.read_text(encoding='utf-8')
        if url in content:
            priority = 'CRITICAL' if 'portal-walkthrough' in str(playbook_file) else 'HIGH'
            affected['playbooks'].append({
                'file_path': str(playbook_file.relative_to(docs_dir)),
                'priority': priority,
            })

    return affected

def determine_priority(change: ChangeRecord) -> str:
    """Escalate priority if critical files affected."""
    if any(p.get('priority') == 'CRITICAL' for p in change.affected_playbooks):
        return 'CRITICAL'
    if change.affected_playbooks or change.classification == 'meaningful':
        return 'HIGH'
    if change.affected_controls:
        return 'MEDIUM'
    return 'LOW'
```

### Anti-Patterns to Avoid

- **Polling too frequently:** Daily is appropriate for regulatory/documentation sources; hourly adds load without value
- **Storing full content in state:** Hash + normalized content is sufficient; raw HTML wastes space
- **Complex HTML parsing:** BeautifulSoup's simple selectors beat regex for HTML; don't hand-roll parsing
- **Ignoring redirects:** Track and report URL redirects to keep watchlist current
- **Auto-merging AI edits:** Always require human review for regulatory content updates

---

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RSS feed parsing | Custom XML parser | `feedparser` library | Handles RSS 2.0, Atom 1.0, RDF; character encoding edge cases; malformed feeds |
| HTML content extraction | Regex-based parsing | BeautifulSoup | HTML is not regular; BeautifulSoup handles malformed HTML, nested tags, encoding |
| Change detection | Character-by-character diff | `difflib.unified_diff` | Standard library, proven, produces readable diffs |
| Hash comparison | Custom checksum | `hashlib.sha256` | Cryptographically sound, collision-resistant, standard |
| Datetime handling | String manipulation | `datetime` with `timezone.utc` | Timezone-aware, ISO 8601 formatting, portable |
| URL redirects | Manual tracking | `requests` with `allow_redirects=True` | Handles 301/302/307/308, multiple hops, circular detection |

**Key insight:** Content monitoring looks simple ("just fetch and compare") but has many edge cases (encoding, malformed HTML, redirects, rate limiting, timeout handling). Using proven libraries avoids reinventing these solutions.

---

## Common Pitfalls

### Pitfall 1: False Positives from Dynamic Content

**What goes wrong:** Every run reports "changes" because timestamps, session IDs, or ad content changed

**Why it happens:** Monitoring raw HTML includes page chrome (headers, footers, ads, metadata) that changes frequently

**How to avoid:**
- Normalize content during extraction (see Pattern 1 above)
- Remove non-content elements (`<script>`, `<style>`, `<nav>`, metadata)
- Mask dynamic patterns (`[DATE]` replacement for timestamps)
- Store normalized content, not raw HTML

**Warning signs:**
- State file growing rapidly (multiple GB)
- Every run reports changes for same URLs
- Diff output shows only metadata/formatting changes

### Pitfall 2: Regulatory Source Overload

**What goes wrong:** Monitoring all FINRA/SEC/Federal Register content produces thousands of irrelevant alerts

**Why it happens:** Regulatory agencies publish content across all industries; most is not FSI AI agent-specific

**How to avoid:**
- **Pre-filter sources:** Monitor specific RSS feeds (e.g., FINRA Regulatory Notices, not all FINRA content)
- **Keyword filtering AFTER fetch:** Extract title/summary, check for FSI/AI keywords before deep analysis
- **Human triage expected:** Regulatory monitoring produces candidates for review, not auto-updates
- **Start narrow, expand gradually:** Begin with 5-10 high-value sources, add more based on relevance rate

**Warning signs:**
- >50 regulatory "changes" per week
- <10% of flagged changes are actually relevant
- Reviewer fatigue from triaging noise

### Pitfall 3: AI Review Skill Not Validated

**What goes wrong:** Skill exists in `.claude/skills/review-learn-changes.md` but hasn't been tested end-to-end

**Why it happens:** Design document created but implementation validation deferred

**How to avoid:**
- Test skill against real change report (e.g., `reports/learn-changes/learn-changes-2026-02-01.md`)
- Validate all 8 change categories (DATE_UPDATE, UI_CHANGE, FEATURE_GA, etc.)
- Verify Edit tool produces correct changes
- Confirm `mkdocs build --strict` passes after edits
- Document any gaps between design and reality

**Warning signs:**
- Skill invocation produces errors
- Proposed edits don't match change report content
- Validation fails after applying edits
- Categories misclassified (e.g., POLICY_CHANGE marked as SKIP)

### Pitfall 4: Monitoring Without Maintenance Budget

**What goes wrong:** Monitors run, reports pile up, no one reviews them, system becomes noise

**Why it happens:** Monitoring is easy to set up, hard to sustain without dedicated review time

**How to avoid:**
- **Allocate review time:** User specified ~30 min/week in CONTEXT.md; this is realistic if noise is minimized
- **Batching:** Weekly review of daily runs is more efficient than daily interruptions
- **Auto-triage HIGH only:** Don't send alerts for MEDIUM/NOISE; summarize weekly
- **Measure signal-to-noise:** Track "alerts reviewed" vs. "documentation updates made"; aim for >25% conversion

**Warning signs:**
- Reports older than 2 weeks unreviewed
- PRs created but never merged
- Team discussing "turning off the monitor"
- Review time creeping toward 1+ hour/week

### Pitfall 5: State File Corruption Recovery

**What goes wrong:** State file gets corrupted (invalid JSON, truncated write, git conflict), monitor crashes

**Why it happens:** Concurrent writes, disk full, git merge conflict in state file

**How to avoid:**
- **Atomic writes:** Write to temp file, then rename (atomic operation)
- **Backup before overwrite:** Keep `state.json.bak` with previous successful run
- **Validation on load:** Try to parse JSON, fall back to empty state if corrupt
- **Git conflict detection:** Check for conflict markers before parsing

**Warning signs:**
- Monitor exits with code 2 (error)
- State file contains `<<<<<<< HEAD` conflict markers
- State file size 0 bytes
- JSON parse errors in logs

---

## Code Examples

Verified patterns from Learn Monitor and industry best practices:

### Fetching Content with Retry Logic

```python
# Source: FSI-AgentGov learn_monitor.py (lines 172-211)
import requests
import time

def fetch_page(url: str, session: requests.Session, max_retries: int = 3) -> dict:
    """Fetch page with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=30, allow_redirects=True)

            # Handle rate limiting
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 60))
                print(f"  Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            return {
                'status_code': response.status_code,
                'content': response.text if response.status_code == 200 else "",
                'final_url': response.url,
                'was_redirected': response.url != url,
                'error': None
            }

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                return {
                    'status_code': 0,
                    'content': "",
                    'final_url': url,
                    'was_redirected': False,
                    'error': str(e)
                }
            # Exponential backoff: 1s, 2s, 4s
            time.sleep(2 ** attempt)

    return {'status_code': 0, 'content': "", 'error': "Max retries exceeded"}
```

### Parsing RSS Feeds for Regulatory Notices

```python
# Source: feedparser documentation + FSI regulatory monitoring requirements
import feedparser
from datetime import datetime, timezone, timedelta

def fetch_regulatory_rss(feed_url: str, since_date: datetime = None) -> list:
    """
    Fetch RSS feed and return entries published after since_date.

    Args:
        feed_url: RSS feed URL (e.g., FINRA regulatory notices)
        since_date: Only return entries newer than this date

    Returns:
        List of entries with {title, link, published, summary}
    """
    feed = feedparser.parse(feed_url)

    if feed.bozo:  # Feed parsing error
        print(f"Warning: Feed parse error for {feed_url}: {feed.bozo_exception}")
        return []

    entries = []
    for entry in feed.entries:
        # Parse publish date (handle various RSS date formats)
        published = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

        # Filter by date if specified
        if since_date and published and published < since_date:
            continue

        entries.append({
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': published.isoformat() if published else None,
            'summary': entry.get('summary', ''),
        })

    return entries
```

### Classifying FSI Relevance for Regulatory Content

```python
# Source: FSI-AgentGov requirements (FINRA/SEC focus on AI agents)
import re

def classify_fsi_relevance(title: str, summary: str) -> tuple[bool, str]:
    """
    Determine if regulatory content is relevant to FSI AI agent governance.

    Returns:
        (is_relevant, reason)
    """
    text = f"{title} {summary}".lower()

    # HIGH relevance: AI + FSI intersection
    high_patterns = [
        (r'\bai\b|\bartificial intelligence\b|machine learning|\bllm\b|generative', 'AI-specific'),
        (r'copilot|power (platform|apps)|agent|chatbot|automation', 'AI agent platforms'),
        (r'finra (rule )?(3110|4511|2210)|sec 17a-[34]|reg s-p|glba', 'FSI AI regulations'),
        (r'supervision|compliance|audit|record[- ]?keeping|retention', 'Supervision/compliance'),
    ]

    for pattern, reason in high_patterns:
        if re.search(pattern, text):
            return (True, reason)

    # MEDIUM relevance: General FSI (capture for triage)
    medium_patterns = [
        (r'broker[- ]?dealer|investment advis(or|er)|registered representative', 'FSI entities'),
        (r'customer|client|suitability|disclosure|communication', 'Customer interaction'),
        (r'cybersecurity|data protection|privacy|breach', 'Security/privacy'),
    ]

    for pattern, reason in medium_patterns:
        if re.search(pattern, text):
            return (True, f"FSI general ({reason})")

    return (False, 'Not FSI AI agent-related')
```

### Atomic State File Writing

```python
# Source: Best practice for preventing state corruption
import json
from pathlib import Path
import shutil

def save_state_atomic(state: dict, state_path: Path):
    """
    Save state file atomically to prevent corruption.
    Creates backup, writes to temp, then renames.
    """
    state_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing state if it exists
    if state_path.exists():
        backup_path = state_path.with_suffix('.json.bak')
        shutil.copy2(state_path, backup_path)

    # Write to temporary file
    temp_path = state_path.with_suffix('.json.tmp')
    temp_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

    # Atomic rename (overwrites existing file)
    temp_path.replace(state_path)

    # Remove backup if write succeeded
    if backup_path.exists():
        backup_path.unlink()
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual URL checking | Automated hash-based detection | 2020s | Scales to hundreds of URLs with zero manual effort |
| Store full HTML | Store normalized content + hash | 2020s | Reduces state file size by 80-90%, faster comparisons |
| Regex HTML parsing | BeautifulSoup/lxml | 2010s | Handles malformed HTML, nested tags, encoding correctly |
| Single diff output | Tiered classification (CRITICAL/HIGH/MEDIUM/NOISE) | 2024+ | Prioritizes human review time, reduces alert fatigue |
| Manual documentation updates | AI-assisted draft generation | 2024+ (emerging) | Reduces documentation lag, maintains quality with human oversight |

**Deprecated/outdated:**
- **Beautiful Soup 3:** Use Beautiful Soup 4 (BS3 deprecated since 2012)
- **`urllib` for HTTP:** Use `requests` (better API, handles encoding, redirects, sessions)
- **`xml.etree` for RSS:** Use `feedparser` (handles RSS/Atom variants, encoding, malformed feeds)
- **Synchronous-only monitoring:** Consider async (`aiohttp`) only if monitoring >1000 URLs; overkill for current scope

---

## Regulatory Monitoring - Recommended Sources

Based on CONTEXT.md requirement: "Monitor official sources directly: FINRA.org, SEC.gov, Federal Register, state legislature sites"

### Tier 1: RSS Feeds (Simplest, Most Reliable)

| Source | RSS URL | Coverage | Cadence |
|--------|---------|----------|---------|
| **FINRA Regulatory Notices** | https://www.finra.org/rules-guidance/notices (has email subscription, check for RSS) | All FINRA regulatory notices, proposed rules | Weekly check |
| **SEC Proposed Rules** | Likely available via SEC.gov RSS (verify) | SEC rulemaking activity | Weekly check |
| **Federal Register** | Use Federal Register API (JSON endpoint) | All federal agency rules (filter for SEC/CFTC/OCC) | Weekly check |

**Note:** Per WebFetch of FINRA notices page, RSS feed not confirmed. FINRA offers [email subscription service](https://www.finra.org/compliance-tools/regulatory-news-feed-and-email-subscription-services). Regulatory monitor should start with email → manual review until RSS/API confirmed.

### Tier 2: Federal Register API (Structured, Reliable)

```python
# Source: Federal Register API documentation
# https://www.federalregister.gov/developers/documentation/api/v1

import requests

def fetch_federal_register_documents(agencies: list, since_date: str) -> list:
    """
    Fetch Federal Register documents from specified agencies.

    Args:
        agencies: List of agency slugs (e.g., ['securities-and-exchange-commission', 'commodity-futures-trading-commission'])
        since_date: ISO date string (e.g., '2026-01-01')

    Returns:
        List of documents with title, url, publication_date, type
    """
    base_url = "https://www.federalregister.gov/api/v1/documents.json"

    params = {
        'conditions[agencies][]': agencies,
        'conditions[publication_date][gte]': since_date,
        'conditions[type][]': ['RULE', 'PRORULE', 'NOTICE'],  # Rules and notices
        'per_page': 100,
        'order': 'newest',
    }

    response = requests.get(base_url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    results = data.get('results', [])

    return [{
        'title': doc['title'],
        'url': doc['html_url'],
        'publication_date': doc['publication_date'],
        'type': doc['type'],
        'abstract': doc.get('abstract', ''),
        'agencies': [a['name'] for a in doc.get('agencies', [])],
    } for doc in results]

# Usage example
docs = fetch_federal_register_documents(
    agencies=['securities-and-exchange-commission', 'commodity-futures-trading-commission'],
    since_date='2026-01-27'  # Last week
)

# Filter for AI/agent relevance
for doc in docs:
    text = f"{doc['title']} {doc['abstract']}".lower()
    if any(keyword in text for keyword in ['artificial intelligence', 'ai', 'machine learning', 'automated']):
        print(f"RELEVANT: {doc['title']}")
        print(f"  URL: {doc['url']}")
        print(f"  Date: {doc['publication_date']}")
```

### Tier 3: State AI Laws (Manual for Now, Automate Later)

User CONTEXT.md specifies: "Broad FSI capture: don't pre-filter to AI-only keywords; capture all FSI regulatory changes"

**Recommended approach:**
1. **Start manual:** Quarterly review of state legislature sites for Colorado, Texas, Illinois, California, NYC
2. **Future automation:** State legislature RSS feeds vary by state; assess in Phase 8 planning if automation value justifies complexity
3. **Current baseline:** CHANGELOG shows state AI law monitoring from v1.2.20-v1.2.31; this was manual research

---

## Unified Monitoring System Design

Based on CONTEXT.md requirement: "Unified monitoring approach — combine Learn documentation and regulatory monitoring into one coherent strategy"

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Unified Monitoring System                      │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Learn Monitor   │         │ Regulatory       │         │
│  │                  │         │ Monitor          │         │
│  │  - 209 Learn URLs│         │ - FINRA RSS      │         │
│  │  - Daily run     │         │ - Federal Reg API│         │
│  │  - 4-tier class  │         │ - SEC sources    │         │
│  └────────┬─────────┘         └─────────┬────────┘         │
│           │                             │                  │
│           └──────────┬──────────────────┘                  │
│                      │                                     │
│           ┌──────────▼──────────┐                          │
│           │  Shared Utilities   │                          │
│           │                     │                          │
│           │  - fetch_content()  │                          │
│           │  - normalize()      │                          │
│           │  - compute_hash()   │                          │
│           │  - classify_change()│                          │
│           │  - find_affected()  │                          │
│           └──────────┬──────────┘                          │
│                      │                                     │
│           ┌──────────▼──────────┐                          │
│           │  Report Generator   │                          │
│           │                     │                          │
│           │  - Markdown reports │                          │
│           │  - 4-tier priority  │                          │
│           │  - Control mapping  │                          │
│           └──────────┬──────────┘                          │
│                      │                                     │
│           ┌──────────▼──────────┐                          │
│           │  AI-Assisted Review │                          │
│           │                     │                          │
│           │  /review-learn-     │                          │
│           │  changes skill      │                          │
│           └─────────────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key design decisions:**

1. **Separate monitors, shared utilities:** Learn Monitor and Regulatory Monitor are separate scripts using shared `monitoring_shared.py` module
2. **Separate state files:** `data/learn-monitor-state.json` and `data/regulatory-monitor-state.json` to avoid conflicts
3. **Separate report directories:** `reports/learn-changes/` and `reports/regulatory-changes/` for clarity
4. **Unified classification:** Both use 4-tier CRITICAL/HIGH/MEDIUM/NOISE system
5. **Unified review workflow:** AI-assisted review skill extended to handle both report types
6. **Different cadences:** Learn Monitor daily (existing), Regulatory Monitor weekly (lower change frequency)

---

## Open Questions

Things that couldn't be fully resolved:

1. **FINRA RSS Feed Availability**
   - What we know: FINRA offers [email subscription service](https://www.finra.org/compliance-tools/regulatory-news-feed-and-email-subscription-services), web notices page exists
   - What's unclear: Whether FINRA provides RSS feed or API (WebFetch did not confirm)
   - Recommendation: Start with manual email subscription → copy links to watchlist; investigate API in Phase 8 planning

2. **AI Review Skill Validation Status**
   - What we know: `.claude/skills/review-learn-changes.md` exists with 197 lines of detailed workflow, designed in v1.2.37
   - What's unclear: Has it been tested end-to-end against real change report?
   - Recommendation: Phase 8 Task 1 should be "Validate AI review skill against latest change report"

3. **Optimal Regulatory Monitor Cadence**
   - What we know: Daily is overkill for regulatory sources (low change frequency), user wants configurable cadence
   - What's unclear: Is weekly sufficient, or should some sources run daily (e.g., Federal Register)?
   - Recommendation: Start weekly for all regulatory sources, add daily option for high-priority sources after data collection

4. **State AI Law Automation Value**
   - What we know: State AI laws (Colorado, Texas, Illinois, California, NYC) were tracked manually in v1.2.20-v1.2.31
   - What's unclear: Do state legislatures offer RSS/APIs? Is automation worth complexity vs. quarterly manual review?
   - Recommendation: Keep manual for Phase 8; assess automation in Phase 9+ if review burden exceeds 30 min/quarter

5. **Control-to-Regulatory-Source Mapping**
   - What we know: Learn Monitor maps URLs to affected controls via content search (lines 316-372)
   - What's unclear: How to map regulatory notices to controls (not embedded in documentation like Learn URLs)
   - Recommendation: Regulatory reports should include keyword-based suggestions (e.g., "mentions 'supervision' → see Control 2.12") but require human triage

---

## Sources

### Primary (HIGH confidence)

- **FSI-AgentGov Learn Monitor Script** - `/Users/admin/dev/FSI-AgentGov/scripts/learn_monitor.py` (857 lines, production code)
- **Learn Monitor Workflow** - `.github/workflows/learn-monitor.yml` (215 lines, daily execution)
- **Learn Monitor Guide** - `docs/reference/learn-monitor-guide.md` (current implementation documentation)
- **AI Enhancement Design** - `docs/reference/learn-monitor-ai-enhancement.md` (design document for AI-assisted review)
- **AI Review Skill** - `.claude/skills/review-learn-changes.md` (197 lines, workflow implementation)
- **Federal Register API Documentation** - [Federal Register API v1](https://www.federalregister.gov/developers/documentation/api/v1) (official REST API, no key required)
- **Federal Register Developer Resources** - [Reader Aids](https://www.federalregister.gov/reader-aids/developer-resources/rest-api) (CSV/JSON endpoints, search functionality)

### Secondary (MEDIUM confidence)

- **FINRA Regulatory News Feed and Email Subscription Services** - [FINRA.org](https://www.finra.org/compliance-tools/regulatory-news-feed-and-email-subscription-services) (confirmed email subscription, RSS not confirmed)
- **FINRA 2026 Annual Regulatory Oversight Report** - [FINRA.org](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report) (GenAI section, supervision guidance)
- **FeedParser Guide** - [ScrapeOps](https://scrapeops.io/python-web-scraping-playbook/feedparser/) (Parse RSS, Atom & RDF feeds with Python)
- **BeautifulSoup Alternatives** - [ZenRows](https://www.zenrows.com/alternative/beautifulsoup), [Oxylabs](https://oxylabs.io/blog/beautifulsoup-alternatives) (industry comparison, requests-html recommended for JS support)
- **Website Change Detection Best Practices 2026** - [UptimeRobot](https://uptimerobot.com/knowledge-hub/monitoring/9-best-website-change-monitoring-tools-compared/), [PageCrawl.io](https://pagecrawl.io/blog/complete-guide-website-monitoring-2026) (hash-based detection, smart filtering, element-specific monitoring)

### Tertiary (LOW confidence)

- **Regulations.gov API** - [GSA Open Technology](https://open.gsa.gov/api/regulationsgov/) (federal rulemaking API, broader than Federal Register)
- **n8n Webpage Change Detection Workflow** - [n8n.io](https://n8n.io/workflows/3366-webpage-change-detection-and-alerts-with-google-suite-and-hash-tracking/) (hash tracking workflow template)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Production Learn Monitor uses requests + BeautifulSoup successfully
- Architecture patterns: HIGH - Extracted from working Learn Monitor code (857 lines, daily execution)
- Regulatory sources: MEDIUM - Federal Register API verified, FINRA RSS not confirmed (email subscription confirmed)
- AI review skill: MEDIUM - Skill exists but end-to-end validation status unclear
- Pitfalls: HIGH - Based on Learn Monitor implementation experience and industry best practices

**Research date:** 2026-02-04
**Valid until:** 60 days (regulatory monitoring space is stable; API endpoints rarely change)

**Key limitations:**
- FINRA RSS feed availability requires confirmation during planning
- AI review skill validation status requires testing
- State AI law automation feasibility requires deeper investigation
- Regulatory monitor does not exist as code (greenfield implementation)
