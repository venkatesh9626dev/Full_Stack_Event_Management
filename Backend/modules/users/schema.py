from pydantic import BaseModel, Field, EmailStr, model_validator, UUID4, StringConstraints,field_validator
from datetime import date, datetime
from typing import Optional, Annotated
import re

# Auth Related Schema

class Auth_Request_Schema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=20 , strip_whitespace=True)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,20}$"
        
        if not re.fullmatch(pattern, password):
            raise ValueError(
                "Password must be 8-20 characters long and include at least:\n"
                "- One uppercase letter\n"
                "- One lowercase letter\n"
                "- One digit\n"
                "- One special character (@$!%*?&)"
            )
        return password
    
    model_config = {
        "frozen": False  # Equivalent to `allow_mutation=True`
    }

class Auth_Response_Schema(BaseModel):
    email: EmailStr

# Common user profile schema

class Profile_Schema(BaseModel):
    first_name: Annotated[
        str, 
        StringConstraints(min_length=2, max_length=30, pattern=r"^[A-Za-z]+$" , strip_whitespace=True)
    ]
    
    last_name: Annotated[
        str, 
        StringConstraints(min_length=2, max_length=30, pattern=r"^[A-Za-z]+$" , strip_whitespace=True)
    ]
    
    college_name: Annotated[
        str, 
        StringConstraints(min_length=3, max_length=100 , strip_whitespace=True)
    ]
    
    gender: Optional[Annotated[
        str, 
        StringConstraints(pattern=r"^(male|female|other)$")
    ]] = None
    
    photo_url: Optional[Annotated[
        str, 
        StringConstraints(pattern=r"^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))$")
    ]] = None
    
    about_me: Optional[Annotated[
        str, 
        StringConstraints(min_length=10, max_length=500, strip_whitespace=True)
    ]] = None
        
# User Profile create Schema

class Profile_Create_Request_Schema(Profile_Schema):
    date_of_birth : Optional[date] = Field(
        None, 
        description="Date of birth in YYYY-MM-DD format."
    )
    
    phone_number: Optional[Annotated[
        str, 
        StringConstraints(pattern=r"^\+?[0-9]{10,15}$")
    ]] = None
    
    @field_validator("phone_number", mode="before")
    @classmethod
    def strip_phone_number(cls, value):
        if isinstance(value, str):
            return value.strip()  
        return value

class Profile_Create_Response_Schema(Profile_Create_Request_Schema):
    created_at: datetime = Field(..., description="Profile creation timestamp.")
    updated_at: datetime = Field(..., description="Profile Updated Timestamp")
# User Profile update and patch schema

class Profile_Update_Request_Schema(BaseModel):    
    first_name: Optional[Annotated[
        str, 
        StringConstraints(min_length=2, max_length=30, pattern=r"^[A-Za-z]+$")
    ]] = None
    
    last_name: Optional[Annotated[
        str, 
        StringConstraints(min_length=2, max_length=30, pattern=r"^[A-Za-z]+$")
    ]] = None
    
    college_name: Optional[Annotated[
        str, 
        StringConstraints(min_length=3, max_length=100)
    ]] = None
    
    gender: Optional[Annotated[
        str, 
        StringConstraints(pattern=r"^(male|female|other)$")
    ]] = None
    
    photo_url: Optional[Annotated[
        str, 
        StringConstraints(pattern=r"^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))$")
    ]] = None
    
    about_me: Optional[Annotated[
        str, 
        StringConstraints(min_length=10, max_length=500)
    ]] = None
    
    date_of_birth: Optional[date] = Field(
        None, 
        description="Date of birth in YYYY-MM-DD format."
    )
    
    phone_number: Optional[Annotated[
        str, 
        StringConstraints(pattern=r"^\+?[0-9]{10,15}$")
    ]] = None
    
    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_field(cls, data):
        if not any(data.values()):
            raise ValueError("At least one field must be provided for update.")
        return data

    

class Profile_Update_Response_Schema(Profile_Create_Response_Schema):
    pass
    
    
# specific user profile get schema

class User_Profile_Response_Schema(Profile_Schema):
    pass

# user profile get schema
    
class Profile_Response_Schema(Profile_Update_Response_Schema):
    pass
    

__all__ = ["Auth_Request_Schema","Auth_Response_Schema","Profile_Create_Request_Schema","Profile_Create_Response_Schema","Profile_Update_Request_Schema","Profile_Update_Response_Schema","User_Profile_Response_Schema","Profile_Response_Schema"]

