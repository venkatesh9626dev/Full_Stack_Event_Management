from pydantic import EmailStr
from .models import Auth_Dao , Profile_Dao
from core.auth import Hashing

class Auth_Validator:
    
    @staticmethod
    def check_email(email : EmailStr ):
        
        email = Auth_Dao.get_user_credentials_by_email(email)
        
        return True if email else False
    
    @staticmethod
    def check_password_match(password,hashed_password):
        
        is_matching = Hashing.verify_password(password,hashed_password)
        
        return True if is_matching else False
    
    @staticmethod
    def check_current_user(user_id):
        
        user = Auth_Dao.get_user_credentials_by_user_id(user_id)
        
        return True if user else False
    

