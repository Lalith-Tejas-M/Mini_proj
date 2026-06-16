from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid
import structlog
from processing.text_processor import process_raw_text
from processing.document_processor import process_document
from processing.speech_processor import process_speech
from database.fluxbase import db_client
from database.schemas import UploadResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/api/upload", tags=["Upload"])

class TextUploadRequest(BaseModel):
    text: str
    user_id: str

@router.post("/text", response_model=UploadResponse)
async def upload_text(request: TextUploadRequest):
    """Process a raw text entry."""
    upload_id = str(uuid.uuid4())
    logger.info("upload_text", upload_id=upload_id, user_id=request.user_id)
    
    cleaned_text = await process_raw_text(request.text)
    
    # Store in DB
    await db_client.insert("uploads", {
        "id": upload_id,
        "user_id": request.user_id,
        "filename": "text_input",
        "type": "text",
        "status": "processed",
        "raw_text": cleaned_text
    })
    
    return UploadResponse(
        id=upload_id,
        filename="text_input",
        type="text",
        status="processed"
    )

@router.post("/document", response_model=UploadResponse)
async def upload_document(user_id: str = Form(...), file: UploadFile = File(...)):
    """Process a document upload (PDF, DOCX, TXT)."""
    upload_id = str(uuid.uuid4())
    logger.info("upload_document", upload_id=upload_id, filename=file.filename)
    
    try:
        file_bytes = await file.read()
        extracted_text = await process_document(file_bytes, file.filename)
        
        await db_client.insert("uploads", {
            "id": upload_id,
            "user_id": user_id,
            "filename": file.filename,
            "type": "document",
            "status": "processed",
            "raw_text": extracted_text
        })
        
        return UploadResponse(
            id=upload_id,
            filename=file.filename,
            type="document",
            status="processed"
        )
    except Exception as e:
        logger.error("document_processing_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

async def background_process_speech(upload_id: str, user_id: str, filename: str, audio_bytes: bytes):
    """Background task for speech processing since Whisper takes time."""
    try:
        extracted_text = await process_speech(audio_bytes)
        
        # In a real app we might update the DB status here
        # For simplicity we insert once it's done
        await db_client.insert("uploads", {
            "id": upload_id,
            "user_id": user_id,
            "filename": filename,
            "type": "speech",
            "status": "processed",
            "raw_text": extracted_text
        })
        logger.info("speech_processing_complete", upload_id=upload_id)
    except Exception as e:
        logger.error("speech_processing_failed", error=str(e), upload_id=upload_id)
        # Ideally we'd insert a failed status record here

@router.post("/speech")
async def upload_speech(background_tasks: BackgroundTasks, user_id: str = Form(...), file: UploadFile = File(...)):
    """Process speech upload asynchronously."""
    upload_id = str(uuid.uuid4())
    logger.info("upload_speech_initiated", upload_id=upload_id, filename=file.filename)
    
    audio_bytes = await file.read()
    
    background_tasks.add_task(
        background_process_speech,
        upload_id,
        user_id,
        file.filename,
        audio_bytes
    )
    
    return {
        "id": upload_id,
        "filename": file.filename,
        "type": "speech",
        "status": "processing_in_background",
        "message": "Speech is being transcribed. Check back later."
    }
