
import logging

from PyQt6.QtCore import QObject, pyqtSignal

from sj_das.core.services.ai_service import AIService
from sj_das.core.services.cloud_service import CloudService

logger = logging.getLogger("SJ_DAS.Cortex.Lobes")


class BaseLobe(QObject):
    """Abstract Lobe."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.ai = AIService.instance()
        self.cloud = CloudService.instance()


class VisionLobe(BaseLobe):
    """
    Sight & Understanding.
    Powers: Segmentation (SAM), Recognition (Met API/CLIP/LLaVA).
    """

    def analyze_selection(self, image_data, x, y):
        """Analyze what is at x,y."""
        # 1. Segment
        mask = self.ai.get_magic_wand_mask(x, y)
        if mask is not None:
            return {"mask": mask, "label": "Detected Object"}
        return None

    def analyze_image(self, base64_image: str):
        """Ask Local Vision AI (LLaVA) to describe the image."""
        import requests

        logger.info("VisionLobe: Analyzing image with LLaVA...")
        try:
            payload = {
                "model": "llava",
                "prompt": "Describe this textile pattern in detail. Mention style, motifs, and colors. Be concise.",
                "images": [base64_image],
                "stream": False
            }
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30)
            if resp.status_code == 200:
                desc = resp.json().get("response", "Analysis failed.")
                self.finished.emit(desc)
            else:
                self.error.emit(f"Vision API Error: {resp.status_code}")
        except Exception as e:
            self.error.emit(f"Vision Analysis Failed: {e}")


class CreativeLobe(BaseLobe):
    """
    Imagination & Generation.
    Powers: Stable Diffusion, Pattern Synthesis.
    """

    def generate_pattern(self, prompt: str):
        """Generate a pattern based on text using Pollinations.ai."""
        import random

        logger.info(f"Dreaming of: {prompt}")
        seed = random.randint(0, 999999)
        enhanced_prompt = f"seamless texture, {prompt}, high quality textile pattern"
        url = f"https://pollinations.ai/p/{enhanced_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"

        self._start_worker(url)

    def _start_worker(self, url):
        from sj_das.core.services.cloud_service import CloudWorker

        # We use CloudService to manage worker to keep it alive
        CloudService.instance()._start_worker(url, self._on_generated)

    def _on_generated(self, data):
        """Handle raw image data from Cloud."""
        from PyQt6.QtGui import QImage
        try:
            img = QImage()
            if isinstance(data, bytes):
                img.loadFromData(data)
                if not img.isNull():
                    logger.info("CreativeLobe: Image generated successfully.")
                    self.finished.emit(img)
                else:
                    self.error.emit("Generated data is not a valid image.")
            else:
                self.error.emit("Unexpected data format from generator.")
        except Exception as e:
            self.error.emit(f"Failed to process generated image: {e}")


class LogicLobe(BaseLobe):
    """
    Reasoning & Planning.
    Powers: Intent Parsing (LLM).
    """
    intent_parsed = pyqtSignal(object)  # Dict or List of Dicts

    def process_command(self, text: str):
        """
        Parse natural language into structured intent.
        Tries Local LLM (Ollama) first, falls back to Regex.
        """
        # 1. Try LLM
        if self._check_ollama():
            try:
                plan = self._query_ollama(text)
                if plan:
                    logger.info(f"LLM Plan: {plan}")
                    self.intent_parsed.emit(plan)
                    return plan
            except Exception as e:
                logger.warning(f"LLM Failed: {e}. Falling back to regex.")

        # 2. Fallback: Simple NLP
        text = text.lower()
        intent = {"action": "unknown", "params": {}}

        if "select" in text or "wand" in text:
            intent["action"] = "activate_tool"
            intent["params"]["tool"] = "magic_wand"
        elif "upscale" in text:
            intent["action"] = "upscale"
        elif "inspire" in text or "met" in text:
            intent["action"] = "open_inspiration"
        elif "describe" in text or "analyze" in text or "what is this" in text:
            intent["action"] = "analyze_canvas"
        elif "generate" in text or "make" in text or "create" in text:
            intent["action"] = "generate"
            prompt = text.replace(
                "generate",
                "").replace(
                "make",
                "").replace(
                "create",
                "").strip()
            intent["params"]["prompt"] = prompt

        self.intent_parsed.emit(intent)
        return intent

    def _check_ollama(self):
        import requests
        try:
            requests.get("http://localhost:11434", timeout=0.2)
            return True
        except BaseException:
            return False

    def _query_ollama(self, text):
        import json

        import requests

        system_prompt = """
        You are Cortex, an AI assistant for a Textile Design App.
        Parse the user's request into a JSON list of actions.
        Available actions:
        - {"action": "generate", "params": {"prompt": "..."}}
        - {"action": "upscale", "params": {}}
        - {"action": "activate_tool", "params": {"tool": "magic_wand"}}
        - {"action": "open_inspiration", "params": {}}
        - {"action": "analyze_canvas", "params": {}}

        Examples:
        "Make a floral pattern" -> [{"action": "generate", "params": {"prompt": "floral pattern"}}]
        "Describe this image" -> [{"action": "analyze_canvas", "params": {}}]

        Return ONLY valid JSON. No markdown.
        """

        payload = {
            "model": "llama3",
            "prompt": f"{system_prompt}\nUser: {text}\nCortex:",
            "stream": False,
            "format": "json"
        }

        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("response", "")
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
        except BaseException:
            pass
        return None
