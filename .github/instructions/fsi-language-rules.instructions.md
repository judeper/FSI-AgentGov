---
applyTo: "docs/**/*.md"
---

# FSI Regulatory Language Rules

When writing or editing documentation in this repository, follow these mandatory language guidelines to avoid legal liability.

## Prohibited Phrases (NEVER use)

| Prohibited | Risk |
|-----------|------|
| "ensures compliance" | Implies legal guarantee |
| "guarantees" | Creates liability |
| "will prevent" | Overclaim |
| "eliminates risk" | Unrealistic |

## Required Alternatives (ALWAYS use)

| Use This | Instead Of |
|----------|-----------|
| "supports compliance with" | "ensures compliance with" |
| "helps meet" | "guarantees compliance" |
| "required for" | "will ensure" |
| "recommended to" | "guarantees" |
| "aids in" | "eliminates the need for" |

## Examples

```markdown
# WRONG
This control ensures you meet SEC 17a-4 requirements.

# RIGHT
This control helps support SEC 17a-4 requirements. Implementation requires...
```

```markdown
# WRONG
Enabling audit logging guarantees regulatory compliance.

# RIGHT
Enabling audit logging aids in meeting regulatory record-keeping requirements. Organizations should verify configuration meets their specific obligations.
```

## Additional Rules

- Include implementation caveats where appropriate ("Implementation requires...", "Organizations should verify...")
- Reference specific regulations by name and section (e.g., "FINRA Rule 4511(a)")
- Do not claim that any single control satisfies a regulation in isolation
- Use "supports", "contributes to", "helps address" for regulatory mapping language

## Role Naming

Use canonical short names from `docs/reference/role-catalog.md`:

| Use This | NOT This |
|----------|----------|
| Entra Global Admin | Global Administrator |
| Purview Compliance Admin | Compliance Administrator |
| Power Platform Admin | Power Apps Admin |
| Exchange Online Admin | Exchange Administrator |
