
from common.utils import load_prompt
from common.gemini_client import call_gemini

class SimulationAgent:
    def simulate(self, query):
        prompt = load_prompt("simulation_prompt.txt")
        final = f"{prompt}\nScenario: {query}"
        return call_gemini(final)

    def run(self, query):
        return self.simulate(query)
