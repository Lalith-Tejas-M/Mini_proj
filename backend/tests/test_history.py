import json
import pytest
from unittest.mock import AsyncMock
from routes.insights import get_insight_history

@pytest.mark.asyncio
async def test_insight_history_user_scoping(mock_db):
    """Verify history query strictly scopes SQL filter to user_id."""
    mock_db.execute = AsyncMock(side_effect=[
        [{"total": 2}], # count query
        [               # select query
            {
                "id": "ins-1",
                "insight_text": "Insight for user A",
                "comparison": '{"traditional_practice": "Practice A", "modern_equivalent": "Modern A", "impact_of_shift": "Shift A"}',
                "recommendations": '{"actionable_step": "Step A", "expected_benefit": "Benefit A"}',
                "confidence_score": 0.85,
                "validation_passed": 1,
                "created_at": "2026-10-16 22:00:00",
                "check_name": "Pipeline Validation",
                "failure_reason": ""
            }
        ]
    ])

    response = await get_insight_history(user_id="user-A", limit=10, offset=0)

    assert response["total"] == 2
    assert len(response["insights"]) == 1
    assert response["insights"][0]["id"] == "ins-1"
    assert response["insights"][0]["validation_status"] == "validated"
    assert response["insights"][0]["comparison"]["traditional_practice"] == "Practice A"

    # Verify both queries filtered by user_id = 'user-A'
    count_sql = mock_db.execute.call_args_list[0][0][0]
    select_sql = mock_db.execute.call_args_list[1][0][0]
    assert "user_id = 'user-A'" in count_sql
    assert "user_id = 'user-A'" in select_sql

@pytest.mark.asyncio
async def test_insight_history_pagination(mock_db):
    """Verify limit and offset are respected in query and return structure."""
    mock_db.execute = AsyncMock(side_effect=[
        [{"total": 45}],
        []
    ])

    response = await get_insight_history(user_id="user-B", limit=15, offset=30)
    assert response["limit"] == 15
    assert response["offset"] == 30
    assert response["total"] == 45

    select_sql = mock_db.execute.call_args_list[1][0][0]
    assert "LIMIT 15 OFFSET 30" in select_sql
