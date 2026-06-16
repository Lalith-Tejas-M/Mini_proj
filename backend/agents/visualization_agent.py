import structlog
from database.fluxbase import db_client

logger = structlog.get_logger()

class VisualizationAgent:
    async def get_dashboard_data(self, user_id: str) -> dict:
        """Aggregates all chart data for the frontend dashboards."""
        data = {
            "type_distribution": [],
            "confidence_scores": [],
            "recent_insights": []
        }
        
        try:
            # 1. Knowledge Type Distribution
            type_sql = """
            SELECT knowledge_type, COUNT(*) as count 
            FROM extracted_knowledge 
            GROUP BY knowledge_type
            """
            type_rows = await db_client.execute(type_sql)
            data["type_distribution"] = [
                {"name": r.get("knowledge_type", "Unknown"), "value": r.get("count", 0)} 
                for r in type_rows
            ]
            
            # 2. Confidence Score Histogram (Simplified for Recharts)
            conf_sql = "SELECT confidence_score FROM insights WHERE confidence_score IS NOT NULL"
            conf_rows = await db_client.execute(conf_sql)
            
            buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
            for row in conf_rows:
                score = row.get("confidence_score", 0.0) * 100
                if score <= 20: buckets["0-20"] += 1
                elif score <= 40: buckets["21-40"] += 1
                elif score <= 60: buckets["41-60"] += 1
                elif score <= 80: buckets["61-80"] += 1
                else: buckets["81-100"] += 1
                
            data["confidence_scores"] = [
                {"range": k, "count": v} for k, v in buckets.items()
            ]
            
            # 3. Recent Insights for the specific user
            recent_sql = f"""
            SELECT id, insight_text, comparison, recommendations, confidence_score, validation_passed, created_at 
            FROM insights 
            WHERE user_id = '{user_id}' 
            ORDER BY created_at DESC LIMIT 5
            """
            recent_rows = await db_client.execute(recent_sql)
            data["recent_insights"] = recent_rows

        except Exception as e:
            logger.error("visualization_aggregation_failed", error=str(e))
            
        return data

visualization_agent = VisualizationAgent()
