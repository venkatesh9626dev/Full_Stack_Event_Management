from pydantic import EmailStr
from .models import Auth_Dao , Profile_Dao
from core.auth import Hashing

class Auth_Validator:

    
    @staticmethod
    def check_password_match(password,hashed_password):
        
        is_matching = Hashing.verify_password(password,hashed_password)
        
        return True if is_matching else False

    

