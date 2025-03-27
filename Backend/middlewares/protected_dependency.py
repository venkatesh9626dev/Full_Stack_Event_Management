from fastapi import Request, HTTPException, status

from core.auth import Jwt_Token

from utils.binaryConversion import str_to_binary

from modules.users.validator import general_user_validation


def get_current_user(request: Request):

    access_token = request.cookies.get("access_token")

    if not access_token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
        )

    user_id = Jwt_Token.verify_access_token(access_token)
    
    user_binary_id = str_to_binary(user_id)
    
    general_user_validation.validate_user_exists(user_binary_id)

    return user_binary_id
