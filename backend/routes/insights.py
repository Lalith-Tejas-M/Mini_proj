from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import structlog
from database.fluxbase import db_client
from agents.insight_agent import insight_agent
from database.schemas import InsightResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/api/insights", tags=["Insights"])

class GenerateInsightRequest(BaseModel):
    topic: str
    user_id: str

@router.post("/generate", response_model=InsightResponse)
async def generate_insight(request: GenerateInsightRequest):
    """Trigger the insight generation pipeline with RAG and Validation."""
    logger.info("insight_generation_requested", topic=request.topic, user_id=request.user_id)
    
    try:
        result = await insight_agent.generate_insight(request.topic, request.user_id)
        
        insight_data = result["insight"]
        validation = result["validation"]
        final_score = result["final_score"]
        
        insight_id = str(uuid.uuid4())
        
        # We need a structured_id for the FK, but this insight might be purely synthesized from multiple memories.
        # For our schema, we'll just leave it NULL or attach it to the most relevant memory if needed.
        # Wait, our schema requires structured_id? Let's check init_fluxbase.
        # `structured_id VARCHAR(255) REFERENCES structured_data(id)` 
        # In SQL, foreign keys can usually be NULL unless marked NOT NULL. We'll pass None for now.
        
        # Save Insight
        await db_client.insert("insights", {
            "id": insight_id,
            "structured_id": None, # Aggregated insight
            "user_id": request.user_id,
            "insight_text": insight_data.get("insight_text", ""),
            "comparison": str(insight_data.get("comparison", {})),
            "recommendations": str(insight_data.get("recommendations", {})),
            "confidence_score": final_score,
            "validation_passed": validation["passed"]
        })
        
        # Save Confidence Scores
        await db_client.insert("confidence_scores", {
            "id": str(uuid.uuid4()),
            "insight_id": insight_id,
            "retrieval_similarity": 0.0, # We'd need to pull this out of the agent
            "semantic_relevance": 0.0,
            "consistency_score": validation.get("consistency_score", 0.0),
            "structural_quality": validation.get("structural_quality", 0.0),
            "memory_alignment": 0.0,
            "final_score": final_score
        })
        
        # Save Validation Logs
        await db_client.insert("validation_logs", {
            "id": str(uuid.uuid4()),
            "insight_id": insight_id,
            "check_name": "Pipeline Validation",
            "passed": validation["passed"],
            "score": validation.get("score", 0.0),
            "failure_reason": validation.get("failure_reason", "")
        })
        
        return InsightResponse(
            id=insight_id,
            insight_text=insight_data.get("insight_text", ""),
            comparison=insight_data.get("comparison", {}),
            recommendations=insight_data.get("recommendations", {}),
            confidence_score=final_score,
            validation_passed=validation["passed"],
            created_at="now" # In a real app we'd fetch the created timestamp
        )
        
    except Exception as e:
        import traceback
        with open("error_traceback.txt", "w") as f:
            f.write(traceback.format_exc())
        logger.error("insight_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
