
"""
Basic API tests for RAG Research Assistant
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_query_endpoint_structure():
    """Test query endpoint accepts valid request"""
    response = client.post(
        "/query",
        json={"question": "test question", "n_results": 3}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "question" in data
    assert "answer" in data
    assert "sources" in data
    assert "num_chunks_used" in data
    
    assert data["question"] == "test question"


def test_query_endpoint_empty_question():
    """Test query endpoint rejects empty question"""
    response = client.post(
        "/query",
        json={"question": "", "n_results": 3}
    )
    assert response.status_code == 400


def test_query_endpoint_invalid_n_results():
    """Test query endpoint validates n_results"""
    # Too low
    response = client.post(
        "/query",
        json={"question": "test", "n_results": 0}
    )
    assert response.status_code == 400
    
    # Too high
    response = client.post(
        "/query",
        json={"question": "test", "n_results": 11}
    )
    assert response.status_code == 400


def test_upload_endpoint_no_file():
    """Test upload endpoint requires file"""
    response = client.post("/upload")
    assert response.status_code == 422  # Validation error


def test_docs_endpoint():
    """Test API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint():
    """Test ReDoc documentation is available"""
    response = client.get("/redoc")
    assert response.status_code == 200