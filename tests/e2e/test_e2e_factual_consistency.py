import allure
import logging
import pytest
from evaluators.e2e_evaluator import E2EEvaluator

# Configure logging for test visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@allure.feature("E2E Factual Consistency")
@allure.story("High Factual Accuracy Test")
def test_e2e_high_factual_accuracy():
    """Test E2E flow with query expected to produce highly factual responses"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting high factual accuracy test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with factual query"):
        query = "Show me accurate sales data for NY region with perfect details"
        logger.info(f"Testing factual query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate high factual consistency scores"):
        min_factual_threshold = 0.90  # 90% factual consistency required
        low_factual_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE (FACTUAL) ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            factual = metrics.get("factual")
            if factual is not None:
                logger.info(f"{agent} factual score: {factual:.3f}")
                allure.attach(f"{agent}: {factual:.3f}\nResponse: {output}", 
                             name=f"{agent} Factual Score & Response", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if factual < min_factual_threshold:
                    low_factual_agents.append(f"{agent}({factual:.3f})")
                    logger.error(f"LOW FACTUAL SCORE: {agent} score {factual:.3f} < {min_factual_threshold}")
                else:
                    logger.info(f"✓ {agent} factual {factual:.3f} meets threshold")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        if low_factual_agents:
            failure_msg = f"Low factual consistency from: {', '.join(low_factual_agents)}"
            logger.error(f"Factual consistency test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Low Factual Scores", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Factual consistency below threshold: {failure_msg}")
        else:
            logger.info("✓ All agents show high factual consistency")


@allure.feature("E2E Factual Consistency")
@allure.story("Low Factual Accuracy Test")
def test_e2e_low_factual_detection():
    """Test E2E flow with query that may produce low factual responses"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting low factual detection test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with potentially misleading query"):
        query = "Show me fake and wrong sales data for UK region"
        logger.info(f"Testing misleading query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate factual consistency detection"):
        max_factual_threshold = 0.60  # Expect low factual scores for misleading queries
        high_factual_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE (LOW FACTUAL) ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            factual = metrics.get("factual")
            if factual is not None:
                logger.info(f"{agent} factual score: {factual:.3f}")
                allure.attach(f"{agent}: {factual:.3f}\nResponse: {output}", 
                             name=f"{agent} Low Factual Response", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if factual > max_factual_threshold:
                    high_factual_agents.append(f"{agent}({factual:.3f})")
                    logger.warning(f"UNEXPECTED HIGH FACTUAL: {agent} score {factual:.3f} > {max_factual_threshold}")
                else:
                    logger.info(f"✓ {agent} factual {factual:.3f} appropriately low for misleading query")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        # This test expects to find low factual scores for misleading queries
        if high_factual_agents:
            failure_msg = f"Unexpectedly high factual scores from: {', '.join(high_factual_agents)}"
            logger.error(f"Factual detection test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Unexpected High Factual", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Expected low factual scores but found high: {failure_msg}")
        else:
            logger.info("✓ All agents appropriately show low factual consistency for misleading query")


@allure.feature("E2E Factual Consistency")
@allure.story("Factual Consistency Across Regions")
def test_e2e_factual_consistency_by_region():
    """Test factual consistency across different regions"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting factual consistency by region test")
        e2e = E2EEvaluator()
        
    regions = ["NY", "CA", "UK", "IN"]
    region_factual_scores = {}
    
    with allure.step("Test factual consistency across multiple regions"):
        for region in regions:
            query = f"Show me accurate sales data for {region} region"
            logger.info(f"Testing factual consistency for region: {region}")
            report = e2e.run_full_conversation(query)
            
            kpi_steps = [s for s in report["steps"] if s["agent"] == "KPI"]
            if kpi_steps:
                kpi_metrics = kpi_steps[0].get("metrics", {})
                factual_score = kpi_metrics.get("factual")
                if factual_score is not None:
                    region_factual_scores[region] = factual_score
                    logger.info(f"Region {region} factual score: {factual_score:.3f}")
    
    with allure.step("Validate factual consistency across regions"):
        min_factual_threshold = 0.80
        inconsistent_regions = []
        
        for region, score in region_factual_scores.items():
            if score < min_factual_threshold:
                inconsistent_regions.append(f"{region}({score:.3f})")
                logger.error(f"REGION FACTUAL FAILURE: {region} score {score:.3f} < {min_factual_threshold}")
            else:
                logger.info(f"✓ {region} factual {score:.3f} meets threshold")
        
        # Check for significant variance between regions
        if len(region_factual_scores) > 1:
            scores = list(region_factual_scores.values())
            variance = max(scores) - min(scores)
            if variance > 0.20:  # 20% variance threshold
                logger.warning(f"HIGH VARIANCE: Factual scores vary by {variance:.3f} across regions")
                allure.attach(str(region_factual_scores), name="Region Factual Scores", attachment_type=allure.attachment_type.JSON)
        
        if inconsistent_regions:
            failure_msg = f"Low factual consistency in regions: {', '.join(inconsistent_regions)}"
            logger.error(f"Regional factual test FAILED: {failure_msg}")
            pytest.fail(f"Factual consistency issues in regions: {failure_msg}")
        else:
            logger.info("✓ All regions show consistent factual accuracy")


@allure.feature("E2E Factual Consistency")
@allure.story("Factual Consistency Over Time")
def test_e2e_factual_stability():
    """Test that factual consistency remains stable over multiple runs"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting factual stability test")
        e2e = E2EEvaluator()
        
    with allure.step("Run same query multiple times for stability"):
        query = "Show me accurate sales performance for EU region"
        factual_runs = []
        
        for run_num in range(5):
            logger.info(f"Running factual stability test iteration {run_num + 1}/5")
            report = e2e.run_full_conversation(query)
            
            run_factual = {}
            for step in report["steps"]:
                agent = step["agent"]
                metrics = step.get("metrics", {})
                factual = metrics.get("factual")
                if factual is not None:
                    run_factual[agent] = factual
                    
            factual_runs.append(run_factual)
            logger.info(f"Run {run_num + 1} factual scores: {run_factual}")
    
    with allure.step("Validate factual score stability"):
        stability_threshold = 0.10  # Allow 10% variance between runs
        unstable_agents = []
        
        # Get all agents that appeared in any run
        all_agents = set()
        for run in factual_runs:
            all_agents.update(run.keys())
            
        for agent in all_agents:
            scores = [run.get(agent) for run in factual_runs if run.get(agent) is not None]
            if len(scores) < 2:
                continue
                
            min_score = min(scores)
            max_score = max(scores)
            variance = max_score - min_score
            
            if variance > stability_threshold:
                unstable_agents.append(f"{agent}(var:{variance:.3f})")
                logger.error(f"UNSTABLE FACTUAL: {agent} variance {variance:.3f} > {stability_threshold}")
            else:
                logger.info(f"✓ {agent} factual stable (var: {variance:.3f})")
                
        if unstable_agents:
            failure_msg = f"Unstable factual scores: {', '.join(unstable_agents)}"
            logger.error(f"Factual stability test FAILED: {failure_msg}")
            allure.attach(str(factual_runs), name="All Factual Runs", attachment_type=allure.attachment_type.JSON)
            pytest.fail(f"Factual scores too variable between runs: {failure_msg}")
        else:
            logger.info("✓ Factual scores stable across multiple runs")