
from common.utils import load_prompt
from common.gemini_client import call_gemini

class KPIAgent:
    def compute_kpi(self, query):
        prompt = load_prompt("kpi_prompt.txt")
        final = f"{prompt}\nQuery: {query}"
        return call_gemini(final)

    def run(self, query):
        return self.compute_kpi(query)
