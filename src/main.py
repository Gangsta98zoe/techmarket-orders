from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime
import os

app = FastAPI(
    title="TechMarket Orders API",
    description="Microservicio de gestión de pedidos - TechMarket",
    version=os.getenv("APP_VERSION", "1.0.0"),
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "blue")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

orders_db: dict = {}


class OrderItem(BaseModel):
    product_id: str
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    customer_id: str
    items: list[OrderItem]
    shipping_address: str


class Order(BaseModel):
    order_id: str
    customer_id: str
    items: list[OrderItem]
    shipping_address: str
    total: float
    status: str
    created_at: str
    environment: str
    version: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "version": APP_VERSION,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


@app.get("/info")
def info():
    return {
        "service": "TechMarket Orders",
        "environment": ENVIRONMENT,
        "version": APP_VERSION,
        "deployment_strategy": "Blue-Green",
    }


@app.post("/orders", response_model=Order, status_code=201)
def create_order(order: OrderCreate):
    order_id = str(uuid.uuid4())
    total = sum(item.quantity * item.unit_price for item in order.items)
    new_order = Order(
        order_id=order_id,
        customer_id=order.customer_id,
        items=order.items,
        shipping_address=order.shipping_address,
        total=round(total, 2),
        status="pending",
        created_at=datetime.datetime.utcnow().isoformat(),
        environment=ENVIRONMENT,
        version=APP_VERSION,
    )
    orders_db[order_id] = new_order
    return new_order


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]


@app.get("/orders")
def list_orders():
    return {
        "total": len(orders_db),
        "orders": list(orders_db.values()),
        "environment": ENVIRONMENT,
        "version": APP_VERSION,
    }


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: str, status: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {valid_statuses}")
    orders_db[order_id].status = status
    return {"order_id": order_id, "status": status, "updated": True}
