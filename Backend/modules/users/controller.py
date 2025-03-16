from fastapi import APIRouter, Request, Response, Depends , HTTPException , status

from . import schema

from .service import Authentication_Service , User_Profile_Service

from .validator import Auth_Validator

from middlewares import protected_dependency

users_router = APIRouter(); 


# Users Authentication routes

@users_router.post("/auth/register")
async def register_user(response : Response , register_credentials : schema.Auth_Request_Schema):
    
    response_details = Authentication_Service.register_user(register_credentials)
    
    response.set_cookie(
        key = "access_token",
        value = response_details["access_token"],
        httponly = True,
        max_age=3600,
        #secure = True This will be added after making https
    )
    
    return schema.Auth_Response_Schema( email = response_details["email"])

@users_router.post("/auth/signin")
async def signin_user(response : Response , authenticate_credentials : schema.Auth_Request_Schema):
    response_details = Authentication_Service.authenticate_user(authenticate_credentials)
    
    response.set_cookie(
        key = "access_token",
        value = response_details["access_token"],
        httponly = True,
        max_age=3600,
        #secure = True This will be added after making https
    )
    
    return schema.Auth_Response_Schema( email = response_details["email"])

# Users Profile routes

@users_router.post("/profile")
async def create_profile(profile_data : schema.Profile_Create_Request_Schema , user_id : str = Depends(protected_dependency.validate_user) ):
    
    is_user_exist = Auth_Validator.check_current_user(user_id)
    
    if not is_user_exist:
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail= "User not exists")
    
    
    response_details = User_Profile_Service.create_profile(profile_data , user_id)
    
    return schema.Profile_Create_Response_Schema(**response_details.__dict__)
    
    

@users_router.get("/profile")
async def get_profile(user_id : str = Depends(protected_dependency.validate_user)):
    
    is_user_exist = Auth_Validator.check_current_user(user_id)
    
    if not is_user_exist:
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail= "User not exists")

    user_profile = User_Profile_Service.get_profile(user_id)
    
    return schema.Profile_Response_Schema(**user_profile.__dict__)
@users_router.patch("/profile")
async def patch_profile(updated_data : schema.Profile_Update_Request_Schema , user_id : str = Depends(protected_dependency.validate_user)):
    
    is_user_exist = Auth_Validator.check_current_user(user_id)
    
    if not is_user_exist:
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail= "User not exists")

    updated_response = User_Profile_Service.update_profile(updated_data , user_id)
    
    return schema.Profile_Update_Response_Schema(**updated_response.__dict__)

@users_router.put("/profile")
async def update_profile(updated_data : schema.Profile_Update_Request_Schema , user_id : str = Depends(protected_dependency.validate_user)):
    
    is_user_exist = Auth_Validator.check_current_user(user_id)
    
    if not is_user_exist:
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail= "User not exists")

    updated_response = User_Profile_Service.update_profile(updated_data , user_id)
    
    return schema.Profile_Update_Response_Schema(**updated_response.__dict__)
# @users_router.get("/{user_id}/profile")
# async def get_user_profile():
#     pass

# Users events route

@users_router.get("/events")
async def get_events():
    pass

@users_router.get("/events/created")
async def get_created_events():
    pass

@users_router.get("/events/registered")
async def get_registered_events():
    pass

# @users_router.get("/{user_id}/events")
# async def get_user_events():
#     pass

# @users_router.get("/{user_id}/events/created")
# async def get_user_created_events():
#     pass

# @users_router.get("/{user_id}/events/registered")
# async def get_user_registered_events():
#     pass

