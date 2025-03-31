from fastapi import Form
from datetime import date

from pydantic import ValidationError

from utils.cloudinary_util import upload_file
from fastapi import File, UploadFile, HTTPException

from typing import Optional

from settings import cipher

# Import your existing schemas
from modules.users.schema import (
    Profile_Create_Request_Schema,
    Profile_Update_Request_Schema,
)


def get_profile_create_data(
    first_name: str = Form(...),
    last_name: str = Form(...),
    college_name: str = Form(...),
    image_file: UploadFile = File(...),
    gender: str = Form(None),
    about_me: str = Form(None),
    date_of_birth: Optional[str] = Form(None),
    phone_number: str = Form(None),
    merchant_id: str = Form(None),
) -> Profile_Create_Request_Schema:
    """
    Extracts form data and returns a validated Profile_Create_Request_Schema object.
    """

    profile_image_url = upload_file(image_file)

    if merchant_id:
        merchant_id = cipher.encrypt(merchant_id.encode())

    try:
        return Profile_Create_Request_Schema(
        first_name=first_name,
        last_name=last_name,
        photo_url=profile_image_url,
        college_name=college_name,
        gender=gender,
        about_me=about_me,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
        merchant_id=merchant_id,
    )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())


def get_profile_update_data(
    first_name: str = Form(None),
    last_name: str = Form(None),
    image_file: UploadFile = File(None),
    college_name: str = Form(None),
    gender: str = Form(None),
    about_me: str = Form(None),
    date_of_birth: str = Form(None),
    phone_number: str = Form(None),
    merchant_id: str = Form(None),
) -> Profile_Update_Request_Schema:
    """
    Extracts form data and returns a validated Profile_Update_Request_Schema object.
    """
    
    def normalize(value):
        return value if value and value.strip() else None

    first_name = normalize(first_name)
    last_name = normalize(last_name)
    college_name = normalize(college_name)
    gender = normalize(gender)
    date_of_birth = normalize(date_of_birth)
    about_me = normalize(about_me)
    phone_number = normalize(phone_number)
    merchant_id = normalize(merchant_id)
    
    profile_image_url= None
                            
    if image_file and image_file.filename:
        allowed_extensions = {"image/jpeg", "image/png", "image/jpg"}
        
        if image_file.content_type not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Only JPG and PNG images are allowed. You uploaded {image_file.content_type}.",
            )

        profile_image_url = upload_file(image_file)

    if merchant_id:
        merchant_id = cipher.encrypt(merchant_id.encode())

    try:
        return Profile_Update_Request_Schema(
        first_name=first_name,
        last_name=last_name,
        photo_url=profile_image_url,
        college_name=college_name,
        gender=gender,
        about_me=about_me,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
        merchant_id=merchant_id,
    )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
        
