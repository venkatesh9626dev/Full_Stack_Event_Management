from . import models
from fastapi import HTTPException, status
from shared import generic_enum
from datetime import datetime
from modules.users.models import profile_dao


class TimeDate_Validator_Class:

   

    def event_registration_expiry_check(self, event_start_date_time):
        current_time = datetime.now()
        if current_time > event_start_date_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The event registration is closed",
            )


class Participant_Validator_Class:

    def __init__(self, event_bookings_dao,profile_dao):
        self.event_bookings_dao = event_bookings_dao
        self.profile_dao = profile_dao
        
    def check_profile_exists(self,attendee_id):
        
        profile = profile_dao.fetch_record(field_name="user_id",field_value=attendee_id)
        
        if not profile:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Profile holders can register in the events")

    def is_already_registered(self, event_id, user_id):

        booking_data = self.event_bookings_dao.get_booking_data(user_id, event_id)

        if booking_data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User has already registered for this event",
            )


class Creator_Validator_Class:

    def __init__(self, user_profile_dao, events_dao):
        self.user_profile_dao = user_profile_dao
        self.events_dao = events_dao

    def is_merchant_id_exists(self, creator_id):

        creator_profile = self.user_profile_dao.get_user_profile(creator_id)

        if not creator_profile:
            raise HTTPException(
                status_code=403, detail="User profile is required to create an event."
            )

        merchant_id = creator_profile.merchant_id

        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User should enter their razorpay merchant id to create a paid events to receive money from participants",
            )
            
    def validate_creator_match(self, event_id, creator_id):
        
        event = self.events_dao.fetch_record(field_name="event_id", field_value = event_id)
        
        if event["creator_id"] != creator_id:
            HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only event creator can see their participant details")


class Events_Validator_Class:

    def __init__(self, event_dao, time_validator, creator_validator):
        self.event_dao = event_dao
        self.time_validator = time_validator
        self.creator_validator = creator_validator

    def validate_event_authorization(self, event_data: dict, creator_id: bytes):

        event_ticket_type = event_data["ticket_type"]

        if event_ticket_type == generic_enum.Ticket_Type_Enum.PAID:

            self.creator_validator.is_merchant_id_exists(creator_id)
    
    def validate_event_exists(self, event_id):
        
        event = self.event_dao.fetch_record(field_name="event_id", field_value = event_id)
        
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Event not exist to see the booking data")

event_dao = models.events_dao
time_validator = TimeDate_Validator_Class()
creator_validator = Creator_Validator_Class(profile_dao,event_dao)
participant_validator = Participant_Validator_Class(event_bookings_dao= models.bookings_dao,profile_dao=profile_dao)

events_validator = Events_Validator_Class(
    event_dao=event_dao,
    time_validator=time_validator,
    creator_validator=creator_validator,
)
