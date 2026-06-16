from sentence_transformers import SentenceTransformer
import structlog
import numpy as np

logger = structlog.get_logger()

# Use a lightweight, fast model for semantic embeddings
MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        logger.info("loading_embedding_model", model=MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def generate_embedding(text: str) -> np.ndarray:
    """Generate a 384-dimensional dense vector representation of the text."""
    model = get_embedding_model()
    # Normalize embeddings to allow dot product for cosine similarity
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding
