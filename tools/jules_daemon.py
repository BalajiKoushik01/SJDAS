import sys
import time
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ast

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.jules_maintenance import JulesAgent
from tools.jules_brain import JulesBrain

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("jules.log"),
        logging.StreamHandler()
    ]
)

class JulesEventHandler(FileSystemEventHandler):
    def __init__(self, brain):
        self.brain = brain
        self.last_modified = {}
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        # Debounce
        current_time = time.time()
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 2:
                return
        self.last_modified[file_path] = current_time

        # Check if Python file
        if file_path.endswith('.py'):
            self.process_python_file(file_path)

    def process_python_file(self, file_path):
        """Check for errors and fix if needed."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 1. Syntactic Validate
            try:
                ast.parse(content)
                # Valid syntax, maybe we refactor?
                # skipping refactor on every save to avoid token usage/loops
                pass 
            except SyntaxError as e:
                logging.error(f"❌ Syntax Error in {file_path}: {e}")
                logging.info(f"🧠 Asking Jules to autofix...")
                
                fixed_code = self.brain.fix_syntax_error(file_path, content, str(e))
                if fixed_code and fixed_code != content:
                    self.apply_fix(file_path, fixed_code)
                    
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

    def apply_fix(self, file_path, new_code):
        """Write the fix back to disk safely."""
        try:
            # Backup
            backup_path = file_path + ".bak"
            if not os.path.exists(backup_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    with open(backup_path, 'w', encoding='utf-8') as b:
                        b.write(f.read())
            
            # Write New
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
                
            logging.info(f"✅ Fixed {file_path}")
            
        except Exception as e:
            logging.error(f"Failed to apply fix: {e}")

def start_daemon():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    brain = JulesBrain()
    
    event_handler = JulesEventHandler(brain)
    observer = Observer()
    
    # Observe recursive
    observer.schedule(event_handler, project_root, recursive=True)
    observer.start()
    
    print("🤖 Jules 24/7 Daemon Started.")
    print(f"Monitoring {project_root} for changes...")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
            # Potentially run periodic full scans here
    except KeyboardInterrupt:
        observer.stop()
        
    observer.join()

if __name__ == "__main__":
    start_daemon()
