
from common.utils import load_prompt
from common.gemini_client import call_gemini

class InsightAgent:
    def generate_insight(self, query):
        prompt = load_prompt("insight_prompt.txt")
        final = f"{prompt}\nInsightRequest: {query}"
        return call_gemini(final)

    def run(self, query):
        return self.generate_insight(query)
