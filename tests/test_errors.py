from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body and body["error"]["code"] == "not_found"


def test_validation_error():
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"


def test_internal_error_rfc7807():
    r = client.get("/error")
    assert r.status_code == 500
    body = r.json()

    assert "type" in body
    assert "title" in body
    assert "status" in body
    assert "detail" in body
    assert "correlation_id" in body

    assert body["detail"] == "An unexpected error occurred."
    assert "ValueError" not in str(body)
