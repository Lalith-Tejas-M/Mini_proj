from fastapi import APIRouter, HTTPException, Query
import structlog
from agents.visualization_agent import visualization_agent

logger = structlog.get_logger()
router = APIRouter(prefix="/api/visualization", tags=["Visualization"])

@router.get("/dashboard")
async def get_dashboard(user_id: str = Query(...)):
    """Fetch all aggregated data required to render the frontend dashboard."""
    try:
        data = await visualization_agent.get_dashboard_data(user_id)
        return data
    except Exception as e:
        logger.error("dashboard_data_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")
