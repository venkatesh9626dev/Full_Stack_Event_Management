from fastapi import HTTPException, status

from core.auth import Jwt_Token, Hashing

from utils import binaryConversion


from .models import auth_dao, profile_dao

from uuid import uuid4

from .validator import Auth_Validator


from settings import cipher


class Authentication_Service:
    @classmethod
    def register_user(cls, register_credentials: dict):
        user = auth_dao.fetch_record(
            field_name="email", field_value=register_credentials["email"]
        )

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email id already exists",
            )

        hash_password = Hashing.hash_data(register_credentials["password"])

        register_credentials.password = hash_password

        user_binary_id = binaryConversion.str_to_binary(str(uuid4()))

        new_user = auth_dao.create_record(
            {**register_credentials, "user_id": user_binary_id}
        )

        user_uuid = binaryConversion.binary_to_str(new_user["user_id"])

        access_token = Jwt_Token.create_access_token({"sub": user_uuid})

        return {"access_token": access_token, "email": new_user["email"]}

    @classmethod
    def authenticate_user(cls, authenticate_credentials: dict):
        user = auth_dao.fetch_record(
            field_name="email", field_value=authenticate_credentials["email"]
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )

        password_check = Auth_Validator.check_password_match(
            authenticate_credentials["password"], user["password"]
        )

        if not password_check:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )

        user_uuid = binaryConversion.binary_to_str(user["user_id"])

        access_token = Jwt_Token.create_access_token({"sub": user_uuid})

        return {"access_token": access_token, "email": user["email"]}


class User_Profile_Service:
    @classmethod
    def create_profile(cls, profile_data: dict, binary_user_id: bytes):
        user_profile = profile_dao.fetch_record(
            field_name="user_id", field_value=binary_user_id
        )

        if user_profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User Profile already exists",
            )
        binary_profile_id = binaryConversion.str_to_binary(str(uuid4()))

        profile_data["user_id"] = binary_user_id
        profile_data["profile_id"] = binary_profile_id

        new_profile = profile_dao.create_record(profile_data)

        if new_profile["merchant_id"]:
            new_profile["merchant_id"] = cipher.decrypt(
                new_profile["merchant_id"]
            ).decode()

        return new_profile

    @classmethod
    def update_profile(cls, update_data: dict, binary_user_id: bytes):
        user_profile = profile_dao.fetch_record(
            field_name="user_id", field_value=binary_user_id
        )

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile doesn't exist",
            )

        filtered_data = {
            f"{key}": value for key, value in update_data.items() if value is not None
        }

        updated_details = profile_dao.update_record(
            data=filtered_data,
            field_name="profile_id",
            field_value=user_profile["profile_id"],
        )

        if updated_details["merchant_id"]:
            updated_details["merchant_id"] = cipher.decrypt(
                updated_details["merchant_id"]
            ).decode()

        return updated_details

    @classmethod
    def get_profile(cls, binary_user_id: str):
        user_profile = profile_dao.fetch_record(
            field_name="user_id", field_value=binary_user_id
        )

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is profile is not yet created",
            )

        if "merchant_id" in user_profile:
            user_profile["merchant_id"] = Hashing.hash_data(user_profile["merchant_id"])

        return user_profile
