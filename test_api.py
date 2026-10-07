from fastapi.testclient import TestClient
import pytest
from app import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.sqlite")) as test_client:
        yield test_client


def test_crud_and_summary(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/products").json() == []
    created = client.post("/products", json={"name": " Latte ", "price_cents": 13000, "stock": 2})
    assert created.status_code == 201
    product = created.json()
    assert product["name"] == "Latte"
    assert client.get(f"/products/{product['id']}").json() == product
    assert client.patch(f"/products/{product['id']}", json={"stock": 3}).json()["stock"] == 3
    assert client.get("/summary").json() == {"products": 1, "units": 3, "value_cents": 39000, "currency": "TRY"}
    assert client.delete(f"/products/{product['id']}").status_code == 204
    assert client.get(f"/products/{product['id']}").status_code == 404
    assert client.get("/summary").json()["value_cents"] == 0


@pytest.mark.parametrize("change", [{"stock": -1}, {"name": "   "}, {"price_cents": 1.5}, {"stock": True}, {"extra": "x"}])
def test_bad_create(client, change):
    assert client.post("/products", json={"name":"Test", "price_cents":100, "stock":1, **change}).status_code == 422


def test_bad_patch_and_missing(client):
    product = client.post("/products", json={"name":"Test", "price_cents":100, "stock":1}).json()
    for changes in ({}, {"name": " "}, {"stock":None}, {"stock":-2}):
        assert client.patch(f"/products/{product['id']}", json=changes).status_code == 422
    assert client.patch("/products/999", json={"stock":2}).status_code == 404
    assert client.delete("/products/999").status_code == 404


def test_pagination_and_parameterized_sql(client):
    name = "'); DROP TABLE products; --"
    client.post("/products", json={"name":name, "price_cents":0, "stock":0})
    client.post("/products", json={"name":"Second", "price_cents":100, "stock":1})
    assert client.get("/products?limit=1&offset=1").json()[0]["name"] == "Second"
    assert client.get("/products").json()[0]["name"] == name
    assert client.get("/products?limit=101").status_code == 422


def test_database_persists_between_app_instances(tmp_path):
    path = tmp_path / "persist.sqlite"
    with TestClient(create_app(path)) as first:
        first.post("/products", json={"name":"Saved", "price_cents":100, "stock":1})
    with TestClient(create_app(path)) as second:
        assert second.get("/products").json()[0]["name"] == "Saved"
