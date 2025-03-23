from fastapi import APIRouter, Depends , HTTPException , status

from middlewares import protected_dependency

from . import schema

from .service import Category_Service, Events_Service


events_router = APIRouter()

@events_router.get("/category")
async def get_categories():
   
   category_list = Category_Service.get_categories()
   
   return schema.Category_Response(category_list=category_list)

@events_router.post("/events")
async def create_event(event_data : schema.Event_Request_Schema, user_id : str = Depends(protected_dependency.validate_user)):
   
   event_create_response = Events_Service.create_event(event_data.model_dump(), user_id)
   
   return schema.Event_Response_Schema(event_create_response)

@events_router.put("/events/{event_id}")
async def update_event_details():
    pass

@events_router.patch("/events/{event_id}")
async def update_event_detail():
    pass

@events_router.get("/events")
async def get_events():
    pass
    
@events_router.get("/events/{category}")
async def get_events_by_category():
    pass

@events_router.get("/events/{event_id}")
async def get_event_by_id():
    pass

@events_router.get("/events/search")
async def search_events():
    pass

@events_router.get("/events/created")
async def get_created_events(user_id : str =  Depends(protected_dependency.validate_user)):
    pass

@events_router.get("/events/registered")
async def get_registered_events(user_id : str =  Depends(protected_dependency.validate_user)):
    pass

