import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router
from routes.knowledge import router as knowledge_router
from routes.insights import router as insights_router
from routes.feedback import router as feedback_router
from routes.users import router as users_router
from routes.visualization import router as visualization_router

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(
    title="Intergenerational Knowledge AI Platform",
    description="Agentic AI system for preserving and processing human knowledge.",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(upload_router)
app.include_router(knowledge_router)
app.include_router(insights_router)
app.include_router(feedback_router)
app.include_router(users_router)
app.include_router(visualization_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Knowledge AI Backend"}

if __name__ == "__main__":
    import uvicorn
    logger.info("starting_server", port=8000)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
