import json
import pytest
from unittest.mock import AsyncMock, patch
from validation.validation_engine import validation_engine
from agents.insight_agent import insight_agent

VALID_INSIGHT = {
    "insight_text": "In traditional rural communities, individuals repaired wooden and metal farm equipment multiple times throughout its lifecycle rather than discarding it at the first sign of wear. This sustained practice cultivated resource conservation, community interdependence, and mechanical problem-solving skills that reduced annual household expenditures significantly.",
    "comparison": {
        "traditional_practice": "Repairing broken implements manually using local scrap parts and copper wire",
        "modern_equivalent": "Discarding malfunctioning electronics and purchasing mass-produced replacements",
        "impact_of_shift": "Loss of practical repair skills, increased consumer debt, and accelerated electronic waste"
    },
    "recommendations": {
        "actionable_step": "Dedicate the first Saturday of each month to repairing one broken household item instead of ordering a replacement",
        "expected_benefit": "Develop practical problem-solving capability while saving money and reducing environmental waste"
    }
}

@pytest.mark.asyncio
async def test_rule_rejection():
    """Verify deterministic rules reject insights with missing fields or insufficient length."""
    too_short_insight = {
        "insight_text": "Short text here.",
        "comparison": {
            "traditional_practice": "Save money",
            "modern_equivalent": "Spend money",
            "impact_of_shift": "Broke"
        },
        "recommendations": {
            "actionable_step": "Stop spending",
            "expected_benefit": "More money"
        }
    }

    result = await validation_engine.evaluate_insight("Frugality", too_short_insight)
    assert result["passed"] is False
    assert result["validation_status"] == "validation_failed"
    assert "too short" in result["failure_reason"].lower()

@pytest.mark.asyncio
async def test_llm_rejection(mock_ollama):
    """Verify LLM auditor rejection marks insight as validation_failed."""
    mock_ollama.generate = AsyncMock(return_value=json.dumps({
        "score": 3.5,
        "passed": False,
        "failure_reason": "Recommendation is not actionable enough and comparison lacks depth."
    }))

    result = await validation_engine.evaluate_insight("Tool Care", VALID_INSIGHT)
    assert result["passed"] is False
    assert result["validation_status"] == "validation_failed"
    assert "not actionable" in result["failure_reason"]

@pytest.mark.asyncio
async def test_auditor_outage(mock_ollama):
    """Verify that when Ollama/auditor throws an exception, it marks validation_unavailable without falsely passing."""
    mock_ollama.generate = AsyncMock(side_effect=Exception("Connection to Ollama timed out (120s)"))

    result = await validation_engine.evaluate_insight("Tool Care", VALID_INSIGHT)
    assert result["passed"] is False
    assert result["validation_status"] == "validation_unavailable"
    assert "Auditor unavailable" in result["failure_reason"]

@pytest.mark.asyncio
async def test_malformed_auditor_output(mock_ollama):
    """Verify that malformed JSON from the auditor is classified as validation_unavailable."""
    mock_ollama.generate = AsyncMock(return_value="<html>502 Bad Gateway</html>")

    result = await validation_engine.evaluate_insight("Tool Care", VALID_INSIGHT)
    assert result["passed"] is False
    assert result["validation_status"] == "validation_unavailable"
    assert "malformed" in result["failure_reason"].lower()

@pytest.mark.asyncio
async def test_successful_validation(mock_ollama):
    """Verify that passing both rules and LLM rubric yields validated status."""
    mock_ollama.generate = AsyncMock(return_value=json.dumps({
        "score": 8.8,
        "passed": True,
        "failure_reason": ""
    }))

    result = await validation_engine.evaluate_insight("Tool Care", VALID_INSIGHT)
    assert result["passed"] is True
    assert result["validation_status"] == "validated"
    assert result["consistency_score"] == 8.8
    assert result["failure_reason"] == ""

@pytest.mark.asyncio
async def test_retry_exhaustion_does_not_silently_pass(mock_ollama, mock_memory_store):
    """Verify that exhausting regeneration attempts does not produce a validated result."""
    # LLM auditor always rejects
    mock_ollama.generate = AsyncMock(side_effect=[
        # 1. Initial generation
        json.dumps(VALID_INSIGHT),
        # 2. Validation attempt 1 (fails)
        json.dumps({"score": 4.0, "passed": False, "failure_reason": "Needs more historical grounding."}),
        # 3. Regeneration 1
        json.dumps(VALID_INSIGHT),
        # 4. Validation attempt 2 (fails)
        json.dumps({"score": 4.5, "passed": False, "failure_reason": "Comparison still vague."}),
        # 5. Regeneration 2
        json.dumps(VALID_INSIGHT),
        # 6. Validation attempt 3 (fails)
        json.dumps({"score": 4.8, "passed": False, "failure_reason": "Action step remains insufficient."}),
    ])

    result = await insight_agent.generate_insight("Frugality", "test-user-id")
    assert result["validation"]["passed"] is False
    assert result["validation"]["validation_status"] == "validation_failed"
    assert "Regeneration exhausted" in result["validation"]["failure_reason"]
    assert result["attempts"] == 3
