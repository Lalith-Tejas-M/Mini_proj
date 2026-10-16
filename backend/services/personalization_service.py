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
                    raw_prefs = user_rows[0]["preferences"]
                    prefs = json.loads(raw_prefs) if isinstance(raw_prefs, str) else raw_prefs
                    if isinstance(prefs, dict) and prefs:
                        context_parts.append("User Preferences & Persona Guidelines:")
                        if prefs.get("topics_of_interest"):
                            topics = prefs["topics_of_interest"]
                            topics_str = ", ".join(topics) if isinstance(topics, list) else str(topics)
                            context_parts.append(f"- Target Topics of Interest: {topics_str}")
                        if prefs.get("preferred_tone"):
                            context_parts.append(f"- Desired Tone: {prefs['preferred_tone']}")
                        if prefs.get("focus_era"):
                            context_parts.append(f"- Priority Historical Era: {prefs['focus_era']}")
                        if prefs.get("actionability_level"):
                            context_parts.append(f"- Actionability Level: {prefs['actionability_level']}")
                        for k, v in prefs.items():
                            if k not in ["topics_of_interest", "preferred_tone", "focus_era", "actionability_level"]:
                                context_parts.append(f"- {k}: {v}")
                except Exception as parse_err:
                    logger.warn("preferences_parse_failed", error=str(parse_err))
            
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
