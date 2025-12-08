
from common.utils import load_prompt
from common.gemini_client import call_gemini

class DashboardAgent:
    def render(self, name):
        prompt = load_prompt("dashboard_prompt.txt")
        final = f"{prompt}\nDashboardName: {name}"
        return call_gemini(final)

    def run(self, query):
        return self.render(query)
