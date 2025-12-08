
from deepeval.metrics import FactualConsistencyMetric, RelevanceMetric, HallucinationMetric, AnswerCorrectnessMetric

factual_metric = FactualConsistencyMetric()
relevance_metric = RelevanceMetric()
hallucination_metric = HallucinationMetric()
correctness_metric = AnswerCorrectnessMetric()

def evaluate_response(query, llm_output, ground):
    return {
        "factual": factual_metric.measure(query, llm_output, ground),
        "relevance": relevance_metric.measure(query, llm_output, ground),
        "hallucination": hallucination_metric.measure(query, llm_output, ground),
        "correctness": correctness_metric.measure(query, llm_output, ground)
    }
