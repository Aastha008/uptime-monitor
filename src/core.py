"""Core algorithmic logic and processing engine."""
import time
import re
from typing import List
from src.models import IngestionItem, MatchResult, ProcessResponse


class Engine:
    """Intelligent query matching and scoring engine."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    def tokenize(self, text: str) -> set[str]:
        """Convert text into cleaned alphanumeric tokens."""
        if not self.case_sensitive:
            text = text.lower()
        tokens = re.findall(r"\b[a-zA-Z0-9_]{2,}\b", text)
        return set(tokens)

    def calculate_similarity(self, query_tokens: set[str], content_tokens: set[str]) -> float:
        """Compute Jaccard similarity coefficient between token sets."""
        if not query_tokens or not content_tokens:
            return 0.0
        intersection = len(query_tokens.intersection(content_tokens))
        union = len(query_tokens.union(content_tokens))
        return float(intersection) / float(union) if union > 0 else 0.0

    def process_query(self, query: str, items: List[IngestionItem], top_k: int = 3) -> ProcessResponse:
        """Evaluate query across items and rank matching results."""
        start_time = time.perf_counter()
        query_tokens = self.tokenize(query)

        scored_results: List[MatchResult] = []
        for item in items:
            content_tokens = self.tokenize(f"{item.title} {item.content} {' '.join(item.tags)}")
            score = self.calculate_similarity(query_tokens, content_tokens)

            excerpt = item.content[:120] + "..." if len(item.content) > 120 else item.content
            scored_results.append(
                MatchResult(
                    item_id=item.id,
                    title=item.title,
                    score=round(score, 4),
                    excerpt=excerpt
                )
            )

        scored_results.sort(key=lambda r: r.score, reverse=True)
        top_results = scored_results[:top_k]

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return ProcessResponse(
            query=query,
            matches_found=len(top_results),
            results=top_results,
            latency_ms=elapsed_ms
        )
