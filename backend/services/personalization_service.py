import json
import structlog
from database.fluxbase import db_client

logger = structlog.get_logger()

class PersonalizationService:
    async def get_user_context(self, user_id: str) -> str:
        """
        Builds a context string from the user's preferences and past approved insights.
        This soft context is injected into the insight prompts to personalize output.
        """
        context_parts = []
        
        try:
            # 1. Fetch User Preferences
            sql_user = f"SELECT preferences FROM users WHERE id = '{user_id}'"
            user_rows = await db_client.execute(sql_user)
            if user_rows and user_rows[0].get("preferences"):
                try:
                    prefs = json.loads(user_rows[0]["preferences"])
                    context_parts.append("User Preferences:")
                    for k, v in prefs.items():
                        context_parts.append(f"- {k}: {v}")
                except:
                    pass
            
            # 2. Fetch past approved patterns (thumbs_up)
            sql_feedback = f"""
            SELECT i.insight_text 
            FROM feedback f
            JOIN insights i ON f.insight_id = i.id
            WHERE f.user_id = '{user_id}' AND f.rating = 'thumbs_up'
            LIMIT 3
            """
            feedback_rows = await db_client.execute(sql_feedback)
            if feedback_rows:
                context_parts.append("\nHistorically, the user has highly rated these types of insights:")
                for row in feedback_rows:
                    snippet = row.get("insight_text", "")[:100] + "..."
                    context_parts.append(f"- {snippet}")
                    
        except Exception as e:
            logger.error("personalization_context_fetch_failed", error=str(e))
            
        return "\n".join(context_parts)

personalization_service = PersonalizationService()
