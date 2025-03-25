from . import models

from uuid import uuid4

import requests

from fastapi import HTTPException, status

from . import schema as event_schema

from . import validator

from utils import string_utils, binaryConversion

from settings import settings  

class Category_Class:
  
    def __init__(self,category_dao):
      self.category_dao = category_dao
      
    def create_category(self, category_data):
      
      return self.category_dao.create_record(category_data.model_dump())
    
    def get_categories(self):
        
        category_list = self.category_dao.fetch_records_from_model()
        
        return category_list
    
    def get_category_by_name(self, category_name : str):
      
      category_data = self.category_dao.fetch_records_by_field_name(field_name= "category_name", field_value = category_name)
      
      return category_data 
# Location Related Class
      
class Location_Class:
  
    def __init__(self, location_schema, location_dao):
      
      self.location_schema = location_schema
      self.location_dao = location_dao
    
    def get_coords(self, address : str):
        
        api_key = settings.GEOCODING_API_KEY
        
        api_url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"
        
        try:
            api_response = requests.get(api_url)
            api_response.raise_for_status()
            
            response_dict = api_response.json()
            
            lon,lat =  response_dict["features"][0]["geometry"]["coordinates"]

            return {"latitude" : lat, "longitude" : lon}
        
        except requests.exceptions.HTTPError as http_err:
          print(f"HTTP error occurred: {http_err}")  # Catches 4xx/5xx errors
        except requests.exceptions.RequestException as err:
          print(f"Request failed: {err}")  # Catches other request errors
          
    def create_location_data(self,full_location : str):
        
        coords = self.get_coords(full_location)
        
        location_data = self.location_schema(**coords, full_location = full_location)
        
        inserted_data = self.location_dao.create_record(location_data.model_dump())
        
        return inserted_data
        
    def get_location_by_name(self,location_name):
      
      location_data = self.location_dao.get_record(field_name = "full_location", field_value = location_name)
      
      return location_data
      
    def get_location_by_id(self, location_id):
      
      location_data = self.location_dao.get_record(field_name = "location_id", field_value = location_id)
      
      return location_data


    
class Bookings_Class:
  
  def __init__(self, bookings_dao):
     self.bookings_dao = bookings_dao
     
  def get_attendee_booking_data(self, event_id, attendee_id):
    
    attendee_data = self.bookings_dao.get_booking_data(attendee_id, event_id)
    
    return attendee_data
  
  def register_attendee(self, event_id, attendee_id):
    
    is_already_registered = self.get_attendee_booking_data(event_id, attendee_id)
  
    if is_already_registered:
      
      raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="You have already registered in this event")
    
    pass
# Events Related Class

class Events_Class:
  
    def __init__(self,location_service,bookings_service,category_service,event_dao,events_validator):
      self.location_service = location_service
      self.bookings_service = bookings_service
      self.category_service = category_service
      self.event_dao = event_dao
      self.event_validator = events_validator

    def create_event(self,event_data : dict , creator_id):
      
        self.event_validator.validate_event_details(event_data, creator_id)
        
        address_dict = event_data["address_details"]
        
        ticket_dict = event_data["ticket_details"]
        
        participant_dict = event_data["participant_details"]
        
        del event_data["address_details"]
        del event_data["participant_details"]
        del event_data["ticket_details"]
        
        full_address = string_utils.create_full_address(address_dict)
        
        category_data = self.category_service.get_category_by_name(event_data["category_name"])
        
        if not category_data:
          
          raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST ,
            detail=f"The requested {event_data["category_name"]} category is not exists" 
          )
        
        address_data =  self.location_service.get_location_by_name(full_address)
        
        if not address_data:
          
          address_data = self.location_service.create_location_data(full_address)
          
        event_id = binaryConversion.str_to_binary(str(uuid4()))
        
        event_schema_object = event_schema.Event_Model_Schema(**event_data,**ticket_dict, **participant_dict, landmark=address_dict["landmark"], category_id=category_data["category_id"], address_id = address_data["address_id"], creator_id=creator_id,event_id = event_id )
        
        new_event_dict = self.event_dao.create_record(event_schema_object.model_dump())
        
        default_attendee = self.bookings_service
        
        new_event_dict["event_id"] = binaryConversion.binary_to_str(new_event_dict["event_id"])
        
        ticket_response = event_schema.Ticket_Response_Schema(**ticket_dict, available_tickets=ticket_dict["total_tickets"]-1)
        
        return {**new_event_dict, "register_state" : "valid", "address" : address_data, "ticket_details" : ticket_response, "participant_details": participant_dict}
      
    def get_events_list(self):
      
      events_list = self.event_dao.fetch_records_from_model()
      
      return events_list if events_list else []
    
    def get_event_by_id(self, byte_event_id, byte_user_id):
      
      
        
      
      event_data = self.event_dao.get_event_by_id(byte_event_id)
      
      if not event_data:
        raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=f"The Event with this ({event_data}) is not exist"
        )
      
      booking_data = self.bookings_service.get_booking_data(byte_event_id,byte_user_id)
      
events_validator = validator.events_validator     
      
category_service = Category_Class(models.category_dao)
bookings_service = Bookings_Class(models.bookings_dao)
location_service = Location_Class(event_schema.Event_Location_Model_Schema,models.location_dao)
events_service = Events_Class(location_service, bookings_service, category_service,models.events_dao,events_validator)

__all__ = ["category_service", "location_service", "events_service"]