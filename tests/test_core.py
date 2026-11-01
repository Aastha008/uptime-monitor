"""Unit tests for the core engine."""
import pytest
from src.models import IngestionItem
from src.core import Engine


@pytest.fixture
def engine():
    return Engine()


@pytest.fixture
def sample_items():
    return [
        IngestionItem(
            id="1",
            title="Python Clean Code",
            content="Writing maintainable Python functions and classes.",
            tags=["python", "refactoring"]
        ),
        IngestionItem(
            id="2",
            title="Database Schema Design",
            content="Relational database normalization and SQL indexing.",
            tags=["database", "sql"]
        )
    ]


def test_tokenize(engine):
    tokens = engine.tokenize("Hello, World! Python_3 is awesome.")
    assert "hello" in tokens
    assert "world" in tokens
    assert "python_3" in tokens
    assert "awesome" in tokens


def test_similarity_calculation(engine):
    set1 = {"python", "fastapi", "docker"}
    set2 = {"python", "fastapi", "kubernetes"}
    score = engine.calculate_similarity(set1, set2)
    assert score == pytest.approx(0.5, 0.01)


def test_process_query(engine, sample_items):
    response = engine.process_query("Python Clean", sample_items, top_k=1)
    assert response.matches_found == 1
    assert response.results[0].item_id == "1"
    assert response.results[0].score > 0.0
    assert response.latency_ms >= 0.0
