from . import models

from uuid import uuid4

import requests

from fastapi import HTTPException, status

from . import schema as event_schema

from utils import string_utils, binaryConversion

from settings import settings  

class Category_Class:
  
    def __init__(self,category_dao):
      self.category_dao = category_dao
    
    def get_categories(self):
        
        category_Object_list = self.category_dao.get_categories()
        
        if not category_Object_list:
          return []
        
        category_list = [category_object.model_dump() for category_object in category_Object_list]
        
        return category_list
    
    def get_category_by_name(self, category_name : str):
      
      category_data = self.get_category_by_name(category_name)
      
      return category_data if category_data else None
    
      
class Location_Class:
  
    def __init__(self, location_schema, location_dao):
      
      self.location_schema = location_schema
      self.location_dao = location_dao
    
    async def get_coords(self, address : str):
        
        api_key = settings.GEOCODING_API_KEY
        
        api_url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"
        
        try:
            api_response = requests.get(api_url)
            api_response.raise_for_status()
            
            response_dict = api_response.json()
            
            [lon,lat] =  response_dict["features"][0]["geometry"]["coordinates"]

            return {"latitude" : lat, "longitude" : lon}
        
        except requests.exceptions.HTTPError as http_err:
          print(f"HTTP error occurred: {http_err}")  # Catches 4xx/5xx errors
        except requests.exceptions.RequestException as err:
          print(f"Request failed: {err}")  # Catches other request errors
          
    async def create_location_data(self,full_address : str):
        
        coords = self.get_coords(full_address)
        
        location_data = self.location_schema(**coords, full_address = full_address)
        
        inserted_data = self.location_dao.create_location_data(location_data)
        
        return inserted_data
        
    async def get_location_by_name(self,location_name):
      
      location_data = self.location_dao.get_location_by_name(location_name)
      
      return location_data if location_data else None
      
    async def get_location_by_id(self, location_id):
      
      location_data = self.location_dao.get_location_by_id(location_id)
      
      return location_data if location_data else None
class Events_Class:
  
    def __init__(self,location_service,ticket_service,category_service,event_dao):
      self.location_service = location_service
      self.ticket_service = ticket_service
      self.category_service = category_service
      self.event_dao = event_dao

    async def create_event(self,event_data : dict , creator_id):
        
        address_dict = event_data["address_details"]
        
        ticket_dict = event_data["ticket_details"]
        
        participant_dict = event_data["participant_details"]
        
        del event_data["address_details"]
        del event_data["participant_details"]
        del event_data["ticket_details"]
        
        full_address = string_utils.create_full_address(**address_dict)
        
        category_data = self.category_service.get_category_by_name(event_data["category_name"])
        
        if not category_data:
          
          raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST ,
            detail=f"The requested {event_data.category_name} category is not exists" 
          )
        
        address_data =  self.location_service.get_location_by_name(full_address)
        
        if not address_data:
          
          address_data = self.Address_Service.get_coords(full_address)
          
        event_id = binaryConversion.str_to_binary(str(uuid4()))
        
        event_schema_object = event_schema.Event_Model_Schema(**event_data,**ticket_dict, **participant_dict, landmark=address_dict["landmark"], category_id=category_data.category_id, address_id = address_data.address_id, creator_id=creator_id,event_id = event_id )
        
        new_event_object = self.event_dao.create_event(event_schema_object)
        
        ticket_response = event_schema.Ticket_Response_Schema(**ticket_dict, available_tickets=ticket_dict["available_tickets"]-1)
        
        return event_schema.Event_Response_Schema(**new_event_object.model_dump(), register_state="valid", address=address_dict, ticket_details=ticket_response, participant_details=participant_dict)
      
Category_Service = Category_Class(models.Category_Dao)
Ticket_Service = None
Location_Service = Location_Class(event_schema.Event_Location_Model_Schema,models.Location_Dao)
Events_Service = Events_Class(Location_Service, Ticket_Service, Category_Service, models.Event_Dao)

__all__ = ["Category_Service", "Location_Service", "Events_Service"]