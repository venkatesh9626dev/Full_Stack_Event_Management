from fastapi import APIRouter, Depends, HTTPException, status

from . import schema

from utils import binaryConversion

from .service import category_service, events_service, bookings_service

from .dependency import get_create_event_data, get_update_event_data

from middlewares.protected_dependency import get_current_user

events_router = APIRouter()


@events_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    user_binary_id: bytes = Depends(get_current_user),
    event_data: schema.Event_Request_Schema = Depends(get_create_event_data)
):


    event_create_response = events_service.create_event(
        event_data.model_dump(), user_binary_id
    )

    return schema.Event_Response_Schema(**event_create_response)


@events_router.put("/{event_id}")
async def update_event_details(
    user_binary_id: bytes = Depends(get_current_user),
    update_data : schema.Event_Update_Request_Schema = Depends(get_update_event_data)
):
    updated_data = events_service.update_event(update_data=update_data,creator_id=user_binary_id)

    return schema.Event_Base_Response_Schema(**updated_data)

@events_router.patch("/{event_id}")
async def update_event_detail(
    user_binary_id: bytes = Depends(get_current_user),
    update_data : schema.Event_Update_Request_Schema = Depends(get_update_event_data)
):
    pass


@events_router.get("/")
async def get_events():
    events_list = events_service.get_events_list()

    return schema.Events_Response_Schema(events_list=events_list)


@events_router.get("/category/{category}")
async def get_events_by_category(
    user_binary_id: bytes = Depends(get_current_user),
):
    pass


@events_router.get("/{event_id}")
async def get_event_by_id(
    event_id: str, user_binary_id: bytes = Depends(get_current_user)
):

    binary_event_id = binaryConversion.str_to_binary(event_id)

    event_data = events_service.get_event_by_id(
        byte_event_id=binary_event_id, byte_user_id=user_binary_id
    )
    
    return schema.Event_Response_Schema(**event_data,event_id= event_id)

@events_router.get("/{event_id}/bookings")
def get_event_bookings(event_id : str, creator_id : bytes = Depends(get_current_user)):
    
    event_bookings = bookings_service.get_event_booking_data(event_id=event_id,creator_id=creator_id)
    
    return schema.User_Bookings_Response_Schema(bookings_list = event_bookings)

@events_router.get("/search")
async def search_events(user_binary_id: bytes = Depends(get_current_user)):
    pass


@events_router.get("/created")
async def get_created_events(
    user_binary_id: bytes = Depends(get_current_user),
):
    pass


@events_router.get("/booked")
async def get_booked_events(
    user_binary_id: bytes = Depends(get_current_user),
):
    pass


@events_router.get("/category")
async def get_categories():

    category_list = category_service.get_categories()

    return schema.Category_Response(category_list=category_list)


@events_router.post("/category", status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: schema.Category_Schema,
    user_binary_id: bytes = Depends(get_current_user),
):

    new_category = category_service.create_category(category_data.model_dump())

    return schema.Category_Schema(**new_category)
