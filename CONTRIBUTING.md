# Contributing to FSI Agent Governance Framework

Thank you for your interest in contributing to the FSI Agent Governance Framework!

## How to Contribute

### Reporting Issues

1. Check existing [Issues](https://github.com/judeper/FSI-AgentGov/issues) to avoid duplicates
2. Use the appropriate issue template (Bug Report or Feature Request)
3. Provide as much detail as possible

### Suggesting Enhancements

- For new controls: Include regulatory reference and implementation guidance
- For documentation: Describe the gap and proposed content
- For templates: Explain the use case and expected format

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test with `mkdocs build --strict`
5. Submit a pull request with a clear description

## Style Guidelines

### Documentation
- Use Markdown with consistent formatting
- Include version footer on all pages
- Reference control IDs where applicable

### Control Files

Control files in `docs/controls/pillar-*/` must follow the standard structure:

**Required Sections:**

Controls follow a standardized format with header metadata, 10 sections, and footer metadata:

**Header Metadata:**
- Control ID, Pillar, Regulatory Reference, Last UI Verified, Governance Levels

**10 Required Sections:**
1. **Objective** - Concise purpose statement
2. **Why This Matters for FSI** - Regulatory bullet points
3. **Control Description** - Detailed technical explanation
4. **Key Configuration Points** - Bulleted configuration items
5. **Zone-Specific Requirements** - Zone 1/2/3 table with requirements and rationale
6. **Roles & Responsibilities** - Admin roles table
7. **Related Controls** - Cross-reference table with relationships
8. **Implementation Guides** - Links to 4 playbooks (portal, powershell, verification, troubleshooting)
9. **Verification Criteria** - Verification checklist
10. **Additional Resources** - Microsoft Learn links

**Footer Metadata:**
- *Updated: Month-Year | Version: v1.1 | UI Verification Status: Current*

**Administrator Role Naming:**
- Use the framework's canonical short role names (e.g., "Power Platform Admin", "Purview Compliance Admin").
- Avoid inconsistent synonyms ("Global Admin" vs "Global Administrator").
- See `docs/reference/role-catalog.md` for canonical names and accepted aliases.

**Language Guidelines:**
- Avoid overclaims like "ensures compliance" or "guarantees"
- Use "supports compliance with" instead of "ensures compliance with"
- Use "required for" or "helps meet" instead of "guarantees"
- Include implementation caveats where appropriate

**Regulatory Mapping:**
- Reference specific regulation sections (e.g., "SEC 17a-3/4" not just "SEC")
- Map to FINRA, SEC, SOX, GLBA, OCC, or Fed SR 11-7 as applicable
- Update `docs/reference/regulatory-mappings.md` if adding new mappings

**Testing:**
```bash
mkdocs build --strict  # Validates links and structure
mkdocs serve           # Preview locally at http://localhost:8000
```

## AI Agent Context

If you're using AI assistants with this repository:

- **`.github/copilot-instructions.md`** - Repository-wide context for GitHub Copilot
- **`.claude/claude.md`** - Context and workflows for Claude Code (interactive pair programming)
- **`AGENTS.md`** - Instructions for autonomous agent tasks
- **`docs/templates/README.md`** - Guide to using control templates

These files help AI assistants understand the project structure, coding conventions, and common workflows.

## Screenshot Verification

Screenshots for verifying portal instructions are stored locally (not pushed to GitHub):

- **Location:** `docs/images/{control-id}/`
- **EXPECTED.md** in each folder lists required screenshots
- **README.md** and **VERIFY.md** explain conventions and workflow

See `docs/images/VERIFY.md` for the full verification process.

## Maintainers: Public Release Checklist

When preparing a public/beta update, confirm these repo-level settings and docs are consistent:

- **GitHub Pages**: Enabled and publishing via **GitHub Actions** (or correctly configured `gh-pages`), and the site is publicly accessible at the configured `site_url`.
- **Repo “About” metadata**: Add a short description, relevant topics, and set the **Website** field to the docs URL.
- **Offline deliverables scope**: Ensure user-facing docs consistently state **web docs + Excel templates only** (no Word/PDF bundle).
- **CI health**: `publish_docs.yml` and `link-check.yml` are green on `main`.

## Questions?

Open an [Issue](https://github.com/judeper/FSI-AgentGov/issues) or contact the maintainers.

---

*FSI Agent Governance Framework v1.1 - January 2026*
