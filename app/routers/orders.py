from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from ..database import get_session
from ..models import Order, OrderCreate, OrderRead, OrderUpdate
from .. import crud

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order_api(payload: OrderCreate, session: Session = Depends(get_session)):
    try:
        return crud.create_order(session, payload)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/{order_id}", response_model=OrderRead)
def get_order_api(order_id: int, session: Session = Depends(get_session)):
    order = crud.get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=OrderRead)
def update_order_api(order_id: int, payload: OrderUpdate, session: Session = Depends(get_session)):
    try:
        return crud.update_order(session, order_id, payload)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_api(order_id: int, session: Session = Depends(get_session)):
    try:
        crud.delete_order(session, order_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return None