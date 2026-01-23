import argparse
import os
import subprocess
import sys
from datetime import datetime

# Configuration
SKIP_EXTENSIONS = {
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.bmp', '.tga', '.tiff', '.webp',
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.db', '.sqlite', '.sqlite3', '.pd', '.arrow', '.parquet',
    '.mp3', '.wav', '.mp4', '.avi', '.mov', '.mkv',
    '.ttf', '.otf', '.woff', '.woff2'
}
MAX_FILE_SIZE_BYTES = 1024 * 1024  # 1 MB


class JulesAgent:
    def __init__(self, fix_mode=False, upgrade_mode=False,
                 security_mode=False, type_mode=False):
        self.fix_mode = fix_mode
        self.upgrade_mode = upgrade_mode
        self.security_mode = security_mode
        self.type_mode = type_mode
        self.issues_fixed = 0
        self.issues_found = 0

    def greeting(self):
        print(f"🤖 Jules Code Maintenance Agent v2.5")
        print(f"Timestamp: {datetime.now()}")
        if self.fix_mode:
            print("🔧 FIX MODE: ERROR CORRECTION ENABLED")
        if self.security_mode:
            print("🛡️ SECURITY MODE: VULNERABILITY SCANNING ENABLED")
        if self.type_mode:
            print("🧠 TYPE MODE: STATIC ANALYSIS ENABLED")
        print("--------------------------------")

    def is_binary_or_skip(self, file_path):
        """Check if file should be skipped based on extension or size."""
        _, ext = os.path.splitext(file_path.lower())
        if ext in SKIP_EXTENSIONS:
            return True

        try:
            if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
                return True
        except OSError:
            return True  # Cannot access

        return False

    def scan_and_fix(self, path):
        print(f"Scanning {path}...")

        for root, dirs, files in os.walk(path):
            # Safe Directory Skipping
            dirs[:] = [d for d in dirs if d not in
                       ['node_modules', '.git', 'venv', '.venv', '__pycache__', 'build', 'dist', '.next']]

            for file in files:
                full_path = os.path.join(root, file)

                if self.is_binary_or_skip(full_path):
                    continue

                self.process_file(full_path)

    def process_file(self, file_path):
        """Analyze and optionally fix a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for generic issues
            if 'TODO' in content:
                # print(f"[NOTE] TODO found in {os.path.basename(file_path)}")
                self.issues_found += 1
            if 'FIXME' in content:
                print(
                    f"[WARNING] FIXME found in {os.path.basename(file_path)}")
                self.issues_found += 1

            # AUTO-FIX: Python Formatting
            if self.fix_mode and file_path.endswith('.py'):
                self.apply_python_fixes(file_path)

        except Exception as e:
            print(f"[ERROR] Could not process {file_path}: {e}")

    def apply_python_fixes(self, file_path):
        """Run autopep8 and isort to clean up code."""
        try:
            # check for indentation errors or simple formatting
            run_fix = False

            # 1. Sort Imports
            subprocess.run(
                [sys.executable, "-m", "isort", file_path],
                check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # 2. Fix PEP8 (Indentation, spacing)
            result = subprocess.run(
                [sys.executable, "-m", "autopep8",
                    "--in-place", "--aggressive", file_path],
                check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            if result.returncode == 0:
                # print(f"  ✨ Fixed styling in {os.path.basename(file_path)}")
                self.issues_fixed += 1

        except Exception as e:
            print(f"  ❌ Failed to fix {os.path.basename(file_path)}: {e}")

    def upgrade_dependencies(self):
        """Upgrade pip packages."""
        print("\n🚀 running dependency upgrades...")
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, "-m", "pip",
                           "install", "--upgrade", "pip"], check=True)

            # Attempt to upgrade requirements if file exists
            req_path = os.path.join(os.getcwd(), 'requirements.txt')
            if os.path.exists(req_path):
                print("  Found requirements.txt, checking for upgrades...")
                # This is a basic upgrade strategy
                subprocess.run(
                    [sys.executable, "-m", "pip", "install",
                        "--upgrade", "-r", req_path],
                    check=False
                )
                print("  ✅ Dependencies upgraded.")
            else:
                print("  ⚠️ No requirements.txt found.")

        except Exception as e:
            print(f"  ❌ Upgrade failed: {e}")

    def run_security_scan(self, path):
        """Run Bandit security scan."""
        print(f"\n🛡️ Running Security Scan (Bandit)...")
        try:
            # Recursive scan, skip tests
            subprocess.run([sys.executable, "-m", "bandit", "-r",
                           path, "-ll", "-x", "tests,venv,.venv"], check=False)
        except Exception as e:
            print(f"  ❌ Security scan failed: {e}")

    def run_type_check(self, path):
        """Run MyPy type check."""
        print(f"\n🧠 Running Type Check (MyPy)...")
        try:
            subprocess.run([sys.executable, "-m", "mypy", path,
                           "--ignore-missing-imports"], check=False)
        except Exception as e:
            print(f"  ❌ Type check failed: {e}")

    def run(self, root_path):
        self.greeting()
        self.scan_and_fix(root_path)

        if self.security_mode:
            self.run_security_scan(root_path)

        if self.type_mode:
            self.run_type_check(root_path)

        if self.upgrade_mode:
            self.upgrade_dependencies()

        print("--------------------------------")
        print(f"Scan Complete.")
        print(f"Issues Found (Syntax/TODOs): {self.issues_found}")
        if self.fix_mode:
            print(f"Files Processed/Fixed: {self.issues_fixed}")
            print("✨ Codebase has been polished by Jules.")
        else:
            print("💡 Tip: Run with --fix to auto-correct formatting issues.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Jules Code Maintenance Agent")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix code style issues")
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Upgrade project dependencies")
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security vulnerability scan")
    parser.add_argument(
        "--types",
        action="store_true",
        help="Run static type checking")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    agent = JulesAgent(
        fix_mode=args.fix,
        upgrade_mode=args.upgrade,
        security_mode=args.security,
        type_mode=args.types
    )
    agent.run(project_root)
