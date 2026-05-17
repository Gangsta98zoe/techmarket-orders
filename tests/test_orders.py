import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "TechMarket Orders"
    assert data["deployment_strategy"] == "Blue-Green"


def test_create_order():
    payload = {
        "customer_id": "cust-001",
        "items": [
            {"product_id": "prod-123", "quantity": 2, "unit_price": 29.99},
            {"product_id": "prod-456", "quantity": 1, "unit_price": 15.00},
        ],
        "shipping_address": "Av. Providencia 1234, Santiago",
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == "cust-001"
    assert data["total"] == 74.98
    assert data["status"] == "pending"
    assert "order_id" in data


def test_get_order():
    payload = {
        "customer_id": "cust-002",
        "items": [{"product_id": "prod-789", "quantity": 1, "unit_price": 50.00}],
        "shipping_address": "Calle Mayor 5, Valparaíso",
    }
    create_resp = client.post("/orders", json=payload)
    order_id = create_resp.json()["order_id"]

    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["order_id"] == order_id


def test_get_order_not_found():
    response = client.get("/orders/nonexistent-id")
    assert response.status_code == 404


def test_list_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    assert "total" in response.json()
    assert "orders" in response.json()


def test_update_order_status():
    payload = {
        "customer_id": "cust-003",
        "items": [{"product_id": "prod-001", "quantity": 3, "unit_price": 10.00}],
        "shipping_address": "Los Leones 999, Santiago",
    }
    create_resp = client.post("/orders", json=payload)
    order_id = create_resp.json()["order_id"]

    response = client.put(f"/orders/{order_id}/status", params={"status": "confirmed"})
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_update_invalid_status():
    payload = {
        "customer_id": "cust-004",
        "items": [{"product_id": "prod-002", "quantity": 1, "unit_price": 5.00}],
        "shipping_address": "Dirección Test 1",
    }
    create_resp = client.post("/orders", json=payload)
    order_id = create_resp.json()["order_id"]

    response = client.put(f"/orders/{order_id}/status", params={"status": "invalid-status"})
    assert response.status_code == 400
