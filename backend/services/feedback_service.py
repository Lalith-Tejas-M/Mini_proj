import uuid
import structlog
from database.fluxbase import db_client

logger = structlog.get_logger()

class FeedbackService:
    async def process_feedback(self, insight_id: str, user_id: str, rating: str, context_tag: str = "") -> dict:
        """
        Record user feedback (thumbs_up / thumbs_down).
        Feedback acts as a learning signal for future ranking and regeneration.
        """
        if rating not in ["thumbs_up", "thumbs_down"]:
            raise ValueError("Rating must be thumbs_up or thumbs_down")
            
        logger.info("processing_feedback", insight_id=insight_id, user_id=user_id, rating=rating)
        
        feedback_id = str(uuid.uuid4())
        
        await db_client.insert("feedback", {
            "id": feedback_id,
            "insight_id": insight_id,
            "user_id": user_id,
            "rating": rating,
            "context_tag": context_tag
        })
        
        return {
            "success": True,
            "message": "Feedback recorded successfully."
        }

feedback_service = FeedbackService()
