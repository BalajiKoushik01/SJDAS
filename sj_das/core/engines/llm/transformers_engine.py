"""
Transformers LLM Engine - Pure Python Fallback.

This engine uses Hugging Face 'transformers' directly.
It is slower than GGUF/llama-cpp but requires NO C++ build tools.
Ideal for users who cannot install Visual Studio Build Tools.
"""

import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

logger = logging.getLogger("SJ_DAS.TransformersLLMEngine")

class TransformersLLMEngine:
    """
    Pure Python LLM Backend.
    Uses 'Qwen/Qwen2.5-Coder-1.5B-Instruct' (Small) or similar 
    that fits in memory without heavy quantization.
    """
    
    def __init__(self):
        self.pipeline = None
        self.model_name = "Qwen/Qwen2.5-Coder-1.5B-Instruct" # Small enough for pure torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def configure(self, model_path: str = "") -> bool:
        """Load the model (Auto-download from HF if needed)."""
        if self.pipeline:
            return True
            
        try:
            logger.info(f"Initializing Pure-Python LLM ({self.model_name}) on {self.device}...")
            
            # Use AutoModel for broad support
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            self.pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512
            )
            
            logger.info("Transformers Engine Loaded Successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Transformers Load Error: {e}")
            return False
            
    def generate(self, prompt: str) -> str:
        """Generate text."""
        if not self.pipeline:
            return "Error: AI not loaded."
            
        try:
            # Chat Format
            messages = [
                {"role": "system", "content": "You are a helpful coding assistant for SJ-DAS."},
                {"role": "user", "content": prompt}
            ]
            
            output = self.pipeline(messages)
            # Result is usually list of dicts or just text depending on version
            # Transformers pipeline for chat usually returns generated text
            generated_text = output[0]['generated_text'][-1]['content']
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation Error: {e}")
            return f"Error: {e}"

    def analyze_design(self, description: str) -> str:
         return self.generate(f"Analyze this design: {description}")
    
    def is_configured(self):
        return self.pipeline is not None

# Global Instance
_engine = None

def get_transformers_engine():
    global _engine
    if _engine is None:
        _engine = TransformersLLMEngine()
    return _engine
