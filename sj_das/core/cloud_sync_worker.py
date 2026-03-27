import json
import logging
import time
import requests
import websocket
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)

class CloudSyncWorker(QThread):
    """
    A PyQt6 QThread worker that handles asynchronous communication with 
    the SJDAS v2.0 FastAPI cloud backend.
    
    1. Sends a REST POST to initiate the heavy Celery Kali-warp math.
    2. Instantly connects to the WebSocket stream to receive live progress.
    3. Emits pyqtSignals to safely update the desktop UI without freezing.
    """
    
    # PyQt Signals to communicate with the main desktop thread
    progress_updated = pyqtSignal(int, str)  # (percentage, message_context)
    task_success = pyqtSignal(str)           # (file_download_url)
    task_error = pyqtSignal(str)             # (error_message)

    def __init__(self, api_url: str, ws_url: str, payload: dict, parent=None):
        super().__init__(parent)
        self.api_url = api_url
        self.ws_url = ws_url
        self.payload = payload
        self.task_id = None
        self._is_running = True

    def run(self):
        """The main thread execution logic."""
        if not self._is_running:
            return

        # Step 1: Fire the REST Request
        self.progress_updated.emit(5, "Initiating Cloud Handshake...")
        try:
            logger.info(f"Triggering REST POST to {self.api_url}")
            response = requests.post(self.api_url, json=self.payload, timeout=15, verify=True)
            response.raise_for_status()
            
            data = response.json()
            if "task_id" not in data:
                raise ValueError("Cloud response missing task_id.")
            
            self.task_id = data["task_id"]
            logger.info(f"Cloud Task Started: {self.task_id}")
            self.progress_updated.emit(10, "Shadow Canvas Task Initialized. Connecting to WebSockets...")
            
        except Exception as e:
            logger.error(f"Failed to initiate cloud task: {str(e)}")
            self.task_error.emit(f"Cloud Server Error: {str(e)}")
            return

        # Step 2: Open the WebSocket Connection for Real-Time Streaming
        ws_endpoint = f"{self.ws_url}/{self.task_id}"
        logger.info(f"Connecting to WS: {ws_endpoint}")
        
        # We use a blocking websocket client here inside the QThread.
        # It's totally safe because QThread runs in the background.
        try:
            ws = websocket.WebSocket()
            ws.connect(ws_endpoint, timeout=5)
            
            while self._is_running:
                raw_message = ws.recv()
                if not raw_message:
                    break
                    
                msg = json.loads(raw_message)
                status = msg.get("status")
                
                if status == "progress":
                    meta = msg.get("meta", {})
                    progress_pct = meta.get("progress", 10)
                    message_text = meta.get("message", "Processing in Cloud...")
                    self.progress_updated.emit(progress_pct, message_text)
                    
                elif status == "success":
                    self.progress_updated.emit(100, "Cloud Compilation Complete!")
                    self.task_success.emit(msg.get("file_url", ""))
                    break
                    
                elif status == "error":
                    self.task_error.emit(msg.get("message", "Unknown Cloud Error"))
                    break
                    
            ws.close()
            
        except websocket.WebSocketTimeoutException:
            self.task_error.emit("WebSocket connection timed out.")
        except Exception as e:
            logger.error(f"WebSocket Error: {str(e)}")
            self.task_error.emit(f"Live Stream Error: {str(e)}")

    def stop(self):
        """Allows the desktop UI to cancel the background synchronization."""
        self._is_running = False
        self.quit()
        self.wait()
