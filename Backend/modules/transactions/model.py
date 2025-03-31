from database import Base, SessionLocal
from sqlalchemy import Column, BINARY, ForeignKey, String, DECIMAL, Integer, TIMESTAMP
from sqlalchemy.sql import func


class Transactions(Base):
    transaction_id = Column(BINARY, primary_key=True)
    booking_id = Column(
        Integer, ForeignKey("Event_Bookings_Model.booking_id"), nullable=False
    )
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_status = Column(String(20), default="PENDING")  # PENDING, SUCCESS, FAILED
    payment_method = Column(String(50), nullable=False)  # "razorpay", "stripe"
    gateway_transaction_id = Column(String(255), nullable=True)  # ID from Razorpay
    created_at = Column(TIMESTAMP, server_default=func.now())
