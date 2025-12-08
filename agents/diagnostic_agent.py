
from common.utils import load_prompt
from common.gemini_client import call_gemini

class DiagnosticAgent:
    def explain(self, query):
        prompt = load_prompt("diagnostic_prompt.txt")
        final = f"{prompt}\nIssue: {query}"
        return call_gemini(final)

    def run(self, query):
        return self.explain(query)
