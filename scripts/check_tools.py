#!/usr/bin/env python3
"""Tool policy enforcement checker.

This script performs AST-based static analysis on Tool implementations
to enforce critical rules that ensure system safety and debuggability.

Enforcement Layers:
- Layer 1 (Enforced): Violations fail CI immediately
- Layer 2 (Recommended): Violations emit warnings only

Usage:
    python scripts/check_tools.py
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path


# Allowlist paths that are excluded from enforcement
ALLOWLIST_PATHS = [
    "packages/core/tools/examples",
    "packages/core/tools/__init__.py",
]

# Forbidden imports (runtime-level)
FORBIDDEN_IMPORTS = {
    "fastapi",
    "apps.api",
    "requests",  # unless infra-backed tool - not in this PR
    "random",
}

# Forbidden function calls (module.function)
FORBIDDEN_CALLS = {
    "random.randint",
    "random.random",
    "random.choice",
    "random.shuffle",
    "datetime.datetime.now",
    "datetime.now",
    "os.getenv",
    "os.environ.get",
}

# Forbidden module prefixes for isolation
FORBIDDEN_MODULE_PREFIXES = [
    "packages.core.agents",
    "apps.api",
]


@dataclass
class Violation:
    """Represents a policy violation."""

    file_path: str
    line: int
    severity: str  # "error" or "warning"
    rule: str
    message: str


@dataclass
class CheckResult:
    """Result of checking a tool file."""

    file_path: str
    violations: list[Violation]
    tool_classes: list[str]


class ToolPolicyChecker(ast.NodeVisitor):
    """AST visitor that checks tool policy rules."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[Violation] = []
        self.tool_classes: list[str] = []
        self.imports: set[str] = set()
        self.current_class: str | None = None
        self.in_run_method = False
        self.run_method_returns_tool_result = False

    def add_violation(self, line: int, severity: str, rule: str, message: str) -> None:
        """Add a violation to the list."""
        self.violations.append(
            Violation(
                file_path=self.file_path,
                line=line,
                severity=severity,
                rule=rule,
                message=message,
            )
        )

    def visit_Import(self, node: ast.Import) -> None:
        """Check import statements."""
        for alias in node.names:
            module_name = alias.name
            self.imports.add(module_name)

            # Check forbidden imports
            if module_name in FORBIDDEN_IMPORTS:
                self.add_violation(
                    node.lineno,
                    "error",
                    "forbidden-import",
                    f"Forbidden import: {module_name}",
                )

            # Check forbidden module prefixes
            for prefix in FORBIDDEN_MODULE_PREFIXES:
                if module_name.startswith(prefix):
                    self.add_violation(
                        node.lineno,
                        "error",
                        "forbidden-module",
                        f"Tool must not import from: {module_name}",
                    )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from...import statements."""
        if node.module:
            module_name = node.module
            self.imports.add(module_name)

            # Check forbidden imports
            if module_name in FORBIDDEN_IMPORTS:
                self.add_violation(
                    node.lineno,
                    "error",
                    "forbidden-import",
                    f"Forbidden import: {module_name}",
                )

            # Check forbidden module prefixes
            for prefix in FORBIDDEN_MODULE_PREFIXES:
                if module_name.startswith(prefix):
                    self.add_violation(
                        node.lineno,
                        "error",
                        "forbidden-module",
                        f"Tool must not import from: {module_name}",
                    )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class definitions for Tool implementations."""
        self.current_class = node.name

        # Check if class inherits from ToolBase
        inherits_toolbase = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "ToolBase":
                inherits_toolbase = True
                self.tool_classes.append(node.name)
                break

        if inherits_toolbase:
            # Check required attributes
            has_name = False
            has_description = False
            has_version = False
            has_run_method = False

            for item in node.body:
                # Check for property decorators
                if isinstance(item, ast.FunctionDef):
                    # Check if it's a property
                    is_property = any(
                        isinstance(dec, ast.Name) and dec.id == "property"
                        for dec in item.decorator_list
                    )
                    is_abstractmethod = any(
                        isinstance(dec, ast.Name) and dec.id == "abstractmethod"
                        for dec in item.decorator_list
                    )

                    if item.name == "name" and (is_property or is_abstractmethod):
                        has_name = True
                    elif item.name == "description" and (
                        is_property or is_abstractmethod
                    ):
                        has_description = True
                    elif item.name == "version" and (is_property or is_abstractmethod):
                        has_version = True
                    elif item.name == "run":
                        has_run_method = True

            # Report missing required attributes
            if not has_name:
                self.add_violation(
                    node.lineno,
                    "error",
                    "missing-attribute",
                    f"Tool {node.name} must define 'name' property",
                )
            if not has_description:
                self.add_violation(
                    node.lineno,
                    "error",
                    "missing-attribute",
                    f"Tool {node.name} must define 'description' property",
                )
            # version has a default, so it's not strictly required but recommended
            if not has_version:
                self.add_violation(
                    node.lineno,
                    "warning",
                    "missing-version",
                    f"Tool {node.name} should define 'version' property",
                )
            if not has_run_method:
                self.add_violation(
                    node.lineno,
                    "error",
                    "missing-run-method",
                    f"Tool {node.name} must implement 'run()' method",
                )

            # Check for docstring
            if not ast.get_docstring(node):
                self.add_violation(
                    node.lineno,
                    "warning",
                    "missing-docstring",
                    f"Tool {node.name} should have a docstring",
                )

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function definitions, especially run() method."""
        if node.name == "run" and self.current_class:
            self.in_run_method = True
            self.run_method_returns_tool_result = False

            # Check return type annotation
            if node.returns:
                if isinstance(node.returns, ast.Name):
                    if node.returns.id == "ToolResult":
                        self.run_method_returns_tool_result = True

            # Check for type hints
            if not node.returns:
                self.add_violation(
                    node.lineno,
                    "warning",
                    "missing-type-hint",
                    "run() method should have return type annotation",
                )

            # Check parameters
            if len(node.args.args) < 2:  # self + context
                self.add_violation(
                    node.lineno,
                    "error",
                    "invalid-signature",
                    "run() must accept 'context: ToolContext' parameter",
                )

            self.generic_visit(node)
            self.in_run_method = False

            # After visiting, check if we found a ToolResult return
            if not self.run_method_returns_tool_result:
                self.add_violation(
                    node.lineno,
                    "warning",
                    "missing-return-annotation",
                    "run() should be annotated to return ToolResult",
                )
        else:
            self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        """Check return statements in run() method."""
        if self.in_run_method and node.value:
            # Check if returning a dict
            if isinstance(node.value, ast.Dict):
                self.add_violation(
                    node.lineno,
                    "error",
                    "invalid-return-value",
                    "run() must return ToolResult, not dict",
                )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for forbidden operations."""
        # Build the full function name
        func_name = self._get_call_name(node.func)

        if func_name in FORBIDDEN_CALLS:
            self.add_violation(
                node.lineno,
                "error",
                "forbidden-call",
                f"Forbidden function call: {func_name}",
            )

        self.generic_visit(node)

    def _get_call_name(self, node: ast.expr) -> str:
        """Extract the full name of a function call."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
            elif isinstance(node.value, ast.Attribute):
                base = self._get_call_name(node.value)
                return f"{base}.{node.attr}"
        return ""


def check_tool_file(file_path: Path) -> CheckResult:
    """Check a single tool file for policy violations."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        checker = ToolPolicyChecker(str(file_path))
        checker.visit(tree)

        return CheckResult(
            file_path=str(file_path),
            violations=checker.violations,
            tool_classes=checker.tool_classes,
        )
    except SyntaxError as e:
        return CheckResult(
            file_path=str(file_path),
            violations=[
                Violation(
                    file_path=str(file_path),
                    line=e.lineno or 0,
                    severity="error",
                    rule="syntax-error",
                    message=f"Syntax error: {e.msg}",
                )
            ],
            tool_classes=[],
        )
    except Exception as e:
        return CheckResult(
            file_path=str(file_path),
            violations=[
                Violation(
                    file_path=str(file_path),
                    line=0,
                    severity="error",
                    rule="check-error",
                    message=f"Error checking file: {e}",
                )
            ],
            tool_classes=[],
        )


def is_allowlisted(file_path: Path, repo_root: Path) -> bool:
    """Check if a file path is in the allowlist."""
    relative_path = file_path.relative_to(repo_root)
    path_str = str(relative_path)

    for allowlist_path in ALLOWLIST_PATHS:
        if path_str.startswith(allowlist_path) or path_str == allowlist_path:
            return True

    # Skip __init__.py files
    if file_path.name == "__init__.py":
        return True

    return False


def find_tool_files(repo_root: Path) -> list[Path]:
    """Find all Python files in the tools directory that contain Tool implementations."""
    tools_dir = repo_root / "packages" / "core" / "tools"

    if not tools_dir.exists():
        return []

    # Exclude base infrastructure files
    INFRASTRUCTURE_FILES = {"base.py", "context.py", "result.py", "__init__.py"}

    python_files = []
    for py_file in tools_dir.rglob("*.py"):
        # Skip if allowlisted
        if is_allowlisted(py_file, repo_root):
            continue

        # Skip infrastructure files
        if py_file.name in INFRASTRUCTURE_FILES:
            continue

        python_files.append(py_file)

    return python_files


def print_violations(results: list[CheckResult]) -> tuple[int, int]:
    """Print violations and return counts."""
    error_count = 0
    warning_count = 0

    for result in results:
        if not result.violations:
            continue

        print(f"\n{result.file_path}:")

        for violation in result.violations:
            prefix = "ERROR" if violation.severity == "error" else "WARNING"
            print(
                f"  {prefix} [line {violation.line}] [{violation.rule}] {violation.message}"
            )

            if violation.severity == "error":
                error_count += 1
            else:
                warning_count += 1

    return error_count, warning_count


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent

    print("=" * 70)
    print("Tool Policy Enforcement Check")
    print("=" * 70)

    # Find tool files
    tool_files = find_tool_files(repo_root)

    if not tool_files:
        print("\n✅ No tool files found to check.")
        return 0

    print(f"\nChecking {len(tool_files)} tool file(s)...")

    # Check each file
    results = [check_tool_file(file_path) for file_path in tool_files]

    # Print violations
    error_count, warning_count = print_violations(results)

    # Print summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Files checked: {len(tool_files)}")
    print(f"Errors: {error_count}")
    print(f"Warnings: {warning_count}")

    if error_count > 0:
        print("\n❌ Policy enforcement failed!")
        print("   Fix the errors above before merging.")
        return 1

    if warning_count > 0:
        print("\n⚠️  Policy check passed with warnings.")
        print("   Consider addressing warnings for better code quality.")
    else:
        print("\n✅ All checks passed!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
