from database import Base

from shared import generic_enum
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DECIMAL,
    Float,
    DateTime,
    TIMESTAMP,
    ForeignKey,
    Enum,
    CheckConstraint,
    BINARY,
    UniqueConstraint,
    BOOLEAN,
)
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from . import schema
from shared.generic_dao import Base_Dao
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.users.models import UsersModel


class Event_Category_Model(Base):

    __tablename__ = "event_categories"

    category_id = Column(Integer, autoincrement=True, nullable=True, primary_key=True)
    category_name = Column(String(255), nullable=False)
    category_image_url = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP, nullable=True, onupdate=func.now()
    )  # Updates on modification

    # Relationship with Events_Model

    events = relationship(
        "Events_Model", back_populates="category", cascade="all, delete-orphan"
    )


class Event_Location_Model(Base):

    __tablename__ = "event_location"

    address_id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    full_location = Column(String(255), nullable=False, unique=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationship with Events_Model

    events = relationship(
        "Events_Model", back_populates="address", cascade="all, delete-orphan"
    )


class Events_Model(Base):

    __tablename__ = "events"

    event_id = Column(BINARY(16), nullable=True, primary_key=True)
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text, nullable=False)
    event_image_url = Column(String(255), nullable=False)
    event_agenda = Column(Text, nullable=False)
    event_start_date_time = Column(DateTime, nullable=False)
    event_end_date_time = Column(DateTime, nullable=False)
    landmark = Column(String(255), nullable=True)

    ticket_type = Column(Enum(generic_enum.Ticket_Type_Enum), nullable=False)
    ticket_fare = Column(DECIMAL(10, 2), nullable=True)
    total_tickets = Column(Integer, nullable=False)

    participant_type = Column(Enum(generic_enum.Participant_Enum), nullable=False)
    participant_count = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP, nullable=True, onupdate=func.now(), server_default=func.now()
    )  # Updates on modification

    category_id = Column(
        Integer, ForeignKey("event_categories.category_id"), nullable=False
    )
    address_id = Column(
        Integer, ForeignKey("event_location.address_id"), nullable=False
    )
    creator_id = Column(BINARY(16), ForeignKey("users.user_id"), nullable=False)

    # Relationships

    category = relationship("Event_Category_Model", back_populates="events")
    address = relationship("Event_Location_Model", back_populates="events")
    creator = relationship("UsersModel")
    bookings = relationship(
        "Event_Bookings_Model", back_populates="event", cascade="all, delete"
    )
    __table_args__ = (
        CheckConstraint(
            "ticket_fare > 0", name="check_ticket_fare_positive"
        ),  # Ensures non-negative fare
        CheckConstraint(
            "total_tickets > 0", name="check_total_tickets_positive"
        ),  # Ensures at least 1 ticket
        CheckConstraint(
            "participant_count > 0", name="check_participant_count_positive"
        ),  # Ensures at least 1 ticket
    )


class Event_Bookings_Model(Base):

    __tablename__ = "event_bookings"

    booking_id = Column(Integer, autoincrement=True, primary_key=True)
    event_id = Column(
        BINARY(16), ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False
    )
    attendee_id = Column(
        BINARY(16), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    booking_status = Column(BOOLEAN, nullable=False)
    scanned_at = Column(TIMESTAMP, nullable=True)
    registered_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    attendee = relationship("UsersModel", back_populates="bookings")
    event = relationship("Events_Model", back_populates="bookings")

    __table_args__ = (
        UniqueConstraint("attendee_id", "event_id", name="uq_user_event"),
    )


class Event_Dao(Base_Dao):

    def __init__(self, model):
        super().__init__(model)


class Event_Bookings_Dao(Base_Dao):

    def __init__(self, model):
        super().__init__(model)

    def get_user_booking_data(self, user_id, event_id):

        try:
            with Base_Dao.session() as db:

                booking_data = (
                    db.query(self.model)
                    .filter(
                        getattr(self.model, user_id) == user_id
                        and getattr(self.model, event_id) == event_id
                    )
                    .first()
                )

                if not booking_data:

                    return None

                return booking_data.__dict__

        except SQLAlchemyError as e:

            raise e

    def get_event_booking_data(self, event_id):

        try:

            with Base_Dao.session() as db:

                booking_data_list = (
                    db.query(self.model)
                    .filter(
                        getattr(self.model, "event_id") == event_id
                        and getattr(self.model, "booking_status") == True
                    )
                    .all()
                )

                if not booking_data_list:
                    return None

                booking_data_list = [data.__dict__ for data in booking_data_list]

                return booking_data_list

        except SQLAlchemyError as e:

            raise e


class Category_Dao(Base_Dao):

    def __init__(self, model):
        super().__init__(model)


class Location_Dao(Base_Dao):

    def __init__(self, model):
        super().__init__(model)


category_dao = Category_Dao(Event_Category_Model)
location_dao = Location_Dao(Event_Location_Model)
events_dao = Event_Dao(Events_Model)
bookings_dao = Event_Bookings_Dao(Event_Bookings_Model)
