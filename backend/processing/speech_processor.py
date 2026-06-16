import whisper
import tempfile
import os
import structlog
from utils.text_utils import clean_and_normalize

logger = structlog.get_logger()

# Load model lazily to avoid heavy startup if not used immediately
_model = None

def get_whisper_model():
    global _model
    if _model is None:
        logger.info("loading_whisper_model", size="base")
        _model = whisper.load_model("base")
    return _model

async def process_speech(audio_bytes: bytes) -> str:
    """Extract text from audio bytes using local Whisper model."""
    # Whisper requires a file path (or numpy array). Writing to temp file is easiest.
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(audio_bytes)
            
        model = get_whisper_model()
        logger.info("transcribing_audio")
        result = model.transcribe(temp_path)
        
        raw_text = result.get("text", "")
        return clean_and_normalize(raw_text)
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
