from shared import generic_enum
import re



class Schema_Validation:

    @staticmethod
    def check_at_least_one_field(data):
        if not data or set(data.values) == {None}:
            raise ValueError("At least one field must be provided for update.")
        return data

    @staticmethod
    def strip_phone_number(value):
        if isinstance(value, str):
            return value.strip()
        return value

    @staticmethod
    def validate_password(password: str):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,20}$"

        if not re.fullmatch(pattern, password):
            raise ValueError(
                "Password must be 8-20 characters long and include at least:\n"
                "- One uppercase letter\n"
                "- One lowercase letter\n"
                "- One digit\n"
                "- One special character (@$!%*?&)"
            )
        return password

    @staticmethod
    def check_ticket_details(ticket_details):

        ticket_type = ticket_details.get("ticket_type")
        ticket_fare = ticket_details.get("ticket_fare")

        if (
            generic_enum.Ticket_Type_Enum(ticket_type)
            == generic_enum.Ticket_Type_Enum.PAID
            and ticket_fare == None
        ):
            raise ValueError(
                "Should provide ticket_fare while providing Paid (Ticket Type)"
            )
        elif (
            generic_enum.Ticket_Type_Enum(ticket_type)
            == generic_enum.Ticket_Type_Enum.FREE
            and ticket_fare
        ):
            raise ValueError("Ticket fare is not required when the ticket type is free")

        return ticket_details

    @staticmethod
    def check_participant_details(participant_details):

        participant_type = participant_details.get("participant_type")
        participant_count = participant_details.get("participant_count")

        if participant_type == generic_enum.Participant_Enum.GROUP and (
            participant_count == None or participant_count == 1
        ):
            raise ValueError(
                "Group participant event need the participants count or the count should be greater than 1"
            )

        elif (
            participant_type == generic_enum.Participant_Enum.INDIVIDUAL
            and participant_count > 1
        ):
            raise ValueError("Participant Count of Individual should be always One")

        return participant_details

