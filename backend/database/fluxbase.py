import httpx
from typing import List, Dict, Any, Optional
from config import settings
import structlog

logger = structlog.get_logger()

class FluxbaseClient:
    def __init__(self):
        self.project_id = settings.FLUXBASE_PROJECT_ID
        self.api_key = settings.FLUXBASE_API_KEY
        self.url = settings.FLUXBASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def execute(self, sql: str) -> List[Dict[str, Any]]:
        """Executes a SQL query against the Fluxbase REST API."""
        payload = {
            "projectId": self.project_id,
            "query": sql
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.url, json=payload, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("success"):
                    # The payload structure based on docs is data['result']['rows']
                    if 'result' in data and 'rows' in data['result']:
                        return data['result']['rows']
                    return []
                else:
                    error_msg = data.get("error", {}).get("message", "Unknown database error")
                    logger.error("db_execute_failed", sql=sql, error=error_msg)
                    raise Exception(f"Fluxbase error: {error_msg}")
                    
            except httpx.HTTPStatusError as e:
                logger.error("db_http_error", status_code=e.response.status_code, text=e.response.text)
                raise Exception(f"HTTP error connecting to Fluxbase: {e.response.text}")
            except Exception as e:
                logger.error("db_connection_error", error=str(e))
                raise

    async def insert(self, table: str, data: Dict[str, Any]) -> None:
        """Helper to insert a dictionary into a table securely (assuming manual escaping or standard SQL format)."""
        # Note: Since this is standard REST execution and no parameterized query is explicitly shown in the basic doc,
        # we will construct safe strings (escaped) or assume simple fields.
        # In a real ORM we use parameterization. We'll do basic string formatting.
        keys = ", ".join(data.keys())
        
        def format_value(v):
            if v is None: return "NULL"
            if isinstance(v, (int, float)): return str(v)
            if isinstance(v, bool): return "TRUE" if v else "FALSE"
            # escape single quotes
            val_str = str(v).replace("'", "''")
            return f"'{val_str}'"
            
        values = ", ".join([format_value(v) for v in data.values()])
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values});"
        await self.execute(sql)

db_client = FluxbaseClient()
