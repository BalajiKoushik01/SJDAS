import json
import os
import queue
import sys
import time

import numpy as np
import sounddevice as sd

from sj_das.core.engines.voice.whisper_engine import WhisperEngine
from sj_das.utils.logger import logger


class TextileVoiceAssistant:
    """
    Offline Voice Control using OpenAI Whisper (via faster-whisper).
    """

    def __init__(self):
        self.engine = WhisperEngine(model_size="medium.en")
        self.q = queue.Queue()
        self.is_listening = False

    def load_model(self):
        return self.engine.load_model()

    def _audio_callback(self, indata, frames, time, status):
        """Capture audio."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def listen_command(self, duration=5):
        """
        Listen and Transcribe.
        """
        if not self.load_model():
            return "Error: Whisper Engine Failed"

        try:
            logger.info("Listening (Whisper)...")

            # Record audio into buffer
            audio_buffer = []

            with sd.InputStream(samplerate=16000, channels=1, callback=self._audio_callback):
                start = time.time()
                while time.time() - start < duration:
                    # Collecting audio...
                    pass

            # Gather data from queue
            while not self.q.empty():
                audio_buffer.append(self.q.get())

            if not audio_buffer:
                return ""

            # Concatenate and normalize
            # Whisper expects float32 [-1, 1]
            audio_np = np.concatenate(
                audio_buffer,
                axis=0).flatten().astype(
                np.float32)

            # Transcribe
            text = self.engine.transcribe(audio_np)
            return text

        except Exception as e:
            logger.error(f"Voice listen error: {e}")
            return ""


# Singleton
_voice_assistant = None


def get_voice_assistant():
    global _voice_assistant
    if _voice_assistant is None:
        _voice_assistant = TextileVoiceAssistant()
    return _voice_assistant
