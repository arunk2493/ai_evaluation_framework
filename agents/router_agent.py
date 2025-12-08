
from common.utils import load_prompt
from common.gemini_client import call_gemini

class RouterAgent:
    def predict_route(self, query):
        prompt = load_prompt("router_prompt.txt")
        final = f"{prompt}\nUser Query: {query}\nReply:"
        return call_gemini(final).strip()

    def run(self, query):
        return self.predict_route(query)
