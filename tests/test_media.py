import pytest
from fastapi.testclient import TestClient

from app.api import media
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    media.MEDIA_DB.clear()
    yield
    media.MEDIA_DB.clear()


@pytest.fixture
def auth_header():
    return {"X-User-Id": "user123"}


def test_create_media(auth_header):
    payload = {
        "title": "Inception",
        "kind": "movie",
        "year": 2010,
        "status": "completed",
    }
    r = client.post("/media/", json=payload, headers=auth_header)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Inception"
    assert data["kind"] == "movie"
    assert data["status"] == "completed"
    assert "id" in data
    assert data["owner_id"] == "user123"


def test_create_media_without_auth():
    payload = {"title": "NoAuth", "kind": "movie", "year": 2020, "status": "planned"}
    r = client.post("/media/", json=payload)
    assert r.status_code == 401
    body = r.json()
    assert body["error"]["code"] == "http_error"
    assert "X-User-Id" in body["error"]["message"]


def test_create_media_invalid_year(auth_header):
    payload = {"title": "BadYear", "kind": "movie", "year": 1800, "status": "planned"}
    r = client.post("/media/", json=payload, headers=auth_header)
    assert r.status_code == 422


def test_list_media_filters(auth_header):
    items = [
        {"title": "Movie A", "kind": "movie", "year": 2020, "status": "completed"},
        {"title": "Course A", "kind": "course", "year": 2021, "status": "planned"},
        {"title": "Movie B", "kind": "movie", "year": 2022, "status": "watching"},
    ]
    for item in items:
        client.post("/media/", json=item, headers=auth_header)

    r = client.get("/media/?kind=movie", headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    assert all(d["kind"] == "movie" for d in data)
    assert len(data) == 2

    r2 = client.get("/media/?status=planned", headers=auth_header)
    assert r2.status_code == 200
    data2 = r2.json()
    assert len(data2) == 1
    assert data2[0]["status"] == "planned"


def test_get_media_success(auth_header):
    payload = {
        "title": "Interstellar",
        "kind": "movie",
        "year": 2014,
        "status": "completed",
    }
    r = client.post("/media/", json=payload, headers=auth_header)
    media_id = r.json()["id"]

    r2 = client.get(f"/media/{media_id}", headers=auth_header)
    assert r2.status_code == 200
    data = r2.json()
    assert data["id"] == media_id
    assert data["title"] == "Interstellar"


def test_get_media_forbidden(auth_header):
    payload = {"title": "Private", "kind": "movie", "year": 2020, "status": "completed"}
    r = client.post("/media/", json=payload, headers=auth_header)
    media_id = r.json()["id"]

    other_header = {"X-User-Id": "other"}
    r2 = client.get(f"/media/{media_id}", headers=other_header)
    assert r2.status_code == 403


def test_update_media(auth_header):
    r = client.post(
        "/media/",
        json={"title": "Old", "kind": "movie", "year": 2020, "status": "planned"},
        headers=auth_header,
    )
    media_id = r.json()["id"]

    r2 = client.put(
        f"/media/{media_id}",
        json={"title": "New title", "status": "completed"},
        headers=auth_header,
    )
    assert r2.status_code == 200
    data = r2.json()
    assert data["title"] == "New title"
    assert data["status"] == "completed"


def test_delete_media(auth_header):
    r = client.post(
        "/media/",
        json={"title": "ToDelete", "kind": "course", "year": 2021, "status": "planned"},
        headers=auth_header,
    )
    media_id = r.json()["id"]

    r2 = client.delete(f"/media/{media_id}", headers=auth_header)
    assert r2.status_code == 204

    r3 = client.get(f"/media/{media_id}", headers=auth_header)
    assert r3.status_code == 404


def test_delete_media_forbidden(auth_header):
    r = client.post(
        "/media/",
        json={"title": "Secret", "kind": "movie", "year": 2020, "status": "planned"},
        headers=auth_header,
    )
    media_id = r.json()["id"]

    other_header = {"X-User-Id": "intruder"}
    r2 = client.delete(f"/media/{media_id}", headers=other_header)
    assert r2.status_code == 403
