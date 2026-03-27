import os
import subprocess
import shutil
import sys

def build():
    print("=" * 60)
    print("   SJDAS Enterprise - Desktop Build Orchestrator")
    print("=" * 60)

    # 1. Cleanup
    print("\n[1/4] Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"      Removed {folder}/")

    # 2. Verify Dependencies
    print("\n[2/4] Verifying PyInstaller...")
    try:
        import PyInstaller
        print(f"      PyInstaller {PyInstaller.__version__} found.")
    except ImportError:
        print("      Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 3. Build Executable
    print("\n[3/4] Running PyInstaller (this may take several minutes)...")
    try:
        # Patch environment for Intel MKL collision (WinError 1114)
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        
        # Use simple spec file
        # Use venv-specific pyinstaller if available
        pyi_exe = os.path.join("venv", "Scripts", "pyinstaller.exe")
        if not os.path.exists(pyi_exe):
            pyi_exe = "pyinstaller" # Fallback
            
        print(f"      Using: {pyi_exe}")
        subprocess.check_call([pyi_exe, "--noconfirm", "sjdas_enterprise.spec"])
        print("\n[SUCCESS] Build completed.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] PyInstaller failed with exit code {e.returncode}")
        sys.exit(1)

    # 4. Final Output
    print("\n[4/4] Verifying artifacts...")
    exe_path = os.path.join("dist", "SJDAS_Enterprise.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"      Found: {exe_path} ({size_mb:.2f} MB)")
        print("\n" + "=" * 60)
        print("   READY FOR DISTRIBUTION")
        print("   Location: " + os.path.abspath(exe_path))
        print("=" * 60)
    else:
        print("      [ERROR] Could not find SJDAS_Enterprise.exe in dist/")

if __name__ == "__main__":
    build()
