from fastapi import FastAPI
from .database import init_db
from .routers import products, orders, webhooks

app = FastAPI(
    title="Orders & Inventory Service",
    version="1.0.0",
    description="FastAPI microservice for products, orders, and signed payment webhooks."
)

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(webhooks.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}