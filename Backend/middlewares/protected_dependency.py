from fastapi import Request , HTTPException , status

from core.auth import Jwt_Token


def validate_user(request : Request):
    
    access_token = request.cookies.get("access_token")
    
    if not access_token:
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    user_id = Jwt_Token.verify_access_token(access_token)

    return user_id
