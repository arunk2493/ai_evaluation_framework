
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

# Configure logging for better test visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class E2EEvaluator:
    def __init__(self):
        log.info("Initializing E2E Evaluator with all agents")
        self.router = RouterAgent()
        self.kpi = KPIAgent()
        self.diagnostic = DiagnosticAgent()
        self.simulation = SimulationAgent()
        self.insight = InsightAgent()
        self.dashboard = DashboardAgent()
        self.memory = MemoryAgent()
        log.info("E2E Evaluator initialization complete")

    def run_full_conversation(self, user_query):
        log.info(f"Starting E2E conversation flow for query: '{user_query}'")
        report = {"steps": [], "classification": None, "query": user_query}

        # ---------------- STEP 1: ROUTER ----------------
        log.info("Step 1: Router - Classifying user query")
        classification = self.router.predict_route(user_query)
        report["classification"] = classification
        log.info(f"Router classification: {classification}")

        # ---------------- STEP 2: KPI ----------------
        log.info("Step 2: KPI - Computing KPI metrics")
        try:
            kpi_out = self.kpi.compute_kpi(user_query)
            log.info(f"KPI outp: {kpi_out}")
            region = None
            for r in ["NY","CA","UK","IN","US","EU","APAC","LATAM"]:
                if r.lower() in user_query.lower() or (kpi_out and r.lower() in kpi_out.lower()):
                    region = r
                    break
            log.info(f"Detected region: {region}")

            if region:
                kpi_assert = assert_kpi_with_output(region, kpi_out)
                kpi_metrics = evaluate_response(user_query, kpi_out, kpi_assert["ground"])
                log.info(f"KPI assertion for {region}: {kpi_assert['ground']}")
            else:
                kpi_metrics = evaluate_response(user_query, kpi_out, "KPI concise summary")

            report["steps"].append({"agent":"KPI","output":kpi_out,"metrics":kpi_metrics,"region":region,"step":2})
            self.memory.store("last_kpi", str(kpi_out))
            log.info("Step 2 completed successfully")
        except Exception as e:
            log.error(f"Step 2 failed: {str(e)}")
            report["steps"].append({"agent":"KPI","output":str(e),"metrics":{"failed":True},"step":2})

        # ---------------- STEP 3: DIAGNOSTIC ----------------
        log.info("Step 3: Diagnostic - Analyzing root causes")
        try:
            diag_query = "Why did this happen?"
            diag_out = self.diagnostic.explain(diag_query)
            diag_metrics = evaluate_response(diag_query, diag_out,"Primary cause and secondary contributors")
            report["steps"].append({"agent":"Diagnostic","output":diag_out,"metrics":diag_metrics,"step":3})
            log.info("Step 3 completed successfully")
        except Exception as e:
            log.error(f"Step 3 failed: {str(e)}")
            report["steps"].append({"agent":"Diagnostic","output":str(e),"metrics":{"failed":True},"step":3})

        # ---------------- STEP 4: SIMULATION ----------------
        log.info("Step 4: Simulation - Running scenario analysis")
        try:
            sim_query = "Simulate a 10% price increase on electronics"
            sim_out = self.simulation.simulate(sim_query)
            sim_metrics = evaluate_response(sim_query, sim_out,"Assumptions + projected impact")
            report["steps"].append({"agent":"Simulation","output":sim_out,"metrics":sim_metrics,"step":4})
            log.info("Step 4 completed successfully")
        except Exception as e:
            log.error(f"Step 4 failed: {str(e)}")
            report["steps"].append({"agent":"Simulation","output":str(e),"metrics":{"failed":True},"step":4})

        # ---------------- STEP 5: INSIGHT ----------------
        log.info("Step 5: Insight - Generating actionable insights")
        try:
            insight_query = "Based on KPI and simulation, give top actions"
            insight_out = self.insight.generate_insight(insight_query)
            insight_metrics = evaluate_response(insight_query, insight_out,"pattern, reason, impact, action")
            report["steps"].append({"agent":"Insight","output":insight_out,"metrics":insight_metrics,"step":5})
            log.info("Step 5 completed successfully")
        except Exception as e:
            log.error(f"Step 5 failed: {str(e)}")
            report["steps"].append({"agent":"Insight","output":str(e),"metrics":{"failed":True},"step":5})

        # ---------------- STEP 6: DASHBOARD ----------------
        log.info("Step 6: Dashboard - Rendering visualization")
        try:
            dash_out = self.dashboard.render("sales_overview")
            dash_metrics = evaluate_response("dashboard_render", dash_out,"KPI_NAME: VALUE TREND: up/down CONFIDENCE")
            report["steps"].append({"agent":"Dashboard","output":dash_out,"metrics":dash_metrics,"step":6})
            log.info("Step 6 completed successfully")
        except Exception as e:
            log.error(f"Step 6 failed: {str(e)}")
            report["steps"].append({"agent":"Dashboard","output":str(e),"metrics":{"failed":True},"step":6})

        # ---------------- STEP 7: MEMORY RETRIEVAL ----------------
        log.info("Step 7: Memory - Retrieving stored context")
        try:
            mem_out = self.memory.retrieve("last_kpi")
            report["steps"].append({"agent":"Memory","output":mem_out,"metrics":{"note":"memory retrieval"},"step":7})
            log.info("Step 7 completed successfully")
        except Exception as e:
            log.error(f"Step 7 failed: {str(e)}")
            report["steps"].append({"agent":"Memory","output":str(e),"metrics":{"failed":True},"step":7})

        # ---------------- FINAL SUMMARY ----------------
        passed = sum(1 for s in report["steps"] if not (s.get("metrics") and s["metrics"].get("failed")))
        report["summary"] = {
            "total": len(report["steps"]),
            "passed": passed,
            "pass_rate": passed / max(1, len(report["steps"]))
        }
        
        log.info(f"E2E conversation flow completed. Summary: {passed}/{len(report['steps'])} steps passed ({report['summary']['pass_rate']:.2%})")
        return report
