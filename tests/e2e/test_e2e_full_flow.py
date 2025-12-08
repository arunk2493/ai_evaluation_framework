
import allure
from evaluators.e2e_evaluator import E2EEvaluator

def test_e2e_full_flow_basic():
    e2e = E2EEvaluator()
    report = e2e.run_full_conversation("Show me NY sales and explain why it dropped.")
    assert "summary" in report
    assert len(report["steps"]) > 0
