from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
)

from . import schema

from utils import binaryConversion

from .models import Auth_Dao

from .service import Authentication_Service, User_Profile_Service

from .validator import Auth_Validator

from middlewares.protected_dependency import get_current_user

from .dependency import get_profile_create_data, get_profile_update_data

users_router = APIRouter()


# Users Authentication routes


@users_router.post("/auth/register")
async def register_user(
    response: Response, register_credentials: schema.Auth_Request_Schema
):
    response_details = Authentication_Service.register_user(
        register_credentials.model_dump()
    )

    response.set_cookie(
        key="access_token",
        value=response_details["access_token"],
        httponly=True,
        max_age=3600,
        # secure = True This will be added after making https
    )

    return schema.Auth_Response_Schema(email=response_details["email"])


@users_router.post("/auth/signin")
async def signin_user(
    response: Response, authenticate_credentials: schema.Auth_Request_Schema
):
    response_details = Authentication_Service.authenticate_user(
        authenticate_credentials.model_dump()
    )

    response.set_cookie(
        key="access_token",
        value=response_details["access_token"],
        httponly=True,
        max_age=3600,
        # secure = True This will be added after making https
    )

    return schema.Auth_Response_Schema(email=response_details["email"])


# Users Profile routes


@users_router.post("/profile")
async def create_profile(
    profile_data: schema.Profile_Create_Request_Schema = Depends(
        get_profile_create_data
    ),
    user_binary_id: bytes = Depends(get_current_user),
):
    response_details = User_Profile_Service.create_profile(
        profile_data.model_dump(), user_binary_id
    )

    return schema.Profile_Create_Response_Schema(**response_details)


@users_router.get("/profile")
async def get_profile(user_binary_id: bytes = Depends(get_current_user)):
    user_profile = User_Profile_Service.get_profile(user_binary_id)

    return schema.User_Profile_Response_Schema(**user_profile)


@users_router.patch("/profile")
async def patch_profile(
    updated_data: schema.Profile_Update_Request_Schema = Depends(
        get_profile_update_data
    ),
    user_binary_id: str = Depends(get_current_user),
):
    updated_response = User_Profile_Service.update_profile(
        updated_data.model_dump(), user_binary_id
    )

    return schema.Profile_Response_Schema(**updated_response)


@users_router.put("/profile")
async def update_profile(
    updated_data: schema.Profile_Update_Request_Schema = Depends(
        get_profile_update_data
    ),
    user_binary_id: bytes = Depends(get_current_user),
):
    updated_response = User_Profile_Service.update_profile(
        updated_data.model_dump(), user_binary_id
    )

    return schema.Profile_Response_Schema(**updated_response)


@users_router.get("/{user_id}/profile")
async def get_user_profile(user_binary_id: bytes = Depends(get_current_user)):
    user_profile = User_Profile_Service.get_profile(user_binary_id)

    return schema.User_Profile_Response_Schema(**user_profile)
