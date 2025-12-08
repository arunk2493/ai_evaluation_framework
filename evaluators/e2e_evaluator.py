
from agents.router_agent import RouterAgent
from agents.kpi_agent import KPIAgent
from agents.diagnostic_agent import DiagnosticAgent
from agents.simulation_agent import SimulationAgent
from agents.insight_agent import InsightAgent
from agents.dashboard_agent import DashboardAgent
from agents.memory_agent import MemoryAgent
from common.deepeval_helpers import evaluate_response
from evaluators.sql_assertion_engine import assert_kpi_with_output
import logging

log = logging.getLogger(__name__)

class E2EEvaluator:
    def __init__(self):
        self.router = RouterAgent()
        self.kpi = KPIAgent()
        self.diagnostic = DiagnosticAgent()
        self.simulation = SimulationAgent()
        self.insight = InsightAgent()
        self.dashboard = DashboardAgent()
        self.memory = MemoryAgent()

    def run_full_conversation(self, user_query):
        report = {"steps": [], "classification": None}

        # ---------------- ROUTER ----------------
        classification = self.router.predict_route(user_query)
        report["classification"] = classification

        # ---------------- KPI ----------------
        try:
            kpi_out = self.kpi.compute_kpi(user_query)
            region = None
            for r in ["NY","CA","UK","IN","US","EU","APAC","LATAM"]:
                if r.lower() in user_query.lower() or (kpi_out and r.lower() in kpi_out.lower()):
                    region = r
                    break

            if region:
                kpi_assert = assert_kpi_with_output(region, kpi_out)
                kpi_metrics = evaluate_response(user_query, kpi_out, kpi_assert["ground"])
            else:
                kpi_metrics = evaluate_response(user_query, kpi_out, "KPI concise summary")

            report["steps"].append({"agent":"KPI","output":kpi_out,"metrics":kpi_metrics,"region":region})
            self.memory.store("last_kpi", str(kpi_out))
        except Exception as e:
            report["steps"].append({"agent":"KPI","output":str(e),"metrics":{"failed":True}})

        # ---------------- DIAGNOSTIC ----------------
        try:
            diag_query = "Why did this happen?"
            diag_out = self.diagnostic.explain(diag_query)
            diag_metrics = evaluate_response(diag_query, diag_out,"Primary cause and secondary contributors")
            report["steps"].append({"agent":"Diagnostic","output":diag_out,"metrics":diag_metrics})
        except Exception as e:
            report["steps"].append({"agent":"Diagnostic","output":str(e),"metrics":{"failed":True}})

        # ---------------- SIMULATION ----------------
        try:
            sim_query = "Simulate a 10% price increase on electronics"
            sim_out = self.simulation.simulate(sim_query)
            sim_metrics = evaluate_response(sim_query, sim_out,"Assumptions + projected impact")
            report["steps"].append({"agent":"Simulation","output":sim_out,"metrics":sim_metrics})
        except Exception as e:
            report["steps"].append({"agent":"Simulation","output":str(e),"metrics":{"failed":True}})

        # ---------------- INSIGHT ----------------
        try:
            insight_query = "Based on KPI and simulation, give top actions"
            insight_out = self.insight.generate_insight(insight_query)
            insight_metrics = evaluate_response(insight_query, insight_out,"pattern, reason, impact, action")
            report["steps"].append({"agent":"Insight","output":insight_out,"metrics":insight_metrics})
        except Exception as e:
            report["steps"].append({"agent":"Insight","output":str(e),"metrics":{"failed":True}})

        # ---------------- DASHBOARD ----------------
        try:
            dash_out = self.dashboard.render("sales_overview")
            dash_metrics = evaluate_response("dashboard_render", dash_out,"KPI_NAME: VALUE TREND: up/down CONFIDENCE")
            report["steps"].append({"agent":"Dashboard","output":dash_out,"metrics":dash_metrics})
        except Exception as e:
            report["steps"].append({"agent":"Dashboard","output":str(e),"metrics":{"failed":True}})

        # ---------------- MEMORY RETRIEVAL ----------------
        try:
            mem_out = self.memory.retrieve("last_kpi")
            report["steps"].append({"agent":"Memory","output":mem_out,"metrics":{"note":"memory retrieval"}})
        except Exception as e:
            report["steps"].append({"agent":"Memory","output":str(e),"metrics":{"failed":True}})

        # ---------------- SUMMARY ----------------
        passed = sum(1 for s in report["steps"] if not (s.get("metrics") and s["metrics"].get("failed")))
        report["summary"] = {
            "total": len(report["steps"]),
            "passed": passed,
            "pass_rate": passed / max(1, len(report["steps"]))
        }
        return report
