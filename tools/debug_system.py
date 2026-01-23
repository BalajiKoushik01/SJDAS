import importlib
import os
import pkgutil
import sys
import traceback

# Add project root
sys.path.insert(0, os.getcwd())


def scan_imports():
    print(f"--- Scanning SJ-DAS System Health ---")
    print(f"Root: {os.getcwd()}\n")

    modules_found = 0
    modules_failed = []

    # Walk sj_das directory
    for root, dirs, files in os.walk("sj_das"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                rel_path = os.path.join(root, file)
                module_name = rel_path.replace(os.sep, ".")[:-3]

                try:
                    importlib.import_module(module_name)
                    # print(f"  [OK] {module_name}")
                    modules_found += 1
                except Exception as e:
                    print(f"  [FAIL] {module_name} -> {e}")
                    modules_failed.append((module_name, str(e)))

    print(f"\n--- Scan Complete ---")
    print(f"Total Modules Verified: {modules_found}")

    if modules_failed:
        print(f"FAILED MODULES ({len(modules_failed)}):")
        for mod, err in modules_failed:
            print(f" - {mod}: {err}")
    else:
        print("ALL MODULES IMPORTED SUCCESSFULLY.")


if __name__ == "__main__":
    scan_imports()
