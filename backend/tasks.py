from celery import Celery
import time
import logging
import os
import numpy as np
from backend.services.kali_engine import generate_tapered_kali, stitch_master_file
from backend.services.bmp_compiler import export_to_indexed_bmp

logger = logging.getLogger(__name__)

# Connect Celery to Redis broker (Configurable via REDIS_URL)
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('sjdas_tasks', broker=redis_url, backend=redis_url)

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
    base_url = os.getenv('BASE_DOWNLOAD_URL', 'http://api.sjdas.cloud/downloads')
    download_url = f"{base_url}/{os.path.basename(file_path)}"
    
    logger.info("Loom file compiled: %s", file_path)
    return download_url


@celery_app.task(bind=True)
def run_decode_pipeline(self, params: dict):
    """
    6-step Screenshot → Loom decode pipeline (Celery async).
    Pushes progress via Celery state; WebSocket endpoint in main.py polls and streams.
    """
    from backend.services.decode_service import run_full_pipeline, DecodeParams
    import dataclasses

    task_id = params.get('task_id', self.request.id)
    decode_params = DecodeParams(
        image_path=params['image_path'],
        hook_count=params.get('hook_count', 600),
        ends_ppi=params.get('ends_ppi', 80),
        color_count=params.get('color_count', 6),
        style_override=params.get('style_override'),
    )

    def on_progress(step: int, total: int, message: str):
        progress = int((step / total) * 100)
        self.update_state(state='PROGRESS', meta={'progress': progress, 'message': message, 'task_id': task_id})

    result = run_full_pipeline(decode_params, progress_callback=on_progress)
    return dataclasses.asdict(result)
