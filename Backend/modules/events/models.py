from database import Base,SessionLocal

from shared import generic_enum
from sqlalchemy import Column , String ,Text, Integer , DECIMAL , Date, TIMESTAMP, ForeignKey, Enum, CheckConstraint, BINARY, UniqueConstraint
from  sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from . import schema

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.users.models import UsersModel


class Event_Category_Model(Base):
    
    __tablename__ = "event_categories"
    
    category_id = Column(Integer , autoincrement=True , nullable=True, primary_key=True)
    category_name = Column(String(255) , nullable=False)
    category_image_url = Column(String(255) , nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())  # Updates on modification

    # Relationship with Events_Model
    
    events = relationship("Events_Model", back_populates="category", cascade="all, delete-orphan")
    
class Event_Location_Model(Base):
    
    __tablename__ = "event_addresses"
    
    address_id = Column(Integer , autoincrement=True , nullable = False, primary_key=True)
    full_address = Column(String(255) , nullable = False, unique=True)
    latitude = Column(DECIMAL(9, 6) , nullable = False)
    longitude = Column(DECIMAL(9, 6) , nullable = False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationship with Events_Model
    
    events = relationship("Events_Model", back_populates="address", cascade="all, delete-orphan")
      
class Events_Model(Base):
    
    
    __tablename__ = "events"
    
    event_id = Column(BINARY, nullable=True, primary_key=True)
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text , nullable=False)
    event_image = Column(String(255), nullable=False)
    event_agenda = Column(Text, nullable=False)
    event_date = Column(Date, nullable=False)
    event_start_time = Column(TIMESTAMP, nullable= False)
    landmark = Column(String(255), nullable=True)
    event_end_time = Column(TIMESTAMP, nullable= False)
    
    ticket_type = Column(Enum(generic_enum.Ticket_Type_Enum), nullable=False)
    ticket_fare = Column(DECIMAL(10,2), nullable=True)
    total_tickets = Column(Integer, nullable=False)
    
    
    participant_type = Column(Enum(generic_enum.Participant_Enum), nullable=False)
    participant_count = Column(Integer, nullable=True)
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())  # Updates on modification
    
    category_id = Column(Integer, ForeignKey("event_categories.category_id"), nullable=False)
    address_id = Column(Integer, ForeignKey("event_addresses.address_id"), nullable=False)
    creator_id= Column(BINARY,ForeignKey("users.user_id"), nullable=False )
    
    # Relationships
    
    category = relationship("Event_Category_Model", back_populates="events")
    address = relationship("Event_Location_Model", back_populates="events")
    creator = relationship("UsersModel")
    bookings = relationship("Event_Bookings_Model", back_populates="event")
    __table_args__ = (
        CheckConstraint("ticket_fare > 0", name="check_ticket_fare_positive"),  # Ensures non-negative fare
        CheckConstraint("total_tickets > 0", name="check_total_tickets_positive"),  # Ensures at least 1 ticket
        CheckConstraint("participant_count > 0", name="check_participant_count_positive"),  # Ensures at least 1 ticket

    )
    
class Event_Bookings_Model(Base):
    
    __tablename__ = "event_bookings"
    
    booking_id = Column(Integer, autoincrement=True, primary_key=True)
    event_id = Column(BINARY, ForeignKey("events.event_id"), nullable=False)
    attendee_id  = Column(BINARY, ForeignKey("users.user_id"), nullable=False)
    ticket_status = Column(Enum(generic_enum.Ticket_Status), nullable=False, default=generic_enum.Ticket_Status.VALID)
    ticket_qr_code = Column(String(255), nullable=False)
    registered_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    attendee = relationship("UsersModel", back_populates="bookings")
    event = relationship("Events_Model", back_populates="bookings")
    
    __table_args__ = (UniqueConstraint("attendee_id", "event_id", name="uq_user_event"),)
    
class Event_Dao:

        
     def create_event(event_data : schema.Event_Model_Schema):
        
        try:
            with SessionLocal() as db:
                
                new_event = Events_Model(**event_data.model_dump())
                
                db.add(new_event)
                
                db.commit()
                
                db.refresh(new_event)
                
                return new_event
        
        except SQLAlchemyError as e:
            
            db.rollback()
            
            raise e
        
     def update_event(update_data : schema.Event_Update_Request_Schema):
        
        event_id = update_data.event_id
        
        try:
            with SessionLocal() as db:
            
                event = db.query(Events_Model).filter(Events_Model.event_id == event_id).first()
                
                for key, value in update_data.model_dump(exclude_unset=True).items():
                    setattr(event, key, value)
                    
                db.commit()
                
                db.refresh(event)
                
                return event
        
        except SQLAlchemyError as e:
            
            db.rollback()
            
            raise e 
    
     def get_events():
        
        try:
            
            with SessionLocal() as db:
                
                events_list = db.query(Events_Model).all()
                
                return events_list
            
        except SQLAlchemyError as e:
            
            raise e
        
     def get_event_by_id(event_id : bytes):
        
        try:
            with SessionLocal() as db:
            
                event_data = db.query(Events_Model).filter(Events_Model.event_id == event_id).first()
                
                return event_data
        except SQLAlchemyError as e:

            raise e
        
            
     def get_events_by_ids(event_id_list : list[bytes]):
        
        try:
            with SessionLocal() as db:
            
                event_data_list = db.query(Events_Model).filter(Events_Model.event_id in(event_id_list)).first()
                
                return event_data_list
        except SQLAlchemyError as e:

            raise e
        
class Event_Bookings_Dao:
    
     def register_attendee(booking_data):
        
        try:
            with SessionLocal() as db:
                
                new_attendee = Event_Bookings_Model(event_id = booking_data.event_id, attendee_id = booking_data.creator_id, ticket_qr_code = booking_data.qr_code_url )
                
                db.add(new_attendee)
                
                db.commit()
                
                db.refresh(new_attendee)
                
                return new_attendee
                
        except SQLAlchemyError as e:

            raise e 
    
     def get_attendee_ids(event_id : bytes):
        
        try:
            with SessionLocal() as db:
            
                attendee_id = db.query(Event_Bookings_Model.attendee_id).filter(Event_Bookings_Model.event_id == event_id).all()
                
                return attendee_id
        except SQLAlchemyError as e:

            raise e
        
     def get_user_bookings(user_id):
        
        try:
            with SessionLocal() as db:
            
                user_bookings = db.query(Event_Bookings_Model).filter(Event_Bookings_Model.user_id == user_id).all()
                
                return user_bookings
            
        except SQLAlchemyError as e:

            raise e
        

class Category_Dao:
    
     def create_category(category_data : schema.Event_Category_Model_Schema):
        
        try:
            with SessionLocal() as db:
            
                new_category = Event_Category_Model(**category_data.model_dump())
                
                db.commit()
                
                db.refresh(new_category)
                
                return new_category        
        except SQLAlchemyError as e:
            
            db.rollback()
            
            raise e
    
     def get_categories():
        
        with SessionLocal() as db:
            
            category_list = db.query(Event_Category_Model).all()
            
            return category_list

     def get_category_by_name(category_name : str):
        
        with SessionLocal() as db:
            
            category_data = db.query(Event_Category_Model).filter(Event_Category_Model.category_name == category_name).first()
            
            return category_data
        
class Location_Dao:
    
     def create_location_data(location_data : schema.Event_Location_Model_Schema):
        
        try:
            with SessionLocal() as db:
                
                new_location = Event_Location_Model(**location_data.model_dump())
                
                db.add(new_location)
                
                db.commit()
                
                db.refresh(new_location)
                
                return new_location
        
        except SQLAlchemyError as e:
            
            db.rollback()
            
            raise e
        
     def get_location_by_name(full_location : str):
        
        try:
            with SessionLocal() as db:
            
                location_data = db.query(Event_Location_Model).filter(Event_Location_Model.full_location == full_location).first()
                
                return location_data
            
        except SQLAlchemyError as e:
            
            raise e
    
     def get_location_by_id(location_id : int):
        
        try:
            with SessionLocal() as db:
            
                location_row = db.query(Event_Location_Model).filter(Event_Location_Model.location_id == location_id).first()
                
                return location_row
        except SQLAlchemyError as e:

            raise e