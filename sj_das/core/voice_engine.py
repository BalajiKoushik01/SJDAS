import re

from sj_das.utils.logger import logger


class VoiceCommandEngine:
    """
    Handles Voice Command Processing.
    Designed to be SAFE: If speech libraries are missing,
    it can accepts string input (for text command bar).
    """

    def __init__(self):
        self.available = False
        try:
            import pyaudio  # Required for mic
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone()
            self.available = True

            # Check for Offline Vosk
            import importlib.util
            self.use_vosk = importlib.util.find_spec("vosk") is not None

            logger.info(
                f"Voice Engine: Enabled. Offline (Vosk): {self.use_vosk}")
        except ImportError:
            logger.warning(
                "Voice Engine: SpeechRecognition lib not found. Voice disabled.")
            self.available = False
        except Exception as e:
            logger.warning(f"Voice Engine: Mic error? {e}")
            self.available = False

        # Command Mapping (Keyword -> ActionID)
        self.commands = {
            "rotate": "rotate_90",
            "flip": "flip_h",
            "upscale": "upscale_4x",
            "scan": "defect_scan",
            "cost": "show_costing",
            "quantize": "quantize_8",
            "save": "save_file",
            "zoom in": "zoom_in",
            "zoom out": "zoom_out",
            "magic": "magic_wand"
        }

    def listen_and_parse(self):
        """
        Listens for 3 seconds and returns mapped action ID or None.
        Blocking call (run in thread).
        """
        if not self.available:
            return None, "Voice Lib Missing"

        try:
            with self.mic as source:
                logger.info("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, timeout=3, phrase_time_limit=3)

            # Recognize
            if self.use_vosk:
                text = self._listen_vosk()
                if not text:
                    # Fallback
                    text = self.recognizer.recognize_google(audio).lower()
            else:
                text = self.recognizer.recognize_google(audio).lower()

            logger.info(f"Distinguished: '{text}'")

            # Parse
            for key, action_id in self.commands.items():
                if key in text:
                    return action_id, text

            return None, text

        except Exception as e:
            logger.error(f"Voice Error: {e}")
            return None, str(e)

    def _listen_vosk(self):
        """Offline recognition using Vosk."""
        try:
            import json

            import pyaudio
            from vosk import KaldiRecognizer, Model

            # Check for model in assets
            model_path = os.path.join(
                os.getcwd(),
                'sj_das',
                'assets',
                'models',
                'voice',
                'vosk-model-small-en-us-0.15')
            if not os.path.exists(model_path):
                logger.warning(
                    "Vosk model not found. Using Google Cloud fallback.")
                return None

            model = Model(model_path)

            # Customization: Construct Grammar from Commands
            # "[\"rotate\", \"flip\", \"upscale\", ...]"
            vocab = list(self.commands.keys())
            # Add some common fillers if needed or strictly commands
            vocab.append("[unk]")

            # grammar syntax for Vosk: '["word1", "word2", "[unk]"]'
            grammar = json.dumps(vocab)

            rec = KaldiRecognizer(model, 16000, grammar)

            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000)
            stream.start_stream()

            logger.info("Listening (Vosk Offline)...")

            # Listen for 3 seconds of data approx (16000 * 3 / 8000 = 6 chunks)
            # This is a bit blocking.
            text = ""
            for i in range(10):  # ~3-4 seconds
                data = stream.read(4000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text += res.get('text', '') + " "

            # Final result
            res = json.loads(rec.FinalResult())
            text += res.get('text', '')

            stream.stop_stream()
            stream.close()
            p.terminate()

            return text.strip()

        except Exception as e:
            logger.error(f"Vosk Error: {e}")
            return None

    def parse_text(self, text):
        """Debug method to parse typed text."""
        text = text.lower()
        for key, action_id in self.commands.items():
            if key in text:
                return action_id
        return None
