# Domain Pitfalls: Documentation Architecture Improvements & Solution Completion

**Domain:** Adding documentation architecture changes and completing WIP solutions in mature governance framework
**Researched:** 2026-02-04
**Confidence:** HIGH

---

## Executive Summary

This research identifies pitfalls specific to v2 milestone work: improving documentation architecture and completing WIP solutions in an **existing, production-used framework** with 62 controls, 254 playbooks, and 209 monitored URLs published to GitHub Pages.

Unlike greenfield development, these changes carry **integration risk** — every navigation change affects existing bookmarks, every PowerShell change breaks existing deployments, every YAML config adds maintenance burden. The framework is mature (v1.2.37) with real FSI customers depending on URL stability and script backward compatibility.

**Key insight:** The biggest pitfalls come from **treating incremental improvements as greenfield projects**. What works for new systems often breaks existing workflows. Documentation changes that "improve" navigation can destroy SEO rankings built over months. Security hardening that "fixes" PowerShell scripts breaks production automation. Configuration externalization that "simplifies" maintenance creates YAML sprawl worse than the code it replaced.

This research focuses on **integration pitfalls** — mistakes that happen when adding features to systems with existing users, URLs, and dependencies.

---

## Critical Pitfalls

### Pitfall 1: MkDocs Awesome-Pages Migration Breaks Existing Links

**What goes wrong:** Migrating from manual `mkdocs.yml` navigation to awesome-pages plugin generates different URLs, breaking all existing bookmarks and search engine indexed pages.

**Why it happens:**
- Awesome-pages v3 generates navigation from scratch, ignoring `mkdocs.yml` nav structure
- Plugin uses alphabetical sorting by default; manual nav had semantic ordering
- `.pages` file rename to `.nav.yml` changes discovery logic
- Glob patterns (`*`) replace explicit file lists, changing URL generation order

**Real-world evidence:**
- [Migration from v2 to v3 - Awesome Nav for MkDocs](https://lukasgeiter.github.io/mkdocs-awesome-nav/migration-v3/) documents breaking changes: "In version 3, the plugin ignores a nav that is defined in mkdocs.yml"
- Version 3 was "developed from scratch using a new approach" — not incremental
- Documentation warns: "filtering expressions will require more attention" during migration

**Consequences:**
- Google Search Console shows 404 errors for previously indexed URLs
- Users' browser bookmarks return 404 or redirect to different content
- Internal cross-references break (248 control playbooks referencing each other)
- SEO ranking drops as search engines detect "site migration" signal
- GitHub Pages rebuild changes all canonical URLs overnight

**FSI-AgentGov-specific impact:**
- 254 playbook files with deep linking paths (`/playbooks/control-implementations/1.1/portal-walkthrough/`)
- Users bookmark specific control URLs for compliance audits
- Framework documentation cited in internal FSI compliance policies (URL changes invalidate references)
- 62 controls × 4 playbooks = 248 potential broken links

**Prevention:**

1. **URL preservation testing BEFORE migration:**
   - Generate navigation with awesome-pages in test branch
   - Run `mkdocs build` and compare `site/` directory structure to production
   - Create URL mapping table: old path → new path
   - If ANY URL changes, migration requires redirect strategy

2. **Implement 301 redirects for changed URLs:**
   - Use MkDocs `redirects` plugin to preserve old URLs
   - Document all URL changes in migration changelog
   - Monitor Google Search Console for 404s post-deployment

3. **Staged rollout with fallback:**
   - Deploy awesome-pages to staging environment first
   - Test ALL internal links with link checker
   - Keep `mkdocs.yml` nav structure in version control for 6 months (rollback option)
   - Monitor analytics for traffic drops indicating broken user workflows

4. **Consider NOT migrating:**
   - Manual navigation provides explicit control over URL structure
   - "Maintenance burden" of updating `mkdocs.yml` is low for stable framework
   - Automation is not always improvement — manual nav prevents accidental URL changes

**Detection:**
- Pre-migration: Build both versions, diff `site/` directories for URL changes
- Post-migration: Monitor HTTP 404 rate in GitHub Pages analytics
- Post-migration: Run `mkdocs build --strict` with link validation
- User feedback: Bookmark breakage reports within 48 hours

**Which phase should address:**
- Phase 1: URL Impact Assessment (migration decision point)
- Phase 2: Redirect Implementation (if proceeding)
- Phase 3: Staged Deployment with Rollback Plan

**Reference:** [The Secret Migration: How Site Navigation Changes Can Destroy SEO](https://sitebulb.com/resources/guides/the-secret-migration-how-site-navigation-changes-can-destroy-seo-without-you-realising/)

---

### Pitfall 2: PowerShell Security Hardening Breaks Production Scripts

**What goes wrong:** Adding `#Requires` statements, replacing `ConvertTo-SecureString -AsPlainText`, and adding try/catch blocks causes existing scripts to fail in production FSI environments with restrictive execution policies.

**Why it happens:**
- FSI environments often run older PowerShell versions (5.1 is common, not 7.x)
- Adding `#Requires -Version 7.0` breaks scripts on systems with only 5.1 installed
- Adding `#Requires -Modules Microsoft.Graph.Authentication` breaks when module not pre-installed
- Changing secret handling from `ConvertTo-SecureString -AsPlainText` to `Get-Secret` requires SecretManagement module (not default)
- New error handling changes script behavior — scripts that silently continued now halt with exceptions

**Real-world evidence from v1 audit:**
- Tech debt item: "12 PowerShell scripts missing #Requires statements"
- Tech debt item: "Register-ServicePrincipal.ps1 uses ConvertTo-SecureString -AsPlainText -Force (exposes secrets in process memory)"
- Tech debt item: "Test-PolicyCompliance.ps1 has zero try/catch error handling"
- "PowerShell validation limited to regex (pwsh unavailable on macOS)" — indicates environment constraints

**Consequences:**
- Scripts fail on first run after "security update" deployment
- FSI security teams block script execution due to new module dependencies
- Users with PowerShell 5.1 cannot run scripts requiring 7.x features
- Breaking changes not documented in CHANGELOG — users assume backward compatibility
- Rollback requires Git revert, but customers may have forked repo before changes

**FSI-AgentGov-specific impact:**
- Solutions deployed in production FSI environments (Message Center Monitor, Pipeline Governance Cleanup)
- Customers may run automation on Windows Server 2019 (PowerShell 5.1 only)
- Changing secret handling affects Environment Lifecycle Management (ELM) solution
- 13 solutions × multiple scripts = high blast radius for breaking changes

**Prevention:**

1. **Backward compatibility testing matrix:**
   ```powershell
   # Test matrix BEFORE merging changes:
   # - PowerShell 5.1 on Windows Server 2019
   # - PowerShell 7.2 on Windows 11
   # - PowerShell 7.4 on macOS (if cross-platform)

   # Test with and without optional modules installed
   # Document minimum supported version in README
   ```

2. **Gradual hardening with feature detection:**
   ```powershell
   # Instead of: #Requires -Modules SecretManagement (breaks existing)
   # Use:
   if (Get-Module -ListAvailable -Name SecretManagement) {
       $secret = Get-Secret -Name $secretName -AsPlainText
   } else {
       Write-Warning "SecretManagement module not found. Using ConvertTo-SecureString (legacy)."
       $secret = Read-Host -Prompt "Enter secret" -AsSecureString
   }
   ```

3. **Version-specific security improvements:**
   - Create separate branches: `v1-stable` (no breaking changes), `v2-hardened` (security improvements)
   - Document migration path in UPGRADE.md
   - Provide conversion scripts to upgrade deployments
   - Maintain v1 for 6 months minimum

4. **Change classification in release notes:**
   - **BREAKING:** Changes requiring user action before upgrade
   - **SECURITY:** Security improvements (may change behavior)
   - **COMPATIBLE:** Backward-compatible enhancements

   Example: "BREAKING: Register-ServicePrincipal.ps1 now requires SecretManagement module. See UPGRADE.md for migration steps."

5. **Don't over-engineer for theoretical risks:**
   - `ConvertTo-SecureString -AsPlainText` is **acceptable** for interactive scripts
   - Process memory exposure is low-risk for one-time setup scripts
   - Adding try/catch everywhere creates verbose code — focus on external API calls only
   - #Requires statements are useful but not mandatory — document prerequisites in README instead

**Detection:**
- Pre-release: Test scripts on PowerShell 5.1 (minimum supported version)
- Pre-release: Test on clean system without optional modules installed
- Pre-release: Run PSScriptAnalyzer with compatibility rules: `Invoke-ScriptAnalyzer -Path . -Settings PSGallery`
- Post-release: Monitor GitHub issues for "script no longer works" reports

**Which phase should address:**
- Phase 1: Compatibility Testing Setup (before any script changes)
- Phase 2: Security Improvements with Feature Detection (gradual hardening)
- Phase 3: Breaking Changes with Migration Guide (if truly necessary)

**Reference:** [Microsoft's Removal of PowerShell 2.0: Security Implications and Migration Guidance](https://redteamnews.com/blue-team/microsofts-removal-of-powershell-2-0-security-implications-and-migration-guidance/)

---

### Pitfall 3: YAML Configuration Externalization Creates More Complexity Than It Solves

**What goes wrong:** Moving hard-coded configuration to external YAML files increases maintenance burden, creates version skew between config and code, and makes simple scripts harder to understand.

**Why it happens:**
- Over-application of "12-factor app" principles to simple automation scripts
- Belief that "configuration should be external" applies to all config, not just environment-specific config
- YAML syntax errors are runtime failures (not caught until script executes)
- Multiple YAML files require synchronization (config drift between environments)
- Users must learn YAML structure on top of PowerShell/Python syntax

**Real-world evidence:**
- [Spring Boot Anti-Patterns: When to Use Design Patterns Without Overengineering](https://medium.com/@sunsetheus/spring-boot-anti-patterns-when-to-use-design-patterns-without-overengineering-361471d986f0): "Overengineering involves applying design patterns unnecessarily, leading to bloated and convoluted codebases"
- [Configuration Externalization — Design Pattern](https://medium.com/@vinciabhinav7/configuration-externalization-design-pattern-an-overview-25a05680ca73): "If you're managing a few microservices and only need one or two credentials, start with environment variables or YAML files, then consider adopting a Config Server or Vault as the platform scales"
- [YAML: probably not so great after all](https://www.arp242.net/yaml-config.html): Documents YAML complexity, ambiguity, and security issues

**Consequences:**
- Simple 50-line script now requires 100-line YAML config file
- Users must edit YAML correctly (indentation matters, no tabs allowed)
- Config schema not enforced — typos cause runtime failures
- Version control shows config changes but not why config structure changed
- Deployment requires distributing script + config + schema documentation

**FSI-AgentGov-specific impact:**
- Learn Monitor (`learn_monitor.py`) has 100+ lines of configuration (209 URLs)
- Regulatory Monitor has state file (`data/monitor-state.json`) — already JSON-based
- Moving Python config to YAML doesn't improve maintainability for this use case
- Scripts are run by administrators, not deployed as services — externalization less valuable

**When externalization DOES make sense:**
- Environment-specific values (tenant IDs, environment URLs) that differ per deployment
- Secrets (already handled by Key Vault or environment variables)
- Large lists of items that change frequently independent of code (e.g., URL monitoring list)

**When externalization is OVERENGINEERING:**
- Hard-coded constants that never change (`DEFAULT_TIMEOUT = 30`)
- Code structure choices (which API version to use)
- Small scripts with <10 configuration values
- Single-environment deployments (no dev/staging/prod split)

**Prevention:**

1. **Apply externalization selectively:**
   ```python
   # GOOD: Externalize environment-specific config
   tenant_id = os.environ.get("TENANT_ID")  # Different per deployment

   # GOOD: Externalize large lists
   monitored_urls = load_yaml("config/monitored-urls.yaml")  # Changes independently

   # BAD: Externalize constants
   # config.yaml: "max_retries: 3"  # This should be a constant in code
   MAX_RETRIES = 3  # Clear, typed, versioned with code
   ```

2. **Validate config at startup:**
   ```python
   # If using YAML, validate structure immediately
   from jsonschema import validate

   config = load_yaml("config.yaml")
   validate(config, schema)  # Fail fast with clear error
   ```

3. **Document the config-code contract:**
   - If config.yaml exists, README must document all fields
   - Config changes should trigger version bumps (breaking vs. non-breaking)
   - Provide example configs for common scenarios

4. **Consider JSON over YAML for machine-edited configs:**
   - JSON schema validation is more mature
   - No indentation ambiguity
   - Easier to programmatically update
   - Python/PowerShell native support without libraries

5. **Start simple, refactor later:**
   - Ship v1.0 with config in code
   - Add externalization in v2.0 if users request it (evidence of need)
   - Don't prematurely optimize for "might need to configure this later"

**Detection:**
- Pre-implementation: Count configuration values — if <10, keep in code
- Pre-implementation: Ask "will users customize this per deployment?" — if no, keep in code
- Code review: Challenge each externalized config item with "why not a constant?"
- Post-release: Monitor issues for "config file is confusing" feedback

**Which phase should address:**
- Phase 1: Configuration Audit (what actually needs externalization)
- Phase 2: Selective Externalization (only environment-specific values)
- Phase 3: Validation & Documentation (if proceeding with YAML)

**Reference:** [Platform Engineering's Patterns And Anti-patterns](https://octopus.com/devops/platform-engineering/patterns-anti-patterns/)

---

## Moderate Pitfalls

### Pitfall 4: "Completing" WIP Solutions Triggers Scope Creep

**What goes wrong:** Attempting to "finish" 6 WIP solutions leads to feature bloat as team adds "just one more" capability that seems necessary for "production readiness."

**Why it happens:**
- No clear definition of "done" for WIP solutions
- "While we're at it" syndrome — adding features because code is already open
- Perfectionism — belief that solution must handle all edge cases before marking Complete
- Feature requests accumulate during implementation ("can we also add X?")
- Sunk cost fallacy — "we've invested this much, might as well make it perfect"

**Real-world evidence:**
- Solutions Index shows: 3 Completed, 1 Validated, **6 WIP**, 3 Planned
- WIP solutions: Deny Event Correlation, Conditional Access Automation, Compliance Dashboard, Segregation Detector, Scope Drift Monitor, RAG Source Validator
- [Scope Creep is a Boss Fight: How to Beat Feature Bloat](https://www.wayline.io/blog/scope-creep-boss-fight-beat-feature-bloat): "Feature creep is the gradual addition of unnecessary features, often at the expense of time, budget, and user experience"
- [Feature Creep, the Bane of Our Existence](https://www.interaction-design.org/literature/article/feature-creep-the-bane-of-our-existence): "Feature creep leads to feature bloat, resulting in a product that is complex, difficult to navigate"

**Consequences:**
- V2 milestone scope expands from "complete 6 WIP solutions" to "complete + add 20 new features"
- Timeline slips as each solution grows from 2 weeks to 6 weeks
- Code quality suffers as features are rushed to meet extended deadline
- Solutions become harder to deploy (more dependencies, longer setup)
- "Perfect" solutions never ship because there's always one more feature to add

**FSI-AgentGov-specific impact:**
- Compliance Dashboard is "v1.0.0-beta" — temptation to add every possible chart before marking v1.0
- Conditional Access Automation has 8 policy templates — temptation to add 20 more "edge case" policies
- Each WIP solution maps to 2-4 framework controls — scope creep delays control automation
- Cross-solution dependencies create cascading delays (Scope Drift depends on Agent Inventory, etc.)

**Prevention:**

1. **Define "Complete" explicitly before starting:**
   ```markdown
   # Compliance Dashboard v1.0 Definition of Done

   MUST HAVE (blocking):
   - [ ] Dataverse tables deployed and schema documented
   - [ ] Sample data loads without errors
   - [ ] README installation steps tested on clean environment
   - [ ] All 62 controls appear in Power BI report template

   SHOULD HAVE (defer to v1.1):
   - Exception workflow automation (manual process documented for v1.0)
   - Trend analysis charts (aggregation exists, visualization deferred)

   WON'T HAVE (out of scope):
   - Real-time alerting (requires Premium capacity, not in scope)
   - Mobile app (web-only for v1.0)
   ```

2. **Use existing Completed solutions as quality bar:**
   - Environment Lifecycle Management (v1.1.2) is Completed
   - Message Center Monitor (v2.1.1) is Completed
   - Compare WIP solution scope to ELM — are you adding more features? Why?

3. **Implement feature freeze 2 weeks before milestone:**
   - No new features accepted after freeze date
   - Only bug fixes and documentation improvements
   - "Great idea, let's add it to v2.1 backlog" becomes default response

4. **Say no to "while we're at it" additions:**
   - Track feature requests in GitHub Issues with "v2.1" milestone
   - Require justification: "Why is this blocking v2.0 completion?"
   - Default to deferral unless customer-requested

5. **Ship iteratively:**
   - v1.0: Core functionality, manual steps documented
   - v1.1: Automation of previously manual steps
   - v2.0: Advanced features based on user feedback

   Example: Compliance Dashboard v1.0 ships with manual exception approval; v1.1 adds Power Automate approval flow.

**Detection:**
- Weekly scope review: "What features were added this week? Were they in original scope?"
- Compare current feature list to initial RESEARCH.md for solution
- Monitor Git commit messages for "add feature" vs. "fix bug" ratio
- Team retrospective: "Are we scope creeping or shipping?"

**Which phase should address:**
- Phase 1: Define "Complete" for Each WIP Solution (blocking)
- Phase 2-N: One Phase per Solution with Explicit Scope
- Final Phase: Integration Testing (no new features)

**Reference:** [4 Steps to Manage with Feature Creep](https://thisisstoked.com/knowledge/how-to-manage-feature-creep)

---

### Pitfall 5: Cross-Repo Changes Create Coordination Failures

**What goes wrong:** Updating documentation in FSI-AgentGov while simultaneously updating solution code in FSI-AgentGov-Solutions leads to version skew, broken links, and incomplete deployments.

**Why it happens:**
- Two repositories require two commits, two PRs, two review cycles
- Documentation changes merge before solution changes (or vice versa)
- Cross-references point to code that doesn't exist yet (or documentation that's missing)
- Reviewers only see one repo at a time, missing cross-repo dependencies
- No automated testing of cross-repo integration

**Real-world evidence:**
- [Cross-repository (or, project-level) PR with multiple branches](https://github.com/orgs/community/discussions/13733): "Coordinating changes that span multiple repositories may require additional effort"
- [Multi-Repo Workflows: Managing Distributed Systems](https://developertoolkit.ai/en/cursor-ide/advanced-techniques/multi-repo-workflows/): "Teams often forget to update components among multiple repositories when working on a topic"
- FSI-AgentGov CLAUDE.md documents: "Each repo has separate git history. Git commands must run from within the target repo."

**Consequences:**
- Documentation references solution features that don't exist yet (links to non-existent files)
- Solution deployed without documentation (users can't figure out how to use it)
- Version mismatch: docs say v1.1.0, solution is still v1.0.8
- Broken playbook links to FSI-AgentGov-Solutions README
- Review cycles double (need approval in both repos, reviews happen at different times)

**FSI-AgentGov-specific impact:**
- 13 solutions in FSI-AgentGov-Solutions
- Each solution documented in FSI-AgentGov playbooks (cross-references)
- Solutions Index (`docs/reference/solutions-index.md`) lists versions — must stay in sync
- Advanced implementation playbooks reference solution code structure

**Prevention:**

1. **Commit order protocol:**
   ```markdown
   # When changing both repos for a feature:
   1. Commit FSI-AgentGov-Solutions changes FIRST (code)
   2. Wait for merge and tag (e.g., v1.1.0)
   3. Commit FSI-AgentGov changes SECOND (documentation)
   4. Reference solution tag in documentation commit message

   Rationale: Documentation can reference tagged code release.
   Reverse order creates broken links to unreleased features.
   ```

2. **Cross-reference validation in CI:**
   ```python
   # In FSI-AgentGov CI pipeline:
   # Parse docs/reference/solutions-index.md for version numbers
   # Check that FSI-AgentGov-Solutions tags exist
   # Example: If docs say "v1.1.0", verify git tag exists

   def validate_solution_versions():
       for solution in parse_solutions_index():
           tag = f"{solution.name}-v{solution.version}"
           if not tag_exists(tag, solutions_repo):
               raise Error(f"Solutions Index references {tag} but tag doesn't exist")
   ```

3. **Atomic documentation updates:**
   - Don't split solution documentation across multiple PRs
   - One PR in FSI-AgentGov should document ALL changes from one solution release
   - PR description links to merged FSI-AgentGov-Solutions PR

4. **Version alignment table in CHANGELOG:**
   ```markdown
   # FSI-AgentGov v1.3.0 - March 2026

   ## Cross-Repo Version Alignment

   | FSI-AgentGov Version | Solutions Versions |
   |---------------------|-------------------|
   | v1.3.0 | - Environment Lifecycle Management v1.2.0 |
   |        | - Compliance Dashboard v1.0.0 (GA) |
   |        | - Conditional Access Automation v1.0.0 (GA) |

   Users deploying v1.3.0 framework should use above solution versions.
   ```

5. **Test deployment with both repos:**
   - Clone both repos at specific tags
   - Follow documentation from FSI-AgentGov
   - Deploy solution from FSI-AgentGov-Solutions
   - Verify all links work, versions match, deployment succeeds

**Detection:**
- Pre-merge: Check that referenced solution version exists in FSI-AgentGov-Solutions
- Pre-merge: Validate all playbook links to solution README files
- Post-merge: Monitor GitHub issues for "documentation doesn't match code" reports
- Post-merge: Run link checker across both repositories

**Which phase should address:**
- Phase 1: Cross-Repo Coordination Protocol (document commit order)
- Each Solution Phase: Commit to Solutions Repo, Then Docs Repo
- Final Phase: Cross-Repo Integration Testing

**Reference:** [Collaborating within the same repository](https://coderefinery.github.io/git-collaborative/same-repository/)

---

### Pitfall 6: JSON to SQLite Migration Adds Complexity Without Clear Benefit

**What goes wrong:** Migrating state files from JSON to SQLite database adds SQLite dependency, migration scripts, and schema management for minimal performance gain on small datasets.

**Why it happens:**
- Belief that "databases are always better than flat files"
- Premature optimization for scale that doesn't exist yet
- Desire to use SQL queries instead of simple Python dict operations
- Copying patterns from large-scale systems to small scripts

**Real-world evidence:**
- [SQLite JSON Storage Debate: Modern Solution or Unnecessary Complexity?](https://biggo.com/news/202412230727_sqlite-json-storage-debate): "Some developers question whether using SQLite for JSON storage adds unnecessary complexity to data storage, particularly when the application requirements are simple"
- [SQLite User Forum: Flat files vs SQLite](https://sqlite.org/forum/forumpost/3d7be1ad3d?t=c): Discusses when SQLite is overkill for simple data
- Current FSI-AgentGov: `data/learn-monitor-state.json` is 209 URLs × ~200 bytes = ~42KB file

**Consequences:**
- Must add SQLite library dependency (or use Python stdlib sqlite3)
- Schema evolution requires migration scripts (ALTER TABLE, version management)
- Debugging harder (can't just open JSON in editor, need SQL client)
- Cross-platform testing expands (SQLite file format varies)
- Backup/restore more complex (can't just copy .json file)
- State file corruption harder to fix (can't hand-edit like JSON)

**FSI-AgentGov-specific impact:**
- Learn Monitor state: 209 URLs, read/write once per day, file size <100KB
- Regulatory Monitor state: Even smaller dataset
- Performance not a bottleneck (current JSON parsing takes <1ms)
- Scripts run once per day in GitHub Actions (not high-concurrency scenario)

**When SQLite DOES make sense:**
- Concurrent read/write operations (JSON requires file locking)
- Large datasets (>10MB) where indexed queries matter
- Complex relational queries across multiple tables
- ACID transaction requirements

**When SQLite is OVERENGINEERING:**
- Single-user scripts with sequential access
- Small datasets (<1MB) with simple structure
- Infrequent updates (once per day or less)
- Current solution works fine (no performance complaints)

**Prevention:**

1. **Measure before migrating:**
   ```python
   # Current JSON approach:
   import json
   import time

   start = time.time()
   with open("data/learn-monitor-state.json") as f:
       state = json.load(f)  # Parse 209 URLs
   elapsed = time.time() - start
   print(f"JSON load time: {elapsed*1000:.2f}ms")

   # Is this slow? (Spoiler: No, it's <5ms)
   # Then why migrate to SQLite?
   ```

2. **Consider alternatives to SQLite:**
   - **Keep JSON** — if current performance is acceptable
   - **Switch to JSONL** (JSON Lines) — easier to append, still text-based
   - **Use TOML** — more human-readable than JSON for config files
   - **Use Parquet** — if query performance matters (unlikely for this use case)

3. **If migrating, automate the migration:**
   ```python
   # scripts/migrate_json_to_sqlite.py
   def migrate_state_file():
       """One-time migration with rollback."""
       # 1. Backup original JSON
       shutil.copy("data/state.json", "data/state.json.backup")

       # 2. Create SQLite schema
       # 3. Import JSON data
       # 4. Validate (compare record counts)
       # 5. If validation fails, restore backup and exit
   ```

4. **Document the rationale:**
   - If migrating, CHANGELOG must explain why (performance? features?)
   - If keeping JSON, document decision to avoid future "why not SQLite?" debates
   - Compare before/after metrics (load time, file size, LOC)

5. **Don't migrate just because it's "more professional":**
   - JSON is a professional format used by production systems
   - Simplicity is a feature, not a limitation
   - Text-based formats are debuggable and versionable

**Detection:**
- Pre-migration: Benchmark current JSON performance (is it actually slow?)
- Pre-migration: Survey team — has anyone complained about state file performance?
- Post-migration: Compare complexity (LOC, dependencies, test coverage) — did it increase?

**Which phase should address:**
- Phase 1: Performance Benchmarking (establish need)
- Phase 2: Migration Script Development (if proceeding)
- Phase 3: Validation & Rollback Testing

**Reference:** [JSON with Sqlite | Hacker News](https://news.ycombinator.com/item?id=19277809)

---

## Minor Pitfalls

### Pitfall 7: Breadcrumb/Navigation Changes Break User Muscle Memory

**What goes wrong:** Changing site breadcrumbs or left-nav structure breaks user workflows even if URLs stay the same — users can't find familiar pages.

**Why it happens:**
- Focus on "improving" information architecture without user testing
- Alphabetical sorting seems logical but disrupts learned navigation patterns
- Adding new categories splits content users expect to be together
- Renaming sections ("Playbooks" → "Implementation Guides") confuses existing users

**Consequences:**
- Support requests increase: "Where did X page go?"
- Users stop using documentation, rely on Google searches instead
- Onboarding harder for new users (no stable reference point)
- Analytics show users returning to homepage repeatedly (lost navigation)

**Prevention:**
- A/B test navigation changes in staging environment
- Survey existing users before major nav restructuring
- Keep top-level nav structure stable (Framework, Controls, Playbooks)
- Add new sections, don't rename existing ones

**Detection:**
- Monitor time-on-site metrics (increases suggest users are lost)
- Track homepage bounce rate (users giving up)
- Review GitHub Discussions for "can't find X anymore"

---

### Pitfall 8: Over-Testing WIP Solutions Delays Completion

**What goes wrong:** Attempting to achieve 100% test coverage on WIP solutions blocks them from reaching "Completed" status.

**Why it happens:**
- Belief that "production ready" requires comprehensive test suite
- Porting enterprise testing standards to small automation scripts
- Perfectionism — solution can't ship until all edge cases tested

**Consequences:**
- 6 WIP solutions remain WIP despite being functionally complete
- Testing phase takes longer than development phase
- Team burns out writing tests for theoretical edge cases
- Users can't deploy solutions that work but lack "official" Completed status

**Prevention:**
- Test critical paths only for v1.0 (happy path + common errors)
- Expand test coverage in v1.1+ based on real-world issues
- Mark solutions "Validated" (functionally tested) before "Completed" (full test suite)
- Remember: These are deployment scripts, not life-critical systems

**Detection:**
- Measure test LOC vs. implementation LOC ratio (>2:1 is often overkill)
- Track time spent on test development vs. feature development
- Ask: "Would this test catch a bug we've actually seen?"

---

### Pitfall 9: Documentation Version Skew (Docs Ahead of Code)

**What goes wrong:** Documentation describes features that exist in development branch but not in released version users deploy.

**Why it happens:**
- Docs updated on main branch while features in feature branch
- Merge order: docs merge first, code merges later (or never)
- No version tags in documentation indicating which release features apply to

**Consequences:**
- Users follow documentation, features don't exist, file bugs
- Support burden increases ("how do I use X?" / "X doesn't exist yet")
- Documentation loses credibility (can't trust it's accurate)

**Prevention:**
- Use version badges in documentation: "Added in v1.3.0", "Deprecated in v2.0.0"
- Merge feature documentation in same PR as feature code
- Release notes clearly indicate which features are GA vs. preview
- Test documentation against released versions, not development branches

**Detection:**
- Search docs for references to unreleased versions
- Check that all documented features exist in latest tagged release
- Review GitHub Issues for "documentation doesn't match release"

---

## Phase Assignments

| Pitfall | Severity | Recommended Phase |
|---------|----------|------------------|
| 1. MkDocs Awesome-Pages Breaking Links | CRITICAL | Phase 1 (URL Impact Assessment) |
| 2. PowerShell Security Hardening Breaking Scripts | CRITICAL | Phase 1 (Compatibility Testing Setup) |
| 3. YAML Configuration Overengineering | HIGH | Phase 1 (Configuration Audit) |
| 4. WIP Solution Scope Creep | HIGH | Phase 1 (Define "Complete" per Solution) |
| 5. Cross-Repo Coordination Failures | HIGH | Phase 1 (Commit Order Protocol) |
| 6. JSON to SQLite Unnecessary Migration | MEDIUM | Phase 1 (Performance Benchmarking) |
| 7. Navigation Changes Break User Workflows | MEDIUM | Phase 2 (Nav Stability Testing) |
| 8. Over-Testing Delays Completion | MEDIUM | Each Solution Phase (Test Pragmatically) |
| 9. Documentation Version Skew | MEDIUM | Final Integration Phase (Version Validation) |

---

## Integration Testing Requirements

Before v2 release, verify these cross-cutting concerns:

### URL Stability Test
```bash
# Compare production site to v2 build
mkdocs build --strict
diff -r site/ ../production-site-backup/
# Zero URL changes = safe to deploy
```

### Backward Compatibility Test
```powershell
# Test scripts on PowerShell 5.1 (minimum supported)
pwsh -Version 5.1 -File scripts/Deploy.ps1
# Must run without errors
```

### Cross-Repo Integration Test
```bash
# Clone both repos at release tags
git clone --branch v2.0.0 FSI-AgentGov
git clone --branch elm-v1.2.0 FSI-AgentGov-Solutions

# Follow documentation from FSI-AgentGov
# Deploy solution from FSI-AgentGov-Solutions
# All links work, versions match
```

### User Workflow Preservation Test
```markdown
# Test these existing user workflows MUST NOT break:
1. Navigate from Solutions Index to control playbook to solution README
2. Bookmark a control URL, access it after v2 deployment (same content)
3. Search for "DLP" in site, find Control 1.5 as first result (SEO preserved)
4. Run existing PowerShell script without modification (backward compatible)
```

---

## Recommended Decision Points

**Phase 1 (Architecture Decisions) should answer:**
- [ ] Are we migrating MkDocs navigation? (YES/NO with URL impact analysis)
- [ ] Are we hardening PowerShell scripts? (GRADUAL with compatibility matrix)
- [ ] Are we externalizing configuration? (SELECTIVE with justification per config item)
- [ ] What defines "Complete" for each WIP solution? (Explicit checklist)
- [ ] What is our cross-repo commit protocol? (Document and follow)

**Each Solution Completion Phase should answer:**
- [ ] Does this solution meet minimum viable "Complete" criteria? (ship it)
- [ ] Are we adding features beyond v1.0 scope? (defer to v1.1)
- [ ] Have we tested on clean environment with documented prerequisites? (works for users)
- [ ] Is cross-repo version alignment verified? (docs match code)

**Final Integration Phase should answer:**
- [ ] Do all URLs from v1.2.37 still work in v2.0? (backward compatible)
- [ ] Do existing bookmarks still resolve? (user workflows preserved)
- [ ] Does v2.0 documentation reference only released code? (no version skew)
- [ ] Can users upgrade from v1.2.37 to v2.0 without breaking changes? (migration path clear)

---

## Sources

- [Migration from v2 to v3 - Awesome Nav for MkDocs](https://lukasgeiter.github.io/mkdocs-awesome-nav/migration-v3/)
- [The Secret Migration: How Site Navigation Changes Can Destroy SEO](https://sitebulb.com/resources/guides/the-secret-migration-how-site-navigation-changes-can-destroy-seo-without-you-realising/)
- [PowerShell security features - Microsoft Learn](https://learn.microsoft.com/en-us/powershell/scripting/security/security-features?view=powershell-7.5)
- [Microsoft's Removal of PowerShell 2.0: Security Implications and Migration Guidance](https://redteamnews.com/blue-team/microsofts-removal-of-powershell-2-0-security-implications-and-migration-guidance/)
- [Spring Boot Anti-Patterns: When to Use Design Patterns Without Overengineering](https://medium.com/@sunsetheus/spring-boot-anti-patterns-when-to-use-design-patterns-without-overengineering-361471d986f0)
- [Configuration Externalization — Design Pattern: An Overview](https://medium.com/@vinciabhinav7/configuration-externalization-design-pattern-an-overview-25a05680ca73)
- [YAML: probably not so great after all](https://www.arp242.net/yaml-config.html)
- [Scope Creep is a Boss Fight: How to Beat Feature Bloat](https://www.wayline.io/blog/scope-creep-boss-fight-beat-feature-bloat)
- [4 Steps to Manage with Feature Creep](https://thisisstoked.com/knowledge/how-to-manage-feature-creep)
- [Multi-Repo Workflows: Managing Distributed Systems](https://developertoolkit.ai/en/cursor-ide/advanced-techniques/multi-repo-workflows/)
- [SQLite JSON Storage Debate: Modern Solution or Unnecessary Complexity?](https://biggo.com/news/202412230727_sqlite-json-storage-debate)
- [MkDocs Writing Your Docs](https://www.mkdocs.org/user-guide/writing-your-docs/)

---

*Researched: 2026-02-04*
*Confidence: HIGH (verified with 2026 sources, existing FSI-AgentGov audit data, and multi-repo architecture patterns)*
