from database import Base

from datetime import datetime

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
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from . import schema
from shared.generic_dao import Base_Dao

from modules.users.models import UsersModel, ProfileModel


class Event_Category_Model(Base):

    __tablename__ = "event_categories"

    category_id = Column(Integer, autoincrement=True, nullable=True, primary_key=True)
    category_name = Column(String(255), nullable=False)
    category_image_url = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP, nullable=True, onupdate=func.now()
    )  # Updates on modification



class Event_Location_Model(Base):

    __tablename__ = "event_location"

    address_id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    full_location = Column(String(255), nullable=False, unique=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())



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

    __table_args__ = (
        UniqueConstraint("attendee_id", "event_id", name="uq_user_event"),
    )


class Event_Dao(Base_Dao):

    def __init__(self, event_model, location_model):
        super().__init__(event_model)
        self.location_model = location_model
        
    def get_event_data_by_id(self, event_id):
        
        try:
            with Base_Dao.session() as db:
                
                event_data_tuple = db.query(self.model,self.location_model).join(self.location_model,self.model.address_id == self.location_model.address_id).filter(self.model.event_id == event_id).first()
                
                return {**event_data_tuple[0]._asdict(), **event_data_tuple[1]._asdict()}

                
        except SQLAlchemyError as e:

            raise e 
        
    def get_events(self):
        
        try:
            with Base_Dao.session() as db:

                records_object_list = (
                    db.query(self.model.event_name,self.model.event_id,self.model.event_image,self.model.event_start_date_time,self.model.event_end_date_time,self.model.ticket_fare,self.model.ticket_type,self.location_model.full_location)
                    .join(self.location_model, self.model.address_id == self.location_model.address_id)
                    .filter(self.model.event_start_date_time  > datetime.now())
                    .mappings()
                    .all()
                )

                if not records_object_list:
                    return []

                records_list = [record.__dict__ for record in records_object_list]

                return records_list
        except SQLAlchemyError as e:
            raise e


class Event_Bookings_Dao(Base_Dao):

    def __init__(self, bookings_model,event_model,profile_model):
        super().__init__(bookings_model)
        self.event_model = event_model
        self.profile_model = profile_model

    def get_user_bookings_by_event_ids(self, attendee_id, event_id_list : list): # This is used for searching bookings by event name or event_id

        try:
            with Base_Dao.session() as db:

                bookings_tuple = (
                    db.query(self.model.booking_id,self.event_model.event_id,self.event_model.event_name,self.event_model.event_image,self.event_model.event_start_date_time,self.event_model.event_end_date_time,self.event_model.ticket_fare)
                    .join(self.event_model , self.model.event_id == self.event_model.event_id).filter(self.model.attendee_id == attendee_id and self.model.booking_status == True and self.model.event_id in(event_id_list)).mappings().all()
                )

                if not bookings_tuple:

                    return []
                
                return list(bookings_tuple)
            

        except SQLAlchemyError as e:

            raise e
        
    def get_user_bookings_data(self, attendee_id):

        try:

            with Base_Dao.session() as db:

                bookings_tuple = (
                    db.query(self.model.booking_id,self.event_model.event_id,self.event_model.event_name,self.event_model.event_image,self.event_model.event_start_date_time,self.event_model.event_end_date_time,self.event_model.ticket_fare)
                    .join(self.event_model , self.model.event_id == self.event_model.event_id)
                    .filter(
                        getattr(self.model, "attendee_id") == attendee_id
                        and getattr(self.model, "booking_status") == True
                    )
                    .all()
                )

                if not bookings_tuple:
                    return []
                
                return list(bookings_tuple)

        except SQLAlchemyError as e:

            raise e       

    def get_event_booking_data(self, event_id):

        try:

            with Base_Dao.session() as db:

                bookings_tuple = (
                    db.query(self.model.booking_id,self.profile_model.first_name,self.profile_model.last_name,self.profile_model.profile_id).join(self.profile_model, self.model.attendee_id == self.profile_model.user_id)  
    .filter( self.model.booking_status == True)
    .mappings()
    .all()
                )

                if not bookings_tuple:
                    return []

                return list(bookings_tuple)

        except SQLAlchemyError as e:

            raise e
        
    def get_event_bookings_count(self,event_id): # This is to find the count of total bookings
        pass


class Category_Dao(Base_Dao):

    def __init__(self, model):
        super().__init__(model)


class Location_Dao(Base_Dao):

    def __init__(self, model):
        super().__init__(model)


category_dao = Category_Dao(Event_Category_Model)
location_dao = Location_Dao(Event_Location_Model)
events_dao = Event_Dao(Events_Model,Event_Location_Model)
bookings_dao = Event_Bookings_Dao(Event_Bookings_Model,Events_Model,ProfileModel)
