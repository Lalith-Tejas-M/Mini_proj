from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog
from database.fluxbase import db_client
from services.extraction_service import extraction_service

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
        if upload.get("status") != "processed":
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
        return {
            "success": True,
            "message": f"Successfully extracted and structured {len(structured_data)} pieces of knowledge.",
            "data": structured_data
        }
    except Exception as e:
        logger.error("extraction_pipeline_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Extraction pipeline failed")

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
