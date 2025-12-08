
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

DEEPEVAL_THRESHOLDS = {
    "kpi_factual": 0.7,
    "kpi_hallucination": 0.25,
    "generic_factual": 0.6,
    "generic_hallucination": 0.35
}
