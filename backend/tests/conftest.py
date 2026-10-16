import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock

# Add backend directory to sys.path so tests can import modules directly
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

@pytest.fixture
def mock_db():
    from database.fluxbase import db_client
    orig_execute = db_client.execute
    orig_insert = db_client.insert
    db_client.execute = AsyncMock(return_value=[])
    db_client.insert = AsyncMock(return_value=None)
    yield db_client
    db_client.execute = orig_execute
    db_client.insert = orig_insert

@pytest.fixture
def mock_ollama():
    from services.ollama_service import ollama_client
    orig_generate = ollama_client.generate
    ollama_client.generate = AsyncMock(return_value="{}")
    yield ollama_client
    ollama_client.generate = orig_generate

@pytest.fixture
def mock_memory_store():
    from memory.memory_manager import memory_manager
    orig_store = memory_manager.store_knowledge_embedding
    orig_retrieve = memory_manager.retrieve_similar
    memory_manager.store_knowledge_embedding = AsyncMock(return_value=None)
    memory_manager.retrieve_similar = AsyncMock(return_value=[])
    yield memory_manager
    memory_manager.store_knowledge_embedding = orig_store
    memory_manager.retrieve_similar = orig_retrieve
