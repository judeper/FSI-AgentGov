# AGENTS.md - Instructions for AI Agents

This file provides guidance for autonomous AI agents working on this repository.

## Before Making Changes

1. **Read `.github/copilot-instructions.md`** for full repository context
2. **Understand the task scope** - is it a control edit, nav update, or new feature?
3. **Check related files** - controls often reference each other

## Claude Code Skills

For Claude Code, detailed workflows are available as on-demand skills in `.claude/skills/`:

| Skill | Use When |
|-------|----------|
| `/update-control` | Modifying existing control content |
| `/add-control` | Adding a new control to a pillar |
| `/update-excel` | Maintaining Excel checklist templates |
| `/verify-ui` | Verifying portal screenshots match documentation |

Use these skills for step-by-step guidance on common tasks.

## Agent Workflows

### Add a New Control

1. Read `docs/templates/control-setup-template.md` for required structure
2. Copy template to correct pillar folder: `docs/controls/pillar-{n}-{name}/`
3. Name file: `{id}-{kebab-case-name}.md` (e.g., `1.20-new-control.md`)
4. Fill all 10 sections (plus header and footer metadata) - do not skip any
5. Update these files:
   - `docs/controls/CONTROL-INDEX.md` - add the new control to the master index
   - `mkdocs.yml` - add to navigation under correct pillar
6. Create `docs/images/{control-id}/EXPECTED.md` for screenshot specs
7. Validate: `mkdocs build --strict`

### Update Existing Control

1. Read current control file completely
2. Preserve all 10 sections - do not remove any
3. Update "Updated" in footer (Month-Year)
4. If portal paths changed, update `docs/images/{control-id}/EXPECTED.md`
5. Validate: `mkdocs build --strict`

### Verify Screenshots

1. Read the control's `.md` file in `docs/controls/pillar-{n}-*/`
2. Read `docs/images/{control-id}/EXPECTED.md` for required screenshots
3. Read `docs/images/VERIFY.md` for detailed verification workflow
4. Compare portal instructions in control doc against screenshot requirements
5. Report: matches, discrepancies, or outdated UI elements

### Update Navigation

1. Edit `mkdocs.yml` - the `nav:` section defines site structure
2. Maintain alphabetical/numerical order within pillars
3. Validate: `mkdocs build --strict`

## Language Guidelines

When writing control documentation:
- **Avoid:** "ensures compliance", "guarantees", "will prevent"
- **Use:** "supports compliance with", "helps meet", "required for"
- Include caveats about implementation requirements

## Validation Commands

Always run before completing work:

```bash
mkdocs build --strict          # Validates links and structure
python scripts/verify_controls.py   # Validates control files
```

## Files to Never Modify Without Permission

- `LICENSE` - Legal file
- `SECURITY.md` - Security policy
- `CODE_OF_CONDUCT.md` - Community standards

## Advanced Implementations

Advanced implementations are complex multi-control solutions in `docs/playbooks/advanced-implementations/`.

### Platform Change Governance

Location: `docs/playbooks/advanced-implementations/platform-change-governance/`

A Dataverse-based solution for operationalizing Microsoft Message Center changes with regulatory-aligned audit trails. Includes:
- Architecture documentation (Dataverse schema, security model)
- Two implementation paths (Dataverse-only vs. Dataverse + Azure DevOps)
- Hands-on labs
- Evidence standards for regulatory examinations

**Companion Repository:** FSI-AgentGov-Solutions contains deployment scripts and solution files.

## Error Handling

If you encounter:
- **Broken links:** Check `mkdocs.yml` nav entries match actual file paths
- **Missing sections in controls:** Refer to `docs/templates/control-setup-template.md`
