import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread

def stream_output(process, prefix):
    for line in iter(process.stdout.readline, ''):
        print(f"[{prefix}] {line.strip()}")
    process.stdout.close()

def start_backend(project_root):
    print("🚀 Starting Backend (FastAPI)...")
    backend_script = os.path.join(project_root, 'backend', 'main.py')
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root
    
    return subprocess.Popen(
        [sys.executable, backend_script],
        cwd=project_root,
        stdout=sys.stdout,
        stderr=sys.stderr, # Share console
        env=env
    )

def start_frontend(project_root):
    print("🚀 Starting Frontend (Next.js)...")
    web_dir = os.path.join(project_root, 'web')
    
    # Check if node_modules exists
    if not os.path.exists(os.path.join(web_dir, 'node_modules')):
        print("📦 Installing frontend dependencies (first run)...")
        subprocess.run(["npm", "install"], cwd=web_dir, shell=True)
    
    return subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=web_dir,
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=True
    )

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    backend_proc = None
    frontend_proc = None
    
    try:
        print("=" * 60)
        print("   SJ-DAS Pro | Design Automation System")
        print("   Version: 2026.1.0 (Web Edition)")
        print("   Architecture: Next.js Frontend + FastAPI Backend")
        print("=" * 60)
        
        backend_proc = start_backend(project_root)
        frontend_proc = start_frontend(project_root)
        
        print("\n✨ Services starting...")
        print("   Backend: http://localhost:8000")
        print("   Frontend: http://localhost:3000")
        print("\nWaiting for servers to initialize (5s)...")
        time.sleep(5)
        
        # Open Browser
        print("🌍 Opening Application...")
        webbrowser.open("http://localhost:3000")
        
        # Keep running
        backend_proc.wait()
        frontend_proc.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        if backend_proc: backend_proc.terminate()
        if frontend_proc: 
            # NPM spawns children, hard to kill cleanly on Windows without tree kill
            # Try basic terminate
            frontend_proc.terminate() 
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
