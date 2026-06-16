import json
import uuid
import structlog
from services.ollama_service import ollama_client
from prompts.extraction_prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT
from agents.structuring_agent import structuring_agent
from database.fluxbase import db_client
from memory.memory_manager import memory_manager
from utils.text_utils import chunk_text

logger = structlog.get_logger()

class ExtractionService:
    async def extract_from_upload(self, upload_id: str, raw_text: str) -> list[dict]:
        """
        Orchestrates the extraction pipeline:
        1. Chunks text if too long
        2. Extracts raw knowledge via LLM
        3. Filters low-quality signals
        4. Structures via StructuringAgent
        5. Saves to Fluxbase DB
        """
        chunks = chunk_text(raw_text, chunk_size=2000, overlap=200)
        all_structured_data = []

        for idx, chunk in enumerate(chunks):
            logger.info("extracting_chunk", chunk_index=idx, total_chunks=len(chunks), upload_id=upload_id)
            
            prompt = EXTRACTION_USER_PROMPT.format(text=chunk)
            try:
                response = await ollama_client.generate(
                    prompt=prompt,
                    system=EXTRACTION_SYSTEM_PROMPT,
                    format_json=True
                )
                
                raw_extractions = json.loads(response)
                if not isinstance(raw_extractions, list):
                    raw_extractions = [raw_extractions]
                    
                for raw_know in raw_extractions:
                    if not self._is_meaningful(raw_know):
                        continue
                        
                    # Save raw knowledge
                    knowledge_id = str(uuid.uuid4())
                    await db_client.insert("extracted_knowledge", {
                        "id": knowledge_id,
                        "upload_id": upload_id,
                        "knowledge_type": raw_know.get("type", "Unknown"),
                        "topic": raw_know.get("topic", "Unknown"),
                        "value_tag": raw_know.get("value", ""),
                        "pattern": raw_know.get("pattern", ""),
                        "raw_snippet": raw_know.get("raw_snippet", "")
                    })
                    
                    # Structure it
                    structured_json = await structuring_agent.structure_knowledge(raw_know)
                    structured_id = str(uuid.uuid4())
                    
                    # Save structured data
                    await db_client.insert("structured_data", {
                        "id": structured_id,
                        "knowledge_id": knowledge_id,
                        "structured_json": json.dumps(structured_json),
                        "agent_version": "1.0"
                    })
                    
                    # Store semantic embedding into FAISS for retrieval
                    snippet_content = f"{raw_know.get('topic', '')}. {raw_know.get('pattern', '')}. {raw_know.get('raw_snippet', '')}"
                    await memory_manager.store_knowledge_embedding(knowledge_id, snippet_content)
                    
                    all_structured_data.append(structured_json)
                    
            except json.JSONDecodeError as e:
                logger.error("extraction_json_parse_error", error=str(e), response=response)
            except Exception as e:
                logger.error("extraction_chunk_failed", error=str(e))
                
        return all_structured_data

    def _is_meaningful(self, extraction: dict) -> bool:
        """Rule-based filter to remove vague or meaningless extractions."""
        snippet = extraction.get("raw_snippet", "")
        if len(snippet.split()) < 5:
            return False # Too short to be a pattern
        
        val = extraction.get("value", "")
        if not val or val.lower() in ["none", "n/a", "unknown"]:
            return False
            
        return True

extraction_service = ExtractionService()
