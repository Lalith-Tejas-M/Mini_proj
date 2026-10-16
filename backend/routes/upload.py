import os
import uuid
import structlog
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from processing.text_processor import process_raw_text
from processing.document_processor import process_document
from processing.speech_processor import process_speech, SUPPORTED_AUDIO_EXTENSIONS
from database.fluxbase import db_client

logger = structlog.get_logger()
router = APIRouter(prefix="/api/upload", tags=["Upload"])

class TextUploadRequest(BaseModel):
    text: str
    user_id: str

@router.post("/text")
async def upload_text(request: TextUploadRequest):
    """Save raw text upload to database."""
    cleaned_text = await process_raw_text(request.text)
    upload_id = str(uuid.uuid4())
    
    await db_client.insert("uploads", {
        "id": upload_id,
        "user_id": request.user_id,
        "filename": "text_input",
        "type": "text",
        "status": "processed",
        "raw_text": cleaned_text
    })
    
    return {
        "id": upload_id,
        "filename": "text_input",
        "type": "text",
        "status": "processed"
    }

@router.post("/document")
async def upload_document(user_id: str = Form(...), file: UploadFile = File(...)):
    """Extract and save document text (PDF, DOCX, TXT) to database."""
    file_bytes = await file.read()
    try:
        cleaned_text = await process_document(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    upload_id = str(uuid.uuid4())
    await db_client.insert("uploads", {
        "id": upload_id,
        "user_id": user_id,
        "filename": file.filename,
        "type": "document",
        "status": "processed",
        "raw_text": cleaned_text
    })
    
    return {
        "id": upload_id,
        "filename": file.filename,
        "type": "document",
        "status": "processed"
    }

async def background_process_speech(upload_id: str, filename: str, audio_bytes: bytes):
    """Background task for speech processing since Whisper takes time."""
    safe_id = upload_id.replace("'", "''")
    try:
        # Mark as processing
        await db_client.execute(f"UPDATE uploads SET status = 'processing' WHERE id = '{safe_id}'")
        
        extracted_text = await process_speech(audio_bytes, filename=filename)
        safe_text = extracted_text.replace("'", "''")
        
        await db_client.execute(
            f"UPDATE uploads SET status = 'completed', raw_text = '{safe_text}' WHERE id = '{safe_id}'"
        )
        logger.info("speech_processing_complete", upload_id=upload_id)
    except Exception as e:
        logger.error("speech_processing_failed", error=str(e), upload_id=upload_id)
        try:
            await db_client.execute(f"UPDATE uploads SET status = 'failed' WHERE id = '{safe_id}'")
        except Exception as db_err:
            logger.error("failed_to_mark_upload_as_failed", error=str(db_err), upload_id=upload_id)

@router.post("/speech")
async def upload_speech(background_tasks: BackgroundTasks, user_id: str = Form(...), file: UploadFile = File(...)):
    """Process speech upload asynchronously."""
    upload_id = str(uuid.uuid4())
    filename = file.filename or "recording.webm"
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        supported_list = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
        logger.warn("unsupported_audio_extension", filename=filename, extension=ext)
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format '{ext or 'unknown'}'. Supported formats: {supported_list}"
        )
        
    logger.info("upload_speech_initiated", upload_id=upload_id, filename=filename, user_id=user_id)
    
    audio_bytes = await file.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty audio payload received")

    # 1. Persist initial upload record before transcription starts with explicit 'pending' status
    await db_client.insert("uploads", {
        "id": upload_id,
        "user_id": user_id,
        "filename": filename,
        "type": "speech",
        "status": "pending",
        "raw_text": None
    })
    
    # 2. Add task to background processor
    background_tasks.add_task(
        background_process_speech,
        upload_id,
        filename,
        audio_bytes
    )
    
    return {
        "id": upload_id,
        "filename": filename,
        "type": "speech",
        "status": "pending",
        "message": "Speech upload received and queued for Whisper transcription."
    }

@router.get("/{upload_id}/status")
async def get_upload_status(upload_id: str):
    """Retrieve the current processing status and transcribed text of an upload."""
    safe_id = upload_id.replace("'", "''")
    rows = await db_client.execute(
        f"SELECT id, user_id, filename, type, status, raw_text, created_at FROM uploads WHERE id = '{safe_id}'"
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Upload not found")
        
    upload = rows[0]
    status = upload.get("status", "unknown")
    raw_text = upload.get("raw_text")
    
    error_message = None
    if status == "failed":
        error_message = "Transcription failed. Please check audio clarity and try again."
        
    return {
        "id": upload.get("id"),
        "user_id": upload.get("user_id"),
        "filename": upload.get("filename"),
        "type": upload.get("type"),
        "status": status,
        "has_text": bool(raw_text and len(raw_text.strip()) > 0),
        "raw_text": raw_text if status in ["completed", "processed"] else None,
        "error_message": error_message,
        "created_at": str(upload.get("created_at", ""))
    }
