
import logging
from typing import Any, Dict, Optional

import requests
import base64
import numpy as np
import cv2
from PyQt6.QtCore import QObject, QThread, pyqtSignal

logger = logging.getLogger("SJ_DAS.Cloud")


class CloudWorker(QThread):
    """Async worker for HTTP requests."""
    finished = pyqtSignal(object)  # Dict or Bytes
    error = pyqtSignal(str)

    def __init__(self, url: str, method: str = 'GET', data: dict = None, headers: dict = None, as_json: bool = False):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data
        self.headers = headers or {}
        self.as_json = as_json

    def run(self):
        try:
            # Increased timeout for GenAI
            if self.method.upper() == 'POST':
                if self.as_json:
                    response = requests.post(self.url, json=self.data, headers=self.headers, timeout=30, verify=True)
                else:
                    response = requests.post(self.url, data=self.data, headers=self.headers, timeout=30, verify=True)
            else:
                response = requests.get(self.url, headers=self.headers, timeout=30, verify=True)
                
            response.raise_for_status()

            # Smart Content Type Handling
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                self.finished.emit(response.json())
            elif 'image' in content_type:
                self.finished.emit(response.content)
            else:
                # Try JSON, fallback to text/bytes
                try:
                    self.finished.emit(response.json())
                except BaseException:
                    self.finished.emit(response.content)
        except Exception as e:
            self.error.emit(str(e))


class CloudService(QObject):
    """
    Manages external API connectivity.
    """
    _instance = None

    # Signals
    color_identified = pyqtSignal(dict)  # {hex, name, rgb}
    met_search_results = pyqtSignal(list)  # List of object IDs
    met_object_details = pyqtSignal(dict)  # Object details with image url
    quote_received = pyqtSignal(dict)  # {text, author}
    request_failed = pyqtSignal(str)
    
    # New Signals for JWT Auth
    login_successful = pyqtSignal(str)
    login_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._cache = {}  # Simple in-memory cache
        self.active_workers = []  # Keep refs
        import os
        self.api_base_url = os.getenv("SJDAS_API_URL", "https://api.sjdas.cloud")
        self.jwt_token = None

    @staticmethod
    def instance() -> 'CloudService':
        if CloudService._instance is None:
            CloudService._instance = CloudService()
        return CloudService._instance

    def _get_auth_headers(self):
        if self.jwt_token:
            return {"Authorization": f"Bearer {self.jwt_token}"}
        return {}

    def _post(self, url: str, data: dict, is_json: bool = True):
        """Internal helper for POST requests with Auth."""
        try:
            headers = self._get_auth_headers()
            if is_json:
                response = requests.post(url, json=data, headers=headers, timeout=60, verify=True)
            else:
                response = requests.post(url, data=data, headers=headers, timeout=60, verify=True)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Cloud POST Error: {e}")
            return None

    def backup_to_cloud(self, design_id: str, data: dict):
        """Uploads design JSON to cloud for multi-device sync."""
        url = f"{self.api_base_url}/api/v1/sync/backup"
        return self._post(url, {"design_id": design_id, "data": data})

    def generate_ai_design(self, prompt: str):
        """Cloud-offloaded AI design generation."""
        url = f"{self.api_base_url}/api/v1/ai/generate"
        response = self._post(url, {"prompt": prompt}, is_json=False) # Form data
        if response and response.status_code == 200:
             resp_data = response.json()
             img_data_str = resp_data["image_data"].split(",")[1]
             img_bytes = base64.b64decode(img_data_str)
             nparr = np.frombuffer(img_bytes, np.uint8)
             return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return None

    def login(self, username, password):
        """Authenticate with the SJDAS Backend."""
        url = f"{self.api_base_url}/api/v1/auth/token"
        data = {
            "username": username,
            "password": password
        }
        # OAuth2 token endpoint requires form data, not JSON
        worker = CloudWorker(url, method='POST', data=data, as_json=False)
        worker.finished.connect(self._handle_login_success)
        worker.error.connect(self._handle_login_error)
        worker.start()
        self.active_workers.append(worker)

    def _handle_login_success(self, data):
        if isinstance(data, dict) and "access_token" in data:
            self.jwt_token = data["access_token"]
            self.login_successful.emit(self.jwt_token)
        else:
            self.login_failed.emit("Invalid response format from server.")

    def _handle_login_error(self, error_msg):
        self.login_failed.emit(error_msg)


    def identify_color(self, hex_code: str):
        """
        Fetch color name from The Color API.
        Args:
            hex_code: e.g. "#FF0000" or "FF0000"
        """
        clean_hex = hex_code.replace('#', '')
        # ... (Cache check omitted for brevity in diff, but implementation keeps it)
        # Check cache
        if clean_hex in self._cache:
            self.color_identified.emit(self._cache[clean_hex])
            return

        url = f"https://www.thecolorapi.com/id?hex={clean_hex}"
        self._start_worker(
            url, lambda d: self._handle_color_response(
                clean_hex, d))

    def search_met_museum(self, query: str):
        """Search The Met Collection."""
        url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q={query}"
        self._start_worker(url, self._handle_met_search, 'met_search')

    def get_met_object(self, object_id: int):
        """Get details for a specific object."""
        url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
        self._start_worker(url, self._handle_met_object, 'met_object')

    def get_daily_quote(self):
        """Get a random quote for inspiration."""
        url = "https://dummyjson.com/quotes/random"
        self._start_worker(url, self._handle_quote, 'quote')

    def _start_worker(self, url, callback, tag=None):
        worker = CloudWorker(url)
        worker.finished.connect(callback)
        worker.error.connect(self._handle_error)
        worker.start()
        self.active_workers.append(worker)

    def _handle_met_search(self, data):
        ids = data.get('objectIDs', [])
        if ids:
            self.met_search_results.emit(ids[:20])  # Limit to 20 for now
        else:
            self.met_search_results.emit([])

    def _handle_met_object(self, data):
        self.met_object_details.emit({
            'id': data.get('objectID'),
            'title': data.get('title'),
            'image_url': data.get('primaryImageSmall'),
            'date': data.get('objectDate')
        })

    def _handle_quote(self, data):
        self.quote_received.emit({
            'text': data.get('quote', 'Design is intelligence made visible.'),
            'author': data.get('author', 'Unknown')
        })

    def _handle_color_response(self, hex_key: str, data: Dict[str, Any]):
        """Process API response."""
        result = {
            "hex": data.get("hex", {}).get("value", ""),
            "name": data.get("name", {}).get("value", "Unknown"),
            "contrast": data.get("contrast", {}).get("value", "#000000")
        }
        self._cache[hex_key] = result
        self.color_identified.emit(result)

    def _handle_error(self, error_msg: str):
        logger.warning(f"Cloud Request Failed: {error_msg}")
        self.request_failed.emit(error_msg)
