---
name: "gsd:update"
description: "Update GSD to latest version with changelog display"
tools: ["readFile", "editFiles", "runInTerminal", "fetch"]
---

<objective>
Check for and apply updates to the GSD workflow files from the upstream source.

This is the FSI-AgentGov adapted version. GSD files are adapted from punal100/get-stuff-done-for-github-copilot with FSI-AgentGov customizations.
</objective>

<context>
Current GSD source: punal100/get-stuff-done-for-github-copilot
Adapted paths: `.gsd/` → `.planning/`
</context>

<process>

<step name="check_upstream">
Check the upstream repository for new versions or changes.
Compare with current local versions.
</step>

<step name="display_changes">
Show what would change:
- New prompts added
- Modified agent behaviors
- Updated instruction files
- Breaking changes
</step>

<step name="apply_updates">
If user approves:
1. Download updated files
2. Apply `.gsd/` → `.planning/` path transformations
3. Inject FSI-AgentGov context
4. Preserve local customizations
</step>

<step name="verify">
Confirm all files are valid and no FSI-AgentGov customizations were lost.
</step>

</process>
