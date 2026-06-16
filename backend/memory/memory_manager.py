import structlog
import uuid
import hashlib
from memory.embedding_pipeline import generate_embedding
from memory.faiss_store import faiss_store
from database.fluxbase import db_client

logger = structlog.get_logger()

class MemoryManager:
    def _uuid_to_int(self, string_uuid: str) -> int:
        """Hash a UUID string to a 64-bit integer for FAISS."""
        # MD5 to 16 bytes, take first 8 bytes for 64-bit int
        hash_digest = hashlib.md5(string_uuid.encode('utf-8')).digest()
        # Convert first 8 bytes to signed 64-bit integer
        return int.from_bytes(hash_digest[:8], byteorder='big', signed=True)

    async def store_knowledge_embedding(self, knowledge_id: str, content: str):
        """Generates embedding for a string, stores it in FAISS and maps it in Fluxbase."""
        logger.info("storing_knowledge_embedding", knowledge_id=knowledge_id)
        
        # 1. Generate dense vector
        vector = generate_embedding(content)
        
        # 2. Convert UUID to int for FAISS
        faiss_id = self._uuid_to_int(knowledge_id)
        
        # 3. Add to FAISS (persisted to disk)
        faiss_store.add_embedding(faiss_id, vector)
        
        # 4. Save metadata in DB so we can map int -> uuid if needed, though we mainly need it for record keeping
        # Wait, if FAISS returns the int_id, how do we get the knowledge_id back?
        # We need an `embeddings` table in Fluxbase. Wait, we didn't add one in init_fluxbase.py.
        # Let's create an embeddings table to map faiss_int_id -> knowledge_id.
        try:
            # First time, ensure the table exists (we missed this in init_fluxbase, let's create it if missing)
            create_sql = """
            CREATE TABLE IF NOT EXISTS embeddings (
                faiss_id VARCHAR(255) PRIMARY KEY,
                knowledge_id VARCHAR(255),
                model_name VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
            await db_client.execute(create_sql)
            
            # Now insert the mapping
            await db_client.insert("embeddings", {
                "faiss_id": str(faiss_id),
                "knowledge_id": knowledge_id,
                "model_name": "all-MiniLM-L6-v2"
            })
        except Exception as e:
            logger.error("failed_to_store_embedding_metadata", error=str(e))
            raise

    async def retrieve_similar(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for related knowledge using semantic search."""
        logger.info("retrieving_semantic_memory", query=query)
        
        vector = generate_embedding(query)
        faiss_ids, scores = faiss_store.search(vector, top_k=top_k)
        
        if not faiss_ids:
            return []
            
        # Convert int IDs to strings for SQL IN clause
        str_ids = [f"'{str(fid)}'" for fid in faiss_ids]
        ids_csv = ",".join(str_ids)
        
        # Join embeddings and extracted_knowledge to get full context
        sql = f"""
        SELECT ek.id, ek.knowledge_type, ek.topic, ek.pattern, ek.raw_snippet, e.faiss_id
        FROM embeddings e
        JOIN extracted_knowledge ek ON e.knowledge_id = ek.id
        WHERE e.faiss_id IN ({ids_csv})
        """
        try:
            results = await db_client.execute(sql)
            
            # We want to return them ordered by FAISS score
            # Create a map of faiss_id (as str) to score for quick lookup
            score_map = {str(fid): score for fid, score in zip(faiss_ids, scores)}
            
            for row in results:
                fid = str(row["faiss_id"])
                row["similarity_score"] = score_map.get(fid, 0.0)
                
            # Sort descending by score
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return results
            
        except Exception as e:
            logger.error("memory_retrieval_failed", error=str(e))
            return []

memory_manager = MemoryManager()
