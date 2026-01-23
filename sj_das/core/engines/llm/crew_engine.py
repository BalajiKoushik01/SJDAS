import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from sj_das.utils.logger import logger


# Mocking the CrewAI structure for Local Execution
class Agent:
    def __init__(self, role, goal, backstory, verbose=True):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose

    def execute_task(self, task, context=None, llm=None):
        if self.verbose:
            logger.info(f"[{self.role}] Starting Task: {task.description}")

        # Construct Prompt
        prompt = f"""
        You are {self.role}.
        Goal: {self.goal}
        Backstory: {self.backstory}

        Current Task: {task.description}
        Context from previous agents: {context if context else 'None'}

        Provide your final answer as the {self.role}.
        """

        if llm:
            return llm.generate_response(prompt)
        return "LLM Not Available"


class Task:
    def __init__(self, description, agent, expected_output=""):
        self.description = description
        self.agent = agent
        self.expected_output = expected_output


class Crew:
    def __init__(self, agents, tasks, process='sequential'):
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.llm_engine = None

    def set_llm(self, llm_engine):
        self.llm_engine = llm_engine

    def kickoff(self):
        context = ""
        results = []

        for task in self.tasks:
            if self.llm_engine:
                res = task.agent.execute_task(task, context, self.llm_engine)
                context += f"\nResult from {task.agent.role}:\n{res}\n"
                results.append(res)
            else:
                logger.error("Crew has no LLM Engine!")

        return context


class LocalLLMEngine:
    """Wrapped Llama 3.2 for Crew usage"""

    def __init__(self):
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'llm',
            'Llama-3.2-3B-Instruct-Q4_K_M.gguf')
        self.llm = None
        self._load()

    def _load(self):
        if not os.path.exists(self.model_path):
            return
        try:
            from llama_cpp import Llama
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=4096,
                n_gpu_layers=-1,
                verbose=False)
        except BaseException:
            pass

    def generate_response(self, prompt):
        if not self.llm:
            return "Artificial Intelligence Offline."

        messages = [{"role": "user", "content": prompt}]
        res = self.llm.create_chat_completion(
            messages=messages, max_tokens=1024)
        return res['choices'][0]['message']['content']
