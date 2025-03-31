from fastapi import Form
from datetime import datetime, date
from typing import Optional
from utils.cloudinary_util import upload_file
from fastapi import File, UploadFile


from modules.events.schema import (
    Event_Request_Schema,
    Address_Schema,
    Ticket_Schema,
    Participant_Schema,
    Event_Update_Request_Schema,
)


def get_create_event_data(
    event_name: str = Form(...),
    image_file: UploadFile = File(...),
    event_description: str = Form(...),
    event_agenda: str = Form(...),
    event_start_date_time: datetime = Form(...),
    event_end_date_time: datetime = Form(...),
    category_id: int = Form(...),
    # Address Details
    street_address: str = Form(...),
    landmark: Optional[str] = Form(None),
    city: str = Form(...),
    state: str = Form(...),
    pin_code: str = Form(...),
    country: str = Form(...),
    # Ticket Details
    ticket_type: str = Form(...),
    ticket_fare: float = Form(...),
    total_tickets: int = Form(...),
    # Participant Details
    participant_type: str = Form(...),
    participant_count: int = Form(...),
) -> Event_Request_Schema:
    """Extracts form data and returns an Event_Request_Schema object"""

    event_image_url = upload_file(image_file)

    # Return Event Schema
    return Event_Request_Schema(
        event_name=event_name,
        event_image_url=event_image_url,
        event_description=event_description,
        event_agenda=event_agenda,
        event_start_date_time=event_start_date_time,
        event_end_date_time=event_end_date_time,
        category_id=category_id,
        street_address=street_address,
        landmark=landmark,
        city=city,
        state=state,
        pin_code=pin_code,
        country=country,
        ticket_type=ticket_type,
        ticket_fare=ticket_fare,
        total_tickets=total_tickets,
        participant_type=participant_type,
        participant_count=participant_count,
    )


def get_update_event_data(
    event_id: str = Form(...),
    event_name: str = Form(None),
    event_description: str = Form(None),
    event_agenda: str = Form(None),
    image_file: UploadFile = File(None),
):
    event_image_url = upload_file(image_file) if image_file else None

    update_data = {
        "event_id": event_id,
        "event_name": event_name,
        "event_description": event_description,
        "event_agenda": event_agenda,
        "event_image_url": event_image_url,
    }

    filtered_data = {
        key: value for key, value in update_data.items() if value is not None
    }

    return Event_Update_Request_Schema(**filtered_data)
