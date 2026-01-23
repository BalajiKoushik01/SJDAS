
import logging
import os

import numpy as np
import torch

logger = logging.getLogger("SJ_DAS.WhisperEngine")


class WhisperEngine:
    """
    State-of-the-Art Voice Recognition using Faster-Whisper.
    Replaces legacy Vosk engine.
    """

    def __init__(self, model_size="medium.en"):
        self.model = None
        self.size = model_size
        self.is_ready = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"

    def load_model(self) -> bool:
        if self.is_ready:
            return True

        try:
            from faster_whisper import WhisperModel

            logger.info(f"Loading Whisper ({self.size}) on {self.device}...")
            # This will auto-download to cache if not present
            self.model = WhisperModel(
                self.size,
                device=self.device,
                compute_type=self.compute_type)

            self.is_ready = True
            logger.info("Whisper Engine Ready.")
            return True

        except ImportError:
            logger.error(
                "faster-whisper not installed. pip install faster-whisper")
            return False
        except Exception as e:
            logger.error(f"Whisper Load Error: {e}")
            return False

    def transcribe(self, audio_data: np.ndarray,
                   sample_rate: int = 16000) -> str:
        """
        Transcribe audio to text.
        Args:
            audio_data: float32 numpy array
        """
        if not self.load_model():
            return ""

        try:
            segments, info = self.model.transcribe(audio_data, beam_size=5)

            full_text = " ".join(
                [segment.text for segment in segments]).strip()

            if full_text:
                logger.debug(
                    f"Transcribed: '{full_text}' (Prob: {info.language_probability:.2f})")

            return full_text

        except Exception as e:
            logger.error(f"Transcribe Error: {e}")
            return ""
