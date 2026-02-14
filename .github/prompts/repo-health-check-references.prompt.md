---
name: "repo-health-check-references"
description: "[3/3] Validate Learn links, terminology, and regulatory citations — requires web access"
tools: ["read", "search", "web"]
---

<objective>
Validate external references, Microsoft terminology currency, and regulatory citation accuracy. This check requires web access for URL validation. If web access is unavailable, skip URL checks and run only the offline checks.
</objective>

<instructions>

## Output Rules

- One line per finding: `🔴|🟡|🔵 file:line — description`
- For Learn URLs: report ONLY broken ones (404, permanent redirect)
- Do not list working URLs
- Do not exceed 80 lines of output
- Skip any check with zero findings

## Prerequisites

**Web access required for Check 1.** If unavailable, skip it and note: "Learn URL validation skipped — no web access."

---

## Checks

1. **Microsoft Learn URL validation:** Extract unique `learn.microsoft.com` URLs from `docs/**/*.md`. Fetch each and report only those returning 404 or permanent redirects to a different page. Format: `🔴 file — URL (HTTP status)`

2. **Deprecated Microsoft terminology:** Search `docs/**/*.md` for outdated terms. **Exclude occurrences inside code blocks (```) and inline code (`)** as these may reference actual cmdlet names or UI strings.
   - "Azure Active Directory" or "Azure AD" → should be "Microsoft Entra ID"
   - "Office 365" → should be "Microsoft 365"
   - "Power Apps portal" → should be "Power Pages"
   - "Common Data Service" or "CDS" → should be "Dataverse"

3. **Regulatory citation specificity:** In control files (`docs/controls/**/*.md`), find regulatory references (FINRA, SEC, SOX, GLBA, OCC, CFTC) that lack specific rule/section numbers. Flag vague citations like just "FINRA" without "Rule 4511(a)". Exclude table headers and column names.

---

## Output Format

```
# External Reference Validation Report
**Date:** {date}
**Issues:** {total} (🔴 {n} / 🟡 {n} / 🔵 {n})

## Findings
[One line per finding, grouped by check number]
```

</instructions>
