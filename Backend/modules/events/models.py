from database import Base,SessionLocal

from shared import generic_enum
from sqlalchemy import Column , String ,Text, Integer , DECIMAL ,Float, DateTime, TIMESTAMP, ForeignKey, Enum, CheckConstraint, BINARY, UniqueConstraint
from  sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from . import schema
from shared.generic_dao import Base_Dao
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
    
    __tablename__ = "event_location"
    
    address_id = Column(Integer , autoincrement=True , nullable = False, primary_key=True)
    full_location= Column(String(255) , nullable = False, unique=True)
    latitude = Column(Float , nullable = False)
    longitude = Column(Float , nullable = False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationship with Events_Model
    
    events = relationship("Events_Model", back_populates="address", cascade="all, delete-orphan")
      
class Events_Model(Base):
    
    
    __tablename__ = "events"
    
    event_id = Column(BINARY(16), nullable=True, primary_key=True)
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text , nullable=False)
    event_image = Column(String(255), nullable=False)
    event_agenda = Column(Text, nullable=False)
    event_start_date_time = Column(DateTime, nullable= False)
    event_end_date_time = Column(DateTime, nullable= False)
    landmark = Column(String(255), nullable=True)
    
    ticket_type = Column(Enum(generic_enum.Ticket_Type_Enum), nullable=False)
    ticket_fare = Column(DECIMAL(10,2), nullable=True)
    total_tickets = Column(Integer, nullable=False)
    
    
    participant_type = Column(Enum(generic_enum.Participant_Enum), nullable=False)
    participant_count = Column(Integer, nullable=True)
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now(), server_default=func.now())  # Updates on modification
    
    category_id = Column(Integer, ForeignKey("event_categories.category_id"), nullable=False)
    address_id = Column(Integer, ForeignKey("event_location.address_id"), nullable=False)
    creator_id= Column(BINARY(16),ForeignKey("users.user_id"), nullable=False )
    
    # Relationships
    
    category = relationship("Event_Category_Model", back_populates="events")
    address = relationship("Event_Location_Model", back_populates="events")
    creator = relationship("UsersModel")
    bookings = relationship("Event_Bookings_Model", back_populates="event",cascade="all, delete" )
    __table_args__ = (
        CheckConstraint("ticket_fare > 0", name="check_ticket_fare_positive"),  # Ensures non-negative fare
        CheckConstraint("total_tickets > 0", name="check_total_tickets_positive"),  # Ensures at least 1 ticket
        CheckConstraint("participant_count > 0", name="check_participant_count_positive"),  # Ensures at least 1 ticket

    )
    

class Event_Bookings_Model(Base):
    
    __tablename__ = "event_bookings"
    
    booking_id = Column(Integer, autoincrement=True, primary_key=True)
    event_id = Column(BINARY(16), ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
    attendee_id  = Column(BINARY(16), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    scanned_at = Column(TIMESTAMP,nullable=True)
    
    registered_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    attendee = relationship("UsersModel", back_populates="bookings")
    event = relationship("Events_Model", back_populates="bookings")
    
    __table_args__ = (UniqueConstraint("attendee_id", "event_id", name="uq_user_event"),)
    
class Event_Dao(Base_Dao):
    
    def __init__(self,model):
        super().__init__(model)

        
    def create_event(self, event_data : schema.Event_Model_Schema):
        
        try:
            with SessionLocal() as db:
                
                new_event = Events_Model(**event_data.model_dump())

                db.add(new_event)
                
                db.commit()
                
                db.refresh(new_event)
                
                return new_event.__dict__
        
        except SQLAlchemyError as e:
            
            db.rollback()
            
            raise e
        
    def update_event(self, update_data : schema.Event_Update_Request_Schema):
        
        event_id = update_data.event_id
        
        try:
            with SessionLocal() as db:
            
                event = db.query(Events_Model).filter(Events_Model.event_id == event_id).first()
                
                for key, value in update_data.model_dump(exclude_unset=True).items():
                    setattr(event, key, value)
                    
                db.commit()
                
                db.refresh(event)
                
                return event.__dict__
        
        except SQLAlchemyError as e:
            
            db.rollback()
            
            raise e 
    
    def get_events(self):
        
        try:
            
            with SessionLocal() as db:
                
                events_list = db.query(Events_Model).all()
                
                if not events_list:
                    return None
                
                return [event.__dict__ for event in events_list]
            
        except SQLAlchemyError as e:
            
            raise e
        
    def get_event_by_id(self, event_id : bytes):
        
        try:
            with SessionLocal() as db:
            
                event_data = db.query(Events_Model).filter(Events_Model.event_id == event_id).first()
                
                if not event_data:
                    return None
                return event_data.__dict__
        except SQLAlchemyError as e:

            raise e
        
            
    def get_events_by_ids(self ,event_id_list : list[bytes]):
        
        try:
            with SessionLocal() as db:
            
                event_data_list = db.query(Events_Model).filter(Events_Model.event_id in(event_id_list)).all()
                
                if not event_data_list:
                    return None
                
                return event_data_list.__dict__
        except SQLAlchemyError as e:

            raise e
        
class Event_Bookings_Dao(Base_Dao):
    
     def register_attendee(self, booking_data):
        
        try:
            with SessionLocal() as db:
                
                new_attendee = Event_Bookings_Model(event_id = booking_data.event_id, attendee_id = booking_data.creator_id, ticket_qr_code = booking_data.qr_code_url )
                
                db.add(new_attendee)
                
                db.commit()
                
                db.refresh(new_attendee)
                
                return new_attendee.__dict__
                
        except SQLAlchemyError as e:

            raise e 
    
     def get_booking_data(self, user_id, event_id):
        
        try:
            with SessionLocal() as db:
                
                booking_data = db.query(Event_Bookings_Model).filter(Event_Bookings_Model.attendee_id == user_id and Event_Bookings_Model.event_id == event_id).first()
                
                if not booking_data:
                    
                    return None
                
                return booking_data.__dict__
            
        except SQLAlchemyError as e:

            raise e        

class Category_Dao(Base_Dao):
    
    def __init__(self,model):
        super().__init__(model)
        
class Location_Dao(Base_Dao):
    
    def __init__(self,model):
        super().__init__(model)    

category_dao = Category_Dao(Event_Category_Model)
location_dao = Location_Dao(Event_Location_Model)
events_dao = Event_Dao(Events_Model)
bookings_dao = Event_Bookings_Dao(Event_Bookings_Model)