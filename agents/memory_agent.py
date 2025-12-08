
from common.utils import load_prompt
from common.gemini_client import call_gemini

class MemoryAgent:
    _memory = {}

    def store(self, key, value):
        self._memory[key] = value
        return "stored"

    def retrieve(self, key):
        if key not in self._memory:
            return "not found"
        prompt = load_prompt("memory_prompt.txt")
        final = f"{prompt}\nRetrieved: {self._memory[key]}"
        return call_gemini(final)

    def run(self, query):
        return self.retrieve(query)
