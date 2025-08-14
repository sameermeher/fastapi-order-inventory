from typing import Optional, List
from sqlmodel import select
from sqlmodel import Session
from .models import Product, ProductCreate, ProductUpdate, Order, OrderCreate, OrderUpdate, OrderStatus

# Products
def create_product(session: Session, data: ProductCreate) -> Product:
    # unique SKU check
    if session.exec(select(Product).where(Product.sku == data.sku)).first():
        raise ValueError("SKU already exists")
    prod = Product(**data.model_dump())
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return prod

def list_products(session: Session) -> List[Product]:
    return session.exec(select(Product)).all()

def get_product(session: Session, product_id: int) -> Optional[Product]:
    return session.get(Product, product_id)

def update_product(session: Session, product_id: int, data: ProductUpdate) -> Product:
    prod = session.get(Product, product_id)
    if not prod:
        raise LookupError("Product not found")
    if data.sku and data.sku != prod.sku:
        if session.exec(select(Product).where(Product.sku == data.sku)).first():
            raise ValueError("SKU already exists")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(prod, k, v)
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return prod

def delete_product(session: Session, product_id: int) -> bool:
    prod = session.get(Product, product_id)
    if not prod:
        raise LookupError("Product not found")
    session.delete(prod)
    session.commit()
    return True

# Orders
def create_order(session: Session, data: OrderCreate) -> Order:
    prod = session.get(Product, data.product_id)
    if not prod:
        raise LookupError("Product not found")
    if prod.stock < data.quantity:
        raise ValueError("Insufficient stock")
    # atomic-ish in SQLite: same transaction
    prod.stock -= data.quantity
    order = Order(product_id=prod.id, quantity=data.quantity, status=OrderStatus.PENDING)
    session.add(order)
    session.add(prod)
    session.commit()
    session.refresh(order)
    return order

def get_order(session: Session, order_id: int) -> Optional[Order]:
    return session.get(Order, order_id)

def update_order(session: Session, order_id: int, data: OrderUpdate) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise LookupError("Order not found")
    # status transitions
    if data.status is not None:
        if data.status == OrderStatus.SHIPPED and order.status != OrderStatus.PAID:
            raise ValueError("Order must be PAID before SHIPPED")
        if order.status == OrderStatus.CANCELED:
            raise ValueError("Cannot change a CANCELED order")
        if order.status == OrderStatus.SHIPPED:
            raise ValueError("Cannot change a SHIPPED order")
        order.status = data.status
    if data.quantity is not None:
        if data.quantity <= 0:
            raise ValueError("Quantity must be > 0")
        delta = data.quantity - order.quantity
        if delta != 0:
            prod = session.get(Product, order.product_id)
            if delta > 0 and prod.stock < delta:
                raise ValueError("Insufficient stock for quantity increase")
            prod.stock -= delta
            session.add(prod)
        order.quantity = data.quantity
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def delete_order(session: Session, order_id: int) -> bool:
    order = session.get(Order, order_id)
    if not order:
        raise LookupError("Order not found")
    if order.status != OrderStatus.PENDING:
        raise ValueError("Only PENDING orders can be deleted")
    # return stock
    prod = session.get(Product, order.product_id)
    prod.stock += order.quantity
    session.delete(order)
    session.add(prod)
    session.commit()
    return True

def mark_order_paid(session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise LookupError("Order not found")
    if order.status == OrderStatus.PAID:
        return order  # idempotent
    if order.status != OrderStatus.PENDING:
        raise ValueError("Only PENDING orders can be marked PAID")
    order.status = OrderStatus.PAID
    session.add(order)
    session.commit()
    session.refresh(order)
    return order