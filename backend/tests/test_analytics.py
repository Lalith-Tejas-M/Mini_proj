import pytest
from unittest.mock import AsyncMock
from agents.visualization_agent import visualization_agent

@pytest.mark.asyncio
async def test_analytics_scoped_to_user(mock_db):
    """Verify that all three analytics queries (type distribution, confidence scores, recent insights) are scoped to the user."""
    mock_db.execute = AsyncMock(side_effect=[
        # 1. Type distribution query
        [{"knowledge_type": "Practices", "count": 4}, {"knowledge_type": "Ethics", "count": 2}],
        # 2. Confidence scores query
        [{"confidence_score": 0.85}, {"confidence_score": 0.72}],
        # 3. Recent insights query
        [{"id": "ins-1", "insight_text": "Insight 1", "comparison": "{}", "recommendations": "{}", "confidence_score": 0.85, "validation_passed": True, "created_at": "2026-10-16"}]
    ])

    data = await visualization_agent.get_dashboard_data(user_id="user-scoped-99")

    assert len(data["type_distribution"]) == 2
    assert data["type_distribution"][0]["name"] == "Practices"
    assert data["type_distribution"][0]["value"] == 4

    # Verify confidence histogram bucketed correctly (85 in 81-100, 72 in 61-80)
    conf_dict = {item["range"]: item["count"] for item in data["confidence_scores"]}
    assert conf_dict["81-100"] == 1
    assert conf_dict["61-80"] == 1
    assert conf_dict["0-20"] == 0

    assert len(data["recent_insights"]) == 1
    assert data["recent_insights"][0]["id"] == "ins-1"

    # CRITICAL: Verify SQL queries strictly contain user_id = 'user-scoped-99'
    type_sql = mock_db.execute.call_args_list[0][0][0]
    conf_sql = mock_db.execute.call_args_list[1][0][0]
    recent_sql = mock_db.execute.call_args_list[2][0][0]

    assert "u.user_id = 'user-scoped-99'" in type_sql
    assert "user_id = 'user-scoped-99'" in conf_sql
    assert "user_id = 'user-scoped-99'" in recent_sql

@pytest.mark.asyncio
async def test_analytics_isolation_between_users(mock_db):
    """Prove that querying analytics for User 1 uses User 1's ID and does not leak User 2's data."""
    mock_db.execute = AsyncMock(side_effect=[
        [], # User 1 has 0 extractions
        [], # User 1 has 0 insights
        []  # User 1 has 0 recent insights
    ])

    data = await visualization_agent.get_dashboard_data(user_id="user-empty-1")

    assert data["type_distribution"] == []
    # Verify every histogram range is 0
    assert all(bucket["count"] == 0 for bucket in data["confidence_scores"])
    assert data["recent_insights"] == []

    type_sql = mock_db.execute.call_args_list[0][0][0]
    conf_sql = mock_db.execute.call_args_list[1][0][0]
    recent_sql = mock_db.execute.call_args_list[2][0][0]

    assert "u.user_id = 'user-empty-1'" in type_sql
    assert "user_id = 'user-empty-1'" in conf_sql
    assert "user_id = 'user-empty-1'" in recent_sql
