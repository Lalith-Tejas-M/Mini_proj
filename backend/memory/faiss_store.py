import faiss
import numpy as np
import os
import structlog

logger = structlog.get_logger()

class FAISSStore:
    def __init__(self, dimension: int = 384, index_path: str = "data/faiss_index/main.index"):
        self.dimension = dimension
        self.index_path = index_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # IndexFlatIP uses Inner Product (Dot Product). 
        # Since we normalize our vectors, Dot Product == Cosine Similarity.
        if os.path.exists(self.index_path):
            logger.info("loading_existing_faiss_index", path=self.index_path)
            self.index = faiss.read_index(self.index_path)
        else:
            logger.info("creating_new_faiss_index", dimension=self.dimension)
            # Create an IDMap so we can map vectors to SQLite integer IDs
            # But wait, FAISS IndexIDMap expects integer IDs (int64).
            # Our database UUIDs are strings. We need a way to map them.
            # Easiest way: FAISS generates sequential int IDs, we maintain a DB table to map int -> string ID.
            # Wait, FAISS `IndexFlatIP` doesn't inherently store string IDs.
            # We will use IndexIDMap to store arbitrary 64-bit ints.
            # We can hash our UUID string to a 64-bit int, or keep an auto-incrementing integer in SQLite just for vectors.
            self.base_index = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIDMap(self.base_index)
            self._save()

    def add_embedding(self, int_id: int, vector: np.ndarray):
        """Add a single embedding to the index with a specific integer ID."""
        # FAISS expects 2D array: (1, D)
        vec_2d = np.array([vector]).astype('float32')
        id_array = np.array([int_id]).astype('int64')
        
        self.index.add_with_ids(vec_2d, id_array)
        self._save()

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> tuple[list[int], list[float]]:
        """Search the index for the top_k most similar vectors. Returns (ids, scores)."""
        if self.index.ntotal == 0:
            return [], []
            
        vec_2d = np.array([query_vector]).astype('float32')
        # D is distances (similarities for IP), I is indices (int IDs)
        D, I = self.index.search(vec_2d, top_k)
        
        ids = I[0].tolist()
        scores = D[0].tolist()
        
        # Filter out invalid results (-1)
        valid_results = [(id, score) for id, score in zip(ids, scores) if id != -1]
        
        if not valid_results:
            return [], []
            
        valid_ids, valid_scores = zip(*valid_results)
        return list(valid_ids), list(valid_scores)

    def _save(self):
        """Persist the index to disk."""
        faiss.write_index(self.index, self.index_path)

# Singleton instance
faiss_store = FAISSStore()
