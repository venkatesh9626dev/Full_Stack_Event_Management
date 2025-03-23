from pydantic import BaseModel, Field ,model_validator, ConfigDict
from typing import List
from datetime import date, datetime
from typing import Optional

from decimal import Decimal

from shared.generic_validation import Schema_Validation

from shared import generic_enum

# Category Schema


class Category_Schema(BaseModel):
    category_name : str = Field(..., min_length=3 , max_length=30)
    category_image_url : str = Field(None, pattern=r"^(http|https)://.*\.(jpg|jpeg|png|gif)$", description="Must be a valid image URL")
    
    model_config = ConfigDict(str_strip_whitespace=True)

class Category_Response(BaseModel):
    
    category_list : List[Category_Schema] = Field(default_factory=list)


# Participant Schema

class Participant_Schema(BaseModel):
    
    participant_type : generic_enum.Participant_Enum = Field(...)
    participant_count : int  = Field(1, gt=0)
    
    @model_validator(mode="before")
    @classmethod
    def check_participant_details(cls , details):
        return Schema_Validation.check_participant_details(details)
    
    
class Ticket_Schema(BaseModel):
    
    ticket_type : generic_enum.Ticket_Type_Enum = Field(...)
    ticket_fare: Decimal | None = Field(None, gt=0 ,  decimal_places=2, max_digits=10)
    total_tickets : int = Field(..., gt=0)
    
    @model_validator(mode="before")
    @classmethod
    def check_ticket_details(cls ,data):
        return Schema_Validation.check_ticket_details(data)
    
   

# Address Schema 


class Address_Schema(BaseModel):
    
    street_address: str = Field(..., min_length=5, max_length=255, example="123, Gandhi Street")
    landmark: Optional[str] = Field(None, max_length=100, example="Near Bus Stand")
    city: str = Field(..., min_length=2, max_length=100, example="Kallakurichi")
    state: str = Field(..., min_length=2, max_length=100, example="Tamil Nadu")
    pin_code: str = Field(..., min_length=4, max_length=10, example="606202")  # For India (6-digit PIN)
    country: str = Field(..., min_length=2, max_length=100, example="India")
    
    model_config = ConfigDict(str_strip_whitespace=True)

class Event_Base_Schema(BaseModel):
    event_name: str = Field(..., min_length=3, max_length=100, description="Event name must be between 3-100 characters" )
    event_description: str = Field(..., min_length=10, max_length=1000, description="Event description must be 10-1000 characters")
    event_image: str = Field(..., pattern=r"^(http|https)://.*\.(jpg|jpeg|png|gif)$", description="Must be a valid image URL")
    event_agenda: str = Field(..., min_length=5, description="Agenda must be at least 5 characters long")
    event_date: date = Field(..., description="Event date should be in YYYY-MM-DD format")
    event_start_time: datetime = Field(..., description="Start time must be a valid datetime format")
    event_end_time: datetime = Field(..., description="End time must be a valid datetime format")
    
    model_config = ConfigDict(str_strip_whitespace=True)
# create event Request Schema

class Event_Request_Schema(Event_Base_Schema):
    category_name: str = Field(..., min_length=3, max_length=50, description="Category name must be between 3-50 characters")  
    address : Address_Schema = Field(...)
    ticket_details : Ticket_Schema = Field(...)
    participant_details : Participant_Schema = Field(...)
    

    
class Event_Update_Request_Schema(BaseModel):
    event_id : str = Field(...)
    event_description: str = Field(None, min_length=10, max_length=1000, description="Event description must be 10-1000 characters")
    event_agenda: str = Field(None, min_length=5, description="Agenda must be at least 5 characters long")
    event_image: str = Field(None, pattern=r"^(http|https)://.*\.(jpg|jpeg|png|gif)$", description="Must be a valid image URL")

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_field(cls , data):
        return Schema_Validation.check_at_least_one_field(data)
    
    model_config = ConfigDict(extra='ignore',str_strip_whitespace=True)
    
    
# Event table schema
    
class Event_Model_Schema(Event_Base_Schema,Participant_Schema,Ticket_Schema):
    event_id :bytes = Field(...)
    landmark: Optional[str] = Field(None, min_length=5, max_length=100, example="Near Bus Stand")
    category_id : int = Field(..., gt=0)
    address_id : int = Field(..., gt=0)
    creator_id : bytes = Field(...)
    
# Event location Model

class Event_Location_Model_Schema(BaseModel):
    
    latitude : Decimal = Field(..., decimal_places=6, max_digits=9)
    longitude : Decimal = Field(..., decimal_places=6, max_digits=9)
    
    full_address : str = Field(... , min_length=3 )
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
# Event category Model ( Admin )

class Event_Category_Model_Schema(Category_Schema):
    pass

   
    
class Ticket_Response_Schema(Ticket_Schema):
    available_tickets : int = Field(..., gt=-1)
    
# Event Response Schema

class Event_Response_Schema(Event_Base_Schema):
    event_id : str = Field(...)
    register_state : bool = Field(...)
    address : Event_Location_Model_Schema = Field(...)
    ticket_details : Ticket_Response_Schema = Field(...)
    participant_details : Participant_Schema = Field(...)

