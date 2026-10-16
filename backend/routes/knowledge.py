from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import structlog
from database.fluxbase import db_client
from services.extraction_service import extraction_service
from memory.memory_manager import memory_manager

logger = structlog.get_logger()
router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])

class ExtractRequest(BaseModel):
    upload_id: str

@router.post("/extract")
async def extract_knowledge_from_upload(request: ExtractRequest):
    """Trigger the knowledge extraction pipeline for a specific upload."""
    logger.info("extraction_requested", upload_id=request.upload_id)
    
    # 1. Fetch raw text from DB
    try:
        sql = f"SELECT raw_text, status FROM uploads WHERE id = '{request.upload_id}'"
        rows = await db_client.execute(sql)
        if not rows:
            raise HTTPException(status_code=404, detail="Upload not found")
            
        upload = rows[0]
        if upload.get("status") not in ["processed", "completed"]:
            raise HTTPException(status_code=400, detail="Upload is not yet processed (e.g. speech still transcribing)")
            
        raw_text = upload.get("raw_text")
        if not raw_text:
            raise HTTPException(status_code=400, detail="No raw text found in upload")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("db_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Database error while fetching upload")

    # 2. Run extraction pipeline
    try:
        structured_data = await extraction_service.extract_from_upload(request.upload_id, raw_text)
        if len(structured_data) == 0:
            return {
                "success": True,
                "status": "no_knowledge_found",
                "message": "No meaningful knowledge found in the provided text.",
                "data": []
            }
        return {
            "success": True,
            "status": "extracted",
            "message": f"Successfully extracted and structured {len(structured_data)} pieces of knowledge.",
            "data": structured_data
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.error("extraction_validation_or_parse_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Extraction model error: {str(e)}")
    except Exception as e:
        logger.error("extraction_pipeline_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Extraction pipeline failed: {str(e)}")

@router.get("/search")
async def search_memory(
    q: str = Query(..., min_length=1, description="Semantic search query"),
    user_id: str = Query(..., description="ID of the user"),
    limit: int = Query(5, ge=1, le=50)
):
    """Perform user-scoped semantic search over preserved knowledge via FAISS embeddings."""
    logger.info("memory_search_requested", query=q, user_id=user_id)
    try:
        results = await memory_manager.retrieve_similar(query=q, user_id=user_id, top_k=limit)
        return {
            "query": q,
            "user_id": user_id,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error("memory_search_failed", error=str(e), query=q, user_id=user_id)
        raise HTTPException(status_code=500, detail="Failed to search memory")

@router.get("/{knowledge_id}")
async def get_knowledge(knowledge_id: str):
    """Retrieve a single extracted knowledge item with its structured JSON."""
    sql = f"""
    SELECT ek.knowledge_type, ek.topic, ek.value_tag, ek.pattern, ek.raw_snippet, sd.structured_json
    FROM extracted_knowledge ek
    LEFT JOIN structured_data sd ON ek.id = sd.knowledge_id
    WHERE ek.id = '{knowledge_id}'
    """
    rows = await db_client.execute(sql)
    if not rows:
        raise HTTPException(status_code=404, detail="Knowledge not found")
        
    return rows[0]
