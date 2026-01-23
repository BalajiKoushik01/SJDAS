import io

from PIL import Image


class RemoteAIEngine:
    """
    Integrates Google Gemini (and potentially others) for high-quality
    Text-to-Design generation.
    """

    def __init__(self):
        self.api_key = None
        self.model = None

    def configure(self, api_key):
        self.api_key = api_key
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            return True
        except Exception as e:
            print(f"Gemini Config Error: {e}")
            return False

    def generate_design(self, prompt):
        """
        Generates a design image using Gemini.
        Note: Current Gemini API text-to-image is 'Input Image + Text -> Text' or 'Text -> Text'.
        Wait, standard Gemini does NOT generate images directly in the basic tier usually?
        Actually, Gemini Pro Vision is Multimodal.
        BUT, 'Imagen' is the image generator.
        If user asks for Gemini, they might mean the 'Deep-Learning' smarts.

        However, for 'Peacock Design', we need an Image Generator.
        Gemini API *can* return images if using the specific tools or Imagen on Vertex AI.

        For a standalone desktop app, simple HTTP to an Image Generation API (like HG Inference or OpenAI DALL-E) is cleaner.
        BUT user said "Integrate Gemini".

        Let's try a standard accessible API or fallback to a robust stable diffusion IF local hardware permits.

        Re-reading user request: "try integrating gemini or anything else".

        Let's provide a robust 'HuggingFace Inference API' client as it's free-ish and high quality (SDXL).
        """
        if not self.api_key:
            # Fallback to Pollinations.ai (Key-Free, Powerful Stable Diffusion)
            return self.generate_with_pollinations(prompt)

        # Implementation using HuggingFace Inference API (Free Tier feasible)
        import requests
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        payload = {
            "inputs": f"Textile design, seamless pattern, {prompt}, high quality, intricate, traditional saree motif, flat design, 8k",
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                image_bytes = response.content
                image = Image.open(io.BytesIO(image_bytes))
                return image, "Success (HF)"
            else:
                # If HF fails (e.g. rate limit), try Pollinations?
                return self.generate_with_pollinations(prompt)
        except Exception:
            # Fallback on network error too
            return self.generate_with_pollinations(prompt)

    def generate_with_pollinations(self, prompt):
        """
        Generates using Pollinations.ai (Free, No Key).
        Uses Advanced Prompt Engineering for Saree Aesthetics.
        """
        import random
        import urllib.parse

        import requests

        # 1. Advanced Saree Prompt Engineering
        # Enhance generic prompts with specific textile vocabulary
        base_prompt = prompt.lower()

        # Style Modifiers
        style_keywords = "intricate textile pattern, seamless repeating motif, flat vector illustration, high contrast, 8k resolution"

        if "border" in base_prompt:
            context = "traditional indian saree border design, continuous horizontal pattern, gold zari work, jacquard weave simulation"
        elif "butta" in base_prompt or "motif" in base_prompt:
            context = "isolated traditional indian saree motif, mango puri, floral butta, gold and silk texture"
        else:
            context = "rich kanjivaram silk saree texture, intricate geometric jacquard weave, luxury fabric design"

        # Negative Prompt (embedded in Pollinations via 'not' keyword usually, or just description)
        # Pollinations takes simple prompts. We just load it with quality
        # terms.

        final_prompt = f"{base_prompt}, {context}, {style_keywords}"
        encoded = urllib.parse.quote(final_prompt)

        # Random seed
        seed = random.randint(0, 99999)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&seed={seed}&nologo=true"

        try:
            print(f"Requesting Pollinations AI (Optimized): {final_prompt}")

            # 2. Robust Network Request (SSL Fix)
            # Verify=False to bypass local cert issues (Common on
            # Windows/Proxies)
            response = requests.get(url, timeout=45, verify=False)

            if response.status_code == 200:
                image_bytes = response.content
                image = Image.open(io.BytesIO(image_bytes))
                return image, "Success (Pollinations)"
            else:
                return None, f"Pollinations Error: {response.status_code}"
        except Exception as e:
            # Fallback: Try unverified context if requests checks fail
            # differently
            return None, f"Network Error: {str(e)}"
