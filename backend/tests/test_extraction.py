import json
import pytest
from unittest.mock import AsyncMock, patch
from prompts.structuring_prompts import STRUCTURING_USER_PROMPT
from agents.structuring_agent import structuring_agent
from services.extraction_service import extraction_service

def test_structuring_prompt_formatting():
    """Regression test: verify STRUCTURING_USER_PROMPT formats cleanly without KeyError."""
    formatted = STRUCTURING_USER_PROMPT.format(
        type="Practices",
        topic="Frugality",
        value="Resourcefulness",
        pattern="Repaired old tools instead of discarding them",
        snippet="My grandfather mended every broken rake with copper wire."
    )
    assert '"core_insight": {' in formatted
    assert 'Type: Practices' in formatted
    assert 'Topic: Frugality' in formatted
    assert 'Value: Resourcefulness' in formatted

@pytest.mark.asyncio
async def test_valid_knowledge_extraction(mock_ollama, mock_db, mock_memory_store):
    """Test standard valid knowledge extraction flow."""
    extraction_output = [
        {
            "type": "Practices",
            "topic": "Tool Repair",
            "value": "Frugality and self-reliance",
            "pattern": "Regularly mending broken wooden tools using wire",
            "raw_snippet": "We repaired things instead of buying new ones whenever possible."
        }
    ]
    structured_output = {
        "core_insight": {
            "type": "Practices",
            "topic": "Tool Repair",
            "value_tag": "Frugality and self-reliance",
            "behavioral_pattern": "Regularly mending broken wooden tools using wire"
        },
        "context": {
            "raw_snippet": "We repaired things instead of buying new ones whenever possible.",
            "implied_era_or_context": "Mid-20th Century"
        },
        "tags": ["repair", "frugality", "tools"]
    }

    mock_ollama.generate = AsyncMock(side_effect=[
        json.dumps(extraction_output),
        json.dumps(structured_output)
    ])

    results = await extraction_service.extract_from_upload(
        upload_id="test-upload-123",
        raw_text="We repaired things instead of buying new ones whenever possible."
    )

    assert len(results) == 1
    assert results[0]["core_insight"]["topic"] == "Tool Repair"
    assert mock_db.insert.call_count >= 2
    assert mock_memory_store.store_knowledge_embedding.called

@pytest.mark.asyncio
async def test_no_meaningful_extraction(mock_ollama, mock_db, mock_memory_store):
    """Test when input text has no meaningful knowledge or fails meaningfulness rules."""
    mock_ollama.generate = AsyncMock(return_value="[]")

    results = await extraction_service.extract_from_upload(
        upload_id="test-upload-empty",
        raw_text="Hello world today was nice."
    )

    assert len(results) == 0
    assert mock_db.insert.call_count == 0

@pytest.mark.asyncio
async def test_malformed_model_output(mock_ollama, mock_db):
    """Test that malformed model JSON raises an explicit ValueError and is not silently swallowed."""
    mock_ollama.generate = AsyncMock(return_value="This is definitely not valid JSON <error>")

    with pytest.raises(ValueError, match="invalid JSON"):
        await extraction_service.extract_from_upload(
            upload_id="test-upload-malformed",
            raw_text="Long enough text to trigger knowledge extraction attempt."
        )

@pytest.mark.asyncio
async def test_structuring_failure(mock_ollama):
    """Test that structuring failure raises and is visible to the caller."""
    raw_know = {
        "type": "Ethics",
        "topic": "Honesty",
        "value": "Truthfulness",
        "pattern": "Always told the truth even when difficult",
        "raw_snippet": "Honesty was taught as the foundation of family honor."
    }

    mock_ollama.generate = AsyncMock(return_value="Invalid json from structuring model")

    with pytest.raises(ValueError, match="Structuring agent failed to parse model JSON"):
        await structuring_agent.structure_knowledge(raw_know)
