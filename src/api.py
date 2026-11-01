"""FastAPI application endpoints."""
from fastapi import FastAPI, HTTPException
from src.models import ProcessRequest, ProcessResponse
from src.core import Engine

app = FastAPI(
    title="Daily Autonomous Project API",
    description="Production-grade API automatically engineered by Daily Project Factory",
    version="1.0.0"
)

engine = Engine()


@app.get("/health")
def health_check():
    """Service liveness and health endpoint."""
    return {"status": "healthy", "service": "DailyProjectApp", "version": "1.0.0"}


@app.post("/api/v1/process", response_model=ProcessResponse)
def process_payload(request: ProcessRequest):
    """Process incoming query against provided document items."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")
    return engine.process_query(request.query, request.items, request.top_k)
