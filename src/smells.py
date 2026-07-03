"""
Test Smell Detectors for Flaky Test Prediction

This module provides AST-based static analysis to detect common test smells
that correlate with test flakiness. Based on research from IDoFT and Flakify.

Each detector function takes Python source code (as a string) and returns
detection results for individual test functions.
"""

import ast
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class SmellResult:
    """Result of smell detection for a single test function."""
    function_name: str
    smells: Dict[str, bool]
    stats: Dict[str, int]


class SmellDetector:
    """
    Detects test smells in Python test code using AST analysis.

    Detects the following smells:
    1. Fire and Forget - spawns threads/processes without proper synchronization
    2. Mystery Guest - accesses external resources (filesystem, network, DB)
    3. Conditional Logic - contains if/elif statements
    4. Assertion Roulette - multiple assertions without clear messages
    5. Resource Optimism - accesses resources without existence checks
    6. Test Run War - reads/writes shared/global state
    7. Eager Testing - tests too many things at once (>5 method calls, heuristic)
    8. Indirect Testing - tests through other objects (depth >= 2, heuristic)

    Note: eager_testing threshold (>5 calls) and indirect_testing depth (>=2)
    are judgment calls based on practical observation, not derived from papers.
    """

    # Modules/functions that indicate thread/process spawning
    ASYNC_PATTERNS = {
        'threading': {'Thread', 'Timer'},
        'multiprocessing': {'Process', 'Pool'},
        'concurrent.futures': {'ThreadPoolExecutor', 'ProcessPoolExecutor'},
        'asyncio': {'create_task', 'ensure_future', 'run'},
    }

    # Patterns indicating external resource access
    EXTERNAL_RESOURCE_PATTERNS = {
        'open',  # filesystem
        'requests',  # HTTP
        'urllib',
        'socket',
        'sqlite3',
        'psycopg2',
        'pymongo',
        'redis',
        'subprocess',
        'os.system',
        'os.popen',
    }

    # File/path related functions
    FILE_ACCESS_PATTERNS = {'open', 'read', 'write', 'Path', 'os.path'}

    # Path existence check functions
    EXISTENCE_CHECKS = {'exists', 'isfile', 'isdir', 'is_file', 'is_dir'}

    def __init__(self, source_code: str):
        """
        Initialize detector with Python source code.

        Args:
            source_code: Python source code as a string
        """
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self._imports = self._collect_imports()

    def _collect_imports(self) -> Dict[str, str]:
        """Collect all imports in the module for reference."""
        imports = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = f"{module}.{alias.name}"
        return imports

    def _get_test_functions(self) -> List[ast.FunctionDef]:
        """Extract all test functions (functions starting with 'test_')."""
        test_functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith('test_'):
                    test_functions.append(node)
        return test_functions

    def detect_fire_and_forget(self, func: ast.FunctionDef) -> bool:
        """
        Detect if test spawns threads/processes without proper join/wait.

        Fire and Forget smell occurs when async operations are started
        but not properly synchronized, leading to race conditions.
        """
        spawns_async = False
        has_join_or_wait = False

        for node in ast.walk(func):
            # Check for thread/process creation
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)

                # Check for Thread(), Process(), etc.
                for module, classes in self.ASYNC_PATTERNS.items():
                    if any(cls in func_name for cls in classes):
                        spawns_async = True
                    if module in func_name:
                        spawns_async = True

                # Check for .start() calls (thread/process start)
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'start':
                        spawns_async = True
                    if node.func.attr in ('join', 'wait', 'result', 'shutdown'):
                        has_join_or_wait = True

        # Fire and forget = spawns async but doesn't wait
        return spawns_async and not has_join_or_wait

    def detect_mystery_guest(self, func: ast.FunctionDef) -> bool:
        """
        Detect if test accesses external resources (filesystem, network, DB).

        Mystery Guest smell occurs when tests depend on external state
        that isn't set up within the test itself.
        """
        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)

                # Check for external resource access patterns
                for pattern in self.EXTERNAL_RESOURCE_PATTERNS:
                    if pattern in func_name:
                        return True

                # Check imports for known external libraries
                if isinstance(node.func, ast.Name):
                    if node.func.id in self._imports:
                        imported_from = self._imports[node.func.id]
                        for pattern in self.EXTERNAL_RESOURCE_PATTERNS:
                            if pattern in imported_from:
                                return True

            # Check for attribute access to external modules
            if isinstance(node, ast.Attribute):
                full_name = self._get_attribute_name(node)
                for pattern in self.EXTERNAL_RESOURCE_PATTERNS:
                    if pattern in full_name:
                        return True

        return False

    def detect_conditional_logic(self, func: ast.FunctionDef) -> bool:
        """
        Detect if test contains conditional (if/elif) statements.

        Conditional logic in tests can lead to different execution paths,
        making test behavior non-deterministic or harder to reason about.
        """
        for node in ast.walk(func):
            if isinstance(node, ast.If):
                return True
        return False

    def detect_assertion_roulette(self, func: ast.FunctionDef) -> bool:
        """
        Detect multiple assertions without descriptive messages.

        Assertion Roulette occurs when a test has multiple assertions
        and it's unclear which one failed without additional context.
        """
        assertions = []

        for node in ast.walk(func):
            if isinstance(node, ast.Assert):
                # Check if assertion has a message
                has_message = node.msg is not None
                assertions.append(has_message)

            # Also check for unittest-style assertions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr.startswith('assert'):
                        # Check if has message argument (usually last arg)
                        has_message = len(node.args) > 2 or len(node.keywords) > 0
                        assertions.append(has_message)

        # Roulette = multiple assertions without messages
        assertions_without_msg = [a for a in assertions if not a]
        return len(assertions_without_msg) > 1

    def detect_resource_optimism(self, func: ast.FunctionDef) -> bool:
        """
        Detect file/resource access without prior existence check.

        Resource Optimism occurs when code assumes a resource exists
        without verifying it first.
        """
        has_file_access = False
        has_existence_check = False
        file_access_line = float('inf')
        existence_check_line = 0

        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)

                # Check for existence checks
                for check in self.EXISTENCE_CHECKS:
                    if check in func_name:
                        has_existence_check = True
                        existence_check_line = max(existence_check_line,
                                                   getattr(node, 'lineno', 0))

                # Check for file access - only built-in open(), not .read() methods
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    has_file_access = True
                    file_access_line = min(file_access_line,
                                          getattr(node, 'lineno', float('inf')))

        # Resource optimism = file access without prior existence check
        if has_file_access and not has_existence_check:
            return True
        if has_file_access and has_existence_check and file_access_line < existence_check_line:
            return True

        return False

    def detect_test_run_war(self, func: ast.FunctionDef) -> bool:
        """
        Detect read/write to shared/global/module-level state.

        Test Run War occurs when tests modify shared state,
        causing interference between test runs.
        """
        for node in ast.walk(func):
            # Check for global keyword
            if isinstance(node, ast.Global):
                return True

            # Check for nonlocal keyword
            if isinstance(node, ast.Nonlocal):
                return True

            # Check for assignment to module-level attributes
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        # Check if accessing class/module attribute
                        if isinstance(target.value, ast.Name):
                            # Assigning to SomeClass.attribute or module.attribute
                            return True

            # Check for modifications to class attributes via self.__class__
            if isinstance(node, ast.Attribute):
                attr_name = self._get_attribute_name(node)
                if '__class__' in attr_name or 'cls.' in attr_name:
                    return True

        return False

    def detect_eager_testing(self, func: ast.FunctionDef) -> bool:
        """
        Detect if test is testing too many things at once.

        Eager Testing occurs when a single test exercises many different
        methods or behaviors, making it fragile and hard to maintain.

        Heuristic: More than 5 distinct method calls on test subject.
        """
        method_calls = set()

        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    method_calls.add(node.func.attr)

        # Eager testing if testing many methods (threshold: 5)
        return len(method_calls) > 5

    def detect_indirect_testing(self, func: ast.FunctionDef) -> bool:
        """
        Detect if test verifies behavior through indirect objects.

        Indirect Testing occurs when assertions are made on objects
        other than the primary subject under test.

        Heuristic: Assertions on deeply nested attributes (2+ levels).
        """
        for node in ast.walk(func):
            if isinstance(node, ast.Assert):
                # Check the assertion expression for deep nesting
                if self._has_deep_attribute_access(node.test):
                    return True

            # Check unittest-style assertions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr.startswith('assert'):
                        for arg in node.args:
                            if self._has_deep_attribute_access(arg):
                                return True

        return False

    def _has_deep_attribute_access(self, node: ast.AST, depth: int = 0) -> bool:
        """Check if an expression has deeply nested attribute access."""
        if isinstance(node, ast.Attribute):
            if depth >= 2:
                return True
            return self._has_deep_attribute_access(node.value, depth + 1)

        for child in ast.iter_child_nodes(node):
            if self._has_deep_attribute_access(child, depth):
                return True

        return False

    def _get_call_name(self, call_node: ast.Call) -> str:
        """Extract the full name of a function call."""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return self._get_attribute_name(call_node.func)
        return ""

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Recursively build the full attribute name."""
        if isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        elif isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        return node.attr

    def get_test_stats(self, func: ast.FunctionDef) -> Dict[str, int]:
        """
        Get basic statistics for a test function.

        Returns:
            Dict with lines_of_code, assertion_count, import_count
        """
        # Lines of code (approximate from AST)
        start_line = func.lineno
        end_line = max(getattr(n, 'lineno', start_line)
                       for n in ast.walk(func))
        loc = end_line - start_line + 1

        # Count assertions
        assertion_count = 0
        for node in ast.walk(func):
            if isinstance(node, ast.Assert):
                assertion_count += 1
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr.startswith('assert'):
                        assertion_count += 1

        return {
            'lines_of_code': loc,
            'assertion_count': assertion_count,
            'import_count': len(self._imports),
        }

    def analyze_test(self, func: ast.FunctionDef) -> SmellResult:
        """
        Run all smell detectors on a single test function.

        Args:
            func: AST node for the test function

        Returns:
            SmellResult with all detected smells and stats
        """
        smells = {
            'fire_and_forget': self.detect_fire_and_forget(func),
            'mystery_guest': self.detect_mystery_guest(func),
            'conditional_logic': self.detect_conditional_logic(func),
            'assertion_roulette': self.detect_assertion_roulette(func),
            'resource_optimism': self.detect_resource_optimism(func),
            'test_run_war': self.detect_test_run_war(func),
            'eager_testing': self.detect_eager_testing(func),
            'indirect_testing': self.detect_indirect_testing(func),
        }

        stats = self.get_test_stats(func)

        return SmellResult(
            function_name=func.name,
            smells=smells,
            stats=stats
        )

    def analyze_all_tests(self) -> List[SmellResult]:
        """
        Analyze all test functions in the source code.

        Returns:
            List of SmellResult for each test function found
        """
        results = []
        for func in self._get_test_functions():
            results.append(self.analyze_test(func))
        return results


def analyze_file(file_path: str) -> List[SmellResult]:
    """
    Convenience function to analyze a Python test file.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        List of SmellResult for each test function in the file
    """
    with open(file_path, 'r') as f:
        source_code = f.read()

    detector = SmellDetector(source_code)
    return detector.analyze_all_tests()


def analyze_source(source_code: str) -> List[SmellResult]:
    """
    Convenience function to analyze Python test source code.

    Args:
        source_code: Python source code as a string

    Returns:
        List of SmellResult for each test function in the code
    """
    detector = SmellDetector(source_code)
    return detector.analyze_all_tests()
