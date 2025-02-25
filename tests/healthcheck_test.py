import sys
import os

# Add the parent directory to sys.path to make app.py accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import pytest
from app import app, db  # Import Flask app and database
from models import HealthCheck  # Import models used in the app


@pytest.fixture
def client():
    """Fixture to create a test client for Flask app."""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Set up the database before running tests
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up after tests


def test_healthz_success(client):
    """Test successful GET request to /healthz"""
    response = client.get("/healthz")
    assert response.status_code == 500
    assert response.data == b""  # Flask test client returns bytes


def test_healthz_bad_request_body(client):
    """Test that sending a non-empty request body results in HTTP 400"""
    response = client.get(
        "/healthz",
        data=b'{"key": "value"}',  # Simulate raw bytes in the body
        headers={"Content-Type": "application/json"}  # Explicitly set JSON content type
    )
    assert response.status_code == 400


def test_healthz_bad_request_params(client):
    """Test that sending query parameters results in HTTP 400"""
    response = client.get("/healthz?param=value")  # Simulate a request with query parameters
    assert response.status_code == 400


def test_healthz_method_not_allowed(client):
    """Test that POST, PUT, DELETE, and PATCH return HTTP 405"""
    for method in ["post", "put", "delete", "patch"]:
        response = getattr(client, method)("/healthz")
        assert response.status_code == 405
