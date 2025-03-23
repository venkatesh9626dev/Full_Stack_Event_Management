from database import Base,SessionLocal
from sqlalchemy import Column,Text,Date,TIMESTAMP,String,BINARY,ForeignKey,Enum as sqlEnum,Date
from  sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import EmailType
from sqlalchemy.sql import func
from enum import Enum

from pydantic import EmailStr

from . import schema as users_schema
from utils import binaryConversion

from uuid import uuid4

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.events.models import Events_Model, Event_Bookings_Model



class GenderEnum(Enum):
    male = "male"
    female = "female"
    other = "other"


class UsersModel(Base):
    __tablename__ = "users"
    
    user_id = Column(BINARY(16),primary_key=True,nullable=False)
    email = Column(EmailType,nullable=False,unique=True)
    password = Column(String(255),nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # relationship with profile table
    
    profile = relationship("ProfileModel",back_populates="users",uselist=False,cascade="all, delete-orphan")
    events = relationship("Events_Model",cascade="all, delete-orphan", back_populates="creator")
    bookings = relationship("Event_Bookings_Model",cascade="all, delete-orphan", back_populates="attendee")
class ProfileModel(Base):
    __tablename__ = "profile"
    
    profile_id = Column(BINARY(16),primary_key=True, nullable=False)
    user_id = Column(BINARY(16),ForeignKey("users.user_id"),nullable=False)
    first_name = Column(String(50), nullable=False) 
    last_name = Column(String(50), nullable=False)
    college_name = Column(String(100),nullable=False)
    gender = Column(sqlEnum(GenderEnum), nullable=True)
    photo_url = Column(String(255),nullable=True)
    about_me = Column(Text,nullable=False)
    phone_number = Column(String(20), nullable = True)
    date_of_birth = Column(Date,nullable = True)
    merchant_id = Column(String(255),nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now(),server_default=func.now())  # Updates on modification

    # relationship with profile table
    
    users = relationship("UsersModel",back_populates="profile")
    
    
class Auth_Dao:
    
    @staticmethod
    def register_user(register_credentials : users_schema.Auth_Request_Schema):

            user_uuid = binaryConversion.str_to_binary(str(uuid4()))
        
            try:
                with SessionLocal() as db:
                    
                    new_user = UsersModel(**register_credentials.model_dump(), user_id = user_uuid)
                    
                    db.add(new_user)
                    
                    db.commit()
                    
                    db.refresh(new_user) 
                    
                    return new_user  
                          
            except SQLAlchemyError as e:
                
                db.rollback()
                
                raise e
    
            
    @staticmethod
    def get_user_credentials_by_email( email : EmailStr):
        
        try:
            with SessionLocal() as db:
                
                user_row = db.query(UsersModel).filter(UsersModel.email == email).first()
                
                return user_row           
        
        except SQLAlchemyError as e:
            
            raise e
    
    @staticmethod
    def get_user_credentials_by_user_id( user_id : str):
        
        binary_id = binaryConversion.str_to_binary(user_id)
        
        try:
            with SessionLocal() as db:
                
                user_row = db.query(UsersModel).filter(UsersModel.user_id == binary_id).first()
                return user_row           
        
        except SQLAlchemyError as e:
            
            raise e
    
    
class Profile_Dao:
    
    @staticmethod
    def create_user_profile(profile_details : users_schema.Profile_Create_Request_Schema , user_uuid):
        
        try:
            profile_uuid = binaryConversion.str_to_binary(str(uuid4()))
            with SessionLocal() as db:
                
                new_profile = ProfileModel(**profile_details.model_dump(),profile_id = profile_uuid , user_id = user_uuid)

                db.add(new_profile)
                
                db.commit()
                
                db.refresh(new_profile) 
                
                return new_profile
        except SQLAlchemyError as e:
            
            db.rollback()
            
            raise e
    @staticmethod
    def update_user_profile( profile_id,update_data : users_schema.Profile_Update_Request_Schema):
        
        try:
            with SessionLocal() as db:
            
                user_profile = db.query(ProfileModel).filter(ProfileModel.profile_id == profile_id).first()
                 
                update_data = {k: v for k, v in update_data.model_dump().items() if v is not None}
                
                for k , v in update_data.items():
                    setattr(user_profile , k , v)
                
                db.commit()
                
                db.refresh(user_profile)
                
                return user_profile
        except SQLAlchemyError as e:
            
            db.rollback()
           
            raise e
        
    @staticmethod
    def get_user_profile(user_id):
        
        try:
            with SessionLocal() as db:
                
                user_profile = db.query(ProfileModel).filter(ProfileModel.user_id == user_id).first()
                
                return user_profile if user_profile else None
            
        except SQLAlchemyError as e:    
            raise e
    