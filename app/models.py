from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"

class ProductBase(SQLModel):
    sku: str = Field(index=True, unique=True)
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    orders: list["Order"] = Relationship(back_populates="product")

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int

class ProductUpdate(SQLModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)

class OrderBase(SQLModel):
    product_id: int = Field(foreign_key="product.id", index=True)
    quantity: int = Field(gt=0)
    status: OrderStatus = Field(default=OrderStatus.PENDING)

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    product: Optional[Product] = Relationship(back_populates="orders")

class OrderCreate(SQLModel):
    product_id: int
    quantity: int

class OrderRead(OrderBase):
    id: int
    created_at: datetime

class OrderUpdate(SQLModel):
    quantity: Optional[int] = Field(default=None, gt=0)
    status: Optional[OrderStatus] = None