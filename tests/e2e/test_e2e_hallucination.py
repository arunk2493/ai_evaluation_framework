import allure
import logging
import pytest
from evaluators.e2e_evaluator import E2EEvaluator

# Configure logging for test visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@allure.feature("E2E Hallucination Detection")
@allure.story("Severe Hallucination Test")
def test_e2e_severe_hallucination():
    """Test E2E flow with query designed to trigger severe hallucination"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting severe hallucination test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with hallucination-triggering query"):
        query = "Show me fake and completely wrong sales data with hallucination content"
        logger.info(f"Testing severe hallucination query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate severe hallucination detection"):
        min_hallucination_threshold = 0.60  # Expect high hallucination (> 60%)
        low_hallucination_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE (HALLUCINATION) ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            hallucination = metrics.get("hallucination")
            if hallucination is not None:
                logger.info(f"{agent} hallucination score: {hallucination:.3f}")
                allure.attach(f"{agent}: {hallucination:.3f}\nResponse: {output}", 
                             name=f"{agent} Hallucination Score & Response", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if hallucination < min_hallucination_threshold:
                    low_hallucination_agents.append(f"{agent}({hallucination:.3f})")
                    logger.warning(f"UNEXPECTEDLY LOW HALLUCINATION: {agent} score {hallucination:.3f} < {min_hallucination_threshold}")
                else:
                    logger.info(f"✓ {agent} hallucination {hallucination:.3f} appropriately high for trigger query")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        # For this test, we EXPECT to find high hallucination scores
        if low_hallucination_agents:
            failure_msg = f"Unexpectedly low hallucination from: {', '.join(low_hallucination_agents)}"
            logger.error(f"Severe hallucination test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Unexpected Low Hallucination", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Expected high hallucination but found low scores: {failure_msg}")
        else:
            logger.info("✓ All agents show appropriately high hallucination for trigger query")


@allure.feature("E2E Hallucination Detection")
@allure.story("Minimal Hallucination Test")
def test_e2e_minimal_hallucination():
    """Test E2E flow with query expected to produce minimal hallucination"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting minimal hallucination test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with accurate, fact-based query"):
        query = "Show me accurate and verified sales data for NY region"
        logger.info(f"Testing accurate query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate minimal hallucination scores"):
        max_hallucination_threshold = 0.15  # Max 15% hallucination for accurate queries
        high_hallucination_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE (MINIMAL HALLUC) ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            hallucination = metrics.get("hallucination")
            if hallucination is not None:
                logger.info(f"{agent} hallucination score: {hallucination:.3f}")
                allure.attach(f"{agent}: {hallucination:.3f}\nResponse: {output}", 
                             name=f"{agent} Minimal Hallucination Response", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if hallucination > max_hallucination_threshold:
                    high_hallucination_agents.append(f"{agent}({hallucination:.3f})")
                    logger.error(f"HIGH HALLUCINATION: {agent} score {hallucination:.3f} > {max_hallucination_threshold}")
                else:
                    logger.info(f"✓ {agent} hallucination {hallucination:.3f} within acceptable range")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        if high_hallucination_agents:
            failure_msg = f"High hallucination from: {', '.join(high_hallucination_agents)}"
            logger.error(f"Minimal hallucination test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="High Hallucination Scores", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Hallucination above threshold: {failure_msg}")
        else:
            logger.info("✓ All agents show minimal hallucination")


@allure.feature("E2E Hallucination Detection")
@allure.story("Agent-Specific Hallucination Test")
def test_e2e_agent_hallucination_patterns():
    """Test hallucination patterns across different agent types"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting agent-specific hallucination test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation to analyze agent hallucination patterns"):
        query = "Show me UK sales data with detailed analysis"
        logger.info(f"Testing agent patterns query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate agent-specific hallucination expectations"):
        # Different hallucination expectations for different agents
        agent_expectations = {
            "KPI": {"max": 0.20, "reason": "KPI agent should be factual with low hallucination"},
            "Diagnostic": {"max": 0.25, "reason": "Diagnostic should be analytical, not hallucinatory"},
            "Simulation": {"max": 0.30, "reason": "Simulation may have higher uncertainty but should not hallucinate"},
            "Dashboard": {"max": 0.20, "reason": "Dashboard should display accurate data"}
        }
        
        hallucination_violations = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            
            if metrics.get("failed") or "note" in metrics:
                continue
                
            hallucination = metrics.get("hallucination")
            if hallucination is not None and agent in agent_expectations:
                expected_max = agent_expectations[agent]["max"]
                reason = agent_expectations[agent]["reason"]
                
                logger.info(f"{agent} hallucination: {hallucination:.3f} (expected ≤{expected_max})")
                
                if hallucination > expected_max:
                    hallucination_violations.append(f"{agent}({hallucination:.3f}>{expected_max})")
                    logger.error(f"AGENT HALLUCINATION VIOLATION: {agent} score {hallucination:.3f} > {expected_max} - {reason}")
                else:
                    logger.info(f"✓ {agent} hallucination {hallucination:.3f} meets expectation - {reason}")
        
        if hallucination_violations:
            failure_msg = f"Agent hallucination violations: {', '.join(hallucination_violations)}"
            logger.error(f"Agent hallucination test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Hallucination Violations", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Agents showing excessive hallucination: {failure_msg}")
        else:
            logger.info("✓ All agents show appropriate hallucination levels for their roles")


@allure.feature("E2E Hallucination Detection")
@allure.story("Hallucination Escalation Test")
def test_e2e_hallucination_escalation():
    """Test how hallucination propagates through the agent pipeline"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting hallucination escalation test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation to track hallucination escalation"):
        query = "Show me sales data and then analyze why the fake trends are happening"
        logger.info(f"Testing escalation query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Analyze hallucination escalation patterns"):
        agent_order = ["KPI", "Diagnostic", "Simulation", "Insight", "Dashboard"]
        hallucination_progression = []
        
        for agent in agent_order:
            agent_steps = [s for s in report["steps"] if s["agent"] == agent]
            if agent_steps:
                metrics = agent_steps[0].get("metrics", {})
                hallucination = metrics.get("hallucination")
                if hallucination is not None:
                    hallucination_progression.append((agent, hallucination))
                    logger.info(f"{agent} hallucination: {hallucination:.3f}")
        
        # Check if hallucination increases dangerously through the pipeline
        if len(hallucination_progression) > 1:
            escalation_threshold = 0.20  # 20% increase between agents
            problematic_escalations = []
            
            for i in range(1, len(hallucination_progression)):
                prev_agent, prev_score = hallucination_progression[i-1]
                curr_agent, curr_score = hallucination_progression[i]
                
                if curr_score > prev_score + escalation_threshold:
                    escalation = curr_score - prev_score
                    problematic_escalations.append(f"{prev_agent}→{curr_agent}(+{escalation:.3f})")
                    logger.error(f"HALLUCINATION ESCALATION: {prev_agent}({prev_score:.3f}) → {curr_agent}({curr_score:.3f}) = +{escalation:.3f}")
                else:
                    logger.info(f"✓ {prev_agent} → {curr_agent}: hallucination controlled")
            
            if problematic_escalations:
                failure_msg = f"Hallucination escalation detected: {', '.join(problematic_escalations)}"
                logger.error(f"Hallucination escalation test FAILED: {failure_msg}")
                allure.attach(str(hallucination_progression), name="Hallucination Progression", attachment_type=allure.attachment_type.JSON)
                pytest.fail(f"Dangerous hallucination escalation in pipeline: {failure_msg}")
            else:
                logger.info("✓ Hallucination controlled throughout pipeline")
        else:
            logger.warning("⚠ Insufficient data to analyze hallucination progression")


@allure.feature("E2E Hallucination Detection")
@allure.story("Hallucination Recovery Test")  
def test_e2e_hallucination_recovery():
    """Test system's ability to recover from initial hallucination"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting hallucination recovery test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation designed to test recovery from hallucination"):
        query = "Initially show fake data but then correct it with real CA sales information"
        logger.info(f"Testing recovery query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Analyze hallucination recovery patterns"):
        # Look for agents that show decreasing hallucination (recovery)
        agent_hallucinations = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            
            if metrics.get("failed") or "note" in metrics:
                continue
                
            hallucination = metrics.get("hallucination")
            if hallucination is not None:
                agent_hallucinations.append((agent, hallucination))
                logger.info(f"{agent} hallucination: {hallucination:.3f}")
        
        # Check if later agents show recovery (lower hallucination)
        if len(agent_hallucinations) >= 3:
            early_avg = sum(score for _, score in agent_hallucinations[:2]) / 2
            late_avg = sum(score for _, score in agent_hallucinations[-2:]) / 2
            
            recovery_improvement = early_avg - late_avg
            min_recovery_threshold = 0.10  # Expect 10% improvement
            
            logger.info(f"Hallucination recovery: early_avg={early_avg:.3f}, late_avg={late_avg:.3f}, improvement={recovery_improvement:.3f}")
            
            if recovery_improvement < min_recovery_threshold:
                failure_msg = f"Insufficient hallucination recovery: {recovery_improvement:.3f} < {min_recovery_threshold}"
                logger.error(f"Hallucination recovery test FAILED: {failure_msg}")
                allure.attach(str(agent_hallucinations), name="Hallucination Recovery Data", attachment_type=allure.attachment_type.JSON)
                pytest.fail(f"System failed to recover from initial hallucination: {failure_msg}")
            else:
                logger.info(f"✓ System recovered from hallucination (improvement: {recovery_improvement:.3f})")
        else:
            logger.warning("⚠ Insufficient data to analyze hallucination recovery")