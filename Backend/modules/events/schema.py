from pydantic import BaseModel, Field, model_validator, ConfigDict, ValidationError
from typing import List
from datetime import date, datetime
from typing import Optional

from decimal import Decimal

from shared.generic_validation import Schema_Validation, event_request_validation

from shared import generic_enum

from fastapi import HTTPException


# Category Schema


class Category_Schema(BaseModel):
    category_name: str = Field(..., min_length=3)
    category_image_url: str = Field(
        ...,
        pattern=r"^(http|https)://.*\.(jpg|jpeg|png|gif)$",
        description="Must be a valid image URL",
    )


class Category_Response(BaseModel):
    category_list: List[Category_Schema] = Field(default_factory=list)


# Participant Schema


class Participant_Schema(BaseModel):
    participant_type: generic_enum.Participant_Enum = Field(...)
    participant_count: int = Field(1, gt=0)


class Ticket_Schema(BaseModel):
    ticket_type: generic_enum.Ticket_Type_Enum = Field(...)
    ticket_fare: Decimal = Field(..., decimal_places=2, max_digits=10)
    total_tickets: int = Field(..., gt=0)


# Address Schema


class Address_Schema(BaseModel):
    street_address: str = Field(
        ..., min_length=5, max_length=255, example="123, Gandhi Street"
    )
    landmark: Optional[str] = Field(None, max_length=100, example="Near Bus Stand")
    city: str = Field(..., min_length=2, max_length=100, example="Kallakurichi")
    state: str = Field(..., min_length=2, max_length=100, example="Tamil Nadu")
    pin_code: str = Field(
        ..., min_length=4, max_length=10, example="606202"
    )  # For India (6-digit PIN)
    country: str = Field(..., min_length=2, max_length=100, example="India")

    model_config = ConfigDict(str_strip_whitespace=True)


class Event_Base_Schema(BaseModel):
    event_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Event name must be between 3-100 characters",
    )
    event_description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Event description must be 10-1000 characters",
    )
    event_image_url: str = Field(
        ...,
        pattern=r"^(http|https)://.*\.(jpg|jpeg|png|gif)$",
        description="Must be a valid image URL",
    )
    event_agenda: str = Field(
        ..., min_length=5, description="Agenda must be at least 5 characters long"
    )
    event_start_date_time: datetime = Field(
        ...,
        description="Start date and time in ISO 8601 format (e.g., 2025-04-15T09:00:00Z)",
    )
    event_end_date_time: datetime = Field(
        ...,
        description="End date and time in ISO 8601 format (e.g., 2025-04-15T12:00:00Z)",
    )

    model_config = ConfigDict(str_strip_whitespace=True)


# create event Request Schema


class Event_Request_Schema(
    Event_Base_Schema, Address_Schema, Ticket_Schema, Participant_Schema
):
    category_id: int = Field(...)

    @model_validator(mode="before")
    @classmethod
    def validate_create_event_request(cls, values):
        errors = event_request_validation.validate_data(values)

        if errors:
            raise HTTPException(status_code=422, detail=errors)

        return values


class Event_Update_Request_Schema(BaseModel):
    event_id: str = Field(...)
    event_name: str = Field(
        None,
        min_length=3,
        max_length=100,
        description="Event name must be between 3-100 characters",
    )
    event_description: str = Field(
        None,
        min_length=10,
        max_length=1000,
        description="Event description must be 10-1000 characters",
    )
    event_agenda: str = Field(
        None, min_length=5, description="Agenda must be at least 5 characters long"
    )
    event_image_url: str = Field(
        None,
        pattern=r"^(http|https)://.*\.(jpg|jpeg|png|gif)$",
        description="Must be a valid image URL",
    )

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        return Schema_Validation.check_at_least_one_field(self)


# Event table schema


class Event_Model_Schema(Event_Base_Schema, Participant_Schema, Ticket_Schema):
    event_id: bytes = Field(...)
    landmark: Optional[str] = Field(
        None, min_length=5, max_length=100, example="Near Bus Stand"
    )
    category_id: int = Field(..., gt=0)
    address_id: int = Field(..., gt=0)
    creator_id: bytes = Field(...)

    model_config = ConfigDict(extra="ignore")


# Event location Model


class Event_Location_Model_Schema(BaseModel):
    latitude: float = Field(..., description="Latitude as a floating-point number")
    longitude: float = Field(..., description="Longitude as a floating-point number")

    full_location: str = Field(..., min_length=3)

    model_config = ConfigDict(str_strip_whitespace=True)


# Event category Model ( Admin )


class Event_Category_Model_Schema(Category_Schema):
    pass


class Booking_Model_Schema(BaseModel):
    event_id: bytes = Field(..., description="binary id of the event.")
    attendee_id: bytes = Field(..., description="binary id of the attendee.")
    booking_status: bool = Field(
        ..., description="True if the attendee is confirmed, False otherwise."
    )
    scanned_at: datetime = Field(
        None, description="Timestamp of when the ticket was scanned (if applicable)."
    )
    registered_at: datetime = Field(
        None, description="Timestamp of when the user registered for the event."
    )


class Ticket_Response_Schema(Ticket_Schema):
    available_tickets: int = Field(..., gt=-1)


class Address_Response_Schema(Event_Location_Model_Schema):
    landmark: str


# Events Response Schema

# This is for the event response before login and for home page


class Event_Base_Response_Schema(Event_Base_Schema):
    event_id: str = Field(...)
    category_name: str = Field(...)
    ticket_fare: Decimal = Field(...)
    ticket_type: generic_enum.Ticket_Type_Enum = Field(...)
    total_tickets: int = Field(...)
    full_location: str = Field(...)
    latitude: float = Field(...)
    longitude: float = Field(...)

    model_config = ConfigDict(extra="ignore")


# Event Response Schema

# This is for the event response schema after login and to event details page


class Event_Response_Schema(Event_Base_Schema):
    category_name : str
    address_details: Address_Response_Schema = Field(...)
    ticket_details: Ticket_Response_Schema = Field(...)
    participant_details: Participant_Schema = Field(...)

    register_state: generic_enum.Registration_Status_Enum = Field(...)

    model_config = ConfigDict(extra="ignore")
    
# Here, after update we dont need to send category name while we already have in the client
    
class Event_Update_Response_Schema(Event_Base_Schema):
    address_details: Address_Response_Schema = Field(...)
    ticket_details: Ticket_Response_Schema = Field(...)
    participant_details: Participant_Schema = Field(...)

    register_state: generic_enum.Registration_Status_Enum = Field(...)

    model_config = ConfigDict(extra="ignore")


class Booking_Request_Schema(BaseModel):
    event_id: str


class Booing_Response_Schema(BaseModel):
    booking_id: str
    register_state: generic_enum.Registration_Status_Enum


# This is to get the list of users bookings

class User_Bookings_Response_Schema(BaseModel):
    booking_id: str
    event_id: str
    event_name: str
    event_image_url: str
    event_start_date_time: datetime
    event_end_date_time: datetime
    ticket_type: generic_enum.Ticket_Type_Enum
    ticket_fare: Decimal
    
# This is the schema after event registration
    
class User_Booking_Response_Schema(BaseModel):
    booking_id : str
    register_state : generic_enum.Registration_Status_Enum


class Event_Bookings_Response_Schema(BaseModel):
    booking_id: str
    profile_id: str
    first_name: str
    last_name: str
