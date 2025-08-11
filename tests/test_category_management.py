import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.models.user import User
from app.db.models.category import Category
from app.schemas.category_dto import CategoryCreateDTO, CategoryUpdateDTO

client = TestClient(app)


@pytest.fixture
def db_session():
    # Implement or import a fixture that returns a SQLAlchemy session
    ...


def test_create_category(client, auth_headers):
    payload = {"name": "Groceries", "color": "#00FF00", "icon": "shopping-cart"}
    response = client.post("/categories/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Groceries"
    assert data["color"] == "#00FF00"
    assert data["icon"] == "shopping-cart"
    assert "id" in data


def test_get_categories(client, auth_headers):
    # Create a category first
    client.post("/categories/", json={"name": "Bills"}, headers=auth_headers)
    response = client.get("/categories/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(cat["name"] == "Bills" for cat in data)


def test_update_category(client, auth_headers):
    # Create a category
    create_resp = client.post(
        "/categories/", json={"name": "Travel"}, headers=auth_headers
    )
    category_id = create_resp.json()["id"]
    # Update it
    update_payload = {"name": "Vacation", "color": "#123456"}
    response = client.put(
        f"/categories/{category_id}", json=update_payload, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Vacation"
    assert data["color"] == "#123456"


def test_delete_category(client, auth_headers):
    # Create a category
    create_resp = client.post(
        "/categories/", json={"name": "ToDelete"}, headers=auth_headers
    )
    category_id = create_resp.json()["id"]
    # Delete it
    response = client.delete(f"/categories/{category_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Category deleted successfully"
    # Ensure it's gone
    get_resp = client.get("/categories/", headers=auth_headers)
    assert all(cat["id"] != category_id for cat in get_resp.json())
