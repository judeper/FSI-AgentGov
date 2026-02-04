# Phase 7: Solutions Functional Testing - Research

**Researched:** 2026-02-03
**Domain:** Documentation-based script validation and static analysis for Microsoft 365 automation
**Confidence:** HIGH

## Summary

Phase 7 requires validating that 13 solutions "work as documented" without access to a live Microsoft 365 environment. Traditional functional testing (runtime execution against live services) is impossible given this constraint. Research reveals a robust alternative: **documentation-based validation** using static analysis, syntactic verification, and documentation-code alignment testing.

The standard approach combines: (1) **PSScriptAnalyzer** for PowerShell static analysis with 50+ built-in rules, (2) **Pytest** or **Python AST parsing** for Python validation, (3) **API deprecation scanning** to detect deprecated Microsoft Graph endpoints, (4) **documentation-code traceability** verification to ensure README instructions match actual script parameters and behavior, and (5) **error handling pattern verification** to ensure scripts fail gracefully with clear error messages.

This approach validates script quality, correctness, and maintainability without requiring live API execution. It detects: syntax errors, deprecated API patterns (x-api-key, EWS, SharePoint Add-Ins), missing error handling, undocumented parameters, security anti-patterns, and documentation-code mismatches. Phase 6 already classified solutions by status (4 Completed, 4 Validated, 2 WIP, 3 Planned), providing clear testing priorities.

**Primary recommendation:** Use PSScriptAnalyzer + Python AST validation + documentation traceability checks to validate all 13 solutions can be deployed by users following the documentation, with test results documenting gaps requiring documentation updates or script corrections.

## Standard Stack

The established tools for documentation-based script validation:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PSScriptAnalyzer | 1.22+ | PowerShell static analysis | Official Microsoft SAST tool, 50+ built-in rules, PowerShell Gallery standard |
| Pytest | 8.x | Python testing framework | Industry standard, powerful fixtures, plugin ecosystem |
| Python AST | 3.11+ stdlib | Python syntax validation | Built-in, no dependencies, reliable parsing |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pester | 5.x | PowerShell mocking framework | Unit testing with external dependency mocking (optional) |
| PSRule | 2.x+ | Policy-as-code validation | Custom rule enforcement for FSI patterns (optional) |
| pylint / flake8 | Latest | Python linting | Additional code quality checks beyond AST (optional) |
| markdownlint | Latest | Markdown validation | README structure validation (optional) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Static analysis | Pester mocking with unit tests | More comprehensive but requires mock setup for all Graph APIs |
| Documentation traceability | Manual review | Automated checks scale better across 13 solutions |
| PSScriptAnalyzer | ScriptCop | PSScriptAnalyzer is actively maintained by Microsoft |

**Installation:**
```bash
# PowerShell tools
Install-Module PSScriptAnalyzer -Force -Scope CurrentUser
Install-Module Pester -Force -Scope CurrentUser -MinimumVersion 5.0

# Python tools
pip install pytest pylint flake8
```

## Architecture Patterns

### Recommended Test Structure

```
.planning/phases/07-solutions-functional-testing/
├── validation-scripts/
│   ├── validate-powershell.ps1        # PSScriptAnalyzer runner
│   ├── validate-python.py             # Python AST validation
│   ├── check-api-deprecations.py      # Deprecated endpoint scanner
│   └── verify-documentation.py        # README-code traceability
├── test-reports/
│   ├── psscriptanalyzer/              # Per-solution reports
│   ├── python-validation/             # Python analysis results
│   ├── api-deprecations/              # Deprecated API findings
│   └── documentation-alignment/       # Traceability gaps
├── test-data/
│   ├── deprecated-apis.json           # Known deprecated endpoints
│   └── expected-parameters.json       # Documentation-declared params
└── 07-VALIDATION-RESULTS.md           # Aggregated findings
```

### Pattern 1: PSScriptAnalyzer Validation

**What:** Static analysis of all PowerShell scripts using Microsoft's official SAST tool.

**When to use:** All `.ps1` files in all 13 solutions.

**Example:**
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/overview
$results = Invoke-ScriptAnalyzer -Path "./solution-name/scripts/" -Recurse -Severity Warning,Error

# Filter critical issues
$critical = $results | Where-Object {
    $_.Severity -eq 'Error' -or
    $_.RuleName -in @('PSAvoidUsingPlainTextForPassword', 'PSAvoidUsingConvertToSecureStringWithPlainText')
}

# Generate report
$critical | Export-Csv -Path "test-reports/psscriptanalyzer/solution-name.csv" -NoTypeInformation
```

### Pattern 2: Python AST Syntax Validation

**What:** Parse Python scripts to detect syntax errors and structural issues without execution.

**When to use:** All `.py` files in all 13 solutions.

**Example:**
```python
# Source: Built-in Python AST library
import ast
import sys

def validate_python_script(filepath):
    """Validate Python script syntax without execution."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read(), filename=filepath)
        return {"status": "pass", "file": filepath}
    except SyntaxError as e:
        return {
            "status": "fail",
            "file": filepath,
            "error": f"Line {e.lineno}: {e.msg}"
        }
```

### Pattern 3: API Deprecation Detection

**What:** Scan scripts for known deprecated Microsoft Graph/Power Platform API patterns.

**When to use:** All scripts making HTTP requests to Microsoft APIs.

**Example:**
```python
# Scan for deprecated patterns
deprecated_patterns = {
    "x-api-key": "Deprecated March 31, 2026 - use Entra ID auth",
    "outlook.office365.com/EWS": "EWS deprecated - use Graph API",
    "/_api/web/lists": "SharePoint REST deprecated - use Graph API",
    "management.azure.com/.../extensions/Microsoft.KeyVault": "Key Vault extension deprecated"
}

# Grep for patterns in all scripts
for pattern, reason in deprecated_patterns.items():
    matches = grep_files(pattern, solution_path)
    if matches:
        report_deprecation(pattern, reason, matches)
```

### Pattern 4: Documentation-Code Traceability

**What:** Verify README installation/configuration steps match actual script parameters and behavior.

**When to use:** All solutions with README.md and deployment scripts.

**Example:**
```python
# Extract parameters from script
def extract_script_parameters(ps1_file):
    """Parse PowerShell script for Param() block."""
    # Look for [Parameter(...)] attributes
    # Return list of parameter names and whether they're mandatory

# Extract documented parameters from README
def extract_readme_parameters(readme_file):
    """Parse README for documented script parameters in usage examples."""
    # Look for code blocks with script invocations
    # Extract parameter names from examples

# Compare
script_params = extract_script_parameters("scripts/Deploy.ps1")
readme_params = extract_readme_parameters("README.md")
undocumented = script_params - readme_params
missing = readme_params - script_params
```

### Pattern 5: Error Handling Verification

**What:** Ensure scripts have proper try/catch blocks and fail with actionable error messages.

**When to use:** All scripts in Completed/Validated/WIP solutions.

**Example:**
```powershell
# PSScriptAnalyzer custom rule
$errorHandlingRules = @(
    'PSAvoidUsingCmdletAliases',
    'PSUseShouldProcessForStateChangingFunctions',
    'PSAvoidGlobalVars',
    'PSUseDeclaredVarsMoreThanAssignments'
)

Invoke-ScriptAnalyzer -Path $scriptPath -IncludeRule $errorHandlingRules
```

### Anti-Patterns to Avoid

- **Manual script execution:** Don't run scripts against live tenant - defeats the purpose of documentation-based validation
- **Ignoring PSScriptAnalyzer warnings:** Warnings often indicate real issues that will trip up users
- **Testing only Completed solutions:** WIP and Planned solutions need validation to ensure code quality matches documentation promises
- **Skipping Python syntax validation:** Python scripts are deployment-critical (ELM, Hallucination Tracker)
- **Not documenting test gaps:** If a script can't be fully validated statically, document what manual verification is needed

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PowerShell static analysis | Custom regex patterns for common issues | PSScriptAnalyzer | 50+ built-in rules, actively maintained by Microsoft, integrates with CI/CD |
| Python syntax checking | Manual code review | Python AST or pytest | Built-in, reliable, catches all syntax errors |
| API deprecation tracking | Manual grep for endpoints | Structured JSON with known deprecated patterns + automated scanning | Scalable, version-controlled, can be updated as Microsoft announces new deprecations |
| Documentation testing | Manual README walkthrough | Automated parameter extraction and comparison | Catches all parameter mismatches, runs in seconds |
| Module dependency checking | Manual requirements.txt review | pip-audit for Python, PSDepend for PowerShell | Detects vulnerable dependencies automatically |

**Key insight:** Static analysis tools are mature and battle-tested. Building custom validators for PowerShell/Python would replicate years of community effort. Invest time in configuring existing tools, not recreating them.

## Common Pitfalls

### Pitfall 1: Assuming "No Syntax Errors" Means "Works as Documented"

**What goes wrong:** Script passes PSScriptAnalyzer but fails when user runs it because parameters are wrong or authentication pattern doesn't match documentation.

**Why it happens:** Static analysis validates code structure, not runtime behavior or documentation accuracy.

**How to avoid:** Always combine static analysis with documentation traceability checks. Verify:
- Script parameters match README usage examples
- Prerequisites in README match script requirements (modules, roles, resources)
- Error messages in script match troubleshooting guidance in README

**Warning signs:** README shows `-TenantId` parameter but script uses `-Tenant`, README says "Install Az.Accounts" but script requires "Install-Module AzureAD".

### Pitfall 2: Ignoring "Planned" Solutions as "Not Ready for Testing"

**What goes wrong:** Planned solutions (COI Testing, Hallucination Tracker, DR Testing) have minimal implementation but are documented as features. Users may try to deploy them and find gaps.

**Why it happens:** Documentation was written before implementation was complete.

**How to avoid:** Test ALL 13 solutions regardless of status. For Planned solutions:
- Verify documented scripts actually exist
- Validate any existing scripts pass static analysis
- Document gaps between documentation promises and actual implementation
- Update README with status badges if implementation is incomplete

**Warning signs:** README describes full deployment workflow but scripts/ directory is empty or has placeholder files.

### Pitfall 3: Missing Service Principal / Entra ID Auth Pattern Validation

**What goes wrong:** Scripts use deprecated auth patterns (x-api-key, username/password) or don't follow modern Entra ID authentication best practices.

**Why it happens:** Scripts were written before authentication migration or copied from old examples.

**How to avoid:** Create custom PSScriptAnalyzer rules or grep patterns to detect:
- `x-api-key` usage (deprecated March 31, 2026 per TECH-08)
- `Get-Credential` without Entra ID context
- Hardcoded credentials or secrets in code
- Missing `-TenantId` parameters for multi-tenant environments

**Warning signs:** Script works in single-tenant lab but fails in production with multiple tenants, authentication errors without clear guidance.

### Pitfall 4: Not Validating Cross-Solution Dependencies

**What goes wrong:** Solution A references Solution B's output (e.g., Compliance Dashboard depends on Deny Event Correlation data) but dependency isn't validated.

**Why it happens:** Each solution tested in isolation without checking integration points.

**How to avoid:** Map solution dependencies from Phase 6 findings:
- Compliance Dashboard → Deny Event Correlation (data dependency)
- FINRA Supervision → Communication Compliance (monitoring dependency)
- DR Testing → Environment Lifecycle Management (provisioning dependency)

Test that:
- Referenced Dataverse tables/columns exist in prerequisites
- Power Automate flows reference correct endpoints
- Documentation explains dependency installation order

**Warning signs:** Solution B README says "requires Solution A deployed" but doesn't specify which version or what artifacts are needed.

### Pitfall 5: Assuming Python Requirements.txt is Complete

**What goes wrong:** Script imports modules not listed in requirements.txt, causing deployment failures.

**Why it happens:** Developer had modules installed globally and didn't test fresh environment installation.

**How to avoid:** For each Python solution:
- Parse all `.py` files for `import` and `from X import` statements
- Compare imported modules against requirements.txt
- Flag any imports not in requirements.txt (except stdlib)

**Warning signs:** Script has `import requests` but requests not in requirements.txt, script has `from elm_client import ELMClient` but elm_client.py doesn't exist.

### Pitfall 6: Documentation References Non-Existent Files

**What goes wrong:** README references `docs/service-principal-setup.md` but file doesn't exist in solution directory.

**Why it happens:** Documentation written before supporting files created, or files moved/renamed without updating links.

**How to avoid:** Automated link validation:
- Extract all `[text](path)` and `See [file.md]` references from README
- Verify all referenced files exist
- Validate all `docs/` folder references resolve
- Check for broken relative paths

**Warning signs:** README has 8 referenced files but only 4 exist in solution directory.

## Code Examples

Verified patterns from research sources:

### PSScriptAnalyzer Basic Validation

```powershell
# Source: https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/overview
# Analyze all scripts in a solution directory
$analysisResults = Invoke-ScriptAnalyzer `
    -Path "/Users/admin/dev/FSI-AgentGov-Solutions/deny-event-correlation-report/scripts/" `
    -Recurse `
    -Severity Error,Warning `
    -Settings PSGallery

# Group by severity
$errors = $analysisResults | Where-Object Severity -eq 'Error'
$warnings = $analysisResults | Where-Object Severity -eq 'Warning'

Write-Host "Errors: $($errors.Count), Warnings: $($warnings.Count)"

# Export for documentation
$analysisResults | Select-Object ScriptPath, Line, Severity, RuleName, Message |
    Export-Csv -Path "test-reports/deny-event-correlation.csv" -NoTypeInformation
```

### Python AST Validation Script

```python
# Source: Python 3.11 stdlib documentation
import ast
import json
from pathlib import Path

def validate_python_solution(solution_path):
    """Validate all Python files in solution directory."""
    results = []

    for py_file in Path(solution_path).glob("**/*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                ast.parse(f.read(), filename=str(py_file))
            results.append({
                "file": str(py_file.relative_to(solution_path)),
                "status": "PASS",
                "errors": []
            })
        except SyntaxError as e:
            results.append({
                "file": str(py_file.relative_to(solution_path)),
                "status": "FAIL",
                "errors": [{
                    "line": e.lineno,
                    "message": e.msg,
                    "text": e.text
                }]
            })

    return results

# Run validation
solution_path = Path("/Users/admin/dev/FSI-AgentGov-Solutions/environment-lifecycle-management")
results = validate_python_solution(solution_path)

# Save results
with open("test-reports/python-validation/elm.json", "w") as f:
    json.dump(results, f, indent=2)
```

### API Deprecation Scanner

```python
# Source: Research finding on deprecated API detection
import re
from pathlib import Path

DEPRECATED_PATTERNS = {
    r"x-api-key": {
        "replacement": "Entra ID authentication via Connect-AzAccount or MSAL",
        "deadline": "2026-03-31",
        "severity": "CRITICAL"
    },
    r"outlook\.office365\.com/EWS": {
        "replacement": "Microsoft Graph API",
        "deadline": "N/A - already deprecated",
        "severity": "HIGH"
    },
    r"/_api/web/": {
        "replacement": "Microsoft Graph API for SharePoint",
        "deadline": "N/A - REST API deprecated",
        "severity": "MEDIUM"
    }
}

def scan_for_deprecated_apis(solution_path):
    """Scan all scripts for deprecated API patterns."""
    findings = []

    for script in Path(solution_path).glob("**/*.ps1"):
        with open(script, 'r', encoding='utf-8') as f:
            content = f.read()

        for pattern, details in DEPRECATED_PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                findings.append({
                    "file": str(script.relative_to(solution_path)),
                    "line": line_num,
                    "pattern": pattern,
                    "severity": details["severity"],
                    "replacement": details["replacement"],
                    "deadline": details["deadline"]
                })

    return findings
```

### Documentation-Code Traceability Check

```python
# Source: Research finding on documentation testing best practices
import re
from pathlib import Path

def extract_script_parameters(ps1_file):
    """Extract PowerShell parameter names from script."""
    with open(ps1_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find Param() block
    param_match = re.search(r'Param\s*\((.*?)\)', content, re.DOTALL | re.IGNORECASE)
    if not param_match:
        return set()

    # Extract parameter names: [Parameter(...)]\n$ParamName
    params = re.findall(r'\$(\w+)', param_match.group(1))
    return set(params)

def extract_readme_examples(readme_file):
    """Extract PowerShell parameter usage from README examples."""
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find PowerShell code blocks
    code_blocks = re.findall(r'```(?:powershell|ps1)\n(.*?)\n```', content, re.DOTALL)

    # Extract -ParameterName patterns
    params = set()
    for block in code_blocks:
        params.update(re.findall(r'-(\w+)', block))

    return params

def verify_documentation_alignment(solution_path):
    """Check if README examples match actual script parameters."""
    readme = solution_path / "README.md"
    scripts = list((solution_path / "scripts").glob("*.ps1"))

    results = []
    for script in scripts:
        script_params = extract_script_parameters(script)
        readme_params = extract_readme_examples(readme)

        undocumented = script_params - readme_params
        nonexistent = readme_params - script_params

        results.append({
            "script": script.name,
            "undocumented_params": list(undocumented),
            "nonexistent_params": list(nonexistent),
            "aligned": len(undocumented) == 0 and len(nonexistent) == 0
        })

    return results
```

### Requirements.txt Completeness Check

```python
# Source: Research finding on Python dependency validation
import ast
from pathlib import Path

def extract_imports_from_file(py_file):
    """Extract all import statements from Python file."""
    with open(py_file, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Get top-level module name
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    return imports

def verify_requirements_complete(solution_path):
    """Check if requirements.txt includes all imported modules."""
    # Get all imports from all .py files
    all_imports = set()
    for py_file in Path(solution_path).glob("**/*.py"):
        all_imports.update(extract_imports_from_file(py_file))

    # Get requirements.txt entries
    req_file = solution_path / "requirements.txt"
    if not req_file.exists():
        return {"status": "MISSING_REQUIREMENTS_FILE", "imports": list(all_imports)}

    with open(req_file, 'r') as f:
        requirements = set()
        for line in f:
            # Extract package name (before ==, >=, etc.)
            match = re.match(r'^([a-zA-Z0-9_-]+)', line.strip())
            if match:
                requirements.add(match.group(1))

    # Filter out stdlib modules (approximation)
    stdlib_modules = {'os', 'sys', 'json', 'pathlib', 'argparse', 're', 'datetime', 'typing'}
    third_party = all_imports - stdlib_modules

    missing = third_party - requirements

    return {
        "status": "PASS" if not missing else "FAIL",
        "missing_requirements": list(missing),
        "documented_requirements": list(requirements)
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual code review | PSScriptAnalyzer static analysis | 2024+ | Automated detection of 50+ issue types, CI/CD integration |
| Runtime testing only | Static analysis + documentation traceability | 2025-2026 | Validate without live environment access |
| Single-pass testing | Layered validation (syntax → rules → deprecations → docs) | 2026 | Comprehensive coverage without execution risk |
| Global policy enforcement | Policy-as-code with PSRule/OPA | 2025+ | Version-controlled security policies |
| Manual deprecation tracking | Automated scanning with structured deprecation database | 2026 | Proactive detection before user deployment |

**Deprecated/outdated:**
- **x-api-key authentication:** Deprecated March 31, 2026 - all scripts must use Entra ID auth
- **ScriptCop for PowerShell analysis:** Replaced by PSScriptAnalyzer (more active maintenance)
- **Manual README walkthroughs:** Replaced by automated documentation-code traceability checks

## Open Questions

Things that couldn't be fully resolved:

1. **Microsoft Graph API endpoint deprecation completeness**
   - What we know: x-api-key, EWS, SharePoint REST are deprecated; documented in TECH-08
   - What's unclear: Full list of deprecated Graph endpoints in solutions (may require Microsoft API changelog review)
   - Recommendation: Start with known deprecations from TECH-08, expand list during validation if new patterns found

2. **Python mocking for Dataverse API calls**
   - What we know: Pester supports PowerShell mocking, Pytest supports Python mocking
   - What's unclear: Whether mocking Graph/Dataverse calls adds sufficient value vs. static analysis alone
   - Recommendation: Start with static analysis, add mocking only if critical logic paths can't be validated otherwise

3. **Solution cross-dependencies testing depth**
   - What we know: Phase 6 identified dependencies (e.g., Compliance Dashboard → Deny Event Correlation)
   - What's unclear: Whether to validate dependency versions, API contracts, or just document existence
   - Recommendation: Validate that documented dependencies exist and are referenced correctly in code; defer API contract testing to Phase 8 monitoring

4. **"Planned" solution validation scope**
   - What we know: 3 solutions (COI Testing, Hallucination Tracker, DR Testing) are status "Planned" with minimal implementation
   - What's unclear: Whether to validate placeholder code or just document implementation gaps
   - Recommendation: Run full validation suite on all files that exist; document gaps where README promises features not yet implemented

5. **Regression testing for Phase 6 fixes**
   - What we know: Phase 6 fixed DEC x-api-key deprecation and FINRA citation
   - What's unclear: Whether functional testing should explicitly verify Phase 6 fixes or just validate current state
   - Recommendation: Validate current state only; Phase 6 fixes are already committed and verified

## Sources

### Primary (HIGH confidence)

- [PSScriptAnalyzer module - PowerShell | Microsoft Learn](https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/overview?view=ps-modules) - Official Microsoft documentation for PowerShell SAST tool
- [Pester - The ubiquitous test and mock framework for PowerShell | Pester](https://pester.dev/) - Official Pester framework documentation
- [GitHub - PowerShell/PSScriptAnalyzer](https://github.com/PowerShell/PSScriptAnalyzer) - Official PSScriptAnalyzer repository
- Python 3.11 AST documentation - Built-in Python standard library documentation

### Secondary (MEDIUM confidence)

- [Testing Infrastructure as Code - A Complete Guide | TechTarget](https://www.techtarget.com/searchitoperations/tip/Infrastructure-as-code-testing-strategies-to-validate-a-deployment) - IaC testing best practices verified with TechTarget
- [Infrastructure as Code Testing in CI/CD: A Complete Guide](https://www.accelq.com/blog/infrastructure-as-code-testing/) - CI/CD integration patterns
- [Test Automation Documentation with Best Practices in 2026](https://research.aimultiple.com/test-automation-documentation/) - Documentation testing approaches
- [Top Python Testing Frameworks in 2026 | TestGrid](https://testgrid.io/blog/python-testing-framework/) - Python testing tool comparison
- [Mocking with Pester | Pester](https://pester.dev/docs/usage/mocking) - Pester mocking documentation

### Tertiary (LOW confidence)

- [Microsoft Graph Developer Proxy for mocking Graph API responses](https://athsharepoint.com/2023/05/05/mock-responses-with-the-microsoft-graph-developer-proxy/) - Community blog post (unverified for 2026 currency)
- [APIScanner - Towards Automated Detection of Deprecated APIs](https://ar5iv.labs.arxiv.org/html/2102.09251) - Academic research paper (Python-focused)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - PSScriptAnalyzer and Pytest are industry-standard tools verified via official Microsoft Learn and official project documentation
- Architecture: HIGH - Layered validation pattern (syntax → static analysis → deprecation → documentation) aligns with IaC testing best practices from multiple authoritative sources
- Pitfalls: MEDIUM - Derived from Microsoft Learn troubleshooting docs + research findings on common automation errors; some pitfalls are project-specific predictions

**Research date:** 2026-02-03
**Valid until:** 2026-04-03 (60 days - static analysis tools stable, API deprecations accelerating)

**Key constraint:** No live Microsoft 365 environment available. All validation must be documentation-based (static analysis, syntactic correctness, documentation-code alignment). This constraint shifts "functional testing" definition from "runtime execution" to "deployability validation."

**Phase 6 context:** 13 solutions already audited with status classifications:
- **Completed (4):** ELM, MCM, PGC, DEC - comprehensive documentation + mature implementation
- **Validated (4):** FINRA, CAA, Segregation Detector, Scope Drift - core functionality validated
- **Work In Progress (2):** Compliance Dashboard, RAG Source Validator - active development
- **Planned (3):** COI Testing, Hallucination Tracker, DR Testing - designed but minimal implementation

Testing priority: Completed → Validated → WIP → Planned (validate what exists, document what's missing).
