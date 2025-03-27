from enum import Enum

# Enum


class Ticket_Type_Enum(str, Enum):

    PAID = "paid"
    FREE = "free"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()

            for member in cls:
                if value == member.value:
                    return member
        return None


class Ticket_Status(str, Enum):

    VALID = "valid"
    USED = "used"


class Participant_Enum(str, Enum):

    GROUP = "group"
    INDIVIDUAL = "individual"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()

            for member in cls:
                if value == member.value:
                    return member
        return None

class Registration_Status_Enum(str,Enum):
    
    REGISTERED = "registered"
    NOT_REGISTERED = "not_registered"

# Cloudinary Based Enum

class AllowedFileTypes(str, Enum):
    JPEG = "image/jpeg"
    PNG = "image/png"