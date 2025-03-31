from shared import generic_enum
import re
from datetime import datetime, timezone
from fastapi import HTTPException

from pydantic_core import ErrorDetails


class Schema_Validation:
    @staticmethod
    def check_at_least_one_field(instance):
        data_dict = instance.model_dump(exclude_none=True)

        event_id = data_dict.pop("event_id", None)

        if len(data_dict) == 0:
            raise HTTPException(
                status_code=422,
                detail=[
                    ErrorDetails(
                        loc=("body", "general"),
                        msg="At least one field must be provided for update",
                        type="value_error",
                    )
                ],
            )

        return instance

    @staticmethod
    def strip_phone_number(value):
        if isinstance(value, str):
            return value.strip()
        return value

    @staticmethod
    def validate_password(password: str):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,20}$"

        if not re.fullmatch(pattern, password):
            raise HTTPException(
                status_code=422,
                detail=[
                    ErrorDetails(
                        loc=("body", "password"),
                        msg=(
                            "Password must be 8-20 characters long and include at least:\n"
                            "- One uppercase letter\n"
                            "- One lowercase letter\n"
                            "- One digit\n"
                            "- One special character (@$!%*?&)"
                        ),
                        type="value_error",
                    )
                ],
            )
        return password


class Event_Request_Validation:
    def check_ticket_details(self, ticket_details):
        ticket_type = ticket_details.get("ticket_type")
        ticket_fare = ticket_details.get("ticket_fare")

        if (
            generic_enum.Ticket_Type_Enum(ticket_type)
            == generic_enum.Ticket_Type_Enum.PAID
            and ticket_fare == 0
        ):
            return ErrorDetails(
                loc=("body", "ticket_fare"),
                msg="Should provide ticket_fare greater than 0 while providing Paid (Ticket Type)",
                type="value_error",
            )

        elif (
            generic_enum.Ticket_Type_Enum(ticket_type)
            == generic_enum.Ticket_Type_Enum.FREE
            and ticket_fare > 0
        ):
            return ErrorDetails(
                loc=("body", "ticket_fare"),
                msg="Ticket fare is not required when the ticket type is free",
                type="value_error",
            )

    def check_event_datetime(self, event_datetime):
        current_datetime = datetime.now(timezone.utc)

        if event_datetime["event_start_date_time"] <= current_datetime:
            return ErrorDetails(
                loc=("body", "event_start_date_time"),
                msg="Event start datetime should be greater than current datetime",
                type="value_error",
            )
        elif event_datetime["event_end_date_time"] <= current_datetime:
            return ErrorDetails(
                loc=("body", "event_end_date_time"),
                msg="Event end time should be greater than current time or event date should be greater than or equal to today's date",
                type="value_error",
            )

        elif (
            event_datetime["event_start_date_time"]
            == event_datetime["event_end_date_time"]
        ):
            return ErrorDetails(
                loc=("body", "event_start_date_time", "event_end_date_time"),
                msg="Event start datetime and Event end datetime shouldn't be the same",
                type="value_error",
            )

    def check_participant_details(self, participant_details):
        print(participant_details)

        participant_type = participant_details.get("participant_type").lower()
        participant_count = participant_details.get("participant_count")

        print(
            participant_type == generic_enum.Participant_Enum.INDIVIDUAL
            and participant_count > 1
        )

        if participant_type == generic_enum.Participant_Enum.GROUP and (
            participant_count == None or participant_count == 1
        ):
            return ErrorDetails(
                loc=("body", "participant_count"),
                msg="Group participant event needs the participants count to be greater than 1",
                type="value_error",
            )

        elif (
            participant_type == generic_enum.Participant_Enum.INDIVIDUAL
            and participant_count > 1
        ):
            return ErrorDetails(
                loc=("body", "participant_count"),
                msg="Participant Count of Individual should always be One",
                type="value_error",
            )

    def validate_data(self, event_data):
        total_errors = []

        participant_data_error = self.check_participant_details(
            {
                "participant_type": event_data["participant_type"],
                "participant_count": event_data["participant_count"],
            }
        )

        ticket_data_error = self.check_ticket_details(
            {
                "ticket_type": event_data["ticket_type"],
                "ticket_fare": event_data["ticket_fare"],
            }
        )

        datetime_data_error = self.check_event_datetime(
            {
                "event_start_date_time": event_data["event_start_date_time"],
                "event_end_date_time": event_data["event_end_date_time"],
            }
        )

        if participant_data_error:
            total_errors.append(participant_data_error)
        if ticket_data_error:
            total_errors.append(ticket_data_error)
        if datetime_data_error:
            total_errors.append(datetime_data_error)

        return total_errors


event_request_validation = Event_Request_Validation()
