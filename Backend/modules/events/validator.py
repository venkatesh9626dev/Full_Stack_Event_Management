from . import models
from fastapi import HTTPException, status
from shared import generic_enum
from datetime import date, datetime
from modules.users.models import profile_dao


class TimeDate_Validator_Class:

    def check_event_datetime(self, event_start_datetime, event_end_datetime):

        current_datetime = datetime.now()

        if event_start_datetime <= current_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event start datetime should be greater than current datetime",
            )
        elif event_end_datetime <= current_datetime:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event start time should be greater than current time or event date should be greater than or equal to today's date",
            )
        elif event_start_datetime == event_end_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event start datetime and Event end datetime shouldn't be same",
            )

    def event_registration_expiry_check(self, event_start_datetime):

        current_time = datetime.now()
        if current_time > event_start_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The event registration is closed",
            )


class Participant_Validator_Class:

    def __init__(self, event_bookings_dao):
        self.event_bookings_dao = event_bookings_dao

    def is_already_registered(self, event_id, user_id):

        booking_data = self.event_bookings_dao.get_booking_data(user_id, event_id)

        if booking_data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User has already registered for this event",
            )


class Creator_Validator_Class:

    def __init__(self, user_profile_dao):
        self.user_profile_dao = user_profile_dao

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


class Events_Validator_Class:

    def __init__(self, event_dao, time_validator, creator_validator):
        self.event_dao = event_dao
        self.time_validator = time_validator
        self.creator_validator = creator_validator

    def validate_event_details(self, event_data: dict, creator_id: bytes):
        event_start_datetime = event_data["event_start_date_time"]
        event_end_datetime = event_data["event_end_date_time"]

        self.time_validator.check_event_datetime(
            event_start_datetime, event_end_datetime
        )

        event_ticket_type = event_data["ticket_details"]["ticket_type"]

        if event_ticket_type == generic_enum.Ticket_Type_Enum.PAID:

            self.creator_validator.is_merchant_id_exists(creator_id)


event_dao = models.events_dao
time_validator = TimeDate_Validator_Class()
creator_validator = Creator_Validator_Class(profile_dao)

events_validator = Events_Validator_Class(
    event_dao=event_dao,
    time_validator=time_validator,
    creator_validator=creator_validator,
)
