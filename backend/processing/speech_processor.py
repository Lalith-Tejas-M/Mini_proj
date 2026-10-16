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

SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".webm", ".ogg", ".m4a", ".flac", ".aac"}

async def process_speech(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Extract text from audio bytes using local Whisper model."""
    suffix = os.path.splitext(filename)[1].lower() if filename else ".wav"
    if not suffix or suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        # Default to webm if unknown or validate
        suffix = ".wav"

    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(audio_bytes)
            
        model = get_whisper_model()
        logger.info("transcribing_audio", filename=filename, suffix=suffix, size_bytes=len(audio_bytes))
        result = model.transcribe(temp_path)
        
        raw_text = result.get("text", "")
        return clean_and_normalize(raw_text)
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
