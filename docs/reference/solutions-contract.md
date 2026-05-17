# Solutions Repository Coupling Contract

This page is the **source-of-truth contract** between the FSI-AgentGov framework
repository and the
[FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions)
implementation catalog. It describes how the two repositories are coupled,
which artifacts cross the boundary, and how each side should pin to the
other to avoid silent breakage.

---

## Why a contract

The framework repository (this one) owns the **78-control taxonomy**, the
control manifest at `assessment/manifest/controls.json`, the assessment
engine, and the regulatory-mapping documentation. The Solutions repository
owns the 36 companion solution implementations (35 live + 1 preview) that map
back to those controls.

The Solutions repository validates each solution's `manifest.yaml` against
the framework's `controls.json` to ensure every claimed control mapping is
real. That validation creates a versioning dependency: if the framework
renames or removes a control on `main`, every Solutions PR that consumes
the framework from `main` will red-line at the same instant — even if the
Solutions change is unrelated.

To keep both repositories releasable, **the Solutions repository must pin
to a framework release tag, not to `main`**.

---

## Versioned contract

| Boundary artifact | Owner | Consumer | Contract |
|-------------------|-------|----------|----------|
| `assessment/manifest/controls.json` | Framework | Solutions (validation), assessment engine | SemVer; control IDs are stable within a major version |
| Control IDs and pillar numbers | Framework | Solutions, downstream docs | Removal or renumbering = **major** version bump |
| Pass-condition strings (`pass_condition`) | Framework | Assessment engine evaluators | Renaming = **minor** unless the evaluator is also updated atomically |
| Solution → control mappings | Solutions | Framework `solutions-integration.md` | Solutions cite framework tag in `manifest.yaml` |
| Generated `solutions.json` (counts + per-solution version/status/controls) | Solutions | Framework `assessment/data/solutions-lock.json`, `solutions-index.md`, prose validators | Solutions repo publishes per-tag artifacts; framework pins the JSON into `solutions-lock.json` for reproducible builds |

### Framework commitments

For any framework release `vX.Y.Z`:

1. The 78 control IDs and their pillar assignments are stable within
   the same **major** version.
2. The `pass_condition` strings used by registered evaluators are stable
   within the same **minor** version. Adding a new `pass_condition` is a
   minor change; renaming an existing one is a major change.
3. The shape of `controls.json` (top-level array of control objects with
   the keys listed in `assessment/manifest/README.md`) is additive within
   a major version — fields may be added but not removed.
4. Bug fixes that change `evaluator_state` rollups (e.g., wiring up a
   missing evaluator) are minor changes. The
   [Assessment Engine Coverage matrix](assessment-coverage.md) shows the
   current state.

### Solutions-side commitments

The Solutions repository is expected to:

1. Pin its framework consumption to a **release tag** (e.g.,
   `framework_version: v1.6.2` in repo-level config), not `main`.
2. Bump the pinned tag deliberately, as part of a release of its own.
3. Treat a framework **major** bump as a planned migration, not an
   incidental dependency update.
4. Re-run cross-repo validation against the new tag in CI before
   updating the pin.

---

## Recommended pinning patterns

There are two patterns the Solutions repository can use. Both are
acceptable; the project should pick one and document it.

### Pattern A — Submodule pin

```bash
# In the Solutions repo, pin the framework as a submodule at a tag.
git submodule add -b v1.6.2 https://github.com/judeper/FSI-AgentGov.git \
    .framework
```

Pros: cryptographically pinned, fully reproducible.
Cons: contributors must remember `git submodule update --init`.

### Pattern B — CI-side fetch-by-tag

In the Solutions repo's validation workflow:

```yaml
- name: Fetch framework manifest at pinned tag
  env:
    FRAMEWORK_TAG: v1.6.2   # update deliberately
  run: |
    curl -fsSL \
      "https://raw.githubusercontent.com/judeper/FSI-AgentGov/${FRAMEWORK_TAG}/assessment/manifest/controls.json" \
      -o .framework/controls.json
```

Pros: zero submodule overhead.
Cons: relies on the consumer to bump `FRAMEWORK_TAG` deliberately.

---

## Compatibility matrix

The Solutions repository is responsible for publishing the matrix below
(or its equivalent) so consumers know which framework tag a given
Solutions release was built against. The framework repository keeps a
mirror only as a courtesy; the authoritative copy lives with the
producer.

| Solutions release | Framework tag | Notes |
|-------------------|---------------|-------|
| _maintained in the Solutions repo_ | _maintained in the Solutions repo_ | This table intentionally left as a pointer — see [FSI-AgentGov-Solutions release notes](https://github.com/judeper/FSI-AgentGov-Solutions/releases) |

---

## When this contract changes

* Framework PRs that touch `controls.json` IDs, pillars, or
  `pass_condition` strings must include a one-line note in the PR
  description identifying the change as additive, minor, or breaking.
* Framework releases that include any breaking change to this contract
  must bump the **major** version and call out the change in the
  release notes.
* The Solutions repository owns its own migration cadence. The
  framework will not delete deprecated control IDs without a deprecation
  release in the prior major version.

---

## Related references

- [Assessment Engine Coverage](assessment-coverage.md) — current
  evaluator state across all 78 controls.
- [Solutions Integration](../framework/solutions-integration.md) —
  high-level architecture of the two-repo system.
- [Solutions Index](solutions-index.md) — current solution catalog.
