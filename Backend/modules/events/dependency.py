from fastapi import Form
from datetime import datetime, date
from typing import Optional
from utils.cloudinary_util import upload_file
from fastapi import File, UploadFile


from modules.events.schema import Event_Request_Schema, Address_Schema, Ticket_Schema, Participant_Schema, Event_Update_Request_Schema

def get_create_event_data(
    event_name: str = Form(...),
    image_file : UploadFile = File(...),
    event_description: str = Form(...),
    event_agenda: str = Form(...),
    event_start_date_time: datetime = Form(...),
    event_end_date_time: datetime = Form(...),
    category_name: str = Form(...),

    # Address Details
    street_address: str = Form(...),
    landmark: Optional[str] = Form(None),
    city: str = Form(...),
    state: str = Form(...),
    pin_code: str = Form(...),
    country: str = Form(...),

    # Ticket Details
    ticket_type: str = Form(...),
    ticket_fare: Optional[float] = Form(None),
    total_tickets: int = Form(...),

    # Participant Details
    participant_type: str = Form(...),
    participant_count: int = Form(...),

) -> Event_Request_Schema:
    """Extracts form data and returns an Event_Request_Schema object"""

    event_image_url = upload_file(image_file)

     
    # Create nested schemas
    address_details = Address_Schema(
        street_address=street_address, landmark=landmark, city=city,
        state=state, pin_code=pin_code, country=country
    )

    ticket_details = Ticket_Schema(
        ticket_type=ticket_type, ticket_fare=ticket_fare, total_tickets=total_tickets
    )

    participant_details = Participant_Schema(
        participant_type=participant_type, participant_count=participant_count
    )

    # Return Event Schema
    return Event_Request_Schema(
        event_name=event_name,event_image=event_image_url, event_description=event_description,
        event_agenda=event_agenda, event_start_date_time=event_start_date_time,
        event_end_date_time=event_end_date_time, category_name=category_name,
        address_details=address_details, ticket_details=ticket_details,
        participant_details=participant_details
    )
    
    
def get_update_event_data(
    event_name : str = Form(None),
    event_description : str = Form(None),
    event_agenda : str = Form(None),
    image_file : UploadFile = File(None)
):
    
    if image_file:
        event_image_url = upload_file(image_file)
        
    return Event_Update_Request_Schema(
        event_name=event_name,event_agenda=event_agenda, event_description=event_description,event_image_url=event_image_url
    )
    