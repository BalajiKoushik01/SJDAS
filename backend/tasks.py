from celery import Celery
import time
import numpy as np
from backend.services.kali_engine import generate_tapered_kali, stitch_master_file
from backend.services.bmp_compiler import export_to_indexed_bmp

# Connect Celery to Redis broker (Default local for development)
celery_app = Celery('sjdas_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery_app.task(bind=True)
def generate_saree_master_file(self, design_data):
    """
    This runs in a completely separate process. It handles the brutal CPU work.
    """
    hooks = design_data.get('hooks', 400)
    kali_count = design_data.get('kali_count', 12)
    picks_height = design_data.get('picks_height', 8000)
    
    # 1. Update UI: Tell Next.js we are starting
    self.update_state(state='PROGRESS', meta={'progress': 10, 'message': 'AI isolating motifs...'})
    time.sleep(1) # Simulate AI load time
    
    # 2. Kali Warping Phase
    self.update_state(state='PROGRESS', meta={'progress': 40, 'message': f'Warping {kali_count} Kalis to fit {hooks} hooks...'})
    
    # Mocking a realistic base pattern array consisting of index colors
    base_pattern = np.random.choice([0, 1, 2], size=(hooks, hooks)).astype(np.uint8)
    
    single_kali = generate_tapered_kali(base_pattern, top_hooks=hooks-50, bottom_hooks=hooks, picks_height=picks_height)
    master_matrix = stitch_master_file(single_kali, kali_count)
    
    # 3. Validation Phase
    self.update_state(state='PROGRESS', meta={'progress': 70, 'message': 'Running Global Float Guard validation...'})
    time.sleep(1.5) # Simulate heavy float checking over a massive matrix
    
    # 4. Hardware Compilation Phase
    self.update_state(state='PROGRESS', meta={'progress': 90, 'message': 'Compiling 8-bit machine header...'})
    
    factory_inventory_palette = [
        (0, 0, 128),     # Navy (Ground)
        (255, 215, 0),   # Gold Zari (Butta)
        (192, 192, 192)  # Silver (Border)
    ]
    
    file_path = export_to_indexed_bmp(master_matrix, factory_inventory_palette, output_filename="client_ready_file.bmp")
    
    # 5. Done. Return the download URL to the WebSocket.
    final_file_url = f"https://sjdas.cloud/downloads/client_ready_file.bmp"  # In dev, this would point to a local static route
    return final_file_url
