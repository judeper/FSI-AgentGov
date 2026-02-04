#!/usr/bin/env python3
"""
Python Solution Validator
Validates syntax, imports, dependencies, API patterns, and error handling for FSI-AgentGov-Solutions.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

# Python 3.9 stdlib modules (partial list - common ones)
STDLIB_MODULES = {
    'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'configparser',
    'copy', 'csv', 'datetime', 'decimal', 'enum', 'functools', 'getpass', 'hashlib', 'http',
    'io', 'itertools', 'json', 'logging', 'math', 'os', 're', 'shutil', 'socket',
    'sqlite3', 'ssl', 'string', 'subprocess', 'sys', 'tempfile', 'threading',
    'time', 'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'xml', 'zipfile',
    'pathlib', 'dataclasses', 'secrets', 'queue', 'pickle', 'platform', 'random',
    'traceback', 'textwrap', 'operator', 'contextlib', 'abc', 'weakref', 'types'
}

class PythonValidator:
    def __init__(self, solutions_root: str):
        self.solutions_root = Path(solutions_root)
        self.results = {}

    def parse_requirements_txt(self, req_path: Path) -> Set[str]:
        """Parse requirements.txt and extract package names."""
        packages = set()
        if not req_path.exists():
            return packages

        with open(req_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Extract package name (handle ==, >=, etc.)
                pkg = re.split(r'[=<>!]', line)[0].strip()
                packages.add(pkg.lower().replace('_', '-'))
        return packages

    def extract_imports(self, tree: ast.AST, script_dir: Path) -> Tuple[Set[str], Set[str], Set[str]]:
        """Extract stdlib, third-party, and local imports from AST.

        Returns full import paths for namespace packages (e.g., 'azure.identity' not just 'azure').
        """
        stdlib_imports = set()
        third_party_imports = set()
        local_imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_base = alias.name.split('.')[0]
                    if module_base in STDLIB_MODULES:
                        stdlib_imports.add(module_base)
                    elif (script_dir / f"{module_base}.py").exists():
                        local_imports.add(module_base)
                    else:
                        # Store full path for namespace packages (azure.identity, not azure)
                        third_party_imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_base = node.module.split('.')[0]
                    if module_base in STDLIB_MODULES:
                        stdlib_imports.add(module_base)
                    elif (script_dir / f"{module_base}.py").exists():
                        local_imports.add(module_base)
                    else:
                        # Store full module path for namespace packages
                        third_party_imports.add(node.module)

        return stdlib_imports, third_party_imports, local_imports

    def check_error_handling(self, tree: ast.AST) -> int:
        """Count try/except blocks in AST."""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                count += 1
        return count

    def check_entry_point(self, content: str) -> bool:
        """Check if script has if __name__ == '__main__': pattern."""
        return 'if __name__' in content and '__main__' in content

    def scan_deprecated_patterns(self, content: str, filepath: str) -> List[str]:
        """Scan for deprecated API patterns."""
        patterns = []

        # Check for hardcoded credentials
        if re.search(r'password\s*=\s*["\']', content, re.IGNORECASE):
            patterns.append("Hardcoded password detected")
        if re.search(r'secret\s*=\s*["\']', content, re.IGNORECASE):
            patterns.append("Hardcoded secret detected")

        # Check for deprecated APIs
        if 'x-api-key' in content.lower():
            patterns.append("Deprecated x-api-key header usage")
        if 'outlook.office365.com/EWS' in content:
            patterns.append("Deprecated EWS endpoint")
        if '/_api/web/' in content:
            patterns.append("Legacy SharePoint REST API (_api/web/)")

        return patterns

    def validate_script(self, script_path: Path, requirements: Set[str],
                       solution_dir: Path) -> Dict:
        """Validate a single Python script."""
        result = {
            'path': str(script_path.relative_to(self.solutions_root)),
            'syntax': 'UNKNOWN',
            'syntax_error': None,
            'imports': {'stdlib': [], 'third_party': [], 'local': []},
            'missing_deps': [],
            'error_handling': 0,
            'has_entry_point': False,
            'deprecated_patterns': [],
            'local_import_issues': []
        }

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content, filename=str(script_path))
                result['syntax'] = 'PASS'

                # Extract imports
                script_dir = script_path.parent
                stdlib, third_party, local = self.extract_imports(tree, script_dir)
                result['imports']['stdlib'] = sorted(stdlib)
                result['imports']['third_party'] = sorted(third_party)
                result['imports']['local'] = sorted(local)

                # Normalize package names for comparison (handle namespace packages)
                normalized_third_party = set()
                for pkg in third_party:
                    # For namespace packages like azure.identity, extract base package
                    base_pkg = pkg.split('.')[0].lower().replace('_', '-')
                    # Also try the full dotted name converted to dash
                    full_pkg = pkg.lower().replace('.', '-').replace('_', '-')
                    normalized_third_party.add(base_pkg)
                    normalized_third_party.add(full_pkg)

                normalized_requirements = {pkg.lower().replace('_', '-') for pkg in requirements}

                # Check for missing dependencies
                missing = []
                for pkg in third_party:
                    base_pkg = pkg.split('.')[0].lower().replace('_', '-')
                    full_pkg = pkg.lower().replace('.', '-').replace('_', '-')

                    # Check if either base or full package is in requirements
                    if base_pkg not in normalized_requirements and full_pkg not in normalized_requirements:
                        missing.append(pkg)

                result['missing_deps'] = missing

                # Check error handling
                result['error_handling'] = self.check_error_handling(tree)

                # Check entry point
                result['has_entry_point'] = self.check_entry_point(content)

                # Scan for deprecated patterns
                result['deprecated_patterns'] = self.scan_deprecated_patterns(content, str(script_path))

            except SyntaxError as e:
                result['syntax'] = 'FAIL'
                result['syntax_error'] = f"Line {e.lineno}: {e.msg}"

        except Exception as e:
            result['syntax'] = 'ERROR'
            result['syntax_error'] = str(e)

        return result

    def validate_solution(self, solution_name: str, scripts: List[str]) -> Dict:
        """Validate all scripts in a solution."""
        solution_dir = self.solutions_root / solution_name
        scripts_dir = solution_dir / 'scripts'
        # Check both locations for requirements.txt
        req_path = scripts_dir / 'requirements.txt'
        if not req_path.exists():
            req_path = solution_dir / 'requirements.txt'

        # Parse requirements
        requirements = self.parse_requirements_txt(req_path)

        solution_result = {
            'name': solution_name,
            'has_requirements': req_path.exists(),
            'requirements': sorted(requirements),
            'scripts': [],
            'summary': {
                'total': len(scripts),
                'syntax_pass': 0,
                'syntax_fail': 0,
                'missing_deps': 0,
                'deprecated_apis': 0,
                'no_error_handling': 0
            }
        }

        # Validate each script
        for script in scripts:
            script_path = scripts_dir / script
            if not script_path.exists():
                continue

            result = self.validate_script(script_path, requirements, solution_dir)
            solution_result['scripts'].append(result)

            # Update summary
            if result['syntax'] == 'PASS':
                solution_result['summary']['syntax_pass'] += 1
            elif result['syntax'] == 'FAIL':
                solution_result['summary']['syntax_fail'] += 1

            if result['missing_deps']:
                solution_result['summary']['missing_deps'] += 1
            if result['deprecated_patterns']:
                solution_result['summary']['deprecated_apis'] += 1
            if result['error_handling'] == 0 and result['has_entry_point']:
                solution_result['summary']['no_error_handling'] += 1

        # Check for unused dependencies
        all_third_party = set()
        for script in solution_result['scripts']:
            all_third_party.update(script['imports']['third_party'])

        normalized_third_party = {pkg.lower().replace('_', '-') for pkg in all_third_party}
        normalized_requirements = {pkg.lower().replace('_', '-') for pkg in requirements}

        unused = normalized_requirements - normalized_third_party
        solution_result['unused_deps'] = sorted(unused)

        return solution_result

    def run_validation(self):
        """Run validation for all solutions."""
        solutions = {
            'environment-lifecycle-management': [
                'create_field_security.py', 'create_business_rules.py', 'deploy.py',
                'export_quarterly_evidence.py', 'register_service_principal.py',
                'validate_immutability.py', 'create_dataverse_schema.py',
                'create_views.py', 'elm_client.py', 'verify_role_privileges.py',
                'create_security_roles.py'
            ],
            'finra-supervision-workflow': [
                'deploy.py', 'export_supervision_evidence.py'
            ],
            'compliance-dashboard': [
                'load_sample_data.py'
            ],
            'coi-testing': [
                'run_coi_tests.py'
            ],
            'hallucination-tracker': [
                'analyze_patterns.py'
            ]
        }

        for solution_name, scripts in solutions.items():
            result = self.validate_solution(solution_name, scripts)
            self.results[solution_name] = result

    def generate_report(self) -> str:
        """Generate markdown report."""
        lines = []
        lines.append("# Python Solution Validation Results")
        lines.append("")
        lines.append("**Validation Date:** 2026-02-04")
        lines.append("**Solutions Validated:** 5")
        lines.append("**Scripts Validated:** 16")
        lines.append("")

        # Summary table
        lines.append("## Summary")
        lines.append("")
        lines.append("| Solution | Scripts | Syntax | Dependencies | Deprecations | Error Handling |")
        lines.append("|----------|---------|--------|--------------|--------------|----------------|")

        for solution_name, result in self.results.items():
            summary = result['summary']
            syntax_status = "✓ PASS" if summary['syntax_fail'] == 0 else f"✗ {summary['syntax_fail']} FAIL"
            deps_status = "✓" if summary['missing_deps'] == 0 else f"⚠ {summary['missing_deps']}"
            deprecated_status = "✓" if summary['deprecated_apis'] == 0 else f"⚠ {summary['deprecated_apis']}"
            error_status = "✓" if summary['no_error_handling'] == 0 else f"⚠ {summary['no_error_handling']}"

            lines.append(f"| {solution_name} | {summary['total']} | {syntax_status} | {deps_status} | {deprecated_status} | {error_status} |")

        lines.append("")

        # Per-solution details
        lines.append("## Per-Solution Details")
        lines.append("")

        for solution_name, result in self.results.items():
            lines.append(f"### {solution_name}")
            lines.append("")
            lines.append(f"**Requirements.txt:** {'✓ Present' if result['has_requirements'] else '✗ MISSING'}")
            lines.append(f"**Scripts:** {result['summary']['total']}")
            lines.append("")

            if not result['has_requirements']:
                lines.append("**⚠ CRITICAL:** Missing requirements.txt file")
                lines.append("")

            # Unused dependencies
            if result['unused_deps']:
                lines.append(f"**Unused Dependencies ({len(result['unused_deps'])}):**")
                for dep in result['unused_deps']:
                    lines.append(f"- {dep}")
                lines.append("")

            # Script details
            for script in result['scripts']:
                lines.append(f"#### {script['path']}")
                lines.append("")

                # Syntax
                if script['syntax'] == 'PASS':
                    lines.append("**Syntax:** ✓ PASS")
                else:
                    lines.append(f"**Syntax:** ✗ FAIL - {script['syntax_error']}")
                lines.append("")

                # Imports
                if script['imports']['third_party']:
                    lines.append(f"**Third-party imports ({len(script['imports']['third_party'])}):** {', '.join(script['imports']['third_party'])}")
                    lines.append("")

                if script['imports']['local']:
                    lines.append(f"**Local imports:** {', '.join(script['imports']['local'])}")
                    lines.append("")

                # Missing dependencies
                if script['missing_deps']:
                    lines.append("**⚠ CRITICAL - Missing Dependencies:**")
                    for dep in script['missing_deps']:
                        lines.append(f"- {dep}")
                    lines.append("")

                # Local import issues
                if script['local_import_issues']:
                    lines.append("**⚠ HIGH - Local Import Issues:**")
                    for issue in script['local_import_issues']:
                        lines.append(f"- {issue}")
                    lines.append("")

                # Deprecated patterns
                if script['deprecated_patterns']:
                    lines.append("**⚠ HIGH - Deprecated Patterns:**")
                    for pattern in script['deprecated_patterns']:
                        lines.append(f"- {pattern}")
                    lines.append("")

                # Error handling
                if script['error_handling'] == 0 and script['has_entry_point']:
                    lines.append("**⚠ HIGH:** No error handling (0 try/except blocks)")
                    lines.append("")
                elif script['error_handling'] > 0:
                    lines.append(f"**Error Handling:** ✓ {script['error_handling']} try/except blocks")
                    lines.append("")

                # Entry point
                if script['has_entry_point']:
                    lines.append("**Entry Point:** ✓ Has `if __name__ == '__main__'`")
                else:
                    lines.append("**Entry Point:** Library module (no main entry point)")
                lines.append("")

                lines.append("---")
                lines.append("")

        # Overall findings
        lines.append("## Overall Findings")
        lines.append("")

        total_scripts = sum(r['summary']['total'] for r in self.results.values())
        total_syntax_fail = sum(r['summary']['syntax_fail'] for r in self.results.values())
        total_missing_deps = sum(r['summary']['missing_deps'] for r in self.results.values())
        total_deprecated = sum(r['summary']['deprecated_apis'] for r in self.results.values())
        total_no_error_handling = sum(r['summary']['no_error_handling'] for r in self.results.values())

        lines.append(f"- **Total Scripts:** {total_scripts}")
        lines.append(f"- **Syntax Failures:** {total_syntax_fail}")
        lines.append(f"- **Scripts with Missing Dependencies:** {total_missing_deps}")
        lines.append(f"- **Scripts with Deprecated Patterns:** {total_deprecated}")
        lines.append(f"- **Scripts with No Error Handling:** {total_no_error_handling}")
        lines.append("")

        # Severity categorization
        lines.append("## Severity Classification")
        lines.append("")
        lines.append("### CRITICAL")
        lines.append("- Syntax errors preventing script execution")
        lines.append("- Missing dependencies (third-party imports not in requirements.txt)")
        lines.append("- Missing requirements.txt file")
        lines.append("")
        lines.append("### HIGH")
        lines.append("- Deprecated API patterns")
        lines.append("- No error handling in executable scripts")
        lines.append("- Local import issues (referenced module not found)")
        lines.append("")
        lines.append("### MEDIUM")
        lines.append("- Unused dependencies in requirements.txt")
        lines.append("")
        lines.append("### LOW")
        lines.append("- Style and best practice recommendations")
        lines.append("")

        return '\n'.join(lines)

if __name__ == '__main__':
    solutions_root = '/Users/admin/dev/FSI-AgentGov-Solutions'

    validator = PythonValidator(solutions_root)
    validator.run_validation()

    report = validator.generate_report()
    print(report)
