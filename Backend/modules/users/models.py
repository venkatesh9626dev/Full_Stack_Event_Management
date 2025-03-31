from database import Base, SessionLocal
from sqlalchemy import (
    Column,
    Text,
    Date,
    TIMESTAMP,
    String,
    BINARY,
    ForeignKey,
    Enum as sqlEnum,
    Date,
)
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import EmailType
from sqlalchemy.sql import func
from enum import Enum

from pydantic import EmailStr

from . import schema as users_schema

from shared.generic_dao import Base_Dao
from utils import binaryConversion

from uuid import uuid4


class GenderEnum(Enum):
    male = "male"
    female = "female"
    other = "other"


class UsersModel(Base):
    __tablename__ = "users"

    user_id = Column(BINARY(16), primary_key=True, nullable=False)
    email = Column(EmailType, nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class ProfileModel(Base):
    __tablename__ = "profile"

    profile_id = Column(BINARY(16), primary_key=True, nullable=False)
    user_id = Column(
        BINARY(16), ForeignKey("users.user_id"), nullable=False, index=True
    )
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    college_name = Column(String(100), nullable=False)
    gender = Column(sqlEnum(GenderEnum), nullable=True)
    photo_url = Column(String(255), nullable=True)
    about_me = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    merchant_id = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP, nullable=True, onupdate=func.now(), server_default=func.now()
    )  # Updates on modification


class Auth_Dao(Base_Dao):
    def __init__(self, model):
        super().__init__(model)


class Profile_Dao(Base_Dao):
    def __init__(self, model):
        super().__init__(model)


profile_dao = Profile_Dao(ProfileModel)
auth_dao = Auth_Dao(UsersModel)
