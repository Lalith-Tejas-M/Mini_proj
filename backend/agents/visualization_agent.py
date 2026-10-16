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
        
        safe_user_id = str(user_id).replace("'", "''")
        try:
            # 1. Knowledge Type Distribution (scoped to current user's uploads)
            type_sql = f"""
            SELECT ek.knowledge_type, COUNT(*) as count 
            FROM extracted_knowledge ek
            JOIN uploads u ON ek.upload_id = u.id
            WHERE u.user_id = '{safe_user_id}'
            GROUP BY ek.knowledge_type
            """
            type_rows = await db_client.execute(type_sql)
            data["type_distribution"] = [
                {"name": r.get("knowledge_type", "Unknown"), "value": r.get("count", 0)} 
                for r in type_rows
            ]
            
            # 2. Confidence Score Histogram (scoped to current user's insights)
            conf_sql = f"""
            SELECT confidence_score 
            FROM insights 
            WHERE user_id = '{safe_user_id}' AND confidence_score IS NOT NULL
            """
            conf_rows = await db_client.execute(conf_sql)
            
            buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
            for row in conf_rows:
                score = float(row.get("confidence_score", 0.0)) * 100.0
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
            WHERE user_id = '{safe_user_id}' 
            ORDER BY created_at DESC LIMIT 5
            """
            recent_rows = await db_client.execute(recent_sql)
            
            formatted_recent = []
            import json
            for r in recent_rows:
                comp = r.get("comparison")
                if isinstance(comp, str):
                    try:
                        comp = json.loads(comp)
                    except Exception:
                        try:
                            comp = json.loads(comp.replace("'", '"'))
                        except Exception:
                            comp = {}
                elif not isinstance(comp, dict):
                    comp = {}

                recs = r.get("recommendations")
                if isinstance(recs, str):
                    try:
                        recs = json.loads(recs)
                    except Exception:
                        try:
                            recs = json.loads(recs.replace("'", '"'))
                        except Exception:
                            recs = {}
                elif not isinstance(recs, dict):
                    recs = {}

                formatted_recent.append({
                    "id": r.get("id"),
                    "insight_text": r.get("insight_text", ""),
                    "comparison": comp,
                    "recommendations": recs,
                    "confidence_score": r.get("confidence_score", 0.0),
                    "validation_passed": bool(r.get("validation_passed", False)),
                    "created_at": str(r.get("created_at", ""))
                })

            data["recent_insights"] = formatted_recent

        except Exception as e:
            logger.error("visualization_aggregation_failed", error=str(e), user_id=user_id)
            
        return data

visualization_agent = VisualizationAgent()
