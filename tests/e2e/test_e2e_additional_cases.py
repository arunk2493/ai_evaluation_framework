
import allure
from evaluators.e2e_evaluator import E2EEvaluator

def test_multi_region():
    e2e = E2EEvaluator()
    for q in ["Show me IN sales","Show me UK sales"]:
        report = e2e.run_full_conversation(q)
        assert report["summary"]["total"] >= 1
