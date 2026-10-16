from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import uuid
import json
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
        component_scores = result.get("component_scores", {})
        
        insight_id = str(uuid.uuid4())
        
        # Save Insight
        await db_client.insert("insights", {
            "id": insight_id,
            "structured_id": None, # Aggregated insight
            "user_id": request.user_id,
            "insight_text": insight_data.get("insight_text", ""),
            "comparison": json.dumps(insight_data.get("comparison", {})),
            "recommendations": json.dumps(insight_data.get("recommendations", {})),
            "confidence_score": final_score,
            "validation_passed": validation["passed"]
        })
        
        # Save actual component scores into confidence_scores
        await db_client.insert("confidence_scores", {
            "id": str(uuid.uuid4()),
            "insight_id": insight_id,
            "retrieval_similarity": component_scores.get("retrieval_similarity", 0.0),
            "semantic_relevance": component_scores.get("semantic_relevance", 0.0),
            "consistency_score": component_scores.get("consistency_score", 0.0),
            "structural_quality": component_scores.get("structural_quality", 0.0),
            "memory_alignment": component_scores.get("memory_alignment", 0.0),
            "final_score": final_score
        })
        
        # Save Validation Logs
        val_status = validation.get("status", "validated" if validation["passed"] else "validation_failed")
        await db_client.insert("validation_logs", {
            "id": str(uuid.uuid4()),
            "insight_id": insight_id,
            "check_name": f"Pipeline Validation ({val_status})",
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
            validation_status=val_status,
            validation_reason=validation.get("failure_reason", ""),
            component_scores=component_scores,
            created_at="now"
        )
        
    except Exception as e:
        logger.error("insight_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_insight_history(
    user_id: str = Query(..., description="ID of the user"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieve persisted insight history for a specific user with pagination."""
    try:
        safe_user_id = user_id.replace("'", "''")
        count_sql = f"SELECT COUNT(*) as total FROM insights WHERE user_id = '{safe_user_id}'"
        count_rows = await db_client.execute(count_sql)
        total = count_rows[0].get("total", 0) if count_rows else 0
        
        sql = f"""
        SELECT i.id, i.insight_text, i.comparison, i.recommendations, i.confidence_score, 
               i.validation_passed, i.created_at, vl.check_name, vl.failure_reason
        FROM insights i
        LEFT JOIN validation_logs vl ON i.id = vl.insight_id
        WHERE i.user_id = '{safe_user_id}'
        ORDER BY i.created_at DESC
        LIMIT {limit} OFFSET {offset}
        """
        rows = await db_client.execute(sql)
        
        formatted_insights = []
        for r in rows:
            comp = r.get("comparison")
            if isinstance(comp, str):
                try:
                    comp = json.loads(comp)
                except Exception:
                    try:
                        comp = json.loads(comp.replace("'", '"'))
                    except Exception:
                        comp = {}
            elif not isinstance(comp, dict):
                comp = {}

            recs = r.get("recommendations")
            if isinstance(recs, str):
                try:
                    recs = json.loads(recs)
                except Exception:
                    try:
                        recs = json.loads(recs.replace("'", '"'))
                    except Exception:
                        recs = {}
            elif not isinstance(recs, dict):
                recs = {}

            val_passed = bool(r.get("validation_passed", False))
            reason = r.get("failure_reason", "")
            if val_passed:
                val_status = "validated"
            elif reason and "unavailable" in reason.lower():
                val_status = "validation_unavailable"
            else:
                val_status = "validation_failed"

            formatted_insights.append({
                "id": r.get("id"),
                "insight_text": r.get("insight_text", ""),
                "comparison": comp,
                "recommendations": recs,
                "confidence_score": r.get("confidence_score", 0.0),
                "validation_passed": val_passed,
                "validation_status": val_status,
                "validation_reason": reason,
                "created_at": str(r.get("created_at", ""))
            })
            
        return {
            "insights": formatted_insights,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error("insight_history_fetch_failed", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="Failed to fetch insight history")
