import allure
import logging
import pytest
from evaluators.e2e_evaluator import E2EEvaluator

# Configure logging for test visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@allure.feature("E2E Relevance Metrics")
@allure.story("High Relevance Test")
def test_e2e_high_relevance():
    """Test E2E flow with query expected to produce highly relevant responses"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting high relevance test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with specific, relevant query"):
        query = "Show me detailed sales metrics for NY region with growth analysis"
        logger.info(f"Testing relevant query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate high relevance scores"):
        min_relevance_threshold = 0.85  # 85% relevance required
        low_relevance_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            relevance = metrics.get("relevance")
            if relevance is not None:
                logger.info(f"{agent} relevance score: {relevance:.3f}")
                allure.attach(f"{agent}: {relevance:.3f}\nResponse: {output}", 
                             name=f"{agent} Relevance Score & Response", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if relevance < min_relevance_threshold:
                    low_relevance_agents.append(f"{agent}({relevance:.3f})")
                    logger.error(f"LOW RELEVANCE: {agent} score {relevance:.3f} < {min_relevance_threshold}")
                else:
                    logger.info(f"✓ {agent} relevance {relevance:.3f} meets threshold")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        if low_relevance_agents:
            failure_msg = f"Low relevance from: {', '.join(low_relevance_agents)}"
            logger.error(f"Relevance test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Low Relevance Scores", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Relevance below threshold: {failure_msg}")
        else:
            logger.info("✓ All agents show high relevance")


@allure.feature("E2E Relevance Metrics")
@allure.story("Off-Topic Query Test")
def test_e2e_off_topic_relevance():
    """Test E2E flow with off-topic query to detect relevance issues"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting off-topic relevance test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with off-topic query"):
        query = "What is the weather like today and how to cook pasta?"
        logger.info(f"Testing off-topic query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate relevance detection for off-topic content"):
        max_relevance_threshold = 0.40  # Expect low relevance for off-topic queries
        high_relevance_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE (OFF-TOPIC) ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            relevance = metrics.get("relevance")
            if relevance is not None:
                logger.info(f"{agent} relevance score: {relevance:.3f}")
                allure.attach(f"{agent}: {relevance:.3f}\nResponse: {output}", 
                             name=f"{agent} Off-Topic Response & Score", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if relevance > max_relevance_threshold:
                    high_relevance_agents.append(f"{agent}({relevance:.3f})")
                    logger.warning(f"UNEXPECTED HIGH RELEVANCE: {agent} score {relevance:.3f} > {max_relevance_threshold}")
                else:
                    logger.info(f"✓ {agent} relevance {relevance:.3f} appropriately low for off-topic query")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        # This test expects to find low relevance scores for off-topic queries
        if high_relevance_agents:
            failure_msg = f"Unexpectedly high relevance from: {', '.join(high_relevance_agents)}"
            logger.error(f"Off-topic relevance test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Unexpected High Relevance", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Expected low relevance but found high: {failure_msg}")
        else:
            logger.info("✓ All agents appropriately show low relevance for off-topic query")


@allure.feature("E2E Relevance Metrics")
@allure.story("Partially Relevant Query Test")
def test_e2e_partially_relevant():
    """Test E2E flow with partially relevant query"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting partially relevant test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with partially relevant query"):
        query = "Show me CA sales and also tell me about the history of California"
        logger.info(f"Testing partially relevant query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate partial relevance handling"):
        min_relevance_threshold = 0.60  # Moderate relevance expected
        max_relevance_threshold = 0.85  # Not too high due to mixed content
        relevance_issues = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE (PARTIAL) ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            relevance = metrics.get("relevance")
            if relevance is not None:
                logger.info(f"{agent} relevance score: {relevance:.3f}")
                allure.attach(f"{agent}: {relevance:.3f}\nResponse: {output}", 
                             name=f"{agent} Partial Relevance Response", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if relevance < min_relevance_threshold:
                    relevance_issues.append(f"{agent}(too_low:{relevance:.3f})")
                    logger.error(f"TOO LOW RELEVANCE: {agent} score {relevance:.3f} < {min_relevance_threshold}")
                elif relevance > max_relevance_threshold:
                    relevance_issues.append(f"{agent}(too_high:{relevance:.3f})")
                    logger.warning(f"TOO HIGH RELEVANCE: {agent} score {relevance:.3f} > {max_relevance_threshold}")
                else:
                    logger.info(f"✓ {agent} relevance {relevance:.3f} in expected range")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        if relevance_issues:
            failure_msg = f"Relevance issues: {', '.join(relevance_issues)}"
            logger.error(f"Partial relevance test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Relevance Issues", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Relevance not in expected range for mixed query: {failure_msg}")
        else:
            logger.info("✓ All agents show appropriate relevance for mixed query")


@allure.feature("E2E Relevance Metrics")
@allure.story("Agent-Specific Relevance Test")
def test_e2e_agent_specific_relevance():
    """Test that different agents show appropriate relevance for their specific roles"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting agent-specific relevance test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation targeting specific agent capabilities"):
        query = "Show me UK sales KPIs and create a dashboard visualization"
        logger.info(f"Testing agent-specific query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate agent-specific relevance expectations"):
        # Different relevance expectations for different agents
        agent_expectations = {
            "KPI": {"min": 0.90, "reason": "KPI agent should be highly relevant for KPI queries"},
            "Dashboard": {"min": 0.85, "reason": "Dashboard agent should be relevant for visualization"},
            "Diagnostic": {"min": 0.60, "reason": "Diagnostic less relevant for direct KPI queries"},
            "Simulation": {"min": 0.50, "reason": "Simulation not directly relevant to KPI display"}
        }
        
        relevance_failures = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            output = step.get("output", "")
            
            # Log agent response for analysis
            logger.info(f"\n=== {agent} AGENT RESPONSE (AGENT-SPECIFIC) ===")
            logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
            logger.info(f"Full response length: {len(str(output))} characters")
            
            if metrics.get("failed") or "note" in metrics:
                logger.info(f"{agent} step failed or is note-only")
                continue
                
            relevance = metrics.get("relevance")
            if relevance is not None and agent in agent_expectations:
                expected_min = agent_expectations[agent]["min"]
                reason = agent_expectations[agent]["reason"]
                
                logger.info(f"{agent} relevance score: {relevance:.3f} (expected ≥{expected_min})")
                allure.attach(f"{agent}: {relevance:.3f}\nExpected: ≥{expected_min}\nReason: {reason}\nResponse: {output}", 
                             name=f"{agent} Agent-Specific Analysis", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if relevance < expected_min:
                    relevance_failures.append(f"{agent}({relevance:.3f}<{expected_min})")
                    logger.error(f"AGENT RELEVANCE FAILURE: {agent} score {relevance:.3f} < {expected_min} - {reason}")
                else:
                    logger.info(f"✓ {agent} relevance {relevance:.3f} meets expectation - {reason}")
            logger.info(f"=== END {agent} RESPONSE ===\n")
        
        if relevance_failures:
            failure_msg = f"Agent relevance failures: {', '.join(relevance_failures)}"
            logger.error(f"Agent-specific relevance test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Agent Relevance Failures", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Agents not showing expected relevance: {failure_msg}")
        else:
            logger.info("✓ All agents show appropriate relevance for their roles")


@allure.feature("E2E Relevance Metrics")
@allure.story("Relevance Consistency Test")
def test_e2e_relevance_consistency():
    """Test that relevance scores are consistent across similar queries"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting relevance consistency test")
        e2e = E2EEvaluator()
        
    with allure.step("Test relevance consistency across similar queries"):
        similar_queries = [
            "Show me sales data for NY region",
            "Display NY sales information",
            "What are the NY sales figures?"
        ]
        
        query_relevance_scores = {}
        
        for i, query in enumerate(similar_queries):
            logger.info(f"Testing query {i+1}: {query}")
            report = e2e.run_full_conversation(query)
            
            agent_relevance = {}
            for step in report["steps"]:
                agent = step["agent"]
                metrics = step.get("metrics", {})
                output = step.get("output", "")
                
                # Log agent response for each query
                logger.info(f"\n=== {agent} RESPONSE FOR QUERY {i+1} ===")
                logger.info(f"Query: {query}")
                logger.info(f"Response: {output[:200]}{'...' if len(str(output)) > 200 else ''}")
                logger.info(f"Full response length: {len(str(output))} characters")
                
                relevance = metrics.get("relevance")
                if relevance is not None:
                    agent_relevance[agent] = relevance
                    logger.info(f"{agent} relevance score: {relevance:.3f}")
                    
                logger.info(f"=== END {agent} RESPONSE ===\n")
                    
            query_relevance_scores[f"query_{i+1}"] = agent_relevance
            logger.info(f"Query {i+1} relevance scores: {agent_relevance}")
    
    with allure.step("Validate relevance consistency across similar queries"):
        consistency_threshold = 0.15  # Allow 15% variance for similar queries
        inconsistent_agents = []
        
        # Get all agents that appeared in any query
        all_agents = set()
        for scores in query_relevance_scores.values():
            all_agents.update(scores.keys())
            
        for agent in all_agents:
            scores = []
            for query_scores in query_relevance_scores.values():
                if agent in query_scores:
                    scores.append(query_scores[agent])
                    
            if len(scores) < 2:
                continue
                
            min_score = min(scores)
            max_score = max(scores)
            variance = max_score - min_score
            
            if variance > consistency_threshold:
                inconsistent_agents.append(f"{agent}(var:{variance:.3f})")
                logger.error(f"INCONSISTENT RELEVANCE: {agent} variance {variance:.3f} > {consistency_threshold}")
            else:
                logger.info(f"✓ {agent} relevance consistent across similar queries (var: {variance:.3f})")
                
        if inconsistent_agents:
            failure_msg = f"Inconsistent relevance across similar queries: {', '.join(inconsistent_agents)}"
            logger.error(f"Relevance consistency test FAILED: {failure_msg}")
            allure.attach(str(query_relevance_scores), name="All Query Relevance Scores", attachment_type=allure.attachment_type.JSON)
            pytest.fail(f"Relevance varies too much for similar queries: {failure_msg}")
        else:
            logger.info("✓ Relevance scores consistent across similar queries")