import json
import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from routes.users import get_user_profile, update_user_preferences, UpdatePreferencesRequest
from services.personalization_service import personalization_service

@pytest.mark.asyncio
async def test_get_user_profile_reads_preferences(mock_db):
    """Verify profile endpoint parses and returns saved preferences."""
    mock_db.execute = AsyncMock(return_value=[{
        "id": "user-pref-1",
        "name": "Jane Elder",
        "email": "jane@example.com",
        "preferences": json.dumps({
            "topics_of_interest": ["Frugality", "Gardening"],
            "preferred_tone": "philosophical",
            "focus_era": "mid-20th-century",
            "actionability_level": "high"
        }),
        "created_at": "2026-10-15 10:00:00"
    }])

    profile = await get_user_profile("user-pref-1")
    assert profile.id == "user-pref-1"
    assert profile.preferences["preferred_tone"] == "philosophical"
    assert profile.preferences["topics_of_interest"] == ["Frugality", "Gardening"]

@pytest.mark.asyncio
async def test_update_preferences_validates_and_persists(mock_db):
    """Verify updating preferences validates fields and persists valid JSON to DB."""
    mock_db.execute = AsyncMock(side_effect=[
        [{"id": "user-pref-1"}], # user exists check
        None                     # update execute
    ])

    req = UpdatePreferencesRequest(preferences={
        "topics_of_interest": "Cooking, Woodworking",
        "preferred_tone": "practical",
        "focus_era": "early-20th-century",
        "actionability_level": "balanced"
    })

    res = await update_user_preferences("user-pref-1", req)
    assert res["success"] is True
    assert res["preferences"]["topics_of_interest"] == ["Cooking", "Woodworking"]
    assert res["preferences"]["preferred_tone"] == "practical"

    # Verify SQL update was executed
    update_sql = mock_db.execute.call_args_list[1][0][0]
    assert "UPDATE users SET preferences =" in update_sql
    assert "Woodworking" in update_sql

@pytest.mark.asyncio
async def test_personalization_context_injection(mock_db):
    """Verify saved preferences are formatted into personalization guidelines for LLM prompting."""
    mock_db.execute = AsyncMock(side_effect=[
        # 1. User preferences query
        [{
            "preferences": json.dumps({
                "topics_of_interest": ["Farming", "Craftsmanship"],
                "preferred_tone": "storytelling",
                "focus_era": "late-20th-century",
                "actionability_level": "high"
            })
        }],
        # 2. Historical thumbs_up feedback query
        [{
            "insight_text": "Always sharpen tools after sunset before resting."
        }]
    ])

    context = await personalization_service.get_user_context("user-pref-1")

    assert "User Preferences & Persona Guidelines:" in context
    assert "- Target Topics of Interest: Farming, Craftsmanship" in context
    assert "- Desired Tone: storytelling" in context
    assert "- Priority Historical Era: late-20th-century" in context
    assert "- Actionability Level: high" in context
    assert "Historically, the user has highly rated these types of insights:" in context
