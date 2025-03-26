from fastapi import Form
from datetime import datetime, date
from typing import Optional
from utils.cloudinary_util import upload_file
from fastapi import File, UploadFile

# Import your existing schemas
from modules.users.schema import Profile_Create_Request_Schema, Profile_Update_Request_Schema

def get_profile_create_data(
    first_name: str = Form(...),
    last_name: str = Form(...),
    college_name: str = Form(...),
    image_file :  UploadFile = File(...),
    gender: str = Form(None),
    about_me: str = Form(None),
    date_of_birth: date = Form(None),
    phone_number: str = Form(None),
    merchant_id: str = Form(None),
) -> Profile_Create_Request_Schema:
    """
    Extracts form data and returns a validated Profile_Create_Request_Schema object.
    """
    
    profile_image_url = upload_file(image_file)
    
    return Profile_Create_Request_Schema(
        first_name=first_name,
        last_name=last_name,
        photo_url = profile_image_url,
        college_name=college_name,
        gender=gender,
        about_me=about_me,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
        merchant_id=merchant_id,
    )
    
def get_profile_update_data(
    first_name: str = Form(None),
    last_name: str = Form(None),
    image_file :  UploadFile = File(None),
    college_name: str = Form(None),
    gender: str = Form(None),
    about_me: str = Form(None),
    date_of_birth: date = Form(None),
    phone_number: str = Form(None),
    merchant_id: str = Form(None),
) -> Profile_Create_Request_Schema:
    """
    Extracts form data and returns a validated Profile_Update_Request_Schema object.
    """
    profile_image_url = upload_file(image_file)
    
    return Profile_Create_Request_Schema(
        first_name=first_name,
        last_name=last_name,
        photo_url = profile_image_url,
        college_name=college_name,
        gender=gender,
        about_me=about_me,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
        merchant_id=merchant_id,
    )
        

