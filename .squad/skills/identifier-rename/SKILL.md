# SKILL: Cross-File Structural Identifier Rename

## When to use

When an issue asks to rename structural identifiers (function names, anchor IDs, test names, namespace tags, JSON field names) that are spread across multiple large documentation files, with full inbound-link updates.

## The Pattern

### Phase 1 — Enumerate COMPLETELY before editing

1. Grep the WHOLE repo (not just target files) for the pattern.
2. For each identifier, collect:
   - Definition location (function `def`, heading that generates anchor, etc.)
   - All inbound references (links, calls, JSON values, test tags, file names)
   - Whether each hit is a STRUCTURAL artifact or LEGITIMATE content
3. Build a complete rename map BEFORE touching any file.
4. Flag "LEAVE IT" candidates where uncertain — conservative is safer.

**Scorched-earth rule:** Do NOT rely on sampling. Every prior sampling pass missed P0 issues.

### Phase 2 — Rename

Write a Python script (not inline PS) for the actual replacements:

```python
def rpl(path, old, new, count=0):
    text = path.read_text(encoding="utf-8")
    n = text.count(old)
    if n == 0:
        print(f"  MISSING: {path.name}")
        return
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"  OK ({n}x): {path.name}")
```

**Ordering matters:** When identifier A is renamed and identifier B references A's new name in a "renamed from A to B" sentence, the sentence will read "from B to B" after the rename. Write the admonition body AFTER renames using arrow notation that avoids the substitution pattern: `A → B` instead of `` `A` to `B` ``.

**Chain renames carefully:**
- When `$varOld` → `$varNew` AND `FieldOld = $varOld` → `FieldNew = $varNew`, do both in one pass.
- After the variable rename, the field line reads `FieldOld = $varNew`. Target THAT intermediate form for the field rename.

### Phase 3 — Catch quote pollution

When a Python script is embedded in a PowerShell `$script` here-string and uses `\u201c`/`\u201d`:
- These render as LEFT/RIGHT curly double-quote marks (`"` / `"`)
- Always verify with a `check_quotes.py` script after running
- Prefer writing the Python script to a file via `[System.IO.File]::WriteAllText()` or `Set-Content -Encoding UTF8` with explicit straight-quote characters

### Phase 4 — HTML comment variant

Files may have maintainer-note blocks that LOOK like HTML comments but lack the `<!--` opener (a common authoring mistake). The regex `<!--[^>]*?-->` fails on these. Detection:
- Search for `-->` in the file; if no matching `<!--` exists, use a direct string replacement targeted on the first known line of the block.
- Alternatively, use `re.DOTALL` with a pattern anchored on a unique landmark (like the `<a id="...">` anchor that follows the block).

### Phase 5 — Verify ALL of these

1. `mkdocs build --strict` — catches broken anchor links
2. `python scripts/verify_xref_graph.py` — catches broken cross-refs in our custom graph
3. `python scripts/verify_language_rules.py` — catches FSI language violations
4. Sanity re-grep: `broken_id=[]` and `mislabeled=[]` in xref output; ZERO structural identifiers in grep (historical "renamed from X" prose is acceptable)

## Common pitfalls

| Pitfall | Mitigation |
|---|---|
| Namespace rename misses JSON schema examples, Pester test tags, file-name patterns, and Merkle-chain attestation files | Enumerate ALL occurrence types before writing the map |
| Double-rename collision in "renamed from X to Y" prose | Write the prose AFTER renames using arrow notation |
| Curly quotes from PS here-string embedding | Write Python scripts to file; verify with check_quotes.py |
| `<!--` absent from maintainer note blocks | Detect by checking `-->` without `<!--`; use landmark-based regex |
| Missing items in second/third pass | Keep a CHANGES dict and surface MISSING lines as errors |
| Legitimate "preview" status text caught by broad regex | Use word-boundary + case-sensitive patterns; hand-review each hit |
