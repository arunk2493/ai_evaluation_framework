
from common.utils import load_prompt
from common.gemini_client import call_gemini

class PersonaAgent:
    def handle(self, query):
        prompt = load_prompt("persona_prompt.txt")
        final = f"{prompt}\nRequest: {query}"
        return call_gemini(final)

    def run(self, query):
        return self.handle(query)
