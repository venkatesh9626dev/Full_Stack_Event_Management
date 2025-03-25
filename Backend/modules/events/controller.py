from fastapi import APIRouter, Depends , HTTPException , status

from middlewares import protected_dependency

from . import schema

from utils import binaryConversion

from .service import category_service, events_service


events_router = APIRouter()


@events_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(event_data : schema.Event_Request_Schema, user_id : str = Depends(protected_dependency.validate_user)):
   
   user_id = binaryConversion.str_to_binary(user_id)
   
   event_create_response = events_service.create_event(event_data.model_dump(), user_id)
   
   return schema.Event_Response_Schema(**event_create_response)

@events_router.put("/{event_id}")
async def update_event_details(user_id : str = Depends(protected_dependency.validate_user)):
    pass

@events_router.patch("/{event_id}")
async def update_event_detail(user_id : str = Depends(protected_dependency.validate_user)):
    pass

@events_router.get("/")
async def get_events():
    events_list = events_service.get_events_list()
    
    return schema.Events_Response_Schema(events_list= events_list)
    
@events_router.get("/category/{category}")
async def get_events_by_category(user_id : str = Depends(protected_dependency.validate_user)):
    pass


@events_router.get("/{event_id}")
async def get_event_by_id(event_id : str ,user_id : str = Depends(protected_dependency.validate_user)):
    
    [byte_event_id, byte_user_id] = [binaryConversion.str_to_binary(id) for id in [event_id, user_id]]
    
    event_data = events_service.get_event_by_id(byte_event_id=byte_event_id, byte_user_id=byte_user_id)
    
    

@events_router.get("/search")
async def search_events(user_id : str = Depends(protected_dependency.validate_user)):
    pass

@events_router.get("/created")
async def get_created_events(user_id : str =  Depends(protected_dependency.validate_user)):
    pass

@events_router.get("/registered")
async def get_registered_events(user_id : str =  Depends(protected_dependency.validate_user)):
    pass

@events_router.get("/category")
async def get_categories():
   
   category_list = category_service.get_categories()
   
   return schema.Category_Response(category_list=category_list)

@events_router.post("/category", status_code=status.HTTP_201_CREATED)
def create_category(category_data : schema.Category_Schema, user_id : str = Depends(protected_dependency.validate_user)):
    
    new_category = category_service.create_category(category_data.model_dump())
    
    return schema.Category_Schema(**new_category)