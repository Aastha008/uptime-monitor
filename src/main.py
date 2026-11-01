"""CLI runner and server entrypoint."""
import sys
from src.models import IngestionItem
from src.core import Engine


def run_cli_demo():
    """Run interactive demonstration in console."""
    print("========================================")
    print(" Daily Project Factory - Executable Demo")
    print("========================================")
    engine = Engine()
    sample_items = [
        IngestionItem(
            id="doc-1",
            title="FastAPI Microservices Guide",
            content="Building high-performance async microservices with Python, FastAPI, and Pydantic validation.",
            tags=["python", "fastapi", "microservices"]
        ),
        IngestionItem(
            id="doc-2",
            title="Machine Learning Pipelines",
            content="Scikit-Learn model training, hyperparameter optimization, and dataset preprocessing techniques.",
            tags=["machine-learning", "scikit-learn", "ai"]
        ),
        IngestionItem(
            id="doc-3",
            title="Automated Testing with Pytest",
            content="Writing robust unit and integration tests using pytest fixtures and coverage reports.",
            tags=["testing", "pytest", "devops"]
        )
    ]

    query = "FastAPI async testing"
    print(f"Executing query: '{query}' against {len(sample_items)} documents...")
    response = engine.process_query(query, sample_items, top_k=2)

    print(f"\nFound {response.matches_found} matches in {response.latency_ms}ms:")
    for rank, res in enumerate(response.results, start=1):
        print(f" [{rank}] {res.title} (Score: {res.score}) -> {res.excerpt}")
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    run_cli_demo()
