import allure
import logging
import pytest
from evaluators.e2e_evaluator import E2EEvaluator

# Configure logging for test visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@allure.feature("E2E Correctness Metrics")
@allure.story("High Correctness Test")
def test_e2e_high_correctness():
    """Test E2E flow with query expected to produce highly correct responses"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting high correctness test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with query requiring accurate responses"):
        query = "Show me accurate and precise sales data for CA region"
        logger.info(f"Testing correctness query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate high correctness scores"):
        min_correctness_threshold = 0.88  # 88% correctness required
        low_correctness_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE (CORRECTNESS) ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            correctness = metrics.get("correctness")
            if correctness is not None:
                logger.info(f"{agent} correctness score: {correctness:.3f}")
                allure.attach(f"{agent}: {correctness:.3f}\nResponse: {output}", 
                             name=f"{agent} Correctness Score & Response", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if correctness < min_correctness_threshold:
                    low_correctness_agents.append(f"{agent}({correctness:.3f})")
                    logger.error(f"LOW CORRECTNESS: {agent} score {correctness:.3f} < {min_correctness_threshold}")
                else:
                    logger.info(f"✓ {agent} correctness {correctness:.3f} meets threshold")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        if low_correctness_agents:
            failure_msg = f"Low correctness from: {', '.join(low_correctness_agents)}"
            logger.error(f"Correctness test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Low Correctness Scores", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Correctness below threshold: {failure_msg}")
        else:
            logger.info("✓ All agents show high correctness")


@allure.feature("E2E Correctness Metrics")
@allure.story("Error-Prone Query Test")
def test_e2e_error_prone_correctness():
    """Test E2E flow with query that may lead to incorrect responses"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting error-prone correctness test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with potentially misleading query"):
        query = "Show me wrong and incorrect sales data for UK region"
        logger.info(f"Testing error-prone query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate correctness detection for error-prone content"):
        max_correctness_threshold = 0.50  # Expect low correctness for misleading queries
        high_correctness_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            
            if metrics.get("failed") or "note" in metrics:
                continue
                
            correctness = metrics.get("correctness")
            if correctness is not None:
                logger.info(f"{agent} correctness score: {correctness:.3f}")
                
                if correctness > max_correctness_threshold:
                    high_correctness_agents.append(f"{agent}({correctness:.3f})")
                    logger.warning(f"UNEXPECTED HIGH CORRECTNESS: {agent} score {correctness:.3f} > {max_correctness_threshold}")
                else:
                    logger.info(f"✓ {agent} correctness {correctness:.3f} appropriately low for misleading query")
        
        if high_correctness_agents:
            failure_msg = f"Unexpectedly high correctness from: {', '.join(high_correctness_agents)}"
            logger.error(f"Error-prone correctness test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Unexpected High Correctness", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Expected low correctness but found high: {failure_msg}")
        else:
            logger.info("✓ All agents appropriately show low correctness for misleading query")


@allure.feature("E2E Correctness Metrics")
@allure.story("Mathematical Correctness Test")
def test_e2e_mathematical_correctness():
    """Test E2E flow with queries requiring mathematical accuracy"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting mathematical correctness test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation requiring mathematical calculations"):
        query = "Calculate the growth percentage for NY sales and show precise numbers"
        logger.info(f"Testing mathematical query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate mathematical correctness"):
        min_mathematical_threshold = 0.85  # High threshold for mathematical accuracy
        math_errors = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            
            if metrics.get("failed") or "note" in metrics:
                continue
                
            correctness = metrics.get("correctness")
            if correctness is not None:
                logger.info(f"{agent} mathematical correctness: {correctness:.3f}")
                
                # KPI and Diagnostic agents should be especially accurate for calculations
                if agent in ["KPI", "Diagnostic"]:
                    if correctness < min_mathematical_threshold:
                        math_errors.append(f"{agent}({correctness:.3f})")
                        logger.error(f"MATH CORRECTNESS ERROR: {agent} score {correctness:.3f} < {min_mathematical_threshold}")
                    else:
                        logger.info(f"✓ {agent} mathematical correctness {correctness:.3f} meets threshold")
        
        if math_errors:
            failure_msg = f"Mathematical correctness errors: {', '.join(math_errors)}"
            logger.error(f"Mathematical correctness test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Mathematical Errors", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Mathematical correctness below threshold: {failure_msg}")
        else:
            logger.info("✓ All agents show appropriate mathematical correctness")


@allure.feature("E2E Correctness Metrics")
@allure.story("Data Format Correctness Test")
def test_e2e_data_format_correctness():
    """Test E2E flow with queries requiring specific data formats"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting data format correctness test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation requiring specific data formats"):
        query = "Show me EU sales data in JSON format with proper structure"
        logger.info(f"Testing data format query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate data format correctness"):
        min_format_threshold = 0.80  # High threshold for format correctness
        format_errors = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            if metrics.get("failed") or "note" in metrics:
                continue
                
            correctness = metrics.get("correctness")
            if correctness is not None:
                logger.info(f"{agent} format correctness: {correctness:.3f}")
                
                # Dashboard agent should be especially good at formatting
                if agent == "Dashboard":
                    if correctness < min_format_threshold:
                        format_errors.append(f"{agent}({correctness:.3f})")
                        logger.error(f"FORMAT CORRECTNESS ERROR: {agent} score {correctness:.3f} < {min_format_threshold}")
                    else:
                        logger.info(f"✓ {agent} format correctness {correctness:.3f} meets threshold")
                
                # Check if output contains structured data indicators
                if isinstance(output, str):
                    has_structure = any(indicator in output.lower() for indicator in ["json", "{", "}", "[", "]", "format"])
                    if has_structure:
                        logger.info(f"✓ {agent} output contains structured data indicators")
                    else:
                        logger.warning(f"⚠ {agent} output may lack structured format")
        
        if format_errors:
            failure_msg = f"Data format correctness errors: {', '.join(format_errors)}"
            logger.error(f"Data format correctness test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Format Errors", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Data format correctness below threshold: {failure_msg}")
        else:
            logger.info("✓ All agents show appropriate data format correctness")


@allure.feature("E2E Correctness Metrics")
@allure.story("Cross-Agent Correctness Validation")
def test_e2e_cross_agent_correctness():
    """Test that agents provide consistent and correct information across the pipeline"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting cross-agent correctness test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation and analyze cross-agent correctness"):
        query = "Show me IN sales data and explain the trends"
        logger.info(f"Testing cross-agent query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate correctness consistency across agents"):
        agent_correctness = {}
        correctness_variance_threshold = 0.20  # Max 20% variance between agents
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            
            if metrics.get("failed") or "note" in metrics:
                continue
                
            correctness = metrics.get("correctness")
            if correctness is not None:
                agent_correctness[agent] = correctness
                logger.info(f"{agent} correctness: {correctness:.3f}")
        
        # Check for significant variance in correctness between agents
        if len(agent_correctness) > 1:
            scores = list(agent_correctness.values())
            min_correctness = min(scores)
            max_correctness = max(scores)
            variance = max_correctness - min_correctness
            
            logger.info(f"Correctness variance across agents: {variance:.3f}")
            
            if variance > correctness_variance_threshold:
                high_agents = [agent for agent, score in agent_correctness.items() if score == max_correctness]
                low_agents = [agent for agent, score in agent_correctness.items() if score == min_correctness]
                
                failure_msg = f"High correctness variance: {variance:.3f} (high: {high_agents}, low: {low_agents})"
                logger.error(f"Cross-agent correctness test FAILED: {failure_msg}")
                allure.attach(str(agent_correctness), name="Agent Correctness Scores", attachment_type=allure.attachment_type.JSON)
                pytest.fail(f"Correctness varies too much between agents: {failure_msg}")
            else:
                logger.info("✓ Correctness consistent across agents")
        
        # Validate minimum correctness threshold
        min_overall_threshold = 0.75
        low_correctness = [f"{agent}({score:.3f})" for agent, score in agent_correctness.items() if score < min_overall_threshold]
        
        if low_correctness:
            failure_msg = f"Agents below minimum correctness: {', '.join(low_correctness)}"
            logger.error(f"Minimum correctness test FAILED: {failure_msg}")
            pytest.fail(f"Some agents below minimum correctness threshold: {failure_msg}")
        else:
            logger.info("✓ All agents meet minimum correctness threshold")