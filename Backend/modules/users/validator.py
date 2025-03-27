from pydantic import EmailStr
from .models import Auth_Dao, Profile_Dao
from core.auth import Hashing

from fastapi import HTTPException, status


class Auth_Validator:

    @staticmethod
    def check_password_match(password, hashed_password):

        is_matching = Hashing.verify_password(password, hashed_password)

        return True if is_matching else False

class User_Validation:
    
    def __init__(self, Auth_Dao):
        self.auth_dao = Auth_Dao
        
    def validate_user_exists(self,user_binary_id):
        
        user = self.auth_dao.get_record(field_name="user_id", field_value=user_binary_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )
        
general_user_validation = User_Validation(Auth_Dao)