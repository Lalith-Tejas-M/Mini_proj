import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from routes.upload import upload_speech, get_upload_status, background_process_speech
from processing.speech_processor import SUPPORTED_AUDIO_EXTENSIONS

class DummyFile:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self._content = content

    async def read(self):
        return self._content

class DummyBackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))

@pytest.mark.asyncio
async def test_speech_upload_persists_pending_state(mock_db):
    """Verify that speech upload persists an initial record with 'pending' status before background processing."""
    bg_tasks = DummyBackgroundTasks()
    file = DummyFile("test_audio.webm", b"fake audio binary data")

    response = await upload_speech(
        background_tasks=bg_tasks,
        user_id="user-123",
        file=file
    )

    assert response["status"] == "pending"
    assert response["filename"] == "test_audio.webm"
    assert len(bg_tasks.tasks) == 1

    # Verify DB insert was called with status='pending'
    mock_db.insert.assert_called_once()
    insert_args = mock_db.insert.call_args[0]
    assert insert_args[0] == "uploads"
    assert insert_args[1]["status"] == "pending"
    assert insert_args[1]["user_id"] == "user-123"

@pytest.mark.asyncio
async def test_speech_upload_unsupported_format(mock_db):
    """Verify unsupported audio format is rejected immediately with 400 error."""
    bg_tasks = DummyBackgroundTasks()
    file = DummyFile("malicious_file.exe", b"invalid binary")

    with pytest.raises(HTTPException) as exc_info:
        await upload_speech(
            background_tasks=bg_tasks,
            user_id="user-123",
            file=file
        )
    assert exc_info.value.status_code == 400
    assert "Unsupported audio format" in exc_info.value.detail

@pytest.mark.asyncio
async def test_background_speech_processing_success(mock_db):
    """Verify successful speech processing updates record to 'completed' with raw_text."""
    with patch("routes.upload.process_speech", AsyncMock(return_value="My grandfather taught me to always fix tools.")):
        await background_process_speech("upload-uuid-1", "recording.webm", b"audio bytes")

        # Expect 2 execute calls: 1 to set 'processing', 1 to set 'completed'
        assert mock_db.execute.call_count == 2
        second_call_sql = mock_db.execute.call_args_list[1][0][0]
        assert "status = 'completed'" in second_call_sql
        assert "raw_text = 'My grandfather taught me to always fix tools.'" in second_call_sql

@pytest.mark.asyncio
async def test_background_speech_processing_failure(mock_db):
    """Verify speech processing failure marks status as 'failed' in DB."""
    with patch("routes.upload.process_speech", AsyncMock(side_effect=RuntimeError("Whisper decode error"))):
        await background_process_speech("upload-uuid-2", "recording.webm", b"corrupted audio")

        assert mock_db.execute.call_count == 2
        fail_call_sql = mock_db.execute.call_args_list[1][0][0]
        assert "status = 'failed'" in fail_call_sql

@pytest.mark.asyncio
async def test_get_upload_status(mock_db):
    """Verify upload status endpoint returns processing status and text when available."""
    mock_db.execute = AsyncMock(return_value=[{
        "id": "upload-abc",
        "user_id": "user-123",
        "filename": "speech.webm",
        "type": "speech",
        "status": "completed",
        "raw_text": "Sample transcribed wisdom.",
        "created_at": "2026-10-17 00:00:00"
    }])

    res = await get_upload_status("upload-abc")
    assert res["status"] == "completed"
    assert res["has_text"] is True
    assert res["raw_text"] == "Sample transcribed wisdom."
    assert res["error_message"] is None

@pytest.mark.asyncio
async def test_get_upload_status_failed(mock_db):
    """Verify upload status endpoint returns error message when status is failed."""
    mock_db.execute = AsyncMock(return_value=[{
        "id": "upload-fail",
        "user_id": "user-123",
        "filename": "speech.webm",
        "type": "speech",
        "status": "failed",
        "raw_text": None,
        "created_at": "2026-10-17 00:00:00"
    }])

    res = await get_upload_status("upload-fail")
    assert res["status"] == "failed"
    assert res["raw_text"] is None
    assert "Transcription failed" in res["error_message"]
