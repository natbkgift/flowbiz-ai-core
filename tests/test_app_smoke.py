from fastapi.testclient import TestClient

from apps.api.main import app


def test_root_endpoint_returns_placeholder_message():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "FlowBiz AI Core API"}
