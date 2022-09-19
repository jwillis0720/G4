"""Unit tests for analysis interface."""
import logging

from fastapi.testclient import TestClient
from g4.main import app

logger = logging.getLogger()

client = TestClient(app)

def test_cli() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "G3 is working"}
