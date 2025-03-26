from fastapi import APIRouter

payment_router = APIRouter()


@payment_router.post("/create_order")
def create_order():
    pass
