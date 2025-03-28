from . import models

from uuid import uuid4

import requests

from fastapi import HTTPException, status

from . import schema as event_schema

from . import validator

from shared import generic_enum

from utils import string_utils, binaryConversion

from settings import settings

from datetime import datetime


class Category_Class:

    def __init__(self, category_dao):
        self.category_dao = category_dao

    def create_category(self, category_data):

        return self.category_dao.create_record(category_data.model_dump())

    def get_categories(self):

        category_list = self.category_dao.fetch_records_from_model()

        return category_list

    def get_category_by_name(self, category_name: str):

        category_data = self.category_dao.fetch_records_by_field_name(
            field_name="category_name", field_value=category_name
        )

        return category_data


# Location Related Class


class Location_Class:

    def __init__(self, location_schema, location_dao):

        self.location_schema = location_schema
        self.location_dao = location_dao

    def get_coords(self, address: str):

        api_key = settings.GEOCODING_API_KEY

        api_url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"

        try:
            api_response = requests.get(api_url)
            api_response.raise_for_status()

            response_dict = api_response.json()

            lon, lat = response_dict["features"][0]["geometry"]["coordinates"]

            return {"latitude": lat, "longitude": lon}

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Catches 4xx/5xx errors
        except requests.exceptions.RequestException as err:
            print(f"Request failed: {err}")  # Catches other request errors

    def create_location_data(self, full_location: str):

        coords = self.get_coords(full_location)

        location_data = self.location_schema(**coords, full_location=full_location)

        inserted_data = self.location_dao.create_record(location_data.model_dump())

        return inserted_data

    def get_location_by_name(self, location_name):

        location_data = self.location_dao.get_record(
            field_name="full_location", field_value=location_name
        )

        return location_data

    def get_location_by_id(self, location_id):

        location_data = self.location_dao.get_record(
            field_name="location_id", field_value=location_id
        )

        return location_data


class Bookings_Class:

    def __init__(self, bookings_dao, event_dao,time_validator):
        self.bookings_dao = bookings_dao
        self.event_dao = event_dao
        self.time_validator = time_validator

    def get_attendee_bookings_by_event_list(self, event_id_list, attendee_id): # This is used for searching bookings by event name or event_id

        attendee_bookings_list = self.bookings_dao.get_user_bookings_by_event_ids(attendee_id, event_id_list)

        if not attendee_bookings_list:
            return []
        
        return [{**data,"booking_id":binaryConversion.binary_to_str(data["booking_id"]),"event_id":binaryConversion.binary_to_str(data["event_id"])} for data in attendee_bookings_list]

    
    def get_attendee_bookings(self,attendee_id):
        
        attendee_bookings_list = self.bookings_dao.get_user_bookings_data(attendee_id)
        
        if not attendee_bookings_list:
            return []
        
        return [{**data,"booking_id":binaryConversion.binary_to_str(data["booking_id"]),"event_id":binaryConversion.binary_to_str(data["event_id"])} for data in attendee_bookings_list]
    def get_attendee_booking_status(self, event_id, attendee_id):

        attendee_data = self.get_attendee_booking_data(event_id, attendee_id)

        if not attendee_data :

            return generic_enum.Registration_Status_Enum.NOT_REGISTERED.value

        return generic_enum.Registration_Status_Enum.REGISTERED.value

    def get_available_bookings(self, event_id, total_tickets):

        bookings_count = self.bookings_dao.get_event_bookings_count(event_id)

        available_tickets = total_tickets - bookings_count

        return available_tickets

    def get_event_booking_data(self, event_id, creator_id):
        
        validator.events_validator.validate_event_exists(event_id)
        
        validator.creator_validator.validate_creator(event_id, creator_id)

        event_bookings_list = self.bookings_dao.get_event_booking_data(event_id)

        if event_bookings_list:
            return []
        return [{**data,"booking_id":binaryConversion.binary_to_str(data["booking_id"]),"profile_id":binaryConversion.binary_to_str(data["profile_id"])} for data in event_bookings_list]

    def register_attendee(self, event_id, attendee_id):

        event_data = self.event_dao.get_record(
            field_name="event_id", field_value=event_id
        )
        
        if not event_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="The event is not found")

        self.time_validator.event_registration_expiry_check(event_start_datetime=event_data["event_start_datetime"])
        
        available_tickets = self.get_available_bookings(
            event_data["event_id"], event_data["total_tickets"]
        )
        
        ticket_type = event_data["ticket_type"]

        if available_tickets == 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There are no tickets available for this event",
            )

        booking_data = self.get_attendee_booking_data(event_id, attendee_id)

        if booking_data:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already registered in this event",
            )

        elif booking_data:
            pass  # connect this with transaction
        
        elif  ticket_type == generic_enum.Ticket_Type_Enum.FREE:

            booking_data = event_schema.Booking_Model_Schema(event_id=event_id,attendee_id=attendee_id,booking_status=True,registered_at=datetime.now())

            new_booking = self.bookings_dao.create_record(**booking_data.model_dump())
            
            return {"booking_id" : new_booking["booking_id"],"register_state" : generic_enum.Registration_Status_Enum.REGISTERED.value}

        elif ticket_type == generic_enum.Ticket_Type_Enum.PAID:
            pass # Will write later
        
# Events Related Class


class Events_Class:
    

    def __init__(
        self,
        location_service,
        bookings_service,
        category_service,
        event_dao,
        events_validator
    ):
        self.location_service = location_service
        self.bookings_service = bookings_service
        self.category_service = category_service
        self.event_dao = event_dao
        self.event_validator = events_validator

    def create_event(self, event_data: dict, creator_id):

        self.event_validator.validate_event_details(event_data, creator_id)

        address_dict = event_data["address_details"]

        ticket_dict = event_data["ticket_details"]

        participant_dict = event_data["participant_details"]

        del event_data["address_details"]
        del event_data["participant_details"]
        del event_data["ticket_details"]

        full_address = string_utils.create_full_address(address_dict)

        category_data = self.category_service.get_category_by_name(
            event_data["category_name"]
        )

        if not category_data:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The requested {event_data["category_name"]} category is not exists",
            )

        address_data = self.location_service.get_location_by_name(full_address)

        if not address_data:

            address_data = self.location_service.create_location_data(full_address)

        event_id = binaryConversion.str_to_binary(str(uuid4()))

        event_schema_object = event_schema.Event_Model_Schema(
            **event_data,
            **ticket_dict,
            **participant_dict,
            landmark=address_dict["landmark"],
            category_id=category_data["category_id"],
            address_id=address_data["address_id"],
            creator_id=creator_id,
            event_id=event_id,
        )

        new_event_dict = self.event_dao.create_record(event_schema_object.model_dump())
    
        # default attendee
        self.bookings_service.register_attendee(new_event_dict["event_id"],creator_id)

        new_event_dict["event_id"] = binaryConversion.binary_to_str(
            new_event_dict["event_id"]
        )

        ticket_response = event_schema.Ticket_Response_Schema(
            **ticket_dict, available_tickets=ticket_dict["total_tickets"] - 1
        )

        return {
            **new_event_dict,
            "register_state": generic_enum.Registration_Status_Enum.REGISTERED.value,
            "address": address_data,
            "ticket_details": ticket_response,
            "participant_details": participant_dict,
        }
        
    def update_event(self,update_data : dict, creator_id):
        
        event_binary_id = binaryConversion.str_to_binary(update_data["event_id"])
        
        validator.events_validator.validate_event_exists(event_binary_id)
        validator.creator_validator.validate_creator_match(event_id=event_binary_id, creator_id=creator_id)
        
        update_data["event_id"] = event_binary_id
        
        updated_data = self.event_dao.update_record(data=update_data, field_name = "event_id", field_value = event_binary_id)

        address_details = event_schema.Address_Schema(**self.location_service.get_location_by_id(updated_data["address_id"]))
        
        participant_details = event_schema.Participant_Schema(participant_type=updated_data["participant_type"],participant_count=updated_data["participant_count"])
        
        available_tickets = self.bookings_service.get_available_bookings
        
        ticket_details = event_schema.Ticket_Response_Schema(ticket_type=updated_data["ticket_type"],ticket_fare=updated_data["ticket_fare"],total_tickets=updated_data["total_tickets"],available_tickets=available_tickets)
        
        return {**updated_data,"address_details" : address_details, "ticket_details" : ticket_details, "participant_details" : participant_details}
    
    def get_events_list(self):

        events_list = self.event_dao.fetch_records_from_model()

        return events_list if events_list else []

    def get_event_by_id(self, byte_event_id, byte_user_id):

        event_data = self.event_dao.get_event_data_by_id(byte_event_id)

        if not event_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The Event with this ({event_data}) is not exist",
            )

        booking_status = self.bookings_service.get_attendee_booking_status(
            byte_event_id, byte_user_id
        )
        
        available_tickets = self.bookings_service.get_available_bookings
        
        ticket_details = event_schema.Ticket_Response_Schema(ticket_type=event_data["ticket_type"],ticket_fare=event_data["ticket_fare"],total_tickets=event_data["total_tickets"],available_tickets=available_tickets)
        
        participant_details = event_schema.Participant_Schema(participant_type=event_data["participant_type"],participant_count=event_data["participant_count"] )
        
        address_details = event_schema.Event_Location_Model_Schema(full_location=event_data["full_location"],latitude=event_data["latitude"],longitude=event_data["longitude"])
        
        return {**event_data,"address_details":address_details,"participant_details" : participant_details,"ticket_details" : ticket_details,"register_state" : booking_status }
        


events_validator = validator.events_validator

category_service = Category_Class(models.category_dao)
bookings_service = Bookings_Class(models.bookings_dao, models.events_dao,validator.time_validator)
location_service = Location_Class(
    event_schema.Event_Location_Model_Schema, models.location_dao
)
events_service = Events_Class(
    location_service,
    bookings_service,
    category_service,
    models.events_dao,
    events_validator
)

__all__ = ["category_service", "location_service", "events_service"]
