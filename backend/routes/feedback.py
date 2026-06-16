from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog
from services.feedback_service import feedback_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

class FeedbackRequest(BaseModel):
    insight_id: str
    user_id: str
    rating: str  # thumbs_up / thumbs_down
    context_tag: str = ""

@router.post("/")
async def submit_feedback(request: FeedbackRequest):
    """Submit thumbs up or down for an insight to improve future personalization."""
    try:
        result = await feedback_service.process_feedback(
            insight_id=request.insight_id,
            user_id=request.user_id,
            rating=request.rating,
            context_tag=request.context_tag
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("feedback_submission_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to record feedback")
