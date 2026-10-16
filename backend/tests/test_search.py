import numpy as np
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from routes.knowledge import search_memory
from memory.memory_manager import memory_manager

@pytest.mark.asyncio
async def test_search_memory_matching_results(mock_db):
    """Verify semantic search maps embeddings back to user-scoped extracted knowledge."""
    # Mock FAISS store search
    with patch("memory.memory_manager.faiss_store.search", return_value=([12345, 67890], [0.92, 0.81])):
        with patch("memory.memory_manager.generate_embedding", return_value=np.zeros(384, dtype=np.float32)):
            mock_db.execute = AsyncMock(return_value=[
                {
                    "id": "know-1",
                    "knowledge_type": "Practices",
                    "topic": "Tool Repair",
                    "value_tag": "Frugality",
                    "pattern": "Fixed tools with copper wire",
                    "raw_snippet": "We repaired tools rather than buying new ones.",
                    "faiss_id": 12345,
                    "user_id": "user-A"
                }
            ])

            response = await search_memory(q="How did they fix tools?", user_id="user-A", limit=5)

            assert response["count"] == 1
            result = response["results"][0]
            assert result["topic"] == "Tool Repair"
            assert result["category"] == "Practices"
            assert result["relevance_score"] == 0.92
            assert result["snippet"] == "We repaired tools rather than buying new ones."

            # Verify SQL query had user scoping clause
            sql = mock_db.execute.call_args[0][0]
            assert "u.user_id = 'user-A'" in sql

@pytest.mark.asyncio
async def test_search_memory_empty_results(mock_db):
    """Verify empty FAISS or database matches return empty results cleanly."""
    with patch("memory.memory_manager.faiss_store.search", return_value=([], [])):
        with patch("memory.memory_manager.generate_embedding", return_value=np.zeros(384, dtype=np.float32)):
            response = await search_memory(q="Non-existent topic", user_id="user-A", limit=5)
            assert response["count"] == 0
            assert response["results"] == []

@pytest.mark.asyncio
async def test_search_memory_user_isolation(mock_db):
    """Verify that search for User A strictly scopes query to User A."""
    with patch("memory.memory_manager.faiss_store.search", return_value=([111], [0.85])):
        with patch("memory.memory_manager.generate_embedding", return_value=np.zeros(384, dtype=np.float32)):
            mock_db.execute = AsyncMock(return_value=[])

            await search_memory(q="Any wisdom", user_id="user-X", limit=5)

            sql = mock_db.execute.call_args[0][0]
            assert "u.user_id = 'user-X'" in sql
