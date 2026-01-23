import json
import os

from sj_das.utils.logger import logger


class AgentEngine:
    """
    Local AGI Engine (Phi-3.5).
    Acts as an intelligent copilot for the user.
    """

    def __init__(self):
        self.llm = None
        self.is_ready = False
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'llm',
            'Phi-3.5-mini-instruct-Q4_K_M.gguf')
        self.history = []
        self.system_prompt = (
            "You are the SJ-DAS Copilot, an expert in Jacquard Textile Design and Manufacturing. "
            "You help the user with design advice, technical loom calculations, and software control. "
            "If the user asks to perform an action (rotate, upscale, cost, segment), "
            "reply with a JSON object: {\"action\": \"action_name\", \"params\": {}}. "
            "Otherwise, reply with helpful text."
        )

    def load_model(self):
        if self.is_ready:
            return True

        try:
            from sj_das.core.crew_engine import LocalLLMEngine
            self.llm_engine = LocalLLMEngine()
            if self.llm_engine.llm is None:
                # Try loading if not loaded inside
                # Actually LocalLLMEngine loads in init
                pass

            self.llm = self.llm_engine.llm  # Backward compatibility
            self.is_ready = True
            logger.info("AGI Engine Loaded (Llama 3.2 via Crew).")
            return True
        except ImportError:
            logger.error("llama-cpp-python not installed.")
            return False
        except Exception as e:
            logger.error(f"AGI Load Error: {e}")
            return False

    def chat(self, user_input: str) -> dict:
        """
        Sends message to LLM.
        Returns Dict with 'text' and optional 'action'.
        """
        if not self.load_model():
            return {
                "text": "I am not active yet. Please check if the model is downloaded.", "action": None}

        # Check for Complex Crew Task
        if any(w in user_input.lower()
               for w in ["plan", "collection", "research", "analyze design"]):
            return self._run_crew(user_input)

        # Build Context (limited history)
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        # Add last 4 turns
        messages.extend(self.history[-4:])
        messages.append({"role": "user", "content": user_input})

        try:
            # Direct Llama Call via Wrapped Engine
            # We need to access standard openai-like completions if possible
            # LocalLLMEngine exposes generate_response but chat is better
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=512,
                temperature=0.7
            )

            content = response['choices'][0]['message']['content']

            # Save history
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": content})

            # Tool Parsing logic
            import re
            action = None
            text = content

            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    json_str = match.group(0)
                    data = json.loads(json_str)
                    if "action" in data:
                        action = data
                except BaseException:
                    pass

            return {"text": text, "action": action}

        except Exception as e:
            logger.error(f"AGI Chat Error: {e}")
            return {"text": "I encountered a neural error.", "action": None}

    def _run_crew(self, task_desc):
        """Runs a multi-agent crew for complex tasks."""
        try:
            from sj_das.core.crew_engine import Agent, Crew, Task

            # Spawning Agents (The Crew)
            designer = Agent(
                role="Creative Director",
                goal="Visualize aesthetic textile concepts",
                backstory="Expert in Indian Saree trends and motifs."
            )

            engineer = Agent(
                role="Textile Engineer",
                goal="Ensure manufacturability on Jacquard Loom",
                backstory="Expert in weave structures and yarn density."
            )

            # Define Tasks
            task1 = Task(
                f"Analyze the creative requirements: {task_desc}",
                designer)
            task2 = Task(
                f"Based on the creative concept, specify technical loom settings (hooks, weft).",
                engineer)

            # Launch
            crew = Crew(agents=[designer, engineer], tasks=[task1, task2])
            crew.set_llm(self.llm_engine)

            result = crew.kickoff()

            final_res = f"**Crew Execution Complete**\n\n{result}"
            return {"text": final_res, "action": None}

        except Exception as e:
            logger.error(f"Crew Error: {e}")
            return {"text": f"Crew failed to assemble: {e}", "action": None}
