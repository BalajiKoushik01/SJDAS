"""
SJ-DAS Code Maintenance System.

This module provides the core logic for the '24/7 Agent' that:
1. Scans the codebase for maintenance opportunities.
2. Identifies complex functions and missing docstrings.
3. Uses Local LLM to generate refactored code and documentation.
"""

import ast
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from sj_das.core.engines.llm.local_llm_engine import get_local_llm_engine

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("SJ_DAS.Maintainer")


class CodeAnalyzer(ast.NodeVisitor):
    """
    AST-based analyzer to gather code metrics.
    """
    def __init__(self):
        self.stats = {
            "functions": [],
            "classes": [],
            "missing_docstrings": []
        }

    def visit_FunctionDef(self, node):
        # Cyclomatic Complexity (Rough Approx by line count for now)
        line_count = node.end_lineno - node.lineno
        
        has_docstring = ast.get_docstring(node) is not None
        
        self.stats["functions"].append({
            "name": node.name,
            "lineno": node.lineno,
            "lines": line_count,
            "has_docstring": has_docstring
        })

        if not has_docstring:
            self.stats["missing_docstrings"].append(node.name)
            
        self.generic_visit(node)


class CodeMaintainer:
    """
    The 'Brain' of the automated maintenance agent.
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.llm = get_local_llm_engine()
        self.ignore_dirs = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode'}

    def start_session(self):
        """Begin a maintenance session."""
        logger.info("Starting Maintenance Session...")
        
        # 1. Ensure AI is ready
        if not self.llm.is_configured():
            logger.info("Initializing Local AI Engine...")
            if not self.llm.configure(""): # Auto-discover
                logger.error("AI Engine could not be loaded. Aborting maintenance.")
                return

        # 2. Scan Codebase
        files = self._scan_files()
        logger.info(f"Scanned {len(files)} Python files.")

        for file_path in files:
            self._process_file(file_path)

    def _scan_files(self) -> List[Path]:
        """Recursively find all python files."""
        py_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                if file.endswith(".py"):
                    py_files.append(Path(root) / file)
        return py_files

    def _process_file(self, file_path: Path):
        """Analyze and improve a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                tree = ast.parse(content)
            except SyntaxError:
                logger.warning(f"Syntax Error in {file_path.name}, skipping.")
                return

            analyzer = CodeAnalyzer()
            analyzer.visit(tree)

            # 1. Check for Missing Docstrings
            self._handle_docstrings(file_path, content, analyzer.stats["missing_docstrings"])

            # 2. Check for Complexity
            self._handle_complexity(file_path, content, analyzer.stats["functions"])

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")

    def _handle_docstrings(self, file_path: Path, content: str, missing_list: List[str]):
        """Generate docstrings for undocumented functions."""
        if not missing_list:
            return

        # Rate limit: Process one per file per run to avoid huge diffs
        target_func = missing_list[0] 
        logger.info(f"[{file_path.name}] Generating docstring for '{target_func}'...")

        # Request AI Generation
        prompt = f"""
        You are a Google-Standard Python Code Maintainer.
        Read this function signature and body from file '{file_path.name}':
        
        [CODE START]
        {self._extract_function_code(content, target_func)}
        [CODE END]

        Generate a Python Google-Style docstring for this function.
        Return ONLY the docstring (triple quotes included).
        """
        
        docstring = self.llm.generate(prompt)
        if docstring:
            self._apply_docstring(file_path, target_func, docstring)

    def _handle_complexity(self, file_path: Path, content: str, functions: List[Dict]):
        """Identify and suggest refactoring for complex functions."""
        COMPLEXITY_THRESHOLD = 50 # Lines
        
        for func in functions:
            if func["lines"] > COMPLEXITY_THRESHOLD:
                logger.info(f"[{file_path.name}] High Complexity: '{func['name']}' ({func['lines']} lines).")
                self._generate_refactor_suggestion(file_path, content, func["name"])
                # Only do one per file to avoid overwhelming
                break

    def _generate_refactor_suggestion(self, file_path: Path, full_content: str, func_name: str):
        """Ask AI to refactor a complex function."""
        func_code = self._extract_function_code(full_content, func_name)
        
        prompt = f"""
        You are an Expert Python Refactoring Agent.
        The following function '{func_name}' is too complex ({len(func_code.splitlines())} lines).
        
        [CODE]
        {func_code}
        [/CODE]
        
        Refactor this function to be cleaner, smaller, and more modular.
        You may break it into sub-helper functions.
        Return the fully refactored Python code for this function (and any helpers).
        """
        
        refactored_code = self.llm.generate(prompt)
        
        if refactored_code:
            # For Safety: Write to a separate .refactor file
            suggestion_path = file_path.with_suffix(file_path.suffix + ".refactor")
            with open(suggestion_path, "w", encoding="utf-8") as f:
                f.write(f"# Auto-Refactor Suggestion for {func_name}\n")
                f.write(refactored_code)
            logger.info(f"Refactor suggestion saved to: {suggestion_path.name}")

    def _extract_function_code(self, content: str, func_name: str) -> str:
        """Helper to extract raw function code using AST ranges (Simplified)."""
        # A robust implementation handles finding the exact lines.
        # For this v1 prototype, we re-parse.
        lines = content.splitlines()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                # ast lines are 1-indexed
                return "\n".join(lines[node.lineno-1 : node.end_lineno])
        return ""

    def _apply_docstring(self, file_path: Path, func_name: str, docstring: str):
        """Injects the docstring into the file (Simplified append for v1)."""
        # In a real implementation, we would rewrite the file AST or splice text.
        # For safety v1: We just log the suggestion or create a patch file.
        patch_path = file_path.with_suffix(file_path.suffix + ".docs")
        with open(patch_path, "a", encoding="utf-8") as f:
            f.write(f"\n# Docstring for {func_name}:\n{docstring}\n")
        logger.info(f"Docstring suggestion appended to {patch_path.name}")
