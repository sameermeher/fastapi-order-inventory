from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from ..database import get_session
from ..config import settings
from ..utils.security import compute_signature, secure_compare
from .. import crud

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/payment")
async def webhook_payment(request: Request, session: Session = Depends(get_session)):
    raw = await request.body()
    provided = request.headers.get("X-Signature")
    if not provided:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Signature")
    expected = compute_signature(settings.WEBHOOK_SECRET, raw)
    if not secure_compare(expected, provided):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    # parse body after verifying signature
    data = await request.json()
    order_id = data.get("order_id")
    event = data.get("event")
    if event != "payment.succeeded":
        return {"detail": "Ignored"}
    try:
        order = crud.mark_order_paid(session, int(order_id))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return {"detail": "Payment processed", "order_id": order.id}