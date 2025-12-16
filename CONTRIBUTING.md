# Contributing to FSI Agent Governance Framework

Thank you for your interest in contributing to the FSI Agent Governance Framework!

## How to Contribute

### Reporting Issues

1. Check existing [Issues](../../issues) to avoid duplicates
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

Control files in `docs/reference/pillar-*/` must follow the standard structure:

**Required Sections:**
1. **Overview** - Control ID, name, regulatory reference, setup time
2. **Governance Levels** - Baseline (Level 1), Recommended (Level 2-3), Regulated (Level 4)
3. **Verification & Testing** - Step-by-step verification procedures with expected results
4. **Implementation Guidance** - 5-step process (Assess, Implement, Verify, Document, Review)
5. **Regulatory Context** - Primary regulations and applicability statement
6. **Related Controls** - Cross-references to other controls
7. **Support & Questions** - Contact information

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

## Questions?

Open a [Discussion](../../discussions) or contact the maintainers.

---

*FSI Agent Governance Framework v1.0 Beta*
