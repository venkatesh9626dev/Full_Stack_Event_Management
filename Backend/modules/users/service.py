from fastapi import HTTPException,status

from core.auth import Jwt_Token, Hashing

from utils import binaryConversion

from .schema import Profile_Create_Request_Schema , Profile_Update_Request_Schema

from . import schema as user_schema

from .models import Auth_Dao , Profile_Dao

from .validator import Auth_Validator 

class Authentication_Service:
    
    @classmethod
    def register_user(cls ,register_credentials : user_schema.Auth_Request_Schema):
        
        is_email_exist = Auth_Validator.check_email(register_credentials.email)
        
        if is_email_exist:
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email id already exists"
            )
            
        hash_password = Hashing.hash_password(register_credentials.password)
        
        register_credentials.password = hash_password
        
        new_user = Auth_Dao.register_user(register_credentials)
        
        user_uuid = binaryConversion.binary_to_str(new_user.user_id)
        
        access_token = Jwt_Token.create_access_token({"sub" : user_uuid})
        
        return {"access_token" : access_token , "email" : new_user.email}
    
    @classmethod
    def authenticate_user(cls ,authenticate_credentials : user_schema.Auth_Request_Schema):
        
        user = Auth_Dao.get_user_credentials_by_email(authenticate_credentials.email)
        
        if not user:
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Credentials"
            )
        
        password_check  = Auth_Validator.check_password_match(authenticate_credentials.password,user.password)
        
        if not password_check:
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Credentials"
            )
        
        user_uuid = binaryConversion.binary_to_str(user.user_id)
        
        access_token = Jwt_Token.create_access_token({"sub" : user_uuid})
        
        return {"access_token" : access_token , "email" : user.email}
        
class User_Profile_Service:
    
    @classmethod
    def create_profile(cls , profile_data : Profile_Create_Request_Schema , user_id : str):
        
        binary_id = binaryConversion.str_to_binary(user_id)
        
        is_profile_exist =  Profile_Dao.get_user_profile(binary_id)
        
        if is_profile_exist:
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User Profile already exists"
            )
        
        user_uuid = binaryConversion.str_to_binary(user_id)     
        
        new_profile = Profile_Dao.create_user_profile(profile_data , user_uuid)
        
        return new_profile
    
    @classmethod
    def update_profile(cls ,updated_data : Profile_Update_Request_Schema , user_id):
        
        user_uuid = binaryConversion.str_to_binary(user_id)     
        
        user_profile =  Profile_Dao.get_user_profile(user_uuid)
        
        if not user_profile:
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "User profile doesn't exist"
            )
        
        updated_details = Profile_Dao.update_user_profile(user_profile.profile_id ,updated_data)
        
        return updated_details
    
    @classmethod
    def get_profile(cls ,user_id : str):
        
        user_uuid = binaryConversion.str_to_binary(user_id)     
        
        user_profile = Profile_Dao.get_user_profile(user_uuid)
        
        if not user_profile:
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "User is profile is not yet created"
            )
        
        return user_profile