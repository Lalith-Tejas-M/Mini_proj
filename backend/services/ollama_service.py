import httpx
import json
import structlog
from config import settings

logger = structlog.get_logger()

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL

    async def generate(self, prompt: str, system: str = "", format_json: bool = False) -> str:
        """
        Call Ollama API for generation.
        If format_json is True, asks Ollama to force JSON mode (supported in some models like llama3).
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        
        if format_json:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                logger.error("ollama_generation_error", error=str(e))
                raise

ollama_client = OllamaService()
