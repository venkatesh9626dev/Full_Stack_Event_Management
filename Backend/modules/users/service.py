from fastapi import HTTPException, status

from core.auth import Jwt_Token, Hashing

from utils import binaryConversion

from .schema import Profile_Create_Request_Schema, Profile_Update_Request_Schema

from . import schema as user_schema

from .models import Auth_Dao, Profile_Dao

from uuid import uuid4

from .validator import Auth_Validator




class Authentication_Service:

    @classmethod
    def register_user(cls, register_credentials: user_schema.Auth_Request_Schema):

        user = Auth_Dao.get_record(
            field_name="email", field_value=register_credentials.email
        )

        if user:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email id already exists",
            )

        hash_password = Hashing.hash_password(register_credentials.password)

        register_credentials.password = hash_password

        user_binary_id = binaryConversion.str_to_binary(str(uuid4()))

        new_user = Auth_Dao.register_user(
            {**register_credentials.model_dump(), "user_id": user_binary_id}
        )

        user_uuid = binaryConversion.binary_to_str(new_user.user_id)

        access_token = Jwt_Token.create_access_token({"sub": user_uuid})

        return {"access_token": access_token, "email": new_user.email}

    @classmethod
    def authenticate_user(
        cls, authenticate_credentials: user_schema.Auth_Request_Schema
    ):

        user = Auth_Dao.get_record(
            field_name="email", field_value=authenticate_credentials.email
        )

        if not user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )

        password_check = Auth_Validator.check_password_match(
            authenticate_credentials.password, user.password
        )

        if not password_check:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )

        user_uuid = binaryConversion.binary_to_str(user.user_id)

        access_token = Jwt_Token.create_access_token({"sub": user_uuid})

        return {"access_token": access_token, "email": user.email}


class User_Profile_Service:

    @classmethod
    def create_profile(cls, profile_data: dict, binary_user_id: bytes):


        user_profile = Profile_Dao.get_record(
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

        new_profile = Profile_Dao.create_record(profile_data)

        return new_profile

    @classmethod
    def update_profile(cls, updated_data: dict, binary_user_id : bytes):


        user_profile = Profile_Dao.get_record(
            field_name="user_id", field_value=binary_user_id
        )

        if not user_profile:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile doesn't exist",
            )

        updated_details = Profile_Dao.update_record(
            data=updated_data,
            field_name="profile_id",
            field_value=user_profile["profile_id"],
        )

        return updated_details

    @classmethod
    def get_profile(cls, binary_user_id: str):


        user_profile = Profile_Dao.get_record(
            field_name="user_id", field_value=binary_user_id
        )

        if not user_profile:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is profile is not yet created",
            )

        return user_profile
