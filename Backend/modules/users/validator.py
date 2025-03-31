from pydantic import EmailStr
from .models import auth_dao, profile_dao
from core.auth import Hashing

from fastapi import HTTPException, status


class Auth_Validator:
    @staticmethod
    def check_password_match(password, hashed_password):
        is_matching = Hashing.verify_hash_data(password, hashed_password)

        return True if is_matching else False


class User_Validation:
    def __init__(self, auth_dao):
        self.auth_dao = auth_dao

    def validate_user_exists(self, user_binary_id):
        user = self.auth_dao.fetch_record(
            field_name="user_id", field_value=user_binary_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )


general_user_validation = User_Validation(auth_dao)
