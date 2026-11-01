"""Domain data models and schemas."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class IngestionItem(BaseModel):
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Item title or header")
    content: str = Field(..., description="Payload body content")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")


class ProcessRequest(BaseModel):
    query: str = Field(..., description="Search or evaluation query")
    items: List[IngestionItem] = Field(default_factory=list, description="Items to evaluate")
    top_k: int = Field(default=3, ge=1, le=20, description="Max results to return")


class MatchResult(BaseModel):
    item_id: str
    title: str
    score: float
    excerpt: str


class ProcessResponse(BaseModel):
    query: str
    matches_found: int
    results: List[MatchResult]
    latency_ms: float
