import os
import re
from .gemini_cli import configure_gemini, generate_response

class JulesBrain:
    def __init__(self):
        self.configured = configure_gemini()
        
    def extract_code(self, response_text):
        """Extract code block from markdown response."""
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response_text, re.DOTALL)
        if code_blocks:
            # Return the longest block as it's likely the full file
            return max(code_blocks, key=len)
        return response_text # Fallback if no blocks
        
    def fix_syntax_error(self, file_path, code_content, error_msg):
        """Ask Gemini to fix a syntax error."""
        if not self.configured: 
            return None
            
        prompt = f"""
You are Jules, an expert Python code maintenance agent.
I have a file '{os.path.basename(file_path)}' that is throwing a SyntaxError/IndentationError.

ERROR:
{error_msg}

CODE:
```python
{code_content}
```

Please fix the error and return the COMPLETE valid python code.
Do not wrap in markdown if possible, or I will strip it.
"""
        response = generate_response(prompt)
        return self.extract_code(response)
        
    def refactor_code(self, file_path, code_content):
        """Ask Gemini to refactor code for better quality."""
        if not self.configured: 
            return None
            
        prompt = f"""
You are Jules, an expert Python code maintenance agent.
Please refactor the following code from '{os.path.basename(file_path)}'.
Focus on:
1. Robust error handling (try/except blocks).
2. Clean code practices (PEP8).
3. Adding type hints if missing.
4. Improving comments and docstrings.

CODE:
```python
{code_content}
```

Return the COMPLETE refactored code.
"""
        response = generate_response(prompt)
        return self.extract_code(response)
