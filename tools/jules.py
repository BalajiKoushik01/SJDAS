#!/usr/bin/env python3
"""
Jules: The SJ-DAS Automated Maintenance Agent.

This script scans the codebase for maintenance tasks, TODOs, and health checks.
It is designed to be run via GitHub Actions.
"""

import os
import re
import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
REPORT_FILE = PROJECT_ROOT / "JULES_REPORT.md"
IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build"}
IGNORE_EXTENSIONS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".lock"}

def scan_file_for_tags(file_path):
    """Scans a file for TODO, FIXME, and XXX tags."""
    tags = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                timestamp = datetime.datetime.now().isoformat()
                if "TODO" in line:
                    tags.append(f"- [ ] **TODO** ({file_path.name}:{i}): {line.strip()}")
                elif "FIXME" in line:
                    tags.append(f"- [ ] **FIXME** ({file_path.name}:{i}): {line.strip()}")
                elif "XXX" in line:
                    tags.append(f"- [ ] **XXX** ({file_path.name}:{i}): {line.strip()}")
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
    return tags

def main():
    print("Jules is initializing...")
    print(f"Scanning project root: {PROJECT_ROOT}")

    all_tags = []
    file_count = 0

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in IGNORE_EXTENSIONS:
                continue
            
            file_count += 1
            tags = scan_file_for_tags(file_path)
            all_tags.extend(tags)

    # Generate Report
    report_content = f"""# Jules Maintenance Report
**Date**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Files Scanned**: {file_count}

## Action Items
"""
    
    if all_tags:
        report_content += "\n".join(all_tags)
    else:
        report_content += "No TODOs or FIXMEs found. The codebase is clean!"

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Scan complete. Found {len(all_tags)} items.")
    print(f"Report generated at: {REPORT_FILE}")

if __name__ == "__main__":
    main()
