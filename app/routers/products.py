from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from ..database import get_session
from ..models import Product, ProductCreate, ProductRead, ProductUpdate
from .. import crud

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product_api(payload: ProductCreate, session: Session = Depends(get_session)):
    try:
        return crud.create_product(session, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("", response_model=list[ProductRead])
def list_products_api(session: Session = Depends(get_session)):
    return crud.list_products(session)

@router.get("/{product_id}", response_model=ProductRead)
def get_product_api(product_id: int, session: Session = Depends(get_session)):
    prod = crud.get_product(session, product_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return prod

@router.put("/{product_id}", response_model=ProductRead)
def update_product_api(product_id: int, payload: ProductUpdate, session: Session = Depends(get_session)):
    try:
        return crud.update_product(session, product_id, payload)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_api(product_id: int, session: Session = Depends(get_session)):
    try:
        crud.delete_product(session, product_id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return None