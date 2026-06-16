import json
import structlog
from services.ollama_service import ollama_client
from prompts.structuring_prompts import STRUCTURING_SYSTEM_PROMPT, STRUCTURING_USER_PROMPT

logger = structlog.get_logger()

class StructuringAgent:
    async def structure_knowledge(self, raw_knowledge: dict) -> dict:
        """Takes a raw extracted dictionary and formats it into the strict agent schema."""
        prompt = STRUCTURING_USER_PROMPT.format(
            type=raw_knowledge.get("type", ""),
            topic=raw_knowledge.get("topic", ""),
            value=raw_knowledge.get("value", ""),
            pattern=raw_knowledge.get("pattern", ""),
            snippet=raw_knowledge.get("raw_snippet", "")
        )
        
        try:
            response = await ollama_client.generate(
                prompt=prompt,
                system=STRUCTURING_SYSTEM_PROMPT,
                format_json=True
            )
            
            # Ollama should return valid JSON
            structured_data = json.loads(response)
            return structured_data
            
        except json.JSONDecodeError as e:
            logger.error("structuring_json_parse_failed", error=str(e), response=response)
            # Fallback structure
            return {
                "core_insight": {
                    "type": raw_knowledge.get("type", ""),
                    "topic": raw_knowledge.get("topic", ""),
                    "value_tag": raw_knowledge.get("value", ""),
                    "behavioral_pattern": raw_knowledge.get("pattern", "")
                },
                "context": {
                    "raw_snippet": raw_knowledge.get("raw_snippet", ""),
                    "implied_era_or_context": "Unknown"
                },
                "tags": []
            }
        except Exception as e:
            logger.error("structuring_agent_failed", error=str(e))
            raise

structuring_agent = StructuringAgent()
