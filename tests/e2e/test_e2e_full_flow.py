
import allure
import logging
import pytest
from evaluators.e2e_evaluator import E2EEvaluator

# Configure logging for test visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@allure.feature("E2E Conversation Flow")
@allure.story("Full Agent Pipeline Test")
def test_e2e_full_flow_basic():
    """Test the complete E2E conversation flow with all agents"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting basic E2E flow test")
        e2e = E2EEvaluator()
        
    with allure.step("Run full conversation for NY sales query"):
        query = "Show me NY sales and explain why it dropped."
        logger.info(f"Testing query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate report structure"):
        logger.info(f"Report generated with {len(report['steps'])} steps")
        assert "summary" in report, "Report should contain summary"
        assert len(report["steps"]) > 0, "Report should have at least one step"
        assert "query" in report, "Report should contain the original query"
        assert report["query"] == query, "Report should preserve the original query"
        
    with allure.step("Validate step structure and numbering"):
        for i, step in enumerate(report["steps"]):
            logger.info(f"Step {step.get('step', i+1)}: {step['agent']} - {'PASSED' if not step.get('metrics', {}).get('failed') else 'FAILED'}")
            assert "agent" in step, f"Step {i} should have agent field"
            assert "output" in step, f"Step {i} should have output field"
            assert "step" in step, f"Step {i} should have step number"
            
    with allure.step("Check summary metrics"):
        summary = report["summary"]
        logger.info(f"Test summary: {summary['passed']}/{summary['total']} passed ({summary['pass_rate']:.2%})")
        allure.attach(str(summary), name="Test Summary", attachment_type=allure.attachment_type.JSON)
        
        assert summary["total"] >= 5, "Should have at least 5 test steps"
        assert summary["passed"] >= 1, "At least one step should pass"
        assert 0 <= summary["pass_rate"] <= 1, "Pass rate should be between 0 and 1"


@allure.feature("E2E Conversation Flow")  
@allure.story("Simple KPI Test")
def test_e2e_simple_kpi():
    """Test a simple KPI-focused conversation"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting simple KPI test")
        e2e = E2EEvaluator()
        
    with allure.step("Run KPI-focused query"):
        query = "What are the UK sales?"
        logger.info(f"Testing KPI query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate KPI step specifically"):
        kpi_steps = [s for s in report["steps"] if s["agent"] == "KPI"]
        assert len(kpi_steps) > 0, "Should have at least one KPI step"
        
        kpi_step = kpi_steps[0] 
        logger.info(f"KPI step region: {kpi_step.get('region')}")
        assert kpi_step.get("region") == "UK", "Should detect UK region from query"
        
    with allure.step("Check basic report validity"):
        assert report["summary"]["total"] > 0, "Should execute some steps"
        logger.info(f"Simple KPI test completed: {report['summary']}")


@allure.feature("E2E Conversation Flow")
@allure.story("Error Handling Test") 
def test_e2e_error_handling():
    """Test E2E flow handles errors gracefully"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting error handling test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with unusual query"):
        query = "Show me sales for MARS region"  # Non-existent region
        logger.info(f"Testing edge case query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate error handling"):
        # Should still complete all steps even with unusual input
        assert "summary" in report, "Report should still be generated"
        assert report["summary"]["total"] > 0, "Should attempt to run steps"
        
        # Check that steps either pass or fail gracefully (no crashes)
        for step in report["steps"]:
            assert "output" in step, "Each step should have output (even if error message)"
            assert "agent" in step, "Each step should identify the agent"
            
        logger.info(f"Error handling test completed: {report['summary']}")


@allure.feature("E2E Conversation Flow")
@allure.story("Negative Test Cases")
def test_e2e_empty_query():
    """Test E2E flow with empty query"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting empty query test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with empty query"):
        query = ""
        logger.info(f"Testing empty query: '{query}'")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate empty query handling"):
        assert "summary" in report, "Report should still be generated for empty query"
        assert report["query"] == query, "Should preserve empty query"
        assert report["summary"]["total"] > 0, "Should still attempt to run steps"
        logger.info(f"Empty query test completed: {report['summary']}")


@allure.feature("E2E Conversation Flow")
@allure.story("Negative Test Cases")
def test_e2e_invalid_region():
    """Test E2E flow with completely invalid region"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting invalid region test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with invalid region"):
        query = "Show me sales for JUPITER and SATURN regions"
        logger.info(f"Testing invalid region query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate invalid region handling"):
        kpi_steps = [s for s in report["steps"] if s["agent"] == "KPI"]
        if kpi_steps:
            kpi_step = kpi_steps[0]
            # Should not detect any valid region
            assert kpi_step.get("region") is None, "Should not detect invalid regions like JUPITER/SATURN"
            logger.info(f"KPI step correctly handled invalid region: {kpi_step.get('region')}")
        
        assert report["summary"]["total"] > 0, "Should still execute steps"
        logger.info(f"Invalid region test completed: {report['summary']}")


@allure.feature("E2E Conversation Flow")
@allure.story("Negative Test Cases")
def test_e2e_special_characters():
    """Test E2E flow with special characters and injection attempts"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting special characters test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with special characters"):
        query = "Show me sales for NY'; DROP TABLE sales; --"
        logger.info(f"Testing special characters query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate special character handling"):
        # Should still complete without crashing
        assert "summary" in report, "Report should be generated despite special characters"
        assert report["summary"]["total"] > 0, "Should execute steps safely"
        
        # Check that NY region is still detected despite injection attempt
        kpi_steps = [s for s in report["steps"] if s["agent"] == "KPI"]
        if kpi_steps:
            kpi_step = kpi_steps[0]
            assert kpi_step.get("region") == "NY", "Should still detect NY region safely"
            logger.info(f"KPI step safely handled injection attempt, detected region: {kpi_step.get('region')}")
        
        logger.info(f"Special characters test completed: {report['summary']}")


@allure.feature("E2E Conversation Flow")
@allure.story("Negative Test Cases")
def test_e2e_very_long_query():
    """Test E2E flow with extremely long query"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting very long query test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with very long query"):
        # Create a very long query
        base_query = "Show me sales for NY region "
        long_query = base_query + "with detailed analysis " * 100  # Very long query
        logger.info(f"Testing very long query of length: {len(long_query)}")
        report = e2e.run_full_conversation(long_query)
        
    with allure.step("Validate long query handling"):
        assert "summary" in report, "Report should be generated for long query"
        assert len(report["query"]) > 1000, "Should preserve long query"
        assert report["summary"]["total"] > 0, "Should execute steps with long input"
        
        # Should still detect NY region
        kpi_steps = [s for s in report["steps"] if s["agent"] == "KPI"]
        if kpi_steps:
            kpi_step = kpi_steps[0]
            assert kpi_step.get("region") == "NY", "Should detect NY region in long query"
            
        logger.info(f"Very long query test completed: {report['summary']}")


@allure.feature("E2E Conversation Flow")
@allure.story("Negative Test Cases")
def test_e2e_unicode_characters():
    """Test E2E flow with unicode and international characters"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting unicode characters test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with unicode characters"):
        query = "显示销售数据 for UK région with émojis 🚀📊"
        logger.info(f"Testing unicode query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate unicode character handling"):
        assert "summary" in report, "Report should handle unicode characters"
        assert report["query"] == query, "Should preserve unicode characters"
        assert report["summary"]["total"] > 0, "Should execute with unicode input"
        
        # Should still detect UK region despite unicode
        kpi_steps = [s for s in report["steps"] if s["agent"] == "KPI"]
        if kpi_steps:
            kpi_step = kpi_steps[0]
            assert kpi_step.get("region") == "UK", "Should detect UK region despite unicode"
            logger.info(f"KPI step handled unicode correctly, detected region: {kpi_step.get('region')}")
            
        logger.info(f"Unicode characters test completed: {report['summary']}")


@allure.feature("E2E Conversation Flow")
@allure.story("Negative Test Cases")
def test_e2e_numeric_only_query():
    """Test E2E flow with numeric-only query"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting numeric-only query test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with numeric query"):
        query = "12345 67890 999.99"
        logger.info(f"Testing numeric query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate numeric query handling"):
        assert "summary" in report, "Report should be generated for numeric query"
        assert report["query"] == query, "Should preserve numeric query"
        assert report["summary"]["total"] > 0, "Should execute with numeric input"
        
        # Should not detect any region from pure numbers
        kpi_steps = [s for s in report["steps"] if s["agent"] == "KPI"]
        if kpi_steps:
            kpi_step = kpi_steps[0]
            assert kpi_step.get("region") is None, "Should not detect region from pure numbers"
            
        logger.info(f"Numeric-only query test completed: {report['summary']}")


@allure.feature("E2E Conversation Flow")
@allure.story("Threshold-based Test Cases")
def test_e2e_metrics_below_threshold():
    """Test E2E flow and validate metrics meet quality thresholds"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting metrics threshold test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation and collect metrics"):
        query = "Show me CA sales performance"
        logger.info(f"Testing query for metrics validation: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Define quality thresholds"):
        # Define minimum acceptable thresholds for each metric
        min_factual_score = 0.90  # 90% factual consistency required
        min_relevance_score = 0.85  # 85% relevance required  
        max_hallucination_score = 0.20  # Max 20% hallucination allowed
        min_correctness_score = 0.88  # 88% correctness required
        min_pass_rate = 0.80  # 80% of steps should pass
        
        logger.info(f"Quality thresholds: factual≥{min_factual_score}, relevance≥{min_relevance_score}, "
                   f"hallucination≤{max_hallucination_score}, correctness≥{min_correctness_score}, "
                   f"pass_rate≥{min_pass_rate}")
        
    with allure.step("Validate metrics against thresholds"):
        failed_validations = []
        
        # Check overall pass rate
        pass_rate = report["summary"]["pass_rate"]
        if pass_rate < min_pass_rate:
            failed_validations.append(f"Pass rate {pass_rate:.2%} below threshold {min_pass_rate:.2%}")
            logger.error(f"THRESHOLD FAILURE: Pass rate {pass_rate:.2%} < {min_pass_rate:.2%}")
        else:
            logger.info(f"✓ Pass rate {pass_rate:.2%} meets threshold {min_pass_rate:.2%}")
            
        # Check individual step metrics
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            
            if metrics.get("failed"):
                failed_validations.append(f"{agent} step failed completely")
                logger.error(f"THRESHOLD FAILURE: {agent} step failed")
                continue
                
            # Skip non-evaluation metrics (like memory notes)
            if "note" in metrics:
                continue
                
            # Validate each metric if present
            factual = metrics.get("factual")
            if factual is not None and factual < min_factual_score:
                failed_validations.append(f"{agent} factual score {factual:.3f} below threshold {min_factual_score}")
                logger.error(f"THRESHOLD FAILURE: {agent} factual {factual:.3f} < {min_factual_score}")
            elif factual is not None:
                logger.info(f"✓ {agent} factual {factual:.3f} meets threshold")
                
            relevance = metrics.get("relevance")  
            if relevance is not None and relevance < min_relevance_score:
                failed_validations.append(f"{agent} relevance score {relevance:.3f} below threshold {min_relevance_score}")
                logger.error(f"THRESHOLD FAILURE: {agent} relevance {relevance:.3f} < {min_relevance_score}")
            elif relevance is not None:
                logger.info(f"✓ {agent} relevance {relevance:.3f} meets threshold")
                
            hallucination = metrics.get("hallucination")
            if hallucination is not None and hallucination > max_hallucination_score:
                failed_validations.append(f"{agent} hallucination score {hallucination:.3f} above threshold {max_hallucination_score}")
                logger.error(f"THRESHOLD FAILURE: {agent} hallucination {hallucination:.3f} > {max_hallucination_score}")
            elif hallucination is not None:
                logger.info(f"✓ {agent} hallucination {hallucination:.3f} meets threshold")
                
            correctness = metrics.get("correctness")
            if correctness is not None and correctness < min_correctness_score:
                failed_validations.append(f"{agent} correctness score {correctness:.3f} below threshold {min_correctness_score}")
                logger.error(f"THRESHOLD FAILURE: {agent} correctness {correctness:.3f} < {min_correctness_score}")
            elif correctness is not None:
                logger.info(f"✓ {agent} correctness {correctness:.3f} meets threshold")
        
    with allure.step("Report threshold validation results"):
        if failed_validations:
            failure_summary = "; ".join(failed_validations)
            logger.error(f"Quality threshold test FAILED: {len(failed_validations)} violations")
            allure.attach(failure_summary, name="Threshold Failures", attachment_type=allure.attachment_type.TEXT)
            
            # This test is designed to fail when metrics are below threshold
            pytest.fail(f"Quality metrics below acceptable thresholds: {failure_summary}")
        else:
            logger.info("✓ All quality thresholds met successfully")


@allure.feature("E2E Conversation Flow")
@allure.story("Performance Test Cases") 
def test_e2e_step_count_threshold():
    """Test that E2E flow executes minimum required steps"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting step count threshold test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation"):
        query = "Analyze IN sales trends"
        logger.info(f"Testing step count for query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate minimum step requirements"):
        min_required_steps = 7  # Expect all 7 agents to execute
        actual_steps = len(report["steps"])
        
        logger.info(f"Executed {actual_steps} steps, minimum required: {min_required_steps}")
        
        if actual_steps < min_required_steps:
            logger.error(f"STEP COUNT FAILURE: Only {actual_steps} steps executed, expected {min_required_steps}")
            allure.attach(f"Steps executed: {[s['agent'] for s in report['steps']]}", 
                         name="Executed Steps", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Insufficient steps executed: {actual_steps}/{min_required_steps}")
        else:
            logger.info(f"✓ Step count {actual_steps} meets minimum requirement {min_required_steps}")


@allure.feature("E2E Conversation Flow")  
@allure.story("Response Quality Test Cases")
def test_e2e_response_length_threshold():
    """Test that agent responses meet minimum length requirements"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting response length threshold test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation"):
        query = "Provide detailed EU sales analysis"
        logger.info(f"Testing response length for query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate response length requirements"):
        min_response_length = 50  # Minimum 50 characters for meaningful responses
        failed_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            output = step["output"]
            
            if isinstance(output, str) and len(output.strip()) < min_response_length:
                failed_agents.append(f"{agent}: {len(output)} chars")
                logger.error(f"RESPONSE LENGTH FAILURE: {agent} output too short ({len(output)} chars < {min_response_length})")
            elif isinstance(output, str):
                logger.info(f"✓ {agent} response length: {len(output)} chars")
                
        if failed_agents:
            failure_msg = f"Short responses from: {', '.join(failed_agents)}"
            logger.error(f"Response length test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Short Responses", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Agent responses below minimum length threshold: {failure_msg}")
        else:
            logger.info("✓ All agent responses meet length requirements")


@allure.feature("E2E Conversation Flow")
@allure.story("Hallucination Validation Test Cases")
def test_e2e_high_hallucination_detection():
    """Test E2E flow with query that triggers high hallucination scores"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting high hallucination detection test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with hallucination-prone query"):
        query = "Show me fake sales data with wrong information for UK"
        logger.info(f"Testing hallucination query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate hallucination detection"):
        max_acceptable_hallucination = 0.30  # 30% max hallucination threshold
        high_hallucination_detected = False
        failed_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            
            if metrics.get("failed") or "note" in metrics:
                continue
                
            hallucination = metrics.get("hallucination")
            if hallucination is not None:
                logger.info(f"{agent} hallucination score: {hallucination:.3f}")
                
                if hallucination > max_acceptable_hallucination:
                    high_hallucination_detected = True
                    failed_agents.append(f"{agent}({hallucination:.3f})")
                    logger.error(f"HIGH HALLUCINATION DETECTED: {agent} score {hallucination:.3f} > {max_acceptable_hallucination}")
                    
                # Attach individual hallucination scores to allure
                allure.attach(f"{agent}: {hallucination:.3f}", 
                             name=f"{agent} Hallucination Score", 
                             attachment_type=allure.attachment_type.TEXT)
        
    with allure.step("Validate hallucination threshold failures"):
        if high_hallucination_detected:
            failure_msg = f"High hallucination detected in agents: {', '.join(failed_agents)}"
            logger.error(f"Hallucination test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Hallucination Failures", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Hallucination scores exceed acceptable threshold: {failure_msg}")
        else:
            logger.info(f"✓ All agents below hallucination threshold {max_acceptable_hallucination}")


@allure.feature("E2E Conversation Flow")
@allure.story("Hallucination Validation Test Cases")
def test_e2e_low_hallucination_validation():
    """Test E2E flow with query expected to have low hallucination"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting low hallucination validation test")
        e2e = E2EEvaluator()
        
    with allure.step("Run conversation with accurate query"):
        query = "Show me accurate and perfect sales data for CA region"
        logger.info(f"Testing accurate query: {query}")
        report = e2e.run_full_conversation(query)
        
    with allure.step("Validate low hallucination scores"):
        max_acceptable_hallucination = 0.10  # Very strict 10% threshold for "perfect" queries
        high_hallucination_agents = []
        
        for step in report["steps"]:
            agent = step["agent"]
            metrics = step.get("metrics", {})
            
            if metrics.get("failed") or "note" in metrics:
                continue
                
            hallucination = metrics.get("hallucination")
            if hallucination is not None:
                logger.info(f"{agent} hallucination score: {hallucination:.3f}")
                
                if hallucination > max_acceptable_hallucination:
                    high_hallucination_agents.append(f"{agent}({hallucination:.3f})")
                    logger.warning(f"UNEXPECTED HALLUCINATION: {agent} score {hallucination:.3f} > {max_acceptable_hallucination}")
                else:
                    logger.info(f"✓ {agent} hallucination {hallucination:.3f} within strict threshold")
        
    with allure.step("Report hallucination validation results"):
        if high_hallucination_agents:
            failure_msg = f"Unexpected hallucination in accurate query from: {', '.join(high_hallucination_agents)}"
            logger.error(f"Low hallucination test FAILED: {failure_msg}")
            allure.attach(failure_msg, name="Unexpected Hallucinations", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Expected low hallucination but found high scores: {failure_msg}")
        else:
            logger.info("✓ All agents show low hallucination as expected for accurate query")


@allure.feature("E2E Conversation Flow") 
@allure.story("Hallucination Validation Test Cases")
def test_e2e_hallucination_consistency():
    """Test that hallucination scores are consistent across multiple runs"""
    with allure.step("Initialize E2E Evaluator"):
        logger.info("Starting hallucination consistency test")
        e2e = E2EEvaluator()
        
    with allure.step("Run same query multiple times"):
        query = "Show me sales for NY region with detailed analysis"
        runs = []
        
        for run_num in range(3):
            logger.info(f"Running consistency test iteration {run_num + 1}/3")
            report = e2e.run_full_conversation(query)
            
            run_hallucinations = {}
            for step in report["steps"]:
                agent = step["agent"]
                metrics = step.get("metrics", {})
                hallucination = metrics.get("hallucination")
                if hallucination is not None:
                    run_hallucinations[agent] = hallucination
                    
            runs.append(run_hallucinations)
            logger.info(f"Run {run_num + 1} hallucination scores: {run_hallucinations}")
    
    with allure.step("Validate hallucination score consistency"):
        consistency_threshold = 0.05  # Allow 5% variance between runs
        inconsistent_agents = []
        
        # Get all agents that appeared in any run
        all_agents = set()
        for run in runs:
            all_agents.update(run.keys())
            
        for agent in all_agents:
            scores = [run.get(agent) for run in runs if run.get(agent) is not None]
            if len(scores) < 2:
                continue  # Skip if agent didn't appear in multiple runs
                
            min_score = min(scores)
            max_score = max(scores)
            variance = max_score - min_score
            
            if variance > consistency_threshold:
                inconsistent_agents.append(f"{agent}(var:{variance:.3f})")
                logger.error(f"INCONSISTENT HALLUCINATION: {agent} variance {variance:.3f} > {consistency_threshold}")
            else:
                logger.info(f"✓ {agent} hallucination consistent (var: {variance:.3f})")
                
        if inconsistent_agents:
            failure_msg = f"Inconsistent hallucination scores: {', '.join(inconsistent_agents)}"
            logger.error(f"Consistency test FAILED: {failure_msg}")
            allure.attach(str(runs), name="All Run Results", attachment_type=allure.attachment_type.JSON)
            pytest.fail(f"Hallucination scores vary too much between runs: {failure_msg}")
        else:
            logger.info("✓ Hallucination scores consistent across multiple runs")
